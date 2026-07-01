from __future__ import annotations

import pandas as pd

from src.long_side.long_forward_observation_dataset_bootstrap_v1 import (
    validate_long_forward_observation_dataset_bootstrap,
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
    print("PHASE 9.5 LONG FORWARD OBSERVATION DATASET BOOTSTRAP")
    print("=" * 100)
    print("Purpose: create empty LONG forward observation dataset structure with persistence guard")
    print("Restriction: dataset bootstrap only. No real evidence persistence. No execution.")
    print()

    result = validate_long_forward_observation_dataset_bootstrap()

    print_section("PHASE 9.5 VALIDATION SUMMARY")
    print_df(result["summary"])

    print_section("PHASE 9.4 SOURCE SUMMARY")
    print_df(result["source_phase_9_4_summary"])

    print_section("SOURCE CONTROLLED RUN SUMMARY")
    print_df(result["source_controlled_run_summary"])

    print_section("SOURCE CONTROLLED RUN LEDGER")
    print_df(result["source_controlled_run_ledger"])

    print_section("SOURCE ACCEPTED INPUTS")
    print_df(result["source_accepted_inputs"])

    print_section("SOURCE REJECTED INPUTS")
    print_df(result["source_rejected_inputs"])

    print_section("LONG FORWARD OBSERVATION DATASET SCHEMA")
    print_df(result["dataset_schema"])

    print_section("EMPTY LONG FORWARD OBSERVATION DATASET TEMPLATE")
    print_df(result["empty_dataset_template"])

    print_section("PERSISTENCE GUARD")
    print_df(result["persistence_guard"])

    print_section("BOOTSTRAP LEDGER")
    print_df(result["bootstrap_ledger"])

    print_section("DATASET BOOTSTRAP SUMMARY")
    print_df(result["dataset_bootstrap_summary"])

    print_section("VALIDATION CHECKS")
    print_df(result["checks"])

    print()
    print("ARCHIVOS GENERADOS")
    print("=" * 100)
    print("- reports/phase_9_5_long_forward_observation_dataset_bootstrap_v1/long_forward_observation_dataset_bootstrap_summary_v1.csv")
    print("- reports/phase_9_5_long_forward_observation_dataset_bootstrap_v1/phase_9_4_source_summary_v1.csv")
    print("- reports/phase_9_5_long_forward_observation_dataset_bootstrap_v1/phase_9_4_source_controlled_run_summary_v1.csv")
    print("- reports/phase_9_5_long_forward_observation_dataset_bootstrap_v1/phase_9_4_source_controlled_run_ledger_v1.csv")
    print("- reports/phase_9_5_long_forward_observation_dataset_bootstrap_v1/phase_9_4_source_accepted_inputs_v1.csv")
    print("- reports/phase_9_5_long_forward_observation_dataset_bootstrap_v1/phase_9_4_source_rejected_inputs_v1.csv")
    print("- reports/phase_9_5_long_forward_observation_dataset_bootstrap_v1/long_forward_observation_dataset_schema_v1.csv")
    print("- reports/phase_9_5_long_forward_observation_dataset_bootstrap_v1/long_forward_observation_dataset_template_v1.csv")
    print("- reports/phase_9_5_long_forward_observation_dataset_bootstrap_v1/long_forward_observation_dataset_persistence_guard_v1.csv")
    print("- reports/phase_9_5_long_forward_observation_dataset_bootstrap_v1/long_forward_observation_dataset_bootstrap_ledger_v1.csv")
    print("- reports/phase_9_5_long_forward_observation_dataset_bootstrap_v1/long_forward_observation_dataset_bootstrap_summary_table_v1.csv")
    print("- reports/phase_9_5_long_forward_observation_dataset_bootstrap_v1/long_forward_observation_dataset_bootstrap_checks_v1.csv")
    print()
    print("Restriccion: Phase 9.5 crea estructura dataset LONG forward, pero no persiste evidencia real ni aprueba ejecucion.")


if __name__ == "__main__":
    main()