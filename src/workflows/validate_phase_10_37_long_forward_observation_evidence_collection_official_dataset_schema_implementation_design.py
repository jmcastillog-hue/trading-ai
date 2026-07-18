from __future__ import annotations

import pandas as pd

from src.long_side.long_forward_observation_phase_10_37_evidence_collection_official_dataset_schema_implementation_design_v1 import (
    run_long_forward_observation_evidence_collection_official_dataset_schema_implementation_design,
)


def print_section(title: str) -> None:
    print()
    print(title)
    print("=" * 100)


def print_df(df: pd.DataFrame) -> None:
    print("Sin registros." if df.empty else df.to_string(index=False))


def main() -> None:
    print(
        "PHASE 10.37 LONG FORWARD OBSERVATION EVIDENCE COLLECTION "
        "OFFICIAL DATASET SCHEMA IMPLEMENTATION DESIGN"
    )
    print("=" * 100)
    print(
        "Restriction: design-only. No dataset implementation or creation, "
        "no evidence collection or persistence, no signals, alerts, paper "
        "trading, real capital, execution or automation."
    )

    result = run_long_forward_observation_evidence_collection_official_dataset_schema_implementation_design()
    sections = [
        ("PHASE 10.37 VALIDATION SUMMARY", "summary"),
        ("PHASE 10.36 SOURCE SUMMARY", "source_summary"),
        ("PHASE 10.36 SOURCE DECISION", "source_decision"),
        ("PHASE 10.36 SOURCE ARTIFACT MANIFEST", "source_artifact_manifest"),
        ("SOURCE VALIDATIONS", "source_validations"),
        ("CANONICAL FIELD CATALOG", "field_catalog"),
        ("ENUM DOMAINS", "enum_domains"),
        ("SCHEMA CONSTRAINTS", "constraints"),
        ("KEY AND INDEX DESIGN", "key_index_design"),
        ("PROVENANCE CONTRACT", "provenance_contract"),
        ("LIFECYCLE CONTRACT", "lifecycle_contract"),
        ("MIGRATION PLAN", "migration_plan"),
        ("SAFETY GUARDS", "safety_guards"),
        ("ACCEPTANCE CRITERIA", "acceptance_criteria"),
        ("DESIGN DECISION", "decision"),
        ("VALIDATION CHECKS", "checks"),
        ("DESIGN MANIFEST", "manifest"),
    ]
    for title, key in sections:
        print_section(title)
        print_df(result[key])

    print()
    print("ARCHIVOS GENERADOS")
    print("=" * 100)
    for filename in [
        "official_dataset_schema_implementation_design_summary_v1.csv",
        "official_dataset_schema_implementation_design_source_validations_v1.csv",
        "official_dataset_schema_field_catalog_v1.csv",
        "official_dataset_schema_enum_domains_v1.csv",
        "official_dataset_schema_constraints_v1.csv",
        "official_dataset_schema_key_index_design_v1.csv",
        "official_dataset_schema_provenance_contract_v1.csv",
        "official_dataset_schema_lifecycle_contract_v1.csv",
        "official_dataset_schema_migration_plan_v1.csv",
        "official_dataset_schema_safety_guards_v1.csv",
        "official_dataset_schema_acceptance_criteria_v1.csv",
        "official_dataset_schema_implementation_design_decision_v1.csv",
        "official_dataset_schema_implementation_design_checks_v1.csv",
        "source_official_dataset_schema_implementation_design_artifact_manifest_v1.csv",
    ]:
        print(
            "- reports/p10_37_evidence_collection_official_dataset_"
            f"schema_implementation_design_v1/{filename}"
        )


if __name__ == "__main__":
    main()
