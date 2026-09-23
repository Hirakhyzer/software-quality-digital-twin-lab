from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Mapping

from .schema import ReleaseForecast
from .telemetry_quality import TelemetryQualityReport


@dataclass(frozen=True)
class TelemetryAssurance:
    """Quality assessment for the evidence used by a release forecast."""

    completeness: float
    stale_fields: tuple[str, ...]
    imputed_fields: tuple[str, ...]
    confidence_multiplier: float
    requires_review: bool
    explanation: str


def assess_telemetry_assurance(
    report: TelemetryQualityReport,
    *,
    signal_age_hours: Mapping[str, float] | None = None,
    stale_after_hours: float = 24.0,
    minimum_completeness: float = 0.85,
) -> TelemetryAssurance:
    """Assess whether telemetry is complete and fresh enough for assurance use.

    The policy is intentionally transparent. Missing values are visible through
    ``imputed_fields`` and freshness is supplied explicitly by the caller. The
    result can reduce forecast confidence and force human review without
    changing the underlying software-quality state.
    """
    if not 0.0 <= minimum_completeness <= 1.0:
        raise ValueError("minimum_completeness must be between 0 and 1")
    if stale_after_hours < 0:
        raise ValueError("stale_after_hours must be non-negative")

    ages = signal_age_hours or {}
    stale_fields = tuple(
        sorted(field for field, age in ages.items() if age > stale_after_hours)
    )

    incompleteness_penalty = 0.35 * (1.0 - report.completeness)
    imputation_penalty = 0.05 * len(report.imputed_fields)
    staleness_penalty = 0.08 * len(stale_fields)
    confidence_multiplier = max(
        0.50,
        min(1.0, 1.0 - incompleteness_penalty - imputation_penalty - staleness_penalty),
    )

    requires_review = (
        report.completeness < minimum_completeness
        or bool(report.imputed_fields)
        or bool(stale_fields)
    )

    reasons: list[str] = [f"telemetry completeness={report.completeness:.2f}"]
    if report.imputed_fields:
        reasons.append("imputed=" + ",".join(report.imputed_fields))
    if stale_fields:
        reasons.append("stale=" + ",".join(stale_fields))
    if not report.imputed_fields and not stale_fields:
        reasons.append("all required signals are directly observed and fresh")

    return TelemetryAssurance(
        completeness=report.completeness,
        stale_fields=stale_fields,
        imputed_fields=report.imputed_fields,
        confidence_multiplier=round(confidence_multiplier, 3),
        requires_review=requires_review,
        explanation="; ".join(reasons),
    )


def apply_telemetry_assurance(
    forecast: ReleaseForecast,
    assurance: TelemetryAssurance,
) -> ReleaseForecast:
    """Apply evidence-quality safeguards to an existing release forecast."""
    recommendation = forecast.recommendation
    if assurance.requires_review and recommendation == "approve":
        recommendation = "review"

    confidence = round(forecast.confidence * assurance.confidence_multiplier, 3)
    explanation = (
        f"{forecast.explanation} Telemetry assurance: {assurance.explanation}. "
        f"Adjusted confidence={confidence:.3f}."
    )
    if assurance.requires_review and forecast.recommendation == "approve":
        explanation += (
            " Recommendation escalated to review because evidence quality is "
            "insufficient for unattended approval."
        )

    return replace(
        forecast,
        confidence=confidence,
        recommendation=recommendation,
        explanation=explanation,
    )
