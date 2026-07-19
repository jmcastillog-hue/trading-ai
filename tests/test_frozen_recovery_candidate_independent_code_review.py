from __future__ import annotations

from dataclasses import replace
import json
import math
import unittest
from unittest.mock import patch

import src.analysis.frozen_recovery_candidate_implementation_v2 as corrected
import src.validation.frozen_recovery_candidate_independent_code_review_v1 as review


class FrozenRecoveryCandidateIndependentCodeReviewTests(unittest.TestCase):
    def setUp(self) -> None:
        self.implementations = corrected.build_verified_implementations()
        self.first = self.implementations[0]
        self.history = review._flat_history()
        self.context = review._context()

    def test_authoritative_phase_2e_commit_is_frozen(self) -> None:
        self.assertEqual(
            review.SOURCE_PHASE_2E_COMMIT,
            "7d7f8ee81156b1858a636b586eb5636b34b1c801",
        )

    def test_phase_2d_root_and_source_are_exact(self) -> None:
        self.assertEqual(
            corrected.verify_phase_2d_specification_root(),
            review.PHASE_2D_ROOT_SHA256,
        )
        self.assertEqual(
            review.normalized_source_sha256(review.PHASE_2D_SOURCE),
            review.PHASE_2D_SOURCE_SHA256,
        )

    def test_phase_2e_baseline_source_is_unchanged(self) -> None:
        self.assertEqual(
            review.normalized_source_sha256(review.PHASE_2E_SOURCE),
            review.PHASE_2E_SOURCE_SHA256,
        )

    def test_corrected_source_hash_is_exact(self) -> None:
        self.assertEqual(
            review.normalized_source_sha256(review.PHASE_2F_CORRECTED_SOURCE),
            review.PHASE_2F_CORRECTED_SOURCE_SHA256,
        )

    def test_source_is_static_and_synthetic_only(self) -> None:
        valid, details = review._source_is_isolated_and_static(
            review.PHASE_2F_CORRECTED_SOURCE
        )
        self.assertTrue(valid, details)

    def test_f01_close_equality_now_blocks(self) -> None:
        decision = corrected.evaluate_frozen_signal(
            self.first,
            history=self.history,
            current=review._f01_close_equality(),
            context=self.context,
        )
        self.assertFalse(decision.signal)
        self.assertEqual(decision.reason, "UPSIDE_SWEEP_RULE_BLOCKED")

    def test_f01_strict_positive_still_signals_for_both_variants(self) -> None:
        for implementation in self.implementations[:2]:
            decision = corrected.evaluate_frozen_signal(
                implementation,
                history=self.history,
                current=review._f01_positive(),
                context=self.context,
            )
            self.assertTrue(decision.signal, implementation.variant_id)

    def test_all_six_variants_have_positive_synthetic_case(self) -> None:
        decisions = tuple(review._positive_signal(item) for item in self.implementations)
        self.assertEqual(len(decisions), 6)
        self.assertTrue(all(item.signal for item in decisions))

    def test_tampered_implementation_identity_raises(self) -> None:
        parameters = self.first.parameters
        parameters["prior_high_lookback_bars"] = 1
        tampered = replace(
            self.first,
            parameter_json=json.dumps(
                parameters, sort_keys=True, separators=(",", ":")
            ),
        )
        with self.assertRaises(corrected.FrozenSpecificationError):
            corrected.evaluate_frozen_signal(
                tampered,
                history=self.history[:20],
                current=review._f01_positive(),
                context=self.context,
            )

    def test_nonfinite_mtf_unit_blocks(self) -> None:
        context = corrected.ClosedMtfContext(
            "BEARISH", "BEARISH", math.inf, 100, 100
        )
        decision = corrected.evaluate_frozen_signal(
            self.first,
            history=self.history,
            current=review._f01_positive(),
            context=context,
        )
        self.assertEqual(decision.reason, "MTF_CONTEXT_BLOCKED")

    def test_late_mtf_and_unknown_regime_block(self) -> None:
        late = corrected.evaluate_frozen_signal(
            self.first,
            history=self.history,
            current=review._f01_positive(),
            context=review._context(available_4h=101),
        )
        unknown = corrected.evaluate_frozen_signal(
            self.first,
            history=self.history,
            current=review._f01_positive(),
            context=corrected.ClosedMtfContext(
                "UNKNOWN", "BEARISH", 100, 100, 100
            ),
        )
        self.assertFalse(late.signal)
        self.assertFalse(unknown.signal)

    def test_nonfinite_signal_stop_blocks_order(self) -> None:
        for value in (math.nan, math.inf, -math.inf):
            decision = corrected.construct_next_open_short_order(
                self.first,
                corrected.SignalDecision(True, "SIGNAL", value),
                signal_bar_index=10,
                fill_bar_index=11,
                next_open=100.0,
                position_already_open=False,
            )
            self.assertEqual(decision.reason, "INVALID_SIGNAL_STOP")

    def test_fractional_or_boolean_bar_indexes_block(self) -> None:
        signal = review._positive_signal(self.first)
        for signal_index, fill_index in ((10.5, 11.5), (True, 2)):
            order = corrected.construct_next_open_short_order(
                self.first,
                signal,
                signal_bar_index=signal_index,
                fill_bar_index=fill_index,
                next_open=100.0,
                position_already_open=False,
            )
            self.assertEqual(order.reason, "INVALID_BAR_INDEX")

    def test_next_open_overlap_and_gap_contracts(self) -> None:
        signal = review._positive_signal(self.first)
        accepted = corrected.construct_next_open_short_order(
            self.first,
            signal,
            signal_bar_index=10,
            fill_bar_index=11,
            next_open=100.0,
            position_already_open=False,
        )
        overlap = corrected.construct_next_open_short_order(
            self.first,
            signal,
            signal_bar_index=10,
            fill_bar_index=11,
            next_open=100.0,
            position_already_open=True,
        )
        gap = corrected.construct_next_open_short_order(
            self.first,
            signal,
            signal_bar_index=10,
            fill_bar_index=11,
            next_open=float(signal.stop_price),
            position_already_open=False,
        )
        self.assertTrue(accepted.accepted)
        self.assertEqual(overlap.reason, "OVERLAPPING_POSITION_BLOCKED")
        self.assertEqual(gap.reason, "INVALID_GAP_STOP_NOT_ABOVE_ENTRY")

    def test_nonfinite_or_incoherent_accepted_order_blocks_exit(self) -> None:
        neutral = (corrected.SyntheticBar(100.0, 100.5, 99.5, 100.0),)
        orders = (
            corrected.OrderDecision(True, "ORDER_ACCEPTED", 100.0, math.nan, 90.0),
            corrected.OrderDecision(True, "ORDER_ACCEPTED", 100.0, 101.0, 98.0),
            corrected.OrderDecision(True, "WRONG_REASON", 100.0, 101.0, 97.5),
        )
        for order in orders:
            self.assertEqual(
                corrected.resolve_short_exit(order, neutral).reason,
                "INVALID_ACCEPTED_ORDER",
            )

    def test_stop_target_simultaneous_and_time_exit_contracts(self) -> None:
        signal = review._positive_signal(self.first)
        order = corrected.construct_next_open_short_order(
            self.first,
            signal,
            signal_bar_index=10,
            fill_bar_index=11,
            next_open=100.0,
            position_already_open=False,
        )
        stop = corrected.SyntheticBar(
            100.0, float(order.stop_price) + 0.1, 99.5, 100.0
        )
        target = corrected.SyntheticBar(
            100.0, 100.5, float(order.target_price) - 0.1, 99.0
        )
        both = corrected.SyntheticBar(
            100.0,
            float(order.stop_price) + 0.1,
            float(order.target_price) - 0.1,
            100.0,
        )
        neutral = corrected.SyntheticBar(100.0, 100.5, 99.5, 100.0)
        self.assertEqual(corrected.resolve_short_exit(order, (stop,)).reason, "STOP")
        self.assertEqual(corrected.resolve_short_exit(order, (target,)).reason, "TARGET")
        self.assertEqual(
            corrected.resolve_short_exit(order, (both,)).reason,
            "STOP_FIRST_SIMULTANEOUS",
        )
        self.assertEqual(
            corrected.resolve_short_exit(
                order, tuple(neutral for _ in range(240))
            ).reason,
            "TIME_EXIT",
        )
        self.assertEqual(
            corrected.resolve_short_exit(
                order, tuple(neutral for _ in range(239))
            ).reason,
            "OPEN_NO_EXIT",
        )

    def test_indicators_and_family_operator_boundaries(self) -> None:
        cases = review.run_synthetic_review_cases()
        self.assertEqual(len(cases), 30)
        self.assertTrue(all(item.passed for item in cases))

    def test_five_findings_are_reproducible_and_corrected(self) -> None:
        findings = review.reproduce_confirmed_findings()
        self.assertEqual(len(findings), 5)
        self.assertTrue(all(item.status == "CORRECTED_IN_V2" for item in findings))

    def test_review_is_deterministic(self) -> None:
        first = review.validate_phase_10_42r_2f(preflight_only=False)
        second = review.validate_phase_10_42r_2f(preflight_only=False)
        self.assertEqual(first, second)

    def test_preflight_is_source_only_and_passes(self) -> None:
        result = review.require_valid_review(preflight_only=True)
        summary = result["summary"]
        self.assertTrue(summary["validation_passed"])
        self.assertFalse(summary["review_completed"])
        self.assertEqual(summary["real_data_access_count"], 0)
        self.assertEqual(summary["holdout_access_count"], 0)

    def test_source_hash_mismatch_fails_closed(self) -> None:
        original = review.normalized_source_sha256

        def tampered(path):
            if path == review.PHASE_2F_CORRECTED_SOURCE:
                return "0" * 64
            return original(path)

        with patch.object(review, "normalized_source_sha256", side_effect=tampered):
            result = review.validate_phase_10_42r_2f(preflight_only=True)
        self.assertFalse(result["summary"]["validation_passed"])
        self.assertEqual(result["summary"]["validation_decision"], "FAIL_CLOSED")
        with patch.object(review, "normalized_source_sha256", side_effect=tampered):
            with self.assertRaises(review.ReviewFailure):
                review.require_valid_review(preflight_only=True)

    def test_permissions_and_prohibited_outputs_remain_zero_false(self) -> None:
        result = review.require_valid_review(preflight_only=False)
        summary = result["summary"]
        self.assertTrue(all(value is False for value in review.SAFETY_FLAGS.values()))
        self.assertEqual(summary["permissions_enabled_count"], 0)
        self.assertEqual(summary["performance_metric_count"], 0)
        self.assertEqual(summary["candidate_comparison_count"], 0)
        self.assertEqual(summary["candidate_ranking_count"], 0)
        self.assertFalse(summary["winner_selected"])


if __name__ == "__main__":
    unittest.main()
