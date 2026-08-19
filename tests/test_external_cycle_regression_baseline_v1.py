from __future__ import annotations

import hashlib
import json
import os
import tempfile
import unittest
from pathlib import Path

from src.context.external_cycle_regression_baseline_v1 import (
    CAPABILITY,
    FEATURE_ID,
    PACKAGE_AUTHORIZATION,
    SNAPSHOT_SCHEMA_VERSION,
    SOURCE_KIND,
    VALUE_UNIT,
    ExternalCycleRegressionBaselineError,
    build_external_cycle_regression_baseline_v1_component,
    prepare_external_cycle_regression_baseline_v1_package,
    validate_component_against_level_a_pack_v1,
    validate_external_cycle_regression_baseline_policy_v1,
    validate_external_cycle_regression_baseline_v1_component,
    validate_external_cycle_regression_baseline_v1_package,
    validate_external_cycle_regression_snapshot_v1,
)

POLICY_EFFECTIVE = "2026-08-19T00:40:00+00:00"
REFERENCE = "2026-08-19T01:00:00+00:00"

def descriptor(reference=REFERENCE, cutoff="2026-08-19T01:00:10+00:00"):
    return {
        "observation_descriptor_schema_version": "FORWARD_OUTCOME_OBSERVATION_DESCRIPTOR_V1",
        "observation_id": "OBS_EXTREG_001",
        "symbol": "BTCUSDT",
        "timeframe": "15m",
        "reference_boundary_utc": reference,
        "reference_closed_candle_utc": "2026-08-19T00:59:59.999000+00:00",
        "synchronized_context_available_at_utc": cutoff,
        "primary_candidate_detected": False,
    }

def policy():
    return {
        "schema_version": "EXTERNAL_CYCLE_REGRESSION_BASELINE_POLICY_V1",
        "feature_id": "EXTERNAL_CYCLE_REGRESSION_BASELINE_V1",
        "policy_effective_from_utc": POLICY_EFFECTIVE,
        "external_snapshot_schema_version": "EXTERNAL_CYCLE_REGRESSION_BASELINE_SNAPSHOT_V1",
        "value_unit": "USD_PER_BTC",
        "external_frozen_snapshot_required": True,
        "reference_time_exact_observation_boundary_required": True,
        "fit_sample_end_not_after_information_cutoff_required": True,
        "information_cutoff_not_after_model_generated_required": True,
        "model_generated_not_after_snapshot_created_required": True,
        "producer_model_fit_allowed": False,
        "producer_network_fetch_allowed": False,
        "producer_market_price_input_allowed": False,
        "producer_residual_calculation_allowed": False,
        "future_outcomes_used": False,
        "directional_meaning_assigned": False,
        "composite_score_assigned": False,
        "signal_semantics": False,
    }

def snapshot(
    reference=REFERENCE,
    info="2026-08-18T23:30:00+00:00",
    generated="2026-08-19T00:15:00+00:00",
    created="2026-08-19T00:30:00+00:00",
    interval=True,
):
    return {
        "snapshot_schema_version": "EXTERNAL_CYCLE_REGRESSION_BASELINE_SNAPSHOT_V1",
        "model_id": "EXAMPLE_EXTERNAL_CYCLE_REGRESSION",
        "model_version": "2026-08-19-v1",
        "model_family": "LOG_PRICE_TIME_REGRESSION",
        "source_name": "EXTERNAL_RESEARCH_SOURCE",
        "source_reference": "frozen-source-reference-001",
        "parameters_sha256": "a" * 64,
        "fit_sample_start_utc": "2015-01-01T00:00:00+00:00",
        "fit_sample_end_utc": "2026-08-18T23:00:00+00:00",
        "information_cutoff_utc": info,
        "model_generated_at_utc": generated,
        "snapshot_created_at_utc": created,
        "reference_time_utc": reference,
        "value_unit": "USD_PER_BTC",
        "baseline_estimate": 65000.0,
        "interval_available": interval,
        "interval_label": "EXTERNAL_SUPPLIED_REFERENCE_BAND",
        "lower_bound": 60000.0 if interval else None,
        "upper_bound": 70000.0 if interval else None,
    }

def component(desc=None, snap=None, produced="2026-08-19T00:40:01+00:00"):
    return build_external_cycle_regression_baseline_v1_component(
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
        (resources / "external_cycle_regression_baseline_policy_v1.json").write_text(
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
        self.assertEqual(VALUE_UNIT, "USD_PER_BTC")
        self.assertEqual(SNAPSHOT_SCHEMA_VERSION, "EXTERNAL_CYCLE_REGRESSION_BASELINE_SNAPSHOT_V1")

    def test_02_authorization(self):
        self.assertEqual(PACKAGE_AUTHORIZATION, "PREPARE_EXTERNAL_CYCLE_REGRESSION_BASELINE_V1")

    def test_03_policy_valid(self):
        self.assertEqual(validate_external_cycle_regression_baseline_policy_v1(policy())["policy_effective_from_utc"], POLICY_EFFECTIVE)

    def test_04_policy_network_forbidden(self):
        value = policy()
        value["producer_network_fetch_allowed"] = True
        with self.assertRaises(ExternalCycleRegressionBaselineError):
            validate_external_cycle_regression_baseline_policy_v1(value)

    def test_05_snapshot_valid(self):
        self.assertEqual(validate_external_cycle_regression_snapshot_v1(snapshot())["baseline_estimate"], 65000.0)

    def test_06_optional_interval(self):
        result = validate_external_cycle_regression_snapshot_v1(snapshot(interval=False))
        self.assertFalse(result["interval_available"])
        self.assertIsNone(result["lower_bound"])
        self.assertIsNone(result["upper_bound"])

    def test_07_interval_order_fails(self):
        value = snapshot()
        value["lower_bound"] = 66000.0
        with self.assertRaises(ExternalCycleRegressionBaselineError):
            validate_external_cycle_regression_snapshot_v1(value)

    def test_08_fit_after_info_fails(self):
        value = snapshot()
        value["fit_sample_end_utc"] = "2026-08-19T00:00:00+00:00"
        with self.assertRaises(ExternalCycleRegressionBaselineError):
            validate_external_cycle_regression_snapshot_v1(value)

    def test_09_info_after_generated_fails(self):
        with self.assertRaises(ExternalCycleRegressionBaselineError):
            validate_external_cycle_regression_snapshot_v1(
                snapshot(info="2026-08-19T00:20:00+00:00")
            )

    def test_10_generated_after_created_fails(self):
        with self.assertRaises(ExternalCycleRegressionBaselineError):
            validate_external_cycle_regression_snapshot_v1(
                snapshot(generated="2026-08-19T00:31:00+00:00")
            )

    def test_11_exact_reference_required(self):
        with self.assertRaises(ExternalCycleRegressionBaselineError):
            component(snap=snapshot(reference="2026-08-19T01:15:00+00:00"))

    def test_12_policy_floor_applied(self):
        result = component()
        self.assertEqual(result["available_at_utc"], POLICY_EFFECTIVE)
        self.assertTrue(result["payload"]["retrospective_policy_floor_applied"])

    def test_13_post_policy_available_at_snapshot(self):
        snap = snapshot(
            generated="2026-08-19T00:50:00+00:00",
            created="2026-08-19T00:55:00+00:00",
        )
        result = component(snap=snap, produced="2026-08-19T00:55:01+00:00")
        self.assertEqual(result["available_at_utc"], "2026-08-19T00:55:00+00:00")
        self.assertFalse(result["payload"]["retrospective_policy_floor_applied"])

    def test_14_old_snapshot_pack_ineligible(self):
        desc = descriptor(
            reference="2026-08-18T00:00:00+00:00",
            cutoff="2026-08-18T00:00:10+00:00",
        )
        snap = snapshot(
            reference="2026-08-18T00:00:00+00:00",
            info="2026-08-17T22:00:00+00:00",
            generated="2026-08-17T23:00:00+00:00",
            created="2026-08-17T23:30:00+00:00",
        )
        snap["fit_sample_end_utc"] = "2026-08-17T21:00:00+00:00"
        result = validate_component_against_level_a_pack_v1(
            observation_descriptor=desc,
            component=component(desc=desc, snap=snap),
        )
        self.assertFalse(result["point_in_time_eligible"])
        self.assertEqual(result["eligibility_reason"], "AVAILABLE_AFTER_CONTEXT_CUTOFF")

    def test_15_post_policy_pack_eligible(self):
        snap = snapshot(
            generated="2026-08-19T00:50:00+00:00",
            created="2026-08-19T00:55:00+00:00",
        )
        result = validate_component_against_level_a_pack_v1(
            observation_descriptor=descriptor(),
            component=component(snap=snap, produced="2026-08-19T00:55:01+00:00"),
        )
        self.assertTrue(result["point_in_time_eligible"])

    def test_16_no_fit_network_price_residual(self):
        payload = component()["payload"]
        self.assertFalse(payload["producer_model_fit_executed"])
        self.assertFalse(payload["producer_network_fetch_executed"])
        self.assertFalse(payload["producer_market_price_input_used"])
        self.assertFalse(payload["producer_residual_calculation_performed"])

    def test_17_no_direction_signal_score_outcomes(self):
        payload = component()["payload"]
        self.assertFalse(payload["directional_semantics"])
        self.assertFalse(payload["signal_semantics"])
        self.assertFalse(payload["composite_score_assigned"])
        self.assertFalse(payload["future_outcomes_used"])

    def test_18_component_validator(self):
        self.assertEqual(validate_external_cycle_regression_baseline_v1_component(component())["status"], "AVAILABLE")

    def _descriptor_file(self):
        path = self.external / "descriptor.json"
        path.write_text(json.dumps(descriptor(), sort_keys=True) + "\n", encoding="utf-8")
        return path

    def _snapshot_file(self, name="snapshot.json"):
        path = self.external / name
        path.write_text(json.dumps(snapshot(), sort_keys=True) + "\n", encoding="utf-8")
        return path

    def test_19_package_missing_auth_fails(self):
        with self.assertRaises(ExternalCycleRegressionBaselineError):
            prepare_external_cycle_regression_baseline_v1_package(
                repo_root=self.repo,
                observation_descriptor_json=self._descriptor_file(),
                external_snapshot_json=self._snapshot_file(),
                output_directory=self.external / "missing",
                produced_at_utc="2026-08-19T00:40:01+00:00",
                authorization=None,
            )

    def test_20_output_inside_repo_fails(self):
        with self.assertRaises(ExternalCycleRegressionBaselineError):
            prepare_external_cycle_regression_baseline_v1_package(
                repo_root=self.repo,
                observation_descriptor_json=self._descriptor_file(),
                external_snapshot_json=self._snapshot_file("inside.json"),
                output_directory=self.repo / "output",
                produced_at_utc="2026-08-19T00:40:01+00:00",
                authorization=PACKAGE_AUTHORIZATION,
            )

    def test_21_gate_enabled_fails(self):
        os.environ["TRADING_AI_OFFICIAL_LONG_EVIDENCE_APPEND_ALLOWED"] = "1"
        with self.assertRaises(ExternalCycleRegressionBaselineError):
            prepare_external_cycle_regression_baseline_v1_package(
                repo_root=self.repo,
                observation_descriptor_json=self._descriptor_file(),
                external_snapshot_json=self._snapshot_file("gate.json"),
                output_directory=self.external / "gate-output",
                produced_at_utc="2026-08-19T00:40:01+00:00",
                authorization=PACKAGE_AUTHORIZATION,
            )

    def test_22_package_roundtrip(self):
        output = self.external / "roundtrip"
        prepare_external_cycle_regression_baseline_v1_package(
            repo_root=self.repo,
            observation_descriptor_json=self._descriptor_file(),
            external_snapshot_json=self._snapshot_file("roundtrip.json"),
            output_directory=output,
            produced_at_utc="2026-08-19T00:40:01+00:00",
            authorization=PACKAGE_AUTHORIZATION,
        )
        result = validate_external_cycle_regression_baseline_v1_package(output)
        self.assertEqual(result["manifest_entries"], 2)

    def test_23_tamper_detected(self):
        output = self.external / "tamper"
        prepare_external_cycle_regression_baseline_v1_package(
            repo_root=self.repo,
            observation_descriptor_json=self._descriptor_file(),
            external_snapshot_json=self._snapshot_file("tamper.json"),
            output_directory=output,
            produced_at_utc="2026-08-19T00:40:01+00:00",
            authorization=PACKAGE_AUTHORIZATION,
        )
        with (output / "external_cycle_regression_baseline_component.json").open("ab") as handle:
            handle.write(b"x")
        with self.assertRaises(ExternalCycleRegressionBaselineError):
            validate_external_cycle_regression_baseline_v1_package(output)

    def test_24_official_and_source_unchanged(self):
        source = self._snapshot_file("unchanged.json")
        before_source = hashlib.sha256(source.read_bytes()).hexdigest()
        dataset = self.repo / "data" / "forward" / "long_forward_observation_dataset_v1.csv"
        manifest = self.repo / "data" / "forward" / "long_forward_observation_dataset_v1.manifest.csv"
        before_official = (dataset.read_bytes(), manifest.read_bytes())

        prepare_external_cycle_regression_baseline_v1_package(
            repo_root=self.repo,
            observation_descriptor_json=self._descriptor_file(),
            external_snapshot_json=source,
            output_directory=self.external / "unchanged-output",
            produced_at_utc="2026-08-19T00:40:01+00:00",
            authorization=PACKAGE_AUTHORIZATION,
        )

        self.assertEqual(hashlib.sha256(source.read_bytes()).hexdigest(), before_source)
        self.assertEqual((dataset.read_bytes(), manifest.read_bytes()), before_official)

if __name__ == "__main__":
    unittest.main(verbosity=2)
