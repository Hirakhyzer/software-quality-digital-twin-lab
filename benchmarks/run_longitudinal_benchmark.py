from __future__ import annotations

import json
from pathlib import Path

from software_quality_twin import QualityTelemetry, SoftwareQualityDigitalTwin


ROOT = Path(__file__).resolve().parents[1]


def load_history() -> list[dict]:
    return json.loads((ROOT / "data" / "quality_history.json").read_text(encoding="utf-8"))


def main() -> None:
    twin = SoftwareQualityDigitalTwin()
    correct = 0
    rows = []

    for raw in load_history():
        telemetry = QualityTelemetry(
            version=raw["version"],
            coverage=raw["coverage"],
            complexity=raw["complexity"],
            failing_tests=raw["failing_tests"],
            defect_count=raw["defect_count"],
            change_size=raw["change_size"],
            tests_changed=raw["tests_changed"],
        )
        state = twin.update(telemetry)
        forecast = twin.forecast()
        drift = twin.drift()
        expected = raw["expected_risk"]
        correct += int(state.risk.value == expected)
        rows.append((raw["version"], expected, state.risk.value, state.quality_score, forecast.recommendation, drift))

    print("version\texpected_risk\ttwin_risk\tquality_score\trecommendation\tdrift")
    for version, expected, risk, score, recommendation, drift in rows:
        drift_text = "n/a" if drift is None else f"{drift.score_delta:.2f}"
        print(f"{version}\t{expected}\t{risk}\t{score:.2f}\t{recommendation}\t{drift_text}")

    total = len(rows)
    print(f"\nRisk classification accuracy: {correct}/{total} ({correct / total:.1%})")


if __name__ == "__main__":
    main()
