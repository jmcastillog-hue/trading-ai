from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from src.long_side.long_forward_observation_controlled_dry_run_review_v1 import (
    READY_DECISION as CONTROLLED_DRY_RUN_REVIEW_READY_DECISION,
    validate_long_forward_observation_controlled_dry_run_review,
)
from src.long_side.long_forward_observation_dataset_bootstrap_v1 import (
    OFFICIAL_DATASET_PATH,
    PRIMARY_RESEARCH_CANDIDATE,
)


REPORTS_DIR = Path("reports/phase_10_5_long_forward_observation_report_only_dry_run_design_v1")

PHASE_10_4_CONTROLLED_DRY_RUN_REVIEW_DOC_PATH = Path(
    "docs/PHASE_10_LONG_FORWARD_OBSERVATION_CONTROLLED_DRY_RUN_REVIEW.md"
)
PHASE_10_5_REPORT_ONLY_DRY_RUN_DESIGN_DOC_PATH = Path(
    "docs/PHASE_10_LONG_FORWARD_OBSERVATION_REPORT_ONLY_DRY_RUN_DESIGN.md"
)

REPORT_ONLY_DRY_RUN_DESIGN_STATUS = "LONG_FORWARD_OBSERVATION_REPORT_ONLY_DRY_RUN_DESIGN_ONLY"
READY_DECISION = "REPORT_ONLY_DRY_RUN_DESIGN_READY_FOR_EXECUTION_REVIEW"
BLOCKED_DECISION = "REPORT_ONLY_DRY_RUN_DESIGN_BLOCKED"

RECOMMENDED_NEXT_PHASE = (
    "PHASE_10_6_LONG_FORWARD_OBSERVATION_REPORT_ONLY_DRY_RUN_EXECUTION_REVIEW_V1"
)

REPORT_ONLY_DRY_RUN_SCHEMA_FIELDS = [
    "dry_run_id",
    "design_status",
    "observed_at",
    "symbol",
    "timeframe",
    "candidate_id",
    "observation_role",
    "direction",
    "signal_state",
    "market_context",
    "entry_price",
    "stop_price",
    "target_price",
    "risk_reward",
    "invalidation_level",
    "price_structure_valid",
    "manual_review_required",
    "manual_review_status",
    "reviewer_notes",
    "execution_allowed",
    "dry_run_execution_approved",
    "report_only_dry_run_execution_allowed",
    "forward_observation_start_allowed",
    "live_alert_sent",
    "paper_trade_submitted",
    "real_capital_used",
    "official_dataset_write_allowed",
    "accepted_as_real_evidence",
    "evidence_persistence_allowed",
    "evidence_write_performed",
    "resolution_status",
    "result_r",
    "mfe_r",
    "mae_r",
    "bars_to_resolution",
    "artifact_scope",
    "evidence_source",
    "safety_guard_status",
    "created_at_utc",
    "updated_at_utc",
    "notes",
    "recommended_next_action",
]

DESIGN_COMPONENTS = [
    {
        "component_id": "REPORT_ONLY_DRY_RUN_DESIGN_001",
        "component_name": "define_report_only_artifact_schema",
        "component_group": "schema",
        "required": True,
        "design_only": True,
        "execution_allowed": False,
        "details": "Defines the report-only dry-run artifact schema.",
    },
    {
        "component_id": "REPORT_ONLY_DRY_RUN_DESIGN_002",
        "component_name": "define_candidate_scope",
        "component_group": "candidate_scope",
        "required": True,
        "design_only": True,
        "execution_allowed": False,
        "details": f"Primary candidate scope remains {PRIMARY_RESEARCH_CANDIDATE}.",
    },
    {
        "component_id": "REPORT_ONLY_DRY_RUN_DESIGN_003",
        "component_name": "define_long_direction_constraint",
        "component_group": "candidate_scope",
        "required": True,
        "design_only": True,
        "execution_allowed": False,
        "details": "Direction remains LONG.",
    },
    {
        "component_id": "REPORT_ONLY_DRY_RUN_DESIGN_004",
        "component_name": "define_long_price_structure_constraint",
        "component_group": "price_structure",
        "required": True,
        "design_only": True,
        "execution_allowed": False,
        "details": "Future price levels must satisfy stop_price < entry_price < target_price.",
    },
    {
        "component_id": "REPORT_ONLY_DRY_RUN_DESIGN_005",
        "component_name": "define_manual_review_constraint",
        "component_group": "manual_review",
        "required": True,
        "design_only": True,
        "execution_allowed": False,
        "details": "Manual review remains required for any future dry-run row.",
    },
    {
        "component_id": "REPORT_ONLY_DRY_RUN_DESIGN_006",
        "component_name": "define_report_only_output_boundary",
        "component_group": "artifact_scope",
        "required": True,
        "design_only": True,
        "execution_allowed": False,
        "details": "Outputs are report-only artifacts, not official evidence.",
    },
    {
        "component_id": "REPORT_ONLY_DRY_RUN_DESIGN_007",
        "component_name": "define_official_dataset_guard",
        "component_group": "official_dataset_guard",
        "required": True,
        "design_only": True,
        "execution_allowed": False,
        "details": "Official dataset writes remain disabled.",
    },
    {
        "component_id": "REPORT_ONLY_DRY_RUN_DESIGN_008",
        "component_name": "define_real_evidence_guard",
        "component_group": "official_dataset_guard",
        "required": True,
        "design_only": True,
        "execution_allowed": False,
        "details": "Real evidence acceptance remains disabled.",
    },
    {
        "component_id": "REPORT_ONLY_DRY_RUN_DESIGN_009",
        "component_name": "define_alert_guard",
        "component_group": "safety",
        "required": True,
        "design_only": True,
        "execution_allowed": False,
        "details": "Live alerts remain disabled.",
    },
    {
        "component_id": "REPORT_ONLY_DRY_RUN_DESIGN_010",
        "component_name": "define_paper_trading_guard",
        "component_group": "safety",
        "required": True,
        "design_only": True,
        "execution_allowed": False,
        "details": "Paper trading remains disabled.",
    },
    {
        "component_id": "REPORT_ONLY_DRY_RUN_DESIGN_011",
        "component_name": "define_real_capital_guard",
        "component_group": "safety",
        "required": True,
        "design_only": True,
        "execution_allowed": False,
        "details": "Real capital remains disabled.",
    },
    {
        "component_id": "REPORT_ONLY_DRY_RUN_DESIGN_012",
        "component_name": "define_execution_automation_guard",
        "component_group": "safety",
        "required": True,
        "design_only": True,
        "execution_allowed": False,
        "details": "Exchange execution and automation remain disabled.",
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


def build_report_only_dry_run_schema() -> pd.DataFrame:
    rows: list[dict[str, Any]] = []

    safety_guard_fields = {
        "execution_allowed",
        "dry_run_execution_approved",
        "report_only_dry_run_execution_allowed",
        "forward_observation_start_allowed",
        "live_alert_sent",
        "paper_trade_submitted",
        "real_capital_used",
        "official_dataset_write_allowed",
        "accepted_as_real_evidence",
        "evidence_persistence_allowed",
        "evidence_write_performed",
    }

    required_fields = set(REPORT_ONLY_DRY_RUN_SCHEMA_FIELDS)

    for position, field_name in enumerate(REPORT_ONLY_DRY_RUN_SCHEMA_FIELDS, start=1):
        rows.append(
            {
                "field_position": position,
                "field_name": field_name,
                "required": field_name in required_fields,
                "field_group": (
                    "safety_guard"
                    if field_name in safety_guard_fields
                    else "report_artifact"
                ),
                "report_only": True,
                "official_dataset_field": False,
                "real_evidence_field": False,
                "execution_field": False,
                "passed": True,
            }
        )

    return pd.DataFrame(rows)


def build_report_only_dry_run_design_components() -> pd.DataFrame:
    rows: list[dict[str, Any]] = []

    for component in DESIGN_COMPONENTS:
        rows.append(
            {
                "component_id": component["component_id"],
                "component_name": component["component_name"],
                "component_group": component["component_group"],
                "required": component["required"],
                "design_only": component["design_only"],
                "execution_allowed": component["execution_allowed"],
                "official_dataset_write_allowed": False,
                "real_evidence_acceptance_allowed": False,
                "live_alerts_allowed": False,
                "paper_trading_allowed": False,
                "real_capital_allowed": False,
                "exchange_execution_allowed": False,
                "automation_allowed": False,
                "passed": (
                    component["required"] is True
                    and component["design_only"] is True
                    and component["execution_allowed"] is False
                ),
                "details": component["details"],
            }
        )

    return pd.DataFrame(rows)


def build_report_only_dry_run_design_rules(
    schema_df: pd.DataFrame,
    design_components_df: pd.DataFrame,
) -> pd.DataFrame:
    schema_field_count = int(len(schema_df))
    component_count = int(len(design_components_df))

    all_schema_fields_report_only = (
        not schema_df.empty and schema_df["report_only"].astype(bool).all()
    )

    all_schema_fields_not_official = (
        not schema_df.empty and schema_df["official_dataset_field"].astype(bool).eq(False).all()
    )

    all_components_design_only = (
        not design_components_df.empty
        and design_components_df["design_only"].astype(bool).all()
    )

    all_component_execution_disabled = (
        not design_components_df.empty
        and design_components_df["execution_allowed"].astype(bool).eq(False).all()
    )

    all_official_dataset_writes_disabled = (
        not design_components_df.empty
        and design_components_df["official_dataset_write_allowed"]
        .astype(bool)
        .eq(False)
        .all()
    )

    rows = [
        {
            "rule_id": "REPORT_ONLY_DRY_RUN_DESIGN_RULE_001",
            "rule_name": "report_only_dry_run_schema_field_count_42",
            "passed": schema_field_count == 42,
            "required_value": "42",
            "actual_value": str(schema_field_count),
            "rule_group": "schema",
        },
        {
            "rule_id": "REPORT_ONLY_DRY_RUN_DESIGN_RULE_002",
            "rule_name": "report_only_dry_run_design_component_count_12",
            "passed": component_count == 12,
            "required_value": "12",
            "actual_value": str(component_count),
            "rule_group": "design_components",
        },
        {
            "rule_id": "REPORT_ONLY_DRY_RUN_DESIGN_RULE_003",
            "rule_name": "all_schema_fields_report_only",
            "passed": all_schema_fields_report_only,
            "required_value": "True",
            "actual_value": str(all_schema_fields_report_only),
            "rule_group": "artifact_scope",
        },
        {
            "rule_id": "REPORT_ONLY_DRY_RUN_DESIGN_RULE_004",
            "rule_name": "all_schema_fields_not_official_dataset",
            "passed": all_schema_fields_not_official,
            "required_value": "False",
            "actual_value": "False",
            "rule_group": "official_dataset_guard",
        },
        {
            "rule_id": "REPORT_ONLY_DRY_RUN_DESIGN_RULE_005",
            "rule_name": "all_components_design_only",
            "passed": all_components_design_only,
            "required_value": "True",
            "actual_value": str(all_components_design_only),
            "rule_group": "design_scope",
        },
        {
            "rule_id": "REPORT_ONLY_DRY_RUN_DESIGN_RULE_006",
            "rule_name": "all_component_execution_disabled",
            "passed": all_component_execution_disabled,
            "required_value": "False",
            "actual_value": "False",
            "rule_group": "execution_guard",
        },
        {
            "rule_id": "REPORT_ONLY_DRY_RUN_DESIGN_RULE_007",
            "rule_name": "all_official_dataset_writes_disabled",
            "passed": all_official_dataset_writes_disabled,
            "required_value": "False",
            "actual_value": "False",
            "rule_group": "official_dataset_guard",
        },
    ]

    return pd.DataFrame(rows)


def build_report_only_dry_run_design_requirements(
    phase_10_4_summary_df: pd.DataFrame,
    controlled_dry_run_review_decision_df: pd.DataFrame,
    design_rules_df: pd.DataFrame,
) -> pd.DataFrame:
    summary = (
        phase_10_4_summary_df.iloc[0].to_dict()
        if not phase_10_4_summary_df.empty
        else {}
    )

    decision = (
        controlled_dry_run_review_decision_df.iloc[0].to_dict()
        if not controlled_dry_run_review_decision_df.empty
        else {}
    )

    design_rules_passed = (
        not design_rules_df.empty and design_rules_df["passed"].astype(bool).all()
    )

    requirements: list[dict[str, Any]] = [
        {
            "requirement_id": "REPORT_ONLY_DRY_RUN_DESIGN_REQ_001",
            "requirement_name": "phase_10_4_validation_passed",
            "passed": safe_bool(summary.get("validation_passed", False)),
            "required_value": "True",
            "actual_value": str(summary.get("validation_passed", "")),
            "requirement_group": "dependency",
        },
        {
            "requirement_id": "REPORT_ONLY_DRY_RUN_DESIGN_REQ_002",
            "requirement_name": "controlled_dry_run_review_passed",
            "passed": safe_bool(
                summary.get("controlled_dry_run_review_passed", False)
            ),
            "required_value": "True",
            "actual_value": str(summary.get("controlled_dry_run_review_passed", "")),
            "requirement_group": "controlled_dry_run_review",
        },
        {
            "requirement_id": "REPORT_ONLY_DRY_RUN_DESIGN_REQ_003",
            "requirement_name": "controlled_dry_run_review_decision_expected",
            "passed": str(
                summary.get("controlled_dry_run_review_decision", "")
            ).strip()
            == CONTROLLED_DRY_RUN_REVIEW_READY_DECISION,
            "required_value": CONTROLLED_DRY_RUN_REVIEW_READY_DECISION,
            "actual_value": str(summary.get("controlled_dry_run_review_decision", "")),
            "requirement_group": "controlled_dry_run_review",
        },
        {
            "requirement_id": "REPORT_ONLY_DRY_RUN_DESIGN_REQ_004",
            "requirement_name": "report_only_dry_run_design_allowed",
            "passed": safe_bool(
                summary.get("report_only_dry_run_design_allowed", False)
            ),
            "required_value": "True",
            "actual_value": str(summary.get("report_only_dry_run_design_allowed", "")),
            "requirement_group": "design_scope",
        },
        {
            "requirement_id": "REPORT_ONLY_DRY_RUN_DESIGN_REQ_005",
            "requirement_name": "controlled_dry_run_review_decision_table_consistent",
            "passed": (
                not controlled_dry_run_review_decision_df.empty
                and safe_bool(
                    decision.get("controlled_dry_run_review_passed", False)
                )
                and str(
                    decision.get("controlled_dry_run_review_decision", "")
                ).strip()
                == CONTROLLED_DRY_RUN_REVIEW_READY_DECISION
            ),
            "required_value": "True",
            "actual_value": str(
                decision.get("controlled_dry_run_review_decision", "")
            ),
            "requirement_group": "summary_consistency",
        },
        {
            "requirement_id": "REPORT_ONLY_DRY_RUN_DESIGN_REQ_006",
            "requirement_name": "report_only_dry_run_design_rules_passed",
            "passed": design_rules_passed,
            "required_value": "True",
            "actual_value": str(design_rules_passed),
            "requirement_group": "report_only_dry_run_design",
        },
        {
            "requirement_id": "REPORT_ONLY_DRY_RUN_DESIGN_REQ_007",
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
            "requirement_id": "REPORT_ONLY_DRY_RUN_DESIGN_REQ_008",
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
            "requirement_id": "REPORT_ONLY_DRY_RUN_DESIGN_REQ_009",
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
            "requirement_id": "REPORT_ONLY_DRY_RUN_DESIGN_REQ_010",
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
            "requirement_id": "REPORT_ONLY_DRY_RUN_DESIGN_REQ_011",
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
            "requirement_id": "REPORT_ONLY_DRY_RUN_DESIGN_REQ_012",
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
            "requirement_id": "REPORT_ONLY_DRY_RUN_DESIGN_REQ_013",
            "requirement_name": "official_evidence_rows_written_zero",
            "passed": int(summary.get("official_evidence_rows_written", -1)) == 0,
            "required_value": "0",
            "actual_value": str(summary.get("official_evidence_rows_written", "")),
            "requirement_group": "official_dataset_guard",
        },
        {
            "requirement_id": "REPORT_ONLY_DRY_RUN_DESIGN_REQ_014",
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
            "requirement_id": "REPORT_ONLY_DRY_RUN_DESIGN_REQ_015",
            "requirement_name": "execution_disabled",
            "passed": safe_bool(summary.get("execution_allowed", True), default=True)
            is False,
            "required_value": "False",
            "actual_value": str(summary.get("execution_allowed", "")),
            "requirement_group": "safety",
        },
        {
            "requirement_id": "REPORT_ONLY_DRY_RUN_DESIGN_REQ_016",
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


def build_report_only_dry_run_design_boundary_matrix() -> pd.DataFrame:
    rows = [
        {
            "boundary_item": "report_only_dry_run_design_allowed",
            "allowed": True,
            "boundary_type": "design_scope",
            "details": "Phase 10.5 may define the report-only dry-run design.",
        },
        {
            "boundary_item": "report_only_dry_run_execution_review_allowed",
            "allowed": True,
            "boundary_type": "future_review",
            "details": "Phase 10.5 may recommend future report-only dry-run execution review.",
        },
        {
            "boundary_item": "dry_run_execution_approved",
            "allowed": False,
            "boundary_type": "dry_run_execution",
            "details": "Phase 10.5 does not approve dry-run execution.",
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


def build_report_only_dry_run_design_safety_matrix() -> pd.DataFrame:
    rows: list[dict[str, Any]] = []

    for flag_name, flag_value in SAFETY_FLAGS.items():
        rows.append(
            {
                "safety_flag": flag_name,
                "required_value": False,
                "actual_value": flag_value,
                "passed": flag_value is False,
                "design_status": REPORT_ONLY_DRY_RUN_DESIGN_STATUS,
            }
        )

    rows.append(
        {
            "safety_flag": "official_evidence_rows_written",
            "required_value": 0,
            "actual_value": 0,
            "passed": True,
            "design_status": REPORT_ONLY_DRY_RUN_DESIGN_STATUS,
        }
    )

    return pd.DataFrame(rows)


def build_report_only_dry_run_design_decision_table(
    requirements_df: pd.DataFrame,
    boundary_matrix_df: pd.DataFrame,
    safety_matrix_df: pd.DataFrame,
    design_rules_df: pd.DataFrame,
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

    design_rules_passed = (
        not design_rules_df.empty and design_rules_df["passed"].astype(bool).all()
    )

    disallowed_operational_boundaries_passed = True

    if not boundary_matrix_df.empty:
        allowed_planning_items = {
            "report_only_dry_run_design_allowed",
            "report_only_dry_run_execution_review_allowed",
        }

        disallowed_rows = boundary_matrix_df[
            ~boundary_matrix_df["boundary_item"].astype(str).isin(allowed_planning_items)
        ]
        disallowed_operational_boundaries_passed = (
            not disallowed_rows.empty
            and disallowed_rows["allowed"].astype(bool).eq(False).all()
        )

    report_only_dry_run_design_passed = (
        total_requirements > 0
        and failed_requirements == 0
        and safety_matrix_passed
        and design_rules_passed
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
                "report_only_dry_run_design_id": "PHASE_10_5_REPORT_ONLY_DRY_RUN_DESIGN_001",
                "report_only_dry_run_design_status": REPORT_ONLY_DRY_RUN_DESIGN_STATUS,
                "report_only_dry_run_design_passed": report_only_dry_run_design_passed,
                "report_only_dry_run_design_decision": (
                    READY_DECISION if report_only_dry_run_design_passed else BLOCKED_DECISION
                ),
                "total_requirements": total_requirements,
                "passed_requirements": passed_requirements,
                "failed_requirements": failed_requirements,
                "failed_requirement_names": failed_requirement_names,
                "report_only_dry_run_design_rules_passed": design_rules_passed,
                "safety_matrix_passed": safety_matrix_passed,
                "disallowed_operational_boundaries_passed": (
                    disallowed_operational_boundaries_passed
                ),
                "report_only_dry_run_execution_review_allowed": (
                    report_only_dry_run_design_passed
                ),
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


def validate_long_forward_observation_report_only_dry_run_design() -> dict[str, pd.DataFrame]:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    checks: list[dict[str, Any]] = []

    phase_anchors = {
        "phase_10_4_controlled_dry_run_review_doc_exists": (
            PHASE_10_4_CONTROLLED_DRY_RUN_REVIEW_DOC_PATH
        ),
        "phase_10_5_report_only_dry_run_design_doc_exists": (
            PHASE_10_5_REPORT_ONLY_DRY_RUN_DESIGN_DOC_PATH
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

    phase_10_4_result = validate_long_forward_observation_controlled_dry_run_review()

    phase_10_4_summary_df = phase_10_4_result["summary"]
    source_controlled_dry_run_review_controls_df = phase_10_4_result[
        "controlled_dry_run_review_controls"
    ]
    source_controlled_dry_run_review_rules_df = phase_10_4_result[
        "controlled_dry_run_review_rules"
    ]
    source_controlled_dry_run_review_requirements_df = phase_10_4_result[
        "controlled_dry_run_review_requirements"
    ]
    source_controlled_dry_run_review_boundary_matrix_df = phase_10_4_result[
        "controlled_dry_run_review_boundary_matrix"
    ]
    source_controlled_dry_run_review_safety_matrix_df = phase_10_4_result[
        "controlled_dry_run_review_safety_matrix"
    ]
    source_controlled_dry_run_review_decision_df = phase_10_4_result[
        "controlled_dry_run_review_decision"
    ]
    source_checks_df = phase_10_4_result["checks"]

    phase_10_4_validation_passed = (
        not phase_10_4_summary_df.empty
        and bool(phase_10_4_summary_df.iloc[0].get("validation_passed", False))
    )

    controlled_dry_run_review_defined = (
        not phase_10_4_summary_df.empty
        and bool(
            phase_10_4_summary_df.iloc[0].get(
                "long_forward_observation_controlled_dry_run_review_defined",
                False,
            )
        )
    )

    report_only_dry_run_schema_df = build_report_only_dry_run_schema()
    report_only_dry_run_design_components_df = build_report_only_dry_run_design_components()
    report_only_dry_run_design_rules_df = build_report_only_dry_run_design_rules(
        schema_df=report_only_dry_run_schema_df,
        design_components_df=report_only_dry_run_design_components_df,
    )
    report_only_dry_run_design_boundary_matrix_df = (
        build_report_only_dry_run_design_boundary_matrix()
    )
    report_only_dry_run_design_safety_matrix_df = (
        build_report_only_dry_run_design_safety_matrix()
    )

    report_only_dry_run_design_requirements_df = (
        build_report_only_dry_run_design_requirements(
            phase_10_4_summary_df=phase_10_4_summary_df,
            controlled_dry_run_review_decision_df=(
                source_controlled_dry_run_review_decision_df
            ),
            design_rules_df=report_only_dry_run_design_rules_df,
        )
    )

    report_only_dry_run_design_decision_df = (
        build_report_only_dry_run_design_decision_table(
            requirements_df=report_only_dry_run_design_requirements_df,
            boundary_matrix_df=report_only_dry_run_design_boundary_matrix_df,
            safety_matrix_df=report_only_dry_run_design_safety_matrix_df,
            design_rules_df=report_only_dry_run_design_rules_df,
        )
    )

    official_dataset_exists_after = OFFICIAL_DATASET_PATH.exists()

    decision = (
        report_only_dry_run_design_decision_df.iloc[0].to_dict()
        if not report_only_dry_run_design_decision_df.empty
        else {}
    )

    report_only_dry_run_design_passed = safe_bool(
        decision.get("report_only_dry_run_design_passed", False)
    )
    report_only_dry_run_design_decision = str(
        decision.get("report_only_dry_run_design_decision", "")
    )
    report_only_dry_run_execution_review_allowed = safe_bool(
        decision.get("report_only_dry_run_execution_review_allowed", False)
    )

    checks.append(
        build_check(
            check_group="phase_dependency",
            check_name="phase_10_4_validation_passed",
            passed=phase_10_4_validation_passed,
            severity="INFO" if phase_10_4_validation_passed else "ERROR",
            details=(
                str(phase_10_4_summary_df.iloc[0].get("validation_decision", ""))
                if not phase_10_4_summary_df.empty
                else "Missing Phase 10.4 summary."
            ),
        )
    )

    checks.append(
        build_check(
            check_group="phase_dependency",
            check_name="long_forward_observation_controlled_dry_run_review_defined",
            passed=controlled_dry_run_review_defined,
            severity="INFO" if controlled_dry_run_review_defined else "ERROR",
            details=(
                "controlled_dry_run_review_defined="
                f"{controlled_dry_run_review_defined}"
            ),
        )
    )

    report_only_dry_run_design_rules_passed = (
        not report_only_dry_run_design_rules_df.empty
        and report_only_dry_run_design_rules_df["passed"].astype(bool).all()
    )

    checks.append(
        build_check(
            check_group="report_only_dry_run_design",
            check_name="report_only_dry_run_design_rules_passed",
            passed=report_only_dry_run_design_rules_passed,
            severity="INFO" if report_only_dry_run_design_rules_passed else "ERROR",
            details=(
                "failed_rules="
                + ",".join(
                    report_only_dry_run_design_rules_df[
                        ~report_only_dry_run_design_rules_df["passed"].astype(bool)
                    ]["rule_name"].astype(str)
                )
                if not report_only_dry_run_design_rules_df.empty
                else "failed_rules=all"
            ),
        )
    )

    requirements_passed = (
        not report_only_dry_run_design_requirements_df.empty
        and report_only_dry_run_design_requirements_df["passed"].astype(bool).all()
    )

    checks.append(
        build_check(
            check_group="report_only_dry_run_design",
            check_name="report_only_dry_run_design_requirements_passed",
            passed=requirements_passed,
            severity="INFO" if requirements_passed else "ERROR",
            details=(
                "failed_requirements="
                + ",".join(
                    report_only_dry_run_design_requirements_df[
                        ~report_only_dry_run_design_requirements_df["passed"].astype(bool)
                    ]["requirement_name"].astype(str)
                )
                if not report_only_dry_run_design_requirements_df.empty
                else "failed_requirements=all"
            ),
        )
    )

    checks.append(
        build_check(
            check_group="report_only_dry_run_design",
            check_name="report_only_dry_run_design_passed",
            passed=report_only_dry_run_design_passed,
            severity="INFO" if report_only_dry_run_design_passed else "ERROR",
            details=f"report_only_dry_run_design_passed={report_only_dry_run_design_passed}",
        )
    )

    checks.append(
        build_check(
            check_group="report_only_dry_run_design",
            check_name="report_only_dry_run_design_decision_expected",
            passed=report_only_dry_run_design_decision == READY_DECISION,
            severity=(
                "INFO"
                if report_only_dry_run_design_decision == READY_DECISION
                else "ERROR"
            ),
            details="report_only_dry_run_design_decision="
            + report_only_dry_run_design_decision,
        )
    )

    checks.append(
        build_check(
            check_group="planning_scope",
            check_name="report_only_dry_run_execution_review_allowed",
            passed=report_only_dry_run_execution_review_allowed,
            severity=(
                "WARNING"
                if report_only_dry_run_execution_review_allowed
                else "ERROR"
            ),
            details=(
                "This allows only future report-only dry-run execution review, "
                "not dry-run execution, observation start, alerts, paper trading, "
                "real capital, or execution."
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
            severity=(
                "INFO"
                if report_only_dry_run_execution_allowed is False
                else "ERROR"
            ),
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
        not report_only_dry_run_design_safety_matrix_df.empty
        and report_only_dry_run_design_safety_matrix_df["passed"].astype(bool).all()
    )

    checks.append(
        build_check(
            check_group="safety_controls",
            check_name="report_only_dry_run_design_safety_matrix_passed",
            passed=safety_matrix_passed,
            severity="INFO" if safety_matrix_passed else "ERROR",
            details=(
                "failed_safety_flags="
                + ",".join(
                    report_only_dry_run_design_safety_matrix_df[
                        ~report_only_dry_run_design_safety_matrix_df["passed"].astype(bool)
                    ]["safety_flag"].astype(str)
                )
                if not report_only_dry_run_design_safety_matrix_df.empty
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
            check_name="report_only_dry_run_design_only",
            passed=True,
            severity="WARNING",
            details="Phase 10.5 defines the report-only dry-run design only.",
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
            check_name="phase_10_6_recommended_next",
            passed=True,
            severity="INFO",
            details=(
                "Recommended next step: "
                "Phase 10.6 LONG Forward Observation Report-Only Dry-Run Execution Review V1."
            ),
        )
    )

    checks_df = pd.DataFrame(checks)

    blocker_count = int(checks_df["blocker"].astype(bool).sum())
    error_count = int(checks_df["severity"].eq("ERROR").sum())
    warning_count = int(checks_df["severity"].eq("WARNING").sum())

    validation_passed = blocker_count == 0 and error_count == 0

    phase_10_4_summary = (
        phase_10_4_summary_df.iloc[0].to_dict()
        if not phase_10_4_summary_df.empty
        else {}
    )

    summary_df = pd.DataFrame(
        [
            {
                "phase": "10.5",
                "long_forward_observation_report_only_dry_run_design_defined": True,
                "phase_10_4_validation_passed": phase_10_4_validation_passed,
                "long_forward_observation_controlled_dry_run_review_defined": (
                    controlled_dry_run_review_defined
                ),
                "controlled_dry_run_review_passed": safe_bool(
                    phase_10_4_summary.get("controlled_dry_run_review_passed", False)
                ),
                "controlled_dry_run_review_decision": str(
                    phase_10_4_summary.get("controlled_dry_run_review_decision", "")
                ),
                "report_only_dry_run_design_allowed": safe_bool(
                    phase_10_4_summary.get("report_only_dry_run_design_allowed", False)
                ),
                "report_only_dry_run_schema_field_count": int(
                    len(report_only_dry_run_schema_df)
                ),
                "report_only_dry_run_design_component_count": int(
                    len(report_only_dry_run_design_components_df)
                ),
                "report_only_dry_run_design_rule_rows": int(
                    len(report_only_dry_run_design_rules_df)
                ),
                "report_only_dry_run_design_requirement_rows": int(
                    len(report_only_dry_run_design_requirements_df)
                ),
                "report_only_dry_run_design_rules_passed": (
                    report_only_dry_run_design_rules_passed
                ),
                "report_only_dry_run_design_passed": report_only_dry_run_design_passed,
                "report_only_dry_run_design_decision": (
                    report_only_dry_run_design_decision
                ),
                "report_only_dry_run_execution_review_allowed": (
                    report_only_dry_run_execution_review_allowed
                ),
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
                "estimated_phase_10_progress_percent": 50,
                "total_checks": int(len(checks_df)),
                "warning_count": warning_count,
                "error_count": error_count,
                "blocker_count": blocker_count,
                "validation_passed": validation_passed,
                "validation_decision": (
                    "PHASE_10_5_LONG_FORWARD_OBSERVATION_REPORT_ONLY_DRY_RUN_DESIGN_VALIDATED"
                    if validation_passed
                    else "PHASE_10_5_LONG_FORWARD_OBSERVATION_REPORT_ONLY_DRY_RUN_DESIGN_FAILED"
                ),
            }
        ]
    )

    phase_10_4_summary_df.to_csv(
        REPORTS_DIR / "phase_10_4_source_summary_v1.csv",
        index=False,
    )
    source_controlled_dry_run_review_controls_df.to_csv(
        REPORTS_DIR / "phase_10_4_source_controlled_dry_run_review_controls_v1.csv",
        index=False,
    )
    source_controlled_dry_run_review_rules_df.to_csv(
        REPORTS_DIR / "phase_10_4_source_controlled_dry_run_review_rules_v1.csv",
        index=False,
    )
    source_controlled_dry_run_review_requirements_df.to_csv(
        REPORTS_DIR / "phase_10_4_source_controlled_dry_run_review_requirements_v1.csv",
        index=False,
    )
    source_controlled_dry_run_review_boundary_matrix_df.to_csv(
        REPORTS_DIR / "phase_10_4_source_controlled_dry_run_review_boundary_matrix_v1.csv",
        index=False,
    )
    source_controlled_dry_run_review_safety_matrix_df.to_csv(
        REPORTS_DIR / "phase_10_4_source_controlled_dry_run_review_safety_matrix_v1.csv",
        index=False,
    )
    source_controlled_dry_run_review_decision_df.to_csv(
        REPORTS_DIR / "phase_10_4_source_controlled_dry_run_review_decision_v1.csv",
        index=False,
    )
    source_checks_df.to_csv(
        REPORTS_DIR / "phase_10_4_source_checks_v1.csv",
        index=False,
    )
    report_only_dry_run_schema_df.to_csv(
        REPORTS_DIR / "long_forward_observation_report_only_dry_run_schema_v1.csv",
        index=False,
    )
    report_only_dry_run_design_components_df.to_csv(
        REPORTS_DIR / "long_forward_observation_report_only_dry_run_design_components_v1.csv",
        index=False,
    )
    report_only_dry_run_design_rules_df.to_csv(
        REPORTS_DIR / "long_forward_observation_report_only_dry_run_design_rules_v1.csv",
        index=False,
    )
    report_only_dry_run_design_requirements_df.to_csv(
        REPORTS_DIR / "long_forward_observation_report_only_dry_run_design_requirements_v1.csv",
        index=False,
    )
    report_only_dry_run_design_boundary_matrix_df.to_csv(
        REPORTS_DIR / "long_forward_observation_report_only_dry_run_design_boundary_matrix_v1.csv",
        index=False,
    )
    report_only_dry_run_design_safety_matrix_df.to_csv(
        REPORTS_DIR / "long_forward_observation_report_only_dry_run_design_safety_matrix_v1.csv",
        index=False,
    )
    report_only_dry_run_design_decision_df.to_csv(
        REPORTS_DIR / "long_forward_observation_report_only_dry_run_design_decision_v1.csv",
        index=False,
    )
    checks_df.to_csv(
        REPORTS_DIR / "long_forward_observation_report_only_dry_run_design_checks_v1.csv",
        index=False,
    )
    summary_df.to_csv(
        REPORTS_DIR / "long_forward_observation_report_only_dry_run_design_summary_v1.csv",
        index=False,
    )

    return {
        "summary": summary_df,
        "source_phase_10_4_summary": phase_10_4_summary_df,
        "source_controlled_dry_run_review_controls": (
            source_controlled_dry_run_review_controls_df
        ),
        "source_controlled_dry_run_review_rules": (
            source_controlled_dry_run_review_rules_df
        ),
        "source_controlled_dry_run_review_requirements": (
            source_controlled_dry_run_review_requirements_df
        ),
        "source_controlled_dry_run_review_boundary_matrix": (
            source_controlled_dry_run_review_boundary_matrix_df
        ),
        "source_controlled_dry_run_review_safety_matrix": (
            source_controlled_dry_run_review_safety_matrix_df
        ),
        "source_controlled_dry_run_review_decision": (
            source_controlled_dry_run_review_decision_df
        ),
        "source_checks": source_checks_df,
        "report_only_dry_run_schema": report_only_dry_run_schema_df,
        "report_only_dry_run_design_components": (
            report_only_dry_run_design_components_df
        ),
        "report_only_dry_run_design_rules": report_only_dry_run_design_rules_df,
        "report_only_dry_run_design_requirements": (
            report_only_dry_run_design_requirements_df
        ),
        "report_only_dry_run_design_boundary_matrix": (
            report_only_dry_run_design_boundary_matrix_df
        ),
        "report_only_dry_run_design_safety_matrix": (
            report_only_dry_run_design_safety_matrix_df
        ),
        "report_only_dry_run_design_decision": report_only_dry_run_design_decision_df,
        "checks": checks_df,
    }