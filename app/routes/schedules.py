from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.train_schedule import TrainScheduleCreate, TrainScheduleRead
from app.services import maintenance_service as svc

router = APIRouter(prefix="/api/schedules", tags=["Schedules"])


@router.get("", response_model=list[TrainScheduleRead])
def list_schedules(
    section: Optional[str] = Query(default=None),
    schedule_date: Optional[date] = Query(default=None),
    db: Session = Depends(get_db),
):
    return svc.list_schedules(db, section=section, schedule_date=schedule_date)


@router.post("", response_model=TrainScheduleRead, status_code=201)
def create_schedule(payload: TrainScheduleCreate, db: Session = Depends(get_db)):
    return svc.create_schedule(db, payload)
