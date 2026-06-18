from src.strategies.fib_v5_strategy import fib_v5_short_signal
from src.market_structure.mtf_regime_filter import short_allowed_by_mtf_regime


def fib_v5_short_with_mtf_filter(df, index: int, config=None) -> str:
    base_signal = fib_v5_short_signal(
        df=df,
        index=index,
        config=config,
        lookback_bars=48,
        fib_entry_low=0.618,
        fib_entry_high=0.786,
        min_impulse_pct=0.02,
        require_bearish_confirmation=True,
        require_rejection_wick=False,
    )

    if base_signal != "SHORT":
        return "NONE"

    row = df.iloc[index]

    regime_1h = row.get("regime_1h", "UNKNOWN")
    regime_4h = row.get("regime_4h", "UNKNOWN")

    if not short_allowed_by_mtf_regime(regime_1h, regime_4h):
        return "NONE"

    return "SHORT"