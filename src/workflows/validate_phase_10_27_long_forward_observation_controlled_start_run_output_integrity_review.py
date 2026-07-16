from __future__ import annotations

import pandas as pd

from src.long_side.long_forward_observation_phase_10_27_controlled_start_run_output_integrity_review_v1 import (
    validate_long_forward_observation_controlled_start_run_output_integrity_review,
)


def print_section(title: str) -> None:
    print()
    print(title)
    print("=" * 100)


def print_df(df: pd.DataFrame, max_rows: int | None = None) -> None:
    if df.empty:
        print("Sin registros.")
        return
    if max_rows is not None:
        print(df.head(max_rows).to_string(index=False))
        return
    print(df.to_string(index=False))


def main() -> None:
    print(
        "PHASE 10.27 LONG FORWARD OBSERVATION CONTROLLED START RUN "
        "OUTPUT INTEGRITY REVIEW"
    )
    print("=" * 100)
    print(
        "Purpose: review the integrity of the Phase 10.26 controlled "
        "start output and supporting artifacts."
    )
    print(
        "Restriction: integrity review only. No second start run, no "
        "evidence collection, no official dataset write, no signals, "
        "no alerts, no paper trading, no real capital, and no market "
        "execution."
    )

    result = (
        validate_long_forward_observation_controlled_start_run_output_integrity_review()
    )

    sections = [
        ("PHASE 10.27 VALIDATION SUMMARY", "summary"),
        ("PHASE 10.26 SOURCE SUMMARY", "source_phase_10_26_summary"),
        ("PHASE 10.26 SOURCE START OUTPUT", "source_start_output"),
        ("PHASE 10.26 SOURCE VALIDATIONS", "source_validations"),
        ("PHASE 10.26 SOURCE EVIDENCE CHAIN", "source_evidence_chain"),
        ("PHASE 10.26 SOURCE CONTROLS", "source_controls"),
        ("PHASE 10.26 SOURCE RULES", "source_rules"),
        ("PHASE 10.26 SOURCE REQUIREMENTS", "source_requirements"),
        ("PHASE 10.26 SOURCE GUARD MATRIX", "source_guard_matrix"),
        ("PHASE 10.26 SOURCE DECISION", "source_decision"),
        ("PHASE 10.26 SOURCE CHECKS", "source_checks"),
        ("SOURCE START-RUN ARTIFACT MANIFEST", "source_manifest"),
        ("OUTPUT INTEGRITY VALIDATIONS", "integrity_validations"),
        ("OUTPUT INTEGRITY EVIDENCE CHAIN", "integrity_evidence_chain"),
        ("OUTPUT INTEGRITY CONTROLS", "integrity_controls"),
        ("OUTPUT INTEGRITY RULES", "integrity_rules"),
        ("OUTPUT INTEGRITY REQUIREMENTS", "integrity_requirements"),
        ("OUTPUT INTEGRITY GUARD MATRIX", "integrity_guard_matrix"),
        ("OUTPUT INTEGRITY DECISION", "integrity_decision"),
        ("VALIDATION CHECKS", "checks"),
    ]

    for title, key in sections:
        print_section(title)
        print_df(result[key])

    print()
    print("ARCHIVOS GENERADOS")
    print("=" * 100)
    generated_files = [
        "start_run_output_integrity_summary_v1.csv",
        "phase_10_26_source_summary_v1.csv",
        "phase_10_26_source_start_output_v1.csv",
        "phase_10_26_source_validations_v1.csv",
        "phase_10_26_source_evidence_chain_v1.csv",
        "phase_10_26_source_controls_v1.csv",
        "phase_10_26_source_rules_v1.csv",
        "phase_10_26_source_requirements_v1.csv",
        "phase_10_26_source_guard_matrix_v1.csv",
        "phase_10_26_source_decision_v1.csv",
        "phase_10_26_source_checks_v1.csv",
        "source_start_run_artifact_manifest_v1.csv",
        "start_run_output_integrity_validations_v1.csv",
        "start_run_output_integrity_evidence_chain_v1.csv",
        "start_run_output_integrity_controls_v1.csv",
        "start_run_output_integrity_rules_v1.csv",
        "start_run_output_integrity_requirements_v1.csv",
        "start_run_output_integrity_guard_matrix_v1.csv",
        "start_run_output_integrity_decision_v1.csv",
        "start_run_output_integrity_checks_v1.csv",
    ]
    for filename in generated_files:
        print(
            "- reports/"
            "p10_27_controlled_start_run_output_integrity_review_v1/"
            f"{filename}"
        )

    print()
    print(
        "Restriccion: Phase 10.27 revisa solamente la integridad del "
        "output de Phase 10.26. Mantiene iniciado el estado controlado "
        "de observacion, pero no ejecuta un segundo start run, no "
        "habilita recoleccion de evidencia, no escribe el dataset "
        "oficial ni habilita senales, alertas, paper trading, capital "
        "real o ejecucion."
    )


if __name__ == "__main__":
    main()
