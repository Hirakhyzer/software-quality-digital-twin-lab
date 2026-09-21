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
    twin.update(
        QualityTelemetry("1.0.0", 90.0, 8.0, 0, 0, 100, True)
    )
    twin.update(
        QualityTelemetry("1.1.0", 68.0, 17.0, 2, 3, 900, False)
    )

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
