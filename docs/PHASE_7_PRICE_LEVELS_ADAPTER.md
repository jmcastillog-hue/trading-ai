# PHASE 7 PRICE LEVELS ADAPTER

## Status

Phase 7.6 implements a manual reviewed price levels adapter.

This phase creates the third operational input family required by the Phase 6 evidence machine:

```text
price_levels

This phase does not fetch live market data.

This phase does not generate signals.

This phase does not execute trades.

This phase does not approve paper trading execution.

This phase does not approve real capital execution.

This phase does not enable live alerts.

This phase does not enable exchange execution.

Purpose

Phase 7.2 validated local OHLC input.

Phase 7.4 validated manual reviewed signal input.

Phase 7.5 validated that signal plus OHLC remains incomplete when price levels are absent.

Phase 7.6 adds the missing price level input family:

entry_price
stop_price
target_price

The goal is to normalize manually reviewed price levels into the operational price level input format used by the evidence pipeline.

Required complete evidence input

A complete operational evidence input requires:

signals
ohlc
price_levels

Phase 7.6 only validates the price level component.

Full bridge compatibility is intentionally deferred to Phase 7.7.

Input schema

The local source price levels CSV must contain at least:

signal_id
context_name
cost_profile
direction
entry_price
stop_price
target_price
price_level_source
notes
Output schema

The adapter writes the operational price level schema:

signal_id
context_name
cost_profile
direction
entry_price
stop_price
target_price
price_level_source
notes
Safety rules

Every generated price level row must satisfy:

execution_allowed = False
paper_trade_execution_allowed = False
real_capital_allowed = False
live_alerts_allowed = False
exchange_execution_allowed = False
automation_allowed = False
SHORT structure rule

For SHORT price levels:

stop_price > entry_price > target_price
LONG structure rule

For future LONG price levels:

stop_price < entry_price < target_price
Directional scope

The controlled fixture in Phase 7.6 uses SHORT because the current official research candidate is SHORT-based.

The adapter remains direction-aware and can validate future LONG rows.

This phase does not establish the LONG side.

LONG-side strategy remains future work.

Explicit non-goals

Phase 7.6 does not:

fetch Binance data
connect to exchange execution
create orders
open positions
close positions
generate live alerts
generate signals
generate OHLC
generate complete evidence
approve entries
complete the LONG side
Expected validation decision

PHASE_7_6_PRICE_LEVELS_ADAPTER_VALIDATED