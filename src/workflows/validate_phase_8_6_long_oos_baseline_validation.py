from __future__ import annotations

import pandas as pd

from src.long_side.long_oos_baseline_validation_v1 import (
    validate_long_oos_baseline_validation,
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
    print("PHASE 8.6 LONG OOS BASELINE VALIDATION VALIDATOR")
    print("=" * 100)
    print("Purpose: validate eligible LONG candidates on separated OOS baseline window")
    print("Restriction: OOS baseline only. No LONG approval. No execution.")
    print()

    result = validate_long_oos_baseline_validation()

    print_section("PHASE 8.6 VALIDATION SUMMARY")
    print_df(result["summary"])

    print_section("PHASE 8.5 SOURCE COMPARISON")
    print_df(result["source_comparison"])

    print_section("OOS ELIGIBLE CANDIDATES")
    print_df(result["eligible_candidates"])

    print_section("OOS EXCLUDED CANDIDATES")
    print_df(result["excluded_candidates"])

    print_section("OOS BASELINE TRADES")
    print_df(result["oos_trades"], max_rows=30)

    print_section("OOS BASELINE METRICS")
    print_df(result["oos_metrics"])

    print_section("VALIDATION CHECKS")
    print_df(result["checks"])

    print()
    print("ARCHIVOS GENERADOS")
    print("=" * 100)
    print("- reports/phase_8_6_long_oos_baseline_validation_v1/long_oos_baseline_validation_summary_v1.csv")
    print("- reports/phase_8_6_long_oos_baseline_validation_v1/phase_8_5_source_comparison_v1.csv")
    print("- reports/phase_8_6_long_oos_baseline_validation_v1/long_oos_eligible_candidates_v1.csv")
    print("- reports/phase_8_6_long_oos_baseline_validation_v1/long_oos_excluded_candidates_v1.csv")
    print("- reports/phase_8_6_long_oos_baseline_validation_v1/long_oos_baseline_trades_v1.csv")
    print("- reports/phase_8_6_long_oos_baseline_validation_v1/long_oos_baseline_metrics_v1.csv")
    print("- reports/phase_8_6_long_oos_baseline_validation_v1/long_oos_baseline_validation_checks_v1.csv")
    print()
    print("Restriccion: Phase 8.6 valida OOS baseline LONG, pero no aprueba LONG ni ejecucion.")


if __name__ == "__main__":
    main()