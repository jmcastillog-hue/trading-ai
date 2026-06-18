from src.strategies.fib_v5_mtf_strategy import fib_v5_short_with_mtf_filter
from src.liquidity.liquidity_zones_v2 import short_allowed_by_liquidity_zone_v2


def fib_v5_short_with_mtf_and_liquidity_v2_filter(df, index: int, config=None) -> str:
    """
    Estrategia combinada:

    1. FIB V5 detecta entrada SHORT en 15m.
    2. MTF bloquea shorts contra 1h/4h fuertemente alcistas.
    3. Liquidez V2 exige espacio hacia swing low / equal low cercano.

    Configuración balanceada seleccionada en el sweep Fase 1.7:
    - lookback_bars: 192
    - min_atr_distance: 0.8
    - equal_low_tolerance_atr: 0.35
    - min_touches: 2
    """

    mtf_signal = fib_v5_short_with_mtf_filter(
        df=df,
        index=index,
        config=config,
    )

    if mtf_signal != "SHORT":
        return "NONE"

    liquidity_ok = short_allowed_by_liquidity_zone_v2(
        df=df,
        index=index,
        min_atr_distance=0.8,
        lookback_bars=192,
        left_bars=2,
        right_bars=2,
        equal_low_tolerance_atr=0.35,
        min_touches=2,
    )

    if not liquidity_ok:
        return "NONE"

    return "SHORT"