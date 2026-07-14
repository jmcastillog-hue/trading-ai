from __future__ import annotations

import pandas as pd

from src.long_side.long_forward_observation_phase_10_21_controlled_start_dry_run_design_v1 import (
    validate_long_forward_observation_controlled_start_dry_run_design,
)


def print_section(title: str) -> None:
    print()
    print(title)
    print("=" * 100)


def print_df(df: pd.DataFrame) -> None:
    if df.empty:
        print("Sin registros.")
        return

    print(df.to_string(index=False))


def main() -> None:
    print(
        "PHASE 10.21 LONG FORWARD OBSERVATION CONTROLLED START DRY-RUN DESIGN"
    )
    print("=" * 100)
    print(
        "Purpose: design the future controlled forward observation start dry-run."
    )
    print(
        "Restriction: no dry-run execution, no forward observation start, "
        "no official evidence, no signals, no alerts, no paper trading, "
        "no market execution."
    )

    result = validate_long_forward_observation_controlled_start_dry_run_design()

    sections = [
        ("PHASE 10.21 VALIDATION SUMMARY", "summary"),
        ("PHASE 10.20 SOURCE SUMMARY", "source_phase_10_20_summary"),
        ("SOURCE ACTIVATION OUTPUT", "source_activation_output"),
        ("SOURCE INTEGRITY VALIDATION", "source_integrity_validation"),
        ("SOURCE INTEGRITY CONTROLS", "source_integrity_controls"),
        ("SOURCE INTEGRITY RULES", "source_integrity_rules"),
        ("SOURCE INTEGRITY REQUIREMENTS", "source_integrity_requirements"),
        ("SOURCE INTEGRITY GUARD MATRIX", "source_integrity_guard_matrix"),
        ("SOURCE INTEGRITY DECISION", "source_integrity_decision"),
        ("SOURCE PRE-START EVIDENCE CHAIN", "source_pre_start_evidence_chain"),
        ("SOURCE PRE-START CONTROLS", "source_pre_start_controls"),
        ("SOURCE PRE-START RULES", "source_pre_start_rules"),
        ("SOURCE PRE-START REQUIREMENTS", "source_pre_start_requirements"),
        ("SOURCE PRE-START GUARD MATRIX", "source_pre_start_guard_matrix"),
        ("SOURCE PRE-START DECISION", "source_pre_start_decision"),
        ("SOURCE CHECKS", "source_checks"),
        ("START DRY-RUN DESIGN OUTPUT", "start_dry_run_design_output"),
        ("START DRY-RUN DESIGN VALIDATION", "start_dry_run_design_validation"),
        ("START DRY-RUN DESIGN CONTROLS", "start_dry_run_design_controls"),
        ("START DRY-RUN DESIGN RULES", "start_dry_run_design_rules"),
        ("START DRY-RUN DESIGN REQUIREMENTS", "start_dry_run_design_requirements"),
        ("START DRY-RUN DESIGN GUARD MATRIX", "start_dry_run_design_guard_matrix"),
        ("START DRY-RUN DESIGN DECISION", "start_dry_run_design_decision"),
        ("VALIDATION CHECKS", "checks"),
    ]

    for title, key in sections:
        print_section(title)
        print_df(result[key])

    print()
    print("ARCHIVOS GENERADOS")
    print("=" * 100)
    print("- reports/p10_21_start_dry_run_design_v1/start_dry_run_design_summary_v1.csv")
    print("- reports/p10_21_start_dry_run_design_v1/controlled_start_dry_run_design_output_v1.csv")
    print("- reports/p10_21_start_dry_run_design_v1/start_dry_run_design_validations_v1.csv")
    print("- reports/p10_21_start_dry_run_design_v1/start_dry_run_design_controls_v1.csv")
    print("- reports/p10_21_start_dry_run_design_v1/start_dry_run_design_rules_v1.csv")
    print("- reports/p10_21_start_dry_run_design_v1/start_dry_run_design_requirements_v1.csv")
    print("- reports/p10_21_start_dry_run_design_v1/start_dry_run_design_guard_matrix_v1.csv")
    print("- reports/p10_21_start_dry_run_design_v1/start_dry_run_design_decision_v1.csv")
    print("- reports/p10_21_start_dry_run_design_v1/start_dry_run_design_checks_v1.csv")
    print()
    print(
        "Restriccion: Phase 10.21 disena solamente el dry-run de inicio; "
        "no ejecuta dry-run, no inicia forward observation ni habilita "
        "evidencia oficial o ejecucion."
    )


if __name__ == "__main__":
    main()