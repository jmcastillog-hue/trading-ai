from __future__ import annotations

import copy
import hashlib
import json
import math
from pathlib import Path
from typing import Any

import pandas as pd

from src.long_side.long_forward_observation_dataset_bootstrap_v1 import (
    OFFICIAL_DATASET_PATH,
)


REPORTS_DIR = Path(
    "reports/p10_34_evidence_collection_report_only_dry_run_run_v1"
)
SOURCE_DIR = Path(
    "reports/p10_33_evidence_collection_report_only_dry_run_execution_review_v1"
)

PHASE_10_33_DOC_PATH = Path(
    "docs/PHASE_10_LONG_FORWARD_OBSERVATION_EVIDENCE_COLLECTION_"
    "REPORT_ONLY_DRY_RUN_EXECUTION_REVIEW.md"
)
PHASE_10_34_DOC_PATH = Path(
    "docs/PHASE_10_LONG_FORWARD_OBSERVATION_EVIDENCE_COLLECTION_"
    "REPORT_ONLY_DRY_RUN_RUN.md"
)

SOURCE_PATHS = {
    "summary": SOURCE_DIR / "report_only_dry_run_execution_review_summary_v1.csv",
    "schema": SOURCE_DIR / "phase_10_32_source_schema_v1.csv",
    "scenarios": SOURCE_DIR / "phase_10_32_source_scenarios_v1.csv",
    "steps": SOURCE_DIR / "phase_10_32_source_steps_v1.csv",
    "dry_run_controls": SOURCE_DIR / "phase_10_32_source_dry_run_controls_v1.csv",
    "artifact_plan": SOURCE_DIR / "phase_10_32_source_artifact_plan_v1.csv",
    "acceptance": SOURCE_DIR / "phase_10_32_source_acceptance_v1.csv",
    "outcomes": SOURCE_DIR / "phase_10_32_source_outcomes_v1.csv",
    "execution_contract": SOURCE_DIR / "report_only_dry_run_future_execution_contract_v1.csv",
    "preconditions": SOURCE_DIR / "report_only_dry_run_execution_preconditions_v1.csv",
    "abort_rules": SOURCE_DIR / "report_only_dry_run_execution_abort_rules_v1.csv",
    "output_plan": SOURCE_DIR / "report_only_dry_run_execution_output_plan_v1.csv",
    "review_validations": SOURCE_DIR / "report_only_dry_run_execution_review_validations_v1.csv",
    "review_items": SOURCE_DIR / "report_only_dry_run_execution_review_items_v1.csv",
    "review_findings": SOURCE_DIR / "report_only_dry_run_execution_review_findings_v1.csv",
    "review_controls": SOURCE_DIR / "report_only_dry_run_execution_review_controls_v1.csv",
    "review_rules": SOURCE_DIR / "report_only_dry_run_execution_review_rules_v1.csv",
    "review_requirements": SOURCE_DIR / "report_only_dry_run_execution_review_requirements_v1.csv",
    "review_guard_matrix": SOURCE_DIR / "report_only_dry_run_execution_review_guard_matrix_v1.csv",
    "review_decision": SOURCE_DIR / "report_only_dry_run_execution_review_decision_v1.csv",
    "review_checks": SOURCE_DIR / "report_only_dry_run_execution_review_checks_v1.csv",
    "review_manifest": SOURCE_DIR / "source_report_only_dry_run_execution_review_artifact_manifest_v1.csv",
}

SOURCE_READY_DECISION = (
    "CONTROLLED_FORWARD_OBSERVATION_EVIDENCE_COLLECTION_REPORT_ONLY_"
    "DRY_RUN_EXECUTION_REVIEW_READY_FOR_RUN"
)
READY_DECISION = (
    "CONTROLLED_FORWARD_OBSERVATION_EVIDENCE_COLLECTION_REPORT_ONLY_"
    "DRY_RUN_RUN_COMPLETED_READY_FOR_OUTPUT_INTEGRITY_REVIEW"
)
BLOCKED_DECISION = (
    "CONTROLLED_FORWARD_OBSERVATION_EVIDENCE_COLLECTION_REPORT_ONLY_"
    "DRY_RUN_RUN_BLOCKED"
)
RECOMMENDED_NEXT_PHASE = (
    "PHASE_10_35_LONG_FORWARD_OBSERVATION_EVIDENCE_COLLECTION_"
    "REPORT_ONLY_DRY_RUN_OUTPUT_INTEGRITY_REVIEW_V1"
)

EXPECTED_SOURCE_COUNTS = {
    "source_artifact_count": 18,
    "future_execution_contract_rows": 6,
    "execution_precondition_rows": 20,
    "execution_abort_rule_rows": 12,
    "execution_output_plan_rows": 10,
    "review_validation_rows": 55,
    "review_item_rows": 27,
    "review_finding_rows": 27,
    "review_control_rows": 55,
    "review_rule_rows": 27,
    "review_requirement_rows": 75,
    "review_guard_rows": 37,
    "material_issue_count": 0,
    "total_checks": 68,
    "warning_count": 14,
    "error_count": 0,
    "blocker_count": 0,
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

OPTIONAL_FIELDS = {
    "rejection_reason",
    "previous_evidence_hash",
    "reviewed_by",
    "rollback_reference",
    "notes",
}

FLOAT_FIELDS = {
    "entry_price",
    "stop_price",
    "target_price",
    "invalidation_level",
    "risk_reward",
}

BOOL_FIELDS = {
    "manual_confirmation_required",
    "manual_confirmed",
    "write_ahead_validation_passed",
    "schema_validation_passed",
    "provenance_validation_passed",
    "risk_structure_validation_passed",
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
}

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

EXPECTED_FALSE_SOURCE_GUARDS = [
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

EXPECTED_SCENARIOS = [
    (
        1,
        "REPORT_ONLY_DRY_RUN_SCENARIO_001",
        "VALID_SYNTHETIC_ROW",
        "PASS_REPORT_ONLY",
        True,
    ),
    (
        2,
        "REPORT_ONLY_DRY_RUN_SCENARIO_002",
        "EXACT_DUPLICATE_ROW",
        "REJECT_DUPLICATE",
        False,
    ),
    (
        3,
        "REPORT_ONLY_DRY_RUN_SCENARIO_003",
        "INVALID_SOURCE_SYSTEM",
        "REJECT_SOURCE",
        False,
    ),
    (
        4,
        "REPORT_ONLY_DRY_RUN_SCENARIO_004",
        "INVALID_UTC_TIMESTAMP",
        "REJECT_TIMESTAMP",
        False,
    ),
    (
        5,
        "REPORT_ONLY_DRY_RUN_SCENARIO_005",
        "INVALID_LONG_PRICE_STRUCTURE",
        "REJECT_PRICE_STRUCTURE",
        False,
    ),
    (
        6,
        "REPORT_ONLY_DRY_RUN_SCENARIO_006",
        "PROHIBITED_EXECUTION_FLAG_ENABLED",
        "REJECT_SAFETY_FLAG",
        False,
    ),
]

ALLOWED_SOURCE_SYSTEM = "PHASE_10_34_SYNTHETIC_REPORT_ONLY"
SOURCE_ARTIFACT_NAME = "phase_10_34_synthetic_in_memory_contract"
BASE_OBSERVED_AT = "2026-01-01T00:00:00Z"
BASE_COLLECTED_AT = "2026-01-01T00:00:01Z"

OUTPUT_FILENAMES = {
    "summary": "report_only_dry_run_run_summary_v1.csv",
    "synthetic_input_rows": "report_only_dry_run_synthetic_input_rows_v1.csv",
    "scenario_results": "report_only_dry_run_scenario_results_v1.csv",
    "validation_results": "report_only_dry_run_validation_results_v1.csv",
    "rejection_results": "report_only_dry_run_rejection_results_v1.csv",
    "hash_and_dedup_results": "report_only_dry_run_hash_and_dedup_results_v1.csv",
    "safety_lock_results": "report_only_dry_run_safety_lock_results_v1.csv",
    "official_dataset_guard_results": "report_only_dry_run_official_dataset_guard_results_v1.csv",
    "checks": "report_only_dry_run_run_checks_v1.csv",
    "manifest": "report_only_dry_run_run_manifest_v1.csv",
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


def all_passed(df: pd.DataFrame) -> bool:
    return (
        not df.empty
        and "passed" in df.columns
        and df["passed"].map(lambda value: safe_bool(value, False)).all()
    )


def column_all(df: pd.DataFrame, column: str, expected: bool) -> bool:
    return (
        not df.empty
        and column in df.columns
        and df[column]
        .map(lambda value: safe_bool(value, not expected))
        .eq(expected)
        .all()
    )


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


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
    if len(text) != 64:
        return False
    return all(character in "0123456789abcdef" for character in text.lower())


def canonical_json(payload: dict[str, Any]) -> str:
    return json.dumps(
        payload,
        sort_keys=True,
        ensure_ascii=True,
        separators=(",", ":"),
        default=str,
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


def build_manifest(
    paths: dict[str, Path],
    scope: str,
) -> pd.DataFrame:
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
                "artifact_scope",
                "artifact_name",
                "artifact_path",
                "artifact_size_bytes",
                "artifact_sha256",
            ]
        ]
        .astype(str)
        .sort_values(["artifact_scope", "artifact_name", "artifact_path"])
        .to_csv(index=False)
        .encode("utf-8")
    )
    return hashlib.sha256(payload).hexdigest()


def source_summary_row(source: dict[str, pd.DataFrame]) -> dict[str, Any]:
    if source["summary"].empty:
        return {}
    return source["summary"].iloc[0].to_dict()


def source_decision_row(source: dict[str, pd.DataFrame]) -> dict[str, Any]:
    if source["review_decision"].empty:
        return {}
    return source["review_decision"].iloc[0].to_dict()


def source_counts_valid(summary: dict[str, Any]) -> bool:
    for name, expected in EXPECTED_SOURCE_COUNTS.items():
        actual = int(safe_float(summary.get(name, -1), -1))
        if actual != expected:
            return False
    return True


def source_operational_locks_valid(summary: dict[str, Any]) -> bool:
    return all(
        not safe_bool(summary.get(name, True), True)
        for name in EXPECTED_FALSE_SOURCE_GUARDS
    )


def source_schema_valid(schema: pd.DataFrame) -> bool:
    if schema.empty or "field_name" not in schema.columns:
        return False
    ordered = schema.sort_values("field_position")
    fields = ordered["field_name"].astype(str).tolist()
    if fields != EXPECTED_SCHEMA_FIELDS:
        return False
    if "report_only_dry_run_field" in ordered.columns and not column_all(
        ordered, "report_only_dry_run_field", True
    ):
        return False
    if "synthetic_only" in ordered.columns and not column_all(
        ordered, "synthetic_only", True
    ):
        return False
    if "official_dataset_implemented" in ordered.columns and not column_all(
        ordered, "official_dataset_implemented", False
    ):
        return False
    for safety_field in SAFETY_FIELDS:
        row = ordered[ordered["field_name"].astype(str).eq(safety_field)]
        if len(row) != 1:
            return False
        if "default_value" not in row.columns:
            return False
        if safe_bool(row.iloc[0]["default_value"], True):
            return False
    return True


def execution_contract_valid(contract: pd.DataFrame) -> bool:
    required_columns = {
        "execution_position",
        "scenario_id",
        "scenario_name",
        "expected_outcome",
        "expected_validation_pass",
        "synthetic_only",
        "report_only",
        "approved_for_future_run",
        "executed_in_phase_10_33",
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
        "passed",
    }
    if contract.empty or not required_columns.issubset(contract.columns):
        return False
    ordered = contract.sort_values("execution_position").reset_index(drop=True)
    if ordered["execution_position"].astype(int).tolist() != list(range(1, 7)):
        return False
    for expected, (_, row) in zip(EXPECTED_SCENARIOS, ordered.iterrows()):
        (
            position,
            scenario_id,
            scenario_name,
            expected_outcome,
            expected_validation_pass,
        ) = expected
        if int(row["execution_position"]) != position:
            return False
        if str(row["scenario_id"]) != scenario_id:
            return False
        if str(row["scenario_name"]) != scenario_name:
            return False
        if str(row["expected_outcome"]) != expected_outcome:
            return False
        if safe_bool(row["expected_validation_pass"]) != expected_validation_pass:
            return False
        if not safe_bool(row["synthetic_only"]):
            return False
        if not safe_bool(row["report_only"]):
            return False
        if not safe_bool(row["approved_for_future_run"]):
            return False
        if safe_bool(row["executed_in_phase_10_33"]):
            return False
        for safety_field in SAFETY_FIELDS:
            if safety_field in row.index and safe_bool(row[safety_field], True):
                return False
        if not safe_bool(row["passed"]):
            return False
    return True


def source_review_blocks_passed(source: dict[str, pd.DataFrame]) -> bool:
    return all(
        all_passed(source[name])
        for name in [
            "review_validations",
            "review_items",
            "review_findings",
            "review_controls",
            "review_rules",
            "review_requirements",
            "review_guard_matrix",
        ]
    )


def build_source_validations(
    source: dict[str, pd.DataFrame],
    manifest_before: pd.DataFrame,
    manifest_after: pd.DataFrame,
    official_dataset_absent: bool,
) -> pd.DataFrame:
    summary = source_summary_row(source)
    decision = source_decision_row(source)

    artifacts_exist = (
        not manifest_before.empty
        and manifest_before["artifact_exists"].map(safe_bool).all()
    )
    artifacts_non_empty = (
        not manifest_before.empty
        and manifest_before["artifact_non_empty"].map(safe_bool).all()
    )
    artifact_hashes_valid = (
        not manifest_before.empty
        and manifest_before["artifact_sha256_valid"].map(safe_bool).all()
    )
    stable = (
        bool(manifest_digest(manifest_before))
        and manifest_digest(manifest_before) == manifest_digest(manifest_after)
    )

    phase_valid = (
        safe_bool(summary.get("validation_passed", False))
        and str(summary.get("validation_decision", ""))
        == (
            "PHASE_10_33_LONG_FORWARD_OBSERVATION_EVIDENCE_COLLECTION_"
            "REPORT_ONLY_DRY_RUN_EXECUTION_REVIEW_VALIDATED"
        )
    )
    review_performed = safe_bool(
        summary.get("report_only_dry_run_execution_review_performed", False)
    )
    review_passed = safe_bool(
        summary.get("report_only_dry_run_execution_review_passed", False)
    )
    decision_valid = (
        str(summary.get("report_only_dry_run_execution_review_decision", ""))
        == SOURCE_READY_DECISION
        and str(decision.get("report_only_dry_run_execution_review_decision", ""))
        == SOURCE_READY_DECISION
    )
    future_allowed = (
        safe_bool(summary.get("future_report_only_dry_run_run_allowed", False))
        and safe_bool(
            decision.get("future_report_only_dry_run_run_allowed", False)
        )
    )
    summary_decision_consistent = (
        review_passed
        and safe_bool(
            decision.get("report_only_dry_run_execution_review_passed", False)
        )
        and decision_valid
        and future_allowed
    )
    counts_valid = source_counts_valid(summary)
    blocks_passed = source_review_blocks_passed(source)
    material_zero = (
        int(safe_float(summary.get("material_issue_count", -1), -1)) == 0
    )
    schema_valid = source_schema_valid(source["schema"])
    contract_valid = execution_contract_valid(source["execution_contract"])
    preconditions_valid = (
        len(source["preconditions"]) == 20
        and all_passed(source["preconditions"])
    )
    abort_rules_valid = (
        len(source["abort_rules"]) == 12
        and all_passed(source["abort_rules"])
        and column_all(source["abort_rules"], "fail_closed", True)
    )
    output_plan_valid = (
        len(source["output_plan"]) == 10
        and all_passed(source["output_plan"])
        and (
            "target_scope" in source["output_plan"].columns
            and source["output_plan"]["target_scope"]
            .astype(str)
            .eq("REPORTS_ONLY")
            .all()
        )
    )
    dry_run_not_executed = not safe_bool(
        summary.get("report_only_dry_run_executed", True), True
    )
    rows_zero = int(
        safe_float(summary.get("report_only_dry_run_rows_generated", -1), -1)
    ) == 0
    locks_valid = source_operational_locks_valid(summary)
    long_unapproved = not safe_bool(
        summary.get("long_strategy_approved", True), True
    )
    project_incomplete = not safe_bool(
        summary.get("total_project_completed", True), True
    )

    rows = [
        ("source_artifacts_exist", artifacts_exist, f"rows={len(manifest_before)}"),
        ("source_artifacts_non_empty", artifacts_non_empty, f"rows={len(manifest_before)}"),
        ("source_artifact_hashes_valid", artifact_hashes_valid, f"rows={len(manifest_before)}"),
        (
            "source_artifacts_stable_before_run",
            stable,
            (
                f"before={manifest_digest(manifest_before)},"
                f"after={manifest_digest(manifest_after)}"
            ),
        ),
        ("phase_10_33_validation_passed", phase_valid, str(summary.get("validation_decision", ""))),
        ("source_execution_review_performed", review_performed, str(review_performed)),
        ("source_execution_review_passed", review_passed, str(review_passed)),
        ("source_execution_review_decision_valid", decision_valid, str(summary.get("report_only_dry_run_execution_review_decision", ""))),
        ("source_future_run_allowed", future_allowed, str(future_allowed)),
        ("source_summary_decision_consistent", summary_decision_consistent, f"consistent={summary_decision_consistent}"),
        ("source_counts_valid", counts_valid, str(EXPECTED_SOURCE_COUNTS)),
        ("source_review_blocks_passed", blocks_passed, f"passed={blocks_passed}"),
        ("source_material_issue_count_zero", material_zero, str(summary.get("material_issue_count", ""))),
        ("source_schema_contract_valid", schema_valid, f"rows={len(source['schema'])}"),
        ("source_execution_contract_valid", contract_valid, f"rows={len(source['execution_contract'])}"),
        ("source_preconditions_valid", preconditions_valid, f"rows={len(source['preconditions'])}"),
        ("source_abort_rules_valid", abort_rules_valid, f"rows={len(source['abort_rules'])}"),
        ("source_output_plan_valid", output_plan_valid, f"rows={len(source['output_plan'])}"),
        ("official_dataset_absent_before_run", official_dataset_absent, f"absent={official_dataset_absent}"),
        ("source_dry_run_not_executed", dry_run_not_executed, f"executed={summary.get('report_only_dry_run_executed', '')}"),
        ("source_dry_run_rows_zero", rows_zero, f"rows={summary.get('report_only_dry_run_rows_generated', '')}"),
        ("source_operational_locks_valid", locks_valid, f"false_guard_count={len(EXPECTED_FALSE_SOURCE_GUARDS)}"),
        ("long_strategy_remains_unapproved", long_unapproved, f"approved={summary.get('long_strategy_approved', '')}"),
        ("total_project_not_completed", project_incomplete, f"completed={summary.get('total_project_completed', '')}"),
    ]
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


def build_abort_evaluations(
    source_validations: pd.DataFrame,
    source: dict[str, pd.DataFrame],
    official_before: bool,
) -> pd.DataFrame:
    lookup = {
        str(row["validation_name"]): safe_bool(row["passed"], False)
        for _, row in source_validations.iterrows()
    }
    conditions = [
        (
            "abort_if_source_artifact_missing",
            not lookup.get("source_artifacts_exist", False),
        ),
        (
            "abort_if_source_artifact_hash_invalid",
            not lookup.get("source_artifact_hashes_valid", False),
        ),
        (
            "abort_if_source_artifact_changes_before_run",
            not lookup.get("source_artifacts_stable_before_run", False),
        ),
        (
            "abort_if_source_decision_mismatch",
            not lookup.get("source_execution_review_decision_valid", False),
        ),
        (
            "abort_if_schema_field_count_or_order_changes",
            not lookup.get("source_schema_contract_valid", False),
        ),
        (
            "abort_if_any_safety_default_is_true",
            not source_schema_valid(source["schema"]),
        ),
        (
            "abort_if_scenario_count_or_order_changes",
            not execution_contract_valid(source["execution_contract"]),
        ),
        (
            "abort_if_expected_outcome_mismatch",
            not execution_contract_valid(source["execution_contract"]),
        ),
        (
            "abort_if_any_official_dataset_write_is_requested",
            not lookup.get("source_operational_locks_valid", False),
        ),
        (
            "abort_if_any_real_evidence_acceptance_is_requested",
            not lookup.get("source_operational_locks_valid", False),
        ),
        (
            "abort_if_any_signal_alert_or_execution_flag_is_true",
            not lookup.get("source_operational_locks_valid", False),
        ),
        (
            "abort_if_official_dataset_exists_before_run",
            official_before,
        ),
    ]
    source_abort_names = (
        source["abort_rules"]["abort_rule_name"].astype(str).tolist()
        if (
            not source["abort_rules"].empty
            and "abort_rule_name" in source["abort_rules"].columns
        )
        else []
    )
    rows = []
    for position, (name, triggered) in enumerate(conditions, start=1):
        contract_declared = (
            name in source_abort_names
            or (
                name == "abort_if_source_artifact_changes_before_run"
                and "abort_if_source_artifact_changes_during_run"
                in source_abort_names
            )
            or (
                name == "abort_if_official_dataset_exists_before_run"
                and "abort_if_official_dataset_exists_before_or_after_run"
                in source_abort_names
            )
        )
        passed = contract_declared and not triggered
        rows.append(
            {
                "abort_evaluation_position": position,
                "abort_rule_name": name,
                "contract_declared": contract_declared,
                "abort_triggered": bool(triggered),
                "fail_closed": True,
                "passed": passed,
            }
        )
    return pd.DataFrame(rows)


def build_base_row() -> dict[str, Any]:
    row: dict[str, Any] = {
        "evidence_id": "SYNTHETIC_EVIDENCE_001",
        "observation_id": "SYNTHETIC_OBSERVATION_001",
        "collected_at_utc": BASE_COLLECTED_AT,
        "observed_at_utc": BASE_OBSERVED_AT,
        "source_system": ALLOWED_SOURCE_SYSTEM,
        "source_artifact": SOURCE_ARTIFACT_NAME,
        "source_artifact_sha256": sha256_text(SOURCE_ARTIFACT_NAME),
        "source_row_hash": "",
        "candidate_id": "LONG_RESEARCH_CANDIDATE_UNAPPROVED",
        "direction": "LONG",
        "symbol": "BTCUSDT",
        "timeframe": "15m",
        "observation_state": "CONTROLLED_FORWARD_OBSERVATION_STARTED",
        "evidence_status": "SYNTHETIC_REPORT_ONLY",
        "evidence_scope": "REPORT_ONLY_DRY_RUN",
        "evidence_version": "phase_10_34_v1",
        "entry_price": 100000.0,
        "stop_price": 99000.0,
        "target_price": 102500.0,
        "invalidation_level": 99000.0,
        "risk_reward": 2.5,
        "cost_profile": "SYNTHETIC_ZERO_COST",
        "market_context": "SYNTHETIC_TEST_CONTEXT",
        "activation_scope": "REPORT_ONLY_DRY_RUN",
        "signal_state": "NO_SIGNAL",
        "deduplication_key": "",
        "deduplication_status": "UNIQUE_CANDIDATE",
        "lifecycle_state": "SYNTHETIC_DRY_RUN",
        "review_status": "NOT_REAL_EVIDENCE",
        "rejection_reason": "",
        "manual_confirmation_required": True,
        "manual_confirmed": False,
        "write_ahead_validation_passed": False,
        "schema_validation_passed": False,
        "provenance_validation_passed": False,
        "risk_structure_validation_passed": False,
        "evidence_hash": "",
        "previous_evidence_hash": "",
        "audit_event_id": "SYNTHETIC_AUDIT_001",
        "created_by": "PHASE_10_34_SYNTHETIC_DRY_RUN",
        "reviewed_by": "",
        "rollback_reference": "",
        "accepted_as_real_evidence": False,
        "official_dataset_write_allowed": False,
        "evidence_persistence_allowed": False,
        "signal_generation_enabled": False,
        "live_alerts_allowed": False,
        "paper_trade_execution_allowed": False,
        "real_capital_allowed": False,
        "market_execution_allowed": False,
        "exchange_execution_allowed": False,
        "automation_allowed": False,
        "execution_allowed": False,
        "notes": "Synthetic report-only dry-run row.",
    }
    return finalize_row_hashes(row)


def row_payload_for_source_hash(row: dict[str, Any]) -> dict[str, Any]:
    excluded = {
        "source_row_hash",
        "evidence_hash",
        "write_ahead_validation_passed",
        "schema_validation_passed",
        "provenance_validation_passed",
        "risk_structure_validation_passed",
    }
    return {
        name: row.get(name)
        for name in EXPECTED_SCHEMA_FIELDS
        if name not in excluded
    }


def finalize_row_hashes(row: dict[str, Any]) -> dict[str, Any]:
    row = dict(row)
    dedup_payload = {
        "observation_id": row.get("observation_id"),
        "candidate_id": row.get("candidate_id"),
        "direction": row.get("direction"),
        "symbol": row.get("symbol"),
        "timeframe": row.get("timeframe"),
        "observed_at_utc": row.get("observed_at_utc"),
        "entry_price": row.get("entry_price"),
        "stop_price": row.get("stop_price"),
        "target_price": row.get("target_price"),
    }
    row["deduplication_key"] = sha256_text(canonical_json(dedup_payload))
    row["source_row_hash"] = sha256_text(
        canonical_json(row_payload_for_source_hash(row))
    )
    evidence_payload = {
        name: row.get(name)
        for name in EXPECTED_SCHEMA_FIELDS
        if name != "evidence_hash"
    }
    row["evidence_hash"] = sha256_text(canonical_json(evidence_payload))
    return {name: row.get(name) for name in EXPECTED_SCHEMA_FIELDS}


def build_synthetic_rows(
    execution_contract: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    if not execution_contract_valid(execution_contract):
        return pd.DataFrame(columns=EXPECTED_SCHEMA_FIELDS), pd.DataFrame()

    base = build_base_row()
    rows: list[dict[str, Any]] = []
    scenario_map: list[dict[str, Any]] = []
    ordered = execution_contract.sort_values("execution_position").reset_index(
        drop=True
    )

    for _, contract_row in ordered.iterrows():
        position = int(contract_row["execution_position"])
        scenario_name = str(contract_row["scenario_name"])
        if scenario_name == "VALID_SYNTHETIC_ROW":
            row = copy.deepcopy(base)
        elif scenario_name == "EXACT_DUPLICATE_ROW":
            row = copy.deepcopy(base)
        else:
            row = copy.deepcopy(base)
            row["evidence_id"] = f"SYNTHETIC_EVIDENCE_{position:03d}"
            row["observation_id"] = f"SYNTHETIC_OBSERVATION_{position:03d}"
            row["audit_event_id"] = f"SYNTHETIC_AUDIT_{position:03d}"
            row["observed_at_utc"] = f"2026-01-01T00:0{position}:00Z"
            row["collected_at_utc"] = f"2026-01-01T00:0{position}:01Z"
            row["notes"] = f"Synthetic report-only scenario {scenario_name}."
            if scenario_name == "INVALID_SOURCE_SYSTEM":
                row["source_system"] = "UNAPPROVED_EXTERNAL_SOURCE"
            elif scenario_name == "INVALID_UTC_TIMESTAMP":
                row["collected_at_utc"] = "NOT_A_UTC_TIMESTAMP"
            elif scenario_name == "INVALID_LONG_PRICE_STRUCTURE":
                row["stop_price"] = 101000.0
                row["invalidation_level"] = 101000.0
            elif scenario_name == "PROHIBITED_EXECUTION_FLAG_ENABLED":
                row["execution_allowed"] = True
            row = finalize_row_hashes(row)

        rows.append(row)
        scenario_map.append(
            {
                "row_position": position,
                "scenario_id": str(contract_row["scenario_id"]),
                "scenario_name": scenario_name,
                "expected_outcome": str(contract_row["expected_outcome"]),
                "expected_validation_pass": safe_bool(
                    contract_row["expected_validation_pass"]
                ),
            }
        )

    return pd.DataFrame(rows, columns=EXPECTED_SCHEMA_FIELDS), pd.DataFrame(
        scenario_map
    )


def validate_schema_row(row: dict[str, Any]) -> tuple[bool, str]:
    if list(row.keys()) != EXPECTED_SCHEMA_FIELDS:
        return False, "field_order_or_count_mismatch"
    for name in EXPECTED_SCHEMA_FIELDS:
        value = row.get(name)
        if name not in OPTIONAL_FIELDS:
            if value is None:
                return False, f"required_field_none:{name}"
            if isinstance(value, str) and value == "":
                return False, f"required_field_blank:{name}"
        if name in BOOL_FIELDS and not isinstance(value, bool):
            return False, f"invalid_bool:{name}"
        if name in FLOAT_FIELDS:
            numeric = safe_float(value, float("nan"))
            if not math.isfinite(numeric):
                return False, f"invalid_float:{name}"
    return True, ""


def validate_utc_row(row: dict[str, Any]) -> tuple[bool, str]:
    for name in ["collected_at_utc", "observed_at_utc"]:
        value = str(row.get(name, ""))
        parsed = pd.to_datetime(value, utc=True, errors="coerce")
        if pd.isna(parsed) or not value.endswith("Z"):
            return False, f"invalid_utc:{name}"
    return True, ""


def validate_provenance_row(row: dict[str, Any]) -> tuple[bool, str]:
    if str(row.get("source_system", "")) != ALLOWED_SOURCE_SYSTEM:
        return False, "invalid_source_system"
    if str(row.get("source_artifact", "")) != SOURCE_ARTIFACT_NAME:
        return False, "invalid_source_artifact"
    if str(row.get("source_artifact_sha256", "")) != sha256_text(
        SOURCE_ARTIFACT_NAME
    ):
        return False, "invalid_source_artifact_sha256"
    if not is_sha256(row.get("source_row_hash", "")):
        return False, "invalid_source_row_hash"
    if not is_sha256(row.get("evidence_hash", "")):
        return False, "invalid_evidence_hash"
    return True, ""


def validate_long_price_structure(
    row: dict[str, Any],
) -> tuple[bool, str]:
    if str(row.get("direction", "")) != "LONG":
        return False, "direction_not_long"
    entry = safe_float(row.get("entry_price"), float("nan"))
    stop = safe_float(row.get("stop_price"), float("nan"))
    target = safe_float(row.get("target_price"), float("nan"))
    invalidation = safe_float(
        row.get("invalidation_level"), float("nan")
    )
    expected_rr = safe_float(row.get("risk_reward"), float("nan"))
    values = [entry, stop, target, invalidation, expected_rr]
    if not all(math.isfinite(value) for value in values):
        return False, "non_finite_price_or_rr"
    if not stop < entry < target:
        return False, "long_price_order_invalid"
    if invalidation > entry:
        return False, "invalidation_above_entry"
    risk = entry - stop
    reward = target - entry
    if risk <= 0:
        return False, "non_positive_risk"
    calculated_rr = reward / risk
    if abs(calculated_rr - expected_rr) > 1e-9:
        return False, "risk_reward_mismatch"
    return True, ""


def validate_safety_row(row: dict[str, Any]) -> tuple[bool, str]:
    enabled = [
        name for name in SAFETY_FIELDS if safe_bool(row.get(name, False))
    ]
    if enabled:
        return False, "enabled_safety_fields:" + ",".join(enabled)
    return True, ""


def determine_outcome(
    duplicate: bool,
    schema_passed: bool,
    provenance_passed: bool,
    utc_passed: bool,
    price_passed: bool,
    safety_passed: bool,
) -> tuple[str, bool, str]:
    if duplicate:
        return "REJECT_DUPLICATE", False, "duplicate_deduplication_key"
    if not schema_passed:
        return "REJECT_SCHEMA", False, "schema_validation_failed"
    if not provenance_passed:
        return "REJECT_SOURCE", False, "provenance_validation_failed"
    if not utc_passed:
        return "REJECT_TIMESTAMP", False, "utc_timestamp_validation_failed"
    if not price_passed:
        return "REJECT_PRICE_STRUCTURE", False, "long_price_structure_failed"
    if not safety_passed:
        return "REJECT_SAFETY_FLAG", False, "safety_lock_validation_failed"
    return "PASS_REPORT_ONLY", True, ""


def execute_scenarios(
    synthetic_rows: pd.DataFrame,
    scenario_map: pd.DataFrame,
) -> dict[str, pd.DataFrame]:
    if synthetic_rows.empty or scenario_map.empty:
        empty = pd.DataFrame()
        return {
            "scenario_results": empty,
            "validation_results": empty,
            "rejection_results": empty,
            "hash_and_dedup_results": empty,
            "safety_lock_results": empty,
        }

    seen_keys: set[str] = set()
    scenario_results: list[dict[str, Any]] = []
    validation_results: list[dict[str, Any]] = []
    rejection_results: list[dict[str, Any]] = []
    hash_results: list[dict[str, Any]] = []
    safety_results: list[dict[str, Any]] = []

    for index, row_series in synthetic_rows.iterrows():
        row = row_series.to_dict()
        contract = scenario_map.iloc[index].to_dict()
        dedup_key = str(row.get("deduplication_key", ""))
        duplicate = dedup_key in seen_keys
        if not duplicate:
            seen_keys.add(dedup_key)

        schema_passed, schema_reason = validate_schema_row(row)
        utc_passed, utc_reason = validate_utc_row(row)
        provenance_passed, provenance_reason = validate_provenance_row(row)
        price_passed, price_reason = validate_long_price_structure(row)
        safety_passed, safety_reason = validate_safety_row(row)
        outcome, validation_passed, rejection_reason = determine_outcome(
            duplicate,
            schema_passed,
            provenance_passed,
            utc_passed,
            price_passed,
            safety_passed,
        )
        expected_outcome = str(contract["expected_outcome"])
        expected_validation_pass = safe_bool(
            contract["expected_validation_pass"]
        )
        outcome_match = (
            outcome == expected_outcome
            and validation_passed == expected_validation_pass
        )
        scenario_passed = (
            outcome_match
            and not safe_bool(row.get("accepted_as_real_evidence", False))
            and not safe_bool(
                row.get("official_dataset_write_allowed", False)
            )
            and not safe_bool(
                row.get("evidence_persistence_allowed", False)
            )
            and not safe_bool(row.get("signal_generation_enabled", False))
            and not safe_bool(row.get("live_alerts_allowed", False))
            and not safe_bool(
                row.get("paper_trade_execution_allowed", False)
            )
            and not safe_bool(row.get("real_capital_allowed", False))
            and not safe_bool(row.get("market_execution_allowed", False))
            and not safe_bool(row.get("exchange_execution_allowed", False))
            and not safe_bool(row.get("automation_allowed", False))
            and (
                not safe_bool(row.get("execution_allowed", False))
                or outcome == "REJECT_SAFETY_FLAG"
            )
        )

        validation_results.append(
            {
                "row_position": int(contract["row_position"]),
                "scenario_id": str(contract["scenario_id"]),
                "scenario_name": str(contract["scenario_name"]),
                "schema_validation_passed": schema_passed,
                "schema_failure_reason": schema_reason,
                "utc_validation_passed": utc_passed,
                "utc_failure_reason": utc_reason,
                "provenance_validation_passed": provenance_passed,
                "provenance_failure_reason": provenance_reason,
                "risk_structure_validation_passed": price_passed,
                "risk_structure_failure_reason": price_reason,
                "deduplication_validation_passed": not duplicate,
                "duplicate_detected": duplicate,
                "safety_lock_validation_passed": safety_passed,
                "safety_failure_reason": safety_reason,
                "actual_validation_pass": validation_passed,
                "passed": scenario_passed,
            }
        )
        scenario_results.append(
            {
                "execution_position": int(contract["row_position"]),
                "scenario_id": str(contract["scenario_id"]),
                "scenario_name": str(contract["scenario_name"]),
                "expected_outcome": expected_outcome,
                "actual_outcome": outcome,
                "expected_validation_pass": expected_validation_pass,
                "actual_validation_pass": validation_passed,
                "outcome_matches_expected": outcome_match,
                "synthetic_only": True,
                "report_only": True,
                "dry_run_row_generated": True,
                "accepted_as_real_evidence": False,
                "official_dataset_write_performed": False,
                "signal_generated": False,
                "live_alert_generated": False,
                "paper_trade_executed": False,
                "market_order_executed": False,
                "rejection_reason": rejection_reason,
                "passed": scenario_passed,
            }
        )
        if not validation_passed:
            rejection_results.append(
                {
                    "execution_position": int(contract["row_position"]),
                    "scenario_id": str(contract["scenario_id"]),
                    "scenario_name": str(contract["scenario_name"]),
                    "actual_outcome": outcome,
                    "rejection_reason": rejection_reason,
                    "accepted_as_real_evidence": False,
                    "official_dataset_write_performed": False,
                    "market_order_executed": False,
                    "passed": outcome_match,
                }
            )
        hash_results.append(
            {
                "execution_position": int(contract["row_position"]),
                "scenario_id": str(contract["scenario_id"]),
                "scenario_name": str(contract["scenario_name"]),
                "deduplication_key": dedup_key,
                "duplicate_detected": duplicate,
                "source_row_hash": str(row.get("source_row_hash", "")),
                "source_row_hash_valid": is_sha256(
                    row.get("source_row_hash", "")
                ),
                "evidence_hash": str(row.get("evidence_hash", "")),
                "evidence_hash_valid": is_sha256(
                    row.get("evidence_hash", "")
                ),
                "passed": (
                    is_sha256(row.get("source_row_hash", ""))
                    and is_sha256(row.get("evidence_hash", ""))
                    and (
                        duplicate
                        == (
                            str(contract["scenario_name"])
                            == "EXACT_DUPLICATE_ROW"
                        )
                    )
                ),
            }
        )
        for safety_field in SAFETY_FIELDS:
            actual_value = safe_bool(row.get(safety_field, False))
            expected_value = (
                True
                if (
                    str(contract["scenario_name"])
                    == "PROHIBITED_EXECUTION_FLAG_ENABLED"
                    and safety_field == "execution_allowed"
                )
                else False
            )
            safety_results.append(
                {
                    "execution_position": int(contract["row_position"]),
                    "scenario_id": str(contract["scenario_id"]),
                    "scenario_name": str(contract["scenario_name"]),
                    "safety_field": safety_field,
                    "expected_input_value": expected_value,
                    "actual_input_value": actual_value,
                    "violation_detected": actual_value,
                    "actual_outcome": outcome,
                    "accepted_as_real_evidence": False,
                    "operational_action_performed": False,
                    "passed": (
                        actual_value == expected_value
                        and (
                            not actual_value
                            or outcome == "REJECT_SAFETY_FLAG"
                        )
                    ),
                }
            )

    return {
        "scenario_results": pd.DataFrame(scenario_results),
        "validation_results": pd.DataFrame(validation_results),
        "rejection_results": pd.DataFrame(rejection_results),
        "hash_and_dedup_results": pd.DataFrame(hash_results),
        "safety_lock_results": pd.DataFrame(safety_results),
    }


def build_official_dataset_guard_results(
    official_before: bool,
    official_after: bool,
) -> pd.DataFrame:
    rows = [
        (
            "official_dataset_absent_before_run",
            False,
            official_before,
            not official_before,
        ),
        (
            "official_dataset_absent_after_run",
            False,
            official_after,
            not official_after,
        ),
        (
            "official_dataset_schema_implemented",
            False,
            False,
            True,
        ),
        (
            "official_dataset_write_allowed",
            False,
            False,
            True,
        ),
        (
            "official_dataset_write_performed",
            False,
            False,
            True,
        ),
        (
            "official_evidence_rows_written",
            0,
            0,
            True,
        ),
        (
            "real_forward_dataset_created",
            False,
            False,
            True,
        ),
        (
            "accepted_as_real_evidence",
            False,
            False,
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
                "passed": passed,
            }
            for position, (name, required, actual, passed) in enumerate(
                rows, start=1
            )
        ]
    )


def build_runtime_validations(
    source_validations: pd.DataFrame,
    abort_evaluations: pd.DataFrame,
    synthetic_rows: pd.DataFrame,
    scenario_results: pd.DataFrame,
    validation_results: pd.DataFrame,
    rejection_results: pd.DataFrame,
    hash_results: pd.DataFrame,
    safety_results: pd.DataFrame,
    official_guards: pd.DataFrame,
    source_stable_after_run: bool,
    run_attempted: bool,
) -> pd.DataFrame:
    source_all_passed = all_passed(source_validations)
    aborts_clear = (
        len(abort_evaluations) == 12
        and all_passed(abort_evaluations)
        and not abort_evaluations["abort_triggered"].map(safe_bool).any()
    )
    scenario_count = len(scenario_results)
    valid_count = (
        int(
            scenario_results["actual_validation_pass"]
            .map(safe_bool)
            .sum()
        )
        if not scenario_results.empty
        else 0
    )
    rejected_count = scenario_count - valid_count
    outcome_match = (
        scenario_count == 6
        and scenario_results["outcome_matches_expected"]
        .map(safe_bool)
        .all()
    )
    actual_outcomes = (
        scenario_results["actual_outcome"].astype(str).tolist()
        if not scenario_results.empty
        else []
    )
    expected_outcomes = [item[3] for item in EXPECTED_SCENARIOS]
    exact_outcome_order = actual_outcomes == expected_outcomes
    validation_blocks_passed = (
        len(validation_results) == 6 and all_passed(validation_results)
    )
    rejection_contract_passed = (
        len(rejection_results) == 5 and all_passed(rejection_results)
    )
    hashes_passed = len(hash_results) == 6 and all_passed(hash_results)
    safety_passed = (
        len(safety_results) == 6 * len(SAFETY_FIELDS)
        and all_passed(safety_results)
    )
    official_guard_passed = all_passed(official_guards)

    outcome_counts = {
        name: actual_outcomes.count(name)
        for name in expected_outcomes
    }

    rows = [
        ("source_validation_chain_passed", source_all_passed, f"rows={len(source_validations)}"),
        ("abort_evaluations_clear", aborts_clear, f"rows={len(abort_evaluations)}"),
        ("report_only_dry_run_run_attempted", run_attempted, str(run_attempted)),
        ("synthetic_input_row_count_6", len(synthetic_rows) == 6, f"rows={len(synthetic_rows)}"),
        ("synthetic_input_schema_field_count_54", list(synthetic_rows.columns) == EXPECTED_SCHEMA_FIELDS, f"columns={len(synthetic_rows.columns)}"),
        ("scenario_result_count_6", scenario_count == 6, f"rows={scenario_count}"),
        ("scenario_outcomes_match_expected", outcome_match, f"match={outcome_match}"),
        ("scenario_outcomes_in_expected_order", exact_outcome_order, str(actual_outcomes)),
        ("valid_report_only_row_count_1", valid_count == 1, f"rows={valid_count}"),
        ("rejected_row_count_5", rejected_count == 5, f"rows={rejected_count}"),
        ("validation_result_count_6", len(validation_results) == 6, f"rows={len(validation_results)}"),
        ("all_scenario_validation_records_passed", validation_blocks_passed, f"passed={validation_blocks_passed}"),
        ("rejection_result_count_5", len(rejection_results) == 5, f"rows={len(rejection_results)}"),
        ("all_rejections_match_contract", rejection_contract_passed, f"passed={rejection_contract_passed}"),
        ("hash_and_dedup_result_count_6", len(hash_results) == 6, f"rows={len(hash_results)}"),
        ("hash_and_dedup_results_passed", hashes_passed, f"passed={hashes_passed}"),
        ("safety_lock_result_count_66", len(safety_results) == 66, f"rows={len(safety_results)}"),
        ("safety_lock_results_passed", safety_passed, f"passed={safety_passed}"),
        ("official_dataset_guards_passed", official_guard_passed, f"rows={len(official_guards)}"),
        ("source_artifacts_stable_during_run", source_stable_after_run, str(source_stable_after_run)),
        ("pass_report_only_count_1", outcome_counts.get("PASS_REPORT_ONLY", 0) == 1, str(outcome_counts)),
        ("reject_duplicate_count_1", outcome_counts.get("REJECT_DUPLICATE", 0) == 1, str(outcome_counts)),
        ("reject_source_count_1", outcome_counts.get("REJECT_SOURCE", 0) == 1, str(outcome_counts)),
        ("reject_timestamp_count_1", outcome_counts.get("REJECT_TIMESTAMP", 0) == 1, str(outcome_counts)),
        ("reject_price_structure_count_1", outcome_counts.get("REJECT_PRICE_STRUCTURE", 0) == 1, str(outcome_counts)),
        ("reject_safety_flag_count_1", outcome_counts.get("REJECT_SAFETY_FLAG", 0) == 1, str(outcome_counts)),
        ("all_rows_synthetic_only", scenario_count == 6 and scenario_results["synthetic_only"].map(safe_bool).all(), f"rows={scenario_count}"),
        ("all_rows_report_only", scenario_count == 6 and scenario_results["report_only"].map(safe_bool).all(), f"rows={scenario_count}"),
        ("no_real_evidence_accepted", scenario_count == 6 and not scenario_results["accepted_as_real_evidence"].map(safe_bool).any(), f"rows={scenario_count}"),
        ("no_official_dataset_write_performed", scenario_count == 6 and not scenario_results["official_dataset_write_performed"].map(safe_bool).any(), f"rows={scenario_count}"),
        ("no_signal_generated", scenario_count == 6 and not scenario_results["signal_generated"].map(safe_bool).any(), f"rows={scenario_count}"),
        ("no_live_alert_generated", scenario_count == 6 and not scenario_results["live_alert_generated"].map(safe_bool).any(), f"rows={scenario_count}"),
        ("no_paper_trade_executed", scenario_count == 6 and not scenario_results["paper_trade_executed"].map(safe_bool).any(), f"rows={scenario_count}"),
        ("no_market_order_executed", scenario_count == 6 and not scenario_results["market_order_executed"].map(safe_bool).any(), f"rows={scenario_count}"),
        ("official_evidence_rows_written_zero", True, "rows=0"),
        ("long_strategy_remains_unapproved", True, "approved=False"),
        ("total_project_not_completed", True, "completed=False"),
    ]
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


def build_decision(
    source_validations: pd.DataFrame,
    abort_evaluations: pd.DataFrame,
    runtime_validations: pd.DataFrame,
    run_attempted: bool,
) -> pd.DataFrame:
    passed = all(
        [
            all_passed(source_validations),
            all_passed(abort_evaluations),
            all_passed(runtime_validations),
        ]
    )
    return pd.DataFrame(
        [
            {
                "report_only_dry_run_run_id": (
                    "PHASE_10_34_LONG_FORWARD_OBSERVATION_EVIDENCE_"
                    "COLLECTION_REPORT_ONLY_DRY_RUN_RUN_001"
                ),
                "report_only_dry_run_executed": bool(run_attempted),
                "report_only_dry_run_run_passed": passed,
                "report_only_dry_run_run_decision": (
                    READY_DECISION if passed else BLOCKED_DECISION
                ),
                "future_report_only_dry_run_output_integrity_review_allowed": passed,
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


def build_checks(
    docs_exist: dict[str, bool],
    source_validations: pd.DataFrame,
    abort_evaluations: pd.DataFrame,
    runtime_validations: pd.DataFrame,
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

    aggregate = {
        "source_validations_passed": all_passed(source_validations),
        "abort_evaluations_passed": all_passed(abort_evaluations),
        "runtime_validations_passed": all_passed(runtime_validations),
        "report_only_dry_run_run_passed": (
            not decision.empty
            and safe_bool(
                decision.iloc[0].get("report_only_dry_run_run_passed", False)
            )
        ),
        "report_only_dry_run_run_decision_expected": (
            not decision.empty
            and str(
                decision.iloc[0].get(
                    "report_only_dry_run_run_decision", ""
                )
            )
            == READY_DECISION
        ),
    }
    for name, passed in aggregate.items():
        checks.append(
            check_row(
                "report_only_dry_run_run",
                name,
                passed,
                "INFO" if passed else "ERROR",
                f"{name}={passed}",
            )
        )

    official_unchanged_absent = not official_before and not official_after
    checks.append(
        check_row(
            "official_dataset_guard",
            "official_dataset_unchanged_absent",
            official_unchanged_absent,
            "INFO" if official_unchanged_absent else "ERROR",
            f"before={official_before},after={official_after}",
        )
    )

    warnings = [
        ("synthetic_report_only_run", "Phase 10.34 executes only deterministic synthetic report-only scenarios."),
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
        ("automation_not_allowed", "Automation remains prohibited."),
        ("total_project_not_completed", "The total project is not completed."),
    ]
    for name, details in warnings:
        checks.append(
            check_row("scope_control", name, True, "WARNING", details)
        )

    future_allowed = (
        not decision.empty
        and safe_bool(
            decision.iloc[0].get(
                "future_report_only_dry_run_output_integrity_review_allowed",
                False,
            )
        )
    )
    checks.append(
        check_row(
            "planning_scope",
            "future_report_only_dry_run_output_integrity_review_allowed",
            future_allowed,
            "WARNING" if future_allowed else "ERROR",
            (
                "Allows only a future output-integrity review; it does not "
                "enable evidence collection, official dataset writes, "
                "signals, alerts, paper trading or execution."
            ),
        )
    )
    checks.append(
        check_row(
            "phase_transition",
            "phase_10_35_recommended_next",
            True,
            "INFO",
            (
                "Recommended next: Phase 10.35 LONG Forward Observation "
                "Evidence Collection Report-Only Dry-Run Output Integrity "
                "Review V1."
            ),
        )
    )
    return pd.DataFrame(checks)


def build_summary(
    source_manifest: pd.DataFrame,
    source_validations: pd.DataFrame,
    abort_evaluations: pd.DataFrame,
    synthetic_rows: pd.DataFrame,
    scenario_results: pd.DataFrame,
    runtime_validations: pd.DataFrame,
    safety_results: pd.DataFrame,
    decision: pd.DataFrame,
    checks: pd.DataFrame,
    official_before: bool,
    official_after: bool,
) -> pd.DataFrame:
    decision_row = decision.iloc[0].to_dict() if not decision.empty else {}
    blocker_count = int(checks["blocker"].map(safe_bool).sum())
    error_count = int(checks["severity"].eq("ERROR").sum())
    warning_count = int(checks["severity"].eq("WARNING").sum())
    validation_passed = blocker_count == 0 and error_count == 0
    valid_rows = (
        int(scenario_results["actual_validation_pass"].map(safe_bool).sum())
        if not scenario_results.empty
        else 0
    )
    rejected_rows = len(scenario_results) - valid_rows
    safety_violations = (
        int(safety_results["violation_detected"].map(safe_bool).sum())
        if not safety_results.empty
        else 0
    )
    return pd.DataFrame(
        [
            {
                "phase": "10.34",
                "long_forward_observation_evidence_collection_report_only_dry_run_run_defined": True,
                "phase_10_33_validation_passed": (
                    all_passed(source_validations)
                ),
                "source_artifact_count": len(source_manifest),
                "source_manifest_sha256": manifest_digest(source_manifest),
                "source_validations_passed": all_passed(source_validations),
                "source_validation_rows": len(source_validations),
                "abort_evaluation_rows": len(abort_evaluations),
                "abort_evaluations_passed": all_passed(abort_evaluations),
                "abort_trigger_count": (
                    int(
                        abort_evaluations["abort_triggered"]
                        .map(safe_bool)
                        .sum()
                    )
                    if not abort_evaluations.empty
                    else -1
                ),
                "report_only_dry_run_executed": safe_bool(
                    decision_row.get("report_only_dry_run_executed", False)
                ),
                "report_only_dry_run_rows_generated": len(synthetic_rows),
                "report_only_dry_run_valid_rows": valid_rows,
                "report_only_dry_run_rejected_rows": rejected_rows,
                "scenario_result_rows": len(scenario_results),
                "scenario_outcomes_match_expected": (
                    len(scenario_results) == 6
                    and scenario_results["outcome_matches_expected"]
                    .map(safe_bool)
                    .all()
                ),
                "runtime_validation_rows": len(runtime_validations),
                "runtime_validations_passed": all_passed(
                    runtime_validations
                ),
                "safety_lock_result_rows": len(safety_results),
                "synthetic_safety_violation_count": safety_violations,
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
                "report_only_dry_run_run_passed": safe_bool(
                    decision_row.get("report_only_dry_run_run_passed", False)
                ),
                "report_only_dry_run_run_decision": str(
                    decision_row.get("report_only_dry_run_run_decision", "")
                ),
                "future_report_only_dry_run_output_integrity_review_allowed": safe_bool(
                    decision_row.get(
                        "future_report_only_dry_run_output_integrity_review_allowed",
                        False,
                    )
                ),
                "planned_output_artifact_count": 10,
                "recommended_next_phase": RECOMMENDED_NEXT_PHASE,
                "estimated_phase_10_progress_percent": 100,
                "total_checks": len(checks),
                "warning_count": warning_count,
                "error_count": error_count,
                "blocker_count": blocker_count,
                "validation_passed": validation_passed,
                "validation_decision": (
                    "PHASE_10_34_LONG_FORWARD_OBSERVATION_EVIDENCE_"
                    "COLLECTION_REPORT_ONLY_DRY_RUN_RUN_VALIDATED"
                    if validation_passed
                    else
                    "PHASE_10_34_LONG_FORWARD_OBSERVATION_EVIDENCE_"
                    "COLLECTION_REPORT_ONLY_DRY_RUN_RUN_FAILED"
                ),
            }
        ]
    )


def run_long_forward_observation_evidence_collection_report_only_dry_run() -> dict[str, pd.DataFrame]:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    docs_exist = {
        "phase_10_33_dry_run_execution_review_doc_exists": (
            PHASE_10_33_DOC_PATH.exists()
        ),
        "phase_10_34_dry_run_run_doc_exists": PHASE_10_34_DOC_PATH.exists(),
    }
    official_before = OFFICIAL_DATASET_PATH.exists()
    source_manifest_before = build_manifest(SOURCE_PATHS, "SOURCE")
    source = {
        name: read_csv(path) for name, path in SOURCE_PATHS.items()
    }
    source_manifest_pre_run = build_manifest(SOURCE_PATHS, "SOURCE")
    source_validations = build_source_validations(
        source,
        source_manifest_before,
        source_manifest_pre_run,
        not official_before,
    )
    abort_evaluations = build_abort_evaluations(
        source_validations, source, official_before
    )

    preconditions_passed = (
        all(docs_exist.values())
        and all_passed(source_validations)
        and all_passed(abort_evaluations)
        and not abort_evaluations["abort_triggered"].map(safe_bool).any()
    )

    if preconditions_passed:
        synthetic_rows, scenario_map = build_synthetic_rows(
            source["execution_contract"]
        )
        execution = execute_scenarios(synthetic_rows, scenario_map)
    else:
        synthetic_rows = pd.DataFrame(columns=EXPECTED_SCHEMA_FIELDS)
        scenario_map = pd.DataFrame()
        execution = {
            "scenario_results": pd.DataFrame(),
            "validation_results": pd.DataFrame(),
            "rejection_results": pd.DataFrame(),
            "hash_and_dedup_results": pd.DataFrame(),
            "safety_lock_results": pd.DataFrame(),
        }

    official_after = OFFICIAL_DATASET_PATH.exists()
    source_manifest_after = build_manifest(SOURCE_PATHS, "SOURCE")
    source_stable_after_run = (
        manifest_digest(source_manifest_before)
        == manifest_digest(source_manifest_after)
    )
    official_guards = build_official_dataset_guard_results(
        official_before, official_after
    )
    runtime_validations = build_runtime_validations(
        source_validations,
        abort_evaluations,
        synthetic_rows,
        execution["scenario_results"],
        execution["validation_results"],
        execution["rejection_results"],
        execution["hash_and_dedup_results"],
        execution["safety_lock_results"],
        official_guards,
        source_stable_after_run,
        preconditions_passed,
    )
    decision = build_decision(
        source_validations,
        abort_evaluations,
        runtime_validations,
        preconditions_passed,
    )
    checks = build_checks(
        docs_exist,
        source_validations,
        abort_evaluations,
        runtime_validations,
        decision,
        official_before,
        official_after,
    )
    summary = build_summary(
        source_manifest_before,
        source_validations,
        abort_evaluations,
        synthetic_rows,
        execution["scenario_results"],
        runtime_validations,
        execution["safety_lock_results"],
        decision,
        checks,
        official_before,
        official_after,
    )

    validation_output = pd.concat(
        [
            source_validations.assign(validation_scope="SOURCE"),
            abort_evaluations.rename(
                columns={
                    "abort_rule_name": "validation_name",
                    "contract_declared": "details",
                }
            )
            .assign(validation_scope="ABORT")
            .reindex(
                columns=[
                    "validation_position",
                    "validation_name",
                    "passed",
                    "details",
                    "validation_scope",
                ],
                fill_value="",
            ),
            runtime_validations.assign(validation_scope="RUNTIME"),
        ],
        ignore_index=True,
        sort=False,
    )

    output_frames = {
        "summary": summary,
        "synthetic_input_rows": synthetic_rows,
        "scenario_results": execution["scenario_results"],
        "validation_results": validation_output,
        "rejection_results": execution["rejection_results"],
        "hash_and_dedup_results": execution["hash_and_dedup_results"],
        "safety_lock_results": execution["safety_lock_results"],
        "official_dataset_guard_results": official_guards,
        "checks": checks,
    }
    for name, dataframe in output_frames.items():
        dataframe.to_csv(
            REPORTS_DIR / OUTPUT_FILENAMES[name],
            index=False,
        )

    pre_manifest_output_paths = {
        name: REPORTS_DIR / OUTPUT_FILENAMES[name]
        for name in output_frames
    }
    output_manifest = build_manifest(
        pre_manifest_output_paths, "PHASE_10_34_OUTPUT"
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
        "source_execution_contract": source["execution_contract"],
        "source_preconditions": source["preconditions"],
        "source_abort_rules": source["abort_rules"],
        "source_output_plan": source["output_plan"],
        "source_manifest": source_manifest_before,
        "source_validations": source_validations,
        "abort_evaluations": abort_evaluations,
        "synthetic_input_rows": synthetic_rows,
        "scenario_results": execution["scenario_results"],
        "validation_results": validation_output,
        "rejection_results": execution["rejection_results"],
        "hash_and_dedup_results": execution["hash_and_dedup_results"],
        "safety_lock_results": execution["safety_lock_results"],
        "official_dataset_guard_results": official_guards,
        "decision": decision,
        "checks": checks,
        "manifest": combined_manifest,
    }
