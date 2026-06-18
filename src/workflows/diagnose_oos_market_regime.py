from pathlib import Path
import pandas as pd

from src.backtesting.backtesting_engine_v3 import (
    BacktestConfig,
    run_backtest_v3,
)

from src.market_structure.mtf_regime_filter import (
    enrich_15m_with_mtf_regime,
    classify_regime,
)

from src.strategies.fib_v5_mtf_strategy import fib_v5_short_with_mtf_filter
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


def add_15m_regime(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    df["ema20"] = df["close"].ewm(span=20, adjust=False).mean()
    df["ema50"] = df["close"].ewm(span=50, adjust=False).mean()
    df["ema200"] = df["close"].ewm(span=200, adjust=False).mean()

    df["regime_15m"] = df.apply(classify_regime, axis=1)

    return df


def value_counts_pct(df: pd.DataFrame, column: str) -> pd.DataFrame:
    counts = df[column].value_counts(dropna=False)
    pct = df[column].value_counts(normalize=True, dropna=False)

    result = pd.DataFrame(
        {
            "count": counts,
            "pct": pct,
        }
    )

    result["pct"] = result["pct"] * 100

    return result.reset_index(names=column)


def summarize_market(label: str, csv_path: Path) -> dict:
    df = pd.read_csv(csv_path)
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    df = df.dropna(subset=["timestamp", "open", "high", "low", "close"])
    df = df.sort_values("timestamp").reset_index(drop=True)

    start_close = float(df.iloc[0]["close"])
    end_close = float(df.iloc[-1]["close"])
    market_return_pct = (end_close / start_close) - 1

    df["candle_return"] = df["close"].pct_change()
    bullish_candles = int((df["close"] > df["open"]).sum())
    bearish_candles = int((df["close"] < df["open"]).sum())
    neutral_candles = int((df["close"] == df["open"]).sum())

    return {
        "label": label,
        "start_time": str(df.iloc[0]["timestamp"]),
        "end_time": str(df.iloc[-1]["timestamp"]),
        "candles": len(df),
        "start_close": start_close,
        "end_close": end_close,
        "market_return_pct": market_return_pct,
        "bullish_candles": bullish_candles,
        "bearish_candles": bearish_candles,
        "neutral_candles": neutral_candles,
        "bullish_candle_pct": bullish_candles / len(df),
        "bearish_candle_pct": bearish_candles / len(df),
    }


def add_trade_context(trades_df: pd.DataFrame, enriched_df: pd.DataFrame) -> pd.DataFrame:
    trades_df = trades_df.copy()

    if len(trades_df) == 0:
        return trades_df

    trades_df["entry_regime_15m"] = trades_df["entry_index"].apply(
        lambda idx: enriched_df.iloc[int(idx)].get("regime_15m", "UNKNOWN")
    )

    trades_df["entry_regime_1h"] = trades_df["entry_index"].apply(
        lambda idx: enriched_df.iloc[int(idx)].get("regime_1h", "UNKNOWN")
    )

    trades_df["entry_regime_4h"] = trades_df["entry_index"].apply(
        lambda idx: enriched_df.iloc[int(idx)].get("regime_4h", "UNKNOWN")
    )

    trades_df["entry_regime_combo"] = (
        trades_df["entry_regime_15m"].astype(str)
        + " | "
        + trades_df["entry_regime_1h"].astype(str)
        + " | "
        + trades_df["entry_regime_4h"].astype(str)
    )

    return trades_df


def summarize_trades_by_regime(trades_df: pd.DataFrame, group_col: str) -> pd.DataFrame:
    if len(trades_df) == 0:
        return pd.DataFrame()

    grouped = []

    for regime, group in trades_df.groupby(group_col):
        total = len(group)
        wins = int((group["net_pnl"] > 0).sum())
        losses = int((group["net_pnl"] < 0).sum())
        net_pnl = float(group["net_pnl"].sum())
        win_rate = wins / total if total > 0 else 0

        gross_profit = float(group.loc[group["net_pnl"] > 0, "net_pnl"].sum())
        gross_loss = float(group.loc[group["net_pnl"] < 0, "net_pnl"].sum())

        if gross_loss < 0:
            profit_factor = gross_profit / abs(gross_loss)
        else:
            profit_factor = None

        grouped.append(
            {
                group_col: regime,
                "trades": total,
                "wins": wins,
                "losses": losses,
                "win_rate": win_rate,
                "net_pnl": net_pnl,
                "profit_factor": profit_factor,
            }
        )

    return pd.DataFrame(grouped).sort_values(by="net_pnl", ascending=False)


def run_strategy_diagnostics(
    label: str,
    enriched_csv: Path,
    strategy_func,
) -> tuple[dict, pd.DataFrame]:
    config = build_config()

    trades_df, summary = run_backtest_v3(
        csv_path=enriched_csv,
        config=config,
        output_dir=Path("reports"),
        strategy_func=strategy_func,
    )

    enriched_df = pd.read_csv(enriched_csv)
    enriched_df = add_15m_regime(enriched_df)

    trades_df = add_trade_context(trades_df, enriched_df)

    result = {
        "label": label,
        "total_trades": summary.get("total_trades", 0),
        "wins": summary.get("wins", 0),
        "losses": summary.get("losses", 0),
        "ending_capital": summary.get("ending_capital", 1000.0),
        "total_return_pct": summary.get("total_return_pct", 0.0),
        "win_rate": summary.get("win_rate", 0.0),
        "profit_factor": summary.get("profit_factor", None),
        "expectancy": summary.get("expectancy", 0.0),
        "max_drawdown_pct": summary.get("max_drawdown_pct", 0.0),
    }

    return result, trades_df


def prepare_dataset(
    label: str,
    entry_csv: Path,
    h1_csv: Path,
    h4_csv: Path,
    output_csv: Path,
) -> pd.DataFrame:
    enrich_15m_with_mtf_regime(
        entry_csv_path=entry_csv,
        h1_csv_path=h1_csv,
        h4_csv_path=h4_csv,
        output_path=output_csv,
    )

    df = pd.read_csv(output_csv)
    df = add_15m_regime(df)
    df["regime_combo"] = (
        df["regime_15m"].astype(str)
        + " | "
        + df["regime_1h"].astype(str)
        + " | "
        + df["regime_4h"].astype(str)
    )

    df.to_csv(output_csv, index=False)

    return df


def main():
    datasets = [
        {
            "label": "IN_SAMPLE_5000",
            "entry_csv": Path("data") / "btcusdt_15m_validation.csv",
            "h1_csv": Path("data") / "btcusdt_1h_validation.csv",
            "h4_csv": Path("data") / "btcusdt_4h_validation.csv",
            "output_csv": Path("reports") / "diagnostic_insample_15m_with_mtf.csv",
        },
        {
            "label": "OOS_2024_01_03",
            "entry_csv": Path("data") / "oos_btcusdt_15m_2024_01_03.csv",
            "h1_csv": Path("data") / "oos_btcusdt_1h_2024_01_03.csv",
            "h4_csv": Path("data") / "oos_btcusdt_4h_2024_01_03.csv",
            "output_csv": Path("reports") / "diagnostic_oos_15m_with_mtf.csv",
        },
    ]

    print("DIAGNÓSTICO DE RÉGIMEN — IN SAMPLE VS OUT OF SAMPLE")
    print("=" * 90)

    market_summaries = []
    strategy_summaries = []

    for dataset in datasets:
        label = dataset["label"]

        print()
        print(f"Preparando dataset: {label}")
        print("-" * 90)

        df = prepare_dataset(**dataset)

        market_summary = summarize_market(
            label=label,
            csv_path=dataset["entry_csv"],
        )

        market_summaries.append(market_summary)

        print()
        print("Resumen de mercado:")
        print(pd.DataFrame([market_summary]).to_string(index=False))

        print()
        print("Distribución régimen 15m:")
        print(value_counts_pct(df, "regime_15m").to_string(index=False))

        print()
        print("Distribución régimen 1h:")
        print(value_counts_pct(df, "regime_1h").to_string(index=False))

        print()
        print("Distribución régimen 4h:")
        print(value_counts_pct(df, "regime_4h").to_string(index=False))

        print()
        print("Top combinaciones de régimen:")
        print(value_counts_pct(df, "regime_combo").head(10).to_string(index=False))

        for strategy_label, strategy_func in [
            (f"{label}_FIB_V5_MTF", fib_v5_short_with_mtf_filter),
            (
                f"{label}_FIB_V5_MTF_LIQUIDITY_V2",
                fib_v5_short_with_mtf_and_liquidity_v2_filter,
            ),
        ]:
            result, trades_df = run_strategy_diagnostics(
                label=strategy_label,
                enriched_csv=dataset["output_csv"],
                strategy_func=strategy_func,
            )

            strategy_summaries.append(result)

            print()
            print(f"Resumen estrategia: {strategy_label}")
            print(pd.DataFrame([result]).to_string(index=False))

            if len(trades_df) > 0:
                print()
                print("Resultado por régimen 1h:")
                print(
                    summarize_trades_by_regime(
                        trades_df,
                        "entry_regime_1h",
                    ).to_string(index=False)
                )

                print()
                print("Resultado por régimen 4h:")
                print(
                    summarize_trades_by_regime(
                        trades_df,
                        "entry_regime_4h",
                    ).to_string(index=False)
                )

    market_df = pd.DataFrame(market_summaries)
    strategy_df = pd.DataFrame(strategy_summaries)

    market_output = Path("reports") / "diagnostic_market_regime_summary.csv"
    strategy_output = Path("reports") / "diagnostic_strategy_by_regime_summary.csv"

    market_df.to_csv(market_output, index=False)
    strategy_df.to_csv(strategy_output, index=False)

    print()
    print("RESUMEN FINAL DE MERCADO")
    print("=" * 90)
    print(market_df.to_string(index=False))

    print()
    print("RESUMEN FINAL DE ESTRATEGIAS")
    print("=" * 90)
    print(strategy_df.to_string(index=False))

    print()
    print(f"Archivos generados:")
    print(f"- {market_output}")
    print(f"- {strategy_output}")


if __name__ == "__main__":
    main()