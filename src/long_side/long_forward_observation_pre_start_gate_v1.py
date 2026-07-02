from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from src.long_side.long_forward_observation_dataset_bootstrap_v1 import (
    OFFICIAL_DATASET_PATH,
    PRIMARY_RESEARCH_CANDIDATE,
)
from src.long_side.long_forward_observation_report_integrity_v1 import (
    validate_long_forward_observation_report_integrity,
)


REPORTS_DIR = Path("reports/phase_9_9_long_forward_observation_pre_start_gate_v1")

PHASE_9_8_REPORT_INTEGRITY_DOC_PATH = Path(
    "docs/PHASE_9_LONG_FORWARD_OBSERVATION_REPORT_INTEGRITY.md"
)
PHASE_9_9_PRE_START_GATE_DOC_PATH = Path(
    "docs/PHASE_9_LONG_FORWARD_OBSERVATION_PRE_START_GATE.md"
)

PRE_START_GATE_STATUS = "LONG_FORWARD_OBSERVATION_PRE_START_GATE_ONLY"
READY_DECISION = "PRE_START_GATE_READY_FOR_CONTROLLED_START_REVIEW"
BLOCKED_DECISION = "PRE_START_GATE_BLOCKED"

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


def build_pre_start_gate_criteria(
    phase_9_8_summary_df: pd.DataFrame,
    report_integrity_summary_df: pd.DataFrame,
) -> pd.DataFrame:
    summary = (
        phase_9_8_summary_df.iloc[0].to_dict()
        if not phase_9_8_summary_df.empty
        else {}
    )

    report_summary = (
        report_integrity_summary_df.iloc[0].to_dict()
        if not report_integrity_summary_df.empty
        else {}
    )

    criteria: list[dict[str, Any]] = [
        {
            "criterion_id": "PRE_START_001",
            "criterion_name": "phase_9_8_validation_passed",
            "passed": safe_bool(summary.get("validation_passed", False)),
            "required_value": "True",
            "actual_value": str(summary.get("validation_passed", "")),
            "gate_category": "dependency",
        },
        {
            "criterion_id": "PRE_START_002",
            "criterion_name": "report_integrity_audit_passed",
            "passed": safe_bool(summary.get("report_integrity_audit_passed", False)),
            "required_value": "True",
            "actual_value": str(summary.get("report_integrity_audit_passed", "")),
            "gate_category": "integrity",
        },
        {
            "criterion_id": "PRE_START_003",
            "criterion_name": "schema_compatibility_passed",
            "passed": safe_bool(summary.get("schema_compatibility_passed", False)),
            "required_value": "True",
            "actual_value": str(summary.get("schema_compatibility_passed", "")),
            "gate_category": "integrity",
        },
        {
            "criterion_id": "PRE_START_004",
            "criterion_name": "provenance_integrity_passed",
            "passed": safe_bool(summary.get("provenance_integrity_passed", False)),
            "required_value": "True",
            "actual_value": str(summary.get("provenance_integrity_passed", "")),
            "gate_category": "integrity",
        },
        {
            "criterion_id": "PRE_START_005",
            "criterion_name": "safety_integrity_passed",
            "passed": safe_bool(summary.get("safety_integrity_passed", False)),
            "required_value": "True",
            "actual_value": str(summary.get("safety_integrity_passed", "")),
            "gate_category": "integrity",
        },
        {
            "criterion_id": "PRE_START_006",
            "criterion_name": "report_only_integrity_passed",
            "passed": safe_bool(summary.get("report_only_integrity_passed", False)),
            "required_value": "True",
            "actual_value": str(summary.get("report_only_integrity_passed", "")),
            "gate_category": "integrity",
        },
        {
            "criterion_id": "PRE_START_007",
            "criterion_name": "controlled_report_write_rows_one",
            "passed": int(summary.get("controlled_report_write_rows", -1)) == 1,
            "required_value": "1",
            "actual_value": str(summary.get("controlled_report_write_rows", "")),
            "gate_category": "controlled_report",
        },
        {
            "criterion_id": "PRE_START_008",
            "criterion_name": "controlled_report_write_only",
            "passed": safe_bool(summary.get("controlled_report_write_only", False)),
            "required_value": "True",
            "actual_value": str(summary.get("controlled_report_write_only", "")),
            "gate_category": "controlled_report",
        },
        {
            "criterion_id": "PRE_START_009",
            "criterion_name": "controlled_row_source_candidate_primary",
            "passed": str(summary.get("controlled_row_source_candidate", "")).strip()
            == PRIMARY_RESEARCH_CANDIDATE,
            "required_value": PRIMARY_RESEARCH_CANDIDATE,
            "actual_value": str(summary.get("controlled_row_source_candidate", "")),
            "gate_category": "candidate_scope",
        },
        {
            "criterion_id": "PRE_START_010",
            "criterion_name": "official_dataset_file_not_created",
            "passed": (
                safe_bool(summary.get("official_dataset_exists_before", True), default=True)
                is False
                and safe_bool(
                    summary.get("official_dataset_exists_after", True),
                    default=True,
                )
                is False
            ),
            "required_value": "False/False",
            "actual_value": (
                f"{summary.get('official_dataset_exists_before', '')}/"
                f"{summary.get('official_dataset_exists_after', '')}"
            ),
            "gate_category": "official_dataset_guard",
        },
        {
            "criterion_id": "PRE_START_011",
            "criterion_name": "official_dataset_write_not_performed",
            "passed": safe_bool(
                summary.get("official_dataset_write_performed", True),
                default=True,
            )
            is False,
            "required_value": "False",
            "actual_value": str(summary.get("official_dataset_write_performed", "")),
            "gate_category": "official_dataset_guard",
        },
        {
            "criterion_id": "PRE_START_012",
            "criterion_name": "official_evidence_rows_written_zero",
            "passed": int(summary.get("official_evidence_rows_written", -1)) == 0,
            "required_value": "0",
            "actual_value": str(summary.get("official_evidence_rows_written", "")),
            "gate_category": "official_dataset_guard",
        },
        {
            "criterion_id": "PRE_START_013",
            "criterion_name": "forward_observation_not_started",
            "passed": safe_bool(
                summary.get("forward_observation_started", True),
                default=True,
            )
            is False,
            "required_value": "False",
            "actual_value": str(summary.get("forward_observation_started", "")),
            "gate_category": "safety",
        },
        {
            "criterion_id": "PRE_START_014",
            "criterion_name": "signal_generation_disabled",
            "passed": safe_bool(
                summary.get("signal_generation_enabled", True),
                default=True,
            )
            is False,
            "required_value": "False",
            "actual_value": str(summary.get("signal_generation_enabled", "")),
            "gate_category": "safety",
        },
        {
            "criterion_id": "PRE_START_015",
            "criterion_name": "execution_disabled",
            "passed": safe_bool(summary.get("execution_allowed", True), default=True)
            is False,
            "required_value": "False",
            "actual_value": str(summary.get("execution_allowed", "")),
            "gate_category": "safety",
        },
        {
            "criterion_id": "PRE_START_016",
            "criterion_name": "report_integrity_summary_consistent",
            "passed": (
                not report_integrity_summary_df.empty
                and safe_bool(
                    report_summary.get("report_integrity_audit_passed", False)
                )
                and str(
                    report_summary.get("controlled_row_source_candidate", "")
                ).strip()
                == PRIMARY_RESEARCH_CANDIDATE
            ),
            "required_value": "True",
            "actual_value": str(
                report_summary.get("report_integrity_audit_passed", "")
            ),
            "gate_category": "summary_consistency",
        },
    ]

    return pd.DataFrame(criteria)


def build_pre_start_gate_decision_table(criteria_df: pd.DataFrame) -> pd.DataFrame:
    total_criteria = int(len(criteria_df))
    passed_criteria = int(criteria_df["passed"].astype(bool).sum()) if total_criteria else 0
    failed_criteria = total_criteria - passed_criteria
    pre_start_gate_passed = total_criteria > 0 and failed_criteria == 0

    gate_decision = READY_DECISION if pre_start_gate_passed else BLOCKED_DECISION

    failed_names = ""

    if not criteria_df.empty:
        failed_names = ",".join(
            criteria_df[~criteria_df["passed"].astype(bool)]["criterion_name"]
            .astype(str)
            .tolist()
        )

    return pd.DataFrame(
        [
            {
                "pre_start_gate_id": "PHASE_9_9_PRE_START_GATE_001",
                "pre_start_gate_status": PRE_START_GATE_STATUS,
                "pre_start_gate_passed": pre_start_gate_passed,
                "pre_start_gate_decision": gate_decision,
                "total_criteria": total_criteria,
                "passed_criteria": passed_criteria,
                "failed_criteria": failed_criteria,
                "failed_criteria_names": failed_names,
                "future_controlled_start_review_allowed": pre_start_gate_passed,
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
            }
        ]
    )


def build_pre_start_gate_safety_matrix() -> pd.DataFrame:
    rows: list[dict[str, Any]] = []

    for flag_name, flag_value in SAFETY_FLAGS.items():
        rows.append(
            {
                "safety_flag": flag_name,
                "required_value": False,
                "actual_value": flag_value,
                "passed": flag_value is False,
                "gate_status": PRE_START_GATE_STATUS,
            }
        )

    rows.append(
        {
            "safety_flag": "official_evidence_rows_written",
            "required_value": 0,
            "actual_value": 0,
            "passed": True,
            "gate_status": PRE_START_GATE_STATUS,
        }
    )

    return pd.DataFrame(rows)


def validate_long_forward_observation_pre_start_gate() -> dict[str, pd.DataFrame]:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    checks: list[dict[str, Any]] = []

    phase_anchors = {
        "phase_9_8_report_integrity_doc_exists": PHASE_9_8_REPORT_INTEGRITY_DOC_PATH,
        "phase_9_9_pre_start_gate_doc_exists": PHASE_9_9_PRE_START_GATE_DOC_PATH,
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

    phase_9_8_result = validate_long_forward_observation_report_integrity()

    phase_9_8_summary_df = phase_9_8_result["summary"]
    source_report_integrity_summary_df = phase_9_8_result["report_integrity_summary"]
    source_combined_integrity_audit_df = phase_9_8_result["combined_integrity_audit"]
    source_checks_df = phase_9_8_result["checks"]

    phase_9_8_validation_passed = (
        not phase_9_8_summary_df.empty
        and bool(phase_9_8_summary_df.iloc[0].get("validation_passed", False))
    )

    report_integrity_defined = (
        not phase_9_8_summary_df.empty
        and bool(
            phase_9_8_summary_df.iloc[0].get(
                "long_forward_observation_report_integrity_defined",
                False,
            )
        )
    )

    pre_start_criteria_df = build_pre_start_gate_criteria(
        phase_9_8_summary_df=phase_9_8_summary_df,
        report_integrity_summary_df=source_report_integrity_summary_df,
    )

    pre_start_gate_decision_df = build_pre_start_gate_decision_table(
        criteria_df=pre_start_criteria_df,
    )

    pre_start_safety_matrix_df = build_pre_start_gate_safety_matrix()

    official_dataset_exists_after = OFFICIAL_DATASET_PATH.exists()

    decision = (
        pre_start_gate_decision_df.iloc[0].to_dict()
        if not pre_start_gate_decision_df.empty
        else {}
    )

    pre_start_gate_passed = safe_bool(
        decision.get("pre_start_gate_passed", False),
        default=False,
    )
    pre_start_gate_decision = str(decision.get("pre_start_gate_decision", ""))

    checks.append(
        build_check(
            check_group="phase_dependency",
            check_name="phase_9_8_validation_passed",
            passed=phase_9_8_validation_passed,
            severity="INFO" if phase_9_8_validation_passed else "ERROR",
            details=(
                str(phase_9_8_summary_df.iloc[0].get("validation_decision", ""))
                if not phase_9_8_summary_df.empty
                else "Missing Phase 9.8 summary."
            ),
        )
    )

    checks.append(
        build_check(
            check_group="phase_dependency",
            check_name="long_forward_observation_report_integrity_defined",
            passed=report_integrity_defined,
            severity="INFO" if report_integrity_defined else "ERROR",
            details=f"report_integrity_defined={report_integrity_defined}",
        )
    )

    checks.append(
        build_check(
            check_group="pre_start_gate",
            check_name="pre_start_criteria_all_passed",
            passed=pre_start_gate_passed,
            severity="INFO" if pre_start_gate_passed else "ERROR",
            details=f"failed_criteria={decision.get('failed_criteria_names', '')}",
        )
    )

    checks.append(
        build_check(
            check_group="pre_start_gate",
            check_name="pre_start_gate_decision_ready_for_review",
            passed=pre_start_gate_decision == READY_DECISION,
            severity="INFO" if pre_start_gate_decision == READY_DECISION else "ERROR",
            details=f"pre_start_gate_decision={pre_start_gate_decision}",
        )
    )

    future_controlled_start_review_allowed = safe_bool(
        decision.get("future_controlled_start_review_allowed", False)
    )

    checks.append(
        build_check(
            check_group="pre_start_gate",
            check_name="future_controlled_start_review_allowed",
            passed=future_controlled_start_review_allowed,
            severity="WARNING" if future_controlled_start_review_allowed else "ERROR",
            details=(
                "This allows only future review, not active observation, "
                "alerts, paper trading, or execution."
            ),
        )
    )

    start_allowed = safe_bool(
        decision.get("forward_observation_start_allowed", True),
        default=True,
    )

    checks.append(
        build_check(
            check_group="safety_controls",
            check_name="forward_observation_start_not_allowed",
            passed=start_allowed is False,
            severity="INFO" if start_allowed is False else "ERROR",
            details=f"forward_observation_start_allowed={start_allowed}",
        )
    )

    official_dataset_not_written = (
        official_dataset_exists_before is False
        and official_dataset_exists_after is False
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
        not pre_start_safety_matrix_df.empty
        and pre_start_safety_matrix_df["passed"].astype(bool).all()
    )

    checks.append(
        build_check(
            check_group="safety_controls",
            check_name="pre_start_safety_matrix_passed",
            passed=safety_matrix_passed,
            severity="INFO" if safety_matrix_passed else "ERROR",
            details=(
                "failed_safety_flags="
                + ",".join(
                    pre_start_safety_matrix_df[
                        ~pre_start_safety_matrix_df["passed"].astype(bool)
                    ]["safety_flag"].astype(str)
                )
                if not pre_start_safety_matrix_df.empty
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
            check_name="pre_start_gate_only",
            passed=True,
            severity="WARNING",
            details="Phase 9.9 defines a pre-start gate only.",
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
            check_group="phase_transition",
            check_name="phase_9_10_recommended_next",
            passed=True,
            severity="INFO",
            details=(
                "Recommended next step: "
                "Phase 9.10 LONG Forward Observation Phase Closure V1."
            ),
        )
    )

    checks_df = pd.DataFrame(checks)

    blocker_count = int(checks_df["blocker"].astype(bool).sum())
    error_count = int(checks_df["severity"].eq("ERROR").sum())
    warning_count = int(checks_df["severity"].eq("WARNING").sum())

    validation_passed = blocker_count == 0 and error_count == 0

    phase_9_8_summary = (
        phase_9_8_summary_df.iloc[0].to_dict()
        if not phase_9_8_summary_df.empty
        else {}
    )

    summary_df = pd.DataFrame(
        [
            {
                "phase": "9.9",
                "long_forward_observation_pre_start_gate_defined": True,
                "phase_9_8_validation_passed": phase_9_8_validation_passed,
                "long_forward_observation_report_integrity_defined": (
                    report_integrity_defined
                ),
                "report_integrity_audit_passed": safe_bool(
                    phase_9_8_summary.get("report_integrity_audit_passed", False)
                ),
                "schema_compatibility_passed": safe_bool(
                    phase_9_8_summary.get("schema_compatibility_passed", False)
                ),
                "provenance_integrity_passed": safe_bool(
                    phase_9_8_summary.get("provenance_integrity_passed", False)
                ),
                "safety_integrity_passed": safe_bool(
                    phase_9_8_summary.get("safety_integrity_passed", False)
                ),
                "report_only_integrity_passed": safe_bool(
                    phase_9_8_summary.get("report_only_integrity_passed", False)
                ),
                "controlled_report_write_rows": int(
                    phase_9_8_summary.get("controlled_report_write_rows", 0)
                ),
                "controlled_report_write_only": safe_bool(
                    phase_9_8_summary.get("controlled_report_write_only", False)
                ),
                "controlled_row_source_candidate": str(
                    phase_9_8_summary.get("controlled_row_source_candidate", "")
                ),
                "pre_start_criteria_rows": int(len(pre_start_criteria_df)),
                "pre_start_gate_passed": pre_start_gate_passed,
                "pre_start_gate_decision": pre_start_gate_decision,
                "future_controlled_start_review_allowed": (
                    future_controlled_start_review_allowed
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
                "recommended_next_phase": (
                    "PHASE_9_10_LONG_FORWARD_OBSERVATION_PHASE_CLOSURE_V1"
                ),
                "estimated_phase_9_progress_percent": 90,
                "total_checks": int(len(checks_df)),
                "warning_count": warning_count,
                "error_count": error_count,
                "blocker_count": blocker_count,
                "validation_passed": validation_passed,
                "validation_decision": (
                    "PHASE_9_9_LONG_FORWARD_OBSERVATION_PRE_START_GATE_VALIDATED"
                    if validation_passed
                    else "PHASE_9_9_LONG_FORWARD_OBSERVATION_PRE_START_GATE_FAILED"
                ),
            }
        ]
    )

    phase_9_8_summary_df.to_csv(
        REPORTS_DIR / "phase_9_8_source_summary_v1.csv",
        index=False,
    )
    source_report_integrity_summary_df.to_csv(
        REPORTS_DIR / "phase_9_8_source_report_integrity_summary_v1.csv",
        index=False,
    )
    source_combined_integrity_audit_df.to_csv(
        REPORTS_DIR / "phase_9_8_source_combined_integrity_audit_v1.csv",
        index=False,
    )
    source_checks_df.to_csv(
        REPORTS_DIR / "phase_9_8_source_checks_v1.csv",
        index=False,
    )
    pre_start_criteria_df.to_csv(
        REPORTS_DIR / "long_forward_observation_pre_start_criteria_v1.csv",
        index=False,
    )
    pre_start_gate_decision_df.to_csv(
        REPORTS_DIR / "long_forward_observation_pre_start_gate_decision_v1.csv",
        index=False,
    )
    pre_start_safety_matrix_df.to_csv(
        REPORTS_DIR / "long_forward_observation_pre_start_safety_matrix_v1.csv",
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
        "source_phase_9_8_summary": phase_9_8_summary_df,
        "source_report_integrity_summary": source_report_integrity_summary_df,
        "source_combined_integrity_audit": source_combined_integrity_audit_df,
        "source_checks": source_checks_df,
        "pre_start_criteria": pre_start_criteria_df,
        "pre_start_gate_decision": pre_start_gate_decision_df,
        "pre_start_safety_matrix": pre_start_safety_matrix_df,
        "checks": checks_df,
    }