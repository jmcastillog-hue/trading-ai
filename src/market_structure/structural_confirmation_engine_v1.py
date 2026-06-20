import pandas as pd


def calculate_atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
    high_low = df["high"] - df["low"]
    high_close = (df["high"] - df["close"].shift(1)).abs()
    low_close = (df["low"] - df["close"].shift(1)).abs()

    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)

    return tr.ewm(alpha=1 / period, adjust=False).mean()


def calculate_rsi(close: pd.Series, period: int = 14) -> pd.Series:
    delta = close.diff()

    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.ewm(alpha=1 / period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1 / period, adjust=False).mean()

    rs = avg_gain / avg_loss.replace(0, pd.NA)
    rsi = 100 - (100 / (1 + rs))

    return rsi.fillna(50)


def normalize_numeric_ohlcv(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy()

    required = ["open", "high", "low", "close"]

    missing = [col for col in required if col not in result.columns]

    if missing:
        raise ValueError(f"Missing OHLC columns for structural engine: {missing}")

    for col in ["open", "high", "low", "close", "volume"]:
        if col in result.columns:
            result[col] = pd.to_numeric(result[col], errors="coerce")

    return result


def _safe_bool(value) -> bool:
    if isinstance(value, bool):
        return value

    if isinstance(value, (int, float)):
        return bool(value)

    if isinstance(value, str):
        return value.strip().lower() in {"true", "1", "yes", "y"}

    return False


def classify_short_structural_block(row: pd.Series) -> str:
    distance_ema20_atr = row.get("scv1_distance_ema20_atr")
    range_position_48 = row.get("scv1_range_position_48")
    rsi14 = row.get("scv1_rsi14")
    atr14 = row.get("scv1_atr14")

    if pd.isna(atr14) or atr14 <= 0:
        return "MISSING_ATR"

    if pd.isna(distance_ema20_atr) or pd.isna(range_position_48) or pd.isna(rsi14):
        return "MISSING_FEATURES"

    if distance_ema20_atr <= -2.50 and range_position_48 <= 0.15:
        return "DOWNSIDE_CHASE_BLOCK"

    if rsi14 <= 22 and range_position_48 <= 0.20:
        return "EXTREME_OVERSOLD_BLOCK"

    return "NONE"


def build_short_structural_reason(row: pd.Series) -> str:
    reasons = []

    if _safe_bool(row.get("scv1_break_low_10")):
        reasons.append("BREAK_LOW_10")

    if _safe_bool(row.get("scv1_break_low_20")):
        reasons.append("BREAK_LOW_20")

    if _safe_bool(row.get("scv1_sweep_high_reject")):
        reasons.append("SWEEP_HIGH_REJECT")

    if _safe_bool(row.get("scv1_bearish_rejection_candle")):
        reasons.append("BEARISH_REJECTION")

    if _safe_bool(row.get("scv1_below_ema20_with_down_slope")):
        reasons.append("BELOW_EMA20_DOWNSLOPE")

    if _safe_bool(row.get("scv1_not_chasing_down")):
        reasons.append("NOT_CHASING_DOWN")

    if not reasons:
        return "NO_STRUCTURAL_REASON"

    return "|".join(reasons)


def add_structural_confirmation_v1_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adds 15m structural confirmation columns.

    Initial design is SHORT-focused because the only robust V3.1 context found so far
    is a SHORT context:
    - directional_context_v3 = SHORT_CAUTION
    - bias_1h_v3 = BEARISH_TREND
    - bias_4h_v3 = BEARISH_OVEREXTENDED
    """

    result = normalize_numeric_ohlcv(df)

    result["scv1_atr14"] = calculate_atr(result, period=14)
    result["scv1_rsi14"] = calculate_rsi(result["close"], period=14)

    result["scv1_ema20"] = result["close"].ewm(span=20, adjust=False).mean()
    result["scv1_ema50"] = result["close"].ewm(span=50, adjust=False).mean()

    result["scv1_ema20_slope_8"] = (
        result["scv1_ema20"] / result["scv1_ema20"].shift(8) - 1
    )

    result["scv1_prior_low_10"] = (
        result["low"].shift(1).rolling(10, min_periods=5).min()
    )

    result["scv1_prior_low_20"] = (
        result["low"].shift(1).rolling(20, min_periods=10).min()
    )

    result["scv1_prior_high_20"] = (
        result["high"].shift(1).rolling(20, min_periods=10).max()
    )

    result["scv1_prior_high_48"] = (
        result["high"].shift(1).rolling(48, min_periods=20).max()
    )

    result["scv1_prior_low_48"] = (
        result["low"].shift(1).rolling(48, min_periods=20).min()
    )

    result["scv1_range_position_48"] = (
        (result["close"] - result["scv1_prior_low_48"])
        / (result["scv1_prior_high_48"] - result["scv1_prior_low_48"]).replace(0, pd.NA)
    )

    result["scv1_distance_ema20_atr"] = (
        (result["close"] - result["scv1_ema20"])
        / result["scv1_atr14"].replace(0, pd.NA)
    )

    candle_range = (result["high"] - result["low"]).replace(0, pd.NA)
    candle_body = (result["close"] - result["open"]).abs()

    result["scv1_upper_wick_ratio"] = (
        result["high"] - result[["open", "close"]].max(axis=1)
    ) / candle_range

    result["scv1_lower_wick_ratio"] = (
        result[["open", "close"]].min(axis=1) - result["low"]
    ) / candle_range

    result["scv1_body_ratio"] = candle_body / candle_range

    result["scv1_bearish_close"] = result["close"] < result["open"]

    result["scv1_break_low_10"] = (
        result["close"] < result["scv1_prior_low_10"]
    )

    result["scv1_break_low_20"] = (
        result["close"] < result["scv1_prior_low_20"]
    )

    result["scv1_sweep_high_reject"] = (
        (result["high"] > result["scv1_prior_high_20"])
        & (result["close"] < result["scv1_prior_high_20"])
        & result["scv1_bearish_close"]
    )

    result["scv1_bearish_rejection_candle"] = (
        result["scv1_bearish_close"]
        & (result["scv1_upper_wick_ratio"] >= 0.35)
        & (result["scv1_body_ratio"] >= 0.15)
    )

    result["scv1_below_ema20_with_down_slope"] = (
        (result["close"] < result["scv1_ema20"])
        & (result["scv1_ema20_slope_8"] < 0)
    )

    result["scv1_not_chasing_down"] = (
        (result["scv1_distance_ema20_atr"] > -2.00)
        & (result["scv1_range_position_48"] > 0.10)
    )

    result["short_structural_score_v1"] = (
        result["scv1_break_low_10"].astype(int)
        + result["scv1_break_low_20"].astype(int)
        + result["scv1_sweep_high_reject"].astype(int) * 2
        + result["scv1_bearish_rejection_candle"].astype(int)
        + result["scv1_below_ema20_with_down_slope"].astype(int)
        + result["scv1_not_chasing_down"].astype(int)
    )

    result["short_structural_block_reason_v1"] = result.apply(
        classify_short_structural_block,
        axis=1,
    )

    result["short_structural_reason_v1"] = result.apply(
        build_short_structural_reason,
        axis=1,
    )

    no_block = result["short_structural_block_reason_v1"] == "NONE"

    result["short_structural_confirmed_v1_not_chasing_only"] = (
        result["scv1_not_chasing_down"] & no_block
    )

    result["short_structural_confirmed_v1_sweep_or_rejection"] = (
        (
            result["scv1_sweep_high_reject"]
            | result["scv1_bearish_rejection_candle"]
        )
        & result["scv1_not_chasing_down"]
        & no_block
    )

    result["short_structural_confirmed_v1_score_2"] = (
        (result["short_structural_score_v1"] >= 2)
        & no_block
    )

    result["short_structural_confirmed_v1_score_3"] = (
        (result["short_structural_score_v1"] >= 3)
        & no_block
    )

    result["short_structural_recent_score_2_lookback_4"] = (
        result["short_structural_confirmed_v1_score_2"]
        .rolling(4, min_periods=1)
        .max()
        .astype(bool)
    )

    result["short_structural_recent_sweep_or_rejection_lookback_4"] = (
        result["short_structural_confirmed_v1_sweep_or_rejection"]
        .rolling(4, min_periods=1)
        .max()
        .astype(bool)
    )

    # Backward-compatible aliases from first V1 test.
    result["short_structural_confirmed_v1_balanced"] = (
        result["short_structural_confirmed_v1_score_2"]
    )

    result["short_structural_confirmed_v1_strict"] = (
        result["short_structural_confirmed_v1_score_3"]
    )

    return result