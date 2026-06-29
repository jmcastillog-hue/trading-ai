# PHASE 8 LONG-SIDE VALIDATION CONTRACT

## Status

Phase 8.1 defines the LONG-side validation contract.

This phase does not create an approved LONG strategy.

This phase does not approve LONG entries.

This phase does not approve paper trading execution.

This phase does not approve real capital execution.

This phase does not approve Binance execution.

This phase does not approve Quantfury execution.

This phase does not approve live alerts.

This phase does not approve automation.

## Purpose

Phase 7 closed the controlled real market input bridge.

The system can now process structured local bridge inputs into controlled forward evidence.

However, the project is not structurally complete because the LONG side remains unvalidated.

Phase 8 begins the LONG-side validation framework.

The first step is to define the contract that any future LONG candidate must satisfy.

## Important distinction

A LONG strategy must not be treated as a simple mirror copy of the SHORT candidate.

SHORT and LONG behavior can differ because market structure, liquidity behavior, liquidation cascades, pullbacks, trend continuation, funding, volatility expansion, and BTC cycle context can affect each side differently.

Therefore, the LONG side requires its own validation path.

## Current official SHORT candidate

The current official first research strategy candidate remains:

- TARGET_SHORT_FIB_V5_MTF_V3_1 + FIXED_RR_2_5

This candidate is SHORT-based.

It remains research/evidence-only.

It is not approved for execution.

## LONG-side contract scope

The LONG-side validation contract defines:

- required input fields
- required price structure
- required context filters
- required evidence gates
- minimum reporting outputs
- safety restrictions
- non-approval rules

## Required LONG price structure

Any valid LONG price level structure must satisfy:

- stop_price < entry_price < target_price

Invalid LONG structures must be rejected.

## Required LONG input families

Future LONG validation must use the same operational input families already validated in Phase 7:

- signals
- ohlc
- price_levels

## Required LONG signal fields

A future LONG signal must include:

- observed_at
- symbol
- timeframe
- signal_type
- router_decision
- cost_profile
- context_name
- direction
- manual_review_required
- notes

Required direction:

- LONG

Required router state during validation:

- WATCH_ONLY

## Required LONG price level fields

A future LONG price level input must include:

- signal_id
- context_name
- cost_profile
- direction
- entry_price
- stop_price
- target_price
- price_level_source
- notes

Required direction:

- LONG

Required price structure:

- stop_price < entry_price < target_price

## Required LONG evidence behavior

A future LONG candidate must be evaluated through evidence before any trading approval.

Required evidence checks include:

- generated_observations
- rejected_observations
- error_observations
- closed_observations
- open_observations
- wins
- losses
- result_r
- mfe_r
- mae_r
- bars_to_resolution
- dataset persistence
- duplicate protection
- backup creation
- snapshot creation

## Required LONG research gates

A future LONG candidate must pass:

- in-sample validation
- out-of-sample validation
- walk-forward validation
- cost-aware validation
- Monte Carlo validation
- position sizing validation
- context risk routing validation
- readiness gate validation
- forward observation validation
- evidence dataset validation

## Required LONG context considerations

Future LONG candidates must consider:

- bullish trend continuation
- bearish trend reversal risk
- liquidity sweeps below price
- failed breakdowns
- Fibonacci pullback zones
- volatility expansion
- BTC cycle context
- higher timeframe regime
- MTF alignment
- liquidation risk
- cost and spread impact

## Non-goals of Phase 8.1

Phase 8.1 does not:

- generate a LONG strategy
- optimize LONG parameters
- approve LONG entries
- create Binance orders
- create Quantfury orders
- execute trades
- enable live alerts
- run paper trading
- deploy automation
- approve real capital

## Safety state

The following must remain false:

- paper_trade_execution_allowed = False
- real_capital_allowed = False
- live_alerts_allowed = False
- exchange_execution_allowed = False
- automation_allowed = False
- execution_allowed = False
- long_side_established = False
- real_entries_approved = False
- total_project_completed = False

## Phase 8.1 validation decision

Expected decision:

PHASE_8_1_LONG_SIDE_VALIDATION_CONTRACT_DEFINED

## Recommended next phase

Recommended next step:

Phase 8.2 — LONG Candidate Discovery Baseline V1

Phase 8.2 should discover and test baseline LONG candidates without approving execution.