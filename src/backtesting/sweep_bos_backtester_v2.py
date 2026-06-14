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

from backtesting.trade_simulator import (
    simulate_trade_with_atr
)

from backtesting.strategy_tester import (
    prepare_indicator_columns
)

from backtesting.performance_metrics import (
    generate_performance_report
)


def detect_sweep_at_index(
    df,
    index,
    swing_highs,
    swing_lows,
    lookback=50
):

    candle = df.iloc[index]

    recent_highs = [
        swing for swing in swing_highs
        if swing["index"] < index
        and swing["index"] >= index - lookback
    ]

    recent_lows = [
        swing for swing in swing_lows
        if swing["index"] < index
        and swing["index"] >= index - lookback
    ]

    for swing in recent_highs:

        if (
            candle["high"] > swing["price"]
            and candle["close"] < swing["price"]
        ):

            return {
                "type": "BUY_SIDE_SWEEP",
                "swept_level": swing["price"],
                "swept_index": swing["index"]
            }

    for swing in recent_lows:

        if (
            candle["low"] < swing["price"]
            and candle["close"] > swing["price"]
        ):

            return {
                "type": "SELL_SIDE_SWEEP",
                "swept_level": swing["price"],
                "swept_index": swing["index"]
            }

    return None


def find_bos_after_sweep(
    df,
    sweep_index,
    sweep_type,
    swing_highs,
    swing_lows,
    lookahead_bars=10
):

    end_index = min(
        sweep_index + lookahead_bars,
        len(df) - 1
    )

    if sweep_type == "BUY_SIDE_SWEEP":

        recent_lows = [
            swing for swing in swing_lows
            if swing["index"] < sweep_index
        ]

        if len(recent_lows) == 0:
            return None

        target_low = recent_lows[-1]

        for i in range(
            sweep_index + 1,
            end_index + 1
        ):

            if df.iloc[i]["close"] < target_low["price"]:

                return {
                    "type": "BEARISH_BOS",
                    "bos_index": i,
                    "broken_level": target_low["price"]
                }

    if sweep_type == "SELL_SIDE_SWEEP":

        recent_highs = [
            swing for swing in swing_highs
            if swing["index"] < sweep_index
        ]

        if len(recent_highs) == 0:
            return None

        target_high = recent_highs[-1]

        for i in range(
            sweep_index + 1,
            end_index + 1
        ):

            if df.iloc[i]["close"] > target_high["price"]:

                return {
                    "type": "BULLISH_BOS",
                    "bos_index": i,
                    "broken_level": target_high["price"]
                }

    return None


def get_direction_from_sweep_bos(
    sweep_type,
    bos_type
):

    if (
        sweep_type == "BUY_SIDE_SWEEP"
        and bos_type == "BEARISH_BOS"
    ):
        return "SHORT"

    if (
        sweep_type == "SELL_SIDE_SWEEP"
        and bos_type == "BULLISH_BOS"
    ):
        return "LONG"

    return "WAIT"


def run_sweep_bos_backtest_v2(
    df,
    sl_multiplier=1,
    tp_multiplier=2,
    max_bars=8,
    structure_lookback=120,
    sweep_lookback=50,
    lookahead_bos=10,
    left_bars=2,
    right_bars=2
):

    df = prepare_indicator_columns(df)

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

    used_bos_indexes = set()

    for i in range(
        structure_lookback,
        len(df) - max_bars - lookahead_bos
    ):

        sweep = detect_sweep_at_index(
            df,
            i,
            swing_highs,
            swing_lows,
            lookback=sweep_lookback
        )

        if sweep is None:
            continue

        bos = find_bos_after_sweep(
            df,
            i,
            sweep["type"],
            swing_highs,
            swing_lows,
            lookahead_bars=lookahead_bos
        )

        if bos is None:
            continue

        if bos["bos_index"] in used_bos_indexes:
            continue

        direction = get_direction_from_sweep_bos(
            sweep["type"],
            bos["type"]
        )

        if direction == "WAIT":
            continue

        entry_index = bos["bos_index"]

        row = df.iloc[entry_index]

        result = simulate_trade_with_atr(
            df=df,
            entry_index=entry_index,
            direction=direction,
            atr_value=row["atr"],
            sl_multiplier=sl_multiplier,
            tp_multiplier=tp_multiplier,
            max_bars=max_bars
        )

        if result is None:
            continue

        used_bos_indexes.add(
            bos["bos_index"]
        )

        trades.append({
            "timestamp": row["timestamp"],
            "direction": direction,
            "sweep_type": sweep["type"],
            "swept_level": sweep["swept_level"],
            "bos_type": bos["type"],
            "broken_level": bos["broken_level"],
            "entry_index": entry_index,
            "result": result["result"],
            "exit_reason": result["exit_reason"],
            "result_pct": result["result_pct"]
        })

    performance = generate_performance_report(
        trades
    )

    return {
        "trades": trades,
        "performance": performance
    }