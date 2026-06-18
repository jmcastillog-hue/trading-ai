from pathlib import Path
import pandas as pd

from src.backtesting.backtesting_engine_v3 import (
    BacktestConfig,
    run_backtest_v3,
    format_summary_text,
)

from src.market_structure.mtf_regime_filter import enrich_15m_with_mtf_regime
from src.strategies.fib_v5_mtf_liquidity_strategy import (
    fib_v5_short_with_mtf_and_liquidity_filter,
)

from src.liquidity.liquidity_context_filter import get_liquidity_context


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
        strategy_func=fib_v5_short_with_mtf_and_liquidity_filter,
    )

    print("BACKTEST V3 — FIB V5 + MTF + LIQUIDITY FILTER")
    print("=" * 75)
    print(format_summary_text(summary))
    print()
    print("Filtros aplicados:")
    print("- Entrada FIB V5 15m")
    print("- Bloquea SHORT si 1h = STRONG_BULLISH")
    print("- Bloquea SHORT si 4h = STRONG_BULLISH")
    print("- Bloquea SHORT si no hay al menos 1.5 ATR hacia sell-side liquidity")
    print()
    print(f"Trades generados: {len(trades_df)}")

    if len(trades_df) > 0:
        enriched_df = pd.read_csv(enriched_csv)

        trades_df["entry_regime_1h"] = trades_df["entry_index"].apply(
            lambda idx: enriched_df.iloc[int(idx)].get("regime_1h", "UNKNOWN")
        )

        trades_df["entry_regime_4h"] = trades_df["entry_index"].apply(
            lambda idx: enriched_df.iloc[int(idx)].get("regime_4h", "UNKNOWN")
        )

        liquidity_contexts = []

        # Para obtener ATR y columnas calculadas, reutilizamos el CSV enriquecido
        # y dejamos que el motor ya haya usado la misma lógica internamente.
        # Aquí recalculamos una aproximación para reporte.
        from src.backtesting.backtesting_engine_v3 import normalize_ohlcv_columns, add_indicators

        enriched_with_indicators = pd.read_csv(enriched_csv)
        enriched_with_indicators = normalize_ohlcv_columns(enriched_with_indicators)
        enriched_with_indicators = add_indicators(enriched_with_indicators, atr_period=14)

        for _, trade in trades_df.iterrows():
            idx = int(trade["entry_index"])
            context = get_liquidity_context(
                df=enriched_with_indicators,
                index=idx,
                min_atr_distance=1.5,
                lookback_bars=96,
            )
            liquidity_contexts.append(context)

        liquidity_df = pd.DataFrame(liquidity_contexts)

        trades_df = pd.concat(
            [trades_df.reset_index(drop=True), liquidity_df.reset_index(drop=True)],
            axis=1,
        )

        detailed_trades_path = Path("reports") / "backtest_v3_fib_mtf_liquidity_trades_detailed.csv"
        trades_df.to_csv(detailed_trades_path, index=False)

        print()
        print("Últimas entradas con contexto MTF y liquidez:")
        print(
            trades_df[
                [
                    "entry_index",
                    "direction",
                    "entry_regime_1h",
                    "entry_regime_4h",
                    "sell_side_liquidity",
                    "distance_to_liquidity",
                    "required_distance",
                    "exit_reason",
                    "net_pnl",
                ]
            ].tail(10).to_string(index=False)
        )

        print()
        print(f"Archivo detallado generado: {detailed_trades_path}")


if __name__ == "__main__":
    main()