# Context Evaluation Engine V1

## Purpose

`CONTEXT_EVALUATION_ENGINE_V1` is an offline, point-in-time evaluation layer for
the eight features in `CONTEXT_FEATURE_PACK_V1_LEVEL_A_STANDARD`.

It answers a deliberately narrow question:

> When a Level A context feature was genuinely available at the synchronized
> context cutoff, what descriptive association did a preregistered scalar
> hypothesis have with the later synchronized-context forward return?

It does **not** decide that a context is profitable, useful, supportive,
dangerous, bullish, bearish, long, short, or tradeable.

## Why this is additive

The repository already contains the older `ContextPerformanceAnalyzer V1`.
That analyzer groups the legacy forward-observation dataset by fields such as
`context_name`, `direction`, `cost_profile`, `result_r`, and applies threshold
classifications.

This engine does not modify or replace that analyzer. The Level A pack is a
different object: it contains eight heterogeneous point-in-time feature
payloads and explicitly has no signal semantics. A separate evaluator is
therefore required.

## Frozen dependencies

V1 consumes only packages already validated by the published contracts:

- `CONTEXT_FEATURE_PACK_V1_LEVEL_A_STANDARD`
- `FORWARD_OUTCOME_LABELER_V1`

The evaluation branch is always:

`synchronized_context_outcome`

The primary-rule outcome branch is never used to score a context hypothesis.
This is essential because context may become available after the primary
reference boundary.

The supported synchronized horizons are exactly:

`1, 2, 4, 8, 16` bars.

## Exact temporal join

For every observation the engine requires:

- identical `observation_id`;
- identical context cutoff between pack and outcome package;
- identical context anchor between pack and synchronized outcome;
- a feature with `status=AVAILABLE`;
- `point_in_time_eligible=True`;
- an `AVAILABLE` synchronized forward-return label.

A missing or late feature is never converted to zero and is never imputed.

## Preregistered hypothesis manifest

Evaluation requires an immutable
`CONTEXT_EVALUATION_HYPOTHESIS_MANIFEST_V1`.

Each hypothesis freezes:

- `hypothesis_id`;
- Level A `feature_id`;
- dictionary-only `payload_path`;
- predictor type: `CONTINUOUS`, `BINARY`, or `CATEGORICAL`;
- one horizon from `1,2,4,8,16`;
- outcome field `forward_return`;
- transform `IDENTITY`.

No expected sign, threshold, rule direction, or optimizer is accepted.

The manifest has a `frozen_at_utc`. V1 requires:

`frozen_at_utc >= policy_effective_from_utc`

and excludes every observation whose context cutoff predates the hypothesis
freeze. This prevents the new evaluator from turning old observations into
retrospective confirmatory evidence.

## Cohort manifest

A separate `CONTEXT_EVALUATION_COHORT_MANIFEST_V1` explicitly enumerates the
context-pack and outcome-package directory for every observation and records
the SHA-256 of each package manifest.

The engine does not scan directories looking for favorable observations.

## Outcome-window overlap

Forward horizons can overlap heavily on 15-minute observations. V1 therefore
uses a deterministic chronological purge for every hypothesis:

1. sort usable observations by context anchor;
2. keep the earliest observation;
3. reject later observations whose forward window starts before the previously
   selected forward window ends;
4. continue until the cohort is exhausted.

The descriptive effect estimate uses only this non-overlapping subset.
Raw usable count and purged count are both reported.

## Descriptive statistics only

### Continuous predictor

V1 reports:

- non-overlapping sample size;
- mean/median predictor;
- mean/median forward return;
- Spearman rank correlation;
- chronological first-half Spearman correlation;
- chronological second-half Spearman correlation.

### Binary predictor

V1 reports:

- false/true group counts;
- group mean and median forward return;
- mean-return difference `true - false`;
- the same mean difference in chronological first and second halves.

### Categorical predictor

V1 reports per-level:

- count;
- mean forward return;
- median forward return.

No single "winner" category is selected.

## What V1 intentionally does not calculate

V1 does not generate:

- p-values;
- statistical significance;
- a multiple-testing winner;
- a feature ranking;
- optimized thresholds;
- fitted models;
- hyperparameter searches;
- composite scores;
- directional signals;
- an edge gate.

This is intentional. A later quality gate may be designed only after a
prospective cohort exists in sufficient quantity.

## Sample sufficiency

Sample thresholds are descriptive quality states only:

- minimum non-overlapping observations: `10`;
- preferred non-overlapping observations: `30`;
- binary group minimum: `5` per group;
- categorical group minimum: `5` per level;
- maximum categorical levels: `8`.

Meeting these thresholds does not establish edge.

## Output package

Authorization:

`PREPARE_CONTEXT_EVALUATION_ENGINE_V1`

The create-only external package contains:

- `evaluation_results.json`
- `evaluation_audit.json`
- `evaluation_checks.json`
- `manifest.sha256`

## Safety

The engine performs no network request, provider query, market-data fetch,
order, alert, paper trade, real-capital action, exchange execution, model fit,
official append, or modification of the frozen primary rule.

## Decision boundary

Every V1 package must state:

`DESCRIPTIVE_ONLY_NO_EDGE_CLAIM`

A quality gate is a separate future capability and must not be inferred from
these descriptive results.
