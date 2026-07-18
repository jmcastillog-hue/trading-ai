from __future__ import annotations

import pandas as pd

from src.long_side.long_forward_observation_phase_10_36_evidence_collection_report_only_dry_run_final_approval_review_v1 import (
    run_long_forward_observation_evidence_collection_report_only_dry_run_final_approval_review,
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
        "PHASE 10.36 LONG FORWARD OBSERVATION EVIDENCE COLLECTION "
        "REPORT-ONLY DRY-RUN FINAL APPROVAL REVIEW"
    )
    print("=" * 100)
    print(
        "Purpose: perform the final approval review of the synthetic "
        "report-only dry-run cycle."
    )
    print(
        "Restriction: review-only. No new dry-run execution, no real "
        "evidence collection, no official dataset implementation or "
        "write, no signals, no alerts, no paper trading, no real "
        "capital and no market execution."
    )

    result = (
        run_long_forward_observation_evidence_collection_report_only_dry_run_final_approval_review()
    )

    sections = [
        ("PHASE 10.36 VALIDATION SUMMARY", "summary"),
        ("PHASE 10.35 SOURCE SUMMARY", "source_summary"),
        (
            "PHASE 10.35 SOURCE VALIDATIONS",
            "source_validations",
        ),
        ("PHASE 10.35 SOURCE REVIEW ITEMS", "source_items"),
        ("PHASE 10.35 SOURCE FINDINGS", "source_findings"),
        ("PHASE 10.35 SOURCE CONTROLS", "source_controls"),
        ("PHASE 10.35 SOURCE RULES", "source_rules"),
        (
            "PHASE 10.35 SOURCE REQUIREMENTS",
            "source_requirements",
        ),
        (
            "PHASE 10.35 SOURCE GUARD MATRIX",
            "source_guard_matrix",
        ),
        ("PHASE 10.35 SOURCE DECISION", "source_decision"),
        ("PHASE 10.35 SOURCE CHECKS", "source_checks"),
        ("PHASE 10.35 SOURCE MANIFEST", "source_manifest"),
        (
            "PHASE 10.35 SOURCE ARTIFACT MANIFEST",
            "source_artifact_manifest",
        ),
        ("FINAL APPROVAL VALIDATIONS", "validations"),
        ("FINAL APPROVAL REVIEW ITEMS", "items"),
        ("FINAL APPROVAL FINDINGS", "findings"),
        ("FINAL APPROVAL CONTROLS", "controls"),
        ("FINAL APPROVAL RULES", "rules"),
        ("FINAL APPROVAL REQUIREMENTS", "requirements"),
        ("FINAL APPROVAL GUARD MATRIX", "guard_matrix"),
        ("FINAL APPROVAL DECISION", "decision"),
        ("VALIDATION CHECKS", "checks"),
        ("FINAL APPROVAL MANIFEST", "manifest"),
    ]

    for title, key in sections:
        print_section(title)
        print_df(result[key])

    print()
    print("ARCHIVOS GENERADOS")
    print("=" * 100)
    generated = [
        "report_only_dry_run_final_approval_review_summary_v1.csv",
        "report_only_dry_run_final_approval_review_validations_v1.csv",
        "report_only_dry_run_final_approval_review_items_v1.csv",
        "report_only_dry_run_final_approval_review_findings_v1.csv",
        "report_only_dry_run_final_approval_review_controls_v1.csv",
        "report_only_dry_run_final_approval_review_rules_v1.csv",
        "report_only_dry_run_final_approval_review_requirements_v1.csv",
        "report_only_dry_run_final_approval_review_guard_matrix_v1.csv",
        "report_only_dry_run_final_approval_review_decision_v1.csv",
        "report_only_dry_run_final_approval_review_checks_v1.csv",
        "source_report_only_dry_run_final_approval_artifact_manifest_v1.csv",
    ]
    for filename in generated:
        print(
            "- reports/p10_36_evidence_collection_report_only_dry_run_"
            f"final_approval_review_v1/{filename}"
        )

    print()
    print(
        "Restriccion: Phase 10.36 aprueba solamente el cierre del "
        "ciclo sintetico report-only y, si todos los controles pasan, "
        "permite avanzar a un diseno futuro del esquema del dataset "
        "oficial. No recolecta evidencia real, no implementa ni "
        "escribe el dataset oficial y no habilita senales, alertas, "
        "paper trading, capital real, ejecucion o automatizacion."
    )


if __name__ == "__main__":
    main()
