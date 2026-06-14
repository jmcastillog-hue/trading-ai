import numpy as np


def calculate_returns(df):
    """
    Retornos porcentuales.
    """

    returns = df["close"].pct_change()

    return returns.dropna()


def calculate_volatility(df):
    """
    Desviación estándar de retornos.
    """

    returns = calculate_returns(df)

    volatility = np.std(returns)

    return float(volatility)


def average_range(df):
    """
    Rango promedio de velas.
    """

    ranges = (
        (df["high"] - df["low"])
        / df["close"]
    )

    return float(ranges.mean())