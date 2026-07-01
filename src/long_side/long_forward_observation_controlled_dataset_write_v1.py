from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from src.long_side.long_forward_observation_dataset_bootstrap_v1 import (
    DATASET_COLUMNS,
    OFFICIAL_DATASET_PATH,
    PRIMARY_RESEARCH_CANDIDATE,
    SECONDARY_REFERENCE_CANDIDATE,
)
from src.long_side.long_forward_observation_persistence_guard_v1 import (
    validate_long_forward_observation_persistence_guard,
)


REPORTS_DIR = Path("reports/phase_9_7_long_forward_observation_controlled_dataset_write_v1")

PHASE_9_6_PERSISTENCE_GUARD_DOC_PATH = Path(
    "docs/PHASE_9_LONG_FORWARD_OBSERVATION_PERSISTENCE_GUARD.md"
)
PHASE_9_7_CONTROLLED_DATASET_WRITE_DOC_PATH = Path(
    "docs/PHASE_9_LONG_FORWARD_OBSERVATION_CONTROLLED_DATASET_WRITE.md"
)

CONTROLLED_WRITE_STATUS = "LONG_FORWARD_OBSERVATION_CONTROLLED_REPORT_WRITE_ONLY"
CONTROLLED_WRITE_SOURCE = "PHASE_9_7_CONTROLLED_REPORT_ONLY_WRITE"

SAFETY_FLAGS = {
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


def select_valid_controlled_attempt(
    persistence_attempts_df: pd.DataFrame,
) -> pd.DataFrame:
    if persistence_attempts_df.empty:
        return pd.DataFrame()

    selected_df = persistence_attempts_df[
        persistence_attempts_df["attempt_scenario"]
        .astype(str)
        .eq("VALID_CONTROLLED_ROW_ATTEMPTS_WRITE")
    ].copy()

    return selected_df.head(1)


def build_source_provenance_lookup(source_bootstrap_ledger_df: pd.DataFrame) -> dict[str, dict[str, str]]:
    provenance: dict[str, dict[str, str]] = {}

    if source_bootstrap_ledger_df.empty:
        return provenance

    for _, row in source_bootstrap_ledger_df.iterrows():
        observation_id = str(row.get("observation_id", "")).strip()

        if not observation_id:
            continue

        source_validation_decision = str(
            row.get("source_validation_decision", "")
        ).strip()

        source_validation_status = str(
            row.get("source_validation_status", "")
        ).strip()

        source_bootstrap_action = str(row.get("bootstrap_action", "")).strip()
        source_bootstrap_decision = str(row.get("bootstrap_decision", "")).strip()

        if source_validation_status == "":
            if source_validation_decision == "VALIDATED_FOR_FUTURE_FORWARD_OBSERVATION_INPUT":
                source_validation_status = "CONTROLLED_VALID_INPUT_ONLY_DERIVED_FROM_BOOTSTRAP_LEDGER"
            elif source_validation_decision == "REJECTED_LONG_FORWARD_JOURNAL_INPUT":
                source_validation_status = "CONTROLLED_REJECTED_INPUT_DERIVED_FROM_BOOTSTRAP_LEDGER"
            else:
                source_validation_status = "SOURCE_STATUS_DERIVED_FROM_BOOTSTRAP_LEDGER"

        provenance[observation_id] = {
            "source_validation_decision": source_validation_decision,
            "source_validation_status": source_validation_status,
            "source_bootstrap_action": source_bootstrap_action,
            "source_bootstrap_decision": source_bootstrap_decision,
        }

    return provenance


def build_controlled_report_dataset_write(
    selected_attempt_df: pd.DataFrame,
    source_bootstrap_ledger_df: pd.DataFrame,
) -> pd.DataFrame:
    if selected_attempt_df.empty:
        return pd.DataFrame()

    provenance_lookup = build_source_provenance_lookup(source_bootstrap_ledger_df)
    rows: list[dict[str, Any]] = []

    for _, source_row in selected_attempt_df.iterrows():
        observation_id = str(source_row.get("observation_id", "")).strip()
        provenance = provenance_lookup.get(observation_id, {})

        row: dict[str, Any] = {}

        for column in DATASET_COLUMNS:
            row[column] = source_row.get(column, "")

        row["dataset_status"] = CONTROLLED_WRITE_STATUS
        row["evidence_source"] = CONTROLLED_WRITE_SOURCE
        row["evidence_row_status"] = "CONTROLLED_SYNTHETIC_REPORT_ONLY"
        row["accepted_as_real_evidence"] = False
        row["evidence_write_allowed"] = False
        row["evidence_write_performed"] = False
        row["forward_observation_started"] = False
        row["signal_generation_enabled"] = False
        row["execution_allowed"] = False
        row["live_alert_sent"] = False
        row["paper_trade_submitted"] = False
        row["real_capital_used"] = False
        row["persistence_guard_status"] = "PERSISTENCE_GUARD_CONFIRMED_REPORT_ONLY"

        row["controlled_write_id"] = "PHASE_9_7_CONTROLLED_REPORT_WRITE_001"
        row["controlled_write_status"] = CONTROLLED_WRITE_STATUS
        row["controlled_write_scope"] = "REPORTS_ONLY_NOT_OFFICIAL_DATASET"
        row["controlled_report_write_allowed"] = True
        row["controlled_report_write_performed"] = True
        row["official_dataset_write_allowed"] = False
        row["official_dataset_write_performed"] = False
        row["official_dataset_path"] = str(OFFICIAL_DATASET_PATH)
        row["controlled_report_path"] = str(
            REPORTS_DIR / "long_forward_observation_controlled_report_dataset_rows_v1.csv"
        )
        row["source_validation_decision"] = provenance.get(
            "source_validation_decision",
            "",
        )
        row["source_validation_status"] = provenance.get(
            "source_validation_status",
            "",
        )
        row["source_bootstrap_action"] = provenance.get(
            "source_bootstrap_action",
            "",
        )
        row["source_bootstrap_decision"] = provenance.get(
            "source_bootstrap_decision",
            "",
        )
        row["controlled_write_note"] = (
            "Synthetic controlled row written only to reports. "
            "Not official evidence. Not execution eligible."
        )

        rows.append(row)

    return pd.DataFrame(rows)


def build_controlled_write_audit(
    controlled_report_write_df: pd.DataFrame,
    official_dataset_exists_before: bool,
    official_dataset_exists_after: bool,
) -> pd.DataFrame:
    checks: list[dict[str, Any]] = []

    if controlled_report_write_df.empty:
        return pd.DataFrame(
            [
                {
                    "audit_check": "controlled_report_write_row_exists",
                    "passed": False,
                    "details": "controlled_report_write_rows=0",
                }
            ]
        )

    row = controlled_report_write_df.iloc[0]

    controlled_report_write_rows = int(len(controlled_report_write_df))
    controlled_report_write_performed = safe_bool(
        row.get("controlled_report_write_performed", False)
    )
    official_dataset_write_performed = safe_bool(
        row.get("official_dataset_write_performed", True),
        default=True,
    )
    accepted_as_real_evidence = safe_bool(
        row.get("accepted_as_real_evidence", True),
        default=True,
    )
    evidence_write_performed = safe_bool(
        row.get("evidence_write_performed", True),
        default=True,
    )
    execution_allowed = safe_bool(row.get("execution_allowed", True), default=True)
    live_alert_sent = safe_bool(row.get("live_alert_sent", True), default=True)
    paper_trade_submitted = safe_bool(
        row.get("paper_trade_submitted", True),
        default=True,
    )
    real_capital_used = safe_bool(row.get("real_capital_used", True), default=True)
    forward_observation_started = safe_bool(
        row.get("forward_observation_started", True),
        default=True,
    )
    signal_generation_enabled = safe_bool(
        row.get("signal_generation_enabled", True),
        default=True,
    )

    source_validation_decision = str(row.get("source_validation_decision", "")).strip()
    source_validation_status = str(row.get("source_validation_status", "")).strip()
    candidate_id = str(row.get("candidate_id", "")).strip()

    checks.append(
        {
            "audit_check": "controlled_report_write_row_exists",
            "passed": controlled_report_write_rows == 1,
            "details": f"controlled_report_write_rows={controlled_report_write_rows}",
        }
    )
    checks.append(
        {
            "audit_check": "controlled_report_write_performed",
            "passed": controlled_report_write_performed,
            "details": f"controlled_report_write_performed={controlled_report_write_performed}",
        }
    )
    checks.append(
        {
            "audit_check": "official_dataset_write_not_performed",
            "passed": not official_dataset_write_performed,
            "details": f"official_dataset_write_performed={official_dataset_write_performed}",
        }
    )
    checks.append(
        {
            "audit_check": "official_dataset_not_created",
            "passed": (
                official_dataset_exists_before is False
                and official_dataset_exists_after is False
            ),
            "details": (
                f"official_dataset_exists_before={official_dataset_exists_before},"
                f"official_dataset_exists_after={official_dataset_exists_after}"
            ),
        }
    )
    checks.append(
        {
            "audit_check": "controlled_row_not_real_evidence",
            "passed": not accepted_as_real_evidence and not evidence_write_performed,
            "details": (
                f"accepted_as_real_evidence={accepted_as_real_evidence},"
                f"evidence_write_performed={evidence_write_performed}"
            ),
        }
    )
    checks.append(
        {
            "audit_check": "controlled_row_primary_candidate",
            "passed": candidate_id == PRIMARY_RESEARCH_CANDIDATE,
            "details": f"candidate_id={candidate_id}",
        }
    )
    checks.append(
        {
            "audit_check": "source_validation_decision_present",
            "passed": source_validation_decision != "",
            "details": f"source_validation_decision={source_validation_decision}",
        }
    )
    checks.append(
        {
            "audit_check": "source_validation_status_present",
            "passed": source_validation_status != "",
            "details": f"source_validation_status={source_validation_status}",
        }
    )
    checks.append(
        {
            "audit_check": "execution_alert_paper_capital_flags_false",
            "passed": (
                not execution_allowed
                and not live_alert_sent
                and not paper_trade_submitted
                and not real_capital_used
            ),
            "details": (
                f"execution_allowed={execution_allowed},"
                f"live_alert_sent={live_alert_sent},"
                f"paper_trade_submitted={paper_trade_submitted},"
                f"real_capital_used={real_capital_used}"
            ),
        }
    )
    checks.append(
        {
            "audit_check": "forward_observation_and_signal_generation_false",
            "passed": (
                not forward_observation_started
                and not signal_generation_enabled
            ),
            "details": (
                f"forward_observation_started={forward_observation_started},"
                f"signal_generation_enabled={signal_generation_enabled}"
            ),
        }
    )

    return pd.DataFrame(checks)


def build_controlled_dataset_write_summary_table(
    controlled_report_write_df: pd.DataFrame,
    controlled_write_audit_df: pd.DataFrame,
    official_dataset_exists_before: bool,
    official_dataset_exists_after: bool,
) -> pd.DataFrame:
    controlled_report_write_rows = int(len(controlled_report_write_df))
    audit_passed = (
        not controlled_write_audit_df.empty
        and controlled_write_audit_df["passed"].astype(bool).all()
    )

    source_validation_decision_present = False
    source_validation_status_present = False
    controlled_row_source_candidate = ""

    if not controlled_report_write_df.empty:
        row = controlled_report_write_df.iloc[0]
        source_validation_decision_present = (
            str(row.get("source_validation_decision", "")).strip() != ""
        )
        source_validation_status_present = (
            str(row.get("source_validation_status", "")).strip() != ""
        )
        controlled_row_source_candidate = str(row.get("candidate_id", "")).strip()

    return pd.DataFrame(
        [
            {
                "controlled_dataset_write_id": "PHASE_9_7_CONTROLLED_DATASET_WRITE_001",
                "controlled_write_status": CONTROLLED_WRITE_STATUS,
                "controlled_report_write_rows": controlled_report_write_rows,
                "controlled_report_write_performed": controlled_report_write_rows == 1,
                "controlled_report_write_only": True,
                "controlled_row_source_candidate": controlled_row_source_candidate,
                "source_validation_decision_present": source_validation_decision_present,
                "source_validation_status_present": source_validation_status_present,
                "controlled_write_audit_rows": int(len(controlled_write_audit_df)),
                "controlled_write_audit_passed": audit_passed,
                "official_dataset_path": str(OFFICIAL_DATASET_PATH),
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
                "execution_allowed": False,
                "live_alerts_allowed": False,
                "real_capital_allowed": False,
                "automation_allowed": False,
            }
        ]
    )


def validate_long_forward_observation_controlled_dataset_write() -> dict[str, pd.DataFrame]:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    checks: list[dict[str, Any]] = []

    phase_anchors = {
        "phase_9_6_persistence_guard_doc_exists": PHASE_9_6_PERSISTENCE_GUARD_DOC_PATH,
        "phase_9_7_controlled_dataset_write_doc_exists": (
            PHASE_9_7_CONTROLLED_DATASET_WRITE_DOC_PATH
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

    phase_9_6_result = validate_long_forward_observation_persistence_guard()

    phase_9_6_summary_df = phase_9_6_result["summary"]
    source_persistence_guard_summary_df = phase_9_6_result["persistence_guard_summary"]
    source_persistence_attempts_df = phase_9_6_result["persistence_attempts"]
    source_evaluated_attempts_df = phase_9_6_result["evaluated_attempts"]
    source_guard_audit_df = phase_9_6_result["guard_audit"]
    source_bootstrap_ledger_df = phase_9_6_result["source_bootstrap_ledger"]

    phase_9_6_validation_passed = (
        not phase_9_6_summary_df.empty
        and bool(phase_9_6_summary_df.iloc[0].get("validation_passed", False))
    )

    persistence_guard_defined = (
        not phase_9_6_summary_df.empty
        and bool(
            phase_9_6_summary_df.iloc[0].get(
                "long_forward_observation_persistence_guard_defined",
                False,
            )
        )
    )

    selected_attempt_df = select_valid_controlled_attempt(
        persistence_attempts_df=source_persistence_attempts_df,
    )

    controlled_report_write_df = build_controlled_report_dataset_write(
        selected_attempt_df=selected_attempt_df,
        source_bootstrap_ledger_df=source_bootstrap_ledger_df,
    )

    official_dataset_exists_after = OFFICIAL_DATASET_PATH.exists()

    controlled_write_audit_df = build_controlled_write_audit(
        controlled_report_write_df=controlled_report_write_df,
        official_dataset_exists_before=official_dataset_exists_before,
        official_dataset_exists_after=official_dataset_exists_after,
    )

    controlled_dataset_write_summary_table_df = build_controlled_dataset_write_summary_table(
        controlled_report_write_df=controlled_report_write_df,
        controlled_write_audit_df=controlled_write_audit_df,
        official_dataset_exists_before=official_dataset_exists_before,
        official_dataset_exists_after=official_dataset_exists_after,
    )

    checks.append(
        build_check(
            check_group="phase_dependency",
            check_name="phase_9_6_validation_passed",
            passed=phase_9_6_validation_passed,
            severity="INFO" if phase_9_6_validation_passed else "ERROR",
            details=(
                str(phase_9_6_summary_df.iloc[0].get("validation_decision", ""))
                if not phase_9_6_summary_df.empty
                else "Missing Phase 9.6 summary."
            ),
        )
    )

    checks.append(
        build_check(
            check_group="phase_dependency",
            check_name="long_forward_observation_persistence_guard_defined",
            passed=persistence_guard_defined,
            severity="INFO" if persistence_guard_defined else "ERROR",
            details=f"persistence_guard_defined={persistence_guard_defined}",
        )
    )

    source_guard_valid = (
        not phase_9_6_summary_df.empty
        and bool(phase_9_6_summary_df.iloc[0].get("guard_audit_passed", False))
        and int(phase_9_6_summary_df.iloc[0].get("persistence_blocked_rows", -1)) == 3
        and int(phase_9_6_summary_df.iloc[0].get("persistence_allowed_rows", -1)) == 0
    )

    checks.append(
        build_check(
            check_group="source_guard",
            check_name="source_persistence_guard_validated",
            passed=source_guard_valid,
            severity="INFO" if source_guard_valid else "ERROR",
            details="Phase 9.6 guard blocked all controlled attempted writes.",
        )
    )

    controlled_report_write_rows = int(len(controlled_report_write_df))

    checks.append(
        build_check(
            check_group="controlled_write",
            check_name="controlled_report_write_row_created",
            passed=controlled_report_write_rows == 1,
            severity="INFO" if controlled_report_write_rows == 1 else "ERROR",
            details=f"controlled_report_write_rows={controlled_report_write_rows}",
        )
    )

    controlled_report_write_performed = (
        not controlled_report_write_df.empty
        and controlled_report_write_df["controlled_report_write_performed"]
        .astype(bool)
        .all()
    )

    checks.append(
        build_check(
            check_group="controlled_write",
            check_name="controlled_report_write_performed",
            passed=controlled_report_write_performed,
            severity="INFO" if controlled_report_write_performed else "ERROR",
            details=f"controlled_report_write_performed={controlled_report_write_performed}",
        )
    )

    source_validation_decision_present = (
        not controlled_report_write_df.empty
        and controlled_report_write_df["source_validation_decision"]
        .fillna("")
        .astype(str)
        .str.strip()
        .ne("")
        .all()
    )

    source_validation_status_present = (
        not controlled_report_write_df.empty
        and controlled_report_write_df["source_validation_status"]
        .fillna("")
        .astype(str)
        .str.strip()
        .ne("")
        .all()
    )

    checks.append(
        build_check(
            check_group="provenance",
            check_name="source_validation_decision_present",
            passed=source_validation_decision_present,
            severity="INFO" if source_validation_decision_present else "ERROR",
            details=f"source_validation_decision_present={source_validation_decision_present}",
        )
    )

    checks.append(
        build_check(
            check_group="provenance",
            check_name="source_validation_status_present",
            passed=source_validation_status_present,
            severity="INFO" if source_validation_status_present else "ERROR",
            details=f"source_validation_status_present={source_validation_status_present}",
        )
    )

    controlled_primary_only = (
        not controlled_report_write_df.empty
        and controlled_report_write_df["candidate_id"]
        .astype(str)
        .eq(PRIMARY_RESEARCH_CANDIDATE)
        .all()
    )

    checks.append(
        build_check(
            check_group="candidate_scope",
            check_name="controlled_write_primary_candidate_only",
            passed=controlled_primary_only,
            severity="INFO" if controlled_primary_only else "ERROR",
            details=(
                "controlled_candidates="
                + ",".join(controlled_report_write_df["candidate_id"].astype(str).unique())
                if not controlled_report_write_df.empty
                else "controlled_candidates="
            ),
        )
    )

    official_dataset_not_written = (
        not controlled_report_write_df.empty
        and not controlled_report_write_df["official_dataset_write_performed"]
        .astype(bool)
        .any()
        and not official_dataset_exists_before
        and not official_dataset_exists_after
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

    not_real_evidence = (
        not controlled_report_write_df.empty
        and not controlled_report_write_df["accepted_as_real_evidence"]
        .astype(bool)
        .any()
        and not controlled_report_write_df["evidence_write_allowed"]
        .astype(bool)
        .any()
        and not controlled_report_write_df["evidence_write_performed"]
        .astype(bool)
        .any()
    )

    checks.append(
        build_check(
            check_group="scope_control",
            check_name="controlled_report_row_not_real_evidence",
            passed=not_real_evidence,
            severity="INFO" if not_real_evidence else "ERROR",
            details="Controlled report row is synthetic and not real evidence.",
        )
    )

    no_action_flags = (
        not controlled_report_write_df.empty
        and not controlled_report_write_df["execution_allowed"].astype(bool).any()
        and not controlled_report_write_df["live_alert_sent"].astype(bool).any()
        and not controlled_report_write_df["paper_trade_submitted"]
        .astype(bool)
        .any()
        and not controlled_report_write_df["real_capital_used"].astype(bool).any()
    )

    checks.append(
        build_check(
            check_group="safety_controls",
            check_name="controlled_write_keeps_action_flags_false",
            passed=no_action_flags,
            severity="INFO" if no_action_flags else "ERROR",
            details="No execution, alerts, paper trades, or real capital actions occur.",
        )
    )

    forward_and_signal_disabled = (
        not controlled_report_write_df.empty
        and not controlled_report_write_df["forward_observation_started"]
        .astype(bool)
        .any()
        and not controlled_report_write_df["signal_generation_enabled"]
        .astype(bool)
        .any()
    )

    checks.append(
        build_check(
            check_group="safety_controls",
            check_name="forward_observation_and_signal_generation_disabled",
            passed=forward_and_signal_disabled,
            severity="INFO" if forward_and_signal_disabled else "ERROR",
            details="Forward observation and signal generation remain disabled.",
        )
    )

    controlled_write_audit_passed = (
        not controlled_write_audit_df.empty
        and controlled_write_audit_df["passed"].astype(bool).all()
    )

    checks.append(
        build_check(
            check_group="controlled_write",
            check_name="controlled_write_audit_passed",
            passed=controlled_write_audit_passed,
            severity="INFO" if controlled_write_audit_passed else "ERROR",
            details=(
                "failed_audit_checks="
                + ",".join(
                    controlled_write_audit_df[
                        ~controlled_write_audit_df["passed"].astype(bool)
                    ]["audit_check"].astype(str)
                )
                if not controlled_write_audit_df.empty
                else "failed_audit_checks=all"
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
            check_name="controlled_report_write_only",
            passed=True,
            severity="WARNING",
            details="Phase 9.7 writes only synthetic non-real rows to reports.",
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
            check_name="phase_9_8_recommended_next",
            passed=True,
            severity="INFO",
            details=(
                "Recommended next step: "
                "Phase 9.8 LONG Forward Observation Report Integrity V1."
            ),
        )
    )

    checks_df = pd.DataFrame(checks)

    blocker_count = int(checks_df["blocker"].astype(bool).sum())
    error_count = int(checks_df["severity"].eq("ERROR").sum())
    warning_count = int(checks_df["severity"].eq("WARNING").sum())

    validation_passed = blocker_count == 0 and error_count == 0

    controlled_write_summary = (
        controlled_dataset_write_summary_table_df.iloc[0].to_dict()
        if not controlled_dataset_write_summary_table_df.empty
        else {}
    )

    summary_df = pd.DataFrame(
        [
            {
                "phase": "9.7",
                "long_forward_observation_controlled_dataset_write_defined": True,
                "phase_9_6_validation_passed": phase_9_6_validation_passed,
                "long_forward_observation_persistence_guard_defined": persistence_guard_defined,
                "source_persistence_attempt_rows": int(
                    phase_9_6_summary_df.iloc[0].get("persistence_attempt_rows", 0)
                    if not phase_9_6_summary_df.empty
                    else 0
                ),
                "source_persistence_allowed_rows": int(
                    phase_9_6_summary_df.iloc[0].get("persistence_allowed_rows", 0)
                    if not phase_9_6_summary_df.empty
                    else 0
                ),
                "source_persistence_blocked_rows": int(
                    phase_9_6_summary_df.iloc[0].get("persistence_blocked_rows", 0)
                    if not phase_9_6_summary_df.empty
                    else 0
                ),
                "controlled_report_write_rows": controlled_report_write_rows,
                "controlled_report_write_performed": controlled_report_write_performed,
                "controlled_report_write_only": True,
                "controlled_row_source_candidate": controlled_write_summary.get(
                    "controlled_row_source_candidate",
                    "",
                ),
                "source_validation_decision_present": source_validation_decision_present,
                "source_validation_status_present": source_validation_status_present,
                "controlled_write_audit_rows": int(len(controlled_write_audit_df)),
                "controlled_write_audit_passed": controlled_write_audit_passed,
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
                    "PHASE_9_8_LONG_FORWARD_OBSERVATION_REPORT_INTEGRITY_V1"
                ),
                "estimated_phase_9_progress_percent": 70,
                "total_checks": int(len(checks_df)),
                "warning_count": warning_count,
                "error_count": error_count,
                "blocker_count": blocker_count,
                "validation_passed": validation_passed,
                "validation_decision": (
                    "PHASE_9_7_LONG_FORWARD_OBSERVATION_CONTROLLED_DATASET_WRITE_VALIDATED"
                    if validation_passed
                    else "PHASE_9_7_LONG_FORWARD_OBSERVATION_CONTROLLED_DATASET_WRITE_FAILED"
                ),
            }
        ]
    )

    phase_9_6_summary_df.to_csv(
        REPORTS_DIR / "phase_9_6_source_summary_v1.csv",
        index=False,
    )
    source_persistence_guard_summary_df.to_csv(
        REPORTS_DIR / "phase_9_6_source_persistence_guard_summary_v1.csv",
        index=False,
    )
    source_persistence_attempts_df.to_csv(
        REPORTS_DIR / "phase_9_6_source_persistence_attempts_v1.csv",
        index=False,
    )
    source_evaluated_attempts_df.to_csv(
        REPORTS_DIR / "phase_9_6_source_evaluated_attempts_v1.csv",
        index=False,
    )
    source_guard_audit_df.to_csv(
        REPORTS_DIR / "phase_9_6_source_guard_audit_v1.csv",
        index=False,
    )
    source_bootstrap_ledger_df.to_csv(
        REPORTS_DIR / "phase_9_5_source_bootstrap_ledger_v1.csv",
        index=False,
    )
    selected_attempt_df.to_csv(
        REPORTS_DIR / "long_forward_observation_selected_controlled_attempt_v1.csv",
        index=False,
    )
    controlled_report_write_df.to_csv(
        REPORTS_DIR / "long_forward_observation_controlled_report_dataset_rows_v1.csv",
        index=False,
    )
    controlled_write_audit_df.to_csv(
        REPORTS_DIR / "long_forward_observation_controlled_dataset_write_audit_v1.csv",
        index=False,
    )
    controlled_dataset_write_summary_table_df.to_csv(
        REPORTS_DIR / "long_forward_observation_controlled_dataset_write_summary_table_v1.csv",
        index=False,
    )
    checks_df.to_csv(
        REPORTS_DIR / "long_forward_observation_controlled_dataset_write_checks_v1.csv",
        index=False,
    )
    summary_df.to_csv(
        REPORTS_DIR / "long_forward_observation_controlled_dataset_write_summary_v1.csv",
        index=False,
    )

    return {
        "summary": summary_df,
        "source_phase_9_6_summary": phase_9_6_summary_df,
        "source_persistence_guard_summary": source_persistence_guard_summary_df,
        "source_persistence_attempts": source_persistence_attempts_df,
        "source_evaluated_attempts": source_evaluated_attempts_df,
        "source_guard_audit": source_guard_audit_df,
        "source_bootstrap_ledger": source_bootstrap_ledger_df,
        "selected_controlled_attempt": selected_attempt_df,
        "controlled_report_write": controlled_report_write_df,
        "controlled_write_audit": controlled_write_audit_df,
        "controlled_dataset_write_summary": controlled_dataset_write_summary_table_df,
        "checks": checks_df,
    }