<h1 align="center">Software Quality Digital Twin Lab</h1>

<p align="center"><b>A research framework for modeling, forecasting, and explaining software-quality evolution with digital twins.</b></p>

## Overview

Software Quality Digital Twin Lab explores whether a continuously updated digital representation of software quality can help detect degradation, forecast release risk, and support evidence-based quality assurance before failures become visible in production.

The project treats a software-quality digital twin as a **versioned quality-state model** built from observable engineering evidence such as code change, test coverage, complexity, defect signals, CI outcomes, and release history. The current research focus is not only present-state classification, but whether **longitudinal context provides earlier and safer quality warnings than static current-version checks**.

## Core Research Question

> **Can a software-quality digital twin detect meaningful quality degradation and forecast release risk early enough to improve continuous software assurance while remaining explainable and empirically reproducible?**

## Research Goals

- model software-quality state over time;
- fuse heterogeneous quality telemetry into an auditable twin state;
- detect quality drift between software versions;
- identify sustained degradation before absolute thresholds are crossed;
- forecast release-readiness risk using current state and recent trajectory;
- distinguish degradation, stability, and recovery;
- explain which evidence and trend features drove each forecast;
- compare longitudinal reasoning against credible static baselines;
- evaluate unsafe under-calls, false warnings, and early-warning behavior;
- support reproducible longitudinal SQA experiments.

## Digital Twin Concept

```text
Software version
     ↓
Quality telemetry
     ↓
State estimator
     ↓
Versioned Quality Twin
     ↓
┌───────────────────────────────┐
│ Current-state risk            │
│ Version-to-version drift      │
│ Rolling quality trend         │
│ Recovery / degradation state  │
└───────────────────────────────┘
     ↓
History-aware release forecast
     ↓
Explainable review recommendation
     ↓
Human quality review
```

## Current Quality Signals

The initial prototype represents:

- test coverage;
- change complexity;
- failing tests;
- defect count;
- change size;
- test-change alignment.

These signals are intentionally transparent so the contribution of longitudinal history can be measured before introducing larger statistical or machine-learning models.

## Longitudinal Intelligence

The twin now preserves version history and computes a rolling trajectory assessment from recent quality states.

For every trend window it records:

- mean version-to-version quality delta;
- cumulative quality-score change;
- consecutive decline count;
- degradation status;
- recovery status.

A sustained decline can escalate an otherwise low-risk current state from `approve` to `review`. This is deliberate: it creates a testable mechanism for evaluating whether a quality twin can surface degradation **before** static thresholds classify the current version as risky.

The release forecast also produces a transparent one-step quality-score projection based on the recent mean trend. This is a baseline forecasting mechanism, not a claim that software quality follows a simple linear process.

## Research Contributions

| Contribution | Purpose |
|---|---|
| Quality-state model | Represent the software system as a versioned quality twin. |
| Telemetry fusion | Combine heterogeneous SQA evidence into one auditable state. |
| Quality drift detection | Identify meaningful change between consecutive versions. |
| Trend analysis | Measure cumulative degradation, repeated decline, and recovery across version windows. |
| History-aware release forecasting | Test whether longitudinal context provides earlier warning than current-state thresholds alone. |
| Safety-oriented metrics | Measure ordinal error and unsafe risk under-calls, not only raw accuracy. |
| Early-warning metrics | Measure warning sensitivity and false-warning burden before future risk increases. |
| Static baseline comparison | Compare the twin against a transparent current-version SQA comparator. |
| Longitudinal benchmark | Evaluate quality evolution rather than isolated static snapshots. |
| Explainability | Preserve the evidence and trajectory responsible for each forecast. |

## Experimental Comparison

The project is designed around four conditions:

| Condition | Information available |
|---|---|
| Static threshold SQA | Current telemetry only |
| Current-state twin | Current telemetry transformed into a versioned quality state |
| Longitudinal twin | Current state + recent history + trend |
| Longitudinal twin + explanation | Same forecast with evidence and trajectory rationale exposed to reviewers |

The project should only claim benefit from longitudinal modeling when experiments show measurable incremental value over the simpler conditions.

## Evaluation Metrics

Implemented evaluation currently includes:

- exact risk-classification accuracy;
- mean ordinal risk error;
- unsafe undercall rate;
- early-warning rate;
- false-warning rate.

The broader evaluation plan also covers drift lead time, recovery responsiveness, calibration, robustness to missing/noisy telemetry, fidelity, reviewer verification accuracy, and review workload.

## Quick Start

```bash
git clone https://github.com/Hirakhyzer/software-quality-digital-twin-lab.git
cd software-quality-digital-twin-lab
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
python -m pip install -e ".[dev]"
python examples/run_demo.py
pytest
python benchmarks/run_longitudinal_benchmark.py
```

The benchmark prints current-version static risk, twin risk, quality score, release recommendation, trend warning, recent mean trend, and version-to-version drift, followed by comparative evaluation metrics.

## Repository Structure

```text
software-quality-digital-twin-lab/
├── README.md
├── benchmarks/
│   └── run_longitudinal_benchmark.py
├── data/
│   └── quality_history.json
├── docs/
│   ├── research-framework.md
│   ├── research-gap.md
│   ├── evaluation-methodology.md
│   └── longitudinal-forecasting-study.md
├── examples/
│   └── run_demo.py
├── src/software_quality_twin/
│   ├── __init__.py
│   ├── schema.py
│   ├── state_estimator.py
│   ├── drift.py
│   ├── trend.py
│   ├── forecasting.py
│   ├── baselines.py
│   ├── evaluation.py
│   └── twin.py
└── tests/
    ├── test_twin.py
    └── test_longitudinal_evaluation.py
```

## Research Boundary

This repository is a research prototype. It does not autonomously approve production releases or replace accountable software-quality professionals. Its purpose is to study measurable quality-state modeling, forecasting, drift, trajectory analysis, and human-interpretable evidence.

The current scoring rules and trend thresholds are experimental parameters. They are not universal definitions of software quality and must be validated, sensitivity-tested, and frozen before held-out evaluation.

## Reproducibility

Experiments should record:

- software version and trajectory identifier;
- input telemetry;
- twin state and quality score;
- drift and trend configuration;
- trend-window length;
- release forecast and confidence;
- explanation and warning state;
- baseline result;
- expected outcome;
- evaluation metrics;
- model or threshold version;
- random seed where applicable.

See [`docs/evaluation-methodology.md`](docs/evaluation-methodology.md) and [`docs/longitudinal-forecasting-study.md`](docs/longitudinal-forecasting-study.md) for the current research protocol.

## License

Released under the MIT License.

## Author

Created by **Hira Khyzer** as a software quality assurance and digital-twin research project.
