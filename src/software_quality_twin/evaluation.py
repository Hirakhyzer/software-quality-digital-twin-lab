from __future__ import annotations

from dataclasses import dataclass
from statistics import mean

from .schema import RiskLevel


_RISK_ORDER = {
    RiskLevel.LOW: 0,
    RiskLevel.MEDIUM: 1,
    RiskLevel.HIGH: 2,
}


@dataclass(frozen=True)
class LongitudinalMetrics:
    accuracy: float
    mean_ordinal_error: float
    undercall_rate: float
    early_warning_rate: float
    false_warning_rate: float


@dataclass(frozen=True)
class RobustnessMetrics:
    """Sensitivity of the twin to perturbed or imputed telemetry."""

    risk_flip_rate: float
    unsafe_flip_rate: float
    mean_score_deviation: float
    max_score_deviation: float


def ordinal_risk_error(predicted: RiskLevel, expected: RiskLevel) -> int:
    return abs(_RISK_ORDER[predicted] - _RISK_ORDER[expected])


def is_risk_undercall(predicted: RiskLevel, expected: RiskLevel) -> bool:
    return _RISK_ORDER[predicted] < _RISK_ORDER[expected]


def summarize_longitudinal(
    predicted: list[RiskLevel],
    expected: list[RiskLevel],
    early_warnings: list[bool] | None = None,
    expected_future_degradation: list[bool] | None = None,
) -> LongitudinalMetrics:
    if not predicted:
        raise ValueError("at least one prediction is required")
    if len(predicted) != len(expected):
        raise ValueError("predicted and expected risk labels must align")

    correct = sum(p == e for p, e in zip(predicted, expected))
    errors = [ordinal_risk_error(p, e) for p, e in zip(predicted, expected)]
    undercalls = sum(is_risk_undercall(p, e) for p, e in zip(predicted, expected))

    early_warning_rate = 0.0
    false_warning_rate = 0.0
    if early_warnings is not None or expected_future_degradation is not None:
        if early_warnings is None or expected_future_degradation is None:
            raise ValueError("warning predictions and future-degradation labels must both be provided")
        if len(early_warnings) != len(predicted) or len(expected_future_degradation) != len(predicted):
            raise ValueError("warning labels must align with risk predictions")

        positives = sum(expected_future_degradation)
        negatives = len(expected_future_degradation) - positives
        true_warnings = sum(
            warning and future
            for warning, future in zip(early_warnings, expected_future_degradation)
        )
        false_warnings = sum(
            warning and not future
            for warning, future in zip(early_warnings, expected_future_degradation)
        )
        early_warning_rate = true_warnings / positives if positives else 0.0
        false_warning_rate = false_warnings / negatives if negatives else 0.0

    return LongitudinalMetrics(
        accuracy=correct / len(predicted),
        mean_ordinal_error=mean(errors),
        undercall_rate=undercalls / len(predicted),
        early_warning_rate=early_warning_rate,
        false_warning_rate=false_warning_rate,
    )


def summarize_robustness(
    clean_risks: list[RiskLevel],
    perturbed_risks: list[RiskLevel],
    clean_scores: list[float],
    perturbed_scores: list[float],
) -> RobustnessMetrics:
    """Compare perturbed twin outputs with clean-telemetry outputs.

    A risk flip is any change in the categorical risk label. An unsafe flip is
    a perturbation that makes the perturbed assessment less conservative than
    the clean assessment. Score deviation measures how far the quality score
    moves under the perturbation.
    """
    if not clean_risks:
        raise ValueError("at least one clean result is required")
    if not (
        len(clean_risks)
        == len(perturbed_risks)
        == len(clean_scores)
        == len(perturbed_scores)
    ):
        raise ValueError("clean and perturbed outputs must align")

    risk_flips = sum(clean != perturbed for clean, perturbed in zip(clean_risks, perturbed_risks))
    unsafe_flips = sum(
        _RISK_ORDER[perturbed] < _RISK_ORDER[clean]
        for clean, perturbed in zip(clean_risks, perturbed_risks)
    )
    deviations = [
        abs(perturbed - clean)
        for clean, perturbed in zip(clean_scores, perturbed_scores)
    ]

    return RobustnessMetrics(
        risk_flip_rate=risk_flips / len(clean_risks),
        unsafe_flip_rate=unsafe_flips / len(clean_risks),
        mean_score_deviation=mean(deviations),
        max_score_deviation=max(deviations),
    )
