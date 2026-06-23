from pathlib import Path

import pandas as pd


def print_section(title: str) -> None:
    print()
    print(title)
    print("=" * 100)


def save_df(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)


def read_text(path: Path) -> str:
    if not path.exists():
        return ""

    return path.read_text(encoding="utf-8")


def validate_required_files() -> pd.DataFrame:
    required_files = [
        "docs/PHASE_3_FORWARD_OBSERVATION_CLOSURE.md",
        "src/journal/forward_observation_intake_v1.py",
        "src/journal/manual_forward_observation_template_v1.py",
        "src/journal/manual_observation_processor_v1.py",
        "src/journal/system_forward_observation_record_builder_v1.py",
        "src/journal/forward_observation_candidate_detector_v1.py",
        "src/journal/forward_observation_auto_pipeline_v1.py",
        "src/journal/forward_observation_resolution_engine_v1.py",
        "src/journal/forward_observation_review_report_v1.py",
        "src/workflows/validate_forward_observation_intake_v1.py",
        "src/workflows/build_manual_forward_observation_template_v1.py",
        "src/workflows/process_manual_observation_file_v1.py",
        "src/workflows/build_system_forward_observation_records_v1.py",
        "src/workflows/detect_forward_observation_candidates_v1.py",
        "src/workflows/run_forward_observation_auto_pipeline_v1.py",
        "src/workflows/resolve_forward_observations_v1.py",
        "src/workflows/build_forward_observation_review_report_v1.py",
    ]

    rows = []

    for file_path in required_files:
        path = Path(file_path)

        rows.append(
            {
                "check_name": f"required_file:{file_path}",
                "passed": path.exists(),
                "details": "OK" if path.exists() else "MISSING",
            }
        )

    return pd.DataFrame(rows)


def validate_closure_document(document_text: str) -> pd.DataFrame:
    required_phrases = [
        "PHASE_3_CLOSED_FORWARD_OBSERVATION_INFRASTRUCTURE_COMPLETE",
        "TARGET_SHORT_FIB_V5_MTF_V3_1 + FIXED_RR_2_5",
        "No capital real",
        "No paper trading ejecutado",
        "No alertas live",
        "No Binance/Quantfury execution",
        "Phase 4.1 — Forward Dataset Quality Gate V1",
        "Minimum 100 forward-observed resolved signals",
        "Preferred 300 forward-observed resolved signals",
    ]

    rows = []

    for phrase in required_phrases:
        passed = phrase in document_text

        rows.append(
            {
                "check_name": f"required_phrase:{phrase}",
                "passed": passed,
                "details": "OK" if passed else "MISSING",
            }
        )

    phase_headers = [
        "Phase 3.1",
        "Phase 3.2",
        "Phase 3.3",
        "Phase 3.4",
        "Phase 3.5",
        "Phase 3.6",
        "Phase 3.7",
        "Phase 3.8",
    ]

    for header in phase_headers:
        passed = header in document_text

        rows.append(
            {
                "check_name": f"phase_header:{header}",
                "passed": passed,
                "details": "OK" if passed else "MISSING",
            }
        )

    return pd.DataFrame(rows)


def build_phase_3_closure_summary(
    file_validation_df: pd.DataFrame,
    document_validation_df: pd.DataFrame,
) -> pd.DataFrame:
    required_files_passed = bool(file_validation_df["passed"].all())
    document_validation_passed = bool(document_validation_df["passed"].all())

    validation_passed = required_files_passed and document_validation_passed

    if validation_passed:
        closure_decision = "PHASE_3_CLOSURE_VALIDATED"
    else:
        closure_decision = "PHASE_3_CLOSURE_REVIEW_REQUIRED"

    return pd.DataFrame(
        [
            {
                "required_files_passed": required_files_passed,
                "document_validation_passed": document_validation_passed,
                "validation_passed": validation_passed,
                "paper_trade_execution_allowed": False,
                "real_capital_allowed": False,
                "live_alerts_allowed": False,
                "exchange_execution_allowed": False,
                "automation_allowed": False,
                "closure_decision": closure_decision,
            }
        ]
    )


def main() -> None:
    print("PHASE 3 FORWARD OBSERVATION CLOSURE VALIDATION")
    print("=" * 100)
    print("Purpose: validate Phase 3 closure documentation and required modules")
    print("Restriction: documentation validation only. No execution.")
    print()

    reports_dir = Path("reports") / "phase_3_forward_observation_closure"
    reports_dir.mkdir(parents=True, exist_ok=True)

    closure_doc_path = Path("docs") / "PHASE_3_FORWARD_OBSERVATION_CLOSURE.md"

    file_validation_df = validate_required_files()
    document_text = read_text(closure_doc_path)
    document_validation_df = validate_closure_document(document_text)
    summary_df = build_phase_3_closure_summary(
        file_validation_df=file_validation_df,
        document_validation_df=document_validation_df,
    )

    save_df(
        file_validation_df,
        reports_dir / "phase_3_required_files_validation.csv",
    )
    save_df(
        document_validation_df,
        reports_dir / "phase_3_closure_document_validation.csv",
    )
    save_df(
        summary_df,
        reports_dir / "phase_3_closure_summary.csv",
    )

    print_section("PHASE 3 CLOSURE SUMMARY")
    print(summary_df.to_string(index=False))

    print_section("REQUIRED FILES VALIDATION")
    print(file_validation_df.to_string(index=False))

    print_section("DOCUMENT VALIDATION")
    print(document_validation_df.to_string(index=False))

    print()
    print("ARCHIVOS GENERADOS")
    print("=" * 100)
    print(f"- {reports_dir / 'phase_3_required_files_validation.csv'}")
    print(f"- {reports_dir / 'phase_3_closure_document_validation.csv'}")
    print(f"- {reports_dir / 'phase_3_closure_summary.csv'}")

    print()
    print("Restriccion: esta validacion no habilita ejecucion operativa.")


if __name__ == "__main__":
    main()