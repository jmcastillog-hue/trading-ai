from __future__ import annotations

import hashlib
import json
import os
import shutil
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence

from src.context.context_feature_pack_v1_level_a_standard import (
    FEATURE_REGISTRY,
    build_context_feature_pack_v1,
)

CAPABILITY = "EVENT_RISK_CALENDAR_CONTEXT_V1"
FEATURE_ID = "EVENT_RISK_CALENDAR_CONTEXT_V1"
FEATURE_SCHEMA_VERSION = "EVENT_RISK_CALENDAR_CONTEXT_V1_SCHEMA_V1"
PACKAGE_SCHEMA_VERSION = "EVENT_RISK_CALENDAR_CONTEXT_V1_PACKAGE_V1"
SNAPSHOT_SCHEMA_VERSION = "EVENT_RISK_CALENDAR_SNAPSHOT_V1"
SOURCE_KIND = "DETERMINISTIC"

PACKAGE_AUTHORIZATION = "PREPARE_EVENT_RISK_CALENDAR_CONTEXT_V1"

MAX_IMPLEMENTATION_OR_REPAIR_ATTEMPTS = 10
IMPLEMENTATION_OR_REPAIR_ATTEMPT = 1

TAXONOMY_PATH = Path(
    "src/context/resources/event_risk_calendar_taxonomy_v1.json"
)
EXPECTED_TAXONOMY_SCHEMA_VERSION = "EVENT_RISK_CALENDAR_TAXONOMY_V1"

COMPONENT_FILENAME = "event_risk_calendar_context_component.json"
CHECKS_FILENAME = "producer_checks.json"
MANIFEST_FILENAME = "manifest.sha256"

OFFICIAL_APPEND_GATE_NAME = "TRADING_AI_OFFICIAL_LONG_EVIDENCE_APPEND_ALLOWED"
OFFICIAL_DATASET = Path("data/forward/long_forward_observation_dataset_v1.csv")
OFFICIAL_MANIFEST = Path(
    "data/forward/long_forward_observation_dataset_v1.manifest.csv"
)
OFFICIAL_LOCK = Path("data/forward/long_forward_observation_dataset_v1.lock")

FUTURE_WINDOWS_SECONDS = {
    "1h": 3600,
    "6h": 6 * 3600,
    "24h": 24 * 3600,
    "72h": 72 * 3600,
    "7d": 7 * 24 * 3600,
}
RECENT_WINDOWS_SECONDS = {
    "1h": 3600,
    "6h": 6 * 3600,
    "24h": 24 * 3600,
}

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


class EventRiskCalendarContextError(RuntimeError):
    def __init__(self, code: str, message: str) -> None:
        self.code = code
        super().__init__(message)


def _req(ok: bool, code: str, message: str) -> None:
    if not ok:
        raise EventRiskCalendarContextError(code, message)


def _sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


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


def _parse_utc(value: Any, field: str) -> datetime:
    text = str(value).strip().replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError as exc:
        raise EventRiskCalendarContextError(
            "TIMESTAMP_INVALID",
            field,
        ) from exc
    _req(
        parsed.tzinfo is not None,
        "TIMESTAMP_TIMEZONE_REQUIRED",
        field,
    )
    return parsed.astimezone(timezone.utc)


def _utc(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat()


def _official_gate_off() -> None:
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


def _read_json_mapping(path: Path, code: str) -> dict[str, Any]:
    _req(
        path.is_file() and not path.is_symlink(),
        code,
        str(path),
    )
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise EventRiskCalendarContextError(
            code,
            str(path),
        ) from exc
    _req(
        isinstance(value, Mapping),
        code,
        str(path),
    )
    return dict(value)


def validate_event_risk_taxonomy_v1(
    taxonomy: Mapping[str, Any],
) -> dict[str, Any]:
    _req(
        isinstance(taxonomy, Mapping),
        "TAXONOMY_INVALID",
        "mapping required",
    )
    _req(
        taxonomy.get("schema_version")
        == EXPECTED_TAXONOMY_SCHEMA_VERSION,
        "TAXONOMY_SCHEMA_INVALID",
        str(taxonomy.get("schema_version")),
    )
    _req(
        taxonomy.get("semantics")
        == "DESCRIPTIVE_SCHEDULED_EVENT_PROXIMITY_ONLY",
        "TAXONOMY_SEMANTICS_INVALID",
        str(taxonomy.get("semantics")),
    )

    event_types = taxonomy.get("event_types")
    _req(
        isinstance(event_types, list)
        and len(event_types) == 8,
        "TAXONOMY_EVENT_TYPE_COUNT_INVALID",
        str(len(event_types) if isinstance(event_types, list) else None),
    )

    expected_types = (
        "FOMC_RATE_DECISION",
        "FOMC_MINUTES",
        "US_CPI",
        "US_PPI",
        "US_NONFARM_PAYROLLS",
        "US_CORE_PCE",
        "US_GDP_ADVANCE",
        "US_RETAIL_SALES",
    )

    actual_types = tuple(
        str(item.get("event_type", ""))
        for item in event_types
    )
    _req(
        actual_types == expected_types,
        "TAXONOMY_EVENT_TYPES_INVALID",
        str(actual_types),
    )
    _req(
        len(set(actual_types)) == len(actual_types),
        "TAXONOMY_EVENT_TYPES_DUPLICATED",
        str(actual_types),
    )

    for item in event_types:
        _req(
            isinstance(item, Mapping)
            and str(item.get("authority_family", "")).strip() != "",
            "TAXONOMY_AUTHORITY_FAMILY_INVALID",
            str(item),
        )

    for field in (
        "directional_meaning_assigned",
        "importance_score_assigned",
        "event_surprise_used",
        "market_reaction_used",
    ):
        _req(
            taxonomy.get(field) is False,
            "TAXONOMY_FORBIDDEN_SEMANTIC_ENABLED",
            field,
        )

    return {
        "event_type_count": len(actual_types),
        "event_types": list(actual_types),
        "directional_meaning_assigned": False,
        "importance_score_assigned": False,
    }


def load_event_risk_taxonomy_v1(
    repo_root: Path | str,
) -> tuple[dict[str, Any], str]:
    repo = Path(repo_root).resolve()
    path = repo / TAXONOMY_PATH
    taxonomy = _read_json_mapping(
        path,
        "TAXONOMY_FILE_INVALID",
    )
    validate_event_risk_taxonomy_v1(taxonomy)
    return taxonomy, _sha(path)


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
        == "FORWARD_OUTCOME_OBSERVATION_DESCRIPTOR_V1",
        "OBSERVATION_DESCRIPTOR_SCHEMA_INVALID",
        str(descriptor.get("observation_descriptor_schema_version")),
    )
    _req(
        descriptor.get("symbol") == "BTCUSDT",
        "OBSERVATION_SYMBOL_INVALID",
        str(descriptor.get("symbol")),
    )
    _req(
        descriptor.get("timeframe") == "15m",
        "OBSERVATION_TIMEFRAME_INVALID",
        str(descriptor.get("timeframe")),
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
    context_cutoff = _parse_utc(
        descriptor.get("synchronized_context_available_at_utc"),
        "synchronized_context_available_at_utc",
    )
    _req(
        context_cutoff >= reference,
        "CONTEXT_CUTOFF_BEFORE_REFERENCE",
        _utc(context_cutoff),
    )

    observation_id = str(
        descriptor.get("observation_id", "")
    ).strip()
    _req(
        bool(observation_id),
        "OBSERVATION_ID_INVALID",
        observation_id,
    )

    return dict(descriptor)


def validate_event_risk_calendar_snapshot_v1(
    snapshot: Mapping[str, Any],
    *,
    taxonomy: Mapping[str, Any],
) -> dict[str, Any]:
    _req(
        isinstance(snapshot, Mapping),
        "SNAPSHOT_INVALID",
        "mapping required",
    )
    _req(
        snapshot.get("schema_version")
        == SNAPSHOT_SCHEMA_VERSION,
        "SNAPSHOT_SCHEMA_INVALID",
        str(snapshot.get("schema_version")),
    )

    snapshot_id = str(snapshot.get("snapshot_id", "")).strip()
    _req(
        bool(snapshot_id),
        "SNAPSHOT_ID_INVALID",
        snapshot_id,
    )

    created_at = _parse_utc(
        snapshot.get("snapshot_created_at_utc"),
        "snapshot_created_at_utc",
    )

    source_name = str(
        snapshot.get("source_name", "")
    ).strip()
    _req(
        bool(source_name),
        "SNAPSHOT_SOURCE_NAME_INVALID",
        source_name,
    )

    events = snapshot.get("events")
    _req(
        isinstance(events, list),
        "SNAPSHOT_EVENTS_INVALID",
        "events must be list",
    )

    allowed_types = {
        str(item["event_type"])
        for item in taxonomy["event_types"]
    }

    seen_ids: set[str] = set()
    normalized: list[dict[str, Any]] = []
    previous_sort_key = None

    for event in events:
        _req(
            isinstance(event, Mapping),
            "SNAPSHOT_EVENT_INVALID",
            str(event),
        )

        event_id = str(event.get("event_id", "")).strip()
        _req(
            bool(event_id),
            "EVENT_ID_INVALID",
            str(event),
        )
        _req(
            event_id not in seen_ids,
            "EVENT_ID_DUPLICATED",
            event_id,
        )
        seen_ids.add(event_id)

        event_type = str(event.get("event_type", ""))
        _req(
            event_type in allowed_types,
            "EVENT_TYPE_NOT_ALLOWED",
            event_type,
        )

        scheduled_at = _parse_utc(
            event.get("scheduled_at_utc"),
            f"{event_id}.scheduled_at_utc",
        )
        schedule_known_at = _parse_utc(
            event.get("schedule_known_at_utc"),
            f"{event_id}.schedule_known_at_utc",
        )

        _req(
            schedule_known_at <= created_at,
            "EVENT_KNOWN_AFTER_SNAPSHOT_CREATED",
            event_id,
        )

        schedule_source = str(
            event.get("schedule_source", "")
        ).strip()
        _req(
            bool(schedule_source),
            "EVENT_SCHEDULE_SOURCE_INVALID",
            event_id,
        )

        sort_key = (scheduled_at, event_id)
        if previous_sort_key is not None:
            _req(
                sort_key > previous_sort_key,
                "EVENT_ORDER_INVALID",
                event_id,
            )
        previous_sort_key = sort_key

        normalized.append(
            {
                "event_id": event_id,
                "event_type": event_type,
                "scheduled_at_utc": _utc(scheduled_at),
                "schedule_known_at_utc": _utc(schedule_known_at),
                "schedule_source": schedule_source,
            }
        )

    return {
        "snapshot_id": snapshot_id,
        "snapshot_created_at_utc": _utc(created_at),
        "source_name": source_name,
        "event_count": len(normalized),
        "events": normalized,
    }


def _count_future(
    events: Sequence[dict[str, Any]],
    reference: datetime,
    seconds: int,
) -> int:
    upper = reference + timedelta(seconds=seconds)
    return sum(
        1
        for event in events
        if reference <= event["scheduled_dt"] <= upper
    )


def _count_recent(
    events: Sequence[dict[str, Any]],
    reference: datetime,
    seconds: int,
) -> int:
    lower = reference - timedelta(seconds=seconds)
    return sum(
        1
        for event in events
        if lower <= event["scheduled_dt"] < reference
    )


def build_event_risk_calendar_context_v1_component(
    *,
    observation_descriptor: Mapping[str, Any],
    calendar_snapshot: Mapping[str, Any],
    snapshot_sha256: str,
    taxonomy: Mapping[str, Any],
    taxonomy_sha256: str,
    produced_at_utc: str,
) -> dict[str, Any]:
    descriptor = _validate_observation_descriptor(
        observation_descriptor
    )
    validate_event_risk_taxonomy_v1(taxonomy)
    snapshot_validation = (
        validate_event_risk_calendar_snapshot_v1(
            calendar_snapshot,
            taxonomy=taxonomy,
        )
    )

    for name, digest in (
        ("snapshot_sha256", snapshot_sha256),
        ("taxonomy_sha256", taxonomy_sha256),
    ):
        _req(
            len(digest) == 64
            and all(
                char in "0123456789abcdef"
                for char in digest
            ),
            "SHA256_INVALID",
            name,
        )

    reference = _parse_utc(
        descriptor["reference_boundary_utc"],
        "reference_boundary_utc",
    )
    context_cutoff = _parse_utc(
        descriptor["synchronized_context_available_at_utc"],
        "synchronized_context_available_at_utc",
    )
    produced_at = _parse_utc(
        produced_at_utc,
        "produced_at_utc",
    )
    snapshot_created_at = _parse_utc(
        snapshot_validation["snapshot_created_at_utc"],
        "snapshot_created_at_utc",
    )

    _req(
        produced_at >= reference,
        "PRODUCED_BEFORE_REFERENCE_BOUNDARY",
        _utc(produced_at),
    )
    _req(
        snapshot_created_at <= produced_at,
        "SNAPSHOT_CREATED_AFTER_PRODUCTION",
        _utc(snapshot_created_at),
    )

    known_events = []
    excluded_post_reference_schedule_knowledge = 0

    for event in snapshot_validation["events"]:
        known_at = _parse_utc(
            event["schedule_known_at_utc"],
            "schedule_known_at_utc",
        )
        scheduled_at = _parse_utc(
            event["scheduled_at_utc"],
            "scheduled_at_utc",
        )

        if known_at <= reference:
            known_events.append(
                {
                    **event,
                    "known_at_dt": known_at,
                    "scheduled_dt": scheduled_at,
                }
            )
        else:
            excluded_post_reference_schedule_knowledge += 1

    previous_events = [
        event
        for event in known_events
        if event["scheduled_dt"] < reference
    ]
    upcoming_events = [
        event
        for event in known_events
        if event["scheduled_dt"] >= reference
    ]

    previous_event = (
        max(
            previous_events,
            key=lambda event: (
                event["scheduled_dt"],
                event["event_id"],
            ),
        )
        if previous_events
        else None
    )
    next_event = (
        min(
            upcoming_events,
            key=lambda event: (
                event["scheduled_dt"],
                event["event_id"],
            ),
        )
        if upcoming_events
        else None
    )

    seconds_since_previous = (
        int(
            (
                reference
                - previous_event["scheduled_dt"]
            ).total_seconds()
        )
        if previous_event is not None
        else None
    )
    seconds_to_next = (
        int(
            (
                next_event["scheduled_dt"]
                - reference
            ).total_seconds()
        )
        if next_event is not None
        else None
    )

    future_counts = {
        name: _count_future(
            known_events,
            reference,
            seconds,
        )
        for name, seconds in FUTURE_WINDOWS_SECONDS.items()
    }
    recent_counts = {
        name: _count_recent(
            known_events,
            reference,
            seconds,
        )
        for name, seconds in RECENT_WINDOWS_SECONDS.items()
    }

    payload = {
        "model_semantics": "DESCRIPTIVE_SCHEDULED_EVENT_PROXIMITY_ONLY",
        "reference_boundary_utc": _utc(reference),
        "context_cutoff_utc": _utc(context_cutoff),
        "calendar_snapshot_id":
            snapshot_validation["snapshot_id"],
        "calendar_snapshot_created_at_utc":
            snapshot_validation["snapshot_created_at_utc"],
        "calendar_source_name":
            snapshot_validation["source_name"],
        "taxonomy_sha256": taxonomy_sha256,
        "known_event_count_at_reference":
            len(known_events),
        "excluded_event_count_schedule_known_after_reference":
            excluded_post_reference_schedule_knowledge,
        "previous_known_event": (
            {
                "event_id": previous_event["event_id"],
                "event_type": previous_event["event_type"],
                "scheduled_at_utc":
                    previous_event["scheduled_at_utc"],
                "schedule_known_at_utc":
                    previous_event["schedule_known_at_utc"],
                "seconds_since_event":
                    seconds_since_previous,
            }
            if previous_event is not None
            else None
        ),
        "next_known_event": (
            {
                "event_id": next_event["event_id"],
                "event_type": next_event["event_type"],
                "scheduled_at_utc":
                    next_event["scheduled_at_utc"],
                "schedule_known_at_utc":
                    next_event["schedule_known_at_utc"],
                "seconds_to_event": seconds_to_next,
            }
            if next_event is not None
            else None
        ),
        "upcoming_event_counts": future_counts,
        "recent_event_counts": recent_counts,
        "event_values_used": False,
        "event_surprise_used": False,
        "market_reaction_used": False,
        "price_input_used": False,
        "market_data_input_used": False,
        "future_outcomes_used": False,
        "directional_semantics": False,
        "signal_semantics": False,
        "importance_score_assigned": False,
        "candidate_modification_semantics": False,
        "post_reference_schedule_knowledge_used": False,
    }

    return {
        "feature_id": FEATURE_ID,
        "source_kind": SOURCE_KIND,
        "feature_schema_version": FEATURE_SCHEMA_VERSION,
        "status": "AVAILABLE",
        "reason": None,
        "available_at_utc": _utc(produced_at),
        "information_cutoff_utc": _utc(reference),
        "source_artifact_sha256": snapshot_sha256,
        "payload": payload,
    }


def _not_configured_component(
    registry_item: Mapping[str, Any],
) -> dict[str, Any]:
    feature_id = str(registry_item["feature_id"])
    return {
        "feature_id": feature_id,
        "source_kind": str(registry_item["source_kind"]),
        "feature_schema_version":
            feature_id + "_PLACEHOLDER_SCHEMA_V1",
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
        str(item["feature_id"]): _not_configured_component(item)
        for item in FEATURE_REGISTRY
    }
    components[FEATURE_ID] = dict(component)

    pack = build_context_feature_pack_v1(
        observation_descriptor=observation_descriptor,
        components=components,
        pack_id="PACK_COMPATIBILITY_CHECK_ONLY",
    )

    feature = next(
        item
        for item in pack["features"]
        if item["feature_id"] == FEATURE_ID
    )

    return {
        "status": feature["status"],
        "point_in_time_eligible":
            feature["point_in_time_eligible"],
        "eligibility_reason":
            feature["eligibility_reason"],
        "payload_sha256":
            feature["payload_sha256"],
    }


def validate_event_risk_calendar_context_v1_component(
    component: Mapping[str, Any],
) -> dict[str, Any]:
    _req(
        isinstance(component, Mapping),
        "COMPONENT_INVALID",
        "mapping required",
    )
    _req(
        component.get("feature_id") == FEATURE_ID,
        "COMPONENT_FEATURE_ID_INVALID",
        str(component.get("feature_id")),
    )
    _req(
        component.get("source_kind") == SOURCE_KIND,
        "COMPONENT_SOURCE_KIND_INVALID",
        str(component.get("source_kind")),
    )
    _req(
        component.get("feature_schema_version")
        == FEATURE_SCHEMA_VERSION,
        "COMPONENT_SCHEMA_INVALID",
        str(component.get("feature_schema_version")),
    )
    _req(
        component.get("status") == "AVAILABLE",
        "COMPONENT_STATUS_INVALID",
        str(component.get("status")),
    )

    available_at = _parse_utc(
        component.get("available_at_utc"),
        "available_at_utc",
    )
    information_cutoff = _parse_utc(
        component.get("information_cutoff_utc"),
        "information_cutoff_utc",
    )
    _req(
        information_cutoff <= available_at,
        "COMPONENT_INFORMATION_AFTER_AVAILABILITY",
        "timestamps",
    )

    source_sha = str(
        component.get("source_artifact_sha256", "")
    )
    _req(
        len(source_sha) == 64
        and all(
            char in "0123456789abcdef"
            for char in source_sha
        ),
        "COMPONENT_SOURCE_SHA_INVALID",
        source_sha,
    )

    payload = component.get("payload")
    _req(
        isinstance(payload, Mapping),
        "COMPONENT_PAYLOAD_INVALID",
        "payload",
    )
    _req(
        payload.get("model_semantics")
        == "DESCRIPTIVE_SCHEDULED_EVENT_PROXIMITY_ONLY",
        "PAYLOAD_SEMANTICS_INVALID",
        str(payload.get("model_semantics")),
    )

    for field in (
        "event_values_used",
        "event_surprise_used",
        "market_reaction_used",
        "price_input_used",
        "market_data_input_used",
        "future_outcomes_used",
        "directional_semantics",
        "signal_semantics",
        "importance_score_assigned",
        "candidate_modification_semantics",
        "post_reference_schedule_knowledge_used",
    ):
        _req(
            payload.get(field) is False,
            "FORBIDDEN_PAYLOAD_SEMANTIC_ENABLED",
            field,
        )

    _req(
        set(payload["upcoming_event_counts"])
        == set(FUTURE_WINDOWS_SECONDS),
        "UPCOMING_WINDOW_KEYS_INVALID",
        str(payload["upcoming_event_counts"]),
    )
    _req(
        set(payload["recent_event_counts"])
        == set(RECENT_WINDOWS_SECONDS),
        "RECENT_WINDOW_KEYS_INVALID",
        str(payload["recent_event_counts"]),
    )

    return {
        "status": "AVAILABLE",
        "known_event_count_at_reference": int(
            payload["known_event_count_at_reference"]
        ),
        "excluded_post_reference_schedule_knowledge": int(
            payload[
                "excluded_event_count_schedule_known_after_reference"
            ]
        ),
        "directional_semantics": False,
        "signal_semantics": False,
    }


def _write_manifest(directory: Path) -> None:
    lines = [
        f"{_sha(directory / name)}  {name}"
        for name in sorted(
            (CHECKS_FILENAME, COMPONENT_FILENAME)
        )
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
            name in (CHECKS_FILENAME, COMPONENT_FILENAME),
            "PACKAGE_MANIFEST_SCOPE_INVALID",
            name,
        )
        candidate = directory / name
        _req(
            candidate.is_file() and not candidate.is_symlink(),
            "PACKAGE_MANIFEST_FILE_MISSING",
            name,
        )
        _req(
            _sha(candidate) == expected,
            "PACKAGE_MANIFEST_HASH_MISMATCH",
            name,
        )
        seen[name] = expected

    _req(
        set(seen) == {CHECKS_FILENAME, COMPONENT_FILENAME},
        "PACKAGE_MANIFEST_SCOPE_INVALID",
        str(sorted(seen)),
    )
    return seen


def validate_event_risk_calendar_context_v1_package(
    directory: Path | str,
) -> dict[str, Any]:
    root = Path(directory).resolve()
    _req(
        root.is_dir() and not root.is_symlink(),
        "PACKAGE_DIRECTORY_INVALID",
        str(root),
    )

    manifest = _read_manifest(root)
    component = _read_json_mapping(
        root / COMPONENT_FILENAME,
        "PACKAGE_COMPONENT_INVALID",
    )
    checks = _read_json_mapping(
        root / CHECKS_FILENAME,
        "PACKAGE_CHECKS_INVALID",
    )
    component_validation = (
        validate_event_risk_calendar_context_v1_component(
            component
        )
    )

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
        checks.get("feature_id") == FEATURE_ID,
        "PACKAGE_FEATURE_ID_INVALID",
        str(checks.get("feature_id")),
    )

    for field in (
        "real_network_request_executed",
        "market_data_acquired",
        "git_network_request_executed",
        "event_values_used",
        "event_surprise_used",
        "market_reaction_used",
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
        **component_validation,
        "manifest_entries": len(manifest),
        "point_in_time_eligible_under_pack_policy": bool(
            checks[
                "point_in_time_eligible_under_pack_policy"
            ]
        ),
        "real_network_request_executed": False,
        "official_append_executed": False,
    }


def prepare_event_risk_calendar_context_v1_package(
    *,
    repo_root: Path | str,
    observation_descriptor_json: Path | str,
    event_calendar_snapshot_json: Path | str,
    output_directory: Path | str,
    produced_at_utc: str,
    authorization: str | None = None,
) -> dict[str, Any]:
    _req(
        authorization == PACKAGE_AUTHORIZATION,
        "PACKAGE_AUTHORIZATION_REQUIRED",
        "authorization",
    )
    _official_gate_off()

    repo = Path(repo_root).resolve()
    descriptor_path = Path(
        observation_descriptor_json
    ).resolve()
    snapshot_path = Path(
        event_calendar_snapshot_json
    ).resolve()
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
        not _inside(snapshot_path, repo),
        "SNAPSHOT_INSIDE_REPOSITORY_PROHIBITED",
        str(snapshot_path),
    )

    official_before = _official(repo)

    descriptor = _read_json_mapping(
        descriptor_path,
        "OBSERVATION_DESCRIPTOR_FILE_INVALID",
    )
    _validate_observation_descriptor(descriptor)

    taxonomy, taxonomy_sha = load_event_risk_taxonomy_v1(
        repo
    )

    snapshot = _read_json_mapping(
        snapshot_path,
        "EVENT_CALENDAR_SNAPSHOT_FILE_INVALID",
    )
    validate_event_risk_calendar_snapshot_v1(
        snapshot,
        taxonomy=taxonomy,
    )
    snapshot_sha = _sha(snapshot_path)

    component = (
        build_event_risk_calendar_context_v1_component(
            observation_descriptor=descriptor,
            calendar_snapshot=snapshot,
            snapshot_sha256=snapshot_sha,
            taxonomy=taxonomy,
            taxonomy_sha256=taxonomy_sha,
            produced_at_utc=produced_at_utc,
        )
    )
    validate_event_risk_calendar_context_v1_component(
        component
    )

    compatibility = (
        validate_component_against_level_a_pack_v1(
            observation_descriptor=descriptor,
            component=component,
        )
    )

    _req(
        _official(repo) == official_before,
        "OFFICIAL_ARTIFACT_CHANGED",
        "before output",
    )
    _official_gate_off()

    temp = (
        output.parent
        / f".{output.name}.tmp-{uuid.uuid4().hex}"
    )
    _req(
        not temp.exists(),
        "TEMPORARY_OUTPUT_COLLISION",
        str(temp),
    )

    try:
        temp.mkdir()

        _write_new(
            temp / COMPONENT_FILENAME,
            _json_bytes(component),
        )

        checks = {
            "package_schema_version": PACKAGE_SCHEMA_VERSION,
            "capability": CAPABILITY,
            "feature_id": FEATURE_ID,
            "observation_descriptor_sha256":
                _sha(descriptor_path),
            "event_calendar_snapshot_sha256":
                snapshot_sha,
            "taxonomy_resource_sha256":
                taxonomy_sha,
            "produced_at_utc": _utc(
                _parse_utc(
                    produced_at_utc,
                    "produced_at_utc",
                )
            ),
            "point_in_time_eligible_under_pack_policy":
                compatibility["point_in_time_eligible"],
            "pack_eligibility_reason":
                compatibility["eligibility_reason"],
            "real_network_request_executed": False,
            "market_data_acquired": False,
            "git_network_request_executed": False,
            "event_values_used": False,
            "event_surprise_used": False,
            "market_reaction_used": False,
            "direction_inferred": False,
            "signal_generated": False,
            "candidate_modified": False,
            "primary_rule_modified": False,
            "official_append_executed": False,
            "official_dataset_changed": False,
            "official_manifest_changed": False,
            **{field: False for field in FALSE_PERMISSION_FIELDS},
        }

        _write_new(
            temp / CHECKS_FILENAME,
            _json_bytes(checks),
        )
        _write_manifest(temp)
        validate_event_risk_calendar_context_v1_package(
            temp
        )

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
    _official_gate_off()

    validation = (
        validate_event_risk_calendar_context_v1_package(
            output
        )
    )

    return {
        "capability": CAPABILITY,
        "feature_id": FEATURE_ID,
        "output_directory": str(output),
        "component_status": validation["status"],
        "known_event_count_at_reference":
            validation["known_event_count_at_reference"],
        "point_in_time_eligible_under_pack_policy":
            validation[
                "point_in_time_eligible_under_pack_policy"
            ],
        "real_network_request_executed": False,
        "market_data_acquired": False,
        "git_network_request_executed": False,
        "official_append_executed": False,
        **{field: False for field in FALSE_PERMISSION_FIELDS},
    }


__all__ = [
    "CAPABILITY",
    "FEATURE_ID",
    "FEATURE_SCHEMA_VERSION",
    "IMPLEMENTATION_OR_REPAIR_ATTEMPT",
    "MAX_IMPLEMENTATION_OR_REPAIR_ATTEMPTS",
    "PACKAGE_AUTHORIZATION",
    "SNAPSHOT_SCHEMA_VERSION",
    "SOURCE_KIND",
    "TAXONOMY_PATH",
    "EventRiskCalendarContextError",
    "build_event_risk_calendar_context_v1_component",
    "load_event_risk_taxonomy_v1",
    "prepare_event_risk_calendar_context_v1_package",
    "validate_component_against_level_a_pack_v1",
    "validate_event_risk_calendar_context_v1_component",
    "validate_event_risk_calendar_context_v1_package",
    "validate_event_risk_calendar_snapshot_v1",
    "validate_event_risk_taxonomy_v1",
]
