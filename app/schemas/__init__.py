from app.schemas.asset import AssetCreate, AssetRead, AssetUpdate
from app.schemas.department import DepartmentCreate, DepartmentRead
from app.schemas.maintenance_block import (
    MaintenanceBlockCreate,
    MaintenanceBlockRead,
    MaintenanceBlockUpdate,
)
from app.schemas.maintenance_task import (
    MaintenanceTaskCreate,
    MaintenanceTaskRead,
    MaintenanceTaskUpdate,
)
from app.schemas.resource import ResourceCreate, ResourceRead, ResourceUpdate
from app.schemas.train import TrainCreate, TrainRead
from app.schemas.train_schedule import TrainScheduleCreate, TrainScheduleRead
from app.schemas.weather import WeatherCreate, WeatherRead, WeatherRescheduleRequest

__all__ = [
    "DepartmentCreate",
    "DepartmentRead",
    "AssetCreate",
    "AssetRead",
    "AssetUpdate",
    "MaintenanceTaskCreate",
    "MaintenanceTaskRead",
    "MaintenanceTaskUpdate",
    "ResourceCreate",
    "ResourceRead",
    "ResourceUpdate",
    "TrainCreate",
    "TrainRead",
    "TrainScheduleCreate",
    "TrainScheduleRead",
    "MaintenanceBlockCreate",
    "MaintenanceBlockRead",
    "MaintenanceBlockUpdate",
    "WeatherCreate",
    "WeatherRead",
    "WeatherRescheduleRequest",
]
