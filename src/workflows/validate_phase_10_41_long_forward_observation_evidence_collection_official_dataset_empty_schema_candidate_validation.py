from __future__ import annotations

import pandas as pd

from src.long_side.long_forward_observation_phase_10_41_evidence_collection_official_dataset_empty_schema_candidate_validation_v1 import (
    run_long_forward_observation_evidence_collection_official_dataset_empty_schema_candidate_validation,
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
        "PHASE 10.41 LONG FORWARD OBSERVATION EVIDENCE COLLECTION "
        "OFFICIAL DATASET EMPTY SCHEMA CANDIDATE VALIDATION"
    )
    print("=" * 100)
    print(
        "Purpose: validate the tracked empty-schema candidate, its "
        "canonical 54-field contract, deterministic bytes, Git state "
        "and controlled rejection of corrupted variants."
    )
    print(
        "Restriction: validation-only. No candidate modification or "
        "promotion, no official dataset creation or write, no evidence "
        "collection or persistence, no signals, alerts, paper trading, "
        "real capital, execution or automation."
    )

    result = (
        run_long_forward_observation_evidence_collection_official_dataset_empty_schema_candidate_validation()
    )

    sections = [
        ("PHASE 10.41 VALIDATION SUMMARY", "summary"),
        (
            "PHASE 10.40 SOURCE IMPLEMENTATION SUMMARY",
            "source_implementation_summary",
        ),
        (
            "PHASE 10.40 SOURCE IMPLEMENTATION DECISION",
            "source_implementation_decision",
        ),
        ("PHASE 10.37 SOURCE FIELD CATALOG", "source_field_catalog"),
        ("SOURCE ARTIFACT MANIFEST", "source_artifact_manifest"),
        ("EMPTY SCHEMA CANDIDATE VALIDATION PROFILE", "candidate_profile"),
        ("CONTROLLED NEGATIVE VALIDATION CASES", "negative_controls"),
        ("CANDIDATE VALIDATIONS", "validations"),
        ("CANDIDATE VALIDATION ITEMS", "items"),
        ("CANDIDATE VALIDATION FINDINGS", "findings"),
        ("CANDIDATE VALIDATION CONTROLS", "controls"),
        ("CANDIDATE VALIDATION RULES", "rules"),
        ("CANDIDATE VALIDATION REQUIREMENTS", "requirements"),
        ("CANDIDATE VALIDATION GUARD MATRIX", "guard_matrix"),
        ("CANDIDATE VALIDATION DECISION", "decision"),
        ("VALIDATION CHECKS", "checks"),
        ("CANDIDATE VALIDATION MANIFEST", "manifest"),
    ]

    for title, key in sections:
        print_section(title)
        print_df(result[key])

    print()
    print("ARCHIVOS DE REPORTE GENERADOS")
    print("=" * 100)
    generated = [
        "official_dataset_empty_schema_candidate_validation_summary_v1.csv",
        "official_dataset_empty_schema_candidate_validation_validations_v1.csv",
        "official_dataset_empty_schema_candidate_validation_profile_v1.csv",
        "official_dataset_empty_schema_candidate_validation_negative_controls_v1.csv",
        "official_dataset_empty_schema_candidate_validation_items_v1.csv",
        "official_dataset_empty_schema_candidate_validation_findings_v1.csv",
        "official_dataset_empty_schema_candidate_validation_controls_v1.csv",
        "official_dataset_empty_schema_candidate_validation_rules_v1.csv",
        "official_dataset_empty_schema_candidate_validation_requirements_v1.csv",
        "official_dataset_empty_schema_candidate_validation_guard_matrix_v1.csv",
        "official_dataset_empty_schema_candidate_validation_decision_v1.csv",
        "official_dataset_empty_schema_candidate_validation_checks_v1.csv",
        "source_official_dataset_empty_schema_candidate_validation_artifact_manifest_v1.csv",
    ]
    for filename in generated:
        print(
            "- reports/p10_41_evidence_collection_official_dataset_"
            f"empty_schema_candidate_validation_v1/{filename}"
        )

    print()
    print(
        "Restriccion: Phase 10.41 valida sin modificar ni promover el "
        "candidato. No crea ni escribe el dataset oficial, no agrega "
        "filas de evidencia y no habilita senales, alertas, paper "
        "trading, capital real, ejecucion o automatizacion."
    )


if __name__ == "__main__":
    main()
