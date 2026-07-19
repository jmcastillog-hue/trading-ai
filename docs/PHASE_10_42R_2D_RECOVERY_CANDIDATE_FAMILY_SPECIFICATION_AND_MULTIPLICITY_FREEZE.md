# Phase 10.42R.2D — Recovery Candidate Family Specification and Multiplicity Freeze

## Decision scope

Phase 10.42R.2D is a specification-only phase. It freezes a bounded set of new
SHORT research hypotheses before any candidate implementation or evaluation.
It does not backtest, calculate candidate performance, compare candidates,
select a winner, repair the retired SHORT in place or access either holdout.

The source boundary is fixed to:

- baseline commit:
  `abb2a4b31a7280b7bb052bcaafc1cd950ffbd995`;
- Phase 2C archive SHA-256:
  `27d6ccb4e77c2453837df5db48fdea09ce3f6f4733bf00e9c5dd2d22da03bb63`;
- known development period: `2022-01-01/2025-12-31`;
- complete symbol cohort: `BTCUSDT`, `ETHUSDT`, `SOLUSDT`.

The Phase 2C outcome slices are hypothesis-generating only. They are not used
to remove a symbol, rank a family, fit a threshold or rehabilitate
`TARGET_SHORT_FIB_V5_MTF_V3_1 + FIXED_RR_2_5`. That reference remains
`RETIRED_REVALIDATED_REJECTED_UNCHANGED`.

## Frozen candidate registry

The maximum contract is three families and four variants per family. This
freeze uses exactly three families and two variants per family: six hypotheses
in one family-wise multiplicity pool.

| Order | New family ID | Frozen variants | Only varying parameter |
|---:|---|---|---|
| 1 | `RCV_SHORT_UPSIDE_SWEEP_REVERSAL_F01_V1` | `...N48_V01`, `...N96_V02` | prior-high lookback: 48 or 96 completed 15m bars |
| 2 | `RCV_SHORT_BREAKDOWN_RETEST_F02_V1` | `...N48_V01`, `...N96_V02` | support lookback: 48 or 96 completed 15m bars |
| 3 | `RCV_SHORT_EMA_PULLBACK_CONTINUATION_F03_V1` | `...S000_V01`, `...S025_V02` | minimum EMA20/EMA50 separation: 0 or 0.25 ATR |

All identifiers are new. The family registry imports no retired strategy,
backtest, exchange, alert, execution or OpenClaw module.

### Family F01 — upside sweep reversal

At closed 15m bar `t`, price must sweep the maximum high of the preceding 48
or 96 completed bars, close back at or below that high, close below its open,
have non-zero body, and have an upper wick at least one body long. The stop is
`high[t] + 0.25 × ATR14[t]`.

### Family F02 — breakdown retest rejection

Within the prior eight completed bars, the most recent bar `j` must close at
least `0.25 × ATR14[j]` below support calculated from the prior 48 or 96 bars.
Bar `t` must retest within `0.25 × ATR14[t]` of that support, close below it and
close bearish. The stop is `max(high[t], support[j]) + 0.25 × ATR14[t]`.

### Family F03 — EMA pullback continuation

At closed bar `t`, EMA20 must be below EMA50 and EMA50 below EMA200. The prior
close must be below its EMA20; bar `t` must touch EMA20 and then close bearish
below it. The two variants require EMA50-minus-EMA20 separation of at least
zero or `0.25 × ATR14[t]`. The stop is `high[t] + 0.25 × ATR14[t]`.

All three families additionally require corrected closed-candle 1H and 4H
regimes in `{BEARISH, STRONG_BEARISH}`. Missing features block the signal.

## Common execution and accounting contract

The following inputs cannot change after this freeze:

- signal: complete 15m bar `t`;
- 1H/4H context: available only after each higher-timeframe candle closes;
- fill: next 15m open, `t + 1`;
- invalid gap: block when the stop is not strictly above the next-open SHORT
  entry;
- target: `entry - 2.5 × (stop - entry)`;
- position rule: one open position per symbol and variant;
- overlapping signal: ignore while that position is open;
- simultaneous stop and target: pessimistic stop first;
- time exit: close of the 240th entry-relative 15m bar;
- nominal risk: 1% per trade;
- accounting: frictionless gross R minus exactly one complete cost profile.

Five existing cost profiles are frozen in their original order. The primary
profile is `BINANCE_SCALP_BASE_ESTIMATE`; mandatory stress uses
`BINANCE_SCALP_STRESS_ESTIMATE`. QuantFury base/stress and the extreme stress
profile must also be published in a future evaluation.

## Fixed evaluation order and multiplicity

The order is F01-N48, F01-N96, F02-N48, F02-N96, F03-S000, F03-S025. It is a
serialization order, not a performance rank. Interim analysis and early
stopping are prohibited, and all six future results must be published.

The primary hypothesis is positive Binance-base normalized average R. Its
unadjusted one-sided p-value is frozen as a 10,000-replicate, symbol/window
cluster bootstrap over the complete `3 symbols × 12 splits = 36` unit
universe, including zero-trade units. The null sample is centered by the
observed average R, resampling uses NumPy `Generator(PCG64)`, and the seed is
`10420200 + evaluation_order`.

The six p-values form one family-wise pool and use step-down Holm-Bonferroni at
alpha 0.05. Ties are broken by evaluation order. This adjustment is mandatory
and cannot be replaced after seeing results.

## Mandatory future promotion gates

Every gate is conjunctive and non-overridable:

- specification hash must match this freeze;
- at least 100 aggregate OOS trades;
- at least 20 OOS trades in each fixed symbol;
- Binance-base normalized average R greater than zero;
- Binance-base profit factor at least 1.05;
- Binance-base positive-window rate at least 0.50;
- positive Binance-base expectancy for every symbol;
- non-negative Binance-base expectancy for every calendar year;
- Binance-stress expectancy non-negative;
- Binance-stress profit factor at least 1.00;
- Binance-stress positive-window rate at least 0.45;
- Holm-adjusted primary p-value at most 0.05;
- all five cost-profile rows published;
- all fail-closed integrity checks passed.

Passing these gates in a later evaluation would create evidence for review;
it would not itself authorize paper trading, real capital, alerts, automation,
exchange access or OpenClaw operations.

## Reproducible artifacts

The workflow emits eight immutable specification tables, their ordered
manifest and a root record. Canonical JSON uses sorted object keys, compact
separators, UTF-8, explicit column order and no NaN values. Each table receives
a SHA-256 over its canonical frame payload. The root binds the ordered table
hashes, full source commit and Phase 2C archive hash.

Expected root SHA-256 for this exact freeze:

`0872b2bf7355e8a9b35d5b4e0e05d3edf291006862ce9ee5eae847910ef4c015`

Changing a rule, parameter, order, cost, gate, identifier or source boundary
must change the root hash and fail verification against the frozen manifest.

## Fail-closed workflow

The preflight requires all 14 Phase 2C report files to match exact hashes,
sizes and row counts. It semantically reads only Phase 2C summary, checks,
errors, preregistration and holdout snapshots; diagnostic outcome tables are
hash-verified but not loaded for selection. Preflight failure writes only
schema-valid empty specification outputs and exits non-zero.

The full run adds 14 specification controls. Success therefore requires 28/28
checks, zero blockers, zero errors, six zero-result variants, no forbidden
output type and an exactly reproducible root.

```powershell
python -m unittest tests.test_recovery_candidate_family_specification_and_multiplicity_freeze -v

python -m py_compile `
    src\analysis\recovery_candidate_family_specification_v1.py `
    src\validation\recovery_candidate_family_specification_and_multiplicity_freeze_v1.py `
    src\workflows\validate_phase_10_42r_2d_recovery_candidate_family_specification_and_multiplicity_freeze.py

python -m src.workflows.validate_phase_10_42r_2d_recovery_candidate_family_specification_and_multiplicity_freeze --preflight-only
python -m src.workflows.validate_phase_10_42r_2d_recovery_candidate_family_specification_and_multiplicity_freeze
```

## Acceptance decision

Phase 2D can close only when all criteria in `acceptance_criteria_v1.csv` pass:
exact Phase 2C lineage; exact 3-family/6-variant registry; new identities;
fixed cohort, timing, costs and order; fixed multiplicity and promotion gates;
reproducible table and root hashes; absent holdouts and official artifacts;
zero evaluation rows; zero errors; and every operational permission false.

The only allowed next phase after clean closure is
`PHASE_10_42R_2E_FROZEN_RECOVERY_CANDIDATE_IMPLEMENTATION_AND_STATIC_CONFORMANCE_V1`.
Phase 2E may implement the frozen rules and prove conformance with synthetic
fixtures. It may not backtest, compare, rank or open a holdout, and it grants
no operational permission.

## Real-run closure

The independently reviewed Phase 2D report archive has SHA-256
`7eaa94579fbb2ad000db675c4f3fb13a276a6403b0b484c06d7e16784e7189d8`.
It contains exactly the 15 expected report CSV files. All 14 Phase 2C lineage
rows match, all eight frozen tables match the declarative builder, every
manifest hash recomputes and the golden root is exact.

The real run passed 28/28 controls with zero blockers and zero errors. It
contains three families and six unique variants, but no evaluated variant,
candidate result, comparison, rank or winner. SHORT remains
`RETIRED_REVALIDATED_REJECTED_UNCHANGED`; LONG remains
`RESEARCH_ONLY_NOT_APPROVED_UNCHANGED`. Both holdouts and the official dataset
remain absent, official evidence rows written remain zero and every operational
permission remains false.

Decision:

`PHASE_10_42R_2D_RECOVERY_CANDIDATE_SPECIFICATION_AND_MULTIPLICITY_FREEZE_COMPLETED`

This is a reproducible specification closure only. It provides no strategy
performance evidence and no operational authorization.
