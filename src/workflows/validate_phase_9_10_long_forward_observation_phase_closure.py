from __future__ import annotations

import pandas as pd

from src.long_side.long_forward_observation_phase_closure_v1 import (
    validate_long_forward_observation_phase_closure,
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
    print("PHASE 9.10 LONG FORWARD OBSERVATION PHASE CLOSURE")
    print("=" * 100)
    print("Purpose: close Phase 9 as LONG forward observation preparation layer")
    print("Restriction: closure only. No forward observation start. No execution.")
    print()

    result = validate_long_forward_observation_phase_closure()

    print_section("PHASE 9.10 VALIDATION SUMMARY")
    print_df(result["summary"])

    print_section("PHASE 9.9 SOURCE SUMMARY")
    print_df(result["source_phase_9_9_summary"])

    print_section("SOURCE PRE-START CRITERIA")
    print_df(result["source_pre_start_criteria"])

    print_section("SOURCE PRE-START GATE DECISION")
    print_df(result["source_pre_start_gate_decision"])

    print_section("SOURCE PRE-START SAFETY MATRIX")
    print_df(result["source_pre_start_safety_matrix"])

    print_section("SOURCE CHECKS")
    print_df(result["source_checks"])

    print_section("PHASE 9 CLOSURE LEDGER")
    print_df(result["phase_9_closure_ledger"])

    print_section("PHASE 9 CLOSURE REQUIREMENTS")
    print_df(result["phase_9_closure_requirements"])

    print_section("PHASE 9 SAFETY CLOSURE MATRIX")
    print_df(result["phase_9_safety_closure_matrix"])

    print_section("PHASE 9 CLOSURE DECISION")
    print_df(result["phase_9_closure_decision"])

    print_section("VALIDATION CHECKS")
    print_df(result["checks"])

    print()
    print("ARCHIVOS GENERADOS")
    print("=" * 100)
    print("- reports/phase_9_10_long_forward_observation_phase_closure_v1/long_forward_observation_phase_closure_summary_v1.csv")
    print("- reports/phase_9_10_long_forward_observation_phase_closure_v1/phase_9_9_source_summary_v1.csv")
    print("- reports/phase_9_10_long_forward_observation_phase_closure_v1/phase_9_9_source_pre_start_criteria_v1.csv")
    print("- reports/phase_9_10_long_forward_observation_phase_closure_v1/phase_9_9_source_pre_start_gate_decision_v1.csv")
    print("- reports/phase_9_10_long_forward_observation_phase_closure_v1/phase_9_9_source_pre_start_safety_matrix_v1.csv")
    print("- reports/phase_9_10_long_forward_observation_phase_closure_v1/phase_9_9_source_checks_v1.csv")
    print("- reports/phase_9_10_long_forward_observation_phase_closure_v1/long_forward_observation_phase_9_closure_ledger_v1.csv")
    print("- reports/phase_9_10_long_forward_observation_phase_closure_v1/long_forward_observation_phase_9_closure_requirements_v1.csv")
    print("- reports/phase_9_10_long_forward_observation_phase_closure_v1/long_forward_observation_phase_9_safety_closure_matrix_v1.csv")
    print("- reports/phase_9_10_long_forward_observation_phase_closure_v1/long_forward_observation_phase_9_closure_decision_v1.csv")
    print("- reports/phase_9_10_long_forward_observation_phase_closure_v1/long_forward_observation_phase_closure_checks_v1.csv")
    print()
    print("Restriccion: Phase 9.10 cierra Phase 9 como preparacion; no inicia observacion forward ni aprueba ejecucion.")


if __name__ == "__main__":
    main()