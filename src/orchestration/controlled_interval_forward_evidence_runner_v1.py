from __future__ import annotations

import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

from src.orchestration.controlled_forward_evidence_cycle_runner_v1 import (
    ControlledForwardEvidenceCycleRunnerConfig,
    run_controlled_forward_evidence_cycle,
)


EXECUTION_FLAG_COLUMNS = [
    "paper_trade_execution_allowed",
    "real_capital_allowed",
    "live_alerts_allowed",
    "exchange_execution_allowed",
    "automation_allowed",
    "execution_allowed",
]


SAFE_CYCLE_DECISIONS = {
    "CONTROLLED_CYCLE_COMPLETED_WITH_EVIDENCE",
    "CONTROLLED_CYCLE_COMPLETED_NO_DATASET_CHANGES",
    "CONTROLLED_CYCLE_WAITING_FOR_INPUTS",
}


@dataclass(frozen=True)
class ControlledIntervalForwardEvidenceRunnerConfig:
    max_cycles: int = 2
    interval_seconds: int = 5
    require_clean_git: bool = False
    stop_on_failed_cycle: bool = True
    stop_on_execution_flag: bool = True
    reports_dir: Path = Path("reports/controlled_interval_forward_evidence_runner_v1")


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


def safe_str(value: Any, default: str = "") -> str:
    if pd.isna(value):
        return default
    return str(value)


def first_row(df: pd.DataFrame) -> dict[str, Any]:
    if df.empty:
        return {}
    return df.iloc[0].to_dict()


def all_execution_flags_false(row: dict[str, Any]) -> bool:
    for column in EXECUTION_FLAG_COLUMNS:
        if safe_bool(row.get(column, False)):
            return False

    return True


def utc_now_text() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


def build_cycle_record(
    cycle_number: int,
    cycle_result: dict[str, pd.DataFrame],
) -> dict[str, Any]:
    summary_row = first_row(cycle_result.get("summary", pd.DataFrame()))

    execution_flags_ok = all_execution_flags_false(summary_row)

    cycle_decision = safe_str(
        summary_row.get("cycle_decision"),
        "UNKNOWN",
    )

    cycle_validated = safe_bool(
        summary_row.get("cycle_validated"),
        False,
    )

    cycle_safe = (
        execution_flags_ok
        and cycle_validated
        and cycle_decision in SAFE_CYCLE_DECISIONS
    )

    return {
        "cycle_number": cycle_number,
        "recorded_at_utc": utc_now_text(),
        "cycle_timestamp_utc": safe_str(
            summary_row.get("cycle_timestamp_utc"),
            "",
        ),
        "git_branch": safe_str(
            summary_row.get("git_branch"),
            "",
        ),
        "git_commit": safe_str(
            summary_row.get("git_commit"),
            "",
        ),
        "preflight_passed": safe_bool(
            summary_row.get("preflight_passed"),
        ),
        "preflight_decision": safe_str(
            summary_row.get("preflight_decision"),
            "",
        ),
        "commands_executed": safe_int(
            summary_row.get("commands_executed"),
            0,
        ),
        "commands_succeeded": safe_int(
            summary_row.get("commands_succeeded"),
            0,
        ),
        "commands_failed": safe_int(
            summary_row.get("commands_failed"),
            0,
        ),
        "adapter_decision": safe_str(
            summary_row.get("adapter_decision"),
            "",
        ),
        "integration_decision": safe_str(
            summary_row.get("integration_decision"),
            "",
        ),
        "generated_observations": safe_int(
            summary_row.get("generated_observations"),
            0,
        ),
        "rejected_observations": safe_int(
            summary_row.get("rejected_observations"),
            0,
        ),
        "closed_observations": safe_int(
            summary_row.get("closed_observations"),
            0,
        ),
        "open_observations": safe_int(
            summary_row.get("open_observations"),
            0,
        ),
        "error_observations": safe_int(
            summary_row.get("error_observations"),
            0,
        ),
        "new_rows_added": safe_int(
            summary_row.get("new_rows_added"),
            0,
        ),
        "duplicate_rows_skipped": safe_int(
            summary_row.get("duplicate_rows_skipped"),
            0,
        ),
        "dataset_rows_after": safe_int(
            summary_row.get("dataset_rows_after"),
            0,
        ),
        "run_log_created_or_updated": safe_bool(
            summary_row.get("run_log_created_or_updated"),
        ),
        "total_logged_runs": safe_int(
            summary_row.get("total_logged_runs"),
            0,
        ),
        "latest_run_id": safe_str(
            summary_row.get("latest_run_id"),
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
        "cycle_safe": cycle_safe,
    }


def classify_interval_decision(
    cycle_records_df: pd.DataFrame,
    config: ControlledIntervalForwardEvidenceRunnerConfig,
) -> str:
    if cycle_records_df.empty:
        return "CONTROLLED_INTERVAL_FAILED"

    any_execution_flag = False

    for _, row in cycle_records_df.iterrows():
        if not all_execution_flags_false(row.to_dict()):
            any_execution_flag = True
            break

    if any_execution_flag and config.stop_on_execution_flag:
        return "CONTROLLED_INTERVAL_STOPPED_ON_EXECUTION_FLAG"

    all_cycles_safe = bool(cycle_records_df["cycle_safe"].all())

    if not all_cycles_safe and config.stop_on_failed_cycle:
        return "CONTROLLED_INTERVAL_STOPPED_ON_FAILED_CYCLE"

    if all_cycles_safe:
        return "CONTROLLED_INTERVAL_COMPLETED"

    return "CONTROLLED_INTERVAL_FAILED"


def build_interval_summary_df(
    cycle_records_df: pd.DataFrame,
    config: ControlledIntervalForwardEvidenceRunnerConfig,
) -> pd.DataFrame:
    interval_decision = classify_interval_decision(
        cycle_records_df=cycle_records_df,
        config=config,
    )

    execution_flags_ok = True

    if not cycle_records_df.empty:
        for _, row in cycle_records_df.iterrows():
            if not all_execution_flags_false(row.to_dict()):
                execution_flags_ok = False
                break

    cycles_completed = int(len(cycle_records_df))
    cycles_safe = int(cycle_records_df["cycle_safe"].sum()) if not cycle_records_df.empty else 0
    cycles_failed = cycles_completed - cycles_safe

    interval_validated = (
        interval_decision == "CONTROLLED_INTERVAL_COMPLETED"
        and cycles_completed == config.max_cycles
        and cycles_failed == 0
        and execution_flags_ok
    )

    validation_decision = (
        "PHASE_6_5_CONTROLLED_INTERVAL_FORWARD_EVIDENCE_RUNNER_VALIDATED"
        if interval_validated
        else "PHASE_6_5_CONTROLLED_INTERVAL_FORWARD_EVIDENCE_RUNNER_FAILED"
    )

    return pd.DataFrame(
        [
            {
                "interval_timestamp_utc": utc_now_text(),
                "max_cycles": config.max_cycles,
                "interval_seconds": config.interval_seconds,
                "require_clean_git": config.require_clean_git,
                "stop_on_failed_cycle": config.stop_on_failed_cycle,
                "stop_on_execution_flag": config.stop_on_execution_flag,
                "cycles_completed": cycles_completed,
                "cycles_safe": cycles_safe,
                "cycles_failed": cycles_failed,
                "total_generated_observations": int(
                    cycle_records_df["generated_observations"].sum()
                )
                if not cycle_records_df.empty
                else 0,
                "total_rejected_observations": int(
                    cycle_records_df["rejected_observations"].sum()
                )
                if not cycle_records_df.empty
                else 0,
                "total_closed_observations": int(
                    cycle_records_df["closed_observations"].sum()
                )
                if not cycle_records_df.empty
                else 0,
                "total_open_observations": int(
                    cycle_records_df["open_observations"].sum()
                )
                if not cycle_records_df.empty
                else 0,
                "total_error_observations": int(
                    cycle_records_df["error_observations"].sum()
                )
                if not cycle_records_df.empty
                else 0,
                "total_new_rows_added": int(
                    cycle_records_df["new_rows_added"].sum()
                )
                if not cycle_records_df.empty
                else 0,
                "latest_total_logged_runs": int(
                    cycle_records_df["total_logged_runs"].iloc[-1]
                )
                if not cycle_records_df.empty
                else 0,
                "latest_run_id": str(
                    cycle_records_df["latest_run_id"].iloc[-1]
                )
                if not cycle_records_df.empty
                else "",
                "paper_trade_execution_allowed": False,
                "real_capital_allowed": False,
                "live_alerts_allowed": False,
                "exchange_execution_allowed": False,
                "automation_allowed": False,
                "execution_allowed": False,
                "interval_decision": interval_decision,
                "interval_validated": interval_validated,
                "validation_decision": validation_decision,
            }
        ]
    )


def save_df(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)


def run_controlled_interval_forward_evidence_runner(
    config: ControlledIntervalForwardEvidenceRunnerConfig | None = None,
) -> dict[str, pd.DataFrame]:
    active_config = config or ControlledIntervalForwardEvidenceRunnerConfig()
    active_config.reports_dir.mkdir(parents=True, exist_ok=True)

    cycle_records = []

    for cycle_number in range(1, active_config.max_cycles + 1):
        cycle_config = ControlledForwardEvidenceCycleRunnerConfig(
            require_clean_git=active_config.require_clean_git,
            stop_on_preflight_blocker=True,
        )

        cycle_result = run_controlled_forward_evidence_cycle(
            config=cycle_config,
        )

        cycle_record = build_cycle_record(
            cycle_number=cycle_number,
            cycle_result=cycle_result,
        )

        cycle_records.append(cycle_record)

        cycle_records_df = pd.DataFrame(cycle_records)

        if (
            active_config.stop_on_execution_flag
            and not all_execution_flags_false(cycle_record)
        ):
            break

        if (
            active_config.stop_on_failed_cycle
            and not bool(cycle_record["cycle_safe"])
        ):
            break

        if cycle_number < active_config.max_cycles:
            time.sleep(active_config.interval_seconds)

    cycle_records_df = pd.DataFrame(cycle_records)

    interval_summary_df = build_interval_summary_df(
        cycle_records_df=cycle_records_df,
        config=active_config,
    )

    save_df(
        interval_summary_df,
        active_config.reports_dir / "controlled_interval_summary_v1.csv",
    )
    save_df(
        cycle_records_df,
        active_config.reports_dir / "controlled_interval_cycle_records_v1.csv",
    )

    return {
        "summary": interval_summary_df,
        "cycle_records": cycle_records_df,
    }