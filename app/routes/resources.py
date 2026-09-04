from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.resource import ResourceCreate, ResourceRead, ResourceUpdate
from app.services import maintenance_service as svc

router = APIRouter(prefix="/api/resources", tags=["Resources"])


@router.get("", response_model=list[ResourceRead])
def list_resources(section: Optional[str] = Query(default=None), db: Session = Depends(get_db)):
    return svc.list_resources(db, section=section)


@router.post("", response_model=ResourceRead, status_code=201)
def create_resource(payload: ResourceCreate, db: Session = Depends(get_db)):
    return svc.create_resource(db, payload)


@router.put("/{resource_id}", response_model=ResourceRead)
def update_resource(resource_id: int, payload: ResourceUpdate, db: Session = Depends(get_db)):
    return svc.update_resource(db, resource_id, payload)
