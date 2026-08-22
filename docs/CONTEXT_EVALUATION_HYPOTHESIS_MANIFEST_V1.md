# Context Evaluation Hypothesis Manifest V1

## Status

This document records the initial prospective preregistration for
`CONTEXT_EVALUATION_ENGINE_V1`.

Canonical hypothesis manifest:

`research/context_evaluation/context_evaluation_hypothesis_manifest_v1.json`

Frozen at UTC:

`2026-08-22T16:15:00+00:00`

Canonical JSON SHA-256:

`4de33a61d2a1456e6bd673ddd044cd0c01bb3369d30595ec57773df1d922442b`

## Scientific boundary

The eight hypotheses below were selected before prospective evaluation.
No forward-outcome package, return, MFE/MAE, PnL, p-value, significance result,
feature ranking, or quality-gate result is read by the preparation workflow.

Every observation with a synchronized context cutoff before `frozen_at_utc`
must be excluded by the published evaluation engine.

No hypothesis has an expected sign. No threshold search, transform search,
model fit, ranking, or winner selection is authorized.

## Initial preregistered hypotheses

1. `H001_BTC_CYCLE_DAYS_H16`
   - feature: `BTC_CYCLE_HALVING_CONTEXT_V1`
   - predictor: `days_since_halving_reference`
   - type: continuous
   - horizon: 16 bars

2. `H002_EVENT_UPCOMING_6H_H16`
   - feature: `EVENT_RISK_CALENDAR_CONTEXT_V1`
   - predictor: `upcoming_event_counts.6h`
   - type: continuous
   - horizon: 16 bars

3. `H003_EXTERNAL_CYCLE_BASELINE_H16`
   - feature: `EXTERNAL_CYCLE_REGRESSION_BASELINE_V1`
   - predictor: `baseline_estimate`
   - type: continuous
   - horizon: 16 bars

4. `H004_LIQUIDITY_LOWER_SWEEP_RECLAIM_H4`
   - feature: `LIQUIDITY_SWEEP_PATTERN_CONTEXT_V1`
   - predictor: `lower_side_sweep_reclaim_same_bar`
   - type: binary
   - horizon: 4 bars

5. `H005_LIQUIDITY_UPPER_SWEEP_REJECTION_H4`
   - feature: `LIQUIDITY_SWEEP_PATTERN_CONTEXT_V1`
   - predictor: `upper_side_sweep_rejection_same_bar`
   - type: binary
   - horizon: 4 bars

6. `H006_EXTERNAL_THESIS_STATE_H16`
   - feature: `EXTERNAL_THESIS_MODEL_CARD_V1`
   - predictor: `state_code`
   - type: categorical
   - horizon: 16 bars

7. `H007_ANALOG_NEAREST_DISTANCE_H4`
   - feature: `ANALOG_ENGINE_CONTEXT_V1`
   - predictor: `nearest_distance`
   - type: continuous
   - horizon: 4 bars

8. `H008_MICRO_MARK_INDEX_BASIS_H2`
   - feature: `SYNCHRONIZED_MICROSTRUCTURE_CONTEXT_V1`
   - predictor:
     `point_in_time_components.mark_price_funding.mark_index_basis_bps`
   - type: continuous
   - horizon: 2 bars

All outcomes are `synchronized_context_outcome.forward_return`.
All transforms are `IDENTITY`.

## Why Onchain is not forced into V1

`ONCHAIN_CONTEXT_INTERFACE_V1` is intentionally provider-agnostic and stores
the actual on-chain metric records in a list. No provider-specific scalar
metric identity has yet been frozen for evaluation.

V1 therefore does not use a weak proxy such as `metric_count`. A future
hypothesis manifest may add one or more on-chain hypotheses only after a
provider adapter and exact metric identity are frozen prospectively.

That later manifest must have its own later `frozen_at_utc`; it cannot modify
or retroactively replace this V1 preregistration.

## Interpretation limits

The manifest defines what may be measured. It does not establish that any
hypothesis is predictive or profitable.

The published engine remains limited to descriptive association and must emit:

`DESCRIPTIVE_ONLY_NO_EDGE_CLAIM`
