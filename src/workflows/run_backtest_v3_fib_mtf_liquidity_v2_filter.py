from pathlib import Path
import pandas as pd

from src.backtesting.backtesting_engine_v3 import (
    BacktestConfig,
    run_backtest_v3,
    format_summary_text,
    normalize_ohlcv_columns,
    add_indicators,
)

from src.market_structure.mtf_regime_filter import enrich_15m_with_mtf_regime
from src.strategies.fib_v5_mtf_strategy import fib_v5_short_with_mtf_filter
from src.strategies.fib_v5_mtf_liquidity_v2_strategy import (
    fib_v5_short_with_mtf_and_liquidity_v2_filter,
)

from src.liquidity.liquidity_zones_v2 import get_liquidity_context_v2


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


def add_context_to_trades(trades_df: pd.DataFrame, enriched_csv: Path) -> pd.DataFrame:
    if len(trades_df) == 0:
        return trades_df

    enriched_df = pd.read_csv(enriched_csv)

    trades_df = trades_df.copy()

    trades_df["entry_regime_1h"] = trades_df["entry_index"].apply(
        lambda idx: enriched_df.iloc[int(idx)].get("regime_1h", "UNKNOWN")
    )

    trades_df["entry_regime_4h"] = trades_df["entry_index"].apply(
        lambda idx: enriched_df.iloc[int(idx)].get("regime_4h", "UNKNOWN")
    )

    enriched_with_indicators = pd.read_csv(enriched_csv)
    enriched_with_indicators = normalize_ohlcv_columns(enriched_with_indicators)
    enriched_with_indicators = add_indicators(enriched_with_indicators, atr_period=14)

    contexts = []

    for _, trade in trades_df.iterrows():
        idx = int(trade["entry_index"])
        context = get_liquidity_context_v2(
            df=enriched_with_indicators,
            index=idx,
            min_atr_distance=0.8,
            lookback_bars=192,
            left_bars=2,
            right_bars=2,
            equal_low_tolerance_atr=0.35,
            min_touches=2,
        )
        contexts.append(context)

    context_df = pd.DataFrame(contexts)

    trades_df = pd.concat(
        [trades_df.reset_index(drop=True), context_df.reset_index(drop=True)],
        axis=1,
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

    config = build_config()

    mtf_trades, mtf_summary = run_backtest_v3(
        csv_path=enriched_csv,
        config=config,
        output_dir=Path("reports"),
        strategy_func=fib_v5_short_with_mtf_filter,
    )

    liquidity_v2_trades, liquidity_v2_summary = run_backtest_v3(
        csv_path=enriched_csv,
        config=config,
        output_dir=Path("reports"),
        strategy_func=fib_v5_short_with_mtf_and_liquidity_v2_filter,
    )

    liquidity_v2_trades = add_context_to_trades(
        trades_df=liquidity_v2_trades,
        enriched_csv=enriched_csv,
    )

    detailed_path = Path("reports") / "backtest_v3_fib_mtf_liquidity_v2_trades_detailed.csv"
    liquidity_v2_trades.to_csv(detailed_path, index=False)

    print("BACKTEST V3 — FIB V5 + MTF + LIQUIDITY V2")
    print("=" * 80)

    print()
    print("BENCHMARK — FIB V5 + MTF")
    print("-" * 80)
    print(f"Trades: {mtf_summary.get('total_trades', 0)}")
    print(f"Return: {mtf_summary.get('total_return_pct', 0):.2%}")
    print(f"Win rate: {mtf_summary.get('win_rate', 0):.2%}")
    print(f"Profit factor: {mtf_summary.get('profit_factor', None)}")
    print(f"Max drawdown: {mtf_summary.get('max_drawdown_pct', 0):.2%}")

    print()
    print("RESULTADO — FIB V5 + MTF + LIQUIDITY V2")
    print("-" * 80)
    print(format_summary_text(liquidity_v2_summary))

    print()
    print("Filtro Liquidez V2:")
    print("- nearest sell-side liquidity bajo el precio")
    print("- swing lows confirmados")
    print("- equal lows agrupados por tolerancia ATR")
    print("- min_atr_distance: 0.8")
    print("- lookback_bars: 192")
    print("- equal_low_tolerance_atr: 0.35")
    print("- min_touches: 2")

    print()
    print(f"Trades generados: {len(liquidity_v2_trades)}")
    print(f"Archivo detallado generado: {detailed_path}")

    if len(liquidity_v2_trades) > 0:
        print()
        print("Últimas entradas con contexto Liquidez V2:")
        print(
            liquidity_v2_trades[
                [
                    "entry_index",
                    "direction",
                    "entry_regime_1h",
                    "entry_regime_4h",
                    "liquidity_v2_zone_level",
                    "liquidity_v2_touches",
                    "liquidity_v2_distance",
                    "liquidity_v2_required_distance",
                    "exit_reason",
                    "net_pnl",
                ]
            ].tail(10).to_string(index=False)
        )


if __name__ == "__main__":
    main()