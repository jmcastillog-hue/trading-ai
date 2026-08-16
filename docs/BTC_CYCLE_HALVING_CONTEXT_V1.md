# BTC Cycle Halving Context V1

## Purpose

`BTC_CYCLE_HALVING_CONTEXT_V1` is the first producer for
`CONTEXT_FEATURE_PACK_V1_LEVEL_A_STANDARD`.

It emits descriptive Bitcoin subsidy-cycle timing context only.

It does not predict price, infer LONG/SHORT direction, generate a signal,
modify the primary candidate, modify the primary rule, or authorize execution.

## Protocol anchor

Bitcoin Core mainnet uses a subsidy halving interval of 210,000 blocks.

This producer records that protocol interval but does not estimate when a future
halving block will occur.

## Calendar policy

The producer uses a frozen local calendar resource:

`src/context/resources/btc_cycle_halving_calendar_v1.json`

The resource contains historical halving block heights and UTC calendar dates.

Important:

The date is intentionally represented as a UTC calendar-day reference beginning
at `00:00:00 UTC`.

It is **not** represented as the exact block timestamp.

This avoids false timestamp precision while keeping the cycle feature
deterministic and auditable at day-scale.

The V1 resource records:

- 2012-11-28 / block 210000
- 2016-07-09 / block 420000
- 2020-05-11 / block 630000
- 2024-04-20 / block 840000

The next protocol halving height after the latest recorded event is 1,050,000.
No future date or time is estimated.

## Point-in-time rule

Inputs:

- frozen observation descriptor;
- frozen local halving calendar;
- explicit `produced_at_utc`.

The feature uses:

`information_cutoff_utc = reference_boundary_utc`

and:

`available_at_utc = produced_at_utc`

The Level A pack therefore decides eligibility using its already-published
policy:

- availability must be no later than context cutoff;
- information cutoff must be no later than context cutoff.

If this producer is executed retrospectively after an old observation, its
component can remain scientifically inspectable, but the Level A pack will mark
it point-in-time ineligible.

This is intentional.

## Historical reconstruction boundary

The producer selects only halving records whose calendar-day reference is at or
before the observation reference boundary.

Historical halving dates after the reference boundary are not used in the
payload.

No favorable or unfavorable forward outcome is used.

## Payload

For an observation at or after the first recorded halving, the component emits:

- halving index;
- halving block height;
- halving calendar date;
- UTC day-reference timestamp;
- post-halving subsidy;
- protocol halving interval;
- elapsed days and seconds since the day reference;
- previous completed cycle length in days, when available;
- elapsed fraction versus the previous completed cycle;
- neutral mathematical quartile versus the previous completed cycle;
- next protocol halving block height;
- explicit absence of a next-halving time estimate.

The quartile values are:

- `Q1`
- `Q2`
- `Q3`
- `Q4`
- `BEYOND_PREVIOUS_COMPLETED_CYCLE_LENGTH`

These quartiles are descriptive time partitions. They have no bullish, bearish,
entry, exit or risk semantics.

## Before first recorded halving

If an observation precedes the first recorded halving reference, the producer
returns:

`status = UNAVAILABLE`

with reason:

`NO_HALVING_REFERENCE_AT_OR_BEFORE_OBSERVATION`

No fabricated genesis-to-first-halving proxy is introduced in V1.

## Explicitly prohibited inputs

The producer does not use:

- BTC price;
- OHLCV;
- order book;
- open interest;
- funding;
- on-chain data;
- future forward outcomes;
- model predictions;
- a future halving-date estimate;
- web/network acquisition.

## Component contract

The output component matches the Level A envelope:

- `feature_id = BTC_CYCLE_HALVING_CONTEXT_V1`
- `source_kind = DETERMINISTIC`
- feature schema version;
- status;
- reason;
- availability timestamp;
- information-cutoff timestamp;
- SHA-256 of the frozen calendar resource;
- payload.

The producer includes an explicit compatibility check against the published
Level A pack contract.

## Local package

Authorization:

`PREPARE_BTC_CYCLE_HALVING_CONTEXT_V1`

Inputs:

- external observation descriptor JSON;
- explicit `produced_at_utc`.

Output:

- `btc_cycle_halving_context_component.json`
- `producer_checks.json`
- `manifest.sha256`

The output is external, create-only and transactional.

## Safety

The producer performs no:

- network request;
- Git network request;
- market-data acquisition;
- signal generation;
- direction inference;
- candidate modification;
- primary-rule modification;
- alert;
- paper trading;
- real-capital action;
- exchange execution;
- official forward-dataset write;
- official append-gate activation;
- scheduler/background process.

## Evaluation boundary

This producer is not evidence that Bitcoin cycle position predicts returns.

Its output can only become a research feature attached to prospective
observations.

A later Context Evaluation Engine must evaluate the feature across a sufficient
sample of immutable observations and forward outcomes before any quality gate
can be considered.
