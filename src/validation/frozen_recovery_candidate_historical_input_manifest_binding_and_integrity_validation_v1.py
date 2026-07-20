from __future__ import annotations

import csv
import hashlib
import json
import math
import subprocess
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any, Iterable


PHASE = "10.42R.2J"
SCHEMA_VERSION = "HISTORICAL_INPUT_MANIFEST_BINDING_AND_INTEGRITY_VALIDATION_V1"
SOURCE_PHASE_2I_COMMIT = "ddcd059bd747891c47e2738974b1b42465ba5adf"
SOURCE_PHASE_2I_HARNESS_DESIGN_SHA256 = (
    "ee62064148bdb119c7b3390d7dab3db338b4d5b50a1eaf7adb44d4c9dffd5dbb"
)
ACQUISITION_SOURCE_SHA256 = (
    "d824c562f331cce54a92fb66aaaac59daec2024e0733dabcacf8d668ff9c7c14"
)
RECOMMENDED_NEXT_PHASE = (
    "PHASE_10_42R_2K_FROZEN_RECOVERY_CANDIDATE_"
    "CONTROLLED_KNOWN_EVIDENCE_EVALUATION_V1"
)

SOURCE_PROVIDER = "BINANCE_PUBLIC_DATA"
SOURCE_MARKET = "BINANCE_SPOT"
ACQUISITION_METHOD = "MONTHLY_KLINE_ARCHIVE_WITH_SHA256_CHECKSUM"
GAP_POLICY = "PRESERVE_AND_DECLARE_CHECKSUM_VERIFIED_SOURCE_GAPS_NO_INTERPOLATION"
EVIDENCE_WINDOW_ID = "KNOWN_EVIDENCE_2022_2025"
START_UTC = datetime(2022, 1, 1, tzinfo=timezone.utc)
END_UTC = datetime(2026, 1, 1, tzinfo=timezone.utc)

SYMBOLS = ("BTCUSDT", "ETHUSDT", "SOLUSDT")
TIMEFRAMES = ("15m", "1h", "4h")
INTERVAL_SECONDS = {"15m": 900, "1h": 3600, "4h": 14400}
ROLE_BY_TIMEFRAME = {
    "15m": "PRIMARY_SIGNAL_AND_SIMULATED_EXECUTION",
    "1h": "CLOSED_CONTEXT_ONLY",
    "4h": "CLOSED_CONTEXT_ONLY",
}
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
PROVENANCE_FIELDS = (
    "slot_id",
    "archive_name",
    "archive_url",
    "checksum_url",
    "checksum_sha256",
    "zip_size_bytes",
)
MISSING_INTERVAL_FIELDS = (
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

INPUT_DIR = Path("data/market_input/local_csv_read_only/input")
MANIFEST_PATH = INPUT_DIR / "phase_10_42r_2j_historical_input_manifest_v1.csv"
PROVENANCE_PATH = INPUT_DIR / "phase_10_42r_2j_archive_provenance_v1.csv"
MISSING_INTERVAL_LEDGER_PATH = (
    INPUT_DIR / "phase_10_42r_2j_missing_interval_ledger_v1.csv"
)

EXPECTED_AUDIT_ARTIFACT_HASHES = {
    MANIFEST_PATH.as_posix(): "40982ff9b92de06df6413fd3d2f448ff4e10f9fdd266cffb0c4945dccd02799c",
    PROVENANCE_PATH.as_posix(): "9c77fac16b34d7a98ae72f251a1015358c9d2dd2899e593d1314bbc6679eabde",
    MISSING_INTERVAL_LEDGER_PATH.as_posix(): "2b079dbd2347f594091a669f608866b8df743ecd3a075a34670c8f05bbf11331",
}

EXPECTED_DATASETS = {
    "BTCUSDT_15M_KNOWN_EVIDENCE_2022_2025": {
        "symbol": "BTCUSDT",
        "timeframe": "15m",
        "relative_path": "data/market_input/local_csv_read_only/input/phase_10_42r_2j_btcusdt_15m_spot_2022_2025_v1.csv",
        "file_sha256": "2d8ff771274b86202866722644e843aba32228463d9fd191f967577b8878dc3b",
        "size_bytes": 19588185,
        "row_count": 140251,
        "missing_interval_count": 5,
    },
    "BTCUSDT_1H_KNOWN_EVIDENCE_2022_2025": {
        "symbol": "BTCUSDT",
        "timeframe": "1h",
        "relative_path": "data/market_input/local_csv_read_only/input/phase_10_42r_2j_btcusdt_1h_spot_2022_2025_v1.csv",
        "file_sha256": "56aab93c9e336babdcfec82b2d022d5f079638ceeb95c19018853c59ae78951e",
        "size_bytes": 4917400,
        "row_count": 35063,
        "missing_interval_count": 1,
    },
    "BTCUSDT_4H_KNOWN_EVIDENCE_2022_2025": {
        "symbol": "BTCUSDT",
        "timeframe": "4h",
        "relative_path": "data/market_input/local_csv_read_only/input/phase_10_42r_2j_btcusdt_4h_spot_2022_2025_v1.csv",
        "file_sha256": "8679bb2a138db53e2a54eb409ef3c82755a3fa042f8c1d65b23314d79b9bb196",
        "size_bytes": 1234933,
        "row_count": 8766,
        "missing_interval_count": 0,
    },
    "ETHUSDT_15M_KNOWN_EVIDENCE_2022_2025": {
        "symbol": "ETHUSDT",
        "timeframe": "15m",
        "relative_path": "data/market_input/local_csv_read_only/input/phase_10_42r_2j_ethusdt_15m_spot_2022_2025_v1.csv",
        "file_sha256": "4ef8ecbe67df362ffb8227bed6cfd577397284ad98a4a6e1bd8f4607eb6b6e59",
        "size_bytes": 19080778,
        "row_count": 140251,
        "missing_interval_count": 5,
    },
    "ETHUSDT_1H_KNOWN_EVIDENCE_2022_2025": {
        "symbol": "ETHUSDT",
        "timeframe": "1h",
        "relative_path": "data/market_input/local_csv_read_only/input/phase_10_42r_2j_ethusdt_1h_spot_2022_2025_v1.csv",
        "file_sha256": "f45a1bf3803818931ed14db5b20429b75b7fefc5b0c90a8554bbf5055fcfca70",
        "size_bytes": 4792596,
        "row_count": 35063,
        "missing_interval_count": 1,
    },
    "ETHUSDT_4H_KNOWN_EVIDENCE_2022_2025": {
        "symbol": "ETHUSDT",
        "timeframe": "4h",
        "relative_path": "data/market_input/local_csv_read_only/input/phase_10_42r_2j_ethusdt_4h_spot_2022_2025_v1.csv",
        "file_sha256": "317d8bae4d74ae7aea10500cef3514b80e684859e0eb97ad8d69763985dd70b7",
        "size_bytes": 1203329,
        "row_count": 8766,
        "missing_interval_count": 0,
    },
    "SOLUSDT_15M_KNOWN_EVIDENCE_2022_2025": {
        "symbol": "SOLUSDT",
        "timeframe": "15m",
        "relative_path": "data/market_input/local_csv_read_only/input/phase_10_42r_2j_solusdt_15m_spot_2022_2025_v1.csv",
        "file_sha256": "4c70aa25c9a79ab4c09753152cbffc35be48299d0b27279e14720dc3931a9747",
        "size_bytes": 18388960,
        "row_count": 140251,
        "missing_interval_count": 5,
    },
    "SOLUSDT_1H_KNOWN_EVIDENCE_2022_2025": {
        "symbol": "SOLUSDT",
        "timeframe": "1h",
        "relative_path": "data/market_input/local_csv_read_only/input/phase_10_42r_2j_solusdt_1h_spot_2022_2025_v1.csv",
        "file_sha256": "d82d9979af9cd786d70a74cccf727e984281517ddf561c4c92ad3ca6c2044598",
        "size_bytes": 4619122,
        "row_count": 35063,
        "missing_interval_count": 1,
    },
    "SOLUSDT_4H_KNOWN_EVIDENCE_2022_2025": {
        "symbol": "SOLUSDT",
        "timeframe": "4h",
        "relative_path": "data/market_input/local_csv_read_only/input/phase_10_42r_2j_solusdt_4h_spot_2022_2025_v1.csv",
        "file_sha256": "f354b3cc4ea6c111955a2160061f8dfcd0a6d93a274964a3844ec03463bd0541",
        "size_bytes": 1159922,
        "row_count": 8766,
        "missing_interval_count": 0,
    },
}

EXPECTED_SOURCE_HASHES = {
    "PHASE_10_42R_2I_MANIFEST.sha256": "6114a67419b9c95619afb8816224b9b71e47d62cebdbb3f2f93e4568015ae31e",
    "docs/PHASE_10_42R_2I_FROZEN_RECOVERY_CANDIDATE_CONTROLLED_HISTORICAL_EVALUATION_HARNESS_DESIGN.md": "6e8644f36a95fd5786506244c18ddbe1dd3db69d0eaaf95acdfafef759fe6a83",
    "src/validation/frozen_recovery_candidate_controlled_historical_evaluation_harness_design_v1.py": "e885aca401384d0ea1db40eada96846081eb4661e88634fb26837769230a2913",
}

PERMISSIONS = {
    "real_data_access_allowed": True,
    "historical_input_binding_allowed": True,
    "historical_file_hashing_allowed": True,
    "historical_schema_parsing_allowed": True,
    "historical_evaluation_allowed": False,
    "retrospective_lockbox_access_allowed": False,
    "prospective_holdout_access_allowed": False,
    "performance_metrics_allowed": False,
    "candidate_comparison_allowed": False,
    "candidate_ranking_allowed": False,
    "winner_selection_allowed": False,
    "candidate_mutation_allowed": False,
    "forward_observation_allowed": False,
    "official_dataset_write_allowed": False,
    "signal_generation_enabled": False,
    "live_alerts_allowed": False,
    "paper_trade_execution_allowed": False,
    "real_capital_allowed": False,
    "market_execution_allowed": False,
    "exchange_execution_allowed": False,
    "automation_allowed": False,
    "execution_allowed": False,
    "openclaw_operational_integration_allowed": False,
}
ALLOWED_TRUE_PERMISSIONS = {
    "real_data_access_allowed",
    "historical_input_binding_allowed",
    "historical_file_hashing_allowed",
    "historical_schema_parsing_allowed",
}

FORBIDDEN_ARTIFACT_PATHS = (
    Path("data/holdout/strategy_recovery_retrospective_lockbox_2026h1_v1.csv"),
    Path("data/holdout/strategy_recovery_prospective_20260720_20270120_v1.csv"),
    Path("data/forward/long_forward_observation_dataset_v1.csv"),
)


@dataclass(frozen=True)
class Check:
    check_id: str
    check_name: str
    passed: bool
    details: str
    blocker: bool


class BindingIntegrityFailure(RuntimeError):
    pass


def canonical_json(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def normalized_source_sha256(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    return sha256_bytes(text.encode("utf-8"))


def canonical_manifest_row_sha256(row: dict[str, str]) -> str:
    payload = {
        field: row[field]
        for field in MANIFEST_FIELDS
        if field != "manifest_row_sha256"
    }
    return sha256_bytes(canonical_json(payload).encode("utf-8"))


def expected_calendar_rows(timeframe: str) -> int:
    seconds = int((END_UTC - START_UTC).total_seconds())
    interval = INTERVAL_SECONDS[timeframe]
    if seconds % interval:
        raise BindingIntegrityFailure("Evidence window is not divisible by interval")
    return seconds // interval


def parse_utc(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise BindingIntegrityFailure(f"Timestamp is not timezone-aware: {value}")
    return parsed.astimezone(timezone.utc)


def datetime_to_microseconds(value: datetime) -> int:
    normalized = value.astimezone(timezone.utc)
    epoch = datetime(1970, 1, 1, tzinfo=timezone.utc)
    delta = normalized - epoch
    return (
        delta.days * 86_400_000_000
        + delta.seconds * 1_000_000
        + delta.microseconds
    )


def _decimal(value: str) -> Decimal:
    try:
        parsed = Decimal(value)
    except InvalidOperation as exc:
        raise BindingIntegrityFailure(f"Invalid decimal: {value}") from exc
    if not parsed.is_finite():
        raise BindingIntegrityFailure(f"Non-finite decimal: {value}")
    return parsed


def validate_ohlcv(row: dict[str, str]) -> None:
    open_value = _decimal(row["open"])
    high_value = _decimal(row["high"])
    low_value = _decimal(row["low"])
    close_value = _decimal(row["close"])
    volume_value = _decimal(row["volume"])
    if volume_value < 0:
        raise BindingIntegrityFailure("Negative volume")
    if high_value < low_value:
        raise BindingIntegrityFailure("High below low")
    if high_value < max(open_value, close_value):
        raise BindingIntegrityFailure("High below open/close")
    if low_value > min(open_value, close_value):
        raise BindingIntegrityFailure("Low above open/close")


def read_csv_rows(path: Path) -> tuple[tuple[str, ...], list[dict[str, str]]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        fieldnames = tuple(reader.fieldnames or ())
        rows = [dict(row) for row in reader]
    return fieldnames, rows


def scan_dataset(path: Path, timeframe: str) -> dict[str, Any]:
    interval_seconds = INTERVAL_SECONDS[timeframe]
    interval_us = interval_seconds * 1_000_000
    row_count = 0
    duplicate_open_time_count = 0
    duplicate_close_time_count = 0
    missing_interval_count = 0
    invalid_ohlcv_row_count = 0
    first_open: datetime | None = None
    last_close: datetime | None = None
    previous_open_us: int | None = None
    previous_close_us: int | None = None
    missing_open_times: list[str] = []

    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != CANONICAL_COLUMNS:
            raise BindingIntegrityFailure(
                f"Unexpected dataset schema for {path}: {reader.fieldnames}"
            )
        for row in reader:
            open_time = parse_utc(row["open_time_utc"])
            close_time = parse_utc(row["close_time_utc"])
            open_us = datetime_to_microseconds(open_time)
            close_us = datetime_to_microseconds(close_time)
            try:
                validate_ohlcv(row)
            except BindingIntegrityFailure:
                invalid_ohlcv_row_count += 1
                raise
            if close_us <= open_us or close_us >= open_us + interval_us:
                raise BindingIntegrityFailure("Close timestamp outside candle boundary")
            if previous_open_us is not None:
                delta = open_us - previous_open_us
                if delta == 0:
                    duplicate_open_time_count += 1
                    raise BindingIntegrityFailure("Duplicate open timestamp")
                if delta < 0 or delta % interval_us:
                    raise BindingIntegrityFailure("Non-monotonic or irregular open timestamp")
                gap_count = delta // interval_us - 1
                missing_interval_count += gap_count
                for index in range(1, gap_count + 1):
                    missing_us = previous_open_us + index * interval_us
                    seconds, micros = divmod(missing_us, 1_000_000)
                    missing_open_times.append(
                        datetime.fromtimestamp(seconds, tz=timezone.utc)
                        .replace(microsecond=micros)
                        .isoformat(timespec="microseconds")
                    )
            if previous_close_us is not None:
                if close_us == previous_close_us:
                    duplicate_close_time_count += 1
                    raise BindingIntegrityFailure("Duplicate close timestamp")
                if close_us < previous_close_us:
                    raise BindingIntegrityFailure("Non-monotonic close timestamp")
            if first_open is None:
                first_open = open_time
            last_close = close_time
            previous_open_us = open_us
            previous_close_us = close_us
            row_count += 1

    return {
        "row_count": row_count,
        "first_open_time_utc": first_open.isoformat(timespec="microseconds") if first_open else "",
        "last_close_time_utc": last_close.isoformat(timespec="microseconds") if last_close else "",
        "duplicate_open_time_count": duplicate_open_time_count,
        "duplicate_close_time_count": duplicate_close_time_count,
        "missing_interval_count": missing_interval_count,
        "invalid_ohlcv_row_count": invalid_ohlcv_row_count,
        "missing_open_times": tuple(missing_open_times),
    }


def build_binding_root_sha256() -> str:
    payload = {
        "phase": PHASE,
        "schema_version": SCHEMA_VERSION,
        "source_phase_2i_commit": SOURCE_PHASE_2I_COMMIT,
        "source_phase_2i_harness_design_sha256": SOURCE_PHASE_2I_HARNESS_DESIGN_SHA256,
        "acquisition_source_sha256": ACQUISITION_SOURCE_SHA256,
        "gap_policy": GAP_POLICY,
        "audit_artifacts": EXPECTED_AUDIT_ARTIFACT_HASHES,
        "datasets": EXPECTED_DATASETS,
    }
    return sha256_bytes(canonical_json(payload).encode("utf-8"))


BINDING_ROOT_SHA256 = build_binding_root_sha256()


def _append(checks: list[Check], name: str, passed: bool, details: str) -> None:
    checks.append(
        Check(
            check_id=f"2J-CHECK-{len(checks) + 1:03d}",
            check_name=name,
            passed=bool(passed),
            details=details,
            blocker=not bool(passed),
        )
    )


def _source_commit_is_ancestor(root: Path) -> tuple[bool, str]:
    result = subprocess.run(
        ["git", "merge-base", "--is-ancestor", SOURCE_PHASE_2I_COMMIT, "HEAD"],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )
    return result.returncode == 0, f"returncode={result.returncode}"


def _path_is_ignored(root: Path, relative_path: str) -> bool:
    result = subprocess.run(
        ["git", "check-ignore", "--quiet", "--", relative_path],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )
    return result.returncode == 0


def _validate_permissions() -> bool:
    true_permissions = {name for name, value in PERMISSIONS.items() if value}
    return true_permissions == ALLOWED_TRUE_PERMISSIONS


def _provenance_payload_for_slot(
    slot_id: str,
    provenance_rows: Iterable[dict[str, str]],
    gap_rows: Iterable[dict[str, str]],
) -> dict[str, Any]:
    archives = [
        {
            "archive_name": row["archive_name"],
            "archive_url": row["archive_url"],
            "checksum_url": row["checksum_url"],
            "checksum_sha256": row["checksum_sha256"],
            "zip_size_bytes": int(row["zip_size_bytes"]),
        }
        for row in provenance_rows
        if row["slot_id"] == slot_id
    ]
    archives.sort(key=lambda row: row["archive_name"])
    gaps = [
        {
            "missing_open_time_utc": row["missing_open_time_utc"],
            "previous_present_open_time_utc": row["previous_present_open_time_utc"],
            "next_present_open_time_utc": row["next_present_open_time_utc"],
            "interval_seconds": int(row["interval_seconds"]),
            "classification": row["classification"],
            "source_archives_checksum_verified": row[
                "source_archives_checksum_verified"
            ].strip().lower()
            == "true",
        }
        for row in gap_rows
        if row["slot_id"] == slot_id
    ]
    gaps.sort(key=lambda row: row["missing_open_time_utc"])
    return {"archives": archives, "declared_missing_intervals": gaps}


def validate_phase_10_42r_2j(
    *, preflight_only: bool = False, root: Path | None = None
) -> dict[str, Any]:
    project_root = (root or Path.cwd()).resolve()
    checks: list[Check] = []

    passed, details = _source_commit_is_ancestor(project_root)
    _append(checks, "source_phase_2i_commit_is_ancestor", passed, details)

    for relative_path, expected_hash in EXPECTED_SOURCE_HASHES.items():
        path = project_root / relative_path
        actual = normalized_source_sha256(path) if path.is_file() else ""
        _append(
            checks,
            "source_anchor_" + relative_path.replace("/", "_"),
            path.is_file() and actual == expected_hash,
            f"expected={expected_hash},actual={actual}",
        )

    acquisition_path = project_root / (
        "src/validation/frozen_recovery_candidate_historical_input_"
        "acquisition_and_binding_v1.py"
    )
    actual_acquisition_hash = (
        normalized_source_sha256(acquisition_path) if acquisition_path.is_file() else ""
    )
    _append(
        checks,
        "acquisition_source_exact",
        acquisition_path.is_file() and actual_acquisition_hash == ACQUISITION_SOURCE_SHA256,
        f"expected={ACQUISITION_SOURCE_SHA256},actual={actual_acquisition_hash}",
    )

    _append(
        checks,
        "limited_permissions_exact",
        _validate_permissions(),
        canonical_json({name: value for name, value in PERMISSIONS.items() if value}),
    )
    _append(
        checks,
        "historical_evaluation_permission_false",
        not PERMISSIONS["historical_evaluation_allowed"],
        "false",
    )
    _append(
        checks,
        "lockboxes_and_forward_dataset_absent",
        not any((project_root / path).exists() for path in FORBIDDEN_ARTIFACT_PATHS),
        ",".join(
            path.as_posix()
            for path in FORBIDDEN_ARTIFACT_PATHS
            if (project_root / path).exists()
        ),
    )
    _append(
        checks,
        "binding_root_deterministic",
        BINDING_ROOT_SHA256 == build_binding_root_sha256(),
        BINDING_ROOT_SHA256,
    )

    preflight_count = len(checks)
    dataset_scan_count = 0
    historical_file_hash_read_count = 0
    historical_schema_parse_count = 0
    real_data_content_read_count = 0

    if not preflight_only:
        audit_paths = {
            relative_path: project_root / relative_path
            for relative_path in EXPECTED_AUDIT_ARTIFACT_HASHES
        }
        for relative_path, expected_hash in EXPECTED_AUDIT_ARTIFACT_HASHES.items():
            path = audit_paths[relative_path]
            actual_hash = sha256_file(path) if path.is_file() else ""
            historical_file_hash_read_count += int(path.is_file())
            real_data_content_read_count += int(path.is_file())
            _append(
                checks,
                "audit_artifact_hash_" + Path(relative_path).name,
                path.is_file() and actual_hash == expected_hash,
                f"expected={expected_hash},actual={actual_hash}",
            )

        manifest_fields, manifest_rows = read_csv_rows(project_root / MANIFEST_PATH)
        provenance_fields, provenance_rows = read_csv_rows(project_root / PROVENANCE_PATH)
        ledger_fields, ledger_rows = read_csv_rows(
            project_root / MISSING_INTERVAL_LEDGER_PATH
        )
        historical_schema_parse_count += 3

        _append(checks, "manifest_schema_exact", manifest_fields == MANIFEST_FIELDS, str(manifest_fields))
        _append(checks, "provenance_schema_exact", provenance_fields == PROVENANCE_FIELDS, str(provenance_fields))
        _append(checks, "missing_interval_schema_exact", ledger_fields == MISSING_INTERVAL_FIELDS, str(ledger_fields))
        _append(checks, "manifest_row_count_nine", len(manifest_rows) == 9, str(len(manifest_rows)))
        _append(checks, "provenance_row_count_432", len(provenance_rows) == 432, str(len(provenance_rows)))
        _append(checks, "missing_interval_row_count_18", len(ledger_rows) == 18, str(len(ledger_rows)))

        manifest_by_slot = {row["slot_id"]: row for row in manifest_rows}
        _append(
            checks,
            "manifest_slot_registry_exact",
            set(manifest_by_slot) == set(EXPECTED_DATASETS),
            canonical_json(sorted(manifest_by_slot)),
        )

        gap_times_by_slot: dict[str, set[str]] = {}
        for row in ledger_rows:
            gap_times_by_slot.setdefault(row["slot_id"], set()).add(
                row["missing_open_time_utc"]
            )
        _append(
            checks,
            "missing_interval_ledger_unique",
            sum(len(values) for values in gap_times_by_slot.values()) == len(ledger_rows),
            str(len(ledger_rows)),
        )
        _append(
            checks,
            "gap_classification_exact",
            all(
                row["classification"]
                == "DECLARED_GAP_IN_CHECKSUM_VERIFIED_BINANCE_ARCHIVES"
                and row["source_archives_checksum_verified"].strip().lower() == "true"
                for row in ledger_rows
            ),
            GAP_POLICY,
        )

        for slot_id, expected in EXPECTED_DATASETS.items():
            row = manifest_by_slot.get(slot_id, {})
            timeframe = expected["timeframe"]
            relative_path = expected["relative_path"]
            path = project_root / relative_path

            exact_manifest_values = bool(row) and all(
                (
                    row.get("symbol") == expected["symbol"],
                    row.get("timeframe") == timeframe,
                    row.get("role") == ROLE_BY_TIMEFRAME[timeframe],
                    row.get("evidence_window_id") == EVIDENCE_WINDOW_ID,
                    row.get("relative_path") == relative_path,
                    row.get("file_sha256") == expected["file_sha256"],
                    row.get("size_bytes") == str(expected["size_bytes"]),
                    row.get("row_count") == str(expected["row_count"]),
                    row.get("interval_seconds") == str(INTERVAL_SECONDS[timeframe]),
                    row.get("source_provider") == SOURCE_PROVIDER,
                    row.get("source_market") == SOURCE_MARKET,
                    row.get("acquisition_method") == ACQUISITION_METHOD,
                    row.get("duplicate_open_time_count") == "0",
                    row.get("duplicate_close_time_count") == "0",
                    row.get("missing_interval_count")
                    == str(expected["missing_interval_count"]),
                    row.get("invalid_ohlcv_row_count") == "0",
                    row.get("binding_state") == "BOUND_VERIFIED",
                    row.get("expected_columns_json")
                    == canonical_json(list(CANONICAL_COLUMNS)),
                )
            )
            _append(
                checks,
                f"manifest_values_exact_{slot_id}",
                exact_manifest_values,
                relative_path,
            )
            _append(
                checks,
                f"manifest_row_hash_exact_{slot_id}",
                bool(row)
                and row.get("manifest_row_sha256")
                == canonical_manifest_row_sha256(row),
                row.get("manifest_row_sha256", ""),
            )

            actual_size = path.stat().st_size if path.is_file() else -1
            actual_hash = sha256_file(path) if path.is_file() else ""
            historical_file_hash_read_count += int(path.is_file())
            real_data_content_read_count += int(path.is_file())
            _append(
                checks,
                f"dataset_size_exact_{slot_id}",
                path.is_file() and actual_size == expected["size_bytes"],
                f"expected={expected['size_bytes']},actual={actual_size}",
            )
            _append(
                checks,
                f"dataset_hash_exact_{slot_id}",
                path.is_file() and actual_hash == expected["file_sha256"],
                f"expected={expected['file_sha256']},actual={actual_hash}",
            )
            _append(
                checks,
                f"dataset_git_ignored_{slot_id}",
                _path_is_ignored(project_root, relative_path),
                relative_path,
            )

            scan = scan_dataset(path, timeframe) if path.is_file() else {}
            dataset_scan_count += int(path.is_file())
            historical_schema_parse_count += int(path.is_file())
            _append(
                checks,
                f"dataset_scan_counts_exact_{slot_id}",
                bool(scan)
                and scan["row_count"] == expected["row_count"]
                and scan["missing_interval_count"]
                == expected["missing_interval_count"]
                and scan["duplicate_open_time_count"] == 0
                and scan["duplicate_close_time_count"] == 0
                and scan["invalid_ohlcv_row_count"] == 0,
                canonical_json(scan) if scan else "missing",
            )
            _append(
                checks,
                f"dataset_boundaries_match_manifest_{slot_id}",
                bool(scan)
                and scan["first_open_time_utc"] == row.get("first_open_time_utc")
                and scan["last_close_time_utc"] == row.get("last_close_time_utc"),
                f"first={scan.get('first_open_time_utc','')},last={scan.get('last_close_time_utc','')}",
            )
            _append(
                checks,
                f"calendar_reconciled_{slot_id}",
                bool(scan)
                and scan["row_count"] + scan["missing_interval_count"]
                == expected_calendar_rows(timeframe),
                f"calendar={expected_calendar_rows(timeframe)}",
            )
            _append(
                checks,
                f"gap_ledger_matches_dataset_{slot_id}",
                bool(scan)
                and set(scan["missing_open_times"])
                == gap_times_by_slot.get(slot_id, set()),
                f"dataset={len(scan.get('missing_open_times',()))},ledger={len(gap_times_by_slot.get(slot_id,set()))}",
            )

            slot_provenance = [
                item for item in provenance_rows if item["slot_id"] == slot_id
            ]
            _append(
                checks,
                f"archive_provenance_count_48_{slot_id}",
                len(slot_provenance) == 48,
                str(len(slot_provenance)),
            )
            _append(
                checks,
                f"archive_provenance_contract_{slot_id}",
                all(
                    item["archive_url"].startswith(
                        "https://data.binance.vision/data/spot/monthly/klines/"
                    )
                    and item["checksum_url"] == item["archive_url"] + ".CHECKSUM"
                    and len(item["checksum_sha256"]) == 64
                    and int(item["zip_size_bytes"]) > 0
                    for item in slot_provenance
                ),
                str(len(slot_provenance)),
            )
            provenance_payload = _provenance_payload_for_slot(
                slot_id, provenance_rows, ledger_rows
            )
            actual_provenance_hash = sha256_bytes(
                canonical_json(provenance_payload).encode("utf-8")
            )
            _append(
                checks,
                f"slot_provenance_hash_exact_{slot_id}",
                bool(row) and row.get("provenance_sha256") == actual_provenance_hash,
                f"expected={row.get('provenance_sha256','')},actual={actual_provenance_hash}",
            )

        _append(
            checks,
            "declared_gap_total_18",
            sum(int(row["missing_interval_count"]) for row in manifest_rows) == 18,
            str(sum(int(row["missing_interval_count"]) for row in manifest_rows)),
        )
        _append(
            checks,
            "no_synthetic_gap_fill",
            all(
                int(row["row_count"]) + int(row["missing_interval_count"])
                == expected_calendar_rows(row["timeframe"])
                for row in manifest_rows
            ),
            "synthetic_gap_fill_count=0",
        )

    failed = tuple(check for check in checks if not check.passed)
    validation_passed = not failed
    decision = (
        "PREFLIGHT_PASSED"
        if preflight_only and validation_passed
        else "HISTORICAL_INPUT_MANIFEST_BOUND_AND_INTEGRITY_VALIDATED"
        if validation_passed
        else "HISTORICAL_INPUT_MANIFEST_BINDING_AND_INTEGRITY_BLOCKED"
    )

    summary = {
        "phase": PHASE,
        "preflight_only": preflight_only,
        "source_phase_2i_commit": SOURCE_PHASE_2I_COMMIT,
        "source_phase_2i_harness_design_sha256": SOURCE_PHASE_2I_HARNESS_DESIGN_SHA256,
        "acquisition_source_sha256": ACQUISITION_SOURCE_SHA256,
        "binding_root_sha256": BINDING_ROOT_SHA256,
        "gap_policy": GAP_POLICY,
        "logical_slot_count": len(EXPECTED_DATASETS),
        "audit_artifact_count": len(EXPECTED_AUDIT_ARTIFACT_HASHES),
        "verified_archive_count": 432 if validation_passed and not preflight_only else 0,
        "declared_source_missing_interval_count": 18 if validation_passed and not preflight_only else 0,
        "synthetic_gap_fill_count": 0,
        "preflight_check_count": preflight_count,
        "binding_check_count": 0 if preflight_only else len(checks) - preflight_count,
        "total_check_count": len(checks),
        "failed_check_count": len(failed),
        "blocker_count": len(failed),
        "real_data_content_read_count": real_data_content_read_count,
        "historical_file_hash_read_count": historical_file_hash_read_count,
        "historical_schema_parse_count": historical_schema_parse_count,
        "dataset_scan_count": dataset_scan_count,
        "historical_evaluation_count": 0,
        "backtest_execution_count": 0,
        "performance_metric_count": 0,
        "candidate_comparison_count": 0,
        "candidate_ranking_count": 0,
        "winner_selection_count": 0,
        "retrospective_lockbox_access_count": 0,
        "prospective_holdout_access_count": 0,
        "result_artifact_write_count": 0,
        "limited_permissions_enabled_count": sum(PERMISSIONS.values()),
        "operational_permissions_enabled_count": 0,
        "binding_completed": bool(validation_passed and not preflight_only),
        "binding_frozen": bool(validation_passed and not preflight_only),
        "historical_evaluation_allowed": False,
        "repair_cycle_open": False,
        "validation_decision": decision,
        "validation_passed": validation_passed,
        "recommended_next_phase": (
            RECOMMENDED_NEXT_PHASE if validation_passed and not preflight_only else "NONE"
        ),
    }
    return {
        "summary": summary,
        "checks": tuple(asdict(check) for check in checks),
        "failed_checks": tuple(asdict(check) for check in failed),
        "permissions": dict(PERMISSIONS),
        "expected_datasets": EXPECTED_DATASETS,
        "expected_audit_artifact_hashes": EXPECTED_AUDIT_ARTIFACT_HASHES,
    }


def require_valid_binding(
    *, preflight_only: bool = False, root: Path | None = None
) -> dict[str, Any]:
    result = validate_phase_10_42r_2j(preflight_only=preflight_only, root=root)
    if not result["summary"]["validation_passed"]:
        names = ", ".join(item["check_name"] for item in result["failed_checks"])
        raise BindingIntegrityFailure("Phase 10.42R.2J failed: " + names)
    return result


__all__ = [
    "ACQUISITION_METHOD",
    "ACQUISITION_SOURCE_SHA256",
    "ALLOWED_TRUE_PERMISSIONS",
    "BINDING_ROOT_SHA256",
    "BindingIntegrityFailure",
    "CANONICAL_COLUMNS",
    "END_UTC",
    "EVIDENCE_WINDOW_ID",
    "EXPECTED_AUDIT_ARTIFACT_HASHES",
    "EXPECTED_DATASETS",
    "GAP_POLICY",
    "INPUT_DIR",
    "INTERVAL_SECONDS",
    "MANIFEST_FIELDS",
    "MANIFEST_PATH",
    "MISSING_INTERVAL_FIELDS",
    "MISSING_INTERVAL_LEDGER_PATH",
    "PERMISSIONS",
    "PHASE",
    "PROVENANCE_FIELDS",
    "PROVENANCE_PATH",
    "RECOMMENDED_NEXT_PHASE",
    "ROLE_BY_TIMEFRAME",
    "SCHEMA_VERSION",
    "SOURCE_MARKET",
    "SOURCE_PHASE_2I_COMMIT",
    "SOURCE_PHASE_2I_HARNESS_DESIGN_SHA256",
    "SOURCE_PROVIDER",
    "START_UTC",
    "SYMBOLS",
    "TIMEFRAMES",
    "build_binding_root_sha256",
    "canonical_json",
    "canonical_manifest_row_sha256",
    "datetime_to_microseconds",
    "expected_calendar_rows",
    "normalized_source_sha256",
    "parse_utc",
    "read_csv_rows",
    "require_valid_binding",
    "scan_dataset",
    "sha256_file",
    "validate_ohlcv",
    "validate_phase_10_42r_2j",
]
