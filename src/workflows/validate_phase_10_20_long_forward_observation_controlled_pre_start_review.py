from __future__ import annotations

import pandas as pd

from src.long_side.long_forward_observation_phase_10_20_controlled_pre_start_review_v1 import (
    validate_long_forward_observation_controlled_pre_start_review,
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
    print("PHASE 10.20 LONG FORWARD OBSERVATION CONTROLLED PRE-START REVIEW")
    print("=" * 100)
    print(
        "Purpose: review readiness for a future controlled forward observation "
        "start dry-run design."
    )
    print(
        "Restriction: no dry-run design, no start dry-run, no forward observation "
        "start, no official evidence, no signals, no alerts, no paper trading, "
        "no market execution."
    )

    result = validate_long_forward_observation_controlled_pre_start_review()

    sections = [
        ("PHASE 10.20 VALIDATION SUMMARY", "summary"),
        ("PHASE 10.19 SOURCE SUMMARY", "source_phase_10_19_summary"),
        ("SOURCE ACTIVATION OUTPUT", "source_activation_output"),
        ("SOURCE INTEGRITY VALIDATION", "source_integrity_validation"),
        ("SOURCE INTEGRITY CONTROLS", "source_integrity_controls"),
        ("SOURCE INTEGRITY RULES", "source_integrity_rules"),
        ("SOURCE INTEGRITY REQUIREMENTS", "source_integrity_requirements"),
        ("SOURCE INTEGRITY GUARD MATRIX", "source_integrity_guard_matrix"),
        ("SOURCE INTEGRITY DECISION", "source_integrity_decision"),
        ("SOURCE CHECKS", "source_checks"),
        ("PRE-START EVIDENCE CHAIN", "pre_start_evidence_chain"),
        ("PRE-START CONTROLS", "pre_start_controls"),
        ("PRE-START RULES", "pre_start_rules"),
        ("PRE-START REQUIREMENTS", "pre_start_requirements"),
        ("PRE-START GUARD MATRIX", "pre_start_guard_matrix"),
        ("PRE-START DECISION", "pre_start_decision"),
        ("VALIDATION CHECKS", "checks"),
    ]

    for title, key in sections:
        print_section(title)
        print_df(result[key])

    print()
    print("ARCHIVOS GENERADOS")
    print("=" * 100)
    print("- reports/p10_20_pre_start_review_v1/pre_start_summary_v1.csv")
    print("- reports/p10_20_pre_start_review_v1/phase_10_19_source_summary_v1.csv")
    print("- reports/p10_20_pre_start_review_v1/phase_10_19_source_activation_output_v1.csv")
    print("- reports/p10_20_pre_start_review_v1/phase_10_19_source_integrity_validations_v1.csv")
    print("- reports/p10_20_pre_start_review_v1/phase_10_19_source_integrity_controls_v1.csv")
    print("- reports/p10_20_pre_start_review_v1/phase_10_19_source_integrity_rules_v1.csv")
    print("- reports/p10_20_pre_start_review_v1/phase_10_19_source_integrity_requirements_v1.csv")
    print("- reports/p10_20_pre_start_review_v1/phase_10_19_source_integrity_guard_matrix_v1.csv")
    print("- reports/p10_20_pre_start_review_v1/phase_10_19_source_integrity_decision_v1.csv")
    print("- reports/p10_20_pre_start_review_v1/phase_10_19_source_checks_v1.csv")
    print("- reports/p10_20_pre_start_review_v1/pre_start_evidence_chain_v1.csv")
    print("- reports/p10_20_pre_start_review_v1/pre_start_controls_v1.csv")
    print("- reports/p10_20_pre_start_review_v1/pre_start_rules_v1.csv")
    print("- reports/p10_20_pre_start_review_v1/pre_start_requirements_v1.csv")
    print("- reports/p10_20_pre_start_review_v1/pre_start_guard_matrix_v1.csv")
    print("- reports/p10_20_pre_start_review_v1/pre_start_decision_v1.csv")
    print("- reports/p10_20_pre_start_review_v1/pre_start_checks_v1.csv")
    print()
    print(
        "Restriccion: Phase 10.20 permite solo un futuro diseno de dry-run "
        "de inicio; no realiza dry-run, no inicia forward observation ni "
        "habilita evidencia oficial o ejecucion."
    )


if __name__ == "__main__":
    main()