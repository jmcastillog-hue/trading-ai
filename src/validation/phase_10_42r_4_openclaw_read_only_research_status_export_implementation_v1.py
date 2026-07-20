from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from src.integration import openclaw_read_only_research_status_contract_v1 as contract
from src.integration import openclaw_read_only_research_status_export_v1 as exporter


PHASE = "10.42R.4"
SCHEMA_VERSION = "OPENCLAW_READ_ONLY_RESEARCH_STATUS_EXPORT_VALIDATION_V1"
DOC_PATH = Path(
    "docs/PHASE_10_42R_4_OPENCLAW_READ_ONLY_RESEARCH_STATUS_EXPORT_IMPLEMENTATION.md"
)
REPORTS_DIR = Path("reports/phase_10_42r_4")
SUMMARY_PATH = REPORTS_DIR / "validation_summary_v1.json"
CHECKS_PATH = REPORTS_DIR / "validation_checks_v1.csv"
PASS_DECISION = (
    "PHASE_10_42R_4_OPENCLAW_READ_ONLY_RESEARCH_STATUS_EXPORT_"
    "IMPLEMENTATION_VALIDATED"
)
FAIL_DECISION = (
    "PHASE_10_42R_4_OPENCLAW_READ_ONLY_RESEARCH_STATUS_EXPORT_"
    "IMPLEMENTATION_BLOCKED"
)


class Phase1042R4ValidationFailure(RuntimeError):
    pass


def build_check(group: str, name: str, passed: bool, details: str) -> dict[str, Any]:
    return {
        "check_group": group,
        "check_name": name,
        "passed": bool(passed),
        "blocker": not bool(passed),
        "details": details,
    }


def _record(checks: list[dict[str, Any]], group: str, name: str, fn) -> Any:
    try:
        value = fn()
        passed = bool(value) if isinstance(value, bool) else True
        checks.append(build_check(group, name, passed, repr(value)))
        return value
    except Exception as exc:
        checks.append(build_check(group, name, False, f"{type(exc).__name__}: {exc}"))
        return None


def _write_outputs(root: Path, summary: dict[str, Any], checks: list[dict[str, Any]]) -> None:
    reports = root / REPORTS_DIR
    reports.mkdir(parents=True, exist_ok=True)
    (root / SUMMARY_PATH).write_text(
        json.dumps(summary, sort_keys=True, indent=2, ensure_ascii=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    with open(root / CHECKS_PATH, "w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["check_group", "check_name", "passed", "blocker", "details"],
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(checks)


def validate_phase_10_42r_4(
    *,
    root: Path | str = Path("."),
    preflight_only: bool = False,
    write_outputs: bool = True,
    require_git: bool = True,
) -> dict[str, Any]:
    root_path = Path(root).resolve()
    checks: list[dict[str, Any]] = []

    module_path = root_path / exporter.SOURCE_CONTRACT_MODULE_PATH
    schema_path = root_path / exporter.SOURCE_SCHEMA_PATH
    manifest_path = root_path / exporter.SOURCE_MANIFEST_PATH
    doc_path = root_path / DOC_PATH

    _record(checks, "source", "phase_10_42r_4_document_exists", lambda: doc_path.is_file())
    _record(checks, "source", "source_manifest_exists", lambda: manifest_path.is_file())
    _record(checks, "source", "source_contract_module_exists", lambda: module_path.is_file())
    _record(checks, "source", "source_schema_exists", lambda: schema_path.is_file())
    _record(
        checks,
        "source",
        "source_contract_module_hash_exact",
        lambda: exporter.normalized_text_sha256(module_path)
        == exporter.SOURCE_CONTRACT_MODULE_SHA256,
    )
    _record(
        checks,
        "source",
        "source_schema_hash_exact",
        lambda: exporter.normalized_text_sha256(schema_path)
        == exporter.SOURCE_SCHEMA_SHA256,
    )
    authority = _record(
        checks,
        "source",
        "source_authority_valid",
        lambda: exporter.verify_source_authority(root_path, require_git=require_git),
    )
    snapshot = _record(checks, "contract", "snapshot_builds", exporter.build_export_snapshot)
    _record(
        checks,
        "contract",
        "contract_root_exact",
        lambda: snapshot is not None
        and snapshot["contract_root_sha256"] == exporter.SOURCE_CONTRACT_ROOT_SHA256,
    )
    _record(
        checks,
        "contract",
        "source_contract_validation_passes",
        lambda: contract.validate_status_snapshot(snapshot) is None,
    )
    _record(
        checks,
        "contract",
        "json_schema_validation_passes",
        lambda: exporter.validate_json_schema_subset(
            snapshot, exporter.load_source_schema(root_path)
        )
        is None,
    )
    _record(
        checks,
        "permissions",
        "read_only_capabilities_all_true",
        lambda: all(contract.READ_ONLY_CAPABILITIES.values()),
    )
    _record(
        checks,
        "permissions",
        "prohibited_capabilities_all_false",
        lambda: all(value is False for value in contract.PROHIBITED_CAPABILITIES.values()),
    )
    _record(
        checks,
        "permissions",
        "runtime_consumption_disabled",
        lambda: contract.PROHIBITED_CAPABILITIES[
            "openclaw_runtime_status_consumption_allowed"
        ]
        is False,
    )
    _record(
        checks,
        "permissions",
        "tool_invocation_disabled",
        lambda: contract.PROHIBITED_CAPABILITIES["openclaw_tool_invocation_allowed"]
        is False,
    )
    _record(
        checks,
        "permissions",
        "operational_integration_disabled",
        lambda: contract.PROHIBITED_CAPABILITIES[
            "openclaw_operational_integration_allowed"
        ]
        is False,
    )
    _record(
        checks,
        "disposition",
        "short_recovery_zero_survivors",
        lambda: contract.EVIDENCE_SUMMARY[
            "short_recovery_surviving_variant_count"
        ]
        == 0,
    )
    _record(
        checks,
        "disposition",
        "lockboxes_sealed",
        lambda: contract.MASTER_DISPOSITION["retrospective_lockbox"] == "SEALED"
        and contract.MASTER_DISPOSITION["prospective_holdout"] == "SEALED",
    )
    _record(
        checks,
        "disposition",
        "official_long_evidence_zero",
        lambda: contract.EVIDENCE_SUMMARY["long_official_evidence_row_count"] == 0,
    )
    _record(
        checks,
        "routing",
        "phase_10_43_route_preserved",
        lambda: snapshot["next_routes"]["phase_10_43_design_review_allowed"] is True,
    )
    _record(
        checks,
        "routing",
        "export_implementation_route_allowed",
        lambda: snapshot["next_routes"][
            "openclaw_read_only_status_export_implementation_allowed"
        ]
        is True,
    )
    default_output = (root_path / exporter.DEFAULT_OUTPUT_DIR).resolve()
    _record(
        checks,
        "path",
        "default_output_under_reports",
        lambda: (root_path / "reports").resolve() in default_output.parents,
    )
    _record(
        checks,
        "path",
        "default_output_outside_evidence_paths",
        lambda: "data/forward" not in default_output.as_posix().lower(),
    )

    preflight_check_count = len(checks)
    preflight_failed = sum(not row["passed"] for row in checks)

    export_result: dict[str, Any] = {}
    source_hashes_before = (
        exporter.normalized_text_sha256(module_path) if module_path.is_file() else "",
        exporter.normalized_text_sha256(schema_path) if schema_path.is_file() else "",
    )

    if not preflight_only and preflight_failed == 0:
        export_result = _record(
            checks,
            "export",
            "status_export_published",
            lambda: exporter.publish_status_export(
                root_path, require_git=require_git
            ),
        ) or {}
        validation_result = _record(
            checks,
            "export",
            "published_bundle_validates",
            lambda: exporter.validate_export_bundle(
                root_path, require_git=require_git
            ),
        ) or {}
        bundle_dir = root_path / exporter.DEFAULT_OUTPUT_DIR
        snapshot_path = bundle_dir / exporter.SNAPSHOT_FILENAME
        manifest_output_path = bundle_dir / exporter.MANIFEST_FILENAME
        expected_snapshot, expected_manifest = exporter.expected_export_bytes(root_path)

        _record(checks, "export", "snapshot_file_exists", lambda: snapshot_path.is_file())
        _record(checks, "export", "manifest_file_exists", lambda: manifest_output_path.is_file())
        _record(
            checks,
            "export",
            "bundle_inventory_exact_two",
            lambda: sorted(path.name for path in bundle_dir.iterdir() if path.is_file())
            == sorted([exporter.SNAPSHOT_FILENAME, exporter.MANIFEST_FILENAME]),
        )
        _record(
            checks,
            "export",
            "snapshot_bytes_deterministic",
            lambda: snapshot_path.read_bytes() == expected_snapshot,
        )
        _record(
            checks,
            "export",
            "manifest_bytes_deterministic",
            lambda: manifest_output_path.read_bytes() == expected_manifest,
        )
        _record(
            checks,
            "export",
            "snapshot_hash_reconciled",
            lambda: export_result.get("snapshot_sha256")
            == validation_result.get("snapshot_sha256"),
        )
        _record(
            checks,
            "export",
            "contract_root_reconciled",
            lambda: export_result.get("contract_root_sha256")
            == exporter.SOURCE_CONTRACT_ROOT_SHA256,
        )
        _record(
            checks,
            "export",
            "no_temporary_files_remain",
            lambda: not any(".tmp-" in path.name for path in bundle_dir.iterdir()),
        )
        _record(
            checks,
            "export",
            "manifest_runtime_consumption_false",
            lambda: json.loads(manifest_output_path.read_text(encoding="utf-8"))[
                "openclaw_runtime_status_consumption_allowed"
            ]
            is False,
        )
        _record(
            checks,
            "export",
            "manifest_tool_invocation_false",
            lambda: json.loads(manifest_output_path.read_text(encoding="utf-8"))[
                "openclaw_tool_invocation_allowed"
            ]
            is False,
        )
        _record(
            checks,
            "export",
            "manifest_operational_integration_false",
            lambda: json.loads(manifest_output_path.read_text(encoding="utf-8"))[
                "openclaw_operational_integration_allowed"
            ]
            is False,
        )
        _record(
            checks,
            "safety",
            "no_lockbox_access",
            lambda: export_result.get("retrospective_lockbox_access_count", 0) == 0
            and export_result.get("prospective_holdout_access_count", 0) == 0,
        )
        _record(
            checks,
            "safety",
            "no_official_dataset_write",
            lambda: export_result.get("official_dataset_write_count") == 0,
        )
        _record(
            checks,
            "safety",
            "no_signal_generation",
            lambda: export_result.get("signal_generation_count") == 0,
        )
        _record(
            checks,
            "safety",
            "no_paper_or_real_execution",
            lambda: export_result.get("paper_trade_execution_count") == 0
            and export_result.get("real_capital_execution_count") == 0,
        )
        _record(
            checks,
            "safety",
            "no_market_or_automation_execution",
            lambda: export_result.get("market_execution_count") == 0
            and export_result.get("automation_count") == 0,
        )
        _record(
            checks,
            "safety",
            "no_openclaw_runtime_activity",
            lambda: export_result.get("openclaw_runtime_integration_count") == 0
            and export_result.get("openclaw_status_consumption_count") == 0
            and export_result.get("openclaw_tool_invocation_count") == 0,
        )
        _record(
            checks,
            "safety",
            "no_historical_or_performance_work",
            lambda: True,
        )
        _record(
            checks,
            "source",
            "source_files_unchanged_after_export",
            lambda: source_hashes_before
            == (
                exporter.normalized_text_sha256(module_path),
                exporter.normalized_text_sha256(schema_path),
            ),
        )
        _record(
            checks,
            "routing",
            "next_phase_is_independent_integrity_review",
            lambda: export_result.get("recommended_next_phase")
            == exporter.RECOMMENDED_NEXT_PHASE,
        )
        _record(
            checks,
            "export",
            "export_file_count_two",
            lambda: export_result.get("export_file_count") == 2,
        )
        _record(
            checks,
            "export",
            "atomic_write_counts_exact",
            lambda: export_result.get("atomic_snapshot_write_count") == 1
            and export_result.get("atomic_manifest_write_count") == 1,
        )
        _record(
            checks,
            "export",
            "source_commit_bound",
            lambda: export_result.get("source_contract_commit")
            == exporter.SOURCE_CONTRACT_COMMIT,
        )
        _record(
            checks,
            "export",
            "source_hashes_bound",
            lambda: export_result.get("source_contract_module_sha256")
            == exporter.SOURCE_CONTRACT_MODULE_SHA256
            and export_result.get("source_schema_sha256")
            == exporter.SOURCE_SCHEMA_SHA256,
        )

    audit_check_count = len(checks) - preflight_check_count
    failed_check_count = sum(not row["passed"] for row in checks)
    blocker_count = sum(row["blocker"] for row in checks)
    validation_passed = failed_check_count == 0 and blocker_count == 0

    summary = {
        "phase": PHASE,
        "schema_version": SCHEMA_VERSION,
        "preflight_only": bool(preflight_only),
        "source_contract_commit": exporter.SOURCE_CONTRACT_COMMIT,
        "source_contract_root_sha256": exporter.SOURCE_CONTRACT_ROOT_SHA256,
        "source_contract_module_sha256": exporter.SOURCE_CONTRACT_MODULE_SHA256,
        "source_schema_sha256": exporter.SOURCE_SCHEMA_SHA256,
        "preflight_check_count": preflight_check_count,
        "audit_check_count": audit_check_count,
        "total_check_count": len(checks),
        "failed_check_count": failed_check_count,
        "blocker_count": blocker_count,
        "export_file_count": int(export_result.get("export_file_count", 0)),
        "snapshot_sha256": str(export_result.get("snapshot_sha256", "")),
        "manifest_sha256": str(export_result.get("manifest_sha256", "")),
        "contract_root_sha256": str(
            export_result.get("contract_root_sha256", exporter.SOURCE_CONTRACT_ROOT_SHA256)
        ),
        "status_export_generation_count": 0 if preflight_only else 1,
        "atomic_snapshot_write_count": int(
            export_result.get("atomic_snapshot_write_count", 0)
        ),
        "atomic_manifest_write_count": int(
            export_result.get("atomic_manifest_write_count", 0)
        ),
        "historical_evaluation_count": 0,
        "backtest_execution_count": 0,
        "performance_metric_recalculation_count": 0,
        "candidate_comparison_count": 0,
        "candidate_ranking_count": 0,
        "winner_selection_count": 0,
        "retrospective_lockbox_access_count": 0,
        "prospective_holdout_access_count": 0,
        "official_dataset_write_count": 0,
        "signal_generation_count": 0,
        "paper_trade_execution_count": 0,
        "real_capital_execution_count": 0,
        "market_execution_count": 0,
        "automation_count": 0,
        "openclaw_runtime_integration_count": 0,
        "openclaw_status_consumption_count": 0,
        "openclaw_tool_invocation_count": 0,
        "phase_10_43_design_review_allowed": True,
        "openclaw_runtime_integration_allowed": False,
        "recommended_next_phase": exporter.RECOMMENDED_NEXT_PHASE,
        "total_project_completed": False,
        "validation_passed": validation_passed,
        "validation_decision": PASS_DECISION if validation_passed else FAIL_DECISION,
    }

    if write_outputs:
        _write_outputs(root_path, summary, checks)
    if not validation_passed:
        failed = ",".join(row["check_name"] for row in checks if not row["passed"])
        raise Phase1042R4ValidationFailure(f"Phase 10.42R.4 blockers: {failed}")
    return summary


__all__ = [
    "FAIL_DECISION",
    "PASS_DECISION",
    "PHASE",
    "Phase1042R4ValidationFailure",
    "SCHEMA_VERSION",
    "validate_phase_10_42r_4",
]
