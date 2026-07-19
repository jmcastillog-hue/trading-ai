from __future__ import annotations

import unittest
from unittest.mock import patch

import pandas as pd

from src.execution.cost_aware_filter_v1 import CostProfile, build_cost_profiles
from src.execution.normalized_cost_accounting_v1 import (
    ACCOUNTING_CONTRACT,
    DRAWDOWN_ORDER_CONTRACT,
    WINDOW_UNIT_CONTRACT,
    accounting_identity_holds,
    apply_single_cost_profile,
    normalize_short_trades,
    reconstruct_short_frictionless_trade,
    summarize_normalized_trades,
)
from src.validation.cost_accounting_normalization_and_strategy_recovery_preregistration_v1 import (
    FILL_NEXT_OPEN,
    NEXT_PHASE,
    SAFETY_FLAGS,
    build_holdout_contract,
    build_recovery_preregistration,
    validate_phase_10_42r_2b,
)


def synthetic_short_trade() -> dict:
    raw_entry = 100.0
    raw_exit = 98.0
    units = 10.0
    risk_amount = 20.0
    spread_rate = 0.0002
    fee_rate = 0.001
    engine_entry = raw_entry * (1.0 - spread_rate / 2.0)
    engine_exit = raw_exit * (1.0 + spread_rate / 2.0)
    gross_pnl = (engine_entry - engine_exit) * units
    fees = (engine_entry + engine_exit) * units * fee_rate
    net_pnl = gross_pnl - fees
    return {
        "symbol": "BTCUSDT",
        "split_name": "TEST_SPLIT",
        "fill_mode": FILL_NEXT_OPEN,
        "direction": "SHORT",
        "entry_time": "2025-06-01 00:15:00",
        "exit_time": "2025-06-01 01:15:00",
        "raw_entry_reference": raw_entry,
        "raw_exit_reference": raw_exit,
        "entry_price": engine_entry,
        "exit_price": engine_exit,
        "position_units": units,
        "risk_amount": risk_amount,
        "gross_pnl": gross_pnl,
        "fees": fees,
        "net_pnl": net_pnl,
        "result_r": net_pnl / risk_amount,
    }


class NormalizedCostAccountingTests(unittest.TestCase):
    def test_internal_engine_result_reconciles_to_frictionless_basis(self) -> None:
        reconstructed = reconstruct_short_frictionless_trade(
            pd.Series(synthetic_short_trade())
        )

        self.assertEqual(reconstructed["accounting_contract"], ACCOUNTING_CONTRACT)
        self.assertAlmostEqual(reconstructed["frictionless_gross_result_r"], 1.0)
        self.assertAlmostEqual(reconstructed["internal_reconciliation_delta_r"], 0.0)
        self.assertGreater(reconstructed["embedded_spread_result_r"], 0.0)
        self.assertGreater(reconstructed["internal_fee_result_r"], 0.0)

    def test_single_profile_starts_from_gross_not_internal_net(self) -> None:
        profile = CostProfile(
            name="TEST_PROFILE",
            platform="TEST",
            mode="TEST",
            fee_pct_round_trip=0.001,
            spread_pct_round_trip=0.001,
            slippage_pct_round_trip=0.001,
            funding_or_time_cost_pct=0.0,
            safety_buffer_pct=0.001,
            default_risk_pct=0.02,
            risk_per_trade_pct=0.01,
        )
        result = apply_single_cost_profile(
            pd.Series(synthetic_short_trade()),
            profile,
        )

        self.assertEqual(result["cost_application_count"], 1)
        self.assertAlmostEqual(
            result["normalized_net_result_r"],
            result["frictionless_gross_result_r"] - result["profile_total_cost_r"],
        )
        self.assertAlmostEqual(
            result["normalization_delta_vs_legacy_r"],
            result["embedded_internal_cost_r"],
        )
        self.assertGreater(
            result["normalized_net_result_r"],
            result["legacy_double_counted_result_r"],
        )
        self.assertFalse(result["normalized_cost_decision_allowed"])
        self.assertFalse(result["candidate_reclassification_allowed"])

    def test_normalized_table_applies_all_profiles_exactly_once(self) -> None:
        trades = pd.DataFrame([synthetic_short_trade(), synthetic_short_trade()])
        profiles = build_cost_profiles()

        normalized = normalize_short_trades(trades, profiles)
        summary = summarize_normalized_trades(normalized)

        self.assertEqual(len(normalized), len(trades) * len(profiles))
        self.assertEqual(normalized["cost_profile"].nunique(), 5)
        self.assertTrue(normalized["cost_application_count"].eq(1).all())
        self.assertTrue(accounting_identity_holds(normalized))
        self.assertFalse(summary["normalized_cost_decision_allowed"].any())

    def test_summary_drawdown_uses_realized_time_not_source_order(self) -> None:
        trades = []
        for symbol, exit_time in (
            ("BTCUSDT", "2025-06-03 01:15:00"),
            ("ETHUSDT", "2025-06-01 01:15:00"),
            ("SOLUSDT", "2025-06-02 01:15:00"),
        ):
            trade = synthetic_short_trade()
            trade["symbol"] = symbol
            trade["exit_time"] = exit_time
            trades.append(trade)
        normalized = normalize_short_trades(
            pd.DataFrame(trades),
            [build_cost_profiles()[0]],
        )
        normalized["normalized_net_result_r"] = [-5.0, 10.0, -7.0]

        summary = summarize_normalized_trades(normalized)
        aggregate = summary[summary["scope"].eq("ALL_SYMBOLS")].iloc[0]

        self.assertEqual(
            aggregate["drawdown_order_contract"],
            DRAWDOWN_ORDER_CONTRACT,
        )
        self.assertAlmostEqual(aggregate["normalized_max_drawdown_r"], -12.0)

    def test_summary_counts_zero_trade_symbol_windows(self) -> None:
        trades = []
        for symbol, split_name, exit_time in (
            ("BTCUSDT", "WINDOW_1", "2025-06-01 01:15:00"),
            ("ETHUSDT", "WINDOW_1", "2025-06-02 01:15:00"),
            ("ETHUSDT", "WINDOW_2", "2025-06-03 01:15:00"),
        ):
            trade = synthetic_short_trade()
            trade["symbol"] = symbol
            trade["split_name"] = split_name
            trade["exit_time"] = exit_time
            trades.append(trade)
        normalized = normalize_short_trades(
            pd.DataFrame(trades),
            [build_cost_profiles()[0]],
        )
        normalized["normalized_net_result_r"] = [1.0, 1.0, 1.0]

        summary = summarize_normalized_trades(normalized)
        aggregate = summary[summary["scope"].eq("ALL_SYMBOLS")].iloc[0]
        btc = summary[summary["scope"].eq("BTCUSDT")].iloc[0]

        self.assertEqual(aggregate["window_unit_contract"], WINDOW_UNIT_CONTRACT)
        self.assertEqual(aggregate["configured_window_rows"], 4)
        self.assertEqual(aggregate["observed_window_rows"], 3)
        self.assertEqual(aggregate["zero_trade_window_rows"], 1)
        self.assertEqual(aggregate["positive_window_rows"], 3)
        self.assertAlmostEqual(aggregate["positive_window_rate"], 0.75)
        self.assertEqual(btc["configured_window_rows"], 2)
        self.assertEqual(btc["zero_trade_window_rows"], 1)

    def test_missing_raw_exit_reference_fails_closed(self) -> None:
        trades = pd.DataFrame([synthetic_short_trade()]).drop(
            columns=["raw_exit_reference"]
        )
        with self.assertRaisesRegex(ValueError, "raw_exit_reference"):
            normalize_short_trades(trades, build_cost_profiles())

    def test_preregistration_and_holdouts_are_locked(self) -> None:
        preregistration = build_recovery_preregistration()
        holdouts = build_holdout_contract()

        self.assertEqual(len(preregistration), 16)
        self.assertTrue(preregistration["preregistered"].all())
        self.assertFalse(preregistration["mutable_after_real_run"].any())
        self.assertFalse(holdouts["access_allowed"].any())
        self.assertTrue(holdouts["must_be_absent_in_phase_2b"].all())

    def test_all_safety_permissions_remain_false(self) -> None:
        self.assertTrue(SAFETY_FLAGS)
        self.assertFalse(any(SAFETY_FLAGS.values()))

    def test_full_orchestration_completes_without_reclassification(self) -> None:
        source_frames = {
            "summary": pd.DataFrame(
                [
                    {
                        "audit_completed": True,
                        "validation_passed": True,
                        "blocker_count": 0,
                        "short_next_open_trades": 1,
                    }
                ]
            ),
            "checks": pd.DataFrame(
                [{"check_name": "all_good", "passed": True, "blocker": False}]
            ),
            "short_timing_trades": pd.DataFrame([synthetic_short_trade()]),
        }
        lineage = pd.DataFrame(
            [
                {
                    "report_name": name,
                    "path": name,
                    "exists": True,
                    "size_bytes": 1,
                    "sha256": name,
                    "rows": len(frame),
                    "missing_columns": "",
                    "read_error": "",
                    "report_valid": True,
                }
                for name, frame in source_frames.items()
            ]
        )

        with (
            patch(
                "src.validation.cost_accounting_normalization_and_strategy_recovery_preregistration_v1.load_r2a_reports",
                return_value=(source_frames, lineage),
            ),
            patch(
                "src.validation.cost_accounting_normalization_and_strategy_recovery_preregistration_v1.write_outputs"
            ),
            patch(
                "src.validation.cost_accounting_normalization_and_strategy_recovery_preregistration_v1.SHORT_SYMBOL_COHORT",
                ("BTCUSDT",),
            ),
            patch(
                "src.validation.cost_accounting_normalization_and_strategy_recovery_preregistration_v1.SHORT_WALK_FORWARD_SPLITS",
                ("TEST_SPLIT",),
            ),
        ):
            result = validate_phase_10_42r_2b()

        summary = result["summary"].iloc[0]
        self.assertTrue(summary["audit_completed"])
        self.assertTrue(summary["validation_passed"])
        self.assertTrue(summary["normalization_contract_validated"])
        self.assertFalse(summary["normalized_cost_decision_published"])
        self.assertFalse(summary["candidate_reclassified"])
        self.assertEqual(summary["recommended_next_phase"], NEXT_PHASE)
        self.assertFalse(result["checks"]["blocker"].astype(bool).any())


if __name__ == "__main__":
    unittest.main()
