from pathlib import Path
from datetime import datetime, timezone
import time
import requests
import pandas as pd

from src.backtesting.backtesting_engine_v3 import BacktestConfig, run_backtest_v3
from src.market_structure.mtf_regime_filter import (
    enrich_15m_with_mtf_regime,
    long_allowed_by_mtf_regime,
)


BINANCE_KLINES_URL = "https://api.binance.com/api/v3/klines"


def to_milliseconds(date_str: str) -> int:
    dt = datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    return int(dt.timestamp() * 1000)


def download_binance_klines_range(
    symbol: str,
    interval: str,
    start_date: str,
    end_date: str,
    output_path: Path,
    limit: int = 1000,
) -> Path:
    """
    Downloads Binance spot klines over a date range and saves CSV.

    This workflow keeps the downloader self-contained so robust validation
    does not depend on older helper signatures.
    """

    output_path.parent.mkdir(parents=True, exist_ok=True)

    start_ms = to_milliseconds(start_date)
    end_ms = to_milliseconds(end_date)

    rows = []
    current_start = start_ms

    while current_start < end_ms:
        params = {
            "symbol": symbol,
            "interval": interval,
            "startTime": current_start,
            "endTime": end_ms,
            "limit": limit,
        }

        response = requests.get(BINANCE_KLINES_URL, params=params, timeout=30)
        response.raise_for_status()

        data = response.json()

        if not data:
            break

        rows.extend(data)

        last_open_time = int(data[-1][0])
        next_start = last_open_time + 1

        if next_start <= current_start:
            break

        current_start = next_start

        time.sleep(0.15)

    if not rows:
        raise RuntimeError(
            f"No data downloaded for {symbol} {interval} {start_date} {end_date}"
        )

    df = pd.DataFrame(
        rows,
        columns=[
            "open_time",
            "open",
            "high",
            "low",
            "close",
            "volume",
            "close_time",
            "quote_asset_volume",
            "number_of_trades",
            "taker_buy_base_volume",
            "taker_buy_quote_volume",
            "ignore",
        ],
    )

    df["timestamp"] = pd.to_datetime(df["open_time"], unit="ms", utc=True)
    df["timestamp"] = df["timestamp"].dt.tz_convert(None)

    keep_cols = [
        "timestamp",
        "open",
        "high",
        "low",
        "close",
        "volume",
        "close_time",
        "quote_asset_volume",
        "number_of_trades",
        "taker_buy_base_volume",
        "taker_buy_quote_volume",
    ]

    df = df[keep_cols].copy()

    numeric_cols = [
        "open",
        "high",
        "low",
        "close",
        "volume",
        "quote_asset_volume",
        "taker_buy_base_volume",
        "taker_buy_quote_volume",
    ]

    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df["number_of_trades"] = pd.to_numeric(df["number_of_trades"], errors="coerce")

    df = df.drop_duplicates(subset=["timestamp"]).sort_values("timestamp")
    df.to_csv(output_path, index=False)

    return output_path


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


def long_v2_candidate_signal(df: pd.DataFrame, index: int, config=None) -> str:
    """
    LONG V2 candidate from Fase 1.14.

    Entry:
    - Fib 0.500 - 0.618
    - break previous high
    - MTF filter enabled

    Risk/exit is handled by Backtesting Engine V3 config.
    """

    lookback_bars = 48
    fib_entry_low = 0.500
    fib_entry_high = 0.618
    min_impulse_pct = 0.02

    if index < lookback_bars:
        return "NONE"

    window = df.iloc[index - lookback_bars:index]

    if window.empty:
        return "NONE"

    impulse_low_idx = window["low"].idxmin()
    impulse_low = float(df.loc[impulse_low_idx, "low"])

    after_low = df.loc[impulse_low_idx:index - 1]

    if after_low.empty:
        return "NONE"

    impulse_high_idx = after_low["high"].idxmax()
    impulse_high = float(df.loc[impulse_high_idx, "high"])

    if impulse_high <= impulse_low:
        return "NONE"

    impulse_pct = (impulse_high / impulse_low) - 1

    if impulse_pct < min_impulse_pct:
        return "NONE"

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
        return "NONE"

    previous_high = float(df.iloc[index - 1]["high"])

    if candle_close <= previous_high:
        return "NONE"

    regime_1h = row.get("regime_1h", "UNKNOWN")
    regime_4h = row.get("regime_4h", "UNKNOWN")

    if not long_allowed_by_mtf_regime(regime_1h, regime_4h):
        return "NONE"

    return "LONG"


def summarize_window(
    window_name: str,
    start_date: str,
    end_date: str,
    market_return_pct: float,
    trades_df: pd.DataFrame,
    summary: dict,
) -> dict:
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

        if "holding_bars" in trades_df.columns:
            avg_holding_bars = float(trades_df["holding_bars"].mean())

    return {
        "window_name": window_name,
        "start_date": start_date,
        "end_date": end_date,
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
        "avg_holding_bars": avg_holding_bars,
    }


def classify_window(row) -> str:
    trades = int(row["total_trades"])
    total_return_pct = float(row["total_return_pct"])
    max_drawdown_pct = float(row["max_drawdown_pct"])
    pf = row["profit_factor"]

    if trades < 10:
        return "INSUFFICIENT_TRADES"

    if pf is None or pd.isna(pf):
        return "INVALID_PF"

    pf = float(pf)

    if total_return_pct > 0.05 and pf >= 1.25 and max_drawdown_pct > -0.10:
        return "PASSED"

    if total_return_pct > 0 and pf >= 1.05:
        return "WEAK_PASS"

    if total_return_pct > -0.03 and pf >= 0.90:
        return "NEAR_BREAKEVEN"

    return "FAILED"


def calculate_market_return(csv_path: Path) -> float:
    df = pd.read_csv(csv_path)

    if len(df) < 2:
        return 0.0

    start_close = float(df.iloc[0]["close"])
    end_close = float(df.iloc[-1]["close"])

    return (end_close / start_close) - 1


def validate_window(
    symbol: str,
    window_name: str,
    start_date: str,
    end_date: str,
) -> dict:
    data_dir = Path("data") / "robust_long_v2"
    reports_dir = Path("reports") / "robust_long_v2"

    data_dir.mkdir(parents=True, exist_ok=True)
    reports_dir.mkdir(parents=True, exist_ok=True)

    base_name = f"{symbol.lower()}_{window_name}"

    csv_15m = data_dir / f"{base_name}_15m.csv"
    csv_1h = data_dir / f"{base_name}_1h.csv"
    csv_4h = data_dir / f"{base_name}_4h.csv"

    enriched_csv = reports_dir / f"{base_name}_15m_with_mtf.csv"

    print()
    print(f"DESCARGANDO / VALIDANDO DATOS: {window_name}")
    print("-" * 100)

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
        output_path=enriched_csv,
    )

    trades_df, summary = run_backtest_v3(
        csv_path=enriched_csv,
        config=build_config(),
        output_dir=reports_dir,
        strategy_func=long_v2_candidate_signal,
    )

    trades_output = reports_dir / f"{base_name}_trades.csv"
    trades_df.to_csv(trades_output, index=False)

    row = summarize_window(
        window_name=window_name,
        start_date=start_date,
        end_date=end_date,
        market_return_pct=market_return_pct,
        trades_df=trades_df,
        summary=summary,
    )

    print(
        f"{window_name} | "
        f"market={market_return_pct:.2%} | "
        f"trades={row['total_trades']} | "
        f"return={row['total_return_pct']:.2%} | "
        f"wr={row['win_rate']:.2%} | "
        f"pf={row['profit_factor']} | "
        f"mdd={row['max_drawdown_pct']:.2%}"
    )

    return row


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

    print("VALIDACION ROBUSTA — LONG V2 CANDIDATE")
    print("=" * 100)
    print("Candidate: Fib 0.500-0.618 + break_prev_high + MTF")
    print("Risk: ATR 1.5 | RR 2.0 | Max holding 96")
    print()

    results = []

    for window_name, start_date, end_date in windows:
        row = validate_window(
            symbol=symbol,
            window_name=window_name,
            start_date=start_date,
            end_date=end_date,
        )
        results.append(row)

    results_df = pd.DataFrame(results)
    results_df["validation_status"] = results_df.apply(classify_window, axis=1)

    output_path = Path("reports") / "long_v2_candidate_robust_validation.csv"
    results_df.to_csv(output_path, index=False)

    print()
    print("RESULTADOS POR VENTANA")
    print("=" * 100)
    print(
        results_df[
            [
                "window_name",
                "validation_status",
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
                "avg_holding_bars",
            ]
        ].to_string(index=False)
    )

    total_windows = len(results_df)
    passed = int((results_df["validation_status"] == "PASSED").sum())
    weak_pass = int((results_df["validation_status"] == "WEAK_PASS").sum())
    near_breakeven = int((results_df["validation_status"] == "NEAR_BREAKEVEN").sum())
    failed = int((results_df["validation_status"] == "FAILED").sum())
    insufficient = int(
        (results_df["validation_status"] == "INSUFFICIENT_TRADES").sum()
    )

    avg_return = float(results_df["total_return_pct"].mean())
    avg_pf = float(results_df["profit_factor"].dropna().mean())
    worst_drawdown = float(results_df["max_drawdown_pct"].min())
    total_trades = int(results_df["total_trades"].sum())

    print()
    print("RESUMEN ROBUSTO")
    print("=" * 100)
    print(f"Total windows: {total_windows}")
    print(f"Passed: {passed}")
    print(f"Weak pass: {weak_pass}")
    print(f"Near breakeven: {near_breakeven}")
    print(f"Failed: {failed}")
    print(f"Insufficient trades: {insufficient}")
    print(f"Total trades: {total_trades}")
    print(f"Average return: {avg_return:.2%}")
    print(f"Average profit factor: {avg_pf:.4f}")
    print(f"Worst drawdown: {worst_drawdown:.2%}")

    print()
    print("DECISION PRELIMINAR")
    print("=" * 100)

    if passed >= 3 and failed <= 1 and avg_pf >= 1.15 and avg_return > 0:
        print("ROBUST_CANDIDATE")
        print("La estrategia merece pasar a una fase de refinamiento o paper trading limitado.")
    elif failed <= 2 and avg_pf >= 1.0 and avg_return > -0.02:
        print("REQUIRES_FILTERS")
        print("La estrategia tiene valor, pero necesita filtros adicionales antes de paper trading.")
    else:
        print("NOT_ROBUST")
        print("La estrategia no sobrevive validacion robusta. No pasar a paper trading.")

    print()
    print("ARCHIVO GENERADO")
    print("=" * 100)
    print(output_path)


if __name__ == "__main__":
    main()