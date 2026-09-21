from __future__ import annotations

from .schema import QualityState, ReleaseForecast, RiskLevel


def forecast_release(state: QualityState) -> ReleaseForecast:
    if state.risk == RiskLevel.HIGH:
        recommendation = "block"
        confidence = 0.92
    elif state.risk == RiskLevel.MEDIUM:
        recommendation = "review"
        confidence = 0.84
    else:
        recommendation = "approve"
        confidence = 0.78

    evidence_summary = "; ".join(state.evidence)
    explanation = (
        f"Version {state.version} has quality score {state.quality_score:.2f} "
        f"with {state.risk.value} risk. Evidence: {evidence_summary}."
    )

    return ReleaseForecast(
        version=state.version,
        risk=state.risk,
        confidence=confidence,
        recommendation=recommendation,
        explanation=explanation,
    )
