from datetime import date, datetime, timedelta
from typing import Any, Optional

from sqlalchemy.orm import Session

from app.config import get_settings
from app.models.maintenance_block import MaintenanceBlock
from app.models.maintenance_task import MaintenanceTask
from app.models.weather import WeatherRecord
from app.schemas.weather import WeatherCreate
from app.services.planning_service import run_optimizer_for_section
from app.services.priority_service import score_task
from app.utils.enums import WeatherType
from app.utils.time_utils import enum_value


def list_weather(db: Session, section: Optional[str] = None) -> list[WeatherRecord]:
    q = db.query(WeatherRecord)
    if section:
        q = q.filter(WeatherRecord.section == section)
    return list(q.all())


def upsert_weather(db: Session, payload: WeatherCreate) -> WeatherRecord:
    existing = (
        db.query(WeatherRecord)
        .filter(
            WeatherRecord.section == payload.section,
            WeatherRecord.date == payload.date,
        )
        .first()
    )
    data = payload.model_dump()
    data["weather_type"] = enum_value(payload.weather_type)
    if existing:
        for key, value in data.items():
            setattr(existing, key, value)
        db.commit()
        db.refresh(existing)
        return existing
    row = WeatherRecord(**data)
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def weather_adjusted_priorities(
    db: Session,
    section: str,
    weather: str,
    as_of: Optional[date] = None,
) -> list[dict[str, Any]]:
    as_of = as_of or date(2026, 9, 5)
    tasks = (
        db.query(MaintenanceTask)
        .filter(MaintenanceTask.section == section, MaintenanceTask.status == "PENDING")
        .all()
    )
    rows = []
    for task in tasks:
        before = score_task(db, task, weather="NORMAL", as_of=as_of)
        after = score_task(db, task, weather=weather, as_of=as_of)
        rows.append(
            {
                "task_id": task.id,
                "original_priority": before["priority"],
                "adjusted_priority": after["priority"],
                "original_score": before["combined_score"],
                "adjusted_score": after["combined_score"],
                "changed": before["priority"] != after["priority"],
            }
        )
    db.commit()
    return rows


def reschedule_for_weather(
    db: Session,
    section: str,
    day: date,
    weather: str,
) -> dict[str, Any]:
    """Risk adjustment → priority adjustment → re-run optimizer. Does not blindly move everything."""
    weather_name = enum_value(weather).upper()
    settings = get_settings()
    rules = settings.weather_rules.get(weather_name, settings.weather_rules["NORMAL"])

    original = run_optimizer_for_section(db, section, weather="NORMAL", day=day, persist=False)
    adjusted = weather_adjusted_priorities(db, section, weather_name, as_of=day)
    updated = run_optimizer_for_section(db, section, weather=weather_name, day=day, persist=False)

    orig_block = original.get("recommended_block")
    new_block = updated.get("recommended_block")
    changed = orig_block != new_block
    reasons = []
    if weather_name == WeatherType.HEAVY_RAIN.value:
        reasons.append("Heavy rainfall predicted; track/drainage/electrical insulation risk increased.")
    elif weather_name == WeatherType.HEATWAVE.value:
        reasons.append("Heatwave: buckling / rail temperature / OHE tension checks ranked higher.")
    elif weather_name == WeatherType.FOG.value:
        reasons.append("Fog: signal visibility and S&T inspection ranked higher.")
    else:
        reasons.append("Weather applied; only weather-sensitive tasks changed rank.")
    if rules.get("restrict_keywords"):
        reasons.append("Restricted work types were kept out of unsafe windows.")
    if not changed:
        reasons.append("Original window remained feasible after weather-adjusted priorities.")

    changed_priority = [row for row in adjusted if row["changed"]]
    upsert_weather(
        db,
        WeatherCreate(
            section=section,
            date=day,
            weather_type=WeatherType(weather_name),
            severity={"NORMAL": 0, "FOG": 40, "HEATWAVE": 55, "HEAVY_RAIN": 70, "THUNDERSTORM": 80}.get(
                weather_name, 10
            ),
            description=f"Demo weather scenario {weather_name}",
        ),
    )
    return {
        "original": orig_block,
        "new": new_block,
        "reason": " ".join(reasons),
        "changed_priority": changed_priority,
        "weather_condition": weather_name,
        "original_plan_status": original.get("status"),
        "new_plan_status": updated.get("status"),
        "data_note": "Weather reschedule is a demo simulation using configurable keyword rules.",
    }
