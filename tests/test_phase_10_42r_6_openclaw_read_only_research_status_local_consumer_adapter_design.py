from __future__ import annotations

import copy
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from src.integration import (
    openclaw_read_only_research_status_local_consumer_adapter_design_v1 as design,
)
from src.validation.phase_10_42r_6_openclaw_read_only_research_status_local_consumer_adapter_design_v1 import (
    PACKAGE_FILES,
    PACKAGE_MANIFEST_PATH,
    SOURCE_REVIEW_DOCUMENT_PATH,
    SOURCE_REVIEW_MANIFEST_PATH,
    SOURCE_REVIEW_MODULE_PATH,
    validate_json_schema_subset,
    validate_phase_10_42r_6,
)


ROOT = Path(__file__).resolve().parents[1]


class LocalConsumerAdapterDesignTests(unittest.TestCase):
    def _fixture_root(self) -> Path:
        temporary = Path(tempfile.mkdtemp(prefix="phase10_42r_6_test_"))
        self.addCleanup(lambda: shutil.rmtree(temporary, ignore_errors=True))
        for relative in (*PACKAGE_FILES, PACKAGE_MANIFEST_PATH):
            source = ROOT / relative
            destination = temporary / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)
        for relative in (SOURCE_REVIEW_DOCUMENT_PATH, SOURCE_REVIEW_MODULE_PATH):
            destination = temporary / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text("fixture\n", encoding="utf-8", newline="\n")
        source_manifest = temporary / SOURCE_REVIEW_MANIFEST_PATH
        source_manifest.write_text("", encoding="utf-8", newline="\n")
        return temporary

    def test_phase_is_exact(self):
        self.assertEqual(design.PHASE, "10.42R.6")

    def test_schema_version_is_exact(self):
        self.assertEqual(
            design.SCHEMA_VERSION,
            "OPENCLAW_READ_ONLY_RESEARCH_STATUS_LOCAL_CONSUMER_ADAPTER_DESIGN_V1",
        )

    def test_adapter_mode_is_design_only(self):
        self.assertEqual(
            design.ADAPTER_MODE,
            "DESIGN_ONLY_LOCAL_READ_ONLY_NO_RUNTIME_INTEGRATION",
        )

    def test_source_review_commit_is_exact(self):
        self.assertEqual(
            design.SOURCE_REVIEW_COMMIT,
            "7e6d180f0cee72437e086eff0b0596a64f22ea78",
        )

    def test_source_hashes_are_exact(self):
        self.assertEqual(len(design.SOURCE_REVIEW_MODULE_SHA256), 64)
        self.assertEqual(len(design.SOURCE_REVIEW_DOCUMENT_SHA256), 64)

    def test_design_root_is_exact(self):
        self.assertEqual(
            design.DESIGN_ROOT_SHA256,
            "b7336e60c705841f3ff313016816d9115fb46485d67d3a016d0206ab43d89e21",
        )

    def test_design_root_is_deterministic(self):
        first = design.build_adapter_design()
        second = design.build_adapter_design()
        self.assertEqual(first, second)
        self.assertEqual(first["design_root_sha256"], design.DESIGN_ROOT_SHA256)

    def test_adapter_design_validates(self):
        value = design.build_adapter_design()
        self.assertIsNone(design.validate_adapter_design(value))

    def test_request_contract_validates(self):
        self.assertIsNone(design.validate_request(design.sample_request()))

    def test_request_rejects_extra_field(self):
        value = design.sample_request()
        value["extra"] = True
        with self.assertRaises(design.AdapterDesignError):
            design.validate_request(value)

    def test_request_rejects_unsupported_operation(self):
        value = design.sample_request()
        value["operation"] = "PLACE_ORDER"
        with self.assertRaises(design.AdapterDesignError):
            design.validate_request(value)

    def test_request_rejects_actionable_fields(self):
        value = design.sample_request()
        value["allow_actionable_fields"] = True
        with self.assertRaises(design.AdapterDesignError):
            design.validate_request(value)

    def test_request_requires_human_review(self):
        value = design.sample_request()
        value["require_human_review"] = False
        with self.assertRaises(design.AdapterDesignError):
            design.validate_request(value)

    def test_response_contract_validates(self):
        self.assertIsNone(design.validate_response(design.sample_response()))

    def test_response_fields_are_exact(self):
        self.assertEqual(set(design.sample_response()), set(design.RESPONSE_FIELDS))

    def test_response_rejects_extra_top_level_field(self):
        value = design.sample_response()
        value["extra"] = True
        with self.assertRaises(design.AdapterDesignError):
            design.validate_response(value)

    def test_response_rejects_actionable_nested_field(self):
        value = design.sample_response()
        value["research_status"]["entry_price"] = 100
        with self.assertRaises(design.AdapterDesignError):
            design.validate_response(value)

    def test_response_rejects_runtime_permission(self):
        value = design.sample_response()
        value["restrictions"]["openclaw_runtime_status_consumption_allowed"] = True
        with self.assertRaises(design.AdapterDesignError):
            design.validate_response(value)

    def test_response_rejects_tool_invocation_permission(self):
        value = design.sample_response()
        value["restrictions"]["openclaw_tool_invocation_allowed"] = True
        with self.assertRaises(design.AdapterDesignError):
            design.validate_response(value)

    def test_operational_permissions_are_all_false(self):
        self.assertTrue(all(value is False for value in design.OPERATIONAL_PERMISSIONS.values()))
        self.assertEqual(len(design.OPERATIONAL_PERMISSIONS), 23)

    def test_read_boundary_is_exact_two_files(self):
        self.assertEqual(design.READ_BOUNDARY["exact_file_count"], 2)
        self.assertEqual(len(design.READ_BOUNDARY["allowed_files"]), 2)
        self.assertFalse(design.READ_BOUNDARY["arbitrary_path_override_allowed"])

    def test_write_boundary_disables_filesystem_writes(self):
        self.assertFalse(design.WRITE_BOUNDARY["filesystem_write_allowed"])
        self.assertFalse(design.WRITE_BOUNDARY["cache_write_allowed"])

    def test_transport_boundary_disables_runtime(self):
        self.assertFalse(design.TRANSPORT_BOUNDARY["transport_implemented_in_this_phase"])
        self.assertFalse(design.TRANSPORT_BOUNDARY["network_allowed"])
        self.assertFalse(design.TRANSPORT_BOUNDARY["tool_registration_allowed"])

    def test_error_registry_has_unique_nonzero_codes(self):
        values = list(design.ERROR_REGISTRY.values())
        self.assertEqual(len(values), len(set(values)))
        self.assertTrue(all(value != 0 for value in values))

    def test_validation_sequence_is_exact(self):
        self.assertEqual(
            tuple(design.build_adapter_design()["validation_sequence"]),
            design.VALIDATION_SEQUENCE,
        )
        self.assertEqual(len(design.VALIDATION_SEQUENCE), 11)

    def test_next_routes_are_independent(self):
        routes = design.build_adapter_design()["next_routes"]
        self.assertTrue(routes["route_independence"])
        self.assertEqual(routes["adapter_track"], design.RECOMMENDED_NEXT_PHASE)
        self.assertEqual(routes["long_dataset_track"], design.PHASE_10_43_ROUTE)

    def test_schema_subset_accepts_design(self):
        schema = json.loads(
            (ROOT / "schemas/openclaw_read_only_research_status_local_consumer_adapter_design_v1.schema.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertIsNone(validate_json_schema_subset(design.build_adapter_design(), schema))

    def test_schema_subset_rejects_wrong_mode(self):
        schema = json.loads(
            (ROOT / "schemas/openclaw_read_only_research_status_local_consumer_adapter_design_v1.schema.json").read_text(
                encoding="utf-8"
            )
        )
        value = design.build_adapter_design()
        value["adapter_mode"] = "RUNTIME"
        with self.assertRaises(ValueError):
            validate_json_schema_subset(value, schema)

    def test_preflight_fixture_passes(self):
        root = self._fixture_root()
        result = validate_phase_10_42r_6(
            root=root,
            preflight_only=True,
            write_outputs=False,
            require_source_authority=False,
        )
        self.assertTrue(result["validation_passed"])
        self.assertEqual(result["failed_check_count"], 0)

    def test_full_validation_fixture_passes(self):
        root = self._fixture_root()
        result = validate_phase_10_42r_6(
            root=root,
            preflight_only=False,
            write_outputs=False,
            require_source_authority=False,
        )
        self.assertTrue(result["validation_passed"])
        self.assertEqual(result["negative_control_count"], 10)
        self.assertEqual(result["local_consumer_adapter_implementation_count"], 0)
        self.assertEqual(result["openclaw_runtime_integration_count"], 0)


if __name__ == "__main__":
    unittest.main()
