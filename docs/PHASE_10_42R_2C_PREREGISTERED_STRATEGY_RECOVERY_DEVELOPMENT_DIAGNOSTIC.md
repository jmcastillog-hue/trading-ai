# Phase 10.42R.2C — Preregistered Strategy-Recovery Development Diagnostic V1

## Purpose

Diagnose failure mechanisms of the retired corrected SHORT reference using
only known 2022–2025 development evidence. This phase is descriptive and
report-only. It cannot repair, rank, optimize, select, reclassify or execute a
strategy.

## Immutable inputs

The harness requires:

- all eight Phase 10.42R.2B report artifacts
- the exact 205 source trades under all five fixed profiles
- the sixteen locked recovery rules
- the canonical frictionless-gross-to-single-profile-net contract
- all nine 15m/1H/4H BTCUSDT, ETHUSDT and SOLUSDT datasets
- hash and row-count equality with the Phase 10.42R.2 dataset manifest

There is no `--allow-download` option. A missing or changed input blocks the
run.

## Feature contracts

Volatility is defined before outcome inspection:

```text
volatility_proxy = signal_atr / signal_close
LOW  <= cohort 1/3 quantile
MID  <= cohort 2/3 quantile
HIGH >  cohort 2/3 quantile
```

Thresholds are calculated over all fixed known source trades. No PnL, return,
symbol result or candidate decision is used.

Trend regime is reconstructed at each source `signal_time` from the corrected
closed-candle 1H and 4H regime engine:

```text
trend_regime = REGIME_1H=<state>|REGIME_4H=<state>
```

Any missing or `UNKNOWN` signal context fails closed.

## Preregistered slices

Exactly five dimensions are published:

1. fixed symbol cohort
2. calendar year 2023, 2024 and 2025 OOS evidence
3. LOW, MID and HIGH volatility terciles
4. corrected 1H×4H trend regime
5. the single retired SHORT signal family

All outputs retain BTCUSDT, ETHUSDT and SOLUSDT. A dimension value with no
trades is a blocker; it cannot be silently removed.

## Metric contract

Every slice/value is repeated for all five fixed cost profiles and publishes:

- trade and unique-source counts
- normalized total and average R
- normalized profit factor
- realized-time chronological max drawdown R
- configured, observed, zero-trade and positive window counts
- positive-window rate
- frictionless gross expectancy, profit factor and drawdown
- profile cost and gross-edge-to-cost ratio
- signed break-even round-trip cost percentage

Rows follow fixed dimension, value and profile order. No performance rank,
winner, recommended symbol or selected cohort is created.

## Safety and holdout boundary

The following remain false: candidate search, parameter optimization,
diagnostic ranking, symbol selection, candidate mutation/reclassification,
holdout access, signals, forward persistence, paper trading, capital, alerts,
exchange access, automation, execution and OpenClaw operational integration.

Both the 2026-H1 retrospective lockbox and the 2026-07-20 to 2027-01-20
prospective holdout must remain absent. The official LONG forward dataset and
all related temporary, lock, manifest and backup artifacts must also remain
absent.

## Fail-closed workflow

```powershell
python -m src.workflows.validate_phase_10_42r_2c_preregistered_strategy_recovery_development_diagnostic --preflight-only
python -m src.workflows.validate_phase_10_42r_2c_preregistered_strategy_recovery_development_diagnostic
```

Preflight performs fifteen lineage, data and safety checks. The full run adds
eleven diagnostic checks. Any ERROR failure returns exit code 1.

## Outputs

The ignored Phase 2C report directory contains:

- phase summary and checks
- Phase 2B report lineage and dataset lineage
- diagnostic contract and explicit acceptance criteria
- preregistration and holdout snapshots
- outcome-independent volatility thresholds
- one feature row per source trade
- deterministic slice catalog and coverage
- all-profile slice metrics
- errors

## Acceptance criteria

Acceptance requires all of the following:

- `26/26` full-run checks pass
- `blocker_count = 0`, `error_rows = 0`, `validation_passed = True`
- source trades = 205, normalized rows = 1,025, profiles = 5
- slice dimensions = 5 and every coverage row is complete
- all slice/value rows contain all five profiles and primary metrics
- SHORT status remains `RETIRED_REVALIDATED_REJECTED_UNCHANGED`
- LONG status remains `RESEARCH_ONLY_NOT_APPROVED_UNCHANGED`
- no symbol is selected and no candidate is ranked or reclassified
- both holdouts and official forward artifacts remain absent
- every execution/automation/OpenClaw permission remains false

Successful diagnostics permit only:

`PHASE_10_42R_2D_RECOVERY_CANDIDATE_FAMILY_SPECIFICATION_AND_MULTIPLICITY_FREEZE_V1`

Phase 2D must freeze at most three families and four variants per family before
any evaluation. Phase 2C itself proposes no winner.

## Real-data closure

The real report archive has SHA-256:

```text
27d6ccb4e77c2453837df5db48fdea09ce3f6f4733bf00e9c5dd2d22da03bb63
```

The run passed all 26 controls with zero blockers and zero errors. It preserved
205 source trades, 1,025 normalized rows, five slice dimensions, 12 catalog
values and 60 all-profile metric rows. All permissions remained false, both
holdouts remained absent and no official forward artifact was created.

The Binance-base calendar-year results were negative in 2023, 2024 and 2025.
The only positive Binance-base trend slice was
`REGIME_1H=STRONG_BEARISH|REGIME_4H=BEARISH`, with `+0.216476 R` average and
profit factor `1.312791`. It turned slightly negative under Binance stress,
contained only 72 trades and included only 15 BTCUSDT trades. It therefore
fails PR-011 minimum evidence and PR-012 stress stability.

Closure decision:

`PHASE_10_42R_2C_PREREGISTERED_DEVELOPMENT_DIAGNOSTIC_COMPLETED`

This decision validates the diagnostic harness and closes Phase 2C. It does
not validate or reactivate a strategy. Phase 2D is the only permitted next
phase and must freeze candidate-family and multiplicity contracts before any
new evaluation, while keeping both holdouts sealed and every operational
permission false.
