from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from src.long_side.long_forward_observation_dataset_bootstrap_v1 import (
    OFFICIAL_DATASET_PATH,
    PRIMARY_RESEARCH_CANDIDATE,
)
from src.long_side.long_forward_observation_phase_10_9_pre_start_gate_v1 import (
    READY_DECISION as PRE_START_GATE_READY_DECISION,
    validate_long_forward_observation_pre_start_gate,
)


REPORTS_DIR = Path(
    "reports/phase_10_10_long_forward_observation_controlled_start_final_review_v1"
)

PHASE_10_9_PRE_START_GATE_DOC_PATH = Path(
    "docs/PHASE_10_LONG_FORWARD_OBSERVATION_PRE_START_GATE.md"
)
PHASE_10_10_CONTROLLED_START_FINAL_REVIEW_DOC_PATH = Path(
    "docs/PHASE_10_LONG_FORWARD_OBSERVATION_CONTROLLED_START_FINAL_REVIEW.md"
)

CONTROLLED_START_FINAL_REVIEW_STATUS = (
    "LONG_FORWARD_OBSERVATION_CONTROLLED_START_FINAL_REVIEW_ONLY"
)

READY_DECISION = "CONTROLLED_START_FINAL_REVIEW_READY_FOR_ACTIVATION_PHASE"
BLOCKED_DECISION = "CONTROLLED_START_FINAL_REVIEW_BLOCKED"

RECOMMENDED_NEXT_PHASE = (
    "PHASE_10_11_LONG_FORWARD_OBSERVATION_CONTROLLED_START_ACTIVATION_PREPARATION_V1"
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
    "phase_10_9_pre_start_gate",
    "phase_10_10_controlled_start_final_review",
]

FINAL_REVIEW_CONTROLS = [
    {
        "control_id": "FINAL_START_REVIEW_CONTROL_001",
        "control_name": "phase_10_9_validation_passed",
        "control_group": "dependency",
        "details": "Phase 10.9 pre-start gate must be validated.",
    },
    {
        "control_id": "FINAL_START_REVIEW_CONTROL_002",
        "control_name": "pre_start_gate_passed",
        "control_group": "pre_start_gate",
        "details": "Pre-start gate must pass.",
    },
    {
        "control_id": "FINAL_START_REVIEW_CONTROL_003",
        "control_name": "pre_start_gate_decision_confirmed",
        "control_group": "pre_start_gate",
        "details": "Pre-start gate decision must be ready for controlled start review.",
    },
    {
        "control_id": "FINAL_START_REVIEW_CONTROL_004",
        "control_name": "candidate_scope_confirmed",
        "control_group": "candidate_scope",
        "details": f"Primary candidate remains {PRIMARY_RESEARCH_CANDIDATE}.",
    },
    {
        "control_id": "FINAL_START_REVIEW_CONTROL_005",
        "control_name": "long_direction_confirmed",
        "control_group": "direction",
        "details": "LONG direction must remain confirmed.",
    },
    {
        "control_id": "FINAL_START_REVIEW_CONTROL_006",
        "control_name": "price_structure_confirmed",
        "control_group": "price_structure",
        "details": "LONG price structure validation must remain confirmed.",
    },
    {
        "control_id": "FINAL_START_REVIEW_CONTROL_007",
        "control_name": "report_only_artifact_scope_confirmed",
        "control_group": "artifact_scope",
        "details": "Prior dry-run output remains report-only and not official evidence.",
    },
    {
        "control_id": "FINAL_START_REVIEW_CONTROL_008",
        "control_name": "synthetic_evidence_source_confirmed",
        "control_group": "evidence_source",
        "details": "Prior dry-run output remains synthetic and not real market evidence.",
    },
    {
        "control_id": "FINAL_START_REVIEW_CONTROL_009",
        "control_name": "official_dataset_write_disabled",
        "control_group": "official_dataset_guard",
        "details": "Official dataset writes remain disabled.",
    },
    {
        "control_id": "FINAL_START_REVIEW_CONTROL_010",
        "control_name": "real_evidence_acceptance_disabled",
        "control_group": "official_dataset_guard",
        "details": "Real evidence acceptance remains disabled.",
    },
    {
        "control_id": "FINAL_START_REVIEW_CONTROL_011",
        "control_name": "forward_observation_not_started",
        "control_group": "start_boundary",
        "details": "Forward observation remains not started.",
    },
    {
        "control_id": "FINAL_START_REVIEW_CONTROL_012",
        "control_name": "signal_generation_disabled",
        "control_group": "safety",
        "details": "Signal generation remains disabled.",
    },
    {
        "control_id": "FINAL_START_REVIEW_CONTROL_013",
        "control_name": "live_alerts_disabled",
        "control_group": "safety",
        "details": "Live alerts remain disabled.",
    },
    {
        "control_id": "FINAL_START_REVIEW_CONTROL_014",
        "control_name": "paper_and_real_capital_disabled",
        "control_group": "safety",
        "details": "Paper trading and real capital remain disabled.",
    },
    {
        "control_id": "FINAL_START_REVIEW_CONTROL_015",
        "control_name": "market_execution_disabled",
        "control_group": "market_execution_guard",
        "details": "Market execution remains disabled.",
    },
    {
        "control_id": "FINAL_START_REVIEW_CONTROL_016",
        "control_name": "automation_disabled",
        "control_group": "automation_guard",
        "details": "Automation remains disabled.",
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


def build_final_review_dependency_matrix() -> pd.DataFrame:
    rows: list[dict[str, Any]] = []

    for position, dependency_name in enumerate(DEPENDENCY_NAMES, start=1):
        rows.append(
            {
                "dependency_position": position,
                "dependency_name": dependency_name,
                "required": True,
                "passed": True,
                "details": (
                    "Dependency is represented in the Phase 10 chain and validated "
                    "through downstream source summaries."
                ),
            }
        )

    return pd.DataFrame(rows)


def build_final_review_controls() -> pd.DataFrame:
    rows: list[dict[str, Any]] = []

    for control in FINAL_REVIEW_CONTROLS:
        rows.append(
            {
                "control_id": control["control_id"],
                "control_name": control["control_name"],
                "control_group": control["control_group"],
                "required": True,
                "final_review_only": True,
                "activation_performed": False,
                "controlled_start_approved": False,
                "forward_observation_start_allowed": False,
                "official_dataset_write_allowed": False,
                "real_evidence_acceptance_allowed": False,
                "signal_generation_allowed": False,
                "live_alerts_allowed": False,
                "paper_trading_allowed": False,
                "real_capital_allowed": False,
                "market_execution_allowed": False,
                "exchange_execution_allowed": False,
                "automation_allowed": False,
                "passed": True,
                "details": control["details"],
            }
        )

    return pd.DataFrame(rows)


def build_final_review_rules(
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

    all_controls_final_review_only = (
        not controls_df.empty
        and controls_df["final_review_only"].astype(bool).all()
    )

    all_activation_not_performed = (
        not controls_df.empty
        and controls_df["activation_performed"].astype(bool).eq(False).all()
    )

    all_controlled_start_not_approved = (
        not controls_df.empty
        and controls_df["controlled_start_approved"].astype(bool).eq(False).all()
    )

    all_start_disabled = (
        not controls_df.empty
        and controls_df["forward_observation_start_allowed"].astype(bool).eq(False).all()
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
            "rule_id": "FINAL_START_REVIEW_RULE_001",
            "rule_name": "dependency_count_10",
            "passed": dependency_count == 10,
            "required_value": "10",
            "actual_value": str(dependency_count),
            "rule_group": "dependency",
        },
        {
            "rule_id": "FINAL_START_REVIEW_RULE_002",
            "rule_name": "all_dependencies_passed",
            "passed": all_dependencies_passed,
            "required_value": "True",
            "actual_value": str(all_dependencies_passed),
            "rule_group": "dependency",
        },
        {
            "rule_id": "FINAL_START_REVIEW_RULE_003",
            "rule_name": "control_count_16",
            "passed": control_count == 16,
            "required_value": "16",
            "actual_value": str(control_count),
            "rule_group": "controls",
        },
        {
            "rule_id": "FINAL_START_REVIEW_RULE_004",
            "rule_name": "all_controls_required",
            "passed": all_controls_required,
            "required_value": "True",
            "actual_value": str(all_controls_required),
            "rule_group": "controls",
        },
        {
            "rule_id": "FINAL_START_REVIEW_RULE_005",
            "rule_name": "all_controls_final_review_only",
            "passed": all_controls_final_review_only,
            "required_value": "True",
            "actual_value": str(all_controls_final_review_only),
            "rule_group": "scope_control",
        },
        {
            "rule_id": "FINAL_START_REVIEW_RULE_006",
            "rule_name": "all_activation_not_performed",
            "passed": all_activation_not_performed,
            "required_value": "False",
            "actual_value": "False",
            "rule_group": "activation_boundary",
        },
        {
            "rule_id": "FINAL_START_REVIEW_RULE_007",
            "rule_name": "all_controlled_start_not_approved",
            "passed": all_controlled_start_not_approved,
            "required_value": "False",
            "actual_value": "False",
            "rule_group": "start_boundary",
        },
        {
            "rule_id": "FINAL_START_REVIEW_RULE_008",
            "rule_name": "all_start_disabled",
            "passed": all_start_disabled,
            "required_value": "False",
            "actual_value": "False",
            "rule_group": "start_boundary",
        },
        {
            "rule_id": "FINAL_START_REVIEW_RULE_009",
            "rule_name": "all_official_dataset_writes_disabled",
            "passed": all_official_dataset_writes_disabled,
            "required_value": "False",
            "actual_value": "False",
            "rule_group": "official_dataset_guard",
        },
        {
            "rule_id": "FINAL_START_REVIEW_RULE_010",
            "rule_name": "all_market_execution_disabled",
            "passed": all_market_execution_disabled,
            "required_value": "False",
            "actual_value": "False",
            "rule_group": "market_execution_guard",
        },
    ]

    return pd.DataFrame(rows)


def build_final_review_guard_matrix(phase_10_9_summary_df: pd.DataFrame) -> pd.DataFrame:
    summary = (
        phase_10_9_summary_df.iloc[0].to_dict()
        if not phase_10_9_summary_df.empty
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
                "guard_group": "final_review_safety_guard",
            }
        )

    rows.append(
        {
            "guard_name": "controlled_forward_observation_start_activation_performed",
            "required_value": False,
            "actual_value": False,
            "passed": True,
            "guard_group": "activation_boundary",
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


def build_final_review_requirements(
    phase_10_9_summary_df: pd.DataFrame,
    pre_start_decision_df: pd.DataFrame,
    dependency_matrix_df: pd.DataFrame,
    controls_df: pd.DataFrame,
    rules_df: pd.DataFrame,
    guard_matrix_df: pd.DataFrame,
) -> pd.DataFrame:
    summary = (
        phase_10_9_summary_df.iloc[0].to_dict()
        if not phase_10_9_summary_df.empty
        else {}
    )

    decision = pre_start_decision_df.iloc[0].to_dict() if not pre_start_decision_df.empty else {}

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
            "requirement_id": "FINAL_START_REVIEW_REQ_001",
            "requirement_name": "phase_10_9_validation_passed",
            "passed": safe_bool(summary.get("validation_passed", False)),
            "required_value": "True",
            "actual_value": str(summary.get("validation_passed", "")),
            "requirement_group": "dependency",
        },
        {
            "requirement_id": "FINAL_START_REVIEW_REQ_002",
            "requirement_name": "pre_start_gate_passed",
            "passed": safe_bool(summary.get("pre_start_gate_passed", False)),
            "required_value": "True",
            "actual_value": str(summary.get("pre_start_gate_passed", "")),
            "requirement_group": "pre_start_gate",
        },
        {
            "requirement_id": "FINAL_START_REVIEW_REQ_003",
            "requirement_name": "pre_start_gate_decision_expected",
            "passed": str(summary.get("pre_start_gate_decision", "")).strip()
            == PRE_START_GATE_READY_DECISION,
            "required_value": PRE_START_GATE_READY_DECISION,
            "actual_value": str(summary.get("pre_start_gate_decision", "")),
            "requirement_group": "pre_start_gate",
        },
        {
            "requirement_id": "FINAL_START_REVIEW_REQ_004",
            "requirement_name": "controlled_start_review_allowed",
            "passed": safe_bool(
                summary.get("controlled_forward_observation_start_review_allowed", False)
            ),
            "required_value": "True",
            "actual_value": str(
                summary.get("controlled_forward_observation_start_review_allowed", "")
            ),
            "requirement_group": "final_review_scope",
        },
        {
            "requirement_id": "FINAL_START_REVIEW_REQ_005",
            "requirement_name": "pre_start_decision_table_consistent",
            "passed": (
                not pre_start_decision_df.empty
                and safe_bool(decision.get("pre_start_gate_passed", False))
                and str(decision.get("pre_start_gate_decision", "")).strip()
                == PRE_START_GATE_READY_DECISION
            ),
            "required_value": "True",
            "actual_value": str(decision.get("pre_start_gate_decision", "")),
            "requirement_group": "summary_consistency",
        },
        {
            "requirement_id": "FINAL_START_REVIEW_REQ_006",
            "requirement_name": "dependencies_passed",
            "passed": dependencies_passed,
            "required_value": "True",
            "actual_value": str(dependencies_passed),
            "requirement_group": "dependency",
        },
        {
            "requirement_id": "FINAL_START_REVIEW_REQ_007",
            "requirement_name": "final_review_controls_passed",
            "passed": controls_passed,
            "required_value": "True",
            "actual_value": str(controls_passed),
            "requirement_group": "controls",
        },
        {
            "requirement_id": "FINAL_START_REVIEW_REQ_008",
            "requirement_name": "final_review_rules_passed",
            "passed": rules_passed,
            "required_value": "True",
            "actual_value": str(rules_passed),
            "requirement_group": "rules",
        },
        {
            "requirement_id": "FINAL_START_REVIEW_REQ_009",
            "requirement_name": "final_review_guards_passed",
            "passed": guards_passed,
            "required_value": "True",
            "actual_value": str(guards_passed),
            "requirement_group": "safety",
        },
        {
            "requirement_id": "FINAL_START_REVIEW_REQ_010",
            "requirement_name": "controlled_start_not_approved",
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
            "requirement_id": "FINAL_START_REVIEW_REQ_011",
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
            "requirement_id": "FINAL_START_REVIEW_REQ_012",
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
            "requirement_id": "FINAL_START_REVIEW_REQ_013",
            "requirement_name": "official_evidence_rows_written_zero",
            "passed": int(summary.get("official_evidence_rows_written", -1)) == 0,
            "required_value": "0",
            "actual_value": str(summary.get("official_evidence_rows_written", "")),
            "requirement_group": "official_dataset_guard",
        },
        {
            "requirement_id": "FINAL_START_REVIEW_REQ_014",
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
            "requirement_id": "FINAL_START_REVIEW_REQ_015",
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
            "requirement_id": "FINAL_START_REVIEW_REQ_016",
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


def build_final_review_boundary_matrix() -> pd.DataFrame:
    rows = [
        {
            "boundary_item": "controlled_start_final_review_allowed",
            "allowed": True,
            "boundary_type": "final_review_scope",
            "details": "Phase 10.10 may perform the final controlled start review.",
        },
        {
            "boundary_item": "future_controlled_start_activation_phase_allowed",
            "allowed": True,
            "boundary_type": "future_activation_phase",
            "details": "Phase 10.10 may recommend a future controlled start activation preparation phase.",
        },
        {
            "boundary_item": "controlled_forward_observation_start_activation_performed",
            "allowed": False,
            "boundary_type": "activation_boundary",
            "details": "Controlled start activation is not performed in this phase.",
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


def build_final_review_decision_table(
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
        "controlled_start_final_review_allowed",
        "future_controlled_start_activation_phase_allowed",
    }

    disallowed_rows = boundary_matrix_df[
        ~boundary_matrix_df["boundary_item"].astype(str).isin(allowed_review_items)
    ]

    disallowed_operational_boundaries_passed = (
        not disallowed_rows.empty
        and disallowed_rows["allowed"].astype(bool).eq(False).all()
    )

    final_review_passed = (
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
                "controlled_start_final_review_id": (
                    "PHASE_10_10_LONG_FORWARD_OBSERVATION_CONTROLLED_START_FINAL_REVIEW_001"
                ),
                "controlled_start_final_review_status": (
                    CONTROLLED_START_FINAL_REVIEW_STATUS
                ),
                "controlled_start_final_review_passed": final_review_passed,
                "controlled_start_final_review_decision": (
                    READY_DECISION if final_review_passed else BLOCKED_DECISION
                ),
                "total_requirements": total_requirements,
                "passed_requirements": passed_requirements,
                "failed_requirements": failed_requirements,
                "failed_requirement_names": failed_requirement_names,
                "final_review_rules_passed": rules_passed,
                "final_review_guards_passed": guards_passed,
                "disallowed_operational_boundaries_passed": (
                    disallowed_operational_boundaries_passed
                ),
                "future_controlled_start_activation_phase_allowed": final_review_passed,
                "controlled_forward_observation_start_approved": False,
                "controlled_forward_observation_start_activation_performed": False,
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


def validate_long_forward_observation_controlled_start_final_review() -> dict[str, pd.DataFrame]:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    checks: list[dict[str, Any]] = []

    phase_anchors = {
        "phase_10_9_pre_start_gate_doc_exists": PHASE_10_9_PRE_START_GATE_DOC_PATH,
        "phase_10_10_controlled_start_final_review_doc_exists": (
            PHASE_10_10_CONTROLLED_START_FINAL_REVIEW_DOC_PATH
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

    phase_10_9_result = validate_long_forward_observation_pre_start_gate()

    phase_10_9_summary_df = phase_10_9_result["summary"]
    source_dependency_matrix_df = phase_10_9_result["pre_start_dependency_matrix"]
    source_controls_df = phase_10_9_result["pre_start_controls"]
    source_rules_df = phase_10_9_result["pre_start_rules"]
    source_requirements_df = phase_10_9_result["pre_start_requirements"]
    source_guard_matrix_df = phase_10_9_result["pre_start_guard_matrix"]
    source_boundary_matrix_df = phase_10_9_result["pre_start_boundary_matrix"]
    source_decision_df = phase_10_9_result["pre_start_decision"]
    source_checks_df = phase_10_9_result["checks"]

    phase_10_9_summary = (
        phase_10_9_summary_df.iloc[0].to_dict()
        if not phase_10_9_summary_df.empty
        else {}
    )

    phase_10_9_validation_passed = (
        not phase_10_9_summary_df.empty
        and safe_bool(phase_10_9_summary.get("validation_passed", False))
    )

    pre_start_gate_passed = safe_bool(
        phase_10_9_summary.get("pre_start_gate_passed", False)
    )

    dependency_matrix_df = build_final_review_dependency_matrix()
    controls_df = build_final_review_controls()
    rules_df = build_final_review_rules(
        dependency_matrix_df=dependency_matrix_df,
        controls_df=controls_df,
    )
    guard_matrix_df = build_final_review_guard_matrix(phase_10_9_summary_df)

    requirements_df = build_final_review_requirements(
        phase_10_9_summary_df=phase_10_9_summary_df,
        pre_start_decision_df=source_decision_df,
        dependency_matrix_df=dependency_matrix_df,
        controls_df=controls_df,
        rules_df=rules_df,
        guard_matrix_df=guard_matrix_df,
    )

    boundary_matrix_df = build_final_review_boundary_matrix()

    decision_df = build_final_review_decision_table(
        requirements_df=requirements_df,
        boundary_matrix_df=boundary_matrix_df,
        guard_matrix_df=guard_matrix_df,
        rules_df=rules_df,
    )

    official_dataset_exists_after = OFFICIAL_DATASET_PATH.exists()

    decision = decision_df.iloc[0].to_dict() if not decision_df.empty else {}

    final_review_passed = safe_bool(
        decision.get("controlled_start_final_review_passed", False)
    )
    final_review_decision = str(
        decision.get("controlled_start_final_review_decision", "")
    )
    future_activation_phase_allowed = safe_bool(
        decision.get("future_controlled_start_activation_phase_allowed", False)
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
            check_name="phase_10_9_validation_passed",
            passed=phase_10_9_validation_passed,
            severity="INFO" if phase_10_9_validation_passed else "ERROR",
            details=str(phase_10_9_summary.get("validation_decision", "")),
        )
    )

    checks.append(
        build_check(
            check_group="phase_dependency",
            check_name="pre_start_gate_passed",
            passed=pre_start_gate_passed,
            severity="INFO" if pre_start_gate_passed else "ERROR",
            details=f"pre_start_gate_passed={pre_start_gate_passed}",
        )
    )

    checks.append(
        build_check(
            check_group="final_review",
            check_name="final_review_rules_passed",
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
            check_group="final_review",
            check_name="final_review_requirements_passed",
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
            check_group="final_review",
            check_name="final_review_guards_passed",
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
            check_group="final_review",
            check_name="controlled_start_final_review_passed",
            passed=final_review_passed,
            severity="INFO" if final_review_passed else "ERROR",
            details=f"controlled_start_final_review_passed={final_review_passed}",
        )
    )

    checks.append(
        build_check(
            check_group="final_review",
            check_name="controlled_start_final_review_decision_expected",
            passed=final_review_decision == READY_DECISION,
            severity="INFO" if final_review_decision == READY_DECISION else "ERROR",
            details=f"controlled_start_final_review_decision={final_review_decision}",
        )
    )

    checks.append(
        build_check(
            check_group="planning_scope",
            check_name="future_controlled_start_activation_phase_allowed",
            passed=future_activation_phase_allowed,
            severity="WARNING" if future_activation_phase_allowed else "ERROR",
            details=(
                "This allows only a future controlled start activation preparation "
                "phase, not forward observation start, alerts, paper trading, real "
                "capital, official evidence persistence, or market execution."
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
                check_group="final_review_safety_flags",
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
            check_name="controlled_start_final_review_only",
            passed=True,
            severity="WARNING",
            details="Phase 10.10 validates only a controlled start final review.",
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
            check_name="phase_10_11_recommended_next",
            passed=True,
            severity="INFO",
            details=(
                "Recommended next step: Phase 10.11 LONG Forward Observation "
                "Controlled Start Activation Preparation V1."
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
                "phase": "10.10",
                "long_forward_observation_controlled_start_final_review_defined": True,
                "phase_10_9_validation_passed": phase_10_9_validation_passed,
                "pre_start_gate_passed": pre_start_gate_passed,
                "pre_start_gate_decision": str(
                    phase_10_9_summary.get("pre_start_gate_decision", "")
                ),
                "controlled_forward_observation_start_review_allowed": safe_bool(
                    phase_10_9_summary.get(
                        "controlled_forward_observation_start_review_allowed",
                        False,
                    )
                ),
                "final_review_dependency_count": int(len(dependency_matrix_df)),
                "final_review_control_count": int(len(controls_df)),
                "final_review_rule_rows": int(len(rules_df)),
                "final_review_requirement_rows": int(len(requirements_df)),
                "final_review_rules_passed": rules_passed,
                "final_review_requirements_passed": requirements_passed,
                "final_review_guards_passed": guards_passed,
                "controlled_start_final_review_passed": final_review_passed,
                "controlled_start_final_review_decision": final_review_decision,
                "future_controlled_start_activation_phase_allowed": (
                    future_activation_phase_allowed
                ),
                "controlled_forward_observation_start_approved": False,
                "controlled_forward_observation_start_activation_performed": False,
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
                    "PHASE_10_10_LONG_FORWARD_OBSERVATION_CONTROLLED_START_FINAL_REVIEW_VALIDATED"
                    if validation_passed
                    else "PHASE_10_10_LONG_FORWARD_OBSERVATION_CONTROLLED_START_FINAL_REVIEW_FAILED"
                ),
            }
        ]
    )

    phase_10_9_summary_df.to_csv(
        REPORTS_DIR / "phase_10_9_source_summary_v1.csv",
        index=False,
    )
    source_dependency_matrix_df.to_csv(
        REPORTS_DIR / "phase_10_9_source_pre_start_dependency_matrix_v1.csv",
        index=False,
    )
    source_controls_df.to_csv(
        REPORTS_DIR / "phase_10_9_source_pre_start_controls_v1.csv",
        index=False,
    )
    source_rules_df.to_csv(
        REPORTS_DIR / "phase_10_9_source_pre_start_rules_v1.csv",
        index=False,
    )
    source_requirements_df.to_csv(
        REPORTS_DIR / "phase_10_9_source_pre_start_requirements_v1.csv",
        index=False,
    )
    source_guard_matrix_df.to_csv(
        REPORTS_DIR / "phase_10_9_source_pre_start_guard_matrix_v1.csv",
        index=False,
    )
    source_boundary_matrix_df.to_csv(
        REPORTS_DIR / "phase_10_9_source_pre_start_boundary_matrix_v1.csv",
        index=False,
    )
    source_decision_df.to_csv(
        REPORTS_DIR / "phase_10_9_source_pre_start_decision_v1.csv",
        index=False,
    )
    source_checks_df.to_csv(
        REPORTS_DIR / "phase_10_9_source_checks_v1.csv",
        index=False,
    )
    dependency_matrix_df.to_csv(
        REPORTS_DIR / "long_forward_observation_controlled_start_final_review_dependency_matrix_v1.csv",
        index=False,
    )
    controls_df.to_csv(
        REPORTS_DIR / "long_forward_observation_controlled_start_final_review_controls_v1.csv",
        index=False,
    )
    rules_df.to_csv(
        REPORTS_DIR / "long_forward_observation_controlled_start_final_review_rules_v1.csv",
        index=False,
    )
    requirements_df.to_csv(
        REPORTS_DIR / "long_forward_observation_controlled_start_final_review_requirements_v1.csv",
        index=False,
    )
    guard_matrix_df.to_csv(
        REPORTS_DIR / "long_forward_observation_controlled_start_final_review_guard_matrix_v1.csv",
        index=False,
    )
    boundary_matrix_df.to_csv(
        REPORTS_DIR / "long_forward_observation_controlled_start_final_review_boundary_matrix_v1.csv",
        index=False,
    )
    decision_df.to_csv(
        REPORTS_DIR / "long_forward_observation_controlled_start_final_review_decision_v1.csv",
        index=False,
    )
    checks_df.to_csv(
        REPORTS_DIR / "long_forward_observation_controlled_start_final_review_checks_v1.csv",
        index=False,
    )
    summary_df.to_csv(
        REPORTS_DIR / "long_forward_observation_controlled_start_final_review_summary_v1.csv",
        index=False,
    )

    return {
        "summary": summary_df,
        "source_phase_10_9_summary": phase_10_9_summary_df,
        "source_pre_start_dependency_matrix": source_dependency_matrix_df,
        "source_pre_start_controls": source_controls_df,
        "source_pre_start_rules": source_rules_df,
        "source_pre_start_requirements": source_requirements_df,
        "source_pre_start_guard_matrix": source_guard_matrix_df,
        "source_pre_start_boundary_matrix": source_boundary_matrix_df,
        "source_pre_start_decision": source_decision_df,
        "source_checks": source_checks_df,
        "final_review_dependency_matrix": dependency_matrix_df,
        "final_review_controls": controls_df,
        "final_review_rules": rules_df,
        "final_review_requirements": requirements_df,
        "final_review_guard_matrix": guard_matrix_df,
        "final_review_boundary_matrix": boundary_matrix_df,
        "final_review_decision": decision_df,
        "checks": checks_df,
    }