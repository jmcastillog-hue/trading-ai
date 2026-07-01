from __future__ import annotations

import pandas as pd

from src.long_side.long_forward_journal_controlled_input_run_v1 import (
    validate_long_forward_journal_controlled_input_run,
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
    print("PHASE 9.4 LONG FORWARD JOURNAL CONTROLLED INPUT RUN")
    print("=" * 100)
    print("Purpose: run controlled LONG journal input flow without accepting real evidence")
    print("Restriction: controlled synthetic run only. No real forward signals. No execution.")
    print()

    result = validate_long_forward_journal_controlled_input_run()

    print_section("PHASE 9.4 VALIDATION SUMMARY")
    print_df(result["summary"])

    print_section("PHASE 9.3 SOURCE SUMMARY")
    print_df(result["source_phase_9_3_summary"])

    print_section("SOURCE CONTROLLED INPUT ROWS")
    print_df(result["source_controlled_input_rows"])

    print_section("SOURCE ROW CHECKS")
    print_df(result["source_row_checks"])

    print_section("SOURCE ACCEPTED INPUTS")
    print_df(result["source_accepted_inputs"])

    print_section("SOURCE REJECTED INPUTS")
    print_df(result["source_rejected_inputs"])

    print_section("CONTROLLED RUN MANIFEST")
    print_df(result["controlled_run_manifest"])

    print_section("CONTROLLED RUN LEDGER")
    print_df(result["controlled_run_ledger"])

    print_section("REJECTION AUDIT")
    print_df(result["rejection_audit"])

    print_section("CONTROLLED RUN SUMMARY")
    print_df(result["controlled_run_summary"])

    print_section("VALIDATION CHECKS")
    print_df(result["checks"])

    print()
    print("ARCHIVOS GENERADOS")
    print("=" * 100)
    print("- reports/phase_9_4_long_forward_journal_controlled_input_run_v1/long_forward_journal_controlled_input_run_summary_v1.csv")
    print("- reports/phase_9_4_long_forward_journal_controlled_input_run_v1/phase_9_3_source_summary_v1.csv")
    print("- reports/phase_9_4_long_forward_journal_controlled_input_run_v1/phase_9_3_source_controlled_input_rows_v1.csv")
    print("- reports/phase_9_4_long_forward_journal_controlled_input_run_v1/phase_9_3_source_row_checks_v1.csv")
    print("- reports/phase_9_4_long_forward_journal_controlled_input_run_v1/phase_9_3_source_accepted_inputs_v1.csv")
    print("- reports/phase_9_4_long_forward_journal_controlled_input_run_v1/phase_9_3_source_rejected_inputs_v1.csv")
    print("- reports/phase_9_4_long_forward_journal_controlled_input_run_v1/long_forward_journal_controlled_run_manifest_v1.csv")
    print("- reports/phase_9_4_long_forward_journal_controlled_input_run_v1/long_forward_journal_controlled_run_ledger_v1.csv")
    print("- reports/phase_9_4_long_forward_journal_controlled_input_run_v1/long_forward_journal_controlled_rejection_audit_v1.csv")
    print("- reports/phase_9_4_long_forward_journal_controlled_input_run_v1/long_forward_journal_controlled_run_summary_table_v1.csv")
    print("- reports/phase_9_4_long_forward_journal_controlled_input_run_v1/long_forward_journal_controlled_input_run_checks_v1.csv")
    print()
    print("Restriccion: Phase 9.4 ejecuta flujo controlado LONG, pero no acepta evidencia real ni aprueba ejecucion.")


if __name__ == "__main__":
    main()