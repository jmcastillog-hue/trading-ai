from __future__ import annotations

import pandas as pd

from src.long_side.long_forward_observation_report_only_dry_run_output_integrity_review_v1 import (
    validate_long_forward_observation_report_only_dry_run_output_integrity_review,
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
    print("PHASE 10.8 LONG FORWARD OBSERVATION REPORT-ONLY DRY-RUN OUTPUT INTEGRITY REVIEW")
    print("=" * 100)
    print("Purpose: review controlled report-only LONG dry-run output integrity")
    print("Restriction: review only. No forward observation start. No official evidence. No market execution.")
    print()

    result = validate_long_forward_observation_report_only_dry_run_output_integrity_review()

    print_section("PHASE 10.8 VALIDATION SUMMARY")
    print_df(result["summary"])

    print_section("PHASE 10.7 SOURCE SUMMARY")
    print_df(result["source_phase_10_7_summary"])

    print_section("SOURCE REPORT-ONLY DRY-RUN SCHEMA")
    print_df(result["source_report_only_dry_run_schema"])

    print_section("SOURCE CONTROLLED REPORT-ONLY DRY-RUN ROWS")
    print_df(result["source_controlled_report_only_dry_run_rows"])

    print_section("SOURCE RUN SCHEMA COMPATIBILITY")
    print_df(result["source_run_schema_compatibility"])

    print_section("SOURCE RUN ASSERTIONS")
    print_df(result["source_run_assertions"])

    print_section("SOURCE RUN REQUIREMENTS")
    print_df(result["source_run_requirements"])

    print_section("SOURCE RUN BOUNDARY MATRIX")
    print_df(result["source_run_boundary_matrix"])

    print_section("SOURCE RUN SAFETY MATRIX")
    print_df(result["source_run_safety_matrix"])

    print_section("SOURCE RUN DECISION")
    print_df(result["source_run_decision"])

    print_section("SOURCE CHECKS")
    print_df(result["source_checks"])

    print_section("OUTPUT SCHEMA INTEGRITY")
    print_df(result["output_schema_integrity"])

    print_section("OUTPUT ROW INTEGRITY")
    print_df(result["output_row_integrity"])

    print_section("SUMMARY GUARD INTEGRITY")
    print_df(result["summary_guard_integrity"])

    print_section("OUTPUT INTEGRITY REQUIREMENTS")
    print_df(result["output_integrity_requirements"])

    print_section("OUTPUT INTEGRITY BOUNDARY MATRIX")
    print_df(result["output_integrity_boundary_matrix"])

    print_section("OUTPUT INTEGRITY DECISION")
    print_df(result["output_integrity_decision"])

    print_section("VALIDATION CHECKS")
    print_df(result["checks"])

    print()
    print("ARCHIVOS GENERADOS")
    print("=" * 100)
    print("- reports/phase_10_8_long_forward_observation_report_only_dry_run_output_integrity_review_v1/long_forward_observation_report_only_dry_run_output_integrity_summary_v1.csv")
    print("- reports/phase_10_8_long_forward_observation_report_only_dry_run_output_integrity_review_v1/phase_10_7_source_summary_v1.csv")
    print("- reports/phase_10_8_long_forward_observation_report_only_dry_run_output_integrity_review_v1/phase_10_7_source_report_only_dry_run_schema_v1.csv")
    print("- reports/phase_10_8_long_forward_observation_report_only_dry_run_output_integrity_review_v1/phase_10_7_source_controlled_report_only_dry_run_rows_v1.csv")
    print("- reports/phase_10_8_long_forward_observation_report_only_dry_run_output_integrity_review_v1/phase_10_7_source_run_schema_compatibility_v1.csv")
    print("- reports/phase_10_8_long_forward_observation_report_only_dry_run_output_integrity_review_v1/phase_10_7_source_run_assertions_v1.csv")
    print("- reports/phase_10_8_long_forward_observation_report_only_dry_run_output_integrity_review_v1/phase_10_7_source_run_requirements_v1.csv")
    print("- reports/phase_10_8_long_forward_observation_report_only_dry_run_output_integrity_review_v1/phase_10_7_source_run_boundary_matrix_v1.csv")
    print("- reports/phase_10_8_long_forward_observation_report_only_dry_run_output_integrity_review_v1/phase_10_7_source_run_safety_matrix_v1.csv")
    print("- reports/phase_10_8_long_forward_observation_report_only_dry_run_output_integrity_review_v1/phase_10_7_source_run_decision_v1.csv")
    print("- reports/phase_10_8_long_forward_observation_report_only_dry_run_output_integrity_review_v1/phase_10_7_source_checks_v1.csv")
    print("- reports/phase_10_8_long_forward_observation_report_only_dry_run_output_integrity_review_v1/long_forward_observation_report_only_dry_run_output_schema_integrity_v1.csv")
    print("- reports/phase_10_8_long_forward_observation_report_only_dry_run_output_integrity_review_v1/long_forward_observation_report_only_dry_run_output_row_integrity_v1.csv")
    print("- reports/phase_10_8_long_forward_observation_report_only_dry_run_output_integrity_review_v1/long_forward_observation_report_only_dry_run_output_summary_guard_integrity_v1.csv")
    print("- reports/phase_10_8_long_forward_observation_report_only_dry_run_output_integrity_review_v1/long_forward_observation_report_only_dry_run_output_integrity_requirements_v1.csv")
    print("- reports/phase_10_8_long_forward_observation_report_only_dry_run_output_integrity_review_v1/long_forward_observation_report_only_dry_run_output_integrity_boundary_matrix_v1.csv")
    print("- reports/phase_10_8_long_forward_observation_report_only_dry_run_output_integrity_review_v1/long_forward_observation_report_only_dry_run_output_integrity_decision_v1.csv")
    print("- reports/phase_10_8_long_forward_observation_report_only_dry_run_output_integrity_review_v1/long_forward_observation_report_only_dry_run_output_integrity_checks_v1.csv")
    print()
    print("Restriccion: Phase 10.8 revisa integridad del output report-only; no inicia forward observation ni aprueba ejecucion de mercado.")


if __name__ == "__main__":
    main()