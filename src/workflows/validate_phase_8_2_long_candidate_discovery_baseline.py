from __future__ import annotations

import pandas as pd

from src.long_side.long_candidate_discovery_baseline_v1 import (
    validate_long_candidate_discovery_baseline,
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
    print("PHASE 8.2 LONG CANDIDATE DISCOVERY BASELINE VALIDATOR")
    print("=" * 100)
    print("Purpose: define baseline LONG research candidates")
    print("Restriction: discovery only. No LONG approval. No execution.")
    print()

    result = validate_long_candidate_discovery_baseline()

    print_section("PHASE 8.2 VALIDATION SUMMARY")
    print_df(result["summary"])

    print_section("LONG BASELINE CANDIDATE REGISTRY")
    print_df(result["candidates"])

    print_section("CONTROLLED LONG PRICE LEVELS")
    print_df(result["controlled_price_levels"])

    print_section("VALIDATION CHECKS")
    print_df(result["checks"])

    print()
    print("ARCHIVOS GENERADOS")
    print("=" * 100)
    print("- reports/phase_8_2_long_candidate_discovery_baseline_v1/long_candidate_discovery_summary_v1.csv")
    print("- reports/phase_8_2_long_candidate_discovery_baseline_v1/long_candidate_discovery_registry_v1.csv")
    print("- reports/phase_8_2_long_candidate_discovery_baseline_v1/long_candidate_controlled_price_levels_v1.csv")
    print("- reports/phase_8_2_long_candidate_discovery_baseline_v1/long_candidate_discovery_checks_v1.csv")
    print()
    print("Restriccion: Phase 8.2 descubre candidatos LONG, pero no aprueba LONG ni ejecucion.")


if __name__ == "__main__":
    main()
