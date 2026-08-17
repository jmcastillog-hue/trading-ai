# Synchronized Microstructure Context V1

## Purpose

`SYNCHRONIZED_MICROSTRUCTURE_CONTEXT_V1` is the Level A producer that converts
an already-preserved public microstructure snapshot into a governed contextual
feature.

It performs **no market-data acquisition**.

Its source must already exist and must satisfy the published
`PUBLIC_READ_ONLY_MICROSTRUCTURE_SNAPSHOT_V1_1` validator.

The producer reuses the published V1.1 synchronization policy rather than
creating a second temporal-alignment interpretation.

## Source lineage

The producer depends on:

- `PUBLIC_READ_ONLY_MICROSTRUCTURE_SNAPSHOT_V1_1`
- `SYNCHRONIZED_COMPONENT_TIMESTAMP_ELIGIBILITY_V1`
- `CONTEXT_FEATURE_PACK_V1_LEVEL_A_STANDARD`

The source snapshot remains immutable.

The producer never calls the Binance endpoint itself.

## Frozen policy

The repository contains:

`src/context/resources/synchronized_microstructure_context_policy_v1.json`

The policy freezes:

- feature ID;
- source capability/provider/symbol/timeframe;
- depth limit `1000`;
- depth bands `5/10/25/50` bps;
- required bands `5/10` bps;
- optional bands `25/50` bps;
- exact reference-boundary equality for historical 15m components;
- preservation but non-use of misaligned historical components;
- point-in-time components as non-historical reconstruction;
- a research-policy effective floor.

The policy effective floor is:

`2026-08-17T00:00:00+00:00`

This is a research-governance boundary, not a market event.

## Why the policy floor exists

A deterministic transform can be computed later from a frozen old source.

Without a policy floor, an old snapshot could be retrospectively converted into
a feature and then falsely treated as if that feature had been preregistered at
the old observation time.

V1 therefore uses:

`available_at_utc = max(source_captured_finished_at_utc, policy_effective_from_utc)`

This means an old source captured before the policy existed remains auditable
but is point-in-time ineligible for the old observation.

For future sources captured after the policy floor, source completion is the
earliest feature availability because the transform is frozen and deterministic.

`produced_at_utc` remains separately recorded for audit and must be no earlier
than both policy effectiveness and source completion.

## Information cutoff

The feature includes point-in-time order-book/open-interest/funding information
observed during the snapshot capture.

Therefore:

`information_cutoff_utc = source_captured_finished_at_utc`

The observation descriptor must use exactly the same
`synchronized_context_available_at_utc`.

The source reference candle and reference boundary must also match exactly.

## Historical 15m components

The historical components are:

- `open_interest_history`
- `taker_buy_sell_volume`
- `global_long_short_account_ratio`

The published V1.1 synchronization policy requires exact provider timestamp
equality with the reference boundary.

If aligned, a small descriptive value payload is exposed.

If misaligned:

- the source provenance is preserved;
- the timestamp delta is preserved;
- `values = null`;
- the component is not usable for synchronized context.

No tolerance window is invented.

No provider-interval equivalence is inferred.

## Point-in-time components

The producer exposes descriptive fields for:

- current open interest;
- mark/index/funding;
- order-book best bid/ask/mid/spread.

These are explicitly marked as point-in-time context, not historical interval
reconstruction.

## Depth

Depth bands are inherited from the V1.1 snapshot:

- 5 bps
- 10 bps
- 25 bps
- 50 bps

Coverage remains explicit.

An incomplete band remains incomplete.

Observed imbalance can be preserved, but an incomplete band receives no usable
imbalance value.

No extrapolation is allowed.

## Interpretation limits

The feature does not claim that:

- visible bid depth predicts upside;
- visible ask depth predicts downside;
- open interest identifies long versus short direction;
- funding or account ratios are actionable;
- taker imbalance is a trading signal;
- the order book reveals hidden stops;
- the order book reveals liquidations.

The output is descriptive context only.

## No scoring

V1 assigns no:

- composite score;
- bullish/bearish direction;
- trade action;
- entry;
- stop;
- target;
- confidence score.

The later Context Evaluation Engine is responsible for determining whether any
feature has measurable out-of-sample value.

## Package authorization

Authorization:

`PREPARE_SYNCHRONIZED_MICROSTRUCTURE_CONTEXT_V1`

Inputs:

- external observation descriptor JSON;
- external pre-existing V1.1 microstructure snapshot directory;
- explicit `produced_at_utc`.

Output:

- `synchronized_microstructure_context_component.json`
- `producer_checks.json`
- `manifest.sha256`

The output is external, create-only and transactional.

## Safety

This producer performs no:

- market-data request;
- authenticated request;
- Git network request;
- source recapture;
- retry loop;
- scheduler;
- background process;
- signal generation;
- live alert;
- candidate modification;
- primary-rule modification;
- paper trading;
- real-capital action;
- exchange execution;
- official dataset write;
- official append-gate activation.

## Evaluation boundary

This feature is not evidence that any microstructure metric predicts BTC
returns.

It only creates preregistered, point-in-time-compatible research variables.

The future Context Evaluation Engine may evaluate them against separately
preserved forward outcomes.

No microstructure field may be promoted from one observation.
