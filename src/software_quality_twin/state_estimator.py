from __future__ import annotations

from .schema import QualityState, QualityTelemetry, RiskLevel


def _clamp(value: float, low: float = 0.0, high: float = 100.0) -> float:
    return max(low, min(high, value))


def estimate_quality_state(telemetry: QualityTelemetry) -> QualityState:
    score = 100.0
    evidence: list[str] = []

    if telemetry.coverage < 80:
        penalty = min(25.0, (80 - telemetry.coverage) * 0.8)
        score -= penalty
        evidence.append(f"coverage below target ({telemetry.coverage:.1f}%)")

    if telemetry.complexity > 10:
        penalty = min(20.0, (telemetry.complexity - 10) * 1.5)
        score -= penalty
        evidence.append(f"elevated complexity ({telemetry.complexity:.1f})")

    if telemetry.failing_tests:
        score -= min(30.0, telemetry.failing_tests * 10.0)
        evidence.append(f"{telemetry.failing_tests} failing test(s)")

    if telemetry.defect_count:
        score -= min(20.0, telemetry.defect_count * 4.0)
        evidence.append(f"{telemetry.defect_count} known defect(s)")

    if telemetry.change_size > 500:
        score -= min(10.0, (telemetry.change_size - 500) / 100.0)
        evidence.append(f"large change size ({telemetry.change_size} LOC)")

    if telemetry.change_size > 0 and not telemetry.tests_changed:
        score -= 8.0
        evidence.append("production change without corresponding test change")

    score = _clamp(score)

    if score < 60:
        risk = RiskLevel.HIGH
    elif score < 80:
        risk = RiskLevel.MEDIUM
    else:
        risk = RiskLevel.LOW

    if not evidence:
        evidence.append("no elevated synthetic quality-risk signal observed")

    return QualityState(
        version=telemetry.version,
        quality_score=round(score, 2),
        risk=risk,
        evidence=tuple(evidence),
    )
