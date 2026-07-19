# Trading-AI / OpenClaw Quantitative Decision-Support System

Local Python project for quantitative cryptocurrency research, historical and
forward validation, risk analysis and human-reviewed decision support.

The project is not an autonomous trading bot. Paper-trade execution, real
capital, exchange orders, live trading alerts and automation remain disabled.

## Current status

- Repository baseline: Phase 10.42R at commit `7f5bd2b`.
- Phase 10.42R.2 real-data revalidation: completed and integrity-valid.
- SHORT candidate: `REVALIDATED_REJECTED`.
- LONG 15m structural chain: `CERTIFIED_UNAFFECTED_AND_CONSISTENCY_REVALIDATED`.
- Official LONG forward-evidence dataset: absent.
- Next workstream: Phase 10.42R.3 read-only OpenClaw research-status contract.
- OpenClaw operational integration and every execution permission: disabled.

Phase 10.42R changed higher-timeframe feature availability so indicators that
use a complete 1H or 4H candle become visible only after that candle closes.
The real-data Phase 10.42R.2 run completed over nine immutable-by-run datasets.
The legacy diagnostic control reproduced the prior optimistic SHORT result,
while the corrected closed-candle run rejected the candidate. The independent
LONG Phase 8 readiness chain reproduced without granting forward observation
or execution.

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
