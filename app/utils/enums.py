from enum import Enum


class AssetStatus(str, Enum):
    OPERATIONAL = "OPERATIONAL"
    DEGRADED = "DEGRADED"
    UNDER_MAINTENANCE = "UNDER_MAINTENANCE"
    FAILED = "FAILED"


class Priority(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class TaskStatus(str, Enum):
    PENDING = "PENDING"
    SCHEDULED = "SCHEDULED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class SourceSystem(str, Enum):
    TMS = "TMS"
    SMMS = "SMMS"
    TDMS = "TDMS"
    INTERNAL = "INTERNAL"


class ResourceStatus(str, Enum):
    AVAILABLE = "AVAILABLE"
    BUSY = "BUSY"
    UNAVAILABLE = "UNAVAILABLE"


class TrainType(str, Enum):
    PASSENGER = "PASSENGER"
    EXPRESS = "EXPRESS"
    FREIGHT = "FREIGHT"
    OTHER = "OTHER"


class OperatingStatus(str, Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    CANCELLED = "CANCELLED"


class BlockStatus(str, Enum):
    PROPOSED = "PROPOSED"
    APPROVED = "APPROVED"
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class BlockType(str, Enum):
    MAINTENANCE = "MAINTENANCE"
    EMERGENCY = "EMERGENCY"
    INSPECTION = "INSPECTION"
    COORDINATED = "COORDINATED"


class WeatherType(str, Enum):
    NORMAL = "NORMAL"
    HEAVY_RAIN = "HEAVY_RAIN"
    HEATWAVE = "HEATWAVE"
    FOG = "FOG"
    THUNDERSTORM = "THUNDERSTORM"


class Horizon(str, Enum):
    WEEKLY = "weekly"
    MONTHLY = "monthly"


class ScenarioType(str, Enum):
    MANUAL = "manual"
    COORDINATED = "coordinated"
    AI = "ai"


class ConflictType(str, Enum):
    TRAIN_CONFLICT = "TRAIN_CONFLICT"
    BLOCK_OVERLAP = "BLOCK_OVERLAP"
    RESOURCE_UNAVAILABLE = "RESOURCE_UNAVAILABLE"
    DURATION_INSUFFICIENT = "DURATION_INSUFFICIENT"
    SECTION_MISMATCH = "SECTION_MISMATCH"
    ASSET_CONFLICT = "ASSET_CONFLICT"
    WEATHER_RESTRICTION = "WEATHER_RESTRICTION"
