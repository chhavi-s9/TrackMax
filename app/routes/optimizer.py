from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.planning_service import monthly_plan, run_optimizer_for_section, weekly_plan

router = APIRouter(tags=["Optimizer"])


@router.post("/api/optimizer/run")
def run_optimizer(
    section: str = Query(...),
    weather: str = Query("NORMAL"),
    plan_date: Optional[date] = Query(default=None),
    db: Session = Depends(get_db),
):
    return run_optimizer_for_section(db, section=section, weather=weather, day=plan_date)


@router.get("/api/weekly-plan")
def get_weekly_plan(
    section: str = Query(...),
    weather: str = Query("NORMAL"),
    db: Session = Depends(get_db),
):
    return weekly_plan(db, section=section, weather=weather)


@router.get("/api/monthly-plan")
def get_monthly_plan(
    section: Optional[str] = Query(default=None),
    db: Session = Depends(get_db),
):
    return monthly_plan(db, section=section)
