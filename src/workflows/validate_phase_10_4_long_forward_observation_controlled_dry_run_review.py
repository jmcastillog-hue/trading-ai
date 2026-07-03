from __future__ import annotations

import pandas as pd

from src.long_side.long_forward_observation_controlled_dry_run_review_v1 import (
    validate_long_forward_observation_controlled_dry_run_review,
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
    print("PHASE 10.4 LONG FORWARD OBSERVATION CONTROLLED DRY-RUN REVIEW")
    print("=" * 100)
    print("Purpose: review readiness for future report-only controlled LONG dry-run design")
    print("Restriction: review only. No dry-run execution. No forward observation start. No execution.")
    print()

    result = validate_long_forward_observation_controlled_dry_run_review()

    print_section("PHASE 10.4 VALIDATION SUMMARY")
    print_df(result["summary"])

    print_section("PHASE 10.3 SOURCE SUMMARY")
    print_df(result["source_phase_10_3_summary"])

    print_section("SOURCE DRY-RUN CHECKLIST ITEMS")
    print_df(result["source_dry_run_checklist_items"])

    print_section("SOURCE DRY-RUN CHECKLIST RULES")
    print_df(result["source_dry_run_checklist_rules"])

    print_section("SOURCE DRY-RUN CHECKLIST REQUIREMENTS")
    print_df(result["source_dry_run_checklist_requirements"])

    print_section("SOURCE DRY-RUN BOUNDARY MATRIX")
    print_df(result["source_dry_run_boundary_matrix"])

    print_section("SOURCE DRY-RUN SAFETY MATRIX")
    print_df(result["source_dry_run_safety_matrix"])

    print_section("SOURCE MANUAL DRY-RUN CHECKLIST DECISION")
    print_df(result["source_manual_dry_run_checklist_decision"])

    print_section("SOURCE CHECKS")
    print_df(result["source_checks"])

    print_section("CONTROLLED DRY-RUN REVIEW CONTROLS")
    print_df(result["controlled_dry_run_review_controls"])

    print_section("CONTROLLED DRY-RUN REVIEW RULES")
    print_df(result["controlled_dry_run_review_rules"])

    print_section("CONTROLLED DRY-RUN REVIEW REQUIREMENTS")
    print_df(result["controlled_dry_run_review_requirements"])

    print_section("CONTROLLED DRY-RUN REVIEW BOUNDARY MATRIX")
    print_df(result["controlled_dry_run_review_boundary_matrix"])

    print_section("CONTROLLED DRY-RUN REVIEW SAFETY MATRIX")
    print_df(result["controlled_dry_run_review_safety_matrix"])

    print_section("CONTROLLED DRY-RUN REVIEW DECISION")
    print_df(result["controlled_dry_run_review_decision"])

    print_section("VALIDATION CHECKS")
    print_df(result["checks"])

    print()
    print("ARCHIVOS GENERADOS")
    print("=" * 100)
    print("- reports/phase_10_4_long_forward_observation_controlled_dry_run_review_v1/long_forward_observation_controlled_dry_run_review_summary_v1.csv")
    print("- reports/phase_10_4_long_forward_observation_controlled_dry_run_review_v1/phase_10_3_source_summary_v1.csv")
    print("- reports/phase_10_4_long_forward_observation_controlled_dry_run_review_v1/phase_10_3_source_dry_run_checklist_items_v1.csv")
    print("- reports/phase_10_4_long_forward_observation_controlled_dry_run_review_v1/phase_10_3_source_dry_run_checklist_rules_v1.csv")
    print("- reports/phase_10_4_long_forward_observation_controlled_dry_run_review_v1/phase_10_3_source_dry_run_checklist_requirements_v1.csv")
    print("- reports/phase_10_4_long_forward_observation_controlled_dry_run_review_v1/phase_10_3_source_dry_run_boundary_matrix_v1.csv")
    print("- reports/phase_10_4_long_forward_observation_controlled_dry_run_review_v1/phase_10_3_source_dry_run_safety_matrix_v1.csv")
    print("- reports/phase_10_4_long_forward_observation_controlled_dry_run_review_v1/phase_10_3_source_manual_dry_run_checklist_decision_v1.csv")
    print("- reports/phase_10_4_long_forward_observation_controlled_dry_run_review_v1/phase_10_3_source_checks_v1.csv")
    print("- reports/phase_10_4_long_forward_observation_controlled_dry_run_review_v1/long_forward_observation_controlled_dry_run_review_controls_v1.csv")
    print("- reports/phase_10_4_long_forward_observation_controlled_dry_run_review_v1/long_forward_observation_controlled_dry_run_review_rules_v1.csv")
    print("- reports/phase_10_4_long_forward_observation_controlled_dry_run_review_v1/long_forward_observation_controlled_dry_run_review_requirements_v1.csv")
    print("- reports/phase_10_4_long_forward_observation_controlled_dry_run_review_v1/long_forward_observation_controlled_dry_run_review_boundary_matrix_v1.csv")
    print("- reports/phase_10_4_long_forward_observation_controlled_dry_run_review_v1/long_forward_observation_controlled_dry_run_review_safety_matrix_v1.csv")
    print("- reports/phase_10_4_long_forward_observation_controlled_dry_run_review_v1/long_forward_observation_controlled_dry_run_review_decision_v1.csv")
    print("- reports/phase_10_4_long_forward_observation_controlled_dry_run_review_v1/long_forward_observation_controlled_dry_run_review_checks_v1.csv")
    print()
    print("Restriccion: Phase 10.4 revisa dry-run controlado; no ejecuta dry-run ni aprueba ejecucion.")


if __name__ == "__main__":
    main()