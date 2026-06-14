from ta.momentum import RSIIndicator


def calculate_rsi(
    df,
    period=14
):

    indicator = RSIIndicator(
        close=df["close"],
        window=period
    )

    return indicator.rsi()