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
DATASET_PATH = Path(
    "data/forward_evidence/operational/forward_evidence_dataset_v1.csv"
)
REPORTS_DIR = Path("reports/phase_6_9_controlled_input_evidence_run_v1")

CONTROLLED_CONTEXT_NAME = "CONTROLLED_INPUT_EVIDENCE_PHASE_6_9"

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


def row_to_searchable_text(row: pd.Series) -> str:
    values = []

    for value in row.tolist():
        try:
            if pd.isna(value):
                values.append("")
            else:
                values.append(str(value))
        except (TypeError, ValueError):
            values.append(str(value))

    return " ".join(values).upper()


def dataframe_contains_text(df: pd.DataFrame, text: str) -> bool:
    if df.empty:
        return False

    text_upper = text.upper()

    for _, row in df.iterrows():
        row_text = row_to_searchable_text(row)
        if text_upper in row_text:
            return True

    return False


def dataframe_row_count_containing_text(df: pd.DataFrame, text: str) -> int:
    if df.empty:
        return 0

    text_upper = text.upper()
    count = 0

    for _, row in df.iterrows():
        row_text = row_to_searchable_text(row)
        if text_upper in row_text:
            count += 1

    return count


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


def validate_phase_6_9_controlled_input_evidence_run() -> dict[str, pd.DataFrame]:
    profile_summary_df = read_csv_if_exists(PROFILE_BASED_SUMMARY_PATH)
    interval_summary_df = read_csv_if_exists(INTERVAL_SUMMARY_PATH)
    cycle_records_df = read_csv_if_exists(CYCLE_RECORDS_PATH)
    dataset_df = read_csv_if_exists(DATASET_PATH)

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
            check_name="dataset_exists",
            passed=not dataset_df.empty,
            severity="INFO" if not dataset_df.empty else "ERROR",
            details=str(DATASET_PATH),
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
            check_name="profile_operational_ready",
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

    total_generated = safe_int(profile_row.get("total_generated_observations"))
    total_closed = safe_int(profile_row.get("total_closed_observations"))
    total_new_rows = safe_int(profile_row.get("total_new_rows_added"))

    checks.append(
        build_check(
            check_name="generated_observations_present",
            passed=total_generated >= 1,
            severity="INFO" if total_generated >= 1 else "ERROR",
            details=f"total_generated_observations={total_generated}",
        )
    )

    checks.append(
        build_check(
            check_name="closed_observations_present",
            passed=total_closed >= 1,
            severity="INFO" if total_closed >= 1 else "ERROR",
            details=f"total_closed_observations={total_closed}",
        )
    )

    checks.append(
        build_check(
            check_name="new_dataset_rows_added",
            passed=total_new_rows >= 1,
            severity="INFO" if total_new_rows >= 1 else "ERROR",
            details=f"total_new_rows_added={total_new_rows}",
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

    if not cycle_records_df.empty and "adapter_decision" in cycle_records_df.columns:
        adapter_ready_count = int(
            cycle_records_df["adapter_decision"]
            .astype(str)
            .eq("OPERATIONAL_INPUT_VALIDATED_READY_FOR_CYCLE")
            .sum()
        )
    else:
        adapter_ready_count = 0

    checks.append(
        build_check(
            check_name="all_cycles_input_ready",
            passed=adapter_ready_count == 4,
            severity="INFO" if adapter_ready_count == 4 else "ERROR",
            details=f"adapter_ready_count={adapter_ready_count}",
        )
    )

    if not cycle_records_df.empty and "integration_decision" in cycle_records_df.columns:
        with_evidence_count = int(
            cycle_records_df["integration_decision"]
            .astype(str)
            .eq("OPERATIONAL_INTEGRATION_COMPLETED_WITH_EVIDENCE")
            .sum()
        )
        no_change_count = int(
            cycle_records_df["integration_decision"]
            .astype(str)
            .eq("OPERATIONAL_INTEGRATION_COMPLETED_NO_DATASET_CHANGES")
            .sum()
        )
    else:
        with_evidence_count = 0
        no_change_count = 0

    checks.append(
        build_check(
            check_name="at_least_one_cycle_completed_with_evidence",
            passed=with_evidence_count >= 1,
            severity="INFO" if with_evidence_count >= 1 else "ERROR",
            details=f"with_evidence_count={with_evidence_count}",
        )
    )

    checks.append(
        build_check(
            check_name="duplicate_cycles_no_dataset_changes",
            passed=no_change_count >= 1,
            severity="INFO" if no_change_count >= 1 else "ERROR",
            details=f"no_change_count={no_change_count}",
        )
    )

    if not cycle_records_df.empty and "new_rows_added" in cycle_records_df.columns:
        cycle_new_rows_sum = int(cycle_records_df["new_rows_added"].fillna(0).astype(int).sum())
    else:
        cycle_new_rows_sum = 0

    if not cycle_records_df.empty and "duplicate_rows_skipped" in cycle_records_df.columns:
        duplicate_rows_sum = int(
            cycle_records_df["duplicate_rows_skipped"].fillna(0).astype(int).sum()
        )
    else:
        duplicate_rows_sum = 0

    checks.append(
        build_check(
            check_name="cycle_new_rows_sum_positive",
            passed=cycle_new_rows_sum >= 1,
            severity="INFO" if cycle_new_rows_sum >= 1 else "ERROR",
            details=f"cycle_new_rows_sum={cycle_new_rows_sum}",
        )
    )

    checks.append(
        build_check(
            check_name="duplicate_protection_observed",
            passed=duplicate_rows_sum >= 1,
            severity="INFO" if duplicate_rows_sum >= 1 else "ERROR",
            details=f"duplicate_rows_sum={duplicate_rows_sum}",
        )
    )

    controlled_context_rows = dataframe_row_count_containing_text(
        dataset_df,
        CONTROLLED_CONTEXT_NAME,
    )

    checks.append(
        build_check(
            check_name="dataset_contains_controlled_context",
            passed=controlled_context_rows >= 1,
            severity="INFO" if controlled_context_rows >= 1 else "ERROR",
            details=f"controlled_context_rows={controlled_context_rows}",
        )
    )

    target_hit_present = dataframe_contains_text(dataset_df, "TARGET_HIT")

    checks.append(
        build_check(
            check_name="dataset_contains_target_hit",
            passed=target_hit_present,
            severity="INFO" if target_hit_present else "ERROR",
            details=f"target_hit_present={target_hit_present}",
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
                "phase": "6.9",
                "profile_name": safe_str(profile_row.get("normalized_profile_name")),
                "profile_readiness": safe_str(profile_row.get("profile_readiness")),
                "cycles_completed": safe_int(profile_row.get("cycles_completed")),
                "cycles_safe": safe_int(profile_row.get("cycles_safe")),
                "cycles_failed": safe_int(profile_row.get("cycles_failed")),
                "total_generated_observations": total_generated,
                "total_closed_observations": total_closed,
                "total_new_rows_added": total_new_rows,
                "with_evidence_count": with_evidence_count,
                "no_change_count": no_change_count,
                "duplicate_rows_sum": duplicate_rows_sum,
                "controlled_context_rows": controlled_context_rows,
                "target_hit_present": target_hit_present,
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
                    "PHASE_6_9_CONTROLLED_INPUT_EVIDENCE_RUN_VALIDATED"
                    if validation_passed
                    else "PHASE_6_9_CONTROLLED_INPUT_EVIDENCE_RUN_FAILED"
                ),
            }
        ]
    )

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    summary_df.to_csv(
        REPORTS_DIR / "phase_6_9_controlled_input_evidence_summary_v1.csv",
        index=False,
    )
    checks_df.to_csv(
        REPORTS_DIR / "phase_6_9_controlled_input_evidence_checks_v1.csv",
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
    print("PHASE 6.9 CONTROLLED INPUT EVIDENCE RUN VALIDATOR")
    print("=" * 100)
    print("Purpose: validate controlled operational input evidence run")
    print("Restriction: validation only. No execution.")
    print()

    result = validate_phase_6_9_controlled_input_evidence_run()

    print_section("PHASE 6.9 VALIDATION SUMMARY")
    print_df(result["summary"])

    print_section("PHASE 6.9 VALIDATION CHECKS")
    print_df(result["checks"])

    print()
    print("ARCHIVOS GENERADOS")
    print("=" * 100)
    print("- reports/phase_6_9_controlled_input_evidence_run_v1/phase_6_9_controlled_input_evidence_summary_v1.csv")
    print("- reports/phase_6_9_controlled_input_evidence_run_v1/phase_6_9_controlled_input_evidence_checks_v1.csv")
    print()
    print("Restriccion: este validador no habilita ejecucion.")


if __name__ == "__main__":
    main()