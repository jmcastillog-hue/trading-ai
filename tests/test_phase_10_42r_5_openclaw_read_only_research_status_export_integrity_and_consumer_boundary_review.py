from __future__ import annotations

import copy
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from src.integration import openclaw_read_only_research_status_consumer_boundary_v1 as review
from src.validation.phase_10_42r_5_openclaw_read_only_research_status_export_integrity_and_consumer_boundary_review_v1 import (
    PASS_DECISION,
    validate_phase_10_42r_5,
)


class ConsumerBoundaryReviewTests(unittest.TestCase):
    def make_fixture(self) -> tuple[tempfile.TemporaryDirectory[str], Path]:
        temporary = tempfile.TemporaryDirectory()
        root = Path(temporary.name)
        bundle = root / review.SOURCE_BUNDLE_DIR
        bundle.mkdir(parents=True)
        snapshot, manifest = review.expected_export_bytes()
        (bundle / review.SNAPSHOT_FILENAME).write_bytes(snapshot)
        (bundle / review.MANIFEST_FILENAME).write_bytes(manifest)
        (root / review.SOURCE_EXPORT_MODULE_PATH).parent.mkdir(parents=True)
        (root / review.SOURCE_EXPORT_MODULE_PATH).write_text("fixture\n", encoding="utf-8")
        (root / review.SOURCE_EXPORT_DOCUMENT_PATH).parent.mkdir(parents=True, exist_ok=True)
        (root / review.SOURCE_EXPORT_DOCUMENT_PATH).write_text("fixture\n", encoding="utf-8")
        return temporary, root

    def test_expected_snapshot_root_exact(self):
        self.assertEqual(
            review.expected_snapshot()["contract_root_sha256"],
            review.SOURCE_CONTRACT_ROOT_SHA256,
        )

    def test_expected_snapshot_hash_exact(self):
        snapshot, _ = review.expected_export_bytes()
        self.assertEqual(review.sha256_bytes(snapshot), review.SOURCE_SNAPSHOT_SHA256)
        self.assertEqual(len(snapshot), review.SOURCE_SNAPSHOT_SIZE_BYTES)

    def test_expected_manifest_hash_exact(self):
        _, manifest = review.expected_export_bytes()
        self.assertEqual(review.sha256_bytes(manifest), review.SOURCE_MANIFEST_SHA256)

    def test_read_only_capability_count_is_six(self):
        self.assertEqual(len(review.READ_ONLY_CAPABILITIES), 6)
        self.assertTrue(all(review.READ_ONLY_CAPABILITIES.values()))

    def test_prohibited_capability_count_is_twenty_three(self):
        self.assertEqual(len(review.PROHIBITED_CAPABILITIES), 23)
        self.assertTrue(all(value is False for value in review.PROHIBITED_CAPABILITIES.values()))

    def test_runtime_permissions_are_false(self):
        for field in (
            "openclaw_runtime_status_consumption_allowed",
            "openclaw_tool_invocation_allowed",
            "openclaw_operational_integration_allowed",
        ):
            self.assertIs(review.PROHIBITED_CAPABILITIES[field], False)

    def test_next_phase_is_exact(self):
        self.assertEqual(
            review.NEXT_PHASE,
            "PHASE_10_42R_6_OPENCLAW_READ_ONLY_RESEARCH_STATUS_LOCAL_CONSUMER_ADAPTER_DESIGN_V1",
        )

    def test_strict_json_rejects_duplicate_key(self):
        with self.assertRaises(review.ConsumerBoundaryError):
            review.load_json_strict(b'{"a":1,"a":2}', label="fixture")

    def test_strict_json_rejects_nonfinite(self):
        with self.assertRaises(review.ConsumerBoundaryError):
            review.load_json_strict(b'{"a":NaN}', label="fixture")

    def test_snapshot_semantics_are_frozen(self):
        snapshot = review.expected_snapshot()
        self.assertEqual(
            snapshot["master_disposition"]["short_recovery_line"],
            "CLOSED_ALL_VARIANTS_REJECTED",
        )
        self.assertEqual(
            snapshot["evidence_summary"]["short_recovery_surviving_variant_count"],
            0,
        )

    def test_lockboxes_are_sealed(self):
        disposition = review.expected_snapshot()["master_disposition"]
        self.assertEqual(disposition["retrospective_lockbox"], "SEALED")
        self.assertEqual(disposition["prospective_holdout"], "SEALED")

    def test_long_evidence_rows_are_zero(self):
        self.assertEqual(
            review.expected_snapshot()["evidence_summary"]["long_official_evidence_row_count"],
            0,
        )

    def test_manifest_binds_snapshot(self):
        snapshot, manifest_bytes = review.expected_export_bytes()
        manifest = json.loads(manifest_bytes)
        self.assertEqual(manifest["snapshot_sha256"], review.sha256_bytes(snapshot))
        self.assertEqual(manifest["snapshot_size_bytes"], len(snapshot))

    def test_manifest_operational_flags_are_false(self):
        _, manifest_bytes = review.expected_export_bytes()
        manifest = json.loads(manifest_bytes)
        for field in (
            "openclaw_runtime_status_consumption_allowed",
            "openclaw_tool_invocation_allowed",
            "openclaw_operational_integration_allowed",
            "official_dataset_write_allowed",
            "signal_generation_enabled",
            "paper_trade_execution_allowed",
            "real_capital_allowed",
            "market_execution_allowed",
            "automation_allowed",
        ):
            self.assertIs(manifest[field], False)

    def test_review_accepts_fixture_without_git_or_source_check(self):
        temporary, root = self.make_fixture()
        try:
            original = review.verify_source_authority
            review.verify_source_authority = lambda *_args, **_kwargs: {
                "git_metadata_available": False,
                "freshness_check_skipped": True,
            }
            try:
                result = review.review_export_bundle(root, require_git=False)
            finally:
                review.verify_source_authority = original
            self.assertTrue(result["validation_passed"])
        finally:
            temporary.cleanup()

    def test_consumer_accepts_fixture_without_git_or_source_check(self):
        temporary, root = self.make_fixture()
        try:
            original = review.verify_source_authority
            review.verify_source_authority = lambda *_args, **_kwargs: {}
            try:
                value = review.simulate_read_only_consumer(root, require_git=False)
            finally:
                review.verify_source_authority = original
            self.assertEqual(
                value["consumer_decision"],
                "READ_ONLY_STATUS_ACCEPTED_FOR_HUMAN_EXPLANATION_SIMULATION",
            )
            self.assertIs(value["openclaw_tool_invocation_allowed"], False)
        finally:
            temporary.cleanup()

    def assert_mutation_rejected(self, mutate):
        temporary, root = self.make_fixture()
        try:
            bundle = root / review.SOURCE_BUNDLE_DIR
            mutate(bundle)
            original = review.verify_source_authority
            review.verify_source_authority = lambda *_args, **_kwargs: {}
            try:
                with self.assertRaises(review.ConsumerBoundaryError):
                    review.review_export_bundle(root, require_git=False)
            finally:
                review.verify_source_authority = original
        finally:
            temporary.cleanup()

    def test_missing_manifest_rejected(self):
        self.assert_mutation_rejected(
            lambda bundle: (bundle / review.MANIFEST_FILENAME).unlink()
        )

    def test_extra_file_rejected(self):
        self.assert_mutation_rejected(
            lambda bundle: (bundle / "extra.txt").write_text("x", encoding="utf-8")
        )

    def test_snapshot_corruption_rejected(self):
        self.assert_mutation_rejected(
            lambda bundle: (bundle / review.SNAPSHOT_FILENAME).write_bytes(b"{}\n")
        )

    def test_manifest_corruption_rejected(self):
        self.assert_mutation_rejected(
            lambda bundle: (bundle / review.MANIFEST_FILENAME).write_bytes(b"{}\n")
        )

    def test_runtime_permission_enabled_rejected(self):
        def mutate(bundle: Path):
            path = bundle / review.SNAPSHOT_FILENAME
            value = json.loads(path.read_text(encoding="utf-8"))
            value["permissions"]["prohibited_capabilities"][
                "openclaw_runtime_status_consumption_allowed"
            ] = True
            path.write_bytes(review.canonical_pretty_json_bytes(value))
        self.assert_mutation_rejected(mutate)

    def test_manifest_source_commit_change_rejected(self):
        def mutate(bundle: Path):
            path = bundle / review.MANIFEST_FILENAME
            value = json.loads(path.read_text(encoding="utf-8"))
            value["source_contract_commit"] = "0" * 40
            path.write_bytes(review.canonical_pretty_json_bytes(value))
        self.assert_mutation_rejected(mutate)

    def test_temporary_file_rejected(self):
        self.assert_mutation_rejected(
            lambda bundle: (bundle / ".x.tmp-interrupted").write_text("x", encoding="utf-8")
        )

    def test_consumer_output_contains_no_actionable_prices(self):
        temporary, root = self.make_fixture()
        try:
            original = review.verify_source_authority
            review.verify_source_authority = lambda *_args, **_kwargs: {}
            try:
                value = review.simulate_read_only_consumer(root, require_git=False)
            finally:
                review.verify_source_authority = original
            forbidden = {"entry_price", "stop_price", "target_price", "position_size"}
            self.assertTrue(forbidden.isdisjoint(value))
        finally:
            temporary.cleanup()

    def test_consumer_output_requires_human_review(self):
        temporary, root = self.make_fixture()
        try:
            original = review.verify_source_authority
            review.verify_source_authority = lambda *_args, **_kwargs: {}
            try:
                value = review.simulate_read_only_consumer(root, require_git=False)
            finally:
                review.verify_source_authority = original
            self.assertIs(value["human_decision_required"], True)
            self.assertEqual(value["runtime_integration_status"], "NOT_IMPLEMENTED")
        finally:
            temporary.cleanup()

    def test_preflight_and_full_validation_decision_constants(self):
        self.assertEqual(
            PASS_DECISION,
            "PHASE_10_42R_5_OPENCLAW_READ_ONLY_RESEARCH_STATUS_EXPORT_INTEGRITY_AND_CONSUMER_BOUNDARY_REVIEW_VALIDATED",
        )

    def test_review_module_contains_no_openclaw_client_import(self):
        source = Path(review.__file__).read_text(encoding="utf-8").lower()
        for token in ("openclaw sdk", "lmstudio", "binance.client", "ccxt", "requests."):
            self.assertNotIn(token, source)

    def test_review_module_contains_no_network_or_process_service(self):
        source = Path(review.__file__).read_text(encoding="utf-8").lower()
        for token in ("socket.", "http.server", "flask", "fastapi", "uvicorn"):
            self.assertNotIn(token, source)

    def test_source_export_commit_is_exact(self):
        self.assertEqual(
            review.SOURCE_EXPORT_COMMIT,
            "a371b3682f2e1f99a8b75c3124ee855b05cd5319",
        )

    def test_phase_is_exact(self):
        self.assertEqual(review.PHASE, "10.42R.5")


if __name__ == "__main__":
    unittest.main()
