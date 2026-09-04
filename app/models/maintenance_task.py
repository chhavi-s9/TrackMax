from datetime import date, datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Date, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.asset import Asset
    from app.models.department import Department
    from app.models.maintenance_block import MaintenanceBlock


class MaintenanceTask(Base):
    __tablename__ = "maintenance_tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    task_code: Mapped[str] = mapped_column(String(64), nullable=False, unique=True, index=True)
    asset_id: Mapped[int] = mapped_column(ForeignKey("assets.id"), nullable=False, index=True)
    department_id: Mapped[int] = mapped_column(
        ForeignKey("departments.id"), nullable=False, index=True
    )
    source_system: Mapped[str] = mapped_column(String(16), nullable=False, index=True)
    task_type: Mapped[str] = mapped_column(String(64), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    section: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    priority: Mapped[str] = mapped_column(String(16), nullable=False, index=True)
    estimated_duration_minutes: Mapped[int] = mapped_column(Integer, nullable=False)
    due_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True, index=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, index=True, default="PENDING")
    required_resource_type: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    risk_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    block_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("maintenance_blocks.id"), nullable=True, index=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    asset: Mapped["Asset"] = relationship(back_populates="maintenance_tasks")
    department: Mapped["Department"] = relationship(back_populates="maintenance_tasks")
    block: Mapped[Optional["MaintenanceBlock"]] = relationship(back_populates="tasks")
