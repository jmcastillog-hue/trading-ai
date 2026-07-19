# Trading-AI — Project Status

## Snapshot

- Baseline commit: `7f5bd2b` — Phase 10.42R merged to `main`.
- Phase 10.42R.2 decision: `PHASE_10_42R_2_CLOSED_CANDLE_MTF_REVALIDATION_COMPLETED`.
- SHORT decision: `REVALIDATED_REJECTED`.
- LONG decision: `CERTIFIED_UNAFFECTED_AND_CONSISTENCY_REVALIDATED`.
- Next phase: `PHASE_10_42R_3_OPENCLAW_READ_ONLY_RESEARCH_STATUS_CONTRACT_V1`.
- Phase 10.43 design review: allowed, but no operational permission is granted.
- Official forward-evidence dataset: not created.
- Total project completed: false.

## Scientific-integrity hold

The earlier MTF enrichment calculated 1H and 4H indicators from complete
candles but timestamped those features at candle open. A backward as-of merge
could therefore expose information before the higher-timeframe candle closed.

Phase 10.42R changes the contract to:

```text
feature_available_at = candle_open_timestamp + timeframe_duration
```

This correction applies to the MTF regime and Directional Context V3/V3.1
paths. All strategy metrics that used those paths require new historical,
out-of-sample, walk-forward, cost-aware and sequence-risk validation.

## Candidate status after 10.42R.2 execution

| Candidate | Current status |
|---|---|
| `TARGET_SHORT_FIB_V5_MTF_V3_1 + FIXED_RR_2_5` | `REVALIDATED_REJECTED` |
| `LONG_BASE_FAILED_BREAKDOWN_V1` | `CERTIFIED_UNAFFECTED_AND_CONSISTENCY_REVALIDATED` / primary research candidate |
| `LONG_BASE_LIQUIDITY_SWEEP_V1` | `CERTIFIED_UNAFFECTED_AND_CONSISTENCY_REVALIDATED` / secondary watchlist |

The SHORT rejection is based on corrected real-data evidence. The legacy
diagnostic returned +71.06% compound OOS performance, whereas the corrected
closed-candle result returned -41.75%, failed all five cost profiles and failed
the deterministic sequence-risk gate. The earlier SHORT edge was therefore an
artifact of higher-timeframe lookahead and is not recoverable.

The primary and secondary LONG candidates do not import the affected MTF
modules. Their complete Phase 8 readiness chain reproduced as a consistency
control. These remain research-only labels, not approved strategies.

## Permissions

The following remain false:

- `forward_observation_allowed`
- `signal_generation_enabled`
- `official_dataset_write_allowed`
- `evidence_persistence_allowed`
- `paper_trade_execution_allowed`
- `real_capital_allowed`
- `live_alerts_allowed`
- `market_execution_allowed`
- `exchange_execution_allowed`
- `automation_allowed`
- `execution_allowed`
- `openclaw_operational_integration_allowed`

## Completed corrective phase

`PHASE_10_42R_2_SHORT_LONG_CLOSED_CANDLE_MTF_REVALIDATION_V1`

The Phase 10.42R.2 harness compares the diagnostic legacy timestamp behavior
against the corrected closed-candle behavior on the same dataset hashes. It
reruns rolling OOS, cost and deterministic sequence-risk gates for the SHORT
candidate.

The audit also established that the primary and secondary LONG candidates use
the independent 15m structural chain. Their Phase 8 readiness chain is rerun as
a consistency control; the rejected MTF LONG candidate remains blocked.

The real-data run completed 72 fixed OOS windows, preserved all nine input
hashes, passed 10/10 integrity and safety controls, produced no errors and
returned exit code 0. It wrote no official forward rows or artifacts.

## Current required phase

`PHASE_10_42R_3_OPENCLAW_READ_ONLY_RESEARCH_STATUS_CONTRACT_V1`

This phase may expose a deterministic, read-only research-status payload to
OpenClaw. It may not produce signals, persist evidence, modify datasets, call
an exchange, authorize forward collection or reinterpret failed gates.
