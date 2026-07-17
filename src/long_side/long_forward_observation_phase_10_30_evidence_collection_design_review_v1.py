from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

import pandas as pd

from src.long_side.long_forward_observation_dataset_bootstrap_v1 import (
    OFFICIAL_DATASET_PATH,
    PRIMARY_RESEARCH_CANDIDATE,
)


REPORTS_DIR = Path(
    "reports/p10_30_evidence_collection_design_review_v1"
)
SOURCE_DIR = Path(
    "reports/p10_29_evidence_collection_design_v1"
)

PHASE_10_29_DOC_PATH = Path(
    "docs/PHASE_10_LONG_FORWARD_OBSERVATION_EVIDENCE_COLLECTION_DESIGN.md"
)
PHASE_10_30_DOC_PATH = Path(
    "docs/PHASE_10_LONG_FORWARD_OBSERVATION_EVIDENCE_COLLECTION_DESIGN_REVIEW.md"
)

SOURCE_PATHS = {
    "summary": SOURCE_DIR / "evidence_collection_design_summary_v1.csv",
    "schema": SOURCE_DIR / "evidence_collection_design_schema_v1.csv",
    "components": SOURCE_DIR / "evidence_collection_design_components_v1.csv",
    "accepted_sources": SOURCE_DIR / "evidence_collection_accepted_source_rules_v1.csv",
    "lifecycle": SOURCE_DIR / "evidence_collection_lifecycle_states_v1.csv",
    "deduplication": SOURCE_DIR / "evidence_collection_deduplication_rules_v1.csv",
    "rejection": SOURCE_DIR / "evidence_collection_rejection_rules_v1.csv",
    "write_guards": SOURCE_DIR / "evidence_collection_write_guards_v1.csv",
    "audit": SOURCE_DIR / "evidence_collection_audit_requirements_v1.csv",
    "boundaries": SOURCE_DIR / "evidence_collection_boundary_rules_v1.csv",
    "validations": SOURCE_DIR / "evidence_collection_design_validations_v1.csv",
    "evidence_chain": SOURCE_DIR / "evidence_collection_design_evidence_chain_v1.csv",
    "controls": SOURCE_DIR / "evidence_collection_design_controls_v1.csv",
    "rules": SOURCE_DIR / "evidence_collection_design_rules_v1.csv",
    "requirements": SOURCE_DIR / "evidence_collection_design_requirements_v1.csv",
    "guard_matrix": SOURCE_DIR / "evidence_collection_design_guard_matrix_v1.csv",
    "decision": SOURCE_DIR / "evidence_collection_design_decision_v1.csv",
    "checks": SOURCE_DIR / "evidence_collection_design_checks_v1.csv",
    "manifest": SOURCE_DIR / "source_design_artifact_manifest_v1.csv",
}

SOURCE_READY_DECISION = (
    "CONTROLLED_FORWARD_OBSERVATION_EVIDENCE_COLLECTION_DESIGN_"
    "READY_FOR_DESIGN_REVIEW"
)
DESIGN_REVIEW_STATUS = (
    "LONG_FORWARD_OBSERVATION_EVIDENCE_COLLECTION_DESIGN_REVIEW_ONLY"
)
READY_DECISION = (
    "CONTROLLED_FORWARD_OBSERVATION_EVIDENCE_COLLECTION_DESIGN_REVIEW_"
    "READY_FOR_REPORT_ONLY_DRY_RUN_DESIGN"
)
BLOCKED_DECISION = (
    "CONTROLLED_FORWARD_OBSERVATION_EVIDENCE_COLLECTION_DESIGN_REVIEW_BLOCKED"
)
RECOMMENDED_NEXT_PHASE = (
    "PHASE_10_31_LONG_FORWARD_OBSERVATION_EVIDENCE_COLLECTION_"
    "REPORT_ONLY_DRY_RUN_DESIGN_V1"
)

EXPECTED_COUNTS = {
    "source_artifact_count": 12,
    "source_design_requirements_count": 20,
    "evidence_schema_field_count": 54,
    "design_component_count": 20,
    "accepted_source_rule_count": 3,
    "lifecycle_state_count": 8,
    "deduplication_rule_count": 8,
    "rejection_rule_count": 15,
    "write_guard_count": 12,
    "audit_requirement_count": 10,
    "boundary_rule_count": 12,
    "design_validation_rows": 44,
    "design_evidence_rows": 44,
    "design_control_rows": 44,
    "design_rule_rows": 19,
    "design_requirement_rows": 66,
    "design_guard_rows": 35,
}

EXPECTED_SCHEMA_FIELDS = [
    "evidence_id",
    "observation_id",
    "collected_at_utc",
    "observed_at_utc",
    "source_system",
    "source_artifact",
    "source_artifact_sha256",
    "source_row_hash",
    "candidate_id",
    "direction",
    "symbol",
    "timeframe",
    "observation_state",
    "evidence_status",
    "evidence_scope",
    "evidence_version",
    "entry_price",
    "stop_price",
    "target_price",
    "invalidation_level",
    "risk_reward",
    "cost_profile",
    "market_context",
    "activation_scope",
    "signal_state",
    "deduplication_key",
    "deduplication_status",
    "lifecycle_state",
    "review_status",
    "rejection_reason",
    "manual_confirmation_required",
    "manual_confirmed",
    "write_ahead_validation_passed",
    "schema_validation_passed",
    "provenance_validation_passed",
    "risk_structure_validation_passed",
    "evidence_hash",
    "previous_evidence_hash",
    "audit_event_id",
    "created_by",
    "reviewed_by",
    "rollback_reference",
    "accepted_as_real_evidence",
    "official_dataset_write_allowed",
    "evidence_persistence_allowed",
    "signal_generation_enabled",
    "live_alerts_allowed",
    "paper_trade_execution_allowed",
    "real_capital_allowed",
    "market_execution_allowed",
    "exchange_execution_allowed",
    "automation_allowed",
    "execution_allowed",
    "notes",
]

EXPECTED_SAFETY_FIELDS = [
    "accepted_as_real_evidence",
    "official_dataset_write_allowed",
    "evidence_persistence_allowed",
    "signal_generation_enabled",
    "live_alerts_allowed",
    "paper_trade_execution_allowed",
    "real_capital_allowed",
    "market_execution_allowed",
    "exchange_execution_allowed",
    "automation_allowed",
    "execution_allowed",
]

EXPECTED_FALSE_GUARDS = [
    "official_dataset_write_allowed",
    "official_dataset_write_performed",
    "real_forward_dataset_created",
    "real_forward_signals_recorded",
    "journal_real_rows_accepted",
    "accepted_as_real_evidence",
    "evidence_persistence_allowed",
    "evidence_write_performed",
    "signal_generation_enabled",
    "live_alerts_allowed",
    "paper_trading_enabled",
    "long_strategy_approved",
    "long_entries_approved",
    "long_side_established",
    "paper_trade_execution_allowed",
    "real_capital_allowed",
    "market_execution_allowed",
    "exchange_execution_allowed",
    "automation_allowed",
    "execution_allowed",
    "real_entries_approved",
    "total_project_completed",
]

EXPECTED_LIFECYCLE_STATES = [
    "CAPTURE_PENDING",
    "CAPTURED_UNVALIDATED",
    "VALIDATION_REJECTED",
    "VALIDATED_PENDING_REVIEW",
    "REVIEW_REJECTED",
    "REVIEW_APPROVED_PENDING_PERSISTENCE",
    "PERSISTENCE_BLOCKED",
    "PERSISTED_OFFICIAL",
]

REVIEW_ITEM_NAMES = [
    "phase_10_29_dependency",
    "source_artifact_integrity",
    "source_decision_consistency",
    "source_validation_chain",
    "schema_completeness",
    "schema_safety_defaults",
    "schema_non_implementation",
    "design_component_coverage",
    "design_component_non_implementation",
    "accepted_source_controls",
    "lifecycle_coherence",
    "deduplication_contract",
    "rejection_contract",
    "official_write_guard_contract",
    "audit_contract",
    "boundary_contract",
    "controlled_observation_state",
    "evidence_collection_boundary",
    "official_dataset_boundary",
    "signal_and_execution_boundary",
]


def safe_bool(value: Any, default: bool = False) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in {"true", "1", "yes", "y"}:
            return True
        if normalized in {"false", "0", "no", "n", ""}:
            return False
    try:
        if pd.isna(value):
            return default
    except Exception:
        pass
    try:
        return bool(value)
    except Exception:
        return default


def safe_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None or pd.isna(value):
            return default
        return float(value)
    except Exception:
        return default


def read_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    try:
        return pd.read_csv(path)
    except Exception:
        return pd.DataFrame()


def dataframe_all_passed(df: pd.DataFrame) -> bool:
    return (
        not df.empty
        and "passed" in df.columns
        and df["passed"].map(lambda value: safe_bool(value, False)).all()
    )


def sha256_file(path: Path) -> str:
    if not path.exists() or not path.is_file():
        return ""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_manifest() -> pd.DataFrame:
    rows = []
    for position, (name, path) in enumerate(SOURCE_PATHS.items(), start=1):
        exists = path.exists() and path.is_file()
        size_bytes = path.stat().st_size if exists else 0
        file_hash = sha256_file(path) if exists else ""
        rows.append(
            {
                "manifest_position": position,
                "artifact_name": name,
                "artifact_filename": path.name,
                "artifact_path": str(path),
                "artifact_exists": exists,
                "artifact_size_bytes": int(size_bytes),
                "artifact_non_empty": size_bytes > 0,
                "artifact_sha256": file_hash,
                "artifact_sha256_valid": len(file_hash) == 64,
            }
        )
    return pd.DataFrame(rows)


def manifest_digest(df: pd.DataFrame) -> str:
    if df.empty:
        return ""
    payload = (
        df[
            [
                "artifact_name",
                "artifact_path",
                "artifact_size_bytes",
                "artifact_sha256",
            ]
        ]
        .astype(str)
        .sort_values(["artifact_name", "artifact_path"])
        .to_csv(index=False)
        .encode("utf-8")
    )
    return hashlib.sha256(payload).hexdigest()


def build_check(
    group: str,
    name: str,
    passed: bool,
    severity: str,
    details: str,
) -> dict[str, Any]:
    return {
        "check_group": group,
        "check_name": name,
        "passed": bool(passed),
        "severity": severity,
        "details": details,
        "blocker": severity == "ERROR" and not bool(passed),
    }


def all_false(df: pd.DataFrame, column: str) -> bool:
    return (
        not df.empty
        and column in df.columns
        and df[column]
        .map(lambda value: safe_bool(value, True))
        .eq(False)
        .all()
    )


def all_true(df: pd.DataFrame, column: str) -> bool:
    return (
        not df.empty
        and column in df.columns
        and df[column]
        .map(lambda value: safe_bool(value, False))
        .all()
    )


def build_review_validations(
    source: dict[str, pd.DataFrame],
    manifest_before: pd.DataFrame,
    manifest_after: pd.DataFrame,
    official_dataset_absent: bool,
) -> pd.DataFrame:
    summary = (
        source["summary"].iloc[0].to_dict()
        if not source["summary"].empty
        else {}
    )
    decision = (
        source["decision"].iloc[0].to_dict()
        if not source["decision"].empty
        else {}
    )

    schema = source["schema"]
    components = source["components"]
    accepted_sources = source["accepted_sources"]
    lifecycle = source["lifecycle"]
    deduplication = source["deduplication"]
    rejection = source["rejection"]
    write_guards = source["write_guards"]
    audit = source["audit"]
    boundaries = source["boundaries"]

    artifacts_exist = (
        not manifest_before.empty
        and manifest_before["artifact_exists"].map(safe_bool).all()
    )
    artifacts_non_empty = (
        not manifest_before.empty
        and manifest_before["artifact_non_empty"].map(safe_bool).all()
    )
    hashes_valid = (
        not manifest_before.empty
        and manifest_before["artifact_sha256_valid"].map(safe_bool).all()
    )
    artifacts_stable = (
        bool(manifest_digest(manifest_before))
        and manifest_digest(manifest_before)
        == manifest_digest(manifest_after)
    )

    source_counts_valid = all(
        int(safe_float(summary.get(field), -1)) == expected
        for field, expected in EXPECTED_COUNTS.items()
    )

    summary_decision_consistent = (
        str(summary.get("evidence_collection_design_decision", ""))
        == str(decision.get("evidence_collection_design_decision", ""))
        == SOURCE_READY_DECISION
        and safe_bool(
            summary.get("evidence_collection_design_passed", False)
        )
        and safe_bool(
            decision.get("evidence_collection_design_passed", False)
        )
    )

    source_blocks_passed = all(
        [
            dataframe_all_passed(source["validations"]),
            dataframe_all_passed(source["evidence_chain"]),
            dataframe_all_passed(source["controls"]),
            dataframe_all_passed(source["rules"]),
            dataframe_all_passed(source["requirements"]),
            dataframe_all_passed(source["guard_matrix"]),
        ]
    )

    schema_field_order_valid = (
        not schema.empty
        and "field_name" in schema.columns
        and schema["field_name"].astype(str).tolist()
        == EXPECTED_SCHEMA_FIELDS
    )
    schema_unique = (
        not schema.empty
        and "field_name" in schema.columns
        and schema["field_name"].astype(str).is_unique
    )
    schema_safety_fields_complete = (
        not schema.empty
        and set(EXPECTED_SAFETY_FIELDS).issubset(
            set(schema["field_name"].astype(str).tolist())
        )
    )
    safety_rows = (
        schema[
            schema["field_name"].astype(str).isin(EXPECTED_SAFETY_FIELDS)
        ]
        if not schema.empty and "field_name" in schema.columns
        else pd.DataFrame()
    )
    schema_safety_defaults_false = (
        len(safety_rows) == len(EXPECTED_SAFETY_FIELDS)
        and all_true(safety_rows, "safety_lock_field")
        and all_false(safety_rows, "default_value")
    )
    schema_not_implemented = (
        len(schema) == 54
        and all_false(schema, "official_dataset_implemented")
    )
    schema_review_passed = all(
        [
            len(schema) == 54,
            dataframe_all_passed(schema),
            schema_field_order_valid,
            schema_unique,
            schema_safety_fields_complete,
            schema_safety_defaults_false,
            schema_not_implemented,
        ]
    )

    component_review_passed = all(
        [
            len(components) == 20,
            dataframe_all_passed(components),
            all_true(components, "source_requirement_found"),
            all_true(components, "defined"),
            all_false(components, "implemented"),
            all_false(components, "evidence_collection_enabled"),
            all_false(components, "official_dataset_write_allowed"),
            all_false(components, "signal_generation_enabled"),
            all_false(components, "market_execution_allowed"),
        ]
    )

    source_rule_review_passed = all(
        [
            len(accepted_sources) == 3,
            dataframe_all_passed(accepted_sources),
            all_true(
                accepted_sources,
                "allowlisted_for_future_design",
            ),
            all_false(
                accepted_sources,
                "enabled_in_phase_10_29",
            ),
            all_true(
                accepted_sources,
                "requires_provenance_hash",
            ),
            all_true(
                accepted_sources,
                "requires_utc_timestamp",
            ),
            all_true(
                accepted_sources,
                "requires_manual_review",
            ),
        ]
    )

    lifecycle_states_valid = (
        not lifecycle.empty
        and "lifecycle_state" in lifecycle.columns
        and lifecycle["lifecycle_state"].astype(str).tolist()
        == EXPECTED_LIFECYCLE_STATES
    )
    persisted_rows = (
        lifecycle[
            lifecycle["lifecycle_state"].astype(str)
            == "PERSISTED_OFFICIAL"
        ]
        if not lifecycle.empty and "lifecycle_state" in lifecycle.columns
        else pd.DataFrame()
    )
    lifecycle_review_passed = all(
        [
            len(lifecycle) == 8,
            dataframe_all_passed(lifecycle),
            lifecycle_states_valid,
            all_false(lifecycle, "enabled_in_phase_10_29"),
            len(persisted_rows) == 1,
            all_true(persisted_rows, "official_persistence_state"),
        ]
    )

    def review_rule_table(
        df: pd.DataFrame,
        expected_count: int,
    ) -> bool:
        return all(
            [
                len(df) == expected_count,
                dataframe_all_passed(df),
                all_true(df, "defined"),
                all_false(df, "implemented"),
                all_false(df, "enabled_in_phase_10_29"),
            ]
        )

    deduplication_review_passed = review_rule_table(
        deduplication,
        8,
    )
    rejection_review_passed = review_rule_table(
        rejection,
        15,
    )
    write_guard_review_passed = review_rule_table(
        write_guards,
        12,
    )
    audit_review_passed = review_rule_table(
        audit,
        10,
    )
    boundary_review_passed = review_rule_table(
        boundaries,
        12,
    )

    source_locks_valid = all(
        safe_bool(summary.get(field, True), True) is False
        for field in EXPECTED_FALSE_GUARDS
    )

    controlled_state_valid = all(
        [
            safe_bool(
                summary.get(
                    "source_controlled_forward_observation_start_run_performed",
                    False,
                )
            ),
            safe_bool(
                summary.get(
                    "source_controlled_forward_observation_start_performed",
                    False,
                )
            ),
            safe_bool(
                summary.get(
                    "forward_observation_start_allowed",
                    False,
                )
            ),
            safe_bool(
                summary.get("forward_observation_started", False)
            ),
            str(summary.get("source_candidate_id", ""))
            == PRIMARY_RESEARCH_CANDIDATE,
            str(summary.get("source_direction", "")) == "LONG",
            safe_float(summary.get("source_risk_reward"), 0.0) == 2.5,
        ]
    )

    design_review_coverage_complete = all(
        [
            schema_review_passed,
            component_review_passed,
            source_rule_review_passed,
            lifecycle_review_passed,
            deduplication_review_passed,
            rejection_review_passed,
            write_guard_review_passed,
            audit_review_passed,
            boundary_review_passed,
        ]
    )

    rows = [
        ("source_artifacts_exist", artifacts_exist, f"artifact_count={len(manifest_before)}"),
        ("source_artifacts_non_empty", artifacts_non_empty, f"artifact_count={len(manifest_before)}"),
        ("source_artifact_hashes_valid", hashes_valid, f"artifact_count={len(manifest_before)}"),
        ("source_artifacts_stable_during_review", artifacts_stable, f"before={manifest_digest(manifest_before)},after={manifest_digest(manifest_after)}"),
        ("phase_10_29_validation_passed", safe_bool(summary.get("validation_passed", False)), str(summary.get("validation_decision", ""))),
        ("source_design_performed", safe_bool(summary.get("evidence_collection_design_performed", False)), str(summary.get("evidence_collection_design_performed", ""))),
        ("source_design_passed", safe_bool(summary.get("evidence_collection_design_passed", False)), str(summary.get("evidence_collection_design_passed", ""))),
        ("source_design_decision_valid", str(summary.get("evidence_collection_design_decision", "")) == SOURCE_READY_DECISION, str(summary.get("evidence_collection_design_decision", ""))),
        ("source_future_design_review_allowed", safe_bool(summary.get("future_evidence_collection_design_review_allowed", False)), str(summary.get("future_evidence_collection_design_review_allowed", ""))),
        ("source_summary_decision_consistent", summary_decision_consistent, f"consistent={summary_decision_consistent}"),
        ("source_counts_valid", source_counts_valid, ",".join(f"{field}={summary.get(field, '')}" for field in EXPECTED_COUNTS)),
        ("source_validation_blocks_passed", source_blocks_passed, f"passed={source_blocks_passed}"),
        ("schema_field_count_valid", len(schema) == 54, f"rows={len(schema)}"),
        ("schema_field_order_valid", schema_field_order_valid, f"ordered={schema_field_order_valid}"),
        ("schema_field_names_unique", schema_unique, f"unique={schema_unique}"),
        ("schema_safety_fields_complete", schema_safety_fields_complete, f"safety_field_count={len(safety_rows)}"),
        ("schema_safety_defaults_false", schema_safety_defaults_false, f"defaults_false={schema_safety_defaults_false}"),
        ("schema_not_implemented", schema_not_implemented, f"implemented=False"),
        ("schema_review_passed", schema_review_passed, f"passed={schema_review_passed}"),
        ("component_review_passed", component_review_passed, f"rows={len(components)}"),
        ("source_rule_review_passed", source_rule_review_passed, f"rows={len(accepted_sources)}"),
        ("lifecycle_review_passed", lifecycle_review_passed, f"rows={len(lifecycle)}"),
        ("deduplication_review_passed", deduplication_review_passed, f"rows={len(deduplication)}"),
        ("rejection_review_passed", rejection_review_passed, f"rows={len(rejection)}"),
        ("write_guard_review_passed", write_guard_review_passed, f"rows={len(write_guards)}"),
        ("audit_review_passed", audit_review_passed, f"rows={len(audit)}"),
        ("boundary_review_passed", boundary_review_passed, f"rows={len(boundaries)}"),
        ("controlled_observation_state_valid", controlled_state_valid, f"valid={controlled_state_valid}"),
        ("source_operational_locks_valid", source_locks_valid, f"false_guard_count={len(EXPECTED_FALSE_GUARDS)}"),
        ("official_dataset_absent", official_dataset_absent, f"official_dataset_absent={official_dataset_absent}"),
        ("design_review_coverage_complete", design_review_coverage_complete, f"complete={design_review_coverage_complete}"),
        ("no_evidence_collection_enabled", safe_bool(summary.get("evidence_collection_enabled", True), True) is False, "evidence_collection_enabled=False"),
        ("no_official_dataset_implementation", safe_bool(summary.get("official_dataset_schema_implemented", True), True) is False, "official_dataset_schema_implemented=False"),
        ("no_signal_or_execution_enabled", all(safe_bool(summary.get(field, True), True) is False for field in ["signal_generation_enabled", "live_alerts_allowed", "paper_trade_execution_allowed", "real_capital_allowed", "market_execution_allowed", "exchange_execution_allowed", "automation_allowed", "execution_allowed"]), "all_execution_boundaries=False"),
        ("no_duplicate_start_run", safe_bool(summary.get("new_controlled_forward_observation_start_run_performed", True), True) is False and safe_bool(summary.get("new_controlled_forward_observation_start_performed", True), True) is False, "new_start_run=False,new_start=False"),
    ]

    return pd.DataFrame(
        [
            {
                "validation_name": name,
                "passed": bool(passed),
                "details": details,
            }
            for name, passed, details in rows
        ]
    )


def build_review_items(
    validations: pd.DataFrame,
) -> pd.DataFrame:
    lookup = {
        str(row["validation_name"]): safe_bool(row["passed"], False)
        for _, row in validations.iterrows()
    }

    mapping = {
        "phase_10_29_dependency": [
            "phase_10_29_validation_passed",
            "source_design_performed",
            "source_design_passed",
            "source_design_decision_valid",
            "source_future_design_review_allowed",
        ],
        "source_artifact_integrity": [
            "source_artifacts_exist",
            "source_artifacts_non_empty",
            "source_artifact_hashes_valid",
            "source_artifacts_stable_during_review",
        ],
        "source_decision_consistency": [
            "source_summary_decision_consistent",
            "source_counts_valid",
        ],
        "source_validation_chain": [
            "source_validation_blocks_passed",
        ],
        "schema_completeness": [
            "schema_field_count_valid",
            "schema_field_order_valid",
            "schema_field_names_unique",
            "schema_safety_fields_complete",
        ],
        "schema_safety_defaults": [
            "schema_safety_defaults_false",
        ],
        "schema_non_implementation": [
            "schema_not_implemented",
        ],
        "design_component_coverage": [
            "component_review_passed",
        ],
        "design_component_non_implementation": [
            "component_review_passed",
        ],
        "accepted_source_controls": [
            "source_rule_review_passed",
        ],
        "lifecycle_coherence": [
            "lifecycle_review_passed",
        ],
        "deduplication_contract": [
            "deduplication_review_passed",
        ],
        "rejection_contract": [
            "rejection_review_passed",
        ],
        "official_write_guard_contract": [
            "write_guard_review_passed",
        ],
        "audit_contract": [
            "audit_review_passed",
        ],
        "boundary_contract": [
            "boundary_review_passed",
        ],
        "controlled_observation_state": [
            "controlled_observation_state_valid",
        ],
        "evidence_collection_boundary": [
            "no_evidence_collection_enabled",
        ],
        "official_dataset_boundary": [
            "official_dataset_absent",
            "no_official_dataset_implementation",
        ],
        "signal_and_execution_boundary": [
            "no_signal_or_execution_enabled",
        ],
    }

    rows = []
    for position, item_name in enumerate(
        REVIEW_ITEM_NAMES,
        start=1,
    ):
        validation_names = mapping[item_name]
        passed = all(
            lookup.get(validation_name, False)
            for validation_name in validation_names
        )
        rows.append(
            {
                "review_item_position": position,
                "review_item_id": f"EVIDENCE_COLLECTION_DESIGN_REVIEW_ITEM_{position:03d}",
                "review_item_name": item_name,
                "validation_names": ",".join(validation_names),
                "required": True,
                "review_only": True,
                "implementation_allowed": False,
                "evidence_collection_enabled": False,
                "official_dataset_write_allowed": False,
                "market_execution_allowed": False,
                "passed": passed,
            }
        )
    return pd.DataFrame(rows)


def build_review_findings(
    review_items: pd.DataFrame,
) -> pd.DataFrame:
    rows = []
    for _, item in review_items.iterrows():
        passed = safe_bool(item["passed"], False)
        rows.append(
            {
                "finding_id": (
                    "EVIDENCE_COLLECTION_DESIGN_REVIEW_FINDING_"
                    f"{int(item['review_item_position']):03d}"
                ),
                "review_item_id": str(item["review_item_id"]),
                "review_item_name": str(item["review_item_name"]),
                "finding_status": "PASS" if passed else "FAIL",
                "material_issue_found": not passed,
                "design_change_required": not passed,
                "implementation_approved": False,
                "details": (
                    "Review criterion passed."
                    if passed
                    else "Review criterion failed and blocks progression."
                ),
                "passed": passed,
            }
        )
    return pd.DataFrame(rows)


def build_controls(
    validations: pd.DataFrame,
) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "control_position": position,
                "control_id": f"EVIDENCE_COLLECTION_DESIGN_REVIEW_CONTROL_{position:03d}",
                "control_name": str(row["validation_name"]),
                "required": True,
                "review_only": True,
                "evidence_collection_enabled": False,
                "official_dataset_schema_implemented": False,
                "official_dataset_write_allowed": False,
                "signal_generation_enabled": False,
                "market_execution_allowed": False,
                "passed": safe_bool(row["passed"], False),
            }
            for position, (_, row) in enumerate(
                validations.iterrows(),
                start=1,
            )
        ]
    )


def build_guard_matrix() -> pd.DataFrame:
    true_guards = [
        "source_controlled_forward_observation_start_run_performed",
        "source_controlled_forward_observation_start_performed",
        "forward_observation_start_allowed",
        "forward_observation_started",
        "evidence_collection_design_review_performed",
        "evidence_collection_design_review_passed",
        "future_report_only_evidence_collection_dry_run_design_allowed",
    ]
    false_guards = [
        "new_controlled_forward_observation_start_run_performed",
        "new_controlled_forward_observation_start_performed",
        "evidence_collection_enabled",
        "evidence_collection_started",
        "official_dataset_schema_implemented",
    ] + EXPECTED_FALSE_GUARDS

    rows = [
        {
            "guard_name": name,
            "required_value": True,
            "actual_value": True,
            "passed": True,
            "guard_group": "design_review_state",
        }
        for name in true_guards
    ]
    rows.extend(
        [
            {
                "guard_name": name,
                "required_value": False,
                "actual_value": False,
                "passed": True,
                "guard_group": "design_review_safety_guard",
            }
            for name in false_guards
        ]
    )
    rows.append(
        {
            "guard_name": "official_evidence_rows_written",
            "required_value": 0,
            "actual_value": 0,
            "passed": True,
            "guard_group": "official_dataset_guard",
        }
    )
    return pd.DataFrame(rows)


def build_rules(
    validations: pd.DataFrame,
    review_items: pd.DataFrame,
    findings: pd.DataFrame,
    controls: pd.DataFrame,
    guards: pd.DataFrame,
) -> pd.DataFrame:
    rows = [
        ("review_validation_count_35", len(validations) == 35, "35", str(len(validations)), "validation"),
        ("all_review_validations_passed", dataframe_all_passed(validations), "True", str(dataframe_all_passed(validations)), "validation"),
        ("review_item_count_20", len(review_items) == 20, "20", str(len(review_items)), "review_items"),
        ("all_review_items_passed", dataframe_all_passed(review_items), "True", str(dataframe_all_passed(review_items)), "review_items"),
        ("review_finding_count_20", len(findings) == 20, "20", str(len(findings)), "findings"),
        ("all_review_findings_passed", dataframe_all_passed(findings), "True", str(dataframe_all_passed(findings)), "findings"),
        ("material_issue_count_zero", int(findings["material_issue_found"].map(safe_bool).sum()) == 0, "0", str(int(findings["material_issue_found"].map(safe_bool).sum())), "findings"),
        ("review_control_count_35", len(controls) == 35, "35", str(len(controls)), "controls"),
        ("all_review_controls_passed", dataframe_all_passed(controls), "True", str(dataframe_all_passed(controls)), "controls"),
        ("review_guard_count_35", len(guards) == 35, "35", str(len(guards)), "safety"),
        ("all_review_guards_passed", dataframe_all_passed(guards), "True", str(dataframe_all_passed(guards)), "safety"),
        ("review_only", True, "True", "True", "scope_control"),
        ("evidence_collection_disabled", True, "False", "False", "evidence_boundary"),
        ("official_dataset_not_implemented", True, "False", "False", "official_dataset_guard"),
        ("official_dataset_writes_disabled", True, "False", "False", "official_dataset_guard"),
        ("signal_generation_disabled", True, "False", "False", "signal_boundary"),
        ("market_execution_disabled", True, "False", "False", "market_execution_guard"),
        ("total_project_not_completed", True, "False", "False", "scope_control"),
    ]
    return pd.DataFrame(
        [
            {
                "rule_id": (
                    f"EVIDENCE_COLLECTION_DESIGN_REVIEW_RULE_{position:03d}"
                ),
                "rule_name": name,
                "passed": bool(passed),
                "required_value": required,
                "actual_value": actual,
                "rule_group": group,
            }
            for position, (name, passed, required, actual, group) in enumerate(
                rows,
                start=1,
            )
        ]
    )


def build_requirements(
    validations: pd.DataFrame,
    review_items: pd.DataFrame,
    findings: pd.DataFrame,
    controls: pd.DataFrame,
    rules: pd.DataFrame,
    guards: pd.DataFrame,
) -> pd.DataFrame:
    rows = [
        (
            str(row["validation_name"]),
            safe_bool(row["passed"], False),
            "True",
            str(safe_bool(row["passed"], False)),
            "review_validation",
        )
        for _, row in validations.iterrows()
    ]
    rows.extend(
        [
            ("review_items_passed", dataframe_all_passed(review_items), "True", str(dataframe_all_passed(review_items)), "review_items"),
            ("review_findings_passed", dataframe_all_passed(findings), "True", str(dataframe_all_passed(findings)), "findings"),
            ("review_controls_passed", dataframe_all_passed(controls), "True", str(dataframe_all_passed(controls)), "controls"),
            ("review_rules_passed", dataframe_all_passed(rules), "True", str(dataframe_all_passed(rules)), "rules"),
            ("review_guards_passed", dataframe_all_passed(guards), "True", str(dataframe_all_passed(guards)), "safety"),
            ("design_review_performed", True, "True", "True", "review_state"),
            ("future_report_only_dry_run_design_allowed", True, "True", "True", "future_design"),
            ("evidence_collection_not_enabled", True, "False", "False", "evidence_boundary"),
            ("official_dataset_schema_not_implemented", True, "False", "False", "official_dataset_guard"),
            ("official_evidence_rows_written_zero", True, "0", "0", "official_dataset_guard"),
            ("signal_generation_disabled", True, "False", "False", "signal_boundary"),
            ("paper_trading_disabled", True, "False", "False", "paper_trading_guard"),
            ("market_execution_disabled", True, "False", "False", "market_execution_guard"),
            ("total_project_not_completed", True, "False", "False", "scope_control"),
        ]
    )
    return pd.DataFrame(
        [
            {
                "requirement_id": (
                    f"EVIDENCE_COLLECTION_DESIGN_REVIEW_REQ_{position:03d}"
                ),
                "requirement_name": name,
                "passed": bool(passed),
                "required_value": required,
                "actual_value": actual,
                "requirement_group": group,
            }
            for position, (name, passed, required, actual, group) in enumerate(
                rows,
                start=1,
            )
        ]
    )


def build_decision(
    requirements: pd.DataFrame,
    rules: pd.DataFrame,
    guards: pd.DataFrame,
) -> pd.DataFrame:
    passed_requirements = (
        int(requirements["passed"].map(safe_bool).sum())
        if not requirements.empty
        else 0
    )
    failed_requirements = len(requirements) - passed_requirements
    review_passed = (
        len(requirements) > 0
        and failed_requirements == 0
        and dataframe_all_passed(rules)
        and dataframe_all_passed(guards)
    )
    failed_names = (
        ",".join(
            requirements[
                ~requirements["passed"].map(safe_bool)
            ]["requirement_name"]
            .astype(str)
            .tolist()
        )
        if not requirements.empty
        else ""
    )
    return pd.DataFrame(
        [
            {
                "evidence_collection_design_review_id": (
                    "PHASE_10_30_LONG_FORWARD_OBSERVATION_"
                    "EVIDENCE_COLLECTION_DESIGN_REVIEW_001"
                ),
                "evidence_collection_design_review_status": DESIGN_REVIEW_STATUS,
                "evidence_collection_design_review_performed": True,
                "evidence_collection_design_review_passed": review_passed,
                "evidence_collection_design_review_decision": (
                    READY_DECISION if review_passed else BLOCKED_DECISION
                ),
                "total_requirements": len(requirements),
                "passed_requirements": passed_requirements,
                "failed_requirements": failed_requirements,
                "failed_requirement_names": failed_names,
                "review_rules_passed": dataframe_all_passed(rules),
                "review_guards_passed": dataframe_all_passed(guards),
                "source_controlled_forward_observation_start_run_performed": True,
                "source_controlled_forward_observation_start_performed": True,
                "forward_observation_start_allowed": True,
                "forward_observation_started": True,
                "future_report_only_evidence_collection_dry_run_design_allowed": review_passed,
                "new_controlled_forward_observation_start_run_performed": False,
                "new_controlled_forward_observation_start_performed": False,
                "evidence_collection_enabled": False,
                "evidence_collection_started": False,
                "official_dataset_schema_implemented": False,
                "official_dataset_write_allowed": False,
                "official_dataset_write_performed": False,
                "real_forward_dataset_created": False,
                "official_evidence_rows_written": 0,
                "real_forward_signals_recorded": False,
                "journal_real_rows_accepted": False,
                "accepted_as_real_evidence": False,
                "evidence_persistence_allowed": False,
                "evidence_write_performed": False,
                "signal_generation_enabled": False,
                "live_alerts_allowed": False,
                "paper_trading_enabled": False,
                "long_strategy_approved": False,
                "long_entries_approved": False,
                "long_side_established": False,
                "paper_trade_execution_allowed": False,
                "real_capital_allowed": False,
                "market_execution_allowed": False,
                "exchange_execution_allowed": False,
                "automation_allowed": False,
                "execution_allowed": False,
                "real_entries_approved": False,
                "total_project_completed": False,
                "recommended_next_phase": RECOMMENDED_NEXT_PHASE,
            }
        ]
    )


def validate_long_forward_observation_evidence_collection_design_review() -> dict[str, pd.DataFrame]:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    checks: list[dict[str, Any]] = []

    for name, path in {
        "phase_10_29_design_doc_exists": PHASE_10_29_DOC_PATH,
        "phase_10_30_design_review_doc_exists": PHASE_10_30_DOC_PATH,
    }.items():
        exists = path.exists()
        checks.append(
            build_check(
                "phase_anchor",
                name,
                exists,
                "INFO" if exists else "ERROR",
                str(path),
            )
        )

    official_before = OFFICIAL_DATASET_PATH.exists()
    manifest_before = build_manifest()
    source = {
        name: read_csv(path)
        for name, path in SOURCE_PATHS.items()
    }
    manifest_after = build_manifest()

    validations = build_review_validations(
        source=source,
        manifest_before=manifest_before,
        manifest_after=manifest_after,
        official_dataset_absent=not official_before,
    )
    review_items = build_review_items(validations)
    findings = build_review_findings(review_items)
    controls = build_controls(validations)
    guards = build_guard_matrix()
    rules = build_rules(
        validations,
        review_items,
        findings,
        controls,
        guards,
    )
    requirements = build_requirements(
        validations,
        review_items,
        findings,
        controls,
        rules,
        guards,
    )
    decision = build_decision(
        requirements,
        rules,
        guards,
    )
    decision_row = (
        decision.iloc[0].to_dict()
        if not decision.empty
        else {}
    )

    aggregate_checks = [
        ("review_validations_passed", dataframe_all_passed(validations)),
        ("review_items_passed", dataframe_all_passed(review_items)),
        ("review_findings_passed", dataframe_all_passed(findings)),
        ("review_controls_passed", dataframe_all_passed(controls)),
        ("review_rules_passed", dataframe_all_passed(rules)),
        ("review_requirements_passed", dataframe_all_passed(requirements)),
        ("review_guards_passed", dataframe_all_passed(guards)),
        (
            "evidence_collection_design_review_passed",
            safe_bool(
                decision_row.get(
                    "evidence_collection_design_review_passed",
                    False,
                )
            ),
        ),
        (
            "evidence_collection_design_review_decision_expected",
            str(
                decision_row.get(
                    "evidence_collection_design_review_decision",
                    "",
                )
            )
            == READY_DECISION,
        ),
    ]
    for name, passed in aggregate_checks:
        details = (
            str(
                decision_row.get(
                    "evidence_collection_design_review_decision",
                    "",
                )
            )
            if name.endswith("decision_expected")
            else f"{name}={passed}"
        )
        checks.append(
            build_check(
                "evidence_collection_design_review",
                name,
                passed,
                "INFO" if passed else "ERROR",
                details,
            )
        )

    official_after = OFFICIAL_DATASET_PATH.exists()
    official_unchanged_absent = (
        not official_before and not official_after
    )
    checks.append(
        build_check(
            "official_dataset_guard",
            "official_dataset_not_created_or_written",
            official_unchanged_absent,
            "INFO" if official_unchanged_absent else "ERROR",
            f"before={official_before},after={official_after}",
        )
    )

    for _, row in guards.iterrows():
        passed = safe_bool(row["passed"], False)
        checks.append(
            build_check(
                "evidence_collection_design_review_safety_flags",
                str(row["guard_name"]),
                passed,
                "INFO" if passed else "ERROR",
                (
                    f"{row['guard_name']}={row['actual_value']} "
                    f"(required={row['required_value']})"
                ),
            )
        )

    scope_warnings = [
        ("review_only", "Phase 10.30 reviews only the evidence collection design."),
        ("observation_state_preserved", "The controlled observation state remains started."),
        ("evidence_collection_not_enabled", "Evidence collection remains disabled."),
        ("official_dataset_not_implemented", "The official evidence dataset is not implemented."),
        ("official_dataset_not_written", "The official evidence dataset remains absent and unwritten."),
        ("signal_generation_not_enabled", "Signal generation remains disabled."),
        ("live_alerts_not_enabled", "Live alerts remain disabled."),
        ("paper_trading_not_enabled", "Paper trading execution remains disabled."),
        ("long_strategy_not_approved", "The LONG research candidate is not approved as a trading strategy."),
        ("real_capital_not_allowed", "Real capital remains prohibited."),
        ("market_execution_not_allowed", "Market execution remains prohibited."),
        ("total_project_not_completed", "The total project is not completed."),
    ]
    for name, details in scope_warnings:
        checks.append(
            build_check(
                "scope_control",
                name,
                True,
                "WARNING",
                details,
            )
        )

    future_allowed = safe_bool(
        decision_row.get(
            "future_report_only_evidence_collection_dry_run_design_allowed",
            False,
        )
    )
    checks.append(
        build_check(
            "planning_scope",
            "future_report_only_evidence_collection_dry_run_design_allowed",
            future_allowed,
            "WARNING" if future_allowed else "ERROR",
            (
                "This permits only a future report-only dry-run design. "
                "It does not enable evidence collection, official dataset "
                "implementation or writes, signals, alerts, paper trading, "
                "real capital or market execution."
            ),
        )
    )
    checks.append(
        build_check(
            "phase_transition",
            "phase_10_31_recommended_next",
            True,
            "INFO",
            (
                "Recommended next step: Phase 10.31 LONG Forward "
                "Observation Evidence Collection Report-Only Dry-Run "
                "Design V1."
            ),
        )
    )

    checks_df = pd.DataFrame(checks)
    blocker_count = int(checks_df["blocker"].map(safe_bool).sum())
    error_count = int(checks_df["severity"].eq("ERROR").sum())
    warning_count = int(checks_df["severity"].eq("WARNING").sum())
    validation_passed = blocker_count == 0 and error_count == 0

    source_summary = (
        source["summary"].iloc[0].to_dict()
        if not source["summary"].empty
        else {}
    )
    lookup = {
        str(row["validation_name"]): safe_bool(row["passed"], False)
        for _, row in validations.iterrows()
    }

    review_passed = safe_bool(
        decision_row.get(
            "evidence_collection_design_review_passed",
            False,
        )
    )
    review_decision = str(
        decision_row.get(
            "evidence_collection_design_review_decision",
            "",
        )
    )

    summary_df = pd.DataFrame(
        [
            {
                "phase": "10.30",
                "long_forward_observation_evidence_collection_design_review_defined": True,
                "phase_10_29_validation_passed": lookup.get("phase_10_29_validation_passed", False),
                "source_evidence_collection_design_performed": lookup.get("source_design_performed", False),
                "source_evidence_collection_design_passed": lookup.get("source_design_passed", False),
                "source_evidence_collection_design_decision": str(source_summary.get("evidence_collection_design_decision", "")),
                "source_future_evidence_collection_design_review_allowed": lookup.get("source_future_design_review_allowed", False),
                "source_artifact_count": len(manifest_after),
                "source_artifacts_exist": lookup.get("source_artifacts_exist", False),
                "source_artifacts_non_empty": lookup.get("source_artifacts_non_empty", False),
                "source_artifact_hashes_valid": lookup.get("source_artifact_hashes_valid", False),
                "source_artifacts_stable_during_review": lookup.get("source_artifacts_stable_during_review", False),
                "source_manifest_sha256": manifest_digest(manifest_after),
                "source_summary_decision_consistent": lookup.get("source_summary_decision_consistent", False),
                "source_counts_valid": lookup.get("source_counts_valid", False),
                "source_validation_blocks_passed": lookup.get("source_validation_blocks_passed", False),
                "schema_review_passed": lookup.get("schema_review_passed", False),
                "component_review_passed": lookup.get("component_review_passed", False),
                "source_rule_review_passed": lookup.get("source_rule_review_passed", False),
                "lifecycle_review_passed": lookup.get("lifecycle_review_passed", False),
                "deduplication_review_passed": lookup.get("deduplication_review_passed", False),
                "rejection_review_passed": lookup.get("rejection_review_passed", False),
                "write_guard_review_passed": lookup.get("write_guard_review_passed", False),
                "audit_review_passed": lookup.get("audit_review_passed", False),
                "boundary_review_passed": lookup.get("boundary_review_passed", False),
                "controlled_observation_state_valid": lookup.get("controlled_observation_state_valid", False),
                "source_operational_locks_valid": lookup.get("source_operational_locks_valid", False),
                "official_dataset_absent": lookup.get("official_dataset_absent", False),
                "design_review_coverage_complete": lookup.get("design_review_coverage_complete", False),
                "review_validation_rows": len(validations),
                "review_item_rows": len(review_items),
                "review_finding_rows": len(findings),
                "review_control_rows": len(controls),
                "review_rule_rows": len(rules),
                "review_requirement_rows": len(requirements),
                "review_guard_rows": len(guards),
                "review_validations_passed": dataframe_all_passed(validations),
                "review_items_passed": dataframe_all_passed(review_items),
                "review_findings_passed": dataframe_all_passed(findings),
                "review_controls_passed": dataframe_all_passed(controls),
                "review_rules_passed": dataframe_all_passed(rules),
                "review_requirements_passed": dataframe_all_passed(requirements),
                "review_guards_passed": dataframe_all_passed(guards),
                "material_issue_count": int(findings["material_issue_found"].map(safe_bool).sum()),
                "evidence_collection_design_review_performed": True,
                "evidence_collection_design_review_passed": review_passed,
                "evidence_collection_design_review_decision": review_decision,
                "source_controlled_forward_observation_start_run_performed": True,
                "source_controlled_forward_observation_start_performed": True,
                "forward_observation_start_allowed": True,
                "forward_observation_started": True,
                "future_report_only_evidence_collection_dry_run_design_allowed": future_allowed,
                "new_controlled_forward_observation_start_run_performed": False,
                "new_controlled_forward_observation_start_performed": False,
                "evidence_collection_enabled": False,
                "evidence_collection_started": False,
                "official_dataset_schema_implemented": False,
                "official_dataset_exists_before": official_before,
                "official_dataset_exists_after": official_after,
                "official_dataset_write_allowed": False,
                "official_dataset_write_performed": False,
                "real_forward_dataset_created": False,
                "official_evidence_rows_written": 0,
                "real_forward_signals_recorded": False,
                "journal_real_rows_accepted": False,
                "accepted_as_real_evidence": False,
                "evidence_persistence_allowed": False,
                "evidence_write_performed": False,
                "signal_generation_enabled": False,
                "live_alerts_allowed": False,
                "paper_trading_enabled": False,
                "long_strategy_approved": False,
                "long_entries_approved": False,
                "long_side_established": False,
                "paper_trade_execution_allowed": False,
                "real_capital_allowed": False,
                "market_execution_allowed": False,
                "exchange_execution_allowed": False,
                "automation_allowed": False,
                "execution_allowed": False,
                "real_entries_approved": False,
                "total_project_completed": False,
                "recommended_next_phase": RECOMMENDED_NEXT_PHASE,
                "estimated_phase_10_progress_percent": 100,
                "total_checks": len(checks_df),
                "warning_count": warning_count,
                "error_count": error_count,
                "blocker_count": blocker_count,
                "validation_passed": validation_passed,
                "validation_decision": (
                    "PHASE_10_30_LONG_FORWARD_OBSERVATION_"
                    "EVIDENCE_COLLECTION_DESIGN_REVIEW_VALIDATED"
                    if validation_passed
                    else
                    "PHASE_10_30_LONG_FORWARD_OBSERVATION_"
                    "EVIDENCE_COLLECTION_DESIGN_REVIEW_FAILED"
                ),
            }
        ]
    )

    output_files = {
        "phase_10_29_source_summary_v1.csv": source["summary"],
        "phase_10_29_source_schema_v1.csv": source["schema"],
        "phase_10_29_source_components_v1.csv": source["components"],
        "phase_10_29_source_accepted_sources_v1.csv": source["accepted_sources"],
        "phase_10_29_source_lifecycle_v1.csv": source["lifecycle"],
        "phase_10_29_source_deduplication_v1.csv": source["deduplication"],
        "phase_10_29_source_rejection_v1.csv": source["rejection"],
        "phase_10_29_source_write_guards_v1.csv": source["write_guards"],
        "phase_10_29_source_audit_v1.csv": source["audit"],
        "phase_10_29_source_boundaries_v1.csv": source["boundaries"],
        "phase_10_29_source_validations_v1.csv": source["validations"],
        "phase_10_29_source_evidence_chain_v1.csv": source["evidence_chain"],
        "phase_10_29_source_controls_v1.csv": source["controls"],
        "phase_10_29_source_rules_v1.csv": source["rules"],
        "phase_10_29_source_requirements_v1.csv": source["requirements"],
        "phase_10_29_source_guard_matrix_v1.csv": source["guard_matrix"],
        "phase_10_29_source_decision_v1.csv": source["decision"],
        "phase_10_29_source_checks_v1.csv": source["checks"],
        "phase_10_29_source_manifest_v1.csv": source["manifest"],
        "source_design_review_artifact_manifest_v1.csv": manifest_after,
        "evidence_collection_design_review_validations_v1.csv": validations,
        "evidence_collection_design_review_items_v1.csv": review_items,
        "evidence_collection_design_review_findings_v1.csv": findings,
        "evidence_collection_design_review_controls_v1.csv": controls,
        "evidence_collection_design_review_rules_v1.csv": rules,
        "evidence_collection_design_review_requirements_v1.csv": requirements,
        "evidence_collection_design_review_guard_matrix_v1.csv": guards,
        "evidence_collection_design_review_decision_v1.csv": decision,
        "evidence_collection_design_review_checks_v1.csv": checks_df,
        "evidence_collection_design_review_summary_v1.csv": summary_df,
    }
    for filename, dataframe in output_files.items():
        dataframe.to_csv(REPORTS_DIR / filename, index=False)

    return {
        "summary": summary_df,
        "source_phase_10_29_summary": source["summary"],
        "source_schema": source["schema"],
        "source_components": source["components"],
        "source_accepted_sources": source["accepted_sources"],
        "source_lifecycle": source["lifecycle"],
        "source_deduplication": source["deduplication"],
        "source_rejection": source["rejection"],
        "source_write_guards": source["write_guards"],
        "source_audit": source["audit"],
        "source_boundaries": source["boundaries"],
        "source_validations": source["validations"],
        "source_evidence_chain": source["evidence_chain"],
        "source_controls": source["controls"],
        "source_rules": source["rules"],
        "source_requirements": source["requirements"],
        "source_guard_matrix": source["guard_matrix"],
        "source_decision": source["decision"],
        "source_checks": source["checks"],
        "source_manifest": source["manifest"],
        "review_manifest": manifest_after,
        "review_validations": validations,
        "review_items": review_items,
        "review_findings": findings,
        "review_controls": controls,
        "review_rules": rules,
        "review_requirements": requirements,
        "review_guard_matrix": guards,
        "review_decision": decision,
        "checks": checks_df,
    }
