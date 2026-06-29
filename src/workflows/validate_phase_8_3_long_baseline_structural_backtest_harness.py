from __future__ import annotations

import pandas as pd

from src.long_side.long_baseline_structural_backtest_harness_v1 import (
    validate_long_baseline_structural_backtest_harness,
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
    print("PHASE 8.3 LONG BASELINE STRUCTURAL BACKTEST HARNESS VALIDATOR")
    print("=" * 100)
    print("Purpose: validate controlled structural measurement for LONG candidates")
    print("Restriction: structural measurement only. No LONG approval. No execution.")
    print()

    result = validate_long_baseline_structural_backtest_harness()

    print_section("PHASE 8.3 VALIDATION SUMMARY")
    print_df(result["summary"])

    print_section("LONG CANDIDATE REGISTRY")
    print_df(result["candidates"])

    print_section("STRUCTURAL BACKTEST TRADES")
    print_df(result["trades"])

    print_section("STRUCTURAL BACKTEST METRICS")
    print_df(result["metrics"])

    print_section("VALIDATION CHECKS")
    print_df(result["checks"])

    print()
    print("ARCHIVOS GENERADOS")
    print("=" * 100)
    print("- reports/phase_8_3_long_baseline_structural_backtest_harness_v1/long_structural_backtest_summary_v1.csv")
    print("- reports/phase_8_3_long_baseline_structural_backtest_harness_v1/long_structural_backtest_candidate_registry_v1.csv")
    print("- reports/phase_8_3_long_baseline_structural_backtest_harness_v1/long_structural_backtest_trades_v1.csv")
    print("- reports/phase_8_3_long_baseline_structural_backtest_harness_v1/long_structural_backtest_metrics_v1.csv")
    print("- reports/phase_8_3_long_baseline_structural_backtest_harness_v1/long_structural_backtest_checks_v1.csv")
    print()
    print("Restriccion: Phase 8.3 mide candidatos LONG estructurales, pero no aprueba LONG ni ejecucion.")


if __name__ == "__main__":
    main()