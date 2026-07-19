from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import pandas as pd

from src.validation.closed_candle_mtf_revalidation_v1 import (
    MODE_CORRECTED,
    MODE_LEGACY,
    aggregate_short_metrics,
    build_combined_context_dataset,
    build_context_shift_diagnostic,
    build_long_dependency_audit,
    profile_dataset,
)


def synthetic_ohlcv(start: str, periods: int, frequency: str) -> pd.DataFrame:
    timestamps = pd.date_range(start=start, periods=periods, freq=frequency)
    closes = pd.Series(
        [100.0 + (index * 0.15) + ((index % 9) - 4) * 0.30 for index in range(periods)]
    )
    opens = closes.shift(1).fillna(closes.iloc[0])
    return pd.DataFrame(
        {
            "timestamp": timestamps,
            "open": opens,
            "high": pd.concat([opens, closes], axis=1).max(axis=1) + 0.8,
            "low": pd.concat([opens, closes], axis=1).min(axis=1) - 0.8,
            "close": closes,
            "volume": [1000.0] * periods,
        }
    )


class ClosedCandleMtfRevalidationTests(unittest.TestCase):
    def test_legacy_control_and_corrected_contract_are_distinct(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            paths = {
                "15m": root / "market_15m.csv",
                "1h": root / "market_1h.csv",
                "4h": root / "market_4h.csv",
            }
            synthetic_ohlcv("2025-01-01", 480, "15min").to_csv(
                paths["15m"], index=False
            )
            synthetic_ohlcv("2025-01-01", 120, "1h").to_csv(
                paths["1h"], index=False
            )
            synthetic_ohlcv("2025-01-01", 40, "4h").to_csv(
                paths["4h"], index=False
            )

            corrected = build_combined_context_dataset(
                paths["15m"], paths["1h"], paths["4h"], MODE_CORRECTED
            )
            legacy = build_combined_context_dataset(
                paths["15m"], paths["1h"], paths["4h"], MODE_LEGACY
            )
            diagnostic = build_context_shift_diagnostic(
                "SYNTHETIC", corrected, legacy
            )

        self.assertTrue(diagnostic["corrected_closed_candle_invariant_passed"])
        self.assertTrue(diagnostic["legacy_control_reproduces_lookahead"])
        self.assertEqual(diagnostic["corrected_rows"], diagnostic["legacy_rows"])
        self.assertGreater(diagnostic["legacy_early_exposure_rows_1h"], 0)
        self.assertGreater(diagnostic["legacy_early_exposure_rows_4h"], 0)

    def test_dataset_profile_fails_closed_on_duplicate_timestamps(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "duplicate.csv"
            frame = synthetic_ohlcv("2025-01-01", 4, "15min")
            frame.loc[1, "timestamp"] = frame.loc[0, "timestamp"]
            frame.to_csv(path, index=False)

            profile = profile_dataset("BTCUSDT", "15m", path)

        self.assertEqual(profile["duplicate_timestamp_rows"], 1)
        self.assertFalse(profile["dataset_valid"])

    def test_long_primary_chain_has_no_affected_mtf_import(self) -> None:
        audit = build_long_dependency_audit()

        self.assertFalse(audit.empty)
        self.assertTrue(
            audit["independent_of_affected_mtf_modules"].astype(bool).all()
        )
        self.assertTrue(
            audit["classification"].eq("UNAFFECTED_15M_STRUCTURAL_CHAIN").all()
        )

    def test_short_aggregate_keeps_timing_modes_separate(self) -> None:
        windows = pd.DataFrame(
            [
                {
                    "timing_mode": MODE_CORRECTED,
                    "test_trades": 20,
                    "test_return": 0.02,
                    "test_profit_factor": 1.20,
                    "test_expectancy_r": 0.08,
                    "test_drawdown": -0.04,
                },
                {
                    "timing_mode": MODE_LEGACY,
                    "test_trades": 25,
                    "test_return": 0.04,
                    "test_profit_factor": 1.35,
                    "test_expectancy_r": 0.12,
                    "test_drawdown": -0.03,
                },
            ]
        )

        aggregate = aggregate_short_metrics(windows)

        self.assertEqual(set(aggregate["timing_mode"]), {MODE_CORRECTED, MODE_LEGACY})
        self.assertEqual(int(aggregate["test_windows"].sum()), 2)


if __name__ == "__main__":
    unittest.main()
