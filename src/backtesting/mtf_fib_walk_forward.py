import os
import sys
import pandas as pd
import itertools

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

from backtesting.performance_metrics import (
    generate_performance_report
)


def build_candidate_configs():

    configs = []

    min_drop_values = [
        5.0,
        5.5,
        6.0
    ]

    max_impulse_values = [
        60,
        80
    ]

    max_wait_values = [
        60,
        80,
        100
    ]

    max_trade_values = [
        80,
        120
    ]

    combinations = itertools.product(
        min_drop_values,
        max_impulse_values,
        max_wait_values,
        max_trade_values
    )

    for (
        min_drop,
        max_impulse,
        max_wait,
        max_trade
    ) in combinations:

        configs.append({
            "entry_zone_low_ratio": "0.236",
            "entry_zone_high_ratio": "0.382",
            "invalidation_ratio": "0.618",
            "min_drop_pct": min_drop,
            "max_impulse_bars": max_impulse,
            "max_wait_bars": max_wait,
            "max_trade_bars": max_trade,
            "left_bars": 2,
            "right_bars": 2
        })

    return configs


def align_common_period(
    htf_df,
    ltf_df
):

    common_start = max(
        htf_df["timestamp"].min(),
        ltf_df["timestamp"].min()
    )

    common_end = min(
        htf_df["timestamp"].max(),
        ltf_df["timestamp"].max()
    )

    htf_df = htf_df[
        (htf_df["timestamp"] >= common_start)
        & (htf_df["timestamp"] <= common_end)
    ].copy()

    ltf_df = ltf_df[
        (ltf_df["timestamp"] >= common_start)
        & (ltf_df["timestamp"] <= common_end)
    ].copy()

    return htf_df, ltf_df, common_start, common_end


def generate_windows(
    common_start,
    common_end,
    train_months=8,
    test_months=2,
    step_months=2
):

    windows = []

    train_start = pd.to_datetime(
        common_start
    )

    window_id = 1

    while True:

        train_end = train_start + pd.DateOffset(
            months=train_months
        )

        test_start = train_end

        test_end = test_start + pd.DateOffset(
            months=test_months
        )

        if test_end > common_end:
            break

        windows.append({
            "window_id": window_id,
            "train_start": train_start,
            "train_end": train_end,
            "test_start": test_start,
            "test_end": test_end
        })

        train_start = train_start + pd.DateOffset(
            months=step_months
        )

        window_id += 1

    return windows


def filter_df_by_time(
    df,
    start_time,
    end_time
):

    return df[
        (df["timestamp"] >= start_time)
        & (df["timestamp"] < end_time)
    ].copy()


def filter_trades_by_entry_time(
    trades,
    start_time,
    end_time
):

    filtered = []

    for trade in trades:

        entry_time = pd.to_datetime(
            trade["entry_time"]
        )

        if (
            entry_time >= start_time
            and entry_time < end_time
        ):
            filtered.append(trade)

    return filtered


def apply_cost_to_trades(
    trades,
    cost_pct=0.10
):

    adjusted = []

    for trade in trades:

        trade_copy = trade.copy()

        trade_copy["raw_result_pct"] = (
            trade_copy["result_pct"]
        )

        trade_copy["cost_pct"] = cost_pct

        trade_copy["result_pct"] = (
            trade_copy["result_pct"] - cost_pct
        )

        adjusted.append(
            trade_copy
        )

    return adjusted


def calculate_net_result(
    trades
):

    return sum(
        trade["result_pct"]
        for trade in trades
    )


def run_config_on_period(
    htf_df,
    ltf_df,
    config,
    entry_start,
    entry_end,
    cost_pct=0.10
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

    trades = filter_trades_by_entry_time(
        report["trades"],
        entry_start,
        entry_end
    )

    trades = apply_cost_to_trades(
        trades,
        cost_pct=cost_pct
    )

    performance = generate_performance_report(
        trades
    )

    performance["net_result"] = calculate_net_result(
        trades
    )

    return {
        "trades": trades,
        "performance": performance
    }


def config_to_text(
    config
):

    return (
        f"drop={config['min_drop_pct']} | "
        f"impulse={config['max_impulse_bars']} | "
        f"wait={config['max_wait_bars']} | "
        f"trade={config['max_trade_bars']}"
    )


def choose_best_config(
    htf_train,
    ltf_train,
    configs,
    train_start,
    train_end,
    cost_pct=0.10,
    min_train_trades=6
):

    candidates = []

    for config in configs:

        result = run_config_on_period(
            htf_df=htf_train,
            ltf_df=ltf_train,
            config=config,
            entry_start=train_start,
            entry_end=train_end,
            cost_pct=cost_pct
        )

        performance = result["performance"]

        if performance["total_trades"] < min_train_trades:
            continue

        if performance["expectancy"] <= 0:
            continue

        candidates.append({
            "config": config,
            "performance": performance
        })

    if len(candidates) == 0:
        return None

    candidates = sorted(
        candidates,
        key=lambda x: (
            x["performance"]["profit_factor"],
            x["performance"]["expectancy"],
            x["performance"]["total_trades"]
        ),
        reverse=True
    )

    return candidates[0]


def run_walk_forward_validation(
    htf_df,
    ltf_df,
    train_months=8,
    test_months=2,
    step_months=2,
    cost_pct=0.10,
    min_train_trades=6
):

    htf_df, ltf_df, common_start, common_end = (
        align_common_period(
            htf_df,
            ltf_df
        )
    )

    windows = generate_windows(
        common_start=common_start,
        common_end=common_end,
        train_months=train_months,
        test_months=test_months,
        step_months=step_months
    )

    configs = build_candidate_configs()

    summary_rows = []

    all_test_trades = []

    for window in windows:

        print(
            f"\nVentana {window['window_id']} | "
            f"TRAIN {window['train_start'].date()} → {window['train_end'].date()} | "
            f"TEST {window['test_start'].date()} → {window['test_end'].date()}",
            flush=True
        )

        htf_train = filter_df_by_time(
            htf_df,
            window["train_start"],
            window["train_end"]
        )

        ltf_train = filter_df_by_time(
            ltf_df,
            window["train_start"],
            window["train_end"]
        )

        best = choose_best_config(
            htf_train=htf_train,
            ltf_train=ltf_train,
            configs=configs,
            train_start=window["train_start"],
            train_end=window["train_end"],
            cost_pct=cost_pct,
            min_train_trades=min_train_trades
        )

        if best is None:

            print(
                "No hubo configuración válida en TRAIN.",
                flush=True
            )

            continue

        best_config = best["config"]

        train_perf = best["performance"]

        print(
            f"Mejor config: {config_to_text(best_config)}",
            flush=True
        )

        print(
            f"TRAIN PF: {train_perf['profit_factor']:.2f} | "
            f"EXP: {train_perf['expectancy']:.2f} | "
            f"TRADES: {train_perf['total_trades']}",
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
            config=best_config,
            entry_start=window["test_start"],
            entry_end=window["test_end"],
            cost_pct=cost_pct
        )

        test_perf = test_result["performance"]

        print(
            f"TEST PF: {test_perf['profit_factor']:.2f} | "
            f"EXP: {test_perf['expectancy']:.2f} | "
            f"TRADES: {test_perf['total_trades']}",
            flush=True
        )

        for trade in test_result["trades"]:

            trade["window_id"] = window["window_id"]

            all_test_trades.append(
                trade
            )

        summary_rows.append({
            "window_id": window["window_id"],
            "train_start": window["train_start"],
            "train_end": window["train_end"],
            "test_start": window["test_start"],
            "test_end": window["test_end"],
            "cost_pct": cost_pct,
            "config": config_to_text(best_config),
            "min_drop_pct": best_config["min_drop_pct"],
            "max_impulse_bars": best_config["max_impulse_bars"],
            "max_wait_bars": best_config["max_wait_bars"],
            "max_trade_bars": best_config["max_trade_bars"],
            "train_trades": train_perf["total_trades"],
            "train_win_rate": train_perf["win_rate"],
            "train_expectancy": train_perf["expectancy"],
            "train_profit_factor": train_perf["profit_factor"],
            "train_max_drawdown": train_perf["max_drawdown"],
            "train_net_result": train_perf["net_result"],
            "test_trades": test_perf["total_trades"],
            "test_win_rate": test_perf["win_rate"],
            "test_expectancy": test_perf["expectancy"],
            "test_profit_factor": test_perf["profit_factor"],
            "test_max_drawdown": test_perf["max_drawdown"],
            "test_net_result": test_perf["net_result"]
        })

    final_performance = generate_performance_report(
        all_test_trades
    )

    final_performance["net_result"] = calculate_net_result(
        all_test_trades
    )

    return {
        "summary": summary_rows,
        "test_trades": all_test_trades,
        "final_performance": final_performance
    }