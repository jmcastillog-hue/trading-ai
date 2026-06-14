def detect_bullish_bos(
    df,
    swing_highs
):

    if len(swing_highs) == 0:
        return None

    last_swing_high = swing_highs[-1]

    last_close = df.iloc[-1]["close"]

    if last_close > last_swing_high["price"]:

        return {
            "type": "BULLISH_BOS",
            "broken_level": last_swing_high["price"],
            "broken_index": last_swing_high["index"],
            "current_close": float(last_close)
        }

    return None


def detect_bearish_bos(
    df,
    swing_lows
):

    if len(swing_lows) == 0:
        return None

    last_swing_low = swing_lows[-1]

    last_close = df.iloc[-1]["close"]

    if last_close < last_swing_low["price"]:

        return {
            "type": "BEARISH_BOS",
            "broken_level": last_swing_low["price"],
            "broken_index": last_swing_low["index"],
            "current_close": float(last_close)
        }

    return None