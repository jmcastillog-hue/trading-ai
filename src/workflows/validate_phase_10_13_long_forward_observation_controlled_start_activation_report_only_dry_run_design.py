from __future__ import annotations

import pandas as pd

from src.long_side.long_forward_observation_phase_10_13_controlled_start_activation_report_only_dry_run_design_v1 import (
    validate_long_forward_observation_controlled_start_activation_report_only_dry_run_design,
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
    print("PHASE 10.13 LONG FORWARD OBSERVATION CONTROLLED START ACTIVATION REPORT-ONLY DRY-RUN DESIGN")
    print("=" * 100)
    print("Purpose: design a future report-only dry-run execution review")
    print("Restriction: design only. No dry-run execution. No forward observation start. No official evidence. No market execution.")
    print()

    result = validate_long_forward_observation_controlled_start_activation_report_only_dry_run_design()

    print_section("PHASE 10.13 VALIDATION SUMMARY")
    print_df(result["summary"])

    print_section("PHASE 10.12 SOURCE SUMMARY")
    print_df(result["source_phase_10_12_summary"])

    print_section("SOURCE ACTIVATION DRY-RUN REVIEW ITEMS")
    print_df(result["source_activation_dry_run_review_items"])

    print_section("SOURCE ACTIVATION DRY-RUN REVIEW CONTROLS")
    print_df(result["source_activation_dry_run_review_controls"])

    print_section("SOURCE ACTIVATION DRY-RUN REVIEW RULES")
    print_df(result["source_activation_dry_run_review_rules"])

    print_section("SOURCE ACTIVATION DRY-RUN REVIEW REQUIREMENTS")
    print_df(result["source_activation_dry_run_review_requirements"])

    print_section("SOURCE ACTIVATION DRY-RUN REVIEW GUARD MATRIX")
    print_df(result["source_activation_dry_run_review_guard_matrix"])

    print_section("SOURCE ACTIVATION DRY-RUN REVIEW BOUNDARY MATRIX")
    print_df(result["source_activation_dry_run_review_boundary_matrix"])

    print_section("SOURCE ACTIVATION DRY-RUN REVIEW DECISION")
    print_df(result["source_activation_dry_run_review_decision"])

    print_section("SOURCE CHECKS")
    print_df(result["source_checks"])

    print_section("REPORT-ONLY DRY-RUN DESIGN SCHEMA")
    print_df(result["report_only_dry_run_design_schema"])

    print_section("REPORT-ONLY DRY-RUN DESIGN COMPONENTS")
    print_df(result["report_only_dry_run_design_components"])

    print_section("REPORT-ONLY DRY-RUN DESIGN CONTROLS")
    print_df(result["report_only_dry_run_design_controls"])

    print_section("REPORT-ONLY DRY-RUN DESIGN RULES")
    print_df(result["report_only_dry_run_design_rules"])

    print_section("REPORT-ONLY DRY-RUN DESIGN REQUIREMENTS")
    print_df(result["report_only_dry_run_design_requirements"])

    print_section("REPORT-ONLY DRY-RUN DESIGN GUARD MATRIX")
    print_df(result["report_only_dry_run_design_guard_matrix"])

    print_section("REPORT-ONLY DRY-RUN DESIGN BOUNDARY MATRIX")
    print_df(result["report_only_dry_run_design_boundary_matrix"])

    print_section("REPORT-ONLY DRY-RUN DESIGN DECISION")
    print_df(result["report_only_dry_run_design_decision"])

    print_section("VALIDATION CHECKS")
    print_df(result["checks"])

    print()
    print("ARCHIVOS GENERADOS")
    print("=" * 100)
    print("- reports/phase_10_13_long_forward_observation_controlled_start_activation_report_only_dry_run_design_v1/long_forward_observation_controlled_start_activation_report_only_dry_run_design_summary_v1.csv")
    print("- reports/phase_10_13_long_forward_observation_controlled_start_activation_report_only_dry_run_design_v1/phase_10_12_source_summary_v1.csv")
    print("- reports/phase_10_13_long_forward_observation_controlled_start_activation_report_only_dry_run_design_v1/phase_10_12_source_activation_dry_run_review_items_v1.csv")
    print("- reports/phase_10_13_long_forward_observation_controlled_start_activation_report_only_dry_run_design_v1/phase_10_12_source_activation_dry_run_review_controls_v1.csv")
    print("- reports/phase_10_13_long_forward_observation_controlled_start_activation_report_only_dry_run_design_v1/phase_10_12_source_activation_dry_run_review_rules_v1.csv")
    print("- reports/phase_10_13_long_forward_observation_controlled_start_activation_report_only_dry_run_design_v1/phase_10_12_source_activation_dry_run_review_requirements_v1.csv")
    print("- reports/phase_10_13_long_forward_observation_controlled_start_activation_report_only_dry_run_design_v1/phase_10_12_source_activation_dry_run_review_guard_matrix_v1.csv")
    print("- reports/phase_10_13_long_forward_observation_controlled_start_activation_report_only_dry_run_design_v1/phase_10_12_source_activation_dry_run_review_boundary_matrix_v1.csv")
    print("- reports/phase_10_13_long_forward_observation_controlled_start_activation_report_only_dry_run_design_v1/phase_10_12_source_activation_dry_run_review_decision_v1.csv")
    print("- reports/phase_10_13_long_forward_observation_controlled_start_activation_report_only_dry_run_design_v1/phase_10_12_source_checks_v1.csv")
    print("- reports/phase_10_13_long_forward_observation_controlled_start_activation_report_only_dry_run_design_v1/long_forward_observation_controlled_start_activation_report_only_dry_run_design_schema_v1.csv")
    print("- reports/phase_10_13_long_forward_observation_controlled_start_activation_report_only_dry_run_design_v1/long_forward_observation_controlled_start_activation_report_only_dry_run_design_components_v1.csv")
    print("- reports/phase_10_13_long_forward_observation_controlled_start_activation_report_only_dry_run_design_v1/long_forward_observation_controlled_start_activation_report_only_dry_run_design_controls_v1.csv")
    print("- reports/phase_10_13_long_forward_observation_controlled_start_activation_report_only_dry_run_design_v1/long_forward_observation_controlled_start_activation_report_only_dry_run_design_rules_v1.csv")
    print("- reports/phase_10_13_long_forward_observation_controlled_start_activation_report_only_dry_run_design_v1/long_forward_observation_controlled_start_activation_report_only_dry_run_design_requirements_v1.csv")
    print("- reports/phase_10_13_long_forward_observation_controlled_start_activation_report_only_dry_run_design_v1/long_forward_observation_controlled_start_activation_report_only_dry_run_design_guard_matrix_v1.csv")
    print("- reports/phase_10_13_long_forward_observation_controlled_start_activation_report_only_dry_run_design_v1/long_forward_observation_controlled_start_activation_report_only_dry_run_design_boundary_matrix_v1.csv")
    print("- reports/phase_10_13_long_forward_observation_controlled_start_activation_report_only_dry_run_design_v1/long_forward_observation_controlled_start_activation_report_only_dry_run_design_decision_v1.csv")
    print("- reports/phase_10_13_long_forward_observation_controlled_start_activation_report_only_dry_run_design_v1/long_forward_observation_controlled_start_activation_report_only_dry_run_design_checks_v1.csv")
    print()
    print("Restriccion: Phase 10.13 valida solo diseño report-only; no ejecuta dry-run, no inicia forward observation ni aprueba ejecucion de mercado.")


if __name__ == "__main__":
    main()