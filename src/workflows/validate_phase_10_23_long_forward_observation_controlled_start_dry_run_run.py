from __future__ import annotations

import pandas as pd

from src.long_side.long_forward_observation_phase_10_23_controlled_start_dry_run_run_v1 import (
    validate_long_forward_observation_controlled_start_dry_run_run,
)


def print_section(title: str) -> None:
    print()
    print(title)
    print("=" * 100)


def print_df(df: pd.DataFrame, max_rows: int | None = None) -> None:
    if df.empty:
        print("Sin registros.")
        return

    if max_rows is not None:
        print(df.head(max_rows).to_string(index=False))
        return

    print(df.to_string(index=False))


def main() -> None:
    print("PHASE 10.23 LONG FORWARD OBSERVATION CONTROLLED START DRY-RUN RUN")
    print("=" * 100)
    print("Purpose: perform one controlled start dry-run artifact.")
    print(
        "Restriction: dry-run only. No forward observation start, official "
        "evidence, live signals, alerts, paper trading, real capital, or "
        "market execution."
    )

    result = validate_long_forward_observation_controlled_start_dry_run_run()

    sections = [
        ("PHASE 10.23 VALIDATION SUMMARY", "summary"),
        ("PHASE 10.22 SOURCE SUMMARY", "source_phase_10_22_summary"),
        ("SOURCE DESIGN OUTPUT", "source_design_output"),
        ("SOURCE DESIGN VALIDATIONS", "source_design_validations"),
        ("SOURCE DESIGN CONTROLS", "source_design_controls"),
        ("SOURCE DESIGN RULES", "source_design_rules"),
        ("SOURCE DESIGN REQUIREMENTS", "source_design_requirements"),
        ("SOURCE DESIGN GUARD MATRIX", "source_design_guard_matrix"),
        ("SOURCE DESIGN DECISION", "source_design_decision"),
        ("SOURCE CHECKS", "source_checks"),
        (
            "SOURCE EXECUTION REVIEW EVIDENCE CHAIN",
            "source_execution_review_evidence_chain",
        ),
        (
            "SOURCE EXECUTION REVIEW CONTROLS",
            "source_execution_review_controls",
        ),
        ("SOURCE EXECUTION REVIEW RULES", "source_execution_review_rules"),
        (
            "SOURCE EXECUTION REVIEW REQUIREMENTS",
            "source_execution_review_requirements",
        ),
        (
            "SOURCE EXECUTION REVIEW GUARD MATRIX",
            "source_execution_review_guard_matrix",
        ),
        (
            "SOURCE EXECUTION REVIEW DECISION",
            "source_execution_review_decision",
        ),
        ("SOURCE PHASE 10.22 CHECKS", "source_phase_10_22_checks"),
        ("CONTROLLED START DRY-RUN OUTPUT", "controlled_start_dry_run_output"),
        ("START DRY-RUN RUN VALIDATIONS", "start_dry_run_run_validations"),
        (
            "START DRY-RUN RUN EVIDENCE CHAIN",
            "start_dry_run_run_evidence_chain",
        ),
        ("START DRY-RUN RUN CONTROLS", "start_dry_run_run_controls"),
        ("START DRY-RUN RUN RULES", "start_dry_run_run_rules"),
        ("START DRY-RUN RUN REQUIREMENTS", "start_dry_run_run_requirements"),
        ("START DRY-RUN RUN GUARD MATRIX", "start_dry_run_run_guard_matrix"),
        ("START DRY-RUN RUN DECISION", "start_dry_run_run_decision"),
        ("VALIDATION CHECKS", "checks"),
    ]

    for title, key in sections:
        print_section(title)
        print_df(result[key])

    print()
    print("ARCHIVOS GENERADOS")
    print("=" * 100)
    generated_files = [
        "reports/p10_23_start_dry_run_run_v1/start_dry_run_run_summary_v1.csv",
        "reports/p10_23_start_dry_run_run_v1/phase_10_22_source_summary_v1.csv",
        "reports/p10_23_start_dry_run_run_v1/phase_10_21_source_design_output_v1.csv",
        "reports/p10_23_start_dry_run_run_v1/phase_10_21_source_design_validations_v1.csv",
        "reports/p10_23_start_dry_run_run_v1/phase_10_21_source_design_controls_v1.csv",
        "reports/p10_23_start_dry_run_run_v1/phase_10_21_source_design_rules_v1.csv",
        "reports/p10_23_start_dry_run_run_v1/phase_10_21_source_design_requirements_v1.csv",
        "reports/p10_23_start_dry_run_run_v1/phase_10_21_source_design_guard_matrix_v1.csv",
        "reports/p10_23_start_dry_run_run_v1/phase_10_21_source_design_decision_v1.csv",
        "reports/p10_23_start_dry_run_run_v1/phase_10_21_source_checks_v1.csv",
        "reports/p10_23_start_dry_run_run_v1/phase_10_22_source_execution_review_evidence_chain_v1.csv",
        "reports/p10_23_start_dry_run_run_v1/phase_10_22_source_execution_review_controls_v1.csv",
        "reports/p10_23_start_dry_run_run_v1/phase_10_22_source_execution_review_rules_v1.csv",
        "reports/p10_23_start_dry_run_run_v1/phase_10_22_source_execution_review_requirements_v1.csv",
        "reports/p10_23_start_dry_run_run_v1/phase_10_22_source_execution_review_guard_matrix_v1.csv",
        "reports/p10_23_start_dry_run_run_v1/phase_10_22_source_execution_review_decision_v1.csv",
        "reports/p10_23_start_dry_run_run_v1/phase_10_22_source_checks_v1.csv",
        "reports/p10_23_start_dry_run_run_v1/controlled_start_dry_run_output_v1.csv",
        "reports/p10_23_start_dry_run_run_v1/start_dry_run_run_validations_v1.csv",
        "reports/p10_23_start_dry_run_run_v1/start_dry_run_run_evidence_chain_v1.csv",
        "reports/p10_23_start_dry_run_run_v1/start_dry_run_run_controls_v1.csv",
        "reports/p10_23_start_dry_run_run_v1/start_dry_run_run_rules_v1.csv",
        "reports/p10_23_start_dry_run_run_v1/start_dry_run_run_requirements_v1.csv",
        "reports/p10_23_start_dry_run_run_v1/start_dry_run_run_guard_matrix_v1.csv",
        "reports/p10_23_start_dry_run_run_v1/start_dry_run_run_decision_v1.csv",
        "reports/p10_23_start_dry_run_run_v1/start_dry_run_run_checks_v1.csv",
    ]

    for path in generated_files:
        print(f"- {path}")

    print()
    print(
        "Restriccion: Phase 10.23 ejecuta solamente un dry-run controlado de "
        "inicio; no inicia forward observation, no persiste evidencia oficial "
        "ni habilita señales, alertas, paper trading, capital real o ejecucion."
    )


if __name__ == "__main__":
    main()