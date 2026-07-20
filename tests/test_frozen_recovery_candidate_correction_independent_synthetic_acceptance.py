from __future__ import annotations

import ast
import dataclasses
import unittest
from pathlib import Path

from src.analysis import frozen_recovery_candidate_implementation_v2 as corrected
from src.validation import frozen_recovery_candidate_correction_independent_synthetic_acceptance_v1 as acceptance


class FrozenRecoveryCandidateCorrectionIndependentSyntheticAcceptanceTests(
    unittest.TestCase
):
    def test_corrected_source_hash_is_exact(self) -> None:
        self.assertEqual(
            acceptance.normalized_source_sha256(
                acceptance.CORRECTED_SOURCE_PATH
            ),
            acceptance.EXPECTED_CORRECTED_SOURCE_SHA256,
        )

    def test_registry_is_exact_and_deterministic(self) -> None:
        first = corrected.build_verified_implementations()
        second = corrected.build_verified_implementations()
        self.assertEqual(first, second)
        self.assertEqual(len(first), 6)
        self.assertEqual(
            tuple(item.variant_id for item in first),
            acceptance.EXPECTED_VARIANT_IDS,
        )

    def test_preflight_passes_without_synthetic_evaluation(self) -> None:
        result = acceptance.validate_phase_10_42r_2g(
            preflight_only=True
        )
        summary = result["summary"]
        self.assertTrue(summary["validation_passed"])
        self.assertEqual(summary["validation_decision"], "PREFLIGHT_PASSED")
        self.assertEqual(summary["preflight_check_count"], 8)
        self.assertEqual(summary["synthetic_case_count"], 0)
        self.assertFalse(summary["acceptance_completed"])

    def test_full_acceptance_passes_all_39_synthetic_cases(self) -> None:
        result = acceptance.validate_phase_10_42r_2g()
        summary = result["summary"]
        self.assertTrue(summary["validation_passed"])
        self.assertEqual(
            summary["validation_decision"],
            acceptance.ACCEPTED_DECISION,
        )
        self.assertEqual(summary["synthetic_case_count"], 39)
        self.assertEqual(summary["total_check_count"], 47)
        self.assertEqual(summary["failed_check_count"], 0)
        self.assertEqual(summary["blocker_count"], 0)
        self.assertTrue(summary["acceptance_completed"])

    def test_acceptance_is_deterministic(self) -> None:
        first = acceptance.validate_phase_10_42r_2g()
        second = acceptance.validate_phase_10_42r_2g()
        self.assertEqual(first, second)

    def test_all_six_variants_have_independent_positive_case(self) -> None:
        result = acceptance.validate_phase_10_42r_2g()
        positive_names = {
            check["check_name"]
            for check in result["checks"]
            if check["group"] == "positive_family_acceptance"
        }
        self.assertEqual(len(positive_names), 6)
        for variant_id in acceptance.EXPECTED_VARIANT_IDS:
            self.assertIn(f"positive_signal_{variant_id}", positive_names)

    def test_correction_specific_boundaries_are_accepted(self) -> None:
        result = acceptance.validate_phase_10_42r_2g()
        by_name = {
            check["check_name"]: check
            for check in result["checks"]
        }
        required = {
            "f01_close_equality_blocks_RCV_SHORT_UPSIDE_SWEEP_REVERSAL_F01_N48_V01",
            "f01_close_equality_blocks_RCV_SHORT_UPSIDE_SWEEP_REVERSAL_F01_N96_V02",
            "infinite_signal_unit_blocks",
            "fractional_bar_indexes_block",
            "boolean_bar_indexes_block",
            "nonfinite_signal_stop_blocks",
            "nonfinite_accepted_order_blocks_exit",
            "tampered_implementation_identity_raises",
        }
        self.assertTrue(required.issubset(by_name))
        self.assertTrue(all(by_name[name]["passed"] for name in required))

    def test_order_contract_cases_pass(self) -> None:
        result = acceptance.validate_phase_10_42r_2g()
        order_checks = [
            check
            for check in result["checks"]
            if check["group"] in {"order_acceptance", "order_fail_closed"}
        ]
        self.assertEqual(len(order_checks), 9)
        self.assertTrue(all(check["passed"] for check in order_checks))

    def test_exit_contract_cases_pass(self) -> None:
        result = acceptance.validate_phase_10_42r_2g()
        exit_checks = [
            check
            for check in result["checks"]
            if check["group"] in {
                "exit_acceptance",
                "exit_boundary_acceptance",
                "exit_fail_closed",
            }
        ]
        self.assertEqual(len(exit_checks), 7)
        self.assertTrue(all(check["passed"] for check in exit_checks))

    def test_tampered_implementation_identity_raises_directly(self) -> None:
        implementation = corrected.build_verified_implementations()[0]
        tampered = dataclasses.replace(
            implementation,
            parameter_json=(
                '{"prior_high_lookback_bars":1,'
                '"stop_atr_buffer":0.25,'
                '"wick_to_body_minimum":1.0}'
            ),
        )
        with self.assertRaises(corrected.FrozenSpecificationError):
            corrected.evaluate_frozen_signal(
                tampered,
                history=acceptance._flat_history(),
                current=acceptance._f01_positive_current(),
                context=acceptance._allowed_context(),
            )

    def test_no_real_data_metrics_comparison_or_winner(self) -> None:
        summary = acceptance.validate_phase_10_42r_2g()["summary"]
        for key in (
            "real_data_access_count",
            "holdout_access_count",
            "historical_evaluation_count",
            "performance_metric_count",
            "candidate_comparison_count",
            "candidate_ranking_count",
            "report_artifact_write_count",
            "permissions_enabled_count",
        ):
            self.assertEqual(summary[key], 0, key)
        self.assertFalse(summary["winner_selected"])

    def test_all_permissions_remain_false(self) -> None:
        permissions = acceptance.validate_phase_10_42r_2g()["permissions"]
        self.assertTrue(permissions)
        self.assertTrue(all(value is False for value in permissions.values()))

    def test_acceptance_source_does_not_import_phase_2f_review(self) -> None:
        path = Path(acceptance.__file__)
        tree = ast.parse(path.read_text(encoding="utf-8"))
        imported_modules: list[str] = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported_modules.extend(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported_modules.append(node.module)
        self.assertFalse(
            any(
                "frozen_recovery_candidate_independent_code_review_v1"
                in module
                for module in imported_modules
            )
        )


if __name__ == "__main__":
    unittest.main()
