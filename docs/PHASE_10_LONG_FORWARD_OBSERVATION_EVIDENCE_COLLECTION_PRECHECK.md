# PHASE 10 LONG FORWARD OBSERVATION EVIDENCE COLLECTION PRECHECK

## Status

Phase 10.28 defines and validates the LONG forward observation evidence collection precheck.

This phase performs a precheck only.

This phase does not enable evidence collection, create or write the official evidence dataset, record real forward signals, generate live signals, enable alerts, enable paper trading, approve the LONG research candidate for execution, approve real capital, permit market or exchange execution, enable automation, or complete the project.

## Purpose

Phase 10.26 opened the controlled forward observation state.

Phase 10.27 verified the integrity of that start output and allowed only a future evidence collection precheck.

Phase 10.28 verifies whether the control plane is ready to proceed to a future evidence collection design phase.

The objectives are:

- verify the Phase 10.27 validation passed
- verify the Phase 10.27 output integrity review was performed and passed
- verify the Phase 10.27 decision is the expected precheck-ready decision
- verify the required source artifacts exist, are non-empty, have valid SHA-256 hashes and remain stable during the precheck
- verify the preserved Phase 10.26 start output still contains exactly one row with the expected 57-column schema
- verify the candidate remains `LONG_BASE_FAILED_BREAKDOWN_V1`
- verify direction remains `LONG`
- verify the LONG price structure and risk/reward 2.5
- verify the controlled observation state remains started
- verify all evidence, signal, alert, paper-trading, capital and execution locks remain active
- verify official evidence rows remain zero and the official dataset remains absent
- verify no duplicate start run is performed
- define the minimum requirements for a future evidence collection design
- permit only a future evidence collection design phase

## Evidence collection design requirements

A future design phase must define at minimum:

- accepted observation source
- timestamp and timezone requirements
- candidate identity, direction, symbol and timeframe requirements
- entry, stop, target, invalidation and risk/reward requirements
- evidence identity and deduplication rules
- observation lifecycle and review states
- rejection rules
- write-ahead validation
- official dataset schema and write guard
- evidence hash, provenance and audit trail
- manual confirmation
- rollback and recovery behavior
- no-signal-generation boundary
- no-execution boundary

Phase 10.28 defines these requirements but does not implement evidence collection.

## Required precheck state

The following must be true:

- `long_forward_observation_evidence_collection_precheck_defined = True`
- `phase_10_27_validation_passed = True`
- `source_output_integrity_review_performed = True`
- `source_output_integrity_review_passed = True`
- `source_output_integrity_review_decision = CONTROLLED_FORWARD_OBSERVATION_START_RUN_OUTPUT_INTEGRITY_REVIEW_READY_FOR_EVIDENCE_COLLECTION_PRECHECK`
- `source_future_evidence_collection_precheck_allowed = True`
- `source_artifacts_exist = True`
- `source_artifacts_non_empty = True`
- `source_artifact_hashes_valid = True`
- `source_artifacts_stable_during_precheck = True`
- `source_start_output_row_count = 1`
- `source_start_output_schema_valid = True`
- `source_candidate_valid = True`
- `source_direction_valid = True`
- `source_price_structure_valid = True`
- `source_risk_reward_valid = True`
- `source_observation_state_started = True`
- `source_start_state_fields_valid = True`
- `source_operational_locks_valid = True`
- `source_official_evidence_rows_zero = True`
- `official_dataset_absent = True`
- `no_duplicate_start_run = True`
- `evidence_collection_remains_disabled = True`
- `evidence_collection_design_requirements_defined = True`
- `evidence_collection_precheck_performed = True`
- `evidence_collection_precheck_passed = True`
- `future_evidence_collection_design_allowed = True`

The following must remain false or zero:

- `new_controlled_forward_observation_start_run_performed = False`
- `new_controlled_forward_observation_start_performed = False`
- `evidence_collection_enabled = False`
- `evidence_collection_started = False`
- `official_dataset_write_allowed = False`
- `official_dataset_write_performed = False`
- `real_forward_dataset_created = False`
- `official_evidence_rows_written = 0`
- `real_forward_signals_recorded = False`
- `journal_real_rows_accepted = False`
- `accepted_as_real_evidence = False`
- `evidence_persistence_allowed = False`
- `evidence_write_performed = False`
- `signal_generation_enabled = False`
- `live_alerts_allowed = False`
- `paper_trading_enabled = False`
- `long_strategy_approved = False`
- `long_entries_approved = False`
- `long_side_established = False`
- `paper_trade_execution_allowed = False`
- `real_capital_allowed = False`
- `market_execution_allowed = False`
- `exchange_execution_allowed = False`
- `automation_allowed = False`
- `execution_allowed = False`
- `real_entries_approved = False`
- `total_project_completed = False`

## Precheck decisions

Phase 10.28 may produce only:

- `CONTROLLED_FORWARD_OBSERVATION_EVIDENCE_COLLECTION_PRECHECK_READY_FOR_EVIDENCE_COLLECTION_DESIGN`
- `CONTROLLED_FORWARD_OBSERVATION_EVIDENCE_COLLECTION_PRECHECK_BLOCKED`

A ready decision permits only a future evidence collection design phase. It does not enable evidence collection, official dataset writes, signals, alerts, paper trading, real capital or market execution.

## Expected validation decision

`PHASE_10_28_LONG_FORWARD_OBSERVATION_EVIDENCE_COLLECTION_PRECHECK_VALIDATED`

## Recommended next phase

Phase 10.29 — LONG Forward Observation Evidence Collection Design V1
