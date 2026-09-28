from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path

from software_quality_twin import QualityTelemetry, RiskLevel, SoftwareQualityDigitalTwin
from software_quality_twin.baselines import static_threshold_risk
from software_quality_twin.evaluation import summarize_longitudinal


ROOT = Path(__file__).resolve().parents[1]
RISK_ORDER = {RiskLevel.LOW: 0, RiskLevel.MEDIUM: 1, RiskLevel.HIGH: 2}


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


def evaluate_trajectory(trajectory: dict, *, trend_window: int = 4) -> dict:
    versions = trajectory["versions"]
    twin = SoftwareQualityDigitalTwin()

    expected = [RiskLevel(v["expected_risk"]) for v in versions]
    static_labels: list[RiskLevel] = []
    twin_labels: list[RiskLevel] = []
    early_warnings: list[bool] = []
    future_degradation: list[bool] = []
    recovery_flags: list[bool] = []
    rows: list[dict] = []

    for index, raw in enumerate(versions):
        telemetry = to_telemetry(raw)
        state = twin.update(telemetry)
        trend = twin.trend(window=trend_window)
        forecast = twin.forecast(window=trend_window)
        static_risk = static_threshold_risk(telemetry)

        will_degrade = index + 1 < len(expected) and RISK_ORDER[expected[index + 1]] > RISK_ORDER[expected[index]]

        static_labels.append(static_risk)
        twin_labels.append(state.risk)
        early_warnings.append(forecast.trend_risk)
        future_degradation.append(will_degrade)
        recovery_flags.append(trend.recovering)
        rows.append(
            {
                "version": raw["version"],
                "expected_risk": expected[index].value,
                "static_risk": static_risk.value,
                "twin_risk": state.risk.value,
                "quality_score": state.quality_score,
                "recommendation": forecast.recommendation,
                "trend_warning": forecast.trend_risk,
                "recovering": trend.recovering,
                "mean_delta": trend.mean_delta,
                "projected_score": forecast.projected_score,
            }
        )

    static_metrics = summarize_longitudinal(static_labels, expected)
    twin_metrics = summarize_longitudinal(
        twin_labels,
        expected,
        early_warnings=early_warnings,
        expected_future_degradation=future_degradation,
    )

    return {
        "trajectory_id": trajectory["trajectory_id"],
        "description": trajectory["description"],
        "versions": len(versions),
        "static_metrics": asdict(static_metrics),
        "twin_metrics": asdict(twin_metrics),
        "recovery_detected": any(recovery_flags),
        "rows": rows,
    }


def load_suite(path: Path) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list) or not data:
        raise ValueError("trajectory suite must be a non-empty JSON list")
    return data


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the multi-trajectory software-quality benchmark suite")
    parser.add_argument("--dataset", type=Path, default=ROOT / "data" / "trajectory_suite.json")
    parser.add_argument("--trend-window", type=int, default=4)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    suite = load_suite(args.dataset)
    results = [evaluate_trajectory(t, trend_window=args.trend_window) for t in suite]

    payload = {
        "benchmark": "software-quality-trajectory-suite",
        "benchmark_version": "0.1.0",
        "trend_window": args.trend_window,
        "trajectory_count": len(results),
        "results": results,
    }

    print("trajectory\tstatic_acc\ttwin_acc\tundercall\tearly_warning\tfalse_warning\trecovery")
    for result in results:
        sm = result["static_metrics"]
        tm = result["twin_metrics"]
        print(
            f"{result['trajectory_id']}\t{sm['accuracy']:.3f}\t{tm['accuracy']:.3f}\t"
            f"{tm['undercall_rate']:.3f}\t{tm['early_warning_rate']:.3f}\t"
            f"{tm['false_warning_rate']:.3f}\t{result['recovery_detected']}"
        )

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
