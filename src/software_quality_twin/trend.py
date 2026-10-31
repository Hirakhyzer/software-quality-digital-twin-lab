from __future__ import annotations

from math import isfinite
from statistics import mean

from .schema import QualityState, RiskLevel, TrendAssessment


_RISK_ORDER = {
    RiskLevel.LOW: 0,
    RiskLevel.MEDIUM: 1,
    RiskLevel.HIGH: 2,
}


def assess_trend(
    states: list[QualityState] | tuple[QualityState, ...],
    window: int = 4,
) -> TrendAssessment:
    """Assess the recent direction of quality evolution.

    The trend intentionally operates on versioned twin states rather than raw
    telemetry. Classification uses full-precision score deltas; rounding is only
    used for reported metrics. Recovery includes both a rebound after an observed
    decline and sustained improvement from an already-degraded starting state
    when categorical risk also decreases.
    """
    if not isinstance(window, int) or isinstance(window, bool) or window < 2:
        raise ValueError("trend window must be an integer of at least 2")
    if len(states) < 2:
        return TrendAssessment(
            window_size=len(states),
            mean_delta=0.0,
            cumulative_delta=0.0,
            consecutive_declines=0,
            degrading=False,
            recovering=False,
            explanation="At least two quality states are required for trend analysis.",
        )

    recent = list(states[-window:])
    raw_deltas = [
        current.quality_score - previous.quality_score
        for previous, current in zip(recent, recent[1:])
    ]
    if not all(isfinite(delta) for delta in raw_deltas):
        raise ValueError("quality-score deltas must be finite")

    raw_mean_delta = mean(raw_deltas)
    raw_cumulative_delta = recent[-1].quality_score - recent[0].quality_score
    mean_delta = round(raw_mean_delta, 2)
    cumulative_delta = round(raw_cumulative_delta, 2)
    reported_deltas = [round(delta, 2) for delta in raw_deltas]

    consecutive_declines = 0
    for delta in reversed(raw_deltas):
        if delta < 0:
            consecutive_declines += 1
        else:
            break

    degrading = (
        consecutive_declines >= 2
        or raw_cumulative_delta <= -8.0
        or raw_mean_delta <= -4.0
    )

    latest_improving = raw_deltas[-1] > 0
    rebound_after_decline = latest_improving and any(delta < 0 for delta in raw_deltas[:-1])
    categorical_risk_improved = (
        _RISK_ORDER[recent[-1].risk] < _RISK_ORDER[recent[0].risk]
    )
    recovery_from_degraded_baseline = (
        latest_improving
        and categorical_risk_improved
        and raw_cumulative_delta > 0
    )
    recovering = rebound_after_decline or recovery_from_degraded_baseline

    if degrading and not recovering:
        explanation = (
            f"Recent quality trajectory is degrading: mean version delta={mean_delta:.2f}, "
            f"cumulative delta={cumulative_delta:.2f}, consecutive declines={consecutive_declines}."
        )
    elif recovering:
        explanation = (
            f"Quality shows recovery: latest delta={reported_deltas[-1]:.2f}, "
            f"window cumulative delta={cumulative_delta:.2f}, "
            f"risk moved from {recent[0].risk.value} to {recent[-1].risk.value}."
        )
    elif raw_mean_delta > 0:
        explanation = (
            f"Recent quality trajectory is improving with mean version delta={mean_delta:.2f}."
        )
    else:
        explanation = (
            f"Recent quality trajectory is stable with mean version delta={mean_delta:.2f}."
        )

    return TrendAssessment(
        window_size=len(recent),
        mean_delta=mean_delta,
        cumulative_delta=cumulative_delta,
        consecutive_declines=consecutive_declines,
        degrading=degrading,
        recovering=recovering,
        explanation=explanation,
    )
