from __future__ import annotations

import hashlib
import json
import math
import os
import shutil
import time
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

import requests

CAPABILITY = "PUBLIC_READ_ONLY_MICROSTRUCTURE_SNAPSHOT_V1"
IMPLEMENTATION_SCHEMA_VERSION = "PUBLIC_READ_ONLY_MICROSTRUCTURE_SNAPSHOT_IMPLEMENTATION_V1"
SNAPSHOT_SCHEMA_VERSION = "PUBLIC_READ_ONLY_MICROSTRUCTURE_SNAPSHOT_V1"
PROVIDER = "BINANCE_USDM_PUBLIC_REST"
BASE_URL = "https://fapi.binance.com"
SYMBOL = "BTCUSDT"
TIMEFRAME = "15m"
REQUEST_TIMEOUT_SECONDS = 20
DEPTH_LIMIT = 100
MAX_REFERENCE_AGE = timedelta(minutes=30)
AUTHORIZATION = "CAPTURE_ONE_SHOT_BINANCE_USDM_PUBLIC_MICROSTRUCTURE_V1"
OFFICIAL_APPEND_GATE = "TRADING_AI_OFFICIAL_LONG_EVIDENCE_APPEND_ALLOWED"

OFFICIAL_DATASET = Path("data/forward/long_forward_observation_dataset_v1.csv")
OFFICIAL_MANIFEST = Path("data/forward/long_forward_observation_dataset_v1.manifest.csv")
OFFICIAL_LOCK = Path("data/forward/long_forward_observation_dataset_v1.lock")

SUMMARY_FILENAME = "microstructure_snapshot.json"
RAW_FILENAME = "raw_responses.json"
REQUEST_LOG_FILENAME = "request_log.json"
MANIFEST_FILENAME = "manifest.sha256"

ENDPOINTS = (
    ("/fapi/v1/klines", {"symbol": SYMBOL, "interval": TIMEFRAME, "limit": 3}),
    ("/fapi/v1/depth", {"symbol": SYMBOL, "limit": DEPTH_LIMIT}),
    ("/fapi/v1/openInterest", {"symbol": SYMBOL}),
    ("/fapi/v1/premiumIndex", {"symbol": SYMBOL}),
    ("/futures/data/openInterestHist", None),
    ("/futures/data/takerlongshortRatio", None),
    ("/futures/data/globalLongShortAccountRatio", None),
)

FALSE_FIELDS = (
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

class MicrostructureSnapshotError(RuntimeError):
    def __init__(self, code: str, message: str) -> None:
        self.code = code
        super().__init__(message)

def _req(ok: bool, code: str, message: str) -> None:
    if not ok:
        raise MicrostructureSnapshotError(code, message)

def _utc_now() -> datetime:
    return datetime.now(timezone.utc)

def _utc_text(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat()

def _ms_to_dt(value: int) -> datetime:
    return datetime.fromtimestamp(int(value) / 1000, tz=timezone.utc)

def _sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def _json_bytes(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False) + "\n").encode("utf-8")

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

def _number(value: Any, field: str) -> float:
    try:
        result = float(value)
    except (TypeError, ValueError) as exc:
        raise MicrostructureSnapshotError("NUMERIC_INVALID", field) from exc
    _req(math.isfinite(result), "NUMERIC_INVALID", field)
    return result

def _official_hashes(repo: Path) -> dict[str, str]:
    dataset = repo / OFFICIAL_DATASET
    manifest = repo / OFFICIAL_MANIFEST
    lock = repo / OFFICIAL_LOCK
    _req(dataset.is_file() and not dataset.is_symlink(), "OFFICIAL_DATASET_INVALID", str(dataset))
    _req(manifest.is_file() and not manifest.is_symlink(), "OFFICIAL_MANIFEST_INVALID", str(manifest))
    _req(not lock.exists() and not lock.is_symlink(), "OFFICIAL_APPEND_LOCK_PRESENT", str(lock))
    return {"dataset_sha256": _sha(dataset), "manifest_sha256": _sha(manifest)}

def _gate_off() -> None:
    _req(os.environ.get(OFFICIAL_APPEND_GATE) != "1", "OFFICIAL_APPEND_GATE_ENABLED", OFFICIAL_APPEND_GATE)

def _select_latest_closed_kline(rows: Any, captured_at: datetime) -> tuple[list[Any], datetime]:
    _req(isinstance(rows, list) and rows, "KLINE_RESPONSE_INVALID", "rows")
    closed = []
    captured_ms = int(captured_at.timestamp() * 1000)
    for row in rows:
        _req(isinstance(row, list) and len(row) >= 7, "KLINE_RESPONSE_INVALID", "row")
        close_ms = int(row[6])
        if close_ms <= captured_ms:
            closed.append(row)
    _req(closed, "NO_CLOSED_FUTURES_KLINE", "closed")
    latest = max(closed, key=lambda r: int(r[6]))
    close_dt = _ms_to_dt(int(latest[6]))
    age = captured_at - close_dt
    _req(age >= timedelta(0), "REFERENCE_CANDLE_IN_FUTURE", str(close_dt))
    _req(age <= MAX_REFERENCE_AGE, "REFERENCE_CANDLE_STALE", str(age))
    return latest, close_dt

def _parse_depth(raw: Any) -> dict[str, Any]:
    _req(isinstance(raw, Mapping), "DEPTH_RESPONSE_INVALID", "mapping")
    bids_raw = raw.get("bids")
    asks_raw = raw.get("asks")
    _req(isinstance(bids_raw, list) and isinstance(asks_raw, list), "DEPTH_RESPONSE_INVALID", "levels")
    _req(len(bids_raw) > 0 and len(asks_raw) > 0, "DEPTH_EMPTY", "levels")

    def parse_side(rows: Sequence[Any], side: str) -> list[tuple[float, float]]:
        out = []
        for idx, row in enumerate(rows):
            _req(isinstance(row, (list, tuple)) and len(row) >= 2, "DEPTH_LEVEL_INVALID", f"{side}:{idx}")
            price = _number(row[0], f"{side}.price")
            qty = _number(row[1], f"{side}.qty")
            _req(price > 0 and qty >= 0, "DEPTH_LEVEL_INVALID", f"{side}:{idx}")
            out.append((price, qty))
        return out

    bids = parse_side(bids_raw, "bid")
    asks = parse_side(asks_raw, "ask")
    best_bid = max(p for p, _ in bids)
    best_ask = min(p for p, _ in asks)
    _req(best_bid < best_ask, "CROSSED_OR_LOCKED_BOOK", f"{best_bid}/{best_ask}")
    mid = (best_bid + best_ask) / 2.0
    spread = best_ask - best_bid
    spread_bps = spread / mid * 10000.0

    furthest_bid_bps = (mid - min(p for p, _ in bids)) / mid * 10000.0
    furthest_ask_bps = (max(p for p, _ in asks) - mid) / mid * 10000.0

    bands: dict[str, Any] = {}
    for bps in (5, 10, 25, 50):
        bid_levels = [(p, q) for p, q in bids if (mid - p) / mid * 10000.0 <= bps]
        ask_levels = [(p, q) for p, q in asks if (p - mid) / mid * 10000.0 <= bps]
        bid_qty = sum(q for _, q in bid_levels)
        ask_qty = sum(q for _, q in ask_levels)
        bid_notional = sum(p * q for p, q in bid_levels)
        ask_notional = sum(p * q for p, q in ask_levels)
        denom = bid_notional + ask_notional
        bands[str(bps)] = {
            "band_bps": bps,
            "bid_level_count": len(bid_levels),
            "ask_level_count": len(ask_levels),
            "bid_qty_base": bid_qty,
            "ask_qty_base": ask_qty,
            "bid_notional_usdt": bid_notional,
            "ask_notional_usdt": ask_notional,
            "notional_imbalance": ((bid_notional - ask_notional) / denom) if denom > 0 else 0.0,
            "coverage_complete": furthest_bid_bps >= bps and furthest_ask_bps >= bps,
        }

    def strongest(levels: list[tuple[float, float]]) -> dict[str, float]:
        p, q = max(levels, key=lambda item: item[0] * item[1])
        return {
            "price": p,
            "qty_base": q,
            "notional_usdt": p * q,
            "distance_from_mid_bps": abs(p - mid) / mid * 10000.0,
        }

    return {
        "last_update_id": int(raw.get("lastUpdateId", 0)),
        "event_time_utc": _utc_text(_ms_to_dt(int(raw["E"]))) if raw.get("E") is not None else None,
        "transaction_time_utc": _utc_text(_ms_to_dt(int(raw["T"]))) if raw.get("T") is not None else None,
        "returned_bid_levels": len(bids),
        "returned_ask_levels": len(asks),
        "best_bid": best_bid,
        "best_ask": best_ask,
        "mid_price": mid,
        "spread": spread,
        "spread_bps": spread_bps,
        "furthest_bid_distance_bps": furthest_bid_bps,
        "furthest_ask_distance_bps": furthest_ask_bps,
        "strongest_returned_bid_level": strongest(bids),
        "strongest_returned_ask_level": strongest(asks),
        "bands": bands,
        "rpi_orders_included": False,
        "directional_interpretation_allowed": False,
    }

def _latest_two(raw: Any, timestamp_field: str, name: str) -> list[Mapping[str, Any]]:
    _req(isinstance(raw, list) and len(raw) >= 2, "HISTORY_INSUFFICIENT", name)
    rows = sorted(raw, key=lambda x: int(x[timestamp_field]))
    return [rows[-2], rows[-1]]

def _parse_open_interest(current: Any, history: Any, mark_price: float) -> dict[str, Any]:
    _req(isinstance(current, Mapping), "OPEN_INTEREST_INVALID", "current")
    oi = _number(current.get("openInterest"), "openInterest")
    _req(oi >= 0, "OPEN_INTEREST_INVALID", "openInterest")
    pair = _latest_two(history, "timestamp", "open_interest_history")
    prev = _number(pair[0].get("sumOpenInterest"), "sumOpenInterest.previous")
    latest = _number(pair[1].get("sumOpenInterest"), "sumOpenInterest.latest")
    prev_value = _number(pair[0].get("sumOpenInterestValue"), "sumOpenInterestValue.previous")
    latest_value = _number(pair[1].get("sumOpenInterestValue"), "sumOpenInterestValue.latest")
    delta = latest - prev
    delta_pct = (delta / prev * 100.0) if prev != 0 else None
    value_delta = latest_value - prev_value
    value_delta_pct = (value_delta / prev_value * 100.0) if prev_value != 0 else None
    return {
        "current_open_interest_base": oi,
        "current_open_interest_approx_usdt_at_mark": oi * mark_price,
        "current_time_utc": _utc_text(_ms_to_dt(int(current["time"]))),
        "previous_15m": {
            "timestamp_utc": _utc_text(_ms_to_dt(int(pair[0]["timestamp"]))),
            "sum_open_interest": prev,
            "sum_open_interest_value_usdt": prev_value,
        },
        "latest_15m": {
            "timestamp_utc": _utc_text(_ms_to_dt(int(pair[1]["timestamp"]))),
            "sum_open_interest": latest,
            "sum_open_interest_value_usdt": latest_value,
        },
        "change_15m": delta,
        "change_15m_percent": delta_pct,
        "value_change_15m_usdt": value_delta,
        "value_change_15m_percent": value_delta_pct,
        "directional_interpretation_allowed": False,
    }

def _parse_mark(raw: Any) -> dict[str, Any]:
    _req(isinstance(raw, Mapping), "MARK_PRICE_INVALID", "mapping")
    mark = _number(raw.get("markPrice"), "markPrice")
    index = _number(raw.get("indexPrice"), "indexPrice")
    funding = _number(raw.get("lastFundingRate"), "lastFundingRate")
    _req(mark > 0 and index > 0, "MARK_PRICE_INVALID", "positive")
    return {
        "mark_price": mark,
        "index_price": index,
        "mark_minus_index": mark - index,
        "mark_index_basis_bps": (mark - index) / index * 10000.0,
        "last_funding_rate": funding,
        "last_funding_rate_percent": funding * 100.0,
        "interest_rate": _number(raw.get("interestRate"), "interestRate"),
        "next_funding_time_utc": _utc_text(_ms_to_dt(int(raw["nextFundingTime"]))),
        "provider_time_utc": _utc_text(_ms_to_dt(int(raw["time"]))),
        "directional_interpretation_allowed": False,
    }

def _parse_taker(raw: Any) -> dict[str, Any]:
    pair = _latest_two(raw, "timestamp", "taker_ratio")
    def one(row: Mapping[str, Any]) -> dict[str, Any]:
        buy = _number(row.get("buyVol"), "buyVol")
        sell = _number(row.get("sellVol"), "sellVol")
        ratio = _number(row.get("buySellRatio"), "buySellRatio")
        _req(buy >= 0 and sell >= 0 and ratio >= 0, "TAKER_RATIO_INVALID", "positive")
        return {
            "timestamp_utc": _utc_text(_ms_to_dt(int(row["timestamp"]))),
            "buy_volume_base": buy,
            "sell_volume_base": sell,
            "buy_sell_ratio": ratio,
            "net_taker_volume_base": buy - sell,
        }
    previous = one(pair[0]); latest = one(pair[1])
    return {
        "previous_15m": previous,
        "latest_15m": latest,
        "buy_sell_ratio_change": latest["buy_sell_ratio"] - previous["buy_sell_ratio"],
        "directional_interpretation_allowed": False,
    }

def _parse_global_ratio(raw: Any) -> dict[str, Any]:
    pair = _latest_two(raw, "timestamp", "global_long_short")
    def one(row: Mapping[str, Any]) -> dict[str, Any]:
        ratio = _number(row.get("longShortRatio"), "longShortRatio")
        long_a = _number(row.get("longAccount"), "longAccount")
        short_a = _number(row.get("shortAccount"), "shortAccount")
        _req(ratio >= 0 and 0 <= long_a <= 1 and 0 <= short_a <= 1, "GLOBAL_RATIO_INVALID", "range")
        return {
            "timestamp_utc": _utc_text(_ms_to_dt(int(row["timestamp"]))),
            "long_short_account_ratio": ratio,
            "long_account_fraction": long_a,
            "short_account_fraction": short_a,
        }
    previous = one(pair[0]); latest = one(pair[1])
    return {
        "previous_15m": previous,
        "latest_15m": latest,
        "ratio_change": latest["long_short_account_ratio"] - previous["long_short_account_ratio"],
        "top_trader_ratio_used": False,
        "directional_interpretation_allowed": False,
    }

def _request_json(
    get: Callable[..., Any],
    path: str,
    params: Mapping[str, Any],
    request_log: list[dict[str, Any]],
    raw: dict[str, Any],
    key: str,
    clock: Callable[[], datetime],
) -> Any:
    started = clock().astimezone(timezone.utc)
    response = get(BASE_URL + path, params=dict(params), timeout=REQUEST_TIMEOUT_SECONDS)
    finished = clock().astimezone(timezone.utc)
    status = int(getattr(response, "status_code", 0))
    _req(status == 200, "HTTP_STATUS_NOT_200", f"{path}:{status}")
    try:
        payload = response.json()
    except Exception as exc:
        raise MicrostructureSnapshotError("HTTP_JSON_INVALID", path) from exc
    request_log.append({
        "sequence": len(request_log) + 1,
        "method": "GET",
        "endpoint_path": path,
        "params": dict(params),
        "status_code": status,
        "started_at_utc": _utc_text(started),
        "finished_at_utc": _utc_text(finished),
        "duration_ms": max(0.0, (finished - started).total_seconds() * 1000.0),
        "api_key_header_sent": False,
        "authenticated": False,
    })
    raw[key] = payload
    return payload

def validate_public_read_only_microstructure_snapshot(directory: Path | str) -> dict[str, Any]:
    root = Path(directory).resolve()
    summary_path = root / SUMMARY_FILENAME
    raw_path = root / RAW_FILENAME
    request_path = root / REQUEST_LOG_FILENAME
    manifest_path = root / MANIFEST_FILENAME
    for path in (summary_path, raw_path, request_path, manifest_path):
        _req(path.is_file() and not path.is_symlink(), "SNAPSHOT_FILE_MISSING", path.name)

    lines = [line for line in manifest_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    _req(len(lines) == 3, "SNAPSHOT_MANIFEST_INVALID", "entry_count")
    names = []
    for line in lines:
        parts = line.split("  ", 1)
        _req(len(parts) == 2 and len(parts[0]) == 64, "SNAPSHOT_MANIFEST_INVALID", line)
        expected, name = parts
        path = root / name
        _req(path.is_file() and _sha(path) == expected, "SNAPSHOT_HASH_MISMATCH", name)
        names.append(name)
    _req(sorted(names) == sorted([SUMMARY_FILENAME, RAW_FILENAME, REQUEST_LOG_FILENAME]), "SNAPSHOT_SCOPE_INVALID", "scope")

    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    requests_log = json.loads(request_path.read_text(encoding="utf-8"))
    raw = json.loads(raw_path.read_text(encoding="utf-8"))
    _req(summary["snapshot_schema_version"] == SNAPSHOT_SCHEMA_VERSION, "SNAPSHOT_SCHEMA_INVALID", "schema")
    _req(summary["capability"] == CAPABILITY, "SNAPSHOT_CAPABILITY_INVALID", "capability")
    _req(summary["provider"] == PROVIDER and summary["symbol"] == SYMBOL and summary["timeframe"] == TIMEFRAME, "SNAPSHOT_IDENTITY_INVALID", "identity")
    _req(int(summary["request_count"]) == 7, "SNAPSHOT_REQUEST_COUNT_INVALID", "summary")
    _req(isinstance(requests_log, list) and len(requests_log) == 7, "SNAPSHOT_REQUEST_COUNT_INVALID", "request_log")
    expected_paths = [x[0] for x in ENDPOINTS]
    _req([x["endpoint_path"] for x in requests_log] == expected_paths, "SNAPSHOT_ENDPOINT_SEQUENCE_INVALID", "sequence")
    _req(all(x["method"] == "GET" and x["api_key_header_sent"] is False and x["authenticated"] is False for x in requests_log), "SNAPSHOT_REQUEST_PERMISSION_INVALID", "request")
    _req(sorted(raw.keys()) == sorted(["futures_klines","order_book","open_interest","mark_price_funding","open_interest_history","taker_buy_sell_volume","global_long_short_account_ratio"]), "RAW_SCOPE_INVALID", "keys")
    for field in FALSE_FIELDS:
        _req(summary[field] is False, "SNAPSHOT_PERMISSION_INVALID", field)
    _req(summary["official_dataset_sha256_before"] == summary["official_dataset_sha256_after"], "OFFICIAL_ARTIFACT_CHANGED", "dataset")
    _req(summary["official_manifest_sha256_before"] == summary["official_manifest_sha256_after"], "OFFICIAL_ARTIFACT_CHANGED", "manifest")
    _req(summary["interpretation_constraints"]["context_only"] is True, "CONTEXT_CONSTRAINT_INVALID", "context_only")
    _req(summary["interpretation_constraints"]["does_not_modify_frozen_long_rule"] is True, "CONTEXT_CONSTRAINT_INVALID", "frozen_rule")
    return {
        "request_count": 7,
        "manifest_entries": 3,
        "reference_closed_candle_utc": summary["reference_closed_candle_utc"],
        "best_bid": summary["order_book"]["best_bid"],
        "best_ask": summary["order_book"]["best_ask"],
        "spread_bps": summary["order_book"]["spread_bps"],
        "last_funding_rate": summary["mark_price_funding"]["last_funding_rate"],
        "open_interest_change_15m_percent": summary["open_interest"]["change_15m_percent"],
        "taker_buy_sell_ratio": summary["taker_buy_sell_volume"]["latest_15m"]["buy_sell_ratio"],
        "global_long_short_account_ratio": summary["global_long_short_account_ratio"]["latest_15m"]["long_short_account_ratio"],
    }

def capture_public_read_only_microstructure_snapshot(
    *,
    repo_root: Path | str,
    output_directory: Path | str,
    authorization: str | None = None,
    request_get: Callable[..., Any] | None = None,
    clock: Callable[[], datetime] | None = None,
) -> dict[str, Any]:
    _req(authorization == AUTHORIZATION, "SNAPSHOT_AUTHORIZATION_REQUIRED", "authorization")
    _gate_off()
    repo = Path(repo_root).resolve()
    out = Path(output_directory).resolve()
    _req((repo / ".git").is_dir(), "REPOSITORY_ROOT_INVALID", str(repo))
    _req(not _inside(out, repo), "OUTPUT_INSIDE_REPOSITORY_PROHIBITED", str(out))
    _req(out.parent.is_dir() and not out.parent.is_symlink(), "OUTPUT_PARENT_INVALID", str(out.parent))
    _req(not out.exists() and not out.is_symlink(), "OUTPUT_ALREADY_EXISTS", str(out))

    now = clock or _utc_now
    get = request_get or requests.get
    official_before = _official_hashes(repo)
    captured_started = now().astimezone(timezone.utc)
    temp = out.parent / f".{out.name}.tmp-{uuid.uuid4().hex}"
    request_log: list[dict[str, Any]] = []
    raw: dict[str, Any] = {}
    try:
        temp.mkdir()
        klines = _request_json(get, "/fapi/v1/klines", {"symbol": SYMBOL, "interval": TIMEFRAME, "limit": 3}, request_log, raw, "futures_klines", now)
        reference_kline, reference_close_dt = _select_latest_closed_kline(klines, captured_started)
        reference_boundary_ms = int(reference_kline[6]) + 1

        depth = _request_json(get, "/fapi/v1/depth", {"symbol": SYMBOL, "limit": DEPTH_LIMIT}, request_log, raw, "order_book", now)
        current_oi = _request_json(get, "/fapi/v1/openInterest", {"symbol": SYMBOL}, request_log, raw, "open_interest", now)
        mark_raw = _request_json(get, "/fapi/v1/premiumIndex", {"symbol": SYMBOL}, request_log, raw, "mark_price_funding", now)
        history_params = {"symbol": SYMBOL, "period": TIMEFRAME, "limit": 2, "endTime": reference_boundary_ms}
        oi_hist = _request_json(get, "/futures/data/openInterestHist", history_params, request_log, raw, "open_interest_history", now)
        taker = _request_json(get, "/futures/data/takerlongshortRatio", history_params, request_log, raw, "taker_buy_sell_volume", now)
        global_ratio = _request_json(get, "/futures/data/globalLongShortAccountRatio", history_params, request_log, raw, "global_long_short_account_ratio", now)

        mark = _parse_mark(mark_raw)
        book = _parse_depth(depth)
        oi = _parse_open_interest(current_oi, oi_hist, mark["mark_price"])
        taker_parsed = _parse_taker(taker)
        global_parsed = _parse_global_ratio(global_ratio)

        official_after = _official_hashes(repo)
        _req(official_after == official_before, "OFFICIAL_ARTIFACT_CHANGED", "official")
        _gate_off()
        captured_finished = now().astimezone(timezone.utc)
        summary = {
            "snapshot_schema_version": SNAPSHOT_SCHEMA_VERSION,
            "capability": CAPABILITY,
            "implementation_schema_version": IMPLEMENTATION_SCHEMA_VERSION,
            "provider": PROVIDER,
            "symbol": SYMBOL,
            "timeframe": TIMEFRAME,
            "capture_mode": "ONE_SHOT_FOREGROUND_PUBLIC_READ_ONLY",
            "captured_started_at_utc": _utc_text(captured_started),
            "captured_finished_at_utc": _utc_text(captured_finished),
            "reference_closed_candle_utc": _utc_text(reference_close_dt),
            "reference_futures_candle": {
                "open_time_utc": _utc_text(_ms_to_dt(int(reference_kline[0]))),
                "open": _number(reference_kline[1], "reference.open"),
                "high": _number(reference_kline[2], "reference.high"),
                "low": _number(reference_kline[3], "reference.low"),
                "close": _number(reference_kline[4], "reference.close"),
                "volume": _number(reference_kline[5], "reference.volume"),
                "close_time_utc": _utc_text(reference_close_dt),
            },
            "request_count": 7,
            "endpoint_paths": [x["endpoint_path"] for x in request_log],
            "order_book": book,
            "open_interest": oi,
            "mark_price_funding": mark,
            "taker_buy_sell_volume": taker_parsed,
            "global_long_short_account_ratio": global_parsed,
            "synchronization": {
                "reference_boundary_utc": _utc_text(_ms_to_dt(reference_boundary_ms)),
                "point_in_time_components": ["order_book","current_open_interest","mark_price_funding"],
                "aligned_15m_components": ["open_interest_history","taker_buy_sell_volume","global_long_short_account_ratio"],
                "point_in_time_components_are_not_historical_reconstruction": True,
            },
            "interpretation_constraints": {
                "context_only": True,
                "does_not_modify_frozen_long_rule": True,
                "order_book_is_resting_visible_depth_only": True,
                "order_book_does_not_reveal_hidden_stops_or_liquidations": True,
                "open_interest_does_not_identify_long_vs_short_direction": True,
                "funding_and_ratios_are_descriptive_not_actionable": True,
                "top_trader_ratios_excluded_because_current_docs_require_api_key": True,
                "liquidation_stream_not_used": True,
                "heatmap_not_used": True,
            },
            "official_dataset_sha256_before": official_before["dataset_sha256"],
            "official_dataset_sha256_after": official_after["dataset_sha256"],
            "official_manifest_sha256_before": official_before["manifest_sha256"],
            "official_manifest_sha256_after": official_after["manifest_sha256"],
            **{field: False for field in FALSE_FIELDS},
        }

        _write_new(temp / RAW_FILENAME, _json_bytes(raw))
        _write_new(temp / REQUEST_LOG_FILENAME, _json_bytes(request_log))
        _write_new(temp / SUMMARY_FILENAME, _json_bytes(summary))
        manifest_lines = [
            f"{_sha(temp / RAW_FILENAME)}  {RAW_FILENAME}",
            f"{_sha(temp / REQUEST_LOG_FILENAME)}  {REQUEST_LOG_FILENAME}",
            f"{_sha(temp / SUMMARY_FILENAME)}  {SUMMARY_FILENAME}",
        ]
        _write_new(temp / MANIFEST_FILENAME, ("\n".join(manifest_lines) + "\n").encode("utf-8"))
        temp.rename(out)
        validation = validate_public_read_only_microstructure_snapshot(out)
        return {
            "capability": CAPABILITY,
            "output_directory": str(out),
            "request_count": 7,
            "reference_closed_candle_utc": summary["reference_closed_candle_utc"],
            "best_bid": book["best_bid"],
            "best_ask": book["best_ask"],
            "mid_price": book["mid_price"],
            "spread_bps": book["spread_bps"],
            "last_funding_rate": mark["last_funding_rate"],
            "open_interest_change_15m_percent": oi["change_15m_percent"],
            "taker_buy_sell_ratio": taker_parsed["latest_15m"]["buy_sell_ratio"],
            "global_long_short_account_ratio": global_parsed["latest_15m"]["long_short_account_ratio"],
            "manifest_entries": validation["manifest_entries"],
            "foreground_only": True,
            "public_read_only": True,
            **{field: False for field in FALSE_FIELDS},
        }
    except Exception:
        if temp.exists():
            shutil.rmtree(temp, ignore_errors=True)
        if out.exists():
            shutil.rmtree(out, ignore_errors=True)
        raise

__all__ = [
    "AUTHORIZATION",
    "CAPABILITY",
    "DEPTH_LIMIT",
    "ENDPOINTS",
    "FALSE_FIELDS",
    "IMPLEMENTATION_SCHEMA_VERSION",
    "MicrostructureSnapshotError",
    "SNAPSHOT_SCHEMA_VERSION",
    "capture_public_read_only_microstructure_snapshot",
    "validate_public_read_only_microstructure_snapshot",
]
