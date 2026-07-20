# Phase 10.42R.2G — Frozen Recovery Candidate Correction Independent Synthetic Acceptance V1

## Status

This phase independently accepts or rejects the corrected frozen recovery candidate implementation `v2` using deterministic synthetic contracts only.

## Authoritative source

- Phase 2F commit: `a1fd9b168e61e94635c16a0f9e808f360268d676`
- Corrected source: `src/analysis/frozen_recovery_candidate_implementation_v2.py`
- Normalized source SHA-256: `ccf3cc05823515fa56e9e1183eb51ab903503e310aa037248847ad7445b2cc1e`
- Frozen Phase 2E source commit: `7d7f8ee81156b1858a636b586eb5636b34b1c801`

## Independence boundary

Phase 2G does not import or call the Phase 2F independent review validator or its private synthetic fixtures. It builds a separate deterministic acceptance harness against the public corrected implementation boundary.

## Accepted scope

The acceptance harness may:

- verify the normalized corrected-source identity;
- verify the six-member canonical registry and its deterministic order;
- create deterministic synthetic OHLC bars;
- create deterministic closed MTF contexts;
- evaluate positive and negative signal contracts;
- validate next-open order construction;
- validate fixed reward-to-risk `2.5`;
- validate overlap, gap, chronology-index, and non-finite guards;
- validate target, stop, simultaneous, and time-exit behavior;
- accept or reject the corrected implementation for a future preregistered historical evaluation phase.

## Prohibited scope

This phase must not:

- read real or historical market data;
- access holdouts;
- download data;
- read or write `data/`, `reports/`, or runtime artifacts;
- calculate performance or profitability metrics;
- compare or rank candidates;
- select a winner;
- start forward observation;
- write the official evidence dataset;
- enable live signals or alerts;
- enable paper trading;
- enable real capital;
- enable exchange or market execution;
- enable automation.

## Canonical variants

1. `RCV_SHORT_UPSIDE_SWEEP_REVERSAL_F01_N48_V01`
2. `RCV_SHORT_UPSIDE_SWEEP_REVERSAL_F01_N96_V02`
3. `RCV_SHORT_BREAKDOWN_RETEST_F02_N48_V01`
4. `RCV_SHORT_BREAKDOWN_RETEST_F02_N96_V02`
5. `RCV_SHORT_EMA_PULLBACK_CONTINUATION_F03_S000_V01`
6. `RCV_SHORT_EMA_PULLBACK_CONTINUATION_F03_S025_V02`

## Acceptance contract

The full run contains:

- 8 preflight checks;
- 39 independent synthetic acceptance cases;
- 47 total checks;
- six positive variant cases;
- explicit correction-boundary cases;
- fail-closed signal, MTF, order, and exit cases;
- zero real-data access;
- zero holdout access;
- zero performance metrics;
- zero comparisons or rankings;
- zero report writes;
- zero enabled permissions.

All checks are required. Any failed check rejects the correction for progression.

## Decisions

Allowed decisions:

- `PREFLIGHT_PASSED`
- `PREFLIGHT_FAILED`
- `CORRECTION_ACCEPTED_INDEPENDENT_SYNTHETIC_ONLY`
- `CORRECTION_REJECTED_INDEPENDENT_SYNTHETIC_ONLY`

Acceptance does not establish profitability, robustness on historical data, candidate superiority, paper-trading readiness, or execution permission.

## Recommended next phase

Only after full 2G acceptance:

`PHASE_10_42R_2H_FROZEN_RECOVERY_CANDIDATE_CONTROLLED_HISTORICAL_EVALUATION_PREREGISTRATION_V1`

Phase 2H must preregister the evaluation protocol before any real or historical dataset is accessed.
