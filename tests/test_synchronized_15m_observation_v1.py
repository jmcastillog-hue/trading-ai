from __future__ import annotations

import csv
import hashlib
import json
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from src.long_side.synchronized_15m_observation_v1 import (
    DEPTH_BANDS_BPS,
    EXPECTED_NETWORK_REQUESTS_PER_CYCLE,
    MAX_IMPLEMENTATION_OR_REPAIR_ATTEMPTS,
    MAX_OBSERVATION_CYCLES,
    MICROSTRUCTURE_DEPTH_LIMIT,
    REAL_SOURCE_ATTESTATION,
    REQUIRED_DEPTH_BANDS_BPS,
    SESSION_AUTHORIZATION,
    SynchronizedObservationError,
    build_microstructure_context,
    next_15m_capture_time,
    run_bounded_synchronized_15m_session,
    validate_synchronized_observation_session,
)

FALSE_SPOT = {
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
    def __init__(self):
        self.value = datetime(2026, 8, 10, 13, 47, 0, tzinfo=timezone.utc)

    def __call__(self):
        return self.value

    def sleep(self, seconds):
        self.value += timedelta(seconds=seconds)


class Tests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.repo = self.root / "repo"
        self.repo.mkdir()
        (self.repo / ".git").mkdir()
        d = self.repo / "data/forward"
        d.mkdir(parents=True)
        (d / "long_forward_observation_dataset_v1.csv").write_text("x\n", encoding="utf-8")
        (d / "long_forward_observation_dataset_v1.manifest.csv").write_text("y\n", encoding="utf-8")
        self.external = self.root / "external"
        self.external.mkdir()
        self.clock = Clock()
        self.spot_count = 0
        self.micro_count = 0
        self.package_count = 0
        self.micro_validate_count = 0
        self.mismatch_micro = False
        self.incomplete_5 = False
        self.candidate_at = None

    def tearDown(self):
        self.tmp.cleanup()

    def err(self, code, fn, *args, **kwargs):
        with self.assertRaises(SynchronizedObservationError) as ctx:
            fn(*args, **kwargs)
        self.assertEqual(ctx.exception.code, code)

    def _close_for_index(self, index):
        return datetime(2026, 8, 10, 13, 59, 59, 999000, tzinfo=timezone.utc) + timedelta(minutes=15 * (index - 1))

    def write_spot_capture(self, directory: Path, close_time: datetime, *, request_count=1, unsafe=False):
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
        start_open = close_time - timedelta(minutes=15 * 62 + 14, seconds=59.999)
        for i in range(63):
            ot = start_open + timedelta(minutes=15 * i)
            ct = ot + timedelta(minutes=14, seconds=59.999)
            p = 65000 + i
            rows.append(
                {
                    "open_time_utc": ot.isoformat(),
                    "close_time_utc": ct.isoformat(),
                    "symbol": "BTCUSDT",
                    "timeframe": "15m",
                    "open": str(p),
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
            json.dumps({"captured_at_utc": (close_time + timedelta(seconds=5)).isoformat()}),
            encoding="utf-8",
        )
        sha = hashlib.sha256(source.read_bytes()).hexdigest()
        result = {
            "capture_id": f"SPOT_{self.spot_count}",
            "source_csv": str(source),
            "metadata_json": str(meta),
            "latest_closed_candle_utc": rows[-1]["close_time_utc"],
            "source_artifact_sha256": sha,
            "network_request_count": request_count,
            "one_shot_foreground": True,
            **FALSE_SPOT,
        }
        if unsafe:
            result["automation_allowed"] = True
        return result

    def spot_capture(self, **kwargs):
        self.spot_count += 1
        return self.write_spot_capture(Path(kwargs["output_directory"]), self._close_for_index(self.spot_count))

    def package(self, **kwargs):
        self.package_count += 1
        out = Path(kwargs["output_directory"])
        out.mkdir()
        candidate = self.candidate_at == self.package_count
        checks = {
            "failed_breakdown": candidate,
            "reclaim_confirmed": True,
            "bullish_confirmation": True,
            "candidate_detected": candidate,
        }
        (out / "adapter_checks.json").write_text(json.dumps(checks), encoding="utf-8")
        return {
            "package_id": f"PKG_{self.package_count}",
            "source_artifact_sha256": kwargs["expected_source_sha256"],
            "latest_closed_candle_utc": kwargs["prospective_start_utc"],
            "candidate_detected": candidate,
            "eligible_for_real_human_review": candidate,
            **FALSE_PACKAGE,
        }

    def _micro_summary(self, close_time: datetime, *, incomplete_5=False):
        bands = {}
        coverage = {"5": not incomplete_5, "10": True, "25": False, "50": False}
        for key, bps in zip(("5", "10", "25", "50"), DEPTH_BANDS_BPS):
            covered = coverage[key]
            bands[key] = {
                "band_bps": bps,
                "bid_level_count": 100 + bps,
                "ask_level_count": 110 + bps,
                "bid_qty_base": 10.0,
                "ask_qty_base": 11.0,
                "bid_notional_usdt": 1000000.0 + bps,
                "ask_notional_usdt": 1100000.0 + bps,
                "notional_imbalance": -0.047,
                "coverage_complete": covered,
            }
        return {
            "snapshot_schema_version": "PUBLIC_READ_ONLY_MICROSTRUCTURE_SNAPSHOT_V1_1",
            "capability": "PUBLIC_READ_ONLY_MICROSTRUCTURE_SNAPSHOT_V1_1",
            "implementation_schema_version": "PUBLIC_READ_ONLY_MICROSTRUCTURE_SNAPSHOT_IMPLEMENTATION_V1_1",
            "provider": "BINANCE_USDM_PUBLIC_REST",
            "symbol": "BTCUSDT",
            "timeframe": "15m",
            "reference_closed_candle_utc": close_time.isoformat(),
            "request_count": 7,
            "depth_limit_requested": 1000,
            "depth_bands_bps": [5, 10, 25, 50],
            "order_book": {
                "returned_bid_levels": 1000,
                "returned_ask_levels": 1000,
                "best_bid": 65100.0,
                "best_ask": 65100.1,
                "mid_price": 65100.05,
                "spread_bps": 0.015,
                "furthest_bid_distance_bps": 20.0,
                "furthest_ask_distance_bps": 19.0,
                "bands": bands,
            },
            "open_interest": {"change_15m_percent": 0.01},
            "mark_price_funding": {"last_funding_rate": 0.00005},
            "taker_buy_sell_volume": {"latest_15m": {"buy_sell_ratio": 1.2}},
            "global_long_short_account_ratio": {"latest_15m": {"long_short_account_ratio": 1.1}},
            "synchronization": {"reference_boundary_utc": (close_time + timedelta(milliseconds=1)).isoformat()},
            "interpretation_constraints": {
                "context_only": True,
                "does_not_modify_frozen_long_rule": True,
                "depth_coverage_is_explicit_not_assumed": True,
            },
            **FALSE_MICRO,
        }

    def micro_capture(self, **kwargs):
        self.micro_count += 1
        out = Path(kwargs["output_directory"])
        out.mkdir()
        close = self._close_for_index(self.micro_count)
        if self.mismatch_micro:
            close += timedelta(minutes=15)
        summary = self._micro_summary(close, incomplete_5=self.incomplete_5)
        (out / "microstructure_snapshot.json").write_text(json.dumps(summary), encoding="utf-8")
        (out / "raw_responses.json").write_text("{}", encoding="utf-8")
        (out / "request_log.json").write_text("[]", encoding="utf-8")
        (out / "manifest.sha256").write_text("mock\n", encoding="utf-8")
        return {
            "capability": "PUBLIC_READ_ONLY_MICROSTRUCTURE_SNAPSHOT_V1_1",
            "output_directory": str(out),
            "request_count": 7,
            "depth_limit_requested": 1000,
            "depth_bands_bps": [5, 10, 25, 50],
            "reference_closed_candle_utc": close.isoformat(),
            "foreground_only": True,
            "public_read_only": True,
            **FALSE_MICRO,
        }

    def micro_validate(self, directory):
        self.micro_validate_count += 1
        summary = json.loads((Path(directory) / "microstructure_snapshot.json").read_text(encoding="utf-8"))
        return {
            "request_count": summary["request_count"],
            "depth_limit_requested": summary["depth_limit_requested"],
            "depth_bands_bps": summary["depth_bands_bps"],
        }

    def human_context(self, latest):
        return {
            "positional_state": "TEST",
            "context_only": True,
            "actionable_signal_generated": False,
        }

    def run_session(self, cycles=1, minimum="2026-08-10T04:29:59.999000+00:00", **overrides):
        return run_bounded_synchronized_15m_session(
            repo_root=self.repo,
            output_directory=self.external / "session",
            max_cycles=cycles,
            source_attestation=REAL_SOURCE_ATTESTATION,
            minimum_latest_closed_candle_utc=minimum,
            authorization=SESSION_AUTHORIZATION,
            clock=self.clock,
            sleeper=self.clock.sleep,
            spot_capture_callable=overrides.get("spot", self.spot_capture),
            package_callable=overrides.get("package", self.package),
            microstructure_capture_callable=overrides.get("micro", self.micro_capture),
            microstructure_validate_callable=overrides.get("micro_validate", self.micro_validate),
            human_context_callable=overrides.get("human", self.human_context),
        )

    def test_01_next_capture_time(self):
        self.assertEqual(
            next_15m_capture_time(datetime(2026, 8, 10, 13, 47, tzinfo=timezone.utc)),
            datetime(2026, 8, 10, 14, 0, 5, tzinfo=timezone.utc),
        )

    def test_02_repair_limit(self):
        self.assertEqual(MAX_IMPLEMENTATION_OR_REPAIR_ATTEMPTS, 10)

    def test_03_cycle_limit(self):
        self.assertEqual(MAX_OBSERVATION_CYCLES, 8)

    def test_04_requests_per_cycle(self):
        self.assertEqual(EXPECTED_NETWORK_REQUESTS_PER_CYCLE, 8)

    def test_05_depth_contract(self):
        self.assertEqual(MICROSTRUCTURE_DEPTH_LIMIT, 1000)
        self.assertEqual(DEPTH_BANDS_BPS, (5, 10, 25, 50))
        self.assertEqual(REQUIRED_DEPTH_BANDS_BPS, (5, 10))

    def test_06_auth_required(self):
        self.err(
            "SESSION_AUTHORIZATION_REQUIRED",
            run_bounded_synchronized_15m_session,
            repo_root=self.repo,
            output_directory=self.external / "s",
            max_cycles=1,
            source_attestation=REAL_SOURCE_ATTESTATION,
            minimum_latest_closed_candle_utc=None,
        )

    def test_07_attestation_required(self):
        self.err(
            "SESSION_SOURCE_ATTESTATION_REQUIRED",
            run_bounded_synchronized_15m_session,
            repo_root=self.repo,
            output_directory=self.external / "s",
            max_cycles=1,
            source_attestation="NO",
            minimum_latest_closed_candle_utc=None,
            authorization=SESSION_AUTHORIZATION,
        )

    def test_08_cycle_zero_rejected(self):
        self.err(
            "SESSION_CYCLE_LIMIT_INVALID",
            run_bounded_synchronized_15m_session,
            repo_root=self.repo,
            output_directory=self.external / "s",
            max_cycles=0,
            source_attestation=REAL_SOURCE_ATTESTATION,
            minimum_latest_closed_candle_utc=None,
            authorization=SESSION_AUTHORIZATION,
        )

    def test_09_cycle_over_max_rejected(self):
        self.err(
            "SESSION_CYCLE_LIMIT_INVALID",
            run_bounded_synchronized_15m_session,
            repo_root=self.repo,
            output_directory=self.external / "s",
            max_cycles=9,
            source_attestation=REAL_SOURCE_ATTESTATION,
            minimum_latest_closed_candle_utc=None,
            authorization=SESSION_AUTHORIZATION,
        )

    def test_10_output_in_repo_rejected(self):
        self.err(
            "OUTPUT_INSIDE_REPOSITORY_PROHIBITED",
            run_bounded_synchronized_15m_session,
            repo_root=self.repo,
            output_directory=self.repo / "s",
            max_cycles=1,
            source_attestation=REAL_SOURCE_ATTESTATION,
            minimum_latest_closed_candle_utc=None,
            authorization=SESSION_AUTHORIZATION,
        )

    def test_11_existing_output_rejected(self):
        p = self.external / "s"
        p.mkdir()
        self.err(
            "OUTPUT_ALREADY_EXISTS",
            run_bounded_synchronized_15m_session,
            repo_root=self.repo,
            output_directory=p,
            max_cycles=1,
            source_attestation=REAL_SOURCE_ATTESTATION,
            minimum_latest_closed_candle_utc=None,
            authorization=SESSION_AUTHORIZATION,
        )

    def test_12_one_cycle_is_eight_requests(self):
        result = self.run_session()
        self.assertEqual(result["completed_cycles"], 1)
        self.assertEqual(result["network_request_count"], 8)
        self.assertTrue(result["synchronized"])

    def test_13_three_cycles_are_twenty_four_requests(self):
        result = self.run_session(3)
        self.assertEqual(result["completed_cycles"], 3)
        self.assertEqual(result["network_request_count"], 24)

    def test_14_stop_on_primary_candidate(self):
        self.candidate_at = 2
        result = self.run_session(3)
        self.assertEqual(result["completed_cycles"], 2)
        self.assertEqual(result["candidate_count"], 1)
        self.assertEqual(result["stop_reason"], "FIRST_PRIMARY_CANDIDATE_PENDING_HUMAN_REVIEW")

    def test_15_old_first_candle_rejected(self):
        def spot(**kwargs):
            self.spot_count += 1
            return self.write_spot_capture(
                Path(kwargs["output_directory"]),
                datetime(2026, 8, 10, 4, 29, 59, 999000, tzinfo=timezone.utc),
            )
        self.err("DUPLICATE_OR_OLD_CANDLE", self.run_session, 1, "2026-08-10T04:29:59.999000+00:00", spot=spot)

    def test_16_bad_spot_request_count_rejected(self):
        def spot(**kwargs):
            self.spot_count += 1
            return self.write_spot_capture(Path(kwargs["output_directory"]), self._close_for_index(1), request_count=2)
        self.err("SPOT_CAPTURE_MODE_INVALID", self.run_session, 1, spot=spot)

    def test_17_spot_permission_rejected(self):
        def spot(**kwargs):
            self.spot_count += 1
            return self.write_spot_capture(Path(kwargs["output_directory"]), self._close_for_index(1), unsafe=True)
        self.err("SPOT_CAPTURE_PERMISSION_INVALID", self.run_session, 1, spot=spot)

    def test_18_micro_request_count_rejected(self):
        def micro(**kwargs):
            result = self.micro_capture(**kwargs)
            result["request_count"] = 6
            return result
        self.err("MICROSTRUCTURE_REQUEST_COUNT_INVALID", self.run_session, 1, micro=micro)

    def test_19_micro_depth_limit_rejected(self):
        def micro(**kwargs):
            result = self.micro_capture(**kwargs)
            result["depth_limit_requested"] = 100
            return result
        self.err("MICROSTRUCTURE_DEPTH_LIMIT_INVALID", self.run_session, 1, micro=micro)

    def test_20_micro_permission_rejected(self):
        def micro(**kwargs):
            result = self.micro_capture(**kwargs)
            result["automation_allowed"] = True
            return result
        self.err("MICROSTRUCTURE_PERMISSION_INVALID", self.run_session, 1, micro=micro)

    def test_21_spot_futures_mismatch_rejected(self):
        self.mismatch_micro = True
        self.err("SPOT_FUTURES_CANDLE_MISMATCH", self.run_session, 1)

    def test_22_complete_bands_are_usable(self):
        summary = self._micro_summary(self._close_for_index(1))
        ctx = build_microstructure_context(summary)
        self.assertTrue(ctx["bands"]["5"]["usable_for_context"])
        self.assertTrue(ctx["bands"]["10"]["usable_for_context"])
        self.assertTrue(ctx["minimum_depth_context_usable"])

    def test_23_incomplete_bands_not_extrapolated(self):
        summary = self._micro_summary(self._close_for_index(1))
        ctx = build_microstructure_context(summary)
        self.assertFalse(ctx["bands"]["25"]["usable_for_context"])
        self.assertIsNone(ctx["bands"]["25"]["notional_imbalance_usable"])
        self.assertFalse(ctx["bands"]["50"]["usable_for_context"])
        self.assertIsNone(ctx["bands"]["50"]["notional_imbalance_usable"])

    def test_24_required_band_missing_marks_minimum_unusable(self):
        summary = self._micro_summary(self._close_for_index(1), incomplete_5=True)
        ctx = build_microstructure_context(summary)
        self.assertFalse(ctx["minimum_depth_context_usable"])
        self.assertFalse(ctx["bands"]["5"]["usable_for_context"])

    def test_25_microstructure_cannot_create_or_cancel_candidate(self):
        ctx = build_microstructure_context(self._micro_summary(self._close_for_index(1)))
        self.assertFalse(ctx["microstructure_can_create_candidate"])
        self.assertFalse(ctx["microstructure_can_cancel_candidate"])
        self.assertFalse(ctx["microstructure_can_modify_primary_rule"])

    def test_26_micro_validator_invoked(self):
        self.run_session()
        self.assertEqual(self.micro_validate_count, 1)

    def test_27_session_validation(self):
        result = self.run_session(2)
        validation = validate_synchronized_observation_session(result["output_directory"])
        self.assertEqual(validation["completed_cycles"], 2)
        self.assertEqual(validation["network_request_count"], 16)
        self.assertEqual(validation["manifest_entries"], 2)

    def test_28_official_artifacts_unchanged(self):
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

    def test_29_no_external_notifications(self):
        result = self.run_session()
        self.assertFalse(result["external_notifications_sent"])
        self.assertFalse(result["manual_confirmed"])

    def test_30_primary_evaluation_preserved_in_event(self):
        result = self.run_session()
        events = [
            json.loads(line)
            for line in (Path(result["output_directory"]) / "session_events.jsonl").read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        cycle = [e for e in events if e["event"] == "CYCLE_COMPLETED"][0]
        self.assertIn("failed_breakdown", cycle["primary_evaluation"])
        self.assertTrue(cycle["synchronization"]["closed_candle_match"])


if __name__ == "__main__":
    unittest.main()
