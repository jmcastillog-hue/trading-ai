# Synchronized 15m Observation V1

## Purpose

`SYNCHRONIZED_15M_OBSERVATION_V1` extends the already closed bounded supervised 15m observation workflow by attaching the closed-candle Spot primary-rule observation to one public/read-only Binance USDⓈ-M Futures microstructure snapshot for the same 15-minute boundary.

The primary LONG rule remains frozen and continues to be evaluated only through the existing Spot source adapter. Microstructure is context only. It cannot create, cancel, modify, confirm, or override the primary candidate.

This phase does not implement Forward Outcome Labeler V1, Level A context features, notifications, paper trading, real-capital trading, browser actions, exchange execution, or official evidence append.

## Frozen per-cycle data flow

Each completed cycle contains exactly:

1. one Binance public Spot BTCUSDT 15m closed-candle capture (`1` GET);
2. one existing primary-rule human-review package built from that Spot source (`0` network requests);
3. one Binance USDⓈ-M Futures public/read-only Microstructure V1.1 snapshot (`7` GETs);
4. one strict synchronization check;
5. one external create-only synchronized session record.

Therefore a successful completed cycle has exactly `8` delegated public market-data GET requests.

No direct HTTP client is implemented in this orchestrator. Network access remains delegated to the already reviewed capture boundaries.

## Synchronization gate

The following must be equal after UTC normalization:

`spot_latest_closed_candle_utc == futures_reference_closed_candle_utc`

If the timestamps differ, the session fails closed with `SPOT_FUTURES_CANDLE_MISMATCH`.

Spot and Futures prices are not required to be equal. They are different market sources. Only the closed 15m boundary must match.

This gate also protects against a capture sequence crossing into a newer 15m boundary while a cycle is in progress.

## Primary rule isolation

The primary source remains:

- provider: Binance public Spot API;
- symbol: BTCUSDT;
- timeframe: 15m;
- detector: existing `LONG_BASE_FAILED_BREAKDOWN_V1`;
- evaluation path: existing `LONG_PRIMARY_PROSPECTIVE_OBSERVATION_SOURCE_ADAPTER_V1`.

Microstructure V1.1 may be recorded beside the primary evaluation but:

- `microstructure_can_create_candidate=false`;
- `microstructure_can_cancel_candidate=false`;
- `microstructure_can_modify_primary_rule=false`;
- `actionable_signal_generated=false`.

The session stops on the first **primary** candidate only, preserving manual human review.

## Microstructure contract

Microstructure uses the already closed:

`PUBLIC_READ_ONLY_MICROSTRUCTURE_SNAPSHOT_V1_1`

with:

- Binance USDⓈ-M Futures public REST;
- BTCUSDT;
- 15m;
- depth request limit `1000`;
- frozen depth bands `5/10/25/50 bps`;
- seven sequential public GET requests;
- no API key;
- no authenticated endpoints;
- no websocket;
- no retry loop;
- no scheduler/background process.

The first real V1.1 validation showed complete depth coverage for 5 and 10 bps and incomplete coverage for 25 and 50 bps in that sample. Synchronized Observation V1 therefore freezes the following semantics rather than assuming future coverage.

### Depth feature usability

For every band:

`usable_for_context = coverage_complete`

If `coverage_complete=false`:

- observed returned depth is preserved;
- `notional_imbalance_observed` is retained as provenance/context;
- `notional_imbalance_usable=null`;
- the missing part of the requested band is never extrapolated.

The minimum depth-context quality flag requires both frozen near-touch bands:

`required_depth_bands_bps = [5, 10]`

`minimum_depth_context_usable = coverage_complete(5) AND coverage_complete(10)`

The 25 and 50 bps bands remain optional. Incomplete optional bands do not invalidate the whole synchronized observation because OI, funding, basis, taker flow, account ratio, spread and any complete depth bands remain separately observable. They simply cannot be treated as complete-band features.

## Bounded foreground session

The session remains:

- foreground only;
- maximum 8 cycles;
- one cycle after each 15m boundary plus 5-second grace;
- stop on first primary candidate pending human review;
- no recurring scheduler;
- no thread/process/background execution;
- no external notifications;
- no automatic trading action.

Each completed cycle stores external evidence under separate directories for:

- `spot_captures/`;
- `reviews/`;
- `microstructure/`.

The session itself adds:

- `session_events.jsonl`;
- `session_summary.json`;
- `manifest.sha256`.

The session manifest covers only the two session-level payloads; the delegated Spot, review-package and microstructure artifacts retain their own existing manifests/provenance.

## Fail-closed behavior

A session aborts if any of the following occurs:

- wrong session authorization;
- wrong source attestation;
- official append gate enabled;
- stale/duplicate Spot candle;
- Spot capture contract violation;
- primary review-package provenance mismatch;
- Microstructure V1.1 request/depth/permission contract violation;
- Microstructure V1.1 validator failure;
- Spot/Futures closed-candle mismatch;
- official dataset or official manifest mutation.

When a failure happens after some delegated calls, the abort event records only the request count confirmed from successfully returned delegated results. It does not pretend to know how many network requests an interrupted delegated capture may have issued internally.

## Official evidence and permissions

The following remain false:

- official dataset write allowed;
- official append allowed;
- evidence persistence to official dataset allowed;
- signal generation;
- live alerts;
- paper trading;
- real capital;
- market/exchange execution;
- automation/execution.

The official dataset and official manifest must remain byte-identical before and after a successful session.

## Approved continuation

After Synchronized Observation V1 is implemented, sandbox validated, intentionally committed/published, and then real-validated under a separately authorized bounded session, the planned next component is:

`FORWARD_OUTCOME_LABELER_V1`

It will provide forward returns, MFE/MAE and target/stop ordering at the approved 1/2/4/8/16-bar horizons.

Only after forward outcomes exist should `Context Feature Pack V1 — Level A Standard` be implemented/evaluated, including:

- deterministic cycle context;
- `EXTERNAL_CYCLE_REGRESSION_BASELINE_V1`;
- `Event Risk Calendar V1`;
- `PLAN_BTC_LIQUIDITY_SWEEP_BEFORE_EXPANSION_RESEARCH_V1`;
- Analog Engine;
- `EXTERNAL_THESIS_MODEL_CARD_V1`.

Level B on-chain/ETF/miner context remains a future extension integrated into the same Level A contract and cannot replace Level A.
