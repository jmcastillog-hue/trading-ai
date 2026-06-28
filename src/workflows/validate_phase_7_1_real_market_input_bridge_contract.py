from __future__ import annotations

import pandas as pd

from src.market_input.real_market_input_bridge_contract_v1 import (
    validate_real_market_input_bridge_contract,
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
    print("PHASE 7.1 REAL MARKET INPUT BRIDGE CONTRACT VALIDATOR")
    print("=" * 100)
    print("Purpose: validate non-executing real market input bridge contract")
    print("Restriction: contract validation only. No market fetch. No execution.")
    print()

    result = validate_real_market_input_bridge_contract()

    print_section("PHASE 7.1 VALIDATION SUMMARY")
    print_df(result["summary"])

    print_section("SOURCE CONTRACTS")
    print_df(result["source_contracts"])

    print_section("OUTPUT SCHEMAS")
    print_df(result["output_schemas"])

    print_section("VALIDATION CHECKS")
    print_df(result["checks"])

    print()
    print("ARCHIVOS GENERADOS")
    print("=" * 100)
    print("- reports/phase_7_1_real_market_input_bridge_contract_v1/real_market_input_bridge_contract_summary_v1.csv")
    print("- reports/phase_7_1_real_market_input_bridge_contract_v1/real_market_input_source_contracts_v1.csv")
    print("- reports/phase_7_1_real_market_input_bridge_contract_v1/real_market_input_output_schemas_v1.csv")
    print("- reports/phase_7_1_real_market_input_bridge_contract_v1/real_market_input_bridge_contract_checks_v1.csv")
    print()
    print("Restriccion: este validador no obtiene mercado real y no habilita ejecucion.")


if __name__ == "__main__":
    main()