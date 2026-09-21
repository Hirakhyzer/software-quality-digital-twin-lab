from __future__ import annotations

from .schema import QualityState, ReleaseForecast, RiskLevel, TrendAssessment


def _clamp(value: float, low: float = 0.0, high: float = 100.0) -> float:
    return max(low, min(high, value))


def forecast_release(
    state: QualityState,
    trend: TrendAssessment | None = None,
) -> ReleaseForecast:
    """Forecast release readiness from current state plus longitudinal trend.

    The current quality state remains the primary signal. A sustained degrading
    trend can make the recommendation more conservative before an absolute risk
    threshold is crossed, which allows the longitudinal model to be tested
    against static quality gates.
    """
    trend_risk = bool(trend and trend.degrading)
    projected_score = None
    if trend and trend.window_size >= 2:
        projected_score = round(_clamp(state.quality_score + trend.mean_delta), 2)

    if state.risk == RiskLevel.HIGH:
        recommendation = "block"
        confidence = 0.92
    elif state.risk == RiskLevel.MEDIUM:
        recommendation = "review"
        confidence = 0.84
    else:
        recommendation = "approve"
        confidence = 0.78

    if trend_risk and state.risk == RiskLevel.LOW:
        recommendation = "review"
        confidence = 0.82
    elif trend_risk and state.risk == RiskLevel.MEDIUM:
        confidence = 0.88

    evidence_summary = "; ".join(state.evidence)
    explanation_parts = [
        f"Version {state.version} has quality score {state.quality_score:.2f} with {state.risk.value} risk.",
        f"Evidence: {evidence_summary}.",
    ]
    if trend is not None:
        explanation_parts.append(trend.explanation)
    if projected_score is not None:
        explanation_parts.append(
            f"One-step trend projection estimates quality score {projected_score:.2f}."
        )
    if trend_risk and state.risk == RiskLevel.LOW:
        explanation_parts.append(
            "Recommendation escalated to review because sustained degradation is visible before the static risk threshold is crossed."
        )

    return ReleaseForecast(
        version=state.version,
        risk=state.risk,
        confidence=confidence,
        recommendation=recommendation,
        explanation=" ".join(explanation_parts),
        trend_risk=trend_risk,
        projected_score=projected_score,
    )
