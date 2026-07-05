from __future__ import annotations

import pandas as pd

from src.long_side.long_forward_observation_controlled_report_only_dry_run_run_v1 import (
    validate_long_forward_observation_controlled_report_only_dry_run_run,
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
    print("PHASE 10.7 LONG FORWARD OBSERVATION CONTROLLED REPORT-ONLY DRY-RUN RUN")
    print("=" * 100)
    print("Purpose: run controlled report-only LONG dry-run artifact")
    print("Restriction: report-only run. No forward observation start. No official evidence. No market execution.")
    print()

    result = validate_long_forward_observation_controlled_report_only_dry_run_run()

    print_section("PHASE 10.7 VALIDATION SUMMARY")
    print_df(result["summary"])

    print_section("PHASE 10.6 SOURCE SUMMARY")
    print_df(result["source_phase_10_6_summary"])

    print_section("SOURCE REPORT-ONLY DRY-RUN SCHEMA")
    print_df(result["source_report_only_dry_run_schema"])

    print_section("SOURCE EXECUTION REVIEW CONTROLS")
    print_df(result["source_execution_review_controls"])

    print_section("SOURCE EXECUTION REVIEW RULES")
    print_df(result["source_execution_review_rules"])

    print_section("SOURCE EXECUTION REVIEW REQUIREMENTS")
    print_df(result["source_execution_review_requirements"])

    print_section("SOURCE EXECUTION REVIEW BOUNDARY MATRIX")
    print_df(result["source_execution_review_boundary_matrix"])

    print_section("SOURCE EXECUTION REVIEW SAFETY MATRIX")
    print_df(result["source_execution_review_safety_matrix"])

    print_section("SOURCE EXECUTION REVIEW DECISION")
    print_df(result["source_execution_review_decision"])

    print_section("SOURCE CHECKS")
    print_df(result["source_checks"])

    print_section("CONTROLLED REPORT-ONLY DRY-RUN ROWS")
    print_df(result["controlled_report_only_dry_run_rows"])

    print_section("RUN SCHEMA COMPATIBILITY")
    print_df(result["run_schema_compatibility"])

    print_section("RUN ASSERTIONS")
    print_df(result["run_assertions"])

    print_section("RUN REQUIREMENTS")
    print_df(result["run_requirements"])

    print_section("RUN BOUNDARY MATRIX")
    print_df(result["run_boundary_matrix"])

    print_section("RUN SAFETY MATRIX")
    print_df(result["run_safety_matrix"])

    print_section("RUN DECISION")
    print_df(result["run_decision"])

    print_section("VALIDATION CHECKS")
    print_df(result["checks"])

    print()
    print("ARCHIVOS GENERADOS")
    print("=" * 100)
    print("- reports/phase_10_7_long_forward_observation_controlled_report_only_dry_run_run_v1/long_forward_observation_controlled_report_only_dry_run_summary_v1.csv")
    print("- reports/phase_10_7_long_forward_observation_controlled_report_only_dry_run_run_v1/phase_10_6_source_summary_v1.csv")
    print("- reports/phase_10_7_long_forward_observation_controlled_report_only_dry_run_run_v1/phase_10_6_source_report_only_dry_run_schema_v1.csv")
    print("- reports/phase_10_7_long_forward_observation_controlled_report_only_dry_run_run_v1/phase_10_6_source_execution_review_controls_v1.csv")
    print("- reports/phase_10_7_long_forward_observation_controlled_report_only_dry_run_run_v1/phase_10_6_source_execution_review_rules_v1.csv")
    print("- reports/phase_10_7_long_forward_observation_controlled_report_only_dry_run_run_v1/phase_10_6_source_execution_review_requirements_v1.csv")
    print("- reports/phase_10_7_long_forward_observation_controlled_report_only_dry_run_run_v1/phase_10_6_source_execution_review_boundary_matrix_v1.csv")
    print("- reports/phase_10_7_long_forward_observation_controlled_report_only_dry_run_run_v1/phase_10_6_source_execution_review_safety_matrix_v1.csv")
    print("- reports/phase_10_7_long_forward_observation_controlled_report_only_dry_run_run_v1/phase_10_6_source_execution_review_decision_v1.csv")
    print("- reports/phase_10_7_long_forward_observation_controlled_report_only_dry_run_run_v1/phase_10_6_source_checks_v1.csv")
    print("- reports/phase_10_7_long_forward_observation_controlled_report_only_dry_run_run_v1/long_forward_observation_controlled_report_only_dry_run_rows_v1.csv")
    print("- reports/phase_10_7_long_forward_observation_controlled_report_only_dry_run_run_v1/long_forward_observation_controlled_report_only_dry_run_schema_compatibility_v1.csv")
    print("- reports/phase_10_7_long_forward_observation_controlled_report_only_dry_run_run_v1/long_forward_observation_controlled_report_only_dry_run_assertions_v1.csv")
    print("- reports/phase_10_7_long_forward_observation_controlled_report_only_dry_run_run_v1/long_forward_observation_controlled_report_only_dry_run_requirements_v1.csv")
    print("- reports/phase_10_7_long_forward_observation_controlled_report_only_dry_run_run_v1/long_forward_observation_controlled_report_only_dry_run_boundary_matrix_v1.csv")
    print("- reports/phase_10_7_long_forward_observation_controlled_report_only_dry_run_run_v1/long_forward_observation_controlled_report_only_dry_run_safety_matrix_v1.csv")
    print("- reports/phase_10_7_long_forward_observation_controlled_report_only_dry_run_run_v1/long_forward_observation_controlled_report_only_dry_run_decision_v1.csv")
    print("- reports/phase_10_7_long_forward_observation_controlled_report_only_dry_run_run_v1/long_forward_observation_controlled_report_only_dry_run_checks_v1.csv")
    print()
    print("Restriccion: Phase 10.7 corre solo un dry-run report-only; no inicia forward observation ni aprueba ejecucion de mercado.")


if __name__ == "__main__":
    main()