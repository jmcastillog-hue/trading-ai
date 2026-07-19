# Trading-AI — Project Status

## Snapshot

- Baseline commit: `e696fa2` — Phase 10.42R.2 merged to `main`.
- Phase 10.42R.2 decision: `PHASE_10_42R_2_CLOSED_CANDLE_MTF_REVALIDATION_COMPLETED`.
- SHORT decision: `REVALIDATED_REJECTED`.
- LONG decision: `CERTIFIED_UNAFFECTED_AND_CONSISTENCY_REVALIDATED`.
- Active phase: `PHASE_10_42R_2A_SIGNAL_TO_FILL_TIMING_INTEGRITY_AUDIT_V1`.
- Phase 10.42R.2A first real run: measurements completed; stage-aware lineage
  correction pending rerun before closure.
- OpenClaw read-only status design and Phase 10.43 remain deferred until the
  signal-to-fill and cost-accounting findings are measured.
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
control. This certification is scoped to the MTF defect. Both historical LONG
candidates confirm their signal using the current 15m candle and record entry
at that same close, so their timing metrics require Phase 10.42R.2A.

## Real-data loss attribution

| Corrected cohort | Trades | Compound return | Average PF |
|---|---:|---:|---:|
| BTCUSDT | 51 | -13.52% | 0.98 |
| ETHUSDT | 69 | -26.00% | 0.70 |
| SOLUSDT | 85 | -8.97% | 1.08 |
| 2023, all symbols | 41 | -2.79% | 0.98 |
| 2024, all symbols | 61 | -7.25% | 1.07 |
| 2025, all symbols | 103 | -35.39% | 0.74 |

The corrected result was worse than the legacy control in 27 of 36 windows,
better in six and equal in three. Ten windows changed return sign. The cohort
breakdown is hypothesis-generating only and cannot authorize symbol or date
selection.

The active SHORT engine already embeds a nominal 0.20% round-trip fee and
0.02% round-trip spread in net `result_r`. The cost-aware layer then subtracts
a complete cost profile from that net value. Phase 10.42R.2A records the
overlap and blocks normalized cost conclusions until the accounting basis is
made explicit. The raw corrected SHORT rejection is unaffected.

The first Phase 10.42R.2A real timing run produced 205 trades in each SHORT
mode. Same-close returned -41.7469% and next-open returned -41.7443%; both
failed walk-forward. The fill repair therefore did not restore the strategy.
All 64 corrected LONG entries occurred after their signals, while all four
historical LONG metric rows remained unchanged because adjacent continuous
candles had equal prior close and next open.

The first harness revision then failed closed on one invalid lineage
comparison: it compared the full Phase 8.4 historical population with Phase
8.10 post-OOS stress-cost readiness inputs. The correction requires two
separate exact reproductions. Audit success means measurement integrity only;
it cannot change any candidate approval.

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

`PHASE_10_42R_2A_SIGNAL_TO_FILL_TIMING_INTEGRITY_AUDIT_V1`

This report-only phase must reproduce the same-close baseline, measure entry at
the next 15m open for SHORT and LONG and audit embedded versus additive costs.
It may not optimize candidates, select a symbol, normalize a cost decision,
produce signals, persist evidence, modify datasets or call an exchange.

Its stage-aware preflight additionally requires the Phase 8.4 historical
metrics and Phase 8.10 Monte Carlo candidate-summary reports. The next phase
may begin only after the corrected audit returns zero blockers.
