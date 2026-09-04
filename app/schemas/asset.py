from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.utils.enums import AssetStatus, Priority


class AssetCreate(BaseModel):
    asset_code: str = Field(min_length=1, max_length=64)
    asset_type: str
    name: str
    section: str
    location: Optional[str] = None
    department_id: int
    installation_date: Optional[date] = None
    last_maintenance_date: Optional[date] = None
    next_maintenance_due: Optional[date] = None
    condition_score: float = Field(ge=0, le=100, default=70)
    failure_count: int = Field(ge=0, default=0)
    criticality: Priority = Priority.MEDIUM
    status: AssetStatus = AssetStatus.OPERATIONAL


class AssetUpdate(BaseModel):
    name: Optional[str] = None
    location: Optional[str] = None
    last_maintenance_date: Optional[date] = None
    next_maintenance_due: Optional[date] = None
    condition_score: Optional[float] = Field(default=None, ge=0, le=100)
    failure_count: Optional[int] = Field(default=None, ge=0)
    criticality: Optional[Priority] = None
    status: Optional[AssetStatus] = None
    department_id: Optional[int] = None
    section: Optional[str] = None


class AssetRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    asset_code: str
    asset_type: str
    name: str
    section: str
    location: Optional[str]
    department_id: int
    installation_date: Optional[date]
    last_maintenance_date: Optional[date]
    next_maintenance_due: Optional[date]
    condition_score: float
    failure_count: int
    criticality: str
    status: str
    created_at: datetime
    updated_at: datetime
