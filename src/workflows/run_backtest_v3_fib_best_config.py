from pathlib import Path

from src.backtesting.backtesting_engine_v3 import (
    BacktestConfig,
    run_backtest_v3,
    format_summary_text,
)

from src.strategies.fib_v5_strategy import fib_v5_short_signal


def best_fib_v5_strategy(df, index, config):
    """
    Mejor configuración encontrada en el primer sweep FIB V5.

    Resultado inicial observado:
    - total_trades: 10
    - total_return_pct: 13.13%
    - win_rate: 80%
    - profit_factor: 4.87
    - max_drawdown_pct: -1.49%

    Nota:
    Esta configuración todavía debe validarse con más datos.
    """

    return fib_v5_short_signal(
        df=df,
        index=index,
        config=config,
        lookback_bars=48,
        fib_entry_low=0.618,
        fib_entry_high=0.786,
        min_impulse_pct=0.02,
        require_bearish_confirmation=True,
        require_rejection_wick=False,
    )


def main():
    csv_path = Path("data") / "btcusdt_15m.csv"

    config = BacktestConfig(
        initial_capital=1000.0,
        risk_per_trade=0.01,
        risk_reward=2.5,
        fee_rate=0.001,
        spread_rate=0.0002,
        atr_period=14,
        atr_multiplier=1.25,
        max_holding_bars=48,
        direction_mode="short_only",
    )

    trades_df, summary = run_backtest_v3(
        csv_path=csv_path,
        config=config,
        output_dir=Path("reports"),
        strategy_func=best_fib_v5_strategy,
    )

    print(format_summary_text(summary))
    print()
    print("Mejor configuración FIB V5 probada:")
    print("- lookback_bars: 48")
    print("- fib zone: 0.618 - 0.786")
    print("- min_impulse_pct: 0.02")
    print("- atr_multiplier: 1.25")
    print("- risk_reward: 2.5")
    print("- require_rejection_wick: False")
    print()
    print("Archivos generados:")
    print("- reports/backtest_v3_trades.csv")
    print("- reports/backtest_v3_summary.json")
    print("- reports/backtest_v3_summary.txt")
    print()
    print(f"Trades generados: {len(trades_df)}")


if __name__ == "__main__":
    main()