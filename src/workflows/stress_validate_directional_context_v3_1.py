from pathlib import Path
import pandas as pd

from src.workflows.validate_directional_context_filter_v3_1 import validate_window


FOCUS_STRATEGIES = [
    "SHORT_FIB_V5_MTF_DIRECTIONAL_V3_1",
    "SHORT_FIB_V5_MTF_LIQUIDITY_V2_DIRECTIONAL_V3_1",
    "LONG_V2_DIRECTIONAL_V3_1",
]


BASE_STRATEGIES = [
    "SHORT_FIB_V5_MTF_BASE",
    "SHORT_FIB_V5_MTF_LIQUIDITY_V2_BASE",
    "LONG_V2_BASE",
]


def safe_float(value, default=0.0):
    try:
        if value is None or pd.isna(value):
            return default
        return float(value)
    except Exception:
        return default


def get_year_from_window(window_name: str) -> str:
    for year in ["2022", "2023", "2024", "2025", "2026"]:
        if year in window_name:
            return year

    return "UNKNOWN"


def classify_stress_result(row: pd.Series) -> str:
    total_trades = int(row.get("total_trades", 0))
    compound_return = safe_float(row.get("compound_return"), 0.0)
    avg_profit_factor = safe_float(row.get("avg_profit_factor"), 0.0)
    worst_drawdown = safe_float(row.get("worst_drawdown"), 0.0)
    positive_window_rate = safe_float(row.get("positive_window_rate"), 0.0)

    if total_trades < 30:
        return "TOO_FEW_TRADES"

    if (
        compound_return > 0.15
        and avg_profit_factor >= 1.20
        and worst_drawdown > -0.15
        and positive_window_rate >= 0.55
    ):
        return "STRESS_PROMISING"

    if (
        compound_return > 0.00
        and avg_profit_factor >= 1.05
        and worst_drawdown > -0.12
        and positive_window_rate >= 0.45
    ):
        return "STRESS_WEAK_PASS"

    if (
        compound_return > -0.05
        and avg_profit_factor >= 0.95
        and worst_drawdown > -0.10
    ):
        return "STRESS_NEAR_BREAKEVEN"

    return "STRESS_FAILED"


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
        worst_drawdown = float(pd.to_numeric(group["max_drawdown_pct"], errors="coerce").min())

        windows = int(group["window_name"].nunique())
        positive_windows = int((return_series > 0).sum())
        negative_windows = int((return_series <= 0).sum())
        positive_window_rate = positive_windows / windows if windows else 0.0

        insufficient_windows = int((group["window_status"] == "INSUFFICIENT_TRADES").sum())
        failed_windows = int((group["window_status"] == "FAILED").sum())
        near_breakeven_windows = int((group["window_status"] == "NEAR_BREAKEVEN").sum())
        weak_pass_windows = int((group["window_status"] == "WEAK_PASS").sum())
        passed_windows = int((group["window_status"] == "PASSED").sum())

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
                "positive_windows": positive_windows,
                "negative_windows": negative_windows,
                "positive_window_rate": positive_window_rate,
                "passed_windows": passed_windows,
                "weak_pass_windows": weak_pass_windows,
                "near_breakeven_windows": near_breakeven_windows,
                "failed_windows": failed_windows,
                "insufficient_windows": insufficient_windows,
            }
        )

        row["stress_decision"] = classify_stress_result(pd.Series(row))

        rows.append(row)

    summary_df = pd.DataFrame(rows)

    sort_cols = [
        col for col in ["strategy_name", "symbol", "year"] if col in summary_df.columns
    ]

    if "compound_return" in summary_df.columns:
        summary_df = summary_df.sort_values(
            by=sort_cols + ["compound_return"] if sort_cols else ["compound_return"],
            ascending=[True] * len(sort_cols) + [False] if sort_cols else [False],
        )

    return summary_df


def summarize_context_pairs(trades_df: pd.DataFrame) -> pd.DataFrame:
    if trades_df.empty:
        return pd.DataFrame()

    df = trades_df.copy()

    df["net_pnl"] = pd.to_numeric(df["net_pnl"], errors="coerce").fillna(0.0)

    group_cols = [
        "strategy_name",
        "direction",
        "directional_context_v3",
        "bias_1h_v3",
        "bias_4h_v3",
        "long_context_decision_v3_1",
        "short_context_decision_v3_1",
    ]

    rows = []

    for keys, group in df.groupby(group_cols):
        (
            strategy_name,
            direction,
            directional_context,
            bias_1h,
            bias_4h,
            long_decision,
            short_decision,
        ) = keys

        gross_profit = float(group.loc[group["net_pnl"] > 0, "net_pnl"].sum())
        gross_loss = float(group.loc[group["net_pnl"] < 0, "net_pnl"].sum())

        if gross_loss == 0:
            profit_factor = None if gross_profit > 0 else 0.0
        else:
            profit_factor = gross_profit / abs(gross_loss)

        by_symbol = group.groupby("symbol")["net_pnl"].sum()
        positive_symbols = int((by_symbol > 0).sum())
        negative_symbols = int((by_symbol <= 0).sum())

        by_year = group.groupby("year")["net_pnl"].sum()
        positive_years = int((by_year > 0).sum())
        negative_years = int((by_year <= 0).sum())

        rows.append(
            {
                "strategy_name": strategy_name,
                "direction": direction,
                "directional_context_v3": directional_context,
                "bias_1h_v3": bias_1h,
                "bias_4h_v3": bias_4h,
                "long_context_decision_v3_1": long_decision,
                "short_context_decision_v3_1": short_decision,
                "symbols": int(group["symbol"].nunique()),
                "years": int(group["year"].nunique()),
                "trades": int(len(group)),
                "wins": int((group["net_pnl"] > 0).sum()),
                "losses": int((group["net_pnl"] <= 0).sum()),
                "win_rate": float((group["net_pnl"] > 0).mean()),
                "total_net_pnl": float(group["net_pnl"].sum()),
                "avg_net_pnl": float(group["net_pnl"].mean()),
                "profit_factor": profit_factor,
                "positive_symbols": positive_symbols,
                "negative_symbols": negative_symbols,
                "positive_years": positive_years,
                "negative_years": negative_years,
            }
        )

    result = pd.DataFrame(rows)
    result = result.sort_values(by="total_net_pnl", ascending=False)

    return result


def print_section(title: str):
    print()
    print(title)
    print("=" * 100)


def print_final_decision(strategy_summary_df: pd.DataFrame, context_summary_df: pd.DataFrame):
    print_section("FINAL V3.1 EXTENDED STRESS DECISION")

    if strategy_summary_df.empty:
        print("NO_DATA")
        return

    display_cols = [
        "strategy_name",
        "stress_decision",
        "windows",
        "total_trades",
        "compound_return",
        "avg_profit_factor",
        "worst_drawdown",
        "positive_window_rate",
        "failed_windows",
        "insufficient_windows",
    ]

    print(strategy_summary_df[display_cols].to_string(index=False))

    print()
    print("Interpretacion:")
    print("- STRESS_PROMISING no significa estrategia operable; solo contexto resistente.")
    print("- TOO_FEW_TRADES significa que el filtro es defensivo, pero no suficiente para aprobar.")
    print("- Si el par robusto falla en ETH/SOL o años antiguos, V3.1 queda como filtro parcial.")
    print("- Si se mantiene positivo, el siguiente paso lógico es Structural Confirmation Engine V1.")
    print("- No paper trading todavía.")


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

    print("V3.1 EXTENDED STRESS VALIDATION")
    print("=" * 100)
    print("Symbols: BTCUSDT, ETHUSDT, SOLUSDT")
    print("Windows: quarterly, 2022-01-01 to 2026-01-01")
    print("Purpose: test whether V3.1 is stable beyond BTC 2024-2025")
    print()

    all_results = []
    all_trades = []
    errors = []

    for symbol in symbols:
        for window_name, start_date, end_date in windows:
            full_window_name = f"{symbol}_{window_name}"

            try:
                window_results, trades_df = validate_window(
                    symbol=symbol,
                    window_name=full_window_name,
                    start_date=start_date,
                    end_date=end_date,
                )

                for row in window_results:
                    row["symbol"] = symbol
                    row["base_window"] = window_name
                    row["year"] = get_year_from_window(window_name)
                    all_results.append(row)

                if not trades_df.empty:
                    trades_df = trades_df.copy()
                    trades_df["symbol"] = symbol
                    trades_df["base_window"] = window_name
                    trades_df["year"] = get_year_from_window(window_name)
                    all_trades.append(trades_df)

            except Exception as exc:
                error_row = {
                    "symbol": symbol,
                    "window_name": full_window_name,
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

    reports_dir = Path("reports") / "directional_context_v3_1_stress"
    reports_dir.mkdir(parents=True, exist_ok=True)

    results_output = reports_dir / "v3_1_stress_window_results.csv"
    trades_output = reports_dir / "v3_1_stress_trade_diagnostics.csv"
    errors_output = reports_dir / "v3_1_stress_errors.csv"

    strategy_summary_df = summarize_group(results_df, ["strategy_name"])
    symbol_summary_df = summarize_group(results_df, ["strategy_name", "symbol"])
    year_summary_df = summarize_group(results_df, ["strategy_name", "year"])
    context_summary_df = summarize_context_pairs(trades_all_df)

    strategy_summary_output = reports_dir / "v3_1_stress_strategy_summary.csv"
    symbol_summary_output = reports_dir / "v3_1_stress_symbol_summary.csv"
    year_summary_output = reports_dir / "v3_1_stress_year_summary.csv"
    context_summary_output = reports_dir / "v3_1_stress_context_pair_summary.csv"

    results_df.to_csv(results_output, index=False)
    trades_all_df.to_csv(trades_output, index=False)
    errors_df.to_csv(errors_output, index=False)
    strategy_summary_df.to_csv(strategy_summary_output, index=False)
    symbol_summary_df.to_csv(symbol_summary_output, index=False)
    year_summary_df.to_csv(year_summary_output, index=False)
    context_summary_df.to_csv(context_summary_output, index=False)

    print_section("V3.1 STRESS AGGREGATE BY STRATEGY")
    if strategy_summary_df.empty:
        print("Sin resultados.")
    else:
        print(
            strategy_summary_df[
                [
                    "strategy_name",
                    "stress_decision",
                    "windows",
                    "total_trades",
                    "compound_return",
                    "avg_return",
                    "avg_profit_factor",
                    "worst_drawdown",
                    "positive_windows",
                    "negative_windows",
                    "positive_window_rate",
                    "failed_windows",
                    "insufficient_windows",
                ]
            ].to_string(index=False)
        )

    print_section("V3.1 STRESS BY SYMBOL")
    if symbol_summary_df.empty:
        print("Sin resultados.")
    else:
        print(
            symbol_summary_df[
                [
                    "strategy_name",
                    "symbol",
                    "stress_decision",
                    "windows",
                    "total_trades",
                    "compound_return",
                    "avg_profit_factor",
                    "worst_drawdown",
                    "positive_window_rate",
                    "failed_windows",
                    "insufficient_windows",
                ]
            ].to_string(index=False)
        )

    print_section("V3.1 STRESS BY YEAR")
    if year_summary_df.empty:
        print("Sin resultados.")
    else:
        print(
            year_summary_df[
                [
                    "strategy_name",
                    "year",
                    "stress_decision",
                    "windows",
                    "total_trades",
                    "compound_return",
                    "avg_profit_factor",
                    "worst_drawdown",
                    "positive_window_rate",
                    "failed_windows",
                    "insufficient_windows",
                ]
            ].to_string(index=False)
        )

    print_section("V3.1 STRESS CONTEXT PAIR SUMMARY")
    if context_summary_df.empty:
        print("Sin trades.")
    else:
        print(
            context_summary_df[
                [
                    "strategy_name",
                    "direction",
                    "directional_context_v3",
                    "bias_1h_v3",
                    "bias_4h_v3",
                    "short_context_decision_v3_1",
                    "long_context_decision_v3_1",
                    "symbols",
                    "years",
                    "trades",
                    "win_rate",
                    "total_net_pnl",
                    "profit_factor",
                    "positive_symbols",
                    "negative_symbols",
                    "positive_years",
                    "negative_years",
                ]
            ].head(40).to_string(index=False)
        )

    print_section("V3.1 STRESS ERRORS")
    if errors_df.empty:
        print("Sin errores.")
    else:
        print(errors_df.to_string(index=False))

    print_final_decision(strategy_summary_df, context_summary_df)

    print()
    print("ARCHIVOS GENERADOS")
    print("=" * 100)
    print(f"- {results_output}")
    print(f"- {trades_output}")
    print(f"- {errors_output}")
    print(f"- {strategy_summary_output}")
    print(f"- {symbol_summary_output}")
    print(f"- {year_summary_output}")
    print(f"- {context_summary_output}")


if __name__ == "__main__":
    main()