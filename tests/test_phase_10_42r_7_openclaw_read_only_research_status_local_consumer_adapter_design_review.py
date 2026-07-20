from __future__ import annotations

import copy
import unittest

from src.integration import openclaw_read_only_research_status_local_consumer_adapter_design_review_v1 as review


def build_valid_design() -> dict:
    response = {
        "adapter_schema_version": review.SOURCE_DESIGN_SCHEMA_VERSION,
        "adapter_mode": review.SOURCE_ADAPTER_MODE,
        "decision": "VALIDATED_RESEARCH_STATUS_AVAILABLE_FOR_HUMAN_EXPLANATION_ONLY",
        "source": {
            "source_review_commit": review.SOURCE_REVIEW_COMMIT,
            "contract_root_sha256": review.SOURCE_CONTRACT_ROOT_SHA256,
            "snapshot_sha256": review.SOURCE_SNAPSHOT_SHA256,
            "manifest_sha256": review.SOURCE_EXPORT_MANIFEST_SHA256,
            "snapshot_size_bytes": review.SOURCE_SNAPSHOT_SIZE_BYTES,
        },
        "research_status": {
            "legacy_short_candidate": "REVALIDATED_REJECTED",
            "short_recovery_line": "CLOSED_ALL_VARIANTS_REJECTED",
            "short_recovery_surviving_variant_count": 0,
            "long_primary_candidate": "RESEARCH_ONLY_CERTIFIED_UNAFFECTED_AND_CONSISTENCY_REVALIDATED",
            "long_secondary_candidate": "WATCHLIST_ONLY_CERTIFIED_UNAFFECTED_AND_CONSISTENCY_REVALIDATED",
            "long_official_evidence_row_count": 0,
            "retrospective_lockbox": "SEALED",
            "prospective_holdout": "SEALED",
            "total_project_completed": False,
        },
        "restrictions": {
            "human_explanation_only": True,
            "actionable_trading_fields_present": False,
            "openclaw_runtime_status_consumption_allowed": False,
            "openclaw_tool_invocation_allowed": False,
            "openclaw_operational_integration_allowed": False,
            "signal_generation_enabled": False,
            "paper_trade_execution_allowed": False,
            "real_capital_allowed": False,
            "market_execution_allowed": False,
            "automation_allowed": False,
        },
        "human_review": {
            "required": True,
            "permission_override_allowed": False,
            "unknown_status_inference_allowed": False,
        },
        "next_routes": {
            "adapter_track": review.SOURCE_RECOMMENDED_ROUTE,
            "long_dataset_track": review.PHASE_10_43_ROUTE,
            "route_independence": True,
        },
    }
    design = {
        "phase": "10.42R.6",
        "schema_version": review.SOURCE_DESIGN_SCHEMA_VERSION,
        "adapter_mode": review.SOURCE_ADAPTER_MODE,
        "decision_boundary": {
            "design_only": True,
            "implementation_allowed": False,
            "runtime_integration_allowed": False,
            "tool_registration_allowed": False,
            "human_review_required": True,
            "python_source_of_truth": True,
        },
        "source_authority": {
            "source_review_commit": review.SOURCE_REVIEW_COMMIT,
            "source_review_module_sha256": review.SOURCE_REVIEW_MODULE_SHA256,
            "source_review_document_sha256": review.SOURCE_REVIEW_DOCUMENT_SHA256,
            "contract_root_sha256": review.SOURCE_CONTRACT_ROOT_SHA256,
            "snapshot_sha256": review.SOURCE_SNAPSHOT_SHA256,
            "manifest_sha256": review.SOURCE_EXPORT_MANIFEST_SHA256,
            "snapshot_size_bytes": review.SOURCE_SNAPSHOT_SIZE_BYTES,
        },
        "request_contract": {
            "exact_fields": list(review.REQUEST_FIELDS),
            "operation": review.ALLOWED_OPERATION,
            "response_profile": review.ALLOWED_RESPONSE_PROFILE,
            "require_human_review": True,
            "allow_actionable_fields": False,
            "additional_fields_allowed": False,
        },
        "response_contract": {
            "exact_top_level_fields": list(review.RESPONSE_FIELDS),
            "additional_top_level_fields_allowed": False,
            "forbidden_actionable_fields": list(review.FORBIDDEN_ACTIONABLE_FIELDS),
            "actionable_trading_content_allowed": False,
            "human_explanation_only": True,
        },
        "validation_sequence": list(review.VALIDATION_SEQUENCE),
        "read_boundary": copy.deepcopy(review.READ_BOUNDARY),
        "write_boundary": copy.deepcopy(review.WRITE_BOUNDARY),
        "transport_boundary": copy.deepcopy(review.TRANSPORT_BOUNDARY),
        "operational_permissions": {name: False for name in review.OPERATIONAL_PERMISSION_NAMES},
        "error_registry": dict(review.ERROR_REGISTRY),
        "exit_code_contract": {
            "success": 0,
            "invalid_request_range": [20, 21],
            "integrity_failure_range": [22, 24],
            "response_boundary_range": [25, 28],
            "internal_fail_closed": 70,
            "nonzero_on_any_failure": True,
        },
        "sample_request": {
            "operation": review.ALLOWED_OPERATION,
            "response_profile": review.ALLOWED_RESPONSE_PROFILE,
            "require_human_review": True,
            "allow_actionable_fields": False,
        },
        "sample_response": response,
        "next_routes": {
            "adapter_track": review.SOURCE_RECOMMENDED_ROUTE,
            "long_dataset_track": review.PHASE_10_43_ROUTE,
            "route_independence": True,
            "phase_10_43_design_review_allowed": True,
            "runtime_integration_allowed": False,
        },
        "total_project_completed": False,
    }
    design["design_root_sha256"] = review.independent_design_root(design)
    return design


class AdapterDesignReviewTests(unittest.TestCase):
    def setUp(self) -> None:
        self.design = build_valid_design()

    def assert_rejected(self, value: dict) -> None:
        with self.assertRaises(review.AdapterDesignReviewError):
            review.review_design_value(value)

    def test_phase_exact(self): self.assertEqual(review.PHASE, "10.42R.7")
    def test_source_commit_exact(self): self.assertEqual(review.SOURCE_DESIGN_COMMIT, "45d22e5dc242fd0f475135182c32b37b2c4d4a4c")
    def test_design_root_exact(self): self.assertEqual(review.SOURCE_DESIGN_ROOT_SHA256, "b7336e60c705841f3ff313016816d9115fb46485d67d3a016d0206ab43d89e21")
    def test_valid_design_passes(self): self.assertTrue(review.review_design_value(self.design)["review_passed"])
    def test_root_reproduces(self): self.assertEqual(review.independent_design_root(self.design), review.SOURCE_DESIGN_ROOT_SHA256)
    def test_request_field_count(self): self.assertEqual(len(review.REQUEST_FIELDS), 4)
    def test_response_field_count(self): self.assertEqual(len(review.RESPONSE_FIELDS), 8)
    def test_validation_gate_count(self): self.assertEqual(len(review.VALIDATION_SEQUENCE), 11)
    def test_error_code_count(self): self.assertEqual(len(review.ERROR_REGISTRY), 10)
    def test_permission_count(self): self.assertEqual(len(review.OPERATIONAL_PERMISSION_NAMES), 23)
    def test_forbidden_field_count(self): self.assertEqual(len(review.FORBIDDEN_ACTIONABLE_FIELDS), 15)
    def test_single_operation(self): self.assertEqual(review.ALLOWED_OPERATION, "GET_VALIDATED_RESEARCH_STATUS")
    def test_request_passes(self): review.review_request_value(self.design["sample_request"])
    def test_response_passes(self): review.review_response_value(self.design["sample_response"])

    def test_reject_root_change(self):
        value = copy.deepcopy(self.design); value["design_root_sha256"] = "0" * 64; self.assert_rejected(value)
    def test_reject_implementation(self):
        value = copy.deepcopy(self.design); value["decision_boundary"]["implementation_allowed"] = True; self.assert_rejected(value)
    def test_reject_runtime(self):
        value = copy.deepcopy(self.design); value["decision_boundary"]["runtime_integration_allowed"] = True; self.assert_rejected(value)
    def test_reject_tool_registration(self):
        value = copy.deepcopy(self.design); value["decision_boundary"]["tool_registration_allowed"] = True; self.assert_rejected(value)
    def test_reject_network(self):
        value = copy.deepcopy(self.design); value["transport_boundary"]["network_allowed"] = True; self.assert_rejected(value)
    def test_reject_arbitrary_path(self):
        value = copy.deepcopy(self.design); value["read_boundary"]["arbitrary_path_override_allowed"] = True; self.assert_rejected(value)
    def test_reject_symlink(self):
        value = copy.deepcopy(self.design); value["read_boundary"]["symbolic_links_allowed"] = True; self.assert_rejected(value)
    def test_reject_permission(self):
        value = copy.deepcopy(self.design); value["operational_permissions"]["automation_allowed"] = True; self.assert_rejected(value)
    def test_reject_duplicate_code(self):
        value = copy.deepcopy(self.design); value["error_registry"]["ADAPTER_E010_INTERNAL_FAIL_CLOSED"] = 20; self.assert_rejected(value)
    def test_reject_reordered_sequence(self):
        value = copy.deepcopy(self.design); value["validation_sequence"] = list(reversed(review.VALIDATION_SEQUENCE)); self.assert_rejected(value)
    def test_reject_request_extra_field(self):
        with self.assertRaises(review.AdapterDesignReviewError): review.review_request_value({**self.design["sample_request"], "symbol": "BTCUSDT"})
    def test_reject_unsupported_operation(self):
        with self.assertRaises(review.AdapterDesignReviewError): review.review_request_value({**self.design["sample_request"], "operation": "PLACE_ORDER"})
    def test_reject_human_review_false(self):
        with self.assertRaises(review.AdapterDesignReviewError): review.review_request_value({**self.design["sample_request"], "require_human_review": False})
    def test_reject_actionable_request(self):
        with self.assertRaises(review.AdapterDesignReviewError): review.review_request_value({**self.design["sample_request"], "allow_actionable_fields": True})
    def test_reject_actionable_response(self):
        with self.assertRaises(review.AdapterDesignReviewError): review.review_response_value({**self.design["sample_response"], "entry_price": 100.0})
    def test_next_route_is_implementation(self): self.assertIn("IMPLEMENTATION_V1", review.RECOMMENDED_NEXT_PHASE)


if __name__ == "__main__":
    unittest.main()
