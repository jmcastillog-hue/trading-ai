# PHASE 8 LONG OOS BASELINE VALIDATION

## Status

Phase 8.6 creates the first LONG-side out-of-sample baseline validation layer.

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

Phase 8.4 measured LONG candidates on available historical OHLC data.

Phase 8.5 classified candidates using historical baseline evidence.

Phase 8.6 tests only the candidates classified as WATCHLIST or RESEARCH_CONTINUATION on a separated out-of-sample window.

The objective is to check whether promising baseline LONG candidates survive outside the initial comparison window.

The objective is not to approve any candidate.

## Candidate scope

Only candidates classified as WATCHLIST or RESEARCH_CONTINUATION are eligible.

Current expected eligible candidates:

- LONG_BASE_FAILED_BREAKDOWN_V1
- LONG_BASE_LIQUIDITY_SWEEP_V1

Rejected candidates do not advance unless redesigned.

Current expected excluded candidates:

- LONG_BASE_FIB_PULLBACK_V1
- LONG_BASE_MTF_BULLISH_CONTINUATION_V1

## OOS split

The Phase 8.6 baseline uses a chronological split of the available OHLC data.

Default split:

- first 70 percent: baseline/reference window
- last 30 percent: OOS validation window

This is a baseline OOS split.

It is not a definitive robustness proof.

A stronger future validation should use multiple windows, walk-forward testing, cost-aware testing, Monte Carlo testing, and forward evidence.

## OOS classification labels

Each eligible candidate must receive one of the following OOS labels:

- OOS_RESEARCH_CONTINUATION
- OOS_WATCHLIST
- OOS_WEAK
- OOS_FAIL
- OOS_NO_SIGNAL

## OOS classification meaning

### OOS_RESEARCH_CONTINUATION

The candidate produced positive OOS evidence and may continue to stricter validation.

This does not mean approval.

### OOS_WATCHLIST

The candidate produced mixed or limited OOS evidence and should remain under observation.

This does not mean approval.

### OOS_WEAK

The candidate produced weak OOS evidence and should not be prioritized.

### OOS_FAIL

The candidate failed the OOS baseline and should not continue as-is.

### OOS_NO_SIGNAL

The candidate produced no OOS trades in the available window.

This is inconclusive and must not be treated as approval.

## Metrics produced

The OOS validation produces:

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
- oos_classification
- oos_recommendation

## Important distinction

Phase 8.6 is an OOS baseline validation layer.

It is not:

- final OOS validation
- walk-forward validation
- Monte Carlo validation
- cost-aware validation
- readiness approval
- paper trading approval
- real capital approval

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

## What Phase 8.6 does not do

Phase 8.6 does not:

- approve a LONG candidate
- select a production LONG strategy
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

PHASE_8_6_LONG_OOS_BASELINE_VALIDATION_VALIDATED

## Recommended next phase

Recommended next step:

Phase 8.7 — LONG OOS Decision Gate V1

Phase 8.7 should decide which LONG candidates, if any, deserve deeper validation after OOS baseline testing, while keeping all execution permissions disabled.