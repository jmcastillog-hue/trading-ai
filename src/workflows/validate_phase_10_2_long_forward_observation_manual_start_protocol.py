from __future__ import annotations

import pandas as pd

from src.long_side.long_forward_observation_manual_start_protocol_v1 import (
    validate_long_forward_observation_manual_start_protocol,
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
    print("PHASE 10.2 LONG FORWARD OBSERVATION MANUAL START PROTOCOL")
    print("=" * 100)
    print("Purpose: define manual protocol before future controlled LONG forward observation")
    print("Restriction: protocol only. No forward observation start. No execution.")
    print()

    result = validate_long_forward_observation_manual_start_protocol()

    print_section("PHASE 10.2 VALIDATION SUMMARY")
    print_df(result["summary"])

    print_section("PHASE 10.1 SOURCE SUMMARY")
    print_df(result["source_phase_10_1_summary"])

    print_section("SOURCE CONTROLLED START REQUIREMENTS")
    print_df(result["source_controlled_start_requirements"])

    print_section("SOURCE CONTROLLED START BOUNDARY MATRIX")
    print_df(result["source_controlled_start_boundary_matrix"])

    print_section("SOURCE CONTROLLED START SAFETY MATRIX")
    print_df(result["source_controlled_start_safety_matrix"])

    print_section("SOURCE CONTROLLED START DECISION")
    print_df(result["source_controlled_start_decision"])

    print_section("SOURCE CHECKS")
    print_df(result["source_checks"])

    print_section("MANUAL PROTOCOL STAGES")
    print_df(result["manual_protocol_stages"])

    print_section("MANUAL PROTOCOL RULES")
    print_df(result["manual_protocol_rules"])

    print_section("MANUAL PROTOCOL REQUIREMENTS")
    print_df(result["manual_protocol_requirements"])

    print_section("MANUAL PROTOCOL BOUNDARY MATRIX")
    print_df(result["manual_protocol_boundary_matrix"])

    print_section("MANUAL PROTOCOL SAFETY MATRIX")
    print_df(result["manual_protocol_safety_matrix"])

    print_section("MANUAL START PROTOCOL DECISION")
    print_df(result["manual_start_protocol_decision"])

    print_section("VALIDATION CHECKS")
    print_df(result["checks"])

    print()
    print("ARCHIVOS GENERADOS")
    print("=" * 100)
    print("- reports/phase_10_2_long_forward_observation_manual_start_protocol_v1/long_forward_observation_manual_start_protocol_summary_v1.csv")
    print("- reports/phase_10_2_long_forward_observation_manual_start_protocol_v1/phase_10_1_source_summary_v1.csv")
    print("- reports/phase_10_2_long_forward_observation_manual_start_protocol_v1/phase_10_1_source_controlled_start_requirements_v1.csv")
    print("- reports/phase_10_2_long_forward_observation_manual_start_protocol_v1/phase_10_1_source_controlled_start_boundary_matrix_v1.csv")
    print("- reports/phase_10_2_long_forward_observation_manual_start_protocol_v1/phase_10_1_source_controlled_start_safety_matrix_v1.csv")
    print("- reports/phase_10_2_long_forward_observation_manual_start_protocol_v1/phase_10_1_source_controlled_start_decision_v1.csv")
    print("- reports/phase_10_2_long_forward_observation_manual_start_protocol_v1/phase_10_1_source_checks_v1.csv")
    print("- reports/phase_10_2_long_forward_observation_manual_start_protocol_v1/long_forward_observation_manual_protocol_stages_v1.csv")
    print("- reports/phase_10_2_long_forward_observation_manual_start_protocol_v1/long_forward_observation_manual_protocol_rules_v1.csv")
    print("- reports/phase_10_2_long_forward_observation_manual_start_protocol_v1/long_forward_observation_manual_protocol_requirements_v1.csv")
    print("- reports/phase_10_2_long_forward_observation_manual_start_protocol_v1/long_forward_observation_manual_protocol_boundary_matrix_v1.csv")
    print("- reports/phase_10_2_long_forward_observation_manual_start_protocol_v1/long_forward_observation_manual_protocol_safety_matrix_v1.csv")
    print("- reports/phase_10_2_long_forward_observation_manual_start_protocol_v1/long_forward_observation_manual_start_protocol_decision_v1.csv")
    print("- reports/phase_10_2_long_forward_observation_manual_start_protocol_v1/long_forward_observation_manual_start_protocol_checks_v1.csv")
    print()
    print("Restriccion: Phase 10.2 define protocolo manual; no inicia observacion forward ni aprueba ejecucion.")


if __name__ == "__main__":
    main()