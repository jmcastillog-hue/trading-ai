from __future__ import annotations

import pandas as pd

from src.long_side.long_forward_observation_phase_10_39_evidence_collection_official_dataset_schema_implementation_precheck_v1 import (
    run_long_forward_observation_evidence_collection_official_dataset_schema_implementation_precheck,
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
        "PHASE 10.39 LONG FORWARD OBSERVATION EVIDENCE COLLECTION "
        "OFFICIAL DATASET SCHEMA IMPLEMENTATION PRECHECK"
    )
    print("=" * 100)
    print(
        "Purpose: validate the reviewed schema contract, planned paths "
        "and local prerequisites for a later empty-schema candidate implementation."
    )
    print(
        "Restriction: precheck-only. No official or candidate dataset creation, "
        "no dataset writes, no evidence collection or persistence, no signals, "
        "alerts, paper trading, real capital, execution or automation."
    )

    result = run_long_forward_observation_evidence_collection_official_dataset_schema_implementation_precheck()

    sections = [
        ("PHASE 10.39 VALIDATION SUMMARY", "summary"),
        ("PHASE 10.38 SOURCE REVIEW SUMMARY", "source_review_summary"),
        ("PHASE 10.38 SOURCE REVIEW DECISION", "source_review_decision"),
        ("PHASE 10.37 SOURCE DESIGN SUMMARY", "source_design_summary"),
        ("PHASE 10.37 SOURCE FIELD CATALOG", "source_field_catalog"),
        ("PHASE 10.37 SOURCE MIGRATION PLAN", "source_migration_plan"),
        ("SOURCE ARTIFACT MANIFEST", "source_artifact_manifest"),
        ("IMPLEMENTATION PRECHECK VALIDATIONS", "validations"),
        ("IMPLEMENTATION PRECHECK ITEMS", "items"),
        ("IMPLEMENTATION PRECHECK FINDINGS", "findings"),
        ("IMPLEMENTATION PRECHECK CONTROLS", "controls"),
        ("IMPLEMENTATION PRECHECK RULES", "rules"),
        ("IMPLEMENTATION PRECHECK REQUIREMENTS", "requirements"),
        ("IMPLEMENTATION PRECHECK GUARD MATRIX", "guard_matrix"),
        ("IMPLEMENTATION PATH PLAN", "path_plan"),
        ("IMPLEMENTATION PRECHECK DECISION", "decision"),
        ("VALIDATION CHECKS", "checks"),
        ("IMPLEMENTATION PRECHECK MANIFEST", "manifest"),
    ]

    for title, key in sections:
        print_section(title)
        print_df(result[key])

    print()
    print("ARCHIVOS GENERADOS")
    print("=" * 100)
    generated = [
        "official_dataset_schema_implementation_precheck_summary_v1.csv",
        "official_dataset_schema_implementation_precheck_validations_v1.csv",
        "official_dataset_schema_implementation_precheck_items_v1.csv",
        "official_dataset_schema_implementation_precheck_findings_v1.csv",
        "official_dataset_schema_implementation_precheck_controls_v1.csv",
        "official_dataset_schema_implementation_precheck_rules_v1.csv",
        "official_dataset_schema_implementation_precheck_requirements_v1.csv",
        "official_dataset_schema_implementation_precheck_guard_matrix_v1.csv",
        "official_dataset_schema_implementation_precheck_path_plan_v1.csv",
        "official_dataset_schema_implementation_precheck_decision_v1.csv",
        "official_dataset_schema_implementation_precheck_checks_v1.csv",
        "source_official_dataset_schema_implementation_precheck_artifact_manifest_v1.csv",
    ]
    for filename in generated:
        print(
            "- reports/p10_39_evidence_collection_official_dataset_"
            f"schema_implementation_precheck_v1/{filename}"
        )

    print()
    print(
        "Restriccion: Phase 10.39 ejecuta solamente un precheck. "
        "No crea el dataset oficial ni el candidato de esquema vacio, "
        "no escribe filas, no recolecta evidencia real y no habilita "
        "senales, alertas, paper trading, capital real, ejecucion o automatizacion."
    )


if __name__ == "__main__":
    main()
