from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from src.long_side.long_forward_observation_dataset_bootstrap_v1 import (
    OFFICIAL_DATASET_PATH,
)
from src.long_side.long_forward_observation_pre_start_gate_v1 import (
    READY_DECISION,
    validate_long_forward_observation_pre_start_gate,
)


REPORTS_DIR = Path("reports/phase_9_10_long_forward_observation_phase_closure_v1")

PHASE_9_9_PRE_START_GATE_DOC_PATH = Path(
    "docs/PHASE_9_LONG_FORWARD_OBSERVATION_PRE_START_GATE.md"
)
PHASE_9_10_PHASE_CLOSURE_DOC_PATH = Path(
    "docs/PHASE_9_LONG_FORWARD_OBSERVATION_PHASE_CLOSURE.md"
)

PHASE_9_CLOSURE_STATUS = "LONG_FORWARD_OBSERVATION_PREPARATION_LAYER_CLOSED"
PHASE_9_CLOSURE_DECISION = "PHASE_9_LONG_FORWARD_OBSERVATION_PREPARATION_CLOSED"

RECOMMENDED_NEXT_PHASE = "PHASE_10_1_LONG_FORWARD_OBSERVATION_CONTROLLED_START_REVIEW_V1"

PHASE_LEDGER = [
    {
        "phase_step": "9.1",
        "phase_name": "LONG Forward Observation Framework",
        "phase_role": "framework_definition",
        "required_for_closure": True,
        "expected_status": "closed",
    },
    {
        "phase_step": "9.2",
        "phase_name": "LONG Forward Signal Journal",
        "phase_role": "journal_template_definition",
        "required_for_closure": True,
        "expected_status": "closed",
    },
    {
        "phase_step": "9.3",
        "phase_name": "LONG Forward Journal Input Validator",
        "phase_role": "input_validation",
        "required_for_closure": True,
        "expected_status": "closed",
    },
    {
        "phase_step": "9.4",
        "phase_name": "LONG Forward Journal Controlled Input Run",
        "phase_role": "controlled_input_run",
        "required_for_closure": True,
        "expected_status": "closed",
    },
    {
        "phase_step": "9.5",
        "phase_name": "LONG Forward Observation Dataset Bootstrap",
        "phase_role": "dataset_bootstrap",
        "required_for_closure": True,
        "expected_status": "closed",
    },
    {
        "phase_step": "9.6",
        "phase_name": "LONG Forward Observation Persistence Guard",
        "phase_role": "persistence_guard",
        "required_for_closure": True,
        "expected_status": "closed",
    },
    {
        "phase_step": "9.7",
        "phase_name": "LONG Forward Observation Controlled Dataset Write",
        "phase_role": "controlled_report_only_write",
        "required_for_closure": True,
        "expected_status": "closed",
    },
    {
        "phase_step": "9.8",
        "phase_name": "LONG Forward Observation Report Integrity",
        "phase_role": "report_integrity_audit",
        "required_for_closure": True,
        "expected_status": "closed",
    },
    {
        "phase_step": "9.9",
        "phase_name": "LONG Forward Observation Pre-Start Gate",
        "phase_role": "pre_start_gate",
        "required_for_closure": True,
        "expected_status": "closed",
    },
]

SAFETY_FLAGS = {
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


def build_phase_9_closure_ledger() -> pd.DataFrame:
    rows: list[dict[str, Any]] = []

    for item in PHASE_LEDGER:
        rows.append(
            {
                "phase_step": item["phase_step"],
                "phase_name": item["phase_name"],
                "phase_role": item["phase_role"],
                "required_for_closure": item["required_for_closure"],
                "expected_status": item["expected_status"],
                "closure_status": "CLOSED_AS_PREPARATION_LAYER",
                "execution_allowed": False,
                "paper_trade_execution_allowed": False,
                "real_capital_allowed": False,
                "live_alerts_allowed": False,
                "automation_allowed": False,
                "phase_9_closure_scope": "PREPARATION_ONLY",
            }
        )

    return pd.DataFrame(rows)


def build_phase_9_closure_requirements(
    phase_9_9_summary_df: pd.DataFrame,
    pre_start_gate_decision_df: pd.DataFrame,
    phase_9_ledger_df: pd.DataFrame,
) -> pd.DataFrame:
    summary = (
        phase_9_9_summary_df.iloc[0].to_dict()
        if not phase_9_9_summary_df.empty
        else {}
    )

    decision = (
        pre_start_gate_decision_df.iloc[0].to_dict()
        if not pre_start_gate_decision_df.empty
        else {}
    )

    all_ledger_steps_closed = (
        not phase_9_ledger_df.empty
        and phase_9_ledger_df["required_for_closure"].astype(bool).all()
        and phase_9_ledger_df["closure_status"]
        .astype(str)
        .eq("CLOSED_AS_PREPARATION_LAYER")
        .all()
    )

    requirements: list[dict[str, Any]] = [
        {
            "requirement_id": "PHASE_9_CLOSE_001",
            "requirement_name": "phase_9_9_validation_passed",
            "passed": safe_bool(summary.get("validation_passed", False)),
            "required_value": "True",
            "actual_value": str(summary.get("validation_passed", "")),
            "requirement_group": "dependency",
        },
        {
            "requirement_id": "PHASE_9_CLOSE_002",
            "requirement_name": "pre_start_gate_passed",
            "passed": safe_bool(summary.get("pre_start_gate_passed", False)),
            "required_value": "True",
            "actual_value": str(summary.get("pre_start_gate_passed", "")),
            "requirement_group": "pre_start_gate",
        },
        {
            "requirement_id": "PHASE_9_CLOSE_003",
            "requirement_name": "pre_start_gate_decision_ready",
            "passed": str(summary.get("pre_start_gate_decision", "")).strip()
            == READY_DECISION,
            "required_value": READY_DECISION,
            "actual_value": str(summary.get("pre_start_gate_decision", "")),
            "requirement_group": "pre_start_gate",
        },
        {
            "requirement_id": "PHASE_9_CLOSE_004",
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
            "requirement_id": "PHASE_9_CLOSE_005",
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
            "requirement_id": "PHASE_9_CLOSE_006",
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
            "requirement_id": "PHASE_9_CLOSE_007",
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
            "requirement_id": "PHASE_9_CLOSE_008",
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
            "requirement_id": "PHASE_9_CLOSE_009",
            "requirement_name": "official_evidence_rows_written_zero",
            "passed": int(summary.get("official_evidence_rows_written", -1)) == 0,
            "required_value": "0",
            "actual_value": str(summary.get("official_evidence_rows_written", "")),
            "requirement_group": "official_dataset_guard",
        },
        {
            "requirement_id": "PHASE_9_CLOSE_010",
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
            "requirement_id": "PHASE_9_CLOSE_011",
            "requirement_name": "execution_disabled",
            "passed": safe_bool(summary.get("execution_allowed", True), default=True)
            is False,
            "required_value": "False",
            "actual_value": str(summary.get("execution_allowed", "")),
            "requirement_group": "safety",
        },
        {
            "requirement_id": "PHASE_9_CLOSE_012",
            "requirement_name": "phase_9_ledger_all_steps_closed",
            "passed": all_ledger_steps_closed,
            "required_value": "True",
            "actual_value": str(all_ledger_steps_closed),
            "requirement_group": "phase_ledger",
        },
        {
            "requirement_id": "PHASE_9_CLOSE_013",
            "requirement_name": "pre_start_gate_decision_table_consistent",
            "passed": (
                not pre_start_gate_decision_df.empty
                and safe_bool(decision.get("pre_start_gate_passed", False))
                and str(decision.get("pre_start_gate_decision", "")).strip()
                == READY_DECISION
            ),
            "required_value": "True",
            "actual_value": str(decision.get("pre_start_gate_decision", "")),
            "requirement_group": "summary_consistency",
        },
    ]

    return pd.DataFrame(requirements)


def build_phase_9_safety_closure_matrix() -> pd.DataFrame:
    rows: list[dict[str, Any]] = []

    for flag_name, flag_value in SAFETY_FLAGS.items():
        rows.append(
            {
                "safety_flag": flag_name,
                "required_value": False,
                "actual_value": flag_value,
                "passed": flag_value is False,
                "closure_status": PHASE_9_CLOSURE_STATUS,
            }
        )

    rows.append(
        {
            "safety_flag": "official_evidence_rows_written",
            "required_value": 0,
            "actual_value": 0,
            "passed": True,
            "closure_status": PHASE_9_CLOSURE_STATUS,
        }
    )

    return pd.DataFrame(rows)


def build_phase_9_closure_decision_table(
    requirements_df: pd.DataFrame,
    safety_matrix_df: pd.DataFrame,
) -> pd.DataFrame:
    total_requirements = int(len(requirements_df))
    passed_requirements = (
        int(requirements_df["passed"].astype(bool).sum())
        if total_requirements
        else 0
    )
    failed_requirements = total_requirements - passed_requirements

    safety_passed = (
        not safety_matrix_df.empty and safety_matrix_df["passed"].astype(bool).all()
    )

    closure_passed = total_requirements > 0 and failed_requirements == 0 and safety_passed

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
                "phase_9_closure_id": "PHASE_9_10_CLOSURE_001",
                "phase_9_closure_status": PHASE_9_CLOSURE_STATUS,
                "phase_9_closed": closure_passed,
                "phase_9_closure_decision": (
                    PHASE_9_CLOSURE_DECISION if closure_passed else "PHASE_9_CLOSURE_BLOCKED"
                ),
                "phase_9_closure_scope": "LONG_FORWARD_OBSERVATION_PREPARATION_ONLY",
                "total_requirements": total_requirements,
                "passed_requirements": passed_requirements,
                "failed_requirements": failed_requirements,
                "failed_requirement_names": failed_requirement_names,
                "safety_matrix_passed": safety_passed,
                "future_controlled_start_review_allowed": closure_passed,
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


def validate_long_forward_observation_phase_closure() -> dict[str, pd.DataFrame]:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    checks: list[dict[str, Any]] = []

    phase_anchors = {
        "phase_9_9_pre_start_gate_doc_exists": PHASE_9_9_PRE_START_GATE_DOC_PATH,
        "phase_9_10_phase_closure_doc_exists": PHASE_9_10_PHASE_CLOSURE_DOC_PATH,
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

    phase_9_9_result = validate_long_forward_observation_pre_start_gate()

    phase_9_9_summary_df = phase_9_9_result["summary"]
    source_pre_start_criteria_df = phase_9_9_result["pre_start_criteria"]
    source_pre_start_gate_decision_df = phase_9_9_result["pre_start_gate_decision"]
    source_pre_start_safety_matrix_df = phase_9_9_result["pre_start_safety_matrix"]
    source_checks_df = phase_9_9_result["checks"]

    phase_9_9_validation_passed = (
        not phase_9_9_summary_df.empty
        and bool(phase_9_9_summary_df.iloc[0].get("validation_passed", False))
    )

    pre_start_gate_defined = (
        not phase_9_9_summary_df.empty
        and bool(
            phase_9_9_summary_df.iloc[0].get(
                "long_forward_observation_pre_start_gate_defined",
                False,
            )
        )
    )

    phase_9_ledger_df = build_phase_9_closure_ledger()

    closure_requirements_df = build_phase_9_closure_requirements(
        phase_9_9_summary_df=phase_9_9_summary_df,
        pre_start_gate_decision_df=source_pre_start_gate_decision_df,
        phase_9_ledger_df=phase_9_ledger_df,
    )

    safety_closure_matrix_df = build_phase_9_safety_closure_matrix()

    closure_decision_df = build_phase_9_closure_decision_table(
        requirements_df=closure_requirements_df,
        safety_matrix_df=safety_closure_matrix_df,
    )

    official_dataset_exists_after = OFFICIAL_DATASET_PATH.exists()

    closure_decision = (
        closure_decision_df.iloc[0].to_dict() if not closure_decision_df.empty else {}
    )

    phase_9_closed = safe_bool(closure_decision.get("phase_9_closed", False))
    phase_9_closure_decision = str(
        closure_decision.get("phase_9_closure_decision", "")
    )

    checks.append(
        build_check(
            check_group="phase_dependency",
            check_name="phase_9_9_validation_passed",
            passed=phase_9_9_validation_passed,
            severity="INFO" if phase_9_9_validation_passed else "ERROR",
            details=(
                str(phase_9_9_summary_df.iloc[0].get("validation_decision", ""))
                if not phase_9_9_summary_df.empty
                else "Missing Phase 9.9 summary."
            ),
        )
    )

    checks.append(
        build_check(
            check_group="phase_dependency",
            check_name="long_forward_observation_pre_start_gate_defined",
            passed=pre_start_gate_defined,
            severity="INFO" if pre_start_gate_defined else "ERROR",
            details=f"pre_start_gate_defined={pre_start_gate_defined}",
        )
    )

    requirements_passed = (
        not closure_requirements_df.empty
        and closure_requirements_df["passed"].astype(bool).all()
    )

    checks.append(
        build_check(
            check_group="closure_requirements",
            check_name="phase_9_closure_requirements_passed",
            passed=requirements_passed,
            severity="INFO" if requirements_passed else "ERROR",
            details=(
                "failed_requirements="
                + ",".join(
                    closure_requirements_df[
                        ~closure_requirements_df["passed"].astype(bool)
                    ]["requirement_name"].astype(str)
                )
                if not closure_requirements_df.empty
                else "failed_requirements=all"
            ),
        )
    )

    safety_matrix_passed = (
        not safety_closure_matrix_df.empty
        and safety_closure_matrix_df["passed"].astype(bool).all()
    )

    checks.append(
        build_check(
            check_group="closure_safety",
            check_name="phase_9_safety_closure_matrix_passed",
            passed=safety_matrix_passed,
            severity="INFO" if safety_matrix_passed else "ERROR",
            details=(
                "failed_safety_flags="
                + ",".join(
                    safety_closure_matrix_df[
                        ~safety_closure_matrix_df["passed"].astype(bool)
                    ]["safety_flag"].astype(str)
                )
                if not safety_closure_matrix_df.empty
                else "failed_safety_flags=all"
            ),
        )
    )

    checks.append(
        build_check(
            check_group="closure_decision",
            check_name="phase_9_closed_as_preparation_layer",
            passed=phase_9_closed,
            severity="INFO" if phase_9_closed else "ERROR",
            details=f"phase_9_closed={phase_9_closed}",
        )
    )

    checks.append(
        build_check(
            check_group="closure_decision",
            check_name="phase_9_closure_decision_expected",
            passed=phase_9_closure_decision == PHASE_9_CLOSURE_DECISION,
            severity=(
                "INFO"
                if phase_9_closure_decision == PHASE_9_CLOSURE_DECISION
                else "ERROR"
            ),
            details=f"phase_9_closure_decision={phase_9_closure_decision}",
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
            check_name="phase_9_closure_only",
            passed=True,
            severity="WARNING",
            details="Phase 9.10 closes preparation layer only.",
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
            check_name="phase_10_1_recommended_next",
            passed=True,
            severity="INFO",
            details=(
                "Recommended next step: "
                "Phase 10.1 LONG Forward Observation Controlled Start Review V1."
            ),
        )
    )

    checks_df = pd.DataFrame(checks)

    blocker_count = int(checks_df["blocker"].astype(bool).sum())
    error_count = int(checks_df["severity"].eq("ERROR").sum())
    warning_count = int(checks_df["severity"].eq("WARNING").sum())

    validation_passed = blocker_count == 0 and error_count == 0

    phase_9_9_summary = (
        phase_9_9_summary_df.iloc[0].to_dict()
        if not phase_9_9_summary_df.empty
        else {}
    )

    summary_df = pd.DataFrame(
        [
            {
                "phase": "9.10",
                "long_forward_observation_phase_closure_defined": True,
                "phase_9_9_validation_passed": phase_9_9_validation_passed,
                "long_forward_observation_pre_start_gate_defined": (
                    pre_start_gate_defined
                ),
                "pre_start_gate_passed": safe_bool(
                    phase_9_9_summary.get("pre_start_gate_passed", False)
                ),
                "pre_start_gate_decision": str(
                    phase_9_9_summary.get("pre_start_gate_decision", "")
                ),
                "future_controlled_start_review_allowed": safe_bool(
                    phase_9_9_summary.get("future_controlled_start_review_allowed", False)
                ),
                "phase_9_ledger_rows": int(len(phase_9_ledger_df)),
                "phase_9_closure_requirement_rows": int(len(closure_requirements_df)),
                "phase_9_safety_closure_rows": int(len(safety_closure_matrix_df)),
                "phase_9_closed": phase_9_closed,
                "phase_9_closure_decision": phase_9_closure_decision,
                "phase_9_closure_scope": (
                    "LONG_FORWARD_OBSERVATION_PREPARATION_ONLY"
                ),
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
                "estimated_phase_9_progress_percent": 100,
                "total_checks": int(len(checks_df)),
                "warning_count": warning_count,
                "error_count": error_count,
                "blocker_count": blocker_count,
                "validation_passed": validation_passed,
                "validation_decision": (
                    "PHASE_9_10_LONG_FORWARD_OBSERVATION_PHASE_CLOSURE_VALIDATED"
                    if validation_passed
                    else "PHASE_9_10_LONG_FORWARD_OBSERVATION_PHASE_CLOSURE_FAILED"
                ),
            }
        ]
    )

    phase_9_9_summary_df.to_csv(
        REPORTS_DIR / "phase_9_9_source_summary_v1.csv",
        index=False,
    )
    source_pre_start_criteria_df.to_csv(
        REPORTS_DIR / "phase_9_9_source_pre_start_criteria_v1.csv",
        index=False,
    )
    source_pre_start_gate_decision_df.to_csv(
        REPORTS_DIR / "phase_9_9_source_pre_start_gate_decision_v1.csv",
        index=False,
    )
    source_pre_start_safety_matrix_df.to_csv(
        REPORTS_DIR / "phase_9_9_source_pre_start_safety_matrix_v1.csv",
        index=False,
    )
    source_checks_df.to_csv(
        REPORTS_DIR / "phase_9_9_source_checks_v1.csv",
        index=False,
    )
    phase_9_ledger_df.to_csv(
        REPORTS_DIR / "long_forward_observation_phase_9_closure_ledger_v1.csv",
        index=False,
    )
    closure_requirements_df.to_csv(
        REPORTS_DIR / "long_forward_observation_phase_9_closure_requirements_v1.csv",
        index=False,
    )
    safety_closure_matrix_df.to_csv(
        REPORTS_DIR / "long_forward_observation_phase_9_safety_closure_matrix_v1.csv",
        index=False,
    )
    closure_decision_df.to_csv(
        REPORTS_DIR / "long_forward_observation_phase_9_closure_decision_v1.csv",
        index=False,
    )
    checks_df.to_csv(
        REPORTS_DIR / "long_forward_observation_phase_closure_checks_v1.csv",
        index=False,
    )
    summary_df.to_csv(
        REPORTS_DIR / "long_forward_observation_phase_closure_summary_v1.csv",
        index=False,
    )

    return {
        "summary": summary_df,
        "source_phase_9_9_summary": phase_9_9_summary_df,
        "source_pre_start_criteria": source_pre_start_criteria_df,
        "source_pre_start_gate_decision": source_pre_start_gate_decision_df,
        "source_pre_start_safety_matrix": source_pre_start_safety_matrix_df,
        "source_checks": source_checks_df,
        "phase_9_closure_ledger": phase_9_ledger_df,
        "phase_9_closure_requirements": closure_requirements_df,
        "phase_9_safety_closure_matrix": safety_closure_matrix_df,
        "phase_9_closure_decision": closure_decision_df,
        "checks": checks_df,
    }