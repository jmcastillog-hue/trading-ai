from __future__ import annotations

import pandas as pd

from src.long_side.long_forward_observation_manual_dry_run_checklist_v1 import (
    validate_long_forward_observation_manual_dry_run_checklist,
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
    print("PHASE 10.3 LONG FORWARD OBSERVATION MANUAL DRY-RUN CHECKLIST")
    print("=" * 100)
    print("Purpose: define checklist before future controlled LONG forward observation dry-run")
    print("Restriction: checklist only. No dry-run execution. No forward observation start. No execution.")
    print()

    result = validate_long_forward_observation_manual_dry_run_checklist()

    print_section("PHASE 10.3 VALIDATION SUMMARY")
    print_df(result["summary"])

    print_section("PHASE 10.2 SOURCE SUMMARY")
    print_df(result["source_phase_10_2_summary"])

    print_section("SOURCE MANUAL PROTOCOL STAGES")
    print_df(result["source_manual_protocol_stages"])

    print_section("SOURCE MANUAL PROTOCOL RULES")
    print_df(result["source_manual_protocol_rules"])

    print_section("SOURCE MANUAL PROTOCOL REQUIREMENTS")
    print_df(result["source_manual_protocol_requirements"])

    print_section("SOURCE MANUAL PROTOCOL BOUNDARY MATRIX")
    print_df(result["source_manual_protocol_boundary_matrix"])

    print_section("SOURCE MANUAL PROTOCOL SAFETY MATRIX")
    print_df(result["source_manual_protocol_safety_matrix"])

    print_section("SOURCE MANUAL START PROTOCOL DECISION")
    print_df(result["source_manual_start_protocol_decision"])

    print_section("SOURCE CHECKS")
    print_df(result["source_checks"])

    print_section("DRY-RUN CHECKLIST ITEMS")
    print_df(result["dry_run_checklist_items"])

    print_section("DRY-RUN CHECKLIST RULES")
    print_df(result["dry_run_checklist_rules"])

    print_section("DRY-RUN CHECKLIST REQUIREMENTS")
    print_df(result["dry_run_checklist_requirements"])

    print_section("DRY-RUN BOUNDARY MATRIX")
    print_df(result["dry_run_boundary_matrix"])

    print_section("DRY-RUN SAFETY MATRIX")
    print_df(result["dry_run_safety_matrix"])

    print_section("MANUAL DRY-RUN CHECKLIST DECISION")
    print_df(result["manual_dry_run_checklist_decision"])

    print_section("VALIDATION CHECKS")
    print_df(result["checks"])

    print()
    print("ARCHIVOS GENERADOS")
    print("=" * 100)
    print("- reports/phase_10_3_long_forward_observation_manual_dry_run_checklist_v1/long_forward_observation_manual_dry_run_checklist_summary_v1.csv")
    print("- reports/phase_10_3_long_forward_observation_manual_dry_run_checklist_v1/phase_10_2_source_summary_v1.csv")
    print("- reports/phase_10_3_long_forward_observation_manual_dry_run_checklist_v1/phase_10_2_source_manual_protocol_stages_v1.csv")
    print("- reports/phase_10_3_long_forward_observation_manual_dry_run_checklist_v1/phase_10_2_source_manual_protocol_rules_v1.csv")
    print("- reports/phase_10_3_long_forward_observation_manual_dry_run_checklist_v1/phase_10_2_source_manual_protocol_requirements_v1.csv")
    print("- reports/phase_10_3_long_forward_observation_manual_dry_run_checklist_v1/phase_10_2_source_manual_protocol_boundary_matrix_v1.csv")
    print("- reports/phase_10_3_long_forward_observation_manual_dry_run_checklist_v1/phase_10_2_source_manual_protocol_safety_matrix_v1.csv")
    print("- reports/phase_10_3_long_forward_observation_manual_dry_run_checklist_v1/phase_10_2_source_manual_start_protocol_decision_v1.csv")
    print("- reports/phase_10_3_long_forward_observation_manual_dry_run_checklist_v1/phase_10_2_source_checks_v1.csv")
    print("- reports/phase_10_3_long_forward_observation_manual_dry_run_checklist_v1/long_forward_observation_manual_dry_run_checklist_items_v1.csv")
    print("- reports/phase_10_3_long_forward_observation_manual_dry_run_checklist_v1/long_forward_observation_manual_dry_run_checklist_rules_v1.csv")
    print("- reports/phase_10_3_long_forward_observation_manual_dry_run_checklist_v1/long_forward_observation_manual_dry_run_checklist_requirements_v1.csv")
    print("- reports/phase_10_3_long_forward_observation_manual_dry_run_checklist_v1/long_forward_observation_manual_dry_run_boundary_matrix_v1.csv")
    print("- reports/phase_10_3_long_forward_observation_manual_dry_run_checklist_v1/long_forward_observation_manual_dry_run_safety_matrix_v1.csv")
    print("- reports/phase_10_3_long_forward_observation_manual_dry_run_checklist_v1/long_forward_observation_manual_dry_run_checklist_decision_v1.csv")
    print("- reports/phase_10_3_long_forward_observation_manual_dry_run_checklist_v1/long_forward_observation_manual_dry_run_checklist_checks_v1.csv")
    print()
    print("Restriccion: Phase 10.3 define checklist dry-run; no ejecuta dry-run ni aprueba ejecucion.")


if __name__ == "__main__":
    main()