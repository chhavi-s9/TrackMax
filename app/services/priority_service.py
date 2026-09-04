from datetime import date
from typing import Any, Optional

from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from app.config import get_settings
from app.exceptions import ModelUnavailableError
from app.ml.feature_engineering import (
    criticality_score,
    impact_score,
    task_features,
    urgency_score,
)
from app.ml.risk_model import model_available, predict_priority
from app.models.asset import Asset
from app.models.maintenance_task import MaintenanceTask
from app.models.train_schedule import TrainSchedule
from app.utils.enums import TaskStatus
from app.utils.time_utils import clamp01, enum_value


def _train_density(db: Session, section: str, as_of: date) -> float:
    count = db.scalar(
        select(func.count()).select_from(TrainSchedule).where(
            TrainSchedule.section == section,
            TrainSchedule.schedule_date == as_of,
        )
    )
    return clamp01((count or 0) / 20.0)


def _maintenance_frequency(db: Session, asset_id: int) -> float:
    count = db.scalar(
        select(func.count()).select_from(MaintenanceTask).where(
            MaintenanceTask.asset_id == asset_id
        )
    )
    return float(count or 0)


def score_task(
    db: Session,
    task: MaintenanceTask,
    weather: Optional[str] = None,
    as_of: Optional[date] = None,
) -> dict[str, Any]:
    settings = get_settings()
    as_of = as_of or date(2026, 9, 5)
    asset: Asset = task.asset
    density = _train_density(db, task.section, as_of)
    freq = _maintenance_frequency(db, task.asset_id)
    features = task_features(
        as_of=as_of,
        installation_date=asset.installation_date,
        last_maintenance_date=asset.last_maintenance_date,
        due_date=task.due_date,
        condition_score=asset.condition_score,
        failure_count=asset.failure_count,
        criticality=asset.criticality,
        maintenance_frequency=freq,
        train_density=density,
        duration_minutes=task.estimated_duration_minutes,
    )
    if not model_available():
        raise ModelUnavailableError()
    ml_label, ml_risk = predict_priority(features)
    crit = criticality_score(asset.criticality, asset.condition_score)
    urg = urgency_score(as_of, task.due_date)
    impact = impact_score(density, task.estimated_duration_minutes)
    combined = (
        settings.rank_weight_ml_risk * ml_risk
        + settings.rank_weight_criticality * crit
        + settings.rank_weight_urgency * urg
        + settings.rank_weight_impact * impact
    )
    weather_name = enum_value(weather).upper() if weather else "NORMAL"
    rules = settings.weather_rules.get(weather_name, {})
    blob = f"{task.task_type or ''} {task.description or ''}".lower()
    if any(k.lower() in blob for k in rules.get("boost_keywords", [])):
        combined = clamp01(combined + settings.weather_boost_factor)
        if ml_label in {"LOW", "MEDIUM"}:
            ml_label = "HIGH"
        elif ml_label == "HIGH":
            ml_label = "CRITICAL"

    task.risk_score = round(ml_risk, 4)
    return {
        "task_id": task.id,
        "task_code": task.task_code,
        "asset": asset.name,
        "asset_id": asset.id,
        "section": task.section,
        "department_id": task.department_id,
        "source_system": task.source_system,
        "task_type": task.task_type,
        "description": task.description,
        "ml_priority": ml_label,
        "priority": ml_label,
        "criticality_score": round(crit, 4),
        "urgency_score": round(urg, 4),
        "impact_score": round(impact, 4),
        "risk_score": round(ml_risk, 4),
        "combined_score": round(combined, 4),
        "estimated_duration_minutes": task.estimated_duration_minutes,
        "required_resource_type": task.required_resource_type,
        "due_date": task.due_date.isoformat() if task.due_date else None,
        "status": task.status,
        "data_note": "Scores use a synthetic Random Forest plus transparent rule weights (demo).",
    }


def prioritized_tasks(
    db: Session,
    section: Optional[str] = None,
    weather: Optional[str] = "NORMAL",
) -> dict[str, Any]:
    stmt = (
        select(MaintenanceTask)
        .options(joinedload(MaintenanceTask.asset), joinedload(MaintenanceTask.department))
        .where(MaintenanceTask.status == TaskStatus.PENDING.value)
    )
    if section:
        stmt = stmt.where(MaintenanceTask.section == section)
    tasks = list(db.scalars(stmt).unique().all())
    ranked = [score_task(db, task, weather=weather) for task in tasks]
    ranked.sort(key=lambda row: row["combined_score"], reverse=True)
    for index, row in enumerate(ranked, start=1):
        row["rank"] = index
    db.commit()
    return {
        "section": section,
        "weather": enum_value(weather).upper() if weather else "NORMAL",
        "tasks": ranked,
        "data_note": "Demonstration ranking only. Not real railway failure prediction.",
    }
