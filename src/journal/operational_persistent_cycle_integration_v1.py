from __future__ import annotations

import hashlib
import os
import shutil
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd

from src.journal.forward_evidence_dataset_persistence_v1 import (
    ForwardEvidenceDatasetPersistenceConfig,
    REQUIRED_PERSISTENCE_COLUMNS,
    all_execution_flags_false,
    normalize_evidence_dataset,
)
from src.journal.operational_forward_evidence_bootstrap_v1 import (
    OperationalForwardEvidenceBootstrapConfig,
    operational_paths,
)
from src.journal.operational_input_file_validator_adapter_v1 import (
    OperationalInputFileValidatorAdapterConfig,
    run_operational_input_file_validator_adapter,
)


@dataclass(frozen=True)
class OperationalPersistentCycleIntegrationConfig:
    operational_root: str = "data/forward_evidence/operational"
    min_forward_observations: int = 100
    preferred_forward_observations: int = 300
    integration_source: str = "OPERATIONAL_PERSISTENT_CYCLE_INTEGRATION_V1"
    paper_trade_execution_allowed: bool = False
    real_capital_allowed: bool = False
    live_alerts_allowed: bool = False
    exchange_execution_allowed: bool = False
    automation_allowed: bool = False


EXECUTION_FLAG_COLUMNS = [
    "paper_trade_execution_allowed",
    "real_capital_allowed",
    "live_alerts_allowed",
    "exchange_execution_allowed",
    "automation_allowed",
]


CLOSED_STATUSES = {
    "TARGET_HIT",
    "STOP_HIT",
}

OPEN_STATUSES = {
    "OPEN_NO_FUTURE_DATA",
    "OPEN_UNRESOLVED",
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


def safe_bool(value: Any, default: bool = False) -> bool:
    if isinstance(value, bool):
        return value

    text = safe_str(value).lower()

    if text in {"true", "1", "yes", "y", "si", "sí"}:
        return True

    if text in {"false", "0", "no", "n"}:
        return False

    return default


def atomic_write_csv(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = path.with_name(f"{path.name}.tmp")

    try:
        df.to_csv(temporary_path, index=False)
        os.replace(temporary_path, path)
    finally:
        if temporary_path.exists():
            temporary_path.unlink()


def build_persistence_config(
    config: OperationalPersistentCycleIntegrationConfig,
) -> ForwardEvidenceDatasetPersistenceConfig:
    return ForwardEvidenceDatasetPersistenceConfig(
        min_forward_observations=config.min_forward_observations,
        preferred_forward_observations=config.preferred_forward_observations,
        paper_trade_execution_allowed=False,
        real_capital_allowed=False,
        live_alerts_allowed=False,
        exchange_execution_allowed=False,
        automation_allowed=False,
    )


def load_operational_dataset(
    dataset_path: Path,
    config: OperationalPersistentCycleIntegrationConfig,
) -> pd.DataFrame:
    persistence_config = build_persistence_config(config)

    if not dataset_path.exists():
        empty_df = pd.DataFrame(columns=REQUIRED_PERSISTENCE_COLUMNS)
        return normalize_evidence_dataset(empty_df, persistence_config)

    try:
        existing_df = pd.read_csv(dataset_path)
    except pd.errors.EmptyDataError:
        existing_df = pd.DataFrame(columns=REQUIRED_PERSISTENCE_COLUMNS)

    return normalize_evidence_dataset(existing_df, persistence_config)


def create_backup_if_needed(
    dataset_path: Path,
    backup_dir: Path,
    write_required: bool,
) -> tuple[bool, str]:
    if not write_required:
        return False, ""

    if not dataset_path.exists():
        return False, ""

    backup_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    backup_path = backup_dir / f"{dataset_path.stem}_backup_{timestamp}.csv"

    shutil.copy2(dataset_path, backup_path)

    return True, str(backup_path)


def create_snapshot_if_needed(
    dataset_df: pd.DataFrame,
    snapshot_dir: Path,
    write_required: bool,
) -> tuple[bool, str]:
    if not write_required:
        return False, ""

    snapshot_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    snapshot_path = snapshot_dir / f"forward_evidence_dataset_snapshot_{timestamp}.csv"

    dataset_df.to_csv(snapshot_path, index=False)

    return True, str(snapshot_path)


def deterministic_signal_id(
    signal_row: pd.Series,
    price_level_row: pd.Series,
) -> str:
    raw_key = "|".join(
        [
            safe_str(signal_row.get("observed_at")),
            safe_str(signal_row.get("symbol")).upper(),
            safe_str(signal_row.get("timeframe")).lower(),
            safe_str(signal_row.get("signal_type")).upper(),
            safe_str(signal_row.get("router_decision")).upper(),
            safe_str(signal_row.get("cost_profile")).upper(),
            safe_str(signal_row.get("context_name")).upper(),
            safe_str(signal_row.get("direction")).upper(),
            safe_str(price_level_row.get("entry_price")),
            safe_str(price_level_row.get("stop_price")),
            safe_str(price_level_row.get("target_price")),
        ]
    )

    digest = hashlib.sha256(raw_key.encode("utf-8")).hexdigest()[:16]

    return f"OPFWD_{digest}"


def find_price_level_for_signal(
    signal_row: pd.Series,
    price_levels_df: pd.DataFrame,
) -> pd.Series | None:
    if price_levels_df.empty:
        return None

    context_name = safe_str(signal_row.get("context_name")).upper()
    cost_profile = safe_str(signal_row.get("cost_profile")).upper()
    direction = safe_str(signal_row.get("direction")).upper()

    candidates = price_levels_df.copy()

    candidates["context_name_match"] = candidates["context_name"].map(
        lambda value: safe_str(value).upper() == context_name
    )
    candidates["cost_profile_match"] = candidates["cost_profile"].map(
        lambda value: safe_str(value).upper() == cost_profile
    )
    candidates["direction_match"] = candidates["direction"].map(
        lambda value: safe_str(value).upper() == direction
    )

    matched = candidates[
        candidates["context_name_match"]
        & candidates["cost_profile_match"]
        & candidates["direction_match"]
    ].copy()

    if matched.empty:
        return None

    return matched.iloc[0]


def filter_future_ohlc_for_signal(
    signal_row: pd.Series,
    ohlc_df: pd.DataFrame,
) -> pd.DataFrame:
    if ohlc_df.empty:
        return pd.DataFrame()

    symbol = safe_str(signal_row.get("symbol")).upper()
    timeframe = safe_str(signal_row.get("timeframe")).lower()
    observed_at = pd.to_datetime(
        signal_row.get("observed_at"),
        errors="coerce",
    )

    if pd.isna(observed_at):
        return pd.DataFrame()

    working = ohlc_df.copy()
    working["timestamp_dt"] = pd.to_datetime(
        working["timestamp"],
        errors="coerce",
    )
    working["symbol_norm"] = working["symbol"].map(lambda value: safe_str(value).upper())
    working["timeframe_norm"] = working["timeframe"].map(lambda value: safe_str(value).lower())

    future = working[
        working["symbol_norm"].eq(symbol)
        & working["timeframe_norm"].eq(timeframe)
        & (working["timestamp_dt"] > observed_at)
    ].copy()

    future = future.sort_values("timestamp_dt").reset_index(drop=True)

    return future


def calculate_resolution(
    signal_row: pd.Series,
    price_level_row: pd.Series,
    ohlc_df: pd.DataFrame,
) -> dict[str, Any]:
    direction = safe_str(signal_row.get("direction")).upper()

    entry_price = safe_float(price_level_row.get("entry_price"))
    stop_price = safe_float(price_level_row.get("stop_price"))
    target_price = safe_float(price_level_row.get("target_price"))

    risk = abs(stop_price - entry_price)

    if risk <= 0:
        return {
            "resolution_status": "RESOLUTION_ERROR",
            "resolution_reason": "invalid_risk_distance",
            "result_r": 0.0,
            "mfe_r": 0.0,
            "mae_r": 0.0,
            "bars_to_resolution": 0,
            "resolution_timestamp": "",
        }

    future_ohlc_df = filter_future_ohlc_for_signal(
        signal_row=signal_row,
        ohlc_df=ohlc_df,
    )

    if future_ohlc_df.empty:
        return {
            "resolution_status": "OPEN_NO_FUTURE_DATA",
            "resolution_reason": "no_future_ohlc_available",
            "result_r": 0.0,
            "mfe_r": 0.0,
            "mae_r": 0.0,
            "bars_to_resolution": 0,
            "resolution_timestamp": "",
        }

    highs = pd.to_numeric(future_ohlc_df["high"], errors="coerce").fillna(0.0)
    lows = pd.to_numeric(future_ohlc_df["low"], errors="coerce").fillna(0.0)

    if direction == "SHORT":
        mfe_values = (entry_price - lows) / risk
        mae_values = (entry_price - highs) / risk
        target_r = abs(entry_price - target_price) / risk

        for position, row in future_ohlc_df.iterrows():
            high = safe_float(row.get("high"))
            low = safe_float(row.get("low"))

            stop_hit = high >= stop_price
            target_hit = low <= target_price

            if stop_hit and target_hit:
                return {
                    "resolution_status": "STOP_HIT",
                    "resolution_reason": "ambiguous_same_candle_stop_first_conservative",
                    "result_r": -1.0,
                    "mfe_r": float(max(0.0, mfe_values.iloc[: position + 1].max())),
                    "mae_r": float(min(0.0, mae_values.iloc[: position + 1].min())),
                    "bars_to_resolution": int(position + 1),
                    "resolution_timestamp": safe_str(row.get("timestamp")),
                }

            if target_hit:
                return {
                    "resolution_status": "TARGET_HIT",
                    "resolution_reason": "target_hit",
                    "result_r": float(target_r),
                    "mfe_r": float(max(0.0, mfe_values.iloc[: position + 1].max())),
                    "mae_r": float(min(0.0, mae_values.iloc[: position + 1].min())),
                    "bars_to_resolution": int(position + 1),
                    "resolution_timestamp": safe_str(row.get("timestamp")),
                }

            if stop_hit:
                return {
                    "resolution_status": "STOP_HIT",
                    "resolution_reason": "stop_hit",
                    "result_r": -1.0,
                    "mfe_r": float(max(0.0, mfe_values.iloc[: position + 1].max())),
                    "mae_r": float(min(0.0, mae_values.iloc[: position + 1].min())),
                    "bars_to_resolution": int(position + 1),
                    "resolution_timestamp": safe_str(row.get("timestamp")),
                }

    if direction == "LONG":
        mfe_values = (highs - entry_price) / risk
        mae_values = (lows - entry_price) / risk
        target_r = abs(target_price - entry_price) / risk

        for position, row in future_ohlc_df.iterrows():
            high = safe_float(row.get("high"))
            low = safe_float(row.get("low"))

            stop_hit = low <= stop_price
            target_hit = high >= target_price

            if stop_hit and target_hit:
                return {
                    "resolution_status": "STOP_HIT",
                    "resolution_reason": "ambiguous_same_candle_stop_first_conservative",
                    "result_r": -1.0,
                    "mfe_r": float(max(0.0, mfe_values.iloc[: position + 1].max())),
                    "mae_r": float(min(0.0, mae_values.iloc[: position + 1].min())),
                    "bars_to_resolution": int(position + 1),
                    "resolution_timestamp": safe_str(row.get("timestamp")),
                }

            if target_hit:
                return {
                    "resolution_status": "TARGET_HIT",
                    "resolution_reason": "target_hit",
                    "result_r": float(target_r),
                    "mfe_r": float(max(0.0, mfe_values.iloc[: position + 1].max())),
                    "mae_r": float(min(0.0, mae_values.iloc[: position + 1].min())),
                    "bars_to_resolution": int(position + 1),
                    "resolution_timestamp": safe_str(row.get("timestamp")),
                }

            if stop_hit:
                return {
                    "resolution_status": "STOP_HIT",
                    "resolution_reason": "stop_hit",
                    "result_r": -1.0,
                    "mfe_r": float(max(0.0, mfe_values.iloc[: position + 1].max())),
                    "mae_r": float(min(0.0, mae_values.iloc[: position + 1].min())),
                    "bars_to_resolution": int(position + 1),
                    "resolution_timestamp": safe_str(row.get("timestamp")),
                }

    return {
        "resolution_status": "OPEN_UNRESOLVED",
        "resolution_reason": "ohlc_available_but_no_target_or_stop_hit",
        "result_r": 0.0,
        "mfe_r": float(max(0.0, mfe_values.max())),
        "mae_r": float(min(0.0, mae_values.min())),
        "bars_to_resolution": int(len(future_ohlc_df)),
        "resolution_timestamp": "",
    }


def build_empty_persistence_row() -> dict[str, Any]:
    row = {column: "" for column in REQUIRED_PERSISTENCE_COLUMNS}

    for column in EXECUTION_FLAG_COLUMNS:
        row[column] = False

    return row


def build_observation_row(
    signal_row: pd.Series,
    price_level_row: pd.Series,
    resolution: dict[str, Any],
    signal_id: str,
    config: OperationalPersistentCycleIntegrationConfig,
) -> dict[str, Any]:
    row = build_empty_persistence_row()

    entry_price = safe_float(price_level_row.get("entry_price"))
    stop_price = safe_float(price_level_row.get("stop_price"))
    target_price = safe_float(price_level_row.get("target_price"))

    updates = {
        "signal_id": signal_id,
        "observed_at": safe_str(signal_row.get("observed_at")),
        "symbol": safe_str(signal_row.get("symbol")).upper(),
        "timeframe": safe_str(signal_row.get("timeframe")).lower(),
        "signal_type": safe_str(signal_row.get("signal_type")).upper(),
        "router_decision": safe_str(signal_row.get("router_decision")).upper(),
        "cost_profile": safe_str(signal_row.get("cost_profile")).upper(),
        "context_name": safe_str(signal_row.get("context_name")).upper(),
        "direction": safe_str(signal_row.get("direction")).upper(),
        "entry_price": entry_price,
        "stop_price": stop_price,
        "target_price": target_price,
        "resolution_status": resolution["resolution_status"],
        "resolution_reason": resolution["resolution_reason"],
        "resolution_timestamp": resolution["resolution_timestamp"],
        "result_r": safe_float(resolution["result_r"]),
        "mfe_r": safe_float(resolution["mfe_r"]),
        "mae_r": safe_float(resolution["mae_r"]),
        "bars_to_resolution": int(resolution["bars_to_resolution"]),
        "manual_review_required": True,
        "resolve_now": False,
        "source": config.integration_source,
        "source_file": safe_str(signal_row.get("source_file")),
        "price_level_source_file": safe_str(price_level_row.get("source_file")),
        "notes": "Operational forward evidence generated from validated CSV inputs. No execution.",
    }

    for key, value in updates.items():
        row[key] = value

    for column in EXECUTION_FLAG_COLUMNS:
        row[column] = False

    return row


def generate_operational_observations(
    adapted_signals_df: pd.DataFrame,
    adapted_ohlc_df: pd.DataFrame,
    adapted_price_levels_df: pd.DataFrame,
    config: OperationalPersistentCycleIntegrationConfig,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    observation_rows = []
    rejected_rows = []

    if adapted_signals_df.empty:
        return pd.DataFrame(), pd.DataFrame()

    for _, signal_row in adapted_signals_df.iterrows():
        price_level_row = find_price_level_for_signal(
            signal_row=signal_row,
            price_levels_df=adapted_price_levels_df,
        )

        if price_level_row is None:
            rejected_rows.append(
                {
                    "observed_at": safe_str(signal_row.get("observed_at")),
                    "symbol": safe_str(signal_row.get("symbol")).upper(),
                    "timeframe": safe_str(signal_row.get("timeframe")).lower(),
                    "context_name": safe_str(signal_row.get("context_name")).upper(),
                    "cost_profile": safe_str(signal_row.get("cost_profile")).upper(),
                    "direction": safe_str(signal_row.get("direction")).upper(),
                    "rejection_reason": "NO_MATCHING_PRICE_LEVEL",
                    "details": "entry/stop/target levels are required before persistence",
                    "source_file": safe_str(signal_row.get("source_file")),
                }
            )
            continue

        signal_id = deterministic_signal_id(
            signal_row=signal_row,
            price_level_row=price_level_row,
        )

        resolution = calculate_resolution(
            signal_row=signal_row,
            price_level_row=price_level_row,
            ohlc_df=adapted_ohlc_df,
        )

        observation_row = build_observation_row(
            signal_row=signal_row,
            price_level_row=price_level_row,
            resolution=resolution,
            signal_id=signal_id,
            config=config,
        )

        observation_rows.append(observation_row)

    return pd.DataFrame(observation_rows), pd.DataFrame(rejected_rows)


def is_closed_status(status: Any) -> bool:
    return safe_str(status).upper() in CLOSED_STATUSES


def is_open_status(status: Any) -> bool:
    return safe_str(status).upper() in OPEN_STATUSES


def persist_operational_observations(
    existing_df: pd.DataFrame,
    generated_observations_df: pd.DataFrame,
    config: OperationalPersistentCycleIntegrationConfig,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    persistence_rows = []

    persistence_config = build_persistence_config(config)

    if generated_observations_df.empty:
        normalized_existing = normalize_evidence_dataset(
            existing_df,
            persistence_config,
        )

        return normalized_existing, pd.DataFrame(
            [
                {
                    "new_rows_added": 0,
                    "updated_rows": 0,
                    "duplicate_rows_skipped": 0,
                    "invalid_rows": 0,
                    "dataset_rows_after": len(normalized_existing),
                    "dataset_write_required": False,
                }
            ]
        )

    existing = normalize_evidence_dataset(
        existing_df,
        persistence_config,
    )

    incoming = normalize_evidence_dataset(
        generated_observations_df,
        persistence_config,
    )

    if "signal_id" not in existing.columns:
        existing["signal_id"] = ""

    new_rows = []
    updated_rows = 0
    duplicate_rows_skipped = 0
    invalid_rows = 0

    for _, incoming_row in incoming.iterrows():
        signal_id = safe_str(incoming_row.get("signal_id"))

        if signal_id == "":
            invalid_rows += 1
            continue

        matched_index = existing.index[
            existing["signal_id"].map(safe_str).eq(signal_id)
        ]

        if len(matched_index) == 0:
            new_rows.append(incoming_row.to_dict())
            continue

        current_index = matched_index[0]
        current_status = existing.loc[current_index, "resolution_status"]
        incoming_status = incoming_row.get("resolution_status")

        if is_open_status(current_status) and is_closed_status(incoming_status):
            for column in incoming.columns:
                existing.loc[current_index, column] = incoming_row[column]

            updated_rows += 1
            continue

        duplicate_rows_skipped += 1

    if new_rows:
        existing = pd.concat(
            [
                existing,
                pd.DataFrame(new_rows),
            ],
            ignore_index=True,
        )

    final_df = normalize_evidence_dataset(
        existing,
        persistence_config,
    )

    dataset_write_required = len(new_rows) > 0 or updated_rows > 0

    persistence_rows.append(
        {
            "new_rows_added": len(new_rows),
            "updated_rows": updated_rows,
            "duplicate_rows_skipped": duplicate_rows_skipped,
            "invalid_rows": invalid_rows,
            "dataset_rows_after": len(final_df),
            "dataset_write_required": dataset_write_required,
        }
    )

    return final_df, pd.DataFrame(persistence_rows)


def build_integration_summary_df(
    adapter_summary_df: pd.DataFrame,
    generated_observations_df: pd.DataFrame,
    rejected_observations_df: pd.DataFrame,
    persistence_summary_df: pd.DataFrame,
    dataset_df: pd.DataFrame,
    backup_created: bool,
    backup_path: str,
    snapshot_created: bool,
    snapshot_path: str,
    write_performed: bool,
) -> pd.DataFrame:
    adapter_row = (
        adapter_summary_df.iloc[0].to_dict()
        if not adapter_summary_df.empty
        else {}
    )

    persistence_row = (
        persistence_summary_df.iloc[0].to_dict()
        if not persistence_summary_df.empty
        else {}
    )

    adapter_decision = safe_str(adapter_row.get("adapter_decision"))
    input_ready_for_cycle = safe_bool(adapter_row.get("input_ready_for_cycle"))
    validation_passed = safe_bool(adapter_row.get("validation_passed"))

    generated_count = len(generated_observations_df)
    rejected_count = len(rejected_observations_df)

    closed_observations = 0
    open_observations = 0
    error_observations = 0
    wins = 0
    losses = 0

    if not generated_observations_df.empty and "resolution_status" in generated_observations_df.columns:
        statuses = generated_observations_df["resolution_status"].map(
            lambda value: safe_str(value).upper()
        )

        closed_observations = int(statuses.isin(CLOSED_STATUSES).sum())
        open_observations = int(statuses.isin(OPEN_STATUSES).sum())
        error_observations = int(statuses.eq("RESOLUTION_ERROR").sum())

    if not dataset_df.empty and "result_r" in dataset_df.columns:
        results_r = pd.to_numeric(dataset_df["result_r"], errors="coerce").fillna(0.0)
        wins = int((results_r > 0).sum())
        losses = int((results_r < 0).sum())

    if not validation_passed:
        integration_decision = "OPERATIONAL_INTEGRATION_BLOCKED_BY_INPUT_VALIDATION"
    elif not input_ready_for_cycle:
        integration_decision = "OPERATIONAL_INTEGRATION_WAITING_FOR_VALID_INPUTS"
    elif generated_count == 0:
        integration_decision = "OPERATIONAL_INTEGRATION_NO_OBSERVATIONS_GENERATED"
    elif rejected_count > 0 and generated_count == 0:
        integration_decision = "OPERATIONAL_INTEGRATION_REJECTED_ALL_OBSERVATIONS"
    elif write_performed:
        integration_decision = "OPERATIONAL_INTEGRATION_COMPLETED_WITH_EVIDENCE"
    else:
        integration_decision = "OPERATIONAL_INTEGRATION_COMPLETED_NO_DATASET_CHANGES"

    return pd.DataFrame(
        [
            {
                "validation_passed": validation_passed,
                "adapter_decision": adapter_decision,
                "input_ready_for_cycle": input_ready_for_cycle,
                "signal_files_found": int(adapter_row.get("signal_files_found", 0)),
                "ohlc_files_found": int(adapter_row.get("ohlc_files_found", 0)),
                "price_level_files_found": int(adapter_row.get("price_level_files_found", 0)),
                "adapted_signal_rows": int(adapter_row.get("adapted_signal_rows", 0)),
                "adapted_ohlc_rows": int(adapter_row.get("adapted_ohlc_rows", 0)),
                "adapted_price_level_rows": int(adapter_row.get("adapted_price_level_rows", 0)),
                "generated_observations": generated_count,
                "rejected_observations": rejected_count,
                "closed_observations": closed_observations,
                "open_observations": open_observations,
                "error_observations": error_observations,
                "wins": wins,
                "losses": losses,
                "new_rows_added": int(persistence_row.get("new_rows_added", 0)),
                "updated_rows": int(persistence_row.get("updated_rows", 0)),
                "duplicate_rows_skipped": int(persistence_row.get("duplicate_rows_skipped", 0)),
                "invalid_rows": int(persistence_row.get("invalid_rows", 0)),
                "dataset_rows_after": int(persistence_row.get("dataset_rows_after", len(dataset_df))),
                "dataset_write_required": safe_bool(persistence_row.get("dataset_write_required")),
                "dataset_write_performed": write_performed,
                "backup_created": backup_created,
                "backup_path": backup_path,
                "snapshot_created": snapshot_created,
                "snapshot_path": snapshot_path,
                "paper_trade_execution_allowed": False,
                "real_capital_allowed": False,
                "live_alerts_allowed": False,
                "exchange_execution_allowed": False,
                "automation_allowed": False,
                "execution_allowed": False,
                "integration_decision": integration_decision,
            }
        ]
    )


def run_operational_persistent_cycle_integration(
    config: OperationalPersistentCycleIntegrationConfig | None = None,
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
]:
    if config is None:
        config = OperationalPersistentCycleIntegrationConfig()

    paths = operational_paths(
        OperationalForwardEvidenceBootstrapConfig(
            operational_root=config.operational_root,
            paper_trade_execution_allowed=False,
            real_capital_allowed=False,
            live_alerts_allowed=False,
            exchange_execution_allowed=False,
            automation_allowed=False,
        )
    )

    (
        adapter_summary_df,
        adapter_validation_df,
        file_inventory_df,
        adapted_signals_df,
        adapted_ohlc_df,
        adapted_price_levels_df,
        adapter_rejected_files_df,
    ) = run_operational_input_file_validator_adapter(
        config=OperationalInputFileValidatorAdapterConfig(
            operational_root=config.operational_root,
            paper_trade_execution_allowed=False,
            real_capital_allowed=False,
            live_alerts_allowed=False,
            exchange_execution_allowed=False,
            automation_allowed=False,
        )
    )

    existing_dataset_df = load_operational_dataset(
        dataset_path=paths["dataset_path"],
        config=config,
    )

    adapter_row = (
        adapter_summary_df.iloc[0].to_dict()
        if not adapter_summary_df.empty
        else {}
    )

    adapter_validation_passed = safe_bool(adapter_row.get("validation_passed"))
    input_ready_for_cycle = safe_bool(adapter_row.get("input_ready_for_cycle"))

    generated_observations_df = pd.DataFrame()
    rejected_observations_df = pd.DataFrame()

    if adapter_validation_passed and input_ready_for_cycle:
        generated_observations_df, rejected_observations_df = (
            generate_operational_observations(
                adapted_signals_df=adapted_signals_df,
                adapted_ohlc_df=adapted_ohlc_df,
                adapted_price_levels_df=adapted_price_levels_df,
                config=config,
            )
        )

    final_dataset_df, persistence_summary_df = persist_operational_observations(
        existing_df=existing_dataset_df,
        generated_observations_df=generated_observations_df,
        config=config,
    )

    dataset_write_required = (
        not persistence_summary_df.empty
        and safe_bool(persistence_summary_df.iloc[0].get("dataset_write_required"))
    )

    backup_created, backup_path = create_backup_if_needed(
        dataset_path=paths["dataset_path"],
        backup_dir=paths["backup_dir"],
        write_required=dataset_write_required,
    )

    write_performed = False

    if dataset_write_required:
        atomic_write_csv(final_dataset_df, paths["dataset_path"])
        write_performed = True

    snapshot_created, snapshot_path = create_snapshot_if_needed(
        dataset_df=final_dataset_df,
        snapshot_dir=paths["snapshot_dir"],
        write_required=write_performed,
    )

    integration_summary_df = build_integration_summary_df(
        adapter_summary_df=adapter_summary_df,
        generated_observations_df=generated_observations_df,
        rejected_observations_df=rejected_observations_df,
        persistence_summary_df=persistence_summary_df,
        dataset_df=final_dataset_df,
        backup_created=backup_created,
        backup_path=backup_path,
        snapshot_created=snapshot_created,
        snapshot_path=snapshot_path,
        write_performed=write_performed,
    )

    if not all_execution_flags_false(final_dataset_df):
        integration_summary_df.loc[:, "execution_allowed"] = True
        integration_summary_df.loc[
            :,
            "integration_decision",
        ] = "OPERATIONAL_INTEGRATION_FAILED_EXECUTION_FLAGS_ENABLED"

    return (
        integration_summary_df,
        adapter_summary_df,
        adapter_validation_df,
        file_inventory_df,
        generated_observations_df,
        rejected_observations_df,
        persistence_summary_df,
        final_dataset_df,
        adapter_rejected_files_df,
    )