from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd

from src.journal.forward_signal_journal_v1 import (
    FORWARD_SIGNAL_JOURNAL_COLUMNS,
    ForwardSignalJournalConfig,
    build_empty_forward_signal_journal,
    map_position_mode,
    summarize_forward_signal_journal,
    validate_forward_signal_journal,
)


@dataclass(frozen=True)
class ForwardObservedSignalInput:
    observed_at: str
    symbol: str
    timeframe: str
    cost_profile: str
    context_name: str
    direction: str
    entry_theoretical: float
    stop_theoretical: float
    target_theoretical: float
    invalidation_level: float
    invalidation_reason: str
    manual_reviewer: str
    manual_notes: str
    data_source: str = "manual_forward_observation"
    screenshot_path: str = ""


def safe_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None or pd.isna(value):
            return default
        return float(value)
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


def load_journal_or_empty(path: Path) -> pd.DataFrame:
    if path.exists():
        df = pd.read_csv(path)

        for column in FORWARD_SIGNAL_JOURNAL_COLUMNS:
            if column not in df.columns:
                df[column] = ""

        return df[FORWARD_SIGNAL_JOURNAL_COLUMNS].copy()

    return build_empty_forward_signal_journal()


def save_journal(journal_df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    journal_df.to_csv(path, index=False)


def calculate_theoretical_risk_reward(
    direction: str,
    entry: float,
    stop: float,
    target: float,
) -> float:
    direction = normalize_text(direction)

    entry = safe_float(entry)
    stop = safe_float(stop)
    target = safe_float(target)

    if direction == "SHORT":
        risk = stop - entry
        reward = entry - target
    elif direction == "LONG":
        risk = entry - stop
        reward = target - entry
    else:
        return 0.0

    if risk <= 0:
        return 0.0

    if reward <= 0:
        return 0.0

    return float(reward / risk)


def calculate_theoretical_result_r(
    direction: str,
    entry: float,
    stop: float,
    observed_exit: float,
) -> float:
    direction = normalize_text(direction)

    entry = safe_float(entry)
    stop = safe_float(stop)
    observed_exit = safe_float(observed_exit)

    if direction == "SHORT":
        risk = stop - entry
        pnl = entry - observed_exit
    elif direction == "LONG":
        risk = entry - stop
        pnl = observed_exit - entry
    else:
        return 0.0

    if risk <= 0:
        return 0.0

    return float(pnl / risk)


def find_template_row(
    template_df: pd.DataFrame,
    cost_profile: str,
    context_name: str,
) -> pd.Series:
    if template_df.empty:
        raise ValueError("template_df is empty")

    required_columns = [
        "cost_profile",
        "context_name",
        "forward_observation_allowed",
        "paper_trade_execution_allowed",
        "real_capital_allowed",
    ]

    for column in required_columns:
        if column not in template_df.columns:
            raise ValueError(f"Missing template column: {column}")

    cost_profile_norm = normalize_text(cost_profile)
    context_name_norm = normalize_text(context_name)

    df = template_df.copy()
    df["_cost_profile_norm"] = df["cost_profile"].astype(str).str.upper()
    df["_context_name_norm"] = df["context_name"].astype(str).str.upper()

    matched = df[
        (df["_cost_profile_norm"] == cost_profile_norm)
        & (df["_context_name_norm"] == context_name_norm)
    ].copy()

    if matched.empty:
        raise ValueError(
            f"No template row found for cost_profile={cost_profile}, "
            f"context_name={context_name}"
        )

    row = matched.iloc[0]

    if not safe_bool(row.get("forward_observation_allowed"), False):
        raise ValueError("Template row is not allowed for forward observation")

    if safe_bool(row.get("paper_trade_execution_allowed"), False):
        raise ValueError("Template row wrongly allows paper trade execution")

    if safe_bool(row.get("real_capital_allowed"), False):
        raise ValueError("Template row wrongly allows real capital")

    return row


def build_record_signal_id(
    observed_at: str,
    symbol: str,
    timeframe: str,
    cost_profile: str,
    context_name: str,
) -> str:
    timestamp_text = (
        str(observed_at)
        .replace("-", "")
        .replace(":", "")
        .replace(" ", "T")
        .replace("/", "")
    )

    symbol = normalize_text(symbol) or "UNKNOWN"
    timeframe = normalize_text(timeframe) or "TF"
    cost_profile = normalize_text(cost_profile) or "PROFILE"
    context_name = normalize_text(context_name) or "CONTEXT"

    return f"FSR-{timestamp_text}-{symbol}-{timeframe}-{cost_profile}-{context_name}"


def build_observed_signal_row(
    template_row: pd.Series,
    signal_input: ForwardObservedSignalInput,
) -> dict:
    entry = safe_float(signal_input.entry_theoretical)
    stop = safe_float(signal_input.stop_theoretical)
    target = safe_float(signal_input.target_theoretical)

    rr = calculate_theoretical_risk_reward(
        direction=signal_input.direction,
        entry=entry,
        stop=stop,
        target=target,
    )

    theoretical_risk = safe_float(template_row.get("theoretical_risk_pct"), 0.0)

    row = {column: "" for column in FORWARD_SIGNAL_JOURNAL_COLUMNS}

    for column in FORWARD_SIGNAL_JOURNAL_COLUMNS:
        if column in template_row.index:
            row[column] = template_row[column]

    row.update(
        {
            "signal_id": build_record_signal_id(
                observed_at=signal_input.observed_at,
                symbol=signal_input.symbol,
                timeframe=signal_input.timeframe,
                cost_profile=signal_input.cost_profile,
                context_name=signal_input.context_name,
            ),
            "created_at": signal_input.observed_at,
            "observed_at": signal_input.observed_at,
            "symbol": signal_input.symbol,
            "timeframe": signal_input.timeframe,
            "cost_profile": signal_input.cost_profile,
            "context_name": signal_input.context_name,
            "direction": normalize_text(signal_input.direction),
            "signal_state": "FORWARD_OBSERVED",
            "entry_theoretical": entry,
            "stop_theoretical": stop,
            "target_theoretical": target,
            "risk_reward_theoretical": rr,
            "theoretical_risk_pct": theoretical_risk,
            "position_mode": map_position_mode(theoretical_risk),
            "invalidation_level": safe_float(signal_input.invalidation_level),
            "invalidation_reason": signal_input.invalidation_reason,
            "manual_review_required": True,
            "manual_review_status": "PENDING",
            "manual_reviewer": signal_input.manual_reviewer,
            "manual_notes": signal_input.manual_notes,
            "entry_triggered": False,
            "exit_observed": False,
            "exit_reason": "",
            "result_r": "",
            "result_pct": "",
            "max_favorable_excursion_r": "",
            "max_adverse_excursion_r": "",
            "bars_to_resolution": "",
            "observation_status": "FORWARD_OBSERVED_NOT_RESOLVED",
            "data_source": signal_input.data_source,
            "screenshot_path": signal_input.screenshot_path,
            "notes": "Forward observed signal only. No execution allowed.",
            "paper_trade_execution_allowed": False,
            "real_capital_allowed": False,
            "forward_observation_allowed": True,
        }
    )

    return row


def append_forward_observed_signal(
    journal_df: pd.DataFrame,
    template_df: pd.DataFrame,
    signal_input: ForwardObservedSignalInput,
) -> pd.DataFrame:
    journal = journal_df.copy()

    for column in FORWARD_SIGNAL_JOURNAL_COLUMNS:
        if column not in journal.columns:
            journal[column] = ""

    journal = journal[FORWARD_SIGNAL_JOURNAL_COLUMNS].copy()

    template_row = find_template_row(
        template_df=template_df,
        cost_profile=signal_input.cost_profile,
        context_name=signal_input.context_name,
    )

    signal_row = build_observed_signal_row(
        template_row=template_row,
        signal_input=signal_input,
    )

    if signal_row["signal_id"] in journal["signal_id"].astype(str).tolist():
        raise ValueError(f"Duplicate signal_id: {signal_row['signal_id']}")

    updated = pd.concat(
        [
            journal,
            pd.DataFrame([signal_row], columns=FORWARD_SIGNAL_JOURNAL_COLUMNS),
        ],
        ignore_index=True,
    )

    return updated[FORWARD_SIGNAL_JOURNAL_COLUMNS].copy()


def resolve_forward_signal(
    journal_df: pd.DataFrame,
    signal_id: str,
    observed_exit: float,
    exit_reason: str,
    max_favorable_excursion_r: float = 0.0,
    max_adverse_excursion_r: float = 0.0,
    bars_to_resolution: int = 0,
) -> pd.DataFrame:
    journal = journal_df.copy()

    if "signal_id" not in journal.columns:
        raise ValueError("journal_df missing signal_id column")

    mask = journal["signal_id"].astype(str) == str(signal_id)

    if not mask.any():
        raise ValueError(f"signal_id not found: {signal_id}")

    index = journal[mask].index[0]

    direction = str(journal.at[index, "direction"])
    entry = safe_float(journal.at[index, "entry_theoretical"])
    stop = safe_float(journal.at[index, "stop_theoretical"])

    result_r = calculate_theoretical_result_r(
        direction=direction,
        entry=entry,
        stop=stop,
        observed_exit=observed_exit,
    )

    result_pct = result_r * safe_float(journal.at[index, "theoretical_risk_pct"], 0.0)

    journal.at[index, "exit_observed"] = True
    journal.at[index, "exit_reason"] = exit_reason
    journal.at[index, "result_r"] = result_r
    journal.at[index, "result_pct"] = result_pct
    journal.at[index, "max_favorable_excursion_r"] = max_favorable_excursion_r
    journal.at[index, "max_adverse_excursion_r"] = max_adverse_excursion_r
    journal.at[index, "bars_to_resolution"] = bars_to_resolution
    journal.at[index, "observation_status"] = "RESOLVED"

    journal.at[index, "paper_trade_execution_allowed"] = False
    journal.at[index, "real_capital_allowed"] = False

    return journal[FORWARD_SIGNAL_JOURNAL_COLUMNS].copy()


def validate_recorded_journal(
    journal_df: pd.DataFrame,
    config: ForwardSignalJournalConfig | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    if config is None:
        config = ForwardSignalJournalConfig()

    validation_df, validation_summary = validate_forward_signal_journal(
        journal_df=journal_df,
        config=config,
    )

    validation_summary_df = pd.DataFrame([validation_summary])
    journal_summary_df = summarize_forward_signal_journal(journal_df)

    return validation_df, validation_summary_df, journal_summary_df