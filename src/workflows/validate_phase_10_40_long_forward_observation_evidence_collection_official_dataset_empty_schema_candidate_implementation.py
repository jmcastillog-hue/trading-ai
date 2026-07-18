from __future__ import annotations

import pandas as pd

from src.long_side.long_forward_observation_phase_10_40_evidence_collection_official_dataset_empty_schema_candidate_implementation_v1 import (
    run_long_forward_observation_evidence_collection_official_dataset_empty_schema_candidate_implementation,
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
        "PHASE 10.40 LONG FORWARD OBSERVATION EVIDENCE COLLECTION "
        "OFFICIAL DATASET EMPTY SCHEMA CANDIDATE IMPLEMENTATION"
    )
    print("=" * 100)
    print(
        "Purpose: create a separate, atomic and idempotent empty-schema "
        "candidate with the exact 54-field canonical header and zero rows."
    )
    print(
        "Restriction: candidate-only. No official dataset creation or write, "
        "no evidence collection or persistence, no signals, alerts, paper "
        "trading, real capital, execution or automation."
    )

    result = (
        run_long_forward_observation_evidence_collection_official_dataset_empty_schema_candidate_implementation()
    )

    sections = [
        ("PHASE 10.40 VALIDATION SUMMARY", "summary"),
        ("PHASE 10.39 SOURCE PRECHECK SUMMARY", "source_precheck_summary"),
        ("PHASE 10.39 SOURCE PRECHECK DECISION", "source_precheck_decision"),
        ("PHASE 10.37 SOURCE FIELD CATALOG", "source_field_catalog"),
        ("SOURCE ARTIFACT MANIFEST", "source_artifact_manifest"),
        ("CANDIDATE IMPLEMENTATION VALIDATIONS", "validations"),
        ("EMPTY SCHEMA CANDIDATE PROFILE", "candidate_profile"),
        ("CANDIDATE IMPLEMENTATION ITEMS", "items"),
        ("CANDIDATE IMPLEMENTATION FINDINGS", "findings"),
        ("CANDIDATE IMPLEMENTATION CONTROLS", "controls"),
        ("CANDIDATE IMPLEMENTATION RULES", "rules"),
        ("CANDIDATE IMPLEMENTATION REQUIREMENTS", "requirements"),
        ("CANDIDATE IMPLEMENTATION GUARD MATRIX", "guard_matrix"),
        ("CANDIDATE IMPLEMENTATION DECISION", "decision"),
        ("VALIDATION CHECKS", "checks"),
        ("CANDIDATE IMPLEMENTATION MANIFEST", "manifest"),
    ]

    for title, key in sections:
        print_section(title)
        print_df(result[key])

    print()
    print("ARCHIVO CANDIDATO")
    print("=" * 100)
    print(
        "- data/forward/candidates/"
        "long_forward_observation_dataset_v1.empty_candidate.csv"
    )

    print()
    print("ARCHIVOS DE REPORTE GENERADOS")
    print("=" * 100)
    generated = [
        "official_dataset_empty_schema_candidate_implementation_summary_v1.csv",
        "official_dataset_empty_schema_candidate_implementation_validations_v1.csv",
        "official_dataset_empty_schema_candidate_profile_v1.csv",
        "official_dataset_empty_schema_candidate_implementation_items_v1.csv",
        "official_dataset_empty_schema_candidate_implementation_findings_v1.csv",
        "official_dataset_empty_schema_candidate_implementation_controls_v1.csv",
        "official_dataset_empty_schema_candidate_implementation_rules_v1.csv",
        "official_dataset_empty_schema_candidate_implementation_requirements_v1.csv",
        "official_dataset_empty_schema_candidate_implementation_guard_matrix_v1.csv",
        "official_dataset_empty_schema_candidate_implementation_decision_v1.csv",
        "official_dataset_empty_schema_candidate_implementation_checks_v1.csv",
        "source_official_dataset_empty_schema_candidate_implementation_artifact_manifest_v1.csv",
    ]
    for filename in generated:
        print(
            "- reports/p10_40_evidence_collection_official_dataset_"
            f"empty_schema_candidate_implementation_v1/{filename}"
        )

    print()
    print(
        "Restriccion: Phase 10.40 crea solamente un candidato de esquema "
        "vacio con cero filas. No crea ni escribe el dataset oficial, no "
        "recolecta evidencia real y no habilita senales, alertas, paper "
        "trading, capital real, ejecucion o automatizacion."
    )


if __name__ == "__main__":
    main()
