from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd

from src.journal.forward_evidence_dataset_persistence_v1 import (
    ForwardEvidenceDatasetPersistenceConfig,
    REQUIRED_PERSISTENCE_COLUMNS,
    all_execution_flags_false,
    normalize_evidence_dataset,
)


@dataclass(frozen=True)
class OperationalForwardEvidenceBootstrapConfig:
    operational_root: str = "data/forward_evidence/operational"
    dataset_filename: str = "forward_evidence_dataset_v1.csv"
    signal_template_filename: str = "operational_signal_input_template_v1.csv"
    ohlc_template_filename: str = "operational_ohlc_input_template_v1.csv"
    price_level_template_filename: str = "operational_price_level_template_v1.csv"
    schema_dictionary_filename: str = "operational_input_schema_dictionary_v1.csv"
    min_forward_observations: int = 100
    preferred_forward_observations: int = 300
    bootstrap_source: str = "OPERATIONAL_FORWARD_EVIDENCE_BOOTSTRAP_V1"
    paper_trade_execution_allowed: bool = False
    real_capital_allowed: bool = False
    live_alerts_allowed: bool = False
    exchange_execution_allowed: bool = False
    automation_allowed: bool = False


SIGNAL_INPUT_COLUMNS = [
    "observed_at",
    "symbol",
    "timeframe",
    "signal_type",
    "router_decision",
    "cost_profile",
    "context_name",
    "direction",
    "manual_review_required",
    "notes",
]


OHLC_INPUT_COLUMNS = [
    "timestamp",
    "open",
    "high",
    "low",
    "close",
    "volume",
    "symbol",
    "timeframe",
    "data_source",
]


PRICE_LEVEL_COLUMNS = [
    "signal_id",
    "context_name",
    "cost_profile",
    "direction",
    "entry_price",
    "stop_price",
    "target_price",
    "price_level_source",
    "notes",
]


EXECUTION_FLAG_COLUMNS = [
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


def safe_int(value: Any, default: int = 0) -> int:
    try:
        if value is None or pd.isna(value):
            return default
        return int(value)
    except Exception:
        return default


def dataframe_validation_passed(validation_df: pd.DataFrame) -> bool:
    if validation_df is None or validation_df.empty:
        return False

    if "passed" not in validation_df.columns:
        return False

    return bool(validation_df["passed"].all())


def operational_paths(
    config: OperationalForwardEvidenceBootstrapConfig,
) -> dict[str, Path]:
    root = Path(config.operational_root)

    return {
        "operational_root": root,
        "input_dir": root / "input",
        "signal_input_dir": root / "input" / "signals",
        "ohlc_input_dir": root / "input" / "ohlc",
        "price_level_input_dir": root / "input" / "price_levels",
        "backup_dir": root / "backups",
        "snapshot_dir": root / "snapshots",
        "template_dir": root / "templates",
        "dataset_path": root / config.dataset_filename,
        "signal_template_path": root / "templates" / config.signal_template_filename,
        "ohlc_template_path": root / "templates" / config.ohlc_template_filename,
        "price_level_template_path": root / "templates" / config.price_level_template_filename,
        "schema_dictionary_path": root / "templates" / config.schema_dictionary_filename,
    }


def write_csv_atomically(
    df: pd.DataFrame,
    path: Path,
) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = path.with_name(f"{path.name}.tmp")

    try:
        df.to_csv(temporary_path, index=False)
        os.replace(temporary_path, path)
    finally:
        if temporary_path.exists():
            temporary_path.unlink()

    return path


def ensure_directories(paths: dict[str, Path]) -> pd.DataFrame:
    directory_keys = [
        "operational_root",
        "input_dir",
        "signal_input_dir",
        "ohlc_input_dir",
        "price_level_input_dir",
        "backup_dir",
        "snapshot_dir",
        "template_dir",
    ]

    rows = []

    for key in directory_keys:
        path = paths[key]
        path.mkdir(parents=True, exist_ok=True)

        rows.append(
            {
                "path_key": key,
                "path": str(path),
                "exists": path.exists(),
                "is_dir": path.is_dir(),
            }
        )

    return pd.DataFrame(rows)


def build_empty_operational_dataset(
    config: OperationalForwardEvidenceBootstrapConfig,
) -> pd.DataFrame:
    dataset_df = pd.DataFrame(columns=REQUIRED_PERSISTENCE_COLUMNS)

    return normalize_evidence_dataset(
        dataset_df=dataset_df,
        config=ForwardEvidenceDatasetPersistenceConfig(
            min_forward_observations=config.min_forward_observations,
            preferred_forward_observations=config.preferred_forward_observations,
            paper_trade_execution_allowed=False,
            real_capital_allowed=False,
            live_alerts_allowed=False,
            exchange_execution_allowed=False,
            automation_allowed=False,
        ),
    )


def ensure_operational_dataset(
    dataset_path: Path,
    config: OperationalForwardEvidenceBootstrapConfig,
) -> tuple[pd.DataFrame, bool]:
    dataset_created = False

    if not dataset_path.exists():
        dataset_df = build_empty_operational_dataset(config)
        write_csv_atomically(dataset_df, dataset_path)
        dataset_created = True

        return dataset_df, dataset_created

    existing_df = pd.read_csv(dataset_path)

    normalized_df = normalize_evidence_dataset(
        dataset_df=existing_df,
        config=ForwardEvidenceDatasetPersistenceConfig(
            min_forward_observations=config.min_forward_observations,
            preferred_forward_observations=config.preferred_forward_observations,
            paper_trade_execution_allowed=False,
            real_capital_allowed=False,
            live_alerts_allowed=False,
            exchange_execution_allowed=False,
            automation_allowed=False,
        ),
    )

    missing_columns = [
        column
        for column in REQUIRED_PERSISTENCE_COLUMNS
        if column not in existing_df.columns
    ]

    if missing_columns:
        write_csv_atomically(normalized_df, dataset_path)

    return normalized_df, dataset_created


def build_signal_template_df() -> pd.DataFrame:
    return pd.DataFrame(columns=SIGNAL_INPUT_COLUMNS)


def build_ohlc_template_df() -> pd.DataFrame:
    return pd.DataFrame(columns=OHLC_INPUT_COLUMNS)


def build_price_level_template_df() -> pd.DataFrame:
    return pd.DataFrame(columns=PRICE_LEVEL_COLUMNS)


def build_schema_dictionary_df() -> pd.DataFrame:
    rows = []

    schema_groups = [
        (
            "signal_input",
            SIGNAL_INPUT_COLUMNS,
            {
                "observed_at": "Observation timestamp. Example: 2026-06-21 05:00:00",
                "symbol": "Market symbol. Example: BTCUSDT",
                "timeframe": "Signal timeframe. Example: 15m",
                "signal_type": "Candidate type. Example: SHORT_ENTRY_SIGNAL",
                "router_decision": "Router state. Example: WATCH_ONLY or BLOCKED",
                "cost_profile": "Cost profile. Example: BINANCE_SCALP_BASE_ESTIMATE",
                "context_name": "Context bucket. Example: NORMAL_VALIDATION_CONTEXT",
                "direction": "Trade direction. Example: SHORT",
                "manual_review_required": "Must remain true for operational bootstrap",
                "notes": "Manual notes. Not used for execution.",
            },
        ),
        (
            "ohlc_input",
            OHLC_INPUT_COLUMNS,
            {
                "timestamp": "OHLC candle timestamp",
                "open": "Candle open price",
                "high": "Candle high price",
                "low": "Candle low price",
                "close": "Candle close price",
                "volume": "Candle volume, optional if unavailable",
                "symbol": "Market symbol. Example: BTCUSDT",
                "timeframe": "OHLC timeframe. Example: 15m",
                "data_source": "Export source. Example: BINANCE_EXPORT_MANUAL",
            },
        ),
        (
            "price_level_input",
            PRICE_LEVEL_COLUMNS,
            {
                "signal_id": "Optional direct match to a generated signal_id",
                "context_name": "Context match if signal_id is empty",
                "cost_profile": "Cost profile match if signal_id is empty",
                "direction": "Direction match if signal_id is empty",
                "entry_price": "Theoretical entry only. No execution.",
                "stop_price": "Theoretical stop only. No execution.",
                "target_price": "Theoretical target only. No execution.",
                "price_level_source": "Source of price levels",
                "notes": "Manual notes. Not used for execution.",
            },
        ),
        (
            "persistent_dataset",
            REQUIRED_PERSISTENCE_COLUMNS,
            {
                column: "Persistent forward evidence dataset column"
                for column in REQUIRED_PERSISTENCE_COLUMNS
            },
        ),
    ]

    for schema_name, columns, descriptions in schema_groups:
        for position, column in enumerate(columns, start=1):
            rows.append(
                {
                    "schema_name": schema_name,
                    "column_position": position,
                    "column_name": column,
                    "description": descriptions.get(column, ""),
                    "required": True,
                }
            )

    return pd.DataFrame(rows)


def ensure_template_file(
    path: Path,
    template_df: pd.DataFrame,
) -> bool:
    if path.exists():
        return False

    write_csv_atomically(template_df, path)

    return True


def count_csv_files(directory: Path) -> int:
    if not directory.exists():
        return 0

    return len(
        [
            path
            for path in directory.glob("*.csv")
            if path.is_file()
        ]
    )


def build_paths_df(paths: dict[str, Path]) -> pd.DataFrame:
    rows = []

    for key, path in paths.items():
        rows.append(
            {
                "path_key": key,
                "path": str(path),
                "exists": path.exists(),
                "is_file": path.is_file(),
                "is_dir": path.is_dir(),
            }
        )

    return pd.DataFrame(rows)


def check_severity(passed: bool) -> str:
    return "INFO" if passed else "ERROR"


def validate_bootstrap_output(
    paths: dict[str, Path],
    dataset_df: pd.DataFrame,
    signal_template_df: pd.DataFrame,
    ohlc_template_df: pd.DataFrame,
    price_level_template_df: pd.DataFrame,
    schema_dictionary_df: pd.DataFrame,
) -> pd.DataFrame:
    rows = []

    required_dirs = [
        "operational_root",
        "input_dir",
        "signal_input_dir",
        "ohlc_input_dir",
        "price_level_input_dir",
        "backup_dir",
        "snapshot_dir",
        "template_dir",
    ]

    for key in required_dirs:
        path = paths[key]
        passed = path.exists() and path.is_dir()

        rows.append(
            {
                "check_name": f"directory_exists:{key}",
                "passed": passed,
                "severity": check_severity(passed),
                "details": str(path),
            }
        )

    required_files = [
        "dataset_path",
        "signal_template_path",
        "ohlc_template_path",
        "price_level_template_path",
        "schema_dictionary_path",
    ]

    for key in required_files:
        path = paths[key]
        passed = path.exists() and path.is_file()

        rows.append(
            {
                "check_name": f"file_exists:{key}",
                "passed": passed,
                "severity": check_severity(passed),
                "details": str(path),
            }
        )

    dataset_missing_columns = [
        column
        for column in REQUIRED_PERSISTENCE_COLUMNS
        if column not in dataset_df.columns
    ]

    passed = len(dataset_missing_columns) == 0

    rows.append(
        {
            "check_name": "dataset_required_columns_present",
            "passed": passed,
            "severity": check_severity(passed),
            "details": (
                "OK"
                if passed
                else ",".join(dataset_missing_columns)
            ),
        }
    )

    passed = list(signal_template_df.columns) == SIGNAL_INPUT_COLUMNS

    rows.append(
        {
            "check_name": "signal_template_columns_match",
            "passed": passed,
            "severity": check_severity(passed),
            "details": ",".join(signal_template_df.columns),
        }
    )

    passed = list(ohlc_template_df.columns) == OHLC_INPUT_COLUMNS

    rows.append(
        {
            "check_name": "ohlc_template_columns_match",
            "passed": passed,
            "severity": check_severity(passed),
            "details": ",".join(ohlc_template_df.columns),
        }
    )

    passed = list(price_level_template_df.columns) == PRICE_LEVEL_COLUMNS

    rows.append(
        {
            "check_name": "price_level_template_columns_match",
            "passed": passed,
            "severity": check_severity(passed),
            "details": ",".join(price_level_template_df.columns),
        }
    )

    passed = len(schema_dictionary_df) > 0

    rows.append(
        {
            "check_name": "schema_dictionary_has_rows",
            "passed": passed,
            "severity": check_severity(passed),
            "details": f"rows={len(schema_dictionary_df)}",
        }
    )

    passed = all_execution_flags_false(dataset_df)

    rows.append(
        {
            "check_name": "all_execution_flags_false",
            "passed": passed,
            "severity": check_severity(passed),
            "details": "operational bootstrap must not enable execution",
        }
    )

    return pd.DataFrame(rows)


def build_bootstrap_summary_df(
    validation_df: pd.DataFrame,
    paths: dict[str, Path],
    dataset_df: pd.DataFrame,
    dataset_created: bool,
    signal_template_created: bool,
    ohlc_template_created: bool,
    price_level_template_created: bool,
    schema_dictionary_created: bool,
    config: OperationalForwardEvidenceBootstrapConfig,
) -> pd.DataFrame:
    validation_passed = dataframe_validation_passed(validation_df)

    signal_input_files = count_csv_files(paths["signal_input_dir"])
    ohlc_input_files = count_csv_files(paths["ohlc_input_dir"])
    price_level_input_files = count_csv_files(paths["price_level_input_dir"])

    input_ready_for_processing = signal_input_files > 0 and ohlc_input_files > 0

    dataset_rows = len(dataset_df)

    if validation_passed:
        bootstrap_decision = "OPERATIONAL_BOOTSTRAP_COMPLETED"
    else:
        bootstrap_decision = "OPERATIONAL_BOOTSTRAP_VALIDATION_FAILED"

    return pd.DataFrame(
        [
            {
                "validation_passed": validation_passed,
                "dataset_created": dataset_created,
                "dataset_exists": paths["dataset_path"].exists(),
                "dataset_rows": dataset_rows,
                "signal_template_created": signal_template_created,
                "ohlc_template_created": ohlc_template_created,
                "price_level_template_created": price_level_template_created,
                "schema_dictionary_created": schema_dictionary_created,
                "input_dirs_created": (
                    paths["signal_input_dir"].exists()
                    and paths["ohlc_input_dir"].exists()
                    and paths["price_level_input_dir"].exists()
                ),
                "signal_input_files": signal_input_files,
                "ohlc_input_files": ohlc_input_files,
                "price_level_input_files": price_level_input_files,
                "input_ready_for_processing": input_ready_for_processing,
                "processing_blocked_without_real_inputs": not input_ready_for_processing,
                "readiness_state": (
                    "OPERATIONAL_INPUT_READY_FOR_MANUAL_REVIEW"
                    if input_ready_for_processing
                    else "WAITING_FOR_REAL_EXPORTED_INPUT_FILES"
                ),
                "dataset_path": str(paths["dataset_path"]),
                "signal_input_dir": str(paths["signal_input_dir"]),
                "ohlc_input_dir": str(paths["ohlc_input_dir"]),
                "price_level_input_dir": str(paths["price_level_input_dir"]),
                "backup_dir": str(paths["backup_dir"]),
                "snapshot_dir": str(paths["snapshot_dir"]),
                "template_dir": str(paths["template_dir"]),
                "min_forward_observations": config.min_forward_observations,
                "preferred_forward_observations": config.preferred_forward_observations,
                "paper_trade_execution_allowed": False,
                "real_capital_allowed": False,
                "live_alerts_allowed": False,
                "exchange_execution_allowed": False,
                "automation_allowed": False,
                "execution_allowed": False,
                "bootstrap_decision": bootstrap_decision,
            }
        ]
    )


def run_operational_forward_evidence_bootstrap(
    config: OperationalForwardEvidenceBootstrapConfig | None = None,
) -> tuple[
    pd.DataFrame,
    pd.DataFrame,
    pd.DataFrame,
    pd.DataFrame,
    pd.DataFrame,
    pd.DataFrame,
    pd.DataFrame,
]:
    if config is None:
        config = OperationalForwardEvidenceBootstrapConfig()

    paths = operational_paths(config)

    directory_status_df = ensure_directories(paths)

    dataset_df, dataset_created = ensure_operational_dataset(
        dataset_path=paths["dataset_path"],
        config=config,
    )

    signal_template_df = build_signal_template_df()
    ohlc_template_df = build_ohlc_template_df()
    price_level_template_df = build_price_level_template_df()
    schema_dictionary_df = build_schema_dictionary_df()

    signal_template_created = ensure_template_file(
        paths["signal_template_path"],
        signal_template_df,
    )

    ohlc_template_created = ensure_template_file(
        paths["ohlc_template_path"],
        ohlc_template_df,
    )

    price_level_template_created = ensure_template_file(
        paths["price_level_template_path"],
        price_level_template_df,
    )

    schema_dictionary_created = ensure_template_file(
        paths["schema_dictionary_path"],
        schema_dictionary_df,
    )

    validation_df = validate_bootstrap_output(
        paths=paths,
        dataset_df=dataset_df,
        signal_template_df=signal_template_df,
        ohlc_template_df=ohlc_template_df,
        price_level_template_df=price_level_template_df,
        schema_dictionary_df=schema_dictionary_df,
    )

    summary_df = build_bootstrap_summary_df(
        validation_df=validation_df,
        paths=paths,
        dataset_df=dataset_df,
        dataset_created=dataset_created,
        signal_template_created=signal_template_created,
        ohlc_template_created=ohlc_template_created,
        price_level_template_created=price_level_template_created,
        schema_dictionary_created=schema_dictionary_created,
        config=config,
    )

    paths_df = build_paths_df(paths)

    return (
        summary_df,
        validation_df,
        paths_df,
        directory_status_df,
        dataset_df,
        signal_template_df,
        ohlc_template_df,
    )