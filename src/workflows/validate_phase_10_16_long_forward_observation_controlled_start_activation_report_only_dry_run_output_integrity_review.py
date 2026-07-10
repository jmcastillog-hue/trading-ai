from __future__ import annotations

import pandas as pd

from src.long_side.long_forward_observation_phase_10_16_controlled_start_activation_report_only_dry_run_output_integrity_review_v1 import (
    validate_long_forward_observation_controlled_start_activation_report_only_dry_run_output_integrity_review,
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
    print("PHASE 10.16 LONG FORWARD OBSERVATION CONTROLLED START ACTIVATION REPORT-ONLY DRY-RUN OUTPUT INTEGRITY REVIEW")
    print("=" * 100)
    print("Purpose: review integrity of the controlled report-only dry-run output artifact")
    print("Restriction: integrity review only. No new dry-run. No forward observation start. No official evidence. No market execution.")
    print()

    result = validate_long_forward_observation_controlled_start_activation_report_only_dry_run_output_integrity_review()

    print_section("PHASE 10.16 VALIDATION SUMMARY")
    print_df(result["summary"])

    print_section("PHASE 10.15 SOURCE SUMMARY")
    print_df(result["source_phase_10_15_summary"])

    print_section("SOURCE REPORT-ONLY DRY-RUN OUTPUT")
    print_df(result["source_report_only_dry_run_output"])

    print_section("SOURCE REPORT-ONLY DRY-RUN DESIGN SCHEMA")
    print_df(result["source_report_only_dry_run_design_schema"])

    print_section("SOURCE RUN DECISION")
    print_df(result["source_run_decision"])

    print_section("SOURCE RUN CONTROLS")
    print_df(result["source_run_controls"])

    print_section("SOURCE ROW VALIDATION")
    print_df(result["source_row_validation"])

    print_section("SOURCE RUN RULES")
    print_df(result["source_run_rules"])

    print_section("SOURCE RUN REQUIREMENTS")
    print_df(result["source_run_requirements"])

    print_section("SOURCE RUN GUARD MATRIX")
    print_df(result["source_run_guard_matrix"])

    print_section("SOURCE CHECKS")
    print_df(result["source_checks"])

    print_section("OUTPUT INTEGRITY CONTROLS")
    print_df(result["output_integrity_controls"])

    print_section("OUTPUT INTEGRITY VALIDATION")
    print_df(result["output_integrity_validation"])

    print_section("OUTPUT INTEGRITY RULES")
    print_df(result["output_integrity_rules"])

    print_section("OUTPUT INTEGRITY REQUIREMENTS")
    print_df(result["output_integrity_requirements"])

    print_section("OUTPUT INTEGRITY GUARD MATRIX")
    print_df(result["output_integrity_guard_matrix"])

    print_section("OUTPUT INTEGRITY DECISION")
    print_df(result["output_integrity_decision"])

    print_section("VALIDATION CHECKS")
    print_df(result["checks"])

    print()
    print("ARCHIVOS GENERADOS")
    print("=" * 100)
    print("- reports/p10_16_activation_output_integrity_v1/output_integrity_review_summary_v1.csv")
    print("- reports/p10_16_activation_output_integrity_v1/phase_10_15_source_summary_v1.csv")
    print("- reports/p10_16_activation_output_integrity_v1/phase_10_15_source_report_only_dry_run_output_v1.csv")
    print("- reports/p10_16_activation_output_integrity_v1/phase_10_13_source_report_only_dry_run_design_schema_v1.csv")
    print("- reports/p10_16_activation_output_integrity_v1/phase_10_15_source_run_decision_v1.csv")
    print("- reports/p10_16_activation_output_integrity_v1/phase_10_15_source_run_controls_v1.csv")
    print("- reports/p10_16_activation_output_integrity_v1/phase_10_15_source_row_validation_v1.csv")
    print("- reports/p10_16_activation_output_integrity_v1/phase_10_15_source_run_rules_v1.csv")
    print("- reports/p10_16_activation_output_integrity_v1/phase_10_15_source_run_requirements_v1.csv")
    print("- reports/p10_16_activation_output_integrity_v1/phase_10_15_source_run_guard_matrix_v1.csv")
    print("- reports/p10_16_activation_output_integrity_v1/phase_10_15_source_checks_v1.csv")
    print("- reports/p10_16_activation_output_integrity_v1/output_integrity_review_controls_v1.csv")
    print("- reports/p10_16_activation_output_integrity_v1/output_integrity_review_validations_v1.csv")
    print("- reports/p10_16_activation_output_integrity_v1/output_integrity_review_rules_v1.csv")
    print("- reports/p10_16_activation_output_integrity_v1/output_integrity_review_requirements_v1.csv")
    print("- reports/p10_16_activation_output_integrity_v1/output_integrity_review_guard_matrix_v1.csv")
    print("- reports/p10_16_activation_output_integrity_v1/output_integrity_review_decision_v1.csv")
    print("- reports/p10_16_activation_output_integrity_v1/output_integrity_review_checks_v1.csv")
    print()
    print("Restriccion: Phase 10.16 revisa solo integridad de output report-only; no ejecuta nuevo dry-run, no inicia forward observation ni aprueba ejecucion de mercado.")


if __name__ == "__main__":
    main()