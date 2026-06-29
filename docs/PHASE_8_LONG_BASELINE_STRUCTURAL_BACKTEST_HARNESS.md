# PHASE 8 LONG BASELINE STRUCTURAL BACKTEST HARNESS

## Status

Phase 8.3 creates the first LONG-side structural backtest harness.

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

Phase 8.3 creates a controlled structural backtest harness for those candidates.

The purpose is not to prove profitability.

The purpose is to prove that LONG candidates can be measured safely and consistently.

## Candidate scope

The harness measures the four baseline LONG candidates from Phase 8.2:

- LONG_BASE_FIB_PULLBACK_V1
- LONG_BASE_LIQUIDITY_SWEEP_V1
- LONG_BASE_MTF_BULLISH_CONTINUATION_V1
- LONG_BASE_FAILED_BREAKDOWN_V1

## Structural measurement

The harness verifies:

- candidate identity
- LONG direction
- WATCH_ONLY router state
- valid LONG price structure
- entry_price
- stop_price
- target_price
- risk
- reward
- risk_reward
- resolution_status
- result_r
- mfe_r
- mae_r
- bars_to_resolution

## LONG price structure

Every measured LONG candidate must satisfy:

- stop_price < entry_price < target_price

Invalid LONG structures must be rejected.

## Controlled outcomes

The Phase 8.3 harness may include mixed controlled outcomes:

- TARGET_HIT
- STOP_HIT
- OPEN_TIMEOUT

Mixed outcomes are intentional.

The objective is to prove measurement behavior, not to force all candidates to win.

## Important distinction

Phase 8.3 is a structural harness.

It is not a robust historical backtest.

It is not out-of-sample validation.

It is not walk-forward validation.

It is not Monte Carlo validation.

It is not readiness approval.

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

## Approval state

Every candidate remains:

- DISCOVERY_BASELINE_ONLY
- MEASURED_BASELINE_ONLY
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

## What Phase 8.3 does not do

Phase 8.3 does not:

- approve a LONG candidate
- run production historical validation
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

PHASE_8_3_LONG_BASELINE_STRUCTURAL_BACKTEST_HARNESS_VALIDATED

## Recommended next phase

Recommended next step:

Phase 8.4 — LONG Historical Baseline Backtest V1

Phase 8.4 should begin measuring candidates on real historical OHLC data while keeping all execution permissions disabled.