import os
import sys
import pandas as pd

sys.path.append(
    os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            "..",
            ".."
        )
    )
)

from src.quantitative.data_loader import (
    load_csv,
    validate_data,
    clean_data
)

from src.backtesting.mtf_fib_walk_forward_v5 import (
    align_common_period,
    generate_windows,
    filter_df_by_time,
    run_config_on_period,
    calculate_net_result
)

from src.backtesting.performance_metrics import (
    generate_performance_report
)


def load_market_data(path):

    df = load_csv(path)

    validate_data(df)

    df = clean_data(df)

    return df


def build_fixed_configs():

    return {
        "v5_fixed_tp1_035_close_050": {
            "entry_zone_low_ratio": "0.236",
            "entry_zone_high_ratio": "0.382",
            "invalidation_ratio": "0.618",
            "min_drop_pct": 5.0,
            "max_impulse_bars": 80,
            "max_wait_bars": 100,
            "max_trade_bars": 120,
            "tp1_ratio": 0.35,
            "tp1_close_weight": 0.50,
            "left_bars": 2,
            "right_bars": 2
        },
        "v5_fixed_tp1_040_close_050": {
            "entry_zone_low_ratio": "0.236",
            "entry_zone_high_ratio": "0.382",
            "invalidation_ratio": "0.618",
            "min_drop_pct": 5.0,
            "max_impulse_bars": 80,
            "max_wait_bars": 100,
            "max_trade_bars": 120,
            "tp1_ratio": 0.40,
            "tp1_close_weight": 0.50,
            "left_bars": 2,
            "right_bars": 2
        }
    }


def run_fixed_config_validation(
    htf_df,
    ltf_df,
    train_months=8,
    test_months=2,
    step_months=2,
    cost_pct=0.10
):

    htf_df, ltf_df, common_start, common_end = align_common_period(
        htf_df,
        ltf_df
    )

    windows = generate_windows(
        common_start=common_start,
        common_end=common_end,
        train_months=train_months,
        test_months=test_months,
        step_months=step_months
    )

    configs = build_fixed_configs()

    summary_rows = []

    all_trades_by_config = {
        name: []
        for name in configs.keys()
    }

    for config_name, config in configs.items():

        print(
            f"\n=== VALIDANDO {config_name} ===\n",
            flush=True
        )

        for window in windows:

            print(
                f"Ventana {window['window_id']} | "
                f"TEST {window['test_start'].date()} → {window['test_end'].date()}",
                flush=True
            )

            htf_context = filter_df_by_time(
                htf_df,
                window["train_start"],
                window["test_end"]
            )

            ltf_context = filter_df_by_time(
                ltf_df,
                window["train_start"],
                window["test_end"]
            )

            test_result = run_config_on_period(
                htf_df=htf_context,
                ltf_df=ltf_context,
                config=config,
                entry_start=window["test_start"],
                entry_end=window["test_end"],
                cost_pct=cost_pct
            )

            test_perf = test_result["performance"]

            for trade in test_result["trades"]:

                trade["config_name"] = config_name
                trade["window_id"] = window["window_id"]

                all_trades_by_config[config_name].append(
                    trade
                )

            summary_rows.append({
                "config_name": config_name,
                "window_id": window["window_id"],
                "test_start": window["test_start"],
                "test_end": window["test_end"],
                "cost_pct": cost_pct,
                "total_trades": test_perf["total_trades"],
                "win_rate": test_perf["win_rate"],
                "expectancy": test_perf["expectancy"],
                "profit_factor": test_perf["profit_factor"],
                "max_drawdown": test_perf["max_drawdown"],
                "net_result": test_perf["net_result"]
            })

            print(
                f"PF: {test_perf['profit_factor']:.2f} | "
                f"EXP: {test_perf['expectancy']:.2f} | "
                f"TRADES: {test_perf['total_trades']} | "
                f"NET: {test_perf['net_result']:.2f}",
                flush=True
            )

    final_rows = []

    for config_name, trades in all_trades_by_config.items():

        final_perf = generate_performance_report(
            trades
        )

        final_perf["net_result"] = calculate_net_result(
            trades
        )

        final_rows.append({
            "config_name": config_name,
            "total_trades": final_perf["total_trades"],
            "wins": final_perf["wins"],
            "losses": final_perf["losses"],
            "win_rate": final_perf["win_rate"],
            "expectancy": final_perf["expectancy"],
            "profit_factor": final_perf["profit_factor"],
            "max_drawdown": final_perf["max_drawdown"],
            "net_result": final_perf["net_result"]
        })

    return {
        "summary": summary_rows,
        "final": final_rows,
        "trades_by_config": all_trades_by_config
    }


def print_final_report(report):

    print(
        "\n=== V5 FIXED CONFIG VALIDATION ===\n"
    )

    for row in report["final"]:

        print(
            f"--- {row['config_name']} ---"
        )

        print(
            f"total_trades: {row['total_trades']}"
        )

        print(
            f"wins: {row['wins']}"
        )

        print(
            f"losses: {row['losses']}"
        )

        print(
            f"win_rate: {row['win_rate']:.2f}"
        )

        print(
            f"expectancy: {row['expectancy']:.2f}"
        )

        print(
            f"profit_factor: {row['profit_factor']:.2f}"
        )

        print(
            f"max_drawdown: {row['max_drawdown']:.2f}"
        )

        print(
            f"net_result: {row['net_result']:.2f}"
        )

        print()


def main():

    htf_df = load_market_data(
        "data/btcusdt_4h_history.csv"
    )

    ltf_df = load_market_data(
        "data/btcusdt_30m_history.csv"
    )

    report = run_fixed_config_validation(
        htf_df=htf_df,
        ltf_df=ltf_df,
        train_months=8,
        test_months=2,
        step_months=2,
        cost_pct=0.10
    )

    os.makedirs(
        "reports",
        exist_ok=True
    )

    pd.DataFrame(
        report["summary"]
    ).to_csv(
        "reports/mtf_fib_v5_fixed_validation_summary.csv",
        index=False
    )

    pd.DataFrame(
        report["final"]
    ).to_csv(
        "reports/mtf_fib_v5_fixed_validation_final.csv",
        index=False
    )

    for config_name, trades in report["trades_by_config"].items():

        pd.DataFrame(
            trades
        ).to_csv(
            f"reports/mtf_fib_v5_fixed_validation_trades_{config_name}.csv",
            index=False
        )

    print_final_report(
        report
    )

    print(
        "Resumen guardado en: reports/mtf_fib_v5_fixed_validation_summary.csv"
    )

    print(
        "Resultado final guardado en: reports/mtf_fib_v5_fixed_validation_final.csv"
    )


if __name__ == "__main__":
    main()