from indicators.ema import calculate_ema
from indicators.rsi import calculate_rsi
from indicators.atr import calculate_atr


def generate_indicator_report(df):

    ema20 = calculate_ema(df, 20)

    ema50 = calculate_ema(df, 50)

    ema200 = calculate_ema(df, 200)

    rsi = calculate_rsi(df)

    atr = calculate_atr(df)

    report = {

        "ema20": float(ema20.iloc[-1]),

        "ema50": float(ema50.iloc[-1]),

        "ema200": float(ema200.iloc[-1]),

        "rsi": float(rsi.iloc[-1]),

        "atr": float(atr.iloc[-1])
    }

    return report