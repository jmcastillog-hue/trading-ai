from __future__ import annotations

import copy
import hashlib
import json
from datetime import datetime, timezone
from typing import Any, Mapping


PHASE = "10.42R.3"
SCHEMA_VERSION = "OPENCLAW_READ_ONLY_RESEARCH_STATUS_CONTRACT_V1"
CONTRACT_MODE = "DESIGN_ONLY_READ_ONLY_STATUS_CONTRACT"
SOURCE_PHASE_2L_COMMIT = "2177f69c1dd221ab9cf0db9a5c40992355a3317c"
SOURCE_PHASE_2K_BUNDLE_ROOT_SHA256 = (
    "2938dcf9596281a8416b9ecd6f7431cbebee89559063bfe100a11258f76cbd02"
)
SOURCE_PHASE_2L_AUDIT_BUNDLE_ROOT_SHA256 = (
    "8f7f9b514f31a6cb98884febf396f9e57ecfbe53b4ebcf844c5752f1d3b055d6"
)
SOURCE_PHASE_2J_BINDING_ROOT_SHA256 = (
    "5c1ccb1c9fecdad2e196558a946944f5b9f89f258c5ef591a65d4c4c480d8c14"
)
SOURCE_LONG_EMPTY_SCHEMA_CANDIDATE_SHA256 = (
    "e3fa86a461fd46f4d66dc2e03f185e49b7b3438d3cbc33340c01f51310514ff1"
)

PHASE_10_43_ROUTE = (
    "PHASE_10_43_LONG_FORWARD_OBSERVATION_EVIDENCE_COLLECTION_"
    "OFFICIAL_DATASET_ATOMIC_WRITE_HARNESS_DESIGN_REVIEW_V1"
)
OPENCLAW_NEXT_ROUTE = (
    "PHASE_10_42R_4_OPENCLAW_READ_ONLY_RESEARCH_STATUS_EXPORT_IMPLEMENTATION_V1"
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

MASTER_DISPOSITION = {
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
}

EVIDENCE_SUMMARY = {
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
}

ALLOWED_FUTURE_OPENCLAW_ACTIONS = (
    "READ_HASH_BOUND_PROJECT_STATUS_SNAPSHOT",
    "SUMMARIZE_VALIDATED_PROJECT_STATUS",
    "EXPLAIN_FAILED_GATES_AND_RESTRICTIONS",
    "CITE_SOURCE_ANCHORS",
    "REQUEST_HUMAN_REVIEW",
)

FORBIDDEN_OPENCLAW_ACTIONS = (
    "RECOMPUTE_OR_OVERRIDE_PYTHON_RESULTS",
    "MUTATE_CANDIDATES_OR_PARAMETERS",
    "OPEN_LOCKBOX_OR_HOLDOUT",
    "GENERATE_ACTIONABLE_TRADING_SIGNALS",
    "SEND_LIVE_ALERTS",
    "SUBMIT_PAPER_OR_REAL_TRADES",
    "WRITE_OFFICIAL_EVIDENCE",
    "INVOKE_EXCHANGE_EXECUTION",
    "ENABLE_AUTOMATION",
)

SOURCE_ANCHORS = {
    "phase_10_42r_2l_commit": SOURCE_PHASE_2L_COMMIT,
    "phase_10_42r_2k_bundle_root_sha256": SOURCE_PHASE_2K_BUNDLE_ROOT_SHA256,
    "phase_10_42r_2l_audit_bundle_root_sha256": (
        SOURCE_PHASE_2L_AUDIT_BUNDLE_ROOT_SHA256
    ),
    "phase_10_42r_2j_binding_root_sha256": SOURCE_PHASE_2J_BINDING_ROOT_SHA256,
    "long_empty_schema_candidate_sha256": SOURCE_LONG_EMPTY_SCHEMA_CANDIDATE_SHA256,
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
}


class StatusContractError(ValueError):
    pass


def canonical_json(value: object) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    )


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _root_material(snapshot: Mapping[str, Any]) -> dict[str, Any]:
    material = copy.deepcopy(dict(snapshot))
    material.pop("contract_root_sha256", None)
    contract = material.get("contract")
    if isinstance(contract, dict):
        contract.pop("generated_at_utc", None)
    return material


def calculate_contract_root(snapshot: Mapping[str, Any]) -> str:
    return sha256_bytes(canonical_json(_root_material(snapshot)).encode("utf-8"))


def build_status_snapshot(*, generated_at_utc: str | None = None) -> dict[str, Any]:
    snapshot: dict[str, Any] = {
        "contract": {
            "phase": PHASE,
            "schema_version": SCHEMA_VERSION,
            "mode": CONTRACT_MODE,
            "generated_at_utc": generated_at_utc or _utc_now(),
            "freshness_basis": "SOURCE_COMMIT_BOUND",
            "stale_when": "SOURCE_COMMIT_OR_CONTRACT_VERSION_DIFFERS",
            "wall_clock_expiry_seconds": 0,
        },
        "source_anchors": dict(SOURCE_ANCHORS),
        "master_disposition": dict(MASTER_DISPOSITION),
        "evidence_summary": dict(EVIDENCE_SUMMARY),
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
            "allowed_future_actions": list(ALLOWED_FUTURE_OPENCLAW_ACTIONS),
            "forbidden_actions": list(FORBIDDEN_OPENCLAW_ACTIONS),
        },
        "next_routes": {
            "long_dataset_track": PHASE_10_43_ROUTE,
            "openclaw_read_only_track": OPENCLAW_NEXT_ROUTE,
            "route_independence": True,
            "phase_10_43_design_review_allowed": True,
            "openclaw_read_only_status_export_implementation_allowed": True,
            "another_recovery_repair_phase_allowed": False,
            "lockbox_opening_allowed": False,
        },
    }
    snapshot["contract_root_sha256"] = calculate_contract_root(snapshot)
    return snapshot


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise StatusContractError(message)


def validate_status_snapshot(snapshot: Mapping[str, Any]) -> None:
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
    _require(set(snapshot) == expected_top, "Top-level contract fields mismatch")

    contract = snapshot["contract"]
    _require(isinstance(contract, Mapping), "contract must be an object")
    _require(contract.get("phase") == PHASE, "phase mismatch")
    _require(contract.get("schema_version") == SCHEMA_VERSION, "schema mismatch")
    _require(contract.get("mode") == CONTRACT_MODE, "mode mismatch")
    _require(
        contract.get("freshness_basis") == "SOURCE_COMMIT_BOUND",
        "freshness basis mismatch",
    )
    _require(
        contract.get("stale_when") == "SOURCE_COMMIT_OR_CONTRACT_VERSION_DIFFERS",
        "staleness rule mismatch",
    )
    _require(contract.get("wall_clock_expiry_seconds") == 0, "expiry mismatch")
    _require(bool(contract.get("generated_at_utc")), "generated_at_utc missing")

    _require(
        dict(snapshot["source_anchors"]) == SOURCE_ANCHORS,
        "source anchors mismatch",
    )
    _require(
        dict(snapshot["master_disposition"]) == MASTER_DISPOSITION,
        "master disposition mismatch",
    )
    _require(
        dict(snapshot["evidence_summary"]) == EVIDENCE_SUMMARY,
        "evidence summary mismatch",
    )

    permissions = snapshot["permissions"]
    _require(
        dict(permissions.get("read_only_capabilities", {})) == READ_ONLY_CAPABILITIES,
        "read-only capabilities mismatch",
    )
    _require(
        dict(permissions.get("prohibited_capabilities", {}))
        == PROHIBITED_CAPABILITIES,
        "prohibited capabilities mismatch",
    )
    _require(
        all(value is True for value in READ_ONLY_CAPABILITIES.values()),
        "read-only capabilities must be true",
    )
    _require(
        all(value is False for value in PROHIBITED_CAPABILITIES.values()),
        "prohibited capabilities must be false",
    )

    policy = snapshot["openclaw_policy"]
    _require(policy.get("required_failure_mode") == "FAIL_CLOSED", "failure mode")
    _require(policy.get("human_decision_required") is True, "human review")
    _require(policy.get("permission_override_allowed") is False, "override")
    _require(policy.get("runtime_integration_status") == "NOT_IMPLEMENTED", "runtime")
    _require(
        tuple(policy.get("allowed_future_actions", ()))
        == ALLOWED_FUTURE_OPENCLAW_ACTIONS,
        "allowed actions mismatch",
    )
    _require(
        tuple(policy.get("forbidden_actions", ())) == FORBIDDEN_OPENCLAW_ACTIONS,
        "forbidden actions mismatch",
    )

    routes = snapshot["next_routes"]
    _require(routes.get("long_dataset_track") == PHASE_10_43_ROUTE, "10.43 route")
    _require(
        routes.get("openclaw_read_only_track") == OPENCLAW_NEXT_ROUTE,
        "OpenClaw route",
    )
    _require(routes.get("route_independence") is True, "route independence")
    _require(
        routes.get("another_recovery_repair_phase_allowed") is False,
        "repair route must remain closed",
    )
    _require(routes.get("lockbox_opening_allowed") is False, "lockbox route")

    expected_root = calculate_contract_root(snapshot)
    _require(
        snapshot.get("contract_root_sha256") == expected_root,
        "contract root mismatch",
    )


__all__ = [
    "ALLOWED_FUTURE_OPENCLAW_ACTIONS",
    "CONTRACT_MODE",
    "EVIDENCE_SUMMARY",
    "FORBIDDEN_OPENCLAW_ACTIONS",
    "MASTER_DISPOSITION",
    "OPENCLAW_NEXT_ROUTE",
    "PHASE",
    "PHASE_10_43_ROUTE",
    "PROHIBITED_CAPABILITIES",
    "READ_ONLY_CAPABILITIES",
    "SCHEMA_VERSION",
    "SOURCE_ANCHORS",
    "StatusContractError",
    "build_status_snapshot",
    "calculate_contract_root",
    "canonical_json",
    "validate_status_snapshot",
]
