from __future__ import annotations

import pandas as pd

from src.long_side.long_forward_observation_phase_10_9_pre_start_gate_v1 import (
    validate_long_forward_observation_pre_start_gate,
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
    print("PHASE 10.9 LONG FORWARD OBSERVATION PRE-START GATE")
    print("=" * 100)
    print("Purpose: validate strict pre-start gate before any controlled LONG forward observation start review")
    print("Restriction: gate only. No forward observation start. No official evidence. No market execution.")
    print()

    result = validate_long_forward_observation_pre_start_gate()

    print_section("PHASE 10.9 VALIDATION SUMMARY")
    print_df(result["summary"])

    print_section("PHASE 10.8 SOURCE SUMMARY")
    print_df(result["source_phase_10_8_summary"])

    print_section("SOURCE OUTPUT SCHEMA INTEGRITY")
    print_df(result["source_output_schema_integrity"])

    print_section("SOURCE OUTPUT ROW INTEGRITY")
    print_df(result["source_output_row_integrity"])

    print_section("SOURCE SUMMARY GUARD INTEGRITY")
    print_df(result["source_summary_guard_integrity"])

    print_section("SOURCE OUTPUT INTEGRITY REQUIREMENTS")
    print_df(result["source_output_integrity_requirements"])

    print_section("SOURCE OUTPUT INTEGRITY BOUNDARY MATRIX")
    print_df(result["source_output_integrity_boundary_matrix"])

    print_section("SOURCE OUTPUT INTEGRITY DECISION")
    print_df(result["source_output_integrity_decision"])

    print_section("SOURCE CHECKS")
    print_df(result["source_checks"])

    print_section("PRE-START DEPENDENCY MATRIX")
    print_df(result["pre_start_dependency_matrix"])

    print_section("PRE-START CONTROLS")
    print_df(result["pre_start_controls"])

    print_section("PRE-START RULES")
    print_df(result["pre_start_rules"])

    print_section("PRE-START REQUIREMENTS")
    print_df(result["pre_start_requirements"])

    print_section("PRE-START GUARD MATRIX")
    print_df(result["pre_start_guard_matrix"])

    print_section("PRE-START BOUNDARY MATRIX")
    print_df(result["pre_start_boundary_matrix"])

    print_section("PRE-START DECISION")
    print_df(result["pre_start_decision"])

    print_section("VALIDATION CHECKS")
    print_df(result["checks"])

    print()
    print("ARCHIVOS GENERADOS")
    print("=" * 100)
    print("- reports/phase_10_9_long_forward_observation_pre_start_gate_v1/long_forward_observation_pre_start_gate_summary_v1.csv")
    print("- reports/phase_10_9_long_forward_observation_pre_start_gate_v1/phase_10_8_source_summary_v1.csv")
    print("- reports/phase_10_9_long_forward_observation_pre_start_gate_v1/phase_10_8_source_output_schema_integrity_v1.csv")
    print("- reports/phase_10_9_long_forward_observation_pre_start_gate_v1/phase_10_8_source_output_row_integrity_v1.csv")
    print("- reports/phase_10_9_long_forward_observation_pre_start_gate_v1/phase_10_8_source_summary_guard_integrity_v1.csv")
    print("- reports/phase_10_9_long_forward_observation_pre_start_gate_v1/phase_10_8_source_output_integrity_requirements_v1.csv")
    print("- reports/phase_10_9_long_forward_observation_pre_start_gate_v1/phase_10_8_source_output_integrity_boundary_matrix_v1.csv")
    print("- reports/phase_10_9_long_forward_observation_pre_start_gate_v1/phase_10_8_source_output_integrity_decision_v1.csv")
    print("- reports/phase_10_9_long_forward_observation_pre_start_gate_v1/phase_10_8_source_checks_v1.csv")
    print("- reports/phase_10_9_long_forward_observation_pre_start_gate_v1/long_forward_observation_pre_start_gate_dependency_matrix_v1.csv")
    print("- reports/phase_10_9_long_forward_observation_pre_start_gate_v1/long_forward_observation_pre_start_gate_controls_v1.csv")
    print("- reports/phase_10_9_long_forward_observation_pre_start_gate_v1/long_forward_observation_pre_start_gate_rules_v1.csv")
    print("- reports/phase_10_9_long_forward_observation_pre_start_gate_v1/long_forward_observation_pre_start_gate_requirements_v1.csv")
    print("- reports/phase_10_9_long_forward_observation_pre_start_gate_v1/long_forward_observation_pre_start_gate_guard_matrix_v1.csv")
    print("- reports/phase_10_9_long_forward_observation_pre_start_gate_v1/long_forward_observation_pre_start_gate_boundary_matrix_v1.csv")
    print("- reports/phase_10_9_long_forward_observation_pre_start_gate_v1/long_forward_observation_pre_start_gate_decision_v1.csv")
    print("- reports/phase_10_9_long_forward_observation_pre_start_gate_v1/long_forward_observation_pre_start_gate_checks_v1.csv")
    print()
    print("Restriccion: Phase 10.9 valida solo gate pre-start; no inicia forward observation ni aprueba ejecucion de mercado.")


if __name__ == "__main__":
    main()
