def get_sell_side_liquidity_level(
    df,
    index: int,
    lookback_bars: int = 96,
) -> float | None:
    """
    Calcula una sell-side liquidity básica usando el mínimo más bajo
    de las últimas N velas anteriores a la entrada.

    Importante:
    No usa velas futuras. Evita lookahead bias.
    """

    if index <= 0:
        return None

    start = max(0, index - lookback_bars)
    window = df.iloc[start:index]

    if window.empty:
        return None

    sell_side_liquidity = float(window["low"].min())

    return sell_side_liquidity


def short_allowed_by_liquidity_space(
    df,
    index: int,
    min_atr_distance: float = 1.5,
    lookback_bars: int = 96,
) -> bool:
    """
    Permite SHORT solo si existe suficiente espacio hacia la liquidez bajista.

    Regla:
    current_price - sell_side_liquidity >= ATR * min_atr_distance
    """

    row = df.iloc[index]

    current_price = float(row["close"])
    atr = float(row.get("atr", 0))

    if atr <= 0:
        return False

    sell_side_liquidity = get_sell_side_liquidity_level(
        df=df,
        index=index,
        lookback_bars=lookback_bars,
    )

    if sell_side_liquidity is None:
        return False

    if sell_side_liquidity >= current_price:
        return False

    distance_to_liquidity = current_price - sell_side_liquidity
    required_distance = atr * min_atr_distance

    return distance_to_liquidity >= required_distance


def get_liquidity_context(
    df,
    index: int,
    min_atr_distance: float = 1.5,
    lookback_bars: int = 96,
) -> dict:
    """
    Devuelve información detallada del contexto de liquidez.
    Útil para análisis posterior.
    """

    row = df.iloc[index]

    current_price = float(row["close"])
    atr = float(row.get("atr", 0))

    sell_side_liquidity = get_sell_side_liquidity_level(
        df=df,
        index=index,
        lookback_bars=lookback_bars,
    )

    if sell_side_liquidity is None or atr <= 0:
        return {
            "sell_side_liquidity": None,
            "distance_to_liquidity": None,
            "required_distance": None,
            "liquidity_space_ok": False,
        }

    distance_to_liquidity = current_price - sell_side_liquidity
    required_distance = atr * min_atr_distance

    liquidity_space_ok = (
        sell_side_liquidity < current_price
        and distance_to_liquidity >= required_distance
    )

    return {
        "sell_side_liquidity": sell_side_liquidity,
        "distance_to_liquidity": distance_to_liquidity,
        "required_distance": required_distance,
        "liquidity_space_ok": liquidity_space_ok,
    }