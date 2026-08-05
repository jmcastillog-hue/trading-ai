from __future__ import annotations

import csv
import hashlib
import json
import math
import os
import shutil
import uuid
from datetime import datetime, timedelta, timezone
from io import StringIO
from pathlib import Path
from typing import Any, Mapping, Sequence

import requests

from src.exchange.binance_historical_downloader import BASE_URLS

CAPABILITY = "LONG_PRIMARY_PUBLIC_CLOSED_CANDLE_CAPTURE_V1"
IMPLEMENTATION_SCHEMA_VERSION = (
    "LONG_PRIMARY_PUBLIC_CLOSED_CANDLE_CAPTURE_IMPLEMENTATION_V1"
)
CAPTURE_SCHEMA_VERSION = "LONG_PRIMARY_PUBLIC_CLOSED_CANDLE_CAPTURE_V1"
PROVIDER = "BINANCE_PUBLIC_SPOT_API"
EXPECTED_SYMBOL = "BTCUSDT"
EXPECTED_TIMEFRAME = "15m"
EXPECTED_INTERVAL_MILLISECONDS = 15 * 60 * 1000
EXPECTED_CLOSE_OFFSET_MILLISECONDS = EXPECTED_INTERVAL_MILLISECONDS - 1
REQUEST_LIMIT = 64
MINIMUM_CLOSED_ROWS = 49
MAX_CAPTURE_LAG = timedelta(minutes=30)
REQUEST_TIMEOUT_SECONDS = 20
REAL_CAPTURE_AUTHORIZATION = (
    "CAPTURE_ONE_SHOT_BINANCE_PUBLIC_CLOSED_CANDLES_V1"
)
PUBLIC_SPOT_KLINES_URL = BASE_URLS["spot"]

OFFICIAL_DATASET_RELATIVE_PATH = Path(
    "data/forward/long_forward_observation_dataset_v1.csv"
)
OFFICIAL_MANIFEST_RELATIVE_PATH = Path(
    "data/forward/long_forward_observation_dataset_v1.manifest.csv"
)
OFFICIAL_LOCK_RELATIVE_PATH = Path(
    "data/forward/long_forward_observation_dataset_v1.lock"
)

SOURCE_FILENAME = "btc_usdt_15m_closed_candles.csv"
METADATA_FILENAME = "capture_metadata.json"
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

PERMISSION_FALSE_FIELDS = (
    "review_package_created",
    "candidate_evaluated",
    "candidate_detected",
    "manual_confirmed",
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
)


class ClosedCandleCaptureError(RuntimeError):
    def __init__(self, code: str, message: str) -> None:
        self.code = code
        super().__init__(message)


def _require(condition: bool, code: str, message: str) -> None:
    if not condition:
        raise ClosedCandleCaptureError(code, message)


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


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _utc_text(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat()


def _milliseconds_to_utc_text(value: int) -> str:
    return _utc_text(datetime.fromtimestamp(value / 1000, tz=timezone.utc))


def _number(value: Any, field: str, row_number: int) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise ClosedCandleCaptureError(
            "BINANCE_KLINE_NUMERIC_INVALID",
            f"Invalid {field} at response row {row_number}.",
        ) from exc
    _require(
        math.isfinite(number),
        "BINANCE_KLINE_NUMERIC_INVALID",
        f"Non-finite {field} at response row {row_number}.",
    )
    return number


def _integer(value: Any, field: str, row_number: int) -> int:
    try:
        number = int(value)
    except (TypeError, ValueError) as exc:
        raise ClosedCandleCaptureError(
            "BINANCE_KLINE_TIME_INVALID",
            f"Invalid {field} at response row {row_number}.",
        ) from exc
    return number


def _number_text(value: float) -> str:
    text = format(float(value), ".10f").rstrip("0").rstrip(".")
    return text if text not in {"", "-0"} else "0"


def _bool_text(value: bool) -> str:
    return "True" if value else "False"


def _is_relative_to(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
    except ValueError:
        return False
    return True


def _official_paths(repo_root: Path) -> tuple[Path, Path, Path]:
    return (
        repo_root / OFFICIAL_DATASET_RELATIVE_PATH,
        repo_root / OFFICIAL_MANIFEST_RELATIVE_PATH,
        repo_root / OFFICIAL_LOCK_RELATIVE_PATH,
    )


def _official_hashes(repo_root: Path) -> dict[str, str]:
    dataset, manifest, lock = _official_paths(repo_root)
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


def _normalize_response_rows(
    raw_rows: Any,
    captured_at: datetime,
) -> tuple[list[dict[str, str]], int]:
    _require(
        isinstance(raw_rows, list),
        "BINANCE_RESPONSE_SCHEMA_INVALID",
        "Binance response must be a list.",
    )
    _require(
        len(raw_rows) > 0,
        "BINANCE_RESPONSE_EMPTY",
        "Binance response contains no klines.",
    )

    capture_ms = int(captured_at.timestamp() * 1000)
    normalized: list[dict[str, str]] = []
    open_rows_excluded = 0
    previous_open_ms: int | None = None

    for row_number, raw in enumerate(raw_rows, start=1):
        _require(
            isinstance(raw, (list, tuple)) and len(raw) >= 7,
            "BINANCE_KLINE_SCHEMA_INVALID",
            f"Response row {row_number} is not a Binance kline.",
        )
        open_ms = _integer(raw[0], "open_time", row_number)
        close_ms = _integer(raw[6], "close_time", row_number)
        _require(
            close_ms - open_ms == EXPECTED_CLOSE_OFFSET_MILLISECONDS,
            "BINANCE_KLINE_INTERVAL_INVALID",
            f"Response row {row_number} is not an exact 15m kline.",
        )
        if previous_open_ms is not None:
            _require(
                open_ms > previous_open_ms,
                "BINANCE_KLINE_ORDER_INVALID",
                "Binance klines are not strictly increasing.",
            )
            _require(
                open_ms - previous_open_ms
                == EXPECTED_INTERVAL_MILLISECONDS,
                "BINANCE_KLINE_GAP_INVALID",
                "Binance klines contain a missing or duplicated interval.",
            )
        previous_open_ms = open_ms

        open_price = _number(raw[1], "open", row_number)
        high = _number(raw[2], "high", row_number)
        low = _number(raw[3], "low", row_number)
        close = _number(raw[4], "close", row_number)
        volume = _number(raw[5], "volume", row_number)
        _require(
            min(open_price, high, low, close) > 0 and volume >= 0,
            "BINANCE_KLINE_RANGE_INVALID",
            f"Response row {row_number} has invalid price or volume.",
        )
        _require(
            high >= max(open_price, close)
            and low <= min(open_price, close)
            and high >= low,
            "BINANCE_KLINE_OHLC_INVALID",
            f"Response row {row_number} violates OHLC structure.",
        )

        if close_ms > capture_ms:
            open_rows_excluded += 1
            continue

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
                "candle_closed": _bool_text(True),
            }
        )

    _require(
        len(normalized) >= MINIMUM_CLOSED_ROWS,
        "CLOSED_CANDLE_WARMUP_INSUFFICIENT",
        f"At least {MINIMUM_CLOSED_ROWS} closed candles are required.",
    )
    latest_close = datetime.fromisoformat(normalized[-1]["close_time_utc"])
    _require(
        timedelta(0) <= captured_at - latest_close <= MAX_CAPTURE_LAG,
        "LATEST_CLOSED_CANDLE_STALE",
        "Latest closed candle is outside the 30-minute freshness window.",
    )
    return normalized, open_rows_excluded


def _source_csv_bytes(rows: Sequence[Mapping[str, str]]) -> bytes:
    output = StringIO(newline="")
    writer = csv.DictWriter(
        output,
        fieldnames=list(SOURCE_COLUMNS),
        lineterminator="\n",
        extrasaction="raise",
    )
    writer.writeheader()
    for row in rows:
        writer.writerow({field: row[field] for field in SOURCE_COLUMNS})
    return output.getvalue().encode("utf-8")


def _write_bytes_create_only(path: Path, payload: bytes) -> None:
    with path.open("xb") as handle:
        handle.write(payload)
        handle.flush()
        os.fsync(handle.fileno())


def _write_manifest(directory: Path, names: Sequence[str]) -> None:
    lines = [
        f"{_sha256_path(directory / name)}  {name}"
        for name in sorted(names)
    ]
    _write_bytes_create_only(
        directory / MANIFEST_FILENAME,
        ("\n".join(lines) + "\n").encode("utf-8"),
    )


def validate_closed_candle_capture(
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
    lines = manifest.read_text(encoding="utf-8").splitlines()
    _require(
        len(lines) == 2,
        "CAPTURE_MANIFEST_INVALID",
        "Capture manifest must contain two entries.",
    )
    names: list[str] = []
    for line in lines:
        parts = line.split("  ", 1)
        _require(
            len(parts) == 2 and len(parts[0]) == 64,
            "CAPTURE_MANIFEST_INVALID",
            "Capture manifest line is invalid.",
        )
        expected, name = parts
        path = root / name
        _require(
            path.is_file() and not path.is_symlink(),
            "CAPTURE_FILE_MISSING",
            f"Capture file is missing: {name}.",
        )
        _require(
            _sha256_path(path) == expected,
            "CAPTURE_HASH_MISMATCH",
            f"Capture hash mismatch: {name}.",
        )
        names.append(name)
    _require(
        sorted(names) == sorted([SOURCE_FILENAME, METADATA_FILENAME]),
        "CAPTURE_SCOPE_INVALID",
        "Capture file scope is invalid.",
    )

    source_payload = (root / SOURCE_FILENAME).read_bytes()
    _require(
        not source_payload.startswith(b"\xef\xbb\xbf"),
        "CAPTURE_SOURCE_ENCODING_INVALID",
        "Capture source must not contain a UTF-8 BOM.",
    )
    source_text = source_payload.decode("utf-8")
    reader = csv.DictReader(source_text.splitlines())
    _require(
        tuple(reader.fieldnames or ()) == SOURCE_COLUMNS,
        "CAPTURE_SOURCE_SCHEMA_INVALID",
        "Capture source columns are invalid.",
    )
    rows = list(reader)
    _require(
        len(rows) >= MINIMUM_CLOSED_ROWS,
        "CAPTURE_SOURCE_ROWS_INVALID",
        "Capture source has insufficient rows.",
    )
    _require(
        all(row["candle_closed"] == "True" for row in rows),
        "CAPTURE_OPEN_CANDLE_PRESENT",
        "Capture source contains an open candle.",
    )

    metadata = json.loads(
        (root / METADATA_FILENAME).read_text(encoding="utf-8")
    )
    _require(
        metadata["capture_schema_version"] == CAPTURE_SCHEMA_VERSION,
        "CAPTURE_METADATA_SCHEMA_INVALID",
        "Capture metadata schema is invalid.",
    )
    _require(
        metadata["source_artifact_sha256"]
        == _sha256_bytes(source_payload),
        "CAPTURE_METADATA_HASH_INVALID",
        "Capture metadata source hash is invalid.",
    )
    for field in PERMISSION_FALSE_FIELDS:
        _require(
            metadata[field] is False,
            "CAPTURE_PERMISSION_INVALID",
            f"Capture metadata enables {field}.",
        )
    return {
        "capture_id": metadata["capture_id"],
        "closed_candle_rows": len(rows),
        "latest_closed_candle_utc": metadata[
            "latest_closed_candle_utc"
        ],
        "source_artifact_sha256": metadata[
            "source_artifact_sha256"
        ],
        "manifest_entries": len(lines),
        "open_candles_excluded": metadata["open_candles_excluded"],
    }


def capture_real_binance_public_closed_candles(
    *,
    repo_root: Path | str,
    output_directory: Path | str,
    authorization: str | None = None,
) -> dict[str, Any]:
    _require(
        authorization == REAL_CAPTURE_AUTHORIZATION,
        "REAL_CAPTURE_AUTHORIZATION_REQUIRED",
        "Exact one-shot public capture authorization is required.",
    )
    repo = Path(repo_root).resolve()
    output = Path(output_directory).resolve()
    _require(
        (repo / ".git").is_dir(),
        "REPOSITORY_ROOT_INVALID",
        "Repository root is invalid.",
    )
    _require(
        not _is_relative_to(output, repo),
        "OUTPUT_INSIDE_REPOSITORY_PROHIBITED",
        "Capture output must be outside the repository.",
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
    captured_at = _utc_now()
    try:
        response = requests.get(
            PUBLIC_SPOT_KLINES_URL,
            params={
                "symbol": EXPECTED_SYMBOL,
                "interval": EXPECTED_TIMEFRAME,
                "limit": REQUEST_LIMIT,
            },
            timeout=REQUEST_TIMEOUT_SECONDS,
            allow_redirects=False,
            headers={
                "Accept": "application/json",
                "User-Agent": "Trading-AI-Closed-Candle-Capture-V1",
            },
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        raise ClosedCandleCaptureError(
            "BINANCE_HTTP_ERROR",
            "Binance public kline request failed.",
        ) from exc
    try:
        raw_rows = response.json()
    except (ValueError, json.JSONDecodeError) as exc:
        raise ClosedCandleCaptureError(
            "BINANCE_RESPONSE_JSON_INVALID",
            "Binance response is not valid JSON.",
        ) from exc

    rows, open_rows_excluded = _normalize_response_rows(
        raw_rows,
        captured_at,
    )
    source_payload = _source_csv_bytes(rows)
    source_sha256 = _sha256_bytes(source_payload)
    capture_id = (
        "LONGCAP_"
        + _sha256_bytes(
            _canonical_json_bytes(
                {
                    "captured_at_utc": _utc_text(captured_at),
                    "provider": PROVIDER,
                    "source_artifact_sha256": source_sha256,
                }
            )
        )[:24].upper()
    )
    metadata: dict[str, Any] = {
        "capture_schema_version": CAPTURE_SCHEMA_VERSION,
        "capability": CAPABILITY,
        "implementation_schema_version": IMPLEMENTATION_SCHEMA_VERSION,
        "capture_id": capture_id,
        "capture_mode": "ONE_SHOT_FOREGROUND",
        "provider": PROVIDER,
        "endpoint": PUBLIC_SPOT_KLINES_URL,
        "symbol": EXPECTED_SYMBOL,
        "timeframe": EXPECTED_TIMEFRAME,
        "request_limit": REQUEST_LIMIT,
        "network_request_count": 1,
        "captured_at_utc": _utc_text(captured_at),
        "closed_candle_rows": len(rows),
        "open_candles_excluded": open_rows_excluded,
        "latest_closed_candle_utc": rows[-1]["close_time_utc"],
        "source_artifact": SOURCE_FILENAME,
        "source_artifact_sha256": source_sha256,
        "source_columns": list(SOURCE_COLUMNS),
        "latest_candle_only_future_evaluation_contract": True,
        "lookahead_used": False,
        "automatic_or_recurring_capture": False,
        "review_package_created": False,
        "candidate_evaluated": False,
        "candidate_detected": False,
        "manual_confirmation_required": True,
        "manual_confirmed": False,
        "official_dataset_write_allowed": False,
        "official_append_allowed": False,
        "signal_generation_enabled": False,
        "live_alerts_allowed": False,
        "paper_trade_execution_allowed": False,
        "real_capital_allowed": False,
        "market_execution_allowed": False,
        "exchange_execution_allowed": False,
        "automation_allowed": False,
        "execution_allowed": False,
    }

    temporary = output.parent / f".{output.name}.{uuid.uuid4().hex}.tmp"
    _require(
        not temporary.exists() and not temporary.is_symlink(),
        "TEMPORARY_OUTPUT_COLLISION",
        "Temporary capture output already exists.",
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
        _write_manifest(
            temporary,
            (SOURCE_FILENAME, METADATA_FILENAME),
        )
        validate_closed_candle_capture(temporary)
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
        validation = validate_closed_candle_capture(output)
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
        "open_candles_excluded": open_rows_excluded,
        "latest_closed_candle_utc": rows[-1]["close_time_utc"],
        "network_request_count": 1,
        "one_shot_foreground": True,
        "review_package_created": False,
        "candidate_evaluated": False,
        "candidate_detected": False,
        "manual_confirmation_required": True,
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
        "capture_manifest_entries": validation["manifest_entries"],
    }


__all__ = [
    "CAPABILITY",
    "CAPTURE_SCHEMA_VERSION",
    "EXPECTED_SYMBOL",
    "EXPECTED_TIMEFRAME",
    "IMPLEMENTATION_SCHEMA_VERSION",
    "MANIFEST_FILENAME",
    "METADATA_FILENAME",
    "MINIMUM_CLOSED_ROWS",
    "PROVIDER",
    "PUBLIC_SPOT_KLINES_URL",
    "REAL_CAPTURE_AUTHORIZATION",
    "REQUEST_LIMIT",
    "SOURCE_COLUMNS",
    "SOURCE_FILENAME",
    "ClosedCandleCaptureError",
    "capture_real_binance_public_closed_candles",
    "validate_closed_candle_capture",
]
