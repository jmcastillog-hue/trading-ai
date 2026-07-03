from __future__ import annotations

import pandas as pd

from src.long_side.long_forward_observation_report_only_dry_run_execution_review_v1 import (
    validate_long_forward_observation_report_only_dry_run_execution_review,
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
    print("PHASE 10.6 LONG FORWARD OBSERVATION REPORT-ONLY DRY-RUN EXECUTION REVIEW")
    print("=" * 100)
    print("Purpose: review readiness for future controlled report-only LONG dry-run run")
    print("Restriction: review only. No dry-run run performed. No forward observation start. No market execution.")
    print()

    result = validate_long_forward_observation_report_only_dry_run_execution_review()

    print_section("PHASE 10.6 VALIDATION SUMMARY")
    print_df(result["summary"])

    print_section("PHASE 10.5 SOURCE SUMMARY")
    print_df(result["source_phase_10_5_summary"])

    print_section("SOURCE REPORT-ONLY DRY-RUN SCHEMA")
    print_df(result["source_report_only_dry_run_schema"])

    print_section("SOURCE REPORT-ONLY DRY-RUN DESIGN COMPONENTS")
    print_df(result["source_report_only_dry_run_design_components"])

    print_section("SOURCE REPORT-ONLY DRY-RUN DESIGN RULES")
    print_df(result["source_report_only_dry_run_design_rules"])

    print_section("SOURCE REPORT-ONLY DRY-RUN DESIGN REQUIREMENTS")
    print_df(result["source_report_only_dry_run_design_requirements"])

    print_section("SOURCE REPORT-ONLY DRY-RUN DESIGN BOUNDARY MATRIX")
    print_df(result["source_report_only_dry_run_design_boundary_matrix"])

    print_section("SOURCE REPORT-ONLY DRY-RUN DESIGN SAFETY MATRIX")
    print_df(result["source_report_only_dry_run_design_safety_matrix"])

    print_section("SOURCE REPORT-ONLY DRY-RUN DESIGN DECISION")
    print_df(result["source_report_only_dry_run_design_decision"])

    print_section("SOURCE CHECKS")
    print_df(result["source_checks"])

    print_section("REPORT-ONLY DRY-RUN EXECUTION REVIEW CONTROLS")
    print_df(result["report_only_dry_run_execution_review_controls"])

    print_section("REPORT-ONLY DRY-RUN EXECUTION REVIEW RULES")
    print_df(result["report_only_dry_run_execution_review_rules"])

    print_section("REPORT-ONLY DRY-RUN EXECUTION REVIEW REQUIREMENTS")
    print_df(result["report_only_dry_run_execution_review_requirements"])

    print_section("REPORT-ONLY DRY-RUN EXECUTION REVIEW BOUNDARY MATRIX")
    print_df(result["report_only_dry_run_execution_review_boundary_matrix"])

    print_section("REPORT-ONLY DRY-RUN EXECUTION REVIEW SAFETY MATRIX")
    print_df(result["report_only_dry_run_execution_review_safety_matrix"])

    print_section("REPORT-ONLY DRY-RUN EXECUTION REVIEW DECISION")
    print_df(result["report_only_dry_run_execution_review_decision"])

    print_section("VALIDATION CHECKS")
    print_df(result["checks"])

    print()
    print("ARCHIVOS GENERADOS")
    print("=" * 100)
    print("- reports/phase_10_6_long_forward_observation_report_only_dry_run_execution_review_v1/long_forward_observation_report_only_dry_run_execution_review_summary_v1.csv")
    print("- reports/phase_10_6_long_forward_observation_report_only_dry_run_execution_review_v1/phase_10_5_source_summary_v1.csv")
    print("- reports/phase_10_6_long_forward_observation_report_only_dry_run_execution_review_v1/phase_10_5_source_report_only_dry_run_schema_v1.csv")
    print("- reports/phase_10_6_long_forward_observation_report_only_dry_run_execution_review_v1/phase_10_5_source_report_only_dry_run_design_components_v1.csv")
    print("- reports/phase_10_6_long_forward_observation_report_only_dry_run_execution_review_v1/phase_10_5_source_report_only_dry_run_design_rules_v1.csv")
    print("- reports/phase_10_6_long_forward_observation_report_only_dry_run_execution_review_v1/phase_10_5_source_report_only_dry_run_design_requirements_v1.csv")
    print("- reports/phase_10_6_long_forward_observation_report_only_dry_run_execution_review_v1/phase_10_5_source_report_only_dry_run_design_boundary_matrix_v1.csv")
    print("- reports/phase_10_6_long_forward_observation_report_only_dry_run_execution_review_v1/phase_10_5_source_report_only_dry_run_design_safety_matrix_v1.csv")
    print("- reports/phase_10_6_long_forward_observation_report_only_dry_run_execution_review_v1/phase_10_5_source_report_only_dry_run_design_decision_v1.csv")
    print("- reports/phase_10_6_long_forward_observation_report_only_dry_run_execution_review_v1/phase_10_5_source_checks_v1.csv")
    print("- reports/phase_10_6_long_forward_observation_report_only_dry_run_execution_review_v1/long_forward_observation_report_only_dry_run_execution_review_controls_v1.csv")
    print("- reports/phase_10_6_long_forward_observation_report_only_dry_run_execution_review_v1/long_forward_observation_report_only_dry_run_execution_review_rules_v1.csv")
    print("- reports/phase_10_6_long_forward_observation_report_only_dry_run_execution_review_v1/long_forward_observation_report_only_dry_run_execution_review_requirements_v1.csv")
    print("- reports/phase_10_6_long_forward_observation_report_only_dry_run_execution_review_v1/long_forward_observation_report_only_dry_run_execution_review_boundary_matrix_v1.csv")
    print("- reports/phase_10_6_long_forward_observation_report_only_dry_run_execution_review_v1/long_forward_observation_report_only_dry_run_execution_review_safety_matrix_v1.csv")
    print("- reports/phase_10_6_long_forward_observation_report_only_dry_run_execution_review_v1/long_forward_observation_report_only_dry_run_execution_review_decision_v1.csv")
    print("- reports/phase_10_6_long_forward_observation_report_only_dry_run_execution_review_v1/long_forward_observation_report_only_dry_run_execution_review_checks_v1.csv")
    print()
    print("Restriccion: Phase 10.6 revisa ejecucion futura report-only; no ejecuta dry-run ni aprueba ejecucion de mercado.")


if __name__ == "__main__":
    main()