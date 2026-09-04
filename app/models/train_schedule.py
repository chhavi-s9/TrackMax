from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import Date, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.train import Train


class TrainSchedule(Base):
    __tablename__ = "train_schedules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    train_id: Mapped[int] = mapped_column(ForeignKey("trains.id"), nullable=False, index=True)
    section: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    arrival_time: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    departure_time: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    schedule_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)

    train: Mapped["Train"] = relationship(back_populates="schedules")
