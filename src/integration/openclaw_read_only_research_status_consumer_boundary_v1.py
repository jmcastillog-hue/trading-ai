from __future__ import annotations

import copy
import hashlib
import json
import re
import subprocess
from pathlib import Path
from typing import Any, Mapping, Sequence


PHASE = "10.42R.5"
REVIEW_SCHEMA_VERSION = (
    "OPENCLAW_READ_ONLY_RESEARCH_STATUS_EXPORT_INTEGRITY_"
    "AND_CONSUMER_BOUNDARY_REVIEW_V1"
)
SOURCE_EXPORT_COMMIT = "a371b3682f2e1f99a8b75c3124ee855b05cd5319"
SOURCE_EXPORT_MODULE_PATH = Path(
    "src/integration/openclaw_read_only_research_status_export_v1.py"
)
SOURCE_EXPORT_DOCUMENT_PATH = Path(
    "docs/PHASE_10_42R_4_OPENCLAW_READ_ONLY_RESEARCH_STATUS_EXPORT_IMPLEMENTATION.md"
)
SOURCE_EXPORT_MANIFEST_PATH = Path("PHASE_10_42R_4_MANIFEST.sha256")
SOURCE_EXPORT_MODULE_SHA256 = (
    "a4b2a81ee104441b71dad2da5d49f7a81a6b0ccea69bcc0a5e78980fe4020cb2"
)
SOURCE_EXPORT_DOCUMENT_SHA256 = (
    "3f9353498510297076d338a2115a111365da1d1fde8fd0044394993233a0de3b"
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
SOURCE_BUNDLE_DIR = Path(
    "reports/phase_10_42r_4/openclaw_read_only_export_v1"
)
SNAPSHOT_FILENAME = "openclaw_read_only_research_status_v1.json"
MANIFEST_FILENAME = "openclaw_read_only_research_status_v1.manifest.json"
NEXT_PHASE = (
    "PHASE_10_42R_6_OPENCLAW_READ_ONLY_RESEARCH_STATUS_"
    "LOCAL_CONSUMER_ADAPTER_DESIGN_V1"
)
PHASE_10_43_ROUTE = (
    "PHASE_10_43_LONG_FORWARD_OBSERVATION_EVIDENCE_COLLECTION_"
    "OFFICIAL_DATASET_ATOMIC_WRITE_HARNESS_DESIGN_REVIEW_V1"
)

READ_ONLY_CAPABILITIES = {
    "project_status_read_allowed": True,
    "source_anchor_read_allowed": True,
    "validated_result_summary_allowed": True,
    "failed_gate_explanation_allowed": True,
    "contract_snapshot_generation_allowed": True,
    "human_review_required": True,
}

PROHIBITED_CAPABILITIES = {
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
    "openclaw_runtime_status_consumption_allowed": False,
    "openclaw_tool_invocation_allowed": False,
    "openclaw_operational_integration_allowed": False,
}

ALLOWED_FUTURE_ACTIONS = [
    "READ_HASH_BOUND_PROJECT_STATUS_SNAPSHOT",
    "SUMMARIZE_VALIDATED_PROJECT_STATUS",
    "EXPLAIN_FAILED_GATES_AND_RESTRICTIONS",
    "CITE_SOURCE_ANCHORS",
    "REQUEST_HUMAN_REVIEW",
]

FORBIDDEN_ACTIONS = [
    "RECOMPUTE_OR_OVERRIDE_PYTHON_RESULTS",
    "MUTATE_CANDIDATES_OR_PARAMETERS",
    "OPEN_LOCKBOX_OR_HOLDOUT",
    "GENERATE_ACTIONABLE_TRADING_SIGNALS",
    "SEND_LIVE_ALERTS",
    "SUBMIT_PAPER_OR_REAL_TRADES",
    "WRITE_OFFICIAL_EVIDENCE",
    "INVOKE_EXCHANGE_EXECUTION",
    "ENABLE_AUTOMATION",
]


class ConsumerBoundaryError(RuntimeError):
    """Raised whenever the passive export cannot be trusted fail-closed."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ConsumerBoundaryError(message)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def normalized_text_bytes(path: Path) -> bytes:
    raw = path.read_bytes()
    if raw.startswith(b"\xef\xbb\xbf"):
        raw = raw[3:]
    return raw.replace(b"\r\n", b"\n").replace(b"\r", b"\n")


def normalized_text_sha256(path: Path) -> str:
    return sha256_bytes(normalized_text_bytes(path))


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


def _reject_duplicate_object_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ConsumerBoundaryError(f"Duplicate JSON field: {key}")
        result[key] = value
    return result


def load_json_strict(payload: bytes, *, label: str) -> dict[str, Any]:
    try:
        value = json.loads(
            payload.decode("utf-8"),
            object_pairs_hook=_reject_duplicate_object_pairs,
            parse_constant=lambda token: (_ for _ in ()).throw(
                ConsumerBoundaryError(f"{label}: non-finite JSON token {token}")
            ),
        )
    except UnicodeDecodeError as exc:
        raise ConsumerBoundaryError(f"{label}: invalid UTF-8") from exc
    except json.JSONDecodeError as exc:
        raise ConsumerBoundaryError(f"{label}: invalid JSON") from exc
    _require(isinstance(value, dict), f"{label}: top-level value must be an object")
    return value


def expected_snapshot() -> dict[str, Any]:
    snapshot: dict[str, Any] = {
        "contract": {
            "phase": "10.42R.3",
            "schema_version": "OPENCLAW_READ_ONLY_RESEARCH_STATUS_CONTRACT_V1",
            "mode": "DESIGN_ONLY_READ_ONLY_STATUS_CONTRACT",
            "generated_at_utc": DETERMINISTIC_GENERATED_AT_UTC,
            "freshness_basis": "SOURCE_COMMIT_BOUND",
            "stale_when": "SOURCE_COMMIT_OR_CONTRACT_VERSION_DIFFERS",
            "wall_clock_expiry_seconds": 0,
        },
        "source_anchors": {
            "phase_10_42r_2l_commit": (
                "2177f69c1dd221ab9cf0db9a5c40992355a3317c"
            ),
            "phase_10_42r_2k_bundle_root_sha256": (
                "2938dcf9596281a8416b9ecd6f7431cbebee89559063bfe100a11258f76cbd02"
            ),
            "phase_10_42r_2l_audit_bundle_root_sha256": (
                "8f7f9b514f31a6cb98884febf396f9e57ecfbe53b4ebcf844c5752f1d3b055d6"
            ),
            "phase_10_42r_2j_binding_root_sha256": (
                "5c1ccb1c9fecdad2e196558a946944f5b9f89f258c5ef591a65d4c4c480d8c14"
            ),
            "long_empty_schema_candidate_sha256": (
                "e3fa86a461fd46f4d66dc2e03f185e49b7b3438d3cbc33340c01f51310514ff1"
            ),
            "phase_10_42_document": (
                "docs/PHASE_10_LONG_FORWARD_OBSERVATION_EVIDENCE_COLLECTION_"
                "OFFICIAL_DATASET_ATOMIC_WRITE_HARNESS_DESIGN.md"
            ),
            "phase_10_42r_document": (
                "docs/PHASE_10_42R_PROJECT_SCIENTIFIC_INTEGRITY_AND_"
                "REPRODUCIBILITY_AUDIT.md"
            ),
            "phase_10_42r_2_document": (
                "docs/PHASE_10_42R_2_SHORT_LONG_CLOSED_CANDLE_MTF_REVALIDATION.md"
            ),
            "phase_10_42r_2l_document": (
                "docs/PHASE_10_42R_2L_FROZEN_RECOVERY_CANDIDATE_"
                "INDEPENDENT_RESULT_AUDIT_AND_DISPOSITION.md"
            ),
        },
        "master_disposition": {
            "phase_10_42_atomic_write_design": "VALIDATED_DESIGN_ONLY",
            "phase_10_42r_scientific_remediation": "COMPLETED",
            "phase_10_42r_2_revalidation": "COMPLETED",
            "legacy_short_candidate": "REVALIDATED_REJECTED",
            "short_recovery_line": "CLOSED_ALL_VARIANTS_REJECTED",
            "long_primary_candidate": (
                "RESEARCH_ONLY_CERTIFIED_UNAFFECTED_AND_CONSISTENCY_REVALIDATED"
            ),
            "long_secondary_candidate": (
                "WATCHLIST_ONLY_CERTIFIED_UNAFFECTED_AND_CONSISTENCY_REVALIDATED"
            ),
            "long_empty_schema_candidate": "TRACKED_54_COLUMNS_ZERO_EVIDENCE_ROWS",
            "retrospective_lockbox": "SEALED",
            "prospective_holdout": "SEALED",
            "openclaw_status_contract": "DESIGN_VALIDATED_RUNTIME_NOT_IMPLEMENTED",
            "total_project_completed": False,
        },
        "evidence_summary": {
            "short_recovery_variant_count": 6,
            "short_recovery_rejected_variant_count": 6,
            "short_recovery_surviving_variant_count": 0,
            "phase_2k_source_artifact_count": 12,
            "phase_2k_signal_row_count": 9216,
            "phase_2k_order_row_count": 9216,
            "phase_2k_trade_row_count": 5689,
            "phase_2k_metric_row_count": 450,
            "phase_2k_multiplicity_row_count": 6,
            "phase_2k_gate_row_count": 60,
            "phase_2l_failed_check_count": 0,
            "phase_2l_blocker_count": 0,
            "retrospective_lockbox_access_count": 0,
            "prospective_holdout_access_count": 0,
            "operational_approval_count": 0,
            "long_empty_schema_column_count": 54,
            "long_official_evidence_row_count": 0,
        },
        "permissions": {
            "read_only_capabilities": dict(READ_ONLY_CAPABILITIES),
            "prohibited_capabilities": dict(PROHIBITED_CAPABILITIES),
        },
        "openclaw_policy": {
            "consumer_role": "EXPLANATION_ONLY_AFTER_FUTURE_IMPLEMENTATION",
            "source_of_truth": "PYTHON_VALIDATOR_AND_HASH_BOUND_STATUS_SNAPSHOT",
            "required_failure_mode": "FAIL_CLOSED",
            "human_decision_required": True,
            "permission_override_allowed": False,
            "stale_snapshot_use_allowed": False,
            "schema_mismatch_use_allowed": False,
            "unknown_status_inference_allowed": False,
            "runtime_integration_status": "NOT_IMPLEMENTED",
            "allowed_future_actions": list(ALLOWED_FUTURE_ACTIONS),
            "forbidden_actions": list(FORBIDDEN_ACTIONS),
        },
        "next_routes": {
            "long_dataset_track": PHASE_10_43_ROUTE,
            "openclaw_read_only_track": (
                "PHASE_10_42R_4_OPENCLAW_READ_ONLY_RESEARCH_STATUS_"
                "EXPORT_IMPLEMENTATION_V1"
            ),
            "route_independence": True,
            "phase_10_43_design_review_allowed": True,
            "openclaw_read_only_status_export_implementation_allowed": True,
            "another_recovery_repair_phase_allowed": False,
            "lockbox_opening_allowed": False,
        },
    }
    root_material = copy.deepcopy(snapshot)
    root_material["contract"].pop("generated_at_utc")
    snapshot["contract_root_sha256"] = sha256_bytes(
        canonical_compact_json_bytes(root_material)
    )
    return snapshot


def expected_manifest(snapshot_bytes: bytes) -> dict[str, Any]:
    return {
        "export_phase": "10.42R.4",
        "export_schema_version": "OPENCLAW_READ_ONLY_RESEARCH_STATUS_EXPORT_V1",
        "export_mode": "LOCAL_FILE_EXPORT_READ_ONLY_NO_RUNTIME_CONSUMER",
        "snapshot_filename": SNAPSHOT_FILENAME,
        "snapshot_sha256": sha256_bytes(snapshot_bytes),
        "snapshot_size_bytes": len(snapshot_bytes),
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


def expected_export_bytes() -> tuple[bytes, bytes]:
    snapshot_bytes = canonical_pretty_json_bytes(expected_snapshot())
    manifest_bytes = canonical_pretty_json_bytes(expected_manifest(snapshot_bytes))
    return snapshot_bytes, manifest_bytes


def _read_source_manifest(root: Path) -> dict[str, str]:
    path = root / SOURCE_EXPORT_MANIFEST_PATH
    _require(path.is_file(), f"Missing Phase 10.42R.4 source manifest: {path}")
    values: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line:
            continue
        match = re.fullmatch(r"([0-9a-f]{64})  (.+)", line)
        _require(match is not None, f"Invalid source manifest line: {raw_line}")
        digest, relative_path = match.groups()
        _require(relative_path not in values, f"Duplicate manifest path: {relative_path}")
        values[relative_path] = digest
    return values


def inspect_source_freshness(root: Path, *, require_git: bool = True) -> dict[str, Any]:
    if not (root / ".git").exists():
        _require(not require_git, "Git metadata is required for review freshness")
        return {
            "git_metadata_available": False,
            "current_head": "NOT_AVAILABLE",
            "source_export_commit_exists": False,
            "source_export_commit_is_ancestor": False,
            "freshness_check_skipped": True,
        }

    def run(args: Sequence[str], *, allow_failure: bool = False) -> subprocess.CompletedProcess[str]:
        result = subprocess.run(
            ["git", "-C", str(root), *args],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        if not allow_failure and result.returncode != 0:
            raise ConsumerBoundaryError(
                f"Git command failed: {' '.join(args)}: {result.stderr.strip()}"
            )
        return result

    head = run(["rev-parse", "HEAD"]).stdout.strip()
    exists = (
        run(
            ["cat-file", "-e", f"{SOURCE_EXPORT_COMMIT}^{{commit}}"],
            allow_failure=True,
        ).returncode
        == 0
    )
    ancestor = False
    if exists:
        ancestor = (
            run(
                ["merge-base", "--is-ancestor", SOURCE_EXPORT_COMMIT, "HEAD"],
                allow_failure=True,
            ).returncode
            == 0
        )
    _require(exists, "Source export commit does not exist")
    _require(ancestor, "Source export commit is not an ancestor of HEAD")
    return {
        "git_metadata_available": True,
        "current_head": head,
        "source_export_commit_exists": exists,
        "source_export_commit_is_ancestor": ancestor,
        "freshness_check_skipped": False,
    }


def verify_source_authority(root: Path, *, require_git: bool = True) -> dict[str, Any]:
    module_path = root / SOURCE_EXPORT_MODULE_PATH
    document_path = root / SOURCE_EXPORT_DOCUMENT_PATH
    _require(module_path.is_file(), f"Missing source export module: {module_path}")
    _require(document_path.is_file(), f"Missing source export document: {document_path}")
    module_hash = normalized_text_sha256(module_path)
    document_hash = normalized_text_sha256(document_path)
    _require(module_hash == SOURCE_EXPORT_MODULE_SHA256, "Source export module hash mismatch")
    _require(document_hash == SOURCE_EXPORT_DOCUMENT_SHA256, "Source export document hash mismatch")
    manifest = _read_source_manifest(root)
    _require(
        manifest.get(SOURCE_EXPORT_MODULE_PATH.as_posix()) == SOURCE_EXPORT_MODULE_SHA256,
        "Source export module is not bound by the 10.42R.4 manifest",
    )
    _require(
        manifest.get(SOURCE_EXPORT_DOCUMENT_PATH.as_posix())
        == SOURCE_EXPORT_DOCUMENT_SHA256,
        "Source export document is not bound by the 10.42R.4 manifest",
    )
    return {
        "source_export_commit": SOURCE_EXPORT_COMMIT,
        "source_export_module_sha256": module_hash,
        "source_export_document_sha256": document_hash,
        **inspect_source_freshness(root, require_git=require_git),
    }


def review_export_bundle(
    root: Path | str = Path("."),
    *,
    bundle_dir: Path | str | None = None,
    require_git: bool = True,
) -> dict[str, Any]:
    root_path = Path(root).resolve()
    authority = verify_source_authority(root_path, require_git=require_git)
    source_dir = (
        Path(bundle_dir).resolve()
        if bundle_dir is not None
        else (root_path / SOURCE_BUNDLE_DIR).resolve()
    )
    _require(source_dir.is_dir(), f"Missing source export directory: {source_dir}")
    paths = list(source_dir.iterdir())
    _require(all(path.is_file() for path in paths), "Subdirectories are not allowed in export bundle")
    inventory = sorted(path.name for path in paths)
    _require(
        inventory == sorted([SNAPSHOT_FILENAME, MANIFEST_FILENAME]),
        f"Export bundle inventory mismatch: {inventory}",
    )
    _require(not any(".tmp-" in path.name for path in paths), "Temporary file remains")

    snapshot_bytes = (source_dir / SNAPSHOT_FILENAME).read_bytes()
    manifest_bytes = (source_dir / MANIFEST_FILENAME).read_bytes()
    _require(len(snapshot_bytes) == SOURCE_SNAPSHOT_SIZE_BYTES, "Snapshot size mismatch")
    _require(sha256_bytes(snapshot_bytes) == SOURCE_SNAPSHOT_SHA256, "Snapshot hash mismatch")
    _require(sha256_bytes(manifest_bytes) == SOURCE_MANIFEST_SHA256, "Manifest hash mismatch")

    snapshot = load_json_strict(snapshot_bytes, label="snapshot")
    manifest = load_json_strict(manifest_bytes, label="manifest")
    expected_snapshot_value = expected_snapshot()
    expected_snapshot_bytes, expected_manifest_bytes = expected_export_bytes()
    _require(snapshot == expected_snapshot_value, "Snapshot semantic content mismatch")
    _require(snapshot_bytes == expected_snapshot_bytes, "Snapshot canonical bytes mismatch")
    _require(manifest == expected_manifest(snapshot_bytes), "Manifest semantic content mismatch")
    _require(manifest_bytes == expected_manifest_bytes, "Manifest canonical bytes mismatch")

    root_material = copy.deepcopy(snapshot)
    actual_root = root_material.pop("contract_root_sha256", None)
    root_material["contract"].pop("generated_at_utc", None)
    calculated_root = sha256_bytes(canonical_compact_json_bytes(root_material))
    _require(actual_root == SOURCE_CONTRACT_ROOT_SHA256, "Contract root value mismatch")
    _require(calculated_root == actual_root, "Contract root cannot be reproduced")

    read_only = snapshot["permissions"]["read_only_capabilities"]
    prohibited = snapshot["permissions"]["prohibited_capabilities"]
    _require(read_only == READ_ONLY_CAPABILITIES, "Read-only capability set mismatch")
    _require(prohibited == PROHIBITED_CAPABILITIES, "Prohibited capability set mismatch")
    _require(all(value is True for value in read_only.values()), "Read-only capability disabled")
    _require(all(value is False for value in prohibited.values()), "Prohibited capability enabled")

    policy = snapshot["openclaw_policy"]
    _require(policy["required_failure_mode"] == "FAIL_CLOSED", "Failure mode mismatch")
    _require(policy["runtime_integration_status"] == "NOT_IMPLEMENTED", "Runtime status mismatch")
    _require(policy["human_decision_required"] is True, "Human review must remain required")
    _require(policy["permission_override_allowed"] is False, "Permission override enabled")
    _require(policy["allowed_future_actions"] == ALLOWED_FUTURE_ACTIONS, "Allowed actions mismatch")
    _require(policy["forbidden_actions"] == FORBIDDEN_ACTIONS, "Forbidden actions mismatch")

    _require(manifest["snapshot_sha256"] == SOURCE_SNAPSHOT_SHA256, "Manifest snapshot hash mismatch")
    _require(manifest["snapshot_size_bytes"] == SOURCE_SNAPSHOT_SIZE_BYTES, "Manifest snapshot size mismatch")
    _require(manifest["source_contract_commit"] == SOURCE_CONTRACT_COMMIT, "Manifest source commit mismatch")
    _require(manifest["source_contract_root_sha256"] == SOURCE_CONTRACT_ROOT_SHA256, "Manifest root mismatch")
    _require(manifest["source_contract_module_sha256"] == SOURCE_CONTRACT_MODULE_SHA256, "Manifest module hash mismatch")
    _require(manifest["source_schema_sha256"] == SOURCE_SCHEMA_SHA256, "Manifest schema hash mismatch")
    for field in (
        "openclaw_runtime_status_consumption_allowed",
        "openclaw_tool_invocation_allowed",
        "openclaw_operational_integration_allowed",
        "official_dataset_write_allowed",
        "signal_generation_enabled",
        "paper_trade_execution_allowed",
        "real_capital_allowed",
        "market_execution_allowed",
        "automation_allowed",
    ):
        _require(manifest[field] is False, f"Manifest prohibited flag enabled: {field}")

    return {
        "validation_passed": True,
        "review_phase": PHASE,
        "review_schema_version": REVIEW_SCHEMA_VERSION,
        "bundle_directory": source_dir.as_posix(),
        "export_file_count": 2,
        "snapshot_sha256": SOURCE_SNAPSHOT_SHA256,
        "snapshot_size_bytes": SOURCE_SNAPSHOT_SIZE_BYTES,
        "manifest_sha256": SOURCE_MANIFEST_SHA256,
        "contract_root_sha256": SOURCE_CONTRACT_ROOT_SHA256,
        "read_only_capability_count": len(read_only),
        "prohibited_capability_count": len(prohibited),
        "consumer_boundary_status": "VALIDATED_FAIL_CLOSED_SIMULATION_ONLY",
        **authority,
    }


def simulate_read_only_consumer(
    root: Path | str = Path("."),
    *,
    bundle_dir: Path | str | None = None,
    require_git: bool = True,
) -> dict[str, Any]:
    review = review_export_bundle(
        root,
        bundle_dir=bundle_dir,
        require_git=require_git,
    )
    source_dir = Path(review["bundle_directory"])
    snapshot = load_json_strict(
        (source_dir / SNAPSHOT_FILENAME).read_bytes(),
        label="snapshot",
    )
    disposition = snapshot["master_disposition"]
    evidence = snapshot["evidence_summary"]
    policy = snapshot["openclaw_policy"]
    routes = snapshot["next_routes"]
    return {
        "consumer_mode": "SIMULATED_LOCAL_READ_ONLY_NO_OPENCLAW_RUNTIME",
        "consumer_decision": "READ_ONLY_STATUS_ACCEPTED_FOR_HUMAN_EXPLANATION_SIMULATION",
        "validation_passed": True,
        "source_export_commit": SOURCE_EXPORT_COMMIT,
        "source_contract_commit": SOURCE_CONTRACT_COMMIT,
        "contract_root_sha256": SOURCE_CONTRACT_ROOT_SHA256,
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
        "human_decision_required": policy["human_decision_required"],
        "runtime_integration_status": policy["runtime_integration_status"],
        "phase_10_43_design_review_allowed": routes[
            "phase_10_43_design_review_allowed"
        ],
        "openclaw_runtime_status_consumption_allowed": False,
        "openclaw_tool_invocation_allowed": False,
        "openclaw_operational_integration_allowed": False,
        "signal_generation_enabled": False,
        "paper_trade_execution_allowed": False,
        "real_capital_allowed": False,
        "market_execution_allowed": False,
        "automation_allowed": False,
        "next_phase": NEXT_PHASE,
    }


__all__ = [
    "ConsumerBoundaryError",
    "MANIFEST_FILENAME",
    "NEXT_PHASE",
    "PHASE",
    "PROHIBITED_CAPABILITIES",
    "READ_ONLY_CAPABILITIES",
    "REVIEW_SCHEMA_VERSION",
    "SNAPSHOT_FILENAME",
    "SOURCE_BUNDLE_DIR",
    "SOURCE_CONTRACT_ROOT_SHA256",
    "SOURCE_EXPORT_COMMIT",
    "SOURCE_MANIFEST_SHA256",
    "SOURCE_SNAPSHOT_SHA256",
    "SOURCE_SNAPSHOT_SIZE_BYTES",
    "canonical_pretty_json_bytes",
    "expected_export_bytes",
    "expected_manifest",
    "expected_snapshot",
    "load_json_strict",
    "normalized_text_sha256",
    "review_export_bundle",
    "sha256_bytes",
    "simulate_read_only_consumer",
    "verify_source_authority",
]
