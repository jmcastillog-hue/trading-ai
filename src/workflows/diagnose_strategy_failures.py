from pathlib import Path
import pandas as pd

from src.backtesting.backtesting_engine_v3 import run_backtest_v3
from src.market_structure.mtf_regime_filter import enrich_15m_with_mtf_regime
from src.market_structure.regime_filter_v2 import calculate_atr, calculate_rsi
from src.strategies.fib_v5_mtf_strategy import fib_v5_short_with_mtf_filter
from src.strategies.fib_v5_mtf_liquidity_v2_strategy import (
    fib_v5_short_with_mtf_and_liquidity_v2_filter,
)
from src.workflows.robust_validate_short_candidates import (
    build_short_config,
    classify_market_window,
)
from src.workflows.validate_long_v2_candidate_robust import (
    build_config as build_long_config,
    calculate_market_return,
    download_binance_klines_range,
    long_v2_candidate_signal,
)


def safe_float(value, default=None):
    try:
        if value is None or pd.isna(value):
            return default
        return float(value)
    except Exception:
        return default


def safe_int(value, default=0):
    try:
        if value is None or pd.isna(value):
            return default
        return int(value)
    except Exception:
        return default


def add_diagnostic_features(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy()

    result["timestamp"] = pd.to_datetime(result["timestamp"], errors="coerce")
    result = result.sort_values("timestamp").reset_index(drop=True)

    for col in ["open", "high", "low", "close", "volume"]:
        if col in result.columns:
            result[col] = pd.to_numeric(result[col], errors="coerce")

    result["ema20_diag"] = result["close"].ewm(span=20, adjust=False).mean()
    result["ema50_diag"] = result["close"].ewm(span=50, adjust=False).mean()
    result["ema200_diag"] = result["close"].ewm(span=200, adjust=False).mean()
    result["atr14_diag"] = calculate_atr(result, period=14)
    result["rsi14_diag"] = calculate_rsi(result["close"], period=14)

    result["distance_close_ema20_atr_diag"] = (
        (result["close"] - result["ema20_diag"])
        / result["atr14_diag"].replace(0, pd.NA)
    )

    result["distance_close_ema50_atr_diag"] = (
        (result["close"] - result["ema50_diag"])
        / result["atr14_diag"].replace(0, pd.NA)
    )

    result["return_24_diag"] = result["close"].pct_change(24)
    result["return_96_diag"] = result["close"].pct_change(96)

    rolling_high = result["high"].rolling(96, min_periods=20).max()
    rolling_low = result["low"].rolling(96, min_periods=20).min()

    result["range_high_96_diag"] = rolling_high
    result["range_low_96_diag"] = rolling_low
    result["range_position_96_diag"] = (
        (result["close"] - rolling_low)
        / (rolling_high - rolling_low).replace(0, pd.NA)
    )

    return result


def bucket_ema20_distance(value) -> str:
    value = safe_float(value, 0.0)

    if value <= -2.0:
        return "BELOW_EMA20_GT_2ATR"
    if value <= -1.0:
        return "BELOW_EMA20_1_TO_2ATR"
    if value < 0:
        return "BELOW_EMA20_LT_1ATR"
    if value < 1.0:
        return "ABOVE_EMA20_LT_1ATR"
    if value < 2.0:
        return "ABOVE_EMA20_1_TO_2ATR"

    return "ABOVE_EMA20_GT_2ATR"


def bucket_range_position(value) -> str:
    value = safe_float(value, 0.5)

    if value <= 0.15:
        return "LOW_RANGE_0_15"
    if value <= 0.35:
        return "LOW_MID_RANGE_15_35"
    if value <= 0.65:
        return "MID_RANGE_35_65"
    if value <= 0.85:
        return "HIGH_MID_RANGE_65_85"

    return "HIGH_RANGE_85_100"


def get_trade_exit_index(trade: pd.Series, entry_index: int, max_index: int) -> int:
    exit_index = safe_int(trade.get("exit_index"), None)

    if exit_index is not None:
        return max(0, min(exit_index, max_index))

    holding_bars = safe_int(trade.get("holding_bars"), 1)
    return max(0, min(entry_index + holding_bars, max_index))


def estimate_trade_risk(
    trade: pd.Series,
    market_row: pd.Series,
    entry_price: float,
    direction: str,
    config,
) -> float:
    stop_loss = safe_float(trade.get("stop_loss"), None)

    if stop_loss is not None:
        risk = abs(stop_loss - entry_price)
        if risk > 0:
            return risk

    atr = safe_float(market_row.get("atr14_diag"), 0.0)

    if atr and atr > 0:
        return atr * float(config.atr_multiplier)

    return entry_price * 0.01


def calculate_mfe_mae_r(
    market_df: pd.DataFrame,
    entry_index: int,
    exit_index: int,
    entry_price: float,
    risk: float,
    direction: str,
    post_bars: int = 96,
) -> dict:
    if risk <= 0:
        return {
            "mfe_r": 0.0,
            "mae_r": 0.0,
            "post_exit_favorable_r": 0.0,
        }

    trade_window = market_df.iloc[entry_index : exit_index + 1]

    if trade_window.empty:
        return {
            "mfe_r": 0.0,
            "mae_r": 0.0,
            "post_exit_favorable_r": 0.0,
        }

    post_window = market_df.iloc[
        exit_index + 1 : min(exit_index + post_bars + 1, len(market_df))
    ]

    if direction == "LONG":
        max_high = float(trade_window["high"].max())
        min_low = float(trade_window["low"].min())

        favorable_move = max_high - entry_price
        adverse_move = entry_price - min_low

        if post_window.empty:
            post_favorable_move = 0.0
        else:
            post_favorable_move = float(post_window["high"].max()) - entry_price

    else:
        min_low = float(trade_window["low"].min())
        max_high = float(trade_window["high"].max())

        favorable_move = entry_price - min_low
        adverse_move = max_high - entry_price

        if post_window.empty:
            post_favorable_move = 0.0
        else:
            post_favorable_move = entry_price - float(post_window["low"].min())

    return {
        "mfe_r": favorable_move / risk,
        "mae_r": -adverse_move / risk,
        "post_exit_favorable_r": post_favorable_move / risk,
    }


def classify_failure_reason(
    direction: str,
    net_pnl: float,
    exit_reason: str,
    market_window_type: str,
    mfe_r: float,
    mae_r: float,
    post_exit_favorable_r: float,
    entry_distance_ema20_atr: float,
    range_position: float,
    rsi: float,
) -> str:
    if net_pnl > 0:
        if mfe_r >= 2.0:
            return "GOOD_TRADE_FULL_FOLLOW_THROUGH"
        return "SMALL_WIN_OR_PARTIAL_FOLLOW_THROUGH"

    if direction == "SHORT":
        if market_window_type in {"BULLISH_MARKET", "MILD_BULLISH_MARKET"}:
            return "SHORT_AGAINST_BULLISH_MARKET"

        if entry_distance_ema20_atr <= -1.5 or range_position <= 0.20 or rsi <= 35:
            return "SHORTING_OVERSOLD_EXTENSION"

    if direction == "LONG":
        if market_window_type in {"BEARISH_MARKET", "MILD_BEARISH_MARKET"}:
            return "LONG_AGAINST_BEARISH_MARKET"

        if entry_distance_ema20_atr >= 1.5 or range_position >= 0.80 or rsi >= 70:
            return "BUYING_OVERBOUGHT_EXTENSION"

    if mfe_r < 0.30:
        return "POOR_ENTRY_NO_FOLLOW_THROUGH"

    if mfe_r >= 1.0 and post_exit_favorable_r >= 2.0:
        return "STOPPED_THEN_WORKED_LATER"

    if mfe_r >= 1.0:
        return "HAD_PROFIT_BUT_EXITED_LOSS"

    if post_exit_favorable_r >= 2.0:
        return "EARLY_ENTRY_OR_BAD_STOP"

    if exit_reason == "MAX_HOLDING_EXIT":
        return "TIME_EXIT_NO_EDGE"

    if mae_r <= -2.0:
        return "HIGH_ADVERSE_EXCURSION"

    return "GENERIC_FAILED_TRADE"


def diagnose_trade(
    trade: pd.Series,
    market_df: pd.DataFrame,
    window_name: str,
    strategy_name: str,
    direction: str,
    market_return_pct: float,
    config,
) -> dict:
    max_index = len(market_df) - 1

    entry_index = safe_int(trade.get("entry_index"), 0)
    entry_index = max(0, min(entry_index, max_index))

    exit_index = get_trade_exit_index(trade, entry_index, max_index)

    entry_row = market_df.iloc[entry_index]

    entry_price = safe_float(
        trade.get("entry_price"),
        safe_float(entry_row.get("close"), 0.0),
    )

    exit_price = safe_float(
        trade.get("exit_price"),
        safe_float(market_df.iloc[exit_index].get("close"), entry_price),
    )

    risk = estimate_trade_risk(
        trade=trade,
        market_row=entry_row,
        entry_price=entry_price,
        direction=direction,
        config=config,
    )

    excursion = calculate_mfe_mae_r(
        market_df=market_df,
        entry_index=entry_index,
        exit_index=exit_index,
        entry_price=entry_price,
        risk=risk,
        direction=direction,
    )

    net_pnl = safe_float(trade.get("net_pnl"), 0.0)
    exit_reason = str(trade.get("exit_reason", "UNKNOWN"))

    entry_distance_ema20_atr = safe_float(
        entry_row.get("distance_close_ema20_atr_diag"),
        0.0,
    )

    range_position = safe_float(entry_row.get("range_position_96_diag"), 0.5)
    rsi = safe_float(entry_row.get("rsi14_diag"), 50.0)

    market_window_type = classify_market_window(market_return_pct)

    failure_reason = classify_failure_reason(
        direction=direction,
        net_pnl=net_pnl,
        exit_reason=exit_reason,
        market_window_type=market_window_type,
        mfe_r=excursion["mfe_r"],
        mae_r=excursion["mae_r"],
        post_exit_favorable_r=excursion["post_exit_favorable_r"],
        entry_distance_ema20_atr=entry_distance_ema20_atr,
        range_position=range_position,
        rsi=rsi,
    )

    row = trade.to_dict()

    row.update(
        {
            "window_name": window_name,
            "strategy_name": strategy_name,
            "direction": direction,
            "market_return_pct": market_return_pct,
            "market_window_type": market_window_type,
            "entry_timestamp": entry_row.get("timestamp", None),
            "entry_index": entry_index,
            "exit_index": exit_index,
            "entry_price_diag": entry_price,
            "exit_price_diag": exit_price,
            "risk_per_unit_diag": risk,
            "mfe_r": excursion["mfe_r"],
            "mae_r": excursion["mae_r"],
            "post_exit_favorable_r": excursion["post_exit_favorable_r"],
            "failure_reason": failure_reason,
            "entry_distance_ema20_atr": entry_distance_ema20_atr,
            "entry_distance_bucket": bucket_ema20_distance(entry_distance_ema20_atr),
            "entry_range_position": range_position,
            "entry_range_bucket": bucket_range_position(range_position),
            "entry_rsi": rsi,
            "entry_return_24": safe_float(entry_row.get("return_24_diag"), 0.0),
            "entry_return_96": safe_float(entry_row.get("return_96_diag"), 0.0),
            "regime_1h": entry_row.get("regime_1h", "UNKNOWN"),
            "regime_4h": entry_row.get("regime_4h", "UNKNOWN"),
            "regime_pair": (
                f"{entry_row.get('regime_1h', 'UNKNOWN')} | "
                f"{entry_row.get('regime_4h', 'UNKNOWN')}"
            ),
        }
    )

    return row


def summarize_backtest_result(
    window_name: str,
    strategy_name: str,
    direction: str,
    market_return_pct: float,
    trades_df: pd.DataFrame,
    summary: dict,
) -> dict:
    return {
        "window_name": window_name,
        "strategy_name": strategy_name,
        "direction": direction,
        "market_return_pct": market_return_pct,
        "market_window_type": classify_market_window(market_return_pct),
        "total_trades": int(summary.get("total_trades", 0)),
        "wins": int(summary.get("wins", 0)),
        "losses": int(summary.get("losses", 0)),
        "total_return_pct": float(summary.get("total_return_pct", 0.0)),
        "win_rate": float(summary.get("win_rate", 0.0)),
        "profit_factor": summary.get("profit_factor", None),
        "expectancy": float(summary.get("expectancy", 0.0)),
        "max_drawdown_pct": float(summary.get("max_drawdown_pct", 0.0)),
    }


def get_strategy_suite():
    return [
        {
            "strategy_name": "SHORT_FIB_V5_MTF",
            "direction": "SHORT",
            "strategy_func": fib_v5_short_with_mtf_filter,
            "config": build_short_config(),
        },
        {
            "strategy_name": "SHORT_FIB_V5_MTF_LIQUIDITY_V2",
            "direction": "SHORT",
            "strategy_func": fib_v5_short_with_mtf_and_liquidity_v2_filter,
            "config": build_short_config(),
        },
        {
            "strategy_name": "LONG_V2_CANDIDATE",
            "direction": "LONG",
            "strategy_func": long_v2_candidate_signal,
            "config": build_long_config(),
        },
    ]


def validate_window(
    symbol: str,
    window_name: str,
    start_date: str,
    end_date: str,
) -> tuple[list[dict], pd.DataFrame]:
    data_dir = Path("data") / "strategy_failure_diagnostics"
    reports_dir = Path("reports") / "strategy_failure_diagnostics"

    data_dir.mkdir(parents=True, exist_ok=True)
    reports_dir.mkdir(parents=True, exist_ok=True)

    base_name = f"{symbol.lower()}_{window_name}"

    csv_15m = data_dir / f"{base_name}_15m.csv"
    csv_1h = data_dir / f"{base_name}_1h.csv"
    csv_4h = data_dir / f"{base_name}_4h.csv"
    enriched_csv = reports_dir / f"{base_name}_15m_with_mtf_diag.csv"

    print()
    print(f"FAILURE DIAGNOSTIC WINDOW: {window_name}")
    print("=" * 100)

    if not csv_15m.exists():
        download_binance_klines_range(symbol, "15m", start_date, end_date, csv_15m)

    if not csv_1h.exists():
        download_binance_klines_range(symbol, "1h", start_date, end_date, csv_1h)

    if not csv_4h.exists():
        download_binance_klines_range(symbol, "4h", start_date, end_date, csv_4h)

    market_return_pct = calculate_market_return(csv_15m)

    market_df = enrich_15m_with_mtf_regime(
        entry_csv_path=csv_15m,
        h1_csv_path=csv_1h,
        h4_csv_path=csv_4h,
        output_path=enriched_csv,
    )

    market_df = add_diagnostic_features(market_df)
    market_df.to_csv(enriched_csv, index=False)

    strategy_summaries = []
    diagnostic_rows = []

    for item in get_strategy_suite():
        strategy_name = item["strategy_name"]
        direction = item["direction"]
        strategy_func = item["strategy_func"]
        config = item["config"]

        trades_df, summary = run_backtest_v3(
            csv_path=enriched_csv,
            config=config,
            output_dir=reports_dir,
            strategy_func=strategy_func,
        )

        summary_row = summarize_backtest_result(
            window_name=window_name,
            strategy_name=strategy_name,
            direction=direction,
            market_return_pct=market_return_pct,
            trades_df=trades_df,
            summary=summary,
        )

        strategy_summaries.append(summary_row)

        if not trades_df.empty:
            for _, trade in trades_df.iterrows():
                diagnostic_rows.append(
                    diagnose_trade(
                        trade=trade,
                        market_df=market_df,
                        window_name=window_name,
                        strategy_name=strategy_name,
                        direction=direction,
                        market_return_pct=market_return_pct,
                        config=config,
                    )
                )

        print(
            f"{strategy_name} | "
            f"direction={direction} | "
            f"market={market_return_pct:.2%} | "
            f"type={summary_row['market_window_type']} | "
            f"trades={summary_row['total_trades']} | "
            f"return={summary_row['total_return_pct']:.2%} | "
            f"wr={summary_row['win_rate']:.2%} | "
            f"pf={summary_row['profit_factor']} | "
            f"mdd={summary_row['max_drawdown_pct']:.2%}"
        )

    diagnostics_df = pd.DataFrame(diagnostic_rows)

    return strategy_summaries, diagnostics_df


def print_grouped_diagnostics(diagnostics_df: pd.DataFrame):
    print()
    print("FAILURE REASON BY STRATEGY")
    print("=" * 100)

    if diagnostics_df.empty:
        print("Sin trades.")
        return

    grouped = (
        diagnostics_df.groupby(["strategy_name", "failure_reason"])
        .agg(
            trades=("entry_index", "count"),
            total_net_pnl=("net_pnl", "sum"),
            avg_net_pnl=("net_pnl", "mean"),
            avg_mfe_r=("mfe_r", "mean"),
            avg_mae_r=("mae_r", "mean"),
            avg_post_exit_favorable_r=("post_exit_favorable_r", "mean"),
        )
        .reset_index()
        .sort_values(by=["strategy_name", "total_net_pnl"], ascending=[True, True])
    )

    print(grouped.to_string(index=False))

    print()
    print("FAILURE REASON BY MARKET TYPE")
    print("=" * 100)

    grouped_market = (
        diagnostics_df.groupby(["strategy_name", "market_window_type", "failure_reason"])
        .agg(
            trades=("entry_index", "count"),
            total_net_pnl=("net_pnl", "sum"),
            avg_net_pnl=("net_pnl", "mean"),
            avg_mfe_r=("mfe_r", "mean"),
            avg_mae_r=("mae_r", "mean"),
        )
        .reset_index()
        .sort_values(by=["strategy_name", "total_net_pnl"], ascending=[True, True])
    )

    print(grouped_market.to_string(index=False))

    print()
    print("ENTRY EXTENSION BUCKETS")
    print("=" * 100)

    extension_grouped = (
        diagnostics_df.groupby(["strategy_name", "entry_distance_bucket", "entry_range_bucket"])
        .agg(
            trades=("entry_index", "count"),
            total_net_pnl=("net_pnl", "sum"),
            avg_net_pnl=("net_pnl", "mean"),
            avg_mfe_r=("mfe_r", "mean"),
            avg_mae_r=("mae_r", "mean"),
        )
        .reset_index()
        .sort_values(by=["strategy_name", "total_net_pnl"], ascending=[True, True])
    )

    print(extension_grouped.to_string(index=False))

    print()
    print("REGIME PAIR FAILURE MAP")
    print("=" * 100)

    regime_grouped = (
        diagnostics_df.groupby(["strategy_name", "regime_pair", "failure_reason"])
        .agg(
            trades=("entry_index", "count"),
            total_net_pnl=("net_pnl", "sum"),
            avg_net_pnl=("net_pnl", "mean"),
            avg_mfe_r=("mfe_r", "mean"),
            avg_mae_r=("mae_r", "mean"),
        )
        .reset_index()
        .sort_values(by=["strategy_name", "total_net_pnl"], ascending=[True, True])
    )

    print(regime_grouped.to_string(index=False))


def print_strategy_summary(summary_df: pd.DataFrame):
    print()
    print("STRATEGY FAILURE SUMMARY")
    print("=" * 100)

    if summary_df.empty:
        print("Sin resumen.")
        return

    aggregate = (
        summary_df.groupby(["strategy_name", "direction"])
        .agg(
            windows=("window_name", "count"),
            total_trades=("total_trades", "sum"),
            avg_return=("total_return_pct", "mean"),
            avg_win_rate=("win_rate", "mean"),
            avg_profit_factor=("profit_factor", "mean"),
            worst_drawdown=("max_drawdown_pct", "min"),
        )
        .reset_index()
        .sort_values(by="avg_return", ascending=False)
    )

    print(aggregate.to_string(index=False))


def print_final_decision(diagnostics_df: pd.DataFrame, summary_df: pd.DataFrame):
    print()
    print("FINAL FAILURE DIAGNOSTIC DECISION")
    print("=" * 100)

    if diagnostics_df.empty or summary_df.empty:
        print("NO_DATA")
        return

    losing_trades = diagnostics_df[diagnostics_df["net_pnl"] <= 0].copy()

    if losing_trades.empty:
        print("No losing trades detected.")
        return

    failure_counts = (
        losing_trades.groupby("failure_reason")
        .agg(
            trades=("entry_index", "count"),
            total_net_pnl=("net_pnl", "sum"),
        )
        .reset_index()
        .sort_values(by="total_net_pnl")
    )

    print(failure_counts.to_string(index=False))

    print()
    print("Interpretacion preliminar:")
    print("- Si domina SHORT_AGAINST_BULLISH_MARKET / LONG_AGAINST_BEARISH_MARKET, falta filtro direccional.")
    print("- Si domina SHORTING_OVERSOLD_EXTENSION / BUYING_OVERBOUGHT_EXTENSION, la entrada llega tarde.")
    print("- Si domina POOR_ENTRY_NO_FOLLOW_THROUGH, falta confirmacion estructural.")
    print("- Si domina STOPPED_THEN_WORKED_LATER, el problema es timing/stop/re-entry.")
    print("- Si domina HAD_PROFIT_BUT_EXITED_LOSS, falta gestion activa de salida.")
    print()
    print("Decision: no optimizar parametros hasta identificar la causa dominante.")


def main():
    symbol = "BTCUSDT"

    windows = [
        ("2024_01_03", "2024-01-01", "2024-03-01"),
        ("2024_03_05", "2024-03-01", "2024-05-01"),
        ("2024_05_07", "2024-05-01", "2024-07-01"),
        ("2024_07_09", "2024-07-01", "2024-09-01"),
        ("2024_09_11", "2024-09-01", "2024-11-01"),
        ("2024_11_2025_01", "2024-11-01", "2025-01-01"),
        ("2025_01_03", "2025-01-01", "2025-03-01"),
        ("2025_03_05", "2025-03-01", "2025-05-01"),
        ("2025_05_07", "2025-05-01", "2025-07-01"),
        ("2025_07_09", "2025-07-01", "2025-09-01"),
        ("2025_09_11", "2025-09-01", "2025-11-01"),
        ("2025_11_2026_01", "2025-11-01", "2026-01-01"),
    ]

    print("STRATEGY FAILURE DIAGNOSTICS")
    print("=" * 100)
    print("Strategies:")
    print("- SHORT_FIB_V5_MTF")
    print("- SHORT_FIB_V5_MTF_LIQUIDITY_V2")
    print("- LONG_V2_CANDIDATE")
    print()

    all_summaries = []
    all_diagnostics = []

    for window_name, start_date, end_date in windows:
        summaries, diagnostics_df = validate_window(
            symbol=symbol,
            window_name=window_name,
            start_date=start_date,
            end_date=end_date,
        )

        all_summaries.extend(summaries)

        if not diagnostics_df.empty:
            all_diagnostics.append(diagnostics_df)

    summary_df = pd.DataFrame(all_summaries)

    if all_diagnostics:
        diagnostics_all_df = pd.concat(all_diagnostics, ignore_index=True)
    else:
        diagnostics_all_df = pd.DataFrame()

    reports_dir = Path("reports") / "strategy_failure_diagnostics"
    reports_dir.mkdir(parents=True, exist_ok=True)

    summary_output = reports_dir / "strategy_failure_summary.csv"
    diagnostics_output = reports_dir / "strategy_failure_trade_diagnostics.csv"

    summary_df.to_csv(summary_output, index=False)
    diagnostics_all_df.to_csv(diagnostics_output, index=False)

    print_strategy_summary(summary_df)
    print_grouped_diagnostics(diagnostics_all_df)
    print_final_decision(diagnostics_all_df, summary_df)

    print()
    print("ARCHIVOS GENERADOS")
    print("=" * 100)
    print(f"- {summary_output}")
    print(f"- {diagnostics_output}")


if __name__ == "__main__":
    main()