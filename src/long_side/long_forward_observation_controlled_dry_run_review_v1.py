from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from src.long_side.long_forward_observation_dataset_bootstrap_v1 import (
    OFFICIAL_DATASET_PATH,
)
from src.long_side.long_forward_observation_manual_dry_run_checklist_v1 import (
    READY_DECISION as MANUAL_DRY_RUN_CHECKLIST_READY_DECISION,
    validate_long_forward_observation_manual_dry_run_checklist,
)


REPORTS_DIR = Path("reports/phase_10_4_long_forward_observation_controlled_dry_run_review_v1")

PHASE_10_3_MANUAL_DRY_RUN_CHECKLIST_DOC_PATH = Path(
    "docs/PHASE_10_LONG_FORWARD_OBSERVATION_MANUAL_DRY_RUN_CHECKLIST.md"
)
PHASE_10_4_CONTROLLED_DRY_RUN_REVIEW_DOC_PATH = Path(
    "docs/PHASE_10_LONG_FORWARD_OBSERVATION_CONTROLLED_DRY_RUN_REVIEW.md"
)

CONTROLLED_DRY_RUN_REVIEW_STATUS = "LONG_FORWARD_OBSERVATION_CONTROLLED_DRY_RUN_REVIEW_ONLY"
READY_DECISION = "CONTROLLED_DRY_RUN_REVIEW_READY_FOR_REPORT_ONLY_DRY_RUN_DESIGN"
BLOCKED_DECISION = "CONTROLLED_DRY_RUN_REVIEW_BLOCKED"

RECOMMENDED_NEXT_PHASE = "PHASE_10_5_LONG_FORWARD_OBSERVATION_REPORT_ONLY_DRY_RUN_DESIGN_V1"

REVIEW_CONTROLS = [
    {
        "control_id": "CONTROLLED_DRY_RUN_REVIEW_001",
        "control_name": "phase_10_3_checklist_validated",
        "control_group": "dependency",
        "required": True,
        "review_only": True,
        "dry_run_execution_allowed": False,
        "details": "Phase 10.3 manual dry-run checklist must be validated.",
    },
    {
        "control_id": "CONTROLLED_DRY_RUN_REVIEW_002",
        "control_name": "dry_run_execution_not_approved",
        "control_group": "dry_run_boundary",
        "required": True,
        "review_only": True,
        "dry_run_execution_allowed": False,
        "details": "Phase 10.4 does not approve dry-run execution.",
    },
    {
        "control_id": "CONTROLLED_DRY_RUN_REVIEW_003",
        "control_name": "forward_observation_start_not_approved",
        "control_group": "start_boundary",
        "required": True,
        "review_only": True,
        "dry_run_execution_allowed": False,
        "details": "Forward observation start remains disabled.",
    },
    {
        "control_id": "CONTROLLED_DRY_RUN_REVIEW_004",
        "control_name": "official_dataset_write_disabled",
        "control_group": "official_dataset_guard",
        "required": True,
        "review_only": True,
        "dry_run_execution_allowed": False,
        "details": "Official dataset writes remain disabled.",
    },
    {
        "control_id": "CONTROLLED_DRY_RUN_REVIEW_005",
        "control_name": "real_evidence_acceptance_disabled",
        "control_group": "official_dataset_guard",
        "required": True,
        "review_only": True,
        "dry_run_execution_allowed": False,
        "details": "Real evidence acceptance remains disabled.",
    },
    {
        "control_id": "CONTROLLED_DRY_RUN_REVIEW_006",
        "control_name": "signal_generation_disabled",
        "control_group": "safety",
        "required": True,
        "review_only": True,
        "dry_run_execution_allowed": False,
        "details": "Signal generation remains disabled.",
    },
    {
        "control_id": "CONTROLLED_DRY_RUN_REVIEW_007",
        "control_name": "live_alerts_disabled",
        "control_group": "safety",
        "required": True,
        "review_only": True,
        "dry_run_execution_allowed": False,
        "details": "Live alerts remain disabled.",
    },
    {
        "control_id": "CONTROLLED_DRY_RUN_REVIEW_008",
        "control_name": "paper_trading_disabled",
        "control_group": "safety",
        "required": True,
        "review_only": True,
        "dry_run_execution_allowed": False,
        "details": "Paper trading remains disabled.",
    },
    {
        "control_id": "CONTROLLED_DRY_RUN_REVIEW_009",
        "control_name": "real_capital_disabled",
        "control_group": "safety",
        "required": True,
        "review_only": True,
        "dry_run_execution_allowed": False,
        "details": "Real capital remains disabled.",
    },
    {
        "control_id": "CONTROLLED_DRY_RUN_REVIEW_010",
        "control_name": "execution_and_automation_disabled",
        "control_group": "safety",
        "required": True,
        "review_only": True,
        "dry_run_execution_allowed": False,
        "details": "Execution and automation remain disabled.",
    },
]

SAFETY_FLAGS = {
    "dry_run_execution_approved": False,
    "report_only_dry_run_execution_allowed": False,
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


def build_controlled_dry_run_review_controls() -> pd.DataFrame:
    rows: list[dict[str, Any]] = []

    for control in REVIEW_CONTROLS:
        rows.append(
            {
                "control_id": control["control_id"],
                "control_name": control["control_name"],
                "control_group": control["control_group"],
                "required": control["required"],
                "review_only": control["review_only"],
                "dry_run_execution_allowed": control["dry_run_execution_allowed"],
                "forward_observation_start_allowed": False,
                "official_dataset_write_allowed": False,
                "real_evidence_acceptance_allowed": False,
                "live_alerts_allowed": False,
                "paper_trading_allowed": False,
                "real_capital_allowed": False,
                "exchange_execution_allowed": False,
                "automation_allowed": False,
                "passed": (
                    control["required"] is True
                    and control["review_only"] is True
                    and control["dry_run_execution_allowed"] is False
                ),
                "details": control["details"],
            }
        )

    return pd.DataFrame(rows)


def build_controlled_dry_run_review_rules(
    review_controls_df: pd.DataFrame,
) -> pd.DataFrame:
    control_count = int(len(review_controls_df))
    required_control_count = (
        int(review_controls_df["required"].astype(bool).sum())
        if control_count
        else 0
    )

    all_review_only = (
        not review_controls_df.empty
        and review_controls_df["review_only"].astype(bool).all()
    )

    all_dry_run_execution_disabled = (
        not review_controls_df.empty
        and review_controls_df["dry_run_execution_allowed"].astype(bool).eq(False).all()
    )

    all_forward_start_disabled = (
        not review_controls_df.empty
        and review_controls_df["forward_observation_start_allowed"]
        .astype(bool)
        .eq(False)
        .all()
    )

    all_official_dataset_writes_disabled = (
        not review_controls_df.empty
        and review_controls_df["official_dataset_write_allowed"]
        .astype(bool)
        .eq(False)
        .all()
    )

    rows = [
        {
            "rule_id": "CONTROLLED_DRY_RUN_REVIEW_RULE_001",
            "rule_name": "controlled_dry_run_review_control_count_10",
            "passed": control_count == 10,
            "required_value": "10",
            "actual_value": str(control_count),
            "rule_group": "review_structure",
        },
        {
            "rule_id": "CONTROLLED_DRY_RUN_REVIEW_RULE_002",
            "rule_name": "all_controls_required",
            "passed": required_control_count == control_count and control_count > 0,
            "required_value": str(control_count),
            "actual_value": str(required_control_count),
            "rule_group": "review_structure",
        },
        {
            "rule_id": "CONTROLLED_DRY_RUN_REVIEW_RULE_003",
            "rule_name": "all_controls_review_only",
            "passed": all_review_only,
            "required_value": "True",
            "actual_value": str(all_review_only),
            "rule_group": "review_scope",
        },
        {
            "rule_id": "CONTROLLED_DRY_RUN_REVIEW_RULE_004",
            "rule_name": "all_dry_run_execution_disabled",
            "passed": all_dry_run_execution_disabled,
            "required_value": "False",
            "actual_value": "False",
            "rule_group": "dry_run_boundary",
        },
        {
            "rule_id": "CONTROLLED_DRY_RUN_REVIEW_RULE_005",
            "rule_name": "all_forward_observation_start_disabled",
            "passed": all_forward_start_disabled,
            "required_value": "False",
            "actual_value": "False",
            "rule_group": "start_boundary",
        },
        {
            "rule_id": "CONTROLLED_DRY_RUN_REVIEW_RULE_006",
            "rule_name": "all_official_dataset_writes_disabled",
            "passed": all_official_dataset_writes_disabled,
            "required_value": "False",
            "actual_value": "False",
            "rule_group": "official_dataset_guard",
        },
    ]

    return pd.DataFrame(rows)


def build_controlled_dry_run_review_requirements(
    phase_10_3_summary_df: pd.DataFrame,
    manual_dry_run_checklist_decision_df: pd.DataFrame,
    review_rules_df: pd.DataFrame,
) -> pd.DataFrame:
    summary = (
        phase_10_3_summary_df.iloc[0].to_dict()
        if not phase_10_3_summary_df.empty
        else {}
    )

    decision = (
        manual_dry_run_checklist_decision_df.iloc[0].to_dict()
        if not manual_dry_run_checklist_decision_df.empty
        else {}
    )

    review_rules_passed = (
        not review_rules_df.empty and review_rules_df["passed"].astype(bool).all()
    )

    requirements: list[dict[str, Any]] = [
        {
            "requirement_id": "CONTROLLED_DRY_RUN_REVIEW_REQ_001",
            "requirement_name": "phase_10_3_validation_passed",
            "passed": safe_bool(summary.get("validation_passed", False)),
            "required_value": "True",
            "actual_value": str(summary.get("validation_passed", "")),
            "requirement_group": "dependency",
        },
        {
            "requirement_id": "CONTROLLED_DRY_RUN_REVIEW_REQ_002",
            "requirement_name": "manual_dry_run_checklist_passed",
            "passed": safe_bool(
                summary.get("manual_dry_run_checklist_passed", False)
            ),
            "required_value": "True",
            "actual_value": str(summary.get("manual_dry_run_checklist_passed", "")),
            "requirement_group": "manual_dry_run_checklist",
        },
        {
            "requirement_id": "CONTROLLED_DRY_RUN_REVIEW_REQ_003",
            "requirement_name": "manual_dry_run_checklist_decision_expected",
            "passed": str(
                summary.get("manual_dry_run_checklist_decision", "")
            ).strip()
            == MANUAL_DRY_RUN_CHECKLIST_READY_DECISION,
            "required_value": MANUAL_DRY_RUN_CHECKLIST_READY_DECISION,
            "actual_value": str(summary.get("manual_dry_run_checklist_decision", "")),
            "requirement_group": "manual_dry_run_checklist",
        },
        {
            "requirement_id": "CONTROLLED_DRY_RUN_REVIEW_REQ_004",
            "requirement_name": "controlled_dry_run_review_allowed",
            "passed": safe_bool(
                summary.get("controlled_dry_run_review_allowed", False)
            ),
            "required_value": "True",
            "actual_value": str(summary.get("controlled_dry_run_review_allowed", "")),
            "requirement_group": "review_scope",
        },
        {
            "requirement_id": "CONTROLLED_DRY_RUN_REVIEW_REQ_005",
            "requirement_name": "manual_dry_run_checklist_decision_table_consistent",
            "passed": (
                not manual_dry_run_checklist_decision_df.empty
                and safe_bool(
                    decision.get("manual_dry_run_checklist_passed", False)
                )
                and str(
                    decision.get("manual_dry_run_checklist_decision", "")
                ).strip()
                == MANUAL_DRY_RUN_CHECKLIST_READY_DECISION
            ),
            "required_value": "True",
            "actual_value": str(decision.get("manual_dry_run_checklist_decision", "")),
            "requirement_group": "summary_consistency",
        },
        {
            "requirement_id": "CONTROLLED_DRY_RUN_REVIEW_REQ_006",
            "requirement_name": "controlled_dry_run_review_rules_passed",
            "passed": review_rules_passed,
            "required_value": "True",
            "actual_value": str(review_rules_passed),
            "requirement_group": "controlled_dry_run_review",
        },
        {
            "requirement_id": "CONTROLLED_DRY_RUN_REVIEW_REQ_007",
            "requirement_name": "dry_run_execution_not_approved",
            "passed": safe_bool(
                summary.get("dry_run_execution_approved", True),
                default=True,
            )
            is False,
            "required_value": "False",
            "actual_value": str(summary.get("dry_run_execution_approved", "")),
            "requirement_group": "dry_run_boundary",
        },
        {
            "requirement_id": "CONTROLLED_DRY_RUN_REVIEW_REQ_008",
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
            "requirement_id": "CONTROLLED_DRY_RUN_REVIEW_REQ_009",
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
            "requirement_id": "CONTROLLED_DRY_RUN_REVIEW_REQ_010",
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
            "requirement_id": "CONTROLLED_DRY_RUN_REVIEW_REQ_011",
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
            "requirement_id": "CONTROLLED_DRY_RUN_REVIEW_REQ_012",
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
            "requirement_id": "CONTROLLED_DRY_RUN_REVIEW_REQ_013",
            "requirement_name": "official_evidence_rows_written_zero",
            "passed": int(summary.get("official_evidence_rows_written", -1)) == 0,
            "required_value": "0",
            "actual_value": str(summary.get("official_evidence_rows_written", "")),
            "requirement_group": "official_dataset_guard",
        },
        {
            "requirement_id": "CONTROLLED_DRY_RUN_REVIEW_REQ_014",
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
            "requirement_id": "CONTROLLED_DRY_RUN_REVIEW_REQ_015",
            "requirement_name": "execution_disabled",
            "passed": safe_bool(summary.get("execution_allowed", True), default=True)
            is False,
            "required_value": "False",
            "actual_value": str(summary.get("execution_allowed", "")),
            "requirement_group": "safety",
        },
        {
            "requirement_id": "CONTROLLED_DRY_RUN_REVIEW_REQ_016",
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


def build_controlled_dry_run_review_boundary_matrix() -> pd.DataFrame:
    rows = [
        {
            "boundary_item": "controlled_dry_run_review_definition_allowed",
            "allowed": True,
            "boundary_type": "review_definition",
            "details": "Phase 10.4 may define the controlled dry-run review.",
        },
        {
            "boundary_item": "report_only_dry_run_design_allowed",
            "allowed": True,
            "boundary_type": "future_design",
            "details": "Phase 10.4 may recommend future report-only dry-run design.",
        },
        {
            "boundary_item": "dry_run_execution_approved",
            "allowed": False,
            "boundary_type": "dry_run_execution",
            "details": "Phase 10.4 does not approve dry-run execution.",
        },
        {
            "boundary_item": "report_only_dry_run_execution_allowed",
            "allowed": False,
            "boundary_type": "dry_run_execution",
            "details": "Report-only dry-run execution remains disabled.",
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


def build_controlled_dry_run_review_safety_matrix() -> pd.DataFrame:
    rows: list[dict[str, Any]] = []

    for flag_name, flag_value in SAFETY_FLAGS.items():
        rows.append(
            {
                "safety_flag": flag_name,
                "required_value": False,
                "actual_value": flag_value,
                "passed": flag_value is False,
                "review_status": CONTROLLED_DRY_RUN_REVIEW_STATUS,
            }
        )

    rows.append(
        {
            "safety_flag": "official_evidence_rows_written",
            "required_value": 0,
            "actual_value": 0,
            "passed": True,
            "review_status": CONTROLLED_DRY_RUN_REVIEW_STATUS,
        }
    )

    return pd.DataFrame(rows)


def build_controlled_dry_run_review_decision_table(
    requirements_df: pd.DataFrame,
    boundary_matrix_df: pd.DataFrame,
    safety_matrix_df: pd.DataFrame,
    review_rules_df: pd.DataFrame,
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

    review_rules_passed = (
        not review_rules_df.empty and review_rules_df["passed"].astype(bool).all()
    )

    disallowed_operational_boundaries_passed = True

    if not boundary_matrix_df.empty:
        allowed_planning_items = {
            "controlled_dry_run_review_definition_allowed",
            "report_only_dry_run_design_allowed",
        }

        disallowed_rows = boundary_matrix_df[
            ~boundary_matrix_df["boundary_item"].astype(str).isin(allowed_planning_items)
        ]
        disallowed_operational_boundaries_passed = (
            not disallowed_rows.empty
            and disallowed_rows["allowed"].astype(bool).eq(False).all()
        )

    controlled_dry_run_review_passed = (
        total_requirements > 0
        and failed_requirements == 0
        and safety_matrix_passed
        and review_rules_passed
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
                "controlled_dry_run_review_id": "PHASE_10_4_CONTROLLED_DRY_RUN_REVIEW_001",
                "controlled_dry_run_review_status": CONTROLLED_DRY_RUN_REVIEW_STATUS,
                "controlled_dry_run_review_passed": controlled_dry_run_review_passed,
                "controlled_dry_run_review_decision": (
                    READY_DECISION if controlled_dry_run_review_passed else BLOCKED_DECISION
                ),
                "total_requirements": total_requirements,
                "passed_requirements": passed_requirements,
                "failed_requirements": failed_requirements,
                "failed_requirement_names": failed_requirement_names,
                "controlled_dry_run_review_rules_passed": review_rules_passed,
                "safety_matrix_passed": safety_matrix_passed,
                "disallowed_operational_boundaries_passed": (
                    disallowed_operational_boundaries_passed
                ),
                "report_only_dry_run_design_allowed": controlled_dry_run_review_passed,
                "dry_run_execution_approved": False,
                "report_only_dry_run_execution_allowed": False,
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


def validate_long_forward_observation_controlled_dry_run_review() -> dict[str, pd.DataFrame]:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    checks: list[dict[str, Any]] = []

    phase_anchors = {
        "phase_10_3_manual_dry_run_checklist_doc_exists": (
            PHASE_10_3_MANUAL_DRY_RUN_CHECKLIST_DOC_PATH
        ),
        "phase_10_4_controlled_dry_run_review_doc_exists": (
            PHASE_10_4_CONTROLLED_DRY_RUN_REVIEW_DOC_PATH
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

    phase_10_3_result = validate_long_forward_observation_manual_dry_run_checklist()

    phase_10_3_summary_df = phase_10_3_result["summary"]
    source_dry_run_checklist_items_df = phase_10_3_result["dry_run_checklist_items"]
    source_dry_run_checklist_rules_df = phase_10_3_result["dry_run_checklist_rules"]
    source_dry_run_checklist_requirements_df = phase_10_3_result[
        "dry_run_checklist_requirements"
    ]
    source_dry_run_boundary_matrix_df = phase_10_3_result["dry_run_boundary_matrix"]
    source_dry_run_safety_matrix_df = phase_10_3_result["dry_run_safety_matrix"]
    source_manual_dry_run_checklist_decision_df = phase_10_3_result[
        "manual_dry_run_checklist_decision"
    ]
    source_checks_df = phase_10_3_result["checks"]

    phase_10_3_validation_passed = (
        not phase_10_3_summary_df.empty
        and bool(phase_10_3_summary_df.iloc[0].get("validation_passed", False))
    )

    manual_dry_run_checklist_defined = (
        not phase_10_3_summary_df.empty
        and bool(
            phase_10_3_summary_df.iloc[0].get(
                "long_forward_observation_manual_dry_run_checklist_defined",
                False,
            )
        )
    )

    controlled_dry_run_review_controls_df = build_controlled_dry_run_review_controls()
    controlled_dry_run_review_rules_df = build_controlled_dry_run_review_rules(
        review_controls_df=controlled_dry_run_review_controls_df,
    )
    controlled_dry_run_review_boundary_matrix_df = (
        build_controlled_dry_run_review_boundary_matrix()
    )
    controlled_dry_run_review_safety_matrix_df = (
        build_controlled_dry_run_review_safety_matrix()
    )

    controlled_dry_run_review_requirements_df = (
        build_controlled_dry_run_review_requirements(
            phase_10_3_summary_df=phase_10_3_summary_df,
            manual_dry_run_checklist_decision_df=(
                source_manual_dry_run_checklist_decision_df
            ),
            review_rules_df=controlled_dry_run_review_rules_df,
        )
    )

    controlled_dry_run_review_decision_df = (
        build_controlled_dry_run_review_decision_table(
            requirements_df=controlled_dry_run_review_requirements_df,
            boundary_matrix_df=controlled_dry_run_review_boundary_matrix_df,
            safety_matrix_df=controlled_dry_run_review_safety_matrix_df,
            review_rules_df=controlled_dry_run_review_rules_df,
        )
    )

    official_dataset_exists_after = OFFICIAL_DATASET_PATH.exists()

    decision = (
        controlled_dry_run_review_decision_df.iloc[0].to_dict()
        if not controlled_dry_run_review_decision_df.empty
        else {}
    )

    controlled_dry_run_review_passed = safe_bool(
        decision.get("controlled_dry_run_review_passed", False)
    )
    controlled_dry_run_review_decision = str(
        decision.get("controlled_dry_run_review_decision", "")
    )
    report_only_dry_run_design_allowed = safe_bool(
        decision.get("report_only_dry_run_design_allowed", False)
    )

    checks.append(
        build_check(
            check_group="phase_dependency",
            check_name="phase_10_3_validation_passed",
            passed=phase_10_3_validation_passed,
            severity="INFO" if phase_10_3_validation_passed else "ERROR",
            details=(
                str(phase_10_3_summary_df.iloc[0].get("validation_decision", ""))
                if not phase_10_3_summary_df.empty
                else "Missing Phase 10.3 summary."
            ),
        )
    )

    checks.append(
        build_check(
            check_group="phase_dependency",
            check_name="long_forward_observation_manual_dry_run_checklist_defined",
            passed=manual_dry_run_checklist_defined,
            severity="INFO" if manual_dry_run_checklist_defined else "ERROR",
            details=f"manual_dry_run_checklist_defined={manual_dry_run_checklist_defined}",
        )
    )

    controlled_dry_run_review_rules_passed = (
        not controlled_dry_run_review_rules_df.empty
        and controlled_dry_run_review_rules_df["passed"].astype(bool).all()
    )

    checks.append(
        build_check(
            check_group="controlled_dry_run_review",
            check_name="controlled_dry_run_review_rules_passed",
            passed=controlled_dry_run_review_rules_passed,
            severity="INFO" if controlled_dry_run_review_rules_passed else "ERROR",
            details=(
                "failed_rules="
                + ",".join(
                    controlled_dry_run_review_rules_df[
                        ~controlled_dry_run_review_rules_df["passed"].astype(bool)
                    ]["rule_name"].astype(str)
                )
                if not controlled_dry_run_review_rules_df.empty
                else "failed_rules=all"
            ),
        )
    )

    requirements_passed = (
        not controlled_dry_run_review_requirements_df.empty
        and controlled_dry_run_review_requirements_df["passed"].astype(bool).all()
    )

    checks.append(
        build_check(
            check_group="controlled_dry_run_review",
            check_name="controlled_dry_run_review_requirements_passed",
            passed=requirements_passed,
            severity="INFO" if requirements_passed else "ERROR",
            details=(
                "failed_requirements="
                + ",".join(
                    controlled_dry_run_review_requirements_df[
                        ~controlled_dry_run_review_requirements_df["passed"].astype(bool)
                    ]["requirement_name"].astype(str)
                )
                if not controlled_dry_run_review_requirements_df.empty
                else "failed_requirements=all"
            ),
        )
    )

    checks.append(
        build_check(
            check_group="controlled_dry_run_review",
            check_name="controlled_dry_run_review_passed",
            passed=controlled_dry_run_review_passed,
            severity="INFO" if controlled_dry_run_review_passed else "ERROR",
            details=f"controlled_dry_run_review_passed={controlled_dry_run_review_passed}",
        )
    )

    checks.append(
        build_check(
            check_group="controlled_dry_run_review",
            check_name="controlled_dry_run_review_decision_expected",
            passed=controlled_dry_run_review_decision == READY_DECISION,
            severity=(
                "INFO"
                if controlled_dry_run_review_decision == READY_DECISION
                else "ERROR"
            ),
            details=(
                "controlled_dry_run_review_decision="
                + controlled_dry_run_review_decision
            ),
        )
    )

    checks.append(
        build_check(
            check_group="planning_scope",
            check_name="report_only_dry_run_design_allowed",
            passed=report_only_dry_run_design_allowed,
            severity="WARNING" if report_only_dry_run_design_allowed else "ERROR",
            details=(
                "This allows only future report-only dry-run design, not dry-run execution, "
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

    report_only_dry_run_execution_allowed = safe_bool(
        decision.get("report_only_dry_run_execution_allowed", True),
        default=True,
    )

    checks.append(
        build_check(
            check_group="safety_controls",
            check_name="report_only_dry_run_execution_not_allowed",
            passed=report_only_dry_run_execution_allowed is False,
            severity="INFO" if report_only_dry_run_execution_allowed is False else "ERROR",
            details=(
                "report_only_dry_run_execution_allowed="
                f"{report_only_dry_run_execution_allowed}"
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

    safety_matrix_passed = (
        not controlled_dry_run_review_safety_matrix_df.empty
        and controlled_dry_run_review_safety_matrix_df["passed"].astype(bool).all()
    )

    checks.append(
        build_check(
            check_group="safety_controls",
            check_name="controlled_dry_run_review_safety_matrix_passed",
            passed=safety_matrix_passed,
            severity="INFO" if safety_matrix_passed else "ERROR",
            details=(
                "failed_safety_flags="
                + ",".join(
                    controlled_dry_run_review_safety_matrix_df[
                        ~controlled_dry_run_review_safety_matrix_df["passed"].astype(bool)
                    ]["safety_flag"].astype(str)
                )
                if not controlled_dry_run_review_safety_matrix_df.empty
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
            check_name="controlled_dry_run_review_only",
            passed=True,
            severity="WARNING",
            details="Phase 10.4 defines controlled dry-run review only.",
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
            check_name="phase_10_5_recommended_next",
            passed=True,
            severity="INFO",
            details=(
                "Recommended next step: "
                "Phase 10.5 LONG Forward Observation Report-Only Dry-Run Design V1."
            ),
        )
    )

    checks_df = pd.DataFrame(checks)

    blocker_count = int(checks_df["blocker"].astype(bool).sum())
    error_count = int(checks_df["severity"].eq("ERROR").sum())
    warning_count = int(checks_df["severity"].eq("WARNING").sum())

    validation_passed = blocker_count == 0 and error_count == 0

    phase_10_3_summary = (
        phase_10_3_summary_df.iloc[0].to_dict()
        if not phase_10_3_summary_df.empty
        else {}
    )

    summary_df = pd.DataFrame(
        [
            {
                "phase": "10.4",
                "long_forward_observation_controlled_dry_run_review_defined": True,
                "phase_10_3_validation_passed": phase_10_3_validation_passed,
                "long_forward_observation_manual_dry_run_checklist_defined": (
                    manual_dry_run_checklist_defined
                ),
                "manual_dry_run_checklist_passed": safe_bool(
                    phase_10_3_summary.get("manual_dry_run_checklist_passed", False)
                ),
                "manual_dry_run_checklist_decision": str(
                    phase_10_3_summary.get("manual_dry_run_checklist_decision", "")
                ),
                "controlled_dry_run_review_allowed": safe_bool(
                    phase_10_3_summary.get("controlled_dry_run_review_allowed", False)
                ),
                "controlled_dry_run_review_control_rows": int(
                    len(controlled_dry_run_review_controls_df)
                ),
                "controlled_dry_run_review_rule_rows": int(
                    len(controlled_dry_run_review_rules_df)
                ),
                "controlled_dry_run_review_requirement_rows": int(
                    len(controlled_dry_run_review_requirements_df)
                ),
                "controlled_dry_run_review_rules_passed": (
                    controlled_dry_run_review_rules_passed
                ),
                "controlled_dry_run_review_passed": controlled_dry_run_review_passed,
                "controlled_dry_run_review_decision": controlled_dry_run_review_decision,
                "report_only_dry_run_design_allowed": report_only_dry_run_design_allowed,
                "dry_run_execution_approved": False,
                "report_only_dry_run_execution_allowed": False,
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
                "estimated_phase_10_progress_percent": 40,
                "total_checks": int(len(checks_df)),
                "warning_count": warning_count,
                "error_count": error_count,
                "blocker_count": blocker_count,
                "validation_passed": validation_passed,
                "validation_decision": (
                    "PHASE_10_4_LONG_FORWARD_OBSERVATION_CONTROLLED_DRY_RUN_REVIEW_VALIDATED"
                    if validation_passed
                    else "PHASE_10_4_LONG_FORWARD_OBSERVATION_CONTROLLED_DRY_RUN_REVIEW_FAILED"
                ),
            }
        ]
    )

    phase_10_3_summary_df.to_csv(
        REPORTS_DIR / "phase_10_3_source_summary_v1.csv",
        index=False,
    )
    source_dry_run_checklist_items_df.to_csv(
        REPORTS_DIR / "phase_10_3_source_dry_run_checklist_items_v1.csv",
        index=False,
    )
    source_dry_run_checklist_rules_df.to_csv(
        REPORTS_DIR / "phase_10_3_source_dry_run_checklist_rules_v1.csv",
        index=False,
    )
    source_dry_run_checklist_requirements_df.to_csv(
        REPORTS_DIR / "phase_10_3_source_dry_run_checklist_requirements_v1.csv",
        index=False,
    )
    source_dry_run_boundary_matrix_df.to_csv(
        REPORTS_DIR / "phase_10_3_source_dry_run_boundary_matrix_v1.csv",
        index=False,
    )
    source_dry_run_safety_matrix_df.to_csv(
        REPORTS_DIR / "phase_10_3_source_dry_run_safety_matrix_v1.csv",
        index=False,
    )
    source_manual_dry_run_checklist_decision_df.to_csv(
        REPORTS_DIR / "phase_10_3_source_manual_dry_run_checklist_decision_v1.csv",
        index=False,
    )
    source_checks_df.to_csv(
        REPORTS_DIR / "phase_10_3_source_checks_v1.csv",
        index=False,
    )
    controlled_dry_run_review_controls_df.to_csv(
        REPORTS_DIR / "long_forward_observation_controlled_dry_run_review_controls_v1.csv",
        index=False,
    )
    controlled_dry_run_review_rules_df.to_csv(
        REPORTS_DIR / "long_forward_observation_controlled_dry_run_review_rules_v1.csv",
        index=False,
    )
    controlled_dry_run_review_requirements_df.to_csv(
        REPORTS_DIR / "long_forward_observation_controlled_dry_run_review_requirements_v1.csv",
        index=False,
    )
    controlled_dry_run_review_boundary_matrix_df.to_csv(
        REPORTS_DIR / "long_forward_observation_controlled_dry_run_review_boundary_matrix_v1.csv",
        index=False,
    )
    controlled_dry_run_review_safety_matrix_df.to_csv(
        REPORTS_DIR / "long_forward_observation_controlled_dry_run_review_safety_matrix_v1.csv",
        index=False,
    )
    controlled_dry_run_review_decision_df.to_csv(
        REPORTS_DIR / "long_forward_observation_controlled_dry_run_review_decision_v1.csv",
        index=False,
    )
    checks_df.to_csv(
        REPORTS_DIR / "long_forward_observation_controlled_dry_run_review_checks_v1.csv",
        index=False,
    )
    summary_df.to_csv(
        REPORTS_DIR / "long_forward_observation_controlled_dry_run_review_summary_v1.csv",
        index=False,
    )

    return {
        "summary": summary_df,
        "source_phase_10_3_summary": phase_10_3_summary_df,
        "source_dry_run_checklist_items": source_dry_run_checklist_items_df,
        "source_dry_run_checklist_rules": source_dry_run_checklist_rules_df,
        "source_dry_run_checklist_requirements": source_dry_run_checklist_requirements_df,
        "source_dry_run_boundary_matrix": source_dry_run_boundary_matrix_df,
        "source_dry_run_safety_matrix": source_dry_run_safety_matrix_df,
        "source_manual_dry_run_checklist_decision": (
            source_manual_dry_run_checklist_decision_df
        ),
        "source_checks": source_checks_df,
        "controlled_dry_run_review_controls": controlled_dry_run_review_controls_df,
        "controlled_dry_run_review_rules": controlled_dry_run_review_rules_df,
        "controlled_dry_run_review_requirements": (
            controlled_dry_run_review_requirements_df
        ),
        "controlled_dry_run_review_boundary_matrix": (
            controlled_dry_run_review_boundary_matrix_df
        ),
        "controlled_dry_run_review_safety_matrix": (
            controlled_dry_run_review_safety_matrix_df
        ),
        "controlled_dry_run_review_decision": controlled_dry_run_review_decision_df,
        "checks": checks_df,
    }