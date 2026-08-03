from __future__ import annotations

import csv
import ctypes
import hashlib
import io
import json
import math
import os
import socket
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

from src.long_side import (
    long_forward_observation_phase_10_44_official_dataset_atomic_write_harness_implementation_v1
    as atomic_create_only,
)

CAPABILITY = "LONG_OFFICIAL_PROSPECTIVE_EVIDENCE_APPEND_V1"
IMPLEMENTATION_SCHEMA_VERSION = (
    "LONG_OFFICIAL_PROSPECTIVE_EVIDENCE_APPEND_IMPLEMENTATION_V1"
)
MANIFEST_SCHEMA_V1 = "LONG_OFFICIAL_DATASET_MANIFEST_V1"
MANIFEST_SCHEMA_V2 = "LONG_OFFICIAL_DATASET_APPEND_MANIFEST_V2"
OFFICIAL_DATASET_RELATIVE_PATH = Path(
    "data/forward/long_forward_observation_dataset_v1.csv"
)
OFFICIAL_MANIFEST_RELATIVE_PATH = Path(
    "data/forward/long_forward_observation_dataset_v1.manifest.csv"
)
OFFICIAL_LOCK_RELATIVE_PATH = Path(
    "data/forward/long_forward_observation_dataset_v1.lock"
)
OFFICIAL_APPEND_AUTHORIZATION = (
    "TRADING_AI_OFFICIAL_LONG_PROSPECTIVE_EVIDENCE_APPEND_V1"
)
OFFICIAL_APPEND_ENVIRONMENT_VARIABLE = (
    "TRADING_AI_OFFICIAL_LONG_EVIDENCE_APPEND_ALLOWED"
)
SANDBOX_APPEND_AUTHORIZATION = "SANDBOX_LONG_PROSPECTIVE_EVIDENCE_APPEND_V1"
GENESIS_EVIDENCE_HASH = "0" * 64
EXPECTED_COLUMN_COUNT = 54
EXPECTED_RISK_REWARD = 2.5

CANONICAL_COLUMNS = (
    "evidence_id",
    "observation_id",
    "collected_at_utc",
    "observed_at_utc",
    "source_system",
    "source_artifact",
    "source_artifact_sha256",
    "source_row_hash",
    "candidate_id",
    "direction",
    "symbol",
    "timeframe",
    "observation_state",
    "evidence_status",
    "evidence_scope",
    "evidence_version",
    "entry_price",
    "stop_price",
    "target_price",
    "invalidation_level",
    "risk_reward",
    "cost_profile",
    "market_context",
    "activation_scope",
    "signal_state",
    "deduplication_key",
    "deduplication_status",
    "lifecycle_state",
    "review_status",
    "rejection_reason",
    "manual_confirmation_required",
    "manual_confirmed",
    "write_ahead_validation_passed",
    "schema_validation_passed",
    "provenance_validation_passed",
    "risk_structure_validation_passed",
    "evidence_hash",
    "previous_evidence_hash",
    "audit_event_id",
    "created_by",
    "reviewed_by",
    "rollback_reference",
    "accepted_as_real_evidence",
    "official_dataset_write_allowed",
    "evidence_persistence_allowed",
    "signal_generation_enabled",
    "live_alerts_allowed",
    "paper_trade_execution_allowed",
    "real_capital_allowed",
    "market_execution_allowed",
    "exchange_execution_allowed",
    "automation_allowed",
    "execution_allowed",
    "notes",
)

MANIFEST_V2_FIELDS = (
    "manifest_schema_version",
    "capability",
    "operation_id",
    "created_at_utc",
    "previous_manifest_sha256",
    "previous_dataset_sha256",
    "previous_evidence_row_count",
    "target_filename",
    "target_canonical_path",
    "target_sha256",
    "target_size_bytes",
    "target_column_count",
    "target_evidence_row_count",
    "appended_evidence_id",
    "appended_evidence_hash",
    "appended_deduplication_key",
    "appended_rows_this_operation",
    "publication_primitive",
    "append_only",
    "replacement_scope",
    "existing_target_replacement_allowed",
    "official_dataset_path_used",
    "official_evidence_rows_written",
    "automatic_recovery_allowed",
    "signal_generation_enabled",
    "live_alerts_allowed",
    "paper_trade_execution_allowed",
    "real_capital_allowed",
    "market_execution_allowed",
    "exchange_execution_allowed",
    "automation_allowed",
    "execution_allowed",
    "human_review_required",
    "manual_confirmation_required",
    "manual_confirmed",
)

EXECUTION_FALSE_COLUMNS = (
    "signal_generation_enabled",
    "live_alerts_allowed",
    "paper_trade_execution_allowed",
    "real_capital_allowed",
    "market_execution_allowed",
    "exchange_execution_allowed",
    "automation_allowed",
    "execution_allowed",
)

APPEND_TRUE_COLUMNS = (
    "manual_confirmation_required",
    "manual_confirmed",
    "write_ahead_validation_passed",
    "schema_validation_passed",
    "provenance_validation_passed",
    "risk_structure_validation_passed",
    "accepted_as_real_evidence",
    "official_dataset_write_allowed",
    "evidence_persistence_allowed",
)

ALLOWED_CANDIDATE_IDS = {
    "LONG_BASE_FAILED_BREAKDOWN_V1",
    "LONG_BASE_LIQUIDITY_SWEEP_V1",
}
ALLOWED_OBSERVATION_STATES = {
    "OBSERVED_OPEN",
    "RESOLVED_TARGET",
    "RESOLVED_STOP",
    "RESOLVED_TIMEOUT",
    "INVALIDATED",
}
ALLOWED_LIFECYCLE_STATES = {"OPEN", "CLOSED", "INVALIDATED"}
FAILPOINTS = {
    "AFTER_LOCK_ACQUIRED",
    "AFTER_TEMPS_DURABLE",
    "AFTER_DATASET_REPLACED",
    "AFTER_MANIFEST_REPLACED",
}


class OfficialEvidenceAppendError(RuntimeError):
    def __init__(
        self,
        code: str,
        message: str,
        *,
        operation_id: str = "",
        rollback_performed: bool = False,
    ) -> None:
        self.code = code
        self.operation_id = operation_id
        self.rollback_performed = rollback_performed
        super().__init__(message)


class InjectedAppendFailure(OfficialEvidenceAppendError):
    pass


@dataclass(frozen=True)
class ReviewedLongEvidenceInput:
    observation_id: str
    observed_at_utc: str
    source_system: str
    source_artifact: str
    source_artifact_sha256: str
    source_row_hash: str
    candidate_id: str
    direction: str
    symbol: str
    timeframe: str
    observation_state: str
    lifecycle_state: str
    entry_price: float
    stop_price: float
    target_price: float
    invalidation_level: float
    risk_reward: float
    cost_profile: str
    market_context: str
    activation_scope: str
    signal_state: str
    audit_event_id: str
    created_by: str
    reviewed_by: str
    notes: str = ""
    review_status: str = "HUMAN_REVIEW_APPROVED_FOR_OFFICIAL_EVIDENCE"
    manual_confirmation_required: bool = True
    manual_confirmed: bool = True
    write_ahead_validation_passed: bool = True
    schema_validation_passed: bool = True
    provenance_validation_passed: bool = True
    risk_structure_validation_passed: bool = True


@dataclass(frozen=True)
class AppendPaths:
    dataset: Path
    manifest: Path
    lock: Path
    dataset_temp: Path
    manifest_temp: Path
    dataset_backup: Path
    manifest_backup: Path


def _require(condition: bool, code: str, message: str) -> None:
    if not condition:
        raise OfficialEvidenceAppendError(code, message)


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _canonical_json_bytes(value: Mapping[str, Any]) -> bytes:
    return (
        json.dumps(
            dict(value),
            sort_keys=False,
            separators=(",", ":"),
            ensure_ascii=True,
            allow_nan=False,
        )
        + "\n"
    ).encode("utf-8")


def _is_sha256(value: str) -> bool:
    text = str(value).strip().lower()
    return len(text) == 64 and all(character in "0123456789abcdef" for character in text)


def _bool_text(value: bool) -> str:
    return "True" if value else "False"


def _parse_bool_text(value: str, field: str) -> bool:
    _require(value in {"True", "False"}, "BOOLEAN_FIELD_INVALID", f"Invalid boolean value for {field}.")
    return value == "True"


def _parse_int(value: str, field: str) -> int:
    try:
        return int(value)
    except (TypeError, ValueError) as exc:
        raise OfficialEvidenceAppendError(
            "INTEGER_FIELD_INVALID",
            f"Invalid integer value for {field}.",
        ) from exc


def _number_text(value: Any, field: str) -> str:
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise OfficialEvidenceAppendError(
            "NUMERIC_FIELD_INVALID",
            f"Invalid numeric value for {field}.",
        ) from exc
    _require(math.isfinite(number), "NUMERIC_FIELD_INVALID", f"Non-finite numeric value for {field}.")
    text = format(number, ".10f").rstrip("0").rstrip(".")
    return text if text not in {"", "-0"} else "0"


def _timestamp_text(value: str, field: str) -> str:
    text = str(value).strip().replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError as exc:
        raise OfficialEvidenceAppendError(
            "TIMESTAMP_INVALID",
            f"Invalid timestamp for {field}.",
        ) from exc
    _require(parsed.tzinfo is not None, "TIMESTAMP_TIMEZONE_REQUIRED", f"Timezone required for {field}.")
    return parsed.astimezone(timezone.utc).isoformat()


def _safe_identifier(value: str, field: str) -> str:
    text = str(value).strip()
    _require(text != "", "REQUIRED_FIELD_MISSING", f"Missing required field: {field}.")
    _require("\x00" not in text and "\r" not in text and "\n" not in text, "TEXT_FIELD_INVALID", f"Unsafe text in {field}.")
    return text


def _dataset_csv_bytes(rows: Sequence[Mapping[str, str]]) -> bytes:
    output = io.StringIO(newline="")
    writer = csv.DictWriter(
        output,
        fieldnames=list(CANONICAL_COLUMNS),
        lineterminator="\n",
        extrasaction="raise",
    )
    writer.writeheader()
    for row in rows:
        writer.writerow({column: row[column] for column in CANONICAL_COLUMNS})
    return output.getvalue().encode("utf-8")


def _manifest_v2_bytes(row: Mapping[str, Any]) -> bytes:
    output = io.StringIO(newline="")
    writer = csv.DictWriter(
        output,
        fieldnames=list(MANIFEST_V2_FIELDS),
        lineterminator="\n",
        extrasaction="raise",
    )
    writer.writeheader()
    writer.writerow({field: row[field] for field in MANIFEST_V2_FIELDS})
    return output.getvalue().encode("utf-8")


def _parse_single_manifest_record(payload: bytes) -> dict[str, str]:
    _require(not payload.startswith(b"\xef\xbb\xbf"), "MANIFEST_ENCODING_INVALID", "Manifest contains a UTF-8 BOM.")
    _require(b"\r" not in payload, "MANIFEST_LINE_ENDING_INVALID", "Manifest must be LF-only.")
    try:
        text = payload.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise OfficialEvidenceAppendError("MANIFEST_ENCODING_INVALID", "Manifest is not valid UTF-8.") from exc
    rows = list(csv.DictReader(io.StringIO(text, newline="")))
    _require(len(rows) == 1, "MANIFEST_RECORD_COUNT_INVALID", "Manifest must contain exactly one record.")
    return {str(key): str(value) for key, value in rows[0].items()}


def calculate_deduplication_key(values: Mapping[str, str]) -> str:
    fields = (
        "observation_id",
        "observed_at_utc",
        "candidate_id",
        "symbol",
        "timeframe",
        "observation_state",
        "lifecycle_state",
    )
    payload = {field: str(values[field]) for field in fields}
    return _sha256_bytes(_canonical_json_bytes(payload))


def calculate_evidence_hash(row: Mapping[str, str]) -> str:
    payload = {
        column: str(row[column])
        for column in CANONICAL_COLUMNS
        if column != "evidence_hash"
    }
    return _sha256_bytes(_canonical_json_bytes(payload))


def validate_dataset_bytes(payload: bytes) -> dict[str, Any]:
    _require(not payload.startswith(b"\xef\xbb\xbf"), "DATASET_ENCODING_INVALID", "Dataset contains a UTF-8 BOM.")
    _require(b"\r" not in payload, "DATASET_LINE_ENDING_INVALID", "Dataset must be LF-only.")
    _require(payload.endswith(b"\n") and not payload.endswith(b"\n\n"), "DATASET_FINAL_LF_INVALID", "Dataset must end with exactly one LF.")
    try:
        text = payload.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise OfficialEvidenceAppendError("DATASET_ENCODING_INVALID", "Dataset is not valid UTF-8.") from exc
    reader = csv.DictReader(io.StringIO(text, newline=""))
    _require(tuple(reader.fieldnames or ()) == CANONICAL_COLUMNS, "DATASET_SCHEMA_INVALID", "Dataset columns do not match the canonical 54-column contract.")
    rows = [{str(key): str(value) for key, value in row.items()} for row in reader]
    previous_hash = GENESIS_EVIDENCE_HASH
    deduplication_keys: set[str] = set()
    for index, row in enumerate(rows, start=1):
        _require(set(row) == set(CANONICAL_COLUMNS), "DATASET_ROW_SCHEMA_INVALID", f"Row {index} does not match canonical columns.")
        _require(row["direction"] == "LONG", "ROW_DIRECTION_INVALID", f"Row {index} is not LONG.")
        _require(row["candidate_id"] in ALLOWED_CANDIDATE_IDS, "ROW_CANDIDATE_INVALID", f"Row {index} candidate is not authorized for research evidence.")
        _require(row["evidence_status"] == "OFFICIAL_PROSPECTIVE_EVIDENCE_ACCEPTED", "ROW_EVIDENCE_STATUS_INVALID", f"Row {index} evidence status is invalid.")
        _require(row["evidence_scope"] == "OFFICIAL_PROSPECTIVE_RESEARCH_EVIDENCE", "ROW_EVIDENCE_SCOPE_INVALID", f"Row {index} evidence scope is invalid.")
        _require(row["review_status"] == "HUMAN_REVIEW_APPROVED_FOR_OFFICIAL_EVIDENCE", "ROW_REVIEW_STATUS_INVALID", f"Row {index} review status is invalid.")
        _require(row["previous_evidence_hash"] == previous_hash, "EVIDENCE_HASH_CHAIN_INVALID", f"Row {index} previous evidence hash is invalid.")
        _require(_is_sha256(row["source_artifact_sha256"]), "ROW_PROVENANCE_HASH_INVALID", f"Row {index} source artifact hash is invalid.")
        _require(_is_sha256(row["source_row_hash"]), "ROW_PROVENANCE_HASH_INVALID", f"Row {index} source row hash is invalid.")
        _require(_is_sha256(row["deduplication_key"]), "ROW_DEDUPLICATION_KEY_INVALID", f"Row {index} deduplication key is invalid.")
        _require(row["deduplication_key"] not in deduplication_keys, "DUPLICATE_EVIDENCE_EVENT", f"Row {index} repeats a deduplication key.")
        deduplication_keys.add(row["deduplication_key"])
        expected_deduplication_key = calculate_deduplication_key(row)
        _require(row["deduplication_key"] == expected_deduplication_key, "ROW_DEDUPLICATION_KEY_INVALID", f"Row {index} deduplication key does not match identity fields.")
        for field in APPEND_TRUE_COLUMNS:
            _require(_parse_bool_text(row[field], field) is True, "ROW_REQUIRED_TRUE_FLAG_INVALID", f"Row {index} requires {field}=True.")
        for field in EXECUTION_FALSE_COLUMNS:
            _require(_parse_bool_text(row[field], field) is False, "ROW_EXECUTION_PERMISSION_INVALID", f"Row {index} enables prohibited permission {field}.")
        entry = float(row["entry_price"])
        stop = float(row["stop_price"])
        target = float(row["target_price"])
        invalidation = float(row["invalidation_level"])
        risk_reward = float(row["risk_reward"])
        _require(all(math.isfinite(value) for value in (entry, stop, target, invalidation, risk_reward)), "ROW_NUMERIC_FIELD_INVALID", f"Row {index} contains a non-finite numeric value.")
        _require(stop < entry < target, "ROW_RISK_STRUCTURE_INVALID", f"Row {index} LONG price structure is invalid.")
        _require(invalidation <= entry and invalidation > 0, "ROW_INVALIDATION_LEVEL_INVALID", f"Row {index} invalidation level is invalid.")
        expected_rr = (target - entry) / (entry - stop)
        _require(abs(expected_rr - EXPECTED_RISK_REWARD) <= 1e-9 and abs(risk_reward - EXPECTED_RISK_REWARD) <= 1e-9, "ROW_RISK_REWARD_INVALID", f"Row {index} risk-reward must equal 2.5.")
        expected_hash = calculate_evidence_hash(row)
        _require(row["evidence_hash"] == expected_hash, "EVIDENCE_HASH_INVALID", f"Row {index} evidence hash mismatch.")
        previous_hash = row["evidence_hash"]
    return {
        "sha256": _sha256_bytes(payload),
        "size_bytes": len(payload),
        "column_count": len(CANONICAL_COLUMNS),
        "evidence_row_count": len(rows),
        "rows": rows,
        "last_evidence_hash": previous_hash,
    }


def validate_pair_bytes(
    dataset_bytes: bytes,
    manifest_bytes: bytes,
    *,
    target_path: Path,
    require_canonical_path: bool,
) -> dict[str, Any]:
    dataset = validate_dataset_bytes(dataset_bytes)
    manifest = _parse_single_manifest_record(manifest_bytes)
    schema = manifest.get("manifest_schema_version", "")
    target_sha256 = dataset["sha256"]
    target_size_bytes = dataset["size_bytes"]
    row_count = dataset["evidence_row_count"]
    _require(manifest.get("target_filename") == target_path.name, "MANIFEST_BINDING_MISMATCH", "Manifest target filename mismatch.")
    _require(manifest.get("target_sha256") == target_sha256, "MANIFEST_BINDING_MISMATCH", "Manifest target SHA-256 mismatch.")
    _require(_parse_int(manifest.get("target_size_bytes", ""), "target_size_bytes") == target_size_bytes, "MANIFEST_BINDING_MISMATCH", "Manifest target size mismatch.")
    _require(_parse_int(manifest.get("target_column_count", ""), "target_column_count") == EXPECTED_COLUMN_COUNT, "MANIFEST_BINDING_MISMATCH", "Manifest column count mismatch.")
    _require(_parse_int(manifest.get("target_evidence_row_count", ""), "target_evidence_row_count") == row_count, "MANIFEST_BINDING_MISMATCH", "Manifest evidence row count mismatch.")
    if require_canonical_path:
        _require(Path(manifest.get("target_canonical_path", "")) == target_path.resolve(), "MANIFEST_BINDING_MISMATCH", "Manifest target canonical path mismatch.")
    if schema == MANIFEST_SCHEMA_V1:
        _require(manifest.get("phase") == "10.45", "MANIFEST_PHASE_INVALID", "Legacy manifest phase mismatch.")
        _require(row_count == 0, "LEGACY_MANIFEST_NON_EMPTY_INVALID", "Manifest V1 may bind only the initialized empty dataset.")
        _require(manifest.get("candidate_sha256") == target_sha256, "MANIFEST_BINDING_MISMATCH", "Legacy candidate SHA mismatch.")
        _require(_parse_int(manifest.get("candidate_size_bytes", ""), "candidate_size_bytes") == target_size_bytes, "MANIFEST_BINDING_MISMATCH", "Legacy candidate size mismatch.")
        _require(_parse_int(manifest.get("official_evidence_rows_written", ""), "official_evidence_rows_written") == 0, "MANIFEST_PERMISSION_INVALID", "Legacy manifest must contain zero evidence rows.")
        for field in ("create_only", "official_dataset_path_used", "human_review_required"):
            _require(_parse_bool_text(manifest.get(field, ""), field) is True, "MANIFEST_PERMISSION_INVALID", f"Legacy manifest requires {field}=True.")
        for field in (
            "existing_target_replacement_allowed",
            "automatic_recovery_allowed",
            *EXECUTION_FALSE_COLUMNS,
        ):
            _require(_parse_bool_text(manifest.get(field, ""), field) is False, "MANIFEST_PERMISSION_INVALID", f"Legacy manifest enables prohibited field {field}.")
        return {
            **dataset,
            "manifest_schema_version": schema,
            "manifest_sha256": _sha256_bytes(manifest_bytes),
            "state": "INITIALIZED_EMPTY_READY_FOR_CONTROLLED_EVIDENCE",
            "phase": "10.45",
            "create_only": True,
            "append_only": False,
            "human_review_required": True,
        }
    _require(schema == MANIFEST_SCHEMA_V2, "MANIFEST_SCHEMA_INVALID", "Unsupported official dataset manifest schema.")
    _require(manifest.get("capability") == CAPABILITY, "MANIFEST_CAPABILITY_INVALID", "Append manifest capability mismatch.")
    _require(row_count >= 1, "APPEND_MANIFEST_EMPTY_INVALID", "Append manifest requires at least one evidence row.")
    _require(_parse_int(manifest.get("official_evidence_rows_written", ""), "official_evidence_rows_written") == row_count, "MANIFEST_BINDING_MISMATCH", "Append manifest total row count mismatch.")
    _require(_parse_int(manifest.get("previous_evidence_row_count", ""), "previous_evidence_row_count") == row_count - 1, "MANIFEST_BINDING_MISMATCH", "Append manifest previous row count mismatch.")
    _require(_parse_int(manifest.get("appended_rows_this_operation", ""), "appended_rows_this_operation") == 1, "MANIFEST_BINDING_MISMATCH", "Append operation must add exactly one row.")
    _require(_is_sha256(manifest.get("previous_manifest_sha256", "")), "MANIFEST_PREVIOUS_HASH_INVALID", "Append manifest previous manifest hash is invalid.")
    _require(_is_sha256(manifest.get("previous_dataset_sha256", "")), "MANIFEST_PREVIOUS_HASH_INVALID", "Append manifest previous dataset hash is invalid.")
    last_row = dataset["rows"][-1]
    _require(manifest.get("appended_evidence_id") == last_row["evidence_id"], "MANIFEST_BINDING_MISMATCH", "Append manifest evidence ID mismatch.")
    _require(manifest.get("appended_evidence_hash") == last_row["evidence_hash"], "MANIFEST_BINDING_MISMATCH", "Append manifest evidence hash mismatch.")
    _require(manifest.get("appended_deduplication_key") == last_row["deduplication_key"], "MANIFEST_BINDING_MISMATCH", "Append manifest deduplication key mismatch.")
    _require(_parse_bool_text(manifest.get("append_only", ""), "append_only") is True, "MANIFEST_PERMISSION_INVALID", "Append manifest must be append-only.")
    _require(manifest.get("replacement_scope") == "VALIDATED_APPEND_TRANSACTION_ONLY", "MANIFEST_PERMISSION_INVALID", "Append replacement scope is invalid.")
    for field in (
        "existing_target_replacement_allowed",
        "official_dataset_path_used",
        "human_review_required",
        "manual_confirmation_required",
        "manual_confirmed",
    ):
        _require(_parse_bool_text(manifest.get(field, ""), field) is True, "MANIFEST_PERMISSION_INVALID", f"Append manifest requires {field}=True.")
    for field in ("automatic_recovery_allowed", *EXECUTION_FALSE_COLUMNS):
        _require(_parse_bool_text(manifest.get(field, ""), field) is False, "MANIFEST_PERMISSION_INVALID", f"Append manifest enables prohibited field {field}.")
    return {
        **dataset,
        "manifest_schema_version": schema,
        "manifest_sha256": _sha256_bytes(manifest_bytes),
        "state": "PROSPECTIVE_EVIDENCE_COLLECTION_ACTIVE_READ_ONLY",
        "phase": CAPABILITY,
        "create_only": False,
        "append_only": True,
        "human_review_required": True,
    }


def validate_existing_pair(
    dataset_path: Path,
    manifest_path: Path,
    *,
    require_canonical_path: bool = True,
    block_on_lock: bool = True,
) -> dict[str, Any]:
    dataset = dataset_path.resolve()
    manifest = manifest_path.resolve()
    _require(dataset.parent == manifest.parent, "PAIR_PATH_BOUNDARY_INVALID", "Dataset and manifest must share one directory.")
    lock_path = dataset.parent / OFFICIAL_LOCK_RELATIVE_PATH.name
    if block_on_lock:
        _require(not lock_path.exists() and not lock_path.is_symlink(), "OFFICIAL_DATASET_LOCK_ACTIVE", "Official dataset lock is active; read fails closed.")
    _require(dataset.is_file() and not dataset.is_symlink(), "DATASET_PATH_INVALID", "Dataset must be a regular file.")
    _require(manifest.is_file() and not manifest.is_symlink(), "MANIFEST_PATH_INVALID", "Manifest must be a regular file.")
    return validate_pair_bytes(
        dataset.read_bytes(),
        manifest.read_bytes(),
        target_path=dataset,
        require_canonical_path=require_canonical_path,
    )


def build_reviewed_evidence_row(
    reviewed: ReviewedLongEvidenceInput,
    *,
    existing_rows: Sequence[Mapping[str, str]],
    previous_manifest_sha256: str,
    collected_at_utc: str,
) -> dict[str, str]:
    candidate_id = _safe_identifier(reviewed.candidate_id, "candidate_id")
    _require(candidate_id in ALLOWED_CANDIDATE_IDS, "CANDIDATE_NOT_AUTHORIZED", "Candidate is not in the frozen LONG research watchlist.")
    _require(_safe_identifier(reviewed.direction, "direction").upper() == "LONG", "DIRECTION_NOT_LONG", "Only LONG evidence is accepted.")
    observation_state = _safe_identifier(reviewed.observation_state, "observation_state").upper()
    lifecycle_state = _safe_identifier(reviewed.lifecycle_state, "lifecycle_state").upper()
    _require(observation_state in ALLOWED_OBSERVATION_STATES, "OBSERVATION_STATE_INVALID", "Unsupported observation state.")
    _require(lifecycle_state in ALLOWED_LIFECYCLE_STATES, "LIFECYCLE_STATE_INVALID", "Unsupported lifecycle state.")
    if observation_state == "OBSERVED_OPEN":
        _require(lifecycle_state == "OPEN", "LIFECYCLE_STATE_INVALID", "OBSERVED_OPEN requires OPEN lifecycle.")
    else:
        _require(lifecycle_state in {"CLOSED", "INVALIDATED"}, "LIFECYCLE_STATE_INVALID", "Resolved or invalidated evidence cannot remain OPEN.")
    _require(reviewed.review_status == "HUMAN_REVIEW_APPROVED_FOR_OFFICIAL_EVIDENCE", "HUMAN_REVIEW_STATUS_INVALID", "Human review approval is required.")
    for field_name in (
        "manual_confirmation_required",
        "manual_confirmed",
        "write_ahead_validation_passed",
        "schema_validation_passed",
        "provenance_validation_passed",
        "risk_structure_validation_passed",
    ):
        _require(bool(getattr(reviewed, field_name)) is True, "HUMAN_OR_VALIDATION_GATE_FAILED", f"Required gate failed: {field_name}.")
    entry = float(_number_text(reviewed.entry_price, "entry_price"))
    stop = float(_number_text(reviewed.stop_price, "stop_price"))
    target = float(_number_text(reviewed.target_price, "target_price"))
    invalidation = float(_number_text(reviewed.invalidation_level, "invalidation_level"))
    risk_reward = float(_number_text(reviewed.risk_reward, "risk_reward"))
    _require(stop < entry < target, "RISK_STRUCTURE_INVALID", "LONG structure requires stop < entry < target.")
    _require(invalidation <= entry and invalidation > 0, "INVALIDATION_LEVEL_INVALID", "Invalidation level must be positive and no higher than entry.")
    computed_rr = (target - entry) / (entry - stop)
    _require(abs(computed_rr - EXPECTED_RISK_REWARD) <= 1e-9 and abs(risk_reward - EXPECTED_RISK_REWARD) <= 1e-9, "RISK_REWARD_INVALID", "Risk-reward must equal the frozen 2.5 contract.")
    source_artifact_sha256 = str(reviewed.source_artifact_sha256).strip().lower()
    source_row_hash = str(reviewed.source_row_hash).strip().lower()
    _require(_is_sha256(source_artifact_sha256), "PROVENANCE_HASH_INVALID", "Source artifact SHA-256 is invalid.")
    _require(_is_sha256(source_row_hash), "PROVENANCE_HASH_INVALID", "Source row hash is invalid.")
    previous_evidence_hash = (
        str(existing_rows[-1]["evidence_hash"])
        if existing_rows
        else GENESIS_EVIDENCE_HASH
    )
    base = {
        "observation_id": _safe_identifier(reviewed.observation_id, "observation_id"),
        "observed_at_utc": _timestamp_text(reviewed.observed_at_utc, "observed_at_utc"),
        "candidate_id": candidate_id,
        "symbol": _safe_identifier(reviewed.symbol, "symbol").upper(),
        "timeframe": _safe_identifier(reviewed.timeframe, "timeframe"),
        "observation_state": observation_state,
        "lifecycle_state": lifecycle_state,
    }
    deduplication_key = calculate_deduplication_key(base)
    existing_keys = {str(row.get("deduplication_key", "")) for row in existing_rows}
    _require(deduplication_key not in existing_keys, "DUPLICATE_EVIDENCE_EVENT", "The same prospective evidence event already exists.")
    evidence_id = "LONG-EVID-" + _sha256_bytes((deduplication_key + previous_evidence_hash).encode("ascii"))[:24]
    row = {
        "evidence_id": evidence_id,
        "observation_id": base["observation_id"],
        "collected_at_utc": _timestamp_text(collected_at_utc, "collected_at_utc"),
        "observed_at_utc": base["observed_at_utc"],
        "source_system": _safe_identifier(reviewed.source_system, "source_system"),
        "source_artifact": _safe_identifier(reviewed.source_artifact, "source_artifact"),
        "source_artifact_sha256": source_artifact_sha256,
        "source_row_hash": source_row_hash,
        "candidate_id": base["candidate_id"],
        "direction": "LONG",
        "symbol": base["symbol"],
        "timeframe": base["timeframe"],
        "observation_state": base["observation_state"],
        "evidence_status": "OFFICIAL_PROSPECTIVE_EVIDENCE_ACCEPTED",
        "evidence_scope": "OFFICIAL_PROSPECTIVE_RESEARCH_EVIDENCE",
        "evidence_version": "1",
        "entry_price": _number_text(entry, "entry_price"),
        "stop_price": _number_text(stop, "stop_price"),
        "target_price": _number_text(target, "target_price"),
        "invalidation_level": _number_text(invalidation, "invalidation_level"),
        "risk_reward": _number_text(risk_reward, "risk_reward"),
        "cost_profile": _safe_identifier(reviewed.cost_profile, "cost_profile"),
        "market_context": _safe_identifier(reviewed.market_context, "market_context"),
        "activation_scope": _safe_identifier(reviewed.activation_scope, "activation_scope"),
        "signal_state": _safe_identifier(reviewed.signal_state, "signal_state"),
        "deduplication_key": deduplication_key,
        "deduplication_status": "UNIQUE_NEW_EVENT",
        "lifecycle_state": base["lifecycle_state"],
        "review_status": reviewed.review_status,
        "rejection_reason": "",
        "manual_confirmation_required": "True",
        "manual_confirmed": "True",
        "write_ahead_validation_passed": "True",
        "schema_validation_passed": "True",
        "provenance_validation_passed": "True",
        "risk_structure_validation_passed": "True",
        "evidence_hash": "",
        "previous_evidence_hash": previous_evidence_hash,
        "audit_event_id": _safe_identifier(reviewed.audit_event_id, "audit_event_id"),
        "created_by": _safe_identifier(reviewed.created_by, "created_by"),
        "reviewed_by": _safe_identifier(reviewed.reviewed_by, "reviewed_by"),
        "rollback_reference": previous_manifest_sha256,
        "accepted_as_real_evidence": "True",
        "official_dataset_write_allowed": "True",
        "evidence_persistence_allowed": "True",
        "signal_generation_enabled": "False",
        "live_alerts_allowed": "False",
        "paper_trade_execution_allowed": "False",
        "real_capital_allowed": "False",
        "market_execution_allowed": "False",
        "exchange_execution_allowed": "False",
        "automation_allowed": "False",
        "execution_allowed": "False",
        "notes": str(reviewed.notes).strip(),
    }
    row["evidence_hash"] = calculate_evidence_hash(row)
    validate_dataset_bytes(_dataset_csv_bytes([*existing_rows, row]))
    return row


def _build_paths(dataset_path: Path, manifest_path: Path, operation_id: str) -> AppendPaths:
    dataset = dataset_path.resolve()
    manifest = manifest_path.resolve()
    _require(dataset.parent == manifest.parent, "PAIR_PATH_BOUNDARY_INVALID", "Dataset and manifest must share one directory.")
    _require(dataset.name == OFFICIAL_DATASET_RELATIVE_PATH.name, "DATASET_FILENAME_INVALID", "Unexpected official dataset filename.")
    _require(manifest.name == OFFICIAL_MANIFEST_RELATIVE_PATH.name, "MANIFEST_FILENAME_INVALID", "Unexpected official manifest filename.")
    directory = dataset.parent
    return AppendPaths(
        dataset=dataset,
        manifest=manifest,
        lock=directory / OFFICIAL_LOCK_RELATIVE_PATH.name,
        dataset_temp=directory / f"{dataset.name}.{operation_id}.tmp",
        manifest_temp=directory / f"{manifest.name}.{operation_id}.tmp",
        dataset_backup=directory / f"{dataset.name}.{operation_id}.bak",
        manifest_backup=directory / f"{manifest.name}.{operation_id}.bak",
    )


def _lock_record(operation_id: str, started_at_utc: str, paths: AppendPaths) -> dict[str, Any]:
    return {
        "lock_schema_version": "LONG_OFFICIAL_DATASET_APPEND_LOCK_V1",
        "capability": CAPABILITY,
        "operation_id": operation_id,
        "pid": os.getpid(),
        "hostname": socket.gethostname(),
        "started_at_utc": started_at_utc,
        "target_canonical_path": str(paths.dataset),
        "manifest_canonical_path": str(paths.manifest),
        "append_only": True,
        "human_review_required": True,
    }


def _acquire_lock(path: Path, record: Mapping[str, Any]) -> None:
    try:
        atomic_create_only._durable_create_exclusive(path, _canonical_json_bytes(record))
    except FileExistsError as exc:
        raise OfficialEvidenceAppendError("LOCK_CONTENTION", f"Exclusive append lock already exists: {path}") from exc


def _release_owned_lock(path: Path, operation_id: str) -> None:
    _require(path.is_file() and not path.is_symlink(), "LOCK_INVALID", "Append lock is missing or invalid.")
    try:
        record = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise OfficialEvidenceAppendError("LOCK_INVALID", "Append lock JSON is invalid.") from exc
    _require(record.get("operation_id") == operation_id, "LOCK_OWNERSHIP_MISMATCH", "Only the lock owner may remove the append lock.")
    path.unlink()
    if os.name == "posix":
        atomic_create_only._fsync_directory(path.parent)


def _remove_owned_artifact(path: Path, operation_id: str) -> None:
    if not path.exists():
        return
    _require(path.is_file() and not path.is_symlink(), "TEMP_OWNERSHIP_MISMATCH", "Residual artifact is not a regular file.")
    _require(f".{operation_id}." in path.name, "TEMP_OWNERSHIP_MISMATCH", "Residual artifact is not owned by this operation.")
    path.unlink()


def _windows_replace_write_through(source: Path, target: Path) -> None:
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    move_file_ex = kernel32.MoveFileExW
    move_file_ex.argtypes = [ctypes.c_wchar_p, ctypes.c_wchar_p, ctypes.c_uint32]
    move_file_ex.restype = ctypes.c_int
    ctypes.set_last_error(0)
    flags = 0x00000001 | 0x00000008
    ok = move_file_ex(str(source), str(target), flags)
    if not ok:
        raise OfficialEvidenceAppendError(
            "ATOMIC_REPLACE_FAILED",
            f"MoveFileExW replacement failed with Windows error {ctypes.get_last_error()}.",
        )


def _replace_write_through(source: Path, target: Path) -> str:
    _require(source.parent == target.parent, "PATH_BOUNDARY_INVALID", "Replacement requires same-directory artifacts.")
    _require(source.is_file() and not source.is_symlink(), "TEMP_ARTIFACT_INVALID", "Replacement source is invalid.")
    if os.name == "nt":
        _windows_replace_write_through(source, target)
        primitive = "WINDOWS_MOVEFILEEX_REPLACE_EXISTING_WRITE_THROUGH"
    elif os.name == "posix":
        os.replace(source, target)
        atomic_create_only._fsync_directory(target.parent)
        primitive = "POSIX_RENAME_REPLACE_PLUS_DIRECTORY_FSYNC"
    else:
        raise OfficialEvidenceAppendError("UNSUPPORTED_PLATFORM_DURABILITY", f"Unsupported platform: {os.name}")
    _require(target.is_file() and not target.is_symlink(), "POST_REPLACE_TARGET_INVALID", "Replacement target is invalid.")
    return primitive


def _trigger_failpoint(requested: str | None, point: str, operation_id: str) -> None:
    if requested == point:
        raise InjectedAppendFailure(
            "INJECTED_FAILURE",
            f"Injected append failure at {point}.",
            operation_id=operation_id,
        )


def _build_manifest_v2(
    *,
    operation_id: str,
    created_at_utc: str,
    previous_dataset_bytes: bytes,
    previous_manifest_bytes: bytes,
    candidate_dataset_bytes: bytes,
    target_path: Path,
    appended_row: Mapping[str, str],
    publication_primitive: str,
) -> dict[str, Any]:
    candidate = validate_dataset_bytes(candidate_dataset_bytes)
    previous = validate_dataset_bytes(previous_dataset_bytes)
    return {
        "manifest_schema_version": MANIFEST_SCHEMA_V2,
        "capability": CAPABILITY,
        "operation_id": operation_id,
        "created_at_utc": created_at_utc,
        "previous_manifest_sha256": _sha256_bytes(previous_manifest_bytes),
        "previous_dataset_sha256": previous["sha256"],
        "previous_evidence_row_count": previous["evidence_row_count"],
        "target_filename": target_path.name,
        "target_canonical_path": str(target_path.resolve()),
        "target_sha256": candidate["sha256"],
        "target_size_bytes": candidate["size_bytes"],
        "target_column_count": candidate["column_count"],
        "target_evidence_row_count": candidate["evidence_row_count"],
        "appended_evidence_id": appended_row["evidence_id"],
        "appended_evidence_hash": appended_row["evidence_hash"],
        "appended_deduplication_key": appended_row["deduplication_key"],
        "appended_rows_this_operation": 1,
        "publication_primitive": publication_primitive,
        "append_only": True,
        "replacement_scope": "VALIDATED_APPEND_TRANSACTION_ONLY",
        "existing_target_replacement_allowed": True,
        "official_dataset_path_used": True,
        "official_evidence_rows_written": candidate["evidence_row_count"],
        "automatic_recovery_allowed": False,
        "signal_generation_enabled": False,
        "live_alerts_allowed": False,
        "paper_trade_execution_allowed": False,
        "real_capital_allowed": False,
        "market_execution_allowed": False,
        "exchange_execution_allowed": False,
        "automation_allowed": False,
        "execution_allowed": False,
        "human_review_required": True,
        "manual_confirmation_required": True,
        "manual_confirmed": True,
    }


def _append_pair(
    *,
    dataset_path: Path,
    manifest_path: Path,
    reviewed: ReviewedLongEvidenceInput,
    authorization: str | None,
    required_authorization: str,
    require_canonical_path_before: bool,
    fail_at: str | None,
    operation_id_factory: Callable[[], str] | None,
    clock: Callable[[], str] | None,
) -> dict[str, Any]:
    _require(authorization == required_authorization, "APPEND_AUTHORIZATION_REQUIRED", "Exact append authorization is required.")
    if fail_at is not None:
        _require(fail_at in FAILPOINTS, "UNKNOWN_FAILPOINT", f"Unknown failpoint: {fail_at}")
    operation_id = operation_id_factory() if operation_id_factory else uuid.uuid4().hex
    _require(len(operation_id) >= 16 and all(character.isalnum() or character in "-_" for character in operation_id), "OPERATION_ID_INVALID", "Unsafe operation ID.")
    started_at = clock() if clock else _utc_now()
    paths = _build_paths(dataset_path, manifest_path, operation_id)
    _require(not paths.lock.exists() and not paths.lock.is_symlink(), "LOCK_CONTENTION", "Append lock already exists.")
    for residual in (paths.dataset_temp, paths.manifest_temp, paths.dataset_backup, paths.manifest_backup):
        _require(not residual.exists() and not residual.is_symlink(), "RESIDUAL_ARTIFACT_PRESENT", f"Residual artifact blocks append: {residual}")
    initial = validate_existing_pair(
        paths.dataset,
        paths.manifest,
        require_canonical_path=require_canonical_path_before,
        block_on_lock=True,
    )
    previous_dataset_bytes = paths.dataset.read_bytes()
    previous_manifest_bytes = paths.manifest.read_bytes()
    previous_dataset_sha256 = _sha256_bytes(previous_dataset_bytes)
    previous_manifest_sha256 = _sha256_bytes(previous_manifest_bytes)
    lock_acquired = False
    dataset_replaced = False
    manifest_replaced = False
    rollback_performed = False
    try:
        _acquire_lock(paths.lock, _lock_record(operation_id, started_at, paths))
        lock_acquired = True
        _trigger_failpoint(fail_at, "AFTER_LOCK_ACQUIRED", operation_id)
        _require(_sha256_bytes(paths.dataset.read_bytes()) == previous_dataset_sha256, "CONCURRENT_DATASET_CHANGE", "Dataset changed before append staging.")
        _require(_sha256_bytes(paths.manifest.read_bytes()) == previous_manifest_sha256, "CONCURRENT_MANIFEST_CHANGE", "Manifest changed before append staging.")
        row = build_reviewed_evidence_row(
            reviewed,
            existing_rows=initial["rows"],
            previous_manifest_sha256=previous_manifest_sha256,
            collected_at_utc=started_at,
        )
        candidate_dataset_bytes = _dataset_csv_bytes([*initial["rows"], row])
        validate_dataset_bytes(candidate_dataset_bytes)
        provisional_primitive = (
            "WINDOWS_MOVEFILEEX_REPLACE_EXISTING_WRITE_THROUGH"
            if os.name == "nt"
            else "POSIX_RENAME_REPLACE_PLUS_DIRECTORY_FSYNC"
        )
        manifest_row = _build_manifest_v2(
            operation_id=operation_id,
            created_at_utc=started_at,
            previous_dataset_bytes=previous_dataset_bytes,
            previous_manifest_bytes=previous_manifest_bytes,
            candidate_dataset_bytes=candidate_dataset_bytes,
            target_path=paths.dataset,
            appended_row=row,
            publication_primitive=provisional_primitive,
        )
        candidate_manifest_bytes = _manifest_v2_bytes(manifest_row)
        validate_pair_bytes(
            candidate_dataset_bytes,
            candidate_manifest_bytes,
            target_path=paths.dataset,
            require_canonical_path=True,
        )
        atomic_create_only._durable_create_exclusive(paths.dataset_temp, candidate_dataset_bytes)
        atomic_create_only._durable_create_exclusive(paths.manifest_temp, candidate_manifest_bytes)
        atomic_create_only._durable_create_exclusive(paths.dataset_backup, previous_dataset_bytes)
        atomic_create_only._durable_create_exclusive(paths.manifest_backup, previous_manifest_bytes)
        _trigger_failpoint(fail_at, "AFTER_TEMPS_DURABLE", operation_id)
        publication_primitive = _replace_write_through(paths.dataset_temp, paths.dataset)
        dataset_replaced = True
        _trigger_failpoint(fail_at, "AFTER_DATASET_REPLACED", operation_id)
        manifest_primitive = _replace_write_through(paths.manifest_temp, paths.manifest)
        manifest_replaced = True
        _require(publication_primitive == manifest_primitive, "PUBLICATION_PRIMITIVE_MISMATCH", "Dataset and manifest used different replacement primitives.")
        _trigger_failpoint(fail_at, "AFTER_MANIFEST_REPLACED", operation_id)
        final = validate_pair_bytes(
            paths.dataset.read_bytes(),
            paths.manifest.read_bytes(),
            target_path=paths.dataset,
            require_canonical_path=True,
        )
        _require(final["evidence_row_count"] == initial["evidence_row_count"] + 1, "APPEND_ROW_COUNT_INVALID", "Append must add exactly one evidence row.")
        _remove_owned_artifact(paths.dataset_backup, operation_id)
        _remove_owned_artifact(paths.manifest_backup, operation_id)
        _release_owned_lock(paths.lock, operation_id)
        lock_acquired = False
        return {
            "capability": CAPABILITY,
            "implementation_schema_version": IMPLEMENTATION_SCHEMA_VERSION,
            "operation_id": operation_id,
            "publication_primitive": publication_primitive,
            "previous_dataset_sha256": previous_dataset_sha256,
            "previous_manifest_sha256": previous_manifest_sha256,
            "target_sha256": final["sha256"],
            "manifest_sha256": final["manifest_sha256"],
            "previous_evidence_row_count": initial["evidence_row_count"],
            "target_evidence_row_count": final["evidence_row_count"],
            "appended_evidence_id": row["evidence_id"],
            "appended_evidence_hash": row["evidence_hash"],
            "appended_deduplication_key": row["deduplication_key"],
            "human_review_required": True,
            "manual_confirmed": True,
            "accepted_as_real_evidence": True,
            "official_dataset_write_performed": True,
            "paper_trade_execution_allowed": False,
            "real_capital_allowed": False,
            "market_execution_allowed": False,
            "exchange_execution_allowed": False,
            "automation_allowed": False,
            "execution_allowed": False,
            "rollback_performed": False,
            "final_state": final["state"],
        }
    except Exception as exc:
        try:
            if dataset_replaced and paths.dataset_backup.exists():
                _replace_write_through(paths.dataset_backup, paths.dataset)
                rollback_performed = True
            if manifest_replaced and paths.manifest_backup.exists():
                _replace_write_through(paths.manifest_backup, paths.manifest)
                rollback_performed = True
            for residual in (
                paths.dataset_temp,
                paths.manifest_temp,
                paths.dataset_backup,
                paths.manifest_backup,
            ):
                if residual.exists():
                    _remove_owned_artifact(residual, operation_id)
            if lock_acquired and paths.lock.exists():
                _release_owned_lock(paths.lock, operation_id)
                lock_acquired = False
            _require(_sha256_bytes(paths.dataset.read_bytes()) == previous_dataset_sha256, "ROLLBACK_DATASET_MISMATCH", "Dataset rollback did not restore the original bytes.")
            _require(_sha256_bytes(paths.manifest.read_bytes()) == previous_manifest_sha256, "ROLLBACK_MANIFEST_MISMATCH", "Manifest rollback did not restore the original bytes.")
        except Exception as rollback_exc:
            raise OfficialEvidenceAppendError(
                "ROLLBACK_FAILED_REVIEW_REQUIRED",
                f"Append failed and rollback could not be certified: {type(rollback_exc).__name__}: {rollback_exc}",
                operation_id=operation_id,
                rollback_performed=rollback_performed,
            ) from exc
        if isinstance(exc, OfficialEvidenceAppendError):
            exc.operation_id = exc.operation_id or operation_id
            exc.rollback_performed = rollback_performed
            raise
        raise OfficialEvidenceAppendError(
            "APPEND_FAILED_CLOSED",
            f"Append failed closed: {type(exc).__name__}: {exc}",
            operation_id=operation_id,
            rollback_performed=rollback_performed,
        ) from exc


def append_sandbox_pair(
    *,
    source_repo_root: Path | str,
    sandbox_root: Path | str,
    reviewed: ReviewedLongEvidenceInput,
    authorization: str | None = None,
    fail_at: str | None = None,
    operation_id_factory: Callable[[], str] | None = None,
    clock: Callable[[], str] | None = None,
) -> dict[str, Any]:
    source_root = Path(source_repo_root).resolve()
    sandbox = Path(sandbox_root).resolve()
    _require(sandbox.is_dir() and not sandbox.is_symlink(), "SANDBOX_INVALID", "Sandbox must be an existing regular directory.")
    try:
        inside_source = sandbox.is_relative_to(source_root)
    except ValueError:
        inside_source = False
    _require(not inside_source, "SANDBOX_INSIDE_REPOSITORY_PROHIBITED", "Sandbox must be outside the source repository.")
    dataset = sandbox / OFFICIAL_DATASET_RELATIVE_PATH
    manifest = sandbox / OFFICIAL_MANIFEST_RELATIVE_PATH
    _require(dataset.is_file() and manifest.is_file(), "SANDBOX_PAIR_MISSING", "Sandbox must contain a copied official dataset and manifest pair.")
    return _append_pair(
        dataset_path=dataset,
        manifest_path=manifest,
        reviewed=reviewed,
        authorization=authorization,
        required_authorization=SANDBOX_APPEND_AUTHORIZATION,
        require_canonical_path_before=False,
        fail_at=fail_at,
        operation_id_factory=operation_id_factory,
        clock=clock,
    )


def append_official_prospective_evidence(
    *,
    repo_root: Path | str,
    reviewed: ReviewedLongEvidenceInput,
    authorization: str | None = None,
    fail_at: str | None = None,
    operation_id_factory: Callable[[], str] | None = None,
    clock: Callable[[], str] | None = None,
) -> dict[str, Any]:
    _require(authorization == OFFICIAL_APPEND_AUTHORIZATION, "OFFICIAL_APPEND_AUTHORIZATION_REQUIRED", "Exact official append authorization is required.")
    _require(os.environ.get(OFFICIAL_APPEND_ENVIRONMENT_VARIABLE) == "1", "OFFICIAL_APPEND_ENVIRONMENT_GATE_REQUIRED", "Official append environment gate is disabled.")
    root = Path(repo_root).resolve()
    return _append_pair(
        dataset_path=root / OFFICIAL_DATASET_RELATIVE_PATH,
        manifest_path=root / OFFICIAL_MANIFEST_RELATIVE_PATH,
        reviewed=reviewed,
        authorization=authorization,
        required_authorization=OFFICIAL_APPEND_AUTHORIZATION,
        require_canonical_path_before=True,
        fail_at=fail_at,
        operation_id_factory=operation_id_factory,
        clock=clock,
    )


__all__ = [
    "ALLOWED_CANDIDATE_IDS",
    "CAPABILITY",
    "CANONICAL_COLUMNS",
    "EXPECTED_COLUMN_COUNT",
    "FAILPOINTS",
    "GENESIS_EVIDENCE_HASH",
    "IMPLEMENTATION_SCHEMA_VERSION",
    "InjectedAppendFailure",
    "MANIFEST_SCHEMA_V1",
    "MANIFEST_SCHEMA_V2",
    "OFFICIAL_APPEND_AUTHORIZATION",
    "OFFICIAL_APPEND_ENVIRONMENT_VARIABLE",
    "OFFICIAL_DATASET_RELATIVE_PATH",
    "OFFICIAL_LOCK_RELATIVE_PATH",
    "OFFICIAL_MANIFEST_RELATIVE_PATH",
    "OfficialEvidenceAppendError",
    "ReviewedLongEvidenceInput",
    "SANDBOX_APPEND_AUTHORIZATION",
    "append_official_prospective_evidence",
    "append_sandbox_pair",
    "build_reviewed_evidence_row",
    "calculate_deduplication_key",
    "calculate_evidence_hash",
    "validate_dataset_bytes",
    "validate_existing_pair",
    "validate_pair_bytes",
]
