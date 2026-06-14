import os
import sys

sys.path.append(
    os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            ".."
        )
    )
)

from structure.swing_points import (
    detect_swing_highs,
    detect_swing_lows
)

from scenarios.fibonacci_engine import (
    calculate_bearish_fibonacci_levels
)

from backtesting.performance_metrics import (
    generate_performance_report
)


def calculate_short_result_pct(
    entry_price,
    exit_price
):

    return (
        (entry_price - exit_price)
        / entry_price
    ) * 100


def find_entry_in_fib_zone(
    df,
    start_index,
    zone_low,
    zone_high,
    max_wait_bars=80
):

    end_index = min(
        start_index + max_wait_bars,
        len(df) - 1
    )

    for i in range(
        start_index + 1,
        end_index + 1
    ):

        candle_high = df.iloc[i]["high"]
        candle_low = df.iloc[i]["low"]
        candle_close = df.iloc[i]["close"]

        touched_zone = (
            candle_high >= zone_low
            and candle_low <= zone_high
        )

        if touched_zone:

            return {
                "entry_index": i,
                "entry_price": float(candle_close),
                "timestamp": df.iloc[i]["timestamp"]
            }

    return None


def simulate_fib_short_trade(
    df,
    entry_index,
    entry_price,
    stop_price,
    target_price,
    max_trade_bars=80
):

    end_index = min(
        entry_index + max_trade_bars,
        len(df) - 1
    )

    for i in range(
        entry_index + 1,
        end_index + 1
    ):

        candle_high = df.iloc[i]["high"]
        candle_low = df.iloc[i]["low"]

        if candle_high >= stop_price:

            result_pct = calculate_short_result_pct(
                entry_price,
                stop_price
            )

            return {
                "exit_index": i,
                "exit_price": float(stop_price),
                "exit_reason": "STOP_LOSS",
                "result_pct": float(result_pct)
            }

        if candle_low <= target_price:

            result_pct = calculate_short_result_pct(
                entry_price,
                target_price
            )

            return {
                "exit_index": i,
                "exit_price": float(target_price),
                "exit_reason": "TARGET",
                "result_pct": float(result_pct)
            }

    exit_price = float(
        df.iloc[end_index]["close"]
    )

    result_pct = calculate_short_result_pct(
        entry_price,
        exit_price
    )

    return {
        "exit_index": end_index,
        "exit_price": exit_price,
        "exit_reason": "TIME_EXIT",
        "result_pct": float(result_pct)
    }


def run_fib_short_scenario_backtest(
    df,
    min_drop_pct=5,
    max_impulse_bars=120,
    max_wait_bars=80,
    max_trade_bars=80,
    entry_zone_low_ratio="0.236",
    entry_zone_high_ratio="0.382",
    invalidation_ratio="0.618",
    left_bars=2,
    right_bars=2
):

    swing_highs = detect_swing_highs(
        df,
        left_bars=left_bars,
        right_bars=right_bars
    )

    swing_lows = detect_swing_lows(
        df,
        left_bars=left_bars,
        right_bars=right_bars
    )

    trades = []

    last_exit_index = 0

    for swing_high in swing_highs:

        high_index = swing_high["index"]

        if high_index <= last_exit_index:
            continue

        candidate_lows = [
            swing_low for swing_low in swing_lows
            if swing_low["index"] > high_index
            and swing_low["index"] <= high_index + max_impulse_bars
        ]

        if len(candidate_lows) == 0:
            continue

        swing_low = min(
            candidate_lows,
            key=lambda x: x["price"]
        )

        high_price = swing_high["price"]
        low_price = swing_low["price"]

        drop_pct = (
            (high_price - low_price)
            / high_price
        ) * 100

        if drop_pct < min_drop_pct:
            continue

        levels = calculate_bearish_fibonacci_levels(
            impulse_high=high_price,
            impulse_low=low_price
        )

        zone_low = levels[entry_zone_low_ratio]
        zone_high = levels[entry_zone_high_ratio]
        stop_price = levels[invalidation_ratio]
        target_price = low_price

        entry = find_entry_in_fib_zone(
            df=df,
            start_index=swing_low["index"],
            zone_low=zone_low,
            zone_high=zone_high,
            max_wait_bars=max_wait_bars
        )

        if entry is None:
            continue

        trade_result = simulate_fib_short_trade(
            df=df,
            entry_index=entry["entry_index"],
            entry_price=entry["entry_price"],
            stop_price=stop_price,
            target_price=target_price,
            max_trade_bars=max_trade_bars
        )

        last_exit_index = trade_result[
            "exit_index"
        ]

        trades.append({
            "timestamp": entry["timestamp"],
            "direction": "SHORT",
            "impulse_high": high_price,
            "impulse_low": low_price,
            "drop_pct": drop_pct,
            "zone_low": zone_low,
            "zone_high": zone_high,
            "entry_price": entry["entry_price"],
            "stop_price": stop_price,
            "target_price": target_price,
            "exit_price": trade_result["exit_price"],
            "exit_reason": trade_result["exit_reason"],
            "result_pct": trade_result["result_pct"]
        })

    performance = generate_performance_report(
        trades
    )

    return {
        "trades": trades,
        "performance": performance
    }