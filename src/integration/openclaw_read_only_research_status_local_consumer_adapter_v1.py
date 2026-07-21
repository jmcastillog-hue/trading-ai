from __future__ import annotations

import copy
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, BinaryIO, Mapping, Sequence, TextIO


PHASE = "10.42R.8"
IMPLEMENTATION_SCHEMA_VERSION = (
    "OPENCLAW_READ_ONLY_RESEARCH_STATUS_LOCAL_CONSUMER_ADAPTER_IMPLEMENTATION_V1"
)
IMPLEMENTATION_MODE = "LOCAL_ONE_SHOT_READ_ONLY_STDIO_NO_OPENCLAW_RUNTIME"

SOURCE_REVIEW_COMMIT = "6df6aa8aef73cd9c5118caf5acf1e723e5438d32"
SOURCE_DESIGN_COMMIT = "45d22e5dc242fd0f475135182c32b37b2c4d4a4c"
SOURCE_DESIGN_ROOT_SHA256 = (
    "b7336e60c705841f3ff313016816d9115fb46485d67d3a016d0206ab43d89e21"
)
SOURCE_CONTRACT_COMMIT = "26c14a5a1fc63fbdb5bbb61f9bbc7d3dd46656d2"
SOURCE_CONTRACT_ROOT_SHA256 = (
    "ba84140879bac8a897505bd55e12d3c117354caf1a5a5ad4f6c3eb003bd6fa46"
)
SOURCE_CONTRACT_MODULE_SHA256 = (
    "03f50b91f32af6cd421792810ba8da469faf1e35882eae8a21d176d861d770b5"
)
SOURCE_SCHEMA_SHA256 = (
    "e7e21b99d899ecd7157aa7b476ae6f379d6a01adea804271c83426b271e71289"
)
SOURCE_SNAPSHOT_SHA256 = (
    "72a77f3a726d38f0008378218958a5ea8ee8fb0162477692a7370dcf9af43e88"
)
SOURCE_MANIFEST_SHA256 = (
    "f829010549a79fb3eb35b38ce51736f730020747d6fc77b7fa56eac5ade6a5f7"
)
SOURCE_SNAPSHOT_SIZE_BYTES = 5965
DETERMINISTIC_GENERATED_AT_UTC = "2026-07-20T00:00:00+00:00"

SOURCE_BUNDLE_DIRECTORY = Path(
    "reports/phase_10_42r_4/openclaw_read_only_export_v1"
)
SNAPSHOT_FILENAME = "openclaw_read_only_research_status_v1.json"
MANIFEST_FILENAME = "openclaw_read_only_research_status_v1.manifest.json"

CONTRACT_SCHEMA_VERSION = "OPENCLAW_READ_ONLY_RESEARCH_STATUS_CONTRACT_V1"
CONTRACT_MODE = "DESIGN_ONLY_READ_ONLY_STATUS_CONTRACT"
EXPORT_SCHEMA_VERSION = "OPENCLAW_READ_ONLY_RESEARCH_STATUS_EXPORT_V1"
EXPORT_MODE = "LOCAL_FILE_EXPORT_READ_ONLY_NO_RUNTIME_CONSUMER"
ADAPTER_RESPONSE_SCHEMA_VERSION = (
    "OPENCLAW_READ_ONLY_RESEARCH_STATUS_LOCAL_CONSUMER_ADAPTER_DESIGN_V1"
)
ADAPTER_RESPONSE_MODE = "DESIGN_ONLY_LOCAL_READ_ONLY_NO_RUNTIME_INTEGRATION"

ALLOWED_OPERATION = "GET_VALIDATED_RESEARCH_STATUS"
ALLOWED_RESPONSE_PROFILE = "HUMAN_EXPLANATION_ONLY"
MAX_REQUEST_BYTES = 4096

PHASE_10_43_ROUTE = (
    "PHASE_10_43_LONG_FORWARD_OBSERVATION_EVIDENCE_COLLECTION_"
    "OFFICIAL_DATASET_ATOMIC_WRITE_HARNESS_DESIGN_REVIEW_V1"
)
RECOMMENDED_NEXT_PHASE = (
    "PHASE_10_42R_9_OPENCLAW_READ_ONLY_RESEARCH_STATUS_LOCAL_CONSUMER_"
    "ADAPTER_INDEPENDENT_IMPLEMENTATION_REVIEW_V1"
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
FORBIDDEN_ACTIONABLE_FIELDS = {
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
}

READ_ONLY_CAPABILITIES = {
    "project_status_read_allowed": True,
    "source_anchor_read_allowed": True,
    "validated_result_summary_allowed": True,
    "failed_gate_explanation_allowed": True,
    "contract_snapshot_generation_allowed": True,
    "human_review_required": True,
}
PROHIBITED_CAPABILITY_NAMES = (
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
    "openclaw_runtime_status_consumption_allowed",
    "openclaw_tool_invocation_allowed",
    "openclaw_operational_integration_allowed",
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


class AdapterFailure(RuntimeError):
    def __init__(self, error_id: str, message: str):
        if error_id not in ERROR_REGISTRY:
            error_id = "ADAPTER_E010_INTERNAL_FAIL_CLOSED"
        self.error_id = error_id
        self.exit_code = ERROR_REGISTRY[error_id]
        super().__init__(message)


def _require(condition: bool, error_id: str, message: str) -> None:
    if not condition:
        raise AdapterFailure(error_id, message)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def canonical_compact_json_bytes(value: object) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode("utf-8")


def canonical_pretty_json_bytes(value: object) -> bytes:
    return (
        json.dumps(
            value,
            sort_keys=True,
            indent=2,
            ensure_ascii=True,
            allow_nan=False,
        )
        + "\n"
    ).encode("utf-8")


def load_json_strict(
    payload: bytes,
    *,
    label: str,
    error_id: str,
) -> Any:
    _require(
        not payload.startswith(b"\xef\xbb\xbf"),
        error_id,
        f"{label} must not contain a UTF-8 BOM",
    )
    try:
        text = payload.decode("utf-8", errors="strict")
    except UnicodeDecodeError as exc:
        raise AdapterFailure(error_id, f"{label} is not strict UTF-8") from exc
    def reject_duplicate_pairs(
        pairs: list[tuple[str, Any]],
    ) -> dict[str, Any]:
        value: dict[str, Any] = {}
        for key, child in pairs:
            if key in value:
                raise AdapterFailure(
                    error_id,
                    f"Duplicate JSON field in {label}: {key}",
                )
            value[key] = child
        return value

    try:
        return json.loads(
            text,
            object_pairs_hook=reject_duplicate_pairs,
            parse_constant=lambda token: (_ for _ in ()).throw(
                ValueError(f"Non-finite JSON constant: {token}")
            ),
        )
    except AdapterFailure:
        raise
    except Exception as exc:
        raise AdapterFailure(error_id, f"{label} is not valid JSON") from exc


def parse_request_bytes(payload: bytes) -> dict[str, Any]:
    _require(
        0 < len(payload) <= MAX_REQUEST_BYTES,
        "ADAPTER_E001_INVALID_REQUEST_SHAPE",
        "Request size is outside the allowed boundary",
    )
    value = load_json_strict(
        payload,
        label="request",
        error_id="ADAPTER_E001_INVALID_REQUEST_SHAPE",
    )
    _require(
        isinstance(value, dict),
        "ADAPTER_E001_INVALID_REQUEST_SHAPE",
        "Request must be a JSON object",
    )
    validate_request(value)
    return value


def validate_request(request: Mapping[str, Any]) -> None:
    _require(
        set(request) == set(REQUEST_FIELDS),
        "ADAPTER_E001_INVALID_REQUEST_SHAPE",
        "Request fields mismatch",
    )
    _require(
        request.get("operation") == ALLOWED_OPERATION,
        "ADAPTER_E002_UNSUPPORTED_OPERATION",
        "Unsupported operation",
    )
    _require(
        request.get("response_profile") == ALLOWED_RESPONSE_PROFILE,
        "ADAPTER_E001_INVALID_REQUEST_SHAPE",
        "Unsupported response profile",
    )
    _require(
        request.get("require_human_review") is True,
        "ADAPTER_E007_HUMAN_REVIEW_REQUIREMENT_MISSING",
        "Human review is required",
    )
    _require(
        request.get("allow_actionable_fields") is False,
        "ADAPTER_E005_PERMISSION_BOUNDARY_VIOLATION",
        "Actionable fields must remain prohibited",
    )


def _run_git(
    root: Path,
    arguments: Sequence[str],
    *,
    allow_failure: bool = False,
) -> subprocess.CompletedProcess[str]:
    completed = subprocess.run(
        ["git", "-C", str(root), *arguments],
        text=True,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
        shell=False,
    )
    if not allow_failure and completed.returncode != 0:
        raise AdapterFailure(
            "ADAPTER_E003_SOURCE_AUTHORITY_FAILURE",
            f"Git source-authority check failed: {' '.join(arguments)}",
        )
    return completed


def inspect_source_freshness(
    root: Path,
    *,
    require_git: bool = True,
) -> dict[str, Any]:
    if not (root / ".git").exists():
        _require(
            not require_git,
            "ADAPTER_E003_SOURCE_AUTHORITY_FAILURE",
            "Git metadata is required",
        )
        return {
            "git_metadata_available": False,
            "current_head": "NOT_AVAILABLE",
            "source_review_commit_exists": False,
            "source_review_commit_is_ancestor": False,
            "freshness_check_skipped": True,
        }

    current_head = _run_git(root, ["rev-parse", "HEAD"]).stdout.strip()
    exists = (
        _run_git(
            root,
            ["cat-file", "-e", f"{SOURCE_REVIEW_COMMIT}^{{commit}}"],
            allow_failure=True,
        ).returncode
        == 0
    )
    ancestor = False
    if exists:
        ancestor = (
            _run_git(
                root,
                ["merge-base", "--is-ancestor", SOURCE_REVIEW_COMMIT, "HEAD"],
                allow_failure=True,
            ).returncode
            == 0
        )
    _require(
        exists,
        "ADAPTER_E008_STALE_SOURCE_BINDING",
        "Source review commit is missing",
    )
    _require(
        ancestor,
        "ADAPTER_E008_STALE_SOURCE_BINDING",
        "Source review commit is not an ancestor of HEAD",
    )
    return {
        "git_metadata_available": True,
        "current_head": current_head,
        "source_review_commit_exists": True,
        "source_review_commit_is_ancestor": True,
        "freshness_check_skipped": False,
    }


def _validate_fixed_bundle_paths(root: Path) -> tuple[Path, Path, Path]:
    _require(
        root.exists() and root.is_dir(),
        "ADAPTER_E004_EXPORT_BUNDLE_INTEGRITY_FAILURE",
        "Repository root does not exist",
    )
    _require(
        not root.is_symlink(),
        "ADAPTER_E004_EXPORT_BUNDLE_INTEGRITY_FAILURE",
        "Repository root may not be a symbolic link",
    )
    bundle_dir = root / SOURCE_BUNDLE_DIRECTORY
    _require(
        bundle_dir.exists() and bundle_dir.is_dir(),
        "ADAPTER_E004_EXPORT_BUNDLE_INTEGRITY_FAILURE",
        "Fixed export directory is missing",
    )
    _require(
        not bundle_dir.is_symlink(),
        "ADAPTER_E004_EXPORT_BUNDLE_INTEGRITY_FAILURE",
        "Export directory may not be a symbolic link",
    )
    entries = list(bundle_dir.iterdir())
    _require(
        all(path.is_file() for path in entries),
        "ADAPTER_E004_EXPORT_BUNDLE_INTEGRITY_FAILURE",
        "Export bundle may contain only regular files",
    )
    _require(
        all(not path.is_symlink() for path in entries),
        "ADAPTER_E004_EXPORT_BUNDLE_INTEGRITY_FAILURE",
        "Export bundle may not contain symbolic links",
    )
    inventory = sorted(path.name for path in entries)
    expected = sorted([SNAPSHOT_FILENAME, MANIFEST_FILENAME])
    _require(
        inventory == expected,
        "ADAPTER_E004_EXPORT_BUNDLE_INTEGRITY_FAILURE",
        f"Export bundle inventory mismatch: {inventory}",
    )
    snapshot_path = bundle_dir / SNAPSHOT_FILENAME
    manifest_path = bundle_dir / MANIFEST_FILENAME
    return bundle_dir, snapshot_path, manifest_path


def _contract_root_material(snapshot: Mapping[str, Any]) -> dict[str, Any]:
    material = copy.deepcopy(dict(snapshot))
    material.pop("contract_root_sha256", None)
    contract = material.get("contract")
    if isinstance(contract, dict):
        contract.pop("generated_at_utc", None)
    return material


def calculate_contract_root(snapshot: Mapping[str, Any]) -> str:
    return sha256_bytes(canonical_compact_json_bytes(_contract_root_material(snapshot)))


def _expected_manifest(snapshot_bytes: bytes) -> dict[str, Any]:
    return {
        "export_phase": "10.42R.4",
        "export_schema_version": EXPORT_SCHEMA_VERSION,
        "export_mode": EXPORT_MODE,
        "snapshot_filename": SNAPSHOT_FILENAME,
        "snapshot_sha256": SOURCE_SNAPSHOT_SHA256,
        "snapshot_size_bytes": SOURCE_SNAPSHOT_SIZE_BYTES,
        "source_contract_commit": SOURCE_CONTRACT_COMMIT,
        "source_contract_root_sha256": SOURCE_CONTRACT_ROOT_SHA256,
        "source_contract_module_sha256": SOURCE_CONTRACT_MODULE_SHA256,
        "source_schema_sha256": SOURCE_SCHEMA_SHA256,
        "deterministic_generated_at_utc": DETERMINISTIC_GENERATED_AT_UTC,
        "atomic_replace_used": True,
        "same_directory_temporary_file_used": True,
        "snapshot_published_before_manifest": True,
        "fail_closed_required": True,
        "human_review_required": True,
        "openclaw_runtime_status_consumption_allowed": False,
        "openclaw_tool_invocation_allowed": False,
        "openclaw_operational_integration_allowed": False,
        "official_dataset_write_allowed": False,
        "signal_generation_enabled": False,
        "paper_trade_execution_allowed": False,
        "real_capital_allowed": False,
        "market_execution_allowed": False,
        "automation_allowed": False,
        "recommended_next_phase": (
            "PHASE_10_42R_5_OPENCLAW_READ_ONLY_RESEARCH_STATUS_EXPORT_"
            "INTEGRITY_AND_CONSUMER_BOUNDARY_REVIEW_V1"
        ),
    }


def validate_export_bundle(
    root: Path | str = Path("."),
    *,
    require_git: bool = True,
) -> dict[str, Any]:
    root_path = Path(root).resolve()
    freshness = inspect_source_freshness(root_path, require_git=require_git)
    bundle_dir, snapshot_path, manifest_path = _validate_fixed_bundle_paths(root_path)

    snapshot_bytes = snapshot_path.read_bytes()
    manifest_bytes = manifest_path.read_bytes()

    _require(
        len(snapshot_bytes) == SOURCE_SNAPSHOT_SIZE_BYTES,
        "ADAPTER_E004_EXPORT_BUNDLE_INTEGRITY_FAILURE",
        "Snapshot size mismatch",
    )
    _require(
        sha256_bytes(snapshot_bytes) == SOURCE_SNAPSHOT_SHA256,
        "ADAPTER_E004_EXPORT_BUNDLE_INTEGRITY_FAILURE",
        "Snapshot hash mismatch",
    )
    _require(
        sha256_bytes(manifest_bytes) == SOURCE_MANIFEST_SHA256,
        "ADAPTER_E004_EXPORT_BUNDLE_INTEGRITY_FAILURE",
        "Manifest hash mismatch",
    )

    snapshot = load_json_strict(
        snapshot_bytes,
        label="snapshot",
        error_id="ADAPTER_E004_EXPORT_BUNDLE_INTEGRITY_FAILURE",
    )
    manifest = load_json_strict(
        manifest_bytes,
        label="manifest",
        error_id="ADAPTER_E004_EXPORT_BUNDLE_INTEGRITY_FAILURE",
    )
    _require(
        isinstance(snapshot, dict) and isinstance(manifest, dict),
        "ADAPTER_E004_EXPORT_BUNDLE_INTEGRITY_FAILURE",
        "Snapshot and manifest must be objects",
    )
    _require(
        canonical_pretty_json_bytes(snapshot) == snapshot_bytes,
        "ADAPTER_E004_EXPORT_BUNDLE_INTEGRITY_FAILURE",
        "Snapshot bytes are not canonical",
    )
    _require(
        canonical_pretty_json_bytes(manifest) == manifest_bytes,
        "ADAPTER_E004_EXPORT_BUNDLE_INTEGRITY_FAILURE",
        "Manifest bytes are not canonical",
    )
    _require(
        manifest == _expected_manifest(snapshot_bytes),
        "ADAPTER_E004_EXPORT_BUNDLE_INTEGRITY_FAILURE",
        "Manifest semantic content mismatch",
    )

    expected_top = {
        "contract",
        "source_anchors",
        "master_disposition",
        "evidence_summary",
        "permissions",
        "openclaw_policy",
        "next_routes",
        "contract_root_sha256",
    }
    _require(
        set(snapshot) == expected_top,
        "ADAPTER_E004_EXPORT_BUNDLE_INTEGRITY_FAILURE",
        "Snapshot top-level fields mismatch",
    )
    contract = snapshot.get("contract")
    _require(
        isinstance(contract, dict),
        "ADAPTER_E004_EXPORT_BUNDLE_INTEGRITY_FAILURE",
        "Contract object is missing",
    )
    _require(
        contract.get("phase") == "10.42R.3",
        "ADAPTER_E004_EXPORT_BUNDLE_INTEGRITY_FAILURE",
        "Contract phase mismatch",
    )
    _require(
        contract.get("schema_version") == CONTRACT_SCHEMA_VERSION,
        "ADAPTER_E004_EXPORT_BUNDLE_INTEGRITY_FAILURE",
        "Contract schema mismatch",
    )
    _require(
        contract.get("mode") == CONTRACT_MODE,
        "ADAPTER_E004_EXPORT_BUNDLE_INTEGRITY_FAILURE",
        "Contract mode mismatch",
    )
    _require(
        snapshot.get("contract_root_sha256") == SOURCE_CONTRACT_ROOT_SHA256,
        "ADAPTER_E004_EXPORT_BUNDLE_INTEGRITY_FAILURE",
        "Contract root value mismatch",
    )
    _require(
        calculate_contract_root(snapshot) == SOURCE_CONTRACT_ROOT_SHA256,
        "ADAPTER_E004_EXPORT_BUNDLE_INTEGRITY_FAILURE",
        "Contract root cannot be reproduced",
    )

    permissions = snapshot.get("permissions")
    _require(
        isinstance(permissions, dict),
        "ADAPTER_E005_PERMISSION_BOUNDARY_VIOLATION",
        "Permissions object is missing",
    )
    read_only = permissions.get("read_only_capabilities")
    prohibited = permissions.get("prohibited_capabilities")
    _require(
        read_only == READ_ONLY_CAPABILITIES,
        "ADAPTER_E005_PERMISSION_BOUNDARY_VIOLATION",
        "Read-only capability set mismatch",
    )
    _require(
        isinstance(prohibited, dict)
        and set(prohibited) == set(PROHIBITED_CAPABILITY_NAMES)
        and all(prohibited[name] is False for name in PROHIBITED_CAPABILITY_NAMES),
        "ADAPTER_E005_PERMISSION_BOUNDARY_VIOLATION",
        "A prohibited capability is enabled or missing",
    )

    policy = snapshot.get("openclaw_policy")
    _require(
        isinstance(policy, dict),
        "ADAPTER_E005_PERMISSION_BOUNDARY_VIOLATION",
        "OpenClaw policy object is missing",
    )
    _require(
        policy.get("required_failure_mode") == "FAIL_CLOSED",
        "ADAPTER_E005_PERMISSION_BOUNDARY_VIOLATION",
        "Failure mode mismatch",
    )
    _require(
        policy.get("human_decision_required") is True,
        "ADAPTER_E007_HUMAN_REVIEW_REQUIREMENT_MISSING",
        "Human review is not required by the snapshot",
    )
    _require(
        policy.get("permission_override_allowed") is False
        and policy.get("unknown_status_inference_allowed") is False,
        "ADAPTER_E005_PERMISSION_BOUNDARY_VIOLATION",
        "Permission override or status inference is enabled",
    )
    _require(
        policy.get("runtime_integration_status") == "NOT_IMPLEMENTED",
        "ADAPTER_E009_RUNTIME_INTEGRATION_PROHIBITED",
        "OpenClaw runtime integration is not prohibited",
    )

    return {
        "root": root_path,
        "bundle_directory": bundle_dir,
        "snapshot": snapshot,
        "manifest": manifest,
        "snapshot_sha256": SOURCE_SNAPSHOT_SHA256,
        "manifest_sha256": SOURCE_MANIFEST_SHA256,
        "contract_root_sha256": SOURCE_CONTRACT_ROOT_SHA256,
        **freshness,
    }


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


def build_allowlisted_response(
    snapshot: Mapping[str, Any],
) -> dict[str, Any]:
    disposition = snapshot["master_disposition"]
    evidence = snapshot["evidence_summary"]
    return {
        "adapter_schema_version": ADAPTER_RESPONSE_SCHEMA_VERSION,
        "adapter_mode": ADAPTER_RESPONSE_MODE,
        "decision": (
            "VALIDATED_RESEARCH_STATUS_AVAILABLE_FOR_HUMAN_EXPLANATION_ONLY"
        ),
        "source": {
            "source_review_commit": SOURCE_REVIEW_COMMIT,
            "contract_root_sha256": SOURCE_CONTRACT_ROOT_SHA256,
            "snapshot_sha256": SOURCE_SNAPSHOT_SHA256,
            "manifest_sha256": SOURCE_MANIFEST_SHA256,
            "snapshot_size_bytes": SOURCE_SNAPSHOT_SIZE_BYTES,
        },
        "research_status": {
            "legacy_short_candidate": disposition["legacy_short_candidate"],
            "short_recovery_line": disposition["short_recovery_line"],
            "short_recovery_surviving_variant_count": evidence[
                "short_recovery_surviving_variant_count"
            ],
            "long_primary_candidate": disposition["long_primary_candidate"],
            "long_secondary_candidate": disposition["long_secondary_candidate"],
            "long_official_evidence_row_count": evidence[
                "long_official_evidence_row_count"
            ],
            "retrospective_lockbox": disposition["retrospective_lockbox"],
            "prospective_holdout": disposition["prospective_holdout"],
            "total_project_completed": disposition["total_project_completed"],
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


def validate_response(response: Mapping[str, Any]) -> None:
    _require(
        set(response) == set(RESPONSE_FIELDS),
        "ADAPTER_E006_RESPONSE_ALLOWLIST_VIOLATION",
        "Response fields mismatch",
    )
    _require(
        response.get("adapter_schema_version") == ADAPTER_RESPONSE_SCHEMA_VERSION,
        "ADAPTER_E006_RESPONSE_ALLOWLIST_VIOLATION",
        "Response schema mismatch",
    )
    _require(
        response.get("adapter_mode") == ADAPTER_RESPONSE_MODE,
        "ADAPTER_E006_RESPONSE_ALLOWLIST_VIOLATION",
        "Response contract mode mismatch",
    )
    keys = _walk_keys(response)
    _require(
        not keys.intersection(FORBIDDEN_ACTIONABLE_FIELDS),
        "ADAPTER_E006_RESPONSE_ALLOWLIST_VIOLATION",
        "Actionable trading field is present",
    )
    restrictions = response.get("restrictions")
    _require(
        isinstance(restrictions, Mapping)
        and restrictions.get("human_explanation_only") is True
        and restrictions.get("actionable_trading_fields_present") is False,
        "ADAPTER_E006_RESPONSE_ALLOWLIST_VIOLATION",
        "Response explanation boundary mismatch",
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
        _require(
            restrictions.get(field) is False,
            "ADAPTER_E006_RESPONSE_ALLOWLIST_VIOLATION",
            f"Prohibited response flag enabled: {field}",
        )
    human = response.get("human_review")
    _require(
        isinstance(human, Mapping)
        and human.get("required") is True
        and human.get("permission_override_allowed") is False
        and human.get("unknown_status_inference_allowed") is False,
        "ADAPTER_E007_HUMAN_REVIEW_REQUIREMENT_MISSING",
        "Human-review response boundary mismatch",
    )


def consume_request(
    request: Mapping[str, Any],
    *,
    root: Path | str = Path("."),
    require_git: bool = True,
) -> dict[str, Any]:
    validate_request(request)
    reviewed = validate_export_bundle(root, require_git=require_git)
    response = build_allowlisted_response(reviewed["snapshot"])
    validate_response(response)
    return response


def _failure_payload(exc: AdapterFailure) -> dict[str, Any]:
    return {
        "error_id": exc.error_id,
        "exit_code": exc.exit_code,
        "failure_mode": "FAIL_CLOSED",
        "message": str(exc),
        "partial_response_emitted": False,
    }


def run_stdio_adapter(
    *,
    stdin: BinaryIO | None = None,
    stdout: BinaryIO | None = None,
    stderr: TextIO | None = None,
    root: Path | str = Path("."),
    require_git: bool = True,
) -> int:
    input_stream = stdin if stdin is not None else sys.stdin.buffer
    output_stream = stdout if stdout is not None else sys.stdout.buffer
    error_stream = stderr if stderr is not None else sys.stderr
    try:
        payload = input_stream.read(MAX_REQUEST_BYTES + 1)
        request = parse_request_bytes(payload)
        response = consume_request(
            request,
            root=root,
            require_git=require_git,
        )
        output_stream.write(canonical_pretty_json_bytes(response))
        output_stream.flush()
        return 0
    except AdapterFailure as exc:
        error_stream.write(
            canonical_compact_json_bytes(_failure_payload(exc)).decode("ascii")
            + "\n"
        )
        error_stream.flush()
        return exc.exit_code
    except Exception as exc:  # pragma: no cover - emergency fail-closed boundary
        failure = AdapterFailure(
            "ADAPTER_E010_INTERNAL_FAIL_CLOSED",
            f"Internal fail-closed error: {type(exc).__name__}",
        )
        error_stream.write(
            canonical_compact_json_bytes(_failure_payload(failure)).decode("ascii")
            + "\n"
        )
        error_stream.flush()
        return failure.exit_code


__all__ = [
    "ADAPTER_RESPONSE_MODE",
    "ADAPTER_RESPONSE_SCHEMA_VERSION",
    "ALLOWED_OPERATION",
    "ALLOWED_RESPONSE_PROFILE",
    "AdapterFailure",
    "ERROR_REGISTRY",
    "FORBIDDEN_ACTIONABLE_FIELDS",
    "IMPLEMENTATION_MODE",
    "IMPLEMENTATION_SCHEMA_VERSION",
    "MANIFEST_FILENAME",
    "MAX_REQUEST_BYTES",
    "PHASE",
    "PROHIBITED_CAPABILITY_NAMES",
    "RECOMMENDED_NEXT_PHASE",
    "REQUEST_FIELDS",
    "RESPONSE_FIELDS",
    "SNAPSHOT_FILENAME",
    "SOURCE_BUNDLE_DIRECTORY",
    "SOURCE_CONTRACT_ROOT_SHA256",
    "SOURCE_DESIGN_ROOT_SHA256",
    "SOURCE_MANIFEST_SHA256",
    "SOURCE_REVIEW_COMMIT",
    "SOURCE_SNAPSHOT_SHA256",
    "SOURCE_SNAPSHOT_SIZE_BYTES",
    "build_allowlisted_response",
    "calculate_contract_root",
    "canonical_compact_json_bytes",
    "canonical_pretty_json_bytes",
    "consume_request",
    "inspect_source_freshness",
    "load_json_strict",
    "parse_request_bytes",
    "run_stdio_adapter",
    "sha256_bytes",
    "validate_export_bundle",
    "validate_request",
    "validate_response",
]
