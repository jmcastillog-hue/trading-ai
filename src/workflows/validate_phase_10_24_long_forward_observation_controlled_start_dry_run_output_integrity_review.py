from __future__ import annotations

import pandas as pd

from src.long_side.long_forward_observation_phase_10_24_controlled_start_dry_run_output_integrity_review_v1 import (
    validate_long_forward_observation_controlled_start_dry_run_output_integrity_review,
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
        "PHASE 10.24 LONG FORWARD OBSERVATION CONTROLLED START "
        "DRY-RUN OUTPUT INTEGRITY REVIEW"
    )
    print("=" * 100)
    print("Purpose: review integrity of the Phase 10.23 dry-run output.")
    print(
        "Restriction: no new dry-run, no forward observation start, "
        "no official evidence, no live signals, no alerts, no paper "
        "trading, no real capital, and no market execution."
    )

    result = (
        validate_long_forward_observation_controlled_start_dry_run_output_integrity_review()
    )

    print_section("PHASE 10.24 VALIDATION SUMMARY")
    print_df(result["summary"])

    print_section("PHASE 10.23 SOURCE SUMMARY")
    print_df(result["source_phase_10_23_summary"])

    print_section("SOURCE DRY-RUN ARTIFACT METADATA")
    print_df(result["source_artifact_metadata"])

    print_section("SOURCE DRY-RUN OUTPUT")
    print_df(result["source_dry_run_output"])

    print_section("SOURCE DRY-RUN VALIDATIONS")
    print_df(result["source_dry_run_validations"])

    print_section("SOURCE DRY-RUN EVIDENCE CHAIN")
    print_df(result["source_dry_run_evidence_chain"])

    print_section("SOURCE DRY-RUN CONTROLS")
    print_df(result["source_dry_run_controls"])

    print_section("SOURCE DRY-RUN RULES")
    print_df(result["source_dry_run_rules"])

    print_section("SOURCE DRY-RUN REQUIREMENTS")
    print_df(result["source_dry_run_requirements"])

    print_section("SOURCE DRY-RUN GUARD MATRIX")
    print_df(result["source_dry_run_guard_matrix"])

    print_section("SOURCE DRY-RUN DECISION")
    print_df(result["source_dry_run_decision"])

    print_section("SOURCE PHASE 10.23 CHECKS")
    print_df(result["source_checks"])

    print_section("OUTPUT INTEGRITY VALIDATIONS")
    print_df(result["integrity_validations"])

    print_section("OUTPUT INTEGRITY CONTROLS")
    print_df(result["integrity_controls"])

    print_section("OUTPUT INTEGRITY RULES")
    print_df(result["integrity_rules"])

    print_section("OUTPUT INTEGRITY REQUIREMENTS")
    print_df(result["integrity_requirements"])

    print_section("OUTPUT INTEGRITY GUARD MATRIX")
    print_df(result["integrity_guard_matrix"])

    print_section("OUTPUT INTEGRITY DECISION")
    print_df(result["integrity_decision"])

    print_section("VALIDATION CHECKS")
    print_df(result["checks"])

    print()
    print("ARCHIVOS GENERADOS")
    print("=" * 100)
    generated_files = [
        "start_dry_run_output_integrity_summary_v1.csv",
        "phase_10_23_source_summary_v1.csv",
        "phase_10_23_source_dry_run_output_v1.csv",
        "phase_10_23_source_dry_run_validations_v1.csv",
        "phase_10_23_source_dry_run_evidence_chain_v1.csv",
        "phase_10_23_source_dry_run_controls_v1.csv",
        "phase_10_23_source_dry_run_rules_v1.csv",
        "phase_10_23_source_dry_run_requirements_v1.csv",
        "phase_10_23_source_dry_run_guard_matrix_v1.csv",
        "phase_10_23_source_dry_run_decision_v1.csv",
        "phase_10_23_source_checks_v1.csv",
        "source_dry_run_artifact_metadata_v1.csv",
        "start_dry_run_output_integrity_validations_v1.csv",
        "start_dry_run_output_integrity_controls_v1.csv",
        "start_dry_run_output_integrity_rules_v1.csv",
        "start_dry_run_output_integrity_requirements_v1.csv",
        "start_dry_run_output_integrity_guard_matrix_v1.csv",
        "start_dry_run_output_integrity_decision_v1.csv",
        "start_dry_run_output_integrity_checks_v1.csv",
    ]

    for filename in generated_files:
        print(
            "- reports/p10_24_start_dry_run_output_integrity_review_v1/"
            f"{filename}"
        )

    print()
    print(
        "Restriccion: Phase 10.24 revisa solamente la integridad del "
        "dry-run de Phase 10.23. No ejecuta un nuevo dry-run, no inicia "
        "forward observation, no persiste evidencia oficial ni habilita "
        "senales, alertas, paper trading, capital real o ejecucion."
    )


if __name__ == "__main__":
    main()
