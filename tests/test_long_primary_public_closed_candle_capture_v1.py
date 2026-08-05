from __future__ import annotations

import csv
import json
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

import requests

from src.exchange.long_primary_public_closed_candle_capture_v1 import (
    CAPTURE_SCHEMA_VERSION,
    EXPECTED_SYMBOL,
    EXPECTED_TIMEFRAME,
    MANIFEST_FILENAME,
    METADATA_FILENAME,
    MINIMUM_CLOSED_ROWS,
    PUBLIC_SPOT_KLINES_URL,
    REAL_CAPTURE_AUTHORIZATION,
    REQUEST_LIMIT,
    SOURCE_COLUMNS,
    SOURCE_FILENAME,
    ClosedCandleCaptureError,
    capture_real_binance_public_closed_candles,
    validate_closed_candle_capture,
)

CAPTURE_TIME = datetime(2026, 8, 5, 0, 30, 0, tzinfo=timezone.utc)
INTERVAL_MS = 15 * 60 * 1000


class FakeResponse:
    def __init__(self, rows=None, error: Exception | None = None) -> None:
        self.rows = rows
        self.error = error

    def raise_for_status(self) -> None:
        if self.error is not None:
            raise self.error

    def json(self):
        if isinstance(self.rows, Exception):
            raise self.rows
        return self.rows


def prepare_repo(root: Path) -> None:
    (root / ".git").mkdir()
    data = root / "data" / "forward"
    data.mkdir(parents=True)
    (data / "long_forward_observation_dataset_v1.csv").write_bytes(
        b"header\n"
    )
    (
        data / "long_forward_observation_dataset_v1.manifest.csv"
    ).write_bytes(b"manifest\n")


def kline_rows(
    *,
    closed_count: int = 63,
    include_open: bool = True,
    latest_close_lag_minutes: int = 0,
) -> list[list[object]]:
    capture_ms = int(CAPTURE_TIME.timestamp() * 1000)
    latest_closed_close_ms = (
        capture_ms
        - 1
        - (latest_close_lag_minutes * 60 * 1000)
    )
    latest_closed_open_ms = latest_closed_close_ms - (INTERVAL_MS - 1)
    first_open_ms = latest_closed_open_ms - ((closed_count - 1) * INTERVAL_MS)
    rows: list[list[object]] = []
    for index in range(closed_count):
        open_ms = first_open_ms + (index * INTERVAL_MS)
        close_ms = open_ms + INTERVAL_MS - 1
        open_price = 60000.0 + index
        close_price = open_price + 5.0
        rows.append(
            [
                open_ms,
                str(open_price),
                str(close_price + 10.0),
                str(open_price - 10.0),
                str(close_price),
                "100.5",
                close_ms,
                "0",
                1,
                "0",
                "0",
                "0",
            ]
        )
    if include_open:
        open_ms = first_open_ms + (closed_count * INTERVAL_MS)
        rows.append(
            [
                open_ms,
                "61000",
                "61010",
                "60990",
                "61005",
                "50",
                open_ms + INTERVAL_MS - 1,
                "0",
                1,
                "0",
                "0",
                "0",
            ]
        )
    return rows


def run_capture(
    repo: Path,
    output: Path,
    rows=None,
    *,
    authorization: str | None = REAL_CAPTURE_AUTHORIZATION,
    response_error: Exception | None = None,
    request_error: Exception | None = None,
):
    fake = FakeResponse(
        rows=kline_rows() if rows is None else rows,
        error=response_error,
    )
    request_patch = patch(
        "src.exchange.long_primary_public_closed_candle_capture_v1.requests.get",
        side_effect=request_error,
    ) if request_error is not None else patch(
        "src.exchange.long_primary_public_closed_candle_capture_v1.requests.get",
        return_value=fake,
    )
    with patch(
        "src.exchange.long_primary_public_closed_candle_capture_v1._utc_now",
        return_value=CAPTURE_TIME,
    ), request_patch as mocked_get:
        result = capture_real_binance_public_closed_candles(
            repo_root=repo,
            output_directory=output,
            authorization=authorization,
        )
    return result, mocked_get


class LongPrimaryPublicClosedCandleCaptureTests(unittest.TestCase):
    def test_frozen_contract_constants_are_exact(self) -> None:
        self.assertEqual(EXPECTED_SYMBOL, "BTCUSDT")
        self.assertEqual(EXPECTED_TIMEFRAME, "15m")
        self.assertEqual(REQUEST_LIMIT, 64)
        self.assertEqual(MINIMUM_CLOSED_ROWS, 49)
        self.assertEqual(
            SOURCE_COLUMNS,
            (
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
            ),
        )

    def test_exact_authorization_is_required(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            repo = root / "repo"
            repo.mkdir()
            prepare_repo(repo)
            with self.assertRaises(ClosedCandleCaptureError) as caught:
                run_capture(repo, root / "capture", authorization=None)
            self.assertEqual(
                caught.exception.code,
                "REAL_CAPTURE_AUTHORIZATION_REQUIRED",
            )

    def test_output_inside_repository_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            repo = Path(temp) / "repo"
            repo.mkdir()
            prepare_repo(repo)
            with self.assertRaises(ClosedCandleCaptureError) as caught:
                run_capture(repo, repo / "capture")
            self.assertEqual(
                caught.exception.code,
                "OUTPUT_INSIDE_REPOSITORY_PROHIBITED",
            )

    def test_existing_output_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            repo = root / "repo"
            repo.mkdir()
            prepare_repo(repo)
            output = root / "capture"
            output.mkdir()
            with self.assertRaises(ClosedCandleCaptureError) as caught:
                run_capture(repo, output)
            self.assertEqual(caught.exception.code, "OUTPUT_ALREADY_EXISTS")

    def test_missing_output_parent_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            repo = root / "repo"
            repo.mkdir()
            prepare_repo(repo)
            with self.assertRaises(ClosedCandleCaptureError) as caught:
                run_capture(repo, root / "missing" / "capture")
            self.assertEqual(caught.exception.code, "OUTPUT_PARENT_INVALID")

    def test_successful_capture_excludes_open_candle(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            repo = root / "repo"
            repo.mkdir()
            prepare_repo(repo)
            result, _ = run_capture(repo, root / "capture")
            self.assertEqual(result["closed_candle_rows"], 63)
            self.assertEqual(result["open_candles_excluded"], 1)
            self.assertFalse(result["review_package_created"])

    def test_source_csv_has_exact_schema_and_no_bom(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            repo = root / "repo"
            repo.mkdir()
            prepare_repo(repo)
            output = root / "capture"
            run_capture(repo, output)
            payload = (output / SOURCE_FILENAME).read_bytes()
            self.assertFalse(payload.startswith(b"\xef\xbb\xbf"))
            with (output / SOURCE_FILENAME).open(
                "r", encoding="utf-8", newline=""
            ) as handle:
                reader = csv.DictReader(handle)
                self.assertEqual(tuple(reader.fieldnames or ()), SOURCE_COLUMNS)
                rows = list(reader)
            self.assertTrue(all(row["candle_closed"] == "True" for row in rows))

    def test_manifest_validation_passes(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            repo = root / "repo"
            repo.mkdir()
            prepare_repo(repo)
            output = root / "capture"
            run_capture(repo, output)
            validation = validate_closed_candle_capture(output)
            self.assertEqual(validation["manifest_entries"], 2)
            self.assertTrue((output / MANIFEST_FILENAME).is_file())

    def test_manifest_tamper_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            repo = root / "repo"
            repo.mkdir()
            prepare_repo(repo)
            output = root / "capture"
            run_capture(repo, output)
            (output / METADATA_FILENAME).write_text("{}\n", encoding="utf-8")
            with self.assertRaises(ClosedCandleCaptureError) as caught:
                validate_closed_candle_capture(output)
            self.assertEqual(caught.exception.code, "CAPTURE_HASH_MISMATCH")

    def test_official_artifacts_remain_unchanged(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            repo = root / "repo"
            repo.mkdir()
            prepare_repo(repo)
            dataset = repo / "data/forward/long_forward_observation_dataset_v1.csv"
            manifest = repo / "data/forward/long_forward_observation_dataset_v1.manifest.csv"
            before = (dataset.read_bytes(), manifest.read_bytes())
            run_capture(repo, root / "capture")
            self.assertEqual(before, (dataset.read_bytes(), manifest.read_bytes()))

    def test_request_contract_is_exact_and_single_call(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            repo = root / "repo"
            repo.mkdir()
            prepare_repo(repo)
            _, mocked_get = run_capture(repo, root / "capture")
            mocked_get.assert_called_once()
            args, kwargs = mocked_get.call_args
            self.assertEqual(args[0], PUBLIC_SPOT_KLINES_URL)
            self.assertEqual(
                kwargs["params"],
                {"symbol": "BTCUSDT", "interval": "15m", "limit": 64},
            )
            self.assertFalse(kwargs["allow_redirects"])

    def test_insufficient_closed_rows_is_rejected_without_output(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            repo = root / "repo"
            repo.mkdir()
            prepare_repo(repo)
            output = root / "capture"
            with self.assertRaises(ClosedCandleCaptureError) as caught:
                run_capture(
                    repo,
                    output,
                    rows=kline_rows(closed_count=48, include_open=True),
                )
            self.assertEqual(
                caught.exception.code,
                "CLOSED_CANDLE_WARMUP_INSUFFICIENT",
            )
            self.assertFalse(output.exists())

    def test_http_error_is_rejected_without_output(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            repo = root / "repo"
            repo.mkdir()
            prepare_repo(repo)
            output = root / "capture"
            with self.assertRaises(ClosedCandleCaptureError) as caught:
                run_capture(
                    repo,
                    output,
                    response_error=requests.HTTPError("500"),
                )
            self.assertEqual(caught.exception.code, "BINANCE_HTTP_ERROR")
            self.assertFalse(output.exists())

    def test_transport_exception_is_rejected_without_output(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            repo = root / "repo"
            repo.mkdir()
            prepare_repo(repo)
            output = root / "capture"
            with self.assertRaises(ClosedCandleCaptureError) as caught:
                run_capture(
                    repo,
                    output,
                    request_error=requests.Timeout("timeout"),
                )
            self.assertEqual(caught.exception.code, "BINANCE_HTTP_ERROR")
            self.assertFalse(output.exists())

    def test_invalid_json_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            repo = root / "repo"
            repo.mkdir()
            prepare_repo(repo)
            with self.assertRaises(ClosedCandleCaptureError) as caught:
                run_capture(repo, root / "capture", rows=ValueError("bad json"))
            self.assertEqual(
                caught.exception.code,
                "BINANCE_RESPONSE_JSON_INVALID",
            )

    def test_malformed_kline_shape_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            repo = root / "repo"
            repo.mkdir()
            prepare_repo(repo)
            rows = kline_rows()
            rows[10] = [1, 2, 3]
            with self.assertRaises(ClosedCandleCaptureError) as caught:
                run_capture(repo, root / "capture", rows=rows)
            self.assertEqual(
                caught.exception.code,
                "BINANCE_KLINE_SCHEMA_INVALID",
            )

    def test_unsorted_kline_times_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            repo = root / "repo"
            repo.mkdir()
            prepare_repo(repo)
            rows = kline_rows()
            rows[11] = list(rows[10])
            with self.assertRaises(ClosedCandleCaptureError) as caught:
                run_capture(repo, root / "capture", rows=rows)
            self.assertEqual(
                caught.exception.code,
                "BINANCE_KLINE_ORDER_INVALID",
            )

    def test_missing_interval_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            repo = root / "repo"
            repo.mkdir()
            prepare_repo(repo)
            rows = kline_rows()
            rows.pop(10)
            with self.assertRaises(ClosedCandleCaptureError) as caught:
                run_capture(repo, root / "capture", rows=rows)
            self.assertEqual(caught.exception.code, "BINANCE_KLINE_GAP_INVALID")

    def test_invalid_ohlc_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            repo = root / "repo"
            repo.mkdir()
            prepare_repo(repo)
            rows = kline_rows()
            rows[10][2] = "1"
            with self.assertRaises(ClosedCandleCaptureError) as caught:
                run_capture(repo, root / "capture", rows=rows)
            self.assertEqual(caught.exception.code, "BINANCE_KLINE_OHLC_INVALID")

    def test_stale_latest_closed_candle_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            repo = root / "repo"
            repo.mkdir()
            prepare_repo(repo)
            rows = kline_rows(
                closed_count=63,
                include_open=False,
                latest_close_lag_minutes=45,
            )
            with self.assertRaises(ClosedCandleCaptureError) as caught:
                run_capture(repo, root / "capture", rows=rows)
            self.assertEqual(
                caught.exception.code,
                "LATEST_CLOSED_CANDLE_STALE",
            )

    def test_metadata_keeps_all_permissions_false(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            repo = root / "repo"
            repo.mkdir()
            prepare_repo(repo)
            output = root / "capture"
            run_capture(repo, output)
            metadata = json.loads(
                (output / METADATA_FILENAME).read_text(encoding="utf-8")
            )
            self.assertEqual(
                metadata["capture_schema_version"],
                CAPTURE_SCHEMA_VERSION,
            )
            self.assertFalse(metadata["review_package_created"])
            self.assertFalse(metadata["candidate_evaluated"])
            for field in (
                "official_dataset_write_allowed",
                "official_append_allowed",
                "signal_generation_enabled",
                "live_alerts_allowed",
                "paper_trade_execution_allowed",
                "real_capital_allowed",
                "market_execution_allowed",
                "exchange_execution_allowed",
                "automation_allowed",
                "execution_allowed",
            ):
                self.assertIs(metadata[field], False)


if __name__ == "__main__":
    unittest.main()
