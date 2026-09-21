from __future__ import annotations

import json
from pathlib import Path

from software_quality_twin import QualityTelemetry, RiskLevel, SoftwareQualityDigitalTwin
from software_quality_twin.baselines import static_threshold_risk
from software_quality_twin.evaluation import summarize_longitudinal


ROOT = Path(__file__).resolve().parents[1]
_RISK_ORDER = {RiskLevel.LOW: 0, RiskLevel.MEDIUM: 1, RiskLevel.HIGH: 2}


def load_history() -> list[dict]:
    return json.loads((ROOT / "data" / "quality_history.json").read_text(encoding="utf-8"))


def to_telemetry(raw: dict) -> QualityTelemetry:
    return QualityTelemetry(
        version=raw["version"],
        coverage=raw["coverage"],
        complexity=raw["complexity"],
        failing_tests=raw["failing_tests"],
        defect_count=raw["defect_count"],
        change_size=raw["change_size"],
        tests_changed=raw["tests_changed"],
    )


def main() -> None:
    history = load_history()
    twin = SoftwareQualityDigitalTwin()

    expected_labels: list[RiskLevel] = []
    twin_labels: list[RiskLevel] = []
    static_labels: list[RiskLevel] = []
    early_warnings: list[bool] = []
    future_degradation: list[bool] = []
    rows = []

    expected_sequence = [RiskLevel(raw["expected_risk"]) for raw in history]

    for index, raw in enumerate(history):
        telemetry = to_telemetry(raw)
        state = twin.update(telemetry)
        forecast = twin.forecast()
        drift = twin.drift()
        trend = twin.trend()
        expected = expected_sequence[index]
        static_risk = static_threshold_risk(telemetry)

        will_degrade = False
        if index + 1 < len(expected_sequence):
            will_degrade = _RISK_ORDER[expected_sequence[index + 1]] > _RISK_ORDER[expected]

        expected_labels.append(expected)
        twin_labels.append(state.risk)
        static_labels.append(static_risk)
        early_warnings.append(forecast.trend_risk)
        future_degradation.append(will_degrade)

        rows.append(
            (
                raw["version"],
                expected.value,
                static_risk.value,
                state.risk.value,
                state.quality_score,
                forecast.recommendation,
                forecast.trend_risk,
                trend.mean_delta,
                drift,
            )
        )

    twin_metrics = summarize_longitudinal(
        twin_labels,
        expected_labels,
        early_warnings=early_warnings,
        expected_future_degradation=future_degradation,
    )
    static_metrics = summarize_longitudinal(static_labels, expected_labels)

    print(
        "version\texpected\tstatic\ttwin\tscore\trecommendation\t"
        "trend_warning\tmean_trend_delta\tdrift"
    )
    for (
        version,
        expected,
        static,
        twin_risk,
        score,
        recommendation,
        warning,
        mean_trend_delta,
        drift,
    ) in rows:
        drift_text = "n/a" if drift is None else f"{drift.score_delta:.2f}"
        print(
            f"{version}\t{expected}\t{static}\t{twin_risk}\t{score:.2f}\t"
            f"{recommendation}\t{warning}\t{mean_trend_delta:.2f}\t{drift_text}"
        )

    print("\nStatic baseline")
    print(f"Accuracy:            {static_metrics.accuracy:.1%}")
    print(f"Mean ordinal error:  {static_metrics.mean_ordinal_error:.3f}")
    print(f"Undercall rate:      {static_metrics.undercall_rate:.1%}")

    print("\nLongitudinal twin")
    print(f"Accuracy:            {twin_metrics.accuracy:.1%}")
    print(f"Mean ordinal error:  {twin_metrics.mean_ordinal_error:.3f}")
    print(f"Undercall rate:      {twin_metrics.undercall_rate:.1%}")
    print(f"Early-warning rate:  {twin_metrics.early_warning_rate:.1%}")
    print(f"False-warning rate:  {twin_metrics.false_warning_rate:.1%}")


if __name__ == "__main__":
    main()
