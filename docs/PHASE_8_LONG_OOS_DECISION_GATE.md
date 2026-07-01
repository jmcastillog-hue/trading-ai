# PHASE 8 LONG OOS DECISION GATE

## Status

Phase 8.7 creates the LONG-side OOS decision gate.

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

Phase 8.7 converts that OOS evidence into a restrictive research decision.

The objective is to decide which LONG candidates may continue to stricter validation.

The objective is not to approve any candidate.

## Current OOS evidence

The current OOS baseline result showed:

- LONG_BASE_FAILED_BREAKDOWN_V1: OOS_RESEARCH_CONTINUATION
- LONG_BASE_LIQUIDITY_SWEEP_V1: OOS_WATCHLIST

The rejected historical candidates remain excluded:

- LONG_BASE_FIB_PULLBACK_V1
- LONG_BASE_MTF_BULLISH_CONTINUATION_V1

## Decision labels

Each candidate must receive one of the following gate decisions:

- ADVANCE_TO_STRICT_VALIDATION
- SECONDARY_WATCHLIST_ONLY
- HOLD_FOR_REDESIGN
- BLOCKED_REJECTED_HISTORICAL
- BLOCKED_AFTER_OOS
- INSUFFICIENT_OOS_SIGNAL

## Decision meaning

### ADVANCE_TO_STRICT_VALIDATION

The candidate may continue to stricter validation.

This does not mean approval.

This does not mean paper trading.

This does not mean real trading.

### SECONDARY_WATCHLIST_ONLY

The candidate remains under observation.

It may be tested again later or used as a secondary research reference.

This does not mean approval.

### HOLD_FOR_REDESIGN

The candidate is not good enough to continue as-is but may be redesigned later.

### BLOCKED_REJECTED_HISTORICAL

The candidate was rejected before OOS and must not advance without redesign.

### BLOCKED_AFTER_OOS

The candidate failed the OOS baseline and must not continue as-is.

### INSUFFICIENT_OOS_SIGNAL

The candidate did not produce enough OOS evidence.

This is inconclusive and must not be treated as approval.

## Expected decision

Expected primary research candidate:

- LONG_BASE_FAILED_BREAKDOWN_V1

Expected secondary watchlist candidate:

- LONG_BASE_LIQUIDITY_SWEEP_V1

Expected blocked candidates:

- LONG_BASE_FIB_PULLBACK_V1
- LONG_BASE_MTF_BULLISH_CONTINUATION_V1

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

## What Phase 8.7 does not do

Phase 8.7 does not:

- approve a LONG candidate
- select a production LONG strategy
- run walk-forward validation
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

PHASE_8_7_LONG_OOS_DECISION_GATE_VALIDATED

## Recommended next phase

Recommended next step:

Phase 8.8 — LONG Walk-Forward Baseline Validation V1

Phase 8.8 should test the primary LONG research candidate with stricter walk-forward-style windows while keeping all execution permissions disabled.