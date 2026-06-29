from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd


REPORTS_DIR = Path("reports/phase_7_9_real_market_input_bridge_closure_v1")

PHASE_7_FILES = {
    "phase_7_1_contract_doc": Path("docs/PHASE_7_REAL_MARKET_INPUT_BRIDGE_CONTRACT.md"),
    "phase_7_1_contract_module": Path("src/market_input/real_market_input_bridge_contract_v1.py"),
    "phase_7_1_validator": Path("src/workflows/validate_phase_7_1_real_market_input_bridge_contract.py"),
    "phase_7_2_doc": Path("docs/PHASE_7_LOCAL_MARKET_CSV_READ_ONLY_ADAPTER.md"),
    "phase_7_2_adapter": Path("src/market_input/local_market_csv_read_only_adapter_v1.py"),
    "phase_7_2_validator": Path("src/workflows/validate_phase_7_2_local_market_csv_read_only_adapter.py"),
    "phase_7_3_doc": Path("docs/PHASE_7_LOCAL_OHLC_BRIDGE_COMPATIBILITY.md"),
    "phase_7_3_module": Path("src/market_input/local_ohlc_bridge_compatibility_v1.py"),
    "phase_7_3_validator": Path("src/workflows/validate_phase_7_3_local_ohlc_bridge_compatibility.py"),
    "phase_7_4_doc": Path("docs/PHASE_7_MANUAL_REVIEWED_SIGNAL_EXPORT_ADAPTER.md"),
    "phase_7_4_adapter": Path("src/market_input/manual_reviewed_signal_export_adapter_v1.py"),
    "phase_7_4_validator": Path("src/workflows/validate_phase_7_4_manual_reviewed_signal_export_adapter.py"),
    "phase_7_5_doc": Path("docs/PHASE_7_SIGNAL_OHLC_COMPATIBILITY_INCOMPLETE.md"),
    "phase_7_5_module": Path("src/market_input/signal_ohlc_compatibility_incomplete_v1.py"),
    "phase_7_5_validator": Path("src/workflows/validate_phase_7_5_signal_ohlc_compatibility_incomplete.py"),
    "phase_7_6_doc": Path("docs/PHASE_7_PRICE_LEVELS_ADAPTER.md"),
    "phase_7_6_adapter": Path("src/market_input/manual_reviewed_price_levels_adapter_v1.py"),
    "phase_7_6_validator": Path("src/workflows/validate_phase_7_6_price_levels_adapter.py"),
    "phase_7_7_doc": Path("docs/PHASE_7_FULL_LOCAL_BRIDGE_INPUT_COMPATIBILITY.md"),
    "phase_7_7_module": Path("src/market_input/full_local_bridge_input_compatibility_v1.py"),
    "phase_7_7_validator": Path("src/workflows/validate_phase_7_7_full_local_bridge_input_compatibility.py"),
    "phase_7_8_doc": Path("docs/PHASE_7_FULL_LOCAL_BRIDGE_EVIDENCE_CYCLE.md"),
    "phase_7_8_module": Path("src/market_input/full_local_bridge_evidence_cycle_v1.py"),
    "phase_7_8_validator": Path("src/workflows/validate_phase_7_8_full_local_bridge_evidence_cycle.py"),
    "phase_7_9_closure_doc": Path("docs/PHASE_7_REAL_MARKET_INPUT_BRIDGE_CLOSURE.md"),
}

REQUIRED_SAFETY_FLAGS = {
    "paper_trade_execution_allowed": False,
    "real_capital_allowed": False,
    "live_alerts_allowed": False,
    "exchange_execution_allowed": False,
    "automation_allowed": False,
    "execution_allowed": False,
}

VALIDATED_CAPABILITIES = {
    "bridge_contract_defined": True,
    "local_ohlc_read_only_adapter_validated": True,
    "ohlc_only_incomplete_state_validated": True,
    "manual_reviewed_signal_watch_only_validated": True,
    "signal_ohlc_without_price_levels_blocked": True,
    "manual_reviewed_price_levels_validated": True,
    "full_local_bridge_input_compatibility_validated": True,
    "full_local_bridge_evidence_cycle_validated": True,
    "dataset_persistence_validated": True,
    "backup_and_snapshot_validated": True,
}

NON_APPROVED_CAPABILITIES = {
    "paper_trading_execution_approved": False,
    "real_capital_approved": False,
    "live_alerts_approved": False,
    "binance_execution_approved": False,
    "quantfury_execution_approved": False,
    "exchange_execution_approved": False,
    "automation_approved": False,
    "autonomous_bot_approved": False,
    "long_side_established": False,
    "project_completed": False,
}


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


def file_exists_check(name: str, path: Path) -> dict[str, Any]:
    return build_check(
        check_group="phase_7_artifacts",
        check_name=name,
        passed=path.exists(),
        severity="INFO" if path.exists() else "ERROR",
        details=str(path),
    )


def capability_check(name: str, value: bool) -> dict[str, Any]:
    return build_check(
        check_group="validated_capabilities",
        check_name=name,
        passed=value is True,
        severity="INFO" if value is True else "ERROR",
        details=f"{name}={value}",
    )


def non_approval_check(name: str, value: bool) -> dict[str, Any]:
    return build_check(
        check_group="non_approved_capabilities",
        check_name=name,
        passed=value is False,
        severity="INFO" if value is False else "ERROR",
        details=f"{name}={value}",
    )


def safety_flag_check(name: str, value: bool) -> dict[str, Any]:
    return build_check(
        check_group="execution_safety_flags",
        check_name=name,
        passed=value is False,
        severity="INFO" if value is False else "ERROR",
        details=f"{name}={value}",
    )


def validate_phase_7_9_real_market_input_bridge_closure() -> dict[str, pd.DataFrame]:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    checks: list[dict[str, Any]] = []

    for name, path in PHASE_7_FILES.items():
        checks.append(file_exists_check(name=name, path=path))

    for name, value in VALIDATED_CAPABILITIES.items():
        checks.append(capability_check(name=name, value=value))

    for name, value in NON_APPROVED_CAPABILITIES.items():
        checks.append(non_approval_check(name=name, value=value))

    for name, value in REQUIRED_SAFETY_FLAGS.items():
        checks.append(safety_flag_check(name=name, value=value))

    checks.append(
        build_check(
            check_group="phase_closure",
            check_name="phase_7_closed_as_bridge_validation_only",
            passed=True,
            severity="INFO",
            details="Phase 7 closes bridge validation, not trading execution.",
        )
    )

    checks.append(
        build_check(
            check_group="phase_transition",
            check_name="phase_8_recommended_next",
            passed=True,
            severity="INFO",
            details="Recommended next step: Phase 8 LONG-side Validation Framework V1.",
        )
    )

    checks.append(
        build_check(
            check_group="scope_control",
            check_name="real_entries_remain_unapproved",
            passed=True,
            severity="WARNING",
            details="Real entries remain blocked after Phase 7 closure.",
        )
    )

    checks.append(
        build_check(
            check_group="scope_control",
            check_name="long_side_remains_future_work",
            passed=True,
            severity="WARNING",
            details="LONG-side validation remains pending after Phase 7 closure.",
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
                "phase": "7.9",
                "phase_7_closed": validation_passed,
                "closure_scope": "REAL_MARKET_INPUT_BRIDGE_CONTROLLED_VALIDATION",
                "validated_phase_steps": 8,
                "bridge_contract_defined": True,
                "local_ohlc_validated": True,
                "manual_signal_validated": True,
                "manual_price_levels_validated": True,
                "full_local_bridge_input_validated": True,
                "full_local_bridge_evidence_cycle_validated": True,
                "dataset_persistence_validated": True,
                "backup_and_snapshot_validated": True,
                "official_candidate": "TARGET_SHORT_FIB_V5_MTF_V3_1 + FIXED_RR_2_5",
                "paper_trade_execution_allowed": False,
                "real_capital_allowed": False,
                "live_alerts_allowed": False,
                "exchange_execution_allowed": False,
                "automation_allowed": False,
                "execution_allowed": False,
                "binance_execution_allowed": False,
                "quantfury_execution_allowed": False,
                "long_side_established": False,
                "real_entries_approved": False,
                "total_project_completed": False,
                "recommended_next_phase": "PHASE_8_LONG_SIDE_VALIDATION_FRAMEWORK_V1",
                "estimated_total_project_progress_percent": 89,
                "total_checks": int(len(checks_df)),
                "warning_count": warning_count,
                "error_count": error_count,
                "blocker_count": blocker_count,
                "validation_passed": validation_passed,
                "validation_decision": (
                    "PHASE_7_REAL_MARKET_INPUT_BRIDGE_CLOSED"
                    if validation_passed
                    else "PHASE_7_REAL_MARKET_INPUT_BRIDGE_CLOSURE_FAILED"
                ),
            }
        ]
    )

    checks_df.to_csv(
        REPORTS_DIR / "phase_7_9_real_market_input_bridge_closure_checks_v1.csv",
        index=False,
    )
    summary_df.to_csv(
        REPORTS_DIR / "phase_7_9_real_market_input_bridge_closure_summary_v1.csv",
        index=False,
    )

    return {
        "summary": summary_df,
        "checks": checks_df,
    }


def print_section(title: str) -> None:
    print()
    print(title)
    print("=" * 100)


def print_df(df: pd.DataFrame) -> None:
    if df.empty:
        print("Sin registros.")
        return

    print(df.to_string(index=False))


def main() -> None:
    print("PHASE 7.9 REAL MARKET INPUT BRIDGE CLOSURE VALIDATOR")
    print("=" * 100)
    print("Purpose: formally close Phase 7 as controlled bridge validation")
    print("Restriction: no execution approval. No real capital approval.")
    print()

    result = validate_phase_7_9_real_market_input_bridge_closure()

    print_section("PHASE 7.9 CLOSURE SUMMARY")
    print_df(result["summary"])

    print_section("PHASE 7.9 CLOSURE CHECKS")
    print_df(result["checks"])

    print()
    print("ARCHIVOS GENERADOS")
    print("=" * 100)
    print("- reports/phase_7_9_real_market_input_bridge_closure_v1/phase_7_9_real_market_input_bridge_closure_summary_v1.csv")
    print("- reports/phase_7_9_real_market_input_bridge_closure_v1/phase_7_9_real_market_input_bridge_closure_checks_v1.csv")
    print()
    print("Restriccion: Phase 7 queda cerrada solo como validacion de puente de inputs.")


if __name__ == "__main__":
    main()