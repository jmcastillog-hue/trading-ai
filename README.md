# Trading-AI / OpenClaw Quantitative Decision-Support System

Local Python project for quantitative cryptocurrency research, historical and
forward validation, risk analysis and human-reviewed decision support.

The project is not an autonomous trading bot. Paper-trade execution, real
capital, exchange orders, live trading alerts and automation remain disabled.

## Current status

- Repository baseline: Phase 10.42 at commit `40d1c37`.
- Corrective workstream: Phase 10.42R scientific-integrity and reproducibility.
- SHORT candidate: `REVALIDATION_REQUIRED`.
- LONG candidates: `REVALIDATION_REQUIRED`.
- Official LONG forward-evidence dataset: absent.
- OpenClaw operational integration: blocked pending corrected revalidation.

Phase 10.42R changes higher-timeframe feature availability so indicators that
use a complete 1H or 4H candle become visible only after that candle closes.
Historical results produced with the prior MTF merge are not certified until
the SHORT and LONG validation chains are repeated.

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
