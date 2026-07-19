from __future__ import annotations

from pathlib import Path
from typing import Final

import pandas as pd


TIMEFRAME_DURATIONS: Final[dict[str, pd.Timedelta]] = {
    "15m": pd.Timedelta(minutes=15),
    "30m": pd.Timedelta(minutes=30),
    "1h": pd.Timedelta(hours=1),
    "4h": pd.Timedelta(hours=4),
    "1d": pd.Timedelta(days=1),
    "1w": pd.Timedelta(weeks=1),
}


def normalize_timeframe_label(timeframe: str) -> str:
    normalized = str(timeframe).strip().lower()
    if normalized not in TIMEFRAME_DURATIONS:
        allowed = ", ".join(TIMEFRAME_DURATIONS)
        raise ValueError(
            f"Unsupported timeframe: {timeframe!r}. Allowed values: {allowed}."
        )
    return normalized


def timeframe_duration(timeframe: str) -> pd.Timedelta:
    return TIMEFRAME_DURATIONS[normalize_timeframe_label(timeframe)]


def expose_features_at_candle_close(
    df: pd.DataFrame,
    timeframe: str,
    timestamp_col: str = "timestamp",
) -> pd.DataFrame:
    """Move feature availability from candle-open time to candle-close time.

    Binance kline timestamps identify candle opens. Indicators calculated from a
    candle's close are not observable until the full candle has completed. This
    helper changes only the merge-availability timestamp; it does not alter OHLCV
    values or calculate indicators.
    """

    normalized = normalize_timeframe_label(timeframe)

    if timestamp_col not in df.columns:
        raise ValueError(f"Missing timestamp column: {timestamp_col}")

    result = df.copy()
    source_timestamps = pd.to_datetime(result[timestamp_col], errors="coerce")

    if source_timestamps.isna().any():
        invalid_count = int(source_timestamps.isna().sum())
        raise ValueError(
            f"Invalid {timestamp_col} values for {normalized}: {invalid_count}."
        )

    if source_timestamps.duplicated().any():
        duplicate_count = int(source_timestamps.duplicated().sum())
        raise ValueError(
            f"Duplicate {timestamp_col} values for {normalized}: {duplicate_count}."
        )

    source_col = f"source_open_timestamp_{normalized}"
    availability_col = f"feature_available_at_{normalized}"
    availability = source_timestamps + timeframe_duration(normalized)

    result[source_col] = source_timestamps
    result[availability_col] = availability
    result[timestamp_col] = availability

    return result.sort_values(timestamp_col).reset_index(drop=True)


def source_uses_closed_candle_contract(path: str | Path) -> bool:
    source_path = Path(path)
    if not source_path.exists() or not source_path.is_file():
        return False
    text = source_path.read_text(encoding="utf-8", errors="ignore")
    return "expose_features_at_candle_close(" in text
