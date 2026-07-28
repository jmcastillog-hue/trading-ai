# Phase 10.45 — Controlled empty initialization of the official LONG dataset

## Status and boundary

Phase 10.45 adds the authorization boundary and controlled create-only entry point needed for a future one-time initialization of the official empty LONG observation dataset. Phase 10.44 remains the validated atomic-write foundation.

Gate A implements and validates only. Official writing is blocked by default and requires a separate explicit Gate B authorization. The Gate A workflow cannot activate Gate B and never initializes the official dataset.

## Frozen candidate

- Canonical candidate: `data/forward/candidates/long_forward_observation_dataset_v1.empty_candidate.csv`
- SHA-256: `e3fa86a461fd46f4d66dc2e03f185e49b7b3438d3cbc33340c01f51310514ff1`
- Size: 981 bytes
- Schema: 54 columns
- Evidence rows: 0
- Encoding: UTF-8 without BOM, LF-only, one final LF

## Official artifacts

- Dataset: `data/forward/long_forward_observation_dataset_v1.csv`
- Manifest: `data/forward/long_forward_observation_dataset_v1.manifest.csv`
- Lock: `data/forward/long_forward_observation_dataset_v1.lock`
- Unique same-directory temporaries: `<artifact>.tmp.<operation_id>`

A fresh preflight must find the dataset, manifest, lock, matching temporaries and backup patterns absent. Any residual blocks initialization. Preexistence or a concurrent publication fails closed; replacement is never allowed.

## Publication contract

The implementation validates the candidate, acquires an exclusive durable lock, writes and fsyncs a unique target temporary, publishes the target with the Phase 10.44 create-only atomic primitive, writes and fsyncs a unique manifest temporary, publishes the manifest only after the target, verifies the committed pair and then releases the owned lock. `COMMITTED_CLEAN` is returned only after the pair is verified and lock/temporary residue is absent.

Before target publication, the verified operation may clean only its own temporaries and owned lock. After target publication there is no automatic deletion, replacement, resume or repair. Residual state is preserved for human inspection.

## Failure injection and negative controls

The isolated suite covers missing or incorrect Gate B authorization; preexisting target, manifest and lock; residual temporary and backup; malformed candidate hash, size, columns or rows; replacement and second-run prohibition; concurrent publication; failures after lock, target temporary, target publication, manifest temporary and manifest publication; wrong lock owner; manifest tampering; official-path rejection in isolated mode; and permanent trading-effect denial.

## Safety invariants

All signal generation, live alerts, paper-trade execution, real capital, market or exchange execution, automation and execution permissions remain false. The dataset contains zero evidence rows. There is no network access, exchange access, OpenClaw operational action or autonomous recovery.

## Gate sequence

1. Gate A implementation and isolated validation.
2. Separate human approval for Gate B after a fresh read-only official preflight.
3. One create-only official initialization using the exact reviewed entry point and command.
4. Independent verification of the committed pair.
5. Commit, merge and push remain three separate later approvals.

A passing Gate A does not close Phase 10.45 and does not authorize official initialization.
