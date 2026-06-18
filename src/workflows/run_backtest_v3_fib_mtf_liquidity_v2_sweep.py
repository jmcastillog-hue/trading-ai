from pathlib import Path
import pandas as pd

from src.backtesting.backtesting_engine_v3 import (
    BacktestConfig,
    run_backtest_v3,
)

from src.market_structure.mtf_regime_filter import enrich_15m_with_mtf_regime
from src.strategies.fib_v5_mtf_strategy import fib_v5_short_with_mtf_filter
from src.liquidity.liquidity_zones_v2 import short_allowed_by_liquidity_zone_v2


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


def make_strategy(
    min_atr_distance: float,
    lookback_bars: int,
    equal_low_tolerance_atr: float,
    min_touches: int,
):
    def strategy(df, index: int, config=None) -> str:
        mtf_signal = fib_v5_short_with_mtf_filter(
            df=df,
            index=index,
            config=config,
        )

        if mtf_signal != "SHORT":
            return "NONE"

        liquidity_ok = short_allowed_by_liquidity_zone_v2(
            df=df,
            index=index,
            min_atr_distance=min_atr_distance,
            lookback_bars=lookback_bars,
            left_bars=2,
            right_bars=2,
            equal_low_tolerance_atr=equal_low_tolerance_atr,
            min_touches=min_touches,
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

    # Benchmark actual: FIB V5 + MTF sin filtro de liquidez
    benchmark_trades, benchmark_summary = run_backtest_v3(
        csv_path=enriched_csv,
        config=config,
        output_dir=Path("reports"),
        strategy_func=fib_v5_short_with_mtf_filter,
    )

    print("SWEEP — FIB V5 + MTF + LIQUIDITY V2")
    print("=" * 90)
    print("BENCHMARK FIB V5 + MTF")
    print("-" * 90)
    print(f"Trades: {benchmark_summary.get('total_trades', 0)}")
    print(f"Return: {benchmark_summary.get('total_return_pct', 0):.2%}")
    print(f"Win rate: {benchmark_summary.get('win_rate', 0):.2%}")
    print(f"Profit factor: {benchmark_summary.get('profit_factor', None)}")
    print(f"Max drawdown: {benchmark_summary.get('max_drawdown_pct', 0):.2%}")
    print("=" * 90)

    min_atr_options = [0.8, 1.0, 1.2, 1.5, 2.0]
    lookback_options = [96, 144, 192]
    tolerance_options = [0.15, 0.25, 0.35]
    min_touches_options = [1, 2, 3]

    results = []

    for lookback_bars in lookback_options:
        for min_atr_distance in min_atr_options:
            for tolerance in tolerance_options:
                for min_touches in min_touches_options:
                    strategy = make_strategy(
                        min_atr_distance=min_atr_distance,
                        lookback_bars=lookback_bars,
                        equal_low_tolerance_atr=tolerance,
                        min_touches=min_touches,
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
                        "equal_low_tolerance_atr": tolerance,
                        "min_touches": min_touches,
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
                        f"lb={lookback_bars:>3} | "
                        f"atr={min_atr_distance:>3} | "
                        f"tol={tolerance:>4} | "
                        f"touches={min_touches} | "
                        f"trades={result['total_trades']:>2} | "
                        f"return={result['total_return_pct']:.2%} | "
                        f"wr={result['win_rate']:.2%} | "
                        f"pf={result['profit_factor']} | "
                        f"mdd={result['max_drawdown_pct']:.2%}"
                    )

    results_df = pd.DataFrame(results)

    output_path = Path("reports") / "backtest_v3_fib_mtf_liquidity_v2_sweep.csv"
    results_df.to_csv(output_path, index=False)

    print()
    print("TOP RESULTADOS POR PROFIT FACTOR")
    print("=" * 90)
    print(
        results_df.sort_values(
            by=["profit_factor", "total_return_pct"],
            ascending=[False, False],
            na_position="last",
        )
        .head(20)
        .to_string(index=False)
    )

    print()
    print("TOP RESULTADOS POR RETORNO")
    print("=" * 90)
    print(
        results_df.sort_values(
            by=["total_return_pct", "profit_factor"],
            ascending=[False, False],
            na_position="last",
        )
        .head(20)
        .to_string(index=False)
    )

    print()
    print("RESULTADOS BALANCEADOS")
    print("=" * 90)
    balanced_df = results_df[
        (results_df["total_trades"] >= 8)
        & (results_df["profit_factor"] >= 3.0)
        & (results_df["max_drawdown_pct"] >= -0.02)
    ].copy()

    if len(balanced_df) > 0:
        print(
            balanced_df.sort_values(
                by=["total_return_pct", "profit_factor"],
                ascending=[False, False],
                na_position="last",
            )
            .head(20)
            .to_string(index=False)
        )
    else:
        print("No hubo resultados balanceados con trades >= 8, PF >= 3.0 y MDD >= -2%.")

    print()
    print(f"Archivo generado: {output_path}")


if __name__ == "__main__":
    main()