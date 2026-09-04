from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.utils.enums import Priority, SourceSystem, TaskStatus


class MaintenanceTaskCreate(BaseModel):
    task_code: str = Field(min_length=1, max_length=64)
    asset_id: int
    department_id: int
    source_system: SourceSystem
    task_type: str
    description: Optional[str] = None
    section: str
    priority: Priority = Priority.MEDIUM
    estimated_duration_minutes: int = Field(gt=0)
    due_date: Optional[date] = None
    status: TaskStatus = TaskStatus.PENDING
    required_resource_type: Optional[str] = None
    risk_score: Optional[float] = Field(default=None, ge=0, le=1)
    block_id: Optional[int] = None


class MaintenanceTaskUpdate(BaseModel):
    description: Optional[str] = None
    priority: Optional[Priority] = None
    estimated_duration_minutes: Optional[int] = Field(default=None, gt=0)
    due_date: Optional[date] = None
    status: Optional[TaskStatus] = None
    required_resource_type: Optional[str] = None
    risk_score: Optional[float] = Field(default=None, ge=0, le=1)
    block_id: Optional[int] = None
    section: Optional[str] = None


class MaintenanceTaskRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    task_code: str
    asset_id: int
    department_id: int
    source_system: str
    task_type: str
    description: Optional[str]
    section: str
    priority: str
    estimated_duration_minutes: int
    due_date: Optional[date]
    status: str
    required_resource_type: Optional[str]
    risk_score: Optional[float]
    block_id: Optional[int]
    created_at: datetime
    updated_at: datetime
