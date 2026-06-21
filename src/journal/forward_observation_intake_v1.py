from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd

from src.journal.forward_signal_journal_v1 import (
    ForwardSignalJournalConfig,
    summarize_forward_signal_journal,
    validate_forward_signal_journal,
)
from src.journal.forward_signal_recorder_v1 import (
    ForwardObservedSignalInput,
    append_forward_observed_signal,
    load_journal_or_empty,
    resolve_forward_signal,
    save_journal,
)


REQUIRED_INTAKE_COLUMNS = [
    "observed_at",
    "symbol",
    "timeframe",
    "cost_profile",
    "context_name",
    "direction",
    "entry_theoretical",
    "stop_theoretical",
    "target_theoretical",
    "invalidation_level",
    "invalidation_reason",
    "manual_reviewer",
    "manual_notes",
]


OPTIONAL_RESOLUTION_COLUMNS = [
    "resolve_now",
    "observed_exit",
    "exit_reason",
    "max_favorable_excursion_r",
    "max_adverse_excursion_r",
    "bars_to_resolution",
]


@dataclass(frozen=True)
class ForwardObservationIntakeConfig:
    min_forward_signals: int = 100
    preferred_forward_signals: int = 300
    max_candidate_theoretical_risk_pct: float = 0.0050
    max_watchlist_theoretical_risk_pct: float = 0.0025
    allow_resolution_from_intake: bool = True


def safe_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None or pd.isna(value):
            return default
        return float(value)
    except Exception:
        return default


def safe_int(value: Any, default: int = 0) -> int:
    try:
        if value is None or pd.isna(value):
            return default
        return int(value)
    except Exception:
        return default


def safe_bool(value: Any, default: bool = False) -> bool:
    if value is None or pd.isna(value):
        return default

    if isinstance(value, bool):
        return value

    value_text = str(value).strip().lower()

    if value_text in ["true", "1", "yes", "y", "si", "sí"]:
        return True

    if value_text in ["false", "0", "no", "n"]:
        return False

    return default


def normalize_text(value: str | None) -> str:
    if value is None:
        return ""

    return str(value).strip().upper()


def build_empty_intake_template() -> pd.DataFrame:
    columns = REQUIRED_INTAKE_COLUMNS + OPTIONAL_RESOLUTION_COLUMNS + [
        "data_source",
        "screenshot_path",
    ]

    return pd.DataFrame(columns=columns)


def validate_intake_columns(intake_df: pd.DataFrame) -> list[dict]:
    errors = []

    for column in REQUIRED_INTAKE_COLUMNS:
        if column not in intake_df.columns:
            errors.append(
                {
                    "severity": "ERROR",
                    "check_name": "missing_required_intake_column",
                    "details": column,
                }
            )

    return errors


def validate_intake_row(row: pd.Series, row_number: int) -> list[dict]:
    errors = []

    for column in REQUIRED_INTAKE_COLUMNS:
        value = row.get(column, None)

        if value is None or pd.isna(value) or str(value).strip() == "":
            errors.append(
                {
                    "severity": "ERROR",
                    "check_name": "missing_required_value",
                    "details": f"row={row_number}; column={column}",
                }
            )

    direction = normalize_text(row.get("direction"))

    if direction not in ["SHORT", "LONG"]:
        errors.append(
            {
                "severity": "ERROR",
                "check_name": "invalid_direction",
                "details": f"row={row_number}; direction={direction}",
            }
        )

    entry = safe_float(row.get("entry_theoretical"), 0.0)
    stop = safe_float(row.get("stop_theoretical"), 0.0)
    target = safe_float(row.get("target_theoretical"), 0.0)

    if entry <= 0 or stop <= 0 or target <= 0:
        errors.append(
            {
                "severity": "ERROR",
                "check_name": "invalid_price_level",
                "details": f"row={row_number}; entry={entry}; stop={stop}; target={target}",
            }
        )

    if direction == "SHORT":
        if not stop > entry:
            errors.append(
                {
                    "severity": "ERROR",
                    "check_name": "invalid_short_stop",
                    "details": f"row={row_number}; stop must be above entry",
                }
            )

        if not target < entry:
            errors.append(
                {
                    "severity": "ERROR",
                    "check_name": "invalid_short_target",
                    "details": f"row={row_number}; target must be below entry",
                }
            )

    if direction == "LONG":
        if not stop < entry:
            errors.append(
                {
                    "severity": "ERROR",
                    "check_name": "invalid_long_stop",
                    "details": f"row={row_number}; stop must be below entry",
                }
            )

        if not target > entry:
            errors.append(
                {
                    "severity": "ERROR",
                    "check_name": "invalid_long_target",
                    "details": f"row={row_number}; target must be above entry",
                }
            )

    return errors


def build_signal_input_from_row(row: pd.Series) -> ForwardObservedSignalInput:
    return ForwardObservedSignalInput(
        observed_at=str(row.get("observed_at")),
        symbol=str(row.get("symbol")),
        timeframe=str(row.get("timeframe")),
        cost_profile=str(row.get("cost_profile")),
        context_name=str(row.get("context_name")),
        direction=str(row.get("direction")),
        entry_theoretical=safe_float(row.get("entry_theoretical")),
        stop_theoretical=safe_float(row.get("stop_theoretical")),
        target_theoretical=safe_float(row.get("target_theoretical")),
        invalidation_level=safe_float(row.get("invalidation_level")),
        invalidation_reason=str(row.get("invalidation_reason")),
        manual_reviewer=str(row.get("manual_reviewer")),
        manual_notes=str(row.get("manual_notes")),
        data_source=str(row.get("data_source", "forward_observation_intake_v1")),
        screenshot_path=str(row.get("screenshot_path", "")),
    )


def process_forward_observation_intake(
    intake_df: pd.DataFrame,
    template_df: pd.DataFrame,
    journal_path: Path,
    config: ForwardObservationIntakeConfig | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    if config is None:
        config = ForwardObservationIntakeConfig()

    errors = validate_intake_columns(intake_df)

    if errors:
        errors_df = pd.DataFrame(errors)
        empty = pd.DataFrame()
        return empty, empty, empty, empty, errors_df

    journal_df = load_journal_or_empty(journal_path)

    accepted_rows = []
    rejected_rows = []

    for index, row in intake_df.iterrows():
        row_number = index + 1

        row_errors = validate_intake_row(row, row_number)

        if row_errors:
            rejected = row.to_dict()
            rejected["rejection_reason"] = ";".join(
                error["check_name"] for error in row_errors
            )
            rejected_rows.append(rejected)
            errors.extend(row_errors)
            continue

        try:
            signal_input = build_signal_input_from_row(row)

            before_count = len(journal_df)

            journal_df = append_forward_observed_signal(
                journal_df=journal_df,
                template_df=template_df,
                signal_input=signal_input,
            )

            signal_id = str(journal_df["signal_id"].iloc[-1])

            if (
                config.allow_resolution_from_intake
                and safe_bool(row.get("resolve_now"), False)
            ):
                journal_df = resolve_forward_signal(
                    journal_df=journal_df,
                    signal_id=signal_id,
                    observed_exit=safe_float(row.get("observed_exit")),
                    exit_reason=str(row.get("exit_reason", "INTAKE_RESOLUTION")),
                    max_favorable_excursion_r=safe_float(
                        row.get("max_favorable_excursion_r"),
                        0.0,
                    ),
                    max_adverse_excursion_r=safe_float(
                        row.get("max_adverse_excursion_r"),
                        0.0,
                    ),
                    bars_to_resolution=safe_int(row.get("bars_to_resolution"), 0),
                )

            accepted = row.to_dict()
            accepted["signal_id"] = signal_id
            accepted["journal_rows_before"] = before_count
            accepted["journal_rows_after"] = len(journal_df)
            accepted_rows.append(accepted)

        except Exception as exc:
            rejected = row.to_dict()
            rejected["rejection_reason"] = repr(exc)
            rejected_rows.append(rejected)

            errors.append(
                {
                    "severity": "ERROR",
                    "check_name": "intake_processing_error",
                    "details": f"row={row_number}; error={repr(exc)}",
                }
            )

    save_journal(journal_df, journal_path)

    journal_config = ForwardSignalJournalConfig(
        min_forward_signals=config.min_forward_signals,
        preferred_forward_signals=config.preferred_forward_signals,
        max_candidate_theoretical_risk_pct=config.max_candidate_theoretical_risk_pct,
        max_watchlist_theoretical_risk_pct=config.max_watchlist_theoretical_risk_pct,
    )

    validation_df, validation_summary = validate_forward_signal_journal(
        journal_df=journal_df,
        config=journal_config,
    )

    journal_summary_df = summarize_forward_signal_journal(journal_df)
    validation_summary_df = pd.DataFrame([validation_summary])

    accepted_df = pd.DataFrame(accepted_rows)
    rejected_df = pd.DataFrame(rejected_rows)

    if errors:
        errors_df = pd.DataFrame(errors)
    else:
        errors_df = pd.DataFrame(columns=["severity", "check_name", "details"])

    if not validation_df.empty:
        errors_df = pd.concat(
            [
                errors_df,
                validation_df,
            ],
            ignore_index=True,
        )

    return journal_df, accepted_df, rejected_df, validation_summary_df, journal_summary_df, errors_df


def build_sample_intake_rows() -> pd.DataFrame:
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
            "invalidation_reason": "Synthetic validation intake row.",
            "manual_reviewer": "manual_review_required",
            "manual_notes": "Synthetic intake row. Not a real market signal.",
            "resolve_now": True,
            "observed_exit": 63750.0,
            "exit_reason": "THEORETICAL_TARGET_REACHED_SYNTHETIC_VALIDATION",
            "max_favorable_excursion_r": 2.5,
            "max_adverse_excursion_r": -0.25,
            "bars_to_resolution": 24,
            "data_source": "forward_observation_intake_v1_validation",
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
            "invalidation_reason": "Synthetic validation intake row.",
            "manual_reviewer": "manual_review_required",
            "manual_notes": "Synthetic intake row. Not a real market signal.",
            "resolve_now": False,
            "observed_exit": "",
            "exit_reason": "",
            "max_favorable_excursion_r": "",
            "max_adverse_excursion_r": "",
            "bars_to_resolution": "",
            "data_source": "forward_observation_intake_v1_validation",
            "screenshot_path": "",
        },
    ]

    return pd.DataFrame(rows)
