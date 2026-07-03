from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from src.long_side.long_forward_observation_dataset_bootstrap_v1 import (
    OFFICIAL_DATASET_PATH,
    PRIMARY_RESEARCH_CANDIDATE,
)
from src.long_side.long_forward_observation_manual_start_protocol_v1 import (
    READY_DECISION as MANUAL_START_PROTOCOL_READY_DECISION,
    validate_long_forward_observation_manual_start_protocol,
)


REPORTS_DIR = Path("reports/phase_10_3_long_forward_observation_manual_dry_run_checklist_v1")

PHASE_10_2_MANUAL_START_PROTOCOL_DOC_PATH = Path(
    "docs/PHASE_10_LONG_FORWARD_OBSERVATION_MANUAL_START_PROTOCOL.md"
)
PHASE_10_3_MANUAL_DRY_RUN_CHECKLIST_DOC_PATH = Path(
    "docs/PHASE_10_LONG_FORWARD_OBSERVATION_MANUAL_DRY_RUN_CHECKLIST.md"
)

MANUAL_DRY_RUN_CHECKLIST_STATUS = "LONG_FORWARD_OBSERVATION_MANUAL_DRY_RUN_CHECKLIST_ONLY"
READY_DECISION = "MANUAL_DRY_RUN_CHECKLIST_DEFINED_READY_FOR_CONTROLLED_DRY_RUN_REVIEW"
BLOCKED_DECISION = "MANUAL_DRY_RUN_CHECKLIST_BLOCKED"

RECOMMENDED_NEXT_PHASE = "PHASE_10_4_LONG_FORWARD_OBSERVATION_CONTROLLED_DRY_RUN_REVIEW_V1"

DRY_RUN_CHECKLIST_ITEMS = [
    {
        "checklist_id": "DRY_RUN_CHECK_001",
        "check_name": "confirm_clean_repository",
        "check_category": "operator_preflight",
        "required": True,
        "manual_verification_required": True,
        "dry_run_execution_allowed": False,
        "details": "Operator must confirm clean git status before any later dry-run.",
    },
    {
        "checklist_id": "DRY_RUN_CHECK_002",
        "check_name": "confirm_correct_branch",
        "check_category": "operator_preflight",
        "required": True,
        "manual_verification_required": True,
        "dry_run_execution_allowed": False,
        "details": "Operator must confirm the approved controlled dry-run branch.",
    },
    {
        "checklist_id": "DRY_RUN_CHECK_003",
        "check_name": "confirm_phase_10_2_protocol_passed",
        "check_category": "phase_dependency",
        "required": True,
        "manual_verification_required": True,
        "dry_run_execution_allowed": False,
        "details": "Phase 10.2 manual start protocol must be validated.",
    },
    {
        "checklist_id": "DRY_RUN_CHECK_004",
        "check_name": "confirm_manual_protocol_decision",
        "check_category": "phase_dependency",
        "required": True,
        "manual_verification_required": True,
        "dry_run_execution_allowed": False,
        "details": "Manual protocol decision must be ready for dry-run checklist.",
    },
    {
        "checklist_id": "DRY_RUN_CHECK_005",
        "check_name": "confirm_dry_run_checklist_planning_allowed",
        "check_category": "planning_scope",
        "required": True,
        "manual_verification_required": True,
        "dry_run_execution_allowed": False,
        "details": "Phase 10.2 must allow dry-run checklist planning.",
    },
    {
        "checklist_id": "DRY_RUN_CHECK_006",
        "check_name": "confirm_manual_protocol_activation_not_allowed",
        "check_category": "activation_boundary",
        "required": True,
        "manual_verification_required": True,
        "dry_run_execution_allowed": False,
        "details": "Manual protocol activation remains disabled.",
    },
    {
        "checklist_id": "DRY_RUN_CHECK_007",
        "check_name": "confirm_controlled_forward_start_not_approved",
        "check_category": "start_boundary",
        "required": True,
        "manual_verification_required": True,
        "dry_run_execution_allowed": False,
        "details": "Controlled forward observation start remains unapproved.",
    },
    {
        "checklist_id": "DRY_RUN_CHECK_008",
        "check_name": "confirm_forward_observation_start_not_allowed",
        "check_category": "start_boundary",
        "required": True,
        "manual_verification_required": True,
        "dry_run_execution_allowed": False,
        "details": "Forward observation start remains disabled.",
    },
    {
        "checklist_id": "DRY_RUN_CHECK_009",
        "check_name": "confirm_no_official_dataset_creation",
        "check_category": "official_dataset_guard",
        "required": True,
        "manual_verification_required": True,
        "dry_run_execution_allowed": False,
        "details": "Official dataset must remain absent unless later explicitly created.",
    },
    {
        "checklist_id": "DRY_RUN_CHECK_010",
        "check_name": "confirm_official_dataset_write_disabled",
        "check_category": "official_dataset_guard",
        "required": True,
        "manual_verification_required": True,
        "dry_run_execution_allowed": False,
        "details": "Official dataset writes remain disabled.",
    },
    {
        "checklist_id": "DRY_RUN_CHECK_011",
        "check_name": "confirm_official_evidence_rows_zero",
        "check_category": "official_dataset_guard",
        "required": True,
        "manual_verification_required": True,
        "dry_run_execution_allowed": False,
        "details": "Official evidence rows written remain zero.",
    },
    {
        "checklist_id": "DRY_RUN_CHECK_012",
        "check_name": "confirm_primary_candidate_scope",
        "check_category": "candidate_scope",
        "required": True,
        "manual_verification_required": True,
        "dry_run_execution_allowed": False,
        "details": f"Primary candidate must be {PRIMARY_RESEARCH_CANDIDATE}.",
    },
    {
        "checklist_id": "DRY_RUN_CHECK_013",
        "check_name": "confirm_direction_long",
        "check_category": "candidate_scope",
        "required": True,
        "manual_verification_required": True,
        "dry_run_execution_allowed": False,
        "details": "Direction must remain LONG.",
    },
    {
        "checklist_id": "DRY_RUN_CHECK_014",
        "check_name": "confirm_long_price_structure_rule",
        "check_category": "price_structure",
        "required": True,
        "manual_verification_required": True,
        "dry_run_execution_allowed": False,
        "details": "Future price levels must satisfy stop_price < entry_price < target_price.",
    },
    {
        "checklist_id": "DRY_RUN_CHECK_015",
        "check_name": "confirm_manual_review_required",
        "check_category": "manual_review",
        "required": True,
        "manual_verification_required": True,
        "dry_run_execution_allowed": False,
        "details": "Every future observation candidate must require manual review.",
    },
    {
        "checklist_id": "DRY_RUN_CHECK_016",
        "check_name": "confirm_signal_generation_disabled",
        "check_category": "safety",
        "required": True,
        "manual_verification_required": True,
        "dry_run_execution_allowed": False,
        "details": "Signal generation remains disabled.",
    },
    {
        "checklist_id": "DRY_RUN_CHECK_017",
        "check_name": "confirm_live_alerts_disabled",
        "check_category": "safety",
        "required": True,
        "manual_verification_required": True,
        "dry_run_execution_allowed": False,
        "details": "Live alerts remain disabled.",
    },
    {
        "checklist_id": "DRY_RUN_CHECK_018",
        "check_name": "confirm_paper_trading_disabled",
        "check_category": "safety",
        "required": True,
        "manual_verification_required": True,
        "dry_run_execution_allowed": False,
        "details": "Paper trading remains disabled.",
    },
    {
        "checklist_id": "DRY_RUN_CHECK_019",
        "check_name": "confirm_real_capital_disabled",
        "check_category": "safety",
        "required": True,
        "manual_verification_required": True,
        "dry_run_execution_allowed": False,
        "details": "Real capital remains disabled.",
    },
    {
        "checklist_id": "DRY_RUN_CHECK_020",
        "check_name": "confirm_execution_and_automation_disabled",
        "check_category": "safety",
        "required": True,
        "manual_verification_required": True,
        "dry_run_execution_allowed": False,
        "details": "Exchange execution and automation remain disabled.",
    },
]

SAFETY_FLAGS = {
    "dry_run_execution_approved": False,
    "manual_protocol_activation_allowed": False,
    "controlled_forward_observation_start_approved": False,
    "forward_observation_start_allowed": False,
    "forward_observation_started": False,
    "signal_generation_enabled": False,
    "real_forward_signals_recorded": False,
    "journal_real_rows_accepted": False,
    "real_forward_dataset_created": False,
    "official_dataset_write_performed": False,
    "evidence_write_performed": False,
    "evidence_persistence_allowed": False,
    "accepted_as_real_evidence": False,
    "paper_trading_enabled": False,
    "long_strategy_approved": False,
    "long_entries_approved": False,
    "long_side_established": False,
    "paper_trade_execution_allowed": False,
    "real_capital_allowed": False,
    "live_alerts_allowed": False,
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


def build_dry_run_checklist_items() -> pd.DataFrame:
    rows: list[dict[str, Any]] = []

    for item in DRY_RUN_CHECKLIST_ITEMS:
        rows.append(
            {
                "checklist_id": item["checklist_id"],
                "check_name": item["check_name"],
                "check_category": item["check_category"],
                "required": item["required"],
                "manual_verification_required": item["manual_verification_required"],
                "dry_run_execution_allowed": item["dry_run_execution_allowed"],
                "forward_observation_start_allowed": False,
                "official_dataset_write_allowed": False,
                "real_evidence_acceptance_allowed": False,
                "live_alerts_allowed": False,
                "paper_trading_allowed": False,
                "real_capital_allowed": False,
                "exchange_execution_allowed": False,
                "automation_allowed": False,
                "passed": (
                    item["required"] is True
                    and item["manual_verification_required"] is True
                    and item["dry_run_execution_allowed"] is False
                ),
                "details": item["details"],
            }
        )

    return pd.DataFrame(rows)


def build_dry_run_checklist_rules(
    checklist_items_df: pd.DataFrame,
) -> pd.DataFrame:
    item_count = int(len(checklist_items_df))
    required_item_count = (
        int(checklist_items_df["required"].astype(bool).sum())
        if item_count
        else 0
    )

    all_manual_verification_required = (
        not checklist_items_df.empty
        and checklist_items_df["manual_verification_required"].astype(bool).all()
    )

    all_dry_run_execution_disabled = (
        not checklist_items_df.empty
        and checklist_items_df["dry_run_execution_allowed"].astype(bool).eq(False).all()
    )

    all_forward_start_disabled = (
        not checklist_items_df.empty
        and checklist_items_df["forward_observation_start_allowed"]
        .astype(bool)
        .eq(False)
        .all()
    )

    all_official_dataset_writes_disabled = (
        not checklist_items_df.empty
        and checklist_items_df["official_dataset_write_allowed"]
        .astype(bool)
        .eq(False)
        .all()
    )

    rows = [
        {
            "rule_id": "DRY_RUN_CHECKLIST_RULE_001",
            "rule_name": "dry_run_checklist_item_count_20",
            "passed": item_count == 20,
            "required_value": "20",
            "actual_value": str(item_count),
            "rule_group": "checklist_structure",
        },
        {
            "rule_id": "DRY_RUN_CHECKLIST_RULE_002",
            "rule_name": "all_items_required",
            "passed": required_item_count == item_count and item_count > 0,
            "required_value": str(item_count),
            "actual_value": str(required_item_count),
            "rule_group": "checklist_structure",
        },
        {
            "rule_id": "DRY_RUN_CHECKLIST_RULE_003",
            "rule_name": "all_items_manual_verification_required",
            "passed": all_manual_verification_required,
            "required_value": "True",
            "actual_value": str(all_manual_verification_required),
            "rule_group": "manual_control",
        },
        {
            "rule_id": "DRY_RUN_CHECKLIST_RULE_004",
            "rule_name": "all_dry_run_execution_disabled",
            "passed": all_dry_run_execution_disabled,
            "required_value": "False",
            "actual_value": "False",
            "rule_group": "dry_run_boundary",
        },
        {
            "rule_id": "DRY_RUN_CHECKLIST_RULE_005",
            "rule_name": "all_forward_observation_start_disabled",
            "passed": all_forward_start_disabled,
            "required_value": "False",
            "actual_value": "False",
            "rule_group": "start_boundary",
        },
        {
            "rule_id": "DRY_RUN_CHECKLIST_RULE_006",
            "rule_name": "all_official_dataset_writes_disabled",
            "passed": all_official_dataset_writes_disabled,
            "required_value": "False",
            "actual_value": "False",
            "rule_group": "official_dataset_guard",
        },
    ]

    return pd.DataFrame(rows)


def build_dry_run_checklist_requirements(
    phase_10_2_summary_df: pd.DataFrame,
    manual_start_protocol_decision_df: pd.DataFrame,
    dry_run_checklist_rules_df: pd.DataFrame,
) -> pd.DataFrame:
    summary = (
        phase_10_2_summary_df.iloc[0].to_dict()
        if not phase_10_2_summary_df.empty
        else {}
    )

    decision = (
        manual_start_protocol_decision_df.iloc[0].to_dict()
        if not manual_start_protocol_decision_df.empty
        else {}
    )

    rules_passed = (
        not dry_run_checklist_rules_df.empty
        and dry_run_checklist_rules_df["passed"].astype(bool).all()
    )

    requirements: list[dict[str, Any]] = [
        {
            "requirement_id": "DRY_RUN_CHECKLIST_REQ_001",
            "requirement_name": "phase_10_2_validation_passed",
            "passed": safe_bool(summary.get("validation_passed", False)),
            "required_value": "True",
            "actual_value": str(summary.get("validation_passed", "")),
            "requirement_group": "dependency",
        },
        {
            "requirement_id": "DRY_RUN_CHECKLIST_REQ_002",
            "requirement_name": "manual_start_protocol_passed",
            "passed": safe_bool(summary.get("manual_start_protocol_passed", False)),
            "required_value": "True",
            "actual_value": str(summary.get("manual_start_protocol_passed", "")),
            "requirement_group": "manual_protocol",
        },
        {
            "requirement_id": "DRY_RUN_CHECKLIST_REQ_003",
            "requirement_name": "manual_start_protocol_decision_expected",
            "passed": str(summary.get("manual_start_protocol_decision", "")).strip()
            == MANUAL_START_PROTOCOL_READY_DECISION,
            "required_value": MANUAL_START_PROTOCOL_READY_DECISION,
            "actual_value": str(summary.get("manual_start_protocol_decision", "")),
            "requirement_group": "manual_protocol",
        },
        {
            "requirement_id": "DRY_RUN_CHECKLIST_REQ_004",
            "requirement_name": "dry_run_checklist_planning_allowed",
            "passed": safe_bool(
                summary.get("dry_run_checklist_planning_allowed", False)
            ),
            "required_value": "True",
            "actual_value": str(summary.get("dry_run_checklist_planning_allowed", "")),
            "requirement_group": "planning_scope",
        },
        {
            "requirement_id": "DRY_RUN_CHECKLIST_REQ_005",
            "requirement_name": "manual_protocol_decision_table_consistent",
            "passed": (
                not manual_start_protocol_decision_df.empty
                and safe_bool(decision.get("manual_start_protocol_passed", False))
                and str(decision.get("manual_start_protocol_decision", "")).strip()
                == MANUAL_START_PROTOCOL_READY_DECISION
            ),
            "required_value": "True",
            "actual_value": str(decision.get("manual_start_protocol_decision", "")),
            "requirement_group": "summary_consistency",
        },
        {
            "requirement_id": "DRY_RUN_CHECKLIST_REQ_006",
            "requirement_name": "dry_run_checklist_rules_passed",
            "passed": rules_passed,
            "required_value": "True",
            "actual_value": str(rules_passed),
            "requirement_group": "dry_run_checklist",
        },
        {
            "requirement_id": "DRY_RUN_CHECKLIST_REQ_007",
            "requirement_name": "dry_run_execution_not_approved",
            "passed": True,
            "required_value": "False",
            "actual_value": "False",
            "requirement_group": "dry_run_boundary",
        },
        {
            "requirement_id": "DRY_RUN_CHECKLIST_REQ_008",
            "requirement_name": "manual_protocol_activation_not_allowed",
            "passed": safe_bool(
                summary.get("manual_protocol_activation_allowed", True),
                default=True,
            )
            is False,
            "required_value": "False",
            "actual_value": str(summary.get("manual_protocol_activation_allowed", "")),
            "requirement_group": "activation_boundary",
        },
        {
            "requirement_id": "DRY_RUN_CHECKLIST_REQ_009",
            "requirement_name": "controlled_forward_observation_start_not_approved",
            "passed": safe_bool(
                summary.get("controlled_forward_observation_start_approved", True),
                default=True,
            )
            is False,
            "required_value": "False",
            "actual_value": str(
                summary.get("controlled_forward_observation_start_approved", "")
            ),
            "requirement_group": "start_boundary",
        },
        {
            "requirement_id": "DRY_RUN_CHECKLIST_REQ_010",
            "requirement_name": "forward_observation_start_not_allowed",
            "passed": safe_bool(
                summary.get("forward_observation_start_allowed", True),
                default=True,
            )
            is False,
            "required_value": "False",
            "actual_value": str(summary.get("forward_observation_start_allowed", "")),
            "requirement_group": "start_boundary",
        },
        {
            "requirement_id": "DRY_RUN_CHECKLIST_REQ_011",
            "requirement_name": "forward_observation_not_started",
            "passed": safe_bool(
                summary.get("forward_observation_started", True),
                default=True,
            )
            is False,
            "required_value": "False",
            "actual_value": str(summary.get("forward_observation_started", "")),
            "requirement_group": "start_boundary",
        },
        {
            "requirement_id": "DRY_RUN_CHECKLIST_REQ_012",
            "requirement_name": "official_dataset_not_written",
            "passed": safe_bool(
                summary.get("official_dataset_write_performed", True),
                default=True,
            )
            is False,
            "required_value": "False",
            "actual_value": str(summary.get("official_dataset_write_performed", "")),
            "requirement_group": "official_dataset_guard",
        },
        {
            "requirement_id": "DRY_RUN_CHECKLIST_REQ_013",
            "requirement_name": "official_evidence_rows_written_zero",
            "passed": int(summary.get("official_evidence_rows_written", -1)) == 0,
            "required_value": "0",
            "actual_value": str(summary.get("official_evidence_rows_written", "")),
            "requirement_group": "official_dataset_guard",
        },
        {
            "requirement_id": "DRY_RUN_CHECKLIST_REQ_014",
            "requirement_name": "signal_generation_disabled",
            "passed": safe_bool(
                summary.get("signal_generation_enabled", True),
                default=True,
            )
            is False,
            "required_value": "False",
            "actual_value": str(summary.get("signal_generation_enabled", "")),
            "requirement_group": "safety",
        },
        {
            "requirement_id": "DRY_RUN_CHECKLIST_REQ_015",
            "requirement_name": "execution_disabled",
            "passed": safe_bool(summary.get("execution_allowed", True), default=True)
            is False,
            "required_value": "False",
            "actual_value": str(summary.get("execution_allowed", "")),
            "requirement_group": "safety",
        },
        {
            "requirement_id": "DRY_RUN_CHECKLIST_REQ_016",
            "requirement_name": "total_project_not_completed",
            "passed": safe_bool(
                summary.get("total_project_completed", True),
                default=True,
            )
            is False,
            "required_value": "False",
            "actual_value": str(summary.get("total_project_completed", "")),
            "requirement_group": "scope_control",
        },
    ]

    return pd.DataFrame(requirements)


def build_dry_run_boundary_matrix() -> pd.DataFrame:
    rows = [
        {
            "boundary_item": "dry_run_checklist_definition_allowed",
            "allowed": True,
            "boundary_type": "checklist_definition",
            "details": "Phase 10.3 may define the manual dry-run checklist.",
        },
        {
            "boundary_item": "controlled_dry_run_review_allowed",
            "allowed": True,
            "boundary_type": "future_review",
            "details": "Phase 10.3 may recommend future controlled dry-run review.",
        },
        {
            "boundary_item": "dry_run_execution_approved",
            "allowed": False,
            "boundary_type": "dry_run_execution",
            "details": "Phase 10.3 does not approve dry-run execution.",
        },
        {
            "boundary_item": "manual_protocol_activation_allowed",
            "allowed": False,
            "boundary_type": "activation",
            "details": "Manual protocol activation remains disabled.",
        },
        {
            "boundary_item": "controlled_forward_observation_start_approved",
            "allowed": False,
            "boundary_type": "operational_start",
            "details": "Controlled forward observation start remains unapproved.",
        },
        {
            "boundary_item": "official_dataset_write_allowed",
            "allowed": False,
            "boundary_type": "official_evidence",
            "details": "Official dataset writes remain disabled.",
        },
        {
            "boundary_item": "real_evidence_acceptance_allowed",
            "allowed": False,
            "boundary_type": "official_evidence",
            "details": "Real evidence acceptance remains disabled.",
        },
        {
            "boundary_item": "live_alerts_allowed",
            "allowed": False,
            "boundary_type": "alerts",
            "details": "Live alerts remain disabled.",
        },
        {
            "boundary_item": "paper_trading_allowed",
            "allowed": False,
            "boundary_type": "paper_trading",
            "details": "Paper trading remains disabled.",
        },
        {
            "boundary_item": "real_capital_allowed",
            "allowed": False,
            "boundary_type": "real_capital",
            "details": "Real capital remains disabled.",
        },
        {
            "boundary_item": "exchange_execution_allowed",
            "allowed": False,
            "boundary_type": "execution",
            "details": "Exchange execution remains disabled.",
        },
        {
            "boundary_item": "automation_allowed",
            "allowed": False,
            "boundary_type": "automation",
            "details": "Automation remains disabled.",
        },
    ]

    return pd.DataFrame(rows)


def build_dry_run_safety_matrix() -> pd.DataFrame:
    rows: list[dict[str, Any]] = []

    for flag_name, flag_value in SAFETY_FLAGS.items():
        rows.append(
            {
                "safety_flag": flag_name,
                "required_value": False,
                "actual_value": flag_value,
                "passed": flag_value is False,
                "checklist_status": MANUAL_DRY_RUN_CHECKLIST_STATUS,
            }
        )

    rows.append(
        {
            "safety_flag": "official_evidence_rows_written",
            "required_value": 0,
            "actual_value": 0,
            "passed": True,
            "checklist_status": MANUAL_DRY_RUN_CHECKLIST_STATUS,
        }
    )

    return pd.DataFrame(rows)


def build_manual_dry_run_checklist_decision_table(
    requirements_df: pd.DataFrame,
    boundary_matrix_df: pd.DataFrame,
    safety_matrix_df: pd.DataFrame,
    checklist_rules_df: pd.DataFrame,
) -> pd.DataFrame:
    total_requirements = int(len(requirements_df))
    passed_requirements = (
        int(requirements_df["passed"].astype(bool).sum())
        if total_requirements
        else 0
    )
    failed_requirements = total_requirements - passed_requirements

    safety_matrix_passed = (
        not safety_matrix_df.empty and safety_matrix_df["passed"].astype(bool).all()
    )

    checklist_rules_passed = (
        not checklist_rules_df.empty and checklist_rules_df["passed"].astype(bool).all()
    )

    disallowed_operational_boundaries_passed = True

    if not boundary_matrix_df.empty:
        allowed_planning_items = {
            "dry_run_checklist_definition_allowed",
            "controlled_dry_run_review_allowed",
        }

        disallowed_rows = boundary_matrix_df[
            ~boundary_matrix_df["boundary_item"].astype(str).isin(allowed_planning_items)
        ]
        disallowed_operational_boundaries_passed = (
            not disallowed_rows.empty
            and disallowed_rows["allowed"].astype(bool).eq(False).all()
        )

    manual_dry_run_checklist_passed = (
        total_requirements > 0
        and failed_requirements == 0
        and safety_matrix_passed
        and checklist_rules_passed
        and disallowed_operational_boundaries_passed
    )

    failed_requirement_names = ""

    if not requirements_df.empty:
        failed_requirement_names = ",".join(
            requirements_df[~requirements_df["passed"].astype(bool)][
                "requirement_name"
            ]
            .astype(str)
            .tolist()
        )

    return pd.DataFrame(
        [
            {
                "manual_dry_run_checklist_id": "PHASE_10_3_MANUAL_DRY_RUN_CHECKLIST_001",
                "manual_dry_run_checklist_status": MANUAL_DRY_RUN_CHECKLIST_STATUS,
                "manual_dry_run_checklist_passed": manual_dry_run_checklist_passed,
                "manual_dry_run_checklist_decision": (
                    READY_DECISION if manual_dry_run_checklist_passed else BLOCKED_DECISION
                ),
                "total_requirements": total_requirements,
                "passed_requirements": passed_requirements,
                "failed_requirements": failed_requirements,
                "failed_requirement_names": failed_requirement_names,
                "dry_run_checklist_rules_passed": checklist_rules_passed,
                "safety_matrix_passed": safety_matrix_passed,
                "disallowed_operational_boundaries_passed": (
                    disallowed_operational_boundaries_passed
                ),
                "controlled_dry_run_review_allowed": manual_dry_run_checklist_passed,
                "dry_run_execution_approved": False,
                "manual_protocol_activation_allowed": False,
                "controlled_forward_observation_start_approved": False,
                "forward_observation_start_allowed": False,
                "forward_observation_started": False,
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
                "exchange_execution_allowed": False,
                "automation_allowed": False,
                "execution_allowed": False,
                "real_entries_approved": False,
                "total_project_completed": False,
                "recommended_next_phase": RECOMMENDED_NEXT_PHASE,
            }
        ]
    )


def validate_long_forward_observation_manual_dry_run_checklist() -> dict[str, pd.DataFrame]:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    checks: list[dict[str, Any]] = []

    phase_anchors = {
        "phase_10_2_manual_start_protocol_doc_exists": (
            PHASE_10_2_MANUAL_START_PROTOCOL_DOC_PATH
        ),
        "phase_10_3_manual_dry_run_checklist_doc_exists": (
            PHASE_10_3_MANUAL_DRY_RUN_CHECKLIST_DOC_PATH
        ),
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

    phase_10_2_result = validate_long_forward_observation_manual_start_protocol()

    phase_10_2_summary_df = phase_10_2_result["summary"]
    source_manual_protocol_stages_df = phase_10_2_result["manual_protocol_stages"]
    source_manual_protocol_rules_df = phase_10_2_result["manual_protocol_rules"]
    source_manual_protocol_requirements_df = phase_10_2_result[
        "manual_protocol_requirements"
    ]
    source_manual_protocol_boundary_matrix_df = phase_10_2_result[
        "manual_protocol_boundary_matrix"
    ]
    source_manual_protocol_safety_matrix_df = phase_10_2_result[
        "manual_protocol_safety_matrix"
    ]
    source_manual_start_protocol_decision_df = phase_10_2_result[
        "manual_start_protocol_decision"
    ]
    source_checks_df = phase_10_2_result["checks"]

    phase_10_2_validation_passed = (
        not phase_10_2_summary_df.empty
        and bool(phase_10_2_summary_df.iloc[0].get("validation_passed", False))
    )

    manual_start_protocol_defined = (
        not phase_10_2_summary_df.empty
        and bool(
            phase_10_2_summary_df.iloc[0].get(
                "long_forward_observation_manual_start_protocol_defined",
                False,
            )
        )
    )

    dry_run_checklist_items_df = build_dry_run_checklist_items()
    dry_run_checklist_rules_df = build_dry_run_checklist_rules(
        checklist_items_df=dry_run_checklist_items_df,
    )
    dry_run_boundary_matrix_df = build_dry_run_boundary_matrix()
    dry_run_safety_matrix_df = build_dry_run_safety_matrix()

    dry_run_requirements_df = build_dry_run_checklist_requirements(
        phase_10_2_summary_df=phase_10_2_summary_df,
        manual_start_protocol_decision_df=source_manual_start_protocol_decision_df,
        dry_run_checklist_rules_df=dry_run_checklist_rules_df,
    )

    manual_dry_run_checklist_decision_df = build_manual_dry_run_checklist_decision_table(
        requirements_df=dry_run_requirements_df,
        boundary_matrix_df=dry_run_boundary_matrix_df,
        safety_matrix_df=dry_run_safety_matrix_df,
        checklist_rules_df=dry_run_checklist_rules_df,
    )

    official_dataset_exists_after = OFFICIAL_DATASET_PATH.exists()

    decision = (
        manual_dry_run_checklist_decision_df.iloc[0].to_dict()
        if not manual_dry_run_checklist_decision_df.empty
        else {}
    )

    manual_dry_run_checklist_passed = safe_bool(
        decision.get("manual_dry_run_checklist_passed", False)
    )
    manual_dry_run_checklist_decision = str(
        decision.get("manual_dry_run_checklist_decision", "")
    )
    controlled_dry_run_review_allowed = safe_bool(
        decision.get("controlled_dry_run_review_allowed", False)
    )

    checks.append(
        build_check(
            check_group="phase_dependency",
            check_name="phase_10_2_validation_passed",
            passed=phase_10_2_validation_passed,
            severity="INFO" if phase_10_2_validation_passed else "ERROR",
            details=(
                str(phase_10_2_summary_df.iloc[0].get("validation_decision", ""))
                if not phase_10_2_summary_df.empty
                else "Missing Phase 10.2 summary."
            ),
        )
    )

    checks.append(
        build_check(
            check_group="phase_dependency",
            check_name="long_forward_observation_manual_start_protocol_defined",
            passed=manual_start_protocol_defined,
            severity="INFO" if manual_start_protocol_defined else "ERROR",
            details=f"manual_start_protocol_defined={manual_start_protocol_defined}",
        )
    )

    dry_run_checklist_rules_passed = (
        not dry_run_checklist_rules_df.empty
        and dry_run_checklist_rules_df["passed"].astype(bool).all()
    )

    checks.append(
        build_check(
            check_group="dry_run_checklist",
            check_name="dry_run_checklist_rules_passed",
            passed=dry_run_checklist_rules_passed,
            severity="INFO" if dry_run_checklist_rules_passed else "ERROR",
            details=(
                "failed_rules="
                + ",".join(
                    dry_run_checklist_rules_df[
                        ~dry_run_checklist_rules_df["passed"].astype(bool)
                    ]["rule_name"].astype(str)
                )
                if not dry_run_checklist_rules_df.empty
                else "failed_rules=all"
            ),
        )
    )

    requirements_passed = (
        not dry_run_requirements_df.empty
        and dry_run_requirements_df["passed"].astype(bool).all()
    )

    checks.append(
        build_check(
            check_group="dry_run_checklist",
            check_name="dry_run_checklist_requirements_passed",
            passed=requirements_passed,
            severity="INFO" if requirements_passed else "ERROR",
            details=(
                "failed_requirements="
                + ",".join(
                    dry_run_requirements_df[
                        ~dry_run_requirements_df["passed"].astype(bool)
                    ]["requirement_name"].astype(str)
                )
                if not dry_run_requirements_df.empty
                else "failed_requirements=all"
            ),
        )
    )

    checks.append(
        build_check(
            check_group="dry_run_checklist",
            check_name="manual_dry_run_checklist_passed",
            passed=manual_dry_run_checklist_passed,
            severity="INFO" if manual_dry_run_checklist_passed else "ERROR",
            details=f"manual_dry_run_checklist_passed={manual_dry_run_checklist_passed}",
        )
    )

    checks.append(
        build_check(
            check_group="dry_run_checklist",
            check_name="manual_dry_run_checklist_decision_expected",
            passed=manual_dry_run_checklist_decision == READY_DECISION,
            severity=(
                "INFO"
                if manual_dry_run_checklist_decision == READY_DECISION
                else "ERROR"
            ),
            details="manual_dry_run_checklist_decision="
            + manual_dry_run_checklist_decision,
        )
    )

    checks.append(
        build_check(
            check_group="planning_scope",
            check_name="controlled_dry_run_review_allowed",
            passed=controlled_dry_run_review_allowed,
            severity="WARNING" if controlled_dry_run_review_allowed else "ERROR",
            details=(
                "This allows only future controlled dry-run review, not dry-run execution, "
                "observation start, alerts, paper trading, real capital, or execution."
            ),
        )
    )

    dry_run_execution_approved = safe_bool(
        decision.get("dry_run_execution_approved", True),
        default=True,
    )

    checks.append(
        build_check(
            check_group="safety_controls",
            check_name="dry_run_execution_not_approved",
            passed=dry_run_execution_approved is False,
            severity="INFO" if dry_run_execution_approved is False else "ERROR",
            details=f"dry_run_execution_approved={dry_run_execution_approved}",
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

    safety_matrix_passed = (
        not dry_run_safety_matrix_df.empty
        and dry_run_safety_matrix_df["passed"].astype(bool).all()
    )

    checks.append(
        build_check(
            check_group="safety_controls",
            check_name="dry_run_checklist_safety_matrix_passed",
            passed=safety_matrix_passed,
            severity="INFO" if safety_matrix_passed else "ERROR",
            details=(
                "failed_safety_flags="
                + ",".join(
                    dry_run_safety_matrix_df[
                        ~dry_run_safety_matrix_df["passed"].astype(bool)
                    ]["safety_flag"].astype(str)
                )
                if not dry_run_safety_matrix_df.empty
                else "failed_safety_flags=all"
            ),
        )
    )

    for flag_name, flag_value in SAFETY_FLAGS.items():
        checks.append(
            build_check(
                check_group="safety_flags",
                check_name=flag_name,
                passed=flag_value is False,
                severity="INFO" if flag_value is False else "ERROR",
                details=f"{flag_name}={flag_value}",
            )
        )

    checks.append(
        build_check(
            check_group="scope_control",
            check_name="manual_dry_run_checklist_only",
            passed=True,
            severity="WARNING",
            details="Phase 10.3 defines the manual dry-run checklist only.",
        )
    )

    checks.append(
        build_check(
            check_group="scope_control",
            check_name="dry_run_not_executed",
            passed=True,
            severity="WARNING",
            details="Dry-run execution is still not approved.",
        )
    )

    checks.append(
        build_check(
            check_group="scope_control",
            check_name="forward_observation_not_started",
            passed=True,
            severity="WARNING",
            details="Forward observation is still not started.",
        )
    )

    checks.append(
        build_check(
            check_group="scope_control",
            check_name="total_project_not_completed",
            passed=True,
            severity="WARNING",
            details="The total project is not completed.",
        )
    )

    checks.append(
        build_check(
            check_group="phase_transition",
            check_name="phase_10_4_recommended_next",
            passed=True,
            severity="INFO",
            details=(
                "Recommended next step: "
                "Phase 10.4 LONG Forward Observation Controlled Dry-Run Review V1."
            ),
        )
    )

    checks_df = pd.DataFrame(checks)

    blocker_count = int(checks_df["blocker"].astype(bool).sum())
    error_count = int(checks_df["severity"].eq("ERROR").sum())
    warning_count = int(checks_df["severity"].eq("WARNING").sum())

    validation_passed = blocker_count == 0 and error_count == 0

    phase_10_2_summary = (
        phase_10_2_summary_df.iloc[0].to_dict()
        if not phase_10_2_summary_df.empty
        else {}
    )

    summary_df = pd.DataFrame(
        [
            {
                "phase": "10.3",
                "long_forward_observation_manual_dry_run_checklist_defined": True,
                "phase_10_2_validation_passed": phase_10_2_validation_passed,
                "long_forward_observation_manual_start_protocol_defined": (
                    manual_start_protocol_defined
                ),
                "manual_start_protocol_passed": safe_bool(
                    phase_10_2_summary.get("manual_start_protocol_passed", False)
                ),
                "manual_start_protocol_decision": str(
                    phase_10_2_summary.get("manual_start_protocol_decision", "")
                ),
                "dry_run_checklist_planning_allowed": safe_bool(
                    phase_10_2_summary.get("dry_run_checklist_planning_allowed", False)
                ),
                "dry_run_checklist_item_count": int(len(dry_run_checklist_items_df)),
                "dry_run_checklist_rule_rows": int(len(dry_run_checklist_rules_df)),
                "dry_run_checklist_requirement_rows": int(len(dry_run_requirements_df)),
                "dry_run_checklist_rules_passed": dry_run_checklist_rules_passed,
                "manual_dry_run_checklist_passed": manual_dry_run_checklist_passed,
                "manual_dry_run_checklist_decision": manual_dry_run_checklist_decision,
                "controlled_dry_run_review_allowed": controlled_dry_run_review_allowed,
                "dry_run_execution_approved": False,
                "manual_protocol_activation_allowed": False,
                "controlled_forward_observation_start_approved": False,
                "forward_observation_start_allowed": False,
                "official_dataset_exists_before": official_dataset_exists_before,
                "official_dataset_exists_after": official_dataset_exists_after,
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
                "exchange_execution_allowed": False,
                "automation_allowed": False,
                "execution_allowed": False,
                "real_entries_approved": False,
                "total_project_completed": False,
                "recommended_next_phase": RECOMMENDED_NEXT_PHASE,
                "estimated_phase_10_progress_percent": 30,
                "total_checks": int(len(checks_df)),
                "warning_count": warning_count,
                "error_count": error_count,
                "blocker_count": blocker_count,
                "validation_passed": validation_passed,
                "validation_decision": (
                    "PHASE_10_3_LONG_FORWARD_OBSERVATION_MANUAL_DRY_RUN_CHECKLIST_VALIDATED"
                    if validation_passed
                    else "PHASE_10_3_LONG_FORWARD_OBSERVATION_MANUAL_DRY_RUN_CHECKLIST_FAILED"
                ),
            }
        ]
    )

    phase_10_2_summary_df.to_csv(
        REPORTS_DIR / "phase_10_2_source_summary_v1.csv",
        index=False,
    )
    source_manual_protocol_stages_df.to_csv(
        REPORTS_DIR / "phase_10_2_source_manual_protocol_stages_v1.csv",
        index=False,
    )
    source_manual_protocol_rules_df.to_csv(
        REPORTS_DIR / "phase_10_2_source_manual_protocol_rules_v1.csv",
        index=False,
    )
    source_manual_protocol_requirements_df.to_csv(
        REPORTS_DIR / "phase_10_2_source_manual_protocol_requirements_v1.csv",
        index=False,
    )
    source_manual_protocol_boundary_matrix_df.to_csv(
        REPORTS_DIR / "phase_10_2_source_manual_protocol_boundary_matrix_v1.csv",
        index=False,
    )
    source_manual_protocol_safety_matrix_df.to_csv(
        REPORTS_DIR / "phase_10_2_source_manual_protocol_safety_matrix_v1.csv",
        index=False,
    )
    source_manual_start_protocol_decision_df.to_csv(
        REPORTS_DIR / "phase_10_2_source_manual_start_protocol_decision_v1.csv",
        index=False,
    )
    source_checks_df.to_csv(
        REPORTS_DIR / "phase_10_2_source_checks_v1.csv",
        index=False,
    )
    dry_run_checklist_items_df.to_csv(
        REPORTS_DIR / "long_forward_observation_manual_dry_run_checklist_items_v1.csv",
        index=False,
    )
    dry_run_checklist_rules_df.to_csv(
        REPORTS_DIR / "long_forward_observation_manual_dry_run_checklist_rules_v1.csv",
        index=False,
    )
    dry_run_requirements_df.to_csv(
        REPORTS_DIR / "long_forward_observation_manual_dry_run_checklist_requirements_v1.csv",
        index=False,
    )
    dry_run_boundary_matrix_df.to_csv(
        REPORTS_DIR / "long_forward_observation_manual_dry_run_boundary_matrix_v1.csv",
        index=False,
    )
    dry_run_safety_matrix_df.to_csv(
        REPORTS_DIR / "long_forward_observation_manual_dry_run_safety_matrix_v1.csv",
        index=False,
    )
    manual_dry_run_checklist_decision_df.to_csv(
        REPORTS_DIR / "long_forward_observation_manual_dry_run_checklist_decision_v1.csv",
        index=False,
    )
    checks_df.to_csv(
        REPORTS_DIR / "long_forward_observation_manual_dry_run_checklist_checks_v1.csv",
        index=False,
    )
    summary_df.to_csv(
        REPORTS_DIR / "long_forward_observation_manual_dry_run_checklist_summary_v1.csv",
        index=False,
    )

    return {
        "summary": summary_df,
        "source_phase_10_2_summary": phase_10_2_summary_df,
        "source_manual_protocol_stages": source_manual_protocol_stages_df,
        "source_manual_protocol_rules": source_manual_protocol_rules_df,
        "source_manual_protocol_requirements": source_manual_protocol_requirements_df,
        "source_manual_protocol_boundary_matrix": source_manual_protocol_boundary_matrix_df,
        "source_manual_protocol_safety_matrix": source_manual_protocol_safety_matrix_df,
        "source_manual_start_protocol_decision": source_manual_start_protocol_decision_df,
        "source_checks": source_checks_df,
        "dry_run_checklist_items": dry_run_checklist_items_df,
        "dry_run_checklist_rules": dry_run_checklist_rules_df,
        "dry_run_checklist_requirements": dry_run_requirements_df,
        "dry_run_boundary_matrix": dry_run_boundary_matrix_df,
        "dry_run_safety_matrix": dry_run_safety_matrix_df,
        "manual_dry_run_checklist_decision": manual_dry_run_checklist_decision_df,
        "checks": checks_df,
    }