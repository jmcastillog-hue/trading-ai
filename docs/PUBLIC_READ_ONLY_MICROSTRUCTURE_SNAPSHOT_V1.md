# Public Read-Only Microstructure Snapshot V1

## Purpose

Create one bounded, foreground, public, read-only BTCUSDT USDⓈ-M Futures microstructure snapshot for research context. This component does **not** alter the frozen LONG candidate rule and cannot create signals, alerts, paper trades, real-capital trades, exchange actions, browser actions, or official evidence appends.

## Public data contract

Provider: Binance USDⓈ-M Futures public REST (`https://fapi.binance.com`).

Exactly seven sequential GET requests are allowed per real snapshot:

1. `/fapi/v1/klines` — establish the latest fully closed BTCUSDT 15m futures candle.
2. `/fapi/v1/depth` — visible resting order-book depth, limit 100.
3. `/fapi/v1/openInterest` — current open interest.
4. `/fapi/v1/premiumIndex` — mark price, index price, latest funding rate and next funding time.
5. `/futures/data/openInterestHist` — two 15m open-interest observations aligned to the reference boundary.
6. `/futures/data/takerlongshortRatio` — two 15m taker buy/sell-volume observations.
7. `/futures/data/globalLongShortAccountRatio` — two 15m global account-ratio observations.

No API key, signature, account endpoint, order endpoint, websocket, retry loop, scheduler, background process, or authenticated endpoint is permitted.

## Why top-trader ratios are excluded

The current Binance USDⓈ-M Futures documentation requires an `X-MBX-APIKEY` header for the top-trader account and position ratio endpoints. V1 deliberately excludes those endpoints so the boundary remains genuinely public and credential-free.

## Metrics

The normalized snapshot records:

- futures reference candle and capture timestamps;
- best bid, best ask, mid price, absolute spread and spread in basis points;
- returned visible depth and notional imbalance inside 5/10/25/50 bps bands;
- coverage flags so incomplete returned depth is not mistaken for complete market depth;
- strongest returned bid and ask levels by visible notional;
- current open interest plus approximate value at mark price;
- 15m change in open interest and open-interest value;
- mark/index basis and latest funding rate;
- 15m taker buy/sell volumes and ratio;
- 15m global long/short account ratio.

## Interpretation restrictions

Visible book depth is not a liquidation map and does not reveal hidden stops. Open interest does not identify which side initiated or will be liquidated. Funding, taker ratios and account ratios are descriptive variables, not trade directions. The point-in-time order book/current OI/mark-price components are captured just after the reference candle and are **not** historical reconstructions of the exact close.

No heatmap or liquidation stream is used in V1.

## Output

The create-only external package contains:

- `microstructure_snapshot.json`
- `raw_responses.json`
- `request_log.json`
- `manifest.sha256`

The repository and official LONG evidence artifacts must remain unchanged.

## Official documentation consulted

Binance Developer Docs, USDⓈ-M Futures Market Data, reviewed 2026-08-08:

- `https://developers.binance.info/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/market-data`
- Order book: `/fapi/v1/depth`
- Open interest: `/fapi/v1/openInterest`
- Open-interest statistics: `/futures/data/openInterestHist`
- Mark price and funding: `/fapi/v1/premiumIndex`
- Taker buy/sell volume: `/futures/data/takerlongshortRatio`
- Global long/short account ratio: `/futures/data/globalLongShortAccountRatio`
