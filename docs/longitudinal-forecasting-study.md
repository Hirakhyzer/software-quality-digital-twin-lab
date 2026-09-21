# Longitudinal Forecasting Study

## Purpose

This study evaluates whether a software-quality digital twin gains measurable value from version history rather than merely reproducing current-version quality thresholds.

The central experimental distinction is between **state assessment** and **trajectory assessment**:

- state assessment asks whether the current release is low, medium, or high risk;
- trajectory assessment asks whether recent versions show a meaningful direction of change that should alter review behavior before an absolute threshold is crossed.

## Research Questions

### LQ1 — Incremental value of history

Does adding recent quality history improve release-risk assessment compared with a static threshold baseline that sees only the current version?

### LQ2 — Early warning

Can a degrading trajectory trigger useful review earlier than absolute quality thresholds?

### LQ3 — Error severity

Does the longitudinal twin reduce unsafe under-calls, especially `low` predictions when the ground-truth state is `high`?

### LQ4 — Recovery sensitivity

Can the twin distinguish genuine recovery from temporary noise after a degraded release?

### LQ5 — Window sensitivity

How does the trend-window length affect early-warning recall, false-warning rate, and stability?

## Implemented Trend Model

The current prototype computes recent quality-score deltas over a configurable rolling window.

For states `q1 ... qn`, version-to-version deltas are:

```text
di = q(i) - q(i-1)
```

The trend assessment records:

- mean version delta;
- cumulative score change within the window;
- number of consecutive declines ending at the current version;
- degrading trajectory flag;
- recovery flag.

A trajectory is currently considered degrading when at least one of the following holds:

```text
consecutive declines >= 2
cumulative window delta <= -8
mean version delta <= -4
```

These thresholds are transparent research parameters, not universal software-quality constants. They should be tuned only on a training/development split and then frozen before evaluation on held-out histories.

## History-Aware Release Forecast

The current quality state remains the primary release signal. Longitudinal trend is used as a conservative modifier.

A low-risk state with a sustained degrading trajectory is escalated from:

```text
approve -> review
```

This creates an explicit experimental mechanism for testing whether history can provide earlier warning than current-version thresholds alone.

The forecast also reports a simple one-step projected quality score:

```text
projected score = current quality score + mean recent delta
```

This projection is intentionally simple. It acts as a transparent baseline before more sophisticated time-series or probabilistic forecasting methods are introduced.

## Baseline

The repository includes a static threshold baseline using only current telemetry:

- coverage;
- complexity;
- failing tests;
- known defects;
- change size;
- test-change alignment.

The baseline has no access to previous versions. This makes the comparison scientifically useful: the study measures whether longitudinal context contributes information beyond a transparent current-state comparator.

## Primary Metrics

### Current-state metrics

- exact risk-classification accuracy;
- mean ordinal risk error;
- unsafe undercall rate.

### Early-warning metrics

- early-warning rate for versions preceding an increase in expected risk;
- false-warning rate when future ground-truth risk does not increase;
- warning lead time in number of versions.

### Stability metrics

- false drift alerts during stable healthy histories;
- trend-state changes under small telemetry perturbations;
- sensitivity to rolling-window length.

### Recovery metrics

- time to stop warning after remediation;
- rate of incorrectly persistent warnings after recovery;
- quality-score recovery magnitude.

## Experimental Families

The benchmark should grow into multiple independent trajectories rather than one long synthetic sequence.

Recommended families:

1. stable healthy evolution;
2. gradual coverage erosion;
3. complexity accumulation;
4. increasing defect burden;
5. test-change misalignment;
6. sudden regression;
7. gradual multi-signal degradation;
8. successful remediation and recovery;
9. partial recovery followed by relapse;
10. noisy but fundamentally stable telemetry;
11. missing telemetry;
12. large benign refactor with strong tests.

Each family should contain multiple trajectories with different magnitudes and timing so that the system cannot succeed by memorizing one threshold pattern.

## Experimental Protocol

For each trajectory:

1. define ground-truth risk labels before running the twin;
2. define whether each point is expected to precede degradation;
3. run the static current-version baseline;
4. run current-state twin estimation;
5. run longitudinal trend analysis;
6. run history-aware release forecasting;
7. record every state, trend, forecast, explanation, and warning;
8. compute current-state and early-warning metrics;
9. repeat with different trend windows;
10. repeat under controlled telemetry noise and missingness.

## Ablation Plan

Remove one information source at a time:

- version history;
- coverage;
- complexity;
- test failures;
- defect count;
- change size;
- test-change alignment.

The key history ablation is especially important:

```text
current-state twin
vs.
current-state twin + longitudinal trend
```

If the history-aware version does not improve early warning, reduce undercalls, or provide another measurable benefit, the project should report that result rather than assume that a digital-twin framing is beneficial.

## Statistical Analysis Plan

Once the benchmark contains enough independent trajectories:

- report confidence intervals for accuracy, undercall rate, and warning metrics;
- use paired comparisons because the same trajectory points are evaluated by each condition;
- report effect sizes alongside significance tests;
- perform per-family analysis to identify where longitudinal information helps or hurts;
- keep threshold tuning separate from final evaluation.

## Threats to Validity

The current prototype uses a hand-designed quality score and synthetic histories. This creates a risk of circular evaluation because the generated scenarios and state estimator may share the same assumptions.

Mitigation should include:

- independently constructed test trajectories;
- externally sourced software histories where licensing permits;
- frozen thresholds before final evaluation;
- sensitivity analysis over scoring weights;
- comparison against independently defined quality labels;
- reporting of negative and contradictory cases.

## Expected Research Value

The contribution is not that a rolling average exists. The research value lies in establishing a reproducible framework for testing **when longitudinal software-quality state provides information that static SQA misses**, how early that information becomes actionable, and what trade-off exists between earlier warning and unnecessary review burden.
