from __future__ import annotations

import pandas as pd

from src.market_input.manual_reviewed_price_levels_adapter_v1 import (
    validate_manual_reviewed_price_levels_adapter,
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
    print("PHASE 7.6 PRICE LEVELS ADAPTER VALIDATOR")
    print("=" * 100)
    print("Purpose: validate manual reviewed price levels adapter")
    print("Restriction: price level normalization only. No execution.")
    print()

    result = validate_manual_reviewed_price_levels_adapter()

    print_section("PHASE 7.6 VALIDATION SUMMARY")
    print_df(result["summary"])

    print_section("NORMALIZED PRICE LEVEL OUTPUT PREVIEW")
    print_df(result["output"])

    print_section("VALIDATION CHECKS")
    print_df(result["checks"])

    print()
    print("ARCHIVOS GENERADOS")
    print("=" * 100)
    print("- reports/phase_7_6_price_levels_adapter_v1/price_levels_adapter_summary_v1.csv")
    print("- reports/phase_7_6_price_levels_adapter_v1/price_levels_adapter_output_preview_v1.csv")
    print("- reports/phase_7_6_price_levels_adapter_v1/price_levels_adapter_checks_v1.csv")
    print("- data/market_input/manual_reviewed_price_levels/input/phase_7_6_manual_reviewed_price_levels_source_v1.csv")
    print("- data/forward_evidence/operational/input/price_levels/phase_7_6_manual_reviewed_price_levels_input_v1.csv")
    print()
    print("Restriccion: este validador no genera señales, OHLC, evidencia completa ni ejecucion.")


if __name__ == "__main__":
    main()