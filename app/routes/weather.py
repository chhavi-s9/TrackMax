from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.weather import WeatherCreate, WeatherRead, WeatherRescheduleRequest
from app.services.weather_service import list_weather, reschedule_for_weather, upsert_weather

router = APIRouter(tags=["Weather"])


@router.get("/api/weather", response_model=list[WeatherRead])
def get_weather(section: Optional[str] = Query(default=None), db: Session = Depends(get_db)):
    return list_weather(db, section=section)


@router.post("/api/weather", response_model=WeatherRead, status_code=201)
def create_weather(payload: WeatherCreate, db: Session = Depends(get_db)):
    return upsert_weather(db, payload)


@router.post("/api/weather/reschedule")
def weather_reschedule(payload: WeatherRescheduleRequest, db: Session = Depends(get_db)):
    return reschedule_for_weather(
        db,
        section=payload.section,
        day=payload.date,
        weather=payload.weather.value,
    )
