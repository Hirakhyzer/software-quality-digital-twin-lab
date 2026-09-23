from software_quality_twin.evidence_assurance import (
    apply_telemetry_assurance,
    assess_telemetry_assurance,
)
from software_quality_twin.schema import ReleaseForecast, RiskLevel
from software_quality_twin.telemetry_quality import TelemetryQualityReport


def make_forecast() -> ReleaseForecast:
    return ReleaseForecast(
        version="2.0.0",
        risk=RiskLevel.LOW,
        confidence=0.80,
        recommendation="approve",
        explanation="Synthetic forecast.",
    )


def test_fresh_complete_telemetry_preserves_approval() -> None:
    report = TelemetryQualityReport(
        version="2.0.0",
        observed_fields=(
            "coverage",
            "complexity",
            "failing_tests",
            "defect_count",
            "change_size",
            "tests_changed",
        ),
        imputed_fields=(),
        completeness=1.0,
    )

    assurance = assess_telemetry_assurance(
        report,
        signal_age_hours={"coverage": 2.0, "complexity": 3.0},
    )
    adjusted = apply_telemetry_assurance(make_forecast(), assurance)

    assert assurance.requires_review is False
    assert assurance.confidence_multiplier == 1.0
    assert adjusted.recommendation == "approve"
    assert adjusted.confidence == 0.80


def test_imputed_signal_escalates_approval_and_reduces_confidence() -> None:
    report = TelemetryQualityReport(
        version="2.0.0",
        observed_fields=(
            "complexity",
            "failing_tests",
            "defect_count",
            "change_size",
            "tests_changed",
        ),
        imputed_fields=("coverage",),
        completeness=5 / 6,
    )

    assurance = assess_telemetry_assurance(report)
    adjusted = apply_telemetry_assurance(make_forecast(), assurance)

    assert assurance.requires_review is True
    assert assurance.confidence_multiplier < 1.0
    assert adjusted.recommendation == "review"
    assert adjusted.confidence < 0.80
    assert "insufficient for unattended approval" in adjusted.explanation


def test_stale_signal_forces_review_even_when_complete() -> None:
    report = TelemetryQualityReport(
        version="2.0.0",
        observed_fields=(
            "coverage",
            "complexity",
            "failing_tests",
            "defect_count",
            "change_size",
            "tests_changed",
        ),
        imputed_fields=(),
        completeness=1.0,
    )

    assurance = assess_telemetry_assurance(
        report,
        signal_age_hours={"coverage": 36.0, "complexity": 4.0},
        stale_after_hours=24.0,
    )
    adjusted = apply_telemetry_assurance(make_forecast(), assurance)

    assert assurance.stale_fields == ("coverage",)
    assert assurance.requires_review is True
    assert adjusted.recommendation == "review"


def test_invalid_assurance_parameters_are_rejected() -> None:
    report = TelemetryQualityReport(
        version="2.0.0",
        observed_fields=(),
        imputed_fields=("coverage",),
        completeness=0.0,
    )

    try:
        assess_telemetry_assurance(report, minimum_completeness=1.2)
    except ValueError as exc:
        assert "minimum_completeness" in str(exc)
    else:
        raise AssertionError("expected ValueError")
