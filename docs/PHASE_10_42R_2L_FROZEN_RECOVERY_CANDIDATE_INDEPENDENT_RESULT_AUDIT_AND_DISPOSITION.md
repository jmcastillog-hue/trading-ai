# Phase 10.42R.2L — Frozen Recovery Candidate Independent Result Audit and Disposition V1

## Decision boundary

Phase 2L independently audits the immutable Phase 2K result bundle. It does not
read the nine OHLCV datasets, regenerate signals, rerun the historical
backtest, modify candidate rules, optimize parameters, compare candidates,
rank variants, select a winner, or open either holdout.

The frozen source is:

- Phase 2K commit: `0a5440a70e91e833925a4147ac2863baa7666b1e`;
- run ID: `known_evidence_2022_2025_v1_5c1ccb1c9fec_9243ae595f7d`;
- Phase 2K bundle root:
  `2938dcf9596281a8416b9ecd6f7431cbebee89559063bfe100a11258f76cbd02`;
- Phase 2K normalized engine SHA-256:
  `9243ae595f7d22bc2653ba34098bec5f1b6bc2a1e79c4114b8ea35fd83c3a4fd`;
- Phase 2J binding root:
  `5c1ccb1c9fecdad2e196558a946944f5b9f89f258c5ef591a65d4c4c480d8c14`.

## Independent reproduction

The audit reads the 12 published Phase 2K artifacts and independently:

1. verifies the exact artifact inventory, every SHA-256 and the bundle root;
2. reconciles 9,216 signal rows, 9,216 order rows and 5,689 eligible trades;
3. reconstructs the five cost-profile applications from the trade ledger;
4. reproduces all 450 metric rows without importing the Phase 2K engine;
5. reproduces the six centered cluster-bootstrap p-values and Holm adjustment;
6. reproduces all 60 mandatory gate rows;
7. records the precise failed gate IDs and metrics for every variant;
8. confirms that no override, ranking, selection, lockbox or operational
   authorization occurred.

## Disposition rule

A variant with one or more failed mandatory gates is assigned:

`REJECTED_AFTER_INDEPENDENT_KNOWN_EVIDENCE_AUDIT_NO_LOCKBOX_OPENING`

Because Phase 2K published all six variants as failing one or more mandatory
gates, the expected finite line decision is:

`INDEPENDENT_RESULT_AUDIT_CONFIRMED_ALL_VARIANTS_REJECTED_RECOVERY_LINE_CLOSED_NO_LOCKBOX_OPENED`

This is not permission to tune the variants after seeing results. Any later
hypothesis must start a separately preregistered research lineage. The
retrospective lockbox and prospective holdout remain sealed and unnecessary for
these rejected candidates.

## Audit outputs

The ignored local directory
`reports/phase_10_42r_2l/independent_result_audit_v1_2938dcf95962_9243ae595f7d/`
contains exactly seven artifacts:

1. source bundle inventory;
2. independently reproduced metric table;
3. independently reproduced multiplicity table;
4. independently reproduced gate table;
5. variant disposition table;
6. audit check ledger;
7. audit summary with its own deterministic root.

## Safety state

Paper trading, real capital, market or exchange execution, live alerts,
automation, candidate mutation, winner selection and OpenClaw operational
integration remain disabled. Phase 2L closes the recovery route; it does not
approve a strategy.

## Next route

After formal closure, return to the Phase 10.42R master disposition and plan
read-only OpenClaw integration around validated project status. Do not create
another repair phase or open a lockbox for the rejected variants.

## Local audit correction incorporated before closure

The source Phase 2K bundle publishes 12 internal engine checks in
`check_ledger.csv`. The 15 checks shown by the Phase 2K validator are a separate
validation-layer count and must not be substituted for the source ledger row
count. Phase 2L therefore binds the source ledger to exactly 12 rows and also
reconciles that count with `run_summary.json`.

Phase 2K CSV artifacts use 15 significant digits. Recomputing aggregate metrics
from the serialized trade ledger can introduce sub-nanounit floating-point
rounding relative to metrics calculated before serialization. Structural fields,
integers, booleans and text remain exact; finite floating-point cells use
absolute tolerance `1e-9` and relative tolerance `1e-12`. Material numerical
drift remains blocking. No gate threshold or candidate outcome is altered.
