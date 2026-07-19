from __future__ import annotations

import unittest
from unittest.mock import patch

import pandas as pd

import src.analysis.frozen_recovery_candidate_implementation_v1 as implementation_module
from src.analysis.frozen_recovery_candidate_implementation_v1 import (
    EXPECTED_VARIANT_IDS,
    SYNTHETIC_FIXTURE_SOURCE,
    ClosedMtfContext,
    FrozenSpecificationError,
    SignalDecision,
    SyntheticBar,
    breakdown_condition,
    build_verified_implementations,
    construct_next_open_short_order,
    ema_pullback_condition,
    evaluate_frozen_signal,
    resolve_short_exit,
    retest_condition,
    verify_phase_2d_specification_root,
)
from src.analysis.recovery_candidate_family_specification_v1 import (
    EXPECTED_SPECIFICATION_ROOT_SHA256,
    build_specification_artifacts,
)
from src.validation.frozen_recovery_candidate_static_conformance_v1 import (
    EXPECTED_IMPLEMENTATION_ROOT_SHA256,
    NEXT_PHASE,
    SAFETY_FLAGS,
    _closed_context,
    _ema_current,
    _ema_trend_history,
    _f01_current,
    _f02_current,
    _f02_history,
    _flat_history,
    build_implementation_catalog,
    implementation_registry_equivalent,
    implementation_source_is_static_and_safe,
    run_synthetic_conformance_cases,
    validate_phase_10_42r_2e,
)


class FrozenRecoveryCandidateStaticConformanceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.implementations = build_verified_implementations()
        self.by_id = {item.variant_id: item for item in self.implementations}

    def test_phase_2d_golden_root_reproduces_before_build(self) -> None:
        self.assertEqual(
            verify_phase_2d_specification_root(),
            EXPECTED_SPECIFICATION_ROOT_SHA256,
        )

    def test_tampered_phase_2d_root_fails_closed(self) -> None:
        original = implementation_module.build_specification_manifest

        def tampered(artifacts):
            manifest, root = original(artifacts)
            root = root.copy()
            root.loc[0, "specification_root_sha256"] = "0" * 64
            return manifest, root

        with patch.object(
            implementation_module,
            "build_specification_manifest",
            side_effect=tampered,
        ):
            with self.assertRaises(FrozenSpecificationError):
                implementation_module.build_verified_implementations()

    def test_catalog_has_exact_six_frozen_variants_in_order(self) -> None:
        self.assertEqual(
            tuple(item.variant_id for item in self.implementations),
            EXPECTED_VARIANT_IDS,
        )
        self.assertEqual(len(self.implementations), 6)

    def test_registry_parameters_and_hashes_equal_implementation(self) -> None:
        catalog = build_implementation_catalog(self.implementations)
        valid, details = implementation_registry_equivalent(catalog)
        self.assertTrue(valid, details)
        registry = build_specification_artifacts()["candidate_variant_registry"]
        self.assertEqual(catalog["parameter_json"].tolist(), registry["parameter_json"].tolist())

    def test_all_implementations_are_unevaluated_and_root_bound(self) -> None:
        catalog = build_implementation_catalog(self.implementations)
        self.assertTrue(
            catalog["specification_root_sha256"]
            .eq(EXPECTED_SPECIFICATION_ROOT_SHA256)
            .all()
        )
        self.assertFalse(catalog["evaluated"].any())
        self.assertTrue(catalog["candidate_result_rows"].eq(0).all())
        self.assertFalse(catalog["ranking_allowed"].any())
        self.assertFalse(catalog["selection_allowed"].any())

    def test_implementation_source_has_no_project_runtime_or_io(self) -> None:
        valid, details = implementation_source_is_static_and_safe()
        self.assertTrue(valid, details)
        self.assertNotIn(".csv", details)
        self.assertNotIn("holdout", details)

    def test_f01_both_variants_positive(self) -> None:
        for variant_id in EXPECTED_VARIANT_IDS[:2]:
            decision = evaluate_frozen_signal(
                self.by_id[variant_id],
                history=_flat_history(),
                current=_f01_current(),
                context=_closed_context(),
            )
            self.assertTrue(decision.signal, variant_id)
            self.assertEqual(decision.reason, "SIGNAL")

    def test_f01_strict_high_and_zero_body_boundaries_block(self) -> None:
        candidate = self.by_id[EXPECTED_VARIANT_IDS[0]]
        high_equal = evaluate_frozen_signal(
            candidate,
            history=_flat_history(),
            current=SyntheticBar(99.8, 100.0, 99.2, 99.5),
            context=_closed_context(),
        )
        zero_body = evaluate_frozen_signal(
            candidate,
            history=_flat_history(),
            current=SyntheticBar(100.0, 101.0, 99.5, 100.0),
            context=_closed_context(),
        )
        self.assertFalse(high_equal.signal)
        self.assertFalse(zero_body.signal)

    def test_f02_both_variants_positive(self) -> None:
        for variant_id in EXPECTED_VARIANT_IDS[2:4]:
            decision = evaluate_frozen_signal(
                self.by_id[variant_id],
                history=_f02_history(),
                current=_f02_current(),
                context=_closed_context(),
            )
            self.assertTrue(decision.signal, variant_id)

    def test_f02_strict_break_and_inclusive_retest_boundaries(self) -> None:
        self.assertFalse(
            breakdown_condition(
                close=99.75,
                support=100.0,
                atr14=1.0,
                break_atr=0.25,
            )
        )
        self.assertTrue(
            retest_condition(
                current=SyntheticBar(99.7, 99.75, 99.4, 99.5),
                support=100.0,
                atr14=1.0,
                tolerance_atr=0.25,
            )
        )

    def test_f03_both_variants_positive(self) -> None:
        for variant_id in EXPECTED_VARIANT_IDS[4:]:
            decision = evaluate_frozen_signal(
                self.by_id[variant_id],
                history=_ema_trend_history(),
                current=_ema_current(),
                context=_closed_context(),
            )
            self.assertTrue(decision.signal, variant_id)

    def test_f03_separation_equality_passes_and_stack_equality_blocks(self) -> None:
        arguments = {
            "current": SyntheticBar(99.0, 100.0, 98.0, 98.5),
            "prior_close": 99.0,
            "ema20_t": 99.5,
            "ema200_t": 101.0,
            "ema20_previous": 100.0,
            "atr14_t": 1.0,
            "minimum_separation_atr": 0.25,
        }
        self.assertTrue(ema_pullback_condition(ema50_t=99.75, **arguments))
        self.assertFalse(ema_pullback_condition(ema50_t=99.5, **arguments))

    def test_mtf_features_available_exactly_at_close_pass(self) -> None:
        candidate = self.by_id[EXPECTED_VARIANT_IDS[0]]
        decision = evaluate_frozen_signal(
            candidate,
            history=_flat_history(),
            current=_f01_current(),
            context=ClosedMtfContext("BEARISH", "BEARISH", 100, 100, 100),
        )
        self.assertTrue(decision.signal)

    def test_late_or_unknown_mtf_context_blocks(self) -> None:
        candidate = self.by_id[EXPECTED_VARIANT_IDS[0]]
        late = evaluate_frozen_signal(
            candidate,
            history=_flat_history(),
            current=_f01_current(),
            context=ClosedMtfContext("BEARISH", "BEARISH", 100, 100, 101),
        )
        unknown = evaluate_frozen_signal(
            candidate,
            history=_flat_history(),
            current=_f01_current(),
            context=ClosedMtfContext("UNKNOWN", "BEARISH", 100, 100, 100),
        )
        self.assertFalse(late.signal)
        self.assertFalse(unknown.signal)

    def test_non_synthetic_or_open_bar_blocks(self) -> None:
        candidate = self.by_id[EXPECTED_VARIANT_IDS[0]]
        real_source = evaluate_frozen_signal(
            candidate,
            history=_flat_history(),
            current=SyntheticBar(
                100.5, 101.0, 99.5, 100.0, source="FORBIDDEN_REAL_SOURCE"
            ),
            context=_closed_context(),
        )
        open_bar = evaluate_frozen_signal(
            candidate,
            history=_flat_history(),
            current=SyntheticBar(100.5, 101.0, 99.5, 100.0, closed=False),
            context=_closed_context(),
        )
        self.assertEqual(real_source.reason, "NON_SYNTHETIC_OR_INVALID_BAR")
        self.assertEqual(open_bar.reason, "NON_SYNTHETIC_OR_INVALID_BAR")

    def _positive_order(self):
        candidate = self.by_id[EXPECTED_VARIANT_IDS[0]]
        signal = evaluate_frozen_signal(
            candidate,
            history=_flat_history(),
            current=_f01_current(),
            context=_closed_context(),
        )
        order = construct_next_open_short_order(
            candidate,
            signal,
            signal_bar_index=10,
            fill_bar_index=11,
            next_open=100.0,
            position_already_open=False,
        )
        return candidate, signal, order

    def test_next_open_order_and_rr_target(self) -> None:
        _, _, order = self._positive_order()
        self.assertTrue(order.accepted)
        risk = order.stop_price - order.entry_price
        self.assertAlmostEqual(order.target_price, order.entry_price - 2.5 * risk)

    def test_wrong_fill_gap_equality_and_overlap_block(self) -> None:
        candidate, signal, _ = self._positive_order()
        wrong_fill = construct_next_open_short_order(
            candidate, signal, signal_bar_index=10, fill_bar_index=10,
            next_open=100.0, position_already_open=False,
        )
        gap_equal = construct_next_open_short_order(
            candidate, signal, signal_bar_index=10, fill_bar_index=11,
            next_open=signal.stop_price, position_already_open=False,
        )
        overlap = construct_next_open_short_order(
            candidate, signal, signal_bar_index=10, fill_bar_index=11,
            next_open=100.0, position_already_open=True,
        )
        self.assertEqual(wrong_fill.reason, "FILL_NOT_NEXT_BAR_OPEN")
        self.assertEqual(gap_equal.reason, "INVALID_GAP_STOP_NOT_ABOVE_ENTRY")
        self.assertEqual(overlap.reason, "OVERLAPPING_POSITION_BLOCKED")

    def test_stop_target_and_simultaneous_stop_first(self) -> None:
        _, _, order = self._positive_order()
        stop = SyntheticBar(100.0, order.stop_price + 0.1, 99.5, 100.0)
        target = SyntheticBar(100.0, 100.5, order.target_price - 0.1, 99.0)
        both = SyntheticBar(
            100.0,
            order.stop_price + 0.1,
            order.target_price - 0.1,
            100.0,
        )
        self.assertEqual(resolve_short_exit(order, (stop,)).reason, "STOP")
        self.assertEqual(resolve_short_exit(order, (target,)).reason, "TARGET")
        self.assertEqual(
            resolve_short_exit(order, (both,)).reason,
            "STOP_FIRST_SIMULTANEOUS",
        )

    def test_time_exit_at_240_and_open_at_239(self) -> None:
        _, _, order = self._positive_order()
        neutral = SyntheticBar(100.0, 100.5, 99.5, 100.0)
        self.assertEqual(
            resolve_short_exit(order, tuple(neutral for _ in range(240))).reason,
            "TIME_EXIT",
        )
        self.assertEqual(
            resolve_short_exit(order, tuple(neutral for _ in range(239))).reason,
            "OPEN_NO_EXIT",
        )

    def test_fixture_catalog_is_deterministic_and_all_passes(self) -> None:
        first = run_synthetic_conformance_cases(self.implementations)
        second = run_synthetic_conformance_cases(self.implementations)
        pd.testing.assert_frame_equal(first, second)
        self.assertEqual(len(first), 32)
        self.assertTrue(first["passed"].all())
        self.assertTrue(first["fixture_source"].eq(SYNTHETIC_FIXTURE_SOURCE).all())

    def test_no_performance_comparison_ranking_or_winner_rows(self) -> None:
        cases = run_synthetic_conformance_cases(self.implementations)
        columns = [
            "real_data_rows",
            "candidate_performance_rows",
            "comparison_rows",
            "ranking_rows",
            "winner_rows",
        ]
        self.assertTrue(cases[columns].eq(0).all(axis=None))

    def test_preflight_writes_only_empty_implementation_schemas(self) -> None:
        with patch(
            "src.validation.frozen_recovery_candidate_static_conformance_v1.write_outputs"
        ):
            outputs = validate_phase_10_42r_2e(preflight_only=True)
        self.assertTrue(outputs["summary"].iloc[0]["validation_passed"])
        self.assertFalse(outputs["summary"].iloc[0]["implementation_completed"])
        self.assertTrue(outputs["implementation_catalog"].empty)
        self.assertTrue(outputs["synthetic_conformance"].empty)
        self.assertEqual(outputs["summary"].iloc[0]["total_checks"], 12)

    def test_full_workflow_completes_without_evaluation(self) -> None:
        with patch(
            "src.validation.frozen_recovery_candidate_static_conformance_v1.write_outputs"
        ):
            outputs = validate_phase_10_42r_2e(preflight_only=False)
        summary = outputs["summary"].iloc[0]
        self.assertTrue(summary["validation_passed"])
        self.assertTrue(summary["implementation_completed"])
        self.assertEqual(summary["total_checks"], 27)
        self.assertEqual(summary["blocker_count"], 0)
        self.assertEqual(summary["candidate_result_rows"], 0)
        self.assertFalse(summary["winner_selected"])
        self.assertEqual(summary["recommended_next_phase"], NEXT_PHASE)
        self.assertEqual(
            summary["implementation_root_sha256"],
            EXPECTED_IMPLEMENTATION_ROOT_SHA256,
        )

    def test_holdout_presence_fails_preflight_closed(self) -> None:
        with (
            patch(
                "src.validation.frozen_recovery_candidate_static_conformance_v1.sealed_inputs_absent",
                return_value=False,
            ),
            patch(
                "src.validation.frozen_recovery_candidate_static_conformance_v1.write_outputs"
            ),
        ):
            outputs = validate_phase_10_42r_2e(preflight_only=True)
        self.assertFalse(outputs["summary"].iloc[0]["validation_passed"])
        self.assertGreater(outputs["summary"].iloc[0]["blocker_count"], 0)
        self.assertTrue(outputs["implementation_catalog"].empty)

    def test_source_hash_mismatch_fails_preflight_closed(self) -> None:
        with (
            patch(
                "src.validation.frozen_recovery_candidate_static_conformance_v1.normalized_source_sha256",
                return_value="bad",
            ),
            patch(
                "src.validation.frozen_recovery_candidate_static_conformance_v1.write_outputs"
            ),
        ):
            outputs = validate_phase_10_42r_2e(preflight_only=True)
        self.assertFalse(outputs["summary"].iloc[0]["validation_passed"])
        self.assertTrue(outputs["implementation_catalog"].empty)

    def test_all_permissions_remain_false(self) -> None:
        self.assertTrue(SAFETY_FLAGS)
        self.assertTrue(all(value is False for value in SAFETY_FLAGS.values()))


if __name__ == "__main__":
    unittest.main()
