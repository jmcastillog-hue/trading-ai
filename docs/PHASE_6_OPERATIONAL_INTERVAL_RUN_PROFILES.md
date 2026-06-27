# PHASE 6 OPERATIONAL INTERVAL RUN PROFILES

## Status

Phase 6.6 defines safe operational interval run profiles for forward evidence collection.

This phase does not execute long-running monitoring.

This phase does not execute trades.

This phase does not enable paper trading execution.

This phase does not connect to Binance.

This phase does not connect to Quantfury.

This phase does not send live alerts.

This phase only defines and validates interval profiles that can later be used by the controlled interval runner.

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

The project can now repeat controlled evidence cycles.

However, repeated cycles should never be launched with improvised values.

This phase defines named run profiles:

```text
DEV_TEST
SHORT_OBSERVATION
HALF_HOUR_MONITOR
TWO_HOUR_MONITOR
DAILY_OBSERVATION
```

## Profile definitions

### DEV_TEST

```text
max_cycles = 2
interval_seconds = 5
require_clean_git = False
estimated_duration = very short
purpose = development validation only
```

### SHORT_OBSERVATION

```text
max_cycles = 4
interval_seconds = 60
require_clean_git = True
estimated_duration = about 3 minutes of waiting plus execution time
purpose = short local observation
```

### HALF_HOUR_MONITOR

```text
max_cycles = 2
interval_seconds = 900
require_clean_git = True
estimated_duration = about 15 minutes of waiting plus execution time
purpose = short market observation
```

### TWO_HOUR_MONITOR

```text
max_cycles = 8
interval_seconds = 900
require_clean_git = True
estimated_duration = about 105 minutes of waiting plus execution time
purpose = controlled two-hour observation
```

### DAILY_OBSERVATION

```text
max_cycles = 48
interval_seconds = 1800
require_clean_git = True
estimated_duration = about 23.5 hours of waiting plus execution time
purpose = daily observation mode
```

## Safety rules

A profile is valid only if:

```text
profile name exists
max_cycles is positive
interval_seconds is positive
duration is bounded
execution flags remain False
long-running profiles require clean Git
profile is explicit and named
```

Development profiles may use:

```text
require_clean_git = False
```

Operational profiles must use:

```text
require_clean_git = True
```

## Valid profile decisions

```text
PROFILE_VALIDATED
PROFILE_VALIDATED_WITH_WARNINGS
PROFILE_BLOCKED
```

## Expected validation decision

```text
PHASE_6_6_OPERATIONAL_INTERVAL_RUN_PROFILES_VALIDATED
```

## Final operating rule

No long interval run should be started without selecting a named profile.

The system remains an evidence machine.

The system is still not a trading bot.
