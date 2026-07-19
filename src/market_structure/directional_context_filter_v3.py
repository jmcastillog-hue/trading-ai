from pathlib import Path
import pandas as pd

from src.market_structure.closed_candle_mtf import (
    expose_features_at_candle_close,
)


def normalize_ohlcv_columns(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy()

    rename_map = {
        "Open time": "timestamp",
        "open_time": "timestamp",
        "Date": "timestamp",
        "Fecha": "timestamp",
        "Open": "open",
        "High": "high",
        "Low": "low",
        "Close": "close",
        "Volume": "volume",
    }

    result = result.rename(columns=rename_map)

    required = ["timestamp", "open", "high", "low", "close"]

    missing = [col for col in required if col not in result.columns]

    if missing:
        raise ValueError(f"Missing OHLCV columns: {missing}")

    result["timestamp"] = pd.to_datetime(result["timestamp"], errors="coerce")

    for col in ["open", "high", "low", "close", "volume"]:
        if col in result.columns:
            result[col] = pd.to_numeric(result[col], errors="coerce")

    result = result.dropna(subset=["timestamp", "open", "high", "low", "close"])
    result = result.sort_values("timestamp").reset_index(drop=True)

    return result


def calculate_rsi(close: pd.Series, period: int = 14) -> pd.Series:
    delta = close.diff()

    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.ewm(alpha=1 / period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1 / period, adjust=False).mean()

    rs = avg_gain / avg_loss.mask(avg_loss.eq(0))

    rsi = 100 - (100 / (1 + rs))

    return rsi.fillna(50)


def calculate_atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
    high_low = df["high"] - df["low"]
    high_close = (df["high"] - df["close"].shift(1)).abs()
    low_close = (df["low"] - df["close"].shift(1)).abs()

    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)

    return tr.ewm(alpha=1 / period, adjust=False).mean()


def prepare_directional_features(df: pd.DataFrame, prefix: str) -> pd.DataFrame:
    result = normalize_ohlcv_columns(df)

    result[f"{prefix}_ema20"] = result["close"].ewm(span=20, adjust=False).mean()
    result[f"{prefix}_ema50"] = result["close"].ewm(span=50, adjust=False).mean()
    result[f"{prefix}_ema200"] = result["close"].ewm(span=200, adjust=False).mean()

    result[f"{prefix}_atr14"] = calculate_atr(result, period=14)
    result[f"{prefix}_rsi14"] = calculate_rsi(result["close"], period=14)

    result[f"{prefix}_return_12"] = result["close"].pct_change(12)
    result[f"{prefix}_return_24"] = result["close"].pct_change(24)
    result[f"{prefix}_return_48"] = result["close"].pct_change(48)

    result[f"{prefix}_ema20_slope_12"] = (
        result[f"{prefix}_ema20"] / result[f"{prefix}_ema20"].shift(12) - 1
    )

    result[f"{prefix}_ema50_slope_12"] = (
        result[f"{prefix}_ema50"] / result[f"{prefix}_ema50"].shift(12) - 1
    )

    result[f"{prefix}_ema_spread_pct"] = (
        (result[f"{prefix}_ema20"] - result[f"{prefix}_ema50"])
        / result["close"].replace(0, pd.NA)
    )

    result[f"{prefix}_distance_ema20_atr"] = (
        (result["close"] - result[f"{prefix}_ema20"])
        / result[f"{prefix}_atr14"].replace(0, pd.NA)
    )

    result[f"{prefix}_distance_ema50_atr"] = (
        (result["close"] - result[f"{prefix}_ema50"])
        / result[f"{prefix}_atr14"].replace(0, pd.NA)
    )

    rolling_high = result["high"].rolling(96, min_periods=20).max()
    rolling_low = result["low"].rolling(96, min_periods=20).min()

    result[f"{prefix}_range_position_96"] = (
        (result["close"] - rolling_low)
        / (rolling_high - rolling_low).replace(0, pd.NA)
    )

    keep_cols = [
        "timestamp",
        "close",
        f"{prefix}_ema20",
        f"{prefix}_ema50",
        f"{prefix}_ema200",
        f"{prefix}_atr14",
        f"{prefix}_rsi14",
        f"{prefix}_return_12",
        f"{prefix}_return_24",
        f"{prefix}_return_48",
        f"{prefix}_ema20_slope_12",
        f"{prefix}_ema50_slope_12",
        f"{prefix}_ema_spread_pct",
        f"{prefix}_distance_ema20_atr",
        f"{prefix}_distance_ema50_atr",
        f"{prefix}_range_position_96",
    ]

    result = result[keep_cols].copy()
    result = result.rename(columns={"close": f"{prefix}_close"})

    return expose_features_at_candle_close(
        result,
        timeframe=prefix,
    )


def classify_tf_bias(row: pd.Series, prefix: str) -> str:
    close = row.get(f"{prefix}_close")
    ema20 = row.get(f"{prefix}_ema20")
    ema50 = row.get(f"{prefix}_ema50")
    ema200 = row.get(f"{prefix}_ema200")
    rsi = row.get(f"{prefix}_rsi14")
    ret_24 = row.get(f"{prefix}_return_24")
    ema20_slope = row.get(f"{prefix}_ema20_slope_12")
    ema50_slope = row.get(f"{prefix}_ema50_slope_12")
    distance_ema20_atr = row.get(f"{prefix}_distance_ema20_atr")
    range_position = row.get(f"{prefix}_range_position_96")

    values = [
        close,
        ema20,
        ema50,
        ema200,
        rsi,
        ret_24,
        ema20_slope,
        ema50_slope,
        distance_ema20_atr,
        range_position,
    ]

    if any(pd.isna(value) for value in values):
        return "UNKNOWN"

    bullish_structure = close > ema20 > ema50
    bearish_structure = close < ema20 < ema50

    strong_bullish_structure = close > ema20 > ema50 > ema200
    strong_bearish_structure = close < ema20 < ema50 < ema200

    bullish_momentum = ret_24 > 0.015 and ema20_slope > 0 and rsi >= 52
    bearish_momentum = ret_24 < -0.015 and ema20_slope < 0 and rsi <= 48

    bullish_slope = ema20_slope > 0 and ema50_slope >= 0
    bearish_slope = ema20_slope < 0 and ema50_slope <= 0

    overextended_up = distance_ema20_atr >= 2.0 or range_position >= 0.90 or rsi >= 72
    overextended_down = distance_ema20_atr <= -2.0 or range_position <= 0.10 or rsi <= 28

    if strong_bullish_structure and bullish_momentum and bullish_slope:
        if overextended_up:
            return "BULLISH_OVEREXTENDED"
        return "BULLISH_TREND"

    if strong_bearish_structure and bearish_momentum and bearish_slope:
        if overextended_down:
            return "BEARISH_OVEREXTENDED"
        return "BEARISH_TREND"

    if bullish_structure and bullish_slope:
        if overextended_up:
            return "BULLISH_OVEREXTENDED"
        return "BULLISH_BIAS"

    if bearish_structure and bearish_slope:
        if overextended_down:
            return "BEARISH_OVEREXTENDED"
        return "BEARISH_BIAS"

    if ret_24 > 0.02 and rsi >= 55:
        return "BULLISH_MOMENTUM"

    if ret_24 < -0.02 and rsi <= 45:
        return "BEARISH_MOMENTUM"

    if overextended_up:
        return "UPSIDE_EXTENSION_RISK"

    if overextended_down:
        return "DOWNSIDE_EXTENSION_RISK"

    return "MIXED_OR_RANGE"


def classify_directional_context_v3(row: pd.Series) -> str:
    bias_1h = row.get("bias_1h_v3", "UNKNOWN")
    bias_4h = row.get("bias_4h_v3", "UNKNOWN")

    bullish_states = {
        "BULLISH_TREND",
        "BULLISH_BIAS",
        "BULLISH_MOMENTUM",
    }

    bearish_states = {
        "BEARISH_TREND",
        "BEARISH_BIAS",
        "BEARISH_MOMENTUM",
    }

    bullish_extension_states = {
        "BULLISH_OVEREXTENDED",
        "UPSIDE_EXTENSION_RISK",
    }

    bearish_extension_states = {
        "BEARISH_OVEREXTENDED",
        "DOWNSIDE_EXTENSION_RISK",
    }

    if bias_1h == "UNKNOWN" or bias_4h == "UNKNOWN":
        return "NO_TRADE"

    if bias_1h in bullish_states and bias_4h in bullish_states:
        return "LONG_ONLY"

    if bias_1h in bearish_states and bias_4h in bearish_states:
        return "SHORT_ONLY"

    if bias_1h in bullish_states and bias_4h in bullish_extension_states:
        return "LONG_CAUTION"

    if bias_1h in bearish_states and bias_4h in bearish_extension_states:
        return "SHORT_CAUTION"

    if bias_1h in bearish_extension_states and bias_4h in bearish_extension_states:
        return "NO_TRADE_DOWNSIDE_EXTENSION"

    if bias_1h in bullish_extension_states and bias_4h in bullish_extension_states:
        return "NO_TRADE_UPSIDE_EXTENSION"

    if bias_1h in bullish_states and bias_4h in bearish_states:
        return "CONFLICT_NO_TRADE"

    if bias_1h in bearish_states and bias_4h in bullish_states:
        return "CONFLICT_NO_TRADE"

    return "NO_TRADE_MIXED"


def long_allowed_by_directional_context_v3(context: str) -> bool:
    return context in {
        "LONG_ONLY",
        "LONG_CAUTION",
    }


def short_allowed_by_directional_context_v3(context: str) -> bool:
    return context in {
        "SHORT_ONLY",
        "SHORT_CAUTION",
    }


def enrich_with_directional_context_v3(
    entry_csv_path: str | Path,
    h1_csv_path: str | Path,
    h4_csv_path: str | Path,
    output_path: str | Path | None = None,
) -> pd.DataFrame:
    entry_df = normalize_ohlcv_columns(pd.read_csv(entry_csv_path))
    h1_df = pd.read_csv(h1_csv_path)
    h4_df = pd.read_csv(h4_csv_path)

    h1_features = prepare_directional_features(h1_df, "1h")
    h4_features = prepare_directional_features(h4_df, "4h")

    entry_df = entry_df.sort_values("timestamp").reset_index(drop=True)
    h1_features = h1_features.sort_values("timestamp").reset_index(drop=True)
    h4_features = h4_features.sort_values("timestamp").reset_index(drop=True)

    enriched = pd.merge_asof(
        entry_df,
        h1_features,
        on="timestamp",
        direction="backward",
    )

    enriched = pd.merge_asof(
        enriched,
        h4_features,
        on="timestamp",
        direction="backward",
    )

    enriched["bias_1h_v3"] = enriched.apply(
        lambda row: classify_tf_bias(row, "1h"),
        axis=1,
    )

    enriched["bias_4h_v3"] = enriched.apply(
        lambda row: classify_tf_bias(row, "4h"),
        axis=1,
    )

    enriched["directional_context_v3"] = enriched.apply(
        classify_directional_context_v3,
        axis=1,
    )

    enriched["long_allowed_v3"] = enriched["directional_context_v3"].apply(
        long_allowed_by_directional_context_v3
    )

    enriched["short_allowed_v3"] = enriched["directional_context_v3"].apply(
        short_allowed_by_directional_context_v3
    )

    if output_path is not None:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        enriched.to_csv(output_path, index=False)

    return enriched
