from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path

from src.long_side import synchronized_15m_observation_v1_1 as sync_v11
from src.long_side.synchronized_15m_observation_v1_1_microstructure_auth_propagation_v1 import (
    CAPABILITY,
    IMPLEMENTATION_OR_REPAIR_ATTEMPT,
    LEGACY_DELEGATED_MICROSTRUCTURE_AUTHORIZATION,
    LEGACY_USER_SESSION_AUTHORIZATION,
    MAX_IMPLEMENTATION_OR_REPAIR_ATTEMPTS,
    MICROSTRUCTURE_V1_1_AUTHORIZATION,
    SESSION_AUTHORIZATION,
    AuthorizationPropagationError,
    make_microstructure_authorization_bridge,
    run_bounded_synchronized_15m_session_with_microstructure_auth_propagation_v1,
    validate_authorization_propagation_session_v1,
)


class Tests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        self.repo = root / "repo"
        self.repo.mkdir()
        (self.repo / ".git").mkdir()
        self.external = root / "external"
        self.external.mkdir()
        os.environ.pop(
            "TRADING_AI_OFFICIAL_LONG_EVIDENCE_APPEND_ALLOWED",
            None,
        )

    def tearDown(self):
        os.environ.pop(
            "TRADING_AI_OFFICIAL_LONG_EVIDENCE_APPEND_ALLOWED",
            None,
        )
        self.tmp.cleanup()

    def test_01_capability(self):
        self.assertEqual(
            CAPABILITY,
            "SYNCHRONIZED_15M_OBSERVATION_V1_1_"
            "MICROSTRUCTURE_AUTHORIZATION_PROPAGATION_V1",
        )

    def test_02_attempt_is_new_line_1_of_10(self):
        self.assertEqual(IMPLEMENTATION_OR_REPAIR_ATTEMPT, 1)
        self.assertEqual(MAX_IMPLEMENTATION_OR_REPAIR_ATTEMPTS, 10)

    def test_03_outer_authorization_is_new(self):
        self.assertNotEqual(
            SESSION_AUTHORIZATION,
            LEGACY_USER_SESSION_AUTHORIZATION,
        )

    def test_04_microstructure_authorization_is_v1_1(self):
        self.assertEqual(
            MICROSTRUCTURE_V1_1_AUTHORIZATION,
            "CAPTURE_ONE_SHOT_BINANCE_USDM_PUBLIC_MICROSTRUCTURE_V1_1",
        )

    def test_05_closed_sync_still_delegates_legacy_micro_token(self):
        self.assertEqual(
            sync_v11.MICROSTRUCTURE_AUTHORIZATION,
            LEGACY_DELEGATED_MICROSTRUCTURE_AUTHORIZATION,
        )

    def test_06_bridge_rejects_unexpected_incoming_token(self):
        calls = []

        def target(**kwargs):
            calls.append(kwargs)
            return {
                "capability": "PUBLIC_READ_ONLY_MICROSTRUCTURE_SNAPSHOT_V1_1",
                "request_count": 7,
            }

        bridge = make_microstructure_authorization_bridge(target)
        with self.assertRaises(AuthorizationPropagationError):
            bridge(
                repo_root=self.repo,
                output_directory=self.external / "x",
                authorization=MICROSTRUCTURE_V1_1_AUTHORIZATION,
            )
        self.assertEqual(calls, [])

    def test_07_bridge_substitutes_repaired_v1_1_token(self):
        seen = []

        def target(**kwargs):
            seen.append(kwargs["authorization"])
            return {
                "capability": "PUBLIC_READ_ONLY_MICROSTRUCTURE_SNAPSHOT_V1_1",
                "request_count": 7,
            }

        audit = []
        bridge = make_microstructure_authorization_bridge(target, audit)
        result = bridge(
            repo_root=self.repo,
            output_directory=self.external / "x",
            authorization=LEGACY_DELEGATED_MICROSTRUCTURE_AUTHORIZATION,
        )
        self.assertEqual(
            seen,
            [MICROSTRUCTURE_V1_1_AUTHORIZATION],
        )
        self.assertEqual(result["request_count"], 7)
        self.assertEqual(len(audit), 1)
        self.assertTrue(
            audit[0]["closed_sync_delegated_authorization_intercepted"]
        )

    def test_08_bridge_rejects_wrong_capability(self):
        def target(**kwargs):
            return {"capability": "WRONG", "request_count": 7}

        bridge = make_microstructure_authorization_bridge(target)
        with self.assertRaises(AuthorizationPropagationError):
            bridge(
                repo_root=self.repo,
                output_directory=self.external / "x",
                authorization=LEGACY_DELEGATED_MICROSTRUCTURE_AUTHORIZATION,
            )

    def test_09_bridge_rejects_wrong_request_count(self):
        def target(**kwargs):
            return {
                "capability": "PUBLIC_READ_ONLY_MICROSTRUCTURE_SNAPSHOT_V1_1",
                "request_count": 6,
            }

        bridge = make_microstructure_authorization_bridge(target)
        with self.assertRaises(AuthorizationPropagationError):
            bridge(
                repo_root=self.repo,
                output_directory=self.external / "x",
                authorization=LEGACY_DELEGATED_MICROSTRUCTURE_AUTHORIZATION,
            )

    def test_10_old_outer_session_authorization_rejected_before_output(self):
        out = self.external / "old"
        with self.assertRaises(AuthorizationPropagationError):
            run_bounded_synchronized_15m_session_with_microstructure_auth_propagation_v1(
                repo_root=self.repo,
                output_directory=out,
                max_cycles=1,
                source_attestation="x",
                minimum_latest_closed_candle_utc=None,
                authorization=LEGACY_USER_SESSION_AUTHORIZATION,
            )
        self.assertFalse(out.exists())

    def test_11_missing_outer_authorization_rejected(self):
        out = self.external / "missing"
        with self.assertRaises(AuthorizationPropagationError):
            run_bounded_synchronized_15m_session_with_microstructure_auth_propagation_v1(
                repo_root=self.repo,
                output_directory=out,
                max_cycles=1,
                source_attestation="x",
                minimum_latest_closed_candle_utc=None,
                authorization=None,
            )
        self.assertFalse(out.exists())

    def test_12_gate_enabled_rejected(self):
        os.environ[
            "TRADING_AI_OFFICIAL_LONG_EVIDENCE_APPEND_ALLOWED"
        ] = "1"
        out = self.external / "gate"
        with self.assertRaises(AuthorizationPropagationError):
            run_bounded_synchronized_15m_session_with_microstructure_auth_propagation_v1(
                repo_root=self.repo,
                output_directory=out,
                max_cycles=1,
                source_attestation="x",
                minimum_latest_closed_candle_utc=None,
                authorization=SESSION_AUTHORIZATION,
            )
        self.assertFalse(out.exists())

    def test_13_output_inside_repo_rejected(self):
        with self.assertRaises(AuthorizationPropagationError):
            run_bounded_synchronized_15m_session_with_microstructure_auth_propagation_v1(
                repo_root=self.repo,
                output_directory=self.repo / "x",
                max_cycles=1,
                source_attestation="x",
                minimum_latest_closed_candle_utc=None,
                authorization=SESSION_AUTHORIZATION,
            )

    def test_14_existing_output_rejected(self):
        out = self.external / "existing"
        out.mkdir()
        with self.assertRaises(AuthorizationPropagationError):
            run_bounded_synchronized_15m_session_with_microstructure_auth_propagation_v1(
                repo_root=self.repo,
                output_directory=out,
                max_cycles=1,
                source_attestation="x",
                minimum_latest_closed_candle_utc=None,
                authorization=SESSION_AUTHORIZATION,
            )

    def test_15_cycle_limit_rejected(self):
        with self.assertRaises(AuthorizationPropagationError):
            run_bounded_synchronized_15m_session_with_microstructure_auth_propagation_v1(
                repo_root=self.repo,
                output_directory=self.external / "cycle",
                max_cycles=9,
                source_attestation="x",
                minimum_latest_closed_candle_utc=None,
                authorization=SESSION_AUTHORIZATION,
            )

    def _run_mock_package(self, out_name="ok"):
        observed = {
            "inner_authorization": None,
            "micro_authorization": None,
        }

        def micro_capture(**kwargs):
            observed["micro_authorization"] = kwargs["authorization"]
            return {
                "capability": "PUBLIC_READ_ONLY_MICROSTRUCTURE_SNAPSHOT_V1_1",
                "request_count": 7,
            }

        def inner_runner(**kwargs):
            observed["inner_authorization"] = kwargs["authorization"]
            child = Path(kwargs["output_directory"])
            child.mkdir()
            (child / "manifest.sha256").write_text(
                "inner-manifest\n",
                encoding="utf-8",
            )
            kwargs["microstructure_capture_callable"](
                repo_root=kwargs["repo_root"],
                output_directory=child / "microstructure",
                authorization=LEGACY_DELEGATED_MICROSTRUCTURE_AUTHORIZATION,
            )
            return {
                "capability": "SYNCHRONIZED_15M_OBSERVATION_V1_1",
                "completed_cycles": 1,
                "candidate_count": 0,
                "stop_reason": "MAX_CYCLES_COMPLETED",
                "network_request_count": 8,
                "network_requests_per_completed_cycle": 8,
            }

        def inner_validator(directory):
            self.assertTrue(Path(directory).is_dir())
            return {
                "completed_cycles": 1,
                "candidate_count": 0,
                "network_request_count": 8,
            }

        out = self.external / out_name
        result = (
            run_bounded_synchronized_15m_session_with_microstructure_auth_propagation_v1(
                repo_root=self.repo,
                output_directory=out,
                max_cycles=1,
                source_attestation="REAL_MARKET_DATA_SOURCE_HUMAN_ATTESTED_NOT_SYNTHETIC",
                minimum_latest_closed_candle_utc=None,
                authorization=SESSION_AUTHORIZATION,
                microstructure_capture_callable=micro_capture,
                inner_run_callable=inner_runner,
                inner_validate_callable=inner_validator,
            )
        )
        return out, result, observed, inner_validator

    def test_16_mock_run_uses_inner_closed_session_auth_only_internally(self):
        _, _, observed, _ = self._run_mock_package("inner-auth")
        self.assertEqual(
            observed["inner_authorization"],
            sync_v11.SESSION_AUTHORIZATION,
        )

    def test_17_mock_run_delegates_new_microstructure_v1_1_auth(self):
        _, _, observed, _ = self._run_mock_package("micro-auth")
        self.assertEqual(
            observed["micro_authorization"],
            MICROSTRUCTURE_V1_1_AUTHORIZATION,
        )

    def test_18_mock_run_network_contract_preserved(self):
        _, result, _, _ = self._run_mock_package("network")
        self.assertEqual(result["completed_cycles"], 1)
        self.assertEqual(result["network_request_count"], 8)
        self.assertEqual(result["network_requests_per_completed_cycle"], 8)

    def test_19_mock_run_records_propagation(self):
        _, result, _, _ = self._run_mock_package("propagation")
        self.assertTrue(result["microstructure_authorization_propagated"])
        self.assertEqual(result["authorization_propagation_count"], 1)

    def test_20_mock_run_legacy_user_auths_false(self):
        _, result, _, _ = self._run_mock_package("legacy-false")
        self.assertFalse(result["legacy_user_session_authorization_accepted"])
        self.assertFalse(
            result["legacy_microstructure_authorization_user_accepted"]
        )

    def test_21_outer_attestation_created(self):
        out, _, _, _ = self._run_mock_package("attestation")
        data = json.loads(
            (out / "authorization_propagation.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertTrue(data["microstructure_authorization_repaired"])
        self.assertTrue(
            data["legacy_delegated_microstructure_authorization_intercepted"]
        )

    def test_22_outer_manifest_has_two_entries(self):
        out, _, _, _ = self._run_mock_package("manifest")
        lines = (
            (out / "manifest.sha256")
            .read_text(encoding="utf-8")
            .splitlines()
        )
        self.assertEqual(len(lines), 2)

    def test_23_roundtrip_validation(self):
        out, _, _, validator = self._run_mock_package("roundtrip")
        result = validate_authorization_propagation_session_v1(
            out,
            inner_validate_callable=validator,
        )
        self.assertEqual(result["completed_cycles"], 1)
        self.assertEqual(result["outer_manifest_entries"], 2)

    def test_24_manifest_tamper_detected(self):
        out, _, _, validator = self._run_mock_package("tamper")
        with (out / "authorization_propagation.json").open(
            "ab"
        ) as handle:
            handle.write(b"x")
        with self.assertRaises(AuthorizationPropagationError):
            validate_authorization_propagation_session_v1(
                out,
                inner_validate_callable=validator,
            )

    def test_25_primary_rule_not_modified(self):
        out, _, _, _ = self._run_mock_package("primary")
        data = json.loads(
            (out / "authorization_propagation.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertFalse(data["primary_long_rule_modified"])

    def test_26_no_permissions_enabled(self):
        out, _, _, _ = self._run_mock_package("permissions")
        data = json.loads(
            (out / "authorization_propagation.json").read_text(
                encoding="utf-8"
            )
        )
        for field in (
            "official_append_allowed",
            "official_dataset_write_allowed",
            "signal_generation_enabled",
            "live_alerts_allowed",
            "paper_trade_execution_allowed",
            "real_capital_allowed",
            "market_execution_allowed",
            "exchange_execution_allowed",
            "automation_allowed",
            "execution_allowed",
        ):
            self.assertIs(data[field], False)

    def test_27_automatic_retry_disabled(self):
        out, _, _, _ = self._run_mock_package("retry")
        data = json.loads(
            (out / "authorization_propagation.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertFalse(data["automatic_retry_allowed"])

    def test_28_attestation_preserves_inner_manifest_hash(self):
        out, _, _, _ = self._run_mock_package("inner-hash")
        data = json.loads(
            (out / "authorization_propagation.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(
            len(data["inner_session_manifest_sha256"]),
            64,
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
