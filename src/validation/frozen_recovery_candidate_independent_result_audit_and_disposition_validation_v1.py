from __future__ import annotations

import ast
import hashlib
from pathlib import Path
from typing import Any

from src.audit import (
    frozen_recovery_candidate_independent_result_audit_and_disposition_v1 as audit,
)


PHASE = "10.42R.2L"
SCHEMA_VERSION = "INDEPENDENT_RESULT_AUDIT_AND_DISPOSITION_VALIDATION_V1"
SOURCE_PHASE_2K_COMMIT = "0a5440a70e91e833925a4147ac2863baa7666b1e"
EXPECTED_AUDIT_SOURCE_SHA256 = "d49bd3a087b46b4751b09bc125a6e0b81e812490c0aac99a84ac8d8e036466aa"
SOURCE_ANCHOR_COUNT = 6
PREFLIGHT_CHECK_COUNT = 12
FULL_AUDIT_CHECK_COUNT = 31
EXPECTED_TOTAL_CHECK_COUNT = PREFLIGHT_CHECK_COUNT + FULL_AUDIT_CHECK_COUNT

SOURCE_PATHS = (
    Path("PHASE_10_42R_2L_MANIFEST.sha256"),
    Path("docs/PHASE_10_42R_2L_FROZEN_RECOVERY_CANDIDATE_INDEPENDENT_RESULT_AUDIT_AND_DISPOSITION.md"),
    Path("src/audit/frozen_recovery_candidate_independent_result_audit_and_disposition_v1.py"),
    Path("src/validation/frozen_recovery_candidate_independent_result_audit_and_disposition_validation_v1.py"),
    Path("src/workflows/run_phase_10_42r_2l_frozen_recovery_candidate_independent_result_audit_and_disposition.py"),
    Path("tests/test_frozen_recovery_candidate_independent_result_audit_and_disposition.py"),
)

FORBIDDEN_IMPORT_PREFIXES = (
    "src.backtesting",
    "src.strategies",
    "src.long_side",
    "src.execution",
)
FORBIDDEN_CALLS = {
    "run_controlled_known_evidence_evaluation",
    "evaluate_variant_on_symbol",
    "download_binance_klines_range",
    "read_excel",
    "read_parquet",
}


def normalized_source_sha256(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _source_boundary_is_independent() -> tuple[bool, str]:
    path = Path("src/audit/frozen_recovery_candidate_independent_result_audit_and_disposition_v1.py")
    tree = ast.parse(path.read_text(encoding="utf-8"))
    imports: list[str] = []
    calls: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imports.append(node.module or "")
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                calls.append(node.func.id)
            elif isinstance(node.func, ast.Attribute):
                calls.append(node.func.attr)
    forbidden_imports = sorted(
        module
        for module in imports
        if any(module == prefix or module.startswith(prefix + ".") for prefix in FORBIDDEN_IMPORT_PREFIXES)
    )
    forbidden_calls = sorted(set(calls) & FORBIDDEN_CALLS)
    valid = not forbidden_imports and not forbidden_calls
    return valid, f"forbidden_imports={forbidden_imports}, forbidden_calls={forbidden_calls}"


def _manifest_is_exact() -> tuple[bool, str]:
    manifest = Path("PHASE_10_42R_2L_MANIFEST.sha256")
    if not manifest.is_file():
        return False, "manifest missing"
    expected_paths = sorted(path.as_posix() for path in SOURCE_PATHS[1:])
    actual_paths: list[str] = []
    for line in manifest.read_text(encoding="utf-8").splitlines():
        parts = line.split("  ", 1)
        if len(parts) != 2 or len(parts[0]) != 64:
            return False, f"invalid manifest line={line}"
        digest, relative = parts
        path = Path(relative)
        if not path.is_file():
            return False, f"missing={relative}"
        if hashlib.sha256(path.read_bytes()).hexdigest() != digest:
            return False, f"hash mismatch={relative}"
        actual_paths.append(relative)
    return sorted(actual_paths) == expected_paths, f"entries={len(actual_paths)}"


def validate_preflight() -> dict[str, Any]:
    checks: list[dict[str, Any]] = []

    def add(name: str, passed: bool, details: str) -> None:
        checks.append(
            {
                "check_id": f"2L-PREFLIGHT-{len(checks) + 1:03d}",
                "check_name": name,
                "passed": bool(passed),
                "details": str(details),
                "blocker": not bool(passed),
            }
        )

    add("phase_exact", audit.PHASE == PHASE, audit.PHASE)
    add("schema_exact", audit.SCHEMA_VERSION == "INDEPENDENT_RESULT_AUDIT_AND_DISPOSITION_V1", audit.SCHEMA_VERSION)
    add("source_phase_2k_commit_exact", audit.SOURCE_PHASE_2K_COMMIT == SOURCE_PHASE_2K_COMMIT, audit.SOURCE_PHASE_2K_COMMIT)
    add("source_run_id_exact", audit.SOURCE_PHASE_2K_RUN_ID == "known_evidence_2022_2025_v1_5c1ccb1c9fec_9243ae595f7d", audit.SOURCE_PHASE_2K_RUN_ID)
    add("source_bundle_root_exact", audit.SOURCE_PHASE_2K_BUNDLE_ROOT_SHA256 == "2938dcf9596281a8416b9ecd6f7431cbebee89559063bfe100a11258f76cbd02", audit.SOURCE_PHASE_2K_BUNDLE_ROOT_SHA256)
    add("source_engine_hash_exact", audit.SOURCE_PHASE_2K_ENGINE_SHA256 == "9243ae595f7d22bc2653ba34098bec5f1b6bc2a1e79c4114b8ea35fd83c3a4fd", audit.SOURCE_PHASE_2K_ENGINE_SHA256)
    add("audit_source_hash_exact", normalized_source_sha256(Path("src/audit/frozen_recovery_candidate_independent_result_audit_and_disposition_v1.py")) == EXPECTED_AUDIT_SOURCE_SHA256, EXPECTED_AUDIT_SOURCE_SHA256)
    manifest_ok, manifest_details = _manifest_is_exact()
    add("package_manifest_exact", manifest_ok, manifest_details)
    boundary_ok, boundary_details = _source_boundary_is_independent()
    add("independent_source_boundary", boundary_ok, boundary_details)
    add("artifact_inventory_exact", len(audit.AUDIT_ARTIFACTS) == 12 and len(audit.OUTPUT_ARTIFACTS) == 7, f"source={len(audit.AUDIT_ARTIFACTS)},output={len(audit.OUTPUT_ARTIFACTS)}")
    add("finite_route_exact", audit.RECOMMENDED_NEXT_ROUTE.startswith("RETURN_TO_PHASE_10_42R_MASTER_DISPOSITION"), audit.RECOMMENDED_NEXT_ROUTE)
    add("no_operational_authorization", "NO_LOCKBOX_OPENED" in audit.FINAL_DECISION, audit.FINAL_DECISION)

    failed = [item for item in checks if not item["passed"]]
    blockers = [item for item in checks if item["blocker"]]
    return {
        "checks": tuple(checks),
        "summary": {
            "phase": PHASE,
            "schema_version": SCHEMA_VERSION,
            "source_anchor_count": SOURCE_ANCHOR_COUNT,
            "preflight_check_count": len(checks),
            "audit_check_count": 0,
            "total_check_count": len(checks),
            "failed_check_count": len(failed),
            "blocker_count": len(blockers),
            "historical_evaluation_count": 0,
            "backtest_execution_count": 0,
            "performance_metric_reproduction_count": 0,
            "retrospective_lockbox_access_count": 0,
            "prospective_holdout_access_count": 0,
            "candidate_comparison_count": 0,
            "candidate_ranking_count": 0,
            "winner_selection_count": 0,
            "preflight_only": True,
            "validation_decision": "PREFLIGHT_PASSED" if not blockers else "PREFLIGHT_BLOCKED",
            "validation_passed": not blockers,
            "recommended_next_route": "NONE",
        },
    }


def validate_phase_10_42r_2l(
    *,
    preflight_only: bool = False,
    root: Path | None = None,
    write_outputs: bool = True,
) -> dict[str, Any]:
    preflight = validate_preflight()
    if preflight_only or not preflight["summary"]["validation_passed"]:
        return preflight
    result = audit.run_independent_result_audit(root=root, write_outputs=write_outputs)
    audit_checks = list(result["checks"])
    all_checks = list(preflight["checks"]) + audit_checks
    failed = [item for item in all_checks if not item["passed"]]
    blockers = [item for item in all_checks if item["blocker"]]
    source_summary = result["summary"]
    summary = {
        "phase": PHASE,
        "schema_version": SCHEMA_VERSION,
        "source_anchor_count": SOURCE_ANCHOR_COUNT,
        "source_artifact_count": source_summary["source_artifact_count"],
        "variant_count": source_summary["variant_count"],
        "rejected_variant_count": source_summary["rejected_variant_count"],
        "surviving_variant_count": source_summary["surviving_variant_count"],
        "signal_row_count": source_summary["signal_row_count"],
        "order_row_count": source_summary["order_row_count"],
        "trade_row_count": source_summary["trade_row_count"],
        "metric_row_count": source_summary["metric_row_count"],
        "multiplicity_row_count": source_summary["multiplicity_row_count"],
        "gate_row_count": source_summary["gate_row_count"],
        "preflight_check_count": len(preflight["checks"]),
        "audit_check_count": len(audit_checks),
        "total_check_count": len(all_checks),
        "failed_check_count": len(failed),
        "blocker_count": len(blockers),
        "historical_evaluation_count": source_summary["historical_evaluation_count"],
        "backtest_execution_count": source_summary["backtest_execution_count"],
        "performance_metric_reproduction_count": source_summary["performance_metric_reproduction_count"],
        "retrospective_lockbox_access_count": source_summary["retrospective_lockbox_access_count"],
        "prospective_holdout_access_count": source_summary["prospective_holdout_access_count"],
        "candidate_comparison_count": source_summary["candidate_comparison_count"],
        "candidate_ranking_count": source_summary["candidate_ranking_count"],
        "winner_selection_count": source_summary["winner_selection_count"],
        "candidate_mutation_count": source_summary["candidate_mutation_count"],
        "recovery_line_closed": source_summary["recovery_line_closed"],
        "lockbox_opening_allowed": source_summary["lockbox_opening_allowed"],
        "audit_bundle_root_sha256": source_summary["audit_bundle_root_sha256"],
        "output_directory": source_summary["output_directory"],
        "publish_status": source_summary["publish_status"],
        "preflight_only": False,
        "validation_decision": source_summary["validation_decision"] if not blockers else "INDEPENDENT_RESULT_AUDIT_BLOCKED",
        "validation_passed": not blockers,
        "recommended_next_route": source_summary["recommended_next_route"] if not blockers else "NONE",
    }
    return {
        "checks": tuple(all_checks),
        "summary": summary,
        "dispositions": result["dispositions"],
    }


__all__ = [
    "EXPECTED_AUDIT_SOURCE_SHA256",
    "EXPECTED_TOTAL_CHECK_COUNT",
    "FULL_AUDIT_CHECK_COUNT",
    "PHASE",
    "PREFLIGHT_CHECK_COUNT",
    "SCHEMA_VERSION",
    "validate_phase_10_42r_2l",
    "validate_preflight",
]
