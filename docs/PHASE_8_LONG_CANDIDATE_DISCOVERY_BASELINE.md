# PHASE 8 LONG CANDIDATE DISCOVERY BASELINE

## Status

Phase 8.2 creates the first LONG-side candidate discovery baseline.

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

Phase 8.2 creates an initial registry of LONG research candidates.

These candidates are not strategies.

They are only baseline hypotheses for future measurement.

The purpose is to define simple, testable, discardable LONG ideas before running deeper validation.

## Why this phase is restrictive

The LONG side must not be treated as a mirror copy of the SHORT candidate.

The current official SHORT candidate remains:

- TARGET_SHORT_FIB_V5_MTF_V3_1 + FIXED_RR_2_5

The LONG side requires its own discovery, validation, evidence gates, and rejection rules.

## Baseline LONG candidates

Phase 8.2 defines four initial LONG baseline candidates:

- LONG_BASE_FIB_PULLBACK_V1
- LONG_BASE_LIQUIDITY_SWEEP_V1
- LONG_BASE_MTF_BULLISH_CONTINUATION_V1
- LONG_BASE_FAILED_BREAKDOWN_V1

## Candidate 1 — LONG_BASE_FIB_PULLBACK_V1

Hypothesis:

A bullish context may produce valid LONG opportunities after controlled pullbacks into Fibonacci zones.

Core idea:

- market bias is bullish or recovering
- price pulls back into a predefined Fibonacci zone
- entry is only considered after confirmation
- stop remains below the pullback structure
- target remains above entry

Required LONG price structure:

- stop_price < entry_price < target_price

Status:

- discovery only
- not approved

## Candidate 2 — LONG_BASE_LIQUIDITY_SWEEP_V1

Hypothesis:

A sweep below local lows followed by recovery may produce valid LONG opportunities if the breakdown fails.

Core idea:

- price sweeps sell-side liquidity
- price reclaims the swept level
- entry is only considered after recovery confirmation
- stop remains below the swept low
- target remains above entry

Required LONG price structure:

- stop_price < entry_price < target_price

Status:

- discovery only
- not approved

## Candidate 3 — LONG_BASE_MTF_BULLISH_CONTINUATION_V1

Hypothesis:

A higher-timeframe bullish context may produce continuation LONG opportunities after lower-timeframe pullbacks.

Core idea:

- higher timeframe is bullish or transitioning bullish
- lower timeframe pulls back without invalidating the trend
- entry is only considered after continuation confirmation
- stop remains below local invalidation
- target remains above entry

Required LONG price structure:

- stop_price < entry_price < target_price

Status:

- discovery only
- not approved

## Candidate 4 — LONG_BASE_FAILED_BREAKDOWN_V1

Hypothesis:

A failed breakdown below support may produce valid LONG opportunities when price recovers and rejects lower prices.

Core idea:

- support breaks temporarily
- breakdown fails
- price reclaims the failed breakdown zone
- entry is only considered after confirmation
- stop remains below the failed breakdown low
- target remains above entry

Required LONG price structure:

- stop_price < entry_price < target_price

Status:

- discovery only
- not approved

## Discovery rules

Every candidate must define:

- candidate_id
- direction
- router_decision
- hypothesis
- trigger_family
- primary_context
- entry_condition
- invalidation_rule
- confirmation_requirement
- price_structure_rule
- expected_signal_type
- evidence_goal
- known_failure_modes
- research_priority
- approval_status

## Required direction

Every candidate must use:

- direction = LONG

## Required router state

Every candidate must use:

- router_decision = WATCH_ONLY

## Required approval status

Every candidate must remain:

- DISCOVERY_BASELINE_ONLY

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

## What Phase 8.2 does not do

Phase 8.2 does not:

- run historical backtests
- run walk-forward validation
- run Monte Carlo validation
- approve a LONG candidate
- select a production LONG strategy
- enable paper trading
- enable real trading
- enable live alerts
- connect to Binance execution
- connect to Quantfury execution
- automate entries
- automate exits

## Expected result

Phase 8.2 should produce a candidate registry and confirm that every LONG baseline candidate is structurally valid but not approved.

Expected decision:

PHASE_8_2_LONG_CANDIDATE_DISCOVERY_BASELINE_DEFINED

## Recommended next phase

Recommended next step:

Phase 8.3 — LONG Baseline Structural Backtest Harness V1

Phase 8.3 should begin measuring these candidates using historical data, but still without approving execution.