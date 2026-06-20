from pathlib import Path
import pandas as pd

from src.backtesting.backtesting_engine_v3 import run_backtest_v3
from src.market_structure.structural_confirmation_engine_v1 import (
    add_structural_confirmation_v1_columns,
)
from src.strategies.fib_v5_mtf_strategy import fib_v5_short_with_mtf_filter
from src.strategies.fib_v5_mtf_liquidity_v2_strategy import (
    fib_v5_short_with_mtf_and_liquidity_v2_filter,
)
from src.workflows.robust_validate_short_candidates import (
    build_short_config,
    classify_market_window,
)
from src.workflows.validate_directional_context_filter_v3_1 import (
    build_combined_context_dataset_v3_1,
    short_mtf_with_directional_context_v3_1,
    short_mtf_liquidity_v2_with_directional_context_v3_1,
)
from src.workflows.validate_long_v2_candidate_robust import (
    calculate_market_return,
    download_binance_klines_range,
)

def is_true(value) -> bool:
    if value is None:
        return False

    try:
        if pd.isna(value):
            return False
    except Exception:
        pass

    value_text = str(value).strip().lower()

    return value_text in {
        "true",
        "1",
        "yes",
        "y",
    }

def short_mtf_v3_1_structural_balanced(df, index: int, config=None) -> str:
    base_signal = short_mtf_with_directional_context_v3_1(df, index, config)

    if base_signal != "SHORT":
        return "NONE"

    row = df.iloc[index]

    if is_true(row.get("short_structural_confirmed_v1_balanced", False)):
        return "SHORT"

    return "NONE"


def short_mtf_v3_1_structural_strict(df, index: int, config=None) -> str:
    base_signal = short_mtf_with_directional_context_v3_1(df, index, config)

    if base_signal != "SHORT":
        return "NONE"

    row = df.iloc[index]

    if is_true(row.get("short_structural_confirmed_v1_strict", False)):
        return "SHORT"

    return "NONE"

def short_mtf_v3_1_not_chasing_only(df, index: int, config=None) -> str:
    base_signal = short_mtf_with_directional_context_v3_1(df, index, config)

    if base_signal != "SHORT":
        return "NONE"

    row = df.iloc[index]

    if is_true(row.get("short_structural_confirmed_v1_not_chasing_only", False)):
        return "SHORT"

    return "NONE"


def short_mtf_v3_1_sweep_or_rejection(df, index: int, config=None) -> str:
    base_signal = short_mtf_with_directional_context_v3_1(df, index, config)

    if base_signal != "SHORT":
        return "NONE"

    row = df.iloc[index]

    if is_true(row.get("short_structural_confirmed_v1_sweep_or_rejection", False)):
        return "SHORT"

    return "NONE"


def short_mtf_v3_1_recent_score_2(df, index: int, config=None) -> str:
    base_signal = short_mtf_with_directional_context_v3_1(df, index, config)

    if base_signal != "SHORT":
        return "NONE"

    row = df.iloc[index]

    if is_true(row.get("short_structural_recent_score_2_lookback_4", False)):
        return "SHORT"

    return "NONE"

def short_mtf_liquidity_v2_v3_1_structural_balanced(df, index: int, config=None) -> str:
    base_signal = short_mtf_liquidity_v2_with_directional_context_v3_1(
        df,
        index,
        config,
    )

    if base_signal != "SHORT":
        return "NONE"

    row = df.iloc[index]

    if is_true(row.get("short_structural_confirmed_v1_balanced", False)):
        return "SHORT"

    return "NONE"


def short_mtf_liquidity_v2_v3_1_structural_strict(df, index: int, config=None) -> str:
    base_signal = short_mtf_liquidity_v2_with_directional_context_v3_1(
        df,
        index,
        config,
    )

    if base_signal != "SHORT":
        return "NONE"

    row = df.iloc[index]

    if is_true(row.get("short_structural_confirmed_v1_strict", False)):
        return "SHORT"

    return "NONE"

def short_mtf_liquidity_v2_v3_1_not_chasing_only(df, index: int, config=None) -> str:
    base_signal = short_mtf_liquidity_v2_with_directional_context_v3_1(
        df,
        index,
        config,
    )

    if base_signal != "SHORT":
        return "NONE"

    row = df.iloc[index]

    if is_true(row.get("short_structural_confirmed_v1_not_chasing_only", False)):
        return "SHORT"

    return "NONE"


def short_mtf_liquidity_v2_v3_1_sweep_or_rejection(df, index: int, config=None) -> str:
    base_signal = short_mtf_liquidity_v2_with_directional_context_v3_1(
        df,
        index,
        config,
    )

    if base_signal != "SHORT":
        return "NONE"

    row = df.iloc[index]

    if is_true(row.get("short_structural_confirmed_v1_sweep_or_rejection", False)):
        return "SHORT"

    return "NONE"


def short_mtf_liquidity_v2_v3_1_recent_score_2(df, index: int, config=None) -> str:
    base_signal = short_mtf_liquidity_v2_with_directional_context_v3_1(
        df,
        index,
        config,
    )

    if base_signal != "SHORT":
        return "NONE"

    row = df.iloc[index]

    if is_true(row.get("short_structural_recent_score_2_lookback_4", False)):
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
    symbol: str,
    base_window: str,
    window_name: str,
    strategy_name: str,
    direction: str,
    market_return_pct: float,
    trades_df: pd.DataFrame,
    summary: dict,
) -> dict:
    row = {
        "symbol": symbol,
        "base_window": base_window,
        "year": base_window[:4],
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
    }

    row["window_status"] = classify_result(row)

    return row


def add_trade_context(
    trades_df: pd.DataFrame,
    market_df: pd.DataFrame,
    symbol: str,
    base_window: str,
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
        row["symbol"] = symbol
        row["base_window"] = base_window
        row["year"] = base_window[:4]
        row["window_name"] = window_name
        row["strategy_name"] = strategy_name
        row["direction"] = direction

        context_cols = [
            "bias_1h_v3",
            "bias_4h_v3",
            "directional_context_v3",
            "short_context_decision_v3_1",
            "short_allowed_v3_1",
            "short_structural_score_v1",
            "short_structural_reason_v1",
            "short_structural_block_reason_v1",
            "short_structural_confirmed_v1_balanced",
            "short_structural_confirmed_v1_strict",
            "scv1_break_low_10",
            "scv1_break_low_20",
            "scv1_sweep_high_reject",
            "scv1_bearish_rejection_candle",
            "scv1_below_ema20_with_down_slope",
            "scv1_not_chasing_down",
            "scv1_distance_ema20_atr",
            "scv1_range_position_48",
            "scv1_rsi14",
            "short_structural_confirmed_v1_not_chasing_only",
            "short_structural_confirmed_v1_sweep_or_rejection",
            "short_structural_confirmed_v1_score_2",
            "short_structural_confirmed_v1_score_3",
            "short_structural_recent_score_2_lookback_4",
            "short_structural_recent_sweep_or_rejection_lookback_4",
        ]

        for col in context_cols:
            row[col] = entry_row.get(col, None)

        rows.append(row)

    return pd.DataFrame(rows)


def validate_window_structural(
    symbol: str,
    base_window: str,
    start_date: str,
    end_date: str,
) -> tuple[list[dict], pd.DataFrame]:
    data_dir = Path("data") / "structural_confirmation_v1"
    reports_dir = Path("reports") / "structural_confirmation_v1"

    data_dir.mkdir(parents=True, exist_ok=True)
    reports_dir.mkdir(parents=True, exist_ok=True)

    window_name = f"{symbol}_{base_window}"
    base_name = f"{symbol.lower()}_{base_window}"

    csv_15m = data_dir / f"{base_name}_15m.csv"
    csv_1h = data_dir / f"{base_name}_1h.csv"
    csv_4h = data_dir / f"{base_name}_4h.csv"

    enriched_csv = reports_dir / f"{base_name}_structural_context_v1.csv"

    print()
    print(f"STRUCTURAL CONFIRMATION V1 WINDOW: {window_name}")
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

    market_df = add_structural_confirmation_v1_columns(market_df)
    market_df.to_csv(enriched_csv, index=False)

    strategies = [
        {
            "strategy_name": "SHORT_FIB_V5_MTF_V3_1",
            "direction": "SHORT",
            "strategy_func": short_mtf_with_directional_context_v3_1,
            "config": build_short_config(),
        },
        {
            "strategy_name": "SHORT_FIB_V5_MTF_V3_1_NOT_CHASING_ONLY",
            "direction": "SHORT",
            "strategy_func": short_mtf_v3_1_not_chasing_only,
            "config": build_short_config(),
        },
        {
            "strategy_name": "SHORT_FIB_V5_MTF_V3_1_SWEEP_OR_REJECTION",
            "direction": "SHORT",
            "strategy_func": short_mtf_v3_1_sweep_or_rejection,
            "config": build_short_config(),
        },
        {
            "strategy_name": "SHORT_FIB_V5_MTF_V3_1_SCORE_2",
            "direction": "SHORT",
            "strategy_func": short_mtf_v3_1_structural_balanced,
            "config": build_short_config(),
        },
        {
            "strategy_name": "SHORT_FIB_V5_MTF_V3_1_SCORE_3",
            "direction": "SHORT",
            "strategy_func": short_mtf_v3_1_structural_strict,
            "config": build_short_config(),
        },
        {
            "strategy_name": "SHORT_FIB_V5_MTF_V3_1_RECENT_SCORE_2_LB4",
            "direction": "SHORT",
            "strategy_func": short_mtf_v3_1_recent_score_2,
            "config": build_short_config(),
        },
        {
            "strategy_name": "SHORT_FIB_V5_MTF_LIQUIDITY_V2_V3_1",
            "direction": "SHORT",
            "strategy_func": short_mtf_liquidity_v2_with_directional_context_v3_1,
            "config": build_short_config(),
        },
        {
            "strategy_name": "SHORT_FIB_V5_MTF_LIQUIDITY_V2_V3_1_NOT_CHASING_ONLY",
            "direction": "SHORT",
            "strategy_func": short_mtf_liquidity_v2_v3_1_not_chasing_only,
            "config": build_short_config(),
        },
        {
            "strategy_name": "SHORT_FIB_V5_MTF_LIQUIDITY_V2_V3_1_SWEEP_OR_REJECTION",
            "direction": "SHORT",
            "strategy_func": short_mtf_liquidity_v2_v3_1_sweep_or_rejection,
            "config": build_short_config(),
        },
        {
            "strategy_name": "SHORT_FIB_V5_MTF_LIQUIDITY_V2_V3_1_SCORE_2",
            "direction": "SHORT",
            "strategy_func": short_mtf_liquidity_v2_v3_1_structural_balanced,
            "config": build_short_config(),
        },
        {
            "strategy_name": "SHORT_FIB_V5_MTF_LIQUIDITY_V2_V3_1_SCORE_3",
            "direction": "SHORT",
            "strategy_func": short_mtf_liquidity_v2_v3_1_structural_strict,
            "config": build_short_config(),
        },
        {
            "strategy_name": "SHORT_FIB_V5_MTF_LIQUIDITY_V2_V3_1_RECENT_SCORE_2_LB4",
            "direction": "SHORT",
            "strategy_func": short_mtf_liquidity_v2_v3_1_recent_score_2,
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
            symbol=symbol,
            base_window=base_window,
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
            symbol=symbol,
            base_window=base_window,
            window_name=window_name,
            strategy_name=strategy_name,
            direction=direction,
        )

        if not trades_with_context.empty:
            window_trades.append(trades_with_context)

        print(
            f"{strategy_name} | "
            f"symbol={symbol} | "
            f"window={base_window} | "
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


def safe_float(value, default=0.0):
    try:
        if value is None or pd.isna(value):
            return default

        return float(value)
    except Exception:
        return default


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
        return "STRUCTURAL_PROMISING"

    if (
        compound_return > 0.00
        and avg_profit_factor >= 1.05
        and worst_drawdown > -0.12
        and positive_window_rate >= 0.45
    ):
        return "STRUCTURAL_WEAK_PASS"

    if (
        compound_return > -0.05
        and avg_profit_factor >= 0.95
        and worst_drawdown > -0.10
    ):
        return "STRUCTURAL_NEAR_BREAKEVEN"

    return "STRUCTURAL_FAILED"


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
                "positive_windows": positive_windows,
                "negative_windows": negative_windows,
                "positive_window_rate": positive_window_rate,
                "failed_windows": failed_windows,
                "insufficient_windows": insufficient_windows,
            }
        )

        row["structural_decision"] = classify_stress_result(pd.Series(row))

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


def summarize_structural_reasons(trades_df: pd.DataFrame) -> pd.DataFrame:
    if trades_df.empty:
        return pd.DataFrame()

    df = trades_df.copy()

    df["net_pnl"] = pd.to_numeric(df["net_pnl"], errors="coerce").fillna(0.0)

    group_cols = [
        "strategy_name",
        "short_structural_reason_v1",
        "short_structural_block_reason_v1",
    ]

    rows = []

    for keys, group in df.groupby(group_cols):
        strategy_name, structural_reason, block_reason = keys

        gross_profit = float(group.loc[group["net_pnl"] > 0, "net_pnl"].sum())
        gross_loss = float(group.loc[group["net_pnl"] < 0, "net_pnl"].sum())

        if gross_loss == 0:
            profit_factor = None if gross_profit > 0 else 0.0
        else:
            profit_factor = gross_profit / abs(gross_loss)

        rows.append(
            {
                "strategy_name": strategy_name,
                "structural_reason": structural_reason,
                "block_reason": block_reason,
                "symbols": int(group["symbol"].nunique()),
                "years": int(group["year"].nunique()),
                "trades": int(len(group)),
                "wins": int((group["net_pnl"] > 0).sum()),
                "losses": int((group["net_pnl"] <= 0).sum()),
                "win_rate": float((group["net_pnl"] > 0).mean()),
                "total_net_pnl": float(group["net_pnl"].sum()),
                "avg_net_pnl": float(group["net_pnl"].mean()),
                "profit_factor": profit_factor,
                "avg_structural_score": float(
                    pd.to_numeric(
                        group["short_structural_score_v1"],
                        errors="coerce",
                    ).mean()
                ),
            }
        )

    result = pd.DataFrame(rows)
    result = result.sort_values(by="total_net_pnl", ascending=False)

    return result


def print_section(title: str):
    print()
    print(title)
    print("=" * 100)


def print_base_vs_structural(strategy_summary_df: pd.DataFrame):
    print_section("BASE V3.1 VS STRUCTURAL CONFIRMATION V1")

    if strategy_summary_df.empty:
        print("Sin resultados.")
        return

    pairs = [
        (
            "SHORT_FIB_V5_MTF_V3_1",
            "SHORT_FIB_V5_MTF_V3_1_NOT_CHASING_ONLY",
        ),
        (
            "SHORT_FIB_V5_MTF_V3_1",
            "SHORT_FIB_V5_MTF_V3_1_SWEEP_OR_REJECTION",
        ),
        (
            "SHORT_FIB_V5_MTF_V3_1",
            "SHORT_FIB_V5_MTF_V3_1_SCORE_2",
        ),
        (
            "SHORT_FIB_V5_MTF_V3_1",
            "SHORT_FIB_V5_MTF_V3_1_SCORE_3",
        ),
        (
            "SHORT_FIB_V5_MTF_V3_1",
            "SHORT_FIB_V5_MTF_V3_1_RECENT_SCORE_2_LB4",
        ),
        (
            "SHORT_FIB_V5_MTF_LIQUIDITY_V2_V3_1",
            "SHORT_FIB_V5_MTF_LIQUIDITY_V2_V3_1_NOT_CHASING_ONLY",
        ),
        (
            "SHORT_FIB_V5_MTF_LIQUIDITY_V2_V3_1",
            "SHORT_FIB_V5_MTF_LIQUIDITY_V2_V3_1_SWEEP_OR_REJECTION",
        ),
        (
            "SHORT_FIB_V5_MTF_LIQUIDITY_V2_V3_1",
            "SHORT_FIB_V5_MTF_LIQUIDITY_V2_V3_1_SCORE_2",
        ),
        (
            "SHORT_FIB_V5_MTF_LIQUIDITY_V2_V3_1",
            "SHORT_FIB_V5_MTF_LIQUIDITY_V2_V3_1_SCORE_3",
        ),
        (
            "SHORT_FIB_V5_MTF_LIQUIDITY_V2_V3_1",
            "SHORT_FIB_V5_MTF_LIQUIDITY_V2_V3_1_RECENT_SCORE_2_LB4",
        ),
    ]

    rows = []

    for base_name, filtered_name in pairs:
        base = strategy_summary_df[strategy_summary_df["strategy_name"] == base_name]
        filtered = strategy_summary_df[
            strategy_summary_df["strategy_name"] == filtered_name
        ]

        if base.empty or filtered.empty:
            continue

        base_row = base.iloc[0]
        filtered_row = filtered.iloc[0]

        rows.append(
            {
                "base_strategy": base_name,
                "filtered_strategy": filtered_name,
                "base_trades": int(base_row["total_trades"]),
                "filtered_trades": int(filtered_row["total_trades"]),
                "trades_removed": int(
                    base_row["total_trades"] - filtered_row["total_trades"]
                ),
                "base_compound_return": float(base_row["compound_return"]),
                "filtered_compound_return": float(filtered_row["compound_return"]),
                "return_delta": float(
                    filtered_row["compound_return"] - base_row["compound_return"]
                ),
                "base_avg_pf": float(base_row["avg_profit_factor"]),
                "filtered_avg_pf": float(filtered_row["avg_profit_factor"]),
                "base_worst_dd": float(base_row["worst_drawdown"]),
                "filtered_worst_dd": float(filtered_row["worst_drawdown"]),
                "base_positive_window_rate": float(base_row["positive_window_rate"]),
                "filtered_positive_window_rate": float(
                    filtered_row["positive_window_rate"]
                ),
            }
        )

    comparison_df = pd.DataFrame(rows)

    if comparison_df.empty:
        print("Sin comparacion.")
    else:
        print(comparison_df.to_string(index=False))


def print_final_decision(strategy_summary_df: pd.DataFrame):
    print_section("FINAL STRUCTURAL CONFIRMATION V1 DECISION")

    if strategy_summary_df.empty:
        print("NO_DATA")
        return

    display_cols = [
        "strategy_name",
        "structural_decision",
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
    print("- Si STRUCTURAL_BALANCED mejora drawdown/PF sin destruir la muestra, sirve.")
    print("- Si STRUCTURAL_STRICT queda con pocos trades, queda solo como filtro defensivo.")
    print("- Si ambos empeoran a V3.1, la estructura elegida no aporta.")
    print("- No paper trading todavía; esta fase solo valida confirmacion estructural.")


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

    print("STRUCTURAL CONFIRMATION ENGINE V1 VALIDATION")
    print("=" * 100)
    print("Symbols: BTCUSDT, ETHUSDT, SOLUSDT")
    print("Windows: quarterly, 2022-01-01 to 2026-01-01")
    print("Purpose: test if structural confirmation improves V3.1 short context")
    print()

    all_results = []
    all_trades = []
    errors = []

    for symbol in symbols:
        for base_window, start_date, end_date in windows:
            try:
                window_results, trades_df = validate_window_structural(
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

    strategy_summary_df = summarize_group(results_df, ["strategy_name"])
    symbol_summary_df = summarize_group(results_df, ["strategy_name", "symbol"])
    year_summary_df = summarize_group(results_df, ["strategy_name", "year"])
    reason_summary_df = summarize_structural_reasons(trades_all_df)

    reports_dir = Path("reports") / "structural_confirmation_v1"
    reports_dir.mkdir(parents=True, exist_ok=True)

    results_output = reports_dir / "structural_confirmation_v1_window_results.csv"
    trades_output = reports_dir / "structural_confirmation_v1_trade_diagnostics.csv"
    errors_output = reports_dir / "structural_confirmation_v1_errors.csv"
    strategy_summary_output = reports_dir / "structural_confirmation_v1_strategy_summary.csv"
    symbol_summary_output = reports_dir / "structural_confirmation_v1_symbol_summary.csv"
    year_summary_output = reports_dir / "structural_confirmation_v1_year_summary.csv"
    reason_summary_output = reports_dir / "structural_confirmation_v1_reason_summary.csv"

    results_df.to_csv(results_output, index=False)
    trades_all_df.to_csv(trades_output, index=False)
    errors_df.to_csv(errors_output, index=False)
    strategy_summary_df.to_csv(strategy_summary_output, index=False)
    symbol_summary_df.to_csv(symbol_summary_output, index=False)
    year_summary_df.to_csv(year_summary_output, index=False)
    reason_summary_df.to_csv(reason_summary_output, index=False)

    print_section("STRUCTURAL CONFIRMATION V1 AGGREGATE BY STRATEGY")
    if strategy_summary_df.empty:
        print("Sin resultados.")
    else:
        print(
            strategy_summary_df[
                [
                    "strategy_name",
                    "structural_decision",
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

    print_section("STRUCTURAL CONFIRMATION V1 BY SYMBOL")
    if symbol_summary_df.empty:
        print("Sin resultados.")
    else:
        print(
            symbol_summary_df[
                [
                    "strategy_name",
                    "symbol",
                    "structural_decision",
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

    print_section("STRUCTURAL CONFIRMATION V1 BY YEAR")
    if year_summary_df.empty:
        print("Sin resultados.")
    else:
        print(
            year_summary_df[
                [
                    "strategy_name",
                    "year",
                    "structural_decision",
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

    print_base_vs_structural(strategy_summary_df)

    print_section("STRUCTURAL CONFIRMATION V1 REASON SUMMARY")
    if reason_summary_df.empty:
        print("Sin trades.")
    else:
        print(
            reason_summary_df[
                [
                    "strategy_name",
                    "structural_reason",
                    "block_reason",
                    "symbols",
                    "years",
                    "trades",
                    "win_rate",
                    "total_net_pnl",
                    "profit_factor",
                    "avg_structural_score",
                ]
            ].head(60).to_string(index=False)
        )

    print_section("STRUCTURAL CONFIRMATION V1 ERRORS")
    if errors_df.empty:
        print("Sin errores.")
    else:
        print(errors_df.to_string(index=False))

    print_final_decision(strategy_summary_df)

    print()
    print("ARCHIVOS GENERADOS")
    print("=" * 100)
    print(f"- {results_output}")
    print(f"- {trades_output}")
    print(f"- {errors_output}")
    print(f"- {strategy_summary_output}")
    print(f"- {symbol_summary_output}")
    print(f"- {year_summary_output}")
    print(f"- {reason_summary_output}")


if __name__ == "__main__":
    main()