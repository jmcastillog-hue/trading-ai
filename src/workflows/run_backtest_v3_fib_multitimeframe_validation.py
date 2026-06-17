from pathlib import Path
import pandas as pd

from src.backtesting.backtesting_engine_v3 import (
    BacktestConfig,
    run_backtest_v3,
)

from src.strategies.fib_v5_strategy import fib_v5_short_signal


def best_fib_v5_strategy(df, index, config):
    """
    Configuración candidata FIB V5 encontrada en Fase 1.1.

    Se mantiene igual en todos los timeframes para evitar sobreoptimización.
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


def run_timeframe_validation(
    timeframe: str,
    csv_path: Path,
    total_candles: int = 5000,
) -> dict:
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

    result = {
        "symbol": "BTCUSDT",
        "timeframe": timeframe,
        "csv_path": str(csv_path),
        "total_candles": total_candles,
        "total_trades": summary.get("total_trades", 0),
        "ending_capital": summary.get("ending_capital", 1000.0),
        "total_return_pct": summary.get("total_return_pct", 0.0),
        "win_rate": summary.get("win_rate", 0.0),
        "profit_factor": summary.get("profit_factor", None),
        "expectancy": summary.get("expectancy", 0.0),
        "max_drawdown_pct": summary.get("max_drawdown_pct", 0.0),
    }

    if len(trades_df) > 0:
        result["avg_holding_bars"] = trades_df["holding_bars"].mean()
        result["max_holding_bars_observed"] = trades_df["holding_bars"].max()
        result["take_profit_count"] = int((trades_df["exit_reason"] == "TAKE_PROFIT").sum())
        result["stop_loss_count"] = int((trades_df["exit_reason"] == "STOP_LOSS").sum())
        result["max_holding_exit_count"] = int(
            (trades_df["exit_reason"] == "MAX_HOLDING_EXIT").sum()
        )
    else:
        result["avg_holding_bars"] = 0
        result["max_holding_bars_observed"] = 0
        result["take_profit_count"] = 0
        result["stop_loss_count"] = 0
        result["max_holding_exit_count"] = 0

    return result


def main():
    datasets = [
        {
            "timeframe": "15m",
            "csv_path": Path("data") / "btcusdt_15m_validation.csv",
            "total_candles": 5000,
        },
        {
            "timeframe": "30m",
            "csv_path": Path("data") / "btcusdt_30m_validation.csv",
            "total_candles": 5000,
        },
        {
            "timeframe": "1h",
            "csv_path": Path("data") / "btcusdt_1h_validation.csv",
            "total_candles": 5000,
        },
        {
            "timeframe": "4h",
            "csv_path": Path("data") / "btcusdt_4h_validation.csv",
            "total_candles": 5000,
        },
    ]

    print("VALIDACIÓN MULTI-TIMEFRAME FIB V5")
    print("=" * 70)
    print("Configuración fija:")
    print("- lookback_bars: 48")
    print("- fib zone: 0.618 - 0.786")
    print("- min_impulse_pct: 0.02")
    print("- atr_multiplier: 1.25")
    print("- risk_reward: 2.5")
    print("- max_holding_bars: 48")
    print("- direction: SHORT only")
    print("=" * 70)
    print()

    results = []

    for dataset in datasets:
        timeframe = dataset["timeframe"]
        csv_path = dataset["csv_path"]

        if not csv_path.exists():
            raise FileNotFoundError(
                f"No existe {csv_path}. "
                "Primero ejecuta: python -m src.workflows.download_multitimeframe_validation_data"
            )

        print(f"Ejecutando validación {timeframe}...")
        result = run_timeframe_validation(
            timeframe=timeframe,
            csv_path=csv_path,
            total_candles=dataset["total_candles"],
        )

        results.append(result)

        print(
            f"{timeframe} | "
            f"trades={result['total_trades']} | "
            f"return={result['total_return_pct']:.2%} | "
            f"win_rate={result['win_rate']:.2%} | "
            f"pf={result['profit_factor']} | "
            f"mdd={result['max_drawdown_pct']:.2%}"
        )

    results_df = pd.DataFrame(results)

    output_path = Path("reports") / "backtest_v3_fib_multitimeframe_validation.csv"
    results_df.to_csv(output_path, index=False)

    print()
    print("RESUMEN MULTI-TIMEFRAME")
    print("=" * 70)
    print(
        results_df[
            [
                "timeframe",
                "total_trades",
                "ending_capital",
                "total_return_pct",
                "win_rate",
                "profit_factor",
                "expectancy",
                "max_drawdown_pct",
                "avg_holding_bars",
                "take_profit_count",
                "stop_loss_count",
                "max_holding_exit_count",
            ]
        ].to_string(index=False)
    )

    print()
    print(f"Archivo generado: {output_path}")


if __name__ == "__main__":
    main()