# Multi-Trajectory Benchmark Protocol

## Purpose

A longitudinal software-quality model should not be evaluated on a single monotonic degradation history. Different quality trajectories can stress different behaviors: stability, gradual erosion, abrupt regression, recovery, and test-change misalignment.

This protocol defines a small but explicit multi-trajectory benchmark so those behaviors can be evaluated separately rather than pooled into one synthetic sequence.

## Current Trajectory Families

The benchmark dataset currently includes:

- **stable-healthy** — benign variation without an intended degradation trend;
- **gradual-erosion** — coverage and complexity degrade over multiple versions before stronger failure signals appear;
- **sudden-regression** — a sharp quality collapse after stable releases;
- **recovery** — a degraded system improves after corrective engineering work;
- **test-misalignment** — large changes accumulate while tests are not updated.

Each trajectory contains versioned telemetry and an expected categorical risk label. These labels are part of a controlled synthetic benchmark and are not presented as universal definitions of software quality.

## Why Multiple Trajectories Matter

A model that performs well on gradual degradation may still fail on abrupt regressions. A model that is highly sensitive to trend may create false warnings on benign variation. A model that detects decline but cannot recognize recovery may impose unnecessary review burden after corrective action.

For that reason, results should be reported per trajectory family before any aggregate summary is considered.

## Experimental Conditions

For every trajectory, the benchmark compares:

1. a static current-version threshold baseline;
2. the current quality-state classification produced by the digital twin;
3. the twin's history-aware warning and release recommendation;
4. recovery detection where applicable.

The default trend window is four versions and can be changed from the command line.

## Metrics

The suite reports, per trajectory:

- static baseline accuracy;
- twin current-state accuracy;
- mean ordinal risk error;
- unsafe undercall rate;
- early-warning rate;
- false-warning rate;
- whether a recovery signal was observed.

Accuracy should not be interpreted alone. An aggressive warning policy can improve early-warning sensitivity while increasing false-warning burden.

## Reproducibility

Run the suite with:

```bash
python benchmarks/run_trajectory_suite.py
```

Write a machine-readable artifact with:

```bash
python benchmarks/run_trajectory_suite.py \
  --trend-window 4 \
  --output results/trajectory-suite.json
```

The output records the benchmark version, trend-window configuration, trajectory-level metrics, and per-version predictions.

## Interpretation Rules

1. Do not claim longitudinal benefit from one trajectory family alone.
2. Report gradual and sudden degradation separately.
3. Treat false warnings on stable trajectories as a first-class cost.
4. Report recovery responsiveness explicitly rather than only degradation detection.
5. Preserve trajectories where the static baseline performs as well as or better than the twin.
6. Treat expected labels as controlled benchmark annotations, not ground truth for real software projects.
7. Do not generalize synthetic results to industrial repositories without external validation.

## Threats to Validity

The current suite is small and hand-constructed. Telemetry fields and labels were designed to exercise known mechanisms in the current implementation, which creates a risk of benchmark-model co-design bias.

The next validation stage should therefore include independently sourced longitudinal histories from open-source projects, externally defined defect/release outcomes, and pre-specified evaluation thresholds.

## Next Extensions

- add longer trajectories with 10-20 releases;
- add oscillating/noisy but non-degrading histories;
- add missing and delayed telemetry inside each trajectory family;
- add independently defined release-failure outcomes;
- add lead-time metrics measured in versions;
- add per-family confidence intervals across generated or real trajectories;
- freeze a benchmark release before comparative model experiments.

## Research Value

This benchmark moves the project away from demonstrating one convenient degradation path and toward testing whether longitudinal reasoning behaves appropriately across qualitatively different software-quality dynamics.
