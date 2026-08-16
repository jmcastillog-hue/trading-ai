from __future__ import annotations

import copy
import json
import os
import tempfile
import unittest
from pathlib import Path

from src.context.btc_cycle_halving_context_v1 import (
    CAPABILITY,
    FEATURE_ID,
    PACKAGE_AUTHORIZATION,
    SOURCE_KIND,
    BtcCycleHalvingContextError,
    build_btc_cycle_halving_context_v1_component,
    load_halving_calendar_v1,
    prepare_btc_cycle_halving_context_v1_package,
    validate_btc_cycle_halving_context_v1_component,
    validate_btc_cycle_halving_context_v1_package,
    validate_component_against_level_a_pack_v1,
    validate_halving_calendar_v1,
)


def descriptor(
    *,
    reference="2026-08-10T23:45:00+00:00",
    cutoff="2026-08-10T23:45:12.139898+00:00",
    candidate=False,
):
    return {
        "observation_descriptor_schema_version":
            "FORWARD_OUTCOME_OBSERVATION_DESCRIPTOR_V1",
        "observation_id": "OBS_CYCLE_001",
        "symbol": "BTCUSDT",
        "timeframe": "15m",
        "reference_boundary_utc": reference,
        "synchronized_context_available_at_utc": cutoff,
        "primary_candidate_detected": candidate,
    }


def calendar_fixture():
    return {
        "schema_version": "BTC_CYCLE_HALVING_CALENDAR_V1",
        "time_basis":
            "UTC_CALENDAR_DAY_START_REFERENCE_NOT_BLOCK_TIMESTAMP",
        "calendar_dates_are_reference_days_not_block_timestamps":
            True,
        "protocol_halving_interval_blocks": 210000,
        "genesis_block_subsidy_btc": "50",
        "historical_halvings": [
            {
                "halving_index": 1,
                "block_height": 210000,
                "calendar_date_utc": "2012-11-28",
                "post_halving_subsidy_btc": "25",
            },
            {
                "halving_index": 2,
                "block_height": 420000,
                "calendar_date_utc": "2016-07-09",
                "post_halving_subsidy_btc": "12.5",
            },
            {
                "halving_index": 3,
                "block_height": 630000,
                "calendar_date_utc": "2020-05-11",
                "post_halving_subsidy_btc": "6.25",
            },
            {
                "halving_index": 4,
                "block_height": 840000,
                "calendar_date_utc": "2024-04-20",
                "post_halving_subsidy_btc": "3.125",
            },
        ],
        "next_protocol_halving_block_height_after_latest_record":
            1050000,
        "future_halving_time_estimated": False,
    }


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

        resource_dir = (
            self.repo / "src" / "context" / "resources"
        )
        resource_dir.mkdir(parents=True)
        (
            resource_dir / "btc_cycle_halving_calendar_v1.json"
        ).write_text(
            json.dumps(
                calendar_fixture(),
                sort_keys=True,
                indent=2,
            )
            + "\n",
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

    def test_01_capability(self):
        self.assertEqual(
            CAPABILITY,
            "BTC_CYCLE_HALVING_CONTEXT_V1",
        )

    def test_02_feature_id(self):
        self.assertEqual(
            FEATURE_ID,
            "BTC_CYCLE_HALVING_CONTEXT_V1",
        )

    def test_03_source_kind(self):
        self.assertEqual(SOURCE_KIND, "DETERMINISTIC")

    def test_04_authorization_exact(self):
        self.assertEqual(
            PACKAGE_AUTHORIZATION,
            "PREPARE_BTC_CYCLE_HALVING_CONTEXT_V1",
        )

    def test_05_calendar_valid(self):
        result = validate_halving_calendar_v1(
            calendar_fixture()
        )
        self.assertEqual(
            result["historical_halving_count"],
            4,
        )
        self.assertEqual(
            result["latest_halving_block_height"],
            840000,
        )

    def test_06_calendar_interval_must_be_210000(self):
        value = calendar_fixture()
        value["protocol_halving_interval_blocks"] = 1
        with self.assertRaises(BtcCycleHalvingContextError):
            validate_halving_calendar_v1(value)

    def test_07_calendar_height_sequence(self):
        value = calendar_fixture()
        value["historical_halvings"][2]["block_height"] = 1
        with self.assertRaises(BtcCycleHalvingContextError):
            validate_halving_calendar_v1(value)

    def test_08_calendar_dates_exact(self):
        value = calendar_fixture()
        value["historical_halvings"][3][
            "calendar_date_utc"
        ] = "2024-04-19"
        with self.assertRaises(BtcCycleHalvingContextError):
            validate_halving_calendar_v1(value)

    def test_09_future_halving_time_estimate_forbidden(self):
        value = calendar_fixture()
        value["future_halving_time_estimated"] = True
        with self.assertRaises(BtcCycleHalvingContextError):
            validate_halving_calendar_v1(value)

    def _component(
        self,
        *,
        desc=None,
        produced="2026-08-10T23:45:10+00:00",
    ):
        return build_btc_cycle_halving_context_v1_component(
            observation_descriptor=desc or descriptor(),
            halving_calendar=calendar_fixture(),
            calendar_sha256="a" * 64,
            produced_at_utc=produced,
        )

    def test_10_current_component_available(self):
        component = self._component()
        self.assertEqual(component["status"], "AVAILABLE")

    def test_11_current_halving_index_4(self):
        component = self._component()
        self.assertEqual(
            component["payload"]["halving_index"],
            4,
        )

    def test_12_current_halving_height_840000(self):
        component = self._component()
        self.assertEqual(
            component["payload"]["halving_block_height"],
            840000,
        )

    def test_13_days_since_2024_halving_reference(self):
        component = self._component()
        self.assertEqual(
            component["payload"][
                "days_since_halving_reference"
            ],
            842,
        )

    def test_14_previous_cycle_length_1440_days(self):
        component = self._component()
        self.assertEqual(
            component["payload"][
                "previous_completed_cycle_length_days"
            ],
            1440,
        )

    def test_15_current_cycle_quartile_q3(self):
        component = self._component()
        self.assertEqual(
            component["payload"][
                "cycle_quartile_vs_previous_completed_cycle_length"
            ],
            "Q3",
        )

    def test_16_no_future_halving_time_estimate(self):
        payload = self._component()["payload"]
        self.assertFalse(
            payload["next_halving_time_estimated"]
        )
        self.assertIsNone(
            payload["estimated_next_halving_utc"]
        )
        self.assertIsNone(
            payload["days_to_next_halving_estimate"]
        )

    def test_17_no_price_market_or_outcome_inputs(self):
        payload = self._component()["payload"]
        self.assertFalse(payload["price_input_used"])
        self.assertFalse(payload["market_data_input_used"])
        self.assertFalse(payload["future_outcomes_used"])

    def test_18_no_direction_or_signal_semantics(self):
        payload = self._component()["payload"]
        self.assertFalse(payload["directional_semantics"])
        self.assertFalse(payload["signal_semantics"])

    def test_19_pre_first_halving_is_unavailable(self):
        component = self._component(
            desc=descriptor(
                reference="2012-01-01T00:00:00+00:00",
                cutoff="2012-01-01T00:00:01+00:00",
            ),
            produced="2012-01-01T00:00:00+00:00",
        )
        self.assertEqual(
            component["status"],
            "UNAVAILABLE",
        )
        self.assertIsNone(component["payload"])

    def test_20_produced_before_reference_fails(self):
        with self.assertRaises(BtcCycleHalvingContextError):
            self._component(
                produced="2026-08-10T23:44:59+00:00"
            )

    def test_21_pack_compatible_before_cutoff(self):
        component = self._component()
        result = validate_component_against_level_a_pack_v1(
            observation_descriptor=descriptor(),
            component=component,
        )
        self.assertTrue(result["point_in_time_eligible"])
        self.assertEqual(
            result["eligibility_reason"],
            "POINT_IN_TIME_ELIGIBLE",
        )

    def test_22_pack_marks_late_producer_ineligible(self):
        component = self._component(
            produced="2026-08-10T23:46:00+00:00"
        )
        result = validate_component_against_level_a_pack_v1(
            observation_descriptor=descriptor(),
            component=component,
        )
        self.assertFalse(result["point_in_time_eligible"])
        self.assertEqual(
            result["eligibility_reason"],
            "AVAILABLE_AFTER_CONTEXT_CUTOFF",
        )

    def test_23_inputs_not_mutated(self):
        desc = descriptor()
        cal = calendar_fixture()
        desc_before = copy.deepcopy(desc)
        cal_before = copy.deepcopy(cal)
        build_btc_cycle_halving_context_v1_component(
            observation_descriptor=desc,
            halving_calendar=cal,
            calendar_sha256="a" * 64,
            produced_at_utc="2026-08-10T23:45:10+00:00",
        )
        self.assertEqual(desc, desc_before)
        self.assertEqual(cal, cal_before)

    def test_24_component_validator(self):
        result = (
            validate_btc_cycle_halving_context_v1_component(
                self._component()
            )
        )
        self.assertEqual(result["halving_index"], 4)

    def _descriptor_file(self):
        path = self.external / "descriptor.json"
        path.write_text(
            json.dumps(descriptor(), sort_keys=True) + "\n",
            encoding="utf-8",
        )
        return path

    def test_25_package_missing_auth_fails(self):
        with self.assertRaises(BtcCycleHalvingContextError):
            prepare_btc_cycle_halving_context_v1_package(
                repo_root=self.repo,
                observation_descriptor_json=self._descriptor_file(),
                output_directory=self.external / "missing-auth",
                produced_at_utc="2026-08-10T23:45:10+00:00",
                authorization=None,
            )

    def test_26_package_output_inside_repo_fails(self):
        with self.assertRaises(BtcCycleHalvingContextError):
            prepare_btc_cycle_halving_context_v1_package(
                repo_root=self.repo,
                observation_descriptor_json=self._descriptor_file(),
                output_directory=self.repo / "package",
                produced_at_utc="2026-08-10T23:45:10+00:00",
                authorization=PACKAGE_AUTHORIZATION,
            )

    def test_27_package_existing_output_fails(self):
        output = self.external / "existing"
        output.mkdir()
        with self.assertRaises(BtcCycleHalvingContextError):
            prepare_btc_cycle_halving_context_v1_package(
                repo_root=self.repo,
                observation_descriptor_json=self._descriptor_file(),
                output_directory=output,
                produced_at_utc="2026-08-10T23:45:10+00:00",
                authorization=PACKAGE_AUTHORIZATION,
            )

    def test_28_gate_enabled_fails(self):
        os.environ[
            "TRADING_AI_OFFICIAL_LONG_EVIDENCE_APPEND_ALLOWED"
        ] = "1"
        with self.assertRaises(BtcCycleHalvingContextError):
            prepare_btc_cycle_halving_context_v1_package(
                repo_root=self.repo,
                observation_descriptor_json=self._descriptor_file(),
                output_directory=self.external / "gate",
                produced_at_utc="2026-08-10T23:45:10+00:00",
                authorization=PACKAGE_AUTHORIZATION,
            )

    def test_29_package_roundtrip(self):
        output = self.external / "roundtrip"
        result = prepare_btc_cycle_halving_context_v1_package(
            repo_root=self.repo,
            observation_descriptor_json=self._descriptor_file(),
            output_directory=output,
            produced_at_utc="2026-08-10T23:45:10+00:00",
            authorization=PACKAGE_AUTHORIZATION,
        )
        validation = (
            validate_btc_cycle_halving_context_v1_package(
                output
            )
        )
        self.assertEqual(
            result["component_status"],
            "AVAILABLE",
        )
        self.assertEqual(
            validation["manifest_entries"],
            2,
        )
        self.assertTrue(
            validation[
                "point_in_time_eligible_under_pack_policy"
            ]
        )

    def test_30_package_late_is_preserved_but_ineligible(self):
        output = self.external / "late"
        prepare_btc_cycle_halving_context_v1_package(
            repo_root=self.repo,
            observation_descriptor_json=self._descriptor_file(),
            output_directory=output,
            produced_at_utc="2026-08-10T23:46:00+00:00",
            authorization=PACKAGE_AUTHORIZATION,
        )
        validation = (
            validate_btc_cycle_halving_context_v1_package(
                output
            )
        )
        self.assertFalse(
            validation[
                "point_in_time_eligible_under_pack_policy"
            ]
        )

    def test_31_package_tamper_detected(self):
        output = self.external / "tamper"
        prepare_btc_cycle_halving_context_v1_package(
            repo_root=self.repo,
            observation_descriptor_json=self._descriptor_file(),
            output_directory=output,
            produced_at_utc="2026-08-10T23:45:10+00:00",
            authorization=PACKAGE_AUTHORIZATION,
        )
        with (
            output
            / "btc_cycle_halving_context_component.json"
        ).open("ab") as handle:
            handle.write(b"x")
        with self.assertRaises(BtcCycleHalvingContextError):
            validate_btc_cycle_halving_context_v1_package(
                output
            )

    def test_32_official_artifacts_unchanged(self):
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

        prepare_btc_cycle_halving_context_v1_package(
            repo_root=self.repo,
            observation_descriptor_json=self._descriptor_file(),
            output_directory=self.external / "official",
            produced_at_utc="2026-08-10T23:45:10+00:00",
            authorization=PACKAGE_AUTHORIZATION,
        )

        after = (dataset.read_bytes(), manifest.read_bytes())
        self.assertEqual(before, after)

    def test_33_load_calendar_returns_resource_sha(self):
        value, digest = load_halving_calendar_v1(
            self.repo
        )
        self.assertEqual(
            value["protocol_halving_interval_blocks"],
            210000,
        )
        self.assertEqual(len(digest), 64)


if __name__ == "__main__":
    unittest.main(verbosity=2)
