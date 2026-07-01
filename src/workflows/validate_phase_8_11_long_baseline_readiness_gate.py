from __future__ import annotations

import pandas as pd

from src.long_side.long_baseline_readiness_gate_v1 import (
    validate_long_baseline_readiness_gate,
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
    print("PHASE 8.11 LONG BASELINE READINESS GATE VALIDATOR")
    print("=" * 100)
    print("Purpose: consolidate LONG baseline evidence and decide future forward observation readiness")
    print("Restriction: readiness gate only. No LONG approval. No execution.")
    print()

    result = validate_long_baseline_readiness_gate()

    print_section("PHASE 8.11 VALIDATION SUMMARY")
    print_df(result["summary"])

    print_section("PHASE 8.10 SOURCE SUMMARY")
    print_df(result["source_phase_8_10_summary"])

    print_section("PHASE 8.9 SOURCE CANDIDATE COST SUMMARY")
    print_df(result["source_candidate_cost_summary"])

    print_section("PHASE 8.10 SOURCE CANDIDATE MC SUMMARY")
    print_df(result["source_candidate_mc_summary"])

    print_section("LONG BASELINE READINESS GATE")
    print_df(result["readiness_gate"])

    print_section("EVIDENCE LEDGER")
    print_df(result["evidence_ledger"])

    print_section("VALIDATION CHECKS")
    print_df(result["checks"])

    print()
    print("ARCHIVOS GENERADOS")
    print("=" * 100)
    print("- reports/phase_8_11_long_baseline_readiness_gate_v1/long_baseline_readiness_gate_summary_v1.csv")
    print("- reports/phase_8_11_long_baseline_readiness_gate_v1/phase_8_10_source_summary_v1.csv")
    print("- reports/phase_8_11_long_baseline_readiness_gate_v1/phase_8_9_source_candidate_cost_summary_v1.csv")
    print("- reports/phase_8_11_long_baseline_readiness_gate_v1/phase_8_10_source_candidate_mc_summary_v1.csv")
    print("- reports/phase_8_11_long_baseline_readiness_gate_v1/long_baseline_readiness_gate_v1.csv")
    print("- reports/phase_8_11_long_baseline_readiness_gate_v1/long_baseline_readiness_evidence_ledger_v1.csv")
    print("- reports/phase_8_11_long_baseline_readiness_gate_v1/long_baseline_readiness_gate_checks_v1.csv")
    print()
    print("Restriccion: Phase 8.11 decide readiness LONG para observacion forward futura, pero no aprueba LONG ni ejecucion.")


if __name__ == "__main__":
    main()