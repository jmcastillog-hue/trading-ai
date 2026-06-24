from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pandas as pd

from src.journal.forward_observation_candidate_detector_v1 import (
    ForwardObservationCandidateDetectorConfig,
    detect_forward_observation_candidates,
)


@dataclass(frozen=True)
class ForwardObservationBatchRunnerConfig:
    min_forward_observations: int = 100
    preferred_forward_observations: int = 300
    duplicate_key_column: str = "signal_id"
    unresolved_status: str = "OPEN_UNRESOLVED"
    batch_runner_name: str = "FORWARD_OBSERVATION_BATCH_RUNNER_V1"
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


def normalize_datetime_token(value: Any) -> str:
    parsed = pd.to_datetime(value, errors="coerce")

    if pd.isna(parsed):
        return "UNKNOWN_TIME"

    return parsed.strftime("%Y%m%dT%H%M%S")


def normalize_token(value: Any, default: str = "UNKNOWN") -> str:
    text = safe_str(value, default)

    if text == "":
        text = default

    return (
        text.upper()
        .replace(" ", "_")
        .replace("/", "_")
        .replace("\\", "_")
        .replace(":", "")
    )


def build_observation_signal_id(row: pd.Series) -> str:
    timestamp_part = normalize_datetime_token(row.get("observed_at"))
    symbol = normalize_token(row.get("symbol"), "UNKNOWN_SYMBOL")
    timeframe = normalize_token(row.get("timeframe"), "UNKNOWN_TF")
    cost_profile = normalize_token(row.get("cost_profile"), "UNKNOWN_COST")
    context_name = normalize_token(row.get("context_name"), "UNKNOWN_CONTEXT")
    direction = normalize_token(row.get("direction"), "UNKNOWN_DIRECTION")
    entry_price = str(safe_float(row.get("entry_price"), 0.0)).replace(".", "_")

    return (
        f"FOB-{timestamp_part}-{symbol}-{timeframe}-"
        f"{cost_profile}-{context_name}-{direction}-{entry_price}"
    )


def ensure_observation_columns(
    observations_df: pd.DataFrame,
    config: ForwardObservationBatchRunnerConfig,
) -> pd.DataFrame:
    df = observations_df.copy()

    for column in REQUIRED_OBSERVATION_COLUMNS:
        if column not in df.columns:
            df[column] = ""

    if "resolved_at" not in df.columns:
        df["resolved_at"] = ""

    if "batch_runner_source" not in df.columns:
        df["batch_runner_source"] = config.batch_runner_name

    if "batch_status" not in df.columns:
        df["batch_status"] = "BATCH_ACCEPTED_NEW_OBSERVATION"

    for column in ["entry_price", "stop_price", "target_price"]:
        df[column] = pd.to_numeric(df[column], errors="coerce").fillna(0.0)

    for column in ["result_r", "mfe_r", "mae_r", "bars_to_resolution"]:
        df[column] = pd.to_numeric(df[column], errors="coerce").fillna(0.0)

    for column in [
        "observed_at",
        "symbol",
        "timeframe",
        "cost_profile",
        "context_name",
        "direction",
        "resolution_status",
        "resolved_at",
        "batch_runner_source",
        "batch_status",
    ]:
        df[column] = df[column].map(lambda value: safe_str(value))

    df["symbol"] = df["symbol"].str.upper()
    df["timeframe"] = df["timeframe"].str.lower()
    df["cost_profile"] = df["cost_profile"].str.upper()
    df["context_name"] = df["context_name"].str.upper()
    df["direction"] = df["direction"].str.upper()
    df["resolution_status"] = config.unresolved_status

    df["result_r"] = 0.0
    df["mfe_r"] = 0.0
    df["mae_r"] = 0.0
    df["bars_to_resolution"] = 0.0
    df["resolved_at"] = ""

    df["paper_trade_execution_allowed"] = False
    df["real_capital_allowed"] = False
    df["live_alerts_allowed"] = False
    df["exchange_execution_allowed"] = False
    df["automation_allowed"] = False

    if "signal_id" not in df.columns:
        df["signal_id"] = ""

    df["signal_id"] = df.apply(
        lambda row: (
            safe_str(row.get("signal_id"))
            if safe_str(row.get("signal_id")) not in {"", "nan", "None"}
            else build_observation_signal_id(row)
        ),
        axis=1,
    )

    return df


def normalize_existing_dataset(
    existing_dataset_df: pd.DataFrame | None,
) -> pd.DataFrame:
    if existing_dataset_df is None or existing_dataset_df.empty:
        return pd.DataFrame(columns=REQUIRED_OBSERVATION_COLUMNS)

    df = existing_dataset_df.copy()

    for column in REQUIRED_OBSERVATION_COLUMNS:
        if column not in df.columns:
            df[column] = ""

    if "resolved_at" not in df.columns:
        df["resolved_at"] = ""

    if "batch_runner_source" not in df.columns:
        df["batch_runner_source"] = ""

    if "batch_status" not in df.columns:
        df["batch_status"] = ""

    df["signal_id"] = df["signal_id"].map(lambda value: safe_str(value))

    return df


def split_new_and_duplicate_observations(
    candidate_observations_df: pd.DataFrame,
    existing_dataset_df: pd.DataFrame,
    config: ForwardObservationBatchRunnerConfig,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    if candidate_observations_df.empty:
        return candidate_observations_df.copy(), pd.DataFrame()

    duplicate_key = config.duplicate_key_column

    if duplicate_key not in candidate_observations_df.columns:
        candidate_observations_df[duplicate_key] = ""

    if duplicate_key not in existing_dataset_df.columns:
        existing_dataset_df[duplicate_key] = ""

    existing_ids = set(
        existing_dataset_df[duplicate_key]
        .dropna()
        .map(lambda value: safe_str(value))
        .tolist()
    )

    df = candidate_observations_df.copy()
    df[duplicate_key] = df[duplicate_key].map(lambda value: safe_str(value))

    duplicate_mask_existing = df[duplicate_key].isin(existing_ids)
    duplicate_mask_batch = df.duplicated(subset=[duplicate_key], keep="first")

    duplicate_mask = duplicate_mask_existing | duplicate_mask_batch

    new_df = df[~duplicate_mask].copy()
    duplicate_df = df[duplicate_mask].copy()

    new_df["batch_status"] = "BATCH_ACCEPTED_NEW_OBSERVATION"
    duplicate_df["batch_status"] = "BATCH_SKIPPED_DUPLICATE_OBSERVATION"

    return new_df.reset_index(drop=True), duplicate_df.reset_index(drop=True)


def validate_batch_runner_output(
    dataset_after_df: pd.DataFrame,
    accepted_new_df: pd.DataFrame,
    duplicate_df: pd.DataFrame,
) -> pd.DataFrame:
    rows = []

    for column in REQUIRED_OBSERVATION_COLUMNS:
        passed = column in dataset_after_df.columns

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
            "check_name": "accepted_rows_have_signal_id",
            "passed": (
                True
                if accepted_new_df.empty
                else accepted_new_df["signal_id"].map(lambda value: safe_str(value) != "").all()
            ),
            "severity": "ERROR",
            "details": f"accepted_rows={len(accepted_new_df)}",
        }
    )

    rows.append(
        {
            "check_name": "duplicates_have_signal_id",
            "passed": (
                True
                if duplicate_df.empty
                else duplicate_df["signal_id"].map(lambda value: safe_str(value) != "").all()
            ),
            "severity": "ERROR",
            "details": f"duplicate_rows={len(duplicate_df)}",
        }
    )

    rows.append(
        {
            "check_name": "all_execution_flags_false",
            "passed": (
                True
                if dataset_after_df.empty
                else (
                    (~dataset_after_df["paper_trade_execution_allowed"].astype(bool)).all()
                    and (~dataset_after_df["real_capital_allowed"].astype(bool)).all()
                    and (~dataset_after_df["live_alerts_allowed"].astype(bool)).all()
                    and (~dataset_after_df["exchange_execution_allowed"].astype(bool)).all()
                    and (~dataset_after_df["automation_allowed"].astype(bool)).all()
                )
            ),
            "severity": "ERROR",
            "details": "execution flags must remain false",
        }
    )

    return pd.DataFrame(rows)


def build_batch_summary_df(
    source_signals_df: pd.DataFrame,
    generated_observations_df: pd.DataFrame,
    detector_accepted_df: pd.DataFrame,
    detector_rejected_df: pd.DataFrame,
    accepted_new_df: pd.DataFrame,
    duplicate_df: pd.DataFrame,
    dataset_after_df: pd.DataFrame,
    validation_df: pd.DataFrame,
    config: ForwardObservationBatchRunnerConfig,
) -> pd.DataFrame:
    validation_passed = bool(validation_df["passed"].all()) if not validation_df.empty else False

    if not validation_passed:
        batch_decision = "BATCH_RUNNER_VALIDATION_FAILED"
    elif len(accepted_new_df) > 0:
        batch_decision = "BATCH_RUNNER_COMPLETED_ACCEPTED_OBSERVATIONS"
    elif len(duplicate_df) > 0:
        batch_decision = "BATCH_RUNNER_COMPLETED_DUPLICATES_SKIPPED"
    else:
        batch_decision = "BATCH_RUNNER_COMPLETED_NO_ACCEPTED_OBSERVATIONS"

    dataset_rows_after = len(dataset_after_df)

    return pd.DataFrame(
        [
            {
                "validation_passed": validation_passed,
                "source_signal_rows": len(source_signals_df),
                "detector_accepted_candidates": len(detector_accepted_df),
                "detector_rejected_candidates": len(detector_rejected_df),
                "generated_observations": len(generated_observations_df),
                "accepted_new_observations": len(accepted_new_df),
                "skipped_duplicate_observations": len(duplicate_df),
                "dataset_rows_after": dataset_rows_after,
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
                "batch_decision": batch_decision,
            }
        ]
    )


def run_forward_observation_batch_runner(
    source_signals_df: pd.DataFrame,
    existing_dataset_df: pd.DataFrame | None = None,
    config: ForwardObservationBatchRunnerConfig | None = None,
) -> tuple[
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
        config = ForwardObservationBatchRunnerConfig()

    existing_dataset = normalize_existing_dataset(existing_dataset_df)

    (
        generated_records_df,
        detector_accepted_df,
        detector_rejected_df,
        detector_validation_df,
    ) = detect_forward_observation_candidates(
        signals_df=source_signals_df,
        config=ForwardObservationCandidateDetectorConfig(),
    )

    generated_observations_df = ensure_observation_columns(
        observations_df=generated_records_df,
        config=config,
    )

    accepted_new_df, duplicate_df = split_new_and_duplicate_observations(
        candidate_observations_df=generated_observations_df,
        existing_dataset_df=existing_dataset,
        config=config,
    )

    dataset_after_df = pd.concat(
        [
            existing_dataset,
            accepted_new_df,
        ],
        ignore_index=True,
    )

    validation_df = validate_batch_runner_output(
        dataset_after_df=dataset_after_df,
        accepted_new_df=accepted_new_df,
        duplicate_df=duplicate_df,
    )

    summary_df = build_batch_summary_df(
        source_signals_df=source_signals_df,
        generated_observations_df=generated_observations_df,
        detector_accepted_df=detector_accepted_df,
        detector_rejected_df=detector_rejected_df,
        accepted_new_df=accepted_new_df,
        duplicate_df=duplicate_df,
        dataset_after_df=dataset_after_df,
        validation_df=validation_df,
        config=config,
    )

    return (
        summary_df,
        validation_df,
        generated_observations_df,
        detector_accepted_df,
        detector_rejected_df,
        accepted_new_df,
        duplicate_df,
        dataset_after_df,
    )