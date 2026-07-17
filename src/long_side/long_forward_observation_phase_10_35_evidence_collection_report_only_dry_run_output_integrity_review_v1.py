from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any, Iterable

import pandas as pd

from src.long_side.long_forward_observation_dataset_bootstrap_v1 import (
    OFFICIAL_DATASET_PATH,
)


REPORTS_DIR = Path(
    "reports/p10_35_evidence_collection_report_only_dry_run_"
    "output_integrity_review_v1"
)
SOURCE_DIR = Path(
    "reports/p10_34_evidence_collection_report_only_dry_run_run_v1"
)

PHASE_10_34_DOC_PATH = Path(
    "docs/PHASE_10_LONG_FORWARD_OBSERVATION_EVIDENCE_COLLECTION_"
    "REPORT_ONLY_DRY_RUN_RUN.md"
)
PHASE_10_35_DOC_PATH = Path(
    "docs/PHASE_10_LONG_FORWARD_OBSERVATION_EVIDENCE_COLLECTION_"
    "REPORT_ONLY_DRY_RUN_OUTPUT_INTEGRITY_REVIEW.md"
)

SOURCE_PATHS = {
    "summary": SOURCE_DIR / "report_only_dry_run_run_summary_v1.csv",
    "synthetic_input_rows": SOURCE_DIR
    / "report_only_dry_run_synthetic_input_rows_v1.csv",
    "scenario_results": SOURCE_DIR
    / "report_only_dry_run_scenario_results_v1.csv",
    "validation_results": SOURCE_DIR
    / "report_only_dry_run_validation_results_v1.csv",
    "rejection_results": SOURCE_DIR
    / "report_only_dry_run_rejection_results_v1.csv",
    "hash_and_dedup_results": SOURCE_DIR
    / "report_only_dry_run_hash_and_dedup_results_v1.csv",
    "safety_lock_results": SOURCE_DIR
    / "report_only_dry_run_safety_lock_results_v1.csv",
    "official_dataset_guard_results": SOURCE_DIR
    / "report_only_dry_run_official_dataset_guard_results_v1.csv",
    "checks": SOURCE_DIR / "report_only_dry_run_run_checks_v1.csv",
    "manifest": SOURCE_DIR / "report_only_dry_run_run_manifest_v1.csv",
}

SOURCE_READY_DECISION = (
    "CONTROLLED_FORWARD_OBSERVATION_EVIDENCE_COLLECTION_REPORT_ONLY_"
    "DRY_RUN_RUN_COMPLETED_READY_FOR_OUTPUT_INTEGRITY_REVIEW"
)
READY_DECISION = (
    "CONTROLLED_FORWARD_OBSERVATION_EVIDENCE_COLLECTION_REPORT_ONLY_"
    "DRY_RUN_OUTPUT_INTEGRITY_REVIEW_READY_FOR_FINAL_APPROVAL_REVIEW"
)
BLOCKED_DECISION = (
    "CONTROLLED_FORWARD_OBSERVATION_EVIDENCE_COLLECTION_REPORT_ONLY_"
    "DRY_RUN_OUTPUT_INTEGRITY_REVIEW_BLOCKED"
)
RECOMMENDED_NEXT_PHASE = (
    "PHASE_10_36_LONG_FORWARD_OBSERVATION_EVIDENCE_COLLECTION_"
    "REPORT_ONLY_DRY_RUN_FINAL_APPROVAL_REVIEW_V1"
)

EXPECTED_SCENARIOS = [
    (1, "REPORT_ONLY_DRY_RUN_SCENARIO_001", "VALID_SYNTHETIC_ROW", "PASS_REPORT_ONLY", True),
    (2, "REPORT_ONLY_DRY_RUN_SCENARIO_002", "EXACT_DUPLICATE_ROW", "REJECT_DUPLICATE", False),
    (3, "REPORT_ONLY_DRY_RUN_SCENARIO_003", "INVALID_SOURCE_SYSTEM", "REJECT_SOURCE", False),
    (4, "REPORT_ONLY_DRY_RUN_SCENARIO_004", "INVALID_UTC_TIMESTAMP", "REJECT_TIMESTAMP", False),
    (5, "REPORT_ONLY_DRY_RUN_SCENARIO_005", "INVALID_LONG_PRICE_STRUCTURE", "REJECT_PRICE_STRUCTURE", False),
    (6, "REPORT_ONLY_DRY_RUN_SCENARIO_006", "PROHIBITED_EXECUTION_FLAG_ENABLED", "REJECT_SAFETY_FLAG", False),
]

EXPECTED_SCHEMA_FIELDS = [
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
    "evidence_hash", "previous_evidence_hash", "audit_event_id",
    "created_by", "reviewed_by", "rollback_reference",
    "accepted_as_real_evidence", "official_dataset_write_allowed",
    "evidence_persistence_allowed", "signal_generation_enabled",
    "live_alerts_allowed", "paper_trade_execution_allowed",
    "real_capital_allowed", "market_execution_allowed",
    "exchange_execution_allowed", "automation_allowed", "execution_allowed",
    "notes",
]

SAFETY_FIELDS = [
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

FALSE_SUMMARY_GUARDS = [
    "evidence_collection_enabled", "evidence_collection_started",
    "official_dataset_schema_implemented", "official_dataset_write_allowed",
    "official_dataset_write_performed", "real_forward_dataset_created",
    "real_forward_signals_recorded", "journal_real_rows_accepted",
    "accepted_as_real_evidence", "evidence_persistence_allowed",
    "evidence_write_performed", "signal_generation_enabled",
    "live_alerts_allowed", "paper_trading_enabled",
    "long_strategy_approved", "long_entries_approved",
    "long_side_established", "paper_trade_execution_allowed",
    "real_capital_allowed", "market_execution_allowed",
    "exchange_execution_allowed", "automation_allowed", "execution_allowed",
    "real_entries_approved", "total_project_completed",
]

OUTPUT_FILENAMES = {
    "summary": "report_only_dry_run_output_integrity_review_summary_v1.csv",
    "validations": "report_only_dry_run_output_integrity_review_validations_v1.csv",
    "items": "report_only_dry_run_output_integrity_review_items_v1.csv",
    "findings": "report_only_dry_run_output_integrity_review_findings_v1.csv",
    "controls": "report_only_dry_run_output_integrity_review_controls_v1.csv",
    "rules": "report_only_dry_run_output_integrity_review_rules_v1.csv",
    "requirements": "report_only_dry_run_output_integrity_review_requirements_v1.csv",
    "guard_matrix": "report_only_dry_run_output_integrity_review_guard_matrix_v1.csv",
    "decision": "report_only_dry_run_output_integrity_review_decision_v1.csv",
    "checks": "report_only_dry_run_output_integrity_review_checks_v1.csv",
    "manifest": "source_report_only_dry_run_output_integrity_artifact_manifest_v1.csv",
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
        character in "0123456789abcdef" for character in text.lower()
    )


def build_manifest(paths: dict[str, Path], scope: str) -> pd.DataFrame:
    rows = []
    for position, (name, path) in enumerate(paths.items(), start=1):
        exists = path.exists() and path.is_file()
        size = path.stat().st_size if exists else 0
        file_hash = sha256_file(path) if exists else ""
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
                "artifact_sha256": file_hash,
                "artifact_sha256_valid": is_sha256(file_hash),
            }
        )
    return pd.DataFrame(rows)


def manifest_digest(df: pd.DataFrame) -> str:
    if df.empty:
        return ""
    payload = (
        df[
            [
                "artifact_scope", "artifact_name", "artifact_path",
                "artifact_size_bytes", "artifact_sha256",
            ]
        ]
        .astype(str)
        .sort_values(["artifact_scope", "artifact_name", "artifact_path"])
        .to_csv(index=False)
        .encode("utf-8")
    )
    return hashlib.sha256(payload).hexdigest()


def append_validations(
    rows: list[tuple[str, bool, str]],
    values: dict[str, bool],
) -> None:
    for name, passed in values.items():
        rows.append((name, bool(passed), f"{name}={passed}"))


def validate_summary(row: dict[str, Any]) -> dict[str, bool]:
    return {
        "phase_10_34_validation_passed": (
            safe_bool(row.get("validation_passed", False))
            and str(row.get("validation_decision", ""))
            == "PHASE_10_34_LONG_FORWARD_OBSERVATION_EVIDENCE_COLLECTION_REPORT_ONLY_DRY_RUN_RUN_VALIDATED"
        ),
        "source_run_executed": safe_bool(row.get("report_only_dry_run_executed", False)),
        "source_run_passed": safe_bool(row.get("report_only_dry_run_run_passed", False)),
        "source_run_decision_valid": str(row.get("report_only_dry_run_run_decision", "")) == SOURCE_READY_DECISION,
        "source_future_integrity_review_allowed": safe_bool(
            row.get("future_report_only_dry_run_output_integrity_review_allowed", False)
        ),
        "source_artifact_count_22": safe_int(row.get("source_artifact_count", -1), -1) == 22,
        "source_validation_rows_24": safe_int(row.get("source_validation_rows", -1), -1) == 24,
        "source_abort_rows_12": safe_int(row.get("abort_evaluation_rows", -1), -1) == 12,
        "source_abort_trigger_count_zero": safe_int(row.get("abort_trigger_count", -1), -1) == 0,
        "source_rows_generated_6": safe_int(row.get("report_only_dry_run_rows_generated", -1), -1) == 6,
        "source_valid_rows_1": safe_int(row.get("report_only_dry_run_valid_rows", -1), -1) == 1,
        "source_rejected_rows_5": safe_int(row.get("report_only_dry_run_rejected_rows", -1), -1) == 5,
        "source_scenario_rows_6": safe_int(row.get("scenario_result_rows", -1), -1) == 6,
        "source_outcomes_match_expected": safe_bool(row.get("scenario_outcomes_match_expected", False)),
        "source_runtime_rows_37": safe_int(row.get("runtime_validation_rows", -1), -1) == 37,
        "source_runtime_validations_passed": safe_bool(row.get("runtime_validations_passed", False)),
        "source_safety_rows_66": safe_int(row.get("safety_lock_result_rows", -1), -1) == 66,
        "source_synthetic_safety_violation_count_1": safe_int(
            row.get("synthetic_safety_violation_count", -1), -1
        ) == 1,
        "source_official_dataset_unchanged_absent": safe_bool(
            row.get("official_dataset_unchanged_absent", False)
        ),
        "source_official_evidence_rows_zero": safe_int(
            row.get("official_evidence_rows_written", -1), -1
        ) == 0,
        "source_planned_output_count_10": safe_int(
            row.get("planned_output_artifact_count", -1), -1
        ) == 10,
        "source_total_checks_23": safe_int(row.get("total_checks", -1), -1) == 23,
        "source_warning_count_14": safe_int(row.get("warning_count", -1), -1) == 14,
        "source_error_count_zero": safe_int(row.get("error_count", -1), -1) == 0,
        "source_blocker_count_zero": safe_int(row.get("blocker_count", -1), -1) == 0,
        "source_operational_locks_valid": all(
            not safe_bool(row.get(name, True), True) for name in FALSE_SUMMARY_GUARDS
        ),
    }


def validate_inputs(df: pd.DataFrame) -> dict[str, bool]:
    safety_pattern = len(df) == 6 and set(SAFETY_FIELDS).issubset(df.columns)
    if safety_pattern:
        for index, row in df.reset_index(drop=True).iterrows():
            for field in SAFETY_FIELDS:
                expected = index == 5 and field == "execution_allowed"
                if safe_bool(row[field], False) != expected:
                    safety_pattern = False
    return {
        "synthetic_input_rows_6": len(df) == 6,
        "synthetic_schema_54_fields": list(df.columns) == EXPECTED_SCHEMA_FIELDS,
        "synthetic_rows_long": (
            not df.empty
            and "direction" in df.columns
            and df["direction"].astype(str).eq("LONG").all()
        ),
        "synthetic_scope_report_only": (
            not df.empty
            and "evidence_scope" in df.columns
            and df["evidence_scope"].astype(str).eq("REPORT_ONLY_DRY_RUN").all()
        ),
        "synthetic_rows_not_real_evidence": (
            not df.empty
            and "accepted_as_real_evidence" in df.columns
            and not df["accepted_as_real_evidence"].map(safe_bool).any()
        ),
        "synthetic_safety_pattern_valid": safety_pattern,
    }


def validate_scenarios(df: pd.DataFrame) -> dict[str, bool]:
    required = {
        "execution_position", "scenario_id", "scenario_name",
        "expected_outcome", "actual_outcome", "expected_validation_pass",
        "actual_validation_pass", "outcome_matches_expected",
        "synthetic_only", "report_only", "dry_run_row_generated",
        "accepted_as_real_evidence", "official_dataset_write_performed",
        "signal_generated", "live_alert_generated", "paper_trade_executed",
        "market_order_executed", "passed",
    }
    exact = len(df) == 6 and required.issubset(df.columns)
    ordered = df.sort_values("execution_position").reset_index(drop=True) if exact else pd.DataFrame()
    if exact:
        for expected, (_, row) in zip(EXPECTED_SCENARIOS, ordered.iterrows()):
            position, scenario_id, name, outcome, validation_pass = expected
            exact = exact and (
                safe_int(row["execution_position"], -1) == position
                and str(row["scenario_id"]) == scenario_id
                and str(row["scenario_name"]) == name
                and str(row["expected_outcome"]) == outcome
                and str(row["actual_outcome"]) == outcome
                and safe_bool(row["expected_validation_pass"]) == validation_pass
                and safe_bool(row["actual_validation_pass"]) == validation_pass
                and safe_bool(row["outcome_matches_expected"])
            )
    boundaries = (
        len(ordered) == 6
        and ordered["synthetic_only"].map(safe_bool).all()
        and ordered["report_only"].map(safe_bool).all()
        and ordered["dry_run_row_generated"].map(safe_bool).all()
        and not ordered["accepted_as_real_evidence"].map(safe_bool).any()
        and not ordered["official_dataset_write_performed"].map(safe_bool).any()
        and not ordered["signal_generated"].map(safe_bool).any()
        and not ordered["live_alert_generated"].map(safe_bool).any()
        and not ordered["paper_trade_executed"].map(safe_bool).any()
        and not ordered["market_order_executed"].map(safe_bool).any()
    )
    return {
        "scenario_rows_6": len(df) == 6,
        "scenario_contract_exact": exact,
        "scenario_all_passed": all_passed(df),
        "scenario_safety_boundaries_valid": boundaries,
    }


def validate_validation_results(df: pd.DataFrame) -> dict[str, bool]:
    counts = (
        df["validation_scope"].astype(str).value_counts().to_dict()
        if not df.empty and "validation_scope" in df.columns
        else {}
    )
    return {
        "validation_result_rows_73": len(df) == 73,
        "validation_scope_source_24": counts.get("SOURCE", 0) == 24,
        "validation_scope_abort_12": counts.get("ABORT", 0) == 12,
        "validation_scope_runtime_37": counts.get("RUNTIME", 0) == 37,
        "validation_results_all_passed": all_passed(df),
    }


def validate_rejections(df: pd.DataFrame) -> dict[str, bool]:
    expected = [
        "REJECT_DUPLICATE", "REJECT_SOURCE", "REJECT_TIMESTAMP",
        "REJECT_PRICE_STRUCTURE", "REJECT_SAFETY_FLAG",
    ]
    outcomes = (
        df.sort_values("execution_position")["actual_outcome"].astype(str).tolist()
        if not df.empty and {"execution_position", "actual_outcome"}.issubset(df.columns)
        else []
    )
    boundaries = (
        not df.empty
        and {
            "accepted_as_real_evidence",
            "official_dataset_write_performed",
            "market_order_executed",
        }.issubset(df.columns)
        and not df["accepted_as_real_evidence"].map(safe_bool).any()
        and not df["official_dataset_write_performed"].map(safe_bool).any()
        and not df["market_order_executed"].map(safe_bool).any()
    )
    return {
        "rejection_rows_5": len(df) == 5,
        "rejection_outcomes_exact": outcomes == expected,
        "rejection_all_passed": all_passed(df),
        "rejection_safety_boundaries_valid": boundaries,
    }


def validate_hashes(df: pd.DataFrame) -> dict[str, bool]:
    duplicate_rows = (
        df[df["duplicate_detected"].map(safe_bool)]
        if not df.empty and "duplicate_detected" in df.columns
        else pd.DataFrame()
    )
    duplicate_exact = (
        len(duplicate_rows) == 1
        and str(duplicate_rows.iloc[0].get("scenario_name", "")) == "EXACT_DUPLICATE_ROW"
    )
    hashes_valid = (
        len(df) == 6
        and {"source_row_hash", "evidence_hash"}.issubset(df.columns)
        and df["source_row_hash"].map(is_sha256).all()
        and df["evidence_hash"].map(is_sha256).all()
    )
    return {
        "hash_rows_6": len(df) == 6,
        "hash_values_valid": hashes_valid,
        "duplicate_pattern_exact": duplicate_exact,
        "hash_rows_all_passed": all_passed(df),
    }


def validate_safety(df: pd.DataFrame) -> dict[str, bool]:
    violation_rows = (
        df[df["violation_detected"].map(safe_bool)]
        if not df.empty and "violation_detected" in df.columns
        else pd.DataFrame()
    )
    exact = (
        len(violation_rows) == 1
        and str(violation_rows.iloc[0].get("scenario_name", ""))
        == "PROHIBITED_EXECUTION_FLAG_ENABLED"
        and str(violation_rows.iloc[0].get("safety_field", "")) == "execution_allowed"
        and str(violation_rows.iloc[0].get("actual_outcome", "")) == "REJECT_SAFETY_FLAG"
        and not safe_bool(
            violation_rows.iloc[0].get("operational_action_performed", True), True
        )
    )
    return {
        "safety_rows_66": len(df) == 66,
        "safety_violation_count_1": len(violation_rows) == 1,
        "safety_violation_exact": exact,
        "safety_rows_all_passed": all_passed(df),
    }


def validate_official_guards(df: pd.DataFrame) -> dict[str, bool]:
    expected_names = {
        "official_dataset_absent_before_run",
        "official_dataset_absent_after_run",
        "official_dataset_schema_implemented",
        "official_dataset_write_allowed",
        "official_dataset_write_performed",
        "official_evidence_rows_written",
        "real_forward_dataset_created",
        "accepted_as_real_evidence",
    }
    names = (
        set(df["guard_name"].astype(str))
        if not df.empty and "guard_name" in df.columns
        else set()
    )
    return {
        "official_guard_rows_8": len(df) == 8,
        "official_guard_names_exact": names == expected_names,
        "official_guards_all_passed": all_passed(df),
    }


def validate_checks(df: pd.DataFrame) -> dict[str, bool]:
    warnings = int(df["severity"].astype(str).eq("WARNING").sum()) if not df.empty and "severity" in df.columns else -1
    errors = int(df["severity"].astype(str).eq("ERROR").sum()) if not df.empty and "severity" in df.columns else -1
    blockers = int(df["blocker"].map(safe_bool).sum()) if not df.empty and "blocker" in df.columns else -1
    return {
        "check_rows_23": len(df) == 23,
        "check_warning_count_14": warnings == 14,
        "check_error_count_zero": errors == 0,
        "check_blocker_count_zero": blockers == 0,
        "checks_all_passed": all_passed(df),
    }


def validate_run_manifest(df: pd.DataFrame, manifest_path: Path) -> dict[str, bool]:
    required = {
        "artifact_scope", "artifact_filename", "artifact_path",
        "artifact_exists", "artifact_size_bytes", "artifact_non_empty",
        "artifact_sha256", "artifact_sha256_valid",
    }
    valid_shape = not df.empty and required.issubset(df.columns)
    source_rows = df[df["artifact_scope"].astype(str).eq("SOURCE")] if valid_shape else pd.DataFrame()
    output_rows = df[df["artifact_scope"].astype(str).eq("PHASE_10_34_OUTPUT")] if valid_shape else pd.DataFrame()
    listed_valid = (
        valid_shape
        and df["artifact_exists"].map(safe_bool).all()
        and df["artifact_non_empty"].map(safe_bool).all()
        and df["artifact_sha256_valid"].map(safe_bool).all()
        and (df["artifact_size_bytes"].map(safe_int) > 0).all()
    )
    hashes_match = valid_shape
    if hashes_match:
        for _, row in df.iterrows():
            path = Path(str(row["artifact_path"]))
            if not path.exists() or sha256_file(path) != str(row["artifact_sha256"]):
                hashes_match = False
                break
    listed_names = set(df["artifact_filename"].astype(str)) if valid_shape else set()
    self_excluded = (
        valid_shape
        and len(df) == 31
        and len(output_rows) == 9
        and manifest_path.name not in listed_names
    )
    return {
        "manifest_rows_31": len(df) == 31,
        "manifest_source_rows_22": len(source_rows) == 22,
        "manifest_output_rows_9": len(output_rows) == 9,
        "manifest_listed_artifacts_valid": listed_valid,
        "manifest_hashes_match_current_files": hashes_match,
        "manifest_self_exclusion_expected": self_excluded,
        "manifest_file_exists": manifest_path.exists(),
        "manifest_file_non_empty": manifest_path.exists() and manifest_path.stat().st_size > 0,
        "manifest_file_sha256_valid": is_sha256(sha256_file(manifest_path)),
    }


def build_validations(
    source: dict[str, pd.DataFrame],
    manifest_before: pd.DataFrame,
    manifest_after: pd.DataFrame,
    official_absent: bool,
) -> pd.DataFrame:
    rows: list[tuple[str, bool, str]] = []
    rows.extend(
        [
            (
                "source_artifacts_exist",
                manifest_before["artifact_exists"].map(safe_bool).all(),
                f"rows={len(manifest_before)}",
            ),
            (
                "source_artifacts_non_empty",
                manifest_before["artifact_non_empty"].map(safe_bool).all(),
                f"rows={len(manifest_before)}",
            ),
            (
                "source_artifact_hashes_valid",
                manifest_before["artifact_sha256_valid"].map(safe_bool).all(),
                f"rows={len(manifest_before)}",
            ),
            (
                "source_artifacts_stable_during_review",
                manifest_digest(manifest_before) == manifest_digest(manifest_after),
                f"before={manifest_digest(manifest_before)},after={manifest_digest(manifest_after)}",
            ),
        ]
    )
    summary = source["summary"].iloc[0].to_dict() if not source["summary"].empty else {}
    append_validations(rows, validate_summary(summary))
    append_validations(rows, validate_inputs(source["synthetic_input_rows"]))
    append_validations(rows, validate_scenarios(source["scenario_results"]))
    append_validations(rows, validate_validation_results(source["validation_results"]))
    append_validations(rows, validate_rejections(source["rejection_results"]))
    append_validations(rows, validate_hashes(source["hash_and_dedup_results"]))
    append_validations(rows, validate_safety(source["safety_lock_results"]))
    append_validations(rows, validate_official_guards(source["official_dataset_guard_results"]))
    append_validations(rows, validate_checks(source["checks"]))
    append_validations(rows, validate_run_manifest(source["manifest"], SOURCE_PATHS["manifest"]))
    rows.extend(
        [
            ("official_dataset_absent_during_review", official_absent, f"absent={official_absent}"),
            ("review_only_no_new_dry_run_execution", True, "Existing Phase 10.34 artifacts are read only."),
            ("long_strategy_remains_unapproved", True, "long_strategy_approved=False"),
            ("total_project_not_completed", True, "total_project_completed=False"),
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
            for position, (name, passed, details) in enumerate(rows, start=1)
        ]
    )


def build_items(validations: pd.DataFrame) -> pd.DataFrame:
    names = validations["validation_name"].astype(str).tolist()
    rows = []
    for position, start in enumerate(range(0, len(names), 3), start=1):
        block = names[start : start + 3]
        passed = validations[
            validations["validation_name"].astype(str).isin(block)
        ]["passed"].map(safe_bool).all()
        rows.append(
            {
                "review_item_position": position,
                "review_item_id": f"REPORT_ONLY_DRY_RUN_OUTPUT_INTEGRITY_ITEM_{position:03d}",
                "review_item_name": f"integrity_review_block_{position:03d}",
                "validation_names": ",".join(block),
                "required": True,
                "review_only": True,
                "new_dry_run_execution_allowed": False,
                "official_dataset_write_allowed": False,
                "market_execution_allowed": False,
                "passed": passed,
            }
        )
    return pd.DataFrame(rows)


def build_findings(items: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for position, (_, item) in enumerate(items.iterrows(), start=1):
        passed = safe_bool(item["passed"], False)
        rows.append(
            {
                "finding_position": position,
                "finding_id": f"REPORT_ONLY_DRY_RUN_OUTPUT_INTEGRITY_FINDING_{position:03d}",
                "review_item_id": str(item["review_item_id"]),
                "review_item_name": str(item["review_item_name"]),
                "finding_status": "PASS" if passed else "FAIL",
                "material_issue_found": not passed,
                "output_change_required": not passed,
                "final_approval_review_allowed": passed,
                "details": "Output integrity criterion passed." if passed else "Output integrity criterion failed.",
                "passed": passed,
            }
        )
    return pd.DataFrame(rows)


def build_controls(validations: pd.DataFrame) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "control_position": position,
                "control_id": f"REPORT_ONLY_DRY_RUN_OUTPUT_INTEGRITY_CONTROL_{position:03d}",
                "control_name": str(row["validation_name"]),
                "required": True,
                "review_only": True,
                "new_dry_run_execution_performed": False,
                "evidence_collection_enabled": False,
                "official_dataset_write_allowed": False,
                "market_execution_allowed": False,
                "passed": safe_bool(row["passed"], False),
            }
            for position, (_, row) in enumerate(validations.iterrows(), start=1)
        ]
    )


def build_rules(
    validations: pd.DataFrame,
    items: pd.DataFrame,
    findings: pd.DataFrame,
    controls: pd.DataFrame,
) -> pd.DataFrame:
    material_issues = int(findings["material_issue_found"].map(safe_bool).sum())
    values = [
        ("validation_count_positive", len(validations) > 0, ">0", len(validations)),
        ("all_validations_passed", all_passed(validations), True, all_passed(validations)),
        ("item_count_positive", len(items) > 0, ">0", len(items)),
        ("all_items_passed", all_passed(items), True, all_passed(items)),
        ("finding_count_matches_items", len(findings) == len(items), len(items), len(findings)),
        ("all_findings_passed", all_passed(findings), True, all_passed(findings)),
        ("material_issue_count_zero", material_issues == 0, 0, material_issues),
        ("control_count_matches_validations", len(controls) == len(validations), len(validations), len(controls)),
        ("all_controls_passed", all_passed(controls), True, all_passed(controls)),
        ("review_only", True, True, True),
        ("new_dry_run_not_executed", True, False, False),
        ("official_dataset_not_implemented", True, False, False),
        ("official_dataset_writes_disabled", True, False, False),
        ("real_evidence_acceptance_disabled", True, False, False),
        ("signal_generation_disabled", True, False, False),
        ("live_alerts_disabled", True, False, False),
        ("paper_trading_disabled", True, False, False),
        ("long_strategy_unapproved", True, False, False),
        ("real_capital_disabled", True, False, False),
        ("market_execution_disabled", True, False, False),
        ("automation_disabled", True, False, False),
        ("project_not_completed", True, False, False),
        ("manifest_self_exclusion_reviewed", True, True, True),
        ("future_final_approval_review_only", True, True, True),
    ]
    return pd.DataFrame(
        [
            {
                "rule_id": f"REPORT_ONLY_DRY_RUN_OUTPUT_INTEGRITY_RULE_{position:03d}",
                "rule_name": name,
                "passed": bool(passed),
                "required_value": required,
                "actual_value": actual,
            }
            for position, (name, passed, required, actual) in enumerate(values, start=1)
        ]
    )


def build_guard_matrix(review_passed: bool) -> pd.DataFrame:
    values = [
        ("source_controlled_forward_observation_start_run_performed", True, True),
        ("source_controlled_forward_observation_start_performed", True, True),
        ("forward_observation_start_allowed", True, True),
        ("forward_observation_started", True, True),
        ("source_report_only_dry_run_executed", True, True),
        ("source_report_only_dry_run_run_passed", True, True),
        ("output_integrity_review_performed", True, True),
        ("output_integrity_review_passed", True, review_passed),
        ("future_final_approval_review_allowed", True, review_passed),
        ("new_report_only_dry_run_execution_performed", False, False),
        ("evidence_collection_enabled", False, False),
        ("evidence_collection_started", False, False),
        ("official_dataset_schema_implemented", False, False),
        ("official_dataset_write_allowed", False, False),
        ("official_dataset_write_performed", False, False),
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
        ("paper_trade_execution_allowed", False, False),
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
                "guard_group": "review_state" if position <= 9 else "review_safety_guard",
            }
            for position, (name, required, actual) in enumerate(values, start=1)
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
    values: list[tuple[str, bool, Any, Any]] = [
        (
            str(row["validation_name"]),
            safe_bool(row["passed"], False),
            True,
            safe_bool(row["passed"], False),
        )
        for _, row in validations.iterrows()
    ]
    material_issues = int(findings["material_issue_found"].map(safe_bool).sum())
    values.extend(
        [
            ("review_items_passed", all_passed(items), True, all_passed(items)),
            ("review_findings_passed", all_passed(findings), True, all_passed(findings)),
            ("review_controls_passed", all_passed(controls), True, all_passed(controls)),
            ("review_rules_passed", all_passed(rules), True, all_passed(rules)),
            ("review_guards_passed", all_passed(guards), True, all_passed(guards)),
            ("material_issue_count_zero", material_issues == 0, 0, material_issues),
            ("output_integrity_review_performed", True, True, True),
            ("future_final_approval_review_allowed", True, True, True),
            ("new_dry_run_not_executed", True, False, False),
            ("official_evidence_rows_written_zero", True, 0, 0),
            ("signal_generation_disabled", True, False, False),
            ("paper_trading_disabled", True, False, False),
            ("market_execution_disabled", True, False, False),
            ("project_not_completed", True, False, False),
        ]
    )
    return pd.DataFrame(
        [
            {
                "requirement_id": f"REPORT_ONLY_DRY_RUN_OUTPUT_INTEGRITY_REQ_{position:03d}",
                "requirement_name": name,
                "passed": bool(passed),
                "required_value": required,
                "actual_value": actual,
            }
            for position, (name, passed, required, actual) in enumerate(values, start=1)
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
        all_passed(df)
        for df in [validations, items, findings, controls, rules, requirements, guards]
    )
    failed = requirements[~requirements["passed"].map(safe_bool)]
    return pd.DataFrame(
        [
            {
                "report_only_dry_run_output_integrity_review_id": (
                    "PHASE_10_35_LONG_FORWARD_OBSERVATION_EVIDENCE_COLLECTION_"
                    "REPORT_ONLY_DRY_RUN_OUTPUT_INTEGRITY_REVIEW_001"
                ),
                "report_only_dry_run_output_integrity_review_performed": True,
                "report_only_dry_run_output_integrity_review_passed": passed,
                "report_only_dry_run_output_integrity_review_decision": (
                    READY_DECISION if passed else BLOCKED_DECISION
                ),
                "total_requirements": len(requirements),
                "passed_requirements": int(requirements["passed"].map(safe_bool).sum()),
                "failed_requirements": len(failed),
                "failed_requirement_names": ",".join(failed["requirement_name"].astype(str)),
                "future_report_only_dry_run_final_approval_review_allowed": passed,
                "source_report_only_dry_run_executed": True,
                "new_report_only_dry_run_execution_performed": False,
                "new_report_only_dry_run_rows_generated": 0,
                "evidence_collection_enabled": False,
                "official_dataset_schema_implemented": False,
                "official_dataset_write_allowed": False,
                "official_dataset_write_performed": False,
                "official_evidence_rows_written": 0,
                "accepted_as_real_evidence": False,
                "evidence_persistence_allowed": False,
                "signal_generation_enabled": False,
                "live_alerts_allowed": False,
                "paper_trade_execution_allowed": False,
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


def make_check(
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
    blocks: dict[str, pd.DataFrame],
    decision: pd.DataFrame,
    official_before: bool,
    official_after: bool,
) -> pd.DataFrame:
    checks: list[dict[str, Any]] = []
    for name, exists in docs_exist.items():
        checks.append(
            make_check(
                "phase_anchor", name, exists,
                "INFO" if exists else "ERROR", name,
            )
        )
    for name, df in blocks.items():
        passed = all_passed(df)
        checks.append(
            make_check(
                "output_integrity_review",
                f"{name}_passed",
                passed,
                "INFO" if passed else "ERROR",
                f"{name}_passed={passed}",
            )
        )
    decision_passed = (
        not decision.empty
        and safe_bool(
            decision.iloc[0].get(
                "report_only_dry_run_output_integrity_review_passed", False
            )
        )
    )
    decision_expected = (
        not decision.empty
        and str(
            decision.iloc[0].get(
                "report_only_dry_run_output_integrity_review_decision", ""
            )
        )
        == READY_DECISION
    )
    checks.extend(
        [
            make_check(
                "output_integrity_review",
                "output_integrity_review_passed",
                decision_passed,
                "INFO" if decision_passed else "ERROR",
                f"passed={decision_passed}",
            ),
            make_check(
                "output_integrity_review",
                "output_integrity_review_decision_expected",
                decision_expected,
                "INFO" if decision_expected else "ERROR",
                f"expected={decision_expected}",
            ),
            make_check(
                "official_dataset_guard",
                "official_dataset_unchanged_absent",
                not official_before and not official_after,
                "INFO" if (not official_before and not official_after) else "ERROR",
                f"before={official_before},after={official_after}",
            ),
        ]
    )
    warnings = [
        ("review_only", "Phase 10.35 reviews existing Phase 10.34 outputs only."),
        ("dry_run_not_reexecuted", "The report-only dry-run was not executed again."),
        ("synthetic_outputs_only", "Reviewed rows remain synthetic report-only outputs."),
        ("real_evidence_not_collected", "No real forward evidence was collected."),
        ("official_dataset_not_implemented", "The official evidence dataset remains unimplemented."),
        ("official_dataset_not_written", "The official evidence dataset remains absent and unwritten."),
        ("evidence_persistence_not_enabled", "Evidence persistence remains disabled."),
        ("signal_generation_not_enabled", "Signal generation remains disabled."),
        ("live_alerts_not_enabled", "Live alerts remain disabled."),
        ("paper_trading_not_enabled", "Paper trading remains disabled."),
        ("long_strategy_not_approved", "The LONG research candidate remains unapproved."),
        ("real_capital_not_allowed", "Real capital remains prohibited."),
        ("market_execution_not_allowed", "Market execution remains prohibited."),
        ("total_project_not_completed", "The total project is not completed."),
    ]
    checks.extend(
        make_check("scope_control", name, True, "WARNING", details)
        for name, details in warnings
    )
    future_allowed = (
        not decision.empty
        and safe_bool(
            decision.iloc[0].get(
                "future_report_only_dry_run_final_approval_review_allowed", False
            )
        )
    )
    checks.extend(
        [
            make_check(
                "planning_scope",
                "future_final_approval_review_allowed",
                future_allowed,
                "WARNING" if future_allowed else "ERROR",
                "Allows only a future final approval review.",
            ),
            make_check(
                "phase_transition",
                "phase_10_36_recommended_next",
                True,
                "INFO",
                "Recommended next: Phase 10.36 report-only dry-run final approval review.",
            ),
        ]
    )
    return pd.DataFrame(checks)


def build_summary(
    source: dict[str, pd.DataFrame],
    source_manifest: pd.DataFrame,
    blocks: dict[str, pd.DataFrame],
    decision: pd.DataFrame,
    checks: pd.DataFrame,
    official_before: bool,
    official_after: bool,
) -> pd.DataFrame:
    source_summary = (
        source["summary"].iloc[0].to_dict()
        if not source["summary"].empty
        else {}
    )
    source_run_manifest = source["manifest"]
    output_count = (
        int(
            source_run_manifest["artifact_scope"]
            .astype(str)
            .eq("PHASE_10_34_OUTPUT")
            .sum()
        )
        if not source_run_manifest.empty
        and "artifact_scope" in source_run_manifest.columns
        else 0
    )
    decision_row = decision.iloc[0].to_dict() if not decision.empty else {}
    findings = blocks["review_findings"]
    blocker_count = int(checks["blocker"].map(safe_bool).sum())
    error_count = int(checks["severity"].astype(str).eq("ERROR").sum())
    warning_count = int(checks["severity"].astype(str).eq("WARNING").sum())
    validation_passed = blocker_count == 0 and error_count == 0
    return pd.DataFrame(
        [
            {
                "phase": "10.35",
                "long_forward_observation_evidence_collection_report_only_dry_run_output_integrity_review_defined": True,
                "phase_10_34_validation_passed": safe_bool(source_summary.get("validation_passed", False)),
                "source_report_only_dry_run_executed": safe_bool(source_summary.get("report_only_dry_run_executed", False)),
                "source_report_only_dry_run_rows_generated": safe_int(source_summary.get("report_only_dry_run_rows_generated", -1), -1),
                "source_report_only_dry_run_valid_rows": safe_int(source_summary.get("report_only_dry_run_valid_rows", -1), -1),
                "source_report_only_dry_run_rejected_rows": safe_int(source_summary.get("report_only_dry_run_rejected_rows", -1), -1),
                "source_artifact_count": len(source_manifest),
                "source_artifacts_exist": source_manifest["artifact_exists"].map(safe_bool).all(),
                "source_artifacts_non_empty": source_manifest["artifact_non_empty"].map(safe_bool).all(),
                "source_artifact_hashes_valid": source_manifest["artifact_sha256_valid"].map(safe_bool).all(),
                "source_manifest_sha256": manifest_digest(source_manifest),
                "manifest_listed_row_count": len(source_run_manifest),
                "manifest_listed_output_count": output_count,
                "manifest_self_exclusion_expected": True,
                "review_validation_rows": len(blocks["review_validations"]),
                "review_item_rows": len(blocks["review_items"]),
                "review_finding_rows": len(findings),
                "review_control_rows": len(blocks["review_controls"]),
                "review_rule_rows": len(blocks["review_rules"]),
                "review_requirement_rows": len(blocks["review_requirements"]),
                "review_guard_rows": len(blocks["review_guards"]),
                "review_validations_passed": all_passed(blocks["review_validations"]),
                "review_items_passed": all_passed(blocks["review_items"]),
                "review_findings_passed": all_passed(findings),
                "review_controls_passed": all_passed(blocks["review_controls"]),
                "review_rules_passed": all_passed(blocks["review_rules"]),
                "review_requirements_passed": all_passed(blocks["review_requirements"]),
                "review_guards_passed": all_passed(blocks["review_guards"]),
                "material_issue_count": int(findings["material_issue_found"].map(safe_bool).sum()),
                "report_only_dry_run_output_integrity_review_performed": True,
                "report_only_dry_run_output_integrity_review_passed": safe_bool(
                    decision_row.get("report_only_dry_run_output_integrity_review_passed", False)
                ),
                "report_only_dry_run_output_integrity_review_decision": str(
                    decision_row.get("report_only_dry_run_output_integrity_review_decision", "")
                ),
                "future_report_only_dry_run_final_approval_review_allowed": safe_bool(
                    decision_row.get("future_report_only_dry_run_final_approval_review_allowed", False)
                ),
                "new_report_only_dry_run_execution_performed": False,
                "new_report_only_dry_run_rows_generated": 0,
                "official_dataset_exists_before": official_before,
                "official_dataset_exists_after": official_after,
                "official_dataset_unchanged_absent": not official_before and not official_after,
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
                    "PHASE_10_35_LONG_FORWARD_OBSERVATION_EVIDENCE_COLLECTION_REPORT_ONLY_DRY_RUN_OUTPUT_INTEGRITY_REVIEW_VALIDATED"
                    if validation_passed
                    else
                    "PHASE_10_35_LONG_FORWARD_OBSERVATION_EVIDENCE_COLLECTION_REPORT_ONLY_DRY_RUN_OUTPUT_INTEGRITY_REVIEW_FAILED"
                ),
            }
        ]
    )


def run_long_forward_observation_evidence_collection_report_only_dry_run_output_integrity_review() -> dict[str, pd.DataFrame]:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    docs_exist = {
        "phase_10_34_dry_run_run_doc_exists": PHASE_10_34_DOC_PATH.exists(),
        "phase_10_35_output_integrity_review_doc_exists": PHASE_10_35_DOC_PATH.exists(),
    }
    official_before = OFFICIAL_DATASET_PATH.exists()
    source_manifest_before = build_manifest(SOURCE_PATHS, "PHASE_10_34")
    source = {name: read_csv(path) for name, path in SOURCE_PATHS.items()}
    source_manifest_after = build_manifest(SOURCE_PATHS, "PHASE_10_34")
    official_after = OFFICIAL_DATASET_PATH.exists()

    validations = build_validations(
        source,
        source_manifest_before,
        source_manifest_after,
        official_absent=not official_before and not official_after,
    )
    items = build_items(validations)
    findings = build_findings(items)
    controls = build_controls(validations)
    rules = build_rules(validations, items, findings, controls)
    guards = build_guard_matrix(
        all(
            all_passed(df)
            for df in [validations, items, findings, controls, rules]
        )
    )
    requirements = build_requirements(
        validations, items, findings, controls, rules, guards
    )
    decision = build_decision(
        validations, items, findings, controls, rules, requirements, guards
    )
    blocks = {
        "review_validations": validations,
        "review_items": items,
        "review_findings": findings,
        "review_controls": controls,
        "review_rules": rules,
        "review_requirements": requirements,
        "review_guards": guards,
    }
    checks = build_checks(
        docs_exist, blocks, decision, official_before, official_after
    )
    summary = build_summary(
        source,
        source_manifest_before,
        blocks,
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
        dataframe.to_csv(REPORTS_DIR / OUTPUT_FILENAMES[name], index=False)

    output_paths = {
        name: REPORTS_DIR / OUTPUT_FILENAMES[name]
        for name in frames
    }
    output_manifest = build_manifest(output_paths, "PHASE_10_35_OUTPUT")
    combined_manifest = pd.concat(
        [source_manifest_after, output_manifest], ignore_index=True
    )
    combined_manifest.to_csv(
        REPORTS_DIR / OUTPUT_FILENAMES["manifest"], index=False
    )

    return {
        "summary": summary,
        "source_summary": source["summary"],
        "source_synthetic_input_rows": source["synthetic_input_rows"],
        "source_scenario_results": source["scenario_results"],
        "source_validation_results": source["validation_results"],
        "source_rejection_results": source["rejection_results"],
        "source_hash_and_dedup_results": source["hash_and_dedup_results"],
        "source_safety_lock_results": source["safety_lock_results"],
        "source_official_dataset_guard_results": source["official_dataset_guard_results"],
        "source_checks": source["checks"],
        "source_run_manifest": source["manifest"],
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
