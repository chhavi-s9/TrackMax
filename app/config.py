from functools import lru_cache
from typing import Dict, List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration loaded from environment variables / `.env`."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    database_url: str
    app_name: str = "Railway Block Planning API"
    debug: bool = False

    # Soft-objective weights for the OR-Tools scheduler (not ML).
    weight_critical_completed: float = 25.0
    weight_high_completed: float = 15.0
    weight_high_risk_coverage: float = 12.0
    weight_before_due: float = 10.0
    weight_resource_utilization: float = 8.0
    weight_asset_availability: float = 10.0
    weight_train_disruption: float = 20.0
    weight_passenger_impact: float = 12.0
    weight_freight_impact: float = 8.0
    weight_lateness: float = 10.0
    weight_extra_block_hours: float = 8.0
    weight_idle_resources: float = 5.0

    # Ranked-task blend (ML is only one component).
    rank_weight_ml_risk: float = 0.35
    rank_weight_criticality: float = 0.25
    rank_weight_urgency: float = 0.25
    rank_weight_impact: float = 0.15

    operating_day_start: str = "00:00"
    operating_day_end: str = "23:59"
    window_slot_minutes: int = 30
    solver_max_time_seconds: float = 8.0

    # Weather rule keywords (task description / type matching). Configurable, not hardcoded in services.
    weather_rules: Dict[str, Dict[str, List[str]]] = Field(
        default_factory=lambda: {
            "HEAVY_RAIN": {
                "boost_keywords": [
                    "drainage",
                    "track stability",
                    "track inspection",
                    "electrical insulation",
                    "embankment",
                ],
                "restrict_keywords": ["hot work", "welding", "rail grinding"],
            },
            "HEATWAVE": {
                "boost_keywords": [
                    "buckling",
                    "rail temperature",
                    "ohe",
                    "tension",
                    "track inspection",
                ],
                "restrict_keywords": [],
            },
            "FOG": {
                "boost_keywords": [
                    "signal visibility",
                    "s&t",
                    "signal",
                    "visibility",
                    "telecommunication",
                ],
                "restrict_keywords": [],
            },
            "THUNDERSTORM": {
                "boost_keywords": ["electrical", "ohe", "insulation", "signal"],
                "restrict_keywords": ["height", "ohe installation"],
            },
            "NORMAL": {
                "boost_keywords": [],
                "restrict_keywords": [],
            },
        }
    )
    weather_boost_factor: float = 0.18
    weather_restrict_blocks: bool = True


@lru_cache
def get_settings() -> Settings:
    return Settings()
