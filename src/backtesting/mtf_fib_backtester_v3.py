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


def short_result_pct(
    entry_price,
    exit_price
):

    return (
        (entry_price - exit_price)
        / entry_price
    ) * 100


def find_first_touch_in_fib_zone(
    ltf_df,
    start_time,
    zone_low,
    zone_high,
    max_wait_bars=100
):

    candidates = ltf_df[
        ltf_df["timestamp"] > start_time
    ].head(max_wait_bars)

    for index, candle in candidates.iterrows():

        touched_zone = (
            candle["high"] >= zone_low
            and candle["low"] <= zone_high
        )

        if touched_zone:

            return {
                "index": index,
                "timestamp": candle["timestamp"],
                "price": float(candle["close"])
            }

    return None


def find_bearish_micro_break_after_touch(
    ltf_df,
    touch_index,
    confirmation_bars=12,
    break_lookback=6
):

    end_index = min(
        touch_index + confirmation_bars,
        len(ltf_df) - 1
    )

    for i in range(
        touch_index + 1,
        end_index + 1
    ):

        if i - break_lookback < 0:
            continue

        previous_lows = ltf_df.iloc[
            i - break_lookback:i
        ]["low"]

        micro_support = previous_lows.min()

        candle = ltf_df.iloc[i]

        bearish_close_break = (
            candle["close"] < micro_support
        )

        bearish_body = (
            candle["close"] < candle["open"]
        )

        if (
            bearish_close_break
            and bearish_body
        ):

            return {
                "index": i,
                "timestamp": candle["timestamp"],
                "entry_price": float(candle["close"]),
                "micro_support": float(micro_support),
                "entry_reason": "BEARISH_MICRO_BREAK"
            }

    return None


def simulate_ltf_short_trade(
    ltf_df,
    entry_time,
    entry_price,
    stop_price,
    target_price,
    max_trade_bars=120
):

    future = ltf_df[
        ltf_df["timestamp"] > entry_time
    ].head(max_trade_bars)

    for _, candle in future.iterrows():

        if candle["high"] >= stop_price:

            return {
                "exit_time": candle["timestamp"],
                "exit_price": float(stop_price),
                "exit_reason": "STOP_LOSS",
                "result_pct": short_result_pct(
                    entry_price,
                    stop_price
                )
            }

        if candle["low"] <= target_price:

            return {
                "exit_time": candle["timestamp"],
                "exit_price": float(target_price),
                "exit_reason": "TARGET",
                "result_pct": short_result_pct(
                    entry_price,
                    target_price
                )
            }

    if len(future) == 0:
        return None

    last_candle = future.iloc[-1]

    return {
        "exit_time": last_candle["timestamp"],
        "exit_price": float(last_candle["close"]),
        "exit_reason": "TIME_EXIT",
        "result_pct": short_result_pct(
            entry_price,
            float(last_candle["close"])
        )
    }


def run_mtf_fib_short_backtest_v3(
    htf_df,
    ltf_df,
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
):

    swing_highs = detect_swing_highs(
        htf_df,
        left_bars=left_bars,
        right_bars=right_bars
    )

    swing_lows = detect_swing_lows(
        htf_df,
        left_bars=left_bars,
        right_bars=right_bars
    )

    trades = []

    last_exit_time = None

    for swing_high in swing_highs:

        if (
            last_exit_time is not None
            and swing_high["timestamp"] <= last_exit_time
        ):
            continue

        candidate_lows = [
            swing_low for swing_low in swing_lows
            if swing_low["index"] > swing_high["index"]
            and swing_low["index"] <= swing_high["index"] + max_impulse_bars
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

        touch = find_first_touch_in_fib_zone(
            ltf_df=ltf_df,
            start_time=swing_low["timestamp"],
            zone_low=zone_low,
            zone_high=zone_high,
            max_wait_bars=max_wait_bars
        )

        if touch is None:
            continue

        entry = find_bearish_micro_break_after_touch(
            ltf_df=ltf_df,
            touch_index=touch["index"],
            confirmation_bars=confirmation_bars,
            break_lookback=break_lookback
        )

        if entry is None:
            continue

        trade_result = simulate_ltf_short_trade(
            ltf_df=ltf_df,
            entry_time=entry["timestamp"],
            entry_price=entry["entry_price"],
            stop_price=stop_price,
            target_price=target_price,
            max_trade_bars=max_trade_bars
        )

        if trade_result is None:
            continue

        last_exit_time = trade_result["exit_time"]

        trades.append({
            "entry_time": entry["timestamp"],
            "exit_time": trade_result["exit_time"],
            "direction": "SHORT",
            "entry_reason": entry["entry_reason"],
            "htf_impulse_high": high_price,
            "htf_impulse_low": low_price,
            "drop_pct": drop_pct,
            "fib_zone_low": zone_low,
            "fib_zone_high": zone_high,
            "touch_time": touch["timestamp"],
            "micro_support": entry["micro_support"],
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