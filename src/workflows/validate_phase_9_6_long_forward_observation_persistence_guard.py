from __future__ import annotations

import pandas as pd

from src.long_side.long_forward_observation_persistence_guard_v1 import (
    validate_long_forward_observation_persistence_guard,
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
    print("PHASE 9.6 LONG FORWARD OBSERVATION PERSISTENCE GUARD")
    print("=" * 100)
    print("Purpose: validate controlled persistence attempts are blocked")
    print("Restriction: persistence guard only. No real evidence persistence. No execution.")
    print()

    result = validate_long_forward_observation_persistence_guard()

    print_section("PHASE 9.6 VALIDATION SUMMARY")
    print_df(result["summary"])

    print_section("PHASE 9.5 SOURCE SUMMARY")
    print_df(result["source_phase_9_5_summary"])

    print_section("SOURCE PERSISTENCE GUARD")
    print_df(result["source_persistence_guard"])

    print_section("SOURCE DATASET SCHEMA")
    print_df(result["source_dataset_schema"])

    print_section("SOURCE EMPTY DATASET TEMPLATE")
    print_df(result["source_empty_dataset_template"])

    print_section("SOURCE BOOTSTRAP LEDGER")
    print_df(result["source_bootstrap_ledger"])

    print_section("CONTROLLED PERSISTENCE ATTEMPTS")
    print_df(result["persistence_attempts"])

    print_section("PERSISTENCE ATTEMPT EVALUATION")
    print_df(result["evaluated_attempts"])

    print_section("PERSISTENCE GUARD AUDIT")
    print_df(result["guard_audit"])

    print_section("PERSISTENCE GUARD SUMMARY")
    print_df(result["persistence_guard_summary"])

    print_section("VALIDATION CHECKS")
    print_df(result["checks"])

    print()
    print("ARCHIVOS GENERADOS")
    print("=" * 100)
    print("- reports/phase_9_6_long_forward_observation_persistence_guard_v1/long_forward_observation_persistence_guard_summary_v1.csv")
    print("- reports/phase_9_6_long_forward_observation_persistence_guard_v1/phase_9_5_source_summary_v1.csv")
    print("- reports/phase_9_6_long_forward_observation_persistence_guard_v1/phase_9_5_source_persistence_guard_v1.csv")
    print("- reports/phase_9_6_long_forward_observation_persistence_guard_v1/phase_9_5_source_dataset_schema_v1.csv")
    print("- reports/phase_9_6_long_forward_observation_persistence_guard_v1/phase_9_5_source_empty_dataset_template_v1.csv")
    print("- reports/phase_9_6_long_forward_observation_persistence_guard_v1/phase_9_5_source_bootstrap_ledger_v1.csv")
    print("- reports/phase_9_6_long_forward_observation_persistence_guard_v1/long_forward_observation_persistence_attempts_v1.csv")
    print("- reports/phase_9_6_long_forward_observation_persistence_guard_v1/long_forward_observation_persistence_attempt_evaluation_v1.csv")
    print("- reports/phase_9_6_long_forward_observation_persistence_guard_v1/long_forward_observation_persistence_guard_audit_v1.csv")
    print("- reports/phase_9_6_long_forward_observation_persistence_guard_v1/long_forward_observation_persistence_guard_summary_table_v1.csv")
    print("- reports/phase_9_6_long_forward_observation_persistence_guard_v1/long_forward_observation_persistence_guard_checks_v1.csv")
    print()
    print("Restriccion: Phase 9.6 prueba intentos controlados de escritura, pero no persiste evidencia real ni aprueba ejecucion.")


if __name__ == "__main__":
    main()