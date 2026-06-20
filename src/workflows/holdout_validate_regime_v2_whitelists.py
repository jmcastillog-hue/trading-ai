from pathlib import Path
import pandas as pd

from src.backtesting.backtesting_engine_v3 import run_backtest_v3
from src.market_structure.regime_filter_v2 import enrich_with_regime_filter_v2
from src.workflows.validate_long_v2_candidate_robust import (
    download_binance_klines_range,
    calculate_market_return,
)
from src.workflows.diagnose_regime_filter_v2 import build_config
from src.workflows.research_regime_v2_whitelists import (
    get_whitelists,
    make_whitelist_signal,
    summarize_result,
    classify_window,
    add_state_pair_to_trades,
)


DISCOVERY_BENCHMARKS = {
    "PRIOR_POSITIVE_PAIRS_EXPERIMENTAL": {
        "discovery_compound_return": 0.263791,
        "discovery_avg_profit_factor": 1.723640,
        "discovery_total_trades": 83,
    },
    "EXHAUSTION_REVERSAL_RESEARCH": {
        "discovery_compound_return": 0.133709,
        "discovery_avg_profit_factor": 1.554174,
        "discovery_total_trades": 47,
    },
    "CONTINUATION_EXHAUSTION": {
        "discovery_compound_return": 0.041395,
        "discovery_avg_profit_factor": 1.540952,
        "discovery_total_trades": 43,
    },
    "CORE_PLUS_EXHAUSTION": {
        "discovery_compound_return": 0.092660,
        "discovery_avg_profit_factor": 1.331554,
        "discovery_total_trades": 69,
    },
    "CONTINUATION_ONLY": {
        "discovery_compound_return": 0.026508,
        "discovery_avg_profit_factor": 1.137846,
        "discovery_total_trades": 45,
    },
    "STRICT_BULLISH_CORE": {
        "discovery_compound_return": -0.000165,
        "discovery_avg_profit_factor": 0.970978,
        "discovery_total_trades": 26,
    },
    "NO_STATE_FILTER_BASELINE": {
        "discovery_compound_return": -0.277816,
        "discovery_avg_profit_factor": 0.799583,
        "discovery_total_trades": 211,
    },
}


def select_holdout_whitelists() -> dict:
    all_whitelists = get_whitelists()

    selected_names = [
        "NO_STATE_FILTER_BASELINE",
        "STRICT_BULLISH_CORE",
        "CONTINUATION_EXHAUSTION",
        "CORE_PLUS_EXHAUSTION",
        "CONTINUATION_ONLY",
        "EXHAUSTION_REVERSAL_RESEARCH",
        "PRIOR_POSITIVE_PAIRS_EXPERIMENTAL",
    ]

    return {
        name: all_whitelists[name]
        for name in selected_names
        if name in all_whitelists
    }


def validate_window(
    symbol: str,
    window_name: str,
    start_date: str,
    end_date: str,
    whitelists: dict,
) -> tuple[list[dict], pd.DataFrame]:
    data_dir = Path("data") / "regime_v2_whitelist_holdout"
    reports_dir = Path("reports") / "regime_v2_whitelist_holdout"

    data_dir.mkdir(parents=True, exist_ok=True)
    reports_dir.mkdir(parents=True, exist_ok=True)

    base_name = f"{symbol.lower()}_{window_name}"

    csv_15m = data_dir / f"{base_name}_15m.csv"
    csv_1h = data_dir / f"{base_name}_1h.csv"
    csv_4h = data_dir / f"{base_name}_4h.csv"

    regime_v2_csv = reports_dir / f"{base_name}_regime_v2.csv"

    print()
    print(f"HOLDOUT WINDOW: {window_name}")
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
        result["start_date"] = start_date
        result["end_date"] = end_date

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


def build_holdout_aggregate(results_df: pd.DataFrame) -> pd.DataFrame:
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
        low_sample_all_win = int((group["window_status"] == "LOW_SAMPLE_ALL_WIN").sum())

        quality_score = (
            compound_return * 100
            + avg_pf * 10
            + passed * 6
            + weak_pass * 3
            + near_breakeven * 1
            + low_sample_all_win * 0.5
            - failed * 8
            - insufficient * 1
            + worst_drawdown * 100
        )

        if total_trades < 30:
            holdout_decision = "TOO_FEW_TRADES"
        elif compound_return > 0.08 and avg_pf >= 1.20 and failed <= 1:
            holdout_decision = "HOLDOUT_PASSED"
        elif compound_return > 0 and avg_pf >= 1.05 and failed <= 2:
            holdout_decision = "HOLDOUT_WEAK_PASS"
        elif compound_return > -0.03 and avg_pf >= 0.95 and failed <= 2:
            holdout_decision = "HOLDOUT_NEAR_BREAKEVEN"
        elif compound_return > 0 and avg_pf >= 1.0:
            holdout_decision = "POSITIVE_BUT_UNSTABLE"
        else:
            holdout_decision = "HOLDOUT_FAILED"

        discovery = DISCOVERY_BENCHMARKS.get(whitelist_name, {})

        discovery_compound = discovery.get("discovery_compound_return", None)
        discovery_pf = discovery.get("discovery_avg_profit_factor", None)
        discovery_trades = discovery.get("discovery_total_trades", None)

        if discovery_compound is not None:
            compound_return_decay = compound_return - discovery_compound
        else:
            compound_return_decay = None

        if discovery_pf is not None:
            pf_decay = avg_pf - discovery_pf
        else:
            pf_decay = None

        rows.append(
            {
                "whitelist_name": whitelist_name,
                "holdout_decision": holdout_decision,
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
                "low_sample_all_win": low_sample_all_win,
                "quality_score": quality_score,
                "discovery_compound_return": discovery_compound,
                "discovery_avg_profit_factor": discovery_pf,
                "discovery_total_trades": discovery_trades,
                "compound_return_decay": compound_return_decay,
                "profit_factor_decay": pf_decay,
            }
        )

    aggregate_df = pd.DataFrame(rows)
    aggregate_df = aggregate_df.sort_values(by="quality_score", ascending=False)

    return aggregate_df


def print_final_decision(aggregate_df: pd.DataFrame):
    print()
    print("FINAL HOLDOUT DECISION")
    print("=" * 100)

    if aggregate_df.empty:
        print("NO_DATA")
        return

    top = aggregate_df.iloc[0]

    print(f"Best whitelist: {top['whitelist_name']}")
    print(f"Decision: {top['holdout_decision']}")
    print(f"Compound return: {top['compound_return']:.2%}")
    print(f"Average PF: {top['avg_profit_factor']:.4f}")
    print(f"Total trades: {int(top['total_trades'])}")
    print(f"Worst drawdown: {top['worst_drawdown']:.2%}")
    print(f"Failed windows: {int(top['failed'])}")

    if top["holdout_decision"] == "HOLDOUT_PASSED":
        print()
        print("Interpretacion: la whitelist sobrevivio holdout y merece fase de estrategia oficial experimental.")
    elif top["holdout_decision"] in {"HOLDOUT_WEAK_PASS", "HOLDOUT_NEAR_BREAKEVEN"}:
        print()
        print("Interpretacion: la whitelist tiene valor, pero requiere mas filtros o diagnostico antes de estrategia oficial.")
    elif top["holdout_decision"] == "POSITIVE_BUT_UNSTABLE":
        print()
        print("Interpretacion: hay edge parcial, pero demasiado inestable para operar o formalizar.")
    else:
        print()
        print("Interpretacion: la whitelist no sobrevivio holdout. Probable sobreajuste en discovery.")


def main():
    symbol = "BTCUSDT"

    holdout_windows = [
        ("2025_01_03", "2025-01-01", "2025-03-01"),
        ("2025_03_05", "2025-03-01", "2025-05-01"),
        ("2025_05_07", "2025-05-01", "2025-07-01"),
        ("2025_07_09", "2025-07-01", "2025-09-01"),
        ("2025_09_11", "2025-09-01", "2025-11-01"),
        ("2025_11_2026_01", "2025-11-01", "2026-01-01"),
    ]

    whitelists = select_holdout_whitelists()

    print("HOLDOUT VALIDATION — REGIME V2 WHITELISTS LONG V2")
    print("=" * 100)
    print("Holdout period: 2025-01-01 to 2026-01-01")
    print("Entry fixed: LONG V2 candidate")
    print("Fib 0.500-0.618 + break_prev_high")
    print("Risk: ATR 1.5 | RR 2.0 | Max holding 96")
    print()

    all_results = []
    all_trades = []

    for window_name, start_date, end_date in holdout_windows:
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

    aggregate_df = build_holdout_aggregate(results_df)

    reports_dir = Path("reports") / "regime_v2_whitelist_holdout"
    reports_dir.mkdir(parents=True, exist_ok=True)

    results_output = reports_dir / "holdout_whitelist_window_results.csv"
    aggregate_output = reports_dir / "holdout_whitelist_aggregate.csv"
    trades_output = reports_dir / "holdout_whitelist_trade_diagnostics.csv"

    results_df.to_csv(results_output, index=False)
    aggregate_df.to_csv(aggregate_output, index=False)
    trades_all_df.to_csv(trades_output, index=False)

    print()
    print("HOLDOUT AGGREGATE RESULTS")
    print("=" * 100)
    print(
        aggregate_df[
            [
                "whitelist_name",
                "holdout_decision",
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
    print("HOLDOUT DETAIL BY WINDOW — TOP WHITELISTS")
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
    print("HOLDOUT VS DISCOVERY COMPARISON")
    print("=" * 100)
    print(
        aggregate_df[
            [
                "whitelist_name",
                "holdout_decision",
                "compound_return",
                "discovery_compound_return",
                "compound_return_decay",
                "avg_profit_factor",
                "discovery_avg_profit_factor",
                "profit_factor_decay",
                "total_trades",
                "discovery_total_trades",
            ]
        ].to_string(index=False)
    )

    print()
    print("PNL BY STATE PAIR — HOLDOUT TOP WHITELISTS")
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

    print_final_decision(aggregate_df)

    print()
    print("ARCHIVOS GENERADOS")
    print("=" * 100)
    print(f"- {results_output}")
    print(f"- {aggregate_output}")
    print(f"- {trades_output}")


if __name__ == "__main__":
    main()