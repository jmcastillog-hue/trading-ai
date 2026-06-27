from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import pandas as pd

from src.orchestration.controlled_interval_forward_evidence_runner_v1 import (
    ControlledIntervalForwardEvidenceRunnerConfig,
)


EXECUTION_FLAGS = {
    "paper_trade_execution_allowed": False,
    "real_capital_allowed": False,
    "live_alerts_allowed": False,
    "exchange_execution_allowed": False,
    "automation_allowed": False,
    "execution_allowed": False,
}


@dataclass(frozen=True)
class OperationalIntervalRunProfile:
    profile_name: str
    profile_type: str
    max_cycles: int
    interval_seconds: int
    require_clean_git: bool
    stop_on_failed_cycle: bool
    stop_on_execution_flag: bool
    purpose: str
    enabled: bool = True


@dataclass(frozen=True)
class OperationalIntervalRunProfilesConfig:
    reports_dir: Path = Path("reports/operational_interval_run_profiles_v1")
    max_allowed_cycles: int = 96
    max_allowed_duration_seconds: int = 86400
    min_allowed_interval_seconds: int = 5


def build_operational_interval_profiles() -> list[OperationalIntervalRunProfile]:
    return [
        OperationalIntervalRunProfile(
            profile_name="DEV_TEST",
            profile_type="DEVELOPMENT",
            max_cycles=2,
            interval_seconds=5,
            require_clean_git=False,
            stop_on_failed_cycle=True,
            stop_on_execution_flag=True,
            purpose="Development validation with two short cycles.",
        ),
        OperationalIntervalRunProfile(
            profile_name="SHORT_OBSERVATION",
            profile_type="OPERATIONAL",
            max_cycles=4,
            interval_seconds=60,
            require_clean_git=True,
            stop_on_failed_cycle=True,
            stop_on_execution_flag=True,
            purpose="Short controlled observation without execution.",
        ),
        OperationalIntervalRunProfile(
            profile_name="HALF_HOUR_MONITOR",
            profile_type="OPERATIONAL",
            max_cycles=2,
            interval_seconds=900,
            require_clean_git=True,
            stop_on_failed_cycle=True,
            stop_on_execution_flag=True,
            purpose="Short market monitor using 15-minute spacing.",
        ),
        OperationalIntervalRunProfile(
            profile_name="TWO_HOUR_MONITOR",
            profile_type="OPERATIONAL",
            max_cycles=8,
            interval_seconds=900,
            require_clean_git=True,
            stop_on_failed_cycle=True,
            stop_on_execution_flag=True,
            purpose="Controlled two-hour observation profile.",
        ),
        OperationalIntervalRunProfile(
            profile_name="DAILY_OBSERVATION",
            profile_type="OPERATIONAL",
            max_cycles=48,
            interval_seconds=1800,
            require_clean_git=True,
            stop_on_failed_cycle=True,
            stop_on_execution_flag=True,
            purpose="Controlled daily observation profile.",
        ),
    ]


def estimated_wait_seconds(profile: OperationalIntervalRunProfile) -> int:
    if profile.max_cycles <= 1:
        return 0

    return int((profile.max_cycles - 1) * profile.interval_seconds)


def profile_to_runner_config(
    profile: OperationalIntervalRunProfile,
    reports_dir: Path | None = None,
) -> ControlledIntervalForwardEvidenceRunnerConfig:
    return ControlledIntervalForwardEvidenceRunnerConfig(
        max_cycles=profile.max_cycles,
        interval_seconds=profile.interval_seconds,
        require_clean_git=profile.require_clean_git,
        stop_on_failed_cycle=profile.stop_on_failed_cycle,
        stop_on_execution_flag=profile.stop_on_execution_flag,
        reports_dir=reports_dir
        if reports_dir is not None
        else Path("reports/controlled_interval_forward_evidence_runner_v1"),
    )


def build_check(
    profile_name: str,
    check_name: str,
    passed: bool,
    severity: str,
    details: str,
    blocker: bool,
) -> dict[str, Any]:
    return {
        "profile_name": profile_name,
        "check_name": check_name,
        "passed": passed,
        "severity": severity,
        "details": details,
        "blocker": blocker,
    }


def validate_profile(
    profile: OperationalIntervalRunProfile,
    config: OperationalIntervalRunProfilesConfig,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []

    profile_name_valid = (
        bool(profile.profile_name)
        and profile.profile_name.upper() == profile.profile_name
        and " " not in profile.profile_name
    )

    rows.append(
        build_check(
            profile_name=profile.profile_name,
            check_name="profile_name_valid",
            passed=profile_name_valid,
            severity="INFO" if profile_name_valid else "ERROR",
            details=profile.profile_name,
            blocker=not profile_name_valid,
        )
    )

    profile_type_valid = profile.profile_type in {"DEVELOPMENT", "OPERATIONAL"}

    rows.append(
        build_check(
            profile_name=profile.profile_name,
            check_name="profile_type_valid",
            passed=profile_type_valid,
            severity="INFO" if profile_type_valid else "ERROR",
            details=profile.profile_type,
            blocker=not profile_type_valid,
        )
    )

    max_cycles_valid = (
        profile.max_cycles > 0
        and profile.max_cycles <= config.max_allowed_cycles
    )

    rows.append(
        build_check(
            profile_name=profile.profile_name,
            check_name="max_cycles_within_bounds",
            passed=max_cycles_valid,
            severity="INFO" if max_cycles_valid else "ERROR",
            details=f"max_cycles={profile.max_cycles}",
            blocker=not max_cycles_valid,
        )
    )

    interval_valid = profile.interval_seconds >= config.min_allowed_interval_seconds

    rows.append(
        build_check(
            profile_name=profile.profile_name,
            check_name="interval_seconds_within_bounds",
            passed=interval_valid,
            severity="INFO" if interval_valid else "ERROR",
            details=f"interval_seconds={profile.interval_seconds}",
            blocker=not interval_valid,
        )
    )

    duration_seconds = estimated_wait_seconds(profile)

    duration_valid = duration_seconds <= config.max_allowed_duration_seconds

    rows.append(
        build_check(
            profile_name=profile.profile_name,
            check_name="estimated_duration_within_bounds",
            passed=duration_valid,
            severity="INFO" if duration_valid else "ERROR",
            details=f"estimated_wait_seconds={duration_seconds}",
            blocker=not duration_valid,
        )
    )

    if profile.profile_type == "OPERATIONAL":
        clean_git_valid = profile.require_clean_git
        rows.append(
            build_check(
                profile_name=profile.profile_name,
                check_name="operational_profile_requires_clean_git",
                passed=clean_git_valid,
                severity="INFO" if clean_git_valid else "ERROR",
                details=f"require_clean_git={profile.require_clean_git}",
                blocker=not clean_git_valid,
            )
        )
    else:
        rows.append(
            build_check(
                profile_name=profile.profile_name,
                check_name="development_profile_clean_git_exception",
                passed=True,
                severity="WARNING",
                details="Development profile may use require_clean_git=False.",
                blocker=False,
            )
        )

    stop_on_failed_valid = profile.stop_on_failed_cycle is True
    rows.append(
        build_check(
            profile_name=profile.profile_name,
            check_name="stop_on_failed_cycle_enabled",
            passed=stop_on_failed_valid,
            severity="INFO" if stop_on_failed_valid else "ERROR",
            details=f"stop_on_failed_cycle={profile.stop_on_failed_cycle}",
            blocker=not stop_on_failed_valid,
        )
    )

    stop_on_flag_valid = profile.stop_on_execution_flag is True
    rows.append(
        build_check(
            profile_name=profile.profile_name,
            check_name="stop_on_execution_flag_enabled",
            passed=stop_on_flag_valid,
            severity="INFO" if stop_on_flag_valid else "ERROR",
            details=f"stop_on_execution_flag={profile.stop_on_execution_flag}",
            blocker=not stop_on_flag_valid,
        )
    )

    for flag_name, flag_value in EXECUTION_FLAGS.items():
        flag_valid = flag_value is False
        rows.append(
            build_check(
                profile_name=profile.profile_name,
                check_name=f"execution_flag_false:{flag_name}",
                passed=flag_valid,
                severity="INFO" if flag_valid else "ERROR",
                details=f"{flag_name}={flag_value}",
                blocker=not flag_valid,
            )
        )

    return rows


def build_profiles_df(
    profiles: list[OperationalIntervalRunProfile],
) -> pd.DataFrame:
    rows = []

    for profile in profiles:
        row = asdict(profile)
        row["estimated_wait_seconds"] = estimated_wait_seconds(profile)
        row["estimated_wait_minutes"] = round(
            row["estimated_wait_seconds"] / 60,
            2,
        )
        row["estimated_wait_hours"] = round(
            row["estimated_wait_seconds"] / 3600,
            2,
        )

        runner_config = profile_to_runner_config(profile)

        row["runner_max_cycles"] = runner_config.max_cycles
        row["runner_interval_seconds"] = runner_config.interval_seconds
        row["runner_require_clean_git"] = runner_config.require_clean_git
        row["runner_stop_on_failed_cycle"] = runner_config.stop_on_failed_cycle
        row["runner_stop_on_execution_flag"] = runner_config.stop_on_execution_flag

        for flag_name, flag_value in EXECUTION_FLAGS.items():
            row[flag_name] = flag_value

        rows.append(row)

    return pd.DataFrame(rows)


def build_validation_checks_df(
    profiles: list[OperationalIntervalRunProfile],
    config: OperationalIntervalRunProfilesConfig,
) -> pd.DataFrame:
    rows = []

    for profile in profiles:
        rows.extend(
            validate_profile(
                profile=profile,
                config=config,
            )
        )

    return pd.DataFrame(rows)


def build_profile_decisions_df(
    profiles_df: pd.DataFrame,
    checks_df: pd.DataFrame,
) -> pd.DataFrame:
    rows = []

    for _, profile_row in profiles_df.iterrows():
        profile_name = profile_row["profile_name"]
        profile_checks = checks_df[checks_df["profile_name"] == profile_name]

        blocker_count = int(profile_checks["blocker"].astype(bool).sum())
        warning_count = int(profile_checks["severity"].eq("WARNING").sum())
        error_count = int(profile_checks["severity"].eq("ERROR").sum())

        if blocker_count > 0:
            profile_decision = "PROFILE_BLOCKED"
            readiness = "BLOCKED"
        elif warning_count > 0:
            profile_decision = "PROFILE_VALIDATED_WITH_WARNINGS"
            readiness = (
                "DEV_ONLY"
                if profile_row["profile_type"] == "DEVELOPMENT"
                else "OPERATIONAL_READY_WITH_WARNINGS"
            )
        else:
            profile_decision = "PROFILE_VALIDATED"
            readiness = (
                "DEV_ONLY"
                if profile_row["profile_type"] == "DEVELOPMENT"
                else "OPERATIONAL_READY"
            )

        rows.append(
            {
                "profile_name": profile_name,
                "profile_type": profile_row["profile_type"],
                "max_cycles": int(profile_row["max_cycles"]),
                "interval_seconds": int(profile_row["interval_seconds"]),
                "estimated_wait_seconds": int(profile_row["estimated_wait_seconds"]),
                "estimated_wait_minutes": float(profile_row["estimated_wait_minutes"]),
                "estimated_wait_hours": float(profile_row["estimated_wait_hours"]),
                "require_clean_git": bool(profile_row["require_clean_git"]),
                "blocker_count": blocker_count,
                "warning_count": warning_count,
                "error_count": error_count,
                "profile_decision": profile_decision,
                "profile_readiness": readiness,
                "paper_trade_execution_allowed": False,
                "real_capital_allowed": False,
                "live_alerts_allowed": False,
                "exchange_execution_allowed": False,
                "automation_allowed": False,
                "execution_allowed": False,
            }
        )

    return pd.DataFrame(rows)


def build_summary_df(
    profiles_df: pd.DataFrame,
    checks_df: pd.DataFrame,
    decisions_df: pd.DataFrame,
) -> pd.DataFrame:
    total_profiles = len(profiles_df)
    blocked_profiles = int(decisions_df["profile_decision"].eq("PROFILE_BLOCKED").sum())
    dev_only_profiles = int(decisions_df["profile_readiness"].eq("DEV_ONLY").sum())
    operational_ready_profiles = int(
        decisions_df["profile_readiness"].isin(
            [
                "OPERATIONAL_READY",
                "OPERATIONAL_READY_WITH_WARNINGS",
            ]
        ).sum()
    )

    warning_count = int(checks_df["severity"].eq("WARNING").sum())
    error_count = int(checks_df["severity"].eq("ERROR").sum())
    blocker_count = int(checks_df["blocker"].astype(bool).sum())

    validation_passed = blocked_profiles == 0 and blocker_count == 0

    validation_decision = (
        "PHASE_6_6_OPERATIONAL_INTERVAL_RUN_PROFILES_VALIDATED"
        if validation_passed
        else "PHASE_6_6_OPERATIONAL_INTERVAL_RUN_PROFILES_FAILED"
    )

    return pd.DataFrame(
        [
            {
                "total_profiles": total_profiles,
                "dev_only_profiles": dev_only_profiles,
                "operational_ready_profiles": operational_ready_profiles,
                "blocked_profiles": blocked_profiles,
                "total_checks": len(checks_df),
                "warning_count": warning_count,
                "error_count": error_count,
                "blocker_count": blocker_count,
                "max_profile_wait_seconds": int(
                    decisions_df["estimated_wait_seconds"].max()
                )
                if not decisions_df.empty
                else 0,
                "max_profile_wait_hours": float(
                    decisions_df["estimated_wait_hours"].max()
                )
                if not decisions_df.empty
                else 0.0,
                "paper_trade_execution_allowed": False,
                "real_capital_allowed": False,
                "live_alerts_allowed": False,
                "exchange_execution_allowed": False,
                "automation_allowed": False,
                "execution_allowed": False,
                "validation_passed": validation_passed,
                "validation_decision": validation_decision,
            }
        ]
    )


def save_df(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)


def validate_operational_interval_run_profiles(
    config: OperationalIntervalRunProfilesConfig | None = None,
) -> dict[str, pd.DataFrame]:
    active_config = config or OperationalIntervalRunProfilesConfig()
    active_config.reports_dir.mkdir(parents=True, exist_ok=True)

    profiles = build_operational_interval_profiles()

    profiles_df = build_profiles_df(profiles)
    checks_df = build_validation_checks_df(
        profiles=profiles,
        config=active_config,
    )
    decisions_df = build_profile_decisions_df(
        profiles_df=profiles_df,
        checks_df=checks_df,
    )
    summary_df = build_summary_df(
        profiles_df=profiles_df,
        checks_df=checks_df,
        decisions_df=decisions_df,
    )

    save_df(
        summary_df,
        active_config.reports_dir / "operational_interval_profiles_summary_v1.csv",
    )
    save_df(
        profiles_df,
        active_config.reports_dir / "operational_interval_profiles_registry_v1.csv",
    )
    save_df(
        checks_df,
        active_config.reports_dir / "operational_interval_profiles_checks_v1.csv",
    )
    save_df(
        decisions_df,
        active_config.reports_dir / "operational_interval_profiles_decisions_v1.csv",
    )

    return {
        "summary": summary_df,
        "profiles": profiles_df,
        "checks": checks_df,
        "decisions": decisions_df,
    }