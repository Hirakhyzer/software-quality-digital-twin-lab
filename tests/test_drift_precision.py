import pytest

from software_quality_twin.drift import assess_drift
from software_quality_twin.schema import QualityState, RiskLevel


def _state(version: str, score: float) -> QualityState:
    return QualityState(version=version, quality_score=score, risk=RiskLevel.LOW)


def test_display_rounding_does_not_trigger_false_drift_threshold_crossing() -> None:
    assessment = assess_drift(
        _state("1.0.0", 90.0),
        _state("1.1.0", 82.004),
        threshold=8.0,
    )

    # The raw decrease is 7.996 points. It displays as -8.00, but must not be
    # classified as an 8-point threshold crossing.
    assert assessment.score_delta == pytest.approx(-8.0)
    assert assessment.degraded is False
    assert "did not reach" in assessment.explanation


def test_exact_threshold_crossing_is_degraded() -> None:
    assessment = assess_drift(
        _state("1.0.0", 90.0),
        _state("1.1.0", 82.0),
        threshold=8.0,
    )
    assert assessment.degraded is True


def test_drift_threshold_must_be_finite_and_nonnegative() -> None:
    with pytest.raises(ValueError, match="finite and non-negative"):
        assess_drift(_state("a", 90.0), _state("b", 80.0), threshold=float("nan"))

    with pytest.raises(ValueError, match="finite and non-negative"):
        assess_drift(_state("a", 90.0), _state("b", 80.0), threshold=-8.0)
