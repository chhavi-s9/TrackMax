from typing import Any, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.scenario_service import compare_scenarios

router = APIRouter(tags=["RailDoot compatibility"])


@router.get("/api/health")
def raildoot_health() -> dict[str, str]:
    return {"status": "ok", "data_mode": "synthetic_demo"}


@router.get("/api/scenarios")
def raildoot_scenarios() -> dict[str, Any]:
    return {
        "weather": ["FOG", "HEATWAVE", "HEAVY_RAIN", "NORMAL", "THUNDERSTORM"],
        "planning_modes": ["MANUAL", "COORDINATED", "AI_OPTIMIZED"],
        "synthetic_data": True,
    }


@router.get("/api/plan-comparison")
def raildoot_plan_comparison(
    section: str = Query("JP-AII"),
    scenario: Optional[str] = Query(default=None),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    result = compare_scenarios(db, section=section, scenario_type=scenario)
    scenarios = {
        "MANUAL": result["comparison"]["manual"],
        "COORDINATED": result["comparison"]["coordinated"],
        "AI_OPTIMIZED": result["comparison"]["ai"],
    }
    return {
        "synthetic_metric": True,
        "section": section,
        "scenarios": scenarios,
        "selected": result.get("selected"),
        "metrics": result.get("metrics"),
        "data_note": result["data_note"],
    }