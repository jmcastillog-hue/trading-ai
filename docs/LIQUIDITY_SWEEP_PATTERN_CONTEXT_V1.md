# Liquidity Sweep Pattern Context V1

## Purpose

`LIQUIDITY_SWEEP_PATTERN_CONTEXT_V1` is a Level A observed-market producer.
It converts an already-preserved BTCUSDT 15m closed-candle capture into a
strictly descriptive sweep/reclaim context.

The producer performs no market-data acquisition and never calls Binance.

## Scientific boundary

The phrase "liquidity sweep" is used only as a price-action proxy. Trading
through a previous high or low does not prove that hidden stops, forced
liquidations, or institutional orders actually existed at that level.

V1 therefore freezes:

- `sweep_is_price_action_proxy_only = true`
- `hidden_stop_orders_observed = false`
- `liquidations_observed = false`

## Source

The source is an external, immutable
`LONG_PRIMARY_PUBLIC_CLOSED_CANDLE_CAPTURE_V1` directory.

The published capture validator is reused locally. The source is never
recaptured by this feature.

## Policy floor

The policy effective floor is:

`2026-08-17T00:00:00+00:00`

This is a research-governance timestamp, not a market event.

A deterministic transform created today must not be represented as if it had
been preregistered for an older observation. Therefore:

`available_at_utc = max(source_captured_at_utc, policy_effective_from_utc)`

A pre-policy capture can be preserved for audit/regression, but the Context
Feature Pack marks it point-in-time ineligible for the old observation.

## Alignment

The source latest closed candle must equal
`reference_closed_candle_utc` exactly. The observation reference boundary must
be exactly one millisecond after that close.

The source capture timestamp must be at or after the reference boundary.

The feature uses only candles at or before that reference and sets:

`information_cutoff_utc = reference_boundary_utc`

## Frozen rolling geometry

For current closed candle `t`, the previous 48 candles are `t-48 ... t-1`.

V1 calculates:

- `rolling_low_48 = min(low[t-48:t])`
- `rolling_high_48 = max(high[t-48:t])`

The current candle is never included in either rolling extreme.

## Sweep flags

Lower-side sweep: `latest.low < rolling_low_48`.

Lower-side same-bar reclaim: `latest.close > rolling_low_48`.

Upper-side sweep: `latest.high > rolling_high_48`.

Upper-side same-bar rejection: `latest.close < rolling_high_48`.

The feature also records whether both extremes were swept in the same candle.
No one-sided or two-sided event receives bullish or bearish meaning.

## Descriptive measurements

V1 also records ATR14, excursion through the rolling extremes in bps and ATR
units, close distance from both extremes, upper/lower wick fraction, body
fraction, and latest volume relative to the median of the previous 48 bars.

These variables are descriptive and are not a composite score.

## Relationship to existing strategy logic

The existing primary rule `LONG_BASE_FAILED_BREAKDOWN_V1` is not called,
modified, confirmed, vetoed, or replaced.

The secondary/watchlist name `LONG_BASE_LIQUIDITY_SWEEP_V1` is not promoted to
an official candidate by this producer.

The feature emits no candidate, entry, stop, target, or trade action.

## Package authorization

Authorization:

`PREPARE_LIQUIDITY_SWEEP_PATTERN_CONTEXT_V1`

Inputs:

- external observation descriptor JSON;
- external pre-existing closed-candle capture directory;
- explicit `produced_at_utc`.

Output:

- `liquidity_sweep_pattern_context_component.json`
- `producer_checks.json`
- `manifest.sha256`

The output is external, create-only, and transactional.

## Safety

No market-data request, source recapture, Git network request, forward-outcome
lookup, candidate modification, primary-rule modification, signal generation,
live alert, paper trade, real-capital action, exchange execution, or official
dataset append is allowed.

## Evaluation boundary

One sweep observation is not evidence of an edge. The later Context Evaluation
Engine must evaluate these preregistered variables over sufficient
point-in-time observations and separately preserved forward outcomes.
