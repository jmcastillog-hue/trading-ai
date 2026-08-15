from __future__ import annotations

import csv
import hashlib
import json
import math
import os
import shutil
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence

CAPABILITY = "FORWARD_OUTCOME_LABELER_V1"
IMPLEMENTATION_SCHEMA_VERSION = "FORWARD_OUTCOME_LABELER_IMPLEMENTATION_V1"
OBSERVATION_DESCRIPTOR_SCHEMA_VERSION = "FORWARD_OUTCOME_OBSERVATION_DESCRIPTOR_V1"
OUTCOME_SCHEMA_VERSION = "FORWARD_OUTCOME_LABELS_V1"
PACKAGE_SCHEMA_VERSION = "FORWARD_OUTCOME_LABEL_PACKAGE_V1"

EXPECTED_SYMBOL = "BTCUSDT"
EXPECTED_TIMEFRAME = "15m"
BAR_DURATION = timedelta(minutes=15)
CLOSE_EPSILON = timedelta(milliseconds=1)
FORWARD_HORIZONS_BARS = (1, 2, 4, 8, 16)
MAX_IMPLEMENTATION_OR_REPAIR_ATTEMPTS = 10
IMPLEMENTATION_OR_REPAIR_ATTEMPT = 1

PACKAGE_AUTHORIZATION = "PREPARE_FORWARD_OUTCOME_LABEL_PACKAGE_V1"

OFFICIAL_APPEND_GATE_NAME = "TRADING_AI_OFFICIAL_LONG_EVIDENCE_APPEND_ALLOWED"
OFFICIAL_DATASET = Path("data/forward/long_forward_observation_dataset_v1.csv")
OFFICIAL_MANIFEST = Path("data/forward/long_forward_observation_dataset_v1.manifest.csv")
OFFICIAL_LOCK = Path("data/forward/long_forward_observation_dataset_v1.lock")

FUTURE_SOURCE_COLUMNS = (
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

ALLOWED_SYNCHRONIZED_CAPABILITIES = (
    "SYNCHRONIZED_15M_OBSERVATION_V1",
    "SYNCHRONIZED_15M_OBSERVATION_V1_1",
)

OUTPUT_FALSE_FIELDS = (
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

PRIMARY_ANCHOR_POLICY = "REFERENCE_BOUNDARY"
CONTEXT_ANCHOR_POLICY = "FIRST_FULL_15M_BAR_OPEN_AT_OR_AFTER_CONTEXT_AVAILABILITY"
TARGET_STOP_SAME_BAR_POLICY = "AMBIGUOUS_SAME_BAR_NO_INTRABAR_ORDER_INFERENCE"


class ForwardOutcomeLabelerError(RuntimeError):
    def __init__(self, code: str, message: str) -> None:
        self.code = code
        super().__init__(message)


def _req(ok: bool, code: str, message: str) -> None:
    if not ok:
        raise ForwardOutcomeLabelerError(code, message)


def _parse_utc(value: Any, field: str) -> datetime:
    text = str(value).strip().replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError as exc:
        raise ForwardOutcomeLabelerError("TIMESTAMP_INVALID", field) from exc
    _req(parsed.tzinfo is not None, "TIMESTAMP_TIMEZONE_REQUIRED", field)
    return parsed.astimezone(timezone.utc)


def _utc(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat()


def _number(value: Any, field: str) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise ForwardOutcomeLabelerError("NUMERIC_FIELD_INVALID", field) from exc
    _req(math.isfinite(number), "NUMERIC_FIELD_INVALID", field)
    return number


def _sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


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
    _req(dataset.is_file() and not dataset.is_symlink(), "OFFICIAL_DATASET_INVALID", str(dataset))
    _req(manifest.is_file() and not manifest.is_symlink(), "OFFICIAL_MANIFEST_INVALID", str(manifest))
    _req(not lock.exists() and not lock.is_symlink(), "OFFICIAL_LOCK_PRESENT", str(lock))
    return {"dataset_sha256": _sha(dataset), "manifest_sha256": _sha(manifest)}


def _write_new(path: Path, payload: bytes) -> None:
    with path.open("xb") as handle:
        handle.write(payload)
        handle.flush()
        os.fsync(handle.fileno())


def _write_manifest(directory: Path, names: Sequence[str]) -> None:
    lines = [f"{_sha(directory / name)}  {name}" for name in sorted(names)]
    _write_new(directory / "manifest.sha256", ("\n".join(lines) + "\n").encode("utf-8"))


def _read_manifest(directory: Path, expected_names: Sequence[str]) -> dict[str, str]:
    manifest = directory / "manifest.sha256"
    _req(manifest.is_file() and not manifest.is_symlink(), "MANIFEST_MISSING", str(manifest))
    lines = manifest.read_text(encoding="utf-8").splitlines()
    _req(len(lines) == len(expected_names), "MANIFEST_ENTRY_COUNT_INVALID", str(manifest))
    seen: dict[str, str] = {}
    for line in lines:
        parts = line.split("  ", 1)
        _req(len(parts) == 2 and len(parts[0]) == 64, "MANIFEST_LINE_INVALID", line)
        expected, name = parts
        path = directory / name
        _req(path.is_file() and not path.is_symlink(), "MANIFEST_FILE_MISSING", name)
        _req(_sha(path) == expected, "MANIFEST_HASH_MISMATCH", name)
        seen[name] = expected
    _req(sorted(seen) == sorted(expected_names), "MANIFEST_SCOPE_INVALID", str(sorted(seen)))
    return seen


def _normalize_candle(row: Mapping[str, Any]) -> dict[str, Any]:
    _req(tuple(row.keys()) == FUTURE_SOURCE_COLUMNS, "FUTURE_SOURCE_SCHEMA_INVALID", "columns")
    open_time = _parse_utc(row["open_time_utc"], "open_time_utc")
    close_time = _parse_utc(row["close_time_utc"], "close_time_utc")
    _req(close_time == open_time + BAR_DURATION - CLOSE_EPSILON, "FUTURE_CANDLE_INTERVAL_INVALID", _utc(open_time))
    _req(str(row["symbol"]) == EXPECTED_SYMBOL, "FUTURE_SYMBOL_INVALID", str(row["symbol"]))
    _req(str(row["timeframe"]) == EXPECTED_TIMEFRAME, "FUTURE_TIMEFRAME_INVALID", str(row["timeframe"]))
    _req(str(row["candle_closed"]).strip().casefold() == "true", "FUTURE_CANDLE_NOT_CLOSED", _utc(open_time))
    o = _number(row["open"], "open")
    h = _number(row["high"], "high")
    l = _number(row["low"], "low")
    c = _number(row["close"], "close")
    v = _number(row["volume"], "volume")
    _req(o > 0 and h > 0 and l > 0 and c > 0 and v >= 0, "FUTURE_CANDLE_VALUE_INVALID", _utc(open_time))
    _req(l <= min(o, c) <= max(o, c) <= h, "FUTURE_OHLC_INVALID", _utc(open_time))
    return {
        "open_time_utc": _utc(open_time),
        "close_time_utc": _utc(close_time),
        "symbol": EXPECTED_SYMBOL,
        "timeframe": EXPECTED_TIMEFRAME,
        "open": o,
        "high": h,
        "low": l,
        "close": c,
        "volume": v,
        "candle_closed": True,
    }


def read_future_closed_candles(path: Path | str) -> list[dict[str, Any]]:
    source = Path(path).resolve()
    _req(source.is_file() and not source.is_symlink(), "FUTURE_SOURCE_INVALID", str(source))
    with source.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        _req(tuple(reader.fieldnames or ()) == FUTURE_SOURCE_COLUMNS, "FUTURE_SOURCE_SCHEMA_INVALID", "columns")
        rows = [_normalize_candle(row) for row in reader]
    opens = [_parse_utc(row["open_time_utc"], "open_time_utc") for row in rows]
    _req(opens == sorted(opens), "FUTURE_SOURCE_NOT_ORDERED", "open_time")
    _req(len(opens) == len(set(opens)), "FUTURE_SOURCE_DUPLICATE_CANDLE", "open_time")
    for previous, current in zip(opens, opens[1:]):
        _req(current - previous == BAR_DURATION, "FUTURE_SOURCE_GAP", f"{_utc(previous)} -> {_utc(current)}")
    return rows


def _ceil_15m(value: datetime) -> datetime:
    current = value.astimezone(timezone.utc)
    minute_floor = (current.minute // 15) * 15
    floor = current.replace(minute=minute_floor, second=0, microsecond=0)
    return floor if current == floor else floor + BAR_DURATION


def _session_integrity(session: Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    _req(session.is_dir() and not session.is_symlink(), "SESSION_DIRECTORY_INVALID", str(session))
    _read_manifest(session, ("session_events.jsonl", "session_summary.json"))
    summary = json.loads((session / "session_summary.json").read_text(encoding="utf-8"))
    _req(summary["capability"] in ALLOWED_SYNCHRONIZED_CAPABILITIES, "SESSION_CAPABILITY_INVALID", str(summary.get("capability")))
    events = [
        json.loads(line)
        for line in (session / "session_events.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    return summary, events


def _microstructure_integrity(directory: Path) -> dict[str, Any]:
    _req(directory.is_dir() and not directory.is_symlink(), "MICROSTRUCTURE_DIRECTORY_INVALID", str(directory))
    _read_manifest(directory, ("microstructure_snapshot.json", "raw_responses.json", "request_log.json"))
    summary = json.loads((directory / "microstructure_snapshot.json").read_text(encoding="utf-8"))
    _req(summary["capability"] == "PUBLIC_READ_ONLY_MICROSTRUCTURE_SNAPSHOT_V1_1", "MICROSTRUCTURE_CAPABILITY_INVALID", str(summary.get("capability")))
    return summary


def build_observation_descriptor_from_synchronized_session(
    *,
    synchronized_session_directory: Path | str,
    cycle_index: int,
) -> dict[str, Any]:
    session = Path(synchronized_session_directory).resolve()
    summary, events = _session_integrity(session)
    cycles = [event for event in events if event.get("event") == "CYCLE_COMPLETED"]
    matches = [event for event in cycles if int(event.get("cycle_index", -1)) == int(cycle_index)]
    _req(len(matches) == 1, "SESSION_CYCLE_NOT_FOUND", str(cycle_index))
    cycle = matches[0]
    _req(cycle["synchronization"]["closed_candle_match"] is True, "SESSION_CANDLE_MISMATCH", str(cycle_index))
    spot = cycle["latest_spot_candle"]
    reference_close = _parse_utc(spot["close_time_utc"], "latest_spot_candle.close_time_utc")
    reference_boundary = reference_close + CLOSE_EPSILON
    reference_price = _number(spot["close"], "latest_spot_candle.close")
    micro_dir = Path(str(cycle["microstructure_output_directory"])).resolve()
    micro = _microstructure_integrity(micro_dir)
    micro_reference = _parse_utc(micro["reference_closed_candle_utc"], "microstructure.reference_closed_candle_utc")
    _req(micro_reference == reference_close, "MICROSTRUCTURE_REFERENCE_MISMATCH", str(cycle_index))
    context_available = _parse_utc(micro["captured_finished_at_utc"], "microstructure.captured_finished_at_utc")
    _req(context_available >= reference_boundary, "CONTEXT_AVAILABILITY_BEFORE_REFERENCE", _utc(context_available))

    candidate = bool(cycle["candidate_detected"])
    entry_price = reference_price
    stop_price: float | None = None
    target_price: float | None = None

    review_dir = session / "reviews" / f"cycle_{int(cycle_index):04d}"
    candidate_csv = review_dir / "candidate_rows.csv"
    _req(candidate_csv.is_file() and not candidate_csv.is_symlink(), "CANDIDATE_ROWS_MISSING", str(candidate_csv))
    with candidate_csv.open("r", encoding="utf-8", newline="") as handle:
        candidate_rows = list(csv.DictReader(handle))
    if candidate:
        _req(len(candidate_rows) == 1, "CANDIDATE_ROW_COUNT_INVALID", str(len(candidate_rows)))
        row = candidate_rows[0]
        _req(str(row.get("candidate_detected", "")).casefold() == "true", "CANDIDATE_ROW_STATE_INVALID", "candidate_detected")
        entry_price = _number(row["entry_price"], "candidate.entry_price")
        stop_price = _number(row["stop_price"], "candidate.stop_price")
        target_price = _number(row["target_price"], "candidate.target_price")
        _req(stop_price < entry_price < target_price, "CANDIDATE_GEOMETRY_INVALID", "LONG")
        _req(abs(entry_price - reference_price) <= max(1e-9, abs(reference_price) * 1e-12), "CANDIDATE_ENTRY_REFERENCE_MISMATCH", "entry")
    else:
        _req(len(candidate_rows) == 0, "NON_CANDIDATE_ROWS_NOT_EMPTY", str(len(candidate_rows)))

    return {
        "observation_descriptor_schema_version": OBSERVATION_DESCRIPTOR_SCHEMA_VERSION,
        "observation_id": str(cycle.get("review_package_id") or f"SYNC_CYCLE_{cycle_index:04d}"),
        "source_session_capability": summary["capability"],
        "source_session_directory": str(session),
        "source_session_summary_sha256": _sha(session / "session_summary.json"),
        "source_session_events_sha256": _sha(session / "session_events.jsonl"),
        "cycle_index": int(cycle_index),
        "symbol": EXPECTED_SYMBOL,
        "timeframe": EXPECTED_TIMEFRAME,
        "reference_closed_candle_utc": _utc(reference_close),
        "reference_boundary_utc": _utc(reference_boundary),
        "reference_price": reference_price,
        "primary_candidate_detected": candidate,
        "primary_entry_price": entry_price,
        "primary_stop_price": stop_price,
        "primary_target_price": target_price,
        "synchronized_context_available_at_utc": _utc(context_available),
        "synchronized_context_anchor_policy": CONTEXT_ANCHOR_POLICY,
        "primary_anchor_policy": PRIMARY_ANCHOR_POLICY,
        "point_in_time_context_is_not_historical_reconstruction": True,
    }


def _validate_descriptor(descriptor: Mapping[str, Any]) -> dict[str, Any]:
    _req(descriptor["observation_descriptor_schema_version"] == OBSERVATION_DESCRIPTOR_SCHEMA_VERSION, "OBSERVATION_DESCRIPTOR_SCHEMA_INVALID", "schema")
    _req(descriptor["symbol"] == EXPECTED_SYMBOL and descriptor["timeframe"] == EXPECTED_TIMEFRAME, "OBSERVATION_IDENTITY_INVALID", "symbol/timeframe")
    reference_close = _parse_utc(descriptor["reference_closed_candle_utc"], "reference_closed_candle_utc")
    reference_boundary = _parse_utc(descriptor["reference_boundary_utc"], "reference_boundary_utc")
    _req(reference_boundary - reference_close == CLOSE_EPSILON, "REFERENCE_BOUNDARY_INVALID", "close + 1ms")
    reference_price = _number(descriptor["reference_price"], "reference_price")
    entry = _number(descriptor["primary_entry_price"], "primary_entry_price")
    _req(reference_price > 0 and entry > 0, "REFERENCE_PRICE_INVALID", "positive")
    candidate = bool(descriptor["primary_candidate_detected"])
    stop = descriptor.get("primary_stop_price")
    target = descriptor.get("primary_target_price")
    if candidate:
        _req(stop is not None and target is not None, "CANDIDATE_GEOMETRY_MISSING", "stop/target")
        stop_n = _number(stop, "primary_stop_price")
        target_n = _number(target, "primary_target_price")
        _req(stop_n < entry < target_n, "CANDIDATE_GEOMETRY_INVALID", "LONG")
    else:
        _req(stop is None and target is None, "NON_CANDIDATE_GEOMETRY_PRESENT", "stop/target")
    context_available = _parse_utc(descriptor["synchronized_context_available_at_utc"], "synchronized_context_available_at_utc")
    _req(context_available >= reference_boundary, "CONTEXT_AVAILABILITY_BEFORE_REFERENCE", _utc(context_available))
    return dict(descriptor)


def _index_rows(rows: Sequence[Mapping[str, Any]]) -> dict[datetime, Mapping[str, Any]]:
    return {_parse_utc(row["open_time_utc"], "open_time_utc"): row for row in rows}


def _available_contiguous_from(
    rows_by_open: Mapping[datetime, Mapping[str, Any]],
    anchor_open: datetime,
) -> list[Mapping[str, Any]]:
    if not rows_by_open:
        return []
    earliest = min(rows_by_open)
    latest = max(rows_by_open)
    if anchor_open < earliest:
        raise ForwardOutcomeLabelerError("FUTURE_SOURCE_STARTS_AFTER_REQUIRED_ANCHOR", _utc(anchor_open))
    if anchor_open > latest:
        return []
    out: list[Mapping[str, Any]] = []
    current = anchor_open
    while current in rows_by_open:
        out.append(rows_by_open[current])
        current += BAR_DURATION
    if current <= latest:
        raise ForwardOutcomeLabelerError("FUTURE_SOURCE_GAP_AFTER_ANCHOR", _utc(current))
    return out


def _touch_order(
    bars: Sequence[Mapping[str, Any]],
    stop_price: float | None,
    target_price: float | None,
    candidate: bool,
) -> str:
    if not candidate:
        return "NOT_APPLICABLE"
    _req(stop_price is not None and target_price is not None, "CANDIDATE_GEOMETRY_MISSING", "touch")
    for bar in bars:
        stop_hit = float(bar["low"]) <= float(stop_price)
        target_hit = float(bar["high"]) >= float(target_price)
        if stop_hit and target_hit:
            return "AMBIGUOUS_SAME_BAR"
        if target_hit:
            return "TARGET_FIRST"
        if stop_hit:
            return "STOP_FIRST"
    return "NEITHER_WITHIN_HORIZON"


def _horizon_labels(
    *,
    bars: Sequence[Mapping[str, Any]],
    anchor_price: float | None,
    candidate: bool,
    stop_price: float | None,
    target_price: float | None,
    include_target_stop: bool,
) -> dict[str, Any]:
    labels: dict[str, Any] = {}
    for horizon in FORWARD_HORIZONS_BARS:
        key = str(horizon)
        if anchor_price is None or len(bars) < horizon:
            labels[key] = {
                "horizon_bars": horizon,
                "label_status": "PENDING",
                "bars_available_from_anchor": len(bars),
                "forward_return": None,
                "mfe_return": None,
                "mae_return": None,
                "horizon_close_price": None,
                "max_high_price": None,
                "min_low_price": None,
                "target_stop_ordering": None,
            }
            continue
        selected = list(bars[:horizon])
        close_price = float(selected[-1]["close"])
        max_high = max(float(bar["high"]) for bar in selected)
        min_low = min(float(bar["low"]) for bar in selected)
        labels[key] = {
            "horizon_bars": horizon,
            "label_status": "AVAILABLE",
            "bars_available_from_anchor": len(bars),
            "forward_return": (close_price / anchor_price) - 1.0,
            "mfe_return": (max_high / anchor_price) - 1.0,
            "mae_return": (min_low / anchor_price) - 1.0,
            "horizon_close_price": close_price,
            "max_high_price": max_high,
            "min_low_price": min_low,
            "target_stop_ordering": (
                _touch_order(selected, stop_price, target_price, candidate)
                if include_target_stop
                else "NOT_APPLICABLE"
            ),
        }
    return labels


def label_forward_outcomes(
    *,
    observation_descriptor: Mapping[str, Any],
    future_closed_candles: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    descriptor = _validate_descriptor(observation_descriptor)
    rows = [_normalize_candle(row) for row in future_closed_candles]
    opens = [_parse_utc(row["open_time_utc"], "open_time_utc") for row in rows]
    _req(opens == sorted(opens), "FUTURE_SOURCE_NOT_ORDERED", "open_time")
    _req(len(opens) == len(set(opens)), "FUTURE_SOURCE_DUPLICATE_CANDLE", "open_time")
    for previous, current in zip(opens, opens[1:]):
        _req(current - previous == BAR_DURATION, "FUTURE_SOURCE_GAP", f"{_utc(previous)} -> {_utc(current)}")

    rows_by_open = _index_rows(rows)
    reference_boundary = _parse_utc(descriptor["reference_boundary_utc"], "reference_boundary_utc")
    context_available = _parse_utc(descriptor["synchronized_context_available_at_utc"], "synchronized_context_available_at_utc")
    context_anchor_open = _ceil_15m(context_available)

    primary_bars = _available_contiguous_from(rows_by_open, reference_boundary)
    context_bars = _available_contiguous_from(rows_by_open, context_anchor_open)
    context_anchor_price: float | None = float(context_bars[0]["open"]) if context_bars else None

    primary_labels = _horizon_labels(
        bars=primary_bars,
        anchor_price=float(descriptor["primary_entry_price"]),
        candidate=bool(descriptor["primary_candidate_detected"]),
        stop_price=descriptor.get("primary_stop_price"),
        target_price=descriptor.get("primary_target_price"),
        include_target_stop=True,
    )
    context_labels = _horizon_labels(
        bars=context_bars,
        anchor_price=context_anchor_price,
        candidate=False,
        stop_price=None,
        target_price=None,
        include_target_stop=False,
    )

    return {
        "outcome_schema_version": OUTCOME_SCHEMA_VERSION,
        "capability": CAPABILITY,
        "observation_id": descriptor["observation_id"],
        "symbol": EXPECTED_SYMBOL,
        "timeframe": EXPECTED_TIMEFRAME,
        "forward_horizons_bars": list(FORWARD_HORIZONS_BARS),
        "primary_rule_outcome": {
            "anchor_policy": PRIMARY_ANCHOR_POLICY,
            "anchor_open_time_utc": _utc(reference_boundary),
            "anchor_price": float(descriptor["primary_entry_price"]),
            "primary_candidate_detected": bool(descriptor["primary_candidate_detected"]),
            "primary_stop_price": descriptor.get("primary_stop_price"),
            "primary_target_price": descriptor.get("primary_target_price"),
            "same_bar_target_stop_policy": TARGET_STOP_SAME_BAR_POLICY,
            "partially_elapsed_bar_allowed": False,
            "labels": primary_labels,
        },
        "synchronized_context_outcome": {
            "anchor_policy": CONTEXT_ANCHOR_POLICY,
            "context_available_at_utc": _utc(context_available),
            "anchor_open_time_utc": _utc(context_anchor_open),
            "anchor_price": context_anchor_price,
            "partially_elapsed_bar_allowed": False,
            "point_in_time_context_is_not_historical_reconstruction": True,
            "labels": context_labels,
        },
        "lookahead_used": False,
        "intrabar_order_inferred": False,
        "future_candles_required_closed": True,
        "future_candles_required_contiguous": True,
        "label_maturity_is_explicit": True,
        **{field: False for field in OUTPUT_FALSE_FIELDS},
    }


def validate_forward_outcome_label_package(directory: Path | str) -> dict[str, Any]:
    root = Path(directory).resolve()
    _read_manifest(root, ("labeler_checks.json", "observation_descriptor.json", "forward_outcomes.json"))
    descriptor = json.loads((root / "observation_descriptor.json").read_text(encoding="utf-8"))
    outcomes = json.loads((root / "forward_outcomes.json").read_text(encoding="utf-8"))
    checks = json.loads((root / "labeler_checks.json").read_text(encoding="utf-8"))
    _validate_descriptor(descriptor)
    _req(outcomes["outcome_schema_version"] == OUTCOME_SCHEMA_VERSION, "OUTCOME_SCHEMA_INVALID", "schema")
    _req(outcomes["capability"] == CAPABILITY, "OUTCOME_CAPABILITY_INVALID", "capability")
    _req(outcomes["lookahead_used"] is False and outcomes["intrabar_order_inferred"] is False, "OUTCOME_LOOKAHEAD_INVALID", "lookahead")
    _req(outcomes["primary_rule_outcome"]["partially_elapsed_bar_allowed"] is False, "PRIMARY_PARTIAL_BAR_INVALID", "partial")
    _req(outcomes["synchronized_context_outcome"]["partially_elapsed_bar_allowed"] is False, "CONTEXT_PARTIAL_BAR_INVALID", "partial")
    _req(tuple(outcomes["forward_horizons_bars"]) == FORWARD_HORIZONS_BARS, "OUTCOME_HORIZONS_INVALID", "horizons")
    for field in OUTPUT_FALSE_FIELDS:
        _req(outcomes[field] is False, "OUTCOME_PERMISSION_INVALID", field)
    _req(checks["package_schema_version"] == PACKAGE_SCHEMA_VERSION, "PACKAGE_SCHEMA_INVALID", "checks")
    _req(checks["real_network_request_executed"] is False, "PACKAGE_NETWORK_INVALID", "network")
    _req(checks["official_append_executed"] is False, "PACKAGE_OFFICIAL_APPEND_INVALID", "append")
    available_primary = sum(1 for item in outcomes["primary_rule_outcome"]["labels"].values() if item["label_status"] == "AVAILABLE")
    available_context = sum(1 for item in outcomes["synchronized_context_outcome"]["labels"].values() if item["label_status"] == "AVAILABLE")
    return {
        "available_primary_horizons": available_primary,
        "available_context_horizons": available_context,
        "manifest_entries": 3,
        "primary_candidate_detected": bool(descriptor["primary_candidate_detected"]),
    }


def prepare_forward_outcome_label_package(
    *,
    repo_root: Path | str,
    synchronized_session_directory: Path | str,
    cycle_index: int,
    future_closed_candles_csv: Path | str,
    output_directory: Path | str,
    authorization: str | None = None,
) -> dict[str, Any]:
    _req(authorization == PACKAGE_AUTHORIZATION, "PACKAGE_AUTHORIZATION_REQUIRED", "authorization")
    _gate_off()
    repo = Path(repo_root).resolve()
    session = Path(synchronized_session_directory).resolve()
    future_source = Path(future_closed_candles_csv).resolve()
    output = Path(output_directory).resolve()
    _req((repo / ".git").is_dir(), "REPOSITORY_ROOT_INVALID", str(repo))
    _req(not _inside(output, repo), "OUTPUT_INSIDE_REPOSITORY_PROHIBITED", str(output))
    _req(output.parent.is_dir() and not output.parent.is_symlink(), "OUTPUT_PARENT_INVALID", str(output.parent))
    _req(not output.exists() and not output.is_symlink(), "OUTPUT_ALREADY_EXISTS", str(output))
    _req(not _inside(future_source, repo), "FUTURE_SOURCE_INSIDE_REPOSITORY_PROHIBITED", str(future_source))
    official_before = _official(repo)
    descriptor = build_observation_descriptor_from_synchronized_session(
        synchronized_session_directory=session,
        cycle_index=cycle_index,
    )
    candles = read_future_closed_candles(future_source)
    outcomes = label_forward_outcomes(
        observation_descriptor=descriptor,
        future_closed_candles=candles,
    )
    _req(_official(repo) == official_before, "OFFICIAL_ARTIFACT_CHANGED", "compute")
    _gate_off()

    temp = output.parent / f".{output.name}.tmp-{uuid.uuid4().hex}"
    _req(not temp.exists(), "TEMPORARY_OUTPUT_COLLISION", str(temp))
    try:
        temp.mkdir()
        _write_new(temp / "observation_descriptor.json", _json_bytes(descriptor))
        _write_new(temp / "forward_outcomes.json", _json_bytes(outcomes))
        checks = {
            "package_schema_version": PACKAGE_SCHEMA_VERSION,
            "capability": CAPABILITY,
            "cycle_index": int(cycle_index),
            "future_source_sha256": _sha(future_source),
            "future_candle_rows": len(candles),
            "forward_horizons_bars": list(FORWARD_HORIZONS_BARS),
            "primary_anchor_policy": PRIMARY_ANCHOR_POLICY,
            "context_anchor_policy": CONTEXT_ANCHOR_POLICY,
            "same_bar_target_stop_policy": TARGET_STOP_SAME_BAR_POLICY,
            "partially_elapsed_primary_bar_allowed": False,
            "partially_elapsed_context_bar_allowed": False,
            "future_candles_closed_required": True,
            "future_candles_contiguous_required": True,
            "real_network_request_executed": False,
            "git_network_request_executed": False,
            "official_append_executed": False,
            "official_dataset_changed": False,
            "official_manifest_changed": False,
            "manual_confirmation_required": True,
            **{field: False for field in OUTPUT_FALSE_FIELDS},
        }
        _write_new(temp / "labeler_checks.json", _json_bytes(checks))
        _write_manifest(temp, ("labeler_checks.json", "observation_descriptor.json", "forward_outcomes.json"))
        validate_forward_outcome_label_package(temp)
        temp.rename(output)
    except Exception:
        if temp.exists():
            shutil.rmtree(temp, ignore_errors=True)
        if output.exists():
            shutil.rmtree(output, ignore_errors=True)
        raise

    _req(_official(repo) == official_before, "OFFICIAL_ARTIFACT_CHANGED", "output")
    _gate_off()
    validation = validate_forward_outcome_label_package(output)
    return {
        "capability": CAPABILITY,
        "output_directory": str(output),
        "observation_id": descriptor["observation_id"],
        "primary_candidate_detected": bool(descriptor["primary_candidate_detected"]),
        "future_candle_rows": len(candles),
        "available_primary_horizons": validation["available_primary_horizons"],
        "available_context_horizons": validation["available_context_horizons"],
        "real_network_request_executed": False,
        "git_network_request_executed": False,
        "official_append_executed": False,
        "manual_confirmation_required": True,
        **{field: False for field in OUTPUT_FALSE_FIELDS},
    }


__all__ = [
    "ALLOWED_SYNCHRONIZED_CAPABILITIES",
    "BAR_DURATION",
    "CAPABILITY",
    "CONTEXT_ANCHOR_POLICY",
    "FORWARD_HORIZONS_BARS",
    "FUTURE_SOURCE_COLUMNS",
    "IMPLEMENTATION_OR_REPAIR_ATTEMPT",
    "MAX_IMPLEMENTATION_OR_REPAIR_ATTEMPTS",
    "OBSERVATION_DESCRIPTOR_SCHEMA_VERSION",
    "OUTCOME_SCHEMA_VERSION",
    "PACKAGE_AUTHORIZATION",
    "PACKAGE_SCHEMA_VERSION",
    "PRIMARY_ANCHOR_POLICY",
    "TARGET_STOP_SAME_BAR_POLICY",
    "ForwardOutcomeLabelerError",
    "build_observation_descriptor_from_synchronized_session",
    "label_forward_outcomes",
    "prepare_forward_outcome_label_package",
    "read_future_closed_candles",
    "validate_forward_outcome_label_package",
]
