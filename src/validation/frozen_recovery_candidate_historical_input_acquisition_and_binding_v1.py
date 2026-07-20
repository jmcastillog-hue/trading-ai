from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
import re
import shutil
import sys
import tempfile
import time
import urllib.error
import urllib.request
import zipfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Iterable


PHASE = "10.42R.2J"
SCHEMA_VERSION = "HISTORICAL_INPUT_MANIFEST_BINDING_AND_INTEGRITY_VALIDATION_V1"
GAP_POLICY = "PRESERVE_AND_DECLARE_CHECKSUM_VERIFIED_SOURCE_GAPS_NO_INTERPOLATION"
SOURCE_PROVIDER = "BINANCE_PUBLIC_DATA"
SOURCE_MARKET = "BINANCE_SPOT"
ACQUISITION_METHOD = "MONTHLY_KLINE_ARCHIVE_WITH_SHA256_CHECKSUM"
ARCHIVE_BASE = "https://data.binance.vision/data/spot/monthly/klines"

SYMBOLS = ("BTCUSDT", "ETHUSDT", "SOLUSDT")
TIMEFRAMES = ("15m", "1h", "4h")
INTERVAL_SECONDS = {"15m": 900, "1h": 3600, "4h": 14400}
ROLE_BY_TIMEFRAME = {
    "15m": "PRIMARY_SIGNAL_AND_SIMULATED_EXECUTION",
    "1h": "CLOSED_CONTEXT_ONLY",
    "4h": "CLOSED_CONTEXT_ONLY",
}

START_UTC = datetime(2022, 1, 1, tzinfo=timezone.utc)
END_UTC = datetime(2026, 1, 1, tzinfo=timezone.utc)
EVIDENCE_WINDOW_ID = "KNOWN_EVIDENCE_2022_2025"

CANONICAL_COLUMNS = (
    "open_time_utc",
    "open",
    "high",
    "low",
    "close",
    "volume",
    "close_time_utc",
)

MANIFEST_FIELDS = (
    "slot_id",
    "symbol",
    "timeframe",
    "role",
    "evidence_window_id",
    "relative_path",
    "file_sha256",
    "size_bytes",
    "row_count",
    "first_open_time_utc",
    "last_close_time_utc",
    "expected_columns_json",
    "timestamp_unit",
    "interval_seconds",
    "source_provider",
    "source_market",
    "acquisition_method",
    "acquisition_time_utc",
    "provenance_sha256",
    "duplicate_open_time_count",
    "duplicate_close_time_count",
    "missing_interval_count",
    "invalid_ohlcv_row_count",
    "binding_state",
    "manifest_row_sha256",
)

RAW_KLINE_COLUMN_COUNT = 12
HEX64_RE = re.compile(r"\b([0-9a-fA-F]{64})\b")


class BindingFailure(RuntimeError):
    pass


@dataclass(frozen=True)
class ArchiveTask:
    symbol: str
    timeframe: str
    year: int
    month: int
    zip_url: str
    checksum_url: str
    zip_path: Path
    checksum_path: Path

    @property
    def archive_name(self) -> str:
        return self.zip_path.name


@dataclass(frozen=True)
class ArchiveEvidence:
    slot_id: str
    archive_name: str
    archive_url: str
    checksum_url: str
    checksum_sha256: str
    zip_size_bytes: int


@dataclass(frozen=True)
class MissingIntervalEvidence:
    slot_id: str
    symbol: str
    timeframe: str
    missing_open_time_utc: str
    previous_present_open_time_utc: str
    next_present_open_time_utc: str
    interval_seconds: int
    classification: str
    source_archives_checksum_verified: bool


@dataclass(frozen=True)
class SlotResult:
    manifest_row: dict[str, str]
    archive_evidence: tuple[ArchiveEvidence, ...]
    missing_interval_evidence: tuple[MissingIntervalEvidence, ...]


def utc_now_text() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def month_range(start_year: int, end_year: int) -> Iterable[tuple[int, int]]:
    for year in range(start_year, end_year + 1):
        for month in range(1, 13):
            yield year, month


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def canonical_json(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def canonical_row_sha256(row: dict[str, str]) -> str:
    payload = {field: row[field] for field in MANIFEST_FIELDS if field != "manifest_row_sha256"}
    return sha256_bytes(canonical_json(payload).encode("utf-8"))


def request_bytes(url: str, timeout_seconds: int) -> bytes:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "TradingAI-Phase-10.42R.2J/1.0",
            "Accept": "*/*",
        },
    )
    with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
        status = getattr(response, "status", 200)
        if status != 200:
            raise BindingFailure(f"HTTP {status} for {url}")
        return response.read()


def atomic_write_bytes(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".part")
    temporary.write_bytes(data)
    os.replace(temporary, path)


def download_with_retries(
    url: str,
    destination: Path,
    *,
    timeout_seconds: int,
    retries: int,
) -> None:
    last_error: Exception | None = None
    for attempt in range(1, retries + 1):
        try:
            data = request_bytes(url, timeout_seconds)
            if not data:
                raise BindingFailure(f"Empty response for {url}")
            atomic_write_bytes(destination, data)
            return
        except (urllib.error.URLError, TimeoutError, BindingFailure, OSError) as exc:
            last_error = exc
            if attempt == retries:
                break
            time.sleep(min(2 ** attempt, 10))
    raise BindingFailure(f"Download failed after {retries} attempts: {url}: {last_error}")


def parse_checksum(path: Path) -> str:
    text = path.read_text(encoding="utf-8-sig", errors="strict")
    match = HEX64_RE.search(text)
    if not match:
        raise BindingFailure(f"No SHA-256 found in checksum file: {path}")
    return match.group(1).lower()


def ensure_archive(task: ArchiveTask, *, timeout_seconds: int, retries: int) -> ArchiveEvidence:
    if not task.checksum_path.is_file():
        download_with_retries(
            task.checksum_url,
            task.checksum_path,
            timeout_seconds=timeout_seconds,
            retries=retries,
        )

    expected = parse_checksum(task.checksum_path)

    if task.zip_path.is_file() and sha256_file(task.zip_path) != expected:
        task.zip_path.unlink()

    if not task.zip_path.is_file():
        download_with_retries(
            task.zip_url,
            task.zip_path,
            timeout_seconds=timeout_seconds,
            retries=retries,
        )

    actual = sha256_file(task.zip_path)
    if actual != expected:
        raise BindingFailure(
            f"Archive checksum mismatch: {task.archive_name}: expected={expected}, actual={actual}"
        )

    if not zipfile.is_zipfile(task.zip_path):
        raise BindingFailure(f"Invalid ZIP archive: {task.zip_path}")

    slot_id = f"{task.symbol}_{task.timeframe.upper()}_{EVIDENCE_WINDOW_ID}"
    return ArchiveEvidence(
        slot_id=slot_id,
        archive_name=task.archive_name,
        archive_url=task.zip_url,
        checksum_url=task.checksum_url,
        checksum_sha256=expected,
        zip_size_bytes=task.zip_path.stat().st_size,
    )


def build_archive_tasks(cache_dir: Path) -> tuple[ArchiveTask, ...]:
    tasks: list[ArchiveTask] = []
    for symbol in SYMBOLS:
        for timeframe in TIMEFRAMES:
            slot_cache = cache_dir / symbol / timeframe
            for year, month in month_range(2022, 2025):
                base_name = f"{symbol}-{timeframe}-{year:04d}-{month:02d}.zip"
                zip_url = f"{ARCHIVE_BASE}/{symbol}/{timeframe}/{base_name}"
                checksum_url = zip_url + ".CHECKSUM"
                tasks.append(
                    ArchiveTask(
                        symbol=symbol,
                        timeframe=timeframe,
                        year=year,
                        month=month,
                        zip_url=zip_url,
                        checksum_url=checksum_url,
                        zip_path=slot_cache / base_name,
                        checksum_path=slot_cache / (base_name + ".CHECKSUM"),
                    )
                )
    return tuple(tasks)


def timestamp_to_microseconds(raw: str) -> int:
    try:
        value = int(raw)
    except ValueError as exc:
        raise BindingFailure(f"Invalid integer timestamp: {raw!r}") from exc

    if value >= 10**15:
        return value
    if value >= 10**12:
        return value * 1000
    raise BindingFailure(f"Unsupported timestamp magnitude: {raw!r}")


def microseconds_to_utc_text(value: int) -> str:
    seconds, micros = divmod(value, 1_000_000)
    moment = datetime.fromtimestamp(seconds, tz=timezone.utc).replace(microsecond=micros)
    return moment.isoformat(timespec="microseconds")


def validate_ohlcv(open_value: str, high_value: str, low_value: str, close_value: str, volume_value: str) -> None:
    try:
        open_decimal = Decimal(open_value)
        high_decimal = Decimal(high_value)
        low_decimal = Decimal(low_value)
        close_decimal = Decimal(close_value)
        volume_decimal = Decimal(volume_value)
    except InvalidOperation as exc:
        raise BindingFailure("Invalid decimal in OHLCV row") from exc

    values = (open_decimal, high_decimal, low_decimal, close_decimal, volume_decimal)
    if not all(value.is_finite() for value in values):
        raise BindingFailure("Non-finite OHLCV value")
    if volume_decimal < 0:
        raise BindingFailure("Negative volume")
    if high_decimal < low_decimal:
        raise BindingFailure("High below low")
    if high_decimal < max(open_decimal, close_decimal):
        raise BindingFailure("High below open/close")
    if low_decimal > min(open_decimal, close_decimal):
        raise BindingFailure("Low above open/close")


def archive_csv_reader(zip_path: Path) -> Iterable[list[str]]:
    with zipfile.ZipFile(zip_path, "r") as archive:
        csv_members = [name for name in archive.namelist() if name.lower().endswith(".csv")]
        if len(csv_members) != 1:
            raise BindingFailure(
                f"Expected exactly one CSV in {zip_path.name}, found {len(csv_members)}"
            )
        with archive.open(csv_members[0], "r") as raw_handle:
            with io.TextIOWrapper(raw_handle, encoding="utf-8-sig", newline="") as text_handle:
                reader = csv.reader(text_handle)
                for row in reader:
                    if not row:
                        continue
                    yield [str(value).strip() for value in row]


def is_header_row(row: list[str]) -> bool:
    if not row:
        return False
    try:
        int(row[0])
        return False
    except ValueError:
        return True


def expected_row_count(timeframe: str) -> int:
    seconds = int((END_UTC - START_UTC).total_seconds())
    interval = INTERVAL_SECONDS[timeframe]
    if seconds % interval:
        raise BindingFailure("Evidence window is not divisible by interval")
    return seconds // interval


def load_previous_acquisition_times(manifest_path: Path) -> dict[str, str]:
    if not manifest_path.is_file():
        return {}
    try:
        with manifest_path.open("r", encoding="utf-8-sig", newline="") as handle:
            return {
                row["slot_id"]: row["acquisition_time_utc"]
                for row in csv.DictReader(handle)
                if row.get("slot_id") and row.get("acquisition_time_utc")
            }
    except Exception:
        return {}


def build_slot(
    *,
    root: Path,
    output_dir: Path,
    symbol: str,
    timeframe: str,
    tasks: tuple[ArchiveTask, ...],
    evidence_by_archive: dict[str, ArchiveEvidence],
    acquisition_time_utc: str,
) -> SlotResult:
    slot_id = f"{symbol}_{timeframe.upper()}_{EVIDENCE_WINDOW_ID}"
    interval_us = INTERVAL_SECONDS[timeframe] * 1_000_000
    required_start_us = int(START_UTC.timestamp() * 1_000_000)
    required_end_us = int(END_UTC.timestamp() * 1_000_000)

    filename = (
        f"phase_10_42r_2j_{symbol.lower()}_{timeframe}_spot_"
        "2022_2025_v1.csv"
    )
    final_path = output_dir / filename
    temporary_path = final_path.with_name(final_path.name + ".part")
    final_path.parent.mkdir(parents=True, exist_ok=True)

    selected_tasks = tuple(
        sorted(
            (task for task in tasks if task.symbol == symbol and task.timeframe == timeframe),
            key=lambda item: (item.year, item.month),
        )
    )
    if len(selected_tasks) != 48:
        raise BindingFailure(f"{slot_id}: expected 48 monthly archives, got {len(selected_tasks)}")

    archive_evidence = tuple(evidence_by_archive[task.archive_name] for task in selected_tasks)
    provenance_rows = [
        {
            "archive_name": item.archive_name,
            "archive_url": item.archive_url,
            "checksum_url": item.checksum_url,
            "checksum_sha256": item.checksum_sha256,
            "zip_size_bytes": item.zip_size_bytes,
        }
        for item in archive_evidence
    ]
    row_count = 0
    duplicate_open_time_count = 0
    duplicate_close_time_count = 0
    missing_interval_count = 0
    invalid_ohlcv_row_count = 0
    first_open_us: int | None = None
    last_open_us: int | None = None
    last_close_us: int | None = None
    previous_open_us: int | None = None
    previous_close_us: int | None = None
    missing_interval_evidence: list[MissingIntervalEvidence] = []

    try:
        with temporary_path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.writer(handle, lineterminator="\n")
            writer.writerow(CANONICAL_COLUMNS)

            for task in selected_tasks:
                header_seen = False
                for row in archive_csv_reader(task.zip_path):
                    if not header_seen and is_header_row(row):
                        header_seen = True
                        continue
                    header_seen = True

                    if len(row) < RAW_KLINE_COLUMN_COUNT:
                        raise BindingFailure(
                            f"{slot_id}: {task.archive_name}: expected >=12 columns, got {len(row)}"
                        )

                    open_us = timestamp_to_microseconds(row[0])
                    close_us = timestamp_to_microseconds(row[6])

                    if open_us < required_start_us or open_us >= required_end_us:
                        raise BindingFailure(
                            f"{slot_id}: timestamp outside frozen evidence window: {row[0]}"
                        )

                    try:
                        validate_ohlcv(row[1], row[2], row[3], row[4], row[5])
                    except BindingFailure:
                        invalid_ohlcv_row_count += 1
                        raise

                    if close_us <= open_us:
                        raise BindingFailure(f"{slot_id}: close timestamp not after open timestamp")
                    if close_us >= open_us + interval_us:
                        raise BindingFailure(f"{slot_id}: close timestamp exceeds interval boundary")

                    if previous_open_us is not None:
                        delta = open_us - previous_open_us
                        if delta == 0:
                            duplicate_open_time_count += 1
                            raise BindingFailure(f"{slot_id}: duplicate open timestamp")
                        if delta < 0:
                            raise BindingFailure(f"{slot_id}: non-monotonic open timestamp")
                        if delta % interval_us != 0:
                            raise BindingFailure(f"{slot_id}: irregular interval delta={delta}")
                        gap_count = delta // interval_us - 1
                        missing_interval_count += gap_count
                        for gap_index in range(1, gap_count + 1):
                            missing_open_us = previous_open_us + gap_index * interval_us
                            missing_interval_evidence.append(
                                MissingIntervalEvidence(
                                    slot_id=slot_id,
                                    symbol=symbol,
                                    timeframe=timeframe,
                                    missing_open_time_utc=microseconds_to_utc_text(
                                        missing_open_us
                                    ),
                                    previous_present_open_time_utc=microseconds_to_utc_text(
                                        previous_open_us
                                    ),
                                    next_present_open_time_utc=microseconds_to_utc_text(
                                        open_us
                                    ),
                                    interval_seconds=INTERVAL_SECONDS[timeframe],
                                    classification=(
                                        "DECLARED_GAP_IN_CHECKSUM_VERIFIED_BINANCE_ARCHIVES"
                                    ),
                                    source_archives_checksum_verified=True,
                                )
                            )

                    if previous_close_us is not None:
                        if close_us == previous_close_us:
                            duplicate_close_time_count += 1
                            raise BindingFailure(f"{slot_id}: duplicate close timestamp")
                        if close_us < previous_close_us:
                            raise BindingFailure(f"{slot_id}: non-monotonic close timestamp")

                    if first_open_us is None:
                        first_open_us = open_us
                    last_open_us = open_us
                    last_close_us = close_us
                    previous_open_us = open_us
                    previous_close_us = close_us
                    row_count += 1

                    writer.writerow(
                        (
                            microseconds_to_utc_text(open_us),
                            row[1],
                            row[2],
                            row[3],
                            row[4],
                            row[5],
                            microseconds_to_utc_text(close_us),
                        )
                    )

        if first_open_us != required_start_us:
            raise BindingFailure(
                f"{slot_id}: first open mismatch: expected={required_start_us}, actual={first_open_us}"
            )
        expected_last_open_us = required_end_us - interval_us
        if last_open_us != expected_last_open_us:
            raise BindingFailure(
                f"{slot_id}: last open mismatch: expected={expected_last_open_us}, actual={last_open_us}"
            )
        calendar_row_count = expected_row_count(timeframe)
        if row_count + missing_interval_count != calendar_row_count:
            raise BindingFailure(
                f"{slot_id}: observed rows plus declared gaps do not reconcile: "
                f"calendar={calendar_row_count}, rows={row_count}, "
                f"declared_gaps={missing_interval_count}"
            )
        if len(missing_interval_evidence) != missing_interval_count:
            raise BindingFailure(
                f"{slot_id}: missing interval ledger mismatch: "
                f"count={missing_interval_count}, ledger={len(missing_interval_evidence)}"
            )
        if duplicate_open_time_count or duplicate_close_time_count or invalid_ohlcv_row_count:
            raise BindingFailure(f"{slot_id}: integrity counts are non-zero")

        os.replace(temporary_path, final_path)
    except Exception:
        temporary_path.unlink(missing_ok=True)
        raise

    declared_gap_rows = [
        {
            "missing_open_time_utc": item.missing_open_time_utc,
            "previous_present_open_time_utc": item.previous_present_open_time_utc,
            "next_present_open_time_utc": item.next_present_open_time_utc,
            "interval_seconds": item.interval_seconds,
            "classification": item.classification,
            "source_archives_checksum_verified": item.source_archives_checksum_verified,
        }
        for item in missing_interval_evidence
    ]
    provenance_payload = {
        "archives": provenance_rows,
        "declared_missing_intervals": declared_gap_rows,
    }
    provenance_sha256 = sha256_bytes(
        canonical_json(provenance_payload).encode("utf-8")
    )

    relative_path = final_path.resolve().relative_to(root).as_posix()
    manifest_row: dict[str, str] = {
        "slot_id": slot_id,
        "symbol": symbol,
        "timeframe": timeframe,
        "role": ROLE_BY_TIMEFRAME[timeframe],
        "evidence_window_id": EVIDENCE_WINDOW_ID,
        "relative_path": relative_path,
        "file_sha256": sha256_file(final_path),
        "size_bytes": str(final_path.stat().st_size),
        "row_count": str(row_count),
        "first_open_time_utc": microseconds_to_utc_text(first_open_us),
        "last_close_time_utc": microseconds_to_utc_text(last_close_us),
        "expected_columns_json": canonical_json(list(CANONICAL_COLUMNS)),
        "timestamp_unit": "SOURCE_MILLISECONDS_THROUGH_2024_MICROSECONDS_FROM_2025_CANONICAL_RFC3339_UTC",
        "interval_seconds": str(INTERVAL_SECONDS[timeframe]),
        "source_provider": SOURCE_PROVIDER,
        "source_market": SOURCE_MARKET,
        "acquisition_method": ACQUISITION_METHOD,
        "acquisition_time_utc": acquisition_time_utc,
        "provenance_sha256": provenance_sha256,
        "duplicate_open_time_count": str(duplicate_open_time_count),
        "duplicate_close_time_count": str(duplicate_close_time_count),
        "missing_interval_count": str(missing_interval_count),
        "invalid_ohlcv_row_count": str(invalid_ohlcv_row_count),
        "binding_state": "BOUND_VERIFIED",
        "manifest_row_sha256": "",
    }
    manifest_row["manifest_row_sha256"] = canonical_row_sha256(manifest_row)
    return SlotResult(
        manifest_row=manifest_row,
        archive_evidence=archive_evidence,
        missing_interval_evidence=tuple(missing_interval_evidence),
    )


def write_manifest(path: Path, rows: list[dict[str, str]]) -> None:
    temporary = path.with_name(path.name + ".part")
    with temporary.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=MANIFEST_FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    os.replace(temporary, path)


def write_provenance(path: Path, rows: list[ArchiveEvidence]) -> None:
    fieldnames = (
        "slot_id",
        "archive_name",
        "archive_url",
        "checksum_url",
        "checksum_sha256",
        "zip_size_bytes",
    )
    temporary = path.with_name(path.name + ".part")
    with temporary.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for item in rows:
            writer.writerow(
                {
                    "slot_id": item.slot_id,
                    "archive_name": item.archive_name,
                    "archive_url": item.archive_url,
                    "checksum_url": item.checksum_url,
                    "checksum_sha256": item.checksum_sha256,
                    "zip_size_bytes": item.zip_size_bytes,
                }
            )
    os.replace(temporary, path)


def write_missing_interval_ledger(
    path: Path, rows: list[MissingIntervalEvidence]
) -> None:
    fieldnames = (
        "slot_id",
        "symbol",
        "timeframe",
        "missing_open_time_utc",
        "previous_present_open_time_utc",
        "next_present_open_time_utc",
        "interval_seconds",
        "classification",
        "source_archives_checksum_verified",
    )
    temporary = path.with_name(path.name + ".part")
    with temporary.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for item in rows:
            writer.writerow(
                {
                    "slot_id": item.slot_id,
                    "symbol": item.symbol,
                    "timeframe": item.timeframe,
                    "missing_open_time_utc": item.missing_open_time_utc,
                    "previous_present_open_time_utc": (
                        item.previous_present_open_time_utc
                    ),
                    "next_present_open_time_utc": item.next_present_open_time_utc,
                    "interval_seconds": item.interval_seconds,
                    "classification": item.classification,
                    "source_archives_checksum_verified": (
                        item.source_archives_checksum_verified
                    ),
                }
            )
    os.replace(temporary, path)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Acquire and bind the nine canonical Phase 10.42R.2J historical inputs."
    )
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--workers", type=int, default=6)
    parser.add_argument("--timeout-seconds", type=int, default=90)
    parser.add_argument("--retries", type=int, default=5)
    parser.add_argument("--cache-dir", type=Path, default=None)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = args.root.resolve()
    if not (root / ".git").exists():
        raise BindingFailure(f"Not a Git working tree root: {root}")

    output_dir = root / "data/market_input/local_csv_read_only/input"
    output_dir.mkdir(parents=True, exist_ok=True)

    default_cache_root = Path(os.environ.get("LOCALAPPDATA", tempfile.gettempdir()))
    cache_dir = (args.cache_dir or default_cache_root / "TradingAI/phase_10_42r_2j/monthly_archives").resolve()
    cache_dir.mkdir(parents=True, exist_ok=True)

    manifest_path = output_dir / "phase_10_42r_2j_historical_input_manifest_v1.csv"
    provenance_path = output_dir / "phase_10_42r_2j_archive_provenance_v1.csv"
    missing_interval_ledger_path = (
        output_dir / "phase_10_42r_2j_missing_interval_ledger_v1.csv"
    )
    previous_acquisition_times = load_previous_acquisition_times(manifest_path)

    tasks = build_archive_tasks(cache_dir)
    print(f"phase={PHASE}")
    print(f"schema_version={SCHEMA_VERSION}")
    print(f"gap_policy={GAP_POLICY}")
    print(f"archive_task_count={len(tasks)}")
    print(f"logical_slot_count={len(SYMBOLS) * len(TIMEFRAMES)}")
    print(f"cache_dir={cache_dir}")
    print(f"output_dir={output_dir}")
    print("historical_evaluation_count=0")
    print("backtest_execution_count=0")
    print("performance_metric_count=0")
    print("candidate_comparison_count=0")
    print("candidate_ranking_count=0")
    print("winner_selection_count=0")
    print("lockbox_access_count=0")
    print()

    evidence_by_archive: dict[str, ArchiveEvidence] = {}
    with ThreadPoolExecutor(max_workers=max(1, args.workers)) as executor:
        future_map = {
            executor.submit(
                ensure_archive,
                task,
                timeout_seconds=args.timeout_seconds,
                retries=args.retries,
            ): task
            for task in tasks
        }
        completed = 0
        for future in as_completed(future_map):
            task = future_map[future]
            evidence = future.result()
            evidence_by_archive[task.archive_name] = evidence
            completed += 1
            if completed % 12 == 0 or completed == len(tasks):
                print(f"verified_archives={completed}/{len(tasks)}")

    if len(evidence_by_archive) != len(tasks):
        raise BindingFailure("Not all archives were verified")

    run_acquisition_time = utc_now_text()
    slot_results: list[SlotResult] = []
    for symbol in SYMBOLS:
        for timeframe in TIMEFRAMES:
            slot_id = f"{symbol}_{timeframe.upper()}_{EVIDENCE_WINDOW_ID}"
            acquisition_time = previous_acquisition_times.get(slot_id, run_acquisition_time)
            result = build_slot(
                root=root,
                output_dir=output_dir,
                symbol=symbol,
                timeframe=timeframe,
                tasks=tasks,
                evidence_by_archive=evidence_by_archive,
                acquisition_time_utc=acquisition_time,
            )
            slot_results.append(result)
            row = result.manifest_row
            print(
                "slot_bound="
                + canonical_json(
                    {
                        "slot_id": row["slot_id"],
                        "relative_path": row["relative_path"],
                        "row_count": int(row["row_count"]),
                        "size_bytes": int(row["size_bytes"]),
                        "file_sha256": row["file_sha256"],
                        "missing_interval_count": int(row["missing_interval_count"]),
                        "binding_state": row["binding_state"],
                    }
                )
            )

    manifest_rows = [result.manifest_row for result in slot_results]
    manifest_rows.sort(key=lambda row: (SYMBOLS.index(row["symbol"]), TIMEFRAMES.index(row["timeframe"])))
    write_manifest(manifest_path, manifest_rows)

    provenance_rows = [item for result in slot_results for item in result.archive_evidence]
    provenance_rows.sort(key=lambda item: (item.slot_id, item.archive_name))
    write_provenance(provenance_path, provenance_rows)

    missing_interval_rows = [
        item
        for result in slot_results
        for item in result.missing_interval_evidence
    ]
    missing_interval_rows.sort(
        key=lambda item: (
            SYMBOLS.index(item.symbol),
            TIMEFRAMES.index(item.timeframe),
            item.missing_open_time_utc,
        )
    )
    write_missing_interval_ledger(
        missing_interval_ledger_path, missing_interval_rows
    )

    if len(manifest_rows) != 9:
        raise BindingFailure("Manifest does not contain exactly nine rows")
    if any(row["binding_state"] != "BOUND_VERIFIED" for row in manifest_rows):
        raise BindingFailure("Not all slots are BOUND_VERIFIED")
    if len(provenance_rows) != 432:
        raise BindingFailure(f"Expected 432 archive provenance rows, got {len(provenance_rows)}")
    declared_gap_total = sum(
        int(row["missing_interval_count"]) for row in manifest_rows
    )
    if declared_gap_total != len(missing_interval_rows):
        raise BindingFailure(
            "Manifest missing interval total does not match the gap ledger"
        )

    print()
    print("PHASE 10.42R.2J ACQUISITION AND BINDING SUMMARY")
    print(f"verified_archive_count={len(provenance_rows)}")
    print(f"bound_slot_count={len(manifest_rows)}")
    print(f"manifest_path={manifest_path.resolve().relative_to(root).as_posix()}")
    print(f"manifest_sha256={sha256_file(manifest_path)}")
    print(f"provenance_path={provenance_path.resolve().relative_to(root).as_posix()}")
    print(f"provenance_sha256={sha256_file(provenance_path)}")
    print(
        "missing_interval_ledger_path="
        + missing_interval_ledger_path.resolve().relative_to(root).as_posix()
    )
    print(
        f"missing_interval_ledger_sha256="
        f"{sha256_file(missing_interval_ledger_path)}"
    )
    print("missing_slot_count=0")
    print("ambiguous_slot_count=0")
    print("invalid_shape_slot_count=0")
    print("duplicate_open_time_count=0")
    print("duplicate_close_time_count=0")
    print(f"declared_source_missing_interval_count={declared_gap_total}")
    print(f"missing_interval_ledger_row_count={len(missing_interval_rows)}")
    print("calendar_row_count_reconciled=True")
    for row in manifest_rows:
        print(
            "slot_missing_interval_count="
            + canonical_json(
                {
                    "slot_id": row["slot_id"],
                    "missing_interval_count": int(
                        row["missing_interval_count"]
                    ),
                }
            )
        )
    print("all_missing_intervals_declared=True")
    print("synthetic_gap_fill_count=0")
    print("invalid_ohlcv_row_count=0")
    print("historical_evaluation_count=0")
    print("backtest_execution_count=0")
    print("performance_metric_count=0")
    print("candidate_comparison_count=0")
    print("candidate_ranking_count=0")
    print("winner_selection_count=0")
    print("lockbox_access_count=0")
    print("binding_completed=True")
    print("historical_evaluation_allowed=False")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except BindingFailure as exc:
        print(f"binding_completed=False", file=sys.stderr)
        print(f"failure={type(exc).__name__}: {exc}", file=sys.stderr)
        raise SystemExit(1)
