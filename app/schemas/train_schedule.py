from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator


class TrainScheduleCreate(BaseModel):
    train_id: int
    section: str
    arrival_time: datetime
    departure_time: datetime
    schedule_date: date

    @model_validator(mode="after")
    def check_times(self) -> "TrainScheduleCreate":
        if self.departure_time < self.arrival_time:
            raise ValueError("departure_time must be on or after arrival_time")
        return self


class TrainScheduleRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    train_id: int
    section: str
    arrival_time: datetime
    departure_time: datetime
    schedule_date: date
