from __future__ import annotations

import pandas as pd

from src.long_side.long_forward_observation_controlled_dataset_write_v1 import (
    validate_long_forward_observation_controlled_dataset_write,
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
    print("PHASE 9.7 LONG FORWARD OBSERVATION CONTROLLED DATASET WRITE")
    print("=" * 100)
    print("Purpose: write synthetic controlled LONG observation rows to reports only")
    print("Restriction: report-only controlled write. No official dataset write. No execution.")
    print()

    result = validate_long_forward_observation_controlled_dataset_write()

    print_section("PHASE 9.7 VALIDATION SUMMARY")
    print_df(result["summary"])

    print_section("PHASE 9.6 SOURCE SUMMARY")
    print_df(result["source_phase_9_6_summary"])

    print_section("SOURCE PERSISTENCE GUARD SUMMARY")
    print_df(result["source_persistence_guard_summary"])

    print_section("SOURCE PERSISTENCE ATTEMPTS")
    print_df(result["source_persistence_attempts"])

    print_section("SOURCE EVALUATED ATTEMPTS")
    print_df(result["source_evaluated_attempts"])

    print_section("SOURCE GUARD AUDIT")
    print_df(result["source_guard_audit"])

    print_section("SOURCE BOOTSTRAP LEDGER")
    print_df(result["source_bootstrap_ledger"])

    print_section("SELECTED CONTROLLED ATTEMPT")
    print_df(result["selected_controlled_attempt"])

    print_section("CONTROLLED REPORT WRITE")
    print_df(result["controlled_report_write"])

    print_section("CONTROLLED WRITE AUDIT")
    print_df(result["controlled_write_audit"])

    print_section("CONTROLLED DATASET WRITE SUMMARY")
    print_df(result["controlled_dataset_write_summary"])

    print_section("VALIDATION CHECKS")
    print_df(result["checks"])

    print()
    print("ARCHIVOS GENERADOS")
    print("=" * 100)
    print("- reports/phase_9_7_long_forward_observation_controlled_dataset_write_v1/long_forward_observation_controlled_dataset_write_summary_v1.csv")
    print("- reports/phase_9_7_long_forward_observation_controlled_dataset_write_v1/phase_9_6_source_summary_v1.csv")
    print("- reports/phase_9_7_long_forward_observation_controlled_dataset_write_v1/phase_9_6_source_persistence_guard_summary_v1.csv")
    print("- reports/phase_9_7_long_forward_observation_controlled_dataset_write_v1/phase_9_6_source_persistence_attempts_v1.csv")
    print("- reports/phase_9_7_long_forward_observation_controlled_dataset_write_v1/phase_9_6_source_evaluated_attempts_v1.csv")
    print("- reports/phase_9_7_long_forward_observation_controlled_dataset_write_v1/phase_9_6_source_guard_audit_v1.csv")
    print("- reports/phase_9_7_long_forward_observation_controlled_dataset_write_v1/phase_9_5_source_bootstrap_ledger_v1.csv")
    print("- reports/phase_9_7_long_forward_observation_controlled_dataset_write_v1/long_forward_observation_selected_controlled_attempt_v1.csv")
    print("- reports/phase_9_7_long_forward_observation_controlled_dataset_write_v1/long_forward_observation_controlled_report_dataset_rows_v1.csv")
    print("- reports/phase_9_7_long_forward_observation_controlled_dataset_write_v1/long_forward_observation_controlled_dataset_write_audit_v1.csv")
    print("- reports/phase_9_7_long_forward_observation_controlled_dataset_write_v1/long_forward_observation_controlled_dataset_write_summary_table_v1.csv")
    print("- reports/phase_9_7_long_forward_observation_controlled_dataset_write_v1/long_forward_observation_controlled_dataset_write_checks_v1.csv")
    print()
    print("Restriccion: Phase 9.7 escribe solo filas sinteticas en reports; no escribe dataset oficial ni aprueba ejecucion.")


if __name__ == "__main__":
    main()