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

CAPABILITY = "EXTERNAL_THESIS_MODEL_CARD_V1"
FEATURE_ID = CAPABILITY
FEATURE_SCHEMA_VERSION = "EXTERNAL_THESIS_MODEL_CARD_V1_SCHEMA_V1"
PACKAGE_SCHEMA_VERSION = "EXTERNAL_THESIS_MODEL_CARD_V1_PACKAGE_V1"
SNAPSHOT_SCHEMA_VERSION = "EXTERNAL_THESIS_MODEL_CARD_SNAPSHOT_V1"
SOURCE_KIND = "EXTERNAL_MODEL"
PACKAGE_AUTHORIZATION = "PREPARE_EXTERNAL_THESIS_MODEL_CARD_V1"

MAX_IMPLEMENTATION_OR_REPAIR_ATTEMPTS = 10
IMPLEMENTATION_OR_REPAIR_ATTEMPT = 1

POLICY_PATH = Path(
    "src/context/resources/external_thesis_model_card_policy_v1.json"
)
EXPECTED_POLICY_SCHEMA_VERSION = "EXTERNAL_THESIS_MODEL_CARD_POLICY_V1"

METHOD_FAMILIES = frozenset(
    {"CYCLE", "MACRO", "TECHNICAL", "ONCHAIN", "FLOW", "MULTI_FACTOR", "OTHER"}
)
HORIZON_LABELS = frozenset(
    {"INTRADAY", "SWING", "MULTI_WEEK", "CYCLE", "UNSPECIFIED"}
)
STATE_CODE_RE = re.compile(r"^[A-Z0-9_:-]{1,64}$")

COMPONENT_FILENAME = "external_thesis_model_card_component.json"
CHECKS_FILENAME = "producer_checks.json"
MANIFEST_FILENAME = "manifest.sha256"

OFFICIAL_APPEND_GATE_NAME = "TRADING_AI_OFFICIAL_LONG_EVIDENCE_APPEND_ALLOWED"
OFFICIAL_DATASET = Path("data/forward/long_forward_observation_dataset_v1.csv")
OFFICIAL_MANIFEST = Path(
    "data/forward/long_forward_observation_dataset_v1.manifest.csv"
)
OFFICIAL_LOCK = Path("data/forward/long_forward_observation_dataset_v1.lock")


class ExternalThesisModelCardError(RuntimeError):
    def __init__(self, code: str, message: str) -> None:
        self.code = code
        super().__init__(message)


def _req(ok: bool, code: str, message: str) -> None:
    if not ok:
        raise ExternalThesisModelCardError(code, message)


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
        raise ExternalThesisModelCardError("TIMESTAMP_INVALID", field) from exc
    _req(dt.tzinfo is not None, "TIMESTAMP_TIMEZONE_REQUIRED", field)
    return dt.astimezone(timezone.utc)


def _utc(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).isoformat()


def _read_json(path: Path, code: str) -> dict[str, Any]:
    _req(path.is_file() and not path.is_symlink(), code, str(path))
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ExternalThesisModelCardError(code, str(path)) from exc
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
    _req(dataset.is_file() and not dataset.is_symlink(), "OFFICIAL_DATASET_INVALID", str(dataset))
    _req(manifest.is_file() and not manifest.is_symlink(), "OFFICIAL_MANIFEST_INVALID", str(manifest))
    _req(not lock.exists() and not lock.is_symlink(), "OFFICIAL_LOCK_PRESENT", str(lock))
    return {"dataset": _sha(dataset), "manifest": _sha(manifest)}


def validate_external_thesis_model_card_policy_v1(
    policy: Mapping[str, Any],
) -> dict[str, Any]:
    _req(isinstance(policy, Mapping), "POLICY_INVALID", "mapping required")
    _req(policy.get("schema_version") == EXPECTED_POLICY_SCHEMA_VERSION, "POLICY_SCHEMA_INVALID", str(policy.get("schema_version")))
    _req(policy.get("feature_id") == FEATURE_ID, "POLICY_FEATURE_ID_INVALID", str(policy.get("feature_id")))
    _req(policy.get("external_snapshot_schema_version") == SNAPSHOT_SCHEMA_VERSION, "POLICY_SNAPSHOT_SCHEMA_INVALID", str(policy.get("external_snapshot_schema_version")))

    effective = _parse_utc(policy.get("policy_effective_from_utc"), "policy_effective_from_utc")

    for field in (
        "external_frozen_snapshot_required",
        "reference_inside_declared_applicability_required",
        "source_published_not_after_information_cutoff_required",
        "information_cutoff_not_after_thesis_generated_required",
        "thesis_generated_not_after_snapshot_created_required",
        "opaque_state_code_required",
    ):
        _req(policy.get(field) is True, "POLICY_REQUIRED_GUARD_INVALID", field)

    for field in (
        "text_claims_ingested",
        "target_prices_ingested",
        "confidence_scores_ingested",
        "producer_network_fetch_allowed",
        "producer_model_execution_allowed",
        "future_outcomes_used",
        "directional_meaning_assigned",
        "composite_score_assigned",
        "signal_semantics",
    ):
        _req(policy.get(field) is False, "POLICY_FORBIDDEN_SEMANTIC_ENABLED", field)

    return {
        "policy_effective_from_utc": _utc(effective),
        "snapshot_schema_version": SNAPSHOT_SCHEMA_VERSION,
    }


def load_external_thesis_model_card_policy_v1(
    repo_root: Path | str,
) -> tuple[dict[str, Any], str]:
    repo = Path(repo_root).resolve()
    path = repo / POLICY_PATH
    policy = _read_json(path, "POLICY_FILE_INVALID")
    validate_external_thesis_model_card_policy_v1(policy)
    return policy, _sha(path)


def validate_external_thesis_model_card_snapshot_v1(
    snapshot: Mapping[str, Any],
) -> dict[str, Any]:
    _req(isinstance(snapshot, Mapping), "SNAPSHOT_INVALID", "mapping required")
    _req(snapshot.get("snapshot_schema_version") == SNAPSHOT_SCHEMA_VERSION, "SNAPSHOT_SCHEMA_INVALID", str(snapshot.get("snapshot_schema_version")))

    for field in (
        "thesis_id",
        "thesis_version",
        "source_name",
        "source_reference",
    ):
        _req(
            isinstance(snapshot.get(field), str) and bool(snapshot[field].strip()),
            "SNAPSHOT_TEXT_INVALID",
            field,
        )

    method_family = str(snapshot.get("method_family", ""))
    horizon_label = str(snapshot.get("horizon_label", ""))
    state_code = str(snapshot.get("state_code", ""))

    _req(method_family in METHOD_FAMILIES, "SNAPSHOT_METHOD_FAMILY_INVALID", method_family)
    _req(horizon_label in HORIZON_LABELS, "SNAPSHOT_HORIZON_INVALID", horizon_label)
    _req(bool(STATE_CODE_RE.fullmatch(state_code)), "SNAPSHOT_STATE_CODE_INVALID", state_code)
    _req(_valid_sha(snapshot.get("thesis_content_sha256")), "SNAPSHOT_CONTENT_SHA_INVALID", str(snapshot.get("thesis_content_sha256")))

    published = _parse_utc(snapshot.get("source_published_at_utc"), "source_published_at_utc")
    info = _parse_utc(snapshot.get("information_cutoff_utc"), "information_cutoff_utc")
    generated = _parse_utc(snapshot.get("thesis_generated_at_utc"), "thesis_generated_at_utc")
    created = _parse_utc(snapshot.get("snapshot_created_at_utc"), "snapshot_created_at_utc")
    start = _parse_utc(snapshot.get("applicability_start_utc"), "applicability_start_utc")

    end_raw = snapshot.get("applicability_end_utc")
    end = None if end_raw is None else _parse_utc(end_raw, "applicability_end_utc")

    _req(published <= info, "SNAPSHOT_PUBLISHED_AFTER_INFORMATION_CUTOFF", _utc(published))
    _req(info <= generated, "SNAPSHOT_INFORMATION_AFTER_THESIS_GENERATED", _utc(info))
    _req(generated <= created, "SNAPSHOT_THESIS_AFTER_SNAPSHOT_CREATED", _utc(generated))
    if end is not None:
        _req(start <= end, "SNAPSHOT_APPLICABILITY_RANGE_INVALID", "start/end")

    return {
        "method_family": method_family,
        "horizon_label": horizon_label,
        "state_code": state_code,
        "source_published_at_utc": _utc(published),
        "information_cutoff_utc": _utc(info),
        "thesis_generated_at_utc": _utc(generated),
        "snapshot_created_at_utc": _utc(created),
        "applicability_start_utc": _utc(start),
        "applicability_end_utc": None if end is None else _utc(end),
    }


def _validate_descriptor(descriptor: Mapping[str, Any]) -> dict[str, Any]:
    _req(isinstance(descriptor, Mapping), "DESCRIPTOR_INVALID", "mapping required")
    _req(descriptor.get("observation_descriptor_schema_version") == "FORWARD_OUTCOME_OBSERVATION_DESCRIPTOR_V1", "DESCRIPTOR_SCHEMA_INVALID", str(descriptor.get("observation_descriptor_schema_version")))
    _req(descriptor.get("symbol") == "BTCUSDT" and descriptor.get("timeframe") == "15m", "DESCRIPTOR_IDENTITY_INVALID", "symbol/timeframe")
    _req(isinstance(descriptor.get("primary_candidate_detected"), bool), "PRIMARY_CANDIDATE_STATE_INVALID", str(descriptor.get("primary_candidate_detected")))
    reference = _parse_utc(descriptor.get("reference_boundary_utc"), "reference_boundary_utc")
    cutoff = _parse_utc(descriptor.get("synchronized_context_available_at_utc"), "synchronized_context_available_at_utc")
    _req(cutoff >= reference, "CONTEXT_CUTOFF_BEFORE_REFERENCE", _utc(cutoff))
    _req(bool(str(descriptor.get("observation_id", "")).strip()), "OBSERVATION_ID_INVALID", str(descriptor.get("observation_id")))
    return dict(descriptor)


def build_external_thesis_model_card_v1_component(
    *,
    observation_descriptor: Mapping[str, Any],
    external_snapshot: Mapping[str, Any],
    external_snapshot_sha256: str,
    policy: Mapping[str, Any],
    policy_sha256: str,
    produced_at_utc: str,
) -> dict[str, Any]:
    descriptor = _validate_descriptor(observation_descriptor)
    p = validate_external_thesis_model_card_policy_v1(policy)
    s = validate_external_thesis_model_card_snapshot_v1(external_snapshot)
    _req(_valid_sha(external_snapshot_sha256), "SNAPSHOT_SHA_INVALID", external_snapshot_sha256)
    _req(_valid_sha(policy_sha256), "POLICY_SHA_INVALID", policy_sha256)

    reference = _parse_utc(descriptor["reference_boundary_utc"], "reference_boundary_utc")
    start = _parse_utc(s["applicability_start_utc"], "applicability_start_utc")
    end = None if s["applicability_end_utc"] is None else _parse_utc(s["applicability_end_utc"], "applicability_end_utc")

    _req(reference >= start, "REFERENCE_BEFORE_THESIS_APPLICABILITY", _utc(reference))
    if end is not None:
        _req(reference <= end, "REFERENCE_AFTER_THESIS_APPLICABILITY", _utc(reference))

    policy_effective = _parse_utc(p["policy_effective_from_utc"], "policy_effective_from_utc")
    snapshot_created = _parse_utc(s["snapshot_created_at_utc"], "snapshot_created_at_utc")
    available = max(snapshot_created, policy_effective)
    produced = _parse_utc(produced_at_utc, "produced_at_utc")
    _req(produced >= available, "PRODUCED_BEFORE_FEATURE_AVAILABLE", _utc(produced))

    payload = {
        "model_semantics": "EXTERNAL_THESIS_MODEL_CARD_OPAQUE_STATE_ONLY",
        "thesis_id": external_snapshot["thesis_id"],
        "thesis_version": external_snapshot["thesis_version"],
        "source_name": external_snapshot["source_name"],
        "source_reference": external_snapshot["source_reference"],
        "thesis_content_sha256": external_snapshot["thesis_content_sha256"],
        "method_family": s["method_family"],
        "horizon_label": s["horizon_label"],
        "state_code": s["state_code"],
        "state_code_semantics_interpreted": False,
        "source_published_at_utc": s["source_published_at_utc"],
        "information_cutoff_utc": s["information_cutoff_utc"],
        "thesis_generated_at_utc": s["thesis_generated_at_utc"],
        "snapshot_created_at_utc": s["snapshot_created_at_utc"],
        "applicability_start_utc": s["applicability_start_utc"],
        "applicability_end_utc": s["applicability_end_utc"],
        "producer_generated_at_utc": _utc(produced),
        "policy_effective_from_utc": p["policy_effective_from_utc"],
        "retrospective_policy_floor_applied": snapshot_created < policy_effective,
        "external_snapshot_reused_only": True,
        "text_claims_ingested": False,
        "target_prices_ingested": False,
        "confidence_scores_ingested": False,
        "producer_network_fetch_executed": False,
        "producer_model_execution_executed": False,
        "market_data_input_used": False,
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
        "information_cutoff_utc": s["information_cutoff_utc"],
        "source_artifact_sha256": external_snapshot_sha256,
        "payload": payload,
    }
    validate_external_thesis_model_card_v1_component(component)
    return component


def validate_external_thesis_model_card_v1_component(
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
    _req(payload.get("model_semantics") == "EXTERNAL_THESIS_MODEL_CARD_OPAQUE_STATE_ONLY", "PAYLOAD_SEMANTICS_INVALID", str(payload.get("model_semantics")))
    _req(bool(STATE_CODE_RE.fullmatch(str(payload.get("state_code", "")))), "PAYLOAD_STATE_CODE_INVALID", str(payload.get("state_code")))
    _req(payload.get("method_family") in METHOD_FAMILIES, "PAYLOAD_METHOD_FAMILY_INVALID", str(payload.get("method_family")))
    _req(payload.get("horizon_label") in HORIZON_LABELS, "PAYLOAD_HORIZON_INVALID", str(payload.get("horizon_label")))
    _req(_valid_sha(payload.get("thesis_content_sha256")), "PAYLOAD_CONTENT_SHA_INVALID", str(payload.get("thesis_content_sha256")))

    _req(payload.get("external_snapshot_reused_only") is True, "PAYLOAD_REUSE_GUARD_INVALID", "external_snapshot_reused_only")

    for field in (
        "state_code_semantics_interpreted",
        "text_claims_ingested",
        "target_prices_ingested",
        "confidence_scores_ingested",
        "producer_network_fetch_executed",
        "producer_model_execution_executed",
        "market_data_input_used",
        "future_outcomes_used",
        "directional_semantics",
        "signal_semantics",
        "composite_score_assigned",
        "candidate_modification_semantics",
        "primary_rule_modification_semantics",
    ):
        _req(payload.get(field) is False, "FORBIDDEN_PAYLOAD_SEMANTIC_ENABLED", field)

    return {
        "status": "AVAILABLE",
        "state_code": payload["state_code"],
        "method_family": payload["method_family"],
        "horizon_label": payload["horizon_label"],
        "retrospective_policy_floor_applied": bool(payload["retrospective_policy_floor_applied"]),
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
    components = {str(item["feature_id"]): _placeholder(item) for item in FEATURE_REGISTRY}
    components[FEATURE_ID] = dict(component)
    pack = build_context_feature_pack_v1(
        observation_descriptor=observation_descriptor,
        components=components,
        pack_id="PACK_COMPATIBILITY_CHECK_ONLY",
    )
    feature = next(x for x in pack["features"] if x["feature_id"] == FEATURE_ID)
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
    _req(path.is_file() and not path.is_symlink(), "PACKAGE_MANIFEST_MISSING", str(path))
    lines = [x for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]
    _req(len(lines) == 2, "PACKAGE_MANIFEST_ENTRY_COUNT_INVALID", str(len(lines)))
    expected_names = {CHECKS_FILENAME, COMPONENT_FILENAME}
    seen = set()
    for line in lines:
        parts = line.split("  ", 1)
        _req(len(parts) == 2 and len(parts[0]) == 64, "PACKAGE_MANIFEST_LINE_INVALID", line)
        digest, name = parts
        _req(name in expected_names, "PACKAGE_MANIFEST_SCOPE_INVALID", name)
        target = directory / name
        _req(target.is_file() and not target.is_symlink(), "PACKAGE_MANIFEST_PAYLOAD_MISSING", name)
        _req(_sha(target) == digest, "PACKAGE_MANIFEST_HASH_MISMATCH", name)
        seen.add(name)
    _req(seen == expected_names, "PACKAGE_MANIFEST_SCOPE_INVALID", str(sorted(seen)))
    return len(lines)


def validate_external_thesis_model_card_v1_package(
    directory: Path | str,
) -> dict[str, Any]:
    root = Path(directory).resolve()
    _req(root.is_dir() and not root.is_symlink(), "PACKAGE_DIRECTORY_INVALID", str(root))
    entries = _validate_manifest(root)
    component = _read_json(root / COMPONENT_FILENAME, "PACKAGE_COMPONENT_INVALID")
    checks = _read_json(root / CHECKS_FILENAME, "PACKAGE_CHECKS_INVALID")
    result = validate_external_thesis_model_card_v1_component(component)
    _req(checks.get("package_schema_version") == PACKAGE_SCHEMA_VERSION, "PACKAGE_SCHEMA_INVALID", str(checks.get("package_schema_version")))
    _req(checks.get("feature_id") == FEATURE_ID, "PACKAGE_FEATURE_ID_INVALID", str(checks.get("feature_id")))

    for field in (
        "real_network_request_executed",
        "external_model_fetched_by_producer",
        "external_model_executed_by_producer",
        "market_data_input_used",
        "future_outcomes_used",
        "direction_inferred",
        "signal_generated",
        "candidate_modified",
        "primary_rule_modified",
        "official_append_executed",
        "official_dataset_changed",
        "official_manifest_changed",
    ):
        _req(checks.get(field) is False, "PACKAGE_CHECK_INVALID", field)

    return {
        **result,
        "manifest_entries": entries,
        "point_in_time_eligible_under_pack_policy": bool(checks["point_in_time_eligible_under_pack_policy"]),
    }


def prepare_external_thesis_model_card_v1_package(
    *,
    repo_root: Path | str,
    observation_descriptor_json: Path | str,
    external_snapshot_json: Path | str,
    output_directory: Path | str,
    produced_at_utc: str,
    authorization: str | None = None,
) -> dict[str, Any]:
    _req(authorization == PACKAGE_AUTHORIZATION, "PACKAGE_AUTHORIZATION_REQUIRED", "authorization")
    _gate_off()

    repo = Path(repo_root).resolve()
    descriptor_path = Path(observation_descriptor_json).resolve()
    snapshot_path = Path(external_snapshot_json).resolve()
    output = Path(output_directory).resolve()

    _req((repo / ".git").is_dir(), "REPOSITORY_ROOT_INVALID", str(repo))
    _req(not _inside(output, repo), "OUTPUT_INSIDE_REPOSITORY_PROHIBITED", str(output))
    _req(output.parent.is_dir() and not output.parent.is_symlink(), "OUTPUT_PARENT_INVALID", str(output.parent))
    _req(not output.exists() and not output.is_symlink(), "OUTPUT_ALREADY_EXISTS", str(output))
    _req(not _inside(descriptor_path, repo), "DESCRIPTOR_INSIDE_REPOSITORY_PROHIBITED", str(descriptor_path))
    _req(not _inside(snapshot_path, repo), "EXTERNAL_SNAPSHOT_INSIDE_REPOSITORY_PROHIBITED", str(snapshot_path))

    official_before = _official(repo)
    descriptor = _read_json(descriptor_path, "DESCRIPTOR_FILE_INVALID")
    snapshot = _read_json(snapshot_path, "EXTERNAL_SNAPSHOT_FILE_INVALID")
    policy, policy_sha = load_external_thesis_model_card_policy_v1(repo)

    component = build_external_thesis_model_card_v1_component(
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

    _req(_official(repo) == official_before, "OFFICIAL_ARTIFACT_CHANGED", "before output")
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
            "point_in_time_eligible_under_pack_policy": compatibility["point_in_time_eligible"],
            "pack_eligibility_reason": compatibility["eligibility_reason"],
            "external_snapshot_was_preexisting": True,
            "external_snapshot_validated_locally": True,
            "real_network_request_executed": False,
            "external_model_fetched_by_producer": False,
            "external_model_executed_by_producer": False,
            "market_data_input_used": False,
            "future_outcomes_used": False,
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
        validate_external_thesis_model_card_v1_package(temp)
        temp.rename(output)
    except Exception:
        if temp.exists():
            shutil.rmtree(temp, ignore_errors=True)
        if output.exists():
            shutil.rmtree(output, ignore_errors=True)
        raise

    _req(_official(repo) == official_before, "OFFICIAL_ARTIFACT_CHANGED", "after output")
    _gate_off()
    result = validate_external_thesis_model_card_v1_package(output)

    return {
        "capability": CAPABILITY,
        "feature_id": FEATURE_ID,
        "output_directory": str(output),
        "component_status": result["status"],
        "state_code": result["state_code"],
        "point_in_time_eligible_under_pack_policy": result["point_in_time_eligible_under_pack_policy"],
        "real_network_request_executed": False,
        "external_model_fetched_by_producer": False,
        "external_model_executed_by_producer": False,
        "market_data_input_used": False,
        "official_append_executed": False,
    }
