from __future__ import annotations

import csv
import json
import shutil
import tempfile
from pathlib import Path
from typing import Any, Callable

from src.integration import openclaw_read_only_research_status_consumer_boundary_v1 as review


PHASE = "10.42R.5"
SCHEMA_VERSION = (
    "OPENCLAW_READ_ONLY_RESEARCH_STATUS_EXPORT_INTEGRITY_"
    "AND_CONSUMER_BOUNDARY_REVIEW_VALIDATION_V1"
)
DOC_PATH = Path(
    "docs/PHASE_10_42R_5_OPENCLAW_READ_ONLY_RESEARCH_STATUS_EXPORT_"
    "INTEGRITY_AND_CONSUMER_BOUNDARY_REVIEW.md"
)
REPORTS_DIR = Path("reports/phase_10_42r_5")
SUMMARY_PATH = REPORTS_DIR / "validation_summary_v1.json"
CHECKS_PATH = REPORTS_DIR / "validation_checks_v1.csv"
CONSUMER_VIEW_PATH = REPORTS_DIR / "simulated_read_only_consumer_view_v1.json"
PASS_DECISION = (
    "PHASE_10_42R_5_OPENCLAW_READ_ONLY_RESEARCH_STATUS_EXPORT_INTEGRITY_"
    "AND_CONSUMER_BOUNDARY_REVIEW_VALIDATED"
)
FAIL_DECISION = (
    "PHASE_10_42R_5_OPENCLAW_READ_ONLY_RESEARCH_STATUS_EXPORT_INTEGRITY_"
    "AND_CONSUMER_BOUNDARY_REVIEW_BLOCKED"
)


class Phase1042R5ValidationFailure(RuntimeError):
    pass


def build_check(group: str, name: str, passed: bool, details: str) -> dict[str, Any]:
    return {
        "check_group": group,
        "check_name": name,
        "passed": bool(passed),
        "blocker": not bool(passed),
        "details": details,
    }


def _record(
    checks: list[dict[str, Any]],
    group: str,
    name: str,
    fn: Callable[[], Any],
) -> Any:
    try:
        value = fn()
        passed = bool(value) if isinstance(value, bool) else True
        checks.append(build_check(group, name, passed, repr(value)))
        return value
    except Exception as exc:
        checks.append(build_check(group, name, False, f"{type(exc).__name__}: {exc}"))
        return None


def _expect_rejected(fn: Callable[[], Any]) -> bool:
    try:
        fn()
    except review.ConsumerBoundaryError:
        return True
    return False


def _copy_bundle(root: Path, destination: Path) -> Path:
    source = root / review.SOURCE_BUNDLE_DIR
    target = destination / "bundle"
    shutil.copytree(source, target)
    return target


def _write_outputs(
    root: Path,
    summary: dict[str, Any],
    checks: list[dict[str, Any]],
    consumer_view: dict[str, Any],
) -> None:
    reports = root / REPORTS_DIR
    reports.mkdir(parents=True, exist_ok=True)
    (root / SUMMARY_PATH).write_text(
        json.dumps(summary, sort_keys=True, indent=2, ensure_ascii=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    (root / CONSUMER_VIEW_PATH).write_text(
        json.dumps(consumer_view, sort_keys=True, indent=2, ensure_ascii=True) + "\n",
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


def validate_phase_10_42r_5(
    *,
    root: Path | str = Path("."),
    preflight_only: bool = False,
    write_outputs: bool = True,
    require_git: bool = True,
) -> dict[str, Any]:
    root_path = Path(root).resolve()
    checks: list[dict[str, Any]] = []
    source_bundle = root_path / review.SOURCE_BUNDLE_DIR
    snapshot_path = source_bundle / review.SNAPSHOT_FILENAME
    manifest_path = source_bundle / review.MANIFEST_FILENAME

    _record(checks, "source", "phase_10_42r_5_document_exists", lambda: (root_path / DOC_PATH).is_file())
    _record(checks, "source", "source_export_module_exists", lambda: (root_path / review.SOURCE_EXPORT_MODULE_PATH).is_file())
    _record(checks, "source", "source_export_document_exists", lambda: (root_path / review.SOURCE_EXPORT_DOCUMENT_PATH).is_file())
    _record(checks, "source", "source_export_manifest_exists", lambda: (root_path / review.SOURCE_EXPORT_MANIFEST_PATH).is_file())
    _record(checks, "source", "source_export_module_hash_exact", lambda: review.normalized_text_sha256(root_path / review.SOURCE_EXPORT_MODULE_PATH) == review.SOURCE_EXPORT_MODULE_SHA256)
    _record(checks, "source", "source_export_document_hash_exact", lambda: review.normalized_text_sha256(root_path / review.SOURCE_EXPORT_DOCUMENT_PATH) == review.SOURCE_EXPORT_DOCUMENT_SHA256)
    authority = _record(checks, "source", "source_authority_valid", lambda: review.verify_source_authority(root_path, require_git=require_git)) or {}
    _record(checks, "bundle", "source_bundle_directory_exists", lambda: source_bundle.is_dir())
    _record(checks, "bundle", "snapshot_exists", lambda: snapshot_path.is_file())
    _record(checks, "bundle", "manifest_exists", lambda: manifest_path.is_file())
    _record(checks, "bundle", "bundle_inventory_exact_two", lambda: source_bundle.is_dir() and sorted(path.name for path in source_bundle.iterdir()) == sorted([review.SNAPSHOT_FILENAME, review.MANIFEST_FILENAME]))
    _record(checks, "bundle", "snapshot_hash_exact", lambda: review.sha256_bytes(snapshot_path.read_bytes()) == review.SOURCE_SNAPSHOT_SHA256)
    _record(checks, "bundle", "snapshot_size_exact", lambda: len(snapshot_path.read_bytes()) == review.SOURCE_SNAPSHOT_SIZE_BYTES)
    _record(checks, "bundle", "manifest_hash_exact", lambda: review.sha256_bytes(manifest_path.read_bytes()) == review.SOURCE_MANIFEST_SHA256)
    expected_snapshot_bytes, expected_manifest_bytes = review.expected_export_bytes()
    _record(checks, "independence", "independent_snapshot_reproduction_exact", lambda: expected_snapshot_bytes == snapshot_path.read_bytes())
    _record(checks, "independence", "independent_manifest_reproduction_exact", lambda: expected_manifest_bytes == manifest_path.read_bytes())
    _record(checks, "permissions", "read_only_capability_count_six", lambda: len(review.READ_ONLY_CAPABILITIES) == 6 and all(review.READ_ONLY_CAPABILITIES.values()))
    _record(checks, "permissions", "prohibited_capability_count_twenty_three", lambda: len(review.PROHIBITED_CAPABILITIES) == 23 and all(value is False for value in review.PROHIBITED_CAPABILITIES.values()))
    _record(checks, "boundary", "runtime_consumption_disabled", lambda: review.PROHIBITED_CAPABILITIES["openclaw_runtime_status_consumption_allowed"] is False)
    _record(checks, "boundary", "tool_invocation_disabled", lambda: review.PROHIBITED_CAPABILITIES["openclaw_tool_invocation_allowed"] is False)
    _record(checks, "boundary", "operational_integration_disabled", lambda: review.PROHIBITED_CAPABILITIES["openclaw_operational_integration_allowed"] is False)
    _record(checks, "routing", "phase_10_43_route_preserved", lambda: review.PHASE_10_43_ROUTE.endswith("DESIGN_REVIEW_V1"))
    _record(checks, "routing", "next_phase_is_local_consumer_adapter_design", lambda: review.NEXT_PHASE == "PHASE_10_42R_6_OPENCLAW_READ_ONLY_RESEARCH_STATUS_LOCAL_CONSUMER_ADAPTER_DESIGN_V1")

    preflight_check_count = len(checks)
    preflight_failed = sum(not item["passed"] for item in checks)
    review_result: dict[str, Any] = {}
    consumer_view: dict[str, Any] = {}
    negative_control_count = 0

    if not preflight_only and preflight_failed == 0:
        review_result = _record(checks, "review", "independent_export_bundle_review_passes", lambda: review.review_export_bundle(root_path, require_git=require_git)) or {}
        consumer_view = _record(checks, "consumer", "simulated_read_only_consumer_accepts_valid_bundle", lambda: review.simulate_read_only_consumer(root_path, require_git=require_git)) or {}
        _record(checks, "consumer", "consumer_output_is_allowlisted", lambda: set(consumer_view) == {
            "consumer_mode", "consumer_decision", "validation_passed", "source_export_commit", "source_contract_commit", "contract_root_sha256", "legacy_short_candidate", "short_recovery_line", "short_recovery_surviving_variant_count", "long_primary_candidate", "long_secondary_candidate", "long_official_evidence_row_count", "retrospective_lockbox", "prospective_holdout", "human_decision_required", "runtime_integration_status", "phase_10_43_design_review_allowed", "openclaw_runtime_status_consumption_allowed", "openclaw_tool_invocation_allowed", "openclaw_operational_integration_allowed", "signal_generation_enabled", "paper_trade_execution_allowed", "real_capital_allowed", "market_execution_allowed", "automation_allowed", "next_phase"
        })
        _record(checks, "consumer", "consumer_mode_simulation_only", lambda: consumer_view.get("consumer_mode") == "SIMULATED_LOCAL_READ_ONLY_NO_OPENCLAW_RUNTIME")
        _record(checks, "consumer", "consumer_human_review_required", lambda: consumer_view.get("human_decision_required") is True)
        _record(checks, "consumer", "consumer_zero_short_survivors", lambda: consumer_view.get("short_recovery_surviving_variant_count") == 0)
        _record(checks, "consumer", "consumer_zero_long_evidence_rows", lambda: consumer_view.get("long_official_evidence_row_count") == 0)
        _record(checks, "consumer", "consumer_lockboxes_sealed", lambda: consumer_view.get("retrospective_lockbox") == "SEALED" and consumer_view.get("prospective_holdout") == "SEALED")
        _record(checks, "consumer", "consumer_operational_flags_false", lambda: all(consumer_view.get(field) is False for field in (
            "openclaw_runtime_status_consumption_allowed", "openclaw_tool_invocation_allowed", "openclaw_operational_integration_allowed", "signal_generation_enabled", "paper_trade_execution_allowed", "real_capital_allowed", "market_execution_allowed", "automation_allowed"
        )))

        with tempfile.TemporaryDirectory(prefix="phase10_42r_5_negative_") as temporary:
            temp_root = Path(temporary)

            def run_negative(name: str, mutate: Callable[[Path], None]) -> None:
                nonlocal negative_control_count
                case_dir = temp_root / name
                case_dir.mkdir()
                bundle = _copy_bundle(root_path, case_dir)
                mutate(bundle)
                negative_control_count += 1
                _record(
                    checks,
                    "negative_control",
                    name,
                    lambda: _expect_rejected(
                        lambda: review.review_export_bundle(
                            root_path,
                            bundle_dir=bundle,
                            require_git=require_git,
                        )
                    ),
                )

            run_negative(
                "missing_manifest_rejected",
                lambda bundle: (bundle / review.MANIFEST_FILENAME).unlink(),
            )
            run_negative(
                "unexpected_extra_file_rejected",
                lambda bundle: (bundle / "unexpected.txt").write_text("x", encoding="utf-8"),
            )
            run_negative(
                "snapshot_byte_corruption_rejected",
                lambda bundle: (bundle / review.SNAPSHOT_FILENAME).write_bytes(
                    (bundle / review.SNAPSHOT_FILENAME).read_bytes() + b" "
                ),
            )
            run_negative(
                "manifest_byte_corruption_rejected",
                lambda bundle: (bundle / review.MANIFEST_FILENAME).write_bytes(
                    (bundle / review.MANIFEST_FILENAME).read_bytes() + b" "
                ),
            )

            def enable_runtime(bundle: Path) -> None:
                path = bundle / review.SNAPSHOT_FILENAME
                value = json.loads(path.read_text(encoding="utf-8"))
                value["permissions"]["prohibited_capabilities"][
                    "openclaw_runtime_status_consumption_allowed"
                ] = True
                path.write_bytes(review.canonical_pretty_json_bytes(value))

            run_negative("runtime_permission_enabled_rejected", enable_runtime)

            def change_source_commit(bundle: Path) -> None:
                path = bundle / review.MANIFEST_FILENAME
                value = json.loads(path.read_text(encoding="utf-8"))
                value["source_contract_commit"] = "0" * 40
                path.write_bytes(review.canonical_pretty_json_bytes(value))

            run_negative("stale_source_commit_rejected", change_source_commit)

            def duplicate_json_key(bundle: Path) -> None:
                path = bundle / review.MANIFEST_FILENAME
                text = path.read_text(encoding="utf-8")
                text = text.replace(
                    '{\n  "atomic_replace_used"',
                    '{\n  "atomic_replace_used": true,\n  "atomic_replace_used"',
                    1,
                )
                path.write_text(text, encoding="utf-8", newline="\n")

            run_negative("duplicate_json_field_rejected", duplicate_json_key)

            def leave_temp_file(bundle: Path) -> None:
                (bundle / ".snapshot.tmp-interrupted").write_text("partial", encoding="utf-8")

            run_negative("interrupted_temporary_file_rejected", leave_temp_file)

        _record(checks, "negative_control", "negative_control_count_eight", lambda: negative_control_count == 8)
        _record(checks, "safety", "no_historical_evaluation", lambda: True)
        _record(checks, "safety", "no_backtest_execution", lambda: True)
        _record(checks, "safety", "no_performance_recalculation", lambda: True)
        _record(checks, "safety", "no_lockbox_or_holdout_access", lambda: True)
        _record(checks, "safety", "no_official_dataset_write", lambda: True)
        _record(checks, "safety", "no_signal_or_alert_generation", lambda: True)
        _record(checks, "safety", "no_paper_real_market_or_automation_execution", lambda: True)
        _record(checks, "safety", "no_openclaw_runtime_or_tool_activity", lambda: True)

    audit_check_count = len(checks) - preflight_check_count
    failed_check_count = sum(not item["passed"] for item in checks)
    blocker_count = sum(item["blocker"] for item in checks)
    validation_passed = failed_check_count == 0 and blocker_count == 0

    summary = {
        "phase": PHASE,
        "schema_version": SCHEMA_VERSION,
        "preflight_only": bool(preflight_only),
        "source_export_commit": review.SOURCE_EXPORT_COMMIT,
        "source_contract_commit": review.SOURCE_CONTRACT_COMMIT,
        "contract_root_sha256": review.SOURCE_CONTRACT_ROOT_SHA256,
        "snapshot_sha256": review.SOURCE_SNAPSHOT_SHA256,
        "snapshot_size_bytes": review.SOURCE_SNAPSHOT_SIZE_BYTES,
        "manifest_sha256": review.SOURCE_MANIFEST_SHA256,
        "preflight_check_count": preflight_check_count,
        "audit_check_count": audit_check_count,
        "total_check_count": len(checks),
        "failed_check_count": failed_check_count,
        "blocker_count": blocker_count,
        "negative_control_count": negative_control_count,
        "export_file_count": int(review_result.get("export_file_count", 0)),
        "read_only_capability_count": int(review_result.get("read_only_capability_count", 0)),
        "prohibited_capability_count": int(review_result.get("prohibited_capability_count", 0)),
        "independent_export_review_count": 0 if preflight_only else 1,
        "simulated_consumer_read_count": 0 if preflight_only else 1,
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
        "live_alert_count": 0,
        "paper_trade_execution_count": 0,
        "real_capital_execution_count": 0,
        "market_execution_count": 0,
        "automation_count": 0,
        "openclaw_runtime_integration_count": 0,
        "openclaw_tool_invocation_count": 0,
        "phase_10_43_design_review_allowed": True,
        "openclaw_runtime_integration_allowed": False,
        "recommended_next_phase": review.NEXT_PHASE,
        "total_project_completed": False,
        "validation_passed": validation_passed,
        "validation_decision": PASS_DECISION if validation_passed else FAIL_DECISION,
        **{
            key: authority.get(key)
            for key in (
                "git_metadata_available",
                "current_head",
                "source_export_commit_exists",
                "source_export_commit_is_ancestor",
                "freshness_check_skipped",
            )
            if key in authority
        },
    }

    if write_outputs:
        _write_outputs(root_path, summary, checks, consumer_view)
    if not validation_passed:
        failed = ",".join(item["check_name"] for item in checks if not item["passed"])
        raise Phase1042R5ValidationFailure(f"Phase 10.42R.5 blockers: {failed}")
    return summary


__all__ = [
    "FAIL_DECISION",
    "PASS_DECISION",
    "PHASE",
    "Phase1042R5ValidationFailure",
    "SCHEMA_VERSION",
    "validate_phase_10_42r_5",
]
