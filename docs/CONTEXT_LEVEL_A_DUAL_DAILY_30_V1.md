> **Superseded before activation:** This V1 design was never
> initialized and has no real cohort observations. It is retained only for
> auditability. Activation fails closed and the prospective replacement is
> `CONTEXT_LEVEL_A_DUAL_DAILY_30_V2`. Missed V1 slots must not be backfilled.

# CONTEXT_LEVEL_A_DUAL_DAILY_30_V1

## Purpose

Prospective context-evaluation cohort adapted to supervised human availability in Chile while preserving the frozen hypothesis manifest and the existing prospective-cohort safety rules. This cohort is additive and independent from `CONTEXT_LEVEL_A_ROTATING_DAILY_30_V1`; no observation is moved, copied, or retrospectively substituted between cohorts.

## Freeze and binding

- Cohort ID: `CONTEXT_LEVEL_A_DUAL_DAILY_30_V1`
- Plan freeze: `2026-08-31T00:57:00+00:00`
- Hypothesis manifest SHA-256: `4de33a61d2a1456e6bd673ddd044cd0c01bb3369d30595ec57773df1d922442b`
- Hypothesis freeze: `2026-08-22T16:15:00+00:00`
- Canonical plan SHA-256: `ed79215f607f66a46ccb992d0b870c2cd95d829dda0dc18a700728972b80f8fa`
- Sampling mode: `PREDECLARED_UTC_CONTEXT_ANCHORS`
- Planned slots: 30
- Required outcome horizons remain H2/H4/H16 through the frozen hypothesis manifest.

## Human schedule

The user-facing routine is fixed at two Chile-local anchors per day:

- Morning context anchor: **06:30 Chile**. Synchronized capture target: **06:15:05 Chile**. Recommended human start: about **06:05 Chile**.
- Evening context anchor: **18:30 Chile**. Synchronized capture target: **18:15:05 Chile**. Recommended human start: about **18:05 Chile**.

The plan is frozen in UTC, not local time. Chile changes from UTC-04 to UTC-03 on 2026-09-06. Therefore:

- 2026-09-01 through 2026-09-05: anchors are 10:30Z and 22:30Z.
- 2026-09-06 through 2026-09-15: anchors are 09:30Z and 21:30Z.

The DST transition creates one 11-hour UTC gap between S010 and S011; every other adjacent gap is 12 hours. Both are well above the frozen minimum spacing of 4 hours (16 x 15-minute bars), and H16 outcome windows do not overlap adjacent anchors.

## Scientific and operational guards

- No slot is selected from market state, direction, price, volatility, candidate presence, or outcome.
- Missed slots remain missed; no retrospective capture or replacement slot is permitted.
- Admission cannot read forward outcomes and must occur before H2 completion.
- Outcome binding requires all preregistered horizons and cannot select on outcome value.
- No feature ranking, p-values, significance claims, quality gate, edge claim, signal generation, paper trading, live trading, exchange execution, background scheduling, or official append is introduced by this cohort.
- Real market capture remains supervised foreground execution.
- Closed V1 components are not modified; the reusable runner verifies their Git blob identities before real operations.

## Reusable runner

`tools/context_evaluation_dual_daily_runner_v1.py` is the single slot-parametrized control surface. It does not duplicate or alter the closed components. Instead it verifies and derives the already real-world-validated S008 context and outcome runners from frozen reference templates.

Supported modes:

- `--self-check`: offline static/template/plan checks only.
- `--initialize-root`: create-only initialization of the external cohort root.
- `--status`: read-only cohort/slot status without outcome values.
- `--offline-validate-context --slot Sxxx`: complete synthetic end-to-end context/admission validation; zero real HTTP.
- `--execute-context --slot Sxxx --source-attestation ...`: one supervised real context capture/admission.
- `--offline-validate-binding --slot Sxxx`: synthetic future-outcome and binding validation after that slot has a real admission; zero real HTTP.
- `--bind-outcomes --slot Sxxx --source-attestation ...`: one supervised public future-candle capture and create-only outcome binding after H16 maturity.

The runner never displays forward-return values in status or binding certification.
