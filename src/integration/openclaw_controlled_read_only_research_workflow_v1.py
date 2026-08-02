from __future__ import annotations

import base64
import binascii
import json
import re
from pathlib import Path
from typing import Any, Mapping

from src.integration.openclaw_controlled_local_utility_connection_v1 import (
    CONNECTION_RESTRICTIONS as LOCAL_CONNECTION_RESTRICTIONS,
    OpenClawLocalUtilityFailure,
    execute_connection_request,
)
from src.integration.openclaw_read_only_local_connection_v1 import (
    CONNECTION_SCHEMA_VERSION as READ_ONLY_CONNECTION_SCHEMA_VERSION,
    LocalConnectionError,
    build_connection_status,
)


PHASE = "11.5"
WORKFLOW_SCHEMA_VERSION = (
    "OPENCLAW_CONTROLLED_READ_ONLY_RESEARCH_WORKFLOW_V1"
)
REQUEST_SCHEMA_VERSION = (
    "OPENCLAW_CONTROLLED_READ_ONLY_RESEARCH_WORKFLOW_REQUEST_V1"
)
ALLOWED_OPERATION = "GET_AND_EXPLAIN_VALIDATED_RESEARCH_STATUS"
MODE_DETERMINISTIC = "DETERMINISTIC_TEMPLATE"
MODE_LOCAL_OLLAMA = "LOCAL_OLLAMA_SUMMARY"
ALLOWED_MODES = {MODE_DETERMINISTIC, MODE_LOCAL_OLLAMA}

MAX_TOKEN_CHARS = 11000
MAX_DECODED_BYTES = 8192
REQUEST_FIELDS = {
    "workflow_request_schema_version",
    "request_id",
    "operation",
    "explanation_mode",
    "max_output_tokens",
    "human_review_required",
}
REQUEST_ID_PATTERN = re.compile(r"^phase-11-5-[a-z0-9][a-z0-9-]{0,79}$")
TOKEN_PATTERN = re.compile(r"^[A-Za-z0-9_-]+$")

FORBIDDEN_ACTIONABLE_FIELDS = {
    "entry",
    "entry_price",
    "stop",
    "stop_loss",
    "target",
    "take_profit",
    "position_size",
    "quantity",
    "leverage",
    "side",
    "order",
    "order_type",
    "exchange_command",
    "browser_command",
    "recipient",
    "destination",
    "send",
    "url",
}

WORKFLOW_RESTRICTIONS = {
    "local_read_only_status_consumption_allowed": True,
    "controlled_local_explanation_allowed": True,
    "status_command_invocation_allowed": True,
    "other_openclaw_tool_invocation_allowed": False,
    "human_explanation_only": True,
    "actionable_trading_fields_present": False,
    "official_dataset_write_allowed": False,
    "openclaw_operational_integration_allowed": False,
    "external_action_allowed": False,
    "browser_control_allowed": False,
    "message_send_allowed": False,
    "trading_execution_allowed": False,
    "signal_generation_enabled": False,
    "paper_trade_execution_allowed": False,
    "real_capital_allowed": False,
    "market_execution_allowed": False,
    "automation_allowed": False,
}

ERROR_EXIT_CODES = {
    "OPENCLAW_RESEARCH_WORKFLOW_E001_INVALID_TOKEN": 20,
    "OPENCLAW_RESEARCH_WORKFLOW_E002_INVALID_REQUEST": 21,
    "OPENCLAW_RESEARCH_WORKFLOW_E003_SOURCE_STATUS_FAILED": 30,
    "OPENCLAW_RESEARCH_WORKFLOW_E004_PERMISSION_BOUNDARY": 31,
    "OPENCLAW_RESEARCH_WORKFLOW_E005_EXPLANATION_FAILED": 32,
    "OPENCLAW_RESEARCH_WORKFLOW_E006_RESPONSE_INVALID": 33,
    "OPENCLAW_RESEARCH_WORKFLOW_E007_INTERNAL_FAIL_CLOSED": 70,
}


class OpenClawResearchWorkflowFailure(RuntimeError):
    def __init__(self, error_id: str, message: str):
        if error_id not in ERROR_EXIT_CODES:
            error_id = "OPENCLAW_RESEARCH_WORKFLOW_E007_INTERNAL_FAIL_CLOSED"
        self.error_id = error_id
        self.exit_code = ERROR_EXIT_CODES[error_id]
        super().__init__(message)


def _require(condition: bool, error_id: str, message: str) -> None:
    if not condition:
        raise OpenClawResearchWorkflowFailure(error_id, message)


def _reject_duplicate_pairs(
    pairs: list[tuple[str, Any]],
) -> dict[str, Any]:
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
        raise OpenClawResearchWorkflowFailure(
            "OPENCLAW_RESEARCH_WORKFLOW_E002_INVALID_REQUEST",
            "Request cannot be serialized canonically",
        ) from exc


def validate_workflow_request(
    request: Mapping[str, Any],
) -> dict[str, Any]:
    _require(
        isinstance(request, Mapping),
        "OPENCLAW_RESEARCH_WORKFLOW_E002_INVALID_REQUEST",
        "Workflow request must be an object",
    )
    _require(
        set(request) == REQUEST_FIELDS,
        "OPENCLAW_RESEARCH_WORKFLOW_E002_INVALID_REQUEST",
        "Workflow request fields mismatch",
    )
    _require(
        request.get("workflow_request_schema_version")
        == REQUEST_SCHEMA_VERSION,
        "OPENCLAW_RESEARCH_WORKFLOW_E002_INVALID_REQUEST",
        "Workflow request schema mismatch",
    )
    request_id = request.get("request_id")
    _require(
        isinstance(request_id, str)
        and REQUEST_ID_PATTERN.fullmatch(request_id) is not None,
        "OPENCLAW_RESEARCH_WORKFLOW_E002_INVALID_REQUEST",
        "request_id is invalid",
    )
    _require(
        request.get("operation") == ALLOWED_OPERATION,
        "OPENCLAW_RESEARCH_WORKFLOW_E002_INVALID_REQUEST",
        "Unsupported operation",
    )
    _require(
        request.get("explanation_mode") in ALLOWED_MODES,
        "OPENCLAW_RESEARCH_WORKFLOW_E002_INVALID_REQUEST",
        "Unsupported explanation mode",
    )
    max_output_tokens = request.get("max_output_tokens")
    _require(
        isinstance(max_output_tokens, int)
        and not isinstance(max_output_tokens, bool)
        and 64 <= max_output_tokens <= 160,
        "OPENCLAW_RESEARCH_WORKFLOW_E002_INVALID_REQUEST",
        "max_output_tokens is outside the allowed boundary",
    )
    _require(
        request.get("human_review_required") is True,
        "OPENCLAW_RESEARCH_WORKFLOW_E004_PERMISSION_BOUNDARY",
        "Human review is mandatory",
    )
    return dict(request)


def encode_workflow_request_token(
    request: Mapping[str, Any],
) -> str:
    validated = validate_workflow_request(request)
    return base64.urlsafe_b64encode(
        _canonical_request_bytes(validated)
    ).decode("ascii").rstrip("=")


def decode_workflow_request_token(token: str) -> dict[str, Any]:
    _require(
        isinstance(token, str) and 0 < len(token) <= MAX_TOKEN_CHARS,
        "OPENCLAW_RESEARCH_WORKFLOW_E001_INVALID_TOKEN",
        "Token length is outside the allowed boundary",
    )
    _require(
        TOKEN_PATTERN.fullmatch(token) is not None,
        "OPENCLAW_RESEARCH_WORKFLOW_E001_INVALID_TOKEN",
        "Token contains unsupported characters",
    )
    padding = "=" * ((4 - len(token) % 4) % 4)
    try:
        decoded = base64.b64decode(
            token + padding,
            altchars=b"-_",
            validate=True,
        )
    except (binascii.Error, ValueError) as exc:
        raise OpenClawResearchWorkflowFailure(
            "OPENCLAW_RESEARCH_WORKFLOW_E001_INVALID_TOKEN",
            "Token is not valid canonical base64url",
        ) from exc
    _require(
        0 < len(decoded) <= MAX_DECODED_BYTES,
        "OPENCLAW_RESEARCH_WORKFLOW_E001_INVALID_TOKEN",
        "Decoded request size is outside the allowed boundary",
    )
    _require(
        base64.urlsafe_b64encode(decoded).decode("ascii").rstrip("=")
        == token,
        "OPENCLAW_RESEARCH_WORKFLOW_E001_INVALID_TOKEN",
        "Token is not canonical base64url",
    )
    _require(
        not decoded.startswith(b"\xef\xbb\xbf"),
        "OPENCLAW_RESEARCH_WORKFLOW_E001_INVALID_TOKEN",
        "Decoded request must not contain a UTF-8 BOM",
    )
    try:
        value = json.loads(
            decoded.decode("utf-8", errors="strict"),
            object_pairs_hook=_reject_duplicate_pairs,
            parse_constant=lambda constant: (_ for _ in ()).throw(
                ValueError(f"Non-finite constant: {constant}")
            ),
        )
    except Exception as exc:
        raise OpenClawResearchWorkflowFailure(
            "OPENCLAW_RESEARCH_WORKFLOW_E001_INVALID_TOKEN",
            "Decoded request is not strict UTF-8 JSON",
        ) from exc
    _require(
        isinstance(value, dict),
        "OPENCLAW_RESEARCH_WORKFLOW_E002_INVALID_REQUEST",
        "Decoded request must be an object",
    )
    validated = validate_workflow_request(value)
    _require(
        _canonical_request_bytes(validated) == decoded,
        "OPENCLAW_RESEARCH_WORKFLOW_E001_INVALID_TOKEN",
        "Decoded request JSON is not canonical",
    )
    return validated


def _walk_keys(value: object) -> set[str]:
    keys: set[str] = set()
    if isinstance(value, Mapping):
        for key, child in value.items():
            keys.add(str(key).lower())
            keys.update(_walk_keys(child))
    elif isinstance(value, list):
        for child in value:
            keys.update(_walk_keys(child))
    return keys


def _validate_source_status(status: Mapping[str, Any]) -> None:
    _require(
        status.get("connection_schema_version")
        == READ_ONLY_CONNECTION_SCHEMA_VERSION,
        "OPENCLAW_RESEARCH_WORKFLOW_E003_SOURCE_STATUS_FAILED",
        "Read-only source schema mismatch",
    )
    _require(
        status.get("decision")
        == (
            "CURRENT_VALIDATED_RESEARCH_STATUS_CONNECTED_"
            "FOR_HUMAN_EXPLANATION_ONLY"
        ),
        "OPENCLAW_RESEARCH_WORKFLOW_E003_SOURCE_STATUS_FAILED",
        "Read-only source decision mismatch",
    )
    research = status.get("research_status")
    restrictions = status.get("restrictions")
    human_review = status.get("human_review")
    _require(
        isinstance(research, Mapping),
        "OPENCLAW_RESEARCH_WORKFLOW_E003_SOURCE_STATUS_FAILED",
        "Read-only research status is missing",
    )
    _require(
        isinstance(restrictions, Mapping),
        "OPENCLAW_RESEARCH_WORKFLOW_E004_PERMISSION_BOUNDARY",
        "Read-only restrictions are missing",
    )
    required_false = (
        "other_openclaw_tool_invocation_allowed",
        "actionable_trading_fields_present",
        "official_dataset_write_allowed",
        "openclaw_operational_integration_allowed",
        "signal_generation_enabled",
        "paper_trade_execution_allowed",
        "real_capital_allowed",
        "market_execution_allowed",
        "automation_allowed",
    )
    for field in required_false:
        _require(
            restrictions.get(field) is False,
            "OPENCLAW_RESEARCH_WORKFLOW_E004_PERMISSION_BOUNDARY",
            f"Read-only prohibited flag enabled or missing: {field}",
        )
    _require(
        restrictions.get("local_read_only_status_consumption_allowed")
        is True,
        "OPENCLAW_RESEARCH_WORKFLOW_E004_PERMISSION_BOUNDARY",
        "Read-only consumption is not enabled",
    )
    _require(
        isinstance(human_review, Mapping)
        and human_review.get("required") is True
        and human_review.get("permission_override_allowed") is False
        and human_review.get("unknown_status_inference_allowed") is False,
        "OPENCLAW_RESEARCH_WORKFLOW_E004_PERMISSION_BOUNDARY",
        "Human-review boundary mismatch",
    )
    _require(
        not _walk_keys(research).intersection(FORBIDDEN_ACTIONABLE_FIELDS),
        "OPENCLAW_RESEARCH_WORKFLOW_E004_PERMISSION_BOUNDARY",
        "Actionable field appeared in validated research status",
    )


def _render_value(value: Any) -> str:
    if isinstance(value, (dict, list)):
        return json.dumps(
            value,
            sort_keys=True,
            ensure_ascii=True,
            separators=(",", ":"),
            allow_nan=False,
        )
    if value is None:
        return "null"
    return str(value)


def build_validated_source_text(
    status: Mapping[str, Any],
) -> str:
    _validate_source_status(status)
    research = status["research_status"]
    ordered_fields = (
        "legacy_short_candidate",
        "short_recovery_line",
        "short_recovery_surviving_variant_count",
        "long_primary_candidate",
        "long_secondary_candidate",
        "long_official_dataset_state",
        "long_official_evidence_row_count",
        "retrospective_lockbox",
        "prospective_holdout",
        "total_project_completed",
    )
    lines = ["Estado científico validado de Trading-AI:"]
    for field in ordered_fields:
        _require(
            field in research,
            "OPENCLAW_RESEARCH_WORKFLOW_E003_SOURCE_STATUS_FAILED",
            f"Required research-status field is missing: {field}",
        )
        lines.append(f"- {field}: {_render_value(research[field])}")
    lines.extend(
        [
            "- human_review_required: true",
            "- official_dataset_write_allowed: false",
            "- signal_generation_enabled: false",
            "- paper_trade_execution_allowed: false",
            "- real_capital_allowed: false",
            "- market_execution_allowed: false",
            "- automation_allowed: false",
        ]
    )
    text = "\n".join(lines)
    _require(
        0 < len(text) <= 4000,
        "OPENCLAW_RESEARCH_WORKFLOW_E003_SOURCE_STATUS_FAILED",
        "Validated source text is outside the allowed boundary",
    )
    return text


def _deterministic_explanation(source_text: str) -> dict[str, Any]:
    return {
        "route": "PYTHON_TEMPLATE",
        "decision": (
            "VALIDATED_RESEARCH_STATUS_FORMATTED_FOR_HUMAN_REVIEW"
        ),
        "output": {"result": source_text},
        "local_model_called": False,
    }


def _local_explanation(
    source_text: str,
    max_output_tokens: int,
    *,
    client: Any = None,
) -> dict[str, Any]:
    internal_request = {
        "connection_request_schema_version": (
            "OPENCLAW_CONTROLLED_LOCAL_UTILITY_REQUEST_V1"
        ),
        "request_id": "phase-11-4-read-only-research-summary-v1",
        "task_type": "SUMMARIZE_VALIDATED_TEXT",
        "payload": {"text": source_text},
        "max_output_tokens": max_output_tokens,
        "human_review_required": True,
    }
    try:
        delegated = execute_connection_request(
            internal_request,
            client=client,
        )
    except OpenClawLocalUtilityFailure as exc:
        raise OpenClawResearchWorkflowFailure(
            "OPENCLAW_RESEARCH_WORKFLOW_E005_EXPLANATION_FAILED",
            f"Controlled local explanation failed: {exc.error_id}: {exc}",
        ) from exc
    _require(
        delegated.get("decision")
        == "OPENCLAW_CONTROLLED_LOCAL_UTILITY_COMPLETED_FOR_HUMAN_REVIEW",
        "OPENCLAW_RESEARCH_WORKFLOW_E005_EXPLANATION_FAILED",
        "Controlled local explanation did not complete",
    )
    _require(
        delegated.get("delegated_route") == "LOCAL_OLLAMA",
        "OPENCLAW_RESEARCH_WORKFLOW_E005_EXPLANATION_FAILED",
        "Controlled local explanation used an unexpected route",
    )
    _require(
        delegated.get("local_model_called") is True,
        "OPENCLAW_RESEARCH_WORKFLOW_E005_EXPLANATION_FAILED",
        "Controlled local explanation did not call the local model",
    )
    restrictions = delegated.get("restrictions")
    _require(
        restrictions == LOCAL_CONNECTION_RESTRICTIONS,
        "OPENCLAW_RESEARCH_WORKFLOW_E004_PERMISSION_BOUNDARY",
        "Controlled local explanation restrictions mismatch",
    )
    output = delegated.get("output")
    _require(
        isinstance(output, Mapping)
        and isinstance(output.get("result"), str)
        and bool(output["result"].strip()),
        "OPENCLAW_RESEARCH_WORKFLOW_E005_EXPLANATION_FAILED",
        "Controlled local explanation output is invalid",
    )
    return {
        "route": delegated["delegated_route"],
        "decision": delegated["decision"],
        "output": dict(output),
        "local_model_called": True,
        "local_model": delegated.get("local_model"),
        "local_metrics": delegated.get("local_metrics"),
    }


def _build_research_snapshot(status: Mapping[str, Any]) -> dict[str, Any]:
    research = status["research_status"]
    fields = (
        "legacy_short_candidate",
        "short_recovery_line",
        "short_recovery_surviving_variant_count",
        "long_primary_candidate",
        "long_secondary_candidate",
        "long_official_dataset_state",
        "long_official_evidence_row_count",
        "retrospective_lockbox",
        "prospective_holdout",
        "total_project_completed",
    )
    return {field: research[field] for field in fields}


def validate_workflow_response(response: Mapping[str, Any]) -> None:
    expected_fields = {
        "workflow_schema_version",
        "phase",
        "request_id",
        "operation",
        "decision",
        "source_connection_schema_version",
        "source_connection_decision",
        "explanation_mode",
        "explanation_route",
        "explanation_decision",
        "explanation_output",
        "local_model_called",
        "research_status",
        "restrictions",
        "human_review",
    }
    _require(
        set(response) == expected_fields,
        "OPENCLAW_RESEARCH_WORKFLOW_E006_RESPONSE_INVALID",
        "Workflow response fields mismatch",
    )
    _require(
        response.get("workflow_schema_version") == WORKFLOW_SCHEMA_VERSION,
        "OPENCLAW_RESEARCH_WORKFLOW_E006_RESPONSE_INVALID",
        "Workflow response schema mismatch",
    )
    _require(
        response.get("decision")
        == (
            "OPENCLAW_CONTROLLED_READ_ONLY_RESEARCH_WORKFLOW_"
            "COMPLETED_FOR_HUMAN_REVIEW"
        ),
        "OPENCLAW_RESEARCH_WORKFLOW_E006_RESPONSE_INVALID",
        "Workflow decision mismatch",
    )
    _require(
        response.get("restrictions") == WORKFLOW_RESTRICTIONS,
        "OPENCLAW_RESEARCH_WORKFLOW_E004_PERMISSION_BOUNDARY",
        "Workflow restrictions mismatch",
    )
    human = response.get("human_review")
    _require(
        human
        == {
            "required": True,
            "permission_override_allowed": False,
            "unknown_status_inference_allowed": False,
        },
        "OPENCLAW_RESEARCH_WORKFLOW_E004_PERMISSION_BOUNDARY",
        "Workflow human-review boundary mismatch",
    )
    _require(
        not _walk_keys(response["research_status"]).intersection(
            FORBIDDEN_ACTIONABLE_FIELDS
        ),
        "OPENCLAW_RESEARCH_WORKFLOW_E004_PERMISSION_BOUNDARY",
        "Actionable field appeared in workflow response",
    )
    output = response.get("explanation_output")
    _require(
        isinstance(output, Mapping)
        and isinstance(output.get("result"), str)
        and bool(output["result"].strip()),
        "OPENCLAW_RESEARCH_WORKFLOW_E006_RESPONSE_INVALID",
        "Workflow explanation output is invalid",
    )


def execute_workflow_request(
    request: Mapping[str, Any],
    *,
    root: Path | str = Path("."),
    client: Any = None,
) -> dict[str, Any]:
    validated = validate_workflow_request(request)
    try:
        status = build_connection_status(root)
    except (LocalConnectionError, Exception) as exc:
        raise OpenClawResearchWorkflowFailure(
            "OPENCLAW_RESEARCH_WORKFLOW_E003_SOURCE_STATUS_FAILED",
            f"Read-only source status failed closed: {type(exc).__name__}: {exc}",
        ) from exc
    _validate_source_status(status)
    source_text = build_validated_source_text(status)

    if validated["explanation_mode"] == MODE_DETERMINISTIC:
        explanation = _deterministic_explanation(source_text)
    else:
        explanation = _local_explanation(
            source_text,
            validated["max_output_tokens"],
            client=client,
        )

    response = {
        "workflow_schema_version": WORKFLOW_SCHEMA_VERSION,
        "phase": PHASE,
        "request_id": validated["request_id"],
        "operation": validated["operation"],
        "decision": (
            "OPENCLAW_CONTROLLED_READ_ONLY_RESEARCH_WORKFLOW_"
            "COMPLETED_FOR_HUMAN_REVIEW"
        ),
        "source_connection_schema_version": status[
            "connection_schema_version"
        ],
        "source_connection_decision": status["decision"],
        "explanation_mode": validated["explanation_mode"],
        "explanation_route": explanation["route"],
        "explanation_decision": explanation["decision"],
        "explanation_output": explanation["output"],
        "local_model_called": explanation["local_model_called"],
        "research_status": _build_research_snapshot(status),
        "restrictions": dict(WORKFLOW_RESTRICTIONS),
        "human_review": {
            "required": True,
            "permission_override_allowed": False,
            "unknown_status_inference_allowed": False,
        },
    }
    validate_workflow_response(response)
    return response


def execute_workflow_token(
    token: str,
    *,
    root: Path | str = Path("."),
    client: Any = None,
) -> dict[str, Any]:
    return execute_workflow_request(
        decode_workflow_request_token(token),
        root=root,
        client=client,
    )


__all__ = [
    "ALLOWED_MODES",
    "ALLOWED_OPERATION",
    "ERROR_EXIT_CODES",
    "FORBIDDEN_ACTIONABLE_FIELDS",
    "MODE_DETERMINISTIC",
    "MODE_LOCAL_OLLAMA",
    "OpenClawResearchWorkflowFailure",
    "PHASE",
    "REQUEST_SCHEMA_VERSION",
    "WORKFLOW_RESTRICTIONS",
    "WORKFLOW_SCHEMA_VERSION",
    "build_validated_source_text",
    "decode_workflow_request_token",
    "encode_workflow_request_token",
    "execute_workflow_request",
    "execute_workflow_token",
    "validate_workflow_request",
    "validate_workflow_response",
]
