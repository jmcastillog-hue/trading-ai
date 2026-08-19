from __future__ import annotations

import hashlib
import json
import os
import tempfile
import unittest
from pathlib import Path

from src.context.analog_engine_context_v1 import (
    CAPABILITY,
    FEATURE_ID,
    LIBRARY_SCHEMA_VERSION,
    PACKAGE_AUTHORIZATION,
    QUERY_SCHEMA_VERSION,
    SOURCE_KIND,
    AnalogEngineContextError,
    build_analog_engine_context_v1_component,
    prepare_analog_engine_context_v1_package,
    validate_analog_engine_context_policy_v1,
    validate_analog_engine_context_v1_component,
    validate_analog_engine_context_v1_package,
    validate_analog_query_vector_snapshot_v1,
    validate_analog_reference_library_snapshot_v1,
    validate_component_against_level_a_pack_v1,
)

POLICY_EFFECTIVE = "2026-08-19T01:30:00+00:00"
REFERENCE = "2026-08-19T01:45:00+00:00"

def descriptor(reference=REFERENCE, cutoff="2026-08-19T01:45:10+00:00"):
    return {
        "observation_descriptor_schema_version": "FORWARD_OUTCOME_OBSERVATION_DESCRIPTOR_V1",
        "observation_id": "QUERY_OBS_001",
        "symbol": "BTCUSDT",
        "timeframe": "15m",
        "reference_boundary_utc": reference,
        "reference_closed_candle_utc": "2026-08-19T01:44:59.999000+00:00",
        "synchronized_context_available_at_utc": cutoff,
        "primary_candidate_detected": False,
    }

def policy():
    return {
        "schema_version": "ANALOG_ENGINE_CONTEXT_POLICY_V1",
        "feature_id": "ANALOG_ENGINE_CONTEXT_V1",
        "policy_effective_from_utc": POLICY_EFFECTIVE,
        "query_snapshot_schema_version": "ANALOG_QUERY_VECTOR_SNAPSHOT_V1",
        "library_snapshot_schema_version": "ANALOG_REFERENCE_LIBRARY_SNAPSHOT_V1",
        "distance_metric": "EUCLIDEAN_PRESTANDARDIZED_VECTOR",
        "top_k": 5,
        "min_feature_count": 2,
        "max_feature_count": 32,
        "min_library_rows": 5,
        "max_library_rows": 10000,
        "exact_feature_space_match_required": True,
        "exact_query_observation_match_required": True,
        "historical_reference_strictly_before_query_required": True,
        "feature_information_cutoff_not_after_reference_required": True,
        "normalization_fit_cutoff_not_after_query_reference_required": True,
        "outcome_fields_allowed": False,
        "future_rows_allowed": False,
        "producer_network_fetch_allowed": False,
        "producer_model_training_allowed": False,
        "producer_market_data_fetch_allowed": False,
        "directional_meaning_assigned": False,
        "analog_vote_allowed": False,
        "composite_score_assigned": False,
        "signal_semantics": False,
        "future_outcomes_used": False,
    }

def query(created="2026-08-19T01:45:01+00:00"):
    return {
        "snapshot_schema_version": "ANALOG_QUERY_VECTOR_SNAPSHOT_V1",
        "observation_id": "QUERY_OBS_001",
        "reference_boundary_utc": REFERENCE,
        "feature_information_cutoff_utc": "2026-08-19T01:44:59+00:00",
        "snapshot_created_at_utc": created,
        "feature_space_sha256": "a" * 64,
        "feature_names": ["F1", "F2", "F3"],
        "vector": [0.0, 0.0, 0.0],
    }

def library(created="2026-08-19T01:25:00+00:00"):
    rows = []
    timestamps = [
        "2026-08-19T00:00:00+00:00",
        "2026-08-19T00:15:00+00:00",
        "2026-08-19T00:30:00+00:00",
        "2026-08-19T00:45:00+00:00",
        "2026-08-19T01:00:00+00:00",
        "2026-08-19T01:15:00+00:00",
    ]
    for i, ts in enumerate(timestamps, start=1):
        rows.append(
            {
                "observation_id": f"HIST_{i:02d}",
                "reference_boundary_utc": ts,
                "feature_information_cutoff_utc": ts,
                "vector": [float(i), 0.0, 0.0],
            }
        )
    return {
        "snapshot_schema_version": "ANALOG_REFERENCE_LIBRARY_SNAPSHOT_V1",
        "feature_space_sha256": "a" * 64,
        "feature_names": ["F1", "F2", "F3"],
        "snapshot_created_at_utc": created,
        "normalization_fit_information_cutoff_utc": "2026-08-18T23:59:00+00:00",
        "rows": rows,
    }

def component(desc=None, q=None, lib=None, produced="2026-08-19T01:45:02+00:00"):
    return build_analog_engine_context_v1_component(
        observation_descriptor=desc or descriptor(),
        query_snapshot=q or query(),
        query_snapshot_sha256="b" * 64,
        library_snapshot=lib or library(),
        library_snapshot_sha256="c" * 64,
        policy=policy(),
        policy_sha256="d" * 64,
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
        (resources / "analog_engine_context_policy_v1.json").write_text(
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
        self.assertEqual(SOURCE_KIND, "MODEL_DERIVED")
        self.assertEqual(QUERY_SCHEMA_VERSION, "ANALOG_QUERY_VECTOR_SNAPSHOT_V1")
        self.assertEqual(LIBRARY_SCHEMA_VERSION, "ANALOG_REFERENCE_LIBRARY_SNAPSHOT_V1")

    def test_02_authorization(self):
        self.assertEqual(PACKAGE_AUTHORIZATION, "PREPARE_ANALOG_ENGINE_CONTEXT_V1")

    def test_03_policy_valid(self):
        result = validate_analog_engine_context_policy_v1(policy())
        self.assertEqual(result["top_k"], 5)
        self.assertEqual(result["policy_effective_from_utc"], POLICY_EFFECTIVE)

    def test_04_policy_vote_forbidden(self):
        value = policy()
        value["analog_vote_allowed"] = True
        with self.assertRaises(AnalogEngineContextError):
            validate_analog_engine_context_policy_v1(value)

    def test_05_query_valid(self):
        p = validate_analog_engine_context_policy_v1(policy())
        self.assertEqual(len(validate_analog_query_vector_snapshot_v1(query(), policy=p)["vector"]), 3)

    def test_06_query_outcome_field_fails(self):
        value = query()
        value["future_outcome"] = 1
        with self.assertRaises(AnalogEngineContextError):
            validate_analog_query_vector_snapshot_v1(
                value,
                policy=validate_analog_engine_context_policy_v1(policy()),
            )

    def test_07_library_valid(self):
        p = validate_analog_engine_context_policy_v1(policy())
        self.assertEqual(len(validate_analog_reference_library_snapshot_v1(library(), policy=p)["rows"]), 6)

    def test_08_library_outcome_field_fails(self):
        value = library()
        value["rows"][0]["forward_return"] = 0.1
        with self.assertRaises(AnalogEngineContextError):
            validate_analog_reference_library_snapshot_v1(
                value,
                policy=validate_analog_engine_context_policy_v1(policy()),
            )

    def test_09_library_order_required(self):
        value = library()
        value["rows"][0], value["rows"][1] = value["rows"][1], value["rows"][0]
        with self.assertRaises(AnalogEngineContextError):
            validate_analog_reference_library_snapshot_v1(
                value,
                policy=validate_analog_engine_context_policy_v1(policy()),
            )

    def test_10_query_snapshot_creation_must_cover_information(self):
        value = query(created="2026-08-19T01:00:00+00:00")
        with self.assertRaises(AnalogEngineContextError):
            validate_analog_query_vector_snapshot_v1(
                value,
                policy=validate_analog_engine_context_policy_v1(policy()),
            )

    def test_11_library_snapshot_creation_must_cover_rows(self):
        value = library(created="2026-08-19T00:30:00+00:00")
        with self.assertRaises(AnalogEngineContextError):
            validate_analog_reference_library_snapshot_v1(
                value,
                policy=validate_analog_engine_context_policy_v1(policy()),
            )

    def test_12_normalization_fit_must_not_postdate_library_snapshot(self):
        value = library(created="2026-08-18T23:30:00+00:00")
        value["normalization_fit_information_cutoff_utc"] = "2026-08-18T23:45:00+00:00"
        for i, row in enumerate(value["rows"]):
            ts = f"2026-08-18T2{i}:00:00+00:00"
            if i > 3:
                ts = f"2026-08-18T23:{(i-4)*10:02d}:00+00:00"
            row["reference_boundary_utc"] = ts
            row["feature_information_cutoff_utc"] = ts
        value["rows"] = sorted(
            value["rows"],
            key=lambda row: (row["reference_boundary_utc"], row["observation_id"]),
        )
        with self.assertRaises(AnalogEngineContextError):
            validate_analog_reference_library_snapshot_v1(
                value,
                policy=validate_analog_engine_context_policy_v1(policy()),
            )

    def test_13_feature_space_must_match(self):
        value = library()
        value["feature_space_sha256"] = "e" * 64
        with self.assertRaises(AnalogEngineContextError):
            component(lib=value)

    def test_14_feature_names_must_match(self):
        value = library()
        value["feature_names"] = ["F1", "F2", "OTHER"]
        with self.assertRaises(AnalogEngineContextError):
            component(lib=value)

    def test_15_query_identity_must_match(self):
        value = query()
        value["observation_id"] = "OTHER"
        with self.assertRaises(AnalogEngineContextError):
            component(q=value)

    def test_16_future_library_row_fails(self):
        value = library()
        value["rows"][-1]["reference_boundary_utc"] = "2026-08-19T02:00:00+00:00"
        value["rows"][-1]["feature_information_cutoff_utc"] = "2026-08-19T02:00:00+00:00"
        with self.assertRaises(AnalogEngineContextError):
            component(lib=value)

    def test_17_normalization_future_fit_fails(self):
        value = library()
        value["normalization_fit_information_cutoff_utc"] = "2026-08-19T02:00:00+00:00"
        with self.assertRaises(AnalogEngineContextError):
            component(lib=value)

    def test_18_deterministic_nearest_five(self):
        result = component()
        ids = [x["observation_id"] for x in result["payload"]["selected_analogs"]]
        self.assertEqual(ids, ["HIST_01", "HIST_02", "HIST_03", "HIST_04", "HIST_05"])

    def test_19_available_not_before_information(self):
        result = component()
        self.assertGreaterEqual(result["available_at_utc"], result["information_cutoff_utc"])

    def test_20_no_training_network_market_or_outcomes(self):
        payload = component()["payload"]
        self.assertFalse(payload["producer_model_training_executed"])
        self.assertFalse(payload["producer_network_fetch_executed"])
        self.assertFalse(payload["producer_market_data_fetch_executed"])
        self.assertFalse(payload["future_outcomes_used"])
        self.assertFalse(payload["analog_vote_performed"])

    def test_21_component_validator(self):
        self.assertEqual(validate_analog_engine_context_v1_component(component())["analog_count"], 5)

    def test_22_old_snapshots_pack_ineligible_due_policy_floor(self):
        desc = descriptor(
            reference="2026-08-19T01:00:00+00:00",
            cutoff="2026-08-19T01:00:10+00:00",
        )
        q = query(created="2026-08-19T01:00:00+00:00")
        q["reference_boundary_utc"] = "2026-08-19T01:00:00+00:00"
        q["feature_information_cutoff_utc"] = "2026-08-19T00:59:59+00:00"

        lib = library(created="2026-08-19T00:50:00+00:00")
        old_times = [
            "2026-08-18T22:00:00+00:00",
            "2026-08-18T22:15:00+00:00",
            "2026-08-18T22:30:00+00:00",
            "2026-08-18T22:45:00+00:00",
            "2026-08-18T23:00:00+00:00",
            "2026-08-18T23:15:00+00:00",
        ]
        for row, ts in zip(lib["rows"], old_times):
            row["reference_boundary_utc"] = ts
            row["feature_information_cutoff_utc"] = ts
        lib["normalization_fit_information_cutoff_utc"] = "2026-08-18T21:59:00+00:00"

        result = validate_component_against_level_a_pack_v1(
            observation_descriptor=desc,
            component=component(
                desc=desc,
                q=q,
                lib=lib,
                produced="2026-08-19T01:30:01+00:00",
            ),
        )
        self.assertFalse(result["point_in_time_eligible"])
        self.assertEqual(result["eligibility_reason"], "AVAILABLE_AFTER_CONTEXT_CUTOFF")

    def test_23_post_policy_pack_eligible(self):
        result = validate_component_against_level_a_pack_v1(
            observation_descriptor=descriptor(),
            component=component(),
        )
        self.assertTrue(result["point_in_time_eligible"])

    def _write(self, name, value):
        path = self.external / name
        path.write_text(json.dumps(value, sort_keys=True) + "\n", encoding="utf-8")
        return path

    def test_24_missing_auth_fails(self):
        with self.assertRaises(AnalogEngineContextError):
            prepare_analog_engine_context_v1_package(
                repo_root=self.repo,
                observation_descriptor_json=self._write("descriptor.json", descriptor()),
                query_snapshot_json=self._write("query.json", query()),
                library_snapshot_json=self._write("library.json", library()),
                output_directory=self.external / "missing",
                produced_at_utc="2026-08-19T01:45:02+00:00",
                authorization=None,
            )

    def test_25_output_inside_repo_fails(self):
        with self.assertRaises(AnalogEngineContextError):
            prepare_analog_engine_context_v1_package(
                repo_root=self.repo,
                observation_descriptor_json=self._write("descriptor2.json", descriptor()),
                query_snapshot_json=self._write("query2.json", query()),
                library_snapshot_json=self._write("library2.json", library()),
                output_directory=self.repo / "output",
                produced_at_utc="2026-08-19T01:45:02+00:00",
                authorization=PACKAGE_AUTHORIZATION,
            )

    def test_26_gate_enabled_fails(self):
        os.environ["TRADING_AI_OFFICIAL_LONG_EVIDENCE_APPEND_ALLOWED"] = "1"
        with self.assertRaises(AnalogEngineContextError):
            prepare_analog_engine_context_v1_package(
                repo_root=self.repo,
                observation_descriptor_json=self._write("descriptor3.json", descriptor()),
                query_snapshot_json=self._write("query3.json", query()),
                library_snapshot_json=self._write("library3.json", library()),
                output_directory=self.external / "gate",
                produced_at_utc="2026-08-19T01:45:02+00:00",
                authorization=PACKAGE_AUTHORIZATION,
            )

    def test_27_roundtrip_tamper_and_immutability(self):
        descriptor_path = self._write("descriptor4.json", descriptor())
        query_path = self._write("query4.json", query())
        library_path = self._write("library4.json", library())
        before_query = hashlib.sha256(query_path.read_bytes()).hexdigest()
        before_library = hashlib.sha256(library_path.read_bytes()).hexdigest()

        dataset = self.repo / "data" / "forward" / "long_forward_observation_dataset_v1.csv"
        official_manifest = self.repo / "data" / "forward" / "long_forward_observation_dataset_v1.manifest.csv"
        official_before = (dataset.read_bytes(), official_manifest.read_bytes())

        output = self.external / "roundtrip"
        prepare_analog_engine_context_v1_package(
            repo_root=self.repo,
            observation_descriptor_json=descriptor_path,
            query_snapshot_json=query_path,
            library_snapshot_json=library_path,
            output_directory=output,
            produced_at_utc="2026-08-19T01:45:02+00:00",
            authorization=PACKAGE_AUTHORIZATION,
        )

        result = validate_analog_engine_context_v1_package(output)
        self.assertEqual(result["manifest_entries"], 2)
        self.assertEqual(hashlib.sha256(query_path.read_bytes()).hexdigest(), before_query)
        self.assertEqual(hashlib.sha256(library_path.read_bytes()).hexdigest(), before_library)
        self.assertEqual((dataset.read_bytes(), official_manifest.read_bytes()), official_before)

        with (output / "analog_engine_context_component.json").open("ab") as handle:
            handle.write(b"x")
        with self.assertRaises(AnalogEngineContextError):
            validate_analog_engine_context_v1_package(output)

if __name__ == "__main__":
    unittest.main(verbosity=2)
