from __future__ import annotations

import copy
import hashlib
import json
import os
import tempfile
import unittest
from pathlib import Path

import src.context.synchronized_microstructure_context_v1 as module_under_test
from src.context.synchronized_microstructure_context_v1 import (
    CAPABILITY,
    FEATURE_ID,
    PACKAGE_AUTHORIZATION,
    SOURCE_KIND,
    SynchronizedMicrostructureContextError,
    build_synchronized_microstructure_context_v1_component,
    load_synchronized_microstructure_context_policy_v1,
    prepare_synchronized_microstructure_context_v1_package,
    validate_component_against_level_a_pack_v1,
    validate_synchronized_microstructure_context_policy_v1,
    validate_synchronized_microstructure_context_v1_component,
    validate_synchronized_microstructure_context_v1_package,
)


POLICY_EFFECTIVE = "2026-08-17T00:00:00+00:00"


def descriptor(
    *,
    reference="2026-08-18T00:00:00+00:00",
    close="2026-08-17T23:59:59.999000+00:00",
    cutoff="2026-08-18T00:00:05+00:00",
    candidate=False,
):
    return {
        "observation_descriptor_schema_version":
            "FORWARD_OUTCOME_OBSERVATION_DESCRIPTOR_V1",
        "observation_id": "OBS_MICRO_001",
        "symbol": "BTCUSDT",
        "timeframe": "15m",
        "reference_boundary_utc": reference,
        "reference_closed_candle_utc": close,
        "synchronized_context_available_at_utc": cutoff,
        "primary_candidate_detected": candidate,
    }


def policy_fixture():
    return {
        "schema_version":
            "SYNCHRONIZED_MICROSTRUCTURE_CONTEXT_POLICY_V1",
        "feature_id":
            "SYNCHRONIZED_MICROSTRUCTURE_CONTEXT_V1",
        "policy_effective_from_utc": POLICY_EFFECTIVE,
        "source_snapshot_capability":
            "PUBLIC_READ_ONLY_MICROSTRUCTURE_SNAPSHOT_V1_1",
        "source_provider":
            "BINANCE_USDM_PUBLIC_REST",
        "source_symbol": "BTCUSDT",
        "source_timeframe": "15m",
        "source_depth_limit": 1000,
        "source_depth_bands_bps": [5, 10, 25, 50],
        "required_depth_bands_bps": [5, 10],
        "optional_depth_bands_bps": [25, 50],
        "temporal_alignment_policy_version":
            "SYNCHRONIZED_COMPONENT_TIMESTAMP_ELIGIBILITY_V1",
        "historical_component_exact_reference_boundary_equality_required":
            True,
        "misaligned_historical_component_preserved_but_not_usable":
            True,
        "point_in_time_components_are_not_historical_reconstruction":
            True,
        "retrospective_source_before_policy_effective_is_not_point_in_time_eligible":
            True,
        "directional_meaning_assigned": False,
        "composite_score_assigned": False,
        "signal_semantics": False,
    }


def summary_fixture(
    *,
    reference="2026-08-18T00:00:00+00:00",
    close="2026-08-17T23:59:59.999000+00:00",
    captured="2026-08-18T00:00:05+00:00",
    taker_timestamp=None,
    band25_complete=False,
    band50_complete=False,
):
    taker_timestamp = (
        taker_timestamp
        or reference
    )

    def band(
        bps,
        complete,
        imbalance,
    ):
        return {
            "band_bps": bps,
            "coverage_complete": complete,
            "bid_level_count": 4,
            "ask_level_count": 5,
            "bid_notional_usdt": 100000.0 + bps,
            "ask_notional_usdt": 90000.0 + bps,
            "notional_imbalance": imbalance,
        }

    return {
        "snapshot_schema_version":
            "PUBLIC_READ_ONLY_MICROSTRUCTURE_SNAPSHOT_V1_1",
        "capability":
            "PUBLIC_READ_ONLY_MICROSTRUCTURE_SNAPSHOT_V1_1",
        "provider": "BINANCE_USDM_PUBLIC_REST",
        "symbol": "BTCUSDT",
        "timeframe": "15m",
        "captured_started_at_utc":
            "2026-08-18T00:00:01+00:00",
        "captured_finished_at_utc": captured,
        "reference_closed_candle_utc": close,
        "request_count": 7,
        "depth_limit_requested": 1000,
        "depth_bands_bps": [5, 10, 25, 50],
        "order_book": {
            "best_bid": 63999.0,
            "best_ask": 64001.0,
            "mid_price": 64000.0,
            "spread_bps": 0.3125,
            "furthest_bid_distance_bps": 30.0,
            "furthest_ask_distance_bps": 31.0,
            "bands": {
                "5": band(5, True, 0.10),
                "10": band(10, True, -0.05),
                "25": band(25, band25_complete, 0.20),
                "50": band(50, band50_complete, 0.30),
            },
        },
        "open_interest": {
            "current_open_interest_base": 1000.0,
            "current_open_interest_approx_usdt_at_mark":
                64000000.0,
            "current_time_utc":
                "2026-08-18T00:00:02+00:00",
            "latest_15m": {
                "timestamp_utc": reference,
                "sum_open_interest": 980.0,
                "sum_open_interest_value_usdt":
                    62720000.0,
            },
            "change_15m_percent": 1.2,
            "value_change_15m_percent": 1.1,
        },
        "mark_price_funding": {
            "provider_time_utc":
                "2026-08-18T00:00:03+00:00",
            "mark_price": 64000.0,
            "index_price": 63990.0,
            "mark_index_basis_bps": 1.562744,
            "last_funding_rate_percent": 0.01,
        },
        "taker_buy_sell_volume": {
            "latest_15m": {
                "timestamp_utc": taker_timestamp,
                "buy_volume_base": 120.0,
                "sell_volume_base": 100.0,
                "buy_sell_ratio": 1.2,
                "net_taker_volume_base": 20.0,
            },
        },
        "global_long_short_account_ratio": {
            "latest_15m": {
                "timestamp_utc": reference,
                "long_short_account_ratio": 1.1,
                "long_account_fraction": 0.524,
                "short_account_fraction": 0.476,
            },
        },
        "synchronization": {
            "reference_boundary_utc": reference,
            "aligned_15m_components": [
                "open_interest_history",
                "taker_buy_sell_volume",
                "global_long_short_account_ratio",
            ],
        },
        "interpretation_constraints": {
            "context_only": True,
        },
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
            official
            / "long_forward_observation_dataset_v1.csv"
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
            resource_dir
            / "synchronized_microstructure_context_policy_v1.json"
        ).write_text(
            json.dumps(
                policy_fixture(),
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

        self._original_snapshot_validator = (
            module_under_test.
            validate_public_read_only_microstructure_snapshot_v1_1
        )
        module_under_test.validate_public_read_only_microstructure_snapshot_v1_1 = (
            lambda directory: {
                "request_count": 7,
                "depth_limit_requested": 1000,
                "depth_bands_bps": [5, 10, 25, 50],
                "manifest_entries": 3,
            }
        )

    def tearDown(self):
        module_under_test.validate_public_read_only_microstructure_snapshot_v1_1 = (
            self._original_snapshot_validator
        )
        os.environ.pop(
            "TRADING_AI_OFFICIAL_LONG_EVIDENCE_APPEND_ALLOWED",
            None,
        )
        self.tmp.cleanup()

    def _component(
        self,
        *,
        desc=None,
        summary=None,
        produced="2026-08-18T00:00:06+00:00",
    ):
        return build_synchronized_microstructure_context_v1_component(
            observation_descriptor=desc or descriptor(),
            microstructure_summary=summary or summary_fixture(),
            microstructure_snapshot_sha256="a" * 64,
            source_manifest_sha256="b" * 64,
            policy=policy_fixture(),
            policy_sha256="c" * 64,
            produced_at_utc=produced,
        )

    def test_01_capability(self):
        self.assertEqual(
            CAPABILITY,
            "SYNCHRONIZED_MICROSTRUCTURE_CONTEXT_V1",
        )

    def test_02_feature_id(self):
        self.assertEqual(
            FEATURE_ID,
            "SYNCHRONIZED_MICROSTRUCTURE_CONTEXT_V1",
        )

    def test_03_source_kind(self):
        self.assertEqual(
            SOURCE_KIND,
            "OBSERVED_MARKET",
        )

    def test_04_authorization_exact(self):
        self.assertEqual(
            PACKAGE_AUTHORIZATION,
            "PREPARE_SYNCHRONIZED_MICROSTRUCTURE_CONTEXT_V1",
        )

    def test_05_policy_valid(self):
        result = (
            validate_synchronized_microstructure_context_policy_v1(
                policy_fixture()
            )
        )
        self.assertEqual(
            result["source_depth_limit"],
            1000,
        )

    def test_06_policy_effective_floor_exact(self):
        result = (
            validate_synchronized_microstructure_context_policy_v1(
                policy_fixture()
            )
        )
        self.assertEqual(
            result["policy_effective_from_utc"],
            POLICY_EFFECTIVE,
        )

    def test_07_policy_wrong_feature_fails(self):
        value = policy_fixture()
        value["feature_id"] = "WRONG"
        with self.assertRaises(
            SynchronizedMicrostructureContextError
        ):
            validate_synchronized_microstructure_context_policy_v1(
                value
            )

    def test_08_policy_direction_forbidden(self):
        value = policy_fixture()
        value["directional_meaning_assigned"] = True
        with self.assertRaises(
            SynchronizedMicrostructureContextError
        ):
            validate_synchronized_microstructure_context_policy_v1(
                value
            )

    def test_09_component_available(self):
        self.assertEqual(
            self._component()["status"],
            "AVAILABLE",
        )

    def test_10_future_snapshot_available_at_capture_finish(self):
        component = self._component()
        self.assertEqual(
            component["available_at_utc"],
            "2026-08-18T00:00:05+00:00",
        )

    def test_11_information_cutoff_is_capture_finish(self):
        component = self._component()
        self.assertEqual(
            component["information_cutoff_utc"],
            "2026-08-18T00:00:05+00:00",
        )

    def test_12_future_snapshot_policy_floor_not_applied(self):
        payload = self._component()["payload"]
        self.assertFalse(
            payload["retrospective_policy_floor_applied"]
        )

    def test_13_old_snapshot_policy_floor_applied(self):
        old_desc = descriptor(
            reference="2026-08-10T23:45:00+00:00",
            close="2026-08-10T23:44:59.999000+00:00",
            cutoff="2026-08-10T23:45:12+00:00",
        )
        old_summary = summary_fixture(
            reference="2026-08-10T23:45:00+00:00",
            close="2026-08-10T23:44:59.999000+00:00",
            captured="2026-08-10T23:45:12+00:00",
        )
        component = self._component(
            desc=old_desc,
            summary=old_summary,
            produced="2026-08-17T00:00:01+00:00",
        )
        self.assertEqual(
            component["available_at_utc"],
            POLICY_EFFECTIVE,
        )
        self.assertTrue(
            component["payload"][
                "retrospective_policy_floor_applied"
            ]
        )

    def test_14_old_snapshot_pack_ineligible(self):
        old_desc = descriptor(
            reference="2026-08-10T23:45:00+00:00",
            close="2026-08-10T23:44:59.999000+00:00",
            cutoff="2026-08-10T23:45:12+00:00",
        )
        old_summary = summary_fixture(
            reference="2026-08-10T23:45:00+00:00",
            close="2026-08-10T23:44:59.999000+00:00",
            captured="2026-08-10T23:45:12+00:00",
        )
        component = self._component(
            desc=old_desc,
            summary=old_summary,
            produced="2026-08-17T00:00:01+00:00",
        )
        result = validate_component_against_level_a_pack_v1(
            observation_descriptor=old_desc,
            component=component,
        )
        self.assertFalse(
            result["point_in_time_eligible"]
        )
        self.assertEqual(
            result["eligibility_reason"],
            "AVAILABLE_AFTER_CONTEXT_CUTOFF",
        )

    def test_15_future_snapshot_pack_eligible(self):
        result = validate_component_against_level_a_pack_v1(
            observation_descriptor=descriptor(),
            component=self._component(),
        )
        self.assertTrue(
            result["point_in_time_eligible"]
        )
        self.assertEqual(
            result["eligibility_reason"],
            "POINT_IN_TIME_ELIGIBLE",
        )

    def test_16_reference_close_mismatch_fails(self):
        value = summary_fixture()
        value["reference_closed_candle_utc"] = (
            "2026-08-17T23:44:59.999000+00:00"
        )
        with self.assertRaises(
            SynchronizedMicrostructureContextError
        ):
            self._component(summary=value)

    def test_17_reference_boundary_mismatch_fails(self):
        value = summary_fixture()
        value["synchronization"][
            "reference_boundary_utc"
        ] = "2026-08-18T00:15:00+00:00"
        with self.assertRaises(
            SynchronizedMicrostructureContextError
        ):
            self._component(summary=value)

    def test_18_context_availability_mismatch_fails(self):
        value = summary_fixture(
            captured="2026-08-18T00:00:06+00:00"
        )
        with self.assertRaises(
            SynchronizedMicrostructureContextError
        ):
            self._component(summary=value)

    def test_19_produced_before_policy_fails(self):
        with self.assertRaises(
            SynchronizedMicrostructureContextError
        ):
            self._component(
                produced="2026-08-16T23:59:59+00:00"
            )

    def test_20_produced_before_source_complete_fails(self):
        with self.assertRaises(
            SynchronizedMicrostructureContextError
        ):
            self._component(
                produced="2026-08-18T00:00:04+00:00"
            )

    def test_21_all_historical_aligned(self):
        payload = self._component()["payload"]
        self.assertTrue(
            payload[
                "all_historical_components_timestamp_aligned"
            ]
        )
        self.assertEqual(
            payload["misaligned_historical_components"],
            [],
        )

    def test_22_misaligned_taker_excluded(self):
        value = summary_fixture(
            taker_timestamp="2026-08-17T23:45:00+00:00"
        )
        payload = self._component(
            summary=value
        )["payload"]
        taker = payload["historical_components"][
            "taker_buy_sell_volume"
        ]
        self.assertFalse(
            taker["usable_for_synchronized_context"]
        )
        self.assertIsNone(taker["values"])
        self.assertIn(
            "taker_buy_sell_volume",
            payload["misaligned_historical_components"],
        )

    def test_23_aligned_open_interest_values_present(self):
        item = self._component()["payload"][
            "historical_components"
        ]["open_interest_history"]
        self.assertTrue(
            item["usable_for_synchronized_context"]
        )
        self.assertIsNotNone(item["values"])

    def test_24_required_depth_usable(self):
        depth = self._component()["payload"]["depth"]
        self.assertTrue(
            depth["minimum_depth_context_usable"]
        )

    def test_25_incomplete_25_band_not_usable(self):
        band = self._component()["payload"][
            "depth"
        ]["bands"]["25"]
        self.assertFalse(band["coverage_complete"])
        self.assertIsNone(
            band["notional_imbalance_usable"]
        )

    def test_26_no_incomplete_depth_extrapolation(self):
        self.assertFalse(
            self._component()["payload"]["depth"][
                "incomplete_depth_extrapolation_allowed"
            ]
        )

    def test_27_no_hidden_stop_claim(self):
        self.assertFalse(
            self._component()["payload"][
                "order_book_hidden_stops_or_liquidations_revealed"
            ]
        )

    def test_28_no_oi_direction_claim(self):
        self.assertFalse(
            self._component()["payload"][
                "open_interest_identifies_long_vs_short_direction"
            ]
        )

    def test_29_no_actionable_funding_ratio_claim(self):
        self.assertFalse(
            self._component()["payload"][
                "funding_and_ratios_actionable"
            ]
        )

    def test_30_no_direction_signal_score_or_outcomes(self):
        payload = self._component()["payload"]
        self.assertFalse(payload["directional_semantics"])
        self.assertFalse(payload["signal_semantics"])
        self.assertFalse(
            payload["composite_score_assigned"]
        )
        self.assertFalse(payload["future_outcomes_used"])

    def test_31_component_validator(self):
        result = (
            validate_synchronized_microstructure_context_v1_component(
                self._component()
            )
        )
        self.assertEqual(
            result["aligned_historical_component_count"],
            3,
        )
        self.assertEqual(
            result["misaligned_historical_component_count"],
            0,
        )

    def test_32_inputs_not_mutated(self):
        desc = descriptor()
        summary = summary_fixture()
        policy = policy_fixture()
        before = (
            copy.deepcopy(desc),
            copy.deepcopy(summary),
            copy.deepcopy(policy),
        )
        build_synchronized_microstructure_context_v1_component(
            observation_descriptor=desc,
            microstructure_summary=summary,
            microstructure_snapshot_sha256="a" * 64,
            source_manifest_sha256="b" * 64,
            policy=policy,
            policy_sha256="c" * 64,
            produced_at_utc="2026-08-18T00:00:06+00:00",
        )
        self.assertEqual(
            (desc, summary, policy),
            before,
        )

    def _descriptor_file(self):
        path = self.external / "descriptor.json"
        path.write_text(
            json.dumps(descriptor(), sort_keys=True) + "\n",
            encoding="utf-8",
        )
        return path

    def _source_dir(self):
        directory = self.external / "source"
        if not directory.exists():
            directory.mkdir()
            summary = summary_fixture()
            (
                directory / "microstructure_snapshot.json"
            ).write_text(
                json.dumps(summary, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            (
                directory / "raw_responses.json"
            ).write_text("{}\n", encoding="utf-8")
            (
                directory / "request_log.json"
            ).write_text("[]\n", encoding="utf-8")
            lines = []
            for name in (
                "raw_responses.json",
                "request_log.json",
                "microstructure_snapshot.json",
            ):
                digest = hashlib.sha256(
                    (directory / name).read_bytes()
                ).hexdigest()
                lines.append(f"{digest}  {name}")
            (
                directory / "manifest.sha256"
            ).write_text(
                "\n".join(lines) + "\n",
                encoding="utf-8",
            )
        return directory

    def test_33_package_missing_auth_fails(self):
        with self.assertRaises(
            SynchronizedMicrostructureContextError
        ):
            prepare_synchronized_microstructure_context_v1_package(
                repo_root=self.repo,
                observation_descriptor_json=
                    self._descriptor_file(),
                microstructure_snapshot_directory=
                    self._source_dir(),
                output_directory=
                    self.external / "missing-auth",
                produced_at_utc=
                    "2026-08-18T00:00:06+00:00",
                authorization=None,
            )

    def test_34_package_output_inside_repo_fails(self):
        with self.assertRaises(
            SynchronizedMicrostructureContextError
        ):
            prepare_synchronized_microstructure_context_v1_package(
                repo_root=self.repo,
                observation_descriptor_json=
                    self._descriptor_file(),
                microstructure_snapshot_directory=
                    self._source_dir(),
                output_directory=self.repo / "package",
                produced_at_utc=
                    "2026-08-18T00:00:06+00:00",
                authorization=PACKAGE_AUTHORIZATION,
            )

    def test_35_package_existing_output_fails(self):
        output = self.external / "existing"
        output.mkdir()
        with self.assertRaises(
            SynchronizedMicrostructureContextError
        ):
            prepare_synchronized_microstructure_context_v1_package(
                repo_root=self.repo,
                observation_descriptor_json=
                    self._descriptor_file(),
                microstructure_snapshot_directory=
                    self._source_dir(),
                output_directory=output,
                produced_at_utc=
                    "2026-08-18T00:00:06+00:00",
                authorization=PACKAGE_AUTHORIZATION,
            )

    def test_36_gate_enabled_fails(self):
        os.environ[
            "TRADING_AI_OFFICIAL_LONG_EVIDENCE_APPEND_ALLOWED"
        ] = "1"
        with self.assertRaises(
            SynchronizedMicrostructureContextError
        ):
            prepare_synchronized_microstructure_context_v1_package(
                repo_root=self.repo,
                observation_descriptor_json=
                    self._descriptor_file(),
                microstructure_snapshot_directory=
                    self._source_dir(),
                output_directory=self.external / "gate",
                produced_at_utc=
                    "2026-08-18T00:00:06+00:00",
                authorization=PACKAGE_AUTHORIZATION,
            )

    def test_37_package_roundtrip(self):
        output = self.external / "roundtrip"
        result = (
            prepare_synchronized_microstructure_context_v1_package(
                repo_root=self.repo,
                observation_descriptor_json=
                    self._descriptor_file(),
                microstructure_snapshot_directory=
                    self._source_dir(),
                output_directory=output,
                produced_at_utc=
                    "2026-08-18T00:00:06+00:00",
                authorization=PACKAGE_AUTHORIZATION,
            )
        )
        validation = (
            validate_synchronized_microstructure_context_v1_package(
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
        self.assertEqual(
            validation["manifest_entries"],
            2,
        )

    def test_38_package_tamper_detected(self):
        output = self.external / "tamper"
        prepare_synchronized_microstructure_context_v1_package(
            repo_root=self.repo,
            observation_descriptor_json=
                self._descriptor_file(),
            microstructure_snapshot_directory=
                self._source_dir(),
            output_directory=output,
            produced_at_utc=
                "2026-08-18T00:00:06+00:00",
            authorization=PACKAGE_AUTHORIZATION,
        )
        with (
            output
            / "synchronized_microstructure_context_component.json"
        ).open("ab") as handle:
            handle.write(b"x")

        with self.assertRaises(
            SynchronizedMicrostructureContextError
        ):
            validate_synchronized_microstructure_context_v1_package(
                output
            )

    def test_39_official_artifacts_unchanged(self):
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
        before = (
            dataset.read_bytes(),
            manifest.read_bytes(),
        )

        prepare_synchronized_microstructure_context_v1_package(
            repo_root=self.repo,
            observation_descriptor_json=
                self._descriptor_file(),
            microstructure_snapshot_directory=
                self._source_dir(),
            output_directory=self.external / "official",
            produced_at_utc=
                "2026-08-18T00:00:06+00:00",
            authorization=PACKAGE_AUTHORIZATION,
        )

        after = (
            dataset.read_bytes(),
            manifest.read_bytes(),
        )
        self.assertEqual(before, after)

    def test_40_load_policy_returns_sha(self):
        value, digest = (
            load_synchronized_microstructure_context_policy_v1(
                self.repo
            )
        )
        self.assertEqual(
            value["feature_id"],
            "SYNCHRONIZED_MICROSTRUCTURE_CONTEXT_V1",
        )
        self.assertEqual(len(digest), 64)


if __name__ == "__main__":
    unittest.main(verbosity=2)
