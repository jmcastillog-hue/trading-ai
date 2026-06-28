# PHASE 7 LOCAL MARKET CSV READ-ONLY ADAPTER

## Status

Phase 7.2 implements the first safe adapter for the real market input bridge.

This adapter is read-only.

This adapter does not fetch live market data.

This adapter does not generate trade signals.

This adapter does not generate price levels.

This adapter does not approve real entries.

This adapter does not enable paper trading execution.

This adapter does not enable exchange execution.

This adapter only reads a local OHLC CSV file and normalizes it into the operational OHLC input format used by the Phase 6 evidence machine.

## Purpose

Phase 7.1 defined the real market input bridge contract.

Phase 7.2 implements the safest first source class:

```text
LOCAL_MARKET_CSV_READ_ONLY

The goal is to verify that local market data can be normalized and written into:

data/forward_evidence/operational/input/ohlc/
Input schema

The local source CSV must contain at least:

timestamp
open
high
low
close
volume
Output schema

The adapter writes the operational OHLC schema:

timestamp
open
high
low
close
volume
symbol
timeframe
data_source
Safety restrictions

The following must remain false:

paper_trade_execution_allowed = False
real_capital_allowed = False
live_alerts_allowed = False
exchange_execution_allowed = False
automation_allowed = False
execution_allowed = False
Explicit non-goals

Phase 7.2 does not:

fetch Binance data
connect to exchange execution
create orders
open positions
close positions
generate live alerts
generate strategy signals
generate price levels
approve entries
complete the LONG side
Expected validation decision
PHASE_7_2_LOCAL_MARKET_CSV_READ_ONLY_ADAPTER_VALIDATED