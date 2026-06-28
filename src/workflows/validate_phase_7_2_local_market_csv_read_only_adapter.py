from __future__ import annotations

import pandas as pd

from src.market_input.local_market_csv_read_only_adapter_v1 import (
    validate_local_market_csv_read_only_adapter,
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
    print("PHASE 7.2 LOCAL MARKET CSV READ-ONLY ADAPTER VALIDATOR")
    print("=" * 100)
    print("Purpose: validate local OHLC CSV read-only adapter")
    print("Restriction: local CSV normalization only. No market fetch. No execution.")
    print()

    result = validate_local_market_csv_read_only_adapter()

    print_section("PHASE 7.2 VALIDATION SUMMARY")
    print_df(result["summary"])

    print_section("NORMALIZED OHLC OUTPUT PREVIEW")
    print_df(result["output"])

    print_section("VALIDATION CHECKS")
    print_df(result["checks"])

    print()
    print("ARCHIVOS GENERADOS")
    print("=" * 100)
    print("- reports/phase_7_2_local_market_csv_read_only_adapter_v1/local_market_csv_read_only_adapter_summary_v1.csv")
    print("- reports/phase_7_2_local_market_csv_read_only_adapter_v1/local_market_csv_read_only_adapter_output_preview_v1.csv")
    print("- reports/phase_7_2_local_market_csv_read_only_adapter_v1/local_market_csv_read_only_adapter_checks_v1.csv")
    print("- data/market_input/local_csv_read_only/input/phase_7_2_local_btcusdt_15m_source_v1.csv")
    print("- data/forward_evidence/operational/input/ohlc/phase_7_2_local_market_ohlc_input_v1.csv")
    print()
    print("Restriccion: este validador no obtiene mercado real y no habilita ejecucion.")


if __name__ == "__main__":
    main()