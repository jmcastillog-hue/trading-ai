from __future__ import annotations

import pandas as pd

from src.long_side.long_walk_forward_baseline_validation_v1 import (
    validate_long_walk_forward_baseline_validation,
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
    print("PHASE 8.8 LONG WALK-FORWARD BASELINE VALIDATION VALIDATOR")
    print("=" * 100)
    print("Purpose: validate primary LONG candidate across walk-forward baseline windows")
    print("Restriction: walk-forward baseline only. No LONG approval. No execution.")
    print()

    result = validate_long_walk_forward_baseline_validation()

    print_section("PHASE 8.8 VALIDATION SUMMARY")
    print_df(result["summary"])

    print_section("PHASE 8.7 SOURCE SUMMARY")
    print_df(result["source_summary"])

    print_section("PHASE 8.7 SOURCE DECISION GATE")
    print_df(result["source_decision_gate"])

    print_section("WALK-FORWARD WINDOWS")
    print_df(result["windows"])

    print_section("WALK-FORWARD TRADES")
    print_df(result["wf_trades"], max_rows=40)

    print_section("WALK-FORWARD WINDOW METRICS")
    print_df(result["window_metrics"])

    print_section("WALK-FORWARD CANDIDATE METRICS")
    print_df(result["candidate_metrics"])

    print_section("VALIDATION CHECKS")
    print_df(result["checks"])

    print()
    print("ARCHIVOS GENERADOS")
    print("=" * 100)
    print("- reports/phase_8_8_long_walk_forward_baseline_validation_v1/long_walk_forward_baseline_summary_v1.csv")
    print("- reports/phase_8_8_long_walk_forward_baseline_validation_v1/phase_8_7_source_summary_v1.csv")
    print("- reports/phase_8_8_long_walk_forward_baseline_validation_v1/phase_8_7_source_decision_gate_v1.csv")
    print("- reports/phase_8_8_long_walk_forward_baseline_validation_v1/long_walk_forward_windows_v1.csv")
    print("- reports/phase_8_8_long_walk_forward_baseline_validation_v1/long_walk_forward_trades_v1.csv")
    print("- reports/phase_8_8_long_walk_forward_baseline_validation_v1/long_walk_forward_window_metrics_v1.csv")
    print("- reports/phase_8_8_long_walk_forward_baseline_validation_v1/long_walk_forward_candidate_metrics_v1.csv")
    print("- reports/phase_8_8_long_walk_forward_baseline_validation_v1/long_walk_forward_baseline_checks_v1.csv")
    print()
    print("Restriccion: Phase 8.8 valida walk-forward baseline LONG, pero no aprueba LONG ni ejecucion.")


if __name__ == "__main__":
    main()