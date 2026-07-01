from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from src.long_side.long_candidate_discovery_baseline_v1 import EXPECTED_CANDIDATES
from src.long_side.long_oos_baseline_validation_v1 import (
    validate_long_oos_baseline_validation,
)


REPORTS_DIR = Path("reports/phase_8_7_long_oos_decision_gate_v1")

PHASE_8_1_CONTRACT_DOC_PATH = Path("docs/PHASE_8_LONG_SIDE_VALIDATION_CONTRACT.md")
PHASE_8_2_DISCOVERY_DOC_PATH = Path("docs/PHASE_8_LONG_CANDIDATE_DISCOVERY_BASELINE.md")
PHASE_8_3_HARNESS_DOC_PATH = Path("docs/PHASE_8_LONG_BASELINE_STRUCTURAL_BACKTEST_HARNESS.md")
PHASE_8_4_HISTORICAL_DOC_PATH = Path("docs/PHASE_8_LONG_HISTORICAL_BASELINE_BACKTEST.md")
PHASE_8_5_COMPARISON_DOC_PATH = Path("docs/PHASE_8_LONG_CANDIDATE_HISTORICAL_COMPARISON.md")
PHASE_8_6_OOS_DOC_PATH = Path("docs/PHASE_8_LONG_OOS_BASELINE_VALIDATION.md")
PHASE_8_7_DECISION_DOC_PATH = Path("docs/PHASE_8_LONG_OOS_DECISION_GATE.md")

PRIMARY_RESEARCH_CANDIDATE = "LONG_BASE_FAILED_BREAKDOWN_V1"
SECONDARY_WATCHLIST_CANDIDATE = "LONG_BASE_LIQUIDITY_SWEEP_V1"

EXPECTED_BLOCKED_CANDIDATES = {
    "LONG_BASE_FIB_PULLBACK_V1",
    "LONG_BASE_MTF_BULLISH_CONTINUATION_V1",
}

ALLOWED_GATE_DECISIONS = {
    "ADVANCE_TO_STRICT_VALIDATION",
    "SECONDARY_WATCHLIST_ONLY",
    "HOLD_FOR_REDESIGN",
    "BLOCKED_REJECTED_HISTORICAL",
    "BLOCKED_AFTER_OOS",
    "INSUFFICIENT_OOS_SIGNAL",
}

SAFETY_FLAGS = {
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


def build_oos_lookup(oos_metrics_df: pd.DataFrame) -> dict[str, dict[str, Any]]:
    if oos_metrics_df.empty:
        return {}

    lookup: dict[str, dict[str, Any]] = {}

    for _, row in oos_metrics_df.iterrows():
        candidate_id = str(row.get("candidate_id", ""))
        if not candidate_id:
            continue

        lookup[candidate_id] = row.to_dict()

    return lookup


def build_historical_lookup(source_comparison_df: pd.DataFrame) -> dict[str, dict[str, Any]]:
    if source_comparison_df.empty:
        return {}

    lookup: dict[str, dict[str, Any]] = {}

    for _, row in source_comparison_df.iterrows():
        candidate_id = str(row.get("candidate_id", ""))
        if not candidate_id:
            continue

        lookup[candidate_id] = row.to_dict()

    return lookup


def decide_candidate_gate(
    candidate_id: str,
    historical_row: dict[str, Any] | None,
    oos_row: dict[str, Any] | None,
) -> tuple[str, str, str]:
    historical_classification = (
        str(historical_row.get("historical_classification", ""))
        if historical_row
        else ""
    )
    oos_classification = (
        str(oos_row.get("oos_classification", ""))
        if oos_row
        else ""
    )

    if historical_classification == "REJECT":
        return (
            "BLOCKED_REJECTED_HISTORICAL",
            "Candidate was rejected during historical comparison and remains blocked.",
            "BLOCKED",
        )

    if oos_classification == "OOS_RESEARCH_CONTINUATION":
        return (
            "ADVANCE_TO_STRICT_VALIDATION",
            "Candidate may advance to stricter validation. No execution approval.",
            "PRIMARY_RESEARCH"
            if candidate_id == PRIMARY_RESEARCH_CANDIDATE
            else "RESEARCH_CONTINUATION",
        )

    if oos_classification == "OOS_WATCHLIST":
        return (
            "SECONDARY_WATCHLIST_ONLY",
            "Candidate remains secondary watchlist only. No execution approval.",
            "SECONDARY_WATCHLIST",
        )

    if oos_classification == "OOS_WEAK":
        return (
            "HOLD_FOR_REDESIGN",
            "Candidate produced weak OOS evidence and should not continue as-is.",
            "BLOCKED",
        )

    if oos_classification == "OOS_FAIL":
        return (
            "BLOCKED_AFTER_OOS",
            "Candidate failed OOS baseline and is blocked as-is.",
            "BLOCKED",
        )

    if oos_classification == "OOS_NO_SIGNAL":
        return (
            "INSUFFICIENT_OOS_SIGNAL",
            "Candidate produced no OOS trades and remains inconclusive.",
            "INSUFFICIENT_EVIDENCE",
        )

    return (
        "HOLD_FOR_REDESIGN",
        "Candidate lacks sufficient decision evidence and remains blocked.",
        "BLOCKED",
    )


def build_decision_gate_table(
    source_comparison_df: pd.DataFrame,
    oos_metrics_df: pd.DataFrame,
) -> pd.DataFrame:
    historical_lookup = build_historical_lookup(source_comparison_df)
    oos_lookup = build_oos_lookup(oos_metrics_df)

    rows: list[dict[str, Any]] = []

    for candidate_id in EXPECTED_CANDIDATES:
        historical_row = historical_lookup.get(candidate_id, {})
        oos_row = oos_lookup.get(candidate_id, {})

        gate_decision, gate_recommendation, research_role = decide_candidate_gate(
            candidate_id=candidate_id,
            historical_row=historical_row,
            oos_row=oos_row,
        )

        rows.append(
            {
                "candidate_id": candidate_id,
                "historical_classification": str(
                    historical_row.get("historical_classification", "")
                ),
                "historical_total_result_r": safe_float(
                    historical_row.get("total_result_r", 0.0)
                ),
                "historical_profit_factor": safe_float(
                    historical_row.get("profit_factor", 0.0)
                ),
                "historical_trades": safe_int(historical_row.get("trades", 0)),
                "oos_classification": str(oos_row.get("oos_classification", "")),
                "oos_total_result_r": safe_float(oos_row.get("total_result_r", 0.0)),
                "oos_profit_factor": safe_float(oos_row.get("profit_factor", 0.0)),
                "oos_trades": safe_int(oos_row.get("trades", 0)),
                "gate_decision": gate_decision,
                "research_role": research_role,
                "gate_recommendation": gate_recommendation,
                "candidate_approved": False,
                "long_strategy_approved": False,
                "long_entries_approved": False,
                "paper_trade_execution_allowed": False,
                "real_capital_allowed": False,
                "live_alerts_allowed": False,
                "exchange_execution_allowed": False,
                "automation_allowed": False,
                "execution_allowed": False,
            }
        )

    gate_decision_rank = {
        "ADVANCE_TO_STRICT_VALIDATION": 1,
        "SECONDARY_WATCHLIST_ONLY": 2,
        "INSUFFICIENT_OOS_SIGNAL": 3,
        "HOLD_FOR_REDESIGN": 4,
        "BLOCKED_AFTER_OOS": 5,
        "BLOCKED_REJECTED_HISTORICAL": 6,
    }

    result_df = pd.DataFrame(rows)
    result_df["gate_decision_rank"] = result_df["gate_decision"].map(gate_decision_rank)

    result_df = result_df.sort_values(
        by=[
            "gate_decision_rank",
            "oos_total_result_r",
            "oos_profit_factor",
            "historical_total_result_r",
        ],
        ascending=[True, False, False, False],
    ).reset_index(drop=True)

    return result_df


def no_approvals_enabled(decision_df: pd.DataFrame) -> bool:
    if decision_df.empty:
        return False

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

    for column in approval_columns:
        if column not in decision_df.columns:
            return False

        if decision_df[column].astype(bool).any():
            return False

    return True


def validate_long_oos_decision_gate() -> dict[str, pd.DataFrame]:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    checks: list[dict[str, Any]] = []

    phase_anchors = {
        "phase_8_1_contract_doc_exists": PHASE_8_1_CONTRACT_DOC_PATH,
        "phase_8_2_discovery_doc_exists": PHASE_8_2_DISCOVERY_DOC_PATH,
        "phase_8_3_harness_doc_exists": PHASE_8_3_HARNESS_DOC_PATH,
        "phase_8_4_historical_doc_exists": PHASE_8_4_HISTORICAL_DOC_PATH,
        "phase_8_5_comparison_doc_exists": PHASE_8_5_COMPARISON_DOC_PATH,
        "phase_8_6_oos_doc_exists": PHASE_8_6_OOS_DOC_PATH,
        "phase_8_7_decision_doc_exists": PHASE_8_7_DECISION_DOC_PATH,
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

    phase_8_6_result = validate_long_oos_baseline_validation()

    source_summary_df = phase_8_6_result["summary"]
    source_comparison_df = phase_8_6_result["source_comparison"]
    eligible_df = phase_8_6_result["eligible_candidates"]
    excluded_df = phase_8_6_result["excluded_candidates"]
    oos_metrics_df = phase_8_6_result["oos_metrics"]

    phase_8_6_validation_passed = (
        not source_summary_df.empty
        and bool(source_summary_df.iloc[0].get("validation_passed", False))
    )

    decision_df = build_decision_gate_table(
        source_comparison_df=source_comparison_df,
        oos_metrics_df=oos_metrics_df,
    )

    decisions = set(decision_df["gate_decision"].astype(str).tolist())

    primary_rows = decision_df[
        decision_df["gate_decision"].astype(str).eq("ADVANCE_TO_STRICT_VALIDATION")
    ].copy()

    secondary_rows = decision_df[
        decision_df["gate_decision"].astype(str).eq("SECONDARY_WATCHLIST_ONLY")
    ].copy()

    blocked_rows = decision_df[
        decision_df["gate_decision"].astype(str).isin(
            {
                "BLOCKED_REJECTED_HISTORICAL",
                "BLOCKED_AFTER_OOS",
                "HOLD_FOR_REDESIGN",
                "INSUFFICIENT_OOS_SIGNAL",
            }
        )
    ].copy()

    primary_candidate_id = (
        str(primary_rows.iloc[0]["candidate_id"])
        if not primary_rows.empty
        else ""
    )

    checks.append(
        build_check(
            check_group="phase_dependency",
            check_name="phase_8_6_validation_passed",
            passed=phase_8_6_validation_passed,
            severity="INFO" if phase_8_6_validation_passed else "ERROR",
            details=(
                str(source_summary_df.iloc[0].get("validation_decision", ""))
                if not source_summary_df.empty
                else "Missing Phase 8.6 summary."
            ),
        )
    )

    checks.append(
        build_check(
            check_group="candidate_scope",
            check_name="all_expected_candidates_decided",
            passed=set(decision_df["candidate_id"].tolist()) == set(EXPECTED_CANDIDATES),
            severity=(
                "INFO"
                if set(decision_df["candidate_id"].tolist()) == set(EXPECTED_CANDIDATES)
                else "ERROR"
            ),
            details=",".join(decision_df["candidate_id"].tolist()),
        )
    )

    checks.append(
        build_check(
            check_group="candidate_scope",
            check_name="decision_rows_match_expected_candidates",
            passed=len(decision_df) == len(EXPECTED_CANDIDATES),
            severity="INFO" if len(decision_df) == len(EXPECTED_CANDIDATES) else "ERROR",
            details=f"decision_rows={len(decision_df)}",
        )
    )

    checks.append(
        build_check(
            check_group="decision_gate",
            check_name="gate_decisions_are_allowed",
            passed=decisions.issubset(ALLOWED_GATE_DECISIONS),
            severity="INFO" if decisions.issubset(ALLOWED_GATE_DECISIONS) else "ERROR",
            details="decisions=" + ",".join(sorted(decisions)),
        )
    )

    checks.append(
        build_check(
            check_group="decision_gate",
            check_name="primary_research_candidate_expected",
            passed=primary_candidate_id == PRIMARY_RESEARCH_CANDIDATE,
            severity="INFO" if primary_candidate_id == PRIMARY_RESEARCH_CANDIDATE else "ERROR",
            details=f"primary_candidate_id={primary_candidate_id}",
        )
    )

    checks.append(
        build_check(
            check_group="decision_gate",
            check_name="single_primary_research_candidate",
            passed=len(primary_rows) == 1,
            severity="INFO" if len(primary_rows) == 1 else "ERROR",
            details=f"primary_count={len(primary_rows)}",
        )
    )

    checks.append(
        build_check(
            check_group="decision_gate",
            check_name="secondary_watchlist_candidate_expected",
            passed=(
                len(secondary_rows) == 1
                and str(secondary_rows.iloc[0]["candidate_id"])
                == SECONDARY_WATCHLIST_CANDIDATE
            ),
            severity=(
                "INFO"
                if (
                    len(secondary_rows) == 1
                    and str(secondary_rows.iloc[0]["candidate_id"])
                    == SECONDARY_WATCHLIST_CANDIDATE
                )
                else "ERROR"
            ),
            details=(
                "secondary_candidates="
                + ",".join(secondary_rows["candidate_id"].astype(str).tolist())
            ),
        )
    )

    blocked_candidate_ids = set(blocked_rows["candidate_id"].astype(str).tolist())

    checks.append(
        build_check(
            check_group="decision_gate",
            check_name="historically_rejected_candidates_blocked",
            passed=EXPECTED_BLOCKED_CANDIDATES.issubset(blocked_candidate_ids),
            severity=(
                "INFO"
                if EXPECTED_BLOCKED_CANDIDATES.issubset(blocked_candidate_ids)
                else "ERROR"
            ),
            details="blocked=" + ",".join(sorted(blocked_candidate_ids)),
        )
    )

    checks.append(
        build_check(
            check_group="approval_control",
            check_name="no_candidate_approved",
            passed=no_approvals_enabled(decision_df),
            severity="INFO" if no_approvals_enabled(decision_df) else "ERROR",
            details="All decision gate approval flags remain False.",
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
            check_name="walk_forward_not_executed",
            passed=True,
            severity="INFO",
            details="Walk-forward validation is deferred to Phase 8.8.",
        )
    )

    checks.append(
        build_check(
            check_group="scope_control",
            check_name="monte_carlo_not_executed",
            passed=True,
            severity="INFO",
            details="Monte Carlo validation is deferred.",
        )
    )

    checks.append(
        build_check(
            check_group="scope_control",
            check_name="cost_aware_not_executed",
            passed=True,
            severity="INFO",
            details="Cost-aware validation is deferred.",
        )
    )

    checks.append(
        build_check(
            check_group="phase_transition",
            check_name="phase_8_8_recommended_next",
            passed=True,
            severity="INFO",
            details="Recommended next step: Phase 8.8 LONG Walk-Forward Baseline Validation V1.",
        )
    )

    checks.append(
        build_check(
            check_group="scope_control",
            check_name="long_side_remains_unestablished",
            passed=True,
            severity="WARNING",
            details="Phase 8.7 creates a research decision gate only; LONG side is not established.",
        )
    )

    checks.append(
        build_check(
            check_group="scope_control",
            check_name="real_entries_remain_blocked",
            passed=True,
            severity="WARNING",
            details="Real entries remain blocked after Phase 8.7.",
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
                "phase": "8.7",
                "oos_decision_gate_defined": True,
                "phase_8_6_validation_passed": phase_8_6_validation_passed,
                "source_oos_trade_count": (
                    int(source_summary_df.iloc[0].get("oos_trade_count", 0))
                    if not source_summary_df.empty
                    else 0
                ),
                "source_oos_metrics_rows": int(len(oos_metrics_df)),
                "eligible_candidate_count": int(len(eligible_df)),
                "excluded_candidate_count": int(len(excluded_df)),
                "decision_rows": int(len(decision_df)),
                "advance_to_strict_validation_count": int(len(primary_rows)),
                "secondary_watchlist_count": int(len(secondary_rows)),
                "blocked_count": int(len(blocked_rows)),
                "primary_research_candidate_id": primary_candidate_id,
                "secondary_watchlist_candidate_id": (
                    str(secondary_rows.iloc[0]["candidate_id"])
                    if not secondary_rows.empty
                    else ""
                ),
                "blocked_candidate_ids": ",".join(
                    sorted(blocked_rows["candidate_id"].astype(str).tolist())
                ),
                "decision_gate_executed": True,
                "walk_forward_executed": False,
                "monte_carlo_executed": False,
                "cost_aware_executed": False,
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
                "recommended_next_phase": "PHASE_8_8_LONG_WALK_FORWARD_BASELINE_VALIDATION_V1",
                "estimated_total_project_progress_percent": 96,
                "total_checks": int(len(checks_df)),
                "warning_count": warning_count,
                "error_count": error_count,
                "blocker_count": blocker_count,
                "validation_passed": validation_passed,
                "validation_decision": (
                    "PHASE_8_7_LONG_OOS_DECISION_GATE_VALIDATED"
                    if validation_passed
                    else "PHASE_8_7_LONG_OOS_DECISION_GATE_FAILED"
                ),
            }
        ]
    )

    source_summary_df.to_csv(
        REPORTS_DIR / "phase_8_6_source_summary_v1.csv",
        index=False,
    )
    oos_metrics_df.to_csv(
        REPORTS_DIR / "phase_8_6_source_oos_metrics_v1.csv",
        index=False,
    )
    source_comparison_df.to_csv(
        REPORTS_DIR / "phase_8_5_source_comparison_v1.csv",
        index=False,
    )
    decision_df.to_csv(
        REPORTS_DIR / "long_oos_decision_gate_v1.csv",
        index=False,
    )
    checks_df.to_csv(
        REPORTS_DIR / "long_oos_decision_gate_checks_v1.csv",
        index=False,
    )
    summary_df.to_csv(
        REPORTS_DIR / "long_oos_decision_gate_summary_v1.csv",
        index=False,
    )

    return {
        "summary": summary_df,
        "source_summary": source_summary_df,
        "source_oos_metrics": oos_metrics_df,
        "source_comparison": source_comparison_df,
        "decision_gate": decision_df,
        "checks": checks_df,
    }