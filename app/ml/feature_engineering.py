from datetime import date
from typing import Optional

import numpy as np

from app.utils.time_utils import clamp01


FEATURE_NAMES = [
    "asset_age_years",
    "condition_score",
    "failure_count",
    "days_since_maintenance",
    "days_overdue",
    "criticality",
    "maintenance_frequency",
    "train_density",
    "task_duration_hours",
]

CRITICALITY_MAP = {"LOW": 0.25, "MEDIUM": 0.5, "HIGH": 0.75, "CRITICAL": 1.0}


def _days_between(later: Optional[date], earlier: Optional[date]) -> float:
    if later is None or earlier is None:
        return 0.0
    return float((later - earlier).days)


def task_features(
    *,
    as_of: date,
    installation_date: Optional[date],
    last_maintenance_date: Optional[date],
    due_date: Optional[date],
    condition_score: float,
    failure_count: int,
    criticality: str,
    maintenance_frequency: float,
    train_density: float,
    duration_minutes: int,
) -> np.ndarray:
    age_years = max(_days_between(as_of, installation_date) / 365.0, 0.0)
    days_since = _days_between(as_of, last_maintenance_date) if last_maintenance_date else 180.0
    days_overdue = max(_days_between(as_of, due_date), 0.0) if due_date and due_date < as_of else 0.0
    if due_date and due_date >= as_of:
        days_overdue = 0.0
    crit = CRITICALITY_MAP.get(criticality, 0.5)
    row = [
        age_years,
        float(condition_score) / 100.0,
        float(failure_count),
        days_since,
        days_overdue,
        crit,
        float(maintenance_frequency),
        float(train_density),
        float(duration_minutes) / 60.0,
    ]
    return np.array(row, dtype=float)


def generate_synthetic_training_set(n_samples: int = 800, seed: int = 42) -> tuple[np.ndarray, np.ndarray]:
    """Demonstration data only — not real railway failure observations."""
    rng = np.random.default_rng(seed)
    X = np.zeros((n_samples, len(FEATURE_NAMES)), dtype=float)
    y = np.zeros(n_samples, dtype=int)
    for i in range(n_samples):
        age = rng.uniform(0, 30)
        condition = rng.uniform(0.2, 1.0)
        failures = rng.integers(0, 12)
        days_since = rng.uniform(0, 400)
        days_overdue = rng.uniform(0, 90) if rng.random() < 0.35 else 0.0
        crit = rng.choice([0.25, 0.5, 0.75, 1.0])
        freq = rng.uniform(0, 8)
        density = rng.uniform(0, 1)
        duration = rng.uniform(0.5, 6)
        X[i] = [age, condition, failures, days_since, days_overdue, crit, freq, density, duration]
        score = (
            (1 - condition) * 2.2
            + min(failures, 10) * 0.18
            + min(days_overdue, 60) / 40.0
            + crit * 1.4
            + min(days_since, 365) / 400.0
            + density * 0.4
            + (age / 40.0)
        )
        if score >= 3.4:
            y[i] = 3  # CRITICAL
        elif score >= 2.4:
            y[i] = 2  # HIGH
        elif score >= 1.4:
            y[i] = 1  # MEDIUM
        else:
            y[i] = 0  # LOW
    return X, y


def urgency_score(as_of: date, due_date: Optional[date]) -> float:
    if due_date is None:
        return 0.4
    delta = (due_date - as_of).days
    if delta <= 0:
        return 1.0
    return clamp01(1.0 - delta / 30.0)


def criticality_score(criticality: str, condition_score: float) -> float:
    base = CRITICALITY_MAP.get(criticality, 0.5)
    degraded = clamp01((100.0 - condition_score) / 100.0)
    return clamp01(0.6 * base + 0.4 * degraded)


def impact_score(train_density: float, duration_minutes: int, train_type_weight: float = 0.5) -> float:
    duration_part = clamp01(duration_minutes / 240.0)
    return clamp01(0.5 * train_density + 0.3 * duration_part + 0.2 * train_type_weight)
