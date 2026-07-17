from __future__ import annotations

import pandas as pd

from src.long_side.long_forward_observation_phase_10_28_evidence_collection_precheck_v1 import (
    validate_long_forward_observation_evidence_collection_precheck,
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
    print("PHASE 10.28 LONG FORWARD OBSERVATION EVIDENCE COLLECTION PRECHECK")
    print("=" * 100)
    print("Purpose: verify readiness for a future evidence collection design phase.")
    print("Restriction: precheck only. No evidence collection, official dataset write, signals, alerts, paper trading, real capital or market execution.")

    result = validate_long_forward_observation_evidence_collection_precheck()

    sections = [
        ("PHASE 10.28 VALIDATION SUMMARY", "summary"),
        ("PHASE 10.27 SOURCE SUMMARY", "source_phase_10_27_summary"),
        ("PRESERVED PHASE 10.26 START OUTPUT", "source_start_output"),
        ("PHASE 10.27 SOURCE VALIDATIONS", "source_validations"),
        ("PHASE 10.27 SOURCE EVIDENCE CHAIN", "source_evidence_chain"),
        ("PHASE 10.27 SOURCE CONTROLS", "source_controls"),
        ("PHASE 10.27 SOURCE RULES", "source_rules"),
        ("PHASE 10.27 SOURCE REQUIREMENTS", "source_requirements"),
        ("PHASE 10.27 SOURCE GUARD MATRIX", "source_guard_matrix"),
        ("PHASE 10.27 SOURCE DECISION", "source_decision"),
        ("PHASE 10.27 SOURCE CHECKS", "source_checks"),
        ("PHASE 10.27 SOURCE MANIFEST", "source_manifest"),
        ("PRECHECK SOURCE ARTIFACT MANIFEST", "precheck_manifest"),
        ("FUTURE EVIDENCE COLLECTION DESIGN REQUIREMENTS", "design_requirements"),
        ("EVIDENCE COLLECTION PRECHECK VALIDATIONS", "precheck_validations"),
        ("EVIDENCE COLLECTION PRECHECK EVIDENCE CHAIN", "precheck_evidence_chain"),
        ("EVIDENCE COLLECTION PRECHECK CONTROLS", "precheck_controls"),
        ("EVIDENCE COLLECTION PRECHECK RULES", "precheck_rules"),
        ("EVIDENCE COLLECTION PRECHECK REQUIREMENTS", "precheck_requirements"),
        ("EVIDENCE COLLECTION PRECHECK GUARD MATRIX", "precheck_guard_matrix"),
        ("EVIDENCE COLLECTION PRECHECK DECISION", "precheck_decision"),
        ("VALIDATION CHECKS", "checks"),
    ]
    for title, key in sections:
        print_section(title)
        print_df(result[key])

    print()
    print("ARCHIVOS GENERADOS")
    print("=" * 100)
    for filename in [
        "evidence_collection_precheck_summary_v1.csv",
        "phase_10_27_source_summary_v1.csv",
        "phase_10_26_source_start_output_v1.csv",
        "phase_10_27_source_validations_v1.csv",
        "phase_10_27_source_evidence_chain_v1.csv",
        "phase_10_27_source_controls_v1.csv",
        "phase_10_27_source_rules_v1.csv",
        "phase_10_27_source_requirements_v1.csv",
        "phase_10_27_source_guard_matrix_v1.csv",
        "phase_10_27_source_decision_v1.csv",
        "phase_10_27_source_checks_v1.csv",
        "phase_10_27_source_manifest_v1.csv",
        "source_precheck_artifact_manifest_v1.csv",
        "evidence_collection_design_requirements_v1.csv",
        "evidence_collection_precheck_validations_v1.csv",
        "evidence_collection_precheck_evidence_chain_v1.csv",
        "evidence_collection_precheck_controls_v1.csv",
        "evidence_collection_precheck_rules_v1.csv",
        "evidence_collection_precheck_requirements_v1.csv",
        "evidence_collection_precheck_guard_matrix_v1.csv",
        "evidence_collection_precheck_decision_v1.csv",
        "evidence_collection_precheck_checks_v1.csv",
    ]:
        print(f"- reports/p10_28_evidence_collection_precheck_v1/{filename}")

    print()
    print("Restriccion: Phase 10.28 ejecuta solamente un precheck. Mantiene iniciado el estado controlado de observacion, pero no habilita recoleccion de evidencia, no escribe el dataset oficial ni habilita senales, alertas, paper trading, capital real o ejecucion.")


if __name__ == "__main__":
    main()
