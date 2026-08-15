from __future__ import annotations

import json
import os
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from src.exchange.forward_outcome_future_closed_candle_source_v1 import (
    AUTHORIZATION,
    CAPABILITY,
    REQUIRED_CLOSED_ROWS,
    FutureClosedCandleSourceError,
    capture_forward_outcome_future_closed_candles_v1,
    validate_forward_outcome_future_closed_candle_capture_v1,
)

START = datetime(2026, 8, 10, 23, 45, tzinfo=timezone.utc)
MATURE = START + timedelta(minutes=15 * REQUIRED_CLOSED_ROWS, seconds=1)


class Response:
    def __init__(self, rows, status_code=200, json_error=False):
        self.rows = rows
        self.status_code = status_code
        self.json_error = json_error

    def json(self):
        if self.json_error:
            raise ValueError("bad json")
        return self.rows


def rows(
    *,
    start=START,
    count=REQUIRED_CLOSED_ROWS,
    gap_at=None,
    open_last=False,
    invalid_ohlc_at=None,
):
    out = []
    for index in range(count):
        actual_index = index + (1 if gap_at is not None and index >= gap_at else 0)
        open_time = start + timedelta(minutes=15 * actual_index)
        open_ms = int(open_time.timestamp() * 1000)
        close_ms = open_ms + (15 * 60 * 1000) - 1
        o = 64000.0 + index
        h = o + 10.0
        l = o - 10.0
        c = o + 2.0
        if invalid_ohlc_at == index:
            h = o - 1.0
        if open_last and index == count - 1:
            close_ms = int((MATURE + timedelta(minutes=30)).timestamp() * 1000)
        out.append(
            [
                open_ms,
                str(o),
                str(h),
                str(l),
                str(c),
                "12.5",
                close_ms,
            ]
        )
    return out


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
        ).write_text(
            "manifest\n",
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

    def _capture(self, name="capture", response_rows=None, **kwargs):
        calls = []

        def get(url, params=None, timeout=None):
            calls.append(
                {
                    "url": url,
                    "params": params,
                    "timeout": timeout,
                }
            )
            return Response(
                rows() if response_rows is None else response_rows
            )

        result = capture_forward_outcome_future_closed_candles_v1(
            repo_root=self.repo,
            output_directory=self.external / name,
            first_required_open_time_utc=START.isoformat(),
            authorization=AUTHORIZATION,
            request_get=get,
            clock=lambda: MATURE,
            **kwargs,
        )
        return result, calls

    def test_01_capability(self):
        self.assertEqual(
            CAPABILITY,
            "FORWARD_OUTCOME_FUTURE_CLOSED_CANDLE_SOURCE_V1",
        )

    def test_02_required_rows_17(self):
        self.assertEqual(REQUIRED_CLOSED_ROWS, 17)

    def test_03_exact_authorization(self):
        self.assertEqual(
            AUTHORIZATION,
            "CAPTURE_ONE_SHOT_FORWARD_OUTCOME_FUTURE_CLOSED_CANDLES_V1",
        )

    def test_04_missing_auth_rejected_before_output(self):
        out = self.external / "missing"
        with self.assertRaises(FutureClosedCandleSourceError):
            capture_forward_outcome_future_closed_candles_v1(
                repo_root=self.repo,
                output_directory=out,
                first_required_open_time_utc=START.isoformat(),
                authorization=None,
                request_get=lambda *a, **k: self.fail("request"),
                clock=lambda: MATURE,
            )
        self.assertFalse(out.exists())

    def test_05_old_spot_auth_rejected_before_request(self):
        calls = []
        with self.assertRaises(FutureClosedCandleSourceError):
            capture_forward_outcome_future_closed_candles_v1(
                repo_root=self.repo,
                output_directory=self.external / "old",
                first_required_open_time_utc=START.isoformat(),
                authorization="CAPTURE_ONE_SHOT_BINANCE_PUBLIC_CLOSED_CANDLES_V1",
                request_get=lambda *a, **k: calls.append(1),
                clock=lambda: MATURE,
            )
        self.assertEqual(calls, [])

    def test_06_output_inside_repo_rejected(self):
        with self.assertRaises(FutureClosedCandleSourceError):
            capture_forward_outcome_future_closed_candles_v1(
                repo_root=self.repo,
                output_directory=self.repo / "x",
                first_required_open_time_utc=START.isoformat(),
                authorization=AUTHORIZATION,
                request_get=lambda *a, **k: self.fail("request"),
                clock=lambda: MATURE,
            )

    def test_07_existing_output_rejected(self):
        out = self.external / "existing"
        out.mkdir()
        with self.assertRaises(FutureClosedCandleSourceError):
            capture_forward_outcome_future_closed_candles_v1(
                repo_root=self.repo,
                output_directory=out,
                first_required_open_time_utc=START.isoformat(),
                authorization=AUTHORIZATION,
                request_get=lambda *a, **k: self.fail("request"),
                clock=lambda: MATURE,
            )

    def test_08_start_must_be_aligned(self):
        with self.assertRaises(FutureClosedCandleSourceError):
            capture_forward_outcome_future_closed_candles_v1(
                repo_root=self.repo,
                output_directory=self.external / "unaligned",
                first_required_open_time_utc=(
                    START + timedelta(seconds=1)
                ).isoformat(),
                authorization=AUTHORIZATION,
                request_get=lambda *a, **k: self.fail("request"),
                clock=lambda: MATURE,
            )

    def test_09_horizon_must_be_mature(self):
        with self.assertRaises(FutureClosedCandleSourceError):
            capture_forward_outcome_future_closed_candles_v1(
                repo_root=self.repo,
                output_directory=self.external / "immature",
                first_required_open_time_utc=START.isoformat(),
                authorization=AUTHORIZATION,
                request_get=lambda *a, **k: self.fail("request"),
                clock=lambda: START + timedelta(hours=1),
            )

    def test_10_one_request_exact_params(self):
        _, calls = self._capture("params")
        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0]["params"]["symbol"], "BTCUSDT")
        self.assertEqual(calls[0]["params"]["interval"], "15m")
        self.assertEqual(calls[0]["params"]["limit"], 17)
        self.assertEqual(
            calls[0]["params"]["startTime"],
            int(START.timestamp() * 1000),
        )

    def test_11_success_row_count(self):
        result, _ = self._capture("rows")
        self.assertEqual(result["closed_row_count"], 17)
        self.assertEqual(result["network_request_count"], 1)

    def test_12_wrong_response_count_rejected(self):
        with self.assertRaises(FutureClosedCandleSourceError):
            self._capture("count", response_rows=rows(count=16))

    def test_13_wrong_first_start_rejected(self):
        with self.assertRaises(FutureClosedCandleSourceError):
            self._capture(
                "wrong-start",
                response_rows=rows(start=START + timedelta(minutes=15)),
            )

    def test_14_gap_rejected(self):
        with self.assertRaises(FutureClosedCandleSourceError):
            self._capture("gap", response_rows=rows(gap_at=8))

    def test_15_open_future_row_rejected(self):
        with self.assertRaises(FutureClosedCandleSourceError):
            self._capture(
                "open-last",
                response_rows=rows(open_last=True),
            )

    def test_16_invalid_ohlc_rejected(self):
        with self.assertRaises(FutureClosedCandleSourceError):
            self._capture(
                "ohlc",
                response_rows=rows(invalid_ohlc_at=3),
            )

    def test_17_http_error_rejected(self):
        def get(*args, **kwargs):
            return Response(rows(), status_code=500)

        with self.assertRaises(FutureClosedCandleSourceError):
            capture_forward_outcome_future_closed_candles_v1(
                repo_root=self.repo,
                output_directory=self.external / "http",
                first_required_open_time_utc=START.isoformat(),
                authorization=AUTHORIZATION,
                request_get=get,
                clock=lambda: MATURE,
            )

    def test_18_bad_json_rejected(self):
        def get(*args, **kwargs):
            return Response(rows(), json_error=True)

        with self.assertRaises(FutureClosedCandleSourceError):
            capture_forward_outcome_future_closed_candles_v1(
                repo_root=self.repo,
                output_directory=self.external / "json",
                first_required_open_time_utc=START.isoformat(),
                authorization=AUTHORIZATION,
                request_get=get,
                clock=lambda: MATURE,
            )

    def test_19_metadata_permissions_false(self):
        result, _ = self._capture("permissions")
        metadata = json.loads(
            Path(result["metadata_json"]).read_text(encoding="utf-8")
        )
        for field in (
            "official_dataset_write_allowed",
            "official_append_allowed",
            "signal_generation_enabled",
            "live_alerts_allowed",
            "paper_trade_execution_allowed",
            "real_capital_allowed",
            "execution_allowed",
        ):
            self.assertIs(metadata[field], False)

    def test_20_metadata_no_auth_account_order_ws(self):
        result, _ = self._capture("public")
        metadata = json.loads(
            Path(result["metadata_json"]).read_text(encoding="utf-8")
        )
        self.assertFalse(metadata["api_key_used"])
        self.assertFalse(metadata["authenticated_endpoint_used"])
        self.assertFalse(metadata["account_endpoint_used"])
        self.assertFalse(metadata["order_endpoint_used"])
        self.assertFalse(metadata["websocket_used"])

    def test_21_validation_roundtrip(self):
        result, _ = self._capture("roundtrip")
        validation = (
            validate_forward_outcome_future_closed_candle_capture_v1(
                result["output_directory"]
            )
        )
        self.assertEqual(validation["closed_row_count"], 17)
        self.assertTrue(
            validation[
                "sufficient_for_primary_and_next_boundary_context_horizon_16"
            ]
        )

    def test_22_manifest_tamper_detected(self):
        result, _ = self._capture("tamper")
        with Path(result["source_csv"]).open("ab") as handle:
            handle.write(b"x")
        with self.assertRaises(FutureClosedCandleSourceError):
            validate_forward_outcome_future_closed_candle_capture_v1(
                result["output_directory"]
            )

    def test_23_gate_enabled_rejected(self):
        os.environ[
            "TRADING_AI_OFFICIAL_LONG_EVIDENCE_APPEND_ALLOWED"
        ] = "1"
        out = self.external / "gate"
        with self.assertRaises(FutureClosedCandleSourceError):
            capture_forward_outcome_future_closed_candles_v1(
                repo_root=self.repo,
                output_directory=out,
                first_required_open_time_utc=START.isoformat(),
                authorization=AUTHORIZATION,
                request_get=lambda *a, **k: self.fail("request"),
                clock=lambda: MATURE,
            )
        self.assertFalse(out.exists())

    def test_24_official_artifacts_unchanged(self):
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
        self._capture("official")
        after = (dataset.read_bytes(), manifest.read_bytes())
        self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main(verbosity=2)
