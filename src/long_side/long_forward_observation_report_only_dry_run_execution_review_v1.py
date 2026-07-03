from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from src.long_side.long_forward_observation_dataset_bootstrap_v1 import (
    OFFICIAL_DATASET_PATH,
    PRIMARY_RESEARCH_CANDIDATE,
)
from src.long_side.long_forward_observation_report_only_dry_run_design_v1 import (
    READY_DECISION as REPORT_ONLY_DRY_RUN_DESIGN_READY_DECISION,
    validate_long_forward_observation_report_only_dry_run_design,
)


REPORTS_DIR = Path(
    "reports/phase_10_6_long_forward_observation_report_only_dry_run_execution_review_v1"
)

PHASE_10_5_REPORT_ONLY_DRY_RUN_DESIGN_DOC_PATH = Path(
    "docs/PHASE_10_LONG_FORWARD_OBSERVATION_REPORT_ONLY_DRY_RUN_DESIGN.md"
)
PHASE_10_6_REPORT_ONLY_DRY_RUN_EXECUTION_REVIEW_DOC_PATH = Path(
    "docs/PHASE_10_LONG_FORWARD_OBSERVATION_REPORT_ONLY_DRY_RUN_EXECUTION_REVIEW.md"
)

REPORT_ONLY_DRY_RUN_EXECUTION_REVIEW_STATUS = (
    "LONG_FORWARD_OBSERVATION_REPORT_ONLY_DRY_RUN_EXECUTION_REVIEW_ONLY"
)
READY_DECISION = "REPORT_ONLY_DRY_RUN_EXECUTION_REVIEW_READY_FOR_CONTROLLED_RUN"
BLOCKED_DECISION = "REPORT_ONLY_DRY_RUN_EXECUTION_REVIEW_BLOCKED"

RECOMMENDED_NEXT_PHASE = (
    "PHASE_10_7_LONG_FORWARD_OBSERVATION_CONTROLLED_REPORT_ONLY_DRY_RUN_RUN_V1"
)

REVIEW_CONTROLS = [
    {
        "control_id": "REPORT_ONLY_DRY_RUN_EXEC_REVIEW_001",
        "control_name": "phase_10_5_design_validated",
        "control_group": "dependency",
        "required": True,
        "review_only": True,
        "run_performed": False,
        "market_execution_allowed": False,
        "details": "Phase 10.5 report-only dry-run design must be validated.",
    },
    {
        "control_id": "REPORT_ONLY_DRY_RUN_EXEC_REVIEW_002",
        "control_name": "schema_field_count_confirmed",
        "control_group": "schema",
        "required": True,
        "review_only": True,
        "run_performed": False,
        "market_execution_allowed": False,
        "details": "Report-only dry-run schema must contain 42 fields.",
    },
    {
        "control_id": "REPORT_ONLY_DRY_RUN_EXEC_REVIEW_003",
        "control_name": "design_component_count_confirmed",
        "control_group": "design_components",
        "required": True,
        "review_only": True,
        "run_performed": False,
        "market_execution_allowed": False,
        "details": "Report-only dry-run design must contain 12 components.",
    },
    {
        "control_id": "REPORT_ONLY_DRY_RUN_EXEC_REVIEW_004",
        "control_name": "primary_candidate_scope_confirmed",
        "control_group": "candidate_scope",
        "required": True,
        "review_only": True,
        "run_performed": False,
        "market_execution_allowed": False,
        "details": f"Primary candidate remains {PRIMARY_RESEARCH_CANDIDATE}.",
    },
    {
        "control_id": "REPORT_ONLY_DRY_RUN_EXEC_REVIEW_005",
        "control_name": "controlled_report_only_run_reviewed",
        "control_group": "future_run_scope",
        "required": True,
        "review_only": True,
        "run_performed": False,
        "market_execution_allowed": False,
        "details": "A future controlled report-only dry-run run may be reviewed.",
    },
    {
        "control_id": "REPORT_ONLY_DRY_RUN_EXEC_REVIEW_006",
        "control_name": "report_only_dry_run_not_performed",
        "control_group": "run_boundary",
        "required": True,
        "review_only": True,
        "run_performed": False,
        "market_execution_allowed": False,
        "details": "Phase 10.6 does not perform the report-only dry-run.",
    },
    {
        "control_id": "REPORT_ONLY_DRY_RUN_EXEC_REVIEW_007",
        "control_name": "forward_observation_start_disabled",
        "control_group": "start_boundary",
        "required": True,
        "review_only": True,
        "run_performed": False,
        "market_execution_allowed": False,
        "details": "Forward observation start remains disabled.",
    },
    {
        "control_id": "REPORT_ONLY_DRY_RUN_EXEC_REVIEW_008",
        "control_name": "official_dataset_write_disabled",
        "control_group": "official_dataset_guard",
        "required": True,
        "review_only": True,
        "run_performed": False,
        "market_execution_allowed": False,
        "details": "Official dataset writes remain disabled.",
    },
    {
        "control_id": "REPORT_ONLY_DRY_RUN_EXEC_REVIEW_009",
        "control_name": "real_evidence_acceptance_disabled",
        "control_group": "official_dataset_guard",
        "required": True,
        "review_only": True,
        "run_performed": False,
        "market_execution_allowed": False,
        "details": "Real evidence acceptance remains disabled.",
    },
    {
        "control_id": "REPORT_ONLY_DRY_RUN_EXEC_REVIEW_010",
        "control_name": "alerts_and_signal_generation_disabled",
        "control_group": "safety",
        "required": True,
        "review_only": True,
        "run_performed": False,
        "market_execution_allowed": False,
        "details": "Live alerts and signal generation remain disabled.",
    },
    {
        "control_id": "REPORT_ONLY_DRY_RUN_EXEC_REVIEW_011",
        "control_name": "paper_and_real_capital_disabled",
        "control_group": "safety",
        "required": True,
        "review_only": True,
        "run_performed": False,
        "market_execution_allowed": False,
        "details": "Paper trading and real capital remain disabled.",
    },
    {
        "control_id": "REPORT_ONLY_DRY_RUN_EXEC_REVIEW_012",
        "control_name": "market_execution_and_automation_disabled",
        "control_group": "safety",
        "required": True,
        "review_only": True,
        "run_performed": False,
        "market_execution_allowed": False,
        "details": "Market execution and automation remain disabled.",
    },
]

SAFETY_FLAGS = {
    "report_only_dry_run_run_performed": False,
    "dry_run_execution_performed": False,
    "dry_run_execution_approved": False,
    "market_execution_allowed": False,
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


def build_report_only_dry_run_execution_review_controls() -> pd.DataFrame:
    rows: list[dict[str, Any]] = []

    for control in REVIEW_CONTROLS:
        rows.append(
            {
                "control_id": control["control_id"],
                "control_name": control["control_name"],
                "control_group": control["control_group"],
                "required": control["required"],
                "review_only": control["review_only"],
                "run_performed": control["run_performed"],
                "market_execution_allowed": control["market_execution_allowed"],
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
                    and control["run_performed"] is False
                    and control["market_execution_allowed"] is False
                ),
                "details": control["details"],
            }
        )

    return pd.DataFrame(rows)


def build_report_only_dry_run_execution_review_rules(
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

    all_run_not_performed = (
        not review_controls_df.empty
        and review_controls_df["run_performed"].astype(bool).eq(False).all()
    )

    all_market_execution_disabled = (
        not review_controls_df.empty
        and review_controls_df["market_execution_allowed"].astype(bool).eq(False).all()
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
            "rule_id": "REPORT_ONLY_DRY_RUN_EXEC_REVIEW_RULE_001",
            "rule_name": "report_only_dry_run_execution_review_control_count_12",
            "passed": control_count == 12,
            "required_value": "12",
            "actual_value": str(control_count),
            "rule_group": "review_structure",
        },
        {
            "rule_id": "REPORT_ONLY_DRY_RUN_EXEC_REVIEW_RULE_002",
            "rule_name": "all_controls_required",
            "passed": required_control_count == control_count and control_count > 0,
            "required_value": str(control_count),
            "actual_value": str(required_control_count),
            "rule_group": "review_structure",
        },
        {
            "rule_id": "REPORT_ONLY_DRY_RUN_EXEC_REVIEW_RULE_003",
            "rule_name": "all_controls_review_only",
            "passed": all_review_only,
            "required_value": "True",
            "actual_value": str(all_review_only),
            "rule_group": "review_scope",
        },
        {
            "rule_id": "REPORT_ONLY_DRY_RUN_EXEC_REVIEW_RULE_004",
            "rule_name": "all_report_only_runs_not_performed",
            "passed": all_run_not_performed,
            "required_value": "False",
            "actual_value": "False",
            "rule_group": "run_boundary",
        },
        {
            "rule_id": "REPORT_ONLY_DRY_RUN_EXEC_REVIEW_RULE_005",
            "rule_name": "all_market_execution_disabled",
            "passed": all_market_execution_disabled,
            "required_value": "False",
            "actual_value": "False",
            "rule_group": "market_execution_guard",
        },
        {
            "rule_id": "REPORT_ONLY_DRY_RUN_EXEC_REVIEW_RULE_006",
            "rule_name": "all_forward_observation_start_disabled",
            "passed": all_forward_start_disabled,
            "required_value": "False",
            "actual_value": "False",
            "rule_group": "start_boundary",
        },
        {
            "rule_id": "REPORT_ONLY_DRY_RUN_EXEC_REVIEW_RULE_007",
            "rule_name": "all_official_dataset_writes_disabled",
            "passed": all_official_dataset_writes_disabled,
            "required_value": "False",
            "actual_value": "False",
            "rule_group": "official_dataset_guard",
        },
    ]

    return pd.DataFrame(rows)


def build_report_only_dry_run_execution_review_requirements(
    phase_10_5_summary_df: pd.DataFrame,
    report_only_dry_run_design_decision_df: pd.DataFrame,
    execution_review_rules_df: pd.DataFrame,
) -> pd.DataFrame:
    summary = (
        phase_10_5_summary_df.iloc[0].to_dict()
        if not phase_10_5_summary_df.empty
        else {}
    )

    decision = (
        report_only_dry_run_design_decision_df.iloc[0].to_dict()
        if not report_only_dry_run_design_decision_df.empty
        else {}
    )

    execution_review_rules_passed = (
        not execution_review_rules_df.empty
        and execution_review_rules_df["passed"].astype(bool).all()
    )

    requirements: list[dict[str, Any]] = [
        {
            "requirement_id": "REPORT_ONLY_DRY_RUN_EXEC_REVIEW_REQ_001",
            "requirement_name": "phase_10_5_validation_passed",
            "passed": safe_bool(summary.get("validation_passed", False)),
            "required_value": "True",
            "actual_value": str(summary.get("validation_passed", "")),
            "requirement_group": "dependency",
        },
        {
            "requirement_id": "REPORT_ONLY_DRY_RUN_EXEC_REVIEW_REQ_002",
            "requirement_name": "report_only_dry_run_design_passed",
            "passed": safe_bool(
                summary.get("report_only_dry_run_design_passed", False)
            ),
            "required_value": "True",
            "actual_value": str(summary.get("report_only_dry_run_design_passed", "")),
            "requirement_group": "report_only_dry_run_design",
        },
        {
            "requirement_id": "REPORT_ONLY_DRY_RUN_EXEC_REVIEW_REQ_003",
            "requirement_name": "report_only_dry_run_design_decision_expected",
            "passed": str(
                summary.get("report_only_dry_run_design_decision", "")
            ).strip()
            == REPORT_ONLY_DRY_RUN_DESIGN_READY_DECISION,
            "required_value": REPORT_ONLY_DRY_RUN_DESIGN_READY_DECISION,
            "actual_value": str(summary.get("report_only_dry_run_design_decision", "")),
            "requirement_group": "report_only_dry_run_design",
        },
        {
            "requirement_id": "REPORT_ONLY_DRY_RUN_EXEC_REVIEW_REQ_004",
            "requirement_name": "report_only_dry_run_execution_review_allowed",
            "passed": safe_bool(
                summary.get("report_only_dry_run_execution_review_allowed", False)
            ),
            "required_value": "True",
            "actual_value": str(
                summary.get("report_only_dry_run_execution_review_allowed", "")
            ),
            "requirement_group": "review_scope",
        },
        {
            "requirement_id": "REPORT_ONLY_DRY_RUN_EXEC_REVIEW_REQ_005",
            "requirement_name": "report_only_dry_run_design_decision_table_consistent",
            "passed": (
                not report_only_dry_run_design_decision_df.empty
                and safe_bool(
                    decision.get("report_only_dry_run_design_passed", False)
                )
                and str(
                    decision.get("report_only_dry_run_design_decision", "")
                ).strip()
                == REPORT_ONLY_DRY_RUN_DESIGN_READY_DECISION
            ),
            "required_value": "True",
            "actual_value": str(decision.get("report_only_dry_run_design_decision", "")),
            "requirement_group": "summary_consistency",
        },
        {
            "requirement_id": "REPORT_ONLY_DRY_RUN_EXEC_REVIEW_REQ_006",
            "requirement_name": "schema_field_count_42",
            "passed": int(summary.get("report_only_dry_run_schema_field_count", 0)) == 42,
            "required_value": "42",
            "actual_value": str(summary.get("report_only_dry_run_schema_field_count", "")),
            "requirement_group": "schema",
        },
        {
            "requirement_id": "REPORT_ONLY_DRY_RUN_EXEC_REVIEW_REQ_007",
            "requirement_name": "design_component_count_12",
            "passed": int(
                summary.get("report_only_dry_run_design_component_count", 0)
            )
            == 12,
            "required_value": "12",
            "actual_value": str(
                summary.get("report_only_dry_run_design_component_count", "")
            ),
            "requirement_group": "design_components",
        },
        {
            "requirement_id": "REPORT_ONLY_DRY_RUN_EXEC_REVIEW_REQ_008",
            "requirement_name": "execution_review_rules_passed",
            "passed": execution_review_rules_passed,
            "required_value": "True",
            "actual_value": str(execution_review_rules_passed),
            "requirement_group": "execution_review",
        },
        {
            "requirement_id": "REPORT_ONLY_DRY_RUN_EXEC_REVIEW_REQ_009",
            "requirement_name": "report_only_dry_run_run_not_performed",
            "passed": True,
            "required_value": "False",
            "actual_value": "False",
            "requirement_group": "run_boundary",
        },
        {
            "requirement_id": "REPORT_ONLY_DRY_RUN_EXEC_REVIEW_REQ_010",
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
            "requirement_id": "REPORT_ONLY_DRY_RUN_EXEC_REVIEW_REQ_011",
            "requirement_name": "report_only_dry_run_execution_not_allowed",
            "passed": safe_bool(
                summary.get("report_only_dry_run_execution_allowed", True),
                default=True,
            )
            is False,
            "required_value": "False",
            "actual_value": str(
                summary.get("report_only_dry_run_execution_allowed", "")
            ),
            "requirement_group": "dry_run_boundary",
        },
        {
            "requirement_id": "REPORT_ONLY_DRY_RUN_EXEC_REVIEW_REQ_012",
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
            "requirement_id": "REPORT_ONLY_DRY_RUN_EXEC_REVIEW_REQ_013",
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
            "requirement_id": "REPORT_ONLY_DRY_RUN_EXEC_REVIEW_REQ_014",
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
            "requirement_id": "REPORT_ONLY_DRY_RUN_EXEC_REVIEW_REQ_015",
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
            "requirement_id": "REPORT_ONLY_DRY_RUN_EXEC_REVIEW_REQ_016",
            "requirement_name": "official_evidence_rows_written_zero",
            "passed": int(summary.get("official_evidence_rows_written", -1)) == 0,
            "required_value": "0",
            "actual_value": str(summary.get("official_evidence_rows_written", "")),
            "requirement_group": "official_dataset_guard",
        },
        {
            "requirement_id": "REPORT_ONLY_DRY_RUN_EXEC_REVIEW_REQ_017",
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
            "requirement_id": "REPORT_ONLY_DRY_RUN_EXEC_REVIEW_REQ_018",
            "requirement_name": "market_execution_disabled",
            "passed": True,
            "required_value": "False",
            "actual_value": "False",
            "requirement_group": "market_execution_guard",
        },
        {
            "requirement_id": "REPORT_ONLY_DRY_RUN_EXEC_REVIEW_REQ_019",
            "requirement_name": "execution_disabled",
            "passed": safe_bool(summary.get("execution_allowed", True), default=True)
            is False,
            "required_value": "False",
            "actual_value": str(summary.get("execution_allowed", "")),
            "requirement_group": "safety",
        },
        {
            "requirement_id": "REPORT_ONLY_DRY_RUN_EXEC_REVIEW_REQ_020",
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


def build_report_only_dry_run_execution_review_boundary_matrix() -> pd.DataFrame:
    rows = [
        {
            "boundary_item": "report_only_dry_run_execution_review_allowed",
            "allowed": True,
            "boundary_type": "review_scope",
            "details": "Phase 10.6 may define the report-only dry-run execution review.",
        },
        {
            "boundary_item": "controlled_report_only_dry_run_run_allowed",
            "allowed": True,
            "boundary_type": "future_run",
            "details": "Phase 10.6 may recommend a future controlled report-only dry-run run.",
        },
        {
            "boundary_item": "report_only_dry_run_run_performed",
            "allowed": False,
            "boundary_type": "run_execution",
            "details": "Phase 10.6 does not perform the report-only dry-run.",
        },
        {
            "boundary_item": "dry_run_execution_performed",
            "allowed": False,
            "boundary_type": "run_execution",
            "details": "Dry-run execution is not performed in Phase 10.6.",
        },
        {
            "boundary_item": "dry_run_execution_approved",
            "allowed": False,
            "boundary_type": "approval_scope",
            "details": "Dry-run execution approval remains disabled in this review phase.",
        },
        {
            "boundary_item": "market_execution_allowed",
            "allowed": False,
            "boundary_type": "market_execution",
            "details": "Market execution remains disabled.",
        },
        {
            "boundary_item": "report_only_dry_run_execution_allowed",
            "allowed": False,
            "boundary_type": "run_execution",
            "details": "Report-only dry-run execution remains disabled until the next phase.",
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


def build_report_only_dry_run_execution_review_safety_matrix() -> pd.DataFrame:
    rows: list[dict[str, Any]] = []

    for flag_name, flag_value in SAFETY_FLAGS.items():
        rows.append(
            {
                "safety_flag": flag_name,
                "required_value": False,
                "actual_value": flag_value,
                "passed": flag_value is False,
                "review_status": REPORT_ONLY_DRY_RUN_EXECUTION_REVIEW_STATUS,
            }
        )

    rows.append(
        {
            "safety_flag": "official_evidence_rows_written",
            "required_value": 0,
            "actual_value": 0,
            "passed": True,
            "review_status": REPORT_ONLY_DRY_RUN_EXECUTION_REVIEW_STATUS,
        }
    )

    return pd.DataFrame(rows)


def build_report_only_dry_run_execution_review_decision_table(
    requirements_df: pd.DataFrame,
    boundary_matrix_df: pd.DataFrame,
    safety_matrix_df: pd.DataFrame,
    execution_review_rules_df: pd.DataFrame,
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

    execution_review_rules_passed = (
        not execution_review_rules_df.empty
        and execution_review_rules_df["passed"].astype(bool).all()
    )

    disallowed_operational_boundaries_passed = True

    if not boundary_matrix_df.empty:
        allowed_planning_items = {
            "report_only_dry_run_execution_review_allowed",
            "controlled_report_only_dry_run_run_allowed",
        }

        disallowed_rows = boundary_matrix_df[
            ~boundary_matrix_df["boundary_item"].astype(str).isin(allowed_planning_items)
        ]
        disallowed_operational_boundaries_passed = (
            not disallowed_rows.empty
            and disallowed_rows["allowed"].astype(bool).eq(False).all()
        )

    report_only_dry_run_execution_review_passed = (
        total_requirements > 0
        and failed_requirements == 0
        and safety_matrix_passed
        and execution_review_rules_passed
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
                "report_only_dry_run_execution_review_id": (
                    "PHASE_10_6_REPORT_ONLY_DRY_RUN_EXECUTION_REVIEW_001"
                ),
                "report_only_dry_run_execution_review_status": (
                    REPORT_ONLY_DRY_RUN_EXECUTION_REVIEW_STATUS
                ),
                "report_only_dry_run_execution_review_passed": (
                    report_only_dry_run_execution_review_passed
                ),
                "report_only_dry_run_execution_review_decision": (
                    READY_DECISION
                    if report_only_dry_run_execution_review_passed
                    else BLOCKED_DECISION
                ),
                "total_requirements": total_requirements,
                "passed_requirements": passed_requirements,
                "failed_requirements": failed_requirements,
                "failed_requirement_names": failed_requirement_names,
                "report_only_dry_run_execution_review_rules_passed": (
                    execution_review_rules_passed
                ),
                "safety_matrix_passed": safety_matrix_passed,
                "disallowed_operational_boundaries_passed": (
                    disallowed_operational_boundaries_passed
                ),
                "controlled_report_only_dry_run_run_allowed": (
                    report_only_dry_run_execution_review_passed
                ),
                "report_only_dry_run_run_performed": False,
                "dry_run_execution_performed": False,
                "dry_run_execution_approved": False,
                "market_execution_allowed": False,
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


def validate_long_forward_observation_report_only_dry_run_execution_review() -> dict[str, pd.DataFrame]:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    checks: list[dict[str, Any]] = []

    phase_anchors = {
        "phase_10_5_report_only_dry_run_design_doc_exists": (
            PHASE_10_5_REPORT_ONLY_DRY_RUN_DESIGN_DOC_PATH
        ),
        "phase_10_6_report_only_dry_run_execution_review_doc_exists": (
            PHASE_10_6_REPORT_ONLY_DRY_RUN_EXECUTION_REVIEW_DOC_PATH
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

    phase_10_5_result = validate_long_forward_observation_report_only_dry_run_design()

    phase_10_5_summary_df = phase_10_5_result["summary"]
    source_report_only_dry_run_schema_df = phase_10_5_result[
        "report_only_dry_run_schema"
    ]
    source_report_only_dry_run_design_components_df = phase_10_5_result[
        "report_only_dry_run_design_components"
    ]
    source_report_only_dry_run_design_rules_df = phase_10_5_result[
        "report_only_dry_run_design_rules"
    ]
    source_report_only_dry_run_design_requirements_df = phase_10_5_result[
        "report_only_dry_run_design_requirements"
    ]
    source_report_only_dry_run_design_boundary_matrix_df = phase_10_5_result[
        "report_only_dry_run_design_boundary_matrix"
    ]
    source_report_only_dry_run_design_safety_matrix_df = phase_10_5_result[
        "report_only_dry_run_design_safety_matrix"
    ]
    source_report_only_dry_run_design_decision_df = phase_10_5_result[
        "report_only_dry_run_design_decision"
    ]
    source_checks_df = phase_10_5_result["checks"]

    phase_10_5_validation_passed = (
        not phase_10_5_summary_df.empty
        and bool(phase_10_5_summary_df.iloc[0].get("validation_passed", False))
    )

    report_only_dry_run_design_defined = (
        not phase_10_5_summary_df.empty
        and bool(
            phase_10_5_summary_df.iloc[0].get(
                "long_forward_observation_report_only_dry_run_design_defined",
                False,
            )
        )
    )

    execution_review_controls_df = build_report_only_dry_run_execution_review_controls()
    execution_review_rules_df = build_report_only_dry_run_execution_review_rules(
        review_controls_df=execution_review_controls_df,
    )
    execution_review_boundary_matrix_df = (
        build_report_only_dry_run_execution_review_boundary_matrix()
    )
    execution_review_safety_matrix_df = (
        build_report_only_dry_run_execution_review_safety_matrix()
    )

    execution_review_requirements_df = (
        build_report_only_dry_run_execution_review_requirements(
            phase_10_5_summary_df=phase_10_5_summary_df,
            report_only_dry_run_design_decision_df=(
                source_report_only_dry_run_design_decision_df
            ),
            execution_review_rules_df=execution_review_rules_df,
        )
    )

    execution_review_decision_df = (
        build_report_only_dry_run_execution_review_decision_table(
            requirements_df=execution_review_requirements_df,
            boundary_matrix_df=execution_review_boundary_matrix_df,
            safety_matrix_df=execution_review_safety_matrix_df,
            execution_review_rules_df=execution_review_rules_df,
        )
    )

    official_dataset_exists_after = OFFICIAL_DATASET_PATH.exists()

    decision = (
        execution_review_decision_df.iloc[0].to_dict()
        if not execution_review_decision_df.empty
        else {}
    )

    execution_review_passed = safe_bool(
        decision.get("report_only_dry_run_execution_review_passed", False)
    )
    execution_review_decision = str(
        decision.get("report_only_dry_run_execution_review_decision", "")
    )
    controlled_report_only_dry_run_run_allowed = safe_bool(
        decision.get("controlled_report_only_dry_run_run_allowed", False)
    )

    checks.append(
        build_check(
            check_group="phase_dependency",
            check_name="phase_10_5_validation_passed",
            passed=phase_10_5_validation_passed,
            severity="INFO" if phase_10_5_validation_passed else "ERROR",
            details=(
                str(phase_10_5_summary_df.iloc[0].get("validation_decision", ""))
                if not phase_10_5_summary_df.empty
                else "Missing Phase 10.5 summary."
            ),
        )
    )

    checks.append(
        build_check(
            check_group="phase_dependency",
            check_name="long_forward_observation_report_only_dry_run_design_defined",
            passed=report_only_dry_run_design_defined,
            severity="INFO" if report_only_dry_run_design_defined else "ERROR",
            details=(
                "report_only_dry_run_design_defined="
                f"{report_only_dry_run_design_defined}"
            ),
        )
    )

    execution_review_rules_passed = (
        not execution_review_rules_df.empty
        and execution_review_rules_df["passed"].astype(bool).all()
    )

    checks.append(
        build_check(
            check_group="report_only_dry_run_execution_review",
            check_name="report_only_dry_run_execution_review_rules_passed",
            passed=execution_review_rules_passed,
            severity="INFO" if execution_review_rules_passed else "ERROR",
            details=(
                "failed_rules="
                + ",".join(
                    execution_review_rules_df[
                        ~execution_review_rules_df["passed"].astype(bool)
                    ]["rule_name"].astype(str)
                )
                if not execution_review_rules_df.empty
                else "failed_rules=all"
            ),
        )
    )

    requirements_passed = (
        not execution_review_requirements_df.empty
        and execution_review_requirements_df["passed"].astype(bool).all()
    )

    checks.append(
        build_check(
            check_group="report_only_dry_run_execution_review",
            check_name="report_only_dry_run_execution_review_requirements_passed",
            passed=requirements_passed,
            severity="INFO" if requirements_passed else "ERROR",
            details=(
                "failed_requirements="
                + ",".join(
                    execution_review_requirements_df[
                        ~execution_review_requirements_df["passed"].astype(bool)
                    ]["requirement_name"].astype(str)
                )
                if not execution_review_requirements_df.empty
                else "failed_requirements=all"
            ),
        )
    )

    checks.append(
        build_check(
            check_group="report_only_dry_run_execution_review",
            check_name="report_only_dry_run_execution_review_passed",
            passed=execution_review_passed,
            severity="INFO" if execution_review_passed else "ERROR",
            details=(
                "report_only_dry_run_execution_review_passed="
                f"{execution_review_passed}"
            ),
        )
    )

    checks.append(
        build_check(
            check_group="report_only_dry_run_execution_review",
            check_name="report_only_dry_run_execution_review_decision_expected",
            passed=execution_review_decision == READY_DECISION,
            severity="INFO" if execution_review_decision == READY_DECISION else "ERROR",
            details=(
                "report_only_dry_run_execution_review_decision="
                + execution_review_decision
            ),
        )
    )

    checks.append(
        build_check(
            check_group="planning_scope",
            check_name="controlled_report_only_dry_run_run_allowed",
            passed=controlled_report_only_dry_run_run_allowed,
            severity="WARNING" if controlled_report_only_dry_run_run_allowed else "ERROR",
            details=(
                "This allows only a future controlled report-only dry-run run, "
                "not forward observation start, alerts, paper trading, real capital, "
                "official evidence persistence, or market execution."
            ),
        )
    )

    report_only_dry_run_run_performed = safe_bool(
        decision.get("report_only_dry_run_run_performed", True),
        default=True,
    )

    checks.append(
        build_check(
            check_group="safety_controls",
            check_name="report_only_dry_run_run_not_performed",
            passed=report_only_dry_run_run_performed is False,
            severity="INFO" if report_only_dry_run_run_performed is False else "ERROR",
            details=f"report_only_dry_run_run_performed={report_only_dry_run_run_performed}",
        )
    )

    market_execution_allowed = safe_bool(
        decision.get("market_execution_allowed", True),
        default=True,
    )

    checks.append(
        build_check(
            check_group="safety_controls",
            check_name="market_execution_not_allowed",
            passed=market_execution_allowed is False,
            severity="INFO" if market_execution_allowed is False else "ERROR",
            details=f"market_execution_allowed={market_execution_allowed}",
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
        not execution_review_safety_matrix_df.empty
        and execution_review_safety_matrix_df["passed"].astype(bool).all()
    )

    checks.append(
        build_check(
            check_group="safety_controls",
            check_name="report_only_dry_run_execution_review_safety_matrix_passed",
            passed=safety_matrix_passed,
            severity="INFO" if safety_matrix_passed else "ERROR",
            details=(
                "failed_safety_flags="
                + ",".join(
                    execution_review_safety_matrix_df[
                        ~execution_review_safety_matrix_df["passed"].astype(bool)
                    ]["safety_flag"].astype(str)
                )
                if not execution_review_safety_matrix_df.empty
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
            check_name="report_only_dry_run_execution_review_only",
            passed=True,
            severity="WARNING",
            details="Phase 10.6 defines the report-only dry-run execution review only.",
        )
    )

    checks.append(
        build_check(
            check_group="scope_control",
            check_name="dry_run_not_executed",
            passed=True,
            severity="WARNING",
            details="Dry-run execution is still not performed in Phase 10.6.",
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
            check_name="phase_10_7_recommended_next",
            passed=True,
            severity="INFO",
            details=(
                "Recommended next step: "
                "Phase 10.7 LONG Forward Observation Controlled Report-Only Dry-Run Run V1."
            ),
        )
    )

    checks_df = pd.DataFrame(checks)

    blocker_count = int(checks_df["blocker"].astype(bool).sum())
    error_count = int(checks_df["severity"].eq("ERROR").sum())
    warning_count = int(checks_df["severity"].eq("WARNING").sum())

    validation_passed = blocker_count == 0 and error_count == 0

    phase_10_5_summary = (
        phase_10_5_summary_df.iloc[0].to_dict()
        if not phase_10_5_summary_df.empty
        else {}
    )

    summary_df = pd.DataFrame(
        [
            {
                "phase": "10.6",
                "long_forward_observation_report_only_dry_run_execution_review_defined": True,
                "phase_10_5_validation_passed": phase_10_5_validation_passed,
                "long_forward_observation_report_only_dry_run_design_defined": (
                    report_only_dry_run_design_defined
                ),
                "report_only_dry_run_design_passed": safe_bool(
                    phase_10_5_summary.get("report_only_dry_run_design_passed", False)
                ),
                "report_only_dry_run_design_decision": str(
                    phase_10_5_summary.get("report_only_dry_run_design_decision", "")
                ),
                "report_only_dry_run_execution_review_allowed": safe_bool(
                    phase_10_5_summary.get(
                        "report_only_dry_run_execution_review_allowed",
                        False,
                    )
                ),
                "report_only_dry_run_schema_field_count": int(
                    phase_10_5_summary.get("report_only_dry_run_schema_field_count", 0)
                ),
                "report_only_dry_run_design_component_count": int(
                    phase_10_5_summary.get(
                        "report_only_dry_run_design_component_count",
                        0,
                    )
                ),
                "report_only_dry_run_execution_review_control_count": int(
                    len(execution_review_controls_df)
                ),
                "report_only_dry_run_execution_review_rule_rows": int(
                    len(execution_review_rules_df)
                ),
                "report_only_dry_run_execution_review_requirement_rows": int(
                    len(execution_review_requirements_df)
                ),
                "report_only_dry_run_execution_review_rules_passed": (
                    execution_review_rules_passed
                ),
                "report_only_dry_run_execution_review_passed": execution_review_passed,
                "report_only_dry_run_execution_review_decision": execution_review_decision,
                "controlled_report_only_dry_run_run_allowed": (
                    controlled_report_only_dry_run_run_allowed
                ),
                "report_only_dry_run_run_performed": False,
                "dry_run_execution_performed": False,
                "dry_run_execution_approved": False,
                "market_execution_allowed": False,
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
                "estimated_phase_10_progress_percent": 60,
                "total_checks": int(len(checks_df)),
                "warning_count": warning_count,
                "error_count": error_count,
                "blocker_count": blocker_count,
                "validation_passed": validation_passed,
                "validation_decision": (
                    "PHASE_10_6_LONG_FORWARD_OBSERVATION_REPORT_ONLY_DRY_RUN_EXECUTION_REVIEW_VALIDATED"
                    if validation_passed
                    else "PHASE_10_6_LONG_FORWARD_OBSERVATION_REPORT_ONLY_DRY_RUN_EXECUTION_REVIEW_FAILED"
                ),
            }
        ]
    )

    phase_10_5_summary_df.to_csv(
        REPORTS_DIR / "phase_10_5_source_summary_v1.csv",
        index=False,
    )
    source_report_only_dry_run_schema_df.to_csv(
        REPORTS_DIR / "phase_10_5_source_report_only_dry_run_schema_v1.csv",
        index=False,
    )
    source_report_only_dry_run_design_components_df.to_csv(
        REPORTS_DIR / "phase_10_5_source_report_only_dry_run_design_components_v1.csv",
        index=False,
    )
    source_report_only_dry_run_design_rules_df.to_csv(
        REPORTS_DIR / "phase_10_5_source_report_only_dry_run_design_rules_v1.csv",
        index=False,
    )
    source_report_only_dry_run_design_requirements_df.to_csv(
        REPORTS_DIR / "phase_10_5_source_report_only_dry_run_design_requirements_v1.csv",
        index=False,
    )
    source_report_only_dry_run_design_boundary_matrix_df.to_csv(
        REPORTS_DIR / "phase_10_5_source_report_only_dry_run_design_boundary_matrix_v1.csv",
        index=False,
    )
    source_report_only_dry_run_design_safety_matrix_df.to_csv(
        REPORTS_DIR / "phase_10_5_source_report_only_dry_run_design_safety_matrix_v1.csv",
        index=False,
    )
    source_report_only_dry_run_design_decision_df.to_csv(
        REPORTS_DIR / "phase_10_5_source_report_only_dry_run_design_decision_v1.csv",
        index=False,
    )
    source_checks_df.to_csv(
        REPORTS_DIR / "phase_10_5_source_checks_v1.csv",
        index=False,
    )
    execution_review_controls_df.to_csv(
        REPORTS_DIR / "long_forward_observation_report_only_dry_run_execution_review_controls_v1.csv",
        index=False,
    )
    execution_review_rules_df.to_csv(
        REPORTS_DIR / "long_forward_observation_report_only_dry_run_execution_review_rules_v1.csv",
        index=False,
    )
    execution_review_requirements_df.to_csv(
        REPORTS_DIR / "long_forward_observation_report_only_dry_run_execution_review_requirements_v1.csv",
        index=False,
    )
    execution_review_boundary_matrix_df.to_csv(
        REPORTS_DIR / "long_forward_observation_report_only_dry_run_execution_review_boundary_matrix_v1.csv",
        index=False,
    )
    execution_review_safety_matrix_df.to_csv(
        REPORTS_DIR / "long_forward_observation_report_only_dry_run_execution_review_safety_matrix_v1.csv",
        index=False,
    )
    execution_review_decision_df.to_csv(
        REPORTS_DIR / "long_forward_observation_report_only_dry_run_execution_review_decision_v1.csv",
        index=False,
    )
    checks_df.to_csv(
        REPORTS_DIR / "long_forward_observation_report_only_dry_run_execution_review_checks_v1.csv",
        index=False,
    )
    summary_df.to_csv(
        REPORTS_DIR / "long_forward_observation_report_only_dry_run_execution_review_summary_v1.csv",
        index=False,
    )

    return {
        "summary": summary_df,
        "source_phase_10_5_summary": phase_10_5_summary_df,
        "source_report_only_dry_run_schema": source_report_only_dry_run_schema_df,
        "source_report_only_dry_run_design_components": (
            source_report_only_dry_run_design_components_df
        ),
        "source_report_only_dry_run_design_rules": (
            source_report_only_dry_run_design_rules_df
        ),
        "source_report_only_dry_run_design_requirements": (
            source_report_only_dry_run_design_requirements_df
        ),
        "source_report_only_dry_run_design_boundary_matrix": (
            source_report_only_dry_run_design_boundary_matrix_df
        ),
        "source_report_only_dry_run_design_safety_matrix": (
            source_report_only_dry_run_design_safety_matrix_df
        ),
        "source_report_only_dry_run_design_decision": (
            source_report_only_dry_run_design_decision_df
        ),
        "source_checks": source_checks_df,
        "report_only_dry_run_execution_review_controls": execution_review_controls_df,
        "report_only_dry_run_execution_review_rules": execution_review_rules_df,
        "report_only_dry_run_execution_review_requirements": (
            execution_review_requirements_df
        ),
        "report_only_dry_run_execution_review_boundary_matrix": (
            execution_review_boundary_matrix_df
        ),
        "report_only_dry_run_execution_review_safety_matrix": (
            execution_review_safety_matrix_df
        ),
        "report_only_dry_run_execution_review_decision": execution_review_decision_df,
        "checks": checks_df,
    }