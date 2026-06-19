from src.strategies.fib_v5_long_strategy import fib_v5_long_signal
from src.market_structure.mtf_regime_filter import long_allowed_by_mtf_regime


def fib_v5_long_with_mtf_filter(df, index: int, config=None) -> str:
    """
    FIB V5 LONG + filtro MTF.

    1. Detecta setup LONG en 15m.
    2. Bloquea LONG si 1h o 4h están fuertemente bajistas.
    """

    base_signal = fib_v5_long_signal(
        df=df,
        index=index,
        config=config,
        lookback_bars=48,
        fib_entry_low=0.618,
        fib_entry_high=0.786,
        min_impulse_pct=0.02,
        require_bullish_confirmation=True,
        require_rejection_wick=False,
    )

    if base_signal != "LONG":
        return "NONE"

    row = df.iloc[index]

    regime_1h = row.get("regime_1h", "UNKNOWN")
    regime_4h = row.get("regime_4h", "UNKNOWN")

    if not long_allowed_by_mtf_regime(regime_1h, regime_4h):
        return "NONE"

    return "LONG"