from __future__ import annotations

import pandas as pd

from src.long_side.long_forward_observation_phase_10_34_evidence_collection_report_only_dry_run_run_v1 import (
    run_long_forward_observation_evidence_collection_report_only_dry_run,
)


def print_section(title: str) -> None:
    print()
    print(title)
    print("=" * 100)


def print_df(df: pd.DataFrame) -> None:
    if df.empty:
        print("Sin registros.")
    else:
        print(df.to_string(index=False))


def main() -> None:
    print(
        "PHASE 10.34 LONG FORWARD OBSERVATION EVIDENCE COLLECTION "
        "REPORT-ONLY DRY-RUN RUN"
    )
    print("=" * 100)
    print(
        "Purpose: execute six deterministic synthetic report-only "
        "dry-run scenarios."
    )
    print(
        "Restriction: synthetic report-only execution. No real evidence "
        "collection, no official dataset implementation or write, no "
        "signals, no alerts, no paper trading, no real capital and no "
        "market execution."
    )

    result = (
        run_long_forward_observation_evidence_collection_report_only_dry_run()
    )

    sections = [
        ("PHASE 10.34 VALIDATION SUMMARY", "summary"),
        ("PHASE 10.33 SOURCE SUMMARY", "source_summary"),
        (
            "PHASE 10.33 SOURCE FUTURE EXECUTION CONTRACT",
            "source_execution_contract",
        ),
        (
            "PHASE 10.33 SOURCE EXECUTION PRECONDITIONS",
            "source_preconditions",
        ),
        (
            "PHASE 10.33 SOURCE ABORT RULES",
            "source_abort_rules",
        ),
        (
            "PHASE 10.33 SOURCE OUTPUT PLAN",
            "source_output_plan",
        ),
        ("PHASE 10.33 SOURCE MANIFEST", "source_manifest"),
        ("SOURCE VALIDATIONS", "source_validations"),
        ("PRE-RUN ABORT EVALUATIONS", "abort_evaluations"),
        ("SYNTHETIC INPUT ROWS", "synthetic_input_rows"),
        ("SCENARIO RESULTS", "scenario_results"),
        ("VALIDATION RESULTS", "validation_results"),
        ("REJECTION RESULTS", "rejection_results"),
        ("HASH AND DEDUPLICATION RESULTS", "hash_and_dedup_results"),
        ("SAFETY LOCK RESULTS", "safety_lock_results"),
        (
            "OFFICIAL DATASET GUARD RESULTS",
            "official_dataset_guard_results",
        ),
        ("DRY-RUN DECISION", "decision"),
        ("VALIDATION CHECKS", "checks"),
        ("RUN MANIFEST", "manifest"),
    ]

    for title, key in sections:
        print_section(title)
        print_df(result[key])

    print()
    print("ARCHIVOS GENERADOS")
    print("=" * 100)
    generated_files = [
        "report_only_dry_run_run_summary_v1.csv",
        "report_only_dry_run_synthetic_input_rows_v1.csv",
        "report_only_dry_run_scenario_results_v1.csv",
        "report_only_dry_run_validation_results_v1.csv",
        "report_only_dry_run_rejection_results_v1.csv",
        "report_only_dry_run_hash_and_dedup_results_v1.csv",
        "report_only_dry_run_safety_lock_results_v1.csv",
        "report_only_dry_run_official_dataset_guard_results_v1.csv",
        "report_only_dry_run_run_checks_v1.csv",
        "report_only_dry_run_run_manifest_v1.csv",
    ]
    for filename in generated_files:
        print(
            "- reports/p10_34_evidence_collection_report_only_"
            f"dry_run_run_v1/{filename}"
        )

    print()
    print(
        "Restriccion: Phase 10.34 ejecuta solo seis escenarios "
        "sinteticos report-only. No recolecta evidencia real, no "
        "implementa ni escribe el dataset oficial y no habilita "
        "senales, alertas, paper trading, capital real, ejecucion o "
        "automatizacion."
    )


if __name__ == "__main__":
    main()
