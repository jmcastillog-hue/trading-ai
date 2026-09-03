# CONTEXT_LEVEL_A_DUAL_DAILY_30_V2

## Status and supersession

This is the active prospective design. It supersedes
`CONTEXT_LEVEL_A_DUAL_DAILY_30_V1` before initialization or any real
observation. V1 remains preserved for auditability, but its activation paths
fail closed. No V1 slot is moved, repeated, replaced, or backfilled.

The prior scientific observation `S008` from
`CONTEXT_LEVEL_A_ROTATING_DAILY_30_V1` remains unchanged and is not part of
this cohort. Its outcomes were not used to choose V2 times or parameters.

## Freeze and binding

- Cohort ID: `CONTEXT_LEVEL_A_DUAL_DAILY_30_V2`
- Plan freeze: `2026-09-03T00:20:00+00:00`
- Hypothesis manifest SHA-256: `4de33a61d2a1456e6bd673ddd044cd0c01bb3369d30595ec57773df1d922442b`
- Hypothesis freeze: `2026-08-22T16:15:00+00:00`
- Canonical plan SHA-256: `fc1094fa9aab3cf5d683c396c3e179601f24260d04f30c2dca26d1e322ddc41b`
- Sampling mode: `PREDECLARED_UTC_CONTEXT_ANCHORS`
- Planned slots: 30 over 15 consecutive days.
- Required outcome horizons: H2/H4/H16 through the frozen hypothesis.

## Frozen human schedule

The local routine is fixed at two Chile anchors per day:

- Morning anchor: **06:30 Chile**. Capture target: **06:15:05 Chile**.
  Recommended supervised start: about **06:05 Chile**.
- Evening anchor: **18:30 Chile**. Capture target: **18:15:05 Chile**.
  Recommended supervised start: about **18:05 Chile**.

Individual UTC timestamps are frozen in the plan:

- 2026-09-04 through 2026-09-05, Chile UTC-04: 10:30Z and 22:30Z.
- 2026-09-06 through 2026-09-18, Chile UTC-03: 09:30Z and 21:30Z.

The DST transition creates one 11-hour UTC gap between S004 and S005. Every
other adjacent gap is 12 hours. All gaps exceed the frozen four-hour minimum,
and the H16 windows do not overlap adjacent anchors.

## External evidence root and Windows path budget

The default V2 evidence root on Windows is `C:\TAE`. This short root is
outside the Git repository and avoids the path-budget issue found in V1.
`TRADING_AI_EVIDENCE_ROOT` may override it only with an absolute, external,
short path. The runner rejects a drive root, the user home, the repository,
an ancestor or descendant of the repository, roots longer than 64 characters,
or a projected evidence path longer than 239 characters.

The reusable runner explicitly rebinds every transformed context and outcome
template path to this V2 root. Therefore cohort admissions, run artifacts,
offline sandboxes, future captures, and bindings cannot silently split between
the old `TradingAI-Evidence` root and the V2 root.

## Scientific and operational guards

- No selection uses market state, direction, price, volatility, candidate
  presence, or outcome.
- Missed slots remain missed. Retrospective capture and replacement slots are
  prohibited.
- Admission cannot read forward outcomes and must occur before H2 completion.
- Outcome binding requires all preregistered horizons and occurs only after H16.
- Microstructure V1.1 authorization propagation remains frozen and verified.
- The official evidence append gate must remain disabled.
- No quality gate, edge claim, signal, paper trading, capital execution,
  authenticated exchange action, browser automation, messaging, or unattended
  scheduling is introduced.
- Real market-data use remains one-shot, foreground, and human supervised.
- If a network phase is entered and fails, the capture is not repeated
  automatically and partial evidence is preserved for diagnosis.

## Runner modes

`tools/context_evaluation_dual_daily_runner_v2.py` is the only V2 control
surface:

- `--self-check`: static plan, transform, root, and path checks; zero network.
- `--initialize-root`: create-only V2 cohort initialization after merge/push.
- `--status`: read-only cohort or slot status; no outcome values.
- `--offline-validate-context --slot Sxxx`: synthetic context/admission path.
- `--execute-context --slot Sxxx --source-attestation ...`: one supervised
  public context capture/admission.
- `--offline-validate-binding --slot Sxxx`: synthetic outcome/binding path
  after the real admission exists.
- `--bind-outcomes --slot Sxxx --source-attestation ...`: one supervised public
  future-candle capture and create-only binding after H16 maturity.

Implementation validation does not initialize `C:\TAE`, perform HTTP calls,
fetch market data, or create any real admission or binding.
