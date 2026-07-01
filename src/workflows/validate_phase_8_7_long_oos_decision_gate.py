from __future__ import annotations

import pandas as pd

from src.long_side.long_oos_decision_gate_v1 import (
    validate_long_oos_decision_gate,
)


def print_section(title: str) -> None:
    print()
    print(title)
    print("=" * 100)


def print_df(df: pd.DataFrame) -> None:
    if df.empty:
        print("Sin registros.")
        return

    print(df.to_string(index=False))


def main() -> None:
    print("PHASE 8.7 LONG OOS DECISION GATE VALIDATOR")
    print("=" * 100)
    print("Purpose: convert LONG OOS baseline evidence into a restrictive research decision gate")
    print("Restriction: decision gate only. No LONG approval. No execution.")
    print()

    result = validate_long_oos_decision_gate()

    print_section("PHASE 8.7 VALIDATION SUMMARY")
    print_df(result["summary"])

    print_section("PHASE 8.6 SOURCE SUMMARY")
    print_df(result["source_summary"])

    print_section("PHASE 8.6 SOURCE OOS METRICS")
    print_df(result["source_oos_metrics"])

    print_section("PHASE 8.5 SOURCE COMPARISON")
    print_df(result["source_comparison"])

    print_section("LONG OOS DECISION GATE")
    print_df(result["decision_gate"])

    print_section("VALIDATION CHECKS")
    print_df(result["checks"])

    print()
    print("ARCHIVOS GENERADOS")
    print("=" * 100)
    print("- reports/phase_8_7_long_oos_decision_gate_v1/long_oos_decision_gate_summary_v1.csv")
    print("- reports/phase_8_7_long_oos_decision_gate_v1/phase_8_6_source_summary_v1.csv")
    print("- reports/phase_8_7_long_oos_decision_gate_v1/phase_8_6_source_oos_metrics_v1.csv")
    print("- reports/phase_8_7_long_oos_decision_gate_v1/phase_8_5_source_comparison_v1.csv")
    print("- reports/phase_8_7_long_oos_decision_gate_v1/long_oos_decision_gate_v1.csv")
    print("- reports/phase_8_7_long_oos_decision_gate_v1/long_oos_decision_gate_checks_v1.csv")
    print()
    print("Restriccion: Phase 8.7 decide continuidad de investigacion LONG, pero no aprueba LONG ni ejecucion.")


if __name__ == "__main__":
    main()