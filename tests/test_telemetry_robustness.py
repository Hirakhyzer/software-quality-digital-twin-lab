from software_quality_twin import QualityTelemetry, RiskLevel
from software_quality_twin.evaluation import summarize_robustness
from software_quality_twin.telemetry_quality import add_numeric_noise, materialize_telemetry


def test_missing_signal_is_imputed_from_previous_version() -> None:
    previous = QualityTelemetry(
        version="1.0.0",
        coverage=90.0,
        complexity=8.0,
        failing_tests=0,
        defect_count=1,
        change_size=120,
        tests_changed=True,
    )
    current = {
        "version": "1.1.0",
        "coverage": None,
        "complexity": 9.0,
        "failing_tests": 0,
        "defect_count": 1,
        "change_size": 180,
        "tests_changed": True,
    }

    telemetry, report = materialize_telemetry(current, previous=previous)

    assert telemetry.coverage == 90.0
    assert report.imputed_fields == ("coverage",)
    assert report.completeness == 5 / 6


def test_missing_signal_without_previous_observation_is_rejected() -> None:
    incomplete = {
        "version": "1.0.0",
        "coverage": None,
        "complexity": 8.0,
        "failing_tests": 0,
        "defect_count": 0,
        "change_size": 100,
        "tests_changed": True,
    }

    try:
        materialize_telemetry(incomplete)
    except ValueError as exc:
        assert "coverage" in str(exc)
    else:
        raise AssertionError("missing telemetry should not be silently invented")


def test_numeric_noise_is_bounded() -> None:
    telemetry = QualityTelemetry("1.0.0", 98.0, 8.0, 0, 0, 100, True)

    noisy = add_numeric_noise(
        telemetry,
        coverage_delta=10.0,
        complexity_delta=-20.0,
        failing_tests_delta=-2,
        defect_count_delta=-1,
        change_size_delta=-200,
    )

    assert noisy.coverage == 100.0
    assert noisy.complexity == 0.0
    assert noisy.failing_tests == 0
    assert noisy.defect_count == 0
    assert noisy.change_size == 0


def test_robustness_metrics_surface_unsafe_risk_flips() -> None:
    clean_risks = [RiskLevel.LOW, RiskLevel.MEDIUM, RiskLevel.HIGH]
    perturbed_risks = [RiskLevel.LOW, RiskLevel.LOW, RiskLevel.MEDIUM]
    clean_scores = [90.0, 70.0, 50.0]
    perturbed_scores = [91.0, 82.0, 61.0]

    metrics = summarize_robustness(
        clean_risks,
        perturbed_risks,
        clean_scores,
        perturbed_scores,
    )

    assert metrics.risk_flip_rate == 2 / 3
    assert metrics.unsafe_flip_rate == 2 / 3
    assert metrics.mean_score_deviation == 8.0
    assert metrics.max_score_deviation == 12.0
