from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.utils.enums import ResourceStatus


class ResourceCreate(BaseModel):
    resource_code: str = Field(min_length=1, max_length=64)
    name: str
    resource_type: str
    department_id: int
    section: str
    capacity: int = Field(ge=1, default=1)
    status: ResourceStatus = ResourceStatus.AVAILABLE
    available_from: Optional[datetime] = None
    available_until: Optional[datetime] = None


class ResourceUpdate(BaseModel):
    name: Optional[str] = None
    resource_type: Optional[str] = None
    section: Optional[str] = None
    capacity: Optional[int] = Field(default=None, ge=1)
    status: Optional[ResourceStatus] = None
    available_from: Optional[datetime] = None
    available_until: Optional[datetime] = None
    department_id: Optional[int] = None


class ResourceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    resource_code: str
    name: str
    resource_type: str
    department_id: int
    section: str
    capacity: int
    status: str
    available_from: Optional[datetime]
    available_until: Optional[datetime]
