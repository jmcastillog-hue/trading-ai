from __future__ import annotations

import inspect
import tempfile
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

from src.audit import (
    frozen_recovery_candidate_independent_result_audit_and_disposition_v1 as audit,
)


class IndependentResultAuditTests(unittest.TestCase):
    def test_phase_and_source_anchors_are_exact(self) -> None:
        self.assertEqual(audit.PHASE, "10.42R.2L")
        self.assertEqual(audit.SOURCE_PHASE_2K_COMMIT, "0a5440a70e91e833925a4147ac2863baa7666b1e")
        self.assertEqual(audit.SOURCE_PHASE_2K_BUNDLE_ROOT_SHA256, "2938dcf9596281a8416b9ecd6f7431cbebee89559063bfe100a11258f76cbd02")

    def test_source_and_output_artifact_inventory_is_exact(self) -> None:
        self.assertEqual(len(audit.AUDIT_ARTIFACTS), 12)
        self.assertEqual(len(audit.OUTPUT_ARTIFACTS), 7)
        self.assertEqual(audit.AUDIT_ARTIFACTS[-1], "run_summary.json")

    def test_variant_registry_is_exact(self) -> None:
        self.assertEqual(len(audit.VARIANT_IDS), 6)
        self.assertEqual(len(set(audit.VARIANT_IDS)), 6)

    def test_parse_bool_accepts_canonical_values(self) -> None:
        self.assertTrue(audit.parse_bool(True))
        self.assertTrue(audit.parse_bool("true"))
        self.assertFalse(audit.parse_bool(False))
        self.assertFalse(audit.parse_bool("False"))

    def test_parse_bool_rejects_unknown_value(self) -> None:
        with self.assertRaises(audit.IndependentAuditFailure):
            audit.parse_bool("maybe")

    def test_profit_factor_is_deterministic(self) -> None:
        self.assertAlmostEqual(audit.profit_factor([2.0, -1.0, 1.0]), 3.0)
        self.assertEqual(audit.profit_factor([]), 0.0)

    def test_max_drawdown_is_deterministic(self) -> None:
        self.assertAlmostEqual(audit.calculate_max_drawdown_r([1.0, -2.0, 0.5]), -2.0)

    def test_holm_tie_break_uses_evaluation_order(self) -> None:
        rows = [
            {"evaluation_order": 2, "unadjusted_p_value": 0.01},
            {"evaluation_order": 1, "unadjusted_p_value": 0.01},
        ]
        adjusted = audit.holm_adjust_p_values(rows)
        by_order = {row["evaluation_order"]: row for row in adjusted}
        self.assertEqual(by_order[1]["holm_rank"], 1)
        self.assertEqual(by_order[2]["holm_rank"], 2)

    def test_bootstrap_is_deterministic(self) -> None:
        frame = pd.DataFrame(
            {
                "symbol": ["BTCUSDT", "ETHUSDT"],
                "split_name": [audit.SPLIT_IDS[0], audit.SPLIT_IDS[1]],
                "normalized_net_result_r": [0.5, -0.25],
            }
        )
        first = audit.cluster_bootstrap_p_value(frame, evaluation_order=1, resamples=100)
        second = audit.cluster_bootstrap_p_value(frame, evaluation_order=1, resamples=100)
        self.assertEqual(first, second)

    def test_normalized_cost_grid_applies_five_profiles_once(self) -> None:
        trade = pd.DataFrame(
            [
                {
                    "evaluation_order": 1,
                    "family_id": audit.FAMILY_IDS[0],
                    "variant_id": audit.VARIANT_IDS[0],
                    "symbol": "BTCUSDT",
                    "split_name": audit.SPLIT_IDS[0],
                    "signal_time_utc": "2023-01-01T00:00:00Z",
                    "entry_time_utc": "2023-01-01T00:15:00Z",
                    "exit_time_utc": "2023-01-01T00:30:00Z",
                    "signal_close": 100.0,
                    "signal_atr14": 1.0,
                    "trend_regime": audit.EXPECTED_REGIME_COMBINATIONS[0],
                    "risk_pct_of_entry": 0.01,
                    "frictionless_gross_result_r": 2.5,
                    "result_eligible": True,
                    "source_trade_row": 0,
                }
            ]
        )
        normalized = audit.build_normalized_trade_profiles(trade)
        self.assertEqual(len(normalized), 5)
        self.assertTrue(normalized["cost_application_count"].eq(1).all())

    def test_normalized_cost_formula_is_exact(self) -> None:
        trade = pd.DataFrame(
            [
                {
                    "evaluation_order": 1,
                    "family_id": audit.FAMILY_IDS[0],
                    "variant_id": audit.VARIANT_IDS[0],
                    "symbol": "BTCUSDT",
                    "split_name": audit.SPLIT_IDS[0],
                    "signal_time_utc": "2023-01-01T00:00:00Z",
                    "entry_time_utc": "2023-01-01T00:15:00Z",
                    "exit_time_utc": "2023-01-01T00:30:00Z",
                    "signal_close": 100.0,
                    "signal_atr14": 1.0,
                    "trend_regime": audit.EXPECTED_REGIME_COMBINATIONS[0],
                    "risk_pct_of_entry": 0.01,
                    "frictionless_gross_result_r": 2.5,
                    "result_eligible": True,
                    "source_trade_row": 0,
                }
            ]
        )
        normalized = audit.build_normalized_trade_profiles(trade)
        base = normalized.loc[normalized["cost_profile"].eq(audit.PRIMARY_COST_PROFILE)].iloc[0]
        self.assertAlmostEqual(float(base["profile_total_cost_r"]), 0.16)
        self.assertAlmostEqual(float(base["normalized_net_result_r"]), 2.34)

    def test_metric_grid_has_450_rows(self) -> None:
        empty = pd.DataFrame(
            columns=[
                "variant_id", "cost_profile", "symbol", "split_name",
                "normalized_net_result_r", "frictionless_gross_result_r",
                "exit_time_utc", "entry_time_utc", "source_trade_row",
                "calendar_year", "volatility_tercile", "trend_regime", "family_id",
            ]
        )
        metrics = audit.build_independent_metric_table(empty)
        self.assertEqual(len(metrics), 450)

    def test_empty_multiplicity_publishes_six_rows(self) -> None:
        empty = pd.DataFrame(
            columns=["variant_id", "cost_profile", "symbol", "split_name", "normalized_net_result_r"]
        )
        table = audit.build_independent_multiplicity_table(empty)
        self.assertEqual(len(table), 6)

    def test_disposition_rejects_failed_variant(self) -> None:
        rows = []
        for order, variant_id in enumerate(audit.VARIANT_IDS, start=1):
            for gate_order in range(1, 11):
                rows.append(
                    {
                        "evaluation_order": order,
                        "variant_id": variant_id,
                        "gate_order": gate_order,
                        "gate_id": f"GATE_{gate_order:03d}",
                        "metric": "x",
                        "passed": gate_order != 1,
                    }
                )
        disposition = audit.build_variant_disposition(pd.DataFrame(rows))
        self.assertTrue(disposition["failed_gate_count"].eq(1).all())
        self.assertTrue(disposition["lockbox_opening_allowed"].eq(False).all())

    def test_phase_2k_internal_check_count_is_exact_twelve(self) -> None:
        self.assertEqual(audit.SOURCE_PHASE_2K_INTERNAL_CHECK_COUNT, 12)

    def test_frames_equivalent_accepts_csv_aggregate_rounding(self) -> None:
        left = pd.DataFrame({"x": [1.0]})
        right = pd.DataFrame({"x": [1.0 + 5e-10]})
        valid, _ = audit.frames_equivalent(left, right)
        self.assertTrue(valid)

    def test_frames_equivalent_rejects_material_numeric_drift(self) -> None:
        left = pd.DataFrame({"x": [1.0]})
        right = pd.DataFrame({"x": [1.0 + 1e-6]})
        valid, _ = audit.frames_equivalent(left, right)
        self.assertFalse(valid)

    def test_frames_equivalent_rejects_column_drift(self) -> None:
        valid, _ = audit.frames_equivalent(pd.DataFrame({"x": [1]}), pd.DataFrame({"y": [1]}))
        self.assertFalse(valid)

    def test_atomic_publish_is_idempotent(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            first = root / "first"
            final = root / "final"
            first.mkdir()
            (first / "x.txt").write_text("x\n", encoding="utf-8")
            self.assertEqual(audit._atomic_publish(first, final), "NEW_AUDIT_ATOMICALLY_PUBLISHED")
            second = root / "second"
            second.mkdir()
            (second / "x.txt").write_text("x\n", encoding="utf-8")
            self.assertEqual(audit._atomic_publish(second, final), "IDEMPOTENT_EXISTING_AUDIT_VERIFIED")

    def test_final_decision_closes_line_without_lockbox(self) -> None:
        self.assertIn("ALL_VARIANTS_REJECTED", audit.FINAL_DECISION)
        self.assertIn("NO_LOCKBOX_OPENED", audit.FINAL_DECISION)

    def test_recommended_route_is_not_another_repair_phase(self) -> None:
        self.assertTrue(audit.RECOMMENDED_NEXT_ROUTE.startswith("RETURN_TO_PHASE_10_42R_MASTER_DISPOSITION"))

    def test_source_contains_no_backtest_import(self) -> None:
        source = inspect.getsource(audit)
        self.assertNotIn("src.backtesting", source)
        self.assertNotIn("run_controlled_known_evidence_evaluation(", source)

    def test_no_operational_permissions_are_exposed(self) -> None:
        source = inspect.getsource(audit)
        self.assertNotIn('paper_trade_execution_allowed": True', source)
        self.assertNotIn('real_capital_allowed": True', source)

    def test_output_root_is_deterministic(self) -> None:
        hashes = {"a": "0" * 64, "b": "1" * 64}
        first = audit.sha256_bytes(audit.canonical_json(hashes).encode("utf-8"))
        second = audit.sha256_bytes(audit.canonical_json(hashes).encode("utf-8"))
        self.assertEqual(first, second)

    def test_normalized_source_hash_ignores_line_endings(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "x.py"
            path.write_bytes(b"a\r\nb\r\n")
            first = audit.normalized_source_sha256(path)
            path.write_bytes(b"a\nb\n")
            second = audit.normalized_source_sha256(path)
            self.assertEqual(first, second)

    def test_cost_profile_names_are_unique(self) -> None:
        names = [profile.name for profile in audit.COST_PROFILES]
        self.assertEqual(len(names), 5)
        self.assertEqual(len(set(names)), 5)


if __name__ == "__main__":
    unittest.main()
