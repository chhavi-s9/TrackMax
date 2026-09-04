from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.maintenance_block import MaintenanceBlockCreate, MaintenanceBlockRead, MaintenanceBlockUpdate
from app.services import maintenance_service as svc
from app.services.overview_service import validate_proposed_block

router = APIRouter(prefix="/api/blocks", tags=["Blocks"])


class BlockValidateRequest(BaseModel):
    section: str
    start_time: datetime
    end_time: datetime
    duration_minutes: int = Field(gt=0)
    required_resource_type: Optional[str] = None
    weather: Optional[str] = None


@router.get("", response_model=list[MaintenanceBlockRead])
def list_blocks(section: Optional[str] = Query(default=None), db: Session = Depends(get_db)):
    return svc.list_blocks(db, section=section)


@router.get("/{block_id}", response_model=MaintenanceBlockRead)
def get_block(block_id: int, db: Session = Depends(get_db)):
    return svc.get_block(db, block_id)


@router.post("", response_model=MaintenanceBlockRead, status_code=201)
def create_block(payload: MaintenanceBlockCreate, db: Session = Depends(get_db)):
    return svc.create_block(db, payload)


@router.put("/{block_id}", response_model=MaintenanceBlockRead)
def update_block(block_id: int, payload: MaintenanceBlockUpdate, db: Session = Depends(get_db)):
    return svc.update_block(db, block_id, payload)


@router.post("/validate")
def validate_block(payload: BlockValidateRequest, db: Session = Depends(get_db)):
    return validate_proposed_block(
        db,
        section=payload.section,
        start=payload.start_time,
        end=payload.end_time,
        duration_minutes=payload.duration_minutes,
        resource_type=payload.required_resource_type,
        weather=payload.weather,
    )
