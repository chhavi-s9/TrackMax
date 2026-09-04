from datetime import datetime, time, timedelta
from typing import Any, Optional, Tuple


def parse_hhmm(value: str) -> time:
    hour, minute = value.split(":")
    return time(int(hour), int(minute))


def combine_date_time(day, clock: time) -> datetime:
    return datetime(day.year, day.month, day.day, clock.hour, clock.minute, clock.second)


def overlaps(
    start_a: datetime,
    end_a: datetime,
    start_b: datetime,
    end_b: datetime,
) -> bool:
    return start_a < end_b and start_b < end_a


def minutes_between(start: datetime, end: datetime) -> int:
    return int((end - start).total_seconds() // 60)


def format_hhmm(value: datetime) -> str:
    return value.strftime("%H:%M")


def enum_value(value: Any) -> str:
    return value.value if hasattr(value, "value") else str(value)


def clamp01(value: float) -> float:
    return max(0.0, min(1.0, value))
