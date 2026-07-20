from __future__ import annotations

import copy
import hashlib
import importlib
import json
import re
import subprocess
from pathlib import Path
from typing import Any, Mapping, Sequence

PHASE = "10.42R.7"
REVIEW_SCHEMA_VERSION = (
    "OPENCLAW_READ_ONLY_RESEARCH_STATUS_LOCAL_CONSUMER_ADAPTER_DESIGN_REVIEW_V1"
)
SOURCE_DESIGN_COMMIT = "45d22e5dc242fd0f475135182c32b37b2c4d4a4c"
SOURCE_MANIFEST_PATH = Path("PHASE_10_42R_6_MANIFEST.sha256")
SOURCE_DOCUMENT_PATH = Path(
    "docs/PHASE_10_42R_6_OPENCLAW_READ_ONLY_RESEARCH_STATUS_LOCAL_CONSUMER_ADAPTER_DESIGN.md"
)
SOURCE_SCHEMA_PATH = Path(
    "schemas/openclaw_read_only_research_status_local_consumer_adapter_design_v1.schema.json"
)
SOURCE_MODULE_PATH = Path(
    "src/integration/openclaw_read_only_research_status_local_consumer_adapter_design_v1.py"
)
SOURCE_VALIDATION_PATH = Path(
    "src/validation/phase_10_42r_6_openclaw_read_only_research_status_local_consumer_adapter_design_v1.py"
)
SOURCE_WORKFLOW_PATH = Path(
    "src/workflows/validate_phase_10_42r_6_openclaw_read_only_research_status_local_consumer_adapter_design.py"
)
SOURCE_TEST_PATH = Path(
    "tests/test_phase_10_42r_6_openclaw_read_only_research_status_local_consumer_adapter_design.py"
)
SOURCE_HASHES = {
    SOURCE_DOCUMENT_PATH.as_posix(): "29d413174fa69dbec0d9f9fc5d7f4e60162d99dcd0da3d7a6267dadf6d8db299",
    SOURCE_SCHEMA_PATH.as_posix(): "598449d371b6d98588538e6b5d7e688652f3f3a3076c52cc8a424f5d52709a13",
    SOURCE_MODULE_PATH.as_posix(): "aff37711a09922f890bb70b8391b29ca0be7f20718c8fa3c70edd3e08273b077",
    SOURCE_VALIDATION_PATH.as_posix(): "f86a107399ef8051eab77d80faa39a66fe20838f15e27a778f084e7b90711fc5",
    SOURCE_WORKFLOW_PATH.as_posix(): "fd35f5af80803e7aeda426304309fbd7ad24e45387e1c13165e43c0a1a4468aa",
    SOURCE_TEST_PATH.as_posix(): "dea37f133573b9bc0aa4b762c058096d639cb2ec2488d87b26a5ab279d1082e7",
}
SOURCE_DESIGN_ROOT_SHA256 = "b7336e60c705841f3ff313016816d9115fb46485d67d3a016d0206ab43d89e21"
SOURCE_CONTRACT_ROOT_SHA256 = "ba84140879bac8a897505bd55e12d3c117354caf1a5a5ad4f6c3eb003bd6fa46"
SOURCE_SNAPSHOT_SHA256 = "72a77f3a726d38f0008378218958a5ea8ee8fb0162477692a7370dcf9af43e88"
SOURCE_EXPORT_MANIFEST_SHA256 = "f829010549a79fb3eb35b38ce51736f730020747d6fc77b7fa56eac5ade6a5f7"
SOURCE_SNAPSHOT_SIZE_BYTES = 5965
SOURCE_REVIEW_COMMIT = "7e6d180f0cee72437e086eff0b0596a64f22ea78"
SOURCE_REVIEW_MODULE_SHA256 = "138181a806f9c0f4d7045cce27c48e9b976de94a44da27824c9548cd9862a89b"
SOURCE_REVIEW_DOCUMENT_SHA256 = "365b254e7814c8d238aa2f04dd9a45d9c99d35f8bb82dd0011b9f1374e9a269b"
SOURCE_DESIGN_SCHEMA_VERSION = (
    "OPENCLAW_READ_ONLY_RESEARCH_STATUS_LOCAL_CONSUMER_ADAPTER_DESIGN_V1"
)
SOURCE_ADAPTER_MODE = "DESIGN_ONLY_LOCAL_READ_ONLY_NO_RUNTIME_INTEGRATION"
ALLOWED_OPERATION = "GET_VALIDATED_RESEARCH_STATUS"
ALLOWED_RESPONSE_PROFILE = "HUMAN_EXPLANATION_ONLY"
PHASE_10_43_ROUTE = (
    "PHASE_10_43_LONG_FORWARD_OBSERVATION_EVIDENCE_COLLECTION_"
    "OFFICIAL_DATASET_ATOMIC_WRITE_HARNESS_DESIGN_REVIEW_V1"
)
SOURCE_RECOMMENDED_ROUTE = (
    "PHASE_10_42R_7_OPENCLAW_READ_ONLY_RESEARCH_STATUS_"
    "LOCAL_CONSUMER_ADAPTER_DESIGN_REVIEW_V1"
)
RECOMMENDED_NEXT_PHASE = (
    "PHASE_10_42R_8_OPENCLAW_READ_ONLY_RESEARCH_STATUS_"
    "LOCAL_CONSUMER_ADAPTER_IMPLEMENTATION_V1"
)

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
    "allowed_directory": "reports/phase_10_42r_4/openclaw_read_only_export_v1",
    "allowed_files": [
        "openclaw_read_only_research_status_v1.json",
        "openclaw_read_only_research_status_v1.manifest.json",
    ],
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
OPERATIONAL_PERMISSION_NAMES = (
    "openclaw_runtime_status_consumption_allowed",
    "openclaw_tool_invocation_allowed",
    "openclaw_operational_integration_allowed",
    "historical_evaluation_allowed",
    "backtest_execution_allowed",
    "performance_metric_recalculation_allowed",
    "candidate_comparison_allowed",
    "candidate_ranking_allowed",
    "winner_selection_allowed",
    "candidate_mutation_allowed",
    "retrospective_lockbox_access_allowed",
    "prospective_holdout_access_allowed",
    "forward_observation_start_allowed",
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
)


class AdapterDesignReviewError(RuntimeError):
    """Raised when the frozen adapter design violates the independent review."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise AdapterDesignReviewError(message)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def normalized_text_bytes(path: Path) -> bytes:
    raw = path.read_bytes()
    if raw.startswith(b"\xef\xbb\xbf"):
        raw = raw[3:]
    return raw.replace(b"\r\n", b"\n").replace(b"\r", b"\n")


def normalized_text_sha256(path: Path) -> str:
    return sha256_bytes(normalized_text_bytes(path))


def canonical_json_bytes(value: object) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode("utf-8")


def independent_design_root(design: Mapping[str, Any]) -> str:
    material = copy.deepcopy(dict(design))
    material.pop("design_root_sha256", None)
    return sha256_bytes(canonical_json_bytes(material))


def _walk_keys(value: object) -> set[str]:
    result: set[str] = set()
    if isinstance(value, Mapping):
        for key, child in value.items():
            result.add(str(key).lower())
            result.update(_walk_keys(child))
    elif isinstance(value, list):
        for child in value:
            result.update(_walk_keys(child))
    return result


def review_request_value(request: Mapping[str, Any]) -> None:
    _require(tuple(request.keys()) == REQUEST_FIELDS, "Request field order or shape mismatch")
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


def review_response_value(response: Mapping[str, Any]) -> None:
    _require(tuple(response.keys()) == RESPONSE_FIELDS, "Response shape mismatch")
    _require(
        response.get("adapter_schema_version") == SOURCE_DESIGN_SCHEMA_VERSION,
        "Response schema mismatch",
    )
    _require(response.get("adapter_mode") == SOURCE_ADAPTER_MODE, "Response mode mismatch")
    _require(
        not _walk_keys(response).intersection(FORBIDDEN_ACTIONABLE_FIELDS),
        "Actionable response field present",
    )
    restrictions = response.get("restrictions")
    _require(isinstance(restrictions, Mapping), "Restrictions object missing")
    _require(restrictions.get("human_explanation_only") is True, "Explanation-only boundary missing")
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
    _require(human.get("required") is True, "Human review disabled")
    _require(human.get("permission_override_allowed") is False, "Permission override enabled")
    _require(
        human.get("unknown_status_inference_allowed") is False,
        "Unknown-status inference enabled",
    )


def review_design_value(design: Mapping[str, Any]) -> dict[str, Any]:
    expected_top = {
        "phase", "schema_version", "adapter_mode", "decision_boundary",
        "source_authority", "request_contract", "response_contract",
        "validation_sequence", "read_boundary", "write_boundary",
        "transport_boundary", "operational_permissions", "error_registry",
        "exit_code_contract", "sample_request", "sample_response",
        "next_routes", "total_project_completed", "design_root_sha256",
    }
    _require(set(design) == expected_top, "Design top-level fields mismatch")
    _require(design.get("phase") == "10.42R.6", "Source phase mismatch")
    _require(design.get("schema_version") == SOURCE_DESIGN_SCHEMA_VERSION, "Schema mismatch")
    _require(design.get("adapter_mode") == SOURCE_ADAPTER_MODE, "Adapter mode mismatch")

    boundary = design.get("decision_boundary")
    _require(isinstance(boundary, Mapping), "Decision boundary missing")
    _require(boundary == {
        "design_only": True,
        "implementation_allowed": False,
        "runtime_integration_allowed": False,
        "tool_registration_allowed": False,
        "human_review_required": True,
        "python_source_of_truth": True,
    }, "Decision boundary mismatch")

    authority = design.get("source_authority")
    _require(isinstance(authority, Mapping), "Source authority missing")
    _require(authority == {
        "source_review_commit": SOURCE_REVIEW_COMMIT,
        "source_review_module_sha256": SOURCE_REVIEW_MODULE_SHA256,
        "source_review_document_sha256": SOURCE_REVIEW_DOCUMENT_SHA256,
        "contract_root_sha256": SOURCE_CONTRACT_ROOT_SHA256,
        "snapshot_sha256": SOURCE_SNAPSHOT_SHA256,
        "manifest_sha256": SOURCE_EXPORT_MANIFEST_SHA256,
        "snapshot_size_bytes": SOURCE_SNAPSHOT_SIZE_BYTES,
    }, "Source authority mismatch")

    request_contract = design.get("request_contract")
    _require(isinstance(request_contract, Mapping), "Request contract missing")
    _require(request_contract == {
        "exact_fields": list(REQUEST_FIELDS),
        "operation": ALLOWED_OPERATION,
        "response_profile": ALLOWED_RESPONSE_PROFILE,
        "require_human_review": True,
        "allow_actionable_fields": False,
        "additional_fields_allowed": False,
    }, "Request contract mismatch")

    response_contract = design.get("response_contract")
    _require(isinstance(response_contract, Mapping), "Response contract missing")
    _require(response_contract.get("exact_top_level_fields") == list(RESPONSE_FIELDS), "Response fields mismatch")
    _require(response_contract.get("additional_top_level_fields_allowed") is False, "Extra response fields enabled")
    _require(response_contract.get("forbidden_actionable_fields") == list(FORBIDDEN_ACTIONABLE_FIELDS), "Forbidden field registry mismatch")
    _require(response_contract.get("actionable_trading_content_allowed") is False, "Actionable content enabled")
    _require(response_contract.get("human_explanation_only") is True, "Human explanation boundary missing")

    _require(tuple(design.get("validation_sequence", ())) == VALIDATION_SEQUENCE, "Validation sequence mismatch")
    _require(design.get("read_boundary") == READ_BOUNDARY, "Read boundary mismatch")
    _require(design.get("write_boundary") == WRITE_BOUNDARY, "Write boundary mismatch")
    _require(design.get("transport_boundary") == TRANSPORT_BOUNDARY, "Transport boundary mismatch")

    permissions = design.get("operational_permissions")
    _require(isinstance(permissions, Mapping), "Operational permissions missing")
    _require(tuple(permissions.keys()) == OPERATIONAL_PERMISSION_NAMES, "Operational permission registry mismatch")
    _require(all(value is False for value in permissions.values()), "Operational permission enabled")

    _require(design.get("error_registry") == ERROR_REGISTRY, "Error registry mismatch")
    codes = list(ERROR_REGISTRY.values())
    _require(all(isinstance(code, int) and code > 0 for code in codes), "Invalid failure code")
    _require(len(codes) == len(set(codes)), "Duplicate failure code")
    _require(design.get("exit_code_contract") == {
        "success": 0,
        "invalid_request_range": [20, 21],
        "integrity_failure_range": [22, 24],
        "response_boundary_range": [25, 28],
        "internal_fail_closed": 70,
        "nonzero_on_any_failure": True,
    }, "Exit-code contract mismatch")

    review_request_value(design["sample_request"])
    review_response_value(design["sample_response"])

    routes = design.get("next_routes")
    _require(isinstance(routes, Mapping), "Next routes missing")
    _require(routes == {
        "adapter_track": SOURCE_RECOMMENDED_ROUTE,
        "long_dataset_track": PHASE_10_43_ROUTE,
        "route_independence": True,
        "phase_10_43_design_review_allowed": True,
        "runtime_integration_allowed": False,
    }, "Route contract mismatch")
    _require(design.get("total_project_completed") is False, "Project completion enabled")
    _require(design.get("design_root_sha256") == SOURCE_DESIGN_ROOT_SHA256, "Design root value mismatch")
    _require(independent_design_root(design) == SOURCE_DESIGN_ROOT_SHA256, "Design root reproduction failed")

    return {
        "review_passed": True,
        "design_root_sha256": SOURCE_DESIGN_ROOT_SHA256,
        "request_field_count": len(REQUEST_FIELDS),
        "response_field_count": len(RESPONSE_FIELDS),
        "validation_gate_count": len(VALIDATION_SEQUENCE),
        "error_code_count": len(ERROR_REGISTRY),
        "operational_permission_count": len(OPERATIONAL_PERMISSION_NAMES),
        "forbidden_actionable_field_count": len(FORBIDDEN_ACTIONABLE_FIELDS),
        "allowed_future_operation_count": 1,
    }


def review_schema_value(schema: Mapping[str, Any]) -> dict[str, Any]:
    required = {
        "phase", "schema_version", "adapter_mode", "decision_boundary",
        "source_authority", "request_contract", "response_contract",
        "validation_sequence", "read_boundary", "write_boundary",
        "transport_boundary", "operational_permissions", "error_registry",
        "exit_code_contract", "sample_request", "sample_response",
        "next_routes", "total_project_completed", "design_root_sha256",
    }
    _require(schema.get("type") == "object", "Schema top-level type mismatch")
    _require(schema.get("additionalProperties") is False, "Schema allows extra properties")
    _require(set(schema.get("required", [])) == required, "Schema required fields mismatch")
    properties = schema.get("properties")
    _require(isinstance(properties, Mapping), "Schema properties missing")
    _require(properties["phase"].get("const") == "10.42R.6", "Schema phase const mismatch")
    _require(properties["schema_version"].get("const") == SOURCE_DESIGN_SCHEMA_VERSION, "Schema version const mismatch")
    _require(properties["adapter_mode"].get("const") == SOURCE_ADAPTER_MODE, "Schema mode const mismatch")
    _require(properties["design_root_sha256"].get("const") == SOURCE_DESIGN_ROOT_SHA256, "Schema design root const mismatch")
    _require(properties["total_project_completed"].get("const") is False, "Schema project completion mismatch")
    decision = properties["decision_boundary"]
    _require(decision.get("additionalProperties") is False, "Decision schema allows extras")
    for key, expected in {
        "design_only": True,
        "implementation_allowed": False,
        "runtime_integration_allowed": False,
        "tool_registration_allowed": False,
        "human_review_required": True,
        "python_source_of_truth": True,
    }.items():
        _require(decision["properties"][key].get("const") is expected, f"Decision schema const mismatch: {key}")
    return {"schema_review_passed": True, "schema_required_field_count": len(required)}


def _read_manifest(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line:
            continue
        match = re.fullmatch(r"([0-9a-f]{64})  (.+)", line)
        _require(match is not None, f"Invalid manifest line: {raw}")
        digest, relative = match.groups()
        _require(relative not in values, f"Duplicate manifest path: {relative}")
        values[relative] = digest
    return values


def inspect_git_freshness(root: Path, *, require_git: bool = True) -> dict[str, Any]:
    if not (root / ".git").exists():
        _require(not require_git, "Git metadata required")
        return {
            "git_metadata_available": False,
            "current_head": "NOT_AVAILABLE",
            "source_design_commit_exists": False,
            "source_design_commit_is_ancestor": False,
            "freshness_check_skipped": True,
        }

    def run(args: Sequence[str], allow_failure: bool = False) -> subprocess.CompletedProcess[str]:
        result = subprocess.run(
            ["git", "-C", str(root), *args],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        if not allow_failure and result.returncode != 0:
            raise AdapterDesignReviewError(
                f"Git command failed: {' '.join(args)}: {result.stderr.strip()}"
            )
        return result

    head = run(["rev-parse", "HEAD"]).stdout.strip()
    exists = run(["cat-file", "-e", f"{SOURCE_DESIGN_COMMIT}^{{commit}}"], True).returncode == 0
    ancestor = exists and run(["merge-base", "--is-ancestor", SOURCE_DESIGN_COMMIT, "HEAD"], True).returncode == 0
    _require(exists, "Source design commit missing")
    _require(ancestor, "Source design commit is not an ancestor of HEAD")
    return {
        "git_metadata_available": True,
        "current_head": head,
        "source_design_commit_exists": exists,
        "source_design_commit_is_ancestor": ancestor,
        "freshness_check_skipped": False,
    }


def verify_source_authority(root: Path | str, *, require_git: bool = True) -> dict[str, Any]:
    root_path = Path(root).resolve()
    _require((root_path / SOURCE_MANIFEST_PATH).is_file(), "Missing 10.42R.6 manifest")
    manifest = _read_manifest(root_path / SOURCE_MANIFEST_PATH)
    _require(manifest == SOURCE_HASHES, "10.42R.6 manifest inventory or digest mismatch")
    for relative, expected in SOURCE_HASHES.items():
        path = root_path / relative
        _require(path.is_file(), f"Missing source file: {relative}")
        _require(normalized_text_sha256(path) == expected, f"Source hash mismatch: {relative}")
    return {
        "source_design_commit": SOURCE_DESIGN_COMMIT,
        "source_manifest_entry_count": len(manifest),
        "source_hash_count": len(SOURCE_HASHES),
        **inspect_git_freshness(root_path, require_git=require_git),
    }


def load_source_design() -> dict[str, Any]:
    module = importlib.import_module(
        "src.integration.openclaw_read_only_research_status_local_consumer_adapter_design_v1"
    )
    design = module.build_adapter_design()
    _require(isinstance(design, dict), "Source design builder did not return an object")
    return design


def review_frozen_adapter_design(
    root: Path | str = Path("."),
    *,
    require_git: bool = True,
) -> dict[str, Any]:
    root_path = Path(root).resolve()
    authority = verify_source_authority(root_path, require_git=require_git)
    design = load_source_design()
    design_review = review_design_value(design)
    schema = json.loads((root_path / SOURCE_SCHEMA_PATH).read_text(encoding="utf-8"))
    _require(isinstance(schema, dict), "Source schema must be an object")
    schema_review = review_schema_value(schema)
    return {
        "validation_passed": True,
        "review_phase": PHASE,
        "review_schema_version": REVIEW_SCHEMA_VERSION,
        **design_review,
        **schema_review,
        **authority,
        "adapter_implementation_count": 0,
        "source_export_bundle_read_count": 0,
        "simulated_consumer_read_count": 0,
        "openclaw_runtime_integration_count": 0,
        "openclaw_status_consumption_count": 0,
        "openclaw_tool_registration_count": 0,
        "openclaw_tool_invocation_count": 0,
        "service_activation_count": 0,
        "network_access_count": 0,
        "recommended_next_phase": RECOMMENDED_NEXT_PHASE,
        "phase_10_43_design_review_allowed": True,
    }


__all__ = [
    "AdapterDesignReviewError",
    "ALLOWED_OPERATION",
    "ERROR_REGISTRY",
    "FORBIDDEN_ACTIONABLE_FIELDS",
    "OPERATIONAL_PERMISSION_NAMES",
    "PHASE",
    "READ_BOUNDARY",
    "RECOMMENDED_NEXT_PHASE",
    "REQUEST_FIELDS",
    "RESPONSE_FIELDS",
    "REVIEW_SCHEMA_VERSION",
    "SOURCE_DESIGN_COMMIT",
    "SOURCE_DESIGN_ROOT_SHA256",
    "SOURCE_HASHES",
    "TRANSPORT_BOUNDARY",
    "VALIDATION_SEQUENCE",
    "WRITE_BOUNDARY",
    "independent_design_root",
    "inspect_git_freshness",
    "load_source_design",
    "normalized_text_sha256",
    "review_design_value",
    "review_frozen_adapter_design",
    "review_request_value",
    "review_response_value",
    "review_schema_value",
    "verify_source_authority",
]
