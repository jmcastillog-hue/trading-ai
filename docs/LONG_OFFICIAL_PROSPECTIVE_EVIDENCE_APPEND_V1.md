# LONG Official Prospective Evidence Append V1

## Status

This increment implements the first authoritative append boundary for the official
54-column LONG prospective evidence dataset.

The implementation is validated only against copied dataset/manifest pairs in an
external sandbox. It does **not** append an official evidence row during installation,
validation or closure.

## Purpose

The repository already contains candidate detection, record construction, manual
review adapters and generic operational persistence. Those components use older
journal/operational schemas and are not permitted to write the official dataset.

This capability adds the missing boundary:

```text
human-reviewed LONG observation
        ↓
canonical 54-column evidence event
        ↓
provenance, schema and risk validation
        ↓
deduplication and evidence-hash chaining
        ↓
complete candidate dataset + append manifest
        ↓
exclusive lock and durable same-directory temporaries
        ↓
transactional dataset/manifest replacement
        ↓
post-write verification or certified rollback
```

## Canonical evidence contract

Every accepted row must:

- contain exactly the official 54 columns in canonical order;
- be `LONG` and reference one of the frozen LONG research candidates;
- use a valid `stop < entry < target` structure with RR exactly `2.5`;
- bind to a source artifact SHA-256 and source-row SHA-256;
- carry an event-specific deduplication key;
- chain `previous_evidence_hash` to the preceding official event;
- carry a deterministic `evidence_hash` over the complete row except the hash field;
- require and record affirmative human confirmation;
- pass write-ahead, schema, provenance and risk-structure validation;
- set `accepted_as_real_evidence`, `official_dataset_write_allowed` and
  `evidence_persistence_allowed` to true only for that reviewed append event;
- keep signal generation, live alerts, paper trading, capital, market/exchange
  execution, automation and general execution false.

The dataset is append-only at the evidence-event level. A later resolution is a new
event and must not silently mutate an earlier row.

## Manifest V2

After the first controlled append, the official manifest transitions from the
Phase 10.45 empty create-only schema to:

```text
LONG_OFFICIAL_DATASET_APPEND_MANIFEST_V2
```

It binds:

- previous dataset and manifest hashes;
- previous and resulting evidence-row counts;
- resulting dataset hash, size and schema;
- the appended evidence ID, evidence hash and deduplication key;
- the exact publication primitive;
- append-only and human-review requirements;
- all execution permissions as false.

## Transaction and rollback model

The writer:

1. validates the current committed pair before locking;
2. acquires an exclusive ownership lock;
3. verifies that neither committed artifact changed after the lock;
4. builds and validates the complete next dataset and manifest in memory;
5. durably stages dataset, manifest and rollback copies in the same directory;
6. replaces the dataset and manifest using write-through/`fsync` primitives;
7. validates the committed pair;
8. removes rollback copies and releases the owned lock.

If a failure occurs after either replacement, the owned operation restores the
exact previous bytes and verifies both hashes before releasing the lock. The
read-only connection fails closed whenever the lock is present, preventing it from
reporting an intermediate pair.

This is a locked transactional pair update, not a claim that two independent files
can be replaced by one filesystem atomic instruction.

## Official-write gate

`append_official_prospective_evidence()` requires both:

- the exact in-process authorization token; and
- `TRADING_AI_OFFICIAL_LONG_EVIDENCE_APPEND_ALLOWED=1`.

The validator never enables that environment gate and verifies that an official
append attempt remains blocked. There is no CLI that performs an official append in
this increment.

## Read-only compatibility

`openclaw_read_only_local_connection_v1` now validates both:

- the original empty `LONG_OFFICIAL_DATASET_MANIFEST_V1`; and
- a future non-empty `LONG_OFFICIAL_DATASET_APPEND_MANIFEST_V2` pair.

OpenClaw remains read-only and non-actionable in both states.

## Fail-closed correction

The operational persistent-cycle integration previously set
`execution_allowed=True` when prohibited execution flags were detected. The failure
decision was correct, but the flag was semantically contradictory. This increment
forces `execution_allowed=False` and adds a behavioral regression test.

## Validation scope

Validation includes:

- successful one-row append in an external sandbox;
- duplicate-event rejection;
- non-LONG, unconfirmed and invalid-RR rejection;
- evidence-hash and manifest-permission tamper rejection;
- lock contention and read-during-lock rejection;
- rollback after dataset replacement;
- rollback after manifest replacement;
- read-only validation of a non-empty Manifest V2 pair;
- regression coverage for the operational fail-closed flag;
- the existing OpenClaw Phase 11.1–11.6 tests;
- verification that the official dataset and manifest remain byte-identical.

## Still prohibited

This capability does not authorize:

- the first official evidence append;
- automatic candidate promotion;
- signal generation or actionable alerts;
- paper trading;
- real capital;
- Binance or Quantfury execution;
- browser control;
- external messaging;
- autonomous recovery;
- OpenClaw write access.

## Closure condition

The increment may close only when all tests and sandbox controls pass, the Git scope
is exact, and the official dataset remains at zero rows with its Phase 10.45 hashes
unchanged.
