from pathlib import Path
import pandas as pd

from src.backtesting.backtesting_engine_v3 import BacktestConfig, run_backtest_v3
from src.market_structure.mtf_regime_filter import enrich_15m_with_mtf_regime
from src.strategies.fib_v5_mtf_strategy import fib_v5_short_with_mtf_filter
from src.strategies.fib_v5_mtf_liquidity_v2_strategy import (
    fib_v5_short_with_mtf_and_liquidity_v2_filter,
)
from src.workflows.validate_long_v2_candidate_robust import (
    download_binance_klines_range,
    calculate_market_return,
)


def build_short_config() -> BacktestConfig:
    """
    SHORT FIB V5 candidate config based on prior best research.

    Fase 1.1 / 1.7 base:
    - ATR multiplier: 1.25
    - Risk reward: 2.5
    - Direction: short_only
    """

    return BacktestConfig(
        initial_capital=1000.0,
        risk_per_trade=0.01,
        risk_reward=2.5,
        fee_rate=0.001,
        spread_rate=0.0002,
        atr_period=14,
        atr_multiplier=1.25,
        max_holding_bars=48,
        direction_mode="short_only",
    )


def classify_market_window(market_return_pct: float) -> str:
    if market_return_pct >= 0.10:
        return "BULLISH_MARKET"

    if market_return_pct <= -0.10:
        return "BEARISH_MARKET"

    if market_return_pct >= 0.03:
        return "MILD_BULLISH_MARKET"

    if market_return_pct <= -0.03:
        return "MILD_BEARISH_MARKET"

    return "RANGE_MARKET"


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

    if total_return_pct > 0.08 and profit_factor >= 1.30 and max_drawdown_pct > -0.10:
        return "PASSED"

    if total_return_pct > 0.03 and profit_factor >= 1.15:
        return "WEAK_PASS"

    if total_return_pct > -0.03 and profit_factor >= 0.90:
        return "NEAR_BREAKEVEN"

    return "FAILED"


def summarize_strategy(
    window_name: str,
    start_date: str,
    end_date: str,
    strategy_name: str,
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
        "start_date": start_date,
        "end_date": end_date,
        "strategy_name": strategy_name,
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
        row["regime_1h"] = entry_row.get("regime_1h", "UNKNOWN")
        row["regime_4h"] = entry_row.get("regime_4h", "UNKNOWN")
        row["regime_pair"] = f"{row['regime_1h']} | {row['regime_4h']}"

        rows.append(row)

    return pd.DataFrame(rows)


def validate_window(
    symbol: str,
    window_name: str,
    start_date: str,
    end_date: str,
) -> tuple[list[dict], pd.DataFrame]:
    data_dir = Path("data") / "short_robust_validation"
    reports_dir = Path("reports") / "short_robust_validation"

    data_dir.mkdir(parents=True, exist_ok=True)
    reports_dir.mkdir(parents=True, exist_ok=True)

    base_name = f"{symbol.lower()}_{window_name}"

    csv_15m = data_dir / f"{base_name}_15m.csv"
    csv_1h = data_dir / f"{base_name}_1h.csv"
    csv_4h = data_dir / f"{base_name}_4h.csv"

    enriched_csv = reports_dir / f"{base_name}_15m_with_mtf.csv"

    print()
    print(f"SHORT ROBUST WINDOW: {window_name}")
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

    config = build_short_config()

    strategies = [
        ("SHORT_FIB_V5_MTF", fib_v5_short_with_mtf_filter),
        (
            "SHORT_FIB_V5_MTF_LIQUIDITY_V2",
            fib_v5_short_with_mtf_and_liquidity_v2_filter,
        ),
    ]

    window_results = []
    window_trades = []

    for strategy_name, strategy_func in strategies:
        trades_df, summary = run_backtest_v3(
            csv_path=enriched_csv,
            config=config,
            output_dir=reports_dir,
            strategy_func=strategy_func,
        )

        result = summarize_strategy(
            window_name=window_name,
            start_date=start_date,
            end_date=end_date,
            strategy_name=strategy_name,
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
        )

        if not trades_with_context.empty:
            window_trades.append(trades_with_context)

        print(
            f"{strategy_name} | "
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


def print_final_decision(aggregate_df: pd.DataFrame):
    print()
    print("FINAL SHORT ROBUST DECISION")
    print("=" * 100)

    if aggregate_df.empty:
        print("NO_DATA")
        return

    top = aggregate_df.iloc[0]

    print(f"Best strategy: {top['strategy_name']}")
    print(f"Decision: {top['research_decision']}")
    print(f"Compound return: {top['compound_return']:.2%}")
    print(f"Average PF: {top['avg_profit_factor']:.4f}")
    print(f"Total trades: {int(top['total_trades'])}")
    print(f"Worst drawdown: {top['worst_drawdown']:.2%}")
    print(f"Failed windows: {int(top['failed'])}")

    if top["research_decision"] == "ROBUST_CANDIDATE":
        print()
        print("Interpretacion: candidato SHORT merece siguiente fase de refinamiento o paper trading controlado.")
    elif top["research_decision"] == "WEAK_CANDIDATE":
        print()
        print("Interpretacion: candidato SHORT tiene valor, pero requiere filtros adicionales.")
    elif top["research_decision"] == "NEAR_BREAKEVEN":
        print()
        print("Interpretacion: candidato SHORT reduce daño, pero no tiene ventaja suficiente.")
    else:
        print()
        print("Interpretacion: candidato SHORT no sobrevive validacion robusta.")


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

    print("ROBUST VALIDATION — SHORT CANDIDATES")
    print("=" * 100)
    print("Candidates:")
    print("- SHORT_FIB_V5_MTF")
    print("- SHORT_FIB_V5_MTF_LIQUIDITY_V2")
    print("Config: ATR 1.25 | RR 2.5 | Max holding 48 | short_only")
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

    reports_dir = Path("reports") / "short_robust_validation"
    reports_dir.mkdir(parents=True, exist_ok=True)

    results_output = reports_dir / "short_candidates_window_results.csv"
    aggregate_output = reports_dir / "short_candidates_aggregate.csv"
    trades_output = reports_dir / "short_candidates_trade_diagnostics.csv"

    results_df.to_csv(results_output, index=False)
    aggregate_df.to_csv(aggregate_output, index=False)
    trades_all_df.to_csv(trades_output, index=False)

    print()
    print("SHORT CANDIDATES AGGREGATE RESULTS")
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
    print("SHORT CANDIDATES DETAIL BY WINDOW")
    print("=" * 100)
    print(
        results_df[
            [
                "window_name",
                "strategy_name",
                "market_window_type",
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
                "avg_holding_bars",
            ]
        ]
        .sort_values(by=["strategy_name", "window_name"])
        .to_string(index=False)
    )

    print()
    print("SHORT PERFORMANCE BY MARKET TYPE")
    print("=" * 100)
    market_type_df = (
        results_df.groupby(["strategy_name", "market_window_type"])
        .agg(
            windows=("window_name", "count"),
            total_trades=("total_trades", "sum"),
            avg_strategy_return=("total_return_pct", "mean"),
            avg_market_return=("market_return_pct", "mean"),
            avg_profit_factor=("profit_factor", "mean"),
            worst_drawdown=("max_drawdown_pct", "min"),
        )
        .reset_index()
        .sort_values(by=["strategy_name", "avg_strategy_return"], ascending=[True, False])
    )

    print(market_type_df.to_string(index=False))

    print()
    print("SHORT PNL BY OLD MTF REGIME PAIR")
    print("=" * 100)

    if not trades_all_df.empty:
        regime_pair_df = (
            trades_all_df.groupby(["strategy_name", "regime_pair"])
            .agg(
                trades=("entry_index", "count"),
                total_net_pnl=("net_pnl", "sum"),
                avg_net_pnl=("net_pnl", "mean"),
            )
            .reset_index()
            .sort_values(by="total_net_pnl", ascending=False)
        )

        print(regime_pair_df.to_string(index=False))
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