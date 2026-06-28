# PHASE 7 MANUAL REVIEWED SIGNAL EXPORT ADAPTER

## Status

Phase 7.4 implements a manual reviewed signal export adapter.

This adapter is read-only from the perspective of strategy execution.

This adapter does not fetch live market data.

This adapter does not create exchange orders.

This adapter does not generate price levels.

This adapter does not approve real entries.

This adapter does not enable paper trading execution.

This adapter does not enable live alerts.

This adapter only normalizes manually reviewed watch-only signal exports into the operational signal input format used by the Phase 6 evidence machine.

## Purpose

Phase 7.1 defined the real market input bridge contract.

Phase 7.2 implemented the local OHLC read-only adapter.

Phase 7.3 validated that OHLC alone is incomplete and must not generate evidence.

Phase 7.4 adds the second required input family:

```text
signals

The signal output must remain watch-only and manually reviewed.

Input schema

The local source signal CSV must contain at least:

observed_at
symbol
timeframe
signal_type
router_decision
cost_profile
context_name
direction
manual_review_required
notes
Output schema

The adapter writes the operational signal schema:

observed_at
symbol
timeframe
signal_type
router_decision
cost_profile
context_name
direction
manual_review_required
notes
Safety rules

Every generated signal must satisfy:

manual_review_required = True
router_decision = WATCH_ONLY
execution_allowed = False
Directional scope

The controlled fixture in Phase 7.4 uses SHORT because the current official research candidate is SHORT-based.

However, the adapter schema must remain direction-aware and allow future LONG-side validation.

LONG-side strategy remains future work and must not be marked complete in this phase.

Explicit non-goals

Phase 7.4 does not:

fetch Binance data
connect to exchange execution
create orders
open positions
close positions
generate live alerts
generate price levels
approve entries
complete the LONG side
generate full evidence alone
Required complete evidence input

A complete operational evidence input still requires:

signals
ohlc
price_levels

Phase 7.4 only creates the signal component.

Expected validation decision
PHASE_7_4_MANUAL_REVIEWED_SIGNAL_EXPORT_ADAPTER_VALIDATED