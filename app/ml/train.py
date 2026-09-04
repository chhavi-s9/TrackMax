"""Train the demonstration Random Forest risk/priority model."""

from app.ml.risk_model import train_demo_model


def main() -> None:
    model = train_demo_model()
    print("Trained demonstration RandomForestClassifier (synthetic data only).")
    print(f"Classes: {list(model.classes_)}")
    print("Saved to models/risk_model.joblib")


if __name__ == "__main__":
    main()
