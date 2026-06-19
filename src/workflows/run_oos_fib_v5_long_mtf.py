from pathlib import Path
import pandas as pd

from src.backtesting.backtesting_engine_v3 import (
    BacktestConfig,
    run_backtest_v3,
    format_summary_text,
)

from src.market_structure.mtf_regime_filter import enrich_15m_with_mtf_regime
from src.strategies.fib_v5_long_strategy import fib_v5_long_signal
from src.strategies.fib_v5_long_mtf_strategy import fib_v5_long_with_mtf_filter
from src.strategies.fib_v5_mtf_strategy import fib_v5_short_with_mtf_filter


def build_config(direction_mode: str) -> BacktestConfig:
    return BacktestConfig(
        initial_capital=1000.0,
        risk_per_trade=0.01,
        risk_reward=2.5,
        fee_rate=0.001,
        spread_rate=0.0002,
        atr_period=14,
        atr_multiplier=1.25,
        max_holding_bars=48,
        direction_mode=direction_mode,
    )


def fib_v5_long_base_strategy(df, index: int, config=None) -> str:
    return fib_v5_long_signal(
        df=df,
        index=index,
        config=config,
        lookback_bars=48,
        fib_entry_low=0.618,
        fib_entry_high=0.786,
        min_impulse_pct=0.02,
        require_bullish_confirmation=True,
        require_rejection_wick=False,
    )


def summarize(label: str, trades_df: pd.DataFrame, summary: dict) -> dict:
    return {
        "label": label,
        "total_trades": summary.get("total_trades", 0),
        "wins": summary.get("wins", 0),
        "losses": summary.get("losses", 0),
        "ending_capital": summary.get("ending_capital", 1000.0),
        "total_return_pct": summary.get("total_return_pct", 0.0),
        "win_rate": summary.get("win_rate", 0.0),
        "profit_factor": summary.get("profit_factor", None),
        "expectancy": summary.get("expectancy", 0.0),
        "max_drawdown_pct": summary.get("max_drawdown_pct", 0.0),
        "take_profit_count": int((trades_df["exit_reason"] == "TAKE_PROFIT").sum())
        if len(trades_df) > 0
        else 0,
        "stop_loss_count": int((trades_df["exit_reason"] == "STOP_LOSS").sum())
        if len(trades_df) > 0
        else 0,
        "max_holding_exit_count": int(
            (trades_df["exit_reason"] == "MAX_HOLDING_EXIT").sum()
        )
        if len(trades_df) > 0
        else 0,
    }


def main():
    enriched_csv = Path("reports") / "oos_btcusdt_15m_with_mtf_regime.csv"

    enrich_15m_with_mtf_regime(
        entry_csv_path=Path("data") / "oos_btcusdt_15m_2024_01_03.csv",
        h1_csv_path=Path("data") / "oos_btcusdt_1h_2024_01_03.csv",
        h4_csv_path=Path("data") / "oos_btcusdt_4h_2024_01_03.csv",
        output_path=enriched_csv,
    )

    print("VALIDACIÓN OOS — FIB V5 LONG ESPEJO")
    print("=" * 80)
    print("Dataset: BTCUSDT spot, 2024-01-01 a 2024-03-01")
    print()

    # Benchmark previo: SHORT + MTF en mercado alcista
    short_mtf_trades, short_mtf_summary = run_backtest_v3(
        csv_path=enriched_csv,
        config=build_config(direction_mode="short_only"),
        output_dir=Path("reports"),
        strategy_func=fib_v5_short_with_mtf_filter,
    )

    # LONG base
    long_base_trades, long_base_summary = run_backtest_v3(
        csv_path=enriched_csv,
        config=build_config(direction_mode="long_only"),
        output_dir=Path("reports"),
        strategy_func=fib_v5_long_base_strategy,
    )

    # LONG + MTF
    long_mtf_trades, long_mtf_summary = run_backtest_v3(
        csv_path=enriched_csv,
        config=build_config(direction_mode="long_only"),
        output_dir=Path("reports"),
        strategy_func=fib_v5_long_with_mtf_filter,
    )

    results = [
        summarize("OOS_SHORT_FIB_V5_MTF", short_mtf_trades, short_mtf_summary),
        summarize("OOS_LONG_FIB_V5_BASE", long_base_trades, long_base_summary),
        summarize("OOS_LONG_FIB_V5_MTF", long_mtf_trades, long_mtf_summary),
    ]

    results_df = pd.DataFrame(results)

    output_path = Path("reports") / "oos_fib_v5_long_mtf_validation.csv"
    results_df.to_csv(output_path, index=False)

    print("RESULTADO SHORT FIB V5 + MTF")
    print("-" * 80)
    print(format_summary_text(short_mtf_summary))

    print()
    print("RESULTADO LONG FIB V5 BASE")
    print("-" * 80)
    print(format_summary_text(long_base_summary))

    print()
    print("RESULTADO LONG FIB V5 + MTF")
    print("-" * 80)
    print(format_summary_text(long_mtf_summary))

    print()
    print("TABLA VALIDACIÓN LONG")
    print("=" * 80)
    print(results_df.to_string(index=False))

    print()
    print(f"Archivo generado: {output_path}")


if __name__ == "__main__":
    main()