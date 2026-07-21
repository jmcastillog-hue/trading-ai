from __future__ import annotations

import copy
import io
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from src.integration import (
    openclaw_read_only_research_status_local_consumer_adapter_v1 as adapter,
)
from src.validation.phase_10_42r_8_openclaw_read_only_research_status_local_consumer_adapter_implementation_v1 import (
    PASS_DECISION,
    validate_phase_10_42r_8,
)


ROOT = Path(".").resolve()
VALID_REQUEST = {
    "operation": "GET_VALIDATED_RESEARCH_STATUS",
    "response_profile": "HUMAN_EXPLANATION_ONLY",
    "require_human_review": True,
    "allow_actionable_fields": False,
}


class LocalConsumerAdapterImplementationTests(unittest.TestCase):
    def copy_bundle(self, destination_root: Path) -> Path:
        source = ROOT / adapter.SOURCE_BUNDLE_DIRECTORY
        destination = destination_root / adapter.SOURCE_BUNDLE_DIRECTORY
        destination.mkdir(parents=True, exist_ok=True)
        for name in (adapter.SNAPSHOT_FILENAME, adapter.MANIFEST_FILENAME):
            shutil.copyfile(source / name, destination / name)
        return destination

    def expect_failure(self, function, code: int | None = None):
        with self.assertRaises(adapter.AdapterFailure) as context:
            function()
        if code is not None:
            self.assertEqual(context.exception.exit_code, code)

    def test_phase_exact(self):
        self.assertEqual(adapter.PHASE, "10.42R.8")

    def test_implementation_mode_exact(self):
        self.assertEqual(
            adapter.IMPLEMENTATION_MODE,
            "LOCAL_ONE_SHOT_READ_ONLY_STDIO_NO_OPENCLAW_RUNTIME",
        )

    def test_source_review_commit_exact(self):
        self.assertEqual(
            adapter.SOURCE_REVIEW_COMMIT,
            "6df6aa8aef73cd9c5118caf5acf1e723e5438d32",
        )

    def test_design_root_exact(self):
        self.assertEqual(
            adapter.SOURCE_DESIGN_ROOT_SHA256,
            "b7336e60c705841f3ff313016816d9115fb46485d67d3a016d0206ab43d89e21",
        )

    def test_contract_root_exact(self):
        self.assertEqual(
            adapter.SOURCE_CONTRACT_ROOT_SHA256,
            "ba84140879bac8a897505bd55e12d3c117354caf1a5a5ad4f6c3eb003bd6fa46",
        )

    def test_snapshot_hash_exact(self):
        self.assertEqual(
            adapter.SOURCE_SNAPSHOT_SHA256,
            "72a77f3a726d38f0008378218958a5ea8ee8fb0162477692a7370dcf9af43e88",
        )

    def test_manifest_hash_exact(self):
        self.assertEqual(
            adapter.SOURCE_MANIFEST_SHA256,
            "f829010549a79fb3eb35b38ce51736f730020747d6fc77b7fa56eac5ade6a5f7",
        )

    def test_request_field_count(self):
        self.assertEqual(len(adapter.REQUEST_FIELDS), 4)

    def test_response_field_count(self):
        self.assertEqual(len(adapter.RESPONSE_FIELDS), 8)

    def test_error_registry_count(self):
        self.assertEqual(len(adapter.ERROR_REGISTRY), 10)
        self.assertEqual(len(set(adapter.ERROR_REGISTRY.values())), 10)

    def test_prohibited_capability_count(self):
        self.assertEqual(len(adapter.PROHIBITED_CAPABILITY_NAMES), 23)

    def test_valid_request(self):
        adapter.validate_request(VALID_REQUEST)

    def test_request_bytes_parse(self):
        parsed = adapter.parse_request_bytes(
            adapter.canonical_compact_json_bytes(VALID_REQUEST)
        )
        self.assertEqual(parsed, VALID_REQUEST)

    def test_reject_malformed_request(self):
        self.expect_failure(lambda: adapter.parse_request_bytes(b"{"), 20)

    def test_reject_duplicate_request_field(self):
        payload = (
            b'{"operation":"GET_VALIDATED_RESEARCH_STATUS",'
            b'"operation":"GET_VALIDATED_RESEARCH_STATUS",'
            b'"response_profile":"HUMAN_EXPLANATION_ONLY",'
            b'"require_human_review":true,"allow_actionable_fields":false}'
        )
        self.expect_failure(lambda: adapter.parse_request_bytes(payload), 20)

    def test_reject_extra_request_field(self):
        request = dict(VALID_REQUEST)
        request["path"] = ".."
        self.expect_failure(lambda: adapter.validate_request(request), 20)

    def test_reject_unsupported_operation(self):
        request = dict(VALID_REQUEST)
        request["operation"] = "PLACE_ORDER"
        self.expect_failure(lambda: adapter.validate_request(request), 21)

    def test_reject_disabled_human_review(self):
        request = dict(VALID_REQUEST)
        request["require_human_review"] = False
        self.expect_failure(lambda: adapter.validate_request(request), 26)

    def test_reject_actionable_request(self):
        request = dict(VALID_REQUEST)
        request["allow_actionable_fields"] = True
        self.expect_failure(lambda: adapter.validate_request(request), 24)

    def test_reject_oversized_request(self):
        self.expect_failure(
            lambda: adapter.parse_request_bytes(
                b" " * (adapter.MAX_REQUEST_BYTES + 1)
            ),
            20,
        )

    def test_source_freshness(self):
        result = adapter.inspect_source_freshness(ROOT)
        self.assertTrue(result["source_review_commit_exists"])
        self.assertTrue(result["source_review_commit_is_ancestor"])

    def test_export_bundle_validates(self):
        result = adapter.validate_export_bundle(ROOT)
        self.assertEqual(
            result["snapshot_sha256"],
            adapter.SOURCE_SNAPSHOT_SHA256,
        )

    def test_consume_request_passes(self):
        response = adapter.consume_request(VALID_REQUEST, root=ROOT)
        adapter.validate_response(response)

    def test_response_contains_no_actionable_fields(self):
        response = adapter.consume_request(VALID_REQUEST, root=ROOT)
        self.assertFalse(
            adapter._walk_keys(response).intersection(
                adapter.FORBIDDEN_ACTIONABLE_FIELDS
            )
        )

    def test_response_requires_human_review(self):
        response = adapter.consume_request(VALID_REQUEST, root=ROOT)
        self.assertTrue(response["human_review"]["required"])

    def test_response_runtime_permissions_false(self):
        response = adapter.consume_request(VALID_REQUEST, root=ROOT)
        restrictions = response["restrictions"]
        self.assertFalse(
            restrictions["openclaw_runtime_status_consumption_allowed"]
        )
        self.assertFalse(restrictions["openclaw_tool_invocation_allowed"])
        self.assertFalse(restrictions["openclaw_operational_integration_allowed"])

    def test_stdio_success(self):
        stdin = io.BytesIO(adapter.canonical_compact_json_bytes(VALID_REQUEST))
        stdout = io.BytesIO()
        stderr = io.StringIO()
        code = adapter.run_stdio_adapter(
            stdin=stdin,
            stdout=stdout,
            stderr=stderr,
            root=ROOT,
        )
        self.assertEqual(code, 0)
        self.assertEqual(stderr.getvalue(), "")
        response = json.loads(stdout.getvalue().decode("utf-8"))
        adapter.validate_response(response)

    def test_stdio_failure_has_empty_stdout(self):
        stdin = io.BytesIO(b"{")
        stdout = io.BytesIO()
        stderr = io.StringIO()
        code = adapter.run_stdio_adapter(
            stdin=stdin,
            stdout=stdout,
            stderr=stderr,
            root=ROOT,
        )
        self.assertNotEqual(code, 0)
        self.assertEqual(stdout.getvalue(), b"")
        error = json.loads(stderr.getvalue())
        self.assertTrue(error["partial_response_emitted"] is False)

    def test_reject_missing_manifest(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            bundle = self.copy_bundle(root)
            (bundle / adapter.MANIFEST_FILENAME).unlink()
            self.expect_failure(
                lambda: adapter.consume_request(
                    VALID_REQUEST,
                    root=root,
                    require_git=False,
                ),
                23,
            )

    def test_reject_extra_bundle_file(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            bundle = self.copy_bundle(root)
            (bundle / "extra.json").write_text("{}", encoding="utf-8")
            self.expect_failure(
                lambda: adapter.consume_request(
                    VALID_REQUEST,
                    root=root,
                    require_git=False,
                ),
                23,
            )

    def test_reject_snapshot_corruption(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            bundle = self.copy_bundle(root)
            path = bundle / adapter.SNAPSHOT_FILENAME
            path.write_bytes(path.read_bytes() + b"\n")
            self.expect_failure(
                lambda: adapter.consume_request(
                    VALID_REQUEST,
                    root=root,
                    require_git=False,
                ),
                23,
            )

    def test_reject_manifest_corruption(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            bundle = self.copy_bundle(root)
            path = bundle / adapter.MANIFEST_FILENAME
            path.write_bytes(path.read_bytes() + b"\n")
            self.expect_failure(
                lambda: adapter.consume_request(
                    VALID_REQUEST,
                    root=root,
                    require_git=False,
                ),
                23,
            )

    def test_reject_actionable_response(self):
        response = adapter.consume_request(VALID_REQUEST, root=ROOT)
        response["research_status"]["entry_price"] = 1
        self.expect_failure(lambda: adapter.validate_response(response), 25)

    def test_reject_tool_permission_response(self):
        response = adapter.consume_request(VALID_REQUEST, root=ROOT)
        response["restrictions"]["openclaw_tool_invocation_allowed"] = True
        self.expect_failure(lambda: adapter.validate_response(response), 25)

    def test_reject_human_review_response(self):
        response = adapter.consume_request(VALID_REQUEST, root=ROOT)
        response["human_review"]["required"] = False
        self.expect_failure(lambda: adapter.validate_response(response), 26)

    def test_preflight_validation_passes(self):
        result = validate_phase_10_42r_8(
            root=ROOT,
            preflight_only=True,
            write_reports=False,
        )
        self.assertTrue(result["summary"]["validation_passed"])

    def test_full_validation_passes(self):
        result = validate_phase_10_42r_8(
            root=ROOT,
            preflight_only=False,
            write_reports=False,
        )
        self.assertTrue(result["summary"]["validation_passed"])
        self.assertEqual(
            result["summary"]["validation_decision"],
            PASS_DECISION,
        )
        self.assertEqual(result["summary"]["negative_control_count"], 14)


if __name__ == "__main__":
    unittest.main()
