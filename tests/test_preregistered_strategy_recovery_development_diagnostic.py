from __future__ import annotations

import unittest
from unittest.mock import patch

import numpy as np
import pandas as pd

from src.analysis.preregistered_strategy_recovery_diagnostic_v1 import (
    DIAGNOSTIC_SIGNAL_FAMILY,
    SLICE_DIMENSIONS,
    attach_closed_candle_context,
    attach_features_to_normalized,
    build_slice_catalog,
    build_slice_coverage,
    build_slice_metrics,
    build_source_trade_features,
    validate_normalized_source_grid,
)
from src.execution.cost_aware_filter_v1 import build_cost_profiles
from src.execution.normalized_cost_accounting_v1 import normalize_short_trades
from src.validation.cost_accounting_normalization_and_strategy_recovery_preregistration_v1 import (
    SHORT_SYMBOL_COHORT,
    SHORT_WALK_FORWARD_SPLITS,
    build_accounting_contract,
    build_recovery_preregistration,
)
from src.validation.preregistered_strategy_recovery_development_diagnostic_v1 import (
    NEXT_PHASE,
    PHASE_2B_REQUIRED_REPORTS,
    SAFETY_FLAGS,
    SPLIT_TEST_YEARS,
    validate_phase_10_42r_2c,
)


def synthetic_trade(
    source_row: int,
    symbol: str,
    split_name: str,
    signal_time: str,
    volatility_proxy: float,
) -> dict:
    raw_entry = 100.0
    raw_exit = 98.0 if source_row % 3 == 0 else 101.0
    units = 10.0
    risk_amount = 20.0
    spread_rate = 0.0002
    fee_rate = 0.001
    engine_entry = raw_entry * (1.0 - spread_rate / 2.0)
    engine_exit = raw_exit * (1.0 + spread_rate / 2.0)
    gross_pnl = (engine_entry - engine_exit) * units
    fees = (engine_entry + engine_exit) * units * fee_rate
    result_r = (gross_pnl - fees) / risk_amount
    timestamp = pd.Timestamp(signal_time)
    return {
        "symbol": symbol,
        "split_name": split_name,
        "fill_mode": "NEXT_BAR_OPEN_CORRECTED",
        "direction": "SHORT",
        "signal_time": timestamp,
        "entry_time": timestamp + pd.Timedelta(minutes=15),
        "exit_time": timestamp + pd.Timedelta(hours=1),
        "signal_atr": raw_entry * volatility_proxy,
        "signal_close": raw_entry,
        "raw_entry_reference": raw_entry,
        "raw_exit_reference": raw_exit,
        "entry_price": engine_entry,
        "exit_price": engine_exit,
        "position_units": units,
        "risk_amount": risk_amount,
        "gross_pnl": gross_pnl,
        "fees": fees,
        "net_pnl": gross_pnl - fees,
        "result_r": result_r,
    }


def synthetic_normalized() -> pd.DataFrame:
    rows = [
        synthetic_trade(0, "BTCUSDT", SHORT_WALK_FORWARD_SPLITS[0], "2023-02-01", 0.005),
        synthetic_trade(1, "ETHUSDT", SHORT_WALK_FORWARD_SPLITS[1], "2023-05-01", 0.007),
        synthetic_trade(2, "SOLUSDT", SHORT_WALK_FORWARD_SPLITS[4], "2024-02-01", 0.009),
        synthetic_trade(3, "BTCUSDT", SHORT_WALK_FORWARD_SPLITS[5], "2024-05-01", 0.012),
        synthetic_trade(4, "ETHUSDT", SHORT_WALK_FORWARD_SPLITS[8], "2025-02-01", 0.016),
        synthetic_trade(5, "SOLUSDT", SHORT_WALK_FORWARD_SPLITS[9], "2025-05-01", 0.025),
    ]
    return normalize_short_trades(pd.DataFrame(rows), build_cost_profiles())


def synthetic_context(normalized: pd.DataFrame) -> pd.DataFrame:
    source = normalized.sort_values("source_trade_row").drop_duplicates(
        "source_trade_row"
    )
    rows = []
    regimes = [
        ("BEARISH", "STRONG_BEARISH"),
        ("NEUTRAL", "BEARISH"),
        ("STRONG_BEARISH", "BEARISH"),
    ]
    for index, row in source.reset_index(drop=True).iterrows():
        regime_1h, regime_4h = regimes[index % len(regimes)]
        rows.append(
            {
                "symbol": row["symbol"],
                "timestamp": row["signal_time"],
                "regime_1h": regime_1h,
                "regime_4h": regime_4h,
            }
        )
    return pd.DataFrame(rows)


def phase_2b_frames(normalized: pd.DataFrame) -> dict[str, pd.DataFrame]:
    profiles = [profile.name for profile in build_cost_profiles()]
    return {
        "summary": pd.DataFrame(
            [
                {
                    "audit_completed": True,
                    "validation_passed": True,
                    "blocker_count": 0,
                    "source_short_next_open_trades": normalized["source_trade_row"].nunique(),
                    "cost_profile_count": len(profiles),
                    "normalized_trade_profile_rows": len(normalized),
                    "accounting_contract": "FRICTIONLESS_GROSS_R_TO_SINGLE_PROFILE_NET_R_V1",
                    "short_candidate_status": "REVALIDATED_REJECTED_UNCHANGED",
                    "long_candidate_status": "RESEARCH_ONLY_NOT_APPROVED",
                    "candidate_reclassified": False,
                }
            ]
        ),
        "checks": pd.DataFrame(
            [{"check_name": "phase_2b_ok", "passed": True, "blocker": False}]
        ),
        "normalized_short_trades": normalized,
        "normalized_short_summary": pd.DataFrame(
            [
                {
                    "scope": "ALL_SYMBOLS",
                    "cost_profile": profiles[0],
                    "trade_rows": normalized["source_trade_row"].nunique(),
                    "normalized_average_result_r": -0.1,
                    "normalized_profit_factor": 0.8,
                    "normalized_max_drawdown_r": -2.0,
                    "positive_window_rate": 0.25,
                }
            ]
        ),
        "recovery_preregistration": build_recovery_preregistration(),
        "accounting_contract": build_accounting_contract(),
        "holdout_contract": pd.DataFrame(
            [
                {
                    "holdout_id": "RETROSPECTIVE_LOCKBOX_2026H1_V1",
                    "path": "data/holdout/retrospective.csv",
                    "exists": False,
                    "access_allowed": False,
                },
                {
                    "holdout_id": "PROSPECTIVE_HOLDOUT_20260720_20270120_V1",
                    "path": "data/holdout/prospective.csv",
                    "exists": False,
                    "access_allowed": False,
                },
            ]
        ),
        "errors": pd.DataFrame(columns=["scope", "error"]),
    }


def valid_lineage() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "report_name": name,
                "path": str(path),
                "exists": True,
                "size_bytes": 1,
                "sha256": name,
                "rows": 0 if name == "errors" else 1,
                "missing_columns": "",
                "read_error": "",
                "report_valid": True,
            }
            for name, path in PHASE_2B_REQUIRED_REPORTS.items()
        ]
    )


class PreregisteredStrategyRecoveryDiagnosticTests(unittest.TestCase):
    def setUp(self) -> None:
        self.normalized = synthetic_normalized()
        self.profiles = [profile.name for profile in build_cost_profiles()]

    def test_exact_source_profile_grid_rejects_missing_pair(self) -> None:
        valid, _ = validate_normalized_source_grid(
            self.normalized,
            expected_source_rows=6,
            expected_profiles=self.profiles,
        )
        invalid, _ = validate_normalized_source_grid(
            self.normalized.iloc[:-1].copy(),
            expected_source_rows=6,
            expected_profiles=self.profiles,
        )
        self.assertTrue(valid)
        self.assertFalse(invalid)

    def test_volatility_terciles_do_not_use_outcomes(self) -> None:
        _, thresholds_a = build_source_trade_features(self.normalized)
        changed = self.normalized.copy()
        changed["normalized_net_result_r"] = np.linspace(-100.0, 100.0, len(changed))
        _, thresholds_b = build_source_trade_features(changed)

        self.assertAlmostEqual(
            thresholds_a.iloc[0]["lower_threshold"],
            thresholds_b.iloc[0]["lower_threshold"],
        )
        self.assertAlmostEqual(
            thresholds_a.iloc[0]["upper_threshold"],
            thresholds_b.iloc[0]["upper_threshold"],
        )
        self.assertFalse(thresholds_a.iloc[0]["outcome_columns_used"])

    def test_closed_candle_context_fails_on_missing_signal(self) -> None:
        source, _ = build_source_trade_features(self.normalized)
        context = synthetic_context(self.normalized).iloc[:-1].copy()
        with self.assertRaisesRegex(ValueError, "context missing"):
            attach_closed_candle_context(source, context)

    def test_all_preregistered_slices_publish_without_ranking(self) -> None:
        source, _ = build_source_trade_features(self.normalized)
        features = attach_closed_candle_context(
            source,
            synthetic_context(self.normalized),
        )
        enriched = attach_features_to_normalized(self.normalized, features)
        catalog = build_slice_catalog(features, list(SHORT_SYMBOL_COHORT))
        coverage = build_slice_coverage(features, catalog)
        metrics = build_slice_metrics(
            enriched,
            catalog,
            symbols=list(SHORT_SYMBOL_COHORT),
            split_names=list(SHORT_WALK_FORWARD_SPLITS),
            split_years=SPLIT_TEST_YEARS,
            expected_profiles=self.profiles,
        )

        self.assertEqual(set(catalog["slice_dimension"]), set(SLICE_DIMENSIONS))
        self.assertTrue(coverage["coverage_complete"].all())
        self.assertEqual(set(metrics["cost_profile"]), set(self.profiles))
        self.assertFalse(metrics["ranking_allowed"].any())
        self.assertFalse(metrics["selection_allowed"].any())
        self.assertFalse(metrics["candidate_reclassification_allowed"].any())
        self.assertEqual(set(features["signal_family"]), {DIAGNOSTIC_SIGNAL_FAMILY})

    def test_fixed_cohort_cannot_drop_result_unfavorable_symbol(self) -> None:
        source, _ = build_source_trade_features(self.normalized)
        features = attach_closed_candle_context(
            source,
            synthetic_context(self.normalized),
        )
        features = features[features["symbol"].ne("SOLUSDT")].copy()
        enriched = attach_features_to_normalized(
            self.normalized[self.normalized["symbol"].ne("SOLUSDT")].copy(),
            features,
        )
        catalog = build_slice_catalog(features, list(SHORT_SYMBOL_COHORT))
        with self.assertRaisesRegex(ValueError, "symbol=SOLUSDT"):
            build_slice_metrics(
                enriched,
                catalog,
                symbols=list(SHORT_SYMBOL_COHORT),
                split_names=list(SHORT_WALK_FORWARD_SPLITS),
                split_years=SPLIT_TEST_YEARS,
                expected_profiles=self.profiles,
            )

    def test_full_orchestration_completes_without_selection(self) -> None:
        frames = phase_2b_frames(self.normalized)
        dataset_lineage = pd.DataFrame(
            [{"dataset_valid": True, "hash_matches_r2": True}]
        )
        with (
            patch(
                "src.validation.preregistered_strategy_recovery_development_diagnostic_v1.load_phase_2b_reports",
                return_value=(frames, valid_lineage()),
            ),
            patch(
                "src.validation.preregistered_strategy_recovery_development_diagnostic_v1.build_dataset_lineage",
                return_value=(dataset_lineage, True, True),
            ),
            patch(
                "src.validation.preregistered_strategy_recovery_development_diagnostic_v1.build_closed_candle_signal_context",
                return_value=synthetic_context(self.normalized),
            ),
            patch(
                "src.validation.preregistered_strategy_recovery_development_diagnostic_v1.EXPECTED_SOURCE_SHORT_TRADES",
                6,
            ),
            patch(
                "src.validation.preregistered_strategy_recovery_development_diagnostic_v1.write_outputs"
            ),
        ):
            result = validate_phase_10_42r_2c(preflight_only=False)

        summary = result["summary"].iloc[0]
        self.assertTrue(summary["validation_passed"])
        self.assertTrue(summary["diagnostic_completed"])
        self.assertEqual(summary["recommended_next_phase"], NEXT_PHASE)
        self.assertEqual(summary["short_candidate_status"], "RETIRED_REVALIDATED_REJECTED_UNCHANGED")
        self.assertFalse(summary["symbol_selected"])
        self.assertFalse(summary["candidate_ranked"])
        self.assertFalse(summary["candidate_reclassified"])
        self.assertFalse(result["checks"]["blocker"].any())

    def test_preflight_fails_closed_when_dataset_lineage_changes(self) -> None:
        frames = phase_2b_frames(self.normalized)
        dataset_lineage = pd.DataFrame(
            [{"dataset_valid": True, "hash_matches_r2": False}]
        )
        with (
            patch(
                "src.validation.preregistered_strategy_recovery_development_diagnostic_v1.load_phase_2b_reports",
                return_value=(frames, valid_lineage()),
            ),
            patch(
                "src.validation.preregistered_strategy_recovery_development_diagnostic_v1.build_dataset_lineage",
                return_value=(dataset_lineage, True, False),
            ),
            patch(
                "src.validation.preregistered_strategy_recovery_development_diagnostic_v1.EXPECTED_SOURCE_SHORT_TRADES",
                6,
            ),
            patch(
                "src.validation.preregistered_strategy_recovery_development_diagnostic_v1.write_outputs"
            ),
        ):
            result = validate_phase_10_42r_2c(preflight_only=True)

        self.assertFalse(result["summary"].iloc[0]["validation_passed"])
        self.assertGreater(result["summary"].iloc[0]["blocker_count"], 0)
        self.assertTrue(result["slice_metrics"].empty)

    def test_preflight_fails_closed_when_source_count_is_not_205(self) -> None:
        frames = phase_2b_frames(self.normalized)
        dataset_lineage = pd.DataFrame(
            [{"dataset_valid": True, "hash_matches_r2": True}]
        )
        with (
            patch(
                "src.validation.preregistered_strategy_recovery_development_diagnostic_v1.load_phase_2b_reports",
                return_value=(frames, valid_lineage()),
            ),
            patch(
                "src.validation.preregistered_strategy_recovery_development_diagnostic_v1.build_dataset_lineage",
                return_value=(dataset_lineage, True, True),
            ),
            patch(
                "src.validation.preregistered_strategy_recovery_development_diagnostic_v1.write_outputs"
            ),
        ):
            result = validate_phase_10_42r_2c(preflight_only=True)

        failed = result["checks"][~result["checks"]["passed"]]
        self.assertFalse(result["summary"].iloc[0]["validation_passed"])
        self.assertIn(
            "phase_2b_source_summary_contract_exact",
            set(failed["check_name"]),
        )

    def test_holdout_presence_blocks_preflight(self) -> None:
        frames = phase_2b_frames(self.normalized)
        dataset_lineage = pd.DataFrame([{"dataset_valid": True}])
        with (
            patch(
                "src.validation.preregistered_strategy_recovery_development_diagnostic_v1.load_phase_2b_reports",
                return_value=(frames, valid_lineage()),
            ),
            patch(
                "src.validation.preregistered_strategy_recovery_development_diagnostic_v1.build_dataset_lineage",
                return_value=(dataset_lineage, True, True),
            ),
            patch(
                "src.validation.preregistered_strategy_recovery_development_diagnostic_v1.holdout_files_absent",
                return_value=False,
            ),
            patch(
                "src.validation.preregistered_strategy_recovery_development_diagnostic_v1.EXPECTED_SOURCE_SHORT_TRADES",
                6,
            ),
            patch(
                "src.validation.preregistered_strategy_recovery_development_diagnostic_v1.write_outputs"
            ),
        ):
            result = validate_phase_10_42r_2c(preflight_only=True)

        self.assertFalse(result["summary"].iloc[0]["validation_passed"])
        failed = result["checks"][~result["checks"]["passed"]]
        self.assertIn("holdout_files_absent_and_unaccessed", set(failed["check_name"]))

    def test_all_safety_permissions_are_false(self) -> None:
        self.assertTrue(SAFETY_FLAGS)
        self.assertFalse(any(SAFETY_FLAGS.values()))


if __name__ == "__main__":
    unittest.main()
