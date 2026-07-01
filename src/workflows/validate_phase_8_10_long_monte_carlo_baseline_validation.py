from __future__ import annotations

import pandas as pd

from src.long_side.long_monte_carlo_baseline_validation_v1 import (
    validate_long_monte_carlo_baseline_validation,
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
    print("PHASE 8.10 LONG MONTE CARLO BASELINE VALIDATION VALIDATOR")
    print("=" * 100)
    print("Purpose: validate surviving LONG candidates under Monte Carlo sequence stress")
    print("Restriction: Monte Carlo baseline only. No LONG approval. No execution.")
    print()

    result = validate_long_monte_carlo_baseline_validation()

    print_section("PHASE 8.10 VALIDATION SUMMARY")
    print_df(result["summary"])

    print_section("PHASE 8.9 SOURCE SUMMARY")
    print_df(result["source_summary"])

    print_section("PHASE 8.9 SOURCE CANDIDATE COST SUMMARY")
    print_df(result["source_candidate_cost_summary"])

    print_section("MONTE CARLO SOURCE STRESS TRADES")
    print_df(result["source_stress_trades"], max_rows=40)

    print_section("MONTE CARLO SIMULATIONS")
    print_df(result["monte_carlo_simulations"], max_rows=40)

    print_section("MONTE CARLO CANDIDATE SUMMARY")
    print_df(result["candidate_mc_summary"])

    print_section("VALIDATION CHECKS")
    print_df(result["checks"])

    print()
    print("ARCHIVOS GENERADOS")
    print("=" * 100)
    print("- reports/phase_8_10_long_monte_carlo_baseline_validation_v1/long_monte_carlo_baseline_summary_v1.csv")
    print("- reports/phase_8_10_long_monte_carlo_baseline_validation_v1/phase_8_9_source_summary_v1.csv")
    print("- reports/phase_8_10_long_monte_carlo_baseline_validation_v1/phase_8_9_source_candidate_cost_summary_v1.csv")
    print("- reports/phase_8_10_long_monte_carlo_baseline_validation_v1/long_monte_carlo_source_stress_trades_v1.csv")
    print("- reports/phase_8_10_long_monte_carlo_baseline_validation_v1/long_monte_carlo_simulations_v1.csv")
    print("- reports/phase_8_10_long_monte_carlo_baseline_validation_v1/long_monte_carlo_candidate_summary_v1.csv")
    print("- reports/phase_8_10_long_monte_carlo_baseline_validation_v1/long_monte_carlo_baseline_checks_v1.csv")
    print()
    print("Restriccion: Phase 8.10 valida Monte Carlo LONG, pero no aprueba LONG ni ejecucion.")


if __name__ == "__main__":
    main()