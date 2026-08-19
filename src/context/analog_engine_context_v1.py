from __future__ import annotations

import hashlib
import json
import math
import os
import shutil
import statistics
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence

from src.context.context_feature_pack_v1_level_a_standard import (
    FEATURE_REGISTRY,
    build_context_feature_pack_v1,
)

CAPABILITY = "ANALOG_ENGINE_CONTEXT_V1"
FEATURE_ID = CAPABILITY
FEATURE_SCHEMA_VERSION = "ANALOG_ENGINE_CONTEXT_V1_SCHEMA_V1"
PACKAGE_SCHEMA_VERSION = "ANALOG_ENGINE_CONTEXT_V1_PACKAGE_V1"
QUERY_SCHEMA_VERSION = "ANALOG_QUERY_VECTOR_SNAPSHOT_V1"
LIBRARY_SCHEMA_VERSION = "ANALOG_REFERENCE_LIBRARY_SNAPSHOT_V1"
SOURCE_KIND = "MODEL_DERIVED"
PACKAGE_AUTHORIZATION = "PREPARE_ANALOG_ENGINE_CONTEXT_V1"

MAX_IMPLEMENTATION_OR_REPAIR_ATTEMPTS = 10
IMPLEMENTATION_OR_REPAIR_ATTEMPT = 1

POLICY_PATH = Path("src/context/resources/analog_engine_context_policy_v1.json")
EXPECTED_POLICY_SCHEMA_VERSION = "ANALOG_ENGINE_CONTEXT_POLICY_V1"

COMPONENT_FILENAME = "analog_engine_context_component.json"
CHECKS_FILENAME = "producer_checks.json"
MANIFEST_FILENAME = "manifest.sha256"

OFFICIAL_APPEND_GATE_NAME = "TRADING_AI_OFFICIAL_LONG_EVIDENCE_APPEND_ALLOWED"
OFFICIAL_DATASET = Path("data/forward/long_forward_observation_dataset_v1.csv")
OFFICIAL_MANIFEST = Path("data/forward/long_forward_observation_dataset_v1.manifest.csv")
OFFICIAL_LOCK = Path("data/forward/long_forward_observation_dataset_v1.lock")

PROHIBITED_OUTCOME_KEYS = frozenset(
    {
        "outcome", "future_outcome", "forward_return", "return", "mfe", "mae",
        "pnl", "profit", "loss", "target_hit", "stop_hit", "winner", "loser",
        "label",
    }
)


class AnalogEngineContextError(RuntimeError):
    def __init__(self, code: str, message: str) -> None:
        self.code = code
        super().__init__(message)


def _req(ok: bool, code: str, message: str) -> None:
    if not ok:
        raise AnalogEngineContextError(code, message)


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
        raise AnalogEngineContextError("TIMESTAMP_INVALID", field) from exc
    _req(dt.tzinfo is not None, "TIMESTAMP_TIMEZONE_REQUIRED", field)
    return dt.astimezone(timezone.utc)


def _utc(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).isoformat()


def _read_json(path: Path, code: str) -> dict[str, Any]:
    _req(path.is_file() and not path.is_symlink(), code, str(path))
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise AnalogEngineContextError(code, str(path)) from exc
    _req(isinstance(value, Mapping), code, str(path))
    return dict(value)


def _write_json_new(path: Path, value: Any) -> None:
    payload = (
        json.dumps(
            value, sort_keys=True, separators=(",", ":"), ensure_ascii=True,
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


def _finite_vector(value: Any, expected_len: int, field: str) -> tuple[float, ...]:
    _req(
        isinstance(value, Sequence) and not isinstance(value, (str, bytes)),
        "VECTOR_INVALID",
        field,
    )
    _req(len(value) == expected_len, "VECTOR_LENGTH_INVALID", field)
    result = []
    for item in value:
        try:
            number = float(item)
        except (TypeError, ValueError) as exc:
            raise AnalogEngineContextError("VECTOR_VALUE_INVALID", field) from exc
        _req(math.isfinite(number), "VECTOR_VALUE_INVALID", field)
        result.append(number)
    return tuple(result)


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


def validate_analog_engine_context_policy_v1(
    policy: Mapping[str, Any],
) -> dict[str, Any]:
    _req(isinstance(policy, Mapping), "POLICY_INVALID", "mapping required")
    _req(policy.get("schema_version") == EXPECTED_POLICY_SCHEMA_VERSION, "POLICY_SCHEMA_INVALID", str(policy.get("schema_version")))
    _req(policy.get("feature_id") == FEATURE_ID, "POLICY_FEATURE_ID_INVALID", str(policy.get("feature_id")))
    _req(policy.get("query_snapshot_schema_version") == QUERY_SCHEMA_VERSION, "POLICY_QUERY_SCHEMA_INVALID", str(policy.get("query_snapshot_schema_version")))
    _req(policy.get("library_snapshot_schema_version") == LIBRARY_SCHEMA_VERSION, "POLICY_LIBRARY_SCHEMA_INVALID", str(policy.get("library_snapshot_schema_version")))
    _req(policy.get("distance_metric") == "EUCLIDEAN_PRESTANDARDIZED_VECTOR", "POLICY_DISTANCE_INVALID", str(policy.get("distance_metric")))
    _req(policy.get("top_k") == 5, "POLICY_TOP_K_INVALID", str(policy.get("top_k")))
    _req(policy.get("min_feature_count") == 2, "POLICY_MIN_FEATURE_INVALID", str(policy.get("min_feature_count")))
    _req(policy.get("max_feature_count") == 32, "POLICY_MAX_FEATURE_INVALID", str(policy.get("max_feature_count")))
    _req(policy.get("min_library_rows") == 5, "POLICY_MIN_LIBRARY_INVALID", str(policy.get("min_library_rows")))
    _req(policy.get("max_library_rows") == 10000, "POLICY_MAX_LIBRARY_INVALID", str(policy.get("max_library_rows")))

    effective = _parse_utc(policy.get("policy_effective_from_utc"), "policy_effective_from_utc")

    for field in (
        "exact_feature_space_match_required",
        "exact_query_observation_match_required",
        "historical_reference_strictly_before_query_required",
        "feature_information_cutoff_not_after_reference_required",
        "normalization_fit_cutoff_not_after_query_reference_required",
    ):
        _req(policy.get(field) is True, "POLICY_REQUIRED_GUARD_INVALID", field)

    for field in (
        "outcome_fields_allowed",
        "future_rows_allowed",
        "producer_network_fetch_allowed",
        "producer_model_training_allowed",
        "producer_market_data_fetch_allowed",
        "directional_meaning_assigned",
        "analog_vote_allowed",
        "composite_score_assigned",
        "signal_semantics",
        "future_outcomes_used",
    ):
        _req(policy.get(field) is False, "POLICY_FORBIDDEN_SEMANTIC_ENABLED", field)

    return {
        "policy_effective_from_utc": _utc(effective),
        "distance_metric": "EUCLIDEAN_PRESTANDARDIZED_VECTOR",
        "top_k": 5,
        "min_feature_count": 2,
        "max_feature_count": 32,
        "min_library_rows": 5,
        "max_library_rows": 10000,
    }


def load_analog_engine_context_policy_v1(
    repo_root: Path | str,
) -> tuple[dict[str, Any], str]:
    repo = Path(repo_root).resolve()
    path = repo / POLICY_PATH
    policy = _read_json(path, "POLICY_FILE_INVALID")
    validate_analog_engine_context_policy_v1(policy)
    return policy, _sha(path)


def _validate_feature_names(value: Any, policy: Mapping[str, Any]) -> tuple[str, ...]:
    _req(
        isinstance(value, Sequence) and not isinstance(value, (str, bytes)),
        "FEATURE_NAMES_INVALID",
        "feature_names",
    )
    names = tuple(str(item) for item in value)
    _req(
        policy["min_feature_count"] <= len(names) <= policy["max_feature_count"],
        "FEATURE_COUNT_INVALID",
        str(len(names)),
    )
    _req(len(set(names)) == len(names), "FEATURE_NAMES_DUPLICATE", str(names))
    for name in names:
        _req(bool(name.strip()), "FEATURE_NAME_INVALID", name)
    return names


def validate_analog_query_vector_snapshot_v1(
    snapshot: Mapping[str, Any],
    *,
    policy: Mapping[str, Any],
) -> dict[str, Any]:
    _assert_no_outcome_keys(snapshot)
    _req(snapshot.get("snapshot_schema_version") == QUERY_SCHEMA_VERSION, "QUERY_SCHEMA_INVALID", str(snapshot.get("snapshot_schema_version")))
    _req(_valid_sha(snapshot.get("feature_space_sha256")), "QUERY_FEATURE_SPACE_SHA_INVALID", str(snapshot.get("feature_space_sha256")))
    names = _validate_feature_names(snapshot.get("feature_names"), policy)
    vector = _finite_vector(snapshot.get("vector"), len(names), "query.vector")
    reference = _parse_utc(snapshot.get("reference_boundary_utc"), "query.reference_boundary_utc")
    info = _parse_utc(snapshot.get("feature_information_cutoff_utc"), "query.feature_information_cutoff_utc")
    created = _parse_utc(snapshot.get("snapshot_created_at_utc"), "query.snapshot_created_at_utc")
    _req(info <= reference, "QUERY_INFORMATION_AFTER_REFERENCE", _utc(info))
    _req(info <= created, "QUERY_INFORMATION_AFTER_SNAPSHOT_CREATED", _utc(info))
    observation_id = str(snapshot.get("observation_id", ""))
    _req(bool(observation_id.strip()), "QUERY_OBSERVATION_ID_INVALID", observation_id)
    return {
        "feature_names": names,
        "vector": vector,
        "reference_boundary_utc": _utc(reference),
        "feature_information_cutoff_utc": _utc(info),
        "snapshot_created_at_utc": _utc(created),
        "feature_space_sha256": str(snapshot["feature_space_sha256"]),
        "observation_id": observation_id,
    }


def validate_analog_reference_library_snapshot_v1(
    snapshot: Mapping[str, Any],
    *,
    policy: Mapping[str, Any],
) -> dict[str, Any]:
    _assert_no_outcome_keys(snapshot)
    _req(snapshot.get("snapshot_schema_version") == LIBRARY_SCHEMA_VERSION, "LIBRARY_SCHEMA_INVALID", str(snapshot.get("snapshot_schema_version")))
    _req(_valid_sha(snapshot.get("feature_space_sha256")), "LIBRARY_FEATURE_SPACE_SHA_INVALID", str(snapshot.get("feature_space_sha256")))

    names = _validate_feature_names(snapshot.get("feature_names"), policy)
    created = _parse_utc(snapshot.get("snapshot_created_at_utc"), "library.snapshot_created_at_utc")
    fit_cutoff = _parse_utc(
        snapshot.get("normalization_fit_information_cutoff_utc"),
        "library.normalization_fit_information_cutoff_utc",
    )

    rows = snapshot.get("rows")
    _req(isinstance(rows, list), "LIBRARY_ROWS_INVALID", "rows")
    _req(
        policy["min_library_rows"] <= len(rows) <= policy["max_library_rows"],
        "LIBRARY_ROW_COUNT_INVALID",
        str(len(rows)),
    )

    parsed_rows = []
    seen = set()
    previous_key = None

    for row in rows:
        _req(isinstance(row, Mapping), "LIBRARY_ROW_INVALID", str(row))
        observation_id = str(row.get("observation_id", ""))
        _req(bool(observation_id.strip()), "LIBRARY_OBSERVATION_ID_INVALID", observation_id)
        _req(observation_id not in seen, "LIBRARY_OBSERVATION_ID_DUPLICATE", observation_id)
        seen.add(observation_id)

        reference = _parse_utc(row.get("reference_boundary_utc"), "library.reference_boundary_utc")
        info = _parse_utc(row.get("feature_information_cutoff_utc"), "library.feature_information_cutoff_utc")
        _req(info <= reference, "LIBRARY_INFORMATION_AFTER_REFERENCE", observation_id)

        vector = _finite_vector(row.get("vector"), len(names), f"library.{observation_id}.vector")

        key = (_utc(reference), observation_id)
        _req(
            previous_key is None or key > previous_key,
            "LIBRARY_ROWS_NOT_STRICTLY_ORDERED",
            observation_id,
        )
        previous_key = key

        parsed_rows.append(
            {
                "observation_id": observation_id,
                "reference_boundary_utc": _utc(reference),
                "feature_information_cutoff_utc": _utc(info),
                "vector": vector,
            }
        )

    latest_row_information = max(
        _parse_utc(row["feature_information_cutoff_utc"], "library.row_information")
        for row in parsed_rows
    )
    _req(
        latest_row_information <= created,
        "LIBRARY_INFORMATION_AFTER_SNAPSHOT_CREATED",
        _utc(latest_row_information),
    )
    _req(
        fit_cutoff <= created,
        "NORMALIZATION_FIT_AFTER_LIBRARY_SNAPSHOT_CREATED",
        _utc(fit_cutoff),
    )

    return {
        "feature_names": names,
        "feature_space_sha256": str(snapshot["feature_space_sha256"]),
        "snapshot_created_at_utc": _utc(created),
        "normalization_fit_information_cutoff_utc": _utc(fit_cutoff),
        "rows": parsed_rows,
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


def _distance(a: Sequence[float], b: Sequence[float]) -> float:
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))


def build_analog_engine_context_v1_component(
    *,
    observation_descriptor: Mapping[str, Any],
    query_snapshot: Mapping[str, Any],
    query_snapshot_sha256: str,
    library_snapshot: Mapping[str, Any],
    library_snapshot_sha256: str,
    policy: Mapping[str, Any],
    policy_sha256: str,
    produced_at_utc: str,
) -> dict[str, Any]:
    descriptor = _validate_descriptor(observation_descriptor)
    p = validate_analog_engine_context_policy_v1(policy)
    q = validate_analog_query_vector_snapshot_v1(query_snapshot, policy=p)
    library = validate_analog_reference_library_snapshot_v1(library_snapshot, policy=p)

    for digest, code in (
        (query_snapshot_sha256, "QUERY_SHA_INVALID"),
        (library_snapshot_sha256, "LIBRARY_SHA_INVALID"),
        (policy_sha256, "POLICY_SHA_INVALID"),
    ):
        _req(_valid_sha(digest), code, digest)

    descriptor_reference = _parse_utc(descriptor["reference_boundary_utc"], "reference_boundary_utc")
    query_reference = _parse_utc(q["reference_boundary_utc"], "query.reference_boundary_utc")
    _req(query_reference == descriptor_reference, "QUERY_REFERENCE_MISMATCH", _utc(query_reference))
    _req(q["observation_id"] == descriptor["observation_id"], "QUERY_OBSERVATION_ID_MISMATCH", q["observation_id"])

    _req(q["feature_space_sha256"] == library["feature_space_sha256"], "FEATURE_SPACE_SHA_MISMATCH", "query/library")
    _req(tuple(q["feature_names"]) == tuple(library["feature_names"]), "FEATURE_NAMES_MISMATCH", "query/library")

    fit_cutoff = _parse_utc(
        library["normalization_fit_information_cutoff_utc"],
        "normalization_fit_information_cutoff_utc",
    )
    _req(
        fit_cutoff <= query_reference,
        "NORMALIZATION_FIT_AFTER_QUERY_REFERENCE",
        _utc(fit_cutoff),
    )

    candidates = []
    row_info_times = []

    for row in library["rows"]:
        row_reference = _parse_utc(row["reference_boundary_utc"], "row.reference_boundary_utc")
        _req(row_reference < query_reference, "FUTURE_OR_CURRENT_ANALOG_ROW", row["observation_id"])
        _req(row["observation_id"] != q["observation_id"], "QUERY_PRESENT_IN_LIBRARY", row["observation_id"])
        distance = _distance(q["vector"], row["vector"])
        _req(math.isfinite(distance), "DISTANCE_INVALID", row["observation_id"])
        row_info_times.append(
            _parse_utc(row["feature_information_cutoff_utc"], "row.feature_information_cutoff_utc")
        )
        candidates.append(
            {
                "observation_id": row["observation_id"],
                "reference_boundary_utc": row["reference_boundary_utc"],
                "distance": distance,
            }
        )

    candidates.sort(
        key=lambda item: (
            item["distance"],
            item["reference_boundary_utc"],
            item["observation_id"],
        )
    )
    selected = candidates[: p["top_k"]]
    _req(len(selected) == p["top_k"], "INSUFFICIENT_ANALOGS_AFTER_FILTERING", str(len(selected)))

    query_info = _parse_utc(q["feature_information_cutoff_utc"], "query.feature_information_cutoff_utc")
    information_cutoff = max([query_info, fit_cutoff] + row_info_times)

    query_created = _parse_utc(q["snapshot_created_at_utc"], "query.snapshot_created_at_utc")
    library_created = _parse_utc(library["snapshot_created_at_utc"], "library.snapshot_created_at_utc")
    policy_effective = _parse_utc(p["policy_effective_from_utc"], "policy_effective_from_utc")
    available = max(query_created, library_created, policy_effective, information_cutoff)

    produced = _parse_utc(produced_at_utc, "produced_at_utc")
    _req(produced >= available, "PRODUCED_BEFORE_FEATURE_AVAILABLE", _utc(produced))

    distances = [item["distance"] for item in selected]

    payload = {
        "model_semantics": "HISTORICAL_ANALOG_DISTANCE_ONLY",
        "distance_metric": p["distance_metric"],
        "top_k": p["top_k"],
        "feature_space_sha256": q["feature_space_sha256"],
        "feature_count": len(q["feature_names"]),
        "library_row_count": len(library["rows"]),
        "normalization_fit_information_cutoff_utc": library[
            "normalization_fit_information_cutoff_utc"
        ],
        "query_reference_boundary_utc": q["reference_boundary_utc"],
        "query_feature_information_cutoff_utc": q["feature_information_cutoff_utc"],
        "selected_analogs": selected,
        "nearest_distance": min(distances),
        "median_selected_distance": statistics.median(distances),
        "query_snapshot_reused_only": True,
        "library_snapshot_reused_only": True,
        "producer_network_fetch_executed": False,
        "producer_market_data_fetch_executed": False,
        "producer_model_training_executed": False,
        "outcome_fields_used": False,
        "future_rows_used": False,
        "future_outcomes_used": False,
        "analog_vote_performed": False,
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
        "source_artifact_sha256": library_snapshot_sha256,
        "payload": payload,
    }

    validate_analog_engine_context_v1_component(component)
    return component


def validate_analog_engine_context_v1_component(
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
    _req(payload.get("model_semantics") == "HISTORICAL_ANALOG_DISTANCE_ONLY", "PAYLOAD_SEMANTICS_INVALID", str(payload.get("model_semantics")))
    _req(payload.get("distance_metric") == "EUCLIDEAN_PRESTANDARDIZED_VECTOR", "PAYLOAD_DISTANCE_INVALID", str(payload.get("distance_metric")))
    _req(payload.get("top_k") == 5, "PAYLOAD_TOP_K_INVALID", str(payload.get("top_k")))
    selected = payload.get("selected_analogs")
    _req(isinstance(selected, list) and len(selected) == 5, "PAYLOAD_ANALOG_COUNT_INVALID", str(selected))

    for item in selected:
        _req(set(item) == {"observation_id", "reference_boundary_utc", "distance"}, "PAYLOAD_ANALOG_FIELDS_INVALID", str(sorted(item)))
        _req(math.isfinite(float(item["distance"])) and float(item["distance"]) >= 0, "PAYLOAD_DISTANCE_VALUE_INVALID", str(item))

    for field in ("query_snapshot_reused_only", "library_snapshot_reused_only"):
        _req(payload.get(field) is True, "PAYLOAD_REUSE_GUARD_INVALID", field)

    for field in (
        "producer_network_fetch_executed",
        "producer_market_data_fetch_executed",
        "producer_model_training_executed",
        "outcome_fields_used",
        "future_rows_used",
        "future_outcomes_used",
        "analog_vote_performed",
        "directional_semantics",
        "signal_semantics",
        "composite_score_assigned",
        "candidate_modification_semantics",
        "primary_rule_modification_semantics",
    ):
        _req(payload.get(field) is False, "FORBIDDEN_PAYLOAD_SEMANTIC_ENABLED", field)

    return {
        "status": "AVAILABLE",
        "analog_count": 5,
        "nearest_distance": float(payload["nearest_distance"]),
        "median_selected_distance": float(payload["median_selected_distance"]),
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


def validate_analog_engine_context_v1_package(
    directory: Path | str,
) -> dict[str, Any]:
    root = Path(directory).resolve()
    _req(root.is_dir() and not root.is_symlink(), "PACKAGE_DIRECTORY_INVALID", str(root))
    entries = _validate_manifest(root)
    component = _read_json(root / COMPONENT_FILENAME, "PACKAGE_COMPONENT_INVALID")
    checks = _read_json(root / CHECKS_FILENAME, "PACKAGE_CHECKS_INVALID")
    result = validate_analog_engine_context_v1_component(component)

    _req(checks.get("package_schema_version") == PACKAGE_SCHEMA_VERSION, "PACKAGE_SCHEMA_INVALID", str(checks.get("package_schema_version")))
    _req(checks.get("feature_id") == FEATURE_ID, "PACKAGE_FEATURE_ID_INVALID", str(checks.get("feature_id")))

    for field in (
        "real_network_request_executed",
        "market_data_fetched_by_producer",
        "model_training_executed",
        "future_outcomes_used",
        "analog_vote_performed",
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
        "point_in_time_eligible_under_pack_policy": bool(
            checks["point_in_time_eligible_under_pack_policy"]
        ),
    }


def prepare_analog_engine_context_v1_package(
    *,
    repo_root: Path | str,
    observation_descriptor_json: Path | str,
    query_snapshot_json: Path | str,
    library_snapshot_json: Path | str,
    output_directory: Path | str,
    produced_at_utc: str,
    authorization: str | None = None,
) -> dict[str, Any]:
    _req(authorization == PACKAGE_AUTHORIZATION, "PACKAGE_AUTHORIZATION_REQUIRED", "authorization")
    _gate_off()

    repo = Path(repo_root).resolve()
    descriptor_path = Path(observation_descriptor_json).resolve()
    query_path = Path(query_snapshot_json).resolve()
    library_path = Path(library_snapshot_json).resolve()
    output = Path(output_directory).resolve()

    _req((repo / ".git").is_dir(), "REPOSITORY_ROOT_INVALID", str(repo))
    _req(not _inside(output, repo), "OUTPUT_INSIDE_REPOSITORY_PROHIBITED", str(output))
    _req(output.parent.is_dir() and not output.parent.is_symlink(), "OUTPUT_PARENT_INVALID", str(output.parent))
    _req(not output.exists() and not output.is_symlink(), "OUTPUT_ALREADY_EXISTS", str(output))

    for path, code in (
        (descriptor_path, "DESCRIPTOR_INSIDE_REPOSITORY_PROHIBITED"),
        (query_path, "QUERY_INSIDE_REPOSITORY_PROHIBITED"),
        (library_path, "LIBRARY_INSIDE_REPOSITORY_PROHIBITED"),
    ):
        _req(not _inside(path, repo), code, str(path))

    official_before = _official(repo)

    descriptor = _read_json(descriptor_path, "DESCRIPTOR_FILE_INVALID")
    query = _read_json(query_path, "QUERY_FILE_INVALID")
    library = _read_json(library_path, "LIBRARY_FILE_INVALID")
    policy, policy_sha = load_analog_engine_context_policy_v1(repo)

    component = build_analog_engine_context_v1_component(
        observation_descriptor=descriptor,
        query_snapshot=query,
        query_snapshot_sha256=_sha(query_path),
        library_snapshot=library,
        library_snapshot_sha256=_sha(library_path),
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
            "query_snapshot_sha256": _sha(query_path),
            "library_snapshot_sha256": _sha(library_path),
            "policy_resource_sha256": policy_sha,
            "point_in_time_eligible_under_pack_policy": compatibility["point_in_time_eligible"],
            "pack_eligibility_reason": compatibility["eligibility_reason"],
            "real_network_request_executed": False,
            "market_data_fetched_by_producer": False,
            "model_training_executed": False,
            "future_outcomes_used": False,
            "analog_vote_performed": False,
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
        validate_analog_engine_context_v1_package(temp)
        temp.rename(output)
    except Exception:
        if temp.exists():
            shutil.rmtree(temp, ignore_errors=True)
        if output.exists():
            shutil.rmtree(output, ignore_errors=True)
        raise

    _req(_official(repo) == official_before, "OFFICIAL_ARTIFACT_CHANGED", "after output")
    _gate_off()

    result = validate_analog_engine_context_v1_package(output)

    return {
        "capability": CAPABILITY,
        "feature_id": FEATURE_ID,
        "output_directory": str(output),
        "component_status": result["status"],
        "analog_count": result["analog_count"],
        "point_in_time_eligible_under_pack_policy": result[
            "point_in_time_eligible_under_pack_policy"
        ],
        "real_network_request_executed": False,
        "market_data_fetched_by_producer": False,
        "model_training_executed": False,
        "official_append_executed": False,
    }
