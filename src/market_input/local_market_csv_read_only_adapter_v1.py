from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd


REPORTS_DIR = Path("reports/phase_7_2_local_market_csv_read_only_adapter_v1")

SOURCE_INPUT_DIR = Path("data/market_input/local_csv_read_only/input")
OPERATIONAL_OHLC_INPUT_DIR = Path("data/forward_evidence/operational/input/ohlc")

CONTROLLED_SOURCE_PATH = (
    SOURCE_INPUT_DIR / "phase_7_2_local_btcusdt_15m_source_v1.csv"
)
CONTROLLED_OUTPUT_PATH = (
    OPERATIONAL_OHLC_INPUT_DIR / "phase_7_2_local_market_ohlc_input_v1.csv"
)

PHASE_7_1_CONTRACT_PATH = Path(
    "docs/PHASE_7_REAL_MARKET_INPUT_BRIDGE_CONTRACT.md"
)
PHASE_6_CLOSURE_PATH = Path(
    "docs/PHASE_6_OPERATIONAL_EVIDENCE_CLOSURE.md"
)

REQUIRED_INPUT_COLUMNS = [
    "timestamp",
    "open",
    "high",
    "low",
    "close",
    "volume",
]

OPERATIONAL_OHLC_COLUMNS = [
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

EXECUTION_FLAGS = {
    "paper_trade_execution_allowed": False,
    "real_capital_allowed": False,
    "live_alerts_allowed": False,
    "exchange_execution_allowed": False,
    "automation_allowed": False,
    "execution_allowed": False,
}


@dataclass(frozen=True)
class LocalMarketCsvReadOnlyAdapterConfig:
    source_csv_path: Path = CONTROLLED_SOURCE_PATH
    output_csv_path: Path = CONTROLLED_OUTPUT_PATH
    reports_dir: Path = REPORTS_DIR
    symbol: str = "BTCUSDT"
    timeframe: str = "15m"
    data_source: str = "LOCAL_MARKET_CSV_READ_ONLY_PHASE_7_2"
    create_controlled_fixture: bool = True


def build_check(
    check_group: str,
    check_name: str,
    passed: bool,
    severity: str,
    details: str,
) -> dict[str, Any]:
    return {
        "check_group": check_group,
        "check_name": check_name,
        "passed": passed,
        "severity": severity,
        "details": details,
        "blocker": severity == "ERROR" and not passed,
    }


def create_controlled_local_ohlc_fixture(
    config: LocalMarketCsvReadOnlyAdapterConfig,
) -> None:
    config.source_csv_path.parent.mkdir(parents=True, exist_ok=True)

    fixture_df = pd.DataFrame(
        [
            {
                "timestamp": "2026-06-27 23:00:00",
                "open": 65000,
                "high": 65100,
                "low": 64800,
                "close": 64900,
                "volume": 100,
            },
            {
                "timestamp": "2026-06-27 23:15:00",
                "open": 64900,
                "high": 65050,
                "low": 64750,
                "close": 64850,
                "volume": 120,
            },
            {
                "timestamp": "2026-06-27 23:30:00",
                "open": 64850,
                "high": 64920,
                "low": 64600,
                "close": 64680,
                "volume": 140,
            },
        ]
    )

    fixture_df.to_csv(config.source_csv_path, index=False)


def normalize_source_columns(df: pd.DataFrame) -> pd.DataFrame:
    normalized_df = df.copy()
    normalized_df.columns = [
        str(column).strip().lower() for column in normalized_df.columns
    ]
    return normalized_df


def build_empty_output_df() -> pd.DataFrame:
    return pd.DataFrame(columns=OPERATIONAL_OHLC_COLUMNS)


def normalize_local_ohlc_df(
    source_df: pd.DataFrame,
    config: LocalMarketCsvReadOnlyAdapterConfig,
) -> tuple[pd.DataFrame, int]:
    working_df = normalize_source_columns(source_df)

    missing_columns = [
        column for column in REQUIRED_INPUT_COLUMNS if column not in working_df.columns
    ]

    if missing_columns:
        return build_empty_output_df(), len(working_df)

    normalized_df = working_df[REQUIRED_INPUT_COLUMNS].copy()

    normalized_df["timestamp"] = pd.to_datetime(
        normalized_df["timestamp"],
        errors="coerce",
    )

    for column in ["open", "high", "low", "close", "volume"]:
        normalized_df[column] = pd.to_numeric(
            normalized_df[column],
            errors="coerce",
        )

    invalid_mask = normalized_df[REQUIRED_INPUT_COLUMNS].isna().any(axis=1)
    invalid_rows = int(invalid_mask.sum())

    normalized_df = normalized_df.loc[~invalid_mask].copy()

    normalized_df["timestamp"] = normalized_df["timestamp"].dt.strftime(
        "%Y-%m-%d %H:%M:%S"
    )
    normalized_df["symbol"] = config.symbol
    normalized_df["timeframe"] = config.timeframe
    normalized_df["data_source"] = config.data_source

    normalized_df = normalized_df[OPERATIONAL_OHLC_COLUMNS]
    normalized_df = normalized_df.drop_duplicates(
        subset=["timestamp", "symbol", "timeframe"],
        keep="last",
    )
    normalized_df = normalized_df.sort_values("timestamp").reset_index(drop=True)

    return normalized_df, invalid_rows


def all_execution_flags_false() -> bool:
    return all(flag_value is False for flag_value in EXECUTION_FLAGS.values())


def validate_output_schema(output_df: pd.DataFrame) -> bool:
    return list(output_df.columns) == OPERATIONAL_OHLC_COLUMNS


def validate_local_market_csv_read_only_adapter(
    config: LocalMarketCsvReadOnlyAdapterConfig | None = None,
) -> dict[str, pd.DataFrame]:
    active_config = config or LocalMarketCsvReadOnlyAdapterConfig()

    active_config.reports_dir.mkdir(parents=True, exist_ok=True)
    active_config.output_csv_path.parent.mkdir(parents=True, exist_ok=True)

    if active_config.create_controlled_fixture:
        create_controlled_local_ohlc_fixture(active_config)

    checks: list[dict[str, Any]] = []

    source_exists = active_config.source_csv_path.exists()

    checks.append(
        build_check(
            check_group="phase_anchor",
            check_name="phase_6_closure_exists",
            passed=PHASE_6_CLOSURE_PATH.exists(),
            severity="INFO" if PHASE_6_CLOSURE_PATH.exists() else "ERROR",
            details=str(PHASE_6_CLOSURE_PATH),
        )
    )

    checks.append(
        build_check(
            check_group="phase_anchor",
            check_name="phase_7_1_contract_exists",
            passed=PHASE_7_1_CONTRACT_PATH.exists(),
            severity="INFO" if PHASE_7_1_CONTRACT_PATH.exists() else "ERROR",
            details=str(PHASE_7_1_CONTRACT_PATH),
        )
    )

    checks.append(
        build_check(
            check_group="source_file",
            check_name="source_csv_exists",
            passed=source_exists,
            severity="INFO" if source_exists else "ERROR",
            details=str(active_config.source_csv_path),
        )
    )

    source_df = pd.DataFrame()
    output_df = build_empty_output_df()
    invalid_rows = 0
    source_rows = 0
    output_written = False
    missing_columns: list[str] = []

    if source_exists:
        source_df = pd.read_csv(active_config.source_csv_path)
        source_rows = int(len(source_df))
        normalized_source_df = normalize_source_columns(source_df)
        missing_columns = [
            column
            for column in REQUIRED_INPUT_COLUMNS
            if column not in normalized_source_df.columns
        ]

        output_df, invalid_rows = normalize_local_ohlc_df(
            source_df=source_df,
            config=active_config,
        )

        if not output_df.empty:
            output_df.to_csv(active_config.output_csv_path, index=False)
            output_written = True

    checks.append(
        build_check(
            check_group="input_schema",
            check_name="required_input_columns_present",
            passed=len(missing_columns) == 0,
            severity="INFO" if len(missing_columns) == 0 else "ERROR",
            details="missing_columns=" + ",".join(missing_columns),
        )
    )

    checks.append(
        build_check(
            check_group="normalization",
            check_name="source_rows_present",
            passed=source_rows > 0,
            severity="INFO" if source_rows > 0 else "ERROR",
            details=f"source_rows={source_rows}",
        )
    )

    checks.append(
        build_check(
            check_group="normalization",
            check_name="output_rows_present",
            passed=len(output_df) > 0,
            severity="INFO" if len(output_df) > 0 else "ERROR",
            details=f"output_rows={len(output_df)}",
        )
    )

    checks.append(
        build_check(
            check_group="normalization",
            check_name="invalid_rows_zero",
            passed=invalid_rows == 0,
            severity="INFO" if invalid_rows == 0 else "WARNING",
            details=f"invalid_rows={invalid_rows}",
        )
    )

    checks.append(
        build_check(
            check_group="output_schema",
            check_name="operational_ohlc_schema_valid",
            passed=validate_output_schema(output_df),
            severity="INFO" if validate_output_schema(output_df) else "ERROR",
            details=",".join(output_df.columns.tolist()),
        )
    )

    checks.append(
        build_check(
            check_group="output_file",
            check_name="operational_ohlc_file_written",
            passed=output_written and active_config.output_csv_path.exists(),
            severity=(
                "INFO"
                if output_written and active_config.output_csv_path.exists()
                else "ERROR"
            ),
            details=str(active_config.output_csv_path),
        )
    )

    checks.append(
        build_check(
            check_group="source_scope",
            check_name="local_csv_read_only_source",
            passed=True,
            severity="INFO",
            details="Adapter reads local CSV source only.",
        )
    )

    checks.append(
        build_check(
            check_group="source_scope",
            check_name="real_market_fetch_disabled",
            passed=True,
            severity="INFO",
            details="No live market fetch is performed in Phase 7.2.",
        )
    )

    checks.append(
        build_check(
            check_group="source_scope",
            check_name="signal_generation_disabled",
            passed=True,
            severity="INFO",
            details="No signal output is generated in Phase 7.2.",
        )
    )

    checks.append(
        build_check(
            check_group="source_scope",
            check_name="price_level_generation_disabled",
            passed=True,
            severity="INFO",
            details="No price-level output is generated in Phase 7.2.",
        )
    )

    checks.append(
        build_check(
            check_group="execution_restrictions",
            check_name="execution_flags_false",
            passed=all_execution_flags_false(),
            severity="INFO" if all_execution_flags_false() else "ERROR",
            details=str(EXECUTION_FLAGS),
        )
    )

    checks.append(
        build_check(
            check_group="scope_control",
            check_name="long_side_not_established",
            passed=True,
            severity="WARNING",
            details="LONG-side strategy remains future work.",
        )
    )

    checks.append(
        build_check(
            check_group="scope_control",
            check_name="real_entries_not_approved",
            passed=True,
            severity="WARNING",
            details="Real entries remain unapproved.",
        )
    )

    checks_df = pd.DataFrame(checks)

    blocker_count = int(checks_df["blocker"].astype(bool).sum())
    error_count = int(checks_df["severity"].eq("ERROR").sum())
    warning_count = int(checks_df["severity"].eq("WARNING").sum())

    validation_passed = blocker_count == 0 and error_count == 0

    summary_row: dict[str, Any] = {
        "phase": "7.2",
        "adapter_name": "LOCAL_MARKET_CSV_READ_ONLY",
        "source_csv_path": str(active_config.source_csv_path),
        "output_csv_path": str(active_config.output_csv_path),
        "source_rows": source_rows,
        "output_rows": int(len(output_df)),
        "invalid_rows": invalid_rows,
        "output_written": output_written,
        "total_checks": int(len(checks_df)),
        "warning_count": warning_count,
        "error_count": error_count,
        "blocker_count": blocker_count,
        "local_csv_read_enabled": True,
        "real_market_fetch_enabled": False,
        "signal_generation_enabled": False,
        "price_level_generation_enabled": False,
        "long_side_established": False,
        "real_entries_approved": False,
        "paper_trade_execution_allowed": False,
        "real_capital_allowed": False,
        "live_alerts_allowed": False,
        "exchange_execution_allowed": False,
        "automation_allowed": False,
        "execution_allowed": False,
        "validation_passed": validation_passed,
        "validation_decision": (
            "PHASE_7_2_LOCAL_MARKET_CSV_READ_ONLY_ADAPTER_VALIDATED"
            if validation_passed
            else "PHASE_7_2_LOCAL_MARKET_CSV_READ_ONLY_ADAPTER_FAILED"
        ),
    }

    for flag_name, flag_value in EXECUTION_FLAGS.items():
        summary_row[flag_name] = flag_value

    summary_df = pd.DataFrame([summary_row])

    summary_df.to_csv(
        active_config.reports_dir
        / "local_market_csv_read_only_adapter_summary_v1.csv",
        index=False,
    )
    output_df.to_csv(
        active_config.reports_dir
        / "local_market_csv_read_only_adapter_output_preview_v1.csv",
        index=False,
    )
    checks_df.to_csv(
        active_config.reports_dir
        / "local_market_csv_read_only_adapter_checks_v1.csv",
        index=False,
    )

    return {
        "summary": summary_df,
        "output": output_df,
        "checks": checks_df,
    }