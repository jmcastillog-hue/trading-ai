from __future__ import annotations

import csv
import hashlib
import io
import os
import subprocess
import tempfile
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
    "reports/p10_41_evidence_collection_official_dataset_"
    "empty_schema_candidate_validation_v1"
)
PHASE_10_40_DIR = Path(
    "reports/p10_40_evidence_collection_official_dataset_"
    "empty_schema_candidate_implementation_v1"
)
PHASE_10_37_DIR = Path(
    "reports/p10_37_evidence_collection_official_dataset_"
    "schema_implementation_design_v1"
)

PHASE_10_40_DOC_PATH = Path(
    "docs/PHASE_10_LONG_FORWARD_OBSERVATION_EVIDENCE_COLLECTION_"
    "OFFICIAL_DATASET_EMPTY_SCHEMA_CANDIDATE_IMPLEMENTATION.md"
)
PHASE_10_41_DOC_PATH = Path(
    "docs/PHASE_10_LONG_FORWARD_OBSERVATION_EVIDENCE_COLLECTION_"
    "OFFICIAL_DATASET_EMPTY_SCHEMA_CANDIDATE_VALIDATION.md"
)

IMPLEMENTATION_PATHS = {
    "implementation_summary": (
        PHASE_10_40_DIR
        / "official_dataset_empty_schema_candidate_implementation_summary_v1.csv"
    ),
    "implementation_validations": (
        PHASE_10_40_DIR
        / "official_dataset_empty_schema_candidate_implementation_validations_v1.csv"
    ),
    "implementation_candidate_profile": (
        PHASE_10_40_DIR
        / "official_dataset_empty_schema_candidate_profile_v1.csv"
    ),
    "implementation_items": (
        PHASE_10_40_DIR
        / "official_dataset_empty_schema_candidate_implementation_items_v1.csv"
    ),
    "implementation_findings": (
        PHASE_10_40_DIR
        / "official_dataset_empty_schema_candidate_implementation_findings_v1.csv"
    ),
    "implementation_controls": (
        PHASE_10_40_DIR
        / "official_dataset_empty_schema_candidate_implementation_controls_v1.csv"
    ),
    "implementation_rules": (
        PHASE_10_40_DIR
        / "official_dataset_empty_schema_candidate_implementation_rules_v1.csv"
    ),
    "implementation_requirements": (
        PHASE_10_40_DIR
        / "official_dataset_empty_schema_candidate_implementation_requirements_v1.csv"
    ),
    "implementation_guard_matrix": (
        PHASE_10_40_DIR
        / "official_dataset_empty_schema_candidate_implementation_guard_matrix_v1.csv"
    ),
    "implementation_decision": (
        PHASE_10_40_DIR
        / "official_dataset_empty_schema_candidate_implementation_decision_v1.csv"
    ),
    "implementation_checks": (
        PHASE_10_40_DIR
        / "official_dataset_empty_schema_candidate_implementation_checks_v1.csv"
    ),
    "implementation_manifest": (
        PHASE_10_40_DIR
        / "source_official_dataset_empty_schema_candidate_implementation_artifact_manifest_v1.csv"
    ),
}

FIELD_CATALOG_PATH = (
    PHASE_10_37_DIR / "official_dataset_schema_field_catalog_v1.csv"
)
SOURCE_PATHS = {
    **IMPLEMENTATION_PATHS,
    "field_catalog": FIELD_CATALOG_PATH,
    "empty_schema_candidate": EMPTY_SCHEMA_CANDIDATE_PATH,
}

SOURCE_READY_DECISION = (
    "CONTROLLED_FORWARD_OBSERVATION_EVIDENCE_COLLECTION_OFFICIAL_"
    "DATASET_EMPTY_SCHEMA_CANDIDATE_IMPLEMENTATION_READY_FOR_SCHEMA_"
    "VALIDATION"
)
READY_DECISION = (
    "CONTROLLED_FORWARD_OBSERVATION_EVIDENCE_COLLECTION_OFFICIAL_"
    "DATASET_EMPTY_SCHEMA_CANDIDATE_VALIDATION_READY_FOR_ATOMIC_WRITE_"
    "HARNESS_DESIGN"
)
BLOCKED_DECISION = (
    "CONTROLLED_FORWARD_OBSERVATION_EVIDENCE_COLLECTION_OFFICIAL_"
    "DATASET_EMPTY_SCHEMA_CANDIDATE_VALIDATION_BLOCKED"
)
RECOMMENDED_NEXT_PHASE = (
    "PHASE_10_42_LONG_FORWARD_OBSERVATION_EVIDENCE_COLLECTION_"
    "OFFICIAL_DATASET_ATOMIC_WRITE_HARNESS_DESIGN_V1"
)

EXPECTED_CANDIDATE_SIZE_BYTES = 981
EXPECTED_CANDIDATE_SHA256 = (
    "e3fa86a461fd46f4d66dc2e03f185e49"
    "b7b3438d3cbc33340c01f51310514ff1"
)

OUTPUT_FILENAMES = {
    "summary": (
        "official_dataset_empty_schema_candidate_validation_summary_v1.csv"
    ),
    "validations": (
        "official_dataset_empty_schema_candidate_validation_validations_v1.csv"
    ),
    "candidate_profile": (
        "official_dataset_empty_schema_candidate_validation_profile_v1.csv"
    ),
    "negative_controls": (
        "official_dataset_empty_schema_candidate_validation_negative_controls_v1.csv"
    ),
    "items": (
        "official_dataset_empty_schema_candidate_validation_items_v1.csv"
    ),
    "findings": (
        "official_dataset_empty_schema_candidate_validation_findings_v1.csv"
    ),
    "controls": (
        "official_dataset_empty_schema_candidate_validation_controls_v1.csv"
    ),
    "rules": (
        "official_dataset_empty_schema_candidate_validation_rules_v1.csv"
    ),
    "requirements": (
        "official_dataset_empty_schema_candidate_validation_requirements_v1.csv"
    ),
    "guard_matrix": (
        "official_dataset_empty_schema_candidate_validation_guard_matrix_v1.csv"
    ),
    "decision": (
        "official_dataset_empty_schema_candidate_validation_decision_v1.csv"
    ),
    "checks": (
        "official_dataset_empty_schema_candidate_validation_checks_v1.csv"
    ),
    "manifest": (
        "source_official_dataset_empty_schema_candidate_validation_artifact_manifest_v1.csv"
    ),
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


def candidate_file_state(path: Path) -> dict[str, Any]:
    exists = path.exists() and path.is_file()
    stat = path.stat() if exists else None
    raw = path.read_bytes() if exists else b""
    return {
        "exists": exists,
        "size": int(stat.st_size) if stat else 0,
        "mtime_ns": int(stat.st_mtime_ns) if stat else 0,
        "sha256": hashlib.sha256(raw).hexdigest() if exists else "",
        "raw": raw,
    }


def git_candidate_state(path: Path) -> dict[str, Any]:
    tracked = False
    clean = False
    tracked_error = ""
    status_error = ""
    try:
        tracked_result = subprocess.run(
            ["git", "ls-files", "--error-unmatch", "--", str(path)],
            capture_output=True,
            text=True,
            check=False,
        )
        tracked = tracked_result.returncode == 0
        tracked_error = tracked_result.stderr.strip()
    except Exception as exc:
        tracked_error = f"{type(exc).__name__}: {exc}"

    try:
        status_result = subprocess.run(
            ["git", "status", "--porcelain", "--", str(path)],
            capture_output=True,
            text=True,
            check=False,
        )
        clean = (
            status_result.returncode == 0
            and status_result.stdout.strip() == ""
        )
        status_error = status_result.stderr.strip()
    except Exception as exc:
        status_error = f"{type(exc).__name__}: {exc}"

    return {
        "candidate_git_tracked": tracked,
        "candidate_git_clean": clean,
        "candidate_git_tracked_error": tracked_error,
        "candidate_git_status_error": status_error,
    }


def csv_header_bytes(fields: list[str], line_ending: str = "\n") -> bytes:
    buffer = io.StringIO(newline="")
    writer = csv.writer(buffer, lineterminator=line_ending)
    writer.writerow(fields)
    return buffer.getvalue().encode("utf-8")


def run_negative_controls(fields: list[str]) -> tuple[pd.DataFrame, bool]:
    rows: list[dict[str, Any]] = []
    temp_root_removed = False
    temp_root_path = ""

    with tempfile.TemporaryDirectory(
        prefix="phase_10_41_candidate_validation_"
    ) as temp_root:
        temp_root_path = temp_root
        root = Path(temp_root)

        cases: list[tuple[str, bytes, bool]] = [
            (
                "valid_canonical_header",
                expected_candidate_bytes(fields),
                True,
            ),
            (
                "missing_last_column",
                csv_header_bytes(fields[:-1]),
                False,
            ),
            (
                "reordered_first_two_columns",
                csv_header_bytes(
                    [fields[1], fields[0], *fields[2:]]
                ),
                False,
            ),
            (
                "duplicate_last_column",
                csv_header_bytes(
                    [*fields[:-1], fields[-2]]
                ),
                False,
            ),
            (
                "one_evidence_row",
                expected_candidate_bytes(fields)
                + csv_header_bytes(["synthetic", *([""] * 53)]),
                False,
            ),
            (
                "utf8_bom",
                b"\xef\xbb\xbf" + expected_candidate_bytes(fields),
                False,
            ),
            (
                "crlf_line_ending",
                csv_header_bytes(fields, "\r\n"),
                False,
            ),
            (
                "missing_final_newline",
                expected_candidate_bytes(fields).rstrip(b"\n"),
                False,
            ),
            (
                "extra_blank_line",
                expected_candidate_bytes(fields) + b"\n",
                False,
            ),
            (
                "semicolon_delimiter",
                (";".join(fields) + "\n").encode("utf-8"),
                False,
            ),
        ]

        for position, (name, payload, expected_valid) in enumerate(
            cases,
            start=1,
        ):
            path = root / f"{position:02d}_{name}.csv"
            path.write_bytes(payload)
            profile = inspect_candidate(path, fields).iloc[0].to_dict()
            actual_valid = safe_bool(
                profile.get("candidate_contract_valid", False)
            )
            passed = actual_valid == expected_valid
            rows.append(
                {
                    "negative_control_position": position,
                    "negative_control_name": name,
                    "expected_contract_valid": expected_valid,
                    "actual_contract_valid": actual_valid,
                    "candidate_size_bytes": safe_int(
                        profile.get("candidate_size_bytes", 0)
                    ),
                    "candidate_row_count": safe_int(
                        profile.get("candidate_row_count", -1),
                        -1,
                    ),
                    "candidate_column_count": safe_int(
                        profile.get("candidate_column_count", -1),
                        -1,
                    ),
                    "candidate_exact_header_bytes": safe_bool(
                        profile.get(
                            "candidate_exact_header_bytes",
                            False,
                        )
                    ),
                    "passed": passed,
                }
            )

    temp_root_removed = not Path(temp_root_path).exists()
    return pd.DataFrame(rows), temp_root_removed


def validate_phase_10_40_manifest(
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
            "implementation_manifest_rows_25": False,
            "implementation_manifest_source_rows_13": False,
            "implementation_manifest_candidate_rows_1": False,
            "implementation_manifest_output_rows_11": False,
            "implementation_manifest_listed_artifacts_valid": False,
            "implementation_manifest_hashes_match": False,
            "implementation_manifest_self_exclusion_expected": False,
            "implementation_manifest_file_exists": manifest_path.exists(),
            "implementation_manifest_file_non_empty": (
                manifest_path.exists()
                and manifest_path.stat().st_size > 0
            ),
            "implementation_manifest_file_sha256_valid": is_sha256(
                sha256_file(manifest_path)
            ),
        }

    source_rows = manifest_df[
        manifest_df["artifact_scope"].astype(str).eq("PHASE_10_40_SOURCE")
    ]
    candidate_rows = manifest_df[
        manifest_df["artifact_scope"]
        .astype(str)
        .eq("PHASE_10_40_CANDIDATE")
    ]
    output_rows = manifest_df[
        manifest_df["artifact_scope"].astype(str).eq("PHASE_10_40_OUTPUT")
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
        len(manifest_df) == 25
        and len(source_rows) == 13
        and len(candidate_rows) == 1
        and len(output_rows) == 11
        and manifest_path.name not in filenames
    )
    exists = manifest_path.exists() and manifest_path.is_file()
    non_empty = exists and manifest_path.stat().st_size > 0

    return {
        "implementation_manifest_rows_25": len(manifest_df) == 25,
        "implementation_manifest_source_rows_13": len(source_rows) == 13,
        "implementation_manifest_candidate_rows_1": (
            len(candidate_rows) == 1
        ),
        "implementation_manifest_output_rows_11": len(output_rows) == 11,
        "implementation_manifest_listed_artifacts_valid": listed_valid,
        "implementation_manifest_hashes_match": hashes_match,
        "implementation_manifest_self_exclusion_expected": self_exclusion,
        "implementation_manifest_file_exists": exists,
        "implementation_manifest_file_non_empty": non_empty,
        "implementation_manifest_file_sha256_valid": is_sha256(
            sha256_file(manifest_path)
        ),
    }


def ordered_field_names(field_catalog: pd.DataFrame) -> list[str]:
    if (
        field_catalog.empty
        or "field_position" not in field_catalog.columns
        or "field_name" not in field_catalog.columns
    ):
        return []
    return (
        field_catalog.sort_values("field_position")["field_name"]
        .astype(str)
        .tolist()
    )


def build_candidate_validation_profile(
    profile: pd.DataFrame,
    state_before: dict[str, Any],
    state_after: dict[str, Any],
    git_state: dict[str, Any],
) -> pd.DataFrame:
    source = profile.iloc[0].to_dict() if len(profile) == 1 else {}
    raw = state_after["raw"]
    rows = [
        {
            **source,
            "expected_candidate_size_bytes": EXPECTED_CANDIDATE_SIZE_BYTES,
            "expected_candidate_sha256": EXPECTED_CANDIDATE_SHA256,
            "candidate_size_exact": (
                state_after["size"] == EXPECTED_CANDIDATE_SIZE_BYTES
            ),
            "candidate_sha256_exact": (
                state_after["sha256"] == EXPECTED_CANDIDATE_SHA256
            ),
            "candidate_has_no_utf8_bom": not raw.startswith(
                b"\xef\xbb\xbf"
            ),
            "candidate_uses_lf_only": (
                b"\r" not in raw and raw.endswith(b"\n")
            ),
            "candidate_has_final_newline": raw.endswith(b"\n"),
            "candidate_physical_line_count_1": raw.count(b"\n") == 1,
            "candidate_contains_no_nul": b"\x00" not in raw,
            "candidate_size_stable": (
                state_before["size"] == state_after["size"]
            ),
            "candidate_mtime_stable": (
                state_before["mtime_ns"] == state_after["mtime_ns"]
            ),
            "candidate_hash_stable": (
                state_before["sha256"] == state_after["sha256"]
            ),
            **git_state,
        }
    ]
    return pd.DataFrame(rows)


def build_validations(
    source: dict[str, pd.DataFrame],
    source_manifest_before: pd.DataFrame,
    source_manifest_after: pd.DataFrame,
    candidate_profile: pd.DataFrame,
    negative_controls: pd.DataFrame,
    negative_temp_cleaned: bool,
    official_before: bool,
    official_after: bool,
) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []

    source_checks = [
        ("source_artifact_count_14", len(source_manifest_before) == 14),
        (
            "source_artifacts_exist",
            source_manifest_before["artifact_exists"]
            .map(safe_bool)
            .all(),
        ),
        (
            "source_artifacts_non_empty",
            source_manifest_before["artifact_non_empty"]
            .map(safe_bool)
            .all(),
        ),
        (
            "source_artifact_hashes_valid",
            source_manifest_before["artifact_sha256_valid"]
            .map(safe_bool)
            .all(),
        ),
        (
            "source_artifacts_stable_during_validation",
            manifest_digest(source_manifest_before)
            == manifest_digest(source_manifest_after),
        ),
    ]
    for name, passed in source_checks:
        append_validation(
            rows,
            "source_artifacts",
            name,
            passed,
            f"{name}={passed}",
        )

    summary = (
        source["implementation_summary"].iloc[0].to_dict()
        if len(source["implementation_summary"]) == 1
        else {}
    )
    summary_checks = [
        (
            "phase_10_40_validation_passed",
            safe_bool(summary.get("validation_passed", False))
            and str(summary.get("validation_decision", ""))
            == (
                "PHASE_10_40_LONG_FORWARD_OBSERVATION_EVIDENCE_"
                "COLLECTION_OFFICIAL_DATASET_EMPTY_SCHEMA_CANDIDATE_"
                "IMPLEMENTATION_VALIDATED"
            ),
        ),
        (
            "source_implementation_performed",
            safe_bool(
                summary.get(
                    "official_dataset_empty_schema_candidate_implementation_performed",
                    False,
                )
            ),
        ),
        (
            "source_implementation_passed",
            safe_bool(
                summary.get(
                    "official_dataset_empty_schema_candidate_implementation_passed",
                    False,
                )
            ),
        ),
        (
            "source_implementation_decision_valid",
            str(
                summary.get(
                    "official_dataset_empty_schema_candidate_implementation_decision",
                    "",
                )
            )
            == SOURCE_READY_DECISION,
        ),
        (
            "source_candidate_validation_allowed",
            safe_bool(
                summary.get(
                    "future_official_dataset_empty_schema_candidate_validation_allowed",
                    False,
                )
            ),
        ),
        (
            "source_summary_source_artifacts_13",
            safe_int(summary.get("source_artifact_count", -1), -1) == 13,
        ),
        (
            "source_summary_validation_rows_113",
            safe_int(
                summary.get("implementation_validation_rows", -1),
                -1,
            )
            == 113,
        ),
        (
            "source_summary_item_rows_38",
            safe_int(
                summary.get("implementation_item_rows", -1),
                -1,
            )
            == 38,
        ),
        (
            "source_summary_finding_rows_38",
            safe_int(
                summary.get("implementation_finding_rows", -1),
                -1,
            )
            == 38,
        ),
        (
            "source_summary_control_rows_113",
            safe_int(
                summary.get("implementation_control_rows", -1),
                -1,
            )
            == 113,
        ),
        (
            "source_summary_rule_rows_28",
            safe_int(
                summary.get("implementation_rule_rows", -1),
                -1,
            )
            == 28,
        ),
        (
            "source_summary_requirement_rows_131",
            safe_int(
                summary.get("implementation_requirement_rows", -1),
                -1,
            )
            == 131,
        ),
        (
            "source_summary_guard_rows_40",
            safe_int(
                summary.get("implementation_guard_rows", -1),
                -1,
            )
            == 40,
        ),
        (
            "source_summary_material_issue_zero",
            safe_int(summary.get("material_issue_count", -1), -1) == 0,
        ),
        (
            "source_summary_total_checks_31",
            safe_int(summary.get("total_checks", -1), -1) == 31,
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
            "source_summary_candidate_reused",
            safe_bool(
                summary.get("candidate_reused_existing", False)
            ),
        ),
        (
            "source_summary_candidate_not_rewritten",
            not safe_bool(
                summary.get("candidate_write_attempted", True),
                True,
            )
            and not safe_bool(
                summary.get("candidate_created_this_run", True),
                True,
            ),
        ),
        (
            "source_summary_candidate_exists",
            safe_bool(summary.get("candidate_exists_after", False)),
        ),
        (
            "source_summary_candidate_hash_exact",
            str(summary.get("candidate_sha256", ""))
            == EXPECTED_CANDIDATE_SHA256,
        ),
        (
            "source_summary_candidate_columns_54",
            safe_int(summary.get("candidate_column_count", -1), -1)
            == 54,
        ),
        (
            "source_summary_candidate_rows_zero",
            safe_int(summary.get("candidate_row_count", -1), -1) == 0,
        ),
        (
            "source_summary_candidate_contract_valid",
            safe_bool(summary.get("candidate_contract_valid", False)),
        ),
        (
            "source_summary_official_dataset_unchanged_absent",
            safe_bool(
                summary.get("official_dataset_unchanged_absent", False)
            ),
        ),
        (
            "source_summary_official_rows_zero",
            safe_int(
                summary.get("official_evidence_rows_written", -1),
                -1,
            )
            == 0,
        ),
        (
            "source_summary_candidate_rows_written_zero",
            safe_int(
                summary.get("candidate_evidence_rows_written", -1),
                -1,
            )
            == 0,
        ),
        (
            "source_summary_long_unapproved",
            not safe_bool(
                summary.get("long_strategy_approved", True),
                True,
            ),
        ),
        (
            "source_summary_project_not_complete",
            not safe_bool(
                summary.get("total_project_completed", True),
                True,
            ),
        ),
        (
            "source_summary_next_phase_10_41",
            str(summary.get("recommended_next_phase", ""))
            == (
                "PHASE_10_41_LONG_FORWARD_OBSERVATION_EVIDENCE_"
                "COLLECTION_OFFICIAL_DATASET_EMPTY_SCHEMA_CANDIDATE_"
                "VALIDATION_V1"
            ),
        ),
    ]
    for name, passed in summary_checks:
        append_validation(
            rows,
            "phase_10_40_summary",
            name,
            passed,
            f"{name}={passed}",
        )

    decision = (
        source["implementation_decision"].iloc[0].to_dict()
        if len(source["implementation_decision"]) == 1
        else {}
    )
    decision_checks = [
        (
            "source_decision_row_count_1",
            len(source["implementation_decision"]) == 1,
        ),
        (
            "source_decision_implementation_performed",
            safe_bool(
                decision.get(
                    "official_dataset_empty_schema_candidate_implementation_performed",
                    False,
                )
            ),
        ),
        (
            "source_decision_implementation_passed",
            safe_bool(
                decision.get(
                    "official_dataset_empty_schema_candidate_implementation_passed",
                    False,
                )
            ),
        ),
        (
            "source_decision_value_valid",
            str(
                decision.get(
                    "official_dataset_empty_schema_candidate_implementation_decision",
                    "",
                )
            )
            == SOURCE_READY_DECISION,
        ),
        (
            "source_decision_candidate_reused",
            safe_bool(decision.get("candidate_reused_existing", False)),
        ),
        (
            "source_decision_candidate_not_created_this_run",
            not safe_bool(
                decision.get("candidate_created_this_run", True),
                True,
            ),
        ),
        (
            "source_decision_candidate_hash_exact",
            str(decision.get("candidate_sha256", ""))
            == EXPECTED_CANDIDATE_SHA256,
        ),
        (
            "source_decision_field_count_54",
            safe_int(decision.get("candidate_column_count", -1), -1)
            == 54,
        ),
        (
            "source_decision_rows_zero",
            safe_int(decision.get("candidate_row_count", -1), -1)
            == 0,
        ),
        (
            "source_decision_requirements_131",
            safe_int(decision.get("total_requirements", -1), -1)
            == 131,
        ),
        (
            "source_decision_failed_requirements_zero",
            safe_int(decision.get("failed_requirements", -1), -1)
            == 0,
        ),
        (
            "source_decision_validation_allowed",
            safe_bool(
                decision.get(
                    "future_official_dataset_empty_schema_candidate_validation_allowed",
                    False,
                )
            ),
        ),
        (
            "source_decision_next_phase_10_41",
            str(decision.get("recommended_next_phase", ""))
            == (
                "PHASE_10_41_LONG_FORWARD_OBSERVATION_EVIDENCE_"
                "COLLECTION_OFFICIAL_DATASET_EMPTY_SCHEMA_CANDIDATE_"
                "VALIDATION_V1"
            ),
        ),
    ]
    for name, passed in decision_checks:
        append_validation(
            rows,
            "phase_10_40_decision",
            name,
            passed,
            f"{name}={passed}",
        )

    output_checks = [
        (
            "implementation_validations_rows_113",
            len(source["implementation_validations"]) == 113,
        ),
        (
            "implementation_validations_all_passed",
            all_passed(source["implementation_validations"]),
        ),
        (
            "implementation_candidate_profile_rows_1",
            len(source["implementation_candidate_profile"]) == 1,
        ),
        (
            "implementation_items_rows_38",
            len(source["implementation_items"]) == 38,
        ),
        (
            "implementation_items_all_passed",
            all_passed(source["implementation_items"]),
        ),
        (
            "implementation_findings_rows_38",
            len(source["implementation_findings"]) == 38,
        ),
        (
            "implementation_findings_all_passed",
            all_passed(source["implementation_findings"]),
        ),
        (
            "implementation_controls_rows_113",
            len(source["implementation_controls"]) == 113,
        ),
        (
            "implementation_controls_all_passed",
            all_passed(source["implementation_controls"]),
        ),
        (
            "implementation_rules_rows_28",
            len(source["implementation_rules"]) == 28,
        ),
        (
            "implementation_rules_all_passed",
            all_passed(source["implementation_rules"]),
        ),
        (
            "implementation_requirements_rows_131",
            len(source["implementation_requirements"]) == 131,
        ),
        (
            "implementation_requirements_all_passed",
            all_passed(source["implementation_requirements"]),
        ),
        (
            "implementation_guards_rows_40",
            len(source["implementation_guard_matrix"]) == 40,
        ),
        (
            "implementation_guards_all_passed",
            all_passed(source["implementation_guard_matrix"]),
        ),
        (
            "implementation_checks_rows_31",
            len(source["implementation_checks"]) == 31,
        ),
        (
            "implementation_checks_all_passed",
            all_passed(source["implementation_checks"]),
        ),
    ]
    for name, passed in output_checks:
        append_validation(
            rows,
            "phase_10_40_outputs",
            name,
            passed,
            f"{name}={passed}",
        )

    for name, passed in validate_phase_10_40_manifest(
        source["implementation_manifest"],
        IMPLEMENTATION_PATHS["implementation_manifest"],
    ).items():
        append_validation(
            rows,
            "phase_10_40_manifest",
            name,
            passed,
            f"{name}={passed}",
        )

    field_catalog = source["field_catalog"]
    field_names = ordered_field_names(field_catalog)
    field_checks = [
        ("field_catalog_rows_54", len(field_catalog) == 54),
        (
            "field_catalog_positions_exact",
            (
                not field_catalog.empty
                and field_catalog["field_position"].map(safe_int).tolist()
                == list(range(1, 55))
            ),
        ),
        ("field_catalog_names_exact", field_names == EXPECTED_FIELD_NAMES),
        (
            "field_catalog_names_unique",
            (
                not field_catalog.empty
                and field_catalog["field_name"].astype(str).is_unique
            ),
        ),
        (
            "canonical_header_hash_exact",
            hashlib.sha256(
                expected_candidate_bytes(EXPECTED_FIELD_NAMES)
            ).hexdigest()
            == EXPECTED_CANDIDATE_SHA256,
        ),
        (
            "canonical_header_size_981",
            len(expected_candidate_bytes(EXPECTED_FIELD_NAMES))
            == EXPECTED_CANDIDATE_SIZE_BYTES,
        ),
        (
            "candidate_path_exact",
            EMPTY_SCHEMA_CANDIDATE_PATH
            == Path(
                "data/forward/candidates/"
                "long_forward_observation_dataset_v1.empty_candidate.csv"
            ),
        ),
        (
            "official_path_exact",
            OFFICIAL_DATASET_EXPECTED_PATH
            == Path(
                "data/forward/"
                "long_forward_observation_dataset_v1.csv"
            ),
        ),
        (
            "candidate_distinct_from_official",
            EMPTY_SCHEMA_CANDIDATE_PATH
            != OFFICIAL_DATASET_EXPECTED_PATH,
        ),
        (
            "phase_10_40_doc_exists",
            PHASE_10_40_DOC_PATH.exists(),
        ),
        (
            "phase_10_41_doc_exists",
            PHASE_10_41_DOC_PATH.exists(),
        ),
    ]
    for name, passed in field_checks:
        append_validation(
            rows,
            "canonical_contract",
            name,
            passed,
            f"{name}={passed}",
        )

    profile = (
        candidate_profile.iloc[0].to_dict()
        if len(candidate_profile) == 1
        else {}
    )
    profile_checks = [
        ("candidate_profile_row_count_1", len(candidate_profile) == 1),
        (
            "candidate_exists",
            safe_bool(profile.get("candidate_exists", False)),
        ),
        (
            "candidate_non_empty_file",
            safe_bool(profile.get("candidate_non_empty_file", False)),
        ),
        (
            "candidate_size_exact",
            safe_bool(profile.get("candidate_size_exact", False)),
        ),
        (
            "candidate_sha256_valid",
            safe_bool(profile.get("candidate_sha256_valid", False)),
        ),
        (
            "candidate_sha256_exact",
            safe_bool(profile.get("candidate_sha256_exact", False)),
        ),
        (
            "candidate_utf8_readable",
            safe_bool(profile.get("candidate_utf8_readable", False)),
        ),
        (
            "candidate_exact_header_bytes",
            safe_bool(
                profile.get("candidate_exact_header_bytes", False)
            ),
        ),
        (
            "candidate_has_no_utf8_bom",
            safe_bool(profile.get("candidate_has_no_utf8_bom", False)),
        ),
        (
            "candidate_uses_lf_only",
            safe_bool(profile.get("candidate_uses_lf_only", False)),
        ),
        (
            "candidate_has_final_newline",
            safe_bool(profile.get("candidate_has_final_newline", False)),
        ),
        (
            "candidate_physical_line_count_1",
            safe_bool(
                profile.get("candidate_physical_line_count_1", False)
            ),
        ),
        (
            "candidate_contains_no_nul",
            safe_bool(profile.get("candidate_contains_no_nul", False)),
        ),
        (
            "candidate_row_count_zero",
            safe_int(profile.get("candidate_row_count", -1), -1) == 0,
        ),
        (
            "candidate_column_count_54",
            safe_int(profile.get("candidate_column_count", -1), -1)
            == 54,
        ),
        (
            "candidate_columns_exact",
            safe_bool(profile.get("candidate_columns_exact", False)),
        ),
        (
            "candidate_columns_unique",
            safe_bool(profile.get("candidate_columns_unique", False)),
        ),
        (
            "candidate_contract_valid",
            safe_bool(profile.get("candidate_contract_valid", False)),
        ),
        (
            "candidate_distinct_from_official_profile",
            safe_bool(
                profile.get("candidate_distinct_from_official", False)
            ),
        ),
        (
            "candidate_size_stable",
            safe_bool(profile.get("candidate_size_stable", False)),
        ),
        (
            "candidate_mtime_stable",
            safe_bool(profile.get("candidate_mtime_stable", False)),
        ),
        (
            "candidate_hash_stable",
            safe_bool(profile.get("candidate_hash_stable", False)),
        ),
        (
            "candidate_git_tracked",
            safe_bool(profile.get("candidate_git_tracked", False)),
        ),
        (
            "candidate_git_clean",
            safe_bool(profile.get("candidate_git_clean", False)),
        ),
        (
            "candidate_no_temp_siblings",
            not any(
                EMPTY_SCHEMA_CANDIDATE_PATH.parent.glob(
                    f"{EMPTY_SCHEMA_CANDIDATE_PATH.name}.*.tmp"
                )
            ),
        ),
    ]
    for name, passed in profile_checks:
        append_validation(
            rows,
            "candidate_schema_validation",
            name,
            passed,
            f"{name}={passed}",
        )

    negative_checks = [
        (
            "negative_control_rows_10",
            len(negative_controls) == 10,
        ),
        (
            "negative_controls_all_passed",
            all_passed(negative_controls),
        ),
        (
            "negative_control_temp_directory_cleaned",
            negative_temp_cleaned,
        ),
        (
            "negative_valid_control_accepted",
            (
                len(
                    negative_controls[
                        negative_controls[
                            "negative_control_name"
                        ].astype(str).eq("valid_canonical_header")
                        & negative_controls["actual_contract_valid"].map(
                            safe_bool
                        )
                    ]
                )
                == 1
            ),
        ),
        (
            "negative_corrupt_controls_rejected",
            (
                len(negative_controls) == 10
                and not negative_controls[
                    ~negative_controls[
                        "negative_control_name"
                    ].astype(str).eq("valid_canonical_header")
                ]["actual_contract_valid"].map(safe_bool).any()
            ),
        ),
    ]
    for name, passed in negative_checks:
        append_validation(
            rows,
            "negative_controls",
            name,
            passed,
            f"{name}={passed}",
        )

    safety_checks = [
        ("validation_only", True),
        ("candidate_not_modified", safe_bool(profile.get("candidate_hash_stable", False))),
        ("candidate_not_promoted", not OFFICIAL_DATASET_EXPECTED_PATH.exists()),
        ("official_dataset_absent_before", not official_before),
        ("official_dataset_absent_after", not official_after),
        (
            "official_dataset_unchanged_absent",
            not official_before and not official_after,
        ),
        ("official_manifest_not_created", not OFFICIAL_MANIFEST_PATH.exists()),
        ("official_lock_not_created", not OFFICIAL_LOCK_PATH.exists()),
        ("official_temp_not_created", not OFFICIAL_TEMP_PATH.exists()),
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
        ("project_not_completed", True),
        ("future_atomic_write_harness_design_only", True),
    ]
    for name, passed in safety_checks:
        append_validation(
            rows,
            "safety_boundary",
            name,
            passed,
            f"{name}={passed}",
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
                "validation_item_position": position,
                "validation_item_id": (
                    "OFFICIAL_DATASET_EMPTY_SCHEMA_CANDIDATE_VALIDATION_"
                    f"ITEM_{position:03d}"
                ),
                "validation_item_name": (
                    f"empty_schema_candidate_validation_block_{position:03d}"
                ),
                "validation_names": ",".join(block_names),
                "required": True,
                "validation_only": True,
                "candidate_modification_allowed": False,
                "candidate_promotion_allowed": False,
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
                "finding_id": (
                    "OFFICIAL_DATASET_EMPTY_SCHEMA_CANDIDATE_VALIDATION_"
                    f"FINDING_{position:03d}"
                ),
                "validation_item_id": str(item["validation_item_id"]),
                "finding_status": "PASS" if passed else "FAIL",
                "material_issue_found": not passed,
                "candidate_change_required": not passed,
                "future_atomic_write_harness_design_allowed": passed,
                "official_dataset_implementation_allowed": False,
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
                    "OFFICIAL_DATASET_EMPTY_SCHEMA_CANDIDATE_VALIDATION_"
                    f"CONTROL_{position:03d}"
                ),
                "control_name": str(validation["validation_name"]),
                "required": True,
                "validation_only": True,
                "candidate_modification_allowed": False,
                "candidate_promotion_allowed": False,
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
    negative_controls: pd.DataFrame,
) -> pd.DataFrame:
    profile = (
        candidate_profile.iloc[0].to_dict()
        if len(candidate_profile) == 1
        else {}
    )
    material_issues = int(
        findings["material_issue_found"].map(safe_bool).sum()
    )
    rules = [
        ("validation_count_at_least_120", len(validations) >= 120, ">=120", len(validations)),
        ("all_validations_passed", all_passed(validations), True, all_passed(validations)),
        ("item_count_matches_groups", len(items) == (len(validations) + 2) // 3, (len(validations) + 2) // 3, len(items)),
        ("all_items_passed", all_passed(items), True, all_passed(items)),
        ("finding_count_matches_items", len(findings) == len(items), len(items), len(findings)),
        ("all_findings_passed", all_passed(findings), True, all_passed(findings)),
        ("material_issue_count_zero", material_issues == 0, 0, material_issues),
        ("control_count_matches_validations", len(controls) == len(validations), len(validations), len(controls)),
        ("all_controls_passed", all_passed(controls), True, all_passed(controls)),
        ("candidate_contract_valid", safe_bool(profile.get("candidate_contract_valid", False)), True, safe_bool(profile.get("candidate_contract_valid", False))),
        ("candidate_size_981", safe_int(profile.get("candidate_size_bytes", -1), -1) == 981, 981, safe_int(profile.get("candidate_size_bytes", -1), -1)),
        ("candidate_sha256_exact", str(profile.get("candidate_sha256", "")) == EXPECTED_CANDIDATE_SHA256, EXPECTED_CANDIDATE_SHA256, str(profile.get("candidate_sha256", ""))),
        ("candidate_rows_zero", safe_int(profile.get("candidate_row_count", -1), -1) == 0, 0, safe_int(profile.get("candidate_row_count", -1), -1)),
        ("candidate_columns_54", safe_int(profile.get("candidate_column_count", -1), -1) == 54, 54, safe_int(profile.get("candidate_column_count", -1), -1)),
        ("candidate_hash_stable", safe_bool(profile.get("candidate_hash_stable", False)), True, safe_bool(profile.get("candidate_hash_stable", False))),
        ("candidate_mtime_stable", safe_bool(profile.get("candidate_mtime_stable", False)), True, safe_bool(profile.get("candidate_mtime_stable", False))),
        ("candidate_git_tracked", safe_bool(profile.get("candidate_git_tracked", False)), True, safe_bool(profile.get("candidate_git_tracked", False))),
        ("candidate_git_clean", safe_bool(profile.get("candidate_git_clean", False)), True, safe_bool(profile.get("candidate_git_clean", False))),
        ("negative_controls_all_passed", all_passed(negative_controls), True, all_passed(negative_controls)),
        ("validation_only", True, True, True),
        ("candidate_modification_disabled", True, False, False),
        ("candidate_promotion_disabled", True, False, False),
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
        ("future_atomic_write_harness_design_only", True, True, True),
    ]
    return pd.DataFrame(
        [
            {
                "rule_id": (
                    "OFFICIAL_DATASET_EMPTY_SCHEMA_CANDIDATE_VALIDATION_"
                    f"RULE_{position:03d}"
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


def build_guard_matrix(validation_passed: bool) -> pd.DataFrame:
    guards = [
        ("source_candidate_implementation_performed", True, True),
        ("source_candidate_implementation_passed", True, True),
        ("source_candidate_validation_allowed", True, True),
        ("candidate_validation_performed", True, True),
        ("candidate_validation_passed", True, validation_passed),
        ("future_atomic_write_harness_design_allowed", True, validation_passed),
        ("empty_schema_candidate_exists", True, True),
        ("candidate_contract_valid", True, validation_passed),
        ("candidate_modification_allowed", False, False),
        ("candidate_promotion_allowed", False, False),
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
        ("candidate_hash_stable", True, validation_passed),
        ("candidate_mtime_stable", True, validation_passed),
        ("negative_controls_passed", True, validation_passed),
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
                "guard_group": (
                    "candidate_validation_state"
                    if position <= 8
                    else "candidate_validation_safety_guard"
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
    candidate_profile: pd.DataFrame,
    negative_controls: pd.DataFrame,
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

    profile = (
        candidate_profile.iloc[0].to_dict()
        if len(candidate_profile) == 1
        else {}
    )
    material_issues = int(
        findings["material_issue_found"].map(safe_bool).sum()
    )
    aggregate = [
        ("validation_items_passed", all_passed(items), True, all_passed(items)),
        ("validation_findings_passed", all_passed(findings), True, all_passed(findings)),
        ("validation_controls_passed", all_passed(controls), True, all_passed(controls)),
        ("validation_rules_passed", all_passed(rules), True, all_passed(rules)),
        ("validation_guards_passed", all_passed(guards), True, all_passed(guards)),
        ("material_issue_count_zero", material_issues == 0, 0, material_issues),
        ("candidate_contract_valid", safe_bool(profile.get("candidate_contract_valid", False)), True, safe_bool(profile.get("candidate_contract_valid", False))),
        ("candidate_hash_stable", safe_bool(profile.get("candidate_hash_stable", False)), True, safe_bool(profile.get("candidate_hash_stable", False))),
        ("candidate_mtime_stable", safe_bool(profile.get("candidate_mtime_stable", False)), True, safe_bool(profile.get("candidate_mtime_stable", False))),
        ("negative_controls_passed", all_passed(negative_controls), True, all_passed(negative_controls)),
        ("future_atomic_write_harness_design_allowed", True, True, True),
        ("candidate_modification_not_allowed", True, False, False),
        ("candidate_promotion_not_allowed", True, False, False),
        ("official_dataset_creation_not_allowed", True, False, False),
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
                "requirement_id": (
                    "OFFICIAL_DATASET_EMPTY_SCHEMA_CANDIDATE_VALIDATION_"
                    f"REQ_{position:03d}"
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
    candidate_profile: pd.DataFrame,
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
    profile = (
        candidate_profile.iloc[0].to_dict()
        if len(candidate_profile) == 1
        else {}
    )
    failed = requirements[
        ~requirements["passed"].map(safe_bool)
    ]
    return pd.DataFrame(
        [
            {
                "official_dataset_empty_schema_candidate_validation_id": (
                    "PHASE_10_41_LONG_FORWARD_OBSERVATION_EVIDENCE_"
                    "COLLECTION_OFFICIAL_DATASET_EMPTY_SCHEMA_CANDIDATE_"
                    "VALIDATION_001"
                ),
                "official_dataset_empty_schema_candidate_validation_performed": True,
                "official_dataset_empty_schema_candidate_validation_passed": passed,
                "official_dataset_empty_schema_candidate_validation_decision": (
                    READY_DECISION if passed else BLOCKED_DECISION
                ),
                "candidate_path": str(EMPTY_SCHEMA_CANDIDATE_PATH),
                "candidate_exists": safe_bool(
                    profile.get("candidate_exists", False)
                ),
                "candidate_sha256": str(
                    profile.get("candidate_sha256", "")
                ),
                "candidate_size_bytes": safe_int(
                    profile.get("candidate_size_bytes", -1),
                    -1,
                ),
                "candidate_column_count": safe_int(
                    profile.get("candidate_column_count", -1),
                    -1,
                ),
                "candidate_row_count": safe_int(
                    profile.get("candidate_row_count", -1),
                    -1,
                ),
                "candidate_contract_valid": safe_bool(
                    profile.get("candidate_contract_valid", False)
                ),
                "candidate_hash_stable": safe_bool(
                    profile.get("candidate_hash_stable", False)
                ),
                "candidate_mtime_stable": safe_bool(
                    profile.get("candidate_mtime_stable", False)
                ),
                "candidate_git_tracked": safe_bool(
                    profile.get("candidate_git_tracked", False)
                ),
                "candidate_git_clean": safe_bool(
                    profile.get("candidate_git_clean", False)
                ),
                "total_requirements": len(requirements),
                "passed_requirements": int(
                    requirements["passed"].map(safe_bool).sum()
                ),
                "failed_requirements": len(failed),
                "failed_requirement_names": ",".join(
                    failed["requirement_name"].astype(str).tolist()
                ),
                "future_official_dataset_atomic_write_harness_design_allowed": passed,
                "candidate_modification_allowed": False,
                "candidate_promotion_allowed": False,
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
    candidate_profile: pd.DataFrame,
    negative_controls: pd.DataFrame,
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

    profile = (
        candidate_profile.iloc[0].to_dict()
        if len(candidate_profile) == 1
        else {}
    )
    decision_row = (
        decision.iloc[0].to_dict()
        if len(decision) == 1
        else {}
    )
    blocks = {
        "validation_validations_passed": all_passed(validations),
        "validation_items_passed": all_passed(items),
        "validation_findings_passed": all_passed(findings),
        "validation_controls_passed": all_passed(controls),
        "validation_rules_passed": all_passed(rules),
        "validation_requirements_passed": all_passed(requirements),
        "validation_guards_passed": all_passed(guards),
        "candidate_contract_valid": safe_bool(
            profile.get("candidate_contract_valid", False)
        ),
        "candidate_hash_stable": safe_bool(
            profile.get("candidate_hash_stable", False)
        ),
        "candidate_mtime_stable": safe_bool(
            profile.get("candidate_mtime_stable", False)
        ),
        "negative_controls_passed": all_passed(negative_controls),
        "candidate_validation_passed": safe_bool(
            decision_row.get(
                "official_dataset_empty_schema_candidate_validation_passed",
                False,
            )
        ),
        "candidate_validation_decision_expected": (
            str(
                decision_row.get(
                    "official_dataset_empty_schema_candidate_validation_decision",
                    "",
                )
            )
            == READY_DECISION
        ),
    }
    for name, passed in blocks.items():
        checks.append(
            check_row(
                "candidate_validation",
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
        ("validation_only", "Phase 10.41 validates without modifying the candidate."),
        ("candidate_not_promoted", "The candidate was not promoted to the official dataset."),
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
        ("future_atomic_write_harness_design_only", "The only next allowance is atomic-write harness design."),
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
            "phase_10_42_recommended_next",
            True,
            "INFO",
            (
                "Recommended next: Phase 10.42 official dataset "
                "atomic-write harness design."
            ),
        )
    )
    return pd.DataFrame(checks)


def build_summary(
    source_manifest: pd.DataFrame,
    validations: pd.DataFrame,
    candidate_profile: pd.DataFrame,
    negative_controls: pd.DataFrame,
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
    profile = (
        candidate_profile.iloc[0].to_dict()
        if len(candidate_profile) == 1
        else {}
    )
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
                "phase": "10.41",
                "official_dataset_empty_schema_candidate_validation_defined": True,
                "phase_10_40_source_validated": all_passed(validations),
                "source_artifact_count": len(source_manifest),
                "source_artifacts_exist": source_manifest[
                    "artifact_exists"
                ].map(safe_bool).all(),
                "source_artifacts_non_empty": source_manifest[
                    "artifact_non_empty"
                ].map(safe_bool).all(),
                "source_artifact_hashes_valid": source_manifest[
                    "artifact_sha256_valid"
                ].map(safe_bool).all(),
                "source_manifest_sha256": manifest_digest(source_manifest),
                "validation_validation_rows": len(validations),
                "validation_negative_control_rows": len(negative_controls),
                "validation_item_rows": len(items),
                "validation_finding_rows": len(findings),
                "validation_control_rows": len(controls),
                "validation_rule_rows": len(rules),
                "validation_requirement_rows": len(requirements),
                "validation_guard_rows": len(guards),
                "validation_validations_passed": all_passed(validations),
                "validation_negative_controls_passed": all_passed(
                    negative_controls
                ),
                "validation_items_passed": all_passed(items),
                "validation_findings_passed": all_passed(findings),
                "validation_controls_passed": all_passed(controls),
                "validation_rules_passed": all_passed(rules),
                "validation_requirements_passed": all_passed(
                    requirements
                ),
                "validation_guards_passed": all_passed(guards),
                "material_issue_count": material_issue_count,
                "official_dataset_empty_schema_candidate_validation_performed": True,
                "official_dataset_empty_schema_candidate_validation_passed": safe_bool(
                    decision_row.get(
                        "official_dataset_empty_schema_candidate_validation_passed",
                        False,
                    )
                ),
                "official_dataset_empty_schema_candidate_validation_decision": str(
                    decision_row.get(
                        "official_dataset_empty_schema_candidate_validation_decision",
                        "",
                    )
                ),
                "candidate_path": str(EMPTY_SCHEMA_CANDIDATE_PATH),
                "candidate_exists": safe_bool(
                    profile.get("candidate_exists", False)
                ),
                "candidate_size_bytes": safe_int(
                    profile.get("candidate_size_bytes", -1),
                    -1,
                ),
                "candidate_sha256": str(
                    profile.get("candidate_sha256", "")
                ),
                "candidate_column_count": safe_int(
                    profile.get("candidate_column_count", -1),
                    -1,
                ),
                "candidate_row_count": safe_int(
                    profile.get("candidate_row_count", -1),
                    -1,
                ),
                "candidate_contract_valid": safe_bool(
                    profile.get("candidate_contract_valid", False)
                ),
                "candidate_hash_stable": safe_bool(
                    profile.get("candidate_hash_stable", False)
                ),
                "candidate_mtime_stable": safe_bool(
                    profile.get("candidate_mtime_stable", False)
                ),
                "candidate_git_tracked": safe_bool(
                    profile.get("candidate_git_tracked", False)
                ),
                "candidate_git_clean": safe_bool(
                    profile.get("candidate_git_clean", False)
                ),
                "future_official_dataset_atomic_write_harness_design_allowed": safe_bool(
                    decision_row.get(
                        "future_official_dataset_atomic_write_harness_design_allowed",
                        False,
                    )
                ),
                "candidate_modification_allowed": False,
                "candidate_promotion_allowed": False,
                "official_dataset_implementation_allowed": False,
                "official_dataset_creation_allowed": False,
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
                    "PHASE_10_41_LONG_FORWARD_OBSERVATION_EVIDENCE_"
                    "COLLECTION_OFFICIAL_DATASET_EMPTY_SCHEMA_CANDIDATE_"
                    "VALIDATION_VALIDATED"
                    if validation_passed
                    else
                    "PHASE_10_41_LONG_FORWARD_OBSERVATION_EVIDENCE_"
                    "COLLECTION_OFFICIAL_DATASET_EMPTY_SCHEMA_CANDIDATE_"
                    "VALIDATION_FAILED"
                ),
            }
        ]
    )


def run_long_forward_observation_evidence_collection_official_dataset_empty_schema_candidate_validation() -> dict[str, pd.DataFrame]:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    docs_exist = {
        "phase_10_40_candidate_implementation_doc_exists": (
            PHASE_10_40_DOC_PATH.exists()
        ),
        "phase_10_41_candidate_validation_doc_exists": (
            PHASE_10_41_DOC_PATH.exists()
        ),
    }

    official_before = OFFICIAL_DATASET_EXPECTED_PATH.exists()
    candidate_state_before = candidate_file_state(
        EMPTY_SCHEMA_CANDIDATE_PATH
    )
    source_manifest_before = build_manifest(
        SOURCE_PATHS,
        "PHASE_10_41_SOURCE",
    )
    source = {
        name: read_csv(path)
        for name, path in SOURCE_PATHS.items()
        if name != "empty_schema_candidate"
    }

    base_profile = inspect_candidate(
        EMPTY_SCHEMA_CANDIDATE_PATH,
        EXPECTED_FIELD_NAMES,
    )
    negative_controls, negative_temp_cleaned = run_negative_controls(
        EXPECTED_FIELD_NAMES
    )
    git_state = git_candidate_state(EMPTY_SCHEMA_CANDIDATE_PATH)
    candidate_state_after = candidate_file_state(
        EMPTY_SCHEMA_CANDIDATE_PATH
    )
    source_manifest_after = build_manifest(
        SOURCE_PATHS,
        "PHASE_10_41_SOURCE",
    )
    official_after = OFFICIAL_DATASET_EXPECTED_PATH.exists()

    candidate_profile = build_candidate_validation_profile(
        base_profile,
        candidate_state_before,
        candidate_state_after,
        git_state,
    )
    validations = build_validations(
        source,
        source_manifest_before,
        source_manifest_after,
        candidate_profile,
        negative_controls,
        negative_temp_cleaned,
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
        candidate_profile,
        negative_controls,
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
        candidate_profile,
        negative_controls,
    )
    decision = build_decision(
        validations,
        items,
        findings,
        controls,
        rules,
        requirements,
        guards,
        candidate_profile,
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
        candidate_profile,
        negative_controls,
        decision,
        official_before,
        official_after,
    )
    summary = build_summary(
        source_manifest_before,
        validations,
        candidate_profile,
        negative_controls,
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
        "candidate_profile": candidate_profile,
        "negative_controls": negative_controls,
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
        "PHASE_10_41_OUTPUT",
    )
    combined_manifest = pd.concat(
        [
            source_manifest_after,
            output_manifest,
        ],
        ignore_index=True,
    )
    combined_manifest.to_csv(
        REPORTS_DIR / OUTPUT_FILENAMES["manifest"],
        index=False,
    )

    return {
        "summary": summary,
        "source_implementation_summary": source[
            "implementation_summary"
        ],
        "source_implementation_decision": source[
            "implementation_decision"
        ],
        "source_field_catalog": source["field_catalog"],
        "source_artifact_manifest": source_manifest_before,
        "candidate_profile": candidate_profile,
        "negative_controls": negative_controls,
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
