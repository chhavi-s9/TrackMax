from datetime import date, datetime, timedelta
from typing import Any, Optional

from sqlalchemy.orm import Session, joinedload

from app.config import get_settings
from app.models.maintenance_block import MaintenanceBlock
from app.models.maintenance_task import MaintenanceTask
from app.models.resource import Resource
from app.optimizer.block_optimizer import recommended_block_payload, solve_block_plan
from app.optimizer.scoring import (
    ExistingBlock,
    ResourceCandidate,
    TaskCandidate,
    WindowCandidate,
)
from app.services.priority_service import prioritized_tasks, score_task
from app.services.window_service import find_windows_from_db
from app.utils.enums import BlockStatus, BlockType, TaskStatus
from app.utils.time_utils import combine_date_time, enum_value, parse_hhmm


def _as_candidates(ranked: list[dict], tasks_by_id: dict[int, MaintenanceTask]) -> list[TaskCandidate]:
    out = []
    for row in ranked:
        task = tasks_by_id[row["task_id"]]
        due = task.due_date
        due_soon = bool(due and (due - date(2026, 9, 5)).days <= 7)
        out.append(
            TaskCandidate(
                task_id=task.id,
                section=task.section,
                duration_minutes=task.estimated_duration_minutes,
                priority=row.get("priority") or task.priority,
                risk_score=float(row.get("risk_score") or task.risk_score or 0.0),
                due_soon=due_soon,
                resource_type=task.required_resource_type,
                department=task.department.code if task.department else "",
                description=task.description or "",
            )
        )
    return out


def _windows_for_section(db: Session, section: str, day: date, weather: Optional[str]) -> list[WindowCandidate]:
    payload = find_windows_from_db(db, section, day, duration_minutes=60, weather_type=weather)
    windows = []
    for idx, win in enumerate(payload["windows"]):
        start = datetime.strptime(f"{day.isoformat()} {win['start']}", "%Y-%m-%d %H:%M")
        end = datetime.strptime(f"{day.isoformat()} {win['end']}", "%Y-%m-%d %H:%M")
        windows.append(
            WindowCandidate(
                window_id=idx,
                section=section,
                start=start,
                end=end,
                train_conflicts=int(win.get("train_conflicts") or 0),
            )
        )
    return windows


def _resource_candidates(db: Session, section: str) -> list[ResourceCandidate]:
    rows = db.query(Resource).filter(Resource.section == section).all()
    return [
        ResourceCandidate(
            resource_id=r.id,
            resource_type=r.resource_type,
            section=r.section,
            capacity=r.capacity,
            available=r.status == "AVAILABLE",
        )
        for r in rows
    ]


def _existing(db: Session, section: str) -> list[ExistingBlock]:
    rows = db.query(MaintenanceBlock).filter(MaintenanceBlock.section == section).all()
    return [
        ExistingBlock(block_id=b.id, section=b.section, start=b.start_time, end=b.end_time)
        for b in rows
        if b.status not in {"CANCELLED", "COMPLETED"}
    ]


def run_optimizer_for_section(
    db: Session,
    section: str,
    weather: Optional[str] = "NORMAL",
    day: Optional[date] = None,
    persist: bool = False,
) -> dict[str, Any]:
    day = day or date(2026, 9, 5)
    ranked = prioritized_tasks(db, section=section, weather=weather)
    tasks = (
        db.query(MaintenanceTask)
        .options(joinedload(MaintenanceTask.department), joinedload(MaintenanceTask.asset))
        .filter(
            MaintenanceTask.section == section,
            MaintenanceTask.status == TaskStatus.PENDING.value,
        )
        .all()
    )
    by_id = {t.id: t for t in tasks}
    candidates = _as_candidates(ranked["tasks"], by_id)
    windows = _windows_for_section(db, section, day, weather)
    resources = _resource_candidates(db, section)
    existing = _existing(db, section)
    result = solve_block_plan(candidates, windows, resources, existing)
    payload = recommended_block_payload(result)
    payload["section"] = section
    payload["date"] = day.isoformat()
    payload["weather"] = enum_value(weather)

    if persist and result.assignments:
        for item in result.assignments:
            start = item["start_dt"]
            end = item["end_dt"]
            code = f"OPT-{section}-{start.strftime('%Y%m%d%H%M')}-{item['task_id']}"
            block = MaintenanceBlock(
                block_code=code,
                section=section,
                start_time=start,
                end_time=end,
                duration_minutes=int((end - start).total_seconds() // 60),
                status=BlockStatus.PROPOSED.value,
                block_type=BlockType.COORDINATED.value,
                optimization_score=result.optimization_score,
            )
            db.add(block)
            db.flush()
            task = by_id.get(item["task_id"])
            if task:
                task.block_id = block.id
                task.status = TaskStatus.SCHEDULED.value
        db.commit()
    return payload


def weekly_plan(
    db: Session,
    section: str,
    weather: Optional[str] = "NORMAL",
    start: Optional[date] = None,
) -> dict[str, Any]:
    start = start or date(2026, 9, 5)
    all_assignments = []
    unscheduled = set()
    scores = []
    conflicts: list[dict[str, Any]] = []
    pending = (
        db.query(MaintenanceTask)
        .filter(
            MaintenanceTask.section == section,
            MaintenanceTask.status == TaskStatus.PENDING.value,
        )
        .all()
    )
    pending_ids = {t.id for t in pending}

    for offset in range(7):
        day = start + timedelta(days=offset)
        result_payload = run_optimizer_for_section(db, section, weather=weather, day=day, persist=False)
        if result_payload["status"] == "INFEASIBLE":
            continue
        for item in result_payload.get("assignments") or []:
            item = dict(item)
            item["date"] = day.isoformat()
            all_assignments.append(item)
            pending_ids.discard(item["task_id"])
        scores.append(result_payload.get("optimization_score") or 0)

    leftover = (
        db.query(MaintenanceTask)
        .options(joinedload(MaintenanceTask.asset))
        .filter(MaintenanceTask.id.in_(pending_ids))
        .all()
        if pending_ids
        else []
    )
    unscheduled_rows = [
        {
            "task_id": t.id,
            "task_code": t.task_code,
            "reason": "No feasible window/resource combination in the 7-day horizon.",
        }
        for t in leftover
    ]

    # Bundle note: assignments sharing date+window.
    bundles: dict[tuple, list] = {}
    for item in all_assignments:
        key = (item.get("date"), item.get("start_time"), item.get("end_time"), item.get("section"))
        bundles.setdefault(key, []).append(item["task_id"])
    bundle_notes = [
        {"window": f"{k[0]} {k[1]}-{k[2]}", "task_ids": v, "bundled": len(v) > 1}
        for k, v in bundles.items()
    ]

    return {
        "section": section,
        "weather": enum_value(weather),
        "horizon": "weekly",
        "scheduled_tasks": all_assignments,
        "blocks": [
            {
                "section": a["section"],
                "start_time": a["start_time"],
                "end_time": a["end_time"],
                "date": a["date"],
                "task_id": a["task_id"],
                "resource_id": a["resource_id"],
            }
            for a in all_assignments
        ],
        "resources": [a["resource_id"] for a in all_assignments],
        "conflicts": conflicts,
        "optimization_score": round(sum(scores) / len(scores), 2) if scores else 0.0,
        "unscheduled_tasks": unscheduled_rows,
        "bundling": bundle_notes,
        "reasons": [
            "Pending tasks were risk-ranked, feasible windows were generated, then CP-SAT assigned blocks.",
            "Compatible same-section tasks may share a window when durations fit and resources differ.",
        ],
        "data_note": "Weekly plan is a demo simulation, not an operational Indian Railways timetable.",
    }


def monthly_plan(db: Session, section: Optional[str] = None) -> dict[str, Any]:
    """High-level four-week outlook. Not minute-level optimization."""
    from sqlalchemy import func
    from app.models.department import Department

    start = date(2026, 9, 7)  # week starting after demo day
    weeks = []
    sections = [section] if section else ["JP-AII", "JP-GAD", "AII-MJ", "JP-BKI"]
    for week_no in range(4):
        week_start = start + timedelta(days=7 * week_no)
        week_end = week_start + timedelta(days=6)
        focus_section = sections[week_no % len(sections)]
        q = (
            db.query(Department.code, func.count(MaintenanceTask.id))
            .join(MaintenanceTask, MaintenanceTask.department_id == Department.id)
            .filter(
                MaintenanceTask.section == focus_section,
                MaintenanceTask.status.in_([TaskStatus.PENDING.value, TaskStatus.SCHEDULED.value]),
            )
            .group_by(Department.code)
            .all()
        )
        dept_codes = [row[0] for row in q] or ["ENG"]
        weeks.append(
            {
                "week": week_no + 1,
                "range": f"{week_start.isoformat()} to {week_end.isoformat()}",
                "section": focus_section,
                "departments": dept_codes,
                "summary": f"Week {week_no + 1} → {focus_section} → {' + '.join(dept_codes)}",
            }
        )
    return {
        "section": section,
        "weeks": weeks,
        "outlook": [w["summary"] for w in weeks],
        "data_note": "Monthly outlook is a high-level demo grouping, not a solved timetable.",
    }
