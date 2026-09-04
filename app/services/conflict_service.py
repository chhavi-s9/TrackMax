from datetime import datetime
from typing import Any, Optional

from app.models.asset import Asset
from app.models.maintenance_block import MaintenanceBlock
from app.models.maintenance_task import MaintenanceTask
from app.models.resource import Resource
from app.models.train import Train
from app.models.train_schedule import TrainSchedule
from app.utils.enums import ConflictType, ResourceStatus
from app.utils.time_utils import enum_value, overlaps


def _text_blob(task: MaintenanceTask) -> str:
    return f"{task.task_type or ''} {task.description or ''}".lower()


def detect_conflicts(
    *,
    section: str,
    start_time: datetime,
    end_time: datetime,
    duration_minutes: int,
    schedules: list[TrainSchedule],
    existing_blocks: list[MaintenanceBlock],
    resources: list[Resource],
    tasks: Optional[list[MaintenanceTask]] = None,
    required_resource_type: Optional[str] = None,
    weather_type: Optional[str] = None,
    restrict_keywords: Optional[list[str]] = None,
    trains: Optional[dict[int, Train]] = None,
    ignore_block_id: Optional[int] = None,
) -> dict[str, Any]:
    """Return structured conflicts for a proposed block. Pure function for tests."""
    conflicts: list[dict[str, Any]] = []
    trains = trains or {}
    tasks = tasks or []

    actual_duration = int((end_time - start_time).total_seconds() // 60)
    if actual_duration < duration_minutes:
        conflicts.append(
            {
                "type": ConflictType.DURATION_INSUFFICIENT.value,
                "section": section,
                "time": start_time.strftime("%H:%M"),
                "detail": f"Window is {actual_duration} min but task needs {duration_minutes} min",
            }
        )

    for sched in schedules:
        if sched.section != section:
            conflicts.append(
                {
                    "type": ConflictType.SECTION_MISMATCH.value,
                    "section": sched.section,
                    "time": sched.arrival_time.strftime("%H:%M"),
                    "detail": "Schedule section does not match proposed block",
                }
            )
            continue
        if overlaps(start_time, end_time, sched.arrival_time, sched.departure_time):
            train = trains.get(sched.train_id)
            conflicts.append(
                {
                    "type": ConflictType.TRAIN_CONFLICT.value,
                    "train_number": train.train_number if train else str(sched.train_id),
                    "section": section,
                    "time": sched.arrival_time.strftime("%H:%M"),
                }
            )

    for block in existing_blocks:
        if ignore_block_id is not None and block.id == ignore_block_id:
            continue
        if block.status in {"CANCELLED", "COMPLETED"}:
            continue
        if block.section != section:
            continue
        if overlaps(start_time, end_time, block.start_time, block.end_time):
            conflicts.append(
                {
                    "type": ConflictType.BLOCK_OVERLAP.value,
                    "block_code": block.block_code,
                    "section": section,
                    "time": block.start_time.strftime("%H:%M"),
                }
            )

    if required_resource_type:
        matching = [
            r
            for r in resources
            if r.resource_type == required_resource_type
            and r.status == ResourceStatus.AVAILABLE.value
            and (r.section == section or r.section == "*")
        ]
        available = []
        for resource in matching:
            from_ok = resource.available_from is None or resource.available_from <= start_time
            until_ok = resource.available_until is None or resource.available_until >= end_time
            if from_ok and until_ok:
                available.append(resource)
        if not available:
            conflicts.append(
                {
                    "type": ConflictType.RESOURCE_UNAVAILABLE.value,
                    "section": section,
                    "time": start_time.strftime("%H:%M"),
                    "resource_type": required_resource_type,
                }
            )

    asset_ids = [t.asset_id for t in tasks]
    if len(asset_ids) != len(set(asset_ids)):
        conflicts.append(
            {
                "type": ConflictType.ASSET_CONFLICT.value,
                "section": section,
                "time": start_time.strftime("%H:%M"),
                "detail": "Multiple tasks target the same asset in this block",
            }
        )

    weather_name = enum_value(weather_type) if weather_type else None
    if weather_name and restrict_keywords:
        for task in tasks:
            blob = _text_blob(task)
            if any(k.lower() in blob for k in restrict_keywords):
                conflicts.append(
                    {
                        "type": ConflictType.WEATHER_RESTRICTION.value,
                        "section": section,
                        "time": start_time.strftime("%H:%M"),
                        "weather": weather_name,
                        "task_id": task.id,
                    }
                )

    return {"valid": len(conflicts) == 0, "conflicts": conflicts}
