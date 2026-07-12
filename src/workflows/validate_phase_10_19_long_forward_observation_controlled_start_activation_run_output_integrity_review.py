from __future__ import annotations

import pandas as pd

from src.long_side.long_forward_observation_phase_10_19_controlled_start_activation_run_output_integrity_review_v1 import (
    validate_long_forward_observation_controlled_start_activation_run_output_integrity_review,
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
        "PHASE 10.19 LONG FORWARD OBSERVATION CONTROLLED START "
        "ACTIVATION RUN OUTPUT INTEGRITY REVIEW"
    )
    print("=" * 100)
    print("Purpose: review integrity of the Phase 10.18 control-plane activation output.")
    print(
        "Restriction: no new activation, no forward observation start, no "
        "official evidence, no signals, no alerts, no paper trading, no market execution."
    )

    result = (
        validate_long_forward_observation_controlled_start_activation_run_output_integrity_review()
    )

    sections = [
        ("PHASE 10.19 VALIDATION SUMMARY", "summary"),
        ("PHASE 10.18 SOURCE SUMMARY", "source_phase_10_18_summary"),
        ("SOURCE ACTIVATION OUTPUT", "source_activation_output"),
        ("SOURCE ACTIVATION VALIDATIONS", "source_activation_validations"),
        ("SOURCE ACTIVATION CONTROLS", "source_activation_controls"),
        ("SOURCE ACTIVATION RULES", "source_activation_rules"),
        ("SOURCE ACTIVATION REQUIREMENTS", "source_activation_requirements"),
        ("SOURCE ACTIVATION GUARD MATRIX", "source_activation_guard_matrix"),
        ("SOURCE ACTIVATION DECISION", "source_activation_decision"),
        ("SOURCE CHECKS", "source_checks"),
        ("ACTIVATION OUTPUT INTEGRITY VALIDATION", "activation_output_integrity_validation"),
        ("ACTIVATION OUTPUT INTEGRITY CONTROLS", "activation_output_integrity_controls"),
        ("ACTIVATION OUTPUT INTEGRITY RULES", "activation_output_integrity_rules"),
        ("ACTIVATION OUTPUT INTEGRITY REQUIREMENTS", "activation_output_integrity_requirements"),
        ("ACTIVATION OUTPUT INTEGRITY GUARD MATRIX", "activation_output_integrity_guard_matrix"),
        ("ACTIVATION OUTPUT INTEGRITY DECISION", "activation_output_integrity_decision"),
        ("VALIDATION CHECKS", "checks"),
    ]

    for title, key in sections:
        print_section(title)
        print_df(result[key])

    print()
    print("ARCHIVOS GENERADOS")
    print("=" * 100)
    print("- reports/p10_19_activation_output_integrity_v1/activation_output_integrity_summary_v1.csv")
    print("- reports/p10_19_activation_output_integrity_v1/phase_10_18_source_summary_v1.csv")
    print("- reports/p10_19_activation_output_integrity_v1/phase_10_18_source_activation_output_v1.csv")
    print("- reports/p10_19_activation_output_integrity_v1/phase_10_18_source_activation_validations_v1.csv")
    print("- reports/p10_19_activation_output_integrity_v1/phase_10_18_source_activation_controls_v1.csv")
    print("- reports/p10_19_activation_output_integrity_v1/phase_10_18_source_activation_rules_v1.csv")
    print("- reports/p10_19_activation_output_integrity_v1/phase_10_18_source_activation_requirements_v1.csv")
    print("- reports/p10_19_activation_output_integrity_v1/phase_10_18_source_activation_guard_matrix_v1.csv")
    print("- reports/p10_19_activation_output_integrity_v1/phase_10_18_source_activation_decision_v1.csv")
    print("- reports/p10_19_activation_output_integrity_v1/phase_10_18_source_checks_v1.csv")
    print("- reports/p10_19_activation_output_integrity_v1/activation_output_integrity_validations_v1.csv")
    print("- reports/p10_19_activation_output_integrity_v1/activation_output_integrity_controls_v1.csv")
    print("- reports/p10_19_activation_output_integrity_v1/activation_output_integrity_rules_v1.csv")
    print("- reports/p10_19_activation_output_integrity_v1/activation_output_integrity_requirements_v1.csv")
    print("- reports/p10_19_activation_output_integrity_v1/activation_output_integrity_guard_matrix_v1.csv")
    print("- reports/p10_19_activation_output_integrity_v1/activation_output_integrity_decision_v1.csv")
    print("- reports/p10_19_activation_output_integrity_v1/activation_output_integrity_checks_v1.csv")
    print()
    print(
        "Restriccion: Phase 10.19 revisa solo integridad del output de "
        "activacion; no inicia forward observation ni habilita evidencia "
        "oficial o ejecucion."
    )


if __name__ == "__main__":
    main()