from __future__ import annotations

import json
import unittest
from unittest.mock import patch

import pandas as pd

from src.analysis.recovery_candidate_family_specification_v1 import (
    FAMILY_LIMIT,
    FIXED_SYMBOLS,
    FROZEN_VARIANT_COUNT,
    EXPECTED_SPECIFICATION_ROOT_SHA256,
    MULTIPLICITY_METHOD,
    SOURCE_BASELINE_COMMIT,
    SOURCE_PHASE_2C_ARCHIVE_SHA256,
    VARIANT_LIMIT_PER_FAMILY,
    build_specification_artifacts,
    build_specification_manifest,
    canonical_frame_payload,
    canonical_sha256,
    validate_new_identifiers_and_no_evaluation,
    validate_registry_limits,
    verify_specification_manifest,
)
from src.validation.cost_accounting_normalization_and_strategy_recovery_preregistration_v1 import (
    build_recovery_preregistration,
)
from src.validation.recovery_candidate_family_specification_and_multiplicity_freeze_v1 import (
    NEXT_PHASE,
    PHASE_2C_REPORT_CONTRACT,
    SAFETY_FLAGS,
    specification_imports_are_safe,
    validate_phase_10_42r_2d,
)


def phase_2c_frames() -> dict[str, pd.DataFrame]:
    return {
        "summary": pd.DataFrame(
            [
                {
                    "diagnostic_completed": True,
                    "validation_passed": True,
                    "source_short_trades": 205,
                    "normalized_trade_profile_rows": 1025,
                    "diagnostic_metric_rows": 60,
                    "blocker_count": 0,
                    "error_rows": 0,
                    "short_candidate_status": "RETIRED_REVALIDATED_REJECTED_UNCHANGED",
                    "long_candidate_status": "RESEARCH_ONLY_NOT_APPROVED_UNCHANGED",
                    "candidate_reclassified": False,
                    "execution_allowed": False,
                    "automation_allowed": False,
                    "openclaw_operational_integration_allowed": False,
                }
            ]
        ),
        "checks": pd.DataFrame(
            [
                {
                    "check_name": f"phase_2c_check_{index:02d}",
                    "passed": True,
                    "blocker": False,
                }
                for index in range(1, 27)
            ]
        ),
        "errors": pd.DataFrame(columns=["scope", "error"]),
        "preregistration": build_recovery_preregistration(),
        "holdout": pd.DataFrame(
            [
                {
                    "holdout_id": "RETROSPECTIVE_LOCKBOX_2026H1_V1",
                    "exists": False,
                    "access_allowed": False,
                    "phase_10_42r_2c_access_allowed": False,
                    "phase_10_42r_2c_accessed": False,
                },
                {
                    "holdout_id": "PROSPECTIVE_HOLDOUT_20260720_20270120_V1",
                    "exists": False,
                    "access_allowed": False,
                    "phase_10_42r_2c_access_allowed": False,
                    "phase_10_42r_2c_accessed": False,
                },
            ]
        ),
    }


def phase_2c_lineage(exact: bool = True) -> pd.DataFrame:
    semantic = {
        "summary_v1.csv",
        "checks_v1.csv",
        "errors_v1.csv",
        "preregistration_snapshot_v1.csv",
        "holdout_contract_snapshot_v1.csv",
    }
    return pd.DataFrame(
        [
            {
                "report_order": order,
                "report_name": filename,
                "path": filename,
                "exists": True,
                "expected_sha256": contract["sha256"],
                "actual_sha256": contract["sha256"] if exact else "bad",
                "hash_matches": exact,
                "expected_size_bytes": contract["size_bytes"],
                "actual_size_bytes": contract["size_bytes"],
                "size_matches": True,
                "expected_rows": contract["rows"],
                "actual_rows": contract["rows"],
                "row_count_matches": True,
                "semantic_content_loaded": filename in semantic,
                "read_error": "",
                "report_exact": exact,
            }
            for order, (filename, contract) in enumerate(
                PHASE_2C_REPORT_CONTRACT.items(),
                start=1,
            )
        ]
    )


class RecoveryCandidateSpecificationFreezeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.artifacts = build_specification_artifacts()
        self.manifest, self.root = build_specification_manifest(self.artifacts)

    def test_canonical_sha_is_independent_of_dictionary_key_order(self) -> None:
        self.assertEqual(
            canonical_sha256({"a": 1, "b": 2}),
            canonical_sha256({"b": 2, "a": 1}),
        )

    def test_root_hash_is_deterministic(self) -> None:
        artifacts_b = build_specification_artifacts()
        manifest_b, root_b = build_specification_manifest(artifacts_b)
        self.assertEqual(
            canonical_frame_payload(self.manifest),
            canonical_frame_payload(manifest_b),
        )
        self.assertEqual(
            self.root.iloc[0]["specification_root_sha256"],
            root_b.iloc[0]["specification_root_sha256"],
        )
        self.assertEqual(
            self.root.iloc[0]["specification_root_sha256"],
            EXPECTED_SPECIFICATION_ROOT_SHA256,
        )
        self.assertEqual(
            self.root.iloc[0]["source_baseline_commit"],
            SOURCE_BASELINE_COMMIT,
        )
        self.assertEqual(
            self.root.iloc[0]["source_phase_2c_archive_sha256"],
            SOURCE_PHASE_2C_ARCHIVE_SHA256,
        )

    def test_manifest_detects_tampered_variant_parameter(self) -> None:
        tampered = {name: frame.copy() for name, frame in self.artifacts.items()}
        variants = tampered["candidate_variant_registry"]
        parameters = json.loads(variants.loc[0, "parameter_json"])
        parameters["stop_atr_buffer"] = 99.0
        variants.loc[0, "parameter_json"] = json.dumps(parameters)
        valid, _ = verify_specification_manifest(tampered, self.manifest, self.root)
        self.assertFalse(valid)

    def test_family_limit_rejects_a_fourth_family(self) -> None:
        families = self.artifacts["candidate_family_registry"].copy()
        fourth = families.iloc[[0]].copy()
        fourth["family_id"] = "RCV_SHORT_NEW_F04_V1"
        fourth["family_order"] = 4
        families = pd.concat([families, fourth], ignore_index=True)
        valid, _ = validate_registry_limits(
            families,
            self.artifacts["candidate_variant_registry"],
        )
        self.assertEqual(FAMILY_LIMIT, 3)
        self.assertFalse(valid)

    def test_variant_limit_rejects_five_variants_in_one_family(self) -> None:
        families = self.artifacts["candidate_family_registry"]
        variants = self.artifacts["candidate_variant_registry"].copy()
        source = variants[variants["family_order"].eq(1)].iloc[[0]]
        extras = []
        for order in (3, 4, 5):
            extra = source.copy()
            extra["variant_id"] = f"RCV_SHORT_UPSIDE_SWEEP_REVERSAL_F01_EXTRA_{order}"
            extra["variant_order_within_family"] = order
            extra["evaluation_order"] = len(variants) + len(extras) + 1
            extras.append(extra)
        variants = pd.concat([variants, *extras], ignore_index=True)
        valid, _ = validate_registry_limits(families, variants)
        self.assertEqual(VARIANT_LIMIT_PER_FAMILY, 4)
        self.assertFalse(valid)

    def test_retired_identifier_token_is_rejected(self) -> None:
        families = self.artifacts["candidate_family_registry"].copy()
        families.loc[0, "family_id"] = "RCV_FIB_V5_REPAIR_F01"
        valid, details = validate_new_identifiers_and_no_evaluation(
            families,
            self.artifacts["candidate_variant_registry"],
        )
        self.assertFalse(valid)
        self.assertIn("FIB_V5", details)

    def test_all_registries_are_unevaluated_and_unranked(self) -> None:
        families = self.artifacts["candidate_family_registry"]
        variants = self.artifacts["candidate_variant_registry"]
        valid, _ = validate_new_identifiers_and_no_evaluation(
            families,
            variants,
        )
        self.assertTrue(valid)
        self.assertFalse(families["evaluated"].any())
        self.assertFalse(variants["evaluated"].any())
        self.assertTrue(variants["result_rows"].eq(0).all())

    def test_fixed_cohort_and_closed_candle_timing_are_locked(self) -> None:
        common = self.artifacts["common_execution_contract"]
        values = {
            row.contract_key: json.loads(row.locked_value_json)
            for row in common.itertuples(index=False)
        }
        self.assertEqual(values["fixed_symbol_cohort"], list(FIXED_SYMBOLS))
        self.assertEqual(
            values["higher_timeframe_availability"],
            "CLOSED_CANDLE_CORRECTED",
        )
        self.assertEqual(values["fill_contract"], "NEXT_15M_BAR_OPEN_T_PLUS_1")
        self.assertFalse(values["retired_reference_import_allowed"])
        self.assertFalse(values["evaluation_allowed_in_phase_2d"])

    def test_multiplicity_scope_is_all_six_variants(self) -> None:
        contract = self.artifacts["multiplicity_contract"]
        values = {
            row.contract_key: json.loads(row.locked_value_json)
            for row in contract.itertuples(index=False)
        }
        self.assertEqual(values["frozen_total_variant_count"], FROZEN_VARIANT_COUNT)
        self.assertEqual(values["multiplicity_method"], MULTIPLICITY_METHOD)
        self.assertEqual(values["correction_scope"], "ALL_6_VARIANTS_SINGLE_FAMILY_WISE_POOL")
        self.assertFalse(values["performance_ranking_allowed"])

    def test_promotion_gates_lock_evidence_and_stress(self) -> None:
        gates = self.artifacts["promotion_gate_contract"].set_index("metric")
        self.assertEqual(gates.loc["AGGREGATE_OOS_TRADE_COUNT", "threshold_json"], "100")
        self.assertEqual(gates.loc["MINIMUM_OOS_TRADES_PER_SYMBOL", "threshold_json"], "20")
        self.assertEqual(gates.loc["STRESS_NORMALIZED_AVERAGE_RESULT_R", "threshold_json"], "0.0")
        self.assertFalse(gates["override_allowed"].any())

    def test_specification_module_has_no_project_runtime_import(self) -> None:
        valid, details = specification_imports_are_safe()
        self.assertTrue(valid, details)
        self.assertNotIn("src.", details)

    def test_full_orchestration_freezes_without_evaluation(self) -> None:
        with (
            patch(
                "src.validation.recovery_candidate_family_specification_and_multiplicity_freeze_v1.load_phase_2c_report_lineage",
                return_value=(phase_2c_frames(), phase_2c_lineage()),
            ),
            patch(
                "src.validation.recovery_candidate_family_specification_and_multiplicity_freeze_v1.write_outputs"
            ),
            patch(
                "src.validation.recovery_candidate_family_specification_and_multiplicity_freeze_v1.holdout_files_absent",
                return_value=True,
            ),
            patch(
                "src.validation.recovery_candidate_family_specification_and_multiplicity_freeze_v1.official_forward_artifacts_absent",
                return_value=True,
            ),
        ):
            result = validate_phase_10_42r_2d(preflight_only=False)

        summary = result["summary"].iloc[0]
        self.assertTrue(summary["validation_passed"])
        self.assertTrue(summary["specification_completed"])
        self.assertEqual(summary["family_count"], 3)
        self.assertEqual(summary["variant_count"], 6)
        self.assertEqual(summary["candidate_result_rows"], 0)
        self.assertFalse(summary["winner_selected"])
        self.assertEqual(summary["recommended_next_phase"], NEXT_PHASE)
        self.assertEqual(summary["total_checks"], 28)

    def test_preflight_writes_only_empty_specification_schemas(self) -> None:
        with (
            patch(
                "src.validation.recovery_candidate_family_specification_and_multiplicity_freeze_v1.load_phase_2c_report_lineage",
                return_value=(phase_2c_frames(), phase_2c_lineage()),
            ),
            patch(
                "src.validation.recovery_candidate_family_specification_and_multiplicity_freeze_v1.write_outputs"
            ),
            patch(
                "src.validation.recovery_candidate_family_specification_and_multiplicity_freeze_v1.holdout_files_absent",
                return_value=True,
            ),
            patch(
                "src.validation.recovery_candidate_family_specification_and_multiplicity_freeze_v1.official_forward_artifacts_absent",
                return_value=True,
            ),
        ):
            result = validate_phase_10_42r_2d(preflight_only=True)

        self.assertTrue(result["summary"].iloc[0]["validation_passed"])
        self.assertFalse(result["summary"].iloc[0]["specification_completed"])
        self.assertTrue(result["candidate_family_registry"].empty)
        self.assertTrue(result["candidate_variant_registry"].empty)

    def test_source_hash_mismatch_fails_closed(self) -> None:
        with (
            patch(
                "src.validation.recovery_candidate_family_specification_and_multiplicity_freeze_v1.load_phase_2c_report_lineage",
                return_value=(phase_2c_frames(), phase_2c_lineage(exact=False)),
            ),
            patch(
                "src.validation.recovery_candidate_family_specification_and_multiplicity_freeze_v1.write_outputs"
            ),
            patch(
                "src.validation.recovery_candidate_family_specification_and_multiplicity_freeze_v1.holdout_files_absent",
                return_value=True,
            ),
            patch(
                "src.validation.recovery_candidate_family_specification_and_multiplicity_freeze_v1.official_forward_artifacts_absent",
                return_value=True,
            ),
        ):
            result = validate_phase_10_42r_2d(preflight_only=True)

        self.assertFalse(result["summary"].iloc[0]["validation_passed"])
        self.assertTrue(result["candidate_family_registry"].empty)
        self.assertGreater(result["summary"].iloc[0]["blocker_count"], 0)

    def test_holdout_presence_fails_closed(self) -> None:
        with (
            patch(
                "src.validation.recovery_candidate_family_specification_and_multiplicity_freeze_v1.load_phase_2c_report_lineage",
                return_value=(phase_2c_frames(), phase_2c_lineage()),
            ),
            patch(
                "src.validation.recovery_candidate_family_specification_and_multiplicity_freeze_v1.write_outputs"
            ),
            patch(
                "src.validation.recovery_candidate_family_specification_and_multiplicity_freeze_v1.holdout_files_absent",
                return_value=False,
            ),
            patch(
                "src.validation.recovery_candidate_family_specification_and_multiplicity_freeze_v1.official_forward_artifacts_absent",
                return_value=True,
            ),
        ):
            result = validate_phase_10_42r_2d(preflight_only=True)

        failed = result["checks"][~result["checks"]["passed"]]
        self.assertFalse(result["summary"].iloc[0]["validation_passed"])
        self.assertIn("phase_2d_holdout_files_absent", set(failed["check_name"]))

    def test_all_permissions_are_false(self) -> None:
        self.assertTrue(SAFETY_FLAGS)
        self.assertFalse(any(SAFETY_FLAGS.values()))


if __name__ == "__main__":
    unittest.main()
