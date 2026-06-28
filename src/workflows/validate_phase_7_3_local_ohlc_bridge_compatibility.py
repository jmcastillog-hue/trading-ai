from __future__ import annotations

import pandas as pd

from src.market_input.local_ohlc_bridge_compatibility_v1 import (
    validate_local_ohlc_bridge_compatibility,
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
    print("PHASE 7.3 LOCAL OHLC BRIDGE COMPATIBILITY VALIDATOR")
    print("=" * 100)
    print("Purpose: validate OHLC-only compatibility with operational input pipeline")
    print("Restriction: no signal generation, no price levels, no execution.")
    print()

    result = validate_local_ohlc_bridge_compatibility()

    print_section("PHASE 7.3 VALIDATION SUMMARY")
    print_df(result["summary"])

    print_section("OPERATIONAL INPUT FILE INVENTORY")
    print_df(result["file_inventory"])

    print_section("LOCAL ADAPTER SUMMARY")
    print_df(result["local_adapter_summary"])

    print_section("OPERATIONAL ADAPTER OUTPUT PREVIEW")
    print_df(result["operational_adapter_output"], max_rows=40)

    print_section("VALIDATION CHECKS")
    print_df(result["checks"])

    print()
    print("ARCHIVOS GENERADOS")
    print("=" * 100)
    print("- reports/phase_7_3_local_ohlc_bridge_compatibility_v1/local_ohlc_bridge_compatibility_summary_v1.csv")
    print("- reports/phase_7_3_local_ohlc_bridge_compatibility_v1/local_ohlc_bridge_compatibility_file_inventory_v1.csv")
    print("- reports/phase_7_3_local_ohlc_bridge_compatibility_v1/local_ohlc_bridge_compatibility_local_adapter_summary_v1.csv")
    print("- reports/phase_7_3_local_ohlc_bridge_compatibility_v1/local_ohlc_bridge_compatibility_operational_adapter_output_v1.csv")
    print("- reports/phase_7_3_local_ohlc_bridge_compatibility_v1/local_ohlc_bridge_compatibility_checks_v1.csv")
    print()
    print("Restriccion: este validador no genera señales, niveles, evidencia ni ejecucion.")


if __name__ == "__main__":
    main()