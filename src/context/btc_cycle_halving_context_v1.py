from __future__ import annotations

import hashlib
import json
import os
import shutil
import uuid
from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from typing import Any, Mapping

from src.context.context_feature_pack_v1_level_a_standard import (
    FEATURE_REGISTRY,
    build_context_feature_pack_v1,
)

CAPABILITY = "BTC_CYCLE_HALVING_CONTEXT_V1"
FEATURE_ID = "BTC_CYCLE_HALVING_CONTEXT_V1"
FEATURE_SCHEMA_VERSION = "BTC_CYCLE_HALVING_CONTEXT_V1_SCHEMA_V1"
PACKAGE_SCHEMA_VERSION = "BTC_CYCLE_HALVING_CONTEXT_V1_PACKAGE_V1"
SOURCE_KIND = "DETERMINISTIC"

PACKAGE_AUTHORIZATION = "PREPARE_BTC_CYCLE_HALVING_CONTEXT_V1"

MAX_IMPLEMENTATION_OR_REPAIR_ATTEMPTS = 10
IMPLEMENTATION_OR_REPAIR_ATTEMPT = 1

RESOURCE_PATH = Path(
    "src/context/resources/btc_cycle_halving_calendar_v1.json"
)

EXPECTED_CALENDAR_SCHEMA_VERSION = "BTC_CYCLE_HALVING_CALENDAR_V1"
EXPECTED_TIME_BASIS = (
    "UTC_CALENDAR_DAY_START_REFERENCE_NOT_BLOCK_TIMESTAMP"
)
EXPECTED_HALVING_INTERVAL_BLOCKS = 210000
EXPECTED_HALVING_COUNT = 4

COMPONENT_FILENAME = "btc_cycle_halving_context_component.json"
CHECKS_FILENAME = "producer_checks.json"
MANIFEST_FILENAME = "manifest.sha256"

OFFICIAL_APPEND_GATE_NAME = "TRADING_AI_OFFICIAL_LONG_EVIDENCE_APPEND_ALLOWED"
OFFICIAL_DATASET = Path("data/forward/long_forward_observation_dataset_v1.csv")
OFFICIAL_MANIFEST = Path(
    "data/forward/long_forward_observation_dataset_v1.manifest.csv"
)
OFFICIAL_LOCK = Path("data/forward/long_forward_observation_dataset_v1.lock")

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


class BtcCycleHalvingContextError(RuntimeError):
    def __init__(self, code: str, message: str) -> None:
        self.code = code
        super().__init__(message)


def _req(ok: bool, code: str, message: str) -> None:
    if not ok:
        raise BtcCycleHalvingContextError(code, message)


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
        raise BtcCycleHalvingContextError(
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


def _date_anchor_utc(calendar_date_utc: str) -> datetime:
    try:
        parsed = datetime.strptime(
            calendar_date_utc,
            "%Y-%m-%d",
        ).replace(tzinfo=timezone.utc)
    except ValueError as exc:
        raise BtcCycleHalvingContextError(
            "HALVING_CALENDAR_DATE_INVALID",
            calendar_date_utc,
        ) from exc
    return parsed


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
        raise BtcCycleHalvingContextError(
            code,
            str(path),
        ) from exc
    _req(
        isinstance(value, Mapping),
        code,
        str(path),
    )
    return dict(value)


def validate_halving_calendar_v1(
    calendar: Mapping[str, Any],
) -> dict[str, Any]:
    _req(
        isinstance(calendar, Mapping),
        "CALENDAR_INVALID",
        "mapping required",
    )
    _req(
        calendar.get("schema_version")
        == EXPECTED_CALENDAR_SCHEMA_VERSION,
        "CALENDAR_SCHEMA_INVALID",
        str(calendar.get("schema_version")),
    )
    _req(
        calendar.get("time_basis") == EXPECTED_TIME_BASIS,
        "CALENDAR_TIME_BASIS_INVALID",
        str(calendar.get("time_basis")),
    )
    _req(
        calendar.get(
            "calendar_dates_are_reference_days_not_block_timestamps"
        )
        is True,
        "CALENDAR_REFERENCE_DAY_POLICY_INVALID",
        "reference-day policy",
    )
    _req(
        int(calendar.get("protocol_halving_interval_blocks", 0))
        == EXPECTED_HALVING_INTERVAL_BLOCKS,
        "HALVING_INTERVAL_INVALID",
        str(calendar.get("protocol_halving_interval_blocks")),
    )
    _req(
        str(calendar.get("genesis_block_subsidy_btc"))
        == "50",
        "GENESIS_SUBSIDY_INVALID",
        str(calendar.get("genesis_block_subsidy_btc")),
    )

    events = calendar.get("historical_halvings")
    _req(
        isinstance(events, list)
        and len(events) == EXPECTED_HALVING_COUNT,
        "HALVING_EVENT_COUNT_INVALID",
        str(len(events) if isinstance(events, list) else None),
    )

    expected_dates = (
        "2012-11-28",
        "2016-07-09",
        "2020-05-11",
        "2024-04-20",
    )

    previous_anchor = None
    previous_height = 0

    for index, event in enumerate(events, start=1):
        _req(
            isinstance(event, Mapping),
            "HALVING_EVENT_INVALID",
            str(index),
        )
        _req(
            int(event.get("halving_index", -1)) == index,
            "HALVING_INDEX_INVALID",
            str(index),
        )
        expected_height = index * EXPECTED_HALVING_INTERVAL_BLOCKS
        _req(
            int(event.get("block_height", -1)) == expected_height,
            "HALVING_HEIGHT_INVALID",
            str(index),
        )
        _req(
            event.get("calendar_date_utc")
            == expected_dates[index - 1],
            "HALVING_DATE_INVALID",
            str(index),
        )

        anchor = _date_anchor_utc(
            str(event["calendar_date_utc"])
        )
        if previous_anchor is not None:
            _req(
                anchor > previous_anchor,
                "HALVING_DATE_ORDER_INVALID",
                str(index),
            )
        _req(
            expected_height > previous_height,
            "HALVING_HEIGHT_ORDER_INVALID",
            str(index),
        )

        expected_subsidy = (
            Decimal("50") / (Decimal(2) ** index)
        )
        actual_subsidy = Decimal(
            str(event.get("post_halving_subsidy_btc"))
        )
        _req(
            actual_subsidy == expected_subsidy,
            "HALVING_SUBSIDY_INVALID",
            str(index),
        )

        previous_anchor = anchor
        previous_height = expected_height

    _req(
        int(
            calendar.get(
                "next_protocol_halving_block_height_after_latest_record",
                -1,
            )
        )
        == (EXPECTED_HALVING_COUNT + 1)
        * EXPECTED_HALVING_INTERVAL_BLOCKS,
        "NEXT_HALVING_HEIGHT_INVALID",
        "next height",
    )
    _req(
        calendar.get("future_halving_time_estimated") is False,
        "FUTURE_HALVING_TIME_ESTIMATE_PROHIBITED",
        "must be false",
    )

    return {
        "historical_halving_count": len(events),
        "latest_halving_index": int(
            events[-1]["halving_index"]
        ),
        "latest_halving_block_height": int(
            events[-1]["block_height"]
        ),
        "latest_halving_calendar_date_utc": str(
            events[-1]["calendar_date_utc"]
        ),
        "next_protocol_halving_block_height": int(
            calendar[
                "next_protocol_halving_block_height_after_latest_record"
            ]
        ),
        "future_halving_time_estimated": False,
    }


def load_halving_calendar_v1(
    repo_root: Path | str,
) -> tuple[dict[str, Any], str]:
    repo = Path(repo_root).resolve()
    path = repo / RESOURCE_PATH
    calendar = _read_json_mapping(
        path,
        "HALVING_CALENDAR_FILE_INVALID",
    )
    validate_halving_calendar_v1(calendar)
    return calendar, _sha(path)


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
        isinstance(
            descriptor.get("primary_candidate_detected"),
            bool,
        ),
        "PRIMARY_CANDIDATE_STATE_INVALID",
        str(descriptor.get("primary_candidate_detected")),
    )

    reference = _parse_utc(
        descriptor.get("reference_boundary_utc"),
        "reference_boundary_utc",
    )
    context_cutoff = _parse_utc(
        descriptor.get(
            "synchronized_context_available_at_utc"
        ),
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


def _ratio_string(
    numerator_seconds: int,
    denominator_days: int,
) -> str:
    denominator_seconds = (
        Decimal(denominator_days) * Decimal(86400)
    )
    ratio = (
        Decimal(numerator_seconds) / denominator_seconds
    ).quantize(
        Decimal("0.00000001"),
        rounding=ROUND_HALF_UP,
    )
    return format(ratio, "f")


def _quartile_from_ratio(ratio: Decimal) -> str:
    if ratio < Decimal("0.25"):
        return "Q1"
    if ratio < Decimal("0.50"):
        return "Q2"
    if ratio < Decimal("0.75"):
        return "Q3"
    if ratio < Decimal("1.00"):
        return "Q4"
    return "BEYOND_PREVIOUS_COMPLETED_CYCLE_LENGTH"


def build_btc_cycle_halving_context_v1_component(
    *,
    observation_descriptor: Mapping[str, Any],
    halving_calendar: Mapping[str, Any],
    calendar_sha256: str,
    produced_at_utc: str,
) -> dict[str, Any]:
    descriptor = _validate_observation_descriptor(
        observation_descriptor
    )
    validate_halving_calendar_v1(halving_calendar)

    _req(
        len(calendar_sha256) == 64
        and all(
            char in "0123456789abcdef"
            for char in calendar_sha256
        ),
        "CALENDAR_SHA256_INVALID",
        calendar_sha256,
    )

    reference = _parse_utc(
        descriptor["reference_boundary_utc"],
        "reference_boundary_utc",
    )
    context_cutoff = _parse_utc(
        descriptor[
            "synchronized_context_available_at_utc"
        ],
        "synchronized_context_available_at_utc",
    )
    produced_at = _parse_utc(
        produced_at_utc,
        "produced_at_utc",
    )

    _req(
        produced_at >= reference,
        "PRODUCED_BEFORE_REFERENCE_BOUNDARY",
        _utc(produced_at),
    )

    events = list(
        halving_calendar["historical_halvings"]
    )
    eligible_events = [
        event
        for event in events
        if _date_anchor_utc(
            str(event["calendar_date_utc"])
        )
        <= reference
    ]

    if not eligible_events:
        return {
            "feature_id": FEATURE_ID,
            "source_kind": SOURCE_KIND,
            "feature_schema_version": FEATURE_SCHEMA_VERSION,
            "status": "UNAVAILABLE",
            "reason": "NO_HALVING_REFERENCE_AT_OR_BEFORE_OBSERVATION",
            "available_at_utc": None,
            "information_cutoff_utc": None,
            "source_artifact_sha256": None,
            "payload": None,
        }

    current = eligible_events[-1]
    current_anchor = _date_anchor_utc(
        str(current["calendar_date_utc"])
    )
    seconds_since = int(
        (reference - current_anchor).total_seconds()
    )
    _req(
        seconds_since >= 0,
        "NEGATIVE_CYCLE_AGE",
        str(seconds_since),
    )

    previous = (
        eligible_events[-2]
        if len(eligible_events) >= 2
        else None
    )

    previous_cycle_length_days = None
    elapsed_ratio = None
    quartile = "UNAVAILABLE_NO_PREVIOUS_COMPLETED_CYCLE"

    if previous is not None:
        previous_anchor = _date_anchor_utc(
            str(previous["calendar_date_utc"])
        )
        previous_cycle_length_days = (
            current_anchor - previous_anchor
        ).days
        _req(
            previous_cycle_length_days > 0,
            "PREVIOUS_CYCLE_LENGTH_INVALID",
            str(previous_cycle_length_days),
        )
        elapsed_ratio = _ratio_string(
            seconds_since,
            previous_cycle_length_days,
        )
        quartile = _quartile_from_ratio(
            Decimal(elapsed_ratio)
        )

    current_index = int(current["halving_index"])
    next_protocol_height = (
        int(current["block_height"])
        + EXPECTED_HALVING_INTERVAL_BLOCKS
    )

    payload = {
        "model_semantics": "DESCRIPTIVE_TEMPORAL_CONTEXT_ONLY",
        "time_basis": EXPECTED_TIME_BASIS,
        "calendar_dates_are_reference_days_not_block_timestamps": True,
        "reference_boundary_utc": _utc(reference),
        "context_cutoff_utc": _utc(context_cutoff),
        "halving_index": current_index,
        "halving_block_height": int(
            current["block_height"]
        ),
        "halving_calendar_date_utc": str(
            current["calendar_date_utc"]
        ),
        "halving_reference_utc": _utc(current_anchor),
        "post_halving_subsidy_btc": str(
            current["post_halving_subsidy_btc"]
        ),
        "protocol_halving_interval_blocks":
            EXPECTED_HALVING_INTERVAL_BLOCKS,
        "days_since_halving_reference": (
            seconds_since // 86400
        ),
        "seconds_since_halving_reference": seconds_since,
        "previous_completed_cycle_length_days":
            previous_cycle_length_days,
        "elapsed_fraction_of_previous_completed_cycle_length":
            elapsed_ratio,
        "cycle_quartile_vs_previous_completed_cycle_length":
            quartile,
        "next_protocol_halving_block_height":
            next_protocol_height,
        "next_halving_time_estimated": False,
        "estimated_next_halving_utc": None,
        "days_to_next_halving_estimate": None,
        "future_halving_date_prediction_used": False,
        "historical_halving_dates_after_reference_used": False,
        "price_input_used": False,
        "market_data_input_used": False,
        "future_outcomes_used": False,
        "directional_semantics": False,
        "signal_semantics": False,
        "candidate_modification_semantics": False,
    }

    return {
        "feature_id": FEATURE_ID,
        "source_kind": SOURCE_KIND,
        "feature_schema_version": FEATURE_SCHEMA_VERSION,
        "status": "AVAILABLE",
        "reason": None,
        "available_at_utc": _utc(produced_at),
        "information_cutoff_utc": _utc(reference),
        "source_artifact_sha256": calendar_sha256,
        "payload": payload,
    }


def _not_configured_component(
    registry_item: Mapping[str, Any],
) -> dict[str, Any]:
    feature_id = str(registry_item["feature_id"])
    return {
        "feature_id": feature_id,
        "source_kind": str(registry_item["source_kind"]),
        "feature_schema_version": (
            feature_id + "_PLACEHOLDER_SCHEMA_V1"
        ),
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


def validate_btc_cycle_halving_context_v1_component(
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

    status = str(component.get("status"))
    _req(
        status in ("AVAILABLE", "UNAVAILABLE"),
        "COMPONENT_STATUS_INVALID",
        status,
    )

    if status == "UNAVAILABLE":
        _req(
            component.get("payload") is None
            and component.get("source_artifact_sha256") is None
            and component.get("available_at_utc") is None
            and component.get("information_cutoff_utc") is None,
            "UNAVAILABLE_COMPONENT_FIELDS_INVALID",
            "unavailable",
        )
        _req(
            bool(str(component.get("reason", "")).strip()),
            "UNAVAILABLE_REASON_REQUIRED",
            "reason",
        )
        return {
            "status": "UNAVAILABLE",
            "directional_semantics": False,
            "signal_semantics": False,
        }

    payload = component.get("payload")
    _req(
        isinstance(payload, Mapping),
        "AVAILABLE_COMPONENT_PAYLOAD_INVALID",
        "payload",
    )
    _parse_utc(
        component.get("available_at_utc"),
        "available_at_utc",
    )
    information_cutoff = _parse_utc(
        component.get("information_cutoff_utc"),
        "information_cutoff_utc",
    )
    available_at = _parse_utc(
        component.get("available_at_utc"),
        "available_at_utc",
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

    _req(
        payload.get("model_semantics")
        == "DESCRIPTIVE_TEMPORAL_CONTEXT_ONLY",
        "PAYLOAD_MODEL_SEMANTICS_INVALID",
        str(payload.get("model_semantics")),
    )
    _req(
        payload.get("directional_semantics") is False,
        "DIRECTIONAL_SEMANTICS_PROHIBITED",
        "direction",
    )
    _req(
        payload.get("signal_semantics") is False,
        "SIGNAL_SEMANTICS_PROHIBITED",
        "signal",
    )
    _req(
        payload.get("price_input_used") is False
        and payload.get("market_data_input_used") is False,
        "MARKET_INPUT_PROHIBITED",
        "market inputs",
    )
    _req(
        payload.get("future_outcomes_used") is False,
        "FUTURE_OUTCOMES_PROHIBITED",
        "future outcomes",
    )
    _req(
        payload.get("next_halving_time_estimated") is False
        and payload.get("estimated_next_halving_utc") is None
        and payload.get("days_to_next_halving_estimate") is None,
        "FUTURE_HALVING_TIME_ESTIMATE_PROHIBITED",
        "future estimate",
    )
    _req(
        payload.get("historical_halving_dates_after_reference_used")
        is False,
        "POST_REFERENCE_HALVING_DATE_USE_PROHIBITED",
        "post reference",
    )

    return {
        "status": "AVAILABLE",
        "halving_index": int(payload["halving_index"]),
        "days_since_halving_reference": int(
            payload["days_since_halving_reference"]
        ),
        "cycle_quartile": str(
            payload[
                "cycle_quartile_vs_previous_completed_cycle_length"
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


def validate_btc_cycle_halving_context_v1_package(
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
        validate_btc_cycle_halving_context_v1_component(
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
    _req(
        checks.get("real_network_request_executed") is False
        and checks.get("market_data_acquired") is False
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
        checks.get("price_input_used") is False
        and checks.get("future_outcomes_used") is False
        and checks.get("direction_inferred") is False
        and checks.get("signal_generated") is False,
        "PACKAGE_RESEARCH_BOUNDARY_INVALID",
        "research",
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


def prepare_btc_cycle_halving_context_v1_package(
    *,
    repo_root: Path | str,
    observation_descriptor_json: Path | str,
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

    official_before = _official(repo)
    descriptor = _read_json_mapping(
        descriptor_path,
        "OBSERVATION_DESCRIPTOR_FILE_INVALID",
    )
    _validate_observation_descriptor(descriptor)

    calendar, calendar_sha = load_halving_calendar_v1(
        repo
    )
    component = build_btc_cycle_halving_context_v1_component(
        observation_descriptor=descriptor,
        halving_calendar=calendar,
        calendar_sha256=calendar_sha,
        produced_at_utc=produced_at_utc,
    )
    validate_btc_cycle_halving_context_v1_component(
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
            "calendar_resource_path": str(RESOURCE_PATH),
            "calendar_resource_sha256": calendar_sha,
            "reference_boundary_utc": descriptor[
                "reference_boundary_utc"
            ],
            "context_cutoff_utc": descriptor[
                "synchronized_context_available_at_utc"
            ],
            "produced_at_utc": _utc(
                _parse_utc(
                    produced_at_utc,
                    "produced_at_utc",
                )
            ),
            "component_status": component["status"],
            "point_in_time_eligible_under_pack_policy":
                compatibility["point_in_time_eligible"],
            "pack_eligibility_reason":
                compatibility["eligibility_reason"],
            "real_network_request_executed": False,
            "market_data_acquired": False,
            "git_network_request_executed": False,
            "price_input_used": False,
            "future_outcomes_used": False,
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
        validate_btc_cycle_halving_context_v1_package(
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
        validate_btc_cycle_halving_context_v1_package(
            output
        )
    )

    return {
        "capability": CAPABILITY,
        "feature_id": FEATURE_ID,
        "output_directory": str(output),
        "component_status": validation["status"],
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
    "RESOURCE_PATH",
    "SOURCE_KIND",
    "BtcCycleHalvingContextError",
    "build_btc_cycle_halving_context_v1_component",
    "load_halving_calendar_v1",
    "prepare_btc_cycle_halving_context_v1_package",
    "validate_btc_cycle_halving_context_v1_component",
    "validate_btc_cycle_halving_context_v1_package",
    "validate_component_against_level_a_pack_v1",
    "validate_halving_calendar_v1",
]
