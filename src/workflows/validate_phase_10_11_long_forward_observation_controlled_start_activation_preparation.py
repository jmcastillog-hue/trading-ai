from __future__ import annotations

import pandas as pd

from src.long_side.long_forward_observation_phase_10_11_controlled_start_activation_preparation_v1 import (
    validate_long_forward_observation_controlled_start_activation_preparation,
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
    print("PHASE 10.11 LONG FORWARD OBSERVATION CONTROLLED START ACTIVATION PREPARATION")
    print("=" * 100)
    print("Purpose: prepare controlled start activation structure for a future dry-run review")
    print("Restriction: preparation only. No forward observation start. No official evidence. No market execution.")
    print()

    result = validate_long_forward_observation_controlled_start_activation_preparation()

    print_section("PHASE 10.11 VALIDATION SUMMARY")
    print_df(result["summary"])

    print_section("PHASE 10.10 SOURCE SUMMARY")
    print_df(result["source_phase_10_10_summary"])

    print_section("SOURCE FINAL REVIEW DEPENDENCY MATRIX")
    print_df(result["source_final_review_dependency_matrix"])

    print_section("SOURCE FINAL REVIEW CONTROLS")
    print_df(result["source_final_review_controls"])

    print_section("SOURCE FINAL REVIEW RULES")
    print_df(result["source_final_review_rules"])

    print_section("SOURCE FINAL REVIEW REQUIREMENTS")
    print_df(result["source_final_review_requirements"])

    print_section("SOURCE FINAL REVIEW GUARD MATRIX")
    print_df(result["source_final_review_guard_matrix"])

    print_section("SOURCE FINAL REVIEW BOUNDARY MATRIX")
    print_df(result["source_final_review_boundary_matrix"])

    print_section("SOURCE FINAL REVIEW DECISION")
    print_df(result["source_final_review_decision"])

    print_section("SOURCE CHECKS")
    print_df(result["source_checks"])

    print_section("ACTIVATION PREPARATION STEPS")
    print_df(result["activation_preparation_steps"])

    print_section("ACTIVATION PREPARATION CONTROLS")
    print_df(result["activation_preparation_controls"])

    print_section("ACTIVATION PREPARATION RULES")
    print_df(result["activation_preparation_rules"])

    print_section("ACTIVATION PREPARATION REQUIREMENTS")
    print_df(result["activation_preparation_requirements"])

    print_section("ACTIVATION PREPARATION GUARD MATRIX")
    print_df(result["activation_preparation_guard_matrix"])

    print_section("ACTIVATION PREPARATION BOUNDARY MATRIX")
    print_df(result["activation_preparation_boundary_matrix"])

    print_section("ACTIVATION PREPARATION DECISION")
    print_df(result["activation_preparation_decision"])

    print_section("VALIDATION CHECKS")
    print_df(result["checks"])

    print()
    print("ARCHIVOS GENERADOS")
    print("=" * 100)
    print("- reports/phase_10_11_long_forward_observation_controlled_start_activation_preparation_v1/long_forward_observation_controlled_start_activation_preparation_summary_v1.csv")
    print("- reports/phase_10_11_long_forward_observation_controlled_start_activation_preparation_v1/phase_10_10_source_summary_v1.csv")
    print("- reports/phase_10_11_long_forward_observation_controlled_start_activation_preparation_v1/phase_10_10_source_final_review_dependency_matrix_v1.csv")
    print("- reports/phase_10_11_long_forward_observation_controlled_start_activation_preparation_v1/phase_10_10_source_final_review_controls_v1.csv")
    print("- reports/phase_10_11_long_forward_observation_controlled_start_activation_preparation_v1/phase_10_10_source_final_review_rules_v1.csv")
    print("- reports/phase_10_11_long_forward_observation_controlled_start_activation_preparation_v1/phase_10_10_source_final_review_requirements_v1.csv")
    print("- reports/phase_10_11_long_forward_observation_controlled_start_activation_preparation_v1/phase_10_10_source_final_review_guard_matrix_v1.csv")
    print("- reports/phase_10_11_long_forward_observation_controlled_start_activation_preparation_v1/phase_10_10_source_final_review_boundary_matrix_v1.csv")
    print("- reports/phase_10_11_long_forward_observation_controlled_start_activation_preparation_v1/phase_10_10_source_final_review_decision_v1.csv")
    print("- reports/phase_10_11_long_forward_observation_controlled_start_activation_preparation_v1/phase_10_10_source_checks_v1.csv")
    print("- reports/phase_10_11_long_forward_observation_controlled_start_activation_preparation_v1/long_forward_observation_controlled_start_activation_preparation_steps_v1.csv")
    print("- reports/phase_10_11_long_forward_observation_controlled_start_activation_preparation_v1/long_forward_observation_controlled_start_activation_preparation_controls_v1.csv")
    print("- reports/phase_10_11_long_forward_observation_controlled_start_activation_preparation_v1/long_forward_observation_controlled_start_activation_preparation_rules_v1.csv")
    print("- reports/phase_10_11_long_forward_observation_controlled_start_activation_preparation_v1/long_forward_observation_controlled_start_activation_preparation_requirements_v1.csv")
    print("- reports/phase_10_11_long_forward_observation_controlled_start_activation_preparation_v1/long_forward_observation_controlled_start_activation_preparation_guard_matrix_v1.csv")
    print("- reports/phase_10_11_long_forward_observation_controlled_start_activation_preparation_v1/long_forward_observation_controlled_start_activation_preparation_boundary_matrix_v1.csv")
    print("- reports/phase_10_11_long_forward_observation_controlled_start_activation_preparation_v1/long_forward_observation_controlled_start_activation_preparation_decision_v1.csv")
    print("- reports/phase_10_11_long_forward_observation_controlled_start_activation_preparation_v1/long_forward_observation_controlled_start_activation_preparation_checks_v1.csv")
    print()
    print("Restriccion: Phase 10.11 valida solo preparacion de activacion; no inicia forward observation ni aprueba ejecucion de mercado.")


if __name__ == "__main__":
    main()