from pathlib import Path

import pandas as pd


PHASE_5_RUNBOOK_PATH = Path("docs") / "PHASE_5_OPERATIONAL_EVIDENCE_RUNBOOK.md"
PHASE_5_CLOSURE_PATH = Path("docs") / "PHASE_5_OPERATIONAL_EVIDENCE_CLOSURE.md"
PHASE_6_CHECKLIST_PATH = Path("docs") / "PHASE_6_FORWARD_EVIDENCE_OPERATIONS_CHECKLIST.md"

REQUIRED_FILES = [
    PHASE_5_RUNBOOK_PATH,
    PHASE_5_CLOSURE_PATH,
    PHASE_6_CHECKLIST_PATH,
    Path("src/workflows/run_operational_forward_evidence_bootstrap_v1.py"),
    Path("src/workflows/run_operational_input_file_validator_adapter_v1.py"),
    Path("src/workflows/run_operational_persistent_cycle_integration_v1.py"),
]

REQUIRED_CHECKLIST_PHRASES = [
    "PHASE 6 FORWARD EVIDENCE OPERATIONS CHECKLIST",
    "NO REAL CAPITAL",
    "NO PAPER TRADING EXECUTION",
    "NO LIVE ALERTS",
    "NO BINANCE EXECUTION",
    "NO QUANTFURY EXECUTION",
    "NO EXCHANGE EXECUTION",
    "NO AUTOMATION",
    "NO AUTONOMOUS TRADING BOT BEHAVIOR",
    "python -m src.workflows.run_operational_forward_evidence_bootstrap_v1",
    "python -m src.workflows.run_operational_input_file_validator_adapter_v1",
    "python -m src.workflows.run_operational_persistent_cycle_integration_v1",
    "minimum 100 resolved forward observations",
    "preferred 300 resolved forward observations",
    "PHASE_6_1_FORWARD_EVIDENCE_OPERATIONS_CHECKLIST_VALIDATED",
]


def print_section(title: str) -> None:
    print()
    print(title)
    print("=" * 100)


def read_text(path: Path) -> str:
    if not path.exists():
        return ""

    return path.read_text(encoding="utf-8", errors="ignore")


def build_required_files_df() -> pd.DataFrame:
    rows = []

    for path in REQUIRED_FILES:
        rows.append(
            {
                "file_path": str(path),
                "exists": path.exists(),
                "is_file": path.is_file(),
                "check_passed": path.exists() and path.is_file(),
            }
        )

    return pd.DataFrame(rows)


def build_document_validation_df() -> pd.DataFrame:
    rows = []
    checklist_text = read_text(PHASE_6_CHECKLIST_PATH)

    for phrase in REQUIRED_CHECKLIST_PHRASES:
        passed = phrase in checklist_text

        rows.append(
            {
                "document": str(PHASE_6_CHECKLIST_PATH),
                "check_name": "required_checklist_phrase",
                "passed": passed,
                "severity": "INFO" if passed else "ERROR",
                "details": phrase,
            }
        )

    return pd.DataFrame(rows)


def build_errors_df(
    required_files_df: pd.DataFrame,
    document_validation_df: pd.DataFrame,
) -> pd.DataFrame:
    rows = []

    missing_files = required_files_df[
        ~required_files_df["check_passed"].astype(bool)
    ]

    for _, row in missing_files.iterrows():
        rows.append(
            {
                "error_type": "MISSING_REQUIRED_FILE",
                "source": row["file_path"],
                "details": "Required file is missing.",
            }
        )

    failed_document_checks = document_validation_df[
        document_validation_df["severity"].eq("ERROR")
        & ~document_validation_df["passed"].astype(bool)
    ]

    for _, row in failed_document_checks.iterrows():
        rows.append(
            {
                "error_type": "DOCUMENT_VALIDATION_FAILED",
                "source": row["document"],
                "details": row["details"],
            }
        )

    return pd.DataFrame(rows)


def build_summary_df(
    required_files_df: pd.DataFrame,
    document_validation_df: pd.DataFrame,
    errors_df: pd.DataFrame,
) -> pd.DataFrame:
    required_files_present = (
        not required_files_df.empty
        and bool(required_files_df["check_passed"].all())
    )

    document_validation_passed = (
        not document_validation_df.empty
        and bool(document_validation_df["passed"].all())
    )

    validation_passed = (
        required_files_present
        and document_validation_passed
        and errors_df.empty
    )

    validation_decision = (
        "PHASE_6_1_FORWARD_EVIDENCE_OPERATIONS_CHECKLIST_VALIDATED"
        if validation_passed
        else "PHASE_6_1_FORWARD_EVIDENCE_OPERATIONS_CHECKLIST_FAILED"
    )

    return pd.DataFrame(
        [
            {
                "required_files_present": required_files_present,
                "required_files": len(required_files_df),
                "missing_files": int(
                    (~required_files_df["check_passed"].astype(bool)).sum()
                )
                if not required_files_df.empty
                else len(REQUIRED_FILES),
                "document_validation_passed": document_validation_passed,
                "failed_checks": len(errors_df),
                "validation_passed": validation_passed,
                "paper_trade_execution_allowed": False,
                "real_capital_allowed": False,
                "live_alerts_allowed": False,
                "exchange_execution_allowed": False,
                "automation_allowed": False,
                "execution_allowed": False,
                "validation_decision": validation_decision,
            }
        ]
    )


def save_df(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)


def print_selected(df: pd.DataFrame, columns: list[str]) -> None:
    if df.empty:
        print("Sin registros.")
        return

    existing_columns = [column for column in columns if column in df.columns]

    if not existing_columns:
        print(df.to_string(index=False))
        return

    print(df[existing_columns].to_string(index=False))


def main() -> None:
    print("PHASE 6.1 FORWARD EVIDENCE OPERATIONS CHECKLIST VALIDATOR V1")
    print("=" * 100)
    print("Purpose: validate Phase 6.1 operational checklist and safety restrictions")
    print("Restriction: checklist validation only. No execution.")
    print()

    reports_dir = Path("reports") / "phase_6_1_forward_evidence_operations_checklist_v1"
    reports_dir.mkdir(parents=True, exist_ok=True)

    required_files_df = build_required_files_df()
    document_validation_df = build_document_validation_df()
    errors_df = build_errors_df(
        required_files_df=required_files_df,
        document_validation_df=document_validation_df,
    )
    summary_df = build_summary_df(
        required_files_df=required_files_df,
        document_validation_df=document_validation_df,
        errors_df=errors_df,
    )

    save_df(
        required_files_df,
        reports_dir / "phase_6_1_required_files_v1.csv",
    )

    save_df(
        document_validation_df,
        reports_dir / "phase_6_1_document_validation_v1.csv",
    )

    save_df(
        errors_df,
        reports_dir / "phase_6_1_errors_v1.csv",
    )

    save_df(
        summary_df,
        reports_dir / "phase_6_1_summary_v1.csv",
    )

    print_section("PHASE 6.1 CHECKLIST SUMMARY")
    print_selected(
        summary_df,
        [
            "required_files_present",
            "required_files",
            "missing_files",
            "document_validation_passed",
            "failed_checks",
            "validation_passed",
            "paper_trade_execution_allowed",
            "real_capital_allowed",
            "live_alerts_allowed",
            "exchange_execution_allowed",
            "automation_allowed",
            "execution_allowed",
            "validation_decision",
        ],
    )

    print_section("REQUIRED FILES")
    print_selected(
        required_files_df,
        [
            "file_path",
            "exists",
            "is_file",
            "check_passed",
        ],
    )

    print_section("DOCUMENT VALIDATION")
    print_selected(
        document_validation_df,
        [
            "document",
            "check_name",
            "passed",
            "severity",
            "details",
        ],
    )

    print_section("ERRORS")
    print_selected(
        errors_df,
        [
            "error_type",
            "source",
            "details",
        ],
    )

    print()
    print("ARCHIVOS GENERADOS")
    print("=" * 100)
    print(f"- {reports_dir / 'phase_6_1_required_files_v1.csv'}")
    print(f"- {reports_dir / 'phase_6_1_document_validation_v1.csv'}")
    print(f"- {reports_dir / 'phase_6_1_errors_v1.csv'}")
    print(f"- {reports_dir / 'phase_6_1_summary_v1.csv'}")


if __name__ == "__main__":
    main()