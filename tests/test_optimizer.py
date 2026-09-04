from datetime import datetime, timedelta

from app.optimizer.block_optimizer import solve_block_plan
from app.optimizer.scoring import ResourceCandidate, TaskCandidate, WindowCandidate


def _task(**kwargs):
    base = dict(
        task_id=12,
        section="JP-AII",
        duration_minutes=120,
        priority="CRITICAL",
        risk_score=0.9,
        due_soon=True,
        resource_type="track_gang",
    )
    base.update(kwargs)
    return TaskCandidate(**base)


def _window(start_h, end_h, conflicts=0, wid=1):
    return WindowCandidate(
        window_id=wid,
        section="JP-AII",
        start=datetime(2026, 9, 5, start_h, 0),
        end=datetime(2026, 9, 5, end_h, 0),
        train_conflicts=conflicts,
    )


def _resource(available=True, rid=4):
    return ResourceCandidate(
        resource_id=rid,
        resource_type="track_gang",
        section="JP-AII",
        capacity=1,
        available=available,
    )


def test_optimizer_valid_schedule() -> None:
    result = solve_block_plan(
        tasks=[_task()],
        windows=[_window(13, 15)],
        resources=[_resource()],
    )
    assert result.status in {"OPTIMAL", "FEASIBLE"}
    assert result.assignments
    assert result.assignments[0]["task_id"] == 12
    assert result.assignments[0]["resource_id"] == 4
    assert result.train_disruption == 0


def test_optimizer_rejects_train_conflicts() -> None:
    result = solve_block_plan(
        tasks=[_task()],
        windows=[_window(11, 13, conflicts=1)],
        resources=[_resource()],
    )
    assert result.status == "INFEASIBLE"
    assert result.infeasible_reason


def test_optimizer_unavailable_resource() -> None:
    result = solve_block_plan(
        tasks=[_task()],
        windows=[_window(13, 15)],
        resources=[_resource(available=False)],
    )
    assert result.status == "INFEASIBLE"


def test_optimizer_infeasible_duration() -> None:
    result = solve_block_plan(
        tasks=[_task(duration_minutes=180)],
        windows=[_window(13, 14)],
        resources=[_resource()],
    )
    assert result.status == "INFEASIBLE"


def test_optimizer_does_not_claim_optimal_when_infeasible() -> None:
    result = solve_block_plan(tasks=[_task()], windows=[], resources=[_resource()])
    assert result.status != "OPTIMAL"
    assert result.status == "INFEASIBLE"
