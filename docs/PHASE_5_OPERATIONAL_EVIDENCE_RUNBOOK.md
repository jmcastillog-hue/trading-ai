# PHASE 5 OPERATIONAL EVIDENCE RUNBOOK

## Status

Phase 5 defines the operational forward evidence layer of the Trading-AI / OpenClaw project.

This layer allows the project to ingest manually exported operational CSV files, validate them, convert them into forward observations, resolve them with available OHLC data, persist them into an operational evidence dataset, and maintain backups and snapshots.

This layer does not execute trades.

This layer does not connect to Binance, Quantfury, or any exchange.

This layer is for controlled evidence collection only.

## Core principle

```text
First measure.
Then test.
Then alert.
Then simulate.
Only at the end automate.
```

## Hard restrictions

```text
NO REAL CAPITAL
NO PAPER TRADING EXECUTION
NO LIVE ALERTS
NO BINANCE EXECUTION
NO QUANTFURY EXECUTION
NO EXCHANGE EXECUTION
NO AUTOMATION
NO AUTONOMOUS TRADING BOT BEHAVIOR
```

All Phase 5 modules must keep the following flags disabled:

```text
paper_trade_execution_allowed = False
real_capital_allowed = False
live_alerts_allowed = False
exchange_execution_allowed = False
automation_allowed = False
execution_allowed = False
```

If any of these flags becomes `True`, the operational evidence flow must be considered invalid.

---

# 1. Phase 5 purpose

Phase 5 exists to move the project from research-only infrastructure into controlled operational evidence collection.

It creates a safe bridge between:

```text
validated strategy research
↓
manual operational CSV exports
↓
forward observation generation
↓
OHLC-based theoretical resolution
↓
persistent evidence dataset
```

The goal is not to trade.

The goal is to collect forward evidence.

---

# 2. Phase 5 components

## 2.1 Phase 5.1 — Forward Observation Batch Runner V1

Main files:

```text
src/journal/forward_observation_batch_runner_v1.py
src/workflows/run_forward_observation_batch_runner_v1.py
```

Purpose:

```text
candidate signals
↓
batch runner
↓
forward observations
↓
duplicate protection
↓
journal / dataset candidate rows
```

Expected behavior:

```text
detect accepted candidates
generate forward observation rows
skip duplicates
keep execution flags disabled
```

---

## 2.2 Phase 5.2 — Forward Observation Batch Resolver V1

Main files:

```text
src/journal/forward_observation_batch_resolver_v1.py
src/workflows/run_forward_observation_batch_resolver_v1.py
```

Purpose:

```text
open forward observations
↓
future OHLC
↓
TARGET_HIT / STOP_HIT / OPEN_NO_FUTURE_DATA / RESOLUTION_ERROR
↓
result_r / MFE / MAE / bars_to_resolution
```

Expected behavior:

```text
resolve theoretical observations
measure result in R
measure maximum favorable excursion
measure maximum adverse excursion
keep execution flags disabled
```

---

## 2.3 Phase 5.3 — Forward Evidence Accumulation Controller V1

Main files:

```text
src/journal/forward_evidence_accumulation_controller_v1.py
src/workflows/run_forward_evidence_accumulation_controller_v1.py
```

Purpose:

```text
candidate signals
↓
new observations
↓
resolution
↓
cumulative evidence summary
↓
sample progress toward 100 / 300 observations
```

Expected behavior:

```text
track cumulative closed observations
track wins and losses
track average result_r
track progress toward minimum and preferred evidence thresholds
keep execution flags disabled
```

---

## 2.4 Phase 5.4 — Forward Evidence Dataset Persistence V1

Main files:

```text
src/journal/forward_evidence_dataset_persistence_v1.py
src/workflows/run_forward_evidence_dataset_persistence_v1.py
```

Purpose:

```text
resolved evidence
↓
persistent dataset
↓
duplicate protection
↓
progress tracking
```

Expected behavior:

```text
write new evidence rows
skip duplicate signal_id values
normalize dataset columns
preserve execution flags as False
```

---

## 2.5 Phase 5.5 — Persistent Forward Evidence Cycle Runner V1

Main files:

```text
src/journal/persistent_forward_evidence_cycle_runner_v1.py
src/workflows/run_persistent_forward_evidence_cycle_runner_v1.py
```

Purpose:

```text
operational cycle
↓
read existing dataset
↓
add new evidence
↓
update open evidence if closed
↓
write dataset atomically
↓
backup / snapshot
```

Expected behavior:

```text
maintain persistent dataset across runs
avoid overwriting existing valid evidence
create backups and snapshots when dataset changes
skip duplicates
keep execution flags disabled
```

---

## 2.6 Phase 5.6 — Operational Forward Evidence Dataset Bootstrap V1

Main files:

```text
src/journal/operational_forward_evidence_bootstrap_v1.py
src/workflows/run_operational_forward_evidence_bootstrap_v1.py
```

Purpose:

```text
create operational folders
↓
create empty operational dataset
↓
create input directories
↓
create templates
↓
wait for real exported files
```

Expected waiting state:

```text
OPERATIONAL_BOOTSTRAP_COMPLETED
WAITING_FOR_REAL_EXPORTED_INPUT_FILES
```

Expected safe output:

```text
dataset_exists = True
dataset_rows = 0
input_ready_for_processing = False
execution_allowed = False
```

---

## 2.7 Phase 5.7 — Operational Input File Validator / Adapter V1

Main files:

```text
src/journal/operational_input_file_validator_adapter_v1.py
src/workflows/run_operational_input_file_validator_adapter_v1.py
```

Purpose:

```text
read operational CSV files
↓
validate required columns
↓
validate timestamps
↓
validate OHLC structure
↓
validate entry / stop / target levels
↓
adapt valid files to internal format
↓
reject invalid files
```

Expected states:

```text
OPERATIONAL_INPUT_WAITING_FOR_FILES
OPERATIONAL_INPUT_VALIDATED_READY_FOR_CYCLE
OPERATIONAL_INPUT_VALIDATION_FAILED
```

Expected behavior:

```text
block incomplete files
block invalid OHLC files
block invalid price levels
require manual_review_required = True
keep execution_allowed = False
```

---

## 2.8 Phase 5.8 — Operational Persistent Cycle Integration V1

Main files:

```text
src/journal/operational_persistent_cycle_integration_v1.py
src/workflows/run_operational_persistent_cycle_integration_v1.py
```

Purpose:

```text
validated operational inputs
↓
forward observation generation
↓
OHLC-based resolution
↓
persistent operational dataset
↓
backup / snapshot
↓
duplicate protection
```

Expected states:

```text
OPERATIONAL_INTEGRATION_WAITING_FOR_VALID_INPUTS
OPERATIONAL_INTEGRATION_COMPLETED_WITH_EVIDENCE
OPERATIONAL_INTEGRATION_COMPLETED_NO_DATASET_CHANGES
OPERATIONAL_INTEGRATION_BLOCKED_BY_INPUT_VALIDATION
```

Expected behavior:

```text
generate operational forward observations
resolve observations when OHLC is available
persist new evidence
skip duplicate evidence
create backup and snapshot when dataset changes
keep execution_allowed = False
```

---

# 3. Operational folder layout

Operational data is stored under:

```text
data/forward_evidence/operational/
```

Expected structure:

```text
data/forward_evidence/operational/
├── forward_evidence_dataset_v1.csv
├── input/
│   ├── signals/
│   ├── ohlc/
│   └── price_levels/
├── backups/
├── snapshots/
└── templates/
```

These folders contain generated operational data and must remain ignored by Git.

They are not research source code.

They are not committed to the repository.

---

# 4. Input file specifications

## 4.1 Signals input

Folder:

```text
data/forward_evidence/operational/input/signals/
```

Required columns:

```text
observed_at
symbol
timeframe
signal_type
router_decision
cost_profile
context_name
direction
manual_review_required
notes
```

Required rules:

```text
observed_at must be parseable as datetime
symbol must not be empty
timeframe must not be empty
signal_type must not be empty
router_decision must not be empty
cost_profile must not be empty
context_name must not be empty
direction must be LONG or SHORT
manual_review_required must be True
```

Allowed router decisions:

```text
WATCH_ONLY
BLOCKED
SKIP
REVIEW_ONLY
```

Example:

```csv
observed_at,symbol,timeframe,signal_type,router_decision,cost_profile,context_name,direction,manual_review_required,notes
2026-06-21 05:00:00,BTCUSDT,15m,SHORT_ENTRY_SIGNAL,WATCH_ONLY,BINANCE_SCALP_BASE_ESTIMATE,NORMAL_VALIDATION_CONTEXT,SHORT,True,manual exported signal
```

---

## 4.2 OHLC input

Folder:

```text
data/forward_evidence/operational/input/ohlc/
```

Required columns:

```text
timestamp
open
high
low
close
volume
symbol
timeframe
data_source
```

Required rules:

```text
timestamp must be parseable as datetime
open must be numeric and positive
high must be numeric and positive
low must be numeric and positive
close must be numeric and positive
volume must not be negative
symbol must not be empty
timeframe must not be empty
```

OHLC consistency rules:

```text
high >= open
high >= close
high >= low
low <= open
low <= close
low <= high
```

Example:

```csv
timestamp,open,high,low,close,volume,symbol,timeframe,data_source
2026-06-21 05:15:00,65000,65100,64800,64900,100,BTCUSDT,15m,MANUAL_EXPORT
2026-06-21 05:30:00,64900,64950,63700,63800,120,BTCUSDT,15m,MANUAL_EXPORT
```

---

## 4.3 Price levels input

Folder:

```text
data/forward_evidence/operational/input/price_levels/
```

Required columns:

```text
signal_id
context_name
cost_profile
direction
entry_price
stop_price
target_price
price_level_source
notes
```

Required rules:

```text
direction must be LONG or SHORT
entry_price must be numeric and positive
stop_price must be numeric and positive
target_price must be numeric and positive
```

Valid SHORT structure:

```text
stop_price > entry_price > target_price
```

Valid LONG structure:

```text
stop_price < entry_price < target_price
```

Example SHORT:

```csv
signal_id,context_name,cost_profile,direction,entry_price,stop_price,target_price,price_level_source,notes
,NORMAL_VALIDATION_CONTEXT,BINANCE_SCALP_BASE_ESTIMATE,SHORT,65000,65500,63750,MANUAL_LEVELS,valid short levels
```

Example LONG:

```csv
signal_id,context_name,cost_profile,direction,entry_price,stop_price,target_price,price_level_source,notes
,NORMAL_VALIDATION_CONTEXT,BINANCE_SCALP_BASE_ESTIMATE,LONG,65000,64500,66250,MANUAL_LEVELS,valid long levels
```

---

# 5. Safe operational sequence

## 5.1 Bootstrap operational environment

Run:

```powershell
python -m src.workflows.run_operational_forward_evidence_bootstrap_v1
```

Expected safe state:

```text
dataset_exists = True
dataset_rows = 0
input_ready_for_processing = False
readiness_state = WAITING_FOR_REAL_EXPORTED_INPUT_FILES
execution_allowed = False
```

This command prepares the operational folder structure.

It does not process evidence.

It does not execute trades.

---

## 5.2 Add exported CSV files manually

Place files manually into:

```text
data/forward_evidence/operational/input/signals/
data/forward_evidence/operational/input/ohlc/
data/forward_evidence/operational/input/price_levels/
```

Do not use exchange connectors.

Do not use automatic execution.

Do not use live alerts.

Do not use API order placement.

---

## 5.3 Validate and adapt files

Run:

```powershell
python -m src.workflows.run_operational_input_file_validator_adapter_v1
```

If no files exist:

```text
adapter_decision = OPERATIONAL_INPUT_WAITING_FOR_FILES
input_ready_for_cycle = False
processing_allowed = False
execution_allowed = False
```

If files are valid:

```text
adapter_decision = OPERATIONAL_INPUT_VALIDATED_READY_FOR_CYCLE
input_ready_for_cycle = True
processing_allowed = True
execution_allowed = False
```

If files are invalid:

```text
adapter_decision = OPERATIONAL_INPUT_VALIDATION_FAILED
input_ready_for_cycle = False
processing_allowed = False
execution_allowed = False
```

Invalid files must be corrected manually before proceeding.

---

## 5.4 Run operational persistent integration

Run:

```powershell
python -m src.workflows.run_operational_persistent_cycle_integration_v1
```

If no valid inputs exist:

```text
integration_decision = OPERATIONAL_INTEGRATION_WAITING_FOR_VALID_INPUTS
dataset_write_performed = False
execution_allowed = False
```

If valid evidence is added:

```text
integration_decision = OPERATIONAL_INTEGRATION_COMPLETED_WITH_EVIDENCE
dataset_write_performed = True
backup_created = True
snapshot_created = True
execution_allowed = False
```

If the same evidence already exists:

```text
integration_decision = OPERATIONAL_INTEGRATION_COMPLETED_NO_DATASET_CHANGES
duplicate_rows_skipped > 0
dataset_write_performed = False
execution_allowed = False
```

---

# 6. Resolution logic

The operational integration resolves observations using OHLC candles after the signal timestamp.

For SHORT observations:

```text
TARGET_HIT if candle low <= target_price
STOP_HIT if candle high >= stop_price
```

For LONG observations:

```text
TARGET_HIT if candle high >= target_price
STOP_HIT if candle low <= stop_price
```

If stop and target are both hit in the same candle, the system uses a conservative assumption:

```text
STOP_HIT first
```

This avoids optimistic backtest bias.

---

# 7. Evidence metrics

Each resolved observation should include:

```text
signal_id
observed_at
symbol
timeframe
signal_type
router_decision
context_name
cost_profile
direction
entry_price
stop_price
target_price
resolution_status
resolution_reason
resolution_timestamp
result_r
mfe_r
mae_r
bars_to_resolution
manual_review_required
resolve_now
source
source_file
price_level_source_file
notes
```

Important metrics:

```text
result_r = theoretical result measured in R
mfe_r = maximum favorable excursion in R
mae_r = maximum adverse excursion in R
bars_to_resolution = number of candles until target or stop resolution
```

---

# 8. Evidence thresholds

Before executed paper trading can be discussed, the project still requires:

```text
minimum 100 resolved forward observations
preferred 300 resolved forward observations
```

These observations must be collected prospectively.

They must not be cherry-picked.

They must include wins, losses, unresolved observations, rejected observations, and duplicate checks.

---

# 9. Required evidence before any future paper-trade execution discussion

Minimum dataset requirements:

```text
100 resolved forward observations
result_r for every resolved observation
MFE / MAE
bars_to_resolution
context_name
cost_profile
direction
router_decision
resolution_status
manual review notes
duplicate protection
blocked / rejected records
```

Preferred dataset requirements:

```text
300 resolved forward observations
performance by context
performance by cost profile
performance by direction
performance by volatility regime
performance by MTF state
performance by Elliott context
performance by skipped / blocked states
```

---

# 10. What Phase 5 allows

```text
manual export of CSV files
schema validation
operational evidence ingestion
forward observation generation
OHLC-based theoretical resolution
dataset persistence
backup and snapshot creation
duplicate protection
manual review
evidence accumulation
```

---

# 11. What Phase 5 does not allow

```text
real capital
executed paper trading
live alerts
exchange execution
Binance execution
Quantfury execution
automatic order placement
autonomous bot behavior
```

---

# 12. Failure handling

## 12.1 If no files are present

Expected state:

```text
OPERATIONAL_INPUT_WAITING_FOR_FILES
OPERATIONAL_INTEGRATION_WAITING_FOR_VALID_INPUTS
```

Action:

```text
Do nothing.
Wait for real exported CSV files.
```

---

## 12.2 If validation fails

Expected state:

```text
OPERATIONAL_INPUT_VALIDATION_FAILED
OPERATIONAL_INTEGRATION_BLOCKED_BY_INPUT_VALIDATION
```

Action:

```text
Do not run persistence.
Review rejected file report.
Fix CSV structure manually.
Run validator again.
```

---

## 12.3 If evidence already exists

Expected state:

```text
OPERATIONAL_INTEGRATION_COMPLETED_NO_DATASET_CHANGES
duplicate_rows_skipped > 0
```

Action:

```text
Do not edit dataset manually.
Confirm duplicate was expected.
Continue with new evidence only.
```

---

## 12.4 If execution flag becomes True

Expected state:

```text
invalid operational flow
```

Action:

```text
Stop immediately.
Do not continue evidence collection.
Review source module.
Restore all execution flags to False.
```

---

# 13. Git policy

Generated operational data must not be committed.

Ignored operational paths:

```text
data/forward_evidence/operational/
reports/operational_forward_evidence_bootstrap_v1/
reports/operational_input_file_validator_adapter_v1/
reports/operational_persistent_cycle_integration_v1/
reports/phase_5_operational_evidence_closure_v1/
```

Source code and documentation should be committed.

Operational CSV inputs, datasets, backups, and snapshots should not be committed.

---

# 14. Manual review policy

Every operational observation requires manual review.

The project can calculate theoretical evidence, but it cannot decide to trade.

The user must review:

```text
context_name
cost_profile
direction
entry_price
stop_price
target_price
resolution_status
result_r
mfe_r
mae_r
bars_to_resolution
notes
```

Manual review is required because this is still evidence collection, not execution.

---

# 15. Final Phase 5 operating rule

If the system has fewer than 100 resolved forward observations, the strategy remains in evidence collection mode.

If a file fails validation, it must not enter the persistent dataset.

If a duplicate signal is detected, it must not be written again.

If any execution flag becomes True, the operational flow must be considered invalid.

Phase 5 is complete when the runbook, closure document, required source files, and closure validator all pass validation.

The system is still not a trading bot.

The system is now an evidence machine.
