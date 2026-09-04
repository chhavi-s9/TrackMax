"""Phase 12 pipeline without requiring MySQL: task → risk → windows → conflicts → CP-SAT → weather."""

from datetime import date, datetime, timedelta
from types import SimpleNamespace

from app.ml.feature_engineering import task_features, urgency_score, criticality_score, impact_score
from app.ml.risk_model import train_demo_model, predict_priority
from app.optimizer.block_optimizer import solve_block_plan
from app.optimizer.scoring import ResourceCandidate, TaskCandidate, WindowCandidate
from app.services.conflict_service import detect_conflicts
from app.services.window_service import find_windows
from app.config import get_settings


def test_end_to_end_pipeline() -> None:
    train_demo_model(n_samples=250, seed=7)

    features = task_features(
        as_of=date(2026, 9, 5),
        installation_date=date(2012, 6, 1),
        last_maintenance_date=date(2026, 3, 1),
        due_date=date(2026, 9, 6),
        condition_score=45,
        failure_count=5,
        criticality="HIGH",
        maintenance_frequency=3,
        train_density=0.6,
        duration_minutes=120,
    )
    ml_label, ml_risk = predict_priority(features)
    assert ml_label in {"LOW", "MEDIUM", "HIGH", "CRITICAL"}

    crit = criticality_score("HIGH", 45)
    urg = urgency_score(date(2026, 9, 5), date(2026, 9, 6))
    impact = impact_score(0.6, 120)
    combined = 0.35 * ml_risk + 0.25 * crit + 0.25 * urg + 0.15 * impact
    assert combined > 0

    schedules = [
        SimpleNamespace(
            section="JP-AII",
            arrival_time=datetime(2026, 9, 5, 11, 20),
            departure_time=datetime(2026, 9, 5, 11, 35),
            train_id=1,
        )
    ]
    resources = [
        SimpleNamespace(
            resource_type="track_gang",
            status="AVAILABLE",
            section="JP-AII",
            available_from=None,
            available_until=None,
        )
    ]
    windows_payload = find_windows(
        section="JP-AII",
        day=date(2026, 9, 5),
        duration_minutes=120,
        schedules=schedules,
        existing_blocks=[],
        resources=resources,
        required_resource_type="track_gang",
    )
    assert windows_payload["windows"]

    blocked = detect_conflicts(
        section="JP-AII",
        start_time=datetime(2026, 9, 5, 11, 0),
        end_time=datetime(2026, 9, 5, 13, 0),
        duration_minutes=120,
        schedules=schedules,
        existing_blocks=[],
        resources=resources,
        required_resource_type="track_gang",
        trains={1: SimpleNamespace(train_number="12956")},
    )
    assert blocked["valid"] is False

    chosen = windows_payload["windows"][0]
    start = datetime.strptime(f"2026-09-05 {chosen['start']}", "%Y-%m-%d %H:%M")
    end = datetime.strptime(f"2026-09-05 {chosen['end']}", "%Y-%m-%d %H:%M")
    result = solve_block_plan(
        tasks=[
            TaskCandidate(
                task_id=12,
                section="JP-AII",
                duration_minutes=120,
                priority=ml_label,
                risk_score=ml_risk,
                due_soon=True,
                resource_type="track_gang",
            )
        ],
        windows=[
            WindowCandidate(window_id=1, section="JP-AII", start=start, end=end, train_conflicts=0)
        ],
        resources=[
            ResourceCandidate(
                resource_id=4,
                resource_type="track_gang",
                section="JP-AII",
                capacity=1,
                available=True,
            )
        ],
    )
    assert result.status in {"OPTIMAL", "FEASIBLE"}
    original = (result.assignments[0]["start_time"], result.assignments[0]["end_time"])

    rules = get_settings().weather_rules["HEAVY_RAIN"]
    blob = "drainage track stability inspection"
    boosted = any(k in blob for k in rules["boost_keywords"])
    assert boosted
    # Weather change can keep the same feasible window; it must not invent a fake OPTIMAL.
    rain_result = solve_block_plan(
        tasks=[
            TaskCandidate(
                task_id=12,
                section="JP-AII",
                duration_minutes=120,
                priority="CRITICAL",
                risk_score=min(1.0, ml_risk + 0.18),
                due_soon=True,
                resource_type="track_gang",
            )
        ],
        windows=[
            WindowCandidate(window_id=1, section="JP-AII", start=start, end=end, train_conflicts=0)
        ],
        resources=[
            ResourceCandidate(
                resource_id=4,
                resource_type="track_gang",
                section="JP-AII",
                capacity=1,
                available=True,
            )
        ],
    )
    assert rain_result.status in {"OPTIMAL", "FEASIBLE"}
    assert rain_result.assignments
    assert original  # original recommended block captured
