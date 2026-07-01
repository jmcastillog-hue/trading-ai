from __future__ import annotations

import pandas as pd

from src.long_side.long_cost_aware_baseline_validation_v1 import (
    validate_long_cost_aware_baseline_validation,
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
    print("PHASE 8.9 LONG COST-AWARE BASELINE VALIDATION VALIDATOR")
    print("=" * 100)
    print("Purpose: validate surviving LONG candidates after estimated trading friction")
    print("Restriction: cost-aware baseline only. No LONG approval. No execution.")
    print()

    result = validate_long_cost_aware_baseline_validation()

    print_section("PHASE 8.9 VALIDATION SUMMARY")
    print_df(result["summary"])

    print_section("PHASE 8.8 SOURCE SUMMARY")
    print_df(result["source_summary"])

    print_section("PHASE 8.8 SOURCE CANDIDATE METRICS")
    print_df(result["source_candidate_metrics"])

    print_section("COST PROFILES")
    print_df(result["cost_profiles"])

    print_section("COST-ADJUSTED TRADES")
    print_df(result["cost_adjusted_trades"], max_rows=40)

    print_section("COST-AWARE METRICS")
    print_df(result["cost_metrics"])

    print_section("CANDIDATE COST-AWARE SUMMARY")
    print_df(result["candidate_cost_summary"])

    print_section("VALIDATION CHECKS")
    print_df(result["checks"])

    print()
    print("ARCHIVOS GENERADOS")
    print("=" * 100)
    print("- reports/phase_8_9_long_cost_aware_baseline_validation_v1/long_cost_aware_baseline_summary_v1.csv")
    print("- reports/phase_8_9_long_cost_aware_baseline_validation_v1/phase_8_8_source_summary_v1.csv")
    print("- reports/phase_8_9_long_cost_aware_baseline_validation_v1/phase_8_8_source_candidate_metrics_v1.csv")
    print("- reports/phase_8_9_long_cost_aware_baseline_validation_v1/long_cost_profiles_v1.csv")
    print("- reports/phase_8_9_long_cost_aware_baseline_validation_v1/long_cost_adjusted_trades_v1.csv")
    print("- reports/phase_8_9_long_cost_aware_baseline_validation_v1/long_cost_aware_metrics_v1.csv")
    print("- reports/phase_8_9_long_cost_aware_baseline_validation_v1/long_cost_aware_candidate_summary_v1.csv")
    print("- reports/phase_8_9_long_cost_aware_baseline_validation_v1/long_cost_aware_baseline_checks_v1.csv")
    print()
    print("Restriccion: Phase 8.9 valida costos LONG, pero no aprueba LONG ni ejecucion.")


if __name__ == "__main__":
    main()