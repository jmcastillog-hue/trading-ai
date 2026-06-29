from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd

from src.journal.operational_input_file_validator_adapter_v1 import (
    OperationalInputFileValidatorAdapterConfig,
    run_operational_input_file_validator_adapter,
)
from src.market_input.local_market_csv_read_only_adapter_v1 import (
    LocalMarketCsvReadOnlyAdapterConfig,
    validate_local_market_csv_read_only_adapter,
)
from src.market_input.manual_reviewed_price_levels_adapter_v1 import (
    ManualReviewedPriceLevelsAdapterConfig,
    validate_manual_reviewed_price_levels_adapter,
)
from src.market_input.manual_reviewed_signal_export_adapter_v1 import (
    ManualReviewedSignalExportAdapterConfig,
    validate_manual_reviewed_signal_export_adapter,
)


REPORTS_DIR = Path("reports/phase_7_7_full_local_bridge_input_compatibility_v1")

PHASE_6_CLOSURE_PATH = Path("docs/PHASE_6_OPERATIONAL_EVIDENCE_CLOSURE.md")
PHASE_7_1_CONTRACT_PATH = Path("docs/PHASE_7_REAL_MARKET_INPUT_BRIDGE_CONTRACT.md")
PHASE_7_2_ADAPTER_DOC_PATH = Path("docs/PHASE_7_LOCAL_MARKET_CSV_READ_ONLY_ADAPTER.md")
PHASE_7_3_COMPATIBILITY_DOC_PATH = Path("docs/PHASE_7_LOCAL_OHLC_BRIDGE_COMPATIBILITY.md")
PHASE_7_4_SIGNAL_DOC_PATH = Path("docs/PHASE_7_MANUAL_REVIEWED_SIGNAL_EXPORT_ADAPTER.md")
PHASE_7_5_SIGNAL_OHLC_DOC_PATH = Path("docs/PHASE_7_SIGNAL_OHLC_COMPATIBILITY_INCOMPLETE.md")
PHASE_7_6_PRICE_LEVELS_DOC_PATH = Path("docs/PHASE_7_PRICE_LEVELS_ADAPTER.md")

EXECUTION_FLAG_COLUMNS = [
    "paper_trade_execution_allowed",
    "real_capital_allowed",
    "live_alerts_allowed",
    "exchange_execution_allowed",
    "automation_allowed",
    "execution_allowed",
]


@dataclass(frozen=True)
class FullLocalBridgeInputCompatibilityConfig:
    reports_dir: Path = REPORTS_DIR
    create_controlled_fixtures: bool = True


def safe_str(value: Any, default: str = "") -> str:
    if value is None:
        return default

    try:
        if pd.isna(value):
            return default
    except (TypeError, ValueError):
        return default

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


def safe_int(value: Any, default: int = 0) -> int:
    try:
        if pd.isna(value):
            return default

        return int(float(value))
    except (TypeError, ValueError):
        return default


def first_row(df: pd.DataFrame) -> dict[str, Any]:
    if df.empty:
        return {}

    return df.iloc[0].to_dict()


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


def normalized_tuple_set(
    df: pd.DataFrame,
    columns: list[str],
) -> set[tuple[str, ...]]:
    if df.empty:
        return set()

    if not set(columns).issubset(df.columns):
        return set()

    result: set[tuple[str, ...]] = set()

    for _, row in df.iterrows():
        result.add(
            tuple(
                safe_str(row.get(column)).upper()
                if column != "timeframe"
                else safe_str(row.get(column)).lower()
                for column in columns
            )
        )

    return result


def operational_execution_flags_false(summary_row: dict[str, Any]) -> bool:
    return all(
        safe_bool(summary_row.get(column), default=True) is False
        for column in EXECUTION_FLAG_COLUMNS
    )


def build_signal_ohlc_compatibility_check(
    adapted_signals_df: pd.DataFrame,
    adapted_ohlc_df: pd.DataFrame,
) -> dict[str, Any]:
    signal_keys = normalized_tuple_set(
        adapted_signals_df,
        ["symbol", "timeframe"],
    )
    ohlc_keys = normalized_tuple_set(
        adapted_ohlc_df,
        ["symbol", "timeframe"],
    )

    intersection = signal_keys.intersection(ohlc_keys)
    passed = len(intersection) > 0

    return build_check(
        check_group="cross_input_compatibility",
        check_name="signal_ohlc_symbol_timeframe_match",
        passed=passed,
        severity="INFO" if passed else "ERROR",
        details=f"matches={sorted(intersection)}",
    )


def build_signal_price_level_compatibility_check(
    adapted_signals_df: pd.DataFrame,
    adapted_price_levels_df: pd.DataFrame,
) -> dict[str, Any]:
    signal_keys = normalized_tuple_set(
        adapted_signals_df,
        ["context_name", "cost_profile", "direction"],
    )
    price_level_keys = normalized_tuple_set(
        adapted_price_levels_df,
        ["context_name", "cost_profile", "direction"],
    )

    intersection = signal_keys.intersection(price_level_keys)
    passed = len(intersection) > 0

    return build_check(
        check_group="cross_input_compatibility",
        check_name="signal_price_level_context_cost_direction_match",
        passed=passed,
        severity="INFO" if passed else "ERROR",
        details=f"matches={sorted(intersection)}",
    )


def validate_full_local_bridge_input_compatibility(
    config: FullLocalBridgeInputCompatibilityConfig | None = None,
) -> dict[str, pd.DataFrame]:
    active_config = config or FullLocalBridgeInputCompatibilityConfig()
    active_config.reports_dir.mkdir(parents=True, exist_ok=True)

    checks: list[dict[str, Any]] = []

    local_adapter_result = validate_local_market_csv_read_only_adapter(
        LocalMarketCsvReadOnlyAdapterConfig(
            create_controlled_fixture=active_config.create_controlled_fixtures
        )
    )

    signal_adapter_result = validate_manual_reviewed_signal_export_adapter(
        ManualReviewedSignalExportAdapterConfig(
            create_controlled_fixture=active_config.create_controlled_fixtures
        )
    )

    price_levels_adapter_result = validate_manual_reviewed_price_levels_adapter(
        ManualReviewedPriceLevelsAdapterConfig(
            create_controlled_fixture=active_config.create_controlled_fixtures
        )
    )

    local_adapter_summary_df = local_adapter_result["summary"]
    signal_adapter_summary_df = signal_adapter_result["summary"]
    price_levels_adapter_summary_df = price_levels_adapter_result["summary"]

    local_adapter_summary_row = first_row(local_adapter_summary_df)
    signal_adapter_summary_row = first_row(signal_adapter_summary_df)
    price_levels_adapter_summary_row = first_row(price_levels_adapter_summary_df)

    (
        operational_summary_df,
        operational_validation_df,
        operational_file_inventory_df,
        adapted_signals_df,
        adapted_ohlc_df,
        adapted_price_levels_df,
        rejected_files_df,
    ) = run_operational_input_file_validator_adapter(
        config=OperationalInputFileValidatorAdapterConfig(
            operational_root="data/forward_evidence/operational",
            paper_trade_execution_allowed=False,
            real_capital_allowed=False,
            live_alerts_allowed=False,
            exchange_execution_allowed=False,
            automation_allowed=False,
        )
    )

    operational_summary_row = first_row(operational_summary_df)

    phase_anchors = [
        ("phase_6_closure_exists", PHASE_6_CLOSURE_PATH),
        ("phase_7_1_contract_exists", PHASE_7_1_CONTRACT_PATH),
        ("phase_7_2_adapter_doc_exists", PHASE_7_2_ADAPTER_DOC_PATH),
        ("phase_7_3_compatibility_doc_exists", PHASE_7_3_COMPATIBILITY_DOC_PATH),
        ("phase_7_4_signal_doc_exists", PHASE_7_4_SIGNAL_DOC_PATH),
        ("phase_7_5_signal_ohlc_doc_exists", PHASE_7_5_SIGNAL_OHLC_DOC_PATH),
        ("phase_7_6_price_levels_doc_exists", PHASE_7_6_PRICE_LEVELS_DOC_PATH),
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

    checks.append(
        build_check(
            check_group="source_adapters",
            check_name="local_ohlc_adapter_validation_passed",
            passed=safe_bool(local_adapter_summary_row.get("validation_passed")),
            severity=(
                "INFO"
                if safe_bool(local_adapter_summary_row.get("validation_passed"))
                else "ERROR"
            ),
            details=safe_str(local_adapter_summary_row.get("validation_decision")),
        )
    )

    checks.append(
        build_check(
            check_group="source_adapters",
            check_name="manual_signal_adapter_validation_passed",
            passed=safe_bool(signal_adapter_summary_row.get("validation_passed")),
            severity=(
                "INFO"
                if safe_bool(signal_adapter_summary_row.get("validation_passed"))
                else "ERROR"
            ),
            details=safe_str(signal_adapter_summary_row.get("validation_decision")),
        )
    )

    checks.append(
        build_check(
            check_group="source_adapters",
            check_name="manual_price_levels_adapter_validation_passed",
            passed=safe_bool(price_levels_adapter_summary_row.get("validation_passed")),
            severity=(
                "INFO"
                if safe_bool(price_levels_adapter_summary_row.get("validation_passed"))
                else "ERROR"
            ),
            details=safe_str(price_levels_adapter_summary_row.get("validation_decision")),
        )
    )

    signal_files_found = safe_int(operational_summary_row.get("signal_files_found"))
    ohlc_files_found = safe_int(operational_summary_row.get("ohlc_files_found"))
    price_level_files_found = safe_int(
        operational_summary_row.get("price_level_files_found")
    )

    adapted_signal_rows = safe_int(operational_summary_row.get("adapted_signal_rows"))
    adapted_ohlc_rows = safe_int(operational_summary_row.get("adapted_ohlc_rows"))
    adapted_price_level_rows = safe_int(
        operational_summary_row.get("adapted_price_level_rows")
    )

    input_ready_for_cycle = safe_bool(
        operational_summary_row.get("input_ready_for_cycle")
    )
    processing_allowed = safe_bool(
        operational_summary_row.get("processing_allowed")
    )
    adapter_decision = safe_str(
        operational_summary_row.get("adapter_decision")
    )

    checks.append(
        build_check(
            check_group="operational_input_files",
            check_name="signals_files_present",
            passed=signal_files_found >= 1,
            severity="INFO" if signal_files_found >= 1 else "ERROR",
            details=f"signal_files_found={signal_files_found}",
        )
    )

    checks.append(
        build_check(
            check_group="operational_input_files",
            check_name="ohlc_files_present",
            passed=ohlc_files_found >= 1,
            severity="INFO" if ohlc_files_found >= 1 else "ERROR",
            details=f"ohlc_files_found={ohlc_files_found}",
        )
    )

    checks.append(
        build_check(
            check_group="operational_input_files",
            check_name="price_level_files_present",
            passed=price_level_files_found >= 1,
            severity="INFO" if price_level_files_found >= 1 else "ERROR",
            details=f"price_level_files_found={price_level_files_found}",
        )
    )

    checks.append(
        build_check(
            check_group="operational_adaptation",
            check_name="adapted_signal_rows_present",
            passed=adapted_signal_rows >= 1,
            severity="INFO" if adapted_signal_rows >= 1 else "ERROR",
            details=f"adapted_signal_rows={adapted_signal_rows}",
        )
    )

    checks.append(
        build_check(
            check_group="operational_adaptation",
            check_name="adapted_ohlc_rows_present",
            passed=adapted_ohlc_rows >= 1,
            severity="INFO" if adapted_ohlc_rows >= 1 else "ERROR",
            details=f"adapted_ohlc_rows={adapted_ohlc_rows}",
        )
    )

    checks.append(
        build_check(
            check_group="operational_adaptation",
            check_name="adapted_price_level_rows_present",
            passed=adapted_price_level_rows >= 1,
            severity="INFO" if adapted_price_level_rows >= 1 else "ERROR",
            details=f"adapted_price_level_rows={adapted_price_level_rows}",
        )
    )

    checks.append(
        build_signal_ohlc_compatibility_check(
            adapted_signals_df=adapted_signals_df,
            adapted_ohlc_df=adapted_ohlc_df,
        )
    )

    checks.append(
        build_signal_price_level_compatibility_check(
            adapted_signals_df=adapted_signals_df,
            adapted_price_levels_df=adapted_price_levels_df,
        )
    )

    checks.append(
        build_check(
            check_group="operational_adapter",
            check_name="operational_adapter_validation_passed",
            passed=safe_bool(operational_summary_row.get("validation_passed")),
            severity=(
                "INFO"
                if safe_bool(operational_summary_row.get("validation_passed"))
                else "ERROR"
            ),
            details=f"validation_error_count={operational_summary_row.get('validation_error_count')}",
        )
    )

    checks.append(
        build_check(
            check_group="operational_adapter",
            check_name="operational_adapter_ready_for_cycle",
            passed=input_ready_for_cycle,
            severity="INFO" if input_ready_for_cycle else "ERROR",
            details=f"input_ready_for_cycle={input_ready_for_cycle}",
        )
    )

    checks.append(
        build_check(
            check_group="operational_adapter",
            check_name="operational_adapter_processing_allowed",
            passed=processing_allowed,
            severity="INFO" if processing_allowed else "ERROR",
            details=f"processing_allowed={processing_allowed}",
        )
    )

    checks.append(
        build_check(
            check_group="operational_adapter",
            check_name="operational_adapter_decision_ready",
            passed=adapter_decision == "OPERATIONAL_INPUT_VALIDATED_READY_FOR_CYCLE",
            severity=(
                "INFO"
                if adapter_decision == "OPERATIONAL_INPUT_VALIDATED_READY_FOR_CYCLE"
                else "ERROR"
            ),
            details=f"adapter_decision={adapter_decision}",
        )
    )

    checks.append(
        build_check(
            check_group="execution_restrictions",
            check_name="operational_execution_flags_false",
            passed=operational_execution_flags_false(operational_summary_row),
            severity=(
                "INFO"
                if operational_execution_flags_false(operational_summary_row)
                else "ERROR"
            ),
            details=str(
                {
                    column: operational_summary_row.get(column)
                    for column in EXECUTION_FLAG_COLUMNS
                }
            ),
        )
    )

    checks.append(
        build_check(
            check_group="scope_control",
            check_name="real_market_fetch_not_performed",
            passed=True,
            severity="INFO",
            details="Phase 7.7 uses local controlled fixtures only.",
        )
    )

    checks.append(
        build_check(
            check_group="scope_control",
            check_name="evidence_cycle_not_executed",
            passed=True,
            severity="INFO",
            details="Phase 7.7 validates bridge readiness only.",
        )
    )

    checks.append(
        build_check(
            check_group="scope_control",
            check_name="live_alerts_not_enabled",
            passed=True,
            severity="INFO",
            details="No live alerts are enabled.",
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

    input_state = (
        "FULL_LOCAL_BRIDGE_INPUT_READY_FOR_EVIDENCE_CYCLE"
        if input_ready_for_cycle
        and processing_allowed
        and adapter_decision == "OPERATIONAL_INPUT_VALIDATED_READY_FOR_CYCLE"
        else "FULL_LOCAL_BRIDGE_INPUT_NOT_READY"
    )

    summary_df = pd.DataFrame(
        [
            {
                "phase": "7.7",
                "input_state": input_state,
                "signal_files_found": signal_files_found,
                "ohlc_files_found": ohlc_files_found,
                "price_level_files_found": price_level_files_found,
                "adapted_signal_rows": adapted_signal_rows,
                "adapted_ohlc_rows": adapted_ohlc_rows,
                "adapted_price_level_rows": adapted_price_level_rows,
                "local_adapter_validation_passed": safe_bool(
                    local_adapter_summary_row.get("validation_passed")
                ),
                "signal_adapter_validation_passed": safe_bool(
                    signal_adapter_summary_row.get("validation_passed")
                ),
                "price_levels_adapter_validation_passed": safe_bool(
                    price_levels_adapter_summary_row.get("validation_passed")
                ),
                "operational_adapter_validation_passed": safe_bool(
                    operational_summary_row.get("validation_passed")
                ),
                "input_ready_for_cycle": input_ready_for_cycle,
                "processing_allowed": processing_allowed,
                "adapter_decision": adapter_decision,
                "pipeline_input_ready_for_evidence_cycle": input_ready_for_cycle,
                "evidence_cycle_executed": False,
                "evidence_generation_enabled": False,
                "real_market_fetch_enabled": False,
                "live_alerts_allowed": False,
                "paper_trade_execution_allowed": False,
                "real_capital_allowed": False,
                "exchange_execution_allowed": False,
                "automation_allowed": False,
                "execution_allowed": False,
                "long_side_established": False,
                "real_entries_approved": False,
                "total_checks": int(len(checks_df)),
                "warning_count": warning_count,
                "error_count": error_count,
                "blocker_count": blocker_count,
                "validation_passed": validation_passed,
                "validation_decision": (
                    "PHASE_7_7_FULL_LOCAL_BRIDGE_INPUT_COMPATIBILITY_VALIDATED"
                    if validation_passed
                    else "PHASE_7_7_FULL_LOCAL_BRIDGE_INPUT_COMPATIBILITY_FAILED"
                ),
            }
        ]
    )

    summary_df.to_csv(
        active_config.reports_dir / "full_local_bridge_input_compatibility_summary_v1.csv",
        index=False,
    )
    checks_df.to_csv(
        active_config.reports_dir / "full_local_bridge_input_compatibility_checks_v1.csv",
        index=False,
    )
    local_adapter_summary_df.to_csv(
        active_config.reports_dir / "full_local_bridge_local_adapter_summary_v1.csv",
        index=False,
    )
    signal_adapter_summary_df.to_csv(
        active_config.reports_dir / "full_local_bridge_signal_adapter_summary_v1.csv",
        index=False,
    )
    price_levels_adapter_summary_df.to_csv(
        active_config.reports_dir / "full_local_bridge_price_levels_adapter_summary_v1.csv",
        index=False,
    )
    operational_summary_df.to_csv(
        active_config.reports_dir / "full_local_bridge_operational_summary_v1.csv",
        index=False,
    )
    operational_file_inventory_df.to_csv(
        active_config.reports_dir / "full_local_bridge_operational_file_inventory_v1.csv",
        index=False,
    )
    operational_validation_df.to_csv(
        active_config.reports_dir / "full_local_bridge_operational_validation_v1.csv",
        index=False,
    )
    adapted_signals_df.to_csv(
        active_config.reports_dir / "full_local_bridge_adapted_signals_v1.csv",
        index=False,
    )
    adapted_ohlc_df.to_csv(
        active_config.reports_dir / "full_local_bridge_adapted_ohlc_v1.csv",
        index=False,
    )
    adapted_price_levels_df.to_csv(
        active_config.reports_dir / "full_local_bridge_adapted_price_levels_v1.csv",
        index=False,
    )
    rejected_files_df.to_csv(
        active_config.reports_dir / "full_local_bridge_rejected_files_v1.csv",
        index=False,
    )

    return {
        "summary": summary_df,
        "checks": checks_df,
        "local_adapter_summary": local_adapter_summary_df,
        "signal_adapter_summary": signal_adapter_summary_df,
        "price_levels_adapter_summary": price_levels_adapter_summary_df,
        "operational_summary": operational_summary_df,
        "operational_file_inventory": operational_file_inventory_df,
        "operational_validation": operational_validation_df,
        "adapted_signals": adapted_signals_df,
        "adapted_ohlc": adapted_ohlc_df,
        "adapted_price_levels": adapted_price_levels_df,
        "rejected_files": rejected_files_df,
    }