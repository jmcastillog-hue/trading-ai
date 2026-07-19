# Phase 10.42R.2 — SHORT/LONG Closed-Candle MTF Revalidation V1

## Purpose

Produce a reproducible scientific decision after the Phase 10.42R correction.
The run compares the former candle-open timestamp behavior with the completed
candle contract on identical raw OHLCV inputs.

The legacy path is an explicit negative control named
`LEGACY_OPEN_TIMESTAMP_DIAGNOSTIC_ONLY`. It is never a valid research output.

## Scope classification

| Candidate | Dependency classification | Required action |
|---|---|---|
| `TARGET_SHORT_FIB_V5_MTF_V3_1 + FIXED_RR_2_5` | Directly uses MTF regime and Directional Context V3.1 | Full corrected revalidation |
| `LONG_BASE_FAILED_BREAKDOWN_V1` | Independent 15m structural chain | Source audit and Phase 8 consistency rerun |
| `LONG_BASE_LIQUIDITY_SWEEP_V1` | Independent 15m structural chain | Source audit and Phase 8 consistency rerun |
| `LONG_BASE_MTF_BULLISH_CONTINUATION_V1` | MTF hypothesis | Remains rejected and out of scope |

## Immutable-by-run data contract

The run requires BTCUSDT, ETHUSDT and SOLUSDT in 15m, 1H and 4H from
2022-01-01 through 2025-12-31. It records path, size, row count, coverage and
SHA-256 for all nine files.

Network use is fail-closed by default. `--allow-download` authorizes downloads
only for missing files from Binance public market-data endpoints. Existing
files are never silently replaced.

## SHORT gates

The fixed official SHORT configuration is evaluated over twelve rolling OOS
test windows per symbol under both timestamp modes. The corrected trades then
pass through:

- raw rolling OOS aggregation
- five cost profiles
- Binance scalp stress friction
- deterministic bootstrap sequence risk with seed 42
- closed-candle availability invariants

A completed run certifies the reported corrected metrics. Candidate status is
independent: it may be revalidated, rejected or marked insufficient.

## LONG consistency control

The source dependency audit parses imports for the historical, OOS,
walk-forward, cost, Monte Carlo and readiness modules. The complete Phase 8.11
chain is then rerun. The expected research-only decisions are:

- `LONG_BASE_FAILED_BREAKDOWN_V1` → `LONG_FORWARD_OBSERVATION_CANDIDATE`
- `LONG_BASE_LIQUIDITY_SWEEP_V1` → `LONG_SECONDARY_WATCHLIST`

These labels do not authorize forward collection or execution.

## Commands

```powershell
python -m unittest discover -s tests -p "test_*.py" -v
python -m compileall -q src
python -m src.workflows.validate_phase_10_42r_2_short_long_closed_candle_mtf_revalidation --preflight-only
python -m src.workflows.validate_phase_10_42r_2_short_long_closed_candle_mtf_revalidation
```

If the preflight reports missing inputs:

```powershell
python -m src.workflows.validate_phase_10_42r_2_short_long_closed_candle_mtf_revalidation --preflight-only --allow-download
```

## Safety boundary

This phase does not write the official forward dataset, collect forward
evidence, generate a live signal, send an alert, submit a paper trade, use real
capital, place an exchange order or enable automation.

After a passing complete run, the next recommended phase is:

`PHASE_10_42R_3_OPENCLAW_READ_ONLY_RESEARCH_STATUS_CONTRACT_V1`

## Real-data execution result

The official corrective run completed on Windows with exit code 0. It passed
all ten validation controls with zero blockers and zero error rows. The run
did not create or mutate the official LONG forward dataset, temporary file,
lock, manifest or backup directory.

### Input manifest

| Symbol | Timeframe | Rows | SHA-256 |
|---|---:|---:|---|
| BTCUSDT | 15m | 140252 | `a110945be3a203ff333e982c5998520fd39a9dcb2d0c8a269c182954f45957e5` |
| BTCUSDT | 1h | 35064 | `04a6d652b5d9078db91e1e8760a61948100f683cbcc5994022b480de8e77700d` |
| BTCUSDT | 4h | 8767 | `2fe44cb35ea8933d28764035284ad696ece63c60fc1b7ff2030266e427717e4f` |
| ETHUSDT | 15m | 140252 | `437e43778550a5eda08022cf4779bc908c6ee25b41b935dad2300c1cf4666013` |
| ETHUSDT | 1h | 35064 | `029234ba563a9e9fcef9431f933d6882203834796fc5daedc2aa054dc0b59ba9` |
| ETHUSDT | 4h | 8767 | `ff21a71e09b402e201fb4b65347c2f4738adaea8ddc06d8d7aa4a42c319effbb` |
| SOLUSDT | 15m | 140252 | `c771aa0280cb273908981d475ad4cc057e29a7113a5cc164f8deebff3db6d093` |
| SOLUSDT | 1h | 35064 | `6508ef8ad248557ee4bd745c0e22e0913451213259555f2c9f1e63ec6008d2ea` |
| SOLUSDT | 4h | 8767 | `c552bd055b1f91e0936f6fac6dfc9578c3a59fd284894fe2ab19d9ae99d417a4` |

All nine hashes were identical before and after the run.

### Closed-candle impact

The corrected context exposed zero 1H or 4H rows before candle close. Against
the legacy control, the corrected Directional Context V3 result changed on
35,988 BTCUSDT rows, 36,933 ETHUSDT rows and 41,483 SOLUSDT rows. The final
SHORT permission changed on 3,344, 3,740 and 5,052 rows respectively.

| Metric | Legacy diagnostic | Corrected |
|---|---:|---:|
| Fixed OOS test windows | 36 | 36 |
| Test trades | 122 | 205 |
| Compound test return | +0.710594 | -0.417469 |
| Average profit factor | 2.424407 | 0.919596 |
| Average expectancy R | +0.410642 | -0.094741 |
| Worst test drawdown | -0.076907 | -0.116739 |
| Positive-window rate | 0.555556 | 0.444444 |
| Walk-forward decision | `WALK_FORWARD_PASS` | `WALK_FORWARD_FAILED` |

The return delta is -1.128063 and the expectancy delta is -0.505383 R. Every
corrected cost profile failed. Under the Binance scalp stress profile, the
corrected compound return was -0.672663 and average expectancy was -0.366963 R.

The deterministic 10,000-simulation sequence-risk run also failed:

| Metric | Corrected stress result |
|---|---:|
| Sample trades | 205 |
| Median return | -0.673439 |
| P05 return | -0.771628 |
| Probability negative return | 1.0 |
| Median max drawdown | -0.682354 |
| Probability drawdown below -15% | 1.0 |
| Decision | `MONTE_CARLO_FAILED` |

### Candidate decision

The affected SHORT candidate is `REVALIDATED_REJECTED`. The positive legacy
control is evidence of the defect's impact and has no approval authority.

The primary and secondary LONG candidates were confirmed independent of the
affected MTF modules, and the Phase 8.11 readiness decisions reproduced. Their
shared status is `CERTIFIED_UNAFFECTED_AND_CONSISTENCY_REVALIDATED`; the primary
candidate remains a future research candidate and the secondary remains a
watchlist. Neither candidate is strategy-approved or execution-approved.

`scientific_revalidation_completed`, `historical_metrics_certified`,
`phase_10_43_design_review_allowed` and
`openclaw_read_only_status_design_allowed` are true. Every operational,
execution, signal, forward-observation, dataset-write and persistence flag is
false. `total_project_completed` remains false.
