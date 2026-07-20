# Phase 10.42R.2K — Frozen recovery candidate controlled known-evidence evaluation

## Decision boundary

Phase 10.42R.2K is the first phase authorized to evaluate the six corrected,
frozen SHORT recovery variants against the known 2022–2025 market dataset.
The evaluated evidence is not a holdout. Calendar year 2022 is used only for
indicator warm-up; eligible entries run from 2023-01-01 through 2025-12-31.

This phase may calculate and persist preregistered historical metrics. It may
classify each variant against the ten frozen gates. It may not compare or rank
variants, select a winner, mutate a rule, open either lockbox, grant operational
approval, emit live signals, paper trade, use real capital, execute at an
exchange, automate operations, or integrate OpenClaw operationally.

Successful execution ends with:

`CONTROLLED_KNOWN_EVIDENCE_EVALUATION_VALIDATED_NO_WINNER`

The only planned successor is:

`PHASE_10_42R_2L_FROZEN_RECOVERY_CANDIDATE_INDEPENDENT_RESULT_AUDIT_AND_DISPOSITION_V1`

## Frozen source anchors

- Phase 2J commit:
  `384f032599a75e203ea02f9a8cc6ea6ceda1ed81`
- Phase 2J binding root:
  `5c1ccb1c9fecdad2e196558a946944f5b9f89f258c5ef591a65d4c4c480d8c14`
- Phase 2H protocol root:
  `a42a8da21d1afd231be37376de8ecdfc0306dc8db2375bacb5f2de567947e493`
- Phase 2I harness design root:
  `ee62064148bdb119c7b3390d7dab3db338b4d5b50a1eaf7adb44d4c9dffd5dbb`
- Corrected candidate implementation normalized SHA-256:
  `ccf3cc05823515fa56e9e1183eb51ab903503e310aa037248847ad7445b2cc1e`
- Frozen candidate specification root:
  `0872b2bf7355e8a9b35d5b4e0e05d3edf291006862ce9ee5eae847910ef4c015`
- Phase 2K evaluation-engine normalized SHA-256:
  `9243ae595f7d22bc2653ba34098bec5f1b6bc2a1e79c4114b8ea35fd83c3a4fd`

Any mismatch blocks evaluation before market content is processed.

## Fixed candidate cohort

The evaluation order is identity order, not a performance rank:

1. `RCV_SHORT_UPSIDE_SWEEP_REVERSAL_F01_N48_V01`
2. `RCV_SHORT_UPSIDE_SWEEP_REVERSAL_F01_N96_V02`
3. `RCV_SHORT_BREAKDOWN_RETEST_F02_N48_V01`
4. `RCV_SHORT_BREAKDOWN_RETEST_F02_N96_V02`
5. `RCV_SHORT_EMA_PULLBACK_CONTINUATION_F03_S000_V01`
6. `RCV_SHORT_EMA_PULLBACK_CONTINUATION_F03_S025_V02`

The symbol cohort remains exactly BTCUSDT, ETHUSDT and SOLUSDT. The input grid
remains exactly 15m, 1h and 4h for each symbol.

## Time, execution and gap semantics

- A signal is confirmed only at the close of 15m bar `t`.
- 1h and 4h regime features become available only at their candle close.
- The 1h and 4h contexts must both be `BEARISH` or `STRONG_BEARISH`.
- A context carried across a missing higher-timeframe interval is stale and is
  blocked.
- Indicator histories reset after a declared source gap. No EMA, ATR, rolling
  high or rolling support calculation bridges an unobserved interval.
- Entry is the next contiguous 15m open `t+1`.
- If `t+1` is absent, the order is blocked.
- The stop must be strictly above the SHORT entry.
- One position may be open per symbol and variant.
- Target is fixed at 2.5R.
- Entry-bar resolution is allowed.
- A simultaneous stop and target resolves stop first.
- The time exit is the close of the 240th entry-relative observed bar.
- If an open trade reaches a declared gap before an observed exit, its outcome
  is unobservable. The row is retained but excluded from metrics; no price is
  interpolated. New orders remain blocked until the maximum theoretical holding
  horizon has elapsed.
- A right-censored position at the known-evidence boundary is retained but
  excluded from metrics.

The source gap ledger remains 18 rows and synthetic gap fill remains zero.

## Cost accounting

Every eligible frictionless result is expanded once across five fixed profiles:

1. `BINANCE_SCALP_BASE_ESTIMATE`
2. `BINANCE_SCALP_STRESS_ESTIMATE`
3. `QUANTFURY_SWING_BASE_ESTIMATE`
4. `QUANTFURY_SWING_STRESS_ESTIMATE`
5. `EXTREME_COST_STRESS_TEST`

The accounting contract is:

`FRICTIONLESS_GROSS_R_TO_SINGLE_PROFILE_NET_R_V1`

For each profile:

`profile_total_cost_r = round_trip_cost_fraction / risk_fraction_of_entry`

`normalized_net_result_r = frictionless_gross_result_r - profile_total_cost_r`

A profile is applied exactly once. No internal or legacy cost is subtracted a
second time.

## Evidence clusters, metrics and multiplicity

The fixed test universe contains 36 symbol-window clusters: three symbols by
twelve quarterly windows from 2023-Q1 through 2025-Q4. Zero-trade clusters are
retained.

The primary test uses the Binance base profile and exactly 10,000 PCG64 cluster
bootstrap resamples. The seed is `10420200 + evaluation_order`. All six
unadjusted p-values enter one Holm-Bonferroni family-wise pool. Ties are resolved
by unadjusted p-value and then evaluation order.

The metric table always publishes the complete frozen grid, including zero-
trade variants or slices:

- aggregate;
- symbol;
- calendar year;
- volatility tercile;
- closed 1h × 4h regime;
- signal family;
- cost profile.

The fixed structural count is 450 metric rows, six multiplicity rows and sixty
gate rows. These counts do not imply a positive result.

## Ten frozen gates

Each variant is classified independently against:

1. aggregate trade count at least 100;
2. at least 20 trades for every symbol;
3. Binance-base profit factor at least 1.05;
4. Binance-base aggregate expectancy above zero;
5. Binance-base expectancy above zero for every symbol;
6. Binance-base expectancy nonnegative for every calendar year;
7. Binance-stress expectancy nonnegative;
8. Binance-stress profit factor at least 1.00;
9. Holm-adjusted primary p-value at most 0.05;
10. all preregistered stability slices non-failing.

Gate 10 requires base positive-window rate at least 0.50, stress positive-window
rate at least 0.45, nonempty and nonnegative base expectancy in every volatility
tercile and all four allowed closed-MTF regimes, five published cost profiles,
and no unresolved or invalidated trade.

Passing all gates is a known-evidence classification only. It is not a winner,
promotion, paper-trading approval or operational authorization.

## Audit bundle

The deterministic run directory is under:

`reports/phase_10_42r_2k/<run_id>/`

It contains exactly:

1. `input_manifest.json`
2. `source_anchors.json`
3. `environment.json`
4. `data_quality.json`
5. `signal_ledger.csv`
6. `order_ledger.csv`
7. `trade_ledger.csv`
8. `metric_table.csv`
9. `multiplicity_table.csv`
10. `gate_classification.csv`
11. `check_ledger.csv`
12. `run_summary.json`

The run ID is derived from the Phase 2J binding root and Phase 2K engine hash.
Writes use a temporary directory followed by an atomic rename. Repeating an
identical run verifies the existing bundle byte-for-byte. A different artifact
under the same deterministic run ID fails closed.

## Validation and closure criteria

Phase 2K is eligible for closure only when:

- all 25 focused unit tests pass;
- `py_compile` passes for the engine, validator, workflow and tests;
- all 15 preflight checks pass;
- the controlled evaluation completes once;
- all 30 formal validation checks pass;
- the bundle contains exactly 12 artifacts;
- the metric, multiplicity and gate tables contain 450, 6 and 60 rows;
- source gaps remain declared and synthetic fills remain zero;
- candidate comparison, ranking and winner counts remain zero;
- both lockbox access counts remain zero;
- every operational permission remains disabled;
- the repository contains only the authorized Phase 2K source changes and the
  Phase 2K report-ignore rule.

A strategy gate failure is a legitimate scientific result and does not block
phase closure. Integrity or reproducibility failure does block closure.
