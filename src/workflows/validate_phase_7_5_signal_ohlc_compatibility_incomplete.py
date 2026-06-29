from __future__ import annotations

import pandas as pd

from src.market_input.signal_ohlc_compatibility_incomplete_v1 import (
    validate_signal_ohlc_compatibility_incomplete,
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
    print("PHASE 7.5 SIGNAL + OHLC COMPATIBILITY INCOMPLETE VALIDATOR")
    print("=" * 100)
    print("Purpose: validate signal + OHLC incomplete state without price levels")
    print("Restriction: no price levels, no complete evidence, no execution.")
    print()

    result = validate_signal_ohlc_compatibility_incomplete()

    print_section("PHASE 7.5 VALIDATION SUMMARY")
    print_df(result["summary"])

    print_section("OPERATIONAL INPUT FILE INVENTORY")
    print_df(result["file_inventory"])

    print_section("LOCAL OHLC ADAPTER SUMMARY")
    print_df(result["local_adapter_summary"])

    print_section("MANUAL SIGNAL ADAPTER SUMMARY")
    print_df(result["signal_adapter_summary"])

    print_section("OPERATIONAL ADAPTER OUTPUT PREVIEW")
    print_df(result["operational_adapter_output"], max_rows=45)

    print_section("VALIDATION CHECKS")
    print_df(result["checks"])

    print()
    print("ARCHIVOS GENERADOS")
    print("=" * 100)
    print("- reports/phase_7_5_signal_ohlc_compatibility_incomplete_v1/signal_ohlc_compatibility_incomplete_summary_v1.csv")
    print("- reports/phase_7_5_signal_ohlc_compatibility_incomplete_v1/signal_ohlc_compatibility_incomplete_file_inventory_v1.csv")
    print("- reports/phase_7_5_signal_ohlc_compatibility_incomplete_v1/signal_ohlc_compatibility_incomplete_local_adapter_summary_v1.csv")
    print("- reports/phase_7_5_signal_ohlc_compatibility_incomplete_v1/signal_ohlc_compatibility_incomplete_signal_adapter_summary_v1.csv")
    print("- reports/phase_7_5_signal_ohlc_compatibility_incomplete_v1/signal_ohlc_compatibility_incomplete_operational_adapter_output_v1.csv")
    print("- reports/phase_7_5_signal_ohlc_compatibility_incomplete_v1/signal_ohlc_compatibility_incomplete_checks_v1.csv")
    print()
    print("Restriccion: este validador no genera niveles, evidencia completa ni ejecucion.")


if __name__ == "__main__":
    main()