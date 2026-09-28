import json
from pathlib import Path

from benchmarks.run_trajectory_suite import evaluate_trajectory, load_suite


ROOT = Path(__file__).resolve().parents[1]
DATASET = ROOT / "data" / "trajectory_suite.json"


def test_trajectory_suite_has_distinct_behavior_families():
    suite = load_suite(DATASET)
    ids = {item["trajectory_id"] for item in suite}
    assert {"stable-healthy", "gradual-erosion", "sudden-regression", "recovery", "test-misalignment"} <= ids
    assert all(len(item["versions"]) >= 4 for item in suite)


def test_each_version_has_required_quality_fields():
    required = {
        "version",
        "coverage",
        "complexity",
        "failing_tests",
        "defect_count",
        "change_size",
        "tests_changed",
        "expected_risk",
    }
    suite = json.loads(DATASET.read_text(encoding="utf-8"))
    for trajectory in suite:
        for version in trajectory["versions"]:
            assert required <= set(version)
            assert version["expected_risk"] in {"low", "medium", "high"}


def test_stable_trajectory_does_not_generate_recovery_signal():
    suite = load_suite(DATASET)
    stable = next(item for item in suite if item["trajectory_id"] == "stable-healthy")
    result = evaluate_trajectory(stable)
    assert result["recovery_detected"] is False
    assert result["versions"] == 4


def test_recovery_trajectory_exposes_recovery_signal():
    suite = load_suite(DATASET)
    recovery = next(item for item in suite if item["trajectory_id"] == "recovery")
    result = evaluate_trajectory(recovery)
    assert result["recovery_detected"] is True
    assert result["rows"][-1]["quality_score"] > result["rows"][0]["quality_score"]
