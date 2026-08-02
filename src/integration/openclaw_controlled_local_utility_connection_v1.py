from __future__ import annotations

import base64
import binascii
import json
import re
from typing import Any, Mapping

from src.integration.local_auxiliary_model_routing_v1 import (
    LOCAL_MODEL,
    LOCAL_TASKS,
    RESTRICTIONS as ROUTER_RESTRICTIONS,
    ROUTE_LOCAL_OLLAMA,
    ROUTE_MODEL_PRINCIPAL,
    ROUTE_PYTHON_TEMPLATE,
    ROUTING_SCHEMA_VERSION,
    TEMPLATE_TASKS,
    LocalModelClient,
    RoutingFailure,
    execute_request,
)


PHASE = "11.4"
CONNECTION_SCHEMA_VERSION = "OPENCLAW_CONTROLLED_LOCAL_UTILITY_CONNECTION_V1"
REQUEST_SCHEMA_VERSION = "OPENCLAW_CONTROLLED_LOCAL_UTILITY_REQUEST_V1"
MAX_TOKEN_CHARS = 11000
MAX_DECODED_BYTES = 8192

REQUEST_FIELDS = {
    "connection_request_schema_version",
    "request_id",
    "task_type",
    "payload",
    "max_output_tokens",
    "human_review_required",
}

ALLOWED_TASKS = TEMPLATE_TASKS | LOCAL_TASKS
TOKEN_PATTERN = re.compile(r"^[A-Za-z0-9_-]+$")
REQUEST_ID_PATTERN = re.compile(r"^phase-11-4-[a-z0-9][a-z0-9-]{0,79}$")

CONNECTION_RESTRICTIONS = {
    "human_review_required": True,
    "external_action_allowed": False,
    "other_openclaw_tool_invocation_allowed": False,
    "browser_control_allowed": False,
    "message_send_allowed": False,
    "trading_execution_allowed": False,
    "official_dataset_write_allowed": False,
    "signal_generation_enabled": False,
    "paper_trade_execution_allowed": False,
    "real_capital_allowed": False,
    "market_execution_allowed": False,
    "automation_allowed": False,
}

ERROR_EXIT_CODES = {
    "OPENCLAW_LOCAL_UTILITY_E001_INVALID_TOKEN": 20,
    "OPENCLAW_LOCAL_UTILITY_E002_INVALID_REQUEST": 21,
    "OPENCLAW_LOCAL_UTILITY_E003_TASK_NOT_ALLOWED": 22,
    "OPENCLAW_LOCAL_UTILITY_E004_ROUTER_FAILED": 30,
    "OPENCLAW_LOCAL_UTILITY_E005_INTERNAL_FAIL_CLOSED": 70,
}


class OpenClawLocalUtilityFailure(RuntimeError):
    def __init__(self, error_id: str, message: str):
        if error_id not in ERROR_EXIT_CODES:
            error_id = "OPENCLAW_LOCAL_UTILITY_E005_INTERNAL_FAIL_CLOSED"
        self.error_id = error_id
        self.exit_code = ERROR_EXIT_CODES[error_id]
        super().__init__(message)


def _require(condition: bool, error_id: str, message: str) -> None:
    if not condition:
        raise OpenClawLocalUtilityFailure(error_id, message)


def _reject_duplicate_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Duplicate JSON field: {key}")
        result[key] = value
    return result


def _canonical_request_bytes(request: Mapping[str, Any]) -> bytes:
    try:
        return json.dumps(
            dict(request),
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
            allow_nan=False,
        ).encode("utf-8")
    except Exception as exc:
        raise OpenClawLocalUtilityFailure(
            "OPENCLAW_LOCAL_UTILITY_E002_INVALID_REQUEST",
            "Request cannot be serialized canonically",
        ) from exc


def encode_request_token(request: Mapping[str, Any]) -> str:
    validated = validate_connection_request(request)
    encoded = base64.urlsafe_b64encode(
        _canonical_request_bytes(validated)
    ).decode("ascii")
    return encoded.rstrip("=")


def decode_request_token(token: str) -> dict[str, Any]:
    _require(
        isinstance(token, str) and 0 < len(token) <= MAX_TOKEN_CHARS,
        "OPENCLAW_LOCAL_UTILITY_E001_INVALID_TOKEN",
        "Request token length is outside the allowed boundary",
    )
    _require(
        TOKEN_PATTERN.fullmatch(token) is not None,
        "OPENCLAW_LOCAL_UTILITY_E001_INVALID_TOKEN",
        "Request token contains unsupported characters",
    )

    padding = "=" * ((4 - len(token) % 4) % 4)
    try:
        decoded = base64.b64decode(
            token + padding,
            altchars=b"-_",
            validate=True,
        )
    except (binascii.Error, ValueError) as exc:
        raise OpenClawLocalUtilityFailure(
            "OPENCLAW_LOCAL_UTILITY_E001_INVALID_TOKEN",
            "Request token is not valid canonical base64url",
        ) from exc

    _require(
        0 < len(decoded) <= MAX_DECODED_BYTES,
        "OPENCLAW_LOCAL_UTILITY_E001_INVALID_TOKEN",
        "Decoded request size is outside the allowed boundary",
    )
    _require(
        base64.urlsafe_b64encode(decoded).decode("ascii").rstrip("=") == token,
        "OPENCLAW_LOCAL_UTILITY_E001_INVALID_TOKEN",
        "Request token is not canonical base64url",
    )
    _require(
        not decoded.startswith(b"\xef\xbb\xbf"),
        "OPENCLAW_LOCAL_UTILITY_E001_INVALID_TOKEN",
        "Decoded request must not contain a UTF-8 BOM",
    )

    try:
        text = decoded.decode("utf-8", errors="strict")
        value = json.loads(
            text,
            object_pairs_hook=_reject_duplicate_pairs,
            parse_constant=lambda constant: (_ for _ in ()).throw(
                ValueError(f"Non-finite JSON constant: {constant}")
            ),
        )
    except Exception as exc:
        raise OpenClawLocalUtilityFailure(
            "OPENCLAW_LOCAL_UTILITY_E001_INVALID_TOKEN",
            "Decoded request is not strict UTF-8 JSON",
        ) from exc

    _require(
        isinstance(value, dict),
        "OPENCLAW_LOCAL_UTILITY_E002_INVALID_REQUEST",
        "Decoded request must be a JSON object",
    )
    validated = validate_connection_request(value)
    _require(
        _canonical_request_bytes(validated) == decoded,
        "OPENCLAW_LOCAL_UTILITY_E001_INVALID_TOKEN",
        "Decoded request JSON is not canonical",
    )
    return validated


def validate_connection_request(
    request: Mapping[str, Any],
) -> dict[str, Any]:
    _require(
        isinstance(request, Mapping),
        "OPENCLAW_LOCAL_UTILITY_E002_INVALID_REQUEST",
        "Connection request must be an object",
    )
    _require(
        set(request) == REQUEST_FIELDS,
        "OPENCLAW_LOCAL_UTILITY_E002_INVALID_REQUEST",
        "Connection request fields mismatch",
    )
    _require(
        request.get("connection_request_schema_version")
        == REQUEST_SCHEMA_VERSION,
        "OPENCLAW_LOCAL_UTILITY_E002_INVALID_REQUEST",
        "Connection request schema version mismatch",
    )

    request_id = request.get("request_id")
    task_type = request.get("task_type")
    payload = request.get("payload")
    max_output_tokens = request.get("max_output_tokens")

    _require(
        isinstance(request_id, str)
        and REQUEST_ID_PATTERN.fullmatch(request_id) is not None,
        "OPENCLAW_LOCAL_UTILITY_E002_INVALID_REQUEST",
        "request_id is invalid",
    )
    _require(
        isinstance(task_type, str) and task_type in ALLOWED_TASKS,
        "OPENCLAW_LOCAL_UTILITY_E003_TASK_NOT_ALLOWED",
        f"Task is not allowed through OpenClaw: {task_type}",
    )
    _require(
        isinstance(payload, dict),
        "OPENCLAW_LOCAL_UTILITY_E002_INVALID_REQUEST",
        "payload must be an object",
    )
    _require(
        isinstance(max_output_tokens, int)
        and not isinstance(max_output_tokens, bool)
        and 64 <= max_output_tokens <= 160,
        "OPENCLAW_LOCAL_UTILITY_E002_INVALID_REQUEST",
        "max_output_tokens is outside the allowed boundary",
    )
    _require(
        request.get("human_review_required") is True,
        "OPENCLAW_LOCAL_UTILITY_E002_INVALID_REQUEST",
        "Human review is mandatory",
    )

    return dict(request)


def _build_router_request(
    connection_request: Mapping[str, Any],
) -> dict[str, Any]:
    return {
        "task_type": connection_request["task_type"],
        "payload": connection_request["payload"],
        "max_output_tokens": connection_request["max_output_tokens"],
        "human_review_required": True,
        "allow_external_action": False,
        "allow_actionable_trading_fields": False,
    }


def _validate_delegated_restrictions(
    delegated: Mapping[str, Any],
) -> None:
    restrictions = delegated.get("restrictions")
    _require(
        isinstance(restrictions, dict),
        "OPENCLAW_LOCAL_UTILITY_E004_ROUTER_FAILED",
        "Delegated router restrictions are missing",
    )
    for key, expected in ROUTER_RESTRICTIONS.items():
        _require(
            restrictions.get(key) is expected,
            "OPENCLAW_LOCAL_UTILITY_E004_ROUTER_FAILED",
            f"Delegated router restriction mismatch: {key}",
        )


def execute_connection_request(
    connection_request: Mapping[str, Any],
    *,
    client: LocalModelClient | None = None,
) -> dict[str, Any]:
    validated = validate_connection_request(connection_request)

    try:
        delegated = execute_request(
            _build_router_request(validated),
            client=client,
        )
    except RoutingFailure as exc:
        raise OpenClawLocalUtilityFailure(
            "OPENCLAW_LOCAL_UTILITY_E004_ROUTER_FAILED",
            f"Local auxiliary router failed closed: {exc.error_id}: {exc}",
        ) from exc

    _validate_delegated_restrictions(delegated)

    delegated_route = delegated.get("route")
    _require(
        delegated_route in {
            ROUTE_PYTHON_TEMPLATE,
            ROUTE_LOCAL_OLLAMA,
            ROUTE_MODEL_PRINCIPAL,
        },
        "OPENCLAW_LOCAL_UTILITY_E004_ROUTER_FAILED",
        "Delegated route is invalid",
    )

    if delegated_route == ROUTE_MODEL_PRINCIPAL:
        decision = "OPENCLAW_LOCAL_UTILITY_REQUIRES_PRINCIPAL_REVIEW"
        output = None
    else:
        decision = (
            "OPENCLAW_CONTROLLED_LOCAL_UTILITY_COMPLETED_FOR_HUMAN_REVIEW"
        )
        output = delegated.get("output")

    response = {
        "connection_schema_version": CONNECTION_SCHEMA_VERSION,
        "phase": PHASE,
        "request_id": validated["request_id"],
        "task_type": validated["task_type"],
        "decision": decision,
        "delegated_routing_schema_version": ROUTING_SCHEMA_VERSION,
        "delegated_route": delegated_route,
        "delegated_decision": delegated.get("decision"),
        "output": output,
        "local_model_called": delegated.get("local_model_called") is True,
        "restrictions": dict(CONNECTION_RESTRICTIONS),
    }

    if delegated.get("local_model") == LOCAL_MODEL:
        response["local_model"] = LOCAL_MODEL
    if isinstance(delegated.get("local_metrics"), dict):
        response["local_metrics"] = dict(delegated["local_metrics"])

    return response


def execute_request_token(
    token: str,
    *,
    client: LocalModelClient | None = None,
) -> dict[str, Any]:
    return execute_connection_request(
        decode_request_token(token),
        client=client,
    )


__all__ = [
    "ALLOWED_TASKS",
    "CONNECTION_RESTRICTIONS",
    "CONNECTION_SCHEMA_VERSION",
    "ERROR_EXIT_CODES",
    "OpenClawLocalUtilityFailure",
    "REQUEST_SCHEMA_VERSION",
    "decode_request_token",
    "encode_request_token",
    "execute_connection_request",
    "execute_request_token",
    "validate_connection_request",
]
