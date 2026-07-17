from __future__ import annotations

import pandas as pd

from src.long_side.long_forward_observation_phase_10_29_evidence_collection_design_v1 import (
    validate_long_forward_observation_evidence_collection_design,
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
        "PHASE 10.29 LONG FORWARD OBSERVATION "
        "EVIDENCE COLLECTION DESIGN"
    )
    print("=" * 100)
    print("Purpose: define the future LONG evidence collection contract.")
    print(
        "Restriction: design-only. No evidence collection, no official "
        "dataset implementation or write, no signals, no alerts, no "
        "paper trading, no real capital and no market execution."
    )

    result = validate_long_forward_observation_evidence_collection_design()

    sections = [
        ("PHASE 10.29 VALIDATION SUMMARY", "summary"),
        ("PHASE 10.28 SOURCE SUMMARY", "source_phase_10_28_summary"),
        ("PRESERVED PHASE 10.26 START OUTPUT", "source_start_output"),
        ("PHASE 10.28 SOURCE DESIGN REQUIREMENTS", "source_design_requirements"),
        ("PHASE 10.28 SOURCE VALIDATIONS", "source_validations"),
        ("PHASE 10.28 SOURCE EVIDENCE CHAIN", "source_evidence_chain"),
        ("PHASE 10.28 SOURCE CONTROLS", "source_controls"),
        ("PHASE 10.28 SOURCE RULES", "source_rules"),
        ("PHASE 10.28 SOURCE REQUIREMENTS", "source_requirements"),
        ("PHASE 10.28 SOURCE GUARD MATRIX", "source_guard_matrix"),
        ("PHASE 10.28 SOURCE DECISION", "source_decision"),
        ("PHASE 10.28 SOURCE CHECKS", "source_checks"),
        ("PHASE 10.28 SOURCE MANIFEST", "source_manifest"),
        ("SOURCE DESIGN ARTIFACT MANIFEST", "design_manifest"),
        ("EVIDENCE COLLECTION DESIGN SCHEMA", "design_schema"),
        ("EVIDENCE COLLECTION DESIGN COMPONENTS", "design_components"),
        ("ACCEPTED SOURCE RULES", "accepted_source_rules"),
        ("EVIDENCE LIFECYCLE STATES", "lifecycle_states"),
        ("DEDUPLICATION RULES", "deduplication_rules"),
        ("REJECTION RULES", "rejection_rules"),
        ("OFFICIAL WRITE GUARDS", "write_guards"),
        ("AUDIT REQUIREMENTS", "audit_requirements"),
        ("DESIGN BOUNDARY RULES", "boundary_rules"),
        ("EVIDENCE COLLECTION DESIGN VALIDATIONS", "design_validations"),
        ("EVIDENCE COLLECTION DESIGN EVIDENCE CHAIN", "design_evidence_chain"),
        ("EVIDENCE COLLECTION DESIGN CONTROLS", "design_controls"),
        ("EVIDENCE COLLECTION DESIGN RULES", "design_rules"),
        ("EVIDENCE COLLECTION DESIGN REQUIREMENTS", "design_requirements"),
        ("EVIDENCE COLLECTION DESIGN GUARD MATRIX", "design_guard_matrix"),
        ("EVIDENCE COLLECTION DESIGN DECISION", "design_decision"),
        ("VALIDATION CHECKS", "checks"),
    ]

    for title, key in sections:
        print_section(title)
        print_df(result[key])

    print()
    print("ARCHIVOS GENERADOS")
    print("=" * 100)

    generated_files = [
        "evidence_collection_design_summary_v1.csv",
        "phase_10_28_source_summary_v1.csv",
        "phase_10_26_source_start_output_v1.csv",
        "phase_10_28_source_design_requirements_v1.csv",
        "phase_10_28_source_validations_v1.csv",
        "phase_10_28_source_evidence_chain_v1.csv",
        "phase_10_28_source_controls_v1.csv",
        "phase_10_28_source_rules_v1.csv",
        "phase_10_28_source_requirements_v1.csv",
        "phase_10_28_source_guard_matrix_v1.csv",
        "phase_10_28_source_decision_v1.csv",
        "phase_10_28_source_checks_v1.csv",
        "phase_10_28_source_manifest_v1.csv",
        "source_design_artifact_manifest_v1.csv",
        "evidence_collection_design_schema_v1.csv",
        "evidence_collection_design_components_v1.csv",
        "evidence_collection_accepted_source_rules_v1.csv",
        "evidence_collection_lifecycle_states_v1.csv",
        "evidence_collection_deduplication_rules_v1.csv",
        "evidence_collection_rejection_rules_v1.csv",
        "evidence_collection_write_guards_v1.csv",
        "evidence_collection_audit_requirements_v1.csv",
        "evidence_collection_boundary_rules_v1.csv",
        "evidence_collection_design_validations_v1.csv",
        "evidence_collection_design_evidence_chain_v1.csv",
        "evidence_collection_design_controls_v1.csv",
        "evidence_collection_design_rules_v1.csv",
        "evidence_collection_design_requirements_v1.csv",
        "evidence_collection_design_guard_matrix_v1.csv",
        "evidence_collection_design_decision_v1.csv",
        "evidence_collection_design_checks_v1.csv",
    ]

    for filename in generated_files:
        print(f"- reports/p10_29_evidence_collection_design_v1/{filename}")

    print()
    print(
        "Restriccion: Phase 10.29 define solamente el contrato de "
        "recoleccion de evidencia. No recolecta evidencia, no implementa "
        "ni escribe el dataset oficial y no habilita senales, alertas, "
        "paper trading, capital real o ejecucion."
    )


if __name__ == "__main__":
    main()
