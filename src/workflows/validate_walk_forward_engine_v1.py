from pathlib import Path

import pandas as pd

from src.validation.walk_forward_engine_v1 import (
    build_walk_forward_candidates,
    run_candidate_backtest,
    select_best_candidate,
    slice_by_date,
    summarize_selected_candidates,
    summarize_walk_forward_tests,
)
from src.workflows.robust_validate_short_candidates import build_short_config
from src.workflows.validate_directional_context_filter_v3_1 import (
    build_combined_context_dataset_v3_1,
    short_mtf_with_directional_context_v3_1,
)
from src.workflows.validate_long_v2_candidate_robust import (
    download_binance_klines_range,
)


def print_section(title: str):
    print()
    print(title)
    print("=" * 100)


def build_walk_forward_splits() -> list[dict]:
    return [
        {
            "split_name": "WF_2022Q1_2022Q4_TO_2023Q1",
            "train_start": "2022-01-01",
            "train_end": "2023-01-01",
            "test_start": "2023-01-01",
            "test_end": "2023-04-01",
        },
        {
            "split_name": "WF_2022Q2_2023Q1_TO_2023Q2",
            "train_start": "2022-04-01",
            "train_end": "2023-04-01",
            "test_start": "2023-04-01",
            "test_end": "2023-07-01",
        },
        {
            "split_name": "WF_2022Q3_2023Q2_TO_2023Q3",
            "train_start": "2022-07-01",
            "train_end": "2023-07-01",
            "test_start": "2023-07-01",
            "test_end": "2023-10-01",
        },
        {
            "split_name": "WF_2022Q4_2023Q3_TO_2023Q4",
            "train_start": "2022-10-01",
            "train_end": "2023-10-01",
            "test_start": "2023-10-01",
            "test_end": "2024-01-01",
        },
        {
            "split_name": "WF_2023Q1_2023Q4_TO_2024Q1",
            "train_start": "2023-01-01",
            "train_end": "2024-01-01",
            "test_start": "2024-01-01",
            "test_end": "2024-04-01",
        },
        {
            "split_name": "WF_2023Q2_2024Q1_TO_2024Q2",
            "train_start": "2023-04-01",
            "train_end": "2024-04-01",
            "test_start": "2024-04-01",
            "test_end": "2024-07-01",
        },
        {
            "split_name": "WF_2023Q3_2024Q2_TO_2024Q3",
            "train_start": "2023-07-01",
            "train_end": "2024-07-01",
            "test_start": "2024-07-01",
            "test_end": "2024-10-01",
        },
        {
            "split_name": "WF_2023Q4_2024Q3_TO_2024Q4",
            "train_start": "2023-10-01",
            "train_end": "2024-10-01",
            "test_start": "2024-10-01",
            "test_end": "2025-01-01",
        },
        {
            "split_name": "WF_2024Q1_2024Q4_TO_2025Q1",
            "train_start": "2024-01-01",
            "train_end": "2025-01-01",
            "test_start": "2025-01-01",
            "test_end": "2025-04-01",
        },
        {
            "split_name": "WF_2024Q2_2025Q1_TO_2025Q2",
            "train_start": "2024-04-01",
            "train_end": "2025-04-01",
            "test_start": "2025-04-01",
            "test_end": "2025-07-01",
        },
        {
            "split_name": "WF_2024Q3_2025Q2_TO_2025Q3",
            "train_start": "2024-07-01",
            "train_end": "2025-07-01",
            "test_start": "2025-07-01",
            "test_end": "2025-10-01",
        },
        {
            "split_name": "WF_2024Q4_2025Q3_TO_2025Q4",
            "train_start": "2024-10-01",
            "train_end": "2025-10-01",
            "test_start": "2025-10-01",
            "test_end": "2026-01-01",
        },
    ]


def build_symbol_dataset(symbol: str) -> pd.DataFrame:
    data_dir = Path("data") / "walk_forward_engine_v1"
    reports_dir = Path("reports") / "walk_forward_engine_v1"

    data_dir.mkdir(parents=True, exist_ok=True)
    reports_dir.mkdir(parents=True, exist_ok=True)

    base_name = f"{symbol.lower()}_2022_2025"

    csv_15m = data_dir / f"{base_name}_15m.csv"
    csv_1h = data_dir / f"{base_name}_1h.csv"
    csv_4h = data_dir / f"{base_name}_4h.csv"

    enriched_csv = reports_dir / f"{base_name}_v3_1_context.csv"

    if not csv_15m.exists():
        download_binance_klines_range(
            symbol,
            "15m",
            "2022-01-01",
            "2026-01-01",
            csv_15m,
        )

    if not csv_1h.exists():
        download_binance_klines_range(
            symbol,
            "1h",
            "2022-01-01",
            "2026-01-01",
            csv_1h,
        )

    if not csv_4h.exists():
        download_binance_klines_range(
            symbol,
            "4h",
            "2022-01-01",
            "2026-01-01",
            csv_4h,
        )

    market_df = build_combined_context_dataset_v3_1(
        csv_15m=csv_15m,
        csv_1h=csv_1h,
        csv_4h=csv_4h,
        enriched_csv=enriched_csv,
        reports_dir=reports_dir,
        base_name=base_name,
    )

    return market_df


def validate_symbol_walk_forward(symbol: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    print_section(f"WALK FORWARD SYMBOL: {symbol}")

    market_df = build_symbol_dataset(symbol)

    candidates = build_walk_forward_candidates()
    base_config = build_short_config()
    splits = build_walk_forward_splits()

    strategy_func = short_mtf_with_directional_context_v3_1

    results = []
    training_rows = []

    official_candidate = [
        candidate for candidate in candidates if candidate["is_official"]
    ][0]

    for split in splits:
        print()
        print(f"Split: {split['split_name']}")

        train_df = slice_by_date(
            market_df,
            split["train_start"],
            split["train_end"],
        )

        test_df = slice_by_date(
            market_df,
            split["test_start"],
            split["test_end"],
        )

        selected_candidate, train_detail_df = select_best_candidate(
            train_df=train_df,
            strategy_func=strategy_func,
            base_config=base_config,
            candidates=candidates,
        )

        train_detail_df["symbol"] = symbol
        train_detail_df["split_name"] = split["split_name"]
        train_detail_df["train_start"] = split["train_start"]
        train_detail_df["train_end"] = split["train_end"]
        train_detail_df["test_start"] = split["test_start"]
        train_detail_df["test_end"] = split["test_end"]

        training_rows.append(train_detail_df)

        for evaluation_mode, candidate in [
            ("WALK_FORWARD_SELECTED", selected_candidate),
            ("OFFICIAL_FIXED", official_candidate),
        ]:
            _, test_summary = run_candidate_backtest(
                df=test_df,
                strategy_func=strategy_func,
                base_config=base_config,
                candidate=candidate,
            )

            row = {
                "symbol": symbol,
                "split_name": split["split_name"],
                "train_start": split["train_start"],
                "train_end": split["train_end"],
                "test_start": split["test_start"],
                "test_end": split["test_end"],
                "evaluation_mode": evaluation_mode,
                "selected_candidate_name": candidate["candidate_name"],
                "risk_reward": candidate["risk_reward"],
                "atr_multiplier": candidate["atr_multiplier"],
                "max_holding_bars": candidate["max_holding_bars"],
                "test_trades": int(test_summary.get("total_trades", 0)),
                "test_return": float(test_summary.get("total_return_pct", 0.0)),
                "test_profit_factor": test_summary.get("profit_factor", None),
                "test_expectancy_r": float(test_summary.get("expectancy_r", 0.0)),
                "test_drawdown": float(test_summary.get("max_drawdown_pct", 0.0)),
                "test_win_rate": float(test_summary.get("win_rate", 0.0)),
            }

            results.append(row)

            print(
                f"{evaluation_mode} | "
                f"candidate={candidate['candidate_name']} | "
                f"trades={row['test_trades']} | "
                f"return={row['test_return']:.2%} | "
                f"pf={row['test_profit_factor']} | "
                f"expR={row['test_expectancy_r']:.4f} | "
                f"dd={row['test_drawdown']:.2%}"
            )

    results_df = pd.DataFrame(results)
    training_df = pd.concat(training_rows, ignore_index=True)

    return results_df, training_df


def main():
    print("WALK FORWARD VALIDATION ENGINE V1")
    print("=" * 100)
    print("Target: TARGET_SHORT_FIB_V5_MTF_V3_1")
    print("Purpose: compare rolling selected params vs official fixed params")
    print()

    symbols = [
        "BTCUSDT",
        "ETHUSDT",
        "SOLUSDT",
    ]

    all_results = []
    all_training = []
    errors = []

    for symbol in symbols:
        try:
            results_df, training_df = validate_symbol_walk_forward(symbol)

            all_results.append(results_df)
            all_training.append(training_df)

        except Exception as exc:
            error_row = {
                "symbol": symbol,
                "error": repr(exc),
            }

            errors.append(error_row)

            print_section("ERROR")
            print(error_row)

    if all_results:
        results_all_df = pd.concat(all_results, ignore_index=True)
    else:
        results_all_df = pd.DataFrame()

    if all_training:
        training_all_df = pd.concat(all_training, ignore_index=True)
    else:
        training_all_df = pd.DataFrame()

    errors_df = pd.DataFrame(errors)

    summary_df = summarize_walk_forward_tests(results_all_df)
    selected_summary_df = summarize_selected_candidates(results_all_df)

    symbol_summary_df = (
        results_all_df.groupby(["symbol", "evaluation_mode"])
        .agg(
            test_windows=("split_name", "count"),
            total_test_trades=("test_trades", "sum"),
            compound_test_return=("test_return", lambda x: float((1 + x).prod() - 1)),
            avg_test_profit_factor=("test_profit_factor", "mean"),
            avg_test_expectancy_r=("test_expectancy_r", "mean"),
            worst_test_drawdown=("test_drawdown", "min"),
            positive_test_rate=("test_return", lambda x: float((x > 0).mean())),
        )
        .reset_index()
        if not results_all_df.empty
        else pd.DataFrame()
    )

    reports_dir = Path("reports") / "walk_forward_engine_v1"
    reports_dir.mkdir(parents=True, exist_ok=True)

    results_output = reports_dir / "walk_forward_v1_results.csv"
    training_output = reports_dir / "walk_forward_v1_training_candidates.csv"
    summary_output = reports_dir / "walk_forward_v1_summary.csv"
    selected_output = reports_dir / "walk_forward_v1_selected_candidates.csv"
    symbol_output = reports_dir / "walk_forward_v1_symbol_summary.csv"
    errors_output = reports_dir / "walk_forward_v1_errors.csv"

    results_all_df.to_csv(results_output, index=False)
    training_all_df.to_csv(training_output, index=False)
    summary_df.to_csv(summary_output, index=False)
    selected_summary_df.to_csv(selected_output, index=False)
    symbol_summary_df.to_csv(symbol_output, index=False)
    errors_df.to_csv(errors_output, index=False)

    print_section("WALK FORWARD V1 SUMMARY")
    if summary_df.empty:
        print("Sin resultados.")
    else:
        print(summary_df.to_string(index=False))

    print_section("WALK FORWARD V1 BY SYMBOL")
    if symbol_summary_df.empty:
        print("Sin resultados.")
    else:
        print(symbol_summary_df.to_string(index=False))

    print_section("SELECTED PARAMETER SUMMARY")
    if selected_summary_df.empty:
        print("Sin candidatos seleccionados.")
    else:
        print(selected_summary_df.to_string(index=False))

    print_section("TRAINING PARAMETER TOP 30")
    if training_all_df.empty:
        print("Sin entrenamiento.")
    else:
        top_train = training_all_df.sort_values(
            by="selection_score",
            ascending=False,
        ).head(30)

        print(
            top_train[
                [
                    "symbol",
                    "split_name",
                    "candidate_name",
                    "train_trades",
                    "train_return",
                    "train_profit_factor",
                    "train_expectancy_r",
                    "train_drawdown",
                    "selection_score",
                ]
            ].to_string(index=False)
        )

    print_section("WALK FORWARD V1 ERRORS")
    if errors_df.empty:
        print("Sin errores.")
    else:
        print(errors_df.to_string(index=False))

    print()
    print("ARCHIVOS GENERADOS")
    print("=" * 100)
    print(f"- {results_output}")
    print(f"- {training_output}")
    print(f"- {summary_output}")
    print(f"- {selected_output}")
    print(f"- {symbol_output}")
    print(f"- {errors_output}")


if __name__ == "__main__":
    main()