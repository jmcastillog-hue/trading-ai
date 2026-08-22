# Context Evaluation Prospective Cohort V1

## Purpose

`CONTEXT_EVALUATION_PROSPECTIVE_COHORT_V1` prevents outcome-aware selection
between the frozen Level A hypothesis manifest and
`CONTEXT_EVALUATION_ENGINE_V1`.

The core rule is that an observation must be admitted before the earliest
preregistered forward outcome can be complete.

## Frozen hypothesis binding

V1 is bound to the published preregistration:

- path: `research/context_evaluation/context_evaluation_hypothesis_manifest_v1.json`
- SHA-256: `4de33a61d2a1456e6bd673ddd044cd0c01bb3369d30595ec57773df1d922442b`
- freeze: `2026-08-22T16:15:00+00:00`

The preregistered horizons are 2, 4 and 16 bars. The earliest outcome matures
30 minutes after the synchronized context anchor and the largest horizon is
4 hours.

The preregistration SHA-256 is the hash of its canonical JSON serialization
(sorted keys, compact separators, UTF-8, one LF terminator), not the raw
working-tree bytes. This keeps the same scientific identity on Windows when
Git presents CRLF line endings without changing the committed Git blob.

## Frozen cohort plan

A real cohort requires a separate
`CONTEXT_EVALUATION_PROSPECTIVE_COHORT_PLAN_V1`. The plan contains only a
cohort ID, plan freeze time, the hypothesis binding, and exact UTC context
anchor slots.

No price, OHLCV, volatility, regime, direction, candidate state, signal,
feature value, return, MFE/MAE, threshold or score is accepted by the plan.

The concrete schedule is a separate next step. It must be committed and
published before its own `plan_frozen_at_utc`.

## Slot spacing

Slots are aligned to 15-minute boundaries and separated by at least 16 bars
(4 hours). This makes the planned sample non-overlapping at every
preregistered horizon. The evaluation engine still keeps its own overlap
purge as an independent guard.

## Stage 1 - pre-outcome admission

`prepare_context_admission_v1` consumes only a validated Level A context pack.
It has no forward-outcome-package argument.

Admission requires an exact predeclared slot, a context cutoff not before the
hypothesis freeze, and a real admission time after the context cutoff but
strictly before `context_anchor_open_utc + 30 minutes`.

Feature availability is not an admission criterion. Missing context features
remain an evaluation-engine concern rather than a reason to discard a market
observation.

## Stage 2 - later outcome binding

`prepare_outcome_binding_v1` can run only after an immutable admission exists.
It validates observation ID, synchronized context cutoff, synchronized context
anchor, and requires the preregistered 2/4/16-bar labels to be `AVAILABLE`.

The receipt stores package identity and maturity metadata only. It does not
copy `forward_return`, MFE, MAE, target/stop result, sign, magnitude or profit.
Outcome values cannot decide whether an already-admitted observation remains
in the cohort.

## Stage 3 - deterministic materialization

`materialize_engine_cohort_manifest_v1` scans the frozen plan. Each slot is
classified as `BOUND_READY_FOR_ENGINE`, `ADMITTED_OUTCOME_NOT_BOUND`, or
`SLOT_NOT_ADMITTED`.

Every valid bound admission is included automatically. There is no manually
selected subset argument. The generated manifest uses the exact
`CONTEXT_EVALUATION_COHORT_MANIFEST_V1` schema expected by the published
engine.

## Safety

V1 performs no market-data acquisition, API/RPC request, background schedule,
model fit, p-value, significance assignment, feature ranking, quality gate,
edge claim, signal, alert, paper trade, real-capital action, exchange execution
or official append.

Publishing this protocol does not start the real cohort. The next step is to
freeze one concrete UTC slot schedule.
