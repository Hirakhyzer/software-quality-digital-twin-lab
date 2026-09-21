from __future__ import annotations

from .schema import DriftAssessment, QualityState


def assess_drift(previous: QualityState, current: QualityState, threshold: float = 8.0) -> DriftAssessment:
    delta = round(current.quality_score - previous.quality_score, 2)
    degraded = delta <= -abs(threshold)
    if degraded:
        explanation = (
            f"Quality score decreased by {abs(delta):.2f} points from "
            f"{previous.version} to {current.version}, exceeding the drift threshold."
        )
    elif delta < 0:
        explanation = (
            f"Quality score decreased by {abs(delta):.2f} points, but the change "
            "did not exceed the configured drift threshold."
        )
    elif delta > 0:
        explanation = f"Quality score improved by {delta:.2f} points."
    else:
        explanation = "Quality score remained unchanged."

    return DriftAssessment(
        from_version=previous.version,
        to_version=current.version,
        score_delta=delta,
        degraded=degraded,
        explanation=explanation,
    )
