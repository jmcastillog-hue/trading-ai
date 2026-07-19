# Phase 10.42R.2A — Signal-to-Fill Timing Integrity Audit V1

## Purpose

Measure the effect of an executable fill contract after the completed-candle
MTF repair. This phase does not search for a profitable configuration.

The existing engines confirm a 15m signal with the current candle OHLC and use
that same candle close as the historical entry. The audit preserves this mode
only as `SAME_CANDLE_CLOSE_DIAGNOSTIC_ONLY` and compares it with
`NEXT_BAR_OPEN_CORRECTED`.

## Real-data Phase 10.42R.2 attribution

The source report archive passed ZIP integrity and contained fourteen CSV
reports. The relevant tables had:

- 72 unique SHORT window rows: 36 corrected and 36 legacy
- 360 unique cost-window rows
- nine stable dataset hashes
- ten passing validation checks and zero blockers

Corrected performance by symbol:

| Symbol | Trades | Compound return | Average PF | Positive windows |
|---|---:|---:|---:|---:|
| BTCUSDT | 51 | -13.52% | 0.98 | 5/12 |
| ETHUSDT | 69 | -26.00% | 0.70 | 5/12 |
| SOLUSDT | 85 | -8.97% | 1.08 | 6/12 |

Corrected performance by calendar year across all symbols:

| Year | Trades | Compound return | Average PF | Positive windows |
|---|---:|---:|---:|---:|
| 2023 | 41 | -2.79% | 0.98 | 5/12 |
| 2024 | 61 | -7.25% | 1.07 | 7/12 |
| 2025 | 103 | -35.39% | 0.74 | 4/12 |

The corrected return was lower than legacy in 27 windows, higher in six and
equal in three. Ten window signs changed. This is an attribution result, not an
authorization to remove ETHUSDT, isolate SOLUSDT or select a favorable year.

## SHORT timing contract

For the official fixed SHORT candidate:

1. Build only the corrected completed-candle MTF context.
2. Reproduce all 36 official same-close windows exactly.
3. Confirm the signal at candle index `i`.
4. Use `open[i+1]` as the raw entry reference.
5. Apply half-spread to the SHORT entry.
6. Use ATR known at signal close for the initial stop distance.
7. Allow stop or target resolution inside the entry candle; stop wins an
   ambiguous same-bar collision.
8. Record signal, entry and exit indexes and timestamps.

The corrected run may still fail or may differ in either direction. No result
can restore the rejected candidate in this phase.

## LONG timing contract

The Phase 8 15m structural candidates are independent of the MTF defect, but
their historical resolver also enters at signal close. The audit keeps two
different lineage stages explicit:

- reproduces all four full historical candidates against the Phase 8.4
  historical metrics
- reproduces the primary and secondary readiness values against the Phase 8.10
  post-OOS, stress-cost Monte Carlo source
- keeps the original signal indexes
- moves entry to `open[i+1]`
- rebuilds stop and target around the new entry using signal-time structure
- processes the entry candle conservatively
- keeps every approval and execution flag false

The Phase 8.4 historical metrics must never be compared directly with the
Phase 8.10 readiness source values. They describe different populations after
different filters.

## First real execution and lineage correction

The first real Phase 10.42R.2A execution reproduced 36/36 SHORT windows and
measured 205 trades in both timing modes:

| Timing mode | Trades | Compound return | Average PF | Decision |
|---|---:|---:|---:|---|
| Same-close diagnostic | 205 | -41.7469% | 0.919596 | `WALK_FORWARD_FAILED` |
| Next-open corrected | 205 | -41.7443% | 0.919609 | `WALK_FORWARD_FAILED` |

The timing correction changed compound return by approximately +0.0026
percentage points and did not recover the rejected SHORT candidate.

All 64 LONG next-open fills occurred after their signals. The four historical
candidate metrics were identical between same-close and next-open because the
continuous source candles had `open[i+1] == close[i]`. This is a measured
historical property, not a strategy approval.

The run failed closed on its sole blocker because the first harness revision
incorrectly compared full Phase 8.4 historical metrics (for example 12 trades
and +5.5 R for failed breakdown) with Phase 8.10 post-filter readiness inputs
(5 trades and +3.002336 R). The revised harness does not waive that blocker;
it replaces the invalid cross-stage assertion with two stage-specific lineage
checks and adds the two source reports to preflight.

An audit completion means that the measurement and its lineage are valid. It
does not mean that a strategy is successful, approved or executable.

## Cost-accounting audit

The active SHORT engine calculates `result_r` from net PnL after internal fees
and spread. The cost-aware layer then subtracts a complete platform cost
profile. The audit reports fee and spread overlap per profile and the remaining
unembedded slippage/buffer components.

This phase does not publish a normalized cost gate. A later remediation must
choose one auditable basis:

```text
gross trade result -> exactly one complete cost model -> net result
```

## Inputs

- the five required Phase 10.42R.2 report CSVs
- the Phase 8.4 full historical metrics report
- the Phase 8.10 post-OOS stress-cost Monte Carlo candidate summary
- the same nine BTCUSDT/ETHUSDT/SOLUSDT 15m, 1H and 4H datasets
- the existing Phase 8 LONG historical 15m source

All dataset hashes must match the Phase 10.42R.2 manifest. Network downloads
are not supported by this audit.

## Commands

```powershell
python -m unittest tests.test_signal_to_fill_timing_integrity_audit -v
python -m py_compile src\validation\signal_to_fill_timing_integrity_audit_v1.py
python -m py_compile src\workflows\validate_phase_10_42r_2a_signal_to_fill_timing_integrity_audit.py
python -m src.workflows.validate_phase_10_42r_2a_signal_to_fill_timing_integrity_audit --preflight-only
python -m src.workflows.validate_phase_10_42r_2a_signal_to_fill_timing_integrity_audit
```

## Safety boundary

The phase writes CSV reports only beneath its ignored report directory. It may
not download data, create or modify the official forward dataset, persist
evidence, generate a signal, send an alert, submit a paper trade, place an
exchange order, use capital, choose a new candidate or enable automation.

After a complete, integrity-valid audit, the proposed next phase is:

`PHASE_10_42R_2B_COST_ACCOUNTING_NORMALIZATION_AND_STRATEGY_RECOVERY_PREREGISTRATION_V1`
