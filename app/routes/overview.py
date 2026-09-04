from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.overview_service import build_overview
from app.services.window_service import find_windows_from_db

router = APIRouter(tags=["Maintenance Overview"])


@router.get("/api/maintenance-overview")
def maintenance_overview(
    section: str = Query(...),
    horizon: str = Query("weekly"),
    db: Session = Depends(get_db),
):
    return build_overview(db, section=section, horizon=horizon)


@router.get("/api/windows")
def available_windows(
    section: str = Query(...),
    date: str = Query(..., description="YYYY-MM-DD"),
    duration_minutes: int = Query(120, gt=0),
    resource: Optional[str] = Query(default=None),
    weather: Optional[str] = Query(default="NORMAL"),
    db: Session = Depends(get_db),
):
    from datetime import date as date_cls

    day = date_cls.fromisoformat(date)
    return find_windows_from_db(
        db,
        section=section,
        day=day,
        duration_minutes=duration_minutes,
        resource_type=resource,
        weather_type=weather,
    )
