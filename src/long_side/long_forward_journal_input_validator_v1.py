from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from src.long_side.long_forward_signal_journal_v1 import (
    JOURNAL_COLUMNS,
    validate_long_forward_signal_journal,
)


REPORTS_DIR = Path("reports/phase_9_3_long_forward_journal_input_validator_v1")

PHASE_9_2_JOURNAL_DOC_PATH = Path("docs/PHASE_9_LONG_FORWARD_SIGNAL_JOURNAL.md")
PHASE_9_3_VALIDATOR_DOC_PATH = Path(
    "docs/PHASE_9_LONG_FORWARD_JOURNAL_INPUT_VALIDATOR.md"
)

PRIMARY_RESEARCH_CANDIDATE = "LONG_BASE_FAILED_BREAKDOWN_V1"
SECONDARY_REFERENCE_CANDIDATE = "LONG_BASE_LIQUIDITY_SWEEP_V1"

BLOCKED_CANDIDATES = [
    "LONG_BASE_FIB_PULLBACK_V1",
    "LONG_BASE_MTF_BULLISH_CONTINUATION_V1",
]

VALIDATOR_STATUS = "LONG_FORWARD_JOURNAL_INPUT_VALIDATOR_ONLY"

ALLOWED_INPUT_SIGNAL_STATES = {
    "CANDIDATE",
    "WATCH_ONLY",
    "INVALIDATED",
    "CLOSED",
}

ALLOWED_RESOLUTION_STATES = {
    "UNRESOLVED",
    "TARGET_HIT",
    "STOP_HIT",
    "INVALIDATED",
    "EXPIRED",
    "CLOSED_MANUALLY",
}

REQUIRED_JOURNAL_COLUMNS = set(JOURNAL_COLUMNS)

SAFETY_FLAGS = {
    "forward_observation_started": False,
    "signal_generation_enabled": False,
    "real_forward_signals_recorded": False,
    "journal_real_rows_accepted": False,
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


def safe_float(value: Any, default: float = 0.0) -> float:
    try:
        if pd.isna(value):
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def safe_int(value: Any, default: int = 0) -> int:
    try:
        if pd.isna(value):
            return default
        return int(value)
    except (TypeError, ValueError):
        return default


def non_empty(value: Any) -> bool:
    if value is None:
        return False

    if pd.isna(value):
        return False

    return str(value).strip() != ""


def build_controlled_input_rows() -> pd.DataFrame:
    rows = [
        {
            "observation_id": "CTL_LONG_VALID_001",
            "journal_status": VALIDATOR_STATUS,
            "observed_at": "2026-06-30 12:00:00",
            "symbol": "BTCUSDT",
            "timeframe": "15m",
            "candidate_id": PRIMARY_RESEARCH_CANDIDATE,
            "observation_role": "PRIMARY_FORWARD_OBSERVATION",
            "direction": "LONG",
            "signal_state": "CANDIDATE",
            "market_context": "Controlled synthetic row. Valid LONG structure.",
            "entry_price": 60000.0,
            "stop_price": 59400.0,
            "target_price": 61500.0,
            "risk_reward": 2.5,
            "invalidation_level": 59400.0,
            "cost_profile": "STRESS_FRICTION",
            "readiness_source": "PHASE_8_11_LONG_BASELINE_READINESS_GATE_VALIDATED",
            "manual_review_required": True,
            "manual_review_status": "PENDING_MANUAL_REVIEW",
            "reviewer_notes": "Controlled validator test only.",
            "execution_allowed": False,
            "live_alert_sent": False,
            "paper_trade_submitted": False,
            "real_capital_used": False,
            "resolution_status": "UNRESOLVED",
            "result_r": 0.0,
            "mfe_r": 0.0,
            "mae_r": 0.0,
            "bars_to_resolution": 0,
            "notes": "Controlled valid candidate row. Not real evidence.",
            "created_at_utc": "2026-06-30T16:00:00Z",
            "updated_at_utc": "2026-06-30T16:00:00Z",
        },
        {
            "observation_id": "CTL_LONG_SECONDARY_001",
            "journal_status": VALIDATOR_STATUS,
            "observed_at": "2026-06-30 12:15:00",
            "symbol": "BTCUSDT",
            "timeframe": "15m",
            "candidate_id": SECONDARY_REFERENCE_CANDIDATE,
            "observation_role": "SECONDARY_REFERENCE_WATCHLIST",
            "direction": "LONG",
            "signal_state": "WATCH_ONLY",
            "market_context": "Controlled secondary reference row.",
            "entry_price": 60000.0,
            "stop_price": 59400.0,
            "target_price": 61500.0,
            "risk_reward": 2.5,
            "invalidation_level": 59400.0,
            "cost_profile": "STRESS_FRICTION",
            "readiness_source": "PHASE_8_11_LONG_BASELINE_READINESS_GATE_VALIDATED",
            "manual_review_required": True,
            "manual_review_status": "REFERENCE_ONLY",
            "reviewer_notes": "Secondary reference must not become active observation.",
            "execution_allowed": False,
            "live_alert_sent": False,
            "paper_trade_submitted": False,
            "real_capital_used": False,
            "resolution_status": "UNRESOLVED",
            "result_r": 0.0,
            "mfe_r": 0.0,
            "mae_r": 0.0,
            "bars_to_resolution": 0,
            "notes": "Controlled reference row. Should be rejected for active acceptance.",
            "created_at_utc": "2026-06-30T16:15:00Z",
            "updated_at_utc": "2026-06-30T16:15:00Z",
        },
        {
            "observation_id": "CTL_LONG_BLOCKED_001",
            "journal_status": VALIDATOR_STATUS,
            "observed_at": "2026-06-30 12:30:00",
            "symbol": "BTCUSDT",
            "timeframe": "15m",
            "candidate_id": "LONG_BASE_FIB_PULLBACK_V1",
            "observation_role": "BLOCKED_NOT_OBSERVED",
            "direction": "LONG",
            "signal_state": "CANDIDATE",
            "market_context": "Controlled blocked candidate row.",
            "entry_price": 60000.0,
            "stop_price": 59400.0,
            "target_price": 61500.0,
            "risk_reward": 2.5,
            "invalidation_level": 59400.0,
            "cost_profile": "STRESS_FRICTION",
            "readiness_source": "PHASE_8_11_LONG_BASELINE_READINESS_GATE_VALIDATED",
            "manual_review_required": True,
            "manual_review_status": "BLOCKED",
            "reviewer_notes": "Blocked candidate should be rejected.",
            "execution_allowed": False,
            "live_alert_sent": False,
            "paper_trade_submitted": False,
            "real_capital_used": False,
            "resolution_status": "UNRESOLVED",
            "result_r": 0.0,
            "mfe_r": 0.0,
            "mae_r": 0.0,
            "bars_to_resolution": 0,
            "notes": "Controlled blocked row.",
            "created_at_utc": "2026-06-30T16:30:00Z",
            "updated_at_utc": "2026-06-30T16:30:00Z",
        },
        {
            "observation_id": "CTL_LONG_BAD_PRICE_001",
            "journal_status": VALIDATOR_STATUS,
            "observed_at": "2026-06-30 12:45:00",
            "symbol": "BTCUSDT",
            "timeframe": "15m",
            "candidate_id": PRIMARY_RESEARCH_CANDIDATE,
            "observation_role": "PRIMARY_FORWARD_OBSERVATION",
            "direction": "LONG",
            "signal_state": "CANDIDATE",
            "market_context": "Controlled invalid price structure row.",
            "entry_price": 60000.0,
            "stop_price": 60600.0,
            "target_price": 61500.0,
            "risk_reward": 2.5,
            "invalidation_level": 60600.0,
            "cost_profile": "STRESS_FRICTION",
            "readiness_source": "PHASE_8_11_LONG_BASELINE_READINESS_GATE_VALIDATED",
            "manual_review_required": True,
            "manual_review_status": "PENDING_MANUAL_REVIEW",
            "reviewer_notes": "Invalid LONG structure should be rejected.",
            "execution_allowed": False,
            "live_alert_sent": False,
            "paper_trade_submitted": False,
            "real_capital_used": False,
            "resolution_status": "UNRESOLVED",
            "result_r": 0.0,
            "mfe_r": 0.0,
            "mae_r": 0.0,
            "bars_to_resolution": 0,
            "notes": "Controlled invalid price row.",
            "created_at_utc": "2026-06-30T16:45:00Z",
            "updated_at_utc": "2026-06-30T16:45:00Z",
        },
        {
            "observation_id": "CTL_LONG_DANGEROUS_FLAGS_001",
            "journal_status": VALIDATOR_STATUS,
            "observed_at": "2026-06-30 13:00:00",
            "symbol": "BTCUSDT",
            "timeframe": "15m",
            "candidate_id": PRIMARY_RESEARCH_CANDIDATE,
            "observation_role": "PRIMARY_FORWARD_OBSERVATION",
            "direction": "LONG",
            "signal_state": "CANDIDATE",
            "market_context": "Controlled dangerous execution flags row.",
            "entry_price": 60000.0,
            "stop_price": 59400.0,
            "target_price": 61500.0,
            "risk_reward": 2.5,
            "invalidation_level": 59400.0,
            "cost_profile": "STRESS_FRICTION",
            "readiness_source": "PHASE_8_11_LONG_BASELINE_READINESS_GATE_VALIDATED",
            "manual_review_required": True,
            "manual_review_status": "PENDING_MANUAL_REVIEW",
            "reviewer_notes": "Dangerous flags should be rejected.",
            "execution_allowed": True,
            "live_alert_sent": True,
            "paper_trade_submitted": True,
            "real_capital_used": True,
            "resolution_status": "UNRESOLVED",
            "result_r": 0.0,
            "mfe_r": 0.0,
            "mae_r": 0.0,
            "bars_to_resolution": 0,
            "notes": "Controlled dangerous flag row.",
            "created_at_utc": "2026-06-30T17:00:00Z",
            "updated_at_utc": "2026-06-30T17:00:00Z",
        },
    ]

    return pd.DataFrame(rows, columns=JOURNAL_COLUMNS)


def validate_required_columns(input_df: pd.DataFrame) -> pd.DataFrame:
    missing_columns = sorted(REQUIRED_JOURNAL_COLUMNS - set(input_df.columns))
    extra_columns = sorted(set(input_df.columns) - REQUIRED_JOURNAL_COLUMNS)

    return pd.DataFrame(
        [
            {
                "column_check": "required_columns_present",
                "passed": len(missing_columns) == 0,
                "severity": "INFO" if len(missing_columns) == 0 else "ERROR",
                "details": "missing_columns=" + ",".join(missing_columns),
                "blocker": len(missing_columns) > 0,
            },
            {
                "column_check": "no_unknown_extra_columns_required",
                "passed": True,
                "severity": "INFO",
                "details": "extra_columns=" + ",".join(extra_columns),
                "blocker": False,
            },
        ]
    )


def validate_single_row(row: pd.Series) -> dict[str, Any]:
    observation_id = str(row.get("observation_id", "")).strip()
    candidate_id = str(row.get("candidate_id", "")).strip()
    direction = str(row.get("direction", "")).strip().upper()
    signal_state = str(row.get("signal_state", "")).strip().upper()
    resolution_status = str(row.get("resolution_status", "")).strip().upper()

    entry_price = safe_float(row.get("entry_price", 0.0))
    stop_price = safe_float(row.get("stop_price", 0.0))
    target_price = safe_float(row.get("target_price", 0.0))
    risk_reward = safe_float(row.get("risk_reward", 0.0))
    invalidation_level = safe_float(row.get("invalidation_level", 0.0))

    manual_review_required = safe_bool(row.get("manual_review_required", False))

    execution_allowed = safe_bool(row.get("execution_allowed", True), default=True)
    live_alert_sent = safe_bool(row.get("live_alert_sent", True), default=True)
    paper_trade_submitted = safe_bool(
        row.get("paper_trade_submitted", True),
        default=True,
    )
    real_capital_used = safe_bool(row.get("real_capital_used", True), default=True)

    required_identity_fields_present = all(
        [
            non_empty(row.get("observation_id", "")),
            non_empty(row.get("observed_at", "")),
            non_empty(row.get("symbol", "")),
            non_empty(row.get("timeframe", "")),
            non_empty(row.get("candidate_id", "")),
            non_empty(row.get("observation_role", "")),
            non_empty(row.get("direction", "")),
            non_empty(row.get("signal_state", "")),
        ]
    )

    candidate_is_primary = candidate_id == PRIMARY_RESEARCH_CANDIDATE
    candidate_is_secondary = candidate_id == SECONDARY_REFERENCE_CANDIDATE
    candidate_is_blocked = candidate_id in BLOCKED_CANDIDATES

    candidate_allowed_for_active_input = candidate_is_primary

    long_price_structure_valid = (
        stop_price > 0.0
        and entry_price > 0.0
        and target_price > 0.0
        and stop_price < entry_price < target_price
    )

    risk_reward_valid = risk_reward > 0.0
    invalidation_valid = invalidation_level > 0.0 and invalidation_level <= entry_price

    safety_flags_clean = (
        execution_allowed is False
        and live_alert_sent is False
        and paper_trade_submitted is False
        and real_capital_used is False
    )

    row_valid = (
        required_identity_fields_present
        and candidate_allowed_for_active_input
        and not candidate_is_secondary
        and not candidate_is_blocked
        and direction == "LONG"
        and signal_state in ALLOWED_INPUT_SIGNAL_STATES
        and resolution_status in ALLOWED_RESOLUTION_STATES
        and manual_review_required
        and long_price_structure_valid
        and risk_reward_valid
        and invalidation_valid
        and safety_flags_clean
    )

    rejection_reasons: list[str] = []

    if not required_identity_fields_present:
        rejection_reasons.append("MISSING_REQUIRED_IDENTITY_FIELDS")

    if not candidate_allowed_for_active_input:
        rejection_reasons.append("CANDIDATE_NOT_ALLOWED_FOR_ACTIVE_LONG_INPUT")

    if candidate_is_secondary:
        rejection_reasons.append("SECONDARY_REFERENCE_ONLY")

    if candidate_is_blocked:
        rejection_reasons.append("BLOCKED_CANDIDATE")

    if direction != "LONG":
        rejection_reasons.append("DIRECTION_NOT_LONG")

    if signal_state not in ALLOWED_INPUT_SIGNAL_STATES:
        rejection_reasons.append("INVALID_SIGNAL_STATE")

    if resolution_status not in ALLOWED_RESOLUTION_STATES:
        rejection_reasons.append("INVALID_RESOLUTION_STATUS")

    if not manual_review_required:
        rejection_reasons.append("MANUAL_REVIEW_NOT_REQUIRED")

    if not long_price_structure_valid:
        rejection_reasons.append("INVALID_LONG_PRICE_STRUCTURE")

    if not risk_reward_valid:
        rejection_reasons.append("INVALID_RISK_REWARD")

    if not invalidation_valid:
        rejection_reasons.append("INVALID_INVALIDATION_LEVEL")

    if not safety_flags_clean:
        rejection_reasons.append("DANGEROUS_EXECUTION_OR_ALERT_FLAGS")

    if row_valid:
        validation_decision = "VALIDATED_FOR_FUTURE_FORWARD_OBSERVATION_INPUT"
        validation_status = "CONTROLLED_VALID_INPUT_ONLY"
    else:
        validation_decision = "REJECTED_LONG_FORWARD_JOURNAL_INPUT"
        validation_status = "CONTROLLED_REJECTED_INPUT"

    return {
        "observation_id": observation_id,
        "candidate_id": candidate_id,
        "candidate_is_primary": candidate_is_primary,
        "candidate_is_secondary": candidate_is_secondary,
        "candidate_is_blocked": candidate_is_blocked,
        "direction": direction,
        "signal_state": signal_state,
        "resolution_status": resolution_status,
        "required_identity_fields_present": required_identity_fields_present,
        "manual_review_required": manual_review_required,
        "long_price_structure_valid": long_price_structure_valid,
        "risk_reward_valid": risk_reward_valid,
        "invalidation_valid": invalidation_valid,
        "safety_flags_clean": safety_flags_clean,
        "execution_allowed": execution_allowed,
        "live_alert_sent": live_alert_sent,
        "paper_trade_submitted": paper_trade_submitted,
        "real_capital_used": real_capital_used,
        "row_valid": row_valid,
        "validation_decision": validation_decision,
        "validation_status": validation_status,
        "rejection_reasons": ",".join(rejection_reasons),
    }


def validate_journal_input_rows(input_df: pd.DataFrame) -> dict[str, pd.DataFrame]:
    column_checks_df = validate_required_columns(input_df)

    if column_checks_df["blocker"].astype(bool).any():
        row_checks_df = pd.DataFrame()
        accepted_df = pd.DataFrame(columns=list(input_df.columns))
        rejected_df = input_df.copy()
        rejected_df["validation_decision"] = "REJECTED_LONG_FORWARD_JOURNAL_INPUT"
        rejected_df["validation_status"] = "MISSING_REQUIRED_COLUMNS"
        rejected_df["rejection_reasons"] = "MISSING_REQUIRED_COLUMNS"

        return {
            "column_checks": column_checks_df,
            "row_checks": row_checks_df,
            "accepted_inputs": accepted_df,
            "rejected_inputs": rejected_df,
        }

    row_check_rows: list[dict[str, Any]] = []

    for _, row in input_df.iterrows():
        row_check_rows.append(validate_single_row(row))

    row_checks_df = pd.DataFrame(row_check_rows)

    accepted_ids = set(
        row_checks_df[row_checks_df["row_valid"].astype(bool)]["observation_id"]
        .astype(str)
        .tolist()
    )

    rejected_ids = set(
        row_checks_df[~row_checks_df["row_valid"].astype(bool)]["observation_id"]
        .astype(str)
        .tolist()
    )

    accepted_df = input_df[
        input_df["observation_id"].astype(str).isin(accepted_ids)
    ].copy()
    rejected_df = input_df[
        input_df["observation_id"].astype(str).isin(rejected_ids)
    ].copy()

    if not accepted_df.empty:
        accepted_df["validation_decision"] = (
            "VALIDATED_FOR_FUTURE_FORWARD_OBSERVATION_INPUT"
        )
        accepted_df["validation_status"] = "CONTROLLED_VALID_INPUT_ONLY"
        accepted_df["accepted_as_real_evidence"] = False
        accepted_df["execution_allowed"] = False
        accepted_df["live_alert_sent"] = False
        accepted_df["paper_trade_submitted"] = False
        accepted_df["real_capital_used"] = False

    if not rejected_df.empty:
        rejection_lookup = row_checks_df.set_index("observation_id")[
            "rejection_reasons"
        ].to_dict()
        rejected_df["validation_decision"] = "REJECTED_LONG_FORWARD_JOURNAL_INPUT"
        rejected_df["validation_status"] = "CONTROLLED_REJECTED_INPUT"
        rejected_df["accepted_as_real_evidence"] = False
        rejected_df["rejection_reasons"] = rejected_df["observation_id"].map(
            rejection_lookup
        )

    return {
        "column_checks": column_checks_df,
        "row_checks": row_checks_df,
        "accepted_inputs": accepted_df,
        "rejected_inputs": rejected_df,
    }


def validate_long_forward_journal_input_validator() -> dict[str, pd.DataFrame]:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    checks: list[dict[str, Any]] = []

    phase_anchors = {
        "phase_9_2_journal_doc_exists": PHASE_9_2_JOURNAL_DOC_PATH,
        "phase_9_3_validator_doc_exists": PHASE_9_3_VALIDATOR_DOC_PATH,
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

    phase_9_2_result = validate_long_forward_signal_journal()

    phase_9_2_summary_df = phase_9_2_result["summary"]
    source_journal_schema_df = phase_9_2_result["journal_schema"]
    source_candidate_registry_df = phase_9_2_result["source_candidate_registry"]

    phase_9_2_validation_passed = (
        not phase_9_2_summary_df.empty
        and bool(phase_9_2_summary_df.iloc[0].get("validation_passed", False))
    )

    journal_defined = (
        not phase_9_2_summary_df.empty
        and bool(
            phase_9_2_summary_df.iloc[0].get(
                "long_forward_signal_journal_defined",
                False,
            )
        )
    )

    controlled_input_rows_df = build_controlled_input_rows()
    validation_result = validate_journal_input_rows(controlled_input_rows_df)

    column_checks_df = validation_result["column_checks"]
    row_checks_df = validation_result["row_checks"]
    accepted_inputs_df = validation_result["accepted_inputs"]
    rejected_inputs_df = validation_result["rejected_inputs"]

    checks.append(
        build_check(
            check_group="phase_dependency",
            check_name="phase_9_2_validation_passed",
            passed=phase_9_2_validation_passed,
            severity="INFO" if phase_9_2_validation_passed else "ERROR",
            details=(
                str(phase_9_2_summary_df.iloc[0].get("validation_decision", ""))
                if not phase_9_2_summary_df.empty
                else "Missing Phase 9.2 summary."
            ),
        )
    )

    checks.append(
        build_check(
            check_group="phase_dependency",
            check_name="long_forward_signal_journal_defined",
            passed=journal_defined,
            severity="INFO" if journal_defined else "ERROR",
            details=f"journal_defined={journal_defined}",
        )
    )

    source_journal_columns = set(
        source_journal_schema_df["column_name"].astype(str).tolist()
    )
    missing_source_columns = sorted(REQUIRED_JOURNAL_COLUMNS - source_journal_columns)

    checks.append(
        build_check(
            check_group="schema_dependency",
            check_name="phase_9_2_journal_schema_available",
            passed=len(missing_source_columns) == 0,
            severity="INFO" if len(missing_source_columns) == 0 else "ERROR",
            details="missing_source_columns=" + ",".join(missing_source_columns),
        )
    )

    column_check_blockers = int(column_checks_df["blocker"].astype(bool).sum())

    checks.append(
        build_check(
            check_group="input_validator",
            check_name="controlled_input_columns_valid",
            passed=column_check_blockers == 0,
            severity="INFO" if column_check_blockers == 0 else "ERROR",
            details=f"column_check_blockers={column_check_blockers}",
        )
    )

    accepted_count = int(len(accepted_inputs_df))
    rejected_count = int(len(rejected_inputs_df))

    checks.append(
        build_check(
            check_group="input_validator",
            check_name="controlled_valid_row_accepted",
            passed=accepted_count == 1,
            severity="INFO" if accepted_count == 1 else "ERROR",
            details=f"accepted_count={accepted_count}",
        )
    )

    checks.append(
        build_check(
            check_group="input_validator",
            check_name="controlled_invalid_rows_rejected",
            passed=rejected_count == 4,
            severity="INFO" if rejected_count == 4 else "ERROR",
            details=f"rejected_count={rejected_count}",
        )
    )

    primary_valid_present = (
        not accepted_inputs_df.empty
        and accepted_inputs_df["candidate_id"]
        .astype(str)
        .eq(PRIMARY_RESEARCH_CANDIDATE)
        .all()
    )

    checks.append(
        build_check(
            check_group="candidate_scope",
            check_name="only_primary_candidate_accepted",
            passed=primary_valid_present,
            severity="INFO" if primary_valid_present else "ERROR",
            details=(
                "accepted_candidates="
                + ",".join(accepted_inputs_df["candidate_id"].astype(str).unique())
                if not accepted_inputs_df.empty
                else "accepted_candidates="
            ),
        )
    )

    secondary_rejected = (
        not rejected_inputs_df.empty
        and SECONDARY_REFERENCE_CANDIDATE
        in set(rejected_inputs_df["candidate_id"].astype(str).tolist())
    )

    checks.append(
        build_check(
            check_group="candidate_scope",
            check_name="secondary_reference_rejected_for_active_input",
            passed=secondary_rejected,
            severity="INFO" if secondary_rejected else "ERROR",
            details=f"secondary={SECONDARY_REFERENCE_CANDIDATE}",
        )
    )

    blocked_rejected = (
        not rejected_inputs_df.empty
        and any(
            candidate in set(rejected_inputs_df["candidate_id"].astype(str).tolist())
            for candidate in BLOCKED_CANDIDATES
        )
    )

    checks.append(
        build_check(
            check_group="candidate_scope",
            check_name="blocked_candidate_rejected",
            passed=blocked_rejected,
            severity="INFO" if blocked_rejected else "ERROR",
            details="blocked=" + ",".join(BLOCKED_CANDIDATES),
        )
    )

    accepted_safety_clean = (
        not accepted_inputs_df.empty
        and not accepted_inputs_df["execution_allowed"].astype(bool).any()
        and not accepted_inputs_df["live_alert_sent"].astype(bool).any()
        and not accepted_inputs_df["paper_trade_submitted"].astype(bool).any()
        and not accepted_inputs_df["real_capital_used"].astype(bool).any()
    )

    checks.append(
        build_check(
            check_group="safety_controls",
            check_name="accepted_rows_keep_execution_flags_false",
            passed=accepted_safety_clean,
            severity="INFO" if accepted_safety_clean else "ERROR",
            details="Accepted controlled rows keep execution, alerts, paper and real capital disabled.",
        )
    )

    accepted_real_evidence_false = (
        not accepted_inputs_df.empty
        and "accepted_as_real_evidence" in accepted_inputs_df.columns
        and not accepted_inputs_df["accepted_as_real_evidence"].astype(bool).any()
    )

    checks.append(
        build_check(
            check_group="scope_control",
            check_name="accepted_rows_not_real_evidence",
            passed=accepted_real_evidence_false,
            severity="INFO" if accepted_real_evidence_false else "ERROR",
            details="Controlled valid rows are not accepted as real evidence in Phase 9.3.",
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
            details="Phase 9.3 validates controlled synthetic rows only.",
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
            check_name="phase_9_4_recommended_next",
            passed=True,
            severity="INFO",
            details="Recommended next step: Phase 9.4 LONG Forward Journal Controlled Input Run V1.",
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
                "phase": "9.3",
                "long_forward_journal_input_validator_defined": True,
                "phase_9_2_validation_passed": phase_9_2_validation_passed,
                "long_forward_signal_journal_defined": journal_defined,
                "controlled_input_rows": int(len(controlled_input_rows_df)),
                "column_check_rows": int(len(column_checks_df)),
                "row_check_rows": int(len(row_checks_df)),
                "accepted_controlled_rows": accepted_count,
                "rejected_controlled_rows": rejected_count,
                "primary_research_candidate_id": PRIMARY_RESEARCH_CANDIDATE,
                "secondary_reference_candidate_id": SECONDARY_REFERENCE_CANDIDATE,
                "only_primary_candidate_accepted": primary_valid_present,
                "secondary_reference_rejected_for_active_input": secondary_rejected,
                "blocked_candidate_rejected": blocked_rejected,
                "real_forward_signals_recorded": False,
                "journal_real_rows_accepted": False,
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
                "recommended_next_phase": "PHASE_9_4_LONG_FORWARD_JOURNAL_CONTROLLED_INPUT_RUN_V1",
                "estimated_phase_9_progress_percent": 30,
                "total_checks": int(len(checks_df)),
                "warning_count": warning_count,
                "error_count": error_count,
                "blocker_count": blocker_count,
                "validation_passed": validation_passed,
                "validation_decision": (
                    "PHASE_9_3_LONG_FORWARD_JOURNAL_INPUT_VALIDATOR_VALIDATED"
                    if validation_passed
                    else "PHASE_9_3_LONG_FORWARD_JOURNAL_INPUT_VALIDATOR_FAILED"
                ),
            }
        ]
    )

    phase_9_2_summary_df.to_csv(
        REPORTS_DIR / "phase_9_2_source_summary_v1.csv",
        index=False,
    )
    source_candidate_registry_df.to_csv(
        REPORTS_DIR / "phase_9_1_source_candidate_registry_v1.csv",
        index=False,
    )
    source_journal_schema_df.to_csv(
        REPORTS_DIR / "phase_9_2_source_journal_schema_v1.csv",
        index=False,
    )
    controlled_input_rows_df.to_csv(
        REPORTS_DIR / "long_forward_journal_controlled_input_rows_v1.csv",
        index=False,
    )
    column_checks_df.to_csv(
        REPORTS_DIR / "long_forward_journal_input_column_checks_v1.csv",
        index=False,
    )
    row_checks_df.to_csv(
        REPORTS_DIR / "long_forward_journal_input_row_checks_v1.csv",
        index=False,
    )
    accepted_inputs_df.to_csv(
        REPORTS_DIR / "long_forward_journal_input_accepted_controlled_rows_v1.csv",
        index=False,
    )
    rejected_inputs_df.to_csv(
        REPORTS_DIR / "long_forward_journal_input_rejected_controlled_rows_v1.csv",
        index=False,
    )
    checks_df.to_csv(
        REPORTS_DIR / "long_forward_journal_input_validator_checks_v1.csv",
        index=False,
    )
    summary_df.to_csv(
        REPORTS_DIR / "long_forward_journal_input_validator_summary_v1.csv",
        index=False,
    )

    return {
        "summary": summary_df,
        "source_phase_9_2_summary": phase_9_2_summary_df,
        "source_candidate_registry": source_candidate_registry_df,
        "source_journal_schema": source_journal_schema_df,
        "controlled_input_rows": controlled_input_rows_df,
        "column_checks": column_checks_df,
        "row_checks": row_checks_df,
        "accepted_inputs": accepted_inputs_df,
        "rejected_inputs": rejected_inputs_df,
        "checks": checks_df,
    }