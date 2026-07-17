from __future__ import annotations

import pandas as pd

from src.long_side.long_forward_observation_phase_10_32_evidence_collection_report_only_dry_run_design_review_v1 import (
    validate_long_forward_observation_evidence_collection_report_only_dry_run_design_review,
)


def print_section(title: str) -> None:
    print()
    print(title)
    print("=" * 100)


def print_df(df: pd.DataFrame) -> None:
    if df.empty:
        print("Sin registros.")
    else:
        print(df.to_string(index=False))


def main() -> None:
    print(
        "PHASE 10.32 LONG FORWARD OBSERVATION EVIDENCE COLLECTION "
        "REPORT-ONLY DRY-RUN DESIGN REVIEW"
    )
    print("=" * 100)
    print("Purpose: review the Phase 10.31 report-only dry-run design.")
    print(
        "Restriction: review-only. No dry-run execution, no generated "
        "dry-run rows, no evidence collection, no official dataset "
        "implementation or write, no signals, no alerts, no paper "
        "trading, no real capital and no market execution."
    )

    result = (
        validate_long_forward_observation_evidence_collection_report_only_dry_run_design_review()
    )

    sections = [
        ("PHASE 10.32 VALIDATION SUMMARY", "summary"),
        ("PHASE 10.31 SOURCE SUMMARY", "source_summary"),
        ("PHASE 10.31 SOURCE SCHEMA", "source_schema"),
        ("PHASE 10.31 SOURCE SCENARIOS", "source_scenarios"),
        ("PHASE 10.31 SOURCE STEPS", "source_steps"),
        ("PHASE 10.31 SOURCE DRY-RUN CONTROLS", "source_dry_run_controls"),
        ("PHASE 10.31 SOURCE ARTIFACT PLAN", "source_artifact_plan"),
        ("PHASE 10.31 SOURCE ACCEPTANCE CRITERIA", "source_acceptance"),
        ("PHASE 10.31 SOURCE EXPECTED OUTCOMES", "source_outcomes"),
        ("PHASE 10.31 SOURCE VALIDATIONS", "source_validations"),
        ("PHASE 10.31 SOURCE EVIDENCE CHAIN", "source_evidence_chain"),
        ("PHASE 10.31 SOURCE VALIDATION CONTROLS", "source_validation_controls"),
        ("PHASE 10.31 SOURCE RULES", "source_rules"),
        ("PHASE 10.31 SOURCE REQUIREMENTS", "source_requirements"),
        ("PHASE 10.31 SOURCE GUARD MATRIX", "source_guard_matrix"),
        ("PHASE 10.31 SOURCE DECISION", "source_decision"),
        ("PHASE 10.31 SOURCE CHECKS", "source_checks"),
        ("PHASE 10.31 SOURCE MANIFEST", "source_manifest"),
        ("DESIGN REVIEW SOURCE MANIFEST", "review_manifest"),
        ("DESIGN REVIEW VALIDATIONS", "review_validations"),
        ("DESIGN REVIEW ITEMS", "review_items"),
        ("DESIGN REVIEW FINDINGS", "review_findings"),
        ("DESIGN REVIEW CONTROLS", "review_controls"),
        ("DESIGN REVIEW RULES", "review_rules"),
        ("DESIGN REVIEW REQUIREMENTS", "review_requirements"),
        ("DESIGN REVIEW GUARD MATRIX", "review_guard_matrix"),
        ("DESIGN REVIEW DECISION", "review_decision"),
        ("VALIDATION CHECKS", "checks"),
    ]

    for title, key in sections:
        print_section(title)
        print_df(result[key])

    print()
    print("ARCHIVOS GENERADOS")
    print("=" * 100)

    generated_files = [
        "report_only_dry_run_design_review_summary_v1.csv",
        "phase_10_31_source_summary_v1.csv",
        "phase_10_31_source_schema_v1.csv",
        "phase_10_31_source_scenarios_v1.csv",
        "phase_10_31_source_steps_v1.csv",
        "phase_10_31_source_dry_run_controls_v1.csv",
        "phase_10_31_source_artifact_plan_v1.csv",
        "phase_10_31_source_acceptance_v1.csv",
        "phase_10_31_source_outcomes_v1.csv",
        "phase_10_31_source_validations_v1.csv",
        "phase_10_31_source_evidence_chain_v1.csv",
        "phase_10_31_source_validation_controls_v1.csv",
        "phase_10_31_source_rules_v1.csv",
        "phase_10_31_source_requirements_v1.csv",
        "phase_10_31_source_guard_matrix_v1.csv",
        "phase_10_31_source_decision_v1.csv",
        "phase_10_31_source_checks_v1.csv",
        "phase_10_31_source_manifest_v1.csv",
        "source_report_only_dry_run_design_review_artifact_manifest_v1.csv",
        "report_only_dry_run_design_review_validations_v1.csv",
        "report_only_dry_run_design_review_items_v1.csv",
        "report_only_dry_run_design_review_findings_v1.csv",
        "report_only_dry_run_design_review_controls_v1.csv",
        "report_only_dry_run_design_review_rules_v1.csv",
        "report_only_dry_run_design_review_requirements_v1.csv",
        "report_only_dry_run_design_review_guard_matrix_v1.csv",
        "report_only_dry_run_design_review_decision_v1.csv",
        "report_only_dry_run_design_review_checks_v1.csv",
    ]

    for filename in generated_files:
        print(
            "- reports/p10_32_evidence_collection_report_only_"
            f"dry_run_design_review_v1/{filename}"
        )

    print()
    print(
        "Restriccion: Phase 10.32 revisa solamente el diseno del dry-run "
        "report-only. No ejecuta el dry-run, no genera filas, no recolecta "
        "evidencia, no implementa ni escribe el dataset oficial y no "
        "habilita senales, alertas, paper trading, capital real o ejecucion."
    )


if __name__ == "__main__":
    main()
