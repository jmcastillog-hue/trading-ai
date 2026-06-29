from __future__ import annotations

import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd

from src.market_input.full_local_bridge_input_compatibility_v1 import (
    FullLocalBridgeInputCompatibilityConfig,
    validate_full_local_bridge_input_compatibility,
)


REPORTS_DIR = Path("reports/phase_7_8_full_local_bridge_evidence_cycle_v1")

PHASE_7_7_DOC_PATH = Path("docs/PHASE_7_FULL_LOCAL_BRIDGE_INPUT_COMPATIBILITY.md")
PHASE_7_6_DOC_PATH = Path("docs/PHASE_7_PRICE_LEVELS_ADAPTER.md")
PHASE_7_5_DOC_PATH = Path("docs/PHASE_7_SIGNAL_OHLC_COMPATIBILITY_INCOMPLETE.md")
PHASE_6_CLOSURE_PATH = Path("docs/PHASE_6_OPERATIONAL_EVIDENCE_CLOSURE.md")

OPERATIONAL_INTEGRATION_MODULE = (
    "src.workflows.run_operational_persistent_cycle_integration_v1"
)

OPERATIONAL_INTEGRATION_REPORTS_DIR = Path(
    "reports/operational_persistent_cycle_integration_v1"
)

OPERATIONAL_SUMMARY_PATH = (
    OPERATIONAL_INTEGRATION_REPORTS_DIR / "operational_integration_summary_v1.csv"
)
OPERATIONAL_GENERATED_OBSERVATIONS_PATH = (
    OPERATIONAL_INTEGRATION_REPORTS_DIR
    / "operational_integration_generated_observations_v1.csv"
)
OPERATIONAL_REJECTED_OBSERVATIONS_PATH = (
    OPERATIONAL_INTEGRATION_REPORTS_DIR
    / "operational_integration_rejected_observations_v1.csv"
)
OPERATIONAL_PERSISTENCE_SUMMARY_PATH = (
    OPERATIONAL_INTEGRATION_REPORTS_DIR
    / "operational_integration_persistence_summary_v1.csv"
)
OPERATIONAL_DATASET_PREVIEW_PATH = (
    OPERATIONAL_INTEGRATION_REPORTS_DIR
    / "operational_integration_dataset_preview_v1.csv"
)

PHASE_7_8_TARGET_HIT_OHLC_PATH = Path(
    "data/forward_evidence/operational/input/ohlc/"
    "phase_7_8_target_hit_extension_ohlc_v1.csv"
)

EXECUTION_FLAG_COLUMNS = [
    "paper_trade_execution_allowed",
    "real_capital_allowed",
    "live_alerts_allowed",
    "exchange_execution_allowed",
    "automation_allowed",
    "execution_allowed",
]


@dataclass(frozen=True)
class FullLocalBridgeEvidenceCycleConfig:
    reports_dir: Path = REPORTS_DIR
    create_controlled_fixtures: bool = True
    create_target_hit_ohlc_extension: bool = True
    run_operational_integration: bool = True


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


def safe_float(value: Any, default: float = 0.0) -> float:
    try:
        if pd.isna(value):
            return default

        return float(value)
    except (TypeError, ValueError):
        return default


def first_row(df: pd.DataFrame) -> dict[str, Any]:
    if df.empty:
        return {}

    return df.iloc[0].to_dict()


def load_csv_if_exists(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()

    try:
        return pd.read_csv(path)
    except Exception:
        return pd.DataFrame()


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


def execution_flags_false(summary_row: dict[str, Any]) -> bool:
    return all(
        safe_bool(summary_row.get(column), default=True) is False
        for column in EXECUTION_FLAG_COLUMNS
    )


def create_phase_7_8_target_hit_ohlc_extension() -> Path:
    PHASE_7_8_TARGET_HIT_OHLC_PATH.parent.mkdir(parents=True, exist_ok=True)

    target_hit_df = pd.DataFrame(
        [
            {
                "timestamp": "2026-06-27 23:45:00",
                "open": 64680.0,
                "high": 64700.0,
                "low": 63700.0,
                "close": 63800.0,
                "volume": 160.0,
                "symbol": "BTCUSDT",
                "timeframe": "15m",
                "data_source": "FULL_LOCAL_BRIDGE_TARGET_HIT_PHASE_7_8",
            }
        ]
    )

    target_hit_df.to_csv(PHASE_7_8_TARGET_HIT_OHLC_PATH, index=False)

    return PHASE_7_8_TARGET_HIT_OHLC_PATH


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


def generated_observation_target_hit_present(generated_df: pd.DataFrame) -> bool:
    if generated_df.empty:
        return False

    if "resolution_status" not in generated_df.columns:
        return False

    return bool(
        generated_df["resolution_status"]
        .astype(str)
        .str.upper()
        .eq("TARGET_HIT")
        .any()
    )


def generated_observation_positive_r_present(generated_df: pd.DataFrame) -> bool:
    if generated_df.empty:
        return False

    if "result_r" not in generated_df.columns:
        return False

    result_r = pd.to_numeric(
        generated_df["result_r"],
        errors="coerce",
    ).fillna(0.0)

    return bool((result_r > 0).any())


def validate_full_local_bridge_evidence_cycle(
    config: FullLocalBridgeEvidenceCycleConfig | None = None,
) -> dict[str, pd.DataFrame]:
    active_config = config or FullLocalBridgeEvidenceCycleConfig()
    active_config.reports_dir.mkdir(parents=True, exist_ok=True)

    checks: list[dict[str, Any]] = []

    phase_anchors = [
        ("phase_6_closure_exists", PHASE_6_CLOSURE_PATH),
        ("phase_7_5_doc_exists", PHASE_7_5_DOC_PATH),
        ("phase_7_6_doc_exists", PHASE_7_6_DOC_PATH),
        ("phase_7_7_doc_exists", PHASE_7_7_DOC_PATH),
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

    bridge_result = validate_full_local_bridge_input_compatibility(
        FullLocalBridgeInputCompatibilityConfig(
            create_controlled_fixtures=active_config.create_controlled_fixtures
        )
    )

    bridge_summary_df = bridge_result["summary"]
    bridge_summary_row = first_row(bridge_summary_df)

    bridge_validated = safe_bool(
        bridge_summary_row.get("validation_passed"),
        default=False,
    )
    bridge_ready = safe_bool(
        bridge_summary_row.get("pipeline_input_ready_for_evidence_cycle"),
        default=False,
    )

    checks.append(
        build_check(
            check_group="full_bridge_input",
            check_name="phase_7_7_bridge_validation_passed",
            passed=bridge_validated,
            severity="INFO" if bridge_validated else "ERROR",
            details=safe_str(bridge_summary_row.get("validation_decision")),
        )
    )

    checks.append(
        build_check(
            check_group="full_bridge_input",
            check_name="phase_7_7_bridge_ready_for_evidence_cycle",
            passed=bridge_ready,
            severity="INFO" if bridge_ready else "ERROR",
            details=f"pipeline_input_ready_for_evidence_cycle={bridge_ready}",
        )
    )

    target_hit_ohlc_path = Path("")

    if active_config.create_target_hit_ohlc_extension:
        target_hit_ohlc_path = create_phase_7_8_target_hit_ohlc_extension()

    checks.append(
        build_check(
            check_group="controlled_fixture",
            check_name="phase_7_8_target_hit_ohlc_extension_written",
            passed=target_hit_ohlc_path.exists(),
            severity="INFO" if target_hit_ohlc_path.exists() else "ERROR",
            details=str(target_hit_ohlc_path),
        )
    )

    integration_result = {
        "module_name": OPERATIONAL_INTEGRATION_MODULE,
        "returncode": 0,
        "stdout": "",
        "stderr": "",
    }

    if active_config.run_operational_integration:
        integration_result = run_python_module(OPERATIONAL_INTEGRATION_MODULE)

    command_output_df = build_stdout_df(
        stdout=safe_str(integration_result.get("stdout")),
        stderr=safe_str(integration_result.get("stderr")),
    )

    integration_returncode = safe_int(integration_result.get("returncode"), default=1)

    checks.append(
        build_check(
            check_group="operational_integration",
            check_name="operational_integration_command_succeeded",
            passed=integration_returncode == 0,
            severity="INFO" if integration_returncode == 0 else "ERROR",
            details=f"returncode={integration_returncode}",
        )
    )

    integration_summary_df = load_csv_if_exists(OPERATIONAL_SUMMARY_PATH)
    generated_observations_df = load_csv_if_exists(OPERATIONAL_GENERATED_OBSERVATIONS_PATH)
    rejected_observations_df = load_csv_if_exists(OPERATIONAL_REJECTED_OBSERVATIONS_PATH)
    persistence_summary_df = load_csv_if_exists(OPERATIONAL_PERSISTENCE_SUMMARY_PATH)
    dataset_preview_df = load_csv_if_exists(OPERATIONAL_DATASET_PREVIEW_PATH)

    integration_summary_row = first_row(integration_summary_df)
    persistence_summary_row = first_row(persistence_summary_df)

    integration_summary_exists = not integration_summary_df.empty

    checks.append(
        build_check(
            check_group="operational_integration",
            check_name="operational_integration_summary_exists",
            passed=integration_summary_exists,
            severity="INFO" if integration_summary_exists else "ERROR",
            details=str(OPERATIONAL_SUMMARY_PATH),
        )
    )

    adapter_decision = safe_str(integration_summary_row.get("adapter_decision"))
    integration_decision = safe_str(integration_summary_row.get("integration_decision"))

    input_ready_for_cycle = safe_bool(
        integration_summary_row.get("input_ready_for_cycle")
    )

    generated_observations = safe_int(
        integration_summary_row.get("generated_observations")
    )
    rejected_observations = safe_int(
        integration_summary_row.get("rejected_observations")
    )
    closed_observations = safe_int(
        integration_summary_row.get("closed_observations")
    )
    open_observations = safe_int(
        integration_summary_row.get("open_observations")
    )
    error_observations = safe_int(
        integration_summary_row.get("error_observations")
    )
    wins = safe_int(integration_summary_row.get("wins"))
    losses = safe_int(integration_summary_row.get("losses"))

    new_rows_added = safe_int(persistence_summary_row.get("new_rows_added"))
    duplicate_rows_skipped = safe_int(
        persistence_summary_row.get("duplicate_rows_skipped")
    )
    dataset_rows_after = safe_int(
        persistence_summary_row.get("dataset_rows_after")
    )

    dataset_write_performed = safe_bool(
        integration_summary_row.get("dataset_write_performed")
    )
    backup_created = safe_bool(
        integration_summary_row.get("backup_created")
    )
    snapshot_created = safe_bool(
        integration_summary_row.get("snapshot_created")
    )

    target_hit_present = generated_observation_target_hit_present(
        generated_observations_df
    )
    positive_r_present = generated_observation_positive_r_present(
        generated_observations_df
    )

    checks.append(
        build_check(
            check_group="operational_integration",
            check_name="adapter_ready_for_cycle",
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
            check_group="operational_integration",
            check_name="integration_input_ready_for_cycle",
            passed=input_ready_for_cycle,
            severity="INFO" if input_ready_for_cycle else "ERROR",
            details=f"input_ready_for_cycle={input_ready_for_cycle}",
        )
    )

    checks.append(
        build_check(
            check_group="evidence_generation",
            check_name="generated_observations_present",
            passed=generated_observations >= 1,
            severity="INFO" if generated_observations >= 1 else "ERROR",
            details=f"generated_observations={generated_observations}",
        )
    )

    checks.append(
        build_check(
            check_group="evidence_generation",
            check_name="no_rejected_observations",
            passed=rejected_observations == 0 and rejected_observations_df.empty,
            severity=(
                "INFO"
                if rejected_observations == 0 and rejected_observations_df.empty
                else "ERROR"
            ),
            details=f"rejected_observations={rejected_observations}",
        )
    )

    checks.append(
        build_check(
            check_group="evidence_generation",
            check_name="no_error_observations",
            passed=error_observations == 0,
            severity="INFO" if error_observations == 0 else "ERROR",
            details=f"error_observations={error_observations}",
        )
    )

    checks.append(
        build_check(
            check_group="evidence_generation",
            check_name="target_hit_observation_present",
            passed=target_hit_present,
            severity="INFO" if target_hit_present else "WARNING",
            details=f"target_hit_present={target_hit_present}",
        )
    )

    checks.append(
        build_check(
            check_group="evidence_generation",
            check_name="positive_result_r_present",
            passed=positive_r_present,
            severity="INFO" if positive_r_present else "WARNING",
            details=f"positive_r_present={positive_r_present}",
        )
    )

    checks.append(
        build_check(
            check_group="evidence_generation",
            check_name="closed_or_open_observation_present",
            passed=(closed_observations + open_observations) >= 1,
            severity=(
                "INFO"
                if (closed_observations + open_observations) >= 1
                else "ERROR"
            ),
            details=(
                f"closed_observations={closed_observations}, "
                f"open_observations={open_observations}"
            ),
        )
    )

    persistence_handled = (
        new_rows_added >= 1
        or duplicate_rows_skipped >= 1
        or dataset_rows_after >= 1
    )

    checks.append(
        build_check(
            check_group="persistence",
            check_name="dataset_persistence_or_duplicate_protection_handled",
            passed=persistence_handled,
            severity="INFO" if persistence_handled else "ERROR",
            details=(
                f"new_rows_added={new_rows_added}, "
                f"duplicate_rows_skipped={duplicate_rows_skipped}, "
                f"dataset_rows_after={dataset_rows_after}"
            ),
        )
    )

    checks.append(
        build_check(
            check_group="execution_restrictions",
            check_name="integration_execution_flags_false",
            passed=execution_flags_false(integration_summary_row),
            severity=(
                "INFO"
                if execution_flags_false(integration_summary_row)
                else "ERROR"
            ),
            details=str(
                {
                    column: integration_summary_row.get(column)
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
            details="Phase 7.8 uses local controlled bridge inputs only.",
        )
    )

    checks.append(
        build_check(
            check_group="scope_control",
            check_name="exchange_execution_not_performed",
            passed=True,
            severity="INFO",
            details="No exchange execution endpoint is called.",
        )
    )

    checks.append(
        build_check(
            check_group="scope_control",
            check_name="live_alerts_not_enabled",
            passed=True,
            severity="INFO",
            details="No live alert mechanism is enabled.",
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
                "phase": "7.8",
                "bridge_validation_passed": bridge_validated,
                "bridge_ready_for_evidence_cycle": bridge_ready,
                "target_hit_ohlc_extension_written": target_hit_ohlc_path.exists(),
                "operational_integration_returncode": integration_returncode,
                "adapter_decision": adapter_decision,
                "integration_decision": integration_decision,
                "input_ready_for_cycle": input_ready_for_cycle,
                "generated_observations": generated_observations,
                "rejected_observations": rejected_observations,
                "closed_observations": closed_observations,
                "open_observations": open_observations,
                "error_observations": error_observations,
                "wins": wins,
                "losses": losses,
                "target_hit_present": target_hit_present,
                "positive_result_r_present": positive_r_present,
                "new_rows_added": new_rows_added,
                "duplicate_rows_skipped": duplicate_rows_skipped,
                "dataset_rows_after": dataset_rows_after,
                "dataset_write_performed": dataset_write_performed,
                "backup_created": backup_created,
                "snapshot_created": snapshot_created,
                "persistence_handled": persistence_handled,
                "real_market_fetch_enabled": False,
                "paper_trade_execution_allowed": False,
                "real_capital_allowed": False,
                "live_alerts_allowed": False,
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
                    "PHASE_7_8_FULL_LOCAL_BRIDGE_EVIDENCE_CYCLE_VALIDATED"
                    if validation_passed
                    else "PHASE_7_8_FULL_LOCAL_BRIDGE_EVIDENCE_CYCLE_FAILED"
                ),
            }
        ]
    )

    summary_df.to_csv(
        active_config.reports_dir / "full_local_bridge_evidence_cycle_summary_v1.csv",
        index=False,
    )
    checks_df.to_csv(
        active_config.reports_dir / "full_local_bridge_evidence_cycle_checks_v1.csv",
        index=False,
    )
    bridge_summary_df.to_csv(
        active_config.reports_dir / "full_local_bridge_evidence_cycle_bridge_summary_v1.csv",
        index=False,
    )
    command_output_df.to_csv(
        active_config.reports_dir / "full_local_bridge_evidence_cycle_command_output_v1.csv",
        index=False,
    )
    integration_summary_df.to_csv(
        active_config.reports_dir / "full_local_bridge_evidence_cycle_integration_summary_v1.csv",
        index=False,
    )
    generated_observations_df.to_csv(
        active_config.reports_dir / "full_local_bridge_evidence_cycle_generated_observations_v1.csv",
        index=False,
    )
    rejected_observations_df.to_csv(
        active_config.reports_dir / "full_local_bridge_evidence_cycle_rejected_observations_v1.csv",
        index=False,
    )
    persistence_summary_df.to_csv(
        active_config.reports_dir / "full_local_bridge_evidence_cycle_persistence_summary_v1.csv",
        index=False,
    )
    dataset_preview_df.to_csv(
        active_config.reports_dir / "full_local_bridge_evidence_cycle_dataset_preview_v1.csv",
        index=False,
    )

    return {
        "summary": summary_df,
        "checks": checks_df,
        "bridge_summary": bridge_summary_df,
        "command_output": command_output_df,
        "integration_summary": integration_summary_df,
        "generated_observations": generated_observations_df,
        "rejected_observations": rejected_observations_df,
        "persistence_summary": persistence_summary_df,
        "dataset_preview": dataset_preview_df,
    }