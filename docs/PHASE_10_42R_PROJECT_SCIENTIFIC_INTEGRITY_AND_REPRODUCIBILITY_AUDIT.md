# Phase 10.42R — Project Scientific Integrity and Reproducibility Audit V1

## Status

Corrective audit and closed-candle MTF remediation.

This phase is inserted after Phase 10.42 and before Phase 10.43 because a
project-wide audit identified higher-timeframe feature availability and clean
clone reproducibility as material blockers.

## Finding

Binance kline timestamps represent candle opens. The prior MTF regime and
Directional Context V3/V3.1 paths calculated features from each complete 1H or
4H candle and merged them at that open timestamp. Lower-timeframe rows could
therefore receive information from a higher-timeframe candle that had not yet
closed.

## Remediation contract

Every higher-timeframe feature row must satisfy:

```text
source_open_timestamp = Binance kline open timestamp
feature_available_at = source_open_timestamp + timeframe duration
merge timestamp = feature_available_at
```

Supported durations are explicit. Duplicate or invalid higher-timeframe
timestamps fail closed.

The correction is applied to:

- `src/market_structure/mtf_regime_filter.py`
- `src/market_structure/directional_context_filter_v3.py`

The shared contract is implemented in:

- `src/market_structure/closed_candle_mtf.py`

## Reproducibility remediation

Phase 10.42R restores a non-empty dependency manifest and adds deterministic
standard-library unit tests. It also introduces a workflow whose process exit
code is non-zero when the corrective audit itself fails.

## Candidate decision

The following candidates move to `REVALIDATION_REQUIRED`:

- `TARGET_SHORT_FIB_V5_MTF_V3_1 + FIXED_RR_2_5`
- `LONG_BASE_FAILED_BREAKDOWN_V1`
- `LONG_BASE_LIQUIDITY_SWEEP_V1`

This is not a strategy rejection. Prior performance metrics remain historical
records but are not certified after the closed-candle correction.

## Safety boundary

This phase does not:

- create or write the official dataset
- collect real forward evidence
- generate an actionable signal
- enable a live alert
- execute a paper trade
- use real capital
- connect to an exchange for order execution
- enable automation
- approve SHORT or LONG execution
- complete the project

## Passing decision

`PHASE_10_42R_PROJECT_SCIENTIFIC_INTEGRITY_AND_REPRODUCIBILITY_AUDIT_VALIDATED_REVALIDATION_REQUIRED`

A passing decision validates the corrective controls only. It does not certify
strategy performance or permit forward observation.

## Recommended next phase

`PHASE_10_42R_2_SHORT_LONG_CLOSED_CANDLE_MTF_REVALIDATION_V1`

Phase 10.42R.2 must repeat the affected SHORT and LONG historical, OOS,
walk-forward, cost-aware and risk validations. Phase 10.43 remains paused until
the corrected evidence has been reviewed.
