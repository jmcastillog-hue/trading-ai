from __future__ import annotations

import hashlib
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


EXECUTION_FLAG_COLUMNS = [
    "paper_trade_execution_allowed",
    "real_capital_allowed",
    "live_alerts_allowed",
    "exchange_execution_allowed",
    "automation_allowed",
    "execution_allowed",
]


DEFAULT_LOG_COLUMNS = [
    "run_id",
    "run_timestamp_utc",
    "git_branch",
    "git_commit",
    "integration_report_exists",
    "adapter_decision",
    "integration_decision",
    "input_ready_for_cycle",
    "signal_files_found",
    "ohlc_files_found",
    "price_level_files_found",
    "adapted_signal_rows",
    "adapted_ohlc_rows",
    "adapted_price_level_rows",
    "generated_observations",
    "rejected_observations",
    "closed_observations",
    "open_observations",
    "error_observations",
    "wins",
    "losses",
    "new_rows_added",
    "updated_rows",
    "duplicate_rows_skipped",
    "invalid_rows",
    "dataset_rows_after",
    "dataset_write_required",
    "dataset_write_performed",
    "backup_created",
    "snapshot_created",
    "paper_trade_execution_allowed",
    "real_capital_allowed",
    "live_alerts_allowed",
    "exchange_execution_allowed",
    "automation_allowed",
    "execution_allowed",
    "run_log_decision",
    "validation_decision",
    "notes",
]


@dataclass(frozen=True)
class ForwardEvidenceRunLogConfig:
    integration_summary_path: Path = Path(
        "reports/operational_persistent_cycle_integration_v1/"
        "operational_integration_summary_v1.csv"
    )
    run_log_path: Path = Path(
        "data/forward_evidence/operational/run_logs/"
        "forward_evidence_run_log_v1.csv"
    )
    reports_dir: Path = Path("reports/forward_evidence_run_log_v1")


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


def empty_log_df() -> pd.DataFrame:
    return pd.DataFrame(columns=DEFAULT_LOG_COLUMNS)


def normalize_log_df(df: pd.DataFrame) -> pd.DataFrame:
    working = df.copy()

    for column in DEFAULT_LOG_COLUMNS:
        if column not in working.columns:
            working[column] = ""

    return working[DEFAULT_LOG_COLUMNS].copy()


def read_csv_or_empty(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()

    try:
        return pd.read_csv(path)
    except Exception:
        return pd.DataFrame()


def get_first_row(df: pd.DataFrame) -> dict[str, Any]:
    if df.empty:
        return {}
    return df.iloc[0].to_dict()


def build_run_id(timestamp_utc: str, git_commit: str, integration_decision: str) -> str:
    raw = f"{timestamp_utc}|{git_commit}|{integration_decision}"
    digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]
    return f"RUNLOG_{digest}"


def all_execution_flags_false(row: dict[str, Any]) -> bool:
    return all(not safe_bool(row.get(column, False)) for column in EXECUTION_FLAG_COLUMNS)


def build_log_row(config: ForwardEvidenceRunLogConfig) -> dict[str, Any]:
    timestamp_utc = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    git_branch = get_git_branch()
    git_commit = get_git_commit()

    integration_df = read_csv_or_empty(config.integration_summary_path)
    integration_report_exists = not integration_df.empty
    source_row = get_first_row(integration_df)

    adapter_decision = safe_str(
        source_row.get("adapter_decision"),
        "NO_INTEGRATION_REPORT",
    )
    integration_decision = safe_str(
        source_row.get("integration_decision"),
        "NO_INTEGRATION_REPORT",
    )

    base_row: dict[str, Any] = {
        "run_timestamp_utc": timestamp_utc,
        "git_branch": git_branch,
        "git_commit": git_commit,
        "integration_report_exists": integration_report_exists,
        "adapter_decision": adapter_decision,
        "integration_decision": integration_decision,
        "input_ready_for_cycle": safe_bool(source_row.get("input_ready_for_cycle")),
        "signal_files_found": safe_int(source_row.get("signal_files_found")),
        "ohlc_files_found": safe_int(source_row.get("ohlc_files_found")),
        "price_level_files_found": safe_int(source_row.get("price_level_files_found")),
        "adapted_signal_rows": safe_int(source_row.get("adapted_signal_rows")),
        "adapted_ohlc_rows": safe_int(source_row.get("adapted_ohlc_rows")),
        "adapted_price_level_rows": safe_int(
            source_row.get("adapted_price_level_rows")
        ),
        "generated_observations": safe_int(source_row.get("generated_observations")),
        "rejected_observations": safe_int(source_row.get("rejected_observations")),
        "closed_observations": safe_int(source_row.get("closed_observations")),
        "open_observations": safe_int(source_row.get("open_observations")),
        "error_observations": safe_int(source_row.get("error_observations")),
        "wins": safe_int(source_row.get("wins")),
        "losses": safe_int(source_row.get("losses")),
        "new_rows_added": safe_int(source_row.get("new_rows_added")),
        "updated_rows": safe_int(source_row.get("updated_rows")),
        "duplicate_rows_skipped": safe_int(source_row.get("duplicate_rows_skipped")),
        "invalid_rows": safe_int(source_row.get("invalid_rows")),
        "dataset_rows_after": safe_int(source_row.get("dataset_rows_after")),
        "dataset_write_required": safe_bool(source_row.get("dataset_write_required")),
        "dataset_write_performed": safe_bool(source_row.get("dataset_write_performed")),
        "backup_created": safe_bool(source_row.get("backup_created")),
        "snapshot_created": safe_bool(source_row.get("snapshot_created")),
        "paper_trade_execution_allowed": False,
        "real_capital_allowed": False,
        "live_alerts_allowed": False,
        "exchange_execution_allowed": False,
        "automation_allowed": False,
        "execution_allowed": False,
    }

    execution_flags_ok = all_execution_flags_false(base_row)

    if not execution_flags_ok:
        run_log_decision = "RUN_LOG_FAILED_EXECUTION_FLAGS_ENABLED"
        validation_decision = "PHASE_6_2_FORWARD_EVIDENCE_RUN_LOG_FAILED"
    elif integration_report_exists:
        run_log_decision = "RUN_LOG_COMPLETED_WITH_INTEGRATION_REPORT"
        validation_decision = "PHASE_6_2_FORWARD_EVIDENCE_RUN_LOG_VALIDATED"
    else:
        run_log_decision = "RUN_LOG_COMPLETED_WITHOUT_INTEGRATION_REPORT"
        validation_decision = "PHASE_6_2_FORWARD_EVIDENCE_RUN_LOG_VALIDATED"

    run_id = build_run_id(
        timestamp_utc=timestamp_utc,
        git_commit=git_commit,
        integration_decision=integration_decision,
    )

    base_row.update(
        {
            "run_id": run_id,
            "run_log_decision": run_log_decision,
            "validation_decision": validation_decision,
            "notes": (
                "Run log generated from latest operational integration summary."
                if integration_report_exists
                else "Run log generated without available integration summary."
            ),
        }
    )

    return base_row


def append_run_log(
    existing_log_df: pd.DataFrame,
    new_row: dict[str, Any],
) -> pd.DataFrame:
    normalized_existing = normalize_log_df(existing_log_df)

    new_row_df = normalize_log_df(pd.DataFrame([new_row]))

    combined = pd.concat(
        [normalized_existing, new_row_df],
        ignore_index=True,
    )

    return normalize_log_df(combined)


def build_summary_df(run_log_df: pd.DataFrame, new_row: dict[str, Any]) -> pd.DataFrame:
    total_runs = len(run_log_df)

    validation_passed = (
        new_row.get("validation_decision")
        == "PHASE_6_2_FORWARD_EVIDENCE_RUN_LOG_VALIDATED"
        and all_execution_flags_false(new_row)
    )

    return pd.DataFrame(
        [
            {
                "run_log_created_or_updated": True,
                "run_log_path": str(
                    ForwardEvidenceRunLogConfig().run_log_path
                ),
                "total_logged_runs": total_runs,
                "latest_run_id": new_row.get("run_id"),
                "latest_git_branch": new_row.get("git_branch"),
                "latest_git_commit": new_row.get("git_commit"),
                "integration_report_exists": new_row.get("integration_report_exists"),
                "adapter_decision": new_row.get("adapter_decision"),
                "integration_decision": new_row.get("integration_decision"),
                "generated_observations": new_row.get("generated_observations"),
                "closed_observations": new_row.get("closed_observations"),
                "open_observations": new_row.get("open_observations"),
                "new_rows_added": new_row.get("new_rows_added"),
                "duplicate_rows_skipped": new_row.get("duplicate_rows_skipped"),
                "dataset_rows_after": new_row.get("dataset_rows_after"),
                "paper_trade_execution_allowed": False,
                "real_capital_allowed": False,
                "live_alerts_allowed": False,
                "exchange_execution_allowed": False,
                "automation_allowed": False,
                "execution_allowed": False,
                "validation_passed": validation_passed,
                "validation_decision": new_row.get("validation_decision"),
            }
        ]
    )


def save_df(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)


def run_forward_evidence_run_log(
    config: ForwardEvidenceRunLogConfig | None = None,
) -> dict[str, pd.DataFrame]:
    active_config = config or ForwardEvidenceRunLogConfig()

    existing_log_df = read_csv_or_empty(active_config.run_log_path)
    if existing_log_df.empty:
        existing_log_df = empty_log_df()

    new_row = build_log_row(active_config)

    updated_log_df = append_run_log(
        existing_log_df=existing_log_df,
        new_row=new_row,
    )

    summary_df = build_summary_df(
        run_log_df=updated_log_df,
        new_row=new_row,
    )

    save_df(updated_log_df, active_config.run_log_path)

    active_config.reports_dir.mkdir(parents=True, exist_ok=True)

    save_df(
        summary_df,
        active_config.reports_dir / "forward_evidence_run_log_summary_v1.csv",
    )
    save_df(
        pd.DataFrame([new_row]),
        active_config.reports_dir / "forward_evidence_latest_run_log_entry_v1.csv",
    )
    save_df(
        updated_log_df.tail(20),
        active_config.reports_dir / "forward_evidence_run_log_tail_v1.csv",
    )

    return {
        "summary": summary_df,
        "latest_entry": pd.DataFrame([new_row]),
        "run_log_tail": updated_log_df.tail(20),
    }