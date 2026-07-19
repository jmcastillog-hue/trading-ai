# PHASE 10 LONG FORWARD OBSERVATION EVIDENCE COLLECTION OFFICIAL DATASET ATOMIC WRITE HARNESS DESIGN

## Status

Phase 10.42 defines the design of a future atomic-write harness for the official LONG forward-observation evidence dataset.

This phase is design-only and report-only. It does not implement, instantiate or execute the harness. It does not create, replace, promote, populate or write the official dataset.

## Source authority

The design depends on the validated Phase 10.41 empty-schema candidate:

`data/forward/candidates/long_forward_observation_dataset_v1.empty_candidate.csv`

The candidate must remain:

- tracked by Git
- clean
- 981 bytes
- UTF-8 without BOM
- LF-only
- one physical header line
- 54 canonical columns
- zero evidence rows
- SHA-256 `e3fa86a461fd46f4d66dc2e03f185e49b7b3438d3cbc33340c01f51310514ff1`

## Purpose

The future harness is intended to provide a controlled mechanism for creating or replacing an official dataset artifact without exposing readers to partial writes.

The design covers:

- preflight gates
- canonical source validation
- path isolation
- exclusive lock acquisition
- same-directory temporary staging
- deterministic byte generation
- file flush and `fsync`
- staged artifact verification
- atomic replacement
- parent-directory durability
- manifest sequencing
- rollback and recovery
- stale-lock handling
- crash-consistency states
- audit evidence
- explicit fail-closed behavior

## Design boundary

Phase 10.42 only defines contracts, states, invariants and failure responses.

It does not allow:

- candidate modification
- candidate promotion
- official dataset implementation
- official dataset creation
- official dataset replacement
- official dataset writes
- temporary official staging files
- lock files
- official manifests
- backups
- evidence rows
- evidence collection
- evidence persistence
- signals
- live alerts
- paper trading
- LONG approval
- real capital
- market or exchange execution
- automation

## Atomicity model

The future implementation must:

1. validate all source and safety gates before acquiring a lock
2. acquire an exclusive lock using create-if-absent semantics
3. write a unique temporary file in the official dataset directory
4. flush and `fsync` the temporary file
5. validate exact schema, bytes, rows and digest
6. atomically replace the target using an operating-system rename/replace primitive
7. `fsync` the parent directory when supported
8. write or update the manifest only after the dataset replacement is durable
9. remove temporary and lock artifacts in controlled cleanup
10. fail closed whenever durability or integrity cannot be established

## Crash consistency

The design distinguishes these states:

- no lock, no temp, no official dataset
- lock acquired
- temp created
- temp durable
- temp validated
- target atomically replaced
- parent directory durable
- manifest durable
- cleanup complete
- failed before replacement
- failed after replacement but before manifest
- recovery required

No state permits silent continuation after an unknown durability outcome.

## Passing decision

`CONTROLLED_FORWARD_OBSERVATION_EVIDENCE_COLLECTION_OFFICIAL_DATASET_ATOMIC_WRITE_HARNESS_DESIGN_READY_FOR_DESIGN_REVIEW`

## Blocked decision

`CONTROLLED_FORWARD_OBSERVATION_EVIDENCE_COLLECTION_OFFICIAL_DATASET_ATOMIC_WRITE_HARNESS_DESIGN_BLOCKED`

## Expected validation decision

`PHASE_10_42_LONG_FORWARD_OBSERVATION_EVIDENCE_COLLECTION_OFFICIAL_DATASET_ATOMIC_WRITE_HARNESS_DESIGN_VALIDATED`

## Recommended next phase

Phase 10.43 — LONG Forward Observation Evidence Collection Official Dataset Atomic Write Harness Design Review V1

## Safety statement

A passing Phase 10.42 permits only a future review of this design.

It does not authorize implementation or any write to the official dataset.
