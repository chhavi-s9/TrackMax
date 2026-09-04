from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.utils.enums import OperatingStatus, Priority, TrainType


class TrainCreate(BaseModel):
    train_number: str = Field(min_length=1, max_length=16)
    train_name: str
    train_type: TrainType
    priority: Priority = Priority.MEDIUM
    operating_status: OperatingStatus = OperatingStatus.ACTIVE


class TrainRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    train_number: str
    train_name: str
    train_type: str
    priority: str
    operating_status: str
