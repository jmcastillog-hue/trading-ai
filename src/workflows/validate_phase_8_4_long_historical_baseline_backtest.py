from __future__ import annotations

import pandas as pd

from src.long_side.long_historical_baseline_backtest_v1 import (
    validate_long_historical_baseline_backtest,
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
    print("PHASE 8.4 LONG HISTORICAL BASELINE BACKTEST VALIDATOR")
    print("=" * 100)
    print("Purpose: measure baseline LONG candidates on available historical OHLC")
    print("Restriction: historical baseline only. No LONG approval. No execution.")
    print()

    result = validate_long_historical_baseline_backtest()

    print_section("PHASE 8.4 VALIDATION SUMMARY")
    print_df(result["summary"])

    print_section("LONG CANDIDATE REGISTRY")
    print_df(result["candidates"])

    print_section("NORMALIZED OHLC PREVIEW")
    print_df(result["normalized_ohlc"], max_rows=10)

    print_section("HISTORICAL BACKTEST TRADES")
    print_df(result["trades"], max_rows=30)

    print_section("HISTORICAL BACKTEST METRICS")
    print_df(result["metrics"])

    print_section("VALIDATION CHECKS")
    print_df(result["checks"])

    print()
    print("ARCHIVOS GENERADOS")
    print("=" * 100)
    print("- reports/phase_8_4_long_historical_baseline_backtest_v1/long_historical_backtest_summary_v1.csv")
    print("- reports/phase_8_4_long_historical_baseline_backtest_v1/long_historical_candidate_registry_v1.csv")
    print("- reports/phase_8_4_long_historical_baseline_backtest_v1/long_historical_normalized_ohlc_preview_v1.csv")
    print("- reports/phase_8_4_long_historical_baseline_backtest_v1/long_historical_backtest_trades_v1.csv")
    print("- reports/phase_8_4_long_historical_baseline_backtest_v1/long_historical_backtest_metrics_v1.csv")
    print("- reports/phase_8_4_long_historical_baseline_backtest_v1/long_historical_backtest_checks_v1.csv")
    print()
    print("Restriccion: Phase 8.4 mide baseline historico LONG, pero no aprueba LONG ni ejecucion.")


if __name__ == "__main__":
    main()