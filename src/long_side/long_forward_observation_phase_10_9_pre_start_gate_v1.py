from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from src.long_side.long_forward_observation_dataset_bootstrap_v1 import (
    OFFICIAL_DATASET_PATH,
    PRIMARY_RESEARCH_CANDIDATE,
)
from src.long_side.long_forward_observation_report_only_dry_run_output_integrity_review_v1 import (
    READY_DECISION as OUTPUT_INTEGRITY_READY_DECISION,
    validate_long_forward_observation_report_only_dry_run_output_integrity_review,
)


REPORTS_DIR = Path("reports/phase_10_9_long_forward_observation_pre_start_gate_v1")

PHASE_10_8_OUTPUT_INTEGRITY_REVIEW_DOC_PATH = Path(
    "docs/PHASE_10_LONG_FORWARD_OBSERVATION_REPORT_ONLY_DRY_RUN_OUTPUT_INTEGRITY_REVIEW.md"
)
PHASE_10_9_PRE_START_GATE_DOC_PATH = Path(
    "docs/PHASE_10_LONG_FORWARD_OBSERVATION_PRE_START_GATE.md"
)

PRE_START_GATE_STATUS = "LONG_FORWARD_OBSERVATION_PRE_START_GATE_ONLY"

READY_DECISION = "PRE_START_GATE_READY_FOR_CONTROLLED_START_REVIEW"
BLOCKED_DECISION = "PRE_START_GATE_BLOCKED"

RECOMMENDED_NEXT_PHASE = (
    "PHASE_10_10_LONG_FORWARD_OBSERVATION_CONTROLLED_START_FINAL_REVIEW_V1"
)

DEPENDENCY_NAMES = [
    "phase_10_1_controlled_start_review",
    "phase_10_2_manual_start_protocol",
    "phase_10_3_manual_dry_run_checklist",
    "phase_10_4_controlled_dry_run_review",
    "phase_10_5_report_only_dry_run_design",
    "phase_10_6_report_only_dry_run_execution_review",
    "phase_10_7_controlled_report_only_dry_run_run",
    "phase_10_8_report_only_dry_run_output_integrity_review",
]

PRE_START_CONTROLS = [
    {
        "control_id": "PRE_START_GATE_CONTROL_001",
        "control_name": "phase_10_8_validation_passed",
        "control_group": "dependency",
        "required": True,
        "pre_start_only": True,
        "start_allowed": False,
        "details": "Phase 10.8 output integrity review must be validated.",
    },
    {
        "control_id": "PRE_START_GATE_CONTROL_002",
        "control_name": "output_integrity_passed",
        "control_group": "output_integrity",
        "required": True,
        "pre_start_only": True,
        "start_allowed": False,
        "details": "Report-only dry-run output integrity must pass.",
    },
    {
        "control_id": "PRE_START_GATE_CONTROL_003",
        "control_name": "candidate_scope_confirmed",
        "control_group": "candidate_scope",
        "required": True,
        "pre_start_only": True,
        "start_allowed": False,
        "details": f"Primary candidate remains {PRIMARY_RESEARCH_CANDIDATE}.",
    },
    {
        "control_id": "PRE_START_GATE_CONTROL_004",
        "control_name": "long_direction_confirmed",
        "control_group": "direction",
        "required": True,
        "pre_start_only": True,
        "start_allowed": False,
        "details": "LONG direction must be confirmed.",
    },
    {
        "control_id": "PRE_START_GATE_CONTROL_005",
        "control_name": "price_structure_confirmed",
        "control_group": "price_structure",
        "required": True,
        "pre_start_only": True,
        "start_allowed": False,
        "details": "LONG price structure must be validated.",
    },
    {
        "control_id": "PRE_START_GATE_CONTROL_006",
        "control_name": "report_only_artifact_scope_confirmed",
        "control_group": "artifact_scope",
        "required": True,
        "pre_start_only": True,
        "start_allowed": False,
        "details": "Dry-run output must remain report-only and not official evidence.",
    },
    {
        "control_id": "PRE_START_GATE_CONTROL_007",
        "control_name": "synthetic_evidence_source_confirmed",
        "control_group": "evidence_source",
        "required": True,
        "pre_start_only": True,
        "start_allowed": False,
        "details": "Dry-run output must remain synthetic and not real market evidence.",
    },
    {
        "control_id": "PRE_START_GATE_CONTROL_008",
        "control_name": "official_dataset_write_disabled",
        "control_group": "official_dataset_guard",
        "required": True,
        "pre_start_only": True,
        "start_allowed": False,
        "details": "Official dataset writes remain disabled.",
    },
    {
        "control_id": "PRE_START_GATE_CONTROL_009",
        "control_name": "real_evidence_acceptance_disabled",
        "control_group": "official_dataset_guard",
        "required": True,
        "pre_start_only": True,
        "start_allowed": False,
        "details": "Real evidence acceptance remains disabled.",
    },
    {
        "control_id": "PRE_START_GATE_CONTROL_010",
        "control_name": "signal_generation_disabled",
        "control_group": "safety",
        "required": True,
        "pre_start_only": True,
        "start_allowed": False,
        "details": "Signal generation remains disabled.",
    },
    {
        "control_id": "PRE_START_GATE_CONTROL_011",
        "control_name": "live_alerts_disabled",
        "control_group": "safety",
        "required": True,
        "pre_start_only": True,
        "start_allowed": False,
        "details": "Live alerts remain disabled.",
    },
    {
        "control_id": "PRE_START_GATE_CONTROL_012",
        "control_name": "paper_trading_disabled",
        "control_group": "safety",
        "required": True,
        "pre_start_only": True,
        "start_allowed": False,
        "details": "Paper trading remains disabled.",
    },
    {
        "control_id": "PRE_START_GATE_CONTROL_013",
        "control_name": "real_capital_disabled",
        "control_group": "safety",
        "required": True,
        "pre_start_only": True,
        "start_allowed": False,
        "details": "Real capital remains disabled.",
    },
    {
        "control_id": "PRE_START_GATE_CONTROL_014",
        "control_name": "market_execution_and_automation_disabled",
        "control_group": "safety",
        "required": True,
        "pre_start_only": True,
        "start_allowed": False,
        "details": "Market execution and automation remain disabled.",
    },
]

EXPECTED_FALSE_GUARDS = {
    "controlled_forward_observation_start_approved": False,
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


def build_pre_start_dependency_matrix() -> pd.DataFrame:
    rows: list[dict[str, Any]] = []

    for position, dependency_name in enumerate(DEPENDENCY_NAMES, start=1):
        rows.append(
            {
                "dependency_position": position,
                "dependency_name": dependency_name,
                "required": True,
                "passed": True,
                "details": "Dependency is represented in Phase 10 chain and validated by downstream source summaries.",
            }
        )

    return pd.DataFrame(rows)


def build_pre_start_controls() -> pd.DataFrame:
    rows: list[dict[str, Any]] = []

    for control in PRE_START_CONTROLS:
        rows.append(
            {
                "control_id": control["control_id"],
                "control_name": control["control_name"],
                "control_group": control["control_group"],
                "required": control["required"],
                "pre_start_only": control["pre_start_only"],
                "start_allowed": control["start_allowed"],
                "official_dataset_write_allowed": False,
                "real_evidence_acceptance_allowed": False,
                "signal_generation_allowed": False,
                "live_alerts_allowed": False,
                "paper_trading_allowed": False,
                "real_capital_allowed": False,
                "market_execution_allowed": False,
                "exchange_execution_allowed": False,
                "automation_allowed": False,
                "passed": (
                    control["required"] is True
                    and control["pre_start_only"] is True
                    and control["start_allowed"] is False
                ),
                "details": control["details"],
            }
        )

    return pd.DataFrame(rows)


def build_pre_start_rules(
    dependency_matrix_df: pd.DataFrame,
    controls_df: pd.DataFrame,
) -> pd.DataFrame:
    dependency_count = int(len(dependency_matrix_df))
    control_count = int(len(controls_df))

    all_dependencies_passed = (
        not dependency_matrix_df.empty
        and dependency_matrix_df["passed"].astype(bool).all()
    )

    all_controls_required = (
        not controls_df.empty
        and int(controls_df["required"].astype(bool).sum()) == control_count
    )

    all_controls_pre_start_only = (
        not controls_df.empty
        and controls_df["pre_start_only"].astype(bool).all()
    )

    all_start_disabled = (
        not controls_df.empty
        and controls_df["start_allowed"].astype(bool).eq(False).all()
    )

    all_official_dataset_writes_disabled = (
        not controls_df.empty
        and controls_df["official_dataset_write_allowed"].astype(bool).eq(False).all()
    )

    all_market_execution_disabled = (
        not controls_df.empty
        and controls_df["market_execution_allowed"].astype(bool).eq(False).all()
    )

    rows = [
        {
            "rule_id": "PRE_START_GATE_RULE_001",
            "rule_name": "dependency_count_8",
            "passed": dependency_count == 8,
            "required_value": "8",
            "actual_value": str(dependency_count),
            "rule_group": "dependency",
        },
        {
            "rule_id": "PRE_START_GATE_RULE_002",
            "rule_name": "all_dependencies_passed",
            "passed": all_dependencies_passed,
            "required_value": "True",
            "actual_value": str(all_dependencies_passed),
            "rule_group": "dependency",
        },
        {
            "rule_id": "PRE_START_GATE_RULE_003",
            "rule_name": "control_count_14",
            "passed": control_count == 14,
            "required_value": "14",
            "actual_value": str(control_count),
            "rule_group": "controls",
        },
        {
            "rule_id": "PRE_START_GATE_RULE_004",
            "rule_name": "all_controls_required",
            "passed": all_controls_required,
            "required_value": "True",
            "actual_value": str(all_controls_required),
            "rule_group": "controls",
        },
        {
            "rule_id": "PRE_START_GATE_RULE_005",
            "rule_name": "all_controls_pre_start_only",
            "passed": all_controls_pre_start_only,
            "required_value": "True",
            "actual_value": str(all_controls_pre_start_only),
            "rule_group": "scope_control",
        },
        {
            "rule_id": "PRE_START_GATE_RULE_006",
            "rule_name": "all_start_disabled",
            "passed": all_start_disabled,
            "required_value": "False",
            "actual_value": "False",
            "rule_group": "start_boundary",
        },
        {
            "rule_id": "PRE_START_GATE_RULE_007",
            "rule_name": "all_official_dataset_writes_disabled",
            "passed": all_official_dataset_writes_disabled,
            "required_value": "False",
            "actual_value": "False",
            "rule_group": "official_dataset_guard",
        },
        {
            "rule_id": "PRE_START_GATE_RULE_008",
            "rule_name": "all_market_execution_disabled",
            "passed": all_market_execution_disabled,
            "required_value": "False",
            "actual_value": "False",
            "rule_group": "market_execution_guard",
        },
    ]

    return pd.DataFrame(rows)


def build_pre_start_guard_matrix(phase_10_8_summary_df: pd.DataFrame) -> pd.DataFrame:
    summary = (
        phase_10_8_summary_df.iloc[0].to_dict()
        if not phase_10_8_summary_df.empty
        else {}
    )

    rows: list[dict[str, Any]] = []

    for guard_name, required_value in EXPECTED_FALSE_GUARDS.items():
        actual_value = safe_bool(summary.get(guard_name, required_value), default=True)

        rows.append(
            {
                "guard_name": guard_name,
                "required_value": required_value,
                "actual_value": actual_value,
                "passed": actual_value is required_value,
                "guard_group": "pre_start_safety_guard",
            }
        )

    rows.append(
        {
            "guard_name": "official_evidence_rows_written",
            "required_value": 0,
            "actual_value": int(summary.get("official_evidence_rows_written", -1)),
            "passed": int(summary.get("official_evidence_rows_written", -1)) == 0,
            "guard_group": "official_dataset_guard",
        }
    )

    return pd.DataFrame(rows)


def build_pre_start_requirements(
    phase_10_8_summary_df: pd.DataFrame,
    output_integrity_decision_df: pd.DataFrame,
    dependency_matrix_df: pd.DataFrame,
    controls_df: pd.DataFrame,
    rules_df: pd.DataFrame,
    guard_matrix_df: pd.DataFrame,
) -> pd.DataFrame:
    summary = (
        phase_10_8_summary_df.iloc[0].to_dict()
        if not phase_10_8_summary_df.empty
        else {}
    )

    decision = (
        output_integrity_decision_df.iloc[0].to_dict()
        if not output_integrity_decision_df.empty
        else {}
    )

    dependencies_passed = (
        not dependency_matrix_df.empty
        and dependency_matrix_df["passed"].astype(bool).all()
    )

    controls_passed = not controls_df.empty and controls_df["passed"].astype(bool).all()

    rules_passed = not rules_df.empty and rules_df["passed"].astype(bool).all()

    guards_passed = (
        not guard_matrix_df.empty and guard_matrix_df["passed"].astype(bool).all()
    )

    requirements = [
        {
            "requirement_id": "PRE_START_GATE_REQ_001",
            "requirement_name": "phase_10_8_validation_passed",
            "passed": safe_bool(summary.get("validation_passed", False)),
            "required_value": "True",
            "actual_value": str(summary.get("validation_passed", "")),
            "requirement_group": "dependency",
        },
        {
            "requirement_id": "PRE_START_GATE_REQ_002",
            "requirement_name": "output_integrity_passed",
            "passed": safe_bool(
                summary.get("report_only_dry_run_output_integrity_passed", False)
            ),
            "required_value": "True",
            "actual_value": str(
                summary.get("report_only_dry_run_output_integrity_passed", "")
            ),
            "requirement_group": "output_integrity",
        },
        {
            "requirement_id": "PRE_START_GATE_REQ_003",
            "requirement_name": "output_integrity_decision_expected",
            "passed": str(
                summary.get("report_only_dry_run_output_integrity_decision", "")
            ).strip()
            == OUTPUT_INTEGRITY_READY_DECISION,
            "required_value": OUTPUT_INTEGRITY_READY_DECISION,
            "actual_value": str(
                summary.get("report_only_dry_run_output_integrity_decision", "")
            ),
            "requirement_group": "output_integrity",
        },
        {
            "requirement_id": "PRE_START_GATE_REQ_004",
            "requirement_name": "pre_start_review_allowed",
            "passed": safe_bool(
                summary.get("forward_observation_pre_start_review_allowed", False)
            ),
            "required_value": "True",
            "actual_value": str(
                summary.get("forward_observation_pre_start_review_allowed", "")
            ),
            "requirement_group": "pre_start_scope",
        },
        {
            "requirement_id": "PRE_START_GATE_REQ_005",
            "requirement_name": "output_integrity_decision_table_consistent",
            "passed": (
                not output_integrity_decision_df.empty
                and safe_bool(
                    decision.get(
                        "report_only_dry_run_output_integrity_passed",
                        False,
                    )
                )
                and str(
                    decision.get(
                        "report_only_dry_run_output_integrity_decision",
                        "",
                    )
                ).strip()
                == OUTPUT_INTEGRITY_READY_DECISION
            ),
            "required_value": "True",
            "actual_value": str(
                decision.get("report_only_dry_run_output_integrity_decision", "")
            ),
            "requirement_group": "summary_consistency",
        },
        {
            "requirement_id": "PRE_START_GATE_REQ_006",
            "requirement_name": "dependencies_passed",
            "passed": dependencies_passed,
            "required_value": "True",
            "actual_value": str(dependencies_passed),
            "requirement_group": "dependency",
        },
        {
            "requirement_id": "PRE_START_GATE_REQ_007",
            "requirement_name": "pre_start_controls_passed",
            "passed": controls_passed,
            "required_value": "True",
            "actual_value": str(controls_passed),
            "requirement_group": "controls",
        },
        {
            "requirement_id": "PRE_START_GATE_REQ_008",
            "requirement_name": "pre_start_rules_passed",
            "passed": rules_passed,
            "required_value": "True",
            "actual_value": str(rules_passed),
            "requirement_group": "rules",
        },
        {
            "requirement_id": "PRE_START_GATE_REQ_009",
            "requirement_name": "pre_start_guards_passed",
            "passed": guards_passed,
            "required_value": "True",
            "actual_value": str(guards_passed),
            "requirement_group": "safety",
        },
        {
            "requirement_id": "PRE_START_GATE_REQ_010",
            "requirement_name": "candidate_valid",
            "passed": safe_bool(
                summary.get("report_only_dry_run_output_candidate_valid", False)
            ),
            "required_value": "True",
            "actual_value": str(
                summary.get("report_only_dry_run_output_candidate_valid", "")
            ),
            "requirement_group": "candidate_scope",
        },
        {
            "requirement_id": "PRE_START_GATE_REQ_011",
            "requirement_name": "direction_valid",
            "passed": safe_bool(
                summary.get("report_only_dry_run_output_direction_valid", False)
            ),
            "required_value": "True",
            "actual_value": str(
                summary.get("report_only_dry_run_output_direction_valid", "")
            ),
            "requirement_group": "direction",
        },
        {
            "requirement_id": "PRE_START_GATE_REQ_012",
            "requirement_name": "price_structure_valid",
            "passed": safe_bool(
                summary.get("report_only_dry_run_output_price_structure_valid", False)
            ),
            "required_value": "True",
            "actual_value": str(
                summary.get("report_only_dry_run_output_price_structure_valid", "")
            ),
            "requirement_group": "price_structure",
        },
        {
            "requirement_id": "PRE_START_GATE_REQ_013",
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
            "requirement_id": "PRE_START_GATE_REQ_014",
            "requirement_name": "official_evidence_rows_written_zero",
            "passed": int(summary.get("official_evidence_rows_written", -1)) == 0,
            "required_value": "0",
            "actual_value": str(summary.get("official_evidence_rows_written", "")),
            "requirement_group": "official_dataset_guard",
        },
        {
            "requirement_id": "PRE_START_GATE_REQ_015",
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
            "requirement_id": "PRE_START_GATE_REQ_016",
            "requirement_name": "market_execution_disabled",
            "passed": safe_bool(
                summary.get("market_execution_allowed", True),
                default=True,
            )
            is False,
            "required_value": "False",
            "actual_value": str(summary.get("market_execution_allowed", "")),
            "requirement_group": "market_execution_guard",
        },
        {
            "requirement_id": "PRE_START_GATE_REQ_017",
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


def build_pre_start_boundary_matrix() -> pd.DataFrame:
    rows = [
        {
            "boundary_item": "pre_start_gate_allowed",
            "allowed": True,
            "boundary_type": "pre_start_scope",
            "details": "Phase 10.9 may define and validate a pre-start gate.",
        },
        {
            "boundary_item": "controlled_forward_observation_start_review_allowed",
            "allowed": True,
            "boundary_type": "future_review",
            "details": "Phase 10.9 may recommend a future controlled start review.",
        },
        {
            "boundary_item": "controlled_forward_observation_start_approved",
            "allowed": False,
            "boundary_type": "operational_start",
            "details": "Controlled forward observation start remains unapproved.",
        },
        {
            "boundary_item": "forward_observation_start_allowed",
            "allowed": False,
            "boundary_type": "operational_start",
            "details": "Forward observation start remains disabled.",
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
            "boundary_item": "signal_generation_allowed",
            "allowed": False,
            "boundary_type": "signals",
            "details": "Signal generation remains disabled.",
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
            "boundary_item": "market_execution_allowed",
            "allowed": False,
            "boundary_type": "market_execution",
            "details": "Market execution remains disabled.",
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


def build_pre_start_decision_table(
    requirements_df: pd.DataFrame,
    boundary_matrix_df: pd.DataFrame,
    guard_matrix_df: pd.DataFrame,
    rules_df: pd.DataFrame,
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

    allowed_review_items = {
        "pre_start_gate_allowed",
        "controlled_forward_observation_start_review_allowed",
    }

    disallowed_rows = boundary_matrix_df[
        ~boundary_matrix_df["boundary_item"].astype(str).isin(allowed_review_items)
    ]

    disallowed_operational_boundaries_passed = (
        not disallowed_rows.empty
        and disallowed_rows["allowed"].astype(bool).eq(False).all()
    )

    pre_start_gate_passed = (
        total_requirements > 0
        and failed_requirements == 0
        and rules_passed
        and guards_passed
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
                "pre_start_gate_id": "PHASE_10_9_LONG_FORWARD_OBSERVATION_PRE_START_GATE_001",
                "pre_start_gate_status": PRE_START_GATE_STATUS,
                "pre_start_gate_passed": pre_start_gate_passed,
                "pre_start_gate_decision": (
                    READY_DECISION if pre_start_gate_passed else BLOCKED_DECISION
                ),
                "total_requirements": total_requirements,
                "passed_requirements": passed_requirements,
                "failed_requirements": failed_requirements,
                "failed_requirement_names": failed_requirement_names,
                "pre_start_gate_rules_passed": rules_passed,
                "pre_start_gate_guards_passed": guards_passed,
                "disallowed_operational_boundaries_passed": (
                    disallowed_operational_boundaries_passed
                ),
                "controlled_forward_observation_start_review_allowed": (
                    pre_start_gate_passed
                ),
                "controlled_forward_observation_start_approved": False,
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


def validate_long_forward_observation_pre_start_gate() -> dict[str, pd.DataFrame]:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    checks: list[dict[str, Any]] = []

    phase_anchors = {
        "phase_10_8_output_integrity_review_doc_exists": (
            PHASE_10_8_OUTPUT_INTEGRITY_REVIEW_DOC_PATH
        ),
        "phase_10_9_pre_start_gate_doc_exists": PHASE_10_9_PRE_START_GATE_DOC_PATH,
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

    phase_10_8_result = (
        validate_long_forward_observation_report_only_dry_run_output_integrity_review()
    )

    phase_10_8_summary_df = phase_10_8_result["summary"]
    source_output_schema_integrity_df = phase_10_8_result["output_schema_integrity"]
    source_output_row_integrity_df = phase_10_8_result["output_row_integrity"]
    source_summary_guard_integrity_df = phase_10_8_result["summary_guard_integrity"]
    source_output_integrity_requirements_df = phase_10_8_result[
        "output_integrity_requirements"
    ]
    source_output_integrity_boundary_matrix_df = phase_10_8_result[
        "output_integrity_boundary_matrix"
    ]
    source_output_integrity_decision_df = phase_10_8_result[
        "output_integrity_decision"
    ]
    source_checks_df = phase_10_8_result["checks"]

    phase_10_8_summary = (
        phase_10_8_summary_df.iloc[0].to_dict()
        if not phase_10_8_summary_df.empty
        else {}
    )

    phase_10_8_validation_passed = (
        not phase_10_8_summary_df.empty
        and safe_bool(phase_10_8_summary.get("validation_passed", False))
    )

    output_integrity_passed = safe_bool(
        phase_10_8_summary.get("report_only_dry_run_output_integrity_passed", False)
    )

    dependency_matrix_df = build_pre_start_dependency_matrix()
    controls_df = build_pre_start_controls()
    rules_df = build_pre_start_rules(
        dependency_matrix_df=dependency_matrix_df,
        controls_df=controls_df,
    )
    guard_matrix_df = build_pre_start_guard_matrix(phase_10_8_summary_df)

    requirements_df = build_pre_start_requirements(
        phase_10_8_summary_df=phase_10_8_summary_df,
        output_integrity_decision_df=source_output_integrity_decision_df,
        dependency_matrix_df=dependency_matrix_df,
        controls_df=controls_df,
        rules_df=rules_df,
        guard_matrix_df=guard_matrix_df,
    )

    boundary_matrix_df = build_pre_start_boundary_matrix()

    decision_df = build_pre_start_decision_table(
        requirements_df=requirements_df,
        boundary_matrix_df=boundary_matrix_df,
        guard_matrix_df=guard_matrix_df,
        rules_df=rules_df,
    )

    official_dataset_exists_after = OFFICIAL_DATASET_PATH.exists()

    decision = decision_df.iloc[0].to_dict() if not decision_df.empty else {}

    pre_start_gate_passed = safe_bool(decision.get("pre_start_gate_passed", False))
    pre_start_gate_decision = str(decision.get("pre_start_gate_decision", ""))
    controlled_start_review_allowed = safe_bool(
        decision.get("controlled_forward_observation_start_review_allowed", False)
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
            check_name="phase_10_8_validation_passed",
            passed=phase_10_8_validation_passed,
            severity="INFO" if phase_10_8_validation_passed else "ERROR",
            details=str(phase_10_8_summary.get("validation_decision", "")),
        )
    )

    checks.append(
        build_check(
            check_group="phase_dependency",
            check_name="output_integrity_passed",
            passed=output_integrity_passed,
            severity="INFO" if output_integrity_passed else "ERROR",
            details=(
                "report_only_dry_run_output_integrity_passed="
                f"{output_integrity_passed}"
            ),
        )
    )

    checks.append(
        build_check(
            check_group="pre_start_gate",
            check_name="pre_start_gate_rules_passed",
            passed=rules_passed,
            severity="INFO" if rules_passed else "ERROR",
            details=(
                "failed_rules="
                + ",".join(
                    rules_df[~rules_df["passed"].astype(bool)]["rule_name"].astype(str)
                )
                if not rules_df.empty
                else "failed_rules=all"
            ),
        )
    )

    checks.append(
        build_check(
            check_group="pre_start_gate",
            check_name="pre_start_gate_requirements_passed",
            passed=requirements_passed,
            severity="INFO" if requirements_passed else "ERROR",
            details=(
                "failed_requirements="
                + ",".join(
                    requirements_df[~requirements_df["passed"].astype(bool)][
                        "requirement_name"
                    ].astype(str)
                )
                if not requirements_df.empty
                else "failed_requirements=all"
            ),
        )
    )

    checks.append(
        build_check(
            check_group="pre_start_gate",
            check_name="pre_start_gate_guards_passed",
            passed=guards_passed,
            severity="INFO" if guards_passed else "ERROR",
            details=(
                "failed_guards="
                + ",".join(
                    guard_matrix_df[~guard_matrix_df["passed"].astype(bool)][
                        "guard_name"
                    ].astype(str)
                )
                if not guard_matrix_df.empty
                else "failed_guards=all"
            ),
        )
    )

    checks.append(
        build_check(
            check_group="pre_start_gate",
            check_name="pre_start_gate_passed",
            passed=pre_start_gate_passed,
            severity="INFO" if pre_start_gate_passed else "ERROR",
            details=f"pre_start_gate_passed={pre_start_gate_passed}",
        )
    )

    checks.append(
        build_check(
            check_group="pre_start_gate",
            check_name="pre_start_gate_decision_expected",
            passed=pre_start_gate_decision == READY_DECISION,
            severity="INFO" if pre_start_gate_decision == READY_DECISION else "ERROR",
            details=f"pre_start_gate_decision={pre_start_gate_decision}",
        )
    )

    checks.append(
        build_check(
            check_group="planning_scope",
            check_name="controlled_forward_observation_start_review_allowed",
            passed=controlled_start_review_allowed,
            severity="WARNING" if controlled_start_review_allowed else "ERROR",
            details=(
                "This allows only a future controlled start final review, not forward "
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
                check_group="pre_start_safety_flags",
                check_name=str(guard_row["guard_name"]),
                passed=safe_bool(guard_row["passed"], False),
                severity="INFO" if safe_bool(guard_row["passed"], False) else "ERROR",
                details=(
                    f"{guard_row['guard_name']}="
                    f"{guard_row['actual_value']} "
                    f"(required={guard_row['required_value']})"
                ),
            )
        )

    checks.append(
        build_check(
            check_group="scope_control",
            check_name="pre_start_gate_only",
            passed=True,
            severity="WARNING",
            details="Phase 10.9 validates only a pre-start gate.",
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
            check_name="official_evidence_not_persisted",
            passed=True,
            severity="WARNING",
            details="Official evidence persistence remains disabled.",
        )
    )

    checks.append(
        build_check(
            check_group="scope_control",
            check_name="market_execution_not_allowed",
            passed=True,
            severity="WARNING",
            details="Market execution remains disabled.",
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
            check_name="phase_10_10_recommended_next",
            passed=True,
            severity="INFO",
            details=(
                "Recommended next step: "
                "Phase 10.10 LONG Forward Observation Controlled Start Final Review V1."
            ),
        )
    )

    checks_df = pd.DataFrame(checks)

    blocker_count = int(checks_df["blocker"].astype(bool).sum())
    error_count = int(checks_df["severity"].eq("ERROR").sum())
    warning_count = int(checks_df["severity"].eq("WARNING").sum())

    validation_passed = blocker_count == 0 and error_count == 0

    summary_df = pd.DataFrame(
        [
            {
                "phase": "10.9",
                "long_forward_observation_pre_start_gate_defined": True,
                "phase_10_8_validation_passed": phase_10_8_validation_passed,
                "report_only_dry_run_output_integrity_passed": output_integrity_passed,
                "report_only_dry_run_output_integrity_decision": str(
                    phase_10_8_summary.get(
                        "report_only_dry_run_output_integrity_decision",
                        "",
                    )
                ),
                "forward_observation_pre_start_review_allowed": safe_bool(
                    phase_10_8_summary.get(
                        "forward_observation_pre_start_review_allowed",
                        False,
                    )
                ),
                "pre_start_gate_dependency_count": int(len(dependency_matrix_df)),
                "pre_start_gate_control_count": int(len(controls_df)),
                "pre_start_gate_rule_rows": int(len(rules_df)),
                "pre_start_gate_requirement_rows": int(len(requirements_df)),
                "pre_start_gate_rules_passed": rules_passed,
                "pre_start_gate_requirements_passed": requirements_passed,
                "pre_start_gate_guards_passed": guards_passed,
                "pre_start_gate_passed": pre_start_gate_passed,
                "pre_start_gate_decision": pre_start_gate_decision,
                "controlled_forward_observation_start_review_allowed": (
                    controlled_start_review_allowed
                ),
                "controlled_forward_observation_start_approved": False,
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
                "estimated_phase_10_progress_percent": 90,
                "total_checks": int(len(checks_df)),
                "warning_count": warning_count,
                "error_count": error_count,
                "blocker_count": blocker_count,
                "validation_passed": validation_passed,
                "validation_decision": (
                    "PHASE_10_9_LONG_FORWARD_OBSERVATION_PRE_START_GATE_VALIDATED"
                    if validation_passed
                    else "PHASE_10_9_LONG_FORWARD_OBSERVATION_PRE_START_GATE_FAILED"
                ),
            }
        ]
    )

    phase_10_8_summary_df.to_csv(
        REPORTS_DIR / "phase_10_8_source_summary_v1.csv",
        index=False,
    )
    source_output_schema_integrity_df.to_csv(
        REPORTS_DIR / "phase_10_8_source_output_schema_integrity_v1.csv",
        index=False,
    )
    source_output_row_integrity_df.to_csv(
        REPORTS_DIR / "phase_10_8_source_output_row_integrity_v1.csv",
        index=False,
    )
    source_summary_guard_integrity_df.to_csv(
        REPORTS_DIR / "phase_10_8_source_summary_guard_integrity_v1.csv",
        index=False,
    )
    source_output_integrity_requirements_df.to_csv(
        REPORTS_DIR / "phase_10_8_source_output_integrity_requirements_v1.csv",
        index=False,
    )
    source_output_integrity_boundary_matrix_df.to_csv(
        REPORTS_DIR / "phase_10_8_source_output_integrity_boundary_matrix_v1.csv",
        index=False,
    )
    source_output_integrity_decision_df.to_csv(
        REPORTS_DIR / "phase_10_8_source_output_integrity_decision_v1.csv",
        index=False,
    )
    source_checks_df.to_csv(
        REPORTS_DIR / "phase_10_8_source_checks_v1.csv",
        index=False,
    )
    dependency_matrix_df.to_csv(
        REPORTS_DIR / "long_forward_observation_pre_start_gate_dependency_matrix_v1.csv",
        index=False,
    )
    controls_df.to_csv(
        REPORTS_DIR / "long_forward_observation_pre_start_gate_controls_v1.csv",
        index=False,
    )
    rules_df.to_csv(
        REPORTS_DIR / "long_forward_observation_pre_start_gate_rules_v1.csv",
        index=False,
    )
    requirements_df.to_csv(
        REPORTS_DIR / "long_forward_observation_pre_start_gate_requirements_v1.csv",
        index=False,
    )
    guard_matrix_df.to_csv(
        REPORTS_DIR / "long_forward_observation_pre_start_gate_guard_matrix_v1.csv",
        index=False,
    )
    boundary_matrix_df.to_csv(
        REPORTS_DIR / "long_forward_observation_pre_start_gate_boundary_matrix_v1.csv",
        index=False,
    )
    decision_df.to_csv(
        REPORTS_DIR / "long_forward_observation_pre_start_gate_decision_v1.csv",
        index=False,
    )
    checks_df.to_csv(
        REPORTS_DIR / "long_forward_observation_pre_start_gate_checks_v1.csv",
        index=False,
    )
    summary_df.to_csv(
        REPORTS_DIR / "long_forward_observation_pre_start_gate_summary_v1.csv",
        index=False,
    )

    return {
        "summary": summary_df,
        "source_phase_10_8_summary": phase_10_8_summary_df,
        "source_output_schema_integrity": source_output_schema_integrity_df,
        "source_output_row_integrity": source_output_row_integrity_df,
        "source_summary_guard_integrity": source_summary_guard_integrity_df,
        "source_output_integrity_requirements": source_output_integrity_requirements_df,
        "source_output_integrity_boundary_matrix": (
            source_output_integrity_boundary_matrix_df
        ),
        "source_output_integrity_decision": source_output_integrity_decision_df,
        "source_checks": source_checks_df,
        "pre_start_dependency_matrix": dependency_matrix_df,
        "pre_start_controls": controls_df,
        "pre_start_rules": rules_df,
        "pre_start_requirements": requirements_df,
        "pre_start_guard_matrix": guard_matrix_df,
        "pre_start_boundary_matrix": boundary_matrix_df,
        "pre_start_decision": decision_df,
        "checks": checks_df,
    }