# Event Risk Calendar Context V1

## Purpose

`EVENT_RISK_CALENDAR_CONTEXT_V1` is the second deterministic producer for
`CONTEXT_FEATURE_PACK_V1_LEVEL_A_STANDARD`.

It describes scheduled macro-event proximity that was knowable at the
observation reference boundary.

It does not classify an event as bullish or bearish, score event importance,
use event surprise values, use market reaction, generate a signal, modify the
primary candidate, or modify the primary rule.

## Separation of acquisition and feature production

This producer performs no web or API acquisition.

Its dynamic input is an external frozen event-calendar snapshot.

A future acquisition adapter can be designed separately and can use official
source calendars. That future adapter is outside this V1 producer.

This separation prevents an HTTP fetch or a changed web calendar from silently
changing the deterministic feature calculation.

## Frozen taxonomy

The repository contains:

`src/context/resources/event_risk_calendar_taxonomy_v1.json`

The V1 taxonomy contains exactly:

1. `FOMC_RATE_DECISION`
2. `FOMC_MINUTES`
3. `US_CPI`
4. `US_PPI`
5. `US_NONFARM_PAYROLLS`
6. `US_CORE_PCE`
7. `US_GDP_ADVANCE`
8. `US_RETAIL_SALES`

The taxonomy records source-authority families only.

It does not assign:

- bullish/bearish direction;
- numeric importance;
- expected surprise;
- expected volatility;
- trade actions.

## External snapshot contract

The external snapshot uses:

`EVENT_RISK_CALENDAR_SNAPSHOT_V1`

Required top-level fields:

- `schema_version`
- `snapshot_id`
- `snapshot_created_at_utc`
- `source_name`
- `events`

Each event contains:

- `event_id`
- `event_type`
- `scheduled_at_utc`
- `schedule_known_at_utc`
- `schedule_source`

Events must be unique and strictly ordered by scheduled time then event ID.

The schedule knowledge timestamp cannot be later than snapshot creation.

## Point-in-time protection

For an observation, the producer uses:

`information_cutoff_utc = reference_boundary_utc`

Only events satisfying:

`schedule_known_at_utc <= reference_boundary_utc`

are allowed into the payload.

An event present in a later calendar snapshot but whose schedule was not known
at the observation boundary is excluded.

The payload explicitly records how many snapshot events were excluded because
their schedule knowledge timestamp was after the reference boundary.

## Availability

The component uses:

`available_at_utc = produced_at_utc`

The published Level A pack therefore remains the final arbiter of point-in-time
eligibility.

A component produced after `synchronized_context_available_at_utc` can be
preserved for audit but is ineligible for that old observation.

## Descriptive outputs

The producer emits:

- total known event count at the reference boundary;
- count excluded for post-reference schedule knowledge;
- previous known scheduled event;
- next known scheduled event;
- seconds since previous event;
- seconds to next event;
- upcoming event counts within 1h, 6h, 24h, 72h and 7d;
- recent event counts within 1h, 6h and 24h.

These are time-distance features only.

No `risk_score`, `direction`, `trade_action`, `entry`, `stop` or `target` is
created.

## Event values are intentionally excluded

V1 does not ingest:

- actual release values;
- consensus values;
- forecast values;
- prior values;
- surprise calculations;
- revisions;
- market reaction.

Those would introduce a different information-time problem and require a
separate governed feature family.

## Market independence

The producer uses no:

- BTC price;
- OHLCV;
- order book;
- open interest;
- funding;
- on-chain data;
- forward outcomes.

The result therefore cannot directly become a trading signal.

## Package authorization

Authorization:

`PREPARE_EVENT_RISK_CALENDAR_CONTEXT_V1`

Inputs:

- external observation descriptor JSON;
- external frozen event-calendar snapshot JSON;
- explicit `produced_at_utc`.

Output:

- `event_risk_calendar_context_component.json`
- `producer_checks.json`
- `manifest.sha256`

The output is external, create-only and transactional.

## Safety

This producer performs no:

- market-data request;
- event-calendar network request;
- Git network request;
- background process;
- scheduler;
- signal generation;
- direction inference;
- candidate modification;
- primary-rule modification;
- alert;
- paper trade;
- real-capital action;
- exchange execution;
- official forward-dataset write;
- official append-gate activation.

## Evaluation boundary

This feature is not evidence that proximity to any event predicts BTC returns.

A later Context Evaluation Engine may compare these immutable time-distance
features against separately preserved 1/2/4/8/16-bar forward outcomes.

No event type or proximity window may be promoted from a single observation.
