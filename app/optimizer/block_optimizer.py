from datetime import datetime
from typing import Optional

from ortools.sat.python import cp_model

from app.config import get_settings
from app.optimizer.constraints import resource_matches, window_fits_task, window_hits_existing_block
from app.optimizer.scoring import (
    ExistingBlock,
    OptimizerWeights,
    ResourceCandidate,
    SolveResult,
    TaskCandidate,
    WindowCandidate,
)

_STATUS = {
    cp_model.OPTIMAL: "OPTIMAL",
    cp_model.FEASIBLE: "FEASIBLE",
    cp_model.INFEASIBLE: "INFEASIBLE",
    cp_model.MODEL_INVALID: "INFEASIBLE",
    cp_model.UNKNOWN: "UNKNOWN",
}


def solve_block_plan(
    tasks: list[TaskCandidate],
    windows: list[WindowCandidate],
    resources: list[ResourceCandidate],
    existing_blocks: Optional[list[ExistingBlock]] = None,
    weights: Optional[OptimizerWeights] = None,
    allow_train_conflicts: bool = False,
) -> SolveResult:
    """Schedule tasks into windows with CP-SAT. Hard constraints are never relaxed."""
    existing_blocks = existing_blocks or []
    weights = weights or OptimizerWeights.from_settings()
    settings = get_settings()

    model = cp_model.CpModel()
    x: dict[tuple[int, int, int], cp_model.IntVar] = {}

    for t_idx, task in enumerate(tasks):
        for w_idx, window in enumerate(windows):
            if not window_fits_task(task, window):
                continue
            if window_hits_existing_block(window, existing_blocks):
                continue
            if window.train_conflicts > 0 and not allow_train_conflicts:
                continue
            for r_idx, resource in enumerate(resources):
                if not resource_matches(task, resource):
                    continue
                var = model.NewBoolVar(f"t{t_idx}_w{w_idx}_r{r_idx}")
                x[t_idx, w_idx, r_idx] = var

    if not x:
        return SolveResult(
            status="INFEASIBLE",
            infeasible_reason=(
                "No feasible task/window/resource combination after hard constraints "
                "(duration, section, trains, existing blocks, resource availability)."
            ),
            reasoning=["Hard constraints left no candidate assignment."],
        )

    # Each task at most once.
    for t_idx, task in enumerate(tasks):
        vars_for_task = [x[key] for key in x if key[0] == t_idx]
        if vars_for_task:
            model.Add(sum(vars_for_task) <= 1)

    # Window capacity: sequential bundling — sum of durations <= window length.
    for w_idx, window in enumerate(windows):
        length = int((window.end - window.start).total_seconds() // 60)
        duration_terms = []
        for (t_idx, w, r_idx), var in x.items():
            if w != w_idx:
                continue
            duration_terms.append(tasks[t_idx].duration_minutes * var)
        if duration_terms:
            model.Add(sum(duration_terms) <= length)

    # Resource not double-booked on overlapping windows.
    for r_idx, resource in enumerate(resources):
        for w_a, window_a in enumerate(windows):
            for w_b, window_b in enumerate(windows):
                if w_b <= w_a:
                    continue
                if window_a.section != window_b.section:
                    continue
                if window_a.end <= window_b.start or window_b.end <= window_a.start:
                    continue
                vars_a = [x[k] for k in x if k[1] == w_a and k[2] == r_idx]
                vars_b = [x[k] for k in x if k[1] == w_b and k[2] == r_idx]
                if vars_a and vars_b:
                    model.Add(sum(vars_a) + sum(vars_b) <= resource.capacity)

        for w_idx, window in enumerate(windows):
            same_window = [x[k] for k in x if k[1] == w_idx and k[2] == r_idx]
            if same_window:
                model.Add(sum(same_window) <= resource.capacity)

    scale = 100
    objective_terms = []
    for (t_idx, w_idx, r_idx), var in x.items():
        task = tasks[t_idx]
        window = windows[w_idx]
        gain = 0.0
        if task.priority == "CRITICAL":
            gain += weights.critical_completed
        elif task.priority == "HIGH":
            gain += weights.high_completed
        gain += weights.high_risk_coverage * task.risk_score
        if task.due_soon:
            gain += weights.before_due
        gain += weights.resource_utilization * 0.5
        gain += weights.asset_availability * 0.5
        penalty = 0.0
        penalty += weights.train_disruption * window.train_conflicts
        penalty += weights.passenger_impact * window.passenger_trains * 0.5
        penalty += weights.freight_impact * window.freight_trains * 0.5
        extra_hours = max(
            int((window.end - window.start).total_seconds() // 60) - task.duration_minutes, 0
        ) / 60.0
        penalty += weights.extra_block_hours * extra_hours * 0.1
        if not task.due_soon:
            penalty += weights.lateness * 0.05
        objective_terms.append(int(round((gain - penalty) * scale)) * var)

    if objective_terms:
        model.Maximize(sum(objective_terms))

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = settings.solver_max_time_seconds
    solver.parameters.num_search_workers = 4
    result = solver.Solve(model)
    status = _STATUS.get(result, "INFEASIBLE")

    if status in {"INFEASIBLE", "UNKNOWN"}:
        return SolveResult(
            status=status,
            infeasible_reason=(
                "CP-SAT could not produce a valid assignment within the solver result."
                if status == "UNKNOWN" else
                "CP-SAT found no assignment that satisfies duration, window bounds, "
                "train conflicts, existing blocks, and resource availability."
            ),
            reasoning=[f"Solver status: {status}. Hard constraints were not relaxed."],
        )

    assignments = []
    used_windows = set()
    train_disruption = 0
    for (t_idx, w_idx, r_idx), var in x.items():
        if solver.Value(var) != 1:
            continue
        task = tasks[t_idx]
        window = windows[w_idx]
        resource = resources[r_idx]
        used_windows.add(w_idx)
        train_disruption += window.train_conflicts
        assignments.append(
            {
                "task_id": task.task_id,
                "resource_id": resource.resource_id,
                "section": window.section,
                "start_time": window.start.strftime("%H:%M"),
                "end_time": window.end.strftime("%H:%M"),
                "start_dt": window.start,
                "end_dt": window.end,
                "duration_minutes": task.duration_minutes,
                "priority": task.priority,
                "window_id": window.window_id,
            }
        )

    raw = solver.ObjectiveValue() / scale if assignments else 0.0
    score = max(0.0, min(100.0, 50.0 + raw))
    reasoning = _reasoning(assignments, tasks, status)
    return SolveResult(
        status=status,
        assignments=assignments,
        optimization_score=round(score, 2),
        train_disruption=train_disruption,
        reasoning=reasoning,
    )


def _reasoning(assignments: list[dict], tasks: list[TaskCandidate], status: str) -> list[str]:
    lines = [f"CP-SAT solver status: {status}."]
    if not assignments:
        lines.append("No tasks were scheduled.")
        return lines
    by_id = {t.task_id: t for t in tasks}
    for item in assignments:
        task = by_id[item["task_id"]]
        lines.append(f"Task {task.task_id} scheduled {item['start_time']}-{item['end_time']} on {item['section']}.")
        if task.priority in {"HIGH", "CRITICAL"}:
            lines.append("High-priority maintenance task.")
        if task.due_soon:
            lines.append("Task is approaching its due date.")
        lines.append("Required resource is available.")
        if item.get("duration_minutes"):
            lines.append("Task duration fits the selected window.")
    lines.append("Hard safety/operational constraints were not relaxed for score.")
    return lines[:12]


def recommended_block_payload(result: SolveResult) -> dict:
    if not result.assignments:
        return {
            "status": result.status,
            "recommended_block": None,
            "optimization_score": result.optimization_score,
            "train_disruption": result.train_disruption,
            "reasoning": result.reasoning,
            "infeasible_reason": result.infeasible_reason,
            "data_note": "Simulation/demo optimizer output.",
        }
    first = result.assignments[0]
    duration = int((first["end_dt"] - first["start_dt"]).total_seconds() // 60)
    return {
        "status": result.status,
        "recommended_block": {
            "section": first["section"],
            "start_time": first["start_time"],
            "end_time": first["end_time"],
            "duration_minutes": duration,
        },
        "optimization_score": result.optimization_score,
        "task_id": first["task_id"],
        "resource_id": first["resource_id"],
        "train_disruption": result.train_disruption,
        "assignments": [
            {k: v for k, v in a.items() if k not in {"start_dt", "end_dt"}} for a in result.assignments
        ],
        "reasoning": result.reasoning,
        "data_note": "Simulation/demo optimizer output. Not a claim about live railway performance.",
    }
