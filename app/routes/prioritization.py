from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.priority_service import prioritized_tasks

router = APIRouter(tags=["Prioritization"])


@router.get("/api/prioritized-tasks")
def get_prioritized_tasks(
    section: Optional[str] = Query(default=None),
    weather: str = Query("normal"),
    db: Session = Depends(get_db),
):
    return prioritized_tasks(db, section=section, weather=weather.upper())
