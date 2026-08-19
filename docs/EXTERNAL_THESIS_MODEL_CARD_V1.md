# External Thesis Model Card V1

## Purpose

`EXTERNAL_THESIS_MODEL_CARD_V1` is the Level A `EXTERNAL_MODEL` producer for
an externally supplied research thesis/model card.

It does not execute the external model, fetch a web source, ingest free-form
forecast text, or turn the external thesis into a trading instruction.

## Frozen external snapshot

The source is an external immutable JSON snapshot with schema:

`EXTERNAL_THESIS_MODEL_CARD_SNAPSHOT_V1`

The card identifies the thesis/model, source, method family, horizon, source
publication time, information cutoff, thesis-generation time, snapshot
creation time, declared applicability window, a content SHA-256 and an opaque
source-defined state code.

The actual narrative thesis is not copied into this feature. Its frozen content
is represented by `thesis_content_sha256` plus `source_reference`.

## Opaque state code

`state_code` is a source-defined categorical identifier such as
`SOURCE_STATE_01`.

The producer does not map that state code to bullish, bearish, long, short,
risk-on, risk-off, buy, sell, confidence, or a numeric score.

A later Context Evaluation Engine may test whether preregistered opaque states
have measurable forward associations without granting them signal semantics.

## Point-in-time order

The required temporal order is:

`source_published_at_utc <= information_cutoff_utc <= thesis_generated_at_utc <= snapshot_created_at_utc`

The observation reference boundary must also lie inside the source-declared
applicability window:

`applicability_start_utc <= reference_boundary_utc`

and, when an end exists:

`reference_boundary_utc <= applicability_end_utc`

No nearest-window substitution is allowed.

## Governance floor

The preregistration floor is:

`2026-08-19T01:02:00+00:00`

Feature availability is:

`available_at_utc = max(snapshot_created_at_utc, policy_effective_from_utc)`

Therefore an old model card frozen before the policy existed may be retained
for audit but cannot be retrospectively promoted as point-in-time evidence for
an older observation.

## Structured metadata

Allowed method families:

- `CYCLE`
- `MACRO`
- `TECHNICAL`
- `ONCHAIN`
- `FLOW`
- `MULTI_FACTOR`
- `OTHER`

Allowed horizon labels:

- `INTRADAY`
- `SWING`
- `MULTI_WEEK`
- `CYCLE`
- `UNSPECIFIED`

These labels are descriptive metadata only.

## Deliberately excluded fields

V1 does not ingest:

- narrative forecast text;
- target prices;
- stops;
- entries;
- confidence scores;
- probabilities;
- trade instructions;
- future outcomes.

This keeps the source card auditable without turning an external thesis into an
actionable signal.

## Package authorization

Authorization:

`PREPARE_EXTERNAL_THESIS_MODEL_CARD_V1`

Inputs:

- external observation descriptor JSON;
- external frozen thesis-card snapshot JSON;
- explicit `produced_at_utc`.

Output:

- `external_thesis_model_card_component.json`
- `producer_checks.json`
- `manifest.sha256`

The package is external, create-only and transactional.

## Safety

No network request, model execution, market-data lookup, candidate mutation,
primary-rule mutation, signal generation, live alert, paper trade, real-capital
action, exchange execution, or official dataset append is permitted.

## Evaluation boundary

An external thesis is a hypothesis source, not evidence of an edge. Any
usefulness must be established later from sufficient point-in-time observations
and separately preserved forward outcomes.
