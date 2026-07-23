# Phase 10.44 — LONG Official Dataset Create-Only Atomic-Write Harness Implementation V1

## Status

Phase 10.44 implements the create-only atomic-write harness authorized by Phase 10.43.

Source review commit: `d5c5acefcc1f965566c20cb4d21bf62144d9a827`

Source review root: `31575687b9439397a920d4cb960c572abd07c00e05148feeb1a1d9dc269552ac`

The implementation is exercised only in isolated temporary test directories. It does not create, replace or modify the official dataset.

## Implemented boundary

The harness verifies the exact 981-byte, 54-column, zero-row candidate; requires a sandbox outside the repository; creates an exclusive ownership lock; creates unique same-directory target and manifest temporaries; flushes and fsyncs staged files; publishes through a create-only atomic primitive; commits the manifest only after target durability; verifies the committed pair; and removes the lock only after success.

Windows uses `MoveFileExW` with `MOVEFILE_WRITE_THROUGH` and without the replace-existing flag. POSIX uses hard-link create-only publication followed by directory `fsync`. Unsupported or failed durability primitives fail closed.

Before target publication, the verified owner may clean its own temporary files and lock. After target publication, the harness performs no automatic deletion, resume or repair. Residual state is left for explicit human inspection.

## Failure injection points

The isolated test harness supports these test-only failpoints:

- `AFTER_LOCK_ACQUIRED`
- `AFTER_TARGET_TEMP_DURABLE`
- `AFTER_TARGET_PUBLISHED`
- `AFTER_MANIFEST_TEMP_DURABLE`
- `AFTER_MANIFEST_PUBLISHED`

## Explicit prohibitions

Phase 10.44 may not write `data/forward/long_forward_observation_dataset_v1.csv`, replace an existing target, append evidence, create backups, open lockboxes, generate signals or alerts, execute paper trades, use real capital, access an exchange, automate trading or invoke OpenClaw operationally.

## Passing decision

`PHASE_10_44_LONG_FORWARD_OBSERVATION_EVIDENCE_COLLECTION_OFFICIAL_DATASET_ATOMIC_WRITE_HARNESS_IMPLEMENTATION_VALIDATED`

Passing validates the harness in temporary fixtures only. It does not initialize the official dataset.

## Next phase

`PHASE_10_45_LONG_FORWARD_OBSERVATION_EVIDENCE_COLLECTION_OFFICIAL_DATASET_CONTROLLED_EMPTY_INITIALIZATION_V1`

Phase 10.45 may perform one controlled create-only initialization of the official empty dataset only after a fresh preflight confirms the target, manifest, lock, fixed temp and backup artifacts are absent. The expected evidence row count remains zero. Paper trading, real capital, signals, alerts, exchange execution and automation remain disabled.
