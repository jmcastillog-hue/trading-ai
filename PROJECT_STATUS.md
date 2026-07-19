# Trading-AI — Project Status

## Snapshot

- Phase 10.42R.2D source baseline: `abb2a4b` — completed Phase 10.42R.2C.
- Phase 10.42R.2 decision: `PHASE_10_42R_2_CLOSED_CANDLE_MTF_REVALIDATION_COMPLETED`.
- SHORT decision: `REVALIDATED_REJECTED`.
- LONG decision: `CERTIFIED_UNAFFECTED_AND_CONSISTENCY_REVALIDATED`.
- Phase 10.42R.2A decision:
  `PHASE_10_42R_2A_SIGNAL_TO_FILL_TIMING_AUDIT_COMPLETED`.
- Phase 10.42R.2B decision:
  `PHASE_10_42R_2B_COST_NORMALIZATION_AND_RECOVERY_PREREGISTRATION_COMPLETED`.
- Phase 10.42R.2C decision:
  `PHASE_10_42R_2C_PREREGISTERED_DEVELOPMENT_DIAGNOSTIC_COMPLETED`.
- Phase 10.42R.2D decision:
  `PHASE_10_42R_2D_RECOVERY_CANDIDATE_SPECIFICATION_AND_MULTIPLICITY_FREEZE_COMPLETED`.
- Phase 10.42R.2E decision:
  `PHASE_10_42R_2E_FROZEN_IMPLEMENTATION_STATIC_CONFORMANCE_COMPLETED`.
- Active phase:
  `PHASE_10_42R_2F_FROZEN_RECOVERY_CANDIDATE_IMPLEMENTATION_INDEPENDENT_CODE_REVIEW_V1`.
- OpenClaw read-only status design and Phase 10.43 remain deferred during the
  frozen candidate implementation and static/synthetic conformance phase.
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

`PHASE_10_42R_2A_SIGNAL_TO_FILL_TIMING_INTEGRITY_AUDIT_V1` also completed.
Its final run passed 17/17 tests and 16/16 controls with zero blockers. SHORT
remained rejected, LONG historical metrics remained unchanged but unapproved,
and the cost-overlap finding remained open for normalization.

## Completed Phase 10.42R.2C

`PHASE_10_42R_2C_PREREGISTERED_STRATEGY_RECOVERY_DEVELOPMENT_DIAGNOSTIC_V1`

This report-only phase consumed the locked Phase 2B normalization output. It
explained the rejected SHORT reference across exactly five preregistered
dimensions and all five fixed cost profiles; it did not repair, rank, optimize,
select, reclassify or execute a candidate.

There was no download mode. The run hash-matched all nine known 2022–2025 OHLCV
inputs, kept both holdouts sealed and preserved SHORT as rejected and LONG as
research-only/not approved.

The Phase 2B V2 real report reconciled all 1,025 normalized rows and confirmed
that normalized Binance base performance remained negative. A post-run
artifact audit corrected aggregate max drawdown to realized-time order and
included the zero-trade BTC window in the 36-unit symbol/window universe. The
final V2 run passed 16/16 controls with zero blockers and preserved the exact
205 × 5 source/profile grid.

Phase 2C published only descriptive diagnostics over known 2022–2025 evidence.
It preserved all three symbols, all five cost profiles and all five
preregistered dimensions. It did not rank cohorts, tune parameters, modify the
retired SHORT, specify a winning candidate, open either holdout, write an
official forward row or enable OpenClaw operations. It recommended only a
separate Phase 2D family/specification freeze before any candidate evaluation.

The real Phase 2C report archive has SHA-256
`27d6ccb4e77c2453837df5db48fdea09ce3f6f4733bf00e9c5dd2d22da03bb63`.
It passed 26/26 controls with zero blockers and zero errors. The exact 205
source trades, 1,025 normalized rows, five dimensions and 60 metric rows were
reconciled independently against the Phase 2B and Phase 10.42R.2 archives.

One preregistered trend slice was positive under Binance base costs, but it
contained only 72 aggregate trades and 15 BTCUSDT trades and turned slightly
negative under Binance stress. It therefore fails the locked minimum-evidence
and stress-stability gates and is not an approved recovery candidate.

## Completed Phase 10.42R.2D and current required phase

`PHASE_10_42R_2D_RECOVERY_CANDIDATE_FAMILY_SPECIFICATION_AND_MULTIPLICITY_FREEZE_V1`

Phase 2D is specification-only. Before evaluating any candidate, it must freeze
at most three candidate families and four variants per family, their exact
deterministic rules, timing, parameters, cost profiles, fixed three-symbol
cohort, family/variant identifiers, multiplicity treatment, evaluation order,
minimum evidence, promotion gates and a reproducible specification hash.

Phase 2D may use Phase 2C solely to generate hypotheses. It cannot calculate a
winning result, retrospectively select a favorable slice, open or create either
holdout, write forward evidence, produce signals, approve LONG or SHORT, or
enable any execution, automation or OpenClaw operational permission.

The completed freeze contains exactly three newly identified families and two
variants each: upside-sweep reversal (48/96 bars), breakdown/retest rejection
(48/96 bars) and EMA pullback continuation (0/0.25 ATR separation). All share
the full BTCUSDT/ETHUSDT/SOLUSDT cohort, corrected closed-candle context,
next-open fill and all five fixed cost profiles. None imports or mutates the
retired SHORT.

All six variants enter a single Holm-Bonferroni pool in declared order. Future
promotion gates require at least 100 aggregate OOS trades, 20 in each symbol,
positive base edge and per-symbol stability, non-negative yearly and stress
edge, and all other frozen integrity gates. Phase 2D produces zero evaluation
rows and cannot declare a winner.

After a 28/28, zero-blocker, reproducible specification freeze, the only
allowed next phase is
`PHASE_10_42R_2E_FROZEN_RECOVERY_CANDIDATE_IMPLEMENTATION_AND_STATIC_CONFORMANCE_V1`.
That phase remains implementation/synthetic-conformance only; holdout,
comparative backtest and every operational permission remain prohibited.

The independently reviewed real Phase 2D report archive has SHA-256
`7eaa94579fbb2ad000db675c4f3fb13a276a6403b0b484c06d7e16784e7189d8`.
It contains exactly 15 expected CSV files, passes 28/28 controls with zero
blockers and zero errors, reproduces all eight frozen artifact tables and the
golden root SHA-256
`0872b2bf7355e8a9b35d5b4e0e05d3edf291006862ce9ee5eae847910ef4c015`.
All six variants remain unevaluated with zero result rows and no winner.

## Current Phase 10.42R.2E contract

Phase 2E implements the exact three-family/six-variant registry only after the
Phase 2D golden root reproduces. The implementation is bound to commit
`a9ec58c`, the exact Phase 2D specification-module hash and root
`0872b2bf7355e8a9b35d5b4e0e05d3edf291006862ce9ee5eae847910ef4c015`.

All rule and execution checks use 32 deterministic fixtures carrying an
explicit synthetic-only marker. They cover positive, negative and equality
boundaries, closed MTF availability, next-open fill, invalid gaps, overlap,
stop/target resolution and the 240-bar time exit.

The implementation module contains no filesystem, network, data-frame,
backtest, result-report or holdout loader. Phase 2E must read zero real OHLCV,
zero result rows and zero sealed rows. It must emit no performance metric,
comparison, ranking, candidate result or winner.

Its expected implementation root is
`c360cae27f60d7854521a769abb569f730f7e50137076b86abf7d1e4e77e4ef1`.
Passing conformance cannot approve SHORT or LONG and cannot enable any
execution, automation or OpenClaw operational permission.

The independently reviewed real Phase 2E report archive has SHA-256
`fb1009b6bd2b7bebc5acb15a2cdfbec4c195e15de8d85f6fa8266e3a527eb371`.
Its ten-file inventory and every CSV reproduce exactly from the source code.
All 27 controls and 32 synthetic fixtures pass with zero blockers and errors;
all manifest hashes and both golden roots are exact.

Independent numerical review also reproduced ATR14 and EMA20/50/200 exactly
against their Pandas EWM definitions on a separate synthetic series. The
implementation reads zero real, result-report or holdout rows and emits zero
performance, comparison, ranking, candidate-result and winner rows. Phase 2E
is closed as software conformance only.

Phase 2F remains a source-only independent review. It cannot introduce real
data, backtests, performance metrics, selection, holdout access or any
operational permission without a separate scientific authorization phase.
