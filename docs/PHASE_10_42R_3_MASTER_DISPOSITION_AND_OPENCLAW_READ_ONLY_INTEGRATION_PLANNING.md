# Phase 10.42R.3 — Master Disposition and OpenClaw Read-Only Research Status Contract V1

## Decision boundary

Phase 10.42R.3 consolidates the validated project state after the scientific
remediation and the independently audited recovery-candidate evaluation. It
defines a hash-bound, fail-closed research-status contract for a future
read-only OpenClaw consumer.

This phase does not integrate OpenClaw at runtime. It does not expose tools,
start a service, generate trading signals, read a lockbox, rerun a backtest,
recalculate performance, mutate a candidate, write official evidence or
authorize execution.

## Source authority

The contract binds:

- Phase 10.42R.2L commit
  `2177f69c1dd221ab9cf0db9a5c40992355a3317c`;
- Phase 10.42R.2K source bundle root
  `2938dcf9596281a8416b9ecd6f7431cbebee89559063bfe100a11258f76cbd02`;
- Phase 10.42R.2L independent audit bundle root
  `8f7f9b514f31a6cb98884febf396f9e57ecfbe53b4ebcf844c5752f1d3b055d6`;
- Phase 10.42R.2J historical-input binding root
  `5c1ccb1c9fecdad2e196558a946944f5b9f89f258c5ef591a65d4c4c480d8c14`;
- Phase 10.41 empty LONG schema candidate hash
  `e3fa86a461fd46f4d66dc2e03f185e49b7b3438d3cbc33340c01f51310514ff1`.

## Master disposition

The official consolidated state is:

- Phase 10.42 atomic-write harness: validated design only;
- Phase 10.42R scientific remediation: completed;
- corrected SHORT reference: `REVALIDATED_REJECTED`;
- SHORT recovery line: closed after six of six variants failed one or more
  mandatory gates and were independently rejected;
- surviving SHORT recovery variants: zero;
- primary LONG candidate: research-only, unaffected by the MTF defect and
  consistency revalidated;
- secondary LONG candidate: watchlist-only, unaffected by the MTF defect and
  consistency revalidated;
- LONG evidence artifact: tracked 54-column empty-schema candidate with zero
  evidence rows;
- retrospective lockbox: sealed;
- prospective holdout: sealed;
- project completion: false.

## Read-only OpenClaw contract

A future implementation may allow OpenClaw to:

- read a hash-bound project-status snapshot;
- summarize already validated project state;
- explain failed gates and restrictions;
- cite source anchors;
- request human review.

OpenClaw may never override Python permissions or infer an approval that is
not present in the snapshot.

The consumer must fail closed when:

- the schema version differs;
- the source commit differs;
- the contract root cannot be reproduced;
- a required field is absent;
- any permission value is unknown;
- the snapshot is stale relative to the repository source;
- a prohibited capability is set to true.

Python remains the source of truth. Human review remains mandatory.

## Freshness model

Freshness is source-commit-bound, not wall-clock-bound. A snapshot is stale
when its source commit or contract version differs from the expected values.
The generation timestamp is informative and is intentionally excluded from
the deterministic contract root.

## Two independent next routes

Phase 10.42R.3 preserves both routes without combining their permissions:

1. `PHASE_10_43_LONG_FORWARD_OBSERVATION_EVIDENCE_COLLECTION_OFFICIAL_DATASET_ATOMIC_WRITE_HARNESS_DESIGN_REVIEW_V1`
   may review the already validated design. It cannot implement or execute the
   harness and cannot write official evidence.
2. `PHASE_10_42R_4_OPENCLAW_READ_ONLY_RESEARCH_STATUS_EXPORT_IMPLEMENTATION_V1`
   may implement a local read-only status export. It cannot grant OpenClaw
   operational tools or any execution authority.

The routes are independent. Passing either route cannot grant permission to
the other.

## Explicitly prohibited

The contract keeps false:

- historical evaluation and backtest execution;
- performance recalculation;
- candidate comparison, ranking, selection and mutation;
- retrospective lockbox and prospective holdout access;
- forward-observation start;
- official-dataset writes and evidence persistence;
- signal generation and live alerts;
- paper trading and real capital;
- market or exchange execution;
- automation;
- OpenClaw runtime consumption, tool invocation and operational integration.

## Validation decision

A passing phase emits:

`PHASE_10_42R_3_MASTER_DISPOSITION_AND_OPENCLAW_READ_ONLY_RESEARCH_STATUS_CONTRACT_VALIDATED`

A passing decision validates the contract design and its local sample snapshot.
It does not mean OpenClaw integration is active and does not approve a
strategy or any operational activity.
