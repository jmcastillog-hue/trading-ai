from __future__ import annotations

import hashlib
import json
import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from src.evaluation import (
    frozen_recovery_candidate_controlled_known_evidence_evaluation_v1 as evaluator,
)


PHASE = "10.42R.2K"
SCHEMA_VERSION = "CONTROLLED_KNOWN_EVIDENCE_EVALUATION_VALIDATION_V1"
SOURCE_PHASE_2J_COMMIT = evaluator.SOURCE_PHASE_2J_COMMIT
EXPECTED_ENGINE_SOURCE_SHA256 = "9243ae595f7d22bc2653ba34098bec5f1b6bc2a1e79c4114b8ea35fd83c3a4fd"
RECOMMENDED_NEXT_PHASE = evaluator.RECOMMENDED_NEXT_PHASE

EXPECTED_SOURCE_HASHES = {
    "src/analysis/frozen_recovery_candidate_implementation_v2.py":
        evaluator.SOURCE_CORRECTED_IMPLEMENTATION_SHA256,
    "src/validation/frozen_recovery_candidate_controlled_historical_evaluation_preregistration_v1.py":
        "89c2d1fed13b1585be90931115c9a834b9009a4f895ee8785cfc14a5910fbcf4",
    "src/validation/frozen_recovery_candidate_controlled_historical_evaluation_harness_design_v1.py":
        "e885aca401384d0ea1db40eada96846081eb4661e88634fb26837769230a2913",
    "src/validation/frozen_recovery_candidate_historical_input_manifest_binding_and_integrity_validation_v1.py":
        "652dc49e9e51f0d77d0cdb5b2ed2854456c17f6f79e335393f84bec10893355d",
    "PHASE_10_42R_2J_MANIFEST.sha256":
        "0d9cf4aa5cddee69f765cf3bd5fa1378442b38306d3136d479b4b4af2778f278",
}

ENGINE_PATH = Path(
    "src/evaluation/"
    "frozen_recovery_candidate_controlled_known_evidence_evaluation_v1.py"
)
REPORT_IGNORE_RULE = "reports/phase_10_42r_2k/"


@dataclass(frozen=True)
class Check:
    check_id: str
    check_name: str
    passed: bool
    details: str
    blocker: bool


class EvaluationValidationFailure(RuntimeError):
    pass


def normalized_source_sha256(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _append(
    checks: list[Check],
    name: str,
    passed: bool,
    details: str,
    *,
    blocker: bool = True,
) -> None:
    ok = bool(passed)
    checks.append(
        Check(
            check_id=f"2K-VALIDATION-{len(checks) + 1:03d}",
            check_name=name,
            passed=ok,
            details=str(details),
            blocker=bool(blocker and not ok),
        )
    )


def _source_commit_is_ancestor(root: Path) -> tuple[bool, str]:
    result = subprocess.run(
        ["git", "merge-base", "--is-ancestor", SOURCE_PHASE_2J_COMMIT, "HEAD"],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )
    return result.returncode == 0, f"returncode={result.returncode}"


def _report_path_is_ignored(root: Path) -> tuple[bool, str]:
    probe = REPORT_IGNORE_RULE + "validation_probe.txt"
    result = subprocess.run(
        ["git", "check-ignore", "--quiet", "--", probe],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )
    return result.returncode == 0, probe


def validate_preflight(root: Path | None = None) -> dict[str, Any]:
    project_root = (root or Path.cwd()).resolve()
    checks: list[Check] = []

    passed, details = _source_commit_is_ancestor(project_root)
    _append(checks, "source_phase_2j_commit_is_ancestor", passed, details)

    for relative_path, expected_hash in EXPECTED_SOURCE_HASHES.items():
        path = project_root / relative_path
        actual_hash = normalized_source_sha256(path) if path.is_file() else ""
        _append(
            checks,
            "source_anchor_" + relative_path.replace("/", "_"),
            path.is_file() and actual_hash == expected_hash,
            f"expected={expected_hash},actual={actual_hash}",
        )

    engine_path = project_root / ENGINE_PATH
    engine_hash = normalized_source_sha256(engine_path) if engine_path.is_file() else ""
    _append(
        checks,
        "evaluation_engine_source_exact",
        engine_path.is_file() and engine_hash == EXPECTED_ENGINE_SOURCE_SHA256,
        f"expected={EXPECTED_ENGINE_SOURCE_SHA256},actual={engine_hash}",
    )

    from src.validation import (
        frozen_recovery_candidate_historical_input_manifest_binding_and_integrity_validation_v1
        as phase_2j,
    )

    _append(
        checks,
        "binding_root_exact",
        phase_2j.BINDING_ROOT_SHA256
        == evaluator.SOURCE_PHASE_2J_BINDING_ROOT_SHA256,
        phase_2j.BINDING_ROOT_SHA256,
    )
    _append(
        checks,
        "bound_dataset_registry_exact",
        len(phase_2j.EXPECTED_DATASETS) == 9,
        str(len(phase_2j.EXPECTED_DATASETS)),
    )
    missing_inputs = [
        details["relative_path"]
        for details in phase_2j.EXPECTED_DATASETS.values()
        if not (project_root / details["relative_path"]).is_file()
    ]
    _append(
        checks,
        "all_nine_bound_datasets_exist",
        not missing_inputs,
        ",".join(missing_inputs),
    )
    missing_audit = [
        path.as_posix()
        for path in (
            phase_2j.MANIFEST_PATH,
            phase_2j.PROVENANCE_PATH,
            phase_2j.MISSING_INTERVAL_LEDGER_PATH,
        )
        if not (project_root / path).is_file()
    ]
    _append(
        checks,
        "all_three_binding_audit_artifacts_exist",
        not missing_audit,
        ",".join(missing_audit),
    )
    existing_forbidden = [
        path.as_posix()
        for path in evaluator.FORBIDDEN_ARTIFACT_PATHS
        if (project_root / path).exists()
    ]
    _append(
        checks,
        "lockboxes_and_forward_dataset_absent",
        not existing_forbidden,
        ",".join(existing_forbidden),
    )
    _append(
        checks,
        "limited_research_permissions_exact",
        {
            name for name, value in evaluator.PERMISSIONS.items() if value
        }
        == evaluator.ALLOWED_TRUE_PERMISSIONS,
        evaluator.canonical_json(
            {name: value for name, value in evaluator.PERMISSIONS.items() if value}
        ),
    )
    ignored, details = _report_path_is_ignored(project_root)
    _append(checks, "phase_2k_report_path_is_git_ignored", ignored, details)
    _append(
        checks,
        "no_ranking_winner_or_operations",
        not evaluator.PERMISSIONS["candidate_ranking_allowed"]
        and not evaluator.PERMISSIONS["winner_selection_allowed"]
        and not evaluator.PERMISSIONS["execution_allowed"]
        and not evaluator.PERMISSIONS["openclaw_operational_integration_allowed"],
        "false",
    )

    failed = tuple(check for check in checks if not check.passed)
    blockers = tuple(check for check in failed if check.blocker)
    summary = {
        "phase": PHASE,
        "schema_version": SCHEMA_VERSION,
        "preflight_only": True,
        "engine_source_sha256": engine_hash,
        "source_anchor_count": len(EXPECTED_SOURCE_HASHES),
        "logical_slot_count": 9,
        "preflight_check_count": len(checks),
        "evaluation_check_count": 0,
        "total_check_count": len(checks),
        "failed_check_count": len(failed),
        "blocker_count": len(blockers),
        "historical_evaluation_count": 0,
        "backtest_execution_count": 0,
        "performance_metric_count": 0,
        "candidate_comparison_count": 0,
        "candidate_ranking_count": 0,
        "winner_selection_count": 0,
        "retrospective_lockbox_access_count": 0,
        "prospective_holdout_access_count": 0,
        "result_artifact_write_count": 0,
        "validation_decision": (
            "PREFLIGHT_PASSED" if not blockers else "PREFLIGHT_BLOCKED"
        ),
        "validation_passed": not blockers,
        "recommended_next_phase": "NONE",
    }
    return {
        "summary": summary,
        "checks": tuple(asdict(check) for check in checks),
        "failed_checks": tuple(asdict(check) for check in failed),
    }


def validate_completed_evaluation(
    evaluation_result: dict[str, Any],
    *,
    root: Path | None = None,
) -> dict[str, Any]:
    project_root = (root or Path.cwd()).resolve()
    preflight = validate_preflight(project_root)
    checks = [Check(**item) for item in preflight["checks"]]
    summary = evaluation_result["summary"]
    output_dir = project_root / summary["output_directory"]

    expected_inventory = set(evaluator.AUDIT_ARTIFACTS)
    actual_inventory = (
        {path.name for path in output_dir.iterdir() if path.is_file()}
        if output_dir.is_dir()
        else set()
    )
    _append(
        checks,
        "audit_artifact_inventory_exact_twelve",
        actual_inventory == expected_inventory,
        evaluator.canonical_json(sorted(actual_inventory)),
    )
    _append(
        checks,
        "evaluation_completed",
        bool(summary.get("evaluation_completed")),
        str(summary.get("evaluation_completed")),
    )
    _append(
        checks,
        "evaluation_internal_integrity_checks_passed",
        int(summary.get("failed_check_count", -1)) == 0
        and int(summary.get("blocker_count", -1)) == 0,
        f"failed={summary.get('failed_check_count')},blockers={summary.get('blocker_count')}",
    )
    _append(
        checks,
        "six_variants_three_families_three_symbols",
        summary.get("variant_count") == 6
        and summary.get("family_count") == 3
        and summary.get("symbol_count") == 3,
        f"{summary.get('variant_count')}/{summary.get('family_count')}/{summary.get('symbol_count')}",
    )
    _append(
        checks,
        "metric_table_row_count_450",
        len(evaluation_result["metric_table"]) == 450,
        str(len(evaluation_result["metric_table"])),
    )
    _append(
        checks,
        "multiplicity_table_row_count_six",
        len(evaluation_result["multiplicity_table"]) == 6,
        str(len(evaluation_result["multiplicity_table"])),
    )
    _append(
        checks,
        "gate_classification_row_count_sixty",
        len(evaluation_result["gate_classification"]) == 60,
        str(len(evaluation_result["gate_classification"])),
    )
    _append(
        checks,
        "all_results_known_evidence_only",
        bool(summary.get("known_evidence_only")),
        str(summary.get("known_evidence_only")),
    )
    _append(
        checks,
        "no_candidate_comparison_ranking_or_winner",
        summary.get("candidate_comparison_count") == 0
        and summary.get("candidate_ranking_count") == 0
        and summary.get("winner_selection_count") == 0
        and summary.get("winner") is None,
        "0/0/0/None",
    )
    _append(
        checks,
        "no_lockbox_access",
        summary.get("retrospective_lockbox_access_count") == 0
        and summary.get("prospective_holdout_access_count") == 0,
        "0/0",
    )
    _append(
        checks,
        "no_operational_approval",
        summary.get("operational_approval_granted") is False
        and summary.get("operational_permissions_enabled_count") == 0,
        "false/0",
    )
    _append(
        checks,
        "declared_gaps_preserved_without_fill",
        summary.get("declared_source_missing_interval_count") == 18
        and summary.get("synthetic_gap_fill_count") == 0,
        f"{summary.get('declared_source_missing_interval_count')}/"
        f"{summary.get('synthetic_gap_fill_count')}",
    )

    run_summary_path = output_dir / "run_summary.json"
    persisted_summary = (
        json.loads(run_summary_path.read_text(encoding="utf-8"))
        if run_summary_path.is_file()
        else {}
    )
    persisted_hashes = persisted_summary.get("artifact_hashes", {})
    actual_hashes = {
        name: sha256_file(output_dir / name)
        for name in evaluator.AUDIT_ARTIFACTS[:-1]
        if (output_dir / name).is_file()
    }
    _append(
        checks,
        "persisted_artifact_hashes_exact",
        persisted_hashes == actual_hashes
        and len(actual_hashes) == len(evaluator.AUDIT_ARTIFACTS) - 1,
        evaluator.canonical_json(actual_hashes),
    )
    expected_bundle_root = hashlib.sha256(
        evaluator.canonical_json(actual_hashes).encode("utf-8")
    ).hexdigest()
    _append(
        checks,
        "bundle_root_exact",
        persisted_summary.get("bundle_root_sha256") == expected_bundle_root,
        expected_bundle_root,
    )
    _append(
        checks,
        "next_phase_is_independent_audit",
        summary.get("recommended_next_phase") == RECOMMENDED_NEXT_PHASE,
        str(summary.get("recommended_next_phase")),
    )

    failed = tuple(check for check in checks if not check.passed)
    blockers = tuple(check for check in failed if check.blocker)
    preflight_count = preflight["summary"]["preflight_check_count"]
    final_summary = {
        "phase": PHASE,
        "schema_version": SCHEMA_VERSION,
        "preflight_only": False,
        "run_id": summary.get("run_id", ""),
        "output_directory": summary.get("output_directory", ""),
        "bundle_root_sha256": expected_bundle_root,
        "variant_count": summary.get("variant_count", 0),
        "family_count": summary.get("family_count", 0),
        "symbol_count": summary.get("symbol_count", 0),
        "signal_row_count": summary.get("signal_row_count", 0),
        "order_row_count": summary.get("order_row_count", 0),
        "trade_row_count": summary.get("trade_row_count", 0),
        "eligible_trade_count": summary.get("eligible_trade_count", 0),
        "metric_row_count": summary.get("metric_row_count", 0),
        "multiplicity_row_count": summary.get("multiplicity_row_count", 0),
        "gate_row_count": summary.get("gate_row_count", 0),
        "preflight_check_count": preflight_count,
        "evaluation_check_count": len(checks) - preflight_count,
        "total_check_count": len(checks),
        "failed_check_count": len(failed),
        "blocker_count": len(blockers),
        "historical_evaluation_count": summary.get("historical_evaluation_count", 0),
        "backtest_execution_count": summary.get("backtest_execution_count", 0),
        "performance_metric_count": summary.get("performance_metric_count", 0),
        "candidate_comparison_count": 0,
        "candidate_ranking_count": 0,
        "winner_selection_count": 0,
        "retrospective_lockbox_access_count": 0,
        "prospective_holdout_access_count": 0,
        "result_artifact_write_count": len(actual_inventory),
        "evaluation_completed": not blockers,
        "winner_selection_allowed": False,
        "validation_decision": (
            "CONTROLLED_KNOWN_EVIDENCE_EVALUATION_VALIDATED_NO_WINNER"
            if not blockers
            else "CONTROLLED_KNOWN_EVIDENCE_EVALUATION_BLOCKED_NO_WINNER"
        ),
        "validation_passed": not blockers,
        "recommended_next_phase": (
            RECOMMENDED_NEXT_PHASE if not blockers else "NONE"
        ),
    }
    return {
        "summary": final_summary,
        "checks": tuple(asdict(check) for check in checks),
        "failed_checks": tuple(asdict(check) for check in failed),
        "evaluation_summary": summary,
    }


def require_valid_preflight(root: Path | None = None) -> dict[str, Any]:
    result = validate_preflight(root)
    if not result["summary"]["validation_passed"]:
        names = ", ".join(
            item["check_name"] for item in result["failed_checks"] if item["blocker"]
        )
        raise EvaluationValidationFailure("Phase 2K preflight failed: " + names)
    return result


__all__ = [
    "ENGINE_PATH",
    "EXPECTED_ENGINE_SOURCE_SHA256",
    "EXPECTED_SOURCE_HASHES",
    "EvaluationValidationFailure",
    "PHASE",
    "RECOMMENDED_NEXT_PHASE",
    "REPORT_IGNORE_RULE",
    "SCHEMA_VERSION",
    "SOURCE_PHASE_2J_COMMIT",
    "normalized_source_sha256",
    "require_valid_preflight",
    "sha256_file",
    "validate_completed_evaluation",
    "validate_preflight",
]
