from __future__ import annotations

import csv
import hashlib
import json
import math
import os
import shutil
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence

CAPABILITY = "LONG_PRIMARY_PROSPECTIVE_OBSERVATION_SOURCE_ADAPTER_V1"
IMPLEMENTATION_SCHEMA_VERSION = (
    "LONG_PRIMARY_PROSPECTIVE_OBSERVATION_SOURCE_ADAPTER_IMPLEMENTATION_V1"
)
SOURCE_SCHEMA_VERSION = "LONG_PRIMARY_PROSPECTIVE_OHLC_SOURCE_V1"
REVIEW_PACKAGE_SCHEMA_VERSION = "LONG_PRIMARY_HUMAN_REVIEW_PACKAGE_V1"
PROVENANCE_SCHEMA_VERSION = "LONG_PRIMARY_SOURCE_PROVENANCE_V1"

PRIMARY_CANDIDATE_ID = "LONG_BASE_FAILED_BREAKDOWN_V1"
SECONDARY_CANDIDATE_ID = "LONG_BASE_LIQUIDITY_SWEEP_V1"
EXPECTED_DIRECTION = "LONG"
EXPECTED_SYMBOL = "BTCUSDT"
EXPECTED_TIMEFRAME = "15m"
EXPECTED_RISK_REWARD = 2.5
MINIMUM_SOURCE_ROWS = 49
ROLLING_LOW_BARS = 48
ATR_BARS = 14
MAX_CAPTURE_LAG = timedelta(minutes=30)

REAL_SOURCE_AUTHORIZATION = (
    "PREPARE_REAL_LONG_PRIMARY_HUMAN_REVIEW_PACKAGE_V1"
)
SANDBOX_SOURCE_AUTHORIZATION = (
    "PREPARE_SANDBOX_LONG_PRIMARY_REVIEW_PACKAGE_V1"
)
REAL_SOURCE_ATTESTATION = (
    "REAL_MARKET_DATA_SOURCE_HUMAN_ATTESTED_NOT_SYNTHETIC"
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

CANDIDATE_COLUMNS = (
    "observation_id",
    "observed_at_utc",
    "source_system",
    "source_capture_id",
    "source_artifact",
    "source_artifact_sha256",
    "source_row_hash",
    "candidate_id",
    "direction",
    "symbol",
    "timeframe",
    "entry_price",
    "stop_price",
    "target_price",
    "invalidation_level",
    "risk_reward",
    "rolling_low_48",
    "atr14",
    "failed_breakdown",
    "reclaim_confirmed",
    "bullish_confirmation",
    "candidate_detected",
    "review_status",
    "manual_confirmation_required",
    "manual_confirmed",
    "official_dataset_write_allowed",
    "evidence_persistence_allowed",
    "signal_generation_enabled",
    "live_alerts_allowed",
    "paper_trade_execution_allowed",
    "real_capital_allowed",
    "market_execution_allowed",
    "exchange_execution_allowed",
    "automation_allowed",
    "execution_allowed",
)

EXECUTION_FALSE_FIELDS = (
    "official_dataset_write_allowed",
    "evidence_persistence_allowed",
    "signal_generation_enabled",
    "live_alerts_allowed",
    "paper_trade_execution_allowed",
    "real_capital_allowed",
    "market_execution_allowed",
    "exchange_execution_allowed",
    "automation_allowed",
    "execution_allowed",
)


class SourceAdapterError(RuntimeError):
    def __init__(self, code: str, message: str) -> None:
        self.code = code
        super().__init__(message)


@dataclass(frozen=True)
class NormalizedCandle:
    open_time_utc: str
    close_time_utc: str
    symbol: str
    timeframe: str
    open: float
    high: float
    low: float
    close: float
    volume: float
    candle_closed: bool

    def as_canonical_mapping(self) -> dict[str, str]:
        return {
            "open_time_utc": self.open_time_utc,
            "close_time_utc": self.close_time_utc,
            "symbol": self.symbol,
            "timeframe": self.timeframe,
            "open": _number_text(self.open),
            "high": _number_text(self.high),
            "low": _number_text(self.low),
            "close": _number_text(self.close),
            "volume": _number_text(self.volume),
            "candle_closed": _bool_text(self.candle_closed),
        }


def _require(condition: bool, code: str, message: str) -> None:
    if not condition:
        raise SourceAdapterError(code, message)


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


def _safe_text(value: Any, field: str) -> str:
    text = str(value).strip()
    _require(text != "", "REQUIRED_FIELD_MISSING", f"Missing {field}.")
    _require(
        "\x00" not in text and "\r" not in text and "\n" not in text,
        "TEXT_FIELD_INVALID",
        f"Unsafe text in {field}.",
    )
    return text


def _bool_text(value: bool) -> str:
    return "True" if value else "False"


def _parse_bool(value: Any, field: str) -> bool:
    text = str(value).strip().casefold()
    if text in {"true", "1", "yes", "y"}:
        return True
    if text in {"false", "0", "no", "n"}:
        return False
    raise SourceAdapterError(
        "BOOLEAN_FIELD_INVALID",
        f"Invalid boolean value for {field}.",
    )


def _number(value: Any, field: str) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise SourceAdapterError(
            "NUMERIC_FIELD_INVALID",
            f"Invalid numeric value for {field}.",
        ) from exc
    _require(
        math.isfinite(number),
        "NUMERIC_FIELD_INVALID",
        f"Non-finite numeric value for {field}.",
    )
    return number


def _number_text(value: float) -> str:
    text = format(float(value), ".10f").rstrip("0").rstrip(".")
    return text if text not in {"", "-0"} else "0"


def _parse_utc(value: Any, field: str) -> datetime:
    text = str(value).strip().replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError as exc:
        raise SourceAdapterError(
            "TIMESTAMP_INVALID",
            f"Invalid timestamp for {field}.",
        ) from exc
    _require(
        parsed.tzinfo is not None,
        "TIMESTAMP_TIMEZONE_REQUIRED",
        f"Timezone required for {field}.",
    )
    return parsed.astimezone(timezone.utc)


def _utc_text(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat()


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


def _read_source_csv(path: Path) -> tuple[bytes, list[NormalizedCandle]]:
    _require(
        path.is_file() and not path.is_symlink(),
        "SOURCE_FILE_INVALID",
        "Source CSV must be a regular file.",
    )
    payload = path.read_bytes()
    _require(payload != b"", "SOURCE_FILE_EMPTY", "Source CSV is empty.")
    _require(
        not payload.startswith(b"\xef\xbb\xbf"),
        "SOURCE_ENCODING_INVALID",
        "Source CSV must not contain a UTF-8 BOM.",
    )
    try:
        text = payload.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise SourceAdapterError(
            "SOURCE_ENCODING_INVALID",
            "Source CSV is not valid UTF-8.",
        ) from exc
    reader = csv.DictReader(text.splitlines())
    _require(
        tuple(reader.fieldnames or ()) == SOURCE_COLUMNS,
        "SOURCE_SCHEMA_INVALID",
        "Source CSV columns do not match the frozen schema.",
    )
    candles: list[NormalizedCandle] = []
    previous_open: datetime | None = None
    previous_close: datetime | None = None
    for row_number, row in enumerate(reader, start=2):
        open_time = _parse_utc(row["open_time_utc"], "open_time_utc")
        close_time = _parse_utc(row["close_time_utc"], "close_time_utc")
        _require(
            open_time < close_time,
            "CANDLE_TIME_RANGE_INVALID",
            f"Row {row_number} open time must precede close time.",
        )
        duration = close_time - open_time
        _require(
            timedelta(minutes=14, seconds=59)
            <= duration
            <= timedelta(minutes=15, seconds=1),
            "CANDLE_DURATION_INVALID",
            f"Row {row_number} is not a 15-minute candle.",
        )
        if previous_open is not None:
            _require(
                open_time > previous_open and close_time > previous_close,
                "CANDLE_ORDER_INVALID",
                f"Row {row_number} timestamps are not strictly increasing.",
            )
        previous_open = open_time
        previous_close = close_time

        symbol = _safe_text(row["symbol"], "symbol").upper()
        timeframe = _safe_text(row["timeframe"], "timeframe")
        _require(
            symbol == EXPECTED_SYMBOL,
            "SOURCE_SYMBOL_INVALID",
            f"Row {row_number} symbol must be {EXPECTED_SYMBOL}.",
        )
        _require(
            timeframe == EXPECTED_TIMEFRAME,
            "SOURCE_TIMEFRAME_INVALID",
            f"Row {row_number} timeframe must be {EXPECTED_TIMEFRAME}.",
        )
        open_price = _number(row["open"], "open")
        high = _number(row["high"], "high")
        low = _number(row["low"], "low")
        close = _number(row["close"], "close")
        volume = _number(row["volume"], "volume")
        candle_closed = _parse_bool(row["candle_closed"], "candle_closed")
        _require(
            candle_closed,
            "OPEN_CANDLE_PROHIBITED",
            f"Row {row_number} is not closed.",
        )
        _require(
            min(open_price, high, low, close) > 0 and volume >= 0,
            "CANDLE_NUMERIC_RANGE_INVALID",
            f"Row {row_number} contains invalid price or volume.",
        )
        _require(
            high >= max(open_price, close)
            and low <= min(open_price, close)
            and high >= low,
            "CANDLE_OHLC_INVALID",
            f"Row {row_number} violates OHLC structure.",
        )
        candles.append(
            NormalizedCandle(
                open_time_utc=_utc_text(open_time),
                close_time_utc=_utc_text(close_time),
                symbol=symbol,
                timeframe=timeframe,
                open=open_price,
                high=high,
                low=low,
                close=close,
                volume=volume,
                candle_closed=candle_closed,
            )
        )
    _require(
        len(candles) >= MINIMUM_SOURCE_ROWS,
        "SOURCE_WARMUP_INSUFFICIENT",
        f"At least {MINIMUM_SOURCE_ROWS} closed candles are required.",
    )
    return payload, candles


def _true_ranges(candles: Sequence[NormalizedCandle]) -> list[float]:
    values: list[float] = []
    previous_close: float | None = None
    for candle in candles:
        components = [candle.high - candle.low]
        if previous_close is not None:
            components.extend(
                [
                    abs(candle.high - previous_close),
                    abs(candle.low - previous_close),
                ]
            )
        values.append(max(components))
        previous_close = candle.close
    return values


def _detect_latest_primary_candidate(
    candles: Sequence[NormalizedCandle],
) -> dict[str, Any]:
    latest = candles[-1]
    preceding = candles[-(ROLLING_LOW_BARS + 1) : -1]
    _require(
        len(preceding) == ROLLING_LOW_BARS,
        "SOURCE_WARMUP_INSUFFICIENT",
        "Exactly 48 preceding candles are required for the latest evaluation.",
    )
    rolling_low = min(candle.low for candle in preceding)
    failed_breakdown = latest.low < rolling_low
    reclaim_confirmed = latest.close > rolling_low
    bullish_confirmation = latest.close > latest.open
    candidate_detected = (
        failed_breakdown and reclaim_confirmed and bullish_confirmation
    )
    true_ranges = _true_ranges(candles)
    atr_values = true_ranges[-ATR_BARS:]
    _require(
        len(atr_values) == ATR_BARS,
        "ATR_WARMUP_INSUFFICIENT",
        "ATR14 warmup is insufficient.",
    )
    atr14 = sum(atr_values) / len(atr_values)
    _require(atr14 > 0, "ATR_INVALID", "ATR14 must be positive.")
    entry = latest.close
    stop = min(
        latest.low - (0.05 * atr14),
        entry - (0.50 * atr14),
    )
    if stop <= 0 or stop >= entry:
        stop = entry - (1.50 * atr14)
    _require(
        stop > 0 and stop < entry,
        "LONG_STOP_INVALID",
        "Derived LONG stop is invalid.",
    )
    risk = entry - stop
    target = entry + (risk * EXPECTED_RISK_REWARD)
    _require(
        stop < entry < target,
        "LONG_PRICE_STRUCTURE_INVALID",
        "Derived LONG price structure is invalid.",
    )
    return {
        "latest": latest,
        "rolling_low_48": rolling_low,
        "atr14": atr14,
        "failed_breakdown": failed_breakdown,
        "reclaim_confirmed": reclaim_confirmed,
        "bullish_confirmation": bullish_confirmation,
        "candidate_detected": candidate_detected,
        "entry_price": entry,
        "stop_price": stop,
        "target_price": target,
        "invalidation_level": stop,
        "risk_reward": EXPECTED_RISK_REWARD,
    }


def _build_candidate_row(
    *,
    source_path: Path,
    source_sha256: str,
    source_system: str,
    source_capture_id: str,
    detection: Mapping[str, Any],
) -> dict[str, str]:
    latest: NormalizedCandle = detection["latest"]
    source_row_hash = _sha256_bytes(
        _canonical_json_bytes(latest.as_canonical_mapping())
    )
    observation_id = (
        "LONGOBS_"
        + _sha256_bytes(
            _canonical_json_bytes(
                {
                    "candidate_id": PRIMARY_CANDIDATE_ID,
                    "source_artifact_sha256": source_sha256,
                    "source_row_hash": source_row_hash,
                    "observed_at_utc": latest.close_time_utc,
                }
            )
        )[:24].upper()
    )
    row: dict[str, str] = {
        "observation_id": observation_id,
        "observed_at_utc": latest.close_time_utc,
        "source_system": source_system,
        "source_capture_id": source_capture_id,
        "source_artifact": str(source_path.resolve()),
        "source_artifact_sha256": source_sha256,
        "source_row_hash": source_row_hash,
        "candidate_id": PRIMARY_CANDIDATE_ID,
        "direction": EXPECTED_DIRECTION,
        "symbol": EXPECTED_SYMBOL,
        "timeframe": EXPECTED_TIMEFRAME,
        "entry_price": _number_text(detection["entry_price"]),
        "stop_price": _number_text(detection["stop_price"]),
        "target_price": _number_text(detection["target_price"]),
        "invalidation_level": _number_text(
            detection["invalidation_level"]
        ),
        "risk_reward": _number_text(EXPECTED_RISK_REWARD),
        "rolling_low_48": _number_text(detection["rolling_low_48"]),
        "atr14": _number_text(detection["atr14"]),
        "failed_breakdown": _bool_text(detection["failed_breakdown"]),
        "reclaim_confirmed": _bool_text(detection["reclaim_confirmed"]),
        "bullish_confirmation": _bool_text(
            detection["bullish_confirmation"]
        ),
        "candidate_detected": _bool_text(
            detection["candidate_detected"]
        ),
        "review_status": "PENDING_HUMAN_REVIEW",
        "manual_confirmation_required": "True",
        "manual_confirmed": "False",
    }
    for field in EXECUTION_FALSE_FIELDS:
        row[field] = "False"
    _require(
        tuple(row) == CANDIDATE_COLUMNS,
        "CANDIDATE_SCHEMA_INTERNAL_ERROR",
        "Candidate row schema is not canonical.",
    )
    return row


def _candidate_csv_bytes(row: Mapping[str, str] | None) -> bytes:
    from io import StringIO

    output = StringIO(newline="")
    writer = csv.DictWriter(
        output,
        fieldnames=list(CANDIDATE_COLUMNS),
        lineterminator="\n",
        extrasaction="raise",
    )
    writer.writeheader()
    if row is not None:
        writer.writerow({field: row[field] for field in CANDIDATE_COLUMNS})
    return output.getvalue().encode("utf-8")


def _write_bytes_create_only(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as handle:
        handle.write(payload)
        handle.flush()
        os.fsync(handle.fileno())


def _write_json_create_only(path: Path, value: Mapping[str, Any]) -> None:
    _write_bytes_create_only(path, _canonical_json_bytes(value))


def _write_manifest(directory: Path, names: Sequence[str]) -> None:
    lines = [
        f"{_sha256_path(directory / name)}  {name}"
        for name in sorted(names)
    ]
    _write_bytes_create_only(
        directory / "manifest.sha256",
        ("\n".join(lines) + "\n").encode("utf-8"),
    )


def validate_review_package(directory: Path | str) -> dict[str, Any]:
    root = Path(directory).resolve()
    _require(
        root.is_dir() and not root.is_symlink(),
        "REVIEW_PACKAGE_INVALID",
        "Review package directory is invalid.",
    )
    manifest = root / "manifest.sha256"
    _require(
        manifest.is_file() and not manifest.is_symlink(),
        "REVIEW_PACKAGE_MANIFEST_MISSING",
        "Review package manifest is missing.",
    )
    lines = manifest.read_text(encoding="utf-8").splitlines()
    _require(
        len(lines) == 4,
        "REVIEW_PACKAGE_MANIFEST_INVALID",
        "Review package manifest must contain four entries.",
    )
    names: list[str] = []
    for line in lines:
        parts = line.split("  ", 1)
        _require(
            len(parts) == 2 and len(parts[0]) == 64,
            "REVIEW_PACKAGE_MANIFEST_INVALID",
            "Review package manifest line is invalid.",
        )
        expected, name = parts
        path = root / name
        _require(
            path.is_file() and not path.is_symlink(),
            "REVIEW_PACKAGE_FILE_MISSING",
            f"Review package file is missing: {name}.",
        )
        _require(
            _sha256_path(path) == expected,
            "REVIEW_PACKAGE_HASH_MISMATCH",
            f"Review package hash mismatch: {name}.",
        )
        names.append(name)
    _require(
        sorted(names)
        == sorted(
            [
                "adapter_checks.json",
                "candidate_review_packet.json",
                "candidate_rows.csv",
                "source_snapshot.csv",
            ]
        ),
        "REVIEW_PACKAGE_SCOPE_INVALID",
        "Review package file scope is invalid.",
    )
    packet = json.loads(
        (root / "candidate_review_packet.json").read_text(
            encoding="utf-8"
        )
    )
    _require(
        packet["review_package_schema_version"]
        == REVIEW_PACKAGE_SCHEMA_VERSION,
        "REVIEW_PACKAGE_SCHEMA_INVALID",
        "Review package schema is invalid.",
    )
    for field in EXECUTION_FALSE_FIELDS:
        _require(
            packet[field] is False,
            "REVIEW_PACKAGE_PERMISSION_INVALID",
            f"Review package enables {field}.",
        )
    _require(
        packet["manual_confirmed"] is False,
        "REVIEW_PACKAGE_REVIEW_STATE_INVALID",
        "Review package must remain unconfirmed.",
    )
    return {
        "candidate_detected": bool(packet["candidate_detected"]),
        "eligible_for_real_human_review": bool(
            packet["eligible_for_real_human_review"]
        ),
        "package_scope": packet["package_scope"],
        "manifest_entries": len(lines),
        "package_sha256": _sha256_path(manifest),
    }


def _prepare_package(
    *,
    repo_root: Path | str,
    source_csv: Path | str,
    output_directory: Path | str,
    captured_at_utc: str,
    prospective_start_utc: str,
    source_system: str,
    source_capture_id: str,
    expected_source_sha256: str | None,
    package_scope: str,
    source_is_real_market_data: bool,
    source_attestation: str,
    authorization: str | None,
    required_authorization: str,
) -> dict[str, Any]:
    _require(
        authorization == required_authorization,
        "LOCAL_REVIEW_PACKAGE_AUTHORIZATION_REQUIRED",
        "Exact local review-package authorization is required.",
    )
    repo = Path(repo_root).resolve()
    source = Path(source_csv).resolve()
    output = Path(output_directory).resolve()
    _require(
        (repo / ".git").is_dir(),
        "REPOSITORY_ROOT_INVALID",
        "Repository root is invalid.",
    )
    _require(
        not _is_relative_to(output, repo),
        "OUTPUT_INSIDE_REPOSITORY_PROHIBITED",
        "Review package output must be outside the repository.",
    )
    _require(
        output.parent.is_dir() and not output.parent.is_symlink(),
        "OUTPUT_PARENT_INVALID",
        "Review package parent must be an existing regular directory.",
    )
    _require(
        not output.exists() and not output.is_symlink(),
        "OUTPUT_ALREADY_EXISTS",
        "Review package output already exists.",
    )
    official_dataset, official_manifest, _ = _official_paths(repo)
    _require(
        source not in {official_dataset.resolve(), official_manifest.resolve()},
        "OFFICIAL_SOURCE_PROHIBITED",
        "Official artifacts cannot be used as source input.",
    )
    official_before = _official_hashes(repo)
    captured_at = _parse_utc(captured_at_utc, "captured_at_utc")
    prospective_start = _parse_utc(
        prospective_start_utc,
        "prospective_start_utc",
    )
    _require(
        prospective_start <= captured_at,
        "PROSPECTIVE_START_INVALID",
        "Prospective start must not follow capture time.",
    )
    source_system_text = _safe_text(source_system, "source_system")
    capture_id_text = _safe_text(source_capture_id, "source_capture_id")
    payload, candles = _read_source_csv(source)
    source_sha256 = _sha256_bytes(payload)
    if expected_source_sha256 is not None:
        _require(
            source_sha256 == expected_source_sha256.lower(),
            "SOURCE_HASH_MISMATCH",
            "Source CSV SHA-256 does not match the expected hash.",
        )
    latest_close = _parse_utc(
        candles[-1].close_time_utc,
        "latest_close_time_utc",
    )
    _require(
        latest_close <= captured_at,
        "SOURCE_CONTAINS_FUTURE_CANDLE",
        "Latest candle closes after capture time.",
    )
    _require(
        captured_at - latest_close <= MAX_CAPTURE_LAG,
        "SOURCE_CAPTURE_STALE",
        "Latest closed candle is too old for prospective review.",
    )
    _require(
        latest_close >= prospective_start,
        "SOURCE_NOT_PROSPECTIVE",
        "Latest candle predates the prospective start.",
    )
    if package_scope == "REAL_PROSPECTIVE_MARKET_SOURCE":
        _require(
            source_is_real_market_data,
            "REAL_SOURCE_ATTESTATION_REQUIRED",
            "Real source package requires a real-market-data attestation.",
        )
        _require(
            source_attestation == REAL_SOURCE_ATTESTATION,
            "REAL_SOURCE_ATTESTATION_REQUIRED",
            "Exact real source attestation is required.",
        )
    else:
        _require(
            not source_is_real_market_data,
            "SANDBOX_SOURCE_SCOPE_INVALID",
            "Sandbox package cannot claim real market data.",
        )
        _require(
            source_attestation == "SANDBOX_VALIDATION_FIXTURE",
            "SANDBOX_SOURCE_SCOPE_INVALID",
            "Sandbox source attestation is invalid.",
        )
    detection = _detect_latest_primary_candidate(candles)
    candidate_row = (
        _build_candidate_row(
            source_path=source,
            source_sha256=source_sha256,
            source_system=source_system_text,
            source_capture_id=capture_id_text,
            detection=detection,
        )
        if detection["candidate_detected"]
        else None
    )
    package_id = (
        "LONGREVIEW_"
        + _sha256_bytes(
            _canonical_json_bytes(
                {
                    "captured_at_utc": _utc_text(captured_at),
                    "package_scope": package_scope,
                    "source_artifact_sha256": source_sha256,
                    "source_capture_id": capture_id_text,
                }
            )
        )[:24].upper()
    )
    latest = detection["latest"]
    review_packet: dict[str, Any] = {
        "review_package_schema_version": REVIEW_PACKAGE_SCHEMA_VERSION,
        "capability": CAPABILITY,
        "implementation_schema_version": IMPLEMENTATION_SCHEMA_VERSION,
        "package_id": package_id,
        "package_scope": package_scope,
        "created_at_utc": _utc_text(captured_at),
        "prospective_start_utc": _utc_text(prospective_start),
        "source_system": source_system_text,
        "source_capture_id": capture_id_text,
        "source_artifact": str(source),
        "source_artifact_sha256": source_sha256,
        "source_is_real_market_data": source_is_real_market_data,
        "source_attestation": source_attestation,
        "source_row_count": len(candles),
        "latest_closed_candle_utc": latest.close_time_utc,
        "latest_candle_only_evaluated": True,
        "lookahead_used": False,
        "candidate_id": PRIMARY_CANDIDATE_ID,
        "secondary_candidate_evaluated": False,
        "direction": EXPECTED_DIRECTION,
        "symbol": EXPECTED_SYMBOL,
        "timeframe": EXPECTED_TIMEFRAME,
        "candidate_detected": bool(detection["candidate_detected"]),
        "eligible_for_real_human_review": bool(
            detection["candidate_detected"]
            and package_scope == "REAL_PROSPECTIVE_MARKET_SOURCE"
        ),
        "review_status": "PENDING_HUMAN_REVIEW",
        "manual_confirmation_required": True,
        "manual_confirmed": False,
        "reviewer": "",
        "review_decision": "PENDING",
        "reviewer_notes": "",
        "official_dataset_write_allowed": False,
        "evidence_persistence_allowed": False,
        "signal_generation_enabled": False,
        "live_alerts_allowed": False,
        "paper_trade_execution_allowed": False,
        "real_capital_allowed": False,
        "market_execution_allowed": False,
        "exchange_execution_allowed": False,
        "automation_allowed": False,
        "execution_allowed": False,
        "candidate": candidate_row,
    }
    checks: dict[str, Any] = {
        "provenance_schema_version": PROVENANCE_SCHEMA_VERSION,
        "source_schema_version": SOURCE_SCHEMA_VERSION,
        "source_sha256_verified": True,
        "source_utf8_without_bom": True,
        "source_rows": len(candles),
        "source_warmup_sufficient": True,
        "all_candles_closed": True,
        "timestamps_strictly_increasing": True,
        "latest_candle_not_future": True,
        "latest_candle_fresh": True,
        "latest_candle_prospective": True,
        "latest_candle_only_evaluated": True,
        "lookahead_used": False,
        "primary_candidate_only": True,
        "failed_breakdown": bool(detection["failed_breakdown"]),
        "reclaim_confirmed": bool(detection["reclaim_confirmed"]),
        "bullish_confirmation": bool(
            detection["bullish_confirmation"]
        ),
        "candidate_detected": bool(detection["candidate_detected"]),
        "human_review_required": True,
        "manual_confirmed": False,
        "official_append_invoked": False,
        "official_append_environment_gate_modified": False,
        "all_execution_permissions_false": True,
    }
    temporary = output.parent / (
        f".{output.name}.{uuid.uuid4().hex}.tmp"
    )
    _require(
        not temporary.exists() and not temporary.is_symlink(),
        "TEMPORARY_OUTPUT_COLLISION",
        "Temporary output path already exists.",
    )
    try:
        temporary.mkdir()
        _write_bytes_create_only(
            temporary / "source_snapshot.csv",
            payload,
        )
        _write_bytes_create_only(
            temporary / "candidate_rows.csv",
            _candidate_csv_bytes(candidate_row),
        )
        _write_json_create_only(
            temporary / "candidate_review_packet.json",
            review_packet,
        )
        _write_json_create_only(
            temporary / "adapter_checks.json",
            checks,
        )
        _write_manifest(
            temporary,
            (
                "source_snapshot.csv",
                "candidate_rows.csv",
                "candidate_review_packet.json",
                "adapter_checks.json",
            ),
        )
        validation = validate_review_package(temporary)
        os.replace(temporary, output)
    except Exception:
        if temporary.exists():
            shutil.rmtree(temporary, ignore_errors=True)
        raise
    official_after = _official_hashes(repo)
    _require(
        official_after == official_before,
        "OFFICIAL_ARTIFACT_CHANGED",
        "Official dataset or manifest changed during package preparation.",
    )
    final_validation = validate_review_package(output)
    return {
        "capability": CAPABILITY,
        "package_id": package_id,
        "package_scope": package_scope,
        "output_directory": str(output),
        "source_artifact_sha256": source_sha256,
        "source_row_count": len(candles),
        "candidate_detected": bool(detection["candidate_detected"]),
        "candidate_rows_written": 1 if candidate_row is not None else 0,
        "eligible_for_real_human_review": final_validation[
            "eligible_for_real_human_review"
        ],
        "latest_closed_candle_utc": latest.close_time_utc,
        "latest_candle_only_evaluated": True,
        "lookahead_used": False,
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
        "review_package_manifest_entries": final_validation[
            "manifest_entries"
        ],
    }


def prepare_sandbox_validation_package(
    *,
    repo_root: Path | str,
    source_csv: Path | str,
    output_directory: Path | str,
    captured_at_utc: str,
    prospective_start_utc: str,
    source_system: str = "SANDBOX_VALIDATION_SOURCE",
    source_capture_id: str = "SANDBOX_CAPTURE_V1",
    expected_source_sha256: str | None = None,
    authorization: str | None = None,
) -> dict[str, Any]:
    return _prepare_package(
        repo_root=repo_root,
        source_csv=source_csv,
        output_directory=output_directory,
        captured_at_utc=captured_at_utc,
        prospective_start_utc=prospective_start_utc,
        source_system=source_system,
        source_capture_id=source_capture_id,
        expected_source_sha256=expected_source_sha256,
        package_scope="SANDBOX_VALIDATION_FIXTURE",
        source_is_real_market_data=False,
        source_attestation="SANDBOX_VALIDATION_FIXTURE",
        authorization=authorization,
        required_authorization=SANDBOX_SOURCE_AUTHORIZATION,
    )


def prepare_real_source_review_package(
    *,
    repo_root: Path | str,
    source_csv: Path | str,
    output_directory: Path | str,
    captured_at_utc: str,
    prospective_start_utc: str,
    source_system: str,
    source_capture_id: str,
    source_attestation: str,
    expected_source_sha256: str | None = None,
    authorization: str | None = None,
) -> dict[str, Any]:
    return _prepare_package(
        repo_root=repo_root,
        source_csv=source_csv,
        output_directory=output_directory,
        captured_at_utc=captured_at_utc,
        prospective_start_utc=prospective_start_utc,
        source_system=source_system,
        source_capture_id=source_capture_id,
        expected_source_sha256=expected_source_sha256,
        package_scope="REAL_PROSPECTIVE_MARKET_SOURCE",
        source_is_real_market_data=True,
        source_attestation=source_attestation,
        authorization=authorization,
        required_authorization=REAL_SOURCE_AUTHORIZATION,
    )


__all__ = [
    "ATR_BARS",
    "CAPABILITY",
    "CANDIDATE_COLUMNS",
    "EXPECTED_DIRECTION",
    "EXPECTED_RISK_REWARD",
    "EXPECTED_SYMBOL",
    "EXPECTED_TIMEFRAME",
    "IMPLEMENTATION_SCHEMA_VERSION",
    "MAX_CAPTURE_LAG",
    "MINIMUM_SOURCE_ROWS",
    "PRIMARY_CANDIDATE_ID",
    "REAL_SOURCE_ATTESTATION",
    "REAL_SOURCE_AUTHORIZATION",
    "REVIEW_PACKAGE_SCHEMA_VERSION",
    "ROLLING_LOW_BARS",
    "SANDBOX_SOURCE_AUTHORIZATION",
    "SECONDARY_CANDIDATE_ID",
    "SOURCE_COLUMNS",
    "SOURCE_SCHEMA_VERSION",
    "SourceAdapterError",
    "prepare_real_source_review_package",
    "prepare_sandbox_validation_package",
    "validate_review_package",
]
