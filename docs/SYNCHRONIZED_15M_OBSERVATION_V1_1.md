# Synchronized 15m Observation V1.1 — Component Timestamp Eligibility

## Purpose

`SYNCHRONIZED_15M_OBSERVATION_V1_1` is a narrow additive repair to the already closed and published `SYNCHRONIZED_15M_OBSERVATION_V1`.

The repair was triggered by the first real synchronized cycle. The cycle itself passed operationally:

- one Spot request;
- seven USDⓈ-M Futures public/read-only requests;
- exact Spot/Futures closed-candle match;
- no candidate;
- no official append;
- no execution;
- no repository mutation.

The real cycle also exposed one reproducible scientific defect: the microstructure snapshot reported `taker_buy_sell_volume.latest_15m.timestamp_utc` at `2026-08-10T23:15:00+00:00` while the synchronized reference boundary was `2026-08-10T23:45:00+00:00`.

V1 preserved that value inside an upstream `aligned_15m_components` claim. V1.1 repairs the downstream synchronized observation contract so that a historical component is not usable merely because the upstream snapshot grouped it under an aligned list.

V1 remains closed and unchanged.

## Repair attempt accounting

This is implementation/repair attempt `3/10` for Synchronized Observation:

- attempt 1: V1 implemented and sandbox validated successfully;
- real validation: operationally passed, then exposed the timestamp-eligibility defect;
- attempt 2: V1.1 logic passed all 32 unit tests, but the installer invoked the standalone validator by file path, so Python set `sys.path` to `src/workflows` and the validator could not import the repository package `src`; the installer failed closed and removed its newly created target files;
- attempt 3: the validator is invoked as repository module `python -m src.workflows.validate_synchronized_15m_observation_v1_1`, preserving repository-root import resolution. The V1.1 temporal-eligibility logic is otherwise unchanged.

No further repair is justified if the V1.1 gates pass.

## New authorization boundary

V1.1 has a new session-level authorization:

`RUN_BOUNDED_SYNCHRONIZED_15M_OBSERVATION_SESSION_V1_1`

The consumed V1 authorization is not accepted by the V1.1 public session entry point.

No real V1.1 session is required merely to validate this repair. The preserved real V1 observation supplies the regression shape that motivated the repair.

## Frozen request and candidate contracts

A successfully completed V1.1 cycle still has exactly:

- `1` public Binance Spot request;
- `7` public Binance USDⓈ-M Futures requests;
- `8` public market-data requests total.

The primary rule remains the frozen Spot rule:

`LONG_BASE_FAILED_BREAKDOWN_V1`

Microstructure remains context only and cannot:

- create a primary candidate;
- cancel a primary candidate;
- modify the frozen primary rule;
- generate an actionable signal;
- authorize alerts, paper trading, real capital, exchange execution or official append.

## Reference-time contract

The synchronized Spot/Futures candle gate is unchanged:

`spot_latest_closed_candle_utc == futures_reference_closed_candle_utc`

The Futures microstructure snapshot also exposes a `reference_boundary_utc`.

V1.1 requires:

`reference_boundary_utc == reference_closed_candle_utc + 1 millisecond`

For a candle closing at:

`2026-08-10T23:44:59.999000+00:00`

the reference boundary is therefore:

`2026-08-10T23:45:00+00:00`

## Historical component timestamp eligibility

The historical provider-timestamped components are:

1. `open_interest_history`;
2. `taker_buy_sell_volume`;
3. `global_long_short_account_ratio`.

Each component receives a deterministic eligibility record:

- `component_name`;
- `temporal_semantics`;
- `component_timestamp_utc`;
- `reference_boundary_utc`;
- `timestamp_delta_seconds`;
- `timestamp_equal_reference_boundary`;
- `historical_interval_equivalence_claimed`;
- `usable_for_synchronized_context`;
- `misalignment_reason`.

The eligibility rule is deliberately conservative:

`usable_for_synchronized_context = timestamp_equal_reference_boundary`

No tolerance window is introduced.

No undocumented provider interval meaning is inferred.

Even when timestamps are equal, V1.1 does **not** claim that the provider's timestamp proves complete equivalence to the full reference candle interval:

`historical_interval_equivalence_claimed = false`

This keeps the project point-in-time safe while avoiding a stronger semantic claim than the provider data supports.

## Real regression case frozen in tests

The first real synchronized V1 cycle produced:

- reference closed candle: `2026-08-10T23:44:59.999000+00:00`;
- reference boundary: `2026-08-10T23:45:00+00:00`;
- open-interest-history latest timestamp: `2026-08-10T23:45:00+00:00`;
- taker latest timestamp: `2026-08-10T23:15:00+00:00`;
- global long/short latest timestamp: `2026-08-10T23:45:00+00:00`.

V1.1 therefore deterministically derives:

- `open_interest_history` → usable;
- `taker_buy_sell_volume` → not usable;
- `global_long_short_account_ratio` → usable.

For the taker component:

- timestamp delta = `-1800` seconds;
- raw numeric values remain preserved for provenance;
- `latest_15m_usable_for_synchronized_context = false`;
- the value must not enter synchronized-context features for that observation.

## Upstream alignment claim handling

V1.1 does not modify the Microstructure V1.1 snapshot artifact.

Instead it preserves the upstream list as provenance:

`upstream_reported_aligned_15m_components`

and recomputes the synchronized-observation lists:

- `aligned_15m_components`;
- `misaligned_15m_components`.

It adds:

`alignment_recomputed_by_synchronized_observation_v1_1 = true`

This makes downstream consumers use the repaired eligibility contract without rewriting already closed Microstructure artifacts.

## Point-in-time components

The following remain point-in-time observations:

- `order_book`;
- `current_open_interest`;
- `mark_price_funding`.

They are explicitly marked:

- `temporal_semantics = POINT_IN_TIME_AFTER_REFERENCE`;
- `historical_alignment_claimed = false`;
- `historical_interval_equivalence_claimed = false`;
- `usable_for_historical_interval_alignment = false`.

V1.1 does not pretend that a point-in-time snapshot taken after the boundary reconstructs the preceding 15-minute interval.

Their precise use in prospective forward labeling must respect observation time and is a responsibility of the future Forward Outcome Labeler contract.

## Depth coverage semantics remain unchanged

Depth remains:

- request limit `1000`;
- frozen bands `5/10/25/50 bps`;
- required near-touch bands `5/10 bps`;
- optional bands `25/50 bps`.

For every band:

`usable_for_context = coverage_complete`

If coverage is incomplete:

- observed returned depth is preserved;
- observed imbalance is preserved;
- `notional_imbalance_usable = null`;
- missing depth is never extrapolated.

This repair does not change the depth contract that already passed real validation.

## Fail-closed behavior

V1.1 fails closed for:

- wrong V1.1 session authorization;
- wrong real-source attestation;
- official append gate enabled;
- output inside repository;
- stale or duplicate Spot candle;
- Spot capture contract violation;
- review-package provenance mismatch;
- Microstructure request/depth/permission contract violation;
- invalid reference boundary;
- Spot/Futures candle mismatch;
- official dataset or manifest mutation.

A historical component timestamp mismatch by itself does **not** abort the whole cycle. The value is retained and explicitly marked not usable for synchronized context.

## Official evidence and permissions

All of the following remain false:

- official dataset write;
- official append;
- signal generation;
- live alerts;
- paper trading;
- real capital;
- market/exchange execution;
- automation/execution.

The official dataset and manifest remain byte-identical.

## Validation strategy

V1.1 is validated without new market-data network access.

The test suite includes the exact temporal shape of the preserved real V1 observation as a regression control:

`reference 23:45 / taker 23:15 / OI 23:45 / global ratio 23:45`

The expected result is:

`misaligned_historical_components = ["taker_buy_sell_volume"]`

The repair is complete when:

- the sandbox unit tests pass;
- the static/mock validator passes;
- V1 remains unchanged;
- Microstructure V1.1 remains unchanged;
- official artifacts remain unchanged;
- no real market request is executed.

## Approved continuation

After V1.1 is sandbox validated, intentionally committed/published, and the preserved real V1 observation is locally reinterpreted under the V1.1 timestamp policy, the synchronized-observation repair line should close.

No repeat of the real synchronized capture is required unless a new concrete blocker appears.

The next planned implementation is:

`FORWARD_OUTCOME_LABELER_V1`

Its design must account for prospective observation time so that forward returns, MFE/MAE and target/stop ordering do not introduce lookahead from post-boundary point-in-time features.

Only after forward outcomes exist should Level A context evaluation proceed.
