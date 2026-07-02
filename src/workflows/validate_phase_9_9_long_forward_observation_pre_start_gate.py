from __future__ import annotations

import pandas as pd

from src.long_side.long_forward_observation_pre_start_gate_v1 import (
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
    print("PHASE 9.9 LONG FORWARD OBSERVATION PRE-START GATE")
    print("=" * 100)
    print("Purpose: validate pre-start gate for future controlled LONG forward observation")
    print("Restriction: pre-start gate only. No forward observation start. No execution.")
    print()

    result = validate_long_forward_observation_pre_start_gate()

    print_section("PHASE 9.9 VALIDATION SUMMARY")
    print_df(result["summary"])

    print_section("PHASE 9.8 SOURCE SUMMARY")
    print_df(result["source_phase_9_8_summary"])

    print_section("SOURCE REPORT INTEGRITY SUMMARY")
    print_df(result["source_report_integrity_summary"])

    print_section("SOURCE COMBINED INTEGRITY AUDIT")
    print_df(result["source_combined_integrity_audit"])

    print_section("SOURCE CHECKS")
    print_df(result["source_checks"])

    print_section("PRE-START CRITERIA")
    print_df(result["pre_start_criteria"])

    print_section("PRE-START GATE DECISION")
    print_df(result["pre_start_gate_decision"])

    print_section("PRE-START SAFETY MATRIX")
    print_df(result["pre_start_safety_matrix"])

    print_section("VALIDATION CHECKS")
    print_df(result["checks"])

    print()
    print("ARCHIVOS GENERADOS")
    print("=" * 100)
    print("- reports/phase_9_9_long_forward_observation_pre_start_gate_v1/long_forward_observation_pre_start_gate_summary_v1.csv")
    print("- reports/phase_9_9_long_forward_observation_pre_start_gate_v1/phase_9_8_source_summary_v1.csv")
    print("- reports/phase_9_9_long_forward_observation_pre_start_gate_v1/phase_9_8_source_report_integrity_summary_v1.csv")
    print("- reports/phase_9_9_long_forward_observation_pre_start_gate_v1/phase_9_8_source_combined_integrity_audit_v1.csv")
    print("- reports/phase_9_9_long_forward_observation_pre_start_gate_v1/phase_9_8_source_checks_v1.csv")
    print("- reports/phase_9_9_long_forward_observation_pre_start_gate_v1/long_forward_observation_pre_start_criteria_v1.csv")
    print("- reports/phase_9_9_long_forward_observation_pre_start_gate_v1/long_forward_observation_pre_start_gate_decision_v1.csv")
    print("- reports/phase_9_9_long_forward_observation_pre_start_gate_v1/long_forward_observation_pre_start_safety_matrix_v1.csv")
    print("- reports/phase_9_9_long_forward_observation_pre_start_gate_v1/long_forward_observation_pre_start_gate_checks_v1.csv")
    print()
    print("Restriccion: Phase 9.9 define gate pre-start; no inicia observacion forward ni aprueba ejecucion.")


if __name__ == "__main__":
    main()