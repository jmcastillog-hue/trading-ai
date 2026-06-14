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

from src.backtesting.mtf_fib_backtester import (
    run_mtf_fib_short_backtest
)

from src.backtesting.mtf_fib_backtester_v4_partial import (
    run_mtf_fib_short_backtest_v4_partial
)


def load_market_data(path):

    df = load_csv(path)

    validate_data(df)

    df = clean_data(df)

    return df


def print_report(title, report):

    print(f"\n=== {title} ===\n")

    for key, value in report["performance"].items():

        if isinstance(value, float):

            print(
                f"{key}: {value:.2f}"
            )

        else:

            print(
                f"{key}: {value}"
            )


def main():

    htf_df = load_market_data(
        "data/btcusdt_4h_history.csv"
    )

    ltf_df = load_market_data(
        "data/btcusdt_30m_history.csv"
    )

    v1 = run_mtf_fib_short_backtest(
        htf_df=htf_df,
        ltf_df=ltf_df,
        min_drop_pct=5.0,
        max_impulse_bars=80,
        max_wait_bars=100,
        max_trade_bars=120,
        entry_zone_low_ratio="0.236",
        entry_zone_high_ratio="0.382",
        invalidation_ratio="0.618",
        left_bars=2,
        right_bars=2
    )

    v4_partial_786 = run_mtf_fib_short_backtest_v4_partial(
        htf_df=htf_df,
        ltf_df=ltf_df,
        min_drop_pct=5.0,
        max_impulse_bars=80,
        max_wait_bars=120,
        max_trade_bars=160,
        invalidation_ratio="0.786",
        require_bearish_candle=True,
        left_bars=2,
        right_bars=2
    )

    v4_partial_1000 = run_mtf_fib_short_backtest_v4_partial(
        htf_df=htf_df,
        ltf_df=ltf_df,
        min_drop_pct=5.0,
        max_impulse_bars=80,
        max_wait_bars=120,
        max_trade_bars=160,
        invalidation_ratio="1.000",
        require_bearish_candle=True,
        left_bars=2,
        right_bars=2
    )

    print_report(
        "MTF FIB SHORT V1",
        v1
    )

    print_report(
        "MTF FIB SHORT V4 PARTIAL STOP 0.786",
        v4_partial_786
    )

    print_report(
        "MTF FIB SHORT V4 PARTIAL STOP 1.000",
        v4_partial_1000
    )

    os.makedirs(
        "reports",
        exist_ok=True
    )

    pd.DataFrame(
        v4_partial_786["trades"]
    ).to_csv(
        "reports/mtf_fib_v4_partial_0786_trades.csv",
        index=False
    )

    pd.DataFrame(
        v4_partial_1000["trades"]
    ).to_csv(
        "reports/mtf_fib_v4_partial_1000_trades.csv",
        index=False
    )

    print(
        "\nTrades V4 guardados en reports/"
    )


if __name__ == "__main__":
    main()