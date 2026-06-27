from pathlib import Path

import pandas as pd


REQUIRED_PHASE_5_FILES = [
    "src/journal/forward_observation_batch_runner_v1.py",
    "src/workflows/run_forward_observation_batch_runner_v1.py",
    "src/journal/forward_observation_batch_resolver_v1.py",
    "src/workflows/run_forward_observation_batch_resolver_v1.py",
    "src/journal/forward_evidence_accumulation_controller_v1.py",
    "src/workflows/run_forward_evidence_accumulation_controller_v1.py",
    "src/journal/forward_evidence_dataset_persistence_v1.py",
    "src/workflows/run_forward_evidence_dataset_persistence_v1.py",
    "src/journal/persistent_forward_evidence_cycle_runner_v1.py",
    "src/workflows/run_persistent_forward_evidence_cycle_runner_v1.py",
    "src/journal/operational_forward_evidence_bootstrap_v1.py",
    "src/workflows/run_operational_forward_evidence_bootstrap_v1.py",
    "src/journal/operational_input_file_validator_adapter_v1.py",
    "src/workflows/run_operational_input_file_validator_adapter_v1.py",
    "src/journal/operational_persistent_cycle_integration_v1.py",
    "src/workflows/run_operational_persistent_cycle_integration_v1.py",
]

RUNBOOK_PATH = Path("docs") / "PHASE_5_OPERATIONAL_EVIDENCE_RUNBOOK.md"
CLOSURE_PATH = Path("docs") / "PHASE_5_OPERATIONAL_EVIDENCE_CLOSURE.md"

REQUIRED_RUNBOOK_PHRASES = [
    "PHASE 5 OPERATIONAL EVIDENCE RUNBOOK",
    "NO REAL CAPITAL",
    "NO PAPER TRADING EXECUTION",
    "NO LIVE ALERTS",
    "NO BINANCE EXECUTION",
    "NO QUANTFURY EXECUTION",
    "NO EXCHANGE EXECUTION",
    "NO AUTOMATION",
    "OPERATIONAL_INPUT_WAITING_FOR_FILES",
    "OPERATIONAL_INPUT_VALIDATED_READY_FOR_CYCLE",
    "OPERATIONAL_INPUT_VALIDATION_FAILED",
    "OPERATIONAL_INTEGRATION_WAITING_FOR_VALID_INPUTS",
    "OPERATIONAL_INTEGRATION_COMPLETED_WITH_EVIDENCE",
    "OPERATIONAL_INTEGRATION_COMPLETED_NO_DATASET_CHANGES",
    "100 resolved forward observations",
    "300 resolved forward observations",
]

REQUIRED_CLOSURE_PHRASES = [
    "PHASE 5 CLOSED",
    "FORWARD EVIDENCE OPERATING LAYER COMPLETE",
    "PHASE_5_OPERATIONAL_EVIDENCE_CLOSURE_VALIDATED",
    "NO REAL CAPITAL",
    "NO PAPER TRADING EXECUTION",
    "NO LIVE ALERTS",
    "NO BINANCE EXECUTION",
    "NO QUANTFURY EXECUTION",
    "NO EXCHANGE EXECUTION",
    "NO AUTOMATION",
    "NO AUTONOMOUS TRADING BOT BEHAVIOR",
    "minimum 100 resolved forward observations",
    "preferred 300 resolved forward observations",
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

    for file_path in REQUIRED_PHASE_5_FILES:
        path = Path(file_path)

        rows.append(
            {
                "file_path": file_path,
                "exists": path.exists(),
                "is_file": path.is_file(),
                "check_passed": path.exists() and path.is_file(),
            }
        )

    return pd.DataFrame(rows)


def build_document_validation_df() -> pd.DataFrame:
    rows = []

    runbook_text = read_text(RUNBOOK_PATH)
    closure_text = read_text(CLOSURE_PATH)

    rows.append(
        {
            "document": str(RUNBOOK_PATH),
            "check_name": "runbook_present",
            "passed": RUNBOOK_PATH.exists() and RUNBOOK_PATH.is_file(),
            "severity": "INFO" if RUNBOOK_PATH.exists() else "ERROR",
            "details": str(RUNBOOK_PATH),
        }
    )

    rows.append(
        {
            "document": str(CLOSURE_PATH),
            "check_name": "closure_document_present",
            "passed": CLOSURE_PATH.exists() and CLOSURE_PATH.is_file(),
            "severity": "INFO" if CLOSURE_PATH.exists() else "ERROR",
            "details": str(CLOSURE_PATH),
        }
    )

    for phrase in REQUIRED_RUNBOOK_PHRASES:
        passed = phrase in runbook_text

        rows.append(
            {
                "document": str(RUNBOOK_PATH),
                "check_name": "required_runbook_phrase",
                "passed": passed,
                "severity": "INFO" if passed else "ERROR",
                "details": phrase,
            }
        )

    for phrase in REQUIRED_CLOSURE_PHRASES:
        passed = phrase in closure_text

        rows.append(
            {
                "document": str(CLOSURE_PATH),
                "check_name": "required_closure_phrase",
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
    error_rows = []

    missing_files = required_files_df[
        ~required_files_df["check_passed"].astype(bool)
    ].copy()

    for _, row in missing_files.iterrows():
        error_rows.append(
            {
                "error_type": "MISSING_PHASE_5_FILE",
                "source": row["file_path"],
                "details": "Required Phase 5 file is missing.",
            }
        )

    failed_doc_checks = document_validation_df[
        document_validation_df["severity"].eq("ERROR")
        & ~document_validation_df["passed"].astype(bool)
    ].copy()

    for _, row in failed_doc_checks.iterrows():
        error_rows.append(
            {
                "error_type": "DOCUMENT_VALIDATION_FAILED",
                "source": row["document"],
                "details": row["details"],
            }
        )

    return pd.DataFrame(error_rows)


def build_closure_summary_df(
    required_files_df: pd.DataFrame,
    document_validation_df: pd.DataFrame,
    errors_df: pd.DataFrame,
) -> pd.DataFrame:
    phase_5_files_present = (
        not required_files_df.empty
        and bool(required_files_df["check_passed"].all())
    )

    runbook_present = RUNBOOK_PATH.exists() and RUNBOOK_PATH.is_file()
    closure_document_present = CLOSURE_PATH.exists() and CLOSURE_PATH.is_file()

    document_validation_passed = (
        not document_validation_df.empty
        and bool(document_validation_df["passed"].all())
    )

    validation_passed = (
        phase_5_files_present
        and runbook_present
        and closure_document_present
        and document_validation_passed
        and errors_df.empty
    )

    closure_decision = (
        "PHASE_5_OPERATIONAL_EVIDENCE_CLOSURE_VALIDATED"
        if validation_passed
        else "PHASE_5_OPERATIONAL_EVIDENCE_CLOSURE_FAILED"
    )

    return pd.DataFrame(
        [
            {
                "phase_5_files_present": phase_5_files_present,
                "phase_5_required_files": len(required_files_df),
                "phase_5_missing_files": int(
                    (~required_files_df["check_passed"].astype(bool)).sum()
                )
                if not required_files_df.empty
                else len(REQUIRED_PHASE_5_FILES),
                "runbook_present": runbook_present,
                "closure_document_present": closure_document_present,
                "document_validation_passed": document_validation_passed,
                "failed_checks": len(errors_df),
                "validation_passed": validation_passed,
                "paper_trade_execution_allowed": False,
                "real_capital_allowed": False,
                "live_alerts_allowed": False,
                "exchange_execution_allowed": False,
                "automation_allowed": False,
                "execution_allowed": False,
                "closure_decision": closure_decision,
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
    print("PHASE 5 OPERATIONAL EVIDENCE CLOSURE VALIDATOR V1")
    print("=" * 100)
    print("Purpose: validate Phase 5 runbook, closure document and required files")
    print("Restriction: documentation and closure validation only. No execution.")
    print()

    reports_dir = Path("reports") / "phase_5_operational_evidence_closure_v1"
    reports_dir.mkdir(parents=True, exist_ok=True)

    required_files_df = build_required_files_df()
    document_validation_df = build_document_validation_df()
    errors_df = build_errors_df(
        required_files_df=required_files_df,
        document_validation_df=document_validation_df,
    )
    closure_summary_df = build_closure_summary_df(
        required_files_df=required_files_df,
        document_validation_df=document_validation_df,
        errors_df=errors_df,
    )

    save_df(
        required_files_df,
        reports_dir / "phase_5_required_files_v1.csv",
    )

    save_df(
        document_validation_df,
        reports_dir / "phase_5_document_validation_v1.csv",
    )

    save_df(
        errors_df,
        reports_dir / "phase_5_closure_errors_v1.csv",
    )

    save_df(
        closure_summary_df,
        reports_dir / "phase_5_closure_summary_v1.csv",
    )

    print_section("PHASE 5 CLOSURE SUMMARY")
    print_selected(
        closure_summary_df,
        [
            "phase_5_files_present",
            "phase_5_required_files",
            "phase_5_missing_files",
            "runbook_present",
            "closure_document_present",
            "document_validation_passed",
            "failed_checks",
            "validation_passed",
            "paper_trade_execution_allowed",
            "real_capital_allowed",
            "live_alerts_allowed",
            "exchange_execution_allowed",
            "automation_allowed",
            "execution_allowed",
            "closure_decision",
        ],
    )

    print_section("REQUIRED PHASE 5 FILES")
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

    print_section("CLOSURE ERRORS")
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
    print(f"- {reports_dir / 'phase_5_required_files_v1.csv'}")
    print(f"- {reports_dir / 'phase_5_document_validation_v1.csv'}")
    print(f"- {reports_dir / 'phase_5_closure_errors_v1.csv'}")
    print(f"- {reports_dir / 'phase_5_closure_summary_v1.csv'}")


if __name__ == "__main__":
    main()