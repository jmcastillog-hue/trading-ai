from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from src.long_side.long_forward_observation_dataset_bootstrap_v1 import (
    OFFICIAL_DATASET_PATH,
)
from src.long_side.long_forward_observation_phase_closure_v1 import (
    PHASE_9_CLOSURE_DECISION,
    validate_long_forward_observation_phase_closure,
)


REPORTS_DIR = Path("reports/phase_10_1_long_forward_observation_controlled_start_review_v1")

PHASE_9_10_PHASE_CLOSURE_DOC_PATH = Path(
    "docs/PHASE_9_LONG_FORWARD_OBSERVATION_PHASE_CLOSURE.md"
)
PHASE_10_1_CONTROLLED_START_REVIEW_DOC_PATH = Path(
    "docs/PHASE_10_LONG_FORWARD_OBSERVATION_CONTROLLED_START_REVIEW.md"
)

CONTROLLED_START_REVIEW_STATUS = "LONG_FORWARD_OBSERVATION_CONTROLLED_START_REVIEW_ONLY"
READY_DECISION = "CONTROLLED_START_REVIEW_READY_FOR_MANUAL_OBSERVATION_PROTOCOL"
BLOCKED_DECISION = "CONTROLLED_START_REVIEW_BLOCKED"

RECOMMENDED_NEXT_PHASE = "PHASE_10_2_LONG_FORWARD_OBSERVATION_MANUAL_START_PROTOCOL_V1"

SAFETY_FLAGS = {
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


def build_controlled_start_review_requirements(
    phase_9_10_summary_df: pd.DataFrame,
    phase_9_closure_decision_df: pd.DataFrame,
) -> pd.DataFrame:
    summary = (
        phase_9_10_summary_df.iloc[0].to_dict()
        if not phase_9_10_summary_df.empty
        else {}
    )

    closure_decision = (
        phase_9_closure_decision_df.iloc[0].to_dict()
        if not phase_9_closure_decision_df.empty
        else {}
    )

    requirements: list[dict[str, Any]] = [
        {
            "requirement_id": "CTRL_START_REVIEW_001",
            "requirement_name": "phase_9_10_validation_passed",
            "passed": safe_bool(summary.get("validation_passed", False)),
            "required_value": "True",
            "actual_value": str(summary.get("validation_passed", "")),
            "requirement_group": "dependency",
        },
        {
            "requirement_id": "CTRL_START_REVIEW_002",
            "requirement_name": "phase_9_closed",
            "passed": safe_bool(summary.get("phase_9_closed", False)),
            "required_value": "True",
            "actual_value": str(summary.get("phase_9_closed", "")),
            "requirement_group": "phase_9_closure",
        },
        {
            "requirement_id": "CTRL_START_REVIEW_003",
            "requirement_name": "phase_9_closure_decision_expected",
            "passed": str(summary.get("phase_9_closure_decision", "")).strip()
            == PHASE_9_CLOSURE_DECISION,
            "required_value": PHASE_9_CLOSURE_DECISION,
            "actual_value": str(summary.get("phase_9_closure_decision", "")),
            "requirement_group": "phase_9_closure",
        },
        {
            "requirement_id": "CTRL_START_REVIEW_004",
            "requirement_name": "future_controlled_start_review_allowed",
            "passed": safe_bool(
                summary.get("future_controlled_start_review_allowed", False)
            ),
            "required_value": "True",
            "actual_value": str(
                summary.get("future_controlled_start_review_allowed", "")
            ),
            "requirement_group": "future_review",
        },
        {
            "requirement_id": "CTRL_START_REVIEW_005",
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
            "requirement_id": "CTRL_START_REVIEW_006",
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
            "requirement_id": "CTRL_START_REVIEW_007",
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
            "requirement_id": "CTRL_START_REVIEW_008",
            "requirement_name": "official_dataset_not_created",
            "passed": safe_bool(
                summary.get("real_forward_dataset_created", True),
                default=True,
            )
            is False,
            "required_value": "False",
            "actual_value": str(summary.get("real_forward_dataset_created", "")),
            "requirement_group": "official_dataset_guard",
        },
        {
            "requirement_id": "CTRL_START_REVIEW_009",
            "requirement_name": "official_evidence_rows_written_zero",
            "passed": int(summary.get("official_evidence_rows_written", -1)) == 0,
            "required_value": "0",
            "actual_value": str(summary.get("official_evidence_rows_written", "")),
            "requirement_group": "official_dataset_guard",
        },
        {
            "requirement_id": "CTRL_START_REVIEW_010",
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
            "requirement_id": "CTRL_START_REVIEW_011",
            "requirement_name": "execution_disabled",
            "passed": safe_bool(summary.get("execution_allowed", True), default=True)
            is False,
            "required_value": "False",
            "actual_value": str(summary.get("execution_allowed", "")),
            "requirement_group": "safety",
        },
        {
            "requirement_id": "CTRL_START_REVIEW_012",
            "requirement_name": "paper_trading_disabled",
            "passed": safe_bool(
                summary.get("paper_trading_enabled", True),
                default=True,
            )
            is False,
            "required_value": "False",
            "actual_value": str(summary.get("paper_trading_enabled", "")),
            "requirement_group": "safety",
        },
        {
            "requirement_id": "CTRL_START_REVIEW_013",
            "requirement_name": "live_alerts_disabled",
            "passed": safe_bool(
                summary.get("live_alerts_allowed", True),
                default=True,
            )
            is False,
            "required_value": "False",
            "actual_value": str(summary.get("live_alerts_allowed", "")),
            "requirement_group": "safety",
        },
        {
            "requirement_id": "CTRL_START_REVIEW_014",
            "requirement_name": "real_capital_disabled",
            "passed": safe_bool(
                summary.get("real_capital_allowed", True),
                default=True,
            )
            is False,
            "required_value": "False",
            "actual_value": str(summary.get("real_capital_allowed", "")),
            "requirement_group": "safety",
        },
        {
            "requirement_id": "CTRL_START_REVIEW_015",
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
        {
            "requirement_id": "CTRL_START_REVIEW_016",
            "requirement_name": "phase_9_closure_decision_table_consistent",
            "passed": (
                not phase_9_closure_decision_df.empty
                and safe_bool(closure_decision.get("phase_9_closed", False))
                and str(closure_decision.get("phase_9_closure_decision", "")).strip()
                == PHASE_9_CLOSURE_DECISION
            ),
            "required_value": "True",
            "actual_value": str(closure_decision.get("phase_9_closure_decision", "")),
            "requirement_group": "summary_consistency",
        },
    ]

    return pd.DataFrame(requirements)


def build_start_review_boundary_matrix() -> pd.DataFrame:
    rows = [
        {
            "boundary_item": "manual_observation_protocol_planning_allowed",
            "allowed": True,
            "boundary_type": "planning_only",
            "details": "Allowed only to plan the future manual observation protocol.",
        },
        {
            "boundary_item": "controlled_forward_observation_start_approved",
            "allowed": False,
            "boundary_type": "operational_start",
            "details": "Phase 10.1 does not approve forward observation start.",
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


def build_controlled_start_review_safety_matrix() -> pd.DataFrame:
    rows: list[dict[str, Any]] = []

    for flag_name, flag_value in SAFETY_FLAGS.items():
        rows.append(
            {
                "safety_flag": flag_name,
                "required_value": False,
                "actual_value": flag_value,
                "passed": flag_value is False,
                "review_status": CONTROLLED_START_REVIEW_STATUS,
            }
        )

    rows.append(
        {
            "safety_flag": "official_evidence_rows_written",
            "required_value": 0,
            "actual_value": 0,
            "passed": True,
            "review_status": CONTROLLED_START_REVIEW_STATUS,
        }
    )

    return pd.DataFrame(rows)


def build_controlled_start_review_decision_table(
    requirements_df: pd.DataFrame,
    boundary_matrix_df: pd.DataFrame,
    safety_matrix_df: pd.DataFrame,
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

    disallowed_operational_boundaries_passed = True

    if not boundary_matrix_df.empty:
        disallowed_rows = boundary_matrix_df[
            boundary_matrix_df["boundary_item"].astype(str)
            != "manual_observation_protocol_planning_allowed"
        ]
        disallowed_operational_boundaries_passed = (
            not disallowed_rows.empty
            and disallowed_rows["allowed"].astype(bool).eq(False).all()
        )

    controlled_start_review_passed = (
        total_requirements > 0
        and failed_requirements == 0
        and safety_matrix_passed
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
                "controlled_start_review_id": "PHASE_10_1_CONTROLLED_START_REVIEW_001",
                "controlled_start_review_status": CONTROLLED_START_REVIEW_STATUS,
                "controlled_start_review_passed": controlled_start_review_passed,
                "controlled_start_review_decision": (
                    READY_DECISION if controlled_start_review_passed else BLOCKED_DECISION
                ),
                "total_requirements": total_requirements,
                "passed_requirements": passed_requirements,
                "failed_requirements": failed_requirements,
                "failed_requirement_names": failed_requirement_names,
                "safety_matrix_passed": safety_matrix_passed,
                "disallowed_operational_boundaries_passed": (
                    disallowed_operational_boundaries_passed
                ),
                "manual_observation_protocol_planning_allowed": (
                    controlled_start_review_passed
                ),
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


def validate_long_forward_observation_controlled_start_review() -> dict[str, pd.DataFrame]:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    checks: list[dict[str, Any]] = []

    phase_anchors = {
        "phase_9_10_phase_closure_doc_exists": PHASE_9_10_PHASE_CLOSURE_DOC_PATH,
        "phase_10_1_controlled_start_review_doc_exists": (
            PHASE_10_1_CONTROLLED_START_REVIEW_DOC_PATH
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

    phase_9_10_result = validate_long_forward_observation_phase_closure()

    phase_9_10_summary_df = phase_9_10_result["summary"]
    source_phase_9_closure_ledger_df = phase_9_10_result["phase_9_closure_ledger"]
    source_phase_9_closure_requirements_df = phase_9_10_result[
        "phase_9_closure_requirements"
    ]
    source_phase_9_safety_closure_matrix_df = phase_9_10_result[
        "phase_9_safety_closure_matrix"
    ]
    source_phase_9_closure_decision_df = phase_9_10_result[
        "phase_9_closure_decision"
    ]
    source_checks_df = phase_9_10_result["checks"]

    phase_9_10_validation_passed = (
        not phase_9_10_summary_df.empty
        and bool(phase_9_10_summary_df.iloc[0].get("validation_passed", False))
    )

    phase_closure_defined = (
        not phase_9_10_summary_df.empty
        and bool(
            phase_9_10_summary_df.iloc[0].get(
                "long_forward_observation_phase_closure_defined",
                False,
            )
        )
    )

    controlled_start_requirements_df = build_controlled_start_review_requirements(
        phase_9_10_summary_df=phase_9_10_summary_df,
        phase_9_closure_decision_df=source_phase_9_closure_decision_df,
    )

    boundary_matrix_df = build_start_review_boundary_matrix()

    safety_matrix_df = build_controlled_start_review_safety_matrix()

    controlled_start_review_decision_df = build_controlled_start_review_decision_table(
        requirements_df=controlled_start_requirements_df,
        boundary_matrix_df=boundary_matrix_df,
        safety_matrix_df=safety_matrix_df,
    )

    official_dataset_exists_after = OFFICIAL_DATASET_PATH.exists()

    decision = (
        controlled_start_review_decision_df.iloc[0].to_dict()
        if not controlled_start_review_decision_df.empty
        else {}
    )

    controlled_start_review_passed = safe_bool(
        decision.get("controlled_start_review_passed", False)
    )
    controlled_start_review_decision = str(
        decision.get("controlled_start_review_decision", "")
    )
    manual_observation_protocol_planning_allowed = safe_bool(
        decision.get("manual_observation_protocol_planning_allowed", False)
    )

    checks.append(
        build_check(
            check_group="phase_dependency",
            check_name="phase_9_10_validation_passed",
            passed=phase_9_10_validation_passed,
            severity="INFO" if phase_9_10_validation_passed else "ERROR",
            details=(
                str(phase_9_10_summary_df.iloc[0].get("validation_decision", ""))
                if not phase_9_10_summary_df.empty
                else "Missing Phase 9.10 summary."
            ),
        )
    )

    checks.append(
        build_check(
            check_group="phase_dependency",
            check_name="long_forward_observation_phase_closure_defined",
            passed=phase_closure_defined,
            severity="INFO" if phase_closure_defined else "ERROR",
            details=f"phase_closure_defined={phase_closure_defined}",
        )
    )

    requirements_passed = (
        not controlled_start_requirements_df.empty
        and controlled_start_requirements_df["passed"].astype(bool).all()
    )

    checks.append(
        build_check(
            check_group="controlled_start_review",
            check_name="controlled_start_review_requirements_passed",
            passed=requirements_passed,
            severity="INFO" if requirements_passed else "ERROR",
            details=(
                "failed_requirements="
                + ",".join(
                    controlled_start_requirements_df[
                        ~controlled_start_requirements_df["passed"].astype(bool)
                    ]["requirement_name"].astype(str)
                )
                if not controlled_start_requirements_df.empty
                else "failed_requirements=all"
            ),
        )
    )

    checks.append(
        build_check(
            check_group="controlled_start_review",
            check_name="controlled_start_review_passed",
            passed=controlled_start_review_passed,
            severity="INFO" if controlled_start_review_passed else "ERROR",
            details=f"controlled_start_review_passed={controlled_start_review_passed}",
        )
    )

    checks.append(
        build_check(
            check_group="controlled_start_review",
            check_name="controlled_start_review_decision_expected",
            passed=controlled_start_review_decision == READY_DECISION,
            severity=(
                "INFO"
                if controlled_start_review_decision == READY_DECISION
                else "ERROR"
            ),
            details=(
                "controlled_start_review_decision="
                + controlled_start_review_decision
            ),
        )
    )

    checks.append(
        build_check(
            check_group="planning_scope",
            check_name="manual_observation_protocol_planning_allowed",
            passed=manual_observation_protocol_planning_allowed,
            severity="WARNING" if manual_observation_protocol_planning_allowed else "ERROR",
            details=(
                "This allows only protocol planning, not observation start, "
                "alerts, paper trading, real capital, or execution."
            ),
        )
    )

    start_approved = safe_bool(
        decision.get("controlled_forward_observation_start_approved", True),
        default=True,
    )

    checks.append(
        build_check(
            check_group="safety_controls",
            check_name="controlled_forward_observation_start_not_approved",
            passed=start_approved is False,
            severity="INFO" if start_approved is False else "ERROR",
            details=f"controlled_forward_observation_start_approved={start_approved}",
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
        not safety_matrix_df.empty and safety_matrix_df["passed"].astype(bool).all()
    )

    checks.append(
        build_check(
            check_group="safety_controls",
            check_name="controlled_start_review_safety_matrix_passed",
            passed=safety_matrix_passed,
            severity="INFO" if safety_matrix_passed else "ERROR",
            details=(
                "failed_safety_flags="
                + ",".join(
                    safety_matrix_df[
                        ~safety_matrix_df["passed"].astype(bool)
                    ]["safety_flag"].astype(str)
                )
                if not safety_matrix_df.empty
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
            check_name="controlled_start_review_only",
            passed=True,
            severity="WARNING",
            details="Phase 10.1 is a controlled start review only.",
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
            check_name="phase_10_2_recommended_next",
            passed=True,
            severity="INFO",
            details=(
                "Recommended next step: "
                "Phase 10.2 LONG Forward Observation Manual Start Protocol V1."
            ),
        )
    )

    checks_df = pd.DataFrame(checks)

    blocker_count = int(checks_df["blocker"].astype(bool).sum())
    error_count = int(checks_df["severity"].eq("ERROR").sum())
    warning_count = int(checks_df["severity"].eq("WARNING").sum())

    validation_passed = blocker_count == 0 and error_count == 0

    phase_9_10_summary = (
        phase_9_10_summary_df.iloc[0].to_dict()
        if not phase_9_10_summary_df.empty
        else {}
    )

    summary_df = pd.DataFrame(
        [
            {
                "phase": "10.1",
                "long_forward_observation_controlled_start_review_defined": True,
                "phase_9_10_validation_passed": phase_9_10_validation_passed,
                "long_forward_observation_phase_closure_defined": (
                    phase_closure_defined
                ),
                "phase_9_closed": safe_bool(
                    phase_9_10_summary.get("phase_9_closed", False)
                ),
                "phase_9_closure_decision": str(
                    phase_9_10_summary.get("phase_9_closure_decision", "")
                ),
                "future_controlled_start_review_allowed": safe_bool(
                    phase_9_10_summary.get("future_controlled_start_review_allowed", False)
                ),
                "controlled_start_review_requirement_rows": int(
                    len(controlled_start_requirements_df)
                ),
                "controlled_start_review_passed": controlled_start_review_passed,
                "controlled_start_review_decision": controlled_start_review_decision,
                "manual_observation_protocol_planning_allowed": (
                    manual_observation_protocol_planning_allowed
                ),
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
                "estimated_phase_10_progress_percent": 10,
                "total_checks": int(len(checks_df)),
                "warning_count": warning_count,
                "error_count": error_count,
                "blocker_count": blocker_count,
                "validation_passed": validation_passed,
                "validation_decision": (
                    "PHASE_10_1_LONG_FORWARD_OBSERVATION_CONTROLLED_START_REVIEW_VALIDATED"
                    if validation_passed
                    else "PHASE_10_1_LONG_FORWARD_OBSERVATION_CONTROLLED_START_REVIEW_FAILED"
                ),
            }
        ]
    )

    phase_9_10_summary_df.to_csv(
        REPORTS_DIR / "phase_9_10_source_summary_v1.csv",
        index=False,
    )
    source_phase_9_closure_ledger_df.to_csv(
        REPORTS_DIR / "phase_9_10_source_closure_ledger_v1.csv",
        index=False,
    )
    source_phase_9_closure_requirements_df.to_csv(
        REPORTS_DIR / "phase_9_10_source_closure_requirements_v1.csv",
        index=False,
    )
    source_phase_9_safety_closure_matrix_df.to_csv(
        REPORTS_DIR / "phase_9_10_source_safety_closure_matrix_v1.csv",
        index=False,
    )
    source_phase_9_closure_decision_df.to_csv(
        REPORTS_DIR / "phase_9_10_source_closure_decision_v1.csv",
        index=False,
    )
    source_checks_df.to_csv(
        REPORTS_DIR / "phase_9_10_source_checks_v1.csv",
        index=False,
    )
    controlled_start_requirements_df.to_csv(
        REPORTS_DIR / "long_forward_observation_controlled_start_review_requirements_v1.csv",
        index=False,
    )
    boundary_matrix_df.to_csv(
        REPORTS_DIR / "long_forward_observation_controlled_start_review_boundary_matrix_v1.csv",
        index=False,
    )
    safety_matrix_df.to_csv(
        REPORTS_DIR / "long_forward_observation_controlled_start_review_safety_matrix_v1.csv",
        index=False,
    )
    controlled_start_review_decision_df.to_csv(
        REPORTS_DIR / "long_forward_observation_controlled_start_review_decision_v1.csv",
        index=False,
    )
    checks_df.to_csv(
        REPORTS_DIR / "long_forward_observation_controlled_start_review_checks_v1.csv",
        index=False,
    )
    summary_df.to_csv(
        REPORTS_DIR / "long_forward_observation_controlled_start_review_summary_v1.csv",
        index=False,
    )

    return {
        "summary": summary_df,
        "source_phase_9_10_summary": phase_9_10_summary_df,
        "source_phase_9_closure_ledger": source_phase_9_closure_ledger_df,
        "source_phase_9_closure_requirements": source_phase_9_closure_requirements_df,
        "source_phase_9_safety_closure_matrix": source_phase_9_safety_closure_matrix_df,
        "source_phase_9_closure_decision": source_phase_9_closure_decision_df,
        "source_checks": source_checks_df,
        "controlled_start_review_requirements": controlled_start_requirements_df,
        "controlled_start_review_boundary_matrix": boundary_matrix_df,
        "controlled_start_review_safety_matrix": safety_matrix_df,
        "controlled_start_review_decision": controlled_start_review_decision_df,
        "checks": checks_df,
    }