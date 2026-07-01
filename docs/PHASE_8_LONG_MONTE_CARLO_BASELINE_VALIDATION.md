# PHASE 8 LONG MONTE CARLO BASELINE VALIDATION

## Status

Phase 8.10 creates the LONG-side Monte Carlo baseline validation layer.

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

Phase 8.9 applied estimated trading friction to the surviving LONG candidates.

Phase 8.10 applies Monte Carlo-style sequence stress to the cost-adjusted LONG results.

The objective is to detect whether the LONG candidates remain acceptable under adverse result sequencing.

The objective is not to approve any candidate.

## Candidate scope

Primary candidate:

- LONG_BASE_FAILED_BREAKDOWN_V1

Secondary reference candidate:

- LONG_BASE_LIQUIDITY_SWEEP_V1

Blocked candidates remain excluded:

- LONG_BASE_FIB_PULLBACK_V1
- LONG_BASE_MTF_BULLISH_CONTINUATION_V1

## Monte Carlo baseline design

The baseline uses cost-adjusted trade results from the STRESS_FRICTION profile.

For each candidate, the validation creates deterministic bootstrap simulations.

Each simulation samples the candidate trade results with replacement.

Each simulation preserves the same number of trades as the source candidate sequence.

The objective is to estimate how sensitive the candidate is to:

- adverse sequencing
- unfavorable resampling
- drawdown clustering
- losing streaks
- weak positive expectancy

This is a baseline Monte Carlo test.

It is not a final statistical proof.

## Metrics produced

The Monte Carlo baseline produces:

- candidate_id
- simulation_id
- simulated_trade_count
- simulated_total_result_r
- simulated_average_result_r
- simulated_max_drawdown_r
- simulated_longest_losing_streak
- probability_positive
- p05_total_result_r
- p50_total_result_r
- p95_total_result_r
- p05_max_drawdown_r
- worst_max_drawdown_r
- mc_classification

## Monte Carlo classifications

Each candidate receives one of the following labels:

- MC_RESEARCH_CONTINUATION
- MC_WATCHLIST
- MC_WEAK
- MC_FAIL
- MC_NO_SIGNAL

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

## What Phase 8.10 does not do

Phase 8.10 does not:

- approve a LONG candidate
- select a production LONG strategy
- connect to Binance
- connect to Quantfury
- use live exchange fees
- run real execution
- enable paper trading
- enable real trading
- enable live alerts
- automate entries
- automate exits

## Expected result

Expected decision:

PHASE_8_10_LONG_MONTE_CARLO_BASELINE_VALIDATION_VALIDATED

## Recommended next phase

Recommended next step:

Phase 8.11 — LONG Baseline Readiness Gate V1

Phase 8.11 should consolidate the LONG baseline evidence and decide whether any LONG candidate deserves future forward observation while keeping all execution permissions disabled.