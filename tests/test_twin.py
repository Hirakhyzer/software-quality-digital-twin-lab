from software_quality_twin import QualityTelemetry, RiskLevel, SoftwareQualityDigitalTwin


def test_low_risk_state_can_be_approved() -> None:
    twin = SoftwareQualityDigitalTwin()
    state = twin.update(
        QualityTelemetry(
            version="1.0.0",
            coverage=92.0,
            complexity=8.0,
            failing_tests=0,
            defect_count=0,
            change_size=120,
            tests_changed=True,
        )
    )

    assert state.risk == RiskLevel.LOW
    assert twin.forecast().recommendation == "approve"


def test_quality_degradation_is_detected() -> None:
    twin = SoftwareQualityDigitalTwin()
    twin.update(QualityTelemetry("1.0.0", 90.0, 8.0, 0, 0, 100, True))
    twin.update(QualityTelemetry("1.1.0", 68.0, 17.0, 2, 3, 900, False))

    drift = twin.drift()
    assert drift is not None
    assert drift.degraded is True
    assert drift.score_delta < 0
    assert twin.forecast().risk == RiskLevel.HIGH


def test_twin_preserves_version_history() -> None:
    twin = SoftwareQualityDigitalTwin()
    twin.update(QualityTelemetry("1.0.0", 85.0, 8.0, 0, 0, 80, True))
    twin.update(QualityTelemetry("1.0.1", 87.0, 8.0, 0, 0, 70, True))

    assert [state.version for state in twin.history] == ["1.0.0", "1.0.1"]


def test_sustained_decline_creates_trend_warning_before_high_risk() -> None:
    twin = SoftwareQualityDigitalTwin()
    twin.update(QualityTelemetry("1.0.0", 92.0, 7.0, 0, 0, 100, True))
    twin.update(QualityTelemetry("1.1.0", 79.0, 8.0, 0, 1, 180, True))
    twin.update(QualityTelemetry("1.2.0", 78.0, 9.0, 0, 1, 220, True))

    trend = twin.trend()
    forecast = twin.forecast()

    assert twin.current_state is not None
    assert twin.current_state.risk == RiskLevel.LOW
    assert trend.degrading is True
    assert trend.consecutive_declines >= 2
    assert forecast.trend_risk is True
    assert forecast.recommendation == "review"
    assert forecast.projected_score is not None


def test_recovery_is_distinguished_from_continued_decline() -> None:
    twin = SoftwareQualityDigitalTwin()
    twin.update(QualityTelemetry("2.0.0", 92.0, 7.0, 0, 0, 100, True))
    twin.update(QualityTelemetry("2.1.0", 72.0, 14.0, 1, 2, 600, False))
    twin.update(QualityTelemetry("2.2.0", 84.0, 9.0, 0, 1, 180, True))

    trend = twin.trend()

    assert trend.recovering is True
    assert trend.consecutive_declines == 0
