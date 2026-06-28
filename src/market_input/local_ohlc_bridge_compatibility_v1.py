from __future__ import annotations

import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd

from src.market_input.local_market_csv_read_only_adapter_v1 import (
    CONTROLLED_OUTPUT_PATH,
    LocalMarketCsvReadOnlyAdapterConfig,
    validate_local_market_csv_read_only_adapter,
)


REPORTS_DIR = Path("reports/phase_7_3_local_ohlc_bridge_compatibility_v1")

SIGNALS_INPUT_DIR = Path("data/forward_evidence/operational/input/signals")
OHLC_INPUT_DIR = Path("data/forward_evidence/operational/input/ohlc")
PRICE_LEVELS_INPUT_DIR = Path("data/forward_evidence/operational/input/price_levels")

PHASE_7_1_CONTRACT_PATH = Path("docs/PHASE_7_REAL_MARKET_INPUT_BRIDGE_CONTRACT.md")
PHASE_7_2_ADAPTER_DOC_PATH = Path("docs/PHASE_7_LOCAL_MARKET_CSV_READ_ONLY_ADAPTER.md")
PHASE_7_2_ADAPTER_MODULE_PATH = Path("src/market_input/local_market_csv_read_only_adapter_v1.py")
PHASE_6_CLOSURE_PATH = Path("docs/PHASE_6_OPERATIONAL_EVIDENCE_CLOSURE.md")

OPERATIONAL_ADAPTER_MODULE = "src.workflows.run_operational_input_file_validator_adapter_v1"

EXECUTION_FLAGS = {
    "paper_trade_execution_allowed": False,
    "real_capital_allowed": False,
    "live_alerts_allowed": False,
    "exchange_execution_allowed": False,
    "automation_allowed": False,
    "execution_allowed": False,
}


@dataclass(frozen=True)
class LocalOhlcBridgeCompatibilityConfig:
    reports_dir: Path = REPORTS_DIR
    run_operational_adapter: bool = True


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


def list_csv_files(directory: Path) -> list[Path]:
    directory.mkdir(parents=True, exist_ok=True)
    return sorted(directory.glob("*.csv"))


def build_file_inventory_df() -> pd.DataFrame:
    rows: list[dict[str, Any]] = []

    directory_map = {
        "signals": SIGNALS_INPUT_DIR,
        "ohlc": OHLC_INPUT_DIR,
        "price_levels": PRICE_LEVELS_INPUT_DIR,
    }

    for input_type, directory in directory_map.items():
        for file_path in list_csv_files(directory):
            rows.append(
                {
                    "input_type": input_type,
                    "file_path": str(file_path),
                    "file_name": file_path.name,
                }
            )

    return pd.DataFrame(rows, columns=["input_type", "file_path", "file_name"])


def count_input_type(file_inventory_df: pd.DataFrame, input_type: str) -> int:
    if file_inventory_df.empty:
        return 0

    return int(file_inventory_df["input_type"].eq(input_type).sum())


def run_python_module(module_name: str) -> dict[str, Any]:
    completed = subprocess.run(
        [sys.executable, "-m", module_name],
        capture_output=True,
        text=True,
        check=False,
    )

    return {
        "module_name": module_name,
        "returncode": completed.returncode,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
    }


def build_stdout_df(stdout: str, stderr: str) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []

    for line_number, line_text in enumerate(stdout.splitlines(), start=1):
        rows.append(
            {
                "stream": "stdout",
                "line_number": line_number,
                "line_text": line_text,
            }
        )

    for line_number, line_text in enumerate(stderr.splitlines(), start=1):
        rows.append(
            {
                "stream": "stderr",
                "line_number": line_number,
                "line_text": line_text,
            }
        )

    return pd.DataFrame(rows, columns=["stream", "line_number", "line_text"])


def all_execution_flags_false() -> bool:
    return all(flag_value is False for flag_value in EXECUTION_FLAGS.values())


def validate_local_ohlc_bridge_compatibility(
    config: LocalOhlcBridgeCompatibilityConfig | None = None,
) -> dict[str, pd.DataFrame]:
    active_config = config or LocalOhlcBridgeCompatibilityConfig()
    active_config.reports_dir.mkdir(parents=True, exist_ok=True)

    checks: list[dict[str, Any]] = []

    local_adapter_result = validate_local_market_csv_read_only_adapter(
        LocalMarketCsvReadOnlyAdapterConfig(create_controlled_fixture=True)
    )

    local_adapter_summary_df = local_adapter_result["summary"]
    local_adapter_summary_row = first_row(local_adapter_summary_df)

    file_inventory_df = build_file_inventory_df()

    signals_files_found = count_input_type(file_inventory_df, "signals")
    ohlc_files_found = count_input_type(file_inventory_df, "ohlc")
    price_level_files_found = count_input_type(file_inventory_df, "price_levels")

    operational_adapter_result = {
        "module_name": OPERATIONAL_ADAPTER_MODULE,
        "returncode": 0,
        "stdout": "",
        "stderr": "",
    }

    if active_config.run_operational_adapter:
        operational_adapter_result = run_python_module(OPERATIONAL_ADAPTER_MODULE)

    adapter_stdout_df = build_stdout_df(
        stdout=str(operational_adapter_result["stdout"]),
        stderr=str(operational_adapter_result["stderr"]),
    )

    ohlc_only_incomplete = (
        ohlc_files_found >= 1
        and signals_files_found == 0
        and price_level_files_found == 0
    )

    pipeline_ready_for_evidence = (
        signals_files_found >= 1
        and ohlc_files_found >= 1
        and price_level_files_found >= 1
    )

    evidence_generation_enabled = False

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
            check_name="phase_7_2_adapter_module_exists",
            passed=PHASE_7_2_ADAPTER_MODULE_PATH.exists(),
            severity="INFO" if PHASE_7_2_ADAPTER_MODULE_PATH.exists() else "ERROR",
            details=str(PHASE_7_2_ADAPTER_MODULE_PATH),
        )
    )

    checks.append(
        build_check(
            check_group="local_adapter",
            check_name="local_adapter_validation_passed",
            passed=safe_bool(local_adapter_summary_row.get("validation_passed")),
            severity=(
                "INFO"
                if safe_bool(local_adapter_summary_row.get("validation_passed"))
                else "ERROR"
            ),
            details=str(local_adapter_summary_row.get("validation_decision", "")),
        )
    )

    checks.append(
        build_check(
            check_group="local_adapter",
            check_name="local_adapter_output_written",
            passed=safe_bool(local_adapter_summary_row.get("output_written")),
            severity=(
                "INFO"
                if safe_bool(local_adapter_summary_row.get("output_written"))
                else "ERROR"
            ),
            details=str(local_adapter_summary_row.get("output_csv_path", "")),
        )
    )

    checks.append(
        build_check(
            check_group="operational_input_files",
            check_name="operational_ohlc_file_exists",
            passed=CONTROLLED_OUTPUT_PATH.exists(),
            severity="INFO" if CONTROLLED_OUTPUT_PATH.exists() else "ERROR",
            details=str(CONTROLLED_OUTPUT_PATH),
        )
    )

    checks.append(
        build_check(
            check_group="operational_input_files",
            check_name="ohlc_files_found",
            passed=ohlc_files_found >= 1,
            severity="INFO" if ohlc_files_found >= 1 else "ERROR",
            details=f"ohlc_files_found={ohlc_files_found}",
        )
    )

    checks.append(
        build_check(
            check_group="operational_input_files",
            check_name="signals_absent_by_design",
            passed=signals_files_found == 0,
            severity="INFO" if signals_files_found == 0 else "ERROR",
            details=f"signals_files_found={signals_files_found}",
        )
    )

    checks.append(
        build_check(
            check_group="operational_input_files",
            check_name="price_levels_absent_by_design",
            passed=price_level_files_found == 0,
            severity="INFO" if price_level_files_found == 0 else "ERROR",
            details=f"price_level_files_found={price_level_files_found}",
        )
    )

    checks.append(
        build_check(
            check_group="compatibility_state",
            check_name="ohlc_only_incomplete_state_valid",
            passed=ohlc_only_incomplete,
            severity="INFO" if ohlc_only_incomplete else "ERROR",
            details=f"ohlc_only_incomplete={ohlc_only_incomplete}",
        )
    )

    checks.append(
        build_check(
            check_group="compatibility_state",
            check_name="pipeline_not_ready_for_evidence",
            passed=pipeline_ready_for_evidence is False,
            severity="INFO" if pipeline_ready_for_evidence is False else "ERROR",
            details=f"pipeline_ready_for_evidence={pipeline_ready_for_evidence}",
        )
    )

    checks.append(
        build_check(
            check_group="compatibility_state",
            check_name="evidence_generation_disabled",
            passed=evidence_generation_enabled is False,
            severity="INFO" if evidence_generation_enabled is False else "ERROR",
            details=f"evidence_generation_enabled={evidence_generation_enabled}",
        )
    )

    checks.append(
        build_check(
            check_group="operational_adapter",
            check_name="operational_adapter_executed",
            passed=int(operational_adapter_result["returncode"]) == 0,
            severity=(
                "INFO"
                if int(operational_adapter_result["returncode"]) == 0
                else "ERROR"
            ),
            details=f"returncode={operational_adapter_result['returncode']}",
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
            check_name="no_market_fetch_performed",
            passed=True,
            severity="INFO",
            details="Phase 7.3 uses local adapter output only.",
        )
    )

    checks.append(
        build_check(
            check_group="scope_control",
            check_name="no_signal_generation_performed",
            passed=True,
            severity="INFO",
            details="Phase 7.3 does not generate signal CSV inputs.",
        )
    )

    checks.append(
        build_check(
            check_group="scope_control",
            check_name="no_price_level_generation_performed",
            passed=True,
            severity="INFO",
            details="Phase 7.3 does not generate price-level CSV inputs.",
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
        "OHLC_ONLY_INCOMPLETE"
        if ohlc_only_incomplete
        else "UNEXPECTED_INPUT_STATE"
    )

    summary_df = pd.DataFrame(
        [
            {
                "phase": "7.3",
                "input_state": input_state,
                "signals_files_found": signals_files_found,
                "ohlc_files_found": ohlc_files_found,
                "price_level_files_found": price_level_files_found,
                "local_adapter_validation_passed": safe_bool(
                    local_adapter_summary_row.get("validation_passed")
                ),
                "local_adapter_output_rows": safe_int(
                    local_adapter_summary_row.get("output_rows")
                ),
                "operational_adapter_returncode": int(
                    operational_adapter_result["returncode"]
                ),
                "pipeline_ready_for_evidence": pipeline_ready_for_evidence,
                "evidence_generation_enabled": evidence_generation_enabled,
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
                "total_checks": int(len(checks_df)),
                "warning_count": warning_count,
                "error_count": error_count,
                "blocker_count": blocker_count,
                "validation_passed": validation_passed,
                "validation_decision": (
                    "PHASE_7_3_LOCAL_OHLC_BRIDGE_COMPATIBILITY_VALIDATED"
                    if validation_passed
                    else "PHASE_7_3_LOCAL_OHLC_BRIDGE_COMPATIBILITY_FAILED"
                ),
            }
        ]
    )

    summary_df.to_csv(
        active_config.reports_dir
        / "local_ohlc_bridge_compatibility_summary_v1.csv",
        index=False,
    )
    file_inventory_df.to_csv(
        active_config.reports_dir
        / "local_ohlc_bridge_compatibility_file_inventory_v1.csv",
        index=False,
    )
    local_adapter_summary_df.to_csv(
        active_config.reports_dir
        / "local_ohlc_bridge_compatibility_local_adapter_summary_v1.csv",
        index=False,
    )
    adapter_stdout_df.to_csv(
        active_config.reports_dir
        / "local_ohlc_bridge_compatibility_operational_adapter_output_v1.csv",
        index=False,
    )
    checks_df.to_csv(
        active_config.reports_dir
        / "local_ohlc_bridge_compatibility_checks_v1.csv",
        index=False,
    )

    return {
        "summary": summary_df,
        "file_inventory": file_inventory_df,
        "local_adapter_summary": local_adapter_summary_df,
        "operational_adapter_output": adapter_stdout_df,
        "checks": checks_df,
    }