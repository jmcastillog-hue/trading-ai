import os
import sys

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

from src.backtesting.mtf_fib_backtester import (
    run_mtf_fib_short_backtest
)


def load_market_data(path):

    df = load_csv(path)

    validate_data(df)

    df = clean_data(df)

    return df


def main():

    htf_df = load_market_data(
        "data/btcusdt_4h_history.csv"
    )

    ltf_df = load_market_data(
        "data/btcusdt_30m_history.csv"
    )

    report = run_mtf_fib_short_backtest(
        htf_df=htf_df,
        ltf_df=ltf_df,
        min_drop_pct=5,
        max_impulse_bars=80,
        max_wait_bars=120,
        max_trade_bars=240,
        entry_zone_low_ratio="0.236",
        entry_zone_high_ratio="0.382",
        invalidation_ratio="0.618",
        left_bars=2,
        right_bars=2
    )

    print("\n=== MTF FIB SHORT BACKTEST V1 ===\n")

    for key, value in report["performance"].items():

        if isinstance(value, float):

            print(
                f"{key}: {value:.2f}"
            )

        else:

            print(
                f"{key}: {value}"
            )


if __name__ == "__main__":
    main()