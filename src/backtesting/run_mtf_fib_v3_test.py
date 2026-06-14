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

from src.backtesting.mtf_fib_backtester_v2 import (
    run_mtf_fib_short_backtest_v2
)

from src.backtesting.mtf_fib_backtester_v3 import (
    run_mtf_fib_short_backtest_v3
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

    v2 = run_mtf_fib_short_backtest_v2(
        htf_df=htf_df,
        ltf_df=ltf_df,
        min_drop_pct=5.0,
        max_impulse_bars=80,
        max_wait_bars=100,
        max_trade_bars=120,
        entry_zone_low_ratio="0.236",
        entry_zone_high_ratio="0.382",
        invalidation_ratio="0.618",
        min_upper_wick_ratio=0.35,
        left_bars=2,
        right_bars=2
    )

    v3 = run_mtf_fib_short_backtest_v3(
        htf_df=htf_df,
        ltf_df=ltf_df,
        min_drop_pct=5.0,
        max_impulse_bars=80,
        max_wait_bars=100,
        max_trade_bars=120,
        confirmation_bars=12,
        break_lookback=6,
        entry_zone_low_ratio="0.236",
        entry_zone_high_ratio="0.382",
        invalidation_ratio="0.618",
        left_bars=2,
        right_bars=2
    )

    print_report(
        "MTF FIB SHORT V1",
        v1
    )

    print_report(
        "MTF FIB SHORT V2 REJECTION",
        v2
    )

    print_report(
        "MTF FIB SHORT V3 MICRO BREAK",
        v3
    )

    os.makedirs(
        "reports",
        exist_ok=True
    )

    pd.DataFrame(
        v3["trades"]
    ).to_csv(
        "reports/mtf_fib_v3_micro_break_trades.csv",
        index=False
    )

    print(
        "\nTrades V3 guardados en: reports/mtf_fib_v3_micro_break_trades.csv"
    )


if __name__ == "__main__":
    main()