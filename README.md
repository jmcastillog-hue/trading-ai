# Trading-AI / OpenClaw Quantitative Decision-Support System

Local Python project for quantitative cryptocurrency research, historical and
forward validation, risk analysis and human-reviewed decision support.

The project is not an autonomous trading bot. Paper-trade execution, real
capital, exchange orders, live trading alerts and automation remain disabled.

## Current status

- Repository baseline: Phase 10.42R.2A at commit `aa51e47`.
- Phase 10.42R.2 real-data revalidation: completed and integrity-valid.
- SHORT candidate: `REVALIDATED_REJECTED`.
- LONG 15m structural chain: `CERTIFIED_UNAFFECTED_AND_CONSISTENCY_REVALIDATED`.
- Official LONG forward-evidence dataset: absent.
- Phase 10.42R.2A signal-to-fill audit: completed with 17/17 tests,
  16/16 controls and zero blockers.
- Active workstream: Phase 10.42R.2B V2 gross-to-net cost normalization,
  chronological summary correction and strategy-recovery preregistration.
- The OpenClaw read-only contract is deferred until normalized cost lineage and
  recovery research boundaries are explicit.
- OpenClaw operational integration and every execution permission: disabled.

Phase 10.42R changed higher-timeframe feature availability so indicators that
use a complete 1H or 4H candle become visible only after that candle closes.
The real-data Phase 10.42R.2 run completed over nine immutable-by-run datasets.
The legacy diagnostic control reproduced the prior optimistic SHORT result,
while the corrected closed-candle run rejected the candidate. The independent
LONG Phase 8 readiness chain reproduced without granting forward observation
or execution.

A subsequent source review found that the 15m signal is confirmed with the
current candle high, low and close while the historical engines use that same
candle close as the fill. Phase 10.42R.2A therefore compares this
diagnostic-only convention against a tradeable `signal close -> next bar open`
contract. The LONG status is certified as unaffected by the MTF defect only;
its signal-to-fill metrics are not yet certified.

## Safety rule

```text
Measure first.
Then validate without future information.
Then observe prospectively.
Then consider paper simulation.
Only at the end consider automation.
```

## Environment

- Windows 11
- Python 3.14.5
- Git
- Pandas / NumPy
- Binance public market-data endpoints
- OpenClaw with LM Studio and a local model

Install the validated dependencies inside the virtual environment:

```powershell
python -m pip install -r requirements.txt
```

## Phase 10.42R validation

```powershell
python -m unittest tests.test_closed_candle_mtf -v
python -m py_compile src\market_structure\closed_candle_mtf.py
python -m py_compile src\market_structure\mtf_regime_filter.py
python -m py_compile src\market_structure\directional_context_filter_v3.py
python -m py_compile src\validation\project_scientific_integrity_and_reproducibility_audit_v1.py
python -m py_compile src\workflows\validate_phase_10_42r_project_scientific_integrity_and_reproducibility_audit.py
python -m src.workflows.validate_phase_10_42r_project_scientific_integrity_and_reproducibility_audit
```

A successful Phase 10.42R audit confirms that the remediation controls are
installed. It does not restore or certify historical strategy performance.

## Phase 10.42R.2 revalidation

The revalidation first checks nine local, immutable-by-run OHLCV inputs: 15m,
1H and 4H for BTCUSDT, ETHUSDT and SOLUSDT over 2022-2025. Network access is
disabled by default.

```powershell
python -m src.workflows.validate_phase_10_42r_2_short_long_closed_candle_mtf_revalidation --preflight-only
```

Only when one or more inputs are missing, an explicit public-data download can
be authorized:

```powershell
python -m src.workflows.validate_phase_10_42r_2_short_long_closed_candle_mtf_revalidation --preflight-only --allow-download
```

After a passing preflight, run the complete deterministic comparison:

```powershell
python -m src.workflows.validate_phase_10_42r_2_short_long_closed_candle_mtf_revalidation
```

The legacy timestamp mode exists only as a diagnostic control. It cannot
produce an approved candidate, forward row, signal or execution permission.

Real-data decision:

| Metric | Legacy diagnostic | Closed-candle corrected |
|---|---:|---:|
| OOS trades | 122 | 205 |
| Compound OOS return | +71.06% | -41.75% |
| Average profit factor | 2.4244 | 0.9196 |
| Average expectancy | +0.4106 R | -0.0947 R |
| Walk-forward decision | `PASS` | `FAILED` |

All five corrected cost profiles failed. The corrected stress sequence also
failed 10,000 deterministic bootstrap simulations with 100% probability of a
negative return in the sampled result. The run passed all ten integrity and
safety checks; this validates the rejection rather than the strategy.

Real-data attribution shows that the corrected loss was concentrated in 2025:
103 trades and -35.39% compound return across the three symbols. ETHUSDT was
the weakest symbol at -26.00%; SOLUSDT was closest to raw break-even at -8.97%,
but still failed the base-cost view. These are diagnostic cohorts and cannot be
selected retrospectively as new approved candidates.

## Phase 10.42R.2A timing audit

```powershell
python -m unittest tests.test_signal_to_fill_timing_integrity_audit -v
python -m src.workflows.validate_phase_10_42r_2a_signal_to_fill_timing_integrity_audit --preflight-only
python -m src.workflows.validate_phase_10_42r_2a_signal_to_fill_timing_integrity_audit
```

The audit must first reproduce the Phase 10.42R.2 same-close result. It then
changes only the fill contract to the next 15m open. It also reports whether
the cost-aware layer subtracts fee/spread estimates from results that already
include internal fees and spread. No normalized cost decision is allowed in
this phase.

The first real execution measured 205 SHORT trades in both modes. Compound
return changed only from -41.7469% to -41.7443%, so the candidate remains
`REVALIDATED_REJECTED_UNCHANGED`. The 64 LONG fills moved after their signals,
but their historical metrics were unchanged because the continuous candles
had `open[i+1] == close[i]`.

The revised lineage guard compares the full LONG historical rerun with Phase
8.4 and independently traces readiness values to the Phase 8.10 post-filter
Monte Carlo source. Passing the integrity audit validates the measurement, not
the strategy: every approval and execution permission remains false.

## Phase 10.42R.2B cost normalization and recovery preregistration

The SHORT engine's `result_r` already embeds internal spread and fees. Phase
10.42R.2B reconstructs frictionless gross R from raw next-open entry/exit
references and applies each complete cost profile exactly once:

```text
frictionless gross R - one complete profile cost R = normalized net R
```

Normalized metrics are diagnostic-only and cannot change the SHORT rejection
or approve LONG. The protocol labels 2022–2025 as known evidence, seals a
secondary 2026-H1 retrospective lockbox and reserves 2026-07-20 through
2027-01-20 as the primary prospective holdout. Neither dataset is downloaded
or opened in Phase 2B.

The V2 report contract orders aggregate drawdown by realized `exit_time`
(then entry time, symbol and source row), never by the source file's
BTC→ETH→SOL concatenation. Positive-window rate uses a fixed
`symbol × split_name` universe and includes configured windows with zero
trades in its denominator. These fields are published alongside trade count,
net expectancy and profit factor, as required by the preregistration.

```powershell
python -m unittest tests.test_cost_accounting_normalization_and_strategy_recovery_preregistration -v
python -m src.workflows.validate_phase_10_42r_2b_cost_accounting_normalization_and_strategy_recovery_preregistration
```

## Architecture direction

```text
Public market data
        ↓
Deterministic Python engines
        ↓
Validation and safety gates
        ↓
Read-only structured output
        ↓
OpenClaw / local model summary
        ↓
Human decision
```

Python remains the source of calculations and permissions. The local language
model may explain validated output, but it must not override a failed gate.
