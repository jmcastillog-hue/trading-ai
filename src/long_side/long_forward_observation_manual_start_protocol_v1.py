from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from src.long_side.long_forward_observation_controlled_start_review_v1 import (
    READY_DECISION as CONTROLLED_START_READY_DECISION,
    validate_long_forward_observation_controlled_start_review,
)
from src.long_side.long_forward_observation_dataset_bootstrap_v1 import (
    OFFICIAL_DATASET_PATH,
    PRIMARY_RESEARCH_CANDIDATE,
)


REPORTS_DIR = Path("reports/phase_10_2_long_forward_observation_manual_start_protocol_v1")

PHASE_10_1_CONTROLLED_START_REVIEW_DOC_PATH = Path(
    "docs/PHASE_10_LONG_FORWARD_OBSERVATION_CONTROLLED_START_REVIEW.md"
)
PHASE_10_2_MANUAL_START_PROTOCOL_DOC_PATH = Path(
    "docs/PHASE_10_LONG_FORWARD_OBSERVATION_MANUAL_START_PROTOCOL.md"
)

MANUAL_START_PROTOCOL_STATUS = "LONG_FORWARD_OBSERVATION_MANUAL_START_PROTOCOL_ONLY"
READY_DECISION = "MANUAL_START_PROTOCOL_DEFINED_READY_FOR_DRY_RUN_CHECKLIST"
BLOCKED_DECISION = "MANUAL_START_PROTOCOL_BLOCKED"

RECOMMENDED_NEXT_PHASE = "PHASE_10_3_LONG_FORWARD_OBSERVATION_MANUAL_DRY_RUN_CHECKLIST_V1"

MANUAL_PROTOCOL_STAGES = [
    {
        "stage_id": "MANUAL_PROTOCOL_001",
        "stage_name": "confirm_clean_repository",
        "stage_category": "operator_preflight",
        "required": True,
        "manual_only": True,
        "execution_allowed": False,
        "details": "Operator must confirm clean git status before any later manual observation workflow.",
    },
    {
        "stage_id": "MANUAL_PROTOCOL_002",
        "stage_name": "confirm_correct_branch",
        "stage_category": "operator_preflight",
        "required": True,
        "manual_only": True,
        "execution_allowed": False,
        "details": "Operator must confirm the future branch is the approved controlled observation branch.",
    },
    {
        "stage_id": "MANUAL_PROTOCOL_003",
        "stage_name": "confirm_phase_9_10_closure_passed",
        "stage_category": "phase_dependency",
        "required": True,
        "manual_only": True,
        "execution_allowed": False,
        "details": "Phase 9.10 closure must be validated before future observation start review.",
    },
    {
        "stage_id": "MANUAL_PROTOCOL_004",
        "stage_name": "confirm_phase_10_1_review_passed",
        "stage_category": "phase_dependency",
        "required": True,
        "manual_only": True,
        "execution_allowed": False,
        "details": "Phase 10.1 controlled start review must be validated.",
    },
    {
        "stage_id": "MANUAL_PROTOCOL_005",
        "stage_name": "confirm_no_official_dataset_creation",
        "stage_category": "official_dataset_guard",
        "required": True,
        "manual_only": True,
        "execution_allowed": False,
        "details": "Official dataset must remain absent until a later explicit phase creates it.",
    },
    {
        "stage_id": "MANUAL_PROTOCOL_006",
        "stage_name": "confirm_start_not_approved",
        "stage_category": "start_boundary",
        "required": True,
        "manual_only": True,
        "execution_allowed": False,
        "details": "Phase 10.2 does not approve controlled forward observation start.",
    },
    {
        "stage_id": "MANUAL_PROTOCOL_007",
        "stage_name": "confirm_manual_review_required",
        "stage_category": "manual_review",
        "required": True,
        "manual_only": True,
        "execution_allowed": False,
        "details": "Every future observation candidate must require manual review.",
    },
    {
        "stage_id": "MANUAL_PROTOCOL_008",
        "stage_name": "confirm_primary_candidate_scope",
        "stage_category": "candidate_scope",
        "required": True,
        "manual_only": True,
        "execution_allowed": False,
        "details": f"Primary candidate must be {PRIMARY_RESEARCH_CANDIDATE}.",
    },
    {
        "stage_id": "MANUAL_PROTOCOL_009",
        "stage_name": "confirm_direction_long",
        "stage_category": "candidate_scope",
        "required": True,
        "manual_only": True,
        "execution_allowed": False,
        "details": "Direction must remain LONG.",
    },
    {
        "stage_id": "MANUAL_PROTOCOL_010",
        "stage_name": "confirm_long_price_structure",
        "stage_category": "price_structure",
        "required": True,
        "manual_only": True,
        "execution_allowed": False,
        "details": "Future price levels must satisfy stop_price < entry_price < target_price.",
    },
    {
        "stage_id": "MANUAL_PROTOCOL_011",
        "stage_name": "confirm_evidence_persistence_disabled",
        "stage_category": "safety",
        "required": True,
        "manual_only": True,
        "execution_allowed": False,
        "details": "Evidence persistence remains disabled.",
    },
    {
        "stage_id": "MANUAL_PROTOCOL_012",
        "stage_name": "confirm_signal_generation_disabled",
        "stage_category": "safety",
        "required": True,
        "manual_only": True,
        "execution_allowed": False,
        "details": "Signal generation remains disabled.",
    },
    {
        "stage_id": "MANUAL_PROTOCOL_013",
        "stage_name": "confirm_live_alerts_disabled",
        "stage_category": "safety",
        "required": True,
        "manual_only": True,
        "execution_allowed": False,
        "details": "Live alerts remain disabled.",
    },
    {
        "stage_id": "MANUAL_PROTOCOL_014",
        "stage_name": "confirm_paper_trading_disabled",
        "stage_category": "safety",
        "required": True,
        "manual_only": True,
        "execution_allowed": False,
        "details": "Paper trading remains disabled.",
    },
    {
        "stage_id": "MANUAL_PROTOCOL_015",
        "stage_name": "confirm_real_capital_disabled",
        "stage_category": "safety",
        "required": True,
        "manual_only": True,
        "execution_allowed": False,
        "details": "Real capital remains disabled.",
    },
    {
        "stage_id": "MANUAL_PROTOCOL_016",
        "stage_name": "confirm_exchange_execution_disabled",
        "stage_category": "safety",
        "required": True,
        "manual_only": True,
        "execution_allowed": False,
        "details": "Exchange execution remains disabled.",
    },
    {
        "stage_id": "MANUAL_PROTOCOL_017",
        "stage_name": "confirm_automation_disabled",
        "stage_category": "safety",
        "required": True,
        "manual_only": True,
        "execution_allowed": False,
        "details": "Automation remains disabled.",
    },
    {
        "stage_id": "MANUAL_PROTOCOL_018",
        "stage_name": "confirm_protocol_artifacts_only",
        "stage_category": "artifact_scope",
        "required": True,
        "manual_only": True,
        "execution_allowed": False,
        "details": "Phase 10.2 output is limited to protocol artifacts.",
    },
]

SAFETY_FLAGS = {
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


def build_manual_protocol_stage_table() -> pd.DataFrame:
    rows: list[dict[str, Any]] = []

    for stage in MANUAL_PROTOCOL_STAGES:
        rows.append(
            {
                "stage_id": stage["stage_id"],
                "stage_name": stage["stage_name"],
                "stage_category": stage["stage_category"],
                "required": stage["required"],
                "manual_only": stage["manual_only"],
                "execution_allowed": stage["execution_allowed"],
                "paper_trade_execution_allowed": False,
                "real_capital_allowed": False,
                "live_alerts_allowed": False,
                "automation_allowed": False,
                "official_dataset_write_allowed": False,
                "real_evidence_acceptance_allowed": False,
                "passed": (
                    stage["required"] is True
                    and stage["manual_only"] is True
                    and stage["execution_allowed"] is False
                ),
                "details": stage["details"],
            }
        )

    return pd.DataFrame(rows)


def build_manual_protocol_rules(
    manual_protocol_stages_df: pd.DataFrame,
) -> pd.DataFrame:
    stage_count = int(len(manual_protocol_stages_df))
    required_stage_count = (
        int(manual_protocol_stages_df["required"].astype(bool).sum())
        if stage_count
        else 0
    )
    all_stages_manual_only = (
        not manual_protocol_stages_df.empty
        and manual_protocol_stages_df["manual_only"].astype(bool).all()
    )
    all_execution_disabled = (
        not manual_protocol_stages_df.empty
        and manual_protocol_stages_df["execution_allowed"].astype(bool).eq(False).all()
    )
    all_official_dataset_writes_disabled = (
        not manual_protocol_stages_df.empty
        and manual_protocol_stages_df["official_dataset_write_allowed"]
        .astype(bool)
        .eq(False)
        .all()
    )

    rows = [
        {
            "rule_id": "MANUAL_PROTOCOL_RULE_001",
            "rule_name": "manual_protocol_stage_count_18",
            "passed": stage_count == 18,
            "required_value": "18",
            "actual_value": str(stage_count),
            "rule_group": "stage_structure",
        },
        {
            "rule_id": "MANUAL_PROTOCOL_RULE_002",
            "rule_name": "all_stages_required",
            "passed": required_stage_count == stage_count and stage_count > 0,
            "required_value": str(stage_count),
            "actual_value": str(required_stage_count),
            "rule_group": "stage_structure",
        },
        {
            "rule_id": "MANUAL_PROTOCOL_RULE_003",
            "rule_name": "all_stages_manual_only",
            "passed": all_stages_manual_only,
            "required_value": "True",
            "actual_value": str(all_stages_manual_only),
            "rule_group": "manual_control",
        },
        {
            "rule_id": "MANUAL_PROTOCOL_RULE_004",
            "rule_name": "all_stage_execution_disabled",
            "passed": all_execution_disabled,
            "required_value": "False",
            "actual_value": "False",
            "rule_group": "safety",
        },
        {
            "rule_id": "MANUAL_PROTOCOL_RULE_005",
            "rule_name": "all_official_dataset_writes_disabled",
            "passed": all_official_dataset_writes_disabled,
            "required_value": "False",
            "actual_value": "False",
            "rule_group": "official_dataset_guard",
        },
    ]

    return pd.DataFrame(rows)


def build_manual_protocol_requirements(
    phase_10_1_summary_df: pd.DataFrame,
    controlled_start_review_decision_df: pd.DataFrame,
    manual_protocol_rules_df: pd.DataFrame,
) -> pd.DataFrame:
    summary = (
        phase_10_1_summary_df.iloc[0].to_dict()
        if not phase_10_1_summary_df.empty
        else {}
    )

    decision = (
        controlled_start_review_decision_df.iloc[0].to_dict()
        if not controlled_start_review_decision_df.empty
        else {}
    )

    rules_passed = (
        not manual_protocol_rules_df.empty
        and manual_protocol_rules_df["passed"].astype(bool).all()
    )

    requirements: list[dict[str, Any]] = [
        {
            "requirement_id": "MANUAL_PROTOCOL_REQ_001",
            "requirement_name": "phase_10_1_validation_passed",
            "passed": safe_bool(summary.get("validation_passed", False)),
            "required_value": "True",
            "actual_value": str(summary.get("validation_passed", "")),
            "requirement_group": "dependency",
        },
        {
            "requirement_id": "MANUAL_PROTOCOL_REQ_002",
            "requirement_name": "controlled_start_review_passed",
            "passed": safe_bool(summary.get("controlled_start_review_passed", False)),
            "required_value": "True",
            "actual_value": str(summary.get("controlled_start_review_passed", "")),
            "requirement_group": "controlled_start_review",
        },
        {
            "requirement_id": "MANUAL_PROTOCOL_REQ_003",
            "requirement_name": "controlled_start_review_decision_expected",
            "passed": str(
                summary.get("controlled_start_review_decision", "")
            ).strip()
            == CONTROLLED_START_READY_DECISION,
            "required_value": CONTROLLED_START_READY_DECISION,
            "actual_value": str(summary.get("controlled_start_review_decision", "")),
            "requirement_group": "controlled_start_review",
        },
        {
            "requirement_id": "MANUAL_PROTOCOL_REQ_004",
            "requirement_name": "manual_observation_protocol_planning_allowed",
            "passed": safe_bool(
                summary.get("manual_observation_protocol_planning_allowed", False)
            ),
            "required_value": "True",
            "actual_value": str(
                summary.get("manual_observation_protocol_planning_allowed", "")
            ),
            "requirement_group": "planning_scope",
        },
        {
            "requirement_id": "MANUAL_PROTOCOL_REQ_005",
            "requirement_name": "controlled_start_decision_table_consistent",
            "passed": (
                not controlled_start_review_decision_df.empty
                and safe_bool(decision.get("controlled_start_review_passed", False))
                and str(decision.get("controlled_start_review_decision", "")).strip()
                == CONTROLLED_START_READY_DECISION
            ),
            "required_value": "True",
            "actual_value": str(decision.get("controlled_start_review_decision", "")),
            "requirement_group": "summary_consistency",
        },
        {
            "requirement_id": "MANUAL_PROTOCOL_REQ_006",
            "requirement_name": "manual_protocol_rules_passed",
            "passed": rules_passed,
            "required_value": "True",
            "actual_value": str(rules_passed),
            "requirement_group": "manual_protocol",
        },
        {
            "requirement_id": "MANUAL_PROTOCOL_REQ_007",
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
            "requirement_group": "safety",
        },
        {
            "requirement_id": "MANUAL_PROTOCOL_REQ_008",
            "requirement_name": "forward_observation_start_not_allowed",
            "passed": safe_bool(
                summary.get("forward_observation_start_allowed", True),
                default=True,
            )
            is False,
            "required_value": "False",
            "actual_value": str(summary.get("forward_observation_start_allowed", "")),
            "requirement_group": "safety",
        },
        {
            "requirement_id": "MANUAL_PROTOCOL_REQ_009",
            "requirement_name": "forward_observation_not_started",
            "passed": safe_bool(
                summary.get("forward_observation_started", True),
                default=True,
            )
            is False,
            "required_value": "False",
            "actual_value": str(summary.get("forward_observation_started", "")),
            "requirement_group": "safety",
        },
        {
            "requirement_id": "MANUAL_PROTOCOL_REQ_010",
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
            "requirement_id": "MANUAL_PROTOCOL_REQ_011",
            "requirement_name": "official_evidence_rows_written_zero",
            "passed": int(summary.get("official_evidence_rows_written", -1)) == 0,
            "required_value": "0",
            "actual_value": str(summary.get("official_evidence_rows_written", "")),
            "requirement_group": "official_dataset_guard",
        },
        {
            "requirement_id": "MANUAL_PROTOCOL_REQ_012",
            "requirement_name": "execution_disabled",
            "passed": safe_bool(summary.get("execution_allowed", True), default=True)
            is False,
            "required_value": "False",
            "actual_value": str(summary.get("execution_allowed", "")),
            "requirement_group": "safety",
        },
        {
            "requirement_id": "MANUAL_PROTOCOL_REQ_013",
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


def build_manual_protocol_boundary_matrix() -> pd.DataFrame:
    rows = [
        {
            "boundary_item": "manual_protocol_definition_allowed",
            "allowed": True,
            "boundary_type": "protocol_definition",
            "details": "Phase 10.2 may define the manual protocol.",
        },
        {
            "boundary_item": "dry_run_checklist_planning_allowed",
            "allowed": True,
            "boundary_type": "future_planning",
            "details": "Phase 10.2 may recommend a future dry-run checklist.",
        },
        {
            "boundary_item": "manual_protocol_activation_allowed",
            "allowed": False,
            "boundary_type": "activation",
            "details": "Phase 10.2 does not activate the manual protocol.",
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


def build_manual_protocol_safety_matrix() -> pd.DataFrame:
    rows: list[dict[str, Any]] = []

    for flag_name, flag_value in SAFETY_FLAGS.items():
        rows.append(
            {
                "safety_flag": flag_name,
                "required_value": False,
                "actual_value": flag_value,
                "passed": flag_value is False,
                "protocol_status": MANUAL_START_PROTOCOL_STATUS,
            }
        )

    rows.append(
        {
            "safety_flag": "official_evidence_rows_written",
            "required_value": 0,
            "actual_value": 0,
            "passed": True,
            "protocol_status": MANUAL_START_PROTOCOL_STATUS,
        }
    )

    return pd.DataFrame(rows)


def build_manual_start_protocol_decision_table(
    requirements_df: pd.DataFrame,
    boundary_matrix_df: pd.DataFrame,
    safety_matrix_df: pd.DataFrame,
    protocol_rules_df: pd.DataFrame,
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

    protocol_rules_passed = (
        not protocol_rules_df.empty and protocol_rules_df["passed"].astype(bool).all()
    )

    disallowed_operational_boundaries_passed = True

    if not boundary_matrix_df.empty:
        allowed_planning_items = {
            "manual_protocol_definition_allowed",
            "dry_run_checklist_planning_allowed",
        }

        disallowed_rows = boundary_matrix_df[
            ~boundary_matrix_df["boundary_item"].astype(str).isin(allowed_planning_items)
        ]
        disallowed_operational_boundaries_passed = (
            not disallowed_rows.empty
            and disallowed_rows["allowed"].astype(bool).eq(False).all()
        )

    manual_start_protocol_passed = (
        total_requirements > 0
        and failed_requirements == 0
        and safety_matrix_passed
        and protocol_rules_passed
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
                "manual_start_protocol_id": "PHASE_10_2_MANUAL_START_PROTOCOL_001",
                "manual_start_protocol_status": MANUAL_START_PROTOCOL_STATUS,
                "manual_start_protocol_passed": manual_start_protocol_passed,
                "manual_start_protocol_decision": (
                    READY_DECISION if manual_start_protocol_passed else BLOCKED_DECISION
                ),
                "total_requirements": total_requirements,
                "passed_requirements": passed_requirements,
                "failed_requirements": failed_requirements,
                "failed_requirement_names": failed_requirement_names,
                "manual_protocol_rules_passed": protocol_rules_passed,
                "safety_matrix_passed": safety_matrix_passed,
                "disallowed_operational_boundaries_passed": (
                    disallowed_operational_boundaries_passed
                ),
                "dry_run_checklist_planning_allowed": manual_start_protocol_passed,
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


def validate_long_forward_observation_manual_start_protocol() -> dict[str, pd.DataFrame]:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    checks: list[dict[str, Any]] = []

    phase_anchors = {
        "phase_10_1_controlled_start_review_doc_exists": (
            PHASE_10_1_CONTROLLED_START_REVIEW_DOC_PATH
        ),
        "phase_10_2_manual_start_protocol_doc_exists": (
            PHASE_10_2_MANUAL_START_PROTOCOL_DOC_PATH
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

    phase_10_1_result = validate_long_forward_observation_controlled_start_review()

    phase_10_1_summary_df = phase_10_1_result["summary"]
    source_controlled_start_requirements_df = phase_10_1_result[
        "controlled_start_review_requirements"
    ]
    source_controlled_start_boundary_matrix_df = phase_10_1_result[
        "controlled_start_review_boundary_matrix"
    ]
    source_controlled_start_safety_matrix_df = phase_10_1_result[
        "controlled_start_review_safety_matrix"
    ]
    source_controlled_start_decision_df = phase_10_1_result[
        "controlled_start_review_decision"
    ]
    source_checks_df = phase_10_1_result["checks"]

    phase_10_1_validation_passed = (
        not phase_10_1_summary_df.empty
        and bool(phase_10_1_summary_df.iloc[0].get("validation_passed", False))
    )

    controlled_start_review_defined = (
        not phase_10_1_summary_df.empty
        and bool(
            phase_10_1_summary_df.iloc[0].get(
                "long_forward_observation_controlled_start_review_defined",
                False,
            )
        )
    )

    manual_protocol_stages_df = build_manual_protocol_stage_table()
    manual_protocol_rules_df = build_manual_protocol_rules(
        manual_protocol_stages_df=manual_protocol_stages_df,
    )
    manual_protocol_boundary_matrix_df = build_manual_protocol_boundary_matrix()
    manual_protocol_safety_matrix_df = build_manual_protocol_safety_matrix()

    manual_protocol_requirements_df = build_manual_protocol_requirements(
        phase_10_1_summary_df=phase_10_1_summary_df,
        controlled_start_review_decision_df=source_controlled_start_decision_df,
        manual_protocol_rules_df=manual_protocol_rules_df,
    )

    manual_start_protocol_decision_df = build_manual_start_protocol_decision_table(
        requirements_df=manual_protocol_requirements_df,
        boundary_matrix_df=manual_protocol_boundary_matrix_df,
        safety_matrix_df=manual_protocol_safety_matrix_df,
        protocol_rules_df=manual_protocol_rules_df,
    )

    official_dataset_exists_after = OFFICIAL_DATASET_PATH.exists()

    decision = (
        manual_start_protocol_decision_df.iloc[0].to_dict()
        if not manual_start_protocol_decision_df.empty
        else {}
    )

    manual_start_protocol_passed = safe_bool(
        decision.get("manual_start_protocol_passed", False)
    )
    manual_start_protocol_decision = str(
        decision.get("manual_start_protocol_decision", "")
    )
    dry_run_checklist_planning_allowed = safe_bool(
        decision.get("dry_run_checklist_planning_allowed", False)
    )

    checks.append(
        build_check(
            check_group="phase_dependency",
            check_name="phase_10_1_validation_passed",
            passed=phase_10_1_validation_passed,
            severity="INFO" if phase_10_1_validation_passed else "ERROR",
            details=(
                str(phase_10_1_summary_df.iloc[0].get("validation_decision", ""))
                if not phase_10_1_summary_df.empty
                else "Missing Phase 10.1 summary."
            ),
        )
    )

    checks.append(
        build_check(
            check_group="phase_dependency",
            check_name="long_forward_observation_controlled_start_review_defined",
            passed=controlled_start_review_defined,
            severity="INFO" if controlled_start_review_defined else "ERROR",
            details=f"controlled_start_review_defined={controlled_start_review_defined}",
        )
    )

    manual_protocol_rules_passed = (
        not manual_protocol_rules_df.empty
        and manual_protocol_rules_df["passed"].astype(bool).all()
    )

    checks.append(
        build_check(
            check_group="manual_protocol",
            check_name="manual_protocol_rules_passed",
            passed=manual_protocol_rules_passed,
            severity="INFO" if manual_protocol_rules_passed else "ERROR",
            details=(
                "failed_rules="
                + ",".join(
                    manual_protocol_rules_df[
                        ~manual_protocol_rules_df["passed"].astype(bool)
                    ]["rule_name"].astype(str)
                )
                if not manual_protocol_rules_df.empty
                else "failed_rules=all"
            ),
        )
    )

    requirements_passed = (
        not manual_protocol_requirements_df.empty
        and manual_protocol_requirements_df["passed"].astype(bool).all()
    )

    checks.append(
        build_check(
            check_group="manual_protocol",
            check_name="manual_protocol_requirements_passed",
            passed=requirements_passed,
            severity="INFO" if requirements_passed else "ERROR",
            details=(
                "failed_requirements="
                + ",".join(
                    manual_protocol_requirements_df[
                        ~manual_protocol_requirements_df["passed"].astype(bool)
                    ]["requirement_name"].astype(str)
                )
                if not manual_protocol_requirements_df.empty
                else "failed_requirements=all"
            ),
        )
    )

    checks.append(
        build_check(
            check_group="manual_protocol",
            check_name="manual_start_protocol_passed",
            passed=manual_start_protocol_passed,
            severity="INFO" if manual_start_protocol_passed else "ERROR",
            details=f"manual_start_protocol_passed={manual_start_protocol_passed}",
        )
    )

    checks.append(
        build_check(
            check_group="manual_protocol",
            check_name="manual_start_protocol_decision_expected",
            passed=manual_start_protocol_decision == READY_DECISION,
            severity=(
                "INFO"
                if manual_start_protocol_decision == READY_DECISION
                else "ERROR"
            ),
            details="manual_start_protocol_decision=" + manual_start_protocol_decision,
        )
    )

    checks.append(
        build_check(
            check_group="planning_scope",
            check_name="dry_run_checklist_planning_allowed",
            passed=dry_run_checklist_planning_allowed,
            severity="WARNING" if dry_run_checklist_planning_allowed else "ERROR",
            details=(
                "This allows only future dry-run checklist planning, not observation start, "
                "alerts, paper trading, real capital, or execution."
            ),
        )
    )

    activation_allowed = safe_bool(
        decision.get("manual_protocol_activation_allowed", True),
        default=True,
    )

    checks.append(
        build_check(
            check_group="safety_controls",
            check_name="manual_protocol_activation_not_allowed",
            passed=activation_allowed is False,
            severity="INFO" if activation_allowed is False else "ERROR",
            details=f"manual_protocol_activation_allowed={activation_allowed}",
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
        not manual_protocol_safety_matrix_df.empty
        and manual_protocol_safety_matrix_df["passed"].astype(bool).all()
    )

    checks.append(
        build_check(
            check_group="safety_controls",
            check_name="manual_protocol_safety_matrix_passed",
            passed=safety_matrix_passed,
            severity="INFO" if safety_matrix_passed else "ERROR",
            details=(
                "failed_safety_flags="
                + ",".join(
                    manual_protocol_safety_matrix_df[
                        ~manual_protocol_safety_matrix_df["passed"].astype(bool)
                    ]["safety_flag"].astype(str)
                )
                if not manual_protocol_safety_matrix_df.empty
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
            check_name="manual_start_protocol_only",
            passed=True,
            severity="WARNING",
            details="Phase 10.2 defines the manual protocol only.",
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
            check_name="phase_10_3_recommended_next",
            passed=True,
            severity="INFO",
            details=(
                "Recommended next step: "
                "Phase 10.3 LONG Forward Observation Manual Dry-Run Checklist V1."
            ),
        )
    )

    checks_df = pd.DataFrame(checks)

    blocker_count = int(checks_df["blocker"].astype(bool).sum())
    error_count = int(checks_df["severity"].eq("ERROR").sum())
    warning_count = int(checks_df["severity"].eq("WARNING").sum())

    validation_passed = blocker_count == 0 and error_count == 0

    phase_10_1_summary = (
        phase_10_1_summary_df.iloc[0].to_dict()
        if not phase_10_1_summary_df.empty
        else {}
    )

    summary_df = pd.DataFrame(
        [
            {
                "phase": "10.2",
                "long_forward_observation_manual_start_protocol_defined": True,
                "phase_10_1_validation_passed": phase_10_1_validation_passed,
                "long_forward_observation_controlled_start_review_defined": (
                    controlled_start_review_defined
                ),
                "controlled_start_review_passed": safe_bool(
                    phase_10_1_summary.get("controlled_start_review_passed", False)
                ),
                "controlled_start_review_decision": str(
                    phase_10_1_summary.get("controlled_start_review_decision", "")
                ),
                "manual_observation_protocol_planning_allowed": safe_bool(
                    phase_10_1_summary.get(
                        "manual_observation_protocol_planning_allowed",
                        False,
                    )
                ),
                "manual_protocol_stage_count": int(len(manual_protocol_stages_df)),
                "manual_protocol_rule_rows": int(len(manual_protocol_rules_df)),
                "manual_protocol_requirement_rows": int(
                    len(manual_protocol_requirements_df)
                ),
                "manual_protocol_rules_passed": manual_protocol_rules_passed,
                "manual_start_protocol_passed": manual_start_protocol_passed,
                "manual_start_protocol_decision": manual_start_protocol_decision,
                "dry_run_checklist_planning_allowed": dry_run_checklist_planning_allowed,
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
                "estimated_phase_10_progress_percent": 20,
                "total_checks": int(len(checks_df)),
                "warning_count": warning_count,
                "error_count": error_count,
                "blocker_count": blocker_count,
                "validation_passed": validation_passed,
                "validation_decision": (
                    "PHASE_10_2_LONG_FORWARD_OBSERVATION_MANUAL_START_PROTOCOL_VALIDATED"
                    if validation_passed
                    else "PHASE_10_2_LONG_FORWARD_OBSERVATION_MANUAL_START_PROTOCOL_FAILED"
                ),
            }
        ]
    )

    phase_10_1_summary_df.to_csv(
        REPORTS_DIR / "phase_10_1_source_summary_v1.csv",
        index=False,
    )
    source_controlled_start_requirements_df.to_csv(
        REPORTS_DIR / "phase_10_1_source_controlled_start_requirements_v1.csv",
        index=False,
    )
    source_controlled_start_boundary_matrix_df.to_csv(
        REPORTS_DIR / "phase_10_1_source_controlled_start_boundary_matrix_v1.csv",
        index=False,
    )
    source_controlled_start_safety_matrix_df.to_csv(
        REPORTS_DIR / "phase_10_1_source_controlled_start_safety_matrix_v1.csv",
        index=False,
    )
    source_controlled_start_decision_df.to_csv(
        REPORTS_DIR / "phase_10_1_source_controlled_start_decision_v1.csv",
        index=False,
    )
    source_checks_df.to_csv(
        REPORTS_DIR / "phase_10_1_source_checks_v1.csv",
        index=False,
    )
    manual_protocol_stages_df.to_csv(
        REPORTS_DIR / "long_forward_observation_manual_protocol_stages_v1.csv",
        index=False,
    )
    manual_protocol_rules_df.to_csv(
        REPORTS_DIR / "long_forward_observation_manual_protocol_rules_v1.csv",
        index=False,
    )
    manual_protocol_requirements_df.to_csv(
        REPORTS_DIR / "long_forward_observation_manual_protocol_requirements_v1.csv",
        index=False,
    )
    manual_protocol_boundary_matrix_df.to_csv(
        REPORTS_DIR / "long_forward_observation_manual_protocol_boundary_matrix_v1.csv",
        index=False,
    )
    manual_protocol_safety_matrix_df.to_csv(
        REPORTS_DIR / "long_forward_observation_manual_protocol_safety_matrix_v1.csv",
        index=False,
    )
    manual_start_protocol_decision_df.to_csv(
        REPORTS_DIR / "long_forward_observation_manual_start_protocol_decision_v1.csv",
        index=False,
    )
    checks_df.to_csv(
        REPORTS_DIR / "long_forward_observation_manual_start_protocol_checks_v1.csv",
        index=False,
    )
    summary_df.to_csv(
        REPORTS_DIR / "long_forward_observation_manual_start_protocol_summary_v1.csv",
        index=False,
    )

    return {
        "summary": summary_df,
        "source_phase_10_1_summary": phase_10_1_summary_df,
        "source_controlled_start_requirements": source_controlled_start_requirements_df,
        "source_controlled_start_boundary_matrix": source_controlled_start_boundary_matrix_df,
        "source_controlled_start_safety_matrix": source_controlled_start_safety_matrix_df,
        "source_controlled_start_decision": source_controlled_start_decision_df,
        "source_checks": source_checks_df,
        "manual_protocol_stages": manual_protocol_stages_df,
        "manual_protocol_rules": manual_protocol_rules_df,
        "manual_protocol_requirements": manual_protocol_requirements_df,
        "manual_protocol_boundary_matrix": manual_protocol_boundary_matrix_df,
        "manual_protocol_safety_matrix": manual_protocol_safety_matrix_df,
        "manual_start_protocol_decision": manual_start_protocol_decision_df,
        "checks": checks_df,
    }