from datetime import date, datetime, timedelta
from typing import Any, Optional

from sqlalchemy.orm import Session

from app.config import get_settings
from app.models.maintenance_block import MaintenanceBlock
from app.models.resource import Resource
from app.models.train_schedule import TrainSchedule
from app.services.conflict_service import detect_conflicts
from app.utils.time_utils import combine_date_time, parse_hhmm


def _busy_intervals(
    schedules: list[TrainSchedule],
    blocks: list[MaintenanceBlock],
    section: str,
) -> list[tuple[datetime, datetime]]:
    busy: list[tuple[datetime, datetime]] = []
    for sched in schedules:
        if sched.section == section:
            busy.append((sched.arrival_time, sched.departure_time))
    for block in blocks:
        if block.section == section and block.status not in {"CANCELLED", "COMPLETED"}:
            busy.append((block.start_time, block.end_time))
    busy.sort(key=lambda item: item[0])
    return busy


def _merge(intervals: list[tuple[datetime, datetime]]) -> list[tuple[datetime, datetime]]:
    if not intervals:
        return []
    merged = [intervals[0]]
    for start, end in intervals[1:]:
        last_start, last_end = merged[-1]
        if start <= last_end:
            merged[-1] = (last_start, max(last_end, end))
        else:
            merged.append((start, end))
    return merged


def find_windows(
    *,
    section: str,
    day: date,
    duration_minutes: int,
    schedules: list[TrainSchedule],
    existing_blocks: list[MaintenanceBlock],
    resources: list[Resource],
    required_resource_type: Optional[str] = None,
    weather_type: Optional[str] = None,
    restrict_keywords: Optional[list[str]] = None,
) -> dict[str, Any]:
    settings = get_settings()
    day_start = combine_date_time(day, parse_hhmm(settings.operating_day_start))
    day_end = combine_date_time(day, parse_hhmm(settings.operating_day_end))
    if day_end <= day_start:
        day_end = day_start + timedelta(days=1)

    busy = _merge(_busy_intervals(schedules, existing_blocks, section))
    free: list[tuple[datetime, datetime]] = []
    cursor = day_start
    for start, end in busy:
        if start > cursor:
            free.append((cursor, start))
        cursor = max(cursor, end)
    if cursor < day_end:
        free.append((cursor, day_end))

    windows: list[dict[str, Any]] = []
    for start, end in free:
        length = int((end - start).total_seconds() // 60)
        if length < duration_minutes:
            continue
        check = detect_conflicts(
            section=section,
            start_time=start,
            end_time=start + timedelta(minutes=duration_minutes),
            duration_minutes=duration_minutes,
            schedules=schedules,
            existing_blocks=existing_blocks,
            resources=resources,
            required_resource_type=required_resource_type,
            weather_type=weather_type,
            restrict_keywords=restrict_keywords,
        )
        train_conflicts = sum(1 for c in check["conflicts"] if c["type"] == "TRAIN_CONFLICT")
        if not check["valid"] and train_conflicts:
            continue
        if not check["valid"] and any(
            c["type"] in {"RESOURCE_UNAVAILABLE", "WEATHER_RESTRICTION"} for c in check["conflicts"]
        ):
            continue
        windows.append(
            {
                "start": start.strftime("%H:%M"),
                "end": end.strftime("%H:%M"),
                "start_time": start.isoformat(sep=" "),
                "end_time": end.isoformat(sep=" "),
                "duration_minutes": length,
                "train_conflicts": train_conflicts,
            }
        )
    return {
        "section": section,
        "date": day.isoformat(),
        "windows": windows,
        "data_note": "Candidate windows derived from synthetic schedules and blocks (demo).",
    }


def find_windows_from_db(
    db: Session,
    section: str,
    day: date,
    duration_minutes: int,
    resource_type: Optional[str] = None,
    weather_type: Optional[str] = None,
) -> dict[str, Any]:
    from app.services.maintenance_service import list_blocks, list_resources, list_schedules
    from app.config import get_settings

    schedules = list_schedules(db, section=section, schedule_date=day)
    blocks = list_blocks(db, section=section)
    resources = list_resources(db, section=section)
    rules = get_settings().weather_rules.get(weather_type or "NORMAL", {})
    return find_windows(
        section=section,
        day=day,
        duration_minutes=duration_minutes,
        schedules=schedules,
        existing_blocks=blocks,
        resources=resources,
        required_resource_type=resource_type,
        weather_type=weather_type,
        restrict_keywords=rules.get("restrict_keywords", []),
    )
