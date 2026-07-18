from __future__ import annotations

import pandas as pd

from src.long_side.long_forward_observation_phase_10_38_evidence_collection_official_dataset_schema_implementation_design_review_v1 import (
    run_long_forward_observation_evidence_collection_official_dataset_schema_implementation_design_review,
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
        "PHASE 10.38 LONG FORWARD OBSERVATION EVIDENCE COLLECTION "
        "OFFICIAL DATASET SCHEMA IMPLEMENTATION DESIGN REVIEW"
    )
    print("=" * 100)
    print(
        "Purpose: independently review the Phase 10.37 official "
        "dataset schema implementation design."
    )
    print(
        "Restriction: review-only. No dataset implementation or "
        "creation, no evidence collection or persistence, no signals, "
        "alerts, paper trading, real capital, execution or automation."
    )

    result = (
        run_long_forward_observation_evidence_collection_official_dataset_schema_implementation_design_review()
    )

    sections = [
        ("PHASE 10.38 VALIDATION SUMMARY", "summary"),
        ("PHASE 10.37 SOURCE SUMMARY", "source_summary"),
        ("PHASE 10.37 SOURCE FIELD CATALOG", "source_field_catalog"),
        ("PHASE 10.37 SOURCE ENUM DOMAINS", "source_enum_domains"),
        ("PHASE 10.37 SOURCE CONSTRAINTS", "source_constraints"),
        (
            "PHASE 10.37 SOURCE KEY AND INDEX DESIGN",
            "source_key_index_design",
        ),
        (
            "PHASE 10.37 SOURCE PROVENANCE CONTRACT",
            "source_provenance_contract",
        ),
        (
            "PHASE 10.37 SOURCE LIFECYCLE CONTRACT",
            "source_lifecycle_contract",
        ),
        (
            "PHASE 10.37 SOURCE MIGRATION PLAN",
            "source_migration_plan",
        ),
        (
            "PHASE 10.37 SOURCE SAFETY GUARDS",
            "source_safety_guards",
        ),
        (
            "PHASE 10.37 SOURCE ACCEPTANCE CRITERIA",
            "source_acceptance_criteria",
        ),
        ("PHASE 10.37 SOURCE DECISION", "source_decision"),
        ("PHASE 10.37 SOURCE CHECKS", "source_checks"),
        ("PHASE 10.37 SOURCE MANIFEST", "source_manifest"),
        (
            "PHASE 10.37 SOURCE ARTIFACT MANIFEST",
            "source_artifact_manifest",
        ),
        ("DESIGN REVIEW VALIDATIONS", "validations"),
        ("DESIGN REVIEW ITEMS", "items"),
        ("DESIGN REVIEW FINDINGS", "findings"),
        ("DESIGN REVIEW CONTROLS", "controls"),
        ("DESIGN REVIEW RULES", "rules"),
        ("DESIGN REVIEW REQUIREMENTS", "requirements"),
        ("DESIGN REVIEW GUARD MATRIX", "guard_matrix"),
        ("DESIGN REVIEW DECISION", "decision"),
        ("VALIDATION CHECKS", "checks"),
        ("DESIGN REVIEW MANIFEST", "manifest"),
    ]

    for title, key in sections:
        print_section(title)
        print_df(result[key])

    print()
    print("ARCHIVOS GENERADOS")
    print("=" * 100)
    generated = [
        "official_dataset_schema_implementation_design_review_summary_v1.csv",
        "official_dataset_schema_implementation_design_review_validations_v1.csv",
        "official_dataset_schema_implementation_design_review_items_v1.csv",
        "official_dataset_schema_implementation_design_review_findings_v1.csv",
        "official_dataset_schema_implementation_design_review_controls_v1.csv",
        "official_dataset_schema_implementation_design_review_rules_v1.csv",
        "official_dataset_schema_implementation_design_review_requirements_v1.csv",
        "official_dataset_schema_implementation_design_review_guard_matrix_v1.csv",
        "official_dataset_schema_implementation_design_review_decision_v1.csv",
        "official_dataset_schema_implementation_design_review_checks_v1.csv",
        "source_official_dataset_schema_implementation_design_review_artifact_manifest_v1.csv",
    ]
    for filename in generated:
        print(
            "- reports/p10_38_evidence_collection_official_dataset_"
            f"schema_implementation_design_review_v1/{filename}"
        )

    print()
    print(
        "Restriccion: Phase 10.38 revisa solamente el diseno de "
        "Phase 10.37. No implementa, crea ni escribe el dataset "
        "oficial; no recolecta evidencia real y no habilita senales, "
        "alertas, paper trading, capital real, ejecucion o "
        "automatizacion."
    )


if __name__ == "__main__":
    main()
