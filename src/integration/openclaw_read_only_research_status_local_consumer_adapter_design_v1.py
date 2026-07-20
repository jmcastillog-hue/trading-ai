from __future__ import annotations

import copy
import hashlib
import json
from typing import Any, Mapping


PHASE = "10.42R.6"
SCHEMA_VERSION = "OPENCLAW_READ_ONLY_RESEARCH_STATUS_LOCAL_CONSUMER_ADAPTER_DESIGN_V1"
ADAPTER_MODE = "DESIGN_ONLY_LOCAL_READ_ONLY_NO_RUNTIME_INTEGRATION"
SOURCE_REVIEW_COMMIT = "7e6d180f0cee72437e086eff0b0596a64f22ea78"
SOURCE_REVIEW_MODULE_SHA256 = (
    "138181a806f9c0f4d7045cce27c48e9b976de94a44da27824c9548cd9862a89b"
)
SOURCE_REVIEW_DOCUMENT_SHA256 = (
    "365b254e7814c8d238aa2f04dd9a45d9c99d35f8bb82dd0011b9f1374e9a269b"
)
SOURCE_CONTRACT_ROOT_SHA256 = (
    "ba84140879bac8a897505bd55e12d3c117354caf1a5a5ad4f6c3eb003bd6fa46"
)
SOURCE_SNAPSHOT_SHA256 = (
    "72a77f3a726d38f0008378218958a5ea8ee8fb0162477692a7370dcf9af43e88"
)
SOURCE_MANIFEST_SHA256 = (
    "f829010549a79fb3eb35b38ce51736f730020747d6fc77b7fa56eac5ade6a5f7"
)
SOURCE_SNAPSHOT_SIZE_BYTES = 5965
SOURCE_BUNDLE_DIRECTORY = "reports/phase_10_42r_4/openclaw_read_only_export_v1"
SOURCE_SNAPSHOT_FILENAME = "openclaw_read_only_research_status_v1.json"
SOURCE_MANIFEST_FILENAME = "openclaw_read_only_research_status_v1.manifest.json"
PHASE_10_43_ROUTE = (
    "PHASE_10_43_LONG_FORWARD_OBSERVATION_EVIDENCE_COLLECTION_"
    "OFFICIAL_DATASET_ATOMIC_WRITE_HARNESS_DESIGN_REVIEW_V1"
)
RECOMMENDED_NEXT_PHASE = (
    "PHASE_10_42R_7_OPENCLAW_READ_ONLY_RESEARCH_STATUS_"
    "LOCAL_CONSUMER_ADAPTER_DESIGN_REVIEW_V1"
)

ALLOWED_OPERATION = "GET_VALIDATED_RESEARCH_STATUS"
ALLOWED_RESPONSE_PROFILE = "HUMAN_EXPLANATION_ONLY"

REQUEST_FIELDS = (
    "operation",
    "response_profile",
    "require_human_review",
    "allow_actionable_fields",
)

RESPONSE_FIELDS = (
    "adapter_schema_version",
    "adapter_mode",
    "decision",
    "source",
    "research_status",
    "restrictions",
    "human_review",
    "next_routes",
)

FORBIDDEN_ACTIONABLE_FIELDS = (
    "entry",
    "entry_price",
    "stop",
    "stop_loss",
    "target",
    "take_profit",
    "position_size",
    "leverage",
    "order",
    "order_type",
    "quantity",
    "side",
    "signal",
    "trade_instruction",
    "exchange_command",
)

ERROR_REGISTRY = {
    "ADAPTER_E001_INVALID_REQUEST_SHAPE": 20,
    "ADAPTER_E002_UNSUPPORTED_OPERATION": 21,
    "ADAPTER_E003_SOURCE_AUTHORITY_FAILURE": 22,
    "ADAPTER_E004_EXPORT_BUNDLE_INTEGRITY_FAILURE": 23,
    "ADAPTER_E005_PERMISSION_BOUNDARY_VIOLATION": 24,
    "ADAPTER_E006_RESPONSE_ALLOWLIST_VIOLATION": 25,
    "ADAPTER_E007_HUMAN_REVIEW_REQUIREMENT_MISSING": 26,
    "ADAPTER_E008_STALE_SOURCE_BINDING": 27,
    "ADAPTER_E009_RUNTIME_INTEGRATION_PROHIBITED": 28,
    "ADAPTER_E010_INTERNAL_FAIL_CLOSED": 70,
}

VALIDATION_SEQUENCE = (
    "VALIDATE_REQUEST_EXACT_SHAPE",
    "VALIDATE_SOURCE_REVIEW_COMMIT_ANCESTRY",
    "VALIDATE_SOURCE_REVIEW_HASH_BINDINGS",
    "VALIDATE_EXACT_TWO_FILE_EXPORT_INVENTORY",
    "VALIDATE_STRICT_UTF8_JSON_NO_DUPLICATE_FIELDS",
    "VALIDATE_SNAPSHOT_AND_MANIFEST_HASHES_AND_SIZE",
    "REPRODUCE_CONTRACT_ROOT",
    "VALIDATE_ALL_PROHIBITED_CAPABILITIES_FALSE",
    "BUILD_ALLOWLISTED_HUMAN_EXPLANATION_RESPONSE",
    "VALIDATE_RESPONSE_EXACT_SHAPE_AND_NO_ACTIONABLE_FIELDS",
    "REQUIRE_HUMAN_REVIEW_BEFORE_ANY_FUTURE_USE",
)

READ_BOUNDARY = {
    "repository_root_resolution": "CALLER_SUPPLIED_TRUSTED_REPOSITORY_ROOT",
    "allowed_directory": SOURCE_BUNDLE_DIRECTORY,
    "allowed_files": [SOURCE_SNAPSHOT_FILENAME, SOURCE_MANIFEST_FILENAME],
    "exact_file_count": 2,
    "subdirectories_allowed": False,
    "symbolic_links_allowed": False,
    "path_traversal_allowed": False,
    "glob_expansion_allowed": False,
    "arbitrary_path_override_allowed": False,
}

WRITE_BOUNDARY = {
    "filesystem_write_allowed": False,
    "source_bundle_mutation_allowed": False,
    "official_dataset_write_allowed": False,
    "temporary_file_creation_allowed": False,
    "cache_write_allowed": False,
    "log_file_write_allowed": False,
    "stdout_json_response_future_only": True,
}

TRANSPORT_BOUNDARY = {
    "future_transport": "LOCAL_PROCESS_STDIO_SINGLE_REQUEST_SINGLE_RESPONSE",
    "transport_implemented_in_this_phase": False,
    "persistent_process_allowed": False,
    "network_allowed": False,
    "http_allowed": False,
    "socket_allowed": False,
    "api_server_allowed": False,
    "background_service_allowed": False,
    "openclaw_invocation_allowed": False,
    "lm_studio_invocation_allowed": False,
    "tool_registration_allowed": False,
    "shell_command_execution_allowed": False,
}

OPERATIONAL_PERMISSIONS = {
    "openclaw_runtime_status_consumption_allowed": False,
    "openclaw_tool_invocation_allowed": False,
    "openclaw_operational_integration_allowed": False,
    "historical_evaluation_allowed": False,
    "backtest_execution_allowed": False,
    "performance_metric_recalculation_allowed": False,
    "candidate_comparison_allowed": False,
    "candidate_ranking_allowed": False,
    "winner_selection_allowed": False,
    "candidate_mutation_allowed": False,
    "retrospective_lockbox_access_allowed": False,
    "prospective_holdout_access_allowed": False,
    "forward_observation_start_allowed": False,
    "official_dataset_write_allowed": False,
    "evidence_persistence_allowed": False,
    "signal_generation_enabled": False,
    "live_alerts_allowed": False,
    "paper_trade_execution_allowed": False,
    "real_capital_allowed": False,
    "market_execution_allowed": False,
    "exchange_execution_allowed": False,
    "automation_allowed": False,
    "execution_allowed": False,
}


class AdapterDesignError(ValueError):
    """Raised whenever the design contract would permit an unsafe adapter."""


def canonical_json(value: object) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    )


def canonical_pretty_json(value: object) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        indent=2,
        ensure_ascii=True,
        allow_nan=False,
    ) + "\n"


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise AdapterDesignError(message)


def _design_root_material(design: Mapping[str, Any]) -> dict[str, Any]:
    material = copy.deepcopy(dict(design))
    material.pop("design_root_sha256", None)
    return material


def calculate_design_root(design: Mapping[str, Any]) -> str:
    return sha256_bytes(canonical_json(_design_root_material(design)).encode("utf-8"))


def sample_request() -> dict[str, Any]:
    return {
        "operation": ALLOWED_OPERATION,
        "response_profile": ALLOWED_RESPONSE_PROFILE,
        "require_human_review": True,
        "allow_actionable_fields": False,
    }


def sample_response() -> dict[str, Any]:
    return {
        "adapter_schema_version": SCHEMA_VERSION,
        "adapter_mode": ADAPTER_MODE,
        "decision": "VALIDATED_RESEARCH_STATUS_AVAILABLE_FOR_HUMAN_EXPLANATION_ONLY",
        "source": {
            "source_review_commit": SOURCE_REVIEW_COMMIT,
            "contract_root_sha256": SOURCE_CONTRACT_ROOT_SHA256,
            "snapshot_sha256": SOURCE_SNAPSHOT_SHA256,
            "manifest_sha256": SOURCE_MANIFEST_SHA256,
            "snapshot_size_bytes": SOURCE_SNAPSHOT_SIZE_BYTES,
        },
        "research_status": {
            "legacy_short_candidate": "REVALIDATED_REJECTED",
            "short_recovery_line": "CLOSED_ALL_VARIANTS_REJECTED",
            "short_recovery_surviving_variant_count": 0,
            "long_primary_candidate": (
                "RESEARCH_ONLY_CERTIFIED_UNAFFECTED_AND_CONSISTENCY_REVALIDATED"
            ),
            "long_secondary_candidate": (
                "WATCHLIST_ONLY_CERTIFIED_UNAFFECTED_AND_CONSISTENCY_REVALIDATED"
            ),
            "long_official_evidence_row_count": 0,
            "retrospective_lockbox": "SEALED",
            "prospective_holdout": "SEALED",
            "total_project_completed": False,
        },
        "restrictions": {
            "human_explanation_only": True,
            "actionable_trading_fields_present": False,
            "openclaw_runtime_status_consumption_allowed": False,
            "openclaw_tool_invocation_allowed": False,
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
        "next_routes": {
            "adapter_track": RECOMMENDED_NEXT_PHASE,
            "long_dataset_track": PHASE_10_43_ROUTE,
            "route_independence": True,
        },
    }


def build_adapter_design() -> dict[str, Any]:
    design: dict[str, Any] = {
        "phase": PHASE,
        "schema_version": SCHEMA_VERSION,
        "adapter_mode": ADAPTER_MODE,
        "decision_boundary": {
            "design_only": True,
            "implementation_allowed": False,
            "runtime_integration_allowed": False,
            "tool_registration_allowed": False,
            "human_review_required": True,
            "python_source_of_truth": True,
        },
        "source_authority": {
            "source_review_commit": SOURCE_REVIEW_COMMIT,
            "source_review_module_sha256": SOURCE_REVIEW_MODULE_SHA256,
            "source_review_document_sha256": SOURCE_REVIEW_DOCUMENT_SHA256,
            "contract_root_sha256": SOURCE_CONTRACT_ROOT_SHA256,
            "snapshot_sha256": SOURCE_SNAPSHOT_SHA256,
            "manifest_sha256": SOURCE_MANIFEST_SHA256,
            "snapshot_size_bytes": SOURCE_SNAPSHOT_SIZE_BYTES,
        },
        "request_contract": {
            "exact_fields": list(REQUEST_FIELDS),
            "operation": ALLOWED_OPERATION,
            "response_profile": ALLOWED_RESPONSE_PROFILE,
            "require_human_review": True,
            "allow_actionable_fields": False,
            "additional_fields_allowed": False,
        },
        "response_contract": {
            "exact_top_level_fields": list(RESPONSE_FIELDS),
            "additional_top_level_fields_allowed": False,
            "forbidden_actionable_fields": list(FORBIDDEN_ACTIONABLE_FIELDS),
            "actionable_trading_content_allowed": False,
            "human_explanation_only": True,
        },
        "validation_sequence": list(VALIDATION_SEQUENCE),
        "read_boundary": copy.deepcopy(READ_BOUNDARY),
        "write_boundary": copy.deepcopy(WRITE_BOUNDARY),
        "transport_boundary": copy.deepcopy(TRANSPORT_BOUNDARY),
        "operational_permissions": copy.deepcopy(OPERATIONAL_PERMISSIONS),
        "error_registry": dict(ERROR_REGISTRY),
        "exit_code_contract": {
            "success": 0,
            "invalid_request_range": [20, 21],
            "integrity_failure_range": [22, 24],
            "response_boundary_range": [25, 28],
            "internal_fail_closed": 70,
            "nonzero_on_any_failure": True,
        },
        "sample_request": sample_request(),
        "sample_response": sample_response(),
        "next_routes": {
            "adapter_track": RECOMMENDED_NEXT_PHASE,
            "long_dataset_track": PHASE_10_43_ROUTE,
            "route_independence": True,
            "phase_10_43_design_review_allowed": True,
            "runtime_integration_allowed": False,
        },
        "total_project_completed": False,
    }
    design["design_root_sha256"] = calculate_design_root(design)
    return design


def _walk_keys(value: object) -> set[str]:
    keys: set[str] = set()
    if isinstance(value, Mapping):
        for key, child in value.items():
            keys.add(str(key))
            keys.update(_walk_keys(child))
    elif isinstance(value, list):
        for child in value:
            keys.update(_walk_keys(child))
    return keys


def validate_request(request: Mapping[str, Any]) -> None:
    _require(set(request) == set(REQUEST_FIELDS), "Request fields mismatch")
    _require(request.get("operation") == ALLOWED_OPERATION, "Unsupported operation")
    _require(
        request.get("response_profile") == ALLOWED_RESPONSE_PROFILE,
        "Unsupported response profile",
    )
    _require(request.get("require_human_review") is True, "Human review is required")
    _require(
        request.get("allow_actionable_fields") is False,
        "Actionable fields must remain prohibited",
    )


def validate_response(response: Mapping[str, Any]) -> None:
    _require(set(response) == set(RESPONSE_FIELDS), "Response fields mismatch")
    _require(response.get("adapter_schema_version") == SCHEMA_VERSION, "Schema mismatch")
    _require(response.get("adapter_mode") == ADAPTER_MODE, "Adapter mode mismatch")
    keys = {key.lower() for key in _walk_keys(response)}
    _require(
        not keys.intersection(FORBIDDEN_ACTIONABLE_FIELDS),
        "Actionable trading field present",
    )
    restrictions = response.get("restrictions")
    _require(isinstance(restrictions, Mapping), "Restrictions must be an object")
    _require(restrictions.get("human_explanation_only") is True, "Explanation boundary")
    _require(
        restrictions.get("actionable_trading_fields_present") is False,
        "Actionable content declared",
    )
    for field in (
        "openclaw_runtime_status_consumption_allowed",
        "openclaw_tool_invocation_allowed",
        "openclaw_operational_integration_allowed",
        "signal_generation_enabled",
        "paper_trade_execution_allowed",
        "real_capital_allowed",
        "market_execution_allowed",
        "automation_allowed",
    ):
        _require(restrictions.get(field) is False, f"Prohibited response flag enabled: {field}")
    human = response.get("human_review")
    _require(isinstance(human, Mapping), "Human-review object missing")
    _require(human.get("required") is True, "Human review must remain required")
    _require(human.get("permission_override_allowed") is False, "Permission override enabled")
    _require(
        human.get("unknown_status_inference_allowed") is False,
        "Unknown status inference enabled",
    )


def validate_adapter_design(design: Mapping[str, Any]) -> None:
    expected_top = {
        "phase",
        "schema_version",
        "adapter_mode",
        "decision_boundary",
        "source_authority",
        "request_contract",
        "response_contract",
        "validation_sequence",
        "read_boundary",
        "write_boundary",
        "transport_boundary",
        "operational_permissions",
        "error_registry",
        "exit_code_contract",
        "sample_request",
        "sample_response",
        "next_routes",
        "total_project_completed",
        "design_root_sha256",
    }
    _require(set(design) == expected_top, "Design top-level fields mismatch")
    _require(design.get("phase") == PHASE, "Phase mismatch")
    _require(design.get("schema_version") == SCHEMA_VERSION, "Schema version mismatch")
    _require(design.get("adapter_mode") == ADAPTER_MODE, "Adapter mode mismatch")
    boundary = design["decision_boundary"]
    _require(boundary["design_only"] is True, "Design-only boundary missing")
    _require(boundary["implementation_allowed"] is False, "Implementation enabled")
    _require(boundary["runtime_integration_allowed"] is False, "Runtime enabled")
    _require(boundary["tool_registration_allowed"] is False, "Tool registration enabled")
    _require(boundary["human_review_required"] is True, "Human review disabled")
    _require(boundary["python_source_of_truth"] is True, "Python authority disabled")
    _require(
        design["source_authority"]["source_review_commit"] == SOURCE_REVIEW_COMMIT,
        "Source review commit mismatch",
    )
    _require(
        design["source_authority"]["contract_root_sha256"]
        == SOURCE_CONTRACT_ROOT_SHA256,
        "Contract root source mismatch",
    )
    _require(tuple(design["validation_sequence"]) == VALIDATION_SEQUENCE, "Sequence mismatch")
    _require(design["read_boundary"] == READ_BOUNDARY, "Read boundary mismatch")
    _require(design["write_boundary"] == WRITE_BOUNDARY, "Write boundary mismatch")
    _require(design["transport_boundary"] == TRANSPORT_BOUNDARY, "Transport mismatch")
    _require(
        design["operational_permissions"] == OPERATIONAL_PERMISSIONS,
        "Operational permissions mismatch",
    )
    _require(
        all(value is False for value in design["operational_permissions"].values()),
        "Operational permission enabled",
    )
    _require(design["error_registry"] == ERROR_REGISTRY, "Error registry mismatch")
    _require(len(set(ERROR_REGISTRY.values())) == len(ERROR_REGISTRY), "Duplicate exit code")
    validate_request(design["sample_request"])
    validate_response(design["sample_response"])
    routes = design["next_routes"]
    _require(routes["adapter_track"] == RECOMMENDED_NEXT_PHASE, "Next adapter route")
    _require(routes["long_dataset_track"] == PHASE_10_43_ROUTE, "10.43 route")
    _require(routes["route_independence"] is True, "Route independence")
    _require(routes["runtime_integration_allowed"] is False, "Runtime route enabled")
    _require(design["total_project_completed"] is False, "Project completion mismatch")
    _require(
        design.get("design_root_sha256") == calculate_design_root(design),
        "Design root mismatch",
    )


DESIGN_ROOT_SHA256 = calculate_design_root(build_adapter_design())


__all__ = [
    "ADAPTER_MODE",
    "ALLOWED_OPERATION",
    "ALLOWED_RESPONSE_PROFILE",
    "AdapterDesignError",
    "DESIGN_ROOT_SHA256",
    "ERROR_REGISTRY",
    "FORBIDDEN_ACTIONABLE_FIELDS",
    "OPERATIONAL_PERMISSIONS",
    "PHASE",
    "PHASE_10_43_ROUTE",
    "READ_BOUNDARY",
    "RECOMMENDED_NEXT_PHASE",
    "REQUEST_FIELDS",
    "RESPONSE_FIELDS",
    "SCHEMA_VERSION",
    "SOURCE_CONTRACT_ROOT_SHA256",
    "SOURCE_MANIFEST_SHA256",
    "SOURCE_REVIEW_COMMIT",
    "SOURCE_REVIEW_DOCUMENT_SHA256",
    "SOURCE_REVIEW_MODULE_SHA256",
    "SOURCE_SNAPSHOT_SHA256",
    "TRANSPORT_BOUNDARY",
    "VALIDATION_SEQUENCE",
    "WRITE_BOUNDARY",
    "build_adapter_design",
    "calculate_design_root",
    "canonical_json",
    "canonical_pretty_json",
    "sample_request",
    "sample_response",
    "sha256_bytes",
    "validate_adapter_design",
    "validate_request",
    "validate_response",
]
