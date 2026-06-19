def fib_v5_long_signal(
    df,
    index: int,
    config=None,
    lookback_bars: int = 48,
    fib_entry_low: float = 0.618,
    fib_entry_high: float = 0.786,
    min_impulse_pct: float = 0.02,
    require_bullish_confirmation: bool = True,
    require_rejection_wick: bool = False,
) -> str:
    """
    Estrategia FIB V5 LONG.

    Lógica espejo del setup SHORT:

    1. Detecta un impulso alcista previo.
    2. Espera retroceso hacia zona Fibonacci 0.618 - 0.786.
    3. Exige confirmación alcista opcional.
    4. Devuelve LONG o NONE.

    Importante:
    No usa velas futuras. Evita lookahead bias.
    """

    if index < lookback_bars:
        return "NONE"

    window = df.iloc[index - lookback_bars:index]

    if window.empty:
        return "NONE"

    # Buscar inicio del impulso: mínimo más bajo del lookback
    impulse_low_idx = window["low"].idxmin()
    impulse_low = float(df.loc[impulse_low_idx, "low"])

    # Buscar máximo posterior al mínimo dentro de la ventana
    after_low = df.loc[impulse_low_idx:index - 1]

    if after_low.empty:
        return "NONE"

    impulse_high_idx = after_low["high"].idxmax()
    impulse_high = float(df.loc[impulse_high_idx, "high"])

    if impulse_high <= impulse_low:
        return "NONE"

    impulse_pct = (impulse_high / impulse_low) - 1

    if impulse_pct < min_impulse_pct:
        return "NONE"

    impulse_range = impulse_high - impulse_low

    # En un impulso alcista, el retroceso Fib cae desde el máximo.
    # 0.618 y 0.786 están bajo el high.
    fib_618_price = impulse_high - (impulse_range * fib_entry_low)
    fib_786_price = impulse_high - (impulse_range * fib_entry_high)

    zone_low = min(fib_618_price, fib_786_price)
    zone_high = max(fib_618_price, fib_786_price)

    row = df.iloc[index]

    candle_open = float(row["open"])
    candle_high = float(row["high"])
    candle_low = float(row["low"])
    candle_close = float(row["close"])

    # La vela actual debe tocar la zona Fib.
    touches_fib_zone = candle_low <= zone_high and candle_high >= zone_low

    if not touches_fib_zone:
        return "NONE"

    if require_bullish_confirmation:
        bullish_confirmation = candle_close > candle_open

        if not bullish_confirmation:
            return "NONE"

    if require_rejection_wick:
        candle_body = abs(candle_close - candle_open)
        lower_wick = min(candle_open, candle_close) - candle_low

        # Exige rechazo inferior: mecha baja relevante.
        if candle_body <= 0:
            return "NONE"

        if lower_wick < candle_body:
            return "NONE"

    return "LONG"