from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from src.long_side.long_forward_observation_dataset_bootstrap_v1 import (
    DATASET_COLUMNS,
    DATASET_STATUS,
    OFFICIAL_DATASET_PATH,
    PERSISTENCE_GUARD_STATUS,
    PRIMARY_RESEARCH_CANDIDATE,
    SECONDARY_REFERENCE_CANDIDATE,
    validate_long_forward_observation_dataset_bootstrap,
)


REPORTS_DIR = Path("reports/phase_9_6_long_forward_observation_persistence_guard_v1")

PHASE_9_5_DATASET_BOOTSTRAP_DOC_PATH = Path(
    "docs/PHASE_9_LONG_FORWARD_OBSERVATION_DATASET_BOOTSTRAP.md"
)
PHASE_9_6_PERSISTENCE_GUARD_DOC_PATH = Path(
    "docs/PHASE_9_LONG_FORWARD_OBSERVATION_PERSISTENCE_GUARD.md"
)

PERSISTENCE_GUARD_RUN_STATUS = "LONG_FORWARD_OBSERVATION_PERSISTENCE_GUARD_ONLY"

SAFETY_FLAGS = {
    "forward_observation_started": False,
    "signal_generation_enabled": False,
    "real_forward_signals_recorded": False,
    "journal_real_rows_accepted": False,
    "real_forward_dataset_created": False,
    "official_dataset_write_performed": False,
    "evidence_write_performed": False,
    "evidence_persistence_allowed": False,
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


def build_attempt_from_source_row(
    source_row: pd.Series,
    attempt_id: str,
    scenario_name: str,
    attempt_note: str,
    force_dangerous_flags: bool = False,
) -> dict[str, Any]:
    row: dict[str, Any] = {}

    for column in DATASET_COLUMNS:
        row[column] = source_row.get(column, "")

    row["dataset_status"] = DATASET_STATUS
    row["evidence_source"] = "PHASE_9_6_CONTROLLED_ATTEMPTED_WRITE"
    row["evidence_row_status"] = "ATTEMPTED_WRITE_BLOCKED_BY_GUARD"
    row["persistence_guard_status"] = PERSISTENCE_GUARD_STATUS
    row["accepted_as_real_evidence"] = False
    row["evidence_write_allowed"] = False
    row["evidence_write_performed"] = False
    row["forward_observation_started"] = False
    row["signal_generation_enabled"] = False
    row["execution_allowed"] = False
    row["live_alert_sent"] = False
    row["paper_trade_submitted"] = False
    row["real_capital_used"] = False

    if force_dangerous_flags:
        row["accepted_as_real_evidence"] = True
        row["evidence_write_allowed"] = True
        row["evidence_write_performed"] = True
        row["forward_observation_started"] = True
        row["signal_generation_enabled"] = True
        row["execution_allowed"] = True
        row["live_alert_sent"] = True
        row["paper_trade_submitted"] = True
        row["real_capital_used"] = True

    row["attempt_id"] = attempt_id
    row["attempt_scenario"] = scenario_name
    row["attempt_note"] = attempt_note
    row["attempted_official_dataset_path"] = str(OFFICIAL_DATASET_PATH)
    row["attempted_real_dataset_write"] = True

    return row


def build_controlled_persistence_attempts(
    source_accepted_inputs_df: pd.DataFrame,
    source_rejected_inputs_df: pd.DataFrame,
) -> pd.DataFrame:
    attempts: list[dict[str, Any]] = []

    if not source_accepted_inputs_df.empty:
        attempts.append(
            build_attempt_from_source_row(
                source_row=source_accepted_inputs_df.iloc[0],
                attempt_id="PERSIST_ATTEMPT_VALID_CONTROLLED_001",
                scenario_name="VALID_CONTROLLED_ROW_ATTEMPTS_WRITE",
                attempt_note=(
                    "Structurally valid controlled row attempts persistence. "
                    "It must remain blocked because Phase 9.6 does not allow evidence writes."
                ),
            )
        )

    if not source_rejected_inputs_df.empty:
        attempts.append(
            build_attempt_from_source_row(
                source_row=source_rejected_inputs_df.iloc[0],
                attempt_id="PERSIST_ATTEMPT_REJECTED_CONTROLLED_001",
                scenario_name="REJECTED_CONTROLLED_ROW_ATTEMPTS_WRITE",
                attempt_note=(
                    "Rejected controlled row attempts persistence. "
                    "It must remain blocked."
                ),
            )
        )

    if not source_accepted_inputs_df.empty:
        attempts.append(
            build_attempt_from_source_row(
                source_row=source_accepted_inputs_df.iloc[0],
                attempt_id="PERSIST_ATTEMPT_DANGEROUS_FLAGS_001",
                scenario_name="DANGEROUS_FLAGS_ATTEMPT_WRITE",
                attempt_note=(
                    "Controlled row attempts persistence with dangerous evidence, "
                    "alert, paper trade, real capital, and execution flags enabled."
                ),
                force_dangerous_flags=True,
            )
        )

    return pd.DataFrame(attempts)


def evaluate_persistence_attempts(attempts_df: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []

    for _, row in attempts_df.iterrows():
        attempt_id = str(row.get("attempt_id", ""))
        scenario_name = str(row.get("attempt_scenario", ""))
        candidate_id = str(row.get("candidate_id", ""))
        source_status = str(row.get("validation_status", ""))
        source_decision = str(row.get("validation_decision", ""))

        attempted_real_dataset_write = safe_bool(
            row.get("attempted_real_dataset_write", False)
        )
        accepted_as_real_evidence = safe_bool(
            row.get("accepted_as_real_evidence", False)
        )
        evidence_write_allowed = safe_bool(row.get("evidence_write_allowed", False))
        evidence_write_performed = safe_bool(
            row.get("evidence_write_performed", False)
        )
        forward_observation_started = safe_bool(
            row.get("forward_observation_started", False)
        )
        signal_generation_enabled = safe_bool(
            row.get("signal_generation_enabled", False)
        )
        execution_allowed = safe_bool(row.get("execution_allowed", False))
        live_alert_sent = safe_bool(row.get("live_alert_sent", False))
        paper_trade_submitted = safe_bool(row.get("paper_trade_submitted", False))
        real_capital_used = safe_bool(row.get("real_capital_used", False))

        block_reasons: list[str] = []

        if attempted_real_dataset_write:
            block_reasons.append("OFFICIAL_DATASET_WRITE_DISABLED")

        if accepted_as_real_evidence:
            block_reasons.append("REAL_EVIDENCE_NOT_ALLOWED")

        if evidence_write_allowed or evidence_write_performed:
            block_reasons.append("EVIDENCE_WRITE_DISABLED")

        if source_decision != "VALIDATED_FOR_FUTURE_FORWARD_OBSERVATION_INPUT":
            block_reasons.append("SOURCE_ROW_NOT_VALIDATED_FOR_ACTIVE_INPUT")

        if source_status != "CONTROLLED_VALID_INPUT_ONLY":
            block_reasons.append("SOURCE_ROW_NOT_CONTROLLED_VALID_INPUT_ONLY")

        if forward_observation_started:
            block_reasons.append("FORWARD_OBSERVATION_NOT_STARTED")

        if signal_generation_enabled:
            block_reasons.append("SIGNAL_GENERATION_DISABLED")

        if execution_allowed:
            block_reasons.append("EXECUTION_DISABLED")

        if live_alert_sent:
            block_reasons.append("LIVE_ALERTS_DISABLED")

        if paper_trade_submitted:
            block_reasons.append("PAPER_TRADING_DISABLED")

        if real_capital_used:
            block_reasons.append("REAL_CAPITAL_DISABLED")

        persistence_allowed = False
        write_performed = False
        evidence_rows_written = 0

        rows.append(
            {
                "attempt_id": attempt_id,
                "attempt_scenario": scenario_name,
                "candidate_id": candidate_id,
                "source_validation_decision": source_decision,
                "source_validation_status": source_status,
                "attempted_real_dataset_write": attempted_real_dataset_write,
                "persistence_guard_active": True,
                "persistence_allowed": persistence_allowed,
                "persistence_blocked": not persistence_allowed,
                "write_performed": write_performed,
                "evidence_rows_written": evidence_rows_written,
                "official_dataset_write_performed": False,
                "real_forward_dataset_created": False,
                "accepted_as_real_evidence_after_guard": False,
                "evidence_write_allowed_after_guard": False,
                "evidence_write_performed_after_guard": False,
                "forward_observation_started_after_guard": False,
                "signal_generation_enabled_after_guard": False,
                "execution_allowed_after_guard": False,
                "live_alert_sent_after_guard": False,
                "paper_trade_submitted_after_guard": False,
                "real_capital_used_after_guard": False,
                "guard_decision": "PERSISTENCE_WRITE_BLOCKED",
                "guard_status": PERSISTENCE_GUARD_RUN_STATUS,
                "block_reasons": ",".join(block_reasons),
            }
        )

    return pd.DataFrame(rows)


def build_guard_audit(evaluated_attempts_df: pd.DataFrame) -> pd.DataFrame:
    expected_block_reasons = [
        "OFFICIAL_DATASET_WRITE_DISABLED",
        "SOURCE_ROW_NOT_VALIDATED_FOR_ACTIVE_INPUT",
        "SOURCE_ROW_NOT_CONTROLLED_VALID_INPUT_ONLY",
        "REAL_EVIDENCE_NOT_ALLOWED",
        "EVIDENCE_WRITE_DISABLED",
        "FORWARD_OBSERVATION_NOT_STARTED",
        "SIGNAL_GENERATION_DISABLED",
        "EXECUTION_DISABLED",
        "LIVE_ALERTS_DISABLED",
        "PAPER_TRADING_DISABLED",
        "REAL_CAPITAL_DISABLED",
    ]

    block_blob = ""

    if not evaluated_attempts_df.empty:
        block_blob = ",".join(
            evaluated_attempts_df["block_reasons"].fillna("").astype(str).tolist()
        )

    rows: list[dict[str, Any]] = []

    for reason in expected_block_reasons:
        rows.append(
            {
                "expected_block_reason": reason,
                "present": reason in block_blob,
                "guard_status": PERSISTENCE_GUARD_RUN_STATUS,
            }
        )

    return pd.DataFrame(rows)


def build_persistence_guard_summary_table(
    attempts_df: pd.DataFrame,
    evaluated_attempts_df: pd.DataFrame,
    guard_audit_df: pd.DataFrame,
) -> pd.DataFrame:
    attempted_rows = int(len(attempts_df))

    blocked_rows = int(
        evaluated_attempts_df["persistence_blocked"].astype(bool).sum()
        if not evaluated_attempts_df.empty
        else 0
    )

    allowed_rows = int(
        evaluated_attempts_df["persistence_allowed"].astype(bool).sum()
        if not evaluated_attempts_df.empty
        else 0
    )

    write_performed_rows = int(
        evaluated_attempts_df["write_performed"].astype(bool).sum()
        if not evaluated_attempts_df.empty
        else 0
    )

    evidence_rows_written = int(
        evaluated_attempts_df["evidence_rows_written"].sum()
        if not evaluated_attempts_df.empty
        else 0
    )

    guard_audit_passed = (
        not guard_audit_df.empty
        and guard_audit_df["present"].astype(bool).all()
    )

    return pd.DataFrame(
        [
            {
                "persistence_guard_run_id": "PHASE_9_6_PERSISTENCE_GUARD_RUN_001",
                "guard_status": PERSISTENCE_GUARD_RUN_STATUS,
                "official_dataset_path": str(OFFICIAL_DATASET_PATH),
                "persistence_guard_active": True,
                "persistence_attempt_rows": attempted_rows,
                "persistence_allowed_rows": allowed_rows,
                "persistence_blocked_rows": blocked_rows,
                "write_performed_rows": write_performed_rows,
                "evidence_rows_written": evidence_rows_written,
                "guard_audit_passed": guard_audit_passed,
                "official_dataset_write_performed": False,
                "real_forward_dataset_created": False,
                "real_forward_signals_recorded": False,
                "journal_real_rows_accepted": False,
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


def validate_long_forward_observation_persistence_guard() -> dict[str, pd.DataFrame]:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    checks: list[dict[str, Any]] = []

    phase_anchors = {
        "phase_9_5_dataset_bootstrap_doc_exists": PHASE_9_5_DATASET_BOOTSTRAP_DOC_PATH,
        "phase_9_6_persistence_guard_doc_exists": PHASE_9_6_PERSISTENCE_GUARD_DOC_PATH,
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

    phase_9_5_result = validate_long_forward_observation_dataset_bootstrap()

    phase_9_5_summary_df = phase_9_5_result["summary"]
    source_persistence_guard_df = phase_9_5_result["persistence_guard"]
    source_dataset_schema_df = phase_9_5_result["dataset_schema"]
    source_empty_dataset_template_df = phase_9_5_result["empty_dataset_template"]
    source_bootstrap_ledger_df = phase_9_5_result["bootstrap_ledger"]
    source_accepted_inputs_df = phase_9_5_result["source_accepted_inputs"]
    source_rejected_inputs_df = phase_9_5_result["source_rejected_inputs"]

    phase_9_5_validation_passed = (
        not phase_9_5_summary_df.empty
        and bool(phase_9_5_summary_df.iloc[0].get("validation_passed", False))
    )

    dataset_bootstrap_defined = (
        not phase_9_5_summary_df.empty
        and bool(
            phase_9_5_summary_df.iloc[0].get(
                "long_forward_observation_dataset_bootstrap_defined",
                False,
            )
        )
    )

    attempts_df = build_controlled_persistence_attempts(
        source_accepted_inputs_df=source_accepted_inputs_df,
        source_rejected_inputs_df=source_rejected_inputs_df,
    )

    evaluated_attempts_df = evaluate_persistence_attempts(attempts_df)
    guard_audit_df = build_guard_audit(evaluated_attempts_df)

    persistence_guard_summary_table_df = build_persistence_guard_summary_table(
        attempts_df=attempts_df,
        evaluated_attempts_df=evaluated_attempts_df,
        guard_audit_df=guard_audit_df,
    )

    checks.append(
        build_check(
            check_group="phase_dependency",
            check_name="phase_9_5_validation_passed",
            passed=phase_9_5_validation_passed,
            severity="INFO" if phase_9_5_validation_passed else "ERROR",
            details=(
                str(phase_9_5_summary_df.iloc[0].get("validation_decision", ""))
                if not phase_9_5_summary_df.empty
                else "Missing Phase 9.5 summary."
            ),
        )
    )

    checks.append(
        build_check(
            check_group="phase_dependency",
            check_name="long_forward_observation_dataset_bootstrap_defined",
            passed=dataset_bootstrap_defined,
            severity="INFO" if dataset_bootstrap_defined else "ERROR",
            details=f"dataset_bootstrap_defined={dataset_bootstrap_defined}",
        )
    )

    source_guard_blocks = (
        not source_persistence_guard_df.empty
        and not source_persistence_guard_df["evidence_persistence_allowed"]
        .astype(bool)
        .any()
        and not source_persistence_guard_df["evidence_write_performed"]
        .astype(bool)
        .any()
    )

    checks.append(
        build_check(
            check_group="source_guard",
            check_name="source_persistence_guard_blocks_writes",
            passed=source_guard_blocks,
            severity="INFO" if source_guard_blocks else "ERROR",
            details="Source Phase 9.5 persistence guard blocks evidence writes.",
        )
    )

    checks.append(
        build_check(
            check_group="dataset_schema",
            check_name="source_dataset_schema_available",
            passed=len(source_dataset_schema_df) == len(DATASET_COLUMNS),
            severity=(
                "INFO" if len(source_dataset_schema_df) == len(DATASET_COLUMNS) else "ERROR"
            ),
            details=f"source_dataset_schema_columns={len(source_dataset_schema_df)}",
        )
    )

    checks.append(
        build_check(
            check_group="dataset_template",
            check_name="source_empty_dataset_template_remains_empty",
            passed=len(source_empty_dataset_template_df) == 0,
            severity="INFO" if len(source_empty_dataset_template_df) == 0 else "ERROR",
            details=f"source_empty_dataset_template_rows={len(source_empty_dataset_template_df)}",
        )
    )

    attempt_count = int(len(attempts_df))
    blocked_count = int(
        evaluated_attempts_df["persistence_blocked"].astype(bool).sum()
        if not evaluated_attempts_df.empty
        else 0
    )
    allowed_count = int(
        evaluated_attempts_df["persistence_allowed"].astype(bool).sum()
        if not evaluated_attempts_df.empty
        else 0
    )

    checks.append(
        build_check(
            check_group="persistence_attempts",
            check_name="controlled_persistence_attempts_created",
            passed=attempt_count == 3,
            severity="INFO" if attempt_count == 3 else "ERROR",
            details=f"attempt_count={attempt_count}",
        )
    )

    checks.append(
        build_check(
            check_group="persistence_attempts",
            check_name="all_persistence_attempts_blocked",
            passed=blocked_count == 3 and allowed_count == 0,
            severity="INFO" if blocked_count == 3 and allowed_count == 0 else "ERROR",
            details=f"blocked_count={blocked_count},allowed_count={allowed_count}",
        )
    )

    no_writes_performed = (
        not evaluated_attempts_df.empty
        and not evaluated_attempts_df["write_performed"].astype(bool).any()
        and not evaluated_attempts_df["official_dataset_write_performed"]
        .astype(bool)
        .any()
        and int(evaluated_attempts_df["evidence_rows_written"].sum()) == 0
    )

    checks.append(
        build_check(
            check_group="persistence_guard",
            check_name="no_official_dataset_writes_performed",
            passed=no_writes_performed,
            severity="INFO" if no_writes_performed else "ERROR",
            details="write_performed=False,official_dataset_write_performed=False,evidence_rows_written=0",
        )
    )

    dangerous_attempt_blocked = (
        not evaluated_attempts_df.empty
        and not evaluated_attempts_df[
            evaluated_attempts_df["attempt_scenario"].astype(str).eq(
                "DANGEROUS_FLAGS_ATTEMPT_WRITE"
            )
        ].empty
        and evaluated_attempts_df[
            evaluated_attempts_df["attempt_scenario"].astype(str).eq(
                "DANGEROUS_FLAGS_ATTEMPT_WRITE"
            )
        ]["persistence_blocked"]
        .astype(bool)
        .all()
    )

    checks.append(
        build_check(
            check_group="persistence_guard",
            check_name="dangerous_flags_attempt_blocked",
            passed=dangerous_attempt_blocked,
            severity="INFO" if dangerous_attempt_blocked else "ERROR",
            details="Dangerous evidence/action flags cannot bypass persistence guard.",
        )
    )

    guard_audit_passed = (
        not guard_audit_df.empty
        and guard_audit_df["present"].astype(bool).all()
    )

    checks.append(
        build_check(
            check_group="persistence_guard",
            check_name="expected_block_reasons_confirmed",
            passed=guard_audit_passed,
            severity="INFO" if guard_audit_passed else "ERROR",
            details=(
                "missing_reasons="
                + ",".join(
                    guard_audit_df[
                        ~guard_audit_df["present"].astype(bool)
                    ]["expected_block_reason"].astype(str)
                )
                if not guard_audit_df.empty
                else "missing_reasons=all"
            ),
        )
    )

    no_action_flags_after_guard = (
        not evaluated_attempts_df.empty
        and not evaluated_attempts_df["execution_allowed_after_guard"]
        .astype(bool)
        .any()
        and not evaluated_attempts_df["live_alert_sent_after_guard"].astype(bool).any()
        and not evaluated_attempts_df["paper_trade_submitted_after_guard"]
        .astype(bool)
        .any()
        and not evaluated_attempts_df["real_capital_used_after_guard"]
        .astype(bool)
        .any()
    )

    checks.append(
        build_check(
            check_group="safety_controls",
            check_name="guard_keeps_all_action_flags_false_after_attempts",
            passed=no_action_flags_after_guard,
            severity="INFO" if no_action_flags_after_guard else "ERROR",
            details="No execution, alerts, paper trades, or real capital after guard evaluation.",
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
            check_name="real_forward_signals_not_recorded",
            passed=True,
            severity="WARNING",
            details="Phase 9.6 tests controlled persistence attempts only.",
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
            check_name="phase_9_7_recommended_next",
            passed=True,
            severity="INFO",
            details=(
                "Recommended next step: "
                "Phase 9.7 LONG Forward Observation Controlled Dataset Write V1."
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
                "phase": "9.6",
                "long_forward_observation_persistence_guard_defined": True,
                "phase_9_5_validation_passed": phase_9_5_validation_passed,
                "long_forward_observation_dataset_bootstrap_defined": dataset_bootstrap_defined,
                "source_dataset_schema_columns": int(len(source_dataset_schema_df)),
                "source_empty_dataset_template_rows": int(
                    len(source_empty_dataset_template_df)
                ),
                "source_bootstrap_ledger_rows": int(len(source_bootstrap_ledger_df)),
                "persistence_attempt_rows": attempt_count,
                "persistence_allowed_rows": allowed_count,
                "persistence_blocked_rows": blocked_count,
                "guard_audit_rows": int(len(guard_audit_df)),
                "guard_audit_passed": guard_audit_passed,
                "persistence_guard_active": True,
                "official_dataset_write_performed": False,
                "real_forward_dataset_created": False,
                "real_forward_signals_recorded": False,
                "journal_real_rows_accepted": False,
                "evidence_persistence_allowed": False,
                "evidence_rows_written": 0,
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
                    "PHASE_9_7_LONG_FORWARD_OBSERVATION_CONTROLLED_DATASET_WRITE_V1"
                ),
                "estimated_phase_9_progress_percent": 60,
                "total_checks": int(len(checks_df)),
                "warning_count": warning_count,
                "error_count": error_count,
                "blocker_count": blocker_count,
                "validation_passed": validation_passed,
                "validation_decision": (
                    "PHASE_9_6_LONG_FORWARD_OBSERVATION_PERSISTENCE_GUARD_VALIDATED"
                    if validation_passed
                    else "PHASE_9_6_LONG_FORWARD_OBSERVATION_PERSISTENCE_GUARD_FAILED"
                ),
            }
        ]
    )

    phase_9_5_summary_df.to_csv(
        REPORTS_DIR / "phase_9_5_source_summary_v1.csv",
        index=False,
    )
    source_persistence_guard_df.to_csv(
        REPORTS_DIR / "phase_9_5_source_persistence_guard_v1.csv",
        index=False,
    )
    source_dataset_schema_df.to_csv(
        REPORTS_DIR / "phase_9_5_source_dataset_schema_v1.csv",
        index=False,
    )
    source_empty_dataset_template_df.to_csv(
        REPORTS_DIR / "phase_9_5_source_empty_dataset_template_v1.csv",
        index=False,
    )
    source_bootstrap_ledger_df.to_csv(
        REPORTS_DIR / "phase_9_5_source_bootstrap_ledger_v1.csv",
        index=False,
    )
    attempts_df.to_csv(
        REPORTS_DIR / "long_forward_observation_persistence_attempts_v1.csv",
        index=False,
    )
    evaluated_attempts_df.to_csv(
        REPORTS_DIR / "long_forward_observation_persistence_attempt_evaluation_v1.csv",
        index=False,
    )
    guard_audit_df.to_csv(
        REPORTS_DIR / "long_forward_observation_persistence_guard_audit_v1.csv",
        index=False,
    )
    persistence_guard_summary_table_df.to_csv(
        REPORTS_DIR / "long_forward_observation_persistence_guard_summary_table_v1.csv",
        index=False,
    )
    checks_df.to_csv(
        REPORTS_DIR / "long_forward_observation_persistence_guard_checks_v1.csv",
        index=False,
    )
    summary_df.to_csv(
        REPORTS_DIR / "long_forward_observation_persistence_guard_summary_v1.csv",
        index=False,
    )

    return {
        "summary": summary_df,
        "source_phase_9_5_summary": phase_9_5_summary_df,
        "source_persistence_guard": source_persistence_guard_df,
        "source_dataset_schema": source_dataset_schema_df,
        "source_empty_dataset_template": source_empty_dataset_template_df,
        "source_bootstrap_ledger": source_bootstrap_ledger_df,
        "persistence_attempts": attempts_df,
        "evaluated_attempts": evaluated_attempts_df,
        "guard_audit": guard_audit_df,
        "persistence_guard_summary": persistence_guard_summary_table_df,
        "checks": checks_df,
    }