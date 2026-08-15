# Public Read-Only Microstructure Snapshot V1.1 — Depth 1000

## Purpose

Refine the already validated V1 public/read-only BTCUSDT USDⓈ-M Futures microstructure snapshot by increasing only the order-book REST depth request from 100 to 1000 levels per side. V1 remains preserved and immutable as the closed baseline.

This component remains research-only and context-only. It does **not** modify `LONG_BASE_FAILED_BREAKDOWN_V1`, create LONG/SHORT signals, authorize alerts, paper trading, real-capital trading, exchange actions, browser actions, or official evidence appends.

## Empirical reason for V1.1

The first certified real V1 snapshot returned 100 bid levels and 100 ask levels, but those levels reached only about 1.67 bps from the mid price on each side. Therefore the 5/10/25/50 bps bands were all correctly marked `coverage_complete=false`.

V1.1 addresses exactly that reproducible limitation. It does not reinterpret the prior snapshot and it does not assume that 1000 levels will always cover 50 bps. Coverage remains an explicit measured property.

## Public data contract

Provider: Binance USDⓈ-M Futures public REST (`https://fapi.binance.com`).

Exactly seven sequential GET requests remain allowed per real snapshot:

1. `/fapi/v1/klines` — latest fully closed BTCUSDT 15m futures candle.
2. `/fapi/v1/depth` — visible resting order-book depth, **limit 1000**.
3. `/fapi/v1/openInterest` — current open interest.
4. `/fapi/v1/premiumIndex` — mark price, index price, latest funding and next funding time.
5. `/futures/data/openInterestHist` — two 15m open-interest observations aligned to the reference boundary.
6. `/futures/data/takerlongshortRatio` — two 15m taker buy/sell-volume observations.
7. `/futures/data/globalLongShortAccountRatio` — two 15m global account-ratio observations.

The V1.1 authorization contract is repaired after a supervised review identified that the original V1.1 implementation incorrectly reused the already-consumed V1 token. A future real V1.1 snapshot now requires the exact fresh, version-specific authorization `CAPTURE_ONE_SHOT_BINANCE_USDM_PUBLIC_MICROSTRUCTURE_V1_1`. The legacy token `CAPTURE_ONE_SHOT_BINANCE_USDM_PUBLIC_MICROSTRUCTURE_V1` is explicitly rejected by the V1.1 capture entry point. The previously preserved real V1.1 artifact captured under the legacy token remains an incident/research artifact and is not retrospectively promoted to formally authorized V1.1 evidence. No automatic recapture is authorized by this repair.

No API key, signature, account endpoint, order endpoint, websocket, retry loop, scheduler, background process, or authenticated endpoint is permitted.

`SYNCHRONIZED_15M_OBSERVATION_V1_1` was published before this authorization repair and still delegates the legacy V1 microstructure token. Therefore a new real synchronized V1.1 session must remain prohibited until a separate additive downstream authorization-propagation repair is implemented and validated. This repair intentionally does not mutate the already closed Synchronized Observation V1.1 implementation.

## Depth coverage contract

The analysis bands remain frozen at 5/10/25/50 bps from the computed mid price.

For every band the snapshot records:
- bid/ask level count;
- bid/ask base quantity;
- bid/ask visible notional;
- notional imbalance;
- `coverage_complete`.

`coverage_complete=true` is allowed only when the furthest returned bid and ask both reach at least the requested band. A request for 1000 levels is **not** equivalent to proof of full 50 bps coverage.

Visible order-book depth is resting displayed liquidity only. It is not a map of hidden stops, liquidations, iceberg liquidity, future cancellations, or trader intent.

## V1.1 validation objective

The next real one-shot validation snapshot should answer a narrow question:

> Does a 1000-level public REST snapshot provide sufficient real BTCUSDT depth to make the 5/10/25/50 bps coverage flags materially more useful?

If any band remains incomplete, the result is preserved as evidence; V1.1 must not fabricate or extrapolate missing depth.

## Approved project continuation after V1.1

The following architecture is approved but **not implemented by this refinement**:

1. `Synchronized Observation V1`: closed 15m OHLCV + frozen primary rule + one-shot microstructure context.
2. `Forward Outcome Labeler V1`: returns plus MFE/MAE and target/stop ordering at 1/2/4/8/16-bar horizons.
3. `Context Feature Pack V1 — Level A Standard`:
   - deterministic cycle context;
   - `EXTERNAL_CYCLE_REGRESSION_BASELINE_V1` as a falsifiable uncertainty-aware baseline, never a point forecast;
   - `Event Risk Calendar V1` with direction unknown before events;
   - `PLAN_BTC_LIQUIDITY_SWEEP_BEFORE_EXPANSION_RESEARCH_V1` as a formally tested hypothesis, not a claimed 95% rule;
   - Analog Engine using leave-one-cycle-out and block bootstrap;
   - `EXTERNAL_THESIS_MODEL_CARD_V1` for every external hypothesis.
4. `Context Evaluation Engine V1`: baseline, ablation, OOS/walk-forward, costs, block bootstrap, Monte Carlo, multiplicity and incremental-value tests.
5. `Context Quality Gate`: only if robust improvement is demonstrated.
6. Level B on-chain/ETF/miner features later, integrated into the same Level A contract. Level B cannot replace Level A or become required for the base system.

Plan BTC point dates, point prices, uncalibrated probabilities and directional forecasts are not adopted.

## Official documentation consulted

Binance Developer Docs, USDⓈ-M Futures REST/API reference, reviewed 2026-08-09:
- official developer catalog: `https://developers.binance.com/en/docs/catalog`
- USDⓈ-M Futures REST product reference;
- `/fapi/v1/depth` public market-data endpoint.

The implementation remains limited to the exact endpoint allowlist already validated in V1.
