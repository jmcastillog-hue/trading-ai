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


def weighted_short_result_pct(
    entries,
    exit_price
):

    total_result = 0

    for entry in entries:

        entry_price = entry["entry_price"]
        weight = entry["weight"]

        result = (
            (entry_price - exit_price)
            / entry_price
        ) * 100

        total_result += result * weight

    return float(total_result)


def candle_touches_zone(
    candle,
    zone_low,
    zone_high
):

    return (
        candle["high"] >= zone_low
        and candle["low"] <= zone_high
    )


def is_bearish_candle(
    candle
):

    return candle["close"] < candle["open"]


def simulate_partial_short_after_impulse_low(
    ltf_df,
    start_time,
    levels,
    target_price,
    stop_price,
    max_wait_bars=120,
    max_trade_bars=160,
    require_bearish_candle=True
):

    entry_plan = [
        {
            "name": "ENTRY_1",
            "zone_low_ratio": "0.236",
            "zone_high_ratio": "0.382",
            "weight": 0.50
        },
        {
            "name": "ENTRY_2",
            "zone_low_ratio": "0.382",
            "zone_high_ratio": "0.500",
            "weight": 0.30
        },
        {
            "name": "ENTRY_3",
            "zone_low_ratio": "0.500",
            "zone_high_ratio": "0.618",
            "weight": 0.20
        }
    ]

    candidates = ltf_df[
        ltf_df["timestamp"] > start_time
    ].head(
        max_wait_bars + max_trade_bars
    )

    entries = []

    filled_names = set()

    first_entry_time = None

    bars_after_first_entry = 0

    for _, candle in candidates.iterrows():

        candle_time = candle["timestamp"]

        if first_entry_time is None:

            for plan in entry_plan:

                if plan["name"] in filled_names:
                    continue

                zone_low = levels[
                    plan["zone_low_ratio"]
                ]

                zone_high = levels[
                    plan["zone_high_ratio"]
                ]

                touched = candle_touches_zone(
                    candle,
                    zone_low,
                    zone_high
                )

                bearish_ok = (
                    is_bearish_candle(candle)
                    if require_bearish_candle
                    else True
                )

                if touched and bearish_ok:

                    entries.append({
                        "name": plan["name"],
                        "timestamp": candle_time,
                        "entry_price": float(candle["close"]),
                        "weight": plan["weight"],
                        "zone_low": float(zone_low),
                        "zone_high": float(zone_high)
                    })

                    filled_names.add(
                        plan["name"]
                    )

                    first_entry_time = candle_time

                    break

            continue

        bars_after_first_entry += 1

        if bars_after_first_entry > max_trade_bars:
            break

        for plan in entry_plan:

            if plan["name"] in filled_names:
                continue

            zone_low = levels[
                plan["zone_low_ratio"]
            ]

            zone_high = levels[
                plan["zone_high_ratio"]
            ]

            touched = candle_touches_zone(
                candle,
                zone_low,
                zone_high
            )

            bearish_ok = (
                is_bearish_candle(candle)
                if require_bearish_candle
                else True
            )

            if touched and bearish_ok:

                entries.append({
                    "name": plan["name"],
                    "timestamp": candle_time,
                    "entry_price": float(candle["close"]),
                    "weight": plan["weight"],
                    "zone_low": float(zone_low),
                    "zone_high": float(zone_high)
                })

                filled_names.add(
                    plan["name"]
                )

        if len(entries) == 0:
            continue

        if candle["high"] >= stop_price:

            result_pct = weighted_short_result_pct(
                entries,
                stop_price
            )

            return {
                "entries": entries,
                "exit_time": candle_time,
                "exit_price": float(stop_price),
                "exit_reason": "STOP_LOSS",
                "result_pct": result_pct
            }

        if candle["low"] <= target_price:

            result_pct = weighted_short_result_pct(
                entries,
                target_price
            )

            return {
                "entries": entries,
                "exit_time": candle_time,
                "exit_price": float(target_price),
                "exit_reason": "TARGET",
                "result_pct": result_pct
            }

    if len(entries) == 0:
        return None

    last_candle = candidates.iloc[-1]

    exit_price = float(
        last_candle["close"]
    )

    result_pct = weighted_short_result_pct(
        entries,
        exit_price
    )

    return {
        "entries": entries,
        "exit_time": last_candle["timestamp"],
        "exit_price": exit_price,
        "exit_reason": "TIME_EXIT",
        "result_pct": result_pct
    }


def calculate_average_entry(
    entries
):

    total_weight = sum(
        entry["weight"]
        for entry in entries
    )

    if total_weight == 0:
        return 0

    weighted_sum = sum(
        entry["entry_price"] * entry["weight"]
        for entry in entries
    )

    return weighted_sum / total_weight


def run_mtf_fib_short_backtest_v4_partial(
    htf_df,
    ltf_df,
    min_drop_pct=5.0,
    max_impulse_bars=80,
    max_wait_bars=120,
    max_trade_bars=160,
    invalidation_ratio="0.786",
    require_bearish_candle=True,
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

        stop_price = levels[
            invalidation_ratio
        ]

        target_price = low_price

        trade_result = simulate_partial_short_after_impulse_low(
            ltf_df=ltf_df,
            start_time=swing_low["timestamp"],
            levels=levels,
            target_price=target_price,
            stop_price=stop_price,
            max_wait_bars=max_wait_bars,
            max_trade_bars=max_trade_bars,
            require_bearish_candle=require_bearish_candle
        )

        if trade_result is None:
            continue

        entries = trade_result["entries"]

        filled_weight = sum(
            entry["weight"]
            for entry in entries
        )

        average_entry = calculate_average_entry(
            entries
        )

        last_exit_time = trade_result[
            "exit_time"
        ]

        trades.append({
            "entry_time": entries[0]["timestamp"],
            "exit_time": trade_result["exit_time"],
            "direction": "SHORT",
            "entry_mode": "PARTIAL_FIB_ENTRIES",
            "htf_impulse_high": high_price,
            "htf_impulse_low": low_price,
            "drop_pct": drop_pct,
            "filled_entries": len(entries),
            "filled_weight": filled_weight,
            "average_entry": average_entry,
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