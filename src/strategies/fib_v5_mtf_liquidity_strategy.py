from src.strategies.fib_v5_mtf_strategy import fib_v5_short_with_mtf_filter
from src.liquidity.liquidity_context_filter import short_allowed_by_liquidity_space


def fib_v5_short_with_mtf_and_liquidity_filter(df, index: int, config=None) -> str:
    """
    Estrategia combinada:

    1. FIB V5 detecta entrada SHORT en 15m.
    2. MTF bloquea shorts contra 1h/4h fuertemente alcistas.
    3. Liquidez bloquea shorts sin espacio suficiente hacia sell-side liquidity.
    """

    mtf_signal = fib_v5_short_with_mtf_filter(
        df=df,
        index=index,
        config=config,
    )

    if mtf_signal != "SHORT":
        return "NONE"

    liquidity_ok = short_allowed_by_liquidity_space(
        df=df,
        index=index,
        min_atr_distance=1.5,
        lookback_bars=96,
    )

    if not liquidity_ok:
        return "NONE"

    return "SHORT"