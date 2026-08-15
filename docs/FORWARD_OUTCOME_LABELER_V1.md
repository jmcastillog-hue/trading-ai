# Forward Outcome Labeler V1

## Purpose

`FORWARD_OUTCOME_LABELER_V1` converts a previously synchronized 15-minute observation into deterministic forward outcome labels without fetching market data, changing the primary LONG rule, writing official evidence, generating a trading signal, or authorizing execution.

It is the next component after the formally closed `SYNCHRONIZED_15M_OBSERVATION_V1_1` temporal-eligibility repair line.

## Scope

The labeler consumes:

1. one preserved synchronized observation cycle from `SYNCHRONIZED_15M_OBSERVATION_V1` or `SYNCHRONIZED_15M_OBSERVATION_V1_1`;
2. one external CSV containing already closed, contiguous Binance Spot `BTCUSDT` `15m` candles;
3. a separate create-only output directory outside the repository.

The labeler performs **zero network requests**. Acquisition of future candles is outside this capability and must be separately governed.

## Forward horizons

The frozen horizons are:

`1, 2, 4, 8, 16` closed 15-minute bars.

Every horizon has an explicit maturity state:

- `AVAILABLE` when all required closed bars exist;
- `PENDING` otherwise.

No partial horizon is extrapolated or backfilled.

## Two clocks, two anchors

### Primary rule outcome anchor

The frozen primary rule already exists at the reference close. Its outcome anchor is:

`reference_boundary_utc = reference_closed_candle_utc + 1 millisecond`

The anchor price is the primary entry price, which for the current frozen LONG candidate is the reference Spot close.

The first forward bar begins exactly at the reference boundary. No partially elapsed primary bar is used.

### Synchronized context outcome anchor

Microstructure is not fully available at the reference boundary because the public read-only snapshot requires sequential requests after the candle closes.

The synchronized context therefore uses:

`context_available_at = microstructure.captured_finished_at_utc`

and:

`context_anchor = first complete 15m bar open >= context_available_at`

Example:

- reference boundary: `23:45:00`;
- microstructure finished: `23:45:12`;
- the `23:45-00:00` bar is already partially elapsed;
- synchronized-context horizon bar 1 begins at `00:00:00`.

This prevents the outcome label from incorporating the first seconds of a bar that occurred before the complete synchronized context existed.

The context anchor price is the open price of that first full eligible bar.

## Metrics per available horizon

For both primary-rule and synchronized-context clocks, V1 produces:

- `forward_return = horizon_close / anchor_price - 1`;
- `mfe_return = maximum_high / anchor_price - 1`;
- `mae_return = minimum_low / anchor_price - 1`;
- horizon close price;
- maximum high price;
- minimum low price.

Returns are decimal fractions, not percentages.

## Target/stop ordering

Target/stop ordering applies only when the primary observation actually contains a candidate and therefore has frozen LONG geometry.

For each mature horizon, the possible states are:

- `TARGET_FIRST`;
- `STOP_FIRST`;
- `AMBIGUOUS_SAME_BAR`;
- `NEITHER_WITHIN_HORIZON`;
- `NOT_APPLICABLE` for non-candidate observations.

If a single 15-minute OHLC candle reaches both target and stop, V1 returns `AMBIGUOUS_SAME_BAR`.

It never invents intrabar ordering from OHLC data.

## Future candle contract

The future candle source must use exactly:

`open_time_utc,close_time_utc,symbol,timeframe,open,high,low,close,volume,candle_closed`

Requirements:

- UTF-8 CSV;
- `BTCUSDT` only;
- `15m` only;
- closed candles only;
- valid positive OHLC and non-negative volume;
- exact 15-minute candle geometry;
- strictly ordered and unique timestamps;
- no gaps between provided rows.

If the source begins after a required anchor while later rows are present, V1 fails closed instead of silently skipping missing bars.

## Preserved synchronized observation provenance

`build_observation_descriptor_from_synchronized_session(...)` verifies the session-level manifest, selects exactly one completed cycle, verifies Spot/Futures candle match, verifies the Microstructure V1.1 artifact manifest, and records:

- source session capability and hashes;
- cycle index;
- reference close and boundary;
- reference price;
- candidate state;
- candidate entry/stop/target when applicable;
- `microstructure.captured_finished_at_utc` as context availability.

If the cycle is a non-candidate, candidate rows must be empty and target/stop are `null`.

If the cycle is a candidate, exactly one candidate row must exist and satisfy `stop < entry < target`.

## Package contract

The create-only package contains:

- `observation_descriptor.json`;
- `forward_outcomes.json`;
- `labeler_checks.json`;
- `manifest.sha256`.

The package requires exact authorization:

`PREPARE_FORWARD_OUTCOME_LABEL_PACKAGE_V1`

Outputs must remain outside the repository and are validated transactionally before publication.

## Scientific boundaries

V1 does not:

- fetch future market data;
- install a scheduler;
- run in the background;
- use WebSocket;
- infer intrabar order;
- modify `LONG_BASE_FAILED_BREAKDOWN_V1`;
- create or cancel a candidate;
- convert context into direction;
- write the official forward dataset;
- enable live alerts;
- enable paper trading;
- enable real capital;
- execute on any exchange.

## Official evidence

The official dataset and official manifest are hash-checked before and after package preparation. The official append gate must remain disabled.

Forward labels created by this component are research artifacts only. A separate later gate must decide whether and how any labels become part of an evaluation dataset.

## Validation strategy

The sandbox validation covers:

- all five horizons;
- primary vs context anchor separation;
- context availability at an exact boundary and inside a partially elapsed bar;
- forward return, MFE and MAE;
- partial maturity / `PENDING`;
- target first;
- stop first;
- ambiguous same-bar target+stop;
- neither touched;
- non-candidate `NOT_APPLICABLE`;
- closed-candle enforcement;
- timestamp gaps and anchor gaps;
- candidate geometry;
- synchronized session provenance;
- create-only package roundtrip;
- unchanged official artifacts;
- zero network activity.

## Approved continuation

After V1 is sandbox validated and intentionally published, the next controlled step is to obtain an appropriate **separately governed** closed-candle future source for a preserved synchronized observation and run one local label package.

Only after the outcome-label contract is validated on real preserved observations should the project implement:

`Context Feature Pack V1 — Level A Standard`

followed by the Context Evaluation Engine and, only if robust incremental value is demonstrated, a Context Quality Gate.
