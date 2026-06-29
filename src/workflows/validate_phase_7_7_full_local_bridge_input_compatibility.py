from __future__ import annotations

import pandas as pd

from src.market_input.full_local_bridge_input_compatibility_v1 import (
    validate_full_local_bridge_input_compatibility,
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
    print("PHASE 7.7 FULL LOCAL BRIDGE INPUT COMPATIBILITY VALIDATOR")
    print("=" * 100)
    print("Purpose: validate signals + OHLC + price_levels together")
    print("Restriction: bridge readiness only. No evidence cycle. No execution.")
    print()

    result = validate_full_local_bridge_input_compatibility()

    print_section("PHASE 7.7 VALIDATION SUMMARY")
    print_df(result["summary"])

    print_section("OPERATIONAL ADAPTER SUMMARY")
    print_df(result["operational_summary"])

    print_section("OPERATIONAL FILE INVENTORY")
    print_df(result["operational_file_inventory"])

    print_section("ADAPTED SIGNALS PREVIEW")
    print_df(result["adapted_signals"], max_rows=10)

    print_section("ADAPTED OHLC PREVIEW")
    print_df(result["adapted_ohlc"], max_rows=10)

    print_section("ADAPTED PRICE LEVELS PREVIEW")
    print_df(result["adapted_price_levels"], max_rows=10)

    print_section("VALIDATION CHECKS")
    print_df(result["checks"])

    print_section("REJECTED FILES")
    print_df(result["rejected_files"])

    print()
    print("ARCHIVOS GENERADOS")
    print("=" * 100)
    print("- reports/phase_7_7_full_local_bridge_input_compatibility_v1/full_local_bridge_input_compatibility_summary_v1.csv")
    print("- reports/phase_7_7_full_local_bridge_input_compatibility_v1/full_local_bridge_input_compatibility_checks_v1.csv")
    print("- reports/phase_7_7_full_local_bridge_input_compatibility_v1/full_local_bridge_operational_summary_v1.csv")
    print("- reports/phase_7_7_full_local_bridge_input_compatibility_v1/full_local_bridge_operational_file_inventory_v1.csv")
    print("- reports/phase_7_7_full_local_bridge_input_compatibility_v1/full_local_bridge_operational_validation_v1.csv")
    print("- reports/phase_7_7_full_local_bridge_input_compatibility_v1/full_local_bridge_adapted_signals_v1.csv")
    print("- reports/phase_7_7_full_local_bridge_input_compatibility_v1/full_local_bridge_adapted_ohlc_v1.csv")
    print("- reports/phase_7_7_full_local_bridge_input_compatibility_v1/full_local_bridge_adapted_price_levels_v1.csv")
    print()
    print("Restriccion: este validador no ejecuta ciclo de evidencia ni operaciones.")


if __name__ == "__main__":
    main()