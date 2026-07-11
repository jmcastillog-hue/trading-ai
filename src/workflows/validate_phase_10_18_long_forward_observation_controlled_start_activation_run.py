from __future__ import annotations

import pandas as pd

from src.long_side.long_forward_observation_phase_10_18_controlled_start_activation_run_v1 import (
    validate_long_forward_observation_controlled_start_activation_run,
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
        "PHASE 10.18 LONG FORWARD OBSERVATION "
        "CONTROLLED START ACTIVATION RUN"
    )
    print("=" * 100)
    print(
        "Purpose: perform the approved control-plane activation procedure."
    )
    print(
        "Restriction: no forward observation start, no official evidence, "
        "no signals, no alerts, no paper trading, no market execution."
    )

    result = (
        validate_long_forward_observation_controlled_start_activation_run()
    )

    sections = [
        ("PHASE 10.18 VALIDATION SUMMARY", "summary"),
        ("PHASE 10.17 SOURCE SUMMARY", "source_phase_10_17_summary"),
        (
            "SOURCE FINAL APPROVAL DECISION",
            "source_final_approval_decision",
        ),
        (
            "SOURCE FINAL APPROVAL EVIDENCE",
            "source_final_approval_evidence",
        ),
        (
            "SOURCE FINAL APPROVAL CONTROLS",
            "source_final_approval_controls",
        ),
        (
            "SOURCE FINAL APPROVAL RULES",
            "source_final_approval_rules",
        ),
        (
            "SOURCE FINAL APPROVAL REQUIREMENTS",
            "source_final_approval_requirements",
        ),
        (
            "SOURCE FINAL APPROVAL GUARD MATRIX",
            "source_final_approval_guard_matrix",
        ),
        ("SOURCE CHECKS", "source_checks"),
        ("CONTROLLED START ACTIVATION OUTPUT", "activation_output"),
        ("ACTIVATION OUTPUT VALIDATION", "activation_validation"),
        ("ACTIVATION RUN CONTROLS", "activation_controls"),
        ("ACTIVATION RUN RULES", "activation_rules"),
        ("ACTIVATION RUN REQUIREMENTS", "activation_requirements"),
        ("ACTIVATION RUN GUARD MATRIX", "activation_guard_matrix"),
        ("ACTIVATION RUN DECISION", "activation_decision"),
        ("VALIDATION CHECKS", "checks"),
    ]

    for title, key in sections:
        print_section(title)
        print_df(result[key])

    print()
    print("ARCHIVOS GENERADOS")
    print("=" * 100)
    print(
        "- reports/p10_18_activation_run_v1/"
        "activation_run_summary_v1.csv"
    )
    print(
        "- reports/p10_18_activation_run_v1/"
        "controlled_start_activation_run_output_v1.csv"
    )
    print(
        "- reports/p10_18_activation_run_v1/"
        "activation_run_validations_v1.csv"
    )
    print(
        "- reports/p10_18_activation_run_v1/"
        "activation_run_controls_v1.csv"
    )
    print(
        "- reports/p10_18_activation_run_v1/"
        "activation_run_rules_v1.csv"
    )
    print(
        "- reports/p10_18_activation_run_v1/"
        "activation_run_requirements_v1.csv"
    )
    print(
        "- reports/p10_18_activation_run_v1/"
        "activation_run_guard_matrix_v1.csv"
    )
    print(
        "- reports/p10_18_activation_run_v1/"
        "activation_run_decision_v1.csv"
    )
    print(
        "- reports/p10_18_activation_run_v1/"
        "activation_run_checks_v1.csv"
    )
    print()
    print(
        "Restriccion: Phase 10.18 registra solo la activacion del "
        "plano de control; no inicia forward observation ni habilita "
        "evidencia oficial o ejecucion."
    )


if __name__ == "__main__":
    main()