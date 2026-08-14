from __future__ import annotations

import csv
import hashlib
import json
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from src.long_side.synchronized_15m_observation_v1_1 import (
    CAPABILITY,
    DEPTH_BANDS_BPS,
    EXPECTED_MICROSTRUCTURE_REQUESTS_PER_CYCLE,
    EXPECTED_NETWORK_REQUESTS_PER_CYCLE,
    EXPECTED_SPOT_REQUESTS_PER_CYCLE,
    HISTORICAL_COMPONENT_NAMES,
    IMPLEMENTATION_OR_REPAIR_ATTEMPT,
    MAX_IMPLEMENTATION_OR_REPAIR_ATTEMPTS,
    MAX_OBSERVATION_CYCLES,
    MICROSTRUCTURE_DEPTH_LIMIT,
    REAL_SOURCE_ATTESTATION,
    REQUIRED_DEPTH_BANDS_BPS,
    SESSION_AUTHORIZATION,
    TEMPORAL_ALIGNMENT_POLICY_VERSION,
    SynchronizedObservationV11Error,
    assess_component_temporal_eligibility,
    build_microstructure_context_v1_1,
    next_15m_capture_time,
    run_bounded_synchronized_15m_session_v1_1,
    validate_synchronized_observation_session_v1_1,
)

FALSE_CAPTURE = {
    "review_package_created": False,
    "candidate_evaluated": False,
    "candidate_detected": False,
    "manual_confirmed": False,
    "official_dataset_write_performed": False,
    "official_manifest_write_performed": False,
    "official_append_invoked": False,
    "official_append_environment_gate_modified": False,
    "signal_generation_enabled": False,
    "live_alerts_allowed": False,
    "paper_trade_execution_allowed": False,
    "real_capital_allowed": False,
    "market_execution_allowed": False,
    "exchange_execution_allowed": False,
    "automation_allowed": False,
    "execution_allowed": False,
}

FALSE_PACKAGE = {
    "manual_confirmation_required": True,
    "manual_confirmed": False,
    "official_dataset_write_performed": False,
    "official_manifest_write_performed": False,
    "official_append_environment_gate_modified": False,
    "paper_trade_execution_allowed": False,
    "real_capital_allowed": False,
    "market_execution_allowed": False,
    "exchange_execution_allowed": False,
    "automation_allowed": False,
    "execution_allowed": False,
}

FALSE_MICRO = {
    "api_key_used": False,
    "authenticated_endpoint_used": False,
    "websocket_used": False,
    "background_execution": False,
    "scheduler_installed": False,
    "directional_recommendation_generated": False,
    "signal_generation_enabled": False,
    "live_alerts_allowed": False,
    "paper_trade_execution_allowed": False,
    "real_capital_allowed": False,
    "market_execution_allowed": False,
    "exchange_execution_allowed": False,
    "official_append_allowed": False,
    "official_dataset_write_performed": False,
    "official_manifest_write_performed": False,
    "automation_allowed": False,
    "execution_allowed": False,
}


class Clock:
    def __init__(self) -> None:
        self.value = datetime(2026, 8, 10, 23, 37, 46, tzinfo=timezone.utc)

    def __call__(self) -> datetime:
        return self.value

    def sleep(self, seconds: float) -> None:
        self.value += timedelta(seconds=seconds)


def micro_summary(
    reference_close: datetime,
    *,
    taker_offset_minutes: int = -30,
    oi_offset_minutes: int = 0,
    global_offset_minutes: int = 0,
    coverage_5: bool = True,
    coverage_10: bool = True,
    coverage_25: bool = False,
    coverage_50: bool = False,
) -> dict:
    boundary = reference_close + timedelta(milliseconds=1)

    def ts(offset: int) -> str:
        return (boundary + timedelta(minutes=offset)).isoformat()

    def band(bps: int, covered: bool, imbalance: float) -> dict:
        return {
            "band_bps": bps,
            "coverage_complete": covered,
            "bid_level_count": 100 if bps <= 10 else 1000,
            "ask_level_count": 100 if bps <= 10 else 1000,
            "bid_notional_usdt": 1000000.0 + bps,
            "ask_notional_usdt": 1200000.0 + bps,
            "notional_imbalance": imbalance,
        }

    return {
        "capability": "PUBLIC_READ_ONLY_MICROSTRUCTURE_SNAPSHOT_V1_1",
        "provider": "BINANCE_USDM_PUBLIC_REST",
        "symbol": "BTCUSDT",
        "timeframe": "15m",
        "request_count": 7,
        "depth_limit_requested": 1000,
        "depth_bands_bps": [5, 10, 25, 50],
        "reference_closed_candle_utc": reference_close.isoformat(),
        "order_book": {
            "best_bid": 63936.6,
            "best_ask": 63936.7,
            "mid_price": 63936.65,
            "spread_bps": 0.0156,
            "furthest_bid_distance_bps": 18.54,
            "furthest_ask_distance_bps": 19.62,
            "bands": {
                "5": band(5, coverage_5, -0.33),
                "10": band(10, coverage_10, -0.15),
                "25": band(25, coverage_25, -0.08),
                "50": band(50, coverage_50, -0.08),
            },
        },
        "open_interest": {
            "latest_15m": {
                "timestamp_utc": ts(oi_offset_minutes),
                "sum_open_interest": 106287.591,
            },
            "previous_15m": {
                "timestamp_utc": ts(oi_offset_minutes - 15),
                "sum_open_interest": 106336.682,
            },
            "current_time_utc": (boundary + timedelta(seconds=1)).isoformat(),
            "current_open_interest_base": 106307.962,
            "change_15m": -49.091,
            "change_15m_percent": -0.046,
            "value_change_15m_usdt": -5256614.88,
            "value_change_15m_percent": -0.077,
            "directional_interpretation_allowed": False,
        },
        "mark_price_funding": {
            "provider_time_utc": (boundary + timedelta(seconds=9)).isoformat(),
            "mark_price": 63938.9,
            "index_price": 63967.5,
            "mark_index_basis_bps": -4.47,
            "last_funding_rate": 0.00002571,
            "directional_interpretation_allowed": False,
        },
        "taker_buy_sell_volume": {
            "latest_15m": {
                "timestamp_utc": ts(taker_offset_minutes),
                "buy_volume_base": 238.723,
                "sell_volume_base": 197.797,
                "net_taker_volume_base": 40.926,
                "buy_sell_ratio": 1.2069,
            },
            "previous_15m": {
                "timestamp_utc": ts(taker_offset_minutes - 15),
                "buy_volume_base": 138.081,
                "sell_volume_base": 210.412,
                "net_taker_volume_base": -72.331,
                "buy_sell_ratio": 0.6562,
            },
            "directional_interpretation_allowed": False,
        },
        "global_long_short_account_ratio": {
            "latest_15m": {
                "timestamp_utc": ts(global_offset_minutes),
                "long_account_fraction": 0.6159,
                "short_account_fraction": 0.3841,
                "long_short_account_ratio": 1.6035,
            },
            "previous_15m": {
                "timestamp_utc": ts(global_offset_minutes - 15),
                "long_account_fraction": 0.6159,
                "short_account_fraction": 0.3841,
                "long_short_account_ratio": 1.6035,
            },
            "directional_interpretation_allowed": False,
            "top_trader_ratio_used": False,
        },
        "synchronization": {
            "reference_boundary_utc": boundary.isoformat(),
            "aligned_15m_components": [
                "open_interest_history",
                "taker_buy_sell_volume",
                "global_long_short_account_ratio",
            ],
            "point_in_time_components": [
                "order_book",
                "current_open_interest",
                "mark_price_funding",
            ],
            "point_in_time_components_are_not_historical_reconstruction": True,
        },
        "interpretation_constraints": {
            "context_only": True,
            "depth_coverage_is_explicit_not_assumed": True,
            "does_not_modify_frozen_long_rule": True,
        },
        **FALSE_MICRO,
    }


class Tests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.repo = self.root / "repo"
        self.repo.mkdir()
        (self.repo / ".git").mkdir()
        d = self.repo / "data/forward"
        d.mkdir(parents=True)
        (d / "long_forward_observation_dataset_v1.csv").write_text(
            "x\n", encoding="utf-8"
        )
        (d / "long_forward_observation_dataset_v1.manifest.csv").write_text(
            "y\n", encoding="utf-8"
        )
        self.external = self.root / "external"
        self.external.mkdir()
        self.clock = Clock()
        self.spot_count = 0
        self.package_count = 0
        self.micro_count = 0

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def err(self, code, fn, *args, **kwargs) -> None:
        with self.assertRaises(SynchronizedObservationV11Error) as ctx:
            fn(*args, **kwargs)
        self.assertEqual(ctx.exception.code, code)

    def reference_close(self, index: int) -> datetime:
        return datetime(
            2026, 8, 10, 23, 44, 59, 999000, tzinfo=timezone.utc
        ) + timedelta(minutes=15 * index)

    def write_spot(self, directory: Path, close_time: datetime, *, safe=True) -> dict:
        directory.mkdir()
        source = directory / "btc_usdt_15m_closed_candles.csv"
        meta = directory / "capture_metadata.json"
        fields = [
            "open_time_utc",
            "close_time_utc",
            "symbol",
            "timeframe",
            "open",
            "high",
            "low",
            "close",
            "volume",
            "candle_closed",
        ]
        rows = []
        start_close = close_time - timedelta(minutes=15 * 62)
        for i in range(63):
            ct = start_close + timedelta(minutes=15 * i)
            ot = ct - timedelta(minutes=14, seconds=59, milliseconds=999)
            p = 63900 + i
            rows.append(
                {
                    "open_time_utc": ot.isoformat(),
                    "close_time_utc": ct.isoformat(),
                    "symbol": "BTCUSDT",
                    "timeframe": "15m",
                    "open": str(p + 10),
                    "high": str(p + 20),
                    "low": str(p - 20),
                    "close": str(p + 5),
                    "volume": "100",
                    "candle_closed": "True",
                }
            )
        with source.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields)
            writer.writeheader()
            writer.writerows(rows)
        meta.write_text(
            json.dumps(
                {
                    "captured_at_utc": (
                        close_time + timedelta(seconds=5, milliseconds=1)
                    ).isoformat()
                }
            ),
            encoding="utf-8",
        )
        sha = hashlib.sha256(source.read_bytes()).hexdigest()
        result = {
            "capture_id": f"SPOT_{self.spot_count}",
            "source_csv": str(source),
            "metadata_json": str(meta),
            "latest_closed_candle_utc": rows[-1]["close_time_utc"],
            "source_artifact_sha256": sha,
            "network_request_count": 1,
            "one_shot_foreground": True,
            **FALSE_CAPTURE,
        }
        if not safe:
            result["automation_allowed"] = True
        return result

    def spot(self, **kwargs) -> dict:
        self.spot_count += 1
        return self.write_spot(
            Path(kwargs["output_directory"]),
            self.reference_close(self.spot_count - 1),
        )

    def package(self, **kwargs) -> dict:
        self.package_count += 1
        out = Path(kwargs["output_directory"])
        out.mkdir()
        candidate = False
        checks = {
            "failed_breakdown": False,
            "reclaim_confirmed": True,
            "bullish_confirmation": False,
            "candidate_detected": candidate,
        }
        (out / "adapter_checks.json").write_text(
            json.dumps(checks), encoding="utf-8"
        )
        return {
            "package_id": f"PKG_{self.package_count}",
            "source_artifact_sha256": kwargs["expected_source_sha256"],
            "latest_closed_candle_utc": kwargs["prospective_start_utc"],
            "candidate_detected": candidate,
            "eligible_for_real_human_review": candidate,
            **FALSE_PACKAGE,
        }

    def micro(
        self,
        **kwargs,
    ) -> dict:
        self.micro_count += 1
        out = Path(kwargs["output_directory"])
        out.mkdir()
        summary = micro_summary(
            self.reference_close(self.micro_count - 1),
            taker_offset_minutes=-30,
        )
        (out / "microstructure_snapshot.json").write_text(
            json.dumps(summary), encoding="utf-8"
        )
        (out / "manifest.sha256").write_text("mock\n", encoding="utf-8")
        return {
            "output_directory": str(out),
            "request_count": 7,
            "depth_limit_requested": 1000,
            "depth_bands_bps": [5, 10, 25, 50],
            "foreground_only": True,
            "public_read_only": True,
            **FALSE_MICRO,
        }

    def micro_validate(self, directory) -> dict:
        summary = json.loads(
            (Path(directory) / "microstructure_snapshot.json").read_text(
                encoding="utf-8"
            )
        )
        return {
            "request_count": summary["request_count"],
            "depth_limit_requested": summary["depth_limit_requested"],
            "depth_bands_bps": summary["depth_bands_bps"],
        }

    def human(self, latest) -> dict:
        return {
            "context_only": True,
            "actionable_signal_generated": False,
            "positional_state": "TEST",
            "latest_candle_direction": "BEARISH",
        }

    def run_session(self, cycles=1, *, authorization=SESSION_AUTHORIZATION, micro=None):
        return run_bounded_synchronized_15m_session_v1_1(
            repo_root=self.repo,
            output_directory=self.external / "session",
            max_cycles=cycles,
            source_attestation=REAL_SOURCE_ATTESTATION,
            minimum_latest_closed_candle_utc="2026-08-08T21:59:59.999000+00:00",
            authorization=authorization,
            clock=self.clock,
            sleeper=self.clock.sleep,
            spot_capture_callable=self.spot,
            package_callable=self.package,
            microstructure_capture_callable=micro or self.micro,
            microstructure_validate_callable=self.micro_validate,
            human_context_callable=self.human,
        )

    def test_01_capability_v1_1(self):
        self.assertEqual(CAPABILITY, "SYNCHRONIZED_15M_OBSERVATION_V1_1")

    def test_02_repair_attempt_is_3(self):
        self.assertEqual(IMPLEMENTATION_OR_REPAIR_ATTEMPT, 3)
        self.assertEqual(MAX_IMPLEMENTATION_OR_REPAIR_ATTEMPTS, 10)

    def test_03_new_authorization(self):
        self.assertEqual(
            SESSION_AUTHORIZATION,
            "RUN_BOUNDED_SYNCHRONIZED_15M_OBSERVATION_SESSION_V1_1",
        )

    def test_04_old_v1_authorization_rejected(self):
        self.err(
            "SESSION_AUTHORIZATION_REQUIRED",
            self.run_session,
            1,
            authorization="RUN_BOUNDED_SYNCHRONIZED_15M_OBSERVATION_SESSION_V1",
        )

    def test_05_next_capture_time(self):
        self.assertEqual(
            next_15m_capture_time(
                datetime(2026, 8, 10, 23, 37, 46, tzinfo=timezone.utc)
            ),
            datetime(2026, 8, 10, 23, 45, 5, tzinfo=timezone.utc),
        )

    def test_06_cycle_limit(self):
        self.assertEqual(MAX_OBSERVATION_CYCLES, 8)

    def test_07_request_contract(self):
        self.assertEqual(EXPECTED_SPOT_REQUESTS_PER_CYCLE, 1)
        self.assertEqual(EXPECTED_MICROSTRUCTURE_REQUESTS_PER_CYCLE, 7)
        self.assertEqual(EXPECTED_NETWORK_REQUESTS_PER_CYCLE, 8)

    def test_08_depth_contract(self):
        self.assertEqual(MICROSTRUCTURE_DEPTH_LIMIT, 1000)
        self.assertEqual(DEPTH_BANDS_BPS, (5, 10, 25, 50))
        self.assertEqual(REQUIRED_DEPTH_BANDS_BPS, (5, 10))

    def test_09_policy_version(self):
        self.assertEqual(
            TEMPORAL_ALIGNMENT_POLICY_VERSION,
            "SYNCHRONIZED_COMPONENT_TIMESTAMP_ELIGIBILITY_V1",
        )

    def test_10_real_fixture_taker_lag_rejected_for_use(self):
        ref = self.reference_close(0)
        e = assess_component_temporal_eligibility(
            micro_summary(ref, taker_offset_minutes=-30)
        )
        taker = e["historical_components"]["taker_buy_sell_volume"]
        self.assertEqual(taker["timestamp_delta_seconds"], -1800.0)
        self.assertFalse(taker["timestamp_equal_reference_boundary"])
        self.assertFalse(taker["usable_for_synchronized_context"])

    def test_11_real_fixture_oi_aligned(self):
        e = assess_component_temporal_eligibility(
            micro_summary(self.reference_close(0))
        )
        self.assertTrue(
            e["historical_components"]["open_interest_history"][
                "usable_for_synchronized_context"
            ]
        )

    def test_12_real_fixture_global_aligned(self):
        e = assess_component_temporal_eligibility(
            micro_summary(self.reference_close(0))
        )
        self.assertTrue(
            e["historical_components"]["global_long_short_account_ratio"][
                "usable_for_synchronized_context"
            ]
        )

    def test_13_alignment_lists_corrected(self):
        c = build_microstructure_context_v1_1(
            micro_summary(self.reference_close(0))
        )
        self.assertEqual(
            c["synchronization"]["aligned_15m_components"],
            ["open_interest_history", "global_long_short_account_ratio"],
        )
        self.assertEqual(
            c["synchronization"]["misaligned_15m_components"],
            ["taker_buy_sell_volume"],
        )

    def test_14_upstream_alignment_claim_preserved_only_as_provenance(self):
        c = build_microstructure_context_v1_1(
            micro_summary(self.reference_close(0))
        )
        self.assertEqual(
            c["synchronization"]["upstream_reported_aligned_15m_components"],
            list(HISTORICAL_COMPONENT_NAMES),
        )
        self.assertTrue(
            c["synchronization"][
                "alignment_recomputed_by_synchronized_observation_v1_1"
            ]
        )

    def test_15_misaligned_numeric_value_preserved(self):
        c = build_microstructure_context_v1_1(
            micro_summary(self.reference_close(0))
        )
        self.assertEqual(
            c["taker_buy_sell_volume"]["latest_15m"]["buy_sell_ratio"],
            1.2069,
        )
        self.assertFalse(
            c["taker_buy_sell_volume"][
                "latest_15m_usable_for_synchronized_context"
            ]
        )

    def test_16_equal_taker_timestamp_becomes_usable(self):
        c = build_microstructure_context_v1_1(
            micro_summary(self.reference_close(0), taker_offset_minutes=0)
        )
        self.assertTrue(
            c["taker_buy_sell_volume"][
                "latest_15m_usable_for_synchronized_context"
            ]
        )

    def test_17_future_historical_timestamp_not_equal_is_unusable(self):
        e = assess_component_temporal_eligibility(
            micro_summary(self.reference_close(0), taker_offset_minutes=15)
        )
        self.assertFalse(
            e["historical_components"]["taker_buy_sell_volume"][
                "usable_for_synchronized_context"
            ]
        )

    def test_18_point_in_time_not_historical_reconstruction(self):
        e = assess_component_temporal_eligibility(
            micro_summary(self.reference_close(0))
        )
        self.assertTrue(
            e["point_in_time_components_are_not_historical_reconstruction"]
        )
        for item in e["point_in_time_components"].values():
            self.assertFalse(item["historical_alignment_claimed"])
            self.assertFalse(item["usable_for_historical_interval_alignment"])

    def test_19_reference_boundary_must_be_close_plus_1ms(self):
        s = micro_summary(self.reference_close(0))
        s["synchronization"]["reference_boundary_utc"] = (
            self.reference_close(0) + timedelta(seconds=1)
        ).isoformat()
        self.err(
            "MICROSTRUCTURE_REFERENCE_BOUNDARY_INVALID",
            assess_component_temporal_eligibility,
            s,
        )

    def test_20_complete_depth_band_usable(self):
        c = build_microstructure_context_v1_1(
            micro_summary(self.reference_close(0))
        )
        self.assertTrue(c["bands"]["5"]["usable_for_context"])
        self.assertIsNotNone(c["bands"]["5"]["notional_imbalance_usable"])

    def test_21_incomplete_depth_band_not_extrapolated(self):
        c = build_microstructure_context_v1_1(
            micro_summary(self.reference_close(0))
        )
        self.assertFalse(c["bands"]["25"]["usable_for_context"])
        self.assertIsNone(c["bands"]["25"]["notional_imbalance_usable"])

    def test_22_minimum_depth_quality(self):
        c = build_microstructure_context_v1_1(
            micro_summary(self.reference_close(0))
        )
        self.assertTrue(c["minimum_depth_context_usable"])

    def test_23_missing_required_depth_quality(self):
        c = build_microstructure_context_v1_1(
            micro_summary(self.reference_close(0), coverage_10=False)
        )
        self.assertFalse(c["minimum_depth_context_usable"])

    def test_24_one_cycle_eight_requests(self):
        r = self.run_session()
        self.assertEqual(r["completed_cycles"], 1)
        self.assertEqual(r["network_request_count"], 8)
        self.assertEqual(r["misaligned_historical_component_observations"], 1)

    def test_25_three_cycles_twenty_four_requests(self):
        r = self.run_session(3)
        self.assertEqual(r["completed_cycles"], 3)
        self.assertEqual(r["network_request_count"], 24)
        self.assertEqual(r["misaligned_historical_component_observations"], 3)

    def test_26_spot_futures_mismatch_rejected(self):
        def bad_micro(**kwargs):
            self.micro_count += 1
            out = Path(kwargs["output_directory"])
            out.mkdir()
            s = micro_summary(self.reference_close(self.micro_count - 1) + timedelta(minutes=15))
            (out / "microstructure_snapshot.json").write_text(
                json.dumps(s), encoding="utf-8"
            )
            (out / "manifest.sha256").write_text("mock\n", encoding="utf-8")
            return {
                "output_directory": str(out),
                "request_count": 7,
                "depth_limit_requested": 1000,
                "depth_bands_bps": [5, 10, 25, 50],
                "foreground_only": True,
                "public_read_only": True,
                **FALSE_MICRO,
            }

        self.err("SPOT_FUTURES_CANDLE_MISMATCH", self.run_session, 1, micro=bad_micro)

    def test_27_session_validation(self):
        r = self.run_session()
        v = validate_synchronized_observation_session_v1_1(
            r["output_directory"]
        )
        self.assertEqual(v["completed_cycles"], 1)
        self.assertEqual(v["network_request_count"], 8)
        self.assertEqual(v["misaligned_historical_component_observations"], 1)

    def test_28_primary_candidate_unmodified(self):
        r = self.run_session()
        events = [
            json.loads(line)
            for line in (
                Path(r["output_directory"]) / "session_events.jsonl"
            ).read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        cycle = [x for x in events if x["event"] == "CYCLE_COMPLETED"][0]
        self.assertFalse(cycle["candidate_detected"])
        self.assertFalse(
            cycle["microstructure_context"]["microstructure_can_create_candidate"]
        )
        self.assertFalse(
            cycle["microstructure_context"]["microstructure_can_cancel_candidate"]
        )

    def test_29_official_artifacts_unchanged(self):
        before = (
            (self.repo / "data/forward/long_forward_observation_dataset_v1.csv").read_bytes(),
            (self.repo / "data/forward/long_forward_observation_dataset_v1.manifest.csv").read_bytes(),
        )
        self.run_session()
        after = (
            (self.repo / "data/forward/long_forward_observation_dataset_v1.csv").read_bytes(),
            (self.repo / "data/forward/long_forward_observation_dataset_v1.manifest.csv").read_bytes(),
        )
        self.assertEqual(before, after)

    def test_30_no_external_notifications_or_execution(self):
        r = self.run_session()
        self.assertFalse(r["external_notifications_sent"])
        self.assertFalse(r["paper_trade_execution_allowed"])
        self.assertFalse(r["real_capital_allowed"])
        self.assertFalse(r["execution_allowed"])

    def test_31_summary_records_temporal_policy(self):
        r = self.run_session()
        s = json.loads(
            (Path(r["output_directory"]) / "session_summary.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(
            s["temporal_alignment_policy_version"],
            TEMPORAL_ALIGNMENT_POLICY_VERSION,
        )
        self.assertTrue(
            s["historical_component_timestamp_alignment_required_for_use"]
        )
        self.assertFalse(s["historical_interval_equivalence_claimed"])

    def test_32_old_auth_does_not_create_output(self):
        out = self.external / "old-auth"
        self.err(
            "SESSION_AUTHORIZATION_REQUIRED",
            run_bounded_synchronized_15m_session_v1_1,
            repo_root=self.repo,
            output_directory=out,
            max_cycles=1,
            source_attestation=REAL_SOURCE_ATTESTATION,
            minimum_latest_closed_candle_utc=None,
            authorization="RUN_BOUNDED_SYNCHRONIZED_15M_OBSERVATION_SESSION_V1",
        )
        self.assertFalse(out.exists())


if __name__ == "__main__":
    unittest.main()
