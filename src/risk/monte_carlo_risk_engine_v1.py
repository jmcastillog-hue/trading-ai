from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class MonteCarloConfig:
    simulations: int = 10000
    random_seed: int = 42
    min_trades: int = 30
    initial_equity: float = 1.0
    sample_with_replacement: bool = True


def safe_float(value, default: float = 0.0) -> float:
    try:
        if value is None or pd.isna(value):
            return default
        return float(value)
    except Exception:
        return default


def calculate_max_drawdown(equity_curve: np.ndarray) -> float:
    if len(equity_curve) == 0:
        return 0.0

    peaks = np.maximum.accumulate(equity_curve)
    drawdowns = equity_curve / peaks - 1.0

    return float(drawdowns.min())


def calculate_max_losing_streak(results_r: np.ndarray) -> int:
    max_streak = 0
    current_streak = 0

    for value in results_r:
        if value <= 0:
            current_streak += 1
            max_streak = max(max_streak, current_streak)
        else:
            current_streak = 0

    return int(max_streak)


def calculate_equity_curve(
    returns: np.ndarray,
    initial_equity: float = 1.0,
) -> np.ndarray:
    equity_values = []
    equity = initial_equity

    for trade_return in returns:
        equity *= 1.0 + float(trade_return)
        equity_values.append(equity)

    return np.array(equity_values, dtype=float)


def prepare_trade_sample(
    trades_df: pd.DataFrame,
    profile_name: str,
) -> pd.DataFrame:
    if trades_df.empty:
        return pd.DataFrame()

    if "cost_profile" not in trades_df.columns:
        raise ValueError("Missing required column: cost_profile")

    filtered = trades_df[trades_df["cost_profile"] == profile_name].copy()

    required_columns = [
        "cost_adjusted_return",
        "cost_adjusted_result_r",
    ]

    for column in required_columns:
        if column not in filtered.columns:
            raise ValueError(f"Missing required column: {column}")

    filtered["cost_adjusted_return"] = pd.to_numeric(
        filtered["cost_adjusted_return"],
        errors="coerce",
    )

    filtered["cost_adjusted_result_r"] = pd.to_numeric(
        filtered["cost_adjusted_result_r"],
        errors="coerce",
    )

    filtered = filtered.dropna(
        subset=[
            "cost_adjusted_return",
            "cost_adjusted_result_r",
        ]
    )

    return filtered.reset_index(drop=True)


def run_monte_carlo_for_profile(
    trades_df: pd.DataFrame,
    profile_name: str,
    config: MonteCarloConfig | None = None,
) -> tuple[pd.DataFrame, dict]:
    if config is None:
        config = MonteCarloConfig()

    sample_df = prepare_trade_sample(
        trades_df=trades_df,
        profile_name=profile_name,
    )

    if len(sample_df) < config.min_trades:
        summary = {
            "cost_profile": profile_name,
            "simulations": 0,
            "sample_trades": int(len(sample_df)),
            "decision": "TOO_FEW_TRADES",
        }

        return pd.DataFrame(), summary

    returns = sample_df["cost_adjusted_return"].to_numpy(dtype=float)
    results_r = sample_df["cost_adjusted_result_r"].to_numpy(dtype=float)

    rng = np.random.default_rng(config.random_seed)

    simulation_rows = []

    trade_count = len(returns)

    for simulation_id in range(config.simulations):
        if config.sample_with_replacement:
            indexes = rng.integers(
                low=0,
                high=trade_count,
                size=trade_count,
            )
        else:
            indexes = rng.permutation(trade_count)

        simulated_returns = returns[indexes]
        simulated_results_r = results_r[indexes]

        equity_curve = calculate_equity_curve(
            returns=simulated_returns,
            initial_equity=config.initial_equity,
        )

        final_equity = float(equity_curve[-1])
        total_return = final_equity / config.initial_equity - 1.0
        max_drawdown = calculate_max_drawdown(equity_curve)
        max_losing_streak = calculate_max_losing_streak(simulated_results_r)

        simulation_rows.append(
            {
                "cost_profile": profile_name,
                "simulation_id": simulation_id,
                "trade_count": trade_count,
                "final_equity": final_equity,
                "total_return": total_return,
                "max_drawdown": max_drawdown,
                "max_losing_streak": max_losing_streak,
                "avg_result_r": float(simulated_results_r.mean()),
                "win_rate": float((simulated_results_r > 0).mean()),
            }
        )

    simulations_df = pd.DataFrame(simulation_rows)
    summary = summarize_monte_carlo_profile(
        simulations_df=simulations_df,
        sample_df=sample_df,
        profile_name=profile_name,
        config=config,
    )

    return simulations_df, summary


def percentile(series: pd.Series, q: float) -> float:
    return float(series.quantile(q))


def summarize_monte_carlo_profile(
    simulations_df: pd.DataFrame,
    sample_df: pd.DataFrame,
    profile_name: str,
    config: MonteCarloConfig,
) -> dict:
    if simulations_df.empty:
        return {
            "cost_profile": profile_name,
            "simulations": 0,
            "sample_trades": int(len(sample_df)),
            "decision": "TOO_FEW_TRADES",
        }

    total_returns = pd.to_numeric(
        simulations_df["total_return"],
        errors="coerce",
    ).fillna(0.0)

    max_drawdowns = pd.to_numeric(
        simulations_df["max_drawdown"],
        errors="coerce",
    ).fillna(0.0)

    losing_streaks = pd.to_numeric(
        simulations_df["max_losing_streak"],
        errors="coerce",
    ).fillna(0)

    raw_returns = pd.to_numeric(
        sample_df["cost_adjusted_return"],
        errors="coerce",
    ).fillna(0.0)

    raw_results_r = pd.to_numeric(
        sample_df["cost_adjusted_result_r"],
        errors="coerce",
    ).fillna(0.0)

    raw_equity_curve = calculate_equity_curve(
        returns=raw_returns.to_numpy(dtype=float),
        initial_equity=config.initial_equity,
    )

    raw_return = float(raw_equity_curve[-1] / config.initial_equity - 1.0)
    raw_max_drawdown = calculate_max_drawdown(raw_equity_curve)
    raw_max_losing_streak = calculate_max_losing_streak(
        raw_results_r.to_numpy(dtype=float)
    )

    summary = {
        "cost_profile": profile_name,
        "simulations": int(len(simulations_df)),
        "sample_trades": int(len(sample_df)),
        "raw_sequence_return": raw_return,
        "raw_sequence_max_drawdown": raw_max_drawdown,
        "raw_sequence_max_losing_streak": raw_max_losing_streak,
        "median_return": percentile(total_returns, 0.50),
        "p05_return": percentile(total_returns, 0.05),
        "p01_return": percentile(total_returns, 0.01),
        "p95_return": percentile(total_returns, 0.95),
        "median_max_drawdown": percentile(max_drawdowns, 0.50),
        "p05_max_drawdown": percentile(max_drawdowns, 0.05),
        "p01_max_drawdown": percentile(max_drawdowns, 0.01),
        "p95_max_drawdown": percentile(max_drawdowns, 0.95),
        "median_losing_streak": percentile(losing_streaks, 0.50),
        "p95_losing_streak": percentile(losing_streaks, 0.95),
        "p99_losing_streak": percentile(losing_streaks, 0.99),
        "probability_negative_return": float((total_returns < 0).mean()),
        "probability_drawdown_below_15pct": float((max_drawdowns <= -0.15).mean()),
        "probability_drawdown_below_20pct": float((max_drawdowns <= -0.20).mean()),
        "avg_result_r": float(raw_results_r.mean()),
        "win_rate": float((raw_results_r > 0).mean()),
    }

    summary["decision"] = classify_monte_carlo_summary(summary)

    return summary


def classify_monte_carlo_summary(summary: dict) -> str:
    trades = int(summary.get("sample_trades", 0))
    p05_return = safe_float(summary.get("p05_return"), 0.0)
    p01_return = safe_float(summary.get("p01_return"), 0.0)
    p01_drawdown = safe_float(summary.get("p01_max_drawdown"), 0.0)
    p99_losing_streak = safe_float(summary.get("p99_losing_streak"), 0.0)
    probability_negative = safe_float(
        summary.get("probability_negative_return"),
        1.0,
    )
    probability_dd_20 = safe_float(
        summary.get("probability_drawdown_below_20pct"),
        1.0,
    )

    if trades < 30:
        return "TOO_FEW_TRADES"

    if (
        p05_return > 0.00
        and p01_return > -0.10
        and p01_drawdown > -0.20
        and p99_losing_streak <= 8
        and probability_negative <= 0.10
        and probability_dd_20 <= 0.05
    ):
        return "MONTE_CARLO_PASS"

    if (
        p05_return > 0.00
        and p01_return > -0.10
        and p01_drawdown > -0.25
        and p99_losing_streak <= 12
        and probability_negative <= 0.05
        and probability_dd_20 <= 0.05
    ):
        return "MONTE_CARLO_EDGE_WITH_SEQUENCE_RISK"

    if (
        p05_return > -0.05
        and p01_return > -0.15
        and p01_drawdown > -0.30
        and p99_losing_streak <= 12
        and probability_negative <= 0.20
        and probability_dd_20 <= 0.15
    ):
        return "MONTE_CARLO_WEAK_PASS_WITH_SEQUENCE_RISK"

    if (
        p05_return > -0.10
        and p01_drawdown > -0.30
        and probability_negative <= 0.35
    ):
        return "MONTE_CARLO_HIGH_SEQUENCE_RISK"

    return "MONTE_CARLO_FAILED"


def summarize_all_profiles(summary_df: pd.DataFrame) -> pd.DataFrame:
    if summary_df.empty:
        return pd.DataFrame()

    return summary_df.sort_values(
        by=[
            "decision",
            "p05_return",
            "p01_max_drawdown",
        ],
        ascending=[
            True,
            False,
            False,
        ],
    ).reset_index(drop=True)