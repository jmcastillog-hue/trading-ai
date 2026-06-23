from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pandas as pd


@dataclass(frozen=True)
class ForwardPerformanceMetricsConfig:
    min_resolved_observations: int = 100
    preferred_resolved_observations: int = 300
    sample_mode: bool = True
    dataset_quality_decision: str = "DATASET_NOT_READY"
    ready_for_phase_4_2_metrics: bool = False
    paper_trade_execution_allowed: bool = False
    real_capital_allowed: bool = False
    live_alerts_allowed: bool = False
    exchange_execution_allowed: bool = False
    automation_allowed: bool = False


REQUIRED_COLUMNS = [
    "signal_id",
    "observed_at",
    "symbol",
    "timeframe",
    "cost_profile",
    "context_name",
    "direction",
    "resolution_status",
    "result_r",
    "mfe_r",
    "mae_r",
    "bars_to_resolution",
]

NUMERIC_COLUMNS = [
    "result_r",
    "mfe_r",
    "mae_r",
    "bars_to_resolution",
]

OPEN_STATUSES = {
    "OPEN_UNRESOLVED",
    "OPEN_NO_FUTURE_DATA",
}


def safe_str(value: Any, default: str = "") -> str:
    if value is None:
        return default

    try:
        if pd.isna(value):
            return default
    except Exception:
        pass

    return str(value).strip()


def normalize_metrics_dataset(dataset_df: pd.DataFrame) -> pd.DataFrame:
    df = dataset_df.copy()

    for column in REQUIRED_COLUMNS:
        if column not in df.columns:
            df[column] = ""

    for column in NUMERIC_COLUMNS:
        df[column] = pd.to_numeric(df[column], errors="coerce").fillna(0.0)

    text_columns = [
        "signal_id",
        "observed_at",
        "symbol",
        "timeframe",
        "cost_profile",
        "context_name",
        "direction",
        "resolution_status",
    ]

    for column in text_columns:
        df[column] = df[column].map(lambda value: safe_str(value))

    df["symbol"] = df["symbol"].str.upper()
    df["timeframe"] = df["timeframe"].str.lower()
    df["cost_profile"] = df["cost_profile"].str.upper()
    df["context_name"] = df["context_name"].str.upper()
    df["direction"] = df["direction"].str.upper()
    df["resolution_status"] = df["resolution_status"].str.upper()

    df["observed_at_dt"] = pd.to_datetime(df["observed_at"], errors="coerce")

    if "resolved_at" in df.columns:
        df["resolved_at_dt"] = pd.to_datetime(df["resolved_at"], errors="coerce")
    else:
        df["resolved_at"] = ""
        df["resolved_at_dt"] = pd.NaT

    df["is_open"] = df["resolution_status"].isin(OPEN_STATUSES)
    df["is_error"] = df["resolution_status"].str.startswith("RESOLUTION_ERROR")
    df["is_closed"] = (
        ~df["is_open"]
        & ~df["is_error"]
        & (df["resolution_status"] != "")
    )

    df["is_win"] = df["is_closed"] & (df["result_r"] > 0)
    df["is_loss"] = df["is_closed"] & (df["result_r"] < 0)
    df["is_breakeven"] = df["is_closed"] & (df["result_r"] == 0)

    return df


def validate_metrics_input(dataset_df: pd.DataFrame) -> pd.DataFrame:
    rows = []

    for column in REQUIRED_COLUMNS:
        passed = column in dataset_df.columns

        rows.append(
            {
                "check_name": f"required_column:{column}",
                "passed": passed,
                "severity": "ERROR",
                "details": "OK" if passed else "MISSING",
            }
        )

    rows.append(
        {
            "check_name": "has_rows",
            "passed": len(dataset_df) > 0,
            "severity": "ERROR",
            "details": f"rows={len(dataset_df)}",
        }
    )

    return pd.DataFrame(rows)


def calculate_profit_factor(closed_df: pd.DataFrame) -> float:
    if closed_df.empty:
        return 0.0

    gross_profit = float(closed_df.loc[closed_df["result_r"] > 0, "result_r"].sum())
    gross_loss = abs(float(closed_df.loc[closed_df["result_r"] < 0, "result_r"].sum()))

    if gross_loss == 0 and gross_profit > 0:
        return 999.0

    if gross_loss == 0:
        return 0.0

    return round(gross_profit / gross_loss, 6)


def calculate_payoff_ratio(closed_df: pd.DataFrame) -> float:
    if closed_df.empty:
        return 0.0

    wins_df = closed_df[closed_df["result_r"] > 0]
    losses_df = closed_df[closed_df["result_r"] < 0]

    if wins_df.empty or losses_df.empty:
        return 0.0

    avg_win = float(wins_df["result_r"].mean())
    avg_loss = abs(float(losses_df["result_r"].mean()))

    if avg_loss == 0:
        return 0.0

    return round(avg_win / avg_loss, 6)


def calculate_consecutive_streak(
    values: list[bool],
) -> int:
    max_streak = 0
    current_streak = 0

    for value in values:
        if value:
            current_streak += 1
            max_streak = max(max_streak, current_streak)
        else:
            current_streak = 0

    return max_streak


def build_equity_curve_df(metrics_df: pd.DataFrame) -> pd.DataFrame:
    closed_df = metrics_df[metrics_df["is_closed"]].copy()

    if closed_df.empty:
        return pd.DataFrame(
            columns=[
                "trade_index",
                "signal_id",
                "observed_at",
                "resolved_at",
                "context_name",
                "cost_profile",
                "direction",
                "resolution_status",
                "result_r",
                "equity_r",
                "equity_peak_r",
                "drawdown_r",
            ]
        )

    closed_df = closed_df.sort_values(
        by=["observed_at_dt", "resolved_at_dt", "signal_id"],
        ascending=[True, True, True],
    ).reset_index(drop=True)

    closed_df["trade_index"] = range(1, len(closed_df) + 1)
    closed_df["equity_r"] = closed_df["result_r"].cumsum()
    closed_df["equity_peak_r"] = closed_df["equity_r"].cummax()
    closed_df["drawdown_r"] = closed_df["equity_r"] - closed_df["equity_peak_r"]

    return closed_df[
        [
            "trade_index",
            "signal_id",
            "observed_at",
            "resolved_at",
            "context_name",
            "cost_profile",
            "direction",
            "resolution_status",
            "result_r",
            "equity_r",
            "equity_peak_r",
            "drawdown_r",
        ]
    ].copy()


def calculate_metrics_dict(
    metrics_df: pd.DataFrame,
) -> dict[str, Any]:
    total_observations = len(metrics_df)
    closed_df = metrics_df[metrics_df["is_closed"]].copy()
    open_observations = int(metrics_df["is_open"].sum()) if not metrics_df.empty else 0
    error_observations = int(metrics_df["is_error"].sum()) if not metrics_df.empty else 0

    resolved_observations = len(closed_df)
    wins = int(closed_df["is_win"].sum()) if not closed_df.empty else 0
    losses = int(closed_df["is_loss"].sum()) if not closed_df.empty else 0
    breakeven = int(closed_df["is_breakeven"].sum()) if not closed_df.empty else 0

    if closed_df.empty:
        return {
            "total_observations": total_observations,
            "resolved_observations": 0,
            "open_observations": open_observations,
            "error_observations": error_observations,
            "wins": 0,
            "losses": 0,
            "breakeven": 0,
            "win_rate": 0.0,
            "loss_rate": 0.0,
            "avg_result_r": 0.0,
            "sum_result_r": 0.0,
            "expectancy_r": 0.0,
            "profit_factor": 0.0,
            "payoff_ratio": 0.0,
            "avg_win_r": 0.0,
            "avg_loss_r": 0.0,
            "best_result_r": 0.0,
            "worst_result_r": 0.0,
            "avg_mfe_r": 0.0,
            "avg_mae_r": 0.0,
            "avg_bars_to_resolution": 0.0,
            "max_consecutive_wins": 0,
            "max_consecutive_losses": 0,
            "max_drawdown_r": 0.0,
        }

    equity_curve_df = build_equity_curve_df(metrics_df)

    win_rate = round(float((closed_df["result_r"] > 0).mean()), 6)
    loss_rate = round(float((closed_df["result_r"] < 0).mean()), 6)

    avg_win_r = (
        round(float(closed_df.loc[closed_df["result_r"] > 0, "result_r"].mean()), 6)
        if wins > 0
        else 0.0
    )

    avg_loss_r = (
        round(float(closed_df.loc[closed_df["result_r"] < 0, "result_r"].mean()), 6)
        if losses > 0
        else 0.0
    )

    win_sequence = (closed_df["result_r"] > 0).tolist()
    loss_sequence = (closed_df["result_r"] < 0).tolist()

    max_drawdown_r = (
        round(float(equity_curve_df["drawdown_r"].min()), 6)
        if not equity_curve_df.empty
        else 0.0
    )

    return {
        "total_observations": total_observations,
        "resolved_observations": resolved_observations,
        "open_observations": open_observations,
        "error_observations": error_observations,
        "wins": wins,
        "losses": losses,
        "breakeven": breakeven,
        "win_rate": win_rate,
        "loss_rate": loss_rate,
        "avg_result_r": round(float(closed_df["result_r"].mean()), 6),
        "sum_result_r": round(float(closed_df["result_r"].sum()), 6),
        "expectancy_r": round(float(closed_df["result_r"].mean()), 6),
        "profit_factor": calculate_profit_factor(closed_df),
        "payoff_ratio": calculate_payoff_ratio(closed_df),
        "avg_win_r": avg_win_r,
        "avg_loss_r": avg_loss_r,
        "best_result_r": round(float(closed_df["result_r"].max()), 6),
        "worst_result_r": round(float(closed_df["result_r"].min()), 6),
        "avg_mfe_r": round(float(closed_df["mfe_r"].mean()), 6),
        "avg_mae_r": round(float(closed_df["mae_r"].mean()), 6),
        "avg_bars_to_resolution": round(float(closed_df["bars_to_resolution"].mean()), 6),
        "max_consecutive_wins": calculate_consecutive_streak(win_sequence),
        "max_consecutive_losses": calculate_consecutive_streak(loss_sequence),
        "max_drawdown_r": max_drawdown_r,
    }


def build_group_metrics_df(
    metrics_df: pd.DataFrame,
    group_columns: list[str],
) -> pd.DataFrame:
    if metrics_df.empty:
        return pd.DataFrame()

    rows = []

    for group_key, group_df in metrics_df.groupby(group_columns, dropna=False):
        group_values = group_key if isinstance(group_key, tuple) else (group_key,)

        row = {}

        for column, value in zip(group_columns, group_values):
            row[column] = value

        row.update(calculate_metrics_dict(group_df))
        rows.append(row)

    result_df = pd.DataFrame(rows)

    if result_df.empty:
        return result_df

    return result_df.sort_values(
        by=["resolved_observations", "avg_result_r"],
        ascending=[False, False],
    ).reset_index(drop=True)


def build_drawdown_summary_df(equity_curve_df: pd.DataFrame) -> pd.DataFrame:
    if equity_curve_df.empty:
        return pd.DataFrame(
            [
                {
                    "trades": 0,
                    "ending_equity_r": 0.0,
                    "max_equity_r": 0.0,
                    "max_drawdown_r": 0.0,
                    "max_drawdown_trade_index": 0,
                }
            ]
        )

    max_drawdown_r = round(float(equity_curve_df["drawdown_r"].min()), 6)
    max_drawdown_rows = equity_curve_df[
        equity_curve_df["drawdown_r"] == equity_curve_df["drawdown_r"].min()
    ]

    max_drawdown_trade_index = (
        int(max_drawdown_rows.iloc[0]["trade_index"])
        if not max_drawdown_rows.empty
        else 0
    )

    return pd.DataFrame(
        [
            {
                "trades": len(equity_curve_df),
                "ending_equity_r": round(float(equity_curve_df["equity_r"].iloc[-1]), 6),
                "max_equity_r": round(float(equity_curve_df["equity_peak_r"].max()), 6),
                "max_drawdown_r": max_drawdown_r,
                "max_drawdown_trade_index": max_drawdown_trade_index,
            }
        ]
    )


def build_metrics_summary_df(
    global_metrics_df: pd.DataFrame,
    validation_df: pd.DataFrame,
    config: ForwardPerformanceMetricsConfig,
) -> pd.DataFrame:
    validation_passed = bool(validation_df["passed"].all()) if not validation_df.empty else False

    resolved_observations = 0

    if not global_metrics_df.empty:
        resolved_observations = int(global_metrics_df.iloc[0].get("resolved_observations", 0))

    minimum_sample_reached = resolved_observations >= config.min_resolved_observations
    preferred_sample_reached = resolved_observations >= config.preferred_resolved_observations

    if not validation_passed:
        metrics_decision = "METRICS_INPUT_VALIDATION_FAILED"
    elif config.sample_mode:
        metrics_decision = "METRICS_ENGINE_VALIDATED_SAMPLE_ONLY"
    elif not config.ready_for_phase_4_2_metrics:
        metrics_decision = "METRICS_BLOCKED_BY_DATASET_QUALITY_GATE"
    elif not minimum_sample_reached:
        metrics_decision = "METRICS_DATASET_NOT_READY"
    elif preferred_sample_reached:
        metrics_decision = "METRICS_PREFERRED_SAMPLE_READY"
    else:
        metrics_decision = "METRICS_MINIMUM_SAMPLE_READY"

    return pd.DataFrame(
        [
            {
                "validation_passed": validation_passed,
                "dataset_quality_decision": config.dataset_quality_decision,
                "ready_for_phase_4_2_metrics": config.ready_for_phase_4_2_metrics,
                "sample_mode": config.sample_mode,
                "resolved_observations": resolved_observations,
                "min_resolved_observations": config.min_resolved_observations,
                "preferred_resolved_observations": config.preferred_resolved_observations,
                "minimum_sample_reached": minimum_sample_reached,
                "preferred_sample_reached": preferred_sample_reached,
                "paper_trade_execution_allowed": False,
                "real_capital_allowed": False,
                "live_alerts_allowed": False,
                "exchange_execution_allowed": False,
                "automation_allowed": False,
                "metrics_decision": metrics_decision,
            }
        ]
    )


def run_forward_performance_metrics(
    dataset_df: pd.DataFrame,
    config: ForwardPerformanceMetricsConfig | None = None,
) -> tuple[
    pd.DataFrame,
    pd.DataFrame,
    pd.DataFrame,
    pd.DataFrame,
    pd.DataFrame,
    pd.DataFrame,
    pd.DataFrame,
    pd.DataFrame,
    pd.DataFrame,
    pd.DataFrame,
]:
    if config is None:
        config = ForwardPerformanceMetricsConfig()

    validation_df = validate_metrics_input(dataset_df)
    metrics_df = normalize_metrics_dataset(dataset_df)

    global_metrics_df = pd.DataFrame([calculate_metrics_dict(metrics_df)])

    by_context_df = build_group_metrics_df(metrics_df, ["context_name"])
    by_cost_profile_df = build_group_metrics_df(metrics_df, ["cost_profile"])
    by_direction_df = build_group_metrics_df(metrics_df, ["direction"])
    by_resolution_status_df = build_group_metrics_df(metrics_df, ["resolution_status"])

    equity_curve_df = build_equity_curve_df(metrics_df)
    drawdown_summary_df = build_drawdown_summary_df(equity_curve_df)

    metrics_summary_df = build_metrics_summary_df(
        global_metrics_df=global_metrics_df,
        validation_df=validation_df,
        config=config,
    )

    return (
        metrics_summary_df,
        validation_df,
        metrics_df,
        global_metrics_df,
        by_context_df,
        by_cost_profile_df,
        by_direction_df,
        by_resolution_status_df,
        equity_curve_df,
        drawdown_summary_df,
    )