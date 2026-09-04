from datetime import datetime, timedelta
from types import SimpleNamespace

from app.services.conflict_service import detect_conflicts
from app.services.window_service import find_windows


def _sched(section, hour, minute=0, dwell=15):
    start = datetime(2026, 9, 5, hour, minute)
    return SimpleNamespace(
        section=section,
        arrival_time=start,
        departure_time=start + timedelta(minutes=dwell),
        train_id=1,
    )


def _block(section, start_h, end_h, status="APPROVED"):
    return SimpleNamespace(
        id=1,
        block_code="BLK-X",
        section=section,
        start_time=datetime(2026, 9, 5, start_h, 0),
        end_time=datetime(2026, 9, 5, end_h, 0),
        status=status,
    )


def _resource(available=True, rtype="track_gang", section="JP-AII"):
    return SimpleNamespace(
        resource_type=rtype,
        status="AVAILABLE" if available else "UNAVAILABLE",
        section=section,
        available_from=None,
        available_until=None,
    )


def test_conflict_train_overlap() -> None:
    result = detect_conflicts(
        section="JP-AII",
        start_time=datetime(2026, 9, 5, 11, 0),
        end_time=datetime(2026, 9, 5, 12, 0),
        duration_minutes=60,
        schedules=[_sched("JP-AII", 11, 20)],
        existing_blocks=[],
        resources=[_resource()],
        trains={1: SimpleNamespace(train_number="12956")},
    )
    assert result["valid"] is False
    assert result["conflicts"][0]["type"] == "TRAIN_CONFLICT"
    assert result["conflicts"][0]["train_number"] == "12956"


def test_conflict_resource_unavailable() -> None:
    result = detect_conflicts(
        section="JP-AII",
        start_time=datetime(2026, 9, 5, 13, 0),
        end_time=datetime(2026, 9, 5, 15, 0),
        duration_minutes=120,
        schedules=[],
        existing_blocks=[],
        resources=[_resource(available=False)],
        required_resource_type="track_gang",
    )
    assert result["valid"] is False
    assert any(c["type"] == "RESOURCE_UNAVAILABLE" for c in result["conflicts"])


def test_window_generation_avoids_trains() -> None:
    payload = find_windows(
        section="JP-AII",
        day=datetime(2026, 9, 5).date(),
        duration_minutes=90,
        schedules=[_sched("JP-AII", 11, 0, dwell=30)],
        existing_blocks=[],
        resources=[_resource()],
        required_resource_type="track_gang",
    )
    assert payload["windows"]
    for win in payload["windows"]:
        assert win["train_conflicts"] == 0
        start_h, start_m = [int(p) for p in win["start"].split(":")]
        end_h, end_m = [int(p) for p in win["end"].split(":")]
        start_min = start_h * 60 + start_m
        end_min = end_h * 60 + end_m
        # The 11:00-11:30 train must not sit inside a returned free window.
        assert not (start_min < 11 * 60 + 30 and end_min > 11 * 60)
