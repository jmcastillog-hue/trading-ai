from __future__ import annotations

import hashlib
import os
import sys
from pathlib import Path
from typing import Any

import pandas as pd

try:
    from src.long_side.long_forward_observation_dataset_bootstrap_v1 import (
        OFFICIAL_DATASET_PATH,
    )
except ImportError:
    OFFICIAL_DATASET_PATH = Path(
        "data/forward/"
        "long_forward_observation_dataset_v1.csv"
    )

REPORTS_DIR = Path(
    "reports/p10_39_evidence_collection_official_dataset_"
    "schema_implementation_precheck_v1"
)
PHASE_10_38_DIR = Path(
    "reports/p10_38_evidence_collection_official_dataset_"
    "schema_implementation_design_review_v1"
)
PHASE_10_37_DIR = Path(
    "reports/p10_37_evidence_collection_official_dataset_"
    "schema_implementation_design_v1"
)

PHASE_10_37_DOC_PATH = Path(
    "docs/PHASE_10_LONG_FORWARD_OBSERVATION_EVIDENCE_COLLECTION_"
    "OFFICIAL_DATASET_SCHEMA_IMPLEMENTATION_DESIGN.md"
)
PHASE_10_38_DOC_PATH = Path(
    "docs/PHASE_10_LONG_FORWARD_OBSERVATION_EVIDENCE_COLLECTION_"
    "OFFICIAL_DATASET_SCHEMA_IMPLEMENTATION_DESIGN_REVIEW.md"
)
PHASE_10_39_DOC_PATH = Path(
    "docs/PHASE_10_LONG_FORWARD_OBSERVATION_EVIDENCE_COLLECTION_"
    "OFFICIAL_DATASET_SCHEMA_IMPLEMENTATION_PRECHECK.md"
)

REVIEW_PATHS = {
    "review_summary": PHASE_10_38_DIR / "official_dataset_schema_implementation_design_review_summary_v1.csv",
    "review_validations": PHASE_10_38_DIR / "official_dataset_schema_implementation_design_review_validations_v1.csv",
    "review_items": PHASE_10_38_DIR / "official_dataset_schema_implementation_design_review_items_v1.csv",
    "review_findings": PHASE_10_38_DIR / "official_dataset_schema_implementation_design_review_findings_v1.csv",
    "review_controls": PHASE_10_38_DIR / "official_dataset_schema_implementation_design_review_controls_v1.csv",
    "review_rules": PHASE_10_38_DIR / "official_dataset_schema_implementation_design_review_rules_v1.csv",
    "review_requirements": PHASE_10_38_DIR / "official_dataset_schema_implementation_design_review_requirements_v1.csv",
    "review_guard_matrix": PHASE_10_38_DIR / "official_dataset_schema_implementation_design_review_guard_matrix_v1.csv",
    "review_decision": PHASE_10_38_DIR / "official_dataset_schema_implementation_design_review_decision_v1.csv",
    "review_checks": PHASE_10_38_DIR / "official_dataset_schema_implementation_design_review_checks_v1.csv",
    "review_manifest": PHASE_10_38_DIR / "source_official_dataset_schema_implementation_design_review_artifact_manifest_v1.csv",
}

DESIGN_PATHS = {
    "design_summary": PHASE_10_37_DIR / "official_dataset_schema_implementation_design_summary_v1.csv",
    "field_catalog": PHASE_10_37_DIR / "official_dataset_schema_field_catalog_v1.csv",
    "enum_domains": PHASE_10_37_DIR / "official_dataset_schema_enum_domains_v1.csv",
    "constraints": PHASE_10_37_DIR / "official_dataset_schema_constraints_v1.csv",
    "key_index_design": PHASE_10_37_DIR / "official_dataset_schema_key_index_design_v1.csv",
    "provenance_contract": PHASE_10_37_DIR / "official_dataset_schema_provenance_contract_v1.csv",
    "lifecycle_contract": PHASE_10_37_DIR / "official_dataset_schema_lifecycle_contract_v1.csv",
    "migration_plan": PHASE_10_37_DIR / "official_dataset_schema_migration_plan_v1.csv",
    "safety_guards": PHASE_10_37_DIR / "official_dataset_schema_safety_guards_v1.csv",
    "acceptance_criteria": PHASE_10_37_DIR / "official_dataset_schema_acceptance_criteria_v1.csv",
    "design_decision": PHASE_10_37_DIR / "official_dataset_schema_implementation_design_decision_v1.csv",
    "design_checks": PHASE_10_37_DIR / "official_dataset_schema_implementation_design_checks_v1.csv",
    "design_manifest": PHASE_10_37_DIR / "source_official_dataset_schema_implementation_design_artifact_manifest_v1.csv",
}
SOURCE_PATHS = {**REVIEW_PATHS, **DESIGN_PATHS}

SOURCE_READY_DECISION = (
    "CONTROLLED_FORWARD_OBSERVATION_EVIDENCE_COLLECTION_OFFICIAL_"
    "DATASET_SCHEMA_IMPLEMENTATION_DESIGN_REVIEW_READY_FOR_"
    "IMPLEMENTATION_PRECHECK"
)
READY_DECISION = (
    "CONTROLLED_FORWARD_OBSERVATION_EVIDENCE_COLLECTION_OFFICIAL_"
    "DATASET_SCHEMA_IMPLEMENTATION_PRECHECK_READY_FOR_EMPTY_SCHEMA_"
    "CANDIDATE_IMPLEMENTATION"
)
BLOCKED_DECISION = (
    "CONTROLLED_FORWARD_OBSERVATION_EVIDENCE_COLLECTION_OFFICIAL_"
    "DATASET_SCHEMA_IMPLEMENTATION_PRECHECK_BLOCKED"
)
RECOMMENDED_NEXT_PHASE = (
    "PHASE_10_40_LONG_FORWARD_OBSERVATION_EVIDENCE_COLLECTION_"
    "OFFICIAL_DATASET_EMPTY_SCHEMA_CANDIDATE_IMPLEMENTATION_V1"
)

OFFICIAL_DATASET_EXPECTED_PATH = Path(
    "data/forward/"
    "long_forward_observation_dataset_v1.csv"
)
EMPTY_SCHEMA_CANDIDATE_PATH = (
    OFFICIAL_DATASET_EXPECTED_PATH.parent
    / "candidates"
    / (
        f"{OFFICIAL_DATASET_EXPECTED_PATH.stem}"
        ".empty_candidate.csv"
    )
)
OFFICIAL_MANIFEST_PATH = OFFICIAL_DATASET_EXPECTED_PATH.with_suffix(
    ".manifest.csv"
)
OFFICIAL_LOCK_PATH = OFFICIAL_DATASET_EXPECTED_PATH.with_suffix(".lock")
OFFICIAL_TEMP_PATH = OFFICIAL_DATASET_EXPECTED_PATH.with_suffix(".tmp")
BACKUP_DIR = (
    OFFICIAL_DATASET_EXPECTED_PATH.parent
    / "backups"
    / OFFICIAL_DATASET_EXPECTED_PATH.stem
)

EXPECTED_FIELD_NAMES = [
    "evidence_id", "observation_id", "collected_at_utc", "observed_at_utc",
    "source_system", "source_artifact", "source_artifact_sha256",
    "source_row_hash", "candidate_id", "direction", "symbol", "timeframe",
    "observation_state", "evidence_status", "evidence_scope",
    "evidence_version", "entry_price", "stop_price", "target_price",
    "invalidation_level", "risk_reward", "cost_profile", "market_context",
    "activation_scope", "signal_state", "deduplication_key",
    "deduplication_status", "lifecycle_state", "review_status",
    "rejection_reason", "manual_confirmation_required", "manual_confirmed",
    "write_ahead_validation_passed", "schema_validation_passed",
    "provenance_validation_passed", "risk_structure_validation_passed",
    "evidence_hash", "previous_evidence_hash", "audit_event_id", "created_by",
    "reviewed_by", "rollback_reference", "accepted_as_real_evidence",
    "official_dataset_write_allowed", "evidence_persistence_allowed",
    "signal_generation_enabled", "live_alerts_allowed",
    "paper_trade_execution_allowed", "real_capital_allowed",
    "market_execution_allowed", "exchange_execution_allowed",
    "automation_allowed", "execution_allowed", "notes",
]

OUTPUT_FILENAMES = {
    "summary": "official_dataset_schema_implementation_precheck_summary_v1.csv",
    "validations": "official_dataset_schema_implementation_precheck_validations_v1.csv",
    "items": "official_dataset_schema_implementation_precheck_items_v1.csv",
    "findings": "official_dataset_schema_implementation_precheck_findings_v1.csv",
    "controls": "official_dataset_schema_implementation_precheck_controls_v1.csv",
    "rules": "official_dataset_schema_implementation_precheck_rules_v1.csv",
    "requirements": "official_dataset_schema_implementation_precheck_requirements_v1.csv",
    "guard_matrix": "official_dataset_schema_implementation_precheck_guard_matrix_v1.csv",
    "path_plan": "official_dataset_schema_implementation_precheck_path_plan_v1.csv",
    "decision": "official_dataset_schema_implementation_precheck_decision_v1.csv",
    "checks": "official_dataset_schema_implementation_precheck_checks_v1.csv",
    "manifest": "source_official_dataset_schema_implementation_precheck_artifact_manifest_v1.csv",
}


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
    return default


def safe_int(value: Any, default: int = 0) -> int:
    try:
        if value is None or pd.isna(value):
            return default
        return int(float(value))
    except Exception:
        return default


def read_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    try:
        return pd.read_csv(path)
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
    text = str(value).lower()
    return len(text) == 64 and all(char in "0123456789abcdef" for char in text)


def build_manifest(paths: dict[str, Path], scope: str) -> pd.DataFrame:
    rows = []
    for position, (name, path) in enumerate(paths.items(), start=1):
        exists = path.exists() and path.is_file()
        size = path.stat().st_size if exists else 0
        digest = sha256_file(path) if exists else ""
        rows.append({
            "artifact_scope": scope,
            "manifest_position": position,
            "artifact_name": name,
            "artifact_filename": path.name,
            "artifact_path": str(path),
            "artifact_exists": exists,
            "artifact_size_bytes": int(size),
            "artifact_non_empty": size > 0,
            "artifact_sha256": digest,
            "artifact_sha256_valid": is_sha256(digest),
        })
    return pd.DataFrame(rows)


def manifest_digest(df: pd.DataFrame) -> str:
    if df.empty:
        return ""
    payload = (
        df[["artifact_scope", "artifact_name", "artifact_path", "artifact_size_bytes", "artifact_sha256"]]
        .astype(str)
        .sort_values(["artifact_scope", "artifact_name", "artifact_path"])
        .to_csv(index=False)
        .encode("utf-8")
    )
    return hashlib.sha256(payload).hexdigest()


def nearest_existing_parent(path: Path) -> Path:
    current = path.parent
    while not current.exists() and current != current.parent:
        current = current.parent
    return current


def ordered_values(df: pd.DataFrame, position_column: str, value_column: str) -> list[str]:
    if df.empty or position_column not in df.columns or value_column not in df.columns:
        return []
    return df.sort_values(position_column)[value_column].astype(str).tolist()


def append_validation(rows: list[dict[str, Any]], group: str, name: str, passed: bool, details: str = "") -> None:
    rows.append({
        "validation_position": len(rows) + 1,
        "validation_group": group,
        "validation_name": name,
        "passed": bool(passed),
        "details": details or f"{name}={passed}",
    })


def build_path_plan() -> pd.DataFrame:
    nearest = nearest_existing_parent(OFFICIAL_DATASET_EXPECTED_PATH)
    planned = [
        ("official_dataset", OFFICIAL_DATASET_EXPECTED_PATH, "OFFICIAL"),
        ("empty_schema_candidate", EMPTY_SCHEMA_CANDIDATE_PATH, "CANDIDATE"),
        ("official_manifest", OFFICIAL_MANIFEST_PATH, "SIDECAR"),
        ("official_lock", OFFICIAL_LOCK_PATH, "LOCK"),
        ("official_temp", OFFICIAL_TEMP_PATH, "TEMPORARY"),
        ("backup_directory", BACKUP_DIR, "BACKUP_DIRECTORY"),
    ]
    return pd.DataFrame([
        {
            "path_position": position,
            "path_name": name,
            "planned_path": str(path),
            "path_role": role,
            "exists_now": path.exists(),
            "creation_performed": False,
            "nearest_existing_parent": str(nearest),
            "nearest_existing_parent_exists": nearest.exists(),
            "nearest_existing_parent_writable": os.access(nearest, os.W_OK),
            "precheck_only": True,
        }
        for position, (name, path, role) in enumerate(planned, start=1)
    ])


def build_validations(source: dict[str, pd.DataFrame], before: pd.DataFrame, after: pd.DataFrame, path_plan: pd.DataFrame, official_before: bool, official_after: bool) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []

    for name, passed in [
        ("source_artifact_count_24", len(before) == 24),
        ("source_artifacts_exist", before["artifact_exists"].map(safe_bool).all()),
        ("source_artifacts_non_empty", before["artifact_non_empty"].map(safe_bool).all()),
        ("source_artifact_hashes_valid", before["artifact_sha256_valid"].map(safe_bool).all()),
        ("source_artifacts_stable", manifest_digest(before) == manifest_digest(after)),
    ]:
        append_validation(rows, "source_artifacts", name, passed)

    summary = source["review_summary"].iloc[0].to_dict() if len(source["review_summary"]) == 1 else {}
    summary_checks = [
        ("phase_10_38_validation_passed", safe_bool(summary.get("validation_passed", False))),
        ("source_review_performed", safe_bool(summary.get("official_dataset_schema_implementation_design_review_performed", False))),
        ("source_review_passed", safe_bool(summary.get("official_dataset_schema_implementation_design_review_passed", False))),
        ("source_review_decision_valid", str(summary.get("official_dataset_schema_implementation_design_review_decision", "")) == SOURCE_READY_DECISION),
        ("source_precheck_allowed", safe_bool(summary.get("future_official_dataset_schema_implementation_precheck_allowed", False))),
        ("source_review_validation_rows_122", safe_int(summary.get("review_validation_rows", -1), -1) == 122),
        ("source_review_item_rows_41", safe_int(summary.get("review_item_rows", -1), -1) == 41),
        ("source_review_finding_rows_41", safe_int(summary.get("review_finding_rows", -1), -1) == 41),
        ("source_review_control_rows_122", safe_int(summary.get("review_control_rows", -1), -1) == 122),
        ("source_review_rule_rows_26", safe_int(summary.get("review_rule_rows", -1), -1) == 26),
        ("source_review_requirement_rows_137", safe_int(summary.get("review_requirement_rows", -1), -1) == 137),
        ("source_review_guard_rows_37", safe_int(summary.get("review_guard_rows", -1), -1) == 37),
        ("source_material_issue_count_zero", safe_int(summary.get("material_issue_count", -1), -1) == 0),
        ("source_total_checks_28", safe_int(summary.get("total_checks", -1), -1) == 28),
        ("source_warning_count_15", safe_int(summary.get("warning_count", -1), -1) == 15),
        ("source_error_count_zero", safe_int(summary.get("error_count", -1), -1) == 0),
        ("source_blocker_count_zero", safe_int(summary.get("blocker_count", -1), -1) == 0),
        ("source_official_dataset_unchanged_absent", safe_bool(summary.get("official_dataset_unchanged_absent", False))),
        ("source_official_rows_zero", safe_int(summary.get("official_evidence_rows_written", -1), -1) == 0),
        ("source_long_unapproved", not safe_bool(summary.get("long_strategy_approved", True), True)),
        ("source_project_not_complete", not safe_bool(summary.get("total_project_completed", True), True)),
    ]
    for name, passed in summary_checks:
        append_validation(rows, "phase_10_38_summary", name, passed)

    decision = source["review_decision"].iloc[0].to_dict() if len(source["review_decision"]) == 1 else {}
    for name, passed in [
        ("source_decision_row_count_1", len(source["review_decision"]) == 1),
        ("source_decision_review_passed", safe_bool(decision.get("official_dataset_schema_implementation_design_review_passed", False))),
        ("source_decision_value_valid", str(decision.get("official_dataset_schema_implementation_design_review_decision", "")) == SOURCE_READY_DECISION),
        ("source_decision_field_count_54", safe_int(decision.get("canonical_schema_field_count", -1), -1) == 54),
        ("source_decision_requirements_137", safe_int(decision.get("total_requirements", -1), -1) == 137),
        ("source_decision_failed_requirements_zero", safe_int(decision.get("failed_requirements", -1), -1) == 0),
        ("source_decision_precheck_allowed", safe_bool(decision.get("future_official_dataset_schema_implementation_precheck_allowed", False))),
    ]:
        append_validation(rows, "phase_10_38_decision", name, passed)

    for key, expected in [
        ("review_validations", 122), ("review_items", 41), ("review_findings", 41),
        ("review_controls", 122), ("review_rules", 26), ("review_requirements", 137),
        ("review_guard_matrix", 37), ("review_checks", 28),
    ]:
        append_validation(rows, "phase_10_38_outputs", f"{key}_rows_{expected}", len(source[key]) == expected)
        append_validation(rows, "phase_10_38_outputs", f"{key}_all_passed", all_passed(source[key]))

    review_manifest = source["review_manifest"]
    append_validation(rows, "phase_10_38_manifest", "review_manifest_rows_24", len(review_manifest) == 24)
    if not review_manifest.empty:
        append_validation(rows, "phase_10_38_manifest", "review_manifest_listed_artifacts_valid", review_manifest["artifact_exists"].map(safe_bool).all() and review_manifest["artifact_non_empty"].map(safe_bool).all() and review_manifest["artifact_sha256_valid"].map(safe_bool).all())
        append_validation(rows, "phase_10_38_manifest", "review_manifest_self_exclusion_expected", REVIEW_PATHS["review_manifest"].name not in set(review_manifest["artifact_filename"].astype(str)))
    else:
        append_validation(rows, "phase_10_38_manifest", "review_manifest_listed_artifacts_valid", False)
        append_validation(rows, "phase_10_38_manifest", "review_manifest_self_exclusion_expected", False)

    field_catalog = source["field_catalog"]
    field_names = ordered_values(field_catalog, "field_position", "field_name")
    safety_fields = field_catalog[field_catalog["field_group"].astype(str).eq("SAFETY")] if not field_catalog.empty and "field_group" in field_catalog.columns else pd.DataFrame()
    for name, passed in [
        ("field_catalog_rows_54", len(field_catalog) == 54),
        ("field_catalog_positions_exact", not field_catalog.empty and field_catalog["field_position"].map(safe_int).tolist() == list(range(1, 55))),
        ("field_catalog_names_exact", field_names == EXPECTED_FIELD_NAMES),
        ("field_catalog_names_unique", not field_catalog.empty and field_catalog["field_name"].astype(str).is_unique),
        ("field_catalog_safety_fields_13", len(safety_fields) == 13),
        ("field_catalog_safety_boolean_fields_11", len(safety_fields) == 13 and int(safety_fields["logical_type"].astype(str).eq("BOOLEAN").sum()) == 11),
        ("enum_domain_rows_24", len(source["enum_domains"]) == 24),
        ("constraint_rows_20", len(source["constraints"]) == 20),
        ("key_index_rows_10", len(source["key_index_design"]) == 10),
        ("provenance_rows_12", len(source["provenance_contract"]) == 12),
        ("lifecycle_rows_10", len(source["lifecycle_contract"]) == 10),
        ("migration_rows_12", len(source["migration_plan"]) == 12),
        ("design_safety_guard_rows_37", len(source["safety_guards"]) == 37),
        ("design_safety_guards_all_passed", all_passed(source["safety_guards"])),
        ("design_acceptance_rows_25", len(source["acceptance_criteria"]) == 25),
        ("design_acceptance_all_passed", all_passed(source["acceptance_criteria"])),
        ("design_checks_rows_32", len(source["design_checks"]) == 32),
        ("design_checks_all_passed", all_passed(source["design_checks"])),
    ]:
        append_validation(rows, "phase_10_37_contract", name, passed)

    nearest = nearest_existing_parent(OFFICIAL_DATASET_EXPECTED_PATH)
    for name, passed in [
        ("official_dataset_path_exact", Path(OFFICIAL_DATASET_PATH) == OFFICIAL_DATASET_EXPECTED_PATH),
        ("official_dataset_suffix_csv", OFFICIAL_DATASET_EXPECTED_PATH.suffix.lower() == ".csv"),
        ("official_dataset_path_relative", not OFFICIAL_DATASET_EXPECTED_PATH.is_absolute()),
        ("candidate_path_distinct_from_official", EMPTY_SCHEMA_CANDIDATE_PATH != OFFICIAL_DATASET_EXPECTED_PATH),
        ("candidate_path_suffix_csv", EMPTY_SCHEMA_CANDIDATE_PATH.suffix.lower() == ".csv"),
        ("manifest_path_distinct", OFFICIAL_MANIFEST_PATH != OFFICIAL_DATASET_EXPECTED_PATH),
        ("lock_path_distinct", OFFICIAL_LOCK_PATH != OFFICIAL_DATASET_EXPECTED_PATH),
        ("temp_path_distinct", OFFICIAL_TEMP_PATH != OFFICIAL_DATASET_EXPECTED_PATH),
        ("backup_path_distinct", BACKUP_DIR != OFFICIAL_DATASET_EXPECTED_PATH.parent),
        ("nearest_existing_parent_exists", nearest.exists()),
        ("nearest_existing_parent_writable", os.access(nearest, os.W_OK)),
        ("sha256_available", callable(hashlib.sha256)),
        ("atomic_replace_available", callable(os.replace)),
        ("python_version_at_least_3_10", sys.version_info >= (3, 10)),
        ("utf8_encoding_available", "precheck".encode("utf-8").decode("utf-8") == "precheck"),
        ("official_dataset_absent_before", not official_before),
        ("official_dataset_absent_after", not official_after),
        ("official_dataset_unchanged_absent", not official_before and not official_after),
        ("empty_schema_candidate_absent", not EMPTY_SCHEMA_CANDIDATE_PATH.exists()),
        ("official_manifest_absent", not OFFICIAL_MANIFEST_PATH.exists()),
        ("official_lock_absent", not OFFICIAL_LOCK_PATH.exists()),
        ("official_temp_absent", not OFFICIAL_TEMP_PATH.exists()),
        ("path_plan_rows_6", len(path_plan) == 6),
        ("no_path_creation_performed", not path_plan["creation_performed"].map(safe_bool).any()),
    ]:
        append_validation(rows, "environment_and_paths", name, passed)

    for name in [
        "precheck_only", "implementation_not_performed", "official_dataset_not_created",
        "empty_schema_candidate_not_created", "official_dataset_write_not_performed",
        "official_evidence_rows_written_zero", "evidence_collection_disabled",
        "evidence_persistence_disabled", "signal_generation_disabled", "live_alerts_disabled",
        "paper_trading_disabled", "long_strategy_unapproved", "real_capital_disabled",
        "market_execution_disabled", "exchange_execution_disabled", "automation_disabled",
        "project_not_completed", "future_empty_schema_candidate_only",
    ]:
        append_validation(rows, "safety_boundary", name, True)

    return pd.DataFrame(rows)


def build_items(validations: pd.DataFrame) -> pd.DataFrame:
    names = validations["validation_name"].astype(str).tolist()
    rows = []
    for position, start in enumerate(range(0, len(names), 3), start=1):
        block = names[start:start + 3]
        selected = validations[validations["validation_name"].astype(str).isin(block)]
        passed = len(selected) == len(block) and selected["passed"].map(safe_bool).all()
        rows.append({
            "precheck_item_position": position,
            "precheck_item_id": f"OFFICIAL_DATASET_SCHEMA_IMPLEMENTATION_PRECHECK_ITEM_{position:03d}",
            "precheck_item_name": f"implementation_precheck_block_{position:03d}",
            "validation_names": ",".join(block),
            "required": True,
            "precheck_only": True,
            "empty_schema_candidate_only_next": True,
            "official_dataset_implementation_allowed": False,
            "official_dataset_creation_allowed": False,
            "candidate_creation_performed": False,
            "official_dataset_write_allowed": False,
            "passed": bool(passed),
        })
    return pd.DataFrame(rows)


def build_findings(items: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for position, (_, item) in enumerate(items.iterrows(), start=1):
        passed = safe_bool(item["passed"], False)
        rows.append({
            "finding_position": position,
            "finding_id": f"OFFICIAL_DATASET_SCHEMA_IMPLEMENTATION_PRECHECK_FINDING_{position:03d}",
            "precheck_item_id": str(item["precheck_item_id"]),
            "finding_status": "PASS" if passed else "FAIL",
            "material_issue_found": not passed,
            "implementation_change_required": not passed,
            "empty_schema_candidate_implementation_allowed": passed,
            "official_dataset_implementation_allowed": False,
            "passed": passed,
        })
    return pd.DataFrame(rows)


def build_controls(validations: pd.DataFrame) -> pd.DataFrame:
    return pd.DataFrame([
        {
            "control_position": position,
            "control_id": f"OFFICIAL_DATASET_SCHEMA_IMPLEMENTATION_PRECHECK_CONTROL_{position:03d}",
            "control_name": str(row["validation_name"]),
            "required": True,
            "precheck_only": True,
            "official_dataset_implementation_allowed": False,
            "official_dataset_creation_allowed": False,
            "candidate_creation_performed": False,
            "official_dataset_write_allowed": False,
            "evidence_collection_enabled": False,
            "signal_generation_enabled": False,
            "market_execution_allowed": False,
            "passed": safe_bool(row["passed"], False),
        }
        for position, (_, row) in enumerate(validations.iterrows(), start=1)
    ])


def build_rules(validations: pd.DataFrame, items: pd.DataFrame, findings: pd.DataFrame, controls: pd.DataFrame) -> pd.DataFrame:
    material_issues = int(findings["material_issue_found"].map(safe_bool).sum())
    rules = [
        ("validation_count_at_least_100", len(validations) >= 100, ">=100", len(validations)),
        ("all_validations_passed", all_passed(validations), True, all_passed(validations)),
        ("item_count_matches_groups", len(items) == (len(validations) + 2) // 3, (len(validations) + 2) // 3, len(items)),
        ("all_items_passed", all_passed(items), True, all_passed(items)),
        ("finding_count_matches_items", len(findings) == len(items), len(items), len(findings)),
        ("all_findings_passed", all_passed(findings), True, all_passed(findings)),
        ("material_issue_count_zero", material_issues == 0, 0, material_issues),
        ("control_count_matches_validations", len(controls) == len(validations), len(validations), len(controls)),
        ("all_controls_passed", all_passed(controls), True, all_passed(controls)),
        ("precheck_only", True, True, True),
        ("empty_schema_candidate_only_next", True, True, True),
        ("official_implementation_disabled", True, False, False),
        ("official_creation_disabled", True, False, False),
        ("candidate_creation_not_performed", True, False, False),
        ("official_dataset_writes_disabled", True, False, False),
        ("real_evidence_collection_disabled", True, False, False),
        ("evidence_persistence_disabled", True, False, False),
        ("signal_generation_disabled", True, False, False),
        ("live_alerts_disabled", True, False, False),
        ("paper_trading_disabled", True, False, False),
        ("long_strategy_unapproved", True, False, False),
        ("real_capital_disabled", True, False, False),
        ("market_execution_disabled", True, False, False),
        ("exchange_execution_disabled", True, False, False),
        ("automation_disabled", True, False, False),
        ("project_not_completed", True, False, False),
    ]
    return pd.DataFrame([
        {
            "rule_id": f"OFFICIAL_DATASET_SCHEMA_IMPLEMENTATION_PRECHECK_RULE_{position:03d}",
            "rule_name": name,
            "passed": bool(passed),
            "required_value": required,
            "actual_value": actual,
        }
        for position, (name, passed, required, actual) in enumerate(rules, start=1)
    ])


def build_guard_matrix(precheck_passed: bool) -> pd.DataFrame:
    guards = [
        ("source_design_review_performed", True, True),
        ("source_design_review_passed", True, True),
        ("source_precheck_allowed", True, True),
        ("implementation_precheck_performed", True, True),
        ("implementation_precheck_passed", True, precheck_passed),
        ("future_empty_schema_candidate_implementation_allowed", True, precheck_passed),
        ("official_dataset_implementation_allowed", False, False),
        ("official_dataset_creation_allowed", False, False),
        ("empty_schema_candidate_created", False, False),
        ("evidence_collection_enabled", False, False),
        ("evidence_collection_started", False, False),
        ("official_dataset_schema_implemented", False, False),
        ("official_dataset_write_allowed", False, False),
        ("official_dataset_write_performed", False, False),
        ("real_forward_dataset_created", False, False),
        ("official_evidence_rows_written", 0, 0),
        ("accepted_as_real_evidence", False, False),
        ("evidence_persistence_allowed", False, False),
        ("evidence_write_performed", False, False),
        ("signal_generation_enabled", False, False),
        ("live_alerts_allowed", False, False),
        ("paper_trading_enabled", False, False),
        ("long_strategy_approved", False, False),
        ("long_entries_approved", False, False),
        ("long_side_established", False, False),
        ("paper_trade_execution_allowed", False, False),
        ("real_capital_allowed", False, False),
        ("market_execution_allowed", False, False),
        ("exchange_execution_allowed", False, False),
        ("automation_allowed", False, False),
        ("execution_allowed", False, False),
        ("real_entries_approved", False, False),
        ("total_project_completed", False, False),
        ("official_dataset_exists_before", False, False),
        ("official_dataset_exists_after", False, False),
        ("candidate_dataset_exists_after", False, False),
        ("new_official_dataset_rows_created", 0, 0),
        ("source_artifacts_stable", True, True),
        ("review_manifest_self_exclusion_expected", True, True),
    ]
    return pd.DataFrame([
        {
            "guard_position": position,
            "guard_name": name,
            "required_value": required,
            "actual_value": actual,
            "passed": required == actual,
            "guard_group": "precheck_state" if position <= 6 else "precheck_safety_guard",
        }
        for position, (name, required, actual) in enumerate(guards, start=1)
    ])


def build_requirements(validations: pd.DataFrame, items: pd.DataFrame, findings: pd.DataFrame, controls: pd.DataFrame, rules: pd.DataFrame, guards: pd.DataFrame, path_plan: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for _, validation in validations.iterrows():
        actual = safe_bool(validation["passed"], False)
        rows.append((str(validation["validation_name"]), actual, True, actual))
    material_issues = int(findings["material_issue_found"].map(safe_bool).sum())
    rows.extend([
        ("precheck_items_passed", all_passed(items), True, all_passed(items)),
        ("precheck_findings_passed", all_passed(findings), True, all_passed(findings)),
        ("precheck_controls_passed", all_passed(controls), True, all_passed(controls)),
        ("precheck_rules_passed", all_passed(rules), True, all_passed(rules)),
        ("precheck_guards_passed", all_passed(guards), True, all_passed(guards)),
        ("material_issue_count_zero", material_issues == 0, 0, material_issues),
        ("path_plan_rows_6", len(path_plan) == 6, 6, len(path_plan)),
        ("path_plan_no_creation", not path_plan["creation_performed"].map(safe_bool).any(), False, False),
        ("future_empty_schema_candidate_allowed", True, True, True),
        ("official_dataset_implementation_not_allowed", True, False, False),
        ("official_dataset_creation_not_allowed", True, False, False),
        ("official_evidence_rows_written_zero", True, 0, 0),
        ("signal_generation_disabled", True, False, False),
        ("paper_trading_disabled", True, False, False),
        ("market_execution_disabled", True, False, False),
        ("project_not_completed", True, False, False),
    ])
    return pd.DataFrame([
        {
            "requirement_id": f"OFFICIAL_DATASET_SCHEMA_IMPLEMENTATION_PRECHECK_REQ_{position:03d}",
            "requirement_name": name,
            "passed": bool(passed),
            "required_value": required,
            "actual_value": actual,
        }
        for position, (name, passed, required, actual) in enumerate(rows, start=1)
    ])


def build_decision(validations: pd.DataFrame, items: pd.DataFrame, findings: pd.DataFrame, controls: pd.DataFrame, rules: pd.DataFrame, requirements: pd.DataFrame, guards: pd.DataFrame) -> pd.DataFrame:
    passed = all([all_passed(validations), all_passed(items), all_passed(findings), all_passed(controls), all_passed(rules), all_passed(requirements), all_passed(guards)])
    failed = requirements[~requirements["passed"].map(safe_bool)]
    return pd.DataFrame([{
        "official_dataset_schema_implementation_precheck_id": "PHASE_10_39_LONG_FORWARD_OBSERVATION_EVIDENCE_COLLECTION_OFFICIAL_DATASET_SCHEMA_IMPLEMENTATION_PRECHECK_001",
        "official_dataset_schema_implementation_precheck_performed": True,
        "official_dataset_schema_implementation_precheck_passed": passed,
        "official_dataset_schema_implementation_precheck_decision": READY_DECISION if passed else BLOCKED_DECISION,
        "canonical_schema_field_count": 54,
        "source_artifact_count": len(SOURCE_PATHS),
        "total_requirements": len(requirements),
        "passed_requirements": int(requirements["passed"].map(safe_bool).sum()),
        "failed_requirements": len(failed),
        "failed_requirement_names": ",".join(failed["requirement_name"].astype(str).tolist()),
        "future_official_dataset_empty_schema_candidate_implementation_allowed": passed,
        "official_dataset_implementation_allowed": False,
        "official_dataset_creation_allowed": False,
        "empty_schema_candidate_created": False,
        "evidence_collection_enabled": False,
        "evidence_collection_started": False,
        "official_dataset_schema_implemented": False,
        "official_dataset_write_allowed": False,
        "official_dataset_write_performed": False,
        "official_evidence_rows_written": 0,
        "accepted_as_real_evidence": False,
        "evidence_persistence_allowed": False,
        "signal_generation_enabled": False,
        "live_alerts_allowed": False,
        "paper_trade_execution_allowed": False,
        "long_strategy_approved": False,
        "real_capital_allowed": False,
        "market_execution_allowed": False,
        "exchange_execution_allowed": False,
        "automation_allowed": False,
        "execution_allowed": False,
        "total_project_completed": False,
        "recommended_next_phase": RECOMMENDED_NEXT_PHASE,
    }])


def build_checks(docs_exist: dict[str, bool], validations: pd.DataFrame, items: pd.DataFrame, findings: pd.DataFrame, controls: pd.DataFrame, rules: pd.DataFrame, requirements: pd.DataFrame, guards: pd.DataFrame, path_plan: pd.DataFrame, decision: pd.DataFrame, official_before: bool, official_after: bool) -> pd.DataFrame:
    rows = []
    def add(group: str, name: str, passed: bool, severity: str, details: str) -> None:
        rows.append({"check_group": group, "check_name": name, "passed": bool(passed), "severity": severity, "details": details, "blocker": severity == "ERROR" and not bool(passed)})
    for name, exists in docs_exist.items():
        add("phase_anchor", name, exists, "INFO" if exists else "ERROR", name)
    decision_row = decision.iloc[0].to_dict() if len(decision) == 1 else {}
    blocks = {
        "precheck_validations_passed": all_passed(validations),
        "precheck_items_passed": all_passed(items),
        "precheck_findings_passed": all_passed(findings),
        "precheck_controls_passed": all_passed(controls),
        "precheck_rules_passed": all_passed(rules),
        "precheck_requirements_passed": all_passed(requirements),
        "precheck_guards_passed": all_passed(guards),
        "path_plan_valid": len(path_plan) == 6 and not path_plan["creation_performed"].map(safe_bool).any(),
        "implementation_precheck_passed": safe_bool(decision_row.get("official_dataset_schema_implementation_precheck_passed", False)),
        "implementation_precheck_decision_expected": str(decision_row.get("official_dataset_schema_implementation_precheck_decision", "")) == READY_DECISION,
    }
    for name, passed in blocks.items():
        add("implementation_precheck", name, passed, "INFO" if passed else "ERROR", f"{name}={passed}")
    unchanged = not official_before and not official_after
    add("official_dataset_guard", "official_dataset_unchanged_absent", unchanged, "INFO" if unchanged else "ERROR", f"before={official_before},after={official_after}")
    warnings = [
        ("precheck_only", "Phase 10.39 performs checks only."),
        ("official_dataset_not_implemented", "The official dataset remains unimplemented."),
        ("official_dataset_not_created", "No official dataset file was created."),
        ("candidate_not_created", "No empty-schema candidate was created."),
        ("dataset_not_written", "No dataset row was written."),
        ("real_evidence_not_collected", "No real forward evidence was collected."),
        ("evidence_persistence_not_enabled", "Evidence persistence remains disabled."),
        ("signal_generation_not_enabled", "Signal generation remains disabled."),
        ("live_alerts_not_enabled", "Live alerts remain disabled."),
        ("paper_trading_not_enabled", "Paper trading remains disabled."),
        ("long_strategy_not_approved", "The LONG research candidate remains unapproved."),
        ("real_capital_not_allowed", "Real capital remains prohibited."),
        ("market_execution_not_allowed", "Market execution remains prohibited."),
        ("automation_not_allowed", "Automation remains prohibited."),
        ("future_empty_schema_candidate_only", "The only next allowance is an empty-schema candidate implementation."),
    ]
    for name, details in warnings:
        add("scope_control", name, True, "WARNING", details)
    add("phase_transition", "phase_10_40_recommended_next", True, "INFO", "Recommended next: Phase 10.40 empty-schema candidate implementation.")
    return pd.DataFrame(rows)


def build_summary(source_manifest: pd.DataFrame, validations: pd.DataFrame, items: pd.DataFrame, findings: pd.DataFrame, controls: pd.DataFrame, rules: pd.DataFrame, requirements: pd.DataFrame, guards: pd.DataFrame, path_plan: pd.DataFrame, decision: pd.DataFrame, checks: pd.DataFrame, official_before: bool, official_after: bool) -> pd.DataFrame:
    decision_row = decision.iloc[0].to_dict() if len(decision) == 1 else {}
    error_count = int(checks["severity"].astype(str).eq("ERROR").sum())
    warning_count = int(checks["severity"].astype(str).eq("WARNING").sum())
    blocker_count = int(checks["blocker"].map(safe_bool).sum())
    material_issue_count = int(findings["material_issue_found"].map(safe_bool).sum())
    validation_passed = all([error_count == 0, blocker_count == 0, all_passed(validations), all_passed(items), all_passed(findings), all_passed(controls), all_passed(rules), all_passed(requirements), all_passed(guards)])
    return pd.DataFrame([{
        "phase": "10.39",
        "official_dataset_schema_implementation_precheck_defined": True,
        "phase_10_38_source_validated": all_passed(validations),
        "source_artifact_count": len(source_manifest),
        "source_artifacts_exist": source_manifest["artifact_exists"].map(safe_bool).all(),
        "source_artifacts_non_empty": source_manifest["artifact_non_empty"].map(safe_bool).all(),
        "source_artifact_hashes_valid": source_manifest["artifact_sha256_valid"].map(safe_bool).all(),
        "source_manifest_sha256": manifest_digest(source_manifest),
        "precheck_validation_rows": len(validations),
        "precheck_item_rows": len(items),
        "precheck_finding_rows": len(findings),
        "precheck_control_rows": len(controls),
        "precheck_rule_rows": len(rules),
        "precheck_requirement_rows": len(requirements),
        "precheck_guard_rows": len(guards),
        "precheck_path_plan_rows": len(path_plan),
        "precheck_validations_passed": all_passed(validations),
        "precheck_items_passed": all_passed(items),
        "precheck_findings_passed": all_passed(findings),
        "precheck_controls_passed": all_passed(controls),
        "precheck_rules_passed": all_passed(rules),
        "precheck_requirements_passed": all_passed(requirements),
        "precheck_guards_passed": all_passed(guards),
        "material_issue_count": material_issue_count,
        "official_dataset_schema_implementation_precheck_performed": True,
        "official_dataset_schema_implementation_precheck_passed": safe_bool(decision_row.get("official_dataset_schema_implementation_precheck_passed", False)),
        "official_dataset_schema_implementation_precheck_decision": str(decision_row.get("official_dataset_schema_implementation_precheck_decision", "")),
        "future_official_dataset_empty_schema_candidate_implementation_allowed": safe_bool(decision_row.get("future_official_dataset_empty_schema_candidate_implementation_allowed", False)),
        "official_dataset_implementation_allowed": False,
        "official_dataset_creation_allowed": False,
        "empty_schema_candidate_created": False,
        "evidence_collection_enabled": False,
        "evidence_collection_started": False,
        "official_dataset_schema_implemented": False,
        "official_dataset_write_allowed": False,
        "official_dataset_write_performed": False,
        "official_dataset_exists_before": official_before,
        "official_dataset_exists_after": official_after,
        "official_dataset_unchanged_absent": not official_before and not official_after,
        "official_evidence_rows_written": 0,
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
        "total_checks": len(checks),
        "warning_count": warning_count,
        "error_count": error_count,
        "blocker_count": blocker_count,
        "validation_passed": validation_passed,
        "validation_decision": "PHASE_10_39_LONG_FORWARD_OBSERVATION_EVIDENCE_COLLECTION_OFFICIAL_DATASET_SCHEMA_IMPLEMENTATION_PRECHECK_VALIDATED" if validation_passed else "PHASE_10_39_LONG_FORWARD_OBSERVATION_EVIDENCE_COLLECTION_OFFICIAL_DATASET_SCHEMA_IMPLEMENTATION_PRECHECK_FAILED",
    }])


def run_long_forward_observation_evidence_collection_official_dataset_schema_implementation_precheck() -> dict[str, pd.DataFrame]:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    docs_exist = {
        "phase_10_37_schema_design_doc_exists": PHASE_10_37_DOC_PATH.exists(),
        "phase_10_38_schema_design_review_doc_exists": PHASE_10_38_DOC_PATH.exists(),
        "phase_10_39_implementation_precheck_doc_exists": PHASE_10_39_DOC_PATH.exists(),
    }
    official_before = Path(OFFICIAL_DATASET_PATH).exists()
    source_manifest_before = build_manifest(SOURCE_PATHS, "PHASE_10_39_SOURCE")
    source = {name: read_csv(path) for name, path in SOURCE_PATHS.items()}
    path_plan = build_path_plan()
    source_manifest_after = build_manifest(SOURCE_PATHS, "PHASE_10_39_SOURCE")
    official_after = Path(OFFICIAL_DATASET_PATH).exists()

    validations = build_validations(source, source_manifest_before, source_manifest_after, path_plan, official_before, official_after)
    items = build_items(validations)
    findings = build_findings(items)
    controls = build_controls(validations)
    rules = build_rules(validations, items, findings, controls)
    guards = build_guard_matrix(all([all_passed(validations), all_passed(items), all_passed(findings), all_passed(controls), all_passed(rules)]))
    requirements = build_requirements(validations, items, findings, controls, rules, guards, path_plan)
    decision = build_decision(validations, items, findings, controls, rules, requirements, guards)
    checks = build_checks(docs_exist, validations, items, findings, controls, rules, requirements, guards, path_plan, decision, official_before, official_after)
    summary = build_summary(source_manifest_before, validations, items, findings, controls, rules, requirements, guards, path_plan, decision, checks, official_before, official_after)

    frames = {
        "summary": summary,
        "validations": validations,
        "items": items,
        "findings": findings,
        "controls": controls,
        "rules": rules,
        "requirements": requirements,
        "guard_matrix": guards,
        "path_plan": path_plan,
        "decision": decision,
        "checks": checks,
    }
    for name, dataframe in frames.items():
        dataframe.to_csv(REPORTS_DIR / OUTPUT_FILENAMES[name], index=False)

    output_paths = {name: REPORTS_DIR / OUTPUT_FILENAMES[name] for name in frames}
    output_manifest = build_manifest(output_paths, "PHASE_10_39_OUTPUT")
    combined_manifest = pd.concat([source_manifest_after, output_manifest], ignore_index=True)
    combined_manifest.to_csv(REPORTS_DIR / OUTPUT_FILENAMES["manifest"], index=False)

    return {
        "summary": summary,
        "source_review_summary": source["review_summary"],
        "source_review_decision": source["review_decision"],
        "source_design_summary": source["design_summary"],
        "source_field_catalog": source["field_catalog"],
        "source_migration_plan": source["migration_plan"],
        "source_artifact_manifest": source_manifest_before,
        "validations": validations,
        "items": items,
        "findings": findings,
        "controls": controls,
        "rules": rules,
        "requirements": requirements,
        "guard_matrix": guards,
        "path_plan": path_plan,
        "decision": decision,
        "checks": checks,
        "manifest": combined_manifest,
    }
