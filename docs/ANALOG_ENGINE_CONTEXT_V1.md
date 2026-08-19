# Analog Engine Context V1

## Purpose

`ANALOG_ENGINE_CONTEXT_V1` is the Level A `MODEL_DERIVED` producer for
deterministic nearest-neighbour context over a frozen, pre-standardized feature
space. It is not an outcome model and not a trading model.

## External inputs

The producer consumes two external immutable JSON snapshots:

- `ANALOG_QUERY_VECTOR_SNAPSHOT_V1`
- `ANALOG_REFERENCE_LIBRARY_SNAPSHOT_V1`

Both must carry the same `feature_space_sha256`, the same ordered
`feature_names`, and finite pre-standardized vectors.

The producer does not normalize data itself and does not fit or train a model.

## Distance contract

V1 freezes `EUCLIDEAN_PRESTANDARDIZED_VECTOR` with `top_k = 5`.

Tie-breaking is deterministic by distance ascending, reference time ascending,
then observation ID ascending.

## Point-in-time contract

Every reference row must be strictly older than the query:

`analog.reference_boundary_utc < query.reference_boundary_utc`

Every query/library feature information cutoff must be no later than the
reference time that generated that vector.

The library normalization-fit cutoff must be no later than the query reference.
This prevents a standardization fitted with future information from entering
the query.

The component's `information_cutoff_utc` is the latest information cutoff used.
Its `available_at_utc` is the maximum of query snapshot creation, library
snapshot creation, policy floor, and that information cutoff.

## Governance floor

`2026-08-19T01:30:00+00:00`

This prevents later-built analogue infrastructure from being retrospectively
promoted as point-in-time evidence for older observations.

## Output

Only descriptive similarity metadata is returned:

- selected historical observation IDs;
- their reference times;
- Euclidean distances;
- nearest distance;
- median selected distance;
- feature count;
- library row count.

No historical returns, MFE, MAE, PnL, target/stop results, winner/loser labels,
future outcomes, or outcome-derived voting are accepted.

## Explicitly prohibited inference

V1 does not perform majority voting, bullish/bearish classification, long/short
classification, expected-return estimation, probability estimation, composite
scoring, candidate modification, signal generation, or execution.

Distance means only similarity in the frozen standardized feature space.

## Package authorization

Authorization: `PREPARE_ANALOG_ENGINE_CONTEXT_V1`

Inputs are an external observation descriptor, query-vector snapshot, reference
library snapshot, and explicit `produced_at_utc`.

Output is create-only and transactional:

- `analog_engine_context_component.json`
- `producer_checks.json`
- `manifest.sha256`

## Safety

No network request, market-data fetch, model training, future-outcome lookup,
live alert, paper trade, real-capital action, exchange execution, or official
dataset append is permitted.

## Evaluation boundary

Similarity is a research descriptor only. Its usefulness must be tested later
by the Context Evaluation Engine against separately preserved forward outcomes.
