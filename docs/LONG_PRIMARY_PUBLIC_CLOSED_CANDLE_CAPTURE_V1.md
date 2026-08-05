# LONG Primary Public Closed-Candle Capture V1

## Status

This increment implements a one-shot, foreground-only capture boundary for the
real prospective source required by the primary LONG observation adapter.

It does not run a capture during installation or validation. Validation uses a
mocked HTTP transport and controlled Binance-shaped fixtures only.

## Reused public-data boundary

The implementation reuses the existing Binance public spot endpoint registry
from `src/exchange/binance_historical_downloader.py`. It does not reuse the old
CSV writer because that output omits close time, symbol, timeframe and closed
state, and can include the current open candle.

## Frozen capture contract

A real capture is fixed to:

- provider: Binance public Spot API;
- symbol: `BTCUSDT`;
- timeframe: `15m`;
- request limit: 64 klines;
- exactly one foreground HTTP request;
- no API key, order endpoint or account endpoint;
- no retry loop, scheduler or background process;
- exact authorization token required for each invocation.

The current open candle is excluded using Binance close time versus the local
UTC capture timestamp. At least 49 fully closed, contiguous 15-minute candles
must remain, and the latest close must be no more than 30 minutes old.

## Exact output

The create-only output directory must be outside the repository. It contains:

- `btc_usdt_15m_closed_candles.csv` with the exact ten-column schema required by
  the source adapter;
- `capture_metadata.json` containing capture provenance and all permissions
  fixed to false;
- `manifest.sha256` covering the two payload files.

The output is assembled transactionally in a temporary sibling directory and
published only after validation.

## Separation of responsibilities

This capability stops after source capture. It does not:

- evaluate the failed-breakdown candidate;
- create a human-review package;
- confirm or approve an observation;
- invoke the official evidence writer;
- enable the official append environment gate;
- create signals or actionable alerts;
- submit paper trades or use real capital;
- execute on Binance, Quantfury, a browser or any exchange;
- send messages or invoke OpenClaw;
- run automatically or recurrently.

A later, separately authorized foreground step may feed the captured CSV to
`prepare_real_source_review_package()`. That later step remains pending and
still cannot append official evidence.

## Validation

Validation covers the exact endpoint and request parameters, one-request-only
behavior, open-candle exclusion, minimum warmup, contiguous intervals, OHLC and
time validation, create-only external output, transactional publication,
manifest integrity, official-artifact immutability, and all permissions false.

No real network request or market-data acquisition occurs during validation.
