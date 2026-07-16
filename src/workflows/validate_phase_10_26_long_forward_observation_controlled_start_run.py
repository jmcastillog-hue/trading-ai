from __future__ import annotations

import pandas as pd

from src.long_side.long_forward_observation_phase_10_26_controlled_start_run_v1 import (
    validate_long_forward_observation_controlled_start_run,
)


def print_section(title: str) -> None:
    print()
    print(title)
    print("=" * 100)


def print_df(
    df: pd.DataFrame,
    max_rows: int | None = None,
) -> None:
    if df.empty:
        print("Sin registros.")
        return

    if max_rows is not None:
        print(df.head(max_rows).to_string(index=False))
        return

    print(df.to_string(index=False))


def main() -> None:
    print(
        "PHASE 10.26 LONG FORWARD OBSERVATION CONTROLLED START RUN"
    )
    print("=" * 100)
    print(
        "Purpose: perform one controlled forward observation start-state run."
    )
    print(
        "Restriction: observation-state start only. No official dataset "
        "write, no real evidence, no live signals, no alerts, no paper "
        "trading, no real capital, and no market execution."
    )

    result = validate_long_forward_observation_controlled_start_run()

    print_section("PHASE 10.26 VALIDATION SUMMARY")
    print_df(result["summary"])

    print_section("PHASE 10.25 SOURCE SUMMARY")
    print_df(result["source_phase_10_25_summary"])

    print_section("SOURCE DRY-RUN OUTPUT")
    print_df(result["source_dry_run_output"])

    print_section("SOURCE FINAL APPROVAL VALIDATIONS")
    print_df(result["source_validations"])

    print_section("SOURCE FINAL APPROVAL EVIDENCE CHAIN")
    print_df(result["source_evidence_chain"])

    print_section("SOURCE FINAL APPROVAL CONTROLS")
    print_df(result["source_controls"])

    print_section("SOURCE FINAL APPROVAL RULES")
    print_df(result["source_rules"])

    print_section("SOURCE FINAL APPROVAL REQUIREMENTS")
    print_df(result["source_requirements"])

    print_section("SOURCE FINAL APPROVAL GUARD MATRIX")
    print_df(result["source_guard_matrix"])

    print_section("SOURCE FINAL APPROVAL DECISION")
    print_df(result["source_decision"])

    print_section("SOURCE PHASE 10.25 CHECKS")
    print_df(result["source_checks"])

    print_section("CONTROLLED FORWARD OBSERVATION START OUTPUT")
    print_df(result["start_output"])

    print_section("CONTROLLED START RUN VALIDATIONS")
    print_df(result["start_validations"])

    print_section("CONTROLLED START RUN EVIDENCE CHAIN")
    print_df(result["start_evidence_chain"])

    print_section("CONTROLLED START RUN CONTROLS")
    print_df(result["start_controls"])

    print_section("CONTROLLED START RUN RULES")
    print_df(result["start_rules"])

    print_section("CONTROLLED START RUN REQUIREMENTS")
    print_df(result["start_requirements"])

    print_section("CONTROLLED START RUN GUARD MATRIX")
    print_df(result["start_guard_matrix"])

    print_section("CONTROLLED START RUN DECISION")
    print_df(result["start_decision"])

    print_section("VALIDATION CHECKS")
    print_df(result["checks"])

    print()
    print("ARCHIVOS GENERADOS")
    print("=" * 100)

    generated_files = [
        "controlled_start_run_summary_v1.csv",
        "phase_10_25_source_summary_v1.csv",
        "phase_10_23_source_dry_run_output_v1.csv",
        "phase_10_25_source_validations_v1.csv",
        "phase_10_25_source_evidence_chain_v1.csv",
        "phase_10_25_source_controls_v1.csv",
        "phase_10_25_source_rules_v1.csv",
        "phase_10_25_source_requirements_v1.csv",
        "phase_10_25_source_guard_matrix_v1.csv",
        "phase_10_25_source_decision_v1.csv",
        "phase_10_25_source_checks_v1.csv",
        "controlled_forward_observation_start_output_v1.csv",
        "controlled_start_run_validations_v1.csv",
        "controlled_start_run_evidence_chain_v1.csv",
        "controlled_start_run_controls_v1.csv",
        "controlled_start_run_rules_v1.csv",
        "controlled_start_run_requirements_v1.csv",
        "controlled_start_run_guard_matrix_v1.csv",
        "controlled_start_run_decision_v1.csv",
        "controlled_start_run_checks_v1.csv",
    ]

    for filename in generated_files:
        print(
            "- reports/p10_26_controlled_start_run_v1/"
            f"{filename}"
        )

    print()
    print(
        "Restriccion: Phase 10.26 inicia solamente el estado controlado "
        "de observacion forward. No crea ni escribe el dataset oficial, "
        "no registra evidencia real, no habilita senales, alertas, paper "
        "trading, capital real, ejecucion de mercado o automatizacion."
    )


if __name__ == "__main__":
    main()
