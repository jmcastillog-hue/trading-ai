import pandas as pd


def bullish_continuation(df):

    total = 0
    success = 0

    for i in range(len(df) - 1):

        current_bull = (
            df.iloc[i]["close"]
            > df.iloc[i]["open"]
        )

        next_bull = (
            df.iloc[i + 1]["close"]
            > df.iloc[i + 1]["open"]
        )

        if current_bull:

            total += 1

            if next_bull:
                success += 1

    if total == 0:
        return 0

    return success / total * 100


def bearish_continuation(df):

    total = 0
    success = 0

    for i in range(len(df) - 1):

        current_bear = (
            df.iloc[i]["close"]
            < df.iloc[i]["open"]
        )

        next_bear = (
            df.iloc[i + 1]["close"]
            < df.iloc[i + 1]["open"]
        )

        if current_bear:

            total += 1

            if next_bear:
                success += 1

    if total == 0:
        return 0

    return success / total * 100


def bullish_reversal(df):

    total = 0
    reversal = 0

    for i in range(len(df) - 1):

        current_bull = (
            df.iloc[i]["close"]
            > df.iloc[i]["open"]
        )

        next_bear = (
            df.iloc[i + 1]["close"]
            < df.iloc[i + 1]["open"]
        )

        if current_bull:

            total += 1

            if next_bear:
                reversal += 1

    if total == 0:
        return 0

    return reversal / total * 100


def bearish_reversal(df):

    total = 0
    reversal = 0

    for i in range(len(df) - 1):

        current_bear = (
            df.iloc[i]["close"]
            < df.iloc[i]["open"]
        )

        next_bull = (
            df.iloc[i + 1]["close"]
            > df.iloc[i + 1]["open"]
        )

        if current_bear:

            total += 1

            if next_bull:
                reversal += 1

    if total == 0:
        return 0

    return reversal / total * 100


def high_breakout_probability(df):

    total = len(df) - 1

    breakout = 0

    for i in range(len(df) - 1):

        current_high = df.iloc[i]["high"]

        next_high = df.iloc[i + 1]["high"]

        if next_high > current_high:
            breakout += 1

    return breakout / total * 100


def low_breakout_probability(df):

    total = len(df) - 1

    breakout = 0

    for i in range(len(df) - 1):

        current_low = df.iloc[i]["low"]

        next_low = df.iloc[i + 1]["low"]

        if next_low < current_low:
            breakout += 1

    return breakout / total * 100


def average_up_move(df):

    bullish = df[
        df["close"] > df["open"]
    ]

    if len(bullish) == 0:
        return 0

    move = (
        (bullish["close"] - bullish["open"])
        / bullish["open"]
    ) * 100

    return float(move.mean())


def average_down_move(df):

    bearish = df[
        df["close"] < df["open"]
    ]

    if len(bearish) == 0:
        return 0

    move = (
        (bearish["close"] - bearish["open"])
        / bearish["open"]
    ) * 100

    return float(move.mean())


def generate_probability_report(df):

    report = {

        "bullish_continuation":
            bullish_continuation(df),

        "bearish_continuation":
            bearish_continuation(df),

        "bullish_reversal":
            bullish_reversal(df),

        "bearish_reversal":
            bearish_reversal(df),

        "high_breakout":
            high_breakout_probability(df),

        "low_breakout":
            low_breakout_probability(df),

        "average_up_move":
            average_up_move(df),

        "average_down_move":
            average_down_move(df),

        "sample_size":
            len(df)
    }

    return report