from __future__ import annotations

import pandas as pd

from src.long_side.long_candidate_historical_comparison_v1 import (
    validate_long_candidate_historical_comparison,
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
    print("PHASE 8.5 LONG CANDIDATE HISTORICAL COMPARISON VALIDATOR")
    print("=" * 100)
    print("Purpose: classify LONG candidates using historical baseline evidence")
    print("Restriction: comparison only. No LONG approval. No execution.")
    print()

    result = validate_long_candidate_historical_comparison()

    print_section("PHASE 8.5 VALIDATION SUMMARY")
    print_df(result["summary"])

    print_section("PHASE 8.4 SOURCE SUMMARY")
    print_df(result["source_summary"])

    print_section("PHASE 8.4 SOURCE METRICS")
    print_df(result["source_metrics"])

    print_section("LONG CANDIDATE HISTORICAL COMPARISON")
    print_df(result["comparison"])

    print_section("VALIDATION CHECKS")
    print_df(result["checks"])

    print()
    print("ARCHIVOS GENERADOS")
    print("=" * 100)
    print("- reports/phase_8_5_long_candidate_historical_comparison_v1/long_candidate_historical_comparison_summary_v1.csv")
    print("- reports/phase_8_5_long_candidate_historical_comparison_v1/phase_8_4_source_summary_v1.csv")
    print("- reports/phase_8_5_long_candidate_historical_comparison_v1/phase_8_4_source_metrics_v1.csv")
    print("- reports/phase_8_5_long_candidate_historical_comparison_v1/long_candidate_historical_comparison_v1.csv")
    print("- reports/phase_8_5_long_candidate_historical_comparison_v1/long_candidate_historical_comparison_checks_v1.csv")
    print()
    print("Restriccion: Phase 8.5 clasifica evidencia historica LONG, pero no aprueba LONG ni ejecucion.")


if __name__ == "__main__":
    main()