# PHASE 6 PROFILE BASED INTERVAL RUNNER

## Status

Phase 6.7 adds a profile-based runner for controlled forward evidence collection.

This phase connects named operational interval profiles with the controlled interval runner.

This phase does not execute trades.

This phase does not enable paper trading execution.

This phase does not connect to Binance.

This phase does not connect to Quantfury.

This phase does not send live alerts.

This phase only allows controlled evidence cycles to run through an explicit named profile.

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

All execution flags must remain:

paper_trade_execution_allowed = False
real_capital_allowed = False
live_alerts_allowed = False
exchange_execution_allowed = False
automation_allowed = False
execution_allowed = False
Purpose

Phase 6.6 defined safe interval profiles.

Phase 6.7 allows the user to select a profile by name and run the controlled interval runner through that profile.

Example:

python -m src.workflows.run_profile_based_interval_forward_evidence_runner_v1 DEV_TEST
Supported profile names
DEV_TEST
SHORT_OBSERVATION
HALF_HOUR_MONITOR
TWO_HOUR_MONITOR
DAILY_OBSERVATION
Validation mode

During Phase 6.7 development, the validation profile is:

DEV_TEST

This profile uses:

max_cycles = 2
interval_seconds = 5
require_clean_git = False

This is acceptable only for development validation.

Operational profiles must require:

require_clean_git = True
Profile-based sequence
1. Receive profile name
2. Validate profile registry
3. Confirm selected profile exists
4. Confirm selected profile is not blocked
5. Convert profile to interval runner config
6. Run controlled interval forward evidence runner
7. Save profile-based summary
8. Confirm execution flags remain False
Valid profile-based decisions
PROFILE_BASED_INTERVAL_RUN_COMPLETED
PROFILE_BASED_INTERVAL_PROFILE_NOT_FOUND
PROFILE_BASED_INTERVAL_PROFILE_BLOCKED
PROFILE_BASED_INTERVAL_RUN_FAILED
Expected validation decision
PHASE_6_7_PROFILE_BASED_INTERVAL_RUNNER_VALIDATED
Final operating rule

A controlled interval run must be launched by explicit named profile.

The system remains an evidence machine.

The system is still not a trading bot.