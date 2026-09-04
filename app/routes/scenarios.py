from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.scenario_service import compare_scenarios

router = APIRouter(tags=["Scenarios"])


@router.get("/api/scenario")
def get_scenario(
    section: str = Query(...),
    type: Optional[str] = Query(default=None, description="manual | coordinated | ai"),
    db: Session = Depends(get_db),
):
    return compare_scenarios(db, section=section, scenario_type=type)
