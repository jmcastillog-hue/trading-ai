from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from src.long_side.long_walk_forward_baseline_validation_v1 import (
    validate_long_walk_forward_baseline_validation,
)


REPORTS_DIR = Path("reports/phase_8_9_long_cost_aware_baseline_validation_v1")

PHASE_8_1_CONTRACT_DOC_PATH = Path("docs/PHASE_8_LONG_SIDE_VALIDATION_CONTRACT.md")
PHASE_8_2_DISCOVERY_DOC_PATH = Path("docs/PHASE_8_LONG_CANDIDATE_DISCOVERY_BASELINE.md")
PHASE_8_3_HARNESS_DOC_PATH = Path("docs/PHASE_8_LONG_BASELINE_STRUCTURAL_BACKTEST_HARNESS.md")
PHASE_8_4_HISTORICAL_DOC_PATH = Path("docs/PHASE_8_LONG_HISTORICAL_BASELINE_BACKTEST.md")
PHASE_8_5_COMPARISON_DOC_PATH = Path("docs/PHASE_8_LONG_CANDIDATE_HISTORICAL_COMPARISON.md")
PHASE_8_6_OOS_DOC_PATH = Path("docs/PHASE_8_LONG_OOS_BASELINE_VALIDATION.md")
PHASE_8_7_DECISION_DOC_PATH = Path("docs/PHASE_8_LONG_OOS_DECISION_GATE.md")
PHASE_8_8_WF_DOC_PATH = Path("docs/PHASE_8_LONG_WALK_FORWARD_BASELINE_VALIDATION.md")
PHASE_8_9_COST_DOC_PATH = Path("docs/PHASE_8_LONG_COST_AWARE_BASELINE_VALIDATION.md")

PRIMARY_RESEARCH_CANDIDATE = "LONG_BASE_FAILED_BREAKDOWN_V1"
SECONDARY_REFERENCE_CANDIDATE = "LONG_BASE_LIQUIDITY_SWEEP_V1"

BLOCKED_CANDIDATES = {
    "LONG_BASE_FIB_PULLBACK_V1",
    "LONG_BASE_MTF_BULLISH_CONTINUATION_V1",
}

COST_STATUS = "COST_AWARE_BASELINE_ONLY"

COST_PROFILES = [
    {
        "cost_profile": "LOW_FRICTION",
        "round_trip_cost_bps": 6.0,
        "description": "Low estimated round-trip trading friction.",
    },
    {
        "cost_profile": "BASELINE_FRICTION",
        "round_trip_cost_bps": 12.0,
        "description": "Baseline estimated round-trip trading friction.",
    },
    {
        "cost_profile": "STRESS_FRICTION",
        "round_trip_cost_bps": 24.0,
        "description": "Stress estimated round-trip trading friction.",
    },
]

ALLOWED_COST_CLASSIFICATIONS = {
    "COST_RESEARCH_CONTINUATION",
    "COST_WATCHLIST",
    "COST_WEAK",
    "COST_FAIL",
    "COST_NO_SIGNAL",
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


def calculate_max_drawdown_r(result_values: list[float]) -> float:
    equity = 0.0
    peak = 0.0
    max_drawdown = 0.0

    for result in result_values:
        equity += result
        peak = max(peak, equity)
        drawdown = equity - peak
        max_drawdown = min(max_drawdown, drawdown)

    return max_drawdown


def calculate_risk_bps(entry_price: float, risk: float) -> float:
    if entry_price <= 0 or risk <= 0:
        return 0.0

    return abs(risk / entry_price) * 10000.0


def calculate_cost_r(round_trip_cost_bps: float, risk_bps: float) -> float:
    if risk_bps <= 0:
        return 0.0

    return round_trip_cost_bps / risk_bps


def build_cost_adjusted_trades(
    wf_trades_df: pd.DataFrame,
    candidate_ids: list[str],
) -> pd.DataFrame:
    if wf_trades_df.empty:
        return pd.DataFrame()

    rows: list[dict[str, Any]] = []

    scoped_trades_df = wf_trades_df[
        wf_trades_df["candidate_id"].astype(str).isin(candidate_ids)
    ].copy()

    for _, trade in scoped_trades_df.iterrows():
        entry_price = safe_float(trade.get("entry_price", 0.0))
        risk = safe_float(trade.get("risk", 0.0))
        raw_result_r = safe_float(trade.get("result_r", 0.0))
        risk_bps = calculate_risk_bps(entry_price=entry_price, risk=risk)

        for profile in COST_PROFILES:
            cost_profile = str(profile["cost_profile"])
            round_trip_cost_bps = safe_float(profile["round_trip_cost_bps"])
            cost_r = calculate_cost_r(
                round_trip_cost_bps=round_trip_cost_bps,
                risk_bps=risk_bps,
            )
            cost_adjusted_result_r = raw_result_r - cost_r

            row = trade.to_dict()
            row["cost_profile"] = cost_profile
            row["round_trip_cost_bps"] = round_trip_cost_bps
            row["risk_bps"] = risk_bps
            row["cost_r"] = cost_r
            row["raw_result_r"] = raw_result_r
            row["cost_adjusted_result_r"] = cost_adjusted_result_r
            row["cost_status"] = COST_STATUS
            row["long_strategy_approved"] = False
            row["long_entries_approved"] = False
            row["execution_allowed"] = False
            rows.append(row)

    return pd.DataFrame(rows)


def classify_cost_metrics(row: pd.Series) -> tuple[str, str]:
    trades = safe_int(row.get("trades", 0))
    total_result_r = safe_float(row.get("cost_adjusted_total_result_r", 0.0))
    profit_factor = safe_float(row.get("cost_adjusted_profit_factor", 0.0))
    max_drawdown_r = safe_float(row.get("max_drawdown_r", 0.0))

    if trades == 0:
        return "COST_NO_SIGNAL", "No trades available for cost-aware validation."

    if total_result_r > 0 and profit_factor >= 1.50 and max_drawdown_r >= -5:
        return (
            "COST_RESEARCH_CONTINUATION",
            "Candidate survives cost-aware baseline validation.",
        )

    if total_result_r > 0 and profit_factor >= 1.00:
        return (
            "COST_WATCHLIST",
            "Candidate remains positive after costs but should stay under watch.",
        )

    if total_result_r <= -3 or profit_factor < 0.75:
        return (
            "COST_FAIL",
            "Candidate fails cost-aware baseline under this profile.",
        )

    return (
        "COST_WEAK",
        "Candidate is weak or inconclusive after cost adjustment.",
    )


def build_cost_metrics(cost_trades_df: pd.DataFrame, candidate_ids: list[str]) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []

    for candidate_id in candidate_ids:
        for profile in COST_PROFILES:
            cost_profile = str(profile["cost_profile"])
            round_trip_cost_bps = safe_float(profile["round_trip_cost_bps"])

            group = cost_trades_df[
                cost_trades_df["candidate_id"].astype(str).eq(candidate_id)
                & cost_trades_df["cost_profile"].astype(str).eq(cost_profile)
            ].copy()

            adjusted_result = pd.to_numeric(
                group.get("cost_adjusted_result_r", pd.Series(dtype=float)),
                errors="coerce",
            ).fillna(0.0)

            raw_result = pd.to_numeric(
                group.get("raw_result_r", pd.Series(dtype=float)),
                errors="coerce",
            ).fillna(0.0)

            cost_r = pd.to_numeric(
                group.get("cost_r", pd.Series(dtype=float)),
                errors="coerce",
            ).fillna(0.0)

            trades = int(len(group))
            wins = int((adjusted_result > 0).sum())
            losses = int((adjusted_result < 0).sum())

            open_trades = (
                int(group["resolution_status"].astype(str).eq("OPEN_TIMEOUT").sum())
                if trades > 0 and "resolution_status" in group.columns
                else 0
            )

            gross_win_r = (
                float(adjusted_result[adjusted_result > 0].sum())
                if trades > 0
                else 0.0
            )
            gross_loss_r = (
                float(adjusted_result[adjusted_result < 0].sum())
                if trades > 0
                else 0.0
            )

            if gross_loss_r < 0:
                profit_factor = gross_win_r / abs(gross_loss_r)
            elif gross_win_r > 0:
                profit_factor = 999.0
            else:
                profit_factor = 0.0

            max_drawdown_r = (
                calculate_max_drawdown_r(adjusted_result.tolist())
                if trades > 0
                else 0.0
            )

            base_row = pd.Series(
                {
                    "trades": trades,
                    "cost_adjusted_total_result_r": (
                        float(adjusted_result.sum()) if trades > 0 else 0.0
                    ),
                    "cost_adjusted_profit_factor": profit_factor,
                    "max_drawdown_r": max_drawdown_r,
                }
            )

            cost_classification, cost_note = classify_cost_metrics(base_row)

            rows.append(
                {
                    "candidate_id": candidate_id,
                    "cost_profile": cost_profile,
                    "round_trip_cost_bps": round_trip_cost_bps,
                    "trades": trades,
                    "wins": wins,
                    "losses": losses,
                    "open_trades": open_trades,
                    "cost_adjusted_win_rate": wins / trades if trades > 0 else 0.0,
                    "raw_total_result_r": float(raw_result.sum()) if trades > 0 else 0.0,
                    "total_cost_r": float(cost_r.sum()) if trades > 0 else 0.0,
                    "average_cost_r": float(cost_r.mean()) if trades > 0 else 0.0,
                    "cost_adjusted_total_result_r": (
                        float(adjusted_result.sum()) if trades > 0 else 0.0
                    ),
                    "cost_adjusted_average_result_r": (
                        float(adjusted_result.mean()) if trades > 0 else 0.0
                    ),
                    "gross_win_r": gross_win_r,
                    "gross_loss_r": gross_loss_r,
                    "cost_adjusted_profit_factor": profit_factor,
                    "max_drawdown_r": max_drawdown_r,
                    "cost_classification": cost_classification,
                    "cost_note": cost_note,
                    "candidate_approved": False,
                    "long_strategy_approved": False,
                    "long_entries_approved": False,
                    "paper_trade_execution_allowed": False,
                    "real_capital_allowed": False,
                    "live_alerts_allowed": False,
                    "exchange_execution_allowed": False,
                    "automation_allowed": False,
                    "execution_allowed": False,
                    "cost_status": COST_STATUS,
                }
            )

    metrics_df = pd.DataFrame(rows)

    classification_rank = {
        "COST_RESEARCH_CONTINUATION": 1,
        "COST_WATCHLIST": 2,
        "COST_WEAK": 3,
        "COST_NO_SIGNAL": 4,
        "COST_FAIL": 5,
    }

    if not metrics_df.empty:
        metrics_df["cost_classification_rank"] = metrics_df["cost_classification"].map(
            classification_rank
        )
        metrics_df = metrics_df.sort_values(
            by=[
                "cost_classification_rank",
                "candidate_id",
                "round_trip_cost_bps",
            ],
            ascending=[True, True, True],
        ).reset_index(drop=True)

    return metrics_df


def build_candidate_cost_summary(cost_metrics_df: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []

    if cost_metrics_df.empty:
        return pd.DataFrame()

    for candidate_id, group in cost_metrics_df.groupby("candidate_id", sort=True):
        stress_group = group[
            group["cost_profile"].astype(str).eq("STRESS_FRICTION")
        ].copy()

        baseline_group = group[
            group["cost_profile"].astype(str).eq("BASELINE_FRICTION")
        ].copy()

        if not stress_group.empty:
            decisive_row = stress_group.iloc[0]
            decisive_profile = "STRESS_FRICTION"
        elif not baseline_group.empty:
            decisive_row = baseline_group.iloc[0]
            decisive_profile = "BASELINE_FRICTION"
        else:
            decisive_row = group.iloc[0]
            decisive_profile = str(decisive_row["cost_profile"])

        decisive_classification = str(decisive_row["cost_classification"])

        if decisive_classification == "COST_RESEARCH_CONTINUATION":
            final_cost_decision = "COST_AWARE_RESEARCH_CONTINUATION"
        elif decisive_classification == "COST_WATCHLIST":
            final_cost_decision = "COST_AWARE_WATCHLIST"
        elif decisive_classification == "COST_WEAK":
            final_cost_decision = "COST_AWARE_WEAK"
        else:
            final_cost_decision = "COST_AWARE_FAIL"

        rows.append(
            {
                "candidate_id": candidate_id,
                "profiles_tested": int(len(group)),
                "decisive_cost_profile": decisive_profile,
                "decisive_cost_classification": decisive_classification,
                "final_cost_decision": final_cost_decision,
                "best_cost_adjusted_total_result_r": float(
                    pd.to_numeric(
                        group["cost_adjusted_total_result_r"],
                        errors="coerce",
                    ).max()
                ),
                "worst_cost_adjusted_total_result_r": float(
                    pd.to_numeric(
                        group["cost_adjusted_total_result_r"],
                        errors="coerce",
                    ).min()
                ),
                "stress_cost_adjusted_total_result_r": safe_float(
                    decisive_row.get("cost_adjusted_total_result_r", 0.0)
                ),
                "stress_cost_adjusted_profit_factor": safe_float(
                    decisive_row.get("cost_adjusted_profit_factor", 0.0)
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
                "cost_status": COST_STATUS,
            }
        )

    decision_rank = {
        "COST_AWARE_RESEARCH_CONTINUATION": 1,
        "COST_AWARE_WATCHLIST": 2,
        "COST_AWARE_WEAK": 3,
        "COST_AWARE_FAIL": 4,
    }

    result_df = pd.DataFrame(rows)
    result_df["final_cost_decision_rank"] = result_df["final_cost_decision"].map(
        decision_rank
    )

    result_df = result_df.sort_values(
        by=[
            "final_cost_decision_rank",
            "stress_cost_adjusted_total_result_r",
            "stress_cost_adjusted_profit_factor",
        ],
        ascending=[True, False, False],
    ).reset_index(drop=True)

    return result_df


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


def validate_long_cost_aware_baseline_validation() -> dict[str, pd.DataFrame]:
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

    phase_8_8_result = validate_long_walk_forward_baseline_validation()

    source_summary_df = phase_8_8_result["summary"]
    source_candidate_metrics_df = phase_8_8_result["candidate_metrics"]
    source_wf_trades_df = phase_8_8_result["wf_trades"]
    source_decision_gate_df = phase_8_8_result["source_decision_gate"]

    phase_8_8_validation_passed = (
        not source_summary_df.empty
        and bool(source_summary_df.iloc[0].get("validation_passed", False))
    )

    primary_df = source_decision_gate_df[
        source_decision_gate_df["candidate_id"].astype(str).eq(
            PRIMARY_RESEARCH_CANDIDATE
        )
        & source_decision_gate_df["gate_decision"].astype(str).eq(
            "ADVANCE_TO_STRICT_VALIDATION"
        )
    ].copy()

    secondary_df = source_decision_gate_df[
        source_decision_gate_df["candidate_id"].astype(str).eq(
            SECONDARY_REFERENCE_CANDIDATE
        )
        & source_decision_gate_df["gate_decision"].astype(str).eq(
            "SECONDARY_WATCHLIST_ONLY"
        )
    ].copy()

    candidate_ids = [
        PRIMARY_RESEARCH_CANDIDATE,
        SECONDARY_REFERENCE_CANDIDATE,
    ]

    cost_profiles_df = pd.DataFrame(COST_PROFILES)
    cost_trades_df = build_cost_adjusted_trades(
        wf_trades_df=source_wf_trades_df,
        candidate_ids=candidate_ids,
    )
    cost_metrics_df = build_cost_metrics(
        cost_trades_df=cost_trades_df,
        candidate_ids=candidate_ids,
    )
    candidate_cost_summary_df = build_candidate_cost_summary(cost_metrics_df)

    checks.append(
        build_check(
            check_group="phase_dependency",
            check_name="phase_8_8_validation_passed",
            passed=phase_8_8_validation_passed,
            severity="INFO" if phase_8_8_validation_passed else "ERROR",
            details=(
                str(source_summary_df.iloc[0].get("validation_decision", ""))
                if not source_summary_df.empty
                else "Missing Phase 8.8 summary."
            ),
        )
    )

    checks.append(
        build_check(
            check_group="candidate_scope",
            check_name="primary_candidate_carried_forward",
            passed=len(primary_df) == 1,
            severity="INFO" if len(primary_df) == 1 else "ERROR",
            details=f"primary={PRIMARY_RESEARCH_CANDIDATE}",
        )
    )

    checks.append(
        build_check(
            check_group="candidate_scope",
            check_name="secondary_candidate_carried_forward_as_reference",
            passed=len(secondary_df) == 1,
            severity="INFO" if len(secondary_df) == 1 else "ERROR",
            details=f"secondary={SECONDARY_REFERENCE_CANDIDATE}",
        )
    )

    wf_candidate_ids = set(source_candidate_metrics_df["candidate_id"].astype(str).tolist())

    checks.append(
        build_check(
            check_group="candidate_scope",
            check_name="blocked_candidates_not_in_cost_scope",
            passed=BLOCKED_CANDIDATES.isdisjoint(set(candidate_ids))
            and BLOCKED_CANDIDATES.isdisjoint(wf_candidate_ids),
            severity=(
                "INFO"
                if BLOCKED_CANDIDATES.isdisjoint(set(candidate_ids))
                and BLOCKED_CANDIDATES.isdisjoint(wf_candidate_ids)
                else "ERROR"
            ),
            details=(
                "blocked="
                + ",".join(sorted(BLOCKED_CANDIDATES))
                + ";cost_candidates="
                + ",".join(candidate_ids)
            ),
        )
    )

    checks.append(
        build_check(
            check_group="cost_profiles",
            check_name="cost_profiles_defined",
            passed=len(cost_profiles_df) == 3,
            severity="INFO" if len(cost_profiles_df) == 3 else "ERROR",
            details="profiles=" + ",".join(cost_profiles_df["cost_profile"].astype(str)),
        )
    )

    checks.append(
        build_check(
            check_group="cost_profiles",
            check_name="stress_profile_present",
            passed=cost_profiles_df["cost_profile"].astype(str).eq("STRESS_FRICTION").any(),
            severity=(
                "INFO"
                if cost_profiles_df["cost_profile"].astype(str).eq("STRESS_FRICTION").any()
                else "ERROR"
            ),
            details="Stress profile required for cost-aware baseline.",
        )
    )

    checks.append(
        build_check(
            check_group="cost_adjustment",
            check_name="cost_adjusted_trades_created",
            passed=len(cost_trades_df) == len(source_wf_trades_df) * len(COST_PROFILES),
            severity=(
                "INFO"
                if len(cost_trades_df) == len(source_wf_trades_df) * len(COST_PROFILES)
                else "ERROR"
            ),
            details=f"cost_adjusted_trades={len(cost_trades_df)}",
        )
    )

    checks.append(
        build_check(
            check_group="cost_adjustment",
            check_name="cost_metrics_created",
            passed=len(cost_metrics_df) == len(candidate_ids) * len(COST_PROFILES),
            severity=(
                "INFO"
                if len(cost_metrics_df) == len(candidate_ids) * len(COST_PROFILES)
                else "ERROR"
            ),
            details=f"cost_metrics_rows={len(cost_metrics_df)}",
        )
    )

    checks.append(
        build_check(
            check_group="cost_adjustment",
            check_name="candidate_cost_summary_created",
            passed=len(candidate_cost_summary_df) == len(candidate_ids),
            severity=(
                "INFO"
                if len(candidate_cost_summary_df) == len(candidate_ids)
                else "ERROR"
            ),
            details=f"candidate_cost_summary_rows={len(candidate_cost_summary_df)}",
        )
    )

    classifications = (
        set(cost_metrics_df["cost_classification"].astype(str).tolist())
        if not cost_metrics_df.empty
        else set()
    )

    checks.append(
        build_check(
            check_group="classification",
            check_name="cost_classifications_allowed",
            passed=classifications.issubset(ALLOWED_COST_CLASSIFICATIONS),
            severity=(
                "INFO"
                if classifications.issubset(ALLOWED_COST_CLASSIFICATIONS)
                else "ERROR"
            ),
            details="classifications=" + ",".join(sorted(classifications)),
        )
    )

    if not cost_trades_df.empty:
        cost_never_improves_result = (
            cost_trades_df["cost_adjusted_result_r"]
            <= cost_trades_df["raw_result_r"]
        ).all()
        positive_costs_present = cost_trades_df["cost_r"].gt(0).all()
    else:
        cost_never_improves_result = False
        positive_costs_present = False

    checks.append(
        build_check(
            check_group="cost_adjustment",
            check_name="cost_never_improves_raw_result",
            passed=bool(cost_never_improves_result),
            severity="INFO" if cost_never_improves_result else "ERROR",
            details=f"cost_never_improves_result={cost_never_improves_result}",
        )
    )

    checks.append(
        build_check(
            check_group="cost_adjustment",
            check_name="positive_costs_present",
            passed=bool(positive_costs_present),
            severity="INFO" if positive_costs_present else "ERROR",
            details=f"positive_costs_present={positive_costs_present}",
        )
    )

    checks.append(
        build_check(
            check_group="approval_control",
            check_name="no_candidate_approved",
            passed=no_approvals_enabled(cost_metrics_df, candidate_cost_summary_df),
            severity=(
                "INFO"
                if no_approvals_enabled(cost_metrics_df, candidate_cost_summary_df)
                else "ERROR"
            ),
            details="All cost-aware approval flags remain False.",
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
            check_name="live_exchange_fees_not_used",
            passed=True,
            severity="INFO",
            details="Cost profiles are research assumptions only.",
        )
    )

    checks.append(
        build_check(
            check_group="scope_control",
            check_name="monte_carlo_not_executed",
            passed=True,
            severity="INFO",
            details="Monte Carlo validation is deferred to Phase 8.10.",
        )
    )

    checks.append(
        build_check(
            check_group="phase_transition",
            check_name="phase_8_10_recommended_next",
            passed=True,
            severity="INFO",
            details="Recommended next step: Phase 8.10 LONG Monte Carlo Baseline Validation V1.",
        )
    )

    checks.append(
        build_check(
            check_group="scope_control",
            check_name="long_side_remains_unestablished",
            passed=True,
            severity="WARNING",
            details="Phase 8.9 validates cost-aware baseline only; LONG side is not established.",
        )
    )

    checks.append(
        build_check(
            check_group="scope_control",
            check_name="real_entries_remain_blocked",
            passed=True,
            severity="WARNING",
            details="Real entries remain blocked after Phase 8.9.",
        )
    )

    checks_df = pd.DataFrame(checks)

    blocker_count = int(checks_df["blocker"].astype(bool).sum())
    error_count = int(checks_df["severity"].eq("ERROR").sum())
    warning_count = int(checks_df["severity"].eq("WARNING").sum())

    validation_passed = blocker_count == 0 and error_count == 0

    primary_cost_summary = candidate_cost_summary_df[
        candidate_cost_summary_df["candidate_id"].astype(str).eq(
            PRIMARY_RESEARCH_CANDIDATE
        )
    ].copy()

    secondary_cost_summary = candidate_cost_summary_df[
        candidate_cost_summary_df["candidate_id"].astype(str).eq(
            SECONDARY_REFERENCE_CANDIDATE
        )
    ].copy()

    primary_final_cost_decision = (
        str(primary_cost_summary.iloc[0]["final_cost_decision"])
        if not primary_cost_summary.empty
        else ""
    )

    primary_stress_result_r = (
        float(primary_cost_summary.iloc[0]["stress_cost_adjusted_total_result_r"])
        if not primary_cost_summary.empty
        else 0.0
    )

    primary_stress_profit_factor = (
        float(primary_cost_summary.iloc[0]["stress_cost_adjusted_profit_factor"])
        if not primary_cost_summary.empty
        else 0.0
    )

    secondary_final_cost_decision = (
        str(secondary_cost_summary.iloc[0]["final_cost_decision"])
        if not secondary_cost_summary.empty
        else ""
    )

    summary_df = pd.DataFrame(
        [
            {
                "phase": "8.9",
                "cost_aware_baseline_defined": True,
                "phase_8_8_validation_passed": phase_8_8_validation_passed,
                "source_wf_trade_count": int(len(source_wf_trades_df)),
                "source_candidate_metrics_rows": int(len(source_candidate_metrics_df)),
                "cost_profile_count": int(len(cost_profiles_df)),
                "cost_adjusted_trade_rows": int(len(cost_trades_df)),
                "cost_metrics_rows": int(len(cost_metrics_df)),
                "candidate_cost_summary_rows": int(len(candidate_cost_summary_df)),
                "primary_research_candidate_id": PRIMARY_RESEARCH_CANDIDATE,
                "secondary_reference_candidate_id": SECONDARY_REFERENCE_CANDIDATE,
                "primary_final_cost_decision": primary_final_cost_decision,
                "primary_stress_cost_adjusted_total_result_r": primary_stress_result_r,
                "primary_stress_cost_adjusted_profit_factor": primary_stress_profit_factor,
                "secondary_final_cost_decision": secondary_final_cost_decision,
                "cost_aware_validation_executed": True,
                "live_exchange_fees_used": False,
                "monte_carlo_executed": False,
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
                "recommended_next_phase": "PHASE_8_10_LONG_MONTE_CARLO_BASELINE_VALIDATION_V1",
                "estimated_total_project_progress_percent": 98,
                "total_checks": int(len(checks_df)),
                "warning_count": warning_count,
                "error_count": error_count,
                "blocker_count": blocker_count,
                "validation_passed": validation_passed,
                "validation_decision": (
                    "PHASE_8_9_LONG_COST_AWARE_BASELINE_VALIDATION_VALIDATED"
                    if validation_passed
                    else "PHASE_8_9_LONG_COST_AWARE_BASELINE_VALIDATION_FAILED"
                ),
            }
        ]
    )

    source_summary_df.to_csv(
        REPORTS_DIR / "phase_8_8_source_summary_v1.csv",
        index=False,
    )
    source_candidate_metrics_df.to_csv(
        REPORTS_DIR / "phase_8_8_source_candidate_metrics_v1.csv",
        index=False,
    )
    cost_profiles_df.to_csv(
        REPORTS_DIR / "long_cost_profiles_v1.csv",
        index=False,
    )
    cost_trades_df.to_csv(
        REPORTS_DIR / "long_cost_adjusted_trades_v1.csv",
        index=False,
    )
    cost_metrics_df.to_csv(
        REPORTS_DIR / "long_cost_aware_metrics_v1.csv",
        index=False,
    )
    candidate_cost_summary_df.to_csv(
        REPORTS_DIR / "long_cost_aware_candidate_summary_v1.csv",
        index=False,
    )
    checks_df.to_csv(
        REPORTS_DIR / "long_cost_aware_baseline_checks_v1.csv",
        index=False,
    )
    summary_df.to_csv(
        REPORTS_DIR / "long_cost_aware_baseline_summary_v1.csv",
        index=False,
    )

    return {
        "summary": summary_df,
        "source_summary": source_summary_df,
        "source_candidate_metrics": source_candidate_metrics_df,
        "cost_profiles": cost_profiles_df,
        "cost_adjusted_trades": cost_trades_df,
        "cost_metrics": cost_metrics_df,
        "candidate_cost_summary": candidate_cost_summary_df,
        "checks": checks_df,
    }