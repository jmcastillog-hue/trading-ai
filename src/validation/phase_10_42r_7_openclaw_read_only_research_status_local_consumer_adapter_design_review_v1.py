from __future__ import annotations

import copy
import csv
import json
from pathlib import Path
from typing import Any, Callable

from src.integration import openclaw_read_only_research_status_local_consumer_adapter_design_review_v1 as review

PHASE = "10.42R.7"
SCHEMA_VERSION = (
    "OPENCLAW_READ_ONLY_RESEARCH_STATUS_LOCAL_CONSUMER_ADAPTER_DESIGN_REVIEW_VALIDATION_V1"
)
DOC_PATH = Path(
    "docs/PHASE_10_42R_7_OPENCLAW_READ_ONLY_RESEARCH_STATUS_LOCAL_CONSUMER_ADAPTER_DESIGN_REVIEW.md"
)
REPORTS_DIR = Path("reports/phase_10_42r_7")
SUMMARY_PATH = REPORTS_DIR / "validation_summary_v1.json"
CHECKS_PATH = REPORTS_DIR / "validation_checks_v1.csv"
PASS_DECISION = (
    "PHASE_10_42R_7_OPENCLAW_READ_ONLY_RESEARCH_STATUS_"
    "LOCAL_CONSUMER_ADAPTER_DESIGN_REVIEW_VALIDATED"
)
FAIL_DECISION = (
    "PHASE_10_42R_7_OPENCLAW_READ_ONLY_RESEARCH_STATUS_"
    "LOCAL_CONSUMER_ADAPTER_DESIGN_REVIEW_BLOCKED"
)


class Phase1042R7ValidationFailure(RuntimeError):
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


def _rejects(fn: Callable[[], Any]) -> bool:
    try:
        fn()
    except review.AdapterDesignReviewError:
        return True
    return False


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


def validate_phase_10_42r_7(
    *,
    root: Path | str = Path("."),
    preflight_only: bool = False,
    write_outputs: bool = True,
    require_git: bool = True,
) -> dict[str, Any]:
    root_path = Path(root).resolve()
    checks: list[dict[str, Any]] = []

    source_paths = [
        review.SOURCE_MANIFEST_PATH,
        review.SOURCE_DOCUMENT_PATH,
        review.SOURCE_SCHEMA_PATH,
        review.SOURCE_MODULE_PATH,
        review.SOURCE_VALIDATION_PATH,
        review.SOURCE_WORKFLOW_PATH,
        review.SOURCE_TEST_PATH,
    ]
    for path in source_paths:
        _record(checks, "source", f"exists_{path.as_posix()}", lambda path=path: (root_path / path).is_file())

    authority = _record(
        checks,
        "source",
        "source_authority_exact",
        lambda: review.verify_source_authority(root_path, require_git=require_git),
    ) or {}
    design = _record(checks, "design", "source_design_builds", review.load_source_design)
    design_result = _record(
        checks,
        "design",
        "independent_design_review_passes",
        lambda: review.review_design_value(design),
    ) or {}
    schema = _record(
        checks,
        "schema",
        "source_schema_loads",
        lambda: json.loads((root_path / review.SOURCE_SCHEMA_PATH).read_text(encoding="utf-8")),
    )
    schema_result = _record(
        checks,
        "schema",
        "independent_schema_review_passes",
        lambda: review.review_schema_value(schema),
    ) or {}

    _record(checks, "design", "design_root_exact", lambda: design_result.get("design_root_sha256") == review.SOURCE_DESIGN_ROOT_SHA256)
    _record(checks, "design", "request_field_count_four", lambda: design_result.get("request_field_count") == 4)
    _record(checks, "design", "response_field_count_eight", lambda: design_result.get("response_field_count") == 8)
    _record(checks, "design", "validation_gate_count_eleven", lambda: design_result.get("validation_gate_count") == 11)
    _record(checks, "design", "error_code_count_ten", lambda: design_result.get("error_code_count") == 10)
    _record(checks, "permissions", "operational_permission_count_twenty_three", lambda: design_result.get("operational_permission_count") == 23)
    _record(checks, "permissions", "single_allowed_operation", lambda: design_result.get("allowed_future_operation_count") == 1)
    _record(checks, "boundary", "read_boundary_exact_two_files", lambda: design["read_boundary"] == review.READ_BOUNDARY)
    _record(checks, "boundary", "write_boundary_zero_writes", lambda: all(value is False for key, value in design["write_boundary"].items() if key != "stdout_json_response_future_only"))
    _record(checks, "boundary", "transport_not_implemented", lambda: design["transport_boundary"]["transport_implemented_in_this_phase"] is False)
    _record(checks, "boundary", "network_disabled", lambda: design["transport_boundary"]["network_allowed"] is False)
    _record(checks, "boundary", "openclaw_invocation_disabled", lambda: design["transport_boundary"]["openclaw_invocation_allowed"] is False)
    _record(checks, "boundary", "tool_registration_disabled", lambda: design["transport_boundary"]["tool_registration_allowed"] is False)
    _record(checks, "routing", "phase_10_43_preserved", lambda: design["next_routes"]["phase_10_43_design_review_allowed"] is True)
    _record(checks, "routing", "routes_independent", lambda: design["next_routes"]["route_independence"] is True)
    _record(checks, "scope", "adapter_not_implemented", lambda: design["decision_boundary"]["implementation_allowed"] is False)
    _record(checks, "scope", "runtime_not_allowed", lambda: design["decision_boundary"]["runtime_integration_allowed"] is False)
    _record(checks, "scope", "human_review_required", lambda: design["decision_boundary"]["human_review_required"] is True)
    _record(checks, "scope", "python_source_of_truth", lambda: design["decision_boundary"]["python_source_of_truth"] is True)
    _record(checks, "scope", "project_not_completed", lambda: design["total_project_completed"] is False)

    preflight_check_count = len(checks)
    preflight_failed = sum(not row["passed"] for row in checks)
    negative_control_count = 0
    full_result: dict[str, Any] = {}

    if not preflight_only and preflight_failed == 0:
        full_result = _record(
            checks,
            "review",
            "full_independent_review_passes",
            lambda: review.review_frozen_adapter_design(root_path, require_git=require_git),
        ) or {}

        negative_cases: list[tuple[str, Callable[[], Any]]] = []

        def mutated(path: tuple[str, ...], value: Any) -> dict[str, Any]:
            candidate = copy.deepcopy(design)
            target: Any = candidate
            for key in path[:-1]:
                target = target[key]
            target[path[-1]] = value
            return candidate

        negative_cases.extend([
            ("reject_altered_design_root", lambda: review.review_design_value(mutated(("design_root_sha256",), "0" * 64))),
            ("reject_implementation_enabled", lambda: review.review_design_value(mutated(("decision_boundary", "implementation_allowed"), True))),
            ("reject_runtime_enabled", lambda: review.review_design_value(mutated(("decision_boundary", "runtime_integration_allowed"), True))),
            ("reject_tool_registration_enabled", lambda: review.review_design_value(mutated(("decision_boundary", "tool_registration_allowed"), True))),
            ("reject_request_extra_field", lambda: review.review_request_value({**design["sample_request"], "symbol": "BTCUSDT"})),
            ("reject_unsupported_operation", lambda: review.review_request_value({**design["sample_request"], "operation": "PLACE_ORDER"})),
            ("reject_actionable_response_field", lambda: review.review_response_value({**design["sample_response"], "entry_price": 100.0})),
            ("reject_arbitrary_path_override", lambda: review.review_design_value(mutated(("read_boundary", "arbitrary_path_override_allowed"), True))),
            ("reject_symlink_read", lambda: review.review_design_value(mutated(("read_boundary", "symbolic_links_allowed"), True))),
            ("reject_network_enabled", lambda: review.review_design_value(mutated(("transport_boundary", "network_allowed"), True))),
            ("reject_duplicate_error_code", lambda: review.review_design_value(mutated(("error_registry", "ADAPTER_E010_INTERNAL_FAIL_CLOSED"), 20))),
            ("reject_reordered_validation_sequence", lambda: review.review_design_value(mutated(("validation_sequence",), list(reversed(review.VALIDATION_SEQUENCE))))),
        ])

        for name, fn in negative_cases:
            negative_control_count += 1
            _record(checks, "negative_control", name, lambda fn=fn: _rejects(fn))

        _record(checks, "safety", "no_source_export_bundle_reads", lambda: full_result.get("source_export_bundle_read_count") == 0)
        _record(checks, "safety", "no_simulated_consumer_reads", lambda: full_result.get("simulated_consumer_read_count") == 0)
        _record(checks, "safety", "no_adapter_implementation", lambda: full_result.get("adapter_implementation_count") == 0)
        _record(checks, "safety", "no_openclaw_runtime", lambda: full_result.get("openclaw_runtime_integration_count") == 0 and full_result.get("openclaw_status_consumption_count") == 0)
        _record(checks, "safety", "no_tools", lambda: full_result.get("openclaw_tool_registration_count") == 0 and full_result.get("openclaw_tool_invocation_count") == 0)
        _record(checks, "safety", "no_service_or_network", lambda: full_result.get("service_activation_count") == 0 and full_result.get("network_access_count") == 0)
        _record(checks, "routing", "next_route_is_local_implementation", lambda: full_result.get("recommended_next_phase") == review.RECOMMENDED_NEXT_PHASE)

    audit_check_count = len(checks) - preflight_check_count
    failed_check_count = sum(not row["passed"] for row in checks)
    blocker_count = sum(row["blocker"] for row in checks)
    validation_passed = failed_check_count == 0 and blocker_count == 0

    summary = {
        "phase": PHASE,
        "schema_version": SCHEMA_VERSION,
        "preflight_only": bool(preflight_only),
        "source_design_commit": review.SOURCE_DESIGN_COMMIT,
        "design_root_sha256": review.SOURCE_DESIGN_ROOT_SHA256,
        "contract_root_sha256": review.SOURCE_CONTRACT_ROOT_SHA256,
        "snapshot_sha256": review.SOURCE_SNAPSHOT_SHA256,
        "manifest_sha256": review.SOURCE_EXPORT_MANIFEST_SHA256,
        "preflight_check_count": preflight_check_count,
        "audit_check_count": audit_check_count,
        "total_check_count": len(checks),
        "negative_control_count": negative_control_count,
        "failed_check_count": failed_check_count,
        "blocker_count": blocker_count,
        "independent_adapter_design_review_count": 0 if preflight_only else 1,
        "request_field_count": int(design_result.get("request_field_count", 0)),
        "response_field_count": int(design_result.get("response_field_count", 0)),
        "validation_gate_count": int(design_result.get("validation_gate_count", 0)),
        "error_code_count": int(design_result.get("error_code_count", 0)),
        "operational_permission_count": int(design_result.get("operational_permission_count", 0)),
        "adapter_implementation_count": 0,
        "source_export_bundle_read_count": 0,
        "simulated_consumer_read_count": 0,
        "openclaw_runtime_integration_count": 0,
        "openclaw_status_consumption_count": 0,
        "openclaw_tool_registration_count": 0,
        "openclaw_tool_invocation_count": 0,
        "service_activation_count": 0,
        "network_access_count": 0,
        "historical_evaluation_count": 0,
        "backtest_execution_count": 0,
        "performance_metric_recalculation_count": 0,
        "candidate_comparison_count": 0,
        "candidate_ranking_count": 0,
        "winner_selection_count": 0,
        "candidate_mutation_count": 0,
        "retrospective_lockbox_access_count": 0,
        "prospective_holdout_access_count": 0,
        "official_dataset_write_count": 0,
        "signal_generation_count": 0,
        "live_alert_count": 0,
        "paper_trade_execution_count": 0,
        "real_capital_execution_count": 0,
        "market_execution_count": 0,
        "automation_count": 0,
        "phase_10_43_design_review_allowed": True,
        "openclaw_runtime_integration_allowed": False,
        "recommended_next_phase": review.RECOMMENDED_NEXT_PHASE,
        "total_project_completed": False,
        "validation_passed": validation_passed,
        "validation_decision": PASS_DECISION if validation_passed else FAIL_DECISION,
        **{key: value for key, value in authority.items() if key not in {"current_head"}},
        "current_head": authority.get("current_head", ""),
    }

    if write_outputs:
        _write_outputs(root_path, summary, checks)
    if not validation_passed:
        failed = ",".join(row["check_name"] for row in checks if not row["passed"])
        raise Phase1042R7ValidationFailure(f"Phase 10.42R.7 blockers: {failed}")
    return summary


__all__ = [
    "FAIL_DECISION",
    "PASS_DECISION",
    "PHASE",
    "Phase1042R7ValidationFailure",
    "SCHEMA_VERSION",
    "validate_phase_10_42r_7",
]
