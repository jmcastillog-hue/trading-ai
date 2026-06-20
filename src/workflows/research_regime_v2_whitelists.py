from pathlib import Path
import pandas as pd

from src.backtesting.backtesting_engine_v3 import run_backtest_v3
from src.market_structure.regime_filter_v2 import enrich_with_regime_filter_v2
from src.workflows.validate_long_v2_candidate_robust import (
    download_binance_klines_range,
    calculate_market_return,
)
from src.workflows.diagnose_regime_filter_v2 import (
    build_config,
    long_v2_entry_logic,
)


def get_whitelists() -> dict:
    """
    Research-only whitelists.

    These are not final trading rules.
    They test which 1h/4h Market State V2 combinations preserve edge.
    """

    bullish_core = {
        ("BULLISH_CONTINUATION", "BULLISH_CONTINUATION"),
        ("BULLISH_CONTINUATION", "BULLISH_PULLBACK"),
        ("BULLISH_PULLBACK", "BULLISH_CONTINUATION"),
        ("BULLISH_PULLBACK", "BULLISH_PULLBACK"),
    }

    continuation_exhaustion = {
        ("BULLISH_CONTINUATION", "BULLISH_CONTINUATION"),
        ("BULLISH_CONTINUATION", "BULLISH_EXHAUSTION"),
    }

    core_plus_exhaustion = bullish_core | {
        ("BULLISH_CONTINUATION", "BULLISH_EXHAUSTION"),
        ("BULLISH_EXHAUSTION", "BULLISH_EXHAUSTION"),
    }

    pullback_only = {
        ("BULLISH_PULLBACK", "BULLISH_PULLBACK"),
        ("BULLISH_PULLBACK", "BULLISH_CONTINUATION"),
        ("BULLISH_CONTINUATION", "BULLISH_PULLBACK"),
    }

    continuation_only = {
        ("BULLISH_CONTINUATION", "BULLISH_CONTINUATION"),
        ("BULLISH_CONTINUATION", "BULLISH_EXHAUSTION"),
        ("BULLISH_CONTINUATION", "NEUTRAL_TRANSITION"),
    }

    exhaustion_reversal_research = {
        ("BULLISH_CONTINUATION", "BULLISH_EXHAUSTION"),
        ("BULLISH_EXHAUSTION", "BULLISH_EXHAUSTION"),
        ("REVERSAL_RISK", "BULLISH_CONTINUATION"),
        ("REVERSAL_RISK", "BULLISH_EXHAUSTION"),
    }

    countertrend_rebound_research = {
        ("BEARISH_PULLBACK", "BEARISH_PULLBACK"),
        ("BEARISH_PULLBACK", "RANGE_CHOP"),
        ("RANGE_CHOP", "RANGE_CHOP"),
    }

    # Intentionally data-mined from Fase 1.16 diagnostics.
    # This is only to understand whether prior profitable state pairs remain robust.
    # It must not be treated as an operative filter without further validation.
    prior_positive_pairs_experimental = {
        ("BULLISH_CONTINUATION", "BULLISH_EXHAUSTION"),
        ("BEARISH_PULLBACK", "BEARISH_PULLBACK"),
        ("REVERSAL_RISK", "BULLISH_CONTINUATION"),
        ("BEARISH_PULLBACK", "RANGE_CHOP"),
        ("BULLISH_EXHAUSTION", "BULLISH_EXHAUSTION"),
        ("REVERSAL_RISK", "BULLISH_EXHAUSTION"),
        ("NEUTRAL_TRANSITION", "RANGE_CHOP"),
        ("REVERSAL_RISK", "NEUTRAL_TRANSITION"),
        ("BULLISH_CONTINUATION", "BEARISH_PULLBACK"),
        ("BULLISH_CONTINUATION", "NEUTRAL_TRANSITION"),
        ("REVERSAL_RISK", "REVERSAL_RISK"),
        ("BULLISH_PULLBACK", "BULLISH_PULLBACK"),
        ("RANGE_CHOP", "RANGE_CHOP"),
        ("NEUTRAL_TRANSITION", "REVERSAL_RISK"),
        ("RANGE_CHOP", "BEARISH_PULLBACK"),
    }

    return {
        "NO_STATE_FILTER_BASELINE": None,
        "STRICT_BULLISH_CORE": bullish_core,
        "CONTINUATION_EXHAUSTION": continuation_exhaustion,
        "CORE_PLUS_EXHAUSTION": core_plus_exhaustion,
        "PULLBACK_ONLY": pullback_only,
        "CONTINUATION_ONLY": continuation_only,
        "EXHAUSTION_REVERSAL_RESEARCH": exhaustion_reversal_research,
        "COUNTERTREND_REBOUND_RESEARCH": countertrend_rebound_research,
        "PRIOR_POSITIVE_PAIRS_EXPERIMENTAL": prior_positive_pairs_experimental,
    }


def make_whitelist_signal(allowed_pairs):
    def strategy_func(df: pd.DataFrame, index: int, config=None) -> str:
        if not long_v2_entry_logic(df, index):
            return "NONE"

        if allowed_pairs is None:
            return "LONG"

        row = df.iloc[index]

        state_1h = str(row.get("state_1h_v2", "UNKNOWN"))
        state_4h = str(row.get("state_4h_v2", "UNKNOWN"))

        if (state_1h, state_4h) not in allowed_pairs:
            return "NONE"

        return "LONG"

    return strategy_func


def classify_window(row) -> str:
    trades = int(row["total_trades"])
    total_return_pct = float(row["total_return_pct"])
    max_drawdown_pct = float(row["max_drawdown_pct"])
    profit_factor = row["profit_factor"]

    if trades < 5:
        return "INSUFFICIENT_TRADES"

    if profit_factor is None or pd.isna(profit_factor):
        if total_return_pct > 0 and int(row["losses"]) == 0:
            return "LOW_SAMPLE_ALL_WIN"
        return "INVALID_PF"

    profit_factor = float(profit_factor)

    if total_return_pct > 0.05 and profit_factor >= 1.25 and max_drawdown_pct > -0.10:
        return "PASSED"

    if total_return_pct > 0 and profit_factor >= 1.05:
        return "WEAK_PASS"

    if total_return_pct > -0.03 and profit_factor >= 0.90:
        return "NEAR_BREAKEVEN"

    return "FAILED"


def summarize_result(
    window_name: str,
    whitelist_name: str,
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
        "whitelist_name": whitelist_name,
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


def add_state_pair_to_trades(
    trades_df: pd.DataFrame,
    market_df: pd.DataFrame,
    window_name: str,
    whitelist_name: str,
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
        row["whitelist_name"] = whitelist_name
        row["state_15m_v2"] = entry_row.get("state_15m_v2", "UNKNOWN")
        row["state_1h_v2"] = entry_row.get("state_1h_v2", "UNKNOWN")
        row["state_4h_v2"] = entry_row.get("state_4h_v2", "UNKNOWN")
        row["state_pair_v2"] = (
            f"{row['state_1h_v2']} | {row['state_4h_v2']}"
        )

        rows.append(row)

    return pd.DataFrame(rows)


def validate_window(
    symbol: str,
    window_name: str,
    start_date: str,
    end_date: str,
    whitelists: dict,
) -> tuple[list[dict], pd.DataFrame]:
    data_dir = Path("data") / "regime_v2_whitelist"
    reports_dir = Path("reports") / "regime_v2_whitelist"

    data_dir.mkdir(parents=True, exist_ok=True)
    reports_dir.mkdir(parents=True, exist_ok=True)

    base_name = f"{symbol.lower()}_{window_name}"

    csv_15m = data_dir / f"{base_name}_15m.csv"
    csv_1h = data_dir / f"{base_name}_1h.csv"
    csv_4h = data_dir / f"{base_name}_4h.csv"

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

    market_df = enrich_with_regime_filter_v2(
        entry_csv_path=csv_15m,
        h1_csv_path=csv_1h,
        h4_csv_path=csv_4h,
        output_path=regime_v2_csv,
    )

    config = build_config()

    window_results = []
    window_trades = []

    for whitelist_name, allowed_pairs in whitelists.items():
        strategy_func = make_whitelist_signal(allowed_pairs)

        trades_df, summary = run_backtest_v3(
            csv_path=regime_v2_csv,
            config=config,
            output_dir=reports_dir,
            strategy_func=strategy_func,
        )

        result = summarize_result(
            window_name=window_name,
            whitelist_name=whitelist_name,
            market_return_pct=market_return_pct,
            trades_df=trades_df,
            summary=summary,
        )

        result["window_status"] = classify_window(result)
        window_results.append(result)

        trades_with_state = add_state_pair_to_trades(
            trades_df=trades_df,
            market_df=market_df,
            window_name=window_name,
            whitelist_name=whitelist_name,
        )

        if not trades_with_state.empty:
            window_trades.append(trades_with_state)

        print(
            f"{whitelist_name} | "
            f"market={market_return_pct:.2%} | "
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

    for whitelist_name, group in results_df.groupby("whitelist_name"):
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
        all_win_low_sample = int((group["window_status"] == "LOW_SAMPLE_ALL_WIN").sum())

        quality_score = (
            compound_return * 100
            + avg_pf * 8
            + passed * 5
            + weak_pass * 3
            + near_breakeven * 1
            + all_win_low_sample * 1
            - failed * 6
            + worst_drawdown * 100
        )

        if total_trades < 30:
            research_decision = "TOO_FEW_TRADES"
        elif failed >= 3:
            research_decision = "NOT_ROBUST"
        elif passed >= 2 and failed <= 1 and compound_return > 0 and avg_pf >= 1.10:
            research_decision = "PROMISING_WHITELIST"
        elif failed <= 2 and compound_return > -0.03 and avg_pf >= 0.95:
            research_decision = "FILTER_CANDIDATE"
        else:
            research_decision = "WEAK_OR_UNSTABLE"

        rows.append(
            {
                "whitelist_name": whitelist_name,
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
                "low_sample_all_win": all_win_low_sample,
                "quality_score": quality_score,
            }
        )

    aggregate_df = pd.DataFrame(rows)
    aggregate_df = aggregate_df.sort_values(by="quality_score", ascending=False)

    return aggregate_df


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

    whitelists = get_whitelists()

    print("REGIME V2 STATE WHITELIST RESEARCH")
    print("=" * 100)
    print("Entry fixed: LONG V2 candidate")
    print("Fib 0.500-0.618 + break_prev_high")
    print("Risk: ATR 1.5 | RR 2.0 | Max holding 96")
    print()

    all_results = []
    all_trades = []

    for window_name, start_date, end_date in windows:
        window_results, trades_df = validate_window(
            symbol=symbol,
            window_name=window_name,
            start_date=start_date,
            end_date=end_date,
            whitelists=whitelists,
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

    reports_dir = Path("reports") / "regime_v2_whitelist"
    reports_dir.mkdir(parents=True, exist_ok=True)

    results_output = reports_dir / "regime_v2_whitelist_window_results.csv"
    aggregate_output = reports_dir / "regime_v2_whitelist_aggregate.csv"
    trades_output = reports_dir / "regime_v2_whitelist_trade_diagnostics.csv"

    results_df.to_csv(results_output, index=False)
    aggregate_df.to_csv(aggregate_output, index=False)
    trades_all_df.to_csv(trades_output, index=False)

    print()
    print("AGGREGATE WHITELIST RESULTS")
    print("=" * 100)
    print(
        aggregate_df[
            [
                "whitelist_name",
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

    top_whitelists = aggregate_df.head(5)["whitelist_name"].tolist()

    print()
    print("BEST WHITELISTS DETAIL BY WINDOW")
    print("=" * 100)
    print(
        results_df[results_df["whitelist_name"].isin(top_whitelists)][
            [
                "window_name",
                "whitelist_name",
                "window_status",
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
        ]
        .sort_values(by=["whitelist_name", "window_name"])
        .to_string(index=False)
    )

    print()
    print("PNL BY STATE PAIR — TOP WHITELISTS")
    print("=" * 100)

    if not trades_all_df.empty:
        state_pair_df = (
            trades_all_df[trades_all_df["whitelist_name"].isin(top_whitelists)]
            .groupby(["whitelist_name", "state_1h_v2", "state_4h_v2"])
            .agg(
                trades=("entry_index", "count"),
                total_net_pnl=("net_pnl", "sum"),
                avg_net_pnl=("net_pnl", "mean"),
            )
            .reset_index()
            .sort_values(by="total_net_pnl", ascending=False)
        )

        print(state_pair_df.to_string(index=False))
    else:
        print("Sin trades.")

    print()
    print("ARCHIVOS GENERADOS")
    print("=" * 100)
    print(f"- {results_output}")
    print(f"- {aggregate_output}")
    print(f"- {trades_output}")


if __name__ == "__main__":
    main()