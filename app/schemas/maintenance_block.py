from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.utils.enums import BlockStatus, BlockType


class MaintenanceBlockCreate(BaseModel):
    block_code: str = Field(min_length=1, max_length=64)
    section: str
    start_time: datetime
    end_time: datetime
    duration_minutes: Optional[int] = Field(default=None, gt=0)
    status: BlockStatus = BlockStatus.PROPOSED
    block_type: BlockType = BlockType.MAINTENANCE
    optimization_score: Optional[float] = None

    @model_validator(mode="after")
    def fill_duration(self) -> "MaintenanceBlockCreate":
        if self.end_time <= self.start_time:
            raise ValueError("end_time must be after start_time")
        if self.duration_minutes is None:
            self.duration_minutes = int((self.end_time - self.start_time).total_seconds() // 60)
        return self


class MaintenanceBlockUpdate(BaseModel):
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    duration_minutes: Optional[int] = Field(default=None, gt=0)
    status: Optional[BlockStatus] = None
    block_type: Optional[BlockType] = None
    optimization_score: Optional[float] = None
    section: Optional[str] = None


class MaintenanceBlockRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    block_code: str
    section: str
    start_time: datetime
    end_time: datetime
    duration_minutes: int
    status: str
    block_type: str
    optimization_score: Optional[float]
    created_at: datetime
