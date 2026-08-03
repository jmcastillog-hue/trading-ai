from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from src.integration.openclaw_read_only_research_status_local_consumer_adapter_v1 import (
    consume_request,
)
from src.long_side.long_official_prospective_evidence_append_v1 import (
    OFFICIAL_DATASET_RELATIVE_PATH,
    OFFICIAL_MANIFEST_RELATIVE_PATH,
    validate_existing_pair,
)


CONNECTION_SCHEMA_VERSION = "OPENCLAW_READ_ONLY_LOCAL_CONNECTION_V1"
CONNECTION_MODE = "LOCAL_READ_ONLY_STATUS_COMMAND_HUMAN_EXPLANATION_ONLY"

OFFICIAL_DATASET_PATH = OFFICIAL_DATASET_RELATIVE_PATH
OFFICIAL_MANIFEST_PATH = OFFICIAL_MANIFEST_RELATIVE_PATH

FIXED_REQUEST: dict[str, Any] = {
    "operation": "GET_VALIDATED_RESEARCH_STATUS",
    "response_profile": "HUMAN_EXPLANATION_ONLY",
    "require_human_review": True,
    "allow_actionable_fields": False,
}


class LocalConnectionError(RuntimeError):
    pass


def validate_official_dataset(
    root: Path | str = Path("."),
) -> dict[str, Any]:
    root_path = Path(root).resolve()
    dataset_path = root_path / OFFICIAL_DATASET_PATH
    manifest_path = root_path / OFFICIAL_MANIFEST_PATH

    try:
        validated = validate_existing_pair(
            dataset_path,
            manifest_path,
            require_canonical_path=True,
            block_on_lock=True,
        )
    except Exception as exc:
        raise LocalConnectionError(str(exc)) from exc

    return {
        "phase": validated["phase"],
        "state": validated["state"],
        "dataset_path": OFFICIAL_DATASET_PATH.as_posix(),
        "manifest_path": OFFICIAL_MANIFEST_PATH.as_posix(),
        "dataset_sha256": validated["sha256"],
        "manifest_sha256": validated["manifest_sha256"],
        "dataset_size_bytes": validated["size_bytes"],
        "column_count": validated["column_count"],
        "evidence_row_count": validated["evidence_row_count"],
        "manifest_schema_version": validated["manifest_schema_version"],
        "create_only": validated["create_only"],
        "append_only": validated["append_only"],
        "human_review_required": validated["human_review_required"],
    }


def validate_official_empty_dataset(
    root: Path | str = Path("."),
) -> dict[str, Any]:
    """Backward-compatible name; validates either the initialized or appended pair."""
    return validate_official_dataset(root)


def build_connection_status(
    root: Path | str = Path("."),
) -> dict[str, Any]:
    root_path = Path(root).resolve()

    historical = consume_request(
        FIXED_REQUEST,
        root=root_path,
        require_git=False,
    )
    official = validate_official_dataset(root_path)

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
    "validate_official_dataset",
    "validate_official_empty_dataset",
]
