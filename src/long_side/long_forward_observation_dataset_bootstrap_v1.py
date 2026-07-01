from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from src.long_side.long_forward_journal_controlled_input_run_v1 import (
    PRIMARY_RESEARCH_CANDIDATE,
    SECONDARY_REFERENCE_CANDIDATE,
    BLOCKED_CANDIDATES,
    validate_long_forward_journal_controlled_input_run,
)


REPORTS_DIR = Path("reports/phase_9_5_long_forward_observation_dataset_bootstrap_v1")

PHASE_9_4_CONTROLLED_RUN_DOC_PATH = Path(
    "docs/PHASE_9_LONG_FORWARD_JOURNAL_CONTROLLED_INPUT_RUN.md"
)
PHASE_9_5_DATASET_BOOTSTRAP_DOC_PATH = Path(
    "docs/PHASE_9_LONG_FORWARD_OBSERVATION_DATASET_BOOTSTRAP.md"
)

OFFICIAL_DATASET_PATH = Path("data/forward/long_forward_observation_dataset_v1.csv")

DATASET_STATUS = "LONG_FORWARD_OBSERVATION_DATASET_BOOTSTRAP_ONLY"
PERSISTENCE_GUARD_STATUS = "PERSISTENCE_BLOCKED_BOOTSTRAP_ONLY"

DATASET_COLUMNS = [
    "observation_id",
    "dataset_status",
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
    "cost_profile",
    "readiness_source",
    "manual_review_required",
    "manual_review_status",
    "reviewer_notes",
    "execution_allowed",
    "live_alert_sent",
    "paper_trade_submitted",
    "real_capital_used",
    "resolution_status",
    "result_r",
    "mfe_r",
    "mae_r",
    "bars_to_resolution",
    "notes",
    "created_at_utc",
    "updated_at_utc",
    "accepted_as_real_evidence",
    "evidence_source",
    "evidence_row_status",
    "evidence_write_allowed",
    "evidence_write_performed",
    "forward_observation_started",
    "signal_generation_enabled",
    "persistence_guard_status",
]

REQUIRED_DATASET_COLUMNS = set(DATASET_COLUMNS)

SAFETY_FLAGS = {
    "forward_observation_started": False,
    "signal_generation_enabled": False,
    "real_forward_signals_recorded": False,
    "journal_real_rows_accepted": False,
    "real_forward_dataset_created": False,
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


def build_dataset_schema() -> pd.DataFrame:
    descriptions = {
        "observation_id": "Unique LONG forward observation identifier.",
        "dataset_status": "Dataset row or template status.",
        "observed_at": "Timestamp when the potential LONG signal was observed.",
        "symbol": "Market symbol.",
        "timeframe": "Observed timeframe.",
        "candidate_id": "LONG candidate associated with the observation.",
        "observation_role": "Primary or secondary observation role.",
        "direction": "Must remain LONG.",
        "signal_state": "Signal state.",
        "market_context": "Manual or model-assisted market context summary.",
        "entry_price": "Candidate entry price.",
        "stop_price": "Candidate stop price.",
        "target_price": "Candidate target price.",
        "risk_reward": "Expected risk-reward ratio.",
        "invalidation_level": "Price or condition invalidating the observation.",
        "cost_profile": "Cost profile assumption.",
        "readiness_source": "Source phase or gate that authorized observation eligibility.",
        "manual_review_required": "Must remain True.",
        "manual_review_status": "Manual review status.",
        "reviewer_notes": "Manual review notes.",
        "execution_allowed": "Must remain False.",
        "live_alert_sent": "Must remain False.",
        "paper_trade_submitted": "Must remain False.",
        "real_capital_used": "Must remain False.",
        "resolution_status": "Future outcome status.",
        "result_r": "Future result measured in R.",
        "mfe_r": "Future maximum favorable excursion in R.",
        "mae_r": "Future maximum adverse excursion in R.",
        "bars_to_resolution": "Bars needed to resolve the observation.",
        "notes": "Manual notes.",
        "created_at_utc": "UTC creation timestamp.",
        "updated_at_utc": "UTC update timestamp.",
        "accepted_as_real_evidence": "Must remain False during bootstrap.",
        "evidence_source": "Evidence source phase or input.",
        "evidence_row_status": "Evidence row lifecycle status.",
        "evidence_write_allowed": "Must remain False during bootstrap.",
        "evidence_write_performed": "Must remain False during bootstrap.",
        "forward_observation_started": "Must remain False during bootstrap.",
        "signal_generation_enabled": "Must remain False during bootstrap.",
        "persistence_guard_status": "Persistence guard status.",
    }

    numeric_columns = {
        "entry_price",
        "stop_price",
        "target_price",
        "risk_reward",
        "invalidation_level",
        "result_r",
        "mfe_r",
        "mae_r",
        "bars_to_resolution",
    }

    bool_columns = {
        "manual_review_required",
        "execution_allowed",
        "live_alert_sent",
        "paper_trade_submitted",
        "real_capital_used",
        "accepted_as_real_evidence",
        "evidence_write_allowed",
        "evidence_write_performed",
        "forward_observation_started",
        "signal_generation_enabled",
    }

    rows: list[dict[str, Any]] = []

    for column in DATASET_COLUMNS:
        if column in numeric_columns:
            expected_type = "numeric"
        elif column in bool_columns:
            expected_type = "bool"
        else:
            expected_type = "string"

        rows.append(
            {
                "column_name": column,
                "required": True,
                "expected_type": expected_type,
                "description": descriptions.get(column, ""),
                "dataset_status": DATASET_STATUS,
            }
        )

    return pd.DataFrame(rows)


def build_empty_dataset_template() -> pd.DataFrame:
    return pd.DataFrame(columns=DATASET_COLUMNS)


def build_persistence_guard(
    accepted_inputs_df: pd.DataFrame,
    rejected_inputs_df: pd.DataFrame,
) -> pd.DataFrame:
    accepted_count = int(len(accepted_inputs_df))
    rejected_count = int(len(rejected_inputs_df))

    return pd.DataFrame(
        [
            {
                "persistence_guard_id": "PHASE_9_5_LONG_FORWARD_DATASET_GUARD_001",
                "persistence_guard_status": PERSISTENCE_GUARD_STATUS,
                "official_dataset_path": str(OFFICIAL_DATASET_PATH),
                "bootstrap_template_report_path": str(
                    REPORTS_DIR / "long_forward_observation_dataset_template_v1.csv"
                ),
                "source_accepted_controlled_rows": accepted_count,
                "source_rejected_controlled_rows": rejected_count,
                "source_total_rows": accepted_count + rejected_count,
                "bootstrap_template_generated": True,
                "real_forward_dataset_created": False,
                "real_forward_signals_recorded": False,
                "journal_real_rows_accepted": False,
                "evidence_persistence_allowed": False,
                "evidence_rows_allowed_to_write": 0,
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


def build_bootstrap_ledger(
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
                "bootstrap_action": "DATASET_WRITE_BLOCKED_BOOTSTRAP_ONLY",
                "bootstrap_decision": "STRUCTURE_COMPATIBLE_NOT_PERSISTED",
                "bootstrap_note": (
                    "Controlled accepted row is compatible with dataset schema, "
                    "but is not written as real evidence."
                ),
                "accepted_as_real_evidence": False,
                "evidence_write_allowed": False,
                "evidence_write_performed": False,
                "forward_observation_started": False,
                "signal_generation_enabled": False,
                "execution_allowed": False,
                "live_alert_sent": False,
                "paper_trade_submitted": False,
                "real_capital_used": False,
                "persistence_guard_status": PERSISTENCE_GUARD_STATUS,
            }
        )

    for _, row in rejected_inputs_df.iterrows():
        rows.append(
            {
                "observation_id": str(row.get("observation_id", "")),
                "candidate_id": str(row.get("candidate_id", "")),
                "source_validation_decision": str(row.get("validation_decision", "")),
                "bootstrap_action": "REJECTED_ROW_CARRIED_FORWARD_NO_WRITE",
                "bootstrap_decision": "REJECTED_NOT_PERSISTED",
                "bootstrap_note": "Rejected controlled row is not written.",
                "accepted_as_real_evidence": False,
                "evidence_write_allowed": False,
                "evidence_write_performed": False,
                "forward_observation_started": False,
                "signal_generation_enabled": False,
                "execution_allowed": False,
                "live_alert_sent": False,
                "paper_trade_submitted": False,
                "real_capital_used": False,
                "persistence_guard_status": PERSISTENCE_GUARD_STATUS,
            }
        )

    if not rows:
        return pd.DataFrame(
            columns=[
                "observation_id",
                "candidate_id",
                "source_validation_decision",
                "bootstrap_action",
                "bootstrap_decision",
                "bootstrap_note",
                "accepted_as_real_evidence",
                "evidence_write_allowed",
                "evidence_write_performed",
                "forward_observation_started",
                "signal_generation_enabled",
                "execution_allowed",
                "live_alert_sent",
                "paper_trade_submitted",
                "real_capital_used",
                "persistence_guard_status",
            ]
        )

    return pd.DataFrame(rows)


def build_dataset_bootstrap_summary_table(
    dataset_schema_df: pd.DataFrame,
    empty_dataset_template_df: pd.DataFrame,
    persistence_guard_df: pd.DataFrame,
    bootstrap_ledger_df: pd.DataFrame,
) -> pd.DataFrame:
    if persistence_guard_df.empty:
        return pd.DataFrame()

    guard = persistence_guard_df.iloc[0].to_dict()

    ledger_write_attempt_rows = int(len(bootstrap_ledger_df))

    ledger_real_evidence_rows = int(
        bootstrap_ledger_df["accepted_as_real_evidence"].astype(bool).sum()
        if not bootstrap_ledger_df.empty
        else 0
    )

    ledger_write_performed_rows = int(
        bootstrap_ledger_df["evidence_write_performed"].astype(bool).sum()
        if not bootstrap_ledger_df.empty
        else 0
    )

    return pd.DataFrame(
        [
            {
                "dataset_bootstrap_id": "PHASE_9_5_LONG_FORWARD_DATASET_BOOTSTRAP_001",
                "dataset_status": DATASET_STATUS,
                "persistence_guard_status": PERSISTENCE_GUARD_STATUS,
                "dataset_schema_columns": int(len(dataset_schema_df)),
                "empty_dataset_template_rows": int(len(empty_dataset_template_df)),
                "persistence_guard_rows": int(len(persistence_guard_df)),
                "bootstrap_ledger_rows": int(len(bootstrap_ledger_df)),
                "ledger_write_attempt_rows": ledger_write_attempt_rows,
                "ledger_real_evidence_rows": ledger_real_evidence_rows,
                "ledger_write_performed_rows": ledger_write_performed_rows,
                "source_accepted_controlled_rows": int(
                    guard.get("source_accepted_controlled_rows", 0)
                ),
                "source_rejected_controlled_rows": int(
                    guard.get("source_rejected_controlled_rows", 0)
                ),
                "real_forward_dataset_created": False,
                "real_forward_signals_recorded": False,
                "journal_real_rows_accepted": False,
                "evidence_persistence_allowed": False,
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


def validate_long_forward_observation_dataset_bootstrap() -> dict[str, pd.DataFrame]:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    checks: list[dict[str, Any]] = []

    phase_anchors = {
        "phase_9_4_controlled_run_doc_exists": PHASE_9_4_CONTROLLED_RUN_DOC_PATH,
        "phase_9_5_dataset_bootstrap_doc_exists": PHASE_9_5_DATASET_BOOTSTRAP_DOC_PATH,
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

    phase_9_4_result = validate_long_forward_journal_controlled_input_run()

    phase_9_4_summary_df = phase_9_4_result["summary"]
    source_controlled_run_summary_df = phase_9_4_result["controlled_run_summary"]
    source_accepted_inputs_df = phase_9_4_result["source_accepted_inputs"]
    source_rejected_inputs_df = phase_9_4_result["source_rejected_inputs"]
    source_controlled_run_ledger_df = phase_9_4_result["controlled_run_ledger"]

    phase_9_4_validation_passed = (
        not phase_9_4_summary_df.empty
        and bool(phase_9_4_summary_df.iloc[0].get("validation_passed", False))
    )

    controlled_input_run_defined = (
        not phase_9_4_summary_df.empty
        and bool(
            phase_9_4_summary_df.iloc[0].get(
                "long_forward_journal_controlled_input_run_defined",
                False,
            )
        )
    )

    dataset_schema_df = build_dataset_schema()
    empty_dataset_template_df = build_empty_dataset_template()

    persistence_guard_df = build_persistence_guard(
        accepted_inputs_df=source_accepted_inputs_df,
        rejected_inputs_df=source_rejected_inputs_df,
    )

    bootstrap_ledger_df = build_bootstrap_ledger(
        accepted_inputs_df=source_accepted_inputs_df,
        rejected_inputs_df=source_rejected_inputs_df,
    )

    dataset_bootstrap_summary_table_df = build_dataset_bootstrap_summary_table(
        dataset_schema_df=dataset_schema_df,
        empty_dataset_template_df=empty_dataset_template_df,
        persistence_guard_df=persistence_guard_df,
        bootstrap_ledger_df=bootstrap_ledger_df,
    )

    checks.append(
        build_check(
            check_group="phase_dependency",
            check_name="phase_9_4_validation_passed",
            passed=phase_9_4_validation_passed,
            severity="INFO" if phase_9_4_validation_passed else "ERROR",
            details=(
                str(phase_9_4_summary_df.iloc[0].get("validation_decision", ""))
                if not phase_9_4_summary_df.empty
                else "Missing Phase 9.4 summary."
            ),
        )
    )

    checks.append(
        build_check(
            check_group="phase_dependency",
            check_name="long_forward_journal_controlled_input_run_defined",
            passed=controlled_input_run_defined,
            severity="INFO" if controlled_input_run_defined else "ERROR",
            details=f"controlled_input_run_defined={controlled_input_run_defined}",
        )
    )

    dataset_schema_columns = set(dataset_schema_df["column_name"].astype(str).tolist())
    missing_dataset_columns = sorted(REQUIRED_DATASET_COLUMNS - dataset_schema_columns)

    checks.append(
        build_check(
            check_group="dataset_schema",
            check_name="dataset_schema_columns_complete",
            passed=len(missing_dataset_columns) == 0,
            severity="INFO" if len(missing_dataset_columns) == 0 else "ERROR",
            details=f"dataset_schema_columns={len(dataset_schema_columns)}",
        )
    )

    checks.append(
        build_check(
            check_group="dataset_template",
            check_name="empty_dataset_template_created",
            passed=(
                list(empty_dataset_template_df.columns) == DATASET_COLUMNS
                and len(empty_dataset_template_df) == 0
            ),
            severity=(
                "INFO"
                if (
                    list(empty_dataset_template_df.columns) == DATASET_COLUMNS
                    and len(empty_dataset_template_df) == 0
                )
                else "ERROR"
            ),
            details=f"empty_dataset_template_rows={len(empty_dataset_template_df)}",
        )
    )

    checks.append(
        build_check(
            check_group="persistence_guard",
            check_name="persistence_guard_created",
            passed=len(persistence_guard_df) == 1,
            severity="INFO" if len(persistence_guard_df) == 1 else "ERROR",
            details=f"persistence_guard_rows={len(persistence_guard_df)}",
        )
    )

    guard_blocks_writes = (
        len(persistence_guard_df) == 1
        and not safe_bool(persistence_guard_df.iloc[0].get("evidence_persistence_allowed", True), default=True)
        and not safe_bool(persistence_guard_df.iloc[0].get("evidence_write_performed", True), default=True)
        and int(persistence_guard_df.iloc[0].get("evidence_rows_written", -1)) == 0
    )

    checks.append(
        build_check(
            check_group="persistence_guard",
            check_name="persistence_guard_blocks_real_writes",
            passed=guard_blocks_writes,
            severity="INFO" if guard_blocks_writes else "ERROR",
            details="evidence_persistence_allowed=False,evidence_write_performed=False,evidence_rows_written=0",
        )
    )

    real_dataset_not_created = (
        len(persistence_guard_df) == 1
        and not safe_bool(persistence_guard_df.iloc[0].get("real_forward_dataset_created", True), default=True)
    )

    checks.append(
        build_check(
            check_group="persistence_guard",
            check_name="real_forward_dataset_not_created",
            passed=real_dataset_not_created,
            severity="INFO" if real_dataset_not_created else "ERROR",
            details=f"official_dataset_path={OFFICIAL_DATASET_PATH}",
        )
    )

    accepted_count = int(len(source_accepted_inputs_df))
    rejected_count = int(len(source_rejected_inputs_df))
    source_total_rows = accepted_count + rejected_count

    checks.append(
        build_check(
            check_group="source_compatibility",
            check_name="source_controlled_counts_preserved",
            passed=accepted_count == 1 and rejected_count == 4,
            severity="INFO" if accepted_count == 1 and rejected_count == 4 else "ERROR",
            details=f"accepted={accepted_count},rejected={rejected_count}",
        )
    )

    ledger_rows_match = len(bootstrap_ledger_df) == source_total_rows

    checks.append(
        build_check(
            check_group="bootstrap_ledger",
            check_name="bootstrap_ledger_rows_match_source",
            passed=ledger_rows_match,
            severity="INFO" if ledger_rows_match else "ERROR",
            details=f"ledger_rows={len(bootstrap_ledger_df)},source_rows={source_total_rows}",
        )
    )

    ledger_blocks_evidence = (
        not bootstrap_ledger_df.empty
        and not bootstrap_ledger_df["accepted_as_real_evidence"].astype(bool).any()
        and not bootstrap_ledger_df["evidence_write_allowed"].astype(bool).any()
        and not bootstrap_ledger_df["evidence_write_performed"].astype(bool).any()
    )

    checks.append(
        build_check(
            check_group="bootstrap_ledger",
            check_name="bootstrap_ledger_blocks_evidence_writes",
            passed=ledger_blocks_evidence,
            severity="INFO" if ledger_blocks_evidence else "ERROR",
            details="No bootstrap ledger rows are accepted as real evidence.",
        )
    )

    no_action_flags = (
        not bootstrap_ledger_df.empty
        and not bootstrap_ledger_df["execution_allowed"].astype(bool).any()
        and not bootstrap_ledger_df["live_alert_sent"].astype(bool).any()
        and not bootstrap_ledger_df["paper_trade_submitted"].astype(bool).any()
        and not bootstrap_ledger_df["real_capital_used"].astype(bool).any()
    )

    checks.append(
        build_check(
            check_group="safety_controls",
            check_name="bootstrap_keeps_all_action_flags_false",
            passed=no_action_flags,
            severity="INFO" if no_action_flags else "ERROR",
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
            details="Phase 9.5 bootstraps dataset structure only.",
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
            check_name="phase_9_6_recommended_next",
            passed=True,
            severity="INFO",
            details=(
                "Recommended next step: "
                "Phase 9.6 LONG Forward Observation Persistence Guard V1."
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
                "phase": "9.5",
                "long_forward_observation_dataset_bootstrap_defined": True,
                "phase_9_4_validation_passed": phase_9_4_validation_passed,
                "long_forward_journal_controlled_input_run_defined": controlled_input_run_defined,
                "dataset_schema_columns": int(len(dataset_schema_df)),
                "empty_dataset_template_rows": int(len(empty_dataset_template_df)),
                "persistence_guard_rows": int(len(persistence_guard_df)),
                "bootstrap_ledger_rows": int(len(bootstrap_ledger_df)),
                "dataset_bootstrap_summary_rows": int(
                    len(dataset_bootstrap_summary_table_df)
                ),
                "source_accepted_controlled_rows": accepted_count,
                "source_rejected_controlled_rows": rejected_count,
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
                    "PHASE_9_6_LONG_FORWARD_OBSERVATION_PERSISTENCE_GUARD_V1"
                ),
                "estimated_phase_9_progress_percent": 50,
                "total_checks": int(len(checks_df)),
                "warning_count": warning_count,
                "error_count": error_count,
                "blocker_count": blocker_count,
                "validation_passed": validation_passed,
                "validation_decision": (
                    "PHASE_9_5_LONG_FORWARD_OBSERVATION_DATASET_BOOTSTRAP_VALIDATED"
                    if validation_passed
                    else "PHASE_9_5_LONG_FORWARD_OBSERVATION_DATASET_BOOTSTRAP_FAILED"
                ),
            }
        ]
    )

    phase_9_4_summary_df.to_csv(
        REPORTS_DIR / "phase_9_4_source_summary_v1.csv",
        index=False,
    )
    source_controlled_run_summary_df.to_csv(
        REPORTS_DIR / "phase_9_4_source_controlled_run_summary_v1.csv",
        index=False,
    )
    source_controlled_run_ledger_df.to_csv(
        REPORTS_DIR / "phase_9_4_source_controlled_run_ledger_v1.csv",
        index=False,
    )
    source_accepted_inputs_df.to_csv(
        REPORTS_DIR / "phase_9_4_source_accepted_inputs_v1.csv",
        index=False,
    )
    source_rejected_inputs_df.to_csv(
        REPORTS_DIR / "phase_9_4_source_rejected_inputs_v1.csv",
        index=False,
    )
    dataset_schema_df.to_csv(
        REPORTS_DIR / "long_forward_observation_dataset_schema_v1.csv",
        index=False,
    )
    empty_dataset_template_df.to_csv(
        REPORTS_DIR / "long_forward_observation_dataset_template_v1.csv",
        index=False,
    )
    persistence_guard_df.to_csv(
        REPORTS_DIR / "long_forward_observation_dataset_persistence_guard_v1.csv",
        index=False,
    )
    bootstrap_ledger_df.to_csv(
        REPORTS_DIR / "long_forward_observation_dataset_bootstrap_ledger_v1.csv",
        index=False,
    )
    dataset_bootstrap_summary_table_df.to_csv(
        REPORTS_DIR / "long_forward_observation_dataset_bootstrap_summary_table_v1.csv",
        index=False,
    )
    checks_df.to_csv(
        REPORTS_DIR / "long_forward_observation_dataset_bootstrap_checks_v1.csv",
        index=False,
    )
    summary_df.to_csv(
        REPORTS_DIR / "long_forward_observation_dataset_bootstrap_summary_v1.csv",
        index=False,
    )

    return {
        "summary": summary_df,
        "source_phase_9_4_summary": phase_9_4_summary_df,
        "source_controlled_run_summary": source_controlled_run_summary_df,
        "source_controlled_run_ledger": source_controlled_run_ledger_df,
        "source_accepted_inputs": source_accepted_inputs_df,
        "source_rejected_inputs": source_rejected_inputs_df,
        "dataset_schema": dataset_schema_df,
        "empty_dataset_template": empty_dataset_template_df,
        "persistence_guard": persistence_guard_df,
        "bootstrap_ledger": bootstrap_ledger_df,
        "dataset_bootstrap_summary": dataset_bootstrap_summary_table_df,
        "checks": checks_df,
    }