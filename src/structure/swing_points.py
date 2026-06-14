def detect_swing_highs(
    df,
    left_bars=2,
    right_bars=2
):

    swing_highs = []

    for i in range(
        left_bars,
        len(df) - right_bars
    ):

        current_high = df.iloc[i]["high"]

        left_highs = df.iloc[
            i - left_bars:i
        ]["high"]

        right_highs = df.iloc[
            i + 1:i + right_bars + 1
        ]["high"]

        if (
            current_high > left_highs.max()
            and current_high > right_highs.max()
        ):

            swing_highs.append({
                "index": i,
                "timestamp": df.iloc[i]["timestamp"],
                "price": float(current_high)
            })

    return swing_highs


def detect_swing_lows(
    df,
    left_bars=2,
    right_bars=2
):

    swing_lows = []

    for i in range(
        left_bars,
        len(df) - right_bars
    ):

        current_low = df.iloc[i]["low"]

        left_lows = df.iloc[
            i - left_bars:i
        ]["low"]

        right_lows = df.iloc[
            i + 1:i + right_bars + 1
        ]["low"]

        if (
            current_low < left_lows.min()
            and current_low < right_lows.min()
        ):

            swing_lows.append({
                "index": i,
                "timestamp": df.iloc[i]["timestamp"],
                "price": float(current_low)
            })

    return swing_lows