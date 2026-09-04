from app.config import get_settings
from app.utils.time_utils import clamp01


def test_weather_rules_are_configurable() -> None:
    rules = get_settings().weather_rules
    assert "HEAVY_RAIN" in rules
    assert "drainage" in [k.lower() for k in rules["HEAVY_RAIN"]["boost_keywords"]]
    assert "HEATWAVE" in rules
    assert "FOG" in rules


def test_priority_blend_weights_sum() -> None:
    s = get_settings()
    total = (
        s.rank_weight_ml_risk
        + s.rank_weight_criticality
        + s.rank_weight_urgency
        + s.rank_weight_impact
    )
    assert abs(total - 1.0) < 1e-6
    assert 0 <= clamp01(1.2) <= 1
