from pathlib import Path
import pandas as pd

from src.backtesting.backtesting_engine_v3 import BacktestConfig, run_backtest_v3
from src.market_structure.mtf_regime_filter import (
    enrich_15m_with_mtf_regime,
    long_allowed_by_mtf_regime,
)


def build_config() -> BacktestConfig:
    return BacktestConfig(
        initial_capital=1000.0,
        risk_per_trade=0.01,
        risk_reward=2.5,
        fee_rate=0.001,
        spread_rate=0.0002,
        atr_period=14,
        atr_multiplier=1.25,
        max_holding_bars=48,
        direction_mode="long_only",
    )


def long_signal_variant(
    df: pd.DataFrame,
    index: int,
    lookback_bars: int,
    fib_entry_low: float,
    fib_entry_high: float,
    min_impulse_pct: float,
    confirmation_type: str,
    use_mtf_filter: bool,
) -> str:
    """
    Research-only LONG signal.

    This does not replace the official FIB V5 LONG strategy.
    It tests alternative Fibonacci zones and confirmation rules.
    """

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

    fib_low_price = impulse_high - (impulse_range * fib_entry_low)
    fib_high_price = impulse_high - (impulse_range * fib_entry_high)

    zone_low = min(fib_low_price, fib_high_price)
    zone_high = max(fib_low_price, fib_high_price)

    row = df.iloc[index]

    candle_open = float(row["open"])
    candle_high = float(row["high"])
    candle_low = float(row["low"])
    candle_close = float(row["close"])

    touches_fib_zone = candle_low <= zone_high and candle_high >= zone_low

    if not touches_fib_zone:
        return "NONE"

    if confirmation_type == "green_candle":
        if candle_close <= candle_open:
            return "NONE"

    elif confirmation_type == "break_prev_high":
        if index < 1:
            return "NONE"

        previous_high = float(df.iloc[index - 1]["high"])

        if candle_close <= previous_high:
            return "NONE"

    elif confirmation_type == "lower_wick_rejection":
        candle_body = abs(candle_close - candle_open)
        lower_wick = min(candle_open, candle_close) - candle_low

        if candle_body <= 0:
            return "NONE"

        if lower_wick < candle_body:
            return "NONE"

    elif confirmation_type == "green_and_break_prev_high":
        if index < 1:
            return "NONE"

        previous_high = float(df.iloc[index - 1]["high"])

        if candle_close <= candle_open:
            return "NONE"

        if candle_close <= previous_high:
            return "NONE"

    elif confirmation_type == "green_and_lower_wick":
        candle_body = abs(candle_close - candle_open)
        lower_wick = min(candle_open, candle_close) - candle_low

        if candle_close <= candle_open:
            return "NONE"

        if candle_body <= 0:
            return "NONE"

        if lower_wick < candle_body:
            return "NONE"

    else:
        raise ValueError(f"Unknown confirmation_type: {confirmation_type}")

    if use_mtf_filter:
        regime_1h = row.get("regime_1h", "UNKNOWN")
        regime_4h = row.get("regime_4h", "UNKNOWN")

        if not long_allowed_by_mtf_regime(regime_1h, regime_4h):
            return "NONE"

    return "LONG"


def make_strategy(
    lookback_bars: int,
    fib_entry_low: float,
    fib_entry_high: float,
    min_impulse_pct: float,
    confirmation_type: str,
    use_mtf_filter: bool,
):
    def strategy_func(df, index: int, config=None) -> str:
        return long_signal_variant(
            df=df,
            index=index,
            lookback_bars=lookback_bars,
            fib_entry_low=fib_entry_low,
            fib_entry_high=fib_entry_high,
            min_impulse_pct=min_impulse_pct,
            confirmation_type=confirmation_type,
            use_mtf_filter=use_mtf_filter,
        )

    return strategy_func


def summarize_result(
    variant_name: str,
    trades_df: pd.DataFrame,
    summary: dict,
    params: dict,
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
        avg_holding_bars = float(trades_df["holding_bars"].mean())

    profit_factor = summary.get("profit_factor", None)

    if profit_factor is None:
        pf_value = 0.0
    else:
        pf_value = float(profit_factor)

    total_return_pct = float(summary.get("total_return_pct", 0.0))
    win_rate = float(summary.get("win_rate", 0.0))
    max_drawdown_pct = float(summary.get("max_drawdown_pct", 0.0))
    expectancy = float(summary.get("expectancy", 0.0))

    # Score investigativo simple.
    # No es señal operativa.
    quality_score = (
        (total_return_pct * 100)
        + (pf_value * 5)
        + (win_rate * 10)
        + (expectancy * 0.20)
        + (max_drawdown_pct * 100)
    )

    return {
        "variant_name": variant_name,
        "lookback_bars": params["lookback_bars"],
        "fib_entry_low": params["fib_entry_low"],
        "fib_entry_high": params["fib_entry_high"],
        "min_impulse_pct": params["min_impulse_pct"],
        "confirmation_type": params["confirmation_type"],
        "use_mtf_filter": params["use_mtf_filter"],
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
    pf = row["profit_factor"]
    win_rate = float(row["win_rate"])
    max_drawdown_pct = float(row["max_drawdown_pct"])

    if trades < 5:
        return "INSUFFICIENT_TRADES"

    if pf is None or pd.isna(pf):
        return "INVALID_PF"

    pf = float(pf)

    if total_return_pct > 0.05 and pf >= 1.5 and win_rate >= 0.50 and max_drawdown_pct > -0.10:
        return "PROMISING"

    if total_return_pct > 0 and pf >= 1.1:
        return "WEAK_PROMISING"

    if total_return_pct > -0.03 and pf >= 0.9:
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

    config = build_config()

    fib_zones = [
        (0.236, 0.500),
        (0.382, 0.618),
        (0.500, 0.618),
        (0.500, 0.786),
        (0.618, 0.786),
    ]

    confirmation_types = [
        "green_candle",
        "break_prev_high",
        "lower_wick_rejection",
        "green_and_break_prev_high",
        "green_and_lower_wick",
    ]

    mtf_options = [False, True]

    lookback_options = [48]
    impulse_options = [0.02]

    results = []

    print("LONG V2 RESEARCH — FIB ZONES + CONFIRMATION")
    print("=" * 100)
    print("Dataset: BTCUSDT spot, 2024-01-01 a 2024-03-01")
    print()

    for lookback_bars in lookback_options:
        for min_impulse_pct in impulse_options:
            for fib_low, fib_high in fib_zones:
                for confirmation_type in confirmation_types:
                    for use_mtf_filter in mtf_options:
                        params = {
                            "lookback_bars": lookback_bars,
                            "fib_entry_low": fib_low,
                            "fib_entry_high": fib_high,
                            "min_impulse_pct": min_impulse_pct,
                            "confirmation_type": confirmation_type,
                            "use_mtf_filter": use_mtf_filter,
                        }

                        variant_name = (
                            f"LONG_FIB_{fib_low:.3f}_{fib_high:.3f}_"
                            f"{confirmation_type}_"
                            f"{'MTF' if use_mtf_filter else 'NO_MTF'}"
                        )

                        strategy_func = make_strategy(**params)

                        trades_df, summary = run_backtest_v3(
                            csv_path=enriched_csv,
                            config=config,
                            output_dir=Path("reports"),
                            strategy_func=strategy_func,
                        )

                        result = summarize_result(
                            variant_name=variant_name,
                            trades_df=trades_df,
                            summary=summary,
                            params=params,
                        )

                        results.append(result)

                        print(
                            f"{variant_name} | "
                            f"trades={result['total_trades']} | "
                            f"return={result['total_return_pct']:.2%} | "
                            f"wr={result['win_rate']:.2%} | "
                            f"pf={result['profit_factor']} | "
                            f"mdd={result['max_drawdown_pct']:.2%}"
                        )

    results_df = pd.DataFrame(results)
    results_df["research_status"] = results_df.apply(classify_result, axis=1)

    output_path = Path("reports") / "long_v2_research_results.csv"
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
            ]
        ]
        .sort_values(by=["profit_factor", "total_trades"], ascending=[False, False])
        .head(15)
        .to_string(index=False)
    )

    print()
    print("PROMEDIO POR ZONA FIB")
    print("=" * 100)
    print(
        results_df.groupby(["fib_entry_low", "fib_entry_high"])
        .agg(
            variants=("variant_name", "count"),
            avg_trades=("total_trades", "mean"),
            avg_return=("total_return_pct", "mean"),
            avg_win_rate=("win_rate", "mean"),
            avg_profit_factor=("profit_factor", "mean"),
            avg_max_drawdown=("max_drawdown_pct", "mean"),
            best_quality_score=("quality_score", "max"),
        )
        .reset_index()
        .sort_values(by="best_quality_score", ascending=False)
        .to_string(index=False)
    )

    print()
    print("PROMEDIO POR CONFIRMACION")
    print("=" * 100)
    print(
        results_df.groupby(["confirmation_type"])
        .agg(
            variants=("variant_name", "count"),
            avg_trades=("total_trades", "mean"),
            avg_return=("total_return_pct", "mean"),
            avg_win_rate=("win_rate", "mean"),
            avg_profit_factor=("profit_factor", "mean"),
            avg_max_drawdown=("max_drawdown_pct", "mean"),
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