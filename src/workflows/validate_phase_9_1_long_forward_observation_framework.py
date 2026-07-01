from __future__ import annotations

import pandas as pd

from src.long_side.long_forward_observation_framework_v1 import (
    validate_long_forward_observation_framework,
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
    print("PHASE 9.1 LONG FORWARD OBSERVATION FRAMEWORK VALIDATOR")
    print("=" * 100)
    print("Purpose: define LONG forward observation framework without starting observation")
    print("Restriction: framework only. No signal generation. No LONG approval. No execution.")
    print()

    result = validate_long_forward_observation_framework()

    print_section("PHASE 9.1 VALIDATION SUMMARY")
    print_df(result["summary"])

    print_section("PHASE 8.11 SOURCE SUMMARY")
    print_df(result["source_phase_8_11_summary"])

    print_section("PHASE 8.11 SOURCE READINESS GATE")
    print_df(result["source_readiness_gate"])

    print_section("PHASE 8.11 SOURCE EVIDENCE LEDGER")
    print_df(result["source_evidence_ledger"])

    print_section("LONG FORWARD OBSERVATION CANDIDATE REGISTRY")
    print_df(result["candidate_registry"])

    print_section("LONG FORWARD OBSERVATION SCHEMA")
    print_df(result["observation_schema"])

    print_section("LONG FORWARD OBSERVATION TEMPLATE")
    print_df(result["observation_template"])

    print_section("FRAMEWORK CONTROLS")
    print_df(result["framework_controls"])

    print_section("VALIDATION CHECKS")
    print_df(result["checks"])

    print()
    print("ARCHIVOS GENERADOS")
    print("=" * 100)
    print("- reports/phase_9_1_long_forward_observation_framework_v1/long_forward_observation_framework_summary_v1.csv")
    print("- reports/phase_9_1_long_forward_observation_framework_v1/phase_8_11_source_summary_v1.csv")
    print("- reports/phase_9_1_long_forward_observation_framework_v1/phase_8_11_source_readiness_gate_v1.csv")
    print("- reports/phase_9_1_long_forward_observation_framework_v1/phase_8_11_source_evidence_ledger_v1.csv")
    print("- reports/phase_9_1_long_forward_observation_framework_v1/long_forward_observation_candidate_registry_v1.csv")
    print("- reports/phase_9_1_long_forward_observation_framework_v1/long_forward_observation_schema_v1.csv")
    print("- reports/phase_9_1_long_forward_observation_framework_v1/long_forward_observation_template_v1.csv")
    print("- reports/phase_9_1_long_forward_observation_framework_v1/long_forward_observation_framework_controls_v1.csv")
    print("- reports/phase_9_1_long_forward_observation_framework_v1/long_forward_observation_framework_checks_v1.csv")
    print()
    print("Restriccion: Phase 9.1 define framework LONG forward, pero no inicia observacion, no aprueba LONG ni ejecucion.")


if __name__ == "__main__":
    main()