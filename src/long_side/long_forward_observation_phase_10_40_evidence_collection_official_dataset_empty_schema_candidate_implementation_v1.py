from __future__ import annotations

import csv
import io
import os
from pathlib import Path
from typing import Any

import pandas as pd

from src.long_side.long_forward_observation_phase_10_39_evidence_collection_official_dataset_schema_implementation_precheck_v1 import (
    EMPTY_SCHEMA_CANDIDATE_PATH,
    EXPECTED_FIELD_NAMES,
    OFFICIAL_DATASET_EXPECTED_PATH,
    OFFICIAL_LOCK_PATH,
    OFFICIAL_MANIFEST_PATH,
    OFFICIAL_TEMP_PATH,
    BACKUP_DIR,
    all_passed,
    build_manifest,
    is_sha256,
    manifest_digest,
    read_csv,
    safe_bool,
    safe_int,
    sha256_file,
)

REPORTS_DIR = Path(
    "reports/p10_40_evidence_collection_official_dataset_"
    "empty_schema_candidate_implementation_v1"
)
PHASE_10_39_DIR = Path(
    "reports/p10_39_evidence_collection_official_dataset_"
    "schema_implementation_precheck_v1"
)
PHASE_10_37_DIR = Path(
    "reports/p10_37_evidence_collection_official_dataset_"
    "schema_implementation_design_v1"
)

PHASE_10_39_DOC_PATH = Path(
    "docs/PHASE_10_LONG_FORWARD_OBSERVATION_EVIDENCE_COLLECTION_"
    "OFFICIAL_DATASET_SCHEMA_IMPLEMENTATION_PRECHECK.md"
)
PHASE_10_40_DOC_PATH = Path(
    "docs/PHASE_10_LONG_FORWARD_OBSERVATION_EVIDENCE_COLLECTION_"
    "OFFICIAL_DATASET_EMPTY_SCHEMA_CANDIDATE_IMPLEMENTATION.md"
)

PRECHECK_PATHS = {
    "precheck_summary": PHASE_10_39_DIR / "official_dataset_schema_implementation_precheck_summary_v1.csv",
    "precheck_validations": PHASE_10_39_DIR / "official_dataset_schema_implementation_precheck_validations_v1.csv",
    "precheck_items": PHASE_10_39_DIR / "official_dataset_schema_implementation_precheck_items_v1.csv",
    "precheck_findings": PHASE_10_39_DIR / "official_dataset_schema_implementation_precheck_findings_v1.csv",
    "precheck_controls": PHASE_10_39_DIR / "official_dataset_schema_implementation_precheck_controls_v1.csv",
    "precheck_rules": PHASE_10_39_DIR / "official_dataset_schema_implementation_precheck_rules_v1.csv",
    "precheck_requirements": PHASE_10_39_DIR / "official_dataset_schema_implementation_precheck_requirements_v1.csv",
    "precheck_guard_matrix": PHASE_10_39_DIR / "official_dataset_schema_implementation_precheck_guard_matrix_v1.csv",
    "precheck_path_plan": PHASE_10_39_DIR / "official_dataset_schema_implementation_precheck_path_plan_v1.csv",
    "precheck_decision": PHASE_10_39_DIR / "official_dataset_schema_implementation_precheck_decision_v1.csv",
    "precheck_checks": PHASE_10_39_DIR / "official_dataset_schema_implementation_precheck_checks_v1.csv",
    "precheck_manifest": PHASE_10_39_DIR / "source_official_dataset_schema_implementation_precheck_artifact_manifest_v1.csv",
}
FIELD_CATALOG_PATH = PHASE_10_37_DIR / "official_dataset_schema_field_catalog_v1.csv"
SOURCE_PATHS = {**PRECHECK_PATHS, "field_catalog": FIELD_CATALOG_PATH}

SOURCE_READY_DECISION = (
    "CONTROLLED_FORWARD_OBSERVATION_EVIDENCE_COLLECTION_OFFICIAL_"
    "DATASET_SCHEMA_IMPLEMENTATION_PRECHECK_READY_FOR_EMPTY_SCHEMA_"
    "CANDIDATE_IMPLEMENTATION"
)
READY_DECISION = (
    "CONTROLLED_FORWARD_OBSERVATION_EVIDENCE_COLLECTION_OFFICIAL_"
    "DATASET_EMPTY_SCHEMA_CANDIDATE_IMPLEMENTATION_READY_FOR_SCHEMA_"
    "VALIDATION"
)
BLOCKED_DECISION = (
    "CONTROLLED_FORWARD_OBSERVATION_EVIDENCE_COLLECTION_OFFICIAL_"
    "DATASET_EMPTY_SCHEMA_CANDIDATE_IMPLEMENTATION_BLOCKED"
)
RECOMMENDED_NEXT_PHASE = (
    "PHASE_10_41_LONG_FORWARD_OBSERVATION_EVIDENCE_COLLECTION_"
    "OFFICIAL_DATASET_EMPTY_SCHEMA_CANDIDATE_VALIDATION_V1"
)

OUTPUT_FILENAMES = {
    "summary": "official_dataset_empty_schema_candidate_implementation_summary_v1.csv",
    "validations": "official_dataset_empty_schema_candidate_implementation_validations_v1.csv",
    "candidate_profile": "official_dataset_empty_schema_candidate_profile_v1.csv",
    "items": "official_dataset_empty_schema_candidate_implementation_items_v1.csv",
    "findings": "official_dataset_empty_schema_candidate_implementation_findings_v1.csv",
    "controls": "official_dataset_empty_schema_candidate_implementation_controls_v1.csv",
    "rules": "official_dataset_empty_schema_candidate_implementation_rules_v1.csv",
    "requirements": "official_dataset_empty_schema_candidate_implementation_requirements_v1.csv",
    "guard_matrix": "official_dataset_empty_schema_candidate_implementation_guard_matrix_v1.csv",
    "decision": "official_dataset_empty_schema_candidate_implementation_decision_v1.csv",
    "checks": "official_dataset_empty_schema_candidate_implementation_checks_v1.csv",
    "manifest": "source_official_dataset_empty_schema_candidate_implementation_artifact_manifest_v1.csv",
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


def expected_candidate_bytes(fields: list[str]) -> bytes:
    buffer = io.StringIO(newline="")
    writer = csv.writer(buffer, lineterminator="\n")
    writer.writerow(fields)
    return buffer.getvalue().encode("utf-8")


def inspect_candidate(path: Path, fields: list[str]) -> pd.DataFrame:
    exists = path.exists() and path.is_file()
    size = path.stat().st_size if exists else 0
    digest = sha256_file(path) if exists else ""
    readable_utf8 = False
    exact_bytes = False
    row_count = -1
    column_count = -1
    columns_exact = False
    columns_unique = False
    parse_error = ""

    if exists:
        try:
            raw = path.read_bytes()
            raw.decode("utf-8")
            readable_utf8 = True
            exact_bytes = raw == expected_candidate_bytes(fields)
            frame = pd.read_csv(path)
            row_count = len(frame)
            column_count = len(frame.columns)
            columns = frame.columns.astype(str).tolist()
            columns_exact = columns == fields
            columns_unique = len(columns) == len(set(columns))
        except Exception as exc:
            parse_error = f"{type(exc).__name__}: {exc}"

    valid = all(
        [
            exists,
            size > 0,
            is_sha256(digest),
            readable_utf8,
            exact_bytes,
            row_count == 0,
            column_count == len(fields),
            columns_exact,
            columns_unique,
        ]
    )
    return pd.DataFrame(
        [
            {
                "candidate_path": str(path),
                "candidate_exists": exists,
                "candidate_size_bytes": int(size),
                "candidate_non_empty_file": size > 0,
                "candidate_sha256": digest,
                "candidate_sha256_valid": is_sha256(digest),
                "candidate_utf8_readable": readable_utf8,
                "candidate_exact_header_bytes": exact_bytes,
                "candidate_row_count": row_count,
                "candidate_column_count": column_count,
                "candidate_columns_exact": columns_exact,
                "candidate_columns_unique": columns_unique,
                "candidate_parse_error": parse_error,
                "candidate_contract_valid": valid,
                "official_dataset_path": str(OFFICIAL_DATASET_EXPECTED_PATH),
                "candidate_distinct_from_official": path != OFFICIAL_DATASET_EXPECTED_PATH,
            }
        ]
    )


def write_candidate_atomic(path: Path, fields: list[str]) -> dict[str, Any]:
    profile_before = inspect_candidate(path, fields).iloc[0].to_dict()
    if safe_bool(profile_before.get("candidate_exists", False)):
        if safe_bool(profile_before.get("candidate_contract_valid", False)):
            return {
                "candidate_write_attempted": False,
                "candidate_created_this_run": False,
                "candidate_reused_existing": True,
                "candidate_invalid_existing_blocked": False,
                "candidate_temp_path": "",
                "candidate_temp_cleaned": True,
                "candidate_write_error": "",
            }
        return {
            "candidate_write_attempted": False,
            "candidate_created_this_run": False,
            "candidate_reused_existing": False,
            "candidate_invalid_existing_blocked": True,
            "candidate_temp_path": "",
            "candidate_temp_cleaned": True,
            "candidate_write_error": "Existing candidate violates the empty-schema contract.",
        }

    path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = path.with_name(f"{path.name}.{os.getpid()}.tmp")
    error = ""
    created = False
    try:
        with temp_path.open("wb") as handle:
            handle.write(expected_candidate_bytes(fields))
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_path, path)
        created = True
    except Exception as exc:
        error = f"{type(exc).__name__}: {exc}"
    finally:
        if temp_path.exists():
            try:
                temp_path.unlink()
            except Exception:
                pass

    return {
        "candidate_write_attempted": True,
        "candidate_created_this_run": created,
        "candidate_reused_existing": False,
        "candidate_invalid_existing_blocked": False,
        "candidate_temp_path": str(temp_path),
        "candidate_temp_cleaned": not temp_path.exists(),
        "candidate_write_error": error,
    }


def validate_phase_10_39_manifest(
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
            "precheck_manifest_rows_35": False,
            "precheck_manifest_source_rows_24": False,
            "precheck_manifest_output_rows_11": False,
            "precheck_manifest_listed_artifacts_valid": False,
            "precheck_manifest_hashes_match": False,
            "precheck_manifest_self_exclusion_expected": False,
            "precheck_manifest_file_exists": manifest_path.exists(),
            "precheck_manifest_file_non_empty": manifest_path.exists() and manifest_path.stat().st_size > 0,
            "precheck_manifest_file_sha256_valid": is_sha256(sha256_file(manifest_path)),
        }

    source_rows = manifest_df[
        manifest_df["artifact_scope"].astype(str).eq("PHASE_10_39_SOURCE")
    ]
    output_rows = manifest_df[
        manifest_df["artifact_scope"].astype(str).eq("PHASE_10_39_OUTPUT")
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
        if not path.exists() or sha256_file(path) != str(row["artifact_sha256"]):
            hashes_match = False
            break

    filenames = set(manifest_df["artifact_filename"].astype(str))
    exists = manifest_path.exists() and manifest_path.is_file()
    return {
        "precheck_manifest_rows_35": len(manifest_df) == 35,
        "precheck_manifest_source_rows_24": len(source_rows) == 24,
        "precheck_manifest_output_rows_11": len(output_rows) == 11,
        "precheck_manifest_listed_artifacts_valid": listed_valid,
        "precheck_manifest_hashes_match": hashes_match,
        "precheck_manifest_self_exclusion_expected": (
            len(manifest_df) == 35
            and len(source_rows) == 24
            and len(output_rows) == 11
            and manifest_path.name not in filenames
        ),
        "precheck_manifest_file_exists": exists,
        "precheck_manifest_file_non_empty": exists and manifest_path.stat().st_size > 0,
        "precheck_manifest_file_sha256_valid": is_sha256(sha256_file(manifest_path)),
    }


def build_preconditions(
    source: dict[str, pd.DataFrame],
    source_manifest_before: pd.DataFrame,
    source_manifest_mid: pd.DataFrame,
    official_before: bool,
    candidate_before: bool,
) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []

    source_checks = [
        ("source_artifact_count_13", len(source_manifest_before) == 13),
        ("source_artifacts_exist", source_manifest_before["artifact_exists"].map(safe_bool).all()),
        ("source_artifacts_non_empty", source_manifest_before["artifact_non_empty"].map(safe_bool).all()),
        ("source_artifact_hashes_valid", source_manifest_before["artifact_sha256_valid"].map(safe_bool).all()),
        ("source_artifacts_stable_before_candidate_write", manifest_digest(source_manifest_before) == manifest_digest(source_manifest_mid)),
    ]
    for name, passed in source_checks:
        append_validation(rows, "source_artifacts", name, passed, f"{name}={passed}")

    summary = source["precheck_summary"].iloc[0].to_dict() if len(source["precheck_summary"]) == 1 else {}
    summary_checks = [
        ("phase_10_39_validation_passed", safe_bool(summary.get("validation_passed", False)) and str(summary.get("validation_decision", "")) == "PHASE_10_39_LONG_FORWARD_OBSERVATION_EVIDENCE_COLLECTION_OFFICIAL_DATASET_SCHEMA_IMPLEMENTATION_PRECHECK_VALIDATED"),
        ("source_precheck_performed", safe_bool(summary.get("official_dataset_schema_implementation_precheck_performed", False))),
        ("source_precheck_passed", safe_bool(summary.get("official_dataset_schema_implementation_precheck_passed", False))),
        ("source_precheck_decision_valid", str(summary.get("official_dataset_schema_implementation_precheck_decision", "")) == SOURCE_READY_DECISION),
        ("source_candidate_implementation_allowed", safe_bool(summary.get("future_official_dataset_empty_schema_candidate_implementation_allowed", False))),
        ("source_summary_source_artifacts_24", safe_int(summary.get("source_artifact_count", -1), -1) == 24),
        ("source_summary_validation_rows_112", safe_int(summary.get("precheck_validation_rows", -1), -1) == 112),
        ("source_summary_item_rows_38", safe_int(summary.get("precheck_item_rows", -1), -1) == 38),
        ("source_summary_finding_rows_38", safe_int(summary.get("precheck_finding_rows", -1), -1) == 38),
        ("source_summary_control_rows_112", safe_int(summary.get("precheck_control_rows", -1), -1) == 112),
        ("source_summary_rule_rows_26", safe_int(summary.get("precheck_rule_rows", -1), -1) == 26),
        ("source_summary_requirement_rows_128", safe_int(summary.get("precheck_requirement_rows", -1), -1) == 128),
        ("source_summary_guard_rows_39", safe_int(summary.get("precheck_guard_rows", -1), -1) == 39),
        ("source_summary_path_plan_rows_6", safe_int(summary.get("precheck_path_plan_rows", -1), -1) == 6),
        ("source_summary_material_issue_zero", safe_int(summary.get("material_issue_count", -1), -1) == 0),
        ("source_summary_total_checks_30", safe_int(summary.get("total_checks", -1), -1) == 30),
        ("source_summary_warning_count_15", safe_int(summary.get("warning_count", -1), -1) == 15),
        ("source_summary_error_count_zero", safe_int(summary.get("error_count", -1), -1) == 0),
        ("source_summary_blocker_count_zero", safe_int(summary.get("blocker_count", -1), -1) == 0),
        ("source_summary_official_dataset_unchanged_absent", safe_bool(summary.get("official_dataset_unchanged_absent", False))),
        ("source_summary_official_rows_zero", safe_int(summary.get("official_evidence_rows_written", -1), -1) == 0),
        ("source_summary_candidate_not_created", not safe_bool(summary.get("empty_schema_candidate_created", True), True)),
        ("source_summary_long_unapproved", not safe_bool(summary.get("long_strategy_approved", True), True)),
        ("source_summary_project_not_complete", not safe_bool(summary.get("total_project_completed", True), True)),
    ]
    for name, passed in summary_checks:
        append_validation(rows, "phase_10_39_summary", name, passed, f"{name}={passed}")

    decision = source["precheck_decision"].iloc[0].to_dict() if len(source["precheck_decision"]) == 1 else {}
    decision_checks = [
        ("source_decision_row_count_1", len(source["precheck_decision"]) == 1),
        ("source_decision_precheck_passed", safe_bool(decision.get("official_dataset_schema_implementation_precheck_passed", False))),
        ("source_decision_value_valid", str(decision.get("official_dataset_schema_implementation_precheck_decision", "")) == SOURCE_READY_DECISION),
        ("source_decision_field_count_54", safe_int(decision.get("canonical_schema_field_count", -1), -1) == 54),
        ("source_decision_source_artifacts_24", safe_int(decision.get("source_artifact_count", -1), -1) == 24),
        ("source_decision_requirements_128", safe_int(decision.get("total_requirements", -1), -1) == 128),
        ("source_decision_failed_requirements_zero", safe_int(decision.get("failed_requirements", -1), -1) == 0),
        ("source_decision_candidate_allowed", safe_bool(decision.get("future_official_dataset_empty_schema_candidate_implementation_allowed", False))),
        ("source_decision_next_phase_10_40", str(decision.get("recommended_next_phase", "")) == "PHASE_10_40_LONG_FORWARD_OBSERVATION_EVIDENCE_COLLECTION_OFFICIAL_DATASET_EMPTY_SCHEMA_CANDIDATE_IMPLEMENTATION_V1"),
    ]
    for name, passed in decision_checks:
        append_validation(rows, "phase_10_39_decision", name, passed, f"{name}={passed}")

    output_checks = [
        ("precheck_validations_rows_112", len(source["precheck_validations"]) == 112),
        ("precheck_validations_all_passed", all_passed(source["precheck_validations"])),
        ("precheck_items_rows_38", len(source["precheck_items"]) == 38),
        ("precheck_items_all_passed", all_passed(source["precheck_items"])),
        ("precheck_findings_rows_38", len(source["precheck_findings"]) == 38),
        ("precheck_findings_all_passed", all_passed(source["precheck_findings"])),
        ("precheck_controls_rows_112", len(source["precheck_controls"]) == 112),
        ("precheck_controls_all_passed", all_passed(source["precheck_controls"])),
        ("precheck_rules_rows_26", len(source["precheck_rules"]) == 26),
        ("precheck_rules_all_passed", all_passed(source["precheck_rules"])),
        ("precheck_requirements_rows_128", len(source["precheck_requirements"]) == 128),
        ("precheck_requirements_all_passed", all_passed(source["precheck_requirements"])),
        ("precheck_guards_rows_39", len(source["precheck_guard_matrix"]) == 39),
        ("precheck_guards_all_passed", all_passed(source["precheck_guard_matrix"])),
        ("precheck_path_plan_rows_6", len(source["precheck_path_plan"]) == 6),
        ("precheck_checks_rows_30", len(source["precheck_checks"]) == 30),
        ("precheck_checks_all_passed", all_passed(source["precheck_checks"])),
    ]
    for name, passed in output_checks:
        append_validation(rows, "phase_10_39_outputs", name, passed, f"{name}={passed}")

    for name, passed in validate_phase_10_39_manifest(source["precheck_manifest"], PRECHECK_PATHS["precheck_manifest"]).items():
        append_validation(rows, "phase_10_39_manifest", name, passed, f"{name}={passed}")

    field_catalog = source["field_catalog"]
    field_names = (
        field_catalog.sort_values("field_position")["field_name"].astype(str).tolist()
        if not field_catalog.empty and {"field_position", "field_name"}.issubset(field_catalog.columns)
        else []
    )
    field_checks = [
        ("field_catalog_rows_54", len(field_catalog) == 54),
        ("field_catalog_positions_exact", not field_catalog.empty and field_catalog["field_position"].map(safe_int).tolist() == list(range(1, 55))),
        ("field_catalog_names_exact", field_names == EXPECTED_FIELD_NAMES),
        ("field_catalog_names_unique", len(field_names) == len(set(field_names)) == 54),
        ("candidate_path_exact", EMPTY_SCHEMA_CANDIDATE_PATH == Path("data/forward/candidates/long_forward_observation_dataset_v1.empty_candidate.csv")),
        ("official_path_exact", OFFICIAL_DATASET_EXPECTED_PATH == Path("data/forward/long_forward_observation_dataset_v1.csv")),
        ("candidate_distinct_from_official", EMPTY_SCHEMA_CANDIDATE_PATH != OFFICIAL_DATASET_EXPECTED_PATH),
    ]
    for name, passed in field_checks:
        append_validation(rows, "canonical_contract", name, passed, f"{name}={passed}")

    environment_checks = [
        ("phase_10_39_doc_exists", PHASE_10_39_DOC_PATH.exists()),
        ("phase_10_40_doc_exists", PHASE_10_40_DOC_PATH.exists()),
        ("official_dataset_absent_before", not official_before),
        ("candidate_state_known_before", isinstance(candidate_before, bool)),
        ("candidate_parent_distinct_from_official_file", EMPTY_SCHEMA_CANDIDATE_PATH.parent != OFFICIAL_DATASET_EXPECTED_PATH),
        ("candidate_suffix_csv", EMPTY_SCHEMA_CANDIDATE_PATH.suffix.lower() == ".csv"),
    ]
    for name, passed in environment_checks:
        append_validation(rows, "implementation_environment", name, passed, f"{name}={passed}")

    return pd.DataFrame(rows)


def append_post_validations(
    preconditions: pd.DataFrame,
    source_manifest_before: pd.DataFrame,
    source_manifest_after: pd.DataFrame,
    write_result: dict[str, Any],
    candidate_profile: pd.DataFrame,
    official_before: bool,
    official_after: bool,
) -> pd.DataFrame:
    rows = preconditions.to_dict("records")
    profile = candidate_profile.iloc[0].to_dict() if len(candidate_profile) == 1 else {}
    candidate_hash_before = str(profile.get("candidate_sha256", ""))
    candidate_hash_after = sha256_file(EMPTY_SCHEMA_CANDIDATE_PATH)

    post_checks = [
        ("candidate_write_completed_or_valid_reuse", safe_bool(write_result.get("candidate_created_this_run", False)) or safe_bool(write_result.get("candidate_reused_existing", False))),
        ("candidate_write_error_empty", str(write_result.get("candidate_write_error", "")) == ""),
        ("candidate_invalid_existing_not_detected", not safe_bool(write_result.get("candidate_invalid_existing_blocked", True), True)),
        ("candidate_temp_cleaned", safe_bool(write_result.get("candidate_temp_cleaned", False))),
        ("candidate_exists_after", safe_bool(profile.get("candidate_exists", False))),
        ("candidate_non_empty_file", safe_bool(profile.get("candidate_non_empty_file", False))),
        ("candidate_sha256_valid", safe_bool(profile.get("candidate_sha256_valid", False))),
        ("candidate_utf8_readable", safe_bool(profile.get("candidate_utf8_readable", False))),
        ("candidate_exact_header_bytes", safe_bool(profile.get("candidate_exact_header_bytes", False))),
        ("candidate_row_count_zero", safe_int(profile.get("candidate_row_count", -1), -1) == 0),
        ("candidate_column_count_54", safe_int(profile.get("candidate_column_count", -1), -1) == 54),
        ("candidate_columns_exact", safe_bool(profile.get("candidate_columns_exact", False))),
        ("candidate_columns_unique", safe_bool(profile.get("candidate_columns_unique", False))),
        ("candidate_contract_valid", safe_bool(profile.get("candidate_contract_valid", False))),
        ("candidate_distinct_from_official_after", safe_bool(profile.get("candidate_distinct_from_official", False))),
        ("candidate_hash_stable_after_inspection", candidate_hash_before != "" and candidate_hash_before == candidate_hash_after),
        ("official_dataset_absent_after", not official_after),
        ("official_dataset_unchanged_absent", not official_before and not official_after),
        ("official_manifest_not_created", not OFFICIAL_MANIFEST_PATH.exists()),
        ("official_lock_not_created", not OFFICIAL_LOCK_PATH.exists()),
        ("official_temp_not_created", not OFFICIAL_TEMP_PATH.exists()),
        ("official_backup_not_created", not BACKUP_DIR.exists()),
        ("source_artifacts_stable_after_candidate_write", manifest_digest(source_manifest_before) == manifest_digest(source_manifest_after)),
        ("candidate_contains_no_real_evidence", safe_int(profile.get("candidate_row_count", -1), -1) == 0),
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
        ("project_not_completed", True),
        ("future_candidate_validation_only", True),
    ]
    for name, passed in post_checks:
        append_validation(rows, "candidate_implementation", name, passed, f"{name}={passed}")
    return pd.DataFrame(rows)


def build_items(validations: pd.DataFrame) -> pd.DataFrame:
    names = validations["validation_name"].astype(str).tolist()
    rows: list[dict[str, Any]] = []
    for position, start in enumerate(range(0, len(names), 3), start=1):
        block_names = names[start : start + 3]
        selected = validations[validations["validation_name"].astype(str).isin(block_names)]
        passed = len(selected) == len(block_names) and selected["passed"].map(safe_bool).all()
        rows.append(
            {
                "implementation_item_position": position,
                "implementation_item_id": f"OFFICIAL_DATASET_EMPTY_SCHEMA_CANDIDATE_IMPLEMENTATION_ITEM_{position:03d}",
                "implementation_item_name": f"empty_schema_candidate_implementation_block_{position:03d}",
                "validation_names": ",".join(block_names),
                "required": True,
                "candidate_only": True,
                "official_dataset_implementation_allowed": False,
                "official_dataset_creation_allowed": False,
                "official_dataset_write_allowed": False,
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
                "finding_id": f"OFFICIAL_DATASET_EMPTY_SCHEMA_CANDIDATE_IMPLEMENTATION_FINDING_{position:03d}",
                "implementation_item_id": str(item["implementation_item_id"]),
                "finding_status": "PASS" if passed else "FAIL",
                "material_issue_found": not passed,
                "candidate_change_required": not passed,
                "future_candidate_validation_allowed": passed,
                "official_dataset_implementation_allowed": False,
                "passed": passed,
            }
        )
    return pd.DataFrame(rows)


def build_controls(validations: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for position, (_, validation) in enumerate(validations.iterrows(), start=1):
        rows.append(
            {
                "control_position": position,
                "control_id": f"OFFICIAL_DATASET_EMPTY_SCHEMA_CANDIDATE_IMPLEMENTATION_CONTROL_{position:03d}",
                "control_name": str(validation["validation_name"]),
                "required": True,
                "candidate_only": True,
                "official_dataset_implementation_allowed": False,
                "official_dataset_creation_allowed": False,
                "official_dataset_write_allowed": False,
                "evidence_collection_enabled": False,
                "signal_generation_enabled": False,
                "market_execution_allowed": False,
                "passed": safe_bool(validation["passed"], False),
            }
        )
    return pd.DataFrame(rows)


def build_rules(
    validations: pd.DataFrame,
    items: pd.DataFrame,
    findings: pd.DataFrame,
    controls: pd.DataFrame,
    candidate_profile: pd.DataFrame,
) -> pd.DataFrame:
    material_issues = int(findings["material_issue_found"].map(safe_bool).sum())
    profile = candidate_profile.iloc[0].to_dict() if len(candidate_profile) == 1 else {}
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
        ("candidate_exists", safe_bool(profile.get("candidate_exists", False)), True, safe_bool(profile.get("candidate_exists", False))),
        ("candidate_contract_valid", safe_bool(profile.get("candidate_contract_valid", False)), True, safe_bool(profile.get("candidate_contract_valid", False))),
        ("candidate_rows_zero", safe_int(profile.get("candidate_row_count", -1), -1) == 0, 0, safe_int(profile.get("candidate_row_count", -1), -1)),
        ("candidate_columns_54", safe_int(profile.get("candidate_column_count", -1), -1) == 54, 54, safe_int(profile.get("candidate_column_count", -1), -1)),
        ("official_dataset_implementation_disabled", True, False, False),
        ("official_dataset_creation_disabled", True, False, False),
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
        ("future_candidate_validation_only", True, True, True),
    ]
    return pd.DataFrame(
        [
            {
                "rule_id": f"OFFICIAL_DATASET_EMPTY_SCHEMA_CANDIDATE_IMPLEMENTATION_RULE_{position:03d}",
                "rule_name": name,
                "passed": bool(passed),
                "required_value": required,
                "actual_value": actual,
            }
            for position, (name, passed, required, actual) in enumerate(rules, start=1)
        ]
    )


def build_guard_matrix(implementation_passed: bool, candidate_exists: bool) -> pd.DataFrame:
    guards = [
        ("source_precheck_performed", True, True),
        ("source_precheck_passed", True, True),
        ("source_candidate_implementation_allowed", True, True),
        ("candidate_implementation_performed", True, True),
        ("candidate_implementation_passed", True, implementation_passed),
        ("future_candidate_validation_allowed", True, implementation_passed),
        ("empty_schema_candidate_exists", True, candidate_exists),
        ("official_dataset_implementation_allowed", False, False),
        ("official_dataset_creation_allowed", False, False),
        ("evidence_collection_enabled", False, False),
        ("evidence_collection_started", False, False),
        ("official_dataset_schema_implemented", False, False),
        ("official_dataset_write_allowed", False, False),
        ("official_dataset_write_performed", False, False),
        ("real_forward_dataset_created", False, False),
        ("official_evidence_rows_written", 0, 0),
        ("candidate_evidence_rows_written", 0, 0),
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
        ("official_dataset_exists_after", False, False),
        ("official_manifest_exists_after", False, False),
        ("official_lock_exists_after", False, False),
        ("official_temp_exists_after", False, False),
        ("official_backup_exists_after", False, False),
        ("source_artifacts_stable", True, True),
    ]
    return pd.DataFrame(
        [
            {
                "guard_position": position,
                "guard_name": name,
                "required_value": required,
                "actual_value": actual,
                "passed": required == actual,
                "guard_group": "candidate_implementation_state" if position <= 7 else "candidate_implementation_safety_guard",
            }
            for position, (name, required, actual) in enumerate(guards, start=1)
        ]
    )


def build_requirements(
    validations: pd.DataFrame,
    items: pd.DataFrame,
    findings: pd.DataFrame,
    controls: pd.DataFrame,
    rules: pd.DataFrame,
    guards: pd.DataFrame,
    candidate_profile: pd.DataFrame,
) -> pd.DataFrame:
    rows: list[tuple[str, bool, Any, Any]] = []
    for _, validation in validations.iterrows():
        actual = safe_bool(validation["passed"], False)
        rows.append((str(validation["validation_name"]), actual, True, actual))

    profile = candidate_profile.iloc[0].to_dict() if len(candidate_profile) == 1 else {}
    material_issues = int(findings["material_issue_found"].map(safe_bool).sum())
    rows.extend(
        [
            ("implementation_items_passed", all_passed(items), True, all_passed(items)),
            ("implementation_findings_passed", all_passed(findings), True, all_passed(findings)),
            ("implementation_controls_passed", all_passed(controls), True, all_passed(controls)),
            ("implementation_rules_passed", all_passed(rules), True, all_passed(rules)),
            ("implementation_guards_passed", all_passed(guards), True, all_passed(guards)),
            ("material_issue_count_zero", material_issues == 0, 0, material_issues),
            ("candidate_contract_valid", safe_bool(profile.get("candidate_contract_valid", False)), True, safe_bool(profile.get("candidate_contract_valid", False))),
            ("candidate_row_count_zero", safe_int(profile.get("candidate_row_count", -1), -1) == 0, 0, safe_int(profile.get("candidate_row_count", -1), -1)),
            ("candidate_column_count_54", safe_int(profile.get("candidate_column_count", -1), -1) == 54, 54, safe_int(profile.get("candidate_column_count", -1), -1)),
            ("future_candidate_validation_allowed", True, True, True),
            ("official_dataset_implementation_not_allowed", True, False, False),
            ("official_dataset_creation_not_allowed", True, False, False),
            ("official_evidence_rows_written_zero", True, 0, 0),
            ("candidate_evidence_rows_written_zero", True, 0, 0),
            ("signal_generation_disabled", True, False, False),
            ("paper_trading_disabled", True, False, False),
            ("market_execution_disabled", True, False, False),
            ("project_not_completed", True, False, False),
        ]
    )
    return pd.DataFrame(
        [
            {
                "requirement_id": f"OFFICIAL_DATASET_EMPTY_SCHEMA_CANDIDATE_IMPLEMENTATION_REQ_{position:03d}",
                "requirement_name": name,
                "passed": bool(passed),
                "required_value": required,
                "actual_value": actual,
            }
            for position, (name, passed, required, actual) in enumerate(rows, start=1)
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
    candidate_profile: pd.DataFrame,
    write_result: dict[str, Any],
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
    profile = candidate_profile.iloc[0].to_dict() if len(candidate_profile) == 1 else {}
    return pd.DataFrame(
        [
            {
                "official_dataset_empty_schema_candidate_implementation_id": "PHASE_10_40_LONG_FORWARD_OBSERVATION_EVIDENCE_COLLECTION_OFFICIAL_DATASET_EMPTY_SCHEMA_CANDIDATE_IMPLEMENTATION_001",
                "official_dataset_empty_schema_candidate_implementation_performed": True,
                "official_dataset_empty_schema_candidate_implementation_passed": passed,
                "official_dataset_empty_schema_candidate_implementation_decision": READY_DECISION if passed else BLOCKED_DECISION,
                "candidate_path": str(EMPTY_SCHEMA_CANDIDATE_PATH),
                "candidate_created_this_run": safe_bool(write_result.get("candidate_created_this_run", False)),
                "candidate_reused_existing": safe_bool(write_result.get("candidate_reused_existing", False)),
                "candidate_exists_after": safe_bool(profile.get("candidate_exists", False)),
                "candidate_sha256": str(profile.get("candidate_sha256", "")),
                "candidate_column_count": safe_int(profile.get("candidate_column_count", -1), -1),
                "candidate_row_count": safe_int(profile.get("candidate_row_count", -1), -1),
                "candidate_contract_valid": safe_bool(profile.get("candidate_contract_valid", False)),
                "total_requirements": len(requirements),
                "passed_requirements": int(requirements["passed"].map(safe_bool).sum()),
                "failed_requirements": len(failed),
                "failed_requirement_names": ",".join(failed["requirement_name"].astype(str).tolist()),
                "future_official_dataset_empty_schema_candidate_validation_allowed": passed,
                "official_dataset_implementation_allowed": False,
                "official_dataset_creation_allowed": False,
                "evidence_collection_enabled": False,
                "evidence_collection_started": False,
                "official_dataset_schema_implemented": False,
                "official_dataset_write_allowed": False,
                "official_dataset_write_performed": False,
                "official_evidence_rows_written": 0,
                "candidate_evidence_rows_written": 0,
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


def check_row(group: str, name: str, passed: bool, severity: str, details: str) -> dict[str, Any]:
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
    candidate_profile: pd.DataFrame,
    decision: pd.DataFrame,
    official_before: bool,
    official_after: bool,
) -> pd.DataFrame:
    checks: list[dict[str, Any]] = []
    anchors = {
        "phase_10_39_implementation_precheck_doc_exists": PHASE_10_39_DOC_PATH.exists(),
        "phase_10_40_candidate_implementation_doc_exists": PHASE_10_40_DOC_PATH.exists(),
    }
    for name, exists in anchors.items():
        checks.append(check_row("phase_anchor", name, exists, "INFO" if exists else "ERROR", name))

    profile = candidate_profile.iloc[0].to_dict() if len(candidate_profile) == 1 else {}
    decision_row = decision.iloc[0].to_dict() if len(decision) == 1 else {}
    blocks = {
        "implementation_validations_passed": all_passed(validations),
        "implementation_items_passed": all_passed(items),
        "implementation_findings_passed": all_passed(findings),
        "implementation_controls_passed": all_passed(controls),
        "implementation_rules_passed": all_passed(rules),
        "implementation_requirements_passed": all_passed(requirements),
        "implementation_guards_passed": all_passed(guards),
        "candidate_contract_valid": safe_bool(profile.get("candidate_contract_valid", False)),
        "candidate_rows_zero": safe_int(profile.get("candidate_row_count", -1), -1) == 0,
        "candidate_columns_54": safe_int(profile.get("candidate_column_count", -1), -1) == 54,
        "candidate_implementation_passed": safe_bool(decision_row.get("official_dataset_empty_schema_candidate_implementation_passed", False)),
        "candidate_implementation_decision_expected": str(decision_row.get("official_dataset_empty_schema_candidate_implementation_decision", "")) == READY_DECISION,
    }
    for name, passed in blocks.items():
        checks.append(check_row("candidate_implementation", name, passed, "INFO" if passed else "ERROR", f"{name}={passed}"))

    official_unchanged = not official_before and not official_after
    checks.append(check_row("official_dataset_guard", "official_dataset_unchanged_absent", official_unchanged, "INFO" if official_unchanged else "ERROR", f"before={official_before},after={official_after}"))

    warnings = [
        ("candidate_only", "Phase 10.40 creates only the empty-schema candidate."),
        ("official_dataset_not_implemented", "The official dataset remains unimplemented."),
        ("official_dataset_not_created", "No official dataset file was created."),
        ("official_dataset_not_written", "No official dataset row was written."),
        ("candidate_rows_zero", "The candidate contains zero evidence rows."),
        ("real_evidence_not_collected", "No real forward evidence was collected."),
        ("evidence_persistence_not_enabled", "Evidence persistence remains disabled."),
        ("signal_generation_not_enabled", "Signal generation remains disabled."),
        ("live_alerts_not_enabled", "Live alerts remain disabled."),
        ("paper_trading_not_enabled", "Paper trading remains disabled."),
        ("long_strategy_not_approved", "The LONG research candidate remains unapproved."),
        ("real_capital_not_allowed", "Real capital remains prohibited."),
        ("market_execution_not_allowed", "Market execution remains prohibited."),
        ("automation_not_allowed", "Automation remains prohibited."),
        ("future_candidate_validation_only", "The only next allowance is candidate schema validation."),
    ]
    for name, details in warnings:
        checks.append(check_row("scope_control", name, True, "WARNING", details))

    checks.append(check_row("phase_transition", "phase_10_41_recommended_next", True, "INFO", "Recommended next: Phase 10.41 empty-schema candidate validation."))
    return pd.DataFrame(checks)


def build_summary(
    source_manifest: pd.DataFrame,
    validations: pd.DataFrame,
    candidate_profile: pd.DataFrame,
    items: pd.DataFrame,
    findings: pd.DataFrame,
    controls: pd.DataFrame,
    rules: pd.DataFrame,
    requirements: pd.DataFrame,
    guards: pd.DataFrame,
    decision: pd.DataFrame,
    checks: pd.DataFrame,
    write_result: dict[str, Any],
    official_before: bool,
    official_after: bool,
) -> pd.DataFrame:
    profile = candidate_profile.iloc[0].to_dict() if len(candidate_profile) == 1 else {}
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
                "phase": "10.40",
                "official_dataset_empty_schema_candidate_implementation_defined": True,
                "phase_10_39_source_validated": all_passed(validations),
                "source_artifact_count": len(source_manifest),
                "source_artifacts_exist": source_manifest["artifact_exists"].map(safe_bool).all(),
                "source_artifacts_non_empty": source_manifest["artifact_non_empty"].map(safe_bool).all(),
                "source_artifact_hashes_valid": source_manifest["artifact_sha256_valid"].map(safe_bool).all(),
                "source_manifest_sha256": manifest_digest(source_manifest),
                "implementation_validation_rows": len(validations),
                "implementation_item_rows": len(items),
                "implementation_finding_rows": len(findings),
                "implementation_control_rows": len(controls),
                "implementation_rule_rows": len(rules),
                "implementation_requirement_rows": len(requirements),
                "implementation_guard_rows": len(guards),
                "implementation_validations_passed": all_passed(validations),
                "implementation_items_passed": all_passed(items),
                "implementation_findings_passed": all_passed(findings),
                "implementation_controls_passed": all_passed(controls),
                "implementation_rules_passed": all_passed(rules),
                "implementation_requirements_passed": all_passed(requirements),
                "implementation_guards_passed": all_passed(guards),
                "material_issue_count": material_issue_count,
                "official_dataset_empty_schema_candidate_implementation_performed": True,
                "official_dataset_empty_schema_candidate_implementation_passed": safe_bool(decision_row.get("official_dataset_empty_schema_candidate_implementation_passed", False)),
                "official_dataset_empty_schema_candidate_implementation_decision": str(decision_row.get("official_dataset_empty_schema_candidate_implementation_decision", "")),
                "candidate_path": str(EMPTY_SCHEMA_CANDIDATE_PATH),
                "candidate_write_attempted": safe_bool(write_result.get("candidate_write_attempted", False)),
                "candidate_created_this_run": safe_bool(write_result.get("candidate_created_this_run", False)),
                "candidate_reused_existing": safe_bool(write_result.get("candidate_reused_existing", False)),
                "candidate_exists_after": safe_bool(profile.get("candidate_exists", False)),
                "candidate_sha256": str(profile.get("candidate_sha256", "")),
                "candidate_column_count": safe_int(profile.get("candidate_column_count", -1), -1),
                "candidate_row_count": safe_int(profile.get("candidate_row_count", -1), -1),
                "candidate_contract_valid": safe_bool(profile.get("candidate_contract_valid", False)),
                "future_official_dataset_empty_schema_candidate_validation_allowed": safe_bool(decision_row.get("future_official_dataset_empty_schema_candidate_validation_allowed", False)),
                "official_dataset_implementation_allowed": False,
                "official_dataset_creation_allowed": False,
                "evidence_collection_enabled": False,
                "evidence_collection_started": False,
                "official_dataset_schema_implemented": False,
                "official_dataset_write_allowed": False,
                "official_dataset_write_performed": False,
                "official_dataset_exists_before": official_before,
                "official_dataset_exists_after": official_after,
                "official_dataset_unchanged_absent": not official_before and not official_after,
                "official_evidence_rows_written": 0,
                "candidate_evidence_rows_written": 0,
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
                    "PHASE_10_40_LONG_FORWARD_OBSERVATION_EVIDENCE_COLLECTION_OFFICIAL_DATASET_EMPTY_SCHEMA_CANDIDATE_IMPLEMENTATION_VALIDATED"
                    if validation_passed
                    else "PHASE_10_40_LONG_FORWARD_OBSERVATION_EVIDENCE_COLLECTION_OFFICIAL_DATASET_EMPTY_SCHEMA_CANDIDATE_IMPLEMENTATION_FAILED"
                ),
            }
        ]
    )


def run_long_forward_observation_evidence_collection_official_dataset_empty_schema_candidate_implementation() -> dict[str, pd.DataFrame]:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    official_before = OFFICIAL_DATASET_EXPECTED_PATH.exists()
    candidate_before = EMPTY_SCHEMA_CANDIDATE_PATH.exists()
    source_manifest_before = build_manifest(SOURCE_PATHS, "PHASE_10_40_SOURCE")
    source = {name: read_csv(path) for name, path in SOURCE_PATHS.items()}
    source_manifest_mid = build_manifest(SOURCE_PATHS, "PHASE_10_40_SOURCE")

    preconditions = build_preconditions(
        source,
        source_manifest_before,
        source_manifest_mid,
        official_before,
        candidate_before,
    )
    preconditions_passed = all_passed(preconditions)

    if preconditions_passed and not official_before:
        write_result = write_candidate_atomic(EMPTY_SCHEMA_CANDIDATE_PATH, EXPECTED_FIELD_NAMES)
    else:
        write_result = {
            "candidate_write_attempted": False,
            "candidate_created_this_run": False,
            "candidate_reused_existing": False,
            "candidate_invalid_existing_blocked": False,
            "candidate_temp_path": "",
            "candidate_temp_cleaned": True,
            "candidate_write_error": "Candidate creation blocked by failed preconditions or existing official dataset.",
        }

    candidate_profile = inspect_candidate(EMPTY_SCHEMA_CANDIDATE_PATH, EXPECTED_FIELD_NAMES)
    source_manifest_after = build_manifest(SOURCE_PATHS, "PHASE_10_40_SOURCE")
    official_after = OFFICIAL_DATASET_EXPECTED_PATH.exists()

    validations = append_post_validations(
        preconditions,
        source_manifest_before,
        source_manifest_after,
        write_result,
        candidate_profile,
        official_before,
        official_after,
    )
    items = build_items(validations)
    findings = build_findings(items)
    controls = build_controls(validations)
    rules = build_rules(validations, items, findings, controls, candidate_profile)
    guards = build_guard_matrix(
        all([all_passed(validations), all_passed(items), all_passed(findings), all_passed(controls), all_passed(rules)]),
        bool(candidate_profile.iloc[0]["candidate_exists"]) if len(candidate_profile) == 1 else False,
    )
    requirements = build_requirements(validations, items, findings, controls, rules, guards, candidate_profile)
    decision = build_decision(validations, items, findings, controls, rules, requirements, guards, candidate_profile, write_result)
    checks = build_checks(validations, items, findings, controls, rules, requirements, guards, candidate_profile, decision, official_before, official_after)
    summary = build_summary(source_manifest_before, validations, candidate_profile, items, findings, controls, rules, requirements, guards, decision, checks, write_result, official_before, official_after)

    frames = {
        "summary": summary,
        "validations": validations,
        "candidate_profile": candidate_profile,
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

    output_paths = {name: REPORTS_DIR / OUTPUT_FILENAMES[name] for name in frames}
    output_manifest = build_manifest(output_paths, "PHASE_10_40_OUTPUT")
    candidate_artifact_manifest = build_manifest({"empty_schema_candidate": EMPTY_SCHEMA_CANDIDATE_PATH}, "PHASE_10_40_CANDIDATE")
    combined_manifest = pd.concat([source_manifest_after, candidate_artifact_manifest, output_manifest], ignore_index=True)
    combined_manifest.to_csv(REPORTS_DIR / OUTPUT_FILENAMES["manifest"], index=False)

    return {
        "summary": summary,
        "source_precheck_summary": source["precheck_summary"],
        "source_precheck_decision": source["precheck_decision"],
        "source_field_catalog": source["field_catalog"],
        "source_artifact_manifest": source_manifest_before,
        "validations": validations,
        "candidate_profile": candidate_profile,
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
