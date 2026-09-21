from __future__ import annotations

from .schema import QualityTelemetry, RiskLevel


def static_threshold_risk(telemetry: QualityTelemetry) -> RiskLevel:
    """Conventional current-version comparator with no version history.

    The baseline intentionally uses transparent absolute thresholds so the
    longitudinal twin can be evaluated for incremental value rather than
    compared only with a weaker arbitrary model.
    """
    high_signals = 0
    medium_signals = 0

    if telemetry.coverage < 70:
        high_signals += 1
    elif telemetry.coverage < 80:
        medium_signals += 1

    if telemetry.complexity >= 18:
        high_signals += 1
    elif telemetry.complexity > 10:
        medium_signals += 1

    if telemetry.failing_tests >= 2:
        high_signals += 1
    elif telemetry.failing_tests == 1:
        medium_signals += 1

    if telemetry.defect_count >= 3:
        high_signals += 1
    elif telemetry.defect_count > 0:
        medium_signals += 1

    if telemetry.change_size >= 1000:
        high_signals += 1
    elif telemetry.change_size > 500:
        medium_signals += 1

    if telemetry.change_size > 0 and not telemetry.tests_changed:
        medium_signals += 1

    if high_signals >= 1 or medium_signals >= 3:
        return RiskLevel.HIGH
    if medium_signals >= 1:
        return RiskLevel.MEDIUM
    return RiskLevel.LOW
