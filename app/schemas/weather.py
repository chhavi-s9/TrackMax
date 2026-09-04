from datetime import date
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.utils.enums import WeatherType


class WeatherCreate(BaseModel):
    section: str
    date: date
    weather_type: WeatherType
    severity: int = Field(ge=0, le=100, default=0)
    rainfall: Optional[float] = None
    temperature: Optional[float] = None
    visibility: Optional[float] = None
    description: Optional[str] = None


class WeatherRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    section: str
    date: date
    weather_type: str
    severity: int
    rainfall: Optional[float]
    temperature: Optional[float]
    visibility: Optional[float]
    description: Optional[str]


class WeatherRescheduleRequest(BaseModel):
    section: str
    date: date
    weather: WeatherType
