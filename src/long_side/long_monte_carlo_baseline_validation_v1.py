from __future__ import annotations

import random
from pathlib import Path
from typing import Any

import pandas as pd

from src.long_side.long_cost_aware_baseline_validation_v1 import (
    validate_long_cost_aware_baseline_validation,
)


REPORTS_DIR = Path("reports/phase_8_10_long_monte_carlo_baseline_validation_v1")

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

PRIMARY_RESEARCH_CANDIDATE = "LONG_BASE_FAILED_BREAKDOWN_V1"
SECONDARY_REFERENCE_CANDIDATE = "LONG_BASE_LIQUIDITY_SWEEP_V1"

BLOCKED_CANDIDATES = {
    "LONG_BASE_FIB_PULLBACK_V1",
    "LONG_BASE_MTF_BULLISH_CONTINUATION_V1",
}

MC_STATUS = "MONTE_CARLO_BASELINE_ONLY"
MC_COST_PROFILE = "STRESS_FRICTION"
MC_SIMULATIONS_PER_CANDIDATE = 1000
MC_RANDOM_SEED = 8102026

ALLOWED_MC_CLASSIFICATIONS = {
    "MC_RESEARCH_CONTINUATION",
    "MC_WATCHLIST",
    "MC_WEAK",
    "MC_FAIL",
    "MC_NO_SIGNAL",
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


def calculate_longest_losing_streak(result_values: list[float]) -> int:
    longest = 0
    current = 0

    for result in result_values:
        if result < 0:
            current += 1
            longest = max(longest, current)
        else:
            current = 0

    return longest


def quantile_value(series: pd.Series, q: float, default: float = 0.0) -> float:
    clean = pd.to_numeric(series, errors="coerce").dropna()

    if clean.empty:
        return default

    return float(clean.quantile(q))


def build_cost_decision_lookup(candidate_cost_summary_df: pd.DataFrame) -> dict[str, str]:
    lookup: dict[str, str] = {}

    if candidate_cost_summary_df.empty:
        return lookup

    for _, row in candidate_cost_summary_df.iterrows():
        candidate_id = str(row.get("candidate_id", ""))
        final_cost_decision = str(row.get("final_cost_decision", ""))

        if candidate_id:
            lookup[candidate_id] = final_cost_decision

    return lookup


def get_stress_trades(
    cost_adjusted_trades_df: pd.DataFrame,
    candidate_ids: list[str],
) -> pd.DataFrame:
    if cost_adjusted_trades_df.empty:
        return pd.DataFrame()

    return cost_adjusted_trades_df[
        cost_adjusted_trades_df["candidate_id"].astype(str).isin(candidate_ids)
        & cost_adjusted_trades_df["cost_profile"].astype(str).eq(MC_COST_PROFILE)
    ].copy()


def build_monte_carlo_simulations(
    stress_trades_df: pd.DataFrame,
    candidate_ids: list[str],
) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []

    rng = random.Random(MC_RANDOM_SEED)

    for candidate_id in candidate_ids:
        candidate_trades = stress_trades_df[
            stress_trades_df["candidate_id"].astype(str).eq(candidate_id)
        ].copy()

        result_values = pd.to_numeric(
            candidate_trades.get("cost_adjusted_result_r", pd.Series(dtype=float)),
            errors="coerce",
        ).dropna().astype(float).tolist()

        source_trade_count = len(result_values)

        if source_trade_count == 0:
            continue

        for simulation_number in range(1, MC_SIMULATIONS_PER_CANDIDATE + 1):
            sampled_results = rng.choices(result_values, k=source_trade_count)

            simulated_total_result_r = float(sum(sampled_results))
            simulated_average_result_r = simulated_total_result_r / source_trade_count
            simulated_max_drawdown_r = calculate_max_drawdown_r(sampled_results)
            simulated_longest_losing_streak = calculate_longest_losing_streak(
                sampled_results
            )

            rows.append(
                {
                    "candidate_id": candidate_id,
                    "simulation_id": f"MC_{simulation_number:04d}",
                    "cost_profile": MC_COST_PROFILE,
                    "source_trade_count": source_trade_count,
                    "simulated_trade_count": source_trade_count,
                    "simulated_total_result_r": simulated_total_result_r,
                    "simulated_average_result_r": simulated_average_result_r,
                    "simulated_max_drawdown_r": simulated_max_drawdown_r,
                    "simulated_longest_losing_streak": simulated_longest_losing_streak,
                    "positive_result": simulated_total_result_r > 0,
                    "drawdown_breach_minus_5r": simulated_max_drawdown_r <= -5.0,
                    "drawdown_breach_minus_7_5r": simulated_max_drawdown_r <= -7.5,
                    "candidate_approved": False,
                    "long_strategy_approved": False,
                    "long_entries_approved": False,
                    "paper_trade_execution_allowed": False,
                    "real_capital_allowed": False,
                    "live_alerts_allowed": False,
                    "exchange_execution_allowed": False,
                    "automation_allowed": False,
                    "execution_allowed": False,
                    "mc_status": MC_STATUS,
                }
            )

    return pd.DataFrame(rows)


def classify_monte_carlo_candidate(row: pd.Series) -> tuple[str, str]:
    source_trade_count = safe_int(row.get("source_trade_count", 0))
    original_total_result_r = safe_float(row.get("original_total_result_r", 0.0))
    probability_positive = safe_float(row.get("probability_positive", 0.0))
    p05_total_result_r = safe_float(row.get("p05_total_result_r", 0.0))
    p50_total_result_r = safe_float(row.get("p50_total_result_r", 0.0))
    p05_max_drawdown_r = safe_float(row.get("p05_max_drawdown_r", 0.0))
    final_cost_decision = str(row.get("final_cost_decision", ""))

    if source_trade_count == 0:
        return "MC_NO_SIGNAL", "No source trades available for Monte Carlo validation."

    if original_total_result_r <= 0:
        return "MC_FAIL", "Original stress-cost sequence is not positive."

    if final_cost_decision == "COST_AWARE_RESEARCH_CONTINUATION":
        if (
            probability_positive >= 0.60
            and p05_total_result_r >= -5.0
            and p05_max_drawdown_r >= -8.0
        ):
            return (
                "MC_RESEARCH_CONTINUATION",
                "Candidate survives Monte Carlo baseline sequence stress.",
            )

        if probability_positive >= 0.50 and p50_total_result_r > 0:
            return (
                "MC_WATCHLIST",
                "Candidate remains positive but sequence risk requires caution.",
            )

    if final_cost_decision == "COST_AWARE_WATCHLIST":
        if probability_positive >= 0.50 and p50_total_result_r > 0:
            return (
                "MC_WATCHLIST",
                "Watchlist candidate remains positive under Monte Carlo baseline.",
            )

    if probability_positive < 0.40 or p50_total_result_r <= 0 or p05_total_result_r <= -7.5:
        return "MC_FAIL", "Candidate fails Monte Carlo baseline sequence stress."

    return "MC_WEAK", "Candidate is weak or inconclusive after Monte Carlo baseline."


def build_monte_carlo_candidate_summary(
    stress_trades_df: pd.DataFrame,
    simulations_df: pd.DataFrame,
    candidate_cost_summary_df: pd.DataFrame,
    candidate_ids: list[str],
) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    cost_decision_lookup = build_cost_decision_lookup(candidate_cost_summary_df)

    for candidate_id in candidate_ids:
        candidate_stress_trades = stress_trades_df[
            stress_trades_df["candidate_id"].astype(str).eq(candidate_id)
        ].copy()

        original_results = pd.to_numeric(
            candidate_stress_trades.get(
                "cost_adjusted_result_r",
                pd.Series(dtype=float),
            ),
            errors="coerce",
        ).dropna()

        if simulations_df.empty:
            candidate_simulations = pd.DataFrame()
        else:
            candidate_simulations = simulations_df[
                simulations_df["candidate_id"].astype(str).eq(candidate_id)
            ].copy()

        source_trade_count = int(len(original_results))
        original_total_result_r = float(original_results.sum()) if source_trade_count > 0 else 0.0
        original_average_result_r = (
            original_total_result_r / source_trade_count
            if source_trade_count > 0
            else 0.0
        )
        original_max_drawdown_r = (
            calculate_max_drawdown_r(original_results.astype(float).tolist())
            if source_trade_count > 0
            else 0.0
        )
        original_longest_losing_streak = (
            calculate_longest_losing_streak(original_results.astype(float).tolist())
            if source_trade_count > 0
            else 0
        )

        simulated_total = (
            pd.to_numeric(
                candidate_simulations.get(
                    "simulated_total_result_r",
                    pd.Series(dtype=float),
                ),
                errors="coerce",
            )
            if not candidate_simulations.empty
            else pd.Series(dtype=float)
        )

        simulated_drawdown = (
            pd.to_numeric(
                candidate_simulations.get(
                    "simulated_max_drawdown_r",
                    pd.Series(dtype=float),
                ),
                errors="coerce",
            )
            if not candidate_simulations.empty
            else pd.Series(dtype=float)
        )

        simulated_losing_streak = (
            pd.to_numeric(
                candidate_simulations.get(
                    "simulated_longest_losing_streak",
                    pd.Series(dtype=float),
                ),
                errors="coerce",
            )
            if not candidate_simulations.empty
            else pd.Series(dtype=float)
        )

        simulation_count = int(len(candidate_simulations))

        probability_positive = (
            float(candidate_simulations["positive_result"].astype(bool).mean())
            if simulation_count > 0 and "positive_result" in candidate_simulations.columns
            else 0.0
        )

        probability_drawdown_breach_minus_5r = (
            float(candidate_simulations["drawdown_breach_minus_5r"].astype(bool).mean())
            if simulation_count > 0
            and "drawdown_breach_minus_5r" in candidate_simulations.columns
            else 0.0
        )

        probability_drawdown_breach_minus_7_5r = (
            float(candidate_simulations["drawdown_breach_minus_7_5r"].astype(bool).mean())
            if simulation_count > 0
            and "drawdown_breach_minus_7_5r" in candidate_simulations.columns
            else 0.0
        )

        base_row = pd.Series(
            {
                "source_trade_count": source_trade_count,
                "original_total_result_r": original_total_result_r,
                "probability_positive": probability_positive,
                "p05_total_result_r": quantile_value(simulated_total, 0.05),
                "p50_total_result_r": quantile_value(simulated_total, 0.50),
                "p05_max_drawdown_r": quantile_value(simulated_drawdown, 0.05),
                "final_cost_decision": cost_decision_lookup.get(candidate_id, ""),
            }
        )

        mc_classification, mc_note = classify_monte_carlo_candidate(base_row)

        rows.append(
            {
                "candidate_id": candidate_id,
                "cost_profile": MC_COST_PROFILE,
                "final_cost_decision": cost_decision_lookup.get(candidate_id, ""),
                "source_trade_count": source_trade_count,
                "simulation_count": simulation_count,
                "original_total_result_r": original_total_result_r,
                "original_average_result_r": original_average_result_r,
                "original_max_drawdown_r": original_max_drawdown_r,
                "original_longest_losing_streak": original_longest_losing_streak,
                "mean_total_result_r": (
                    float(simulated_total.mean()) if simulation_count > 0 else 0.0
                ),
                "p05_total_result_r": quantile_value(simulated_total, 0.05),
                "p50_total_result_r": quantile_value(simulated_total, 0.50),
                "p95_total_result_r": quantile_value(simulated_total, 0.95),
                "p05_max_drawdown_r": quantile_value(simulated_drawdown, 0.05),
                "p50_max_drawdown_r": quantile_value(simulated_drawdown, 0.50),
                "worst_max_drawdown_r": (
                    float(simulated_drawdown.min()) if simulation_count > 0 else 0.0
                ),
                "p95_longest_losing_streak": quantile_value(
                    simulated_losing_streak,
                    0.95,
                ),
                "probability_positive": probability_positive,
                "probability_drawdown_breach_minus_5r": probability_drawdown_breach_minus_5r,
                "probability_drawdown_breach_minus_7_5r": probability_drawdown_breach_minus_7_5r,
                "mc_classification": mc_classification,
                "mc_note": mc_note,
                "candidate_approved": False,
                "long_strategy_approved": False,
                "long_entries_approved": False,
                "paper_trade_execution_allowed": False,
                "real_capital_allowed": False,
                "live_alerts_allowed": False,
                "exchange_execution_allowed": False,
                "automation_allowed": False,
                "execution_allowed": False,
                "mc_status": MC_STATUS,
            }
        )

    result_df = pd.DataFrame(rows)

    classification_rank = {
        "MC_RESEARCH_CONTINUATION": 1,
        "MC_WATCHLIST": 2,
        "MC_WEAK": 3,
        "MC_NO_SIGNAL": 4,
        "MC_FAIL": 5,
    }

    if not result_df.empty:
        result_df["mc_classification_rank"] = result_df["mc_classification"].map(
            classification_rank
        )
        result_df = result_df.sort_values(
            by=[
                "mc_classification_rank",
                "candidate_id",
                "probability_positive",
                "p05_total_result_r",
            ],
            ascending=[True, True, False, False],
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


def validate_long_monte_carlo_baseline_validation() -> dict[str, pd.DataFrame]:
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

    phase_8_9_result = validate_long_cost_aware_baseline_validation()

    source_summary_df = phase_8_9_result["summary"]
    source_candidate_metrics_df = phase_8_9_result["source_candidate_metrics"]
    cost_profiles_df = phase_8_9_result["cost_profiles"]
    cost_adjusted_trades_df = phase_8_9_result["cost_adjusted_trades"]
    cost_metrics_df = phase_8_9_result["cost_metrics"]
    candidate_cost_summary_df = phase_8_9_result["candidate_cost_summary"]

    phase_8_9_validation_passed = (
        not source_summary_df.empty
        and bool(source_summary_df.iloc[0].get("validation_passed", False))
    )

    candidate_ids = [
        PRIMARY_RESEARCH_CANDIDATE,
        SECONDARY_REFERENCE_CANDIDATE,
    ]

    stress_trades_df = get_stress_trades(
        cost_adjusted_trades_df=cost_adjusted_trades_df,
        candidate_ids=candidate_ids,
    )
    monte_carlo_simulations_df = build_monte_carlo_simulations(
        stress_trades_df=stress_trades_df,
        candidate_ids=candidate_ids,
    )
    candidate_mc_summary_df = build_monte_carlo_candidate_summary(
        stress_trades_df=stress_trades_df,
        simulations_df=monte_carlo_simulations_df,
        candidate_cost_summary_df=candidate_cost_summary_df,
        candidate_ids=candidate_ids,
    )

    checks.append(
        build_check(
            check_group="phase_dependency",
            check_name="phase_8_9_validation_passed",
            passed=phase_8_9_validation_passed,
            severity="INFO" if phase_8_9_validation_passed else "ERROR",
            details=(
                str(source_summary_df.iloc[0].get("validation_decision", ""))
                if not source_summary_df.empty
                else "Missing Phase 8.9 summary."
            ),
        )
    )

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

    checks.append(
        build_check(
            check_group="candidate_scope",
            check_name="primary_candidate_carried_forward",
            passed=(
                len(primary_cost_summary) == 1
                and str(primary_cost_summary.iloc[0]["final_cost_decision"])
                == "COST_AWARE_RESEARCH_CONTINUATION"
            ),
            severity=(
                "INFO"
                if (
                    len(primary_cost_summary) == 1
                    and str(primary_cost_summary.iloc[0]["final_cost_decision"])
                    == "COST_AWARE_RESEARCH_CONTINUATION"
                )
                else "ERROR"
            ),
            details=f"primary={PRIMARY_RESEARCH_CANDIDATE}",
        )
    )

    checks.append(
        build_check(
            check_group="candidate_scope",
            check_name="secondary_candidate_carried_forward_as_reference",
            passed=(
                len(secondary_cost_summary) == 1
                and str(secondary_cost_summary.iloc[0]["final_cost_decision"])
                == "COST_AWARE_WATCHLIST"
            ),
            severity=(
                "INFO"
                if (
                    len(secondary_cost_summary) == 1
                    and str(secondary_cost_summary.iloc[0]["final_cost_decision"])
                    == "COST_AWARE_WATCHLIST"
                )
                else "ERROR"
            ),
            details=f"secondary={SECONDARY_REFERENCE_CANDIDATE}",
        )
    )

    checks.append(
        build_check(
            check_group="candidate_scope",
            check_name="blocked_candidates_not_in_mc_scope",
            passed=BLOCKED_CANDIDATES.isdisjoint(set(candidate_ids)),
            severity=(
                "INFO"
                if BLOCKED_CANDIDATES.isdisjoint(set(candidate_ids))
                else "ERROR"
            ),
            details=(
                "blocked="
                + ",".join(sorted(BLOCKED_CANDIDATES))
                + ";mc_candidates="
                + ",".join(candidate_ids)
            ),
        )
    )

    checks.append(
        build_check(
            check_group="cost_dependency",
            check_name="stress_cost_profile_present",
            passed=cost_profiles_df["cost_profile"].astype(str).eq(MC_COST_PROFILE).any(),
            severity=(
                "INFO"
                if cost_profiles_df["cost_profile"].astype(str).eq(MC_COST_PROFILE).any()
                else "ERROR"
            ),
            details=f"required_profile={MC_COST_PROFILE}",
        )
    )

    checks.append(
        build_check(
            check_group="monte_carlo",
            check_name="stress_trades_present",
            passed=len(stress_trades_df) > 0,
            severity="INFO" if len(stress_trades_df) > 0 else "ERROR",
            details=f"stress_trade_rows={len(stress_trades_df)}",
        )
    )

    expected_simulation_rows = MC_SIMULATIONS_PER_CANDIDATE * len(candidate_ids)

    checks.append(
        build_check(
            check_group="monte_carlo",
            check_name="monte_carlo_simulations_created",
            passed=len(monte_carlo_simulations_df) == expected_simulation_rows,
            severity=(
                "INFO"
                if len(monte_carlo_simulations_df) == expected_simulation_rows
                else "ERROR"
            ),
            details=(
                f"simulation_rows={len(monte_carlo_simulations_df)}, "
                f"expected={expected_simulation_rows}"
            ),
        )
    )

    checks.append(
        build_check(
            check_group="monte_carlo",
            check_name="candidate_mc_summary_created",
            passed=len(candidate_mc_summary_df) == len(candidate_ids),
            severity=(
                "INFO"
                if len(candidate_mc_summary_df) == len(candidate_ids)
                else "ERROR"
            ),
            details=f"candidate_mc_summary_rows={len(candidate_mc_summary_df)}",
        )
    )

    mc_classifications = (
        set(candidate_mc_summary_df["mc_classification"].astype(str).tolist())
        if not candidate_mc_summary_df.empty
        else set()
    )

    checks.append(
        build_check(
            check_group="classification",
            check_name="mc_classifications_allowed",
            passed=mc_classifications.issubset(ALLOWED_MC_CLASSIFICATIONS),
            severity=(
                "INFO"
                if mc_classifications.issubset(ALLOWED_MC_CLASSIFICATIONS)
                else "ERROR"
            ),
            details="classifications=" + ",".join(sorted(mc_classifications)),
        )
    )

    primary_mc_summary = candidate_mc_summary_df[
        candidate_mc_summary_df["candidate_id"].astype(str).eq(
            PRIMARY_RESEARCH_CANDIDATE
        )
    ].copy()

    checks.append(
        build_check(
            check_group="monte_carlo",
            check_name="primary_mc_result_recorded",
            passed=not primary_mc_summary.empty,
            severity="INFO" if not primary_mc_summary.empty else "ERROR",
            details=(
                "primary_mc_classification="
                + (
                    str(primary_mc_summary.iloc[0]["mc_classification"])
                    if not primary_mc_summary.empty
                    else ""
                )
            ),
        )
    )

    checks.append(
        build_check(
            check_group="approval_control",
            check_name="no_candidate_approved",
            passed=no_approvals_enabled(
                monte_carlo_simulations_df,
                candidate_mc_summary_df,
            ),
            severity=(
                "INFO"
                if no_approvals_enabled(
                    monte_carlo_simulations_df,
                    candidate_mc_summary_df,
                )
                else "ERROR"
            ),
            details="All Monte Carlo approval flags remain False.",
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
            check_name="live_execution_not_used",
            passed=True,
            severity="INFO",
            details="Monte Carlo uses saved research outputs only.",
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
            check_name="phase_8_11_recommended_next",
            passed=True,
            severity="INFO",
            details="Recommended next step: Phase 8.11 LONG Baseline Readiness Gate V1.",
        )
    )

    checks.append(
        build_check(
            check_group="scope_control",
            check_name="long_side_remains_unestablished",
            passed=True,
            severity="WARNING",
            details="Phase 8.10 validates Monte Carlo baseline only; LONG side is not established.",
        )
    )

    checks.append(
        build_check(
            check_group="scope_control",
            check_name="real_entries_remain_blocked",
            passed=True,
            severity="WARNING",
            details="Real entries remain blocked after Phase 8.10.",
        )
    )

    checks_df = pd.DataFrame(checks)

    blocker_count = int(checks_df["blocker"].astype(bool).sum())
    error_count = int(checks_df["severity"].eq("ERROR").sum())
    warning_count = int(checks_df["severity"].eq("WARNING").sum())

    validation_passed = blocker_count == 0 and error_count == 0

    primary_mc_classification = (
        str(primary_mc_summary.iloc[0]["mc_classification"])
        if not primary_mc_summary.empty
        else ""
    )

    primary_probability_positive = (
        float(primary_mc_summary.iloc[0]["probability_positive"])
        if not primary_mc_summary.empty
        else 0.0
    )

    primary_p05_total_result_r = (
        float(primary_mc_summary.iloc[0]["p05_total_result_r"])
        if not primary_mc_summary.empty
        else 0.0
    )

    primary_p05_max_drawdown_r = (
        float(primary_mc_summary.iloc[0]["p05_max_drawdown_r"])
        if not primary_mc_summary.empty
        else 0.0
    )

    secondary_mc_summary = candidate_mc_summary_df[
        candidate_mc_summary_df["candidate_id"].astype(str).eq(
            SECONDARY_REFERENCE_CANDIDATE
        )
    ].copy()

    secondary_mc_classification = (
        str(secondary_mc_summary.iloc[0]["mc_classification"])
        if not secondary_mc_summary.empty
        else ""
    )

    summary_df = pd.DataFrame(
        [
            {
                "phase": "8.10",
                "monte_carlo_baseline_defined": True,
                "phase_8_9_validation_passed": phase_8_9_validation_passed,
                "source_cost_adjusted_trade_rows": int(len(cost_adjusted_trades_df)),
                "stress_trade_rows": int(len(stress_trades_df)),
                "source_cost_metrics_rows": int(len(cost_metrics_df)),
                "source_candidate_cost_summary_rows": int(len(candidate_cost_summary_df)),
                "mc_cost_profile": MC_COST_PROFILE,
                "mc_random_seed": MC_RANDOM_SEED,
                "mc_simulations_per_candidate": MC_SIMULATIONS_PER_CANDIDATE,
                "mc_simulation_rows": int(len(monte_carlo_simulations_df)),
                "candidate_mc_summary_rows": int(len(candidate_mc_summary_df)),
                "primary_research_candidate_id": PRIMARY_RESEARCH_CANDIDATE,
                "secondary_reference_candidate_id": SECONDARY_REFERENCE_CANDIDATE,
                "primary_mc_classification": primary_mc_classification,
                "primary_probability_positive": primary_probability_positive,
                "primary_p05_total_result_r": primary_p05_total_result_r,
                "primary_p05_max_drawdown_r": primary_p05_max_drawdown_r,
                "secondary_mc_classification": secondary_mc_classification,
                "monte_carlo_validation_executed": True,
                "live_execution_used": False,
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
                "recommended_next_phase": "PHASE_8_11_LONG_BASELINE_READINESS_GATE_V1",
                "estimated_total_project_progress_percent": 99,
                "total_checks": int(len(checks_df)),
                "warning_count": warning_count,
                "error_count": error_count,
                "blocker_count": blocker_count,
                "validation_passed": validation_passed,
                "validation_decision": (
                    "PHASE_8_10_LONG_MONTE_CARLO_BASELINE_VALIDATION_VALIDATED"
                    if validation_passed
                    else "PHASE_8_10_LONG_MONTE_CARLO_BASELINE_VALIDATION_FAILED"
                ),
            }
        ]
    )

    source_summary_df.to_csv(
        REPORTS_DIR / "phase_8_9_source_summary_v1.csv",
        index=False,
    )
    candidate_cost_summary_df.to_csv(
        REPORTS_DIR / "phase_8_9_source_candidate_cost_summary_v1.csv",
        index=False,
    )
    stress_trades_df.to_csv(
        REPORTS_DIR / "long_monte_carlo_source_stress_trades_v1.csv",
        index=False,
    )
    monte_carlo_simulations_df.to_csv(
        REPORTS_DIR / "long_monte_carlo_simulations_v1.csv",
        index=False,
    )
    candidate_mc_summary_df.to_csv(
        REPORTS_DIR / "long_monte_carlo_candidate_summary_v1.csv",
        index=False,
    )
    checks_df.to_csv(
        REPORTS_DIR / "long_monte_carlo_baseline_checks_v1.csv",
        index=False,
    )
    summary_df.to_csv(
        REPORTS_DIR / "long_monte_carlo_baseline_summary_v1.csv",
        index=False,
    )

    return {
        "summary": summary_df,
        "source_summary": source_summary_df,
        "source_candidate_cost_summary": candidate_cost_summary_df,
        "source_stress_trades": stress_trades_df,
        "monte_carlo_simulations": monte_carlo_simulations_df,
        "candidate_mc_summary": candidate_mc_summary_df,
        "checks": checks_df,
    }