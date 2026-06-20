from pathlib import Path
import pandas as pd

from src.backtesting.backtesting_engine_v3 import BacktestConfig, run_backtest_v3
from src.market_structure.mtf_regime_filter import enrich_15m_with_mtf_regime
from src.strategies.fib_v5_long_strategy import fib_v5_long_signal
from src.strategies.fib_v5_long_mtf_strategy import fib_v5_long_with_mtf_filter


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
        direction_mode="long_only",
    )


def fib_v5_long_base_strategy(df, index: int, config=None) -> str:
    return fib_v5_long_signal(
        df=df,
        index=index,
        config=config,
        lookback_bars=48,
        fib_entry_low=0.618,
        fib_entry_high=0.786,
        min_impulse_pct=0.02,
        require_bullish_confirmation=True,
        require_rejection_wick=False,
    )


def safe_float(value, default=None):
    try:
        if pd.isna(value):
            return default
        return float(value)
    except Exception:
        return default


def get_trade_price(row, market_df: pd.DataFrame, index: int, column_options: list[str]):
    for col in column_options:
        if col in row.index:
            value = safe_float(row[col])
            if value is not None:
                return value

    if 0 <= index < len(market_df):
        return float(market_df.iloc[index]["close"])

    return None


def diagnose_single_trade(
    row,
    market_df: pd.DataFrame,
    strategy_name: str,
    post_exit_bars: int = 48,
) -> dict:
    entry_index = int(row["entry_index"])
    exit_index = int(row["exit_index"])

    entry_price = get_trade_price(
        row=row,
        market_df=market_df,
        index=entry_index,
        column_options=["entry_price", "entry"],
    )

    exit_price = get_trade_price(
        row=row,
        market_df=market_df,
        index=exit_index,
        column_options=["exit_price", "exit"],
    )

    stop_loss = get_trade_price(
        row=row,
        market_df=market_df,
        index=entry_index,
        column_options=["stop_loss", "stop_price"],
    )

    take_profit = get_trade_price(
        row=row,
        market_df=market_df,
        index=entry_index,
        column_options=["take_profit", "target_price", "tp_price"],
    )

    if entry_price is None:
        raise ValueError(f"No entry price found for trade at index {entry_index}")

    trade_window = market_df.iloc[entry_index : exit_index + 1].copy()

    post_start = exit_index + 1
    post_end = min(exit_index + 1 + post_exit_bars, len(market_df))
    post_window = market_df.iloc[post_start:post_end].copy()

    min_low_during_trade = float(trade_window["low"].min())
    max_high_during_trade = float(trade_window["high"].max())

    mae_pct = (min_low_during_trade / entry_price) - 1
    mfe_pct = (max_high_during_trade / entry_price) - 1

    risk_pct = None
    reward_pct = None

    if stop_loss is not None and stop_loss < entry_price:
        risk_pct = (entry_price - stop_loss) / entry_price

    if take_profit is not None and take_profit > entry_price:
        reward_pct = (take_profit - entry_price) / entry_price

    mae_r = None
    mfe_r = None

    if risk_pct is not None and risk_pct > 0:
        mae_r = mae_pct / risk_pct
        mfe_r = mfe_pct / risk_pct

    post_exit_max_high = None
    post_exit_recovery_pct = None
    post_exit_recovery_r = None

    if len(post_window) > 0:
        post_exit_max_high = float(post_window["high"].max())
        post_exit_recovery_pct = (post_exit_max_high / entry_price) - 1

        if risk_pct is not None and risk_pct > 0:
            post_exit_recovery_r = post_exit_recovery_pct / risk_pct

    exit_reason = str(row.get("exit_reason", "UNKNOWN"))
    net_pnl = safe_float(row.get("net_pnl"), 0.0)
    holding_bars = safe_float(row.get("holding_bars"), None)

    entry_row = market_df.iloc[entry_index]

    regime_1h = entry_row.get("regime_1h", "UNKNOWN")
    regime_4h = entry_row.get("regime_4h", "UNKNOWN")

    diagnosis = "UNCLASSIFIED"

    if exit_reason == "STOP_LOSS":
        if post_exit_recovery_r is not None and post_exit_recovery_r >= 1.0:
            diagnosis = "STOPPED_THEN_RECOVERED"
        elif mfe_r is not None and mfe_r < 0.5:
            diagnosis = "POOR_ENTRY_NO_FOLLOW_THROUGH"
        elif mae_r is not None and mae_r <= -1.0 and mfe_r is not None and mfe_r >= 0.5:
            diagnosis = "STOP_TOO_TIGHT_OR_ENTRY_EARLY"
        else:
            diagnosis = "STOP_LOSS_UNCLEAR"

    elif exit_reason == "TAKE_PROFIT":
        diagnosis = "GOOD_TRADE"

    elif exit_reason == "MAX_HOLDING_EXIT":
        if mfe_r is not None and mfe_r >= 1.0:
            diagnosis = "TIME_EXIT_AFTER_PARTIAL_MOVE"
        else:
            diagnosis = "NO_MOMENTUM"

    return {
        "strategy_name": strategy_name,
        "entry_index": entry_index,
        "exit_index": exit_index,
        "exit_reason": exit_reason,
        "diagnosis": diagnosis,
        "entry_price": entry_price,
        "exit_price": exit_price,
        "stop_loss": stop_loss,
        "take_profit": take_profit,
        "risk_pct": risk_pct,
        "reward_pct": reward_pct,
        "mae_pct": mae_pct,
        "mfe_pct": mfe_pct,
        "mae_r": mae_r,
        "mfe_r": mfe_r,
        "post_exit_recovery_pct": post_exit_recovery_pct,
        "post_exit_recovery_r": post_exit_recovery_r,
        "holding_bars": holding_bars,
        "net_pnl": net_pnl,
        "entry_regime_1h": regime_1h,
        "entry_regime_4h": regime_4h,
    }


def run_diagnostic_for_strategy(
    strategy_name: str,
    strategy_func,
    enriched_csv: Path,
    market_df: pd.DataFrame,
) -> tuple[dict, pd.DataFrame]:
    trades_df, summary = run_backtest_v3(
        csv_path=enriched_csv,
        config=build_config(),
        output_dir=Path("reports"),
        strategy_func=strategy_func,
    )

    diagnostics = []

    for _, row in trades_df.iterrows():
        diagnostics.append(
            diagnose_single_trade(
                row=row,
                market_df=market_df,
                strategy_name=strategy_name,
                post_exit_bars=48,
            )
        )

    diagnostics_df = pd.DataFrame(diagnostics)

    summary_row = {
        "strategy_name": strategy_name,
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

    return summary_row, diagnostics_df


def print_grouped_table(df: pd.DataFrame, group_cols: list[str]):
    if df.empty:
        print("No hay trades para agrupar.")
        return

    grouped = (
        df.groupby(group_cols)
        .agg(
            trades=("entry_index", "count"),
            avg_net_pnl=("net_pnl", "mean"),
            total_net_pnl=("net_pnl", "sum"),
            avg_mae_r=("mae_r", "mean"),
            avg_mfe_r=("mfe_r", "mean"),
            avg_post_exit_recovery_r=("post_exit_recovery_r", "mean"),
        )
        .reset_index()
        .sort_values(by="total_net_pnl", ascending=False)
    )

    print(grouped.to_string(index=False))


def main():
    enriched_csv = Path("reports") / "oos_btcusdt_15m_with_mtf_regime.csv"

    enrich_15m_with_mtf_regime(
        entry_csv_path=Path("data") / "oos_btcusdt_15m_2024_01_03.csv",
        h1_csv_path=Path("data") / "oos_btcusdt_1h_2024_01_03.csv",
        h4_csv_path=Path("data") / "oos_btcusdt_4h_2024_01_03.csv",
        output_path=enriched_csv,
    )

    market_df = pd.read_csv(enriched_csv)
    market_df["timestamp"] = pd.to_datetime(market_df["timestamp"], errors="coerce")

    strategies = [
        ("OOS_LONG_FIB_V5_BASE", fib_v5_long_base_strategy),
        ("OOS_LONG_FIB_V5_MTF", fib_v5_long_with_mtf_filter),
    ]

    summaries = []
    all_diagnostics = []

    print("DIAGNOSTICO MAE/MFE — FIB V5 LONG")
    print("=" * 90)
    print("Dataset: BTCUSDT spot, 2024-01-01 a 2024-03-01")
    print()

    for strategy_name, strategy_func in strategies:
        summary_row, diagnostics_df = run_diagnostic_for_strategy(
            strategy_name=strategy_name,
            strategy_func=strategy_func,
            enriched_csv=enriched_csv,
            market_df=market_df,
        )

        summaries.append(summary_row)

        if not diagnostics_df.empty:
            all_diagnostics.append(diagnostics_df)

        print()
        print(f"RESUMEN: {strategy_name}")
        print("-" * 90)
        print(pd.DataFrame([summary_row]).to_string(index=False))

        print()
        print("DIAGNOSTICO POR EXIT_REASON Y DIAGNOSIS")
        print("-" * 90)
        print_grouped_table(diagnostics_df, ["exit_reason", "diagnosis"])

        print()
        print("DIAGNOSTICO POR REGIMEN 1H")
        print("-" * 90)
        print_grouped_table(diagnostics_df, ["entry_regime_1h"])

        print()
        print("DIAGNOSTICO POR REGIMEN 4H")
        print("-" * 90)
        print_grouped_table(diagnostics_df, ["entry_regime_4h"])

    summaries_df = pd.DataFrame(summaries)

    if all_diagnostics:
        diagnostics_all_df = pd.concat(all_diagnostics, ignore_index=True)
    else:
        diagnostics_all_df = pd.DataFrame()

    summary_output = Path("reports") / "long_mae_mfe_summary.csv"
    diagnostics_output = Path("reports") / "long_mae_mfe_diagnostics.csv"

    summaries_df.to_csv(summary_output, index=False)
    diagnostics_all_df.to_csv(diagnostics_output, index=False)

    print()
    print("RESUMEN FINAL")
    print("=" * 90)
    print(summaries_df.to_string(index=False))

    print()
    print("ARCHIVOS GENERADOS")
    print("=" * 90)
    print(f"- {summary_output}")
    print(f"- {diagnostics_output}")


if __name__ == "__main__":
    main()