def detect_buy_side_sweep(
    df,
    swing_highs,
    lookback=50
):

    recent_highs = [
        swing for swing in swing_highs
        if swing["index"] >= len(df) - lookback
    ]

    if len(recent_highs) == 0:
        return None

    last_candle = df.iloc[-1]

    for swing in recent_highs:

        swept = (
            last_candle["high"] > swing["price"]
            and last_candle["close"] < swing["price"]
        )

        if swept:

            return {
                "type": "BUY_SIDE_SWEEP",
                "swept_level": swing["price"],
                "swept_index": swing["index"],
                "current_high": float(last_candle["high"]),
                "current_close": float(last_candle["close"])
            }

    return None


def detect_sell_side_sweep(
    df,
    swing_lows,
    lookback=50
):

    recent_lows = [
        swing for swing in swing_lows
        if swing["index"] >= len(df) - lookback
    ]

    if len(recent_lows) == 0:
        return None

    last_candle = df.iloc[-1]

    for swing in recent_lows:

        swept = (
            last_candle["low"] < swing["price"]
            and last_candle["close"] > swing["price"]
        )

        if swept:

            return {
                "type": "SELL_SIDE_SWEEP",
                "swept_level": swing["price"],
                "swept_index": swing["index"],
                "current_low": float(last_candle["low"]),
                "current_close": float(last_candle["close"])
            }

    return None


def detect_sweep_bos_signal(
    market_structure_report
):

    buy_side_sweep = market_structure_report.get(
        "buy_side_sweep"
    )

    sell_side_sweep = market_structure_report.get(
        "sell_side_sweep"
    )

    bullish_bos = market_structure_report.get(
        "bullish_bos"
    )

    bearish_bos = market_structure_report.get(
        "bearish_bos"
    )

    if buy_side_sweep and bearish_bos:

        return {
            "setup": "SHORT_SWEEP_BOS",
            "bias": "BEARISH",
            "comment": "Barrida de liquidez superior con BOS bajista."
        }

    if sell_side_sweep and bullish_bos:

        return {
            "setup": "LONG_SWEEP_BOS",
            "bias": "BULLISH",
            "comment": "Barrida de liquidez inferior con BOS alcista."
        }

    return {
        "setup": "NO_SWEEP_BOS",
        "bias": "NEUTRAL",
        "comment": "No hay combinación válida de sweep + BOS."
    }