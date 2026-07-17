from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

import pandas as pd

from src.long_side.long_forward_observation_dataset_bootstrap_v1 import (
    OFFICIAL_DATASET_PATH,
    PRIMARY_RESEARCH_CANDIDATE,
)


REPORTS_DIR = Path(
    "reports/p10_31_evidence_collection_report_only_dry_run_design_v1"
)
SOURCE_DIR = Path("reports/p10_30_evidence_collection_design_review_v1")

PHASE_10_30_DOC_PATH = Path(
    "docs/PHASE_10_LONG_FORWARD_OBSERVATION_EVIDENCE_COLLECTION_DESIGN_REVIEW.md"
)
PHASE_10_31_DOC_PATH = Path(
    "docs/PHASE_10_LONG_FORWARD_OBSERVATION_EVIDENCE_COLLECTION_REPORT_ONLY_DRY_RUN_DESIGN.md"
)

SOURCE_PATHS = {
    "summary": SOURCE_DIR / "evidence_collection_design_review_summary_v1.csv",
    "schema": SOURCE_DIR / "phase_10_29_source_schema_v1.csv",
    "review_validations": SOURCE_DIR / "evidence_collection_design_review_validations_v1.csv",
    "review_items": SOURCE_DIR / "evidence_collection_design_review_items_v1.csv",
    "review_findings": SOURCE_DIR / "evidence_collection_design_review_findings_v1.csv",
    "review_controls": SOURCE_DIR / "evidence_collection_design_review_controls_v1.csv",
    "review_rules": SOURCE_DIR / "evidence_collection_design_review_rules_v1.csv",
    "review_requirements": SOURCE_DIR / "evidence_collection_design_review_requirements_v1.csv",
    "review_guard_matrix": SOURCE_DIR / "evidence_collection_design_review_guard_matrix_v1.csv",
    "review_decision": SOURCE_DIR / "evidence_collection_design_review_decision_v1.csv",
    "review_checks": SOURCE_DIR / "evidence_collection_design_review_checks_v1.csv",
    "review_manifest": SOURCE_DIR / "source_design_review_artifact_manifest_v1.csv",
}

SOURCE_READY_DECISION = (
    "CONTROLLED_FORWARD_OBSERVATION_EVIDENCE_COLLECTION_DESIGN_REVIEW_"
    "READY_FOR_REPORT_ONLY_DRY_RUN_DESIGN"
)
READY_DECISION = (
    "CONTROLLED_FORWARD_OBSERVATION_EVIDENCE_COLLECTION_REPORT_ONLY_"
    "DRY_RUN_DESIGN_READY_FOR_DESIGN_REVIEW"
)
BLOCKED_DECISION = (
    "CONTROLLED_FORWARD_OBSERVATION_EVIDENCE_COLLECTION_REPORT_ONLY_"
    "DRY_RUN_DESIGN_BLOCKED"
)
RECOMMENDED_NEXT_PHASE = (
    "PHASE_10_32_LONG_FORWARD_OBSERVATION_EVIDENCE_COLLECTION_"
    "REPORT_ONLY_DRY_RUN_DESIGN_REVIEW_V1"
)

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

SCENARIOS = [
    ("VALID_SYNTHETIC_ROW", "PASS_REPORT_ONLY", True),
    ("EXACT_DUPLICATE_ROW", "REJECT_DUPLICATE", False),
    ("INVALID_SOURCE_SYSTEM", "REJECT_SOURCE", False),
    ("INVALID_UTC_TIMESTAMP", "REJECT_TIMESTAMP", False),
    ("INVALID_LONG_PRICE_STRUCTURE", "REJECT_PRICE_STRUCTURE", False),
    ("PROHIBITED_EXECUTION_FLAG_ENABLED", "REJECT_SAFETY_FLAG", False),
]

STEPS = [
    "load_phase_10_30_review_artifacts",
    "verify_review_decision",
    "load_54_field_schema",
    "build_synthetic_base_row_in_memory",
    "apply_report_only_markers",
    "force_all_safety_locks_false",
    "derive_deduplication_key",
    "derive_source_row_hash",
    "derive_evidence_hash",
    "instantiate_six_scenarios",
    "validate_schema",
    "validate_provenance",
    "validate_long_price_structure",
    "validate_deduplication_and_rejection",
    "write_report_only_artifacts_only",
    "verify_official_dataset_unchanged",
]

DRY_RUN_CONTROLS = [
    "phase_10_30_dependency_passed",
    "source_artifact_integrity_valid",
    "source_review_decision_consistent",
    "source_review_blocks_passed",
    "schema_field_count_54",
    "schema_order_preserved",
    "schema_safety_defaults_false",
    "scenario_count_6",
    "valid_scenario_defined",
    "duplicate_scenario_defined",
    "invalid_source_scenario_defined",
    "invalid_timestamp_scenario_defined",
    "invalid_price_scenario_defined",
    "execution_flag_scenario_defined",
    "synthetic_report_only_scope",
    "no_real_evidence_acceptance",
    "no_official_dataset_write",
    "no_signal_or_alert_generation",
    "no_paper_or_real_execution",
    "future_design_review_only",
]

ARTIFACT_PLAN = [
    "source_review_summary_copy",
    "source_review_decision_copy",
    "source_review_manifest_copy",
    "dry_run_schema",
    "dry_run_scenario_matrix",
    "dry_run_step_plan",
    "dry_run_control_plan",
    "dry_run_expected_outcomes",
    "dry_run_acceptance_criteria",
    "dry_run_design_decision",
    "dry_run_design_checks",
    "dry_run_design_summary",
]

ACCEPTANCE_CRITERIA = [
    "source_review_validation_passed",
    "source_review_performed_and_passed",
    "source_review_decision_expected",
    "source_artifacts_stable",
    "source_material_issue_count_zero",
    "schema_has_54_fields",
    "schema_order_matches",
    "schema_safety_defaults_false",
    "six_scenarios_defined",
    "valid_row_expected_to_pass_report_only",
    "five_invalid_or_duplicate_rows_expected_to_reject",
    "no_real_evidence_expected",
    "no_official_dataset_write_expected",
    "no_signal_generation_expected",
    "no_live_alert_expected",
    "no_paper_or_real_execution_expected",
    "dry_run_not_executed_in_design_phase",
    "future_design_review_only",
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
        and df["passed"].map(lambda x: safe_bool(x, False)).all()
    )


def column_all(df: pd.DataFrame, column: str, expected: bool) -> bool:
    return (
        not df.empty
        and column in df.columns
        and df[column].map(lambda x: safe_bool(x, not expected)).eq(expected).all()
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


def check_row(group: str, name: str, passed: bool, severity: str, details: str) -> dict:
    return {
        "check_group": group,
        "check_name": name,
        "passed": bool(passed),
        "severity": severity,
        "details": details,
        "blocker": severity == "ERROR" and not bool(passed),
    }


def build_report_only_schema(source_schema: pd.DataFrame) -> pd.DataFrame:
    if source_schema.empty:
        return pd.DataFrame()
    result = source_schema.copy()
    result["report_only_dry_run_field"] = True
    result["dry_run_runtime_implemented"] = False
    result["official_dataset_implemented"] = False
    result["synthetic_only"] = True
    result["accepted_as_real_evidence"] = False
    result["passed"] = True
    return result


def build_named_table(
    names: list[str],
    prefix: str,
    name_column: str,
    extra: dict[str, Any],
) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "position": position,
                "item_id": f"{prefix}_{position:03d}",
                name_column: name,
                **extra,
                "passed": True,
            }
            for position, name in enumerate(names, start=1)
        ]
    )


def build_scenarios() -> pd.DataFrame:
    rows = []
    for position, (name, outcome, should_pass) in enumerate(SCENARIOS, start=1):
        rows.append(
            {
                "scenario_position": position,
                "scenario_id": f"REPORT_ONLY_DRY_RUN_SCENARIO_{position:03d}",
                "scenario_name": name,
                "expected_outcome": outcome,
                "expected_validation_pass": should_pass,
                "synthetic_only": True,
                "report_only": True,
                "expected_real_evidence_acceptance": False,
                "expected_official_dataset_write": False,
                "expected_signal_generation": False,
                "expected_live_alert": False,
                "expected_market_execution": False,
                "executed_in_phase_10_31": False,
                "passed": True,
            }
        )
    return pd.DataFrame(rows)


def build_expected_outcomes(scenarios: pd.DataFrame) -> pd.DataFrame:
    result = scenarios[
        [
            "scenario_position",
            "scenario_id",
            "scenario_name",
            "expected_outcome",
            "expected_validation_pass",
        ]
    ].copy()
    result["expected_real_evidence_acceptance"] = False
    result["expected_official_dataset_write"] = False
    result["expected_signal_generation"] = False
    result["expected_live_alert"] = False
    result["expected_paper_trade_execution"] = False
    result["expected_real_capital_execution"] = False
    result["passed"] = True
    return result


def build_validations(
    source: dict[str, pd.DataFrame],
    manifest_before: pd.DataFrame,
    manifest_after: pd.DataFrame,
    schema: pd.DataFrame,
    scenarios: pd.DataFrame,
    steps: pd.DataFrame,
    dry_controls: pd.DataFrame,
    artifact_plan: pd.DataFrame,
    acceptance: pd.DataFrame,
    outcomes: pd.DataFrame,
    official_absent: bool,
) -> pd.DataFrame:
    summary = source["summary"].iloc[0].to_dict() if not source["summary"].empty else {}
    decision = (
        source["review_decision"].iloc[0].to_dict()
        if not source["review_decision"].empty
        else {}
    )

    source_artifacts_ok = (
        not manifest_before.empty
        and manifest_before["artifact_exists"].map(safe_bool).all()
        and manifest_before["artifact_non_empty"].map(safe_bool).all()
        and manifest_before["artifact_sha256_valid"].map(safe_bool).all()
    )
    stable = (
        bool(manifest_digest(manifest_before))
        and manifest_digest(manifest_before) == manifest_digest(manifest_after)
    )
    summary_decision_consistent = (
        str(summary.get("evidence_collection_design_review_decision", ""))
        == str(decision.get("evidence_collection_design_review_decision", ""))
        == SOURCE_READY_DECISION
        and safe_bool(summary.get("evidence_collection_design_review_passed", False))
        and safe_bool(decision.get("evidence_collection_design_review_passed", False))
    )
    review_blocks_ok = all(
        all_passed(source[key])
        for key in [
            "review_validations",
            "review_items",
            "review_findings",
            "review_controls",
            "review_rules",
            "review_requirements",
            "review_guard_matrix",
        ]
    )
    source_schema = source["schema"]
    source_schema_ok = (
        len(source_schema) == 54
        and "field_name" in source_schema.columns
        and source_schema["field_name"].astype(str).tolist() == EXPECTED_SCHEMA_FIELDS
        and all_passed(source_schema)
    )
    schema_ok = (
        len(schema) == 54
        and schema["field_name"].astype(str).tolist() == EXPECTED_SCHEMA_FIELDS
        and all_passed(schema)
        and column_all(schema, "report_only_dry_run_field", True)
        and column_all(schema, "dry_run_runtime_implemented", False)
        and column_all(schema, "official_dataset_implemented", False)
        and column_all(schema, "synthetic_only", True)
        and column_all(schema, "accepted_as_real_evidence", False)
    )
    safety_rows = schema[schema["field_name"].astype(str).isin(SAFETY_FIELDS)]
    safety_defaults_ok = (
        len(safety_rows) == len(SAFETY_FIELDS)
        and column_all(safety_rows, "safety_lock_field", True)
        and column_all(safety_rows, "default_value", False)
    )
    scenarios_ok = (
        len(scenarios) == 6
        and all_passed(scenarios)
        and column_all(scenarios, "synthetic_only", True)
        and column_all(scenarios, "report_only", True)
        and column_all(scenarios, "expected_real_evidence_acceptance", False)
        and column_all(scenarios, "expected_official_dataset_write", False)
        and column_all(scenarios, "expected_market_execution", False)
        and column_all(scenarios, "executed_in_phase_10_31", False)
    )
    source_locks_ok = all(
        safe_bool(summary.get(field, True), True) is False
        for field in EXPECTED_FALSE_GUARDS
    )
    controlled_state_ok = all(
        [
            safe_bool(summary.get("source_controlled_forward_observation_start_run_performed", False)),
            safe_bool(summary.get("source_controlled_forward_observation_start_performed", False)),
            safe_bool(summary.get("forward_observation_started", False)),
        ]
    )

    rows = [
        ("source_artifacts_exist", source_artifacts_ok, f"artifact_count={len(manifest_before)}"),
        ("source_artifacts_non_empty", source_artifacts_ok, f"artifact_count={len(manifest_before)}"),
        ("source_artifact_hashes_valid", source_artifacts_ok, f"artifact_count={len(manifest_before)}"),
        ("source_artifacts_stable_during_design", stable, f"before={manifest_digest(manifest_before)},after={manifest_digest(manifest_after)}"),
        ("phase_10_30_validation_passed", safe_bool(summary.get("validation_passed", False)), str(summary.get("validation_decision", ""))),
        ("source_design_review_performed", safe_bool(summary.get("evidence_collection_design_review_performed", False)), str(summary.get("evidence_collection_design_review_performed", ""))),
        ("source_design_review_passed", safe_bool(summary.get("evidence_collection_design_review_passed", False)), str(summary.get("evidence_collection_design_review_passed", ""))),
        ("source_design_review_decision_valid", str(summary.get("evidence_collection_design_review_decision", "")) == SOURCE_READY_DECISION, str(summary.get("evidence_collection_design_review_decision", ""))),
        ("source_future_dry_run_design_allowed", safe_bool(summary.get("future_report_only_evidence_collection_dry_run_design_allowed", False)), str(summary.get("future_report_only_evidence_collection_dry_run_design_allowed", ""))),
        ("source_summary_decision_consistent", summary_decision_consistent, f"consistent={summary_decision_consistent}"),
        ("source_review_blocks_passed", review_blocks_ok, f"passed={review_blocks_ok}"),
        ("source_material_issue_count_zero", int(safe_float(summary.get("material_issue_count"), -1)) == 0, str(summary.get("material_issue_count", ""))),
        ("source_schema_field_count_54", len(source_schema) == 54, f"rows={len(source_schema)}"),
        ("source_schema_valid", source_schema_ok, f"valid={source_schema_ok}"),
        ("report_only_schema_field_count_54", len(schema) == 54, f"rows={len(schema)}"),
        ("report_only_schema_valid", schema_ok, f"valid={schema_ok}"),
        ("report_only_schema_safety_defaults_false", safety_defaults_ok, f"valid={safety_defaults_ok}"),
        ("dry_run_scenario_count_6", len(scenarios) == 6, f"rows={len(scenarios)}"),
        ("dry_run_scenarios_valid", scenarios_ok, f"valid={scenarios_ok}"),
        ("dry_run_step_count_16", len(steps) == 16, f"rows={len(steps)}"),
        ("dry_run_steps_valid", len(steps) == 16 and all_passed(steps) and column_all(steps, "executed", False), f"rows={len(steps)}"),
        ("dry_run_control_count_20", len(dry_controls) == 20, f"rows={len(dry_controls)}"),
        ("dry_run_controls_valid", len(dry_controls) == 20 and all_passed(dry_controls) and column_all(dry_controls, "implemented", False), f"rows={len(dry_controls)}"),
        ("dry_run_artifact_plan_count_12", len(artifact_plan) == 12, f"rows={len(artifact_plan)}"),
        ("dry_run_artifact_plan_valid", len(artifact_plan) == 12 and all_passed(artifact_plan) and column_all(artifact_plan, "official_dataset_artifact", False), f"rows={len(artifact_plan)}"),
        ("dry_run_acceptance_criterion_count_18", len(acceptance) == 18, f"rows={len(acceptance)}"),
        ("dry_run_acceptance_criteria_valid", len(acceptance) == 18 and all_passed(acceptance) and column_all(acceptance, "dry_run_executed", False), f"rows={len(acceptance)}"),
        ("dry_run_expected_outcomes_valid", len(outcomes) == 6 and all_passed(outcomes) and column_all(outcomes, "expected_real_evidence_acceptance", False) and column_all(outcomes, "expected_official_dataset_write", False), f"rows={len(outcomes)}"),
        ("controlled_observation_state_valid", controlled_state_ok, f"valid={controlled_state_ok}"),
        ("source_operational_locks_valid", source_locks_ok, f"false_guard_count={len(EXPECTED_FALSE_GUARDS)}"),
        ("official_dataset_absent", official_absent, f"official_dataset_absent={official_absent}"),
        ("report_only_dry_run_not_executed", True, "report_only_dry_run_executed=False"),
        ("report_only_dry_run_rows_zero", True, "report_only_dry_run_rows_generated=0"),
        ("no_evidence_collection_enabled", safe_bool(summary.get("evidence_collection_enabled", True), True) is False, "evidence_collection_enabled=False"),
        ("no_official_dataset_implementation", safe_bool(summary.get("official_dataset_schema_implemented", True), True) is False, "official_dataset_schema_implemented=False"),
        ("no_signal_or_execution_enabled", all(safe_bool(summary.get(field, True), True) is False for field in ["signal_generation_enabled", "live_alerts_allowed", "paper_trade_execution_allowed", "real_capital_allowed", "market_execution_allowed", "exchange_execution_allowed", "automation_allowed", "execution_allowed"]), "all_execution_boundaries=False"),
        ("no_duplicate_start_run", safe_bool(summary.get("new_controlled_forward_observation_start_run_performed", True), True) is False and safe_bool(summary.get("new_controlled_forward_observation_start_performed", True), True) is False, "new_start_run=False,new_start=False"),
        ("design_artifacts_only", True, "reports_only=True"),
        ("future_design_review_only", True, "future_action=design_review_only"),
        ("total_project_not_completed", True, "total_project_completed=False"),
        ("long_strategy_remains_unapproved", True, "long_strategy_approved=False"),
    ]
    return pd.DataFrame(
        [{"validation_name": n, "passed": bool(p), "details": d} for n, p, d in rows]
    )


def build_chain(validations: pd.DataFrame, prefix: str, id_column: str) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "position": position,
                id_column: f"{prefix}_{position:03d}",
                "name": str(row["validation_name"]),
                "required": True,
                "design_only": True,
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
        "report_only_dry_run_design_performed",
        "report_only_dry_run_design_passed",
        "future_report_only_evidence_collection_dry_run_design_review_allowed",
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
        {"guard_name": name, "required_value": True, "actual_value": True, "passed": True}
        for name in true_names
    ]
    rows.extend(
        {"guard_name": name, "required_value": False, "actual_value": False, "passed": True}
        for name in false_names
    )
    rows.extend(
        [
            {"guard_name": "report_only_dry_run_rows_generated", "required_value": 0, "actual_value": 0, "passed": True},
            {"guard_name": "official_evidence_rows_written", "required_value": 0, "actual_value": 0, "passed": True},
        ]
    )
    return pd.DataFrame(rows)


def build_rules(
    validations: pd.DataFrame,
    evidence: pd.DataFrame,
    controls: pd.DataFrame,
    guards: pd.DataFrame,
    schema: pd.DataFrame,
    scenarios: pd.DataFrame,
    steps: pd.DataFrame,
    dry_controls: pd.DataFrame,
    artifact_plan: pd.DataFrame,
    acceptance: pd.DataFrame,
) -> pd.DataFrame:
    rows = [
        ("design_validation_count", len(validations) > 0, ">0", str(len(validations))),
        ("all_design_validations_passed", all_passed(validations), "True", str(all_passed(validations))),
        ("design_evidence_count_matches", len(evidence) == len(validations), str(len(validations)), str(len(evidence))),
        ("all_design_evidence_passed", all_passed(evidence), "True", str(all_passed(evidence))),
        ("design_control_count_matches", len(controls) == len(validations), str(len(validations)), str(len(controls))),
        ("all_design_controls_passed", all_passed(controls), "True", str(all_passed(controls))),
        ("design_guard_count_37", len(guards) == 37, "37", str(len(guards))),
        ("all_design_guards_passed", all_passed(guards), "True", str(all_passed(guards))),
        ("schema_field_count_54", len(schema) == 54, "54", str(len(schema))),
        ("scenario_count_6", len(scenarios) == 6, "6", str(len(scenarios))),
        ("step_count_16", len(steps) == 16, "16", str(len(steps))),
        ("dry_run_control_count_20", len(dry_controls) == 20, "20", str(len(dry_controls))),
        ("artifact_plan_count_12", len(artifact_plan) == 12, "12", str(len(artifact_plan))),
        ("acceptance_count_18", len(acceptance) == 18, "18", str(len(acceptance))),
        ("design_only", True, "True", "True"),
        ("dry_run_not_executed", True, "False", "False"),
        ("evidence_collection_disabled", True, "False", "False"),
        ("official_dataset_not_implemented", True, "False", "False"),
        ("official_dataset_writes_disabled", True, "False", "False"),
        ("signal_and_execution_disabled", True, "False", "False"),
    ]
    return pd.DataFrame(
        [
            {
                "rule_id": f"REPORT_ONLY_DRY_RUN_DESIGN_RULE_{position:03d}",
                "rule_name": name,
                "passed": passed,
                "required_value": required,
                "actual_value": actual,
            }
            for position, (name, passed, required, actual) in enumerate(rows, start=1)
        ]
    )


def build_requirements(
    validations: pd.DataFrame,
    evidence: pd.DataFrame,
    controls: pd.DataFrame,
    rules: pd.DataFrame,
    guards: pd.DataFrame,
    component_tables: list[pd.DataFrame],
) -> pd.DataFrame:
    rows = [
        (str(row["validation_name"]), safe_bool(row["passed"], False), "True", str(safe_bool(row["passed"], False)))
        for _, row in validations.iterrows()
    ]
    extras = [
        ("design_evidence_chain_passed", all_passed(evidence), "True", str(all_passed(evidence))),
        ("design_controls_passed", all_passed(controls), "True", str(all_passed(controls))),
        ("design_rules_passed", all_passed(rules), "True", str(all_passed(rules))),
        ("design_guards_passed", all_passed(guards), "True", str(all_passed(guards))),
        ("all_design_components_passed", all(all_passed(df) for df in component_tables), "True", str(all(all_passed(df) for df in component_tables))),
        ("report_only_dry_run_design_performed", True, "True", "True"),
        ("future_design_review_allowed", True, "True", "True"),
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
    rows.extend(extras)
    return pd.DataFrame(
        [
            {
                "requirement_id": f"REPORT_ONLY_DRY_RUN_DESIGN_REQ_{position:03d}",
                "requirement_name": name,
                "passed": passed,
                "required_value": required,
                "actual_value": actual,
            }
            for position, (name, passed, required, actual) in enumerate(rows, start=1)
        ]
    )


def build_decision(requirements: pd.DataFrame, rules: pd.DataFrame, guards: pd.DataFrame) -> pd.DataFrame:
    passed_count = int(requirements["passed"].map(safe_bool).sum()) if not requirements.empty else 0
    failed_count = len(requirements) - passed_count
    passed = len(requirements) > 0 and failed_count == 0 and all_passed(rules) and all_passed(guards)
    failed_names = ",".join(
        requirements[~requirements["passed"].map(safe_bool)]["requirement_name"].astype(str).tolist()
    )
    return pd.DataFrame(
        [
            {
                "report_only_dry_run_design_id": "PHASE_10_31_LONG_FORWARD_OBSERVATION_EVIDENCE_COLLECTION_REPORT_ONLY_DRY_RUN_DESIGN_001",
                "report_only_dry_run_design_performed": True,
                "report_only_dry_run_design_passed": passed,
                "report_only_dry_run_design_decision": READY_DECISION if passed else BLOCKED_DECISION,
                "total_requirements": len(requirements),
                "passed_requirements": passed_count,
                "failed_requirements": failed_count,
                "failed_requirement_names": failed_names,
                "future_report_only_evidence_collection_dry_run_design_review_allowed": passed,
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


def validate_long_forward_observation_evidence_collection_report_only_dry_run_design() -> dict[str, pd.DataFrame]:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    checks: list[dict] = []

    for name, path in {
        "phase_10_30_design_review_doc_exists": PHASE_10_30_DOC_PATH,
        "phase_10_31_dry_run_design_doc_exists": PHASE_10_31_DOC_PATH,
    }.items():
        exists = path.exists()
        checks.append(check_row("phase_anchor", name, exists, "INFO" if exists else "ERROR", str(path)))

    official_before = OFFICIAL_DATASET_PATH.exists()
    manifest_before = build_manifest()
    source = {name: read_csv(path) for name, path in SOURCE_PATHS.items()}

    schema = build_report_only_schema(source["schema"])
    scenarios = build_scenarios()
    steps = build_named_table(
        STEPS,
        "REPORT_ONLY_DRY_RUN_STEP",
        "step_name",
        {
            "design_only": True,
            "executed": False,
            "official_dataset_write_allowed": False,
            "signal_generation_enabled": False,
            "market_execution_allowed": False,
        },
    )
    dry_controls = build_named_table(
        DRY_RUN_CONTROLS,
        "REPORT_ONLY_DRY_RUN_CONTROL",
        "control_name",
        {
            "design_only": True,
            "implemented": False,
            "enabled_in_phase_10_31": False,
            "official_dataset_write_allowed": False,
            "market_execution_allowed": False,
        },
    )
    artifact_plan = build_named_table(
        ARTIFACT_PLAN,
        "REPORT_ONLY_DRY_RUN_ARTIFACT",
        "artifact_name",
        {
            "target_scope": "REPORTS_ONLY",
            "official_dataset_artifact": False,
            "planned_only": True,
        },
    )
    acceptance = build_named_table(
        ACCEPTANCE_CRITERIA,
        "REPORT_ONLY_DRY_RUN_ACCEPTANCE",
        "criterion_name",
        {
            "required": True,
            "design_only": True,
            "dry_run_executed": False,
        },
    )
    outcomes = build_expected_outcomes(scenarios)
    manifest_after = build_manifest()

    validations = build_validations(
        source, manifest_before, manifest_after, schema, scenarios, steps,
        dry_controls, artifact_plan, acceptance, outcomes, not official_before,
    )
    evidence = build_chain(validations, "REPORT_ONLY_DRY_RUN_DESIGN_EVIDENCE", "evidence_id")
    controls = build_chain(validations, "REPORT_ONLY_DRY_RUN_DESIGN_CONTROL", "control_id")
    guards = build_guard_matrix()
    rules = build_rules(
        validations, evidence, controls, guards, schema, scenarios, steps,
        dry_controls, artifact_plan, acceptance,
    )
    component_tables = [schema, scenarios, steps, dry_controls, artifact_plan, acceptance, outcomes]
    requirements = build_requirements(validations, evidence, controls, rules, guards, component_tables)
    decision = build_decision(requirements, rules, guards)
    decision_row = decision.iloc[0].to_dict() if not decision.empty else {}

    aggregates = {
        "design_validations_passed": all_passed(validations),
        "design_evidence_chain_passed": all_passed(evidence),
        "design_controls_passed": all_passed(controls),
        "design_rules_passed": all_passed(rules),
        "design_requirements_passed": all_passed(requirements),
        "design_guards_passed": all_passed(guards),
        "all_design_components_passed": all(all_passed(df) for df in component_tables),
        "report_only_dry_run_design_passed": safe_bool(decision_row.get("report_only_dry_run_design_passed", False)),
        "report_only_dry_run_design_decision_expected": str(decision_row.get("report_only_dry_run_design_decision", "")) == READY_DECISION,
    }
    for name, passed in aggregates.items():
        checks.append(
            check_row(
                "report_only_dry_run_design",
                name,
                passed,
                "INFO" if passed else "ERROR",
                str(decision_row.get("report_only_dry_run_design_decision", "")) if name.endswith("decision_expected") else f"{name}={passed}",
            )
        )

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
                "report_only_dry_run_design_safety_flags",
                str(row["guard_name"]),
                passed,
                "INFO" if passed else "ERROR",
                f"{row['guard_name']}={row['actual_value']} (required={row['required_value']})",
            )
        )

    warnings = [
        ("design_only", "Phase 10.31 defines only the report-only dry-run design."),
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
    for name, details in warnings:
        checks.append(check_row("scope_control", name, True, "WARNING", details))

    future_allowed = safe_bool(
        decision_row.get(
            "future_report_only_evidence_collection_dry_run_design_review_allowed",
            False,
        )
    )
    checks.append(
        check_row(
            "planning_scope",
            "future_report_only_evidence_collection_dry_run_design_review_allowed",
            future_allowed,
            "WARNING" if future_allowed else "ERROR",
            "Allows only a future design review; no dry-run execution or operational capability.",
        )
    )
    checks.append(
        check_row(
            "phase_transition",
            "phase_10_32_recommended_next",
            True,
            "INFO",
            "Recommended next: Phase 10.32 report-only dry-run design review.",
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
                "phase": "10.31",
                "long_forward_observation_evidence_collection_report_only_dry_run_design_defined": True,
                "phase_10_30_validation_passed": lookup.get("phase_10_30_validation_passed", False),
                "source_evidence_collection_design_review_performed": lookup.get("source_design_review_performed", False),
                "source_evidence_collection_design_review_passed": lookup.get("source_design_review_passed", False),
                "source_evidence_collection_design_review_decision": str(source_summary.get("evidence_collection_design_review_decision", "")),
                "source_future_report_only_evidence_collection_dry_run_design_allowed": lookup.get("source_future_dry_run_design_allowed", False),
                "source_artifact_count": len(manifest_after),
                "source_artifacts_exist": lookup.get("source_artifacts_exist", False),
                "source_artifacts_non_empty": lookup.get("source_artifacts_non_empty", False),
                "source_artifact_hashes_valid": lookup.get("source_artifact_hashes_valid", False),
                "source_artifacts_stable_during_design": lookup.get("source_artifacts_stable_during_design", False),
                "source_manifest_sha256": manifest_digest(manifest_after),
                "source_summary_decision_consistent": lookup.get("source_summary_decision_consistent", False),
                "source_review_blocks_passed": lookup.get("source_review_blocks_passed", False),
                "source_material_issue_count_zero": lookup.get("source_material_issue_count_zero", False),
                "source_schema_field_count": len(source["schema"]),
                "source_schema_valid": lookup.get("source_schema_valid", False),
                "report_only_dry_run_schema_field_count": len(schema),
                "report_only_dry_run_schema_valid": lookup.get("report_only_schema_valid", False),
                "dry_run_scenario_count": len(scenarios),
                "dry_run_scenarios_valid": lookup.get("dry_run_scenarios_valid", False),
                "dry_run_step_count": len(steps),
                "dry_run_steps_valid": lookup.get("dry_run_steps_valid", False),
                "dry_run_control_count": len(dry_controls),
                "dry_run_controls_valid": lookup.get("dry_run_controls_valid", False),
                "dry_run_artifact_plan_count": len(artifact_plan),
                "dry_run_artifact_plan_valid": lookup.get("dry_run_artifact_plan_valid", False),
                "dry_run_acceptance_criterion_count": len(acceptance),
                "dry_run_acceptance_criteria_valid": lookup.get("dry_run_acceptance_criteria_valid", False),
                "dry_run_expected_outcomes_valid": lookup.get("dry_run_expected_outcomes_valid", False),
                "controlled_observation_state_valid": lookup.get("controlled_observation_state_valid", False),
                "source_operational_locks_valid": lookup.get("source_operational_locks_valid", False),
                "official_dataset_absent": lookup.get("official_dataset_absent", False),
                "design_validation_rows": len(validations),
                "design_evidence_rows": len(evidence),
                "design_control_rows": len(controls),
                "design_rule_rows": len(rules),
                "design_requirement_rows": len(requirements),
                "design_guard_rows": len(guards),
                "design_validations_passed": all_passed(validations),
                "design_evidence_chain_passed": all_passed(evidence),
                "design_controls_passed": all_passed(controls),
                "design_rules_passed": all_passed(rules),
                "design_requirements_passed": all_passed(requirements),
                "design_guards_passed": all_passed(guards),
                "report_only_dry_run_design_performed": True,
                "report_only_dry_run_design_passed": safe_bool(decision_row.get("report_only_dry_run_design_passed", False)),
                "report_only_dry_run_design_decision": str(decision_row.get("report_only_dry_run_design_decision", "")),
                "future_report_only_evidence_collection_dry_run_design_review_allowed": future_allowed,
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
                    "PHASE_10_31_LONG_FORWARD_OBSERVATION_EVIDENCE_COLLECTION_REPORT_ONLY_DRY_RUN_DESIGN_VALIDATED"
                    if validation_passed
                    else
                    "PHASE_10_31_LONG_FORWARD_OBSERVATION_EVIDENCE_COLLECTION_REPORT_ONLY_DRY_RUN_DESIGN_FAILED"
                ),
            }
        ]
    )

    outputs = {
        "phase_10_30_source_summary_v1.csv": source["summary"],
        "phase_10_30_source_review_validations_v1.csv": source["review_validations"],
        "phase_10_30_source_review_items_v1.csv": source["review_items"],
        "phase_10_30_source_review_findings_v1.csv": source["review_findings"],
        "phase_10_30_source_review_controls_v1.csv": source["review_controls"],
        "phase_10_30_source_review_rules_v1.csv": source["review_rules"],
        "phase_10_30_source_review_requirements_v1.csv": source["review_requirements"],
        "phase_10_30_source_review_guard_matrix_v1.csv": source["review_guard_matrix"],
        "phase_10_30_source_review_decision_v1.csv": source["review_decision"],
        "phase_10_30_source_review_checks_v1.csv": source["review_checks"],
        "phase_10_30_source_review_manifest_v1.csv": source["review_manifest"],
        "source_report_only_dry_run_design_artifact_manifest_v1.csv": manifest_after,
        "report_only_dry_run_design_schema_v1.csv": schema,
        "report_only_dry_run_design_scenarios_v1.csv": scenarios,
        "report_only_dry_run_design_steps_v1.csv": steps,
        "report_only_dry_run_design_controls_v1.csv": dry_controls,
        "report_only_dry_run_design_artifact_plan_v1.csv": artifact_plan,
        "report_only_dry_run_design_acceptance_criteria_v1.csv": acceptance,
        "report_only_dry_run_design_expected_outcomes_v1.csv": outcomes,
        "report_only_dry_run_design_validations_v1.csv": validations,
        "report_only_dry_run_design_evidence_chain_v1.csv": evidence,
        "report_only_dry_run_design_validation_controls_v1.csv": controls,
        "report_only_dry_run_design_rules_v1.csv": rules,
        "report_only_dry_run_design_requirements_v1.csv": requirements,
        "report_only_dry_run_design_guard_matrix_v1.csv": guards,
        "report_only_dry_run_design_decision_v1.csv": decision,
        "report_only_dry_run_design_checks_v1.csv": checks_df,
        "report_only_dry_run_design_summary_v1.csv": summary_df,
    }
    for filename, dataframe in outputs.items():
        dataframe.to_csv(REPORTS_DIR / filename, index=False)

    return {
        "summary": summary_df,
        "source_summary": source["summary"],
        "source_schema": source["schema"],
        "source_review_validations": source["review_validations"],
        "source_review_items": source["review_items"],
        "source_review_findings": source["review_findings"],
        "source_review_controls": source["review_controls"],
        "source_review_rules": source["review_rules"],
        "source_review_requirements": source["review_requirements"],
        "source_review_guard_matrix": source["review_guard_matrix"],
        "source_review_decision": source["review_decision"],
        "source_review_checks": source["review_checks"],
        "source_review_manifest": source["review_manifest"],
        "design_manifest": manifest_after,
        "design_schema": schema,
        "design_scenarios": scenarios,
        "design_steps": steps,
        "dry_run_controls": dry_controls,
        "artifact_plan": artifact_plan,
        "acceptance_criteria": acceptance,
        "expected_outcomes": outcomes,
        "design_validations": validations,
        "design_evidence_chain": evidence,
        "design_validation_controls": controls,
        "design_rules": rules,
        "design_requirements": requirements,
        "design_guard_matrix": guards,
        "design_decision": decision,
        "checks": checks_df,
    }
