# PHASE 8 LONG COST AWARE BASELINE VALIDATION

## Status

Phase 8.9 creates the LONG-side cost-aware baseline validation layer.

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

Phase 8.4 measured LONG candidates on historical OHLC data.

Phase 8.5 classified candidates using historical baseline evidence.

Phase 8.6 tested eligible candidates on an OOS baseline window.

Phase 8.7 converted OOS evidence into a restrictive research decision gate.

Phase 8.8 tested the primary and secondary LONG candidates across walk-forward-style windows.

Phase 8.9 applies estimated trading friction to the surviving LONG research candidates.

The objective is to detect whether the LONG candidates remain viable after fee, spread, and slippage assumptions.

The objective is not to approve any candidate.

## Candidate scope

Primary candidate:

- LONG_BASE_FAILED_BREAKDOWN_V1

Secondary reference candidate:

- LONG_BASE_LIQUIDITY_SWEEP_V1

Blocked candidates remain excluded:

- LONG_BASE_FIB_PULLBACK_V1
- LONG_BASE_MTF_BULLISH_CONTINUATION_V1

## Cost-aware baseline design

The baseline applies round-trip cost assumptions to each historical walk-forward trade.

Cost is converted into R units using the trade risk distance.

For each trade:

- risk_bps = absolute risk distance divided by entry price
- cost_r = round_trip_cost_bps divided by risk_bps
- cost_adjusted_result_r = raw_result_r minus cost_r

This produces a cost-adjusted result in R.

## Cost profiles

The first cost-aware baseline uses three conservative profiles:

- LOW_FRICTION
- BASELINE_FRICTION
- STRESS_FRICTION

The profiles are intentionally simple.

They are not broker-specific.

They are not exchange-specific.

They are not Binance execution settings.

They are not Quantfury execution settings.

They are research assumptions only.

## Metrics produced

The cost-aware baseline produces:

- candidate_id
- cost_profile
- trades
- wins
- losses
- open_trades
- raw_total_result_r
- cost_adjusted_total_result_r
- cost_adjusted_average_result_r
- gross_win_r
- gross_loss_r
- cost_adjusted_profit_factor
- max_drawdown_r
- cost_classification

## Cost classifications

Each candidate and cost profile receives one of the following labels:

- COST_RESEARCH_CONTINUATION
- COST_WATCHLIST
- COST_WEAK
- COST_FAIL
- COST_NO_SIGNAL

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

## What Phase 8.9 does not do

Phase 8.9 does not:

- approve a LONG candidate
- select a production LONG strategy
- connect to Binance
- connect to Quantfury
- use live exchange fees
- run Monte Carlo validation
- enable paper trading
- enable real trading
- enable live alerts
- automate entries
- automate exits

## Expected result

Expected decision:

PHASE_8_9_LONG_COST_AWARE_BASELINE_VALIDATION_VALIDATED

## Recommended next phase

Recommended next step:

Phase 8.10 — LONG Monte Carlo Baseline Validation V1

Phase 8.10 should stress the surviving LONG candidate sequences using Monte Carlo-style reshuffling while keeping all execution permissions disabled.