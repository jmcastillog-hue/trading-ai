# LONG Primary Prospective Observation Source Adapter V1

## Status

This increment implements a non-writing source adapter for the primary LONG
research candidate:

```text
LONG_BASE_FAILED_BREAKDOWN_V1
```

It does not acquire market data, generate actionable alerts, call OpenClaw,
write the official dataset, or authorize execution. Installation and validation
use controlled fixtures in external temporary directories only.

## Purpose

The official 54-column evidence append boundary is already implemented, but the
repository contains no real prospective LONG observation suitable for human
review. Historical, synthetic, report-only and old operational-schema artifacts
must not be promoted into official evidence.

This adapter creates the missing safe boundary:

```text
explicit local closed-candle CSV
        ↓
strict source and provenance validation
        ↓
latest closed BTCUSDT 15m candle only
        ↓
frozen failed-breakdown rule
        ↓
external human-review package
        ↓
manual decision remains pending
```

## Frozen source contract

The source CSV must contain exactly these columns:

```text
open_time_utc,close_time_utc,symbol,timeframe,open,high,low,close,volume,candle_closed
```

The adapter requires:

- valid UTF-8 without BOM;
- at least 49 strictly ordered, fully closed 15-minute candles;
- `BTCUSDT` and `15m` on every row;
- valid positive OHLC values and nonnegative volume;
- the latest candle close at or before the declared capture time;
- no more than 30 minutes between the latest close and capture time;
- the latest close at or after the declared prospective start;
- an optional expected source SHA-256 that must match exactly.

Warmup candles may predate the prospective start. Only the latest fully closed
candle is eligible for evaluation.

## Frozen candidate rule

The latest candle is a primary failed-breakdown candidate only when all three
conditions are true:

1. its low is below the minimum low of the preceding 48 candles;
2. its close reclaims above that preceding 48-candle low;
3. its close is above its open.

No future candle, resolution data or lookahead is used. Entry is the latest
candle close. The structural stop follows the frozen historical baseline rule,
using the latest low and ATR14. Target is fixed at RR `2.5`.

The secondary liquidity-sweep candidate is not evaluated or promoted by this
adapter.

## Human-review package

A create-only package is written outside the repository. It contains:

- the byte-identical source snapshot;
- one canonical candidate row or an empty candidate CSV;
- an adapter-check record;
- a pending human-review packet;
- a SHA-256 manifest covering all package files.

Even when a candidate is detected:

- `manual_confirmed` remains false;
- `review_decision` remains `PENDING`;
- official dataset and evidence persistence permissions remain false;
- signal generation, alerts, paper trading, capital, market/exchange execution,
  automation and general execution remain false.

A sandbox package can never be eligible as real evidence. A real-source package
requires an explicit local authorization and the exact human attestation:

```text
REAL_MARKET_DATA_SOURCE_HUMAN_ATTESTED_NOT_SYNTHETIC
```

That attestation makes the package eligible for review only. It does not approve
the observation or authorize an official append.

## File-system boundary

The source may be local or external, but it cannot be the official dataset or
manifest. The output directory:

- must be outside the repository;
- must not already exist;
- is created transactionally through a temporary sibling directory;
- is validated before publication.

The adapter snapshots and rechecks the official dataset and manifest hashes
before and after package creation. The official append lock must be absent.

## Validation

Validation covers:

- a controlled latest-candle failed-breakdown candidate;
- a controlled no-candidate path;
- latest-candle-only evaluation and no lookahead;
- insufficient warmup;
- future, stale and open-candle rejection;
- invalid OHLC, order, symbol and timeframe rejection;
- source-hash mismatch;
- UTF-8 BOM rejection;
- output-boundary and create-only enforcement;
- exact local authorization;
- exact real-source attestation;
- pending manual confirmation and all permissions false;
- package-manifest tamper rejection;
- absence of any call to the official append writer;
- byte-identical official dataset and manifest.

## Still prohibited

This increment does not authorize:

- market-data download or network access;
- automatic or recurring capture;
- candidate promotion;
- automatic human-review approval;
- the first official evidence append;
- signal generation or actionable alerts;
- paper trading or real capital;
- Binance, Quantfury or browser execution;
- external messaging;
- OpenClaw write access.

## Closure condition

The increment may close when all existing tests and new adapter tests pass,
sandbox validation reports zero failures, the source scope is exact, and the
official dataset and manifest remain unchanged at zero evidence rows.
