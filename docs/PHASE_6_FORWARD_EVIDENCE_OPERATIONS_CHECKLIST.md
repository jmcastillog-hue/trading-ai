# PHASE 6 FORWARD EVIDENCE OPERATIONS CHECKLIST

## Status

Phase 6 starts the controlled operational evidence collection stage of the Trading-AI / OpenClaw project.

Phase 6 does not authorize trade execution.

Phase 6 does not authorize paper trading execution.

Phase 6 does not authorize live alerts.

Phase 6 does not authorize exchange execution.

Phase 6 is focused on using the Phase 5 operational evidence layer with real manually exported CSV files.

## Core operating principle

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

All execution flags must remain:

```text
paper_trade_execution_allowed = False
real_capital_allowed = False
live_alerts_allowed = False
exchange_execution_allowed = False
automation_allowed = False
execution_allowed = False
```

If any execution flag becomes `True`, the operational run must be considered invalid.

---

# 1. Purpose of Phase 6.1

Phase 6.1 defines the manual operations checklist for forward evidence collection.

The checklist exists to make sure every real evidence run is controlled, reproducible, reviewable, and safe.

Each operational run should answer:

```text
What files were loaded?
Were they validated?
How many signals were processed?
How many observations were created?
How many were resolved?
How many remain open?
How many were rejected?
How many were duplicates?
Was the dataset updated?
Was a backup created?
Was a snapshot created?
Did all execution flags remain False?
```

---

# 2. Required preconditions before each operational run

Before running the operational evidence pipeline, confirm:

```text
Project is on the correct branch.
Working tree is clean or intentional changes are understood.
Phase 5 runbook exists.
Phase 5 closure document exists.
Operational dataset exists.
Operational input directories exist.
CSV files were exported manually.
No exchange connector is active.
No live alert system is active.
No order execution path is active.
```

Required operational folders:

```text
data/forward_evidence/operational/
data/forward_evidence/operational/input/signals/
data/forward_evidence/operational/input/ohlc/
data/forward_evidence/operational/input/price_levels/
data/forward_evidence/operational/backups/
data/forward_evidence/operational/snapshots/
data/forward_evidence/operational/templates/
```

Required operational dataset:

```text
data/forward_evidence/operational/forward_evidence_dataset_v1.csv
```

---

# 3. Required manual CSV files

Each real operational run should use manually exported CSV files.

## 3.1 Signals file

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

Checklist:

```text
observed_at is correct.
symbol is correct.
timeframe is correct.
signal_type is correct.
router_decision is WATCH_ONLY, BLOCKED, SKIP, or REVIEW_ONLY.
cost_profile is correct.
context_name is correct.
direction is LONG or SHORT.
manual_review_required is True.
notes are present when needed.
```

## 3.2 OHLC file

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

Checklist:

```text
timestamp is correct.
open, high, low, close are numeric.
volume is non-negative.
symbol matches the signal.
timeframe matches the signal.
OHLC structure is consistent.
OHLC data is after the observed_at timestamp.
```

## 3.3 Price levels file

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

Checklist:

```text
context_name matches the signal context.
cost_profile matches the signal cost profile.
direction matches the signal direction.
entry_price is numeric and positive.
stop_price is numeric and positive.
target_price is numeric and positive.
SHORT structure: stop_price > entry_price > target_price.
LONG structure: stop_price < entry_price < target_price.
```

---

# 4. Safe operational sequence

## 4.1 Bootstrap operational environment

Run:

```powershell
python -m src.workflows.run_operational_forward_evidence_bootstrap_v1
```

Expected safe state:

```text
dataset_exists = True
input_ready_for_processing = False
readiness_state = WAITING_FOR_REAL_EXPORTED_INPUT_FILES
execution_allowed = False
```

## 4.2 Validate operational input files

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

Do not continue if validation fails.

## 4.3 Run operational persistent integration

Run:

```powershell
python -m src.workflows.run_operational_persistent_cycle_integration_v1
```

If no valid input exists:

```text
integration_decision = OPERATIONAL_INTEGRATION_WAITING_FOR_VALID_INPUTS
dataset_write_performed = False
execution_allowed = False
```

If new evidence is added:

```text
integration_decision = OPERATIONAL_INTEGRATION_COMPLETED_WITH_EVIDENCE
dataset_write_performed = True
backup_created = True
snapshot_created = True
execution_allowed = False
```

If only duplicates are found:

```text
integration_decision = OPERATIONAL_INTEGRATION_COMPLETED_NO_DATASET_CHANGES
duplicate_rows_skipped > 0
dataset_write_performed = False
execution_allowed = False
```

---

# 5. Required run log after each operational run

After each run, record:

```text
run_date
operator
branch
latest_commit
signal_files_found
ohlc_files_found
price_level_files_found
adapted_signal_rows
adapted_ohlc_rows
adapted_price_level_rows
generated_observations
rejected_observations
closed_observations
open_observations
error_observations
wins
losses
new_rows_added
updated_rows
duplicate_rows_skipped
invalid_rows
dataset_rows_after
dataset_write_required
dataset_write_performed
backup_created
snapshot_created
execution_allowed
adapter_decision
integration_decision
manual_review_notes
```

---

# 6. Required review after each run

Review the generated outputs:

```text
reports/operational_input_file_validator_adapter_v1/
reports/operational_persistent_cycle_integration_v1/
```

Review the operational dataset:

```text
data/forward_evidence/operational/forward_evidence_dataset_v1.csv
```

Review backups and snapshots if the dataset changed:

```text
data/forward_evidence/operational/backups/
data/forward_evidence/operational/snapshots/
```

---

# 7. Evidence thresholds

The project remains in evidence collection mode until it reaches:

```text
minimum 100 resolved forward observations
preferred 300 resolved forward observations
```

Before any future paper-trade execution discussion, the project must have:

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
rejected records
duplicate checks
blocked or skipped records
```

Preferred evidence:

```text
300 resolved forward observations
performance by context
performance by cost profile
performance by direction
performance by volatility regime
performance by MTF state
performance by Elliott context
performance by skipped / blocked state
```

---

# 8. Failure handling

## 8.1 Validation failure

If the adapter reports validation failure:

```text
Do not run persistence.
Open rejected file report.
Correct CSV manually.
Run validator again.
```

## 8.2 Duplicate-only run

If the integration reports duplicate-only:

```text
Do not edit dataset manually.
Confirm duplicate detection was expected.
Add only genuinely new evidence in the next run.
```

## 8.3 Open observations

If observations remain open:

```text
Do not force resolution.
Wait for future OHLC.
Run integration again when additional OHLC is available.
```

## 8.4 Execution flag violation

If any execution flag becomes True:

```text
Stop immediately.
Do not continue the operational run.
Review the module that produced the flag.
Restore all execution flags to False.
Treat the run as invalid.
```

---

# 9. What Phase 6.1 allows

```text
manual operational evidence collection
manual CSV export ingestion
schema validation
forward observation generation
theoretical OHLC-based resolution
dataset persistence
backup and snapshot review
duplicate detection
manual review
progress tracking toward 100 / 300 resolved observations
```

---

# 10. What Phase 6.1 does not allow

```text
real capital
paper trading execution
live alerts
Binance execution
Quantfury execution
exchange execution
automatic order placement
autonomous trading bot behavior
```

---

# 11. Phase 6.1 validation decision

Phase 6.1 is valid only if:

```text
Phase 5 runbook exists.
Phase 5 closure document exists.
Phase 6 operations checklist exists.
Operational evidence commands are documented.
Evidence thresholds are documented.
Hard restrictions are documented.
Execution flags remain False.
```

Expected validation decision:

```text
PHASE_6_1_FORWARD_EVIDENCE_OPERATIONS_CHECKLIST_VALIDATED
```

---

# 12. Final operating rule

Every forward evidence run must be reproducible, reviewable, and non-executing.

The project remains in evidence collection mode until the minimum forward sample is reached.

The system is still not a trading bot.

The system is now collecting operational evidence.
