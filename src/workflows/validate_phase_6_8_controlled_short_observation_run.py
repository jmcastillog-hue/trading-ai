from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd


PROFILE_BASED_SUMMARY_PATH = Path(
    "reports/profile_based_interval_forward_evidence_runner_v1/"
    "profile_based_interval_summary_v1.csv"
)
INTERVAL_SUMMARY_PATH = Path(
    "reports/profile_based_interval_forward_evidence_runner_v1/"
    "profile_based_interval_runner_summary_v1.csv"
)
CYCLE_RECORDS_PATH = Path(
    "reports/profile_based_interval_forward_evidence_runner_v1/"
    "profile_based_interval_cycle_records_v1.csv"
)
REPORTS_DIR = Path("reports/phase_6_8_controlled_short_observation_run_v1")


EXECUTION_FLAG_COLUMNS = [
    "paper_trade_execution_allowed",
    "real_capital_allowed",
    "live_alerts_allowed",
    "exchange_execution_allowed",
    "automation_allowed",
    "execution_allowed",
]


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
    if value is None:
        return default

    try:
        if pd.isna(value):
            return default
    except (TypeError, ValueError):
        return default

    return str(value)


def read_csv_if_exists(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()

    return pd.read_csv(path)


def first_row(df: pd.DataFrame) -> dict[str, Any]:
    if df.empty:
        return {}

    return df.iloc[0].to_dict()


def all_execution_flags_false(row: dict[str, Any]) -> bool:
    for column in EXECUTION_FLAG_COLUMNS:
        if safe_bool(row.get(column, False)):
            return False

    return True


def build_check(
    check_name: str,
    passed: bool,
    severity: str,
    details: str,
) -> dict[str, Any]:
    return {
        "check_name": check_name,
        "passed": passed,
        "severity": severity,
        "details": details,
        "blocker": severity == "ERROR" and not passed,
    }


def validate_phase_6_8_controlled_short_observation_run() -> dict[str, pd.DataFrame]:
    profile_summary_df = read_csv_if_exists(PROFILE_BASED_SUMMARY_PATH)
    interval_summary_df = read_csv_if_exists(INTERVAL_SUMMARY_PATH)
    cycle_records_df = read_csv_if_exists(CYCLE_RECORDS_PATH)

    profile_row = first_row(profile_summary_df)
    interval_row = first_row(interval_summary_df)

    checks = []

    checks.append(
        build_check(
            check_name="profile_summary_exists",
            passed=not profile_summary_df.empty,
            severity="INFO" if not profile_summary_df.empty else "ERROR",
            details=str(PROFILE_BASED_SUMMARY_PATH),
        )
    )
    checks.append(
        build_check(
            check_name="interval_summary_exists",
            passed=not interval_summary_df.empty,
            severity="INFO" if not interval_summary_df.empty else "ERROR",
            details=str(INTERVAL_SUMMARY_PATH),
        )
    )
    checks.append(
        build_check(
            check_name="cycle_records_exist",
            passed=not cycle_records_df.empty,
            severity="INFO" if not cycle_records_df.empty else "ERROR",
            details=str(CYCLE_RECORDS_PATH),
        )
    )

    checks.append(
        build_check(
            check_name="selected_profile_is_short_observation",
            passed=safe_str(profile_row.get("normalized_profile_name")) == "SHORT_OBSERVATION",
            severity="INFO"
            if safe_str(profile_row.get("normalized_profile_name")) == "SHORT_OBSERVATION"
            else "ERROR",
            details=safe_str(profile_row.get("normalized_profile_name")),
        )
    )

    checks.append(
        build_check(
            check_name="profile_is_operational_ready",
            passed=safe_str(profile_row.get("profile_readiness")) == "OPERATIONAL_READY",
            severity="INFO"
            if safe_str(profile_row.get("profile_readiness")) == "OPERATIONAL_READY"
            else "ERROR",
            details=safe_str(profile_row.get("profile_readiness")),
        )
    )

    checks.append(
        build_check(
            check_name="profile_requires_clean_git",
            passed=safe_bool(profile_row.get("require_clean_git")) is True,
            severity="INFO" if safe_bool(profile_row.get("require_clean_git")) is True else "ERROR",
            details=f"require_clean_git={safe_bool(profile_row.get('require_clean_git'))}",
        )
    )

    checks.append(
        build_check(
            check_name="cycles_completed_is_4",
            passed=safe_int(profile_row.get("cycles_completed")) == 4,
            severity="INFO" if safe_int(profile_row.get("cycles_completed")) == 4 else "ERROR",
            details=f"cycles_completed={safe_int(profile_row.get('cycles_completed'))}",
        )
    )

    checks.append(
        build_check(
            check_name="cycles_safe_is_4",
            passed=safe_int(profile_row.get("cycles_safe")) == 4,
            severity="INFO" if safe_int(profile_row.get("cycles_safe")) == 4 else "ERROR",
            details=f"cycles_safe={safe_int(profile_row.get('cycles_safe'))}",
        )
    )

    checks.append(
        build_check(
            check_name="cycles_failed_is_0",
            passed=safe_int(profile_row.get("cycles_failed")) == 0,
            severity="INFO" if safe_int(profile_row.get("cycles_failed")) == 0 else "ERROR",
            details=f"cycles_failed={safe_int(profile_row.get('cycles_failed'))}",
        )
    )

    checks.append(
        build_check(
            check_name="interval_completed",
            passed=safe_str(profile_row.get("interval_decision")) == "CONTROLLED_INTERVAL_COMPLETED",
            severity="INFO"
            if safe_str(profile_row.get("interval_decision")) == "CONTROLLED_INTERVAL_COMPLETED"
            else "ERROR",
            details=safe_str(profile_row.get("interval_decision")),
        )
    )

    checks.append(
        build_check(
            check_name="profile_based_validated",
            passed=safe_bool(profile_row.get("profile_based_validated")) is True,
            severity="INFO"
            if safe_bool(profile_row.get("profile_based_validated")) is True
            else "ERROR",
            details=f"profile_based_validated={safe_bool(profile_row.get('profile_based_validated'))}",
        )
    )

    checks.append(
        build_check(
            check_name="interval_validated",
            passed=safe_bool(interval_row.get("interval_validated")) is True,
            severity="INFO"
            if safe_bool(interval_row.get("interval_validated")) is True
            else "ERROR",
            details=f"interval_validated={safe_bool(interval_row.get('interval_validated'))}",
        )
    )

    checks.append(
        build_check(
            check_name="cycle_records_count_is_4",
            passed=len(cycle_records_df) == 4,
            severity="INFO" if len(cycle_records_df) == 4 else "ERROR",
            details=f"cycle_records={len(cycle_records_df)}",
        )
    )

    if not cycle_records_df.empty and "cycle_safe" in cycle_records_df.columns:
        cycle_safe_count = int(cycle_records_df["cycle_safe"].astype(bool).sum())
    else:
        cycle_safe_count = 0

    checks.append(
        build_check(
            check_name="all_cycle_records_safe",
            passed=cycle_safe_count == 4,
            severity="INFO" if cycle_safe_count == 4 else "ERROR",
            details=f"cycle_safe_count={cycle_safe_count}",
        )
    )

    if not cycle_records_df.empty and "preflight_decision" in cycle_records_df.columns:
        clean_preflight_count = int(
            cycle_records_df["preflight_decision"]
            .astype(str)
            .eq("OPERATIONAL_PREFLIGHT_VALIDATED")
            .sum()
        )
    else:
        clean_preflight_count = 0

    checks.append(
        build_check(
            check_name="all_preflights_cleanly_validated",
            passed=clean_preflight_count == 4,
            severity="INFO" if clean_preflight_count == 4 else "ERROR",
            details=f"clean_preflight_count={clean_preflight_count}",
        )
    )

    checks.append(
        build_check(
            check_name="profile_execution_flags_false",
            passed=all_execution_flags_false(profile_row),
            severity="INFO" if all_execution_flags_false(profile_row) else "ERROR",
            details="profile-based summary execution flags must remain false",
        )
    )

    checks.append(
        build_check(
            check_name="interval_execution_flags_false",
            passed=all_execution_flags_false(interval_row),
            severity="INFO" if all_execution_flags_false(interval_row) else "ERROR",
            details="interval summary execution flags must remain false",
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
                "phase": "6.8",
                "profile_name": safe_str(profile_row.get("normalized_profile_name")),
                "profile_readiness": safe_str(profile_row.get("profile_readiness")),
                "cycles_completed": safe_int(profile_row.get("cycles_completed")),
                "cycles_safe": safe_int(profile_row.get("cycles_safe")),
                "cycles_failed": safe_int(profile_row.get("cycles_failed")),
                "clean_preflight_count": clean_preflight_count,
                "latest_run_id": safe_str(profile_row.get("latest_run_id")),
                "total_checks": len(checks_df),
                "warning_count": warning_count,
                "error_count": error_count,
                "blocker_count": blocker_count,
                "paper_trade_execution_allowed": False,
                "real_capital_allowed": False,
                "live_alerts_allowed": False,
                "exchange_execution_allowed": False,
                "automation_allowed": False,
                "execution_allowed": False,
                "validation_passed": validation_passed,
                "validation_decision": (
                    "PHASE_6_8_CONTROLLED_SHORT_OBSERVATION_RUN_VALIDATED"
                    if validation_passed
                    else "PHASE_6_8_CONTROLLED_SHORT_OBSERVATION_RUN_FAILED"
                ),
            }
        ]
    )

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    summary_df.to_csv(
        REPORTS_DIR / "phase_6_8_controlled_short_observation_summary_v1.csv",
        index=False,
    )
    checks_df.to_csv(
        REPORTS_DIR / "phase_6_8_controlled_short_observation_checks_v1.csv",
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
    print("PHASE 6.8 CONTROLLED SHORT OBSERVATION RUN VALIDATOR")
    print("=" * 100)
    print("Purpose: validate first clean operational short observation run")
    print("Restriction: validation only. No execution.")
    print()

    result = validate_phase_6_8_controlled_short_observation_run()

    print_section("PHASE 6.8 VALIDATION SUMMARY")
    print_df(result["summary"])

    print_section("PHASE 6.8 VALIDATION CHECKS")
    print_df(result["checks"])

    print()
    print("ARCHIVOS GENERADOS")
    print("=" * 100)
    print("- reports/phase_6_8_controlled_short_observation_run_v1/phase_6_8_controlled_short_observation_summary_v1.csv")
    print("- reports/phase_6_8_controlled_short_observation_run_v1/phase_6_8_controlled_short_observation_checks_v1.csv")
    print()
    print("Restriccion: este validador no habilita ejecucion.")


if __name__ == "__main__":
    main()