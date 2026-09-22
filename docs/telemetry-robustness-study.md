# Telemetry Robustness Study

## Purpose

A software-quality digital twin depends on engineering telemetry that can be incomplete, delayed, stale, or noisy. A twin that performs well only when every signal is perfect is not a credible continuous assurance mechanism.

This study evaluates how sensitive the twin is to telemetry quality problems and makes that sensitivity measurable rather than implicit.

## Research Questions

- **TRQ1:** Which telemetry families cause the largest change in quality-state estimates when missing?
- **TRQ2:** Which forms of telemetry noise are most likely to change categorical release risk?
- **TRQ3:** Can simple last-observation-carried-forward imputation preserve decision stability without creating unsafe underestimation of risk?
- **TRQ4:** How much score deviation can occur before a categorical risk label changes?
- **TRQ5:** Which telemetry signals require stricter freshness or completeness guarantees before the twin should be trusted for review support?

## Experimental Conditions

The current benchmark evaluates two perturbation families.

### Missing-signal experiments

One signal is removed from every version after the initial observation and replaced with the previous observed value. The experiment is repeated independently for:

- coverage;
- complexity;
- failing tests;
- defect count;
- change size;
- test-change alignment.

This is intentionally a simple imputation baseline. It is not assumed to be the best missing-data method.

### Deterministic noise experiments

The current benchmark includes controlled perturbations such as:

- coverage reduced by five percentage points;
- complexity increased by two points;
- defect count increased by one.

Future work should vary noise magnitudes symmetrically, sample from empirically justified error distributions, and distinguish sensor error from true software-quality change.

## Metrics

### Risk flip rate

The fraction of versions whose low/medium/high risk class changes relative to the clean-telemetry run.

### Unsafe flip rate

The fraction of versions where perturbed telemetry makes the twin less conservative than the clean run. For example, a clean `high` assessment that becomes `medium` under missing or noisy telemetry is counted as an unsafe flip.

### Mean score deviation

The average absolute difference between clean and perturbed quality scores.

### Maximum score deviation

The largest absolute score difference observed in the perturbation condition.

### Telemetry completeness

For missing-data experiments, completeness is the fraction of required signals directly observed rather than imputed.

## Imputation Policy

The research utility in `src/software_quality_twin/telemetry_quality.py` uses **last observation carried forward (LOCF)** when a previous version exists.

The implementation deliberately refuses to silently fabricate a missing first observation. If a required field is absent and no previous value exists, the experiment fails with an explicit error.

This design keeps imputation auditable and prevents hidden defaults from being mistaken for observed software evidence.

## Benchmark

Run:

```bash
python benchmarks/run_telemetry_robustness.py
```

The benchmark compares each perturbation with the clean twin output and reports:

```text
experiment
mean_completeness
risk_flip
unsafe_flip
mean_score_deviation
max_score_deviation
```

## Interpretation

Robustness should not be equated with invariance. A twin that never changes under degraded telemetry may simply be insensitive.

The desired behavior depends on the perturbation:

- harmless measurement noise should ideally produce small score changes and few risk flips;
- loss of a safety-critical signal should reduce confidence or trigger review rather than silently preserve an optimistic assessment;
- conservative perturbations may increase review burden without creating an unsafe undercall;
- imputation that lowers apparent risk is especially important to surface.

The current implementation measures output sensitivity first. A later extension should propagate telemetry completeness into forecast confidence and escalation policy.

## Threats to Validity

The present perturbations are synthetic and deterministic. They do not yet represent empirically measured CI telemetry error distributions.

LOCF can also be inappropriate when software quality changes rapidly, because stale values may conceal real degradation. Results should therefore be interpreted as sensitivity analysis, not evidence that LOCF is suitable for operational deployment.

The benchmark dataset is currently small. Robustness claims should be deferred until larger, independent longitudinal histories are evaluated.

## Next Extensions

1. Add telemetry freshness timestamps and explicit staleness measures.
2. Propagate completeness and freshness into forecast confidence.
3. Compare LOCF with conservative imputation and model-based imputation.
4. Add Monte Carlo perturbation experiments across multiple noise magnitudes.
5. Report per-signal sensitivity curves.
6. Evaluate interactions where multiple telemetry families are missing simultaneously.
7. Introduce real open-source CI histories with documented provenance.

## Research Value

This study strengthens the project by treating **input quality as part of software assurance quality**. The twin is not evaluated only on whether it produces the correct risk label; it is also evaluated on whether its conclusions remain trustworthy when the evidence pipeline is imperfect.
