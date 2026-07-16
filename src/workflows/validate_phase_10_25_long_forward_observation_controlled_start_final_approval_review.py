from __future__ import annotations

import pandas as pd

from src.long_side.long_forward_observation_phase_10_25_controlled_start_final_approval_review_v1 import (
    validate_long_forward_observation_controlled_start_final_approval_review,
)


def print_section(title: str) -> None:
    print()
    print(title)
    print("=" * 100)


def print_df(
    df: pd.DataFrame,
    max_rows: int | None = None,
) -> None:
    if df.empty:
        print("Sin registros.")
        return

    if max_rows is not None:
        print(df.head(max_rows).to_string(index=False))
        return

    print(df.to_string(index=False))


def main() -> None:
    print(
        "PHASE 10.25 LONG FORWARD OBSERVATION CONTROLLED START "
        "FINAL APPROVAL REVIEW"
    )
    print("=" * 100)
    print(
        "Purpose: perform the final approval review for a future "
        "controlled forward observation start run."
    )
    print(
        "Restriction: review only. No start run, no forward observation "
        "start, no official evidence, no signals, no alerts, no paper "
        "trading, no real capital, and no market execution."
    )

    result = (
        validate_long_forward_observation_controlled_start_final_approval_review()
    )

    print_section("PHASE 10.25 VALIDATION SUMMARY")
    print_df(result["summary"])

    print_section("PHASE 10.24 SOURCE SUMMARY")
    print_df(result["source_phase_10_24_summary"])

    print_section("SOURCE INTEGRITY REVIEW ARTIFACT MANIFEST")
    print_df(result["source_manifest"])

    print_section("SOURCE DRY-RUN OUTPUT")
    print_df(result["source_dry_run_output"])

    print_section("SOURCE DRY-RUN ARTIFACT METADATA")
    print_df(result["source_artifact_metadata"])

    print_section("SOURCE INTEGRITY VALIDATIONS")
    print_df(result["source_integrity_validations"])

    print_section("SOURCE INTEGRITY CONTROLS")
    print_df(result["source_integrity_controls"])

    print_section("SOURCE INTEGRITY RULES")
    print_df(result["source_integrity_rules"])

    print_section("SOURCE INTEGRITY REQUIREMENTS")
    print_df(result["source_integrity_requirements"])

    print_section("SOURCE INTEGRITY GUARD MATRIX")
    print_df(result["source_integrity_guard_matrix"])

    print_section("SOURCE INTEGRITY DECISION")
    print_df(result["source_integrity_decision"])

    print_section("SOURCE PHASE 10.24 CHECKS")
    print_df(result["source_checks"])

    print_section("FINAL APPROVAL VALIDATIONS")
    print_df(result["final_approval_validations"])

    print_section("FINAL APPROVAL EVIDENCE CHAIN")
    print_df(result["final_approval_evidence_chain"])

    print_section("FINAL APPROVAL CONTROLS")
    print_df(result["final_approval_controls"])

    print_section("FINAL APPROVAL RULES")
    print_df(result["final_approval_rules"])

    print_section("FINAL APPROVAL REQUIREMENTS")
    print_df(result["final_approval_requirements"])

    print_section("FINAL APPROVAL GUARD MATRIX")
    print_df(result["final_approval_guard_matrix"])

    print_section("FINAL APPROVAL DECISION")
    print_df(result["final_approval_decision"])

    print_section("VALIDATION CHECKS")
    print_df(result["checks"])

    print()
    print("ARCHIVOS GENERADOS")
    print("=" * 100)

    generated_files = [
        "start_final_approval_summary_v1.csv",
        "phase_10_24_source_summary_v1.csv",
        "phase_10_23_source_dry_run_output_v1.csv",
        "phase_10_24_source_artifact_metadata_v1.csv",
        "phase_10_24_source_integrity_validations_v1.csv",
        "phase_10_24_source_integrity_controls_v1.csv",
        "phase_10_24_source_integrity_rules_v1.csv",
        "phase_10_24_source_integrity_requirements_v1.csv",
        "phase_10_24_source_integrity_guard_matrix_v1.csv",
        "phase_10_24_source_integrity_decision_v1.csv",
        "phase_10_24_source_checks_v1.csv",
        "source_integrity_review_artifact_manifest_v1.csv",
        "start_final_approval_validations_v1.csv",
        "start_final_approval_evidence_chain_v1.csv",
        "start_final_approval_controls_v1.csv",
        "start_final_approval_rules_v1.csv",
        "start_final_approval_requirements_v1.csv",
        "start_final_approval_guard_matrix_v1.csv",
        "start_final_approval_decision_v1.csv",
        "start_final_approval_checks_v1.csv",
    ]

    for filename in generated_files:
        print(
            "- reports/p10_25_start_final_approval_review_v1/"
            f"{filename}"
        )

    print()
    print(
        "Restriccion: Phase 10.25 ejecuta solamente la revision final "
        "de aprobacion para un futuro start run controlado. No ejecuta "
        "el start run, no inicia forward observation, no persiste "
        "evidencia oficial ni habilita senales, alertas, paper trading, "
        "capital real o ejecucion."
    )


if __name__ == "__main__":
    main()
