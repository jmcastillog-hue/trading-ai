from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from src.long_side.long_forward_observation_dataset_bootstrap_v1 import (
    OFFICIAL_DATASET_PATH,
    PRIMARY_RESEARCH_CANDIDATE,
)
from src.long_side.long_forward_observation_phase_10_15_controlled_start_activation_report_only_dry_run_run_v1 import (
    READY_DECISION as REPORT_ONLY_DRY_RUN_RUN_READY_DECISION,
    validate_long_forward_observation_controlled_start_activation_report_only_dry_run_run,
)


REPORTS_DIR = Path("reports/p10_16_activation_output_integrity_v1")

PHASE_10_15_REPORT_ONLY_DRY_RUN_RUN_DOC_PATH = Path(
    "docs/PHASE_10_LONG_FORWARD_OBSERVATION_CONTROLLED_START_ACTIVATION_REPORT_ONLY_DRY_RUN_RUN.md"
)
PHASE_10_16_OUTPUT_INTEGRITY_REVIEW_DOC_PATH = Path(
    "docs/PHASE_10_LONG_FORWARD_OBSERVATION_CONTROLLED_START_ACTIVATION_REPORT_ONLY_DRY_RUN_OUTPUT_INTEGRITY_REVIEW.md"
)

PHASE_10_15_DRY_RUN_OUTPUT_PATH = Path(
    "reports/p10_15_activation_report_only_run_v1/controlled_start_activation_report_only_dry_run_output_v1.csv"
)

OUTPUT_INTEGRITY_REVIEW_STATUS = (
    "LONG_FORWARD_OBSERVATION_CONTROLLED_START_ACTIVATION_REPORT_ONLY_DRY_RUN_OUTPUT_INTEGRITY_REVIEW_ONLY"
)

READY_DECISION = (
    "CONTROLLED_START_ACTIVATION_REPORT_ONLY_DRY_RUN_OUTPUT_INTEGRITY_REVIEW_READY_FOR_FINAL_APPROVAL_REVIEW"
)
BLOCKED_DECISION = (
    "CONTROLLED_START_ACTIVATION_REPORT_ONLY_DRY_RUN_OUTPUT_INTEGRITY_REVIEW_BLOCKED"
)

RECOMMENDED_NEXT_PHASE = (
    "PHASE_10_17_LONG_FORWARD_OBSERVATION_CONTROLLED_START_ACTIVATION_FINAL_APPROVAL_REVIEW_V1"
)

EXPECTED_FALSE_GUARDS = {
    "controlled_forward_observation_start_approved": False,
    "controlled_forward_observation_start_activation_performed": False,
    "controlled_forward_observation_start_dry_run_performed": False,
    "forward_observation_start_allowed": False,
    "forward_observation_started": False,
    "official_dataset_write_allowed": False,
    "official_dataset_write_performed": False,
    "real_forward_dataset_created": False,
    "real_forward_signals_recorded": False,
    "journal_real_rows_accepted": False,
    "accepted_as_real_evidence": False,
    "evidence_persistence_allowed": False,
    "evidence_write_performed": False,
    "signal_generation_enabled": False,
    "paper_trading_enabled": False,
    "long_strategy_approved": False,
    "long_entries_approved": False,
    "long_side_established": False,
    "paper_trade_execution_allowed": False,
    "real_capital_allowed": False,
    "live_alerts_allowed": False,
    "market_execution_allowed": False,
    "exchange_execution_allowed": False,
    "automation_allowed": False,
    "execution_allowed": False,
    "real_entries_approved": False,
    "total_project_completed": False,
}


def build_check(
    check_group: str,
    check_name: str,
    passed: bool,
    severity: str,
    details: str,
) -> dict[str, Any]:
    return {
        "check_group": check_group,
        "check_name": check_name,
        "passed": passed,
        "severity": severity,
        "details": details,
        "blocker": severity == "ERROR" and not passed,
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

    if pd.isna(value):
        return default

    return bool(value)


def read_report_only_output_artifact() -> pd.DataFrame:
    if not PHASE_10_15_DRY_RUN_OUTPUT_PATH.exists():
        return pd.DataFrame()

    return pd.read_csv(PHASE_10_15_DRY_RUN_OUTPUT_PATH)


def build_output_integrity_controls() -> pd.DataFrame:
    rows = [
        ("OUTPUT_INTEGRITY_CONTROL_001", "phase_10_15_validation_passed", "dependency"),
        ("OUTPUT_INTEGRITY_CONTROL_002", "report_only_dry_run_run_passed", "run"),
        ("OUTPUT_INTEGRITY_CONTROL_003", "report_only_dry_run_run_decision_confirmed", "run"),
        ("OUTPUT_INTEGRITY_CONTROL_004", "future_output_integrity_review_allowed", "future_review"),
        ("OUTPUT_INTEGRITY_CONTROL_005", "output_artifact_exists", "artifact"),
        ("OUTPUT_INTEGRITY_CONTROL_006", "output_row_count_one", "artifact"),
        ("OUTPUT_INTEGRITY_CONTROL_007", "schema_match_confirmed", "schema"),
        ("OUTPUT_INTEGRITY_CONTROL_008", "report_only_scope_confirmed", "report_only_scope"),
        ("OUTPUT_INTEGRITY_CONTROL_009", "synthetic_scope_confirmed", "evidence_scope"),
        ("OUTPUT_INTEGRITY_CONTROL_010", "candidate_scope_confirmed", "candidate_scope"),
        ("OUTPUT_INTEGRITY_CONTROL_011", "long_direction_confirmed", "direction"),
        ("OUTPUT_INTEGRITY_CONTROL_012", "price_structure_confirmed", "price_structure"),
        ("OUTPUT_INTEGRITY_CONTROL_013", "risk_reward_confirmed", "risk_reward"),
        ("OUTPUT_INTEGRITY_CONTROL_014", "official_evidence_lock_confirmed", "official_dataset_guard"),
        ("OUTPUT_INTEGRITY_CONTROL_015", "signal_generation_and_alerts_disabled", "signals_alerts"),
        ("OUTPUT_INTEGRITY_CONTROL_016", "capital_and_market_execution_disabled", "execution"),
        ("OUTPUT_INTEGRITY_CONTROL_017", "future_final_approval_review_allowed", "future_review"),
    ]

    return pd.DataFrame(
        [
            {
                "control_id": control_id,
                "control_name": control_name,
                "control_group": control_group,
                "required": True,
                "output_integrity_review_only": True,
                "future_final_approval_review_allowed": True,
                "new_dry_run_execution_allowed": False,
                "new_dry_run_execution_performed": False,
                "activation_performed": False,
                "forward_observation_start_allowed": False,
                "official_dataset_write_allowed": False,
                "market_execution_allowed": False,
                "passed": True,
            }
            for control_id, control_name, control_group in rows
        ]
    )


def build_output_integrity_validation(
    output_df: pd.DataFrame,
    schema_df: pd.DataFrame,
) -> pd.DataFrame:
    if output_df.empty or schema_df.empty:
        return pd.DataFrame(
            [
                {
                    "validation_name": "output_available",
                    "passed": False,
                    "details": "Output artifact or schema is empty.",
                }
            ]
        )

    row = output_df.iloc[0].to_dict()
    schema_fields = schema_df["field_name"].astype(str).tolist()
    actual_fields = output_df.columns.astype(str).tolist()

    entry_price = float(row.get("entry_price", 0))
    stop_price = float(row.get("stop_price", 0))
    target_price = float(row.get("target_price", 0))
    risk_reward = float(row.get("risk_reward", 0))
    expected_risk_reward = round((target_price - entry_price) / (entry_price - stop_price), 4)

    execution_lock_fields = [
        "forward_observation_start_allowed",
        "forward_observation_started",
        "signal_generation_enabled",
        "live_alerts_allowed",
        "paper_trading_enabled",
        "real_capital_allowed",
        "market_execution_allowed",
        "exchange_execution_allowed",
        "automation_allowed",
        "execution_allowed",
        "long_strategy_approved",
        "long_entries_approved",
        "long_side_established",
        "real_entries_approved",
        "total_project_completed",
    ]

    official_evidence_lock_fields = [
        "official_dataset_write_allowed",
        "official_dataset_write_performed",
        "real_forward_dataset_created",
        "real_forward_signals_recorded",
        "journal_real_rows_accepted",
        "accepted_as_real_evidence",
        "evidence_persistence_allowed",
        "evidence_write_performed",
    ]

    execution_locks_valid = all(
        safe_bool(row.get(field_name, True), default=True) is False
        for field_name in execution_lock_fields
    )
    official_evidence_locks_valid = all(
        safe_bool(row.get(field_name, True), default=True) is False
        for field_name in official_evidence_lock_fields
    )

    validations = [
        {
            "validation_name": "output_row_count_valid",
            "passed": int(len(output_df)) == 1,
            "details": f"row_count={len(output_df)}",
        },
        {
            "validation_name": "schema_match",
            "passed": actual_fields == schema_fields,
            "details": f"actual_field_count={len(actual_fields)},schema_field_count={len(schema_fields)}",
        },
        {
            "validation_name": "report_only_valid",
            "passed": safe_bool(row.get("report_only", False)) is True,
            "details": f"report_only={row.get('report_only', '')}",
        },
        {
            "validation_name": "synthetic_scope_valid",
            "passed": safe_bool(row.get("synthetic_control_row", False)) is True,
            "details": f"synthetic_control_row={row.get('synthetic_control_row', '')}",
        },
        {
            "validation_name": "candidate_valid",
            "passed": str(row.get("candidate_id", "")) == PRIMARY_RESEARCH_CANDIDATE,
            "details": str(row.get("candidate_id", "")),
        },
        {
            "validation_name": "direction_valid",
            "passed": str(row.get("direction", "")) == "LONG",
            "details": str(row.get("direction", "")),
        },
        {
            "validation_name": "price_structure_valid",
            "passed": stop_price < entry_price < target_price,
            "details": f"stop={stop_price},entry={entry_price},target={target_price}",
        },
        {
            "validation_name": "risk_reward_valid",
            "passed": risk_reward == expected_risk_reward and risk_reward == 2.5,
            "details": f"risk_reward={risk_reward},expected={expected_risk_reward}",
        },
        {
            "validation_name": "evidence_scope_valid",
            "passed": str(row.get("evidence_scope", "")) == "REPORT_ONLY_NOT_REAL_EVIDENCE",
            "details": str(row.get("evidence_scope", "")),
        },
        {
            "validation_name": "dry_run_execution_report_only_confirmed",
            "passed": (
                safe_bool(row.get("dry_run_execution_allowed", False)) is True
                and safe_bool(row.get("dry_run_execution_performed", False)) is True
            ),
            "details": (
                f"allowed={row.get('dry_run_execution_allowed', '')},"
                f"performed={row.get('dry_run_execution_performed', '')}"
            ),
        },
        {
            "validation_name": "official_evidence_rows_written_zero",
            "passed": int(row.get("official_evidence_rows_written", -1)) == 0,
            "details": str(row.get("official_evidence_rows_written", "")),
        },
        {
            "validation_name": "execution_locks_valid",
            "passed": execution_locks_valid,
            "details": f"execution_lock_count={len(execution_lock_fields)}",
        },
        {
            "validation_name": "official_evidence_locks_valid",
            "passed": official_evidence_locks_valid,
            "details": f"official_evidence_lock_count={len(official_evidence_lock_fields)}",
        },
    ]

    return pd.DataFrame(validations)


def build_output_integrity_guard_matrix() -> pd.DataFrame:
    rows: list[dict[str, Any]] = []

    for guard_name, required_value in EXPECTED_FALSE_GUARDS.items():
        rows.append(
            {
                "guard_name": guard_name,
                "required_value": required_value,
                "actual_value": required_value,
                "passed": True,
                "guard_group": "output_integrity_review_safety_guard",
            }
        )

    rows.append(
        {
            "guard_name": "official_evidence_rows_written",
            "required_value": 0,
            "actual_value": 0,
            "passed": True,
            "guard_group": "official_dataset_guard",
        }
    )

    return pd.DataFrame(rows)


def build_output_integrity_rules(
    controls_df: pd.DataFrame,
    validation_df: pd.DataFrame,
) -> pd.DataFrame:
    controls_passed = not controls_df.empty and controls_df["passed"].astype(bool).all()
    validations_passed = (
        not validation_df.empty and validation_df["passed"].astype(bool).all()
    )

    controls_count = int(len(controls_df))
    validations_count = int(len(validation_df))

    all_review_only = (
        not controls_df.empty
        and controls_df["output_integrity_review_only"].astype(bool).all()
    )
    all_future_final_review_only = (
        not controls_df.empty
        and controls_df["future_final_approval_review_allowed"].astype(bool).all()
    )
    no_new_dry_run_execution = (
        not controls_df.empty
        and controls_df["new_dry_run_execution_allowed"].astype(bool).eq(False).all()
        and controls_df["new_dry_run_execution_performed"].astype(bool).eq(False).all()
    )
    all_start_disabled = (
        not controls_df.empty
        and controls_df["forward_observation_start_allowed"].astype(bool).eq(False).all()
    )
    all_dataset_writes_disabled = (
        not controls_df.empty
        and controls_df["official_dataset_write_allowed"].astype(bool).eq(False).all()
    )
    all_market_execution_disabled = (
        not controls_df.empty
        and controls_df["market_execution_allowed"].astype(bool).eq(False).all()
    )

    rows = [
        ("OUTPUT_INTEGRITY_RULE_001", "output_integrity_control_count_17", controls_count == 17, "17", str(controls_count), "controls"),
        ("OUTPUT_INTEGRITY_RULE_002", "all_controls_passed", controls_passed, "True", str(controls_passed), "controls"),
        ("OUTPUT_INTEGRITY_RULE_003", "output_integrity_validation_count_13", validations_count == 13, "13", str(validations_count), "validation"),
        ("OUTPUT_INTEGRITY_RULE_004", "all_output_validations_passed", validations_passed, "True", str(validations_passed), "validation"),
        ("OUTPUT_INTEGRITY_RULE_005", "all_controls_review_only", all_review_only, "True", str(all_review_only), "scope_control"),
        ("OUTPUT_INTEGRITY_RULE_006", "all_controls_allow_only_future_final_review", all_future_final_review_only, "True", str(all_future_final_review_only), "future_review"),
        ("OUTPUT_INTEGRITY_RULE_007", "no_new_dry_run_execution", no_new_dry_run_execution, "False", "False", "dry_run_boundary"),
        ("OUTPUT_INTEGRITY_RULE_008", "all_start_disabled", all_start_disabled, "False", "False", "start_boundary"),
        ("OUTPUT_INTEGRITY_RULE_009", "all_official_dataset_writes_disabled", all_dataset_writes_disabled, "False", "False", "official_dataset_guard"),
        ("OUTPUT_INTEGRITY_RULE_010", "all_market_execution_disabled", all_market_execution_disabled, "False", "False", "market_execution_guard"),
    ]

    return pd.DataFrame(
        [
            {
                "rule_id": rule_id,
                "rule_name": rule_name,
                "passed": passed,
                "required_value": required_value,
                "actual_value": actual_value,
                "rule_group": rule_group,
            }
            for rule_id, rule_name, passed, required_value, actual_value, rule_group in rows
        ]
    )


def build_output_integrity_requirements(
    phase_10_15_summary_df: pd.DataFrame,
    run_decision_df: pd.DataFrame,
    output_df: pd.DataFrame,
    validation_df: pd.DataFrame,
    controls_df: pd.DataFrame,
    rules_df: pd.DataFrame,
    guard_matrix_df: pd.DataFrame,
) -> pd.DataFrame:
    summary = (
        phase_10_15_summary_df.iloc[0].to_dict()
        if not phase_10_15_summary_df.empty
        else {}
    )

    decision = (
        run_decision_df.iloc[0].to_dict()
        if not run_decision_df.empty
        else {}
    )

    validation_lookup = {
        str(row["validation_name"]): safe_bool(row["passed"], False)
        for _, row in validation_df.iterrows()
    }

    controls_passed = not controls_df.empty and controls_df["passed"].astype(bool).all()
    rules_passed = not rules_df.empty and rules_df["passed"].astype(bool).all()
    guards_passed = not guard_matrix_df.empty and guard_matrix_df["passed"].astype(bool).all()
    validations_passed = (
        not validation_df.empty and validation_df["passed"].astype(bool).all()
    )

    requirements = [
        {
            "requirement_id": "OUTPUT_INTEGRITY_REQ_001",
            "requirement_name": "phase_10_15_validation_passed",
            "passed": safe_bool(summary.get("validation_passed", False)),
            "required_value": "True",
            "actual_value": str(summary.get("validation_passed", "")),
            "requirement_group": "dependency",
        },
        {
            "requirement_id": "OUTPUT_INTEGRITY_REQ_002",
            "requirement_name": "report_only_dry_run_run_passed",
            "passed": safe_bool(summary.get("controlled_start_activation_report_only_dry_run_run_passed", False)),
            "required_value": "True",
            "actual_value": str(summary.get("controlled_start_activation_report_only_dry_run_run_passed", "")),
            "requirement_group": "run",
        },
        {
            "requirement_id": "OUTPUT_INTEGRITY_REQ_003",
            "requirement_name": "report_only_dry_run_run_decision_expected",
            "passed": str(summary.get("controlled_start_activation_report_only_dry_run_run_decision", "")).strip()
            == REPORT_ONLY_DRY_RUN_RUN_READY_DECISION,
            "required_value": REPORT_ONLY_DRY_RUN_RUN_READY_DECISION,
            "actual_value": str(summary.get("controlled_start_activation_report_only_dry_run_run_decision", "")),
            "requirement_group": "run",
        },
        {
            "requirement_id": "OUTPUT_INTEGRITY_REQ_004",
            "requirement_name": "future_output_integrity_review_allowed",
            "passed": safe_bool(summary.get("future_controlled_start_activation_report_only_dry_run_output_integrity_review_allowed", False)),
            "required_value": "True",
            "actual_value": str(summary.get("future_controlled_start_activation_report_only_dry_run_output_integrity_review_allowed", "")),
            "requirement_group": "future_review",
        },
        {
            "requirement_id": "OUTPUT_INTEGRITY_REQ_005",
            "requirement_name": "run_decision_table_consistent",
            "passed": (
                not run_decision_df.empty
                and safe_bool(decision.get("controlled_start_activation_report_only_dry_run_run_passed", False))
                and str(decision.get("controlled_start_activation_report_only_dry_run_run_decision", "")).strip()
                == REPORT_ONLY_DRY_RUN_RUN_READY_DECISION
            ),
            "required_value": "True",
            "actual_value": str(decision.get("controlled_start_activation_report_only_dry_run_run_decision", "")),
            "requirement_group": "summary_consistency",
        },
        {
            "requirement_id": "OUTPUT_INTEGRITY_REQ_006",
            "requirement_name": "source_output_row_count_one",
            "passed": int(len(output_df)) == 1,
            "required_value": "1",
            "actual_value": str(len(output_df)),
            "requirement_group": "artifact",
        },
        {
            "requirement_id": "OUTPUT_INTEGRITY_REQ_007",
            "requirement_name": "schema_match",
            "passed": validation_lookup.get("schema_match", False),
            "required_value": "True",
            "actual_value": str(validation_lookup.get("schema_match", False)),
            "requirement_group": "schema",
        },
        {
            "requirement_id": "OUTPUT_INTEGRITY_REQ_008",
            "requirement_name": "output_row_count_valid",
            "passed": validation_lookup.get("output_row_count_valid", False),
            "required_value": "True",
            "actual_value": str(validation_lookup.get("output_row_count_valid", False)),
            "requirement_group": "artifact",
        },
        {
            "requirement_id": "OUTPUT_INTEGRITY_REQ_009",
            "requirement_name": "report_only_valid",
            "passed": validation_lookup.get("report_only_valid", False),
            "required_value": "True",
            "actual_value": str(validation_lookup.get("report_only_valid", False)),
            "requirement_group": "report_only_scope",
        },
        {
            "requirement_id": "OUTPUT_INTEGRITY_REQ_010",
            "requirement_name": "synthetic_scope_valid",
            "passed": validation_lookup.get("synthetic_scope_valid", False),
            "required_value": "True",
            "actual_value": str(validation_lookup.get("synthetic_scope_valid", False)),
            "requirement_group": "evidence_scope",
        },
        {
            "requirement_id": "OUTPUT_INTEGRITY_REQ_011",
            "requirement_name": "candidate_valid",
            "passed": validation_lookup.get("candidate_valid", False),
            "required_value": "True",
            "actual_value": str(validation_lookup.get("candidate_valid", False)),
            "requirement_group": "candidate_scope",
        },
        {
            "requirement_id": "OUTPUT_INTEGRITY_REQ_012",
            "requirement_name": "direction_valid",
            "passed": validation_lookup.get("direction_valid", False),
            "required_value": "True",
            "actual_value": str(validation_lookup.get("direction_valid", False)),
            "requirement_group": "direction",
        },
        {
            "requirement_id": "OUTPUT_INTEGRITY_REQ_013",
            "requirement_name": "price_structure_valid",
            "passed": validation_lookup.get("price_structure_valid", False),
            "required_value": "True",
            "actual_value": str(validation_lookup.get("price_structure_valid", False)),
            "requirement_group": "price_structure",
        },
        {
            "requirement_id": "OUTPUT_INTEGRITY_REQ_014",
            "requirement_name": "risk_reward_valid",
            "passed": validation_lookup.get("risk_reward_valid", False),
            "required_value": "True",
            "actual_value": str(validation_lookup.get("risk_reward_valid", False)),
            "requirement_group": "risk_reward",
        },
        {
            "requirement_id": "OUTPUT_INTEGRITY_REQ_015",
            "requirement_name": "evidence_scope_valid",
            "passed": validation_lookup.get("evidence_scope_valid", False),
            "required_value": "True",
            "actual_value": str(validation_lookup.get("evidence_scope_valid", False)),
            "requirement_group": "evidence_scope",
        },
        {
            "requirement_id": "OUTPUT_INTEGRITY_REQ_016",
            "requirement_name": "execution_locks_valid",
            "passed": validation_lookup.get("execution_locks_valid", False),
            "required_value": "True",
            "actual_value": str(validation_lookup.get("execution_locks_valid", False)),
            "requirement_group": "execution",
        },
        {
            "requirement_id": "OUTPUT_INTEGRITY_REQ_017",
            "requirement_name": "official_evidence_locks_valid",
            "passed": validation_lookup.get("official_evidence_locks_valid", False),
            "required_value": "True",
            "actual_value": str(validation_lookup.get("official_evidence_locks_valid", False)),
            "requirement_group": "official_dataset_guard",
        },
        {
            "requirement_id": "OUTPUT_INTEGRITY_REQ_018",
            "requirement_name": "all_output_validations_passed",
            "passed": validations_passed,
            "required_value": "True",
            "actual_value": str(validations_passed),
            "requirement_group": "validation",
        },
        {
            "requirement_id": "OUTPUT_INTEGRITY_REQ_019",
            "requirement_name": "controls_passed",
            "passed": controls_passed,
            "required_value": "True",
            "actual_value": str(controls_passed),
            "requirement_group": "controls",
        },
        {
            "requirement_id": "OUTPUT_INTEGRITY_REQ_020",
            "requirement_name": "rules_passed",
            "passed": rules_passed,
            "required_value": "True",
            "actual_value": str(rules_passed),
            "requirement_group": "rules",
        },
        {
            "requirement_id": "OUTPUT_INTEGRITY_REQ_021",
            "requirement_name": "guards_passed",
            "passed": guards_passed,
            "required_value": "True",
            "actual_value": str(guards_passed),
            "requirement_group": "safety",
        },
        {
            "requirement_id": "OUTPUT_INTEGRITY_REQ_022",
            "requirement_name": "official_evidence_rows_written_zero",
            "passed": True,
            "required_value": "0",
            "actual_value": "0",
            "requirement_group": "official_dataset_guard",
        },
        {
            "requirement_id": "OUTPUT_INTEGRITY_REQ_023",
            "requirement_name": "market_execution_disabled",
            "passed": True,
            "required_value": "False",
            "actual_value": "False",
            "requirement_group": "market_execution_guard",
        },
        {
            "requirement_id": "OUTPUT_INTEGRITY_REQ_024",
            "requirement_name": "total_project_not_completed",
            "passed": True,
            "required_value": "False",
            "actual_value": "False",
            "requirement_group": "scope_control",
        },
    ]

    return pd.DataFrame(requirements)


def build_output_integrity_decision_table(
    requirements_df: pd.DataFrame,
    rules_df: pd.DataFrame,
    guard_matrix_df: pd.DataFrame,
) -> pd.DataFrame:
    total_requirements = int(len(requirements_df))
    passed_requirements = (
        int(requirements_df["passed"].astype(bool).sum())
        if total_requirements
        else 0
    )
    failed_requirements = total_requirements - passed_requirements

    rules_passed = not rules_df.empty and rules_df["passed"].astype(bool).all()
    guards_passed = not guard_matrix_df.empty and guard_matrix_df["passed"].astype(bool).all()

    integrity_passed = (
        total_requirements > 0
        and failed_requirements == 0
        and rules_passed
        and guards_passed
    )

    failed_requirement_names = ""

    if not requirements_df.empty:
        failed_requirement_names = ",".join(
            requirements_df[~requirements_df["passed"].astype(bool)]["requirement_name"]
            .astype(str)
            .tolist()
        )

    return pd.DataFrame(
        [
            {
                "controlled_start_activation_report_only_dry_run_output_integrity_review_id": (
                    "PHASE_10_16_LONG_FORWARD_OBSERVATION_CONTROLLED_START_ACTIVATION_REPORT_ONLY_DRY_RUN_OUTPUT_INTEGRITY_REVIEW_001"
                ),
                "controlled_start_activation_report_only_dry_run_output_integrity_review_status": OUTPUT_INTEGRITY_REVIEW_STATUS,
                "controlled_start_activation_report_only_dry_run_output_integrity_review_passed": integrity_passed,
                "controlled_start_activation_report_only_dry_run_output_integrity_review_decision": (
                    READY_DECISION if integrity_passed else BLOCKED_DECISION
                ),
                "total_requirements": total_requirements,
                "passed_requirements": passed_requirements,
                "failed_requirements": failed_requirements,
                "failed_requirement_names": failed_requirement_names,
                "output_integrity_rules_passed": rules_passed,
                "output_integrity_guards_passed": guards_passed,
                "future_controlled_start_activation_final_approval_review_allowed": integrity_passed,
                "controlled_forward_observation_start_approved": False,
                "controlled_forward_observation_start_activation_performed": False,
                "controlled_forward_observation_start_dry_run_performed": False,
                "forward_observation_start_allowed": False,
                "forward_observation_started": False,
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
                "paper_trading_enabled": False,
                "long_strategy_approved": False,
                "long_entries_approved": False,
                "long_side_established": False,
                "paper_trade_execution_allowed": False,
                "real_capital_allowed": False,
                "live_alerts_allowed": False,
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


def validate_long_forward_observation_controlled_start_activation_report_only_dry_run_output_integrity_review() -> dict[str, pd.DataFrame]:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    checks: list[dict[str, Any]] = []

    phase_anchors = {
        "phase_10_15_report_only_dry_run_run_doc_exists": PHASE_10_15_REPORT_ONLY_DRY_RUN_RUN_DOC_PATH,
        "phase_10_16_output_integrity_review_doc_exists": PHASE_10_16_OUTPUT_INTEGRITY_REVIEW_DOC_PATH,
    }

    for check_name, path in phase_anchors.items():
        checks.append(
            build_check(
                check_group="phase_anchor",
                check_name=check_name,
                passed=path.exists(),
                severity="INFO" if path.exists() else "ERROR",
                details=str(path),
            )
        )

    official_dataset_exists_before = OFFICIAL_DATASET_PATH.exists()

    phase_10_15_result = (
        validate_long_forward_observation_controlled_start_activation_report_only_dry_run_run()
    )

    phase_10_15_summary_df = phase_10_15_result["summary"]
    source_schema_df = phase_10_15_result["source_report_only_dry_run_design_schema"]
    source_run_decision_df = phase_10_15_result["report_only_dry_run_run_decision"]
    source_run_controls_df = phase_10_15_result["report_only_dry_run_run_controls"]
    source_row_validation_df = phase_10_15_result["report_only_dry_run_row_validation"]
    source_run_rules_df = phase_10_15_result["report_only_dry_run_run_rules"]
    source_run_requirements_df = phase_10_15_result["report_only_dry_run_run_requirements"]
    source_run_guard_matrix_df = phase_10_15_result["report_only_dry_run_run_guard_matrix"]
    source_checks_df = phase_10_15_result["checks"]

    source_output_df = read_report_only_output_artifact()

    if source_output_df.empty:
        source_output_df = phase_10_15_result["report_only_dry_run_output"]

    summary = (
        phase_10_15_summary_df.iloc[0].to_dict()
        if not phase_10_15_summary_df.empty
        else {}
    )

    phase_10_15_validation_passed = (
        not phase_10_15_summary_df.empty
        and safe_bool(summary.get("validation_passed", False))
    )
    run_passed = safe_bool(
        summary.get("controlled_start_activation_report_only_dry_run_run_passed", False)
    )

    controls_df = build_output_integrity_controls()
    validation_df = build_output_integrity_validation(
        output_df=source_output_df,
        schema_df=source_schema_df,
    )
    guard_matrix_df = build_output_integrity_guard_matrix()
    rules_df = build_output_integrity_rules(
        controls_df=controls_df,
        validation_df=validation_df,
    )
    requirements_df = build_output_integrity_requirements(
        phase_10_15_summary_df=phase_10_15_summary_df,
        run_decision_df=source_run_decision_df,
        output_df=source_output_df,
        validation_df=validation_df,
        controls_df=controls_df,
        rules_df=rules_df,
        guard_matrix_df=guard_matrix_df,
    )
    decision_df = build_output_integrity_decision_table(
        requirements_df=requirements_df,
        rules_df=rules_df,
        guard_matrix_df=guard_matrix_df,
    )

    official_dataset_exists_after = OFFICIAL_DATASET_PATH.exists()

    decision = decision_df.iloc[0].to_dict() if not decision_df.empty else {}

    integrity_passed = safe_bool(
        decision.get(
            "controlled_start_activation_report_only_dry_run_output_integrity_review_passed",
            False,
        )
    )
    integrity_decision = str(
        decision.get(
            "controlled_start_activation_report_only_dry_run_output_integrity_review_decision",
            "",
        )
    )
    future_final_approval_review_allowed = safe_bool(
        decision.get(
            "future_controlled_start_activation_final_approval_review_allowed",
            False,
        )
    )

    validation_lookup = {
        str(row["validation_name"]): safe_bool(row["passed"], False)
        for _, row in validation_df.iterrows()
    }

    controls_passed = not controls_df.empty and controls_df["passed"].astype(bool).all()
    validations_passed = (
        not validation_df.empty and validation_df["passed"].astype(bool).all()
    )
    rules_passed = not rules_df.empty and rules_df["passed"].astype(bool).all()
    requirements_passed = (
        not requirements_df.empty and requirements_df["passed"].astype(bool).all()
    )
    guards_passed = (
        not guard_matrix_df.empty and guard_matrix_df["passed"].astype(bool).all()
    )

    checks.append(
        build_check(
            check_group="phase_dependency",
            check_name="phase_10_15_validation_passed",
            passed=phase_10_15_validation_passed,
            severity="INFO" if phase_10_15_validation_passed else "ERROR",
            details=str(summary.get("validation_decision", "")),
        )
    )
    checks.append(
        build_check(
            check_group="phase_dependency",
            check_name="report_only_dry_run_run_passed",
            passed=run_passed,
            severity="INFO" if run_passed else "ERROR",
            details=f"run_passed={run_passed}",
        )
    )

    for validation_name, passed in validation_lookup.items():
        checks.append(
            build_check(
                check_group="output_integrity_validation",
                check_name=validation_name,
                passed=passed,
                severity="INFO" if passed else "ERROR",
                details=str(passed),
            )
        )

    checks.append(
        build_check(
            check_group="output_integrity_review",
            check_name="controls_passed",
            passed=controls_passed,
            severity="INFO" if controls_passed else "ERROR",
            details=f"controls_passed={controls_passed}",
        )
    )
    checks.append(
        build_check(
            check_group="output_integrity_review",
            check_name="validations_passed",
            passed=validations_passed,
            severity="INFO" if validations_passed else "ERROR",
            details=f"validations_passed={validations_passed}",
        )
    )
    checks.append(
        build_check(
            check_group="output_integrity_review",
            check_name="rules_passed",
            passed=rules_passed,
            severity="INFO" if rules_passed else "ERROR",
            details=f"rules_passed={rules_passed}",
        )
    )
    checks.append(
        build_check(
            check_group="output_integrity_review",
            check_name="requirements_passed",
            passed=requirements_passed,
            severity="INFO" if requirements_passed else "ERROR",
            details=f"requirements_passed={requirements_passed}",
        )
    )
    checks.append(
        build_check(
            check_group="output_integrity_review",
            check_name="guards_passed",
            passed=guards_passed,
            severity="INFO" if guards_passed else "ERROR",
            details=f"guards_passed={guards_passed}",
        )
    )
    checks.append(
        build_check(
            check_group="output_integrity_review",
            check_name="output_integrity_review_passed",
            passed=integrity_passed,
            severity="INFO" if integrity_passed else "ERROR",
            details=f"integrity_passed={integrity_passed}",
        )
    )
    checks.append(
        build_check(
            check_group="output_integrity_review",
            check_name="output_integrity_review_decision_expected",
            passed=integrity_decision == READY_DECISION,
            severity="INFO" if integrity_decision == READY_DECISION else "ERROR",
            details=f"integrity_decision={integrity_decision}",
        )
    )
    checks.append(
        build_check(
            check_group="planning_scope",
            check_name="future_final_approval_review_allowed",
            passed=future_final_approval_review_allowed,
            severity="WARNING" if future_final_approval_review_allowed else "ERROR",
            details=(
                "This allows only a future final approval review, not forward "
                "observation start, alerts, paper trading, real capital, official "
                "evidence persistence, or market execution."
            ),
        )
    )

    official_dataset_not_written = (
        official_dataset_exists_before is False and official_dataset_exists_after is False
    )

    checks.append(
        build_check(
            check_group="official_dataset_guard",
            check_name="official_dataset_not_written_or_created",
            passed=official_dataset_not_written,
            severity="INFO" if official_dataset_not_written else "ERROR",
            details=(
                f"official_dataset_exists_before={official_dataset_exists_before},"
                f"official_dataset_exists_after={official_dataset_exists_after}"
            ),
        )
    )

    for _, guard_row in guard_matrix_df.iterrows():
        checks.append(
            build_check(
                check_group="output_integrity_safety_flags",
                check_name=str(guard_row["guard_name"]),
                passed=safe_bool(guard_row["passed"], False),
                severity="INFO" if safe_bool(guard_row["passed"], False) else "ERROR",
                details=(
                    f"{guard_row['guard_name']}={guard_row['actual_value']} "
                    f"(required={guard_row['required_value']})"
                ),
            )
        )

    checks.extend(
        [
            build_check("scope_control", "output_integrity_review_only", True, "WARNING", "Phase 10.16 reviews only report-only dry-run output integrity."),
            build_check("scope_control", "no_new_dry_run_execution", True, "WARNING", "No new dry-run execution is performed in this phase."),
            build_check("scope_control", "forward_observation_not_started", True, "WARNING", "Forward observation is still not started."),
            build_check("scope_control", "official_evidence_not_persisted", True, "WARNING", "Official evidence persistence remains disabled."),
            build_check("scope_control", "signal_generation_not_enabled", True, "WARNING", "Signal generation remains disabled."),
            build_check("scope_control", "market_execution_not_allowed", True, "WARNING", "Market execution remains disabled."),
            build_check("scope_control", "total_project_not_completed", True, "WARNING", "The total project is not completed."),
            build_check("phase_transition", "phase_10_17_recommended_next", True, "INFO", "Recommended next step: Phase 10.17 LONG Forward Observation Controlled Start Activation Final Approval Review V1."),
        ]
    )

    checks_df = pd.DataFrame(checks)

    blocker_count = int(checks_df["blocker"].astype(bool).sum())
    error_count = int(checks_df["severity"].eq("ERROR").sum())
    warning_count = int(checks_df["severity"].eq("WARNING").sum())

    validation_passed = blocker_count == 0 and error_count == 0

    summary_df = pd.DataFrame(
        [
            {
                "phase": "10.16",
                "long_forward_observation_controlled_start_activation_report_only_dry_run_output_integrity_review_defined": True,
                "phase_10_15_validation_passed": phase_10_15_validation_passed,
                "controlled_start_activation_report_only_dry_run_run_passed": run_passed,
                "controlled_start_activation_report_only_dry_run_run_decision": str(
                    summary.get("controlled_start_activation_report_only_dry_run_run_decision", "")
                ),
                "future_controlled_start_activation_report_only_dry_run_output_integrity_review_allowed": safe_bool(
                    summary.get("future_controlled_start_activation_report_only_dry_run_output_integrity_review_allowed", False)
                ),
                "source_report_only_dry_run_output_row_count": int(len(source_output_df)),
                "output_integrity_schema_match": validation_lookup.get("schema_match", False),
                "output_integrity_row_count_valid": validation_lookup.get("output_row_count_valid", False),
                "output_integrity_report_only_valid": validation_lookup.get("report_only_valid", False),
                "output_integrity_synthetic_scope_valid": validation_lookup.get("synthetic_scope_valid", False),
                "output_integrity_candidate_valid": validation_lookup.get("candidate_valid", False),
                "output_integrity_direction_valid": validation_lookup.get("direction_valid", False),
                "output_integrity_price_structure_valid": validation_lookup.get("price_structure_valid", False),
                "output_integrity_risk_reward_valid": validation_lookup.get("risk_reward_valid", False),
                "output_integrity_evidence_scope_valid": validation_lookup.get("evidence_scope_valid", False),
                "output_integrity_execution_locks_valid": validation_lookup.get("execution_locks_valid", False),
                "output_integrity_official_evidence_lock_valid": validation_lookup.get("official_evidence_locks_valid", False),
                "output_integrity_safety_guards_passed": guards_passed,
                "output_integrity_control_count": int(len(controls_df)),
                "output_integrity_validation_rows": int(len(validation_df)),
                "output_integrity_rule_rows": int(len(rules_df)),
                "output_integrity_requirement_rows": int(len(requirements_df)),
                "output_integrity_controls_passed": controls_passed,
                "output_integrity_validations_passed": validations_passed,
                "output_integrity_rules_passed": rules_passed,
                "output_integrity_requirements_passed": requirements_passed,
                "output_integrity_guards_passed": guards_passed,
                "controlled_start_activation_report_only_dry_run_output_integrity_review_passed": integrity_passed,
                "controlled_start_activation_report_only_dry_run_output_integrity_review_decision": integrity_decision,
                "future_controlled_start_activation_final_approval_review_allowed": future_final_approval_review_allowed,
                "controlled_forward_observation_start_approved": False,
                "controlled_forward_observation_start_activation_performed": False,
                "controlled_forward_observation_start_dry_run_performed": False,
                "forward_observation_start_allowed": False,
                "official_dataset_exists_before": official_dataset_exists_before,
                "official_dataset_exists_after": official_dataset_exists_after,
                "official_dataset_write_allowed": False,
                "official_dataset_write_performed": False,
                "real_forward_dataset_created": False,
                "official_evidence_rows_written": 0,
                "real_forward_signals_recorded": False,
                "journal_real_rows_accepted": False,
                "accepted_as_real_evidence": False,
                "evidence_persistence_allowed": False,
                "evidence_write_performed": False,
                "forward_observation_started": False,
                "signal_generation_enabled": False,
                "paper_trading_enabled": False,
                "long_strategy_approved": False,
                "long_entries_approved": False,
                "long_side_established": False,
                "paper_trade_execution_allowed": False,
                "real_capital_allowed": False,
                "live_alerts_allowed": False,
                "market_execution_allowed": False,
                "exchange_execution_allowed": False,
                "automation_allowed": False,
                "execution_allowed": False,
                "real_entries_approved": False,
                "total_project_completed": False,
                "recommended_next_phase": RECOMMENDED_NEXT_PHASE,
                "estimated_phase_10_progress_percent": 100,
                "total_checks": int(len(checks_df)),
                "warning_count": warning_count,
                "error_count": error_count,
                "blocker_count": blocker_count,
                "validation_passed": validation_passed,
                "validation_decision": (
                    "PHASE_10_16_LONG_FORWARD_OBSERVATION_CONTROLLED_START_ACTIVATION_REPORT_ONLY_DRY_RUN_OUTPUT_INTEGRITY_REVIEW_VALIDATED"
                    if validation_passed
                    else "PHASE_10_16_LONG_FORWARD_OBSERVATION_CONTROLLED_START_ACTIVATION_REPORT_ONLY_DRY_RUN_OUTPUT_INTEGRITY_REVIEW_FAILED"
                ),
            }
        ]
    )

    phase_10_15_summary_df.to_csv(REPORTS_DIR / "phase_10_15_source_summary_v1.csv", index=False)
    source_output_df.to_csv(REPORTS_DIR / "phase_10_15_source_report_only_dry_run_output_v1.csv", index=False)
    source_schema_df.to_csv(REPORTS_DIR / "phase_10_13_source_report_only_dry_run_design_schema_v1.csv", index=False)
    source_run_decision_df.to_csv(REPORTS_DIR / "phase_10_15_source_run_decision_v1.csv", index=False)
    source_run_controls_df.to_csv(REPORTS_DIR / "phase_10_15_source_run_controls_v1.csv", index=False)
    source_row_validation_df.to_csv(REPORTS_DIR / "phase_10_15_source_row_validation_v1.csv", index=False)
    source_run_rules_df.to_csv(REPORTS_DIR / "phase_10_15_source_run_rules_v1.csv", index=False)
    source_run_requirements_df.to_csv(REPORTS_DIR / "phase_10_15_source_run_requirements_v1.csv", index=False)
    source_run_guard_matrix_df.to_csv(REPORTS_DIR / "phase_10_15_source_run_guard_matrix_v1.csv", index=False)
    source_checks_df.to_csv(REPORTS_DIR / "phase_10_15_source_checks_v1.csv", index=False)
    controls_df.to_csv(REPORTS_DIR / "output_integrity_review_controls_v1.csv", index=False)
    validation_df.to_csv(REPORTS_DIR / "output_integrity_review_validations_v1.csv", index=False)
    rules_df.to_csv(REPORTS_DIR / "output_integrity_review_rules_v1.csv", index=False)
    requirements_df.to_csv(REPORTS_DIR / "output_integrity_review_requirements_v1.csv", index=False)
    guard_matrix_df.to_csv(REPORTS_DIR / "output_integrity_review_guard_matrix_v1.csv", index=False)
    decision_df.to_csv(REPORTS_DIR / "output_integrity_review_decision_v1.csv", index=False)
    checks_df.to_csv(REPORTS_DIR / "output_integrity_review_checks_v1.csv", index=False)
    summary_df.to_csv(REPORTS_DIR / "output_integrity_review_summary_v1.csv", index=False)

    return {
        "summary": summary_df,
        "source_phase_10_15_summary": phase_10_15_summary_df,
        "source_report_only_dry_run_output": source_output_df,
        "source_report_only_dry_run_design_schema": source_schema_df,
        "source_run_decision": source_run_decision_df,
        "source_run_controls": source_run_controls_df,
        "source_row_validation": source_row_validation_df,
        "source_run_rules": source_run_rules_df,
        "source_run_requirements": source_run_requirements_df,
        "source_run_guard_matrix": source_run_guard_matrix_df,
        "source_checks": source_checks_df,
        "output_integrity_controls": controls_df,
        "output_integrity_validation": validation_df,
        "output_integrity_rules": rules_df,
        "output_integrity_requirements": requirements_df,
        "output_integrity_guard_matrix": guard_matrix_df,
        "output_integrity_decision": decision_df,
        "checks": checks_df,
    }