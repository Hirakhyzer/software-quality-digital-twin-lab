# Evidence-Quality Assurance Policy

## Purpose

Software-quality decisions are only as trustworthy as the engineering evidence behind them. A release forecast should not retain the same confidence when required telemetry is missing, imputed, or stale.

This document defines a transparent evidence-quality safeguard for the Software Quality Digital Twin Lab.

## Design Principle

The project now separates two questions:

1. **What does the current software-quality state indicate?**
2. **How trustworthy is the evidence used to support that state and forecast?**

The first question is handled by the state estimator, trend analysis, and release forecast. The second is handled by a separate telemetry-assurance layer.

This separation avoids silently changing the underlying quality state when evidence quality degrades. Instead, evidence problems reduce confidence and can escalate a release recommendation to human review.

## Assurance Inputs

The evidence-quality layer currently considers:

- telemetry completeness;
- fields that were imputed;
- explicit signal age supplied by the experiment or integration;
- a configurable freshness threshold;
- a configurable minimum completeness threshold.

The implementation is available in:

```text
src/software_quality_twin/evidence_assurance.py
```

## Confidence Adjustment

The safeguard computes a confidence multiplier from transparent penalties for:

- incomplete telemetry;
- imputed fields;
- stale fields.

The multiplier is bounded so that the policy cannot produce arbitrary negative confidence values.

The adjusted confidence is:

```text
adjusted confidence = forecast confidence × telemetry confidence multiplier
```

This formula is an experimental policy, not a universal calibration rule. Its coefficients should be sensitivity-tested and replaced or learned from empirical evidence when larger datasets become available.

## Review Escalation

A forecast that originally recommends `approve` is escalated to `review` when the telemetry-assurance policy identifies insufficient evidence quality.

Current escalation triggers include:

- completeness below the configured minimum;
- at least one imputed required field;
- at least one stale field.

The policy does **not** downgrade an existing `review` or `block` recommendation.

## Why This Matters for SQA

Traditional quality gates often treat telemetry values as if they were equally trustworthy. In practice, CI and engineering evidence can be delayed, partially unavailable, or carried forward from previous runs.

A quality-assurance system that ignores evidence quality can produce a dangerous failure mode: a superficially healthy release assessment supported by stale or incomplete data.

This project therefore treats evidence quality as a first-class assurance concern rather than only a data-cleaning problem.

## Research Questions

- **EA-RQ1:** How strongly should forecast confidence decrease as telemetry completeness falls?
- **EA-RQ2:** Which telemetry families should have stricter freshness requirements?
- **EA-RQ3:** Does explicit evidence-quality escalation reduce unsafe approvals without creating excessive review burden?
- **EA-RQ4:** Are imputed values more harmful in rapidly degrading trajectories than in stable trajectories?
- **EA-RQ5:** Can evidence-quality features improve calibration of release-risk confidence?

## Evaluation Plan

Future experiments should compare at least three policies:

1. no evidence-quality adjustment;
2. confidence reduction only;
3. confidence reduction plus review escalation.

Report:

- unsafe approval rate;
- review escalation rate;
- false escalation rate;
- confidence calibration;
- decision stability;
- per-signal sensitivity;
- reviewer workload.

## Threats to Validity

The current penalties and thresholds are hand-specified experimental parameters. They should not be interpreted as operationally validated values.

Signal age is also externally supplied rather than inferred from real CI timestamps. Before making empirical claims, the project should evaluate timestamped open-source build histories and freeze the policy before held-out testing.

## Reproducibility Requirements

Every experiment using this safeguard should record:

- completeness threshold;
- freshness threshold;
- field ages;
- imputed fields;
- confidence multiplier;
- original forecast;
- adjusted forecast;
- whether review escalation occurred.

## Research Value

This addition moves the project beyond predicting software quality alone. It evaluates whether a quality decision remains defensible when the **evidence itself has uncertainty, incompleteness, or staleness**.
