from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from src.long_side.long_candidate_historical_comparison_v1 import (
    validate_long_candidate_historical_comparison,
)
from src.long_side.long_historical_baseline_backtest_v1 import (
    add_indicators,
    build_candidate_metrics,
    candidate_signal_indexes,
    find_historical_data_path,
    normalize_ohlc_df,
    resolve_long_trade,
)


REPORTS_DIR = Path("reports/phase_8_6_long_oos_baseline_validation_v1")

PHASE_8_1_CONTRACT_DOC_PATH = Path("docs/PHASE_8_LONG_SIDE_VALIDATION_CONTRACT.md")
PHASE_8_2_DISCOVERY_DOC_PATH = Path("docs/PHASE_8_LONG_CANDIDATE_DISCOVERY_BASELINE.md")
PHASE_8_3_HARNESS_DOC_PATH = Path("docs/PHASE_8_LONG_BASELINE_STRUCTURAL_BACKTEST_HARNESS.md")
PHASE_8_4_HISTORICAL_DOC_PATH = Path("docs/PHASE_8_LONG_HISTORICAL_BASELINE_BACKTEST.md")
PHASE_8_5_COMPARISON_DOC_PATH = Path("docs/PHASE_8_LONG_CANDIDATE_HISTORICAL_COMPARISON.md")
PHASE_8_6_OOS_DOC_PATH = Path("docs/PHASE_8_LONG_OOS_BASELINE_VALIDATION.md")

OOS_STATUS = "OOS_BASELINE_ONLY"
OOS_START_FRACTION = 0.70

ELIGIBLE_CLASSIFICATIONS = {
    "WATCHLIST",
    "RESEARCH_CONTINUATION",
}

EXPECTED_ELIGIBLE_CANDIDATES = {
    "LONG_BASE_FAILED_BREAKDOWN_V1",
    "LONG_BASE_LIQUIDITY_SWEEP_V1",
}

EXPECTED_EXCLUDED_CANDIDATES = {
    "LONG_BASE_FIB_PULLBACK_V1",
    "LONG_BASE_MTF_BULLISH_CONTINUATION_V1",
}

ALLOWED_OOS_CLASSIFICATIONS = {
    "OOS_RESEARCH_CONTINUATION",
    "OOS_WATCHLIST",
    "OOS_WEAK",
    "OOS_FAIL",
    "OOS_NO_SIGNAL",
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


def classify_oos_candidate(row: pd.Series) -> tuple[str, str, int, str]:
    trades = safe_int(row.get("trades", 0))
    win_rate = safe_float(row.get("win_rate", 0.0))
    profit_factor = safe_float(row.get("profit_factor", 0.0))
    total_result_r = safe_float(row.get("total_result_r", 0.0))
    average_result_r = safe_float(row.get("average_result_r", 0.0))
    max_drawdown_r = safe_float(row.get("max_drawdown_r", 0.0))

    score = 0
    reasons: list[str] = []

    if trades == 0:
        return (
            "OOS_NO_SIGNAL",
            "No OOS trades were produced. Keep blocked and collect more data.",
            -3,
            "no_oos_trades",
        )

    if trades >= 10:
        score += 2
        reasons.append("oos_trade_count_sufficient")
    elif trades >= 3:
        score += 1
        reasons.append("oos_trade_count_limited")
    else:
        score -= 1
        reasons.append("oos_trade_count_low")

    if profit_factor >= 1.50:
        score += 3
        reasons.append("oos_profit_factor_strong")
    elif profit_factor >= 1.00:
        score += 1
        reasons.append("oos_profit_factor_positive")
    elif profit_factor < 0.75:
        score -= 3
        reasons.append("oos_profit_factor_poor")
    else:
        score -= 1
        reasons.append("oos_profit_factor_weak")

    if total_result_r > 3:
        score += 2
        reasons.append("oos_total_result_positive_strong")
    elif total_result_r > 0:
        score += 1
        reasons.append("oos_total_result_positive")
    elif total_result_r <= -3:
        score -= 3
        reasons.append("oos_total_result_negative_strong")
    else:
        score -= 1
        reasons.append("oos_total_result_flat_or_negative")

    if average_result_r > 0:
        score += 1
        reasons.append("oos_average_result_positive")
    else:
        score -= 1
        reasons.append("oos_average_result_not_positive")

    if win_rate >= 0.40:
        score += 1
        reasons.append("oos_win_rate_acceptable_for_rr_2_5")
    elif win_rate < 0.15:
        score -= 2
        reasons.append("oos_win_rate_poor")
    else:
        reasons.append("oos_win_rate_low_but_possible_with_rr_2_5")

    if max_drawdown_r <= -5:
        score -= 2
        reasons.append("oos_drawdown_poor")
    elif max_drawdown_r >= -3:
        score += 1
        reasons.append("oos_drawdown_acceptable_baseline")
    else:
        reasons.append("oos_drawdown_moderate")

    if total_result_r <= -3 and profit_factor < 0.75:
        classification = "OOS_FAIL"
        recommendation = "Fail OOS baseline as-is. Do not continue without redesign."
    elif total_result_r <= 0 or profit_factor < 1.0:
        classification = "OOS_WEAK"
        recommendation = "Weak OOS evidence. Do not prioritize."
    elif (
        total_result_r > 0
        and profit_factor >= 1.50
        and trades >= 3
        and max_drawdown_r >= -5
    ):
        classification = "OOS_RESEARCH_CONTINUATION"
        recommendation = "Continue to OOS decision gate. No execution approval."
    elif total_result_r > 0 and profit_factor >= 1.0:
        classification = "OOS_WATCHLIST"
        recommendation = "Keep under OOS watchlist. No execution approval."
    else:
        classification = "OOS_WEAK"
        recommendation = "OOS evidence is inconclusive. Keep blocked."

    return classification, recommendation, score, ";".join(reasons)


def build_empty_trades_df() -> pd.DataFrame:
    return pd.DataFrame(
        columns=[
            "candidate_id",
            "signal_index",
            "observed_at",
            "symbol",
            "timeframe",
            "direction",
            "router_decision",
            "entry_price",
            "stop_price",
            "target_price",
            "risk",
            "reward",
            "risk_reward",
            "valid_long_structure",
            "resolution_status",
            "result_r",
            "mfe_r",
            "mae_r",
            "bars_to_resolution",
            "resolution_timestamp",
            "historical_status",
            "approval_status",
            "long_strategy_approved",
            "long_entries_approved",
            "execution_allowed",
        ]
    )


def run_oos_backtest(
    oos_df: pd.DataFrame,
    eligible_candidate_ids: list[str],
) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []

    for candidate_id in eligible_candidate_ids:
        indexes = candidate_signal_indexes(df=oos_df, candidate_id=candidate_id)

        for signal_index in indexes:
            trade = resolve_long_trade(
                df=oos_df,
                signal_index=signal_index,
                candidate_id=candidate_id,
            )
            trade["oos_status"] = OOS_STATUS
            trade["historical_status"] = OOS_STATUS
            trade["long_strategy_approved"] = False
            trade["long_entries_approved"] = False
            trade["execution_allowed"] = False
            rows.append(trade)

    if not rows:
        return build_empty_trades_df()

    return pd.DataFrame(rows)


def build_oos_metrics(
    trades_df: pd.DataFrame,
    eligible_candidate_ids: list[str],
) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []

    for candidate_id in eligible_candidate_ids:
        group = trades_df[trades_df["candidate_id"].astype(str).eq(candidate_id)].copy()

        result_r = pd.to_numeric(
            group.get("result_r", pd.Series(dtype=float)),
            errors="coerce",
        ).fillna(0.0)

        trades = int(len(group))
        wins = int((result_r > 0).sum())
        losses = int((result_r < 0).sum())
        open_trades = (
            int(group["resolution_status"].astype(str).eq("OPEN_TIMEOUT").sum())
            if trades > 0 and "resolution_status" in group.columns
            else 0
        )

        gross_win_r = float(result_r[result_r > 0].sum()) if trades > 0 else 0.0
        gross_loss_r = float(result_r[result_r < 0].sum()) if trades > 0 else 0.0

        if gross_loss_r < 0:
            profit_factor = gross_win_r / abs(gross_loss_r)
        elif gross_win_r > 0:
            profit_factor = 999.0
        else:
            profit_factor = 0.0

        temp_metrics_df = build_candidate_metrics(group) if trades > 0 else pd.DataFrame()
        max_drawdown_r = (
            safe_float(temp_metrics_df.iloc[0].get("max_drawdown_r", 0.0))
            if not temp_metrics_df.empty
            else 0.0
        )

        base_row = pd.Series(
            {
                "trades": trades,
                "win_rate": wins / trades if trades > 0 else 0.0,
                "profit_factor": profit_factor,
                "total_result_r": float(result_r.sum()) if trades > 0 else 0.0,
                "average_result_r": float(result_r.mean()) if trades > 0 else 0.0,
                "max_drawdown_r": max_drawdown_r,
            }
        )

        classification, recommendation, score, reasons = classify_oos_candidate(base_row)

        rows.append(
            {
                "candidate_id": candidate_id,
                "trades": trades,
                "wins": wins,
                "losses": losses,
                "open_trades": open_trades,
                "win_rate": wins / trades if trades > 0 else 0.0,
                "gross_win_r": gross_win_r,
                "gross_loss_r": gross_loss_r,
                "profit_factor": profit_factor,
                "total_result_r": float(result_r.sum()) if trades > 0 else 0.0,
                "average_result_r": float(result_r.mean()) if trades > 0 else 0.0,
                "max_drawdown_r": max_drawdown_r,
                "oos_classification": classification,
                "oos_score": score,
                "oos_reasons": reasons,
                "oos_recommendation": recommendation,
                "candidate_approved": False,
                "long_strategy_approved": False,
                "long_entries_approved": False,
                "paper_trade_execution_allowed": False,
                "real_capital_allowed": False,
                "live_alerts_allowed": False,
                "exchange_execution_allowed": False,
                "automation_allowed": False,
                "execution_allowed": False,
                "oos_status": OOS_STATUS,
            }
        )

    metrics_df = pd.DataFrame(rows)

    classification_rank = {
        "OOS_RESEARCH_CONTINUATION": 1,
        "OOS_WATCHLIST": 2,
        "OOS_WEAK": 3,
        "OOS_NO_SIGNAL": 4,
        "OOS_FAIL": 5,
    }

    if not metrics_df.empty:
        metrics_df["oos_classification_rank"] = metrics_df["oos_classification"].map(
            classification_rank
        )
        metrics_df = metrics_df.sort_values(
            by=[
                "oos_classification_rank",
                "oos_score",
                "total_result_r",
                "profit_factor",
            ],
            ascending=[True, False, False, False],
        ).reset_index(drop=True)

    return metrics_df


def no_approvals_enabled(metrics_df: pd.DataFrame, trades_df: pd.DataFrame) -> bool:
    approval_columns = [
        "long_strategy_approved",
        "long_entries_approved",
        "execution_allowed",
    ]

    if not trades_df.empty:
        for column in approval_columns:
            if column not in trades_df.columns:
                return False
            if trades_df[column].astype(bool).any():
                return False

    metrics_approval_columns = [
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

    if metrics_df.empty:
        return False

    for column in metrics_approval_columns:
        if column not in metrics_df.columns:
            return False
        if metrics_df[column].astype(bool).any():
            return False

    return True


def validate_long_oos_baseline_validation() -> dict[str, pd.DataFrame]:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    checks: list[dict[str, Any]] = []

    phase_anchors = {
        "phase_8_1_contract_doc_exists": PHASE_8_1_CONTRACT_DOC_PATH,
        "phase_8_2_discovery_doc_exists": PHASE_8_2_DISCOVERY_DOC_PATH,
        "phase_8_3_harness_doc_exists": PHASE_8_3_HARNESS_DOC_PATH,
        "phase_8_4_historical_doc_exists": PHASE_8_4_HISTORICAL_DOC_PATH,
        "phase_8_5_comparison_doc_exists": PHASE_8_5_COMPARISON_DOC_PATH,
        "phase_8_6_oos_doc_exists": PHASE_8_6_OOS_DOC_PATH,
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

    phase_8_5_result = validate_long_candidate_historical_comparison()
    source_comparison_df = phase_8_5_result["comparison"]
    source_summary_df = phase_8_5_result["summary"]

    phase_8_5_validation_passed = (
        not source_summary_df.empty
        and bool(source_summary_df.iloc[0].get("validation_passed", False))
    )

    eligible_df = source_comparison_df[
        source_comparison_df["historical_classification"].astype(str).isin(
            ELIGIBLE_CLASSIFICATIONS
        )
    ].copy()

    excluded_df = source_comparison_df[
        ~source_comparison_df["historical_classification"].astype(str).isin(
            ELIGIBLE_CLASSIFICATIONS
        )
    ].copy()

    eligible_candidate_ids = sorted(eligible_df["candidate_id"].astype(str).tolist())
    excluded_candidate_ids = sorted(excluded_df["candidate_id"].astype(str).tolist())

    historical_data_path = find_historical_data_path()
    raw_df = pd.DataFrame()
    normalized_df = pd.DataFrame()
    indicator_df = pd.DataFrame()
    oos_df = pd.DataFrame()
    oos_trades_df = pd.DataFrame()
    oos_metrics_df = pd.DataFrame()
    missing_columns: list[str] = []

    if historical_data_path is not None:
        raw_df = pd.read_csv(historical_data_path)
        normalized_df, missing_columns = normalize_ohlc_df(raw_df)

        if not normalized_df.empty:
            indicator_df = add_indicators(normalized_df)
            split_index = int(len(indicator_df) * OOS_START_FRACTION)
            oos_df = indicator_df.iloc[split_index:].reset_index(drop=True).copy()
            oos_trades_df = run_oos_backtest(
                oos_df=oos_df,
                eligible_candidate_ids=eligible_candidate_ids,
            )
            oos_metrics_df = build_oos_metrics(
                trades_df=oos_trades_df,
                eligible_candidate_ids=eligible_candidate_ids,
            )

    checks.append(
        build_check(
            check_group="phase_dependency",
            check_name="phase_8_5_validation_passed",
            passed=phase_8_5_validation_passed,
            severity="INFO" if phase_8_5_validation_passed else "ERROR",
            details=(
                str(source_summary_df.iloc[0].get("validation_decision", ""))
                if not source_summary_df.empty
                else "Missing Phase 8.5 summary."
            ),
        )
    )

    checks.append(
        build_check(
            check_group="candidate_scope",
            check_name="eligible_candidates_match_expected",
            passed=set(eligible_candidate_ids) == EXPECTED_ELIGIBLE_CANDIDATES,
            severity=(
                "INFO"
                if set(eligible_candidate_ids) == EXPECTED_ELIGIBLE_CANDIDATES
                else "ERROR"
            ),
            details="eligible=" + ",".join(eligible_candidate_ids),
        )
    )

    checks.append(
        build_check(
            check_group="candidate_scope",
            check_name="rejected_candidates_excluded",
            passed=EXPECTED_EXCLUDED_CANDIDATES.issubset(set(excluded_candidate_ids)),
            severity=(
                "INFO"
                if EXPECTED_EXCLUDED_CANDIDATES.issubset(set(excluded_candidate_ids))
                else "ERROR"
            ),
            details="excluded=" + ",".join(excluded_candidate_ids),
        )
    )

    checks.append(
        build_check(
            check_group="historical_data",
            check_name="historical_ohlc_file_exists",
            passed=historical_data_path is not None,
            severity="INFO" if historical_data_path is not None else "ERROR",
            details=str(historical_data_path) if historical_data_path else "No supported OHLC file found.",
        )
    )

    checks.append(
        build_check(
            check_group="historical_data",
            check_name="required_ohlc_columns_present",
            passed=len(missing_columns) == 0,
            severity="INFO" if len(missing_columns) == 0 else "ERROR",
            details="missing_columns=" + ",".join(missing_columns),
        )
    )

    checks.append(
        build_check(
            check_group="oos_split",
            check_name="oos_window_rows_present",
            passed=len(oos_df) > 100,
            severity="INFO" if len(oos_df) > 100 else "ERROR",
            details=f"oos_rows={len(oos_df)}",
        )
    )

    checks.append(
        build_check(
            check_group="oos_validation",
            check_name="oos_metrics_created_for_eligible_candidates",
            passed=len(oos_metrics_df) == len(eligible_candidate_ids),
            severity=(
                "INFO"
                if len(oos_metrics_df) == len(eligible_candidate_ids)
                else "ERROR"
            ),
            details=f"oos_metrics_rows={len(oos_metrics_df)}",
        )
    )

    oos_classifications = (
        set(oos_metrics_df["oos_classification"].astype(str).tolist())
        if not oos_metrics_df.empty
        else set()
    )

    checks.append(
        build_check(
            check_group="oos_validation",
            check_name="oos_classifications_are_allowed",
            passed=oos_classifications.issubset(ALLOWED_OOS_CLASSIFICATIONS),
            severity=(
                "INFO"
                if oos_classifications.issubset(ALLOWED_OOS_CLASSIFICATIONS)
                else "ERROR"
            ),
            details="classifications=" + ",".join(sorted(oos_classifications)),
        )
    )

    checks.append(
        build_check(
            check_group="oos_validation",
            check_name="oos_trade_count_recorded",
            passed=True,
            severity="INFO" if len(oos_trades_df) > 0 else "WARNING",
            details=f"oos_trade_count={len(oos_trades_df)}",
        )
    )

    if not oos_trades_df.empty:
        all_trades_long = oos_trades_df["direction"].astype(str).str.upper().eq("LONG").all()
        all_watch_only = (
            oos_trades_df["router_decision"].astype(str).str.upper().eq("WATCH_ONLY").all()
        )
        all_valid_long_structure = oos_trades_df["valid_long_structure"].astype(bool).all()
    else:
        all_trades_long = True
        all_watch_only = True
        all_valid_long_structure = True

    checks.append(
        build_check(
            check_group="directional_contract",
            check_name="all_oos_trades_direction_long",
            passed=all_trades_long,
            severity="INFO" if all_trades_long else "ERROR",
            details=f"all_trades_long={all_trades_long}",
        )
    )

    checks.append(
        build_check(
            check_group="directional_contract",
            check_name="all_oos_trades_watch_only",
            passed=all_watch_only,
            severity="INFO" if all_watch_only else "ERROR",
            details=f"all_watch_only={all_watch_only}",
        )
    )

    checks.append(
        build_check(
            check_group="price_structure",
            check_name="all_oos_long_price_structures_valid",
            passed=all_valid_long_structure,
            severity="INFO" if all_valid_long_structure else "ERROR",
            details=f"all_valid_long_structure={all_valid_long_structure}",
        )
    )

    checks.append(
        build_check(
            check_group="approval_control",
            check_name="no_candidate_approved",
            passed=no_approvals_enabled(
                metrics_df=oos_metrics_df,
                trades_df=oos_trades_df,
            ),
            severity=(
                "INFO"
                if no_approvals_enabled(metrics_df=oos_metrics_df, trades_df=oos_trades_df)
                else "ERROR"
            ),
            details="All OOS candidate approval flags remain False.",
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
            check_name="phase_8_7_recommended_next",
            passed=True,
            severity="INFO",
            details="Recommended next step: Phase 8.7 LONG OOS Decision Gate V1.",
        )
    )

    checks.append(
        build_check(
            check_group="scope_control",
            check_name="long_side_remains_unestablished",
            passed=True,
            severity="WARNING",
            details="Phase 8.6 validates OOS baseline only; LONG side is not established.",
        )
    )

    checks.append(
        build_check(
            check_group="scope_control",
            check_name="real_entries_remain_blocked",
            passed=True,
            severity="WARNING",
            details="Real entries remain blocked after Phase 8.6.",
        )
    )

    checks_df = pd.DataFrame(checks)

    blocker_count = int(checks_df["blocker"].astype(bool).sum())
    error_count = int(checks_df["severity"].eq("ERROR").sum())
    warning_count = int(checks_df["severity"].eq("WARNING").sum())

    validation_passed = blocker_count == 0 and error_count == 0

    classification_counts = (
        oos_metrics_df["oos_classification"].value_counts().to_dict()
        if not oos_metrics_df.empty
        else {}
    )

    result_r = pd.to_numeric(
        oos_trades_df.get("result_r", pd.Series(dtype=float)),
        errors="coerce",
    ).fillna(0.0)

    best_candidate_id = (
        str(oos_metrics_df.iloc[0]["candidate_id"])
        if not oos_metrics_df.empty
        else ""
    )
    best_oos_classification = (
        str(oos_metrics_df.iloc[0]["oos_classification"])
        if not oos_metrics_df.empty
        else ""
    )
    best_oos_total_result_r = (
        float(oos_metrics_df.iloc[0]["total_result_r"])
        if not oos_metrics_df.empty
        else 0.0
    )
    best_oos_profit_factor = (
        float(oos_metrics_df.iloc[0]["profit_factor"])
        if not oos_metrics_df.empty
        else 0.0
    )

    summary_df = pd.DataFrame(
        [
            {
                "phase": "8.6",
                "oos_baseline_validation_defined": True,
                "phase_8_5_validation_passed": phase_8_5_validation_passed,
                "historical_data_path": str(historical_data_path) if historical_data_path else "",
                "raw_rows": int(len(raw_df)),
                "normalized_rows": int(len(normalized_df)),
                "indicator_rows": int(len(indicator_df)),
                "oos_start_fraction": float(OOS_START_FRACTION),
                "oos_rows": int(len(oos_df)),
                "eligible_candidate_count": int(len(eligible_candidate_ids)),
                "excluded_candidate_count": int(len(excluded_candidate_ids)),
                "oos_trade_count": int(len(oos_trades_df)),
                "oos_metrics_rows": int(len(oos_metrics_df)),
                "oos_target_hits": (
                    int(oos_trades_df["resolution_status"].eq("TARGET_HIT").sum())
                    if not oos_trades_df.empty
                    else 0
                ),
                "oos_stop_hits": (
                    int(oos_trades_df["resolution_status"].eq("STOP_HIT").sum())
                    if not oos_trades_df.empty
                    else 0
                ),
                "oos_open_timeouts": (
                    int(oos_trades_df["resolution_status"].eq("OPEN_TIMEOUT").sum())
                    if not oos_trades_df.empty
                    else 0
                ),
                "oos_total_result_r": float(result_r.sum()) if len(result_r) > 0 else 0.0,
                "oos_average_result_r": float(result_r.mean()) if len(result_r) > 0 else 0.0,
                "oos_research_continuation_count": int(
                    classification_counts.get("OOS_RESEARCH_CONTINUATION", 0)
                ),
                "oos_watchlist_count": int(classification_counts.get("OOS_WATCHLIST", 0)),
                "oos_weak_count": int(classification_counts.get("OOS_WEAK", 0)),
                "oos_fail_count": int(classification_counts.get("OOS_FAIL", 0)),
                "oos_no_signal_count": int(classification_counts.get("OOS_NO_SIGNAL", 0)),
                "best_candidate_id": best_candidate_id,
                "best_oos_classification": best_oos_classification,
                "best_oos_total_result_r": best_oos_total_result_r,
                "best_oos_profit_factor": best_oos_profit_factor,
                "oos_validation_executed": True,
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
                "recommended_next_phase": "PHASE_8_7_LONG_OOS_DECISION_GATE_V1",
                "estimated_total_project_progress_percent": 95,
                "total_checks": int(len(checks_df)),
                "warning_count": warning_count,
                "error_count": error_count,
                "blocker_count": blocker_count,
                "validation_passed": validation_passed,
                "validation_decision": (
                    "PHASE_8_6_LONG_OOS_BASELINE_VALIDATION_VALIDATED"
                    if validation_passed
                    else "PHASE_8_6_LONG_OOS_BASELINE_VALIDATION_FAILED"
                ),
            }
        ]
    )

    source_comparison_df.to_csv(
        REPORTS_DIR / "phase_8_5_source_comparison_v1.csv",
        index=False,
    )
    eligible_df.to_csv(
        REPORTS_DIR / "long_oos_eligible_candidates_v1.csv",
        index=False,
    )
    excluded_df.to_csv(
        REPORTS_DIR / "long_oos_excluded_candidates_v1.csv",
        index=False,
    )
    oos_trades_df.to_csv(
        REPORTS_DIR / "long_oos_baseline_trades_v1.csv",
        index=False,
    )
    oos_metrics_df.to_csv(
        REPORTS_DIR / "long_oos_baseline_metrics_v1.csv",
        index=False,
    )
    checks_df.to_csv(
        REPORTS_DIR / "long_oos_baseline_validation_checks_v1.csv",
        index=False,
    )
    summary_df.to_csv(
        REPORTS_DIR / "long_oos_baseline_validation_summary_v1.csv",
        index=False,
    )

    return {
        "summary": summary_df,
        "source_comparison": source_comparison_df,
        "eligible_candidates": eligible_df,
        "excluded_candidates": excluded_df,
        "oos_trades": oos_trades_df,
        "oos_metrics": oos_metrics_df,
        "checks": checks_df,
    }