from __future__ import annotations

import pandas as pd

from src.long_side.long_forward_observation_phase_10_15_controlled_start_activation_report_only_dry_run_run_v1 import (
    validate_long_forward_observation_controlled_start_activation_report_only_dry_run_run,
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
    print("PHASE 10.15 LONG FORWARD OBSERVATION CONTROLLED START ACTIVATION REPORT-ONLY DRY-RUN RUN")
    print("=" * 100)
    print("Purpose: run one controlled report-only dry-run artifact")
    print("Restriction: report-only artifact. No forward observation start. No official evidence. No live signals. No market execution.")
    print()

    result = validate_long_forward_observation_controlled_start_activation_report_only_dry_run_run()

    print_section("PHASE 10.15 VALIDATION SUMMARY")
    print_df(result["summary"])

    print_section("PHASE 10.14 SOURCE SUMMARY")
    print_df(result["source_phase_10_14_summary"])

    print_section("SOURCE REPORT-ONLY DRY-RUN DESIGN SCHEMA")
    print_df(result["source_report_only_dry_run_design_schema"])

    print_section("SOURCE REPORT-ONLY DRY-RUN DESIGN COMPONENTS")
    print_df(result["source_report_only_dry_run_design_components"])

    print_section("SOURCE REPORT-ONLY DRY-RUN DESIGN CONTROLS")
    print_df(result["source_report_only_dry_run_design_controls"])

    print_section("SOURCE REPORT-ONLY DRY-RUN DESIGN RULES")
    print_df(result["source_report_only_dry_run_design_rules"])

    print_section("SOURCE REPORT-ONLY DRY-RUN DESIGN REQUIREMENTS")
    print_df(result["source_report_only_dry_run_design_requirements"])

    print_section("SOURCE REPORT-ONLY DRY-RUN DESIGN GUARD MATRIX")
    print_df(result["source_report_only_dry_run_design_guard_matrix"])

    print_section("SOURCE REPORT-ONLY DRY-RUN DESIGN BOUNDARY MATRIX")
    print_df(result["source_report_only_dry_run_design_boundary_matrix"])

    print_section("SOURCE REPORT-ONLY DRY-RUN DESIGN DECISION")
    print_df(result["source_report_only_dry_run_design_decision"])

    print_section("SOURCE CHECKS")
    print_df(result["source_checks"])

    print_section("SOURCE EXECUTION REVIEW ITEMS")
    print_df(result["source_execution_review_items"])

    print_section("SOURCE EXECUTION REVIEW CONTROLS")
    print_df(result["source_execution_review_controls"])

    print_section("SOURCE EXECUTION REVIEW RULES")
    print_df(result["source_execution_review_rules"])

    print_section("SOURCE EXECUTION REVIEW REQUIREMENTS")
    print_df(result["source_execution_review_requirements"])

    print_section("SOURCE EXECUTION REVIEW GUARD MATRIX")
    print_df(result["source_execution_review_guard_matrix"])

    print_section("SOURCE EXECUTION REVIEW BOUNDARY MATRIX")
    print_df(result["source_execution_review_boundary_matrix"])

    print_section("SOURCE EXECUTION REVIEW DECISION")
    print_df(result["source_execution_review_decision"])

    print_section("REPORT-ONLY DRY-RUN OUTPUT")
    print_df(result["report_only_dry_run_output"])

    print_section("REPORT-ONLY DRY-RUN RUN CONTROLS")
    print_df(result["report_only_dry_run_run_controls"])

    print_section("REPORT-ONLY DRY-RUN ROW VALIDATION")
    print_df(result["report_only_dry_run_row_validation"])

    print_section("REPORT-ONLY DRY-RUN RUN RULES")
    print_df(result["report_only_dry_run_run_rules"])

    print_section("REPORT-ONLY DRY-RUN RUN GUARD MATRIX")
    print_df(result["report_only_dry_run_run_guard_matrix"])

    print_section("REPORT-ONLY DRY-RUN RUN REQUIREMENTS")
    print_df(result["report_only_dry_run_run_requirements"])

    print_section("REPORT-ONLY DRY-RUN RUN DECISION")
    print_df(result["report_only_dry_run_run_decision"])

    print_section("VALIDATION CHECKS")
    print_df(result["checks"])

    print()
    print("ARCHIVOS GENERADOS")
    print("=" * 100)
    print("- reports/p10_15_activation_report_only_run_v1/controlled_start_activation_report_only_dry_run_output_v1.csv")
    print("- reports/p10_15_activation_report_only_run_v1/controlled_start_activation_report_only_dry_run_run_summary_v1.csv")
    print("- reports/p10_15_activation_report_only_run_v1/phase_10_14_source_summary_v1.csv")
    print("- reports/p10_15_activation_report_only_run_v1/phase_10_13_source_report_only_dry_run_design_schema_v1.csv")
    print("- reports/p10_15_activation_report_only_run_v1/phase_10_13_source_report_only_dry_run_design_components_v1.csv")
    print("- reports/p10_15_activation_report_only_run_v1/phase_10_13_source_report_only_dry_run_design_controls_v1.csv")
    print("- reports/p10_15_activation_report_only_run_v1/phase_10_13_source_report_only_dry_run_design_rules_v1.csv")
    print("- reports/p10_15_activation_report_only_run_v1/phase_10_13_source_report_only_dry_run_design_requirements_v1.csv")
    print("- reports/p10_15_activation_report_only_run_v1/phase_10_13_source_report_only_dry_run_design_guard_matrix_v1.csv")
    print("- reports/p10_15_activation_report_only_run_v1/phase_10_13_source_report_only_dry_run_design_boundary_matrix_v1.csv")
    print("- reports/p10_15_activation_report_only_run_v1/phase_10_13_source_report_only_dry_run_design_decision_v1.csv")
    print("- reports/p10_15_activation_report_only_run_v1/phase_10_13_source_checks_v1.csv")
    print("- reports/p10_15_activation_report_only_run_v1/phase_10_14_source_execution_review_items_v1.csv")
    print("- reports/p10_15_activation_report_only_run_v1/phase_10_14_source_execution_review_controls_v1.csv")
    print("- reports/p10_15_activation_report_only_run_v1/phase_10_14_source_execution_review_rules_v1.csv")
    print("- reports/p10_15_activation_report_only_run_v1/phase_10_14_source_execution_review_requirements_v1.csv")
    print("- reports/p10_15_activation_report_only_run_v1/phase_10_14_source_execution_review_guard_matrix_v1.csv")
    print("- reports/p10_15_activation_report_only_run_v1/phase_10_14_source_execution_review_boundary_matrix_v1.csv")
    print("- reports/p10_15_activation_report_only_run_v1/phase_10_14_source_execution_review_decision_v1.csv")
    print("- reports/p10_15_activation_report_only_run_v1/controlled_start_activation_report_only_dry_run_run_controls_v1.csv")
    print("- reports/p10_15_activation_report_only_run_v1/controlled_start_activation_report_only_dry_run_row_validation_v1.csv")
    print("- reports/p10_15_activation_report_only_run_v1/controlled_start_activation_report_only_dry_run_run_rules_v1.csv")
    print("- reports/p10_15_activation_report_only_run_v1/controlled_start_activation_report_only_dry_run_run_guard_matrix_v1.csv")
    print("- reports/p10_15_activation_report_only_run_v1/controlled_start_activation_report_only_dry_run_run_requirements_v1.csv")
    print("- reports/p10_15_activation_report_only_run_v1/controlled_start_activation_report_only_dry_run_run_decision_v1.csv")
    print("- reports/p10_15_activation_report_only_run_v1/controlled_start_activation_report_only_dry_run_run_checks_v1.csv")
    print()
    print("Restriccion: Phase 10.15 ejecuta solo dry-run report-only controlado; no inicia forward observation, no crea evidencia oficial ni aprueba ejecucion de mercado.")


if __name__ == "__main__":
    main()