# Phase 10.43 — LONG Official Dataset Atomic-Write Harness Final Design Review V1

## Decision

This is the final design review before implementation. It is not an additional
OpenClaw review and it does not authorize an official dataset write.

Source Phase 10.42 commit:

`40d1c3720a398dad7751fb45212edb91f7f914ce`

Review root:

`31575687b9439397a920d4cb960c572abd07c00e05148feeb1a1d9dc269552ac`

Passing decision:

`PHASE_10_43_LONG_FORWARD_OBSERVATION_EVIDENCE_COLLECTION_OFFICIAL_DATASET_ATOMIC_WRITE_HARNESS_DESIGN_REVIEW_VALIDATED`

Next phase:

`PHASE_10_44_LONG_FORWARD_OBSERVATION_EVIDENCE_COLLECTION_OFFICIAL_DATASET_ATOMIC_WRITE_HARNESS_IMPLEMENTATION_V1`

The next phase is implementation, not another review.

## Material clarifications resolved

The Phase 10.42 architecture is sound, but three implementation ambiguities
needed binding resolution:

1. The design requires a unique same-directory temp file while an earlier path
   constant exposes a fixed `.tmp` name. The fixed path is a naming anchor only;
   implementations must derive a unique create-exclusive temp path per operation.
2. The target is atomic, but the manifest must also be committed atomically.
   Directly writing the final manifest path is prohibited.
3. Replacement and rollback are broader than the immediate MVP. Phase 10.44 is
   constrained to create-only empty initialization in temporary test
   directories. An existing target must fail closed. The first controlled
   official creation is reserved for Phase 10.45.

## Binding amendments

### R43-A1 — Unique temp path template

The target and temp must share a parent. The temp name includes an unpredictable
operation identifier and is opened create-exclusive. The fixed `.tmp` path may
not be used as the actual staging file.

### R43-A2 — Atomic manifest commit

After target durability is established, the manifest is generated
deterministically, staged to its own unique same-directory temp, flushed,
fsynced, verified, atomically replaced and passed through the selected directory
durability barrier.

### R43-A3 — Create-only implementation scope

Phase 10.44 implements and tests only target-absent empty initialization in
temporary directories. It must not mutate the official dataset path and must
reject an existing target. Dataset replacement and evidence append are outside
10.44.

### R43-A4 — Platform durability adapter

The implementation must select a supported platform-specific durability path
and record which primitive was used. A failed or unsupported required barrier
must block the operation. Silent best-effort fallback is prohibited.

### R43-A5 — Lock record

The exclusive lock contains operation id, process id, host, start time,
candidate digest, canonical target path and phase. Only the verified owner may
remove it.

### R43-A6 — No automatic recovery

Age alone never authorizes stale-lock deletion. Phase 10.44 may classify
recovery states but may not automatically resume, delete or mutate unowned
artifacts.

## Phase 10.44 acceptance boundary

Phase 10.44 may:

- implement the create-only harness;
- run it only inside isolated temporary test directories;
- test successful empty initialization;
- test failure before and after each commit boundary;
- verify exact candidate bytes, 54 columns and zero rows;
- test lock contention and residual-artifact classification.

Phase 10.44 may not:

- run against `data/forward/long_forward_observation_dataset_v1.csv`;
- replace an existing dataset;
- append evidence;
- open either lockbox;
- generate signals or alerts;
- enable paper trading, real capital, exchange execution or automation.

## Phase 10.45 boundary

Only after 10.44 passes may Phase 10.45 perform one controlled initialization of
the official empty dataset. The expected row count remains zero.

## Roadmap status

This review is on the critical path because it resolves the persistence
boundary. It closes the design-review step. No Phase 10.43R review is authorized
by default. A repair is allowed only for a reproducible material defect.

The project is not complete.
