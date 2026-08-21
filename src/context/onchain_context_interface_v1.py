from __future__ import annotations

import hashlib
import json
import math
import os
import re
import shutil
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from src.context.context_feature_pack_v1_level_a_standard import (
    FEATURE_REGISTRY,
    build_context_feature_pack_v1,
)

CAPABILITY = "ONCHAIN_CONTEXT_INTERFACE_V1"
FEATURE_ID = CAPABILITY
FEATURE_SCHEMA_VERSION = "ONCHAIN_CONTEXT_INTERFACE_V1_SCHEMA_V1"
PACKAGE_SCHEMA_VERSION = "ONCHAIN_CONTEXT_INTERFACE_V1_PACKAGE_V1"
SNAPSHOT_SCHEMA_VERSION = "ONCHAIN_CONTEXT_SNAPSHOT_V1"
SOURCE_KIND = "FUTURE_INTERFACE"
PACKAGE_AUTHORIZATION = "PREPARE_ONCHAIN_CONTEXT_INTERFACE_V1"

MAX_IMPLEMENTATION_OR_REPAIR_ATTEMPTS = 10
IMPLEMENTATION_OR_REPAIR_ATTEMPT = 1

POLICY_PATH = Path("src/context/resources/onchain_context_interface_policy_v1.json")
EXPECTED_POLICY_SCHEMA_VERSION = "ONCHAIN_CONTEXT_INTERFACE_POLICY_V1"

COMPONENT_FILENAME = "onchain_context_interface_component.json"
CHECKS_FILENAME = "producer_checks.json"
MANIFEST_FILENAME = "manifest.sha256"

OFFICIAL_APPEND_GATE_NAME = "TRADING_AI_OFFICIAL_LONG_EVIDENCE_APPEND_ALLOWED"
OFFICIAL_DATASET = Path("data/forward/long_forward_observation_dataset_v1.csv")
OFFICIAL_MANIFEST = Path(
    "data/forward/long_forward_observation_dataset_v1.manifest.csv"
)
OFFICIAL_LOCK = Path("data/forward/long_forward_observation_dataset_v1.lock")

METRIC_ID_RE = re.compile(r"^[A-Z0-9_.:-]{1,96}$")
PROHIBITED_OUTCOME_KEYS = frozenset(
    {
        "outcome",
        "future_outcome",
        "forward_return",
        "return",
        "mfe",
        "mae",
        "pnl",
        "profit",
        "loss",
        "target_hit",
        "stop_hit",
        "winner",
        "loser",
        "label",
    }
)


class OnchainContextInterfaceError(RuntimeError):
    def __init__(self, code: str, message: str) -> None:
        self.code = code
        super().__init__(message)


def _req(ok: bool, code: str, message: str) -> None:
    if not ok:
        raise OnchainContextInterfaceError(code, message)


def _sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _valid_sha(value: Any) -> bool:
    text = str(value)
    return len(text) == 64 and all(c in "0123456789abcdef" for c in text)


def _parse_utc(value: Any, field: str) -> datetime:
    try:
        dt = datetime.fromisoformat(str(value).strip().replace("Z", "+00:00"))
    except ValueError as exc:
        raise OnchainContextInterfaceError("TIMESTAMP_INVALID", field) from exc
    _req(dt.tzinfo is not None, "TIMESTAMP_TIMEZONE_REQUIRED", field)
    return dt.astimezone(timezone.utc)


def _utc(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).isoformat()


def _read_json(path: Path, code: str) -> dict[str, Any]:
    _req(path.is_file() and not path.is_symlink(), code, str(path))
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise OnchainContextInterfaceError(code, str(path)) from exc
    _req(isinstance(value, Mapping), code, str(path))
    return dict(value)


def _write_json_new(path: Path, value: Any) -> None:
    payload = (
        json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
            allow_nan=False,
        )
        + "\n"
    ).encode("utf-8")
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
    return {"dataset": _sha(dataset), "manifest": _sha(manifest)}


def _assert_no_outcome_keys(value: Any, path: str = "$") -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            normalized = str(key).strip().lower()
            _req(
                normalized not in PROHIBITED_OUTCOME_KEYS,
                "PROHIBITED_OUTCOME_FIELD",
                f"{path}.{key}",
            )
            _assert_no_outcome_keys(child, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _assert_no_outcome_keys(child, f"{path}[{index}]")


def validate_onchain_context_interface_policy_v1(
    policy: Mapping[str, Any],
) -> dict[str, Any]:
    _req(isinstance(policy, Mapping), "POLICY_INVALID", "mapping required")
    _req(
        policy.get("schema_version") == EXPECTED_POLICY_SCHEMA_VERSION,
        "POLICY_SCHEMA_INVALID",
        str(policy.get("schema_version")),
    )
    _req(
        policy.get("feature_id") == FEATURE_ID,
        "POLICY_FEATURE_ID_INVALID",
        str(policy.get("feature_id")),
    )
    _req(
        policy.get("snapshot_schema_version") == SNAPSHOT_SCHEMA_VERSION,
        "POLICY_SNAPSHOT_SCHEMA_INVALID",
        str(policy.get("snapshot_schema_version")),
    )
    _req(policy.get("asset") == "BTC", "POLICY_ASSET_INVALID", str(policy.get("asset")))
    _req(
        policy.get("network") == "BITCOIN",
        "POLICY_NETWORK_INVALID",
        str(policy.get("network")),
    )
    _req(policy.get("min_metric_count") == 1, "POLICY_MIN_METRICS_INVALID", str(policy.get("min_metric_count")))
    _req(policy.get("max_metric_count") == 64, "POLICY_MAX_METRICS_INVALID", str(policy.get("max_metric_count")))

    effective = _parse_utc(
        policy.get("policy_effective_from_utc"),
        "policy_effective_from_utc",
    )

    for field in (
        "exact_observation_identity_required",
        "metric_observation_not_after_reference_required",
        "metric_information_cutoff_not_before_observation_end_required",
        "metric_provider_availability_not_before_information_cutoff_required",
        "snapshot_creation_not_before_metric_availability_required",
        "metric_ids_unique_and_sorted_required",
    ):
        _req(
            policy.get(field) is True,
            "POLICY_REQUIRED_GUARD_INVALID",
            field,
        )

    for field in (
        "producer_network_fetch_allowed",
        "producer_market_data_fetch_allowed",
        "producer_chain_rpc_allowed",
        "producer_provider_api_allowed",
        "metric_interpretation_allowed",
        "directional_meaning_assigned",
        "threshold_signal_allowed",
        "composite_score_assigned",
        "signal_semantics",
        "future_outcomes_used",
    ):
        _req(
            policy.get(field) is False,
            "POLICY_FORBIDDEN_SEMANTIC_ENABLED",
            field,
        )

    return {
        "policy_effective_from_utc": _utc(effective),
        "asset": "BTC",
        "network": "BITCOIN",
        "min_metric_count": 1,
        "max_metric_count": 64,
    }


def load_onchain_context_interface_policy_v1(
    repo_root: Path | str,
) -> tuple[dict[str, Any], str]:
    repo = Path(repo_root).resolve()
    path = repo / POLICY_PATH
    policy = _read_json(path, "POLICY_FILE_INVALID")
    validate_onchain_context_interface_policy_v1(policy)
    return policy, _sha(path)


def validate_onchain_context_snapshot_v1(
    snapshot: Mapping[str, Any],
    *,
    policy: Mapping[str, Any],
) -> dict[str, Any]:
    _assert_no_outcome_keys(snapshot)
    _req(
        snapshot.get("snapshot_schema_version") == SNAPSHOT_SCHEMA_VERSION,
        "SNAPSHOT_SCHEMA_INVALID",
        str(snapshot.get("snapshot_schema_version")),
    )
    _req(snapshot.get("asset") == "BTC", "SNAPSHOT_ASSET_INVALID", str(snapshot.get("asset")))
    _req(snapshot.get("network") == "BITCOIN", "SNAPSHOT_NETWORK_INVALID", str(snapshot.get("network")))
    _req(
        _valid_sha(snapshot.get("metric_schema_sha256")),
        "METRIC_SCHEMA_SHA_INVALID",
        str(snapshot.get("metric_schema_sha256")),
    )

    for field in (
        "observation_id",
        "provider_name",
        "dataset_id",
        "dataset_version",
        "source_reference",
    ):
        _req(
            isinstance(snapshot.get(field), str) and bool(snapshot[field].strip()),
            "SNAPSHOT_TEXT_INVALID",
            field,
        )

    reference = _parse_utc(
        snapshot.get("reference_boundary_utc"),
        "reference_boundary_utc",
    )
    created = _parse_utc(
        snapshot.get("snapshot_created_at_utc"),
        "snapshot_created_at_utc",
    )

    metrics = snapshot.get("metrics")
    _req(isinstance(metrics, list), "METRICS_INVALID", "metrics")
    _req(
        policy["min_metric_count"]
        <= len(metrics)
        <= policy["max_metric_count"],
        "METRIC_COUNT_INVALID",
        str(len(metrics)),
    )

    parsed = []
    ids = []
    max_provider_available = None
    max_information_cutoff = None

    for metric in metrics:
        _req(isinstance(metric, Mapping), "METRIC_INVALID", str(metric))
        metric_id = str(metric.get("metric_id", ""))
        unit = str(metric.get("unit", ""))
        revision_id = str(metric.get("revision_id", ""))

        _req(bool(METRIC_ID_RE.fullmatch(metric_id)), "METRIC_ID_INVALID", metric_id)
        _req(bool(unit.strip()) and len(unit) <= 64, "METRIC_UNIT_INVALID", unit)
        _req(bool(revision_id.strip()), "METRIC_REVISION_INVALID", revision_id)

        try:
            value = float(metric.get("value"))
        except (TypeError, ValueError) as exc:
            raise OnchainContextInterfaceError(
                "METRIC_VALUE_INVALID",
                metric_id,
            ) from exc
        _req(math.isfinite(value), "METRIC_VALUE_INVALID", metric_id)

        start = _parse_utc(
            metric.get("observation_start_utc"),
            f"{metric_id}.observation_start_utc",
        )
        end = _parse_utc(
            metric.get("observation_end_utc"),
            f"{metric_id}.observation_end_utc",
        )
        info = _parse_utc(
            metric.get("information_cutoff_utc"),
            f"{metric_id}.information_cutoff_utc",
        )
        provider_available = _parse_utc(
            metric.get("provider_available_at_utc"),
            f"{metric_id}.provider_available_at_utc",
        )

        _req(start <= end, "METRIC_OBSERVATION_RANGE_INVALID", metric_id)
        _req(
            end <= info,
            "METRIC_INFORMATION_BEFORE_OBSERVATION_END",
            metric_id,
        )
        _req(
            info <= provider_available,
            "METRIC_PROVIDER_AVAILABLE_BEFORE_INFORMATION",
            metric_id,
        )
        _req(
            provider_available <= created,
            "SNAPSHOT_CREATED_BEFORE_METRIC_AVAILABLE",
            metric_id,
        )

        ids.append(metric_id)
        max_provider_available = (
            provider_available
            if max_provider_available is None
            else max(max_provider_available, provider_available)
        )
        max_information_cutoff = (
            info
            if max_information_cutoff is None
            else max(max_information_cutoff, info)
        )

        parsed.append(
            {
                "metric_id": metric_id,
                "unit": unit,
                "value": value,
                "revision_id": revision_id,
                "observation_start_utc": _utc(start),
                "observation_end_utc": _utc(end),
                "information_cutoff_utc": _utc(info),
                "provider_available_at_utc": _utc(provider_available),
            }
        )

    _req(len(ids) == len(set(ids)), "METRIC_IDS_DUPLICATE", str(ids))
    _req(ids == sorted(ids), "METRIC_IDS_NOT_SORTED", str(ids))

    return {
        "observation_id": str(snapshot["observation_id"]),
        "reference_boundary_utc": _utc(reference),
        "snapshot_created_at_utc": _utc(created),
        "metric_schema_sha256": str(snapshot["metric_schema_sha256"]),
        "provider_name": str(snapshot["provider_name"]),
        "dataset_id": str(snapshot["dataset_id"]),
        "dataset_version": str(snapshot["dataset_version"]),
        "source_reference": str(snapshot["source_reference"]),
        "metrics": parsed,
        "max_provider_available_at_utc": _utc(max_provider_available),
        "max_information_cutoff_utc": _utc(max_information_cutoff),
    }


def _validate_descriptor(
    descriptor: Mapping[str, Any],
) -> dict[str, Any]:
    _req(isinstance(descriptor, Mapping), "DESCRIPTOR_INVALID", "mapping required")
    _req(
        descriptor.get("observation_descriptor_schema_version")
        == "FORWARD_OUTCOME_OBSERVATION_DESCRIPTOR_V1",
        "DESCRIPTOR_SCHEMA_INVALID",
        str(descriptor.get("observation_descriptor_schema_version")),
    )
    _req(
        descriptor.get("symbol") == "BTCUSDT"
        and descriptor.get("timeframe") == "15m",
        "DESCRIPTOR_IDENTITY_INVALID",
        "symbol/timeframe",
    )
    _req(
        isinstance(descriptor.get("primary_candidate_detected"), bool),
        "PRIMARY_CANDIDATE_STATE_INVALID",
        str(descriptor.get("primary_candidate_detected")),
    )

    reference = _parse_utc(
        descriptor.get("reference_boundary_utc"),
        "reference_boundary_utc",
    )
    cutoff = _parse_utc(
        descriptor.get("synchronized_context_available_at_utc"),
        "synchronized_context_available_at_utc",
    )
    _req(
        cutoff >= reference,
        "CONTEXT_CUTOFF_BEFORE_REFERENCE",
        _utc(cutoff),
    )
    _req(
        bool(str(descriptor.get("observation_id", "")).strip()),
        "OBSERVATION_ID_INVALID",
        str(descriptor.get("observation_id")),
    )
    return dict(descriptor)


def build_onchain_context_interface_v1_component(
    *,
    observation_descriptor: Mapping[str, Any],
    external_snapshot: Mapping[str, Any],
    external_snapshot_sha256: str,
    policy: Mapping[str, Any],
    policy_sha256: str,
    produced_at_utc: str,
) -> dict[str, Any]:
    descriptor = _validate_descriptor(observation_descriptor)
    p = validate_onchain_context_interface_policy_v1(policy)
    s = validate_onchain_context_snapshot_v1(external_snapshot, policy=p)

    _req(
        _valid_sha(external_snapshot_sha256),
        "SNAPSHOT_SHA_INVALID",
        external_snapshot_sha256,
    )
    _req(_valid_sha(policy_sha256), "POLICY_SHA_INVALID", policy_sha256)

    reference = _parse_utc(
        descriptor["reference_boundary_utc"],
        "reference_boundary_utc",
    )
    snapshot_reference = _parse_utc(
        s["reference_boundary_utc"],
        "snapshot.reference_boundary_utc",
    )

    _req(
        snapshot_reference == reference,
        "SNAPSHOT_REFERENCE_MISMATCH",
        s["reference_boundary_utc"],
    )
    _req(
        s["observation_id"] == descriptor["observation_id"],
        "SNAPSHOT_OBSERVATION_ID_MISMATCH",
        s["observation_id"],
    )

    for metric in s["metrics"]:
        end = _parse_utc(
            metric["observation_end_utc"],
            f"{metric['metric_id']}.observation_end_utc",
        )
        _req(
            end <= reference,
            "METRIC_OBSERVATION_AFTER_REFERENCE",
            metric["metric_id"],
        )

    policy_effective = _parse_utc(
        p["policy_effective_from_utc"],
        "policy_effective_from_utc",
    )
    snapshot_created = _parse_utc(
        s["snapshot_created_at_utc"],
        "snapshot_created_at_utc",
    )
    max_provider_available = _parse_utc(
        s["max_provider_available_at_utc"],
        "max_provider_available_at_utc",
    )
    information_cutoff = _parse_utc(
        s["max_information_cutoff_utc"],
        "max_information_cutoff_utc",
    )

    available = max(
        snapshot_created,
        policy_effective,
        max_provider_available,
        information_cutoff,
    )
    produced = _parse_utc(produced_at_utc, "produced_at_utc")
    _req(
        produced >= available,
        "PRODUCED_BEFORE_FEATURE_AVAILABLE",
        _utc(produced),
    )

    metrics_payload = []
    for metric in s["metrics"]:
        end = _parse_utc(
            metric["observation_end_utc"],
            f"{metric['metric_id']}.observation_end_utc",
        )
        metrics_payload.append(
            {
                **metric,
                "age_seconds_at_reference": (
                    reference - end
                ).total_seconds(),
            }
        )

    payload = {
        "interface_semantics": "PROVIDER_AGNOSTIC_ONCHAIN_RAW_METRICS_ONLY",
        "asset": "BTC",
        "network": "BITCOIN",
        "provider_name": s["provider_name"],
        "dataset_id": s["dataset_id"],
        "dataset_version": s["dataset_version"],
        "source_reference": s["source_reference"],
        "metric_schema_sha256": s["metric_schema_sha256"],
        "metric_count": len(metrics_payload),
        "metrics": metrics_payload,
        "snapshot_created_at_utc": s["snapshot_created_at_utc"],
        "policy_effective_from_utc": p["policy_effective_from_utc"],
        "external_snapshot_reused_only": True,
        "producer_network_fetch_executed": False,
        "producer_market_data_fetch_executed": False,
        "producer_chain_rpc_executed": False,
        "producer_provider_api_executed": False,
        "metric_interpretation_performed": False,
        "threshold_signal_evaluated": False,
        "future_outcomes_used": False,
        "directional_semantics": False,
        "signal_semantics": False,
        "composite_score_assigned": False,
        "candidate_modification_semantics": False,
        "primary_rule_modification_semantics": False,
    }

    component = {
        "feature_id": FEATURE_ID,
        "source_kind": SOURCE_KIND,
        "feature_schema_version": FEATURE_SCHEMA_VERSION,
        "status": "AVAILABLE",
        "reason": None,
        "available_at_utc": _utc(available),
        "information_cutoff_utc": _utc(information_cutoff),
        "source_artifact_sha256": external_snapshot_sha256,
        "payload": payload,
    }

    validate_onchain_context_interface_v1_component(component)
    return component


def validate_onchain_context_interface_v1_component(
    component: Mapping[str, Any],
) -> dict[str, Any]:
    _req(isinstance(component, Mapping), "COMPONENT_INVALID", "mapping required")
    _req(component.get("feature_id") == FEATURE_ID, "COMPONENT_FEATURE_ID_INVALID", str(component.get("feature_id")))
    _req(component.get("source_kind") == SOURCE_KIND, "COMPONENT_SOURCE_KIND_INVALID", str(component.get("source_kind")))
    _req(component.get("feature_schema_version") == FEATURE_SCHEMA_VERSION, "COMPONENT_SCHEMA_INVALID", str(component.get("feature_schema_version")))
    _req(component.get("status") == "AVAILABLE", "COMPONENT_STATUS_INVALID", str(component.get("status")))

    available = _parse_utc(component.get("available_at_utc"), "available_at_utc")
    info = _parse_utc(component.get("information_cutoff_utc"), "information_cutoff_utc")
    _req(info <= available, "COMPONENT_INFORMATION_AFTER_AVAILABILITY", "timestamps")
    _req(_valid_sha(component.get("source_artifact_sha256")), "COMPONENT_SOURCE_SHA_INVALID", str(component.get("source_artifact_sha256")))

    payload = component.get("payload")
    _req(isinstance(payload, Mapping), "COMPONENT_PAYLOAD_INVALID", "payload")
    _req(
        payload.get("interface_semantics")
        == "PROVIDER_AGNOSTIC_ONCHAIN_RAW_METRICS_ONLY",
        "PAYLOAD_SEMANTICS_INVALID",
        str(payload.get("interface_semantics")),
    )
    _req(payload.get("asset") == "BTC", "PAYLOAD_ASSET_INVALID", str(payload.get("asset")))
    _req(payload.get("network") == "BITCOIN", "PAYLOAD_NETWORK_INVALID", str(payload.get("network")))
    _req(_valid_sha(payload.get("metric_schema_sha256")), "PAYLOAD_METRIC_SCHEMA_SHA_INVALID", str(payload.get("metric_schema_sha256")))
    _req(
        isinstance(payload.get("metrics"), list)
        and payload.get("metric_count") == len(payload["metrics"])
        and len(payload["metrics"]) >= 1,
        "PAYLOAD_METRIC_COUNT_INVALID",
        str(payload.get("metric_count")),
    )

    metric_ids = []
    for metric in payload["metrics"]:
        _req(
            set(metric)
            == {
                "metric_id",
                "unit",
                "value",
                "revision_id",
                "observation_start_utc",
                "observation_end_utc",
                "information_cutoff_utc",
                "provider_available_at_utc",
                "age_seconds_at_reference",
            },
            "PAYLOAD_METRIC_FIELDS_INVALID",
            str(sorted(metric)),
        )
        _req(math.isfinite(float(metric["value"])), "PAYLOAD_METRIC_VALUE_INVALID", str(metric))
        _req(
            math.isfinite(float(metric["age_seconds_at_reference"]))
            and float(metric["age_seconds_at_reference"]) >= 0,
            "PAYLOAD_METRIC_AGE_INVALID",
            str(metric),
        )
        metric_ids.append(metric["metric_id"])

    _req(metric_ids == sorted(metric_ids), "PAYLOAD_METRICS_NOT_SORTED", str(metric_ids))
    _req(len(metric_ids) == len(set(metric_ids)), "PAYLOAD_METRICS_DUPLICATE", str(metric_ids))
    _req(payload.get("external_snapshot_reused_only") is True, "PAYLOAD_REUSE_GUARD_INVALID", "external_snapshot_reused_only")

    for field in (
        "producer_network_fetch_executed",
        "producer_market_data_fetch_executed",
        "producer_chain_rpc_executed",
        "producer_provider_api_executed",
        "metric_interpretation_performed",
        "threshold_signal_evaluated",
        "future_outcomes_used",
        "directional_semantics",
        "signal_semantics",
        "composite_score_assigned",
        "candidate_modification_semantics",
        "primary_rule_modification_semantics",
    ):
        _req(
            payload.get(field) is False,
            "FORBIDDEN_PAYLOAD_SEMANTIC_ENABLED",
            field,
        )

    return {
        "status": "AVAILABLE",
        "metric_count": len(payload["metrics"]),
        "directional_semantics": False,
        "signal_semantics": False,
    }


def _placeholder(item: Mapping[str, Any]) -> dict[str, Any]:
    fid = str(item["feature_id"])
    return {
        "feature_id": fid,
        "source_kind": str(item["source_kind"]),
        "feature_schema_version": fid + "_PLACEHOLDER_SCHEMA_V1",
        "status": "NOT_CONFIGURED",
        "reason": "not configured for producer integration check",
        "available_at_utc": None,
        "information_cutoff_utc": None,
        "source_artifact_sha256": None,
        "payload": None,
    }


def validate_component_against_level_a_pack_v1(
    *,
    observation_descriptor: Mapping[str, Any],
    component: Mapping[str, Any],
) -> dict[str, Any]:
    components = {
        str(item["feature_id"]): _placeholder(item)
        for item in FEATURE_REGISTRY
    }
    components[FEATURE_ID] = dict(component)
    pack = build_context_feature_pack_v1(
        observation_descriptor=observation_descriptor,
        components=components,
        pack_id="PACK_COMPATIBILITY_CHECK_ONLY",
    )
    feature = next(
        x for x in pack["features"] if x["feature_id"] == FEATURE_ID
    )
    return {
        "status": feature["status"],
        "point_in_time_eligible": feature["point_in_time_eligible"],
        "eligibility_reason": feature["eligibility_reason"],
        "payload_sha256": feature["payload_sha256"],
    }


def _write_manifest(directory: Path) -> None:
    lines = [
        f"{_sha(directory / name)}  {name}"
        for name in sorted((CHECKS_FILENAME, COMPONENT_FILENAME))
    ]
    path = directory / MANIFEST_FILENAME
    with path.open("xb") as handle:
        handle.write(("\n".join(lines) + "\n").encode("utf-8"))


def _validate_manifest(directory: Path) -> int:
    path = directory / MANIFEST_FILENAME
    _req(
        path.is_file() and not path.is_symlink(),
        "PACKAGE_MANIFEST_MISSING",
        str(path),
    )
    lines = [
        x for x in path.read_text(encoding="utf-8").splitlines() if x.strip()
    ]
    _req(
        len(lines) == 2,
        "PACKAGE_MANIFEST_ENTRY_COUNT_INVALID",
        str(len(lines)),
    )

    expected_names = {CHECKS_FILENAME, COMPONENT_FILENAME}
    seen = set()

    for line in lines:
        parts = line.split("  ", 1)
        _req(
            len(parts) == 2 and len(parts[0]) == 64,
            "PACKAGE_MANIFEST_LINE_INVALID",
            line,
        )
        digest, name = parts
        _req(
            name in expected_names,
            "PACKAGE_MANIFEST_SCOPE_INVALID",
            name,
        )
        target = directory / name
        _req(
            target.is_file() and not target.is_symlink(),
            "PACKAGE_MANIFEST_PAYLOAD_MISSING",
            name,
        )
        _req(
            _sha(target) == digest,
            "PACKAGE_MANIFEST_HASH_MISMATCH",
            name,
        )
        seen.add(name)

    _req(
        seen == expected_names,
        "PACKAGE_MANIFEST_SCOPE_INVALID",
        str(sorted(seen)),
    )
    return len(lines)


def validate_onchain_context_interface_v1_package(
    directory: Path | str,
) -> dict[str, Any]:
    root = Path(directory).resolve()
    _req(
        root.is_dir() and not root.is_symlink(),
        "PACKAGE_DIRECTORY_INVALID",
        str(root),
    )
    entries = _validate_manifest(root)
    component = _read_json(
        root / COMPONENT_FILENAME,
        "PACKAGE_COMPONENT_INVALID",
    )
    checks = _read_json(root / CHECKS_FILENAME, "PACKAGE_CHECKS_INVALID")
    result = validate_onchain_context_interface_v1_component(component)

    _req(
        checks.get("package_schema_version") == PACKAGE_SCHEMA_VERSION,
        "PACKAGE_SCHEMA_INVALID",
        str(checks.get("package_schema_version")),
    )
    _req(
        checks.get("feature_id") == FEATURE_ID,
        "PACKAGE_FEATURE_ID_INVALID",
        str(checks.get("feature_id")),
    )

    for field in (
        "real_network_request_executed",
        "provider_api_request_executed",
        "chain_rpc_request_executed",
        "market_data_fetched_by_producer",
        "future_outcomes_used",
        "metric_interpretation_performed",
        "direction_inferred",
        "signal_generated",
        "candidate_modified",
        "primary_rule_modified",
        "official_append_executed",
        "official_dataset_changed",
        "official_manifest_changed",
    ):
        _req(
            checks.get(field) is False,
            "PACKAGE_CHECK_INVALID",
            field,
        )

    return {
        **result,
        "manifest_entries": entries,
        "point_in_time_eligible_under_pack_policy": bool(
            checks["point_in_time_eligible_under_pack_policy"]
        ),
    }


def prepare_onchain_context_interface_v1_package(
    *,
    repo_root: Path | str,
    observation_descriptor_json: Path | str,
    external_snapshot_json: Path | str,
    output_directory: Path | str,
    produced_at_utc: str,
    authorization: str | None = None,
) -> dict[str, Any]:
    _req(
        authorization == PACKAGE_AUTHORIZATION,
        "PACKAGE_AUTHORIZATION_REQUIRED",
        "authorization",
    )
    _gate_off()

    repo = Path(repo_root).resolve()
    descriptor_path = Path(observation_descriptor_json).resolve()
    snapshot_path = Path(external_snapshot_json).resolve()
    output = Path(output_directory).resolve()

    _req((repo / ".git").is_dir(), "REPOSITORY_ROOT_INVALID", str(repo))
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
        not _inside(snapshot_path, repo),
        "ONCHAIN_SNAPSHOT_INSIDE_REPOSITORY_PROHIBITED",
        str(snapshot_path),
    )

    official_before = _official(repo)
    descriptor = _read_json(descriptor_path, "DESCRIPTOR_FILE_INVALID")
    snapshot = _read_json(snapshot_path, "ONCHAIN_SNAPSHOT_FILE_INVALID")
    policy, policy_sha = load_onchain_context_interface_policy_v1(repo)

    component = build_onchain_context_interface_v1_component(
        observation_descriptor=descriptor,
        external_snapshot=snapshot,
        external_snapshot_sha256=_sha(snapshot_path),
        policy=policy,
        policy_sha256=policy_sha,
        produced_at_utc=produced_at_utc,
    )

    compatibility = validate_component_against_level_a_pack_v1(
        observation_descriptor=descriptor,
        component=component,
    )

    _req(
        _official(repo) == official_before,
        "OFFICIAL_ARTIFACT_CHANGED",
        "before output",
    )
    _gate_off()

    temp = output.parent / f".{output.name}.tmp-{uuid.uuid4().hex}"

    try:
        temp.mkdir()
        _write_json_new(temp / COMPONENT_FILENAME, component)

        checks = {
            "package_schema_version": PACKAGE_SCHEMA_VERSION,
            "capability": CAPABILITY,
            "feature_id": FEATURE_ID,
            "observation_descriptor_sha256": _sha(descriptor_path),
            "external_snapshot_sha256": _sha(snapshot_path),
            "policy_resource_sha256": policy_sha,
            "point_in_time_eligible_under_pack_policy": compatibility[
                "point_in_time_eligible"
            ],
            "pack_eligibility_reason": compatibility["eligibility_reason"],
            "external_snapshot_was_preexisting": True,
            "external_snapshot_validated_locally": True,
            "real_network_request_executed": False,
            "provider_api_request_executed": False,
            "chain_rpc_request_executed": False,
            "market_data_fetched_by_producer": False,
            "future_outcomes_used": False,
            "metric_interpretation_performed": False,
            "direction_inferred": False,
            "signal_generated": False,
            "candidate_modified": False,
            "primary_rule_modified": False,
            "official_append_executed": False,
            "official_dataset_changed": False,
            "official_manifest_changed": False,
        }

        _write_json_new(temp / CHECKS_FILENAME, checks)
        _write_manifest(temp)
        validate_onchain_context_interface_v1_package(temp)
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

    result = validate_onchain_context_interface_v1_package(output)

    return {
        "capability": CAPABILITY,
        "feature_id": FEATURE_ID,
        "output_directory": str(output),
        "component_status": result["status"],
        "metric_count": result["metric_count"],
        "point_in_time_eligible_under_pack_policy": result[
            "point_in_time_eligible_under_pack_policy"
        ],
        "real_network_request_executed": False,
        "provider_api_request_executed": False,
        "chain_rpc_request_executed": False,
        "market_data_fetched_by_producer": False,
        "official_append_executed": False,
    }
