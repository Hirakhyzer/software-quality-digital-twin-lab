from __future__ import annotations

from statistics import mean

from .schema import QualityState, TrendAssessment


def assess_trend(states: list[QualityState] | tuple[QualityState, ...], window: int = 4) -> TrendAssessment:
    """Assess the recent direction of quality evolution.

    The trend intentionally operates on versioned twin states rather than raw
    telemetry. It is therefore usable with any future state estimator that
    preserves the QualityState interface.
    """
    if window < 2:
        raise ValueError("trend window must be at least 2")
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
    deltas = [
        round(current.quality_score - previous.quality_score, 2)
        for previous, current in zip(recent, recent[1:])
    ]
    mean_delta = round(mean(deltas), 2)
    cumulative_delta = round(recent[-1].quality_score - recent[0].quality_score, 2)

    consecutive_declines = 0
    for delta in reversed(deltas):
        if delta < 0:
            consecutive_declines += 1
        else:
            break

    degrading = (
        consecutive_declines >= 2
        or cumulative_delta <= -8.0
        or mean_delta <= -4.0
    )
    recovering = len(deltas) >= 2 and deltas[-1] > 0 and cumulative_delta < 0

    if degrading:
        explanation = (
            f"Recent quality trajectory is degrading: mean version delta={mean_delta:.2f}, "
            f"cumulative delta={cumulative_delta:.2f}, consecutive declines={consecutive_declines}."
        )
    elif recovering:
        explanation = (
            f"Quality shows recovery after earlier degradation: latest delta={deltas[-1]:.2f}, "
            f"window cumulative delta={cumulative_delta:.2f}."
        )
    elif mean_delta > 0:
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
