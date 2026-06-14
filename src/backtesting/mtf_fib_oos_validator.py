import os
import sys
import pandas as pd

sys.path.append(
    os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            ".."
        )
    )
)

from backtesting.mtf_fib_backtester import (
    run_mtf_fib_short_backtest
)


def align_dataframes_by_common_start(
    htf_df,
    ltf_df
):

    common_start = max(
        htf_df["timestamp"].min(),
        ltf_df["timestamp"].min()
    )

    htf_df = htf_df[
        htf_df["timestamp"] >= common_start
    ].copy()

    ltf_df = ltf_df[
        ltf_df["timestamp"] >= common_start
    ].copy()

    return htf_df, ltf_df, common_start


def split_train_test(
    df,
    split_date
):

    split_timestamp = pd.to_datetime(
        split_date
    )

    train_df = df[
        df["timestamp"] < split_timestamp
    ].copy()

    test_df = df[
        df["timestamp"] >= split_timestamp
    ].copy()

    return train_df, test_df


def run_single_config_validation(
    config_name,
    htf_df,
    ltf_df,
    config
):

    report = run_mtf_fib_short_backtest(
        htf_df=htf_df,
        ltf_df=ltf_df,
        min_drop_pct=config["min_drop_pct"],
        max_impulse_bars=config["max_impulse_bars"],
        max_wait_bars=config["max_wait_bars"],
        max_trade_bars=config["max_trade_bars"],
        entry_zone_low_ratio=config["entry_zone_low_ratio"],
        entry_zone_high_ratio=config["entry_zone_high_ratio"],
        invalidation_ratio=config["invalidation_ratio"],
        left_bars=config["left_bars"],
        right_bars=config["right_bars"]
    )

    performance = report["performance"]

    summary = {
        "config_name": config_name,
        "zone": (
            f"{config['entry_zone_low_ratio']}-"
            f"{config['entry_zone_high_ratio']}"
        ),
        "invalidation": config["invalidation_ratio"],
        "min_drop_pct": config["min_drop_pct"],
        "max_impulse_bars": config["max_impulse_bars"],
        "max_wait_bars": config["max_wait_bars"],
        "max_trade_bars": config["max_trade_bars"],
        "total_trades": performance["total_trades"],
        "win_rate": performance["win_rate"],
        "expectancy": performance["expectancy"],
        "profit_factor": performance["profit_factor"],
        "max_drawdown": performance["max_drawdown"]
    }

    return {
        "summary": summary,
        "trades": report["trades"]
    }


def run_oos_validation(
    htf_df,
    ltf_df,
    split_date="2026-01-01"
):

    htf_df, ltf_df, common_start = (
        align_dataframes_by_common_start(
            htf_df,
            ltf_df
        )
    )

    htf_train, htf_test = split_train_test(
        htf_df,
        split_date
    )

    ltf_train, ltf_test = split_train_test(
        ltf_df,
        split_date
    )

    configs = {
        "robust_v2": {
            "entry_zone_low_ratio": "0.236",
            "entry_zone_high_ratio": "0.382",
            "invalidation_ratio": "0.618",
            "min_drop_pct": 5.0,
            "max_impulse_bars": 80,
            "max_wait_bars": 100,
            "max_trade_bars": 120,
            "left_bars": 2,
            "right_bars": 2
        },
        "aggressive_v2": {
            "entry_zone_low_ratio": "0.236",
            "entry_zone_high_ratio": "0.382",
            "invalidation_ratio": "0.618",
            "min_drop_pct": 6.0,
            "max_impulse_bars": 80,
            "max_wait_bars": 100,
            "max_trade_bars": 120,
            "left_bars": 2,
            "right_bars": 2
        },
        "base_v1": {
            "entry_zone_low_ratio": "0.236",
            "entry_zone_high_ratio": "0.382",
            "invalidation_ratio": "0.618",
            "min_drop_pct": 5.0,
            "max_impulse_bars": 80,
            "max_wait_bars": 80,
            "max_trade_bars": 120,
            "left_bars": 2,
            "right_bars": 2
        }
    }

    summary_rows = []
    trade_exports = {}

    for config_name, config in configs.items():

        train_result = run_single_config_validation(
            config_name=config_name,
            htf_df=htf_train,
            ltf_df=ltf_train,
            config=config
        )

        train_summary = train_result["summary"]
        train_summary["period"] = "TRAIN"
        train_summary["split_date"] = split_date
        train_summary["common_start"] = common_start

        summary_rows.append(
            train_summary
        )

        trade_exports[
            f"{config_name}_train"
        ] = train_result["trades"]

        test_result = run_single_config_validation(
            config_name=config_name,
            htf_df=htf_test,
            ltf_df=ltf_test,
            config=config
        )

        test_summary = test_result["summary"]
        test_summary["period"] = "TEST"
        test_summary["split_date"] = split_date
        test_summary["common_start"] = common_start

        summary_rows.append(
            test_summary
        )

        trade_exports[
            f"{config_name}_test"
        ] = test_result["trades"]

    return {
        "summary": summary_rows,
        "trades": trade_exports
    }