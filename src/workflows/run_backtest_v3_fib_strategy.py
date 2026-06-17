from pathlib import Path

from src.backtesting.backtesting_engine_v3 import (
    BacktestConfig,
    run_backtest_v3,
    format_summary_text,
)

from src.strategies.fib_v5_strategy import fib_v5_short_signal


def main():
    csv_path = Path("data") / "btcusdt_15m.csv"

    config = BacktestConfig(
        initial_capital=1000.0,
        risk_per_trade=0.01,
        risk_reward=2.0,
        fee_rate=0.001,
        spread_rate=0.0002,
        atr_period=14,
        atr_multiplier=1.5,
        max_holding_bars=48,
        direction_mode="short_only",
    )

    trades_df, summary = run_backtest_v3(
        csv_path=csv_path,
        config=config,
        output_dir=Path("reports"),
        strategy_func=fib_v5_short_signal,
    )

    print(format_summary_text(summary))
    print()
    print("Archivos generados:")
    print("- reports/backtest_v3_trades.csv")
    print("- reports/backtest_v3_summary.json")
    print("- reports/backtest_v3_summary.txt")
    print()
    print(f"Trades generados: {len(trades_df)}")


if __name__ == "__main__":
    main()