from __future__ import annotations

import pandas as pd

from src.market_input.full_local_bridge_evidence_cycle_v1 import (
    validate_full_local_bridge_evidence_cycle,
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
    print("PHASE 7.8 FULL LOCAL BRIDGE EVIDENCE CYCLE VALIDATOR")
    print("=" * 100)
    print("Purpose: validate full local bridge package through evidence cycle")
    print("Restriction: evidence persistence only. No execution.")
    print()

    result = validate_full_local_bridge_evidence_cycle()

    print_section("PHASE 7.8 VALIDATION SUMMARY")
    print_df(result["summary"])

    print_section("BRIDGE SUMMARY")
    print_df(result["bridge_summary"])

    print_section("OPERATIONAL INTEGRATION SUMMARY")
    print_df(result["integration_summary"])

    print_section("GENERATED OBSERVATIONS")
    print_df(result["generated_observations"])

    print_section("REJECTED OBSERVATIONS")
    print_df(result["rejected_observations"])

    print_section("PERSISTENCE SUMMARY")
    print_df(result["persistence_summary"])

    print_section("DATASET PREVIEW")
    print_df(result["dataset_preview"], max_rows=20)

    print_section("VALIDATION CHECKS")
    print_df(result["checks"])

    print_section("COMMAND OUTPUT PREVIEW")
    print_df(result["command_output"], max_rows=60)

    print()
    print("ARCHIVOS GENERADOS")
    print("=" * 100)
    print("- reports/phase_7_8_full_local_bridge_evidence_cycle_v1/full_local_bridge_evidence_cycle_summary_v1.csv")
    print("- reports/phase_7_8_full_local_bridge_evidence_cycle_v1/full_local_bridge_evidence_cycle_checks_v1.csv")
    print("- reports/phase_7_8_full_local_bridge_evidence_cycle_v1/full_local_bridge_evidence_cycle_bridge_summary_v1.csv")
    print("- reports/phase_7_8_full_local_bridge_evidence_cycle_v1/full_local_bridge_evidence_cycle_command_output_v1.csv")
    print("- reports/phase_7_8_full_local_bridge_evidence_cycle_v1/full_local_bridge_evidence_cycle_integration_summary_v1.csv")
    print("- reports/phase_7_8_full_local_bridge_evidence_cycle_v1/full_local_bridge_evidence_cycle_generated_observations_v1.csv")
    print("- reports/phase_7_8_full_local_bridge_evidence_cycle_v1/full_local_bridge_evidence_cycle_persistence_summary_v1.csv")
    print()
    print("Restriccion: este validador genera evidencia controlada, pero no ejecuta operaciones.")


if __name__ == "__main__":
    main()