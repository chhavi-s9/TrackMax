from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from app.config import Settings, get_settings


@dataclass
class OptimizerWeights:
    critical_completed: float
    high_completed: float
    high_risk_coverage: float
    before_due: float
    resource_utilization: float
    asset_availability: float
    train_disruption: float
    passenger_impact: float
    freight_impact: float
    lateness: float
    extra_block_hours: float
    idle_resources: float

    @classmethod
    def from_settings(cls, settings: Optional[Settings] = None) -> "OptimizerWeights":
        s = settings or get_settings()
        return cls(
            critical_completed=s.weight_critical_completed,
            high_completed=s.weight_high_completed,
            high_risk_coverage=s.weight_high_risk_coverage,
            before_due=s.weight_before_due,
            resource_utilization=s.weight_resource_utilization,
            asset_availability=s.weight_asset_availability,
            train_disruption=s.weight_train_disruption,
            passenger_impact=s.weight_passenger_impact,
            freight_impact=s.weight_freight_impact,
            lateness=s.weight_lateness,
            extra_block_hours=s.weight_extra_block_hours,
            idle_resources=s.weight_idle_resources,
        )


@dataclass
class TaskCandidate:
    task_id: int
    section: str
    duration_minutes: int
    priority: str
    risk_score: float
    due_soon: bool
    resource_type: Optional[str]
    department: str = ""
    description: str = ""


@dataclass
class WindowCandidate:
    window_id: int
    section: str
    start: datetime
    end: datetime
    train_conflicts: int = 0
    passenger_trains: int = 0
    freight_trains: int = 0


@dataclass
class ResourceCandidate:
    resource_id: int
    resource_type: str
    section: str
    capacity: int
    available: bool = True


@dataclass
class ExistingBlock:
    block_id: int
    section: str
    start: datetime
    end: datetime


@dataclass
class SolveResult:
    status: str
    assignments: list[dict] = field(default_factory=list)
    optimization_score: float = 0.0
    train_disruption: int = 0
    reasoning: list[str] = field(default_factory=list)
    infeasible_reason: Optional[str] = None
