from pathlib import Path
import pandas as pd

from src.backtesting.backtesting_engine_v3 import BacktestConfig, run_backtest_v3
from src.market_structure.mtf_regime_filter import (
    enrich_15m_with_mtf_regime,
    long_allowed_by_mtf_regime,
)


def build_config(
    atr_multiplier: float,
    risk_reward: float,
    max_holding_bars: int,
) -> BacktestConfig:
    return BacktestConfig(
        initial_capital=1000.0,
        risk_per_trade=0.01,
        risk_reward=risk_reward,
        fee_rate=0.001,
        spread_rate=0.0002,
        atr_period=14,
        atr_multiplier=atr_multiplier,
        max_holding_bars=max_holding_bars,
        direction_mode="long_only",
    )


def long_v2_best_entry_signal(df: pd.DataFrame, index: int, config=None) -> str:
    """
    LONG V2 research signal.

    Fixed entry logic based on Fase 1.13 best result:
    - Fibonacci zone: 0.500 - 0.618
    - Confirmation: break previous high
    - MTF filter: enabled

    This is still research-only.
    It does not replace the official strategy.
    """

    lookback_bars = 48
    fib_entry_low = 0.500
    fib_entry_high = 0.618
    min_impulse_pct = 0.02

    if index < lookback_bars:
        return "NONE"

    window = df.iloc[index - lookback_bars:index]

    if window.empty:
        return "NONE"

    impulse_low_idx = window["low"].idxmin()
    impulse_low = float(df.loc[impulse_low_idx, "low"])

    after_low = df.loc[impulse_low_idx:index - 1]

    if after_low.empty:
        return "NONE"

    impulse_high_idx = after_low["high"].idxmax()
    impulse_high = float(df.loc[impulse_high_idx, "high"])

    if impulse_high <= impulse_low:
        return "NONE"

    impulse_pct = (impulse_high / impulse_low) - 1

    if impulse_pct < min_impulse_pct:
        return "NONE"

    impulse_range = impulse_high - impulse_low

    fib_050_price = impulse_high - (impulse_range * fib_entry_low)
    fib_0618_price = impulse_high - (impulse_range * fib_entry_high)

    zone_low = min(fib_050_price, fib_0618_price)
    zone_high = max(fib_050_price, fib_0618_price)

    row = df.iloc[index]

    candle_high = float(row["high"])
    candle_low = float(row["low"])
    candle_close = float(row["close"])

    touches_fib_zone = candle_low <= zone_high and candle_high >= zone_low

    if not touches_fib_zone:
        return "NONE"

    previous_high = float(df.iloc[index - 1]["high"])

    if candle_close <= previous_high:
        return "NONE"

    regime_1h = row.get("regime_1h", "UNKNOWN")
    regime_4h = row.get("regime_4h", "UNKNOWN")

    if not long_allowed_by_mtf_regime(regime_1h, regime_4h):
        return "NONE"

    return "LONG"


def summarize_result(
    atr_multiplier: float,
    risk_reward: float,
    max_holding_bars: int,
    trades_df: pd.DataFrame,
    summary: dict,
) -> dict:
    total_trades = int(summary.get("total_trades", 0))

    take_profit_count = 0
    stop_loss_count = 0
    max_holding_exit_count = 0
    avg_holding_bars = 0.0

    if len(trades_df) > 0:
        take_profit_count = int((trades_df["exit_reason"] == "TAKE_PROFIT").sum())
        stop_loss_count = int((trades_df["exit_reason"] == "STOP_LOSS").sum())
        max_holding_exit_count = int(
            (trades_df["exit_reason"] == "MAX_HOLDING_EXIT").sum()
        )

        if "holding_bars" in trades_df.columns:
            avg_holding_bars = float(trades_df["holding_bars"].mean())

    profit_factor = summary.get("profit_factor", None)

    if profit_factor is None or pd.isna(profit_factor):
        pf_value = 0.0
    else:
        pf_value = float(profit_factor)

    total_return_pct = float(summary.get("total_return_pct", 0.0))
    win_rate = float(summary.get("win_rate", 0.0))
    expectancy = float(summary.get("expectancy", 0.0))
    max_drawdown_pct = float(summary.get("max_drawdown_pct", 0.0))

    # Research score only.
    # Penalizes drawdown and rewards return, PF, win rate and expectancy.
    quality_score = (
        (total_return_pct * 100)
        + (pf_value * 6)
        + (win_rate * 10)
        + (expectancy * 0.25)
        + (max_drawdown_pct * 100)
    )

    return {
        "variant_name": (
            f"LONG_V2_ATR_{atr_multiplier}_RR_{risk_reward}_HOLD_{max_holding_bars}"
        ),
        "atr_multiplier": atr_multiplier,
        "risk_reward": risk_reward,
        "max_holding_bars": max_holding_bars,
        "total_trades": total_trades,
        "wins": int(summary.get("wins", 0)),
        "losses": int(summary.get("losses", 0)),
        "ending_capital": summary.get("ending_capital", 1000.0),
        "total_return_pct": total_return_pct,
        "win_rate": win_rate,
        "profit_factor": profit_factor,
        "expectancy": expectancy,
        "max_drawdown_pct": max_drawdown_pct,
        "take_profit_count": take_profit_count,
        "stop_loss_count": stop_loss_count,
        "max_holding_exit_count": max_holding_exit_count,
        "avg_holding_bars": avg_holding_bars,
        "quality_score": quality_score,
    }


def classify_result(row) -> str:
    trades = int(row["total_trades"])
    total_return_pct = float(row["total_return_pct"])
    win_rate = float(row["win_rate"])
    max_drawdown_pct = float(row["max_drawdown_pct"])
    profit_factor = row["profit_factor"]

    if trades < 10:
        return "INSUFFICIENT_TRADES"

    if profit_factor is None or pd.isna(profit_factor):
        return "INVALID_PF"

    profit_factor = float(profit_factor)

    if (
        total_return_pct > 0.08
        and profit_factor >= 1.25
        and win_rate >= 0.45
        and max_drawdown_pct > -0.10
    ):
        return "PROMISING"

    if total_return_pct > 0.03 and profit_factor >= 1.15:
        return "WEAK_PROMISING"

    if total_return_pct > 0 and profit_factor >= 1.0:
        return "NEAR_BREAKEVEN_POSITIVE"

    if total_return_pct > -0.03 and profit_factor >= 0.90:
        return "NEAR_BREAKEVEN"

    return "REJECTED"


def main():
    enriched_csv = Path("reports") / "oos_btcusdt_15m_with_mtf_regime.csv"

    enrich_15m_with_mtf_regime(
        entry_csv_path=Path("data") / "oos_btcusdt_15m_2024_01_03.csv",
        h1_csv_path=Path("data") / "oos_btcusdt_1h_2024_01_03.csv",
        h4_csv_path=Path("data") / "oos_btcusdt_4h_2024_01_03.csv",
        output_path=enriched_csv,
    )

    atr_multipliers = [1.0, 1.25, 1.5, 2.0]
    risk_rewards = [1.5, 2.0, 2.5, 3.0]
    max_holding_options = [24, 48, 72, 96]

    results = []

    print("LONG V2 RISK / EXIT RESEARCH")
    print("=" * 100)
    print("Dataset: BTCUSDT spot, 2024-01-01 a 2024-03-01")
    print("Entry fixed: Fib 0.500–0.618 + break_prev_high + MTF")
    print()

    for atr_multiplier in atr_multipliers:
        for risk_reward in risk_rewards:
            for max_holding_bars in max_holding_options:
                config = build_config(
                    atr_multiplier=atr_multiplier,
                    risk_reward=risk_reward,
                    max_holding_bars=max_holding_bars,
                )

                trades_df, summary = run_backtest_v3(
                    csv_path=enriched_csv,
                    config=config,
                    output_dir=Path("reports"),
                    strategy_func=long_v2_best_entry_signal,
                )

                result = summarize_result(
                    atr_multiplier=atr_multiplier,
                    risk_reward=risk_reward,
                    max_holding_bars=max_holding_bars,
                    trades_df=trades_df,
                    summary=summary,
                )

                results.append(result)

                print(
                    f"{result['variant_name']} | "
                    f"trades={result['total_trades']} | "
                    f"return={result['total_return_pct']:.2%} | "
                    f"wr={result['win_rate']:.2%} | "
                    f"pf={result['profit_factor']} | "
                    f"mdd={result['max_drawdown_pct']:.2%}"
                )

    results_df = pd.DataFrame(results)
    results_df["research_status"] = results_df.apply(classify_result, axis=1)

    output_path = Path("reports") / "long_v2_risk_exit_research_results.csv"
    results_df.to_csv(output_path, index=False)

    print()
    print("TOP 15 POR QUALITY SCORE")
    print("=" * 100)
    print(
        results_df[
            [
                "variant_name",
                "research_status",
                "quality_score",
                "total_trades",
                "total_return_pct",
                "win_rate",
                "profit_factor",
                "expectancy",
                "max_drawdown_pct",
                "take_profit_count",
                "stop_loss_count",
                "max_holding_exit_count",
                "avg_holding_bars",
            ]
        ]
        .sort_values(by="quality_score", ascending=False)
        .head(15)
        .to_string(index=False)
    )

    print()
    print("TOP 15 POR PROFIT FACTOR")
    print("=" * 100)
    print(
        results_df[
            [
                "variant_name",
                "research_status",
                "quality_score",
                "total_trades",
                "total_return_pct",
                "win_rate",
                "profit_factor",
                "expectancy",
                "max_drawdown_pct",
                "take_profit_count",
                "stop_loss_count",
                "max_holding_exit_count",
            ]
        ]
        .sort_values(by=["profit_factor", "total_return_pct"], ascending=[False, False])
        .head(15)
        .to_string(index=False)
    )

    print()
    print("PROMEDIO POR ATR MULTIPLIER")
    print("=" * 100)
    print(
        results_df.groupby(["atr_multiplier"])
        .agg(
            variants=("variant_name", "count"),
            avg_trades=("total_trades", "mean"),
            avg_return=("total_return_pct", "mean"),
            avg_win_rate=("win_rate", "mean"),
            avg_profit_factor=("profit_factor", "mean"),
            avg_drawdown=("max_drawdown_pct", "mean"),
            best_quality_score=("quality_score", "max"),
        )
        .reset_index()
        .sort_values(by="best_quality_score", ascending=False)
        .to_string(index=False)
    )

    print()
    print("PROMEDIO POR RISK REWARD")
    print("=" * 100)
    print(
        results_df.groupby(["risk_reward"])
        .agg(
            variants=("variant_name", "count"),
            avg_trades=("total_trades", "mean"),
            avg_return=("total_return_pct", "mean"),
            avg_win_rate=("win_rate", "mean"),
            avg_profit_factor=("profit_factor", "mean"),
            avg_drawdown=("max_drawdown_pct", "mean"),
            best_quality_score=("quality_score", "max"),
        )
        .reset_index()
        .sort_values(by="best_quality_score", ascending=False)
        .to_string(index=False)
    )

    print()
    print("PROMEDIO POR MAX HOLDING BARS")
    print("=" * 100)
    print(
        results_df.groupby(["max_holding_bars"])
        .agg(
            variants=("variant_name", "count"),
            avg_trades=("total_trades", "mean"),
            avg_return=("total_return_pct", "mean"),
            avg_win_rate=("win_rate", "mean"),
            avg_profit_factor=("profit_factor", "mean"),
            avg_drawdown=("max_drawdown_pct", "mean"),
            best_quality_score=("quality_score", "max"),
        )
        .reset_index()
        .sort_values(by="best_quality_score", ascending=False)
        .to_string(index=False)
    )

    print()
    print("ARCHIVO GENERADO")
    print("=" * 100)
    print(output_path)


if __name__ == "__main__":
    main()