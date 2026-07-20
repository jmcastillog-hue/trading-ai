from __future__ import annotations

import ast
import inspect
import unittest
from dataclasses import replace
from pathlib import Path

from src.validation import (
    frozen_recovery_candidate_controlled_historical_evaluation_preregistration_v1
    as prereg,
)


class ControlledHistoricalEvaluationPreregistrationTests(unittest.TestCase):
    def test_source_anchors_are_exact(self) -> None:
        root = Path.cwd()
        for relative_path, expected_hash in prereg.EXPECTED_SOURCE_HASHES.items():
            path = root / relative_path
            self.assertTrue(path.is_file(), relative_path)
            self.assertEqual(
                prereg.normalized_source_sha256(path),
                expected_hash,
                relative_path,
            )

    def test_source_is_not_runtime_or_backtest_code(self) -> None:
        source = inspect.getsource(prereg)
        tree = ast.parse(source)
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.extend(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                imports.append(node.module or "")
        forbidden_prefixes = (
            "pandas",
            "numpy",
            "scipy",
            "src.backtesting",
            "src.exchange",
            "src.analysis",
            "src.execution",
            "src.long_side",
            "src.journal",
        )
        self.assertFalse(
            any(
                name == prefix or name.startswith(prefix + ".")
                for name in imports
                for prefix in forbidden_prefixes
            ),
            imports,
        )

    def test_dataset_slots_form_exact_three_by_three_grid(self) -> None:
        slots = prereg.build_dataset_slots()
        self.assertEqual(len(slots), 9)
        self.assertEqual(
            {(row[0], row[1]) for row in slots},
            {
                (symbol, timeframe)
                for symbol in prereg.SYMBOLS
                for timeframe in prereg.TIMEFRAMES
            },
        )

    def test_evidence_windows_are_half_open_and_lockboxes_sealed(self) -> None:
        windows = prereg.build_evidence_windows()
        self.assertEqual(len(windows), 3)
        self.assertEqual(windows[0][1], "2022-01-01T00:00:00+00:00")
        self.assertEqual(windows[0][2], "2026-01-01T00:00:00+00:00")
        self.assertEqual(windows[1][2], windows[2][1])
        self.assertIn("SEALED", windows[1][3])
        self.assertIn("SEALED", windows[2][3])

    def test_five_cost_profiles_are_exact(self) -> None:
        profiles = prereg.build_cost_profiles()
        self.assertEqual(len(profiles), 5)
        self.assertEqual(profiles[0][:4], (
            "BINANCE_SCALP_BASE_ESTIMATE", 0.0008, 0.0004, 0.0004
        ))
        self.assertEqual(profiles[1][:4], (
            "BINANCE_SCALP_STRESS_ESTIMATE", 0.0012, 0.0008, 0.0008
        ))
        self.assertEqual(profiles[-1][:4], (
            "EXTREME_COST_STRESS_TEST", 0.0015, 0.0080, 0.0020
        ))

    def test_multiplicity_is_one_pool_of_six(self) -> None:
        protocol = prereg.build_protocol()
        multiplicity = protocol.multiplicity
        self.assertEqual(multiplicity[:4], (6, 3, 6, 1))
        self.assertEqual(
            multiplicity[4],
            "STEP_DOWN_HOLM_BONFERRONI",
        )
        self.assertEqual(multiplicity[5], 0.05)
        self.assertEqual(multiplicity[7], prereg.VARIANTS)
        self.assertFalse(multiplicity[8])

    def test_promotion_gates_lock_known_thresholds(self) -> None:
        gates = prereg.build_promotion_gates()
        self.assertEqual(len(gates), 10)
        self.assertEqual(gates[0][3], "100")
        self.assertEqual(gates[1][3], "20")
        self.assertEqual(gates[2][3], "1.05")
        self.assertEqual(gates[7][3], "1.00")
        self.assertEqual(gates[8][3], "0.05")

    def test_thirty_rules_are_locked_and_immutable(self) -> None:
        rules = prereg.build_rules()
        self.assertEqual(len(rules), 30)
        self.assertEqual(rules[0][0], "PR-001")
        self.assertEqual(rules[-1][0], "HPR-030")
        self.assertTrue(all(row[3] for row in rules))
        self.assertTrue(all(not row[4] for row in rules))

    def test_all_permissions_are_false(self) -> None:
        self.assertTrue(prereg.PERMISSIONS)
        self.assertTrue(all(v is False for v in prereg.PERMISSIONS.values()))

    def test_protocol_is_deterministic(self) -> None:
        first = prereg.build_protocol()
        second = prereg.build_protocol()
        self.assertEqual(first, second)
        self.assertEqual(
            prereg.protocol_sha256(first),
            prereg.protocol_sha256(second),
        )

    def test_tampered_protocol_is_rejected(self) -> None:
        protocol = prereg.build_protocol()
        tampered = replace(protocol, fixed_reward_to_risk=3.0)
        self.assertIn(
            "fixed_reward_to_risk",
            prereg.validate_protocol_object(tampered),
        )

    def test_preflight_passes_without_data_access(self) -> None:
        result = prereg.require_valid_preregistration(preflight_only=True)
        summary = result["summary"]
        self.assertEqual(summary["validation_decision"], "PREFLIGHT_PASSED")
        self.assertTrue(summary["validation_passed"])
        self.assertEqual(summary["real_data_content_read_count"], 0)
        self.assertEqual(summary["historical_evaluation_count"], 0)
        self.assertEqual(summary["backtest_execution_count"], 0)
        self.assertEqual(summary["performance_metric_count"], 0)
        self.assertFalse(summary["historical_evaluation_allowed"])

    def test_full_preregistration_locks_without_evaluation(self) -> None:
        result = prereg.require_valid_preregistration()
        summary = result["summary"]
        self.assertEqual(
            summary["validation_decision"],
            "CONTROLLED_HISTORICAL_EVALUATION_PREREGISTRATION_LOCKED",
        )
        self.assertTrue(summary["validation_passed"])
        self.assertTrue(summary["preregistration_locked"])
        self.assertEqual(summary["dataset_slot_count"], 9)
        self.assertEqual(summary["variant_count"], 6)
        self.assertEqual(summary["family_count"], 3)
        self.assertEqual(summary["cost_profile_count"], 5)
        self.assertEqual(summary["promotion_gate_count"], 10)
        self.assertEqual(summary["preregistration_rule_count"], 30)
        self.assertEqual(summary["failed_check_count"], 0)
        self.assertEqual(summary["blocker_count"], 0)
        self.assertEqual(summary["real_data_content_read_count"], 0)
        self.assertEqual(summary["historical_evaluation_count"], 0)
        self.assertEqual(summary["retrospective_lockbox_access_count"], 0)
        self.assertEqual(summary["prospective_holdout_access_count"], 0)
        self.assertEqual(summary["candidate_comparison_count"], 0)
        self.assertEqual(summary["candidate_ranking_count"], 0)
        self.assertEqual(summary["winner_selection_count"], 0)
        self.assertEqual(summary["permissions_enabled_count"], 0)

    def test_full_preregistration_is_deterministic(self) -> None:
        first = prereg.require_valid_preregistration()
        second = prereg.require_valid_preregistration()
        self.assertEqual(first["summary"], second["summary"])
        self.assertEqual(first["checks"], second["checks"])
        self.assertEqual(first["protocol"], second["protocol"])


if __name__ == "__main__":
    unittest.main()
