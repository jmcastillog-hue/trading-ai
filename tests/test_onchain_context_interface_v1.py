from __future__ import annotations

import hashlib
import json
import math
import os
import tempfile
import unittest
from pathlib import Path

from src.context.onchain_context_interface_v1 import (
    CAPABILITY,
    FEATURE_ID,
    PACKAGE_AUTHORIZATION,
    SNAPSHOT_SCHEMA_VERSION,
    SOURCE_KIND,
    OnchainContextInterfaceError,
    build_onchain_context_interface_v1_component,
    prepare_onchain_context_interface_v1_package,
    validate_component_against_level_a_pack_v1,
    validate_onchain_context_interface_policy_v1,
    validate_onchain_context_interface_v1_component,
    validate_onchain_context_interface_v1_package,
    validate_onchain_context_snapshot_v1,
)

POLICY_EFFECTIVE = "2026-08-19T02:27:00+00:00"
REFERENCE = "2026-08-19T02:30:00+00:00"

def descriptor(reference=REFERENCE, cutoff="2026-08-19T02:30:10+00:00"):
    return {
        "observation_descriptor_schema_version": "FORWARD_OUTCOME_OBSERVATION_DESCRIPTOR_V1",
        "observation_id": "OBS_ONCHAIN_001",
        "symbol": "BTCUSDT",
        "timeframe": "15m",
        "reference_boundary_utc": reference,
        "reference_closed_candle_utc": "2026-08-19T02:29:59.999000+00:00",
        "synchronized_context_available_at_utc": cutoff,
        "primary_candidate_detected": False,
    }

def policy():
    return {
        "schema_version": "ONCHAIN_CONTEXT_INTERFACE_POLICY_V1",
        "feature_id": "ONCHAIN_CONTEXT_INTERFACE_V1",
        "policy_effective_from_utc": POLICY_EFFECTIVE,
        "snapshot_schema_version": "ONCHAIN_CONTEXT_SNAPSHOT_V1",
        "asset": "BTC",
        "network": "BITCOIN",
        "min_metric_count": 1,
        "max_metric_count": 64,
        "exact_observation_identity_required": True,
        "metric_observation_not_after_reference_required": True,
        "metric_information_cutoff_not_before_observation_end_required": True,
        "metric_provider_availability_not_before_information_cutoff_required": True,
        "snapshot_creation_not_before_metric_availability_required": True,
        "metric_ids_unique_and_sorted_required": True,
        "producer_network_fetch_allowed": False,
        "producer_market_data_fetch_allowed": False,
        "producer_chain_rpc_allowed": False,
        "producer_provider_api_allowed": False,
        "metric_interpretation_allowed": False,
        "directional_meaning_assigned": False,
        "threshold_signal_allowed": False,
        "composite_score_assigned": False,
        "signal_semantics": False,
        "future_outcomes_used": False,
    }

def metric(metric_id, value, end, info, available):
    return {
        "metric_id": metric_id,
        "unit": "NATIVE",
        "value": value,
        "revision_id": "REV_001",
        "observation_start_utc": end,
        "observation_end_utc": end,
        "information_cutoff_utc": info,
        "provider_available_at_utc": available,
    }

def snapshot(
    created="2026-08-19T02:30:05+00:00",
    reference=REFERENCE,
):
    return {
        "snapshot_schema_version": "ONCHAIN_CONTEXT_SNAPSHOT_V1",
        "observation_id": "OBS_ONCHAIN_001",
        "reference_boundary_utc": reference,
        "asset": "BTC",
        "network": "BITCOIN",
        "provider_name": "EXTERNAL_PROVIDER",
        "dataset_id": "BTC_ONCHAIN_CONTEXT",
        "dataset_version": "V1",
        "source_reference": "frozen-source-reference-001",
        "metric_schema_sha256": "a" * 64,
        "snapshot_created_at_utc": created,
        "metrics": [
            metric(
                "ACTIVE_ADDRESSES",
                100.0,
                "2026-08-19T02:00:00+00:00",
                "2026-08-19T02:00:01+00:00",
                "2026-08-19T02:00:02+00:00",
            ),
            metric(
                "EXCHANGE_NETFLOW",
                -5.0,
                "2026-08-19T02:15:00+00:00",
                "2026-08-19T02:15:01+00:00",
                "2026-08-19T02:15:02+00:00",
            ),
        ],
    }

def component(desc=None, snap=None, produced="2026-08-19T02:30:06+00:00"):
    return build_onchain_context_interface_v1_component(
        observation_descriptor=desc or descriptor(),
        external_snapshot=snap or snapshot(),
        external_snapshot_sha256="b" * 64,
        policy=policy(),
        policy_sha256="c" * 64,
        produced_at_utc=produced,
    )

class Tests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        self.repo = root / "repo"
        self.repo.mkdir()
        (self.repo / ".git").mkdir()

        official = self.repo / "data" / "forward"
        official.mkdir(parents=True)
        (official / "long_forward_observation_dataset_v1.csv").write_text(
            "header\n",
            encoding="utf-8",
        )
        (
            official
            / "long_forward_observation_dataset_v1.manifest.csv"
        ).write_text("manifest\n", encoding="utf-8")

        resources = self.repo / "src" / "context" / "resources"
        resources.mkdir(parents=True)
        (
            resources / "onchain_context_interface_policy_v1.json"
        ).write_text(
            json.dumps(policy(), sort_keys=True, indent=2) + "\n",
            encoding="utf-8",
        )

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

    def test_01_identity(self):
        self.assertEqual(CAPABILITY, FEATURE_ID)
        self.assertEqual(SOURCE_KIND, "FUTURE_INTERFACE")
        self.assertEqual(
            SNAPSHOT_SCHEMA_VERSION,
            "ONCHAIN_CONTEXT_SNAPSHOT_V1",
        )

    def test_02_authorization(self):
        self.assertEqual(
            PACKAGE_AUTHORIZATION,
            "PREPARE_ONCHAIN_CONTEXT_INTERFACE_V1",
        )

    def test_03_policy_valid(self):
        result = validate_onchain_context_interface_policy_v1(policy())
        self.assertEqual(result["asset"], "BTC")
        self.assertEqual(
            result["policy_effective_from_utc"],
            POLICY_EFFECTIVE,
        )

    def test_04_policy_network_forbidden(self):
        value = policy()
        value["producer_network_fetch_allowed"] = True
        with self.assertRaises(OnchainContextInterfaceError):
            validate_onchain_context_interface_policy_v1(value)

    def test_05_snapshot_valid(self):
        result = validate_onchain_context_snapshot_v1(
            snapshot(),
            policy=validate_onchain_context_interface_policy_v1(policy()),
        )
        self.assertEqual(len(result["metrics"]), 2)

    def test_06_outcome_field_fails(self):
        value = snapshot()
        value["metrics"][0]["forward_return"] = 0.1
        with self.assertRaises(OnchainContextInterfaceError):
            validate_onchain_context_snapshot_v1(
                value,
                policy=validate_onchain_context_interface_policy_v1(policy()),
            )

    def test_07_duplicate_metric_id_fails(self):
        value = snapshot()
        value["metrics"][1]["metric_id"] = "ACTIVE_ADDRESSES"
        with self.assertRaises(OnchainContextInterfaceError):
            validate_onchain_context_snapshot_v1(
                value,
                policy=validate_onchain_context_interface_policy_v1(policy()),
            )

    def test_08_unsorted_metric_ids_fail(self):
        value = snapshot()
        value["metrics"].reverse()
        with self.assertRaises(OnchainContextInterfaceError):
            validate_onchain_context_snapshot_v1(
                value,
                policy=validate_onchain_context_interface_policy_v1(policy()),
            )

    def test_09_observation_after_reference_fails(self):
        value = snapshot()
        value["metrics"][1] = metric(
            "EXCHANGE_NETFLOW",
            -5.0,
            "2026-08-19T02:31:00+00:00",
            "2026-08-19T02:31:01+00:00",
            "2026-08-19T02:31:02+00:00",
        )
        value["snapshot_created_at_utc"] = "2026-08-19T02:31:03+00:00"
        with self.assertRaises(OnchainContextInterfaceError):
            component(
                snap=value,
                produced="2026-08-19T02:31:04+00:00",
            )

    def test_10_information_before_observation_fails(self):
        value = snapshot()
        value["metrics"][0]["information_cutoff_utc"] = (
            "2026-08-19T01:59:59+00:00"
        )
        with self.assertRaises(OnchainContextInterfaceError):
            validate_onchain_context_snapshot_v1(
                value,
                policy=validate_onchain_context_interface_policy_v1(policy()),
            )

    def test_11_provider_available_before_information_fails(self):
        value = snapshot()
        value["metrics"][0]["provider_available_at_utc"] = (
            "2026-08-19T02:00:00+00:00"
        )
        with self.assertRaises(OnchainContextInterfaceError):
            validate_onchain_context_snapshot_v1(
                value,
                policy=validate_onchain_context_interface_policy_v1(policy()),
            )

    def test_12_snapshot_created_before_metric_available_fails(self):
        value = snapshot(created="2026-08-19T02:10:00+00:00")
        with self.assertRaises(OnchainContextInterfaceError):
            validate_onchain_context_snapshot_v1(
                value,
                policy=validate_onchain_context_interface_policy_v1(policy()),
            )

    def test_13_reference_must_match_descriptor(self):
        value = snapshot(reference="2026-08-19T02:15:00+00:00")
        with self.assertRaises(OnchainContextInterfaceError):
            component(snap=value)

    def test_14_observation_id_must_match_descriptor(self):
        value = snapshot()
        value["observation_id"] = "OTHER"
        with self.assertRaises(OnchainContextInterfaceError):
            component(snap=value)

    def test_15_old_snapshot_pack_ineligible_due_policy_floor(self):
        desc = descriptor(
            reference="2026-08-19T02:15:00+00:00",
            cutoff="2026-08-19T02:15:10+00:00",
        )
        value = snapshot(
            created="2026-08-19T02:10:00+00:00",
            reference="2026-08-19T02:15:00+00:00",
        )
        value["metrics"] = [
            metric(
                "ACTIVE_ADDRESSES",
                100.0,
                "2026-08-19T01:45:00+00:00",
                "2026-08-19T01:45:01+00:00",
                "2026-08-19T01:45:02+00:00",
            )
        ]
        result = validate_component_against_level_a_pack_v1(
            observation_descriptor=desc,
            component=component(
                desc=desc,
                snap=value,
                produced="2026-08-19T02:27:01+00:00",
            ),
        )
        self.assertFalse(result["point_in_time_eligible"])
        self.assertEqual(
            result["eligibility_reason"],
            "AVAILABLE_AFTER_CONTEXT_CUTOFF",
        )

    def test_16_post_policy_pack_eligible(self):
        result = validate_component_against_level_a_pack_v1(
            observation_descriptor=descriptor(),
            component=component(),
        )
        self.assertTrue(result["point_in_time_eligible"])

    def test_17_metric_ages_are_descriptive(self):
        payload = component()["payload"]
        ages = [
            item["age_seconds_at_reference"]
            for item in payload["metrics"]
        ]
        self.assertEqual(ages, [1800.0, 900.0])

    def test_18_no_network_rpc_interpretation_or_signal(self):
        payload = component()["payload"]
        self.assertFalse(payload["producer_network_fetch_executed"])
        self.assertFalse(payload["producer_provider_api_executed"])
        self.assertFalse(payload["producer_chain_rpc_executed"])
        self.assertFalse(payload["metric_interpretation_performed"])
        self.assertFalse(payload["threshold_signal_evaluated"])
        self.assertFalse(payload["directional_semantics"])
        self.assertFalse(payload["signal_semantics"])

    def test_19_component_validator(self):
        result = validate_onchain_context_interface_v1_component(
            component()
        )
        self.assertEqual(result["metric_count"], 2)

    def test_20_nan_metric_fails(self):
        value = snapshot()
        value["metrics"][0]["value"] = math.nan
        with self.assertRaises(OnchainContextInterfaceError):
            validate_onchain_context_snapshot_v1(
                value,
                policy=validate_onchain_context_interface_policy_v1(policy()),
            )

    def test_21_bad_metric_schema_sha_fails(self):
        value = snapshot()
        value["metric_schema_sha256"] = "bad"
        with self.assertRaises(OnchainContextInterfaceError):
            validate_onchain_context_snapshot_v1(
                value,
                policy=validate_onchain_context_interface_policy_v1(policy()),
            )

    def test_22_source_metadata_required(self):
        value = snapshot()
        value["provider_name"] = ""
        with self.assertRaises(OnchainContextInterfaceError):
            validate_onchain_context_snapshot_v1(
                value,
                policy=validate_onchain_context_interface_policy_v1(policy()),
            )

    def test_23_snapshot_after_context_cutoff_pack_ineligible(self):
        desc = descriptor(
            cutoff="2026-08-19T02:30:10+00:00"
        )
        value = snapshot(
            created="2026-08-19T02:30:20+00:00"
        )
        result = validate_component_against_level_a_pack_v1(
            observation_descriptor=desc,
            component=component(
                desc=desc,
                snap=value,
                produced="2026-08-19T02:30:21+00:00",
            ),
        )
        self.assertFalse(result["point_in_time_eligible"])
        self.assertEqual(
            result["eligibility_reason"],
            "AVAILABLE_AFTER_CONTEXT_CUTOFF",
        )

    def _write(self, name, value):
        path = self.external / name
        path.write_text(
            json.dumps(value, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        return path

    def test_24_missing_auth_fails(self):
        with self.assertRaises(OnchainContextInterfaceError):
            prepare_onchain_context_interface_v1_package(
                repo_root=self.repo,
                observation_descriptor_json=self._write(
                    "descriptor.json",
                    descriptor(),
                ),
                external_snapshot_json=self._write(
                    "snapshot.json",
                    snapshot(),
                ),
                output_directory=self.external / "missing",
                produced_at_utc="2026-08-19T02:30:06+00:00",
                authorization=None,
            )

    def test_25_output_inside_repo_fails(self):
        with self.assertRaises(OnchainContextInterfaceError):
            prepare_onchain_context_interface_v1_package(
                repo_root=self.repo,
                observation_descriptor_json=self._write(
                    "descriptor2.json",
                    descriptor(),
                ),
                external_snapshot_json=self._write(
                    "snapshot2.json",
                    snapshot(),
                ),
                output_directory=self.repo / "output",
                produced_at_utc="2026-08-19T02:30:06+00:00",
                authorization=PACKAGE_AUTHORIZATION,
            )

    def test_26_gate_enabled_fails(self):
        os.environ[
            "TRADING_AI_OFFICIAL_LONG_EVIDENCE_APPEND_ALLOWED"
        ] = "1"
        with self.assertRaises(OnchainContextInterfaceError):
            prepare_onchain_context_interface_v1_package(
                repo_root=self.repo,
                observation_descriptor_json=self._write(
                    "descriptor3.json",
                    descriptor(),
                ),
                external_snapshot_json=self._write(
                    "snapshot3.json",
                    snapshot(),
                ),
                output_directory=self.external / "gate",
                produced_at_utc="2026-08-19T02:30:06+00:00",
                authorization=PACKAGE_AUTHORIZATION,
            )

    def test_27_snapshot_inside_repo_fails(self):
        inside = self.repo / "inside.json"
        inside.write_text(
            json.dumps(snapshot(), sort_keys=True) + "\n",
            encoding="utf-8",
        )
        with self.assertRaises(OnchainContextInterfaceError):
            prepare_onchain_context_interface_v1_package(
                repo_root=self.repo,
                observation_descriptor_json=self._write(
                    "descriptor4.json",
                    descriptor(),
                ),
                external_snapshot_json=inside,
                output_directory=self.external / "inside",
                produced_at_utc="2026-08-19T02:30:06+00:00",
                authorization=PACKAGE_AUTHORIZATION,
            )

    def test_28_roundtrip_tamper_and_immutability(self):
        descriptor_path = self._write("descriptor5.json", descriptor())
        snapshot_path = self._write("snapshot5.json", snapshot())

        snapshot_before = hashlib.sha256(
            snapshot_path.read_bytes()
        ).hexdigest()

        dataset = (
            self.repo
            / "data"
            / "forward"
            / "long_forward_observation_dataset_v1.csv"
        )
        official_manifest = (
            self.repo
            / "data"
            / "forward"
            / "long_forward_observation_dataset_v1.manifest.csv"
        )
        official_before = (
            dataset.read_bytes(),
            official_manifest.read_bytes(),
        )

        output = self.external / "roundtrip"

        prepare_onchain_context_interface_v1_package(
            repo_root=self.repo,
            observation_descriptor_json=descriptor_path,
            external_snapshot_json=snapshot_path,
            output_directory=output,
            produced_at_utc="2026-08-19T02:30:06+00:00",
            authorization=PACKAGE_AUTHORIZATION,
        )

        result = validate_onchain_context_interface_v1_package(output)
        self.assertEqual(result["manifest_entries"], 2)
        self.assertEqual(
            hashlib.sha256(snapshot_path.read_bytes()).hexdigest(),
            snapshot_before,
        )
        self.assertEqual(
            (dataset.read_bytes(), official_manifest.read_bytes()),
            official_before,
        )

        with (
            output / "onchain_context_interface_component.json"
        ).open("ab") as handle:
            handle.write(b"x")

        with self.assertRaises(OnchainContextInterfaceError):
            validate_onchain_context_interface_v1_package(output)

if __name__ == "__main__":
    unittest.main(verbosity=2)
