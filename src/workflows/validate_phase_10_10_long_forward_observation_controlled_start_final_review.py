from __future__ import annotations

import pandas as pd

from src.long_side.long_forward_observation_phase_10_10_controlled_start_final_review_v1 import (
    validate_long_forward_observation_controlled_start_final_review,
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
    print("PHASE 10.10 LONG FORWARD OBSERVATION CONTROLLED START FINAL REVIEW")
    print("=" * 100)
    print("Purpose: validate final review before any future controlled LONG forward observation activation phase")
    print("Restriction: final review only. No forward observation start. No official evidence. No market execution.")
    print()

    result = validate_long_forward_observation_controlled_start_final_review()

    print_section("PHASE 10.10 VALIDATION SUMMARY")
    print_df(result["summary"])

    print_section("PHASE 10.9 SOURCE SUMMARY")
    print_df(result["source_phase_10_9_summary"])

    print_section("SOURCE PRE-START DEPENDENCY MATRIX")
    print_df(result["source_pre_start_dependency_matrix"])

    print_section("SOURCE PRE-START CONTROLS")
    print_df(result["source_pre_start_controls"])

    print_section("SOURCE PRE-START RULES")
    print_df(result["source_pre_start_rules"])

    print_section("SOURCE PRE-START REQUIREMENTS")
    print_df(result["source_pre_start_requirements"])

    print_section("SOURCE PRE-START GUARD MATRIX")
    print_df(result["source_pre_start_guard_matrix"])

    print_section("SOURCE PRE-START BOUNDARY MATRIX")
    print_df(result["source_pre_start_boundary_matrix"])

    print_section("SOURCE PRE-START DECISION")
    print_df(result["source_pre_start_decision"])

    print_section("SOURCE CHECKS")
    print_df(result["source_checks"])

    print_section("FINAL REVIEW DEPENDENCY MATRIX")
    print_df(result["final_review_dependency_matrix"])

    print_section("FINAL REVIEW CONTROLS")
    print_df(result["final_review_controls"])

    print_section("FINAL REVIEW RULES")
    print_df(result["final_review_rules"])

    print_section("FINAL REVIEW REQUIREMENTS")
    print_df(result["final_review_requirements"])

    print_section("FINAL REVIEW GUARD MATRIX")
    print_df(result["final_review_guard_matrix"])

    print_section("FINAL REVIEW BOUNDARY MATRIX")
    print_df(result["final_review_boundary_matrix"])

    print_section("FINAL REVIEW DECISION")
    print_df(result["final_review_decision"])

    print_section("VALIDATION CHECKS")
    print_df(result["checks"])

    print()
    print("ARCHIVOS GENERADOS")
    print("=" * 100)
    print("- reports/phase_10_10_long_forward_observation_controlled_start_final_review_v1/long_forward_observation_controlled_start_final_review_summary_v1.csv")
    print("- reports/phase_10_10_long_forward_observation_controlled_start_final_review_v1/phase_10_9_source_summary_v1.csv")
    print("- reports/phase_10_10_long_forward_observation_controlled_start_final_review_v1/phase_10_9_source_pre_start_dependency_matrix_v1.csv")
    print("- reports/phase_10_10_long_forward_observation_controlled_start_final_review_v1/phase_10_9_source_pre_start_controls_v1.csv")
    print("- reports/phase_10_10_long_forward_observation_controlled_start_final_review_v1/phase_10_9_source_pre_start_rules_v1.csv")
    print("- reports/phase_10_10_long_forward_observation_controlled_start_final_review_v1/phase_10_9_source_pre_start_requirements_v1.csv")
    print("- reports/phase_10_10_long_forward_observation_controlled_start_final_review_v1/phase_10_9_source_pre_start_guard_matrix_v1.csv")
    print("- reports/phase_10_10_long_forward_observation_controlled_start_final_review_v1/phase_10_9_source_pre_start_boundary_matrix_v1.csv")
    print("- reports/phase_10_10_long_forward_observation_controlled_start_final_review_v1/phase_10_9_source_pre_start_decision_v1.csv")
    print("- reports/phase_10_10_long_forward_observation_controlled_start_final_review_v1/phase_10_9_source_checks_v1.csv")
    print("- reports/phase_10_10_long_forward_observation_controlled_start_final_review_v1/long_forward_observation_controlled_start_final_review_dependency_matrix_v1.csv")
    print("- reports/phase_10_10_long_forward_observation_controlled_start_final_review_v1/long_forward_observation_controlled_start_final_review_controls_v1.csv")
    print("- reports/phase_10_10_long_forward_observation_controlled_start_final_review_v1/long_forward_observation_controlled_start_final_review_rules_v1.csv")
    print("- reports/phase_10_10_long_forward_observation_controlled_start_final_review_v1/long_forward_observation_controlled_start_final_review_requirements_v1.csv")
    print("- reports/phase_10_10_long_forward_observation_controlled_start_final_review_v1/long_forward_observation_controlled_start_final_review_guard_matrix_v1.csv")
    print("- reports/phase_10_10_long_forward_observation_controlled_start_final_review_v1/long_forward_observation_controlled_start_final_review_boundary_matrix_v1.csv")
    print("- reports/phase_10_10_long_forward_observation_controlled_start_final_review_v1/long_forward_observation_controlled_start_final_review_decision_v1.csv")
    print("- reports/phase_10_10_long_forward_observation_controlled_start_final_review_v1/long_forward_observation_controlled_start_final_review_checks_v1.csv")
    print()
    print("Restriccion: Phase 10.10 valida solo revision final; no inicia forward observation ni aprueba ejecucion de mercado.")


if __name__ == "__main__":
    main()