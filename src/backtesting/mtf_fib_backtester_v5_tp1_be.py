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


def calculate_tp1_price(
    entry_price,
    target_price,
    tp1_ratio=0.50
):
    distance = entry_price - target_price

    return entry_price - (
        distance * tp1_ratio
    )


def find_ltf_entry_in_fib_zone(
    ltf_df,
    start_time,
    zone_low,
    zone_high,
    max_wait_bars=100
):
    candidates = ltf_df[
        ltf_df["timestamp"] > start_time
    ].head(max_wait_bars)

    for _, candle in candidates.iterrows():

        touched_zone = (
            candle["high"] >= zone_low
            and candle["low"] <= zone_high
        )

        bearish_confirmation = (
            candle["close"] < candle["open"]
        )

        if touched_zone and bearish_confirmation:

            return {
                "timestamp": candle["timestamp"],
                "entry_price": float(candle["close"])
            }

    return None


def simulate_short_trade_tp1_be(
    ltf_df,
    entry_time,
    entry_price,
    stop_price,
    target_price,
    max_trade_bars=120,
    tp1_ratio=0.50,
    tp1_close_weight=0.50
):
    future = ltf_df[
        ltf_df["timestamp"] > entry_time
    ].head(max_trade_bars)

    if len(future) == 0:
        return None

    tp1_price = calculate_tp1_price(
        entry_price=entry_price,
        target_price=target_price,
        tp1_ratio=tp1_ratio
    )

    tp1_hit = False

    realized_result = 0

    remaining_weight = 1.0

    stop_after_tp1 = stop_price

    exit_reason = None

    exit_price = None

    exit_time = None

    for _, candle in future.iterrows():

        candle_time = candle["timestamp"]
        candle_high = candle["high"]
        candle_low = candle["low"]

        if not tp1_hit:

            if candle_high >= stop_price:

                full_loss = short_result_pct(
                    entry_price,
                    stop_price
                )

                return {
                    "exit_time": candle_time,
                    "exit_price": float(stop_price),
                    "exit_reason": "STOP_LOSS_BEFORE_TP1",
                    "tp1_hit": False,
                    "tp1_price": float(tp1_price),
                    "result_pct": float(full_loss)
                }

            if candle_low <= tp1_price:

                tp1_result = short_result_pct(
                    entry_price,
                    tp1_price
                )

                realized_result += (
                    tp1_result * tp1_close_weight
                )

                remaining_weight = (
                    1.0 - tp1_close_weight
                )

                tp1_hit = True

                stop_after_tp1 = entry_price

                if candle_low <= target_price:

                    tp2_result = short_result_pct(
                        entry_price,
                        target_price
                    )

                    realized_result += (
                        tp2_result * remaining_weight
                    )

                    return {
                        "exit_time": candle_time,
                        "exit_price": float(target_price),
                        "exit_reason": "TP1_AND_TARGET",
                        "tp1_hit": True,
                        "tp1_price": float(tp1_price),
                        "result_pct": float(realized_result)
                    }

                continue

        if tp1_hit:

            if candle_high >= stop_after_tp1:

                be_result = short_result_pct(
                    entry_price,
                    stop_after_tp1
                )

                realized_result += (
                    be_result * remaining_weight
                )

                return {
                    "exit_time": candle_time,
                    "exit_price": float(stop_after_tp1),
                    "exit_reason": "TP1_THEN_BREAKEVEN",
                    "tp1_hit": True,
                    "tp1_price": float(tp1_price),
                    "result_pct": float(realized_result)
                }

            if candle_low <= target_price:

                tp2_result = short_result_pct(
                    entry_price,
                    target_price
                )

                realized_result += (
                    tp2_result * remaining_weight
                )

                return {
                    "exit_time": candle_time,
                    "exit_price": float(target_price),
                    "exit_reason": "TP1_THEN_TARGET",
                    "tp1_hit": True,
                    "tp1_price": float(tp1_price),
                    "result_pct": float(realized_result)
                }

    last_candle = future.iloc[-1]

    exit_price = float(
        last_candle["close"]
    )

    exit_time = last_candle["timestamp"]

    if tp1_hit:

        remaining_result = short_result_pct(
            entry_price,
            exit_price
        )

        realized_result += (
            remaining_result * remaining_weight
        )

        exit_reason = "TP1_THEN_TIME_EXIT"

    else:

        realized_result = short_result_pct(
            entry_price,
            exit_price
        )

        exit_reason = "TIME_EXIT_NO_TP1"

    return {
        "exit_time": exit_time,
        "exit_price": exit_price,
        "exit_reason": exit_reason,
        "tp1_hit": tp1_hit,
        "tp1_price": float(tp1_price),
        "result_pct": float(realized_result)
    }


def run_mtf_fib_short_backtest_v5_tp1_be(
    htf_df,
    ltf_df,
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

        zone_low = levels[
            entry_zone_low_ratio
        ]

        zone_high = levels[
            entry_zone_high_ratio
        ]

        stop_price = levels[
            invalidation_ratio
        ]

        target_price = low_price

        entry = find_ltf_entry_in_fib_zone(
            ltf_df=ltf_df,
            start_time=swing_low["timestamp"],
            zone_low=zone_low,
            zone_high=zone_high,
            max_wait_bars=max_wait_bars
        )

        if entry is None:
            continue

        trade_result = simulate_short_trade_tp1_be(
            ltf_df=ltf_df,
            entry_time=entry["timestamp"],
            entry_price=entry["entry_price"],
            stop_price=stop_price,
            target_price=target_price,
            max_trade_bars=max_trade_bars,
            tp1_ratio=tp1_ratio,
            tp1_close_weight=tp1_close_weight
        )

        if trade_result is None:
            continue

        last_exit_time = trade_result[
            "exit_time"
        ]

        trades.append({
            "entry_time": entry["timestamp"],
            "exit_time": trade_result["exit_time"],
            "direction": "SHORT",
            "entry_mode": "FIB_ZONE_TP1_BE",
            "htf_impulse_high": high_price,
            "htf_impulse_low": low_price,
            "drop_pct": drop_pct,
            "fib_zone_low": zone_low,
            "fib_zone_high": zone_high,
            "entry_price": entry["entry_price"],
            "stop_price": stop_price,
            "target_price": target_price,
            "tp1_price": trade_result["tp1_price"],
            "tp1_hit": trade_result["tp1_hit"],
            "tp1_ratio": tp1_ratio,
            "tp1_close_weight": tp1_close_weight,
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