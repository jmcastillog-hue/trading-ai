from pathlib import Path

from src.backtesting.backtesting_engine_v3 import (
    BacktestConfig,
    run_backtest_v3,
    format_summary_text,
)

from src.market_structure.mtf_regime_filter import enrich_15m_with_mtf_regime
from src.strategies.fib_v5_mtf_strategy import fib_v5_short_with_mtf_filter


def main():
    enriched_csv = Path("reports") / "btcusdt_15m_with_mtf_regime.csv"

    enrich_15m_with_mtf_regime(
        entry_csv_path=Path("data") / "btcusdt_15m_validation.csv",
        h1_csv_path=Path("data") / "btcusdt_1h_validation.csv",
        h4_csv_path=Path("data") / "btcusdt_4h_validation.csv",
        output_path=enriched_csv,
    )

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
        csv_path=enriched_csv,
        config=config,
        output_dir=Path("reports"),
        strategy_func=fib_v5_short_with_mtf_filter,
    )

    print("BACKTEST V3 — FIB V5 + MTF REGIME FILTER")
    print("=" * 70)
    print(format_summary_text(summary))
    print()
    print("Filtro aplicado:")
    print("- Entrada FIB V5 15m")
    print("- Bloquea SHORT si 1h = STRONG_BULLISH")
    print("- Bloquea SHORT si 4h = STRONG_BULLISH")
    print()
    print(f"Trades generados: {len(trades_df)}")

    if len(trades_df) > 0:
        import pandas as pd

        enriched_df = pd.read_csv(enriched_csv)

        trades_df["entry_regime_1h"] = trades_df["entry_index"].apply(
            lambda idx: enriched_df.iloc[int(idx)].get("regime_1h", "UNKNOWN")
        )

        trades_df["entry_regime_4h"] = trades_df["entry_index"].apply(
            lambda idx: enriched_df.iloc[int(idx)].get("regime_4h", "UNKNOWN")
        )

        detailed_trades_path = Path("reports") / "backtest_v3_fib_mtf_trades_detailed.csv"
        trades_df.to_csv(detailed_trades_path, index=False)

        print()
        print("Regímenes usados en las últimas entradas:")
        print(
            trades_df[
                [
                    "entry_index",
                    "direction",
                    "entry_regime_1h",
                    "entry_regime_4h",
                    "exit_reason",
                    "net_pnl",
                ]
            ].tail(10)
        )

        print()
        print(f"Archivo detallado generado: {detailed_trades_path}")


if __name__ == "__main__":
    main()