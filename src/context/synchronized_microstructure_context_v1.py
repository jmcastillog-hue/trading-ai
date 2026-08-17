from __future__ import annotations

import hashlib
import json
import os
import shutil
import uuid
from copy import deepcopy
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Mapping

from src.context.context_feature_pack_v1_level_a_standard import (
    FEATURE_REGISTRY,
    build_context_feature_pack_v1,
)
from src.exchange.public_read_only_microstructure_snapshot_v1_1 import (
    validate_public_read_only_microstructure_snapshot_v1_1,
)
from src.long_side.synchronized_15m_observation_v1_1 import (
    HISTORICAL_COMPONENT_NAMES,
    TEMPORAL_ALIGNMENT_POLICY_VERSION,
    build_microstructure_context_v1_1,
)

CAPABILITY = "SYNCHRONIZED_MICROSTRUCTURE_CONTEXT_V1"
FEATURE_ID = "SYNCHRONIZED_MICROSTRUCTURE_CONTEXT_V1"
FEATURE_SCHEMA_VERSION = "SYNCHRONIZED_MICROSTRUCTURE_CONTEXT_V1_SCHEMA_V1"
PACKAGE_SCHEMA_VERSION = "SYNCHRONIZED_MICROSTRUCTURE_CONTEXT_V1_PACKAGE_V1"
SOURCE_KIND = "OBSERVED_MARKET"

PACKAGE_AUTHORIZATION = "PREPARE_SYNCHRONIZED_MICROSTRUCTURE_CONTEXT_V1"

MAX_IMPLEMENTATION_OR_REPAIR_ATTEMPTS = 10
IMPLEMENTATION_OR_REPAIR_ATTEMPT = 1

POLICY_PATH = Path(
    "src/context/resources/synchronized_microstructure_context_policy_v1.json"
)
EXPECTED_POLICY_SCHEMA_VERSION = "SYNCHRONIZED_MICROSTRUCTURE_CONTEXT_POLICY_V1"

EXPECTED_SNAPSHOT_CAPABILITY = "PUBLIC_READ_ONLY_MICROSTRUCTURE_SNAPSHOT_V1_1"
EXPECTED_PROVIDER = "BINANCE_USDM_PUBLIC_REST"
EXPECTED_SYMBOL = "BTCUSDT"
EXPECTED_TIMEFRAME = "15m"
EXPECTED_DEPTH_LIMIT = 1000
EXPECTED_DEPTH_BANDS_BPS = (5, 10, 25, 50)
REQUIRED_DEPTH_BANDS_BPS = (5, 10)
OPTIONAL_DEPTH_BANDS_BPS = (25, 50)

SUMMARY_FILENAME = "microstructure_snapshot.json"
SOURCE_MANIFEST_FILENAME = "manifest.sha256"

COMPONENT_FILENAME = "synchronized_microstructure_context_component.json"
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


class SynchronizedMicrostructureContextError(RuntimeError):
    def __init__(self, code: str, message: str) -> None:
        self.code = code
        super().__init__(message)


def _req(ok: bool, code: str, message: str) -> None:
    if not ok:
        raise SynchronizedMicrostructureContextError(code, message)


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
        raise SynchronizedMicrostructureContextError(
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
        raise SynchronizedMicrostructureContextError(
            code,
            str(path),
        ) from exc

    _req(
        isinstance(value, Mapping),
        code,
        str(path),
    )
    return dict(value)


def validate_synchronized_microstructure_context_policy_v1(
    policy: Mapping[str, Any],
) -> dict[str, Any]:
    _req(
        isinstance(policy, Mapping),
        "POLICY_INVALID",
        "mapping required",
    )
    _req(
        policy.get("schema_version")
        == EXPECTED_POLICY_SCHEMA_VERSION,
        "POLICY_SCHEMA_INVALID",
        str(policy.get("schema_version")),
    )
    _req(
        policy.get("feature_id") == FEATURE_ID,
        "POLICY_FEATURE_ID_INVALID",
        str(policy.get("feature_id")),
    )

    effective = _parse_utc(
        policy.get("policy_effective_from_utc"),
        "policy_effective_from_utc",
    )

    _req(
        policy.get("source_snapshot_capability")
        == EXPECTED_SNAPSHOT_CAPABILITY,
        "POLICY_SOURCE_CAPABILITY_INVALID",
        str(policy.get("source_snapshot_capability")),
    )
    _req(
        policy.get("source_provider") == EXPECTED_PROVIDER,
        "POLICY_PROVIDER_INVALID",
        str(policy.get("source_provider")),
    )
    _req(
        policy.get("source_symbol") == EXPECTED_SYMBOL
        and policy.get("source_timeframe") == EXPECTED_TIMEFRAME,
        "POLICY_IDENTITY_INVALID",
        "symbol/timeframe",
    )
    _req(
        int(policy.get("source_depth_limit", -1))
        == EXPECTED_DEPTH_LIMIT,
        "POLICY_DEPTH_LIMIT_INVALID",
        str(policy.get("source_depth_limit")),
    )
    _req(
        tuple(int(x) for x in policy.get("source_depth_bands_bps", []))
        == EXPECTED_DEPTH_BANDS_BPS,
        "POLICY_DEPTH_BANDS_INVALID",
        str(policy.get("source_depth_bands_bps")),
    )
    _req(
        tuple(int(x) for x in policy.get("required_depth_bands_bps", []))
        == REQUIRED_DEPTH_BANDS_BPS,
        "POLICY_REQUIRED_DEPTH_BANDS_INVALID",
        str(policy.get("required_depth_bands_bps")),
    )
    _req(
        tuple(int(x) for x in policy.get("optional_depth_bands_bps", []))
        == OPTIONAL_DEPTH_BANDS_BPS,
        "POLICY_OPTIONAL_DEPTH_BANDS_INVALID",
        str(policy.get("optional_depth_bands_bps")),
    )
    _req(
        policy.get("temporal_alignment_policy_version")
        == TEMPORAL_ALIGNMENT_POLICY_VERSION,
        "POLICY_TEMPORAL_ALIGNMENT_VERSION_INVALID",
        str(policy.get("temporal_alignment_policy_version")),
    )

    for field in (
        "historical_component_exact_reference_boundary_equality_required",
        "misaligned_historical_component_preserved_but_not_usable",
        "point_in_time_components_are_not_historical_reconstruction",
        "retrospective_source_before_policy_effective_is_not_point_in_time_eligible",
    ):
        _req(
            policy.get(field) is True,
            "POLICY_REQUIRED_GUARD_INVALID",
            field,
        )

    for field in (
        "directional_meaning_assigned",
        "composite_score_assigned",
        "signal_semantics",
    ):
        _req(
            policy.get(field) is False,
            "POLICY_FORBIDDEN_SEMANTIC_ENABLED",
            field,
        )

    return {
        "policy_effective_from_utc": _utc(effective),
        "source_depth_limit": EXPECTED_DEPTH_LIMIT,
        "source_depth_bands_bps": list(EXPECTED_DEPTH_BANDS_BPS),
        "temporal_alignment_policy_version":
            TEMPORAL_ALIGNMENT_POLICY_VERSION,
    }


def load_synchronized_microstructure_context_policy_v1(
    repo_root: Path | str,
) -> tuple[dict[str, Any], str]:
    repo = Path(repo_root).resolve()
    path = repo / POLICY_PATH
    policy = _read_json_mapping(
        path,
        "POLICY_FILE_INVALID",
    )
    validate_synchronized_microstructure_context_policy_v1(
        policy
    )
    return policy, _sha(path)


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
        descriptor.get("symbol") == EXPECTED_SYMBOL,
        "OBSERVATION_SYMBOL_INVALID",
        str(descriptor.get("symbol")),
    )
    _req(
        descriptor.get("timeframe") == EXPECTED_TIMEFRAME,
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
    reference_close = _parse_utc(
        descriptor.get("reference_closed_candle_utc"),
        "reference_closed_candle_utc",
    )
    context_cutoff = _parse_utc(
        descriptor.get("synchronized_context_available_at_utc"),
        "synchronized_context_available_at_utc",
    )

    _req(
        reference - reference_close == timedelta(milliseconds=1),
        "REFERENCE_BOUNDARY_INVALID",
        "must be exactly 1ms after closed candle",
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


def _validate_summary_identity(
    summary: Mapping[str, Any],
    descriptor: Mapping[str, Any],
) -> dict[str, datetime]:
    _req(
        isinstance(summary, Mapping),
        "MICROSTRUCTURE_SUMMARY_INVALID",
        "mapping required",
    )
    _req(
        summary.get("capability") == EXPECTED_SNAPSHOT_CAPABILITY,
        "MICROSTRUCTURE_CAPABILITY_INVALID",
        str(summary.get("capability")),
    )
    _req(
        summary.get("provider") == EXPECTED_PROVIDER,
        "MICROSTRUCTURE_PROVIDER_INVALID",
        str(summary.get("provider")),
    )
    _req(
        summary.get("symbol") == EXPECTED_SYMBOL
        and summary.get("timeframe") == EXPECTED_TIMEFRAME,
        "MICROSTRUCTURE_IDENTITY_INVALID",
        "symbol/timeframe",
    )
    _req(
        int(summary.get("request_count", -1)) == 7,
        "MICROSTRUCTURE_REQUEST_COUNT_INVALID",
        str(summary.get("request_count")),
    )
    _req(
        int(summary.get("depth_limit_requested", -1))
        == EXPECTED_DEPTH_LIMIT,
        "MICROSTRUCTURE_DEPTH_LIMIT_INVALID",
        str(summary.get("depth_limit_requested")),
    )
    _req(
        tuple(
            int(x)
            for x in summary.get("depth_bands_bps", [])
        )
        == EXPECTED_DEPTH_BANDS_BPS,
        "MICROSTRUCTURE_DEPTH_BANDS_INVALID",
        str(summary.get("depth_bands_bps")),
    )

    reference = _parse_utc(
        descriptor["reference_boundary_utc"],
        "reference_boundary_utc",
    )
    reference_close = _parse_utc(
        descriptor["reference_closed_candle_utc"],
        "reference_closed_candle_utc",
    )
    context_cutoff = _parse_utc(
        descriptor["synchronized_context_available_at_utc"],
        "synchronized_context_available_at_utc",
    )

    source_close = _parse_utc(
        summary.get("reference_closed_candle_utc"),
        "summary.reference_closed_candle_utc",
    )
    source_boundary = _parse_utc(
        summary.get("synchronization", {}).get(
            "reference_boundary_utc"
        ),
        "summary.synchronization.reference_boundary_utc",
    )
    captured_finished = _parse_utc(
        summary.get("captured_finished_at_utc"),
        "summary.captured_finished_at_utc",
    )

    _req(
        source_close == reference_close,
        "REFERENCE_CLOSED_CANDLE_MISMATCH",
        _utc(source_close),
    )
    _req(
        source_boundary == reference,
        "REFERENCE_BOUNDARY_MISMATCH",
        _utc(source_boundary),
    )
    _req(
        captured_finished == context_cutoff,
        "CONTEXT_AVAILABILITY_MISMATCH",
        (
            f"captured={_utc(captured_finished)} "
            f"descriptor={_utc(context_cutoff)}"
        ),
    )

    return {
        "reference": reference,
        "reference_close": reference_close,
        "context_cutoff": context_cutoff,
        "captured_finished": captured_finished,
    }


def _safe_band(
    context: Mapping[str, Any],
    bps: int,
) -> dict[str, Any]:
    raw = context["bands"][str(bps)]
    covered = bool(raw["coverage_complete"])

    return {
        "band_bps": bps,
        "coverage_complete": covered,
        "usable_for_context": bool(
            raw["usable_for_context"]
        ),
        "bid_level_count": int(raw["bid_level_count"]),
        "ask_level_count": int(raw["ask_level_count"]),
        "bid_notional_usdt": float(
            raw["bid_notional_usdt"]
        ),
        "ask_notional_usdt": float(
            raw["ask_notional_usdt"]
        ),
        "notional_imbalance_observed": float(
            raw["notional_imbalance_observed"]
        ),
        "notional_imbalance_usable": (
            float(raw["notional_imbalance_usable"])
            if raw["notional_imbalance_usable"] is not None
            else None
        ),
    }


def _historical_component_payload(
    context: Mapping[str, Any],
    name: str,
) -> dict[str, Any]:
    eligibility = context[
        "component_temporal_eligibility"
    ]["historical_components"][name]
    usable = bool(
        eligibility["usable_for_synchronized_context"]
    )

    if name == "open_interest_history":
        raw = context["open_interest"]
        values = (
            {
                "latest_sum_open_interest":
                    float(
                        raw["latest_15m"][
                            "sum_open_interest"
                        ]
                    ),
                "latest_sum_open_interest_value_usdt":
                    float(
                        raw["latest_15m"][
                            "sum_open_interest_value_usdt"
                        ]
                    ),
                "change_15m_percent": (
                    float(raw["change_15m_percent"])
                    if raw["change_15m_percent"] is not None
                    else None
                ),
                "value_change_15m_percent": (
                    float(raw["value_change_15m_percent"])
                    if raw["value_change_15m_percent"] is not None
                    else None
                ),
            }
            if usable
            else None
        )
    elif name == "taker_buy_sell_volume":
        raw = context["taker_buy_sell_volume"]
        values = (
            {
                "buy_volume_base":
                    float(
                        raw["latest_15m"][
                            "buy_volume_base"
                        ]
                    ),
                "sell_volume_base":
                    float(
                        raw["latest_15m"][
                            "sell_volume_base"
                        ]
                    ),
                "buy_sell_ratio":
                    float(
                        raw["latest_15m"][
                            "buy_sell_ratio"
                        ]
                    ),
                "net_taker_volume_base":
                    float(
                        raw["latest_15m"][
                            "net_taker_volume_base"
                        ]
                    ),
            }
            if usable
            else None
        )
    elif name == "global_long_short_account_ratio":
        raw = context[
            "global_long_short_account_ratio"
        ]
        values = (
            {
                "long_short_account_ratio":
                    float(
                        raw["latest_15m"][
                            "long_short_account_ratio"
                        ]
                    ),
                "long_account_fraction":
                    float(
                        raw["latest_15m"][
                            "long_account_fraction"
                        ]
                    ),
                "short_account_fraction":
                    float(
                        raw["latest_15m"][
                            "short_account_fraction"
                        ]
                    ),
            }
            if usable
            else None
        )
    else:
        raise SynchronizedMicrostructureContextError(
            "HISTORICAL_COMPONENT_NAME_INVALID",
            name,
        )

    return {
        "component_name": name,
        "timestamp_utc":
            eligibility["component_timestamp_utc"],
        "timestamp_delta_seconds":
            float(eligibility["timestamp_delta_seconds"]),
        "timestamp_equal_reference_boundary":
            bool(
                eligibility[
                    "timestamp_equal_reference_boundary"
                ]
            ),
        "usable_for_synchronized_context": usable,
        "misalignment_reason":
            eligibility["misalignment_reason"],
        "values": values,
        "misaligned_values_excluded_from_usable_payload":
            not usable,
    }


def build_synchronized_microstructure_context_v1_component(
    *,
    observation_descriptor: Mapping[str, Any],
    microstructure_summary: Mapping[str, Any],
    microstructure_snapshot_sha256: str,
    source_manifest_sha256: str,
    policy: Mapping[str, Any],
    policy_sha256: str,
    produced_at_utc: str,
) -> dict[str, Any]:
    descriptor = _validate_observation_descriptor(
        observation_descriptor
    )
    policy_validation = (
        validate_synchronized_microstructure_context_policy_v1(
            policy
        )
    )
    times = _validate_summary_identity(
        microstructure_summary,
        descriptor,
    )

    for name, digest in (
        (
            "microstructure_snapshot_sha256",
            microstructure_snapshot_sha256,
        ),
        ("source_manifest_sha256", source_manifest_sha256),
        ("policy_sha256", policy_sha256),
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

    produced_at = _parse_utc(
        produced_at_utc,
        "produced_at_utc",
    )
    policy_effective = _parse_utc(
        policy_validation["policy_effective_from_utc"],
        "policy_effective_from_utc",
    )

    _req(
        produced_at >= policy_effective,
        "PRODUCED_BEFORE_POLICY_EFFECTIVE",
        _utc(produced_at),
    )
    _req(
        produced_at >= times["captured_finished"],
        "PRODUCED_BEFORE_SOURCE_COMPLETE",
        _utc(produced_at),
    )

    context = build_microstructure_context_v1_1(
        microstructure_summary
    )

    eligibility = context[
        "component_temporal_eligibility"
    ]
    _req(
        eligibility["policy_version"]
        == TEMPORAL_ALIGNMENT_POLICY_VERSION,
        "TEMPORAL_POLICY_VERSION_INVALID",
        str(eligibility["policy_version"]),
    )
    _req(
        eligibility[
            "exact_reference_boundary_equality_required"
        ]
        is True,
        "TEMPORAL_EXACT_EQUALITY_GUARD_INVALID",
        "exact equality",
    )
    _req(
        eligibility[
            "misaligned_historical_component_preserved_but_not_usable"
        ]
        is True,
        "MISALIGNED_PRESERVATION_GUARD_INVALID",
        "misaligned",
    )
    _req(
        eligibility[
            "point_in_time_components_are_not_historical_reconstruction"
        ]
        is True,
        "POINT_IN_TIME_RECONSTRUCTION_GUARD_INVALID",
        "point in time",
    )

    aligned = list(
        eligibility["aligned_historical_components"]
    )
    misaligned = list(
        eligibility["misaligned_historical_components"]
    )

    component_available_at = max(
        times["captured_finished"],
        policy_effective,
    )
    retrospective_floor_applied = (
        times["captured_finished"] < policy_effective
    )

    depth_bands = {
        str(bps): _safe_band(context, bps)
        for bps in EXPECTED_DEPTH_BANDS_BPS
    }

    historical = {
        name: _historical_component_payload(
            context,
            name,
        )
        for name in HISTORICAL_COMPONENT_NAMES
    }

    current_oi_temporal = eligibility[
        "point_in_time_components"
    ]["current_open_interest"]
    mark_temporal = eligibility[
        "point_in_time_components"
    ]["mark_price_funding"]

    payload = {
        "model_semantics":
            "DESCRIPTIVE_SYNCHRONIZED_MICROSTRUCTURE_CONTEXT_ONLY",
        "reference_closed_candle_utc":
            descriptor["reference_closed_candle_utc"],
        "reference_boundary_utc":
            descriptor["reference_boundary_utc"],
        "context_cutoff_utc":
            descriptor[
                "synchronized_context_available_at_utc"
            ],
        "source_snapshot_capability":
            microstructure_summary["capability"],
        "source_provider":
            microstructure_summary["provider"],
        "source_captured_finished_at_utc":
            microstructure_summary[
                "captured_finished_at_utc"
            ],
        "source_manifest_sha256":
            source_manifest_sha256,
        "policy_sha256":
            policy_sha256,
        "policy_effective_from_utc":
            policy_validation[
                "policy_effective_from_utc"
            ],
        "retrospective_policy_floor_applied":
            retrospective_floor_applied,
        "producer_generated_at_utc":
            _utc(produced_at),
        "temporal_alignment_policy_version":
            TEMPORAL_ALIGNMENT_POLICY_VERSION,
        "historical_component_exact_reference_boundary_equality_required":
            True,
        "aligned_historical_components": aligned,
        "misaligned_historical_components": misaligned,
        "all_historical_components_timestamp_aligned":
            len(misaligned) == 0,
        "misaligned_historical_component_preserved_in_source_but_not_usable":
            True,
        "historical_components": historical,
        "point_in_time_components_are_not_historical_reconstruction":
            True,
        "point_in_time_components": {
            "current_open_interest": {
                "provider_time_utc":
                    current_oi_temporal[
                        "component_timestamp_utc"
                    ],
                "observed_at_or_after_reference":
                    current_oi_temporal[
                        "observed_at_or_after_reference"
                    ],
                "current_open_interest_base":
                    float(
                        context["open_interest"][
                            "current_open_interest_base"
                        ]
                    ),
                "current_open_interest_approx_usdt_at_mark":
                    float(
                        context["open_interest"][
                            "current_open_interest_approx_usdt_at_mark"
                        ]
                    ),
            },
            "mark_price_funding": {
                "provider_time_utc":
                    mark_temporal[
                        "component_timestamp_utc"
                    ],
                "observed_at_or_after_reference":
                    mark_temporal[
                        "observed_at_or_after_reference"
                    ],
                "mark_price":
                    float(
                        context["mark_price_funding"][
                            "mark_price"
                        ]
                    ),
                "index_price":
                    float(
                        context["mark_price_funding"][
                            "index_price"
                        ]
                    ),
                "mark_index_basis_bps":
                    float(
                        context["mark_price_funding"][
                            "mark_index_basis_bps"
                        ]
                    ),
                "last_funding_rate_percent":
                    float(
                        context["mark_price_funding"][
                            "last_funding_rate_percent"
                        ]
                    ),
            },
            "order_book": {
                "best_bid": float(context["best_bid"]),
                "best_ask": float(context["best_ask"]),
                "mid_price": float(context["mid_price"]),
                "spread_bps": float(
                    context["spread_bps"]
                ),
                "resting_visible_depth_only": True,
                "hidden_stops_or_liquidations_revealed":
                    False,
            },
        },
        "depth": {
            "depth_limit_requested":
                int(context["depth_limit_requested"]),
            "depth_bands_bps":
                list(context["depth_bands_bps"]),
            "required_depth_bands_bps":
                list(context["required_depth_bands_bps"]),
            "optional_depth_bands_bps":
                list(context["optional_depth_bands_bps"]),
            "complete_bands_bps":
                list(context["complete_bands_bps"]),
            "incomplete_bands_bps":
                list(context["incomplete_bands_bps"]),
            "minimum_depth_context_usable":
                bool(
                    context[
                        "minimum_depth_context_usable"
                    ]
                ),
            "incomplete_depth_extrapolation_allowed":
                False,
            "bands": depth_bands,
        },
        "order_book_resting_visible_depth_only": True,
        "order_book_hidden_stops_or_liquidations_revealed":
            False,
        "open_interest_identifies_long_vs_short_direction":
            False,
        "funding_and_ratios_actionable":
            False,
        "market_data_acquired_by_producer": False,
        "future_outcomes_used": False,
        "directional_semantics": False,
        "signal_semantics": False,
        "composite_score_assigned": False,
        "candidate_modification_semantics": False,
    }

    component = {
        "feature_id": FEATURE_ID,
        "source_kind": SOURCE_KIND,
        "feature_schema_version":
            FEATURE_SCHEMA_VERSION,
        "status": "AVAILABLE",
        "reason": None,
        "available_at_utc":
            _utc(component_available_at),
        "information_cutoff_utc":
            _utc(times["captured_finished"]),
        "source_artifact_sha256":
            microstructure_snapshot_sha256,
        "payload": payload,
    }

    validate_synchronized_microstructure_context_v1_component(
        component
    )
    return component


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
        "reason":
            "not configured for producer integration check",
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
        str(item["feature_id"]):
            _not_configured_component(item)
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


def validate_synchronized_microstructure_context_v1_component(
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
        == "DESCRIPTIVE_SYNCHRONIZED_MICROSTRUCTURE_CONTEXT_ONLY",
        "PAYLOAD_SEMANTICS_INVALID",
        str(payload.get("model_semantics")),
    )

    for field in (
        "market_data_acquired_by_producer",
        "future_outcomes_used",
        "directional_semantics",
        "signal_semantics",
        "composite_score_assigned",
        "candidate_modification_semantics",
        "order_book_hidden_stops_or_liquidations_revealed",
        "open_interest_identifies_long_vs_short_direction",
        "funding_and_ratios_actionable",
    ):
        _req(
            payload.get(field) is False,
            "FORBIDDEN_PAYLOAD_SEMANTIC_ENABLED",
            field,
        )

    _req(
        payload.get(
            "historical_component_exact_reference_boundary_equality_required"
        )
        is True,
        "HISTORICAL_ALIGNMENT_GUARD_INVALID",
        "exact equality",
    )
    _req(
        payload.get(
            "misaligned_historical_component_preserved_in_source_but_not_usable"
        )
        is True,
        "MISALIGNED_GUARD_INVALID",
        "misaligned",
    )
    _req(
        payload.get(
            "point_in_time_components_are_not_historical_reconstruction"
        )
        is True,
        "POINT_IN_TIME_GUARD_INVALID",
        "point in time",
    )

    depth = payload.get("depth")
    _req(
        isinstance(depth, Mapping),
        "DEPTH_PAYLOAD_INVALID",
        "depth",
    )
    _req(
        int(depth.get("depth_limit_requested", -1))
        == EXPECTED_DEPTH_LIMIT,
        "DEPTH_LIMIT_INVALID",
        str(depth.get("depth_limit_requested")),
    )
    _req(
        tuple(int(x) for x in depth.get("depth_bands_bps", []))
        == EXPECTED_DEPTH_BANDS_BPS,
        "DEPTH_BANDS_INVALID",
        str(depth.get("depth_bands_bps")),
    )
    _req(
        depth.get(
            "incomplete_depth_extrapolation_allowed"
        )
        is False,
        "DEPTH_EXTRAPOLATION_PROHIBITED",
        "incomplete depth",
    )

    historical = payload.get("historical_components")
    _req(
        isinstance(historical, Mapping)
        and set(historical.keys())
        == set(HISTORICAL_COMPONENT_NAMES),
        "HISTORICAL_COMPONENT_SCOPE_INVALID",
        str(historical.keys())
        if isinstance(historical, Mapping)
        else "not mapping",
    )

    usable_count = 0
    misaligned_count = 0

    for name in HISTORICAL_COMPONENT_NAMES:
        item = historical[name]
        usable = bool(
            item["usable_for_synchronized_context"]
        )
        if usable:
            usable_count += 1
            _req(
                isinstance(item["values"], Mapping),
                "USABLE_HISTORICAL_VALUES_MISSING",
                name,
            )
            _req(
                item[
                    "timestamp_equal_reference_boundary"
                ]
                is True,
                "USABLE_HISTORICAL_TIMESTAMP_INVALID",
                name,
            )
        else:
            misaligned_count += 1
            _req(
                item["values"] is None,
                "MISALIGNED_VALUES_MUST_BE_EXCLUDED",
                name,
            )
            _req(
                item[
                    "misaligned_values_excluded_from_usable_payload"
                ]
                is True,
                "MISALIGNED_EXCLUSION_GUARD_INVALID",
                name,
            )

    return {
        "status": "AVAILABLE",
        "aligned_historical_component_count":
            usable_count,
        "misaligned_historical_component_count":
            misaligned_count,
        "minimum_depth_context_usable":
            bool(
                depth["minimum_depth_context_usable"]
            ),
        "retrospective_policy_floor_applied":
            bool(
                payload[
                    "retrospective_policy_floor_applied"
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
        for line in path.read_text(
            encoding="utf-8"
        ).splitlines()
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
            name in (
                CHECKS_FILENAME,
                COMPONENT_FILENAME,
            ),
            "PACKAGE_MANIFEST_SCOPE_INVALID",
            name,
        )
        candidate = directory / name
        _req(
            candidate.is_file()
            and not candidate.is_symlink(),
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
        set(seen)
        == {CHECKS_FILENAME, COMPONENT_FILENAME},
        "PACKAGE_MANIFEST_SCOPE_INVALID",
        str(sorted(seen)),
    )
    return seen


def validate_synchronized_microstructure_context_v1_package(
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
        validate_synchronized_microstructure_context_v1_component(
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
        "market_data_acquired_by_producer",
        "git_network_request_executed",
        "future_outcomes_used",
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
        "point_in_time_eligible_under_pack_policy":
            bool(
                checks[
                    "point_in_time_eligible_under_pack_policy"
                ]
            ),
        "real_network_request_executed": False,
        "official_append_executed": False,
    }


def prepare_synchronized_microstructure_context_v1_package(
    *,
    repo_root: Path | str,
    observation_descriptor_json: Path | str,
    microstructure_snapshot_directory: Path | str,
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
    source_directory = Path(
        microstructure_snapshot_directory
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
        output.parent.is_dir()
        and not output.parent.is_symlink(),
        "OUTPUT_PARENT_INVALID",
        str(output.parent),
    )
    _req(
        not output.exists()
        and not output.is_symlink(),
        "OUTPUT_ALREADY_EXISTS",
        str(output),
    )
    _req(
        not _inside(descriptor_path, repo),
        "DESCRIPTOR_INSIDE_REPOSITORY_PROHIBITED",
        str(descriptor_path),
    )
    _req(
        not _inside(source_directory, repo),
        "SOURCE_SNAPSHOT_INSIDE_REPOSITORY_PROHIBITED",
        str(source_directory),
    )
    _req(
        source_directory.is_dir()
        and not source_directory.is_symlink(),
        "SOURCE_SNAPSHOT_DIRECTORY_INVALID",
        str(source_directory),
    )

    official_before = _official(repo)

    descriptor = _read_json_mapping(
        descriptor_path,
        "OBSERVATION_DESCRIPTOR_FILE_INVALID",
    )
    _validate_observation_descriptor(descriptor)

    source_validation = (
        validate_public_read_only_microstructure_snapshot_v1_1(
            source_directory
        )
    )
    _req(
        int(source_validation["request_count"]) == 7,
        "SOURCE_VALIDATION_REQUEST_COUNT_INVALID",
        str(source_validation["request_count"]),
    )
    _req(
        int(
            source_validation[
                "depth_limit_requested"
            ]
        )
        == EXPECTED_DEPTH_LIMIT,
        "SOURCE_VALIDATION_DEPTH_LIMIT_INVALID",
        str(
            source_validation[
                "depth_limit_requested"
            ]
        ),
    )

    summary_path = (
        source_directory / SUMMARY_FILENAME
    )
    source_manifest_path = (
        source_directory / SOURCE_MANIFEST_FILENAME
    )
    summary = _read_json_mapping(
        summary_path,
        "SOURCE_SUMMARY_INVALID",
    )
    _req(
        source_manifest_path.is_file()
        and not source_manifest_path.is_symlink(),
        "SOURCE_MANIFEST_INVALID",
        str(source_manifest_path),
    )

    policy, policy_sha = (
        load_synchronized_microstructure_context_policy_v1(
            repo
        )
    )

    component = (
        build_synchronized_microstructure_context_v1_component(
            observation_descriptor=descriptor,
            microstructure_summary=summary,
            microstructure_snapshot_sha256=
                _sha(summary_path),
            source_manifest_sha256=
                _sha(source_manifest_path),
            policy=policy,
            policy_sha256=policy_sha,
            produced_at_utc=produced_at_utc,
        )
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
            "package_schema_version":
                PACKAGE_SCHEMA_VERSION,
            "capability": CAPABILITY,
            "feature_id": FEATURE_ID,
            "observation_descriptor_sha256":
                _sha(descriptor_path),
            "source_microstructure_summary_sha256":
                _sha(summary_path),
            "source_microstructure_manifest_sha256":
                _sha(source_manifest_path),
            "policy_resource_sha256":
                policy_sha,
            "produced_at_utc":
                _utc(
                    _parse_utc(
                        produced_at_utc,
                        "produced_at_utc",
                    )
                ),
            "component_available_at_utc":
                component["available_at_utc"],
            "component_information_cutoff_utc":
                component[
                    "information_cutoff_utc"
                ],
            "point_in_time_eligible_under_pack_policy":
                compatibility[
                    "point_in_time_eligible"
                ],
            "pack_eligibility_reason":
                compatibility[
                    "eligibility_reason"
                ],
            "source_snapshot_was_preexisting":
                True,
            "source_snapshot_validated_locally":
                True,
            "real_network_request_executed":
                False,
            "market_data_acquired_by_producer":
                False,
            "git_network_request_executed":
                False,
            "future_outcomes_used": False,
            "direction_inferred": False,
            "signal_generated": False,
            "candidate_modified": False,
            "primary_rule_modified": False,
            "official_append_executed": False,
            "official_dataset_changed": False,
            "official_manifest_changed": False,
            **{
                field: False
                for field in FALSE_PERMISSION_FIELDS
            },
        }

        _write_new(
            temp / CHECKS_FILENAME,
            _json_bytes(checks),
        )
        _write_manifest(temp)

        validate_synchronized_microstructure_context_v1_package(
            temp
        )

        temp.rename(output)
    except Exception:
        if temp.exists():
            shutil.rmtree(
                temp,
                ignore_errors=True,
            )
        if output.exists():
            shutil.rmtree(
                output,
                ignore_errors=True,
            )
        raise

    _req(
        _official(repo) == official_before,
        "OFFICIAL_ARTIFACT_CHANGED",
        "after output",
    )
    _official_gate_off()

    validation = (
        validate_synchronized_microstructure_context_v1_package(
            output
        )
    )

    return {
        "capability": CAPABILITY,
        "feature_id": FEATURE_ID,
        "output_directory": str(output),
        "component_status":
            validation["status"],
        "aligned_historical_component_count":
            validation[
                "aligned_historical_component_count"
            ],
        "misaligned_historical_component_count":
            validation[
                "misaligned_historical_component_count"
            ],
        "minimum_depth_context_usable":
            validation[
                "minimum_depth_context_usable"
            ],
        "retrospective_policy_floor_applied":
            validation[
                "retrospective_policy_floor_applied"
            ],
        "point_in_time_eligible_under_pack_policy":
            validation[
                "point_in_time_eligible_under_pack_policy"
            ],
        "real_network_request_executed": False,
        "market_data_acquired_by_producer": False,
        "git_network_request_executed": False,
        "official_append_executed": False,
        **{
            field: False
            for field in FALSE_PERMISSION_FIELDS
        },
    }


__all__ = [
    "CAPABILITY",
    "FEATURE_ID",
    "FEATURE_SCHEMA_VERSION",
    "IMPLEMENTATION_OR_REPAIR_ATTEMPT",
    "MAX_IMPLEMENTATION_OR_REPAIR_ATTEMPTS",
    "PACKAGE_AUTHORIZATION",
    "POLICY_PATH",
    "SOURCE_KIND",
    "SynchronizedMicrostructureContextError",
    "build_synchronized_microstructure_context_v1_component",
    "load_synchronized_microstructure_context_policy_v1",
    "prepare_synchronized_microstructure_context_v1_package",
    "validate_component_against_level_a_pack_v1",
    "validate_synchronized_microstructure_context_policy_v1",
    "validate_synchronized_microstructure_context_v1_component",
    "validate_synchronized_microstructure_context_v1_package",
]
