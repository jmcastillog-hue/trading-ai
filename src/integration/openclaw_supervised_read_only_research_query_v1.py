"""Supervised, closed-catalog, read-only research queries for Phase 11.6."""

from __future__ import annotations

import base64
import binascii
import copy
import hmac
import json
import re
from pathlib import Path
from typing import Any

from src.integration import openclaw_controlled_read_only_research_workflow_v1 as source_workflow

PHASE = "PHASE_11_6_OPENCLAW_SUPERVISED_READ_ONLY_RESEARCH_QUERY_V1"
QUERY_REQUEST_SCHEMA_VERSION = (
    "OPENCLAW_SUPERVISED_READ_ONLY_RESEARCH_QUERY_REQUEST_V1"
)
QUERY_RESPONSE_SCHEMA_VERSION = "OPENCLAW_SUPERVISED_READ_ONLY_RESEARCH_QUERY_V1"
QUERY_DECISION = (
    "PHASE_11_6_OPENCLAW_SUPERVISED_READ_ONLY_RESEARCH_QUERY_COMPLETED"
)
QUERY_ROUTE = "PYTHON_TEMPLATE"
SOURCE_WORKFLOW_REQUEST_ID = "phase-11-5-first-controlled-research-summary-v1"

PROJECT_COMPLETION_STATUS = "PROJECT_COMPLETION_STATUS"
LONG_RESEARCH_STATUS = "LONG_RESEARCH_STATUS"
SHORT_RESEARCH_STATUS = "SHORT_RESEARCH_STATUS"
EVIDENCE_DATASET_STATUS = "EVIDENCE_DATASET_STATUS"
RESEARCH_LOCK_STATUS = "RESEARCH_LOCK_STATUS"
OPERATIONAL_PERMISSION_STATUS = "OPERATIONAL_PERMISSION_STATUS"

ALLOWED_QUERY_IDS = frozenset(
    {
        PROJECT_COMPLETION_STATUS,
        LONG_RESEARCH_STATUS,
        SHORT_RESEARCH_STATUS,
        EVIDENCE_DATASET_STATUS,
        RESEARCH_LOCK_STATUS,
        OPERATIONAL_PERMISSION_STATUS,
    }
)

QUERY_RESTRICTIONS: dict[str, Any] = {
    "arbitrary_prompts_accepted": False,
    "automation": False,
    "browser_control": False,
    "capital_use": False,
    "external_access": False,
    "external_actions": False,
    "field_selection_accepted": False,
    "free_text_accepted": False,
    "human_review_required": True,
    "message_sending": False,
    "paper_trading": False,
    "real_trading": False,
    "source_mode": source_workflow.MODE_DETERMINISTIC,
}

_REQUEST_FIELDS = frozenset(
    {
        "query_request_schema_version",
        "request_id",
        "query_id",
        "human_review_required",
    }
)
_RESPONSE_FIELDS = frozenset(
    {
        "query_response_schema_version",
        "phase",
        "decision",
        "request_id",
        "query_id",
        "query_route",
        "local_model_called",
        "human_review_required",
        "query_result",
        "restrictions",
        "source_workflow_schema_version",
        "source_connection_schema_version",
        "source_operation",
    }
)
_SOURCE_RESPONSE_FIELDS = frozenset(
    {
        "decision",
        "explanation_decision",
        "explanation_mode",
        "explanation_output",
        "explanation_route",
        "human_review",
        "local_model_called",
        "operation",
        "phase",
        "request_id",
        "research_status",
        "restrictions",
        "source_connection_decision",
        "source_connection_schema_version",
        "workflow_schema_version",
    }
)
_RESEARCH_STATUS_FIELDS = frozenset(
    {
        "legacy_short_candidate",
        "long_official_dataset_state",
        "long_official_evidence_row_count",
        "long_primary_candidate",
        "long_secondary_candidate",
        "prospective_holdout",
        "retrospective_lockbox",
        "short_recovery_line",
        "short_recovery_surviving_variant_count",
        "total_project_completed",
    }
)
_RESULT_FIELDS = {
    PROJECT_COMPLETION_STATUS: frozenset({"total_project_completed"}),
    LONG_RESEARCH_STATUS: frozenset(
        {
            "long_primary_candidate",
            "long_secondary_candidate",
            "long_official_dataset_state",
        }
    ),
    SHORT_RESEARCH_STATUS: frozenset(
        {
            "legacy_short_candidate",
            "short_recovery_line",
            "short_recovery_surviving_variant_count",
        }
    ),
    EVIDENCE_DATASET_STATUS: frozenset(
        {
            "long_official_dataset_state",
            "long_official_evidence_row_count",
        }
    ),
    RESEARCH_LOCK_STATUS: frozenset(
        {
            "prospective_holdout",
            "retrospective_lockbox",
        }
    ),
    OPERATIONAL_PERMISSION_STATUS: frozenset(
        {
            "automation",
            "capital_use",
            "external_actions",
            "human_review_required",
            "read_only",
        }
    ),
}
_REQUEST_ID_PATTERN = re.compile(r"^[a-z0-9](?:[a-z0-9-]{0,126}[a-z0-9])?$")
_TOKEN_PATTERN = re.compile(r"^[A-Za-z0-9_-]+$")
_DANGEROUS_RESPONSE_FIELDS = frozenset(
    {
        "buy",
        "command",
        "destination",
        "entry",
        "exit",
        "market",
        "order",
        "order_parameters",
        "sell",
        "side",
        "stop_loss",
        "strategy",
        "symbol",
        "take_profit",
    }
)
_PERMISSION_KEY_TERMS = (
    "automation",
    "capital_use",
    "external_action",
    "operational_permission",
    "paper_trading",
    "real_trading",
    "tool_execution_allowed",
    "trading_allowed",
)


class QueryContractError(ValueError):
    """Raised when the Phase 11.6 closed contract is violated."""


def _canonical_json_bytes(value: dict[str, Any]) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")


def _reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise QueryContractError(f"Duplicate JSON key: {key}")
        result[key] = value
    return result


def _require_exact_fields(
    value: dict[str, Any],
    expected: frozenset[str],
    label: str,
) -> None:
    actual = frozenset(value)
    if actual != expected:
        missing = sorted(expected - actual)
        extra = sorted(actual - expected)
        raise QueryContractError(
            f"{label} fields changed; missing={missing}, extra={extra}"
        )


def _assert_no_enabled_operational_permission(
    value: Any,
    path: str = "$",
) -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            normalized = key.casefold()
            if child is True and any(term in normalized for term in _PERMISSION_KEY_TERMS):
                raise QueryContractError(
                    f"Enabled operational permission at {path}.{key}"
                )
            _assert_no_enabled_operational_permission(child, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _assert_no_enabled_operational_permission(child, f"{path}[{index}]")


def _assert_no_actionable_response_fields(
    value: Any,
    path: str = "$",
) -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            if key.casefold() in _DANGEROUS_RESPONSE_FIELDS:
                raise QueryContractError(
                    f"Actionable trading field is forbidden at {path}.{key}"
                )
            _assert_no_actionable_response_fields(child, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _assert_no_actionable_response_fields(child, f"{path}[{index}]")


def validate_query_request(request: Any) -> dict[str, Any]:
    """Validate and copy a closed-catalog Phase 11.6 request."""

    if type(request) is not dict:
        raise QueryContractError("Query request must be a plain JSON object")

    _require_exact_fields(request, _REQUEST_FIELDS, "query request")

    if request["query_request_schema_version"] != QUERY_REQUEST_SCHEMA_VERSION:
        raise QueryContractError("Unsupported query request schema version")

    request_id = request["request_id"]
    if type(request_id) is not str or not _REQUEST_ID_PATTERN.fullmatch(request_id):
        raise QueryContractError("Unsafe request_id")

    query_id = request["query_id"]
    if type(query_id) is not str or query_id not in ALLOWED_QUERY_IDS:
        raise QueryContractError("query_id is not in the closed catalog")

    if request["human_review_required"] is not True:
        raise QueryContractError("human_review_required must be true")

    return copy.deepcopy(request)


def encode_query_request_token(request: Any) -> str:
    """Encode a validated request as canonical unpadded Base64URL."""

    validated = validate_query_request(request)
    encoded = base64.urlsafe_b64encode(_canonical_json_bytes(validated))
    return encoded.decode("ascii").rstrip("=")


def decode_query_request_token(token: Any) -> dict[str, Any]:
    """Decode a canonical token and reject shell metacharacters or duplicate keys."""

    if type(token) is not str or not token or len(token) > 4096:
        raise QueryContractError("Query token must be a non-empty bounded string")
    if not _TOKEN_PATTERN.fullmatch(token):
        raise QueryContractError("Query token contains forbidden characters")

    padding = "=" * (-len(token) % 4)
    try:
        payload = base64.b64decode(
            token + padding,
            altchars=b"-_",
            validate=True,
        )
        decoded = payload.decode("utf-8")
        request = json.loads(
            decoded,
            object_pairs_hook=_reject_duplicate_keys,
        )
    except (binascii.Error, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise QueryContractError("Invalid query token") from exc

    validated = validate_query_request(request)
    canonical = encode_query_request_token(validated)
    if not hmac.compare_digest(canonical, token):
        raise QueryContractError("Query token is not canonical")
    return validated


def _build_source_request() -> dict[str, Any]:
    return {
        "workflow_request_schema_version": source_workflow.REQUEST_SCHEMA_VERSION,
        "request_id": SOURCE_WORKFLOW_REQUEST_ID,
        "operation": source_workflow.ALLOWED_OPERATION,
        "explanation_mode": source_workflow.MODE_DETERMINISTIC,
        "max_output_tokens": 112,
        "human_review_required": True,
    }


def _validate_source_response(response: Any) -> dict[str, Any]:
    if type(response) is not dict:
        raise QueryContractError("Source workflow response must be a plain object")

    _require_exact_fields(response, _SOURCE_RESPONSE_FIELDS, "source response")

    research_status = response.get("research_status")
    if type(research_status) is not dict:
        raise QueryContractError("Source research_status must be a plain object")
    _require_exact_fields(
        research_status,
        _RESEARCH_STATUS_FIELDS,
        "source research_status",
    )

    if response.get("restrictions") != source_workflow.WORKFLOW_RESTRICTIONS:
        raise QueryContractError("Source workflow restrictions changed")

    _assert_no_enabled_operational_permission(response)

    try:
        source_workflow.validate_workflow_response(response)
    except Exception as exc:
        raise QueryContractError("Source workflow response validation failed") from exc

    if response["workflow_schema_version"] != source_workflow.WORKFLOW_SCHEMA_VERSION:
        raise QueryContractError("Source workflow schema version changed")
    if (
        response["source_connection_schema_version"]
        != source_workflow.READ_ONLY_CONNECTION_SCHEMA_VERSION
    ):
        raise QueryContractError("Source connection schema version changed")
    if response["operation"] != source_workflow.ALLOWED_OPERATION:
        raise QueryContractError("Source operation changed")
    if response["request_id"] != SOURCE_WORKFLOW_REQUEST_ID:
        raise QueryContractError("Source workflow request_id changed")
    if response["explanation_mode"] != source_workflow.MODE_DETERMINISTIC:
        raise QueryContractError("Source explanation mode changed")
    if response["explanation_route"] != QUERY_ROUTE:
        raise QueryContractError("Source explanation route changed")
    if response["local_model_called"] is not False:
        raise QueryContractError("Source local model call is forbidden")

    return copy.deepcopy(response)


def _build_query_result(
    query_id: str,
    research_status: dict[str, Any],
) -> dict[str, Any]:
    if query_id == PROJECT_COMPLETION_STATUS:
        return {
            "total_project_completed": research_status["total_project_completed"],
        }
    if query_id == LONG_RESEARCH_STATUS:
        return {
            "long_primary_candidate": research_status["long_primary_candidate"],
            "long_secondary_candidate": research_status["long_secondary_candidate"],
            "long_official_dataset_state": research_status[
                "long_official_dataset_state"
            ],
        }
    if query_id == SHORT_RESEARCH_STATUS:
        return {
            "legacy_short_candidate": research_status["legacy_short_candidate"],
            "short_recovery_line": research_status["short_recovery_line"],
            "short_recovery_surviving_variant_count": research_status[
                "short_recovery_surviving_variant_count"
            ],
        }
    if query_id == EVIDENCE_DATASET_STATUS:
        return {
            "long_official_dataset_state": research_status[
                "long_official_dataset_state"
            ],
            "long_official_evidence_row_count": research_status[
                "long_official_evidence_row_count"
            ],
        }
    if query_id == RESEARCH_LOCK_STATUS:
        return {
            "prospective_holdout": research_status["prospective_holdout"],
            "retrospective_lockbox": research_status["retrospective_lockbox"],
        }
    if query_id == OPERATIONAL_PERMISSION_STATUS:
        return {
            "automation": False,
            "capital_use": False,
            "external_actions": False,
            "human_review_required": True,
            "read_only": True,
        }
    raise QueryContractError("Unsupported query_id")


def validate_query_response(response: Any) -> None:
    """Validate the exact Phase 11.6 response contract."""

    if type(response) is not dict:
        raise QueryContractError("Query response must be a plain JSON object")

    _require_exact_fields(response, _RESPONSE_FIELDS, "query response")

    if response["query_response_schema_version"] != QUERY_RESPONSE_SCHEMA_VERSION:
        raise QueryContractError("Query response schema version changed")
    if response["phase"] != PHASE:
        raise QueryContractError("Query response phase changed")
    if response["decision"] != QUERY_DECISION:
        raise QueryContractError("Query response decision changed")
    if response["query_route"] != QUERY_ROUTE:
        raise QueryContractError("Only PYTHON_TEMPLATE is allowed")
    if response["local_model_called"] is not False:
        raise QueryContractError("Local model calls are forbidden")
    if response["human_review_required"] is not True:
        raise QueryContractError("Human review is mandatory")
    if response["restrictions"] != QUERY_RESTRICTIONS:
        raise QueryContractError("Query restrictions changed")
    if (
        response["source_workflow_schema_version"]
        != source_workflow.WORKFLOW_SCHEMA_VERSION
    ):
        raise QueryContractError("Source workflow schema version changed")
    if (
        response["source_connection_schema_version"]
        != source_workflow.READ_ONLY_CONNECTION_SCHEMA_VERSION
    ):
        raise QueryContractError("Source connection schema version changed")
    if response["source_operation"] != source_workflow.ALLOWED_OPERATION:
        raise QueryContractError("Source operation changed")

    request_projection = {
        "query_request_schema_version": QUERY_REQUEST_SCHEMA_VERSION,
        "request_id": response["request_id"],
        "query_id": response["query_id"],
        "human_review_required": response["human_review_required"],
    }
    validate_query_request(request_projection)

    query_result = response["query_result"]
    if type(query_result) is not dict:
        raise QueryContractError("query_result must be a plain object")
    _require_exact_fields(
        query_result,
        _RESULT_FIELDS[response["query_id"]],
        "query_result",
    )
    _assert_no_actionable_response_fields(response)


def execute_query_request(
    request: Any,
    *,
    root: Path = Path("."),
    client: Any = None,
) -> dict[str, Any]:
    """Execute one supervised query through the deterministic Phase 11.5 workflow."""

    validated_request = validate_query_request(request)
    source_request = _build_source_request()

    try:
        validated_source_request = source_workflow.validate_workflow_request(
            source_request
        )
    except Exception as exc:
        raise QueryContractError("Source workflow request validation failed") from exc

    if validated_source_request != source_request:
        raise QueryContractError("Source workflow request normalization changed")

    source_response = source_workflow.execute_workflow_request(
        source_request,
        root=Path(root),
        client=client,
    )
    validated_source_response = _validate_source_response(source_response)

    response = {
        "query_response_schema_version": QUERY_RESPONSE_SCHEMA_VERSION,
        "phase": PHASE,
        "decision": QUERY_DECISION,
        "request_id": validated_request["request_id"],
        "query_id": validated_request["query_id"],
        "query_route": QUERY_ROUTE,
        "local_model_called": False,
        "human_review_required": True,
        "query_result": _build_query_result(
            validated_request["query_id"],
            validated_source_response["research_status"],
        ),
        "restrictions": copy.deepcopy(QUERY_RESTRICTIONS),
        "source_workflow_schema_version": source_workflow.WORKFLOW_SCHEMA_VERSION,
        "source_connection_schema_version": (
            source_workflow.READ_ONLY_CONNECTION_SCHEMA_VERSION
        ),
        "source_operation": source_workflow.ALLOWED_OPERATION,
    }
    validate_query_response(response)
    return response


def execute_query_token(
    token: Any,
    *,
    root: Path = Path("."),
    client: Any = None,
) -> dict[str, Any]:
    """Decode and execute one canonical supervised query token."""

    request = decode_query_request_token(token)
    return execute_query_request(request, root=root, client=client)


__all__ = [
    "ALLOWED_QUERY_IDS",
    "EVIDENCE_DATASET_STATUS",
    "LONG_RESEARCH_STATUS",
    "OPERATIONAL_PERMISSION_STATUS",
    "PHASE",
    "PROJECT_COMPLETION_STATUS",
    "QUERY_DECISION",
    "QUERY_REQUEST_SCHEMA_VERSION",
    "QUERY_RESPONSE_SCHEMA_VERSION",
    "QUERY_RESTRICTIONS",
    "QUERY_ROUTE",
    "QueryContractError",
    "RESEARCH_LOCK_STATUS",
    "SHORT_RESEARCH_STATUS",
    "decode_query_request_token",
    "encode_query_request_token",
    "execute_query_request",
    "execute_query_token",
    "validate_query_request",
    "validate_query_response",
]
