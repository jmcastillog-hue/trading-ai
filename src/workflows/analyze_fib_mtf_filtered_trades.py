from pathlib import Path
import pandas as pd

from src.backtesting.backtesting_engine_v3 import (
    BacktestConfig,
    run_backtest_v3,
)

from src.strategies.fib_v5_strategy import fib_v5_short_signal
from src.strategies.fib_v5_mtf_strategy import fib_v5_short_with_mtf_filter
from src.market_structure.mtf_regime_filter import enrich_15m_with_mtf_regime


def best_fib_v5_strategy(df, index, config):
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


def build_config():
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


def add_entry_regimes(trades_df: pd.DataFrame, enriched_df: pd.DataFrame) -> pd.DataFrame:
    trades_df = trades_df.copy()

    if len(trades_df) == 0:
        return trades_df

    trades_df["entry_regime_1h"] = trades_df["entry_index"].apply(
        lambda idx: enriched_df.iloc[int(idx)].get("regime_1h", "UNKNOWN")
    )

    trades_df["entry_regime_4h"] = trades_df["entry_index"].apply(
        lambda idx: enriched_df.iloc[int(idx)].get("regime_4h", "UNKNOWN")
    )

    return trades_df


def main():
    enriched_csv = Path("reports") / "btcusdt_15m_with_mtf_regime.csv"

    enrich_15m_with_mtf_regime(
        entry_csv_path=Path("data") / "btcusdt_15m_validation.csv",
        h1_csv_path=Path("data") / "btcusdt_1h_validation.csv",
        h4_csv_path=Path("data") / "btcusdt_4h_validation.csv",
        output_path=enriched_csv,
    )

    enriched_df = pd.read_csv(enriched_csv)

    config = build_config()

    base_trades, base_summary = run_backtest_v3(
        csv_path=enriched_csv,
        config=config,
        output_dir=Path("reports"),
        strategy_func=best_fib_v5_strategy,
    )

    mtf_trades, mtf_summary = run_backtest_v3(
        csv_path=enriched_csv,
        config=config,
        output_dir=Path("reports"),
        strategy_func=fib_v5_short_with_mtf_filter,
    )

    base_trades = add_entry_regimes(base_trades, enriched_df)
    mtf_trades = add_entry_regimes(mtf_trades, enriched_df)

    base_entries = set(base_trades["entry_index"].astype(int).tolist())
    mtf_entries = set(mtf_trades["entry_index"].astype(int).tolist())

    blocked_entries = sorted(list(base_entries - mtf_entries))

    blocked_trades = base_trades[
        base_trades["entry_index"].astype(int).isin(blocked_entries)
    ].copy()

    output_path = Path("reports") / "fib_mtf_filtered_trades_analysis.csv"
    blocked_trades.to_csv(output_path, index=False)

    print("ANÁLISIS DE TRADES FILTRADOS — FIB V5 + MTF")
    print("=" * 70)

    print()
    print("Resumen sin filtro MTF:")
    print(f"- Trades: {base_summary.get('total_trades', 0)}")
    print(f"- Return: {base_summary.get('total_return_pct', 0):.2%}")
    print(f"- Win rate: {base_summary.get('win_rate', 0):.2%}")
    print(f"- Profit factor: {base_summary.get('profit_factor', None)}")
    print(f"- Max drawdown: {base_summary.get('max_drawdown_pct', 0):.2%}")

    print()
    print("Resumen con filtro MTF:")
    print(f"- Trades: {mtf_summary.get('total_trades', 0)}")
    print(f"- Return: {mtf_summary.get('total_return_pct', 0):.2%}")
    print(f"- Win rate: {mtf_summary.get('win_rate', 0):.2%}")
    print(f"- Profit factor: {mtf_summary.get('profit_factor', None)}")
    print(f"- Max drawdown: {mtf_summary.get('max_drawdown_pct', 0):.2%}")

    print()
    print(f"Trades bloqueados por el filtro MTF: {len(blocked_trades)}")

    if len(blocked_trades) > 0:
        print()
        print("Detalle de trades bloqueados:")
        print(
            blocked_trades[
                [
                    "entry_index",
                    "exit_index",
                    "direction",
                    "entry_price",
                    "exit_price",
                    "exit_reason",
                    "net_pnl",
                    "return_pct",
                    "entry_regime_1h",
                    "entry_regime_4h",
                ]
            ].to_string(index=False)
        )

        total_blocked_pnl = blocked_trades["net_pnl"].sum()
        print()
        print(f"PnL total de trades bloqueados: {total_blocked_pnl:.4f}")

        if total_blocked_pnl < 0:
            print("Lectura: el filtro bloqueó pérdida neta.")
        elif total_blocked_pnl > 0:
            print("Lectura: el filtro bloqueó ganancia neta.")
        else:
            print("Lectura: el filtro bloqueó resultado neutro.")

    print()
    print(f"Archivo generado: {output_path}")


if __name__ == "__main__":
    main()