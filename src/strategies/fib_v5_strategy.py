def fib_v5_short_signal(
    df,
    index: int,
    config=None,
    lookback_bars: int = 96,
    fib_entry_low: float = 0.618,
    fib_entry_high: float = 0.786,
    min_impulse_pct: float = 0.02,
    require_bearish_confirmation: bool = True,
    require_rejection_wick: bool = False,
) -> str:
    """
    Estrategia FIB V5 histórica para backtesting.

    Lógica:
    1. Busca un impulso bajista dentro de una ventana histórica.
    2. Calcula zona Fibonacci de rebote.
    3. Detecta si la vela actual toca la zona Fib.
    4. Si hay confirmación bajista, genera señal SHORT.

    Esta versión no usa EMA.
    """

    if index < lookback_bars + 1:
        return "NONE"

    window = df.iloc[index - lookback_bars:index]

    swing_high_idx = window["high"].idxmax()
    swing_low_idx = window["low"].idxmin()

    swing_high = float(window.loc[swing_high_idx, "high"])
    swing_low = float(window.loc[swing_low_idx, "low"])

    if swing_high <= 0 or swing_low <= 0:
        return "NONE"

    # Para SHORT queremos primero un máximo y luego una caída.
    if swing_high_idx > swing_low_idx:
        return "NONE"

    impulse_pct = (swing_high - swing_low) / swing_high

    if impulse_pct < min_impulse_pct:
        return "NONE"

    fib_range = swing_high - swing_low

    fib_low_price = swing_low + (fib_range * fib_entry_low)
    fib_high_price = swing_low + (fib_range * fib_entry_high)

    current_row = df.iloc[index]
    previous_row = df.iloc[index - 1]

    current_open = float(current_row["open"])
    current_high = float(current_row["high"])
    current_low = float(current_row["low"])
    current_close = float(current_row["close"])
    previous_close = float(previous_row["close"])

    # La vela toca la zona Fib si su rango cruza la zona.
    price_touched_fib_zone = (
        current_high >= fib_low_price
        and current_low <= fib_high_price
    )

    if not price_touched_fib_zone:
        return "NONE"

    bearish_candle = current_close < current_open
    bearish_close = current_close < previous_close

    body_size = abs(current_close - current_open)
    upper_wick = current_high - max(current_close, current_open)

    if body_size == 0:
        body_size = 0.0000001

    rejection_wick = upper_wick >= body_size * 0.5

    if require_bearish_confirmation:
        if not (bearish_candle and bearish_close):
            return "NONE"

    if require_rejection_wick:
        if not rejection_wick:
            return "NONE"

    return "SHORT"