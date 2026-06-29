from __future__ import annotations

import pandas as pd

from src.long_side.long_side_validation_contract_v1 import (
    validate_long_side_contract,
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
    print("PHASE 8.1 LONG-SIDE VALIDATION CONTRACT VALIDATOR")
    print("=" * 100)
    print("Purpose: define LONG-side validation contract")
    print("Restriction: contract only. No LONG approval. No execution.")
    print()

    result = validate_long_side_contract()

    print_section("PHASE 8.1 VALIDATION SUMMARY")
    print_df(result["summary"])

    print_section("VALIDATION CHECKS")
    print_df(result["checks"])

    print_section("REQUIRED LONG SIGNAL COLUMNS")
    print_df(result["signal_columns"])

    print_section("REQUIRED LONG PRICE LEVEL COLUMNS")
    print_df(result["price_level_columns"])

    print_section("REQUIRED LONG EVIDENCE COLUMNS")
    print_df(result["evidence_columns"])

    print_section("REQUIRED LONG RESEARCH GATES")
    print_df(result["research_gates"])

    print_section("REQUIRED LONG CONTEXT CONSIDERATIONS")
    print_df(result["context_considerations"])

    print()
    print("ARCHIVOS GENERADOS")
    print("=" * 100)
    print("- reports/phase_8_1_long_side_validation_contract_v1/long_side_validation_contract_summary_v1.csv")
    print("- reports/phase_8_1_long_side_validation_contract_v1/long_side_validation_contract_checks_v1.csv")
    print("- reports/phase_8_1_long_side_validation_contract_v1/required_long_signal_columns_v1.csv")
    print("- reports/phase_8_1_long_side_validation_contract_v1/required_long_price_level_columns_v1.csv")
    print("- reports/phase_8_1_long_side_validation_contract_v1/required_long_evidence_columns_v1.csv")
    print("- reports/phase_8_1_long_side_validation_contract_v1/required_long_research_gates_v1.csv")
    print("- reports/phase_8_1_long_side_validation_contract_v1/required_long_context_considerations_v1.csv")
    print()
    print("Restriccion: Phase 8.1 define contrato LONG, pero no aprueba LONG ni ejecucion.")


if __name__ == "__main__":
    main()