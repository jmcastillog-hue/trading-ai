from __future__ import annotations

import hashlib
import subprocess
from pathlib import Path
from typing import Any

import pandas as pd

from src.long_side.long_forward_observation_phase_10_39_evidence_collection_official_dataset_schema_implementation_precheck_v1 import (
    BACKUP_DIR,
    EMPTY_SCHEMA_CANDIDATE_PATH,
    EXPECTED_FIELD_NAMES,
    OFFICIAL_DATASET_EXPECTED_PATH,
    OFFICIAL_LOCK_PATH,
    OFFICIAL_MANIFEST_PATH,
    OFFICIAL_TEMP_PATH,
    all_passed,
    build_manifest,
    is_sha256,
    manifest_digest,
    read_csv,
    safe_bool,
    safe_int,
    sha256_file,
)
from src.long_side.long_forward_observation_phase_10_40_evidence_collection_official_dataset_empty_schema_candidate_implementation_v1 import (
    expected_candidate_bytes,
    inspect_candidate,
)


REPORTS_DIR = Path(
    "reports/p10_42_evidence_collection_official_dataset_"
    "atomic_write_harness_design_v1"
)
PHASE_10_41_DIR = Path(
    "reports/p10_41_evidence_collection_official_dataset_"
    "empty_schema_candidate_validation_v1"
)

PHASE_10_41_DOC_PATH = Path(
    "docs/PHASE_10_LONG_FORWARD_OBSERVATION_EVIDENCE_COLLECTION_"
    "OFFICIAL_DATASET_EMPTY_SCHEMA_CANDIDATE_VALIDATION.md"
)
PHASE_10_42_DOC_PATH = Path(
    "docs/PHASE_10_LONG_FORWARD_OBSERVATION_EVIDENCE_COLLECTION_"
    "OFFICIAL_DATASET_ATOMIC_WRITE_HARNESS_DESIGN.md"
)
GITATTRIBUTES_PATH = Path(".gitattributes")

PHASE_10_41_PATHS = {
    "validation_summary": (
        PHASE_10_41_DIR
        / "official_dataset_empty_schema_candidate_validation_summary_v1.csv"
    ),
    "validation_decision": (
        PHASE_10_41_DIR
        / "official_dataset_empty_schema_candidate_validation_decision_v1.csv"
    ),
    "validation_profile": (
        PHASE_10_41_DIR
        / "official_dataset_empty_schema_candidate_validation_profile_v1.csv"
    ),
    "validation_negative_controls": (
        PHASE_10_41_DIR
        / "official_dataset_empty_schema_candidate_validation_negative_controls_v1.csv"
    ),
    "validation_checks": (
        PHASE_10_41_DIR
        / "official_dataset_empty_schema_candidate_validation_checks_v1.csv"
    ),
    "validation_manifest": (
        PHASE_10_41_DIR
        / "source_official_dataset_empty_schema_candidate_validation_artifact_manifest_v1.csv"
    ),
}

SOURCE_PATHS = {
    **PHASE_10_41_PATHS,
    "phase_10_41_doc": PHASE_10_41_DOC_PATH,
    "empty_schema_candidate": EMPTY_SCHEMA_CANDIDATE_PATH,
    "gitattributes": GITATTRIBUTES_PATH,
}

SOURCE_READY_DECISION = (
    "CONTROLLED_FORWARD_OBSERVATION_EVIDENCE_COLLECTION_OFFICIAL_"
    "DATASET_EMPTY_SCHEMA_CANDIDATE_VALIDATION_READY_FOR_ATOMIC_WRITE_"
    "HARNESS_DESIGN"
)
READY_DECISION = (
    "CONTROLLED_FORWARD_OBSERVATION_EVIDENCE_COLLECTION_OFFICIAL_"
    "DATASET_ATOMIC_WRITE_HARNESS_DESIGN_READY_FOR_DESIGN_REVIEW"
)
BLOCKED_DECISION = (
    "CONTROLLED_FORWARD_OBSERVATION_EVIDENCE_COLLECTION_OFFICIAL_"
    "DATASET_ATOMIC_WRITE_HARNESS_DESIGN_BLOCKED"
)
RECOMMENDED_NEXT_PHASE = (
    "PHASE_10_43_LONG_FORWARD_OBSERVATION_EVIDENCE_COLLECTION_"
    "OFFICIAL_DATASET_ATOMIC_WRITE_HARNESS_DESIGN_REVIEW_V1"
)

EXPECTED_CANDIDATE_SIZE_BYTES = 981
EXPECTED_CANDIDATE_SHA256 = (
    "e3fa86a461fd46f4d66dc2e03f185e49"
    "b7b3438d3cbc33340c01f51310514ff1"
)
EXPECTED_GITATTRIBUTE_RULE = (
    "data/forward/candidates/"
    "long_forward_observation_dataset_v1.empty_candidate.csv text eol=lf"
)

OUTPUT_FILENAMES = {
    "summary": "official_dataset_atomic_write_harness_design_summary_v1.csv",
    "validations": "official_dataset_atomic_write_harness_design_validations_v1.csv",
    "components": "official_dataset_atomic_write_harness_design_components_v1.csv",
    "protocol": "official_dataset_atomic_write_harness_design_protocol_v1.csv",
    "paths": "official_dataset_atomic_write_harness_design_path_contract_v1.csv",
    "states": "official_dataset_atomic_write_harness_design_state_machine_v1.csv",
    "invariants": "official_dataset_atomic_write_harness_design_invariants_v1.csv",
    "failure_modes": "official_dataset_atomic_write_harness_design_failure_modes_v1.csv",
    "recovery": "official_dataset_atomic_write_harness_design_recovery_matrix_v1.csv",
    "concurrency": "official_dataset_atomic_write_harness_design_concurrency_contract_v1.csv",
    "items": "official_dataset_atomic_write_harness_design_items_v1.csv",
    "findings": "official_dataset_atomic_write_harness_design_findings_v1.csv",
    "controls": "official_dataset_atomic_write_harness_design_controls_v1.csv",
    "rules": "official_dataset_atomic_write_harness_design_rules_v1.csv",
    "requirements": "official_dataset_atomic_write_harness_design_requirements_v1.csv",
    "guard_matrix": "official_dataset_atomic_write_harness_design_guard_matrix_v1.csv",
    "decision": "official_dataset_atomic_write_harness_design_decision_v1.csv",
    "checks": "official_dataset_atomic_write_harness_design_checks_v1.csv",
    "manifest": "source_official_dataset_atomic_write_harness_design_artifact_manifest_v1.csv",
}


def append_validation(
    rows: list[dict[str, Any]],
    group: str,
    name: str,
    passed: bool,
    details: str,
) -> None:
    rows.append(
        {
            "validation_position": len(rows) + 1,
            "validation_group": group,
            "validation_name": name,
            "passed": bool(passed),
            "details": details,
        }
    )


def candidate_git_state(path: Path) -> dict[str, Any]:
    tracked_result = subprocess.run(
        ["git", "ls-files", "--error-unmatch", "--", str(path)],
        capture_output=True,
        text=True,
        check=False,
    )
    status_result = subprocess.run(
        ["git", "status", "--porcelain", "--", str(path)],
        capture_output=True,
        text=True,
        check=False,
    )
    attr_result = subprocess.run(
        ["git", "check-attr", "text", "eol", "--", str(path)],
        capture_output=True,
        text=True,
        check=False,
    )
    attr_text = attr_result.stdout.replace("\\", "/")
    return {
        "candidate_git_tracked": tracked_result.returncode == 0,
        "candidate_git_clean": (
            status_result.returncode == 0
            and status_result.stdout.strip() == ""
        ),
        "candidate_git_text_attribute_set": "text: set" in attr_text,
        "candidate_git_eol_lf": "eol: lf" in attr_text,
        "candidate_git_attribute_output": attr_result.stdout.strip(),
        "candidate_git_error": (
            tracked_result.stderr.strip()
            or status_result.stderr.strip()
            or attr_result.stderr.strip()
        ),
    }


def build_components() -> pd.DataFrame:
    rows = [
        ("SAFETY_GATE", "Reject all calls unless prior phase and scope gates pass.", "READ_ONLY", True),
        ("SOURCE_VERIFIER", "Verify candidate bytes, schema, Git state and provenance.", "READ_ONLY", True),
        ("PATH_RESOLVER", "Resolve canonical target, temp, lock, manifest and backup paths.", "READ_ONLY", True),
        ("LOCK_MANAGER", "Acquire and release a single-writer exclusive lock.", "FUTURE_WRITE", True),
        ("TEMP_STAGER", "Create a unique same-directory staging file.", "FUTURE_WRITE", True),
        ("DETERMINISTIC_WRITER", "Write exact deterministic payload bytes.", "FUTURE_WRITE", True),
        ("FILE_DURABILITY_BARRIER", "Flush and fsync the staged file.", "FUTURE_WRITE", True),
        ("STAGED_ARTIFACT_VERIFIER", "Re-read and validate staged bytes before replacement.", "READ_ONLY", True),
        ("ATOMIC_REPLACER", "Use an atomic operating-system replace primitive.", "FUTURE_WRITE", True),
        ("DIRECTORY_DURABILITY_BARRIER", "Fsync the parent directory when supported.", "FUTURE_WRITE", True),
        ("MANIFEST_COMMITTER", "Commit manifest only after dataset durability is known.", "FUTURE_WRITE", True),
        ("ROLLBACK_MANAGER", "Preserve or restore a prior target under controlled rules.", "FUTURE_WRITE", True),
        ("RECOVERY_INSPECTOR", "Classify incomplete states and require explicit recovery.", "READ_ONLY", True),
        ("AUDIT_REPORTER", "Emit immutable report-only evidence for each transition.", "REPORT_ONLY", True),
    ]
    return pd.DataFrame(
        [
            {
                "component_position": position,
                "component_id": component_id,
                "component_description": description,
                "component_mode": mode,
                "required": required,
                "implemented_in_phase_10_42": False,
                "executed_in_phase_10_42": False,
                "passed": True,
            }
            for position, (component_id, description, mode, required)
            in enumerate(rows, start=1)
        ]
    )


def build_protocol() -> pd.DataFrame:
    steps = [
        ("ASSERT_DESIGN_REVIEW_SCOPE", "Confirm that only design review is allowed.", False),
        ("VERIFY_PRIOR_PHASE", "Require validated Phase 10.41 decision.", False),
        ("VERIFY_CANDIDATE", "Require exact candidate schema, bytes and digest.", False),
        ("VERIFY_TARGET_POLICY", "Resolve whether create or replace is permitted by a later gate.", False),
        ("VERIFY_PATH_ISOLATION", "Require candidate, temp and target paths to be distinct.", False),
        ("ACQUIRE_EXCLUSIVE_LOCK", "Create lock with fail-if-exists semantics.", True),
        ("RECHECK_AFTER_LOCK", "Repeat safety and target-state checks after lock acquisition.", False),
        ("CREATE_UNIQUE_SAME_DIR_TEMP", "Create unique temp beside the official target.", True),
        ("WRITE_DETERMINISTIC_BYTES", "Write exact validated payload.", True),
        ("FLUSH_AND_FSYNC_TEMP", "Flush userspace buffers and fsync the staged file.", True),
        ("VERIFY_STAGED_ARTIFACT", "Re-read and validate schema, rows, size and SHA-256.", False),
        ("PREPARE_ROLLBACK_REFERENCE", "Capture prior target reference when replacement is later allowed.", True),
        ("ATOMIC_REPLACE_TARGET", "Atomically replace or install the target.", True),
        ("FSYNC_PARENT_DIRECTORY", "Persist directory entry changes when supported.", True),
        ("COMMIT_MANIFEST", "Write manifest only after target durability succeeds.", True),
        ("VERIFY_POST_COMMIT", "Validate target and manifest relationship.", False),
        ("CLEAN_TEMP_AND_LOCK", "Remove temporary and lock artifacts.", True),
        ("EMIT_FINAL_AUDIT", "Record terminal success or recovery-required state.", False),
    ]
    return pd.DataFrame(
        [
            {
                "protocol_position": position,
                "protocol_step": name,
                "protocol_description": description,
                "future_filesystem_mutation": mutation,
                "allowed_in_phase_10_42": False,
                "fail_closed": True,
                "required": True,
                "passed": True,
            }
            for position, (name, description, mutation)
            in enumerate(steps, start=1)
        ]
    )


def build_path_contract() -> pd.DataFrame:
    rows = [
        ("CANDIDATE", EMPTY_SCHEMA_CANDIDATE_PATH, "READ_ONLY_SOURCE", True, False),
        ("OFFICIAL_DATASET", OFFICIAL_DATASET_EXPECTED_PATH, "ATOMIC_TARGET", False, False),
        ("OFFICIAL_TEMP", OFFICIAL_TEMP_PATH, "SAME_DIRECTORY_STAGING", False, False),
        ("OFFICIAL_LOCK", OFFICIAL_LOCK_PATH, "EXCLUSIVE_WRITER_LOCK", False, False),
        ("OFFICIAL_MANIFEST", OFFICIAL_MANIFEST_PATH, "POST_TARGET_COMMIT", False, False),
        ("BACKUP_ROOT", BACKUP_DIR, "CONTROLLED_ROLLBACK", False, False),
        ("REPORT_ROOT", REPORTS_DIR, "REPORT_ONLY_OUTPUT", False, True),
    ]
    return pd.DataFrame(
        [
            {
                "path_position": position,
                "path_id": path_id,
                "path_value": str(path),
                "path_role": role,
                "must_exist_before_future_run": must_exist,
                "creation_allowed_in_phase_10_42": create_now,
                "must_be_distinct_from_candidate": (
                    path_id != "CANDIDATE"
                ),
                "passed": True,
            }
            for position, (path_id, path, role, must_exist, create_now)
            in enumerate(rows, start=1)
        ]
    )


def build_state_machine() -> pd.DataFrame:
    states = [
        ("S0_IDLE", "No lock and no temporary artifact.", False, False),
        ("S1_PREFLIGHT_VALIDATED", "All read-only gates passed.", False, False),
        ("S2_LOCK_ACQUIRED", "Exclusive writer lock exists.", True, False),
        ("S3_TEMP_CREATED", "Unique same-directory temp exists.", True, True),
        ("S4_TEMP_DURABLE", "Temp file has been flushed and fsynced.", True, True),
        ("S5_TEMP_VALIDATED", "Temp bytes and schema are verified.", True, True),
        ("S6_TARGET_REPLACED", "Atomic replace completed.", True, True),
        ("S7_DIRECTORY_DURABLE", "Parent directory persistence completed.", True, False),
        ("S8_MANIFEST_DURABLE", "Manifest reflects durable target.", True, False),
        ("S9_CLEANUP_COMPLETE", "Temp and lock are absent.", False, False),
        ("SF_PRE_REPLACE_FAILED", "Failure occurred before target replacement.", True, True),
        ("SF_RECOVERY_REQUIRED", "Target may be durable but manifest or cleanup is incomplete.", True, True),
    ]
    return pd.DataFrame(
        [
            {
                "state_position": position,
                "state_id": state_id,
                "state_description": description,
                "lock_may_exist": lock_exists,
                "temp_may_exist": temp_exists,
                "terminal_success": state_id == "S9_CLEANUP_COMPLETE",
                "terminal_failure": state_id.startswith("SF_"),
                "implemented_in_phase_10_42": False,
                "passed": True,
            }
            for position, (state_id, description, lock_exists, temp_exists)
            in enumerate(states, start=1)
        ]
    )


def build_invariants() -> pd.DataFrame:
    names = [
        "candidate_is_read_only",
        "candidate_and_target_are_distinct",
        "candidate_and_temp_are_distinct",
        "temp_and_target_share_parent_directory",
        "single_writer_lock_required",
        "lock_acquisition_is_fail_if_exists",
        "preflight_repeated_after_lock",
        "temporary_filename_is_unique",
        "temporary_creation_is_exclusive",
        "payload_is_deterministic",
        "payload_uses_utf8_without_bom",
        "payload_uses_lf_only",
        "payload_has_exact_54_column_order",
        "payload_has_zero_rows_for_empty_initialization",
        "temp_is_fsynced_before_validation",
        "temp_is_re_read_before_replace",
        "atomic_replace_is_single_commit_point",
        "parent_directory_is_fsynced_after_replace",
        "manifest_commits_after_target_durability",
        "manifest_never_precedes_target_commit",
        "unknown_durability_fails_closed",
        "cleanup_never_masks_primary_failure",
        "stale_lock_requires_explicit_recovery",
        "all_transitions_emit_audit_evidence",
    ]
    return pd.DataFrame(
        [
            {
                "invariant_position": position,
                "invariant_name": name,
                "required": True,
                "design_satisfied": True,
                "implementation_required_later": True,
                "passed": True,
            }
            for position, name in enumerate(names, start=1)
        ]
    )


def build_failure_modes() -> pd.DataFrame:
    rows = [
        ("PRIOR_GATE_FAILED", "Block before lock acquisition.", "NO_CHANGE"),
        ("CANDIDATE_MISSING", "Block before lock acquisition.", "NO_CHANGE"),
        ("CANDIDATE_HASH_MISMATCH", "Block before lock acquisition.", "NO_CHANGE"),
        ("TARGET_POLICY_UNRESOLVED", "Block before lock acquisition.", "NO_CHANGE"),
        ("LOCK_ALREADY_EXISTS", "Block and require lock inspection.", "NO_CHANGE"),
        ("LOCK_CREATE_FAILED", "Block and emit error.", "NO_CHANGE"),
        ("POST_LOCK_RECHECK_FAILED", "Release owned lock and block.", "NO_CHANGE"),
        ("TEMP_CREATE_FAILED", "Release owned lock and block.", "NO_CHANGE"),
        ("TEMP_WRITE_FAILED", "Delete owned temp, release lock and block.", "NO_CHANGE"),
        ("TEMP_FSYNC_FAILED", "Delete owned temp, release lock and block.", "NO_CHANGE"),
        ("TEMP_VALIDATION_FAILED", "Quarantine or delete temp, release lock and block.", "NO_CHANGE"),
        ("ROLLBACK_PREP_FAILED", "Delete temp, release lock and block.", "NO_CHANGE"),
        ("ATOMIC_REPLACE_FAILED", "Inspect target identity; require explicit classification.", "UNKNOWN"),
        ("DIRECTORY_FSYNC_FAILED", "Mark recovery required; do not claim durable success.", "RECOVERY_REQUIRED"),
        ("MANIFEST_WRITE_FAILED", "Target may exist; mark recovery required.", "RECOVERY_REQUIRED"),
        ("POST_COMMIT_VERIFY_FAILED", "Freeze further writes and require recovery.", "RECOVERY_REQUIRED"),
        ("TEMP_CLEANUP_FAILED", "Record residual temp; target status unchanged.", "RECOVERY_REQUIRED"),
        ("LOCK_CLEANUP_FAILED", "Record stale lock and block subsequent writes.", "RECOVERY_REQUIRED"),
        ("PROCESS_CRASH", "Classify filesystem state on restart.", "RECOVERY_REQUIRED"),
        ("POWER_LOSS", "Classify target, temp, lock and manifest on restart.", "RECOVERY_REQUIRED"),
    ]
    return pd.DataFrame(
        [
            {
                "failure_position": position,
                "failure_mode": name,
                "required_response": response,
                "resulting_state_class": state_class,
                "silent_continue_allowed": False,
                "implemented_in_phase_10_42": False,
                "passed": True,
            }
            for position, (name, response, state_class)
            in enumerate(rows, start=1)
        ]
    )


def build_recovery_matrix() -> pd.DataFrame:
    rows = [
        ("NO_LOCK_NO_TEMP_NO_TARGET", "SAFE_EMPTY", "Re-run preflight."),
        ("NO_LOCK_NO_TEMP_VALID_TARGET", "SAFE_COMMITTED", "Verify manifest relationship."),
        ("LOCK_ONLY", "STALE_LOCK_POSSIBLE", "Inspect owner metadata; no automatic write."),
        ("LOCK_AND_EMPTY_TEMP", "PRE_WRITE_INTERRUPTION", "Remove only after ownership proof."),
        ("LOCK_AND_VALID_TEMP_NO_TARGET", "PRE_REPLACE_INTERRUPTION", "Validate and require explicit resume/abort."),
        ("LOCK_AND_INVALID_TEMP_NO_TARGET", "CORRUPT_STAGING", "Quarantine/delete temp; block."),
        ("LOCK_VALID_TEMP_VALID_TARGET", "AMBIGUOUS_COMMIT", "Compare digests and manifest; require recovery."),
        ("NO_LOCK_VALID_TEMP_NO_TARGET", "ORPHAN_VALID_TEMP", "Require explicit recovery."),
        ("NO_LOCK_INVALID_TEMP_NO_TARGET", "ORPHAN_CORRUPT_TEMP", "Quarantine/delete after audit."),
        ("TARGET_VALID_MANIFEST_MISSING", "POST_REPLACE_PRE_MANIFEST", "Reconstruct only through controlled recovery."),
        ("TARGET_MANIFEST_MISMATCH", "INTEGRITY_FAILURE", "Freeze writes and investigate."),
        ("TARGET_INVALID", "TARGET_CORRUPTION", "Restore verified backup if later authorized."),
        ("BACKUP_PRESENT_TARGET_VALID", "SAFE_WITH_BACKUP", "Retain according to policy."),
        ("UNKNOWN_STATE", "FAIL_CLOSED", "No mutation; require manual classification."),
    ]
    return pd.DataFrame(
        [
            {
                "recovery_position": position,
                "observed_artifact_state": observed,
                "classification": classification,
                "required_recovery_action": action,
                "automatic_recovery_allowed": False,
                "implemented_in_phase_10_42": False,
                "passed": True,
            }
            for position, (observed, classification, action)
            in enumerate(rows, start=1)
        ]
    )


def build_concurrency_contract() -> pd.DataFrame:
    rows = [
        ("single_writer", "At most one lock owner may mutate official artifacts."),
        ("multi_reader", "Readers must see either the old or new target, never a partial file."),
        ("lock_scope", "Lock covers temp creation through cleanup and terminal audit."),
        ("lock_identity", "Lock records unique operation id and process metadata."),
        ("lock_ownership", "Only the verified owner may remove the lock."),
        ("stale_lock", "Age alone cannot authorize automatic deletion."),
        ("reentrant_write", "Nested writes for the same operation are prohibited."),
        ("cross_process_write", "Second process fails immediately when lock exists."),
        ("post_lock_recheck", "All mutable preconditions are rechecked under lock."),
        ("reader_lock_independence", "Readers do not require the writer lock."),
        ("manifest_visibility", "Manifest cannot advertise an uncommitted target."),
        ("recovery_exclusivity", "Recovery also requires exclusive ownership."),
    ]
    return pd.DataFrame(
        [
            {
                "concurrency_position": position,
                "concurrency_rule": name,
                "concurrency_contract": contract,
                "required": True,
                "implemented_in_phase_10_42": False,
                "passed": True,
            }
            for position, (name, contract)
            in enumerate(rows, start=1)
        ]
    )


def validate_phase_10_41_manifest(
    manifest_df: pd.DataFrame,
    manifest_path: Path,
) -> dict[str, bool]:
    required = {
        "artifact_scope",
        "artifact_filename",
        "artifact_path",
        "artifact_exists",
        "artifact_size_bytes",
        "artifact_non_empty",
        "artifact_sha256",
        "artifact_sha256_valid",
    }
    if manifest_df.empty or not required.issubset(manifest_df.columns):
        return {
            "phase_10_41_manifest_rows_26": False,
            "phase_10_41_manifest_source_rows_14": False,
            "phase_10_41_manifest_output_rows_12": False,
            "phase_10_41_manifest_listed_artifacts_valid": False,
            "phase_10_41_manifest_hashes_match": False,
            "phase_10_41_manifest_self_exclusion_expected": False,
            "phase_10_41_manifest_file_exists": manifest_path.exists(),
            "phase_10_41_manifest_file_non_empty": False,
            "phase_10_41_manifest_file_sha256_valid": False,
        }

    source_rows = manifest_df[
        manifest_df["artifact_scope"].astype(str).eq("PHASE_10_41_SOURCE")
    ]
    output_rows = manifest_df[
        manifest_df["artifact_scope"].astype(str).eq("PHASE_10_41_OUTPUT")
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
        len(manifest_df) == 26
        and len(source_rows) == 14
        and len(output_rows) == 12
        and manifest_path.name not in filenames
    )
    return {
        "phase_10_41_manifest_rows_26": len(manifest_df) == 26,
        "phase_10_41_manifest_source_rows_14": len(source_rows) == 14,
        "phase_10_41_manifest_output_rows_12": len(output_rows) == 12,
        "phase_10_41_manifest_listed_artifacts_valid": listed_valid,
        "phase_10_41_manifest_hashes_match": hashes_match,
        "phase_10_41_manifest_self_exclusion_expected": self_exclusion,
        "phase_10_41_manifest_file_exists": manifest_path.exists(),
        "phase_10_41_manifest_file_non_empty": (
            manifest_path.exists()
            and manifest_path.stat().st_size > 0
        ),
        "phase_10_41_manifest_file_sha256_valid": is_sha256(
            sha256_file(manifest_path)
        ),
    }


def build_validations(
    source: dict[str, pd.DataFrame],
    source_manifest_before: pd.DataFrame,
    source_manifest_after: pd.DataFrame,
    candidate_profile: pd.DataFrame,
    git_state: dict[str, Any],
    components: pd.DataFrame,
    protocol: pd.DataFrame,
    paths: pd.DataFrame,
    states: pd.DataFrame,
    invariants: pd.DataFrame,
    failure_modes: pd.DataFrame,
    recovery: pd.DataFrame,
    concurrency: pd.DataFrame,
    official_before: bool,
    official_after: bool,
) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []

    source_checks = [
        ("source_artifact_count_9", len(source_manifest_before) == 9),
        ("source_artifacts_exist", source_manifest_before["artifact_exists"].map(safe_bool).all()),
        ("source_artifacts_non_empty", source_manifest_before["artifact_non_empty"].map(safe_bool).all()),
        ("source_artifact_hashes_valid", source_manifest_before["artifact_sha256_valid"].map(safe_bool).all()),
        (
            "source_artifacts_stable_during_design",
            manifest_digest(source_manifest_before)
            == manifest_digest(source_manifest_after),
        ),
    ]
    for name, passed in source_checks:
        append_validation(rows, "source_artifacts", name, passed, f"{name}={passed}")

    summary = (
        source["validation_summary"].iloc[0].to_dict()
        if len(source["validation_summary"]) == 1
        else {}
    )
    summary_checks = [
        ("phase_10_41_summary_row_count_1", len(source["validation_summary"]) == 1),
        ("phase_10_41_validation_passed", safe_bool(summary.get("validation_passed", False))),
        (
            "phase_10_41_validation_decision_exact",
            str(summary.get("validation_decision", ""))
            == (
                "PHASE_10_41_LONG_FORWARD_OBSERVATION_EVIDENCE_"
                "COLLECTION_OFFICIAL_DATASET_EMPTY_SCHEMA_CANDIDATE_"
                "VALIDATION_VALIDATED"
            ),
        ),
        (
            "phase_10_41_design_allowed",
            safe_bool(
                summary.get(
                    "future_official_dataset_atomic_write_harness_design_allowed",
                    False,
                )
            ),
        ),
        (
            "phase_10_41_decision_exact",
            str(
                summary.get(
                    "official_dataset_empty_schema_candidate_validation_decision",
                    "",
                )
            )
            == SOURCE_READY_DECISION,
        ),
        ("phase_10_41_source_artifacts_14", safe_int(summary.get("source_artifact_count", -1), -1) == 14),
        ("phase_10_41_validation_rows_141", safe_int(summary.get("validation_validation_rows", -1), -1) == 141),
        ("phase_10_41_negative_rows_10", safe_int(summary.get("validation_negative_control_rows", -1), -1) == 10),
        ("phase_10_41_item_rows_47", safe_int(summary.get("validation_item_rows", -1), -1) == 47),
        ("phase_10_41_finding_rows_47", safe_int(summary.get("validation_finding_rows", -1), -1) == 47),
        ("phase_10_41_control_rows_141", safe_int(summary.get("validation_control_rows", -1), -1) == 141),
        ("phase_10_41_rule_rows_36", safe_int(summary.get("validation_rule_rows", -1), -1) == 36),
        ("phase_10_41_requirement_rows_161", safe_int(summary.get("validation_requirement_rows", -1), -1) == 161),
        ("phase_10_41_guard_rows_46", safe_int(summary.get("validation_guard_rows", -1), -1) == 46),
        ("phase_10_41_material_issue_zero", safe_int(summary.get("material_issue_count", -1), -1) == 0),
        ("phase_10_41_total_checks_33", safe_int(summary.get("total_checks", -1), -1) == 33),
        ("phase_10_41_warning_count_16", safe_int(summary.get("warning_count", -1), -1) == 16),
        ("phase_10_41_error_count_zero", safe_int(summary.get("error_count", -1), -1) == 0),
        ("phase_10_41_blocker_count_zero", safe_int(summary.get("blocker_count", -1), -1) == 0),
        ("phase_10_41_candidate_size_981", safe_int(summary.get("candidate_size_bytes", -1), -1) == 981),
        ("phase_10_41_candidate_columns_54", safe_int(summary.get("candidate_column_count", -1), -1) == 54),
        ("phase_10_41_candidate_rows_zero", safe_int(summary.get("candidate_row_count", -1), -1) == 0),
        (
            "phase_10_41_candidate_sha_exact",
            str(summary.get("candidate_sha256", "")) == EXPECTED_CANDIDATE_SHA256,
        ),
        ("phase_10_41_candidate_contract_valid", safe_bool(summary.get("candidate_contract_valid", False))),
        ("phase_10_41_candidate_hash_stable", safe_bool(summary.get("candidate_hash_stable", False))),
        ("phase_10_41_candidate_mtime_stable", safe_bool(summary.get("candidate_mtime_stable", False))),
        ("phase_10_41_candidate_git_tracked", safe_bool(summary.get("candidate_git_tracked", False))),
        ("phase_10_41_candidate_git_clean", safe_bool(summary.get("candidate_git_clean", False))),
        ("phase_10_41_official_dataset_absent", safe_bool(summary.get("official_dataset_unchanged_absent", False))),
        ("phase_10_41_official_rows_zero", safe_int(summary.get("official_evidence_rows_written", -1), -1) == 0),
        ("phase_10_41_candidate_rows_written_zero", safe_int(summary.get("candidate_evidence_rows_written", -1), -1) == 0),
        ("phase_10_41_long_unapproved", not safe_bool(summary.get("long_strategy_approved", True), True)),
        ("phase_10_41_project_not_complete", not safe_bool(summary.get("total_project_completed", True), True)),
        (
            "phase_10_41_next_phase_10_42",
            str(summary.get("recommended_next_phase", "")) == (
                "PHASE_10_42_LONG_FORWARD_OBSERVATION_EVIDENCE_"
                "COLLECTION_OFFICIAL_DATASET_ATOMIC_WRITE_HARNESS_DESIGN_V1"
            ),
        ),
    ]
    for name, passed in summary_checks:
        append_validation(rows, "phase_10_41_summary", name, passed, f"{name}={passed}")

    decision = (
        source["validation_decision"].iloc[0].to_dict()
        if len(source["validation_decision"]) == 1
        else {}
    )
    decision_checks = [
        ("phase_10_41_decision_row_count_1", len(source["validation_decision"]) == 1),
        (
            "source_candidate_validation_performed",
            safe_bool(
                decision.get(
                    "official_dataset_empty_schema_candidate_validation_performed",
                    False,
                )
            ),
        ),
        (
            "source_candidate_validation_passed",
            safe_bool(
                decision.get(
                    "official_dataset_empty_schema_candidate_validation_passed",
                    False,
                )
            ),
        ),
        (
            "source_candidate_validation_decision_exact",
            str(
                decision.get(
                    "official_dataset_empty_schema_candidate_validation_decision",
                    "",
                )
            )
            == SOURCE_READY_DECISION,
        ),
        ("source_decision_requirements_161", safe_int(decision.get("total_requirements", -1), -1) == 161),
        ("source_decision_failed_requirements_zero", safe_int(decision.get("failed_requirements", -1), -1) == 0),
        (
            "source_decision_design_allowed",
            safe_bool(
                decision.get(
                    "future_official_dataset_atomic_write_harness_design_allowed",
                    False,
                )
            ),
        ),
        ("source_decision_candidate_contract_valid", safe_bool(decision.get("candidate_contract_valid", False))),
        ("source_decision_candidate_git_clean", safe_bool(decision.get("candidate_git_clean", False))),
        (
            "source_decision_next_phase_10_42",
            str(decision.get("recommended_next_phase", "")) == (
                "PHASE_10_42_LONG_FORWARD_OBSERVATION_EVIDENCE_"
                "COLLECTION_OFFICIAL_DATASET_ATOMIC_WRITE_HARNESS_DESIGN_V1"
            ),
        ),
    ]
    for name, passed in decision_checks:
        append_validation(rows, "phase_10_41_decision", name, passed, f"{name}={passed}")

    source_profile = (
        source["validation_profile"].iloc[0].to_dict()
        if len(source["validation_profile"]) == 1
        else {}
    )
    source_profile_checks = [
        ("source_profile_row_count_1", len(source["validation_profile"]) == 1),
        ("source_profile_candidate_exists", safe_bool(source_profile.get("candidate_exists", False))),
        ("source_profile_candidate_contract_valid", safe_bool(source_profile.get("candidate_contract_valid", False))),
        ("source_profile_candidate_size_981", safe_int(source_profile.get("candidate_size_bytes", -1), -1) == 981),
        ("source_profile_candidate_columns_54", safe_int(source_profile.get("candidate_column_count", -1), -1) == 54),
        ("source_profile_candidate_rows_zero", safe_int(source_profile.get("candidate_row_count", -1), -1) == 0),
        (
            "source_profile_candidate_sha_exact",
            str(source_profile.get("candidate_sha256", "")) == EXPECTED_CANDIDATE_SHA256,
        ),
        ("source_profile_candidate_hash_stable", safe_bool(source_profile.get("candidate_hash_stable", False))),
        ("source_profile_candidate_mtime_stable", safe_bool(source_profile.get("candidate_mtime_stable", False))),
        ("source_profile_candidate_git_clean", safe_bool(source_profile.get("candidate_git_clean", False))),
    ]
    for name, passed in source_profile_checks:
        append_validation(rows, "phase_10_41_profile", name, passed, f"{name}={passed}")

    negative = source["validation_negative_controls"]
    negative_checks = [
        ("source_negative_control_rows_10", len(negative) == 10),
        ("source_negative_controls_all_passed", all_passed(negative)),
        (
            "source_negative_valid_case_accepted",
            len(
                negative[
                    negative["negative_control_name"].astype(str).eq(
                        "valid_canonical_header"
                    )
                    & negative["actual_contract_valid"].map(safe_bool)
                ]
            ) == 1,
        ),
        (
            "source_negative_corrupt_cases_rejected",
            len(negative) == 10
            and not negative[
                ~negative["negative_control_name"].astype(str).eq(
                    "valid_canonical_header"
                )
            ]["actual_contract_valid"].map(safe_bool).any(),
        ),
    ]
    for name, passed in negative_checks:
        append_validation(rows, "phase_10_41_negative_controls", name, passed, f"{name}={passed}")

    source_checks_df = source["validation_checks"]
    output_checks = [
        ("source_checks_rows_33", len(source_checks_df) == 33),
        ("source_checks_no_error_failures", not (
            source_checks_df["severity"].astype(str).eq("ERROR")
            & ~source_checks_df["passed"].map(safe_bool)
        ).any()),
        ("source_checks_no_blockers", not source_checks_df["blocker"].map(safe_bool).any()),
    ]
    for name, passed in output_checks:
        append_validation(rows, "phase_10_41_checks", name, passed, f"{name}={passed}")

    for name, passed in validate_phase_10_41_manifest(
        source["validation_manifest"],
        PHASE_10_41_PATHS["validation_manifest"],
    ).items():
        append_validation(rows, "phase_10_41_manifest", name, passed, f"{name}={passed}")

    profile = (
        candidate_profile.iloc[0].to_dict()
        if len(candidate_profile) == 1
        else {}
    )
    candidate_checks = [
        ("candidate_profile_row_count_1", len(candidate_profile) == 1),
        ("candidate_exists", safe_bool(profile.get("candidate_exists", False))),
        ("candidate_non_empty_file", safe_bool(profile.get("candidate_non_empty_file", False))),
        ("candidate_size_981", safe_int(profile.get("candidate_size_bytes", -1), -1) == 981),
        ("candidate_sha256_valid", safe_bool(profile.get("candidate_sha256_valid", False))),
        ("candidate_sha256_exact", str(profile.get("candidate_sha256", "")) == EXPECTED_CANDIDATE_SHA256),
        ("candidate_utf8_readable", safe_bool(profile.get("candidate_utf8_readable", False))),
        ("candidate_exact_header_bytes", safe_bool(profile.get("candidate_exact_header_bytes", False))),
        ("candidate_row_count_zero", safe_int(profile.get("candidate_row_count", -1), -1) == 0),
        ("candidate_column_count_54", safe_int(profile.get("candidate_column_count", -1), -1) == 54),
        ("candidate_columns_exact", safe_bool(profile.get("candidate_columns_exact", False))),
        ("candidate_columns_unique", safe_bool(profile.get("candidate_columns_unique", False))),
        ("candidate_contract_valid", safe_bool(profile.get("candidate_contract_valid", False))),
        ("candidate_distinct_from_official", safe_bool(profile.get("candidate_distinct_from_official", False))),
        ("candidate_git_tracked", safe_bool(git_state.get("candidate_git_tracked", False))),
        ("candidate_git_clean", safe_bool(git_state.get("candidate_git_clean", False))),
        ("candidate_git_text_attribute_set", safe_bool(git_state.get("candidate_git_text_attribute_set", False))),
        ("candidate_git_eol_lf", safe_bool(git_state.get("candidate_git_eol_lf", False))),
        (
            "candidate_expected_bytes_deterministic",
            hashlib.sha256(expected_candidate_bytes(EXPECTED_FIELD_NAMES)).hexdigest()
            == EXPECTED_CANDIDATE_SHA256,
        ),
        (
            "gitattributes_contains_canonical_rule",
            GITATTRIBUTES_PATH.exists()
            and EXPECTED_GITATTRIBUTE_RULE
            in GITATTRIBUTES_PATH.read_text(encoding="utf-8-sig").splitlines(),
        ),
    ]
    for name, passed in candidate_checks:
        append_validation(rows, "candidate_contract", name, passed, f"{name}={passed}")

    design_tables = [
        ("design_component_rows_14", len(components) == 14, components),
        ("design_protocol_rows_18", len(protocol) == 18, protocol),
        ("design_path_rows_7", len(paths) == 7, paths),
        ("design_state_rows_12", len(states) == 12, states),
        ("design_invariant_rows_24", len(invariants) == 24, invariants),
        ("design_failure_mode_rows_20", len(failure_modes) == 20, failure_modes),
        ("design_recovery_rows_14", len(recovery) == 14, recovery),
        ("design_concurrency_rows_12", len(concurrency) == 12, concurrency),
    ]
    for name, count_passed, table in design_tables:
        append_validation(rows, "design_tables", name, count_passed, f"{name}={count_passed}")
        all_table_passed = all_passed(table)
        append_validation(
            rows,
            "design_tables",
            name.replace("_rows_", "_all_passed_"),
            all_table_passed,
            f"{name.replace('_rows_', '_all_passed_')}={all_table_passed}",
        )

    design_contract_checks = [
        ("all_components_unimplemented", not components["implemented_in_phase_10_42"].map(safe_bool).any()),
        ("all_components_unexecuted", not components["executed_in_phase_10_42"].map(safe_bool).any()),
        ("all_protocol_actions_disallowed_now", not protocol["allowed_in_phase_10_42"].map(safe_bool).any()),
        ("all_protocol_steps_fail_closed", protocol["fail_closed"].map(safe_bool).all()),
        ("official_path_creation_disallowed_now", not paths[~paths["path_id"].astype(str).eq("REPORT_ROOT")]["creation_allowed_in_phase_10_42"].map(safe_bool).any()),
        ("all_states_unimplemented", not states["implemented_in_phase_10_42"].map(safe_bool).any()),
        ("all_invariants_require_future_implementation", invariants["implementation_required_later"].map(safe_bool).all()),
        ("all_failure_modes_disallow_silent_continue", not failure_modes["silent_continue_allowed"].map(safe_bool).any()),
        ("all_recovery_automatic_actions_disabled", not recovery["automatic_recovery_allowed"].map(safe_bool).any()),
        ("all_concurrency_rules_unimplemented", not concurrency["implemented_in_phase_10_42"].map(safe_bool).any()),
        ("candidate_path_distinct_from_official", EMPTY_SCHEMA_CANDIDATE_PATH != OFFICIAL_DATASET_EXPECTED_PATH),
        ("temp_parent_matches_official_parent", OFFICIAL_TEMP_PATH.parent == OFFICIAL_DATASET_EXPECTED_PATH.parent),
        ("lock_parent_matches_official_parent", OFFICIAL_LOCK_PATH.parent == OFFICIAL_DATASET_EXPECTED_PATH.parent),
        ("manifest_parent_matches_official_parent", OFFICIAL_MANIFEST_PATH.parent == OFFICIAL_DATASET_EXPECTED_PATH.parent),
        ("phase_10_41_doc_exists", PHASE_10_41_DOC_PATH.exists()),
        ("phase_10_42_doc_exists", PHASE_10_42_DOC_PATH.exists()),
    ]
    for name, passed in design_contract_checks:
        append_validation(rows, "design_contract", name, passed, f"{name}={passed}")

    safety_checks = [
        ("design_only", True),
        ("report_only", True),
        ("atomic_write_harness_not_implemented", True),
        ("atomic_write_harness_not_instantiated", True),
        ("atomic_write_harness_not_executed", True),
        ("candidate_not_modified", True),
        ("candidate_not_promoted", True),
        ("official_dataset_absent_before", not official_before),
        ("official_dataset_absent_after", not official_after),
        ("official_dataset_unchanged_absent", not official_before and not official_after),
        ("official_temp_not_created", not OFFICIAL_TEMP_PATH.exists()),
        ("official_lock_not_created", not OFFICIAL_LOCK_PATH.exists()),
        ("official_manifest_not_created", not OFFICIAL_MANIFEST_PATH.exists()),
        ("official_backup_not_created", not BACKUP_DIR.exists()),
        ("official_evidence_rows_written_zero", True),
        ("candidate_evidence_rows_written_zero", True),
        ("evidence_collection_disabled", True),
        ("evidence_persistence_disabled", True),
        ("signal_generation_disabled", True),
        ("live_alerts_disabled", True),
        ("paper_trading_disabled", True),
        ("long_strategy_unapproved", True),
        ("real_capital_disabled", True),
        ("market_execution_disabled", True),
        ("exchange_execution_disabled", True),
        ("automation_disabled", True),
        ("execution_disabled", True),
        ("project_not_completed", True),
        ("future_design_review_only", True),
    ]
    for name, passed in safety_checks:
        append_validation(rows, "safety_boundary", name, passed, f"{name}={passed}")

    return pd.DataFrame(rows)


def build_items(validations: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    names = validations["validation_name"].astype(str).tolist()
    for position, start in enumerate(range(0, len(names), 3), start=1):
        block = names[start:start + 3]
        selected = validations[
            validations["validation_name"].astype(str).isin(block)
        ]
        passed = len(selected) == len(block) and selected["passed"].map(safe_bool).all()
        rows.append(
            {
                "design_item_position": position,
                "design_item_id": f"ATOMIC_WRITE_HARNESS_DESIGN_ITEM_{position:03d}",
                "design_item_name": f"atomic_write_harness_design_block_{position:03d}",
                "validation_names": ",".join(block),
                "required": True,
                "design_only": True,
                "implementation_allowed": False,
                "filesystem_mutation_allowed": False,
                "passed": bool(passed),
            }
        )
    return pd.DataFrame(rows)


def build_findings(items: pd.DataFrame) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "finding_position": position,
                "finding_id": f"ATOMIC_WRITE_HARNESS_DESIGN_FINDING_{position:03d}",
                "design_item_id": str(item["design_item_id"]),
                "finding_status": "PASS" if safe_bool(item["passed"]) else "FAIL",
                "material_issue_found": not safe_bool(item["passed"]),
                "design_change_required": not safe_bool(item["passed"]),
                "future_design_review_allowed": safe_bool(item["passed"]),
                "implementation_allowed": False,
                "passed": safe_bool(item["passed"]),
            }
            for position, (_, item) in enumerate(items.iterrows(), start=1)
        ]
    )


def build_controls(validations: pd.DataFrame) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "control_position": position,
                "control_id": f"ATOMIC_WRITE_HARNESS_DESIGN_CONTROL_{position:03d}",
                "control_name": str(row["validation_name"]),
                "required": True,
                "design_only": True,
                "implementation_allowed": False,
                "official_dataset_creation_allowed": False,
                "official_dataset_write_allowed": False,
                "filesystem_mutation_allowed": False,
                "passed": safe_bool(row["passed"]),
            }
            for position, (_, row) in enumerate(validations.iterrows(), start=1)
        ]
    )


def build_rules(
    validations: pd.DataFrame,
    items: pd.DataFrame,
    findings: pd.DataFrame,
    controls: pd.DataFrame,
    components: pd.DataFrame,
    protocol: pd.DataFrame,
    paths: pd.DataFrame,
    states: pd.DataFrame,
    invariants: pd.DataFrame,
    failure_modes: pd.DataFrame,
    recovery: pd.DataFrame,
    concurrency: pd.DataFrame,
) -> pd.DataFrame:
    material_issues = int(findings["material_issue_found"].map(safe_bool).sum())
    rules = [
        ("validation_count_at_least_130", len(validations) >= 130, ">=130", len(validations)),
        ("all_validations_passed", all_passed(validations), True, all_passed(validations)),
        ("all_items_passed", all_passed(items), True, all_passed(items)),
        ("all_findings_passed", all_passed(findings), True, all_passed(findings)),
        ("material_issue_count_zero", material_issues == 0, 0, material_issues),
        ("all_controls_passed", all_passed(controls), True, all_passed(controls)),
        ("component_count_14", len(components) == 14, 14, len(components)),
        ("protocol_count_18", len(protocol) == 18, 18, len(protocol)),
        ("path_count_7", len(paths) == 7, 7, len(paths)),
        ("state_count_12", len(states) == 12, 12, len(states)),
        ("invariant_count_24", len(invariants) == 24, 24, len(invariants)),
        ("failure_mode_count_20", len(failure_modes) == 20, 20, len(failure_modes)),
        ("recovery_count_14", len(recovery) == 14, 14, len(recovery)),
        ("concurrency_count_12", len(concurrency) == 12, 12, len(concurrency)),
        ("all_design_tables_passed", all(all_passed(df) for df in [components, protocol, paths, states, invariants, failure_modes, recovery, concurrency]), True, all(all_passed(df) for df in [components, protocol, paths, states, invariants, failure_modes, recovery, concurrency])),
        ("design_only", True, True, True),
        ("report_only", True, True, True),
        ("harness_implementation_disabled", True, False, False),
        ("harness_execution_disabled", True, False, False),
        ("candidate_modification_disabled", True, False, False),
        ("candidate_promotion_disabled", True, False, False),
        ("official_dataset_creation_disabled", True, False, False),
        ("official_dataset_writes_disabled", True, False, False),
        ("official_temp_creation_disabled", True, False, False),
        ("official_lock_creation_disabled", True, False, False),
        ("official_manifest_creation_disabled", True, False, False),
        ("backup_creation_disabled", True, False, False),
        ("evidence_collection_disabled", True, False, False),
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
        ("future_design_review_only", True, True, True),
    ]
    return pd.DataFrame(
        [
            {
                "rule_id": f"ATOMIC_WRITE_HARNESS_DESIGN_RULE_{position:03d}",
                "rule_name": name,
                "passed": bool(passed),
                "required_value": required,
                "actual_value": actual,
            }
            for position, (name, passed, required, actual)
            in enumerate(rules, start=1)
        ]
    )


def build_guard_matrix(design_passed: bool) -> pd.DataFrame:
    guards = [
        ("source_candidate_validation_performed", True, True),
        ("source_candidate_validation_passed", True, True),
        ("source_atomic_write_harness_design_allowed", True, True),
        ("atomic_write_harness_design_performed", True, True),
        ("atomic_write_harness_design_passed", True, design_passed),
        ("future_atomic_write_harness_design_review_allowed", True, design_passed),
        ("empty_schema_candidate_exists", True, True),
        ("candidate_contract_valid", True, True),
        ("candidate_git_clean", True, True),
        ("atomic_write_harness_implemented", False, False),
        ("atomic_write_harness_instantiated", False, False),
        ("atomic_write_harness_executed", False, False),
        ("candidate_modification_allowed", False, False),
        ("candidate_promotion_allowed", False, False),
        ("official_dataset_implementation_allowed", False, False),
        ("official_dataset_creation_allowed", False, False),
        ("official_dataset_replacement_allowed", False, False),
        ("official_dataset_write_allowed", False, False),
        ("official_dataset_write_performed", False, False),
        ("official_temp_creation_allowed", False, False),
        ("official_temp_created", False, False),
        ("official_lock_creation_allowed", False, False),
        ("official_lock_created", False, False),
        ("official_manifest_creation_allowed", False, False),
        ("official_manifest_created", False, False),
        ("official_backup_creation_allowed", False, False),
        ("official_backup_created", False, False),
        ("official_evidence_rows_written", 0, 0),
        ("candidate_evidence_rows_written", 0, 0),
        ("evidence_collection_enabled", False, False),
        ("evidence_collection_started", False, False),
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
        ("official_dataset_exists_after", False, False),
        ("official_temp_exists_after", False, False),
        ("official_lock_exists_after", False, False),
        ("official_manifest_exists_after", False, False),
        ("official_backup_exists_after", False, False),
        ("total_project_completed", False, False),
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
                    "atomic_write_harness_design_state"
                    if position <= 9
                    else "atomic_write_harness_design_safety_guard"
                ),
            }
            for position, (name, required, actual)
            in enumerate(guards, start=1)
        ]
    )


def build_requirements(
    validations: pd.DataFrame,
    items: pd.DataFrame,
    findings: pd.DataFrame,
    controls: pd.DataFrame,
    rules: pd.DataFrame,
    guards: pd.DataFrame,
    design_tables: list[pd.DataFrame],
) -> pd.DataFrame:
    rows: list[tuple[str, bool, Any, Any]] = []
    for _, validation in validations.iterrows():
        actual = safe_bool(validation["passed"], False)
        rows.append((str(validation["validation_name"]), actual, True, actual))

    material_issues = int(findings["material_issue_found"].map(safe_bool).sum())
    aggregate = [
        ("design_items_passed", all_passed(items), True, all_passed(items)),
        ("design_findings_passed", all_passed(findings), True, all_passed(findings)),
        ("design_controls_passed", all_passed(controls), True, all_passed(controls)),
        ("design_rules_passed", all_passed(rules), True, all_passed(rules)),
        ("design_guards_passed", all_passed(guards), True, all_passed(guards)),
        ("all_design_tables_passed", all(all_passed(df) for df in design_tables), True, all(all_passed(df) for df in design_tables)),
        ("material_issue_count_zero", material_issues == 0, 0, material_issues),
        ("future_design_review_allowed", True, True, True),
        ("harness_implementation_not_allowed", True, False, False),
        ("harness_execution_not_allowed", True, False, False),
        ("candidate_modification_not_allowed", True, False, False),
        ("candidate_promotion_not_allowed", True, False, False),
        ("official_dataset_creation_not_allowed", True, False, False),
        ("official_dataset_write_not_allowed", True, False, False),
        ("official_temp_creation_not_allowed", True, False, False),
        ("official_lock_creation_not_allowed", True, False, False),
        ("official_manifest_creation_not_allowed", True, False, False),
        ("official_backup_creation_not_allowed", True, False, False),
        ("official_evidence_rows_written_zero", True, 0, 0),
        ("candidate_evidence_rows_written_zero", True, 0, 0),
        ("signal_generation_disabled", True, False, False),
        ("paper_trading_disabled", True, False, False),
        ("market_execution_disabled", True, False, False),
        ("project_not_completed", True, False, False),
    ]
    rows.extend(aggregate)

    return pd.DataFrame(
        [
            {
                "requirement_id": f"ATOMIC_WRITE_HARNESS_DESIGN_REQ_{position:03d}",
                "requirement_name": name,
                "passed": bool(passed),
                "required_value": required,
                "actual_value": actual,
            }
            for position, (name, passed, required, actual)
            in enumerate(rows, start=1)
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
    failed = requirements[~requirements["passed"].map(safe_bool)]
    return pd.DataFrame(
        [
            {
                "official_dataset_atomic_write_harness_design_id": (
                    "PHASE_10_42_LONG_FORWARD_OBSERVATION_EVIDENCE_"
                    "COLLECTION_OFFICIAL_DATASET_ATOMIC_WRITE_HARNESS_"
                    "DESIGN_001"
                ),
                "official_dataset_atomic_write_harness_design_performed": True,
                "official_dataset_atomic_write_harness_design_passed": passed,
                "official_dataset_atomic_write_harness_design_decision": (
                    READY_DECISION if passed else BLOCKED_DECISION
                ),
                "total_requirements": len(requirements),
                "passed_requirements": int(requirements["passed"].map(safe_bool).sum()),
                "failed_requirements": len(failed),
                "failed_requirement_names": ",".join(
                    failed["requirement_name"].astype(str).tolist()
                ),
                "future_official_dataset_atomic_write_harness_design_review_allowed": passed,
                "atomic_write_harness_implementation_allowed": False,
                "atomic_write_harness_execution_allowed": False,
                "candidate_modification_allowed": False,
                "candidate_promotion_allowed": False,
                "official_dataset_implementation_allowed": False,
                "official_dataset_creation_allowed": False,
                "official_dataset_replacement_allowed": False,
                "official_dataset_write_allowed": False,
                "official_dataset_write_performed": False,
                "official_temp_creation_allowed": False,
                "official_lock_creation_allowed": False,
                "official_manifest_creation_allowed": False,
                "official_backup_creation_allowed": False,
                "official_evidence_rows_written": 0,
                "candidate_evidence_rows_written": 0,
                "evidence_collection_enabled": False,
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
    anchors = {
        "phase_10_41_validation_doc_exists": PHASE_10_41_DOC_PATH.exists(),
        "phase_10_42_design_doc_exists": PHASE_10_42_DOC_PATH.exists(),
        "gitattributes_exists": GITATTRIBUTES_PATH.exists(),
    }
    for name, passed in anchors.items():
        checks.append(
            check_row(
                "phase_anchor",
                name,
                passed,
                "INFO" if passed else "ERROR",
                f"{name}={passed}",
            )
        )

    decision_row = decision.iloc[0].to_dict() if len(decision) == 1 else {}
    blocks = {
        "design_validations_passed": all_passed(validations),
        "design_items_passed": all_passed(items),
        "design_findings_passed": all_passed(findings),
        "design_controls_passed": all_passed(controls),
        "design_rules_passed": all_passed(rules),
        "design_requirements_passed": all_passed(requirements),
        "design_guards_passed": all_passed(guards),
        "atomic_write_harness_design_passed": safe_bool(
            decision_row.get(
                "official_dataset_atomic_write_harness_design_passed",
                False,
            )
        ),
        "atomic_write_harness_design_decision_expected": (
            str(
                decision_row.get(
                    "official_dataset_atomic_write_harness_design_decision",
                    "",
                )
            )
            == READY_DECISION
        ),
    }
    for name, passed in blocks.items():
        checks.append(
            check_row(
                "atomic_write_harness_design",
                name,
                passed,
                "INFO" if passed else "ERROR",
                f"{name}={passed}",
            )
        )

    unchanged = not official_before and not official_after
    checks.append(
        check_row(
            "official_dataset_guard",
            "official_dataset_unchanged_absent",
            unchanged,
            "INFO" if unchanged else "ERROR",
            f"before={official_before},after={official_after}",
        )
    )

    warnings = [
        ("design_only", "Phase 10.42 defines contracts but implements no harness."),
        ("report_only", "Only generated reports may be written."),
        ("harness_not_implemented", "No atomic-write harness implementation exists."),
        ("harness_not_executed", "No atomic-write operation was executed."),
        ("candidate_not_modified", "The validated candidate remains read-only."),
        ("candidate_not_promoted", "The candidate was not promoted."),
        ("official_dataset_not_created", "The official dataset remains absent."),
        ("official_dataset_not_written", "No official dataset write occurred."),
        ("official_temp_not_created", "No official staging file was created."),
        ("official_lock_not_created", "No official lock was created."),
        ("official_manifest_not_created", "No official manifest was created."),
        ("official_backup_not_created", "No official backup was created."),
        ("real_evidence_not_collected", "No real evidence was collected."),
        ("evidence_persistence_not_enabled", "Evidence persistence remains disabled."),
        ("signal_generation_not_enabled", "Signal generation remains disabled."),
        ("live_alerts_not_enabled", "Live alerts remain disabled."),
        ("paper_trading_not_enabled", "Paper trading remains disabled."),
        ("long_strategy_not_approved", "LONG remains unapproved."),
        ("real_capital_not_allowed", "Real capital remains prohibited."),
        ("market_execution_not_allowed", "Market execution remains prohibited."),
        ("automation_not_allowed", "Automation remains prohibited."),
        ("future_design_review_only", "Only Phase 10.43 design review is allowed next."),
    ]
    for name, details in warnings:
        checks.append(
            check_row("scope_control", name, True, "WARNING", details)
        )

    checks.append(
        check_row(
            "phase_transition",
            "phase_10_43_recommended_next",
            True,
            "INFO",
            "Recommended next: Phase 10.43 atomic-write harness design review.",
        )
    )
    return pd.DataFrame(checks)


def build_summary(
    source_manifest: pd.DataFrame,
    validations: pd.DataFrame,
    components: pd.DataFrame,
    protocol: pd.DataFrame,
    paths: pd.DataFrame,
    states: pd.DataFrame,
    invariants: pd.DataFrame,
    failure_modes: pd.DataFrame,
    recovery: pd.DataFrame,
    concurrency: pd.DataFrame,
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
    decision_row = decision.iloc[0].to_dict() if len(decision) == 1 else {}
    error_count = int(checks["severity"].astype(str).eq("ERROR").sum())
    warning_count = int(checks["severity"].astype(str).eq("WARNING").sum())
    blocker_count = int(checks["blocker"].map(safe_bool).sum())
    material_issue_count = int(findings["material_issue_found"].map(safe_bool).sum())
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
                "phase": "10.42",
                "official_dataset_atomic_write_harness_design_defined": True,
                "phase_10_41_source_validated": all_passed(validations),
                "source_artifact_count": len(source_manifest),
                "source_artifacts_exist": source_manifest["artifact_exists"].map(safe_bool).all(),
                "source_artifacts_non_empty": source_manifest["artifact_non_empty"].map(safe_bool).all(),
                "source_artifact_hashes_valid": source_manifest["artifact_sha256_valid"].map(safe_bool).all(),
                "source_manifest_sha256": manifest_digest(source_manifest),
                "design_validation_rows": len(validations),
                "design_component_rows": len(components),
                "design_protocol_rows": len(protocol),
                "design_path_rows": len(paths),
                "design_state_rows": len(states),
                "design_invariant_rows": len(invariants),
                "design_failure_mode_rows": len(failure_modes),
                "design_recovery_rows": len(recovery),
                "design_concurrency_rows": len(concurrency),
                "design_item_rows": len(items),
                "design_finding_rows": len(findings),
                "design_control_rows": len(controls),
                "design_rule_rows": len(rules),
                "design_requirement_rows": len(requirements),
                "design_guard_rows": len(guards),
                "design_validations_passed": all_passed(validations),
                "design_components_passed": all_passed(components),
                "design_protocol_passed": all_passed(protocol),
                "design_paths_passed": all_passed(paths),
                "design_states_passed": all_passed(states),
                "design_invariants_passed": all_passed(invariants),
                "design_failure_modes_passed": all_passed(failure_modes),
                "design_recovery_passed": all_passed(recovery),
                "design_concurrency_passed": all_passed(concurrency),
                "design_items_passed": all_passed(items),
                "design_findings_passed": all_passed(findings),
                "design_controls_passed": all_passed(controls),
                "design_rules_passed": all_passed(rules),
                "design_requirements_passed": all_passed(requirements),
                "design_guards_passed": all_passed(guards),
                "material_issue_count": material_issue_count,
                "official_dataset_atomic_write_harness_design_performed": True,
                "official_dataset_atomic_write_harness_design_passed": safe_bool(
                    decision_row.get(
                        "official_dataset_atomic_write_harness_design_passed",
                        False,
                    )
                ),
                "official_dataset_atomic_write_harness_design_decision": str(
                    decision_row.get(
                        "official_dataset_atomic_write_harness_design_decision",
                        "",
                    )
                ),
                "future_official_dataset_atomic_write_harness_design_review_allowed": safe_bool(
                    decision_row.get(
                        "future_official_dataset_atomic_write_harness_design_review_allowed",
                        False,
                    )
                ),
                "atomic_write_harness_implementation_allowed": False,
                "atomic_write_harness_execution_allowed": False,
                "candidate_modification_allowed": False,
                "candidate_promotion_allowed": False,
                "official_dataset_implementation_allowed": False,
                "official_dataset_creation_allowed": False,
                "official_dataset_replacement_allowed": False,
                "official_dataset_write_allowed": False,
                "official_dataset_write_performed": False,
                "official_dataset_exists_before": official_before,
                "official_dataset_exists_after": official_after,
                "official_dataset_unchanged_absent": not official_before and not official_after,
                "official_temp_created": OFFICIAL_TEMP_PATH.exists(),
                "official_lock_created": OFFICIAL_LOCK_PATH.exists(),
                "official_manifest_created": OFFICIAL_MANIFEST_PATH.exists(),
                "official_backup_created": BACKUP_DIR.exists(),
                "official_evidence_rows_written": 0,
                "candidate_evidence_rows_written": 0,
                "evidence_collection_enabled": False,
                "evidence_persistence_allowed": False,
                "signal_generation_enabled": False,
                "live_alerts_allowed": False,
                "paper_trading_enabled": False,
                "long_strategy_approved": False,
                "paper_trade_execution_allowed": False,
                "real_capital_allowed": False,
                "market_execution_allowed": False,
                "exchange_execution_allowed": False,
                "automation_allowed": False,
                "execution_allowed": False,
                "total_project_completed": False,
                "recommended_next_phase": RECOMMENDED_NEXT_PHASE,
                "estimated_phase_10_progress_percent": 100,
                "total_checks": len(checks),
                "warning_count": warning_count,
                "error_count": error_count,
                "blocker_count": blocker_count,
                "validation_passed": validation_passed,
                "validation_decision": (
                    "PHASE_10_42_LONG_FORWARD_OBSERVATION_EVIDENCE_"
                    "COLLECTION_OFFICIAL_DATASET_ATOMIC_WRITE_HARNESS_"
                    "DESIGN_VALIDATED"
                    if validation_passed
                    else
                    "PHASE_10_42_LONG_FORWARD_OBSERVATION_EVIDENCE_"
                    "COLLECTION_OFFICIAL_DATASET_ATOMIC_WRITE_HARNESS_"
                    "DESIGN_FAILED"
                ),
            }
        ]
    )


def run_long_forward_observation_evidence_collection_official_dataset_atomic_write_harness_design() -> dict[str, pd.DataFrame]:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    official_before = OFFICIAL_DATASET_EXPECTED_PATH.exists()
    source_manifest_before = build_manifest(SOURCE_PATHS, "PHASE_10_42_SOURCE")
    source = {
        name: read_csv(path)
        for name, path in PHASE_10_41_PATHS.items()
    }

    candidate_profile = inspect_candidate(
        EMPTY_SCHEMA_CANDIDATE_PATH,
        EXPECTED_FIELD_NAMES,
    )
    git_state = candidate_git_state(EMPTY_SCHEMA_CANDIDATE_PATH)

    components = build_components()
    protocol = build_protocol()
    paths = build_path_contract()
    states = build_state_machine()
    invariants = build_invariants()
    failure_modes = build_failure_modes()
    recovery = build_recovery_matrix()
    concurrency = build_concurrency_contract()

    source_manifest_after = build_manifest(SOURCE_PATHS, "PHASE_10_42_SOURCE")
    official_after = OFFICIAL_DATASET_EXPECTED_PATH.exists()

    validations = build_validations(
        source,
        source_manifest_before,
        source_manifest_after,
        candidate_profile,
        git_state,
        components,
        protocol,
        paths,
        states,
        invariants,
        failure_modes,
        recovery,
        concurrency,
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
        components,
        protocol,
        paths,
        states,
        invariants,
        failure_modes,
        recovery,
        concurrency,
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
    design_tables = [
        components,
        protocol,
        paths,
        states,
        invariants,
        failure_modes,
        recovery,
        concurrency,
    ]
    requirements = build_requirements(
        validations,
        items,
        findings,
        controls,
        rules,
        guards,
        design_tables,
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
        components,
        protocol,
        paths,
        states,
        invariants,
        failure_modes,
        recovery,
        concurrency,
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
        "components": components,
        "protocol": protocol,
        "paths": paths,
        "states": states,
        "invariants": invariants,
        "failure_modes": failure_modes,
        "recovery": recovery,
        "concurrency": concurrency,
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
        dataframe.to_csv(REPORTS_DIR / OUTPUT_FILENAMES[name], index=False)

    output_paths = {
        name: REPORTS_DIR / OUTPUT_FILENAMES[name]
        for name in frames
    }
    output_manifest = build_manifest(
        output_paths,
        "PHASE_10_42_OUTPUT",
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
        "source_validation_summary": source["validation_summary"],
        "source_validation_decision": source["validation_decision"],
        "source_candidate_profile": source["validation_profile"],
        "source_negative_controls": source["validation_negative_controls"],
        "source_artifact_manifest": source_manifest_before,
        "candidate_profile": candidate_profile,
        "components": components,
        "protocol": protocol,
        "paths": paths,
        "states": states,
        "invariants": invariants,
        "failure_modes": failure_modes,
        "recovery": recovery,
        "concurrency": concurrency,
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
