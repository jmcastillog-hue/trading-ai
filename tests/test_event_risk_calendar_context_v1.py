from __future__ import annotations

import copy
import json
import os
import tempfile
import unittest
from pathlib import Path

from src.context.event_risk_calendar_context_v1 import (
    CAPABILITY,
    FEATURE_ID,
    PACKAGE_AUTHORIZATION,
    SNAPSHOT_SCHEMA_VERSION,
    SOURCE_KIND,
    EventRiskCalendarContextError,
    build_event_risk_calendar_context_v1_component,
    load_event_risk_taxonomy_v1,
    prepare_event_risk_calendar_context_v1_package,
    validate_component_against_level_a_pack_v1,
    validate_event_risk_calendar_context_v1_component,
    validate_event_risk_calendar_context_v1_package,
    validate_event_risk_calendar_snapshot_v1,
    validate_event_risk_taxonomy_v1,
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
        "observation_id": "OBS_EVENT_001",
        "symbol": "BTCUSDT",
        "timeframe": "15m",
        "reference_boundary_utc": reference,
        "synchronized_context_available_at_utc": cutoff,
        "primary_candidate_detected": candidate,
    }


def taxonomy_fixture():
    return {
        "schema_version": "EVENT_RISK_CALENDAR_TAXONOMY_V1",
        "semantics":
            "DESCRIPTIVE_SCHEDULED_EVENT_PROXIMITY_ONLY",
        "event_types": [
            {"event_type": "FOMC_RATE_DECISION", "authority_family": "FEDERAL_RESERVE"},
            {"event_type": "FOMC_MINUTES", "authority_family": "FEDERAL_RESERVE"},
            {"event_type": "US_CPI", "authority_family": "BLS"},
            {"event_type": "US_PPI", "authority_family": "BLS"},
            {"event_type": "US_NONFARM_PAYROLLS", "authority_family": "BLS"},
            {"event_type": "US_CORE_PCE", "authority_family": "BEA"},
            {"event_type": "US_GDP_ADVANCE", "authority_family": "BEA"},
            {"event_type": "US_RETAIL_SALES", "authority_family": "CENSUS"},
        ],
        "directional_meaning_assigned": False,
        "importance_score_assigned": False,
        "event_surprise_used": False,
        "market_reaction_used": False,
    }


def snapshot_fixture():
    return {
        "schema_version": "EVENT_RISK_CALENDAR_SNAPSHOT_V1",
        "snapshot_id": "SNAP_001",
        "snapshot_created_at_utc":
            "2026-08-10T23:45:05+00:00",
        "source_name": "SYNTHETIC_OFFICIAL_CALENDAR_FIXTURE",
        "events": [
            {
                "event_id": "E1",
                "event_type": "US_CPI",
                "scheduled_at_utc":
                    "2026-08-10T23:00:00+00:00",
                "schedule_known_at_utc":
                    "2026-08-01T00:00:00+00:00",
                "schedule_source": "SYNTHETIC_BLS",
            },
            {
                "event_id": "E2",
                "event_type": "FOMC_RATE_DECISION",
                "scheduled_at_utc":
                    "2026-08-11T00:15:00+00:00",
                "schedule_known_at_utc":
                    "2026-08-01T00:00:00+00:00",
                "schedule_source": "SYNTHETIC_FED",
            },
            {
                "event_id": "E3",
                "event_type": "US_CORE_PCE",
                "scheduled_at_utc":
                    "2026-08-11T12:00:00+00:00",
                "schedule_known_at_utc":
                    "2026-08-01T00:00:00+00:00",
                "schedule_source": "SYNTHETIC_BEA",
            },
            {
                "event_id": "E4",
                "event_type": "US_PPI",
                "scheduled_at_utc":
                    "2026-08-12T12:00:00+00:00",
                "schedule_known_at_utc":
                    "2026-08-10T23:45:01+00:00",
                "schedule_source": "SYNTHETIC_BLS",
            },
        ],
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
            resource_dir / "event_risk_calendar_taxonomy_v1.json"
        ).write_text(
            json.dumps(
                taxonomy_fixture(),
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
            "EVENT_RISK_CALENDAR_CONTEXT_V1",
        )

    def test_02_feature_id(self):
        self.assertEqual(
            FEATURE_ID,
            "EVENT_RISK_CALENDAR_CONTEXT_V1",
        )

    def test_03_source_kind(self):
        self.assertEqual(SOURCE_KIND, "DETERMINISTIC")

    def test_04_snapshot_schema(self):
        self.assertEqual(
            SNAPSHOT_SCHEMA_VERSION,
            "EVENT_RISK_CALENDAR_SNAPSHOT_V1",
        )

    def test_05_authorization_exact(self):
        self.assertEqual(
            PACKAGE_AUTHORIZATION,
            "PREPARE_EVENT_RISK_CALENDAR_CONTEXT_V1",
        )

    def test_06_taxonomy_valid(self):
        result = validate_event_risk_taxonomy_v1(
            taxonomy_fixture()
        )
        self.assertEqual(result["event_type_count"], 8)

    def test_07_taxonomy_exact_order(self):
        result = validate_event_risk_taxonomy_v1(
            taxonomy_fixture()
        )
        self.assertEqual(
            result["event_types"][0],
            "FOMC_RATE_DECISION",
        )
        self.assertEqual(
            result["event_types"][-1],
            "US_RETAIL_SALES",
        )

    def test_08_taxonomy_direction_forbidden(self):
        value = taxonomy_fixture()
        value["directional_meaning_assigned"] = True
        with self.assertRaises(EventRiskCalendarContextError):
            validate_event_risk_taxonomy_v1(value)

    def test_09_snapshot_valid(self):
        result = validate_event_risk_calendar_snapshot_v1(
            snapshot_fixture(),
            taxonomy=taxonomy_fixture(),
        )
        self.assertEqual(result["event_count"], 4)

    def test_10_snapshot_unknown_event_type_fails(self):
        value = snapshot_fixture()
        value["events"][0]["event_type"] = "UNKNOWN"
        with self.assertRaises(EventRiskCalendarContextError):
            validate_event_risk_calendar_snapshot_v1(
                value,
                taxonomy=taxonomy_fixture(),
            )

    def test_11_snapshot_duplicate_event_id_fails(self):
        value = snapshot_fixture()
        value["events"][1]["event_id"] = "E1"
        with self.assertRaises(EventRiskCalendarContextError):
            validate_event_risk_calendar_snapshot_v1(
                value,
                taxonomy=taxonomy_fixture(),
            )

    def test_12_snapshot_order_required(self):
        value = snapshot_fixture()
        value["events"] = list(reversed(value["events"]))
        with self.assertRaises(EventRiskCalendarContextError):
            validate_event_risk_calendar_snapshot_v1(
                value,
                taxonomy=taxonomy_fixture(),
            )

    def test_13_schedule_known_after_snapshot_fails(self):
        value = snapshot_fixture()
        value["events"][0]["schedule_known_at_utc"] = (
            "2026-08-11T00:00:00+00:00"
        )
        with self.assertRaises(EventRiskCalendarContextError):
            validate_event_risk_calendar_snapshot_v1(
                value,
                taxonomy=taxonomy_fixture(),
            )

    def _component(
        self,
        *,
        desc=None,
        snapshot=None,
        produced="2026-08-10T23:45:10+00:00",
    ):
        return build_event_risk_calendar_context_v1_component(
            observation_descriptor=desc or descriptor(),
            calendar_snapshot=snapshot or snapshot_fixture(),
            snapshot_sha256="a" * 64,
            taxonomy=taxonomy_fixture(),
            taxonomy_sha256="b" * 64,
            produced_at_utc=produced,
        )

    def test_14_component_available(self):
        self.assertEqual(
            self._component()["status"],
            "AVAILABLE",
        )

    def test_15_post_reference_schedule_knowledge_excluded(self):
        payload = self._component()["payload"]
        self.assertEqual(
            payload[
                "excluded_event_count_schedule_known_after_reference"
            ],
            1,
        )
        self.assertFalse(
            payload["post_reference_schedule_knowledge_used"]
        )

    def test_16_known_event_count(self):
        self.assertEqual(
            self._component()["payload"][
                "known_event_count_at_reference"
            ],
            3,
        )

    def test_17_previous_event(self):
        previous = self._component()["payload"][
            "previous_known_event"
        ]
        self.assertEqual(previous["event_id"], "E1")
        self.assertEqual(previous["seconds_since_event"], 2700)

    def test_18_next_event(self):
        next_event = self._component()["payload"][
            "next_known_event"
        ]
        self.assertEqual(next_event["event_id"], "E2")
        self.assertEqual(next_event["seconds_to_event"], 1800)

    def test_19_upcoming_counts(self):
        counts = self._component()["payload"][
            "upcoming_event_counts"
        ]
        self.assertEqual(counts["1h"], 1)
        self.assertEqual(counts["24h"], 2)

    def test_20_recent_counts(self):
        counts = self._component()["payload"][
            "recent_event_counts"
        ]
        self.assertEqual(counts["1h"], 1)
        self.assertEqual(counts["6h"], 1)

    def test_21_no_event_values_surprise_or_market_reaction(self):
        payload = self._component()["payload"]
        self.assertFalse(payload["event_values_used"])
        self.assertFalse(payload["event_surprise_used"])
        self.assertFalse(payload["market_reaction_used"])

    def test_22_no_price_market_data_or_outcomes(self):
        payload = self._component()["payload"]
        self.assertFalse(payload["price_input_used"])
        self.assertFalse(payload["market_data_input_used"])
        self.assertFalse(payload["future_outcomes_used"])

    def test_23_no_direction_signal_or_importance_score(self):
        payload = self._component()["payload"]
        self.assertFalse(payload["directional_semantics"])
        self.assertFalse(payload["signal_semantics"])
        self.assertFalse(payload["importance_score_assigned"])

    def test_24_produced_before_reference_fails(self):
        with self.assertRaises(EventRiskCalendarContextError):
            self._component(
                produced="2026-08-10T23:44:59+00:00"
            )

    def test_25_snapshot_after_production_fails(self):
        with self.assertRaises(EventRiskCalendarContextError):
            self._component(
                produced="2026-08-10T23:45:04+00:00"
            )

    def test_26_pack_compatible_before_cutoff(self):
        result = validate_component_against_level_a_pack_v1(
            observation_descriptor=descriptor(),
            component=self._component(),
        )
        self.assertTrue(result["point_in_time_eligible"])
        self.assertEqual(
            result["eligibility_reason"],
            "POINT_IN_TIME_ELIGIBLE",
        )

    def test_27_pack_marks_late_producer_ineligible(self):
        result = validate_component_against_level_a_pack_v1(
            observation_descriptor=descriptor(),
            component=self._component(
                produced="2026-08-10T23:46:00+00:00"
            ),
        )
        self.assertFalse(result["point_in_time_eligible"])
        self.assertEqual(
            result["eligibility_reason"],
            "AVAILABLE_AFTER_CONTEXT_CUTOFF",
        )

    def test_28_inputs_not_mutated(self):
        desc = descriptor()
        snap = snapshot_fixture()
        tax = taxonomy_fixture()
        before = (
            copy.deepcopy(desc),
            copy.deepcopy(snap),
            copy.deepcopy(tax),
        )
        build_event_risk_calendar_context_v1_component(
            observation_descriptor=desc,
            calendar_snapshot=snap,
            snapshot_sha256="a" * 64,
            taxonomy=tax,
            taxonomy_sha256="b" * 64,
            produced_at_utc="2026-08-10T23:45:10+00:00",
        )
        self.assertEqual(
            (desc, snap, tax),
            before,
        )

    def test_29_component_validator(self):
        result = (
            validate_event_risk_calendar_context_v1_component(
                self._component()
            )
        )
        self.assertEqual(
            result["known_event_count_at_reference"],
            3,
        )

    def _descriptor_file(self):
        path = self.external / "descriptor.json"
        path.write_text(
            json.dumps(descriptor(), sort_keys=True) + "\n",
            encoding="utf-8",
        )
        return path

    def _snapshot_file(self):
        path = self.external / "snapshot.json"
        path.write_text(
            json.dumps(snapshot_fixture(), sort_keys=True) + "\n",
            encoding="utf-8",
        )
        return path

    def test_30_package_missing_auth_fails(self):
        with self.assertRaises(EventRiskCalendarContextError):
            prepare_event_risk_calendar_context_v1_package(
                repo_root=self.repo,
                observation_descriptor_json=self._descriptor_file(),
                event_calendar_snapshot_json=self._snapshot_file(),
                output_directory=self.external / "missing-auth",
                produced_at_utc="2026-08-10T23:45:10+00:00",
                authorization=None,
            )

    def test_31_package_output_inside_repo_fails(self):
        with self.assertRaises(EventRiskCalendarContextError):
            prepare_event_risk_calendar_context_v1_package(
                repo_root=self.repo,
                observation_descriptor_json=self._descriptor_file(),
                event_calendar_snapshot_json=self._snapshot_file(),
                output_directory=self.repo / "package",
                produced_at_utc="2026-08-10T23:45:10+00:00",
                authorization=PACKAGE_AUTHORIZATION,
            )

    def test_32_package_existing_output_fails(self):
        output = self.external / "existing"
        output.mkdir()
        with self.assertRaises(EventRiskCalendarContextError):
            prepare_event_risk_calendar_context_v1_package(
                repo_root=self.repo,
                observation_descriptor_json=self._descriptor_file(),
                event_calendar_snapshot_json=self._snapshot_file(),
                output_directory=output,
                produced_at_utc="2026-08-10T23:45:10+00:00",
                authorization=PACKAGE_AUTHORIZATION,
            )

    def test_33_gate_enabled_fails(self):
        os.environ[
            "TRADING_AI_OFFICIAL_LONG_EVIDENCE_APPEND_ALLOWED"
        ] = "1"
        with self.assertRaises(EventRiskCalendarContextError):
            prepare_event_risk_calendar_context_v1_package(
                repo_root=self.repo,
                observation_descriptor_json=self._descriptor_file(),
                event_calendar_snapshot_json=self._snapshot_file(),
                output_directory=self.external / "gate",
                produced_at_utc="2026-08-10T23:45:10+00:00",
                authorization=PACKAGE_AUTHORIZATION,
            )

    def test_34_package_roundtrip(self):
        output = self.external / "roundtrip"
        result = prepare_event_risk_calendar_context_v1_package(
            repo_root=self.repo,
            observation_descriptor_json=self._descriptor_file(),
            event_calendar_snapshot_json=self._snapshot_file(),
            output_directory=output,
            produced_at_utc="2026-08-10T23:45:10+00:00",
            authorization=PACKAGE_AUTHORIZATION,
        )
        validation = (
            validate_event_risk_calendar_context_v1_package(
                output
            )
        )
        self.assertEqual(
            result["component_status"],
            "AVAILABLE",
        )
        self.assertTrue(
            validation[
                "point_in_time_eligible_under_pack_policy"
            ]
        )
        self.assertEqual(validation["manifest_entries"], 2)

    def test_35_package_late_is_preserved_but_ineligible(self):
        output = self.external / "late"
        prepare_event_risk_calendar_context_v1_package(
            repo_root=self.repo,
            observation_descriptor_json=self._descriptor_file(),
            event_calendar_snapshot_json=self._snapshot_file(),
            output_directory=output,
            produced_at_utc="2026-08-10T23:46:00+00:00",
            authorization=PACKAGE_AUTHORIZATION,
        )
        validation = (
            validate_event_risk_calendar_context_v1_package(
                output
            )
        )
        self.assertFalse(
            validation[
                "point_in_time_eligible_under_pack_policy"
            ]
        )

    def test_36_package_tamper_detected(self):
        output = self.external / "tamper"
        prepare_event_risk_calendar_context_v1_package(
            repo_root=self.repo,
            observation_descriptor_json=self._descriptor_file(),
            event_calendar_snapshot_json=self._snapshot_file(),
            output_directory=output,
            produced_at_utc="2026-08-10T23:45:10+00:00",
            authorization=PACKAGE_AUTHORIZATION,
        )
        with (
            output
            / "event_risk_calendar_context_component.json"
        ).open("ab") as handle:
            handle.write(b"x")
        with self.assertRaises(EventRiskCalendarContextError):
            validate_event_risk_calendar_context_v1_package(
                output
            )

    def test_37_official_artifacts_unchanged(self):
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

        prepare_event_risk_calendar_context_v1_package(
            repo_root=self.repo,
            observation_descriptor_json=self._descriptor_file(),
            event_calendar_snapshot_json=self._snapshot_file(),
            output_directory=self.external / "official",
            produced_at_utc="2026-08-10T23:45:10+00:00",
            authorization=PACKAGE_AUTHORIZATION,
        )

        after = (dataset.read_bytes(), manifest.read_bytes())
        self.assertEqual(before, after)

    def test_38_load_taxonomy_returns_sha(self):
        value, digest = load_event_risk_taxonomy_v1(
            self.repo
        )
        self.assertEqual(
            value["schema_version"],
            "EVENT_RISK_CALENDAR_TAXONOMY_V1",
        )
        self.assertEqual(len(digest), 64)


if __name__ == "__main__":
    unittest.main(verbosity=2)
