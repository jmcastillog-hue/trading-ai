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
    run_walk_forward_validation_v5
)


def load_market_data(path):

    df = load_csv(path)

    validate_data(df)

    df = clean_data(df)

    return df


def print_final_report(report):

    print("\n=== MTF FIB WALK FORWARD V5 VALIDATION ===\n")

    final = report["final_performance"]

    print("Resultado combinado de todos los periodos TEST:\n")

    for key, value in final.items():

        if isinstance(value, float):

            print(
                f"{key}: {value:.2f}"
            )

        else:

            print(
                f"{key}: {value}"
            )

    print("\nResumen por ventana:\n")

    for row in report["summary"]:

        print(
            f"Ventana {row['window_id']} | "
            f"TEST {row['test_start'].date()} → {row['test_end'].date()}"
        )

        print(
            f"config: {row['config']}"
        )

        print(
            f"train_pf: {row['train_profit_factor']:.2f} | "
            f"test_pf: {row['test_profit_factor']:.2f}"
        )

        print(
            f"train_exp: {row['train_expectancy']:.2f} | "
            f"test_exp: {row['test_expectancy']:.2f}"
        )

        print(
            f"test_trades: {row['test_trades']} | "
            f"test_net: {row['test_net_result']:.2f}"
        )

        print()


def main():

    htf_df = load_market_data(
        "data/btcusdt_4h_history.csv"
    )

    ltf_df = load_market_data(
        "data/btcusdt_30m_history.csv"
    )

    report = run_walk_forward_validation_v5(
        htf_df=htf_df,
        ltf_df=ltf_df,
        train_months=8,
        test_months=2,
        step_months=2,
        cost_pct=0.10,
        min_train_trades=6
    )

    os.makedirs(
        "reports",
        exist_ok=True
    )

    summary_df = pd.DataFrame(
        report["summary"]
    )

    trades_df = pd.DataFrame(
        report["test_trades"]
    )

    summary_df.to_csv(
        "reports/mtf_fib_walk_forward_v5_summary.csv",
        index=False
    )

    trades_df.to_csv(
        "reports/mtf_fib_walk_forward_v5_test_trades.csv",
        index=False
    )

    print_final_report(
        report
    )

    print(
        "Resumen guardado en: reports/mtf_fib_walk_forward_v5_summary.csv"
    )

    print(
        "Trades TEST guardados en: reports/mtf_fib_walk_forward_v5_test_trades.csv"
    )


if __name__ == "__main__":
    main()