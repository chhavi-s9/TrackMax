from datetime import date
from typing import Any, Optional

from sqlalchemy.orm import Session

from app.services.planning_service import weekly_plan
from app.utils.enums import ScenarioType
from app.utils.time_utils import enum_value


def _metrics(
    *,
    block_hours: float,
    blocks: int,
    conflicts: int,
    availability: float,
    disruption: float,
    completed: int,
    label: str,
) -> dict[str, Any]:
    return {
        "total_block_hours": round(block_hours, 2),
        "number_of_blocks": blocks,
        "number_of_conflicts": conflicts,
        "estimated_asset_availability": round(availability, 3),
        "estimated_train_disruption": round(disruption, 3),
        "tasks_completed": completed,
        "label": label,
        "data_note": "Simulation/demo metrics only. Not measured railway performance.",
    }


def compare_scenarios(db: Session, section: str, scenario_type: Optional[str] = None) -> dict[str, Any]:
    """Deterministic baselines for manual/coordinated; CP-SAT for AI."""
    ai_plan = weekly_plan(db, section=section, weather="NORMAL")
    scheduled = ai_plan.get("scheduled_tasks") or []
    unscheduled = ai_plan.get("unscheduled_tasks") or []
    ai_blocks = len(ai_plan.get("blocks") or [])
    ai_hours = 0.0
    for b in ai_plan.get("blocks") or []:
        ai_hours += datetime_minutes(b["start_time"], b["end_time"]) / 60.0

    n_tasks = len(scheduled) + len(unscheduled)
    ai_completed = len(scheduled)

    # Manual: departments independently → ~1.6x blocks, more conflicts, fewer bundled.
    manual_blocks = max(ai_blocks + max(len(scheduled) - ai_blocks, 0) + 2, ai_blocks + 2)
    manual_hours = round(ai_hours * 1.55 + 2.0, 2)
    manual_conflicts = 4 + max(n_tasks // 5, 1)
    manual_completed = max(ai_completed - 3, n_tasks // 3)

    # Coordinated: share windows, some bundling.
    coord_blocks = max(int(round(ai_blocks * 1.2)) + 1, 1)
    coord_hours = round(ai_hours * 1.2 + 0.8, 2)
    coord_conflicts = 2
    coord_completed = max(ai_completed - 1, manual_completed)

    scenarios = {
        ScenarioType.MANUAL.value: _metrics(
            block_hours=manual_hours,
            blocks=manual_blocks,
            conflicts=manual_conflicts,
            availability=0.82,
            disruption=0.18,
            completed=manual_completed,
            label="Manual (independent departmental requests — baseline simulation)",
        ),
        ScenarioType.COORDINATED.value: _metrics(
            block_hours=coord_hours,
            blocks=coord_blocks,
            conflicts=coord_conflicts,
            availability=0.88,
            disruption=0.10,
            completed=coord_completed,
            label="Coordinated (shared windows, some bundling — baseline simulation)",
        ),
        ScenarioType.AI.value: _metrics(
            block_hours=round(ai_hours, 2),
            blocks=ai_blocks,
            conflicts=len(ai_plan.get("conflicts") or []),
            availability=0.93,
            disruption=0.04,
            completed=ai_completed,
            label="AI optimized (risk ranking + CP-SAT — demo simulation)",
        ),
    }

    selected = enum_value(scenario_type).lower() if scenario_type else None
    body = {
        "section": section,
        "comparison": scenarios,
        "ai_plan_excerpt": {
            "scheduled": len(scheduled),
            "unscheduled": len(unscheduled),
            "optimization_score": ai_plan.get("optimization_score"),
        },
        "data_note": (
            "All figures are simulation/demo metrics for the SIH prototype. "
            "They are not claims about live Indian Railways performance."
        ),
    }
    if selected in scenarios:
        body["selected"] = selected
        body["metrics"] = scenarios[selected]
    return body


def datetime_minutes(start_hhmm: str, end_hhmm: str) -> int:
    sh, sm = [int(p) for p in start_hhmm.split(":")]
    eh, em = [int(p) for p in end_hhmm.split(":")]
    return (eh * 60 + em) - (sh * 60 + sm)
