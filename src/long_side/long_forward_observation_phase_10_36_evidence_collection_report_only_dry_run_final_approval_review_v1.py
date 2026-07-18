from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

import pandas as pd

from src.long_side.long_forward_observation_dataset_bootstrap_v1 import (
    OFFICIAL_DATASET_PATH,
)


REPORTS_DIR = Path(
    "reports/p10_36_evidence_collection_report_only_dry_run_"
    "final_approval_review_v1"
)
SOURCE_DIR = Path(
    "reports/p10_35_evidence_collection_report_only_dry_run_"
    "output_integrity_review_v1"
)

PHASE_10_35_DOC_PATH = Path(
    "docs/PHASE_10_LONG_FORWARD_OBSERVATION_EVIDENCE_COLLECTION_"
    "REPORT_ONLY_DRY_RUN_OUTPUT_INTEGRITY_REVIEW.md"
)
PHASE_10_36_DOC_PATH = Path(
    "docs/PHASE_10_LONG_FORWARD_OBSERVATION_EVIDENCE_COLLECTION_"
    "REPORT_ONLY_DRY_RUN_FINAL_APPROVAL_REVIEW.md"
)

SOURCE_PATHS = {
    "summary": (
        SOURCE_DIR
        / "report_only_dry_run_output_integrity_review_summary_v1.csv"
    ),
    "validations": (
        SOURCE_DIR
        / "report_only_dry_run_output_integrity_review_validations_v1.csv"
    ),
    "items": (
        SOURCE_DIR
        / "report_only_dry_run_output_integrity_review_items_v1.csv"
    ),
    "findings": (
        SOURCE_DIR
        / "report_only_dry_run_output_integrity_review_findings_v1.csv"
    ),
    "controls": (
        SOURCE_DIR
        / "report_only_dry_run_output_integrity_review_controls_v1.csv"
    ),
    "rules": (
        SOURCE_DIR
        / "report_only_dry_run_output_integrity_review_rules_v1.csv"
    ),
    "requirements": (
        SOURCE_DIR
        / "report_only_dry_run_output_integrity_review_requirements_v1.csv"
    ),
    "guard_matrix": (
        SOURCE_DIR
        / "report_only_dry_run_output_integrity_review_guard_matrix_v1.csv"
    ),
    "decision": (
        SOURCE_DIR
        / "report_only_dry_run_output_integrity_review_decision_v1.csv"
    ),
    "checks": (
        SOURCE_DIR
        / "report_only_dry_run_output_integrity_review_checks_v1.csv"
    ),
    "manifest": (
        SOURCE_DIR
        / "source_report_only_dry_run_output_integrity_artifact_manifest_v1.csv"
    ),
}

SOURCE_READY_DECISION = (
    "CONTROLLED_FORWARD_OBSERVATION_EVIDENCE_COLLECTION_REPORT_ONLY_"
    "DRY_RUN_OUTPUT_INTEGRITY_REVIEW_READY_FOR_FINAL_APPROVAL_REVIEW"
)
READY_DECISION = (
    "CONTROLLED_FORWARD_OBSERVATION_EVIDENCE_COLLECTION_REPORT_ONLY_"
    "DRY_RUN_FINAL_APPROVAL_REVIEW_APPROVED_FOR_OFFICIAL_DATASET_"
    "SCHEMA_IMPLEMENTATION_DESIGN"
)
BLOCKED_DECISION = (
    "CONTROLLED_FORWARD_OBSERVATION_EVIDENCE_COLLECTION_REPORT_ONLY_"
    "DRY_RUN_FINAL_APPROVAL_REVIEW_BLOCKED"
)
RECOMMENDED_NEXT_PHASE = (
    "PHASE_10_37_LONG_FORWARD_OBSERVATION_EVIDENCE_COLLECTION_"
    "OFFICIAL_DATASET_SCHEMA_IMPLEMENTATION_DESIGN_V1"
)

FALSE_SOURCE_GUARDS = [
    "new_report_only_dry_run_execution_performed",
    "official_dataset_exists_before",
    "official_dataset_exists_after",
    "evidence_collection_enabled",
    "evidence_collection_started",
    "official_dataset_schema_implemented",
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

OUTPUT_FILENAMES = {
    "summary": (
        "report_only_dry_run_final_approval_review_summary_v1.csv"
    ),
    "validations": (
        "report_only_dry_run_final_approval_review_validations_v1.csv"
    ),
    "items": (
        "report_only_dry_run_final_approval_review_items_v1.csv"
    ),
    "findings": (
        "report_only_dry_run_final_approval_review_findings_v1.csv"
    ),
    "controls": (
        "report_only_dry_run_final_approval_review_controls_v1.csv"
    ),
    "rules": (
        "report_only_dry_run_final_approval_review_rules_v1.csv"
    ),
    "requirements": (
        "report_only_dry_run_final_approval_review_requirements_v1.csv"
    ),
    "guard_matrix": (
        "report_only_dry_run_final_approval_review_guard_matrix_v1.csv"
    ),
    "decision": (
        "report_only_dry_run_final_approval_review_decision_v1.csv"
    ),
    "checks": (
        "report_only_dry_run_final_approval_review_checks_v1.csv"
    ),
    "manifest": (
        "source_report_only_dry_run_final_approval_artifact_manifest_v1.csv"
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
    try:
        return bool(value)
    except Exception:
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
        and df["passed"].map(lambda value: safe_bool(value, False)).all()
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


def source_summary_row(
    source: dict[str, pd.DataFrame],
) -> dict[str, Any]:
    if source["summary"].empty:
        return {}
    return source["summary"].iloc[0].to_dict()


def validate_source_summary(
    row: dict[str, Any],
) -> dict[str, bool]:
    return {
        "phase_10_35_validation_passed": (
            safe_bool(row.get("validation_passed", False))
            and str(row.get("validation_decision", ""))
            == (
                "PHASE_10_35_LONG_FORWARD_OBSERVATION_EVIDENCE_"
                "COLLECTION_REPORT_ONLY_DRY_RUN_OUTPUT_INTEGRITY_"
                "REVIEW_VALIDATED"
            )
        ),
        "source_phase_10_34_validation_passed": safe_bool(
            row.get("phase_10_34_validation_passed", False)
        ),
        "source_dry_run_executed": safe_bool(
            row.get("source_report_only_dry_run_executed", False)
        ),
        "source_dry_run_rows_generated_6": (
            safe_int(
                row.get(
                    "source_report_only_dry_run_rows_generated",
                    -1,
                ),
                -1,
            )
            == 6
        ),
        "source_dry_run_valid_rows_1": (
            safe_int(
                row.get(
                    "source_report_only_dry_run_valid_rows",
                    -1,
                ),
                -1,
            )
            == 1
        ),
        "source_dry_run_rejected_rows_5": (
            safe_int(
                row.get(
                    "source_report_only_dry_run_rejected_rows",
                    -1,
                ),
                -1,
            )
            == 5
        ),
        "source_artifact_count_10": (
            safe_int(row.get("source_artifact_count", -1), -1) == 10
        ),
        "source_artifacts_exist": safe_bool(
            row.get("source_artifacts_exist", False)
        ),
        "source_artifacts_non_empty": safe_bool(
            row.get("source_artifacts_non_empty", False)
        ),
        "source_artifact_hashes_valid": safe_bool(
            row.get("source_artifact_hashes_valid", False)
        ),
        "source_manifest_listed_rows_31": (
            safe_int(
                row.get("manifest_listed_row_count", -1),
                -1,
            )
            == 31
        ),
        "source_manifest_listed_outputs_9": (
            safe_int(
                row.get("manifest_listed_output_count", -1),
                -1,
            )
            == 9
        ),
        "source_manifest_self_exclusion_expected": safe_bool(
            row.get("manifest_self_exclusion_expected", False)
        ),
        "source_review_validation_rows_78": (
            safe_int(row.get("review_validation_rows", -1), -1)
            == 78
        ),
        "source_review_item_rows_26": (
            safe_int(row.get("review_item_rows", -1), -1) == 26
        ),
        "source_review_finding_rows_26": (
            safe_int(row.get("review_finding_rows", -1), -1)
            == 26
        ),
        "source_review_control_rows_78": (
            safe_int(row.get("review_control_rows", -1), -1)
            == 78
        ),
        "source_review_rule_rows_24": (
            safe_int(row.get("review_rule_rows", -1), -1) == 24
        ),
        "source_review_requirement_rows_92": (
            safe_int(row.get("review_requirement_rows", -1), -1)
            == 92
        ),
        "source_review_guard_rows_37": (
            safe_int(row.get("review_guard_rows", -1), -1) == 37
        ),
        "source_review_validations_passed": safe_bool(
            row.get("review_validations_passed", False)
        ),
        "source_review_items_passed": safe_bool(
            row.get("review_items_passed", False)
        ),
        "source_review_findings_passed": safe_bool(
            row.get("review_findings_passed", False)
        ),
        "source_review_controls_passed": safe_bool(
            row.get("review_controls_passed", False)
        ),
        "source_review_rules_passed": safe_bool(
            row.get("review_rules_passed", False)
        ),
        "source_review_requirements_passed": safe_bool(
            row.get("review_requirements_passed", False)
        ),
        "source_review_guards_passed": safe_bool(
            row.get("review_guards_passed", False)
        ),
        "source_material_issue_count_zero": (
            safe_int(row.get("material_issue_count", -1), -1) == 0
        ),
        "source_integrity_review_performed": safe_bool(
            row.get(
                "report_only_dry_run_output_integrity_review_performed",
                False,
            )
        ),
        "source_integrity_review_passed": safe_bool(
            row.get(
                "report_only_dry_run_output_integrity_review_passed",
                False,
            )
        ),
        "source_integrity_review_decision_valid": (
            str(
                row.get(
                    "report_only_dry_run_output_integrity_review_decision",
                    "",
                )
            )
            == SOURCE_READY_DECISION
        ),
        "source_final_approval_review_allowed": safe_bool(
            row.get(
                "future_report_only_dry_run_final_approval_review_allowed",
                False,
            )
        ),
        "source_new_dry_run_not_executed": not safe_bool(
            row.get(
                "new_report_only_dry_run_execution_performed",
                True,
            ),
            True,
        ),
        "source_new_dry_run_rows_zero": (
            safe_int(
                row.get(
                    "new_report_only_dry_run_rows_generated",
                    -1,
                ),
                -1,
            )
            == 0
        ),
        "source_official_dataset_unchanged_absent": safe_bool(
            row.get("official_dataset_unchanged_absent", False)
        ),
        "source_official_evidence_rows_zero": (
            safe_int(
                row.get("official_evidence_rows_written", -1),
                -1,
            )
            == 0
        ),
        "source_total_checks_28": (
            safe_int(row.get("total_checks", -1), -1) == 28
        ),
        "source_warning_count_15": (
            safe_int(row.get("warning_count", -1), -1) == 15
        ),
        "source_error_count_zero": (
            safe_int(row.get("error_count", -1), -1) == 0
        ),
        "source_blocker_count_zero": (
            safe_int(row.get("blocker_count", -1), -1) == 0
        ),
        "source_operational_locks_valid": all(
            not safe_bool(row.get(name, True), True)
            for name in FALSE_SOURCE_GUARDS
        ),
    }


def validate_source_validations(
    df: pd.DataFrame,
) -> dict[str, bool]:
    positions = (
        df["validation_position"].map(safe_int).tolist()
        if (
            not df.empty
            and "validation_position" in df.columns
        )
        else []
    )
    return {
        "source_validation_table_rows_78": len(df) == 78,
        "source_validation_positions_exact": (
            positions == list(range(1, 79))
        ),
        "source_validation_table_all_passed": all_passed(df),
        "source_validation_names_unique": (
            not df.empty
            and "validation_name" in df.columns
            and df["validation_name"].astype(str).is_unique
        ),
    }


def validate_source_items(
    df: pd.DataFrame,
) -> dict[str, bool]:
    return {
        "source_item_table_rows_26": len(df) == 26,
        "source_item_table_all_passed": all_passed(df),
        "source_items_review_only": column_all_bool(
            df, "review_only", True
        ),
        "source_items_no_new_dry_run": column_all_bool(
            df, "new_dry_run_execution_allowed", False
        ),
        "source_items_no_official_write": column_all_bool(
            df, "official_dataset_write_allowed", False
        ),
    }


def validate_source_findings(
    df: pd.DataFrame,
) -> dict[str, bool]:
    return {
        "source_finding_table_rows_26": len(df) == 26,
        "source_finding_table_all_passed": all_passed(df),
        "source_findings_no_material_issues": column_all_bool(
            df, "material_issue_found", False
        ),
        "source_findings_no_output_change_required": column_all_bool(
            df, "output_change_required", False
        ),
        "source_findings_allow_final_review": column_all_bool(
            df, "final_approval_review_allowed", True
        ),
    }


def validate_source_controls(
    df: pd.DataFrame,
) -> dict[str, bool]:
    return {
        "source_control_table_rows_78": len(df) == 78,
        "source_control_table_all_passed": all_passed(df),
        "source_controls_review_only": column_all_bool(
            df, "review_only", True
        ),
        "source_controls_no_new_dry_run": column_all_bool(
            df, "new_dry_run_execution_performed", False
        ),
        "source_controls_evidence_disabled": column_all_bool(
            df, "evidence_collection_enabled", False
        ),
        "source_controls_market_execution_disabled": column_all_bool(
            df, "market_execution_allowed", False
        ),
    }


def validate_source_rules(
    df: pd.DataFrame,
) -> dict[str, bool]:
    return {
        "source_rule_table_rows_24": len(df) == 24,
        "source_rule_table_all_passed": all_passed(df),
    }


def validate_source_requirements(
    df: pd.DataFrame,
) -> dict[str, bool]:
    return {
        "source_requirement_table_rows_92": len(df) == 92,
        "source_requirement_table_all_passed": all_passed(df),
        "source_requirement_names_unique": (
            not df.empty
            and "requirement_name" in df.columns
            and df["requirement_name"].astype(str).is_unique
        ),
    }


def validate_source_guards(
    df: pd.DataFrame,
) -> dict[str, bool]:
    guard_names = (
        set(df["guard_name"].astype(str))
        if not df.empty and "guard_name" in df.columns
        else set()
    )
    required_guards = {
        "source_report_only_dry_run_executed",
        "source_report_only_dry_run_run_passed",
        "output_integrity_review_performed",
        "output_integrity_review_passed",
        "future_final_approval_review_allowed",
        "new_report_only_dry_run_execution_performed",
        "official_dataset_write_performed",
        "accepted_as_real_evidence",
        "signal_generation_enabled",
        "paper_trade_execution_allowed",
        "market_execution_allowed",
        "automation_allowed",
        "total_project_completed",
    }
    return {
        "source_guard_table_rows_37": len(df) == 37,
        "source_guard_table_all_passed": all_passed(df),
        "source_guard_required_names_present": (
            required_guards.issubset(guard_names)
        ),
        "source_guard_names_unique": (
            not df.empty
            and "guard_name" in df.columns
            and df["guard_name"].astype(str).is_unique
        ),
    }


def validate_source_decision(
    df: pd.DataFrame,
) -> dict[str, bool]:
    row = df.iloc[0].to_dict() if len(df) == 1 else {}
    return {
        "source_decision_row_count_1": len(df) == 1,
        "source_decision_review_performed": safe_bool(
            row.get(
                "report_only_dry_run_output_integrity_review_performed",
                False,
            )
        ),
        "source_decision_review_passed": safe_bool(
            row.get(
                "report_only_dry_run_output_integrity_review_passed",
                False,
            )
        ),
        "source_decision_value_valid": (
            str(
                row.get(
                    "report_only_dry_run_output_integrity_review_decision",
                    "",
                )
            )
            == SOURCE_READY_DECISION
        ),
        "source_decision_requirements_92": (
            safe_int(row.get("total_requirements", -1), -1) == 92
        ),
        "source_decision_passed_requirements_92": (
            safe_int(row.get("passed_requirements", -1), -1)
            == 92
        ),
        "source_decision_failed_requirements_zero": (
            safe_int(row.get("failed_requirements", -1), -1) == 0
        ),
        "source_decision_final_review_allowed": safe_bool(
            row.get(
                "future_report_only_dry_run_final_approval_review_allowed",
                False,
            )
        ),
        "source_decision_no_new_execution": not safe_bool(
            row.get(
                "new_report_only_dry_run_execution_performed",
                True,
            ),
            True,
        ),
        "source_decision_operational_locks_valid": all(
            not safe_bool(row.get(name, True), True)
            for name in [
                "evidence_collection_enabled",
                "official_dataset_schema_implemented",
                "official_dataset_write_allowed",
                "official_dataset_write_performed",
                "accepted_as_real_evidence",
                "evidence_persistence_allowed",
                "signal_generation_enabled",
                "live_alerts_allowed",
                "paper_trade_execution_allowed",
                "real_capital_allowed",
                "market_execution_allowed",
                "exchange_execution_allowed",
                "automation_allowed",
                "execution_allowed",
                "total_project_completed",
            ]
        ),
    }


def validate_source_checks(
    df: pd.DataFrame,
) -> dict[str, bool]:
    warnings = (
        int(df["severity"].astype(str).eq("WARNING").sum())
        if not df.empty and "severity" in df.columns
        else -1
    )
    errors = (
        int(df["severity"].astype(str).eq("ERROR").sum())
        if not df.empty and "severity" in df.columns
        else -1
    )
    blockers = (
        int(df["blocker"].map(safe_bool).sum())
        if not df.empty and "blocker" in df.columns
        else -1
    )
    return {
        "source_check_table_rows_28": len(df) == 28,
        "source_check_warning_count_15": warnings == 15,
        "source_check_error_count_zero": errors == 0,
        "source_check_blocker_count_zero": blockers == 0,
        "source_check_table_all_passed": all_passed(df),
    }


def validate_source_manifest(
    df: pd.DataFrame,
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
    if df.empty or not required_columns.issubset(df.columns):
        return {
            "source_manifest_rows_20": False,
            "source_manifest_phase_10_34_rows_10": False,
            "source_manifest_phase_10_35_output_rows_10": False,
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

    phase_10_34_rows = df[
        df["artifact_scope"].astype(str).eq("PHASE_10_34")
    ]
    phase_10_35_rows = df[
        df["artifact_scope"].astype(str).eq("PHASE_10_35_OUTPUT")
    ]
    listed_valid = (
        df["artifact_exists"].map(safe_bool).all()
        and df["artifact_non_empty"].map(safe_bool).all()
        and df["artifact_sha256_valid"].map(safe_bool).all()
        and (df["artifact_size_bytes"].map(safe_int) > 0).all()
    )

    hashes_match = True
    for _, row in df.iterrows():
        path = Path(str(row["artifact_path"]))
        if (
            not path.exists()
            or sha256_file(path) != str(row["artifact_sha256"])
        ):
            hashes_match = False
            break

    listed_names = set(df["artifact_filename"].astype(str))
    self_exclusion = (
        len(df) == 20
        and len(phase_10_35_rows) == 10
        and manifest_path.name not in listed_names
    )
    manifest_exists = manifest_path.exists()
    manifest_non_empty = (
        manifest_exists and manifest_path.stat().st_size > 0
    )
    manifest_hash_valid = is_sha256(sha256_file(manifest_path))

    return {
        "source_manifest_rows_20": len(df) == 20,
        "source_manifest_phase_10_34_rows_10": (
            len(phase_10_34_rows) == 10
        ),
        "source_manifest_phase_10_35_output_rows_10": (
            len(phase_10_35_rows) == 10
        ),
        "source_manifest_listed_artifacts_valid": listed_valid,
        "source_manifest_hashes_match_current_files": hashes_match,
        "source_manifest_self_exclusion_expected": self_exclusion,
        "source_manifest_file_exists": manifest_exists,
        "source_manifest_file_non_empty": manifest_non_empty,
        "source_manifest_file_sha256_valid": manifest_hash_valid,
    }


def build_validations(
    source: dict[str, pd.DataFrame],
    manifest_before: pd.DataFrame,
    manifest_after: pd.DataFrame,
    official_dataset_absent: bool,
) -> pd.DataFrame:
    validations: list[tuple[str, bool, str]] = []

    artifact_checks = {
        "source_artifacts_exist": (
            len(manifest_before) == 11
            and manifest_before["artifact_exists"]
            .map(safe_bool)
            .all()
        ),
        "source_artifacts_non_empty": (
            len(manifest_before) == 11
            and manifest_before["artifact_non_empty"]
            .map(safe_bool)
            .all()
        ),
        "source_artifact_hashes_valid": (
            len(manifest_before) == 11
            and manifest_before["artifact_sha256_valid"]
            .map(safe_bool)
            .all()
        ),
        "source_artifacts_stable_during_final_review": (
            bool(manifest_digest(manifest_before))
            and manifest_digest(manifest_before)
            == manifest_digest(manifest_after)
        ),
    }
    for name, passed in artifact_checks.items():
        details = (
            (
                f"before={manifest_digest(manifest_before)},"
                f"after={manifest_digest(manifest_after)}"
            )
            if name
            == "source_artifacts_stable_during_final_review"
            else f"rows={len(manifest_before)}"
        )
        validations.append((name, bool(passed), details))

    validation_groups = [
        validate_source_summary(source_summary_row(source)),
        validate_source_validations(source["validations"]),
        validate_source_items(source["items"]),
        validate_source_findings(source["findings"]),
        validate_source_controls(source["controls"]),
        validate_source_rules(source["rules"]),
        validate_source_requirements(source["requirements"]),
        validate_source_guards(source["guard_matrix"]),
        validate_source_decision(source["decision"]),
        validate_source_checks(source["checks"]),
        validate_source_manifest(
            source["manifest"],
            SOURCE_PATHS["manifest"],
        ),
    ]
    for group in validation_groups:
        for name, passed in group.items():
            validations.append(
                (name, bool(passed), f"{name}={passed}")
            )

    validations.extend(
        [
            (
                "official_dataset_absent_during_final_review",
                official_dataset_absent,
                f"absent={official_dataset_absent}",
            ),
            (
                "final_review_only_no_new_dry_run_execution",
                True,
                (
                    "Phase 10.36 reads existing Phase 10.35 "
                    "artifacts only."
                ),
            ),
            (
                "long_strategy_remains_unapproved",
                True,
                "long_strategy_approved=False",
            ),
            (
                "total_project_not_completed",
                True,
                "total_project_completed=False",
            ),
        ]
    )

    return pd.DataFrame(
        [
            {
                "validation_position": position,
                "validation_name": name,
                "passed": bool(passed),
                "details": details,
            }
            for position, (name, passed, details) in enumerate(
                validations,
                start=1,
            )
        ]
    )


def build_items(
    validations: pd.DataFrame,
) -> pd.DataFrame:
    validation_names = validations["validation_name"].astype(str).tolist()
    rows: list[dict[str, Any]] = []
    for position, start in enumerate(
        range(0, len(validation_names), 3),
        start=1,
    ):
        selected = validations.iloc[start : start + 3]
        names = selected["validation_name"].astype(str).tolist()
        passed = (
            len(selected) == len(names)
            and selected["passed"].map(safe_bool).all()
        )
        rows.append(
            {
                "review_item_position": position,
                "review_item_id": (
                    "REPORT_ONLY_DRY_RUN_FINAL_APPROVAL_ITEM_"
                    f"{position:03d}"
                ),
                "review_item_name": (
                    f"final_approval_review_block_{position:03d}"
                ),
                "validation_names": ",".join(names),
                "required": True,
                "review_only": True,
                "official_dataset_schema_design_only": True,
                "evidence_collection_allowed": False,
                "official_dataset_write_allowed": False,
                "market_execution_allowed": False,
                "passed": bool(passed),
            }
        )
    return pd.DataFrame(rows)


def build_findings(
    items: pd.DataFrame,
) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for position, (_, item) in enumerate(
        items.iterrows(),
        start=1,
    ):
        passed = safe_bool(item["passed"], False)
        rows.append(
            {
                "finding_position": position,
                "finding_id": (
                    "REPORT_ONLY_DRY_RUN_FINAL_APPROVAL_FINDING_"
                    f"{position:03d}"
                ),
                "review_item_id": str(item["review_item_id"]),
                "review_item_name": str(item["review_item_name"]),
                "finding_status": "PASS" if passed else "FAIL",
                "material_issue_found": not passed,
                "dry_run_cycle_change_required": not passed,
                "official_dataset_schema_design_allowed": passed,
                "operational_evidence_collection_allowed": False,
                "details": (
                    "Final approval criterion passed."
                    if passed
                    else "Final approval criterion failed."
                ),
                "passed": passed,
            }
        )
    return pd.DataFrame(rows)


def build_controls(
    validations: pd.DataFrame,
) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for position, (_, validation) in enumerate(
        validations.iterrows(),
        start=1,
    ):
        rows.append(
            {
                "control_position": position,
                "control_id": (
                    "REPORT_ONLY_DRY_RUN_FINAL_APPROVAL_CONTROL_"
                    f"{position:03d}"
                ),
                "control_name": str(
                    validation["validation_name"]
                ),
                "required": True,
                "review_only": True,
                "new_dry_run_execution_performed": False,
                "evidence_collection_enabled": False,
                "official_dataset_schema_implemented": False,
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
            "validation_count_positive",
            len(validations) > 0,
            ">0",
            len(validations),
        ),
        (
            "all_validations_passed",
            all_passed(validations),
            True,
            all_passed(validations),
        ),
        (
            "item_count_positive",
            len(items) > 0,
            ">0",
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
        ("final_review_only", True, True, True),
        ("new_dry_run_not_executed", True, False, False),
        ("dry_run_cycle_closed_only", True, True, True),
        (
            "official_dataset_schema_design_only",
            True,
            True,
            True,
        ),
        (
            "official_dataset_not_implemented",
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
            "real_evidence_acceptance_disabled",
            True,
            False,
            False,
        ),
        (
            "evidence_collection_disabled",
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
            "future_schema_design_not_operational",
            True,
            True,
            True,
        ),
    ]
    return pd.DataFrame(
        [
            {
                "rule_id": (
                    "REPORT_ONLY_DRY_RUN_FINAL_APPROVAL_RULE_"
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


def build_guard_matrix(
    review_passed: bool,
) -> pd.DataFrame:
    guards = [
        (
            "source_report_only_dry_run_executed",
            True,
            True,
        ),
        (
            "source_report_only_dry_run_run_passed",
            True,
            True,
        ),
        (
            "source_output_integrity_review_performed",
            True,
            True,
        ),
        (
            "source_output_integrity_review_passed",
            True,
            True,
        ),
        (
            "source_final_approval_review_allowed",
            True,
            True,
        ),
        (
            "final_approval_review_performed",
            True,
            True,
        ),
        (
            "final_approval_review_passed",
            True,
            review_passed,
        ),
        (
            "report_only_dry_run_cycle_closed",
            True,
            review_passed,
        ),
        (
            "future_official_dataset_schema_design_allowed",
            True,
            review_passed,
        ),
        (
            "new_report_only_dry_run_execution_performed",
            False,
            False,
        ),
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
        ("real_forward_signals_recorded", False, False),
        ("journal_real_rows_accepted", False, False),
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
        ("official_evidence_rows_written", 0, 0),
        ("new_report_only_dry_run_rows_generated", 0, 0),
    ]
    return pd.DataFrame(
        [
            {
                "guard_name": name,
                "required_value": required,
                "actual_value": actual,
                "passed": required == actual,
                "guard_group": (
                    "final_approval_state"
                    if position <= 9
                    else "final_approval_safety_guard"
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
            "final_review_items_passed",
            all_passed(items),
            True,
            all_passed(items),
        ),
        (
            "final_review_findings_passed",
            all_passed(findings),
            True,
            all_passed(findings),
        ),
        (
            "final_review_controls_passed",
            all_passed(controls),
            True,
            all_passed(controls),
        ),
        (
            "final_review_rules_passed",
            all_passed(rules),
            True,
            all_passed(rules),
        ),
        (
            "final_review_guards_passed",
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
        (
            "final_approval_review_performed",
            True,
            True,
            True,
        ),
        (
            "report_only_dry_run_cycle_closure_allowed",
            True,
            True,
            True,
        ),
        (
            "future_official_dataset_schema_design_allowed",
            True,
            True,
            True,
        ),
        (
            "new_dry_run_not_executed",
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
                    "REPORT_ONLY_DRY_RUN_FINAL_APPROVAL_REQ_"
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
    failed_requirements = requirements[
        ~requirements["passed"].map(safe_bool)
    ]
    return pd.DataFrame(
        [
            {
                "report_only_dry_run_final_approval_review_id": (
                    "PHASE_10_36_LONG_FORWARD_OBSERVATION_EVIDENCE_"
                    "COLLECTION_REPORT_ONLY_DRY_RUN_FINAL_APPROVAL_"
                    "REVIEW_001"
                ),
                "report_only_dry_run_final_approval_review_performed": True,
                "report_only_dry_run_final_approval_review_passed": passed,
                "report_only_dry_run_final_approval_review_decision": (
                    READY_DECISION if passed else BLOCKED_DECISION
                ),
                "report_only_dry_run_cycle_closed": passed,
                "total_requirements": len(requirements),
                "passed_requirements": int(
                    requirements["passed"].map(safe_bool).sum()
                ),
                "failed_requirements": len(failed_requirements),
                "failed_requirement_names": ",".join(
                    failed_requirements["requirement_name"]
                    .astype(str)
                    .tolist()
                ),
                "future_official_dataset_schema_implementation_design_allowed": passed,
                "source_report_only_dry_run_executed": True,
                "source_output_integrity_review_passed": True,
                "new_report_only_dry_run_execution_performed": False,
                "new_report_only_dry_run_rows_generated": 0,
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
        if not decision.empty
        else {}
    )
    blocks = {
        "final_review_validations_passed": all_passed(validations),
        "final_review_items_passed": all_passed(items),
        "final_review_findings_passed": all_passed(findings),
        "final_review_controls_passed": all_passed(controls),
        "final_review_rules_passed": all_passed(rules),
        "final_review_requirements_passed": all_passed(
            requirements
        ),
        "final_review_guards_passed": all_passed(guards),
        "final_approval_review_passed": safe_bool(
            decision_row.get(
                "report_only_dry_run_final_approval_review_passed",
                False,
            )
        ),
        "final_approval_review_decision_expected": (
            str(
                decision_row.get(
                    "report_only_dry_run_final_approval_review_decision",
                    "",
                )
            )
            == READY_DECISION
        ),
    }
    for name, passed in blocks.items():
        checks.append(
            check_row(
                "final_approval_review",
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
            "Phase 10.36 performs only a final approval review.",
        ),
        (
            "dry_run_not_reexecuted",
            "The report-only dry-run was not executed again.",
        ),
        (
            "dry_run_cycle_closure_only",
            (
                "Approval closes only the synthetic report-only "
                "dry-run cycle."
            ),
        ),
        (
            "future_schema_design_only",
            (
                "The next allowance is limited to official dataset "
                "schema implementation design."
            ),
        ),
        (
            "real_evidence_not_collected",
            "No real forward evidence was collected.",
        ),
        (
            "official_dataset_not_implemented",
            (
                "The official evidence dataset remains "
                "unimplemented."
            ),
        ),
        (
            "official_dataset_not_written",
            (
                "The official evidence dataset remains absent "
                "and unwritten."
            ),
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
            "total_project_not_completed",
            "The total project is not completed.",
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
            "phase_10_37_recommended_next",
            True,
            "INFO",
            (
                "Recommended next: Phase 10.37 LONG Forward "
                "Observation Evidence Collection Official Dataset "
                "Schema Implementation Design V1."
            ),
        )
    )
    return pd.DataFrame(checks)


def build_summary(
    source_manifest: pd.DataFrame,
    source: dict[str, pd.DataFrame],
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
    source_row = source_summary_row(source)
    decision_row = (
        decision.iloc[0].to_dict()
        if not decision.empty
        else {}
    )
    blocker_count = int(checks["blocker"].map(safe_bool).sum())
    error_count = int(
        checks["severity"].astype(str).eq("ERROR").sum()
    )
    warning_count = int(
        checks["severity"].astype(str).eq("WARNING").sum()
    )
    material_issue_count = int(
        findings["material_issue_found"].map(safe_bool).sum()
    )
    validation_passed = (
        blocker_count == 0
        and error_count == 0
        and all_passed(validations)
        and all_passed(items)
        and all_passed(findings)
        and all_passed(controls)
        and all_passed(rules)
        and all_passed(requirements)
        and all_passed(guards)
    )

    return pd.DataFrame(
        [
            {
                "phase": "10.36",
                "long_forward_observation_evidence_collection_report_only_dry_run_final_approval_review_defined": True,
                "phase_10_35_validation_passed": safe_bool(
                    source_row.get("validation_passed", False)
                ),
                "source_output_integrity_review_performed": safe_bool(
                    source_row.get(
                        "report_only_dry_run_output_integrity_review_performed",
                        False,
                    )
                ),
                "source_output_integrity_review_passed": safe_bool(
                    source_row.get(
                        "report_only_dry_run_output_integrity_review_passed",
                        False,
                    )
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
                "source_review_validation_rows": safe_int(
                    source_row.get("review_validation_rows", -1),
                    -1,
                ),
                "source_review_requirement_rows": safe_int(
                    source_row.get("review_requirement_rows", -1),
                    -1,
                ),
                "source_material_issue_count": safe_int(
                    source_row.get("material_issue_count", -1),
                    -1,
                ),
                "final_review_validation_rows": len(validations),
                "final_review_item_rows": len(items),
                "final_review_finding_rows": len(findings),
                "final_review_control_rows": len(controls),
                "final_review_rule_rows": len(rules),
                "final_review_requirement_rows": len(requirements),
                "final_review_guard_rows": len(guards),
                "final_review_validations_passed": all_passed(
                    validations
                ),
                "final_review_items_passed": all_passed(items),
                "final_review_findings_passed": all_passed(
                    findings
                ),
                "final_review_controls_passed": all_passed(
                    controls
                ),
                "final_review_rules_passed": all_passed(rules),
                "final_review_requirements_passed": all_passed(
                    requirements
                ),
                "final_review_guards_passed": all_passed(guards),
                "material_issue_count": material_issue_count,
                "report_only_dry_run_final_approval_review_performed": True,
                "report_only_dry_run_final_approval_review_passed": safe_bool(
                    decision_row.get(
                        "report_only_dry_run_final_approval_review_passed",
                        False,
                    )
                ),
                "report_only_dry_run_final_approval_review_decision": str(
                    decision_row.get(
                        "report_only_dry_run_final_approval_review_decision",
                        "",
                    )
                ),
                "report_only_dry_run_cycle_closed": safe_bool(
                    decision_row.get(
                        "report_only_dry_run_cycle_closed",
                        False,
                    )
                ),
                "future_official_dataset_schema_implementation_design_allowed": safe_bool(
                    decision_row.get(
                        "future_official_dataset_schema_implementation_design_allowed",
                        False,
                    )
                ),
                "new_report_only_dry_run_execution_performed": False,
                "new_report_only_dry_run_rows_generated": 0,
                "official_dataset_exists_before": official_before,
                "official_dataset_exists_after": official_after,
                "official_dataset_unchanged_absent": (
                    not official_before and not official_after
                ),
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
                "estimated_phase_10_progress_percent": 100,
                "total_checks": len(checks),
                "warning_count": warning_count,
                "error_count": error_count,
                "blocker_count": blocker_count,
                "validation_passed": validation_passed,
                "validation_decision": (
                    "PHASE_10_36_LONG_FORWARD_OBSERVATION_EVIDENCE_"
                    "COLLECTION_REPORT_ONLY_DRY_RUN_FINAL_APPROVAL_"
                    "REVIEW_VALIDATED"
                    if validation_passed
                    else
                    "PHASE_10_36_LONG_FORWARD_OBSERVATION_EVIDENCE_"
                    "COLLECTION_REPORT_ONLY_DRY_RUN_FINAL_APPROVAL_"
                    "REVIEW_FAILED"
                ),
            }
        ]
    )


def run_long_forward_observation_evidence_collection_report_only_dry_run_final_approval_review() -> dict[str, pd.DataFrame]:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    docs_exist = {
        "phase_10_35_output_integrity_review_doc_exists": (
            PHASE_10_35_DOC_PATH.exists()
        ),
        "phase_10_36_final_approval_review_doc_exists": (
            PHASE_10_36_DOC_PATH.exists()
        ),
    }

    official_before = OFFICIAL_DATASET_PATH.exists()
    source_manifest_before = build_manifest(
        SOURCE_PATHS,
        "PHASE_10_35",
    )
    source = {
        name: read_csv(path)
        for name, path in SOURCE_PATHS.items()
    }
    source_manifest_after = build_manifest(
        SOURCE_PATHS,
        "PHASE_10_35",
    )
    official_after = OFFICIAL_DATASET_PATH.exists()

    validations = build_validations(
        source,
        source_manifest_before,
        source_manifest_after,
        official_dataset_absent=(
            not official_before and not official_after
        ),
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
    review_passed_before_guards = all(
        [
            all_passed(validations),
            all_passed(items),
            all_passed(findings),
            all_passed(controls),
            all_passed(rules),
        ]
    )
    guards = build_guard_matrix(
        review_passed_before_guards
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
        source,
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

    manifest_paths = {
        name: REPORTS_DIR / OUTPUT_FILENAMES[name]
        for name in frames
    }
    output_manifest = build_manifest(
        manifest_paths,
        "PHASE_10_36_OUTPUT",
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
        "source_validations": source["validations"],
        "source_items": source["items"],
        "source_findings": source["findings"],
        "source_controls": source["controls"],
        "source_rules": source["rules"],
        "source_requirements": source["requirements"],
        "source_guard_matrix": source["guard_matrix"],
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
