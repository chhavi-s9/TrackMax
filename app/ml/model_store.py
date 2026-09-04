from pathlib import Path

import joblib

MODEL_PATH = Path(__file__).resolve().parents[2] / "models" / "risk_model.joblib"

LABELS = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]


def save_model(model) -> Path:
    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    return MODEL_PATH


def load_model():
    if not MODEL_PATH.exists():
        return None
    return joblib.load(MODEL_PATH)
