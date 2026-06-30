from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from src.long_side.long_candidate_discovery_baseline_v1 import EXPECTED_CANDIDATES
from src.long_side.long_historical_baseline_backtest_v1 import (
    validate_long_historical_baseline_backtest,
)


REPORTS_DIR = Path("reports/phase_8_5_long_candidate_historical_comparison_v1")

PHASE_8_1_CONTRACT_DOC_PATH = Path("docs/PHASE_8_LONG_SIDE_VALIDATION_CONTRACT.md")
PHASE_8_2_DISCOVERY_DOC_PATH = Path("docs/PHASE_8_LONG_CANDIDATE_DISCOVERY_BASELINE.md")
PHASE_8_3_HARNESS_DOC_PATH = Path("docs/PHASE_8_LONG_BASELINE_STRUCTURAL_BACKTEST_HARNESS.md")
PHASE_8_4_HISTORICAL_DOC_PATH = Path("docs/PHASE_8_LONG_HISTORICAL_BASELINE_BACKTEST.md")
PHASE_8_5_COMPARISON_DOC_PATH = Path("docs/PHASE_8_LONG_CANDIDATE_HISTORICAL_COMPARISON.md")

ALLOWED_CLASSIFICATIONS = {
    "REJECT",
    "WEAK",
    "WATCHLIST",
    "RESEARCH_CONTINUATION",
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


def classify_candidate(row: pd.Series) -> tuple[str, str, int, str]:
    trades = safe_int(row.get("trades", 0))
    win_rate = safe_float(row.get("win_rate", 0.0))
    profit_factor = safe_float(row.get("profit_factor", 0.0))
    total_result_r = safe_float(row.get("total_result_r", 0.0))
    average_result_r = safe_float(row.get("average_result_r", 0.0))
    max_drawdown_r = safe_float(row.get("max_drawdown_r", 0.0))

    evidence_score = 0
    reasons: list[str] = []

    if trades >= 20:
        evidence_score += 2
        reasons.append("trade_count_sufficient")
    elif trades >= 10:
        evidence_score += 1
        reasons.append("trade_count_minimum")
    else:
        evidence_score -= 2
        reasons.append("trade_count_low")

    if profit_factor >= 1.50:
        evidence_score += 3
        reasons.append("profit_factor_strong")
    elif profit_factor >= 1.00:
        evidence_score += 1
        reasons.append("profit_factor_positive")
    elif profit_factor < 0.75:
        evidence_score -= 3
        reasons.append("profit_factor_poor")
    else:
        evidence_score -= 1
        reasons.append("profit_factor_weak")

    if total_result_r > 5:
        evidence_score += 2
        reasons.append("total_result_positive_strong")
    elif total_result_r > 0:
        evidence_score += 1
        reasons.append("total_result_positive")
    elif total_result_r <= -5:
        evidence_score -= 3
        reasons.append("total_result_negative_strong")
    else:
        evidence_score -= 1
        reasons.append("total_result_flat_or_negative")

    if average_result_r > 0:
        evidence_score += 1
        reasons.append("average_result_positive")
    else:
        evidence_score -= 1
        reasons.append("average_result_not_positive")

    if win_rate >= 0.40:
        evidence_score += 1
        reasons.append("win_rate_acceptable_for_rr_2_5")
    elif win_rate < 0.15:
        evidence_score -= 2
        reasons.append("win_rate_poor")
    else:
        reasons.append("win_rate_low_but_possible_with_rr_2_5")

    if max_drawdown_r <= -8:
        evidence_score -= 2
        reasons.append("drawdown_poor")
    elif max_drawdown_r >= -5:
        evidence_score += 1
        reasons.append("drawdown_acceptable_baseline")
    else:
        reasons.append("drawdown_moderate")

    if trades == 0:
        classification = "REJECT"
        recommendation = "Reject until candidate produces historical signals."
    elif total_result_r <= -5 and profit_factor < 0.75:
        classification = "REJECT"
        recommendation = "Reject as-is. Redesign required before further testing."
    elif total_result_r <= 0 or profit_factor < 1.0:
        classification = "WEAK"
        recommendation = "Do not prioritize. Keep only for later redesign review."
    elif (
        total_result_r > 0
        and profit_factor >= 1.50
        and trades >= 10
        and max_drawdown_r >= -5
    ):
        classification = "RESEARCH_CONTINUATION"
        recommendation = "Continue to stricter validation. No execution approval."
    elif total_result_r > 0 and profit_factor >= 1.0 and trades >= 10:
        classification = "WATCHLIST"
        recommendation = "Keep on watchlist and test under OOS restrictions."
    else:
        classification = "WEAK"
        recommendation = "Evidence is inconclusive. Do not prioritize."

    return classification, recommendation, evidence_score, ";".join(reasons)


def build_historical_comparison(metrics_df: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []

    if metrics_df.empty:
        return pd.DataFrame(
            columns=[
                "candidate_id",
                "trades",
                "wins",
                "losses",
                "open_trades",
                "win_rate",
                "profit_factor",
                "total_result_r",
                "average_result_r",
                "max_drawdown_r",
                "historical_classification",
                "evidence_score",
                "classification_reasons",
                "recommended_action",
                "candidate_approved",
                "long_strategy_approved",
                "long_entries_approved",
                "execution_allowed",
            ]
        )

    for _, row in metrics_df.iterrows():
        classification, recommendation, evidence_score, reasons = classify_candidate(row)

        rows.append(
            {
                "candidate_id": str(row.get("candidate_id", "")),
                "trades": safe_int(row.get("trades", 0)),
                "wins": safe_int(row.get("wins", 0)),
                "losses": safe_int(row.get("losses", 0)),
                "open_trades": safe_int(row.get("open_trades", 0)),
                "win_rate": safe_float(row.get("win_rate", 0.0)),
                "gross_win_r": safe_float(row.get("gross_win_r", 0.0)),
                "gross_loss_r": safe_float(row.get("gross_loss_r", 0.0)),
                "profit_factor": safe_float(row.get("profit_factor", 0.0)),
                "total_result_r": safe_float(row.get("total_result_r", 0.0)),
                "average_result_r": safe_float(row.get("average_result_r", 0.0)),
                "max_drawdown_r": safe_float(row.get("max_drawdown_r", 0.0)),
                "historical_classification": classification,
                "evidence_score": evidence_score,
                "classification_reasons": reasons,
                "recommended_action": recommendation,
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

    comparison_df = pd.DataFrame(rows)

    classification_rank = {
        "RESEARCH_CONTINUATION": 1,
        "WATCHLIST": 2,
        "WEAK": 3,
        "REJECT": 4,
    }

    comparison_df["classification_rank"] = comparison_df["historical_classification"].map(
        classification_rank
    )

    comparison_df = comparison_df.sort_values(
        by=[
            "classification_rank",
            "evidence_score",
            "total_result_r",
            "profit_factor",
        ],
        ascending=[True, False, False, False],
    ).reset_index(drop=True)

    return comparison_df


def no_approvals_enabled(comparison_df: pd.DataFrame) -> bool:
    if comparison_df.empty:
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
        if column not in comparison_df.columns:
            return False

        if comparison_df[column].astype(bool).any():
            return False

    return True


def validate_long_candidate_historical_comparison() -> dict[str, pd.DataFrame]:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    checks: list[dict[str, Any]] = []

    phase_anchors = {
        "phase_8_1_contract_doc_exists": PHASE_8_1_CONTRACT_DOC_PATH,
        "phase_8_2_discovery_doc_exists": PHASE_8_2_DISCOVERY_DOC_PATH,
        "phase_8_3_harness_doc_exists": PHASE_8_3_HARNESS_DOC_PATH,
        "phase_8_4_historical_doc_exists": PHASE_8_4_HISTORICAL_DOC_PATH,
        "phase_8_5_comparison_doc_exists": PHASE_8_5_COMPARISON_DOC_PATH,
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

    phase_8_4_result = validate_long_historical_baseline_backtest()

    phase_8_4_summary_df = phase_8_4_result["summary"]
    phase_8_4_metrics_df = phase_8_4_result["metrics"]
    phase_8_4_trades_df = phase_8_4_result["trades"]

    comparison_df = build_historical_comparison(phase_8_4_metrics_df)

    phase_8_4_validation_passed = (
        not phase_8_4_summary_df.empty
        and bool(phase_8_4_summary_df.iloc[0].get("validation_passed", False))
    )

    checks.append(
        build_check(
            check_group="phase_dependency",
            check_name="phase_8_4_validation_passed",
            passed=phase_8_4_validation_passed,
            severity="INFO" if phase_8_4_validation_passed else "ERROR",
            details=(
                str(phase_8_4_summary_df.iloc[0].get("validation_decision", ""))
                if not phase_8_4_summary_df.empty
                else "Missing Phase 8.4 summary."
            ),
        )
    )

    checks.append(
        build_check(
            check_group="candidate_scope",
            check_name="all_expected_candidates_compared",
            passed=set(comparison_df["candidate_id"].tolist()) == set(EXPECTED_CANDIDATES),
            severity=(
                "INFO"
                if set(comparison_df["candidate_id"].tolist()) == set(EXPECTED_CANDIDATES)
                else "ERROR"
            ),
            details=",".join(comparison_df["candidate_id"].tolist()),
        )
    )

    checks.append(
        build_check(
            check_group="candidate_scope",
            check_name="comparison_rows_match_expected_candidates",
            passed=len(comparison_df) == len(EXPECTED_CANDIDATES),
            severity="INFO" if len(comparison_df) == len(EXPECTED_CANDIDATES) else "ERROR",
            details=f"comparison_rows={len(comparison_df)}",
        )
    )

    classifications = set(comparison_df["historical_classification"].astype(str).tolist())

    checks.append(
        build_check(
            check_group="classification",
            check_name="classifications_are_allowed",
            passed=classifications.issubset(ALLOWED_CLASSIFICATIONS),
            severity="INFO" if classifications.issubset(ALLOWED_CLASSIFICATIONS) else "ERROR",
            details="classifications=" + ",".join(sorted(classifications)),
        )
    )

    checks.append(
        build_check(
            check_group="classification",
            check_name="positive_and_negative_candidates_separated",
            passed=(
                comparison_df["total_result_r"].gt(0).any()
                and comparison_df["total_result_r"].lt(0).any()
            ),
            severity=(
                "INFO"
                if (
                    comparison_df["total_result_r"].gt(0).any()
                    and comparison_df["total_result_r"].lt(0).any()
                )
                else "WARNING"
            ),
            details=(
                "positive_candidates="
                + str(int(comparison_df["total_result_r"].gt(0).sum()))
                + ", negative_candidates="
                + str(int(comparison_df["total_result_r"].lt(0).sum()))
            ),
        )
    )

    checks.append(
        build_check(
            check_group="classification",
            check_name="at_least_one_candidate_not_rejected",
            passed=comparison_df["historical_classification"].isin(
                ["WATCHLIST", "RESEARCH_CONTINUATION"]
            ).any(),
            severity=(
                "INFO"
                if comparison_df["historical_classification"].isin(
                    ["WATCHLIST", "RESEARCH_CONTINUATION"]
                ).any()
                else "WARNING"
            ),
            details=(
                "continuation_or_watchlist_count="
                + str(
                    int(
                        comparison_df["historical_classification"].isin(
                            ["WATCHLIST", "RESEARCH_CONTINUATION"]
                        ).sum()
                    )
                )
            ),
        )
    )

    checks.append(
        build_check(
            check_group="approval_control",
            check_name="no_candidate_approved",
            passed=no_approvals_enabled(comparison_df),
            severity="INFO" if no_approvals_enabled(comparison_df) else "ERROR",
            details="All candidate approval flags remain False.",
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
            check_name="out_of_sample_not_executed",
            passed=True,
            severity="INFO",
            details="OOS validation is deferred to Phase 8.6.",
        )
    )

    checks.append(
        build_check(
            check_group="scope_control",
            check_name="walk_forward_not_executed",
            passed=True,
            severity="INFO",
            details="Walk-forward validation is deferred.",
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
            check_group="phase_transition",
            check_name="phase_8_6_recommended_next",
            passed=True,
            severity="INFO",
            details="Recommended next step: Phase 8.6 LONG OOS Baseline Validation V1.",
        )
    )

    checks.append(
        build_check(
            check_group="scope_control",
            check_name="long_side_remains_unestablished",
            passed=True,
            severity="WARNING",
            details="Phase 8.5 classifies historical evidence only; LONG side is not established.",
        )
    )

    checks.append(
        build_check(
            check_group="scope_control",
            check_name="real_entries_remain_blocked",
            passed=True,
            severity="WARNING",
            details="Real entries remain blocked after Phase 8.5.",
        )
    )

    checks_df = pd.DataFrame(checks)

    blocker_count = int(checks_df["blocker"].astype(bool).sum())
    error_count = int(checks_df["severity"].eq("ERROR").sum())
    warning_count = int(checks_df["severity"].eq("WARNING").sum())

    validation_passed = blocker_count == 0 and error_count == 0

    classification_counts = comparison_df["historical_classification"].value_counts().to_dict()

    summary_df = pd.DataFrame(
        [
            {
                "phase": "8.5",
                "historical_comparison_defined": True,
                "phase_8_4_validation_passed": phase_8_4_validation_passed,
                "source_trade_count": int(len(phase_8_4_trades_df)),
                "source_metrics_rows": int(len(phase_8_4_metrics_df)),
                "comparison_rows": int(len(comparison_df)),
                "reject_count": int(classification_counts.get("REJECT", 0)),
                "weak_count": int(classification_counts.get("WEAK", 0)),
                "watchlist_count": int(classification_counts.get("WATCHLIST", 0)),
                "research_continuation_count": int(
                    classification_counts.get("RESEARCH_CONTINUATION", 0)
                ),
                "best_candidate_id": (
                    str(comparison_df.iloc[0]["candidate_id"])
                    if not comparison_df.empty
                    else ""
                ),
                "best_candidate_classification": (
                    str(comparison_df.iloc[0]["historical_classification"])
                    if not comparison_df.empty
                    else ""
                ),
                "best_candidate_total_result_r": (
                    float(comparison_df.iloc[0]["total_result_r"])
                    if not comparison_df.empty
                    else 0.0
                ),
                "best_candidate_profit_factor": (
                    float(comparison_df.iloc[0]["profit_factor"])
                    if not comparison_df.empty
                    else 0.0
                ),
                "historical_comparison_executed": True,
                "out_of_sample_executed": False,
                "walk_forward_executed": False,
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
                "recommended_next_phase": "PHASE_8_6_LONG_OOS_BASELINE_VALIDATION_V1",
                "estimated_total_project_progress_percent": 94,
                "total_checks": int(len(checks_df)),
                "warning_count": warning_count,
                "error_count": error_count,
                "blocker_count": blocker_count,
                "validation_passed": validation_passed,
                "validation_decision": (
                    "PHASE_8_5_LONG_CANDIDATE_HISTORICAL_COMPARISON_VALIDATED"
                    if validation_passed
                    else "PHASE_8_5_LONG_CANDIDATE_HISTORICAL_COMPARISON_FAILED"
                ),
            }
        ]
    )

    phase_8_4_summary_df.to_csv(
        REPORTS_DIR / "phase_8_4_source_summary_v1.csv",
        index=False,
    )
    phase_8_4_metrics_df.to_csv(
        REPORTS_DIR / "phase_8_4_source_metrics_v1.csv",
        index=False,
    )
    comparison_df.to_csv(
        REPORTS_DIR / "long_candidate_historical_comparison_v1.csv",
        index=False,
    )
    checks_df.to_csv(
        REPORTS_DIR / "long_candidate_historical_comparison_checks_v1.csv",
        index=False,
    )
    summary_df.to_csv(
        REPORTS_DIR / "long_candidate_historical_comparison_summary_v1.csv",
        index=False,
    )

    return {
        "summary": summary_df,
        "source_summary": phase_8_4_summary_df,
        "source_metrics": phase_8_4_metrics_df,
        "comparison": comparison_df,
        "checks": checks_df,
    }