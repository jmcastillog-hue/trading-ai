from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd


REPORTS_DIR = Path("reports/phase_6_10_operational_evidence_closure_v1")

PHASE_6_REQUIRED_FILES = [
    "docs/PHASE_6_FORWARD_EVIDENCE_OPERATIONS_CHECKLIST.md",
    "docs/PHASE_6_FORWARD_EVIDENCE_RUN_LOG.md",
    "docs/PHASE_6_OPERATIONAL_SAFETY_GUARD_PREFLIGHT.md",
    "docs/PHASE_6_CONTROLLED_FORWARD_EVIDENCE_CYCLE_RUNNER.md",
    "docs/PHASE_6_CONTROLLED_INTERVAL_FORWARD_EVIDENCE_RUNNER.md",
    "docs/PHASE_6_OPERATIONAL_INTERVAL_RUN_PROFILES.md",
    "docs/PHASE_6_PROFILE_BASED_INTERVAL_RUNNER.md",
    "docs/PHASE_6_CONTROLLED_SHORT_OBSERVATION_RUN.md",
    "docs/PHASE_6_CONTROLLED_INPUT_EVIDENCE_RUN.md",
    "docs/PHASE_6_OPERATIONAL_EVIDENCE_CLOSURE.md",
    "src/workflows/validate_phase_6_1_forward_evidence_operations_checklist.py",
    "src/journal/forward_evidence_run_log_v1.py",
    "src/workflows/run_forward_evidence_run_log_v1.py",
    "src/validation/operational_safety_guard_preflight_v1.py",
    "src/workflows/run_operational_safety_guard_preflight_v1.py",
    "src/orchestration/controlled_forward_evidence_cycle_runner_v1.py",
    "src/workflows/run_controlled_forward_evidence_cycle_runner_v1.py",
    "src/orchestration/controlled_interval_forward_evidence_runner_v1.py",
    "src/workflows/run_controlled_interval_forward_evidence_runner_v1.py",
    "src/orchestration/operational_interval_run_profiles_v1.py",
    "src/workflows/validate_operational_interval_run_profiles_v1.py",
    "src/orchestration/profile_based_interval_forward_evidence_runner_v1.py",
    "src/workflows/run_profile_based_interval_forward_evidence_runner_v1.py",
    "src/workflows/validate_phase_6_8_controlled_short_observation_run.py",
    "src/workflows/validate_phase_6_9_controlled_input_evidence_run.py",
]

DEPENDENCY_FILES = [
    "src/workflows/run_operational_forward_evidence_bootstrap_v1.py",
    "src/workflows/run_operational_input_file_validator_adapter_v1.py",
    "src/workflows/run_operational_persistent_cycle_integration_v1.py",
    "data/forward_evidence/operational/forward_evidence_dataset_v1.csv",
]

PHASE_6_9_SUMMARY_PATH = Path(
    "reports/phase_6_9_controlled_input_evidence_run_v1/"
    "phase_6_9_controlled_input_evidence_summary_v1.csv"
)
PHASE_6_9_CHECKS_PATH = Path(
    "reports/phase_6_9_controlled_input_evidence_run_v1/"
    "phase_6_9_controlled_input_evidence_checks_v1.csv"
)
DATASET_PATH = Path("data/forward_evidence/operational/forward_evidence_dataset_v1.csv")

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
        if text_upper in row_to_searchable_text(row):
            return True

    return False


def all_execution_flags_false(row: dict[str, Any]) -> bool:
    for column in EXECUTION_FLAG_COLUMNS:
        if safe_bool(row.get(column, False)):
            return False

    return True


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


def validate_file_exists(path_text: str, check_group: str) -> dict[str, Any]:
    path = Path(path_text)
    exists = path.exists()

    return build_check(
        check_group=check_group,
        check_name=f"file_exists:{path_text}",
        passed=exists,
        severity="INFO" if exists else "ERROR",
        details=str(path),
    )


def validate_phase_6_10_operational_evidence_closure() -> dict[str, pd.DataFrame]:
    checks: list[dict[str, Any]] = []

    for path_text in PHASE_6_REQUIRED_FILES:
        checks.append(
            validate_file_exists(
                path_text=path_text,
                check_group="phase_6_required_files",
            )
        )

    for path_text in DEPENDENCY_FILES:
        checks.append(
            validate_file_exists(
                path_text=path_text,
                check_group="phase_6_dependency_files",
            )
        )

    phase_6_9_summary_df = read_csv_if_exists(PHASE_6_9_SUMMARY_PATH)
    phase_6_9_checks_df = read_csv_if_exists(PHASE_6_9_CHECKS_PATH)
    dataset_df = read_csv_if_exists(DATASET_PATH)

    phase_6_9_row = first_row(phase_6_9_summary_df)

    checks.append(
        build_check(
            check_group="phase_6_9_evidence",
            check_name="phase_6_9_summary_exists",
            passed=not phase_6_9_summary_df.empty,
            severity="INFO" if not phase_6_9_summary_df.empty else "ERROR",
            details=str(PHASE_6_9_SUMMARY_PATH),
        )
    )

    checks.append(
        build_check(
            check_group="phase_6_9_evidence",
            check_name="phase_6_9_checks_exist",
            passed=not phase_6_9_checks_df.empty,
            severity="INFO" if not phase_6_9_checks_df.empty else "ERROR",
            details=str(PHASE_6_9_CHECKS_PATH),
        )
    )

    checks.append(
        build_check(
            check_group="phase_6_9_evidence",
            check_name="phase_6_9_validated",
            passed=safe_str(phase_6_9_row.get("validation_decision"))
            == "PHASE_6_9_CONTROLLED_INPUT_EVIDENCE_RUN_VALIDATED",
            severity="INFO"
            if safe_str(phase_6_9_row.get("validation_decision"))
            == "PHASE_6_9_CONTROLLED_INPUT_EVIDENCE_RUN_VALIDATED"
            else "ERROR",
            details=safe_str(phase_6_9_row.get("validation_decision")),
        )
    )

    checks.append(
        build_check(
            check_group="phase_6_9_evidence",
            check_name="phase_6_9_generated_observations",
            passed=safe_int(phase_6_9_row.get("total_generated_observations")) >= 1,
            severity="INFO"
            if safe_int(phase_6_9_row.get("total_generated_observations")) >= 1
            else "ERROR",
            details=f"total_generated_observations={safe_int(phase_6_9_row.get('total_generated_observations'))}",
        )
    )

    checks.append(
        build_check(
            check_group="phase_6_9_evidence",
            check_name="phase_6_9_new_rows_added",
            passed=safe_int(phase_6_9_row.get("total_new_rows_added")) >= 1,
            severity="INFO"
            if safe_int(phase_6_9_row.get("total_new_rows_added")) >= 1
            else "ERROR",
            details=f"total_new_rows_added={safe_int(phase_6_9_row.get('total_new_rows_added'))}",
        )
    )

    checks.append(
        build_check(
            check_group="phase_6_9_evidence",
            check_name="duplicate_protection_validated",
            passed=safe_int(phase_6_9_row.get("duplicate_rows_sum")) >= 1,
            severity="INFO"
            if safe_int(phase_6_9_row.get("duplicate_rows_sum")) >= 1
            else "ERROR",
            details=f"duplicate_rows_sum={safe_int(phase_6_9_row.get('duplicate_rows_sum'))}",
        )
    )

    checks.append(
        build_check(
            check_group="dataset_evidence",
            check_name="dataset_contains_controlled_context",
            passed=dataframe_contains_text(dataset_df, CONTROLLED_CONTEXT_NAME),
            severity="INFO"
            if dataframe_contains_text(dataset_df, CONTROLLED_CONTEXT_NAME)
            else "ERROR",
            details=CONTROLLED_CONTEXT_NAME,
        )
    )

    checks.append(
        build_check(
            check_group="dataset_evidence",
            check_name="dataset_contains_target_hit",
            passed=dataframe_contains_text(dataset_df, "TARGET_HIT"),
            severity="INFO" if dataframe_contains_text(dataset_df, "TARGET_HIT") else "ERROR",
            details="TARGET_HIT",
        )
    )

    checks.append(
        build_check(
            check_group="execution_restrictions",
            check_name="phase_6_9_execution_flags_false",
            passed=all_execution_flags_false(phase_6_9_row),
            severity="INFO" if all_execution_flags_false(phase_6_9_row) else "ERROR",
            details="Phase 6.9 summary execution flags must remain false.",
        )
    )

    checks.append(
        build_check(
            check_group="scope_control",
            check_name="phase_6_closed_but_project_not_complete",
            passed=True,
            severity="INFO",
            details="Phase 6 closure is not total project completion.",
        )
    )

    checks.append(
        build_check(
            check_group="scope_control",
            check_name="long_side_not_established_yet",
            passed=True,
            severity="WARNING",
            details="LONG-side strategy remains future work and must not be marked complete.",
        )
    )

    checks.append(
        build_check(
            check_group="scope_control",
            check_name="real_entries_not_approved_yet",
            passed=True,
            severity="WARNING",
            details="Real operational entries are not approved by Phase 6 closure.",
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
                "phase": "6.10",
                "phase_6_required_files": len(PHASE_6_REQUIRED_FILES),
                "dependency_files": len(DEPENDENCY_FILES),
                "total_checks": len(checks_df),
                "warning_count": warning_count,
                "error_count": error_count,
                "blocker_count": blocker_count,
                "phase_6_9_validation_decision": safe_str(
                    phase_6_9_row.get("validation_decision")
                ),
                "phase_6_9_generated_observations": safe_int(
                    phase_6_9_row.get("total_generated_observations")
                ),
                "phase_6_9_new_rows_added": safe_int(
                    phase_6_9_row.get("total_new_rows_added")
                ),
                "phase_6_9_duplicate_rows_sum": safe_int(
                    phase_6_9_row.get("duplicate_rows_sum")
                ),
                "phase_6_closed": validation_passed,
                "total_project_completed": False,
                "long_side_established": False,
                "real_entries_approved": False,
                "paper_trade_execution_allowed": False,
                "real_capital_allowed": False,
                "live_alerts_allowed": False,
                "exchange_execution_allowed": False,
                "automation_allowed": False,
                "execution_allowed": False,
                "estimated_total_project_progress_percent": 76,
                "validation_passed": validation_passed,
                "validation_decision": (
                    "PHASE_6_10_OPERATIONAL_EVIDENCE_CLOSURE_VALIDATED"
                    if validation_passed
                    else "PHASE_6_10_OPERATIONAL_EVIDENCE_CLOSURE_FAILED"
                ),
            }
        ]
    )

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    summary_df.to_csv(
        REPORTS_DIR / "phase_6_10_operational_evidence_closure_summary_v1.csv",
        index=False,
    )
    checks_df.to_csv(
        REPORTS_DIR / "phase_6_10_operational_evidence_closure_checks_v1.csv",
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
    print("PHASE 6.10 OPERATIONAL EVIDENCE CLOSURE VALIDATOR")
    print("=" * 100)
    print("Purpose: validate Phase 6 operational evidence closure")
    print("Restriction: closure validation only. No execution.")
    print()

    result = validate_phase_6_10_operational_evidence_closure()

    print_section("PHASE 6.10 VALIDATION SUMMARY")
    print_df(result["summary"])

    print_section("PHASE 6.10 VALIDATION CHECKS")
    print_df(result["checks"])

    print()
    print("ARCHIVOS GENERADOS")
    print("=" * 100)
    print("- reports/phase_6_10_operational_evidence_closure_v1/phase_6_10_operational_evidence_closure_summary_v1.csv")
    print("- reports/phase_6_10_operational_evidence_closure_v1/phase_6_10_operational_evidence_closure_checks_v1.csv")
    print()
    print("Restriccion: este validador no habilita ejecucion.")


if __name__ == "__main__":
    main()