from structure.swing_points import (
    detect_swing_highs,
    detect_swing_lows
)

from structure.bos_detector import (
    detect_bullish_bos,
    detect_bearish_bos
)

from structure.sweep_bos_detector import (
    detect_buy_side_sweep,
    detect_sell_side_sweep,
    detect_sweep_bos_signal
)


def generate_market_structure_report(
    df,
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

    bullish_bos = detect_bullish_bos(
        df,
        swing_highs
    )

    bearish_bos = detect_bearish_bos(
        df,
        swing_lows
    )

    buy_side_sweep = detect_buy_side_sweep(
        df,
        swing_highs
    )

    sell_side_sweep = detect_sell_side_sweep(
        df,
        swing_lows
    )

    if bullish_bos:
        structure_bias = "BULLISH"

    elif bearish_bos:
        structure_bias = "BEARISH"

    else:
        structure_bias = "NEUTRAL"

    last_swing_high = (
        swing_highs[-1]
        if len(swing_highs) > 0
        else None
    )

    last_swing_low = (
        swing_lows[-1]
        if len(swing_lows) > 0
        else None
    )

    sweep_bos_signal = detect_sweep_bos_signal({
    "buy_side_sweep": buy_side_sweep,
    "sell_side_sweep": sell_side_sweep,
    "bullish_bos": bullish_bos,
    "bearish_bos": bearish_bos
    })

    return {
        "structure_bias": structure_bias,
        "swing_high_count": len(swing_highs),
        "swing_low_count": len(swing_lows),
        "last_swing_high": last_swing_high,
        "last_swing_low": last_swing_low,
        "bullish_bos": bullish_bos,
        "bearish_bos": bearish_bos,
        "buy_side_sweep": buy_side_sweep,
        "sell_side_sweep": sell_side_sweep,
        "sweep_bos_signal": sweep_bos_signal
    }