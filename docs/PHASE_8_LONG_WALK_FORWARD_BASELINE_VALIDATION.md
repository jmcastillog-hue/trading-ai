# PHASE 8 LONG WALK FORWARD BASELINE VALIDATION

## Status

Phase 8.8 creates the LONG-side walk-forward baseline validation layer.

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

Phase 8.8 tests the primary LONG research candidate across multiple walk-forward-style windows.

The objective is to detect whether the candidate remains stable across separated chronological windows.

The objective is not to approve any candidate.

## Candidate scope

Primary candidate:

- LONG_BASE_FAILED_BREAKDOWN_V1

Secondary reference candidate:

- LONG_BASE_LIQUIDITY_SWEEP_V1

Blocked candidates remain excluded:

- LONG_BASE_FIB_PULLBACK_V1
- LONG_BASE_MTF_BULLISH_CONTINUATION_V1

## Walk-forward baseline design

The baseline uses chronological rolling windows.

Each window has:

- reference window
- validation window

The reference window exists for structure and chronology.

The validation window is where trades are measured.

This is not final walk-forward optimization.

This phase does not optimize parameters.

This phase does not tune thresholds.

This phase only measures whether the candidate behavior remains acceptable across separated windows.

## Metrics produced

The walk-forward baseline produces:

- window_id
- candidate_id
- train_start_index
- train_end_index
- test_start_index
- test_end_index
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
- window_classification

## Window classifications

Each candidate window receives one of the following labels:

- WF_PASS
- WF_WATCH
- WF_WEAK
- WF_FAIL
- WF_NO_SIGNAL

## Candidate-level classifications

Each candidate receives one of the following aggregate labels:

- WF_RESEARCH_CONTINUATION
- WF_WATCHLIST
- WF_WEAK
- WF_FAIL

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

## What Phase 8.8 does not do

Phase 8.8 does not:

- approve a LONG candidate
- select a production LONG strategy
- optimize parameters
- run final walk-forward validation
- run Monte Carlo validation
- run cost-aware validation
- enable paper trading
- enable real trading
- enable live alerts
- connect to Binance execution
- connect to Quantfury execution
- automate entries
- automate exits

## Expected result

Expected decision:

PHASE_8_8_LONG_WALK_FORWARD_BASELINE_VALIDATION_VALIDATED

## Recommended next phase

Recommended next step:

Phase 8.9 — LONG Cost-Aware Baseline Validation V1

Phase 8.9 should apply cost-aware stress to the surviving LONG research candidate while keeping all execution permissions disabled.