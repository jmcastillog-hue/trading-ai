from __future__ import annotations

import csv
import hashlib
import json
import math
import os
import shutil
import statistics
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence

from src.context.context_feature_pack_v1_level_a_standard import FEATURE_REGISTRY, build_context_feature_pack_v1
from src.exchange.long_primary_public_closed_candle_capture_v1 import (
    CAPABILITY as CLOSED_CANDLE_CAPTURE_CAPABILITY,
    METADATA_FILENAME as SOURCE_METADATA_FILENAME,
    PROVIDER as SOURCE_PROVIDER,
    SOURCE_COLUMNS,
    SOURCE_FILENAME,
    validate_closed_candle_capture,
)

CAPABILITY = "LIQUIDITY_SWEEP_PATTERN_CONTEXT_V1"
FEATURE_ID = "LIQUIDITY_SWEEP_PATTERN_CONTEXT_V1"
FEATURE_SCHEMA_VERSION = "LIQUIDITY_SWEEP_PATTERN_CONTEXT_V1_SCHEMA_V1"
PACKAGE_SCHEMA_VERSION = "LIQUIDITY_SWEEP_PATTERN_CONTEXT_V1_PACKAGE_V1"
SOURCE_KIND = "OBSERVED_MARKET"
PACKAGE_AUTHORIZATION = "PREPARE_LIQUIDITY_SWEEP_PATTERN_CONTEXT_V1"
MAX_IMPLEMENTATION_OR_REPAIR_ATTEMPTS = 10
IMPLEMENTATION_OR_REPAIR_ATTEMPT = 1
POLICY_PATH = Path("src/context/resources/liquidity_sweep_pattern_context_policy_v1.json")
EXPECTED_POLICY_SCHEMA_VERSION = "LIQUIDITY_SWEEP_PATTERN_CONTEXT_POLICY_V1"
EXPECTED_SYMBOL = "BTCUSDT"
EXPECTED_TIMEFRAME = "15m"
ROLLING_EXTREME_LOOKBACK_BARS = 48
ATR_BARS = 14
MINIMUM_REQUIRED_ROWS = 49
BAR_DURATION = timedelta(minutes=15)
CLOSE_EPSILON = timedelta(milliseconds=1)
COMPONENT_FILENAME = "liquidity_sweep_pattern_context_component.json"
CHECKS_FILENAME = "producer_checks.json"
MANIFEST_FILENAME = "manifest.sha256"
OFFICIAL_APPEND_GATE_NAME = "TRADING_AI_OFFICIAL_LONG_EVIDENCE_APPEND_ALLOWED"
OFFICIAL_DATASET = Path("data/forward/long_forward_observation_dataset_v1.csv")
OFFICIAL_MANIFEST = Path("data/forward/long_forward_observation_dataset_v1.manifest.csv")
OFFICIAL_LOCK = Path("data/forward/long_forward_observation_dataset_v1.lock")
FALSE_PERMISSION_FIELDS = (
    "candidate_modification_allowed", "primary_rule_modification_allowed",
    "signal_generation_enabled", "live_alerts_allowed",
    "paper_trade_execution_allowed", "real_capital_allowed",
    "market_execution_allowed", "exchange_execution_allowed",
    "official_dataset_write_allowed", "official_append_allowed",
    "automation_allowed", "execution_allowed",
)

class LiquiditySweepPatternContextError(RuntimeError):
    def __init__(self, code: str, message: str) -> None:
        self.code = code
        super().__init__(message)

def _req(ok: bool, code: str, message: str) -> None:
    if not ok:
        raise LiquiditySweepPatternContextError(code, message)

def _sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def _json_bytes(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False) + "\n").encode("utf-8")

def _write_new(path: Path, payload: bytes) -> None:
    with path.open("xb") as f:
        f.write(payload); f.flush(); os.fsync(f.fileno())

def _inside(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root); return True
    except ValueError:
        return False

def _parse_utc(value: Any, field: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(str(value).strip().replace("Z", "+00:00"))
    except ValueError as exc:
        raise LiquiditySweepPatternContextError("TIMESTAMP_INVALID", field) from exc
    _req(parsed.tzinfo is not None, "TIMESTAMP_TIMEZONE_REQUIRED", field)
    return parsed.astimezone(timezone.utc)

def _utc(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat()

def _number(value: Any, field: str) -> float:
    try:
        x = float(value)
    except (TypeError, ValueError) as exc:
        raise LiquiditySweepPatternContextError("NUMERIC_FIELD_INVALID", field) from exc
    _req(math.isfinite(x), "NUMERIC_FIELD_INVALID", field)
    return x

def _gate_off() -> None:
    _req(os.environ.get(OFFICIAL_APPEND_GATE_NAME) != "1", "OFFICIAL_APPEND_GATE_ENABLED", OFFICIAL_APPEND_GATE_NAME)

def _official(repo: Path) -> dict[str, str]:
    dataset, manifest, lock = repo / OFFICIAL_DATASET, repo / OFFICIAL_MANIFEST, repo / OFFICIAL_LOCK
    _req(dataset.is_file() and not dataset.is_symlink(), "OFFICIAL_DATASET_INVALID", str(dataset))
    _req(manifest.is_file() and not manifest.is_symlink(), "OFFICIAL_MANIFEST_INVALID", str(manifest))
    _req(not lock.exists() and not lock.is_symlink(), "OFFICIAL_LOCK_PRESENT", str(lock))
    return {"dataset_sha256": _sha(dataset), "manifest_sha256": _sha(manifest)}

def _read_json(path: Path, code: str) -> dict[str, Any]:
    _req(path.is_file() and not path.is_symlink(), code, str(path))
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise LiquiditySweepPatternContextError(code, str(path)) from exc
    _req(isinstance(value, Mapping), code, str(path))
    return dict(value)

def validate_liquidity_sweep_pattern_context_policy_v1(policy: Mapping[str, Any]) -> dict[str, Any]:
    _req(isinstance(policy, Mapping), "POLICY_INVALID", "mapping required")
    _req(policy.get("schema_version") == EXPECTED_POLICY_SCHEMA_VERSION, "POLICY_SCHEMA_INVALID", str(policy.get("schema_version")))
    _req(policy.get("feature_id") == FEATURE_ID, "POLICY_FEATURE_ID_INVALID", str(policy.get("feature_id")))
    effective = _parse_utc(policy.get("policy_effective_from_utc"), "policy_effective_from_utc")
    _req(policy.get("source_capture_capability") == CLOSED_CANDLE_CAPTURE_CAPABILITY, "POLICY_SOURCE_CAPABILITY_INVALID", str(policy.get("source_capture_capability")))
    _req(policy.get("source_provider") == SOURCE_PROVIDER, "POLICY_SOURCE_PROVIDER_INVALID", str(policy.get("source_provider")))
    _req(policy.get("source_symbol") == EXPECTED_SYMBOL and policy.get("source_timeframe") == EXPECTED_TIMEFRAME, "POLICY_SOURCE_IDENTITY_INVALID", "symbol/timeframe")
    _req(int(policy.get("rolling_extreme_lookback_bars", -1)) == 48, "POLICY_LOOKBACK_INVALID", str(policy.get("rolling_extreme_lookback_bars")))
    _req(int(policy.get("atr_bars", -1)) == 14, "POLICY_ATR_INVALID", str(policy.get("atr_bars")))
    for field in ("same_bar_response_only", "symmetric_high_low_context", "sweep_is_price_action_proxy_only"):
        _req(policy.get(field) is True, "POLICY_REQUIRED_GUARD_INVALID", field)
    for field in ("future_bar_confirmation_used", "hidden_stop_orders_observed", "liquidations_observed", "primary_candidate_semantics_reused", "directional_meaning_assigned", "composite_score_assigned", "signal_semantics"):
        _req(policy.get(field) is False, "POLICY_FORBIDDEN_SEMANTIC_ENABLED", field)
    return {"policy_effective_from_utc": _utc(effective), "rolling_extreme_lookback_bars": 48, "atr_bars": 14}

def load_liquidity_sweep_pattern_context_policy_v1(repo_root: Path | str) -> tuple[dict[str, Any], str]:
    repo = Path(repo_root).resolve(); path = repo / POLICY_PATH
    policy = _read_json(path, "POLICY_FILE_INVALID")
    validate_liquidity_sweep_pattern_context_policy_v1(policy)
    return policy, _sha(path)

def _validate_descriptor(descriptor: Mapping[str, Any]) -> dict[str, Any]:
    _req(isinstance(descriptor, Mapping), "OBSERVATION_DESCRIPTOR_INVALID", "mapping required")
    _req(descriptor.get("observation_descriptor_schema_version") == "FORWARD_OUTCOME_OBSERVATION_DESCRIPTOR_V1", "OBSERVATION_DESCRIPTOR_SCHEMA_INVALID", str(descriptor.get("observation_descriptor_schema_version")))
    _req(descriptor.get("symbol") == EXPECTED_SYMBOL and descriptor.get("timeframe") == EXPECTED_TIMEFRAME, "OBSERVATION_IDENTITY_INVALID", "symbol/timeframe")
    _req(isinstance(descriptor.get("primary_candidate_detected"), bool), "PRIMARY_CANDIDATE_STATE_INVALID", str(descriptor.get("primary_candidate_detected")))
    reference = _parse_utc(descriptor.get("reference_boundary_utc"), "reference_boundary_utc")
    close = _parse_utc(descriptor.get("reference_closed_candle_utc"), "reference_closed_candle_utc")
    cutoff = _parse_utc(descriptor.get("synchronized_context_available_at_utc"), "synchronized_context_available_at_utc")
    _req(reference - close == CLOSE_EPSILON, "REFERENCE_BOUNDARY_INVALID", "1ms required")
    _req(cutoff >= reference, "CONTEXT_CUTOFF_BEFORE_REFERENCE", _utc(cutoff))
    _req(bool(str(descriptor.get("observation_id", "")).strip()), "OBSERVATION_ID_INVALID", "missing")
    return dict(descriptor)

def _read_closed_candles(path: Path) -> list[dict[str, Any]]:
    payload = path.read_bytes(); _req(payload and not payload.startswith(b"\xef\xbb\xbf"), "SOURCE_CSV_ENCODING_INVALID", str(path))
    reader = csv.DictReader(payload.decode("utf-8").splitlines())
    _req(tuple(reader.fieldnames or ()) == tuple(SOURCE_COLUMNS), "SOURCE_CSV_SCHEMA_INVALID", str(reader.fieldnames))
    rows = []; prev_open = prev_close = None
    for idx, row in enumerate(reader, start=2):
        open_time = _parse_utc(row["open_time_utc"], f"row{idx}.open")
        close_time = _parse_utc(row["close_time_utc"], f"row{idx}.close")
        _req(close_time - open_time == BAR_DURATION - CLOSE_EPSILON, "CANDLE_DURATION_INVALID", str(idx))
        if prev_open is not None:
            _req(open_time - prev_open == BAR_DURATION and close_time - prev_close == BAR_DURATION, "CANDLE_GAP_OR_DUPLICATION", str(idx))
        prev_open, prev_close = open_time, close_time
        _req(row["symbol"] == EXPECTED_SYMBOL and row["timeframe"] == EXPECTED_TIMEFRAME and row["candle_closed"] == "True", "SOURCE_ROW_IDENTITY_INVALID", str(idx))
        o,h,l,c,v = (_number(row[k], k) for k in ("open","high","low","close","volume"))
        _req(min(o,h,l,c) > 0 and v >= 0 and h >= max(o,c) and l <= min(o,c) and h >= l, "CANDLE_OHLC_INVALID", str(idx))
        rows.append({"open_time":open_time,"close_time":close_time,"open":o,"high":h,"low":l,"close":c,"volume":v})
    _req(len(rows) >= MINIMUM_REQUIRED_ROWS, "SOURCE_WARMUP_INSUFFICIENT", str(len(rows)))
    return rows

def _true_ranges(candles: Sequence[Mapping[str, Any]]) -> list[float]:
    values=[]; prev=None
    for c in candles:
        parts=[float(c["high"])-float(c["low"])]
        if prev is not None: parts += [abs(float(c["high"])-prev), abs(float(c["low"])-prev)]
        values.append(max(parts)); prev=float(c["close"])
    return values

def _metrics(candles: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    latest=candles[-1]; preceding=list(candles[-49:-1]); _req(len(preceding)==48,"SOURCE_WARMUP_INSUFFICIENT",str(len(preceding)))
    lo=min(float(c["low"]) for c in preceding); hi=max(float(c["high"]) for c in preceding); _req(0 < lo < hi,"ROLLING_EXTREMES_INVALID",f"{lo},{hi}")
    o,h,l,c,v=(float(latest[k]) for k in ("open","high","low","close","volume"))
    lower=l<lo; lower_reclaim=c>lo; upper=h>hi; upper_reject=c<hi
    atr_vals=_true_ranges(candles)[-14:]; atr=sum(atr_vals)/len(atr_vals); _req(atr>0,"ATR_INVALID",str(atr))
    median_vol=float(statistics.median(float(x["volume"]) for x in preceding))
    rng=h-l; upper_wick=h-max(o,c); lower_wick=min(o,c)-l; body=abs(c-o)
    lower_exc=max(0.0,lo-l); upper_exc=max(0.0,h-hi)
    return {
        "rolling_low_48":lo,"rolling_high_48":hi,"atr14":atr,"prior_48_median_volume":median_vol,
        "latest_open":o,"latest_high":h,"latest_low":l,"latest_close":c,"latest_volume":v,
        "lower_side_price_sweep":lower,"lower_side_same_bar_reclaim":lower_reclaim,"lower_side_sweep_reclaim_same_bar":lower and lower_reclaim,
        "upper_side_price_sweep":upper,"upper_side_same_bar_rejection":upper_reject,"upper_side_sweep_rejection_same_bar":upper and upper_reject,
        "two_sided_sweep_same_bar":lower and upper,"any_rolling_extreme_sweep":lower or upper,
        "lower_excursion_bps":lower_exc/lo*10000.0,"upper_excursion_bps":upper_exc/hi*10000.0,
        "close_from_rolling_low_bps":(c-lo)/lo*10000.0,"close_from_rolling_high_bps":(c-hi)/hi*10000.0,
        "lower_excursion_atr":lower_exc/atr,"upper_excursion_atr":upper_exc/atr,
        "upper_wick_fraction_of_range":upper_wick/rng if rng>0 else None,"lower_wick_fraction_of_range":lower_wick/rng if rng>0 else None,"body_fraction_of_range":body/rng if rng>0 else None,
        "volume_ratio_to_prior_48_median":v/median_vol if median_vol>0 else None,
    }

def build_liquidity_sweep_pattern_context_v1_component(*, observation_descriptor: Mapping[str, Any], capture_metadata: Mapping[str, Any], candles: Sequence[Mapping[str, Any]], source_csv_sha256: str, source_manifest_sha256: str, policy: Mapping[str, Any], policy_sha256: str, produced_at_utc: str) -> dict[str, Any]:
    d=_validate_descriptor(observation_descriptor); p=validate_liquidity_sweep_pattern_context_policy_v1(policy)
    _req(capture_metadata.get("capability")==CLOSED_CANDLE_CAPTURE_CAPABILITY,"SOURCE_CAPTURE_CAPABILITY_INVALID",str(capture_metadata.get("capability")))
    _req(capture_metadata.get("provider")==SOURCE_PROVIDER and capture_metadata.get("symbol")==EXPECTED_SYMBOL and capture_metadata.get("timeframe")==EXPECTED_TIMEFRAME,"SOURCE_CAPTURE_IDENTITY_INVALID","identity")
    _req(int(capture_metadata.get("network_request_count",-1))==1,"SOURCE_REQUEST_COUNT_INVALID",str(capture_metadata.get("network_request_count")))
    _req(capture_metadata.get("candidate_evaluated") is False and capture_metadata.get("candidate_detected") is False,"SOURCE_CAPTURE_CANDIDATE_STATE_INVALID","candidate")
    for name,digest in (("source_csv",source_csv_sha256),("source_manifest",source_manifest_sha256),("policy",policy_sha256)):
        _req(len(digest)==64 and all(ch in "0123456789abcdef" for ch in digest),"SHA256_INVALID",name)
    reference=_parse_utc(d["reference_boundary_utc"],"reference_boundary_utc"); close=_parse_utc(d["reference_closed_candle_utc"],"reference_closed_candle_utc")
    captured=_parse_utc(capture_metadata.get("captured_at_utc"),"captured_at_utc"); latest_meta=_parse_utc(capture_metadata.get("latest_closed_candle_utc"),"latest_closed_candle_utc")
    _req(latest_meta==close,"SOURCE_REFERENCE_CANDLE_MISMATCH",_utc(latest_meta)); _req(captured>=reference,"SOURCE_CAPTURE_BEFORE_REFERENCE",_utc(captured))
    _req(len(candles)>=49,"SOURCE_WARMUP_INSUFFICIENT",str(len(candles))); latest_close=candles[-1]["close_time"]
    if not isinstance(latest_close, datetime): latest_close=_parse_utc(latest_close,"latest_close")
    _req(latest_close==close,"SOURCE_CSV_REFERENCE_CANDLE_MISMATCH",_utc(latest_close))
    policy_effective=_parse_utc(p["policy_effective_from_utc"],"policy_effective"); available=max(captured,policy_effective); produced=_parse_utc(produced_at_utc,"produced_at_utc")
    _req(produced>=available,"PRODUCED_BEFORE_FEATURE_AVAILABLE",_utc(produced))
    payload={
        "model_semantics":"DESCRIPTIVE_LIQUIDITY_SWEEP_PRICE_ACTION_CONTEXT_ONLY",
        "reference_closed_candle_utc":d["reference_closed_candle_utc"],"reference_boundary_utc":d["reference_boundary_utc"],"context_cutoff_utc":d["synchronized_context_available_at_utc"],
        "source_capture_id":str(capture_metadata.get("capture_id","")),"source_capture_capability":CLOSED_CANDLE_CAPTURE_CAPABILITY,"source_provider":SOURCE_PROVIDER,"source_captured_at_utc":_utc(captured),
        "source_manifest_sha256":source_manifest_sha256,"policy_sha256":policy_sha256,"policy_effective_from_utc":p["policy_effective_from_utc"],"retrospective_policy_floor_applied":captured<policy_effective,"producer_generated_at_utc":_utc(produced),
        "rolling_extreme_lookback_bars":48,"atr_bars":14,**_metrics(candles),
        "same_bar_response_only":True,"future_bar_confirmation_used":False,"symmetric_high_low_context":True,"sweep_is_price_action_proxy_only":True,
        "hidden_stop_orders_observed":False,"liquidations_observed":False,"primary_candidate_semantics_reused":False,"secondary_candidate_promoted":False,"candidate_emitted":False,
        "candidate_modification_semantics":False,"primary_rule_modification_semantics":False,"future_outcomes_used":False,"directional_semantics":False,"signal_semantics":False,"composite_score_assigned":False,
        "market_data_acquired_by_producer":False,"source_recaptured_by_producer":False,
    }
    component={"feature_id":FEATURE_ID,"source_kind":SOURCE_KIND,"feature_schema_version":FEATURE_SCHEMA_VERSION,"status":"AVAILABLE","reason":None,"available_at_utc":_utc(available),"information_cutoff_utc":_utc(reference),"source_artifact_sha256":source_csv_sha256,"payload":payload}
    validate_liquidity_sweep_pattern_context_v1_component(component); return component

def _placeholder(item: Mapping[str, Any]) -> dict[str, Any]:
    fid=str(item["feature_id"]); return {"feature_id":fid,"source_kind":str(item["source_kind"]),"feature_schema_version":fid+"_PLACEHOLDER_SCHEMA_V1","status":"NOT_CONFIGURED","reason":"not configured for producer integration check","available_at_utc":None,"information_cutoff_utc":None,"source_artifact_sha256":None,"payload":None}

def validate_component_against_level_a_pack_v1(*, observation_descriptor: Mapping[str, Any], component: Mapping[str, Any]) -> dict[str, Any]:
    components={str(item["feature_id"]):_placeholder(item) for item in FEATURE_REGISTRY}; components[FEATURE_ID]=dict(component)
    pack=build_context_feature_pack_v1(observation_descriptor=observation_descriptor,components=components,pack_id="PACK_COMPATIBILITY_CHECK_ONLY")
    feature=next(x for x in pack["features"] if x["feature_id"]==FEATURE_ID)
    return {"status":feature["status"],"point_in_time_eligible":feature["point_in_time_eligible"],"eligibility_reason":feature["eligibility_reason"],"payload_sha256":feature["payload_sha256"]}

def validate_liquidity_sweep_pattern_context_v1_component(component: Mapping[str, Any]) -> dict[str, Any]:
    _req(isinstance(component,Mapping),"COMPONENT_INVALID","mapping"); _req(component.get("feature_id")==FEATURE_ID and component.get("source_kind")==SOURCE_KIND and component.get("feature_schema_version")==FEATURE_SCHEMA_VERSION and component.get("status")=="AVAILABLE","COMPONENT_IDENTITY_INVALID","identity")
    available=_parse_utc(component.get("available_at_utc"),"available_at"); info=_parse_utc(component.get("information_cutoff_utc"),"information_cutoff"); _req(info<=available,"COMPONENT_INFORMATION_AFTER_AVAILABILITY","timestamps")
    source_sha=str(component.get("source_artifact_sha256","")); _req(len(source_sha)==64 and all(ch in "0123456789abcdef" for ch in source_sha),"COMPONENT_SOURCE_SHA_INVALID",source_sha)
    payload=component.get("payload"); _req(isinstance(payload,Mapping),"COMPONENT_PAYLOAD_INVALID","payload"); _req(payload.get("model_semantics")=="DESCRIPTIVE_LIQUIDITY_SWEEP_PRICE_ACTION_CONTEXT_ONLY","PAYLOAD_SEMANTICS_INVALID","semantics")
    for field in ("same_bar_response_only","symmetric_high_low_context","sweep_is_price_action_proxy_only"):_req(payload.get(field) is True,"REQUIRED_PAYLOAD_GUARD_INVALID",field)
    for field in ("future_bar_confirmation_used","hidden_stop_orders_observed","liquidations_observed","primary_candidate_semantics_reused","secondary_candidate_promoted","candidate_emitted","candidate_modification_semantics","primary_rule_modification_semantics","future_outcomes_used","directional_semantics","signal_semantics","composite_score_assigned","market_data_acquired_by_producer","source_recaptured_by_producer"):_req(payload.get(field) is False,"FORBIDDEN_PAYLOAD_SEMANTIC_ENABLED",field)
    _req(float(payload["rolling_low_48"]) < float(payload["rolling_high_48"]),"PAYLOAD_ROLLING_EXTREMES_INVALID","extremes"); _req(float(payload["atr14"])>0,"PAYLOAD_ATR_INVALID","atr")
    return {"status":"AVAILABLE","lower_side_price_sweep":bool(payload["lower_side_price_sweep"]),"upper_side_price_sweep":bool(payload["upper_side_price_sweep"]),"two_sided_sweep_same_bar":bool(payload["two_sided_sweep_same_bar"]),"retrospective_policy_floor_applied":bool(payload["retrospective_policy_floor_applied"]),"directional_semantics":False,"signal_semantics":False}

def _write_manifest(directory: Path) -> None:
    lines=[f"{_sha(directory/name)}  {name}" for name in sorted((CHECKS_FILENAME,COMPONENT_FILENAME))]; _write_new(directory/MANIFEST_FILENAME,("\n".join(lines)+"\n").encode("utf-8"))

def _read_manifest(directory: Path) -> dict[str,str]:
    path=directory/MANIFEST_FILENAME; _req(path.is_file() and not path.is_symlink(),"PACKAGE_MANIFEST_MISSING",str(path)); lines=[x for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]; _req(len(lines)==2,"PACKAGE_MANIFEST_ENTRY_COUNT_INVALID",str(len(lines))); seen={}
    for line in lines:
        parts=line.split("  ",1); _req(len(parts)==2 and len(parts[0])==64,"PACKAGE_MANIFEST_LINE_INVALID",line); expected,name=parts; _req(name in (CHECKS_FILENAME,COMPONENT_FILENAME),"PACKAGE_MANIFEST_SCOPE_INVALID",name); candidate=directory/name; _req(candidate.is_file() and _sha(candidate)==expected,"PACKAGE_MANIFEST_HASH_MISMATCH",name); seen[name]=expected
    return seen

def validate_liquidity_sweep_pattern_context_v1_package(directory: Path | str) -> dict[str, Any]:
    root=Path(directory).resolve(); _req(root.is_dir() and not root.is_symlink(),"PACKAGE_DIRECTORY_INVALID",str(root)); manifest=_read_manifest(root); component=_read_json(root/COMPONENT_FILENAME,"PACKAGE_COMPONENT_INVALID"); checks=_read_json(root/CHECKS_FILENAME,"PACKAGE_CHECKS_INVALID"); cv=validate_liquidity_sweep_pattern_context_v1_component(component)
    _req(checks.get("package_schema_version")==PACKAGE_SCHEMA_VERSION and checks.get("capability")==CAPABILITY and checks.get("feature_id")==FEATURE_ID,"PACKAGE_IDENTITY_INVALID","identity")
    for field in ("real_network_request_executed","market_data_acquired_by_producer","source_recaptured_by_producer","git_network_request_executed","future_outcomes_used","direction_inferred","signal_generated","candidate_modified","primary_rule_modified","official_append_executed","official_dataset_changed","official_manifest_changed"):_req(checks.get(field) is False,"PACKAGE_CHECK_INVALID",field)
    return {**cv,"manifest_entries":len(manifest),"point_in_time_eligible_under_pack_policy":bool(checks["point_in_time_eligible_under_pack_policy"]),"real_network_request_executed":False,"official_append_executed":False}

def prepare_liquidity_sweep_pattern_context_v1_package(*, repo_root: Path | str, observation_descriptor_json: Path | str, closed_candle_capture_directory: Path | str, output_directory: Path | str, produced_at_utc: str, authorization: str | None = None) -> dict[str, Any]:
    _req(authorization==PACKAGE_AUTHORIZATION,"PACKAGE_AUTHORIZATION_REQUIRED","authorization"); _gate_off(); repo=Path(repo_root).resolve(); descriptor_path=Path(observation_descriptor_json).resolve(); source_dir=Path(closed_candle_capture_directory).resolve(); output=Path(output_directory).resolve()
    _req((repo/".git").is_dir(),"REPOSITORY_ROOT_INVALID",str(repo)); _req(not _inside(output,repo),"OUTPUT_INSIDE_REPOSITORY_PROHIBITED",str(output)); _req(output.parent.is_dir() and not output.exists(),"OUTPUT_INVALID",str(output)); _req(not _inside(descriptor_path,repo),"DESCRIPTOR_INSIDE_REPOSITORY_PROHIBITED",str(descriptor_path)); _req(not _inside(source_dir,repo) and source_dir.is_dir(),"SOURCE_CAPTURE_INSIDE_REPOSITORY_PROHIBITED",str(source_dir))
    official_before=_official(repo); descriptor=_read_json(descriptor_path,"OBSERVATION_DESCRIPTOR_FILE_INVALID"); _validate_descriptor(descriptor); source_validation=validate_closed_candle_capture(source_dir); _req(int(source_validation["closed_candle_rows"])>=49,"SOURCE_VALIDATION_ROWS_INVALID",str(source_validation["closed_candle_rows"]))
    source_csv=source_dir/SOURCE_FILENAME; metadata_path=source_dir/SOURCE_METADATA_FILENAME; source_manifest=source_dir/MANIFEST_FILENAME; metadata=_read_json(metadata_path,"SOURCE_METADATA_INVALID"); candles=_read_closed_candles(source_csv); csv_sha=_sha(source_csv); _req(metadata.get("source_artifact_sha256")==csv_sha,"SOURCE_METADATA_HASH_INVALID",str(metadata.get("source_artifact_sha256")))
    policy,policy_sha=load_liquidity_sweep_pattern_context_policy_v1(repo); component=build_liquidity_sweep_pattern_context_v1_component(observation_descriptor=descriptor,capture_metadata=metadata,candles=candles,source_csv_sha256=csv_sha,source_manifest_sha256=_sha(source_manifest),policy=policy,policy_sha256=policy_sha,produced_at_utc=produced_at_utc); compatibility=validate_component_against_level_a_pack_v1(observation_descriptor=descriptor,component=component)
    _req(_official(repo)==official_before,"OFFICIAL_ARTIFACT_CHANGED","before output"); _gate_off(); temp=output.parent/f".{output.name}.tmp-{uuid.uuid4().hex}"; _req(not temp.exists(),"TEMPORARY_OUTPUT_COLLISION",str(temp))
    try:
        temp.mkdir(); _write_new(temp/COMPONENT_FILENAME,_json_bytes(component)); checks={"package_schema_version":PACKAGE_SCHEMA_VERSION,"capability":CAPABILITY,"feature_id":FEATURE_ID,"observation_descriptor_sha256":_sha(descriptor_path),"source_capture_id":metadata["capture_id"],"source_csv_sha256":csv_sha,"source_capture_manifest_sha256":_sha(source_manifest),"policy_resource_sha256":policy_sha,"produced_at_utc":_utc(_parse_utc(produced_at_utc,"produced_at_utc")),"component_available_at_utc":component["available_at_utc"],"component_information_cutoff_utc":component["information_cutoff_utc"],"point_in_time_eligible_under_pack_policy":compatibility["point_in_time_eligible"],"pack_eligibility_reason":compatibility["eligibility_reason"],"source_capture_was_preexisting":True,"source_capture_validated_locally":True,"real_network_request_executed":False,"market_data_acquired_by_producer":False,"source_recaptured_by_producer":False,"git_network_request_executed":False,"future_outcomes_used":False,"direction_inferred":False,"signal_generated":False,"candidate_modified":False,"primary_rule_modified":False,"official_append_executed":False,"official_dataset_changed":False,"official_manifest_changed":False,**{f:False for f in FALSE_PERMISSION_FIELDS}}; _write_new(temp/CHECKS_FILENAME,_json_bytes(checks)); _write_manifest(temp); validate_liquidity_sweep_pattern_context_v1_package(temp); temp.rename(output)
    except Exception:
        if temp.exists(): shutil.rmtree(temp,ignore_errors=True)
        if output.exists(): shutil.rmtree(output,ignore_errors=True)
        raise
    _req(_official(repo)==official_before,"OFFICIAL_ARTIFACT_CHANGED","after output"); _gate_off(); validation=validate_liquidity_sweep_pattern_context_v1_package(output)
    return {"capability":CAPABILITY,"feature_id":FEATURE_ID,"output_directory":str(output),"component_status":validation["status"],"point_in_time_eligible_under_pack_policy":validation["point_in_time_eligible_under_pack_policy"],"real_network_request_executed":False,"market_data_acquired_by_producer":False,"source_recaptured_by_producer":False,"git_network_request_executed":False,"official_append_executed":False,**{f:False for f in FALSE_PERMISSION_FIELDS}}

__all__ = ["ATR_BARS","CAPABILITY","FEATURE_ID","FEATURE_SCHEMA_VERSION","IMPLEMENTATION_OR_REPAIR_ATTEMPT","MAX_IMPLEMENTATION_OR_REPAIR_ATTEMPTS","PACKAGE_AUTHORIZATION","POLICY_PATH","ROLLING_EXTREME_LOOKBACK_BARS","SOURCE_KIND","LiquiditySweepPatternContextError","build_liquidity_sweep_pattern_context_v1_component","load_liquidity_sweep_pattern_context_policy_v1","prepare_liquidity_sweep_pattern_context_v1_package","validate_component_against_level_a_pack_v1","validate_liquidity_sweep_pattern_context_policy_v1","validate_liquidity_sweep_pattern_context_v1_component","validate_liquidity_sweep_pattern_context_v1_package"]
