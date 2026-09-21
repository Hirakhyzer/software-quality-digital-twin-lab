# Research Framework

## Conceptual Model

The project treats software quality as a time-varying latent state inferred from observable engineering telemetry.

```text
Versioned software change
        ↓
Quality telemetry
        ↓
State estimation
        ↓
Versioned digital twin state
        ↓
Drift detection + risk forecasting
        ↓
Evidence-linked human review
```

## Design Principles

1. **Longitudinal over static:** evaluate trajectories across versions, not only isolated snapshots.
2. **Evidence before score:** every quality state should remain traceable to observable telemetry.
3. **State and forecast are separate:** the twin estimates current quality before forecasting release risk.
4. **Drift is first-class:** relative degradation may matter even before a fixed threshold is crossed.
5. **Human accountability:** forecasts support review; they do not autonomously authorize production releases.
6. **Reproducibility:** telemetry, state, thresholds, forecasts, and outcomes must be versioned.

## Experimental Conditions

- static threshold baseline;
- current-version twin state only;
- longitudinal twin with drift features;
- longitudinal twin with explanation shown to reviewers.

## Independent Variables

- number of historical versions;
- telemetry families available;
- drift threshold;
- missing/noisy telemetry rate;
- defect and regression severity;
- change size and complexity;
- quality trajectory pattern.

## Dependent Variables

- risk classification accuracy;
- early-degradation detection rate;
- false alarm rate;
- drift detection lead time;
- forecast calibration;
- twin-state stability;
- reviewer verification accuracy;
- review time;
- explanation usefulness.

## Research Boundary

The digital twin is an experimental representation of software-quality evidence, not a claim that software quality can be fully reduced to a single score. Multiple metrics and qualitative review remain necessary.
