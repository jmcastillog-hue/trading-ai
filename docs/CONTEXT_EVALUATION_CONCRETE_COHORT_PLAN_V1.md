# Context Evaluation Concrete Cohort Plan V1

## Status

This document records the first concrete prospective sampling plan for
`CONTEXT_EVALUATION_PROSPECTIVE_COHORT_V1`.

Canonical plan:

`research/context_evaluation/context_evaluation_concrete_cohort_plan_v1.json`

Cohort ID:

`CONTEXT_LEVEL_A_ROTATING_DAILY_30_V1`

Plan freeze:

`2026-08-22T19:15:00+00:00`

Canonical plan SHA-256:

`b38d27f8a5eeec320e7b35c11b9c22ab663c047f9b451a218002c746d893ce0b`

## Frozen scientific binding

The plan is bound to the already-published Level A hypothesis manifest:

- canonical hypothesis SHA-256:
  `4de33a61d2a1456e6bd673ddd044cd0c01bb3369d30595ec57773df1d922442b`
- hypothesis freeze:
  `2026-08-22T16:15:00+00:00`

No hypothesis, sign, threshold, transform, feature, or outcome is selected by
this plan.

## Sampling schedule

The plan contains exactly 30 predeclared slots.

First slot:

`2026-08-23T14:00:00+00:00`

Last slot:

`2026-09-21T22:00:00+00:00`

The UTC hour rotates deterministically through:

`14:00 -> 18:00 -> 22:00 -> repeat`

There is one slot per UTC calendar day. This provides multiple intraday
contexts without requiring several supervised admissions every day.

The smallest consecutive spacing is 16 hours, which is greater than the
protocol minimum of 4 hours. Therefore the schedule does not overlap at the
largest preregistered H16 horizon.

## Why UTC is canonical

The plan is intentionally expressed only in UTC. Local civil time may change
because of daylight-saving transitions. UTC avoids changing the scientific
sampling rule after publication.

## Missing slots

A missed slot is not replaced retrospectively.

The prospective cohort protocol records it as `SLOT_NOT_ADMITTED`. Replacing
a missed observation with a favorable later market state would reopen
selection bias.

A future additional cohort may be preregistered separately if more sample
size is needed.

## Admission window

For every slot, a Level A context pack must be admitted after its context
cutoff and strictly before:

`context_anchor_open_utc + 30 minutes`

The admission stage has no forward-outcome argument.

## Safety and scope

Preparing and publishing this plan performs no:

- real market-data request;
- real context capture;
- real cohort-root initialization;
- real admission;
- outcome binding;
- evaluation;
- p-value or significance calculation;
- quality gate;
- edge claim;
- signal;
- alert;
- paper trade;
- real-capital action;
- exchange execution;
- official append.

After this plan is formally frozen and published, the next stage is to
initialize its external create-only cohort root before the first scheduled
slot.
