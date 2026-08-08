# LONG Supervised 15m Observation Loop V2

## Purpose

V2 replaces repeated manual one-shot observations with a bounded, foreground-only supervised session. It reuses the already validated public BTCUSDT 15m closed-candle capture and the real prospective review-package adapter.

## Development repair limit

The project-level implementation/repair budget for this increment is capped at 10 attempts. Attempt 1 is this implementation. Stop earlier as soon as the defined gates pass. A new repair attempt is allowed only for a concrete reproducible failure; the loop itself does not consume this repair budget.

## Runtime boundary

A real session requires explicit session authorization, the exact real-market-data attestation, an external create-only output directory, and 1-8 observation cycles. It runs in the foreground. Every cycle waits until the next 15-minute boundary plus a five-second grace period, performs one validated public capture, requires a candle newer than the prior prospective observation, prepares one external pending-human-review package, writes an append-only local event, and stops immediately on the first candidate.

The session does not install a scheduler, service, daemon, background process, browser controller, WebSocket listener, messaging integration, or exchange execution path.

## Frozen human contexts

The prior 4h hypothesis remains separate and non-actionable:

- entry 61310.00
- stop 59224.68
- target 68053.13

The revised 15m comparison context is frozen as:

- 38.2 confluence: 63956.34-64019.05
- intermediate: 64358.87
- upper level 1: 65114.87
- upper liquidity cluster: 65644.66-65925.31
- lower cluster: 63310.99-63350.39
- lower level: 62844.75

These values classify location, distance and candle touches only. They cannot alter the frozen LONG candidate rule, infer direction from Fibonacci levels, infer long/short positioning without a microstructure source, or generate an actionable signal.

## Future microstructure layer

Depth, aggressive trade flow, futures open interest, funding, liquidations and heatmap-like evidence remain a separate future research layer. V2 explicitly records that no heatmap or microstructure inference was used.

## Explicit prohibitions

V2 does not send WhatsApp, email, SMS or alerts; access TradingView accounts; control a browser; use Quantfury; confirm a candidate; append official evidence; enable paper trading; use real capital; or execute on an exchange.

## Validation

Validation uses injected deterministic clock/sleep, mock capture and mock package boundaries. It makes no real network request and acquires no real market data. Targeted unit tests cover timing, authorizations, bounded cycles, provenance monotonicity, safety failures, neutral human-context classification, candidate-stop behavior and session integrity.
