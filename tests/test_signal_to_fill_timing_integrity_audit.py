from __future__ import annotations

import unittest
from pathlib import Path
from unittest.mock import patch

import pandas as pd

from src.backtesting.backtesting_engine_v3 import BacktestConfig
from src.exits.active_exit_manager_v1 import add_active_exit_features
from src.validation.signal_to_fill_timing_integrity_audit_v1 import (
    FILL_SAME_CLOSE,
    FILL_NEXT_OPEN,
    LONG_PRIMARY,
    LONG_SECONDARY,
    SAFETY_FLAGS,
    build_cost_accounting_audit,
    compare_long_historical_to_phase_8_4,
    compare_phase_8_10_to_r2_readiness,
    long_timing_metrics_are_identical,
    resolve_long_trade_next_open,
    run_signal_to_fill_timing_integrity_audit,
    run_short_next_open_backtest,
    simulate_short_trade_next_open,
)
from src.validation.walk_forward_engine_v1 import build_fixed_rr_exit_profile


def market_frame(periods: int = 320) -> pd.DataFrame:
    timestamps = pd.date_range("2026-01-01", periods=periods, freq="15min")
    closes = pd.Series([100.0 + (index % 7) * 0.1 for index in range(periods)])
    opens = closes.shift(1).fillna(100.0)
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


class SignalToFillTimingIntegrityAuditTests(unittest.TestCase):
    def setUp(self) -> None:
        self.config = BacktestConfig(
            initial_capital=1000.0,
            risk_per_trade=0.01,
            risk_reward=2.5,
            fee_rate=0.001,
            spread_rate=0.0002,
            atr_period=14,
            atr_multiplier=1.25,
            max_holding_bars=48,
            direction_mode="short_only",
        )
        self.exit_profile = build_fixed_rr_exit_profile(2.5, "TEST_FIXED_RR")

    def test_short_fill_uses_next_bar_open_after_signal(self) -> None:
        frame = add_active_exit_features(market_frame(20))
        frame.loc[5, "close"] = 100.0
        frame.loc[6, "open"] = 105.0
        frame.loc[5, "aev1_atr14"] = 2.0
        frame.loc[6, "high"] = 110.0
        frame.loc[6, "low"] = 104.0

        trade = simulate_short_trade_next_open(
            frame,
            signal_index=5,
            capital=1000.0,
            config=self.config,
            exit_profile=self.exit_profile,
        )

        self.assertIsNotNone(trade)
        assert trade is not None
        self.assertEqual(trade["fill_mode"], FILL_NEXT_OPEN)
        self.assertEqual(trade["entry_index"], trade["signal_index"] + 1)
        self.assertGreater(pd.Timestamp(trade["entry_time"]), pd.Timestamp(trade["signal_time"]))
        self.assertAlmostEqual(trade["raw_entry_reference"], 105.0)
        self.assertNotAlmostEqual(trade["raw_entry_reference"], trade["signal_close"])
        self.assertEqual(trade["exit_index"], trade["entry_index"])
        self.assertEqual(trade["exit_reason"], "STOP_LOSS")

    def test_short_backtest_keeps_signal_and_fill_indexes_distinct(self) -> None:
        frame = market_frame()
        frame.loc[251, "open"] = 103.0

        def one_signal(df: pd.DataFrame, index: int, config: object) -> str:
            return "SHORT" if index == 250 else "NONE"

        trades, summary = run_short_next_open_backtest(
            frame,
            one_signal,
            self.config,
            self.exit_profile,
        )

        self.assertEqual(int(summary["total_trades"]), 1)
        self.assertEqual(int(trades.iloc[0]["signal_index"]), 250)
        self.assertEqual(int(trades.iloc[0]["entry_index"]), 251)
        self.assertGreater(
            pd.Timestamp(trades.iloc[0]["entry_time"]),
            pd.Timestamp(trades.iloc[0]["signal_time"]),
        )

    def test_long_fill_uses_next_bar_open_after_signal(self) -> None:
        frame = market_frame(50)
        frame["symbol"] = "BTCUSDT"
        frame["timeframe"] = "15m"
        frame["atr14"] = 1.0
        frame["rolling_low_20"] = frame["low"].shift(1).fillna(frame["low"])
        frame.loc[10, "close"] = 100.0
        frame.loc[11, "open"] = 102.0

        trade = resolve_long_trade_next_open(
            frame,
            signal_index=10,
            candidate_id=LONG_PRIMARY,
        )

        self.assertIsNotNone(trade)
        assert trade is not None
        self.assertEqual(trade["entry_index"], 11)
        self.assertEqual(trade["entry_price"], 102.0)
        self.assertGreater(pd.Timestamp(trade["entry_time"]), pd.Timestamp(trade["observed_at"]))
        self.assertTrue(trade["valid_long_structure"])
        self.assertFalse(trade["long_strategy_approved"])
        self.assertFalse(trade["execution_allowed"])

    def test_cost_audit_detects_embedded_cost_overlap(self) -> None:
        audit = build_cost_accounting_audit()

        self.assertEqual(len(audit), 5)
        self.assertTrue(
            audit["potential_cost_double_count_confirmed"].astype(bool).all()
        )
        self.assertTrue(
            audit["current_pipeline_subtracts_full_profile_from_net_result"]
            .astype(bool)
            .all()
        )
        self.assertFalse(audit["normalized_cost_decision_allowed"].astype(bool).any())
        self.assertTrue(audit["overlapping_cost_pct"].gt(0).all())

    def test_all_safety_permissions_remain_false(self) -> None:
        self.assertTrue(SAFETY_FLAGS)
        self.assertFalse(any(SAFETY_FLAGS.values()))

    def test_long_lineage_keeps_historical_and_readiness_stages_distinct(self) -> None:
        historical = pd.DataFrame(
            [
                {
                    "candidate_id": LONG_PRIMARY,
                    "trades": 12,
                    "total_result_r": 5.5,
                    "average_result_r": 5.5 / 12,
                    "profit_factor": 2.1,
                    "max_drawdown_r": -2.0,
                },
                {
                    "candidate_id": LONG_SECONDARY,
                    "trades": 21,
                    "total_result_r": 4.5,
                    "average_result_r": 4.5 / 21,
                    "profit_factor": 1.4,
                    "max_drawdown_r": -4.0,
                },
            ]
        )
        current = pd.concat(
            [historical.assign(fill_mode=FILL_SAME_CLOSE)],
            ignore_index=True,
        )
        historical_comparison = compare_long_historical_to_phase_8_4(
            current,
            historical,
        )
        self.assertTrue(historical_comparison["all_metrics_match"].all())

        monte_carlo = pd.DataFrame(
            [
                {
                    "candidate_id": LONG_PRIMARY,
                    "source_trade_count": 5,
                    "original_total_result_r": 3.002336,
                },
                {
                    "candidate_id": LONG_SECONDARY,
                    "source_trade_count": 10,
                    "original_total_result_r": 1.501988,
                },
            ]
        )
        readiness = monte_carlo.copy()
        readiness_comparison = compare_phase_8_10_to_r2_readiness(
            monte_carlo,
            readiness,
        )
        self.assertTrue(readiness_comparison["all_metrics_match"].all())
        self.assertFalse(
            historical["trades"].tolist()
            == monte_carlo["source_trade_count"].tolist()
        )

    def test_long_aggregate_metrics_can_match_despite_entry_level_shift(self) -> None:
        rows = []
        for fill_mode in (FILL_SAME_CLOSE, FILL_NEXT_OPEN):
            for candidate in (
                "LONG_BASE_FIB_PULLBACK_V1",
                LONG_SECONDARY,
                "LONG_BASE_MTF_BULLISH_CONTINUATION_V1",
                LONG_PRIMARY,
            ):
                rows.append(
                    {
                        "fill_mode": fill_mode,
                        "candidate_id": candidate,
                        "trades": 10,
                        "total_result_r": 2.5,
                        "average_result_r": 0.25,
                        "profit_factor": 1.5,
                        "max_drawdown_r": -2.0,
                    }
                )

        self.assertTrue(long_timing_metrics_are_identical(pd.DataFrame(rows)))

    def test_full_orchestration_completes_with_reproduced_inputs(self) -> None:
        manifest_rows = []
        for symbol in ("BTCUSDT", "ETHUSDT", "SOLUSDT"):
            for timeframe in ("15m", "1h", "4h"):
                manifest_rows.append(
                    {
                        "symbol": symbol,
                        "timeframe": timeframe,
                        "sha256": f"{symbol}-{timeframe}",
                        "rows": 1000,
                        "dataset_valid": True,
                    }
                )
        manifest = pd.DataFrame(manifest_rows)
        r2_lineage = pd.DataFrame(
            [
                {
                    "report_name": name,
                    "path": name,
                    "exists": True,
                    "size_bytes": 1,
                    "sha256": name,
                    "rows": 1,
                    "read_error": "",
                    "report_valid": True,
                }
                for name in (
                    "summary",
                    "checks",
                    "dataset_manifest",
                    "short_window_metrics",
                    "long_readiness",
                )
            ]
        )
        long_stage_lineage = pd.DataFrame(
            [
                {
                    "report_name": name,
                    "source_stage": stage,
                    "path": name,
                    "exists": True,
                    "size_bytes": 1,
                    "sha256": name,
                    "rows": 1,
                    "read_error": "",
                    "report_valid": True,
                }
                for name, stage in (
                    (
                        "phase_8_4_historical_metrics",
                        "PHASE_8_4_FULL_HISTORICAL_BASELINE",
                    ),
                    (
                        "phase_8_10_monte_carlo_summary",
                        "PHASE_8_10_POST_OOS_STRESS_COST_MONTE_CARLO_SOURCE",
                    ),
                )
            ]
        )
        timing_rows = []
        r2_window_rows = []
        for symbol in ("BTCUSDT", "ETHUSDT", "SOLUSDT"):
            for quarter in range(12):
                split = f"SPLIT_{quarter}"
                test_start = f"2023-{quarter % 12 + 1:02d}-01"
                base = {
                    "symbol": symbol,
                    "split_name": split,
                    "test_start": test_start,
                    "test_end": "2026-01-01",
                    "test_trades": 2,
                    "test_return": -0.01,
                    "test_profit_factor": 0.9,
                    "test_expectancy_r": -0.1,
                    "test_drawdown": -0.02,
                    "test_win_rate": 0.4,
                }
                timing_rows.append(
                    {
                        **base,
                        "timing_mode": FILL_SAME_CLOSE,
                        "source_mtf_mode": "CLOSED_CANDLE_CORRECTED",
                    }
                )
                timing_rows.append(
                    {
                        **base,
                        "timing_mode": FILL_NEXT_OPEN,
                        "source_mtf_mode": "CLOSED_CANDLE_CORRECTED",
                    }
                )
                r2_window_rows.append(
                    {**base, "timing_mode": "CLOSED_CANDLE_CORRECTED"}
                )
        short_metrics = pd.DataFrame(timing_rows)
        r2_windows = pd.DataFrame(r2_window_rows)
        short_trades = pd.DataFrame(
            [
                {
                    "symbol": "BTCUSDT",
                    "split_name": "SPLIT_0",
                    "signal_time": "2025-01-01 00:00:00",
                    "entry_time": "2025-01-01 00:00:00",
                    "exit_time": "2025-01-01 01:00:00",
                    "entry_price": 100.0,
                    "exit_price": 101.0,
                    "result_r": -1.0,
                    "net_pnl": -10.0,
                    "exit_reason": "STOP_LOSS",
                    "fill_mode": FILL_SAME_CLOSE,
                    "signal_index": 250,
                    "entry_index": 250,
                },
                {
                    "symbol": "BTCUSDT",
                    "split_name": "SPLIT_0",
                    "signal_time": "2025-01-01 00:00:00",
                    "entry_time": "2025-01-01 00:15:00",
                    "exit_time": "2025-01-01 01:00:00",
                    "entry_price": 100.2,
                    "exit_price": 101.2,
                    "result_r": -1.0,
                    "net_pnl": -10.0,
                    "exit_reason": "STOP_LOSS",
                    "fill_mode": FILL_NEXT_OPEN,
                    "signal_index": 250,
                    "entry_index": 251,
                },
            ]
        )
        historical_candidates = (
            ("LONG_BASE_FIB_PULLBACK_V1", 17, -11.5, 0.5, -6.0),
            (LONG_SECONDARY, 21, 4.5, 1.4, -4.0),
            ("LONG_BASE_MTF_BULLISH_CONTINUATION_V1", 14, -7.5, 0.6, -5.0),
            (LONG_PRIMARY, 12, 5.5, 2.1, -2.0),
        )
        long_metrics = pd.DataFrame(
            [
                {
                    "fill_mode": fill_mode,
                    "candidate_id": candidate,
                    "trades": trades,
                    "total_result_r": total_r,
                    "average_result_r": total_r / trades,
                    "profit_factor": profit_factor,
                    "max_drawdown_r": max_drawdown_r,
                }
                for fill_mode in (FILL_SAME_CLOSE, FILL_NEXT_OPEN)
                for candidate, trades, total_r, profit_factor, max_drawdown_r
                in historical_candidates
            ]
        )
        long_trades = pd.DataFrame(
            [
                {
                    "candidate_id": LONG_PRIMARY,
                    "signal_index": 10,
                    "entry_index": 10,
                    "observed_at": "2025-01-01 00:00:00",
                    "entry_time": "2025-01-01 00:00:00",
                    "fill_mode": FILL_SAME_CLOSE,
                },
                {
                    "candidate_id": LONG_PRIMARY,
                    "signal_index": 10,
                    "entry_index": 11,
                    "observed_at": "2025-01-01 00:00:00",
                    "entry_time": "2025-01-01 00:15:00",
                    "fill_mode": FILL_NEXT_OPEN,
                },
            ]
        )
        r2_frames = {
            "summary": pd.DataFrame([{"validation_passed": True}]),
            "checks": pd.DataFrame([{"passed": True}]),
            "dataset_manifest": manifest.copy(),
            "short_window_metrics": r2_windows,
            "long_readiness": pd.DataFrame(
                [
                    {
                        "candidate_id": LONG_PRIMARY,
                        "source_trade_count": 5,
                        "original_total_result_r": 3.0,
                    },
                    {
                        "candidate_id": LONG_SECONDARY,
                        "source_trade_count": 10,
                        "original_total_result_r": 1.5,
                    },
                ]
            ),
        }
        long_stage_frames = {
            "phase_8_4_historical_metrics": long_metrics[
                long_metrics["fill_mode"].eq(FILL_SAME_CLOSE)
            ].drop(columns=["fill_mode"]),
            "phase_8_10_monte_carlo_summary": pd.DataFrame(
                [
                    {
                        "candidate_id": LONG_PRIMARY,
                        "source_trade_count": 5,
                        "original_total_result_r": 3.0,
                    },
                    {
                        "candidate_id": LONG_SECONDARY,
                        "source_trade_count": 10,
                        "original_total_result_r": 1.5,
                    },
                ]
            ),
        }

        with (
            patch(
                "src.validation.signal_to_fill_timing_integrity_audit_v1.load_r2_reports",
                return_value=(r2_frames, r2_lineage),
            ),
            patch(
                "src.validation.signal_to_fill_timing_integrity_audit_v1.load_long_stage_reports",
                return_value=(long_stage_frames, long_stage_lineage),
            ),
            patch(
                "src.validation.signal_to_fill_timing_integrity_audit_v1.prepare_dataset_manifest",
                return_value=manifest,
            ),
            patch(
                "src.validation.signal_to_fill_timing_integrity_audit_v1.find_historical_data_path",
                return_value=Path("data/btcusdt_15m.csv"),
            ),
            patch(
                "src.validation.signal_to_fill_timing_integrity_audit_v1.run_short_timing_audit",
                return_value=(short_metrics, short_trades),
            ),
            patch(
                "src.validation.signal_to_fill_timing_integrity_audit_v1.run_long_timing_audit",
                return_value=(long_metrics, long_trades, pd.DataFrame()),
            ),
            patch(
                "src.validation.signal_to_fill_timing_integrity_audit_v1.write_outputs"
            ),
        ):
            result = run_signal_to_fill_timing_integrity_audit()

        summary = result["summary"].iloc[0]
        self.assertTrue(summary["audit_completed"])
        self.assertTrue(summary["validation_passed"])
        self.assertEqual(
            summary["validation_decision"],
            "PHASE_10_42R_2A_SIGNAL_TO_FILL_TIMING_AUDIT_COMPLETED",
        )
        self.assertTrue(summary["long_next_open_metrics_unchanged"])
        self.assertEqual(
            summary["long_timing_status"],
            "NEXT_OPEN_HISTORICAL_METRICS_UNCHANGED_NOT_APPROVED",
        )
        self.assertFalse(result["checks"]["blocker"].astype(bool).any())


if __name__ == "__main__":
    unittest.main()
