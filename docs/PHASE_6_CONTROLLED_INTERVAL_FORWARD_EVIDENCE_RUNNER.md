# PHASE 6 CONTROLLED INTERVAL FORWARD EVIDENCE RUNNER

## Status

Phase 6.5 adds a controlled interval runner for forward evidence collection.

This runner can execute the Phase 6.4 controlled cycle multiple times with a fixed interval between cycles.

This phase is not trade automation.

This phase is not paper trading execution.

This phase is not live alerting.

This phase is not exchange execution.

This phase only repeats evidence collection cycles under strict safety controls.

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

## Controlled interval sequence

Each interval cycle runs:

```text
1. Controlled Forward Evidence Cycle Runner V1
2. Operational Safety Guard / Preflight
3. Operational Forward Evidence Bootstrap
4. Operational Input File Validator Adapter
5. Operational Persistent Cycle Integration
6. Forward Evidence Run Log
7. Cycle summary capture
```

The interval runner then waits for the configured number of seconds and repeats until `max_cycles` is reached or a blocking condition appears.

## Development mode

During Phase 6.5 development, the workflow may run with:

```text
require_clean_git = False
max_cycles = 2
interval_seconds = 5
```

This is only for validation while new files are uncommitted.

For real controlled evidence monitoring, the future recommended mode is:

```text
require_clean_git = True
max_cycles = limited and explicit
interval_seconds = 900 or 1800
```

That means one cycle every 15 or 30 minutes.

## Valid interval decisions

```text
CONTROLLED_INTERVAL_COMPLETED
CONTROLLED_INTERVAL_STOPPED_ON_FAILED_CYCLE
CONTROLLED_INTERVAL_STOPPED_ON_EXECUTION_FLAG
CONTROLLED_INTERVAL_FAILED
```

## Valid cycle decisions inside interval mode

```text
CONTROLLED_CYCLE_COMPLETED_WITH_EVIDENCE
CONTROLLED_CYCLE_COMPLETED_NO_DATASET_CHANGES
CONTROLLED_CYCLE_WAITING_FOR_INPUTS
```

Blocking cycle decisions:

```text
CONTROLLED_CYCLE_BLOCKED_BY_PREFLIGHT
CONTROLLED_CYCLE_FAILED
```

## Expected validation decision

```text
PHASE_6_5_CONTROLLED_INTERVAL_FORWARD_EVIDENCE_RUNNER_VALIDATED
```

## Final operating rule

The interval runner may repeat evidence collection cycles.

It must never place orders.

It must never connect to Binance execution.

It must never connect to Quantfury execution.

It must never send live trade alerts.

It must never enable paper trading execution.

The system remains an evidence machine.

The system is still not a trading bot.
