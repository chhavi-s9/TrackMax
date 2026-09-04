from datetime import date, datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import Date, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.department import Department
    from app.models.maintenance_task import MaintenanceTask


class Asset(Base):
    __tablename__ = "assets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    asset_code: Mapped[str] = mapped_column(String(64), nullable=False, unique=True, index=True)
    asset_type: Mapped[str] = mapped_column(String(64), nullable=False)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    section: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    location: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    department_id: Mapped[int] = mapped_column(
        ForeignKey("departments.id"), nullable=False, index=True
    )
    installation_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    last_maintenance_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    next_maintenance_due: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    condition_score: Mapped[float] = mapped_column(Float, nullable=False, default=70.0)
    failure_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    criticality: Mapped[str] = mapped_column(String(16), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, index=True, default="OPERATIONAL")
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    department: Mapped["Department"] = relationship(back_populates="assets")
    maintenance_tasks: Mapped[List["MaintenanceTask"]] = relationship(back_populates="asset")
