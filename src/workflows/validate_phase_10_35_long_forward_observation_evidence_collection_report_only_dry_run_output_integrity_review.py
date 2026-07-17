from __future__ import annotations

import pandas as pd

from src.long_side.long_forward_observation_phase_10_35_evidence_collection_report_only_dry_run_output_integrity_review_v1 import (
    run_long_forward_observation_evidence_collection_report_only_dry_run_output_integrity_review,
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
        "PHASE 10.35 LONG FORWARD OBSERVATION EVIDENCE COLLECTION "
        "REPORT-ONLY DRY-RUN OUTPUT INTEGRITY REVIEW"
    )
    print("=" * 100)
    print(
        "Purpose: review integrity of the Phase 10.34 synthetic "
        "report-only dry-run outputs."
    )
    print(
        "Restriction: review-only. No new dry-run execution, no real "
        "evidence collection, no official dataset implementation or "
        "write, no signals, no alerts, no paper trading, no real "
        "capital and no market execution."
    )

    result = (
        run_long_forward_observation_evidence_collection_report_only_dry_run_output_integrity_review()
    )

    sections = [
        ("PHASE 10.35 VALIDATION SUMMARY", "summary"),
        ("PHASE 10.34 SOURCE SUMMARY", "source_summary"),
        (
            "PHASE 10.34 SOURCE SYNTHETIC INPUT ROWS",
            "source_synthetic_input_rows",
        ),
        (
            "PHASE 10.34 SOURCE SCENARIO RESULTS",
            "source_scenario_results",
        ),
        (
            "PHASE 10.34 SOURCE VALIDATION RESULTS",
            "source_validation_results",
        ),
        (
            "PHASE 10.34 SOURCE REJECTION RESULTS",
            "source_rejection_results",
        ),
        (
            "PHASE 10.34 SOURCE HASH AND DEDUPLICATION RESULTS",
            "source_hash_and_dedup_results",
        ),
        (
            "PHASE 10.34 SOURCE SAFETY LOCK RESULTS",
            "source_safety_lock_results",
        ),
        (
            "PHASE 10.34 SOURCE OFFICIAL DATASET GUARDS",
            "source_official_dataset_guard_results",
        ),
        ("PHASE 10.34 SOURCE CHECKS", "source_checks"),
        ("PHASE 10.34 SOURCE RUN MANIFEST", "source_run_manifest"),
        (
            "PHASE 10.34 SOURCE ARTIFACT MANIFEST",
            "source_artifact_manifest",
        ),
        ("OUTPUT INTEGRITY VALIDATIONS", "validations"),
        ("OUTPUT INTEGRITY REVIEW ITEMS", "items"),
        ("OUTPUT INTEGRITY FINDINGS", "findings"),
        ("OUTPUT INTEGRITY CONTROLS", "controls"),
        ("OUTPUT INTEGRITY RULES", "rules"),
        ("OUTPUT INTEGRITY REQUIREMENTS", "requirements"),
        ("OUTPUT INTEGRITY GUARD MATRIX", "guard_matrix"),
        ("OUTPUT INTEGRITY DECISION", "decision"),
        ("VALIDATION CHECKS", "checks"),
        ("REVIEW MANIFEST", "manifest"),
    ]

    for title, key in sections:
        print_section(title)
        print_df(result[key])

    print()
    print("ARCHIVOS GENERADOS")
    print("=" * 100)
    generated = [
        "report_only_dry_run_output_integrity_review_summary_v1.csv",
        "report_only_dry_run_output_integrity_review_validations_v1.csv",
        "report_only_dry_run_output_integrity_review_items_v1.csv",
        "report_only_dry_run_output_integrity_review_findings_v1.csv",
        "report_only_dry_run_output_integrity_review_controls_v1.csv",
        "report_only_dry_run_output_integrity_review_rules_v1.csv",
        "report_only_dry_run_output_integrity_review_requirements_v1.csv",
        "report_only_dry_run_output_integrity_review_guard_matrix_v1.csv",
        "report_only_dry_run_output_integrity_review_decision_v1.csv",
        "report_only_dry_run_output_integrity_review_checks_v1.csv",
        "source_report_only_dry_run_output_integrity_artifact_manifest_v1.csv",
    ]
    for filename in generated:
        print(
            "- reports/p10_35_evidence_collection_report_only_dry_run_"
            f"output_integrity_review_v1/{filename}"
        )

    print()
    print(
        "Restriccion: Phase 10.35 revisa solamente la integridad de "
        "los artefactos del dry-run report-only de Phase 10.34. No "
        "ejecuta nuevamente el dry-run, no recolecta evidencia real, "
        "no implementa ni escribe el dataset oficial y no habilita "
        "senales, alertas, paper trading, capital real, ejecucion o "
        "automatizacion."
    )


if __name__ == "__main__":
    main()
