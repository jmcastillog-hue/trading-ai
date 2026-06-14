from ta.volatility import AverageTrueRange


def calculate_atr(
    df,
    period=14
):

    indicator = AverageTrueRange(
        high=df["high"],
        low=df["low"],
        close=df["close"],
        window=period
    )

    return indicator.average_true_range()