from __future__ import annotations

import pandas as pd

from src.long_side.long_forward_observation_report_integrity_v1 import (
    validate_long_forward_observation_report_integrity,
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
    print("PHASE 9.8 LONG FORWARD OBSERVATION REPORT INTEGRITY")
    print("=" * 100)
    print("Purpose: validate integrity of controlled LONG report-only dataset output")
    print("Restriction: report integrity only. No official dataset write. No execution.")
    print()

    result = validate_long_forward_observation_report_integrity()

    print_section("PHASE 9.8 VALIDATION SUMMARY")
    print_df(result["summary"])

    print_section("PHASE 9.7 SOURCE SUMMARY")
    print_df(result["source_phase_9_7_summary"])

    print_section("SOURCE CONTROLLED REPORT WRITE")
    print_df(result["source_controlled_report_write"])

    print_section("SOURCE CONTROLLED WRITE AUDIT")
    print_df(result["source_controlled_write_audit"])

    print_section("SOURCE CONTROLLED DATASET WRITE SUMMARY")
    print_df(result["source_controlled_dataset_write_summary"])

    print_section("SCHEMA INTEGRITY AUDIT")
    print_df(result["schema_integrity_audit"])

    print_section("PROVENANCE INTEGRITY AUDIT")
    print_df(result["provenance_integrity_audit"])

    print_section("SAFETY INTEGRITY AUDIT")
    print_df(result["safety_integrity_audit"])

    print_section("REPORT ONLY INTEGRITY AUDIT")
    print_df(result["report_only_integrity_audit"])

    print_section("COMBINED REPORT INTEGRITY AUDIT")
    print_df(result["combined_integrity_audit"])

    print_section("REPORT INTEGRITY SUMMARY")
    print_df(result["report_integrity_summary"])

    print_section("VALIDATION CHECKS")
    print_df(result["checks"])

    print()
    print("ARCHIVOS GENERADOS")
    print("=" * 100)
    print("- reports/phase_9_8_long_forward_observation_report_integrity_v1/long_forward_observation_report_integrity_summary_v1.csv")
    print("- reports/phase_9_8_long_forward_observation_report_integrity_v1/phase_9_7_source_summary_v1.csv")
    print("- reports/phase_9_8_long_forward_observation_report_integrity_v1/phase_9_7_source_controlled_report_write_v1.csv")
    print("- reports/phase_9_8_long_forward_observation_report_integrity_v1/phase_9_7_source_controlled_write_audit_v1.csv")
    print("- reports/phase_9_8_long_forward_observation_report_integrity_v1/phase_9_7_source_controlled_dataset_write_summary_v1.csv")
    print("- reports/phase_9_8_long_forward_observation_report_integrity_v1/long_forward_observation_report_schema_integrity_audit_v1.csv")
    print("- reports/phase_9_8_long_forward_observation_report_integrity_v1/long_forward_observation_report_provenance_integrity_audit_v1.csv")
    print("- reports/phase_9_8_long_forward_observation_report_integrity_v1/long_forward_observation_report_safety_integrity_audit_v1.csv")
    print("- reports/phase_9_8_long_forward_observation_report_integrity_v1/long_forward_observation_report_only_integrity_audit_v1.csv")
    print("- reports/phase_9_8_long_forward_observation_report_integrity_v1/long_forward_observation_report_integrity_audit_v1.csv")
    print("- reports/phase_9_8_long_forward_observation_report_integrity_v1/long_forward_observation_report_integrity_summary_table_v1.csv")
    print("- reports/phase_9_8_long_forward_observation_report_integrity_v1/long_forward_observation_report_integrity_checks_v1.csv")
    print()
    print("Restriccion: Phase 9.8 audita integridad del reporte controlado; no escribe dataset oficial ni aprueba ejecucion.")


if __name__ == "__main__":
    main()