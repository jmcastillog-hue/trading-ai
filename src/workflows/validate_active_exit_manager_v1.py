from pathlib import Path
import pandas as pd

from src.exits.active_exit_manager_v1 import (
    build_exit_profile,
    run_active_exit_backtest,
)
from src.workflows.validate_directional_context_filter_v3_1 import (
    build_combined_context_dataset_v3_1,
    short_mtf_with_directional_context_v3_1,
    short_mtf_liquidity_v2_with_directional_context_v3_1,
)
from src.workflows.robust_validate_short_candidates import (
    build_short_config,
    classify_market_window,
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


def classify_exit_result(row: pd.Series) -> str:
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
        return "EXIT_PROMISING"

    if (
        compound_return > 0.00
        and avg_profit_factor >= 1.05
        and worst_drawdown > -0.12
        and positive_window_rate >= 0.45
    ):
        return "EXIT_WEAK_PASS"

    if (
        compound_return > -0.05
        and avg_profit_factor >= 0.95
        and worst_drawdown > -0.10
    ):
        return "EXIT_NEAR_BREAKEVEN"

    return "EXIT_FAILED"


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
    exit_profile: str,
    market_return_pct: float,
    summary: dict,
) -> dict:
    row = {
        "symbol": symbol,
        "base_window": base_window,
        "year": base_window[:4],
        "window_name": f"{symbol}_{base_window}",
        "strategy_name": strategy_name,
        "exit_profile": exit_profile,
        "strategy_profile": f"{strategy_name}__{exit_profile}",
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
    exit_profile: str,
) -> pd.DataFrame:
    if trades_df.empty:
        return pd.DataFrame()

    result = trades_df.copy()

    result["symbol"] = symbol
    result["base_window"] = base_window
    result["year"] = base_window[:4]
    result["window_name"] = f"{symbol}_{base_window}"
    result["strategy_name"] = strategy_name
    result["exit_profile"] = exit_profile
    result["strategy_profile"] = f"{strategy_name}__{exit_profile}"

    return result


def summarize_group(results_df: pd.DataFrame, group_cols: list[str]) -> pd.DataFrame:
    if results_df.empty:
        return pd.DataFrame()

    rows = []

    for keys, group in results_df.groupby(group_cols):
        if not isinstance(keys, tuple):
            keys = (keys,)

        group = group.copy()

        pf_series = pd.to_numeric(group["profit_factor"], errors="coerce")
        return_series = pd.to_numeric(group["total_return_pct"], errors="coerce")
        trade_series = pd.to_numeric(group["total_trades"], errors="coerce")

        total_trades = int(trade_series.sum())
        compound_return = float((1 + return_series).prod() - 1)
        avg_return = float(return_series.mean())
        median_return = float(return_series.median())
        avg_profit_factor = (
            float(pf_series.dropna().mean()) if len(pf_series.dropna()) else 0.0
        )
        worst_drawdown = float(
            pd.to_numeric(group["max_drawdown_pct"], errors="coerce").min()
        )
        avg_expectancy_r = float(
            pd.to_numeric(group["expectancy_r"], errors="coerce").mean()
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
                "worst_drawdown": worst_drawdown,
                "avg_expectancy_r": avg_expectancy_r,
                "positive_windows": positive_windows,
                "negative_windows": negative_windows,
                "positive_window_rate": positive_window_rate,
                "failed_windows": failed_windows,
                "insufficient_windows": insufficient_windows,
            }
        )

        row["exit_decision"] = classify_exit_result(pd.Series(row))

        rows.append(row)

    summary_df = pd.DataFrame(rows)

    if summary_df.empty:
        return summary_df

    sort_cols = [
        col
        for col in ["strategy_name", "exit_profile", "symbol", "year"]
        if col in summary_df.columns
    ]

    summary_df = summary_df.sort_values(
        by=sort_cols + ["compound_return"],
        ascending=[True] * len(sort_cols) + [False],
    )

    return summary_df


def summarize_exit_reasons(trades_df: pd.DataFrame) -> pd.DataFrame:
    if trades_df.empty:
        return pd.DataFrame()

    df = trades_df.copy()

    df["net_pnl"] = pd.to_numeric(df["net_pnl"], errors="coerce").fillna(0.0)
    df["result_r"] = pd.to_numeric(df["result_r"], errors="coerce").fillna(0.0)

    rows = []

    for keys, group in df.groupby(["strategy_profile", "exit_reason"]):
        strategy_profile, exit_reason = keys

        gross_profit = float(group.loc[group["net_pnl"] > 0, "net_pnl"].sum())
        gross_loss = float(group.loc[group["net_pnl"] < 0, "net_pnl"].sum())

        if gross_loss == 0:
            profit_factor = None if gross_profit > 0 else 0.0
        else:
            profit_factor = gross_profit / abs(gross_loss)

        rows.append(
            {
                "strategy_profile": strategy_profile,
                "exit_reason": exit_reason,
                "trades": int(len(group)),
                "wins": int((group["net_pnl"] > 0).sum()),
                "losses": int((group["net_pnl"] <= 0).sum()),
                "win_rate": float((group["net_pnl"] > 0).mean()),
                "total_net_pnl": float(group["net_pnl"].sum()),
                "avg_net_pnl": float(group["net_pnl"].mean()),
                "avg_result_r": float(group["result_r"].mean()),
                "profit_factor": profit_factor,
                "avg_bars_held": float(group["bars_held"].mean()),
                "avg_mfe_r": float(group["max_favorable_r"].mean()),
                "avg_mae_r": float(group["max_adverse_r"].mean()),
            }
        )

    result = pd.DataFrame(rows)
    result = result.sort_values(by=["strategy_profile", "total_net_pnl"], ascending=[True, False])

    return result


def validate_window_active_exit(
    symbol: str,
    base_window: str,
    start_date: str,
    end_date: str,
) -> tuple[list[dict], pd.DataFrame]:
    data_dir = Path("data") / "active_exit_manager_v1"
    reports_dir = Path("reports") / "active_exit_manager_v1"

    data_dir.mkdir(parents=True, exist_ok=True)
    reports_dir.mkdir(parents=True, exist_ok=True)

    base_name = f"{symbol.lower()}_{base_window}"

    csv_15m = data_dir / f"{base_name}_15m.csv"
    csv_1h = data_dir / f"{base_name}_1h.csv"
    csv_4h = data_dir / f"{base_name}_4h.csv"

    enriched_csv = reports_dir / f"{base_name}_v3_1_context.csv"

    print()
    print(f"ACTIVE EXIT MANAGER V1 WINDOW: {symbol}_{base_window}")
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

    strategies = [
        {
            "strategy_name": "SHORT_FIB_V5_MTF_V3_1",
            "strategy_func": short_mtf_with_directional_context_v3_1,
        },
    ]

    exit_profiles = [
        "FIXED_RR_2_5",
        "BREAKEVEN_AFTER_1R",
        "TRAIL_ATR_AFTER_1R",
        "PARTIAL_1R_THEN_2_5R",
        "MOMENTUM_EXIT_AFTER_1R",
    ]

    window_results = []
    window_trades = []

    for strategy_item in strategies:
        strategy_name = strategy_item["strategy_name"]
        strategy_func = strategy_item["strategy_func"]

        for exit_profile_name in exit_profiles:
            exit_profile = build_exit_profile(exit_profile_name)

            trades_df, summary = run_active_exit_backtest(
                df=market_df,
                strategy_func=strategy_func,
                config=build_short_config(),
                exit_profile=exit_profile,
            )

            result = summarize_strategy(
                symbol=symbol,
                base_window=base_window,
                strategy_name=strategy_name,
                exit_profile=exit_profile_name,
                market_return_pct=market_return_pct,
                summary=summary,
            )

            window_results.append(result)

            trades_with_context = add_trade_context(
                trades_df=trades_df,
                symbol=symbol,
                base_window=base_window,
                strategy_name=strategy_name,
                exit_profile=exit_profile_name,
            )

            if not trades_with_context.empty:
                window_trades.append(trades_with_context)

            print(
                f"{strategy_name} | "
                f"exit={exit_profile_name} | "
                f"symbol={symbol} | "
                f"window={base_window} | "
                f"market={market_return_pct:.2%} | "
                f"trades={result['total_trades']} | "
                f"return={result['total_return_pct']:.2%} | "
                f"wr={result['win_rate']:.2%} | "
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


def print_exit_profile_comparison(profile_summary_df: pd.DataFrame):
    print_section("ACTIVE EXIT MANAGER V1 PROFILE COMPARISON")

    if profile_summary_df.empty:
        print("Sin resultados.")
        return

    display_cols = [
        "strategy_name",
        "exit_profile",
        "exit_decision",
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

    print(profile_summary_df[display_cols].to_string(index=False))


def print_final_decision(profile_summary_df: pd.DataFrame):
    print_section("FINAL ACTIVE EXIT MANAGER V1 DECISION")

    if profile_summary_df.empty:
        print("NO_DATA")
        return

    display_cols = [
        "strategy_name",
        "exit_profile",
        "exit_decision",
        "total_trades",
        "compound_return",
        "avg_profit_factor",
        "avg_expectancy_r",
        "worst_drawdown",
        "positive_window_rate",
        "failed_windows",
        "insufficient_windows",
    ]

    print(profile_summary_df[display_cols].to_string(index=False))

    print()
    print("Interpretacion:")
    print("- Si una salida mejora retorno y drawdown contra FIXED_RR_2_5, puede pasar a V2.")
    print("- Si reduce muestra o expectativa, se descarta como salida principal.")
    print("- Esta fase no habilita paper trading; solo valida políticas de salida.")


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

    print("ACTIVE EXIT MANAGER V1 VALIDATION")
    print("=" * 100)
    print("Symbols: BTCUSDT, ETHUSDT, SOLUSDT")
    print("Windows: quarterly, 2022-01-01 to 2026-01-01")
    print("Purpose: test active exits over V3.1 short context")
    print()

    all_results = []
    all_trades = []
    errors = []

    for symbol in symbols:
        for base_window, start_date, end_date in windows:
            try:
                window_results, trades_df = validate_window_active_exit(
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

    profile_summary_df = summarize_group(
        results_df,
        ["strategy_name", "exit_profile"],
    )

    symbol_summary_df = summarize_group(
        results_df,
        ["strategy_name", "exit_profile", "symbol"],
    )

    year_summary_df = summarize_group(
        results_df,
        ["strategy_name", "exit_profile", "year"],
    )

    exit_reason_summary_df = summarize_exit_reasons(trades_all_df)

    reports_dir = Path("reports") / "active_exit_manager_v1"
    reports_dir.mkdir(parents=True, exist_ok=True)

    results_output = reports_dir / "active_exit_v1_window_results.csv"
    trades_output = reports_dir / "active_exit_v1_trade_diagnostics.csv"
    errors_output = reports_dir / "active_exit_v1_errors.csv"
    profile_summary_output = reports_dir / "active_exit_v1_profile_summary.csv"
    symbol_summary_output = reports_dir / "active_exit_v1_symbol_summary.csv"
    year_summary_output = reports_dir / "active_exit_v1_year_summary.csv"
    exit_reason_output = reports_dir / "active_exit_v1_exit_reason_summary.csv"

    results_df.to_csv(results_output, index=False)
    trades_all_df.to_csv(trades_output, index=False)
    errors_df.to_csv(errors_output, index=False)
    profile_summary_df.to_csv(profile_summary_output, index=False)
    symbol_summary_df.to_csv(symbol_summary_output, index=False)
    year_summary_df.to_csv(year_summary_output, index=False)
    exit_reason_summary_df.to_csv(exit_reason_output, index=False)

    print_section("ACTIVE EXIT MANAGER V1 AGGREGATE BY PROFILE")
    if profile_summary_df.empty:
        print("Sin resultados.")
    else:
        print(
            profile_summary_df[
                [
                    "strategy_name",
                    "exit_profile",
                    "exit_decision",
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

    print_section("ACTIVE EXIT MANAGER V1 BY SYMBOL")
    if symbol_summary_df.empty:
        print("Sin resultados.")
    else:
        print(
            symbol_summary_df[
                [
                    "strategy_name",
                    "exit_profile",
                    "symbol",
                    "exit_decision",
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

    print_section("ACTIVE EXIT MANAGER V1 BY YEAR")
    if year_summary_df.empty:
        print("Sin resultados.")
    else:
        print(
            year_summary_df[
                [
                    "strategy_name",
                    "exit_profile",
                    "year",
                    "exit_decision",
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

    print_exit_profile_comparison(profile_summary_df)

    print_section("ACTIVE EXIT MANAGER V1 EXIT REASON SUMMARY")
    if exit_reason_summary_df.empty:
        print("Sin trades.")
    else:
        print(
            exit_reason_summary_df[
                [
                    "strategy_profile",
                    "exit_reason",
                    "trades",
                    "win_rate",
                    "total_net_pnl",
                    "avg_result_r",
                    "profit_factor",
                    "avg_bars_held",
                    "avg_mfe_r",
                    "avg_mae_r",
                ]
            ].head(80).to_string(index=False)
        )

    print_section("ACTIVE EXIT MANAGER V1 ERRORS")
    if errors_df.empty:
        print("Sin errores.")
    else:
        print(errors_df.to_string(index=False))

    print_final_decision(profile_summary_df)

    print()
    print("ARCHIVOS GENERADOS")
    print("=" * 100)
    print(f"- {results_output}")
    print(f"- {trades_output}")
    print(f"- {errors_output}")
    print(f"- {profile_summary_output}")
    print(f"- {symbol_summary_output}")
    print(f"- {year_summary_output}")
    print(f"- {exit_reason_output}")


if __name__ == "__main__":
    main()