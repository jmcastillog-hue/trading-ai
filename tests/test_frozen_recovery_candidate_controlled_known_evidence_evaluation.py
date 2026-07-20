from __future__ import annotations

import math
import tempfile
import unittest
from dataclasses import dataclass
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pandas as pd

from src.evaluation import (
    frozen_recovery_candidate_controlled_known_evidence_evaluation_v1 as evaluation,
)
from src.validation import (
    frozen_recovery_candidate_controlled_known_evidence_evaluation_validation_v1
    as validation,
)


@dataclass(frozen=True)
class FakeImplementation:
    evaluation_order: int
    family_id: str
    variant_id: str
    parameters: dict[str, float | int]


def _base_feature_frame(length: int = 260) -> pd.DataFrame:
    timestamps = pd.date_range(
        "2022-12-28T00:00:00Z",
        periods=length,
        freq="15min",
    )
    close = np.linspace(120.0, 90.0, length)
    frame = pd.DataFrame(
        {
            "open_time_utc": timestamps,
            "close_time_utc": timestamps + pd.Timedelta(minutes=15) - pd.Timedelta(microseconds=1),
            "open": close + 0.2,
            "high": close + 0.5,
            "low": close - 0.5,
            "close": close,
            "volume": np.full(length, 10.0),
            "regime_1h": "BEARISH",
            "regime_4h": "STRONG_BEARISH",
            "context_allowed": True,
            "trend_regime": "REGIME_1H=BEARISH|REGIME_4H=STRONG_BEARISH",
        }
    )
    frame["signal_close_available_at"] = frame["open_time_utc"] + pd.Timedelta(minutes=15)
    return evaluation.prepare_signal_features(frame)


def _normalized_fixture() -> tuple[pd.DataFrame, pd.DataFrame]:
    trade_rows: list[dict[str, object]] = []
    source_row = 0
    regime_values = evaluation.EXPECTED_REGIME_COMBINATIONS
    volatility_values = ("LOW", "MID", "HIGH")
    variant_to_family = {
        evaluation.VARIANT_IDS[0]: "RCV_SHORT_UPSIDE_SWEEP_REVERSAL_F01_V1",
        evaluation.VARIANT_IDS[1]: "RCV_SHORT_UPSIDE_SWEEP_REVERSAL_F01_V1",
        evaluation.VARIANT_IDS[2]: "RCV_SHORT_BREAKDOWN_RETEST_F02_V1",
        evaluation.VARIANT_IDS[3]: "RCV_SHORT_BREAKDOWN_RETEST_F02_V1",
        evaluation.VARIANT_IDS[4]: "RCV_SHORT_EMA_PULLBACK_CONTINUATION_F03_V1",
        evaluation.VARIANT_IDS[5]: "RCV_SHORT_EMA_PULLBACK_CONTINUATION_F03_V1",
    }
    for evaluation_order, variant_id in enumerate(evaluation.VARIANT_IDS, start=1):
        for symbol_index, symbol in enumerate(evaluation.SYMBOLS):
            for split_index, (split_name, start, _) in enumerate(evaluation.SPLITS):
                for repetition in range(3):
                    entry = pd.Timestamp(start, tz="UTC") + pd.Timedelta(
                        days=repetition + 1,
                        minutes=15 * symbol_index,
                    )
                    trade_rows.append(
                        {
                            "evaluation_order": evaluation_order,
                            "variant_id": variant_id,
                            "family_id": variant_to_family[variant_id],
                            "symbol": symbol,
                            "split_name": split_name,
                            "signal_time_utc": (entry - pd.Timedelta(minutes=15)).isoformat(),
                            "entry_time_utc": entry.isoformat(),
                            "exit_time_utc": (entry + pd.Timedelta(hours=1)).isoformat(),
                            "signal_atr14": 2.0,
                            "signal_close": 100.0,
                            "calendar_year": entry.year,
                            "volatility_proxy": 0.02,
                            "volatility_tercile": volatility_values[
                                (symbol_index + split_index + repetition) % 3
                            ],
                            "trend_regime": regime_values[
                                (symbol_index + split_index + repetition) % 4
                            ],
                            "entry_price": 100.0,
                            "stop_price": 102.0,
                            "target_price": 95.0,
                            "exit_price": 95.0,
                            "risk_distance": 2.0,
                            "risk_pct_of_entry": 0.02,
                            "elapsed_trade_bars": 4,
                            "exit_reason": "TARGET",
                            "gap_crossing_count": 0,
                            "frictionless_gross_result_r": 2.5,
                            "result_eligible": True,
                            "invalidation_reason": "",
                            "source_trade_row": source_row,
                        }
                    )
                    source_row += 1
    trades = pd.DataFrame(trade_rows)
    normalized = evaluation.apply_cost_profiles(trades)
    return trades, normalized


class ControlledKnownEvidenceEvaluationTests(unittest.TestCase):
    def test_phase_and_finite_route_are_exact(self) -> None:
        self.assertEqual(evaluation.PHASE, "10.42R.2K")
        self.assertIn("2L", evaluation.RECOMMENDED_NEXT_PHASE)
        self.assertEqual(len(evaluation.VARIANT_IDS), 6)
        self.assertEqual(len(evaluation.COST_PROFILES), 5)

    def test_permissions_enable_only_limited_research_actions(self) -> None:
        enabled = {
            name for name, value in evaluation.PERMISSIONS.items() if value
        }
        self.assertEqual(enabled, evaluation.ALLOWED_TRUE_PERMISSIONS)
        self.assertFalse(evaluation.PERMISSIONS["candidate_ranking_allowed"])
        self.assertFalse(evaluation.PERMISSIONS["winner_selection_allowed"])
        self.assertFalse(evaluation.PERMISSIONS["execution_allowed"])
        self.assertFalse(
            evaluation.PERMISSIONS["openclaw_operational_integration_allowed"]
        )

    def test_run_id_is_deterministic(self) -> None:
        source_hash = "a" * 64
        first = evaluation.build_run_id(source_hash)
        second = evaluation.build_run_id(source_hash)
        self.assertEqual(first, second)
        self.assertIn(source_hash[:12], first)
        self.assertIn(evaluation.SOURCE_PHASE_2J_BINDING_ROOT_SHA256[:12], first)

    def test_split_boundaries_are_exact(self) -> None:
        self.assertEqual(
            evaluation.split_name_for_timestamp(pd.Timestamp("2023-01-01T00:00:00Z")),
            evaluation.SPLITS[0][0],
        )
        self.assertEqual(
            evaluation.split_name_for_timestamp(pd.Timestamp("2025-12-31T23:45:00Z")),
            evaluation.SPLITS[-1][0],
        )
        self.assertEqual(
            evaluation.split_name_for_timestamp(pd.Timestamp("2022-12-31T23:45:00Z")),
            "",
        )

    def test_regime_classification_order_is_exact(self) -> None:
        close = pd.Series([110.0, 105.0, 90.0, 95.0, 100.0])
        ema20 = pd.Series([108.0, 104.0, 92.0, 96.0, 100.0])
        ema50 = pd.Series([105.0, 100.0, 95.0, 98.0, 100.0])
        ema200 = pd.Series([100.0, 101.0, 100.0, 97.0, 100.0])
        regimes = evaluation.classify_regime_values(close, ema20, ema50, ema200)
        self.assertEqual(
            regimes.tolist(),
            ["STRONG_BULLISH", "BULLISH", "STRONG_BEARISH", "BEARISH", "NEUTRAL"],
        )

    def test_signal_features_reset_after_declared_15m_gap(self) -> None:
        frame = _base_feature_frame(230).drop(
            index=list(range(205, 210))
        ).reset_index(drop=True)
        featured = evaluation.prepare_signal_features(
            frame.drop(
                columns=[
                    "atr14",
                    "ema20",
                    "ema50",
                    "ema200",
                    "ema20_previous",
                    "prior_close",
                    "continuity_segment_id",
                ],
                errors="ignore",
            )
        )
        self.assertEqual(featured["continuity_segment_id"].nunique(), 2)
        second = featured.loc[featured["continuity_segment_id"].eq(2)]
        self.assertTrue(second["ema200"].isna().all())
        self.assertTrue(second.iloc[:13]["atr14"].isna().all())

    def test_context_regime_resets_after_higher_timeframe_gap(self) -> None:
        timestamps = pd.date_range(
            "2022-01-01T00:00:00Z", periods=230, freq="1h"
        )
        frame = pd.DataFrame(
            {
                "open_time_utc": timestamps,
                "close": np.linspace(120.0, 90.0, len(timestamps)),
            }
        ).drop(index=210).reset_index(drop=True)
        regimes = evaluation.build_regime_features(frame, "1h")
        after_gap = regimes.loc[
            regimes["source_open_time_1h_utc"]
            > pd.Timestamp("2022-01-09T18:00:00Z")
        ]
        self.assertFalse(after_gap.empty)
        self.assertTrue(after_gap["regime_1h"].eq("UNKNOWN").all())

    def test_signal_feature_ewm_matches_frozen_formulas(self) -> None:
        frame = _base_feature_frame(40)
        closes = frame["close"].to_numpy(dtype=float)
        alpha = 2.0 / 21.0
        expected_ema20 = closes[0]
        for value in closes[1:]:
            expected_ema20 = alpha * value + (1.0 - alpha) * expected_ema20
        self.assertAlmostEqual(frame["ema20"].iloc[-1], expected_ema20, places=12)
        self.assertTrue(math.isfinite(float(frame["atr14"].iloc[-1])))

    def test_upside_sweep_uses_strict_close_below_prior_high(self) -> None:
        frame = _base_feature_frame(80)
        frame.loc[:, "high"] = 100.0
        frame.loc[:, "open"] = 99.5
        frame.loc[:, "close"] = 99.0
        frame.loc[:, "low"] = 98.0
        frame.loc[79, ["open", "high", "low", "close"]] = [100.0, 102.0, 98.0, 100.0]
        frame = evaluation.prepare_signal_features(frame.drop(columns=["atr14", "ema20", "ema50", "ema200", "ema20_previous", "prior_close"]))
        implementation = FakeImplementation(
            1,
            "RCV_SHORT_UPSIDE_SWEEP_REVERSAL_F01_V1",
            evaluation.VARIANT_IDS[0],
            {
                "prior_high_lookback_bars": 48,
                "wick_to_body_minimum": 1.0,
                "stop_atr_buffer": 0.25,
            },
        )
        mask, _ = evaluation.build_signal_candidate_arrays(frame, implementation)
        self.assertFalse(mask[-1])
        frame.loc[79, "close"] = 99.8
        frame.loc[79, "open"] = 100.2
        frame = evaluation.prepare_signal_features(frame.drop(columns=["atr14", "ema20", "ema50", "ema200", "ema20_previous", "prior_close"]))
        mask, stop = evaluation.build_signal_candidate_arrays(frame, implementation)
        self.assertTrue(mask[-1])
        self.assertGreater(stop[-1], frame.loc[79, "high"])

    def test_breakdown_retest_uses_most_recent_prior_eight_bars(self) -> None:
        frame = _base_feature_frame(100)
        frame.loc[:, ["open", "high", "low", "close"]] = [100.0, 101.0, 99.0, 100.0]
        frame.loc[96, ["open", "high", "low", "close"]] = [100.0, 100.0, 95.0, 96.0]
        frame.loc[99, ["open", "high", "low", "close"]] = [99.5, 100.0, 97.0, 98.0]
        frame = evaluation.prepare_signal_features(frame.drop(columns=["atr14", "ema20", "ema50", "ema200", "ema20_previous", "prior_close"]))
        implementation = FakeImplementation(
            3,
            "RCV_SHORT_BREAKDOWN_RETEST_F02_V1",
            evaluation.VARIANT_IDS[2],
            {
                "support_lookback_bars": 48,
                "retest_window_bars": 8,
                "break_atr": 0.25,
                "retest_tolerance_atr": 0.25,
                "stop_atr_buffer": 0.25,
            },
        )
        mask, _ = evaluation.build_signal_candidate_arrays(frame, implementation)
        self.assertTrue(mask[-1])

    def test_ema_pullback_rule_respects_separation(self) -> None:
        frame = _base_feature_frame(220)
        frame.loc[219, "open"] = frame.loc[219, "ema20"] + 1.0
        frame.loc[219, "high"] = frame.loc[219, "ema20"] + 1.5
        frame.loc[219, "close"] = frame.loc[219, "ema20"] - 0.5
        frame.loc[219, "low"] = frame.loc[219, "close"] - 0.5
        frame.loc[218, "close"] = frame.loc[218, "ema20"] - 0.5
        implementation = FakeImplementation(
            5,
            "RCV_SHORT_EMA_PULLBACK_CONTINUATION_F03_V1",
            evaluation.VARIANT_IDS[4],
            {
                "minimum_ema20_ema50_separation_atr": 0.0,
                "stop_atr_buffer": 0.25,
            },
        )
        mask, _ = evaluation.build_signal_candidate_arrays(frame, implementation)
        self.assertTrue(mask[-1])
        strict = FakeImplementation(
            6,
            implementation.family_id,
            evaluation.VARIANT_IDS[5],
            {
                "minimum_ema20_ema50_separation_atr": 100.0,
                "stop_atr_buffer": 0.25,
            },
        )
        strict_mask, _ = evaluation.build_signal_candidate_arrays(frame, strict)
        self.assertFalse(strict_mask[-1])

    def test_exit_resolution_is_stop_first_and_time_exit_240(self) -> None:
        frame = _base_feature_frame(250)
        frame.loc[0, ["high", "low"]] = [103.0, 94.0]
        result = evaluation._resolve_short_trade(frame, 0, 100.0, 102.0, 95.0)
        self.assertEqual(result["exit_reason"], "STOP_FIRST_SIMULTANEOUS")
        frame = _base_feature_frame(250)
        frame.loc[:, "high"] = 101.0
        frame.loc[:, "low"] = 96.0
        result = evaluation._resolve_short_trade(frame, 0, 100.0, 102.0, 95.0)
        self.assertEqual(result["exit_reason"], "TIME_EXIT")
        self.assertEqual(result["elapsed_trade_bars"], 240)

    def test_declared_gap_invalidates_unknown_outcome_without_fill(self) -> None:
        frame = _base_feature_frame(30)
        frame.loc[:, "high"] = 101.0
        frame.loc[:, "low"] = 96.0
        frame.loc[8:, "open_time_utc"] = (
            frame.loc[8:, "open_time_utc"] + pd.Timedelta(minutes=15)
        )
        frame.loc[8:, "close_time_utc"] = (
            frame.loc[8:, "close_time_utc"] + pd.Timedelta(minutes=15)
        )
        result = evaluation._resolve_short_trade(
            frame, 0, 100.0, 102.0, 95.0
        )
        self.assertFalse(result["result_eligible"])
        self.assertEqual(
            result["exit_reason"],
            "SOURCE_GAP_CROSSED_OUTCOME_UNOBSERVABLE",
        )
        self.assertEqual(result["gap_crossing_count"], 1)

    def test_empty_variant_still_publishes_fixed_metric_and_pvalue_rows(self) -> None:
        trades, normalized = _normalized_fixture()
        missing_variant = evaluation.VARIANT_IDS[-1]
        reduced = normalized.loc[
            ~normalized["variant_id"].eq(missing_variant)
        ].copy()
        metrics = evaluation.build_metric_table(reduced)
        multiplicity = evaluation.build_multiplicity_table(reduced)
        self.assertEqual(len(metrics), 450)
        self.assertEqual(len(multiplicity), 6)
        aggregate = metrics.loc[
            metrics["variant_id"].eq(missing_variant)
            & metrics["cost_profile"].eq(evaluation.PRIMARY_COST_PROFILE)
            & metrics["slice_dimension"].eq("AGGREGATE")
        ].iloc[0]
        pvalue = multiplicity.loc[
            multiplicity["variant_id"].eq(missing_variant)
        ].iloc[0]
        self.assertEqual(int(aggregate["trade_count"]), 0)
        self.assertEqual(int(pvalue["trade_count"]), 0)
        self.assertEqual(float(pvalue["unadjusted_p_value"]), 1.0)

    def test_cost_accounting_applies_one_profile_once(self) -> None:
        trades = pd.DataFrame(
            [
                {
                    "result_eligible": True,
                    "risk_pct_of_entry": 0.02,
                    "frictionless_gross_result_r": 2.5,
                }
            ]
        )
        normalized = evaluation.apply_cost_profiles(trades)
        self.assertEqual(len(normalized), 5)
        self.assertTrue(normalized["cost_application_count"].eq(1).all())
        base = normalized.loc[
            normalized["cost_profile"].eq(evaluation.PRIMARY_COST_PROFILE)
        ].iloc[0]
        self.assertAlmostEqual(base["profile_total_cost_r"], 0.08)
        self.assertAlmostEqual(base["normalized_net_result_r"], 2.42)

    def test_profit_factor_and_drawdown_are_deterministic(self) -> None:
        values = [1.0, -0.5, 2.0, -1.0]
        self.assertAlmostEqual(evaluation.profit_factor(values), 2.0)
        self.assertAlmostEqual(evaluation.calculate_max_drawdown_r(values), -1.0)

    def test_cluster_bootstrap_is_deterministic(self) -> None:
        _, normalized = _normalized_fixture()
        primary = normalized.loc[
            normalized["variant_id"].eq(evaluation.VARIANT_IDS[0])
            & normalized["cost_profile"].eq(evaluation.PRIMARY_COST_PROFILE)
        ]
        first = evaluation.cluster_bootstrap_p_value(
            primary, evaluation_order=1, resamples=500
        )
        second = evaluation.cluster_bootstrap_p_value(
            primary, evaluation_order=1, resamples=500
        )
        self.assertEqual(first, second)
        self.assertGreater(first[0], 0.0)

    def test_holm_adjustment_uses_fixed_tie_break(self) -> None:
        rows = [
            {"evaluation_order": 2, "unadjusted_p_value": 0.01},
            {"evaluation_order": 1, "unadjusted_p_value": 0.01},
            {"evaluation_order": 3, "unadjusted_p_value": 0.03},
        ]
        adjusted = evaluation.holm_adjust_p_values(rows)
        by_order = {row["evaluation_order"]: row for row in adjusted}
        self.assertEqual(by_order[1]["holm_rank"], 1)
        self.assertEqual(by_order[2]["holm_rank"], 2)
        self.assertGreaterEqual(
            by_order[3]["holm_adjusted_p_value"],
            by_order[2]["holm_adjusted_p_value"],
        )

    def test_metric_table_has_exact_predeclared_grid(self) -> None:
        _, normalized = _normalized_fixture()
        metrics = evaluation.build_metric_table(normalized)
        self.assertEqual(len(metrics), 450)
        self.assertEqual(metrics["variant_id"].nunique(), 6)
        self.assertEqual(metrics["cost_profile"].nunique(), 5)

    def test_multiplicity_and_gate_tables_publish_all_variants(self) -> None:
        trades, normalized = _normalized_fixture()
        metrics = evaluation.build_metric_table(normalized)
        multiplicity = evaluation.build_multiplicity_table(normalized)
        gates = evaluation.build_gate_classification(metrics, multiplicity, trades)
        self.assertEqual(len(multiplicity), 6)
        self.assertEqual(len(gates), 60)
        self.assertEqual(gates["variant_id"].nunique(), 6)
        self.assertFalse(gates["ranking_allowed"].astype(bool).any())
        self.assertFalse(gates["winner_selection_allowed"].astype(bool).any())

    def test_audit_artifact_inventory_is_exact_twelve(self) -> None:
        self.assertEqual(len(evaluation.AUDIT_ARTIFACTS), 12)
        self.assertEqual(evaluation.AUDIT_ARTIFACTS[-1], "run_summary.json")

    def test_engine_hash_anchor_matches_validator(self) -> None:
        root = Path(__file__).resolve().parents[1]
        engine_path = root / validation.ENGINE_PATH
        self.assertEqual(
            validation.normalized_source_sha256(engine_path),
            validation.EXPECTED_ENGINE_SOURCE_SHA256,
        )

    def test_environment_artifact_excludes_process_specific_identity(self) -> None:
        source = Path(
            evaluation.__file__
        ).read_text(encoding="utf-8")
        self.assertNotIn('"process_id"', source)

    def test_atomic_publish_is_idempotent_for_identical_bundle(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            final = root / "final"
            first = root / "first"
            first.mkdir()
            (first / "a.txt").write_text("same\n", encoding="utf-8")
            status = evaluation._atomic_publish_bundle(first, final)
            self.assertEqual(status, "NEW_BUNDLE_ATOMICALLY_PUBLISHED")
            second = root / "second"
            second.mkdir()
            (second / "a.txt").write_text("same\n", encoding="utf-8")
            status = evaluation._atomic_publish_bundle(second, final)
            self.assertEqual(status, "IDEMPOTENT_EXISTING_BUNDLE_VERIFIED")

    def test_source_contains_no_winner_selection_logic(self) -> None:
        root = Path(__file__).resolve().parents[1]
        source = (root / validation.ENGINE_PATH).read_text(encoding="utf-8")
        self.assertNotIn("sort_values(\"performance_rank\"", source)
        self.assertNotIn("selected_winner", source)
        self.assertIn('"winner": None', source)


if __name__ == "__main__":
    unittest.main()
