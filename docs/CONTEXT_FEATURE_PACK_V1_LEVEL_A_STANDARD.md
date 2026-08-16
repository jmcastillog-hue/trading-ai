# Context Feature Pack V1 - Level A Standard

## Purpose

`CONTEXT_FEATURE_PACK_V1_LEVEL_A_STANDARD` is the canonical aggregation contract
for point-in-time contextual research features.

It does not create a trading strategy, signal, score, ranking, direction or
execution decision.

The pack is attached to a synchronized observation and preserves the primary
candidate state exactly as observed.

## Scientific boundary

The pack exists to answer future research questions such as:

- when the primary rule produced `candidate=False`, what contextual features
  were actually available at that time?
- how did later 1/2/4/8/16-bar forward outcomes distribute conditional on those
  point-in-time features?
- does a contextual feature improve discrimination out of sample?

The pack may not answer those questions by itself. Evaluation belongs to the
later Context Evaluation Engine.

A single observation must never be used to promote, reject or tune a feature.

## Context clock

The pack uses:

`context_cutoff_utc = synchronized_context_available_at_utc`

from the frozen observation descriptor.

The context outcome anchor remains:

`FIRST_FULL_15M_BAR_OPEN_AT_OR_AFTER_CONTEXT_AVAILABILITY`

A feature is point-in-time eligible only when both:

1. `available_at_utc <= context_cutoff_utc`; and
2. `information_cutoff_utc <= context_cutoff_utc`.

An artifact created after the context cutoff is retained as unavailable for that
observation even if it describes older information.

This prevents retrospective feature reconstruction from being silently treated
as prospective evidence.

## Level A registry

The registry is fixed in this order:

1. `BTC_CYCLE_HALVING_CONTEXT_V1`
2. `EVENT_RISK_CALENDAR_CONTEXT_V1`
3. `EXTERNAL_CYCLE_REGRESSION_BASELINE_V1`
4. `LIQUIDITY_SWEEP_PATTERN_CONTEXT_V1`
5. `EXTERNAL_THESIS_MODEL_CARD_V1`
6. `ANALOG_ENGINE_CONTEXT_V1`
7. `SYNCHRONIZED_MICROSTRUCTURE_CONTEXT_V1`
8. `ONCHAIN_CONTEXT_INTERFACE_V1`

Every pack contains all eight slots.

A slot can be:

- `AVAILABLE`
- `UNAVAILABLE`
- `NOT_CONFIGURED`

Missing or extra feature IDs fail closed.

## Registry semantics

### BTC cycle / halving context

Deterministic cycle position only. It is context, never an entry trigger.

### Event risk calendar

Deterministic event-risk state based only on information that was actually
available before the context cutoff.

### External cycle regression baseline

A separately governed model output. The pack does not fit or refit the model.

### Liquidity sweep pattern context

A descriptive research feature only. It must not directly convert a sweep into
LONG/SHORT direction.

### External thesis model card

A separately governed external thesis snapshot with explicit provenance and
availability time.

### Analog Engine context

A separately governed similarity result. Neighbor selection, distance metrics
and data boundaries belong to that component, not to the pack.

### Synchronized microstructure context

Point-in-time read-only market context. It remains non-directional at the pack
layer.

### On-chain context interface

A reserved Level A slot. It may remain `NOT_CONFIGURED` until an on-chain source
is separately designed and validated.

## Component envelope

Every component is supplied under its registry feature ID and contains:

- `feature_id`
- `source_kind`
- `feature_schema_version`
- `status`
- `reason`
- `available_at_utc`
- `information_cutoff_utc`
- `source_artifact_sha256`
- `payload`

For `AVAILABLE`:

- payload must be a mapping;
- source artifact SHA-256 is mandatory;
- availability and information cutoff timestamps are mandatory;
- information cutoff cannot be later than availability.

For unavailable/not-configured slots:

- payload must be null;
- source SHA must be null;
- timestamps must be null;
- reason is mandatory.

The pack computes a canonical payload SHA-256.

## No retrospective mutation

The pack copies the observation's original:

- observation ID;
- primary candidate state;
- reference boundary;
- synchronized context availability.

It does not modify the primary rule.

A later favorable forward outcome does not make a historical
`candidate=False` observation into a candidate.

## No scoring in V1

V1 intentionally forbids pack-level:

- composite scores;
- direction inference;
- trade actions;
- entry prices;
- stop prices;
- target prices.

Weights, scores and gates may only be introduced later after a separately
preregistered evaluation procedure demonstrates value.

## Package output

The package writer is local-only and create-only.

Authorization:

`PREPARE_CONTEXT_FEATURE_PACK_V1_LEVEL_A_STANDARD`

Inputs are external:

- observation descriptor JSON;
- components JSON.

Output:

- `context_feature_pack.json`
- `pack_checks.json`
- `manifest.sha256`

The writer performs no network request and does not fetch any component source.

## Safety

This component does not:

- modify the primary candidate;
- modify the primary rule;
- generate a signal;
- send an alert;
- enable paper trading;
- enable real capital;
- execute orders;
- write the official forward dataset;
- enable the official append gate;
- schedule work;
- run in the background.

## Current implementation scope

This phase implements only:

1. the Level A registry;
2. point-in-time eligibility rules;
3. pack normalization;
4. create-only local packaging;
5. synthetic/static validation.

It does not yet implement the eight feature producers.

## Recommended implementation order after publication

1. `BTC_CYCLE_HALVING_CONTEXT_V1`
2. `EVENT_RISK_CALENDAR_CONTEXT_V1`
3. `SYNCHRONIZED_MICROSTRUCTURE_CONTEXT_V1`
4. `LIQUIDITY_SWEEP_PATTERN_CONTEXT_V1`
5. `EXTERNAL_CYCLE_REGRESSION_BASELINE_V1`
6. `EXTERNAL_THESIS_MODEL_CARD_V1`
7. `ANALOG_ENGINE_CONTEXT_V1`
8. `ONCHAIN_CONTEXT_INTERFACE_V1`

The deterministic components come first because they are the easiest to audit
without market or model-network access.

## Evaluation

After feature producers exist, packs may be attached prospectively to future
observations.

`FORWARD_OUTCOME_LABELER_V1` outcomes remain separate labels.

The future Context Evaluation Engine may join feature packs to forward outcomes
only by immutable observation identity and explicit point-in-time eligibility.

No feature may be promoted from a single observation.
