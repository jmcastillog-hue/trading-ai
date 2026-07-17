from __future__ import annotations

import pandas as pd

from src.long_side.long_forward_observation_phase_10_30_evidence_collection_design_review_v1 import (
    validate_long_forward_observation_evidence_collection_design_review,
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
        "PHASE 10.30 LONG FORWARD OBSERVATION "
        "EVIDENCE COLLECTION DESIGN REVIEW"
    )
    print("=" * 100)
    print(
        "Purpose: review the Phase 10.29 LONG evidence collection design."
    )
    print(
        "Restriction: review-only. No evidence collection, no official "
        "dataset implementation or write, no signals, no alerts, no "
        "paper trading, no real capital and no market execution."
    )

    result = (
        validate_long_forward_observation_evidence_collection_design_review()
    )

    sections = [
        ("PHASE 10.30 VALIDATION SUMMARY", "summary"),
        ("PHASE 10.29 SOURCE SUMMARY", "source_phase_10_29_summary"),
        ("PHASE 10.29 SOURCE SCHEMA", "source_schema"),
        ("PHASE 10.29 SOURCE COMPONENTS", "source_components"),
        ("PHASE 10.29 SOURCE ACCEPTED SOURCES", "source_accepted_sources"),
        ("PHASE 10.29 SOURCE LIFECYCLE", "source_lifecycle"),
        ("PHASE 10.29 SOURCE DEDUPLICATION", "source_deduplication"),
        ("PHASE 10.29 SOURCE REJECTION", "source_rejection"),
        ("PHASE 10.29 SOURCE WRITE GUARDS", "source_write_guards"),
        ("PHASE 10.29 SOURCE AUDIT", "source_audit"),
        ("PHASE 10.29 SOURCE BOUNDARIES", "source_boundaries"),
        ("PHASE 10.29 SOURCE VALIDATIONS", "source_validations"),
        ("PHASE 10.29 SOURCE EVIDENCE CHAIN", "source_evidence_chain"),
        ("PHASE 10.29 SOURCE CONTROLS", "source_controls"),
        ("PHASE 10.29 SOURCE RULES", "source_rules"),
        ("PHASE 10.29 SOURCE REQUIREMENTS", "source_requirements"),
        ("PHASE 10.29 SOURCE GUARD MATRIX", "source_guard_matrix"),
        ("PHASE 10.29 SOURCE DECISION", "source_decision"),
        ("PHASE 10.29 SOURCE CHECKS", "source_checks"),
        ("PHASE 10.29 SOURCE MANIFEST", "source_manifest"),
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
        "evidence_collection_design_review_summary_v1.csv",
        "phase_10_29_source_summary_v1.csv",
        "phase_10_29_source_schema_v1.csv",
        "phase_10_29_source_components_v1.csv",
        "phase_10_29_source_accepted_sources_v1.csv",
        "phase_10_29_source_lifecycle_v1.csv",
        "phase_10_29_source_deduplication_v1.csv",
        "phase_10_29_source_rejection_v1.csv",
        "phase_10_29_source_write_guards_v1.csv",
        "phase_10_29_source_audit_v1.csv",
        "phase_10_29_source_boundaries_v1.csv",
        "phase_10_29_source_validations_v1.csv",
        "phase_10_29_source_evidence_chain_v1.csv",
        "phase_10_29_source_controls_v1.csv",
        "phase_10_29_source_rules_v1.csv",
        "phase_10_29_source_requirements_v1.csv",
        "phase_10_29_source_guard_matrix_v1.csv",
        "phase_10_29_source_decision_v1.csv",
        "phase_10_29_source_checks_v1.csv",
        "phase_10_29_source_manifest_v1.csv",
        "source_design_review_artifact_manifest_v1.csv",
        "evidence_collection_design_review_validations_v1.csv",
        "evidence_collection_design_review_items_v1.csv",
        "evidence_collection_design_review_findings_v1.csv",
        "evidence_collection_design_review_controls_v1.csv",
        "evidence_collection_design_review_rules_v1.csv",
        "evidence_collection_design_review_requirements_v1.csv",
        "evidence_collection_design_review_guard_matrix_v1.csv",
        "evidence_collection_design_review_decision_v1.csv",
        "evidence_collection_design_review_checks_v1.csv",
    ]

    for filename in generated_files:
        print(
            "- reports/p10_30_evidence_collection_design_review_v1/"
            f"{filename}"
        )

    print()
    print(
        "Restriccion: Phase 10.30 revisa solamente el contrato de "
        "recoleccion de evidencia. No recolecta evidencia, no implementa "
        "ni escribe el dataset oficial y no habilita senales, alertas, "
        "paper trading, capital real o ejecucion."
    )


if __name__ == "__main__":
    main()
