from pathlib import Path

import pandas as pd


REQUIRED_FILES = [
    "src/validation/forward_dataset_quality_gate_v1.py",
    "src/workflows/validate_forward_dataset_quality_gate_v1.py",
    "src/metrics/forward_performance_metrics_v1.py",
    "src/workflows/calculate_forward_performance_metrics_v1.py",
    "src/analysis/context_performance_analyzer_v1.py",
    "src/workflows/analyze_context_performance_v1.py",
    "src/analysis/forward_risk_regime_breakdown_analyzer_v1.py",
    "src/workflows/analyze_forward_risk_regime_breakdown_v1.py",
    "src/reports/forward_evidence_dashboard_v1.py",
    "src/workflows/build_forward_evidence_dashboard_v1.py",
    "docs/PHASE_4_FORWARD_EVIDENCE_CLOSURE.md",
]


REQUIRED_DOCUMENT_MARKERS = [
    "Phase 4 is formally closed",
    "DATASET_NOT_READY",
    "NO_EXECUTION_ALLOWED",
    "FORWARD_EVIDENCE_REPORT_SAMPLE_ONLY",
    "PHASE_4_FORWARD_EVIDENCE_CLOSURE_VALIDATED",
    "Resolved observations: `2`",
    "Gap to minimum: `98`",
    "Gap to preferred: `298`",
    "Real capital trading",
    "Executed paper trading",
    "Live trading alerts",
    "Binance execution",
    "Quantfury execution",
    "Automated order execution",
]


def save_df(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)


def validate_required_files() -> pd.DataFrame:
    rows = []

    for file_path in REQUIRED_FILES:
        path = Path(file_path)
        passed = path.exists() and path.is_file()

        rows.append(
            {
                "check_name": f"required_file:{file_path}",
                "passed": passed,
                "severity": "ERROR" if not passed else "INFO",
                "details": "OK" if passed else "MISSING",
            }
        )

    return pd.DataFrame(rows)


def validate_document_markers(document_path: Path) -> pd.DataFrame:
    rows = []

    if not document_path.exists():
        return pd.DataFrame(
            [
                {
                    "check_name": "closure_document_exists",
                    "passed": False,
                    "severity": "ERROR",
                    "details": "MISSING",
                }
            ]
        )

    content = document_path.read_text(encoding="utf-8")

    for marker in REQUIRED_DOCUMENT_MARKERS:
        passed = marker in content

        rows.append(
            {
                "check_name": f"document_marker:{marker}",
                "passed": passed,
                "severity": "ERROR" if not passed else "INFO",
                "details": "OK" if passed else "MISSING",
            }
        )

    return pd.DataFrame(rows)


def build_phase_4_closure_summary(checks_df: pd.DataFrame) -> pd.DataFrame:
    validation_passed = bool(checks_df["passed"].all()) if not checks_df.empty else False

    failed_checks = 0

    if not checks_df.empty:
        failed_checks = int((~checks_df["passed"]).sum())

    closure_decision = (
        "PHASE_4_FORWARD_EVIDENCE_CLOSURE_VALIDATED"
        if validation_passed
        else "PHASE_4_FORWARD_EVIDENCE_CLOSURE_VALIDATION_FAILED"
    )

    return pd.DataFrame(
        [
            {
                "validation_passed": validation_passed,
                "failed_checks": failed_checks,
                "phase_4_1_quality_gate_closed": True,
                "phase_4_2_metrics_closed": True,
                "phase_4_3_context_analyzer_closed": True,
                "phase_4_4_risk_regime_analyzer_closed": True,
                "phase_4_5_dashboard_closed": True,
                "dataset_quality_decision": "DATASET_NOT_READY",
                "readiness_state": "DATASET_NOT_READY",
                "execution_state": "NO_EXECUTION_ALLOWED",
                "resolved_observations": 2,
                "min_resolved_observations": 100,
                "preferred_resolved_observations": 300,
                "sample_gap_to_minimum": 98,
                "sample_gap_to_preferred": 298,
                "paper_trade_execution_allowed": False,
                "real_capital_allowed": False,
                "live_alerts_allowed": False,
                "exchange_execution_allowed": False,
                "automation_allowed": False,
                "closure_decision": closure_decision,
            }
        ]
    )


def print_section(title: str) -> None:
    print()
    print(title)
    print("=" * 100)


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
    print("PHASE 4 FORWARD EVIDENCE CLOSURE VALIDATION")
    print("=" * 100)
    print("Purpose: validate formal closure of Phase 4 forward evidence infrastructure")
    print("Restriction: closure validation only. No execution.")
    print()

    reports_dir = Path("reports") / "phase_4_forward_evidence_closure_v1"
    summary_path = reports_dir / "phase_4_forward_evidence_closure_summary_v1.csv"
    checks_path = reports_dir / "phase_4_forward_evidence_closure_checks_v1.csv"

    required_files_df = validate_required_files()
    document_markers_df = validate_document_markers(
        Path("docs") / "PHASE_4_FORWARD_EVIDENCE_CLOSURE.md"
    )

    checks_df = pd.concat(
        [
            required_files_df,
            document_markers_df,
        ],
        ignore_index=True,
    )

    summary_df = build_phase_4_closure_summary(checks_df)

    save_df(summary_df, summary_path)
    save_df(checks_df, checks_path)

    print_section("PHASE 4 CLOSURE SUMMARY")
    print_selected(
        summary_df,
        [
            "validation_passed",
            "failed_checks",
            "dataset_quality_decision",
            "readiness_state",
            "execution_state",
            "resolved_observations",
            "min_resolved_observations",
            "preferred_resolved_observations",
            "sample_gap_to_minimum",
            "sample_gap_to_preferred",
            "paper_trade_execution_allowed",
            "real_capital_allowed",
            "live_alerts_allowed",
            "exchange_execution_allowed",
            "automation_allowed",
            "closure_decision",
        ],
    )

    print_section("FAILED CHECKS")
    failed_df = checks_df[~checks_df["passed"]].copy()
    print_selected(
        failed_df,
        [
            "check_name",
            "severity",
            "details",
        ],
    )

    print()
    print("ARCHIVOS GENERADOS")
    print("=" * 100)
    print(f"- {summary_path}")
    print(f"- {checks_path}")

    print()
    print("Restriccion: este cierre valida infraestructura. No habilita ejecucion operativa.")


if __name__ == "__main__":
    main()