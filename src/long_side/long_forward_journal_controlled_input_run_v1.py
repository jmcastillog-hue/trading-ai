from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from src.long_side.long_forward_journal_input_validator_v1 import (
    PRIMARY_RESEARCH_CANDIDATE,
    SECONDARY_REFERENCE_CANDIDATE,
    BLOCKED_CANDIDATES,
    validate_long_forward_journal_input_validator,
)


REPORTS_DIR = Path("reports/phase_9_4_long_forward_journal_controlled_input_run_v1")

PHASE_9_3_VALIDATOR_DOC_PATH = Path(
    "docs/PHASE_9_LONG_FORWARD_JOURNAL_INPUT_VALIDATOR.md"
)
PHASE_9_4_CONTROLLED_RUN_DOC_PATH = Path(
    "docs/PHASE_9_LONG_FORWARD_JOURNAL_CONTROLLED_INPUT_RUN.md"
)

CONTROLLED_RUN_STATUS = "LONG_FORWARD_JOURNAL_CONTROLLED_INPUT_RUN_ONLY"

SAFETY_FLAGS = {
    "forward_observation_started": False,
    "signal_generation_enabled": False,
    "real_forward_signals_recorded": False,
    "journal_real_rows_accepted": False,
    "evidence_write_performed": False,
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


def build_controlled_run_manifest(
    accepted_inputs_df: pd.DataFrame,
    rejected_inputs_df: pd.DataFrame,
) -> pd.DataFrame:
    accepted_count = int(len(accepted_inputs_df))
    rejected_count = int(len(rejected_inputs_df))
    total_count = accepted_count + rejected_count

    return pd.DataFrame(
        [
            {
                "controlled_run_id": "PHASE_9_4_CONTROLLED_LONG_INPUT_RUN_001",
                "controlled_run_status": CONTROLLED_RUN_STATUS,
                "run_mode": "CONTROLLED_SYNTHETIC_INPUT_RUN",
                "source_validator": "PHASE_9_3_LONG_FORWARD_JOURNAL_INPUT_VALIDATOR_VALIDATED",
                "primary_research_candidate_id": PRIMARY_RESEARCH_CANDIDATE,
                "secondary_reference_candidate_id": SECONDARY_REFERENCE_CANDIDATE,
                "source_total_rows": total_count,
                "source_accepted_controlled_rows": accepted_count,
                "source_rejected_controlled_rows": rejected_count,
                "simulated_structural_acceptance_rows": accepted_count,
                "confirmed_rejection_rows": rejected_count,
                "real_forward_signals_recorded": False,
                "journal_real_rows_accepted": False,
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
            }
        ]
    )


def build_controlled_run_ledger(
    accepted_inputs_df: pd.DataFrame,
    rejected_inputs_df: pd.DataFrame,
) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []

    for _, row in accepted_inputs_df.iterrows():
        rows.append(
            {
                "observation_id": str(row.get("observation_id", "")),
                "candidate_id": str(row.get("candidate_id", "")),
                "source_validation_decision": str(row.get("validation_decision", "")),
                "source_validation_status": str(row.get("validation_status", "")),
                "controlled_run_action": "STRUCTURAL_ACCEPTANCE_SIMULATED",
                "controlled_run_decision": "CONTROLLED_INPUT_ACCEPTED_FOR_STRUCTURE_ONLY",
                "controlled_run_note": (
                    "Valid controlled row passed structural validation, "
                    "but is not accepted as real evidence."
                ),
                "rejection_reasons": "",
                "accepted_as_real_evidence": False,
                "evidence_persistence_allowed": False,
                "evidence_write_performed": False,
                "forward_observation_started": False,
                "signal_generation_enabled": False,
                "execution_allowed": False,
                "live_alert_sent": False,
                "paper_trade_submitted": False,
                "real_capital_used": False,
                "controlled_run_status": CONTROLLED_RUN_STATUS,
            }
        )

    for _, row in rejected_inputs_df.iterrows():
        rows.append(
            {
                "observation_id": str(row.get("observation_id", "")),
                "candidate_id": str(row.get("candidate_id", "")),
                "source_validation_decision": str(row.get("validation_decision", "")),
                "source_validation_status": str(row.get("validation_status", "")),
                "controlled_run_action": "REJECTION_CONFIRMED",
                "controlled_run_decision": "CONTROLLED_INPUT_REJECTED",
                "controlled_run_note": (
                    "Invalid or ineligible controlled row remained rejected."
                ),
                "rejection_reasons": str(row.get("rejection_reasons", "")),
                "accepted_as_real_evidence": False,
                "evidence_persistence_allowed": False,
                "evidence_write_performed": False,
                "forward_observation_started": False,
                "signal_generation_enabled": False,
                "execution_allowed": False,
                "live_alert_sent": False,
                "paper_trade_submitted": False,
                "real_capital_used": False,
                "controlled_run_status": CONTROLLED_RUN_STATUS,
            }
        )

    if not rows:
        return pd.DataFrame(
            columns=[
                "observation_id",
                "candidate_id",
                "source_validation_decision",
                "source_validation_status",
                "controlled_run_action",
                "controlled_run_decision",
                "controlled_run_note",
                "rejection_reasons",
                "accepted_as_real_evidence",
                "evidence_persistence_allowed",
                "evidence_write_performed",
                "forward_observation_started",
                "signal_generation_enabled",
                "execution_allowed",
                "live_alert_sent",
                "paper_trade_submitted",
                "real_capital_used",
                "controlled_run_status",
            ]
        )

    return pd.DataFrame(rows)


def build_rejection_audit(rejected_inputs_df: pd.DataFrame) -> pd.DataFrame:
    expected_rejection_reasons = [
        "SECONDARY_REFERENCE_ONLY",
        "BLOCKED_CANDIDATE",
        "INVALID_LONG_PRICE_STRUCTURE",
        "DANGEROUS_EXECUTION_OR_ALERT_FLAGS",
    ]

    rejection_blob = ""

    if not rejected_inputs_df.empty and "rejection_reasons" in rejected_inputs_df.columns:
        rejection_blob = ",".join(
            rejected_inputs_df["rejection_reasons"].fillna("").astype(str).tolist()
        )

    rows: list[dict[str, Any]] = []

    for reason in expected_rejection_reasons:
        rows.append(
            {
                "expected_rejection_reason": reason,
                "present": reason in rejection_blob,
                "controlled_run_status": CONTROLLED_RUN_STATUS,
            }
        )

    return pd.DataFrame(rows)


def build_controlled_run_summary_table(
    controlled_run_manifest_df: pd.DataFrame,
    controlled_run_ledger_df: pd.DataFrame,
    rejection_audit_df: pd.DataFrame,
) -> pd.DataFrame:
    if controlled_run_manifest_df.empty:
        return pd.DataFrame()

    manifest = controlled_run_manifest_df.iloc[0].to_dict()

    structural_acceptance_rows = int(
        controlled_run_ledger_df["controlled_run_decision"]
        .astype(str)
        .eq("CONTROLLED_INPUT_ACCEPTED_FOR_STRUCTURE_ONLY")
        .sum()
        if not controlled_run_ledger_df.empty
        else 0
    )

    controlled_rejection_rows = int(
        controlled_run_ledger_df["controlled_run_decision"]
        .astype(str)
        .eq("CONTROLLED_INPUT_REJECTED")
        .sum()
        if not controlled_run_ledger_df.empty
        else 0
    )

    rejection_audit_passed = (
        not rejection_audit_df.empty
        and rejection_audit_df["present"].astype(bool).all()
    )

    return pd.DataFrame(
        [
            {
                "controlled_run_id": manifest.get("controlled_run_id", ""),
                "controlled_run_status": CONTROLLED_RUN_STATUS,
                "source_total_rows": int(manifest.get("source_total_rows", 0)),
                "structural_acceptance_rows": structural_acceptance_rows,
                "controlled_rejection_rows": controlled_rejection_rows,
                "rejection_audit_passed": rejection_audit_passed,
                "real_forward_signals_recorded": False,
                "journal_real_rows_accepted": False,
                "evidence_rows_written": 0,
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


def validate_long_forward_journal_controlled_input_run() -> dict[str, pd.DataFrame]:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    checks: list[dict[str, Any]] = []

    phase_anchors = {
        "phase_9_3_validator_doc_exists": PHASE_9_3_VALIDATOR_DOC_PATH,
        "phase_9_4_controlled_run_doc_exists": PHASE_9_4_CONTROLLED_RUN_DOC_PATH,
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

    phase_9_3_result = validate_long_forward_journal_input_validator()

    phase_9_3_summary_df = phase_9_3_result["summary"]
    source_controlled_input_rows_df = phase_9_3_result["controlled_input_rows"]
    source_row_checks_df = phase_9_3_result["row_checks"]
    source_accepted_inputs_df = phase_9_3_result["accepted_inputs"]
    source_rejected_inputs_df = phase_9_3_result["rejected_inputs"]

    phase_9_3_validation_passed = (
        not phase_9_3_summary_df.empty
        and bool(phase_9_3_summary_df.iloc[0].get("validation_passed", False))
    )

    input_validator_defined = (
        not phase_9_3_summary_df.empty
        and bool(
            phase_9_3_summary_df.iloc[0].get(
                "long_forward_journal_input_validator_defined",
                False,
            )
        )
    )

    controlled_run_manifest_df = build_controlled_run_manifest(
        accepted_inputs_df=source_accepted_inputs_df,
        rejected_inputs_df=source_rejected_inputs_df,
    )

    controlled_run_ledger_df = build_controlled_run_ledger(
        accepted_inputs_df=source_accepted_inputs_df,
        rejected_inputs_df=source_rejected_inputs_df,
    )

    rejection_audit_df = build_rejection_audit(source_rejected_inputs_df)

    controlled_run_summary_df = build_controlled_run_summary_table(
        controlled_run_manifest_df=controlled_run_manifest_df,
        controlled_run_ledger_df=controlled_run_ledger_df,
        rejection_audit_df=rejection_audit_df,
    )

    checks.append(
        build_check(
            check_group="phase_dependency",
            check_name="phase_9_3_validation_passed",
            passed=phase_9_3_validation_passed,
            severity="INFO" if phase_9_3_validation_passed else "ERROR",
            details=(
                str(phase_9_3_summary_df.iloc[0].get("validation_decision", ""))
                if not phase_9_3_summary_df.empty
                else "Missing Phase 9.3 summary."
            ),
        )
    )

    checks.append(
        build_check(
            check_group="phase_dependency",
            check_name="long_forward_journal_input_validator_defined",
            passed=input_validator_defined,
            severity="INFO" if input_validator_defined else "ERROR",
            details=f"input_validator_defined={input_validator_defined}",
        )
    )

    accepted_count = int(len(source_accepted_inputs_df))
    rejected_count = int(len(source_rejected_inputs_df))
    source_total_count = accepted_count + rejected_count

    checks.append(
        build_check(
            check_group="controlled_run",
            check_name="source_controlled_rows_available",
            passed=source_total_count == 5,
            severity="INFO" if source_total_count == 5 else "ERROR",
            details=f"source_total_count={source_total_count}",
        )
    )

    checks.append(
        build_check(
            check_group="controlled_run",
            check_name="single_structural_acceptance_simulated",
            passed=accepted_count == 1,
            severity="INFO" if accepted_count == 1 else "ERROR",
            details=f"accepted_count={accepted_count}",
        )
    )

    checks.append(
        build_check(
            check_group="controlled_run",
            check_name="invalid_rows_rejection_confirmed",
            passed=rejected_count == 4,
            severity="INFO" if rejected_count == 4 else "ERROR",
            details=f"rejected_count={rejected_count}",
        )
    )

    accepted_primary_only = (
        not source_accepted_inputs_df.empty
        and source_accepted_inputs_df["candidate_id"]
        .astype(str)
        .eq(PRIMARY_RESEARCH_CANDIDATE)
        .all()
    )

    checks.append(
        build_check(
            check_group="candidate_scope",
            check_name="accepted_rows_primary_candidate_only",
            passed=accepted_primary_only,
            severity="INFO" if accepted_primary_only else "ERROR",
            details=(
                "accepted_candidates="
                + ",".join(
                    source_accepted_inputs_df["candidate_id"].astype(str).unique()
                )
                if not source_accepted_inputs_df.empty
                else "accepted_candidates="
            ),
        )
    )

    secondary_rejected = (
        not source_rejected_inputs_df.empty
        and SECONDARY_REFERENCE_CANDIDATE
        in set(source_rejected_inputs_df["candidate_id"].astype(str).tolist())
    )

    checks.append(
        build_check(
            check_group="candidate_scope",
            check_name="secondary_reference_rejection_confirmed",
            passed=secondary_rejected,
            severity="INFO" if secondary_rejected else "ERROR",
            details=f"secondary={SECONDARY_REFERENCE_CANDIDATE}",
        )
    )

    blocked_rejected = (
        not source_rejected_inputs_df.empty
        and any(
            candidate in set(source_rejected_inputs_df["candidate_id"].astype(str))
            for candidate in BLOCKED_CANDIDATES
        )
    )

    checks.append(
        build_check(
            check_group="candidate_scope",
            check_name="blocked_candidate_rejection_confirmed",
            passed=blocked_rejected,
            severity="INFO" if blocked_rejected else "ERROR",
            details="blocked=" + ",".join(BLOCKED_CANDIDATES),
        )
    )

    rejection_audit_passed = (
        not rejection_audit_df.empty
        and rejection_audit_df["present"].astype(bool).all()
    )

    checks.append(
        build_check(
            check_group="controlled_run",
            check_name="expected_rejection_reasons_confirmed",
            passed=rejection_audit_passed,
            severity="INFO" if rejection_audit_passed else "ERROR",
            details=(
                "missing_reasons="
                + ",".join(
                    rejection_audit_df[
                        ~rejection_audit_df["present"].astype(bool)
                    ]["expected_rejection_reason"].astype(str)
                )
                if not rejection_audit_df.empty
                else "missing_reasons=all"
            ),
        )
    )

    ledger_rows_match = len(controlled_run_ledger_df) == source_total_count

    checks.append(
        build_check(
            check_group="controlled_run",
            check_name="controlled_run_ledger_rows_match_source",
            passed=ledger_rows_match,
            severity="INFO" if ledger_rows_match else "ERROR",
            details=f"ledger_rows={len(controlled_run_ledger_df)},source_rows={source_total_count}",
        )
    )

    no_real_evidence = (
        not controlled_run_ledger_df.empty
        and not controlled_run_ledger_df["accepted_as_real_evidence"].astype(bool).any()
        and not controlled_run_ledger_df["evidence_write_performed"].astype(bool).any()
    )

    checks.append(
        build_check(
            check_group="scope_control",
            check_name="controlled_rows_not_real_evidence",
            passed=no_real_evidence,
            severity="INFO" if no_real_evidence else "ERROR",
            details="Controlled run rows are not accepted as real evidence.",
        )
    )

    no_execution_or_alert_actions = (
        not controlled_run_ledger_df.empty
        and not controlled_run_ledger_df["execution_allowed"].astype(bool).any()
        and not controlled_run_ledger_df["live_alert_sent"].astype(bool).any()
        and not controlled_run_ledger_df["paper_trade_submitted"].astype(bool).any()
        and not controlled_run_ledger_df["real_capital_used"].astype(bool).any()
    )

    checks.append(
        build_check(
            check_group="safety_controls",
            check_name="controlled_run_keeps_all_action_flags_false",
            passed=no_execution_or_alert_actions,
            severity="INFO" if no_execution_or_alert_actions else "ERROR",
            details="No execution, alerts, paper trades, or real capital actions occur.",
        )
    )

    evidence_rows_written = 0

    checks.append(
        build_check(
            check_group="scope_control",
            check_name="evidence_rows_written_zero",
            passed=evidence_rows_written == 0,
            severity="INFO" if evidence_rows_written == 0 else "ERROR",
            details=f"evidence_rows_written={evidence_rows_written}",
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
            details="Phase 9.4 runs controlled synthetic input flow only.",
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
            check_name="phase_9_5_recommended_next",
            passed=True,
            severity="INFO",
            details=(
                "Recommended next step: "
                "Phase 9.5 LONG Forward Observation Dataset Bootstrap V1."
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
                "phase": "9.4",
                "long_forward_journal_controlled_input_run_defined": True,
                "phase_9_3_validation_passed": phase_9_3_validation_passed,
                "long_forward_journal_input_validator_defined": input_validator_defined,
                "source_controlled_input_rows": int(len(source_controlled_input_rows_df)),
                "source_row_check_rows": int(len(source_row_checks_df)),
                "accepted_source_rows": accepted_count,
                "rejected_source_rows": rejected_count,
                "controlled_run_manifest_rows": int(len(controlled_run_manifest_df)),
                "controlled_run_ledger_rows": int(len(controlled_run_ledger_df)),
                "controlled_run_summary_rows": int(len(controlled_run_summary_df)),
                "rejection_audit_rows": int(len(rejection_audit_df)),
                "single_structural_acceptance_simulated": accepted_count == 1,
                "invalid_rows_rejection_confirmed": rejected_count == 4,
                "accepted_rows_primary_candidate_only": accepted_primary_only,
                "secondary_reference_rejection_confirmed": secondary_rejected,
                "blocked_candidate_rejection_confirmed": blocked_rejected,
                "expected_rejection_reasons_confirmed": rejection_audit_passed,
                "real_forward_signals_recorded": False,
                "journal_real_rows_accepted": False,
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
                    "PHASE_9_5_LONG_FORWARD_OBSERVATION_DATASET_BOOTSTRAP_V1"
                ),
                "estimated_phase_9_progress_percent": 40,
                "total_checks": int(len(checks_df)),
                "warning_count": warning_count,
                "error_count": error_count,
                "blocker_count": blocker_count,
                "validation_passed": validation_passed,
                "validation_decision": (
                    "PHASE_9_4_LONG_FORWARD_JOURNAL_CONTROLLED_INPUT_RUN_VALIDATED"
                    if validation_passed
                    else "PHASE_9_4_LONG_FORWARD_JOURNAL_CONTROLLED_INPUT_RUN_FAILED"
                ),
            }
        ]
    )

    phase_9_3_summary_df.to_csv(
        REPORTS_DIR / "phase_9_3_source_summary_v1.csv",
        index=False,
    )
    source_controlled_input_rows_df.to_csv(
        REPORTS_DIR / "phase_9_3_source_controlled_input_rows_v1.csv",
        index=False,
    )
    source_row_checks_df.to_csv(
        REPORTS_DIR / "phase_9_3_source_row_checks_v1.csv",
        index=False,
    )
    source_accepted_inputs_df.to_csv(
        REPORTS_DIR / "phase_9_3_source_accepted_inputs_v1.csv",
        index=False,
    )
    source_rejected_inputs_df.to_csv(
        REPORTS_DIR / "phase_9_3_source_rejected_inputs_v1.csv",
        index=False,
    )
    controlled_run_manifest_df.to_csv(
        REPORTS_DIR / "long_forward_journal_controlled_run_manifest_v1.csv",
        index=False,
    )
    controlled_run_ledger_df.to_csv(
        REPORTS_DIR / "long_forward_journal_controlled_run_ledger_v1.csv",
        index=False,
    )
    rejection_audit_df.to_csv(
        REPORTS_DIR / "long_forward_journal_controlled_rejection_audit_v1.csv",
        index=False,
    )
    controlled_run_summary_df.to_csv(
        REPORTS_DIR / "long_forward_journal_controlled_run_summary_table_v1.csv",
        index=False,
    )
    checks_df.to_csv(
        REPORTS_DIR / "long_forward_journal_controlled_input_run_checks_v1.csv",
        index=False,
    )
    summary_df.to_csv(
        REPORTS_DIR / "long_forward_journal_controlled_input_run_summary_v1.csv",
        index=False,
    )

    return {
        "summary": summary_df,
        "source_phase_9_3_summary": phase_9_3_summary_df,
        "source_controlled_input_rows": source_controlled_input_rows_df,
        "source_row_checks": source_row_checks_df,
        "source_accepted_inputs": source_accepted_inputs_df,
        "source_rejected_inputs": source_rejected_inputs_df,
        "controlled_run_manifest": controlled_run_manifest_df,
        "controlled_run_ledger": controlled_run_ledger_df,
        "rejection_audit": rejection_audit_df,
        "controlled_run_summary": controlled_run_summary_df,
        "checks": checks_df,
    }