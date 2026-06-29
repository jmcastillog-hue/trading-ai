# PHASE 8 LONG HISTORICAL BASELINE BACKTEST

## Status

Phase 8.4 creates the first LONG-side historical baseline backtest.

This phase does not approve a LONG strategy.

This phase does not establish the LONG side.

This phase does not approve LONG entries.

This phase does not approve paper trading execution.

This phase does not approve real capital execution.

This phase does not approve live alerts.

This phase does not approve exchange execution.

This phase does not approve automation.

## Purpose

Phase 8.1 defined the LONG-side validation contract.

Phase 8.2 defined the first LONG baseline candidate registry.

Phase 8.3 validated a controlled structural backtest harness.

Phase 8.4 begins measuring the LONG baseline candidates on available historical OHLC data.

The goal is to produce initial historical metrics.

The goal is not to prove robustness.

The goal is not to approve any candidate.

## Candidate scope

The historical baseline measures the four Phase 8.2 candidates:

- LONG_BASE_FIB_PULLBACK_V1
- LONG_BASE_LIQUIDITY_SWEEP_V1
- LONG_BASE_MTF_BULLISH_CONTINUATION_V1
- LONG_BASE_FAILED_BREAKDOWN_V1

## Historical data scope

The backtest searches for available OHLC data in local project data files.

Preferred source:

- data/btcusdt_15m.csv

Alternative supported names may also be searched if available.

## Baseline indicators

The historical harness may compute:

- EMA20
- EMA50
- EMA200
- RSI14
- ATR14
- rolling highs
- rolling lows

## Candidate baseline logic

The candidate rules are intentionally simple.

They are not optimized.

They are not production rules.

They are not final strategy definitions.

They are baseline hypotheses for measurement only.

## Metrics produced

The harness produces:

- trades
- wins
- losses
- open_trades
- win_rate
- gross_win_r
- gross_loss_r
- profit_factor
- total_result_r
- average_result_r
- max_drawdown_r

## Important distinction

Phase 8.4 is the first historical baseline measurement.

It is not:

- out-of-sample validation
- walk-forward validation
- Monte Carlo validation
- cost-aware validation
- readiness approval
- paper trading approval
- real capital approval

## Approval state

Every candidate remains:

- DISCOVERY_BASELINE_ONLY
- HISTORICAL_BASELINE_ONLY
- not approved

## Required safety state

The following must remain false:

- long_strategy_approved = False
- long_entries_approved = False
- long_side_established = False
- paper_trade_execution_allowed = False
- real_capital_allowed = False
- live_alerts_allowed = False
- exchange_execution_allowed = False
- automation_allowed = False
- execution_allowed = False
- real_entries_approved = False
- total_project_completed = False

## What Phase 8.4 does not do

Phase 8.4 does not:

- approve a LONG candidate
- run out-of-sample validation
- run walk-forward validation
- run Monte Carlo validation
- enable paper trading
- enable real trading
- enable live alerts
- connect to Binance execution
- connect to Quantfury execution
- automate entries
- automate exits

## Expected result

Expected decision:

PHASE_8_4_LONG_HISTORICAL_BASELINE_BACKTEST_VALIDATED

## Recommended next phase

Recommended next step:

Phase 8.5 — LONG Candidate Historical Comparison V1

Phase 8.5 should compare candidates and classify them as reject, weak, watchlist, or research-continuation candidates without approving execution.