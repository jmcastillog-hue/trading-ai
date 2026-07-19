from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import pandas as pd

from src.market_structure.closed_candle_mtf import (
    expose_features_at_candle_close,
    timeframe_duration,
)
from src.market_structure.directional_context_filter_v3 import (
    prepare_directional_features,
)
from src.market_structure.mtf_regime_filter import (
    enrich_15m_with_mtf_regime,
)


def build_ohlcv(timestamps: list[str], closes: list[float]) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "timestamp": pd.to_datetime(timestamps),
            "open": closes,
            "high": [value + 1.0 for value in closes],
            "low": [value - 1.0 for value in closes],
            "close": closes,
            "volume": [100.0] * len(closes),
        }
    )


class ClosedCandleMtfContractTests(unittest.TestCase):
    def test_timeframe_durations_are_explicit(self) -> None:
        self.assertEqual(timeframe_duration("1h"), pd.Timedelta(hours=1))
        self.assertEqual(timeframe_duration("4H"), pd.Timedelta(hours=4))

    def test_features_become_available_only_at_close(self) -> None:
        source = pd.DataFrame(
            {
                "timestamp": pd.to_datetime(["2026-01-01 00:00:00"]),
                "regime_4h": ["BEARISH"],
            }
        )

        available = expose_features_at_candle_close(source, "4h")

        self.assertEqual(
            available.loc[0, "source_open_timestamp_4h"],
            pd.Timestamp("2026-01-01 00:00:00"),
        )
        self.assertEqual(
            available.loc[0, "timestamp"],
            pd.Timestamp("2026-01-01 04:00:00"),
        )

    def test_duplicate_higher_timeframe_open_is_rejected(self) -> None:
        source = pd.DataFrame(
            {
                "timestamp": pd.to_datetime(
                    ["2026-01-01 00:00:00", "2026-01-01 00:00:00"]
                ),
                "regime_1h": ["BEARISH", "BULLISH"],
            }
        )

        with self.assertRaisesRegex(ValueError, "Duplicate timestamp"):
            expose_features_at_candle_close(source, "1h")

    def test_mtf_merge_cannot_see_open_hour_candle_early(self) -> None:
        entry = build_ohlcv(
            [
                "2026-01-01 00:00:00",
                "2026-01-01 00:45:00",
                "2026-01-01 01:00:00",
            ],
            [100.0, 99.0, 98.0],
        )
        h1 = build_ohlcv(
            ["2026-01-01 00:00:00", "2026-01-01 01:00:00"],
            [90.0, 80.0],
        )
        h4 = build_ohlcv(["2026-01-01 00:00:00"], [85.0])

        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            entry_path = root / "entry.csv"
            h1_path = root / "h1.csv"
            h4_path = root / "h4.csv"
            output_path = root / "enriched.csv"
            entry.to_csv(entry_path, index=False)
            h1.to_csv(h1_path, index=False)
            h4.to_csv(h4_path, index=False)

            enriched = enrich_15m_with_mtf_regime(
                entry_csv_path=entry_path,
                h1_csv_path=h1_path,
                h4_csv_path=h4_path,
                output_path=output_path,
            )

        before_close = enriched.loc[
            enriched["timestamp"].eq(pd.Timestamp("2026-01-01 00:45:00"))
        ].iloc[0]
        at_close = enriched.loc[
            enriched["timestamp"].eq(pd.Timestamp("2026-01-01 01:00:00"))
        ].iloc[0]

        self.assertEqual(before_close["regime_1h"], "UNKNOWN")
        self.assertTrue(pd.isna(before_close["source_open_timestamp_1h"]))
        self.assertEqual(
            at_close["source_open_timestamp_1h"],
            pd.Timestamp("2026-01-01 00:00:00"),
        )
        self.assertEqual(at_close["regime_4h"], "UNKNOWN")

    def test_directional_features_use_close_availability(self) -> None:
        source = build_ohlcv(
            ["2026-01-01 00:00:00", "2026-01-01 01:00:00"],
            [100.0, 101.0],
        )

        result = prepare_directional_features(source, "1h")

        self.assertEqual(
            result.loc[0, "source_open_timestamp_1h"],
            pd.Timestamp("2026-01-01 00:00:00"),
        )
        self.assertEqual(
            result.loc[0, "timestamp"],
            pd.Timestamp("2026-01-01 01:00:00"),
        )


if __name__ == "__main__":
    unittest.main()
