from __future__ import annotations

import pandas as pd

from src.long_side.long_forward_observation_phase_10_22_controlled_start_dry_run_execution_review_v1 import (
    validate_long_forward_observation_controlled_start_dry_run_execution_review,
)


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
    print(
        "PHASE 10.22 LONG FORWARD OBSERVATION CONTROLLED START "
        "DRY-RUN EXECUTION REVIEW"
    )
    print("=" * 100)
    print("Purpose: review readiness for a future controlled start dry-run run.")
    print(
        "Restriction: no dry-run execution, no forward observation start, no "
        "official evidence, no signals, no alerts, no paper trading, no market execution."
    )

    result = validate_long_forward_observation_controlled_start_dry_run_execution_review()

    sections = [
        ("PHASE 10.22 VALIDATION SUMMARY", "summary"),
        ("PHASE 10.21 SOURCE SUMMARY", "source_phase_10_21_summary"),
        ("SOURCE DESIGN OUTPUT", "source_design_output"),
        ("SOURCE DESIGN VALIDATIONS", "source_design_validations"),
        ("SOURCE DESIGN CONTROLS", "source_design_controls"),
        ("SOURCE DESIGN RULES", "source_design_rules"),
        ("SOURCE DESIGN REQUIREMENTS", "source_design_requirements"),
        ("SOURCE DESIGN GUARD MATRIX", "source_design_guard_matrix"),
        ("SOURCE DESIGN DECISION", "source_design_decision"),
        ("SOURCE CHECKS", "source_checks"),
        ("EXECUTION REVIEW EVIDENCE CHAIN", "execution_review_evidence_chain"),
        ("EXECUTION REVIEW CONTROLS", "execution_review_controls"),
        ("EXECUTION REVIEW RULES", "execution_review_rules"),
        ("EXECUTION REVIEW REQUIREMENTS", "execution_review_requirements"),
        ("EXECUTION REVIEW GUARD MATRIX", "execution_review_guard_matrix"),
        ("EXECUTION REVIEW DECISION", "execution_review_decision"),
        ("VALIDATION CHECKS", "checks"),
    ]

    for title, key in sections:
        print_section(title)
        print_df(result[key])

    print()
    print("ARCHIVOS GENERADOS")
    print("=" * 100)
    print("- reports/p10_22_start_dry_run_execution_review_v1/start_dry_run_execution_review_summary_v1.csv")
    print("- reports/p10_22_start_dry_run_execution_review_v1/phase_10_21_source_summary_v1.csv")
    print("- reports/p10_22_start_dry_run_execution_review_v1/phase_10_21_source_design_output_v1.csv")
    print("- reports/p10_22_start_dry_run_execution_review_v1/phase_10_21_source_design_validations_v1.csv")
    print("- reports/p10_22_start_dry_run_execution_review_v1/phase_10_21_source_design_controls_v1.csv")
    print("- reports/p10_22_start_dry_run_execution_review_v1/phase_10_21_source_design_rules_v1.csv")
    print("- reports/p10_22_start_dry_run_execution_review_v1/phase_10_21_source_design_requirements_v1.csv")
    print("- reports/p10_22_start_dry_run_execution_review_v1/phase_10_21_source_design_guard_matrix_v1.csv")
    print("- reports/p10_22_start_dry_run_execution_review_v1/phase_10_21_source_design_decision_v1.csv")
    print("- reports/p10_22_start_dry_run_execution_review_v1/phase_10_21_source_checks_v1.csv")
    print("- reports/p10_22_start_dry_run_execution_review_v1/start_dry_run_execution_review_evidence_chain_v1.csv")
    print("- reports/p10_22_start_dry_run_execution_review_v1/start_dry_run_execution_review_controls_v1.csv")
    print("- reports/p10_22_start_dry_run_execution_review_v1/start_dry_run_execution_review_rules_v1.csv")
    print("- reports/p10_22_start_dry_run_execution_review_v1/start_dry_run_execution_review_requirements_v1.csv")
    print("- reports/p10_22_start_dry_run_execution_review_v1/start_dry_run_execution_review_guard_matrix_v1.csv")
    print("- reports/p10_22_start_dry_run_execution_review_v1/start_dry_run_execution_review_decision_v1.csv")
    print("- reports/p10_22_start_dry_run_execution_review_v1/start_dry_run_execution_review_checks_v1.csv")
    print()
    print(
        "Restriccion: Phase 10.22 revisa solamente la ejecucion futura del "
        "dry-run de inicio; no ejecuta dry-run, no inicia forward observation "
        "ni habilita evidencia oficial o ejecucion."
    )


if __name__ == "__main__":
    main()