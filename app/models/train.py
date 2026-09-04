from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.train_schedule import TrainSchedule


class Train(Base):
    __tablename__ = "trains"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    train_number: Mapped[str] = mapped_column(String(16), nullable=False, unique=True, index=True)
    train_name: Mapped[str] = mapped_column(String(128), nullable=False)
    train_type: Mapped[str] = mapped_column(String(16), nullable=False, index=True)
    priority: Mapped[str] = mapped_column(String(16), nullable=False, index=True)
    operating_status: Mapped[str] = mapped_column(String(16), nullable=False, default="ACTIVE")

    schedules: Mapped[List["TrainSchedule"]] = relationship(back_populates="train")
