from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

import pandas as pd

from src.journal.operational_forward_evidence_bootstrap_v1 import (
    OHLC_INPUT_COLUMNS,
    PRICE_LEVEL_COLUMNS,
    SIGNAL_INPUT_COLUMNS,
    OperationalForwardEvidenceBootstrapConfig,
    operational_paths,
)


@dataclass(frozen=True)
class OperationalInputFileValidatorAdapterConfig:
    operational_root: str = "data/forward_evidence/operational"
    max_files_per_input_type: int = 100
    adapter_source: str = "OPERATIONAL_INPUT_FILE_VALIDATOR_ADAPTER_V1"
    paper_trade_execution_allowed: bool = False
    real_capital_allowed: bool = False
    live_alerts_allowed: bool = False
    exchange_execution_allowed: bool = False
    automation_allowed: bool = False


ALLOWED_DIRECTIONS = {"LONG", "SHORT"}
ALLOWED_ROUTER_DECISIONS = {"WATCH_ONLY", "BLOCKED", "SKIP", "REVIEW_ONLY"}
REQUIRED_SIGNAL_TEXT_COLUMNS = [
    "observed_at",
    "symbol",
    "timeframe",
    "signal_type",
    "router_decision",
    "cost_profile",
    "context_name",
    "direction",
]

REQUIRED_OHLC_PRICE_COLUMNS = ["open", "high", "low", "close"]
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


def safe_bool(value: Any, default: bool = False) -> bool:
    if isinstance(value, bool):
        return value

    text = safe_str(value).lower()

    if text in {"true", "1", "yes", "y", "si", "sí"}:
        return True

    if text in {"false", "0", "no", "n"}:
        return False

    return default


def validation_passed(validation_df: pd.DataFrame) -> bool:
    if validation_df is None or validation_df.empty:
        return True

    if not {"passed", "severity"}.issubset(validation_df.columns):
        return False

    error_failures = validation_df[
        validation_df["severity"].eq("ERROR")
        & ~validation_df["passed"].astype(bool)
    ]

    return error_failures.empty


def error_count(validation_df: pd.DataFrame) -> int:
    if validation_df is None or validation_df.empty:
        return 0

    if not {"passed", "severity"}.issubset(validation_df.columns):
        return 1

    return int(
        (
            validation_df["severity"].eq("ERROR")
            & ~validation_df["passed"].astype(bool)
        ).sum()
    )


def make_validation_row(
    check_name: str,
    passed: bool,
    details: str,
    severity: str | None = None,
    source_file: str = "",
    input_type: str = "",
) -> dict[str, Any]:
    resolved_severity = severity if severity is not None else ("INFO if passed else ERROR")

    if resolved_severity == "INFO if passed else ERROR":
        resolved_severity = "INFO" if passed else "ERROR"

    return {
        "input_type": input_type,
        "source_file": source_file,
        "check_name": check_name,
        "passed": bool(passed),
        "severity": resolved_severity,
        "details": details,
    }


def list_csv_files(input_dir: Path, max_files: int) -> list[Path]:
    if not input_dir.exists():
        return []

    files = sorted(
        [
            path
            for path in input_dir.glob("*.csv")
            if path.is_file()
        ]
    )

    return files[:max_files]


def validate_required_columns(
    df: pd.DataFrame,
    required_columns: list[str],
    source_file: Path,
    input_type: str,
) -> list[dict[str, Any]]:
    missing_columns = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    passed = len(missing_columns) == 0

    return [
        make_validation_row(
            input_type=input_type,
            source_file=str(source_file),
            check_name="required_columns_present",
            passed=passed,
            details="OK" if passed else ",".join(missing_columns),
        )
    ]


def validate_signal_file(
    df: pd.DataFrame,
    source_file: Path,
) -> pd.DataFrame:
    rows = []

    rows.extend(
        validate_required_columns(
            df=df,
            required_columns=SIGNAL_INPUT_COLUMNS,
            source_file=source_file,
            input_type="signals",
        )
    )

    if any(not row["passed"] for row in rows):
        return pd.DataFrame(rows)

    has_rows = len(df) > 0

    rows.append(
        make_validation_row(
            input_type="signals",
            source_file=str(source_file),
            check_name="file_has_rows",
            passed=has_rows,
            details=f"rows={len(df)}",
        )
    )

    if not has_rows:
        return pd.DataFrame(rows)

    parsed_timestamps = pd.to_datetime(df["observed_at"], errors="coerce")
    invalid_timestamp_count = int(parsed_timestamps.isna().sum())

    rows.append(
        make_validation_row(
            input_type="signals",
            source_file=str(source_file),
            check_name="observed_at_parseable",
            passed=invalid_timestamp_count == 0,
            details=f"invalid_timestamps={invalid_timestamp_count}",
        )
    )

    for column in REQUIRED_SIGNAL_TEXT_COLUMNS:
        blank_count = int(df[column].map(lambda value: safe_str(value) == "").sum())

        rows.append(
            make_validation_row(
                input_type="signals",
                source_file=str(source_file),
                check_name=f"non_empty:{column}",
                passed=blank_count == 0,
                details=f"blank_rows={blank_count}",
            )
        )

    directions = df["direction"].map(lambda value: safe_str(value).upper())
    invalid_direction_count = int((~directions.isin(ALLOWED_DIRECTIONS)).sum())

    rows.append(
        make_validation_row(
            input_type="signals",
            source_file=str(source_file),
            check_name="direction_allowed",
            passed=invalid_direction_count == 0,
            details=f"invalid_directions={invalid_direction_count}",
        )
    )

    router_decisions = df["router_decision"].map(lambda value: safe_str(value).upper())
    invalid_router_count = int((~router_decisions.isin(ALLOWED_ROUTER_DECISIONS)).sum())

    rows.append(
        make_validation_row(
            input_type="signals",
            source_file=str(source_file),
            check_name="router_decision_allowed",
            passed=invalid_router_count == 0,
            details=f"invalid_router_decisions={invalid_router_count}",
        )
    )

    manual_review_values = df["manual_review_required"].map(
        lambda value: safe_bool(value, default=False)
    )

    false_manual_review_count = int((~manual_review_values).sum())

    rows.append(
        make_validation_row(
            input_type="signals",
            source_file=str(source_file),
            check_name="manual_review_required_true",
            passed=false_manual_review_count == 0,
            details=f"false_manual_review_rows={false_manual_review_count}",
        )
    )

    return pd.DataFrame(rows)


def validate_ohlc_file(
    df: pd.DataFrame,
    source_file: Path,
) -> pd.DataFrame:
    rows = []

    rows.extend(
        validate_required_columns(
            df=df,
            required_columns=OHLC_INPUT_COLUMNS,
            source_file=source_file,
            input_type="ohlc",
        )
    )

    if any(not row["passed"] for row in rows):
        return pd.DataFrame(rows)

    has_rows = len(df) > 0

    rows.append(
        make_validation_row(
            input_type="ohlc",
            source_file=str(source_file),
            check_name="file_has_rows",
            passed=has_rows,
            details=f"rows={len(df)}",
        )
    )

    if not has_rows:
        return pd.DataFrame(rows)

    parsed_timestamps = pd.to_datetime(df["timestamp"], errors="coerce")
    invalid_timestamp_count = int(parsed_timestamps.isna().sum())

    rows.append(
        make_validation_row(
            input_type="ohlc",
            source_file=str(source_file),
            check_name="timestamp_parseable",
            passed=invalid_timestamp_count == 0,
            details=f"invalid_timestamps={invalid_timestamp_count}",
        )
    )

    for column in REQUIRED_OHLC_PRICE_COLUMNS:
        numeric_values = pd.to_numeric(df[column], errors="coerce")
        invalid_count = int(numeric_values.isna().sum())
        non_positive_count = int((numeric_values <= 0).sum())

        rows.append(
            make_validation_row(
                input_type="ohlc",
                source_file=str(source_file),
                check_name=f"numeric_positive:{column}",
                passed=invalid_count == 0 and non_positive_count == 0,
                details=(
                    f"invalid_numeric={invalid_count}, "
                    f"non_positive={non_positive_count}"
                ),
            )
        )

    high = pd.to_numeric(df["high"], errors="coerce")
    low = pd.to_numeric(df["low"], errors="coerce")
    open_ = pd.to_numeric(df["open"], errors="coerce")
    close = pd.to_numeric(df["close"], errors="coerce")

    inconsistent_rows = int(
        (
            (high < low)
            | (high < open_)
            | (high < close)
            | (low > open_)
            | (low > close)
        ).sum()
    )

    rows.append(
        make_validation_row(
            input_type="ohlc",
            source_file=str(source_file),
            check_name="ohlc_price_structure_consistent",
            passed=inconsistent_rows == 0,
            details=f"inconsistent_rows={inconsistent_rows}",
        )
    )

    blank_symbol_count = int(df["symbol"].map(lambda value: safe_str(value) == "").sum())
    blank_timeframe_count = int(df["timeframe"].map(lambda value: safe_str(value) == "").sum())

    rows.append(
        make_validation_row(
            input_type="ohlc",
            source_file=str(source_file),
            check_name="symbol_non_empty",
            passed=blank_symbol_count == 0,
            details=f"blank_symbol_rows={blank_symbol_count}",
        )
    )

    rows.append(
        make_validation_row(
            input_type="ohlc",
            source_file=str(source_file),
            check_name="timeframe_non_empty",
            passed=blank_timeframe_count == 0,
            details=f"blank_timeframe_rows={blank_timeframe_count}",
        )
    )

    if "volume" in df.columns:
        volume = pd.to_numeric(df["volume"], errors="coerce").fillna(0.0)
        negative_volume_count = int((volume < 0).sum())

        rows.append(
            make_validation_row(
                input_type="ohlc",
                source_file=str(source_file),
                check_name="volume_non_negative",
                passed=negative_volume_count == 0,
                details=f"negative_volume_rows={negative_volume_count}",
            )
        )

    return pd.DataFrame(rows)


def validate_price_level_file(
    df: pd.DataFrame,
    source_file: Path,
) -> pd.DataFrame:
    rows = []

    rows.extend(
        validate_required_columns(
            df=df,
            required_columns=PRICE_LEVEL_COLUMNS,
            source_file=source_file,
            input_type="price_levels",
        )
    )

    if any(not row["passed"] for row in rows):
        return pd.DataFrame(rows)

    if len(df) == 0:
        rows.append(
            make_validation_row(
                input_type="price_levels",
                source_file=str(source_file),
                check_name="file_has_rows",
                passed=True,
                severity="INFO",
                details="rows=0 optional_file_empty",
            )
        )

        return pd.DataFrame(rows)

    directions = df["direction"].map(lambda value: safe_str(value).upper())
    invalid_direction_count = int((~directions.isin(ALLOWED_DIRECTIONS)).sum())

    rows.append(
        make_validation_row(
            input_type="price_levels",
            source_file=str(source_file),
            check_name="direction_allowed",
            passed=invalid_direction_count == 0,
            details=f"invalid_directions={invalid_direction_count}",
        )
    )

    for column in ["entry_price", "stop_price", "target_price"]:
        numeric_values = pd.to_numeric(df[column], errors="coerce")
        invalid_count = int(numeric_values.isna().sum())
        non_positive_count = int((numeric_values <= 0).sum())

        rows.append(
            make_validation_row(
                input_type="price_levels",
                source_file=str(source_file),
                check_name=f"numeric_positive:{column}",
                passed=invalid_count == 0 and non_positive_count == 0,
                details=(
                    f"invalid_numeric={invalid_count}, "
                    f"non_positive={non_positive_count}"
                ),
            )
        )

    valid_structure_count = 0
    invalid_structure_count = 0

    for _, row in df.iterrows():
        direction = safe_str(row.get("direction")).upper()
        entry_price = pd.to_numeric(row.get("entry_price"), errors="coerce")
        stop_price = pd.to_numeric(row.get("stop_price"), errors="coerce")
        target_price = pd.to_numeric(row.get("target_price"), errors="coerce")

        if pd.isna(entry_price) or pd.isna(stop_price) or pd.isna(target_price):
            invalid_structure_count += 1
            continue

        if direction == "SHORT" and stop_price > entry_price > target_price:
            valid_structure_count += 1
            continue

        if direction == "LONG" and stop_price < entry_price < target_price:
            valid_structure_count += 1
            continue

        invalid_structure_count += 1

    rows.append(
        make_validation_row(
            input_type="price_levels",
            source_file=str(source_file),
            check_name="entry_stop_target_structure_valid",
            passed=invalid_structure_count == 0,
            details=(
                f"valid_rows={valid_structure_count}, "
                f"invalid_rows={invalid_structure_count}"
            ),
        )
    )

    return pd.DataFrame(rows)


def normalize_signal_df(df: pd.DataFrame, source_file: Path) -> pd.DataFrame:
    normalized = df.copy()

    for column in SIGNAL_INPUT_COLUMNS:
        if column not in normalized.columns:
            normalized[column] = ""

    normalized = normalized[SIGNAL_INPUT_COLUMNS].copy()
    normalized["observed_at"] = pd.to_datetime(
        normalized["observed_at"],
        errors="coerce",
    ).dt.strftime("%Y-%m-%d %H:%M:%S")

    for column in [
        "symbol",
        "timeframe",
        "signal_type",
        "router_decision",
        "cost_profile",
        "context_name",
        "direction",
    ]:
        normalized[column] = normalized[column].map(lambda value: safe_str(value).upper())

    normalized["timeframe"] = normalized["timeframe"].str.lower()
    normalized["manual_review_required"] = normalized["manual_review_required"].map(
        lambda value: safe_bool(value, default=False)
    )
    normalized["source_file"] = str(source_file)

    for column in EXECUTION_FLAG_COLUMNS:
        normalized[column] = False

    return normalized


def normalize_ohlc_df(df: pd.DataFrame, source_file: Path) -> pd.DataFrame:
    normalized = df.copy()

    for column in OHLC_INPUT_COLUMNS:
        if column not in normalized.columns:
            normalized[column] = ""

    normalized = normalized[OHLC_INPUT_COLUMNS].copy()
    normalized["timestamp"] = pd.to_datetime(
        normalized["timestamp"],
        errors="coerce",
    ).dt.strftime("%Y-%m-%d %H:%M:%S")

    for column in REQUIRED_OHLC_PRICE_COLUMNS + ["volume"]:
        normalized[column] = pd.to_numeric(
            normalized[column],
            errors="coerce",
        ).fillna(0.0)

    normalized["symbol"] = normalized["symbol"].map(lambda value: safe_str(value).upper())
    normalized["timeframe"] = normalized["timeframe"].map(lambda value: safe_str(value).lower())
    normalized["data_source"] = normalized["data_source"].map(lambda value: safe_str(value).upper())
    normalized["source_file"] = str(source_file)

    for column in EXECUTION_FLAG_COLUMNS:
        normalized[column] = False

    return normalized


def normalize_price_level_df(df: pd.DataFrame, source_file: Path) -> pd.DataFrame:
    normalized = df.copy()

    for column in PRICE_LEVEL_COLUMNS:
        if column not in normalized.columns:
            normalized[column] = ""

    normalized = normalized[PRICE_LEVEL_COLUMNS].copy()

    for column in ["signal_id", "context_name", "cost_profile", "direction", "price_level_source"]:
        normalized[column] = normalized[column].map(lambda value: safe_str(value).upper())

    for column in ["entry_price", "stop_price", "target_price"]:
        normalized[column] = pd.to_numeric(
            normalized[column],
            errors="coerce",
        ).fillna(0.0)

    normalized["notes"] = normalized["notes"].map(lambda value: safe_str(value))
    normalized["source_file"] = str(source_file)

    for column in EXECUTION_FLAG_COLUMNS:
        normalized[column] = False

    return normalized


def load_validate_and_adapt_group(
    input_type: str,
    input_dir: Path,
    required_columns: list[str],
    validator: Callable[[pd.DataFrame, Path], pd.DataFrame],
    normalizer: Callable[[pd.DataFrame, Path], pd.DataFrame],
    config: OperationalInputFileValidatorAdapterConfig,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    files = list_csv_files(input_dir, config.max_files_per_input_type)

    validation_frames = []
    adapted_frames = []
    rejected_file_rows = []

    if not files:
        validation_frames.append(
            pd.DataFrame(
                [
                    make_validation_row(
                        input_type=input_type,
                        source_file="",
                        check_name=f"{input_type}_files_found",
                        passed=True,
                        severity="INFO",
                        details="count=0 waiting_for_files",
                    )
                ]
            )
        )

        return (
            pd.DataFrame(),
            pd.concat(validation_frames, ignore_index=True),
            pd.DataFrame(),
        )

    for file_path in files:
        try:
            raw_df = pd.read_csv(file_path)
        except Exception as exc:
            validation_frames.append(
                pd.DataFrame(
                    [
                        make_validation_row(
                            input_type=input_type,
                            source_file=str(file_path),
                            check_name="csv_readable",
                            passed=False,
                            severity="ERROR",
                            details=repr(exc),
                        )
                    ]
                )
            )

            rejected_file_rows.append(
                {
                    "input_type": input_type,
                    "source_file": str(file_path),
                    "rejection_reason": "CSV_READ_ERROR",
                    "details": repr(exc),
                }
            )

            continue

        file_validation_df = validator(raw_df, file_path)
        validation_frames.append(file_validation_df)

        file_has_errors = error_count(file_validation_df) > 0

        if file_has_errors:
            rejected_file_rows.append(
                {
                    "input_type": input_type,
                    "source_file": str(file_path),
                    "rejection_reason": "FILE_VALIDATION_FAILED",
                    "details": f"error_count={error_count(file_validation_df)}",
                }
            )

            continue

        adapted_df = normalizer(raw_df, file_path)

        for column in required_columns:
            if column not in adapted_df.columns:
                adapted_df[column] = ""

        adapted_frames.append(adapted_df)

    adapted_all_df = (
        pd.concat(adapted_frames, ignore_index=True)
        if adapted_frames
        else pd.DataFrame()
    )

    validation_all_df = (
        pd.concat(validation_frames, ignore_index=True)
        if validation_frames
        else pd.DataFrame()
    )

    rejected_files_df = pd.DataFrame(rejected_file_rows)

    return adapted_all_df, validation_all_df, rejected_files_df


def build_file_inventory_df(paths: dict[str, Path]) -> pd.DataFrame:
    inventory_rows = []

    inventory_map = {
        "signals": paths["signal_input_dir"],
        "ohlc": paths["ohlc_input_dir"],
        "price_levels": paths["price_level_input_dir"],
    }

    for input_type, directory in inventory_map.items():
        files = list_csv_files(directory, max_files=10_000)

        inventory_rows.append(
            {
                "input_type": input_type,
                "directory": str(directory),
                "directory_exists": directory.exists(),
                "csv_files_found": len(files),
                "files": "|".join([str(path) for path in files]),
            }
        )

    return pd.DataFrame(inventory_rows)


def validate_operational_directories(paths: dict[str, Path]) -> pd.DataFrame:
    rows = []

    for key in ["signal_input_dir", "ohlc_input_dir", "price_level_input_dir"]:
        path = paths[key]
        passed = path.exists() and path.is_dir()

        rows.append(
            make_validation_row(
                input_type="directories",
                source_file="",
                check_name=f"directory_exists:{key}",
                passed=passed,
                details=str(path),
            )
        )

    return pd.DataFrame(rows)


def build_adapter_summary_df(
    validation_df: pd.DataFrame,
    file_inventory_df: pd.DataFrame,
    adapted_signals_df: pd.DataFrame,
    adapted_ohlc_df: pd.DataFrame,
    adapted_price_levels_df: pd.DataFrame,
    rejected_files_df: pd.DataFrame,
) -> pd.DataFrame:
    validation_ok = validation_passed(validation_df)
    validation_errors = error_count(validation_df)

    def inventory_count(input_type: str) -> int:
        if file_inventory_df.empty:
            return 0

        matched = file_inventory_df[file_inventory_df["input_type"].eq(input_type)]

        if matched.empty:
            return 0

        return int(matched.iloc[0]["csv_files_found"])

    signal_files_found = inventory_count("signals")
    ohlc_files_found = inventory_count("ohlc")
    price_level_files_found = inventory_count("price_levels")

    signal_rows = len(adapted_signals_df)
    ohlc_rows = len(adapted_ohlc_df)
    price_level_rows = len(adapted_price_levels_df)

    input_ready_for_cycle = (
        validation_ok
        and signal_files_found > 0
        and ohlc_files_found > 0
        and signal_rows > 0
        and ohlc_rows > 0
    )

    if validation_errors > 0:
        adapter_decision = "OPERATIONAL_INPUT_VALIDATION_FAILED"
    elif input_ready_for_cycle:
        adapter_decision = "OPERATIONAL_INPUT_VALIDATED_READY_FOR_CYCLE"
    else:
        adapter_decision = "OPERATIONAL_INPUT_WAITING_FOR_FILES"

    return pd.DataFrame(
        [
            {
                "validation_passed": validation_ok,
                "validation_error_count": validation_errors,
                "signal_files_found": signal_files_found,
                "ohlc_files_found": ohlc_files_found,
                "price_level_files_found": price_level_files_found,
                "adapted_signal_rows": signal_rows,
                "adapted_ohlc_rows": ohlc_rows,
                "adapted_price_level_rows": price_level_rows,
                "rejected_files": len(rejected_files_df),
                "input_ready_for_cycle": input_ready_for_cycle,
                "processing_allowed": input_ready_for_cycle,
                "paper_trade_execution_allowed": False,
                "real_capital_allowed": False,
                "live_alerts_allowed": False,
                "exchange_execution_allowed": False,
                "automation_allowed": False,
                "execution_allowed": False,
                "adapter_decision": adapter_decision,
            }
        ]
    )


def run_operational_input_file_validator_adapter(
    config: OperationalInputFileValidatorAdapterConfig | None = None,
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
        config = OperationalInputFileValidatorAdapterConfig()

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

    directory_validation_df = validate_operational_directories(paths)
    file_inventory_df = build_file_inventory_df(paths)

    adapted_signals_df, signal_validation_df, rejected_signal_files_df = (
        load_validate_and_adapt_group(
            input_type="signals",
            input_dir=paths["signal_input_dir"],
            required_columns=SIGNAL_INPUT_COLUMNS,
            validator=validate_signal_file,
            normalizer=normalize_signal_df,
            config=config,
        )
    )

    adapted_ohlc_df, ohlc_validation_df, rejected_ohlc_files_df = (
        load_validate_and_adapt_group(
            input_type="ohlc",
            input_dir=paths["ohlc_input_dir"],
            required_columns=OHLC_INPUT_COLUMNS,
            validator=validate_ohlc_file,
            normalizer=normalize_ohlc_df,
            config=config,
        )
    )

    adapted_price_levels_df, price_level_validation_df, rejected_price_files_df = (
        load_validate_and_adapt_group(
            input_type="price_levels",
            input_dir=paths["price_level_input_dir"],
            required_columns=PRICE_LEVEL_COLUMNS,
            validator=validate_price_level_file,
            normalizer=normalize_price_level_df,
            config=config,
        )
    )

    validation_df = pd.concat(
        [
            directory_validation_df,
            signal_validation_df,
            ohlc_validation_df,
            price_level_validation_df,
        ],
        ignore_index=True,
    )

    rejected_files_df = pd.concat(
        [
            rejected_signal_files_df,
            rejected_ohlc_files_df,
            rejected_price_files_df,
        ],
        ignore_index=True,
    )

    summary_df = build_adapter_summary_df(
        validation_df=validation_df,
        file_inventory_df=file_inventory_df,
        adapted_signals_df=adapted_signals_df,
        adapted_ohlc_df=adapted_ohlc_df,
        adapted_price_levels_df=adapted_price_levels_df,
        rejected_files_df=rejected_files_df,
    )

    return (
        summary_df,
        validation_df,
        file_inventory_df,
        adapted_signals_df,
        adapted_ohlc_df,
        adapted_price_levels_df,
        rejected_files_df,
    )