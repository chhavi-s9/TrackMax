from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.exceptions import BadRequestError, NotFoundError
from app.models.asset import Asset
from app.models.department import Department
from app.models.maintenance_block import MaintenanceBlock
from app.models.maintenance_task import MaintenanceTask
from app.models.resource import Resource
from app.models.train import Train
from app.models.train_schedule import TrainSchedule
from app.schemas.asset import AssetCreate, AssetUpdate
from app.schemas.department import DepartmentCreate
from app.schemas.maintenance_block import MaintenanceBlockCreate, MaintenanceBlockUpdate
from app.schemas.maintenance_task import MaintenanceTaskCreate, MaintenanceTaskUpdate
from app.schemas.resource import ResourceCreate, ResourceUpdate
from app.schemas.train import TrainCreate
from app.schemas.train_schedule import TrainScheduleCreate
from app.services import apply_updates, commit_or_conflict, dump_enums, get_or_404, list_all


def list_departments(db: Session) -> list[Department]:
    return list_all(db, Department)


def get_department(db: Session, department_id: int) -> Department:
    return get_or_404(db, Department, department_id, "Department")


def create_department(db: Session, payload: DepartmentCreate) -> Department:
    obj = Department(**payload.model_dump())
    return commit_or_conflict(db, obj, "Department name or code already exists")


def list_assets(db: Session, section: Optional[str] = None) -> list[Asset]:
    stmt = select(Asset)
    if section:
        stmt = stmt.where(Asset.section == section)
    return list(db.scalars(stmt).all())


def get_asset(db: Session, asset_id: int) -> Asset:
    return get_or_404(db, Asset, asset_id, "Asset")


def create_asset(db: Session, payload: AssetCreate) -> Asset:
    get_department(db, payload.department_id)
    data = dump_enums(payload.model_dump())
    return commit_or_conflict(db, Asset(**data), "Asset code already exists")


def update_asset(db: Session, asset_id: int, payload: AssetUpdate) -> Asset:
    obj = get_asset(db, asset_id)
    apply_updates(obj, payload.model_dump(exclude_unset=True))
    db.commit()
    db.refresh(obj)
    return obj


def delete_asset(db: Session, asset_id: int) -> None:
    obj = get_asset(db, asset_id)
    db.delete(obj)
    db.commit()


def list_tasks(
    db: Session,
    section: Optional[str] = None,
    status: Optional[str] = None,
) -> list[MaintenanceTask]:
    stmt = select(MaintenanceTask)
    if section:
        stmt = stmt.where(MaintenanceTask.section == section)
    if status:
        stmt = stmt.where(MaintenanceTask.status == status)
    return list(db.scalars(stmt).all())


def get_task(db: Session, task_id: int) -> MaintenanceTask:
    return get_or_404(db, MaintenanceTask, task_id, "Maintenance task")


def create_task(db: Session, payload: MaintenanceTaskCreate) -> MaintenanceTask:
    get_asset(db, payload.asset_id)
    get_department(db, payload.department_id)
    data = dump_enums(payload.model_dump())
    return commit_or_conflict(db, MaintenanceTask(**data), "Task code already exists")


def update_task(db: Session, task_id: int, payload: MaintenanceTaskUpdate) -> MaintenanceTask:
    obj = get_task(db, task_id)
    apply_updates(obj, payload.model_dump(exclude_unset=True))
    db.commit()
    db.refresh(obj)
    return obj


def delete_task(db: Session, task_id: int) -> None:
    obj = get_task(db, task_id)
    db.delete(obj)
    db.commit()


def list_resources(db: Session, section: Optional[str] = None) -> list[Resource]:
    stmt = select(Resource)
    if section:
        stmt = stmt.where(Resource.section == section)
    return list(db.scalars(stmt).all())


def get_resource(db: Session, resource_id: int) -> Resource:
    return get_or_404(db, Resource, resource_id, "Resource")


def create_resource(db: Session, payload: ResourceCreate) -> Resource:
    get_department(db, payload.department_id)
    data = dump_enums(payload.model_dump())
    return commit_or_conflict(db, Resource(**data), "Resource code already exists")


def update_resource(db: Session, resource_id: int, payload: ResourceUpdate) -> Resource:
    obj = get_resource(db, resource_id)
    apply_updates(obj, payload.model_dump(exclude_unset=True))
    db.commit()
    db.refresh(obj)
    return obj


def list_trains(db: Session) -> list[Train]:
    return list_all(db, Train)


def get_train(db: Session, train_id: int) -> Train:
    return get_or_404(db, Train, train_id, "Train")


def create_train(db: Session, payload: TrainCreate) -> Train:
    data = dump_enums(payload.model_dump())
    return commit_or_conflict(db, Train(**data), "Train number already exists")


def list_schedules(
    db: Session,
    section: Optional[str] = None,
    schedule_date=None,
) -> list[TrainSchedule]:
    stmt = select(TrainSchedule)
    if section:
        stmt = stmt.where(TrainSchedule.section == section)
    if schedule_date is not None:
        stmt = stmt.where(TrainSchedule.schedule_date == schedule_date)
    return list(db.scalars(stmt.order_by(TrainSchedule.arrival_time)).all())


def create_schedule(db: Session, payload: TrainScheduleCreate) -> TrainSchedule:
    get_train(db, payload.train_id)
    obj = TrainSchedule(**payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def list_blocks(db: Session, section: Optional[str] = None) -> list[MaintenanceBlock]:
    stmt = select(MaintenanceBlock)
    if section:
        stmt = stmt.where(MaintenanceBlock.section == section)
    return list(db.scalars(stmt).all())


def get_block(db: Session, block_id: int) -> MaintenanceBlock:
    return get_or_404(db, MaintenanceBlock, block_id, "Maintenance block")


def create_block(db: Session, payload: MaintenanceBlockCreate) -> MaintenanceBlock:
    data = dump_enums(payload.model_dump())
    return commit_or_conflict(db, MaintenanceBlock(**data), "Block code already exists")


def update_block(db: Session, block_id: int, payload: MaintenanceBlockUpdate) -> MaintenanceBlock:
    obj = get_block(db, block_id)
    apply_updates(obj, payload.model_dump(exclude_unset=True))
    if obj.end_time <= obj.start_time:
        db.rollback()
        raise BadRequestError("end_time must be after start_time")
    obj.duration_minutes = int((obj.end_time - obj.start_time).total_seconds() // 60)
    db.commit()
    db.refresh(obj)
    return obj
