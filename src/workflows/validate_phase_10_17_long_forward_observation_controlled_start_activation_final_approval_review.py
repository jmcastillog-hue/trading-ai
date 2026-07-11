from __future__ import annotations

import pandas as pd

from src.long_side.long_forward_observation_phase_10_17_controlled_start_activation_final_approval_review_v1 import (
    validate_long_forward_observation_controlled_start_activation_final_approval_review,
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
        "PHASE 10.17 LONG FORWARD OBSERVATION CONTROLLED START "
        "ACTIVATION FINAL APPROVAL REVIEW"
    )
    print("=" * 100)
    print(
        "Purpose: review and approve only a future controlled start "
        "activation run"
    )
    print(
        "Restriction: no activation, no forward observation start, no "
        "official evidence, no alerts, no paper trading, no market execution."
    )

    result = (
        validate_long_forward_observation_controlled_start_activation_final_approval_review()
    )

    sections = [
        ("PHASE 10.17 VALIDATION SUMMARY", "summary"),
        ("PHASE 10.16 SOURCE SUMMARY", "source_phase_10_16_summary"),
        ("SOURCE REPORT-ONLY DRY-RUN OUTPUT", "source_report_only_dry_run_output"),
        ("SOURCE INTEGRITY CONTROLS", "source_integrity_controls"),
        ("SOURCE INTEGRITY VALIDATION", "source_integrity_validation"),
        ("SOURCE INTEGRITY RULES", "source_integrity_rules"),
        ("SOURCE INTEGRITY REQUIREMENTS", "source_integrity_requirements"),
        ("SOURCE INTEGRITY GUARD MATRIX", "source_integrity_guard_matrix"),
        ("SOURCE INTEGRITY DECISION", "source_integrity_decision"),
        ("SOURCE CHECKS", "source_checks"),
        ("FINAL APPROVAL EVIDENCE CHAIN", "final_approval_evidence_chain"),
        ("FINAL APPROVAL CONTROLS", "final_approval_controls"),
        ("FINAL APPROVAL RULES", "final_approval_rules"),
        ("FINAL APPROVAL REQUIREMENTS", "final_approval_requirements"),
        ("FINAL APPROVAL GUARD MATRIX", "final_approval_guard_matrix"),
        ("FINAL APPROVAL DECISION", "final_approval_decision"),
        ("VALIDATION CHECKS", "checks"),
    ]

    for title, key in sections:
        print_section(title)
        print_df(result[key])

    print()
    print("ARCHIVOS GENERADOS")
    print("=" * 100)
    print("- reports/p10_17_final_approval_review_v1/final_approval_summary_v1.csv")
    print("- reports/p10_17_final_approval_review_v1/phase_10_16_source_summary_v1.csv")
    print("- reports/p10_17_final_approval_review_v1/phase_10_15_source_report_only_dry_run_output_v1.csv")
    print("- reports/p10_17_final_approval_review_v1/phase_10_16_source_integrity_controls_v1.csv")
    print("- reports/p10_17_final_approval_review_v1/phase_10_16_source_integrity_validations_v1.csv")
    print("- reports/p10_17_final_approval_review_v1/phase_10_16_source_integrity_rules_v1.csv")
    print("- reports/p10_17_final_approval_review_v1/phase_10_16_source_integrity_requirements_v1.csv")
    print("- reports/p10_17_final_approval_review_v1/phase_10_16_source_integrity_guard_matrix_v1.csv")
    print("- reports/p10_17_final_approval_review_v1/phase_10_16_source_integrity_decision_v1.csv")
    print("- reports/p10_17_final_approval_review_v1/phase_10_16_source_checks_v1.csv")
    print("- reports/p10_17_final_approval_review_v1/final_approval_evidence_chain_v1.csv")
    print("- reports/p10_17_final_approval_review_v1/final_approval_controls_v1.csv")
    print("- reports/p10_17_final_approval_review_v1/final_approval_rules_v1.csv")
    print("- reports/p10_17_final_approval_review_v1/final_approval_requirements_v1.csv")
    print("- reports/p10_17_final_approval_review_v1/final_approval_guard_matrix_v1.csv")
    print("- reports/p10_17_final_approval_review_v1/final_approval_decision_v1.csv")
    print("- reports/p10_17_final_approval_review_v1/final_approval_checks_v1.csv")
    print()
    print(
        "Restriccion: Phase 10.17 aprueba solamente un futuro run de "
        "activacion controlada; no inicia forward observation ni habilita "
        "evidencia oficial o ejecucion de mercado."
    )


if __name__ == "__main__":
    main()