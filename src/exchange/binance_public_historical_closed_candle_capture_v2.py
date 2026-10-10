from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import os
import shutil
import sys
import uuid
from datetime import datetime, timedelta, timezone
from io import StringIO
from pathlib import Path
from typing import Any, Mapping, Sequence

import requests


CAPABILITY = "BINANCE_PUBLIC_HISTORICAL_CLOSED_CANDLE_CAPTURE_V2"
IMPLEMENTATION_SCHEMA_VERSION = (
    "BINANCE_PUBLIC_HISTORICAL_CLOSED_CANDLE_CAPTURE_IMPLEMENTATION_V2"
)
CAPTURE_SCHEMA_VERSION = (
    "BINANCE_PUBLIC_HISTORICAL_CLOSED_CANDLE_CAPTURE_V2"
)
PROVIDER = "BINANCE_PUBLIC_SPOT_API"
PUBLIC_SPOT_KLINES_URL = "https://api.binance.com/api/v3/klines"

EXPECTED_SYMBOL = "BTCUSDT"
EXPECTED_TIMEFRAME = "15m"
BAR = timedelta(minutes=15)
BAR_MILLISECONDS = 15 * 60 * 1000
CLOSE_OFFSET_MILLISECONDS = BAR_MILLISECONDS - 1
EXPECTED_HISTORICAL_ROW_COUNT = 17
REQUEST_TIMEOUT_SECONDS = 20

AUTOMATED_CAPTURE_AUTHORIZATION = (
    "AUTOMATED_PUBLIC_READ_ONLY_MARKET_DATA_CAPTURE_V1"
)

OFFICIAL_DATASET_RELATIVE_PATH = Path(
    "data/forward/long_forward_observation_dataset_v1.csv"
)
OFFICIAL_MANIFEST_RELATIVE_PATH = Path(
    "data/forward/long_forward_observation_dataset_v1.manifest.csv"
)
OFFICIAL_LOCK_RELATIVE_PATH = Path(
    "data/forward/long_forward_observation_dataset_v1.lock"
)

SOURCE_FILENAME = "btc_usdt_15m_historical_closed_candles.csv"
METADATA_FILENAME = "historical_capture_metadata.json"
MANIFEST_FILENAME = "manifest.sha256"

SOURCE_COLUMNS = (
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
)


class HistoricalClosedCandleCaptureError(RuntimeError):
    def __init__(self, code: str, message: str) -> None:
        self.code = code
        super().__init__(message)


def _require(condition: bool, code: str, message: str) -> None:
    if not condition:
        raise HistoricalClosedCandleCaptureError(code, message)


def _sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _canonical_json_bytes(value: Mapping[str, Any]) -> bytes:
    return (
        json.dumps(
            dict(value),
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
            allow_nan=False,
        )
        + "\n"
    ).encode("utf-8")


def _parse_utc(value: datetime | str) -> datetime:
    if isinstance(value, datetime):
        parsed = value
    else:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    _require(
        parsed.tzinfo is not None,
        "TIMESTAMP_TIMEZONE_REQUIRED",
        "Timestamp must include a timezone.",
    )
    return parsed.astimezone(timezone.utc)


def _utc_text(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat()


def _milliseconds_to_utc_text(value: int) -> str:
    return _utc_text(
        datetime.fromtimestamp(value / 1000, tz=timezone.utc)
    )


def _milliseconds(value: datetime) -> int:
    return int(value.timestamp() * 1000)


def _aligned_open(value: datetime) -> bool:
    return (
        value.second == 0
        and value.microsecond == 0
        and value.minute % 15 == 0
    )


def _integer(value: Any, field: str, row_number: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError) as exc:
        raise HistoricalClosedCandleCaptureError(
            "BINANCE_KLINE_TIME_INVALID",
            f"Invalid {field} at row {row_number}.",
        ) from exc


def _number(value: Any, field: str, row_number: int) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise HistoricalClosedCandleCaptureError(
            "BINANCE_KLINE_NUMERIC_INVALID",
            f"Invalid {field} at row {row_number}.",
        ) from exc
    _require(
        math.isfinite(number),
        "BINANCE_KLINE_NUMERIC_INVALID",
        f"Non-finite {field} at row {row_number}.",
    )
    return number


def _number_text(value: float) -> str:
    text = format(float(value), ".10f").rstrip("0").rstrip(".")
    return text if text not in {"", "-0"} else "0"


def _is_relative_to(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
    except ValueError:
        return False
    return True


def _official_hashes(repo: Path) -> dict[str, str]:
    dataset = repo / OFFICIAL_DATASET_RELATIVE_PATH
    manifest = repo / OFFICIAL_MANIFEST_RELATIVE_PATH
    lock = repo / OFFICIAL_LOCK_RELATIVE_PATH
    _require(
        dataset.is_file() and not dataset.is_symlink(),
        "OFFICIAL_DATASET_MISSING",
        "Official dataset is missing or invalid.",
    )
    _require(
        manifest.is_file() and not manifest.is_symlink(),
        "OFFICIAL_MANIFEST_MISSING",
        "Official manifest is missing or invalid.",
    )
    _require(
        not lock.exists() and not lock.is_symlink(),
        "OFFICIAL_APPEND_LOCK_PRESENT",
        "Official append lock is present.",
    )
    return {
        "dataset_sha256": _sha256_path(dataset),
        "manifest_sha256": _sha256_path(manifest),
    }


def _normalize_rows(
    raw_rows: Any,
    start_open: datetime,
    end_open: datetime,
    captured_at: datetime,
) -> list[dict[str, str]]:
    _require(
        isinstance(raw_rows, list),
        "BINANCE_RESPONSE_SCHEMA_INVALID",
        "Binance response must be a list.",
    )
    _require(
        len(raw_rows) == EXPECTED_HISTORICAL_ROW_COUNT,
        "HISTORICAL_ROW_COUNT_INVALID",
        "Historical response must contain exactly 17 rows.",
    )

    captured_ms = _milliseconds(captured_at)
    start_ms = _milliseconds(start_open)
    normalized: list[dict[str, str]] = []

    for row_number, raw in enumerate(raw_rows, start=1):
        _require(
            isinstance(raw, (list, tuple)) and len(raw) >= 7,
            "BINANCE_KLINE_SCHEMA_INVALID",
            f"Row {row_number} is not a Binance kline.",
        )
        open_ms = _integer(raw[0], "open_time", row_number)
        close_ms = _integer(raw[6], "close_time", row_number)
        expected_open_ms = (
            start_ms + (row_number - 1) * BAR_MILLISECONDS
        )

        _require(
            open_ms == expected_open_ms,
            "HISTORICAL_OPEN_TIME_SEQUENCE_INVALID",
            f"Unexpected open time at row {row_number}.",
        )
        _require(
            close_ms - open_ms == CLOSE_OFFSET_MILLISECONDS,
            "BINANCE_KLINE_INTERVAL_INVALID",
            f"Row {row_number} is not an exact 15m candle.",
        )
        _require(
            close_ms <= captured_ms,
            "HISTORICAL_OPEN_CANDLE_PRESENT",
            f"Row {row_number} was not closed at capture time.",
        )

        open_price = _number(raw[1], "open", row_number)
        high = _number(raw[2], "high", row_number)
        low = _number(raw[3], "low", row_number)
        close = _number(raw[4], "close", row_number)
        volume = _number(raw[5], "volume", row_number)

        _require(
            min(open_price, high, low, close) > 0 and volume >= 0,
            "BINANCE_KLINE_RANGE_INVALID",
            f"Invalid price or volume at row {row_number}.",
        )
        _require(
            high >= max(open_price, close)
            and low <= min(open_price, close)
            and high >= low,
            "BINANCE_KLINE_OHLC_INVALID",
            f"OHLC structure invalid at row {row_number}.",
        )

        normalized.append(
            {
                "open_time_utc": _milliseconds_to_utc_text(open_ms),
                "close_time_utc": _milliseconds_to_utc_text(close_ms),
                "symbol": EXPECTED_SYMBOL,
                "timeframe": EXPECTED_TIMEFRAME,
                "open": _number_text(open_price),
                "high": _number_text(high),
                "low": _number_text(low),
                "close": _number_text(close),
                "volume": _number_text(volume),
                "candle_closed": "True",
            }
        )

    _require(
        normalized[0]["open_time_utc"] == _utc_text(start_open),
        "HISTORICAL_START_BOUNDARY_MISMATCH",
        "First historical candle does not match requested start.",
    )
    _require(
        normalized[-1]["open_time_utc"] == _utc_text(end_open),
        "HISTORICAL_END_BOUNDARY_MISMATCH",
        "Last historical candle does not match requested end.",
    )
    return normalized


def _source_csv_bytes(
    rows: Sequence[Mapping[str, str]],
) -> bytes:
    output = StringIO(newline="")
    writer = csv.DictWriter(
        output,
        fieldnames=list(SOURCE_COLUMNS),
        lineterminator="\n",
        extrasaction="raise",
    )
    writer.writeheader()
    for row in rows:
        writer.writerow(
            {field: row[field] for field in SOURCE_COLUMNS}
        )
    return output.getvalue().encode("utf-8")


def _write_bytes_create_only(path: Path, payload: bytes) -> None:
    with path.open("xb") as handle:
        handle.write(payload)
        handle.flush()
        os.fsync(handle.fileno())


def _write_manifest(directory: Path) -> None:
    names = (SOURCE_FILENAME, METADATA_FILENAME)
    payload = (
        "\n".join(
            f"{_sha256_path(directory / name)}  {name}"
            for name in sorted(names)
        )
        + "\n"
    ).encode("utf-8")
    _write_bytes_create_only(
        directory / MANIFEST_FILENAME,
        payload,
    )


def validate_historical_closed_candle_capture(
    directory: Path | str,
) -> dict[str, Any]:
    root = Path(directory).resolve()
    _require(
        root.is_dir() and not root.is_symlink(),
        "CAPTURE_DIRECTORY_INVALID",
        "Capture directory is invalid.",
    )

    manifest = root / MANIFEST_FILENAME
    _require(
        manifest.is_file() and not manifest.is_symlink(),
        "CAPTURE_MANIFEST_MISSING",
        "Capture manifest is missing.",
    )

    manifest_lines = manifest.read_text(
        encoding="utf-8"
    ).splitlines()
    _require(
        len(manifest_lines) == 2,
        "CAPTURE_MANIFEST_INVALID",
        "Capture manifest must contain exactly two entries.",
    )

    manifest_names: list[str] = []
    for line in manifest_lines:
        parts = line.split("  ", 1)
        _require(
            len(parts) == 2 and len(parts[0]) == 64,
            "CAPTURE_MANIFEST_INVALID",
            "Capture manifest line is invalid.",
        )
        expected_hash, name = parts
        file_path = root / name
        _require(
            file_path.is_file() and not file_path.is_symlink(),
            "CAPTURE_FILE_MISSING",
            f"Capture file is missing: {name}.",
        )
        _require(
            _sha256_path(file_path) == expected_hash,
            "CAPTURE_HASH_MISMATCH",
            f"Capture hash mismatch: {name}.",
        )
        manifest_names.append(name)

    _require(
        sorted(manifest_names)
        == sorted([SOURCE_FILENAME, METADATA_FILENAME]),
        "CAPTURE_SCOPE_INVALID",
        "Capture manifest file scope is invalid.",
    )

    source_path = root / SOURCE_FILENAME
    source_payload = source_path.read_bytes()
    _require(
        not source_payload.startswith(b"\xef\xbb\xbf"),
        "CAPTURE_SOURCE_ENCODING_INVALID",
        "Capture CSV must not contain a UTF-8 BOM.",
    )

    reader = csv.DictReader(
        source_payload.decode("utf-8").splitlines()
    )
    _require(
        tuple(reader.fieldnames or ()) == SOURCE_COLUMNS,
        "CAPTURE_SOURCE_SCHEMA_INVALID",
        "Capture CSV columns are invalid.",
    )
    rows = list(reader)
    _require(
        len(rows) == EXPECTED_HISTORICAL_ROW_COUNT,
        "CAPTURE_SOURCE_ROWS_INVALID",
        "Capture CSV must contain exactly 17 rows.",
    )
    _require(
        all(row["candle_closed"] == "True" for row in rows),
        "CAPTURE_OPEN_CANDLE_PRESENT",
        "Capture CSV contains an open candle.",
    )

    opens = [
        _parse_utc(row["open_time_utc"]) for row in rows
    ]
    _require(
        all(
            later - earlier == BAR
            for earlier, later in zip(opens, opens[1:])
        ),
        "CAPTURE_SOURCE_SPACING_INVALID",
        "Historical candles are not exactly 15m apart.",
    )

    metadata = json.loads(
        (root / METADATA_FILENAME).read_text(encoding="utf-8")
    )
    _require(
        metadata["capture_schema_version"]
        == CAPTURE_SCHEMA_VERSION,
        "CAPTURE_METADATA_SCHEMA_INVALID",
        "Capture metadata schema is invalid.",
    )
    _require(
        metadata["source_artifact_sha256"]
        == _sha256_bytes(source_payload),
        "CAPTURE_METADATA_HASH_INVALID",
        "Capture metadata source hash is invalid.",
    )
    _require(
        metadata["historical_range_exact"] is True,
        "HISTORICAL_RANGE_CONTRACT_INVALID",
        "Capture is not marked as an exact historical range.",
    )
    _require(
        metadata["automated_public_read_only_capture"] is True,
        "AUTOMATED_CAPTURE_CONTRACT_INVALID",
        "Automated public read-only capture is not certified.",
    )
    _require(
        metadata["human_attestation_required"] is False,
        "HUMAN_ATTESTATION_CONTRACT_INVALID",
        "Historical capture unexpectedly requires human attestation.",
    )
    _require(
        metadata["official_append_executed"] is False,
        "OFFICIAL_APPEND_CONTRACT_INVALID",
        "Historical capture reports an official append.",
    )
    _require(
        metadata["network_request_count"] == 1,
        "NETWORK_REQUEST_COUNT_INVALID",
        "Historical capture must use exactly one request.",
    )
    _require(
        _parse_utc(metadata["requested_start_open_utc"])
        == opens[0],
        "METADATA_START_BOUNDARY_MISMATCH",
        "Metadata start boundary does not match CSV.",
    )
    _require(
        _parse_utc(metadata["requested_end_open_utc"])
        == opens[-1],
        "METADATA_END_BOUNDARY_MISMATCH",
        "Metadata end boundary does not match CSV.",
    )

    return {
        "capture_id": metadata["capture_id"],
        "closed_candle_rows": len(rows),
        "first_open_utc": rows[0]["open_time_utc"],
        "last_open_utc": rows[-1]["open_time_utc"],
        "source_artifact_sha256": metadata[
            "source_artifact_sha256"
        ],
        "manifest_entries": len(manifest_lines),
        "historical_range_exact": True,
    }


def capture_real_binance_public_historical_closed_candles(
    *,
    repo_root: Path | str,
    output_directory: Path | str,
    start_open_utc: datetime | str,
    end_open_utc: datetime | str,
    authorization: str | None = None,
) -> dict[str, Any]:
    _require(
        authorization == AUTOMATED_CAPTURE_AUTHORIZATION,
        "AUTOMATED_CAPTURE_AUTHORIZATION_REQUIRED",
        "Exact automated public read-only authorization is required.",
    )

    repo = Path(repo_root).resolve()
    output = Path(output_directory).resolve()
    start_open = _parse_utc(start_open_utc)
    end_open = _parse_utc(end_open_utc)

    _require(
        (repo / ".git").is_dir(),
        "REPOSITORY_ROOT_INVALID",
        "Repository root is invalid.",
    )
    _require(
        _aligned_open(start_open) and _aligned_open(end_open),
        "HISTORICAL_BOUNDARY_ALIGNMENT_INVALID",
        "Historical boundaries must align to exact 15m opens.",
    )
    _require(
        end_open >= start_open,
        "HISTORICAL_BOUNDARY_ORDER_INVALID",
        "Historical end must not precede start.",
    )

    expected_rows = (
        int((end_open - start_open).total_seconds())
        // int(BAR.total_seconds())
        + 1
    )
    _require(
        expected_rows == EXPECTED_HISTORICAL_ROW_COUNT,
        "HISTORICAL_EXPECTED_ROW_COUNT_INVALID",
        "Historical contract requires exactly 17 candles.",
    )
    _require(
        datetime.now(timezone.utc) >= end_open + BAR,
        "HISTORICAL_RANGE_NOT_MATURED",
        "Requested historical range is not fully closed.",
    )
    _require(
        not _is_relative_to(output, repo),
        "OUTPUT_INSIDE_REPOSITORY_PROHIBITED",
        "Capture output must remain outside the repository.",
    )
    _require(
        output.parent.is_dir() and not output.parent.is_symlink(),
        "OUTPUT_PARENT_INVALID",
        "Capture parent must be an existing regular directory.",
    )
    _require(
        not output.exists() and not output.is_symlink(),
        "OUTPUT_ALREADY_EXISTS",
        "Capture output already exists.",
    )

    official_before = _official_hashes(repo)
    captured_at = datetime.now(timezone.utc)
    start_ms = _milliseconds(start_open)
    end_ms = (
        _milliseconds(end_open) + CLOSE_OFFSET_MILLISECONDS
    )

    try:
        response = requests.get(
            PUBLIC_SPOT_KLINES_URL,
            params={
                "symbol": EXPECTED_SYMBOL,
                "interval": EXPECTED_TIMEFRAME,
                "startTime": start_ms,
                "endTime": end_ms,
                "limit": EXPECTED_HISTORICAL_ROW_COUNT,
            },
            timeout=REQUEST_TIMEOUT_SECONDS,
            allow_redirects=False,
            headers={
                "Accept": "application/json",
                "User-Agent": (
                    "Trading-AI-Historical-Closed-Candle-Capture-V2"
                ),
            },
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        raise HistoricalClosedCandleCaptureError(
            "BINANCE_HTTP_ERROR",
            "Binance public historical kline request failed.",
        ) from exc

    try:
        raw_rows = response.json()
    except ValueError as exc:
        raise HistoricalClosedCandleCaptureError(
            "BINANCE_RESPONSE_JSON_INVALID",
            "Binance response is not valid JSON.",
        ) from exc

    rows = _normalize_rows(
        raw_rows,
        start_open,
        end_open,
        captured_at,
    )
    source_payload = _source_csv_bytes(rows)
    source_sha256 = _sha256_bytes(source_payload)

    capture_id = (
        "HISTCAP_"
        + _sha256_bytes(
            _canonical_json_bytes(
                {
                    "captured_at_utc": _utc_text(captured_at),
                    "requested_start_open_utc": _utc_text(start_open),
                    "requested_end_open_utc": _utc_text(end_open),
                    "source_artifact_sha256": source_sha256,
                }
            )
        )[:24].upper()
    )

    metadata: dict[str, Any] = {
        "capture_schema_version": CAPTURE_SCHEMA_VERSION,
        "implementation_schema_version": (
            IMPLEMENTATION_SCHEMA_VERSION
        ),
        "capability": CAPABILITY,
        "capture_id": capture_id,
        "capture_mode": "AUTOMATED_EXACT_HISTORICAL_RANGE",
        "provider": PROVIDER,
        "endpoint": PUBLIC_SPOT_KLINES_URL,
        "symbol": EXPECTED_SYMBOL,
        "timeframe": EXPECTED_TIMEFRAME,
        "request_start_time_ms": start_ms,
        "request_end_time_ms": end_ms,
        "request_limit": EXPECTED_HISTORICAL_ROW_COUNT,
        "requested_start_open_utc": _utc_text(start_open),
        "requested_end_open_utc": _utc_text(end_open),
        "captured_at_utc": _utc_text(captured_at),
        "closed_candle_rows": len(rows),
        "network_request_count": 1,
        "source_artifact": SOURCE_FILENAME,
        "source_artifact_sha256": source_sha256,
        "historical_range_exact": True,
        "automated_public_read_only_capture": True,
        "human_attestation_required": False,
        "lookahead_beyond_preregistered_h16_used": False,
        "authenticated_endpoint_used": False,
        "exchange_credentials_used": False,
        "official_dataset_write_performed": False,
        "official_manifest_write_performed": False,
        "official_append_executed": False,
        "quality_gate_evaluated": False,
        "edge_established": False,
        "signal_generated": False,
        "order_endpoint_used": False,
        "paper_trade_execution_allowed": False,
        "real_capital_allowed": False,
        "market_execution_allowed": False,
    }

    temporary = (
        output.parent
        / f".{output.name}.{uuid.uuid4().hex}.tmp"
    )
    _require(
        not temporary.exists() and not temporary.is_symlink(),
        "TEMPORARY_OUTPUT_COLLISION",
        "Temporary output already exists.",
    )

    try:
        temporary.mkdir()
        _write_bytes_create_only(
            temporary / SOURCE_FILENAME,
            source_payload,
        )
        _write_bytes_create_only(
            temporary / METADATA_FILENAME,
            _canonical_json_bytes(metadata),
        )
        _write_manifest(temporary)
        validate_historical_closed_candle_capture(temporary)
        os.replace(temporary, output)
    except Exception:
        if temporary.exists():
            shutil.rmtree(temporary, ignore_errors=True)
        raise

    try:
        official_after = _official_hashes(repo)
        _require(
            official_after == official_before,
            "OFFICIAL_ARTIFACT_CHANGED",
            "Official dataset or manifest changed during capture.",
        )
        validation = validate_historical_closed_candle_capture(
            output
        )
    except Exception:
        if output.exists():
            shutil.rmtree(output, ignore_errors=True)
        raise

    return {
        "capability": CAPABILITY,
        "capture_id": capture_id,
        "output_directory": str(output),
        "source_csv": str(output / SOURCE_FILENAME),
        "metadata_json": str(output / METADATA_FILENAME),
        "source_artifact_sha256": source_sha256,
        "closed_candle_rows": len(rows),
        "first_open_utc": rows[0]["open_time_utc"],
        "last_open_utc": rows[-1]["open_time_utc"],
        "network_request_count": 1,
        "historical_range_exact": True,
        "automated_public_read_only_capture": True,
        "human_attestation_required": False,
        "official_dataset_sha256_before": official_before[
            "dataset_sha256"
        ],
        "official_dataset_sha256_after": official_after[
            "dataset_sha256"
        ],
        "official_manifest_sha256_before": official_before[
            "manifest_sha256"
        ],
        "official_manifest_sha256_after": official_after[
            "manifest_sha256"
        ],
        "capture_manifest_entries": validation[
            "manifest_entries"
        ],
    }


def offline_self_check(repo_root: Path | str) -> int:
    repo = Path(repo_root).resolve()
    evidence_root = Path(
        os.environ.get("TRADING_AI_EVIDENCE_ROOT", "C:/TAE")
    ).resolve()
    sandbox_parent = evidence_root / "ov"
    sandbox_parent.mkdir(parents=True, exist_ok=True)
    sandbox = (
        sandbox_parent / ("HISTV2_" + uuid.uuid4().hex[:10])
    )
    sandbox.mkdir()

    start_open = datetime(
        2026, 10, 9, 21, 15, tzinfo=timezone.utc
    )
    end_open = start_open + BAR * 16
    raw_rows: list[list[Any]] = []

    for index in range(EXPECTED_HISTORICAL_ROW_COUNT):
        open_time = start_open + BAR * index
        open_ms = _milliseconds(open_time)
        base = 80000.0 + index
        raw_rows.append(
            [
                open_ms,
                str(base),
                str(base + 20.0),
                str(base - 20.0),
                str(base + 5.0),
                str(1000.0 + index),
                open_ms + CLOSE_OFFSET_MILLISECONDS,
                "0",
                1,
                "0",
                "0",
                "0",
            ]
        )

    call_record: dict[str, Any] = {}

    class FakeResponse:
        def raise_for_status(self) -> None:
            return None

        def json(self) -> list[list[Any]]:
            return raw_rows

    def fake_get(
        url: str,
        *,
        params: Mapping[str, Any],
        timeout: int,
        allow_redirects: bool,
        headers: Mapping[str, str],
    ) -> FakeResponse:
        call_record["url"] = url
        call_record["params"] = dict(params)
        call_record["timeout"] = timeout
        call_record["allow_redirects"] = allow_redirects
        call_record["headers"] = dict(headers)
        return FakeResponse()

    original_get = requests.get
    output = sandbox / "capture"

    print(
        "=== HISTORICAL CLOSED CANDLE CAPTURE V2 "
        "OFFLINE SELF CHECK ==="
    )
    print("REAL_NETWORK_REQUEST_ALLOWED=False")
    print("REAL_COHORT_MODIFICATION_ALLOWED=False")
    print("OFFICIAL_APPEND_ALLOWED=False")

    try:
        requests.get = fake_get
        result = (
            capture_real_binance_public_historical_closed_candles(
                repo_root=repo,
                output_directory=output,
                start_open_utc=start_open,
                end_open_utc=end_open,
                authorization=AUTOMATED_CAPTURE_AUTHORIZATION,
            )
        )
        validation = validate_historical_closed_candle_capture(
            output
        )

        expected_start_ms = _milliseconds(start_open)
        expected_end_ms = (
            _milliseconds(end_open)
            + CLOSE_OFFSET_MILLISECONDS
        )

        _require(
            call_record["params"]["startTime"]
            == expected_start_ms,
            "SELF_CHECK_START_TIME_INVALID",
            "Self-check did not propagate startTime.",
        )
        _require(
            call_record["params"]["endTime"] == expected_end_ms,
            "SELF_CHECK_END_TIME_INVALID",
            "Self-check did not propagate endTime.",
        )
        _require(
            call_record["params"]["limit"]
            == EXPECTED_HISTORICAL_ROW_COUNT,
            "SELF_CHECK_LIMIT_INVALID",
            "Self-check request limit is invalid.",
        )
        _require(
            result["closed_candle_rows"]
            == EXPECTED_HISTORICAL_ROW_COUNT,
            "SELF_CHECK_RESULT_ROW_COUNT_INVALID",
            "Self-check result row count is invalid.",
        )
        _require(
            validation["historical_range_exact"] is True,
            "SELF_CHECK_RANGE_CONTRACT_INVALID",
            "Self-check range contract is invalid.",
        )

        print("START_TIME_PROPAGATION_VERIFIED=True")
        print("END_TIME_PROPAGATION_VERIFIED=True")
        print("EXACT_17_ROW_CONTRACT_VERIFIED=True")
        print("EXACT_15M_SPACING_VERIFIED=True")
        print("AUTOMATED_AUTHORIZATION_VERIFIED=True")
        print("HUMAN_ATTESTATION_REQUIRED=False")
        print("ATOMIC_EXTERNAL_OUTPUT_VERIFIED=True")
        print("REAL_HTTP_CALLS=0")
        print("OFFICIAL_APPEND_EXECUTED=False")
        print("SELF_CHECK_PASSED=True")
        return 0
    finally:
        requests.get = original_get
        if sandbox.exists():
            shutil.rmtree(sandbox, ignore_errors=False)
        print("OFFLINE_SANDBOX_CLEANED=True")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-check", action="store_true")
    parser.add_argument(
        "--repo",
        default=str(
            Path.home() / "OpenClawProjects" / "trading-ai"
        ),
    )
    args = parser.parse_args()
    if args.self_check:
        return offline_self_check(Path(args.repo))
    raise RuntimeError("MODE_REQUIRED")


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(
            "HISTORICAL_CAPTURE_V2_STATUS=FAILED",
            file=sys.stderr,
        )
        print(
            f"ERROR={type(exc).__name__}: {exc}",
            file=sys.stderr,
        )
        print(
            "NO_RESET_NO_FORCE_NO_AMEND=True",
            file=sys.stderr,
        )
        raise


__all__ = [
    "AUTOMATED_CAPTURE_AUTHORIZATION",
    "CAPABILITY",
    "CAPTURE_SCHEMA_VERSION",
    "EXPECTED_HISTORICAL_ROW_COUNT",
    "EXPECTED_SYMBOL",
    "EXPECTED_TIMEFRAME",
    "HistoricalClosedCandleCaptureError",
    "capture_real_binance_public_historical_closed_candles",
    "validate_historical_closed_candle_capture",
]