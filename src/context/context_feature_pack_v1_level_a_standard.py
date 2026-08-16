from __future__ import annotations

import hashlib
import json
import math
import os
import shutil
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Mapping

CAPABILITY = "CONTEXT_FEATURE_PACK_V1_LEVEL_A_STANDARD"
PACK_SCHEMA_VERSION = "CONTEXT_FEATURE_PACK_V1_LEVEL_A_STANDARD_SCHEMA_V1"
PACKAGE_SCHEMA_VERSION = "CONTEXT_FEATURE_PACK_V1_LEVEL_A_STANDARD_PACKAGE_V1"

EXPECTED_OBSERVATION_DESCRIPTOR_SCHEMA = (
    "FORWARD_OUTCOME_OBSERVATION_DESCRIPTOR_V1"
)
EXPECTED_SYMBOL = "BTCUSDT"
EXPECTED_TIMEFRAME = "15m"
BAR_DURATION = timedelta(minutes=15)

PACKAGE_AUTHORIZATION = "PREPARE_CONTEXT_FEATURE_PACK_V1_LEVEL_A_STANDARD"

MAX_IMPLEMENTATION_OR_REPAIR_ATTEMPTS = 10
IMPLEMENTATION_OR_REPAIR_ATTEMPT = 1

OFFICIAL_APPEND_GATE_NAME = "TRADING_AI_OFFICIAL_LONG_EVIDENCE_APPEND_ALLOWED"
OFFICIAL_DATASET = Path("data/forward/long_forward_observation_dataset_v1.csv")
OFFICIAL_MANIFEST = Path(
    "data/forward/long_forward_observation_dataset_v1.manifest.csv"
)
OFFICIAL_LOCK = Path("data/forward/long_forward_observation_dataset_v1.lock")

PACK_FILENAME = "context_feature_pack.json"
CHECKS_FILENAME = "pack_checks.json"
MANIFEST_FILENAME = "manifest.sha256"

FEATURE_REGISTRY = (
    {
        "feature_id": "BTC_CYCLE_HALVING_CONTEXT_V1",
        "family": "CYCLE",
        "source_kind": "DETERMINISTIC",
        "level": "A",
    },
    {
        "feature_id": "EVENT_RISK_CALENDAR_CONTEXT_V1",
        "family": "EVENT_RISK",
        "source_kind": "DETERMINISTIC",
        "level": "A",
    },
    {
        "feature_id": "EXTERNAL_CYCLE_REGRESSION_BASELINE_V1",
        "family": "EXTERNAL_BASELINE",
        "source_kind": "EXTERNAL_MODEL",
        "level": "A",
    },
    {
        "feature_id": "LIQUIDITY_SWEEP_PATTERN_CONTEXT_V1",
        "family": "LIQUIDITY_PATTERN",
        "source_kind": "OBSERVED_MARKET",
        "level": "A",
    },
    {
        "feature_id": "EXTERNAL_THESIS_MODEL_CARD_V1",
        "family": "EXTERNAL_THESIS",
        "source_kind": "EXTERNAL_MODEL",
        "level": "A",
    },
    {
        "feature_id": "ANALOG_ENGINE_CONTEXT_V1",
        "family": "ANALOG",
        "source_kind": "MODEL_DERIVED",
        "level": "A",
    },
    {
        "feature_id": "SYNCHRONIZED_MICROSTRUCTURE_CONTEXT_V1",
        "family": "MICROSTRUCTURE",
        "source_kind": "OBSERVED_MARKET",
        "level": "A",
    },
    {
        "feature_id": "ONCHAIN_CONTEXT_INTERFACE_V1",
        "family": "ONCHAIN",
        "source_kind": "FUTURE_INTERFACE",
        "level": "A",
    },
)

FEATURE_IDS = tuple(item["feature_id"] for item in FEATURE_REGISTRY)
FEATURE_REGISTRY_BY_ID = {
    item["feature_id"]: dict(item) for item in FEATURE_REGISTRY
}
ALLOWED_COMPONENT_STATUSES = (
    "AVAILABLE",
    "UNAVAILABLE",
    "NOT_CONFIGURED",
)

FALSE_PERMISSION_FIELDS = (
    "candidate_modification_allowed",
    "primary_rule_modification_allowed",
    "signal_generation_enabled",
    "live_alerts_allowed",
    "paper_trade_execution_allowed",
    "real_capital_allowed",
    "market_execution_allowed",
    "exchange_execution_allowed",
    "official_dataset_write_allowed",
    "official_append_allowed",
    "automation_allowed",
    "execution_allowed",
)

FORBIDDEN_PACK_KEYS = (
    "composite_score",
    "direction",
    "trade_action",
    "entry_price",
    "stop_price",
    "target_price",
)


class ContextFeaturePackError(RuntimeError):
    def __init__(self, code: str, message: str) -> None:
        self.code = code
        super().__init__(message)


def _req(ok: bool, code: str, message: str) -> None:
    if not ok:
        raise ContextFeaturePackError(code, message)


def _parse_utc(value: Any, field: str) -> datetime:
    text = str(value).strip().replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError as exc:
        raise ContextFeaturePackError("TIMESTAMP_INVALID", field) from exc
    _req(
        parsed.tzinfo is not None,
        "TIMESTAMP_TIMEZONE_REQUIRED",
        field,
    )
    return parsed.astimezone(timezone.utc)


def _utc(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat()


def _ceil_15m(value: datetime) -> datetime:
    current = value.astimezone(timezone.utc)
    floor_minute = (current.minute // 15) * 15
    floor = current.replace(
        minute=floor_minute,
        second=0,
        microsecond=0,
    )
    return floor if current == floor else floor + BAR_DURATION


def _json_bytes(value: Any) -> bytes:
    return (
        json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
            allow_nan=False,
        )
        + "\n"
    ).encode("utf-8")


def _canonical_sha256(value: Any) -> str:
    return hashlib.sha256(_json_bytes(value)).hexdigest()


def _sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _inside(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def _write_new(path: Path, payload: bytes) -> None:
    with path.open("xb") as handle:
        handle.write(payload)
        handle.flush()
        os.fsync(handle.fileno())


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


def _validate_observation_descriptor(
    descriptor: Mapping[str, Any],
) -> dict[str, Any]:
    _req(
        isinstance(descriptor, Mapping),
        "OBSERVATION_DESCRIPTOR_INVALID",
        "mapping required",
    )
    _req(
        descriptor.get("observation_descriptor_schema_version")
        == EXPECTED_OBSERVATION_DESCRIPTOR_SCHEMA,
        "OBSERVATION_DESCRIPTOR_SCHEMA_INVALID",
        str(descriptor.get("observation_descriptor_schema_version")),
    )
    _req(
        descriptor.get("symbol") == EXPECTED_SYMBOL,
        "OBSERVATION_SYMBOL_INVALID",
        str(descriptor.get("symbol")),
    )
    _req(
        descriptor.get("timeframe") == EXPECTED_TIMEFRAME,
        "OBSERVATION_TIMEFRAME_INVALID",
        str(descriptor.get("timeframe")),
    )
    reference_boundary = _parse_utc(
        descriptor.get("reference_boundary_utc"),
        "reference_boundary_utc",
    )
    context_cutoff = _parse_utc(
        descriptor.get("synchronized_context_available_at_utc"),
        "synchronized_context_available_at_utc",
    )
    _req(
        context_cutoff >= reference_boundary,
        "CONTEXT_CUTOFF_BEFORE_REFERENCE",
        _utc(context_cutoff),
    )
    _req(
        isinstance(descriptor.get("primary_candidate_detected"), bool),
        "PRIMARY_CANDIDATE_STATE_INVALID",
        str(descriptor.get("primary_candidate_detected")),
    )
    observation_id = str(descriptor.get("observation_id", "")).strip()
    _req(
        bool(observation_id),
        "OBSERVATION_ID_INVALID",
        observation_id,
    )
    return dict(descriptor)


def _is_sha256(value: Any) -> bool:
    text = str(value or "")
    return (
        len(text) == 64
        and all(char in "0123456789abcdef" for char in text)
    )


def _normalize_component(
    component: Mapping[str, Any],
    *,
    context_cutoff: datetime,
) -> dict[str, Any]:
    _req(
        isinstance(component, Mapping),
        "COMPONENT_INVALID",
        "mapping required",
    )

    feature_id = str(component.get("feature_id", ""))
    _req(
        feature_id in FEATURE_REGISTRY_BY_ID,
        "FEATURE_ID_INVALID",
        feature_id,
    )
    registry = FEATURE_REGISTRY_BY_ID[feature_id]

    _req(
        component.get("source_kind") == registry["source_kind"],
        "FEATURE_SOURCE_KIND_INVALID",
        feature_id,
    )
    _req(
        str(component.get("feature_schema_version", "")).strip() != "",
        "FEATURE_SCHEMA_VERSION_INVALID",
        feature_id,
    )

    status = str(component.get("status", ""))
    _req(
        status in ALLOWED_COMPONENT_STATUSES,
        "FEATURE_STATUS_INVALID",
        f"{feature_id}:{status}",
    )

    reason = str(component.get("reason", "")).strip()
    payload = component.get("payload")
    source_sha = component.get("source_artifact_sha256")
    available_at_raw = component.get("available_at_utc")
    information_cutoff_raw = component.get("information_cutoff_utc")

    if status == "AVAILABLE":
        _req(
            isinstance(payload, Mapping),
            "AVAILABLE_FEATURE_PAYLOAD_INVALID",
            feature_id,
        )
        _req(
            _is_sha256(source_sha),
            "AVAILABLE_FEATURE_SOURCE_SHA256_INVALID",
            feature_id,
        )
        available_at = _parse_utc(
            available_at_raw,
            f"{feature_id}.available_at_utc",
        )
        information_cutoff = _parse_utc(
            information_cutoff_raw,
            f"{feature_id}.information_cutoff_utc",
        )
        _req(
            information_cutoff <= available_at,
            "FEATURE_INFORMATION_AFTER_AVAILABILITY",
            feature_id,
        )
        availability_ok = available_at <= context_cutoff
        information_ok = information_cutoff <= context_cutoff
        eligible = availability_ok and information_ok
        if eligible:
            eligibility_reason = "POINT_IN_TIME_ELIGIBLE"
        elif not availability_ok:
            eligibility_reason = "AVAILABLE_AFTER_CONTEXT_CUTOFF"
        else:
            eligibility_reason = "INFORMATION_AFTER_CONTEXT_CUTOFF"
    else:
        _req(
            payload is None,
            "UNAVAILABLE_FEATURE_PAYLOAD_PRESENT",
            feature_id,
        )
        _req(
            source_sha is None,
            "UNAVAILABLE_FEATURE_SOURCE_SHA_PRESENT",
            feature_id,
        )
        _req(
            available_at_raw is None,
            "UNAVAILABLE_FEATURE_AVAILABLE_AT_PRESENT",
            feature_id,
        )
        _req(
            information_cutoff_raw is None,
            "UNAVAILABLE_FEATURE_INFORMATION_CUTOFF_PRESENT",
            feature_id,
        )
        _req(
            bool(reason),
            "UNAVAILABLE_FEATURE_REASON_REQUIRED",
            feature_id,
        )
        available_at = None
        information_cutoff = None
        eligible = False
        eligibility_reason = status

    normalized = {
        "feature_id": feature_id,
        "family": registry["family"],
        "level": registry["level"],
        "source_kind": registry["source_kind"],
        "feature_schema_version": str(
            component["feature_schema_version"]
        ),
        "status": status,
        "reason": reason or None,
        "available_at_utc": (
            _utc(available_at) if available_at is not None else None
        ),
        "information_cutoff_utc": (
            _utc(information_cutoff)
            if information_cutoff is not None
            else None
        ),
        "source_artifact_sha256": (
            str(source_sha) if source_sha is not None else None
        ),
        "payload": dict(payload) if isinstance(payload, Mapping) else None,
        "payload_sha256": (
            _canonical_sha256(dict(payload))
            if isinstance(payload, Mapping)
            else None
        ),
        "point_in_time_eligible": eligible,
        "eligibility_reason": eligibility_reason,
        "context_only_no_signal_semantics": True,
    }
    return normalized


def build_context_feature_pack_v1(
    *,
    observation_descriptor: Mapping[str, Any],
    components: Mapping[str, Mapping[str, Any]],
    pack_id: str | None = None,
) -> dict[str, Any]:
    descriptor = _validate_observation_descriptor(
        observation_descriptor
    )
    _req(
        isinstance(components, Mapping),
        "COMPONENTS_INVALID",
        "mapping required",
    )

    component_keys = tuple(components.keys())
    _req(
        set(component_keys) == set(FEATURE_IDS),
        "FEATURE_REGISTRY_SCOPE_INVALID",
        str(sorted(component_keys)),
    )

    reference_boundary = _parse_utc(
        descriptor["reference_boundary_utc"],
        "reference_boundary_utc",
    )
    context_cutoff = _parse_utc(
        descriptor["synchronized_context_available_at_utc"],
        "synchronized_context_available_at_utc",
    )
    context_anchor = _ceil_15m(context_cutoff)

    normalized_features = []
    for feature_id in FEATURE_IDS:
        component = components[feature_id]
        _req(
            component.get("feature_id") == feature_id,
            "FEATURE_KEY_ID_MISMATCH",
            feature_id,
        )
        normalized_features.append(
            _normalize_component(
                component,
                context_cutoff=context_cutoff,
            )
        )

    status_counts = {
        status: sum(
            1
            for item in normalized_features
            if item["status"] == status
        )
        for status in ALLOWED_COMPONENT_STATUSES
    }
    eligible_count = sum(
        1
        for item in normalized_features
        if item["point_in_time_eligible"]
    )
    late_count = sum(
        1
        for item in normalized_features
        if (
            item["status"] == "AVAILABLE"
            and not item["point_in_time_eligible"]
        )
    )

    pack = {
        "pack_schema_version": PACK_SCHEMA_VERSION,
        "capability": CAPABILITY,
        "pack_id": (
            str(pack_id)
            if pack_id is not None
            else "CTXP_" + uuid.uuid4().hex[:24].upper()
        ),
        "observation_id": descriptor["observation_id"],
        "symbol": EXPECTED_SYMBOL,
        "timeframe": EXPECTED_TIMEFRAME,
        "reference_boundary_utc": _utc(reference_boundary),
        "context_cutoff_utc": _utc(context_cutoff),
        "context_anchor_open_utc": _utc(context_anchor),
        "primary_candidate_detected": bool(
            descriptor["primary_candidate_detected"]
        ),
        "primary_candidate_state_preserved": True,
        "primary_rule_modified": False,
        "context_only": True,
        "historical_reconstruction_used": False,
        "feature_registry_version": "LEVEL_A_STANDARD_V1",
        "feature_registry_order": list(FEATURE_IDS),
        "feature_count": len(normalized_features),
        "available_feature_count": status_counts["AVAILABLE"],
        "unavailable_feature_count": status_counts["UNAVAILABLE"],
        "not_configured_feature_count": status_counts["NOT_CONFIGURED"],
        "point_in_time_eligible_feature_count": eligible_count,
        "available_but_ineligible_feature_count": late_count,
        "features": normalized_features,
        "composite_scoring_performed": False,
        "direction_inferred": False,
        "trade_action_inferred": False,
        **{field: False for field in FALSE_PERMISSION_FIELDS},
    }

    for key in FORBIDDEN_PACK_KEYS:
        _req(
            key not in pack,
            "FORBIDDEN_PACK_KEY_PRESENT",
            key,
        )

    validate_context_feature_pack_v1(pack)
    return pack


def validate_context_feature_pack_v1(
    pack: Mapping[str, Any],
) -> dict[str, Any]:
    _req(
        isinstance(pack, Mapping),
        "PACK_INVALID",
        "mapping required",
    )
    _req(
        pack.get("pack_schema_version") == PACK_SCHEMA_VERSION,
        "PACK_SCHEMA_INVALID",
        str(pack.get("pack_schema_version")),
    )
    _req(
        pack.get("capability") == CAPABILITY,
        "PACK_CAPABILITY_INVALID",
        str(pack.get("capability")),
    )
    _req(
        pack.get("symbol") == EXPECTED_SYMBOL
        and pack.get("timeframe") == EXPECTED_TIMEFRAME,
        "PACK_IDENTITY_INVALID",
        "symbol/timeframe",
    )
    _req(
        tuple(pack.get("feature_registry_order", ())) == FEATURE_IDS,
        "PACK_FEATURE_ORDER_INVALID",
        "registry order",
    )
    features = pack.get("features")
    _req(
        isinstance(features, list)
        and len(features) == len(FEATURE_IDS),
        "PACK_FEATURE_COUNT_INVALID",
        str(len(features) if isinstance(features, list) else None),
    )
    _req(
        tuple(item.get("feature_id") for item in features)
        == FEATURE_IDS,
        "PACK_FEATURE_IDS_INVALID",
        "feature ids",
    )

    context_cutoff = _parse_utc(
        pack["context_cutoff_utc"],
        "context_cutoff_utc",
    )
    context_anchor = _parse_utc(
        pack["context_anchor_open_utc"],
        "context_anchor_open_utc",
    )
    _req(
        context_anchor == _ceil_15m(context_cutoff),
        "PACK_CONTEXT_ANCHOR_INVALID",
        _utc(context_anchor),
    )

    available = 0
    unavailable = 0
    not_configured = 0
    eligible = 0
    late = 0

    for item in features:
        feature_id = item["feature_id"]
        registry = FEATURE_REGISTRY_BY_ID[feature_id]
        _req(
            item["family"] == registry["family"]
            and item["level"] == registry["level"]
            and item["source_kind"] == registry["source_kind"],
            "PACK_FEATURE_REGISTRY_MISMATCH",
            feature_id,
        )
        status = item["status"]
        _req(
            status in ALLOWED_COMPONENT_STATUSES,
            "PACK_FEATURE_STATUS_INVALID",
            feature_id,
        )
        _req(
            item["context_only_no_signal_semantics"] is True,
            "PACK_FEATURE_CONTEXT_SEMANTICS_INVALID",
            feature_id,
        )

        if status == "AVAILABLE":
            available += 1
            payload = item["payload"]
            _req(
                isinstance(payload, Mapping),
                "PACK_AVAILABLE_PAYLOAD_INVALID",
                feature_id,
            )
            _req(
                item["payload_sha256"]
                == _canonical_sha256(dict(payload)),
                "PACK_PAYLOAD_HASH_INVALID",
                feature_id,
            )
            _req(
                _is_sha256(item["source_artifact_sha256"]),
                "PACK_SOURCE_HASH_INVALID",
                feature_id,
            )
            available_at = _parse_utc(
                item["available_at_utc"],
                f"{feature_id}.available_at_utc",
            )
            information_cutoff = _parse_utc(
                item["information_cutoff_utc"],
                f"{feature_id}.information_cutoff_utc",
            )
            expected_eligible = (
                available_at <= context_cutoff
                and information_cutoff <= context_cutoff
            )
            _req(
                item["point_in_time_eligible"]
                is expected_eligible,
                "PACK_POINT_IN_TIME_ELIGIBILITY_INVALID",
                feature_id,
            )
            if expected_eligible:
                eligible += 1
            else:
                late += 1
        elif status == "UNAVAILABLE":
            unavailable += 1
            _req(
                item["point_in_time_eligible"] is False,
                "PACK_UNAVAILABLE_ELIGIBILITY_INVALID",
                feature_id,
            )
        else:
            not_configured += 1
            _req(
                item["point_in_time_eligible"] is False,
                "PACK_NOT_CONFIGURED_ELIGIBILITY_INVALID",
                feature_id,
            )

    _req(
        int(pack["feature_count"]) == len(FEATURE_IDS),
        "PACK_FEATURE_COUNT_SUMMARY_INVALID",
        "feature_count",
    )
    _req(
        int(pack["available_feature_count"]) == available,
        "PACK_AVAILABLE_COUNT_INVALID",
        "available",
    )
    _req(
        int(pack["unavailable_feature_count"]) == unavailable,
        "PACK_UNAVAILABLE_COUNT_INVALID",
        "unavailable",
    )
    _req(
        int(pack["not_configured_feature_count"]) == not_configured,
        "PACK_NOT_CONFIGURED_COUNT_INVALID",
        "not_configured",
    )
    _req(
        int(pack["point_in_time_eligible_feature_count"]) == eligible,
        "PACK_ELIGIBLE_COUNT_INVALID",
        "eligible",
    )
    _req(
        int(pack["available_but_ineligible_feature_count"]) == late,
        "PACK_LATE_COUNT_INVALID",
        "late",
    )

    _req(
        pack["primary_candidate_state_preserved"] is True
        and pack["primary_rule_modified"] is False,
        "PACK_PRIMARY_RULE_STATE_INVALID",
        "primary state",
    )
    _req(
        pack["context_only"] is True
        and pack["historical_reconstruction_used"] is False,
        "PACK_CONTEXT_ONLY_STATE_INVALID",
        "context only",
    )
    _req(
        pack["composite_scoring_performed"] is False
        and pack["direction_inferred"] is False
        and pack["trade_action_inferred"] is False,
        "PACK_INFERENCE_STATE_INVALID",
        "inference",
    )
    for field in FALSE_PERMISSION_FIELDS:
        _req(
            pack[field] is False,
            "PACK_PERMISSION_INVALID",
            field,
        )
    for key in FORBIDDEN_PACK_KEYS:
        _req(
            key not in pack,
            "FORBIDDEN_PACK_KEY_PRESENT",
            key,
        )

    return {
        "feature_count": len(features),
        "available_feature_count": available,
        "point_in_time_eligible_feature_count": eligible,
        "available_but_ineligible_feature_count": late,
        "context_anchor_open_utc": pack["context_anchor_open_utc"],
        "primary_candidate_detected": bool(
            pack["primary_candidate_detected"]
        ),
    }


def _read_json_mapping(path: Path, code: str) -> dict[str, Any]:
    _req(
        path.is_file() and not path.is_symlink(),
        code,
        str(path),
    )
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise ContextFeaturePackError(code, str(path)) from exc
    _req(
        isinstance(value, Mapping),
        code,
        str(path),
    )
    return dict(value)


def _write_manifest(directory: Path) -> None:
    names = (CHECKS_FILENAME, PACK_FILENAME)
    lines = [
        f"{_sha(directory / name)}  {name}"
        for name in sorted(names)
    ]
    _write_new(
        directory / MANIFEST_FILENAME,
        ("\n".join(lines) + "\n").encode("utf-8"),
    )


def _read_manifest(directory: Path) -> dict[str, str]:
    path = directory / MANIFEST_FILENAME
    _req(
        path.is_file() and not path.is_symlink(),
        "PACKAGE_MANIFEST_MISSING",
        str(path),
    )
    lines = [
        line
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    _req(
        len(lines) == 2,
        "PACKAGE_MANIFEST_ENTRY_COUNT_INVALID",
        str(len(lines)),
    )
    seen: dict[str, str] = {}
    for line in lines:
        parts = line.split("  ", 1)
        _req(
            len(parts) == 2 and len(parts[0]) == 64,
            "PACKAGE_MANIFEST_LINE_INVALID",
            line,
        )
        expected, name = parts
        _req(
            name in (CHECKS_FILENAME, PACK_FILENAME),
            "PACKAGE_MANIFEST_SCOPE_INVALID",
            name,
        )
        file_path = directory / name
        _req(
            file_path.is_file() and not file_path.is_symlink(),
            "PACKAGE_MANIFEST_FILE_MISSING",
            name,
        )
        _req(
            _sha(file_path) == expected,
            "PACKAGE_MANIFEST_HASH_MISMATCH",
            name,
        )
        seen[name] = expected
    _req(
        set(seen) == {CHECKS_FILENAME, PACK_FILENAME},
        "PACKAGE_MANIFEST_SCOPE_INVALID",
        str(sorted(seen)),
    )
    return seen


def validate_context_feature_pack_v1_package(
    directory: Path | str,
) -> dict[str, Any]:
    root = Path(directory).resolve()
    _req(
        root.is_dir() and not root.is_symlink(),
        "PACKAGE_DIRECTORY_INVALID",
        str(root),
    )
    manifest = _read_manifest(root)
    pack = _read_json_mapping(
        root / PACK_FILENAME,
        "PACKAGE_PACK_INVALID",
    )
    checks = _read_json_mapping(
        root / CHECKS_FILENAME,
        "PACKAGE_CHECKS_INVALID",
    )
    pack_validation = validate_context_feature_pack_v1(pack)

    _req(
        checks.get("package_schema_version")
        == PACKAGE_SCHEMA_VERSION,
        "PACKAGE_SCHEMA_INVALID",
        str(checks.get("package_schema_version")),
    )
    _req(
        checks.get("capability") == CAPABILITY,
        "PACKAGE_CAPABILITY_INVALID",
        str(checks.get("capability")),
    )
    _req(
        checks.get("real_network_request_executed") is False
        and checks.get("git_network_request_executed") is False,
        "PACKAGE_NETWORK_STATE_INVALID",
        "network",
    )
    _req(
        checks.get("official_append_executed") is False
        and checks.get("official_dataset_changed") is False
        and checks.get("official_manifest_changed") is False,
        "PACKAGE_OFFICIAL_STATE_INVALID",
        "official",
    )
    _req(
        checks.get("component_source_network_performed_by_pack") is False,
        "PACKAGE_COMPONENT_NETWORK_INVALID",
        "component network",
    )

    return {
        **pack_validation,
        "manifest_entries": len(manifest),
        "real_network_request_executed": False,
        "official_append_executed": False,
    }


def prepare_context_feature_pack_v1_package(
    *,
    repo_root: Path | str,
    observation_descriptor_json: Path | str,
    components_json: Path | str,
    output_directory: Path | str,
    authorization: str | None = None,
    pack_id: str | None = None,
) -> dict[str, Any]:
    _req(
        authorization == PACKAGE_AUTHORIZATION,
        "PACKAGE_AUTHORIZATION_REQUIRED",
        "authorization",
    )
    _gate_off()

    repo = Path(repo_root).resolve()
    descriptor_path = Path(observation_descriptor_json).resolve()
    components_path = Path(components_json).resolve()
    output = Path(output_directory).resolve()

    _req(
        (repo / ".git").is_dir(),
        "REPOSITORY_ROOT_INVALID",
        str(repo),
    )
    _req(
        not _inside(output, repo),
        "OUTPUT_INSIDE_REPOSITORY_PROHIBITED",
        str(output),
    )
    _req(
        output.parent.is_dir() and not output.parent.is_symlink(),
        "OUTPUT_PARENT_INVALID",
        str(output.parent),
    )
    _req(
        not output.exists() and not output.is_symlink(),
        "OUTPUT_ALREADY_EXISTS",
        str(output),
    )
    _req(
        not _inside(descriptor_path, repo),
        "DESCRIPTOR_INSIDE_REPOSITORY_PROHIBITED",
        str(descriptor_path),
    )
    _req(
        not _inside(components_path, repo),
        "COMPONENTS_INSIDE_REPOSITORY_PROHIBITED",
        str(components_path),
    )

    official_before = _official(repo)
    descriptor = _read_json_mapping(
        descriptor_path,
        "OBSERVATION_DESCRIPTOR_FILE_INVALID",
    )
    components = _read_json_mapping(
        components_path,
        "COMPONENTS_FILE_INVALID",
    )

    pack = build_context_feature_pack_v1(
        observation_descriptor=descriptor,
        components=components,
        pack_id=pack_id,
    )

    _req(
        _official(repo) == official_before,
        "OFFICIAL_ARTIFACT_CHANGED",
        "before output",
    )
    _gate_off()

    temp = output.parent / f".{output.name}.tmp-{uuid.uuid4().hex}"
    _req(
        not temp.exists(),
        "TEMPORARY_OUTPUT_COLLISION",
        str(temp),
    )
    try:
        temp.mkdir()
        _write_new(temp / PACK_FILENAME, _json_bytes(pack))
        checks = {
            "package_schema_version": PACKAGE_SCHEMA_VERSION,
            "capability": CAPABILITY,
            "observation_descriptor_sha256": _sha(descriptor_path),
            "components_source_sha256": _sha(components_path),
            "feature_registry_order": list(FEATURE_IDS),
            "feature_count": len(FEATURE_IDS),
            "real_network_request_executed": False,
            "git_network_request_executed": False,
            "component_source_network_performed_by_pack": False,
            "official_append_executed": False,
            "official_dataset_changed": False,
            "official_manifest_changed": False,
            "primary_candidate_modified": False,
            "primary_rule_modified": False,
            "composite_scoring_performed": False,
            "direction_inferred": False,
            "trade_action_inferred": False,
            "manual_confirmation_required": True,
            **{field: False for field in FALSE_PERMISSION_FIELDS},
        }
        _write_new(temp / CHECKS_FILENAME, _json_bytes(checks))
        _write_manifest(temp)
        validate_context_feature_pack_v1_package(temp)
        temp.rename(output)
    except Exception:
        if temp.exists():
            shutil.rmtree(temp, ignore_errors=True)
        if output.exists():
            shutil.rmtree(output, ignore_errors=True)
        raise

    _req(
        _official(repo) == official_before,
        "OFFICIAL_ARTIFACT_CHANGED",
        "after output",
    )
    _gate_off()

    validation = validate_context_feature_pack_v1_package(output)
    return {
        "capability": CAPABILITY,
        "output_directory": str(output),
        "pack_id": pack["pack_id"],
        "observation_id": pack["observation_id"],
        "feature_count": validation["feature_count"],
        "available_feature_count": validation["available_feature_count"],
        "point_in_time_eligible_feature_count": validation[
            "point_in_time_eligible_feature_count"
        ],
        "context_anchor_open_utc": validation[
            "context_anchor_open_utc"
        ],
        "primary_candidate_detected": validation[
            "primary_candidate_detected"
        ],
        "real_network_request_executed": False,
        "git_network_request_executed": False,
        "official_append_executed": False,
        **{field: False for field in FALSE_PERMISSION_FIELDS},
    }


__all__ = [
    "ALLOWED_COMPONENT_STATUSES",
    "CAPABILITY",
    "FEATURE_IDS",
    "FEATURE_REGISTRY",
    "IMPLEMENTATION_OR_REPAIR_ATTEMPT",
    "MAX_IMPLEMENTATION_OR_REPAIR_ATTEMPTS",
    "PACKAGE_AUTHORIZATION",
    "PACK_SCHEMA_VERSION",
    "ContextFeaturePackError",
    "build_context_feature_pack_v1",
    "prepare_context_feature_pack_v1_package",
    "validate_context_feature_pack_v1",
    "validate_context_feature_pack_v1_package",
]
