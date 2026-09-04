from datetime import date, timedelta
from typing import Any, Optional

from sqlalchemy.orm import Session, joinedload

from app.models.maintenance_task import MaintenanceTask
from app.models.train import Train
from app.services.conflict_service import detect_conflicts
from app.services.maintenance_service import list_blocks, list_resources, list_schedules, list_tasks
from app.services.window_service import find_windows
from app.utils.enums import Horizon, Priority


def _horizon_end(start: date, horizon: str) -> date:
    if horizon == Horizon.MONTHLY.value or horizon == "monthly":
        return start + timedelta(days=30)
    return start + timedelta(days=7)


def build_overview(
    db: Session,
    section: str,
    horizon: str = "weekly",
    as_of: Optional[date] = None,
) -> dict[str, Any]:
    as_of = as_of or date(2026, 9, 5)
    end = _horizon_end(as_of, horizon)
    tasks = (
        db.query(MaintenanceTask)
        .options(joinedload(MaintenanceTask.asset), joinedload(MaintenanceTask.department))
        .filter(MaintenanceTask.section == section)
        .all()
    )
    days = [as_of + timedelta(days=i) for i in range((end - as_of).days + 1)]
    schedules = []
    for day in days:
        schedules.extend(list_schedules(db, section=section, schedule_date=day))
    blocks = list_blocks(db, section=section)
    resources = list_resources(db, section=section)
    trains = {t.id: t for t in db.query(Train).all()}

    task_rows = []
    for task in tasks:
        task_rows.append(
            {
                "id": task.id,
                "task_code": task.task_code,
                "source_system": task.source_system,
                "department": task.department.name if task.department else None,
                "asset": task.asset.name if task.asset else None,
                "priority": task.priority,
                "risk_score": task.risk_score,
                "status": task.status,
                "section": task.section,
                "due_date": task.due_date.isoformat() if task.due_date else None,
                "estimated_duration_minutes": task.estimated_duration_minutes,
            }
        )

    durations = [t.estimated_duration_minutes for t in tasks] or [120]
    median_duration = sorted(durations)[len(durations) // 2]
    windows = find_windows(
        section=section,
        day=as_of,
        duration_minutes=median_duration,
        schedules=list_schedules(db, section=section, schedule_date=as_of),
        existing_blocks=blocks,
        resources=resources,
    )["windows"]

    movements = []
    for sched in list_schedules(db, section=section, schedule_date=as_of):
        train = trains.get(sched.train_id)
        movements.append(
            {
                "train_number": train.train_number if train else None,
                "train_name": train.train_name if train else None,
                "section": sched.section,
                "arrival_time": sched.arrival_time.isoformat(sep=" "),
                "departure_time": sched.departure_time.isoformat(sep=" "),
                "schedule_date": sched.schedule_date.isoformat(),
            }
        )

    priorities = [t.priority for t in tasks]
    return {
        "section": section,
        "horizon": horizon,
        "tasks": task_rows,
        "available_windows": windows,
        "train_movements": movements,
        "summary": {
            "total_defects": len(tasks),
            "critical": priorities.count(Priority.CRITICAL.value),
            "high": priorities.count(Priority.HIGH.value),
            "medium": priorities.count(Priority.MEDIUM.value),
            "low": priorities.count(Priority.LOW.value),
        },
        "data_note": (
            "Unified view of synthetic TMS/SMMS/TDMS-style tasks plus corridor/train data. "
            "Not live Indian Railways feeds."
        ),
    }


def validate_proposed_block(
    db: Session,
    section: str,
    start,
    end,
    duration_minutes: int,
    resource_type: Optional[str] = None,
    weather: Optional[str] = None,
) -> dict[str, Any]:
    from app.config import get_settings

    schedules = list_schedules(db, section=section, schedule_date=start.date())
    blocks = list_blocks(db, section=section)
    resources = list_resources(db, section=section)
    trains = {t.id: t for t in db.query(Train).all()}
    rules = get_settings().weather_rules.get((weather or "NORMAL").upper(), {})
    return detect_conflicts(
        section=section,
        start_time=start,
        end_time=end,
        duration_minutes=duration_minutes,
        schedules=schedules,
        existing_blocks=blocks,
        resources=resources,
        required_resource_type=resource_type,
        weather_type=weather,
        restrict_keywords=rules.get("restrict_keywords", []),
        trains=trains,
    )
