# External Cycle Regression Baseline V1

## Purpose

`EXTERNAL_CYCLE_REGRESSION_BASELINE_V1` is a Level A `EXTERNAL_MODEL`
producer. It validates a frozen external BTC cycle-regression snapshot and
exposes the externally supplied baseline as descriptive research context.

The producer does not fit a regression, fetch an external model, read current
market price, or calculate a market residual.

## External snapshot

The required schema is:

`EXTERNAL_CYCLE_REGRESSION_BASELINE_SNAPSHOT_V1`

The snapshot must contain model identity/version, source reference, parameter
SHA-256, fit-sample start/end, information cutoff, model generation time,
snapshot creation time, exact reference time, USD-per-BTC baseline estimate,
and an optional externally supplied interval.

The source remains external and immutable.

## Point-in-time rules

The required order is:

`fit_sample_end_utc <= information_cutoff_utc <= model_generated_at_utc <= snapshot_created_at_utc`

The snapshot `reference_time_utc` must equal the observation
`reference_boundary_utc` exactly. No nearest-time lookup, interpolation, or
extrapolation is allowed.

Feature availability is:

`available_at_utc = max(snapshot_created_at_utc, policy_effective_from_utc)`

Information cutoff remains the external snapshot's own information cutoff.

The governance floor is:

`2026-08-19T00:40:00+00:00`

This prevents an older external model snapshot from being retrospectively
promoted as if this feature definition had existed at the older observation.

## Numerical semantics

The only supported unit is `USD_PER_BTC`.

`baseline_estimate` must be finite and positive.

If `interval_available=true`, both bounds must exist and satisfy:

`0 < lower_bound < baseline_estimate < upper_bound`

If the interval is unavailable, both bounds must be null.

No interval is invented by the producer.

## Deliberately absent comparison

V1 does not calculate overvaluation, undervaluation, residual, z-score,
bullish/bearish state, long/short recommendation, entry, stop, target, or
confidence.

Those questions belong to a later preregistered Context Evaluation Engine.

## Package

Authorization:

`PREPARE_EXTERNAL_CYCLE_REGRESSION_BASELINE_V1`

Inputs are an external observation descriptor, an external frozen model
snapshot, and explicit `produced_at_utc`.

Output is create-only and transactional:

- `external_cycle_regression_baseline_component.json`
- `producer_checks.json`
- `manifest.sha256`

## Safety

No web request, market-data request, Git network request, model fitting,
future-outcome lookup, signal generation, candidate modification, live alert,
paper trade, real-capital action, exchange execution, or official append is
performed.

## Evaluation boundary

An external regression is a benchmark hypothesis, not evidence of an edge.
Its usefulness must be evaluated prospectively across sufficient observations
and separately preserved forward outcomes.
