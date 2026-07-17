from __future__ import annotations

import pandas as pd

from src.long_side.long_forward_observation_phase_10_33_evidence_collection_report_only_dry_run_execution_review_v1 import (
    validate_long_forward_observation_evidence_collection_report_only_dry_run_execution_review,
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
        "PHASE 10.33 LONG FORWARD OBSERVATION EVIDENCE COLLECTION "
        "REPORT-ONLY DRY-RUN EXECUTION REVIEW"
    )
    print("=" * 100)
    print(
        "Purpose: review readiness for a future synthetic report-only "
        "dry-run run."
    )
    print(
        "Restriction: review-only. No dry-run execution, no generated "
        "dry-run rows, no evidence collection, no official dataset "
        "implementation or write, no signals, no alerts, no paper "
        "trading, no real capital and no market execution."
    )

    result = (
        validate_long_forward_observation_evidence_collection_report_only_dry_run_execution_review()
    )

    sections = [
        ("PHASE 10.33 VALIDATION SUMMARY", "summary"),
        ("PHASE 10.32 SOURCE SUMMARY", "source_summary"),
        ("PHASE 10.32 SOURCE SCHEMA", "source_schema"),
        ("PHASE 10.32 SOURCE SCENARIOS", "source_scenarios"),
        ("PHASE 10.32 SOURCE STEPS", "source_steps"),
        (
            "PHASE 10.32 SOURCE DRY-RUN CONTROLS",
            "source_dry_run_controls",
        ),
        (
            "PHASE 10.32 SOURCE ARTIFACT PLAN",
            "source_artifact_plan",
        ),
        (
            "PHASE 10.32 SOURCE ACCEPTANCE CRITERIA",
            "source_acceptance",
        ),
        (
            "PHASE 10.32 SOURCE EXPECTED OUTCOMES",
            "source_outcomes",
        ),
        (
            "PHASE 10.32 SOURCE REVIEW VALIDATIONS",
            "source_review_validations",
        ),
        (
            "PHASE 10.32 SOURCE REVIEW ITEMS",
            "source_review_items",
        ),
        (
            "PHASE 10.32 SOURCE REVIEW FINDINGS",
            "source_review_findings",
        ),
        (
            "PHASE 10.32 SOURCE REVIEW CONTROLS",
            "source_review_controls",
        ),
        (
            "PHASE 10.32 SOURCE REVIEW RULES",
            "source_review_rules",
        ),
        (
            "PHASE 10.32 SOURCE REVIEW REQUIREMENTS",
            "source_review_requirements",
        ),
        (
            "PHASE 10.32 SOURCE REVIEW GUARD MATRIX",
            "source_review_guard_matrix",
        ),
        (
            "PHASE 10.32 SOURCE REVIEW DECISION",
            "source_review_decision",
        ),
        (
            "PHASE 10.32 SOURCE REVIEW CHECKS",
            "source_review_checks",
        ),
        (
            "PHASE 10.32 SOURCE REVIEW MANIFEST",
            "source_review_manifest",
        ),
        (
            "EXECUTION REVIEW SOURCE MANIFEST",
            "execution_review_manifest",
        ),
        (
            "FUTURE REPORT-ONLY DRY-RUN EXECUTION CONTRACT",
            "future_execution_contract",
        ),
        (
            "REPORT-ONLY DRY-RUN EXECUTION PRECONDITIONS",
            "execution_preconditions",
        ),
        (
            "REPORT-ONLY DRY-RUN EXECUTION ABORT RULES",
            "execution_abort_rules",
        ),
        (
            "REPORT-ONLY DRY-RUN EXECUTION OUTPUT PLAN",
            "execution_output_plan",
        ),
        (
            "EXECUTION REVIEW VALIDATIONS",
            "review_validations",
        ),
        ("EXECUTION REVIEW ITEMS", "review_items"),
        ("EXECUTION REVIEW FINDINGS", "review_findings"),
        ("EXECUTION REVIEW CONTROLS", "review_controls"),
        ("EXECUTION REVIEW RULES", "review_rules"),
        ("EXECUTION REVIEW REQUIREMENTS", "review_requirements"),
        ("EXECUTION REVIEW GUARD MATRIX", "review_guard_matrix"),
        ("EXECUTION REVIEW DECISION", "review_decision"),
        ("VALIDATION CHECKS", "checks"),
    ]

    for title, key in sections:
        print_section(title)
        print_df(result[key])

    print()
    print("ARCHIVOS GENERADOS")
    print("=" * 100)

    generated_files = [
        "report_only_dry_run_execution_review_summary_v1.csv",
        "phase_10_32_source_summary_v1.csv",
        "phase_10_32_source_schema_v1.csv",
        "phase_10_32_source_scenarios_v1.csv",
        "phase_10_32_source_steps_v1.csv",
        "phase_10_32_source_dry_run_controls_v1.csv",
        "phase_10_32_source_artifact_plan_v1.csv",
        "phase_10_32_source_acceptance_v1.csv",
        "phase_10_32_source_outcomes_v1.csv",
        "phase_10_32_source_review_validations_v1.csv",
        "phase_10_32_source_review_items_v1.csv",
        "phase_10_32_source_review_findings_v1.csv",
        "phase_10_32_source_review_controls_v1.csv",
        "phase_10_32_source_review_rules_v1.csv",
        "phase_10_32_source_review_requirements_v1.csv",
        "phase_10_32_source_review_guard_matrix_v1.csv",
        "phase_10_32_source_review_decision_v1.csv",
        "phase_10_32_source_review_checks_v1.csv",
        "phase_10_32_source_review_manifest_v1.csv",
        "source_report_only_dry_run_execution_review_artifact_manifest_v1.csv",
        "report_only_dry_run_future_execution_contract_v1.csv",
        "report_only_dry_run_execution_preconditions_v1.csv",
        "report_only_dry_run_execution_abort_rules_v1.csv",
        "report_only_dry_run_execution_output_plan_v1.csv",
        "report_only_dry_run_execution_review_validations_v1.csv",
        "report_only_dry_run_execution_review_items_v1.csv",
        "report_only_dry_run_execution_review_findings_v1.csv",
        "report_only_dry_run_execution_review_controls_v1.csv",
        "report_only_dry_run_execution_review_rules_v1.csv",
        "report_only_dry_run_execution_review_requirements_v1.csv",
        "report_only_dry_run_execution_review_guard_matrix_v1.csv",
        "report_only_dry_run_execution_review_decision_v1.csv",
        "report_only_dry_run_execution_review_checks_v1.csv",
    ]

    for filename in generated_files:
        print(
            "- reports/p10_33_evidence_collection_report_only_"
            f"dry_run_execution_review_v1/{filename}"
        )

    print()
    print(
        "Restriccion: Phase 10.33 revisa solamente la preparacion para "
        "una futura ejecucion sintetica report-only. No ejecuta el "
        "dry-run, no genera filas, no recolecta evidencia, no implementa "
        "ni escribe el dataset oficial y no habilita senales, alertas, "
        "paper trading, capital real o ejecucion."
    )


if __name__ == "__main__":
    main()
