from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from src.long_side.long_baseline_readiness_gate_v1 import (
    validate_long_baseline_readiness_gate,
)


REPORTS_DIR = Path("reports/phase_9_1_long_forward_observation_framework_v1")

PHASE_8_11_READINESS_DOC_PATH = Path("docs/PHASE_8_LONG_BASELINE_READINESS_GATE.md")
PHASE_9_1_FRAMEWORK_DOC_PATH = Path("docs/PHASE_9_LONG_FORWARD_OBSERVATION_FRAMEWORK.md")

PRIMARY_RESEARCH_CANDIDATE = "LONG_BASE_FAILED_BREAKDOWN_V1"
SECONDARY_REFERENCE_CANDIDATE = "LONG_BASE_LIQUIDITY_SWEEP_V1"

BLOCKED_CANDIDATES = [
    "LONG_BASE_FIB_PULLBACK_V1",
    "LONG_BASE_MTF_BULLISH_CONTINUATION_V1",
]

FRAMEWORK_STATUS = "LONG_FORWARD_OBSERVATION_FRAMEWORK_ONLY"

OBSERVATION_SCHEMA_COLUMNS = [
    "observation_id",
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
]

REQUIRED_OBSERVATION_COLUMNS = set(OBSERVATION_SCHEMA_COLUMNS)

SAFETY_FLAGS = {
    "forward_observation_started": False,
    "signal_generation_enabled": False,
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


def build_readiness_lookup(readiness_df: pd.DataFrame) -> dict[str, dict[str, Any]]:
    lookup: dict[str, dict[str, Any]] = {}

    if readiness_df.empty:
        return lookup

    for _, row in readiness_df.iterrows():
        candidate_id = str(row.get("candidate_id", ""))

        if candidate_id:
            lookup[candidate_id] = row.to_dict()

    return lookup


def build_candidate_registry(readiness_df: pd.DataFrame) -> pd.DataFrame:
    readiness_lookup = build_readiness_lookup(readiness_df)

    candidate_ids = [
        PRIMARY_RESEARCH_CANDIDATE,
        SECONDARY_REFERENCE_CANDIDATE,
        *BLOCKED_CANDIDATES,
    ]

    rows: list[dict[str, Any]] = []

    for candidate_id in candidate_ids:
        readiness_row = readiness_lookup.get(candidate_id, {})
        readiness_decision = str(readiness_row.get("readiness_decision", ""))
        readiness_role = str(readiness_row.get("readiness_role", ""))

        active_forward_observation_candidate = (
            candidate_id == PRIMARY_RESEARCH_CANDIDATE
            and readiness_decision == "LONG_FORWARD_OBSERVATION_CANDIDATE"
        )

        secondary_reference_watchlist = (
            candidate_id == SECONDARY_REFERENCE_CANDIDATE
            and readiness_decision == "LONG_SECONDARY_WATCHLIST"
        )

        blocked_candidate = candidate_id in BLOCKED_CANDIDATES

        if active_forward_observation_candidate:
            observation_framework_decision = "FORWARD_OBSERVATION_ELIGIBLE"
            observation_role = "PRIMARY_FORWARD_OBSERVATION"
            included_in_future_observation = True
        elif secondary_reference_watchlist:
            observation_framework_decision = "REFERENCE_WATCHLIST_ONLY"
            observation_role = "SECONDARY_REFERENCE_WATCHLIST"
            included_in_future_observation = False
        elif blocked_candidate:
            observation_framework_decision = "EXCLUDED_BLOCKED"
            observation_role = "BLOCKED_NOT_OBSERVED"
            included_in_future_observation = False
        else:
            observation_framework_decision = "NOT_READY"
            observation_role = "NOT_READY"
            included_in_future_observation = False

        rows.append(
            {
                "candidate_id": candidate_id,
                "readiness_decision": readiness_decision,
                "readiness_role": readiness_role,
                "observation_framework_decision": observation_framework_decision,
                "observation_role": observation_role,
                "active_forward_observation_candidate": active_forward_observation_candidate,
                "secondary_reference_watchlist": secondary_reference_watchlist,
                "blocked_candidate": blocked_candidate,
                "included_in_future_observation": included_in_future_observation,
                "direction": "LONG",
                "manual_review_required": True,
                "forward_observation_started": False,
                "signal_generation_enabled": False,
                "candidate_approved": False,
                "long_strategy_approved": False,
                "long_entries_approved": False,
                "paper_trade_execution_allowed": False,
                "real_capital_allowed": False,
                "live_alerts_allowed": False,
                "exchange_execution_allowed": False,
                "automation_allowed": False,
                "execution_allowed": False,
                "framework_status": FRAMEWORK_STATUS,
            }
        )

    decision_rank = {
        "FORWARD_OBSERVATION_ELIGIBLE": 1,
        "REFERENCE_WATCHLIST_ONLY": 2,
        "NOT_READY": 3,
        "EXCLUDED_BLOCKED": 4,
    }

    registry_df = pd.DataFrame(rows)
    registry_df["observation_framework_rank"] = registry_df[
        "observation_framework_decision"
    ].map(decision_rank)

    registry_df = registry_df.sort_values(
        by=[
            "observation_framework_rank",
            "candidate_id",
        ],
        ascending=[True, True],
    ).reset_index(drop=True)

    return registry_df


def build_observation_schema() -> pd.DataFrame:
    descriptions = {
        "observation_id": "Unique observation identifier.",
        "observed_at": "Timestamp when the potential LONG signal was observed.",
        "symbol": "Market symbol.",
        "timeframe": "Observed timeframe.",
        "candidate_id": "LONG candidate associated with the observation.",
        "observation_role": "Primary or secondary observation role.",
        "direction": "Must remain LONG.",
        "signal_state": "Signal state such as CANDIDATE, WATCH_ONLY, INVALIDATED, or CLOSED.",
        "market_context": "Manual or model-assisted market context summary.",
        "entry_price": "Candidate entry price.",
        "stop_price": "Candidate stop price.",
        "target_price": "Candidate target price.",
        "risk_reward": "Expected risk-reward ratio.",
        "invalidation_level": "Price or condition invalidating the observation.",
        "cost_profile": "Cost profile assumption.",
        "readiness_source": "Source phase or gate that authorized observation eligibility.",
        "manual_review_required": "Must remain True.",
        "execution_allowed": "Must remain False.",
        "live_alert_sent": "Must remain False in this phase.",
        "paper_trade_submitted": "Must remain False in this phase.",
        "real_capital_used": "Must remain False.",
        "resolution_status": "Future outcome status.",
        "result_r": "Future result measured in R.",
        "mfe_r": "Future maximum favorable excursion in R.",
        "mae_r": "Future maximum adverse excursion in R.",
        "bars_to_resolution": "Bars needed to resolve the observation.",
        "notes": "Manual notes.",
        "created_at_utc": "UTC creation timestamp.",
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

    for column in OBSERVATION_SCHEMA_COLUMNS:
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
                "framework_status": FRAMEWORK_STATUS,
            }
        )

    return pd.DataFrame(rows)


def build_empty_observation_template() -> pd.DataFrame:
    return pd.DataFrame(columns=OBSERVATION_SCHEMA_COLUMNS)


def build_framework_controls() -> pd.DataFrame:
    controls = [
        {
            "control_name": "manual_review_required",
            "control_value": True,
            "required_value": True,
            "passed": True,
            "details": "All future LONG observations require manual review.",
        },
        {
            "control_name": "forward_observation_started",
            "control_value": False,
            "required_value": False,
            "passed": True,
            "details": "Phase 9.1 defines the framework only.",
        },
        {
            "control_name": "signal_generation_enabled",
            "control_value": False,
            "required_value": False,
            "passed": True,
            "details": "Signal generation is not enabled in Phase 9.1.",
        },
        {
            "control_name": "paper_trade_execution_allowed",
            "control_value": False,
            "required_value": False,
            "passed": True,
            "details": "Paper trading remains disabled.",
        },
        {
            "control_name": "real_capital_allowed",
            "control_value": False,
            "required_value": False,
            "passed": True,
            "details": "Real capital remains disabled.",
        },
        {
            "control_name": "live_alerts_allowed",
            "control_value": False,
            "required_value": False,
            "passed": True,
            "details": "Live alerts remain disabled.",
        },
        {
            "control_name": "exchange_execution_allowed",
            "control_value": False,
            "required_value": False,
            "passed": True,
            "details": "Exchange execution remains disabled.",
        },
        {
            "control_name": "automation_allowed",
            "control_value": False,
            "required_value": False,
            "passed": True,
            "details": "Automation remains disabled.",
        },
        {
            "control_name": "execution_allowed",
            "control_value": False,
            "required_value": False,
            "passed": True,
            "details": "Execution remains disabled.",
        },
    ]

    rows: list[dict[str, Any]] = []

    for control in controls:
        row = dict(control)
        row["candidate_approved"] = False
        row["long_strategy_approved"] = False
        row["long_entries_approved"] = False
        row["paper_trade_execution_allowed"] = False
        row["real_capital_allowed"] = False
        row["live_alerts_allowed"] = False
        row["exchange_execution_allowed"] = False
        row["automation_allowed"] = False
        row["execution_allowed"] = False
        row["framework_status"] = FRAMEWORK_STATUS
        rows.append(row)

    return pd.DataFrame(rows)


def no_approvals_enabled(*frames: pd.DataFrame) -> bool:
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

    for df in frames:
        if df.empty:
            return False

        for column in approval_columns:
            if column not in df.columns:
                return False

            if df[column].astype(bool).any():
                return False

    return True


def validate_long_forward_observation_framework() -> dict[str, pd.DataFrame]:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    checks: list[dict[str, Any]] = []

    phase_anchors = {
        "phase_8_11_readiness_doc_exists": PHASE_8_11_READINESS_DOC_PATH,
        "phase_9_1_framework_doc_exists": PHASE_9_1_FRAMEWORK_DOC_PATH,
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

    phase_8_11_result = validate_long_baseline_readiness_gate()

    phase_8_11_summary_df = phase_8_11_result["summary"]
    source_readiness_gate_df = phase_8_11_result["readiness_gate"]
    source_evidence_ledger_df = phase_8_11_result["evidence_ledger"]

    phase_8_11_validation_passed = (
        not phase_8_11_summary_df.empty
        and bool(phase_8_11_summary_df.iloc[0].get("validation_passed", False))
    )

    phase_8_baseline_framework_closed = (
        not phase_8_11_summary_df.empty
        and bool(
            phase_8_11_summary_df.iloc[0].get(
                "phase_8_baseline_framework_closed",
                False,
            )
        )
    )

    long_forward_observation_candidate_exists = (
        not phase_8_11_summary_df.empty
        and bool(
            phase_8_11_summary_df.iloc[0].get(
                "long_forward_observation_candidate_exists",
                False,
            )
        )
    )

    candidate_registry_df = build_candidate_registry(source_readiness_gate_df)
    observation_schema_df = build_observation_schema()
    observation_template_df = build_empty_observation_template()
    framework_controls_df = build_framework_controls()

    checks.append(
        build_check(
            check_group="phase_dependency",
            check_name="phase_8_11_validation_passed",
            passed=phase_8_11_validation_passed,
            severity="INFO" if phase_8_11_validation_passed else "ERROR",
            details=(
                str(phase_8_11_summary_df.iloc[0].get("validation_decision", ""))
                if not phase_8_11_summary_df.empty
                else "Missing Phase 8.11 summary."
            ),
        )
    )

    checks.append(
        build_check(
            check_group="phase_dependency",
            check_name="phase_8_baseline_framework_closed",
            passed=phase_8_baseline_framework_closed,
            severity="INFO" if phase_8_baseline_framework_closed else "ERROR",
            details=f"phase_8_baseline_framework_closed={phase_8_baseline_framework_closed}",
        )
    )

    checks.append(
        build_check(
            check_group="phase_dependency",
            check_name="long_forward_observation_candidate_exists",
            passed=long_forward_observation_candidate_exists,
            severity="INFO" if long_forward_observation_candidate_exists else "ERROR",
            details=(
                f"long_forward_observation_candidate_exists="
                f"{long_forward_observation_candidate_exists}"
            ),
        )
    )

    primary_registry = candidate_registry_df[
        candidate_registry_df["candidate_id"].astype(str).eq(
            PRIMARY_RESEARCH_CANDIDATE
        )
    ].copy()

    secondary_registry = candidate_registry_df[
        candidate_registry_df["candidate_id"].astype(str).eq(
            SECONDARY_REFERENCE_CANDIDATE
        )
    ].copy()

    blocked_registry = candidate_registry_df[
        candidate_registry_df["candidate_id"].astype(str).isin(BLOCKED_CANDIDATES)
    ].copy()

    checks.append(
        build_check(
            check_group="candidate_registry",
            check_name="primary_candidate_observation_eligible",
            passed=(
                len(primary_registry) == 1
                and str(primary_registry.iloc[0]["observation_framework_decision"])
                == "FORWARD_OBSERVATION_ELIGIBLE"
                and safe_bool(
                    primary_registry.iloc[0]["active_forward_observation_candidate"]
                )
            ),
            severity=(
                "INFO"
                if (
                    len(primary_registry) == 1
                    and str(primary_registry.iloc[0]["observation_framework_decision"])
                    == "FORWARD_OBSERVATION_ELIGIBLE"
                    and safe_bool(
                        primary_registry.iloc[0]["active_forward_observation_candidate"]
                    )
                )
                else "ERROR"
            ),
            details=(
                str(primary_registry.iloc[0]["observation_framework_decision"])
                if not primary_registry.empty
                else "missing"
            ),
        )
    )

    checks.append(
        build_check(
            check_group="candidate_registry",
            check_name="secondary_candidate_reference_only",
            passed=(
                len(secondary_registry) == 1
                and str(secondary_registry.iloc[0]["observation_framework_decision"])
                == "REFERENCE_WATCHLIST_ONLY"
                and safe_bool(
                    secondary_registry.iloc[0]["secondary_reference_watchlist"]
                )
            ),
            severity=(
                "INFO"
                if (
                    len(secondary_registry) == 1
                    and str(secondary_registry.iloc[0]["observation_framework_decision"])
                    == "REFERENCE_WATCHLIST_ONLY"
                    and safe_bool(
                        secondary_registry.iloc[0]["secondary_reference_watchlist"]
                    )
                )
                else "ERROR"
            ),
            details=(
                str(secondary_registry.iloc[0]["observation_framework_decision"])
                if not secondary_registry.empty
                else "missing"
            ),
        )
    )

    checks.append(
        build_check(
            check_group="candidate_registry",
            check_name="blocked_candidates_excluded_from_active_observation",
            passed=(
                len(blocked_registry) == len(BLOCKED_CANDIDATES)
                and blocked_registry["observation_framework_decision"]
                .astype(str)
                .eq("EXCLUDED_BLOCKED")
                .all()
                and not blocked_registry["included_in_future_observation"]
                .astype(bool)
                .any()
            ),
            severity=(
                "INFO"
                if (
                    len(blocked_registry) == len(BLOCKED_CANDIDATES)
                    and blocked_registry["observation_framework_decision"]
                    .astype(str)
                    .eq("EXCLUDED_BLOCKED")
                    .all()
                    and not blocked_registry["included_in_future_observation"]
                    .astype(bool)
                    .any()
                )
                else "ERROR"
            ),
            details="blocked=" + ",".join(blocked_registry["candidate_id"].astype(str)),
        )
    )

    schema_columns = set(observation_schema_df["column_name"].astype(str).tolist())

    checks.append(
        build_check(
            check_group="observation_schema",
            check_name="observation_schema_columns_complete",
            passed=REQUIRED_OBSERVATION_COLUMNS.issubset(schema_columns),
            severity=(
                "INFO"
                if REQUIRED_OBSERVATION_COLUMNS.issubset(schema_columns)
                else "ERROR"
            ),
            details=f"schema_columns={len(schema_columns)}",
        )
    )

    checks.append(
        build_check(
            check_group="observation_schema",
            check_name="observation_template_created_empty",
            passed=(
                list(observation_template_df.columns) == OBSERVATION_SCHEMA_COLUMNS
                and len(observation_template_df) == 0
            ),
            severity=(
                "INFO"
                if (
                    list(observation_template_df.columns) == OBSERVATION_SCHEMA_COLUMNS
                    and len(observation_template_df) == 0
                )
                else "ERROR"
            ),
            details=f"template_rows={len(observation_template_df)}",
        )
    )

    checks.append(
        build_check(
            check_group="framework_controls",
            check_name="framework_controls_pass",
            passed=framework_controls_df["passed"].astype(bool).all(),
            severity=(
                "INFO"
                if framework_controls_df["passed"].astype(bool).all()
                else "ERROR"
            ),
            details=f"framework_controls={len(framework_controls_df)}",
        )
    )

    checks.append(
        build_check(
            check_group="approval_control",
            check_name="no_candidate_or_framework_approved",
            passed=no_approvals_enabled(candidate_registry_df, framework_controls_df),
            severity=(
                "INFO"
                if no_approvals_enabled(candidate_registry_df, framework_controls_df)
                else "ERROR"
            ),
            details="All framework approval flags remain False.",
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
            check_name="forward_observation_not_started",
            passed=True,
            severity="WARNING",
            details="Phase 9.1 defines the framework only; observation starts later.",
        )
    )

    checks.append(
        build_check(
            check_group="scope_control",
            check_name="paper_trading_not_enabled",
            passed=True,
            severity="WARNING",
            details="Paper trading remains disabled after Phase 9.1.",
        )
    )

    checks.append(
        build_check(
            check_group="phase_transition",
            check_name="phase_9_2_recommended_next",
            passed=True,
            severity="INFO",
            details="Recommended next step: Phase 9.2 LONG Forward Signal Journal V1.",
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
                "phase": "9.1",
                "long_forward_observation_framework_defined": True,
                "phase_8_11_validation_passed": phase_8_11_validation_passed,
                "phase_8_baseline_framework_closed": phase_8_baseline_framework_closed,
                "long_forward_observation_candidate_exists": long_forward_observation_candidate_exists,
                "primary_research_candidate_id": PRIMARY_RESEARCH_CANDIDATE,
                "secondary_reference_candidate_id": SECONDARY_REFERENCE_CANDIDATE,
                "candidate_registry_rows": int(len(candidate_registry_df)),
                "observation_schema_columns": int(len(observation_schema_df)),
                "observation_template_rows": int(len(observation_template_df)),
                "framework_controls_rows": int(len(framework_controls_df)),
                "primary_observation_framework_decision": (
                    str(primary_registry.iloc[0]["observation_framework_decision"])
                    if not primary_registry.empty
                    else ""
                ),
                "secondary_observation_framework_decision": (
                    str(secondary_registry.iloc[0]["observation_framework_decision"])
                    if not secondary_registry.empty
                    else ""
                ),
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
                "recommended_next_phase": "PHASE_9_2_LONG_FORWARD_SIGNAL_JOURNAL_V1",
                "estimated_phase_9_progress_percent": 10,
                "total_checks": int(len(checks_df)),
                "warning_count": warning_count,
                "error_count": error_count,
                "blocker_count": blocker_count,
                "validation_passed": validation_passed,
                "validation_decision": (
                    "PHASE_9_1_LONG_FORWARD_OBSERVATION_FRAMEWORK_VALIDATED"
                    if validation_passed
                    else "PHASE_9_1_LONG_FORWARD_OBSERVATION_FRAMEWORK_FAILED"
                ),
            }
        ]
    )

    phase_8_11_summary_df.to_csv(
        REPORTS_DIR / "phase_8_11_source_summary_v1.csv",
        index=False,
    )
    source_readiness_gate_df.to_csv(
        REPORTS_DIR / "phase_8_11_source_readiness_gate_v1.csv",
        index=False,
    )
    source_evidence_ledger_df.to_csv(
        REPORTS_DIR / "phase_8_11_source_evidence_ledger_v1.csv",
        index=False,
    )
    candidate_registry_df.to_csv(
        REPORTS_DIR / "long_forward_observation_candidate_registry_v1.csv",
        index=False,
    )
    observation_schema_df.to_csv(
        REPORTS_DIR / "long_forward_observation_schema_v1.csv",
        index=False,
    )
    observation_template_df.to_csv(
        REPORTS_DIR / "long_forward_observation_template_v1.csv",
        index=False,
    )
    framework_controls_df.to_csv(
        REPORTS_DIR / "long_forward_observation_framework_controls_v1.csv",
        index=False,
    )
    checks_df.to_csv(
        REPORTS_DIR / "long_forward_observation_framework_checks_v1.csv",
        index=False,
    )
    summary_df.to_csv(
        REPORTS_DIR / "long_forward_observation_framework_summary_v1.csv",
        index=False,
    )

    return {
        "summary": summary_df,
        "source_phase_8_11_summary": phase_8_11_summary_df,
        "source_readiness_gate": source_readiness_gate_df,
        "source_evidence_ledger": source_evidence_ledger_df,
        "candidate_registry": candidate_registry_df,
        "observation_schema": observation_schema_df,
        "observation_template": observation_template_df,
        "framework_controls": framework_controls_df,
        "checks": checks_df,
    }