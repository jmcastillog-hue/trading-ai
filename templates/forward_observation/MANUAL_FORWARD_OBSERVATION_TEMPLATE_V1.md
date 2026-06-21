# Manual Forward Observation CSV Template V1

## Purpose

This template is used to manually record forward-observed theoretical signals.

It is not an execution file.

It is not a paper trading order file.

It is not a Binance, Quantfury or broker execution instruction.

## Allowed Use

Allowed:

- Manual forward observation
- Theoretical signal recording
- Manual review
- Result tracking in R
- Dataset building

Not allowed:

- Real capital execution
- Paper trading execution
- Live trading alerts
- Automated order execution
- Autonomous bot behavior

## How To Use

1. Open `manual_forward_observation_template_v1.csv`.
2. Copy the header row into a working CSV file.
3. Add one row per observed theoretical setup.
4. Keep all required fields completed.
5. Use `resolve_now=False` for open observations.
6. Use `resolve_now=True` only when the observation already has an observed theoretical exit.
7. Save your working file separately.
8. Process it with the intake workflow in later phases.

## Required Signal Rule

For SHORT observations:

- `stop_theoretical` must be above `entry_theoretical`
- `target_theoretical` must be below `entry_theoretical`

For LONG observations:

- `stop_theoretical` must be below `entry_theoretical`
- `target_theoretical` must be above `entry_theoretical`

## Evidence Rule

The minimum evidence threshold remains:

- 100 forward-observed signals minimum
- 300 forward-observed signals preferred

Synthetic examples do not count as market evidence.

## Current Project Restriction

The project remains observational only.

No execution is authorized.
