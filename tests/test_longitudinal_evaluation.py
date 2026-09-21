from software_quality_twin import RiskLevel
from software_quality_twin.evaluation import (
    is_risk_undercall,
    ordinal_risk_error,
    summarize_longitudinal,
)


def test_ordinal_risk_error_distinguishes_error_severity() -> None:
    assert ordinal_risk_error(RiskLevel.LOW, RiskLevel.HIGH) == 2
    assert ordinal_risk_error(RiskLevel.MEDIUM, RiskLevel.HIGH) == 1
    assert ordinal_risk_error(RiskLevel.HIGH, RiskLevel.HIGH) == 0


def test_undercall_flags_less_conservative_risk_predictions() -> None:
    assert is_risk_undercall(RiskLevel.LOW, RiskLevel.MEDIUM) is True
    assert is_risk_undercall(RiskLevel.MEDIUM, RiskLevel.HIGH) is True
    assert is_risk_undercall(RiskLevel.HIGH, RiskLevel.MEDIUM) is False


def test_summary_reports_accuracy_safety_and_warning_quality() -> None:
    predicted = [RiskLevel.LOW, RiskLevel.MEDIUM, RiskLevel.MEDIUM, RiskLevel.HIGH]
    expected = [RiskLevel.LOW, RiskLevel.MEDIUM, RiskLevel.HIGH, RiskLevel.HIGH]
    warnings = [False, True, True, False]
    future_degradation = [False, True, True, False]

    metrics = summarize_longitudinal(
        predicted,
        expected,
        early_warnings=warnings,
        expected_future_degradation=future_degradation,
    )

    assert metrics.accuracy == 0.75
    assert metrics.mean_ordinal_error == 0.25
    assert metrics.undercall_rate == 0.25
    assert metrics.early_warning_rate == 1.0
    assert metrics.false_warning_rate == 0.0
