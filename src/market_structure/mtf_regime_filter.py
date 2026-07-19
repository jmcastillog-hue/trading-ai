from pathlib import Path
import pandas as pd

from src.market_structure.closed_candle_mtf import (
    expose_features_at_candle_close,
)


def load_ohlcv(csv_path: str | Path) -> pd.DataFrame:
    df = pd.read_csv(csv_path)
    df.columns = [str(col).strip().lower() for col in df.columns]

    if "open_time" in df.columns and "timestamp" not in df.columns:
        df = df.rename(columns={"open_time": "timestamp"})

    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")

    for col in ["open", "high", "low", "close", "volume"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.dropna(subset=["timestamp", "open", "high", "low", "close"])
    df = df.sort_values("timestamp").reset_index(drop=True)

    return df


def classify_regime(row) -> str:
    close = row["close"]
    ema20 = row["ema20"]
    ema50 = row["ema50"]
    ema200 = row["ema200"]

    if close > ema20 > ema50 > ema200:
        return "STRONG_BULLISH"

    if close > ema50 and ema20 > ema50:
        return "BULLISH"

    if close < ema20 < ema50 < ema200:
        return "STRONG_BEARISH"

    if close < ema50 and ema20 < ema50:
        return "BEARISH"

    return "NEUTRAL"


def build_regime_df(csv_path: str | Path, timeframe_label: str) -> pd.DataFrame:
    df = load_ohlcv(csv_path)

    df["ema20"] = df["close"].ewm(span=20, adjust=False).mean()
    df["ema50"] = df["close"].ewm(span=50, adjust=False).mean()
    df["ema200"] = df["close"].ewm(span=200, adjust=False).mean()

    df[f"regime_{timeframe_label}"] = df.apply(classify_regime, axis=1)

    regime_df = df[["timestamp", f"regime_{timeframe_label}"]].copy()

    return expose_features_at_candle_close(
        regime_df,
        timeframe=timeframe_label,
    )


def enrich_15m_with_mtf_regime(
    entry_csv_path: str | Path,
    h1_csv_path: str | Path,
    h4_csv_path: str | Path,
    output_path: str | Path,
) -> pd.DataFrame:
    entry_df = load_ohlcv(entry_csv_path)
    h1_regime = build_regime_df(h1_csv_path, "1h")
    h4_regime = build_regime_df(h4_csv_path, "4h")

    entry_df = pd.merge_asof(
        entry_df.sort_values("timestamp"),
        h1_regime.sort_values("timestamp"),
        on="timestamp",
        direction="backward",
    )

    entry_df = pd.merge_asof(
        entry_df.sort_values("timestamp"),
        h4_regime.sort_values("timestamp"),
        on="timestamp",
        direction="backward",
    )

    entry_df["regime_1h"] = entry_df["regime_1h"].fillna("UNKNOWN")
    entry_df["regime_4h"] = entry_df["regime_4h"].fillna("UNKNOWN")

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    entry_df.to_csv(output_path, index=False)

    return entry_df

def short_allowed_by_mtf_regime(regime_1h: str, regime_4h: str) -> bool:
    """
    Initial conservative rule for SHORT.

    Allows SHORT if:
    - 1h is not STRONG_BULLISH.
    - 4h is not STRONG_BULLISH.
    - 1h and 4h regimes exist.

    This rule avoids selling against strong bullish impulse.
    """

    if regime_1h == "UNKNOWN" or regime_4h == "UNKNOWN":
        return False

    if regime_1h == "STRONG_BULLISH":
        return False

    if regime_4h == "STRONG_BULLISH":
        return False

    return True


def long_allowed_by_mtf_regime(regime_1h: str, regime_4h: str) -> bool:
    """
    Initial conservative rule for LONG.

    Allows LONG if:
    - 1h is not STRONG_BEARISH.
    - 4h is not STRONG_BEARISH.
    - 1h and 4h regimes exist.

    This rule avoids buying against strong bearish impulse.
    """

    if regime_1h == "UNKNOWN" or regime_4h == "UNKNOWN":
        return False

    if regime_1h == "STRONG_BEARISH":
        return False

    if regime_4h == "STRONG_BEARISH":
        return False

    return True
