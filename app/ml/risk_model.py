from typing import Optional

import numpy as np
from sklearn.ensemble import RandomForestClassifier

from app.ml.feature_engineering import generate_synthetic_training_set
from app.ml.model_store import LABELS, load_model, save_model


def train_demo_model(n_samples: int = 800, seed: int = 42) -> RandomForestClassifier:
    """Train a RandomForestClassifier on synthetic demonstration data.

    This is not a real railway failure predictor.
    """
    X, y = generate_synthetic_training_set(n_samples=n_samples, seed=seed)
    model = RandomForestClassifier(
        n_estimators=120,
        max_depth=8,
        min_samples_leaf=4,
        random_state=seed,
        class_weight="balanced",
    )
    model.fit(X, y)
    save_model(model)
    return model


def predict_priority(features: np.ndarray) -> tuple[str, float]:
    model = load_model()
    if model is None:
        raise RuntimeError("Risk model file is missing")
    x = features.reshape(1, -1)
    cls = int(model.predict(x)[0])
    proba = model.predict_proba(x)[0]
    risk = float(proba[cls]) if len(proba) > cls else float(np.max(proba))
    rank_score = (cls + risk) / 4.0
    return LABELS[cls], min(1.0, rank_score)


def model_available() -> bool:
    return load_model() is not None
