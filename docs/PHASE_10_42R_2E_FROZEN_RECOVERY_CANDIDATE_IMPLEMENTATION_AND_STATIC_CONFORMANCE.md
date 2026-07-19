# Phase 10.42R.2E — Frozen Recovery Candidate Implementation and Static Conformance

## Scope

Phase 10.42R.2E translates the Phase 2D registry into literal, immutable Python
handlers and verifies them exclusively with deterministic synthetic fixtures.
It is an implementation-conformance phase, not a candidate evaluation.

The source boundary is locked to:

- Phase 2D commit:
  `a9ec58c493a46c9835b2ddb19c301f2957dadaca`;
- Phase 2D specification-module SHA-256:
  `54f71b968c89239b0f4b5e49298be30ddf84c65170be3ce240743d94031f5c4b`;
- Phase 2D golden root:
  `0872b2bf7355e8a9b35d5b4e0e05d3edf291006862ce9ee5eae847910ef4c015`.

The root and manifest are reconstructed in memory before an implementation
object can be built. Any mismatch raises `FrozenSpecificationError`; the
workflow exits non-zero and emits no implementation catalog.
The source hash canonicalizes CRLF and LF to LF before hashing, so the lock is
reproducible on Windows and Linux without weakening content validation.

## Exact implementation registry

The implementation catalog contains the same six variants, parameters, order
and family/variant hashes frozen in Phase 2D:

| Order | Variant | Handler |
|---:|---|---|
| 1 | `RCV_SHORT_UPSIDE_SWEEP_REVERSAL_F01_N48_V01` | `UPSIDE_SWEEP_REVERSAL_HANDLER_V1` |
| 2 | `RCV_SHORT_UPSIDE_SWEEP_REVERSAL_F01_N96_V02` | `UPSIDE_SWEEP_REVERSAL_HANDLER_V1` |
| 3 | `RCV_SHORT_BREAKDOWN_RETEST_F02_N48_V01` | `BREAKDOWN_RETEST_HANDLER_V1` |
| 4 | `RCV_SHORT_BREAKDOWN_RETEST_F02_N96_V02` | `BREAKDOWN_RETEST_HANDLER_V1` |
| 5 | `RCV_SHORT_EMA_PULLBACK_CONTINUATION_F03_S000_V01` | `EMA_PULLBACK_CONTINUATION_HANDLER_V1` |
| 6 | `RCV_SHORT_EMA_PULLBACK_CONTINUATION_F03_S025_V02` | `EMA_PULLBACK_CONTINUATION_HANDLER_V1` |

No variant is evaluated, ranked, selected or promoted. Each catalog row has
`evaluated=False`, `candidate_result_rows=0`, `ranking_allowed=False` and
`selection_allowed=False`.

## Literal rule implementation

### F01 — upside sweep reversal

The handler computes the maximum high of the preceding 48 or 96 complete
synthetic bars, excludes the current bar, and requires:

- `high[t] > prior_high`;
- `close[t] <= prior_high`;
- `close[t] < open[t]`;
- non-zero body;
- upper wick greater than or equal to the frozen body multiple.

The stop is `high[t] + 0.25 × ATR14[t]`.

### F02 — breakdown/retest rejection

The handler searches backward through exactly the prior eight bars for the
most recent qualifying breakdown. Support is the minimum low of the preceding
48 or 96 bars before the candidate breakdown bar `j`. Breakdown is strict:

`close[j] < support[j] - 0.25 × ATR14[j]`.

The retest high boundary is inclusive, while close below support and bearish
close are strict. The stop is
`max(high[t], support[j]) + 0.25 × ATR14[t]`.

### F03 — EMA pullback continuation

EMA20, EMA50 and EMA200 use `adjust=False`, alpha `2/(span+1)` and minimum
periods equal to the span. The rule requires a strict bearish EMA stack,
prior close below prior EMA20, current high at or above EMA20, and bearish
close below EMA20. Separation of zero or 0.25 ATR is inclusive. The stop is
`high[t] + 0.25 × ATR14[t]`.

ATR14 uses true range and Wilder EWM with alpha `1/14`, `adjust=False` and 14
minimum periods.

## Timing and synthetic execution conformance

All input bars must be complete and carry the exact marker
`SYNTHETIC_DETERMINISTIC_PHASE_10_42R_2E_V1`. Late 1H/4H availability,
unknown regimes, open bars or any other source marker block the signal.

The execution contract verifies:

- fill index equals signal index plus one;
- fill price is the next synthetic bar open;
- an existing position blocks an overlapping signal;
- SHORT stop must be strictly above entry; equality fails closed;
- target is `entry - 2.5 × (stop - entry)`;
- entry-bar resolution is allowed;
- simultaneous stop and target resolves stop first;
- a still-open position exits at the 240th entry-relative bar;
- 239 neutral bars remain unresolved.

These objects exist only to prove deterministic control flow. They never
calculate PnL, R, returns, expectancy, profit factor, drawdown or any other
performance statistic.

## Synthetic fixture contract

The full workflow executes 32 fixed conformance cases:

- six positive family cases, one per variant;
- strict/inclusive boundary and negative cases for all three families;
- exact-close, late and unknown MTF cases;
- non-synthetic and open-bar rejection;
- next-open, wrong-fill, gap-equality and overlap cases;
- stop, target and simultaneous stop-first cases;
- 239/240-bar time-exit cases;
- ATR14 and EMA200 minimum-period cases.

Every output row contains only expected and observed conformance codes,
boolean pass/fail state and explicit zero counters for real data, performance,
comparison, ranking and winner rows. No synthetic price is persisted.

## Prohibited inputs and outputs

The implementation module is AST-checked. It contains no filesystem, network,
Pandas, exchange, strategy runtime, backtest, report or holdout loader. Phase
2E reads no real OHLCV, previous result report or sealed dataset. Filesystem
checks on holdout and official paths inspect absence only and never open them.

The following remain exactly zero or false:

- real OHLCV rows read;
- Phase result-report rows read;
- holdout rows read;
- backtest rows;
- performance-metric rows;
- comparison, ranking and candidate-result rows;
- winner selected;
- official evidence rows written;
- every execution, automation and OpenClaw operational permission.

SHORT remains `RETIRED_REVALIDATED_REJECTED_UNCHANGED`; LONG remains
`RESEARCH_ONLY_NOT_APPROVED_UNCHANGED`.

## Reproducible implementation root

The catalog, 32-case conformance table and contract snapshot receive canonical
SHA-256 values. Their ordered manifest binds to the Phase 2D root and source
commit. The golden Phase 2E implementation root is:

`c360cae27f60d7854521a769abb569f730f7e50137076b86abf7d1e4e77e4ef1`

Any implementation, fixture or contract drift changes the root and fails the
full workflow.

## Verification

```powershell
python -m unittest tests.test_frozen_recovery_candidate_static_conformance -v

python -m py_compile `
    src\analysis\frozen_recovery_candidate_implementation_v1.py `
    src\validation\frozen_recovery_candidate_static_conformance_v1.py `
    src\workflows\validate_phase_10_42r_2e_frozen_recovery_candidate_implementation_and_static_conformance.py

python -m src.workflows.validate_phase_10_42r_2e_frozen_recovery_candidate_implementation_and_static_conformance --preflight-only
python -m src.workflows.validate_phase_10_42r_2e_frozen_recovery_candidate_implementation_and_static_conformance
```

Acceptance requires the preflight to pass 12/12 controls and the full workflow
to pass 27/27 with zero blockers and errors. The full suite must also pass.

## Decision boundary

Successful Phase 2E conformance proves only that code matches the frozen
specification on deterministic synthetic fixtures. It is not evidence of
strategy performance and cannot approve a candidate.

The only permitted next step is
`PHASE_10_42R_2F_FROZEN_RECOVERY_CANDIDATE_IMPLEMENTATION_INDEPENDENT_CODE_REVIEW_V1`,
still without real data, backtests, performance metrics, selection, holdouts or
operational permissions.

## Real-run closure and independent review

The real Phase 2E report archive has SHA-256
`fb1009b6bd2b7bebc5acb15a2cdfbec4c195e15de8d85f6fa8266e3a527eb371`.
It contains exactly the ten expected CSV files. An independent in-memory rerun
reproduced every file, all three manifest hashes, the Phase 2D root and the
Phase 2E implementation root.

The source review found no prohibited import, I/O call or data-path literal.
EMA20, EMA50, EMA200 and ATR14 matched their frozen Pandas definitions exactly
on a separate deterministic synthetic series. Family operators, most-recent
breakdown selection, closed MTF timing, next-open fill, gap equality,
overlapping-position blocking, stop-first resolution and 239/240-bar behavior
all conform to Phase 2D.

The run passed 27/27 controls and 32/32 fixtures with zero blockers and zero
errors. It read zero real OHLCV, Phase result-report and holdout rows. It wrote
zero performance, comparison, ranking, candidate-result, winner and official
evidence rows. All permissions remain false and candidate statuses are
unchanged.

Decision:

`PHASE_10_42R_2E_FROZEN_IMPLEMENTATION_STATIC_CONFORMANCE_COMPLETED`

This decision certifies software conformance only. It neither validates
strategy performance nor grants permission to evaluate or operate a candidate.
