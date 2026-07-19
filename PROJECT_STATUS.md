# Trading-AI — Project Status

## Snapshot

- Baseline commit: `40d1c37` — Phase 10.42 merged to `main`.
- Active corrective branch: `phase-10-42r-project-scientific-integrity-and-reproducibility-audit-v1`.
- Current decision: `REVALIDATION_REQUIRED`.
- Phase 10.43: paused.
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

## Candidate status

| Candidate | Current status |
|---|---|
| `TARGET_SHORT_FIB_V5_MTF_V3_1 + FIXED_RR_2_5` | `REVALIDATION_REQUIRED` |
| `LONG_BASE_FAILED_BREAKDOWN_V1` | `REVALIDATION_REQUIRED` |
| `LONG_BASE_LIQUIDITY_SWEEP_V1` | `REVALIDATION_REQUIRED` |

The status change is precautionary. It does not prove that a candidate lacks
edge; it means the previous metrics are not certified under the corrected
closed-candle contract.

## Permissions

The following remain false:

- `forward_observation_allowed`
- `paper_trade_execution_allowed`
- `real_capital_allowed`
- `live_alerts_allowed`
- `exchange_execution_allowed`
- `automation_allowed`
- `execution_allowed`

## Next required phase

`PHASE_10_42R_2_SHORT_LONG_CLOSED_CANDLE_MTF_REVALIDATION_V1`

This next phase must compare prior and corrected results and may promote a
candidate only if it independently survives every required gate. Phase 10.43
may resume only after that decision.
