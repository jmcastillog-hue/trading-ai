from pathlib import Path

import pandas as pd

from src.execution.cost_aware_filter_v1 import (
    aggregate_cost_summaries,
    apply_cost_profile_to_trades,
    build_cost_profiles,
    summarize_cost_adjusted_trades,
)
from src.validation.walk_forward_engine_v1 import (
    build_walk_forward_candidates,
    run_candidate_backtest,
    slice_by_date,
)
from src.workflows.robust_validate_short_candidates import build_short_config
from src.workflows.validate_directional_context_filter_v3_1 import (
    short_mtf_with_directional_context_v3_1,
)
from src.workflows.validate_walk_forward_engine_v1 import (
    build_symbol_dataset,
    build_walk_forward_splits,
)


def print_section(title: str):
    print()
    print(title)
    print("=" * 100)


def get_official_candidate() -> dict:
    candidates = build_walk_forward_candidates()

    official = [
        candidate for candidate in candidates if candidate["is_official"]
    ]

    if not official:
        raise ValueError("Official candidate not found.")

    return official[0]


def validate_symbol_cost_aware(symbol: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    print_section(f"COST-AWARE SYMBOL: {symbol}")

    market_df = build_symbol_dataset(symbol)

    base_config = build_short_config()
    splits = build_walk_forward_splits()
    profiles = build_cost_profiles()
    official_candidate = get_official_candidate()

    strategy_func = short_mtf_with_directional_context_v3_1

    summary_rows = []
    adjusted_trade_rows = []

    for split in splits:
        print()
        print(f"Split: {split['split_name']}")

        test_df = slice_by_date(
            market_df,
            split["test_start"],
            split["test_end"],
        )

        trades_df, raw_summary = run_candidate_backtest(
            df=test_df,
            strategy_func=strategy_func,
            base_config=base_config,
            candidate=official_candidate,
        )

        raw_trades = int(raw_summary.get("total_trades", 0))
        raw_return = float(raw_summary.get("total_return_pct", 0.0))
        raw_pf = raw_summary.get("profit_factor", None)
        raw_exp_r = float(raw_summary.get("expectancy_r", 0.0))
        raw_dd = float(raw_summary.get("max_drawdown_pct", 0.0))

        print(
            f"RAW_OFFICIAL | trades={raw_trades} | "
            f"return={raw_return:.2%} | pf={raw_pf} | "
            f"expR={raw_exp_r:.4f} | dd={raw_dd:.2%}"
        )

        for profile in profiles:
            adjusted_df = apply_cost_profile_to_trades(
                trades_df=trades_df,
                profile=profile,
            )

            adjusted_summary = summarize_cost_adjusted_trades(
                adjusted_trades_df=adjusted_df,
                profile=profile,
            )

            row = {
                "symbol": symbol,
                "split_name": split["split_name"],
                "test_start": split["test_start"],
                "test_end": split["test_end"],
                "raw_trades": raw_trades,
                "raw_return": raw_return,
                "raw_profit_factor": raw_pf,
                "raw_expectancy_r": raw_exp_r,
                "raw_drawdown": raw_dd,
                **adjusted_summary,
            }

            summary_rows.append(row)

            if not adjusted_df.empty:
                adjusted_df["symbol"] = symbol
                adjusted_df["split_name"] = split["split_name"]
                adjusted_df["test_start"] = split["test_start"]
                adjusted_df["test_end"] = split["test_end"]
                adjusted_trade_rows.append(adjusted_df)

            print(
                f"{profile.name} | "
                f"trades={adjusted_summary['total_trades']} | "
                f"return={adjusted_summary['compound_return']:.2%} | "
                f"pf={adjusted_summary['profit_factor']:.4f} | "
                f"expR={adjusted_summary['expectancy_r']:.4f} | "
                f"costR={adjusted_summary['avg_cost_r']:.4f} | "
                f"dd={adjusted_summary['max_drawdown']:.2%} | "
                f"decision={adjusted_summary['cost_decision']}"
            )

    summary_df = pd.DataFrame(summary_rows)

    if adjusted_trade_rows:
        trades_all_df = pd.concat(adjusted_trade_rows, ignore_index=True)
    else:
        trades_all_df = pd.DataFrame()

    return summary_df, trades_all_df


def main():
    print("COST-AWARE VALIDATION FILTER V1")
    print("=" * 100)
    print("Target: TARGET_SHORT_FIB_V5_MTF_V3_1 + FIXED_RR_2_5")
    print("Purpose: stress test official fixed strategy under platform cost profiles")
    print()

    symbols = [
        "BTCUSDT",
        "ETHUSDT",
        "SOLUSDT",
    ]

    all_summary = []
    all_trades = []
    errors = []

    for symbol in symbols:
        try:
            summary_df, trades_df = validate_symbol_cost_aware(symbol)

            all_summary.append(summary_df)

            if not trades_df.empty:
                all_trades.append(trades_df)

        except Exception as exc:
            error_row = {
                "symbol": symbol,
                "error": repr(exc),
            }

            errors.append(error_row)

            print_section("ERROR")
            print(error_row)

    if all_summary:
        summary_all_df = pd.concat(all_summary, ignore_index=True)
    else:
        summary_all_df = pd.DataFrame()

    if all_trades:
        trades_all_df = pd.concat(all_trades, ignore_index=True)
    else:
        trades_all_df = pd.DataFrame()

    errors_df = pd.DataFrame(errors)

    aggregate_df = aggregate_cost_summaries(summary_all_df)

    symbol_profile_df = (
        summary_all_df.groupby(["symbol", "cost_profile"])
        .agg(
            platform=("platform", "first"),
            execution_mode=("execution_mode", "first"),
            windows=("split_name", "count"),
            total_trades=("total_trades", "sum"),
            compound_return=("compound_return", lambda x: float((1 + x).prod() - 1)),
            avg_profit_factor=("profit_factor", "mean"),
            avg_expectancy_r=("expectancy_r", "mean"),
            avg_cost_r=("avg_cost_r", "mean"),
            worst_drawdown=("max_drawdown", "min"),
            positive_window_rate=("compound_return", lambda x: float((x > 0).mean())),
        )
        .reset_index()
        if not summary_all_df.empty
        else pd.DataFrame()
    )

    reports_dir = Path("reports") / "cost_aware_filter_v1"
    reports_dir.mkdir(parents=True, exist_ok=True)

    summary_output = reports_dir / "cost_aware_v1_window_summary.csv"
    aggregate_output = reports_dir / "cost_aware_v1_aggregate_summary.csv"
    symbol_output = reports_dir / "cost_aware_v1_symbol_profile_summary.csv"
    trades_output = reports_dir / "cost_aware_v1_adjusted_trades.csv"
    errors_output = reports_dir / "cost_aware_v1_errors.csv"

    summary_all_df.to_csv(summary_output, index=False)
    aggregate_df.to_csv(aggregate_output, index=False)
    symbol_profile_df.to_csv(symbol_output, index=False)
    trades_all_df.to_csv(trades_output, index=False)
    errors_df.to_csv(errors_output, index=False)

    print_section("COST-AWARE V1 AGGREGATE SUMMARY")
    if aggregate_df.empty:
        print("Sin resultados.")
    else:
        print(aggregate_df.to_string(index=False))

    print_section("COST-AWARE V1 BY SYMBOL / PROFILE")
    if symbol_profile_df.empty:
        print("Sin resultados.")
    else:
        print(symbol_profile_df.to_string(index=False))

    print_section("COST-AWARE V1 ERRORS")
    if errors_df.empty:
        print("Sin errores.")
    else:
        print(errors_df.to_string(index=False))

    print()
    print("ARCHIVOS GENERADOS")
    print("=" * 100)
    print(f"- {summary_output}")
    print(f"- {aggregate_output}")
    print(f"- {symbol_output}")
    print(f"- {trades_output}")
    print(f"- {errors_output}")


if __name__ == "__main__":
    main()