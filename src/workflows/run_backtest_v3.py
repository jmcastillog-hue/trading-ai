from pathlib import Path

from src.backtesting.backtesting_engine_v3 import (
    BacktestConfig,
    run_backtest_v3,
    format_summary_text,
)


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
        direction_mode="both",
    )

    trades_df, summary = run_backtest_v3(
        csv_path=csv_path,
        config=config,
        output_dir=Path("reports"),
    )

    print(format_summary_text(summary))
    print()
    print("Archivos generados:")
    print("- reports/backtest_v3_trades.csv")
    print("- reports/backtest_v3_summary.json")
    print("- reports/backtest_v3_summary.txt")


if __name__ == "__main__":
    main()