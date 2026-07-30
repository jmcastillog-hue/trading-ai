from __future__ import annotations

import csv
import hashlib
import io
import json
import sys
from pathlib import Path
from typing import Any, Mapping

from src.integration.openclaw_read_only_research_status_local_consumer_adapter_v1 import (
    consume_request,
)


CONNECTION_SCHEMA_VERSION = "OPENCLAW_READ_ONLY_LOCAL_CONNECTION_V1"
CONNECTION_MODE = "LOCAL_READ_ONLY_STATUS_COMMAND_HUMAN_EXPLANATION_ONLY"

OFFICIAL_DATASET_PATH = Path(
    "data/forward/long_forward_observation_dataset_v1.csv"
)
OFFICIAL_MANIFEST_PATH = Path(
    "data/forward/long_forward_observation_dataset_v1.manifest.csv"
)

FIXED_REQUEST: dict[str, Any] = {
    "operation": "GET_VALIDATED_RESEARCH_STATUS",
    "response_profile": "HUMAN_EXPLANATION_ONLY",
    "require_human_review": True,
    "allow_actionable_fields": False,
}


class LocalConnectionError(RuntimeError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise LocalConnectionError(message)


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _manifest_bool(row: Mapping[str, str], field: str) -> bool:
    value = row.get(field)
    _require(value in {"True", "False"}, f"Invalid boolean field: {field}")
    return value == "True"


def _manifest_int(row: Mapping[str, str], field: str) -> int:
    value = row.get(field)
    _require(value is not None, f"Missing integer field: {field}")
    try:
        return int(value)
    except ValueError as exc:
        raise LocalConnectionError(
            f"Invalid integer field: {field}"
        ) from exc


def validate_official_empty_dataset(
    root: Path | str = Path("."),
) -> dict[str, Any]:
    root_path = Path(root).resolve()
    dataset_path = root_path / OFFICIAL_DATASET_PATH
    manifest_path = root_path / OFFICIAL_MANIFEST_PATH

    _require(
        dataset_path.is_file() and not dataset_path.is_symlink(),
        "Official dataset is missing or is not a regular file",
    )
    _require(
        manifest_path.is_file() and not manifest_path.is_symlink(),
        "Official dataset manifest is missing or is not a regular file",
    )

    dataset_bytes = dataset_path.read_bytes()
    _require(
        not dataset_bytes.startswith(b"\xef\xbb\xbf"),
        "Official dataset contains a UTF-8 BOM",
    )
    _require(b"\r" not in dataset_bytes, "Official dataset is not LF-only")
    _require(
        dataset_bytes.endswith(b"\n")
        and not dataset_bytes.endswith(b"\n\n"),
        "Official dataset must contain one final LF",
    )

    try:
        dataset_text = dataset_bytes.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise LocalConnectionError(
            "Official dataset is not valid UTF-8"
        ) from exc

    parsed_dataset = list(
        csv.reader(io.StringIO(dataset_text, newline=""))
    )
    _require(
        len(parsed_dataset) == 1,
        "Official empty dataset must contain exactly one header row",
    )

    column_count = len(parsed_dataset[0])
    evidence_row_count = len(parsed_dataset) - 1
    dataset_sha256 = _sha256_bytes(dataset_bytes)
    dataset_size_bytes = len(dataset_bytes)

    manifest_text = manifest_path.read_text(
        encoding="utf-8",
        newline="",
    )
    reader = csv.DictReader(io.StringIO(manifest_text, newline=""))
    manifest_rows = list(reader)

    _require(
        len(manifest_rows) == 1,
        "Official dataset manifest must contain exactly one record",
    )
    row = manifest_rows[0]

    _require(row.get("phase") == "10.45", "Manifest phase mismatch")
    _require(
        row.get("manifest_schema_version")
        == "LONG_OFFICIAL_DATASET_MANIFEST_V1",
        "Manifest schema mismatch",
    )
    _require(
        row.get("target_filename")
        == OFFICIAL_DATASET_PATH.name,
        "Manifest target filename mismatch",
    )
    _require(
        row.get("target_sha256") == dataset_sha256,
        "Official dataset SHA-256 mismatch",
    )
    _require(
        row.get("candidate_sha256") == dataset_sha256,
        "Candidate SHA-256 mismatch",
    )
    _require(
        _manifest_int(row, "target_size_bytes") == dataset_size_bytes,
        "Official dataset size mismatch",
    )
    _require(
        _manifest_int(row, "candidate_size_bytes") == dataset_size_bytes,
        "Candidate size mismatch",
    )
    _require(
        _manifest_int(row, "target_column_count") == column_count,
        "Official dataset column-count mismatch",
    )
    _require(
        _manifest_int(row, "target_evidence_row_count")
        == evidence_row_count,
        "Official dataset row-count mismatch",
    )
    _require(
        _manifest_int(row, "official_evidence_rows_written")
        == evidence_row_count,
        "Manifest evidence-row count mismatch",
    )

    _require(column_count == 54, "Official dataset must have 54 columns")
    _require(
        evidence_row_count == 0,
        "Phase 11.1 requires the official dataset to remain empty",
    )

    required_true = (
        "create_only",
        "official_dataset_path_used",
        "human_review_required",
    )
    required_false = (
        "existing_target_replacement_allowed",
        "automatic_recovery_allowed",
        "execution_allowed",
        "exchange_execution_allowed",
        "market_execution_allowed",
        "paper_trade_execution_allowed",
        "real_capital_allowed",
        "signal_generation_enabled",
        "live_alerts_allowed",
        "automation_allowed",
    )

    for field in required_true:
        _require(
            _manifest_bool(row, field) is True,
            f"Required true manifest field is disabled: {field}",
        )

    for field in required_false:
        _require(
            _manifest_bool(row, field) is False,
            f"Prohibited manifest field is enabled: {field}",
        )

    return {
        "phase": "10.45",
        "state": "INITIALIZED_EMPTY_READY_FOR_CONTROLLED_EVIDENCE",
        "dataset_path": OFFICIAL_DATASET_PATH.as_posix(),
        "manifest_path": OFFICIAL_MANIFEST_PATH.as_posix(),
        "dataset_sha256": dataset_sha256,
        "dataset_size_bytes": dataset_size_bytes,
        "column_count": column_count,
        "evidence_row_count": evidence_row_count,
        "create_only": True,
        "human_review_required": True,
    }


def build_connection_status(
    root: Path | str = Path("."),
) -> dict[str, Any]:
    root_path = Path(root).resolve()

    historical = consume_request(
        FIXED_REQUEST,
        root=root_path,
        require_git=False,
    )
    official = validate_official_empty_dataset(root_path)

    research_status = dict(historical["research_status"])
    research_status["long_official_evidence_row_count"] = (
        official["evidence_row_count"]
    )
    research_status["long_official_dataset_state"] = official["state"]
    research_status["total_project_completed"] = False

    return {
        "connection_schema_version": CONNECTION_SCHEMA_VERSION,
        "connection_mode": CONNECTION_MODE,
        "decision": (
            "CURRENT_VALIDATED_RESEARCH_STATUS_CONNECTED_"
            "FOR_HUMAN_EXPLANATION_ONLY"
        ),
        "sources": {
            "historical_research_contract": historical["source"],
            "official_long_dataset": official,
        },
        "research_status": research_status,
        "restrictions": {
            "local_read_only_status_consumption_allowed": True,
            "status_command_invocation_allowed": True,
            "other_openclaw_tool_invocation_allowed": False,
            "human_explanation_only": True,
            "actionable_trading_fields_present": False,
            "official_dataset_write_allowed": False,
            "openclaw_operational_integration_allowed": False,
            "signal_generation_enabled": False,
            "paper_trade_execution_allowed": False,
            "real_capital_allowed": False,
            "market_execution_allowed": False,
            "automation_allowed": False,
        },
        "human_review": {
            "required": True,
            "permission_override_allowed": False,
            "unknown_status_inference_allowed": False,
        },
    }


def run_cli(root: Path | str = Path(".")) -> int:
    try:
        result = build_connection_status(root)
    except Exception as exc:
        failure = {
            "connection_schema_version": CONNECTION_SCHEMA_VERSION,
            "decision": "LOCAL_READ_ONLY_CONNECTION_FAILED_CLOSED",
            "error_type": type(exc).__name__,
            "error": str(exc),
            "all_operational_permissions_allowed": False,
        }
        print(
            json.dumps(
                failure,
                indent=2,
                sort_keys=True,
                ensure_ascii=True,
            ),
            file=sys.stderr,
        )
        return 1

    print(
        json.dumps(
            result,
            indent=2,
            sort_keys=True,
            ensure_ascii=True,
        )
    )
    return 0


__all__ = [
    "CONNECTION_MODE",
    "CONNECTION_SCHEMA_VERSION",
    "LocalConnectionError",
    "build_connection_status",
    "run_cli",
    "validate_official_empty_dataset",
]
