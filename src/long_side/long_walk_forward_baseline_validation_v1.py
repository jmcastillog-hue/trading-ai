from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from src.long_side.long_historical_baseline_backtest_v1 import (
    add_indicators,
    candidate_signal_indexes,
    find_historical_data_path,
    normalize_ohlc_df,
    resolve_long_trade,
)
from src.long_side.long_oos_decision_gate_v1 import (
    validate_long_oos_decision_gate,
)


REPORTS_DIR = Path("reports/phase_8_8_long_walk_forward_baseline_validation_v1")

PHASE_8_1_CONTRACT_DOC_PATH = Path("docs/PHASE_8_LONG_SIDE_VALIDATION_CONTRACT.md")
PHASE_8_2_DISCOVERY_DOC_PATH = Path("docs/PHASE_8_LONG_CANDIDATE_DISCOVERY_BASELINE.md")
PHASE_8_3_HARNESS_DOC_PATH = Path("docs/PHASE_8_LONG_BASELINE_STRUCTURAL_BACKTEST_HARNESS.md")
PHASE_8_4_HISTORICAL_DOC_PATH = Path("docs/PHASE_8_LONG_HISTORICAL_BASELINE_BACKTEST.md")
PHASE_8_5_COMPARISON_DOC_PATH = Path("docs/PHASE_8_LONG_CANDIDATE_HISTORICAL_COMPARISON.md")
PHASE_8_6_OOS_DOC_PATH = Path("docs/PHASE_8_LONG_OOS_BASELINE_VALIDATION.md")
PHASE_8_7_DECISION_DOC_PATH = Path("docs/PHASE_8_LONG_OOS_DECISION_GATE.md")
PHASE_8_8_WF_DOC_PATH = Path("docs/PHASE_8_LONG_WALK_FORWARD_BASELINE_VALIDATION.md")

PRIMARY_RESEARCH_CANDIDATE = "LONG_BASE_FAILED_BREAKDOWN_V1"
SECONDARY_REFERENCE_CANDIDATE = "LONG_BASE_LIQUIDITY_SWEEP_V1"

BLOCKED_CANDIDATES = {
    "LONG_BASE_FIB_PULLBACK_V1",
    "LONG_BASE_MTF_BULLISH_CONTINUATION_V1",
}

WF_STATUS = "WALK_FORWARD_BASELINE_ONLY"

TRAIN_WINDOW_ROWS = 300
TEST_WINDOW_ROWS = 160
STEP_ROWS = 160

ALLOWED_WINDOW_CLASSIFICATIONS = {
    "WF_PASS",
    "WF_WATCH",
    "WF_WEAK",
    "WF_FAIL",
    "WF_NO_SIGNAL",
}

ALLOWED_CANDIDATE_CLASSIFICATIONS = {
    "WF_RESEARCH_CONTINUATION",
    "WF_WATCHLIST",
    "WF_WEAK",
    "WF_FAIL",
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


def build_walk_forward_windows(total_rows: int) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    window_number = 1
    start = 0

    while start + TRAIN_WINDOW_ROWS + TEST_WINDOW_ROWS <= total_rows:
        train_start = start
        train_end = start + TRAIN_WINDOW_ROWS
        test_start = train_end
        test_end = train_end + TEST_WINDOW_ROWS

        rows.append(
            {
                "window_id": f"WF_{window_number:03d}",
                "train_start_index": train_start,
                "train_end_index": train_end - 1,
                "test_start_index": test_start,
                "test_end_index": test_end - 1,
                "train_rows": TRAIN_WINDOW_ROWS,
                "test_rows": TEST_WINDOW_ROWS,
                "wf_status": WF_STATUS,
            }
        )

        window_number += 1
        start += STEP_ROWS

    return pd.DataFrame(rows)


def build_empty_trades_df() -> pd.DataFrame:
    return pd.DataFrame(
        columns=[
            "window_id",
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
            "wf_status",
            "approval_status",
            "long_strategy_approved",
            "long_entries_approved",
            "execution_allowed",
        ]
    )


def run_candidate_on_window(
    test_df: pd.DataFrame,
    window_id: str,
    candidate_id: str,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    signal_indexes = candidate_signal_indexes(df=test_df, candidate_id=candidate_id)

    for signal_index in signal_indexes:
        trade = resolve_long_trade(
            df=test_df,
            signal_index=signal_index,
            candidate_id=candidate_id,
        )

        trade["window_id"] = window_id
        trade["wf_status"] = WF_STATUS
        trade["historical_status"] = WF_STATUS
        trade["long_strategy_approved"] = False
        trade["long_entries_approved"] = False
        trade["execution_allowed"] = False

        rows.append(trade)

    return rows


def run_walk_forward_backtest(
    indicator_df: pd.DataFrame,
    windows_df: pd.DataFrame,
    candidate_ids: list[str],
) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []

    for _, window in windows_df.iterrows():
        window_id = str(window["window_id"])
        test_start = safe_int(window["test_start_index"])
        test_end = safe_int(window["test_end_index"])

        test_df = indicator_df.iloc[test_start : test_end + 1].reset_index(drop=True).copy()

        for candidate_id in candidate_ids:
            rows.extend(
                run_candidate_on_window(
                    test_df=test_df,
                    window_id=window_id,
                    candidate_id=candidate_id,
                )
            )

    if not rows:
        return build_empty_trades_df()

    return pd.DataFrame(rows)


def classify_window_metrics(row: pd.Series) -> tuple[str, str]:
    trades = safe_int(row.get("trades", 0))
    profit_factor = safe_float(row.get("profit_factor", 0.0))
    total_result_r = safe_float(row.get("total_result_r", 0.0))
    max_drawdown_r = safe_float(row.get("max_drawdown_r", 0.0))

    if trades == 0:
        return "WF_NO_SIGNAL", "No trades in this validation window."

    if total_result_r > 0 and profit_factor >= 1.5 and max_drawdown_r >= -3:
        return "WF_PASS", "Positive window with acceptable baseline drawdown."

    if total_result_r > 0 and profit_factor >= 1.0:
        return "WF_WATCH", "Positive but not strong enough to pass."

    if total_result_r <= -3 or profit_factor < 0.75:
        return "WF_FAIL", "Negative or poor profit factor window."

    return "WF_WEAK", "Weak or inconclusive walk-forward window."


def build_window_metrics(
    trades_df: pd.DataFrame,
    windows_df: pd.DataFrame,
    candidate_ids: list[str],
) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []

    for _, window in windows_df.iterrows():
        window_id = str(window["window_id"])

        for candidate_id in candidate_ids:
            group = trades_df[
                trades_df["window_id"].astype(str).eq(window_id)
                & trades_df["candidate_id"].astype(str).eq(candidate_id)
            ].copy()

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

            base_row = pd.Series(
                {
                    "trades": trades,
                    "profit_factor": profit_factor,
                    "total_result_r": float(result_r.sum()) if trades > 0 else 0.0,
                    "max_drawdown_r": (
                        calculate_max_drawdown_r(result_r.tolist())
                        if trades > 0
                        else 0.0
                    ),
                }
            )

            window_classification, window_note = classify_window_metrics(base_row)

            rows.append(
                {
                    "window_id": window_id,
                    "candidate_id": candidate_id,
                    "train_start_index": safe_int(window["train_start_index"]),
                    "train_end_index": safe_int(window["train_end_index"]),
                    "test_start_index": safe_int(window["test_start_index"]),
                    "test_end_index": safe_int(window["test_end_index"]),
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
                    "max_drawdown_r": (
                        calculate_max_drawdown_r(result_r.tolist())
                        if trades > 0
                        else 0.0
                    ),
                    "window_classification": window_classification,
                    "window_note": window_note,
                    "candidate_approved": False,
                    "long_strategy_approved": False,
                    "long_entries_approved": False,
                    "execution_allowed": False,
                    "wf_status": WF_STATUS,
                }
            )

    return pd.DataFrame(rows)


def classify_candidate_aggregate(row: pd.Series) -> tuple[str, str]:
    total_trades = safe_int(row.get("total_trades", 0))
    total_result_r = safe_float(row.get("total_result_r", 0.0))
    aggregate_profit_factor = safe_float(row.get("aggregate_profit_factor", 0.0))
    pass_windows = safe_int(row.get("pass_windows", 0))
    watch_windows = safe_int(row.get("watch_windows", 0))
    fail_windows = safe_int(row.get("fail_windows", 0))
    no_signal_windows = safe_int(row.get("no_signal_windows", 0))
    total_windows = safe_int(row.get("total_windows", 0))

    positive_windows = pass_windows + watch_windows

    if total_trades == 0:
        return "WF_FAIL", "No walk-forward trades were produced."

    if fail_windows > positive_windows:
        return "WF_FAIL", "More failing windows than positive windows."

    if (
        total_result_r > 0
        and aggregate_profit_factor >= 1.5
        and positive_windows >= max(1, total_windows // 2)
        and no_signal_windows <= total_windows // 2
    ):
        return "WF_RESEARCH_CONTINUATION", "Candidate survives baseline walk-forward validation."

    if total_result_r > 0 and aggregate_profit_factor >= 1.0:
        return "WF_WATCHLIST", "Candidate remains positive but not strong enough."

    if total_result_r <= 0 or aggregate_profit_factor < 1.0:
        return "WF_WEAK", "Candidate shows weak aggregate walk-forward evidence."

    return "WF_WEAK", "Candidate remains inconclusive after walk-forward baseline."


def build_candidate_aggregate_metrics(window_metrics_df: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []

    for candidate_id, group in window_metrics_df.groupby("candidate_id", sort=True):
        total_trades = int(pd.to_numeric(group["trades"], errors="coerce").sum())
        total_wins = int(pd.to_numeric(group["wins"], errors="coerce").sum())
        total_losses = int(pd.to_numeric(group["losses"], errors="coerce").sum())
        total_open = int(pd.to_numeric(group["open_trades"], errors="coerce").sum())

        gross_win_r = float(pd.to_numeric(group["gross_win_r"], errors="coerce").sum())
        gross_loss_r = float(pd.to_numeric(group["gross_loss_r"], errors="coerce").sum())

        if gross_loss_r < 0:
            aggregate_profit_factor = gross_win_r / abs(gross_loss_r)
        elif gross_win_r > 0:
            aggregate_profit_factor = 999.0
        else:
            aggregate_profit_factor = 0.0

        total_result_r = float(pd.to_numeric(group["total_result_r"], errors="coerce").sum())

        window_classes = group["window_classification"].astype(str)

        base_row = pd.Series(
            {
                "total_windows": int(len(group)),
                "total_trades": total_trades,
                "total_result_r": total_result_r,
                "aggregate_profit_factor": aggregate_profit_factor,
                "pass_windows": int(window_classes.eq("WF_PASS").sum()),
                "watch_windows": int(window_classes.eq("WF_WATCH").sum()),
                "weak_windows": int(window_classes.eq("WF_WEAK").sum()),
                "fail_windows": int(window_classes.eq("WF_FAIL").sum()),
                "no_signal_windows": int(window_classes.eq("WF_NO_SIGNAL").sum()),
            }
        )

        candidate_classification, candidate_note = classify_candidate_aggregate(base_row)

        rows.append(
            {
                "candidate_id": candidate_id,
                "total_windows": int(len(group)),
                "total_trades": total_trades,
                "total_wins": total_wins,
                "total_losses": total_losses,
                "total_open_trades": total_open,
                "aggregate_win_rate": total_wins / total_trades if total_trades > 0 else 0.0,
                "gross_win_r": gross_win_r,
                "gross_loss_r": gross_loss_r,
                "aggregate_profit_factor": aggregate_profit_factor,
                "total_result_r": total_result_r,
                "average_result_r": total_result_r / total_trades if total_trades > 0 else 0.0,
                "pass_windows": int(window_classes.eq("WF_PASS").sum()),
                "watch_windows": int(window_classes.eq("WF_WATCH").sum()),
                "weak_windows": int(window_classes.eq("WF_WEAK").sum()),
                "fail_windows": int(window_classes.eq("WF_FAIL").sum()),
                "no_signal_windows": int(window_classes.eq("WF_NO_SIGNAL").sum()),
                "candidate_wf_classification": candidate_classification,
                "candidate_wf_note": candidate_note,
                "candidate_approved": False,
                "long_strategy_approved": False,
                "long_entries_approved": False,
                "paper_trade_execution_allowed": False,
                "real_capital_allowed": False,
                "live_alerts_allowed": False,
                "exchange_execution_allowed": False,
                "automation_allowed": False,
                "execution_allowed": False,
                "wf_status": WF_STATUS,
            }
        )

    classification_rank = {
        "WF_RESEARCH_CONTINUATION": 1,
        "WF_WATCHLIST": 2,
        "WF_WEAK": 3,
        "WF_FAIL": 4,
    }

    result_df = pd.DataFrame(rows)

    if not result_df.empty:
        result_df["candidate_wf_rank"] = result_df["candidate_wf_classification"].map(
            classification_rank
        )
        result_df = result_df.sort_values(
            by=[
                "candidate_wf_rank",
                "total_result_r",
                "aggregate_profit_factor",
            ],
            ascending=[True, False, False],
        ).reset_index(drop=True)

    return result_df


def no_approvals_enabled(candidate_metrics_df: pd.DataFrame, window_metrics_df: pd.DataFrame) -> bool:
    approval_columns = [
        "candidate_approved",
        "long_strategy_approved",
        "long_entries_approved",
        "execution_allowed",
    ]

    for df in [candidate_metrics_df, window_metrics_df]:
        if df.empty:
            return False

        for column in approval_columns:
            if column not in df.columns:
                return False

            if df[column].astype(bool).any():
                return False

    extended_columns = [
        "paper_trade_execution_allowed",
        "real_capital_allowed",
        "live_alerts_allowed",
        "exchange_execution_allowed",
        "automation_allowed",
    ]

    for column in extended_columns:
        if column not in candidate_metrics_df.columns:
            return False

        if candidate_metrics_df[column].astype(bool).any():
            return False

    return True


def validate_long_walk_forward_baseline_validation() -> dict[str, pd.DataFrame]:
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

    phase_8_7_result = validate_long_oos_decision_gate()

    source_summary_df = phase_8_7_result["summary"]
    source_decision_df = phase_8_7_result["decision_gate"]

    phase_8_7_validation_passed = (
        not source_summary_df.empty
        and bool(source_summary_df.iloc[0].get("validation_passed", False))
    )

    primary_df = source_decision_df[
        source_decision_df["gate_decision"].astype(str).eq("ADVANCE_TO_STRICT_VALIDATION")
    ].copy()

    secondary_df = source_decision_df[
        source_decision_df["gate_decision"].astype(str).eq("SECONDARY_WATCHLIST_ONLY")
    ].copy()

    blocked_df = source_decision_df[
        source_decision_df["research_role"].astype(str).eq("BLOCKED")
    ].copy()

    candidate_ids = []

    if not primary_df.empty:
        candidate_ids.extend(primary_df["candidate_id"].astype(str).tolist())

    if not secondary_df.empty:
        candidate_ids.extend(secondary_df["candidate_id"].astype(str).tolist())

    candidate_ids = sorted(set(candidate_ids))

    historical_data_path = find_historical_data_path()
    raw_df = pd.DataFrame()
    normalized_df = pd.DataFrame()
    indicator_df = pd.DataFrame()
    windows_df = pd.DataFrame()
    wf_trades_df = build_empty_trades_df()
    window_metrics_df = pd.DataFrame()
    candidate_metrics_df = pd.DataFrame()
    missing_columns: list[str] = []

    if historical_data_path is not None:
        raw_df = pd.read_csv(historical_data_path)
        normalized_df, missing_columns = normalize_ohlc_df(raw_df)

        if not normalized_df.empty:
            indicator_df = add_indicators(normalized_df)
            windows_df = build_walk_forward_windows(total_rows=len(indicator_df))
            wf_trades_df = run_walk_forward_backtest(
                indicator_df=indicator_df,
                windows_df=windows_df,
                candidate_ids=candidate_ids,
            )
            window_metrics_df = build_window_metrics(
                trades_df=wf_trades_df,
                windows_df=windows_df,
                candidate_ids=candidate_ids,
            )
            candidate_metrics_df = build_candidate_aggregate_metrics(window_metrics_df)

    checks.append(
        build_check(
            check_group="phase_dependency",
            check_name="phase_8_7_validation_passed",
            passed=phase_8_7_validation_passed,
            severity="INFO" if phase_8_7_validation_passed else "ERROR",
            details=(
                str(source_summary_df.iloc[0].get("validation_decision", ""))
                if not source_summary_df.empty
                else "Missing Phase 8.7 summary."
            ),
        )
    )

    checks.append(
        build_check(
            check_group="candidate_scope",
            check_name="primary_candidate_selected",
            passed=(
                len(primary_df) == 1
                and str(primary_df.iloc[0]["candidate_id"]) == PRIMARY_RESEARCH_CANDIDATE
            ),
            severity=(
                "INFO"
                if (
                    len(primary_df) == 1
                    and str(primary_df.iloc[0]["candidate_id"]) == PRIMARY_RESEARCH_CANDIDATE
                )
                else "ERROR"
            ),
            details=(
                "primary="
                + ",".join(primary_df["candidate_id"].astype(str).tolist())
            ),
        )
    )

    checks.append(
        build_check(
            check_group="candidate_scope",
            check_name="secondary_reference_selected",
            passed=(
                len(secondary_df) == 1
                and str(secondary_df.iloc[0]["candidate_id"]) == SECONDARY_REFERENCE_CANDIDATE
            ),
            severity=(
                "INFO"
                if (
                    len(secondary_df) == 1
                    and str(secondary_df.iloc[0]["candidate_id"]) == SECONDARY_REFERENCE_CANDIDATE
                )
                else "ERROR"
            ),
            details=(
                "secondary="
                + ",".join(secondary_df["candidate_id"].astype(str).tolist())
            ),
        )
    )

    blocked_ids = set(blocked_df["candidate_id"].astype(str).tolist())

    checks.append(
        build_check(
            check_group="candidate_scope",
            check_name="blocked_candidates_excluded_from_wf",
            passed=BLOCKED_CANDIDATES.issubset(blocked_ids)
            and BLOCKED_CANDIDATES.isdisjoint(set(candidate_ids)),
            severity=(
                "INFO"
                if BLOCKED_CANDIDATES.issubset(blocked_ids)
                and BLOCKED_CANDIDATES.isdisjoint(set(candidate_ids))
                else "ERROR"
            ),
            details=(
                "blocked="
                + ",".join(sorted(blocked_ids))
                + ";wf_candidates="
                + ",".join(candidate_ids)
            ),
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
            check_group="walk_forward",
            check_name="walk_forward_windows_created",
            passed=len(windows_df) >= 3,
            severity="INFO" if len(windows_df) >= 3 else "ERROR",
            details=f"window_count={len(windows_df)}",
        )
    )

    checks.append(
        build_check(
            check_group="walk_forward",
            check_name="window_metrics_created",
            passed=len(window_metrics_df) == len(windows_df) * len(candidate_ids)
            and len(window_metrics_df) > 0,
            severity=(
                "INFO"
                if len(window_metrics_df) == len(windows_df) * len(candidate_ids)
                and len(window_metrics_df) > 0
                else "ERROR"
            ),
            details=f"window_metrics_rows={len(window_metrics_df)}",
        )
    )

    checks.append(
        build_check(
            check_group="walk_forward",
            check_name="candidate_aggregate_metrics_created",
            passed=len(candidate_metrics_df) == len(candidate_ids) and len(candidate_metrics_df) > 0,
            severity=(
                "INFO"
                if len(candidate_metrics_df) == len(candidate_ids)
                and len(candidate_metrics_df) > 0
                else "ERROR"
            ),
            details=f"candidate_metrics_rows={len(candidate_metrics_df)}",
        )
    )

    window_classes = (
        set(window_metrics_df["window_classification"].astype(str).tolist())
        if not window_metrics_df.empty
        else set()
    )

    checks.append(
        build_check(
            check_group="walk_forward",
            check_name="window_classifications_allowed",
            passed=window_classes.issubset(ALLOWED_WINDOW_CLASSIFICATIONS),
            severity=(
                "INFO"
                if window_classes.issubset(ALLOWED_WINDOW_CLASSIFICATIONS)
                else "ERROR"
            ),
            details="window_classes=" + ",".join(sorted(window_classes)),
        )
    )

    candidate_classes = (
        set(candidate_metrics_df["candidate_wf_classification"].astype(str).tolist())
        if not candidate_metrics_df.empty
        else set()
    )

    checks.append(
        build_check(
            check_group="walk_forward",
            check_name="candidate_classifications_allowed",
            passed=candidate_classes.issubset(ALLOWED_CANDIDATE_CLASSIFICATIONS),
            severity=(
                "INFO"
                if candidate_classes.issubset(ALLOWED_CANDIDATE_CLASSIFICATIONS)
                else "ERROR"
            ),
            details="candidate_classes=" + ",".join(sorted(candidate_classes)),
        )
    )

    if not wf_trades_df.empty:
        all_trades_long = wf_trades_df["direction"].astype(str).str.upper().eq("LONG").all()
        all_watch_only = (
            wf_trades_df["router_decision"].astype(str).str.upper().eq("WATCH_ONLY").all()
        )
        all_valid_long_structure = (
            wf_trades_df["valid_long_structure"].astype(bool).all()
            if "valid_long_structure" in wf_trades_df.columns
            else False
        )
    else:
        all_trades_long = True
        all_watch_only = True
        all_valid_long_structure = True

    checks.append(
        build_check(
            check_group="directional_contract",
            check_name="all_wf_trades_direction_long",
            passed=all_trades_long,
            severity="INFO" if all_trades_long else "ERROR",
            details=f"all_trades_long={all_trades_long}",
        )
    )

    checks.append(
        build_check(
            check_group="directional_contract",
            check_name="all_wf_trades_watch_only",
            passed=all_watch_only,
            severity="INFO" if all_watch_only else "ERROR",
            details=f"all_watch_only={all_watch_only}",
        )
    )

    checks.append(
        build_check(
            check_group="price_structure",
            check_name="all_wf_long_price_structures_valid",
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
                candidate_metrics_df=candidate_metrics_df,
                window_metrics_df=window_metrics_df,
            ),
            severity=(
                "INFO"
                if no_approvals_enabled(
                    candidate_metrics_df=candidate_metrics_df,
                    window_metrics_df=window_metrics_df,
                )
                else "ERROR"
            ),
            details="All walk-forward approval flags remain False.",
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
            check_name="parameter_optimization_not_executed",
            passed=True,
            severity="INFO",
            details="No parameter optimization is executed in Phase 8.8.",
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
            details="Cost-aware validation is deferred to Phase 8.9.",
        )
    )

    checks.append(
        build_check(
            check_group="phase_transition",
            check_name="phase_8_9_recommended_next",
            passed=True,
            severity="INFO",
            details="Recommended next step: Phase 8.9 LONG Cost-Aware Baseline Validation V1.",
        )
    )

    checks.append(
        build_check(
            check_group="scope_control",
            check_name="long_side_remains_unestablished",
            passed=True,
            severity="WARNING",
            details="Phase 8.8 validates baseline walk-forward only; LONG side is not established.",
        )
    )

    checks.append(
        build_check(
            check_group="scope_control",
            check_name="real_entries_remain_blocked",
            passed=True,
            severity="WARNING",
            details="Real entries remain blocked after Phase 8.8.",
        )
    )

    checks_df = pd.DataFrame(checks)

    blocker_count = int(checks_df["blocker"].astype(bool).sum())
    error_count = int(checks_df["severity"].eq("ERROR").sum())
    warning_count = int(checks_df["severity"].eq("WARNING").sum())

    validation_passed = blocker_count == 0 and error_count == 0

    primary_candidate_metrics = candidate_metrics_df[
        candidate_metrics_df["candidate_id"].astype(str).eq(PRIMARY_RESEARCH_CANDIDATE)
    ].copy()

    primary_wf_classification = (
        str(primary_candidate_metrics.iloc[0]["candidate_wf_classification"])
        if not primary_candidate_metrics.empty
        else ""
    )

    primary_total_result_r = (
        float(primary_candidate_metrics.iloc[0]["total_result_r"])
        if not primary_candidate_metrics.empty
        else 0.0
    )

    primary_profit_factor = (
        float(primary_candidate_metrics.iloc[0]["aggregate_profit_factor"])
        if not primary_candidate_metrics.empty
        else 0.0
    )

    total_result_r = (
        float(pd.to_numeric(candidate_metrics_df["total_result_r"], errors="coerce").sum())
        if not candidate_metrics_df.empty
        else 0.0
    )

    summary_df = pd.DataFrame(
        [
            {
                "phase": "8.8",
                "walk_forward_baseline_defined": True,
                "phase_8_7_validation_passed": phase_8_7_validation_passed,
                "historical_data_path": str(historical_data_path) if historical_data_path else "",
                "raw_rows": int(len(raw_df)),
                "normalized_rows": int(len(normalized_df)),
                "indicator_rows": int(len(indicator_df)),
                "train_window_rows": TRAIN_WINDOW_ROWS,
                "test_window_rows": TEST_WINDOW_ROWS,
                "step_rows": STEP_ROWS,
                "walk_forward_window_count": int(len(windows_df)),
                "wf_candidate_count": int(len(candidate_ids)),
                "wf_trade_count": int(len(wf_trades_df)),
                "window_metrics_rows": int(len(window_metrics_df)),
                "candidate_metrics_rows": int(len(candidate_metrics_df)),
                "primary_research_candidate_id": PRIMARY_RESEARCH_CANDIDATE,
                "secondary_reference_candidate_id": SECONDARY_REFERENCE_CANDIDATE,
                "primary_wf_classification": primary_wf_classification,
                "primary_total_result_r": primary_total_result_r,
                "primary_profit_factor": primary_profit_factor,
                "aggregate_total_result_r": total_result_r,
                "walk_forward_validation_executed": True,
                "parameter_optimization_executed": False,
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
                "recommended_next_phase": "PHASE_8_9_LONG_COST_AWARE_BASELINE_VALIDATION_V1",
                "estimated_total_project_progress_percent": 97,
                "total_checks": int(len(checks_df)),
                "warning_count": warning_count,
                "error_count": error_count,
                "blocker_count": blocker_count,
                "validation_passed": validation_passed,
                "validation_decision": (
                    "PHASE_8_8_LONG_WALK_FORWARD_BASELINE_VALIDATION_VALIDATED"
                    if validation_passed
                    else "PHASE_8_8_LONG_WALK_FORWARD_BASELINE_VALIDATION_FAILED"
                ),
            }
        ]
    )

    source_summary_df.to_csv(
        REPORTS_DIR / "phase_8_7_source_summary_v1.csv",
        index=False,
    )
    source_decision_df.to_csv(
        REPORTS_DIR / "phase_8_7_source_decision_gate_v1.csv",
        index=False,
    )
    windows_df.to_csv(
        REPORTS_DIR / "long_walk_forward_windows_v1.csv",
        index=False,
    )
    wf_trades_df.to_csv(
        REPORTS_DIR / "long_walk_forward_trades_v1.csv",
        index=False,
    )
    window_metrics_df.to_csv(
        REPORTS_DIR / "long_walk_forward_window_metrics_v1.csv",
        index=False,
    )
    candidate_metrics_df.to_csv(
        REPORTS_DIR / "long_walk_forward_candidate_metrics_v1.csv",
        index=False,
    )
    checks_df.to_csv(
        REPORTS_DIR / "long_walk_forward_baseline_checks_v1.csv",
        index=False,
    )
    summary_df.to_csv(
        REPORTS_DIR / "long_walk_forward_baseline_summary_v1.csv",
        index=False,
    )

    return {
        "summary": summary_df,
        "source_summary": source_summary_df,
        "source_decision_gate": source_decision_df,
        "windows": windows_df,
        "wf_trades": wf_trades_df,
        "window_metrics": window_metrics_df,
        "candidate_metrics": candidate_metrics_df,
        "checks": checks_df,
    }