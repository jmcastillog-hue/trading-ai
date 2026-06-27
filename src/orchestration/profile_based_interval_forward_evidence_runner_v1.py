from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd

from src.orchestration.controlled_interval_forward_evidence_runner_v1 import (
    run_controlled_interval_forward_evidence_runner,
)
from src.orchestration.operational_interval_run_profiles_v1 import (
    OperationalIntervalRunProfile,
    build_operational_interval_profiles,
    profile_to_runner_config,
    validate_operational_interval_run_profiles,
)


EXECUTION_FLAG_COLUMNS = [
    "paper_trade_execution_allowed",
    "real_capital_allowed",
    "live_alerts_allowed",
    "exchange_execution_allowed",
    "automation_allowed",
    "execution_allowed",
]


VALID_PROFILE_DECISIONS = {
    "PROFILE_VALIDATED",
    "PROFILE_VALIDATED_WITH_WARNINGS",
}


@dataclass(frozen=True)
class ProfileBasedIntervalForwardEvidenceRunnerConfig:
    reports_dir: Path = Path("reports/profile_based_interval_forward_evidence_runner_v1")
    default_profile_name: str = "DEV_TEST"


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


def safe_float(value: Any, default: float = 0.0) -> float:
    try:
        if pd.isna(value):
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def safe_str(value: Any, default: str = "") -> str:
    if value is None:
        return default

    try:
        if pd.isna(value):
            return default
    except (TypeError, ValueError):
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


def normalize_profile_name(profile_name: str | None, default_profile_name: str) -> str:
    raw_name = profile_name or default_profile_name
    return raw_name.strip().upper()


def find_profile(
    profile_name: str,
    profiles: list[OperationalIntervalRunProfile],
) -> OperationalIntervalRunProfile | None:
    for profile in profiles:
        if profile.profile_name == profile_name:
            return profile

    return None


def filter_df_by_profile(
    df: pd.DataFrame,
    profile_name: str,
) -> pd.DataFrame:
    if df.empty or "profile_name" not in df.columns:
        return pd.DataFrame()

    return df[df["profile_name"] == profile_name].copy()


def build_non_executed_summary_df(
    profile_name_requested: str,
    normalized_profile_name: str,
    profile_found: bool,
    profile_decision: str,
    profile_readiness: str,
    profile_based_decision: str,
    validation_decision: str,
) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "profile_name_requested": profile_name_requested,
                "normalized_profile_name": normalized_profile_name,
                "profile_found": profile_found,
                "profile_decision": profile_decision,
                "profile_readiness": profile_readiness,
                "interval_executed": False,
                "cycles_completed": 0,
                "cycles_safe": 0,
                "cycles_failed": 0,
                "total_generated_observations": 0,
                "total_rejected_observations": 0,
                "total_closed_observations": 0,
                "total_open_observations": 0,
                "total_error_observations": 0,
                "total_new_rows_added": 0,
                "latest_total_logged_runs": 0,
                "latest_run_id": "",
                "interval_decision": "",
                "interval_validated": False,
                "paper_trade_execution_allowed": False,
                "real_capital_allowed": False,
                "live_alerts_allowed": False,
                "exchange_execution_allowed": False,
                "automation_allowed": False,
                "execution_allowed": False,
                "profile_based_decision": profile_based_decision,
                "profile_based_validated": False,
                "validation_decision": validation_decision,
            }
        ]
    )


def build_executed_summary_df(
    profile_name_requested: str,
    normalized_profile_name: str,
    profile_decision_row: dict[str, Any],
    interval_summary_row: dict[str, Any],
) -> pd.DataFrame:
    interval_execution_flags_ok = all_execution_flags_false(interval_summary_row)

    interval_validated = safe_bool(
        interval_summary_row.get("interval_validated"),
        False,
    )

    interval_decision = safe_str(
        interval_summary_row.get("interval_decision"),
        "",
    )

    profile_decision = safe_str(
        profile_decision_row.get("profile_decision"),
        "",
    )

    profile_based_validated = (
        profile_decision in VALID_PROFILE_DECISIONS
        and interval_validated
        and interval_execution_flags_ok
        and interval_decision == "CONTROLLED_INTERVAL_COMPLETED"
    )

    profile_based_decision = (
        "PROFILE_BASED_INTERVAL_RUN_COMPLETED"
        if profile_based_validated
        else "PROFILE_BASED_INTERVAL_RUN_FAILED"
    )

    validation_decision = (
        "PHASE_6_7_PROFILE_BASED_INTERVAL_RUNNER_VALIDATED"
        if profile_based_validated
        else "PHASE_6_7_PROFILE_BASED_INTERVAL_RUNNER_FAILED"
    )

    return pd.DataFrame(
        [
            {
                "profile_name_requested": profile_name_requested,
                "normalized_profile_name": normalized_profile_name,
                "profile_found": True,
                "profile_decision": profile_decision,
                "profile_readiness": safe_str(
                    profile_decision_row.get("profile_readiness"),
                    "",
                ),
                "profile_type": safe_str(
                    profile_decision_row.get("profile_type"),
                    "",
                ),
                "max_cycles": safe_int(
                    profile_decision_row.get("max_cycles"),
                    0,
                ),
                "interval_seconds": safe_int(
                    profile_decision_row.get("interval_seconds"),
                    0,
                ),
                "estimated_wait_seconds": safe_int(
                    profile_decision_row.get("estimated_wait_seconds"),
                    0,
                ),
                "estimated_wait_minutes": safe_float(
                    profile_decision_row.get("estimated_wait_minutes"),
                    0.0,
                ),
                "estimated_wait_hours": safe_float(
                    profile_decision_row.get("estimated_wait_hours"),
                    0.0,
                ),
                "require_clean_git": safe_bool(
                    profile_decision_row.get("require_clean_git"),
                    False,
                ),
                "interval_executed": True,
                "cycles_completed": safe_int(
                    interval_summary_row.get("cycles_completed"),
                    0,
                ),
                "cycles_safe": safe_int(
                    interval_summary_row.get("cycles_safe"),
                    0,
                ),
                "cycles_failed": safe_int(
                    interval_summary_row.get("cycles_failed"),
                    0,
                ),
                "total_generated_observations": safe_int(
                    interval_summary_row.get("total_generated_observations"),
                    0,
                ),
                "total_rejected_observations": safe_int(
                    interval_summary_row.get("total_rejected_observations"),
                    0,
                ),
                "total_closed_observations": safe_int(
                    interval_summary_row.get("total_closed_observations"),
                    0,
                ),
                "total_open_observations": safe_int(
                    interval_summary_row.get("total_open_observations"),
                    0,
                ),
                "total_error_observations": safe_int(
                    interval_summary_row.get("total_error_observations"),
                    0,
                ),
                "total_new_rows_added": safe_int(
                    interval_summary_row.get("total_new_rows_added"),
                    0,
                ),
                "latest_total_logged_runs": safe_int(
                    interval_summary_row.get("latest_total_logged_runs"),
                    0,
                ),
                "latest_run_id": safe_str(
                    interval_summary_row.get("latest_run_id"),
                    "",
                ),
                "interval_decision": interval_decision,
                "interval_validated": interval_validated,
                "paper_trade_execution_allowed": False,
                "real_capital_allowed": False,
                "live_alerts_allowed": False,
                "exchange_execution_allowed": False,
                "automation_allowed": False,
                "execution_allowed": False,
                "profile_based_decision": profile_based_decision,
                "profile_based_validated": profile_based_validated,
                "validation_decision": validation_decision,
            }
        ]
    )


def save_df(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)


def run_profile_based_interval_forward_evidence_runner(
    profile_name: str | None = None,
    config: ProfileBasedIntervalForwardEvidenceRunnerConfig | None = None,
) -> dict[str, pd.DataFrame]:
    active_config = config or ProfileBasedIntervalForwardEvidenceRunnerConfig()
    active_config.reports_dir.mkdir(parents=True, exist_ok=True)

    requested_profile_name = profile_name or active_config.default_profile_name
    normalized_profile_name = normalize_profile_name(
        profile_name=requested_profile_name,
        default_profile_name=active_config.default_profile_name,
    )

    profile_validation_result = validate_operational_interval_run_profiles()
    profiles = build_operational_interval_profiles()

    selected_profile = find_profile(
        profile_name=normalized_profile_name,
        profiles=profiles,
    )

    selected_profile_decision_df = filter_df_by_profile(
        df=profile_validation_result["decisions"],
        profile_name=normalized_profile_name,
    )

    selected_profile_registry_df = filter_df_by_profile(
        df=profile_validation_result["profiles"],
        profile_name=normalized_profile_name,
    )

    selected_profile_checks_df = filter_df_by_profile(
        df=profile_validation_result["checks"],
        profile_name=normalized_profile_name,
    )

    if selected_profile is None:
        summary_df = build_non_executed_summary_df(
            profile_name_requested=requested_profile_name,
            normalized_profile_name=normalized_profile_name,
            profile_found=False,
            profile_decision="",
            profile_readiness="",
            profile_based_decision="PROFILE_BASED_INTERVAL_PROFILE_NOT_FOUND",
            validation_decision="PHASE_6_7_PROFILE_BASED_INTERVAL_RUNNER_FAILED",
        )

        empty_interval_summary_df = pd.DataFrame()
        empty_cycle_records_df = pd.DataFrame()

    else:
        profile_decision_row = first_row(selected_profile_decision_df)
        profile_decision = safe_str(
            profile_decision_row.get("profile_decision"),
            "",
        )
        profile_readiness = safe_str(
            profile_decision_row.get("profile_readiness"),
            "",
        )

        if profile_decision not in VALID_PROFILE_DECISIONS:
            summary_df = build_non_executed_summary_df(
                profile_name_requested=requested_profile_name,
                normalized_profile_name=normalized_profile_name,
                profile_found=True,
                profile_decision=profile_decision,
                profile_readiness=profile_readiness,
                profile_based_decision="PROFILE_BASED_INTERVAL_PROFILE_BLOCKED",
                validation_decision="PHASE_6_7_PROFILE_BASED_INTERVAL_RUNNER_FAILED",
            )

            empty_interval_summary_df = pd.DataFrame()
            empty_cycle_records_df = pd.DataFrame()

        else:
            interval_reports_dir = (
                active_config.reports_dir
                / "interval_runner_outputs"
                / normalized_profile_name.lower()
            )

            runner_config = profile_to_runner_config(
                profile=selected_profile,
                reports_dir=interval_reports_dir,
            )

            interval_result = run_controlled_interval_forward_evidence_runner(
                config=runner_config,
            )

            empty_interval_summary_df = interval_result["summary"]
            empty_cycle_records_df = interval_result["cycle_records"]

            interval_summary_row = first_row(empty_interval_summary_df)

            summary_df = build_executed_summary_df(
                profile_name_requested=requested_profile_name,
                normalized_profile_name=normalized_profile_name,
                profile_decision_row=profile_decision_row,
                interval_summary_row=interval_summary_row,
            )

    save_df(
        summary_df,
        active_config.reports_dir / "profile_based_interval_summary_v1.csv",
    )
    save_df(
        selected_profile_decision_df,
        active_config.reports_dir / "profile_based_selected_profile_decision_v1.csv",
    )
    save_df(
        selected_profile_registry_df,
        active_config.reports_dir / "profile_based_selected_profile_registry_v1.csv",
    )
    save_df(
        selected_profile_checks_df,
        active_config.reports_dir / "profile_based_selected_profile_checks_v1.csv",
    )
    save_df(
        empty_interval_summary_df,
        active_config.reports_dir / "profile_based_interval_runner_summary_v1.csv",
    )
    save_df(
        empty_cycle_records_df,
        active_config.reports_dir / "profile_based_interval_cycle_records_v1.csv",
    )

    return {
        "summary": summary_df,
        "selected_profile_decision": selected_profile_decision_df,
        "selected_profile_registry": selected_profile_registry_df,
        "selected_profile_checks": selected_profile_checks_df,
        "interval_summary": empty_interval_summary_df,
        "cycle_records": empty_cycle_records_df,
    }