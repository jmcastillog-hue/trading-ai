from pathlib import Path
import pandas as pd


LONG_ALLOWED_STATES = {
    "BULLISH_CONTINUATION",
    "BULLISH_PULLBACK",
}

SHORT_ALLOWED_STATES = {
    "BEARISH_CONTINUATION",
    "BEARISH_PULLBACK",
}


def calculate_rsi(series: pd.Series, period: int = 14) -> pd.Series:
    delta = series.diff()

    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.ewm(alpha=1 / period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1 / period, adjust=False).mean()

    rs = avg_gain / avg_loss.replace(0, pd.NA)
    rsi = 100 - (100 / (1 + rs))

    return rsi.fillna(50)


def calculate_atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
    high = df["high"]
    low = df["low"]
    close = df["close"]

    previous_close = close.shift(1)

    tr_1 = high - low
    tr_2 = (high - previous_close).abs()
    tr_3 = (low - previous_close).abs()

    true_range = pd.concat([tr_1, tr_2, tr_3], axis=1).max(axis=1)
    atr = true_range.ewm(alpha=1 / period, adjust=False).mean()

    return atr


def prepare_regime_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adds technical features needed by Regime Filter V2.

    Expected columns:
    timestamp, open, high, low, close, volume
    """

    result = df.copy()

    result["timestamp"] = pd.to_datetime(result["timestamp"], errors="coerce")
    result = result.dropna(subset=["timestamp"])
    result = result.sort_values("timestamp").reset_index(drop=True)

    numeric_cols = ["open", "high", "low", "close", "volume"]

    for col in numeric_cols:
        if col in result.columns:
            result[col] = pd.to_numeric(result[col], errors="coerce")

    result = result.dropna(subset=["open", "high", "low", "close"])

    result["ema20_v2"] = result["close"].ewm(span=20, adjust=False).mean()
    result["ema50_v2"] = result["close"].ewm(span=50, adjust=False).mean()
    result["ema200_v2"] = result["close"].ewm(span=200, adjust=False).mean()

    result["rsi14_v2"] = calculate_rsi(result["close"], period=14)
    result["atr14_v2"] = calculate_atr(result, period=14)

    result["atr_pct_v2"] = result["atr14_v2"] / result["close"]

    result["ema_spread_pct_v2"] = (
        (result["ema20_v2"] - result["ema200_v2"]).abs() / result["close"]
    )

    result["distance_close_ema20_atr_v2"] = (
        (result["close"] - result["ema20_v2"]) / result["atr14_v2"].replace(0, pd.NA)
    )

    rolling_high = result["high"].rolling(96, min_periods=20).max()
    rolling_low = result["low"].rolling(96, min_periods=20).min()

    result["range_high_96_v2"] = rolling_high
    result["range_low_96_v2"] = rolling_low
    result["range_position_96_v2"] = (
        (result["close"] - rolling_low)
        / (rolling_high - rolling_low).replace(0, pd.NA)
    )

    result["return_24_v2"] = result["close"].pct_change(24)
    result["return_96_v2"] = result["close"].pct_change(96)

    result["market_state_v2"] = result.apply(classify_market_state_v2, axis=1)

    return result


def classify_market_state_v2(row) -> str:
    close = row.get("close")
    ema20 = row.get("ema20_v2")
    ema50 = row.get("ema50_v2")
    ema200 = row.get("ema200_v2")
    rsi = row.get("rsi14_v2")
    atr_distance = row.get("distance_close_ema20_atr_v2")
    ema_spread_pct = row.get("ema_spread_pct_v2")
    range_position = row.get("range_position_96_v2")

    values = [close, ema20, ema50, ema200, rsi]

    if any(pd.isna(value) for value in values):
        return "UNKNOWN"

    close = float(close)
    ema20 = float(ema20)
    ema50 = float(ema50)
    ema200 = float(ema200)
    rsi = float(rsi)

    atr_distance = 0.0 if pd.isna(atr_distance) else float(atr_distance)
    ema_spread_pct = 0.0 if pd.isna(ema_spread_pct) else float(ema_spread_pct)
    range_position = 0.5 if pd.isna(range_position) else float(range_position)

    bullish_stack = ema20 > ema50 > ema200
    bearish_stack = ema20 < ema50 < ema200

    close_above_ema20 = close > ema20
    close_below_ema20 = close < ema20

    close_above_ema50 = close > ema50
    close_below_ema50 = close < ema50

    close_above_ema200 = close > ema200
    close_below_ema200 = close < ema200

    overextended_up = (
        rsi >= 70
        or range_position >= 0.88
        or atr_distance >= 2.0
    )

    overextended_down = (
        rsi <= 30
        or range_position <= 0.12
        or atr_distance <= -2.0
    )

    range_chop = (
        ema_spread_pct <= 0.012
        and 42 <= rsi <= 58
        and 0.25 <= range_position <= 0.75
    )

    if range_chop:
        return "RANGE_CHOP"

    if bullish_stack and close_above_ema20:
        if overextended_up:
            return "BULLISH_EXHAUSTION"

        if 50 <= rsi <= 70:
            return "BULLISH_CONTINUATION"

    if bullish_stack and close_below_ema20 and close_above_ema50:
        if overextended_down:
            return "REVERSAL_RISK"

        if 38 <= rsi <= 58:
            return "BULLISH_PULLBACK"

    if bullish_stack and close_below_ema50:
        return "REVERSAL_RISK"

    if bearish_stack and close_below_ema20:
        if overextended_down:
            return "BEARISH_EXHAUSTION"

        if 30 <= rsi <= 50:
            return "BEARISH_CONTINUATION"

    if bearish_stack and close_above_ema20 and close_below_ema50:
        if overextended_up:
            return "REVERSAL_RISK"

        if 42 <= rsi <= 62:
            return "BEARISH_PULLBACK"

    if bearish_stack and close_above_ema50:
        return "REVERSAL_RISK"

    if close_above_ema200 and close_above_ema50 and rsi >= 55:
        return "BULLISH_CONTINUATION"

    if close_above_ema200 and close_below_ema20 and 40 <= rsi <= 55:
        return "BULLISH_PULLBACK"

    if close_below_ema200 and close_below_ema50 and rsi <= 45:
        return "BEARISH_CONTINUATION"

    if close_below_ema200 and close_above_ema20 and 45 <= rsi <= 60:
        return "BEARISH_PULLBACK"

    return "NEUTRAL_TRANSITION"


def build_prefixed_context(
    df: pd.DataFrame,
    prefix: str,
) -> pd.DataFrame:
    features = prepare_regime_features(df)

    keep_cols = [
        "timestamp",
        "market_state_v2",
        "ema20_v2",
        "ema50_v2",
        "ema200_v2",
        "rsi14_v2",
        "atr14_v2",
        "atr_pct_v2",
        "ema_spread_pct_v2",
        "distance_close_ema20_atr_v2",
        "range_position_96_v2",
        "return_24_v2",
        "return_96_v2",
    ]

    context = features[keep_cols].copy()

    rename_map = {
        col: f"{prefix}_{col}"
        for col in context.columns
        if col != "timestamp"
    }

    context = context.rename(columns=rename_map)

    return context


def enrich_with_regime_filter_v2(
    entry_csv_path: Path,
    h1_csv_path: Path,
    h4_csv_path: Path,
    output_path: Path,
) -> pd.DataFrame:
    """
    Enriches entry timeframe data with 15m, 1h and 4h Market State V2 context.

    entry_csv_path may already contain old MTF columns.
    Existing columns are preserved.
    """

    output_path.parent.mkdir(parents=True, exist_ok=True)

    entry_df = pd.read_csv(entry_csv_path)
    h1_df = pd.read_csv(h1_csv_path)
    h4_df = pd.read_csv(h4_csv_path)

    entry_features = prepare_regime_features(entry_df)

    entry_features = entry_features.rename(
        columns={
            "market_state_v2": "state_15m_v2",
            "ema20_v2": "ema20_15m_v2",
            "ema50_v2": "ema50_15m_v2",
            "ema200_v2": "ema200_15m_v2",
            "rsi14_v2": "rsi14_15m_v2",
            "atr14_v2": "atr14_15m_v2",
            "atr_pct_v2": "atr_pct_15m_v2",
            "ema_spread_pct_v2": "ema_spread_pct_15m_v2",
            "distance_close_ema20_atr_v2": "distance_close_ema20_atr_15m_v2",
            "range_position_96_v2": "range_position_96_15m_v2",
            "return_24_v2": "return_24_15m_v2",
            "return_96_v2": "return_96_15m_v2",
        }
    )

    h1_context = build_prefixed_context(h1_df, "h1")
    h4_context = build_prefixed_context(h4_df, "h4")

    entry_features = entry_features.sort_values("timestamp")
    h1_context = h1_context.sort_values("timestamp")
    h4_context = h4_context.sort_values("timestamp")

    merged = pd.merge_asof(
        entry_features,
        h1_context,
        on="timestamp",
        direction="backward",
    )

    merged = pd.merge_asof(
        merged,
        h4_context,
        on="timestamp",
        direction="backward",
    )

    merged = merged.rename(
        columns={
            "h1_market_state_v2": "state_1h_v2",
            "h4_market_state_v2": "state_4h_v2",
        }
    )

    merged.to_csv(output_path, index=False)

    return merged


def long_allowed_by_regime_v2(state_1h: str, state_4h: str) -> bool:
    if pd.isna(state_1h) or pd.isna(state_4h):
        return False

    state_1h = str(state_1h)
    state_4h = str(state_4h)

    return state_1h in LONG_ALLOWED_STATES and state_4h in LONG_ALLOWED_STATES


def short_allowed_by_regime_v2(state_1h: str, state_4h: str) -> bool:
    if pd.isna(state_1h) or pd.isna(state_4h):
        return False

    state_1h = str(state_1h)
    state_4h = str(state_4h)

    return state_1h in SHORT_ALLOWED_STATES and state_4h in SHORT_ALLOWED_STATES