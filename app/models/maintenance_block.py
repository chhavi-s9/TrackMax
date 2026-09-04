from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import DateTime, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.maintenance_task import MaintenanceTask


class MaintenanceBlock(Base):
    __tablename__ = "maintenance_blocks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    block_code: Mapped[str] = mapped_column(String(64), nullable=False, unique=True, index=True)
    section: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    start_time: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    end_time: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    duration_minutes: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, index=True, default="PROPOSED")
    block_type: Mapped[str] = mapped_column(String(32), nullable=False, default="MAINTENANCE")
    optimization_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)

    tasks: Mapped[List["MaintenanceTask"]] = relationship(back_populates="block")
