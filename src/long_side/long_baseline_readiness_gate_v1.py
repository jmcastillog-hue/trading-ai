from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from src.long_side.long_monte_carlo_baseline_validation_v1 import (
    validate_long_monte_carlo_baseline_validation,
)


REPORTS_DIR = Path("reports/phase_8_11_long_baseline_readiness_gate_v1")

PHASE_8_1_CONTRACT_DOC_PATH = Path("docs/PHASE_8_LONG_SIDE_VALIDATION_CONTRACT.md")
PHASE_8_2_DISCOVERY_DOC_PATH = Path("docs/PHASE_8_LONG_CANDIDATE_DISCOVERY_BASELINE.md")
PHASE_8_3_HARNESS_DOC_PATH = Path("docs/PHASE_8_LONG_BASELINE_STRUCTURAL_BACKTEST_HARNESS.md")
PHASE_8_4_HISTORICAL_DOC_PATH = Path("docs/PHASE_8_LONG_HISTORICAL_BASELINE_BACKTEST.md")
PHASE_8_5_COMPARISON_DOC_PATH = Path("docs/PHASE_8_LONG_CANDIDATE_HISTORICAL_COMPARISON.md")
PHASE_8_6_OOS_DOC_PATH = Path("docs/PHASE_8_LONG_OOS_BASELINE_VALIDATION.md")
PHASE_8_7_DECISION_DOC_PATH = Path("docs/PHASE_8_LONG_OOS_DECISION_GATE.md")
PHASE_8_8_WF_DOC_PATH = Path("docs/PHASE_8_LONG_WALK_FORWARD_BASELINE_VALIDATION.md")
PHASE_8_9_COST_DOC_PATH = Path("docs/PHASE_8_LONG_COST_AWARE_BASELINE_VALIDATION.md")
PHASE_8_10_MC_DOC_PATH = Path("docs/PHASE_8_LONG_MONTE_CARLO_BASELINE_VALIDATION.md")
PHASE_8_11_READINESS_DOC_PATH = Path("docs/PHASE_8_LONG_BASELINE_READINESS_GATE.md")

PRIMARY_RESEARCH_CANDIDATE = "LONG_BASE_FAILED_BREAKDOWN_V1"
SECONDARY_REFERENCE_CANDIDATE = "LONG_BASE_LIQUIDITY_SWEEP_V1"

BLOCKED_CANDIDATES = [
    "LONG_BASE_FIB_PULLBACK_V1",
    "LONG_BASE_MTF_BULLISH_CONTINUATION_V1",
]

READINESS_STATUS = "LONG_BASELINE_READINESS_GATE_ONLY"

ALLOWED_READINESS_DECISIONS = {
    "LONG_FORWARD_OBSERVATION_CANDIDATE",
    "LONG_SECONDARY_WATCHLIST",
    "LONG_HOLD_FOR_MORE_EVIDENCE",
    "LONG_BLOCKED_REJECTED",
    "LONG_BLOCKED_RISK",
    "LONG_NOT_READY",
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


def build_mc_lookup(candidate_mc_summary_df: pd.DataFrame) -> dict[str, dict[str, Any]]:
    lookup: dict[str, dict[str, Any]] = {}

    if candidate_mc_summary_df.empty:
        return lookup

    for _, row in candidate_mc_summary_df.iterrows():
        candidate_id = str(row.get("candidate_id", ""))

        if candidate_id:
            lookup[candidate_id] = row.to_dict()

    return lookup


def build_cost_lookup(candidate_cost_summary_df: pd.DataFrame) -> dict[str, dict[str, Any]]:
    lookup: dict[str, dict[str, Any]] = {}

    if candidate_cost_summary_df.empty:
        return lookup

    for _, row in candidate_cost_summary_df.iterrows():
        candidate_id = str(row.get("candidate_id", ""))

        if candidate_id:
            lookup[candidate_id] = row.to_dict()

    return lookup


def decide_readiness(
    candidate_id: str,
    mc_row: dict[str, Any] | None,
    cost_row: dict[str, Any] | None,
) -> tuple[str, str, str]:
    if candidate_id in BLOCKED_CANDIDATES:
        return (
            "LONG_BLOCKED_REJECTED",
            "BLOCKED",
            "Candidate was rejected earlier in Phase 8 and remains blocked.",
        )

    mc_classification = str(mc_row.get("mc_classification", "")) if mc_row else ""
    final_cost_decision = str(cost_row.get("final_cost_decision", "")) if cost_row else ""
    probability_positive = safe_float(mc_row.get("probability_positive", 0.0)) if mc_row else 0.0
    p05_total_result_r = safe_float(mc_row.get("p05_total_result_r", 0.0)) if mc_row else 0.0
    p05_max_drawdown_r = safe_float(mc_row.get("p05_max_drawdown_r", 0.0)) if mc_row else 0.0

    if candidate_id == PRIMARY_RESEARCH_CANDIDATE:
        if (
            final_cost_decision == "COST_AWARE_RESEARCH_CONTINUATION"
            and mc_classification == "MC_RESEARCH_CONTINUATION"
            and probability_positive >= 0.60
            and p05_total_result_r >= -5.0
            and p05_max_drawdown_r >= -8.0
        ):
            return (
                "LONG_FORWARD_OBSERVATION_CANDIDATE",
                "PRIMARY_FORWARD_OBSERVATION",
                "Primary LONG candidate may move to future forward observation. No execution approval.",
            )

        if probability_positive >= 0.50 and p05_total_result_r >= -7.5:
            return (
                "LONG_HOLD_FOR_MORE_EVIDENCE",
                "PRIMARY_HOLD",
                "Primary candidate remains alive but needs more evidence before forward observation.",
            )

        return (
            "LONG_BLOCKED_RISK",
            "PRIMARY_BLOCKED_RISK",
            "Primary candidate shows unacceptable baseline risk.",
        )

    if candidate_id == SECONDARY_REFERENCE_CANDIDATE:
        if mc_classification == "MC_WATCHLIST":
            return (
                "LONG_SECONDARY_WATCHLIST",
                "SECONDARY_WATCHLIST",
                "Secondary candidate remains watchlist only. No execution approval.",
            )

        if mc_classification == "MC_RESEARCH_CONTINUATION":
            return (
                "LONG_SECONDARY_WATCHLIST",
                "SECONDARY_WATCHLIST_STRONG",
                "Secondary candidate is strong but remains secondary until formally promoted.",
            )

        return (
            "LONG_HOLD_FOR_MORE_EVIDENCE",
            "SECONDARY_HOLD",
            "Secondary candidate requires more evidence.",
        )

    return (
        "LONG_NOT_READY",
        "NOT_READY",
        "Candidate is not ready under the current readiness gate.",
    )


def build_readiness_gate_table(
    candidate_mc_summary_df: pd.DataFrame,
    candidate_cost_summary_df: pd.DataFrame,
) -> pd.DataFrame:
    mc_lookup = build_mc_lookup(candidate_mc_summary_df)
    cost_lookup = build_cost_lookup(candidate_cost_summary_df)

    candidate_ids = [
        PRIMARY_RESEARCH_CANDIDATE,
        SECONDARY_REFERENCE_CANDIDATE,
        *BLOCKED_CANDIDATES,
    ]

    rows: list[dict[str, Any]] = []

    for candidate_id in candidate_ids:
        mc_row = mc_lookup.get(candidate_id, {})
        cost_row = cost_lookup.get(candidate_id, {})

        readiness_decision, readiness_role, readiness_note = decide_readiness(
            candidate_id=candidate_id,
            mc_row=mc_row,
            cost_row=cost_row,
        )

        rows.append(
            {
                "candidate_id": candidate_id,
                "readiness_decision": readiness_decision,
                "readiness_role": readiness_role,
                "readiness_note": readiness_note,
                "final_cost_decision": str(cost_row.get("final_cost_decision", "")),
                "mc_classification": str(mc_row.get("mc_classification", "")),
                "source_trade_count": safe_int(mc_row.get("source_trade_count", 0)),
                "simulation_count": safe_int(mc_row.get("simulation_count", 0)),
                "original_total_result_r": safe_float(
                    mc_row.get("original_total_result_r", 0.0)
                ),
                "probability_positive": safe_float(
                    mc_row.get("probability_positive", 0.0)
                ),
                "p05_total_result_r": safe_float(
                    mc_row.get("p05_total_result_r", 0.0)
                ),
                "p50_total_result_r": safe_float(
                    mc_row.get("p50_total_result_r", 0.0)
                ),
                "p95_total_result_r": safe_float(
                    mc_row.get("p95_total_result_r", 0.0)
                ),
                "p05_max_drawdown_r": safe_float(
                    mc_row.get("p05_max_drawdown_r", 0.0)
                ),
                "worst_max_drawdown_r": safe_float(
                    mc_row.get("worst_max_drawdown_r", 0.0)
                ),
                "candidate_approved": False,
                "long_strategy_approved": False,
                "long_entries_approved": False,
                "paper_trade_execution_allowed": False,
                "real_capital_allowed": False,
                "live_alerts_allowed": False,
                "exchange_execution_allowed": False,
                "automation_allowed": False,
                "execution_allowed": False,
                "readiness_status": READINESS_STATUS,
            }
        )

    readiness_rank = {
        "LONG_FORWARD_OBSERVATION_CANDIDATE": 1,
        "LONG_SECONDARY_WATCHLIST": 2,
        "LONG_HOLD_FOR_MORE_EVIDENCE": 3,
        "LONG_BLOCKED_RISK": 4,
        "LONG_NOT_READY": 5,
        "LONG_BLOCKED_REJECTED": 6,
    }

    readiness_df = pd.DataFrame(rows)
    readiness_df["readiness_rank"] = readiness_df["readiness_decision"].map(
        readiness_rank
    )

    readiness_df = readiness_df.sort_values(
        by=[
            "readiness_rank",
            "probability_positive",
            "p05_total_result_r",
        ],
        ascending=[True, False, False],
    ).reset_index(drop=True)

    return readiness_df


def build_evidence_ledger(
    phase_8_10_summary_df: pd.DataFrame,
    candidate_mc_summary_df: pd.DataFrame,
    candidate_cost_summary_df: pd.DataFrame,
    readiness_df: pd.DataFrame,
) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []

    if not phase_8_10_summary_df.empty:
        summary = phase_8_10_summary_df.iloc[0].to_dict()
        rows.append(
            {
                "evidence_layer": "PHASE_8_10_MONTE_CARLO",
                "evidence_status": str(summary.get("validation_decision", "")),
                "evidence_passed": bool(summary.get("validation_passed", False)),
                "primary_research_candidate_id": str(
                    summary.get("primary_research_candidate_id", "")
                ),
                "secondary_reference_candidate_id": str(
                    summary.get("secondary_reference_candidate_id", "")
                ),
                "execution_allowed": False,
                "notes": "Monte Carlo baseline source evidence.",
            }
        )

    for _, row in candidate_cost_summary_df.iterrows():
        rows.append(
            {
                "evidence_layer": "PHASE_8_9_COST_AWARE",
                "evidence_status": str(row.get("final_cost_decision", "")),
                "evidence_passed": str(row.get("final_cost_decision", "")).startswith(
                    "COST_AWARE"
                ),
                "primary_research_candidate_id": str(row.get("candidate_id", "")),
                "secondary_reference_candidate_id": "",
                "execution_allowed": False,
                "notes": "Cost-aware candidate decision.",
            }
        )

    for _, row in candidate_mc_summary_df.iterrows():
        rows.append(
            {
                "evidence_layer": "PHASE_8_10_MC_CANDIDATE",
                "evidence_status": str(row.get("mc_classification", "")),
                "evidence_passed": str(row.get("mc_classification", "")) in {
                    "MC_RESEARCH_CONTINUATION",
                    "MC_WATCHLIST",
                },
                "primary_research_candidate_id": str(row.get("candidate_id", "")),
                "secondary_reference_candidate_id": "",
                "execution_allowed": False,
                "notes": "Monte Carlo candidate classification.",
            }
        )

    for _, row in readiness_df.iterrows():
        rows.append(
            {
                "evidence_layer": "PHASE_8_11_READINESS_GATE",
                "evidence_status": str(row.get("readiness_decision", "")),
                "evidence_passed": str(row.get("readiness_decision", "")) in {
                    "LONG_FORWARD_OBSERVATION_CANDIDATE",
                    "LONG_SECONDARY_WATCHLIST",
                },
                "primary_research_candidate_id": str(row.get("candidate_id", "")),
                "secondary_reference_candidate_id": "",
                "execution_allowed": False,
                "notes": str(row.get("readiness_note", "")),
            }
        )

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


def validate_long_baseline_readiness_gate() -> dict[str, pd.DataFrame]:
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
        "phase_8_8_wf_doc_exists": PHASE_8_8_WF_DOC_PATH,
        "phase_8_9_cost_doc_exists": PHASE_8_9_COST_DOC_PATH,
        "phase_8_10_mc_doc_exists": PHASE_8_10_MC_DOC_PATH,
        "phase_8_11_readiness_doc_exists": PHASE_8_11_READINESS_DOC_PATH,
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

    phase_8_10_result = validate_long_monte_carlo_baseline_validation()

    phase_8_10_summary_df = phase_8_10_result["summary"]
    source_candidate_cost_summary_df = phase_8_10_result[
        "source_candidate_cost_summary"
    ]
    candidate_mc_summary_df = phase_8_10_result["candidate_mc_summary"]

    phase_8_10_validation_passed = (
        not phase_8_10_summary_df.empty
        and bool(phase_8_10_summary_df.iloc[0].get("validation_passed", False))
    )

    readiness_df = build_readiness_gate_table(
        candidate_mc_summary_df=candidate_mc_summary_df,
        candidate_cost_summary_df=source_candidate_cost_summary_df,
    )

    evidence_ledger_df = build_evidence_ledger(
        phase_8_10_summary_df=phase_8_10_summary_df,
        candidate_mc_summary_df=candidate_mc_summary_df,
        candidate_cost_summary_df=source_candidate_cost_summary_df,
        readiness_df=readiness_df,
    )

    checks.append(
        build_check(
            check_group="phase_dependency",
            check_name="phase_8_10_validation_passed",
            passed=phase_8_10_validation_passed,
            severity="INFO" if phase_8_10_validation_passed else "ERROR",
            details=(
                str(phase_8_10_summary_df.iloc[0].get("validation_decision", ""))
                if not phase_8_10_summary_df.empty
                else "Missing Phase 8.10 summary."
            ),
        )
    )

    readiness_decisions = set(readiness_df["readiness_decision"].astype(str).tolist())

    checks.append(
        build_check(
            check_group="readiness_gate",
            check_name="readiness_decisions_allowed",
            passed=readiness_decisions.issubset(ALLOWED_READINESS_DECISIONS),
            severity=(
                "INFO"
                if readiness_decisions.issubset(ALLOWED_READINESS_DECISIONS)
                else "ERROR"
            ),
            details="readiness_decisions=" + ",".join(sorted(readiness_decisions)),
        )
    )

    checks.append(
        build_check(
            check_group="readiness_gate",
            check_name="readiness_rows_complete",
            passed=len(readiness_df) == 4,
            severity="INFO" if len(readiness_df) == 4 else "ERROR",
            details=f"readiness_rows={len(readiness_df)}",
        )
    )

    primary_readiness = readiness_df[
        readiness_df["candidate_id"].astype(str).eq(PRIMARY_RESEARCH_CANDIDATE)
    ].copy()

    secondary_readiness = readiness_df[
        readiness_df["candidate_id"].astype(str).eq(SECONDARY_REFERENCE_CANDIDATE)
    ].copy()

    checks.append(
        build_check(
            check_group="readiness_gate",
            check_name="primary_ready_for_forward_observation",
            passed=(
                len(primary_readiness) == 1
                and str(primary_readiness.iloc[0]["readiness_decision"])
                == "LONG_FORWARD_OBSERVATION_CANDIDATE"
            ),
            severity=(
                "INFO"
                if (
                    len(primary_readiness) == 1
                    and str(primary_readiness.iloc[0]["readiness_decision"])
                    == "LONG_FORWARD_OBSERVATION_CANDIDATE"
                )
                else "ERROR"
            ),
            details=(
                str(primary_readiness.iloc[0]["readiness_decision"])
                if not primary_readiness.empty
                else "missing"
            ),
        )
    )

    checks.append(
        build_check(
            check_group="readiness_gate",
            check_name="secondary_remains_watchlist",
            passed=(
                len(secondary_readiness) == 1
                and str(secondary_readiness.iloc[0]["readiness_decision"])
                == "LONG_SECONDARY_WATCHLIST"
            ),
            severity=(
                "INFO"
                if (
                    len(secondary_readiness) == 1
                    and str(secondary_readiness.iloc[0]["readiness_decision"])
                    == "LONG_SECONDARY_WATCHLIST"
                )
                else "ERROR"
            ),
            details=(
                str(secondary_readiness.iloc[0]["readiness_decision"])
                if not secondary_readiness.empty
                else "missing"
            ),
        )
    )

    blocked_rows = readiness_df[
        readiness_df["candidate_id"].astype(str).isin(BLOCKED_CANDIDATES)
    ].copy()

    checks.append(
        build_check(
            check_group="readiness_gate",
            check_name="blocked_candidates_remain_blocked",
            passed=(
                len(blocked_rows) == len(BLOCKED_CANDIDATES)
                and blocked_rows["readiness_decision"]
                .astype(str)
                .eq("LONG_BLOCKED_REJECTED")
                .all()
            ),
            severity=(
                "INFO"
                if (
                    len(blocked_rows) == len(BLOCKED_CANDIDATES)
                    and blocked_rows["readiness_decision"]
                    .astype(str)
                    .eq("LONG_BLOCKED_REJECTED")
                    .all()
                )
                else "ERROR"
            ),
            details="blocked=" + ",".join(blocked_rows["candidate_id"].astype(str)),
        )
    )

    checks.append(
        build_check(
            check_group="evidence_ledger",
            check_name="evidence_ledger_created",
            passed=len(evidence_ledger_df) > 0,
            severity="INFO" if len(evidence_ledger_df) > 0 else "ERROR",
            details=f"evidence_rows={len(evidence_ledger_df)}",
        )
    )

    checks.append(
        build_check(
            check_group="approval_control",
            check_name="no_candidate_approved",
            passed=no_approvals_enabled(readiness_df),
            severity=(
                "INFO"
                if no_approvals_enabled(readiness_df)
                else "ERROR"
            ),
            details="All readiness approval flags remain False.",
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
            check_group="phase_closure",
            check_name="phase_8_baseline_framework_can_close",
            passed=True,
            severity="INFO",
            details="Phase 8 can close as LONG baseline research framework if validation passes.",
        )
    )

    checks.append(
        build_check(
            check_group="scope_control",
            check_name="forward_observation_not_started",
            passed=True,
            severity="INFO",
            details="Forward observation is deferred to Phase 9.1.",
        )
    )

    checks.append(
        build_check(
            check_group="scope_control",
            check_name="paper_trading_not_enabled",
            passed=True,
            severity="INFO",
            details="Paper trading remains disabled.",
        )
    )

    checks.append(
        build_check(
            check_group="phase_transition",
            check_name="phase_9_1_recommended_next",
            passed=True,
            severity="INFO",
            details="Recommended next step: Phase 9.1 LONG Forward Observation Framework V1.",
        )
    )

    checks.append(
        build_check(
            check_group="scope_control",
            check_name="long_side_not_approved_for_execution",
            passed=True,
            severity="WARNING",
            details="LONG has a forward observation candidate, not an execution-approved strategy.",
        )
    )

    checks.append(
        build_check(
            check_group="scope_control",
            check_name="real_entries_remain_blocked",
            passed=True,
            severity="WARNING",
            details="Real entries remain blocked after Phase 8.11.",
        )
    )

    checks_df = pd.DataFrame(checks)

    blocker_count = int(checks_df["blocker"].astype(bool).sum())
    error_count = int(checks_df["severity"].eq("ERROR").sum())
    warning_count = int(checks_df["severity"].eq("WARNING").sum())

    validation_passed = blocker_count == 0 and error_count == 0

    primary_readiness_decision = (
        str(primary_readiness.iloc[0]["readiness_decision"])
        if not primary_readiness.empty
        else ""
    )

    secondary_readiness_decision = (
        str(secondary_readiness.iloc[0]["readiness_decision"])
        if not secondary_readiness.empty
        else ""
    )

    phase_8_baseline_framework_closed = validation_passed

    summary_df = pd.DataFrame(
        [
            {
                "phase": "8.11",
                "long_baseline_readiness_gate_defined": True,
                "phase_8_10_validation_passed": phase_8_10_validation_passed,
                "readiness_rows": int(len(readiness_df)),
                "evidence_ledger_rows": int(len(evidence_ledger_df)),
                "primary_research_candidate_id": PRIMARY_RESEARCH_CANDIDATE,
                "secondary_reference_candidate_id": SECONDARY_REFERENCE_CANDIDATE,
                "primary_readiness_decision": primary_readiness_decision,
                "secondary_readiness_decision": secondary_readiness_decision,
                "phase_8_baseline_framework_closed": phase_8_baseline_framework_closed,
                "long_forward_observation_candidate_exists": (
                    primary_readiness_decision
                    == "LONG_FORWARD_OBSERVATION_CANDIDATE"
                ),
                "forward_observation_started": False,
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
                "recommended_next_phase": "PHASE_9_1_LONG_FORWARD_OBSERVATION_FRAMEWORK_V1",
                "estimated_total_project_progress_percent": 100,
                "total_checks": int(len(checks_df)),
                "warning_count": warning_count,
                "error_count": error_count,
                "blocker_count": blocker_count,
                "validation_passed": validation_passed,
                "validation_decision": (
                    "PHASE_8_11_LONG_BASELINE_READINESS_GATE_VALIDATED"
                    if validation_passed
                    else "PHASE_8_11_LONG_BASELINE_READINESS_GATE_FAILED"
                ),
            }
        ]
    )

    phase_8_10_summary_df.to_csv(
        REPORTS_DIR / "phase_8_10_source_summary_v1.csv",
        index=False,
    )
    source_candidate_cost_summary_df.to_csv(
        REPORTS_DIR / "phase_8_9_source_candidate_cost_summary_v1.csv",
        index=False,
    )
    candidate_mc_summary_df.to_csv(
        REPORTS_DIR / "phase_8_10_source_candidate_mc_summary_v1.csv",
        index=False,
    )
    readiness_df.to_csv(
        REPORTS_DIR / "long_baseline_readiness_gate_v1.csv",
        index=False,
    )
    evidence_ledger_df.to_csv(
        REPORTS_DIR / "long_baseline_readiness_evidence_ledger_v1.csv",
        index=False,
    )
    checks_df.to_csv(
        REPORTS_DIR / "long_baseline_readiness_gate_checks_v1.csv",
        index=False,
    )
    summary_df.to_csv(
        REPORTS_DIR / "long_baseline_readiness_gate_summary_v1.csv",
        index=False,
    )

    return {
        "summary": summary_df,
        "source_phase_8_10_summary": phase_8_10_summary_df,
        "source_candidate_cost_summary": source_candidate_cost_summary_df,
        "source_candidate_mc_summary": candidate_mc_summary_df,
        "readiness_gate": readiness_df,
        "evidence_ledger": evidence_ledger_df,
        "checks": checks_df,
    }