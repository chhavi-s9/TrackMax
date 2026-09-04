from typing import Optional

from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.maintenance_task import MaintenanceTaskCreate, MaintenanceTaskRead, MaintenanceTaskUpdate
from app.services import maintenance_service as svc

router = APIRouter(prefix="/api/maintenance/tasks", tags=["Maintenance"])


@router.get("", response_model=list[MaintenanceTaskRead])
def list_tasks(
    section: Optional[str] = Query(default=None),
    status: Optional[str] = Query(default=None),
    db: Session = Depends(get_db),
):
    return svc.list_tasks(db, section=section, status=status)


@router.get("/{task_id}", response_model=MaintenanceTaskRead)
def get_task(task_id: int, db: Session = Depends(get_db)):
    return svc.get_task(db, task_id)


@router.post("", response_model=MaintenanceTaskRead, status_code=201)
def create_task(payload: MaintenanceTaskCreate, db: Session = Depends(get_db)):
    return svc.create_task(db, payload)


@router.put("/{task_id}", response_model=MaintenanceTaskRead)
def update_task(task_id: int, payload: MaintenanceTaskUpdate, db: Session = Depends(get_db)):
    return svc.update_task(db, task_id, payload)


@router.delete("/{task_id}", status_code=204)
def delete_task(task_id: int, db: Session = Depends(get_db)):
    svc.delete_task(db, task_id)
    return Response(status_code=204)
