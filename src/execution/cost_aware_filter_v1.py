from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class CostProfile:
    name: str
    platform: str
    mode: str
    fee_pct_round_trip: float
    spread_pct_round_trip: float
    slippage_pct_round_trip: float
    funding_or_time_cost_pct: float
    safety_buffer_pct: float
    default_risk_pct: float
    risk_per_trade_pct: float

    @property
    def total_cost_pct(self) -> float:
        return (
            self.fee_pct_round_trip
            + self.spread_pct_round_trip
            + self.slippage_pct_round_trip
            + self.funding_or_time_cost_pct
            + self.safety_buffer_pct
        )


def safe_float(value, default: float = 0.0) -> float:
    try:
        if value is None or pd.isna(value):
            return default
        return float(value)
    except Exception:
        return default


def build_cost_profiles() -> list[CostProfile]:
    return [
        CostProfile(
            name="BINANCE_SCALP_BASE_ESTIMATE",
            platform="BINANCE",
            mode="SCALP",
            fee_pct_round_trip=0.0008,
            spread_pct_round_trip=0.0004,
            slippage_pct_round_trip=0.0004,
            funding_or_time_cost_pct=0.0000,
            safety_buffer_pct=0.0004,
            default_risk_pct=0.0125,
            risk_per_trade_pct=0.0100,
        ),
        CostProfile(
            name="BINANCE_SCALP_STRESS_ESTIMATE",
            platform="BINANCE",
            mode="SCALP",
            fee_pct_round_trip=0.0012,
            spread_pct_round_trip=0.0008,
            slippage_pct_round_trip=0.0008,
            funding_or_time_cost_pct=0.0000,
            safety_buffer_pct=0.0007,
            default_risk_pct=0.0125,
            risk_per_trade_pct=0.0100,
        ),
        CostProfile(
            name="QUANTFURY_SWING_BASE_ESTIMATE",
            platform="QUANTFURY",
            mode="SWING",
            fee_pct_round_trip=0.0000,
            spread_pct_round_trip=0.0035,
            slippage_pct_round_trip=0.0005,
            funding_or_time_cost_pct=0.0000,
            safety_buffer_pct=0.0010,
            default_risk_pct=0.0350,
            risk_per_trade_pct=0.0100,
        ),
        CostProfile(
            name="QUANTFURY_SWING_STRESS_ESTIMATE",
            platform="QUANTFURY",
            mode="SWING",
            fee_pct_round_trip=0.0000,
            spread_pct_round_trip=0.0060,
            slippage_pct_round_trip=0.0010,
            funding_or_time_cost_pct=0.0000,
            safety_buffer_pct=0.0015,
            default_risk_pct=0.0350,
            risk_per_trade_pct=0.0100,
        ),
        CostProfile(
            name="EXTREME_COST_STRESS_TEST",
            platform="GENERIC",
            mode="STRESS",
            fee_pct_round_trip=0.0015,
            spread_pct_round_trip=0.0080,
            slippage_pct_round_trip=0.0020,
            funding_or_time_cost_pct=0.0000,
            safety_buffer_pct=0.0020,
            default_risk_pct=0.0350,
            risk_per_trade_pct=0.0100,
        ),
    ]


def infer_result_r(row: pd.Series) -> float:
    for col in [
        "result_r",
        "r_multiple",
        "trade_r",
        "pnl_r",
        "net_r",
    ]:
        if col in row.index:
            return safe_float(row[col], 0.0)

    for col in [
        "net_pnl_r",
        "gross_pnl_r",
    ]:
        if col in row.index:
            return safe_float(row[col], 0.0)

    return 0.0


def infer_risk_pct(row: pd.Series, default_risk_pct: float) -> float:
    for col in [
        "risk_pct",
        "initial_risk_pct",
        "stop_distance_pct",
    ]:
        if col in row.index:
            value = abs(safe_float(row[col], 0.0))
            if value > 0:
                return value

    if "entry_price" in row.index and "stop_loss" in row.index:
        entry = abs(safe_float(row["entry_price"], 0.0))
        stop = abs(safe_float(row["stop_loss"], 0.0))

        if entry > 0 and stop > 0:
            risk_pct = abs(entry - stop) / entry
            if risk_pct > 0:
                return risk_pct

    if "entry_price" in row.index and "stop_price" in row.index:
        entry = abs(safe_float(row["entry_price"], 0.0))
        stop = abs(safe_float(row["stop_price"], 0.0))

        if entry > 0 and stop > 0:
            risk_pct = abs(entry - stop) / entry
            if risk_pct > 0:
                return risk_pct

    return default_risk_pct


def apply_cost_profile_to_trades(
    trades_df: pd.DataFrame,
    profile: CostProfile,
) -> pd.DataFrame:
    if trades_df is None or trades_df.empty:
        return pd.DataFrame()

    adjusted = trades_df.copy()

    result_r_values = []
    risk_pct_values = []
    cost_r_values = []
    adjusted_result_r_values = []
    adjusted_return_values = []

    for _, row in adjusted.iterrows():
        result_r = infer_result_r(row)
        risk_pct = infer_risk_pct(row, profile.default_risk_pct)

        if risk_pct <= 0:
            risk_pct = profile.default_risk_pct

        cost_r = profile.total_cost_pct / risk_pct
        adjusted_result_r = result_r - cost_r
        adjusted_return = adjusted_result_r * profile.risk_per_trade_pct

        result_r_values.append(result_r)
        risk_pct_values.append(risk_pct)
        cost_r_values.append(cost_r)
        adjusted_result_r_values.append(adjusted_result_r)
        adjusted_return_values.append(adjusted_return)

    adjusted["cost_profile"] = profile.name
    adjusted["platform"] = profile.platform
    adjusted["execution_mode"] = profile.mode
    adjusted["estimated_total_cost_pct"] = profile.total_cost_pct
    adjusted["estimated_risk_pct"] = risk_pct_values
    adjusted["raw_result_r"] = result_r_values
    adjusted["estimated_cost_r"] = cost_r_values
    adjusted["cost_adjusted_result_r"] = adjusted_result_r_values
    adjusted["cost_adjusted_return"] = adjusted_return_values

    return adjusted


def summarize_cost_adjusted_trades(
    adjusted_trades_df: pd.DataFrame,
    profile: CostProfile,
) -> dict:
    if adjusted_trades_df is None or adjusted_trades_df.empty:
        return {
            "cost_profile": profile.name,
            "platform": profile.platform,
            "execution_mode": profile.mode,
            "total_trades": 0,
            "compound_return": 0.0,
            "win_rate": 0.0,
            "profit_factor": 0.0,
            "expectancy_r": 0.0,
            "avg_cost_r": 0.0,
            "avg_risk_pct": 0.0,
            "max_drawdown": 0.0,
            "positive_trades": 0,
            "negative_trades": 0,
            "cost_decision": "TOO_FEW_TRADES",
        }

    results_r = pd.to_numeric(
        adjusted_trades_df["cost_adjusted_result_r"],
        errors="coerce",
    ).fillna(0.0)

    returns = pd.to_numeric(
        adjusted_trades_df["cost_adjusted_return"],
        errors="coerce",
    ).fillna(0.0)

    equity = 1.0
    peak = 1.0
    max_drawdown = 0.0

    for trade_return in returns:
        equity *= 1 + trade_return
        peak = max(peak, equity)
        drawdown = equity / peak - 1
        max_drawdown = min(max_drawdown, drawdown)

    wins = results_r[results_r > 0]
    losses = results_r[results_r <= 0]

    gross_profit = float(wins.sum())
    gross_loss = abs(float(losses.sum()))

    profit_factor = gross_profit / gross_loss if gross_loss > 0 else 0.0

    summary = {
        "cost_profile": profile.name,
        "platform": profile.platform,
        "execution_mode": profile.mode,
        "total_cost_pct": profile.total_cost_pct,
        "risk_per_trade_pct": profile.risk_per_trade_pct,
        "total_trades": int(len(results_r)),
        "compound_return": float(equity - 1),
        "win_rate": float((results_r > 0).mean()),
        "profit_factor": float(profit_factor),
        "expectancy_r": float(results_r.mean()),
        "avg_cost_r": float(
            pd.to_numeric(
                adjusted_trades_df["estimated_cost_r"],
                errors="coerce",
            ).mean()
        ),
        "avg_risk_pct": float(
            pd.to_numeric(
                adjusted_trades_df["estimated_risk_pct"],
                errors="coerce",
            ).mean()
        ),
        "max_drawdown": float(max_drawdown),
        "positive_trades": int((results_r > 0).sum()),
        "negative_trades": int((results_r <= 0).sum()),
    }

    summary["cost_decision"] = classify_cost_adjusted_result(summary)

    return summary


def classify_cost_adjusted_result(summary: dict) -> str:
    trades = int(summary.get("total_trades", 0))
    compound_return = safe_float(summary.get("compound_return"), 0.0)
    profit_factor = safe_float(summary.get("profit_factor"), 0.0)
    expectancy_r = safe_float(summary.get("expectancy_r"), 0.0)
    max_drawdown = safe_float(summary.get("max_drawdown"), 0.0)
    win_rate = safe_float(summary.get("win_rate"), 0.0)

    if trades < 30:
        return "TOO_FEW_TRADES"

    if (
        compound_return > 0.20
        and profit_factor >= 1.25
        and expectancy_r >= 0.10
        and max_drawdown > -0.15
        and win_rate >= 0.40
    ):
        return "COST_AWARE_PASS"

    if (
        compound_return > 0.00
        and profit_factor >= 1.05
        and expectancy_r > 0.00
        and max_drawdown > -0.18
    ):
        return "COST_AWARE_WEAK_PASS"

    if (
        compound_return > -0.05
        and profit_factor >= 0.95
        and max_drawdown > -0.15
    ):
        return "COST_AWARE_NEAR_BREAKEVEN"

    return "COST_AWARE_FAILED"


def classify_aggregate_cost_result(row: dict) -> str:
    trades = int(row.get("total_trades", 0))
    compound_return = safe_float(row.get("compound_return"), 0.0)
    avg_profit_factor = safe_float(row.get("avg_profit_factor"), 0.0)
    avg_expectancy_r = safe_float(row.get("avg_expectancy_r"), 0.0)
    worst_drawdown = safe_float(row.get("worst_drawdown"), 0.0)
    positive_window_rate = safe_float(row.get("positive_window_rate"), 0.0)

    if trades < 30:
        return "TOO_FEW_TRADES"

    if (
        compound_return > 0.20
        and avg_profit_factor >= 1.25
        and avg_expectancy_r >= 0.10
        and worst_drawdown > -0.15
        and positive_window_rate >= 0.50
    ):
        return "COST_AWARE_PASS"

    if (
        compound_return > 0.00
        and avg_profit_factor >= 1.05
        and avg_expectancy_r > 0.00
        and worst_drawdown > -0.18
        and positive_window_rate >= 0.45
    ):
        return "COST_AWARE_WEAK_PASS"

    if (
        compound_return > -0.05
        and avg_profit_factor >= 0.95
        and worst_drawdown > -0.15
    ):
        return "COST_AWARE_NEAR_BREAKEVEN"

    return "COST_AWARE_FAILED"


def aggregate_cost_summaries(summary_df: pd.DataFrame) -> pd.DataFrame:
    if summary_df.empty:
        return pd.DataFrame()

    rows = []

    for cost_profile, group in summary_df.groupby("cost_profile"):
        group = group.copy()

        returns = pd.to_numeric(group["compound_return"], errors="coerce").fillna(0.0)
        trades = pd.to_numeric(group["total_trades"], errors="coerce").fillna(0)

        row = {
            "cost_profile": cost_profile,
            "platform": group["platform"].iloc[0],
            "execution_mode": group["execution_mode"].iloc[0],
            "windows": int(len(group)),
            "total_trades": int(trades.sum()),
            "compound_return": float((1 + returns).prod() - 1),
            "avg_profit_factor": float(
                pd.to_numeric(group["profit_factor"], errors="coerce").mean()
            ),
            "avg_expectancy_r": float(
                pd.to_numeric(group["expectancy_r"], errors="coerce").mean()
            ),
            "avg_cost_r": float(
                pd.to_numeric(group["avg_cost_r"], errors="coerce").mean()
            ),
            "avg_risk_pct": float(
                pd.to_numeric(group["avg_risk_pct"], errors="coerce").mean()
            ),
            "worst_drawdown": float(
                pd.to_numeric(group["max_drawdown"], errors="coerce").min()
            ),
            "positive_window_rate": float((returns > 0).mean()),
        }

        row["cost_decision"] = classify_aggregate_cost_result(row)

        rows.append(row)

    return pd.DataFrame(rows).sort_values(
        by=["platform", "compound_return"],
        ascending=[True, False],
    )