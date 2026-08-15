from __future__ import annotations

import csv
import hashlib
import json
import math
import os
import uuid
from datetime import datetime, timedelta, timezone
from io import StringIO
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

import requests

from src.exchange.long_primary_public_closed_candle_capture_v1 import (
    PUBLIC_SPOT_KLINES_URL,
)
from src.long_side.forward_outcome_labeler_v1 import (
    FORWARD_HORIZONS_BARS,
    FUTURE_SOURCE_COLUMNS,
)

CAPABILITY = "FORWARD_OUTCOME_FUTURE_CLOSED_CANDLE_SOURCE_V1"
IMPLEMENTATION_SCHEMA_VERSION = (
    "FORWARD_OUTCOME_FUTURE_CLOSED_CANDLE_SOURCE_IMPLEMENTATION_V1"
)
CAPTURE_SCHEMA_VERSION = "FORWARD_OUTCOME_FUTURE_CLOSED_CANDLE_CAPTURE_V1"

PROVIDER = "BINANCE_PUBLIC_SPOT_API"
SYMBOL = "BTCUSDT"
TIMEFRAME = "15m"
BAR_DURATION = timedelta(minutes=15)
BAR_DURATION_MILLISECONDS = 15 * 60 * 1000
CLOSE_OFFSET_MILLISECONDS = BAR_DURATION_MILLISECONDS - 1
REQUEST_TIMEOUT_SECONDS = 20
REQUIRED_CLOSED_ROWS = max(FORWARD_HORIZONS_BARS) + 1

AUTHORIZATION = "CAPTURE_ONE_SHOT_FORWARD_OUTCOME_FUTURE_CLOSED_CANDLES_V1"

SOURCE_FILENAME = "future_closed_candles.csv"
METADATA_FILENAME = "capture_metadata.json"
MANIFEST_FILENAME = "manifest.sha256"

OFFICIAL_APPEND_GATE_NAME = "TRADING_AI_OFFICIAL_LONG_EVIDENCE_APPEND_ALLOWED"
OFFICIAL_DATASET = Path("data/forward/long_forward_observation_dataset_v1.csv")
OFFICIAL_MANIFEST = Path(
    "data/forward/long_forward_observation_dataset_v1.manifest.csv"
)
OFFICIAL_LOCK = Path("data/forward/long_forward_observation_dataset_v1.lock")

FALSE_FIELDS = (
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


class FutureClosedCandleSourceError(RuntimeError):
    def __init__(self, code: str, message: str) -> None:
        self.code = code
        super().__init__(message)


def _req(ok: bool, code: str, message: str) -> None:
    if not ok:
        raise FutureClosedCandleSourceError(code, message)


def _sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _utc(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat()


def _parse_utc(value: Any, field: str) -> datetime:
    text = str(value).strip().replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError as exc:
        raise FutureClosedCandleSourceError(
            "TIMESTAMP_INVALID",
            field,
        ) from exc
    _req(parsed.tzinfo is not None, "TIMESTAMP_TIMEZONE_REQUIRED", field)
    return parsed.astimezone(timezone.utc)


def _aligned_15m(value: datetime) -> bool:
    current = value.astimezone(timezone.utc)
    return (
        current.minute % 15 == 0
        and current.second == 0
        and current.microsecond == 0
    )


def _milliseconds(value: datetime) -> int:
    return int(value.timestamp() * 1000)


def _from_ms(value: int) -> str:
    return _utc(datetime.fromtimestamp(value / 1000, tz=timezone.utc))


def _number(value: Any, field: str, row_number: int) -> float:
    try:
        result = float(value)
    except (TypeError, ValueError) as exc:
        raise FutureClosedCandleSourceError(
            "BINANCE_KLINE_NUMERIC_INVALID",
            f"{field}:{row_number}",
        ) from exc
    _req(
        math.isfinite(result),
        "BINANCE_KLINE_NUMERIC_INVALID",
        f"{field}:{row_number}",
    )
    return result


def _integer(value: Any, field: str, row_number: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError) as exc:
        raise FutureClosedCandleSourceError(
            "BINANCE_KLINE_TIME_INVALID",
            f"{field}:{row_number}",
        ) from exc


def _number_text(value: float) -> str:
    text = format(float(value), ".10f").rstrip("0").rstrip(".")
    return text if text not in {"", "-0"} else "0"


def _json_bytes(value: Mapping[str, Any]) -> bytes:
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


def _csv_bytes(rows: Sequence[Mapping[str, str]]) -> bytes:
    output = StringIO(newline="")
    writer = csv.DictWriter(
        output,
        fieldnames=list(FUTURE_SOURCE_COLUMNS),
        lineterminator="\n",
        extrasaction="raise",
    )
    writer.writeheader()
    for row in rows:
        writer.writerow(
            {field: row[field] for field in FUTURE_SOURCE_COLUMNS}
        )
    return output.getvalue().encode("utf-8")


def _write_new(path: Path, payload: bytes) -> None:
    with path.open("xb") as handle:
        handle.write(payload)
        handle.flush()
        os.fsync(handle.fileno())


def _inside(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def _gate_off() -> None:
    _req(
        os.environ.get(OFFICIAL_APPEND_GATE_NAME) != "1",
        "OFFICIAL_APPEND_GATE_ENABLED",
        OFFICIAL_APPEND_GATE_NAME,
    )


def _official(repo: Path) -> dict[str, str]:
    dataset = repo / OFFICIAL_DATASET
    manifest = repo / OFFICIAL_MANIFEST
    lock = repo / OFFICIAL_LOCK
    _req(
        dataset.is_file() and not dataset.is_symlink(),
        "OFFICIAL_DATASET_INVALID",
        str(dataset),
    )
    _req(
        manifest.is_file() and not manifest.is_symlink(),
        "OFFICIAL_MANIFEST_INVALID",
        str(manifest),
    )
    _req(
        not lock.exists() and not lock.is_symlink(),
        "OFFICIAL_LOCK_PRESENT",
        str(lock),
    )
    return {
        "dataset_sha256": _sha(dataset),
        "manifest_sha256": _sha(manifest),
    }


def _normalize_rows(
    raw_rows: Any,
    *,
    required_start_open: datetime,
    captured_at: datetime,
) -> list[dict[str, str]]:
    _req(
        isinstance(raw_rows, list),
        "BINANCE_RESPONSE_SCHEMA_INVALID",
        "response",
    )
    _req(
        len(raw_rows) == REQUIRED_CLOSED_ROWS,
        "BINANCE_RESPONSE_ROW_COUNT_INVALID",
        f"{len(raw_rows)} != {REQUIRED_CLOSED_ROWS}",
    )

    expected_open_ms = _milliseconds(required_start_open)
    capture_ms = _milliseconds(captured_at)
    normalized: list[dict[str, str]] = []

    for row_number, raw in enumerate(raw_rows, start=1):
        _req(
            isinstance(raw, (list, tuple)) and len(raw) >= 7,
            "BINANCE_KLINE_SCHEMA_INVALID",
            str(row_number),
        )

        open_ms = _integer(raw[0], "open_time", row_number)
        close_ms = _integer(raw[6], "close_time", row_number)

        _req(
            open_ms == expected_open_ms,
            "BINANCE_KLINE_START_OR_GAP_INVALID",
            f"{open_ms} != {expected_open_ms}",
        )
        _req(
            close_ms - open_ms == CLOSE_OFFSET_MILLISECONDS,
            "BINANCE_KLINE_INTERVAL_INVALID",
            str(row_number),
        )
        _req(
            close_ms <= capture_ms,
            "FUTURE_CANDLE_NOT_CLOSED_AT_CAPTURE",
            _from_ms(open_ms),
        )

        o = _number(raw[1], "open", row_number)
        h = _number(raw[2], "high", row_number)
        l = _number(raw[3], "low", row_number)
        c = _number(raw[4], "close", row_number)
        v = _number(raw[5], "volume", row_number)

        _req(
            min(o, h, l, c) > 0 and v >= 0,
            "BINANCE_KLINE_VALUE_INVALID",
            str(row_number),
        )
        _req(
            l <= min(o, c) <= max(o, c) <= h,
            "BINANCE_KLINE_OHLC_INVALID",
            str(row_number),
        )

        normalized.append(
            {
                "open_time_utc": _from_ms(open_ms),
                "close_time_utc": _from_ms(close_ms),
                "symbol": SYMBOL,
                "timeframe": TIMEFRAME,
                "open": _number_text(o),
                "high": _number_text(h),
                "low": _number_text(l),
                "close": _number_text(c),
                "volume": _number_text(v),
                "candle_closed": "True",
            }
        )
        expected_open_ms += BAR_DURATION_MILLISECONDS

    return normalized


def validate_forward_outcome_future_closed_candle_capture_v1(
    directory: Path | str,
) -> dict[str, Any]:
    root = Path(directory).resolve()
    _req(
        root.is_dir() and not root.is_symlink(),
        "CAPTURE_DIRECTORY_INVALID",
        str(root),
    )

    source = root / SOURCE_FILENAME
    metadata_path = root / METADATA_FILENAME
    manifest = root / MANIFEST_FILENAME

    for path in (source, metadata_path, manifest):
        _req(
            path.is_file() and not path.is_symlink(),
            "CAPTURE_FILE_MISSING",
            str(path),
        )

    lines = [
        line
        for line in manifest.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    _req(
        len(lines) == 2,
        "MANIFEST_ENTRY_COUNT_INVALID",
        str(len(lines)),
    )

    seen = set()
    for line in lines:
        parts = line.split("  ", 1)
        _req(
            len(parts) == 2 and len(parts[0]) == 64,
            "MANIFEST_LINE_INVALID",
            line,
        )
        expected_sha, name = parts
        path = root / name
        _req(
            path.is_file() and not path.is_symlink(),
            "MANIFEST_FILE_MISSING",
            name,
        )
        _req(
            _sha(path) == expected_sha,
            "MANIFEST_HASH_MISMATCH",
            name,
        )
        seen.add(name)

    _req(
        seen == {SOURCE_FILENAME, METADATA_FILENAME},
        "MANIFEST_SCOPE_INVALID",
        str(sorted(seen)),
    )

    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    _req(
        metadata["capture_schema_version"] == CAPTURE_SCHEMA_VERSION,
        "CAPTURE_SCHEMA_INVALID",
        "metadata",
    )
    _req(
        metadata["capability"] == CAPABILITY,
        "CAPABILITY_INVALID",
        str(metadata.get("capability")),
    )
    _req(
        metadata["provider"] == PROVIDER
        and metadata["symbol"] == SYMBOL
        and metadata["timeframe"] == TIMEFRAME,
        "CAPTURE_IDENTITY_INVALID",
        "provider/symbol/timeframe",
    )
    _req(
        int(metadata["request_count"]) == 1,
        "REQUEST_COUNT_INVALID",
        str(metadata.get("request_count")),
    )
    _req(
        int(metadata["closed_row_count"]) == REQUIRED_CLOSED_ROWS,
        "CLOSED_ROW_COUNT_INVALID",
        str(metadata.get("closed_row_count")),
    )
    _req(
        tuple(metadata["forward_horizons_bars"]) == FORWARD_HORIZONS_BARS,
        "FORWARD_HORIZONS_INVALID",
        str(metadata.get("forward_horizons_bars")),
    )
    _req(
        metadata["source_sha256"] == _sha(source),
        "SOURCE_SHA256_INVALID",
        "source",
    )
    _req(
        isinstance(metadata["real_network_request_executed"], bool),
        "REAL_NETWORK_ATTESTATION_INVALID",
        "metadata",
    )
    _req(
        metadata["one_shot_foreground"] is True
        and metadata["automatic_retry_executed"] is False,
        "CAPTURE_MODE_INVALID",
        "mode",
    )
    for field in FALSE_FIELDS:
        _req(
            metadata[field] is False,
            "CAPTURE_PERMISSION_INVALID",
            field,
        )

    with source.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        _req(
            tuple(reader.fieldnames or ()) == FUTURE_SOURCE_COLUMNS,
            "FUTURE_SOURCE_SCHEMA_INVALID",
            "columns",
        )
        rows = list(reader)

    _req(
        len(rows) == REQUIRED_CLOSED_ROWS,
        "FUTURE_SOURCE_ROW_COUNT_INVALID",
        str(len(rows)),
    )

    first_open = _parse_utc(rows[0]["open_time_utc"], "first_open")
    _req(
        _aligned_15m(first_open),
        "FUTURE_SOURCE_FIRST_OPEN_NOT_ALIGNED",
        _utc(first_open),
    )

    for index, row in enumerate(rows):
        _req(
            row["symbol"] == SYMBOL
            and row["timeframe"] == TIMEFRAME
            and row["candle_closed"] == "True",
            "FUTURE_SOURCE_ROW_IDENTITY_INVALID",
            str(index),
        )
        open_time = _parse_utc(row["open_time_utc"], "open_time_utc")
        close_time = _parse_utc(row["close_time_utc"], "close_time_utc")
        _req(
            open_time == first_open + (BAR_DURATION * index),
            "FUTURE_SOURCE_GAP",
            str(index),
        )
        _req(
            close_time == open_time + BAR_DURATION - timedelta(milliseconds=1),
            "FUTURE_SOURCE_INTERVAL_INVALID",
            str(index),
        )

    _req(
        metadata["first_open_time_utc"] == rows[0]["open_time_utc"],
        "FIRST_OPEN_METADATA_MISMATCH",
        "first",
    )
    _req(
        metadata["last_close_time_utc"] == rows[-1]["close_time_utc"],
        "LAST_CLOSE_METADATA_MISMATCH",
        "last",
    )

    return {
        "closed_row_count": len(rows),
        "request_count": int(metadata["request_count"]),
        "first_open_time_utc": rows[0]["open_time_utc"],
        "last_close_time_utc": rows[-1]["close_time_utc"],
        "manifest_entries": len(lines),
        "source_sha256": _sha(source),
        "sufficient_for_primary_and_next_boundary_context_horizon_16": True,
    }


def capture_forward_outcome_future_closed_candles_v1(
    *,
    repo_root: Path | str,
    output_directory: Path | str,
    first_required_open_time_utc: str,
    authorization: str | None = None,
    request_get: Callable[..., Any] | None = None,
    clock: Callable[[], datetime] | None = None,
) -> dict[str, Any]:
    _req(
        authorization == AUTHORIZATION,
        "CAPTURE_AUTHORIZATION_REQUIRED",
        "authorization",
    )
    _gate_off()

    repo = Path(repo_root).resolve()
    out = Path(output_directory).resolve()

    _req(
        (repo / ".git").is_dir(),
        "REPOSITORY_ROOT_INVALID",
        str(repo),
    )
    _req(
        not _inside(out, repo),
        "OUTPUT_INSIDE_REPOSITORY_PROHIBITED",
        str(out),
    )
    _req(
        out.parent.is_dir() and not out.parent.is_symlink(),
        "OUTPUT_PARENT_INVALID",
        str(out.parent),
    )
    _req(
        not out.exists() and not out.is_symlink(),
        "OUTPUT_ALREADY_EXISTS",
        str(out),
    )

    first_open = _parse_utc(
        first_required_open_time_utc,
        "first_required_open_time_utc",
    )
    _req(
        _aligned_15m(first_open),
        "FIRST_REQUIRED_OPEN_NOT_15M_ALIGNED",
        _utc(first_open),
    )

    official_before = _official(repo)
    now = (clock or (lambda: datetime.now(timezone.utc)))().astimezone(
        timezone.utc
    )

    last_required_close = (
        first_open
        + (BAR_DURATION * REQUIRED_CLOSED_ROWS)
        - timedelta(milliseconds=1)
    )
    _req(
        now >= last_required_close,
        "REQUIRED_FORWARD_HORIZON_NOT_YET_MATURE",
        _utc(last_required_close),
    )

    get = request_get or requests.get
    params = {
        "symbol": SYMBOL,
        "interval": TIMEFRAME,
        "startTime": _milliseconds(first_open),
        "limit": REQUIRED_CLOSED_ROWS,
    }

    response = get(
        PUBLIC_SPOT_KLINES_URL,
        params=params,
        timeout=REQUEST_TIMEOUT_SECONDS,
    )
    _req(
        int(getattr(response, "status_code", 0)) == 200,
        "BINANCE_HTTP_STATUS_INVALID",
        str(getattr(response, "status_code", None)),
    )

    try:
        raw_rows = response.json()
    except Exception as exc:
        raise FutureClosedCandleSourceError(
            "BINANCE_RESPONSE_JSON_INVALID",
            "response",
        ) from exc

    rows = _normalize_rows(
        raw_rows,
        required_start_open=first_open,
        captured_at=now,
    )

    _req(
        _official(repo) == official_before,
        "OFFICIAL_ARTIFACT_CHANGED",
        "before write",
    )
    _gate_off()

    out.mkdir()
    source_path = out / SOURCE_FILENAME
    metadata_path = out / METADATA_FILENAME

    _write_new(source_path, _csv_bytes(rows))
    source_sha = _sha(source_path)

    metadata = {
        "capture_schema_version": CAPTURE_SCHEMA_VERSION,
        "capability": CAPABILITY,
        "implementation_schema_version": IMPLEMENTATION_SCHEMA_VERSION,
        "capture_id": "FUTURECAP_" + uuid.uuid4().hex[:24].upper(),
        "provider": PROVIDER,
        "endpoint": PUBLIC_SPOT_KLINES_URL,
        "symbol": SYMBOL,
        "timeframe": TIMEFRAME,
        "captured_at_utc": _utc(now),
        "first_required_open_time_utc": _utc(first_open),
        "first_open_time_utc": rows[0]["open_time_utc"],
        "last_close_time_utc": rows[-1]["close_time_utc"],
        "closed_row_count": len(rows),
        "required_closed_rows": REQUIRED_CLOSED_ROWS,
        "forward_horizons_bars": list(FORWARD_HORIZONS_BARS),
        "request_count": 1,
        "request_limit": REQUIRED_CLOSED_ROWS,
        "request_start_time_milliseconds": _milliseconds(first_open),
        "request_timeout_seconds": REQUEST_TIMEOUT_SECONDS,
        "source_csv": str(source_path),
        "source_sha256": source_sha,
        "source_columns": list(FUTURE_SOURCE_COLUMNS),
        "one_shot_foreground": True,
        "automatic_retry_executed": False,
        "api_key_used": False,
        "authenticated_endpoint_used": False,
        "account_endpoint_used": False,
        "order_endpoint_used": False,
        "websocket_used": False,
        "background_execution": False,
        "scheduler_installed": False,
        "real_network_request_executed": request_get is None,
        "future_horizon_mature_at_capture": True,
        "sufficient_for_primary_and_next_boundary_context_horizon_16": True,
        **{field: False for field in FALSE_FIELDS},
    }
    _write_new(metadata_path, _json_bytes(metadata))

    manifest_lines = [
        f"{_sha(metadata_path)}  {METADATA_FILENAME}",
        f"{_sha(source_path)}  {SOURCE_FILENAME}",
    ]
    _write_new(
        out / MANIFEST_FILENAME,
        ("\n".join(manifest_lines) + "\n").encode("utf-8"),
    )

    validation = validate_forward_outcome_future_closed_candle_capture_v1(
        out
    )

    _req(
        _official(repo) == official_before,
        "OFFICIAL_ARTIFACT_CHANGED",
        "after write",
    )
    _gate_off()

    return {
        "capability": CAPABILITY,
        "capture_id": metadata["capture_id"],
        "output_directory": str(out),
        "source_csv": str(source_path),
        "metadata_json": str(metadata_path),
        "source_sha256": source_sha,
        "first_open_time_utc": validation["first_open_time_utc"],
        "last_close_time_utc": validation["last_close_time_utc"],
        "closed_row_count": validation["closed_row_count"],
        "network_request_count": 1,
        "one_shot_foreground": True,
        "manual_confirmation_required": True,
        "manual_confirmed": False,
        **{field: False for field in FALSE_FIELDS},
    }


__all__ = [
    "AUTHORIZATION",
    "CAPABILITY",
    "CAPTURE_SCHEMA_VERSION",
    "PROVIDER",
    "REQUIRED_CLOSED_ROWS",
    "SYMBOL",
    "TIMEFRAME",
    "FutureClosedCandleSourceError",
    "capture_forward_outcome_future_closed_candles_v1",
    "validate_forward_outcome_future_closed_candle_capture_v1",
]
