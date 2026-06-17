from pathlib import Path
import pandas as pd

from src.backtesting.backtesting_engine_v3 import (
    BacktestConfig,
    run_backtest_v3,
)

from src.strategies.fib_v5_strategy import fib_v5_short_signal


def make_strategy(
    lookback_bars,
    fib_entry_low,
    fib_entry_high,
    min_impulse_pct,
    require_bearish_confirmation,
    require_rejection_wick,
):
    def strategy(df, index, config):
        return fib_v5_short_signal(
            df=df,
            index=index,
            config=config,
            lookback_bars=lookback_bars,
            fib_entry_low=fib_entry_low,
            fib_entry_high=fib_entry_high,
            min_impulse_pct=min_impulse_pct,
            require_bearish_confirmation=require_bearish_confirmation,
            require_rejection_wick=require_rejection_wick,
        )

    return strategy


def main():
    csv_path = Path("data") / "btcusdt_15m.csv"
    output_dir = Path("reports")

    results = []

    lookback_options = [48, 72, 96, 144]
    fib_zones = [
        (0.500, 0.618),
        (0.618, 0.786),
        (0.618, 0.886),
        (0.500, 0.786),
    ]
    impulse_options = [0.01, 0.015, 0.02]
    atr_multipliers = [1.0, 1.25, 1.5, 2.0]
    risk_rewards = [1.5, 2.0, 2.5]
    bearish_confirmation_options = [True]
    rejection_wick_options = [False, True]

    total_tests = (
        len(lookback_options)
        * len(fib_zones)
        * len(impulse_options)
        * len(atr_multipliers)
        * len(risk_rewards)
        * len(bearish_confirmation_options)
        * len(rejection_wick_options)
    )

    test_number = 0

    for lookback in lookback_options:
        for fib_low, fib_high in fib_zones:
            for impulse in impulse_options:
                for atr_multiplier in atr_multipliers:
                    for rr in risk_rewards:
                        for bearish_confirmation in bearish_confirmation_options:
                            for rejection_wick in rejection_wick_options:
                                test_number += 1

                                config = BacktestConfig(
                                    initial_capital=1000.0,
                                    risk_per_trade=0.01,
                                    risk_reward=rr,
                                    fee_rate=0.001,
                                    spread_rate=0.0002,
                                    atr_period=14,
                                    atr_multiplier=atr_multiplier,
                                    max_holding_bars=48,
                                    direction_mode="short_only",
                                )

                                strategy_func = make_strategy(
                                    lookback_bars=lookback,
                                    fib_entry_low=fib_low,
                                    fib_entry_high=fib_high,
                                    min_impulse_pct=impulse,
                                    require_bearish_confirmation=bearish_confirmation,
                                    require_rejection_wick=rejection_wick,
                                )

                                trades_df, summary = run_backtest_v3(
                                    csv_path=csv_path,
                                    config=config,
                                    output_dir=output_dir,
                                    strategy_func=strategy_func,
                                )

                                row = {
                                    "test_number": test_number,
                                    "lookback_bars": lookback,
                                    "fib_entry_low": fib_low,
                                    "fib_entry_high": fib_high,
                                    "min_impulse_pct": impulse,
                                    "atr_multiplier": atr_multiplier,
                                    "risk_reward": rr,
                                    "require_bearish_confirmation": bearish_confirmation,
                                    "require_rejection_wick": rejection_wick,
                                    "total_trades": summary.get("total_trades", 0),
                                    "ending_capital": summary.get("ending_capital", 1000.0),
                                    "total_return_pct": summary.get("total_return_pct", 0.0),
                                    "win_rate": summary.get("win_rate", 0.0),
                                    "profit_factor": summary.get("profit_factor", None),
                                    "expectancy": summary.get("expectancy", 0.0),
                                    "max_drawdown_pct": summary.get("max_drawdown_pct", 0.0),
                                }

                                results.append(row)

                                print(
                                    f"[{test_number}/{total_tests}] "
                                    f"trades={row['total_trades']} "
                                    f"return={row['total_return_pct']:.2%} "
                                    f"pf={row['profit_factor']} "
                                    f"lookback={lookback} "
                                    f"fib={fib_low}-{fib_high} "
                                    f"impulse={impulse} "
                                    f"atr={atr_multiplier} "
                                    f"rr={rr} "
                                    f"wick={rejection_wick}"
                                )

    results_df = pd.DataFrame(results)

    results_df = results_df.sort_values(
        by=["total_return_pct", "profit_factor", "total_trades"],
        ascending=[False, False, False],
    )

    output_path = output_dir / "backtest_v3_fib_sweep_results.csv"
    results_df.to_csv(output_path, index=False)

    print()
    print("TOP 10 RESULTADOS")
    print(
        results_df.head(10)[
            [
                "total_trades",
                "ending_capital",
                "total_return_pct",
                "win_rate",
                "profit_factor",
                "expectancy",
                "max_drawdown_pct",
                "lookback_bars",
                "fib_entry_low",
                "fib_entry_high",
                "min_impulse_pct",
                "atr_multiplier",
                "risk_reward",
                "require_rejection_wick",
            ]
        ].to_string(index=False)
    )

    print()
    print(f"Archivo generado: {output_path}")


if __name__ == "__main__":
    main()