from __future__ import annotations

import copy
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from src.integration import openclaw_read_only_research_status_contract_v1 as contract
from src.integration import openclaw_read_only_research_status_export_v1 as exporter
from src.validation.phase_10_42r_4_openclaw_read_only_research_status_export_implementation_v1 import (
    PASS_DECISION,
    validate_phase_10_42r_4,
)


class OpenClawReadOnlyResearchStatusExportTests(unittest.TestCase):
    def setUp(self):
        self.root = Path(__file__).resolve().parents[1]

    def build_temp_root(self) -> Path:
        temp = Path(tempfile.mkdtemp())
        for relative in (
            exporter.SOURCE_CONTRACT_MODULE_PATH,
            exporter.SOURCE_SCHEMA_PATH,
            exporter.SOURCE_MANIFEST_PATH,
            Path("docs/PHASE_10_42R_4_OPENCLAW_READ_ONLY_RESEARCH_STATUS_EXPORT_IMPLEMENTATION.md"),
        ):
            source = self.root / relative
            destination = temp / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)
        return temp

    def test_phase_is_exact(self):
        self.assertEqual(exporter.PHASE, "10.42R.4")

    def test_source_commit_is_exact(self):
        self.assertEqual(
            exporter.SOURCE_CONTRACT_COMMIT,
            "26c14a5a1fc63fbdb5bbb61f9bbc7d3dd46656d2",
        )

    def test_source_contract_root_is_exact(self):
        self.assertEqual(
            exporter.SOURCE_CONTRACT_ROOT_SHA256,
            "ba84140879bac8a897505bd55e12d3c117354caf1a5a5ad4f6c3eb003bd6fa46",
        )

    def test_source_hashes_are_exact(self):
        authority = exporter.verify_source_authority(self.root, require_git=False)
        self.assertEqual(
            authority["source_contract_module_sha256"],
            exporter.SOURCE_CONTRACT_MODULE_SHA256,
        )
        self.assertEqual(
            authority["source_schema_sha256"], exporter.SOURCE_SCHEMA_SHA256
        )

    def test_normalized_hash_ignores_crlf(self):
        with tempfile.TemporaryDirectory() as directory:
            first = Path(directory) / "a.txt"
            second = Path(directory) / "b.txt"
            first.write_bytes(b"a\nb\n")
            second.write_bytes(b"a\r\nb\r\n")
            self.assertEqual(
                exporter.normalized_text_sha256(first),
                exporter.normalized_text_sha256(second),
            )

    def test_snapshot_root_is_exact(self):
        snapshot = exporter.build_export_snapshot()
        self.assertEqual(
            snapshot["contract_root_sha256"], exporter.SOURCE_CONTRACT_ROOT_SHA256
        )

    def test_snapshot_validates_source_contract(self):
        contract.validate_status_snapshot(exporter.build_export_snapshot())

    def test_snapshot_validates_schema_subset(self):
        exporter.validate_json_schema_subset(
            exporter.build_export_snapshot(), exporter.load_source_schema(self.root)
        )

    def test_schema_rejects_extra_top_level_field(self):
        snapshot = exporter.build_export_snapshot()
        snapshot["unexpected"] = True
        with self.assertRaises(exporter.StatusExportError):
            exporter.validate_json_schema_subset(
                snapshot, exporter.load_source_schema(self.root)
            )

    def test_schema_rejects_wrong_const(self):
        snapshot = exporter.build_export_snapshot()
        snapshot["contract"]["phase"] = "10.42R.4"
        with self.assertRaises(exporter.StatusExportError):
            exporter.validate_json_schema_subset(
                snapshot, exporter.load_source_schema(self.root)
            )

    def test_snapshot_bytes_are_deterministic(self):
        first, _ = exporter.expected_export_bytes(self.root)
        second, _ = exporter.expected_export_bytes(self.root)
        self.assertEqual(first, second)

    def test_manifest_bytes_are_deterministic(self):
        _, first = exporter.expected_export_bytes(self.root)
        _, second = exporter.expected_export_bytes(self.root)
        self.assertEqual(first, second)

    def test_manifest_binds_snapshot_hash_and_size(self):
        snapshot, manifest_bytes = exporter.expected_export_bytes(self.root)
        manifest = json.loads(manifest_bytes)
        self.assertEqual(manifest["snapshot_sha256"], exporter.sha256_bytes(snapshot))
        self.assertEqual(manifest["snapshot_size_bytes"], len(snapshot))

    def test_atomic_write_creates_exact_bytes(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "x.json"
            result = exporter.atomic_write_bytes(path, b"abc")
            self.assertEqual(path.read_bytes(), b"abc")
            self.assertTrue(result["atomic_replace_performed"])

    def test_atomic_write_is_idempotent(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "x.json"
            exporter.atomic_write_bytes(path, b"abc")
            exporter.atomic_write_bytes(path, b"abc")
            self.assertEqual(path.read_bytes(), b"abc")
            self.assertFalse(any(".tmp-" in item.name for item in path.parent.iterdir()))

    def test_publish_creates_exact_two_file_bundle(self):
        temp = self.build_temp_root()
        try:
            output = temp / "reports/phase_10_42r_4/openclaw_read_only_export_v1"
            result = exporter.publish_status_export(
                temp, output_dir=output, require_git=False
            )
            self.assertEqual(result["export_file_count"], 2)
            self.assertEqual(
                sorted(path.name for path in output.iterdir()),
                sorted([exporter.SNAPSHOT_FILENAME, exporter.MANIFEST_FILENAME]),
            )
        finally:
            shutil.rmtree(temp)

    def test_publish_and_validate_round_trip(self):
        temp = self.build_temp_root()
        try:
            output = temp / "reports/phase_10_42r_4/openclaw_read_only_export_v1"
            exporter.publish_status_export(temp, output_dir=output, require_git=False)
            result = exporter.validate_export_bundle(
                temp, output_dir=output, require_git=False
            )
            self.assertTrue(result["validation_passed"])
        finally:
            shutil.rmtree(temp)

    def test_corrupted_snapshot_is_rejected(self):
        temp = self.build_temp_root()
        try:
            output = temp / "reports/phase_10_42r_4/openclaw_read_only_export_v1"
            exporter.publish_status_export(temp, output_dir=output, require_git=False)
            snapshot_path = output / exporter.SNAPSHOT_FILENAME
            value = json.loads(snapshot_path.read_text(encoding="utf-8"))
            value["master_disposition"]["legacy_short_candidate"] = "APPROVED"
            snapshot_path.write_text(json.dumps(value), encoding="utf-8")
            with self.assertRaises((exporter.StatusExportError, contract.StatusContractError)):
                exporter.validate_export_bundle(temp, output_dir=output, require_git=False)
        finally:
            shutil.rmtree(temp)

    def test_corrupted_manifest_is_rejected(self):
        temp = self.build_temp_root()
        try:
            output = temp / "reports/phase_10_42r_4/openclaw_read_only_export_v1"
            exporter.publish_status_export(temp, output_dir=output, require_git=False)
            manifest_path = output / exporter.MANIFEST_FILENAME
            value = json.loads(manifest_path.read_text(encoding="utf-8"))
            value["snapshot_sha256"] = "0" * 64
            manifest_path.write_text(json.dumps(value), encoding="utf-8")
            with self.assertRaises(exporter.StatusExportError):
                exporter.validate_export_bundle(temp, output_dir=output, require_git=False)
        finally:
            shutil.rmtree(temp)

    def test_unexpected_bundle_file_is_rejected(self):
        temp = self.build_temp_root()
        try:
            output = temp / "reports/phase_10_42r_4/openclaw_read_only_export_v1"
            exporter.publish_status_export(temp, output_dir=output, require_git=False)
            (output / "unexpected.txt").write_text("x", encoding="utf-8")
            with self.assertRaises(exporter.StatusExportError):
                exporter.validate_export_bundle(temp, output_dir=output, require_git=False)
        finally:
            shutil.rmtree(temp)

    def test_source_module_mutation_is_rejected(self):
        temp = self.build_temp_root()
        try:
            path = temp / exporter.SOURCE_CONTRACT_MODULE_PATH
            path.write_text(path.read_text(encoding="utf-8") + "\n# mutation\n", encoding="utf-8")
            with self.assertRaises(exporter.StatusExportError):
                exporter.verify_source_authority(temp, require_git=False)
        finally:
            shutil.rmtree(temp)

    def test_source_schema_mutation_is_rejected(self):
        temp = self.build_temp_root()
        try:
            path = temp / exporter.SOURCE_SCHEMA_PATH
            value = json.loads(path.read_text(encoding="utf-8"))
            value["title"] = "mutated"
            path.write_text(json.dumps(value), encoding="utf-8")
            with self.assertRaises(exporter.StatusExportError):
                exporter.verify_source_authority(temp, require_git=False)
        finally:
            shutil.rmtree(temp)

    def test_runtime_and_tool_permissions_remain_false(self):
        snapshot = exporter.build_export_snapshot()
        prohibited = snapshot["permissions"]["prohibited_capabilities"]
        self.assertFalse(prohibited["openclaw_runtime_status_consumption_allowed"])
        self.assertFalse(prohibited["openclaw_tool_invocation_allowed"])
        self.assertFalse(prohibited["openclaw_operational_integration_allowed"])

    def test_all_prohibited_permissions_are_false(self):
        snapshot = exporter.build_export_snapshot()
        self.assertTrue(
            all(
                value is False
                for value in snapshot["permissions"]["prohibited_capabilities"].values()
            )
        )

    def test_all_read_only_permissions_are_true(self):
        snapshot = exporter.build_export_snapshot()
        self.assertTrue(
            all(
                value is True
                for value in snapshot["permissions"]["read_only_capabilities"].values()
            )
        )

    def test_default_output_is_not_official_evidence_path(self):
        self.assertTrue(exporter.DEFAULT_OUTPUT_DIR.as_posix().startswith("reports/"))
        self.assertNotIn("data/forward", exporter.DEFAULT_OUTPUT_DIR.as_posix())

    def test_recommended_next_phase_is_exact(self):
        self.assertEqual(
            exporter.RECOMMENDED_NEXT_PHASE,
            "PHASE_10_42R_5_OPENCLAW_READ_ONLY_RESEARCH_STATUS_EXPORT_"
            "INTEGRITY_AND_CONSUMER_BOUNDARY_REVIEW_V1",
        )

    def test_export_source_contains_no_market_or_exchange_client(self):
        source = (self.root / "src/integration/openclaw_read_only_research_status_export_v1.py").read_text(encoding="utf-8")
        forbidden = ("from binance", "import ccxt", "requests.get", "websocket")
        self.assertTrue(all(token not in source for token in forbidden))

    def test_preflight_validation_passes_without_git_for_fixture(self):
        summary = validate_phase_10_42r_4(
            root=self.root,
            preflight_only=True,
            write_outputs=False,
            require_git=False,
        )
        self.assertTrue(summary["validation_passed"])
        self.assertEqual(summary["validation_decision"], PASS_DECISION)

    def test_full_validation_passes_without_git_for_fixture(self):
        temp = self.build_temp_root()
        try:
            # The validation module itself is imported from the build tree, while
            # source authority and outputs are scoped to this isolated root.
            summary = validate_phase_10_42r_4(
                root=temp,
                preflight_only=False,
                write_outputs=False,
                require_git=False,
            )
            self.assertTrue(summary["validation_passed"])
            self.assertEqual(summary["export_file_count"], 2)
            self.assertEqual(summary["openclaw_runtime_integration_count"], 0)
        finally:
            shutil.rmtree(temp)


if __name__ == "__main__":
    unittest.main()
