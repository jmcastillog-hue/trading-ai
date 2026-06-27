# PHASE 6 OPERATIONAL SAFETY GUARD PREFLIGHT

## Status

Phase 6.3 adds an operational safety guard / preflight layer before any controlled forward evidence cycle.

This phase does not execute trades.

This phase does not connect to exchanges.

This phase does not create live alerts.

This phase validates safety conditions before operational evidence processing.

## Hard restrictions

```text
NO REAL CAPITAL
NO PAPER TRADING EXECUTION
NO LIVE ALERTS
NO BINANCE EXECUTION
NO QUANTFURY EXECUTION
NO EXCHANGE EXECUTION
NO AUTOMATION
NO AUTONOMOUS TRADING BOT BEHAVIOR
```

All execution flags must remain:

```text
paper_trade_execution_allowed = False
real_capital_allowed = False
live_alerts_allowed = False
exchange_execution_allowed = False
automation_allowed = False
execution_allowed = False
```

## Purpose

The preflight guard checks whether the local project state is safe before running the operational evidence workflow.

It checks:

```text
required documentation exists
required Phase 5 and Phase 6 workflows exist
operational folders exist
operational dataset exists
run log exists
Git branch is valid
Git working tree status is known
execution flags remain False
dangerous order execution functions are absent from operational files
```

## Development mode versus strict mode

During development of this phase, the validator may run with `require_clean_git = False` because the new files are still uncommitted.

For future operational evidence cycles, strict mode should require:

```text
Git working tree clean
required runtime files present
execution flags False
no blocker checks
```

## Safe preflight decisions

Valid safe decisions:

```text
OPERATIONAL_PREFLIGHT_VALIDATED
OPERATIONAL_PREFLIGHT_VALIDATED_WITH_WARNINGS
```

Blocking decision:

```text
OPERATIONAL_PREFLIGHT_BLOCKED
```

## Blocking conditions

The preflight must block if:

```text
required source files are missing
required operational directories are missing
operational dataset is missing
run log is missing
execution flags are True
dangerous order execution functions are detected
Git working tree is dirty while strict clean mode is required
```

## Expected validation decision

```text
PHASE_6_3_OPERATIONAL_SAFETY_GUARD_PREFLIGHT_VALIDATED
```

## Final operating rule

No multi-hour or multi-day forward evidence cycle should run until the safety preflight exists and passes.

The system remains an evidence machine.

The system is still not a trading bot.
