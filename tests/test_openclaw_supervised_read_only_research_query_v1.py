"""Tests for the Phase 11.6 closed supervised query contract."""

from __future__ import annotations

import base64
import copy
import json
from pathlib import Path
from typing import Any

import pytest

from src.integration import openclaw_controlled_read_only_research_workflow_v1 as source_workflow
from src.integration import openclaw_supervised_read_only_research_query_v1 as query_module
from src.integration.openclaw_supervised_read_only_research_query_v1 import (
    ALLOWED_QUERY_IDS,
    EVIDENCE_DATASET_STATUS,
    QUERY_REQUEST_SCHEMA_VERSION,
    QUERY_ROUTE,
    QueryContractError,
    decode_query_request_token,
    encode_query_request_token,
    execute_query_request,
    execute_query_token,
    validate_query_request,
    validate_query_response,
)

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
EXAMPLE_REQUEST_PATH = (
    REPOSITORY_ROOT
    / "examples"
    / "phase_11_6_first_controlled_supervised_query_request_v1.json"
)


def _request(query_id: str = EVIDENCE_DATASET_STATUS) -> dict[str, Any]:
    suffix = query_id.casefold().replace("_", "-")
    return {
        "query_request_schema_version": QUERY_REQUEST_SCHEMA_VERSION,
        "request_id": f"phase-11-6-{suffix}-v1",
        "query_id": query_id,
        "human_review_required": True,
    }


def _source_request() -> dict[str, Any]:
    return {
        "workflow_request_schema_version": source_workflow.REQUEST_SCHEMA_VERSION,
        "request_id": query_module.SOURCE_WORKFLOW_REQUEST_ID,
        "operation": source_workflow.ALLOWED_OPERATION,
        "explanation_mode": source_workflow.MODE_DETERMINISTIC,
        "max_output_tokens": 112,
        "human_review_required": True,
    }


def _valid_source_response() -> dict[str, Any]:
    return source_workflow.execute_workflow_request(
        _source_request(),
        root=REPOSITORY_ROOT,
    )


def _encode_raw_json(raw_json: str) -> str:
    return base64.urlsafe_b64encode(raw_json.encode("utf-8")).decode("ascii").rstrip(
        "="
    )


@pytest.mark.parametrize("query_id", sorted(ALLOWED_QUERY_IDS))
def test_executes_each_allowed_query_through_python_template(query_id: str) -> None:
    response = execute_query_request(_request(query_id), root=REPOSITORY_ROOT)

    assert response["query_id"] == query_id
    assert response["query_route"] == QUERY_ROUTE
    assert response["local_model_called"] is False
    assert response["human_review_required"] is True
    validate_query_response(response)


def test_first_controlled_evidence_query_returns_expected_status() -> None:
    request = json.loads(EXAMPLE_REQUEST_PATH.read_text(encoding="utf-8"))
    response = execute_query_request(request, root=REPOSITORY_ROOT)

    assert response["query_id"] == EVIDENCE_DATASET_STATUS
    assert response["query_route"] == "PYTHON_TEMPLATE"
    assert response["local_model_called"] is False
    assert response["query_result"] == {
        "long_official_dataset_state": (
            "INITIALIZED_EMPTY_READY_FOR_CONTROLLED_EVIDENCE"
        ),
        "long_official_evidence_row_count": 0,
    }


def test_canonical_token_round_trip_is_stable() -> None:
    request = _request()
    token = encode_query_request_token(request)

    assert decode_query_request_token(token) == request
    assert encode_query_request_token(decode_query_request_token(token)) == token


def test_response_validator_accepts_generated_response() -> None:
    response = execute_query_token(
        encode_query_request_token(_request()),
        root=REPOSITORY_ROOT,
    )

    validate_query_response(response)


def test_rejects_noncanonical_token() -> None:
    token = encode_query_request_token(_request())

    with pytest.raises(QueryContractError):
        decode_query_request_token(f"{token}=")


def test_rejects_token_with_shell_metacharacters() -> None:
    token = encode_query_request_token(_request())

    with pytest.raises(QueryContractError):
        decode_query_request_token(f"{token};whoami")


def test_rejects_duplicate_json_key() -> None:
    raw = (
        '{"human_review_required":true,'
        '"query_id":"EVIDENCE_DATASET_STATUS",'
        '"query_id":"LONG_RESEARCH_STATUS",'
        '"query_request_schema_version":'
        '"OPENCLAW_SUPERVISED_READ_ONLY_RESEARCH_QUERY_REQUEST_V1",'
        '"request_id":"phase-11-6-duplicate-key-v1"}'
    )

    with pytest.raises(QueryContractError):
        decode_query_request_token(_encode_raw_json(raw))


def test_rejects_extra_or_missing_request_field() -> None:
    extra = {**_request(), "unexpected": "blocked"}
    missing = _request()
    missing.pop("query_id")

    with pytest.raises(QueryContractError):
        validate_query_request(extra)
    with pytest.raises(QueryContractError):
        validate_query_request(missing)


def test_rejects_human_review_false() -> None:
    request = {**_request(), "human_review_required": False}

    with pytest.raises(QueryContractError):
        validate_query_request(request)


def test_rejects_query_id_outside_closed_catalog() -> None:
    request = {**_request(), "query_id": "FREE_FORM_RESEARCH"}

    with pytest.raises(QueryContractError):
        validate_query_request(request)


def test_rejects_unsafe_request_id() -> None:
    request = {**_request(), "request_id": "unsafe;whoami"}

    with pytest.raises(QueryContractError):
        validate_query_request(request)


def test_rejects_symbol_and_strategy_fields() -> None:
    for forbidden_field in ("symbol", "strategy"):
        request = {**_request(), forbidden_field: "blocked"}
        with pytest.raises(QueryContractError):
            validate_query_request(request)


def test_rejects_source_response_with_extra_field(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    request = _request()
    source_response = copy.deepcopy(_valid_source_response())
    source_response["unexpected_source_field"] = "blocked"

    monkeypatch.setattr(
        query_module.source_workflow,
        "execute_workflow_request",
        lambda *args, **kwargs: source_response,
    )

    with pytest.raises(QueryContractError):
        execute_query_request(request, root=REPOSITORY_ROOT)


def test_rejects_source_response_with_operational_permission_enabled(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    request = _request()
    source_response = copy.deepcopy(_valid_source_response())
    human_review = source_response.get("human_review")
    if not isinstance(human_review, dict):
        human_review = {"source_value": human_review}
        source_response["human_review"] = human_review
    human_review["operational_permission_enabled"] = True

    monkeypatch.setattr(
        query_module.source_workflow,
        "execute_workflow_request",
        lambda *args, **kwargs: source_response,
    )

    with pytest.raises(QueryContractError):
        execute_query_request(request, root=REPOSITORY_ROOT)
