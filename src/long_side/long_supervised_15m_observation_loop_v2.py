from __future__ import annotations

import csv, hashlib, json, os, time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Callable, Mapping

CAPABILITY = "LONG_SUPERVISED_15M_OBSERVATION_LOOP_V2"
IMPLEMENTATION_SCHEMA_VERSION = "LONG_SUPERVISED_15M_OBSERVATION_LOOP_IMPLEMENTATION_V2"
SESSION_SCHEMA_VERSION = "LONG_SUPERVISED_15M_OBSERVATION_SESSION_V2"
SESSION_AUTHORIZATION = "RUN_BOUNDED_SUPERVISED_15M_OBSERVATION_SESSION_V2"
REAL_SOURCE_ATTESTATION = "REAL_MARKET_DATA_SOURCE_HUMAN_ATTESTED_NOT_SYNTHETIC"
MAX_OBSERVATION_CYCLES = 8
MAX_IMPLEMENTATION_OR_REPAIR_ATTEMPTS = 10
IMPLEMENTATION_OR_REPAIR_ATTEMPT = 1
CAPTURE_GRACE_SECONDS = 5
OFFICIAL_APPEND_GATE_NAME = "TRADING_AI_OFFICIAL_LONG_EVIDENCE_APPEND_ALLOWED"

HUMAN_4H_PULLBACK_HYPOTHESIS = {"entry": 61310.00, "stop": 59224.68, "target": 68053.13}
HUMAN_15M_FIBONACCI_CONTEXT = {
    "confluence_38_2_low": 63956.34,
    "confluence_38_2_high": 64019.05,
    "intermediate": 64358.87,
    "upper_level_1": 65114.87,
    "upper_liquidity_cluster_low": 65644.66,
    "upper_liquidity_cluster_high": 65925.31,
    "lower_cluster_low": 63310.99,
    "lower_cluster_high": 63350.39,
    "lower_level": 62844.75,
}

DATASET = Path("data/forward/long_forward_observation_dataset_v1.csv")
OFFICIAL_MANIFEST = Path("data/forward/long_forward_observation_dataset_v1.manifest.csv")
OFFICIAL_LOCK = Path("data/forward/long_forward_observation_dataset_v1.lock")
EVENTS_FILENAME = "session_events.jsonl"
SUMMARY_FILENAME = "session_summary.json"
MANIFEST_FILENAME = "manifest.sha256"
FALSE_FIELDS = (
    "official_dataset_write_allowed", "official_append_allowed", "evidence_persistence_allowed",
    "signal_generation_enabled", "live_alerts_allowed", "paper_trade_execution_allowed",
    "real_capital_allowed", "market_execution_allowed", "exchange_execution_allowed",
    "automation_allowed", "execution_allowed",
)

class Supervised15mObservationLoopError(RuntimeError):
    def __init__(self, code: str, message: str) -> None:
        self.code = code
        super().__init__(message)

def _req(ok: bool, code: str, message: str) -> None:
    if not ok:
        raise Supervised15mObservationLoopError(code, message)

def _utc(v: datetime) -> str:
    return v.astimezone(timezone.utc).isoformat()

def _parse(v: str, field: str) -> datetime:
    try:
        out = datetime.fromisoformat(v)
    except (TypeError, ValueError) as exc:
        raise Supervised15mObservationLoopError("UTC_TIMESTAMP_INVALID", field) from exc
    _req(out.tzinfo is not None, "UTC_TIMESTAMP_INVALID", field)
    return out.astimezone(timezone.utc)

def _inside(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False

def _sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def _json_bytes(obj: Mapping[str, Any]) -> bytes:
    return (json.dumps(dict(obj), sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False) + "\n").encode()

def _append(path: Path, obj: Mapping[str, Any]) -> None:
    with path.open("ab") as f:
        f.write(_json_bytes(obj)); f.flush(); os.fsync(f.fileno())

def _write_new(path: Path, data: bytes) -> None:
    with path.open("xb") as f:
        f.write(data); f.flush(); os.fsync(f.fileno())

def _official(repo: Path) -> dict[str, str]:
    ds, mf, lock = repo / DATASET, repo / OFFICIAL_MANIFEST, repo / OFFICIAL_LOCK
    _req(ds.is_file() and not ds.is_symlink(), "OFFICIAL_DATASET_INVALID", str(ds))
    _req(mf.is_file() and not mf.is_symlink(), "OFFICIAL_MANIFEST_INVALID", str(mf))
    _req(not lock.exists() and not lock.is_symlink(), "OFFICIAL_APPEND_LOCK_PRESENT", str(lock))
    return {"dataset_sha256": _sha(ds), "manifest_sha256": _sha(mf)}

def _gate_off() -> None:
    _req(os.environ.get(OFFICIAL_APPEND_GATE_NAME) != "1", "OFFICIAL_APPEND_GATE_ENABLED", "gate")

def next_15m_capture_time(now: datetime) -> datetime:
    cur = now.astimezone(timezone.utc)
    minute = (cur.minute // 15) * 15
    boundary = cur.replace(minute=minute, second=0, microsecond=0)
    target = boundary + timedelta(seconds=CAPTURE_GRACE_SECONDS)
    return target if cur <= target else target + timedelta(minutes=15)

def _validate_context() -> None:
    h4 = HUMAN_4H_PULLBACK_HYPOTHESIS
    _req(0 < h4["stop"] < h4["entry"] < h4["target"], "HUMAN_4H_CONTEXT_INVALID", "order")
    h = HUMAN_15M_FIBONACCI_CONTEXT
    ordered = [h["lower_level"], h["lower_cluster_low"], h["lower_cluster_high"], h["confluence_38_2_low"], h["confluence_38_2_high"], h["intermediate"], h["upper_level_1"], h["upper_liquidity_cluster_low"], h["upper_liquidity_cluster_high"]]
    _req(all(a < b for a, b in zip(ordered, ordered[1:])), "HUMAN_15M_CONTEXT_INVALID", "order")

def _zone(low: float, high: float, a: float, b: float) -> bool:
    return high >= a and low <= b

def _state(close: float) -> str:
    h = HUMAN_15M_FIBONACCI_CONTEXT
    if close > h["upper_liquidity_cluster_high"]: return "ABOVE_UPPER_LIQUIDITY_CLUSTER"
    if close >= h["upper_liquidity_cluster_low"]: return "INSIDE_UPPER_LIQUIDITY_CLUSTER"
    if close > h["upper_level_1"]: return "BETWEEN_UPPER_LEVEL_1_AND_UPPER_LIQUIDITY_CLUSTER"
    if close > h["intermediate"]: return "BETWEEN_INTERMEDIATE_AND_UPPER_LEVEL_1"
    if close > h["confluence_38_2_high"]: return "BETWEEN_38_2_CONFLUENCE_AND_INTERMEDIATE"
    if close >= h["confluence_38_2_low"]: return "INSIDE_38_2_CONFLUENCE"
    if close > h["lower_cluster_high"]: return "BETWEEN_LOWER_CLUSTER_AND_38_2_CONFLUENCE"
    if close >= h["lower_cluster_low"]: return "INSIDE_LOWER_CLUSTER"
    if close > h["lower_level"]: return "BETWEEN_LOWER_LEVEL_AND_LOWER_CLUSTER"
    return "AT_OR_BELOW_LOWER_LEVEL"

def compare_with_frozen_human_context(latest: Mapping[str, Any]) -> dict[str, Any]:
    _validate_context()
    o, hi, lo, c = map(float, (latest["open"], latest["high"], latest["low"], latest["close"]))
    h = HUMAN_15M_FIBONACCI_CONTEXT
    levels = {}
    for name, price in h.items():
        levels[name] = {
            "price": price, "close_minus_level": c - price, "absolute_distance": abs(c - price),
            "position": "ABOVE" if c > price else "BELOW" if c < price else "AT",
            "touched_by_latest_candle": lo <= price <= hi,
        }
    nearest_name, nearest = min(levels.items(), key=lambda item: item[1]["absolute_distance"])
    h4 = HUMAN_4H_PULLBACK_HYPOTHESIS
    return {
        "latest_candle_direction": "BULLISH" if c > o else "BEARISH" if c < o else "FLAT",
        "positional_state": _state(c), "nearest_level": nearest_name,
        "nearest_level_price": nearest["price"], "nearest_level_distance": nearest["absolute_distance"],
        "levels": levels,
        "zones": {
            "confluence_38_2_touched": _zone(lo, hi, h["confluence_38_2_low"], h["confluence_38_2_high"]),
            "upper_liquidity_cluster_touched": _zone(lo, hi, h["upper_liquidity_cluster_low"], h["upper_liquidity_cluster_high"]),
            "lower_cluster_touched": _zone(lo, hi, h["lower_cluster_low"], h["lower_cluster_high"]),
        },
        "human_4h_pullback_hypothesis": {
            **h4, "entry_touched": lo <= h4["entry"] <= hi, "stop_touched": lo <= h4["stop"] <= hi,
            "target_touched": lo <= h4["target"] <= hi, "close_minus_entry": c - h4["entry"],
            "target_minus_close": h4["target"] - c,
            "reward_risk_ratio": (h4["target"] - h4["entry"]) / (h4["entry"] - h4["stop"]),
        },
        "direction_inferred_from_levels": False, "liquidity_side_inferred_without_microstructure": False,
        "heatmap_used": False, "context_only": True, "actionable_signal_generated": False,
    }

def _latest(source: Path) -> dict[str, Any]:
    with source.open("r", encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    _req(len(rows) >= 49, "SOURCE_WARMUP_INSUFFICIENT", "rows")
    r = rows[-1]
    _req(r["symbol"] == "BTCUSDT" and r["timeframe"] == "15m" and r["candle_closed"] == "True", "SOURCE_CONTRACT_INVALID", "latest")
    return {k: (float(r[k]) if k in {"open","high","low","close","volume"} else True if k == "candle_closed" else r[k]) for k in ("open_time_utc","close_time_utc","symbol","timeframe","open","high","low","close","volume","candle_closed")}

def _capture_default():
    from src.exchange.long_primary_public_closed_candle_capture_v1 import capture_real_binance_public_closed_candles
    return capture_real_binance_public_closed_candles

def _package_default():
    from src.long_side.long_primary_prospective_observation_source_adapter_v1 import prepare_real_source_review_package
    return prepare_real_source_review_package

def _capture_safe(c: Mapping[str, Any]) -> None:
    _req(int(c["network_request_count"]) == 1 and bool(c["one_shot_foreground"]), "CAPTURE_MODE_INVALID", "capture")
    for field in ("review_package_created","candidate_evaluated","candidate_detected","manual_confirmed","official_dataset_write_performed","official_manifest_write_performed","official_append_invoked","official_append_environment_gate_modified","signal_generation_enabled","live_alerts_allowed","paper_trade_execution_allowed","real_capital_allowed","market_execution_allowed","exchange_execution_allowed","automation_allowed","execution_allowed"):
        _req(bool(c[field]) is False, "CAPTURE_PERMISSION_INVALID", field)

def _package_safe(p: Mapping[str, Any], c: Mapping[str, Any]) -> None:
    _req(str(p["source_artifact_sha256"]) == str(c["source_artifact_sha256"]), "PACKAGE_PROVENANCE_MISMATCH", "hash")
    _req(str(p["latest_closed_candle_utc"]) == str(c["latest_closed_candle_utc"]), "PACKAGE_CANDLE_MISMATCH", "time")
    _req(bool(p["manual_confirmation_required"]) and not bool(p["manual_confirmed"]), "PACKAGE_REVIEW_STATE_INVALID", "review")
    for field in ("official_dataset_write_performed","official_manifest_write_performed","official_append_environment_gate_modified","paper_trade_execution_allowed","real_capital_allowed","market_execution_allowed","exchange_execution_allowed","automation_allowed","execution_allowed"):
        _req(bool(p[field]) is False, "PACKAGE_PERMISSION_INVALID", field)

def validate_supervised_15m_session(directory: Path | str) -> dict[str, Any]:
    root = Path(directory).resolve(); events = root / EVENTS_FILENAME; summary = root / SUMMARY_FILENAME; manifest = root / MANIFEST_FILENAME
    for p in (events, summary, manifest): _req(p.is_file() and not p.is_symlink(), "SESSION_FILE_MISSING", p.name)
    lines = manifest.read_text(encoding="utf-8").splitlines(); _req(len(lines) == 2, "SESSION_MANIFEST_INVALID", "count")
    names = []
    for line in lines:
        parts = line.split("  ", 1); _req(len(parts) == 2 and len(parts[0]) == 64, "SESSION_MANIFEST_INVALID", line)
        expected, name = parts; p = root / name; _req(p.is_file() and _sha(p) == expected, "SESSION_HASH_MISMATCH", name); names.append(name)
    _req(sorted(names) == sorted([EVENTS_FILENAME, SUMMARY_FILENAME]), "SESSION_SCOPE_INVALID", "scope")
    s = json.loads(summary.read_text(encoding="utf-8")); _req(s["session_schema_version"] == SESSION_SCHEMA_VERSION, "SESSION_SCHEMA_INVALID", "schema")
    for field in FALSE_FIELDS: _req(s[field] is False, "SESSION_PERMISSION_INVALID", field)
    es = [json.loads(x) for x in events.read_text(encoding="utf-8").splitlines() if x.strip()]
    cycles = [x for x in es if x.get("event") == "CYCLE_COMPLETED"]
    _req(len(cycles) == int(s["completed_cycles"]), "SESSION_EVENT_COUNT_INVALID", "events")
    return {"completed_cycles": int(s["completed_cycles"]), "candidate_count": int(s["candidate_count"]), "stop_reason": s["stop_reason"], "event_count": len(es), "manifest_entries": 2}

def run_bounded_supervised_15m_session(*, repo_root: Path | str, output_directory: Path | str, max_cycles: int, source_attestation: str, minimum_latest_closed_candle_utc: str | None, authorization: str | None = None, clock: Callable[[], datetime] | None = None, sleeper: Callable[[float], None] | None = None, capture_callable: Callable[..., Mapping[str, Any]] | None = None, package_callable: Callable[..., Mapping[str, Any]] | None = None) -> dict[str, Any]:
    _req(authorization == SESSION_AUTHORIZATION, "SESSION_AUTHORIZATION_REQUIRED", "authorization")
    _req(source_attestation == REAL_SOURCE_ATTESTATION, "SESSION_SOURCE_ATTESTATION_REQUIRED", "attestation")
    _req(isinstance(max_cycles, int) and 1 <= max_cycles <= MAX_OBSERVATION_CYCLES, "SESSION_CYCLE_LIMIT_INVALID", "cycles")
    _validate_context(); _gate_off()
    repo, out = Path(repo_root).resolve(), Path(output_directory).resolve()
    _req((repo / ".git").is_dir(), "REPOSITORY_ROOT_INVALID", "repo")
    _req(not _inside(out, repo), "OUTPUT_INSIDE_REPOSITORY_PROHIBITED", "output")
    _req(out.parent.is_dir() and not out.parent.is_symlink(), "OUTPUT_PARENT_INVALID", "parent")
    _req(not out.exists() and not out.is_symlink(), "OUTPUT_ALREADY_EXISTS", "output")
    official_before = _official(repo)
    prior = _parse(minimum_latest_closed_candle_utc, "minimum_latest_closed_candle_utc") if minimum_latest_closed_candle_utc else None
    now = clock or (lambda: datetime.now(timezone.utc)); sleep = sleeper or time.sleep; capture_fn = capture_callable or _capture_default(); package_fn = package_callable or _package_default()
    out.mkdir(); captures = out / "captures"; reviews = out / "reviews"; captures.mkdir(); reviews.mkdir(); events = out / EVENTS_FILENAME; _write_new(events, b"")
    started = now().astimezone(timezone.utc); _append(events, {"event":"SESSION_STARTED","at_utc":_utc(started),"requested_cycles":max_cycles,"minimum_latest_closed_candle_utc":_utc(prior) if prior else None,"human_context_is_non_actionable":True,"external_notifications_allowed":False,"official_append_allowed":False})
    completed = candidates = 0; latest_text = None; stop_reason = "MAX_CYCLES_COMPLETED"
    try:
        for idx in range(1, max_cycles + 1):
            _gate_off(); scheduled = next_15m_capture_time(now()); sleep(max(0.0, (scheduled - now().astimezone(timezone.utc)).total_seconds()))
            name = f"cycle_{idx:04d}"; c = dict(capture_fn(repo_root=repo, output_directory=captures/name, authorization="CAPTURE_ONE_SHOT_BINANCE_PUBLIC_CLOSED_CANDLES_V1")); _capture_safe(c)
            latest_dt = _parse(str(c["latest_closed_candle_utc"]), "latest_closed_candle_utc"); _req(prior is None or latest_dt > prior, "DUPLICATE_OR_OLD_CANDLE", "candle"); prior = latest_dt; latest_text = _utc(latest_dt)
            source = Path(str(c["source_csv"])).resolve(); last = _latest(source); comparison = compare_with_frozen_human_context(last); metadata = json.loads(Path(str(c["metadata_json"])).read_text(encoding="utf-8"))
            p = dict(package_fn(repo_root=repo, source_csv=source, output_directory=reviews/name, captured_at_utc=str(metadata["captured_at_utc"]), prospective_start_utc=str(c["latest_closed_candle_utc"]), source_system="BINANCE_PUBLIC_SPOT_API", source_capture_id=str(c["capture_id"]), source_attestation=source_attestation, expected_source_sha256=str(c["source_artifact_sha256"]), authorization="PREPARE_REAL_LONG_PRIMARY_HUMAN_REVIEW_PACKAGE_V1")); _package_safe(p, c)
            candidate = bool(p["candidate_detected"]); completed += 1; candidates += int(candidate)
            _append(events, {"event":"CYCLE_COMPLETED","cycle_index":idx,"scheduled_at_utc":_utc(scheduled),"capture_id":c["capture_id"],"package_id":p["package_id"],"latest_closed_candle_utc":c["latest_closed_candle_utc"],"source_artifact_sha256":c["source_artifact_sha256"],"latest_candle":last,"human_context_comparison":comparison,"candidate_detected":candidate,"eligible_for_real_human_review":bool(p["eligible_for_real_human_review"]),"manual_confirmed":False,"official_append_invoked":False,"external_notification_sent":False,"actionable_signal_generated":False})
            _req(_official(repo) == official_before, "OFFICIAL_ARTIFACT_CHANGED", "official"); _gate_off()
            if candidate: stop_reason = "FIRST_CANDIDATE_PENDING_HUMAN_REVIEW"; break
    except Exception as exc:
        _append(events, {"event":"SESSION_ABORTED_FAIL_CLOSED","at_utc":_utc(now()),"completed_cycles":completed,"error_type":type(exc).__name__,"error_message":str(exc),"official_append_invoked":False,"external_notification_sent":False}); raise
    official_after = _official(repo); _req(official_after == official_before, "OFFICIAL_ARTIFACT_CHANGED", "official"); _gate_off(); finished = now().astimezone(timezone.utc)
    s = {"session_schema_version":SESSION_SCHEMA_VERSION,"capability":CAPABILITY,"implementation_schema_version":IMPLEMENTATION_SCHEMA_VERSION,"implementation_or_repair_attempt":IMPLEMENTATION_OR_REPAIR_ATTEMPT,"max_implementation_or_repair_attempts":MAX_IMPLEMENTATION_OR_REPAIR_ATTEMPTS,"session_mode":"BOUNDED_FOREGROUND_SUPERVISED","started_at_utc":_utc(started),"finished_at_utc":_utc(finished),"requested_cycles":max_cycles,"completed_cycles":completed,"candidate_count":candidates,"no_candidate_count":completed-candidates,"stop_on_first_candidate":True,"stop_reason":stop_reason,"latest_closed_candle_utc":latest_text,"network_request_count":completed,"human_4h_context":HUMAN_4H_PULLBACK_HYPOTHESIS,"human_15m_context":HUMAN_15M_FIBONACCI_CONTEXT,"human_context_mutates_frozen_candidate_rule":False,"automatic_or_background_execution":False,"recurring_scheduler_installed":False,"external_notifications_sent":False,"messages_sent":False,"browser_control_used":False,"tradingview_account_accessed":False,"heatmap_used":False,"microstructure_layer_enabled":False,"manual_confirmation_required":True,"manual_confirmed":False,"official_dataset_sha256_before":official_before["dataset_sha256"],"official_dataset_sha256_after":official_after["dataset_sha256"],"official_manifest_sha256_before":official_before["manifest_sha256"],"official_manifest_sha256_after":official_after["manifest_sha256"],**{f:False for f in FALSE_FIELDS}}
    _write_new(out/SUMMARY_FILENAME, _json_bytes(s)); lines = [f"{_sha(events)}  {EVENTS_FILENAME}", f"{_sha(out/SUMMARY_FILENAME)}  {SUMMARY_FILENAME}"]; _write_new(out/MANIFEST_FILENAME, ("\n".join(lines)+"\n").encode())
    v = validate_supervised_15m_session(out)
    return {"capability":CAPABILITY,"output_directory":str(out),"requested_cycles":max_cycles,"completed_cycles":completed,"candidate_count":candidates,"no_candidate_count":completed-candidates,"stop_reason":stop_reason,"network_request_count":completed,"latest_closed_candle_utc":latest_text,"foreground_only":True,"bounded":True,"external_notifications_sent":False,"manual_confirmation_required":True,"manual_confirmed":False,**{f:False for f in FALSE_FIELDS},"session_manifest_entries":v["manifest_entries"],"session_event_count":v["event_count"]}

__all__ = ["CAPABILITY","HUMAN_15M_FIBONACCI_CONTEXT","HUMAN_4H_PULLBACK_HYPOTHESIS","IMPLEMENTATION_OR_REPAIR_ATTEMPT","MAX_IMPLEMENTATION_OR_REPAIR_ATTEMPTS","MAX_OBSERVATION_CYCLES","REAL_SOURCE_ATTESTATION","SESSION_AUTHORIZATION","Supervised15mObservationLoopError","compare_with_frozen_human_context","next_15m_capture_time","run_bounded_supervised_15m_session","validate_supervised_15m_session"]
