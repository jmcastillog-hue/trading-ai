from __future__ import annotations

import hashlib
import json
import os
import tempfile
import unittest
from pathlib import Path

from src.context.external_thesis_model_card_v1 import (
    CAPABILITY,
    FEATURE_ID,
    PACKAGE_AUTHORIZATION,
    SNAPSHOT_SCHEMA_VERSION,
    SOURCE_KIND,
    ExternalThesisModelCardError,
    build_external_thesis_model_card_v1_component,
    prepare_external_thesis_model_card_v1_package,
    validate_component_against_level_a_pack_v1,
    validate_external_thesis_model_card_policy_v1,
    validate_external_thesis_model_card_snapshot_v1,
    validate_external_thesis_model_card_v1_component,
    validate_external_thesis_model_card_v1_package,
)

POLICY_EFFECTIVE = "2026-08-19T01:02:00+00:00"
REFERENCE = "2026-08-19T01:15:00+00:00"

def descriptor(reference=REFERENCE, cutoff="2026-08-19T01:15:10+00:00"):
    return {
        "observation_descriptor_schema_version": "FORWARD_OUTCOME_OBSERVATION_DESCRIPTOR_V1",
        "observation_id": "OBS_THESIS_001",
        "symbol": "BTCUSDT",
        "timeframe": "15m",
        "reference_boundary_utc": reference,
        "reference_closed_candle_utc": "2026-08-19T01:14:59.999000+00:00",
        "synchronized_context_available_at_utc": cutoff,
        "primary_candidate_detected": False,
    }

def policy():
    return {
        "schema_version": "EXTERNAL_THESIS_MODEL_CARD_POLICY_V1",
        "feature_id": "EXTERNAL_THESIS_MODEL_CARD_V1",
        "policy_effective_from_utc": POLICY_EFFECTIVE,
        "external_snapshot_schema_version": "EXTERNAL_THESIS_MODEL_CARD_SNAPSHOT_V1",
        "external_frozen_snapshot_required": True,
        "reference_inside_declared_applicability_required": True,
        "source_published_not_after_information_cutoff_required": True,
        "information_cutoff_not_after_thesis_generated_required": True,
        "thesis_generated_not_after_snapshot_created_required": True,
        "opaque_state_code_required": True,
        "text_claims_ingested": False,
        "target_prices_ingested": False,
        "confidence_scores_ingested": False,
        "producer_network_fetch_allowed": False,
        "producer_model_execution_allowed": False,
        "future_outcomes_used": False,
        "directional_meaning_assigned": False,
        "composite_score_assigned": False,
        "signal_semantics": False,
    }

def snapshot(
    published="2026-08-18T22:00:00+00:00",
    info="2026-08-18T23:00:00+00:00",
    generated="2026-08-19T00:00:00+00:00",
    created="2026-08-19T00:30:00+00:00",
    start="2026-08-19T00:00:00+00:00",
    end="2026-08-20T00:00:00+00:00",
):
    return {
        "snapshot_schema_version": "EXTERNAL_THESIS_MODEL_CARD_SNAPSHOT_V1",
        "thesis_id": "EXAMPLE_EXTERNAL_THESIS",
        "thesis_version": "2026-08-19-v1",
        "source_name": "EXTERNAL_RESEARCH_SOURCE",
        "source_reference": "frozen-source-reference-001",
        "thesis_content_sha256": "a" * 64,
        "method_family": "CYCLE",
        "horizon_label": "CYCLE",
        "state_code": "SOURCE_STATE_01",
        "source_published_at_utc": published,
        "information_cutoff_utc": info,
        "thesis_generated_at_utc": generated,
        "snapshot_created_at_utc": created,
        "applicability_start_utc": start,
        "applicability_end_utc": end,
    }

def component(desc=None, snap=None, produced="2026-08-19T01:02:01+00:00"):
    return build_external_thesis_model_card_v1_component(
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
        (official / "long_forward_observation_dataset_v1.csv").write_text("header\n", encoding="utf-8")
        (official / "long_forward_observation_dataset_v1.manifest.csv").write_text("manifest\n", encoding="utf-8")
        resources = self.repo / "src" / "context" / "resources"
        resources.mkdir(parents=True)
        (resources / "external_thesis_model_card_policy_v1.json").write_text(
            json.dumps(policy(), sort_keys=True, indent=2) + "\n",
            encoding="utf-8",
        )
        self.external = root / "external"
        self.external.mkdir()
        os.environ.pop("TRADING_AI_OFFICIAL_LONG_EVIDENCE_APPEND_ALLOWED", None)

    def tearDown(self):
        os.environ.pop("TRADING_AI_OFFICIAL_LONG_EVIDENCE_APPEND_ALLOWED", None)
        self.tmp.cleanup()

    def test_01_identity(self):
        self.assertEqual(CAPABILITY, FEATURE_ID)
        self.assertEqual(SOURCE_KIND, "EXTERNAL_MODEL")
        self.assertEqual(SNAPSHOT_SCHEMA_VERSION, "EXTERNAL_THESIS_MODEL_CARD_SNAPSHOT_V1")

    def test_02_authorization(self):
        self.assertEqual(PACKAGE_AUTHORIZATION, "PREPARE_EXTERNAL_THESIS_MODEL_CARD_V1")

    def test_03_policy_valid(self):
        self.assertEqual(validate_external_thesis_model_card_policy_v1(policy())["policy_effective_from_utc"], POLICY_EFFECTIVE)

    def test_04_policy_network_forbidden(self):
        value = policy()
        value["producer_network_fetch_allowed"] = True
        with self.assertRaises(ExternalThesisModelCardError):
            validate_external_thesis_model_card_policy_v1(value)

    def test_05_snapshot_valid(self):
        result = validate_external_thesis_model_card_snapshot_v1(snapshot())
        self.assertEqual(result["state_code"], "SOURCE_STATE_01")

    def test_06_bad_time_order_fails(self):
        with self.assertRaises(ExternalThesisModelCardError):
            validate_external_thesis_model_card_snapshot_v1(
                snapshot(info="2026-08-18T21:00:00+00:00")
            )

    def test_07_bad_state_code_fails(self):
        value = snapshot()
        value["state_code"] = "bullish state"
        with self.assertRaises(ExternalThesisModelCardError):
            validate_external_thesis_model_card_snapshot_v1(value)

    def test_08_bad_method_family_fails(self):
        value = snapshot()
        value["method_family"] = "UNKNOWN_FAMILY"
        with self.assertRaises(ExternalThesisModelCardError):
            validate_external_thesis_model_card_snapshot_v1(value)

    def test_09_bad_horizon_fails(self):
        value = snapshot()
        value["horizon_label"] = "FOREVER"
        with self.assertRaises(ExternalThesisModelCardError):
            validate_external_thesis_model_card_snapshot_v1(value)

    def test_10_reference_before_start_fails(self):
        with self.assertRaises(ExternalThesisModelCardError):
            component(snap=snapshot(start="2026-08-19T01:30:00+00:00"))

    def test_11_reference_after_end_fails(self):
        with self.assertRaises(ExternalThesisModelCardError):
            component(snap=snapshot(end="2026-08-19T01:00:00+00:00"))

    def test_12_open_ended_applicability_passes(self):
        value = snapshot()
        value["applicability_end_utc"] = None
        self.assertEqual(component(snap=value)["status"], "AVAILABLE")

    def test_13_policy_floor_applied(self):
        result = component()
        self.assertEqual(result["available_at_utc"], POLICY_EFFECTIVE)
        self.assertTrue(result["payload"]["retrospective_policy_floor_applied"])

    def test_14_post_policy_available_at_snapshot(self):
        value = snapshot(
            generated="2026-08-19T01:05:00+00:00",
            created="2026-08-19T01:10:00+00:00",
        )
        result = component(snap=value, produced="2026-08-19T01:10:01+00:00")
        self.assertEqual(result["available_at_utc"], "2026-08-19T01:10:00+00:00")

    def test_15_old_snapshot_pack_ineligible(self):
        desc = descriptor(
            reference="2026-08-18T23:30:00+00:00",
            cutoff="2026-08-18T23:30:10+00:00",
        )
        value = snapshot(
            published="2026-08-18T20:00:00+00:00",
            info="2026-08-18T21:00:00+00:00",
            generated="2026-08-18T22:00:00+00:00",
            created="2026-08-18T22:30:00+00:00",
            start="2026-08-18T22:00:00+00:00",
            end="2026-08-19T00:00:00+00:00",
        )
        result = validate_component_against_level_a_pack_v1(
            observation_descriptor=desc,
            component=component(desc=desc, snap=value),
        )
        self.assertFalse(result["point_in_time_eligible"])
        self.assertEqual(result["eligibility_reason"], "AVAILABLE_AFTER_CONTEXT_CUTOFF")

    def test_16_post_policy_pack_eligible(self):
        value = snapshot(
            generated="2026-08-19T01:05:00+00:00",
            created="2026-08-19T01:10:00+00:00",
        )
        result = validate_component_against_level_a_pack_v1(
            observation_descriptor=descriptor(),
            component=component(snap=value, produced="2026-08-19T01:10:01+00:00"),
        )
        self.assertTrue(result["point_in_time_eligible"])

    def test_17_no_model_execution_network_or_market(self):
        p = component()["payload"]
        self.assertFalse(p["producer_model_execution_executed"])
        self.assertFalse(p["producer_network_fetch_executed"])
        self.assertFalse(p["market_data_input_used"])

    def test_18_no_text_targets_confidence(self):
        p = component()["payload"]
        self.assertFalse(p["text_claims_ingested"])
        self.assertFalse(p["target_prices_ingested"])
        self.assertFalse(p["confidence_scores_ingested"])

    def test_19_no_direction_signal_score_outcomes(self):
        p = component()["payload"]
        self.assertFalse(p["directional_semantics"])
        self.assertFalse(p["signal_semantics"])
        self.assertFalse(p["composite_score_assigned"])
        self.assertFalse(p["future_outcomes_used"])

    def test_20_component_validator(self):
        self.assertEqual(validate_external_thesis_model_card_v1_component(component())["status"], "AVAILABLE")

    def _descriptor_file(self):
        path = self.external / "descriptor.json"
        path.write_text(json.dumps(descriptor(), sort_keys=True) + "\n", encoding="utf-8")
        return path

    def _snapshot_file(self, name="snapshot.json"):
        path = self.external / name
        path.write_text(json.dumps(snapshot(), sort_keys=True) + "\n", encoding="utf-8")
        return path

    def test_21_missing_auth_fails(self):
        with self.assertRaises(ExternalThesisModelCardError):
            prepare_external_thesis_model_card_v1_package(
                repo_root=self.repo,
                observation_descriptor_json=self._descriptor_file(),
                external_snapshot_json=self._snapshot_file(),
                output_directory=self.external / "missing",
                produced_at_utc="2026-08-19T01:02:01+00:00",
                authorization=None,
            )

    def test_22_output_inside_repo_fails(self):
        with self.assertRaises(ExternalThesisModelCardError):
            prepare_external_thesis_model_card_v1_package(
                repo_root=self.repo,
                observation_descriptor_json=self._descriptor_file(),
                external_snapshot_json=self._snapshot_file("inside.json"),
                output_directory=self.repo / "output",
                produced_at_utc="2026-08-19T01:02:01+00:00",
                authorization=PACKAGE_AUTHORIZATION,
            )

    def test_23_gate_enabled_fails(self):
        os.environ["TRADING_AI_OFFICIAL_LONG_EVIDENCE_APPEND_ALLOWED"] = "1"
        with self.assertRaises(ExternalThesisModelCardError):
            prepare_external_thesis_model_card_v1_package(
                repo_root=self.repo,
                observation_descriptor_json=self._descriptor_file(),
                external_snapshot_json=self._snapshot_file("gate.json"),
                output_directory=self.external / "gate-output",
                produced_at_utc="2026-08-19T01:02:01+00:00",
                authorization=PACKAGE_AUTHORIZATION,
            )

    def test_24_roundtrip_tamper_and_immutability(self):
        snapshot_path = self._snapshot_file("roundtrip.json")
        snapshot_before = hashlib.sha256(snapshot_path.read_bytes()).hexdigest()
        dataset = self.repo / "data" / "forward" / "long_forward_observation_dataset_v1.csv"
        official_manifest = self.repo / "data" / "forward" / "long_forward_observation_dataset_v1.manifest.csv"
        official_before = (dataset.read_bytes(), official_manifest.read_bytes())

        output = self.external / "roundtrip"
        prepare_external_thesis_model_card_v1_package(
            repo_root=self.repo,
            observation_descriptor_json=self._descriptor_file(),
            external_snapshot_json=snapshot_path,
            output_directory=output,
            produced_at_utc="2026-08-19T01:02:01+00:00",
            authorization=PACKAGE_AUTHORIZATION,
        )
        result = validate_external_thesis_model_card_v1_package(output)
        self.assertEqual(result["manifest_entries"], 2)
        self.assertEqual(hashlib.sha256(snapshot_path.read_bytes()).hexdigest(), snapshot_before)
        self.assertEqual((dataset.read_bytes(), official_manifest.read_bytes()), official_before)

        with (output / "external_thesis_model_card_component.json").open("ab") as handle:
            handle.write(b"x")
        with self.assertRaises(ExternalThesisModelCardError):
            validate_external_thesis_model_card_v1_package(output)

if __name__ == "__main__":
    unittest.main(verbosity=2)
