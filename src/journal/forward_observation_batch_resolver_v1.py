from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pandas as pd

from src.journal.forward_observation_resolution_engine_v1 import (
    ForwardObservationResolutionConfig,
    resolve_forward_observations,
)


@dataclass(frozen=True)
class ForwardObservationBatchResolverConfig:
    min_forward_observations: int = 100
    preferred_forward_observations: int = 300
    timestamp_column: str = "timestamp"
    same_bar_policy: str = "CONSERVATIVE_STOP"
    max_bars_after_observation: int = 96
    open_status: str = "OPEN_UNRESOLVED"
    no_future_data_status: str = "OPEN_NO_FUTURE_DATA"
    invalid_price_status: str = "RESOLUTION_ERROR_INVALID_PRICE_LEVELS"
    batch_resolver_name: str = "FORWARD_OBSERVATION_BATCH_RESOLVER_V1"
    paper_trade_execution_allowed: bool = False
    real_capital_allowed: bool = False
    live_alerts_allowed: bool = False
    exchange_execution_allowed: bool = False
    automation_allowed: bool = False


REQUIRED_OBSERVATION_COLUMNS = [
    "signal_id",
    "observed_at",
    "symbol",
    "timeframe",
    "cost_profile",
    "context_name",
    "direction",
    "entry_price",
    "stop_price",
    "target_price",
    "resolution_status",
    "result_r",
    "mfe_r",
    "mae_r",
    "bars_to_resolution",
    "paper_trade_execution_allowed",
    "real_capital_allowed",
    "live_alerts_allowed",
    "exchange_execution_allowed",
    "automation_allowed",
]


PRICE_ALIASES = {
    "entry_price": [
        "entry_price",
        "theoretical_entry_price",
        "theoretical_entry",
        "planned_entry_price",
        "planned_entry",
        "entry",
    ],
    "stop_price": [
        "stop_price",
        "theoretical_stop_price",
        "theoretical_stop",
        "planned_stop_price",
        "planned_stop",
        "stop",
    ],
    "target_price": [
        "target_price",
        "theoretical_target_price",
        "theoretical_target",
        "planned_target_price",
        "planned_target",
        "target",
    ],
}


def safe_str(value: Any, default: str = "") -> str:
    if value is None:
        return default

    try:
        if pd.isna(value):
            return default
    except Exception:
        pass

    return str(value).strip()


def safe_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None or pd.isna(value):
            return default
        return float(value)
    except Exception:
        return default


def first_available_numeric_value(row: pd.Series, aliases: list[str]) -> float:
    for column in aliases:
        if column not in row.index:
            continue

        value = safe_float(row.get(column), 0.0)

        if value > 0:
            return value

    return 0.0


def ensure_observation_columns(
    observations_df: pd.DataFrame,
    config: ForwardObservationBatchResolverConfig,
) -> pd.DataFrame:
    df = observations_df.copy()

    for column in REQUIRED_OBSERVATION_COLUMNS:
        if column not in df.columns:
            df[column] = ""

    if "resolved_at" not in df.columns:
        df["resolved_at"] = ""

    if "batch_resolver_source" not in df.columns:
        df["batch_resolver_source"] = config.batch_resolver_name

    if "batch_resolution_status" not in df.columns:
        df["batch_resolution_status"] = ""

    for column in ["entry_price", "stop_price", "target_price"]:
        df[column] = pd.to_numeric(df[column], errors="coerce").fillna(0.0)

    for target_column, aliases in PRICE_ALIASES.items():
        df[target_column] = df.apply(
            lambda row: (
                safe_float(row.get(target_column), 0.0)
                if safe_float(row.get(target_column), 0.0) > 0
                else first_available_numeric_value(row, aliases)
            ),
            axis=1,
        )

    for column in ["result_r", "mfe_r", "mae_r", "bars_to_resolution"]:
        df[column] = pd.to_numeric(df[column], errors="coerce").fillna(0.0)

    for column in [
        "signal_id",
        "observed_at",
        "symbol",
        "timeframe",
        "cost_profile",
        "context_name",
        "direction",
        "resolution_status",
        "resolved_at",
        "batch_resolver_source",
        "batch_resolution_status",
    ]:
        df[column] = df[column].map(lambda value: safe_str(value))

    df["symbol"] = df["symbol"].str.upper()
    df["timeframe"] = df["timeframe"].str.lower()
    df["cost_profile"] = df["cost_profile"].str.upper()
    df["context_name"] = df["context_name"].str.upper()
    df["direction"] = df["direction"].str.upper()
    df["resolution_status"] = df["resolution_status"].str.upper()

    df["paper_trade_execution_allowed"] = False
    df["real_capital_allowed"] = False
    df["live_alerts_allowed"] = False
    df["exchange_execution_allowed"] = False
    df["automation_allowed"] = False

    return df


def has_valid_price_levels(row: pd.Series) -> bool:
    entry_price = safe_float(row.get("entry_price"), 0.0)
    stop_price = safe_float(row.get("stop_price"), 0.0)
    target_price = safe_float(row.get("target_price"), 0.0)

    if entry_price <= 0 or stop_price <= 0 or target_price <= 0:
        return False

    if entry_price == stop_price or entry_price == target_price:
        return False

    direction = safe_str(row.get("direction")).upper()

    if direction == "SHORT":
        return stop_price > entry_price > target_price

    if direction == "LONG":
        return stop_price < entry_price < target_price

    return False


def split_resolution_candidates(
    observations_df: pd.DataFrame,
    config: ForwardObservationBatchResolverConfig,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    if observations_df.empty:
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

    df = observations_df.copy()

    open_mask = df["resolution_status"].eq(config.open_status)
    open_df = df[open_mask].copy()
    already_resolved_or_other_df = df[~open_mask].copy()

    if open_df.empty:
        return open_df, pd.DataFrame(), already_resolved_or_other_df

    valid_price_mask = open_df.apply(has_valid_price_levels, axis=1)

    resolution_input_df = open_df[valid_price_mask].copy()
    invalid_price_df = open_df[~valid_price_mask].copy()

    if not invalid_price_df.empty:
        invalid_price_df["resolution_status"] = config.invalid_price_status
        invalid_price_df["batch_resolution_status"] = "BATCH_RESOLUTION_SKIPPED_INVALID_PRICE_LEVELS"
        invalid_price_df["result_r"] = 0.0
        invalid_price_df["mfe_r"] = 0.0
        invalid_price_df["mae_r"] = 0.0
        invalid_price_df["bars_to_resolution"] = 0.0
        invalid_price_df["paper_trade_execution_allowed"] = False
        invalid_price_df["real_capital_allowed"] = False
        invalid_price_df["live_alerts_allowed"] = False
        invalid_price_df["exchange_execution_allowed"] = False
        invalid_price_df["automation_allowed"] = False

    return (
        resolution_input_df.reset_index(drop=True),
        invalid_price_df.reset_index(drop=True),
        already_resolved_or_other_df.reset_index(drop=True),
    )


def normalize_resolved_output(
    resolved_df: pd.DataFrame,
    config: ForwardObservationBatchResolverConfig,
) -> pd.DataFrame:
    df = ensure_observation_columns(resolved_df, config)

    if df.empty:
        return df

    df["batch_resolution_status"] = df["resolution_status"].map(
        lambda status: (
            "BATCH_RESOLUTION_CLOSED"
            if safe_str(status).upper() in {"TARGET_HIT", "STOP_HIT", "TIME_EXIT", "MANUAL_CLOSE"}
            else (
                "BATCH_RESOLUTION_OPEN"
                if safe_str(status).upper() in {config.open_status, config.no_future_data_status}
                else (
                    "BATCH_RESOLUTION_ERROR"
                    if safe_str(status).upper().startswith("RESOLUTION_ERROR")
                    else "BATCH_RESOLUTION_REVIEW"
                )
            )
        )
    )

    df["paper_trade_execution_allowed"] = False
    df["real_capital_allowed"] = False
    df["live_alerts_allowed"] = False
    df["exchange_execution_allowed"] = False
    df["automation_allowed"] = False

    return df


def validate_batch_resolver_output(
    dataset_after_resolution_df: pd.DataFrame,
    resolution_input_df: pd.DataFrame,
    invalid_price_df: pd.DataFrame,
) -> pd.DataFrame:
    rows = []

    for column in REQUIRED_OBSERVATION_COLUMNS:
        passed = column in dataset_after_resolution_df.columns

        rows.append(
            {
                "check_name": f"required_column:{column}",
                "passed": passed,
                "severity": "ERROR" if not passed else "INFO",
                "details": "OK" if passed else "MISSING",
            }
        )

    rows.append(
        {
            "check_name": "resolution_input_has_valid_prices",
            "passed": (
                True
                if resolution_input_df.empty
                else resolution_input_df.apply(has_valid_price_levels, axis=1).all()
            ),
            "severity": "ERROR",
            "details": f"resolution_input_rows={len(resolution_input_df)}",
        }
    )

    rows.append(
        {
            "check_name": "invalid_price_rows_marked",
            "passed": (
                True
                if invalid_price_df.empty
                else invalid_price_df["resolution_status"]
                .map(lambda status: safe_str(status).startswith("RESOLUTION_ERROR"))
                .all()
            ),
            "severity": "ERROR",
            "details": f"invalid_price_rows={len(invalid_price_df)}",
        }
    )

    rows.append(
        {
            "check_name": "all_execution_flags_false",
            "passed": (
                True
                if dataset_after_resolution_df.empty
                else (
                    (~dataset_after_resolution_df["paper_trade_execution_allowed"].astype(bool)).all()
                    and (~dataset_after_resolution_df["real_capital_allowed"].astype(bool)).all()
                    and (~dataset_after_resolution_df["live_alerts_allowed"].astype(bool)).all()
                    and (~dataset_after_resolution_df["exchange_execution_allowed"].astype(bool)).all()
                    and (~dataset_after_resolution_df["automation_allowed"].astype(bool)).all()
                )
            ),
            "severity": "ERROR",
            "details": "execution flags must remain false",
        }
    )

    return pd.DataFrame(rows)


def build_batch_resolver_summary_df(
    source_observations_df: pd.DataFrame,
    resolution_input_df: pd.DataFrame,
    invalid_price_df: pd.DataFrame,
    already_resolved_or_other_df: pd.DataFrame,
    resolved_all_df: pd.DataFrame,
    resolved_closed_df: pd.DataFrame,
    still_open_df: pd.DataFrame,
    resolution_errors_df: pd.DataFrame,
    dataset_after_resolution_df: pd.DataFrame,
    validation_df: pd.DataFrame,
    config: ForwardObservationBatchResolverConfig,
) -> pd.DataFrame:
    validation_passed = bool(validation_df["passed"].all()) if not validation_df.empty else False

    closed_observations = len(resolved_closed_df)
    open_observations = len(still_open_df)
    error_observations = len(resolution_errors_df) + len(invalid_price_df)

    wins = 0
    losses = 0
    avg_result_r = 0.0
    sum_result_r = 0.0

    if not resolved_closed_df.empty and "result_r" in resolved_closed_df.columns:
        wins = int((resolved_closed_df["result_r"] > 0).sum())
        losses = int((resolved_closed_df["result_r"] < 0).sum())
        avg_result_r = round(float(resolved_closed_df["result_r"].mean()), 6)
        sum_result_r = round(float(resolved_closed_df["result_r"].sum()), 6)

    if not validation_passed:
        batch_resolver_decision = "BATCH_RESOLVER_VALIDATION_FAILED"
    elif error_observations > 0:
        batch_resolver_decision = "BATCH_RESOLVER_COMPLETED_WITH_ERRORS"
    elif len(resolution_input_df) > 0 and closed_observations == len(resolution_input_df) and open_observations == 0:
        batch_resolver_decision = "BATCH_RESOLVER_COMPLETED_ALL_CLOSED"
    elif closed_observations > 0 and open_observations > 0:
        batch_resolver_decision = "BATCH_RESOLVER_COMPLETED_PARTIAL"
    elif open_observations > 0 and closed_observations == 0:
        batch_resolver_decision = "BATCH_RESOLVER_COMPLETED_ALL_OPEN"
    else:
        batch_resolver_decision = "BATCH_RESOLVER_COMPLETED_NO_RESOLUTION_INPUT"

    dataset_rows_after = len(dataset_after_resolution_df)

    return pd.DataFrame(
        [
            {
                "validation_passed": validation_passed,
                "source_observations": len(source_observations_df),
                "resolution_input_observations": len(resolution_input_df),
                "invalid_price_observations": len(invalid_price_df),
                "already_resolved_or_other_observations": len(already_resolved_or_other_df),
                "resolved_all_observations": len(resolved_all_df),
                "closed_observations": closed_observations,
                "open_observations": open_observations,
                "error_observations": error_observations,
                "wins": wins,
                "losses": losses,
                "avg_result_r": avg_result_r,
                "sum_result_r": sum_result_r,
                "dataset_rows_after_resolution": dataset_rows_after,
                "min_forward_observations": config.min_forward_observations,
                "preferred_forward_observations": config.preferred_forward_observations,
                "minimum_sample_reached": dataset_rows_after >= config.min_forward_observations,
                "preferred_sample_reached": dataset_rows_after >= config.preferred_forward_observations,
                "sample_gap_to_minimum": max(
                    config.min_forward_observations - dataset_rows_after,
                    0,
                ),
                "sample_gap_to_preferred": max(
                    config.preferred_forward_observations - dataset_rows_after,
                    0,
                ),
                "paper_trade_execution_allowed": False,
                "real_capital_allowed": False,
                "live_alerts_allowed": False,
                "exchange_execution_allowed": False,
                "automation_allowed": False,
                "batch_resolver_decision": batch_resolver_decision,
            }
        ]
    )


def run_forward_observation_batch_resolver(
    observations_df: pd.DataFrame,
    ohlc_df: pd.DataFrame,
    config: ForwardObservationBatchResolverConfig | None = None,
) -> tuple[
    pd.DataFrame,
    pd.DataFrame,
    pd.DataFrame,
    pd.DataFrame,
    pd.DataFrame,
    pd.DataFrame,
    pd.DataFrame,
    pd.DataFrame,
    pd.DataFrame,
    pd.DataFrame,
]:
    if config is None:
        config = ForwardObservationBatchResolverConfig()

    source_observations_df = ensure_observation_columns(observations_df, config)

    (
        resolution_input_df,
        invalid_price_df,
        already_resolved_or_other_df,
    ) = split_resolution_candidates(
        observations_df=source_observations_df,
        config=config,
    )

    if resolution_input_df.empty:
        resolved_all_df = pd.DataFrame()
        resolved_closed_df = pd.DataFrame()
        still_open_df = pd.DataFrame()
        resolution_errors_df = pd.DataFrame()
        ohlc_validation_df = pd.DataFrame()
        resolution_summary_df = pd.DataFrame()
    else:
        (
            resolved_all_df,
            resolved_closed_df,
            still_open_df,
            resolution_errors_df,
            ohlc_validation_df,
            resolution_summary_df,
        ) = resolve_forward_observations(
            observations_df=resolution_input_df,
            ohlc_df=ohlc_df,
            config=ForwardObservationResolutionConfig(
                timestamp_column=config.timestamp_column,
                same_bar_policy=config.same_bar_policy,
                max_bars_after_observation=config.max_bars_after_observation,
                paper_trade_execution_allowed=False,
                real_capital_allowed=False,
            ),
        )

    resolved_all_df = normalize_resolved_output(resolved_all_df, config)
    resolved_closed_df = normalize_resolved_output(resolved_closed_df, config)
    still_open_df = normalize_resolved_output(still_open_df, config)

    dataset_after_resolution_df = pd.concat(
        [
            already_resolved_or_other_df,
            invalid_price_df,
            resolved_all_df,
        ],
        ignore_index=True,
    )

    dataset_after_resolution_df = ensure_observation_columns(
        dataset_after_resolution_df,
        config,
    )

    validation_df = validate_batch_resolver_output(
        dataset_after_resolution_df=dataset_after_resolution_df,
        resolution_input_df=resolution_input_df,
        invalid_price_df=invalid_price_df,
    )

    summary_df = build_batch_resolver_summary_df(
        source_observations_df=source_observations_df,
        resolution_input_df=resolution_input_df,
        invalid_price_df=invalid_price_df,
        already_resolved_or_other_df=already_resolved_or_other_df,
        resolved_all_df=resolved_all_df,
        resolved_closed_df=resolved_closed_df,
        still_open_df=still_open_df,
        resolution_errors_df=resolution_errors_df,
        dataset_after_resolution_df=dataset_after_resolution_df,
        validation_df=validation_df,
        config=config,
    )

    return (
        summary_df,
        validation_df,
        source_observations_df,
        resolution_input_df,
        invalid_price_df,
        resolved_all_df,
        resolved_closed_df,
        still_open_df,
        resolution_errors_df,
        dataset_after_resolution_df,
    )