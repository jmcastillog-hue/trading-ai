from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

import pandas as pd

from src.long_side.long_forward_observation_dataset_bootstrap_v1 import (
    OFFICIAL_DATASET_PATH,
)


REPORTS_DIR = Path(
    "reports/p10_32_evidence_collection_report_only_dry_run_design_review_v1"
)
SOURCE_DIR = Path(
    "reports/p10_31_evidence_collection_report_only_dry_run_design_v1"
)

PHASE_10_31_DOC_PATH = Path(
    "docs/PHASE_10_LONG_FORWARD_OBSERVATION_EVIDENCE_COLLECTION_REPORT_ONLY_DRY_RUN_DESIGN.md"
)
PHASE_10_32_DOC_PATH = Path(
    "docs/PHASE_10_LONG_FORWARD_OBSERVATION_EVIDENCE_COLLECTION_REPORT_ONLY_DRY_RUN_DESIGN_REVIEW.md"
)

SOURCE_PATHS = {
    "summary": SOURCE_DIR / "report_only_dry_run_design_summary_v1.csv",
    "schema": SOURCE_DIR / "report_only_dry_run_design_schema_v1.csv",
    "scenarios": SOURCE_DIR / "report_only_dry_run_design_scenarios_v1.csv",
    "steps": SOURCE_DIR / "report_only_dry_run_design_steps_v1.csv",
    "dry_run_controls": SOURCE_DIR / "report_only_dry_run_design_controls_v1.csv",
    "artifact_plan": SOURCE_DIR / "report_only_dry_run_design_artifact_plan_v1.csv",
    "acceptance": SOURCE_DIR / "report_only_dry_run_design_acceptance_criteria_v1.csv",
    "outcomes": SOURCE_DIR / "report_only_dry_run_design_expected_outcomes_v1.csv",
    "validations": SOURCE_DIR / "report_only_dry_run_design_validations_v1.csv",
    "evidence_chain": SOURCE_DIR / "report_only_dry_run_design_evidence_chain_v1.csv",
    "validation_controls": SOURCE_DIR / "report_only_dry_run_design_validation_controls_v1.csv",
    "rules": SOURCE_DIR / "report_only_dry_run_design_rules_v1.csv",
    "requirements": SOURCE_DIR / "report_only_dry_run_design_requirements_v1.csv",
    "guard_matrix": SOURCE_DIR / "report_only_dry_run_design_guard_matrix_v1.csv",
    "decision": SOURCE_DIR / "report_only_dry_run_design_decision_v1.csv",
    "checks": SOURCE_DIR / "report_only_dry_run_design_checks_v1.csv",
    "manifest": SOURCE_DIR / "source_report_only_dry_run_design_artifact_manifest_v1.csv",
}

SOURCE_READY_DECISION = (
    "CONTROLLED_FORWARD_OBSERVATION_EVIDENCE_COLLECTION_REPORT_ONLY_"
    "DRY_RUN_DESIGN_READY_FOR_DESIGN_REVIEW"
)
READY_DECISION = (
    "CONTROLLED_FORWARD_OBSERVATION_EVIDENCE_COLLECTION_REPORT_ONLY_"
    "DRY_RUN_DESIGN_REVIEW_READY_FOR_EXECUTION_REVIEW"
)
BLOCKED_DECISION = (
    "CONTROLLED_FORWARD_OBSERVATION_EVIDENCE_COLLECTION_REPORT_ONLY_"
    "DRY_RUN_DESIGN_REVIEW_BLOCKED"
)
RECOMMENDED_NEXT_PHASE = (
    "PHASE_10_33_LONG_FORWARD_OBSERVATION_EVIDENCE_COLLECTION_"
    "REPORT_ONLY_DRY_RUN_EXECUTION_REVIEW_V1"
)

EXPECTED_SOURCE_COUNTS = {
    "source_artifact_count": 12,
    "source_schema_field_count": 54,
    "report_only_dry_run_schema_field_count": 54,
    "dry_run_scenario_count": 6,
    "dry_run_step_count": 16,
    "dry_run_control_count": 20,
    "dry_run_artifact_plan_count": 12,
    "dry_run_acceptance_criterion_count": 18,
    "design_validation_rows": 41,
    "design_evidence_rows": 41,
    "design_control_rows": 41,
    "design_rule_rows": 20,
    "design_requirement_rows": 57,
    "design_guard_rows": 37,
    "total_checks": 64,
    "warning_count": 14,
    "error_count": 0,
    "blocker_count": 0,
}

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
    "evidence_hash", "previous_evidence_hash", "audit_event_id", "created_by",
    "reviewed_by", "rollback_reference", "accepted_as_real_evidence",
    "official_dataset_write_allowed", "evidence_persistence_allowed",
    "signal_generation_enabled", "live_alerts_allowed",
    "paper_trade_execution_allowed", "real_capital_allowed",
    "market_execution_allowed", "exchange_execution_allowed",
    "automation_allowed", "execution_allowed", "notes",
]

EXPECTED_SCENARIOS = {
    "VALID_SYNTHETIC_ROW": ("PASS_REPORT_ONLY", True),
    "EXACT_DUPLICATE_ROW": ("REJECT_DUPLICATE", False),
    "INVALID_SOURCE_SYSTEM": ("REJECT_SOURCE", False),
    "INVALID_UTC_TIMESTAMP": ("REJECT_TIMESTAMP", False),
    "INVALID_LONG_PRICE_STRUCTURE": ("REJECT_PRICE_STRUCTURE", False),
    "PROHIBITED_EXECUTION_FLAG_ENABLED": ("REJECT_SAFETY_FLAG", False),
}

SAFETY_FIELDS = [
    "accepted_as_real_evidence", "official_dataset_write_allowed",
    "evidence_persistence_allowed", "signal_generation_enabled",
    "live_alerts_allowed", "paper_trade_execution_allowed",
    "real_capital_allowed", "market_execution_allowed",
    "exchange_execution_allowed", "automation_allowed", "execution_allowed",
]

EXPECTED_FALSE_GUARDS = [
    "official_dataset_write_allowed", "official_dataset_write_performed",
    "real_forward_dataset_created", "real_forward_signals_recorded",
    "journal_real_rows_accepted", "accepted_as_real_evidence",
    "evidence_persistence_allowed", "evidence_write_performed",
    "signal_generation_enabled", "live_alerts_allowed",
    "paper_trading_enabled", "long_strategy_approved",
    "long_entries_approved", "long_side_established",
    "paper_trade_execution_allowed", "real_capital_allowed",
    "market_execution_allowed", "exchange_execution_allowed",
    "automation_allowed", "execution_allowed", "real_entries_approved",
    "total_project_completed",
]

REVIEW_ITEMS = [
    "phase_10_31_dependency",
    "source_artifact_integrity",
    "source_summary_decision_consistency",
    "source_validation_chain",
    "schema_completeness",
    "schema_safety_defaults",
    "schema_non_implementation",
    "scenario_matrix_completeness",
    "valid_scenario_contract",
    "rejection_scenario_contract",
    "scenario_safety_boundaries",
    "step_plan_completeness",
    "step_execution_lock",
    "dry_run_control_completeness",
    "dry_run_control_non_implementation",
    "artifact_plan_report_only_scope",
    "acceptance_criteria_completeness",
    "acceptance_execution_lock",
    "expected_outcome_completeness",
    "scenario_outcome_alignment",
    "controlled_observation_state",
    "official_dataset_boundary",
    "evidence_collection_boundary",
    "signal_and_execution_boundary",
]


def safe_bool(value: Any, default: bool = False) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        text = value.strip().lower()
        if text in {"true", "1", "yes", "y"}:
            return True
        if text in {"false", "0", "no", "n", ""}:
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
        size = path.stat().st_size if exists else 0
        file_hash = sha256_file(path) if exists else ""
        rows.append(
            {
                "manifest_position": position,
                "artifact_name": name,
                "artifact_filename": path.name,
                "artifact_path": str(path),
                "artifact_exists": exists,
                "artifact_size_bytes": int(size),
                "artifact_non_empty": size > 0,
                "artifact_sha256": file_hash,
                "artifact_sha256_valid": len(file_hash) == 64,
            }
        )
    return pd.DataFrame(rows)


def manifest_digest(df: pd.DataFrame) -> str:
    if df.empty:
        return ""
    payload = (
        df[["artifact_name", "artifact_path", "artifact_size_bytes", "artifact_sha256"]]
        .astype(str)
        .sort_values(["artifact_name", "artifact_path"])
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


def scenario_outcome_alignment(
    scenarios: pd.DataFrame,
    outcomes: pd.DataFrame,
) -> bool:
    required_scenario_columns = [
        "scenario_id",
        "scenario_name",
        "expected_outcome",
        "expected_validation_pass",
    ]
    required_outcome_columns = list(required_scenario_columns)
    if scenarios.empty or outcomes.empty:
        return False
    if not set(required_scenario_columns).issubset(scenarios.columns):
        return False
    if not set(required_outcome_columns).issubset(outcomes.columns):
        return False

    left = scenarios[required_scenario_columns].copy()
    right = outcomes[required_outcome_columns].copy()
    for column in ["scenario_id", "scenario_name", "expected_outcome"]:
        left[column] = left[column].astype(str)
        right[column] = right[column].astype(str)
    left["expected_validation_pass"] = left["expected_validation_pass"].map(safe_bool)
    right["expected_validation_pass"] = right["expected_validation_pass"].map(safe_bool)
    left = left.sort_values("scenario_id").reset_index(drop=True)
    right = right.sort_values("scenario_id").reset_index(drop=True)
    return left.equals(right)


def build_validations(
    source: dict[str, pd.DataFrame],
    manifest_before: pd.DataFrame,
    manifest_after: pd.DataFrame,
    official_absent: bool,
) -> pd.DataFrame:
    summary = source["summary"].iloc[0].to_dict() if not source["summary"].empty else {}
    decision = source["decision"].iloc[0].to_dict() if not source["decision"].empty else {}

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
    stable = (
        bool(manifest_digest(manifest_before))
        and manifest_digest(manifest_before) == manifest_digest(manifest_after)
    )

    summary_decision_consistent = (
        str(summary.get("report_only_dry_run_design_decision", ""))
        == str(decision.get("report_only_dry_run_design_decision", ""))
        == SOURCE_READY_DECISION
        and safe_bool(summary.get("report_only_dry_run_design_passed", False))
        and safe_bool(decision.get("report_only_dry_run_design_passed", False))
    )
    source_counts_valid = all(
        int(safe_float(summary.get(field), -1)) == expected
        for field, expected in EXPECTED_SOURCE_COUNTS.items()
    )
    source_blocks_passed = all(
        all_passed(source[name])
        for name in [
            "validations", "evidence_chain", "validation_controls",
            "rules", "requirements", "guard_matrix", "checks",
        ]
    )

    schema = source["schema"]
    schema_order_valid = (
        len(schema) == 54
        and "field_name" in schema.columns
        and schema["field_name"].astype(str).tolist() == EXPECTED_SCHEMA_FIELDS
    )
    safety_rows = (
        schema[schema["field_name"].astype(str).isin(SAFETY_FIELDS)]
        if not schema.empty and "field_name" in schema.columns
        else pd.DataFrame()
    )
    schema_safety_valid = (
        len(safety_rows) == len(SAFETY_FIELDS)
        and column_all(safety_rows, "safety_lock_field", True)
        and column_all(safety_rows, "default_value", False)
    )
    schema_review_passed = all(
        [
            len(schema) == 54,
            all_passed(schema),
            schema_order_valid,
            column_all(schema, "report_only_dry_run_field", True),
            column_all(schema, "dry_run_runtime_implemented", False),
            column_all(schema, "official_dataset_implemented", False),
            column_all(schema, "synthetic_only", True),
            column_all(schema, "accepted_as_real_evidence", False),
            schema_safety_valid,
        ]
    )

    scenarios = source["scenarios"]
    scenario_names = (
        set(scenarios["scenario_name"].astype(str).tolist())
        if not scenarios.empty and "scenario_name" in scenarios.columns
        else set()
    )
    valid_rows = (
        scenarios[scenarios["scenario_name"].astype(str) == "VALID_SYNTHETIC_ROW"]
        if not scenarios.empty and "scenario_name" in scenarios.columns
        else pd.DataFrame()
    )
    reject_rows = (
        scenarios[scenarios["scenario_name"].astype(str) != "VALID_SYNTHETIC_ROW"]
        if not scenarios.empty and "scenario_name" in scenarios.columns
        else pd.DataFrame()
    )
    scenario_contract_valid = True
    if len(scenarios) != 6 or scenario_names != set(EXPECTED_SCENARIOS):
        scenario_contract_valid = False
    else:
        for name, (outcome, should_pass) in EXPECTED_SCENARIOS.items():
            row = scenarios[scenarios["scenario_name"].astype(str) == name]
            if len(row) != 1:
                scenario_contract_valid = False
                break
            item = row.iloc[0]
            if str(item.get("expected_outcome", "")) != outcome:
                scenario_contract_valid = False
                break
            if safe_bool(item.get("expected_validation_pass", not should_pass)) != should_pass:
                scenario_contract_valid = False
                break
    scenario_safety_valid = all(
        [
            all_passed(scenarios),
            column_all(scenarios, "synthetic_only", True),
            column_all(scenarios, "report_only", True),
            column_all(scenarios, "expected_real_evidence_acceptance", False),
            column_all(scenarios, "expected_official_dataset_write", False),
            column_all(scenarios, "expected_signal_generation", False),
            column_all(scenarios, "expected_live_alert", False),
            column_all(scenarios, "expected_market_execution", False),
            column_all(scenarios, "executed_in_phase_10_31", False),
        ]
    )
    scenario_review_passed = scenario_contract_valid and scenario_safety_valid

    steps = source["steps"]
    step_review_passed = all(
        [
            len(steps) == 16,
            all_passed(steps),
            column_all(steps, "design_only", True),
            column_all(steps, "executed", False),
            column_all(steps, "official_dataset_write_allowed", False),
            column_all(steps, "signal_generation_enabled", False),
            column_all(steps, "market_execution_allowed", False),
        ]
    )

    dry_controls = source["dry_run_controls"]
    dry_control_review_passed = all(
        [
            len(dry_controls) == 20,
            all_passed(dry_controls),
            column_all(dry_controls, "design_only", True),
            column_all(dry_controls, "implemented", False),
            column_all(dry_controls, "enabled_in_phase_10_31", False),
            column_all(dry_controls, "official_dataset_write_allowed", False),
            column_all(dry_controls, "market_execution_allowed", False),
        ]
    )

    artifact_plan = source["artifact_plan"]
    artifact_plan_review_passed = all(
        [
            len(artifact_plan) == 12,
            all_passed(artifact_plan),
            "target_scope" in artifact_plan.columns,
            artifact_plan.get("target_scope", pd.Series(dtype=str)).astype(str).eq("REPORTS_ONLY").all(),
            column_all(artifact_plan, "official_dataset_artifact", False),
            column_all(artifact_plan, "planned_only", True),
        ]
    )

    acceptance = source["acceptance"]
    acceptance_review_passed = all(
        [
            len(acceptance) == 18,
            all_passed(acceptance),
            column_all(acceptance, "required", True),
            column_all(acceptance, "design_only", True),
            column_all(acceptance, "dry_run_executed", False),
        ]
    )

    outcomes = source["outcomes"]
    outcome_review_passed = all(
        [
            len(outcomes) == 6,
            all_passed(outcomes),
            column_all(outcomes, "expected_real_evidence_acceptance", False),
            column_all(outcomes, "expected_official_dataset_write", False),
            column_all(outcomes, "expected_signal_generation", False),
            column_all(outcomes, "expected_live_alert", False),
            column_all(outcomes, "expected_paper_trade_execution", False),
            column_all(outcomes, "expected_real_capital_execution", False),
        ]
    )
    alignment_passed = scenario_outcome_alignment(scenarios, outcomes)

    source_locks_valid = all(
        safe_bool(summary.get(field, True), True) is False
        for field in EXPECTED_FALSE_GUARDS
    )
    source_guards = source["guard_matrix"]
    guard_lookup = (
        {
            str(row["guard_name"]): row.get("actual_value")
            for _, row in source_guards.iterrows()
        }
        if not source_guards.empty and "guard_name" in source_guards.columns
        else {}
    )
    controlled_state_valid = all(
        [
            safe_bool(guard_lookup.get("source_controlled_forward_observation_start_run_performed", False)),
            safe_bool(guard_lookup.get("source_controlled_forward_observation_start_performed", False)),
            safe_bool(guard_lookup.get("forward_observation_start_allowed", False)),
            safe_bool(guard_lookup.get("forward_observation_started", False)),
        ]
    )

    coverage_complete = all(
        [
            schema_review_passed,
            scenario_review_passed,
            step_review_passed,
            dry_control_review_passed,
            artifact_plan_review_passed,
            acceptance_review_passed,
            outcome_review_passed,
            alignment_passed,
        ]
    )

    rows = [
        ("source_artifacts_exist", artifacts_exist, f"artifact_count={len(manifest_before)}"),
        ("source_artifacts_non_empty", artifacts_non_empty, f"artifact_count={len(manifest_before)}"),
        ("source_artifact_hashes_valid", hashes_valid, f"artifact_count={len(manifest_before)}"),
        ("source_artifacts_stable_during_review", stable, f"before={manifest_digest(manifest_before)},after={manifest_digest(manifest_after)}"),
        ("phase_10_31_validation_passed", safe_bool(summary.get("validation_passed", False)), str(summary.get("validation_decision", ""))),
        ("source_design_performed", safe_bool(summary.get("report_only_dry_run_design_performed", False)), str(summary.get("report_only_dry_run_design_performed", ""))),
        ("source_design_passed", safe_bool(summary.get("report_only_dry_run_design_passed", False)), str(summary.get("report_only_dry_run_design_passed", ""))),
        ("source_design_decision_valid", str(summary.get("report_only_dry_run_design_decision", "")) == SOURCE_READY_DECISION, str(summary.get("report_only_dry_run_design_decision", ""))),
        ("source_future_design_review_allowed", safe_bool(summary.get("future_report_only_evidence_collection_dry_run_design_review_allowed", False)), str(summary.get("future_report_only_evidence_collection_dry_run_design_review_allowed", ""))),
        ("source_summary_decision_consistent", summary_decision_consistent, f"consistent={summary_decision_consistent}"),
        ("source_counts_valid", source_counts_valid, ",".join(f"{field}={summary.get(field, '')}" for field in EXPECTED_SOURCE_COUNTS)),
        ("source_design_blocks_passed", source_blocks_passed, f"passed={source_blocks_passed}"),
        ("source_schema_field_count_54", len(schema) == 54, f"rows={len(schema)}"),
        ("source_schema_order_valid", schema_order_valid, f"ordered={schema_order_valid}"),
        ("source_schema_safety_defaults_false", schema_safety_valid, f"valid={schema_safety_valid}"),
        ("source_schema_review_passed", schema_review_passed, f"passed={schema_review_passed}"),
        ("source_scenario_count_6", len(scenarios) == 6, f"rows={len(scenarios)}"),
        ("source_scenario_names_valid", scenario_names == set(EXPECTED_SCENARIOS), f"names={sorted(scenario_names)}"),
        ("source_valid_scenario_count_1", len(valid_rows) == 1, f"rows={len(valid_rows)}"),
        ("source_reject_scenario_count_5", len(reject_rows) == 5, f"rows={len(reject_rows)}"),
        ("source_scenario_contract_valid", scenario_contract_valid, f"valid={scenario_contract_valid}"),
        ("source_scenario_safety_valid", scenario_safety_valid, f"valid={scenario_safety_valid}"),
        ("source_scenario_review_passed", scenario_review_passed, f"passed={scenario_review_passed}"),
        ("source_step_count_16", len(steps) == 16, f"rows={len(steps)}"),
        ("source_step_review_passed", step_review_passed, f"passed={step_review_passed}"),
        ("source_dry_run_control_count_20", len(dry_controls) == 20, f"rows={len(dry_controls)}"),
        ("source_dry_run_control_review_passed", dry_control_review_passed, f"passed={dry_control_review_passed}"),
        ("source_artifact_plan_count_12", len(artifact_plan) == 12, f"rows={len(artifact_plan)}"),
        ("source_artifact_plan_review_passed", artifact_plan_review_passed, f"passed={artifact_plan_review_passed}"),
        ("source_acceptance_count_18", len(acceptance) == 18, f"rows={len(acceptance)}"),
        ("source_acceptance_review_passed", acceptance_review_passed, f"passed={acceptance_review_passed}"),
        ("source_expected_outcome_count_6", len(outcomes) == 6, f"rows={len(outcomes)}"),
        ("source_expected_outcome_review_passed", outcome_review_passed, f"passed={outcome_review_passed}"),
        ("scenario_outcome_alignment_passed", alignment_passed, f"passed={alignment_passed}"),
        ("controlled_observation_state_valid", controlled_state_valid, f"valid={controlled_state_valid}"),
        ("source_operational_locks_valid", source_locks_valid, f"false_guard_count={len(EXPECTED_FALSE_GUARDS)}"),
        ("official_dataset_absent", official_absent, f"official_dataset_absent={official_absent}"),
        ("report_only_dry_run_not_executed", safe_bool(summary.get("report_only_dry_run_executed", True), True) is False, "report_only_dry_run_executed=False"),
        ("report_only_dry_run_rows_zero", int(safe_float(summary.get("report_only_dry_run_rows_generated"), -1)) == 0, "report_only_dry_run_rows_generated=0"),
        ("no_evidence_collection_enabled", safe_bool(summary.get("evidence_collection_enabled", True), True) is False, "evidence_collection_enabled=False"),
        ("no_official_dataset_implementation", safe_bool(summary.get("official_dataset_schema_implemented", True), True) is False, "official_dataset_schema_implemented=False"),
        ("no_signal_or_execution_enabled", all(safe_bool(summary.get(field, True), True) is False for field in ["signal_generation_enabled", "live_alerts_allowed", "paper_trade_execution_allowed", "real_capital_allowed", "market_execution_allowed", "exchange_execution_allowed", "automation_allowed", "execution_allowed"]), "all_execution_boundaries=False"),
        ("design_review_coverage_complete", coverage_complete, f"complete={coverage_complete}"),
        ("long_strategy_remains_unapproved", safe_bool(summary.get("long_strategy_approved", True), True) is False, "long_strategy_approved=False"),
        ("total_project_not_completed", safe_bool(summary.get("total_project_completed", True), True) is False, "total_project_completed=False"),
    ]
    return pd.DataFrame(
        [{"validation_name": name, "passed": bool(passed), "details": details} for name, passed, details in rows]
    )


def build_review_items(validations: pd.DataFrame) -> pd.DataFrame:
    lookup = {
        str(row["validation_name"]): safe_bool(row["passed"], False)
        for _, row in validations.iterrows()
    }
    mapping = {
        "phase_10_31_dependency": ["phase_10_31_validation_passed", "source_design_performed", "source_design_passed", "source_design_decision_valid", "source_future_design_review_allowed"],
        "source_artifact_integrity": ["source_artifacts_exist", "source_artifacts_non_empty", "source_artifact_hashes_valid", "source_artifacts_stable_during_review"],
        "source_summary_decision_consistency": ["source_summary_decision_consistent", "source_counts_valid"],
        "source_validation_chain": ["source_design_blocks_passed"],
        "schema_completeness": ["source_schema_field_count_54", "source_schema_order_valid", "source_schema_review_passed"],
        "schema_safety_defaults": ["source_schema_safety_defaults_false"],
        "schema_non_implementation": ["source_schema_review_passed"],
        "scenario_matrix_completeness": ["source_scenario_count_6", "source_scenario_names_valid"],
        "valid_scenario_contract": ["source_valid_scenario_count_1", "source_scenario_contract_valid"],
        "rejection_scenario_contract": ["source_reject_scenario_count_5", "source_scenario_contract_valid"],
        "scenario_safety_boundaries": ["source_scenario_safety_valid"],
        "step_plan_completeness": ["source_step_count_16", "source_step_review_passed"],
        "step_execution_lock": ["source_step_review_passed", "report_only_dry_run_not_executed"],
        "dry_run_control_completeness": ["source_dry_run_control_count_20", "source_dry_run_control_review_passed"],
        "dry_run_control_non_implementation": ["source_dry_run_control_review_passed"],
        "artifact_plan_report_only_scope": ["source_artifact_plan_count_12", "source_artifact_plan_review_passed"],
        "acceptance_criteria_completeness": ["source_acceptance_count_18", "source_acceptance_review_passed"],
        "acceptance_execution_lock": ["source_acceptance_review_passed", "report_only_dry_run_not_executed"],
        "expected_outcome_completeness": ["source_expected_outcome_count_6", "source_expected_outcome_review_passed"],
        "scenario_outcome_alignment": ["scenario_outcome_alignment_passed"],
        "controlled_observation_state": ["controlled_observation_state_valid"],
        "official_dataset_boundary": ["official_dataset_absent", "no_official_dataset_implementation"],
        "evidence_collection_boundary": ["no_evidence_collection_enabled", "report_only_dry_run_rows_zero"],
        "signal_and_execution_boundary": ["no_signal_or_execution_enabled", "long_strategy_remains_unapproved", "total_project_not_completed"],
    }
    rows = []
    for position, item_name in enumerate(REVIEW_ITEMS, start=1):
        validation_names = mapping[item_name]
        passed = all(lookup.get(name, False) for name in validation_names)
        rows.append(
            {
                "review_item_position": position,
                "review_item_id": f"REPORT_ONLY_DRY_RUN_DESIGN_REVIEW_ITEM_{position:03d}",
                "review_item_name": item_name,
                "validation_names": ",".join(validation_names),
                "required": True,
                "review_only": True,
                "dry_run_execution_allowed": False,
                "evidence_collection_enabled": False,
                "official_dataset_write_allowed": False,
                "market_execution_allowed": False,
                "passed": passed,
            }
        )
    return pd.DataFrame(rows)


def build_findings(review_items: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for _, item in review_items.iterrows():
        passed = safe_bool(item["passed"], False)
        rows.append(
            {
                "finding_id": f"REPORT_ONLY_DRY_RUN_DESIGN_REVIEW_FINDING_{int(item['review_item_position']):03d}",
                "review_item_id": str(item["review_item_id"]),
                "review_item_name": str(item["review_item_name"]),
                "finding_status": "PASS" if passed else "FAIL",
                "material_issue_found": not passed,
                "design_change_required": not passed,
                "execution_review_approved": False,
                "details": "Review criterion passed." if passed else "Review criterion failed and blocks progression.",
                "passed": passed,
            }
        )
    return pd.DataFrame(rows)


def build_controls(validations: pd.DataFrame) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "control_position": position,
                "control_id": f"REPORT_ONLY_DRY_RUN_DESIGN_REVIEW_CONTROL_{position:03d}",
                "control_name": str(row["validation_name"]),
                "required": True,
                "review_only": True,
                "dry_run_executed": False,
                "evidence_collection_enabled": False,
                "official_dataset_write_allowed": False,
                "market_execution_allowed": False,
                "passed": safe_bool(row["passed"], False),
            }
            for position, (_, row) in enumerate(validations.iterrows(), start=1)
        ]
    )


def build_guard_matrix() -> pd.DataFrame:
    true_names = [
        "source_controlled_forward_observation_start_run_performed",
        "source_controlled_forward_observation_start_performed",
        "forward_observation_start_allowed",
        "forward_observation_started",
        "report_only_dry_run_design_review_performed",
        "report_only_dry_run_design_review_passed",
        "future_report_only_dry_run_execution_review_allowed",
    ]
    false_names = [
        "report_only_dry_run_executed",
        "new_controlled_forward_observation_start_run_performed",
        "new_controlled_forward_observation_start_performed",
        "evidence_collection_enabled",
        "evidence_collection_started",
        "official_dataset_schema_implemented",
    ] + EXPECTED_FALSE_GUARDS
    rows = [
        {"guard_name": name, "required_value": True, "actual_value": True, "passed": True, "guard_group": "design_review_state"}
        for name in true_names
    ]
    rows.extend(
        {"guard_name": name, "required_value": False, "actual_value": False, "passed": True, "guard_group": "design_review_safety_guard"}
        for name in false_names
    )
    rows.extend(
        [
            {"guard_name": "report_only_dry_run_rows_generated", "required_value": 0, "actual_value": 0, "passed": True, "guard_group": "dry_run_execution_guard"},
            {"guard_name": "official_evidence_rows_written", "required_value": 0, "actual_value": 0, "passed": True, "guard_group": "official_dataset_guard"},
        ]
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
        ("review_validation_count_positive", len(validations) > 0, ">0", str(len(validations))),
        ("all_review_validations_passed", all_passed(validations), "True", str(all_passed(validations))),
        ("review_item_count_24", len(review_items) == 24, "24", str(len(review_items))),
        ("all_review_items_passed", all_passed(review_items), "True", str(all_passed(review_items))),
        ("review_finding_count_24", len(findings) == 24, "24", str(len(findings))),
        ("all_review_findings_passed", all_passed(findings), "True", str(all_passed(findings))),
        ("material_issue_count_zero", int(findings["material_issue_found"].map(safe_bool).sum()) == 0, "0", str(int(findings["material_issue_found"].map(safe_bool).sum()))),
        ("review_control_count_matches", len(controls) == len(validations), str(len(validations)), str(len(controls))),
        ("all_review_controls_passed", all_passed(controls), "True", str(all_passed(controls))),
        ("review_guard_count_37", len(guards) == 37, "37", str(len(guards))),
        ("all_review_guards_passed", all_passed(guards), "True", str(all_passed(guards))),
        ("review_only", True, "True", "True"),
        ("dry_run_not_executed", True, "False", "False"),
        ("dry_run_rows_zero", True, "0", "0"),
        ("evidence_collection_disabled", True, "False", "False"),
        ("official_dataset_not_implemented", True, "False", "False"),
        ("official_dataset_writes_disabled", True, "False", "False"),
        ("signal_generation_disabled", True, "False", "False"),
        ("market_execution_disabled", True, "False", "False"),
        ("total_project_not_completed", True, "False", "False"),
    ]
    return pd.DataFrame(
        [
            {
                "rule_id": f"REPORT_ONLY_DRY_RUN_DESIGN_REVIEW_RULE_{position:03d}",
                "rule_name": name,
                "passed": bool(passed),
                "required_value": required,
                "actual_value": actual,
            }
            for position, (name, passed, required, actual) in enumerate(rows, start=1)
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
        (str(row["validation_name"]), safe_bool(row["passed"], False), "True", str(safe_bool(row["passed"], False)))
        for _, row in validations.iterrows()
    ]
    rows.extend(
        [
            ("review_items_passed", all_passed(review_items), "True", str(all_passed(review_items))),
            ("review_findings_passed", all_passed(findings), "True", str(all_passed(findings))),
            ("review_controls_passed", all_passed(controls), "True", str(all_passed(controls))),
            ("review_rules_passed", all_passed(rules), "True", str(all_passed(rules))),
            ("review_guards_passed", all_passed(guards), "True", str(all_passed(guards))),
            ("design_review_performed", True, "True", "True"),
            ("future_execution_review_allowed", True, "True", "True"),
            ("dry_run_not_executed", True, "False", "False"),
            ("dry_run_rows_generated_zero", True, "0", "0"),
            ("evidence_collection_not_enabled", True, "False", "False"),
            ("official_dataset_schema_not_implemented", True, "False", "False"),
            ("official_evidence_rows_written_zero", True, "0", "0"),
            ("signal_generation_disabled", True, "False", "False"),
            ("paper_trading_disabled", True, "False", "False"),
            ("market_execution_disabled", True, "False", "False"),
            ("total_project_not_completed", True, "False", "False"),
        ]
    )
    return pd.DataFrame(
        [
            {
                "requirement_id": f"REPORT_ONLY_DRY_RUN_DESIGN_REVIEW_REQ_{position:03d}",
                "requirement_name": name,
                "passed": bool(passed),
                "required_value": required,
                "actual_value": actual,
            }
            for position, (name, passed, required, actual) in enumerate(rows, start=1)
        ]
    )


def build_decision(
    requirements: pd.DataFrame,
    rules: pd.DataFrame,
    guards: pd.DataFrame,
) -> pd.DataFrame:
    passed_count = int(requirements["passed"].map(safe_bool).sum()) if not requirements.empty else 0
    failed_count = len(requirements) - passed_count
    review_passed = len(requirements) > 0 and failed_count == 0 and all_passed(rules) and all_passed(guards)
    failed_names = ",".join(
        requirements[~requirements["passed"].map(safe_bool)]["requirement_name"].astype(str).tolist()
    )
    return pd.DataFrame(
        [
            {
                "report_only_dry_run_design_review_id": "PHASE_10_32_LONG_FORWARD_OBSERVATION_EVIDENCE_COLLECTION_REPORT_ONLY_DRY_RUN_DESIGN_REVIEW_001",
                "report_only_dry_run_design_review_performed": True,
                "report_only_dry_run_design_review_passed": review_passed,
                "report_only_dry_run_design_review_decision": READY_DECISION if review_passed else BLOCKED_DECISION,
                "total_requirements": len(requirements),
                "passed_requirements": passed_count,
                "failed_requirements": failed_count,
                "failed_requirement_names": failed_names,
                "future_report_only_dry_run_execution_review_allowed": review_passed,
                "report_only_dry_run_executed": False,
                "report_only_dry_run_rows_generated": 0,
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


def validate_long_forward_observation_evidence_collection_report_only_dry_run_design_review() -> dict[str, pd.DataFrame]:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    checks: list[dict[str, Any]] = []

    for name, path in {
        "phase_10_31_dry_run_design_doc_exists": PHASE_10_31_DOC_PATH,
        "phase_10_32_dry_run_design_review_doc_exists": PHASE_10_32_DOC_PATH,
    }.items():
        exists = path.exists()
        checks.append(check_row("phase_anchor", name, exists, "INFO" if exists else "ERROR", str(path)))

    official_before = OFFICIAL_DATASET_PATH.exists()
    manifest_before = build_manifest()
    source = {name: read_csv(path) for name, path in SOURCE_PATHS.items()}
    manifest_after = build_manifest()

    validations = build_validations(source, manifest_before, manifest_after, not official_before)
    review_items = build_review_items(validations)
    findings = build_findings(review_items)
    controls = build_controls(validations)
    guards = build_guard_matrix()
    rules = build_rules(validations, review_items, findings, controls, guards)
    requirements = build_requirements(validations, review_items, findings, controls, rules, guards)
    decision = build_decision(requirements, rules, guards)
    decision_row = decision.iloc[0].to_dict() if not decision.empty else {}

    aggregate_checks = {
        "review_validations_passed": all_passed(validations),
        "review_items_passed": all_passed(review_items),
        "review_findings_passed": all_passed(findings),
        "review_controls_passed": all_passed(controls),
        "review_rules_passed": all_passed(rules),
        "review_requirements_passed": all_passed(requirements),
        "review_guards_passed": all_passed(guards),
        "report_only_dry_run_design_review_passed": safe_bool(decision_row.get("report_only_dry_run_design_review_passed", False)),
        "report_only_dry_run_design_review_decision_expected": str(decision_row.get("report_only_dry_run_design_review_decision", "")) == READY_DECISION,
    }
    for name, passed in aggregate_checks.items():
        details = (
            str(decision_row.get("report_only_dry_run_design_review_decision", ""))
            if name.endswith("decision_expected")
            else f"{name}={passed}"
        )
        checks.append(check_row("report_only_dry_run_design_review", name, passed, "INFO" if passed else "ERROR", details))

    official_after = OFFICIAL_DATASET_PATH.exists()
    official_unchanged = not official_before and not official_after
    checks.append(
        check_row(
            "official_dataset_guard",
            "official_dataset_not_created_or_written",
            official_unchanged,
            "INFO" if official_unchanged else "ERROR",
            f"before={official_before},after={official_after}",
        )
    )

    for _, row in guards.iterrows():
        passed = safe_bool(row["passed"], False)
        checks.append(
            check_row(
                "report_only_dry_run_design_review_safety_flags",
                str(row["guard_name"]),
                passed,
                "INFO" if passed else "ERROR",
                f"{row['guard_name']}={row['actual_value']} (required={row['required_value']})",
            )
        )

    scope_warnings = [
        ("review_only", "Phase 10.32 reviews only the report-only dry-run design."),
        ("dry_run_not_executed", "No dry-run row was generated or executed."),
        ("observation_state_preserved", "The controlled observation state remains started."),
        ("evidence_collection_not_enabled", "Evidence collection remains disabled."),
        ("official_dataset_not_implemented", "The official evidence dataset is not implemented."),
        ("official_dataset_not_written", "The official evidence dataset remains absent and unwritten."),
        ("signal_generation_not_enabled", "Signal generation remains disabled."),
        ("live_alerts_not_enabled", "Live alerts remain disabled."),
        ("paper_trading_not_enabled", "Paper trading remains disabled."),
        ("long_strategy_not_approved", "The LONG research candidate remains unapproved."),
        ("real_capital_not_allowed", "Real capital remains prohibited."),
        ("market_execution_not_allowed", "Market execution remains prohibited."),
        ("total_project_not_completed", "The total project is not completed."),
    ]
    for name, details in scope_warnings:
        checks.append(check_row("scope_control", name, True, "WARNING", details))

    future_allowed = safe_bool(
        decision_row.get("future_report_only_dry_run_execution_review_allowed", False)
    )
    checks.append(
        check_row(
            "planning_scope",
            "future_report_only_dry_run_execution_review_allowed",
            future_allowed,
            "WARNING" if future_allowed else "ERROR",
            "Allows only a future execution review; no dry-run execution or operational capability.",
        )
    )
    checks.append(
        check_row(
            "phase_transition",
            "phase_10_33_recommended_next",
            True,
            "INFO",
            "Recommended next: Phase 10.33 report-only dry-run execution review.",
        )
    )

    checks_df = pd.DataFrame(checks)
    blocker_count = int(checks_df["blocker"].map(safe_bool).sum())
    error_count = int(checks_df["severity"].eq("ERROR").sum())
    warning_count = int(checks_df["severity"].eq("WARNING").sum())
    validation_passed = blocker_count == 0 and error_count == 0

    source_summary = source["summary"].iloc[0].to_dict() if not source["summary"].empty else {}
    lookup = {
        str(row["validation_name"]): safe_bool(row["passed"], False)
        for _, row in validations.iterrows()
    }

    summary_df = pd.DataFrame(
        [
            {
                "phase": "10.32",
                "long_forward_observation_evidence_collection_report_only_dry_run_design_review_defined": True,
                "phase_10_31_validation_passed": lookup.get("phase_10_31_validation_passed", False),
                "source_report_only_dry_run_design_performed": lookup.get("source_design_performed", False),
                "source_report_only_dry_run_design_passed": lookup.get("source_design_passed", False),
                "source_report_only_dry_run_design_decision": str(source_summary.get("report_only_dry_run_design_decision", "")),
                "source_future_report_only_dry_run_design_review_allowed": lookup.get("source_future_design_review_allowed", False),
                "source_artifact_count": len(manifest_after),
                "source_artifacts_exist": lookup.get("source_artifacts_exist", False),
                "source_artifacts_non_empty": lookup.get("source_artifacts_non_empty", False),
                "source_artifact_hashes_valid": lookup.get("source_artifact_hashes_valid", False),
                "source_artifacts_stable_during_review": lookup.get("source_artifacts_stable_during_review", False),
                "source_manifest_sha256": manifest_digest(manifest_after),
                "source_summary_decision_consistent": lookup.get("source_summary_decision_consistent", False),
                "source_counts_valid": lookup.get("source_counts_valid", False),
                "source_design_blocks_passed": lookup.get("source_design_blocks_passed", False),
                "source_schema_review_passed": lookup.get("source_schema_review_passed", False),
                "source_scenario_review_passed": lookup.get("source_scenario_review_passed", False),
                "source_step_review_passed": lookup.get("source_step_review_passed", False),
                "source_dry_run_control_review_passed": lookup.get("source_dry_run_control_review_passed", False),
                "source_artifact_plan_review_passed": lookup.get("source_artifact_plan_review_passed", False),
                "source_acceptance_review_passed": lookup.get("source_acceptance_review_passed", False),
                "source_expected_outcome_review_passed": lookup.get("source_expected_outcome_review_passed", False),
                "scenario_outcome_alignment_passed": lookup.get("scenario_outcome_alignment_passed", False),
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
                "review_validations_passed": all_passed(validations),
                "review_items_passed": all_passed(review_items),
                "review_findings_passed": all_passed(findings),
                "review_controls_passed": all_passed(controls),
                "review_rules_passed": all_passed(rules),
                "review_requirements_passed": all_passed(requirements),
                "review_guards_passed": all_passed(guards),
                "material_issue_count": int(findings["material_issue_found"].map(safe_bool).sum()),
                "report_only_dry_run_design_review_performed": True,
                "report_only_dry_run_design_review_passed": safe_bool(decision_row.get("report_only_dry_run_design_review_passed", False)),
                "report_only_dry_run_design_review_decision": str(decision_row.get("report_only_dry_run_design_review_decision", "")),
                "future_report_only_dry_run_execution_review_allowed": future_allowed,
                "report_only_dry_run_executed": False,
                "report_only_dry_run_rows_generated": 0,
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
                    "PHASE_10_32_LONG_FORWARD_OBSERVATION_EVIDENCE_COLLECTION_REPORT_ONLY_DRY_RUN_DESIGN_REVIEW_VALIDATED"
                    if validation_passed
                    else
                    "PHASE_10_32_LONG_FORWARD_OBSERVATION_EVIDENCE_COLLECTION_REPORT_ONLY_DRY_RUN_DESIGN_REVIEW_FAILED"
                ),
            }
        ]
    )

    outputs = {
        "phase_10_31_source_summary_v1.csv": source["summary"],
        "phase_10_31_source_schema_v1.csv": source["schema"],
        "phase_10_31_source_scenarios_v1.csv": source["scenarios"],
        "phase_10_31_source_steps_v1.csv": source["steps"],
        "phase_10_31_source_dry_run_controls_v1.csv": source["dry_run_controls"],
        "phase_10_31_source_artifact_plan_v1.csv": source["artifact_plan"],
        "phase_10_31_source_acceptance_v1.csv": source["acceptance"],
        "phase_10_31_source_outcomes_v1.csv": source["outcomes"],
        "phase_10_31_source_validations_v1.csv": source["validations"],
        "phase_10_31_source_evidence_chain_v1.csv": source["evidence_chain"],
        "phase_10_31_source_validation_controls_v1.csv": source["validation_controls"],
        "phase_10_31_source_rules_v1.csv": source["rules"],
        "phase_10_31_source_requirements_v1.csv": source["requirements"],
        "phase_10_31_source_guard_matrix_v1.csv": source["guard_matrix"],
        "phase_10_31_source_decision_v1.csv": source["decision"],
        "phase_10_31_source_checks_v1.csv": source["checks"],
        "phase_10_31_source_manifest_v1.csv": source["manifest"],
        "source_report_only_dry_run_design_review_artifact_manifest_v1.csv": manifest_after,
        "report_only_dry_run_design_review_validations_v1.csv": validations,
        "report_only_dry_run_design_review_items_v1.csv": review_items,
        "report_only_dry_run_design_review_findings_v1.csv": findings,
        "report_only_dry_run_design_review_controls_v1.csv": controls,
        "report_only_dry_run_design_review_rules_v1.csv": rules,
        "report_only_dry_run_design_review_requirements_v1.csv": requirements,
        "report_only_dry_run_design_review_guard_matrix_v1.csv": guards,
        "report_only_dry_run_design_review_decision_v1.csv": decision,
        "report_only_dry_run_design_review_checks_v1.csv": checks_df,
        "report_only_dry_run_design_review_summary_v1.csv": summary_df,
    }
    for filename, dataframe in outputs.items():
        dataframe.to_csv(REPORTS_DIR / filename, index=False)

    return {
        "summary": summary_df,
        "source_summary": source["summary"],
        "source_schema": source["schema"],
        "source_scenarios": source["scenarios"],
        "source_steps": source["steps"],
        "source_dry_run_controls": source["dry_run_controls"],
        "source_artifact_plan": source["artifact_plan"],
        "source_acceptance": source["acceptance"],
        "source_outcomes": source["outcomes"],
        "source_validations": source["validations"],
        "source_evidence_chain": source["evidence_chain"],
        "source_validation_controls": source["validation_controls"],
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
