from pathlib import Path

import pandas as pd

from src.benchmarks.benchmark_engine_v1 import (
    build_random_baseline_strategies,
    context_only_v3_1_short_strategy,
    ema_trend_short_strategy,
)
from src.exits.active_exit_manager_v1 import (
    add_active_exit_features,
    build_exit_profile,
    run_active_exit_backtest,
)
from src.strategies.fib_v5_mtf_strategy import fib_v5_short_with_mtf_filter
from src.workflows.robust_validate_short_candidates import (
    build_short_config,
    classify_market_window,
)
from src.workflows.validate_directional_context_filter_v3_1 import (
    build_combined_context_dataset_v3_1,
    short_mtf_with_directional_context_v3_1,
)
from src.workflows.validate_long_v2_candidate_robust import (
    calculate_market_return,
    download_binance_klines_range,
)


def safe_float(value, default=0.0):
    try:
        if value is None or pd.isna(value):
            return default

        return float(value)
    except Exception:
        return default


def classify_benchmark_result(row: pd.Series) -> str:
    trades = int(row.get("total_trades", 0))
    compound_return = safe_float(row.get("compound_return"), 0.0)
    avg_profit_factor = safe_float(row.get("avg_profit_factor"), 0.0)
    worst_drawdown = safe_float(row.get("worst_drawdown"), 0.0)
    positive_window_rate = safe_float(row.get("positive_window_rate"), 0.0)

    if trades < 30:
        return "TOO_FEW_TRADES"

    if (
        compound_return > 0.15
        and avg_profit_factor >= 1.20
        and worst_drawdown > -0.15
        and positive_window_rate >= 0.55
    ):
        return "BENCHMARK_PROMISING"

    if (
        compound_return > 0
        and avg_profit_factor >= 1.05
        and worst_drawdown > -0.12
        and positive_window_rate >= 0.45
    ):
        return "BENCHMARK_WEAK_PASS"

    if (
        compound_return > -0.05
        and avg_profit_factor >= 0.95
        and worst_drawdown > -0.10
    ):
        return "BENCHMARK_NEAR_BREAKEVEN"

    return "BENCHMARK_FAILED"


def classify_window_status(summary: dict) -> str:
    trades = int(summary.get("total_trades", 0))
    total_return_pct = safe_float(summary.get("total_return_pct"), 0.0)
    profit_factor = summary.get("profit_factor", None)
    max_drawdown_pct = safe_float(summary.get("max_drawdown_pct"), 0.0)

    if trades < 5:
        return "INSUFFICIENT_TRADES"

    if profit_factor is None or pd.isna(profit_factor):
        if total_return_pct > 0:
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
    symbol: str,
    base_window: str,
    strategy_name: str,
    benchmark_group: str,
    market_return_pct: float,
    summary: dict,
) -> dict:
    row = {
        "symbol": symbol,
        "base_window": base_window,
        "year": base_window[:4],
        "window_name": f"{symbol}_{base_window}",
        "strategy_name": strategy_name,
        "benchmark_group": benchmark_group,
        "market_return_pct": market_return_pct,
        "market_window_type": classify_market_window(market_return_pct),
        "total_trades": int(summary.get("total_trades", 0)),
        "wins": int(summary.get("wins", 0)),
        "losses": int(summary.get("losses", 0)),
        "ending_capital": summary.get("ending_capital", 1000.0),
        "total_return_pct": safe_float(summary.get("total_return_pct"), 0.0),
        "win_rate": safe_float(summary.get("win_rate"), 0.0),
        "profit_factor": summary.get("profit_factor", None),
        "expectancy": safe_float(summary.get("expectancy"), 0.0),
        "expectancy_r": safe_float(summary.get("expectancy_r"), 0.0),
        "max_drawdown_pct": safe_float(summary.get("max_drawdown_pct"), 0.0),
        "avg_bars_held": safe_float(summary.get("avg_bars_held"), 0.0),
    }

    row["window_status"] = classify_window_status(summary)

    return row


def add_trade_context(
    trades_df: pd.DataFrame,
    symbol: str,
    base_window: str,
    strategy_name: str,
    benchmark_group: str,
) -> pd.DataFrame:
    if trades_df.empty:
        return pd.DataFrame()

    result = trades_df.copy()

    result["symbol"] = symbol
    result["base_window"] = base_window
    result["year"] = base_window[:4]
    result["window_name"] = f"{symbol}_{base_window}"
    result["strategy_name"] = strategy_name
    result["benchmark_group"] = benchmark_group

    return result


def summarize_group(results_df: pd.DataFrame, group_cols: list[str]) -> pd.DataFrame:
    if results_df.empty:
        return pd.DataFrame()

    rows = []

    for keys, group in results_df.groupby(group_cols):
        if not isinstance(keys, tuple):
            keys = (keys,)

        group = group.copy()

        return_series = pd.to_numeric(group["total_return_pct"], errors="coerce")
        pf_series = pd.to_numeric(group["profit_factor"], errors="coerce")
        trade_series = pd.to_numeric(group["total_trades"], errors="coerce")
        expectancy_r_series = pd.to_numeric(group["expectancy_r"], errors="coerce")

        total_trades = int(trade_series.sum())
        compound_return = float((1 + return_series).prod() - 1)
        avg_return = float(return_series.mean())
        median_return = float(return_series.median())
        avg_profit_factor = (
            float(pf_series.dropna().mean()) if len(pf_series.dropna()) else 0.0
        )
        avg_expectancy_r = float(expectancy_r_series.mean())
        worst_drawdown = float(
            pd.to_numeric(group["max_drawdown_pct"], errors="coerce").min()
        )

        windows = int(group["window_name"].nunique())
        positive_windows = int((return_series > 0).sum())
        negative_windows = int((return_series <= 0).sum())
        positive_window_rate = positive_windows / windows if windows else 0.0

        failed_windows = int((group["window_status"] == "FAILED").sum())
        insufficient_windows = int(
            (group["window_status"] == "INSUFFICIENT_TRADES").sum()
        )

        row = {}

        for col, value in zip(group_cols, keys):
            row[col] = value

        row.update(
            {
                "windows": windows,
                "total_trades": total_trades,
                "compound_return": compound_return,
                "avg_return": avg_return,
                "median_return": median_return,
                "avg_profit_factor": avg_profit_factor,
                "avg_expectancy_r": avg_expectancy_r,
                "worst_drawdown": worst_drawdown,
                "positive_windows": positive_windows,
                "negative_windows": negative_windows,
                "positive_window_rate": positive_window_rate,
                "failed_windows": failed_windows,
                "insufficient_windows": insufficient_windows,
            }
        )

        row["benchmark_decision"] = classify_benchmark_result(pd.Series(row))

        rows.append(row)

    summary_df = pd.DataFrame(rows)

    if summary_df.empty:
        return summary_df

    sort_cols = [
        col
        for col in ["benchmark_group", "strategy_name", "symbol", "year"]
        if col in summary_df.columns
    ]

    summary_df = summary_df.sort_values(
        by=sort_cols + ["compound_return"],
        ascending=[True] * len(sort_cols) + [False],
    )

    return summary_df


def summarize_target_vs_benchmarks(strategy_summary_df: pd.DataFrame) -> pd.DataFrame:
    if strategy_summary_df.empty:
        return pd.DataFrame()

    target = strategy_summary_df[
        strategy_summary_df["strategy_name"] == "TARGET_SHORT_FIB_V5_MTF_V3_1"
    ]

    if target.empty:
        return pd.DataFrame()

    target_row = target.iloc[0]

    rows = []

    for _, benchmark_row in strategy_summary_df.iterrows():
        if benchmark_row["strategy_name"] == "TARGET_SHORT_FIB_V5_MTF_V3_1":
            continue

        rows.append(
            {
                "target_strategy": target_row["strategy_name"],
                "benchmark_strategy": benchmark_row["strategy_name"],
                "benchmark_group": benchmark_row["benchmark_group"],
                "target_total_trades": int(target_row["total_trades"]),
                "benchmark_total_trades": int(benchmark_row["total_trades"]),
                "target_compound_return": float(target_row["compound_return"]),
                "benchmark_compound_return": float(benchmark_row["compound_return"]),
                "return_delta": float(
                    target_row["compound_return"] - benchmark_row["compound_return"]
                ),
                "target_avg_pf": float(target_row["avg_profit_factor"]),
                "benchmark_avg_pf": float(benchmark_row["avg_profit_factor"]),
                "pf_delta": float(
                    target_row["avg_profit_factor"] - benchmark_row["avg_profit_factor"]
                ),
                "target_worst_dd": float(target_row["worst_drawdown"]),
                "benchmark_worst_dd": float(benchmark_row["worst_drawdown"]),
                "target_positive_window_rate": float(target_row["positive_window_rate"]),
                "benchmark_positive_window_rate": float(
                    benchmark_row["positive_window_rate"]
                ),
            }
        )

    result = pd.DataFrame(rows)

    if result.empty:
        return result

    result = result.sort_values(by="return_delta", ascending=False)

    return result


def summarize_random_baseline(strategy_summary_df: pd.DataFrame) -> pd.DataFrame:
    random_df = strategy_summary_df[
        strategy_summary_df["benchmark_group"] == "RANDOM_BASELINE"
    ].copy()

    if random_df.empty:
        return pd.DataFrame()

    row = {
        "random_variants": int(random_df["strategy_name"].nunique()),
        "avg_total_trades": float(random_df["total_trades"].mean()),
        "avg_compound_return": float(random_df["compound_return"].mean()),
        "max_compound_return": float(random_df["compound_return"].max()),
        "min_compound_return": float(random_df["compound_return"].min()),
        "avg_profit_factor": float(random_df["avg_profit_factor"].mean()),
        "best_profit_factor": float(random_df["avg_profit_factor"].max()),
        "avg_worst_drawdown": float(random_df["worst_drawdown"].mean()),
        "avg_positive_window_rate": float(random_df["positive_window_rate"].mean()),
    }

    return pd.DataFrame([row])


def validate_window_benchmark(
    symbol: str,
    base_window: str,
    start_date: str,
    end_date: str,
) -> tuple[list[dict], pd.DataFrame]:
    data_dir = Path("data") / "benchmark_engine_v1"
    reports_dir = Path("reports") / "benchmark_engine_v1"

    data_dir.mkdir(parents=True, exist_ok=True)
    reports_dir.mkdir(parents=True, exist_ok=True)

    base_name = f"{symbol.lower()}_{base_window}"

    csv_15m = data_dir / f"{base_name}_15m.csv"
    csv_1h = data_dir / f"{base_name}_1h.csv"
    csv_4h = data_dir / f"{base_name}_4h.csv"

    enriched_csv = reports_dir / f"{base_name}_benchmark_context.csv"

    print()
    print(f"BENCHMARK ENGINE V1 WINDOW: {symbol}_{base_window}")
    print("=" * 100)

    if not csv_15m.exists():
        download_binance_klines_range(symbol, "15m", start_date, end_date, csv_15m)

    if not csv_1h.exists():
        download_binance_klines_range(symbol, "1h", start_date, end_date, csv_1h)

    if not csv_4h.exists():
        download_binance_klines_range(symbol, "4h", start_date, end_date, csv_4h)

    market_return_pct = calculate_market_return(csv_15m)

    market_df = build_combined_context_dataset_v3_1(
        csv_15m=csv_15m,
        csv_1h=csv_1h,
        csv_4h=csv_4h,
        enriched_csv=enriched_csv,
        reports_dir=reports_dir,
        base_name=base_name,
    )

    market_df = add_active_exit_features(market_df)

    config = build_short_config()
    exit_profile = build_exit_profile("FIXED_RR_2_5")

    benchmark_strategies = [
        {
            "strategy_name": "TARGET_SHORT_FIB_V5_MTF_V3_1",
            "benchmark_group": "TARGET",
            "strategy_func": short_mtf_with_directional_context_v3_1,
        },
        {
            "strategy_name": "BASE_SHORT_FIB_V5_MTF",
            "benchmark_group": "BASE_STRATEGY",
            "strategy_func": fib_v5_short_with_mtf_filter,
        },
        {
            "strategy_name": "CONTEXT_ONLY_V3_1_SHORT",
            "benchmark_group": "CONTEXT_ONLY",
            "strategy_func": context_only_v3_1_short_strategy,
        },
        {
            "strategy_name": "EMA_TREND_SHORT",
            "benchmark_group": "EMA_BASELINE",
            "strategy_func": ema_trend_short_strategy,
        },
    ]

    random_strategies = build_random_baseline_strategies(
        df=market_df,
        reference_strategy_func=short_mtf_with_directional_context_v3_1,
        config=config,
        seeds=[11, 22, 33],
    )

    for item in random_strategies:
        item["benchmark_group"] = "RANDOM_BASELINE"

    benchmark_strategies.extend(random_strategies)

    window_results = []
    window_trades = []

    for item in benchmark_strategies:
        strategy_name = item["strategy_name"]
        benchmark_group = item["benchmark_group"]
        strategy_func = item["strategy_func"]

        trades_df, summary = run_active_exit_backtest(
            df=market_df,
            strategy_func=strategy_func,
            config=config,
            exit_profile=exit_profile,
        )

        result = summarize_strategy(
            symbol=symbol,
            base_window=base_window,
            strategy_name=strategy_name,
            benchmark_group=benchmark_group,
            market_return_pct=market_return_pct,
            summary=summary,
        )

        window_results.append(result)

        trades_with_context = add_trade_context(
            trades_df=trades_df,
            symbol=symbol,
            base_window=base_window,
            strategy_name=strategy_name,
            benchmark_group=benchmark_group,
        )

        if not trades_with_context.empty:
            window_trades.append(trades_with_context)

        print(
            f"{strategy_name} | "
            f"group={benchmark_group} | "
            f"symbol={symbol} | "
            f"window={base_window} | "
            f"market={market_return_pct:.2%} | "
            f"trades={result['total_trades']} | "
            f"return={result['total_return_pct']:.2%} | "
            f"pf={result['profit_factor']} | "
            f"expR={result['expectancy_r']:.4f} | "
            f"mdd={result['max_drawdown_pct']:.2%} | "
            f"status={result['window_status']}"
        )

    if window_trades:
        trades_window_df = pd.concat(window_trades, ignore_index=True)
    else:
        trades_window_df = pd.DataFrame()

    return window_results, trades_window_df


def print_section(title: str):
    print()
    print(title)
    print("=" * 100)


def print_final_decision(
    strategy_summary_df: pd.DataFrame,
    target_vs_benchmark_df: pd.DataFrame,
    random_summary_df: pd.DataFrame,
):
    print_section("FINAL BENCHMARK ENGINE V1 DECISION")

    if strategy_summary_df.empty:
        print("NO_DATA")
        return

    display_cols = [
        "strategy_name",
        "benchmark_group",
        "benchmark_decision",
        "total_trades",
        "compound_return",
        "avg_profit_factor",
        "avg_expectancy_r",
        "worst_drawdown",
        "positive_window_rate",
        "failed_windows",
        "insufficient_windows",
    ]

    print(strategy_summary_df[display_cols].to_string(index=False))

    print()
    print("Interpretacion:")
    print("- Si TARGET supera a base, contexto-only, EMA y random, V3.1 tiene edge relevante.")
    print("- Si random o EMA igualan/superan al TARGET, hay riesgo de edge trivial o sobreajuste.")
    print("- Esta fase no habilita paper trading; solo valida si la estrategia supera benchmarks.")


def main():
    symbols = [
        "BTCUSDT",
        "ETHUSDT",
        "SOLUSDT",
    ]

    windows = [
        ("2022_Q1", "2022-01-01", "2022-04-01"),
        ("2022_Q2", "2022-04-01", "2022-07-01"),
        ("2022_Q3", "2022-07-01", "2022-10-01"),
        ("2022_Q4", "2022-10-01", "2023-01-01"),
        ("2023_Q1", "2023-01-01", "2023-04-01"),
        ("2023_Q2", "2023-04-01", "2023-07-01"),
        ("2023_Q3", "2023-07-01", "2023-10-01"),
        ("2023_Q4", "2023-10-01", "2024-01-01"),
        ("2024_Q1", "2024-01-01", "2024-04-01"),
        ("2024_Q2", "2024-04-01", "2024-07-01"),
        ("2024_Q3", "2024-07-01", "2024-10-01"),
        ("2024_Q4", "2024-10-01", "2025-01-01"),
        ("2025_Q1", "2025-01-01", "2025-04-01"),
        ("2025_Q2", "2025-04-01", "2025-07-01"),
        ("2025_Q3", "2025-07-01", "2025-10-01"),
        ("2025_Q4", "2025-10-01", "2026-01-01"),
    ]

    print("BENCHMARK ENGINE V1 VALIDATION")
    print("=" * 100)
    print("Target: SHORT_FIB_V5_MTF_V3_1 + FIXED_RR_2_5")
    print("Benchmarks: base MTF, context-only, EMA trend, random short")
    print()

    all_results = []
    all_trades = []
    errors = []

    for symbol in symbols:
        for base_window, start_date, end_date in windows:
            try:
                window_results, trades_df = validate_window_benchmark(
                    symbol=symbol,
                    base_window=base_window,
                    start_date=start_date,
                    end_date=end_date,
                )

                all_results.extend(window_results)

                if not trades_df.empty:
                    all_trades.append(trades_df)

            except Exception as exc:
                error_row = {
                    "symbol": symbol,
                    "base_window": base_window,
                    "start_date": start_date,
                    "end_date": end_date,
                    "error": repr(exc),
                }

                errors.append(error_row)

                print()
                print("ERROR EN VENTANA")
                print("=" * 100)
                print(error_row)

    results_df = pd.DataFrame(all_results)

    if all_trades:
        trades_all_df = pd.concat(all_trades, ignore_index=True)
    else:
        trades_all_df = pd.DataFrame()

    errors_df = pd.DataFrame(errors)

    strategy_summary_df = summarize_group(results_df, ["strategy_name", "benchmark_group"])
    symbol_summary_df = summarize_group(
        results_df,
        ["strategy_name", "benchmark_group", "symbol"],
    )
    year_summary_df = summarize_group(
        results_df,
        ["strategy_name", "benchmark_group", "year"],
    )
    target_vs_benchmark_df = summarize_target_vs_benchmarks(strategy_summary_df)
    random_summary_df = summarize_random_baseline(strategy_summary_df)

    reports_dir = Path("reports") / "benchmark_engine_v1"
    reports_dir.mkdir(parents=True, exist_ok=True)

    results_output = reports_dir / "benchmark_v1_window_results.csv"
    trades_output = reports_dir / "benchmark_v1_trade_diagnostics.csv"
    errors_output = reports_dir / "benchmark_v1_errors.csv"
    strategy_summary_output = reports_dir / "benchmark_v1_strategy_summary.csv"
    symbol_summary_output = reports_dir / "benchmark_v1_symbol_summary.csv"
    year_summary_output = reports_dir / "benchmark_v1_year_summary.csv"
    target_vs_benchmark_output = reports_dir / "benchmark_v1_target_vs_benchmarks.csv"
    random_summary_output = reports_dir / "benchmark_v1_random_summary.csv"

    results_df.to_csv(results_output, index=False)
    trades_all_df.to_csv(trades_output, index=False)
    errors_df.to_csv(errors_output, index=False)
    strategy_summary_df.to_csv(strategy_summary_output, index=False)
    symbol_summary_df.to_csv(symbol_summary_output, index=False)
    year_summary_df.to_csv(year_summary_output, index=False)
    target_vs_benchmark_df.to_csv(target_vs_benchmark_output, index=False)
    random_summary_df.to_csv(random_summary_output, index=False)

    print_section("BENCHMARK ENGINE V1 AGGREGATE BY STRATEGY")
    if strategy_summary_df.empty:
        print("Sin resultados.")
    else:
        print(
            strategy_summary_df[
                [
                    "strategy_name",
                    "benchmark_group",
                    "benchmark_decision",
                    "windows",
                    "total_trades",
                    "compound_return",
                    "avg_return",
                    "avg_profit_factor",
                    "avg_expectancy_r",
                    "worst_drawdown",
                    "positive_windows",
                    "negative_windows",
                    "positive_window_rate",
                    "failed_windows",
                    "insufficient_windows",
                ]
            ].to_string(index=False)
        )

    print_section("BENCHMARK ENGINE V1 BY SYMBOL")
    if symbol_summary_df.empty:
        print("Sin resultados.")
    else:
        print(
            symbol_summary_df[
                [
                    "strategy_name",
                    "benchmark_group",
                    "symbol",
                    "benchmark_decision",
                    "windows",
                    "total_trades",
                    "compound_return",
                    "avg_profit_factor",
                    "avg_expectancy_r",
                    "worst_drawdown",
                    "positive_window_rate",
                    "failed_windows",
                    "insufficient_windows",
                ]
            ].to_string(index=False)
        )

    print_section("BENCHMARK ENGINE V1 BY YEAR")
    if year_summary_df.empty:
        print("Sin resultados.")
    else:
        print(
            year_summary_df[
                [
                    "strategy_name",
                    "benchmark_group",
                    "year",
                    "benchmark_decision",
                    "windows",
                    "total_trades",
                    "compound_return",
                    "avg_profit_factor",
                    "avg_expectancy_r",
                    "worst_drawdown",
                    "positive_window_rate",
                    "failed_windows",
                    "insufficient_windows",
                ]
            ].to_string(index=False)
        )

    print_section("TARGET VS BENCHMARKS")
    if target_vs_benchmark_df.empty:
        print("Sin comparacion.")
    else:
        print(target_vs_benchmark_df.to_string(index=False))

    print_section("RANDOM BASELINE SUMMARY")
    if random_summary_df.empty:
        print("Sin random baseline.")
    else:
        print(random_summary_df.to_string(index=False))

    print_section("BENCHMARK ENGINE V1 ERRORS")
    if errors_df.empty:
        print("Sin errores.")
    else:
        print(errors_df.to_string(index=False))

    print_final_decision(
        strategy_summary_df=strategy_summary_df,
        target_vs_benchmark_df=target_vs_benchmark_df,
        random_summary_df=random_summary_df,
    )

    print()
    print("ARCHIVOS GENERADOS")
    print("=" * 100)
    print(f"- {results_output}")
    print(f"- {trades_output}")
    print(f"- {errors_output}")
    print(f"- {strategy_summary_output}")
    print(f"- {symbol_summary_output}")
    print(f"- {year_summary_output}")
    print(f"- {target_vs_benchmark_output}")
    print(f"- {random_summary_output}")


if __name__ == "__main__":
    main()