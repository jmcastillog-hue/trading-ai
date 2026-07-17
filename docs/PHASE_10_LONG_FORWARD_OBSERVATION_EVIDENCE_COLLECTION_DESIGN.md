# PHASE 10 LONG FORWARD OBSERVATION EVIDENCE COLLECTION DESIGN

## Status

Phase 10.29 defines and validates the LONG forward observation evidence collection design.

This phase is design-only. It writes only design and validation artifacts under `reports/`.

This phase does not enable evidence collection, collect real forward evidence, create or write the official evidence dataset, record real forward signals, generate alerts, enable paper trading, approve the LONG strategy, use real capital, execute orders, enable automation, or complete the project.

## Purpose

Phase 10.28 completed the evidence collection precheck and allowed only a future evidence collection design phase.

Phase 10.29 converts the twenty precheck requirements into a concrete machine-readable design contract.

The design defines:

- a 54-field future evidence schema
- accepted observation sources
- UTC timestamp and provenance requirements
- candidate, direction, symbol and timeframe requirements
- LONG price-structure and risk/reward rules
- evidence identity and deduplication rules
- lifecycle and review states
- evidence rejection rules
- write-ahead validations
- official dataset write guards
- evidence hash and provenance fields
- audit-trail requirements
- manual-confirmation requirements
- rollback and recovery behavior
- no-signal and no-execution boundaries

## Design-only boundary

A passed design means only that the future evidence collection mechanism has a documented contract.

It does not mean that evidence collection is enabled, real observations may be accepted, evidence may be persisted, the official dataset may be created or written, signals or alerts may be produced, paper trading is enabled, the LONG strategy is approved, capital may be used, or execution is allowed.

## Evidence schema

The schema contains 54 fields covering identity, provenance, timestamps, market identity, LONG price structure, risk/reward, lifecycle, review, deduplication, validation, audit, rollback and safety locks.

The schema is written only as a report artifact. It is not the official evidence dataset.

## Accepted observation sources

The future source allowlist is:

- `SYSTEM_FORWARD_OBSERVATION_CANDIDATE_DETECTOR`
- `MANUAL_RESEARCH_REVIEW`
- `CONTROLLED_MARKET_DATA_SNAPSHOT`

Every future source must include a source identifier, artifact reference, SHA-256, row hash, UTC timestamps, candidate identity, symbol, timeframe and provenance status.

## Lifecycle design

The future lifecycle is:

1. `CAPTURE_PENDING`
2. `CAPTURED_UNVALIDATED`
3. `VALIDATION_REJECTED`
4. `VALIDATED_PENDING_REVIEW`
5. `REVIEW_REJECTED`
6. `REVIEW_APPROVED_PENDING_PERSISTENCE`
7. `PERSISTENCE_BLOCKED`
8. `PERSISTED_OFFICIAL`

Phase 10.29 defines these states only. It does not transition any real observation through them.

## Required design state

The following must be true:

- `long_forward_observation_evidence_collection_design_defined = True`
- `phase_10_28_validation_passed = True`
- `source_evidence_collection_precheck_performed = True`
- `source_evidence_collection_precheck_passed = True`
- `source_evidence_collection_precheck_decision = CONTROLLED_FORWARD_OBSERVATION_EVIDENCE_COLLECTION_PRECHECK_READY_FOR_EVIDENCE_COLLECTION_DESIGN`
- `source_future_evidence_collection_design_allowed = True`
- source artifacts exist, are non-empty, hashed and stable
- source design requirements contain 20 valid unimplemented requirements
- the controlled observation state remains started
- candidate, direction, LONG price structure and R/R 2.5 remain valid
- the 54-field evidence schema is valid
- all design components, source rules, lifecycle states, deduplication rules, rejection rules, write guards, audit requirements and boundaries are valid
- `evidence_collection_design_performed = True`
- `evidence_collection_design_passed = True`
- `future_evidence_collection_design_review_allowed = True`

The following must remain false or zero:

- new start run or start performed
- evidence collection enabled or started
- official dataset schema implemented
- official dataset write allowed or performed
- real forward dataset created
- official evidence rows written
- real signals or journal rows accepted
- evidence persistence or write performed
- signal generation or alerts
- paper trading
- LONG strategy, entries or side approval
- real capital
- market or exchange execution
- automation or execution
- real entries
- total project completion

## Design decisions

Phase 10.29 may produce only:

- `CONTROLLED_FORWARD_OBSERVATION_EVIDENCE_COLLECTION_DESIGN_READY_FOR_DESIGN_REVIEW`
- `CONTROLLED_FORWARD_OBSERVATION_EVIDENCE_COLLECTION_DESIGN_BLOCKED`

A ready decision permits only a future design review.

## Expected validation decision

`PHASE_10_29_LONG_FORWARD_OBSERVATION_EVIDENCE_COLLECTION_DESIGN_VALIDATED`

## Recommended next phase

Phase 10.30 — LONG Forward Observation Evidence Collection Design Review V1
