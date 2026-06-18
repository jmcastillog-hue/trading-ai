from pathlib import Path
import pandas as pd

from src.backtesting.backtesting_engine_v3 import (
    BacktestConfig,
    run_backtest_v3,
)

from src.market_structure.mtf_regime_filter import enrich_15m_with_mtf_regime

from src.strategies.fib_v5_strategy import fib_v5_short_signal
from src.strategies.fib_v5_mtf_strategy import fib_v5_short_with_mtf_filter
from src.strategies.fib_v5_mtf_liquidity_strategy import (
    fib_v5_short_with_mtf_and_liquidity_filter,
)
from src.strategies.fib_v5_mtf_liquidity_v2_strategy import (
    fib_v5_short_with_mtf_and_liquidity_v2_filter,
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
        direction_mode="short_only",
    )


def fib_v5_base_strategy(df, index: int, config=None) -> str:
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


def summarize_strategy(
    strategy_name: str,
    strategy_func,
    csv_path: Path,
    config: BacktestConfig,
) -> dict:
    trades_df, summary = run_backtest_v3(
        csv_path=csv_path,
        config=config,
        output_dir=Path("reports"),
        strategy_func=strategy_func,
    )

    total_trades = int(summary.get("total_trades", 0))
    wins = int(summary.get("wins", 0))
    losses = int(summary.get("losses", 0))

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

    return {
        "strategy_name": strategy_name,
        "total_trades": total_trades,
        "wins": wins,
        "losses": losses,
        "ending_capital": summary.get("ending_capital", 1000.0),
        "total_return_pct": summary.get("total_return_pct", 0.0),
        "win_rate": summary.get("win_rate", 0.0),
        "profit_factor": summary.get("profit_factor", None),
        "expectancy": summary.get("expectancy", 0.0),
        "average_win": summary.get("average_win", 0.0),
        "average_loss": summary.get("average_loss", 0.0),
        "max_drawdown_pct": summary.get("max_drawdown_pct", 0.0),
        "take_profit_count": take_profit_count,
        "stop_loss_count": stop_loss_count,
        "max_holding_exit_count": max_holding_exit_count,
        "avg_holding_bars": avg_holding_bars,
    }


def classify_candidate(row) -> str:
    trades = row["total_trades"]
    ret = row["total_return_pct"]
    pf = row["profit_factor"]
    mdd = row["max_drawdown_pct"]
    wr = row["win_rate"]

    if trades < 5:
        return "INSUFFICIENT_TRADES"

    if ret > 0.10 and pf >= 3.0 and wr >= 0.70 and mdd >= -0.03:
        return "STRONG_CANDIDATE"

    if ret > 0.05 and pf >= 2.0 and wr >= 0.60 and mdd >= -0.05:
        return "VALID_CANDIDATE"

    if ret > 0 and pf >= 1.2:
        return "WEAK_CANDIDATE"

    return "REJECTED"


def main():
    enriched_csv = Path("reports") / "btcusdt_15m_with_mtf_regime.csv"

    enrich_15m_with_mtf_regime(
        entry_csv_path=Path("data") / "btcusdt_15m_validation.csv",
        h1_csv_path=Path("data") / "btcusdt_1h_validation.csv",
        h4_csv_path=Path("data") / "btcusdt_4h_validation.csv",
        output_path=enriched_csv,
    )

    config = build_config()

    strategies = [
        {
            "strategy_name": "FIB_V5_BASE",
            "strategy_func": fib_v5_base_strategy,
        },
        {
            "strategy_name": "FIB_V5_MTF",
            "strategy_func": fib_v5_short_with_mtf_filter,
        },
        {
            "strategy_name": "FIB_V5_MTF_LIQUIDITY_V1",
            "strategy_func": fib_v5_short_with_mtf_and_liquidity_filter,
        },
        {
            "strategy_name": "FIB_V5_MTF_LIQUIDITY_V2",
            "strategy_func": fib_v5_short_with_mtf_and_liquidity_v2_filter,
        },
    ]

    results = []

    print("COMPARACIÓN DE ESTRATEGIAS CANDIDATAS — FIB V5")
    print("=" * 90)

    for item in strategies:
        strategy_name = item["strategy_name"]
        strategy_func = item["strategy_func"]

        print(f"Ejecutando: {strategy_name}")

        result = summarize_strategy(
            strategy_name=strategy_name,
            strategy_func=strategy_func,
            csv_path=enriched_csv,
            config=config,
        )

        results.append(result)

        print(
            f"{strategy_name} | "
            f"trades={result['total_trades']} | "
            f"return={result['total_return_pct']:.2%} | "
            f"wr={result['win_rate']:.2%} | "
            f"pf={result['profit_factor']} | "
            f"mdd={result['max_drawdown_pct']:.2%}"
        )

    results_df = pd.DataFrame(results)
    results_df["candidate_status"] = results_df.apply(classify_candidate, axis=1)

    # Ranking simple: prioriza retorno positivo, PF, drawdown y cantidad razonable.
    results_df["quality_score"] = (
        (results_df["total_return_pct"] * 100)
        + (results_df["profit_factor"].fillna(0) * 5)
        + (results_df["win_rate"] * 10)
        + (results_df["max_drawdown_pct"] * 100)
    )

    output_path = Path("reports") / "fib_strategy_candidates_comparison.csv"
    results_df.to_csv(output_path, index=False)

    print()
    print("TABLA COMPARATIVA")
    print("=" * 90)
    print(
        results_df[
            [
                "strategy_name",
                "candidate_status",
                "quality_score",
                "total_trades",
                "wins",
                "losses",
                "ending_capital",
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
        .sort_values(by=["candidate_status", "quality_score"], ascending=[True, False])
        .to_string(index=False)
    )

    print()
    print("RANKING POR QUALITY SCORE")
    print("=" * 90)
    print(
        results_df[
            [
                "strategy_name",
                "candidate_status",
                "quality_score",
                "total_trades",
                "total_return_pct",
                "win_rate",
                "profit_factor",
                "max_drawdown_pct",
                "expectancy",
            ]
        ]
        .sort_values(by="quality_score", ascending=False)
        .to_string(index=False)
    )

    print()
    print("LECTURA SUGERIDA")
    print("=" * 90)
    best = results_df.sort_values(by="quality_score", ascending=False).iloc[0]

    print(f"Mejor estrategia por quality_score: {best['strategy_name']}")
    print(f"Estado: {best['candidate_status']}")
    print(f"Trades: {int(best['total_trades'])}")
    print(f"Retorno: {best['total_return_pct']:.2%}")
    print(f"Win rate: {best['win_rate']:.2%}")
    print(f"Profit factor: {best['profit_factor']}")
    print(f"Max drawdown: {best['max_drawdown_pct']:.2%}")
    print()
    print(f"Archivo generado: {output_path}")


if __name__ == "__main__":
    main()