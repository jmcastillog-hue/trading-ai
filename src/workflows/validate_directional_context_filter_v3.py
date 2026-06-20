from pathlib import Path
import pandas as pd

from src.market_structure.mtf_regime_filter import enrich_15m_with_mtf_regime
from src.backtesting.backtesting_engine_v3 import run_backtest_v3
from src.market_structure.directional_context_filter_v3 import (
    enrich_with_directional_context_v3,
)
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


def long_v2_with_directional_context_v3(df, index: int, config=None) -> str:
    base_signal = long_v2_candidate_signal(df, index, config)

    if base_signal != "LONG":
        return "NONE"

    row = df.iloc[index]

    if bool(row.get("long_allowed_v3", False)):
        return "LONG"

    return "NONE"


def short_mtf_with_directional_context_v3(df, index: int, config=None) -> str:
    base_signal = fib_v5_short_with_mtf_filter(df, index, config)

    if base_signal != "SHORT":
        return "NONE"

    row = df.iloc[index]

    if bool(row.get("short_allowed_v3", False)):
        return "SHORT"

    return "NONE"


def short_mtf_liquidity_v2_with_directional_context_v3(df, index: int, config=None) -> str:
    base_signal = fib_v5_short_with_mtf_and_liquidity_v2_filter(df, index, config)

    if base_signal != "SHORT":
        return "NONE"

    row = df.iloc[index]

    if bool(row.get("short_allowed_v3", False)):
        return "SHORT"

    return "NONE"


def classify_result(row) -> str:
    trades = int(row["total_trades"])
    total_return_pct = float(row["total_return_pct"])
    profit_factor = row["profit_factor"]
    max_drawdown_pct = float(row["max_drawdown_pct"])

    if trades < 5:
        return "INSUFFICIENT_TRADES"

    if profit_factor is None or pd.isna(profit_factor):
        if total_return_pct > 0 and int(row["losses"]) == 0:
            return "LOW_SAMPLE_ALL_WIN"
        return "INVALID_PF"

    profit_factor = float(profit_factor)

    if total_return_pct > 0.08 and profit_factor >= 1.25 and max_drawdown_pct > -0.10:
        return "PASSED"

    if total_return_pct > 0.03 and profit_factor >= 1.10:
        return "WEAK_PASS"

    if total_return_pct > -0.03 and profit_factor >= 0.90:
        return "NEAR_BREAKEVEN"

    return "FAILED"


def summarize_strategy(
    window_name: str,
    strategy_name: str,
    direction: str,
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

    row = {
        "window_name": window_name,
        "strategy_name": strategy_name,
        "direction": direction,
        "market_return_pct": market_return_pct,
        "market_window_type": classify_market_window(market_return_pct),
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

    row["window_status"] = classify_result(row)

    return row


def add_trade_context(
    trades_df: pd.DataFrame,
    market_df: pd.DataFrame,
    window_name: str,
    strategy_name: str,
    direction: str,
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
        row["direction"] = direction
        row["bias_1h_v3"] = entry_row.get("bias_1h_v3", "UNKNOWN")
        row["bias_4h_v3"] = entry_row.get("bias_4h_v3", "UNKNOWN")
        row["directional_context_v3"] = entry_row.get(
            "directional_context_v3",
            "UNKNOWN",
        )
        row["long_allowed_v3"] = entry_row.get("long_allowed_v3", False)
        row["short_allowed_v3"] = entry_row.get("short_allowed_v3", False)

        rows.append(row)

    return pd.DataFrame(rows)


def build_combined_context_dataset(
    csv_15m: Path,
    csv_1h: Path,
    csv_4h: Path,
    enriched_csv: Path,
    reports_dir: Path,
    base_name: str,
) -> pd.DataFrame:
    """
    Build one dataset containing:
    - original 15m OHLCV
    - old MTF regime columns required by existing FIB strategies
    - new Directional Context V3 columns

    This avoids breaking base strategies that depend on regime_1h/regime_4h.
    """

    mtf_csv = reports_dir / f"{base_name}_mtf_context.csv"
    directional_csv = reports_dir / f"{base_name}_directional_only.csv"

    mtf_df = enrich_15m_with_mtf_regime(
        entry_csv_path=csv_15m,
        h1_csv_path=csv_1h,
        h4_csv_path=csv_4h,
        output_path=mtf_csv,
    )

    directional_df = enrich_with_directional_context_v3(
        entry_csv_path=csv_15m,
        h1_csv_path=csv_1h,
        h4_csv_path=csv_4h,
        output_path=directional_csv,
    )

    mtf_df = mtf_df.copy()
    directional_df = directional_df.copy()

    mtf_df["timestamp"] = pd.to_datetime(mtf_df["timestamp"], errors="coerce")
    directional_df["timestamp"] = pd.to_datetime(
        directional_df["timestamp"],
        errors="coerce",
    )

    mtf_df = mtf_df.sort_values("timestamp").reset_index(drop=True)
    directional_df = directional_df.sort_values("timestamp").reset_index(drop=True)

    directional_cols = [
        "timestamp",
        "bias_1h_v3",
        "bias_4h_v3",
        "directional_context_v3",
        "long_allowed_v3",
        "short_allowed_v3",
    ]

    directional_cols = [
        col for col in directional_cols if col in directional_df.columns
    ]

    combined_df = pd.merge_asof(
        mtf_df,
        directional_df[directional_cols],
        on="timestamp",
        direction="nearest",
        tolerance=pd.Timedelta("1min"),
    )

    combined_df["bias_1h_v3"] = combined_df["bias_1h_v3"].fillna("UNKNOWN")
    combined_df["bias_4h_v3"] = combined_df["bias_4h_v3"].fillna("UNKNOWN")
    combined_df["directional_context_v3"] = combined_df[
        "directional_context_v3"
    ].fillna("NO_TRADE")
    combined_df["long_allowed_v3"] = combined_df["long_allowed_v3"].fillna(False)
    combined_df["short_allowed_v3"] = combined_df["short_allowed_v3"].fillna(False)

    combined_df.to_csv(enriched_csv, index=False)

    return combined_df

def validate_window(
    symbol: str,
    window_name: str,
    start_date: str,
    end_date: str,
) -> tuple[list[dict], pd.DataFrame]:
    data_dir = Path("data") / "directional_context_v3"
    reports_dir = Path("reports") / "directional_context_v3"

    data_dir.mkdir(parents=True, exist_ok=True)
    reports_dir.mkdir(parents=True, exist_ok=True)

    base_name = f"{symbol.lower()}_{window_name}"

    csv_15m = data_dir / f"{base_name}_15m.csv"
    csv_1h = data_dir / f"{base_name}_1h.csv"
    csv_4h = data_dir / f"{base_name}_4h.csv"

    enriched_csv = reports_dir / f"{base_name}_directional_context_v3.csv"

    print()
    print(f"DIRECTIONAL CONTEXT V3 WINDOW: {window_name}")
    print("=" * 100)

    if not csv_15m.exists():
        download_binance_klines_range(symbol, "15m", start_date, end_date, csv_15m)

    if not csv_1h.exists():
        download_binance_klines_range(symbol, "1h", start_date, end_date, csv_1h)

    if not csv_4h.exists():
        download_binance_klines_range(symbol, "4h", start_date, end_date, csv_4h)

    market_return_pct = calculate_market_return(csv_15m)

    market_df = build_combined_context_dataset(
        csv_15m=csv_15m,
        csv_1h=csv_1h,
        csv_4h=csv_4h,
        enriched_csv=enriched_csv,
        reports_dir=reports_dir,
        base_name=base_name,
    )

    strategies = [
        {
            "strategy_name": "LONG_V2_BASE",
            "direction": "LONG",
            "strategy_func": long_v2_candidate_signal,
            "config": build_long_config(),
        },
        {
            "strategy_name": "LONG_V2_DIRECTIONAL_V3",
            "direction": "LONG",
            "strategy_func": long_v2_with_directional_context_v3,
            "config": build_long_config(),
        },
        {
            "strategy_name": "SHORT_FIB_V5_MTF_BASE",
            "direction": "SHORT",
            "strategy_func": fib_v5_short_with_mtf_filter,
            "config": build_short_config(),
        },
        {
            "strategy_name": "SHORT_FIB_V5_MTF_DIRECTIONAL_V3",
            "direction": "SHORT",
            "strategy_func": short_mtf_with_directional_context_v3,
            "config": build_short_config(),
        },
        {
            "strategy_name": "SHORT_FIB_V5_MTF_LIQUIDITY_V2_BASE",
            "direction": "SHORT",
            "strategy_func": fib_v5_short_with_mtf_and_liquidity_v2_filter,
            "config": build_short_config(),
        },
        {
            "strategy_name": "SHORT_FIB_V5_MTF_LIQUIDITY_V2_DIRECTIONAL_V3",
            "direction": "SHORT",
            "strategy_func": short_mtf_liquidity_v2_with_directional_context_v3,
            "config": build_short_config(),
        },
    ]

    window_results = []
    window_trades = []

    for item in strategies:
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

        result = summarize_strategy(
            window_name=window_name,
            strategy_name=strategy_name,
            direction=direction,
            market_return_pct=market_return_pct,
            trades_df=trades_df,
            summary=summary,
        )

        window_results.append(result)

        trades_with_context = add_trade_context(
            trades_df=trades_df,
            market_df=market_df,
            window_name=window_name,
            strategy_name=strategy_name,
            direction=direction,
        )

        if not trades_with_context.empty:
            window_trades.append(trades_with_context)

        print(
            f"{strategy_name} | "
            f"dir={direction} | "
            f"market={market_return_pct:.2%} | "
            f"type={result['market_window_type']} | "
            f"trades={result['total_trades']} | "
            f"return={result['total_return_pct']:.2%} | "
            f"wr={result['win_rate']:.2%} | "
            f"pf={result['profit_factor']} | "
            f"mdd={result['max_drawdown_pct']:.2%} | "
            f"status={result['window_status']}"
        )

    if window_trades:
        trades_window_df = pd.concat(window_trades, ignore_index=True)
    else:
        trades_window_df = pd.DataFrame()

    return window_results, trades_window_df


def build_aggregate(results_df: pd.DataFrame) -> pd.DataFrame:
    rows = []

    for strategy_name, group in results_df.groupby("strategy_name"):
        group = group.copy()

        pf_series = pd.to_numeric(group["profit_factor"], errors="coerce")

        compound_return = float((1 + group["total_return_pct"]).prod() - 1)
        avg_return = float(group["total_return_pct"].mean())
        avg_pf = float(pf_series.dropna().mean()) if len(pf_series.dropna()) else 0.0
        worst_drawdown = float(group["max_drawdown_pct"].min())
        total_trades = int(group["total_trades"].sum())
        avg_trades = float(group["total_trades"].mean())

        passed = int((group["window_status"] == "PASSED").sum())
        weak_pass = int((group["window_status"] == "WEAK_PASS").sum())
        near_breakeven = int((group["window_status"] == "NEAR_BREAKEVEN").sum())
        failed = int((group["window_status"] == "FAILED").sum())
        insufficient = int((group["window_status"] == "INSUFFICIENT_TRADES").sum())

        quality_score = (
            compound_return * 100
            + avg_pf * 10
            + passed * 6
            + weak_pass * 3
            + near_breakeven * 1
            - failed * 8
            - insufficient * 1
            + worst_drawdown * 100
        )

        if total_trades < 30:
            research_decision = "TOO_FEW_TRADES"
        elif compound_return > 0.10 and avg_pf >= 1.20 and failed <= 2:
            research_decision = "ROBUST_CANDIDATE"
        elif compound_return > 0 and avg_pf >= 1.05 and failed <= 3:
            research_decision = "WEAK_CANDIDATE"
        elif compound_return > -0.05 and avg_pf >= 0.95:
            research_decision = "NEAR_BREAKEVEN"
        else:
            research_decision = "NOT_ROBUST"

        rows.append(
            {
                "strategy_name": strategy_name,
                "research_decision": research_decision,
                "windows": int(group["window_name"].nunique()),
                "total_trades": total_trades,
                "avg_trades_per_window": avg_trades,
                "compound_return": compound_return,
                "avg_return": avg_return,
                "avg_profit_factor": avg_pf,
                "worst_drawdown": worst_drawdown,
                "passed": passed,
                "weak_pass": weak_pass,
                "near_breakeven": near_breakeven,
                "failed": failed,
                "insufficient": insufficient,
                "quality_score": quality_score,
            }
        )

    aggregate_df = pd.DataFrame(rows)
    aggregate_df = aggregate_df.sort_values(by="quality_score", ascending=False)

    return aggregate_df


def print_directional_context_distribution(trades_df: pd.DataFrame):
    print()
    print("DIRECTIONAL CONTEXT TRADE DISTRIBUTION")
    print("=" * 100)

    if trades_df.empty:
        print("Sin trades.")
        return

    context_df = (
        trades_df.groupby(
            [
                "strategy_name",
                "directional_context_v3",
                "bias_1h_v3",
                "bias_4h_v3",
            ]
        )
        .agg(
            trades=("entry_index", "count"),
            total_net_pnl=("net_pnl", "sum"),
            avg_net_pnl=("net_pnl", "mean"),
        )
        .reset_index()
        .sort_values(by=["strategy_name", "total_net_pnl"], ascending=[True, False])
    )

    print(context_df.to_string(index=False))


def print_base_vs_filtered(results_df: pd.DataFrame):
    print()
    print("BASE VS DIRECTIONAL V3 COMPARISON")
    print("=" * 100)

    pairs = [
        ("LONG_V2_BASE", "LONG_V2_DIRECTIONAL_V3"),
        ("SHORT_FIB_V5_MTF_BASE", "SHORT_FIB_V5_MTF_DIRECTIONAL_V3"),
        (
            "SHORT_FIB_V5_MTF_LIQUIDITY_V2_BASE",
            "SHORT_FIB_V5_MTF_LIQUIDITY_V2_DIRECTIONAL_V3",
        ),
    ]

    rows = []

    for base_name, filtered_name in pairs:
        base = results_df[results_df["strategy_name"] == base_name]
        filtered = results_df[results_df["strategy_name"] == filtered_name]

        if base.empty or filtered.empty:
            continue

        base_compound = float((1 + base["total_return_pct"]).prod() - 1)
        filtered_compound = float((1 + filtered["total_return_pct"]).prod() - 1)

        rows.append(
            {
                "base_strategy": base_name,
                "filtered_strategy": filtered_name,
                "base_trades": int(base["total_trades"].sum()),
                "filtered_trades": int(filtered["total_trades"].sum()),
                "trades_removed": int(base["total_trades"].sum() - filtered["total_trades"].sum()),
                "base_compound_return": base_compound,
                "filtered_compound_return": filtered_compound,
                "return_delta": filtered_compound - base_compound,
                "base_avg_pf": pd.to_numeric(base["profit_factor"], errors="coerce").mean(),
                "filtered_avg_pf": pd.to_numeric(filtered["profit_factor"], errors="coerce").mean(),
                "base_worst_dd": float(base["max_drawdown_pct"].min()),
                "filtered_worst_dd": float(filtered["max_drawdown_pct"].min()),
            }
        )

    comparison_df = pd.DataFrame(rows)

    if comparison_df.empty:
        print("Sin comparacion.")
    else:
        print(comparison_df.to_string(index=False))


def print_final_decision(aggregate_df: pd.DataFrame):
    print()
    print("FINAL DIRECTIONAL CONTEXT V3 DECISION")
    print("=" * 100)

    if aggregate_df.empty:
        print("NO_DATA")
        return

    print(
        aggregate_df[
            [
                "strategy_name",
                "research_decision",
                "total_trades",
                "compound_return",
                "avg_profit_factor",
                "worst_drawdown",
                "failed",
                "insufficient",
            ]
        ].to_string(index=False)
    )

    print()
    print("Interpretacion:")
    print("- Si Directional V3 mejora retorno, PF y drawdown, el filtro aporta valor.")
    print("- Si elimina demasiados trades, hay que suavizar condiciones.")
    print("- Si sigue negativo, entonces el problema dominante no es solo direccion.")
    print("- No pasar a paper trading aunque mejore; esta fase solo valida filtro contextual.")


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

    print("VALIDATE DIRECTIONAL CONTEXT FILTER V3")
    print("=" * 100)
    print("Purpose: reduce LONG_AGAINST_BEARISH_MARKET and SHORT_AGAINST_BULLISH_MARKET")
    print()

    all_results = []
    all_trades = []

    for window_name, start_date, end_date in windows:
        window_results, trades_df = validate_window(
            symbol=symbol,
            window_name=window_name,
            start_date=start_date,
            end_date=end_date,
        )

        all_results.extend(window_results)

        if not trades_df.empty:
            all_trades.append(trades_df)

    results_df = pd.DataFrame(all_results)

    if all_trades:
        trades_all_df = pd.concat(all_trades, ignore_index=True)
    else:
        trades_all_df = pd.DataFrame()

    aggregate_df = build_aggregate(results_df)

    reports_dir = Path("reports") / "directional_context_v3"
    reports_dir.mkdir(parents=True, exist_ok=True)

    results_output = reports_dir / "directional_context_v3_window_results.csv"
    aggregate_output = reports_dir / "directional_context_v3_aggregate.csv"
    trades_output = reports_dir / "directional_context_v3_trade_diagnostics.csv"

    results_df.to_csv(results_output, index=False)
    aggregate_df.to_csv(aggregate_output, index=False)
    trades_all_df.to_csv(trades_output, index=False)

    print()
    print("DIRECTIONAL CONTEXT V3 AGGREGATE RESULTS")
    print("=" * 100)
    print(
        aggregate_df[
            [
                "strategy_name",
                "research_decision",
                "quality_score",
                "windows",
                "total_trades",
                "compound_return",
                "avg_return",
                "avg_profit_factor",
                "worst_drawdown",
                "passed",
                "weak_pass",
                "near_breakeven",
                "failed",
                "insufficient",
            ]
        ].to_string(index=False)
    )

    print()
    print("DIRECTIONAL CONTEXT V3 DETAIL BY WINDOW")
    print("=" * 100)
    print(
        results_df[
            [
                "window_name",
                "strategy_name",
                "direction",
                "market_window_type",
                "window_status",
                "market_return_pct",
                "total_trades",
                "total_return_pct",
                "win_rate",
                "profit_factor",
                "expectancy",
                "max_drawdown_pct",
            ]
        ]
        .sort_values(by=["strategy_name", "window_name"])
        .to_string(index=False)
    )

    print_base_vs_filtered(results_df)
    print_directional_context_distribution(trades_all_df)
    print_final_decision(aggregate_df)

    print()
    print("ARCHIVOS GENERADOS")
    print("=" * 100)
    print(f"- {results_output}")
    print(f"- {aggregate_output}")
    print(f"- {trades_output}")


if __name__ == "__main__":
    main()