from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from src.long_side import long_forward_observation_phase_10_44_official_dataset_atomic_write_harness_implementation_v1 as harness
from src.validation.phase_10_44_long_official_dataset_atomic_write_harness_implementation_v1 import PASS_DECISION, validate

CANDIDATE_BYTES = (
    b"evidence_id,observation_id,collected_at_utc,observed_at_utc,source_system,"
    b"source_artifact,source_artifact_sha256,source_row_hash,candidate_id,direction,"
    b"symbol,timeframe,observation_state,evidence_status,evidence_scope,evidence_version,"
    b"entry_price,stop_price,target_price,invalidation_level,risk_reward,cost_profile,"
    b"market_context,activation_scope,signal_state,deduplication_key,deduplication_status,"
    b"lifecycle_state,review_status,rejection_reason,manual_confirmation_required,"
    b"manual_confirmed,write_ahead_validation_passed,schema_validation_passed,"
    b"provenance_validation_passed,risk_structure_validation_passed,evidence_hash,"
    b"previous_evidence_hash,audit_event_id,created_by,reviewed_by,rollback_reference,"
    b"accepted_as_real_evidence,official_dataset_write_allowed,evidence_persistence_allowed,"
    b"signal_generation_enabled,live_alerts_allowed,paper_trade_execution_allowed,"
    b"real_capital_allowed,market_execution_allowed,exchange_execution_allowed,"
    b"automation_allowed,execution_allowed,notes\n"
)


class Phase1044Tests(unittest.TestCase):
    def setUp(self) -> None:
        self.repo_temp = tempfile.TemporaryDirectory(prefix="p10_44_repo_")
        self.repo = Path(self.repo_temp.name)
        candidate = self.repo / harness.CANDIDATE_RELATIVE_PATH
        candidate.parent.mkdir(parents=True, exist_ok=True)
        candidate.write_bytes(CANDIDATE_BYTES)

    def tearDown(self) -> None:
        self.repo_temp.cleanup()

    def success(self, sandbox: Path) -> dict:
        return harness.initialize_empty_dataset_in_sandbox(
            repo_root=self.repo,
            sandbox_root=sandbox,
            operation_id_factory=lambda: "1" * 32,
            clock=lambda: "2026-07-22T00:00:00+00:00",
        )

    def expect_code(self, code: str, function) -> harness.HarnessError:
        with self.assertRaises(harness.HarnessError) as context:
            function()
        self.assertEqual(context.exception.code, code)
        return context.exception

    def test_01_candidate_exact(self):
        result = harness.validate_candidate_bytes(CANDIDATE_BYTES)
        self.assertEqual((result["size_bytes"], result["column_count"], result["evidence_row_count"]), (981, 54, 0))

    def test_02_candidate_hash(self):
        self.assertEqual(harness.sha256_bytes(CANDIDATE_BYTES), harness.EXPECTED_CANDIDATE_SHA256)

    def test_03_extra_newline_rejected(self):
        self.expect_code("CANDIDATE_SIZE_MISMATCH", lambda: harness.validate_candidate_bytes(CANDIDATE_BYTES + b"\n"))

    def test_04_bom_rejected(self):
        self.expect_code("CANDIDATE_SIZE_MISMATCH", lambda: harness.validate_candidate_bytes(b"\xef\xbb\xbf" + CANDIDATE_BYTES))

    def test_05_crlf_rejected(self):
        self.expect_code("CANDIDATE_SIZE_MISMATCH", lambda: harness.validate_candidate_bytes(CANDIDATE_BYTES.replace(b"\n", b"\r\n")))

    def test_06_lock_schema(self):
        record = harness.build_lock_record(
            operation_id="a" * 32,
            started_at_utc="2026-07-22T00:00:00+00:00",
            candidate_path=self.repo / harness.CANDIDATE_RELATIVE_PATH,
            target_path=Path(tempfile.gettempdir()) / harness.TARGET_FILENAME,
        )
        self.assertEqual(set(record), set(harness.LOCK_FIELDS))
        self.assertTrue(record["create_only"])
        self.assertFalse(record["official_dataset_path_used"])

    def test_07_success(self):
        with tempfile.TemporaryDirectory(prefix="p10_44_success_") as raw:
            result = self.success(Path(raw))
            self.assertEqual(result["final_state"], "COMMITTED_CLEAN")
            self.assertEqual((result["target_size_bytes"], result["target_column_count"], result["target_evidence_row_count"]), (981, 54, 0))

    def test_08_success_no_residuals(self):
        with tempfile.TemporaryDirectory(prefix="p10_44_success_") as raw:
            sandbox = Path(raw); self.success(sandbox)
            self.assertFalse((sandbox / harness.LOCK_FILENAME).exists())
            self.assertFalse(list(sandbox.glob("*.tmp.*")))

    def test_09_target_exact(self):
        with tempfile.TemporaryDirectory(prefix="p10_44_success_") as raw:
            sandbox = Path(raw); self.success(sandbox)
            self.assertEqual((sandbox / harness.TARGET_FILENAME).read_bytes(), CANDIDATE_BYTES)

    def test_10_manifest_valid(self):
        with tempfile.TemporaryDirectory(prefix="p10_44_success_") as raw:
            sandbox = Path(raw); result = self.success(sandbox)
            pair = harness.validate_committed_pair(sandbox / harness.TARGET_FILENAME, sandbox / harness.MANIFEST_FILENAME)
            self.assertEqual(pair["target_sha256"], result["target_sha256"])

    def test_11_existing_target_rejected(self):
        with tempfile.TemporaryDirectory(prefix="p10_44_existing_") as raw:
            sandbox = Path(raw); (sandbox / harness.TARGET_FILENAME).write_text("existing", encoding="utf-8")
            self.expect_code("SANDBOX_NOT_CLEAN", lambda: self.success(sandbox))

    def test_12_second_run_rejected(self):
        with tempfile.TemporaryDirectory(prefix="p10_44_second_") as raw:
            sandbox = Path(raw); self.success(sandbox)
            self.expect_code("SANDBOX_NOT_CLEAN", lambda: self.success(sandbox))

    def test_13_existing_lock_rejected(self):
        with tempfile.TemporaryDirectory(prefix="p10_44_lock_") as raw:
            sandbox = Path(raw); (sandbox / harness.LOCK_FILENAME).write_text("{}", encoding="utf-8")
            self.expect_code("SANDBOX_NOT_CLEAN", lambda: self.success(sandbox))

    def test_14_repository_sandbox_rejected(self):
        sandbox = self.repo / "sandbox"; sandbox.mkdir()
        try:
            self.expect_code("OFFICIAL_OR_REPOSITORY_PATH_PROHIBITED", lambda: self.success(sandbox))
        finally:
            sandbox.rmdir()

    def test_15_fail_after_lock_cleans(self):
        with tempfile.TemporaryDirectory(prefix="p10_44_fail_") as raw:
            sandbox = Path(raw)
            self.expect_code("INJECTED_FAILURE", lambda: harness.initialize_empty_dataset_in_sandbox(repo_root=self.repo, sandbox_root=sandbox, fail_at="AFTER_LOCK_ACQUIRED", operation_id_factory=lambda: "2" * 32))
            self.assertEqual(harness.inspect_recovery_state(sandbox)["state"], "CLEAN_EMPTY")

    def test_16_fail_after_temp_cleans(self):
        with tempfile.TemporaryDirectory(prefix="p10_44_fail_") as raw:
            sandbox = Path(raw)
            self.expect_code("INJECTED_FAILURE", lambda: harness.initialize_empty_dataset_in_sandbox(repo_root=self.repo, sandbox_root=sandbox, fail_at="AFTER_TARGET_TEMP_DURABLE", operation_id_factory=lambda: "3" * 32))
            self.assertEqual(harness.inspect_recovery_state(sandbox)["state"], "CLEAN_EMPTY")

    def test_17_fail_after_target_requires_review(self):
        with tempfile.TemporaryDirectory(prefix="p10_44_fail_") as raw:
            sandbox = Path(raw)
            self.expect_code("INJECTED_FAILURE", lambda: harness.initialize_empty_dataset_in_sandbox(repo_root=self.repo, sandbox_root=sandbox, fail_at="AFTER_TARGET_PUBLISHED", operation_id_factory=lambda: "4" * 32))
            state = harness.inspect_recovery_state(sandbox)
            self.assertEqual(state["state"], "TARGET_WITHOUT_MANIFEST_RECOVERY_REQUIRED")
            self.assertFalse(state["automatic_recovery_performed"])

    def test_18_fail_after_manifest_temp_keeps_temp(self):
        with tempfile.TemporaryDirectory(prefix="p10_44_fail_") as raw:
            sandbox = Path(raw)
            self.expect_code("INJECTED_FAILURE", lambda: harness.initialize_empty_dataset_in_sandbox(repo_root=self.repo, sandbox_root=sandbox, fail_at="AFTER_MANIFEST_TEMP_DURABLE", operation_id_factory=lambda: "5" * 32))
            state = harness.inspect_recovery_state(sandbox)
            self.assertEqual(state["state"], "TARGET_WITHOUT_MANIFEST_RECOVERY_REQUIRED")
            self.assertEqual(state["manifest_temp_count"], 1)

    def test_19_fail_after_manifest_publish_keeps_lock(self):
        with tempfile.TemporaryDirectory(prefix="p10_44_fail_") as raw:
            sandbox = Path(raw)
            self.expect_code("INJECTED_FAILURE", lambda: harness.initialize_empty_dataset_in_sandbox(repo_root=self.repo, sandbox_root=sandbox, fail_at="AFTER_MANIFEST_PUBLISHED", operation_id_factory=lambda: "6" * 32))
            self.assertEqual(harness.inspect_recovery_state(sandbox)["state"], "TARGET_AND_MANIFEST_WITH_LOCK_RECOVERY_REQUIRED")

    def test_20_wrong_owner_cannot_release(self):
        with tempfile.TemporaryDirectory(prefix="p10_44_owner_") as raw:
            sandbox = Path(raw); lock = sandbox / harness.LOCK_FILENAME
            record = harness.build_lock_record(operation_id="a" * 32, started_at_utc="2026-07-22T00:00:00+00:00", candidate_path=self.repo / harness.CANDIDATE_RELATIVE_PATH, target_path=sandbox / harness.TARGET_FILENAME)
            harness.acquire_lock(lock, record)
            self.expect_code("LOCK_OWNERSHIP_MISMATCH", lambda: harness.release_owned_lock(lock, "b" * 32))
            self.assertTrue(lock.exists())

    def test_21_manifest_tamper_rejected(self):
        with tempfile.TemporaryDirectory(prefix="p10_44_tamper_") as raw:
            sandbox = Path(raw); self.success(sandbox)
            manifest = sandbox / harness.MANIFEST_FILENAME
            manifest.write_text(manifest.read_text(encoding="utf-8").replace(harness.EXPECTED_CANDIDATE_SHA256, "0" * 64), encoding="utf-8", newline="\n")
            self.expect_code("MANIFEST_BINDING_MISMATCH", lambda: harness.validate_committed_pair(sandbox / harness.TARGET_FILENAME, manifest))

    def test_22_manifest_permissions_false(self):
        with tempfile.TemporaryDirectory(prefix="p10_44_manifest_") as raw:
            sandbox = Path(raw); self.success(sandbox)
            row = harness.read_manifest(sandbox / harness.MANIFEST_FILENAME)
            for field in ("existing_target_replacement_allowed", "official_dataset_path_used", "automatic_recovery_allowed", "signal_generation_enabled", "live_alerts_allowed", "paper_trade_execution_allowed", "real_capital_allowed", "market_execution_allowed", "exchange_execution_allowed", "automation_allowed", "execution_allowed"):
                self.assertEqual(row[field].lower(), "false")

    def test_23_inspector_read_only(self):
        with tempfile.TemporaryDirectory(prefix="p10_44_inspect_") as raw:
            sandbox = Path(raw); lock = sandbox / harness.LOCK_FILENAME; lock.write_text("{}", encoding="utf-8")
            before = lock.read_bytes(); state = harness.inspect_recovery_state(sandbox); after = lock.read_bytes()
            self.assertEqual(state["state"], "LOCK_ONLY_RECOVERY_REQUIRED")
            self.assertEqual(before, after)

    def test_24_full_validation_offline(self):
        result = validate(root=self.repo, verify_git=False, write_reports=False)
        self.assertTrue(result["summary"]["validation_passed"])
        self.assertEqual(result["summary"]["validation_decision"], PASS_DECISION)
        self.assertEqual(result["summary"]["negative_control_count"], 12)
        self.assertEqual(result["summary"]["official_dataset_write_count"], 0)


if __name__ == "__main__":
    unittest.main()
