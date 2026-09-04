from datetime import date

import numpy as np

from app.ml.feature_engineering import FEATURE_NAMES, generate_synthetic_training_set, task_features
from app.ml.risk_model import train_demo_model, predict_priority, model_available
from app.ml.model_store import LABELS


def test_ml_prediction() -> None:
    train_demo_model(n_samples=200, seed=1)
    assert model_available()
    features = task_features(
        as_of=date(2026, 9, 5),
        installation_date=date(2010, 1, 1),
        last_maintenance_date=date(2025, 1, 1),
        due_date=date(2026, 8, 1),
        condition_score=40,
        failure_count=8,
        criticality="CRITICAL",
        maintenance_frequency=5,
        train_density=0.8,
        duration_minutes=120,
    )
    assert features.shape == (len(FEATURE_NAMES),)
    label, risk = predict_priority(features)
    assert label in LABELS
    assert 0 <= risk <= 1


def test_synthetic_training_labels() -> None:
    X, y = generate_synthetic_training_set(n_samples=50, seed=0)
    assert X.shape[0] == 50
    assert set(y).issubset({0, 1, 2, 3})
