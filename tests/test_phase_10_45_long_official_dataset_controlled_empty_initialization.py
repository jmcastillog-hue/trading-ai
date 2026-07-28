from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from src.long_side import long_forward_observation_phase_10_44_official_dataset_atomic_write_harness_implementation_v1 as atomic
from src.long_side import long_forward_observation_phase_10_45_official_dataset_controlled_empty_initialization_v1 as phase

CANDIDATE_BYTES = (Path(__file__).resolve().parents[1] / atomic.CANDIDATE_RELATIVE_PATH).read_bytes()


class Phase1045Tests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="phase_10_45_repo_")
        self.repo = Path(self.temp.name)
        candidate = self.repo / atomic.CANDIDATE_RELATIVE_PATH
        candidate.parent.mkdir(parents=True)
        candidate.write_bytes(CANDIDATE_BYTES)
        (self.repo / "data/forward").mkdir(parents=True, exist_ok=True)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def error(self, code: str, function) -> atomic.HarnessError:
        with self.assertRaises(atomic.HarnessError) as caught:
            function()
        self.assertEqual(caught.exception.code, code)
        return caught.exception

    def run_official(self, **kwargs):
        return phase.initialize_official_empty_dataset(repo_root=self.repo, gate_b_authorization=phase.GATE_B_AUTHORIZATION, operation_id_factory=lambda: "1" * 32, clock=lambda: "2026-07-26T00:00:00+00:00", **kwargs)

    def test_01_candidate_correct(self):
        result = phase.preflight_official(self.repo)
        self.assertEqual((result["candidate_sha256"], result["candidate_size_bytes"], result["candidate_column_count"], result["candidate_evidence_row_count"]), (phase.EXPECTED_SHA256, 981, 54, 0))

    def test_02_gate_b_absent(self):
        self.error("GATE_B_AUTHORIZATION_REQUIRED", lambda: phase.initialize_official_empty_dataset(repo_root=self.repo))

    def test_03_gate_b_wrong(self):
        self.error("GATE_B_AUTHORIZATION_REQUIRED", lambda: phase.initialize_official_empty_dataset(repo_root=self.repo, gate_b_authorization="wrong"))

    def test_04_target_preexisting(self):
        (self.repo / "data/forward" / phase.TARGET_FILENAME).write_text("existing")
        self.error("OFFICIAL_PREFLIGHT_FAILED", self.run_official)

    def test_05_manifest_preexisting(self):
        (self.repo / "data/forward" / phase.MANIFEST_FILENAME).write_text("existing")
        self.error("OFFICIAL_PREFLIGHT_FAILED", self.run_official)

    def test_06_lock_preexisting(self):
        (self.repo / "data/forward" / phase.LOCK_FILENAME).write_text("{}")
        self.error("OFFICIAL_PREFLIGHT_FAILED", self.run_official)

    def test_07_temp_residual(self):
        (self.repo / "data/forward" / f"{phase.TARGET_FILENAME}.tmp.residual").write_text("x")
        self.error("OFFICIAL_PREFLIGHT_FAILED", self.run_official)

    def test_08_backup_residual(self):
        (self.repo / "data/forward" / f"{phase.TARGET_FILENAME}.backup").write_text("x")
        self.error("OFFICIAL_PREFLIGHT_FAILED", self.run_official)

    def test_09_hash_wrong(self):
        candidate = self.repo / atomic.CANDIDATE_RELATIVE_PATH
        candidate.write_bytes(b"x" * 981)
        self.error("CANDIDATE_HASH_MISMATCH", lambda: phase.preflight_official(self.repo))

    def test_10_size_wrong(self):
        candidate = self.repo / atomic.CANDIDATE_RELATIVE_PATH
        candidate.write_bytes(CANDIDATE_BYTES + b"x")
        self.error("CANDIDATE_SIZE_MISMATCH", lambda: phase.preflight_official(self.repo))

    def test_11_columns_wrong(self):
        candidate = self.repo / atomic.CANDIDATE_RELATIVE_PATH
        payload = CANDIDATE_BYTES.replace(b",notes\n", b"\n")
        payload = payload + b" " * (981 - len(payload))
        candidate.write_bytes(payload)
        self.error("CANDIDATE_HASH_MISMATCH", lambda: phase.preflight_official(self.repo))

    def test_12_unexpected_row(self):
        candidate = self.repo / atomic.CANDIDATE_RELATIVE_PATH
        candidate.write_bytes(CANDIDATE_BYTES + b"," * 53 + b"\n")
        self.error("CANDIDATE_SIZE_MISMATCH", lambda: phase.preflight_official(self.repo))

    def test_13_success_create_only(self):
        result = self.run_official()
        self.assertEqual(result["final_state"], "COMMITTED_CLEAN")
        self.assertTrue(result["create_only"])
        self.assertFalse(result["replacement_allowed"])

    def test_14_second_execution_forbidden(self):
        self.run_official()
        self.error("OFFICIAL_PREFLIGHT_FAILED", self.run_official)

    def test_15_concurrent_publication(self):
        original = atomic.publish_create_only
        def competing(temp: Path, target: Path):
            target.write_text("competitor")
            return original(temp, target)
        atomic.publish_create_only = competing
        try:
            self.error("EXISTING_TARGET_BLOCKED", self.run_official)
            target = phase.official_paths(self.repo)["target"]
            self.assertEqual(target.read_text(), "competitor")
        finally:
            atomic.publish_create_only = original

    def test_16_failure_after_lock_cleans(self):
        self.error("INJECTED_FAILURE", lambda: self.run_official(fail_at="AFTER_LOCK_ACQUIRED"))
        self.assertEqual(phase.preflight_official(self.repo)["state"], "CLEAN_EMPTY")

    def test_17_failure_after_temp_cleans(self):
        self.error("INJECTED_FAILURE", lambda: self.run_official(fail_at="AFTER_TARGET_TEMP_DURABLE"))
        self.assertEqual(phase.preflight_official(self.repo)["state"], "CLEAN_EMPTY")

    def test_18_failure_after_target_preserves(self):
        self.error("INJECTED_FAILURE", lambda: self.run_official(fail_at="AFTER_TARGET_PUBLISHED"))
        paths = phase.official_paths(self.repo)
        self.assertTrue(paths["target"].exists())
        self.assertTrue(paths["lock"].exists())
        self.assertFalse(paths["manifest"].exists())

    def test_19_failure_after_manifest_temp_preserves(self):
        self.error("INJECTED_FAILURE", lambda: self.run_official(fail_at="AFTER_MANIFEST_TEMP_DURABLE"))
        directory = phase.official_paths(self.repo)["directory"]
        self.assertTrue(list(directory.glob(f"{phase.MANIFEST_FILENAME}.tmp.*")))

    def test_20_failure_after_manifest_publish_preserves_lock(self):
        self.error("INJECTED_FAILURE", lambda: self.run_official(fail_at="AFTER_MANIFEST_PUBLISHED"))
        paths = phase.official_paths(self.repo)
        self.assertTrue(paths["target"].exists() and paths["manifest"].exists() and paths["lock"].exists())

    def test_21_wrong_lock_owner(self):
        path = phase.official_paths(self.repo)["lock"]
        record = atomic.build_lock_record(operation_id="a" * 32, started_at_utc="2026-07-26T00:00:00+00:00", candidate_path=self.repo / atomic.CANDIDATE_RELATIVE_PATH, target_path=phase.official_paths(self.repo)["target"])
        atomic.acquire_lock(path, record)
        self.error("LOCK_OWNERSHIP_MISMATCH", lambda: atomic.release_owned_lock(path, "b" * 32))

    def test_22_manifest_tamper(self):
        self.run_official()
        paths = phase.official_paths(self.repo)
        text = paths["manifest"].read_text(encoding="utf-8")
        paths["manifest"].write_text(text.replace(phase.EXPECTED_SHA256, "0" * 64), encoding="utf-8", newline="\n")
        self.error("MANIFEST_BINDING_MISMATCH", lambda: phase.verify_committed_pair(paths["target"], paths["manifest"]))

    def test_23_official_path_forbidden_in_isolation(self):
        self.error("OFFICIAL_PATH_PROHIBITED_IN_ISOLATION", lambda: phase.initialize_in_isolated_directory(repo_root=self.repo, isolated_directory=self.repo / "data/forward", gate_b_authorization=phase.GATE_B_AUTHORIZATION))

    def test_24_trading_permissions_false(self):
        result = self.run_official()
        for name in ("signal_generation_enabled", "live_alerts_allowed", "paper_trade_execution_allowed", "real_capital_allowed", "market_execution_allowed", "exchange_execution_allowed", "automation_allowed", "execution_allowed"):
            self.assertFalse(result[name])
        self.assertEqual(result["official_evidence_rows_written"], 0)

    def test_25_isolated_success_uses_no_official_path(self):
        with tempfile.TemporaryDirectory(prefix="phase_10_45_isolated_") as raw:
            result = phase.initialize_in_isolated_directory(repo_root=self.repo, isolated_directory=raw, gate_b_authorization=phase.GATE_B_AUTHORIZATION, operation_id_factory=lambda: "2" * 32)
            self.assertEqual(result["final_state"], "COMMITTED_CLEAN")
            self.assertFalse(result["official_dataset_path_used"])
            for name in ("signal_generation_enabled", "live_alerts_allowed", "paper_trade_execution_allowed", "real_capital_allowed", "market_execution_allowed", "exchange_execution_allowed", "automation_allowed", "execution_allowed"):
                self.assertFalse(result[name])


if __name__ == "__main__":
    unittest.main()
