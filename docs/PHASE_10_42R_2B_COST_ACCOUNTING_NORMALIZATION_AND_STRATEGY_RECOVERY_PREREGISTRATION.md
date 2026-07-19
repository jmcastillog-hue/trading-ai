# Phase 10.42R.2B — Cost Accounting Normalization and Strategy Recovery Preregistration V2

## Purpose

Define and validate one canonical gross-to-net accounting identity for the
corrected next-open SHORT trades, then lock the scientific protocol that any
strategy-recovery work must follow.

This phase is report-only. It does not repair the rejected candidate, publish
a normalized cost decision, optimize parameters, open holdout data or approve
execution.

## Source finding

The SHORT engine reports `result_r` after half-spread adjustment at entry and
exit plus entry and exit fees. The legacy cost-aware layer then subtracts a
complete fee, spread, slippage and buffer profile from that already-net result.
Fee and spread therefore overlap.

The Phase 8 structural LONG chain is different: its baseline `result_r` is a
frictionless structural outcome and its later cost layer applies one profile.
Phase 2B does not rewrite that historical chain.

## Canonical SHORT accounting identity

```text
frictionless_gross_pnl
  = (raw_entry_reference - raw_exit_reference) * position_units

frictionless_gross_result_r
  = frictionless_gross_pnl / risk_amount

profile_total_cost_r
  = sum(profile cost component percentages) / risk_pct_of_raw_entry

normalized_net_result_r
  = frictionless_gross_result_r - profile_total_cost_r
```

The existing engine output must independently reconcile:

```text
frictionless gross R
- embedded spread R
- internal fee R
= engine result_r
```

Tolerance is `1e-10 R`. Each normalized row must have
`cost_application_count = 1`.

## Chronological and window-summary contracts

Max drawdown represents a realized sequence. Every aggregate and per-symbol
summary therefore orders trades by UTC `exit_time`, then UTC `entry_time`,
symbol and `source_trade_row`. Input concatenation order is not a permitted
equity order.

Positive-window rate uses one fixed unit:

```text
window unit = configured symbol × walk-forward split_name
```

The denominator includes zero-trade units. For the real source this yields 36
configured units: three fixed symbols times twelve test windows. The BTC unit
for `WF_202210_202310_TO_202310_202401` has no trade and remains in the
denominator. Reports publish configured, observed, zero-trade and positive
window counts plus the positive-window rate.

The source/profile guard validates the exact Cartesian product of 205 source
rows and five named profiles. A matching total row count alone is insufficient.

## Decision boundary

The normalization tables are labeled
`DIAGNOSTIC_ONLY_NOT_DECISION_ELIGIBLE`. Even if a normalized metric improves,
Phase 2B cannot change the SHORT rejection, promote LONG, select a favorable
cohort, publish a cost reclassification or enable execution.

## Preregistered recovery rules

The protocol locks sixteen rules before the real normalization run. Principal
constraints include:

- only closed-candle MTF plus next-bar-open timing is eligible
- the rejected SHORT is a retired failed reference, not a tunable candidate
- BTCUSDT, ETHUSDT and SOLUSDT remain a fixed cohort
- 2022–2025 is known evidence and can never be relabeled as holdout
- diagnostic slices are fixed before evaluation
- later search is limited to at most three declared families and four variants
  per family
- all five fixed cost profiles use the canonical contract
- no future promotion with fewer than 100 aggregate OOS trades or fewer than
  20 per symbol
- post-result changes require a new version and forfeit unopened-test claims
  for data already viewed

## Holdout boundary

Phase 2B defines but does not download or open:

| Dataset | Interval | Evidence role |
|---|---|---|
| Retrospective lockbox | 2026-01-01 to 2026-07-20 | Secondary, one-time after candidate hash freeze |
| Prospective holdout | 2026-07-20 to 2027-01-20 | Primary confirmatory evidence |

The retrospective lockbox predates preregistration, so it is not described as
fully prospective. The second interval is the higher-grade evidence tier.

## Inputs and outputs

Required Phase 10.42R.2A reports:

- `summary_v1.csv`
- `checks_v1.csv`
- `short_timing_trades_v1.csv`

Principal outputs include source lineage, the accounting contract, normalized
per-trade/profile diagnostics, summaries, the locked preregistration, the
sealed holdout contract, checks and phase summary. All remain beneath the
ignored Phase 2B report directory.

The normalized summary must publish all PR-010 metrics: trade count, net
expectancy R, profit factor, chronological max drawdown R and positive-window
rate.

## Validation commands

```powershell
python -m unittest tests.test_cost_accounting_normalization_and_strategy_recovery_preregistration -v
python -m py_compile src\execution\normalized_cost_accounting_v1.py
python -m py_compile src\validation\cost_accounting_normalization_and_strategy_recovery_preregistration_v1.py
python -m py_compile src\workflows\validate_phase_10_42r_2b_cost_accounting_normalization_and_strategy_recovery_preregistration.py
python -m src.workflows.validate_phase_10_42r_2b_cost_accounting_normalization_and_strategy_recovery_preregistration
```

## Proposed next phase

After a real run with zero blockers:

`PHASE_10_42R_2C_PREREGISTERED_STRATEGY_RECOVERY_DEVELOPMENT_DIAGNOSTIC_V1`

Phase 2C may perform only the preregistered development diagnostics. It may not
open either holdout or promote a candidate.
