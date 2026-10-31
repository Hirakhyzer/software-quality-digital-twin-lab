from __future__ import annotations

from math import isfinite

from .schema import DriftAssessment, QualityState


def assess_drift(
    previous: QualityState,
    current: QualityState,
    threshold: float = 8.0,
) -> DriftAssessment:
    """Assess release-to-release quality drift without threshold-rounding bias.

    Classification uses the full-precision score delta. Rounding is applied only
    to the reported ``score_delta`` and human-readable explanation so values that
    merely *display* as the threshold are not falsely classified as crossing it.
    """
    if not isfinite(threshold) or threshold < 0:
        raise ValueError("threshold must be finite and non-negative")

    raw_delta = current.quality_score - previous.quality_score
    if not isfinite(raw_delta):
        raise ValueError("quality-score delta must be finite")

    threshold_magnitude = abs(threshold)
    degraded = raw_delta <= -threshold_magnitude
    reported_delta = round(raw_delta, 2)

    if degraded:
        explanation = (
            f"Quality score decreased by {abs(reported_delta):.2f} points from "
            f"{previous.version} to {current.version}, meeting or exceeding "
            "the configured drift threshold."
        )
    elif raw_delta < 0:
        explanation = (
            f"Quality score decreased by {abs(reported_delta):.2f} points, but the change "
            "did not reach the configured drift threshold."
        )
    elif raw_delta > 0:
        explanation = f"Quality score improved by {reported_delta:.2f} points."
    else:
        explanation = "Quality score remained unchanged."

    return DriftAssessment(
        from_version=previous.version,
        to_version=current.version,
        score_delta=reported_delta,
        degraded=degraded,
        explanation=explanation,
    )
