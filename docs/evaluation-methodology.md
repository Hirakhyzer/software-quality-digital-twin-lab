# Evaluation Methodology

## Goal

Evaluate whether longitudinal software-quality digital twins provide useful information beyond static software-quality checks.

## Primary Comparisons

1. Static threshold-based SQA.
2. Twin state estimated from the current version only.
3. Longitudinal twin using version history and drift.
4. Longitudinal twin plus evidence-linked explanation for human review.

## Scenario Families

- gradual coverage erosion;
- complexity accumulation;
- defect growth;
- test-change misalignment;
- sudden regression;
- recovery after remediation;
- noisy telemetry;
- missing telemetry;
- stable healthy evolution.

## Metrics

### Quality-state performance

- risk classification accuracy;
- macro F1 across low/medium/high risk;
- ordinal risk error.

### Drift performance

- true-positive degradation detection;
- false-positive drift alerts;
- detection lead time;
- magnitude error for score change.

### Forecasting performance

- release recommendation accuracy;
- calibration when probabilistic forecasts are introduced;
- conservative versus unsafe forecast errors.

### Twin fidelity

- responsiveness to controlled quality changes;
- stability under unchanged quality conditions;
- robustness under missing or noisy telemetry;
- agreement with independently defined ground truth.

### Human-centered outcomes

- reviewer verification accuracy;
- time to decision;
- perceived explanation usefulness;
- appropriate reliance on the forecast.

## Ablation Studies

Remove one telemetry family at a time to measure its contribution:

- coverage;
- complexity;
- failing tests;
- defect counts;
- change size;
- test-change alignment;
- version-history features.

## Reporting

Every experiment should publish the dataset version, telemetry definition, quality-state formula/model, thresholds, drift configuration, baseline definition, raw predictions, and negative results.
