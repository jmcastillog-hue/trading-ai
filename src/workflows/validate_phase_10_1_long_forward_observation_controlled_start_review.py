from __future__ import annotations

import pandas as pd

from src.long_side.long_forward_observation_controlled_start_review_v1 import (
    validate_long_forward_observation_controlled_start_review,
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
    print("PHASE 10.1 LONG FORWARD OBSERVATION CONTROLLED START REVIEW")
    print("=" * 100)
    print("Purpose: review readiness for future manual LONG forward observation protocol")
    print("Restriction: review only. No forward observation start. No execution.")
    print()

    result = validate_long_forward_observation_controlled_start_review()

    print_section("PHASE 10.1 VALIDATION SUMMARY")
    print_df(result["summary"])

    print_section("PHASE 9.10 SOURCE SUMMARY")
    print_df(result["source_phase_9_10_summary"])

    print_section("SOURCE PHASE 9 CLOSURE LEDGER")
    print_df(result["source_phase_9_closure_ledger"])

    print_section("SOURCE PHASE 9 CLOSURE REQUIREMENTS")
    print_df(result["source_phase_9_closure_requirements"])

    print_section("SOURCE PHASE 9 SAFETY CLOSURE MATRIX")
    print_df(result["source_phase_9_safety_closure_matrix"])

    print_section("SOURCE PHASE 9 CLOSURE DECISION")
    print_df(result["source_phase_9_closure_decision"])

    print_section("SOURCE CHECKS")
    print_df(result["source_checks"])

    print_section("CONTROLLED START REVIEW REQUIREMENTS")
    print_df(result["controlled_start_review_requirements"])

    print_section("CONTROLLED START REVIEW BOUNDARY MATRIX")
    print_df(result["controlled_start_review_boundary_matrix"])

    print_section("CONTROLLED START REVIEW SAFETY MATRIX")
    print_df(result["controlled_start_review_safety_matrix"])

    print_section("CONTROLLED START REVIEW DECISION")
    print_df(result["controlled_start_review_decision"])

    print_section("VALIDATION CHECKS")
    print_df(result["checks"])

    print()
    print("ARCHIVOS GENERADOS")
    print("=" * 100)
    print("- reports/phase_10_1_long_forward_observation_controlled_start_review_v1/long_forward_observation_controlled_start_review_summary_v1.csv")
    print("- reports/phase_10_1_long_forward_observation_controlled_start_review_v1/phase_9_10_source_summary_v1.csv")
    print("- reports/phase_10_1_long_forward_observation_controlled_start_review_v1/phase_9_10_source_closure_ledger_v1.csv")
    print("- reports/phase_10_1_long_forward_observation_controlled_start_review_v1/phase_9_10_source_closure_requirements_v1.csv")
    print("- reports/phase_10_1_long_forward_observation_controlled_start_review_v1/phase_9_10_source_safety_closure_matrix_v1.csv")
    print("- reports/phase_10_1_long_forward_observation_controlled_start_review_v1/phase_9_10_source_closure_decision_v1.csv")
    print("- reports/phase_10_1_long_forward_observation_controlled_start_review_v1/phase_9_10_source_checks_v1.csv")
    print("- reports/phase_10_1_long_forward_observation_controlled_start_review_v1/long_forward_observation_controlled_start_review_requirements_v1.csv")
    print("- reports/phase_10_1_long_forward_observation_controlled_start_review_v1/long_forward_observation_controlled_start_review_boundary_matrix_v1.csv")
    print("- reports/phase_10_1_long_forward_observation_controlled_start_review_v1/long_forward_observation_controlled_start_review_safety_matrix_v1.csv")
    print("- reports/phase_10_1_long_forward_observation_controlled_start_review_v1/long_forward_observation_controlled_start_review_decision_v1.csv")
    print("- reports/phase_10_1_long_forward_observation_controlled_start_review_v1/long_forward_observation_controlled_start_review_checks_v1.csv")
    print()
    print("Restriccion: Phase 10.1 revisa readiness; no inicia observacion forward ni aprueba ejecucion.")


if __name__ == "__main__":
    main()