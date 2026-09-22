from __future__ import annotations

import json
from pathlib import Path

from software_quality_twin import QualityTelemetry, SoftwareQualityDigitalTwin
from software_quality_twin.evaluation import summarize_robustness
from software_quality_twin.telemetry_quality import add_numeric_noise, materialize_telemetry


ROOT = Path(__file__).resolve().parents[1]


def load_history() -> list[dict]:
    return json.loads((ROOT / "data" / "quality_history.json").read_text(encoding="utf-8"))


def to_telemetry(raw: dict) -> QualityTelemetry:
    telemetry, _ = materialize_telemetry(raw)
    return telemetry


def evaluate_sequence(sequence: list[QualityTelemetry]) -> tuple[list, list[float]]:
    twin = SoftwareQualityDigitalTwin()
    risks = []
    scores = []
    for telemetry in sequence:
        state = twin.update(telemetry)
        risks.append(state.risk)
        scores.append(state.quality_score)
    return risks, scores


def missing_signal_sequence(history: list[dict], field: str) -> tuple[list[QualityTelemetry], float]:
    sequence: list[QualityTelemetry] = []
    completeness = []
    previous: QualityTelemetry | None = None

    for index, raw in enumerate(history):
        record = dict(raw)
        record.pop("expected_risk", None)
        if index > 0:
            record[field] = None
        telemetry, report = materialize_telemetry(record, previous=previous)
        sequence.append(telemetry)
        completeness.append(report.completeness)
        previous = telemetry

    return sequence, sum(completeness) / len(completeness)


def noisy_sequence(history: list[dict], profile: str) -> list[QualityTelemetry]:
    sequence = []
    for raw in history:
        telemetry = to_telemetry(raw)
        if profile == "coverage-minus-5":
            telemetry = add_numeric_noise(telemetry, coverage_delta=-5.0)
        elif profile == "complexity-plus-2":
            telemetry = add_numeric_noise(telemetry, complexity_delta=2.0)
        elif profile == "defect-plus-1":
            telemetry = add_numeric_noise(telemetry, defect_count_delta=1)
        else:
            raise ValueError(f"unknown noise profile: {profile}")
        sequence.append(telemetry)
    return sequence


def main() -> None:
    history = load_history()
    clean_sequence = [to_telemetry(raw) for raw in history]
    clean_risks, clean_scores = evaluate_sequence(clean_sequence)

    experiments: list[tuple[str, list[QualityTelemetry], float | None]] = []
    for field in (
        "coverage",
        "complexity",
        "failing_tests",
        "defect_count",
        "change_size",
        "tests_changed",
    ):
        sequence, completeness = missing_signal_sequence(history, field)
        experiments.append((f"missing-{field}-locf", sequence, completeness))

    for profile in ("coverage-minus-5", "complexity-plus-2", "defect-plus-1"):
        experiments.append((profile, noisy_sequence(history, profile), None))

    print("experiment\tmean_completeness\trisk_flip\tunsafe_flip\tmean_score_deviation\tmax_score_deviation")
    for name, sequence, completeness in experiments:
        risks, scores = evaluate_sequence(sequence)
        metrics = summarize_robustness(clean_risks, risks, clean_scores, scores)
        completeness_text = "n/a" if completeness is None else f"{completeness:.3f}"
        print(
            f"{name}\t{completeness_text}\t{metrics.risk_flip_rate:.3f}\t"
            f"{metrics.unsafe_flip_rate:.3f}\t{metrics.mean_score_deviation:.3f}\t"
            f"{metrics.max_score_deviation:.3f}"
        )


if __name__ == "__main__":
    main()
