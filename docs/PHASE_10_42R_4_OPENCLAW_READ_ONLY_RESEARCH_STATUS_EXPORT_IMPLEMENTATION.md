# Phase 10.42R.4 — OpenClaw Read-Only Research Status Export Implementation V1

## Decision boundary

Phase 10.42R.4 implements a local, deterministic and fail-closed export of the
validated Phase 10.42R.3 research-status contract. The export is a passive file
artifact for a future consumer. It is not OpenClaw runtime integration.

This phase does not start a service, expose an API, register a tool, invoke
OpenClaw, read market data, generate a signal, rerun a backtest, recalculate
performance, open a lockbox, write official LONG evidence or authorize any
trading activity.

## Source authority

The exporter is bound to:

- Phase 10.42R.3 source commit
  `26c14a5a1fc63fbdb5bbb61f9bbc7d3dd46656d2`;
- Phase 10.42R.3 contract root
  `ba84140879bac8a897505bd55e12d3c117354caf1a5a5ad4f6c3eb003bd6fa46`;
- normalized Phase 10.42R.3 contract-module SHA-256
  `03f50b91f32af6cd421792810ba8da469faf1e35882eae8a21d176d861d770b5`;
- normalized Phase 10.42R.3 schema SHA-256
  `e7e21b99d899ecd7157aa7b476ae6f379d6a01adea804271c83426b271e71289`.

The source commit must exist in the repository and be an ancestor of the
current HEAD. The source contract module and schema must still match their
normalized hashes. Any mismatch is stale and blocks export.

## Export bundle

The local ignored directory
`reports/phase_10_42r_4/openclaw_read_only_export_v1/` contains exactly:

1. `openclaw_read_only_research_status_v1.json`;
2. `openclaw_read_only_research_status_v1.manifest.json`.

The snapshot is deterministic. Its generation field uses the fixed source
snapshot epoch `2026-07-20T00:00:00+00:00`; freshness is commit- and
contract-bound, not wall-clock-bound.

The manifest records the snapshot SHA-256, byte size, source commit, source
hashes, contract root and all disabled operational capabilities.

## Atomic publication

Each file is written to a unique temporary file in the destination directory,
flushed, `fsync`-ed and published with `os.replace`. The snapshot is published
before the manifest. A crash between those operations leaves a snapshot whose
old manifest cannot validate, so consumers must fail closed.

Temporary files are removed on failure. Any unexpected file in the export
bundle is blocking.

## Consumer boundary

Phase 10.42R.4 produces files only. It does not allow OpenClaw to consume them
at runtime. A future consumer must independently validate:

- exact two-file inventory;
- source commit ancestry;
- source hashes;
- schema version;
- contract root;
- snapshot hash and byte size;
- all prohibited permissions remain false.

Python remains the source of truth and human review remains mandatory.

## Explicitly prohibited

The implementation keeps zero or false:

- OpenClaw runtime status consumption;
- OpenClaw tool invocation;
- OpenClaw operational integration;
- historical evaluation and backtest execution;
- performance recalculation;
- candidate comparison, ranking, selection and mutation;
- retrospective lockbox and prospective holdout access;
- forward-observation start;
- official-dataset writes and evidence persistence;
- signal generation and live alerts;
- paper trading and real capital;
- market or exchange execution;
- automation.

## Validation decision

A passing phase emits:

`PHASE_10_42R_4_OPENCLAW_READ_ONLY_RESEARCH_STATUS_EXPORT_IMPLEMENTATION_VALIDATED`

A passing decision validates only the local export implementation and files.
It does not activate an OpenClaw consumer and does not approve a strategy.

## Recommended next phase

`PHASE_10_42R_5_OPENCLAW_READ_ONLY_RESEARCH_STATUS_EXPORT_INTEGRITY_AND_CONSUMER_BOUNDARY_REVIEW_V1`

Phase 10.43 remains separately allowed and not started. Passing either route
cannot grant permission to the other.
