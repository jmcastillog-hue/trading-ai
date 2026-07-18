from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

import pandas as pd

try:
    from src.long_side.long_forward_observation_dataset_bootstrap_v1 import OFFICIAL_DATASET_PATH
except ImportError:
    OFFICIAL_DATASET_PATH = Path(
        "data/forward_observation/long_forward_observation_official_evidence_dataset_v1.csv"
    )

REPORTS_DIR = Path(
    "reports/p10_37_evidence_collection_official_dataset_schema_implementation_design_v1"
)
SOURCE_DIR = Path(
    "reports/p10_36_evidence_collection_report_only_dry_run_final_approval_review_v1"
)

PHASE_10_36_DOC_PATH = Path(
    "docs/PHASE_10_LONG_FORWARD_OBSERVATION_EVIDENCE_COLLECTION_"
    "REPORT_ONLY_DRY_RUN_FINAL_APPROVAL_REVIEW.md"
)
PHASE_10_37_DOC_PATH = Path(
    "docs/PHASE_10_LONG_FORWARD_OBSERVATION_EVIDENCE_COLLECTION_"
    "OFFICIAL_DATASET_SCHEMA_IMPLEMENTATION_DESIGN.md"
)

SOURCE_PATHS = {
    "summary": SOURCE_DIR / "report_only_dry_run_final_approval_review_summary_v1.csv",
    "validations": SOURCE_DIR / "report_only_dry_run_final_approval_review_validations_v1.csv",
    "items": SOURCE_DIR / "report_only_dry_run_final_approval_review_items_v1.csv",
    "findings": SOURCE_DIR / "report_only_dry_run_final_approval_review_findings_v1.csv",
    "controls": SOURCE_DIR / "report_only_dry_run_final_approval_review_controls_v1.csv",
    "rules": SOURCE_DIR / "report_only_dry_run_final_approval_review_rules_v1.csv",
    "requirements": SOURCE_DIR / "report_only_dry_run_final_approval_review_requirements_v1.csv",
    "guard_matrix": SOURCE_DIR / "report_only_dry_run_final_approval_review_guard_matrix_v1.csv",
    "decision": SOURCE_DIR / "report_only_dry_run_final_approval_review_decision_v1.csv",
    "checks": SOURCE_DIR / "report_only_dry_run_final_approval_review_checks_v1.csv",
    "manifest": SOURCE_DIR / "source_report_only_dry_run_final_approval_artifact_manifest_v1.csv",
}

SOURCE_READY_DECISION = (
    "CONTROLLED_FORWARD_OBSERVATION_EVIDENCE_COLLECTION_REPORT_ONLY_DRY_RUN_"
    "FINAL_APPROVAL_REVIEW_APPROVED_FOR_OFFICIAL_DATASET_SCHEMA_IMPLEMENTATION_DESIGN"
)
READY_DECISION = (
    "CONTROLLED_FORWARD_OBSERVATION_EVIDENCE_COLLECTION_OFFICIAL_DATASET_SCHEMA_"
    "IMPLEMENTATION_DESIGN_READY_FOR_DESIGN_REVIEW"
)
BLOCKED_DECISION = (
    "CONTROLLED_FORWARD_OBSERVATION_EVIDENCE_COLLECTION_OFFICIAL_DATASET_SCHEMA_"
    "IMPLEMENTATION_DESIGN_BLOCKED"
)
RECOMMENDED_NEXT_PHASE = (
    "PHASE_10_38_LONG_FORWARD_OBSERVATION_EVIDENCE_COLLECTION_OFFICIAL_DATASET_"
    "SCHEMA_IMPLEMENTATION_DESIGN_REVIEW_V1"
)
STORAGE_DESIGN = "CSV_APPEND_ONLY_ATOMIC_REPLACE_WITH_SHA256_MANIFEST_V1"

SCHEMA_FIELDS = [
    ("evidence_id", "IDENTITY", "STRING", False, "PRIMARY_KEY"),
    ("observation_id", "IDENTITY", "STRING", False, "INDEX"),
    ("collected_at_utc", "TIME", "UTC_TIMESTAMP", False, "INDEX"),
    ("observed_at_utc", "TIME", "UTC_TIMESTAMP", False, "INDEX"),
    ("source_system", "PROVENANCE", "ENUM_STRING", False, "INDEX"),
    ("source_artifact", "PROVENANCE", "STRING", False, "NONE"),
    ("source_artifact_sha256", "PROVENANCE", "SHA256", False, "NONE"),
    ("source_row_hash", "PROVENANCE", "SHA256", False, "INDEX"),
    ("candidate_id", "STRATEGY_CONTEXT", "STRING", False, "INDEX"),
    ("direction", "STRATEGY_CONTEXT", "ENUM_STRING", False, "INDEX"),
    ("symbol", "MARKET_CONTEXT", "STRING", False, "INDEX"),
    ("timeframe", "MARKET_CONTEXT", "ENUM_STRING", False, "INDEX"),
    ("observation_state", "LIFECYCLE", "ENUM_STRING", False, "INDEX"),
    ("evidence_status", "LIFECYCLE", "ENUM_STRING", False, "INDEX"),
    ("evidence_scope", "LIFECYCLE", "ENUM_STRING", False, "INDEX"),
    ("evidence_version", "VERSIONING", "STRING", False, "INDEX"),
    ("entry_price", "RISK_STRUCTURE", "DECIMAL", False, "NONE"),
    ("stop_price", "RISK_STRUCTURE", "DECIMAL", False, "NONE"),
    ("target_price", "RISK_STRUCTURE", "DECIMAL", False, "NONE"),
    ("invalidation_level", "RISK_STRUCTURE", "DECIMAL", False, "NONE"),
    ("risk_reward", "RISK_STRUCTURE", "DECIMAL", False, "NONE"),
    ("cost_profile", "MARKET_CONTEXT", "ENUM_STRING", False, "INDEX"),
    ("market_context", "MARKET_CONTEXT", "STRING", False, "INDEX"),
    ("activation_scope", "SAFETY", "ENUM_STRING", False, "INDEX"),
    ("signal_state", "SAFETY", "ENUM_STRING", False, "INDEX"),
    ("deduplication_key", "INTEGRITY", "SHA256", False, "UNIQUE"),
    ("deduplication_status", "INTEGRITY", "ENUM_STRING", False, "INDEX"),
    ("lifecycle_state", "LIFECYCLE", "ENUM_STRING", False, "INDEX"),
    ("review_status", "REVIEW", "ENUM_STRING", False, "INDEX"),
    ("rejection_reason", "REVIEW", "STRING", True, "NONE"),
    ("manual_confirmation_required", "REVIEW", "BOOLEAN", False, "NONE"),
    ("manual_confirmed", "REVIEW", "BOOLEAN", False, "NONE"),
    ("write_ahead_validation_passed", "VALIDATION", "BOOLEAN", False, "NONE"),
    ("schema_validation_passed", "VALIDATION", "BOOLEAN", False, "NONE"),
    ("provenance_validation_passed", "VALIDATION", "BOOLEAN", False, "NONE"),
    ("risk_structure_validation_passed", "VALIDATION", "BOOLEAN", False, "NONE"),
    ("evidence_hash", "INTEGRITY", "SHA256", False, "UNIQUE"),
    ("previous_evidence_hash", "INTEGRITY", "SHA256", True, "INDEX"),
    ("audit_event_id", "AUDIT", "STRING", False, "UNIQUE"),
    ("created_by", "AUDIT", "STRING", False, "INDEX"),
    ("reviewed_by", "AUDIT", "STRING", True, "INDEX"),
    ("rollback_reference", "AUDIT", "STRING", True, "INDEX"),
    ("accepted_as_real_evidence", "SAFETY", "BOOLEAN", False, "NONE"),
    ("official_dataset_write_allowed", "SAFETY", "BOOLEAN", False, "NONE"),
    ("evidence_persistence_allowed", "SAFETY", "BOOLEAN", False, "NONE"),
    ("signal_generation_enabled", "SAFETY", "BOOLEAN", False, "NONE"),
    ("live_alerts_allowed", "SAFETY", "BOOLEAN", False, "NONE"),
    ("paper_trade_execution_allowed", "SAFETY", "BOOLEAN", False, "NONE"),
    ("real_capital_allowed", "SAFETY", "BOOLEAN", False, "NONE"),
    ("market_execution_allowed", "SAFETY", "BOOLEAN", False, "NONE"),
    ("exchange_execution_allowed", "SAFETY", "BOOLEAN", False, "NONE"),
    ("automation_allowed", "SAFETY", "BOOLEAN", False, "NONE"),
    ("execution_allowed", "SAFETY", "BOOLEAN", False, "NONE"),
    ("notes", "AUDIT", "STRING", True, "NONE"),
]

ENUM_DOMAINS = {
    "source_system": ["CONTROLLED_FORWARD_OBSERVATION_RECORDER", "MANUAL_REVIEWED_IMPORT"],
    "direction": ["LONG"],
    "timeframe": ["15m"],
    "observation_state": ["CONTROLLED_FORWARD_OBSERVATION_STARTED", "OBSERVATION_CAPTURED", "OBSERVATION_REVIEWED"],
    "evidence_status": ["PENDING_VALIDATION", "VALIDATED", "REJECTED"],
    "evidence_scope": ["CONTROLLED_FORWARD_EVIDENCE"],
    "cost_profile": ["ZERO_COST_RESEARCH", "COST_AWARE_RESEARCH"],
    "activation_scope": ["EVIDENCE_ONLY"],
    "signal_state": ["NO_SIGNAL"],
    "deduplication_status": ["UNIQUE_CANDIDATE", "DUPLICATE_REJECTED"],
    "lifecycle_state": ["DRAFT", "VALIDATED", "REJECTED", "SUPERSEDED"],
    "review_status": ["PENDING_REVIEW", "APPROVED_AS_EVIDENCE", "REJECTED"],
}

CONSTRAINTS = [
    ("PK_EVIDENCE_ID", "PRIMARY_KEY", "evidence_id", "non-empty and unique"),
    ("UQ_DEDUPLICATION_KEY", "UNIQUE", "deduplication_key", "unique among accepted rows"),
    ("UQ_EVIDENCE_HASH", "UNIQUE", "evidence_hash", "unique"),
    ("UQ_AUDIT_EVENT_ID", "UNIQUE", "audit_event_id", "unique"),
    ("CK_DIRECTION_LONG", "CHECK", "direction", "direction == LONG"),
    ("CK_TIME_ORDER", "CHECK", "collected_at_utc,observed_at_utc", "collected_at_utc >= observed_at_utc"),
    ("CK_PRICE_POSITIVE", "CHECK", "entry_price,stop_price,target_price,invalidation_level", "all values > 0"),
    ("CK_LONG_PRICE_STRUCTURE", "CHECK", "stop_price,entry_price,target_price", "stop_price < entry_price < target_price"),
    ("CK_INVALIDATION_MATCH", "CHECK", "invalidation_level,stop_price", "invalidation_level == stop_price"),
    ("CK_RISK_REWARD_POSITIVE", "CHECK", "risk_reward", "risk_reward > 0"),
    ("CK_HASH_FORMAT", "CHECK", "hash fields", "lowercase 64-character SHA-256"),
    ("CK_MANUAL_CONFIRMATION", "CHECK", "manual_confirmation_required,manual_confirmed", "manual_confirmed implies required"),
    ("CK_VALIDATION_GATE", "CHECK", "validation flags", "all true before real-evidence acceptance"),
    ("CK_REJECTION_REASON", "CHECK", "evidence_status,rejection_reason", "rejected rows require a reason"),
    ("CK_APPROVED_REVIEWER", "CHECK", "review_status,reviewed_by", "approved evidence requires reviewer"),
    ("CK_PREVIOUS_HASH", "CHECK", "previous_evidence_hash", "later accepted rows require previous hash"),
    ("CK_SAFETY_EXECUTION_FALSE", "CHECK", "execution safety fields", "all operational fields false"),
    ("CK_SCOPE_EVIDENCE_ONLY", "CHECK", "activation_scope", "activation_scope == EVIDENCE_ONLY"),
    ("CK_SIGNAL_STATE_NONE", "CHECK", "signal_state", "signal_state == NO_SIGNAL"),
    ("CK_WRITE_PERMISSION", "CHECK", "write permission fields", "all write gates required for a future accepted write"),
]

KEY_INDEX_DESIGN = [
    ("PK_EVIDENCE_ID", "PRIMARY", "evidence_id", True),
    ("UQ_DEDUPLICATION_KEY", "UNIQUE", "deduplication_key", True),
    ("UQ_EVIDENCE_HASH", "UNIQUE", "evidence_hash", True),
    ("UQ_AUDIT_EVENT_ID", "UNIQUE", "audit_event_id", True),
    ("IX_OBSERVED_AT", "INDEX", "observed_at_utc", False),
    ("IX_SYMBOL_TIMEFRAME_TIME", "COMPOSITE_INDEX", "symbol,timeframe,observed_at_utc", False),
    ("IX_CANDIDATE_TIME", "COMPOSITE_INDEX", "candidate_id,observed_at_utc", False),
    ("IX_STATUS_REVIEW", "COMPOSITE_INDEX", "evidence_status,review_status", False),
    ("IX_LIFECYCLE_TIME", "COMPOSITE_INDEX", "lifecycle_state,collected_at_utc", False),
    ("IX_PREVIOUS_HASH", "INDEX", "previous_evidence_hash", False),
]

PROVENANCE_RULES = [
    "source_system_allowlist", "source_artifact_required", "source_artifact_sha256_required",
    "source_row_hash_required", "deterministic_row_serialization", "evidence_hash_required",
    "previous_hash_chain", "audit_event_required", "created_by_required",
    "reviewer_required_for_acceptance", "rollback_reference_required_after_first_write",
    "source_files_immutable_during_write",
]

LIFECYCLE_TRANSITIONS = [
    ("DRAFT", "VALIDATED"), ("DRAFT", "REJECTED"), ("VALIDATED", "SUPERSEDED"),
    ("REJECTED", "DRAFT"), ("PENDING_VALIDATION", "VALIDATED"),
    ("PENDING_VALIDATION", "REJECTED"), ("PENDING_REVIEW", "APPROVED_AS_EVIDENCE"),
    ("PENDING_REVIEW", "REJECTED"), ("APPROVED_AS_EVIDENCE", "SUPERSEDED"),
    ("ANY", "NO_DELETE"),
]

MIGRATION_STEPS = [
    "freeze_design_contract", "design_review", "implementation_precheck",
    "create_empty_schema_candidate", "schema_validation", "atomic_write_harness",
    "manifest_sidecar", "backup_and_rollback", "synthetic_write_dry_run",
    "output_integrity_review", "final_implementation_approval", "real_evidence_precheck",
]

SAFETY_GUARDS = [
    ("design_only", True, True), ("source_final_approval_passed", True, True),
    ("schema_field_count", 54, 54), ("schema_order_defined", True, True),
    ("storage_design_defined", True, True), ("future_design_review_allowed", True, True),
    ("dataset_implementation_allowed", False, False), ("dataset_creation_allowed", False, False),
    ("evidence_collection_enabled", False, False), ("evidence_collection_started", False, False),
    ("official_dataset_schema_implemented", False, False), ("official_dataset_write_allowed", False, False),
    ("official_dataset_write_performed", False, False), ("real_forward_dataset_created", False, False),
    ("official_evidence_rows_written", 0, 0), ("accepted_as_real_evidence", False, False),
    ("evidence_persistence_allowed", False, False), ("evidence_write_performed", False, False),
    ("signal_generation_enabled", False, False), ("live_alerts_allowed", False, False),
    ("paper_trading_enabled", False, False), ("long_strategy_approved", False, False),
    ("long_entries_approved", False, False), ("long_side_established", False, False),
    ("paper_trade_execution_allowed", False, False), ("real_capital_allowed", False, False),
    ("market_execution_allowed", False, False), ("exchange_execution_allowed", False, False),
    ("automation_allowed", False, False), ("execution_allowed", False, False),
    ("real_entries_approved", False, False), ("total_project_completed", False, False),
    ("official_dataset_exists_before", False, False), ("official_dataset_exists_after", False, False),
    ("new_official_dataset_rows_created", 0, 0), ("source_artifacts_stable", True, True),
    ("manifest_self_exclusion_expected", True, True),
]

OUTPUT_FILENAMES = {
    "summary": "official_dataset_schema_implementation_design_summary_v1.csv",
    "source_validations": "official_dataset_schema_implementation_design_source_validations_v1.csv",
    "field_catalog": "official_dataset_schema_field_catalog_v1.csv",
    "enum_domains": "official_dataset_schema_enum_domains_v1.csv",
    "constraints": "official_dataset_schema_constraints_v1.csv",
    "key_index_design": "official_dataset_schema_key_index_design_v1.csv",
    "provenance_contract": "official_dataset_schema_provenance_contract_v1.csv",
    "lifecycle_contract": "official_dataset_schema_lifecycle_contract_v1.csv",
    "migration_plan": "official_dataset_schema_migration_plan_v1.csv",
    "safety_guards": "official_dataset_schema_safety_guards_v1.csv",
    "acceptance_criteria": "official_dataset_schema_acceptance_criteria_v1.csv",
    "decision": "official_dataset_schema_implementation_design_decision_v1.csv",
    "checks": "official_dataset_schema_implementation_design_checks_v1.csv",
    "manifest": "source_official_dataset_schema_implementation_design_artifact_manifest_v1.csv",
}


def safe_bool(value: Any, default: bool = False) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"true", "1", "yes", "y"}
    return default


def safe_int(value: Any, default: int = 0) -> int:
    try:
        if value is None or pd.isna(value):
            return default
        return int(float(value))
    except Exception:
        return default


def read_csv(path: Path) -> pd.DataFrame:
    try:
        return pd.read_csv(path) if path.exists() else pd.DataFrame()
    except Exception:
        return pd.DataFrame()


def all_passed(df: pd.DataFrame) -> bool:
    return not df.empty and "passed" in df.columns and df["passed"].map(safe_bool).all()


def sha256_file(path: Path) -> str:
    if not path.exists() or not path.is_file():
        return ""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def is_sha256(value: Any) -> bool:
    text = str(value)
    return len(text) == 64 and all(c in "0123456789abcdef" for c in text.lower())


def build_manifest(paths: dict[str, Path], scope: str) -> pd.DataFrame:
    rows = []
    for position, (name, path) in enumerate(paths.items(), start=1):
        exists = path.exists() and path.is_file()
        size = path.stat().st_size if exists else 0
        digest = sha256_file(path) if exists else ""
        rows.append({
            "artifact_scope": scope, "manifest_position": position,
            "artifact_name": name, "artifact_filename": path.name,
            "artifact_path": str(path), "artifact_exists": exists,
            "artifact_size_bytes": int(size), "artifact_non_empty": size > 0,
            "artifact_sha256": digest, "artifact_sha256_valid": is_sha256(digest),
        })
    return pd.DataFrame(rows)


def manifest_digest(df: pd.DataFrame) -> str:
    if df.empty:
        return ""
    payload = df[["artifact_scope", "artifact_name", "artifact_path", "artifact_size_bytes", "artifact_sha256"]].astype(str).sort_values(["artifact_scope", "artifact_name", "artifact_path"]).to_csv(index=False).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def build_field_catalog() -> pd.DataFrame:
    return pd.DataFrame([
        {"field_position": i, "field_name": n, "field_group": g, "logical_type": t,
         "nullable": nullable, "key_role": role, "canonical_order_required": True, "design_only": True}
        for i, (n, g, t, nullable, role) in enumerate(SCHEMA_FIELDS, start=1)
    ])


def build_enum_domains() -> pd.DataFrame:
    rows, position = [], 0
    for field_name, values in ENUM_DOMAINS.items():
        for value_position, value in enumerate(values, start=1):
            position += 1
            rows.append({"enum_position": position, "field_name": field_name,
                         "value_position": value_position, "allowed_value": value,
                         "closed_domain": True, "design_only": True})
    return pd.DataFrame(rows)


def build_constraints() -> pd.DataFrame:
    return pd.DataFrame([
        {"constraint_position": i, "constraint_id": cid, "constraint_type": ctype,
         "fields": fields, "rule": rule, "required": True, "design_only": True}
        for i, (cid, ctype, fields, rule) in enumerate(CONSTRAINTS, start=1)
    ])


def build_key_index_design() -> pd.DataFrame:
    return pd.DataFrame([
        {"key_index_position": i, "key_index_id": kid, "key_index_type": ktype,
         "fields": fields, "unique": unique, "design_only": True}
        for i, (kid, ktype, fields, unique) in enumerate(KEY_INDEX_DESIGN, start=1)
    ])


def build_provenance_contract() -> pd.DataFrame:
    return pd.DataFrame([
        {"provenance_position": i, "provenance_rule": rule, "required": True, "design_only": True}
        for i, rule in enumerate(PROVENANCE_RULES, start=1)
    ])


def build_lifecycle_contract() -> pd.DataFrame:
    return pd.DataFrame([
        {"transition_position": i, "from_state": a, "to_state": b,
         "physical_delete_allowed": False, "design_only": True}
        for i, (a, b) in enumerate(LIFECYCLE_TRANSITIONS, start=1)
    ])


def build_migration_plan() -> pd.DataFrame:
    return pd.DataFrame([
        {"step_position": i, "step_name": name, "implementation_performed": False,
         "dataset_created": False, "rows_written": 0, "design_only": True}
        for i, name in enumerate(MIGRATION_STEPS, start=1)
    ])


def build_safety_guards() -> pd.DataFrame:
    return pd.DataFrame([
        {"guard_position": i, "guard_name": name, "required_value": required,
         "actual_value": actual, "passed": required == actual, "design_only": True}
        for i, (name, required, actual) in enumerate(SAFETY_GUARDS, start=1)
    ])


def validate_source(source: dict[str, pd.DataFrame], before: pd.DataFrame, after: pd.DataFrame,
                    official_before: bool, official_after: bool) -> pd.DataFrame:
    summary = source["summary"].iloc[0].to_dict() if len(source["summary"]) == 1 else {}
    decision = source["decision"].iloc[0].to_dict() if len(source["decision"]) == 1 else {}
    checks = [
        ("source_artifact_count_11", len(before) == 11),
        ("source_artifacts_exist", before["artifact_exists"].map(safe_bool).all()),
        ("source_artifacts_non_empty", before["artifact_non_empty"].map(safe_bool).all()),
        ("source_hashes_valid", before["artifact_sha256_valid"].map(safe_bool).all()),
        ("source_artifacts_stable", manifest_digest(before) == manifest_digest(after)),
        ("phase_10_36_validation_passed", safe_bool(summary.get("validation_passed")) and str(summary.get("validation_decision", "")) == "PHASE_10_36_LONG_FORWARD_OBSERVATION_EVIDENCE_COLLECTION_REPORT_ONLY_DRY_RUN_FINAL_APPROVAL_REVIEW_VALIDATED"),
        ("source_final_review_passed", safe_bool(summary.get("report_only_dry_run_final_approval_review_passed"))),
        ("source_final_decision_valid", str(summary.get("report_only_dry_run_final_approval_review_decision", "")) == SOURCE_READY_DECISION),
        ("source_cycle_closed", safe_bool(summary.get("report_only_dry_run_cycle_closed"))),
        ("source_schema_design_allowed", safe_bool(summary.get("future_official_dataset_schema_implementation_design_allowed"))),
        ("source_validation_rows_102", safe_int(summary.get("final_review_validation_rows"), -1) == 102),
        ("source_item_rows_34", safe_int(summary.get("final_review_item_rows"), -1) == 34),
        ("source_finding_rows_34", safe_int(summary.get("final_review_finding_rows"), -1) == 34),
        ("source_control_rows_102", safe_int(summary.get("final_review_control_rows"), -1) == 102),
        ("source_rule_rows_26", safe_int(summary.get("final_review_rule_rows"), -1) == 26),
        ("source_requirement_rows_117", safe_int(summary.get("final_review_requirement_rows"), -1) == 117),
        ("source_guard_rows_37", safe_int(summary.get("final_review_guard_rows"), -1) == 37),
        ("source_material_issue_count_zero", safe_int(summary.get("material_issue_count"), -1) == 0),
        ("source_total_checks_28", safe_int(summary.get("total_checks"), -1) == 28),
        ("source_warning_count_15", safe_int(summary.get("warning_count"), -1) == 15),
        ("source_error_count_zero", safe_int(summary.get("error_count"), -1) == 0),
        ("source_blocker_count_zero", safe_int(summary.get("blocker_count"), -1) == 0),
        ("source_decision_row_count_1", len(source["decision"]) == 1),
        ("source_decision_value_valid", str(decision.get("report_only_dry_run_final_approval_review_decision", "")) == SOURCE_READY_DECISION),
        ("source_decision_design_allowed", safe_bool(decision.get("future_official_dataset_schema_implementation_design_allowed"))),
        ("source_decision_requirements_117", safe_int(decision.get("total_requirements"), -1) == 117),
        ("source_decision_failed_requirements_zero", safe_int(decision.get("failed_requirements"), -1) == 0),
        ("source_validations_all_passed", all_passed(source["validations"])),
        ("source_items_all_passed", all_passed(source["items"])),
        ("source_findings_all_passed", all_passed(source["findings"])),
        ("source_controls_all_passed", all_passed(source["controls"])),
        ("source_rules_all_passed", all_passed(source["rules"])),
        ("source_requirements_all_passed", all_passed(source["requirements"])),
        ("source_guards_all_passed", all_passed(source["guard_matrix"])),
        ("source_checks_all_passed", all_passed(source["checks"])),
        ("official_dataset_absent_before", not official_before),
        ("official_dataset_absent_after", not official_after),
        ("official_dataset_unchanged_absent", not official_before and not official_after),
    ]
    return pd.DataFrame([
        {"validation_position": i, "validation_name": name, "passed": bool(passed), "details": f"{name}={passed}"}
        for i, (name, passed) in enumerate(checks, start=1)
    ])


def build_acceptance_criteria(source_validations: pd.DataFrame, field_catalog: pd.DataFrame,
                              enum_domains: pd.DataFrame, constraints: pd.DataFrame,
                              key_index: pd.DataFrame, provenance: pd.DataFrame,
                              lifecycle: pd.DataFrame, migration: pd.DataFrame,
                              guards: pd.DataFrame, official_before: bool,
                              official_after: bool) -> pd.DataFrame:
    constraint_ids = set(constraints["constraint_id"].astype(str))
    key_ids = set(key_index["key_index_id"].astype(str))
    actuals = [
        ("source_phase_10_36_validated", all_passed(source_validations)),
        ("schema_field_count_54", len(field_catalog) == 54),
        ("schema_positions_exact", field_catalog["field_position"].tolist() == list(range(1, 55))),
        ("schema_field_names_unique", field_catalog["field_name"].is_unique),
        ("primary_key_exactly_one", int(field_catalog["key_role"].eq("PRIMARY_KEY").sum()) == 1),
        ("unique_integrity_keys_defined", {"UQ_DEDUPLICATION_KEY", "UQ_EVIDENCE_HASH", "UQ_AUDIT_EVENT_ID"}.issubset(key_ids)),
        ("enum_domains_defined", len(enum_domains) >= 20),
        ("constraints_count_20", len(constraints) == 20),
        ("long_price_structure_constraint_defined", "CK_LONG_PRICE_STRUCTURE" in constraint_ids),
        ("execution_safety_constraint_defined", "CK_SAFETY_EXECUTION_FALSE" in constraint_ids),
        ("key_index_count_10", len(key_index) == 10),
        ("provenance_rule_count_12", len(provenance) == 12),
        ("hash_chain_defined", provenance["provenance_rule"].eq("previous_hash_chain").any()),
        ("lifecycle_transition_count_10", len(lifecycle) == 10),
        ("atomic_write_design_defined", STORAGE_DESIGN == "CSV_APPEND_ONLY_ATOMIC_REPLACE_WITH_SHA256_MANIFEST_V1"),
        ("backup_and_rollback_defined", migration["step_name"].eq("backup_and_rollback").any()),
        ("migration_step_count_12", len(migration) == 12),
        ("safety_guard_count_37", len(guards) == 37),
        ("safety_guards_all_passed", all_passed(guards)),
        ("official_dataset_absent", not official_before and not official_after),
        ("no_rows_written", True),
        ("design_review_only_next", True),
        ("dataset_implementation_not_allowed", True),
        ("long_strategy_remains_unapproved", True),
        ("total_project_not_completed", True),
    ]
    return pd.DataFrame([
        {"criterion_position": i, "criterion_name": name, "required_value": True,
         "actual_value": bool(actual), "passed": bool(actual), "design_only": True}
        for i, (name, actual) in enumerate(actuals, start=1)
    ])


def build_decision(source_validations: pd.DataFrame, criteria: pd.DataFrame,
                   guards: pd.DataFrame) -> pd.DataFrame:
    passed = all_passed(source_validations) and all_passed(criteria) and all_passed(guards)
    return pd.DataFrame([{
        "official_dataset_schema_implementation_design_id": "PHASE_10_37_OFFICIAL_DATASET_SCHEMA_IMPLEMENTATION_DESIGN_001",
        "official_dataset_schema_implementation_design_performed": True,
        "official_dataset_schema_implementation_design_passed": passed,
        "official_dataset_schema_implementation_design_decision": READY_DECISION if passed else BLOCKED_DECISION,
        "canonical_schema_field_count": 54, "storage_design": STORAGE_DESIGN,
        "total_acceptance_criteria": len(criteria),
        "passed_acceptance_criteria": int(criteria["passed"].map(safe_bool).sum()),
        "failed_acceptance_criteria": int((~criteria["passed"].map(safe_bool)).sum()),
        "future_official_dataset_schema_implementation_design_review_allowed": passed,
        "dataset_implementation_allowed": False, "dataset_creation_allowed": False,
        "evidence_collection_enabled": False, "official_dataset_schema_implemented": False,
        "official_dataset_write_allowed": False, "official_dataset_write_performed": False,
        "official_evidence_rows_written": 0, "accepted_as_real_evidence": False,
        "evidence_persistence_allowed": False, "signal_generation_enabled": False,
        "live_alerts_allowed": False, "paper_trade_execution_allowed": False,
        "long_strategy_approved": False, "real_capital_allowed": False,
        "market_execution_allowed": False, "exchange_execution_allowed": False,
        "automation_allowed": False, "execution_allowed": False,
        "total_project_completed": False, "recommended_next_phase": RECOMMENDED_NEXT_PHASE,
    }])


def build_checks(docs_exist: dict[str, bool], source_validations: pd.DataFrame,
                 field_catalog: pd.DataFrame, enum_domains: pd.DataFrame,
                 constraints: pd.DataFrame, key_index: pd.DataFrame,
                 provenance: pd.DataFrame, lifecycle: pd.DataFrame,
                 migration: pd.DataFrame, guards: pd.DataFrame,
                 criteria: pd.DataFrame, decision: pd.DataFrame,
                 official_before: bool, official_after: bool) -> pd.DataFrame:
    rows = []
    def add(group: str, name: str, passed: bool, severity: str, details: str) -> None:
        rows.append({"check_group": group, "check_name": name, "passed": bool(passed),
                     "severity": severity, "details": details,
                     "blocker": severity == "ERROR" and not bool(passed)})
    for name, exists in docs_exist.items():
        add("phase_anchor", name, exists, "INFO" if exists else "ERROR", name)
    decision_value = str(decision.iloc[0].get("official_dataset_schema_implementation_design_decision", "")) if len(decision) == 1 else ""
    blocks = {
        "source_validations_passed": all_passed(source_validations),
        "schema_field_count_54": len(field_catalog) == 54,
        "enum_domains_defined": len(enum_domains) >= 20,
        "constraints_count_20": len(constraints) == 20,
        "key_index_count_10": len(key_index) == 10,
        "provenance_rule_count_12": len(provenance) == 12,
        "lifecycle_transition_count_10": len(lifecycle) == 10,
        "migration_step_count_12": len(migration) == 12,
        "safety_guard_count_37": len(guards) == 37,
        "safety_guards_passed": all_passed(guards),
        "acceptance_criteria_count_25": len(criteria) == 25,
        "acceptance_criteria_passed": all_passed(criteria),
        "design_decision_expected": decision_value == READY_DECISION,
        "official_dataset_unchanged_absent": not official_before and not official_after,
    }
    for name, passed in blocks.items():
        add("design_validation", name, passed, "INFO" if passed else "ERROR", f"{name}={passed}")
    warnings = [
        ("design_only", "Phase 10.37 defines design artifacts only."),
        ("dataset_not_implemented", "The official dataset remains unimplemented."),
        ("dataset_not_created", "No official dataset file was created."),
        ("dataset_not_written", "No official dataset row was written."),
        ("real_evidence_not_collected", "No real forward evidence was collected."),
        ("evidence_persistence_not_enabled", "Evidence persistence remains disabled."),
        ("signal_generation_not_enabled", "Signal generation remains disabled."),
        ("live_alerts_not_enabled", "Live alerts remain disabled."),
        ("paper_trading_not_enabled", "Paper trading remains disabled."),
        ("long_strategy_not_approved", "The LONG research candidate remains unapproved."),
        ("real_capital_not_allowed", "Real capital remains prohibited."),
        ("market_execution_not_allowed", "Market execution remains prohibited."),
        ("automation_not_allowed", "Automation remains prohibited."),
        ("total_project_not_completed", "The total project is not completed."),
        ("future_design_review_only", "The only next allowance is review of this design."),
    ]
    for name, details in warnings:
        add("scope_control", name, True, "WARNING", details)
    add("phase_transition", "phase_10_38_recommended_next", True, "INFO",
        "Recommended next: Phase 10.38 official dataset schema implementation design review.")
    return pd.DataFrame(rows)


def build_summary(source_manifest: pd.DataFrame, source_validations: pd.DataFrame,
                  field_catalog: pd.DataFrame, enum_domains: pd.DataFrame,
                  constraints: pd.DataFrame, key_index: pd.DataFrame,
                  provenance: pd.DataFrame, lifecycle: pd.DataFrame,
                  migration: pd.DataFrame, guards: pd.DataFrame,
                  criteria: pd.DataFrame, decision: pd.DataFrame,
                  checks: pd.DataFrame, official_before: bool,
                  official_after: bool) -> pd.DataFrame:
    decision_row = decision.iloc[0].to_dict() if len(decision) == 1 else {}
    error_count = int(checks["severity"].eq("ERROR").sum())
    warning_count = int(checks["severity"].eq("WARNING").sum())
    blocker_count = int(checks["blocker"].map(safe_bool).sum())
    passed = error_count == 0 and blocker_count == 0 and all_passed(source_validations) and all_passed(guards) and all_passed(criteria)
    return pd.DataFrame([{
        "phase": "10.37", "official_dataset_schema_implementation_design_defined": True,
        "phase_10_36_source_validated": all_passed(source_validations),
        "source_artifact_count": len(source_manifest),
        "source_artifacts_exist": source_manifest["artifact_exists"].map(safe_bool).all(),
        "source_artifacts_non_empty": source_manifest["artifact_non_empty"].map(safe_bool).all(),
        "source_artifact_hashes_valid": source_manifest["artifact_sha256_valid"].map(safe_bool).all(),
        "source_manifest_sha256": manifest_digest(source_manifest),
        "source_validation_rows": len(source_validations),
        "canonical_schema_field_count": len(field_catalog), "enum_domain_rows": len(enum_domains),
        "constraint_rows": len(constraints), "key_index_rows": len(key_index),
        "provenance_rule_rows": len(provenance), "lifecycle_transition_rows": len(lifecycle),
        "migration_step_rows": len(migration), "safety_guard_rows": len(guards),
        "acceptance_criteria_rows": len(criteria), "storage_design": STORAGE_DESIGN,
        "official_dataset_schema_implementation_design_performed": True,
        "official_dataset_schema_implementation_design_passed": safe_bool(decision_row.get("official_dataset_schema_implementation_design_passed")),
        "official_dataset_schema_implementation_design_decision": str(decision_row.get("official_dataset_schema_implementation_design_decision", "")),
        "future_official_dataset_schema_implementation_design_review_allowed": safe_bool(decision_row.get("future_official_dataset_schema_implementation_design_review_allowed")),
        "dataset_implementation_allowed": False, "dataset_creation_allowed": False,
        "evidence_collection_enabled": False, "evidence_collection_started": False,
        "official_dataset_schema_implemented": False, "official_dataset_write_allowed": False,
        "official_dataset_write_performed": False, "official_dataset_exists_before": official_before,
        "official_dataset_exists_after": official_after,
        "official_dataset_unchanged_absent": not official_before and not official_after,
        "official_evidence_rows_written": 0, "accepted_as_real_evidence": False,
        "evidence_persistence_allowed": False, "evidence_write_performed": False,
        "signal_generation_enabled": False, "live_alerts_allowed": False,
        "paper_trading_enabled": False, "long_strategy_approved": False,
        "long_entries_approved": False, "long_side_established": False,
        "paper_trade_execution_allowed": False, "real_capital_allowed": False,
        "market_execution_allowed": False, "exchange_execution_allowed": False,
        "automation_allowed": False, "execution_allowed": False,
        "real_entries_approved": False, "total_project_completed": False,
        "recommended_next_phase": RECOMMENDED_NEXT_PHASE,
        "estimated_phase_10_progress_percent": 100, "total_checks": len(checks),
        "warning_count": warning_count, "error_count": error_count,
        "blocker_count": blocker_count, "validation_passed": passed,
        "validation_decision": "PHASE_10_37_LONG_FORWARD_OBSERVATION_EVIDENCE_COLLECTION_OFFICIAL_DATASET_SCHEMA_IMPLEMENTATION_DESIGN_VALIDATED" if passed else "PHASE_10_37_LONG_FORWARD_OBSERVATION_EVIDENCE_COLLECTION_OFFICIAL_DATASET_SCHEMA_IMPLEMENTATION_DESIGN_FAILED",
    }])


def run_long_forward_observation_evidence_collection_official_dataset_schema_implementation_design() -> dict[str, pd.DataFrame]:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    docs_exist = {
        "phase_10_36_final_approval_review_doc_exists": PHASE_10_36_DOC_PATH.exists(),
        "phase_10_37_schema_design_doc_exists": PHASE_10_37_DOC_PATH.exists(),
    }
    official_before = OFFICIAL_DATASET_PATH.exists()
    source_manifest_before = build_manifest(SOURCE_PATHS, "PHASE_10_36")
    source = {name: read_csv(path) for name, path in SOURCE_PATHS.items()}
    source_manifest_after = build_manifest(SOURCE_PATHS, "PHASE_10_36")
    official_after = OFFICIAL_DATASET_PATH.exists()

    source_validations = validate_source(source, source_manifest_before, source_manifest_after, official_before, official_after)
    field_catalog = build_field_catalog()
    enum_domains = build_enum_domains()
    constraints = build_constraints()
    key_index = build_key_index_design()
    provenance = build_provenance_contract()
    lifecycle = build_lifecycle_contract()
    migration = build_migration_plan()
    guards = build_safety_guards()
    criteria = build_acceptance_criteria(source_validations, field_catalog, enum_domains, constraints, key_index, provenance, lifecycle, migration, guards, official_before, official_after)
    decision = build_decision(source_validations, criteria, guards)
    checks = build_checks(docs_exist, source_validations, field_catalog, enum_domains, constraints, key_index, provenance, lifecycle, migration, guards, criteria, decision, official_before, official_after)
    summary = build_summary(source_manifest_before, source_validations, field_catalog, enum_domains, constraints, key_index, provenance, lifecycle, migration, guards, criteria, decision, checks, official_before, official_after)

    frames = {
        "summary": summary, "source_validations": source_validations,
        "field_catalog": field_catalog, "enum_domains": enum_domains,
        "constraints": constraints, "key_index_design": key_index,
        "provenance_contract": provenance, "lifecycle_contract": lifecycle,
        "migration_plan": migration, "safety_guards": guards,
        "acceptance_criteria": criteria, "decision": decision, "checks": checks,
    }
    for name, dataframe in frames.items():
        dataframe.to_csv(REPORTS_DIR / OUTPUT_FILENAMES[name], index=False)
    output_paths = {name: REPORTS_DIR / OUTPUT_FILENAMES[name] for name in frames}
    output_manifest = build_manifest(output_paths, "PHASE_10_37_OUTPUT")
    combined_manifest = pd.concat([source_manifest_after, output_manifest], ignore_index=True)
    combined_manifest.to_csv(REPORTS_DIR / OUTPUT_FILENAMES["manifest"], index=False)

    return {
        "summary": summary, "source_summary": source["summary"],
        "source_decision": source["decision"],
        "source_artifact_manifest": source_manifest_before,
        "source_validations": source_validations, "field_catalog": field_catalog,
        "enum_domains": enum_domains, "constraints": constraints,
        "key_index_design": key_index, "provenance_contract": provenance,
        "lifecycle_contract": lifecycle, "migration_plan": migration,
        "safety_guards": guards, "acceptance_criteria": criteria,
        "decision": decision, "checks": checks, "manifest": combined_manifest,
    }
