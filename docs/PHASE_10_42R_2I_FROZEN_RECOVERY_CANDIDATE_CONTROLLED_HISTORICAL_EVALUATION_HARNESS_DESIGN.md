# Phase 10.42R.2I — Frozen Recovery Candidate Controlled Historical Evaluation Harness Design

## Status

Phase 10.42R.2I freezes one finite source-only design for the future controlled
historical evaluation harness. It is not another strategy repair phase.

The repair line is closed after the corrected implementation was accepted in
2G and the historical protocol was locked in 2H. No new repair subphase may be
created unless a concrete, reproducible and blocking defect prevents the
frozen route from continuing.

## Finite completion route

The remaining recovery route is explicitly bounded:

1. `2I_HARNESS_DESIGN`
2. `2J_INPUT_MANIFEST_BINDING_AND_INTEGRITY`
3. `2K_CONTROLLED_KNOWN_EVIDENCE_EVALUATION`
4. `2L_INDEPENDENT_RESULT_AUDIT_AND_DISPOSITION`

Passing 2I advances directly to 2J. It does not reopen 2F, 2G or 2H and does
not create recursive review or repair branches.

## Phase boundary

2I performs static design only. It does not:

- bind historical paths;
- hash historical files;
- parse historical schemas;
- read OHLCV content;
- execute the harness or a backtest;
- calculate metrics;
- compare or rank variants;
- select a winner;
- open either lockbox;
- write result artifacts;
- enable signals, alerts, paper trading, capital, execution or automation.

## Frozen source authority

The design is anchored to:

- Phase 2H commit `5777da3d52908de15841c0e814290577ae4dffba`;
- Phase 2H protocol SHA-256
  `a42a8da21d1afd231be37376de8ecdfc0306dc8db2375bacb5f2de567947e493`;
- the Phase 2H manifest, document and validator;
- the Phase 2G independent synthetic acceptance;
- corrected frozen implementation `v2`.

All source anchors use normalized SHA-256.

## Historical input-manifest schema

The future manifest contains exactly nine rows:

- `BTCUSDT`, `ETHUSDT`, `SOLUSDT`;
- `15m`, `1h`, `4h`;
- known-evidence window only.

Each row uses 25 ordered fields covering logical identity, repository-relative
path, file SHA-256, size, row count, UTC coverage, exact schema, interval,
provider provenance, duplicate counts, missing intervals, invalid OHLCV rows,
binding state and a canonical row hash.

All nine slots remain `UNBOUND_DESIGN_ONLY` in 2I. Paths and hashes are blank,
and market-content access is false.

## Harness component graph

The future harness has 13 ordered components:

1. source-anchor verifier;
2. input-manifest binder;
3. byte-integrity verifier;
4. schema and coverage validator;
5. closed-MTF alignment engine;
6. frozen-variant evaluator;
7. next-open order engine;
8. position and exit engine;
9. single-profile cost accounting;
10. metric and slice aggregator;
11. multiplicity controller;
12. gate classifier;
13. audit-bundle writer.

Every dependency points backward in the fixed order. No component is
implemented or executed in 2I.

## State machine

The permitted 2I path ends at `DESIGN_FROZEN_TERMINAL`. Attempts to bind input,
read market bytes, execute historical evaluation or open a lockbox are routed
to a blocked fail-closed state because those actions belong to later phases.

## Failure model

Twenty failure modes cover source identity, manifest completeness, safe paths,
file integrity, schema, UTC chronology, coverage, interval continuity, OHLCV
integrity, closed-MTF availability, registry identity, next-open orders,
position overlap, exits, cost accounting, metrics, multiplicity,
interpretation and lockbox access.

Every failure blocks all downstream stages and terminates the run as
`BLOCKED_FAIL_CLOSED`.

## Future audit bundle

The design declares twelve future artifacts:

- input manifest;
- source anchors;
- environment manifest;
- data-quality report;
- signal ledger;
- order ledger;
- trade ledger;
- metric table;
- multiplicity table;
- gate classification;
- check ledger;
- run summary.

Their templates point to a future Phase 2K run directory. 2I writes none of
them.

## Immutable invariants

Twenty-four invariants preserve the frozen protocol, nine-slot dataset,
closed-candle MTF timing, next-open fill, non-overlap, 2.5R exits,
single-profile costs, preregistered metrics and slices, chronological drawdown,
one six-test Holm pool, no winner selection, lockbox sealing, operational
prohibitions, reproducibility, mutation rules, repair termination and phase
termination.

## Passing decision

`CONTROLLED_HISTORICAL_EVALUATION_HARNESS_DESIGN_FROZEN`

A passing decision permits only:

`PHASE_10_42R_2J_FROZEN_RECOVERY_CANDIDATE_HISTORICAL_INPUT_MANIFEST_BINDING_AND_INTEGRITY_VALIDATION_V1`

It does not authorize historical evaluation.
