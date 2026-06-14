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

from src.backtesting.mtf_fib_backtester_v5_tp1_be import (
    run_mtf_fib_short_backtest_v5_tp1_be
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


def print_exit_reason_summary(title, trades):

    print(f"\n--- {title} EXIT REASONS ---\n")

    if len(trades) == 0:

        print("Sin trades.")
        return

    df = pd.DataFrame(trades)

    counts = df["exit_reason"].value_counts()

    for reason, count in counts.items():

        print(
            f"{reason}: {count}"
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

    v5_50_50 = run_mtf_fib_short_backtest_v5_tp1_be(
        htf_df=htf_df,
        ltf_df=ltf_df,
        min_drop_pct=5.0,
        max_impulse_bars=80,
        max_wait_bars=100,
        max_trade_bars=120,
        entry_zone_low_ratio="0.236",
        entry_zone_high_ratio="0.382",
        invalidation_ratio="0.618",
        tp1_ratio=0.50,
        tp1_close_weight=0.50,
        left_bars=2,
        right_bars=2
    )

    v5_40_50 = run_mtf_fib_short_backtest_v5_tp1_be(
        htf_df=htf_df,
        ltf_df=ltf_df,
        min_drop_pct=5.0,
        max_impulse_bars=80,
        max_wait_bars=100,
        max_trade_bars=120,
        entry_zone_low_ratio="0.236",
        entry_zone_high_ratio="0.382",
        invalidation_ratio="0.618",
        tp1_ratio=0.40,
        tp1_close_weight=0.50,
        left_bars=2,
        right_bars=2
    )

    v5_50_70 = run_mtf_fib_short_backtest_v5_tp1_be(
        htf_df=htf_df,
        ltf_df=ltf_df,
        min_drop_pct=5.0,
        max_impulse_bars=80,
        max_wait_bars=100,
        max_trade_bars=120,
        entry_zone_low_ratio="0.236",
        entry_zone_high_ratio="0.382",
        invalidation_ratio="0.618",
        tp1_ratio=0.50,
        tp1_close_weight=0.70,
        left_bars=2,
        right_bars=2
    )

    print_report(
        "MTF FIB SHORT V1",
        v1
    )

    print_report(
        "MTF FIB SHORT V5 TP1 50% CLOSE 50%",
        v5_50_50
    )

    print_report(
        "MTF FIB SHORT V5 TP1 40% CLOSE 50%",
        v5_40_50
    )

    print_report(
        "MTF FIB SHORT V5 TP1 50% CLOSE 70%",
        v5_50_70
    )

    print_exit_reason_summary(
        "V5 TP1 50 CLOSE 50",
        v5_50_50["trades"]
    )

    os.makedirs(
        "reports",
        exist_ok=True
    )

    pd.DataFrame(
        v5_50_50["trades"]
    ).to_csv(
        "reports/mtf_fib_v5_tp1_50_close_50_trades.csv",
        index=False
    )

    pd.DataFrame(
        v5_40_50["trades"]
    ).to_csv(
        "reports/mtf_fib_v5_tp1_40_close_50_trades.csv",
        index=False
    )

    pd.DataFrame(
        v5_50_70["trades"]
    ).to_csv(
        "reports/mtf_fib_v5_tp1_50_close_70_trades.csv",
        index=False
    )

    print(
        "\nTrades V5 guardados en reports/"
    )


if __name__ == "__main__":
    main()