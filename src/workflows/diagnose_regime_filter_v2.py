from pathlib import Path
import pandas as pd

from src.backtesting.backtesting_engine_v3 import BacktestConfig, run_backtest_v3
from src.market_structure.mtf_regime_filter import (
    enrich_15m_with_mtf_regime,
    long_allowed_by_mtf_regime,
)
from src.market_structure.regime_filter_v2 import (
    enrich_with_regime_filter_v2,
    long_allowed_by_regime_v2,
)
from src.workflows.validate_long_v2_candidate_robust import (
    download_binance_klines_range,
    calculate_market_return,
)


def build_config() -> BacktestConfig:
    return BacktestConfig(
        initial_capital=1000.0,
        risk_per_trade=0.01,
        risk_reward=2.0,
        fee_rate=0.001,
        spread_rate=0.0002,
        atr_period=14,
        atr_multiplier=1.5,
        max_holding_bars=96,
        direction_mode="long_only",
    )


def long_v2_entry_logic(df: pd.DataFrame, index: int) -> bool:
    lookback_bars = 48
    fib_entry_low = 0.500
    fib_entry_high = 0.618
    min_impulse_pct = 0.02

    if index < lookback_bars:
        return False

    window = df.iloc[index - lookback_bars:index]

    if window.empty:
        return False

    impulse_low_idx = window["low"].idxmin()
    impulse_low = float(df.loc[impulse_low_idx, "low"])

    after_low = df.loc[impulse_low_idx:index - 1]

    if after_low.empty:
        return False

    impulse_high_idx = after_low["high"].idxmax()
    impulse_high = float(df.loc[impulse_high_idx, "high"])

    if impulse_high <= impulse_low:
        return False

    impulse_pct = (impulse_high / impulse_low) - 1

    if impulse_pct < min_impulse_pct:
        return False

    impulse_range = impulse_high - impulse_low

    fib_050_price = impulse_high - (impulse_range * fib_entry_low)
    fib_0618_price = impulse_high - (impulse_range * fib_entry_high)

    zone_low = min(fib_050_price, fib_0618_price)
    zone_high = max(fib_050_price, fib_0618_price)

    row = df.iloc[index]

    candle_high = float(row["high"])
    candle_low = float(row["low"])
    candle_close = float(row["close"])

    touches_fib_zone = candle_low <= zone_high and candle_high >= zone_low

    if not touches_fib_zone:
        return False

    previous_high = float(df.iloc[index - 1]["high"])

    if candle_close <= previous_high:
        return False

    return True


def long_v2_old_mtf_signal(df: pd.DataFrame, index: int, config=None) -> str:
    if not long_v2_entry_logic(df, index):
        return "NONE"

    row = df.iloc[index]

    regime_1h = row.get("regime_1h", "UNKNOWN")
    regime_4h = row.get("regime_4h", "UNKNOWN")

    if not long_allowed_by_mtf_regime(regime_1h, regime_4h):
        return "NONE"

    return "LONG"


def long_v2_regime_filter_v2_signal(df: pd.DataFrame, index: int, config=None) -> str:
    if not long_v2_entry_logic(df, index):
        return "NONE"

    row = df.iloc[index]

    state_1h = row.get("state_1h_v2", "UNKNOWN")
    state_4h = row.get("state_4h_v2", "UNKNOWN")

    if not long_allowed_by_regime_v2(state_1h, state_4h):
        return "NONE"

    return "LONG"


def summarize_strategy(
    window_name: str,
    strategy_name: str,
    market_return_pct: float,
    trades_df: pd.DataFrame,
    summary: dict,
) -> dict:
    take_profit_count = 0
    stop_loss_count = 0
    max_holding_exit_count = 0

    if len(trades_df) > 0:
        take_profit_count = int((trades_df["exit_reason"] == "TAKE_PROFIT").sum())
        stop_loss_count = int((trades_df["exit_reason"] == "STOP_LOSS").sum())
        max_holding_exit_count = int(
            (trades_df["exit_reason"] == "MAX_HOLDING_EXIT").sum()
        )

    return {
        "window_name": window_name,
        "strategy_name": strategy_name,
        "market_return_pct": market_return_pct,
        "total_trades": int(summary.get("total_trades", 0)),
        "wins": int(summary.get("wins", 0)),
        "losses": int(summary.get("losses", 0)),
        "ending_capital": summary.get("ending_capital", 1000.0),
        "total_return_pct": float(summary.get("total_return_pct", 0.0)),
        "win_rate": float(summary.get("win_rate", 0.0)),
        "profit_factor": summary.get("profit_factor", None),
        "expectancy": float(summary.get("expectancy", 0.0)),
        "max_drawdown_pct": float(summary.get("max_drawdown_pct", 0.0)),
        "take_profit_count": take_profit_count,
        "stop_loss_count": stop_loss_count,
        "max_holding_exit_count": max_holding_exit_count,
    }


def add_entry_states_to_trades(
    trades_df: pd.DataFrame,
    market_df: pd.DataFrame,
    window_name: str,
    strategy_name: str,
) -> pd.DataFrame:
    if trades_df.empty:
        return pd.DataFrame()

    rows = []

    for _, trade in trades_df.iterrows():
        entry_index = int(trade["entry_index"])

        if entry_index < 0 or entry_index >= len(market_df):
            continue

        entry_row = market_df.iloc[entry_index]

        row = trade.to_dict()
        row["window_name"] = window_name
        row["strategy_name"] = strategy_name
        row["state_15m_v2"] = entry_row.get("state_15m_v2", "UNKNOWN")
        row["state_1h_v2"] = entry_row.get("state_1h_v2", "UNKNOWN")
        row["state_4h_v2"] = entry_row.get("state_4h_v2", "UNKNOWN")
        row["regime_1h_old"] = entry_row.get("regime_1h", "UNKNOWN")
        row["regime_4h_old"] = entry_row.get("regime_4h", "UNKNOWN")

        rows.append(row)

    return pd.DataFrame(rows)


def print_state_diagnostics(trades_df: pd.DataFrame, label: str):
    print()
    print(label)
    print("-" * 100)

    if trades_df.empty:
        print("Sin trades.")
        return

    grouped = (
        trades_df.groupby(["state_1h_v2", "state_4h_v2"])
        .agg(
            trades=("entry_index", "count"),
            total_net_pnl=("net_pnl", "sum"),
            avg_net_pnl=("net_pnl", "mean"),
        )
        .reset_index()
        .sort_values(by="total_net_pnl", ascending=False)
    )

    print(grouped.to_string(index=False))


def print_state_distribution(market_df: pd.DataFrame, window_name: str):
    print()
    print(f"DISTRIBUCION DE ESTADOS V2: {window_name}")
    print("-" * 100)

    for col in ["state_15m_v2", "state_1h_v2", "state_4h_v2"]:
        if col not in market_df.columns:
            continue

        distribution = (
            market_df[col]
            .value_counts(normalize=True)
            .mul(100)
            .round(2)
            .reset_index()
        )

        distribution.columns = [col, "pct"]

        print()
        print(col)
        print(distribution.to_string(index=False))


def validate_window(
    symbol: str,
    window_name: str,
    start_date: str,
    end_date: str,
) -> tuple[list[dict], pd.DataFrame]:
    data_dir = Path("data") / "regime_v2"
    reports_dir = Path("reports") / "regime_v2"

    data_dir.mkdir(parents=True, exist_ok=True)
    reports_dir.mkdir(parents=True, exist_ok=True)

    base_name = f"{symbol.lower()}_{window_name}"

    csv_15m = data_dir / f"{base_name}_15m.csv"
    csv_1h = data_dir / f"{base_name}_1h.csv"
    csv_4h = data_dir / f"{base_name}_4h.csv"

    old_mtf_csv = reports_dir / f"{base_name}_old_mtf.csv"
    regime_v2_csv = reports_dir / f"{base_name}_regime_v2.csv"

    print()
    print(f"VENTANA: {window_name}")
    print("=" * 100)

    if not csv_15m.exists():
        download_binance_klines_range(symbol, "15m", start_date, end_date, csv_15m)

    if not csv_1h.exists():
        download_binance_klines_range(symbol, "1h", start_date, end_date, csv_1h)

    if not csv_4h.exists():
        download_binance_klines_range(symbol, "4h", start_date, end_date, csv_4h)

    market_return_pct = calculate_market_return(csv_15m)

    enrich_15m_with_mtf_regime(
        entry_csv_path=csv_15m,
        h1_csv_path=csv_1h,
        h4_csv_path=csv_4h,
        output_path=old_mtf_csv,
    )

    market_df = enrich_with_regime_filter_v2(
        entry_csv_path=old_mtf_csv,
        h1_csv_path=csv_1h,
        h4_csv_path=csv_4h,
        output_path=regime_v2_csv,
    )

    print_state_distribution(market_df, window_name)

    results = []
    all_trades = []

    strategy_map = [
        ("LONG_V2_OLD_MTF", long_v2_old_mtf_signal),
        ("LONG_V2_REGIME_V2", long_v2_regime_filter_v2_signal),
    ]

    for strategy_name, strategy_func in strategy_map:
        trades_df, summary = run_backtest_v3(
            csv_path=regime_v2_csv,
            config=build_config(),
            output_dir=reports_dir,
            strategy_func=strategy_func,
        )

        result = summarize_strategy(
            window_name=window_name,
            strategy_name=strategy_name,
            market_return_pct=market_return_pct,
            trades_df=trades_df,
            summary=summary,
        )

        results.append(result)

        trades_with_states = add_entry_states_to_trades(
            trades_df=trades_df,
            market_df=market_df,
            window_name=window_name,
            strategy_name=strategy_name,
        )

        if not trades_with_states.empty:
            all_trades.append(trades_with_states)

        print(
            f"{strategy_name} | "
            f"market={market_return_pct:.2%} | "
            f"trades={result['total_trades']} | "
            f"return={result['total_return_pct']:.2%} | "
            f"wr={result['win_rate']:.2%} | "
            f"pf={result['profit_factor']} | "
            f"mdd={result['max_drawdown_pct']:.2%}"
        )

        print_state_diagnostics(
            trades_with_states,
            f"DIAGNOSTICO ESTADOS — {window_name} — {strategy_name}",
        )

    if all_trades:
        trades_window_df = pd.concat(all_trades, ignore_index=True)
    else:
        trades_window_df = pd.DataFrame()

    return results, trades_window_df


def main():
    symbol = "BTCUSDT"

    windows = [
        ("2024_01_03", "2024-01-01", "2024-03-01"),
        ("2024_03_05", "2024-03-01", "2024-05-01"),
        ("2024_05_07", "2024-05-01", "2024-07-01"),
        ("2024_07_09", "2024-07-01", "2024-09-01"),
        ("2024_09_11", "2024-09-01", "2024-11-01"),
        ("2024_11_2025_01", "2024-11-01", "2025-01-01"),
    ]

    print("DIAGNOSTICO REGIME FILTER V2")
    print("=" * 100)
    print("Comparacion:")
    print("- LONG_V2_OLD_MTF")
    print("- LONG_V2_REGIME_V2")
    print()

    all_results = []
    all_trades = []

    for window_name, start_date, end_date in windows:
        results, trades_df = validate_window(
            symbol=symbol,
            window_name=window_name,
            start_date=start_date,
            end_date=end_date,
        )

        all_results.extend(results)

        if not trades_df.empty:
            all_trades.append(trades_df)

    results_df = pd.DataFrame(all_results)

    if all_trades:
        trades_all_df = pd.concat(all_trades, ignore_index=True)
    else:
        trades_all_df = pd.DataFrame()

    reports_dir = Path("reports") / "regime_v2"
    summary_output = reports_dir / "regime_filter_v2_summary.csv"
    trades_output = reports_dir / "regime_filter_v2_trade_diagnostics.csv"

    results_df.to_csv(summary_output, index=False)
    trades_all_df.to_csv(trades_output, index=False)

    print()
    print("RESUMEN COMPARATIVO")
    print("=" * 100)
    print(
        results_df[
            [
                "window_name",
                "strategy_name",
                "market_return_pct",
                "total_trades",
                "total_return_pct",
                "win_rate",
                "profit_factor",
                "expectancy",
                "max_drawdown_pct",
                "take_profit_count",
                "stop_loss_count",
                "max_holding_exit_count",
            ]
        ].to_string(index=False)
    )

    print()
    print("AGREGADO POR ESTRATEGIA")
    print("=" * 100)
    aggregated = (
        results_df.groupby("strategy_name")
        .agg(
            windows=("window_name", "count"),
            total_trades=("total_trades", "sum"),
            avg_return=("total_return_pct", "mean"),
            avg_win_rate=("win_rate", "mean"),
            avg_profit_factor=("profit_factor", "mean"),
            worst_drawdown=("max_drawdown_pct", "min"),
        )
        .reset_index()
        .sort_values(by="avg_profit_factor", ascending=False)
    )

    print(aggregated.to_string(index=False))

    print()
    print("PNL POR COMBINACION DE ESTADOS V2")
    print("=" * 100)

    if not trades_all_df.empty:
        state_grouped = (
            trades_all_df.groupby(["strategy_name", "state_1h_v2", "state_4h_v2"])
            .agg(
                trades=("entry_index", "count"),
                total_net_pnl=("net_pnl", "sum"),
                avg_net_pnl=("net_pnl", "mean"),
            )
            .reset_index()
            .sort_values(by="total_net_pnl", ascending=False)
        )

        print(state_grouped.to_string(index=False))
    else:
        print("Sin trades.")

    print()
    print("ARCHIVOS GENERADOS")
    print("=" * 100)
    print(f"- {summary_output}")
    print(f"- {trades_output}")


if __name__ == "__main__":
    main()