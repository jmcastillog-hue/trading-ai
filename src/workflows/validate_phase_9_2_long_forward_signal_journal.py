from __future__ import annotations

import pandas as pd

from src.long_side.long_forward_signal_journal_v1 import (
    validate_long_forward_signal_journal,
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
    print("PHASE 9.2 LONG FORWARD SIGNAL JOURNAL VALIDATOR")
    print("=" * 100)
    print("Purpose: define LONG forward signal journal template without recording real signals")
    print("Restriction: journal template only. No forward observation. No LONG approval. No execution.")
    print()

    result = validate_long_forward_signal_journal()

    print_section("PHASE 9.2 VALIDATION SUMMARY")
    print_df(result["summary"])

    print_section("PHASE 9.1 SOURCE SUMMARY")
    print_df(result["source_phase_9_1_summary"])

    print_section("PHASE 9.1 SOURCE CANDIDATE REGISTRY")
    print_df(result["source_candidate_registry"])

    print_section("PHASE 9.1 SOURCE OBSERVATION SCHEMA")
    print_df(result["source_observation_schema"])

    print_section("LONG FORWARD SIGNAL JOURNAL SCHEMA")
    print_df(result["journal_schema"])

    print_section("EMPTY LONG FORWARD SIGNAL JOURNAL TEMPLATE")
    print_df(result["empty_journal_template"])

    print_section("CONTROLLED TEMPLATE ROW")
    print_df(result["controlled_template_row"])

    print_section("JOURNAL RULES")
    print_df(result["journal_rules"])

    print_section("TEMPLATE ROW CHECKS")
    print_df(result["template_row_checks"])

    print_section("VALIDATION CHECKS")
    print_df(result["checks"])

    print()
    print("ARCHIVOS GENERADOS")
    print("=" * 100)
    print("- reports/phase_9_2_long_forward_signal_journal_v1/long_forward_signal_journal_summary_v1.csv")
    print("- reports/phase_9_2_long_forward_signal_journal_v1/phase_9_1_source_summary_v1.csv")
    print("- reports/phase_9_2_long_forward_signal_journal_v1/phase_9_1_source_candidate_registry_v1.csv")
    print("- reports/phase_9_2_long_forward_signal_journal_v1/phase_9_1_source_observation_schema_v1.csv")
    print("- reports/phase_9_2_long_forward_signal_journal_v1/long_forward_signal_journal_schema_v1.csv")
    print("- reports/phase_9_2_long_forward_signal_journal_v1/long_forward_signal_journal_template_v1.csv")
    print("- reports/phase_9_2_long_forward_signal_journal_v1/long_forward_signal_journal_controlled_template_row_v1.csv")
    print("- reports/phase_9_2_long_forward_signal_journal_v1/long_forward_signal_journal_rules_v1.csv")
    print("- reports/phase_9_2_long_forward_signal_journal_v1/long_forward_signal_journal_template_row_checks_v1.csv")
    print("- reports/phase_9_2_long_forward_signal_journal_v1/long_forward_signal_journal_checks_v1.csv")
    print()
    print("Restriccion: Phase 9.2 define journal LONG forward, pero no registra senales reales ni aprueba ejecucion.")


if __name__ == "__main__":
    main()