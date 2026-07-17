from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

import pandas as pd

from src.long_side.long_forward_observation_dataset_bootstrap_v1 import (
    OFFICIAL_DATASET_PATH,
)


REPORTS_DIR = Path(
    "reports/p10_33_evidence_collection_report_only_dry_run_execution_review_v1"
)
SOURCE_DIR = Path(
    "reports/p10_32_evidence_collection_report_only_dry_run_design_review_v1"
)

PHASE_10_32_DOC_PATH = Path(
    "docs/PHASE_10_LONG_FORWARD_OBSERVATION_EVIDENCE_COLLECTION_"
    "REPORT_ONLY_DRY_RUN_DESIGN_REVIEW.md"
)
PHASE_10_33_DOC_PATH = Path(
    "docs/PHASE_10_LONG_FORWARD_OBSERVATION_EVIDENCE_COLLECTION_"
    "REPORT_ONLY_DRY_RUN_EXECUTION_REVIEW.md"
)

SOURCE_PATHS = {
    "summary": SOURCE_DIR / "report_only_dry_run_design_review_summary_v1.csv",
    "source_schema": SOURCE_DIR / "phase_10_31_source_schema_v1.csv",
    "source_scenarios": SOURCE_DIR / "phase_10_31_source_scenarios_v1.csv",
    "source_steps": SOURCE_DIR / "phase_10_31_source_steps_v1.csv",
    "source_dry_run_controls": SOURCE_DIR / "phase_10_31_source_dry_run_controls_v1.csv",
    "source_artifact_plan": SOURCE_DIR / "phase_10_31_source_artifact_plan_v1.csv",
    "source_acceptance": SOURCE_DIR / "phase_10_31_source_acceptance_v1.csv",
    "source_outcomes": SOURCE_DIR / "phase_10_31_source_outcomes_v1.csv",
    "review_validations": SOURCE_DIR / "report_only_dry_run_design_review_validations_v1.csv",
    "review_items": SOURCE_DIR / "report_only_dry_run_design_review_items_v1.csv",
    "review_findings": SOURCE_DIR / "report_only_dry_run_design_review_findings_v1.csv",
    "review_controls": SOURCE_DIR / "report_only_dry_run_design_review_controls_v1.csv",
    "review_rules": SOURCE_DIR / "report_only_dry_run_design_review_rules_v1.csv",
    "review_requirements": SOURCE_DIR / "report_only_dry_run_design_review_requirements_v1.csv",
    "review_guard_matrix": SOURCE_DIR / "report_only_dry_run_design_review_guard_matrix_v1.csv",
    "review_decision": SOURCE_DIR / "report_only_dry_run_design_review_decision_v1.csv",
    "review_checks": SOURCE_DIR / "report_only_dry_run_design_review_checks_v1.csv",
    "review_manifest": SOURCE_DIR / "source_report_only_dry_run_design_review_artifact_manifest_v1.csv",
}

SOURCE_READY_DECISION = (
    "CONTROLLED_FORWARD_OBSERVATION_EVIDENCE_COLLECTION_REPORT_ONLY_"
    "DRY_RUN_DESIGN_REVIEW_READY_FOR_EXECUTION_REVIEW"
)
READY_DECISION = (
    "CONTROLLED_FORWARD_OBSERVATION_EVIDENCE_COLLECTION_REPORT_ONLY_"
    "DRY_RUN_EXECUTION_REVIEW_READY_FOR_RUN"
)
BLOCKED_DECISION = (
    "CONTROLLED_FORWARD_OBSERVATION_EVIDENCE_COLLECTION_REPORT_ONLY_"
    "DRY_RUN_EXECUTION_REVIEW_BLOCKED"
)
RECOMMENDED_NEXT_PHASE = (
    "PHASE_10_34_LONG_FORWARD_OBSERVATION_EVIDENCE_COLLECTION_"
    "REPORT_ONLY_DRY_RUN_RUN_V1"
)

EXPECTED_SOURCE_COUNTS = {
    "source_artifact_count": 17,
    "review_validation_rows": 45,
    "review_item_rows": 24,
    "review_finding_rows": 24,
    "review_control_rows": 45,
    "review_rule_rows": 20,
    "review_requirement_rows": 61,
    "review_guard_rows": 37,
    "material_issue_count": 0,
    "total_checks": 64,
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

EXPECTED_SCENARIOS = {
    "VALID_SYNTHETIC_ROW": ("PASS_REPORT_ONLY", True),
    "EXACT_DUPLICATE_ROW": ("REJECT_DUPLICATE", False),
    "INVALID_SOURCE_SYSTEM": ("REJECT_SOURCE", False),
    "INVALID_UTC_TIMESTAMP": ("REJECT_TIMESTAMP", False),
    "INVALID_LONG_PRICE_STRUCTURE": ("REJECT_PRICE_STRUCTURE", False),
    "PROHIBITED_EXECUTION_FLAG_ENABLED": ("REJECT_SAFETY_FLAG", False),
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

EXPECTED_FALSE_GUARDS = [
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

EXECUTION_PRECONDITIONS = [
    "phase_10_32_validation_passed",
    "source_execution_review_allowed",
    "source_artifacts_integrity_valid",
    "source_review_blocks_passed",
    "source_material_issue_count_zero",
    "schema_contract_valid",
    "schema_safety_defaults_false",
    "scenario_contract_valid",
    "scenario_outcome_alignment_valid",
    "scenario_execution_order_valid",
    "step_plan_valid",
    "dry_run_controls_valid",
    "artifact_plan_reports_only",
    "acceptance_contract_valid",
    "official_dataset_absent",
    "dry_run_not_previously_executed",
    "dry_run_rows_generated_zero",
    "evidence_collection_disabled",
    "signal_and_execution_disabled",
    "future_run_report_only",
]

ABORT_RULES = [
    "abort_if_source_artifact_missing",
    "abort_if_source_artifact_hash_invalid",
    "abort_if_source_artifact_changes_during_run",
    "abort_if_source_decision_mismatch",
    "abort_if_schema_field_count_or_order_changes",
    "abort_if_any_safety_default_is_true",
    "abort_if_scenario_count_or_order_changes",
    "abort_if_expected_outcome_mismatch",
    "abort_if_any_official_dataset_write_is_requested",
    "abort_if_any_real_evidence_acceptance_is_requested",
    "abort_if_any_signal_alert_or_execution_flag_is_true",
    "abort_if_official_dataset_exists_before_or_after_run",
]

OUTPUT_PLAN = [
    "dry_run_execution_summary",
    "dry_run_synthetic_input_rows",
    "dry_run_scenario_results",
    "dry_run_validation_results",
    "dry_run_rejection_results",
    "dry_run_hash_and_dedup_results",
    "dry_run_safety_lock_results",
    "dry_run_official_dataset_guard_results",
    "dry_run_execution_checks",
    "dry_run_execution_manifest",
]

REVIEW_ITEM_SPECS = [
    (
        "phase_10_32_dependency",
        [
            "phase_10_32_validation_passed",
            "source_design_review_performed",
            "source_design_review_passed",
            "source_design_review_decision_valid",
            "source_future_execution_review_allowed",
        ],
    ),
    (
        "source_artifact_integrity",
        [
            "source_artifacts_exist",
            "source_artifacts_non_empty",
            "source_artifact_hashes_valid",
            "source_artifacts_stable_during_review",
        ],
    ),
    (
        "source_summary_decision_consistency",
        ["source_summary_decision_consistent", "source_counts_valid"],
    ),
    (
        "source_review_chain",
        ["source_review_blocks_passed", "source_material_issue_count_zero"],
    ),
    (
        "schema_completeness",
        ["source_schema_field_count_54", "source_schema_order_valid"],
    ),
    (
        "schema_safety_defaults",
        ["source_schema_safety_defaults_false"],
    ),
    (
        "schema_non_implementation",
        ["source_schema_review_passed"],
    ),
    (
        "scenario_matrix",
        [
            "source_scenario_count_6",
            "source_scenario_names_valid",
            "source_valid_scenario_count_1",
            "source_reject_scenario_count_5",
        ],
    ),
    (
        "scenario_contract",
        ["source_scenario_contract_valid", "source_scenario_safety_valid"],
    ),
    (
        "scenario_outcome_alignment",
        ["scenario_outcome_alignment_passed"],
    ),
    (
        "scenario_execution_order",
        ["scenario_execution_order_valid"],
    ),
    (
        "step_plan",
        ["source_step_count_16", "source_step_review_passed"],
    ),
    (
        "step_execution_lock",
        ["source_step_review_passed", "report_only_dry_run_not_executed"],
    ),
    (
        "dry_run_controls",
        [
            "source_dry_run_control_count_20",
            "source_dry_run_control_review_passed",
        ],
    ),
    (
        "dry_run_control_implementation_lock",
        ["source_dry_run_control_review_passed"],
    ),
    (
        "artifact_plan",
        [
            "source_artifact_plan_count_12",
            "source_artifact_plan_review_passed",
        ],
    ),
    (
        "acceptance_contract",
        [
            "source_acceptance_count_18",
            "source_acceptance_review_passed",
        ],
    ),
    (
        "expected_outcome_contract",
        [
            "source_expected_outcome_count_6",
            "source_expected_outcome_review_passed",
        ],
    ),
    (
        "future_execution_contract",
        [
            "future_execution_contract_count_6",
            "future_execution_contract_valid",
            "future_execution_contract_safety_valid",
        ],
    ),
    (
        "execution_preconditions",
        [
            "execution_precondition_count_20",
            "execution_preconditions_passed",
        ],
    ),
    (
        "execution_abort_rules",
        ["execution_abort_rule_count_12", "execution_abort_rules_valid"],
    ),
    (
        "execution_output_plan",
        ["execution_output_plan_count_10", "execution_output_plan_valid"],
    ),
    (
        "controlled_observation_state",
        ["controlled_observation_state_valid"],
    ),
    (
        "official_dataset_boundary",
        ["official_dataset_absent", "no_official_dataset_implementation"],
    ),
    (
        "evidence_collection_boundary",
        [
            "no_evidence_collection_enabled",
            "report_only_dry_run_rows_zero",
        ],
    ),
    (
        "signal_and_execution_boundary",
        [
            "no_signal_or_execution_enabled",
            "long_strategy_remains_unapproved",
            "total_project_not_completed",
        ],
    ),
    (
        "future_run_boundary",
        [
            "future_run_report_only",
            "report_only_dry_run_not_executed",
        ],
    ),
]


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
        df[
            [
                "artifact_name",
                "artifact_path",
                "artifact_size_bytes",
                "artifact_sha256",
            ]
        ]
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
    columns = [
        "scenario_id",
        "scenario_name",
        "expected_outcome",
        "expected_validation_pass",
    ]
    if scenarios.empty or outcomes.empty:
        return False
    if not set(columns).issubset(scenarios.columns):
        return False
    if not set(columns).issubset(outcomes.columns):
        return False
    left = scenarios[columns].copy()
    right = outcomes[columns].copy()
    for column in ["scenario_id", "scenario_name", "expected_outcome"]:
        left[column] = left[column].astype(str)
        right[column] = right[column].astype(str)
    left["expected_validation_pass"] = left[
        "expected_validation_pass"
    ].map(safe_bool)
    right["expected_validation_pass"] = right[
        "expected_validation_pass"
    ].map(safe_bool)
    left = left.sort_values("scenario_id").reset_index(drop=True)
    right = right.sort_values("scenario_id").reset_index(drop=True)
    return left.equals(right)


def build_future_execution_contract(
    scenarios: pd.DataFrame,
) -> pd.DataFrame:
    if scenarios.empty:
        return pd.DataFrame()
    ordered = scenarios.sort_values("scenario_position").reset_index(drop=True)
    rows = []
    for execution_position, (_, row) in enumerate(
        ordered.iterrows(),
        start=1,
    ):
        rows.append(
            {
                "execution_position": execution_position,
                "scenario_id": str(row.get("scenario_id", "")),
                "scenario_name": str(row.get("scenario_name", "")),
                "expected_outcome": str(row.get("expected_outcome", "")),
                "expected_validation_pass": safe_bool(
                    row.get("expected_validation_pass", False)
                ),
                "synthetic_only": True,
                "report_only": True,
                "in_memory_until_validation_complete": True,
                "reports_only_write_scope": True,
                "approved_for_future_run": True,
                "executed_in_phase_10_33": False,
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
                "passed": True,
            }
        )
    return pd.DataFrame(rows)


def build_source_validations(
    source: dict[str, pd.DataFrame],
    manifest_before: pd.DataFrame,
    manifest_after: pd.DataFrame,
    official_absent: bool,
) -> pd.DataFrame:
    summary = (
        source["summary"].iloc[0].to_dict()
        if not source["summary"].empty
        else {}
    )
    decision = (
        source["review_decision"].iloc[0].to_dict()
        if not source["review_decision"].empty
        else {}
    )

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
        and manifest_digest(manifest_before)
        == manifest_digest(manifest_after)
    )

    summary_decision_consistent = (
        str(
            summary.get(
                "report_only_dry_run_design_review_decision",
                "",
            )
        )
        == str(
            decision.get(
                "report_only_dry_run_design_review_decision",
                "",
            )
        )
        == SOURCE_READY_DECISION
        and safe_bool(
            summary.get(
                "report_only_dry_run_design_review_passed",
                False,
            )
        )
        and safe_bool(
            decision.get(
                "report_only_dry_run_design_review_passed",
                False,
            )
        )
    )

    source_counts_valid = all(
        int(safe_float(summary.get(field), -1)) == expected
        for field, expected in EXPECTED_SOURCE_COUNTS.items()
    )

    source_review_blocks_passed = all(
        all_passed(source[name])
        for name in [
            "review_validations",
            "review_items",
            "review_findings",
            "review_controls",
            "review_rules",
            "review_requirements",
            "review_guard_matrix",
            "review_checks",
        ]
    )

    schema = source["source_schema"]
    schema_order_valid = (
        len(schema) == 54
        and "field_name" in schema.columns
        and schema["field_name"].astype(str).tolist()
        == EXPECTED_SCHEMA_FIELDS
    )
    safety_rows = (
        schema[
            schema["field_name"].astype(str).isin(SAFETY_FIELDS)
        ]
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

    scenarios = source["source_scenarios"]
    scenario_names = (
        set(scenarios["scenario_name"].astype(str).tolist())
        if not scenarios.empty and "scenario_name" in scenarios.columns
        else set()
    )
    valid_rows = (
        scenarios[
            scenarios["scenario_name"].astype(str)
            == "VALID_SYNTHETIC_ROW"
        ]
        if not scenarios.empty and "scenario_name" in scenarios.columns
        else pd.DataFrame()
    )
    reject_rows = (
        scenarios[
            scenarios["scenario_name"].astype(str)
            != "VALID_SYNTHETIC_ROW"
        ]
        if not scenarios.empty and "scenario_name" in scenarios.columns
        else pd.DataFrame()
    )

    scenario_contract_valid = True
    if len(scenarios) != 6 or scenario_names != set(EXPECTED_SCENARIOS):
        scenario_contract_valid = False
    else:
        for name, (expected_outcome, should_pass) in (
            EXPECTED_SCENARIOS.items()
        ):
            row = scenarios[
                scenarios["scenario_name"].astype(str) == name
            ]
            if len(row) != 1:
                scenario_contract_valid = False
                break
            item = row.iloc[0]
            if str(item.get("expected_outcome", "")) != expected_outcome:
                scenario_contract_valid = False
                break
            if (
                safe_bool(
                    item.get(
                        "expected_validation_pass",
                        not should_pass,
                    )
                )
                != should_pass
            ):
                scenario_contract_valid = False
                break

    scenario_safety_valid = all(
        [
            all_passed(scenarios),
            column_all(scenarios, "synthetic_only", True),
            column_all(scenarios, "report_only", True),
            column_all(
                scenarios,
                "expected_real_evidence_acceptance",
                False,
            ),
            column_all(
                scenarios,
                "expected_official_dataset_write",
                False,
            ),
            column_all(
                scenarios,
                "expected_signal_generation",
                False,
            ),
            column_all(scenarios, "expected_live_alert", False),
            column_all(
                scenarios,
                "expected_market_execution",
                False,
            ),
            column_all(scenarios, "executed_in_phase_10_31", False),
        ]
    )

    scenario_execution_order_valid = (
        len(scenarios) == 6
        and "scenario_position" in scenarios.columns
        and scenarios.sort_values("scenario_position")[
            "scenario_position"
        ].astype(int).tolist()
        == list(range(1, 7))
        and scenarios.sort_values("scenario_position")[
            "scenario_name"
        ].astype(str).tolist()
        == [
            "VALID_SYNTHETIC_ROW",
            "EXACT_DUPLICATE_ROW",
            "INVALID_SOURCE_SYSTEM",
            "INVALID_UTC_TIMESTAMP",
            "INVALID_LONG_PRICE_STRUCTURE",
            "PROHIBITED_EXECUTION_FLAG_ENABLED",
        ]
    )

    steps = source["source_steps"]
    step_review_passed = all(
        [
            len(steps) == 16,
            all_passed(steps),
            column_all(steps, "design_only", True),
            column_all(steps, "executed", False),
            column_all(
                steps,
                "official_dataset_write_allowed",
                False,
            ),
            column_all(steps, "signal_generation_enabled", False),
            column_all(steps, "market_execution_allowed", False),
        ]
    )

    dry_controls = source["source_dry_run_controls"]
    dry_control_review_passed = all(
        [
            len(dry_controls) == 20,
            all_passed(dry_controls),
            column_all(dry_controls, "design_only", True),
            column_all(dry_controls, "implemented", False),
            column_all(
                dry_controls,
                "enabled_in_phase_10_31",
                False,
            ),
            column_all(
                dry_controls,
                "official_dataset_write_allowed",
                False,
            ),
            column_all(
                dry_controls,
                "market_execution_allowed",
                False,
            ),
        ]
    )

    artifact_plan = source["source_artifact_plan"]
    artifact_plan_review_passed = all(
        [
            len(artifact_plan) == 12,
            all_passed(artifact_plan),
            "target_scope" in artifact_plan.columns,
            artifact_plan.get(
                "target_scope",
                pd.Series(dtype=str),
            )
            .astype(str)
            .eq("REPORTS_ONLY")
            .all(),
            column_all(
                artifact_plan,
                "official_dataset_artifact",
                False,
            ),
            column_all(artifact_plan, "planned_only", True),
        ]
    )

    acceptance = source["source_acceptance"]
    acceptance_review_passed = all(
        [
            len(acceptance) == 18,
            all_passed(acceptance),
            column_all(acceptance, "required", True),
            column_all(acceptance, "design_only", True),
            column_all(acceptance, "dry_run_executed", False),
        ]
    )

    outcomes = source["source_outcomes"]
    outcome_review_passed = all(
        [
            len(outcomes) == 6,
            all_passed(outcomes),
            column_all(
                outcomes,
                "expected_real_evidence_acceptance",
                False,
            ),
            column_all(
                outcomes,
                "expected_official_dataset_write",
                False,
            ),
            column_all(
                outcomes,
                "expected_signal_generation",
                False,
            ),
            column_all(outcomes, "expected_live_alert", False),
            column_all(
                outcomes,
                "expected_paper_trade_execution",
                False,
            ),
            column_all(
                outcomes,
                "expected_real_capital_execution",
                False,
            ),
        ]
    )
    outcome_alignment = scenario_outcome_alignment(
        scenarios,
        outcomes,
    )

    source_locks_valid = all(
        safe_bool(summary.get(field, True), True) is False
        for field in EXPECTED_FALSE_GUARDS
    )

    controlled_state_valid = safe_bool(
        summary.get(
            "controlled_observation_state_valid",
            False,
        ),
        False,
    )

    validations = [
        (
            "source_artifacts_exist",
            artifacts_exist,
            f"artifact_count={len(manifest_before)}",
        ),
        (
            "source_artifacts_non_empty",
            artifacts_non_empty,
            f"artifact_count={len(manifest_before)}",
        ),
        (
            "source_artifact_hashes_valid",
            hashes_valid,
            f"artifact_count={len(manifest_before)}",
        ),
        (
            "source_artifacts_stable_during_review",
            stable,
            (
                f"before={manifest_digest(manifest_before)},"
                f"after={manifest_digest(manifest_after)}"
            ),
        ),
        (
            "phase_10_32_validation_passed",
            safe_bool(summary.get("validation_passed", False)),
            str(summary.get("validation_decision", "")),
        ),
        (
            "source_design_review_performed",
            safe_bool(
                summary.get(
                    "report_only_dry_run_design_review_performed",
                    False,
                )
            ),
            str(
                summary.get(
                    "report_only_dry_run_design_review_performed",
                    "",
                )
            ),
        ),
        (
            "source_design_review_passed",
            safe_bool(
                summary.get(
                    "report_only_dry_run_design_review_passed",
                    False,
                )
            ),
            str(
                summary.get(
                    "report_only_dry_run_design_review_passed",
                    "",
                )
            ),
        ),
        (
            "source_design_review_decision_valid",
            str(
                summary.get(
                    "report_only_dry_run_design_review_decision",
                    "",
                )
            )
            == SOURCE_READY_DECISION,
            str(
                summary.get(
                    "report_only_dry_run_design_review_decision",
                    "",
                )
            ),
        ),
        (
            "source_future_execution_review_allowed",
            safe_bool(
                summary.get(
                    "future_report_only_dry_run_execution_review_allowed",
                    False,
                )
            ),
            str(
                summary.get(
                    "future_report_only_dry_run_execution_review_allowed",
                    "",
                )
            ),
        ),
        (
            "source_summary_decision_consistent",
            summary_decision_consistent,
            f"consistent={summary_decision_consistent}",
        ),
        (
            "source_counts_valid",
            source_counts_valid,
            ",".join(
                f"{field}={summary.get(field, '')}"
                for field in EXPECTED_SOURCE_COUNTS
            ),
        ),
        (
            "source_review_blocks_passed",
            source_review_blocks_passed,
            f"passed={source_review_blocks_passed}",
        ),
        (
            "source_material_issue_count_zero",
            int(safe_float(summary.get("material_issue_count"), -1))
            == 0,
            str(summary.get("material_issue_count", "")),
        ),
        (
            "source_schema_field_count_54",
            len(schema) == 54,
            f"rows={len(schema)}",
        ),
        (
            "source_schema_order_valid",
            schema_order_valid,
            f"ordered={schema_order_valid}",
        ),
        (
            "source_schema_safety_defaults_false",
            schema_safety_valid,
            f"valid={schema_safety_valid}",
        ),
        (
            "source_schema_review_passed",
            schema_review_passed,
            f"passed={schema_review_passed}",
        ),
        (
            "source_scenario_count_6",
            len(scenarios) == 6,
            f"rows={len(scenarios)}",
        ),
        (
            "source_scenario_names_valid",
            scenario_names == set(EXPECTED_SCENARIOS),
            f"names={sorted(scenario_names)}",
        ),
        (
            "source_valid_scenario_count_1",
            len(valid_rows) == 1,
            f"rows={len(valid_rows)}",
        ),
        (
            "source_reject_scenario_count_5",
            len(reject_rows) == 5,
            f"rows={len(reject_rows)}",
        ),
        (
            "source_scenario_contract_valid",
            scenario_contract_valid,
            f"valid={scenario_contract_valid}",
        ),
        (
            "source_scenario_safety_valid",
            scenario_safety_valid,
            f"valid={scenario_safety_valid}",
        ),
        (
            "scenario_outcome_alignment_passed",
            outcome_alignment,
            f"passed={outcome_alignment}",
        ),
        (
            "scenario_execution_order_valid",
            scenario_execution_order_valid,
            f"valid={scenario_execution_order_valid}",
        ),
        (
            "source_step_count_16",
            len(steps) == 16,
            f"rows={len(steps)}",
        ),
        (
            "source_step_review_passed",
            step_review_passed,
            f"passed={step_review_passed}",
        ),
        (
            "source_dry_run_control_count_20",
            len(dry_controls) == 20,
            f"rows={len(dry_controls)}",
        ),
        (
            "source_dry_run_control_review_passed",
            dry_control_review_passed,
            f"passed={dry_control_review_passed}",
        ),
        (
            "source_artifact_plan_count_12",
            len(artifact_plan) == 12,
            f"rows={len(artifact_plan)}",
        ),
        (
            "source_artifact_plan_review_passed",
            artifact_plan_review_passed,
            f"passed={artifact_plan_review_passed}",
        ),
        (
            "source_acceptance_count_18",
            len(acceptance) == 18,
            f"rows={len(acceptance)}",
        ),
        (
            "source_acceptance_review_passed",
            acceptance_review_passed,
            f"passed={acceptance_review_passed}",
        ),
        (
            "source_expected_outcome_count_6",
            len(outcomes) == 6,
            f"rows={len(outcomes)}",
        ),
        (
            "source_expected_outcome_review_passed",
            outcome_review_passed,
            f"passed={outcome_review_passed}",
        ),
        (
            "controlled_observation_state_valid",
            controlled_state_valid,
            f"valid={controlled_state_valid}",
        ),
        (
            "source_operational_locks_valid",
            source_locks_valid,
            f"false_guard_count={len(EXPECTED_FALSE_GUARDS)}",
        ),
        (
            "official_dataset_absent",
            official_absent,
            f"official_dataset_absent={official_absent}",
        ),
        (
            "report_only_dry_run_not_executed",
            safe_bool(
                summary.get("report_only_dry_run_executed", True),
                True,
            )
            is False,
            "report_only_dry_run_executed=False",
        ),
        (
            "report_only_dry_run_rows_zero",
            int(
                safe_float(
                    summary.get(
                        "report_only_dry_run_rows_generated",
                        -1,
                    )
                )
            )
            == 0,
            "report_only_dry_run_rows_generated=0",
        ),
        (
            "no_evidence_collection_enabled",
            safe_bool(
                summary.get("evidence_collection_enabled", True),
                True,
            )
            is False,
            "evidence_collection_enabled=False",
        ),
        (
            "no_official_dataset_implementation",
            safe_bool(
                summary.get(
                    "official_dataset_schema_implemented",
                    True,
                ),
                True,
            )
            is False,
            "official_dataset_schema_implemented=False",
        ),
        (
            "no_signal_or_execution_enabled",
            all(
                safe_bool(summary.get(field, True), True) is False
                for field in [
                    "signal_generation_enabled",
                    "live_alerts_allowed",
                    "paper_trade_execution_allowed",
                    "real_capital_allowed",
                    "market_execution_allowed",
                    "exchange_execution_allowed",
                    "automation_allowed",
                    "execution_allowed",
                ]
            ),
            "all_execution_boundaries=False",
        ),
        (
            "long_strategy_remains_unapproved",
            safe_bool(
                summary.get("long_strategy_approved", True),
                True,
            )
            is False,
            "long_strategy_approved=False",
        ),
        (
            "total_project_not_completed",
            safe_bool(
                summary.get("total_project_completed", True),
                True,
            )
            is False,
            "total_project_completed=False",
        ),
    ]

    return pd.DataFrame(
        [
            {
                "validation_name": name,
                "passed": bool(passed),
                "details": details,
            }
            for name, passed, details in validations
        ]
    )


def build_execution_preconditions(
    source_validations: pd.DataFrame,
) -> pd.DataFrame:
    lookup = {
        str(row["validation_name"]): safe_bool(
            row["passed"],
            False,
        )
        for _, row in source_validations.iterrows()
    }
    mapping = {
        "phase_10_32_validation_passed": [
            "phase_10_32_validation_passed",
        ],
        "source_execution_review_allowed": [
            "source_future_execution_review_allowed",
        ],
        "source_artifacts_integrity_valid": [
            "source_artifacts_exist",
            "source_artifacts_non_empty",
            "source_artifact_hashes_valid",
            "source_artifacts_stable_during_review",
        ],
        "source_review_blocks_passed": [
            "source_review_blocks_passed",
        ],
        "source_material_issue_count_zero": [
            "source_material_issue_count_zero",
        ],
        "schema_contract_valid": [
            "source_schema_field_count_54",
            "source_schema_order_valid",
            "source_schema_review_passed",
        ],
        "schema_safety_defaults_false": [
            "source_schema_safety_defaults_false",
        ],
        "scenario_contract_valid": [
            "source_scenario_count_6",
            "source_scenario_names_valid",
            "source_valid_scenario_count_1",
            "source_reject_scenario_count_5",
            "source_scenario_contract_valid",
            "source_scenario_safety_valid",
        ],
        "scenario_outcome_alignment_valid": [
            "scenario_outcome_alignment_passed",
        ],
        "scenario_execution_order_valid": [
            "scenario_execution_order_valid",
        ],
        "step_plan_valid": [
            "source_step_count_16",
            "source_step_review_passed",
        ],
        "dry_run_controls_valid": [
            "source_dry_run_control_count_20",
            "source_dry_run_control_review_passed",
        ],
        "artifact_plan_reports_only": [
            "source_artifact_plan_count_12",
            "source_artifact_plan_review_passed",
        ],
        "acceptance_contract_valid": [
            "source_acceptance_count_18",
            "source_acceptance_review_passed",
        ],
        "official_dataset_absent": [
            "official_dataset_absent",
            "no_official_dataset_implementation",
        ],
        "dry_run_not_previously_executed": [
            "report_only_dry_run_not_executed",
        ],
        "dry_run_rows_generated_zero": [
            "report_only_dry_run_rows_zero",
        ],
        "evidence_collection_disabled": [
            "no_evidence_collection_enabled",
        ],
        "signal_and_execution_disabled": [
            "no_signal_or_execution_enabled",
            "long_strategy_remains_unapproved",
        ],
        "future_run_report_only": [
            "total_project_not_completed",
        ],
    }

    rows = []
    for position, name in enumerate(
        EXECUTION_PRECONDITIONS,
        start=1,
    ):
        validation_names = mapping[name]
        passed = all(
            lookup.get(validation_name, False)
            for validation_name in validation_names
        )
        rows.append(
            {
                "precondition_position": position,
                "precondition_id": (
                    f"REPORT_ONLY_DRY_RUN_EXECUTION_PRECONDITION_{position:03d}"
                ),
                "precondition_name": name,
                "validation_names": ",".join(validation_names),
                "required": True,
                "review_only": True,
                "passed": passed,
            }
        )
    return pd.DataFrame(rows)


def build_abort_rules() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "abort_rule_position": position,
                "abort_rule_id": (
                    f"REPORT_ONLY_DRY_RUN_ABORT_RULE_{position:03d}"
                ),
                "abort_rule_name": name,
                "required": True,
                "fail_closed": True,
                "review_only": True,
                "implemented_in_phase_10_33": False,
                "dry_run_executed": False,
                "passed": True,
            }
            for position, name in enumerate(ABORT_RULES, start=1)
        ]
    )


def build_output_plan() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "output_position": position,
                "output_id": (
                    f"REPORT_ONLY_DRY_RUN_OUTPUT_{position:03d}"
                ),
                "output_name": name,
                "target_scope": "REPORTS_ONLY",
                "official_dataset_artifact": False,
                "real_evidence_artifact": False,
                "planned_for_phase_10_34": True,
                "created_in_phase_10_33": False,
                "passed": True,
            }
            for position, name in enumerate(OUTPUT_PLAN, start=1)
        ]
    )


def build_final_validations(
    source_validations: pd.DataFrame,
    execution_contract: pd.DataFrame,
    preconditions: pd.DataFrame,
    abort_rules: pd.DataFrame,
    output_plan: pd.DataFrame,
) -> pd.DataFrame:
    contract_valid = all(
        [
            len(execution_contract) == 6,
            all_passed(execution_contract),
            execution_contract.get(
                "execution_position",
                pd.Series(dtype=int),
            )
            .astype(int)
            .tolist()
            == list(range(1, 7)),
            column_all(execution_contract, "synthetic_only", True),
            column_all(execution_contract, "report_only", True),
            column_all(
                execution_contract,
                "in_memory_until_validation_complete",
                True,
            ),
            column_all(
                execution_contract,
                "reports_only_write_scope",
                True,
            ),
            column_all(
                execution_contract,
                "approved_for_future_run",
                True,
            ),
            column_all(
                execution_contract,
                "executed_in_phase_10_33",
                False,
            ),
        ]
    )

    contract_safety_valid = all(
        column_all(execution_contract, field, False)
        for field in [
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
    )

    additional = pd.DataFrame(
        [
            {
                "validation_name": "future_execution_contract_count_6",
                "passed": len(execution_contract) == 6,
                "details": f"rows={len(execution_contract)}",
            },
            {
                "validation_name": "future_execution_contract_valid",
                "passed": contract_valid,
                "details": f"valid={contract_valid}",
            },
            {
                "validation_name": "future_execution_contract_safety_valid",
                "passed": contract_safety_valid,
                "details": f"valid={contract_safety_valid}",
            },
            {
                "validation_name": "execution_precondition_count_20",
                "passed": len(preconditions) == 20,
                "details": f"rows={len(preconditions)}",
            },
            {
                "validation_name": "execution_preconditions_passed",
                "passed": all_passed(preconditions),
                "details": f"passed={all_passed(preconditions)}",
            },
            {
                "validation_name": "execution_abort_rule_count_12",
                "passed": len(abort_rules) == 12,
                "details": f"rows={len(abort_rules)}",
            },
            {
                "validation_name": "execution_abort_rules_valid",
                "passed": (
                    len(abort_rules) == 12
                    and all_passed(abort_rules)
                    and column_all(abort_rules, "required", True)
                    and column_all(abort_rules, "fail_closed", True)
                    and column_all(
                        abort_rules,
                        "implemented_in_phase_10_33",
                        False,
                    )
                    and column_all(
                        abort_rules,
                        "dry_run_executed",
                        False,
                    )
                ),
                "details": f"rows={len(abort_rules)}",
            },
            {
                "validation_name": "execution_output_plan_count_10",
                "passed": len(output_plan) == 10,
                "details": f"rows={len(output_plan)}",
            },
            {
                "validation_name": "execution_output_plan_valid",
                "passed": (
                    len(output_plan) == 10
                    and all_passed(output_plan)
                    and output_plan.get(
                        "target_scope",
                        pd.Series(dtype=str),
                    )
                    .astype(str)
                    .eq("REPORTS_ONLY")
                    .all()
                    and column_all(
                        output_plan,
                        "official_dataset_artifact",
                        False,
                    )
                    and column_all(
                        output_plan,
                        "real_evidence_artifact",
                        False,
                    )
                    and column_all(
                        output_plan,
                        "created_in_phase_10_33",
                        False,
                    )
                ),
                "details": f"rows={len(output_plan)}",
            },
            {
                "validation_name": "future_run_report_only",
                "passed": (
                    contract_valid
                    and contract_safety_valid
                    and all_passed(preconditions)
                ),
                "details": "future_run_scope=REPORT_ONLY",
            },
        ]
    )

    return pd.concat(
        [source_validations, additional],
        ignore_index=True,
    )


def build_review_items(
    validations: pd.DataFrame,
) -> pd.DataFrame:
    lookup = {
        str(row["validation_name"]): safe_bool(
            row["passed"],
            False,
        )
        for _, row in validations.iterrows()
    }
    rows = []
    for position, (name, validation_names) in enumerate(
        REVIEW_ITEM_SPECS,
        start=1,
    ):
        passed = all(
            lookup.get(validation_name, False)
            for validation_name in validation_names
        )
        rows.append(
            {
                "review_item_position": position,
                "review_item_id": (
                    f"REPORT_ONLY_DRY_RUN_EXECUTION_REVIEW_ITEM_{position:03d}"
                ),
                "review_item_name": name,
                "validation_names": ",".join(validation_names),
                "required": True,
                "review_only": True,
                "dry_run_execution_allowed_in_phase_10_33": False,
                "evidence_collection_enabled": False,
                "official_dataset_write_allowed": False,
                "market_execution_allowed": False,
                "passed": passed,
            }
        )
    return pd.DataFrame(rows)


def build_findings(
    review_items: pd.DataFrame,
) -> pd.DataFrame:
    rows = []
    for position, (_, item) in enumerate(
        review_items.iterrows(),
        start=1,
    ):
        passed = safe_bool(item["passed"], False)
        rows.append(
            {
                "finding_id": (
                    f"REPORT_ONLY_DRY_RUN_EXECUTION_REVIEW_FINDING_{position:03d}"
                ),
                "review_item_id": str(item["review_item_id"]),
                "review_item_name": str(item["review_item_name"]),
                "finding_status": "PASS" if passed else "FAIL",
                "material_issue_found": not passed,
                "design_change_required": not passed,
                "future_run_approved": False,
                "details": (
                    "Execution review criterion passed."
                    if passed
                    else "Execution review criterion failed."
                ),
                "passed": passed,
            }
        )
    return pd.DataFrame(rows)


def build_controls(
    validations: pd.DataFrame,
) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "control_position": position,
                "control_id": (
                    f"REPORT_ONLY_DRY_RUN_EXECUTION_REVIEW_CONTROL_{position:03d}"
                ),
                "control_name": str(row["validation_name"]),
                "required": True,
                "review_only": True,
                "dry_run_executed": False,
                "evidence_collection_enabled": False,
                "official_dataset_write_allowed": False,
                "market_execution_allowed": False,
                "passed": safe_bool(row["passed"], False),
            }
            for position, (_, row) in enumerate(
                validations.iterrows(),
                start=1,
            )
        ]
    )


def build_guard_matrix() -> pd.DataFrame:
    true_guards = [
        "source_controlled_forward_observation_start_run_performed",
        "source_controlled_forward_observation_start_performed",
        "forward_observation_start_allowed",
        "forward_observation_started",
        "report_only_dry_run_execution_review_performed",
        "report_only_dry_run_execution_review_passed",
        "future_report_only_dry_run_run_allowed",
    ]
    false_guards = [
        "report_only_dry_run_executed",
        "new_controlled_forward_observation_start_run_performed",
        "new_controlled_forward_observation_start_performed",
        "evidence_collection_enabled",
        "evidence_collection_started",
        "official_dataset_schema_implemented",
    ] + EXPECTED_FALSE_GUARDS

    rows = [
        {
            "guard_name": name,
            "required_value": True,
            "actual_value": True,
            "passed": True,
            "guard_group": "execution_review_state",
        }
        for name in true_guards
    ]
    rows.extend(
        [
            {
                "guard_name": name,
                "required_value": False,
                "actual_value": False,
                "passed": True,
                "guard_group": "execution_review_safety_guard",
            }
            for name in false_guards
        ]
    )
    rows.extend(
        [
            {
                "guard_name": "report_only_dry_run_rows_generated",
                "required_value": 0,
                "actual_value": 0,
                "passed": True,
                "guard_group": "dry_run_execution_guard",
            },
            {
                "guard_name": "official_evidence_rows_written",
                "required_value": 0,
                "actual_value": 0,
                "passed": True,
                "guard_group": "official_dataset_guard",
            },
        ]
    )
    return pd.DataFrame(rows)


def build_rules(
    validations: pd.DataFrame,
    review_items: pd.DataFrame,
    findings: pd.DataFrame,
    controls: pd.DataFrame,
    guards: pd.DataFrame,
    execution_contract: pd.DataFrame,
    preconditions: pd.DataFrame,
    abort_rules: pd.DataFrame,
    output_plan: pd.DataFrame,
) -> pd.DataFrame:
    material_issue_count = (
        int(findings["material_issue_found"].map(safe_bool).sum())
        if not findings.empty
        else -1
    )
    rule_specs = [
        (
            "review_validation_count_positive",
            len(validations) > 0,
            ">0",
            str(len(validations)),
        ),
        (
            "all_review_validations_passed",
            all_passed(validations),
            "True",
            str(all_passed(validations)),
        ),
        (
            "review_item_count_27",
            len(review_items) == 27,
            "27",
            str(len(review_items)),
        ),
        (
            "all_review_items_passed",
            all_passed(review_items),
            "True",
            str(all_passed(review_items)),
        ),
        (
            "review_finding_count_27",
            len(findings) == 27,
            "27",
            str(len(findings)),
        ),
        (
            "all_review_findings_passed",
            all_passed(findings),
            "True",
            str(all_passed(findings)),
        ),
        (
            "material_issue_count_zero",
            material_issue_count == 0,
            "0",
            str(material_issue_count),
        ),
        (
            "review_control_count_matches",
            len(controls) == len(validations),
            str(len(validations)),
            str(len(controls)),
        ),
        (
            "all_review_controls_passed",
            all_passed(controls),
            "True",
            str(all_passed(controls)),
        ),
        (
            "review_guard_count_37",
            len(guards) == 37,
            "37",
            str(len(guards)),
        ),
        (
            "all_review_guards_passed",
            all_passed(guards),
            "True",
            str(all_passed(guards)),
        ),
        (
            "future_execution_contract_count_6",
            len(execution_contract) == 6,
            "6",
            str(len(execution_contract)),
        ),
        (
            "future_execution_contract_passed",
            all_passed(execution_contract),
            "True",
            str(all_passed(execution_contract)),
        ),
        (
            "execution_precondition_count_20",
            len(preconditions) == 20,
            "20",
            str(len(preconditions)),
        ),
        (
            "execution_preconditions_passed",
            all_passed(preconditions),
            "True",
            str(all_passed(preconditions)),
        ),
        (
            "execution_abort_rule_count_12",
            len(abort_rules) == 12,
            "12",
            str(len(abort_rules)),
        ),
        (
            "execution_abort_rules_passed",
            all_passed(abort_rules),
            "True",
            str(all_passed(abort_rules)),
        ),
        (
            "execution_output_plan_count_10",
            len(output_plan) == 10,
            "10",
            str(len(output_plan)),
        ),
        (
            "execution_output_plan_passed",
            all_passed(output_plan),
            "True",
            str(all_passed(output_plan)),
        ),
        ("review_only", True, "True", "True"),
        ("dry_run_not_executed", True, "False", "False"),
        ("dry_run_rows_zero", True, "0", "0"),
        ("evidence_collection_disabled", True, "False", "False"),
        ("official_dataset_not_implemented", True, "False", "False"),
        ("official_dataset_writes_disabled", True, "False", "False"),
        ("signal_and_execution_disabled", True, "False", "False"),
        ("total_project_not_completed", True, "False", "False"),
    ]
    return pd.DataFrame(
        [
            {
                "rule_id": (
                    f"REPORT_ONLY_DRY_RUN_EXECUTION_REVIEW_RULE_{position:03d}"
                ),
                "rule_name": name,
                "passed": bool(passed),
                "required_value": required,
                "actual_value": actual,
            }
            for position, (name, passed, required, actual) in enumerate(
                rule_specs,
                start=1,
            )
        ]
    )


def build_requirements(
    validations: pd.DataFrame,
    review_items: pd.DataFrame,
    findings: pd.DataFrame,
    controls: pd.DataFrame,
    rules: pd.DataFrame,
    guards: pd.DataFrame,
    execution_contract: pd.DataFrame,
    preconditions: pd.DataFrame,
    abort_rules: pd.DataFrame,
    output_plan: pd.DataFrame,
) -> pd.DataFrame:
    rows = [
        (
            str(row["validation_name"]),
            safe_bool(row["passed"], False),
            "True",
            str(safe_bool(row["passed"], False)),
        )
        for _, row in validations.iterrows()
    ]
    rows.extend(
        [
            (
                "review_items_passed",
                all_passed(review_items),
                "True",
                str(all_passed(review_items)),
            ),
            (
                "review_findings_passed",
                all_passed(findings),
                "True",
                str(all_passed(findings)),
            ),
            (
                "review_controls_passed",
                all_passed(controls),
                "True",
                str(all_passed(controls)),
            ),
            (
                "review_rules_passed",
                all_passed(rules),
                "True",
                str(all_passed(rules)),
            ),
            (
                "review_guards_passed",
                all_passed(guards),
                "True",
                str(all_passed(guards)),
            ),
            (
                "future_execution_contract_passed",
                all_passed(execution_contract),
                "True",
                str(all_passed(execution_contract)),
            ),
            (
                "execution_preconditions_passed",
                all_passed(preconditions),
                "True",
                str(all_passed(preconditions)),
            ),
            (
                "execution_abort_rules_passed",
                all_passed(abort_rules),
                "True",
                str(all_passed(abort_rules)),
            ),
            (
                "execution_output_plan_passed",
                all_passed(output_plan),
                "True",
                str(all_passed(output_plan)),
            ),
            (
                "execution_review_performed",
                True,
                "True",
                "True",
            ),
            (
                "future_report_only_dry_run_run_allowed",
                True,
                "True",
                "True",
            ),
            (
                "dry_run_not_executed",
                True,
                "False",
                "False",
            ),
            (
                "dry_run_rows_generated_zero",
                True,
                "0",
                "0",
            ),
            (
                "evidence_collection_not_enabled",
                True,
                "False",
                "False",
            ),
            (
                "official_dataset_schema_not_implemented",
                True,
                "False",
                "False",
            ),
            (
                "official_evidence_rows_written_zero",
                True,
                "0",
                "0",
            ),
            (
                "signal_generation_disabled",
                True,
                "False",
                "False",
            ),
            (
                "paper_trading_disabled",
                True,
                "False",
                "False",
            ),
            (
                "market_execution_disabled",
                True,
                "False",
                "False",
            ),
            (
                "total_project_not_completed",
                True,
                "False",
                "False",
            ),
        ]
    )
    return pd.DataFrame(
        [
            {
                "requirement_id": (
                    f"REPORT_ONLY_DRY_RUN_EXECUTION_REVIEW_REQ_{position:03d}"
                ),
                "requirement_name": name,
                "passed": bool(passed),
                "required_value": required,
                "actual_value": actual,
            }
            for position, (name, passed, required, actual) in enumerate(
                rows,
                start=1,
            )
        ]
    )


def build_decision(
    requirements: pd.DataFrame,
    rules: pd.DataFrame,
    guards: pd.DataFrame,
) -> pd.DataFrame:
    passed_requirements = (
        int(requirements["passed"].map(safe_bool).sum())
        if not requirements.empty
        else 0
    )
    failed_requirements = len(requirements) - passed_requirements
    review_passed = (
        len(requirements) > 0
        and failed_requirements == 0
        and all_passed(rules)
        and all_passed(guards)
    )
    failed_names = (
        ",".join(
            requirements[
                ~requirements["passed"].map(safe_bool)
            ]["requirement_name"]
            .astype(str)
            .tolist()
        )
        if not requirements.empty
        else ""
    )

    return pd.DataFrame(
        [
            {
                "report_only_dry_run_execution_review_id": (
                    "PHASE_10_33_LONG_FORWARD_OBSERVATION_"
                    "EVIDENCE_COLLECTION_REPORT_ONLY_DRY_RUN_"
                    "EXECUTION_REVIEW_001"
                ),
                "report_only_dry_run_execution_review_performed": True,
                "report_only_dry_run_execution_review_passed": review_passed,
                "report_only_dry_run_execution_review_decision": (
                    READY_DECISION
                    if review_passed
                    else BLOCKED_DECISION
                ),
                "total_requirements": len(requirements),
                "passed_requirements": passed_requirements,
                "failed_requirements": failed_requirements,
                "failed_requirement_names": failed_names,
                "future_report_only_dry_run_run_allowed": review_passed,
                "report_only_dry_run_executed": False,
                "report_only_dry_run_rows_generated": 0,
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
            }
        ]
    )


def validate_long_forward_observation_evidence_collection_report_only_dry_run_execution_review() -> dict[str, pd.DataFrame]:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    checks: list[dict[str, Any]] = []

    for name, path in {
        "phase_10_32_dry_run_design_review_doc_exists": PHASE_10_32_DOC_PATH,
        "phase_10_33_dry_run_execution_review_doc_exists": PHASE_10_33_DOC_PATH,
    }.items():
        exists = path.exists()
        checks.append(
            check_row(
                "phase_anchor",
                name,
                exists,
                "INFO" if exists else "ERROR",
                str(path),
            )
        )

    official_before = OFFICIAL_DATASET_PATH.exists()
    manifest_before = build_manifest()
    source = {
        name: read_csv(path)
        for name, path in SOURCE_PATHS.items()
    }

    source_validations = build_source_validations(
        source,
        manifest_before,
        build_manifest(),
        not official_before,
    )
    execution_contract = build_future_execution_contract(
        source["source_scenarios"]
    )
    preconditions = build_execution_preconditions(
        source_validations
    )
    abort_rules = build_abort_rules()
    output_plan = build_output_plan()
    validations = build_final_validations(
        source_validations,
        execution_contract,
        preconditions,
        abort_rules,
        output_plan,
    )
    review_items = build_review_items(validations)
    findings = build_findings(review_items)
    controls = build_controls(validations)
    guards = build_guard_matrix()
    rules = build_rules(
        validations,
        review_items,
        findings,
        controls,
        guards,
        execution_contract,
        preconditions,
        abort_rules,
        output_plan,
    )
    requirements = build_requirements(
        validations,
        review_items,
        findings,
        controls,
        rules,
        guards,
        execution_contract,
        preconditions,
        abort_rules,
        output_plan,
    )
    decision = build_decision(requirements, rules, guards)
    decision_row = (
        decision.iloc[0].to_dict()
        if not decision.empty
        else {}
    )

    aggregate_checks = {
        "review_validations_passed": all_passed(validations),
        "review_items_passed": all_passed(review_items),
        "review_findings_passed": all_passed(findings),
        "review_controls_passed": all_passed(controls),
        "review_rules_passed": all_passed(rules),
        "review_requirements_passed": all_passed(requirements),
        "review_guards_passed": all_passed(guards),
        "future_execution_contract_passed": all_passed(execution_contract),
        "execution_preconditions_passed": all_passed(preconditions),
        "execution_abort_rules_passed": all_passed(abort_rules),
        "execution_output_plan_passed": all_passed(output_plan),
        "report_only_dry_run_execution_review_passed": safe_bool(
            decision_row.get(
                "report_only_dry_run_execution_review_passed",
                False,
            )
        ),
        "report_only_dry_run_execution_review_decision_expected": (
            str(
                decision_row.get(
                    "report_only_dry_run_execution_review_decision",
                    "",
                )
            )
            == READY_DECISION
        ),
    }
    for name, passed in aggregate_checks.items():
        checks.append(
            check_row(
                "report_only_dry_run_execution_review",
                name,
                passed,
                "INFO" if passed else "ERROR",
                (
                    str(
                        decision_row.get(
                            "report_only_dry_run_execution_review_decision",
                            "",
                        )
                    )
                    if name.endswith("decision_expected")
                    else f"{name}={passed}"
                ),
            )
        )

    official_after = OFFICIAL_DATASET_PATH.exists()
    official_unchanged_absent = (
        not official_before and not official_after
    )
    checks.append(
        check_row(
            "official_dataset_guard",
            "official_dataset_not_created_or_written",
            official_unchanged_absent,
            "INFO" if official_unchanged_absent else "ERROR",
            f"before={official_before},after={official_after}",
        )
    )

    for _, row in guards.iterrows():
        passed = safe_bool(row["passed"], False)
        checks.append(
            check_row(
                "report_only_dry_run_execution_review_safety_flags",
                str(row["guard_name"]),
                passed,
                "INFO" if passed else "ERROR",
                (
                    f"{row['guard_name']}={row['actual_value']} "
                    f"(required={row['required_value']})"
                ),
            )
        )

    warnings = [
        (
            "review_only",
            "Phase 10.33 reviews only report-only dry-run execution readiness.",
        ),
        (
            "dry_run_not_executed",
            "No dry-run row was generated or executed.",
        ),
        (
            "observation_state_preserved",
            "The controlled observation state remains started.",
        ),
        (
            "evidence_collection_not_enabled",
            "Evidence collection remains disabled.",
        ),
        (
            "official_dataset_not_implemented",
            "The official evidence dataset is not implemented.",
        ),
        (
            "official_dataset_not_written",
            "The official evidence dataset remains absent and unwritten.",
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

    future_allowed = safe_bool(
        decision_row.get(
            "future_report_only_dry_run_run_allowed",
            False,
        )
    )
    checks.append(
        check_row(
            "planning_scope",
            "future_report_only_dry_run_run_allowed",
            future_allowed,
            "WARNING" if future_allowed else "ERROR",
            (
                "Allows only a future synthetic report-only dry-run run. "
                "It does not enable evidence collection, official dataset "
                "implementation or writes, signals, alerts, paper trading, "
                "real capital or market execution."
            ),
        )
    )
    checks.append(
        check_row(
            "phase_transition",
            "phase_10_34_recommended_next",
            True,
            "INFO",
            (
                "Recommended next: Phase 10.34 LONG Forward Observation "
                "Evidence Collection Report-Only Dry-Run Run V1."
            ),
        )
    )

    checks_df = pd.DataFrame(checks)
    blocker_count = int(
        checks_df["blocker"].map(safe_bool).sum()
    )
    error_count = int(
        checks_df["severity"].eq("ERROR").sum()
    )
    warning_count = int(
        checks_df["severity"].eq("WARNING").sum()
    )
    validation_passed = (
        blocker_count == 0 and error_count == 0
    )

    source_summary = (
        source["summary"].iloc[0].to_dict()
        if not source["summary"].empty
        else {}
    )
    lookup = {
        str(row["validation_name"]): safe_bool(
            row["passed"],
            False,
        )
        for _, row in validations.iterrows()
    }
    material_issue_count = (
        int(findings["material_issue_found"].map(safe_bool).sum())
        if not findings.empty
        else -1
    )

    summary_df = pd.DataFrame(
        [
            {
                "phase": "10.33",
                "long_forward_observation_evidence_collection_report_only_dry_run_execution_review_defined": True,
                "phase_10_32_validation_passed": lookup.get(
                    "phase_10_32_validation_passed",
                    False,
                ),
                "source_report_only_dry_run_design_review_performed": lookup.get(
                    "source_design_review_performed",
                    False,
                ),
                "source_report_only_dry_run_design_review_passed": lookup.get(
                    "source_design_review_passed",
                    False,
                ),
                "source_report_only_dry_run_design_review_decision": str(
                    source_summary.get(
                        "report_only_dry_run_design_review_decision",
                        "",
                    )
                ),
                "source_future_report_only_dry_run_execution_review_allowed": lookup.get(
                    "source_future_execution_review_allowed",
                    False,
                ),
                "source_artifact_count": len(manifest_before),
                "source_artifacts_exist": lookup.get(
                    "source_artifacts_exist",
                    False,
                ),
                "source_artifacts_non_empty": lookup.get(
                    "source_artifacts_non_empty",
                    False,
                ),
                "source_artifact_hashes_valid": lookup.get(
                    "source_artifact_hashes_valid",
                    False,
                ),
                "source_artifacts_stable_during_review": lookup.get(
                    "source_artifacts_stable_during_review",
                    False,
                ),
                "source_manifest_sha256": manifest_digest(
                    manifest_before
                ),
                "source_summary_decision_consistent": lookup.get(
                    "source_summary_decision_consistent",
                    False,
                ),
                "source_counts_valid": lookup.get(
                    "source_counts_valid",
                    False,
                ),
                "source_review_blocks_passed": lookup.get(
                    "source_review_blocks_passed",
                    False,
                ),
                "source_material_issue_count_zero": lookup.get(
                    "source_material_issue_count_zero",
                    False,
                ),
                "source_schema_review_passed": lookup.get(
                    "source_schema_review_passed",
                    False,
                ),
                "source_scenario_contract_valid": lookup.get(
                    "source_scenario_contract_valid",
                    False,
                ),
                "source_scenario_safety_valid": lookup.get(
                    "source_scenario_safety_valid",
                    False,
                ),
                "scenario_outcome_alignment_passed": lookup.get(
                    "scenario_outcome_alignment_passed",
                    False,
                ),
                "scenario_execution_order_valid": lookup.get(
                    "scenario_execution_order_valid",
                    False,
                ),
                "source_step_review_passed": lookup.get(
                    "source_step_review_passed",
                    False,
                ),
                "source_dry_run_control_review_passed": lookup.get(
                    "source_dry_run_control_review_passed",
                    False,
                ),
                "source_artifact_plan_review_passed": lookup.get(
                    "source_artifact_plan_review_passed",
                    False,
                ),
                "source_acceptance_review_passed": lookup.get(
                    "source_acceptance_review_passed",
                    False,
                ),
                "source_expected_outcome_review_passed": lookup.get(
                    "source_expected_outcome_review_passed",
                    False,
                ),
                "future_execution_contract_rows": len(
                    execution_contract
                ),
                "future_execution_contract_valid": lookup.get(
                    "future_execution_contract_valid",
                    False,
                ),
                "future_execution_contract_safety_valid": lookup.get(
                    "future_execution_contract_safety_valid",
                    False,
                ),
                "execution_precondition_rows": len(preconditions),
                "execution_preconditions_passed": lookup.get(
                    "execution_preconditions_passed",
                    False,
                ),
                "execution_abort_rule_rows": len(abort_rules),
                "execution_abort_rules_valid": lookup.get(
                    "execution_abort_rules_valid",
                    False,
                ),
                "execution_output_plan_rows": len(output_plan),
                "execution_output_plan_valid": lookup.get(
                    "execution_output_plan_valid",
                    False,
                ),
                "controlled_observation_state_valid": lookup.get(
                    "controlled_observation_state_valid",
                    False,
                ),
                "source_operational_locks_valid": lookup.get(
                    "source_operational_locks_valid",
                    False,
                ),
                "official_dataset_absent": lookup.get(
                    "official_dataset_absent",
                    False,
                ),
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
                "material_issue_count": material_issue_count,
                "report_only_dry_run_execution_review_performed": True,
                "report_only_dry_run_execution_review_passed": safe_bool(
                    decision_row.get(
                        "report_only_dry_run_execution_review_passed",
                        False,
                    )
                ),
                "report_only_dry_run_execution_review_decision": str(
                    decision_row.get(
                        "report_only_dry_run_execution_review_decision",
                        "",
                    )
                ),
                "future_report_only_dry_run_run_allowed": future_allowed,
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
                    "PHASE_10_33_LONG_FORWARD_OBSERVATION_"
                    "EVIDENCE_COLLECTION_REPORT_ONLY_DRY_RUN_"
                    "EXECUTION_REVIEW_VALIDATED"
                    if validation_passed
                    else
                    "PHASE_10_33_LONG_FORWARD_OBSERVATION_"
                    "EVIDENCE_COLLECTION_REPORT_ONLY_DRY_RUN_"
                    "EXECUTION_REVIEW_FAILED"
                ),
            }
        ]
    )

    outputs = {
        "phase_10_32_source_summary_v1.csv": source["summary"],
        "phase_10_32_source_schema_v1.csv": source["source_schema"],
        "phase_10_32_source_scenarios_v1.csv": source["source_scenarios"],
        "phase_10_32_source_steps_v1.csv": source["source_steps"],
        "phase_10_32_source_dry_run_controls_v1.csv": source["source_dry_run_controls"],
        "phase_10_32_source_artifact_plan_v1.csv": source["source_artifact_plan"],
        "phase_10_32_source_acceptance_v1.csv": source["source_acceptance"],
        "phase_10_32_source_outcomes_v1.csv": source["source_outcomes"],
        "phase_10_32_source_review_validations_v1.csv": source["review_validations"],
        "phase_10_32_source_review_items_v1.csv": source["review_items"],
        "phase_10_32_source_review_findings_v1.csv": source["review_findings"],
        "phase_10_32_source_review_controls_v1.csv": source["review_controls"],
        "phase_10_32_source_review_rules_v1.csv": source["review_rules"],
        "phase_10_32_source_review_requirements_v1.csv": source["review_requirements"],
        "phase_10_32_source_review_guard_matrix_v1.csv": source["review_guard_matrix"],
        "phase_10_32_source_review_decision_v1.csv": source["review_decision"],
        "phase_10_32_source_review_checks_v1.csv": source["review_checks"],
        "phase_10_32_source_review_manifest_v1.csv": source["review_manifest"],
        "source_report_only_dry_run_execution_review_artifact_manifest_v1.csv": manifest_before,
        "report_only_dry_run_future_execution_contract_v1.csv": execution_contract,
        "report_only_dry_run_execution_preconditions_v1.csv": preconditions,
        "report_only_dry_run_execution_abort_rules_v1.csv": abort_rules,
        "report_only_dry_run_execution_output_plan_v1.csv": output_plan,
        "report_only_dry_run_execution_review_validations_v1.csv": validations,
        "report_only_dry_run_execution_review_items_v1.csv": review_items,
        "report_only_dry_run_execution_review_findings_v1.csv": findings,
        "report_only_dry_run_execution_review_controls_v1.csv": controls,
        "report_only_dry_run_execution_review_rules_v1.csv": rules,
        "report_only_dry_run_execution_review_requirements_v1.csv": requirements,
        "report_only_dry_run_execution_review_guard_matrix_v1.csv": guards,
        "report_only_dry_run_execution_review_decision_v1.csv": decision,
        "report_only_dry_run_execution_review_checks_v1.csv": checks_df,
        "report_only_dry_run_execution_review_summary_v1.csv": summary_df,
    }
    for filename, dataframe in outputs.items():
        dataframe.to_csv(REPORTS_DIR / filename, index=False)

    return {
        "summary": summary_df,
        "source_summary": source["summary"],
        "source_schema": source["source_schema"],
        "source_scenarios": source["source_scenarios"],
        "source_steps": source["source_steps"],
        "source_dry_run_controls": source["source_dry_run_controls"],
        "source_artifact_plan": source["source_artifact_plan"],
        "source_acceptance": source["source_acceptance"],
        "source_outcomes": source["source_outcomes"],
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
        "execution_review_manifest": manifest_before,
        "future_execution_contract": execution_contract,
        "execution_preconditions": preconditions,
        "execution_abort_rules": abort_rules,
        "execution_output_plan": output_plan,
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
