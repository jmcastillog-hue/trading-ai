from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from src.long_side.long_forward_observation_framework_v1 import (
    OBSERVATION_SCHEMA_COLUMNS,
    validate_long_forward_observation_framework,
)


REPORTS_DIR = Path("reports/phase_9_2_long_forward_signal_journal_v1")

PHASE_9_1_FRAMEWORK_DOC_PATH = Path("docs/PHASE_9_LONG_FORWARD_OBSERVATION_FRAMEWORK.md")
PHASE_9_2_JOURNAL_DOC_PATH = Path("docs/PHASE_9_LONG_FORWARD_SIGNAL_JOURNAL.md")

PRIMARY_RESEARCH_CANDIDATE = "LONG_BASE_FAILED_BREAKDOWN_V1"
SECONDARY_REFERENCE_CANDIDATE = "LONG_BASE_LIQUIDITY_SWEEP_V1"

BLOCKED_CANDIDATES = [
    "LONG_BASE_FIB_PULLBACK_V1",
    "LONG_BASE_MTF_BULLISH_CONTINUATION_V1",
]

JOURNAL_STATUS = "LONG_FORWARD_SIGNAL_JOURNAL_TEMPLATE_ONLY"

JOURNAL_COLUMNS = [
    "observation_id",
    "journal_status",
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
]

REQUIRED_JOURNAL_COLUMNS = set(JOURNAL_COLUMNS)

ALLOWED_SIGNAL_STATES = {
    "TEMPLATE_ONLY",
    "CANDIDATE",
    "WATCH_ONLY",
    "INVALIDATED",
    "CLOSED",
}

ALLOWED_PHASE_9_2_SIGNAL_STATES = {
    "TEMPLATE_ONLY",
}

ALLOWED_RESOLUTION_STATES = {
    "UNRESOLVED",
    "TARGET_HIT",
    "STOP_HIT",
    "INVALIDATED",
    "EXPIRED",
    "CLOSED_MANUALLY",
}

SAFETY_FLAGS = {
    "forward_observation_started": False,
    "signal_generation_enabled": False,
    "real_forward_signals_recorded": False,
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

        if normalized in {"false", "0", "no", "n"}:
            return False

    if pd.isna(value):
        return default

    return bool(value)


def build_journal_schema() -> pd.DataFrame:
    descriptions = {
        "observation_id": "Unique future journal observation identifier.",
        "journal_status": "Journal row status.",
        "observed_at": "Timestamp when the potential LONG signal was observed.",
        "symbol": "Market symbol.",
        "timeframe": "Observed timeframe.",
        "candidate_id": "LONG candidate associated with the observation.",
        "observation_role": "Primary or secondary observation role.",
        "direction": "Must remain LONG.",
        "signal_state": "Signal state. Phase 9.2 only allows TEMPLATE_ONLY.",
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
    }

    rows: list[dict[str, Any]] = []

    for column in JOURNAL_COLUMNS:
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
                "journal_status": JOURNAL_STATUS,
            }
        )

    return pd.DataFrame(rows)


def build_empty_journal_template() -> pd.DataFrame:
    return pd.DataFrame(columns=JOURNAL_COLUMNS)


def build_controlled_template_row() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "observation_id": "TEMPLATE_ONLY_DO_NOT_USE_FOR_SIGNAL",
                "journal_status": JOURNAL_STATUS,
                "observed_at": "",
                "symbol": "BTCUSDT",
                "timeframe": "15m",
                "candidate_id": PRIMARY_RESEARCH_CANDIDATE,
                "observation_role": "PRIMARY_FORWARD_OBSERVATION",
                "direction": "LONG",
                "signal_state": "TEMPLATE_ONLY",
                "market_context": "Template row only. Not a real market observation.",
                "entry_price": 0.0,
                "stop_price": 0.0,
                "target_price": 0.0,
                "risk_reward": 0.0,
                "invalidation_level": 0.0,
                "cost_profile": "STRESS_FRICTION",
                "readiness_source": "PHASE_8_11_LONG_BASELINE_READINESS_GATE_VALIDATED",
                "manual_review_required": True,
                "manual_review_status": "TEMPLATE_ONLY",
                "reviewer_notes": "Template only. Do not use as evidence.",
                "execution_allowed": False,
                "live_alert_sent": False,
                "paper_trade_submitted": False,
                "real_capital_used": False,
                "resolution_status": "UNRESOLVED",
                "result_r": 0.0,
                "mfe_r": 0.0,
                "mae_r": 0.0,
                "bars_to_resolution": 0,
                "notes": "Template row only. No real forward observation.",
                "created_at_utc": "",
                "updated_at_utc": "",
            }
        ]
    )


def build_journal_rules(candidate_registry_df: pd.DataFrame) -> pd.DataFrame:
    primary_registry = candidate_registry_df[
        candidate_registry_df["candidate_id"].astype(str).eq(PRIMARY_RESEARCH_CANDIDATE)
    ].copy()

    secondary_registry = candidate_registry_df[
        candidate_registry_df["candidate_id"].astype(str).eq(SECONDARY_REFERENCE_CANDIDATE)
    ].copy()

    blocked_registry = candidate_registry_df[
        candidate_registry_df["candidate_id"].astype(str).isin(BLOCKED_CANDIDATES)
    ].copy()

    primary_eligible = (
        len(primary_registry) == 1
        and str(primary_registry.iloc[0]["observation_framework_decision"])
        == "FORWARD_OBSERVATION_ELIGIBLE"
    )

    secondary_reference_only = (
        len(secondary_registry) == 1
        and str(secondary_registry.iloc[0]["observation_framework_decision"])
        == "REFERENCE_WATCHLIST_ONLY"
    )

    blocked_excluded = (
        len(blocked_registry) == len(BLOCKED_CANDIDATES)
        and blocked_registry["observation_framework_decision"]
        .astype(str)
        .eq("EXCLUDED_BLOCKED")
        .all()
    )

    rules = [
        {
            "rule_name": "primary_candidate_allowed_for_future_journal",
            "rule_passed": primary_eligible,
            "severity": "INFO" if primary_eligible else "ERROR",
            "details": PRIMARY_RESEARCH_CANDIDATE,
        },
        {
            "rule_name": "secondary_candidate_reference_only",
            "rule_passed": secondary_reference_only,
            "severity": "INFO" if secondary_reference_only else "ERROR",
            "details": SECONDARY_REFERENCE_CANDIDATE,
        },
        {
            "rule_name": "blocked_candidates_excluded",
            "rule_passed": blocked_excluded,
            "severity": "INFO" if blocked_excluded else "ERROR",
            "details": ",".join(BLOCKED_CANDIDATES),
        },
        {
            "rule_name": "phase_9_2_signal_state_template_only",
            "rule_passed": True,
            "severity": "INFO",
            "details": "Phase 9.2 only allows TEMPLATE_ONLY rows.",
        },
        {
            "rule_name": "manual_review_required",
            "rule_passed": True,
            "severity": "INFO",
            "details": "Every future journal row must require manual review.",
        },
        {
            "rule_name": "execution_disabled",
            "rule_passed": True,
            "severity": "INFO",
            "details": "Execution remains disabled.",
        },
        {
            "rule_name": "live_alerts_disabled",
            "rule_passed": True,
            "severity": "INFO",
            "details": "Live alerts remain disabled.",
        },
        {
            "rule_name": "paper_trading_disabled",
            "rule_passed": True,
            "severity": "INFO",
            "details": "Paper trading remains disabled.",
        },
        {
            "rule_name": "real_capital_disabled",
            "rule_passed": True,
            "severity": "INFO",
            "details": "Real capital remains disabled.",
        },
    ]

    return pd.DataFrame(rules)


def validate_template_row(template_row_df: pd.DataFrame) -> pd.DataFrame:
    checks: list[dict[str, Any]] = []

    if template_row_df.empty:
        checks.append(
            {
                "template_check": "template_row_exists",
                "passed": False,
                "severity": "ERROR",
                "details": "Controlled template row is missing.",
                "blocker": True,
            }
        )
        return pd.DataFrame(checks)

    row = template_row_df.iloc[0]

    expected_false_columns = [
        "execution_allowed",
        "live_alert_sent",
        "paper_trade_submitted",
        "real_capital_used",
    ]

    checks.append(
        {
            "template_check": "template_row_exists",
            "passed": len(template_row_df) == 1,
            "severity": "INFO" if len(template_row_df) == 1 else "ERROR",
            "details": f"template_rows={len(template_row_df)}",
            "blocker": len(template_row_df) != 1,
        }
    )

    checks.append(
        {
            "template_check": "template_only_signal_state",
            "passed": str(row.get("signal_state", "")) in ALLOWED_PHASE_9_2_SIGNAL_STATES,
            "severity": (
                "INFO"
                if str(row.get("signal_state", "")) in ALLOWED_PHASE_9_2_SIGNAL_STATES
                else "ERROR"
            ),
            "details": str(row.get("signal_state", "")),
            "blocker": str(row.get("signal_state", "")) not in ALLOWED_PHASE_9_2_SIGNAL_STATES,
        }
    )

    checks.append(
        {
            "template_check": "manual_review_required_true",
            "passed": safe_bool(row.get("manual_review_required", False)),
            "severity": (
                "INFO"
                if safe_bool(row.get("manual_review_required", False))
                else "ERROR"
            ),
            "details": f"manual_review_required={row.get('manual_review_required', '')}",
            "blocker": not safe_bool(row.get("manual_review_required", False)),
        }
    )

    for column in expected_false_columns:
        value_is_false = not safe_bool(row.get(column, True), default=True)
        checks.append(
            {
                "template_check": f"{column}_false",
                "passed": value_is_false,
                "severity": "INFO" if value_is_false else "ERROR",
                "details": f"{column}={row.get(column, '')}",
                "blocker": not value_is_false,
            }
        )

    checks.append(
        {
            "template_check": "direction_long",
            "passed": str(row.get("direction", "")).upper() == "LONG",
            "severity": (
                "INFO"
                if str(row.get("direction", "")).upper() == "LONG"
                else "ERROR"
            ),
            "details": str(row.get("direction", "")),
            "blocker": str(row.get("direction", "")).upper() != "LONG",
        }
    )

    return pd.DataFrame(checks)


def no_approvals_enabled(candidate_registry_df: pd.DataFrame) -> bool:
    approval_columns = [
        "candidate_approved",
        "long_strategy_approved",
        "long_entries_approved",
        "paper_trade_execution_allowed",
        "real_capital_allowed",
        "live_alerts_allowed",
        "exchange_execution_allowed",
        "automation_allowed",
        "execution_allowed",
    ]

    if candidate_registry_df.empty:
        return False

    for column in approval_columns:
        if column not in candidate_registry_df.columns:
            return False

        if candidate_registry_df[column].astype(bool).any():
            return False

    return True


def validate_long_forward_signal_journal() -> dict[str, pd.DataFrame]:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    checks: list[dict[str, Any]] = []

    phase_anchors = {
        "phase_9_1_framework_doc_exists": PHASE_9_1_FRAMEWORK_DOC_PATH,
        "phase_9_2_journal_doc_exists": PHASE_9_2_JOURNAL_DOC_PATH,
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

    phase_9_1_result = validate_long_forward_observation_framework()

    phase_9_1_summary_df = phase_9_1_result["summary"]
    source_candidate_registry_df = phase_9_1_result["candidate_registry"]
    source_observation_schema_df = phase_9_1_result["observation_schema"]

    phase_9_1_validation_passed = (
        not phase_9_1_summary_df.empty
        and bool(phase_9_1_summary_df.iloc[0].get("validation_passed", False))
    )

    journal_schema_df = build_journal_schema()
    empty_journal_template_df = build_empty_journal_template()
    controlled_template_row_df = build_controlled_template_row()
    journal_rules_df = build_journal_rules(source_candidate_registry_df)
    template_row_checks_df = validate_template_row(controlled_template_row_df)

    checks.append(
        build_check(
            check_group="phase_dependency",
            check_name="phase_9_1_validation_passed",
            passed=phase_9_1_validation_passed,
            severity="INFO" if phase_9_1_validation_passed else "ERROR",
            details=(
                str(phase_9_1_summary_df.iloc[0].get("validation_decision", ""))
                if not phase_9_1_summary_df.empty
                else "Missing Phase 9.1 summary."
            ),
        )
    )

    framework_defined = (
        not phase_9_1_summary_df.empty
        and bool(
            phase_9_1_summary_df.iloc[0].get(
                "long_forward_observation_framework_defined",
                False,
            )
        )
    )

    checks.append(
        build_check(
            check_group="phase_dependency",
            check_name="long_forward_observation_framework_defined",
            passed=framework_defined,
            severity="INFO" if framework_defined else "ERROR",
            details=f"framework_defined={framework_defined}",
        )
    )

    framework_columns = set(source_observation_schema_df["column_name"].astype(str).tolist())
    missing_framework_columns = sorted(set(OBSERVATION_SCHEMA_COLUMNS) - framework_columns)

    checks.append(
        build_check(
            check_group="schema_compatibility",
            check_name="phase_9_1_schema_available",
            passed=len(missing_framework_columns) == 0,
            severity="INFO" if len(missing_framework_columns) == 0 else "ERROR",
            details="missing_framework_columns=" + ",".join(missing_framework_columns),
        )
    )

    journal_columns = set(journal_schema_df["column_name"].astype(str).tolist())
    missing_journal_columns = sorted(REQUIRED_JOURNAL_COLUMNS - journal_columns)

    checks.append(
        build_check(
            check_group="journal_schema",
            check_name="journal_schema_columns_complete",
            passed=len(missing_journal_columns) == 0,
            severity="INFO" if len(missing_journal_columns) == 0 else "ERROR",
            details=f"journal_schema_columns={len(journal_columns)}",
        )
    )

    checks.append(
        build_check(
            check_group="journal_schema",
            check_name="journal_template_created_empty",
            passed=(
                list(empty_journal_template_df.columns) == JOURNAL_COLUMNS
                and len(empty_journal_template_df) == 0
            ),
            severity=(
                "INFO"
                if (
                    list(empty_journal_template_df.columns) == JOURNAL_COLUMNS
                    and len(empty_journal_template_df) == 0
                )
                else "ERROR"
            ),
            details=f"journal_template_rows={len(empty_journal_template_df)}",
        )
    )

    checks.append(
        build_check(
            check_group="journal_schema",
            check_name="controlled_template_row_created",
            passed=(
                len(controlled_template_row_df) == 1
                and list(controlled_template_row_df.columns) == JOURNAL_COLUMNS
            ),
            severity=(
                "INFO"
                if (
                    len(controlled_template_row_df) == 1
                    and list(controlled_template_row_df.columns) == JOURNAL_COLUMNS
                )
                else "ERROR"
            ),
            details=f"controlled_template_rows={len(controlled_template_row_df)}",
        )
    )

    journal_rule_errors = int(journal_rules_df["severity"].astype(str).eq("ERROR").sum())

    checks.append(
        build_check(
            check_group="journal_rules",
            check_name="journal_rules_pass",
            passed=journal_rule_errors == 0,
            severity="INFO" if journal_rule_errors == 0 else "ERROR",
            details=f"journal_rule_errors={journal_rule_errors}",
        )
    )

    template_check_blockers = int(template_row_checks_df["blocker"].astype(bool).sum())

    checks.append(
        build_check(
            check_group="journal_template",
            check_name="controlled_template_row_validated",
            passed=template_check_blockers == 0,
            severity="INFO" if template_check_blockers == 0 else "ERROR",
            details=f"template_check_blockers={template_check_blockers}",
        )
    )

    allowed_signal_state_check = (
        set(controlled_template_row_df["signal_state"].astype(str).tolist())
        .issubset(ALLOWED_PHASE_9_2_SIGNAL_STATES)
        if not controlled_template_row_df.empty
        else False
    )

    checks.append(
        build_check(
            check_group="journal_template",
            check_name="phase_9_2_only_template_state",
            passed=allowed_signal_state_check,
            severity="INFO" if allowed_signal_state_check else "ERROR",
            details="allowed_phase_9_2_signal_states="
            + ",".join(sorted(ALLOWED_PHASE_9_2_SIGNAL_STATES)),
        )
    )

    checks.append(
        build_check(
            check_group="approval_control",
            check_name="no_candidate_or_framework_approved",
            passed=no_approvals_enabled(source_candidate_registry_df),
            severity=(
                "INFO"
                if no_approvals_enabled(source_candidate_registry_df)
                else "ERROR"
            ),
            details="All candidate registry approval flags remain False.",
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
            details="Phase 9.2 creates journal structure only; no real signals are recorded.",
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
            check_name="phase_9_3_recommended_next",
            passed=True,
            severity="INFO",
            details="Recommended next step: Phase 9.3 LONG Forward Journal Input Validator V1.",
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
                "phase": "9.2",
                "long_forward_signal_journal_defined": True,
                "phase_9_1_validation_passed": phase_9_1_validation_passed,
                "long_forward_observation_framework_defined": framework_defined,
                "journal_schema_columns": int(len(journal_schema_df)),
                "empty_journal_template_rows": int(len(empty_journal_template_df)),
                "controlled_template_rows": int(len(controlled_template_row_df)),
                "journal_rules_rows": int(len(journal_rules_df)),
                "template_row_checks": int(len(template_row_checks_df)),
                "primary_research_candidate_id": PRIMARY_RESEARCH_CANDIDATE,
                "secondary_reference_candidate_id": SECONDARY_REFERENCE_CANDIDATE,
                "allowed_signal_states_count": int(len(ALLOWED_SIGNAL_STATES)),
                "phase_9_2_allowed_signal_states": ",".join(
                    sorted(ALLOWED_PHASE_9_2_SIGNAL_STATES)
                ),
                "forward_observation_started": False,
                "signal_generation_enabled": False,
                "real_forward_signals_recorded": False,
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
                "recommended_next_phase": "PHASE_9_3_LONG_FORWARD_JOURNAL_INPUT_VALIDATOR_V1",
                "estimated_phase_9_progress_percent": 20,
                "total_checks": int(len(checks_df)),
                "warning_count": warning_count,
                "error_count": error_count,
                "blocker_count": blocker_count,
                "validation_passed": validation_passed,
                "validation_decision": (
                    "PHASE_9_2_LONG_FORWARD_SIGNAL_JOURNAL_VALIDATED"
                    if validation_passed
                    else "PHASE_9_2_LONG_FORWARD_SIGNAL_JOURNAL_FAILED"
                ),
            }
        ]
    )

    phase_9_1_summary_df.to_csv(
        REPORTS_DIR / "phase_9_1_source_summary_v1.csv",
        index=False,
    )
    source_candidate_registry_df.to_csv(
        REPORTS_DIR / "phase_9_1_source_candidate_registry_v1.csv",
        index=False,
    )
    source_observation_schema_df.to_csv(
        REPORTS_DIR / "phase_9_1_source_observation_schema_v1.csv",
        index=False,
    )
    journal_schema_df.to_csv(
        REPORTS_DIR / "long_forward_signal_journal_schema_v1.csv",
        index=False,
    )
    empty_journal_template_df.to_csv(
        REPORTS_DIR / "long_forward_signal_journal_template_v1.csv",
        index=False,
    )
    controlled_template_row_df.to_csv(
        REPORTS_DIR / "long_forward_signal_journal_controlled_template_row_v1.csv",
        index=False,
    )
    journal_rules_df.to_csv(
        REPORTS_DIR / "long_forward_signal_journal_rules_v1.csv",
        index=False,
    )
    template_row_checks_df.to_csv(
        REPORTS_DIR / "long_forward_signal_journal_template_row_checks_v1.csv",
        index=False,
    )
    checks_df.to_csv(
        REPORTS_DIR / "long_forward_signal_journal_checks_v1.csv",
        index=False,
    )
    summary_df.to_csv(
        REPORTS_DIR / "long_forward_signal_journal_summary_v1.csv",
        index=False,
    )

    return {
        "summary": summary_df,
        "source_phase_9_1_summary": phase_9_1_summary_df,
        "source_candidate_registry": source_candidate_registry_df,
        "source_observation_schema": source_observation_schema_df,
        "journal_schema": journal_schema_df,
        "empty_journal_template": empty_journal_template_df,
        "controlled_template_row": controlled_template_row_df,
        "journal_rules": journal_rules_df,
        "template_row_checks": template_row_checks_df,
        "checks": checks_df,
    }