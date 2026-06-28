from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd


REPORTS_DIR = Path("reports/phase_7_4_manual_reviewed_signal_export_adapter_v1")

SOURCE_INPUT_DIR = Path("data/market_input/manual_reviewed_signal_export/input")
OPERATIONAL_SIGNAL_INPUT_DIR = Path("data/forward_evidence/operational/input/signals")

CONTROLLED_SOURCE_PATH = (
    SOURCE_INPUT_DIR / "phase_7_4_manual_reviewed_signal_source_v1.csv"
)
CONTROLLED_OUTPUT_PATH = (
    OPERATIONAL_SIGNAL_INPUT_DIR / "phase_7_4_manual_reviewed_signal_input_v1.csv"
)

PHASE_7_1_CONTRACT_PATH = Path("docs/PHASE_7_REAL_MARKET_INPUT_BRIDGE_CONTRACT.md")
PHASE_7_2_ADAPTER_DOC_PATH = Path("docs/PHASE_7_LOCAL_MARKET_CSV_READ_ONLY_ADAPTER.md")
PHASE_7_3_COMPATIBILITY_DOC_PATH = Path("docs/PHASE_7_LOCAL_OHLC_BRIDGE_COMPATIBILITY.md")
PHASE_6_CLOSURE_PATH = Path("docs/PHASE_6_OPERATIONAL_EVIDENCE_CLOSURE.md")

REQUIRED_SIGNAL_COLUMNS = [
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

OPERATIONAL_SIGNAL_COLUMNS = REQUIRED_SIGNAL_COLUMNS.copy()

VALID_DIRECTIONS = {"SHORT", "LONG", "WAIT"}
VALID_ROUTER_DECISIONS = {"WATCH_ONLY"}

EXECUTION_FLAGS = {
    "paper_trade_execution_allowed": False,
    "real_capital_allowed": False,
    "live_alerts_allowed": False,
    "exchange_execution_allowed": False,
    "automation_allowed": False,
    "execution_allowed": False,
}


@dataclass(frozen=True)
class ManualReviewedSignalExportAdapterConfig:
    source_csv_path: Path = CONTROLLED_SOURCE_PATH
    output_csv_path: Path = CONTROLLED_OUTPUT_PATH
    reports_dir: Path = REPORTS_DIR
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


def create_controlled_manual_reviewed_signal_fixture(
    config: ManualReviewedSignalExportAdapterConfig,
) -> None:
    config.source_csv_path.parent.mkdir(parents=True, exist_ok=True)

    fixture_df = pd.DataFrame(
        [
            {
                "observed_at": "2026-06-27 23:00:00",
                "symbol": "BTCUSDT",
                "timeframe": "15m",
                "signal_type": "SHORT_ENTRY_SIGNAL",
                "router_decision": "WATCH_ONLY",
                "cost_profile": "BINANCE_SCALP_BASE_ESTIMATE",
                "context_name": "MANUAL_REVIEWED_SIGNAL_PHASE_7_4",
                "direction": "SHORT",
                "manual_review_required": True,
                "notes": (
                    "Phase 7.4 controlled manual reviewed signal. "
                    "Watch-only. No execution."
                ),
            }
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
    return pd.DataFrame(columns=OPERATIONAL_SIGNAL_COLUMNS)


def safe_bool(value: Any, default: bool = False) -> bool:
    if isinstance(value, bool):
        return value

    if value is None:
        return default

    try:
        if pd.isna(value):
            return default
    except (TypeError, ValueError):
        return default

    normalized = str(value).strip().lower()

    if normalized in {"true", "1", "yes", "y"}:
        return True

    if normalized in {"false", "0", "no", "n"}:
        return False

    return default


def normalize_bool_series(series: pd.Series) -> pd.Series:
    return series.apply(lambda value: safe_bool(value, default=False))


def normalize_manual_reviewed_signal_df(
    source_df: pd.DataFrame,
) -> tuple[pd.DataFrame, int, list[str]]:
    working_df = normalize_source_columns(source_df)

    missing_columns = [
        column for column in REQUIRED_SIGNAL_COLUMNS if column not in working_df.columns
    ]

    if missing_columns:
        return build_empty_output_df(), len(working_df), missing_columns

    normalized_df = working_df[REQUIRED_SIGNAL_COLUMNS].copy()

    for column in [
        "symbol",
        "timeframe",
        "signal_type",
        "router_decision",
        "cost_profile",
        "context_name",
        "direction",
        "notes",
    ]:
        normalized_df[column] = normalized_df[column].astype(str).str.strip()

    normalized_df["observed_at"] = pd.to_datetime(
        normalized_df["observed_at"],
        errors="coerce",
    )

    normalized_df["manual_review_required"] = normalize_bool_series(
        normalized_df["manual_review_required"]
    )

    normalized_df["router_decision"] = normalized_df["router_decision"].str.upper()
    normalized_df["direction"] = normalized_df["direction"].str.upper()

    invalid_mask = (
        normalized_df["observed_at"].isna()
        | normalized_df["symbol"].eq("")
        | normalized_df["timeframe"].eq("")
        | normalized_df["signal_type"].eq("")
        | normalized_df["router_decision"].eq("")
        | normalized_df["cost_profile"].eq("")
        | normalized_df["context_name"].eq("")
        | normalized_df["direction"].eq("")
        | ~normalized_df["manual_review_required"]
        | ~normalized_df["router_decision"].isin(VALID_ROUTER_DECISIONS)
        | ~normalized_df["direction"].isin(VALID_DIRECTIONS)
    )

    invalid_rows = int(invalid_mask.sum())

    normalized_df = normalized_df.loc[~invalid_mask].copy()

    normalized_df["observed_at"] = normalized_df["observed_at"].dt.strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    normalized_df = normalized_df[OPERATIONAL_SIGNAL_COLUMNS]
    normalized_df = normalized_df.drop_duplicates(
        subset=["observed_at", "symbol", "timeframe", "signal_type", "direction"],
        keep="last",
    )
    normalized_df = normalized_df.sort_values(
        ["observed_at", "symbol", "timeframe", "signal_type"]
    ).reset_index(drop=True)

    return normalized_df, invalid_rows, missing_columns


def validate_output_schema(output_df: pd.DataFrame) -> bool:
    return list(output_df.columns) == OPERATIONAL_SIGNAL_COLUMNS


def all_execution_flags_false() -> bool:
    return all(flag_value is False for flag_value in EXECUTION_FLAGS.values())


def count_true_manual_review_rows(output_df: pd.DataFrame) -> int:
    if output_df.empty:
        return 0

    return int(output_df["manual_review_required"].apply(safe_bool).sum())


def count_watch_only_rows(output_df: pd.DataFrame) -> int:
    if output_df.empty:
        return 0

    return int(output_df["router_decision"].astype(str).str.upper().eq("WATCH_ONLY").sum())


def count_direction_rows(output_df: pd.DataFrame, direction: str) -> int:
    if output_df.empty:
        return 0

    return int(output_df["direction"].astype(str).str.upper().eq(direction.upper()).sum())


def validate_manual_reviewed_signal_export_adapter(
    config: ManualReviewedSignalExportAdapterConfig | None = None,
) -> dict[str, pd.DataFrame]:
    active_config = config or ManualReviewedSignalExportAdapterConfig()

    active_config.reports_dir.mkdir(parents=True, exist_ok=True)
    active_config.output_csv_path.parent.mkdir(parents=True, exist_ok=True)

    if active_config.create_controlled_fixture:
        create_controlled_manual_reviewed_signal_fixture(active_config)

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
            check_group="phase_anchor",
            check_name="phase_7_2_adapter_doc_exists",
            passed=PHASE_7_2_ADAPTER_DOC_PATH.exists(),
            severity="INFO" if PHASE_7_2_ADAPTER_DOC_PATH.exists() else "ERROR",
            details=str(PHASE_7_2_ADAPTER_DOC_PATH),
        )
    )

    checks.append(
        build_check(
            check_group="phase_anchor",
            check_name="phase_7_3_compatibility_doc_exists",
            passed=PHASE_7_3_COMPATIBILITY_DOC_PATH.exists(),
            severity="INFO" if PHASE_7_3_COMPATIBILITY_DOC_PATH.exists() else "ERROR",
            details=str(PHASE_7_3_COMPATIBILITY_DOC_PATH),
        )
    )

    checks.append(
        build_check(
            check_group="source_file",
            check_name="source_signal_csv_exists",
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

        output_df, invalid_rows, missing_columns = normalize_manual_reviewed_signal_df(
            source_df=source_df
        )

        if not output_df.empty:
            output_df.to_csv(active_config.output_csv_path, index=False)
            output_written = True

    manual_review_rows = count_true_manual_review_rows(output_df)
    watch_only_rows = count_watch_only_rows(output_df)
    short_rows = count_direction_rows(output_df, "SHORT")
    long_rows = count_direction_rows(output_df, "LONG")

    checks.append(
        build_check(
            check_group="input_schema",
            check_name="required_signal_columns_present",
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
            check_name="operational_signal_schema_valid",
            passed=validate_output_schema(output_df),
            severity="INFO" if validate_output_schema(output_df) else "ERROR",
            details=",".join(output_df.columns.tolist()),
        )
    )

    checks.append(
        build_check(
            check_group="output_file",
            check_name="operational_signal_file_written",
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
            check_group="safety_rules",
            check_name="all_output_rows_manual_review_required",
            passed=manual_review_rows == len(output_df) and len(output_df) > 0,
            severity=(
                "INFO"
                if manual_review_rows == len(output_df) and len(output_df) > 0
                else "ERROR"
            ),
            details=f"manual_review_rows={manual_review_rows}, output_rows={len(output_df)}",
        )
    )

    checks.append(
        build_check(
            check_group="safety_rules",
            check_name="all_output_rows_watch_only",
            passed=watch_only_rows == len(output_df) and len(output_df) > 0,
            severity=(
                "INFO"
                if watch_only_rows == len(output_df) and len(output_df) > 0
                else "ERROR"
            ),
            details=f"watch_only_rows={watch_only_rows}, output_rows={len(output_df)}",
        )
    )

    checks.append(
        build_check(
            check_group="directional_scope",
            check_name="direction_values_valid",
            passed=(short_rows + long_rows) <= len(output_df),
            severity="INFO" if (short_rows + long_rows) <= len(output_df) else "ERROR",
            details=f"short_rows={short_rows}, long_rows={long_rows}",
        )
    )

    checks.append(
        build_check(
            check_group="directional_scope",
            check_name="controlled_fixture_short_present",
            passed=short_rows >= 1,
            severity="INFO" if short_rows >= 1 else "WARNING",
            details=f"short_rows={short_rows}",
        )
    )

    checks.append(
        build_check(
            check_group="source_scope",
            check_name="local_signal_export_source",
            passed=True,
            severity="INFO",
            details="Adapter reads local manual reviewed signal export only.",
        )
    )

    checks.append(
        build_check(
            check_group="source_scope",
            check_name="real_market_fetch_disabled",
            passed=True,
            severity="INFO",
            details="No live market fetch is performed in Phase 7.4.",
        )
    )

    checks.append(
        build_check(
            check_group="source_scope",
            check_name="price_level_generation_disabled",
            passed=True,
            severity="INFO",
            details="No price-level output is generated in Phase 7.4.",
        )
    )

    checks.append(
        build_check(
            check_group="source_scope",
            check_name="evidence_generation_disabled",
            passed=True,
            severity="INFO",
            details="Signal alone does not generate complete evidence.",
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
        "phase": "7.4",
        "adapter_name": "MANUAL_REVIEWED_SIGNAL_EXPORT",
        "source_csv_path": str(active_config.source_csv_path),
        "output_csv_path": str(active_config.output_csv_path),
        "source_rows": source_rows,
        "output_rows": int(len(output_df)),
        "invalid_rows": invalid_rows,
        "manual_review_rows": manual_review_rows,
        "watch_only_rows": watch_only_rows,
        "short_rows": short_rows,
        "long_rows": long_rows,
        "output_written": output_written,
        "total_checks": int(len(checks_df)),
        "warning_count": warning_count,
        "error_count": error_count,
        "blocker_count": blocker_count,
        "manual_review_signal_export_enabled": True,
        "real_market_fetch_enabled": False,
        "price_level_generation_enabled": False,
        "evidence_generation_enabled": False,
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
            "PHASE_7_4_MANUAL_REVIEWED_SIGNAL_EXPORT_ADAPTER_VALIDATED"
            if validation_passed
            else "PHASE_7_4_MANUAL_REVIEWED_SIGNAL_EXPORT_ADAPTER_FAILED"
        ),
    }

    for flag_name, flag_value in EXECUTION_FLAGS.items():
        summary_row[flag_name] = flag_value

    summary_df = pd.DataFrame([summary_row])

    summary_df.to_csv(
        active_config.reports_dir
        / "manual_reviewed_signal_export_adapter_summary_v1.csv",
        index=False,
    )
    output_df.to_csv(
        active_config.reports_dir
        / "manual_reviewed_signal_export_adapter_output_preview_v1.csv",
        index=False,
    )
    checks_df.to_csv(
        active_config.reports_dir
        / "manual_reviewed_signal_export_adapter_checks_v1.csv",
        index=False,
    )

    return {
        "summary": summary_df,
        "output": output_df,
        "checks": checks_df,
    }

def validate_manual_reviewed_signal_export_adapter(
    config: ManualReviewedSignalExportAdapterConfig | None = None,
) -> dict[str, pd.DataFrame]:
    active_config = config or ManualReviewedSignalExportAdapterConfig()

    active_config.reports_dir.mkdir(parents=True, exist_ok=True)
    active_config.output_csv_path.parent.mkdir(parents=True, exist_ok=True)

    if active_config.create_controlled_fixture:
        create_controlled_manual_reviewed_signal_fixture(active_config)

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
            check_group="phase_anchor",
            check_name="phase_7_2_adapter_doc_exists",
            passed=PHASE_7_2_ADAPTER_DOC_PATH.exists(),
            severity="INFO" if PHASE_7_2_ADAPTER_DOC_PATH.exists() else "ERROR",
            details=str(PHASE_7_2_ADAPTER_DOC_PATH),
        )
    )

    checks.append(
        build_check(
            check_group="phase_anchor",
            check_name="phase_7_3_compatibility_doc_exists",
            passed=PHASE_7_3_COMPATIBILITY_DOC_PATH.exists(),
            severity="INFO" if PHASE_7_3_COMPATIBILITY_DOC_PATH.exists() else "ERROR",
            details=str(PHASE_7_3_COMPATIBILITY_DOC_PATH),
        )
    )

    checks.append(
        build_check(
            check_group="source_file",
            check_name="source_signal_csv_exists",
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

        output_df, invalid_rows, missing_columns = normalize_manual_reviewed_signal_df(
            source_df=source_df
        )

        if not output_df.empty:
            output_df.to_csv(active_config.output_csv_path, index=False)
            output_written = True

    manual_review_rows = count_true_manual_review_rows(output_df)
    watch_only_rows = count_watch_only_rows(output_df)
    short_rows = count_direction_rows(output_df, "SHORT")
    long_rows = count_direction_rows(output_df, "LONG")

    checks.append(
        build_check(
            check_group="input_schema",
            check_name="required_signal_columns_present",
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
            check_name="operational_signal_schema_valid",
            passed=validate_output_schema(output_df),
            severity="INFO" if validate_output_schema(output_df) else "ERROR",
            details=",".join(output_df.columns.tolist()),
        )
    )

    checks.append(
        build_check(
            check_group="output_file",
            check_name="operational_signal_file_written",
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
            check_group="safety_rules",
            check_name="all_output_rows_manual_review_required",
            passed=manual_review_rows == len(output_df) and len(output_df) > 0,
            severity=(
                "INFO"
                if manual_review_rows == len(output_df) and len(output_df) > 0
                else "ERROR"
            ),
            details=f"manual_review_rows={manual_review_rows}, output_rows={len(output_df)}",
        )
    )

    checks.append(
        build_check(
            check_group="safety_rules",
            check_name="all_output_rows_watch_only",
            passed=watch_only_rows == len(output_df) and len(output_df) > 0,
            severity=(
                "INFO"
                if watch_only_rows == len(output_df) and len(output_df) > 0
                else "ERROR"
            ),
            details=f"watch_only_rows={watch_only_rows}, output_rows={len(output_df)}",
        )
    )

    checks.append(
        build_check(
            check_group="directional_scope",
            check_name="direction_values_valid",
            passed=(short_rows + long_rows) <= len(output_df),
            severity="INFO" if (short_rows + long_rows) <= len(output_df) else "ERROR",
            details=f"short_rows={short_rows}, long_rows={long_rows}",
        )
    )

    checks.append(
        build_check(
            check_group="directional_scope",
            check_name="controlled_fixture_short_present",
            passed=short_rows >= 1,
            severity="INFO" if short_rows >= 1 else "WARNING",
            details=f"short_rows={short_rows}",
        )
    )

    checks.append(
        build_check(
            check_group="source_scope",
            check_name="local_signal_export_source",
            passed=True,
            severity="INFO",
            details="Adapter reads local manual reviewed signal export only.",
        )
    )

    checks.append(
        build_check(
            check_group="source_scope",
            check_name="real_market_fetch_disabled",
            passed=True,
            severity="INFO",
            details="No live market fetch is performed in Phase 7.4.",
        )
    )

    checks.append(
        build_check(
            check_group="source_scope",
            check_name="price_level_generation_disabled",
            passed=True,
            severity="INFO",
            details="No price-level output is generated in Phase 7.4.",
        )
    )

    checks.append(
        build_check(
            check_group="source_scope",
            check_name="evidence_generation_disabled",
            passed=True,
            severity="INFO",
            details="Signal alone does not generate complete evidence.",
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
        "phase": "7.4",
        "adapter_name": "MANUAL_REVIEWED_SIGNAL_EXPORT",
        "source_csv_path": str(active_config.source_csv_path),
        "output_csv_path": str(active_config.output_csv_path),
        "source_rows": source_rows,
        "output_rows": int(len(output_df)),
        "invalid_rows": invalid_rows,
        "manual_review_rows": manual_review_rows,
        "watch_only_rows": watch_only_rows,
        "short_rows": short_rows,
        "long_rows": long_rows,
        "output_written": output_written,
        "total_checks": int(len(checks_df)),
        "warning_count": warning_count,
        "error_count": error_count,
        "blocker_count": blocker_count,
        "manual_review_signal_export_enabled": True,
        "real_market_fetch_enabled": False,
        "price_level_generation_enabled": False,
        "evidence_generation_enabled": False,
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
            "PHASE_7_4_MANUAL_REVIEWED_SIGNAL_EXPORT_ADAPTER_VALIDATED"
            if validation_passed
            else "PHASE_7_4_MANUAL_REVIEWED_SIGNAL_EXPORT_ADAPTER_FAILED"
        ),
    }

    for flag_name, flag_value in EXECUTION_FLAGS.items():
        summary_row[flag_name] = flag_value

    summary_df = pd.DataFrame([summary_row])

    summary_df.to_csv(
        active_config.reports_dir
        / "manual_reviewed_signal_export_adapter_summary_v1.csv",
        index=False,
    )
    output_df.to_csv(
        active_config.reports_dir
        / "manual_reviewed_signal_export_adapter_output_preview_v1.csv",
        index=False,
    )
    checks_df.to_csv(
        active_config.reports_dir
        / "manual_reviewed_signal_export_adapter_checks_v1.csv",
        index=False,
    )

    return {
        "summary": summary_df,
        "output": output_df,
        "checks": checks_df,
    }