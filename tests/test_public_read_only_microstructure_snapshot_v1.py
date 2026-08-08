from __future__ import annotations

import json
import os
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch
from urllib.parse import urlparse

from src.exchange.public_read_only_microstructure_snapshot_v1 import (
    AUTHORIZATION,
    FALSE_FIELDS,
    MicrostructureSnapshotError,
    _parse_depth,
    capture_public_read_only_microstructure_snapshot,
    validate_public_read_only_microstructure_snapshot,
)

FIXED = datetime(2026, 8, 8, 22, 0, 5, tzinfo=timezone.utc)
BOUNDARY = 1786226400000  # 2026-08-08T22:00:00Z
REF_CLOSE = BOUNDARY - 1
REF_OPEN = BOUNDARY - 15 * 60 * 1000

class Response:
    def __init__(self, payload, status_code=200):
        self._payload = payload
        self.status_code = status_code
    def json(self):
        return self._payload

def kline(open_ms, close_ms, o, h, l, c, v):
    return [open_ms, str(o), str(h), str(l), str(c), str(v), close_ms, "0", 10, "0", "0", "0"]

def payloads():
    return {
        "/fapi/v1/klines": [
            kline(REF_OPEN - 15*60*1000, REF_OPEN - 1, 64900, 65000, 64880, 64980, 100),
            kline(REF_OPEN, REF_CLOSE, 64980, 65050, 64970, 65020, 120),
            kline(BOUNDARY, BOUNDARY + 15*60*1000 - 1, 65020, 65030, 65010, 65025, 5),
        ],
        "/fapi/v1/depth": {
            "lastUpdateId": 123,
            "E": BOUNDARY + 2000,
            "T": BOUNDARY + 1900,
            "bids": [["65019.0", "2"], ["65010.0", "3"], ["64900.0", "1"]],
            "asks": [["65021.0", "1.5"], ["65030.0", "4"], ["65150.0", "2"]],
        },
        "/fapi/v1/openInterest": {
            "openInterest": "12000",
            "symbol": "BTCUSDT",
            "time": BOUNDARY + 2500,
        },
        "/fapi/v1/premiumIndex": {
            "symbol": "BTCUSDT",
            "markPrice": "65020",
            "indexPrice": "65000",
            "estimatedSettlePrice": "0",
            "lastFundingRate": "0.0001",
            "interestRate": "0.0001",
            "nextFundingTime": BOUNDARY + 8*60*60*1000,
            "time": BOUNDARY + 2600,
        },
        "/futures/data/openInterestHist": [
            {"symbol":"BTCUSDT","sumOpenInterest":"11800","sumOpenInterestValue":"767000000","CMCCirculatingSupply":"0","timestamp":BOUNDARY-15*60*1000},
            {"symbol":"BTCUSDT","sumOpenInterest":"12000","sumOpenInterestValue":"780000000","CMCCirculatingSupply":"0","timestamp":BOUNDARY},
        ],
        "/futures/data/takerlongshortRatio": [
            {"buySellRatio":"0.9","buyVol":"90","sellVol":"100","timestamp":BOUNDARY-30*60*1000},
            {"buySellRatio":"1.2","buyVol":"120","sellVol":"100","timestamp":BOUNDARY-15*60*1000},
        ],
        "/futures/data/globalLongShortAccountRatio": [
            {"symbol":"BTCUSDT","longShortRatio":"1.1","longAccount":"0.5238","shortAccount":"0.4762","timestamp":BOUNDARY-15*60*1000},
            {"symbol":"BTCUSDT","longShortRatio":"1.2","longAccount":"0.5455","shortAccount":"0.4545","timestamp":BOUNDARY},
        ],
    }

class MockGet:
    def __init__(self, override=None, fail_path=None):
        self.data = payloads()
        if override:
            self.data.update(override)
        self.calls = []
        self.fail_path = fail_path
    def __call__(self, url, *, params, timeout):
        path = urlparse(url).path
        self.calls.append((path, dict(params), timeout))
        if self.fail_path == path:
            return Response({"error":"x"}, 500)
        return Response(self.data[path], 200)

class Tests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        self.repo = root / "repo"
        self.repo.mkdir()
        (self.repo / ".git").mkdir()
        official = self.repo / "data" / "forward"
        official.mkdir(parents=True)
        (official / "long_forward_observation_dataset_v1.csv").write_bytes(b"header\n")
        (official / "long_forward_observation_dataset_v1.manifest.csv").write_bytes(b"manifest\n")
        self.external = root / "external"
        self.external.mkdir()
        os.environ.pop("TRADING_AI_OFFICIAL_LONG_EVIDENCE_APPEND_ALLOWED", None)

    def tearDown(self):
        os.environ.pop("TRADING_AI_OFFICIAL_LONG_EVIDENCE_APPEND_ALLOWED", None)
        self.tmp.cleanup()

    def run_capture(self, get=None, name="snap"):
        get = get or MockGet()
        out = self.external / name
        result = capture_public_read_only_microstructure_snapshot(
            repo_root=self.repo,
            output_directory=out,
            authorization=AUTHORIZATION,
            request_get=get,
            clock=lambda: FIXED,
        )
        return out, result, get

    def test_01_authorization_required(self):
        with self.assertRaises(MicrostructureSnapshotError):
            capture_public_read_only_microstructure_snapshot(
                repo_root=self.repo, output_directory=self.external/"x",
                authorization=None, request_get=MockGet(), clock=lambda: FIXED,
            )

    def test_02_gate_must_be_off(self):
        os.environ["TRADING_AI_OFFICIAL_LONG_EVIDENCE_APPEND_ALLOWED"] = "1"
        with self.assertRaises(MicrostructureSnapshotError):
            capture_public_read_only_microstructure_snapshot(
                repo_root=self.repo, output_directory=self.external/"x",
                authorization=AUTHORIZATION, request_get=MockGet(), clock=lambda: FIXED,
            )

    def test_03_output_inside_repo_rejected(self):
        with self.assertRaises(MicrostructureSnapshotError):
            capture_public_read_only_microstructure_snapshot(
                repo_root=self.repo, output_directory=self.repo/"x",
                authorization=AUTHORIZATION, request_get=MockGet(), clock=lambda: FIXED,
            )

    def test_04_existing_output_rejected(self):
        out = self.external/"x"; out.mkdir()
        with self.assertRaises(MicrostructureSnapshotError):
            capture_public_read_only_microstructure_snapshot(
                repo_root=self.repo, output_directory=out,
                authorization=AUTHORIZATION, request_get=MockGet(), clock=lambda: FIXED,
            )

    def test_05_exactly_seven_get_requests(self):
        out, result, get = self.run_capture()
        self.assertEqual(result["request_count"], 7)
        self.assertEqual(len(get.calls), 7)

    def test_06_endpoint_sequence(self):
        out, result, get = self.run_capture()
        self.assertEqual([x[0] for x in get.calls], [
            "/fapi/v1/klines", "/fapi/v1/depth", "/fapi/v1/openInterest",
            "/fapi/v1/premiumIndex", "/futures/data/openInterestHist",
            "/futures/data/takerlongshortRatio", "/futures/data/globalLongShortAccountRatio",
        ])

    def test_07_no_api_key_header_path(self):
        out, _, _ = self.run_capture()
        log = json.loads((out/"request_log.json").read_text())
        self.assertTrue(all(x["api_key_header_sent"] is False and x["authenticated"] is False for x in log))

    def test_08_latest_open_kline_excluded(self):
        out, result, _ = self.run_capture()
        self.assertEqual(result["reference_closed_candle_utc"], "2026-08-08T21:59:59.999000+00:00")

    def test_09_stale_reference_rejected(self):
        old = payloads()
        old["/fapi/v1/klines"] = [
            kline(BOUNDARY-60*60*1000, BOUNDARY-45*60*1000-1, 1,2,1,2,1),
            kline(BOUNDARY-45*60*1000, BOUNDARY-30*60*1000-1, 1,2,1,2,1),
        ]
        with self.assertRaises(MicrostructureSnapshotError):
            self.run_capture(MockGet(override={"/fapi/v1/klines": old["/fapi/v1/klines"]}))

    def test_10_crossed_book_rejected(self):
        bad = payloads()["/fapi/v1/depth"].copy()
        bad["bids"] = [["65022","1"]]
        bad["asks"] = [["65021","1"]]
        with self.assertRaises(MicrostructureSnapshotError):
            self.run_capture(MockGet(override={"/fapi/v1/depth": bad}))

    def test_11_depth_metrics(self):
        out, _, _ = self.run_capture()
        s = json.loads((out/"microstructure_snapshot.json").read_text())
        self.assertAlmostEqual(s["order_book"]["best_bid"], 65019.0)
        self.assertAlmostEqual(s["order_book"]["best_ask"], 65021.0)
        self.assertGreater(s["order_book"]["spread_bps"], 0)

    def test_12_depth_imbalance_is_numeric(self):
        out, _, _ = self.run_capture()
        s = json.loads((out/"microstructure_snapshot.json").read_text())
        value = s["order_book"]["bands"]["10"]["notional_imbalance"]
        self.assertTrue(-1 <= value <= 1)

    def test_13_open_interest_change(self):
        out, result, _ = self.run_capture()
        self.assertAlmostEqual(result["open_interest_change_15m_percent"], (200/11800)*100)

    def test_14_funding_and_basis(self):
        out, result, _ = self.run_capture()
        s = json.loads((out/"microstructure_snapshot.json").read_text())
        self.assertAlmostEqual(result["last_funding_rate"], 0.0001)
        self.assertAlmostEqual(s["mark_price_funding"]["mark_index_basis_bps"], (20/65000)*10000)

    def test_15_taker_ratio(self):
        out, result, _ = self.run_capture()
        self.assertAlmostEqual(result["taker_buy_sell_ratio"], 1.2)

    def test_16_global_ratio(self):
        out, result, _ = self.run_capture()
        self.assertAlmostEqual(result["global_long_short_account_ratio"], 1.2)

    def test_17_false_permissions(self):
        out, _, _ = self.run_capture()
        s = json.loads((out/"microstructure_snapshot.json").read_text())
        for field in FALSE_FIELDS:
            self.assertIs(s[field], False)

    def test_18_transactional_failure_cleans_output(self):
        get = MockGet(fail_path="/fapi/v1/openInterest")
        out = self.external/"broken"
        with self.assertRaises(MicrostructureSnapshotError):
            capture_public_read_only_microstructure_snapshot(
                repo_root=self.repo, output_directory=out,
                authorization=AUTHORIZATION, request_get=get, clock=lambda: FIXED,
            )
        self.assertFalse(out.exists())

    def test_19_official_artifacts_unchanged(self):
        before = (self.repo/"data/forward/long_forward_observation_dataset_v1.csv").read_bytes()
        self.run_capture()
        after = (self.repo/"data/forward/long_forward_observation_dataset_v1.csv").read_bytes()
        self.assertEqual(before, after)

    def test_20_validation_success(self):
        out, _, _ = self.run_capture()
        v = validate_public_read_only_microstructure_snapshot(out)
        self.assertEqual(v["request_count"], 7)
        self.assertEqual(v["manifest_entries"], 3)

    def test_21_validation_detects_tamper(self):
        out, _, _ = self.run_capture()
        with (out/"microstructure_snapshot.json").open("ab") as handle:
            handle.write(b"x")
        with self.assertRaises(MicrostructureSnapshotError):
            validate_public_read_only_microstructure_snapshot(out)

    def test_22_interpretation_constraints(self):
        out, _, _ = self.run_capture()
        s = json.loads((out/"microstructure_snapshot.json").read_text())
        c = s["interpretation_constraints"]
        self.assertTrue(c["context_only"])
        self.assertTrue(c["does_not_modify_frozen_long_rule"])
        self.assertTrue(c["order_book_does_not_reveal_hidden_stops_or_liquidations"])
        self.assertTrue(c["top_trader_ratios_excluded_because_current_docs_require_api_key"])

if __name__ == "__main__":
    unittest.main(verbosity=2)
