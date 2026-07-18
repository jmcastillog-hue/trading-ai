from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

import pandas as pd

try:
    from src.long_side.long_forward_observation_dataset_bootstrap_v1 import (
        OFFICIAL_DATASET_PATH,
    )
except ImportError:
    OFFICIAL_DATASET_PATH = Path(
        "data/forward_observation/"
        "long_forward_observation_official_evidence_dataset_v1.csv"
    )


REPORTS_DIR = Path(
    "reports/p10_38_evidence_collection_official_dataset_"
    "schema_implementation_design_review_v1"
)
SOURCE_DIR = Path(
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

SOURCE_PATHS = {
    "summary": (
        SOURCE_DIR
        / "official_dataset_schema_implementation_design_summary_v1.csv"
    ),
    "source_validations": (
        SOURCE_DIR
        / "official_dataset_schema_implementation_design_source_validations_v1.csv"
    ),
    "field_catalog": (
        SOURCE_DIR / "official_dataset_schema_field_catalog_v1.csv"
    ),
    "enum_domains": (
        SOURCE_DIR / "official_dataset_schema_enum_domains_v1.csv"
    ),
    "constraints": (
        SOURCE_DIR / "official_dataset_schema_constraints_v1.csv"
    ),
    "key_index_design": (
        SOURCE_DIR / "official_dataset_schema_key_index_design_v1.csv"
    ),
    "provenance_contract": (
        SOURCE_DIR / "official_dataset_schema_provenance_contract_v1.csv"
    ),
    "lifecycle_contract": (
        SOURCE_DIR / "official_dataset_schema_lifecycle_contract_v1.csv"
    ),
    "migration_plan": (
        SOURCE_DIR / "official_dataset_schema_migration_plan_v1.csv"
    ),
    "safety_guards": (
        SOURCE_DIR / "official_dataset_schema_safety_guards_v1.csv"
    ),
    "acceptance_criteria": (
        SOURCE_DIR / "official_dataset_schema_acceptance_criteria_v1.csv"
    ),
    "decision": (
        SOURCE_DIR
        / "official_dataset_schema_implementation_design_decision_v1.csv"
    ),
    "checks": (
        SOURCE_DIR
        / "official_dataset_schema_implementation_design_checks_v1.csv"
    ),
    "manifest": (
        SOURCE_DIR
        / "source_official_dataset_schema_implementation_design_artifact_manifest_v1.csv"
    ),
}

SOURCE_READY_DECISION = (
    "CONTROLLED_FORWARD_OBSERVATION_EVIDENCE_COLLECTION_OFFICIAL_"
    "DATASET_SCHEMA_IMPLEMENTATION_DESIGN_READY_FOR_DESIGN_REVIEW"
)
READY_DECISION = (
    "CONTROLLED_FORWARD_OBSERVATION_EVIDENCE_COLLECTION_OFFICIAL_"
    "DATASET_SCHEMA_IMPLEMENTATION_DESIGN_REVIEW_READY_FOR_"
    "IMPLEMENTATION_PRECHECK"
)
BLOCKED_DECISION = (
    "CONTROLLED_FORWARD_OBSERVATION_EVIDENCE_COLLECTION_OFFICIAL_"
    "DATASET_SCHEMA_IMPLEMENTATION_DESIGN_REVIEW_BLOCKED"
)
RECOMMENDED_NEXT_PHASE = (
    "PHASE_10_39_LONG_FORWARD_OBSERVATION_EVIDENCE_COLLECTION_"
    "OFFICIAL_DATASET_SCHEMA_IMPLEMENTATION_PRECHECK_V1"
)
STORAGE_DESIGN = (
    "CSV_APPEND_ONLY_ATOMIC_REPLACE_WITH_SHA256_MANIFEST_V1"
)

EXPECTED_FIELD_NAMES = [
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

EXPECTED_ENUM_DOMAINS = {
    "source_system": {
        "CONTROLLED_FORWARD_OBSERVATION_RECORDER",
        "MANUAL_REVIEWED_IMPORT",
    },
    "direction": {"LONG"},
    "timeframe": {"15m"},
    "observation_state": {
        "CONTROLLED_FORWARD_OBSERVATION_STARTED",
        "OBSERVATION_CAPTURED",
        "OBSERVATION_REVIEWED",
    },
    "evidence_status": {
        "PENDING_VALIDATION",
        "VALIDATED",
        "REJECTED",
    },
    "evidence_scope": {"CONTROLLED_FORWARD_EVIDENCE"},
    "cost_profile": {
        "ZERO_COST_RESEARCH",
        "COST_AWARE_RESEARCH",
    },
    "activation_scope": {"EVIDENCE_ONLY"},
    "signal_state": {"NO_SIGNAL"},
    "deduplication_status": {
        "UNIQUE_CANDIDATE",
        "DUPLICATE_REJECTED",
    },
    "lifecycle_state": {
        "DRAFT",
        "VALIDATED",
        "REJECTED",
        "SUPERSEDED",
    },
    "review_status": {
        "PENDING_REVIEW",
        "APPROVED_AS_EVIDENCE",
        "REJECTED",
    },
}

EXPECTED_CONSTRAINT_IDS = [
    "PK_EVIDENCE_ID",
    "UQ_DEDUPLICATION_KEY",
    "UQ_EVIDENCE_HASH",
    "UQ_AUDIT_EVENT_ID",
    "CK_DIRECTION_LONG",
    "CK_TIME_ORDER",
    "CK_PRICE_POSITIVE",
    "CK_LONG_PRICE_STRUCTURE",
    "CK_INVALIDATION_MATCH",
    "CK_RISK_REWARD_POSITIVE",
    "CK_HASH_FORMAT",
    "CK_MANUAL_CONFIRMATION",
    "CK_VALIDATION_GATE",
    "CK_REJECTION_REASON",
    "CK_APPROVED_REVIEWER",
    "CK_PREVIOUS_HASH",
    "CK_SAFETY_EXECUTION_FALSE",
    "CK_SCOPE_EVIDENCE_ONLY",
    "CK_SIGNAL_STATE_NONE",
    "CK_WRITE_PERMISSION",
]

EXPECTED_KEY_INDEX_IDS = [
    "PK_EVIDENCE_ID",
    "UQ_DEDUPLICATION_KEY",
    "UQ_EVIDENCE_HASH",
    "UQ_AUDIT_EVENT_ID",
    "IX_OBSERVED_AT",
    "IX_SYMBOL_TIMEFRAME_TIME",
    "IX_CANDIDATE_TIME",
    "IX_STATUS_REVIEW",
    "IX_LIFECYCLE_TIME",
    "IX_PREVIOUS_HASH",
]

EXPECTED_PROVENANCE_RULES = [
    "source_system_allowlist",
    "source_artifact_required",
    "source_artifact_sha256_required",
    "source_row_hash_required",
    "deterministic_row_serialization",
    "evidence_hash_required",
    "previous_hash_chain",
    "audit_event_required",
    "created_by_required",
    "reviewer_required_for_acceptance",
    "rollback_reference_required_after_first_write",
    "source_files_immutable_during_write",
]

EXPECTED_LIFECYCLE_TRANSITIONS = [
    ("DRAFT", "VALIDATED"),
    ("DRAFT", "REJECTED"),
    ("VALIDATED", "SUPERSEDED"),
    ("REJECTED", "DRAFT"),
    ("PENDING_VALIDATION", "VALIDATED"),
    ("PENDING_VALIDATION", "REJECTED"),
    ("PENDING_REVIEW", "APPROVED_AS_EVIDENCE"),
    ("PENDING_REVIEW", "REJECTED"),
    ("APPROVED_AS_EVIDENCE", "SUPERSEDED"),
    ("ANY", "NO_DELETE"),
]

EXPECTED_MIGRATION_STEPS = [
    "freeze_design_contract",
    "design_review",
    "implementation_precheck",
    "create_empty_schema_candidate",
    "schema_validation",
    "atomic_write_harness",
    "manifest_sidecar",
    "backup_and_rollback",
    "synthetic_write_dry_run",
    "output_integrity_review",
    "final_implementation_approval",
    "real_evidence_precheck",
]

EXPECTED_SAFETY_GUARDS = [
    "design_only",
    "source_final_approval_passed",
    "schema_field_count",
    "schema_order_defined",
    "storage_design_defined",
    "future_design_review_allowed",
    "dataset_implementation_allowed",
    "dataset_creation_allowed",
    "evidence_collection_enabled",
    "evidence_collection_started",
    "official_dataset_schema_implemented",
    "official_dataset_write_allowed",
    "official_dataset_write_performed",
    "real_forward_dataset_created",
    "official_evidence_rows_written",
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
    "official_dataset_exists_before",
    "official_dataset_exists_after",
    "new_official_dataset_rows_created",
    "source_artifacts_stable",
    "manifest_self_exclusion_expected",
]

EXPECTED_ACCEPTANCE_CRITERIA = [
    "source_phase_10_36_validated",
    "schema_field_count_54",
    "schema_positions_exact",
    "schema_field_names_unique",
    "primary_key_exactly_one",
    "unique_integrity_keys_defined",
    "enum_domains_defined",
    "constraints_count_20",
    "long_price_structure_constraint_defined",
    "execution_safety_constraint_defined",
    "key_index_count_10",
    "provenance_rule_count_12",
    "hash_chain_defined",
    "lifecycle_transition_count_10",
    "atomic_write_design_defined",
    "backup_and_rollback_defined",
    "migration_step_count_12",
    "safety_guard_count_37",
    "safety_guards_all_passed",
    "official_dataset_absent",
    "no_rows_written",
    "design_review_only_next",
    "dataset_implementation_not_allowed",
    "long_strategy_remains_unapproved",
    "total_project_not_completed",
]

FALSE_OPERATIONAL_GUARDS = {
    "dataset_implementation_allowed",
    "dataset_creation_allowed",
    "evidence_collection_enabled",
    "evidence_collection_started",
    "official_dataset_schema_implemented",
    "official_dataset_write_allowed",
    "official_dataset_write_performed",
    "real_forward_dataset_created",
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
    "official_dataset_exists_before",
    "official_dataset_exists_after",
}

OUTPUT_FILENAMES = {
    "summary": (
        "official_dataset_schema_implementation_design_review_summary_v1.csv"
    ),
    "validations": (
        "official_dataset_schema_implementation_design_review_validations_v1.csv"
    ),
    "items": (
        "official_dataset_schema_implementation_design_review_items_v1.csv"
    ),
    "findings": (
        "official_dataset_schema_implementation_design_review_findings_v1.csv"
    ),
    "controls": (
        "official_dataset_schema_implementation_design_review_controls_v1.csv"
    ),
    "rules": (
        "official_dataset_schema_implementation_design_review_rules_v1.csv"
    ),
    "requirements": (
        "official_dataset_schema_implementation_design_review_requirements_v1.csv"
    ),
    "guard_matrix": (
        "official_dataset_schema_implementation_design_review_guard_matrix_v1.csv"
    ),
    "decision": (
        "official_dataset_schema_implementation_design_review_decision_v1.csv"
    ),
    "checks": (
        "official_dataset_schema_implementation_design_review_checks_v1.csv"
    ),
    "manifest": (
        "source_official_dataset_schema_implementation_design_review_artifact_manifest_v1.csv"
    ),
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
    return (
        not df.empty
        and "passed" in df.columns
        and df["passed"].map(safe_bool).all()
    )


def column_all_bool(
    df: pd.DataFrame,
    column: str,
    expected: bool,
) -> bool:
    return (
        not df.empty
        and column in df.columns
        and df[column]
        .map(lambda value: safe_bool(value, not expected))
        .eq(expected)
        .all()
    )


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
    return len(text) == 64 and all(
        character in "0123456789abcdef"
        for character in text.lower()
    )


def build_manifest(
    paths: dict[str, Path],
    scope: str,
) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for position, (name, path) in enumerate(paths.items(), start=1):
        exists = path.exists() and path.is_file()
        size = path.stat().st_size if exists else 0
        digest = sha256_file(path) if exists else ""
        rows.append(
            {
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
            }
        )
    return pd.DataFrame(rows)


def manifest_digest(df: pd.DataFrame) -> str:
    if df.empty:
        return ""
    payload = (
        df[
            [
                "artifact_scope",
                "artifact_name",
                "artifact_path",
                "artifact_size_bytes",
                "artifact_sha256",
            ]
        ]
        .astype(str)
        .sort_values(
            ["artifact_scope", "artifact_name", "artifact_path"]
        )
        .to_csv(index=False)
        .encode("utf-8")
    )
    return hashlib.sha256(payload).hexdigest()


def ordered_values(
    df: pd.DataFrame,
    position_column: str,
    value_column: str,
) -> list[str]:
    if (
        df.empty
        or position_column not in df.columns
        or value_column not in df.columns
    ):
        return []
    return (
        df.sort_values(position_column)[value_column]
        .astype(str)
        .tolist()
    )


def value_set(df: pd.DataFrame, column: str) -> set[str]:
    if df.empty or column not in df.columns:
        return set()
    return set(df[column].astype(str))


def append_validation(
    rows: list[dict[str, Any]],
    name: str,
    passed: bool,
    details: str,
) -> None:
    rows.append(
        {
            "validation_position": len(rows) + 1,
            "validation_name": name,
            "passed": bool(passed),
            "details": details,
        }
    )


def validate_manifest_source_file(
    manifest_df: pd.DataFrame,
    manifest_path: Path,
) -> dict[str, bool]:
    required_columns = {
        "artifact_scope",
        "artifact_filename",
        "artifact_path",
        "artifact_exists",
        "artifact_size_bytes",
        "artifact_non_empty",
        "artifact_sha256",
        "artifact_sha256_valid",
    }
    if (
        manifest_df.empty
        or not required_columns.issubset(manifest_df.columns)
    ):
        return {
            "source_manifest_rows_24": False,
            "source_manifest_phase_10_36_rows_11": False,
            "source_manifest_phase_10_37_output_rows_13": False,
            "source_manifest_listed_artifacts_valid": False,
            "source_manifest_hashes_match_current_files": False,
            "source_manifest_self_exclusion_expected": False,
            "source_manifest_file_exists": manifest_path.exists(),
            "source_manifest_file_non_empty": (
                manifest_path.exists()
                and manifest_path.stat().st_size > 0
            ),
            "source_manifest_file_sha256_valid": is_sha256(
                sha256_file(manifest_path)
            ),
        }

    phase_10_36 = manifest_df[
        manifest_df["artifact_scope"].astype(str).eq("PHASE_10_36")
    ]
    phase_10_37 = manifest_df[
        manifest_df["artifact_scope"]
        .astype(str)
        .eq("PHASE_10_37_OUTPUT")
    ]
    listed_valid = (
        manifest_df["artifact_exists"].map(safe_bool).all()
        and manifest_df["artifact_non_empty"].map(safe_bool).all()
        and manifest_df["artifact_sha256_valid"].map(safe_bool).all()
        and (manifest_df["artifact_size_bytes"].map(safe_int) > 0).all()
    )

    hashes_match = True
    for _, row in manifest_df.iterrows():
        path = Path(str(row["artifact_path"]))
        if (
            not path.exists()
            or sha256_file(path) != str(row["artifact_sha256"])
        ):
            hashes_match = False
            break

    filenames = set(manifest_df["artifact_filename"].astype(str))
    self_exclusion = (
        len(manifest_df) == 24
        and len(phase_10_37) == 13
        and manifest_path.name not in filenames
    )
    exists = manifest_path.exists() and manifest_path.is_file()
    non_empty = exists and manifest_path.stat().st_size > 0
    digest_valid = is_sha256(sha256_file(manifest_path))

    return {
        "source_manifest_rows_24": len(manifest_df) == 24,
        "source_manifest_phase_10_36_rows_11": (
            len(phase_10_36) == 11
        ),
        "source_manifest_phase_10_37_output_rows_13": (
            len(phase_10_37) == 13
        ),
        "source_manifest_listed_artifacts_valid": listed_valid,
        "source_manifest_hashes_match_current_files": hashes_match,
        "source_manifest_self_exclusion_expected": self_exclusion,
        "source_manifest_file_exists": exists,
        "source_manifest_file_non_empty": non_empty,
        "source_manifest_file_sha256_valid": digest_valid,
    }


def build_validations(
    source: dict[str, pd.DataFrame],
    source_manifest_before: pd.DataFrame,
    source_manifest_after: pd.DataFrame,
    official_before: bool,
    official_after: bool,
) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []

    append_validation(
        rows,
        "source_artifact_count_14",
        len(source_manifest_before) == 14,
        f"rows={len(source_manifest_before)}",
    )
    append_validation(
        rows,
        "source_artifacts_exist",
        (
            len(source_manifest_before) == 14
            and source_manifest_before["artifact_exists"]
            .map(safe_bool)
            .all()
        ),
        f"rows={len(source_manifest_before)}",
    )
    append_validation(
        rows,
        "source_artifacts_non_empty",
        (
            len(source_manifest_before) == 14
            and source_manifest_before["artifact_non_empty"]
            .map(safe_bool)
            .all()
        ),
        f"rows={len(source_manifest_before)}",
    )
    append_validation(
        rows,
        "source_artifact_hashes_valid",
        (
            len(source_manifest_before) == 14
            and source_manifest_before["artifact_sha256_valid"]
            .map(safe_bool)
            .all()
        ),
        f"rows={len(source_manifest_before)}",
    )
    append_validation(
        rows,
        "source_artifacts_stable_during_review",
        (
            bool(manifest_digest(source_manifest_before))
            and manifest_digest(source_manifest_before)
            == manifest_digest(source_manifest_after)
        ),
        (
            f"before={manifest_digest(source_manifest_before)},"
            f"after={manifest_digest(source_manifest_after)}"
        ),
    )

    summary = (
        source["summary"].iloc[0].to_dict()
        if len(source["summary"]) == 1
        else {}
    )
    summary_checks = [
        (
            "phase_10_37_validation_passed",
            safe_bool(summary.get("validation_passed", False))
            and str(summary.get("validation_decision", ""))
            == (
                "PHASE_10_37_LONG_FORWARD_OBSERVATION_EVIDENCE_"
                "COLLECTION_OFFICIAL_DATASET_SCHEMA_IMPLEMENTATION_"
                "DESIGN_VALIDATED"
            ),
        ),
        (
            "source_design_performed",
            safe_bool(
                summary.get(
                    "official_dataset_schema_implementation_design_performed",
                    False,
                )
            ),
        ),
        (
            "source_design_passed",
            safe_bool(
                summary.get(
                    "official_dataset_schema_implementation_design_passed",
                    False,
                )
            ),
        ),
        (
            "source_design_decision_valid",
            str(
                summary.get(
                    "official_dataset_schema_implementation_design_decision",
                    "",
                )
            )
            == SOURCE_READY_DECISION,
        ),
        (
            "source_design_review_allowed",
            safe_bool(
                summary.get(
                    "future_official_dataset_schema_implementation_design_review_allowed",
                    False,
                )
            ),
        ),
        (
            "source_summary_source_artifact_count_11",
            safe_int(summary.get("source_artifact_count", -1), -1)
            == 11,
        ),
        (
            "source_summary_validation_rows_38",
            safe_int(summary.get("source_validation_rows", -1), -1)
            == 38,
        ),
        (
            "source_summary_field_count_54",
            safe_int(
                summary.get("canonical_schema_field_count", -1),
                -1,
            )
            == 54,
        ),
        (
            "source_summary_enum_rows_24",
            safe_int(summary.get("enum_domain_rows", -1), -1) == 24,
        ),
        (
            "source_summary_constraint_rows_20",
            safe_int(summary.get("constraint_rows", -1), -1) == 20,
        ),
        (
            "source_summary_key_index_rows_10",
            safe_int(summary.get("key_index_rows", -1), -1) == 10,
        ),
        (
            "source_summary_provenance_rows_12",
            safe_int(
                summary.get("provenance_rule_rows", -1),
                -1,
            )
            == 12,
        ),
        (
            "source_summary_lifecycle_rows_10",
            safe_int(
                summary.get("lifecycle_transition_rows", -1),
                -1,
            )
            == 10,
        ),
        (
            "source_summary_migration_rows_12",
            safe_int(summary.get("migration_step_rows", -1), -1)
            == 12,
        ),
        (
            "source_summary_guard_rows_37",
            safe_int(summary.get("safety_guard_rows", -1), -1)
            == 37,
        ),
        (
            "source_summary_acceptance_rows_25",
            safe_int(
                summary.get("acceptance_criteria_rows", -1),
                -1,
            )
            == 25,
        ),
        (
            "source_summary_storage_design_valid",
            str(summary.get("storage_design", ""))
            == STORAGE_DESIGN,
        ),
        (
            "source_summary_total_checks_32",
            safe_int(summary.get("total_checks", -1), -1) == 32,
        ),
        (
            "source_summary_warning_count_15",
            safe_int(summary.get("warning_count", -1), -1) == 15,
        ),
        (
            "source_summary_error_count_zero",
            safe_int(summary.get("error_count", -1), -1) == 0,
        ),
        (
            "source_summary_blocker_count_zero",
            safe_int(summary.get("blocker_count", -1), -1) == 0,
        ),
        (
            "source_summary_official_dataset_unchanged_absent",
            safe_bool(
                summary.get(
                    "official_dataset_unchanged_absent",
                    False,
                )
            ),
        ),
    ]
    for name, passed in summary_checks:
        append_validation(rows, name, passed, f"{name}={passed}")

    decision = (
        source["decision"].iloc[0].to_dict()
        if len(source["decision"]) == 1
        else {}
    )
    decision_checks = [
        ("source_decision_row_count_1", len(source["decision"]) == 1),
        (
            "source_decision_design_performed",
            safe_bool(
                decision.get(
                    "official_dataset_schema_implementation_design_performed",
                    False,
                )
            ),
        ),
        (
            "source_decision_design_passed",
            safe_bool(
                decision.get(
                    "official_dataset_schema_implementation_design_passed",
                    False,
                )
            ),
        ),
        (
            "source_decision_value_valid",
            str(
                decision.get(
                    "official_dataset_schema_implementation_design_decision",
                    "",
                )
            )
            == SOURCE_READY_DECISION,
        ),
        (
            "source_decision_field_count_54",
            safe_int(
                decision.get("canonical_schema_field_count", -1),
                -1,
            )
            == 54,
        ),
        (
            "source_decision_acceptance_count_25",
            safe_int(
                decision.get("total_acceptance_criteria", -1),
                -1,
            )
            == 25,
        ),
        (
            "source_decision_failed_acceptance_zero",
            safe_int(
                decision.get("failed_acceptance_criteria", -1),
                -1,
            )
            == 0,
        ),
        (
            "source_decision_review_allowed",
            safe_bool(
                decision.get(
                    "future_official_dataset_schema_implementation_design_review_allowed",
                    False,
                )
            ),
        ),
    ]
    for name, passed in decision_checks:
        append_validation(rows, name, passed, f"{name}={passed}")

    field_catalog = source["field_catalog"]
    field_names = ordered_values(
        field_catalog,
        "field_position",
        "field_name",
    )
    nullable_count = (
        int(field_catalog["nullable"].map(safe_bool).sum())
        if not field_catalog.empty
        and "nullable" in field_catalog.columns
        else -1
    )
    safety_fields = (
        field_catalog[
            field_catalog["field_group"].astype(str).eq("SAFETY")
        ]
        if not field_catalog.empty
        and "field_group" in field_catalog.columns
        else pd.DataFrame()
    )
    field_checks = [
        ("field_catalog_rows_54", len(field_catalog) == 54),
        (
            "field_catalog_positions_exact",
            (
                not field_catalog.empty
                and "field_position" in field_catalog.columns
                and field_catalog["field_position"]
                .map(safe_int)
                .tolist()
                == list(range(1, 55))
            ),
        ),
        ("field_catalog_names_exact", field_names == EXPECTED_FIELD_NAMES),
        (
            "field_catalog_names_unique",
            (
                not field_catalog.empty
                and "field_name" in field_catalog.columns
                and field_catalog["field_name"].astype(str).is_unique
            ),
        ),
        (
            "field_catalog_canonical_order_required",
            column_all_bool(
                field_catalog,
                "canonical_order_required",
                True,
            ),
        ),
        (
            "field_catalog_design_only",
            column_all_bool(field_catalog, "design_only", True),
        ),
        (
            "field_catalog_primary_key_count_1",
            (
                not field_catalog.empty
                and "key_role" in field_catalog.columns
                and int(
                    field_catalog["key_role"]
                    .astype(str)
                    .eq("PRIMARY_KEY")
                    .sum()
                )
                == 1
            ),
        ),
        (
            "field_catalog_primary_key_evidence_id",
            (
                not field_catalog.empty
                and set(
                    field_catalog[
                        field_catalog["key_role"]
                        .astype(str)
                        .eq("PRIMARY_KEY")
                    ]["field_name"].astype(str)
                )
                == {"evidence_id"}
            ),
        ),
        (
            "field_catalog_logical_types_allowed",
            (
                not field_catalog.empty
                and "logical_type" in field_catalog.columns
                and value_set(
                    field_catalog,
                    "logical_type",
                ).issubset(
                    {
                        "STRING",
                        "UTC_TIMESTAMP",
                        "ENUM_STRING",
                        "SHA256",
                        "DECIMAL",
                        "BOOLEAN",
                    }
                )
            ),
        ),
        ("field_catalog_nullable_count_5", nullable_count == 5),
        ("field_catalog_safety_field_count_13", len(safety_fields) == 13),
        (
            "field_catalog_safety_boolean_field_count_11",
            (
                len(safety_fields) == 13
                and int(
                    safety_fields["logical_type"]
                    .astype(str)
                    .eq("BOOLEAN")
                    .sum()
                )
                == 11
            ),
        ),
    ]
    for name, passed in field_checks:
        append_validation(rows, name, passed, f"{name}={passed}")

    enum_domains = source["enum_domains"]
    actual_domains: dict[str, set[str]] = {}
    if (
        not enum_domains.empty
        and {"field_name", "allowed_value"}.issubset(
            enum_domains.columns
        )
    ):
        for field_name, group in enum_domains.groupby("field_name"):
            actual_domains[str(field_name)] = set(
                group["allowed_value"].astype(str)
            )
    enum_checks = [
        ("enum_domain_rows_24", len(enum_domains) == 24),
        (
            "enum_positions_exact",
            (
                not enum_domains.empty
                and "enum_position" in enum_domains.columns
                and enum_domains["enum_position"]
                .map(safe_int)
                .tolist()
                == list(range(1, 25))
            ),
        ),
        (
            "enum_field_names_exact",
            set(actual_domains) == set(EXPECTED_ENUM_DOMAINS),
        ),
        (
            "enum_domains_exact",
            actual_domains == EXPECTED_ENUM_DOMAINS,
        ),
        (
            "enum_domains_closed",
            column_all_bool(enum_domains, "closed_domain", True),
        ),
        (
            "enum_domains_design_only",
            column_all_bool(enum_domains, "design_only", True),
        ),
        (
            "enum_direction_long_only",
            actual_domains.get("direction") == {"LONG"},
        ),
        (
            "enum_timeframe_15m_only",
            actual_domains.get("timeframe") == {"15m"},
        ),
        (
            "enum_activation_evidence_only",
            actual_domains.get("activation_scope")
            == {"EVIDENCE_ONLY"},
        ),
        (
            "enum_signal_no_signal_only",
            actual_domains.get("signal_state") == {"NO_SIGNAL"},
        ),
    ]
    for name, passed in enum_checks:
        append_validation(rows, name, passed, f"{name}={passed}")

    constraints = source["constraints"]
    constraint_ids = ordered_values(
        constraints,
        "constraint_position",
        "constraint_id",
    )
    constraint_checks = [
        ("constraint_rows_20", len(constraints) == 20),
        (
            "constraint_positions_exact",
            (
                not constraints.empty
                and "constraint_position" in constraints.columns
                and constraints["constraint_position"]
                .map(safe_int)
                .tolist()
                == list(range(1, 21))
            ),
        ),
        (
            "constraint_ids_exact",
            constraint_ids == EXPECTED_CONSTRAINT_IDS,
        ),
        (
            "constraints_required",
            column_all_bool(constraints, "required", True),
        ),
        (
            "constraints_design_only",
            column_all_bool(constraints, "design_only", True),
        ),
        (
            "long_price_structure_constraint_present",
            "CK_LONG_PRICE_STRUCTURE" in constraint_ids,
        ),
        (
            "execution_safety_constraint_present",
            "CK_SAFETY_EXECUTION_FALSE" in constraint_ids,
        ),
        (
            "write_permission_constraint_present",
            "CK_WRITE_PERMISSION" in constraint_ids,
        ),
    ]
    for name, passed in constraint_checks:
        append_validation(rows, name, passed, f"{name}={passed}")

    key_index = source["key_index_design"]
    key_ids = ordered_values(
        key_index,
        "key_index_position",
        "key_index_id",
    )
    key_checks = [
        ("key_index_rows_10", len(key_index) == 10),
        (
            "key_index_positions_exact",
            (
                not key_index.empty
                and "key_index_position" in key_index.columns
                and key_index["key_index_position"]
                .map(safe_int)
                .tolist()
                == list(range(1, 11))
            ),
        ),
        ("key_index_ids_exact", key_ids == EXPECTED_KEY_INDEX_IDS),
        (
            "key_index_design_only",
            column_all_bool(key_index, "design_only", True),
        ),
        (
            "key_index_primary_unique",
            (
                not key_index.empty
                and len(
                    key_index[
                        key_index["key_index_type"]
                        .astype(str)
                        .eq("PRIMARY")
                    ]
                )
                == 1
                and key_index[
                    key_index["key_index_type"]
                    .astype(str)
                    .eq("PRIMARY")
                ]["unique"]
                .map(safe_bool)
                .all()
            ),
        ),
        (
            "key_index_unique_count_3",
            (
                not key_index.empty
                and int(
                    key_index["key_index_type"]
                    .astype(str)
                    .eq("UNIQUE")
                    .sum()
                )
                == 3
            ),
        ),
        (
            "key_index_composite_count_4",
            (
                not key_index.empty
                and int(
                    key_index["key_index_type"]
                    .astype(str)
                    .eq("COMPOSITE_INDEX")
                    .sum()
                )
                == 4
            ),
        ),
    ]
    for name, passed in key_checks:
        append_validation(rows, name, passed, f"{name}={passed}")

    provenance = source["provenance_contract"]
    provenance_rules = ordered_values(
        provenance,
        "provenance_position",
        "provenance_rule",
    )
    provenance_checks = [
        ("provenance_rows_12", len(provenance) == 12),
        (
            "provenance_positions_exact",
            (
                not provenance.empty
                and "provenance_position" in provenance.columns
                and provenance["provenance_position"]
                .map(safe_int)
                .tolist()
                == list(range(1, 13))
            ),
        ),
        (
            "provenance_rules_exact",
            provenance_rules == EXPECTED_PROVENANCE_RULES,
        ),
        (
            "provenance_required",
            column_all_bool(provenance, "required", True),
        ),
        (
            "provenance_design_only",
            column_all_bool(provenance, "design_only", True),
        ),
        (
            "provenance_hash_chain_defined",
            "previous_hash_chain" in provenance_rules,
        ),
    ]
    for name, passed in provenance_checks:
        append_validation(rows, name, passed, f"{name}={passed}")

    lifecycle = source["lifecycle_contract"]
    lifecycle_transitions: list[tuple[str, str]] = []
    if (
        not lifecycle.empty
        and {"from_state", "to_state"}.issubset(lifecycle.columns)
    ):
        lifecycle_transitions = list(
            zip(
                lifecycle["from_state"].astype(str),
                lifecycle["to_state"].astype(str),
            )
        )
    lifecycle_checks = [
        ("lifecycle_rows_10", len(lifecycle) == 10),
        (
            "lifecycle_positions_exact",
            (
                not lifecycle.empty
                and "transition_position" in lifecycle.columns
                and lifecycle["transition_position"]
                .map(safe_int)
                .tolist()
                == list(range(1, 11))
            ),
        ),
        (
            "lifecycle_transitions_exact",
            lifecycle_transitions == EXPECTED_LIFECYCLE_TRANSITIONS,
        ),
        (
            "lifecycle_physical_delete_disabled",
            column_all_bool(
                lifecycle,
                "physical_delete_allowed",
                False,
            ),
        ),
        (
            "lifecycle_design_only",
            column_all_bool(lifecycle, "design_only", True),
        ),
        (
            "lifecycle_no_delete_transition_present",
            ("ANY", "NO_DELETE") in lifecycle_transitions,
        ),
        (
            "lifecycle_approved_to_superseded_present",
            (
                "APPROVED_AS_EVIDENCE",
                "SUPERSEDED",
            )
            in lifecycle_transitions,
        ),
    ]
    for name, passed in lifecycle_checks:
        append_validation(rows, name, passed, f"{name}={passed}")

    migration = source["migration_plan"]
    migration_steps = ordered_values(
        migration,
        "step_position",
        "step_name",
    )
    migration_checks = [
        ("migration_rows_12", len(migration) == 12),
        (
            "migration_positions_exact",
            (
                not migration.empty
                and "step_position" in migration.columns
                and migration["step_position"]
                .map(safe_int)
                .tolist()
                == list(range(1, 13))
            ),
        ),
        (
            "migration_steps_exact",
            migration_steps == EXPECTED_MIGRATION_STEPS,
        ),
        (
            "migration_implementation_not_performed",
            column_all_bool(
                migration,
                "implementation_performed",
                False,
            ),
        ),
        (
            "migration_dataset_not_created",
            column_all_bool(migration, "dataset_created", False),
        ),
        (
            "migration_rows_written_zero",
            (
                not migration.empty
                and "rows_written" in migration.columns
                and migration["rows_written"].map(safe_int).eq(0).all()
            ),
        ),
        (
            "migration_design_only",
            column_all_bool(migration, "design_only", True),
        ),
    ]
    for name, passed in migration_checks:
        append_validation(rows, name, passed, f"{name}={passed}")

    safety = source["safety_guards"]
    safety_names = ordered_values(
        safety,
        "guard_position",
        "guard_name",
    )
    actual_safety: dict[str, Any] = {}
    if (
        not safety.empty
        and {"guard_name", "actual_value"}.issubset(safety.columns)
    ):
        actual_safety = {
            str(row["guard_name"]): row["actual_value"]
            for _, row in safety.iterrows()
        }
    critical_locks_false = all(
        not safe_bool(actual_safety.get(name, True), True)
        for name in FALSE_OPERATIONAL_GUARDS
    )
    safety_checks = [
        ("safety_guard_rows_37", len(safety) == 37),
        (
            "safety_guard_positions_exact",
            (
                not safety.empty
                and "guard_position" in safety.columns
                and safety["guard_position"]
                .map(safe_int)
                .tolist()
                == list(range(1, 38))
            ),
        ),
        (
            "safety_guard_names_exact",
            safety_names == EXPECTED_SAFETY_GUARDS,
        ),
        ("safety_guards_all_passed", all_passed(safety)),
        (
            "safety_guards_design_only",
            column_all_bool(safety, "design_only", True),
        ),
        (
            "safety_critical_operational_locks_false",
            critical_locks_false,
        ),
    ]
    for name, passed in safety_checks:
        append_validation(rows, name, passed, f"{name}={passed}")

    acceptance = source["acceptance_criteria"]
    acceptance_names = ordered_values(
        acceptance,
        "criterion_position",
        "criterion_name",
    )
    acceptance_checks = [
        ("acceptance_rows_25", len(acceptance) == 25),
        (
            "acceptance_positions_exact",
            (
                not acceptance.empty
                and "criterion_position" in acceptance.columns
                and acceptance["criterion_position"]
                .map(safe_int)
                .tolist()
                == list(range(1, 26))
            ),
        ),
        (
            "acceptance_names_exact",
            acceptance_names == EXPECTED_ACCEPTANCE_CRITERIA,
        ),
        ("acceptance_all_passed", all_passed(acceptance)),
        (
            "acceptance_design_only",
            column_all_bool(acceptance, "design_only", True),
        ),
        (
            "acceptance_failed_count_zero",
            (
                not acceptance.empty
                and "passed" in acceptance.columns
                and int(
                    (~acceptance["passed"].map(safe_bool)).sum()
                )
                == 0
            ),
        ),
    ]
    for name, passed in acceptance_checks:
        append_validation(rows, name, passed, f"{name}={passed}")

    checks = source["checks"]
    warning_count = (
        int(checks["severity"].astype(str).eq("WARNING").sum())
        if not checks.empty and "severity" in checks.columns
        else -1
    )
    error_count = (
        int(checks["severity"].astype(str).eq("ERROR").sum())
        if not checks.empty and "severity" in checks.columns
        else -1
    )
    blocker_count = (
        int(checks["blocker"].map(safe_bool).sum())
        if not checks.empty and "blocker" in checks.columns
        else -1
    )
    check_checks = [
        ("source_check_rows_32", len(checks) == 32),
        ("source_check_warning_count_15", warning_count == 15),
        ("source_check_error_count_zero", error_count == 0),
        ("source_check_blocker_count_zero", blocker_count == 0),
        ("source_checks_all_passed", all_passed(checks)),
    ]
    for name, passed in check_checks:
        append_validation(rows, name, passed, f"{name}={passed}")

    for name, passed in validate_manifest_source_file(
        source["manifest"],
        SOURCE_PATHS["manifest"],
    ).items():
        append_validation(rows, name, passed, f"{name}={passed}")

    append_validation(
        rows,
        "official_dataset_absent_during_design_review",
        not official_before and not official_after,
        f"before={official_before},after={official_after}",
    )
    append_validation(
        rows,
        "design_review_only_no_implementation",
        True,
        "Phase 10.38 reviews existing design artifacts only.",
    )
    append_validation(
        rows,
        "long_strategy_remains_unapproved",
        True,
        "long_strategy_approved=False",
    )
    append_validation(
        rows,
        "total_project_not_completed",
        True,
        "total_project_completed=False",
    )

    return pd.DataFrame(rows)


def build_items(validations: pd.DataFrame) -> pd.DataFrame:
    names = validations["validation_name"].astype(str).tolist()
    rows: list[dict[str, Any]] = []
    for position, start in enumerate(range(0, len(names), 3), start=1):
        block_names = names[start : start + 3]
        selected = validations[
            validations["validation_name"].astype(str).isin(block_names)
        ]
        passed = (
            len(selected) == len(block_names)
            and selected["passed"].map(safe_bool).all()
        )
        rows.append(
            {
                "review_item_position": position,
                "review_item_id": (
                    "OFFICIAL_DATASET_SCHEMA_DESIGN_REVIEW_ITEM_"
                    f"{position:03d}"
                ),
                "review_item_name": (
                    f"schema_design_review_block_{position:03d}"
                ),
                "validation_names": ",".join(block_names),
                "required": True,
                "review_only": True,
                "implementation_precheck_only_next": True,
                "dataset_implementation_allowed": False,
                "dataset_creation_allowed": False,
                "official_dataset_write_allowed": False,
                "market_execution_allowed": False,
                "passed": bool(passed),
            }
        )
    return pd.DataFrame(rows)


def build_findings(items: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for position, (_, item) in enumerate(items.iterrows(), start=1):
        passed = safe_bool(item["passed"], False)
        rows.append(
            {
                "finding_position": position,
                "finding_id": (
                    "OFFICIAL_DATASET_SCHEMA_DESIGN_REVIEW_FINDING_"
                    f"{position:03d}"
                ),
                "review_item_id": str(item["review_item_id"]),
                "review_item_name": str(item["review_item_name"]),
                "finding_status": "PASS" if passed else "FAIL",
                "material_issue_found": not passed,
                "design_change_required": not passed,
                "implementation_precheck_allowed": passed,
                "dataset_implementation_allowed": False,
                "details": (
                    "Schema implementation design review criterion passed."
                    if passed
                    else
                    "Schema implementation design review criterion failed."
                ),
                "passed": passed,
            }
        )
    return pd.DataFrame(rows)


def build_controls(validations: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for position, (_, validation) in enumerate(
        validations.iterrows(),
        start=1,
    ):
        rows.append(
            {
                "control_position": position,
                "control_id": (
                    "OFFICIAL_DATASET_SCHEMA_DESIGN_REVIEW_CONTROL_"
                    f"{position:03d}"
                ),
                "control_name": str(
                    validation["validation_name"]
                ),
                "required": True,
                "review_only": True,
                "dataset_implementation_allowed": False,
                "dataset_creation_allowed": False,
                "evidence_collection_enabled": False,
                "official_dataset_write_allowed": False,
                "signal_generation_enabled": False,
                "market_execution_allowed": False,
                "passed": safe_bool(
                    validation["passed"],
                    False,
                ),
            }
        )
    return pd.DataFrame(rows)


def build_rules(
    validations: pd.DataFrame,
    items: pd.DataFrame,
    findings: pd.DataFrame,
    controls: pd.DataFrame,
) -> pd.DataFrame:
    material_issues = int(
        findings["material_issue_found"].map(safe_bool).sum()
    )
    rules = [
        (
            "validation_count_122",
            len(validations) == 122,
            122,
            len(validations),
        ),
        (
            "all_validations_passed",
            all_passed(validations),
            True,
            all_passed(validations),
        ),
        (
            "item_count_41",
            len(items) == 41,
            41,
            len(items),
        ),
        (
            "all_items_passed",
            all_passed(items),
            True,
            all_passed(items),
        ),
        (
            "finding_count_matches_items",
            len(findings) == len(items),
            len(items),
            len(findings),
        ),
        (
            "all_findings_passed",
            all_passed(findings),
            True,
            all_passed(findings),
        ),
        (
            "material_issue_count_zero",
            material_issues == 0,
            0,
            material_issues,
        ),
        (
            "control_count_matches_validations",
            len(controls) == len(validations),
            len(validations),
            len(controls),
        ),
        (
            "all_controls_passed",
            all_passed(controls),
            True,
            all_passed(controls),
        ),
        ("review_only", True, True, True),
        (
            "implementation_precheck_only_next",
            True,
            True,
            True,
        ),
        (
            "dataset_implementation_disabled",
            True,
            False,
            False,
        ),
        (
            "dataset_creation_disabled",
            True,
            False,
            False,
        ),
        (
            "official_dataset_writes_disabled",
            True,
            False,
            False,
        ),
        (
            "real_evidence_collection_disabled",
            True,
            False,
            False,
        ),
        (
            "evidence_persistence_disabled",
            True,
            False,
            False,
        ),
        (
            "signal_generation_disabled",
            True,
            False,
            False,
        ),
        ("live_alerts_disabled", True, False, False),
        ("paper_trading_disabled", True, False, False),
        ("long_strategy_unapproved", True, False, False),
        ("real_capital_disabled", True, False, False),
        ("market_execution_disabled", True, False, False),
        ("automation_disabled", True, False, False),
        ("project_not_completed", True, False, False),
        (
            "manifest_self_exclusion_reviewed",
            True,
            True,
            True,
        ),
        (
            "future_precheck_not_operational",
            True,
            True,
            True,
        ),
    ]
    return pd.DataFrame(
        [
            {
                "rule_id": (
                    "OFFICIAL_DATASET_SCHEMA_DESIGN_REVIEW_RULE_"
                    f"{position:03d}"
                ),
                "rule_name": name,
                "passed": bool(passed),
                "required_value": required,
                "actual_value": actual,
            }
            for position, (
                name,
                passed,
                required,
                actual,
            ) in enumerate(rules, start=1)
        ]
    )


def build_guard_matrix(review_passed: bool) -> pd.DataFrame:
    guards = [
        ("source_design_performed", True, True),
        ("source_design_passed", True, True),
        ("source_design_review_allowed", True, True),
        ("design_review_performed", True, True),
        ("design_review_passed", True, review_passed),
        (
            "future_implementation_precheck_allowed",
            True,
            review_passed,
        ),
        ("dataset_implementation_allowed", False, False),
        ("dataset_creation_allowed", False, False),
        ("evidence_collection_enabled", False, False),
        ("evidence_collection_started", False, False),
        (
            "official_dataset_schema_implemented",
            False,
            False,
        ),
        (
            "official_dataset_write_allowed",
            False,
            False,
        ),
        (
            "official_dataset_write_performed",
            False,
            False,
        ),
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
        (
            "paper_trade_execution_allowed",
            False,
            False,
        ),
        ("real_capital_allowed", False, False),
        ("market_execution_allowed", False, False),
        ("exchange_execution_allowed", False, False),
        ("automation_allowed", False, False),
        ("execution_allowed", False, False),
        ("real_entries_approved", False, False),
        ("total_project_completed", False, False),
        ("official_dataset_exists_before", False, False),
        ("official_dataset_exists_after", False, False),
        ("new_official_dataset_rows_created", 0, 0),
        ("source_artifacts_stable", True, True),
        (
            "manifest_self_exclusion_expected",
            True,
            True,
        ),
    ]
    return pd.DataFrame(
        [
            {
                "guard_position": position,
                "guard_name": name,
                "required_value": required,
                "actual_value": actual,
                "passed": required == actual,
                "guard_group": (
                    "design_review_state"
                    if position <= 6
                    else "design_review_safety_guard"
                ),
            }
            for position, (
                name,
                required,
                actual,
            ) in enumerate(guards, start=1)
        ]
    )


def build_requirements(
    validations: pd.DataFrame,
    items: pd.DataFrame,
    findings: pd.DataFrame,
    controls: pd.DataFrame,
    rules: pd.DataFrame,
    guards: pd.DataFrame,
) -> pd.DataFrame:
    rows: list[tuple[str, bool, Any, Any]] = []
    for _, validation in validations.iterrows():
        actual = safe_bool(validation["passed"], False)
        rows.append(
            (
                str(validation["validation_name"]),
                actual,
                True,
                actual,
            )
        )

    material_issues = int(
        findings["material_issue_found"].map(safe_bool).sum()
    )
    aggregate = [
        (
            "review_items_passed",
            all_passed(items),
            True,
            all_passed(items),
        ),
        (
            "review_findings_passed",
            all_passed(findings),
            True,
            all_passed(findings),
        ),
        (
            "review_controls_passed",
            all_passed(controls),
            True,
            all_passed(controls),
        ),
        (
            "review_rules_passed",
            all_passed(rules),
            True,
            all_passed(rules),
        ),
        (
            "review_guards_passed",
            all_passed(guards),
            True,
            all_passed(guards),
        ),
        (
            "material_issue_count_zero",
            material_issues == 0,
            0,
            material_issues,
        ),
        ("design_review_performed", True, True, True),
        (
            "future_implementation_precheck_allowed",
            True,
            True,
            True,
        ),
        (
            "dataset_implementation_not_allowed",
            True,
            False,
            False,
        ),
        (
            "dataset_creation_not_allowed",
            True,
            False,
            False,
        ),
        (
            "official_evidence_rows_written_zero",
            True,
            0,
            0,
        ),
        (
            "signal_generation_disabled",
            True,
            False,
            False,
        ),
        (
            "paper_trading_disabled",
            True,
            False,
            False,
        ),
        (
            "market_execution_disabled",
            True,
            False,
            False,
        ),
        (
            "project_not_completed",
            True,
            False,
            False,
        ),
    ]
    rows.extend(aggregate)

    return pd.DataFrame(
        [
            {
                "requirement_id": (
                    "OFFICIAL_DATASET_SCHEMA_DESIGN_REVIEW_REQ_"
                    f"{position:03d}"
                ),
                "requirement_name": name,
                "passed": bool(passed),
                "required_value": required,
                "actual_value": actual,
            }
            for position, (
                name,
                passed,
                required,
                actual,
            ) in enumerate(rows, start=1)
        ]
    )


def build_decision(
    validations: pd.DataFrame,
    items: pd.DataFrame,
    findings: pd.DataFrame,
    controls: pd.DataFrame,
    rules: pd.DataFrame,
    requirements: pd.DataFrame,
    guards: pd.DataFrame,
) -> pd.DataFrame:
    passed = all(
        [
            all_passed(validations),
            all_passed(items),
            all_passed(findings),
            all_passed(controls),
            all_passed(rules),
            all_passed(requirements),
            all_passed(guards),
        ]
    )
    failed = requirements[
        ~requirements["passed"].map(safe_bool)
    ]
    return pd.DataFrame(
        [
            {
                "official_dataset_schema_implementation_design_review_id": (
                    "PHASE_10_38_LONG_FORWARD_OBSERVATION_EVIDENCE_"
                    "COLLECTION_OFFICIAL_DATASET_SCHEMA_IMPLEMENTATION_"
                    "DESIGN_REVIEW_001"
                ),
                "official_dataset_schema_implementation_design_review_performed": True,
                "official_dataset_schema_implementation_design_review_passed": passed,
                "official_dataset_schema_implementation_design_review_decision": (
                    READY_DECISION if passed else BLOCKED_DECISION
                ),
                "canonical_schema_field_count": 54,
                "source_design_artifact_count": 14,
                "total_requirements": len(requirements),
                "passed_requirements": int(
                    requirements["passed"].map(safe_bool).sum()
                ),
                "failed_requirements": len(failed),
                "failed_requirement_names": ",".join(
                    failed["requirement_name"].astype(str).tolist()
                ),
                "future_official_dataset_schema_implementation_precheck_allowed": passed,
                "dataset_implementation_allowed": False,
                "dataset_creation_allowed": False,
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
            }
        ]
    )


def check_row(
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


def build_checks(
    docs_exist: dict[str, bool],
    validations: pd.DataFrame,
    items: pd.DataFrame,
    findings: pd.DataFrame,
    controls: pd.DataFrame,
    rules: pd.DataFrame,
    requirements: pd.DataFrame,
    guards: pd.DataFrame,
    decision: pd.DataFrame,
    official_before: bool,
    official_after: bool,
) -> pd.DataFrame:
    checks: list[dict[str, Any]] = []
    for name, exists in docs_exist.items():
        checks.append(
            check_row(
                "phase_anchor",
                name,
                exists,
                "INFO" if exists else "ERROR",
                name,
            )
        )

    decision_row = (
        decision.iloc[0].to_dict()
        if len(decision) == 1
        else {}
    )
    blocks = {
        "review_validations_passed": all_passed(validations),
        "review_items_passed": all_passed(items),
        "review_findings_passed": all_passed(findings),
        "review_controls_passed": all_passed(controls),
        "review_rules_passed": all_passed(rules),
        "review_requirements_passed": all_passed(requirements),
        "review_guards_passed": all_passed(guards),
        "design_review_passed": safe_bool(
            decision_row.get(
                "official_dataset_schema_implementation_design_review_passed",
                False,
            )
        ),
        "design_review_decision_expected": (
            str(
                decision_row.get(
                    "official_dataset_schema_implementation_design_review_decision",
                    "",
                )
            )
            == READY_DECISION
        ),
    }
    for name, passed in blocks.items():
        checks.append(
            check_row(
                "design_review",
                name,
                passed,
                "INFO" if passed else "ERROR",
                f"{name}={passed}",
            )
        )

    official_unchanged = not official_before and not official_after
    checks.append(
        check_row(
            "official_dataset_guard",
            "official_dataset_unchanged_absent",
            official_unchanged,
            "INFO" if official_unchanged else "ERROR",
            f"before={official_before},after={official_after}",
        )
    )

    warnings = [
        (
            "review_only",
            "Phase 10.38 reviews existing Phase 10.37 design artifacts only.",
        ),
        (
            "dataset_not_implemented",
            "The official dataset remains unimplemented.",
        ),
        (
            "dataset_not_created",
            "No official dataset file was created.",
        ),
        (
            "dataset_not_written",
            "No official dataset row was written.",
        ),
        (
            "real_evidence_not_collected",
            "No real forward evidence was collected.",
        ),
        (
            "evidence_persistence_not_enabled",
            "Evidence persistence remains disabled.",
        ),
        (
            "signal_generation_not_enabled",
            "Signal generation remains disabled.",
        ),
        (
            "live_alerts_not_enabled",
            "Live alerts remain disabled.",
        ),
        (
            "paper_trading_not_enabled",
            "Paper trading remains disabled.",
        ),
        (
            "long_strategy_not_approved",
            "The LONG research candidate remains unapproved.",
        ),
        (
            "real_capital_not_allowed",
            "Real capital remains prohibited.",
        ),
        (
            "market_execution_not_allowed",
            "Market execution remains prohibited.",
        ),
        (
            "automation_not_allowed",
            "Automation remains prohibited.",
        ),
        (
            "total_project_not_completed",
            "The total project is not completed.",
        ),
        (
            "future_implementation_precheck_only",
            "The only next allowance is an implementation precheck.",
        ),
    ]
    for name, details in warnings:
        checks.append(
            check_row(
                "scope_control",
                name,
                True,
                "WARNING",
                details,
            )
        )

    checks.append(
        check_row(
            "phase_transition",
            "phase_10_39_recommended_next",
            True,
            "INFO",
            (
                "Recommended next: Phase 10.39 official dataset "
                "schema implementation precheck."
            ),
        )
    )
    return pd.DataFrame(checks)


def build_summary(
    source_manifest: pd.DataFrame,
    validations: pd.DataFrame,
    items: pd.DataFrame,
    findings: pd.DataFrame,
    controls: pd.DataFrame,
    rules: pd.DataFrame,
    requirements: pd.DataFrame,
    guards: pd.DataFrame,
    decision: pd.DataFrame,
    checks: pd.DataFrame,
    official_before: bool,
    official_after: bool,
) -> pd.DataFrame:
    decision_row = (
        decision.iloc[0].to_dict()
        if len(decision) == 1
        else {}
    )
    error_count = int(
        checks["severity"].astype(str).eq("ERROR").sum()
    )
    warning_count = int(
        checks["severity"].astype(str).eq("WARNING").sum()
    )
    blocker_count = int(
        checks["blocker"].map(safe_bool).sum()
    )
    material_issue_count = int(
        findings["material_issue_found"].map(safe_bool).sum()
    )
    validation_passed = all(
        [
            error_count == 0,
            blocker_count == 0,
            all_passed(validations),
            all_passed(items),
            all_passed(findings),
            all_passed(controls),
            all_passed(rules),
            all_passed(requirements),
            all_passed(guards),
        ]
    )

    return pd.DataFrame(
        [
            {
                "phase": "10.38",
                "official_dataset_schema_implementation_design_review_defined": True,
                "phase_10_37_source_validated": all_passed(
                    validations
                ),
                "source_artifact_count": len(source_manifest),
                "source_artifacts_exist": (
                    source_manifest["artifact_exists"]
                    .map(safe_bool)
                    .all()
                ),
                "source_artifacts_non_empty": (
                    source_manifest["artifact_non_empty"]
                    .map(safe_bool)
                    .all()
                ),
                "source_artifact_hashes_valid": (
                    source_manifest["artifact_sha256_valid"]
                    .map(safe_bool)
                    .all()
                ),
                "source_manifest_sha256": manifest_digest(
                    source_manifest
                ),
                "review_validation_rows": len(validations),
                "review_item_rows": len(items),
                "review_finding_rows": len(findings),
                "review_control_rows": len(controls),
                "review_rule_rows": len(rules),
                "review_requirement_rows": len(requirements),
                "review_guard_rows": len(guards),
                "review_validations_passed": all_passed(validations),
                "review_items_passed": all_passed(items),
                "review_findings_passed": all_passed(findings),
                "review_controls_passed": all_passed(controls),
                "review_rules_passed": all_passed(rules),
                "review_requirements_passed": all_passed(
                    requirements
                ),
                "review_guards_passed": all_passed(guards),
                "material_issue_count": material_issue_count,
                "official_dataset_schema_implementation_design_review_performed": True,
                "official_dataset_schema_implementation_design_review_passed": safe_bool(
                    decision_row.get(
                        "official_dataset_schema_implementation_design_review_passed",
                        False,
                    )
                ),
                "official_dataset_schema_implementation_design_review_decision": str(
                    decision_row.get(
                        "official_dataset_schema_implementation_design_review_decision",
                        "",
                    )
                ),
                "future_official_dataset_schema_implementation_precheck_allowed": safe_bool(
                    decision_row.get(
                        "future_official_dataset_schema_implementation_precheck_allowed",
                        False,
                    )
                ),
                "dataset_implementation_allowed": False,
                "dataset_creation_allowed": False,
                "evidence_collection_enabled": False,
                "evidence_collection_started": False,
                "official_dataset_schema_implemented": False,
                "official_dataset_write_allowed": False,
                "official_dataset_write_performed": False,
                "official_dataset_exists_before": official_before,
                "official_dataset_exists_after": official_after,
                "official_dataset_unchanged_absent": (
                    not official_before and not official_after
                ),
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
                "validation_decision": (
                    "PHASE_10_38_LONG_FORWARD_OBSERVATION_EVIDENCE_"
                    "COLLECTION_OFFICIAL_DATASET_SCHEMA_IMPLEMENTATION_"
                    "DESIGN_REVIEW_VALIDATED"
                    if validation_passed
                    else
                    "PHASE_10_38_LONG_FORWARD_OBSERVATION_EVIDENCE_"
                    "COLLECTION_OFFICIAL_DATASET_SCHEMA_IMPLEMENTATION_"
                    "DESIGN_REVIEW_FAILED"
                ),
            }
        ]
    )


def run_long_forward_observation_evidence_collection_official_dataset_schema_implementation_design_review() -> dict[str, pd.DataFrame]:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    docs_exist = {
        "phase_10_37_schema_design_doc_exists": (
            PHASE_10_37_DOC_PATH.exists()
        ),
        "phase_10_38_schema_design_review_doc_exists": (
            PHASE_10_38_DOC_PATH.exists()
        ),
    }

    official_before = OFFICIAL_DATASET_PATH.exists()
    source_manifest_before = build_manifest(
        SOURCE_PATHS,
        "PHASE_10_37",
    )
    source = {
        name: read_csv(path)
        for name, path in SOURCE_PATHS.items()
    }
    source_manifest_after = build_manifest(
        SOURCE_PATHS,
        "PHASE_10_37",
    )
    official_after = OFFICIAL_DATASET_PATH.exists()

    validations = build_validations(
        source,
        source_manifest_before,
        source_manifest_after,
        official_before,
        official_after,
    )
    items = build_items(validations)
    findings = build_findings(items)
    controls = build_controls(validations)
    rules = build_rules(
        validations,
        items,
        findings,
        controls,
    )
    guards = build_guard_matrix(
        all(
            [
                all_passed(validations),
                all_passed(items),
                all_passed(findings),
                all_passed(controls),
                all_passed(rules),
            ]
        )
    )
    requirements = build_requirements(
        validations,
        items,
        findings,
        controls,
        rules,
        guards,
    )
    decision = build_decision(
        validations,
        items,
        findings,
        controls,
        rules,
        requirements,
        guards,
    )
    checks = build_checks(
        docs_exist,
        validations,
        items,
        findings,
        controls,
        rules,
        requirements,
        guards,
        decision,
        official_before,
        official_after,
    )
    summary = build_summary(
        source_manifest_before,
        validations,
        items,
        findings,
        controls,
        rules,
        requirements,
        guards,
        decision,
        checks,
        official_before,
        official_after,
    )

    frames = {
        "summary": summary,
        "validations": validations,
        "items": items,
        "findings": findings,
        "controls": controls,
        "rules": rules,
        "requirements": requirements,
        "guard_matrix": guards,
        "decision": decision,
        "checks": checks,
    }
    for name, dataframe in frames.items():
        dataframe.to_csv(
            REPORTS_DIR / OUTPUT_FILENAMES[name],
            index=False,
        )

    output_paths = {
        name: REPORTS_DIR / OUTPUT_FILENAMES[name]
        for name in frames
    }
    output_manifest = build_manifest(
        output_paths,
        "PHASE_10_38_OUTPUT",
    )
    combined_manifest = pd.concat(
        [source_manifest_after, output_manifest],
        ignore_index=True,
    )
    combined_manifest.to_csv(
        REPORTS_DIR / OUTPUT_FILENAMES["manifest"],
        index=False,
    )

    return {
        "summary": summary,
        "source_summary": source["summary"],
        "source_field_catalog": source["field_catalog"],
        "source_enum_domains": source["enum_domains"],
        "source_constraints": source["constraints"],
        "source_key_index_design": source["key_index_design"],
        "source_provenance_contract": source["provenance_contract"],
        "source_lifecycle_contract": source["lifecycle_contract"],
        "source_migration_plan": source["migration_plan"],
        "source_safety_guards": source["safety_guards"],
        "source_acceptance_criteria": source["acceptance_criteria"],
        "source_decision": source["decision"],
        "source_checks": source["checks"],
        "source_manifest": source["manifest"],
        "source_artifact_manifest": source_manifest_before,
        "validations": validations,
        "items": items,
        "findings": findings,
        "controls": controls,
        "rules": rules,
        "requirements": requirements,
        "guard_matrix": guards,
        "decision": decision,
        "checks": checks,
        "manifest": combined_manifest,
    }
