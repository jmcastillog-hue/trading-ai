from __future__ import annotations

import csv
import hashlib
import json
import os
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Callable, Mapping

CAPABILITY = "SYNCHRONIZED_15M_OBSERVATION_V1"
IMPLEMENTATION_SCHEMA_VERSION = "SYNCHRONIZED_15M_OBSERVATION_IMPLEMENTATION_V1"
SESSION_SCHEMA_VERSION = "SYNCHRONIZED_15M_OBSERVATION_SESSION_V1"
SESSION_AUTHORIZATION = "RUN_BOUNDED_SYNCHRONIZED_15M_OBSERVATION_SESSION_V1"
REAL_SOURCE_ATTESTATION = "REAL_MARKET_DATA_SOURCE_HUMAN_ATTESTED_NOT_SYNTHETIC"

MAX_OBSERVATION_CYCLES = 8
MAX_IMPLEMENTATION_OR_REPAIR_ATTEMPTS = 10
IMPLEMENTATION_OR_REPAIR_ATTEMPT = 1
CAPTURE_GRACE_SECONDS = 5

EXPECTED_SPOT_REQUESTS_PER_CYCLE = 1
EXPECTED_MICROSTRUCTURE_REQUESTS_PER_CYCLE = 7
EXPECTED_NETWORK_REQUESTS_PER_CYCLE = 8
MICROSTRUCTURE_DEPTH_LIMIT = 1000
DEPTH_BANDS_BPS = (5, 10, 25, 50)
REQUIRED_DEPTH_BANDS_BPS = (5, 10)
OPTIONAL_DEPTH_BANDS_BPS = (25, 50)

SPOT_CAPTURE_AUTHORIZATION = "CAPTURE_ONE_SHOT_BINANCE_PUBLIC_CLOSED_CANDLES_V1"
REVIEW_PACKAGE_AUTHORIZATION = "PREPARE_REAL_LONG_PRIMARY_HUMAN_REVIEW_PACKAGE_V1"
MICROSTRUCTURE_AUTHORIZATION = "CAPTURE_ONE_SHOT_BINANCE_USDM_PUBLIC_MICROSTRUCTURE_V1"

OFFICIAL_APPEND_GATE_NAME = "TRADING_AI_OFFICIAL_LONG_EVIDENCE_APPEND_ALLOWED"
DATASET = Path("data/forward/long_forward_observation_dataset_v1.csv")
OFFICIAL_MANIFEST = Path("data/forward/long_forward_observation_dataset_v1.manifest.csv")
OFFICIAL_LOCK = Path("data/forward/long_forward_observation_dataset_v1.lock")

EVENTS_FILENAME = "session_events.jsonl"
SUMMARY_FILENAME = "session_summary.json"
MANIFEST_FILENAME = "manifest.sha256"

SESSION_FALSE_FIELDS = (
    "official_dataset_write_allowed",
    "official_append_allowed",
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

SPOT_CAPTURE_FALSE_FIELDS = (
    "review_package_created",
    "candidate_evaluated",
    "candidate_detected",
    "manual_confirmed",
    "official_dataset_write_performed",
    "official_manifest_write_performed",
    "official_append_invoked",
    "official_append_environment_gate_modified",
    "signal_generation_enabled",
    "live_alerts_allowed",
    "paper_trade_execution_allowed",
    "real_capital_allowed",
    "market_execution_allowed",
    "exchange_execution_allowed",
    "automation_allowed",
    "execution_allowed",
)

PACKAGE_FALSE_FIELDS = (
    "official_dataset_write_performed",
    "official_manifest_write_performed",
    "official_append_environment_gate_modified",
    "paper_trade_execution_allowed",
    "real_capital_allowed",
    "market_execution_allowed",
    "exchange_execution_allowed",
    "automation_allowed",
    "execution_allowed",
)

MICROSTRUCTURE_FALSE_FIELDS = (
    "api_key_used",
    "authenticated_endpoint_used",
    "websocket_used",
    "background_execution",
    "scheduler_installed",
    "directional_recommendation_generated",
    "signal_generation_enabled",
    "live_alerts_allowed",
    "paper_trade_execution_allowed",
    "real_capital_allowed",
    "market_execution_allowed",
    "exchange_execution_allowed",
    "official_append_allowed",
    "official_dataset_write_performed",
    "official_manifest_write_performed",
    "automation_allowed",
    "execution_allowed",
)


class SynchronizedObservationError(RuntimeError):
    def __init__(self, code: str, message: str) -> None:
        self.code = code
        super().__init__(message)


def _req(ok: bool, code: str, message: str) -> None:
    if not ok:
        raise SynchronizedObservationError(code, message)


def _utc(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat()


def _parse_utc(value: Any, field: str) -> datetime:
    text = str(value).strip().replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError as exc:
        raise SynchronizedObservationError("UTC_TIMESTAMP_INVALID", field) from exc
    _req(parsed.tzinfo is not None, "UTC_TIMESTAMP_INVALID", field)
    return parsed.astimezone(timezone.utc)


def _inside(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def _sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


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


def _write_new(path: Path, payload: bytes) -> None:
    with path.open("xb") as handle:
        handle.write(payload)
        handle.flush()
        os.fsync(handle.fileno())


def _append(path: Path, value: Mapping[str, Any]) -> None:
    with path.open("ab") as handle:
        handle.write(_json_bytes(value))
        handle.flush()
        os.fsync(handle.fileno())


def _official(repo: Path) -> dict[str, str]:
    dataset = repo / DATASET
    manifest = repo / OFFICIAL_MANIFEST
    lock = repo / OFFICIAL_LOCK
    _req(dataset.is_file() and not dataset.is_symlink(), "OFFICIAL_DATASET_INVALID", str(dataset))
    _req(manifest.is_file() and not manifest.is_symlink(), "OFFICIAL_MANIFEST_INVALID", str(manifest))
    _req(not lock.exists() and not lock.is_symlink(), "OFFICIAL_APPEND_LOCK_PRESENT", str(lock))
    return {
        "dataset_sha256": _sha(dataset),
        "manifest_sha256": _sha(manifest),
    }


def _gate_off() -> None:
    _req(
        os.environ.get(OFFICIAL_APPEND_GATE_NAME) != "1",
        "OFFICIAL_APPEND_GATE_ENABLED",
        OFFICIAL_APPEND_GATE_NAME,
    )


def next_15m_capture_time(now: datetime) -> datetime:
    current = now.astimezone(timezone.utc)
    minute = (current.minute // 15) * 15
    boundary = current.replace(minute=minute, second=0, microsecond=0)
    target = boundary + timedelta(seconds=CAPTURE_GRACE_SECONDS)
    return target if current <= target else target + timedelta(minutes=15)


def _spot_capture_default():
    from src.exchange.long_primary_public_closed_candle_capture_v1 import (
        capture_real_binance_public_closed_candles,
    )
    return capture_real_binance_public_closed_candles


def _package_default():
    from src.long_side.long_primary_prospective_observation_source_adapter_v1 import (
        prepare_real_source_review_package,
    )
    return prepare_real_source_review_package


def _micro_capture_default():
    from src.exchange.public_read_only_microstructure_snapshot_v1_1 import (
        capture_public_read_only_microstructure_snapshot_v1_1,
    )
    return capture_public_read_only_microstructure_snapshot_v1_1


def _micro_validate_default():
    from src.exchange.public_read_only_microstructure_snapshot_v1_1 import (
        validate_public_read_only_microstructure_snapshot_v1_1,
    )
    return validate_public_read_only_microstructure_snapshot_v1_1


def _human_context_default():
    from src.long_side.long_supervised_15m_observation_loop_v2 import (
        compare_with_frozen_human_context,
    )
    return compare_with_frozen_human_context


def _latest_spot_candle(source: Path) -> dict[str, Any]:
    _req(source.is_file() and not source.is_symlink(), "SPOT_SOURCE_INVALID", str(source))
    with source.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    _req(len(rows) >= 49, "SPOT_SOURCE_WARMUP_INSUFFICIENT", "rows")
    row = rows[-1]
    expected = (
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
    _req(tuple(row.keys()) == expected, "SPOT_SOURCE_SCHEMA_INVALID", "columns")
    _req(
        row["symbol"] == "BTCUSDT"
        and row["timeframe"] == "15m"
        and row["candle_closed"] == "True",
        "SPOT_SOURCE_CONTRACT_INVALID",
        "latest",
    )
    return {
        key: (
            float(row[key])
            if key in {"open", "high", "low", "close", "volume"}
            else True
            if key == "candle_closed"
            else row[key]
        )
        for key in expected
    }


def _spot_capture_safe(result: Mapping[str, Any]) -> None:
    _req(
        int(result["network_request_count"]) == EXPECTED_SPOT_REQUESTS_PER_CYCLE
        and bool(result["one_shot_foreground"]),
        "SPOT_CAPTURE_MODE_INVALID",
        "capture",
    )
    for field in SPOT_CAPTURE_FALSE_FIELDS:
        _req(bool(result[field]) is False, "SPOT_CAPTURE_PERMISSION_INVALID", field)


def _package_safe(result: Mapping[str, Any], spot: Mapping[str, Any]) -> None:
    _req(
        str(result["source_artifact_sha256"]) == str(spot["source_artifact_sha256"]),
        "PACKAGE_PROVENANCE_MISMATCH",
        "source hash",
    )
    _req(
        _parse_utc(result["latest_closed_candle_utc"], "package.latest_closed_candle_utc")
        == _parse_utc(spot["latest_closed_candle_utc"], "spot.latest_closed_candle_utc"),
        "PACKAGE_CANDLE_MISMATCH",
        "close time",
    )
    _req(
        bool(result["manual_confirmation_required"]) and not bool(result["manual_confirmed"]),
        "PACKAGE_REVIEW_STATE_INVALID",
        "manual confirmation",
    )
    for field in PACKAGE_FALSE_FIELDS:
        _req(bool(result[field]) is False, "PACKAGE_PERMISSION_INVALID", field)


def _read_primary_evaluation(package_directory: Path) -> dict[str, bool]:
    checks_path = package_directory / "adapter_checks.json"
    _req(checks_path.is_file() and not checks_path.is_symlink(), "PACKAGE_CHECKS_MISSING", str(checks_path))
    checks = json.loads(checks_path.read_text(encoding="utf-8"))
    fields = (
        "failed_breakdown",
        "reclaim_confirmed",
        "bullish_confirmation",
        "candidate_detected",
    )
    out: dict[str, bool] = {}
    for field in fields:
        _req(field in checks and isinstance(checks[field], bool), "PACKAGE_CHECKS_INVALID", field)
        out[field] = checks[field]
    return out


def _micro_capture_safe(result: Mapping[str, Any], expected_output: Path) -> None:
    _req(str(Path(str(result["output_directory"])).resolve()) == str(expected_output.resolve()), "MICROSTRUCTURE_OUTPUT_MISMATCH", "output")
    _req(int(result["request_count"]) == EXPECTED_MICROSTRUCTURE_REQUESTS_PER_CYCLE, "MICROSTRUCTURE_REQUEST_COUNT_INVALID", "request_count")
    _req(int(result["depth_limit_requested"]) == MICROSTRUCTURE_DEPTH_LIMIT, "MICROSTRUCTURE_DEPTH_LIMIT_INVALID", "depth_limit")
    _req(tuple(int(x) for x in result["depth_bands_bps"]) == DEPTH_BANDS_BPS, "MICROSTRUCTURE_DEPTH_BANDS_INVALID", "bands")
    _req(bool(result["foreground_only"]) and bool(result["public_read_only"]), "MICROSTRUCTURE_MODE_INVALID", "mode")
    for field in MICROSTRUCTURE_FALSE_FIELDS:
        _req(bool(result[field]) is False, "MICROSTRUCTURE_PERMISSION_INVALID", field)


def _read_microstructure_summary(
    directory: Path,
    validate_callable: Callable[[Path | str], Mapping[str, Any]],
) -> dict[str, Any]:
    validation = dict(validate_callable(directory))
    _req(int(validation["request_count"]) == EXPECTED_MICROSTRUCTURE_REQUESTS_PER_CYCLE, "MICROSTRUCTURE_VALIDATION_INVALID", "request_count")
    _req(int(validation["depth_limit_requested"]) == MICROSTRUCTURE_DEPTH_LIMIT, "MICROSTRUCTURE_VALIDATION_INVALID", "depth_limit")
    _req(tuple(int(x) for x in validation["depth_bands_bps"]) == DEPTH_BANDS_BPS, "MICROSTRUCTURE_VALIDATION_INVALID", "bands")
    summary_path = directory / "microstructure_snapshot.json"
    _req(summary_path.is_file() and not summary_path.is_symlink(), "MICROSTRUCTURE_SUMMARY_MISSING", str(summary_path))
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    _req(summary["capability"] == "PUBLIC_READ_ONLY_MICROSTRUCTURE_SNAPSHOT_V1_1", "MICROSTRUCTURE_CAPABILITY_INVALID", "capability")
    _req(summary["provider"] == "BINANCE_USDM_PUBLIC_REST", "MICROSTRUCTURE_PROVIDER_INVALID", "provider")
    _req(summary["symbol"] == "BTCUSDT" and summary["timeframe"] == "15m", "MICROSTRUCTURE_IDENTITY_INVALID", "identity")
    _req(int(summary["request_count"]) == EXPECTED_MICROSTRUCTURE_REQUESTS_PER_CYCLE, "MICROSTRUCTURE_REQUEST_COUNT_INVALID", "summary")
    _req(int(summary["depth_limit_requested"]) == MICROSTRUCTURE_DEPTH_LIMIT, "MICROSTRUCTURE_DEPTH_LIMIT_INVALID", "summary")
    _req(tuple(int(x) for x in summary["depth_bands_bps"]) == DEPTH_BANDS_BPS, "MICROSTRUCTURE_DEPTH_BANDS_INVALID", "summary")
    for field in MICROSTRUCTURE_FALSE_FIELDS:
        _req(summary[field] is False, "MICROSTRUCTURE_PERMISSION_INVALID", field)
    return summary


def build_microstructure_context(summary: Mapping[str, Any]) -> dict[str, Any]:
    book = summary["order_book"]
    source_bands = book["bands"]
    bands: dict[str, Any] = {}
    complete: list[int] = []
    incomplete: list[int] = []
    for bps in DEPTH_BANDS_BPS:
        key = str(bps)
        _req(key in source_bands, "MICROSTRUCTURE_BAND_MISSING", key)
        raw = source_bands[key]
        covered = bool(raw["coverage_complete"])
        if covered:
            complete.append(bps)
        else:
            incomplete.append(bps)
        observed_imbalance = float(raw["notional_imbalance"])
        bands[key] = {
            "band_bps": bps,
            "coverage_complete": covered,
            "usable_for_context": covered,
            "bid_level_count": int(raw["bid_level_count"]),
            "ask_level_count": int(raw["ask_level_count"]),
            "bid_notional_usdt": float(raw["bid_notional_usdt"]),
            "ask_notional_usdt": float(raw["ask_notional_usdt"]),
            "notional_imbalance_observed": observed_imbalance,
            "notional_imbalance_usable": observed_imbalance if covered else None,
        }
    minimum_usable = all(str(bps) in bands and bands[str(bps)]["usable_for_context"] for bps in REQUIRED_DEPTH_BANDS_BPS)
    return {
        "microstructure_capability": summary["capability"],
        "provider": summary["provider"],
        "reference_closed_candle_utc": summary["reference_closed_candle_utc"],
        "depth_limit_requested": int(summary["depth_limit_requested"]),
        "depth_bands_bps": list(DEPTH_BANDS_BPS),
        "required_depth_bands_bps": list(REQUIRED_DEPTH_BANDS_BPS),
        "optional_depth_bands_bps": list(OPTIONAL_DEPTH_BANDS_BPS),
        "complete_bands_bps": complete,
        "incomplete_bands_bps": incomplete,
        "minimum_depth_context_usable": minimum_usable,
        "incomplete_depth_extrapolation_allowed": False,
        "best_bid": float(book["best_bid"]),
        "best_ask": float(book["best_ask"]),
        "mid_price": float(book["mid_price"]),
        "spread_bps": float(book["spread_bps"]),
        "furthest_bid_distance_bps": float(book["furthest_bid_distance_bps"]),
        "furthest_ask_distance_bps": float(book["furthest_ask_distance_bps"]),
        "bands": bands,
        "open_interest": summary["open_interest"],
        "mark_price_funding": summary["mark_price_funding"],
        "taker_buy_sell_volume": summary["taker_buy_sell_volume"],
        "global_long_short_account_ratio": summary["global_long_short_account_ratio"],
        "synchronization": summary["synchronization"],
        "interpretation_constraints": summary["interpretation_constraints"],
        "microstructure_can_create_candidate": False,
        "microstructure_can_cancel_candidate": False,
        "microstructure_can_modify_primary_rule": False,
        "actionable_signal_generated": False,
    }


def validate_synchronized_observation_session(directory: Path | str) -> dict[str, Any]:
    root = Path(directory).resolve()
    events_path = root / EVENTS_FILENAME
    summary_path = root / SUMMARY_FILENAME
    manifest_path = root / MANIFEST_FILENAME
    for path in (events_path, summary_path, manifest_path):
        _req(path.is_file() and not path.is_symlink(), "SESSION_FILE_MISSING", path.name)
    manifest_lines = manifest_path.read_text(encoding="utf-8").splitlines()
    _req(len(manifest_lines) == 2, "SESSION_MANIFEST_INVALID", "count")
    names: list[str] = []
    for line in manifest_lines:
        parts = line.split("  ", 1)
        _req(len(parts) == 2 and len(parts[0]) == 64, "SESSION_MANIFEST_INVALID", line)
        expected, name = parts
        path = root / name
        _req(path.is_file() and _sha(path) == expected, "SESSION_HASH_MISMATCH", name)
        names.append(name)
    _req(sorted(names) == sorted([EVENTS_FILENAME, SUMMARY_FILENAME]), "SESSION_SCOPE_INVALID", "scope")

    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    _req(summary["session_schema_version"] == SESSION_SCHEMA_VERSION, "SESSION_SCHEMA_INVALID", "schema")
    _req(summary["capability"] == CAPABILITY, "SESSION_CAPABILITY_INVALID", "capability")
    _req(int(summary["network_requests_per_completed_cycle"]) == EXPECTED_NETWORK_REQUESTS_PER_CYCLE, "SESSION_REQUEST_CONTRACT_INVALID", "per cycle")
    _req(int(summary["network_request_count"]) == int(summary["completed_cycles"]) * EXPECTED_NETWORK_REQUESTS_PER_CYCLE, "SESSION_REQUEST_COUNT_INVALID", "total")
    _req(summary["spot_futures_closed_candle_match_required"] is True, "SESSION_SYNCHRONIZATION_CONTRACT_INVALID", "required")
    _req(summary["microstructure_mutates_frozen_candidate_rule"] is False, "SESSION_PRIMARY_RULE_INVALID", "microstructure")
    for field in SESSION_FALSE_FIELDS:
        _req(summary[field] is False, "SESSION_PERMISSION_INVALID", field)

    events = [json.loads(line) for line in events_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    cycles = [event for event in events if event.get("event") == "CYCLE_COMPLETED"]
    _req(len(cycles) == int(summary["completed_cycles"]), "SESSION_EVENT_COUNT_INVALID", "cycles")
    for event in cycles:
        _req(event["synchronization"]["closed_candle_match"] is True, "SESSION_CANDLE_MISMATCH", "event")
        spot_time = _parse_utc(event["synchronization"]["spot_latest_closed_candle_utc"], "event.spot")
        futures_time = _parse_utc(event["synchronization"]["futures_reference_closed_candle_utc"], "event.futures")
        _req(spot_time == futures_time, "SESSION_CANDLE_MISMATCH", "event time")
        _req(event["microstructure_context"]["microstructure_can_create_candidate"] is False, "SESSION_PRIMARY_RULE_INVALID", "create candidate")
        _req(event["microstructure_context"]["microstructure_can_cancel_candidate"] is False, "SESSION_PRIMARY_RULE_INVALID", "cancel candidate")
        for band in event["microstructure_context"]["bands"].values():
            if band["coverage_complete"]:
                _req(band["usable_for_context"] is True and band["notional_imbalance_usable"] is not None, "SESSION_DEPTH_USAGE_INVALID", "complete band")
            else:
                _req(band["usable_for_context"] is False and band["notional_imbalance_usable"] is None, "SESSION_DEPTH_USAGE_INVALID", "incomplete band")
    return {
        "completed_cycles": int(summary["completed_cycles"]),
        "candidate_count": int(summary["candidate_count"]),
        "stop_reason": summary["stop_reason"],
        "network_request_count": int(summary["network_request_count"]),
        "event_count": len(events),
        "manifest_entries": len(manifest_lines),
    }


def run_bounded_synchronized_15m_session(
    *,
    repo_root: Path | str,
    output_directory: Path | str,
    max_cycles: int,
    source_attestation: str,
    minimum_latest_closed_candle_utc: str | None,
    authorization: str | None = None,
    clock: Callable[[], datetime] | None = None,
    sleeper: Callable[[float], None] | None = None,
    spot_capture_callable: Callable[..., Mapping[str, Any]] | None = None,
    package_callable: Callable[..., Mapping[str, Any]] | None = None,
    microstructure_capture_callable: Callable[..., Mapping[str, Any]] | None = None,
    microstructure_validate_callable: Callable[[Path | str], Mapping[str, Any]] | None = None,
    human_context_callable: Callable[[Mapping[str, Any]], Mapping[str, Any]] | None = None,
) -> dict[str, Any]:
    _req(authorization == SESSION_AUTHORIZATION, "SESSION_AUTHORIZATION_REQUIRED", "authorization")
    _req(source_attestation == REAL_SOURCE_ATTESTATION, "SESSION_SOURCE_ATTESTATION_REQUIRED", "attestation")
    _req(isinstance(max_cycles, int) and 1 <= max_cycles <= MAX_OBSERVATION_CYCLES, "SESSION_CYCLE_LIMIT_INVALID", "cycles")

    _gate_off()
    repo = Path(repo_root).resolve()
    out = Path(output_directory).resolve()
    _req((repo / ".git").is_dir(), "REPOSITORY_ROOT_INVALID", str(repo))
    _req(not _inside(out, repo), "OUTPUT_INSIDE_REPOSITORY_PROHIBITED", str(out))
    _req(out.parent.is_dir() and not out.parent.is_symlink(), "OUTPUT_PARENT_INVALID", str(out.parent))
    _req(not out.exists() and not out.is_symlink(), "OUTPUT_ALREADY_EXISTS", str(out))

    official_before = _official(repo)
    prior = (
        _parse_utc(minimum_latest_closed_candle_utc, "minimum_latest_closed_candle_utc")
        if minimum_latest_closed_candle_utc
        else None
    )
    now = clock or (lambda: datetime.now(timezone.utc))
    sleep = sleeper or time.sleep
    spot_capture_fn = spot_capture_callable or _spot_capture_default()
    package_fn = package_callable or _package_default()
    micro_capture_fn = microstructure_capture_callable or _micro_capture_default()
    micro_validate_fn = microstructure_validate_callable or _micro_validate_default()
    human_context_fn = human_context_callable or _human_context_default()

    out.mkdir()
    spot_root = out / "spot_captures"
    review_root = out / "reviews"
    micro_root = out / "microstructure"
    spot_root.mkdir()
    review_root.mkdir()
    micro_root.mkdir()
    events_path = out / EVENTS_FILENAME
    _write_new(events_path, b"")

    started = now().astimezone(timezone.utc)
    _append(
        events_path,
        {
            "event": "SESSION_STARTED",
            "at_utc": _utc(started),
            "requested_cycles": max_cycles,
            "minimum_latest_closed_candle_utc": _utc(prior) if prior else None,
            "network_requests_per_completed_cycle": EXPECTED_NETWORK_REQUESTS_PER_CYCLE,
            "spot_futures_closed_candle_match_required": True,
            "microstructure_mutates_frozen_candidate_rule": False,
            "external_notifications_allowed": False,
            "official_append_allowed": False,
        },
    )

    completed = 0
    candidates = 0
    confirmed_network_requests = 0
    latest_text: str | None = None
    stop_reason = "MAX_CYCLES_COMPLETED"

    try:
        for index in range(1, max_cycles + 1):
            _gate_off()
            scheduled = next_15m_capture_time(now())
            sleep(max(0.0, (scheduled - now().astimezone(timezone.utc)).total_seconds()))

            name = f"cycle_{index:04d}"
            spot_output = spot_root / name
            review_output = review_root / name
            micro_output = micro_root / name

            spot = dict(
                spot_capture_fn(
                    repo_root=repo,
                    output_directory=spot_output,
                    authorization=SPOT_CAPTURE_AUTHORIZATION,
                )
            )
            _spot_capture_safe(spot)
            confirmed_network_requests += EXPECTED_SPOT_REQUESTS_PER_CYCLE

            latest_dt = _parse_utc(spot["latest_closed_candle_utc"], "spot.latest_closed_candle_utc")
            _req(prior is None or latest_dt > prior, "DUPLICATE_OR_OLD_CANDLE", "spot candle")
            prior = latest_dt
            latest_text = _utc(latest_dt)

            source = Path(str(spot["source_csv"])).resolve()
            latest_spot = _latest_spot_candle(source)
            metadata = json.loads(Path(str(spot["metadata_json"])).read_text(encoding="utf-8"))

            package = dict(
                package_fn(
                    repo_root=repo,
                    source_csv=source,
                    output_directory=review_output,
                    captured_at_utc=str(metadata["captured_at_utc"]),
                    prospective_start_utc=str(spot["latest_closed_candle_utc"]),
                    source_system="BINANCE_PUBLIC_SPOT_API",
                    source_capture_id=str(spot["capture_id"]),
                    source_attestation=source_attestation,
                    expected_source_sha256=str(spot["source_artifact_sha256"]),
                    authorization=REVIEW_PACKAGE_AUTHORIZATION,
                )
            )
            _package_safe(package, spot)
            primary_evaluation = _read_primary_evaluation(review_output)
            _req(
                bool(package["candidate_detected"]) == primary_evaluation["candidate_detected"],
                "PACKAGE_CHECKS_MISMATCH",
                "candidate_detected",
            )

            micro = dict(
                micro_capture_fn(
                    repo_root=repo,
                    output_directory=micro_output,
                    authorization=MICROSTRUCTURE_AUTHORIZATION,
                )
            )
            _micro_capture_safe(micro, micro_output)
            confirmed_network_requests += EXPECTED_MICROSTRUCTURE_REQUESTS_PER_CYCLE

            micro_summary = _read_microstructure_summary(micro_output, micro_validate_fn)
            futures_dt = _parse_utc(
                micro_summary["reference_closed_candle_utc"],
                "microstructure.reference_closed_candle_utc",
            )
            _req(latest_dt == futures_dt, "SPOT_FUTURES_CANDLE_MISMATCH", f"{latest_dt.isoformat()} != {futures_dt.isoformat()}")

            micro_context = build_microstructure_context(micro_summary)
            human_context = dict(human_context_fn(latest_spot))
            candidate = bool(package["candidate_detected"])

            completed += 1
            candidates += int(candidate)

            _append(
                events_path,
                {
                    "event": "CYCLE_COMPLETED",
                    "cycle_index": index,
                    "scheduled_at_utc": _utc(scheduled),
                    "spot_capture_id": spot["capture_id"],
                    "spot_source_artifact_sha256": spot["source_artifact_sha256"],
                    "review_package_id": package["package_id"],
                    "microstructure_output_directory": str(micro_output),
                    "microstructure_manifest_sha256": _sha(micro_output / "manifest.sha256"),
                    "latest_spot_candle": latest_spot,
                    "primary_evaluation": primary_evaluation,
                    "human_context_comparison": human_context,
                    "microstructure_context": micro_context,
                    "synchronization": {
                        "spot_latest_closed_candle_utc": _utc(latest_dt),
                        "futures_reference_closed_candle_utc": _utc(futures_dt),
                        "closed_candle_match": True,
                    },
                    "candidate_detected": candidate,
                    "eligible_for_real_human_review": bool(package["eligible_for_real_human_review"]),
                    "manual_confirmed": False,
                    "official_append_invoked": False,
                    "external_notification_sent": False,
                    "actionable_signal_generated": False,
                },
            )

            _req(_official(repo) == official_before, "OFFICIAL_ARTIFACT_CHANGED", "official")
            _gate_off()

            if candidate:
                stop_reason = "FIRST_PRIMARY_CANDIDATE_PENDING_HUMAN_REVIEW"
                break

    except Exception as exc:
        _append(
            events_path,
            {
                "event": "SESSION_ABORTED_FAIL_CLOSED",
                "at_utc": _utc(now().astimezone(timezone.utc)),
                "completed_cycles": completed,
                "confirmed_network_request_count": confirmed_network_requests,
                "error_type": type(exc).__name__,
                "error_message": str(exc),
                "official_append_invoked": False,
                "external_notification_sent": False,
            },
        )
        raise

    official_after = _official(repo)
    _req(official_after == official_before, "OFFICIAL_ARTIFACT_CHANGED", "official")
    _gate_off()
    finished = now().astimezone(timezone.utc)

    summary = {
        "session_schema_version": SESSION_SCHEMA_VERSION,
        "capability": CAPABILITY,
        "implementation_schema_version": IMPLEMENTATION_SCHEMA_VERSION,
        "implementation_or_repair_attempt": IMPLEMENTATION_OR_REPAIR_ATTEMPT,
        "max_implementation_or_repair_attempts": MAX_IMPLEMENTATION_OR_REPAIR_ATTEMPTS,
        "session_mode": "BOUNDED_FOREGROUND_SYNCHRONIZED_SUPERVISED",
        "started_at_utc": _utc(started),
        "finished_at_utc": _utc(finished),
        "requested_cycles": max_cycles,
        "completed_cycles": completed,
        "candidate_count": candidates,
        "no_candidate_count": completed - candidates,
        "stop_on_first_primary_candidate": True,
        "stop_reason": stop_reason,
        "latest_closed_candle_utc": latest_text,
        "spot_requests_per_completed_cycle": EXPECTED_SPOT_REQUESTS_PER_CYCLE,
        "microstructure_requests_per_completed_cycle": EXPECTED_MICROSTRUCTURE_REQUESTS_PER_CYCLE,
        "network_requests_per_completed_cycle": EXPECTED_NETWORK_REQUESTS_PER_CYCLE,
        "network_request_count": completed * EXPECTED_NETWORK_REQUESTS_PER_CYCLE,
        "spot_source": "BINANCE_PUBLIC_SPOT_API",
        "microstructure_source": "BINANCE_USDM_PUBLIC_REST",
        "microstructure_version": "PUBLIC_READ_ONLY_MICROSTRUCTURE_SNAPSHOT_V1_1",
        "microstructure_depth_limit": MICROSTRUCTURE_DEPTH_LIMIT,
        "depth_bands_bps": list(DEPTH_BANDS_BPS),
        "required_depth_bands_bps": list(REQUIRED_DEPTH_BANDS_BPS),
        "optional_depth_bands_bps": list(OPTIONAL_DEPTH_BANDS_BPS),
        "incomplete_depth_extrapolation_allowed": False,
        "spot_futures_closed_candle_match_required": True,
        "microstructure_mutates_frozen_candidate_rule": False,
        "microstructure_can_create_candidate": False,
        "microstructure_can_cancel_candidate": False,
        "human_context_mutates_frozen_candidate_rule": False,
        "automatic_or_background_execution": False,
        "recurring_scheduler_installed": False,
        "external_notifications_sent": False,
        "messages_sent": False,
        "browser_control_used": False,
        "tradingview_account_accessed": False,
        "manual_confirmation_required": True,
        "manual_confirmed": False,
        "official_dataset_sha256_before": official_before["dataset_sha256"],
        "official_dataset_sha256_after": official_after["dataset_sha256"],
        "official_manifest_sha256_before": official_before["manifest_sha256"],
        "official_manifest_sha256_after": official_after["manifest_sha256"],
        **{field: False for field in SESSION_FALSE_FIELDS},
    }

    _write_new(out / SUMMARY_FILENAME, _json_bytes(summary))
    manifest_lines = [
        f"{_sha(events_path)}  {EVENTS_FILENAME}",
        f"{_sha(out / SUMMARY_FILENAME)}  {SUMMARY_FILENAME}",
    ]
    _write_new(out / MANIFEST_FILENAME, ("\n".join(manifest_lines) + "\n").encode("utf-8"))

    validation = validate_synchronized_observation_session(out)
    return {
        "capability": CAPABILITY,
        "output_directory": str(out),
        "requested_cycles": max_cycles,
        "completed_cycles": completed,
        "candidate_count": candidates,
        "no_candidate_count": completed - candidates,
        "stop_reason": stop_reason,
        "network_request_count": completed * EXPECTED_NETWORK_REQUESTS_PER_CYCLE,
        "network_requests_per_completed_cycle": EXPECTED_NETWORK_REQUESTS_PER_CYCLE,
        "latest_closed_candle_utc": latest_text,
        "foreground_only": True,
        "bounded": True,
        "synchronized": True,
        "external_notifications_sent": False,
        "manual_confirmation_required": True,
        "manual_confirmed": False,
        **{field: False for field in SESSION_FALSE_FIELDS},
        "session_manifest_entries": validation["manifest_entries"],
        "session_event_count": validation["event_count"],
    }


__all__ = [
    "CAPABILITY",
    "CAPTURE_GRACE_SECONDS",
    "DEPTH_BANDS_BPS",
    "EXPECTED_MICROSTRUCTURE_REQUESTS_PER_CYCLE",
    "EXPECTED_NETWORK_REQUESTS_PER_CYCLE",
    "EXPECTED_SPOT_REQUESTS_PER_CYCLE",
    "IMPLEMENTATION_OR_REPAIR_ATTEMPT",
    "MAX_IMPLEMENTATION_OR_REPAIR_ATTEMPTS",
    "MAX_OBSERVATION_CYCLES",
    "MICROSTRUCTURE_AUTHORIZATION",
    "MICROSTRUCTURE_DEPTH_LIMIT",
    "OPTIONAL_DEPTH_BANDS_BPS",
    "REAL_SOURCE_ATTESTATION",
    "REQUIRED_DEPTH_BANDS_BPS",
    "SESSION_AUTHORIZATION",
    "SynchronizedObservationError",
    "build_microstructure_context",
    "next_15m_capture_time",
    "run_bounded_synchronized_15m_session",
    "validate_synchronized_observation_session",
]
