# Phase 10.42R.2H — Frozen Recovery Candidate Controlled Historical Evaluation Preregistration

## Status

Phase 10.42R.2H freezes the protocol for a future controlled historical evaluation of the six corrected SHORT recovery variants accepted synthetically in Phase 10.42R.2G.

This phase is preregistration-only. It does not read OHLCV, historical result reports, retrospective lockboxes or prospective holdouts. It does not execute a backtest, calculate performance, compare or rank candidates, select a winner, write the official forward dataset, generate signals, enable alerts, permit paper trading, use capital, connect to an exchange or automate execution.

## Source authority

The preregistration is anchored to:

- Phase 10.42R.2B normalized cost accounting and recovery preregistration;
- Phase 10.42R.2D frozen candidate families, variants and multiplicity;
- Phase 10.42R.2G independent synthetic acceptance;
- corrected implementation `v2`;
- source commit `a1ced46cf71f4a5880d74b76ad2bc8d1eaae16e3`.

Every source anchor is checked with normalized SHA-256 so Windows CRLF conversion cannot silently alter the scientific contract.

## Fixed candidate scope

The evaluation order remains:

1. `RCV_SHORT_UPSIDE_SWEEP_REVERSAL_F01_N48_V01`
2. `RCV_SHORT_UPSIDE_SWEEP_REVERSAL_F01_N96_V02`
3. `RCV_SHORT_BREAKDOWN_RETEST_F02_N48_V01`
4. `RCV_SHORT_BREAKDOWN_RETEST_F02_N96_V02`
5. `RCV_SHORT_EMA_PULLBACK_CONTINUATION_F03_S000_V01`
6. `RCV_SHORT_EMA_PULLBACK_CONTINUATION_F03_S025_V02`

The six variants belong to three frozen families and one family-wise multiplicity pool. Result-driven deletion, mutation, addition or reordering is forbidden.

## Dataset contract

The fixed cohort is:

- symbols: `BTCUSDT`, `ETHUSDT`, `SOLUSDT`;
- timeframes: `15m`, `1h`, `4h`;
- nine mandatory logical OHLCV slots.

Phase 2H does not bind or read physical files. A future input-manifest or harness-design phase must bind all nine slots to immutable paths and SHA-256 values before the first content read. Each manifest row must also freeze byte size, row count, UTC coverage, schema and provenance.

The `15m` slot is the signal and simulated execution clock. `1h` and `4h` are closed-candle context only.

## Evidence windows

All intervals are half-open UTC intervals.

| Window | Interval | Tier | Phase 2H |
|---|---|---|---|
| Known evidence | `[2022-01-01, 2026-01-01)` | Descriptive known evidence | No content read |
| Retrospective lockbox | `[2026-01-01, 2026-07-20)` | Secondary one-time evidence | Sealed |
| Prospective holdout | `[2026-07-20, 2027-01-20)` | Primary confirmatory evidence | Sealed |

Known 2022–2025 evidence can never be relabeled as holdout. Neither lockbox may be opened by Phase 2H or by the next harness-design phase.

## Timing and simulated trade resolution

The future evaluator must preserve:

- completed 15m signal bar `t`;
- 1H and 4H context available only after each source candle closes;
- fill at the next 15m open `t + 1`;
- invalid SHORT gap blocked when stop is not strictly above entry;
- one open position maximum;
- fixed target `2.5R`;
- stop-first resolution when stop and target occur in the same bar;
- time exit at entry-relative 15m bar 240.

These are research-simulation contracts only. They grant no execution permission.

## Cost accounting

Every future result must begin with frictionless gross R and apply exactly one fixed round-trip profile under:

`FRICTIONLESS_GROSS_R_TO_SINGLE_PROFILE_NET_R_V1`

| Profile | Fee | Spread | Slippage | Role |
|---|---:|---:|---:|---|
| Binance scalp base | 0.0008 | 0.0004 | 0.0004 | Primary base gate |
| Binance scalp stress | 0.0012 | 0.0008 | 0.0008 | Primary stress gate |
| Quantfury swing base | 0.0000 | 0.0035 | 0.0005 | Secondary diagnostic |
| Quantfury swing stress | 0.0000 | 0.0060 | 0.0010 | Secondary diagnostic |
| Extreme stress | 0.0015 | 0.0080 | 0.0020 | Extreme diagnostic |

Embedded fees or spread may not be charged twice.

## Metrics and slices

Primary metrics:

- trade count;
- net expectancy R;
- profit factor;
- chronological max drawdown R;
- positive-window rate;
- Holm-adjusted p-value.

Frictionless gross expectancy and profit factor remain diagnostic only.

Required slices:

- aggregate;
- symbol;
- calendar year;
- volatility tercile;
- corrected closed-candle trend regime;
- signal family;
- cost profile.

No weak slice may be deleted after results are known.

Chronological drawdown ordering is:

`EXIT_TIME_UTC_THEN_ENTRY_TIME_UTC_THEN_SYMBOL_THEN_SOURCE_TRADE_ROW_ASCENDING`

## Multiplicity and gates

The six p-values form one family-wise pool. Evaluation order is frozen and step-down Holm-Bonferroni is applied at family-wise alpha `0.05`. The underlying p-value method is inherited exactly from the Phase 2D frozen specification rather than silently redefined here.

Required gates include:

- at least 100 aggregate trades;
- at least 20 trades per symbol;
- Binance-base profit factor at least 1.05;
- positive Binance-base aggregate expectancy;
- positive Binance-base expectancy for every symbol;
- non-negative Binance-base expectancy for every calendar year;
- non-negative Binance-stress expectancy;
- Binance-stress profit factor at least 1.00;
- Holm-adjusted p-value at most 0.05;
- all predeclared stability slices non-failing.

Passing known-evidence gates is not confirmatory evidence and does not select a winner. It may support only a later, separately approved lockbox decision.

## Mutation and interpretation

Any post-result change to a family, parameter, threshold, timing rule, cost profile, slice, metric, statistical method or promotion gate requires a new version. Data already viewed can no longer support an unopened-test claim for that new version.

Known-evidence output may not be represented as profitability certification, robustness certification, paper-trading readiness or execution approval.

## Passing decision

`CONTROLLED_HISTORICAL_EVALUATION_PREREGISTRATION_LOCKED`

A passing decision permits only:

`PHASE_10_42R_2I_FROZEN_RECOVERY_CANDIDATE_CONTROLLED_HISTORICAL_EVALUATION_HARNESS_DESIGN_V1`

It does not permit historical evaluation itself.

## Safety boundary

Every operational permission remains false:

- real-data access in Phase 2H;
- historical evaluation;
- retrospective lockbox access;
- prospective holdout access;
- performance generation;
- candidate comparison or ranking;
- winner selection;
- candidate mutation;
- forward observation;
- official dataset writes;
- evidence persistence;
- signal generation;
- live alerts;
- paper trading;
- real capital;
- market or exchange execution;
- automation;
- OpenClaw operational integration.
