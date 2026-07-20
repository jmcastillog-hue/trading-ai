from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

from src.integration import openclaw_read_only_research_status_contract_v1 as contract


class OpenClawReadOnlyResearchStatusContractTests(unittest.TestCase):
    def test_phase_and_schema_are_exact(self):
        self.assertEqual(contract.PHASE, "10.42R.3")
        self.assertEqual(
            contract.SCHEMA_VERSION,
            "OPENCLAW_READ_ONLY_RESEARCH_STATUS_CONTRACT_V1",
        )

    def test_source_phase_2l_commit_is_exact(self):
        self.assertEqual(
            contract.SOURCE_ANCHORS["phase_10_42r_2l_commit"],
            "2177f69c1dd221ab9cf0db9a5c40992355a3317c",
        )

    def test_source_bundle_roots_are_exact(self):
        self.assertEqual(
            contract.SOURCE_ANCHORS["phase_10_42r_2k_bundle_root_sha256"],
            "2938dcf9596281a8416b9ecd6f7431cbebee89559063bfe100a11258f76cbd02",
        )
        self.assertEqual(
            contract.SOURCE_ANCHORS["phase_10_42r_2l_audit_bundle_root_sha256"],
            "8f7f9b514f31a6cb98884febf396f9e57ecfbe53b4ebcf844c5752f1d3b055d6",
        )

    def test_read_only_capabilities_are_all_true(self):
        self.assertTrue(all(contract.READ_ONLY_CAPABILITIES.values()))

    def test_prohibited_capabilities_are_all_false(self):
        self.assertTrue(
            all(value is False for value in contract.PROHIBITED_CAPABILITIES.values())
        )

    def test_snapshot_validates(self):
        snapshot = contract.build_status_snapshot(
            generated_at_utc="2026-07-20T00:00:00+00:00"
        )
        contract.validate_status_snapshot(snapshot)

    def test_contract_root_is_deterministic(self):
        first = contract.build_status_snapshot(
            generated_at_utc="2026-07-20T00:00:00+00:00"
        )
        second = contract.build_status_snapshot(
            generated_at_utc="2026-07-21T00:00:00+00:00"
        )
        self.assertEqual(first["contract_root_sha256"], second["contract_root_sha256"])

    def test_generated_timestamp_is_not_root_material(self):
        snapshot = contract.build_status_snapshot(
            generated_at_utc="2026-07-20T00:00:00+00:00"
        )
        mutated = copy.deepcopy(snapshot)
        mutated["contract"]["generated_at_utc"] = "2030-01-01T00:00:00+00:00"
        self.assertEqual(
            snapshot["contract_root_sha256"],
            contract.calculate_contract_root(mutated),
        )

    def test_material_mutation_changes_root(self):
        snapshot = contract.build_status_snapshot(
            generated_at_utc="2026-07-20T00:00:00+00:00"
        )
        mutated = copy.deepcopy(snapshot)
        mutated["evidence_summary"]["short_recovery_surviving_variant_count"] = 1
        self.assertNotEqual(
            snapshot["contract_root_sha256"],
            contract.calculate_contract_root(mutated),
        )

    def test_material_mutation_is_rejected(self):
        snapshot = contract.build_status_snapshot(
            generated_at_utc="2026-07-20T00:00:00+00:00"
        )
        snapshot["master_disposition"]["legacy_short_candidate"] = "APPROVED"
        with self.assertRaises(contract.StatusContractError):
            contract.validate_status_snapshot(snapshot)

    def test_operational_permission_mutation_is_rejected(self):
        snapshot = contract.build_status_snapshot(
            generated_at_utc="2026-07-20T00:00:00+00:00"
        )
        snapshot["permissions"]["prohibited_capabilities"][
            "paper_trade_execution_allowed"
        ] = True
        snapshot["contract_root_sha256"] = contract.calculate_contract_root(snapshot)
        with self.assertRaises(contract.StatusContractError):
            contract.validate_status_snapshot(snapshot)

    def test_short_recovery_disposition_is_closed(self):
        self.assertEqual(
            contract.MASTER_DISPOSITION["short_recovery_line"],
            "CLOSED_ALL_VARIANTS_REJECTED",
        )
        self.assertEqual(contract.EVIDENCE_SUMMARY["short_recovery_variant_count"], 6)
        self.assertEqual(
            contract.EVIDENCE_SUMMARY["short_recovery_rejected_variant_count"], 6
        )
        self.assertEqual(
            contract.EVIDENCE_SUMMARY["short_recovery_surviving_variant_count"], 0
        )

    def test_long_candidates_remain_research_only(self):
        self.assertIn(
            "RESEARCH_ONLY",
            contract.MASTER_DISPOSITION["long_primary_candidate"],
        )
        self.assertIn(
            "WATCHLIST_ONLY",
            contract.MASTER_DISPOSITION["long_secondary_candidate"],
        )

    def test_long_schema_candidate_has_zero_evidence(self):
        self.assertEqual(
            contract.EVIDENCE_SUMMARY["long_empty_schema_column_count"], 54
        )
        self.assertEqual(
            contract.EVIDENCE_SUMMARY["long_official_evidence_row_count"], 0
        )

    def test_lockboxes_are_sealed(self):
        self.assertEqual(
            contract.MASTER_DISPOSITION["retrospective_lockbox"], "SEALED"
        )
        self.assertEqual(
            contract.MASTER_DISPOSITION["prospective_holdout"], "SEALED"
        )

    def test_phase_10_43_route_is_preserved(self):
        self.assertEqual(
            contract.PHASE_10_43_ROUTE,
            "PHASE_10_43_LONG_FORWARD_OBSERVATION_EVIDENCE_COLLECTION_"
            "OFFICIAL_DATASET_ATOMIC_WRITE_HARNESS_DESIGN_REVIEW_V1",
        )

    def test_openclaw_next_route_is_separate(self):
        self.assertEqual(
            contract.OPENCLAW_NEXT_ROUTE,
            "PHASE_10_42R_4_OPENCLAW_READ_ONLY_RESEARCH_STATUS_"
            "EXPORT_IMPLEMENTATION_V1",
        )

    def test_openclaw_runtime_is_not_implemented(self):
        snapshot = contract.build_status_snapshot(
            generated_at_utc="2026-07-20T00:00:00+00:00"
        )
        self.assertEqual(
            snapshot["openclaw_policy"]["runtime_integration_status"],
            "NOT_IMPLEMENTED",
        )
        self.assertFalse(
            snapshot["permissions"]["prohibited_capabilities"][
                "openclaw_runtime_status_consumption_allowed"
            ]
        )

    def test_openclaw_cannot_override_permissions(self):
        snapshot = contract.build_status_snapshot(
            generated_at_utc="2026-07-20T00:00:00+00:00"
        )
        self.assertFalse(
            snapshot["openclaw_policy"]["permission_override_allowed"]
        )
        self.assertTrue(snapshot["openclaw_policy"]["human_decision_required"])

    def test_failure_mode_is_fail_closed(self):
        snapshot = contract.build_status_snapshot(
            generated_at_utc="2026-07-20T00:00:00+00:00"
        )
        self.assertEqual(
            snapshot["openclaw_policy"]["required_failure_mode"], "FAIL_CLOSED"
        )
        self.assertFalse(snapshot["openclaw_policy"]["stale_snapshot_use_allowed"])
        self.assertFalse(
            snapshot["openclaw_policy"]["schema_mismatch_use_allowed"]
        )

    def test_top_level_inventory_is_exact(self):
        snapshot = contract.build_status_snapshot(
            generated_at_utc="2026-07-20T00:00:00+00:00"
        )
        self.assertEqual(
            set(snapshot),
            {
                "contract",
                "source_anchors",
                "master_disposition",
                "evidence_summary",
                "permissions",
                "openclaw_policy",
                "next_routes",
                "contract_root_sha256",
            },
        )

    def test_canonical_json_rejects_nan(self):
        with self.assertRaises(ValueError):
            contract.canonical_json({"value": float("nan")})

    def test_schema_file_has_exact_top_level_contract(self):
        schema_path = Path(
            "schemas/openclaw_read_only_research_status_contract_v1.schema.json"
        )
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        self.assertEqual(
            set(schema["required"]),
            {
                "contract",
                "source_anchors",
                "master_disposition",
                "evidence_summary",
                "permissions",
                "openclaw_policy",
                "next_routes",
                "contract_root_sha256",
            },
        )
        self.assertFalse(schema["additionalProperties"])

    def test_contract_source_contains_no_execution_imports(self):
        source = Path(
            "src/integration/openclaw_read_only_research_status_contract_v1.py"
        ).read_text(encoding="utf-8")
        forbidden = (
            "python-binance",
            "from binance",
            "import ccxt",
            "subprocess",
            "requests.",
        )
        self.assertTrue(all(token not in source for token in forbidden))


if __name__ == "__main__":
    unittest.main()
