from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd


REPORTS_DIR = Path("reports/phase_7_6_price_levels_adapter_v1")

SOURCE_INPUT_DIR = Path("data/market_input/manual_reviewed_price_levels/input")
OPERATIONAL_PRICE_LEVEL_INPUT_DIR = (
    Path("data/forward_evidence/operational/input/price_levels")
)

CONTROLLED_SOURCE_PATH = (
    SOURCE_INPUT_DIR / "phase_7_6_manual_reviewed_price_levels_source_v1.csv"
)
CONTROLLED_OUTPUT_PATH = (
    OPERATIONAL_PRICE_LEVEL_INPUT_DIR
    / "phase_7_6_manual_reviewed_price_levels_input_v1.csv"
)

PHASE_6_CLOSURE_PATH = Path("docs/PHASE_6_OPERATIONAL_EVIDENCE_CLOSURE.md")
PHASE_7_1_CONTRACT_PATH = Path("docs/PHASE_7_REAL_MARKET_INPUT_BRIDGE_CONTRACT.md")
PHASE_7_2_ADAPTER_DOC_PATH = Path("docs/PHASE_7_LOCAL_MARKET_CSV_READ_ONLY_ADAPTER.md")
PHASE_7_3_COMPATIBILITY_DOC_PATH = Path("docs/PHASE_7_LOCAL_OHLC_BRIDGE_COMPATIBILITY.md")
PHASE_7_4_SIGNAL_DOC_PATH = Path("docs/PHASE_7_MANUAL_REVIEWED_SIGNAL_EXPORT_ADAPTER.md")
PHASE_7_5_SIGNAL_OHLC_DOC_PATH = Path("docs/PHASE_7_SIGNAL_OHLC_COMPATIBILITY_INCOMPLETE.md")

REQUIRED_PRICE_LEVEL_COLUMNS = [
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

OPERATIONAL_PRICE_LEVEL_COLUMNS = REQUIRED_PRICE_LEVEL_COLUMNS.copy()

VALID_DIRECTIONS = {"SHORT", "LONG"}

EXECUTION_FLAGS = {
    "paper_trade_execution_allowed": False,
    "real_capital_allowed": False,
    "live_alerts_allowed": False,
    "exchange_execution_allowed": False,
    "automation_allowed": False,
    "execution_allowed": False,
}


@dataclass(frozen=True)
class ManualReviewedPriceLevelsAdapterConfig:
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


def create_controlled_manual_reviewed_price_levels_fixture(
    config: ManualReviewedPriceLevelsAdapterConfig,
) -> None:
    config.source_csv_path.parent.mkdir(parents=True, exist_ok=True)

    fixture_df = pd.DataFrame(
        [
            {
                "signal_id": "PHASE_7_6_CONTROLLED_SHORT_SIGNAL",
                "context_name": "MANUAL_REVIEWED_SIGNAL_PHASE_7_4",
                "cost_profile": "BINANCE_SCALP_BASE_ESTIMATE",
                "direction": "SHORT",
                "entry_price": 65000.0,
                "stop_price": 65500.0,
                "target_price": 63750.0,
                "price_level_source": "MANUAL_REVIEWED_PRICE_LEVELS_PHASE_7_6",
                "notes": (
                    "Phase 7.6 controlled manual reviewed SHORT price levels. "
                    "Watch-only. No execution."
                ),
            }
        ]
    )

    fixture_df.to_csv(config.source_csv_path, index=False)


def safe_str(value: Any, default: str = "") -> str:
    if value is None:
        return default

    try:
        if pd.isna(value):
            return default
    except (TypeError, ValueError):
        return default

    return str(value).strip()


def safe_float(value: Any, default: float = 0.0) -> float:
    try:
        if pd.isna(value):
            return default

        return float(value)
    except (TypeError, ValueError):
        return default


def normalize_source_columns(df: pd.DataFrame) -> pd.DataFrame:
    normalized_df = df.copy()
    normalized_df.columns = [
        str(column).strip().lower() for column in normalized_df.columns
    ]
    return normalized_df


def build_empty_output_df() -> pd.DataFrame:
    return pd.DataFrame(columns=OPERATIONAL_PRICE_LEVEL_COLUMNS)


def validate_price_structure(row: pd.Series) -> bool:
    direction = safe_str(row.get("direction")).upper()
    entry_price = safe_float(row.get("entry_price"))
    stop_price = safe_float(row.get("stop_price"))
    target_price = safe_float(row.get("target_price"))

    if direction == "SHORT":
        return stop_price > entry_price > target_price

    if direction == "LONG":
        return stop_price < entry_price < target_price

    return False


def normalize_manual_reviewed_price_levels_df(
    source_df: pd.DataFrame,
) -> tuple[pd.DataFrame, int, list[str]]:
    working_df = normalize_source_columns(source_df)

    missing_columns = [
        column
        for column in REQUIRED_PRICE_LEVEL_COLUMNS
        if column not in working_df.columns
    ]

    if missing_columns:
        return build_empty_output_df(), len(working_df), missing_columns

    normalized_df = working_df[REQUIRED_PRICE_LEVEL_COLUMNS].copy()

    for column in [
        "signal_id",
        "context_name",
        "cost_profile",
        "direction",
        "price_level_source",
        "notes",
    ]:
        normalized_df[column] = normalized_df[column].map(safe_str)

    for column in ["entry_price", "stop_price", "target_price"]:
        normalized_df[column] = pd.to_numeric(
            normalized_df[column],
            errors="coerce",
        )

    normalized_df["signal_id"] = normalized_df["signal_id"].str.upper()
    normalized_df["context_name"] = normalized_df["context_name"].str.upper()
    normalized_df["cost_profile"] = normalized_df["cost_profile"].str.upper()
    normalized_df["direction"] = normalized_df["direction"].str.upper()
    normalized_df["price_level_source"] = normalized_df["price_level_source"].str.upper()

    structure_valid = normalized_df.apply(validate_price_structure, axis=1)

    invalid_mask = (
        normalized_df["signal_id"].eq("")
        | normalized_df["context_name"].eq("")
        | normalized_df["cost_profile"].eq("")
        | normalized_df["direction"].eq("")
        | normalized_df["price_level_source"].eq("")
        | ~normalized_df["direction"].isin(VALID_DIRECTIONS)
        | normalized_df["entry_price"].isna()
        | normalized_df["stop_price"].isna()
        | normalized_df["target_price"].isna()
        | (normalized_df["entry_price"] <= 0)
        | (normalized_df["stop_price"] <= 0)
        | (normalized_df["target_price"] <= 0)
        | ~structure_valid
    )

    invalid_rows = int(invalid_mask.sum())

    normalized_df = normalized_df.loc[~invalid_mask].copy()

    normalized_df = normalized_df[OPERATIONAL_PRICE_LEVEL_COLUMNS]
    normalized_df = normalized_df.drop_duplicates(
        subset=["signal_id", "context_name", "cost_profile", "direction"],
        keep="last",
    )
    normalized_df = normalized_df.sort_values(
        ["signal_id", "context_name", "cost_profile", "direction"]
    ).reset_index(drop=True)

    return normalized_df, invalid_rows, missing_columns


def validate_output_schema(output_df: pd.DataFrame) -> bool:
    return list(output_df.columns) == OPERATIONAL_PRICE_LEVEL_COLUMNS


def all_execution_flags_false() -> bool:
    return all(flag_value is False for flag_value in EXECUTION_FLAGS.values())


def count_direction_rows(output_df: pd.DataFrame, direction: str) -> int:
    if output_df.empty:
        return 0

    return int(output_df["direction"].astype(str).str.upper().eq(direction.upper()).sum())


def count_valid_structure_rows(output_df: pd.DataFrame) -> int:
    if output_df.empty:
        return 0

    return int(output_df.apply(validate_price_structure, axis=1).sum())


def calculate_average_risk_reward(output_df: pd.DataFrame) -> float:
    if output_df.empty:
        return 0.0

    rr_values: list[float] = []

    for _, row in output_df.iterrows():
        direction = safe_str(row.get("direction")).upper()
        entry_price = safe_float(row.get("entry_price"))
        stop_price = safe_float(row.get("stop_price"))
        target_price = safe_float(row.get("target_price"))

        if direction == "SHORT" and stop_price > entry_price > target_price:
            risk = stop_price - entry_price
            reward = entry_price - target_price
            rr_values.append(reward / risk)

        if direction == "LONG" and stop_price < entry_price < target_price:
            risk = entry_price - stop_price
            reward = target_price - entry_price
            rr_values.append(reward / risk)

    if not rr_values:
        return 0.0

    return float(sum(rr_values) / len(rr_values))


def validate_manual_reviewed_price_levels_adapter(
    config: ManualReviewedPriceLevelsAdapterConfig | None = None,
) -> dict[str, pd.DataFrame]:
    active_config = config or ManualReviewedPriceLevelsAdapterConfig()

    active_config.reports_dir.mkdir(parents=True, exist_ok=True)
    active_config.output_csv_path.parent.mkdir(parents=True, exist_ok=True)

    if active_config.create_controlled_fixture:
        create_controlled_manual_reviewed_price_levels_fixture(active_config)

    checks: list[dict[str, Any]] = []

    phase_anchors = [
        ("phase_6_closure_exists", PHASE_6_CLOSURE_PATH),
        ("phase_7_1_contract_exists", PHASE_7_1_CONTRACT_PATH),
        ("phase_7_2_adapter_doc_exists", PHASE_7_2_ADAPTER_DOC_PATH),
        ("phase_7_3_compatibility_doc_exists", PHASE_7_3_COMPATIBILITY_DOC_PATH),
        ("phase_7_4_signal_doc_exists", PHASE_7_4_SIGNAL_DOC_PATH),
        ("phase_7_5_signal_ohlc_doc_exists", PHASE_7_5_SIGNAL_OHLC_DOC_PATH),
    ]

    for check_name, path in phase_anchors:
        checks.append(
            build_check(
                check_group="phase_anchor",
                check_name=check_name,
                passed=path.exists(),
                severity="INFO" if path.exists() else "ERROR",
                details=str(path),
            )
        )

    source_exists = active_config.source_csv_path.exists()

    checks.append(
        build_check(
            check_group="source_file",
            check_name="source_price_levels_csv_exists",
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

        output_df, invalid_rows, missing_columns = normalize_manual_reviewed_price_levels_df(
            source_df=source_df
        )

        if not output_df.empty:
            output_df.to_csv(active_config.output_csv_path, index=False)
            output_written = True

    short_rows = count_direction_rows(output_df, "SHORT")
    long_rows = count_direction_rows(output_df, "LONG")
    valid_structure_rows = count_valid_structure_rows(output_df)
    average_risk_reward = calculate_average_risk_reward(output_df)

    checks.append(
        build_check(
            check_group="input_schema",
            check_name="required_price_level_columns_present",
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
            check_name="operational_price_level_schema_valid",
            passed=validate_output_schema(output_df),
            severity="INFO" if validate_output_schema(output_df) else "ERROR",
            details=",".join(output_df.columns.tolist()),
        )
    )

    checks.append(
        build_check(
            check_group="output_file",
            check_name="operational_price_level_file_written",
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
            check_group="price_structure",
            check_name="all_output_rows_have_valid_price_structure",
            passed=valid_structure_rows == len(output_df) and len(output_df) > 0,
            severity=(
                "INFO"
                if valid_structure_rows == len(output_df) and len(output_df) > 0
                else "ERROR"
            ),
            details=f"valid_structure_rows={valid_structure_rows}, output_rows={len(output_df)}",
        )
    )

    checks.append(
        build_check(
            check_group="directional_scope",
            check_name="direction_values_valid",
            passed=(short_rows + long_rows) == len(output_df) and len(output_df) > 0,
            severity=(
                "INFO"
                if (short_rows + long_rows) == len(output_df) and len(output_df) > 0
                else "ERROR"
            ),
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
            check_group="risk_reward",
            check_name="average_risk_reward_positive",
            passed=average_risk_reward > 0,
            severity="INFO" if average_risk_reward > 0 else "ERROR",
            details=f"average_risk_reward={average_risk_reward}",
        )
    )

    checks.append(
        build_check(
            check_group="source_scope",
            check_name="local_price_level_export_source",
            passed=True,
            severity="INFO",
            details="Adapter reads local manual reviewed price level export only.",
        )
    )

    checks.append(
        build_check(
            check_group="source_scope",
            check_name="real_market_fetch_disabled",
            passed=True,
            severity="INFO",
            details="No live market fetch is performed in Phase 7.6.",
        )
    )

    checks.append(
        build_check(
            check_group="source_scope",
            check_name="signal_generation_disabled",
            passed=True,
            severity="INFO",
            details="No signal output is generated in Phase 7.6.",
        )
    )

    checks.append(
        build_check(
            check_group="source_scope",
            check_name="ohlc_generation_disabled",
            passed=True,
            severity="INFO",
            details="No OHLC output is generated in Phase 7.6.",
        )
    )

    checks.append(
        build_check(
            check_group="source_scope",
            check_name="evidence_generation_disabled",
            passed=True,
            severity="INFO",
            details="Price levels alone do not generate complete evidence.",
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

    summary_df = pd.DataFrame(
        [
            {
                "phase": "7.6",
                "adapter_name": "MANUAL_REVIEWED_PRICE_LEVELS",
                "source_csv_path": str(active_config.source_csv_path),
                "output_csv_path": str(active_config.output_csv_path),
                "source_rows": source_rows,
                "output_rows": int(len(output_df)),
                "invalid_rows": invalid_rows,
                "short_rows": short_rows,
                "long_rows": long_rows,
                "valid_structure_rows": valid_structure_rows,
                "average_risk_reward": average_risk_reward,
                "output_written": output_written,
                "total_checks": int(len(checks_df)),
                "warning_count": warning_count,
                "error_count": error_count,
                "blocker_count": blocker_count,
                "manual_reviewed_price_levels_enabled": True,
                "real_market_fetch_enabled": False,
                "signal_generation_enabled": False,
                "ohlc_generation_enabled": False,
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
                    "PHASE_7_6_PRICE_LEVELS_ADAPTER_VALIDATED"
                    if validation_passed
                    else "PHASE_7_6_PRICE_LEVELS_ADAPTER_FAILED"
                ),
            }
        ]
    )

    summary_df.to_csv(
        active_config.reports_dir / "price_levels_adapter_summary_v1.csv",
        index=False,
    )
    output_df.to_csv(
        active_config.reports_dir / "price_levels_adapter_output_preview_v1.csv",
        index=False,
    )
    checks_df.to_csv(
        active_config.reports_dir / "price_levels_adapter_checks_v1.csv",
        index=False,
    )

    return {
        "summary": summary_df,
        "output": output_df,
        "checks": checks_df,
    }