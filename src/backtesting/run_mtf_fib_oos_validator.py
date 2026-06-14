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

from src.backtesting.mtf_fib_oos_validator import (
    run_oos_validation
)


def load_market_data(path):

    df = load_csv(path)

    validate_data(df)

    df = clean_data(df)

    return df


def print_summary(summary_rows):

    print("\n=== MTF FIB OUT-OF-SAMPLE VALIDATION ===\n")

    for row in summary_rows:

        print(
            f"--- {row['config_name']} | {row['period']} ---"
        )

        print(
            f"zone: {row['zone']}"
        )

        print(
            f"invalidation: {row['invalidation']}"
        )

        print(
            f"min_drop_pct: {row['min_drop_pct']}"
        )

        print(
            f"max_impulse_bars: {row['max_impulse_bars']}"
        )

        print(
            f"max_wait_bars: {row['max_wait_bars']}"
        )

        print(
            f"max_trade_bars: {row['max_trade_bars']}"
        )

        print(
            f"total_trades: {row['total_trades']}"
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

        print()


def main():

    htf_df = load_market_data(
        "data/btcusdt_4h_history.csv"
    )

    ltf_df = load_market_data(
        "data/btcusdt_30m_history.csv"
    )

    report = run_oos_validation(
        htf_df=htf_df,
        ltf_df=ltf_df,
        split_date="2026-01-01"
    )

    os.makedirs(
        "reports",
        exist_ok=True
    )

    summary_df = pd.DataFrame(
        report["summary"]
    )

    summary_df.to_csv(
        "reports/mtf_fib_oos_summary.csv",
        index=False
    )

    for name, trades in report["trades"].items():

        trades_df = pd.DataFrame(
            trades
        )

        trades_df.to_csv(
            f"reports/mtf_fib_oos_trades_{name}.csv",
            index=False
        )

    print_summary(
        report["summary"]
    )

    print(
        "Resumen guardado en: reports/mtf_fib_oos_summary.csv"
    )

    print(
        "Trades guardados en: reports/mtf_fib_oos_trades_*.csv"
    )


if __name__ == "__main__":
    main()