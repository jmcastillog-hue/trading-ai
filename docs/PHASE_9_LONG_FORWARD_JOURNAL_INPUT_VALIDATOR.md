# PHASE 9 LONG FORWARD JOURNAL INPUT VALIDATOR

## Status

Phase 9.3 creates the LONG-side forward journal input validator.

This phase does not start forward observation.

This phase does not record real forward signals.

This phase does not accept real market observations as evidence.

This phase does not generate live signals.

This phase does not approve a LONG strategy.

This phase does not establish the LONG side for execution.

This phase does not approve LONG entries.

This phase does not approve paper trading execution.

This phase does not approve real capital execution.

This phase does not approve live alerts.

This phase does not approve exchange execution.

This phase does not approve automation.

## Purpose

Phase 9.1 created the LONG forward observation framework.

Phase 9.2 created the LONG forward signal journal template.

Phase 9.3 creates a validator for future user-supplied LONG journal rows.

The validator checks that future rows are structurally complete, safe, and compatible with the approved observation framework.

The objective is to prevent unsafe or malformed journal rows from being accepted later.

The objective is not to record real observations yet.

The objective is not to approve paper trading.

The objective is not to approve live alerts.

The objective is not to approve real capital.

The objective is not to automate trading.

## Candidate scope

Primary forward observation candidate:

- LONG_BASE_FAILED_BREAKDOWN_V1

Secondary reference candidate:

- LONG_BASE_LIQUIDITY_SWEEP_V1

Blocked candidates remain excluded from active observation:

- LONG_BASE_FIB_PULLBACK_V1
- LONG_BASE_MTF_BULLISH_CONTINUATION_V1

## Input validator responsibilities

The Phase 9.3 validator checks:

- required journal columns
- valid candidate scope
- LONG direction only
- valid signal states
- valid resolution states
- manual review requirement
- no-execution state
- no-live-alert state
- no-paper-trade state
- no-real-capital state
- valid LONG price structure
- valid risk/reward structure
- blocked candidate rejection
- secondary watchlist rejection for active observation
- missing or dangerous row rejection

## Valid active candidate

Only this candidate can be validated as a future active LONG observation input:

- LONG_BASE_FAILED_BREAKDOWN_V1

## Secondary candidate handling

LONG_BASE_LIQUIDITY_SWEEP_V1 remains reference-only.

It is not accepted as an active forward observation input in Phase 9.3.

## Blocked candidate handling

The following candidates are rejected:

- LONG_BASE_FIB_PULLBACK_V1
- LONG_BASE_MTF_BULLISH_CONTINUATION_V1

## Valid signal states for future validation

Allowed signal states:

- CANDIDATE
- WATCH_ONLY
- INVALIDATED
- CLOSED

Phase 9.3 uses controlled synthetic rows only.

## Valid resolution states

Allowed resolution states:

- UNRESOLVED
- TARGET_HIT
- STOP_HIT
- INVALIDATED
- EXPIRED
- CLOSED_MANUALLY

For future candidate rows, the default should be:

- UNRESOLVED

## Valid LONG price structure

A valid LONG row must satisfy:

stop_price < entry_price < target_price

The expected risk/reward must be positive.

The preferred baseline risk/reward remains 2.5.

## Required safety state

The following must remain false:

- forward_observation_started = False
- signal_generation_enabled = False
- real_forward_signals_recorded = False
- journal_real_rows_accepted = False
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

## Manual review requirement

All future LONG journal rows must require manual review.

Manual review does not approve execution.

Manual review only confirms that a signal is eligible to be recorded as observation evidence in a future phase.

## What Phase 9.3 does not do

Phase 9.3 does not:

- start forward observation
- accept real market observations
- persist real evidence
- generate live signals
- create alerts
- send notifications
- connect to Binance
- connect to Quantfury
- submit paper trades
- submit real trades
- automate entries
- automate exits
- approve LONG execution
- complete the whole project

## Expected result

Expected decision:

PHASE_9_3_LONG_FORWARD_JOURNAL_INPUT_VALIDATOR_VALIDATED

## Recommended next phase

Recommended next step:

Phase 9.4 — LONG Forward Journal Controlled Input Run V1

Phase 9.4 should run a controlled journal input scenario and verify that only safe, validated, manual-review LONG rows can pass structural validation while keeping all execution permissions disabled.