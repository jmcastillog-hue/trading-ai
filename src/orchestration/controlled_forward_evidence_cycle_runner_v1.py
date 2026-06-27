from __future__ import annotations

import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

from src.validation.operational_safety_guard_preflight_v1 import (
    OperationalSafetyGuardPreflightConfig,
    run_operational_safety_guard_preflight,
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
class ControlledForwardEvidenceCycleRunnerConfig:
    require_clean_git: bool = False
    stop_on_preflight_blocker: bool = True
    python_executable: str = sys.executable
    reports_dir: Path = Path("reports/controlled_forward_evidence_cycle_runner_v1")

    bootstrap_module: str = "src.workflows.run_operational_forward_evidence_bootstrap_v1"
    input_validator_module: str = "src.workflows.run_operational_input_file_validator_adapter_v1"
    integration_module: str = "src.workflows.run_operational_persistent_cycle_integration_v1"
    run_log_module: str = "src.workflows.run_forward_evidence_run_log_v1"

    preflight_summary_path: Path = Path(
        "reports/operational_safety_guard_preflight_v1/"
        "operational_safety_guard_preflight_summary_v1.csv"
    )
    integration_summary_path: Path = Path(
        "reports/operational_persistent_cycle_integration_v1/"
        "operational_integration_summary_v1.csv"
    )
    run_log_summary_path: Path = Path(
        "reports/forward_evidence_run_log_v1/"
        "forward_evidence_run_log_summary_v1.csv"
    )


def safe_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value

    if pd.isna(value):
        return False

    normalized = str(value).strip().lower()
    return normalized in {"true", "1", "yes", "y"}


def safe_int(value: Any, default: int = 0) -> int:
    try:
        if pd.isna(value):
            return default
        return int(float(value))
    except (TypeError, ValueError):
        return default


def safe_str(value: Any, default: str = "") -> str:
    if pd.isna(value):
        return default
    return str(value)


def read_csv_or_empty(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()

    try:
        return pd.read_csv(path)
    except Exception:
        return pd.DataFrame()


def first_row(df: pd.DataFrame) -> dict[str, Any]:
    if df.empty:
        return {}
    return df.iloc[0].to_dict()


def run_git_command(args: list[str]) -> str:
    try:
        completed = subprocess.run(
            ["git", *args],
            capture_output=True,
            text=True,
            check=False,
        )
        if completed.returncode != 0:
            return "UNKNOWN"
        return completed.stdout.strip() or "UNKNOWN"
    except Exception:
        return "UNKNOWN"


def get_git_branch() -> str:
    return run_git_command(["branch", "--show-current"])


def get_git_commit() -> str:
    return run_git_command(["rev-parse", "--short", "HEAD"])


def run_python_module(
    module_name: str,
    config: ControlledForwardEvidenceCycleRunnerConfig,
) -> dict[str, Any]:
    started_at = datetime.now(timezone.utc)

    completed = subprocess.run(
        [
            config.python_executable,
            "-m",
            module_name,
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    finished_at = datetime.now(timezone.utc)

    stdout = completed.stdout or ""
    stderr = completed.stderr or ""

    return {
        "module_name": module_name,
        "started_at_utc": started_at.strftime("%Y-%m-%d %H:%M:%S"),
        "finished_at_utc": finished_at.strftime("%Y-%m-%d %H:%M:%S"),
        "returncode": int(completed.returncode),
        "command_succeeded": completed.returncode == 0,
        "stdout_tail": stdout[-4000:],
        "stderr_tail": stderr[-4000:],
    }


def all_execution_flags_false(*rows: dict[str, Any]) -> bool:
    for row in rows:
        for column in EXECUTION_FLAG_COLUMNS:
            if safe_bool(row.get(column, False)):
                return False

    return True


def classify_cycle_decision(
    preflight_row: dict[str, Any],
    command_results_df: pd.DataFrame,
    integration_row: dict[str, Any],
    run_log_row: dict[str, Any],
) -> str:
    preflight_passed = safe_bool(preflight_row.get("preflight_passed", False))
    blocker_count = safe_int(preflight_row.get("blocker_count", 0))

    if not preflight_passed or blocker_count > 0:
        return "CONTROLLED_CYCLE_BLOCKED_BY_PREFLIGHT"

    if not command_results_df.empty:
        if not bool(command_results_df["command_succeeded"].all()):
            return "CONTROLLED_CYCLE_FAILED"

    integration_decision = safe_str(integration_row.get("integration_decision"))

    if integration_decision == "OPERATIONAL_INTEGRATION_COMPLETED_WITH_EVIDENCE":
        return "CONTROLLED_CYCLE_COMPLETED_WITH_EVIDENCE"

    if integration_decision == "OPERATIONAL_INTEGRATION_COMPLETED_NO_DATASET_CHANGES":
        return "CONTROLLED_CYCLE_COMPLETED_NO_DATASET_CHANGES"

    if integration_decision == "OPERATIONAL_INTEGRATION_WAITING_FOR_VALID_INPUTS":
        return "CONTROLLED_CYCLE_WAITING_FOR_INPUTS"

    if not run_log_row:
        return "CONTROLLED_CYCLE_FAILED"

    return "CONTROLLED_CYCLE_COMPLETED_NO_DATASET_CHANGES"


def build_summary_df(
    config: ControlledForwardEvidenceCycleRunnerConfig,
    preflight_summary_df: pd.DataFrame,
    command_results_df: pd.DataFrame,
) -> pd.DataFrame:
    preflight_row = first_row(preflight_summary_df)

    integration_summary_df = read_csv_or_empty(config.integration_summary_path)
    run_log_summary_df = read_csv_or_empty(config.run_log_summary_path)

    integration_row = first_row(integration_summary_df)
    run_log_row = first_row(run_log_summary_df)

    cycle_decision = classify_cycle_decision(
        preflight_row=preflight_row,
        command_results_df=command_results_df,
        integration_row=integration_row,
        run_log_row=run_log_row,
    )

    execution_flags_ok = all_execution_flags_false(
        preflight_row,
        integration_row,
        run_log_row,
    )

    command_success = (
        not command_results_df.empty
        and bool(command_results_df["command_succeeded"].all())
    )

    cycle_validated = (
        execution_flags_ok
        and cycle_decision
        in {
            "CONTROLLED_CYCLE_COMPLETED_WITH_EVIDENCE",
            "CONTROLLED_CYCLE_COMPLETED_NO_DATASET_CHANGES",
            "CONTROLLED_CYCLE_WAITING_FOR_INPUTS",
        }
        and command_success
    )

    validation_decision = (
        "PHASE_6_4_CONTROLLED_FORWARD_EVIDENCE_CYCLE_RUNNER_VALIDATED"
        if cycle_validated
        else "PHASE_6_4_CONTROLLED_FORWARD_EVIDENCE_CYCLE_RUNNER_FAILED"
    )

    return pd.DataFrame(
        [
            {
                "cycle_timestamp_utc": datetime.now(timezone.utc).strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),
                "git_branch": get_git_branch(),
                "git_commit": get_git_commit(),
                "require_clean_git": config.require_clean_git,
                "preflight_passed": safe_bool(
                    preflight_row.get("preflight_passed", False)
                ),
                "preflight_decision": safe_str(
                    preflight_row.get("preflight_decision"),
                    "UNKNOWN",
                ),
                "preflight_blocker_count": safe_int(
                    preflight_row.get("blocker_count"),
                    0,
                ),
                "commands_executed": int(len(command_results_df)),
                "commands_succeeded": int(
                    command_results_df["command_succeeded"].sum()
                )
                if not command_results_df.empty
                else 0,
                "commands_failed": int(
                    (~command_results_df["command_succeeded"].astype(bool)).sum()
                )
                if not command_results_df.empty
                else 0,
                "adapter_decision": safe_str(
                    integration_row.get("adapter_decision"),
                    "UNKNOWN",
                ),
                "integration_decision": safe_str(
                    integration_row.get("integration_decision"),
                    "UNKNOWN",
                ),
                "generated_observations": safe_int(
                    integration_row.get("generated_observations"),
                    0,
                ),
                "rejected_observations": safe_int(
                    integration_row.get("rejected_observations"),
                    0,
                ),
                "closed_observations": safe_int(
                    integration_row.get("closed_observations"),
                    0,
                ),
                "open_observations": safe_int(
                    integration_row.get("open_observations"),
                    0,
                ),
                "error_observations": safe_int(
                    integration_row.get("error_observations"),
                    0,
                ),
                "new_rows_added": safe_int(
                    integration_row.get("new_rows_added"),
                    0,
                ),
                "duplicate_rows_skipped": safe_int(
                    integration_row.get("duplicate_rows_skipped"),
                    0,
                ),
                "dataset_rows_after": safe_int(
                    integration_row.get("dataset_rows_after"),
                    0,
                ),
                "dataset_write_performed": safe_bool(
                    integration_row.get("dataset_write_performed"),
                ),
                "backup_created": safe_bool(
                    integration_row.get("backup_created"),
                ),
                "snapshot_created": safe_bool(
                    integration_row.get("snapshot_created"),
                ),
                "run_log_created_or_updated": safe_bool(
                    run_log_row.get("run_log_created_or_updated"),
                ),
                "total_logged_runs": safe_int(
                    run_log_row.get("total_logged_runs"),
                    0,
                ),
                "latest_run_id": safe_str(
                    run_log_row.get("latest_run_id"),
                    "",
                ),
                "paper_trade_execution_allowed": False,
                "real_capital_allowed": False,
                "live_alerts_allowed": False,
                "exchange_execution_allowed": False,
                "automation_allowed": False,
                "execution_allowed": False,
                "cycle_decision": cycle_decision,
                "cycle_validated": cycle_validated,
                "validation_decision": validation_decision,
            }
        ]
    )


def save_df(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)


def run_controlled_forward_evidence_cycle(
    config: ControlledForwardEvidenceCycleRunnerConfig | None = None,
) -> dict[str, pd.DataFrame]:
    active_config = config or ControlledForwardEvidenceCycleRunnerConfig()
    active_config.reports_dir.mkdir(parents=True, exist_ok=True)

    preflight_config = OperationalSafetyGuardPreflightConfig(
        require_clean_git=active_config.require_clean_git,
    )

    preflight_result = run_operational_safety_guard_preflight(
        config=preflight_config,
    )

    preflight_summary_df = preflight_result["summary"]

    preflight_row = first_row(preflight_summary_df)
    preflight_passed = safe_bool(preflight_row.get("preflight_passed", False))
    preflight_blockers = safe_int(preflight_row.get("blocker_count"), 0)

    command_rows = []

    if (
        active_config.stop_on_preflight_blocker
        and (not preflight_passed or preflight_blockers > 0)
    ):
        command_results_df = pd.DataFrame(command_rows)

        summary_df = build_summary_df(
            config=active_config,
            preflight_summary_df=preflight_summary_df,
            command_results_df=command_results_df,
        )

        save_df(
            summary_df,
            active_config.reports_dir / "controlled_cycle_summary_v1.csv",
        )
        save_df(
            command_results_df,
            active_config.reports_dir / "controlled_cycle_command_results_v1.csv",
        )

        return {
            "summary": summary_df,
            "command_results": command_results_df,
            "preflight_summary": preflight_summary_df,
        }

    for module_name in [
        active_config.bootstrap_module,
        active_config.input_validator_module,
        active_config.integration_module,
        active_config.run_log_module,
    ]:
        command_result = run_python_module(
            module_name=module_name,
            config=active_config,
        )
        command_rows.append(command_result)

        if not command_result["command_succeeded"]:
            break

    command_results_df = pd.DataFrame(command_rows)

    summary_df = build_summary_df(
        config=active_config,
        preflight_summary_df=preflight_summary_df,
        command_results_df=command_results_df,
    )

    save_df(
        summary_df,
        active_config.reports_dir / "controlled_cycle_summary_v1.csv",
    )
    save_df(
        command_results_df,
        active_config.reports_dir / "controlled_cycle_command_results_v1.csv",
    )
    save_df(
        preflight_summary_df,
        active_config.reports_dir / "controlled_cycle_preflight_summary_v1.csv",
    )

    return {
        "summary": summary_df,
        "command_results": command_results_df,
        "preflight_summary": preflight_summary_df,
    }