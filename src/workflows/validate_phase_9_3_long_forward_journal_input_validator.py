from __future__ import annotations

import pandas as pd

from src.long_side.long_forward_journal_input_validator_v1 import (
    validate_long_forward_journal_input_validator,
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
    print("PHASE 9.3 LONG FORWARD JOURNAL INPUT VALIDATOR")
    print("=" * 100)
    print("Purpose: validate controlled future LONG journal input rows without accepting real evidence")
    print("Restriction: input validator only. No real forward signals. No LONG approval. No execution.")
    print()

    result = validate_long_forward_journal_input_validator()

    print_section("PHASE 9.3 VALIDATION SUMMARY")
    print_df(result["summary"])

    print_section("PHASE 9.2 SOURCE SUMMARY")
    print_df(result["source_phase_9_2_summary"])

    print_section("SOURCE CANDIDATE REGISTRY")
    print_df(result["source_candidate_registry"])

    print_section("SOURCE JOURNAL SCHEMA")
    print_df(result["source_journal_schema"])

    print_section("CONTROLLED INPUT ROWS")
    print_df(result["controlled_input_rows"])

    print_section("COLUMN CHECKS")
    print_df(result["column_checks"])

    print_section("ROW CHECKS")
    print_df(result["row_checks"])

    print_section("ACCEPTED CONTROLLED INPUTS")
    print_df(result["accepted_inputs"])

    print_section("REJECTED CONTROLLED INPUTS")
    print_df(result["rejected_inputs"])

    print_section("VALIDATION CHECKS")
    print_df(result["checks"])

    print()
    print("ARCHIVOS GENERADOS")
    print("=" * 100)
    print("- reports/phase_9_3_long_forward_journal_input_validator_v1/long_forward_journal_input_validator_summary_v1.csv")
    print("- reports/phase_9_3_long_forward_journal_input_validator_v1/phase_9_2_source_summary_v1.csv")
    print("- reports/phase_9_3_long_forward_journal_input_validator_v1/phase_9_1_source_candidate_registry_v1.csv")
    print("- reports/phase_9_3_long_forward_journal_input_validator_v1/phase_9_2_source_journal_schema_v1.csv")
    print("- reports/phase_9_3_long_forward_journal_input_validator_v1/long_forward_journal_controlled_input_rows_v1.csv")
    print("- reports/phase_9_3_long_forward_journal_input_validator_v1/long_forward_journal_input_column_checks_v1.csv")
    print("- reports/phase_9_3_long_forward_journal_input_validator_v1/long_forward_journal_input_row_checks_v1.csv")
    print("- reports/phase_9_3_long_forward_journal_input_validator_v1/long_forward_journal_input_accepted_controlled_rows_v1.csv")
    print("- reports/phase_9_3_long_forward_journal_input_validator_v1/long_forward_journal_input_rejected_controlled_rows_v1.csv")
    print("- reports/phase_9_3_long_forward_journal_input_validator_v1/long_forward_journal_input_validator_checks_v1.csv")
    print()
    print("Restriccion: Phase 9.3 valida inputs controlados LONG forward, pero no acepta evidencia real ni aprueba ejecucion.")


if __name__ == "__main__":
    main()