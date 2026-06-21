from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.journal.forward_observation_intake_v1 import (
    OPTIONAL_RESOLUTION_COLUMNS,
    REQUIRED_INTAKE_COLUMNS,
    build_empty_intake_template,
)


TEMPLATE_COLUMNS = REQUIRED_INTAKE_COLUMNS + OPTIONAL_RESOLUTION_COLUMNS + [
    "data_source",
    "screenshot_path",
]


def build_manual_forward_observation_template() -> pd.DataFrame:
    return build_empty_intake_template()


def build_manual_forward_observation_sample() -> pd.DataFrame:
    rows = [
        {
            "observed_at": "2026-06-21 01:00:00",
            "symbol": "BTCUSDT",
            "timeframe": "15m",
            "cost_profile": "BINANCE_SCALP_BASE_ESTIMATE",
            "context_name": "NORMAL_VALIDATION_CONTEXT",
            "direction": "SHORT",
            "entry_theoretical": 65000.0,
            "stop_theoretical": 65500.0,
            "target_theoretical": 63750.0,
            "invalidation_level": 65500.0,
            "invalidation_reason": "Example only. Stop above theoretical invalidation zone.",
            "manual_reviewer": "manual_review_required",
            "manual_notes": "Example row only. Not a real signal and not a trade.",
            "resolve_now": True,
            "observed_exit": 63750.0,
            "exit_reason": "EXAMPLE_THEORETICAL_TARGET_REACHED",
            "max_favorable_excursion_r": 2.5,
            "max_adverse_excursion_r": -0.25,
            "bars_to_resolution": 24,
            "data_source": "manual_forward_observation_template_v1_sample",
            "screenshot_path": "",
        },
        {
            "observed_at": "2026-06-21 02:00:00",
            "symbol": "BTCUSDT",
            "timeframe": "15m",
            "cost_profile": "QUANTFURY_SWING_BASE_ESTIMATE",
            "context_name": "WAVE_5_CAUTION_CONTEXT",
            "direction": "SHORT",
            "entry_theoretical": 66000.0,
            "stop_theoretical": 66800.0,
            "target_theoretical": 64000.0,
            "invalidation_level": 66800.0,
            "invalidation_reason": "Example only. Invalidation above local structure.",
            "manual_reviewer": "manual_review_required",
            "manual_notes": "Example open observation. Not a real signal and not a trade.",
            "resolve_now": False,
            "observed_exit": "",
            "exit_reason": "",
            "max_favorable_excursion_r": "",
            "max_adverse_excursion_r": "",
            "bars_to_resolution": "",
            "data_source": "manual_forward_observation_template_v1_sample",
            "screenshot_path": "",
        },
    ]

    return pd.DataFrame(rows, columns=TEMPLATE_COLUMNS)


def build_manual_forward_observation_dictionary() -> pd.DataFrame:
    rows = [
        {
            "column": "observed_at",
            "required": True,
            "type": "datetime text",
            "allowed_values": "YYYY-MM-DD HH:MM:SS",
            "description": "Date and time when the theoretical signal was observed.",
        },
        {
            "column": "symbol",
            "required": True,
            "type": "text",
            "allowed_values": "Example: BTCUSDT",
            "description": "Observed market symbol.",
        },
        {
            "column": "timeframe",
            "required": True,
            "type": "text",
            "allowed_values": "Example: 15m, 1h, 4h, 1d",
            "description": "Chart timeframe used for the observation.",
        },
        {
            "column": "cost_profile",
            "required": True,
            "type": "text",
            "allowed_values": "BINANCE_SCALP_BASE_ESTIMATE, QUANTFURY_SWING_BASE_ESTIMATE",
            "description": "Cost profile to test the observation under.",
        },
        {
            "column": "context_name",
            "required": True,
            "type": "text",
            "allowed_values": "NORMAL_VALIDATION_CONTEXT, WAVE_5_CAUTION_CONTEXT, STRONG_MTF_CONTEXT, WAVE_3_OPPORTUNITY_CONTEXT",
            "description": "Manual market context classification.",
        },
        {
            "column": "direction",
            "required": True,
            "type": "text",
            "allowed_values": "SHORT, LONG",
            "description": "Theoretical direction of the observed signal.",
        },
        {
            "column": "entry_theoretical",
            "required": True,
            "type": "float",
            "allowed_values": "Positive price",
            "description": "Theoretical entry price. This is not an executed entry.",
        },
        {
            "column": "stop_theoretical",
            "required": True,
            "type": "float",
            "allowed_values": "Positive price",
            "description": "Theoretical stop price. For SHORT it must be above entry. For LONG it must be below entry.",
        },
        {
            "column": "target_theoretical",
            "required": True,
            "type": "float",
            "allowed_values": "Positive price",
            "description": "Theoretical target price. For SHORT it must be below entry. For LONG it must be above entry.",
        },
        {
            "column": "invalidation_level",
            "required": True,
            "type": "float",
            "allowed_values": "Positive price",
            "description": "Manual price level that invalidates the idea.",
        },
        {
            "column": "invalidation_reason",
            "required": True,
            "type": "text",
            "allowed_values": "Free text",
            "description": "Why the observation should be invalidated if that level is reached.",
        },
        {
            "column": "manual_reviewer",
            "required": True,
            "type": "text",
            "allowed_values": "Free text",
            "description": "Person or process responsible for manual review.",
        },
        {
            "column": "manual_notes",
            "required": True,
            "type": "text",
            "allowed_values": "Free text",
            "description": "Manual notes about context, setup quality, liquidity, Fibonacci, Elliott or invalidation.",
        },
        {
            "column": "resolve_now",
            "required": False,
            "type": "boolean",
            "allowed_values": "True, False",
            "description": "Whether the observation is already resolved at intake time.",
        },
        {
            "column": "observed_exit",
            "required": False,
            "type": "float",
            "allowed_values": "Positive price or blank",
            "description": "Observed theoretical exit price if the observation is already resolved.",
        },
        {
            "column": "exit_reason",
            "required": False,
            "type": "text",
            "allowed_values": "Free text or blank",
            "description": "Reason why the observation was resolved.",
        },
        {
            "column": "max_favorable_excursion_r",
            "required": False,
            "type": "float",
            "allowed_values": "R multiple or blank",
            "description": "Maximum favorable movement in R before resolution.",
        },
        {
            "column": "max_adverse_excursion_r",
            "required": False,
            "type": "float",
            "allowed_values": "R multiple or blank",
            "description": "Maximum adverse movement in R before resolution.",
        },
        {
            "column": "bars_to_resolution",
            "required": False,
            "type": "integer",
            "allowed_values": "Integer or blank",
            "description": "Number of bars from observation to resolution.",
        },
        {
            "column": "data_source",
            "required": False,
            "type": "text",
            "allowed_values": "Free text",
            "description": "Manual source label. Example: TradingView manual observation.",
        },
        {
            "column": "screenshot_path",
            "required": False,
            "type": "text",
            "allowed_values": "File path or blank",
            "description": "Optional screenshot path for later review.",
        },
    ]

    return pd.DataFrame(rows)


def build_manual_forward_observation_guide() -> str:
    return """# Manual Forward Observation CSV Template V1

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
"""


def save_manual_forward_observation_bundle(output_dir: Path) -> dict[str, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)

    template_path = output_dir / "manual_forward_observation_template_v1.csv"
    sample_path = output_dir / "manual_forward_observation_sample_v1.csv"
    dictionary_path = output_dir / "manual_forward_observation_dictionary_v1.csv"
    guide_path = output_dir / "MANUAL_FORWARD_OBSERVATION_TEMPLATE_V1.md"

    template_df = build_manual_forward_observation_template()
    sample_df = build_manual_forward_observation_sample()
    dictionary_df = build_manual_forward_observation_dictionary()
    guide_text = build_manual_forward_observation_guide()

    template_df.to_csv(template_path, index=False)
    sample_df.to_csv(sample_path, index=False)
    dictionary_df.to_csv(dictionary_path, index=False)
    guide_path.write_text(guide_text, encoding="utf-8")

    return {
        "template_path": template_path,
        "sample_path": sample_path,
        "dictionary_path": dictionary_path,
        "guide_path": guide_path,
    }


def validate_manual_forward_observation_bundle(output_dir: Path) -> pd.DataFrame:
    template_path = output_dir / "manual_forward_observation_template_v1.csv"
    sample_path = output_dir / "manual_forward_observation_sample_v1.csv"
    dictionary_path = output_dir / "manual_forward_observation_dictionary_v1.csv"
    guide_path = output_dir / "MANUAL_FORWARD_OBSERVATION_TEMPLATE_V1.md"

    checks = []

    for path in [template_path, sample_path, dictionary_path, guide_path]:
        checks.append(
            {
                "check_name": "file_exists",
                "target": str(path),
                "passed": path.exists(),
            }
        )

    if template_path.exists():
        template_df = pd.read_csv(template_path)
        checks.append(
            {
                "check_name": "template_columns_match",
                "target": str(template_path),
                "passed": list(template_df.columns) == TEMPLATE_COLUMNS,
            }
        )

    if sample_path.exists():
        sample_df = pd.read_csv(sample_path)
        checks.append(
            {
                "check_name": "sample_columns_match",
                "target": str(sample_path),
                "passed": list(sample_df.columns) == TEMPLATE_COLUMNS,
            }
        )
        checks.append(
            {
                "check_name": "sample_has_rows",
                "target": str(sample_path),
                "passed": len(sample_df) > 0,
            }
        )

    if dictionary_path.exists():
        dictionary_df = pd.read_csv(dictionary_path)
        checks.append(
            {
                "check_name": "dictionary_covers_all_template_columns",
                "target": str(dictionary_path),
                "passed": set(dictionary_df["column"].astype(str).tolist()) == set(TEMPLATE_COLUMNS),
            }
        )

    return pd.DataFrame(checks)