# Phase 10.42R.2F — Frozen recovery candidate implementation independent code review

## Decision

`CONFIRMED_DEFECTS_CORRECTED_SOURCE_ONLY_PENDING_LOCAL_APPLICATION`

The authoritative baseline is Phase 2E commit
`7d7f8ee81156b1858a636b586eb5636b34b1c801`. The Phase 2D root remains
`0872b2bf7355e8a9b35d5b4e0e05d3edf291006862ce9ee5eae847910ef4c015`.
The Phase 2E implementation remains present and unchanged as `v1`; this package
adds a corrected `v2` and does not rewrite the prior audit evidence.

This review used source code and deterministic synthetic objects only. It did
not read real OHLCV, historical result reports, forward datasets or holdouts;
it did not run a backtest or produce performance, comparison, ranking,
selection or winner output.

## Confirmed findings

| ID | Severity | File and symbol | Minimal reproducible case | Baseline observation | Contract requirement | Correction |
|---|---|---|---|---|---|---|
| `2F-CF-001` | High | `src/analysis/frozen_recovery_candidate_implementation_v1.py::_evaluate_upside_sweep` | `prior_high=100`, `high_t=101`, `close_t=100` | `SIGNAL` | Phase 2D says `CLOSE_T_LESS_THAN_PRIOR_HIGH`; equality must block | `v2` uses strict `<`; result is `UPSIDE_SWEEP_RULE_BLOCKED` |
| `2F-CF-002` | High | `construct_next_open_short_order` and `resolve_short_exit` | `signal.stop_price=NaN`; accepted order with `stop_price=NaN` | order accepted; exit remained open | Non-finite state must fail closed | `INVALID_SIGNAL_STOP` and `INVALID_ACCEPTED_ORDER` |
| `2F-CF-003` | High | `evaluate_frozen_signal` | Replace canonical F01 `parameter_json` with `lookback=1` while retaining the golden root | altered implementation generated `SIGNAL` | Runtime identity must equal the frozen registry, not only its root string | exact dataclass identity is checked against the six reconstructed canonical implementations; mismatch raises `FrozenSpecificationError` |
| `2F-CF-004` | Medium | `mtf_context_is_closed_and_allowed` | `signal_close_unit=+Infinity` with finite availability units | `SIGNAL` | MTF availability indices must be valid integer closed-candle units | result is `MTF_CONTEXT_BLOCKED` |
| `2F-CF-005` | Medium | `construct_next_open_short_order` | `signal_bar_index=10.5`, `fill_bar_index=11.5` | `ORDER_ACCEPTED` | Bar indices must be integers and fill must be exactly `t+1` | result is `INVALID_BAR_INDEX` |

No other defect was classified without a reproducer. F02 most-recent breakdown
search, F03 EMA conditions, Wilder ATR14, EMA `adjust=False`, next-open fill,
invalid gap, overlap, fixed RR 2.5, entry-bar resolution, pessimistic
simultaneous stop-first handling and the 239/240 time-exit boundary conformed in
the deterministic review cases.

## Risks not demonstrated as defects

- `2F-RISK-001`: synthetic bars have no timestamp field, so tuple chronology is
  a caller invariant. No incorrect result was reproduced when documented order
  was respected.
- `2F-RISK-002`: `SignalDecision` has no variant identity field. The corrected
  source validates decision state and implementation identity, and no
  operational consumer is authorized. This is not classified as a defect in
  Phase 2F.

## Optional improvements outside scope

- `2F-OPT-001`: typed synthetic sequence identifiers before any separately
  authorized evaluation phase.
- `2F-OPT-002`: variant provenance on a future `SignalDecision` version if an
  operational boundary is ever authorized.

Neither improvement is implemented here because it would expand the frozen
contract or anticipate an operational integration.

## Exact package scope

The package contains only:

1. `docs/PHASE_10_42R_2F_FROZEN_RECOVERY_CANDIDATE_IMPLEMENTATION_INDEPENDENT_CODE_REVIEW.md`
2. `src/analysis/frozen_recovery_candidate_implementation_v2.py`
3. `src/validation/frozen_recovery_candidate_independent_code_review_v1.py`
4. `src/workflows/validate_phase_10_42r_2f_frozen_recovery_candidate_implementation_independent_code_review.py`
5. `tests/test_frozen_recovery_candidate_independent_code_review.py`
6. `PHASE_10_42R_2F_MANIFEST.sha256`

The manifest hashes the first five files. The manifest is not self-hashed.

## Acceptance criteria

Phase 2F is eligible for local closure only when all conditions hold:

1. Active branch is
   `phase-10-42r-2f-frozen-recovery-candidate-implementation-independent-code-review-v1`.
2. `HEAD` is exactly descended from authoritative commit `7d7f8ee` and the work
   tree was clean before applying the package.
3. Package SHA-256 and every manifest entry match.
4. Exactly the six package paths are added and no pre-existing path is modified.
5. `git diff --check` passes.
6. The Phase 2F test module passes completely.
7. `py_compile` passes for the corrected implementation, validator, workflow and
   test module.
8. Preflight passes all 7 source-only checks.
9. Full workflow passes all 40 checks, including 30 deterministic synthetic
   cases, with 0 failures and 0 blockers.
10. Exactly five confirmed findings reproduce on `v1` and are blocked on `v2`.
11. Phase 2D root, Phase 2D source and Phase 2E `v1` source hashes remain exact.
12. Real-data access, report access, holdout access, backtests and performance
    outputs remain zero.
13. All execution, automation and OpenClaw permissions remain `False`.
14. No candidate is compared, ranked, selected, rehabilitated or activated.

## Local validation

Run from the repository root in PowerShell after verifying the package hash and
copying exactly the manifest paths:

```powershell
git diff --check

python -m unittest `
    tests.test_frozen_recovery_candidate_independent_code_review `
    -v
if ($LASTEXITCODE -ne 0) { throw "Fallaron las pruebas 2F." }

python -m py_compile `
    src\analysis\frozen_recovery_candidate_implementation_v2.py `
    src\validation\frozen_recovery_candidate_independent_code_review_v1.py `
    src\workflows\validate_phase_10_42r_2f_frozen_recovery_candidate_implementation_independent_code_review.py `
    tests\test_frozen_recovery_candidate_independent_code_review.py
if ($LASTEXITCODE -ne 0) { throw "Falló py_compile 2F." }

python -m src.workflows.validate_phase_10_42r_2f_frozen_recovery_candidate_implementation_independent_code_review --preflight-only
if ($LASTEXITCODE -ne 0) { throw "Falló el preflight 2F." }

python -m src.workflows.validate_phase_10_42r_2f_frozen_recovery_candidate_implementation_independent_code_review
if ($LASTEXITCODE -ne 0) { throw "Falló el workflow 2F." }

git status --short
git diff --stat
```

Do not run the prior full workflow or broad test discovery for this closure:
that would be redundant and may invoke checks outside the exclusive source-only
scope. The Phase 2F module is the complete authorized suite for this package.

## Next safe phase

`PHASE_10_42R_2G_FROZEN_RECOVERY_CANDIDATE_CORRECTION_INDEPENDENT_SYNTHETIC_ACCEPTANCE_V1`

Phase 2G may independently accept the corrected source using only deterministic
synthetic fixtures and static inspection. It must not read real data, result
reports or holdouts; run backtests; calculate performance; compare, rank or
select candidates; modify the retired SHORT or Phase 2D; or enable operational,
automation or OpenClaw permissions. Any scientific authorization to evaluate
the candidates must be a later, separate decision after 2G closes.
