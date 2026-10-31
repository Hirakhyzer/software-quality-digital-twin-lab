from software_quality_twin.schema import QualityState, RiskLevel
from software_quality_twin.trend import assess_trend


def _state(version: str, score: float, risk: RiskLevel) -> QualityState:
    return QualityState(version=version, quality_score=score, risk=risk)


def test_rounding_does_not_create_false_degrading_trend() -> None:
    trend = assess_trend(
        [
            _state("1.0", 90.0, RiskLevel.LOW),
            _state("1.1", 86.002, RiskLevel.LOW),
            _state("1.2", 82.004, RiskLevel.LOW),
        ]
    )

    # Each raw decline is 3.998 points and the cumulative decline is 7.996.
    # They display as -4.00 and -8.00 respectively but must remain below the
    # configured degrading thresholds at full precision.
    assert trend.mean_delta == -4.0
    assert trend.cumulative_delta == -8.0
    assert trend.degrading is False


def test_improvement_from_degraded_baseline_is_recovery() -> None:
    trend = assess_trend(
        [
            _state("2.0", 55.0, RiskLevel.HIGH),
            _state("2.1", 64.0, RiskLevel.MEDIUM),
            _state("2.2", 76.0, RiskLevel.MEDIUM),
            _state("2.3", 88.0, RiskLevel.LOW),
        ]
    )

    assert trend.recovering is True
    assert trend.degrading is False
    assert "high to low" in trend.explanation
