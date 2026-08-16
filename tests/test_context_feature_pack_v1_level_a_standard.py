from __future__ import annotations

import copy
import hashlib
import json
import os
import tempfile
import unittest
from pathlib import Path

from src.context.context_feature_pack_v1_level_a_standard import (
    CAPABILITY,
    FEATURE_IDS,
    FEATURE_REGISTRY,
    PACKAGE_AUTHORIZATION,
    ContextFeaturePackError,
    build_context_feature_pack_v1,
    prepare_context_feature_pack_v1_package,
    validate_context_feature_pack_v1,
    validate_context_feature_pack_v1_package,
)


def descriptor(
    *,
    context_available="2026-08-10T23:45:12.139898+00:00",
    candidate=False,
):
    return {
        "observation_descriptor_schema_version":
            "FORWARD_OUTCOME_OBSERVATION_DESCRIPTOR_V1",
        "observation_id": "OBS_001",
        "symbol": "BTCUSDT",
        "timeframe": "15m",
        "reference_boundary_utc": "2026-08-10T23:45:00+00:00",
        "synchronized_context_available_at_utc": context_available,
        "primary_candidate_detected": candidate,
    }


def unavailable_components(status="NOT_CONFIGURED"):
    result = {}
    for item in FEATURE_REGISTRY:
        feature_id = item["feature_id"]
        result[feature_id] = {
            "feature_id": feature_id,
            "source_kind": item["source_kind"],
            "feature_schema_version": feature_id + "_SCHEMA_V1",
            "status": status,
            "reason": "not configured in synthetic fixture",
            "available_at_utc": None,
            "information_cutoff_utc": None,
            "source_artifact_sha256": None,
            "payload": None,
        }
    return result


def make_available(
    components,
    feature_id,
    *,
    available_at="2026-08-10T23:45:10+00:00",
    information_cutoff="2026-08-10T23:45:00+00:00",
    payload=None,
):
    item = components[feature_id]
    item["status"] = "AVAILABLE"
    item["reason"] = None
    item["available_at_utc"] = available_at
    item["information_cutoff_utc"] = information_cutoff
    item["source_artifact_sha256"] = "a" * 64
    item["payload"] = payload or {"regime": "SYNTHETIC"}


class Tests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        self.repo = root / "repo"
        self.repo.mkdir()
        (self.repo / ".git").mkdir()
        official = self.repo / "data" / "forward"
        official.mkdir(parents=True)
        (
            official / "long_forward_observation_dataset_v1.csv"
        ).write_text("header\n", encoding="utf-8")
        (
            official
            / "long_forward_observation_dataset_v1.manifest.csv"
        ).write_text("manifest\n", encoding="utf-8")
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
            "CONTEXT_FEATURE_PACK_V1_LEVEL_A_STANDARD",
        )

    def test_02_registry_has_8_features(self):
        self.assertEqual(len(FEATURE_IDS), 8)

    def test_03_registry_order_exact(self):
        self.assertEqual(
            FEATURE_IDS,
            (
                "BTC_CYCLE_HALVING_CONTEXT_V1",
                "EVENT_RISK_CALENDAR_CONTEXT_V1",
                "EXTERNAL_CYCLE_REGRESSION_BASELINE_V1",
                "LIQUIDITY_SWEEP_PATTERN_CONTEXT_V1",
                "EXTERNAL_THESIS_MODEL_CARD_V1",
                "ANALOG_ENGINE_CONTEXT_V1",
                "SYNCHRONIZED_MICROSTRUCTURE_CONTEXT_V1",
                "ONCHAIN_CONTEXT_INTERFACE_V1",
            ),
        )

    def test_04_package_authorization_exact(self):
        self.assertEqual(
            PACKAGE_AUTHORIZATION,
            "PREPARE_CONTEXT_FEATURE_PACK_V1_LEVEL_A_STANDARD",
        )

    def test_05_all_not_configured_pack_valid(self):
        pack = build_context_feature_pack_v1(
            observation_descriptor=descriptor(),
            components=unavailable_components(),
            pack_id="PACK_SYNTHETIC",
        )
        result = validate_context_feature_pack_v1(pack)
        self.assertEqual(result["feature_count"], 8)
        self.assertEqual(
            result["point_in_time_eligible_feature_count"],
            0,
        )

    def test_06_available_before_cutoff_is_eligible(self):
        components = unavailable_components()
        make_available(
            components,
            "BTC_CYCLE_HALVING_CONTEXT_V1",
        )
        pack = build_context_feature_pack_v1(
            observation_descriptor=descriptor(),
            components=components,
        )
        feature = pack["features"][0]
        self.assertTrue(feature["point_in_time_eligible"])

    def test_07_available_after_cutoff_is_ineligible(self):
        components = unavailable_components()
        make_available(
            components,
            "BTC_CYCLE_HALVING_CONTEXT_V1",
            available_at="2026-08-10T23:46:00+00:00",
        )
        pack = build_context_feature_pack_v1(
            observation_descriptor=descriptor(),
            components=components,
        )
        feature = pack["features"][0]
        self.assertFalse(feature["point_in_time_eligible"])
        self.assertEqual(
            feature["eligibility_reason"],
            "AVAILABLE_AFTER_CONTEXT_CUTOFF",
        )

    def test_08_information_after_cutoff_is_ineligible(self):
        components = unavailable_components()
        make_available(
            components,
            "BTC_CYCLE_HALVING_CONTEXT_V1",
            available_at="2026-08-10T23:46:00+00:00",
            information_cutoff="2026-08-10T23:45:30+00:00",
        )
        pack = build_context_feature_pack_v1(
            observation_descriptor=descriptor(
                context_available="2026-08-10T23:47:00+00:00"
            ),
            components=components,
        )
        feature = pack["features"][0]
        self.assertTrue(feature["point_in_time_eligible"])

    def test_09_information_cannot_follow_availability(self):
        components = unavailable_components()
        make_available(
            components,
            "BTC_CYCLE_HALVING_CONTEXT_V1",
            available_at="2026-08-10T23:45:05+00:00",
            information_cutoff="2026-08-10T23:45:06+00:00",
        )
        with self.assertRaises(ContextFeaturePackError):
            build_context_feature_pack_v1(
                observation_descriptor=descriptor(),
                components=components,
            )

    def test_10_payload_sha_is_canonical(self):
        components = unavailable_components()
        make_available(
            components,
            "BTC_CYCLE_HALVING_CONTEXT_V1",
            payload={"b": 2, "a": 1},
        )
        pack = build_context_feature_pack_v1(
            observation_descriptor=descriptor(),
            components=components,
        )
        payload = {"a": 1, "b": 2}
        expected = hashlib.sha256(
            (
                json.dumps(
                    payload,
                    sort_keys=True,
                    separators=(",", ":"),
                    ensure_ascii=True,
                    allow_nan=False,
                )
                + "\n"
            ).encode("utf-8")
        ).hexdigest()
        self.assertEqual(
            pack["features"][0]["payload_sha256"],
            expected,
        )

    def test_11_primary_candidate_false_preserved(self):
        pack = build_context_feature_pack_v1(
            observation_descriptor=descriptor(candidate=False),
            components=unavailable_components(),
        )
        self.assertFalse(pack["primary_candidate_detected"])
        self.assertTrue(pack["primary_candidate_state_preserved"])

    def test_12_primary_candidate_true_preserved(self):
        pack = build_context_feature_pack_v1(
            observation_descriptor=descriptor(candidate=True),
            components=unavailable_components(),
        )
        self.assertTrue(pack["primary_candidate_detected"])
        self.assertTrue(pack["primary_candidate_state_preserved"])

    def test_13_missing_feature_fails(self):
        components = unavailable_components()
        components.pop(FEATURE_IDS[-1])
        with self.assertRaises(ContextFeaturePackError):
            build_context_feature_pack_v1(
                observation_descriptor=descriptor(),
                components=components,
            )

    def test_14_extra_feature_fails(self):
        components = unavailable_components()
        components["EXTRA"] = copy.deepcopy(
            components[FEATURE_IDS[0]]
        )
        components["EXTRA"]["feature_id"] = "EXTRA"
        with self.assertRaises(ContextFeaturePackError):
            build_context_feature_pack_v1(
                observation_descriptor=descriptor(),
                components=components,
            )

    def test_15_key_id_mismatch_fails(self):
        components = unavailable_components()
        components[FEATURE_IDS[0]]["feature_id"] = FEATURE_IDS[1]
        with self.assertRaises(ContextFeaturePackError):
            build_context_feature_pack_v1(
                observation_descriptor=descriptor(),
                components=components,
            )

    def test_16_invalid_status_fails(self):
        components = unavailable_components()
        components[FEATURE_IDS[0]]["status"] = "BROKEN"
        with self.assertRaises(ContextFeaturePackError):
            build_context_feature_pack_v1(
                observation_descriptor=descriptor(),
                components=components,
            )

    def test_17_invalid_available_hash_fails(self):
        components = unavailable_components()
        make_available(
            components,
            "BTC_CYCLE_HALVING_CONTEXT_V1",
        )
        components[
            "BTC_CYCLE_HALVING_CONTEXT_V1"
        ]["source_artifact_sha256"] = "bad"
        with self.assertRaises(ContextFeaturePackError):
            build_context_feature_pack_v1(
                observation_descriptor=descriptor(),
                components=components,
            )

    def test_18_unavailable_payload_fails(self):
        components = unavailable_components()
        components[FEATURE_IDS[0]]["payload"] = {"x": 1}
        with self.assertRaises(ContextFeaturePackError):
            build_context_feature_pack_v1(
                observation_descriptor=descriptor(),
                components=components,
            )

    def test_19_context_anchor_ceils_to_next_bar(self):
        pack = build_context_feature_pack_v1(
            observation_descriptor=descriptor(),
            components=unavailable_components(),
        )
        self.assertEqual(
            pack["context_anchor_open_utc"],
            "2026-08-11T00:00:00+00:00",
        )

    def test_20_exact_boundary_stays_exact(self):
        pack = build_context_feature_pack_v1(
            observation_descriptor=descriptor(
                context_available="2026-08-11T00:00:00+00:00"
            ),
            components=unavailable_components(),
        )
        self.assertEqual(
            pack["context_anchor_open_utc"],
            "2026-08-11T00:00:00+00:00",
        )

    def test_21_no_scoring_or_direction(self):
        pack = build_context_feature_pack_v1(
            observation_descriptor=descriptor(),
            components=unavailable_components(),
        )
        self.assertFalse(pack["composite_scoring_performed"])
        self.assertFalse(pack["direction_inferred"])
        self.assertFalse(pack["trade_action_inferred"])
        self.assertNotIn("composite_score", pack)
        self.assertNotIn("direction", pack)

    def test_22_permissions_false(self):
        pack = build_context_feature_pack_v1(
            observation_descriptor=descriptor(),
            components=unavailable_components(),
        )
        for field in (
            "candidate_modification_allowed",
            "signal_generation_enabled",
            "live_alerts_allowed",
            "paper_trade_execution_allowed",
            "real_capital_allowed",
            "official_append_allowed",
            "execution_allowed",
        ):
            self.assertIs(pack[field], False)

    def _write_inputs(self):
        descriptor_path = self.external / "descriptor.json"
        components_path = self.external / "components.json"
        descriptor_path.write_text(
            json.dumps(descriptor(), sort_keys=True) + "\n",
            encoding="utf-8",
        )
        components_path.write_text(
            json.dumps(
                unavailable_components(),
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )
        return descriptor_path, components_path

    def test_23_package_missing_auth_fails(self):
        descriptor_path, components_path = self._write_inputs()
        with self.assertRaises(ContextFeaturePackError):
            prepare_context_feature_pack_v1_package(
                repo_root=self.repo,
                observation_descriptor_json=descriptor_path,
                components_json=components_path,
                output_directory=self.external / "package",
                authorization=None,
            )

    def test_24_package_output_inside_repo_fails(self):
        descriptor_path, components_path = self._write_inputs()
        with self.assertRaises(ContextFeaturePackError):
            prepare_context_feature_pack_v1_package(
                repo_root=self.repo,
                observation_descriptor_json=descriptor_path,
                components_json=components_path,
                output_directory=self.repo / "package",
                authorization=PACKAGE_AUTHORIZATION,
            )

    def test_25_package_existing_output_fails(self):
        descriptor_path, components_path = self._write_inputs()
        output = self.external / "existing"
        output.mkdir()
        with self.assertRaises(ContextFeaturePackError):
            prepare_context_feature_pack_v1_package(
                repo_root=self.repo,
                observation_descriptor_json=descriptor_path,
                components_json=components_path,
                output_directory=output,
                authorization=PACKAGE_AUTHORIZATION,
            )

    def test_26_gate_enabled_fails(self):
        descriptor_path, components_path = self._write_inputs()
        os.environ[
            "TRADING_AI_OFFICIAL_LONG_EVIDENCE_APPEND_ALLOWED"
        ] = "1"
        with self.assertRaises(ContextFeaturePackError):
            prepare_context_feature_pack_v1_package(
                repo_root=self.repo,
                observation_descriptor_json=descriptor_path,
                components_json=components_path,
                output_directory=self.external / "gate",
                authorization=PACKAGE_AUTHORIZATION,
            )

    def test_27_package_roundtrip(self):
        descriptor_path, components_path = self._write_inputs()
        output = self.external / "roundtrip"
        result = prepare_context_feature_pack_v1_package(
            repo_root=self.repo,
            observation_descriptor_json=descriptor_path,
            components_json=components_path,
            output_directory=output,
            authorization=PACKAGE_AUTHORIZATION,
            pack_id="PACK_ROUNDTRIP",
        )
        validation = validate_context_feature_pack_v1_package(
            output
        )
        self.assertEqual(result["feature_count"], 8)
        self.assertEqual(validation["manifest_entries"], 2)

    def test_28_package_tamper_detected(self):
        descriptor_path, components_path = self._write_inputs()
        output = self.external / "tamper"
        prepare_context_feature_pack_v1_package(
            repo_root=self.repo,
            observation_descriptor_json=descriptor_path,
            components_json=components_path,
            output_directory=output,
            authorization=PACKAGE_AUTHORIZATION,
        )
        with (output / "context_feature_pack.json").open(
            "ab"
        ) as handle:
            handle.write(b"x")
        with self.assertRaises(ContextFeaturePackError):
            validate_context_feature_pack_v1_package(output)

    def test_29_official_artifacts_unchanged(self):
        descriptor_path, components_path = self._write_inputs()
        dataset = (
            self.repo
            / "data"
            / "forward"
            / "long_forward_observation_dataset_v1.csv"
        )
        manifest = (
            self.repo
            / "data"
            / "forward"
            / "long_forward_observation_dataset_v1.manifest.csv"
        )
        before = (dataset.read_bytes(), manifest.read_bytes())
        prepare_context_feature_pack_v1_package(
            repo_root=self.repo,
            observation_descriptor_json=descriptor_path,
            components_json=components_path,
            output_directory=self.external / "official",
            authorization=PACKAGE_AUTHORIZATION,
        )
        after = (dataset.read_bytes(), manifest.read_bytes())
        self.assertEqual(before, after)

    def test_30_package_checks_network_false(self):
        descriptor_path, components_path = self._write_inputs()
        output = self.external / "network"
        prepare_context_feature_pack_v1_package(
            repo_root=self.repo,
            observation_descriptor_json=descriptor_path,
            components_json=components_path,
            output_directory=output,
            authorization=PACKAGE_AUTHORIZATION,
        )
        checks = json.loads(
            (output / "pack_checks.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertFalse(checks["real_network_request_executed"])
        self.assertFalse(
            checks["component_source_network_performed_by_pack"]
        )

    def test_31_inputs_are_not_mutated(self):
        components = unavailable_components()
        before = copy.deepcopy(components)
        build_context_feature_pack_v1(
            observation_descriptor=descriptor(),
            components=components,
        )
        self.assertEqual(components, before)

    def test_32_malformed_descriptor_fails(self):
        broken = descriptor()
        broken["symbol"] = "ETHUSDT"
        with self.assertRaises(ContextFeaturePackError):
            build_context_feature_pack_v1(
                observation_descriptor=broken,
                components=unavailable_components(),
            )


if __name__ == "__main__":
    unittest.main(verbosity=2)
