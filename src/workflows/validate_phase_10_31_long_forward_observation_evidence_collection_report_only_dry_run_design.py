from __future__ import annotations

import pandas as pd

from src.long_side.long_forward_observation_phase_10_31_evidence_collection_report_only_dry_run_design_v1 import (
    validate_long_forward_observation_evidence_collection_report_only_dry_run_design,
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
        "PHASE 10.31 LONG FORWARD OBSERVATION EVIDENCE COLLECTION "
        "REPORT-ONLY DRY-RUN DESIGN"
    )
    print("=" * 100)
    print("Purpose: define the future report-only dry-run contract.")
    print(
        "Restriction: design-only. No dry-run execution, no evidence "
        "collection, no official dataset implementation or write, no "
        "signals, no alerts, no paper trading, no real capital and no "
        "market execution."
    )

    result = (
        validate_long_forward_observation_evidence_collection_report_only_dry_run_design()
    )

    sections = [
        ("PHASE 10.31 VALIDATION SUMMARY", "summary"),
        ("PHASE 10.30 SOURCE SUMMARY", "source_summary"),
        ("SOURCE EVIDENCE SCHEMA", "source_schema"),
        ("SOURCE REVIEW VALIDATIONS", "source_review_validations"),
        ("SOURCE REVIEW ITEMS", "source_review_items"),
        ("SOURCE REVIEW FINDINGS", "source_review_findings"),
        ("SOURCE REVIEW CONTROLS", "source_review_controls"),
        ("SOURCE REVIEW RULES", "source_review_rules"),
        ("SOURCE REVIEW REQUIREMENTS", "source_review_requirements"),
        ("SOURCE REVIEW GUARD MATRIX", "source_review_guard_matrix"),
        ("SOURCE REVIEW DECISION", "source_review_decision"),
        ("SOURCE REVIEW CHECKS", "source_review_checks"),
        ("SOURCE REVIEW MANIFEST", "source_review_manifest"),
        ("REPORT-ONLY DRY-RUN DESIGN SOURCE MANIFEST", "design_manifest"),
        ("REPORT-ONLY DRY-RUN DESIGN SCHEMA", "design_schema"),
        ("REPORT-ONLY DRY-RUN DESIGN SCENARIOS", "design_scenarios"),
        ("REPORT-ONLY DRY-RUN DESIGN STEPS", "design_steps"),
        ("REPORT-ONLY DRY-RUN CONTROLS", "dry_run_controls"),
        ("REPORT-ONLY DRY-RUN ARTIFACT PLAN", "artifact_plan"),
        ("REPORT-ONLY DRY-RUN ACCEPTANCE CRITERIA", "acceptance_criteria"),
        ("REPORT-ONLY DRY-RUN EXPECTED OUTCOMES", "expected_outcomes"),
        ("REPORT-ONLY DRY-RUN DESIGN VALIDATIONS", "design_validations"),
        ("REPORT-ONLY DRY-RUN DESIGN EVIDENCE CHAIN", "design_evidence_chain"),
        ("REPORT-ONLY DRY-RUN DESIGN VALIDATION CONTROLS", "design_validation_controls"),
        ("REPORT-ONLY DRY-RUN DESIGN RULES", "design_rules"),
        ("REPORT-ONLY DRY-RUN DESIGN REQUIREMENTS", "design_requirements"),
        ("REPORT-ONLY DRY-RUN DESIGN GUARD MATRIX", "design_guard_matrix"),
        ("REPORT-ONLY DRY-RUN DESIGN DECISION", "design_decision"),
        ("VALIDATION CHECKS", "checks"),
    ]

    for title, key in sections:
        print_section(title)
        print_df(result[key])

    print()
    print("ARCHIVOS GENERADOS")
    print("=" * 100)

    generated_files = [
        "report_only_dry_run_design_summary_v1.csv",
        "phase_10_30_source_summary_v1.csv",
        "phase_10_30_source_review_validations_v1.csv",
        "phase_10_30_source_review_items_v1.csv",
        "phase_10_30_source_review_findings_v1.csv",
        "phase_10_30_source_review_controls_v1.csv",
        "phase_10_30_source_review_rules_v1.csv",
        "phase_10_30_source_review_requirements_v1.csv",
        "phase_10_30_source_review_guard_matrix_v1.csv",
        "phase_10_30_source_review_decision_v1.csv",
        "phase_10_30_source_review_checks_v1.csv",
        "phase_10_30_source_review_manifest_v1.csv",
        "source_report_only_dry_run_design_artifact_manifest_v1.csv",
        "report_only_dry_run_design_schema_v1.csv",
        "report_only_dry_run_design_scenarios_v1.csv",
        "report_only_dry_run_design_steps_v1.csv",
        "report_only_dry_run_design_controls_v1.csv",
        "report_only_dry_run_design_artifact_plan_v1.csv",
        "report_only_dry_run_design_acceptance_criteria_v1.csv",
        "report_only_dry_run_design_expected_outcomes_v1.csv",
        "report_only_dry_run_design_validations_v1.csv",
        "report_only_dry_run_design_evidence_chain_v1.csv",
        "report_only_dry_run_design_validation_controls_v1.csv",
        "report_only_dry_run_design_rules_v1.csv",
        "report_only_dry_run_design_requirements_v1.csv",
        "report_only_dry_run_design_guard_matrix_v1.csv",
        "report_only_dry_run_design_decision_v1.csv",
        "report_only_dry_run_design_checks_v1.csv",
    ]

    for filename in generated_files:
        print(
            "- reports/p10_31_evidence_collection_report_only_"
            f"dry_run_design_v1/{filename}"
        )

    print()
    print(
        "Restriccion: Phase 10.31 define solamente el dry-run "
        "report-only. No ejecuta el dry-run, no recolecta evidencia, no "
        "implementa ni escribe el dataset oficial y no habilita senales, "
        "alertas, paper trading, capital real o ejecucion."
    )


if __name__ == "__main__":
    main()
