from pathlib import Path
import pandas as pd

from src.backtesting.backtesting_engine_v3 import (
    BacktestConfig,
    run_backtest_v3,
)

from src.market_structure.mtf_regime_filter import enrich_15m_with_mtf_regime
from src.strategies.fib_v5_mtf_strategy import fib_v5_short_with_mtf_filter
from src.liquidity.liquidity_context_filter import short_allowed_by_liquidity_space


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
        direction_mode="short_only",
    )


def make_strategy(min_atr_distance: float, lookback_bars: int = 96):
    def strategy(df, index: int, config=None) -> str:
        mtf_signal = fib_v5_short_with_mtf_filter(
            df=df,
            index=index,
            config=config,
        )

        if mtf_signal != "SHORT":
            return "NONE"

        liquidity_ok = short_allowed_by_liquidity_space(
            df=df,
            index=index,
            min_atr_distance=min_atr_distance,
            lookback_bars=lookback_bars,
        )

        if not liquidity_ok:
            return "NONE"

        return "SHORT"

    return strategy


def main():
    enriched_csv = Path("reports") / "btcusdt_15m_with_mtf_regime.csv"

    enrich_15m_with_mtf_regime(
        entry_csv_path=Path("data") / "btcusdt_15m_validation.csv",
        h1_csv_path=Path("data") / "btcusdt_1h_validation.csv",
        h4_csv_path=Path("data") / "btcusdt_4h_validation.csv",
        output_path=enriched_csv,
    )

    config = build_config()

    min_atr_options = [
        1.0,
        1.5,
        2.0,
        2.5,
        3.0,
        4.0,
        5.0,
        6.0,
        8.0,
        10.0,
    ]

    lookback_options = [
        48,
        96,
        144,
    ]

    results = []

    print("SWEEP — FIB V5 + MTF + LIQUIDITY FILTER")
    print("=" * 80)

    for lookback_bars in lookback_options:
        for min_atr_distance in min_atr_options:
            strategy = make_strategy(
                min_atr_distance=min_atr_distance,
                lookback_bars=lookback_bars,
            )

            trades_df, summary = run_backtest_v3(
                csv_path=enriched_csv,
                config=config,
                output_dir=Path("reports"),
                strategy_func=strategy,
            )

            result = {
                "lookback_bars": lookback_bars,
                "min_atr_distance": min_atr_distance,
                "total_trades": summary.get("total_trades", 0),
                "ending_capital": summary.get("ending_capital", 1000.0),
                "total_return_pct": summary.get("total_return_pct", 0.0),
                "win_rate": summary.get("win_rate", 0.0),
                "profit_factor": summary.get("profit_factor", None),
                "expectancy": summary.get("expectancy", 0.0),
                "max_drawdown_pct": summary.get("max_drawdown_pct", 0.0),
            }

            results.append(result)

            print(
                f"lookback={lookback_bars:>3} | "
                f"min_atr={min_atr_distance:>4} | "
                f"trades={result['total_trades']:>2} | "
                f"return={result['total_return_pct']:.2%} | "
                f"win_rate={result['win_rate']:.2%} | "
                f"pf={result['profit_factor']} | "
                f"mdd={result['max_drawdown_pct']:.2%}"
            )

    results_df = pd.DataFrame(results)

    output_path = Path("reports") / "backtest_v3_fib_mtf_liquidity_sweep.csv"
    results_df.to_csv(output_path, index=False)

    print()
    print("TOP RESULTADOS POR PROFIT FACTOR")
    print("=" * 80)
    print(
        results_df.sort_values(
            by=["profit_factor", "total_return_pct"],
            ascending=[False, False],
            na_position="last",
        )
        .head(15)
        .to_string(index=False)
    )

    print()
    print("TOP RESULTADOS POR RETORNO")
    print("=" * 80)
    print(
        results_df.sort_values(
            by=["total_return_pct", "profit_factor"],
            ascending=[False, False],
            na_position="last",
        )
        .head(15)
        .to_string(index=False)
    )

    print()
    print(f"Archivo generado: {output_path}")


if __name__ == "__main__":
    main()