# PHASE 8 LONG CANDIDATE HISTORICAL COMPARISON

## Status

Phase 8.5 creates the first LONG-side historical candidate comparison layer.

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

Phase 8.4 measured LONG baseline candidates on available historical OHLC data.

Phase 8.5 compares those historical baseline results and classifies each candidate.

The objective is to separate weak candidates from candidates that deserve further research.

The objective is not to approve any candidate.

## Candidate scope

The comparison covers the four Phase 8.2 LONG baseline candidates:

- LONG_BASE_FIB_PULLBACK_V1
- LONG_BASE_LIQUIDITY_SWEEP_V1
- LONG_BASE_MTF_BULLISH_CONTINUATION_V1
- LONG_BASE_FAILED_BREAKDOWN_V1

## Classification labels

Each candidate must receive one of the following labels:

- REJECT
- WEAK
- WATCHLIST
- RESEARCH_CONTINUATION

## Classification meaning

### REJECT

The candidate shows poor baseline historical evidence.

A rejected candidate should not advance unless redesigned.

### WEAK

The candidate is not good enough to continue as-is.

A weak candidate may be reviewed later, but should not be prioritized.

### WATCHLIST

The candidate shows some positive evidence but not enough to be treated as a serious candidate.

A watchlist candidate may continue to stricter testing only with caution.

### RESEARCH_CONTINUATION

The candidate shows enough baseline evidence to deserve further research.

This does not mean approval.

This does not mean paper trading.

This does not mean real trading.

## Historical comparison metrics

The comparison may use:

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

## Baseline classification rules

The first classification rules are intentionally simple and conservative.

A candidate may be rejected if:

- profit_factor is below 0.75
- total_result_r is strongly negative
- historical drawdown is poor
- win_rate is poor

A candidate may be weak if:

- profit_factor is below 1.0
- total_result_r is negative or flat
- trade count is too low
- evidence is inconclusive

A candidate may be watchlist if:

- total_result_r is positive
- profit_factor is above 1.0
- trade count is sufficient
- drawdown is not excessive

A candidate may continue research if:

- total_result_r is positive
- profit_factor is meaningfully above 1.0
- trade count is sufficient
- drawdown is acceptable
- evidence is better than the other candidates

## Important distinction

Phase 8.5 is a historical comparison layer.

It is not:

- out-of-sample validation
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

## What Phase 8.5 does not do

Phase 8.5 does not:

- approve a LONG candidate
- select a production LONG strategy
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

PHASE_8_5_LONG_CANDIDATE_HISTORICAL_COMPARISON_VALIDATED

## Recommended next phase

Recommended next step:

Phase 8.6 — LONG OOS Baseline Validation V1

Phase 8.6 should test only the candidates classified as WATCHLIST or RESEARCH_CONTINUATION on a separated out-of-sample window, while keeping all execution permissions disabled.