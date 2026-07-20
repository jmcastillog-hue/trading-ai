from __future__ import annotations

import copy
import csv
import hashlib
import json
import re
import subprocess
from pathlib import Path
from typing import Any, Mapping, Sequence

from src.integration import (
    openclaw_read_only_research_status_local_consumer_adapter_design_v1 as design,
)


PHASE = "10.42R.6"
SCHEMA_VERSION = "OPENCLAW_READ_ONLY_RESEARCH_STATUS_LOCAL_CONSUMER_ADAPTER_DESIGN_VALIDATION_V1"
PASS_DECISION = (
    "PHASE_10_42R_6_OPENCLAW_READ_ONLY_RESEARCH_STATUS_"
    "LOCAL_CONSUMER_ADAPTER_DESIGN_VALIDATED"
)
FAIL_DECISION = (
    "PHASE_10_42R_6_OPENCLAW_READ_ONLY_RESEARCH_STATUS_"
    "LOCAL_CONSUMER_ADAPTER_DESIGN_BLOCKED"
)
DOC_PATH = Path(
    "docs/PHASE_10_42R_6_OPENCLAW_READ_ONLY_RESEARCH_STATUS_"
    "LOCAL_CONSUMER_ADAPTER_DESIGN.md"
)
DESIGN_SCHEMA_PATH = Path(
    "schemas/openclaw_read_only_research_status_local_consumer_adapter_design_v1.schema.json"
)
DESIGN_MODULE_PATH = Path(
    "src/integration/openclaw_read_only_research_status_local_consumer_adapter_design_v1.py"
)
WORKFLOW_PATH = Path(
    "src/workflows/validate_phase_10_42r_6_openclaw_read_only_research_status_"
    "local_consumer_adapter_design.py"
)
VALIDATION_PATH = Path(
    "src/validation/phase_10_42r_6_openclaw_read_only_research_status_"
    "local_consumer_adapter_design_v1.py"
)
TEST_PATH = Path(
    "tests/test_phase_10_42r_6_openclaw_read_only_research_status_"
    "local_consumer_adapter_design.py"
)
PACKAGE_MANIFEST_PATH = Path("PHASE_10_42R_6_MANIFEST.sha256")
PACKAGE_FILES = (
    DOC_PATH,
    DESIGN_SCHEMA_PATH,
    DESIGN_MODULE_PATH,
    VALIDATION_PATH,
    WORKFLOW_PATH,
    TEST_PATH,
)
SOURCE_REVIEW_DOCUMENT_PATH = Path(
    "docs/PHASE_10_42R_5_OPENCLAW_READ_ONLY_RESEARCH_STATUS_EXPORT_"
    "INTEGRITY_AND_CONSUMER_BOUNDARY_REVIEW.md"
)
SOURCE_REVIEW_MODULE_PATH = Path(
    "src/integration/openclaw_read_only_research_status_consumer_boundary_v1.py"
)
SOURCE_REVIEW_MANIFEST_PATH = Path("PHASE_10_42R_5_MANIFEST.sha256")
REPORTS_DIR = Path("reports/phase_10_42r_6")
SUMMARY_PATH = REPORTS_DIR / "validation_summary_v1.json"
CHECKS_PATH = REPORTS_DIR / "validation_checks_v1.csv"
DESIGN_SNAPSHOT_PATH = REPORTS_DIR / "adapter_design_snapshot_v1.json"


class Phase1042R6ValidationFailure(RuntimeError):
    pass


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def normalized_text_bytes(path: Path) -> bytes:
    raw = path.read_bytes()
    if raw.startswith(b"\xef\xbb\xbf"):
        raw = raw[3:]
    return raw.replace(b"\r\n", b"\n").replace(b"\r", b"\n")


def normalized_text_sha256(path: Path) -> str:
    return sha256_bytes(normalized_text_bytes(path))


def _parse_manifest(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line:
            continue
        match = re.fullmatch(r"([0-9a-f]{64})  (.+)", line)
        if match is None:
            raise ValueError(f"Invalid manifest line: {raw_line}")
        digest, relative = match.groups()
        if relative in values:
            raise ValueError(f"Duplicate manifest path: {relative}")
        values[relative] = digest
    return values


def _git_freshness(root: Path) -> dict[str, Any]:
    def run(arguments: Sequence[str], *, allow_failure: bool = False) -> subprocess.CompletedProcess[str]:
        result = subprocess.run(
            ["git", "-C", str(root), *arguments],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        if not allow_failure and result.returncode != 0:
            raise RuntimeError(
                f"Git command failed: {' '.join(arguments)}: {result.stderr.strip()}"
            )
        return result

    head = run(["rev-parse", "HEAD"]).stdout.strip()
    exists = (
        run(
            ["cat-file", "-e", f"{design.SOURCE_REVIEW_COMMIT}^{{commit}}"],
            allow_failure=True,
        ).returncode
        == 0
    )
    ancestor = False
    if exists:
        ancestor = (
            run(
                ["merge-base", "--is-ancestor", design.SOURCE_REVIEW_COMMIT, "HEAD"],
                allow_failure=True,
            ).returncode
            == 0
        )
    if not exists or not ancestor:
        raise RuntimeError("Source review commit is missing or not an ancestor of HEAD")
    return {
        "current_head": head,
        "source_review_commit_exists": exists,
        "source_review_commit_is_ancestor": ancestor,
    }


def _json_type_matches(value: object, expected: str) -> bool:
    if expected == "object":
        return isinstance(value, Mapping)
    if expected == "array":
        return isinstance(value, list)
    if expected == "string":
        return isinstance(value, str)
    if expected == "boolean":
        return isinstance(value, bool)
    if expected == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if expected == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if expected == "null":
        return value is None
    raise ValueError(f"Unsupported JSON schema type: {expected}")


def validate_json_schema_subset(
    value: object,
    schema: Mapping[str, Any],
    *,
    location: str = "$",
) -> None:
    expected_type = schema.get("type")
    if expected_type is not None and not _json_type_matches(value, str(expected_type)):
        raise ValueError(f"{location}: type mismatch")
    if "const" in schema and value != schema["const"]:
        raise ValueError(f"{location}: const mismatch")
    if isinstance(value, Mapping):
        required = schema.get("required", [])
        if not isinstance(required, list):
            raise ValueError(f"{location}: invalid required")
        missing = [name for name in required if name not in value]
        if missing:
            raise ValueError(f"{location}: missing fields {missing}")
        properties = schema.get("properties", {})
        if not isinstance(properties, Mapping):
            raise ValueError(f"{location}: invalid properties")
        if schema.get("additionalProperties") is False:
            extras = sorted(set(value) - set(properties))
            if extras:
                raise ValueError(f"{location}: unexpected fields {extras}")
        for name, child in properties.items():
            if name in value:
                if not isinstance(child, Mapping):
                    raise ValueError(f"{location}.{name}: invalid child schema")
                validate_json_schema_subset(value[name], child, location=f"{location}.{name}")


def _build_check(group: str, name: str, passed: bool, details: str) -> dict[str, Any]:
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
        checks.append(_build_check(group, name, passed, repr(value)))
        return value
    except Exception as exc:
        checks.append(_build_check(group, name, False, f"{type(exc).__name__}: {exc}"))
        return None


def _expect_rejected(fn) -> bool:
    try:
        fn()
    except Exception:
        return True
    return False


def _write_outputs(
    root: Path,
    summary: dict[str, Any],
    checks: list[dict[str, Any]],
    adapter_design: Mapping[str, Any] | None,
) -> None:
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
    if adapter_design is not None:
        (root / DESIGN_SNAPSHOT_PATH).write_text(
            design.canonical_pretty_json(adapter_design),
            encoding="utf-8",
            newline="\n",
        )


def validate_phase_10_42r_6(
    *,
    root: Path | str = Path("."),
    preflight_only: bool = False,
    write_outputs: bool = True,
    require_source_authority: bool = True,
) -> dict[str, Any]:
    root_path = Path(root).resolve()
    checks: list[dict[str, Any]] = []

    phase_doc = root_path / DOC_PATH
    design_schema_path = root_path / DESIGN_SCHEMA_PATH
    design_module_path = root_path / DESIGN_MODULE_PATH
    package_manifest_path = root_path / PACKAGE_MANIFEST_PATH
    source_doc = root_path / SOURCE_REVIEW_DOCUMENT_PATH
    source_module = root_path / SOURCE_REVIEW_MODULE_PATH
    source_manifest_path = root_path / SOURCE_REVIEW_MANIFEST_PATH

    _record(checks, "package", "phase_document_exists", lambda: phase_doc.is_file())
    _record(checks, "package", "design_schema_exists", lambda: design_schema_path.is_file())
    _record(checks, "package", "design_module_exists", lambda: design_module_path.is_file())
    _record(checks, "package", "package_manifest_exists", lambda: package_manifest_path.is_file())
    _record(checks, "source", "source_review_document_exists", lambda: source_doc.is_file())
    _record(checks, "source", "source_review_module_exists", lambda: source_module.is_file())
    _record(checks, "source", "source_review_manifest_exists", lambda: source_manifest_path.is_file())

    if require_source_authority:
        _record(
            checks,
            "source",
            "source_review_document_hash_exact",
            lambda: normalized_text_sha256(source_doc) == design.SOURCE_REVIEW_DOCUMENT_SHA256,
        )
        _record(
            checks,
            "source",
            "source_review_module_hash_exact",
            lambda: normalized_text_sha256(source_module) == design.SOURCE_REVIEW_MODULE_SHA256,
        )
        source_manifest = _record(
            checks,
            "source",
            "source_review_manifest_parses",
            lambda: _parse_manifest(source_manifest_path),
        ) or {}
        _record(
            checks,
            "source",
            "source_review_manifest_binds_document",
            lambda: source_manifest.get(SOURCE_REVIEW_DOCUMENT_PATH.as_posix())
            == design.SOURCE_REVIEW_DOCUMENT_SHA256,
        )
        _record(
            checks,
            "source",
            "source_review_manifest_binds_module",
            lambda: source_manifest.get(SOURCE_REVIEW_MODULE_PATH.as_posix())
            == design.SOURCE_REVIEW_MODULE_SHA256,
        )
        git_state = _record(checks, "source", "source_review_commit_fresh", lambda: _git_freshness(root_path)) or {}
    else:
        _record(checks, "source", "source_review_document_hash_exact", lambda: True)
        _record(checks, "source", "source_review_module_hash_exact", lambda: True)
        _record(checks, "source", "source_review_manifest_parses", lambda: {})
        _record(checks, "source", "source_review_manifest_binds_document", lambda: True)
        _record(checks, "source", "source_review_manifest_binds_module", lambda: True)
        git_state = _record(checks, "source", "source_review_commit_fresh", lambda: {
            "current_head": "SOURCE_AUTHORITY_SKIPPED_FOR_FIXTURE",
            "source_review_commit_exists": False,
            "source_review_commit_is_ancestor": False,
        }) or {}

    package_manifest = _record(
        checks,
        "package",
        "package_manifest_inventory_exact",
        lambda: _parse_manifest(package_manifest_path),
    ) or {}
    _record(
        checks,
        "package",
        "package_manifest_paths_exact",
        lambda: set(package_manifest) == {path.as_posix() for path in PACKAGE_FILES},
    )
    _record(
        checks,
        "package",
        "package_manifest_hashes_valid",
        lambda: all(
            (root_path / relative).is_file()
            and normalized_text_sha256(root_path / relative) == digest
            for relative, digest in package_manifest.items()
        ),
    )

    adapter_design = _record(checks, "design", "adapter_design_builds", design.build_adapter_design)
    _record(
        checks,
        "design",
        "adapter_design_validates",
        lambda: design.validate_adapter_design(adapter_design) is None,
    )
    _record(
        checks,
        "design",
        "design_root_exact",
        lambda: adapter_design is not None
        and adapter_design["design_root_sha256"] == design.DESIGN_ROOT_SHA256,
    )
    schema = _record(
        checks,
        "design",
        "design_schema_parses",
        lambda: json.loads(design_schema_path.read_text(encoding="utf-8")),
    )
    _record(
        checks,
        "design",
        "design_schema_validates",
        lambda: validate_json_schema_subset(adapter_design, schema) is None,
    )
    _record(
        checks,
        "boundary",
        "design_only_true",
        lambda: adapter_design["decision_boundary"]["design_only"] is True,
    )
    _record(
        checks,
        "boundary",
        "implementation_disabled",
        lambda: adapter_design["decision_boundary"]["implementation_allowed"] is False,
    )
    _record(
        checks,
        "boundary",
        "runtime_disabled",
        lambda: adapter_design["decision_boundary"]["runtime_integration_allowed"] is False,
    )
    _record(
        checks,
        "boundary",
        "tool_registration_disabled",
        lambda: adapter_design["decision_boundary"]["tool_registration_allowed"] is False,
    )
    _record(
        checks,
        "boundary",
        "all_operational_permissions_false",
        lambda: all(value is False for value in design.OPERATIONAL_PERMISSIONS.values()),
    )
    _record(
        checks,
        "routing",
        "phase_10_43_route_preserved",
        lambda: adapter_design["next_routes"]["long_dataset_track"] == design.PHASE_10_43_ROUTE,
    )
    _record(
        checks,
        "routing",
        "next_phase_exact",
        lambda: adapter_design["next_routes"]["adapter_track"] == design.RECOMMENDED_NEXT_PHASE,
    )

    preflight_check_count = len(checks)
    preflight_failed = sum(not item["passed"] for item in checks)
    negative_control_count = 0

    source_hashes_before = (
        normalized_text_sha256(source_doc) if source_doc.is_file() else "",
        normalized_text_sha256(source_module) if source_module.is_file() else "",
    )

    if not preflight_only and preflight_failed == 0:
        _record(checks, "contract", "sample_request_validates", lambda: design.validate_request(design.sample_request()) is None)
        _record(checks, "contract", "sample_response_validates", lambda: design.validate_response(design.sample_response()) is None)
        _record(checks, "contract", "request_fields_exact", lambda: set(design.sample_request()) == set(design.REQUEST_FIELDS))
        _record(checks, "contract", "response_fields_exact", lambda: set(design.sample_response()) == set(design.RESPONSE_FIELDS))
        _record(checks, "contract", "validation_sequence_exact", lambda: tuple(adapter_design["validation_sequence"]) == design.VALIDATION_SEQUENCE)
        _record(checks, "boundary", "read_boundary_exact", lambda: adapter_design["read_boundary"] == design.READ_BOUNDARY)
        _record(checks, "boundary", "write_boundary_no_writes", lambda: all(value is False for key, value in design.WRITE_BOUNDARY.items() if key.endswith("_allowed")))
        _record(checks, "boundary", "transport_no_network_or_service", lambda: all(design.TRANSPORT_BOUNDARY[key] is False for key in ("transport_implemented_in_this_phase", "persistent_process_allowed", "network_allowed", "http_allowed", "socket_allowed", "api_server_allowed", "background_service_allowed", "openclaw_invocation_allowed", "lm_studio_invocation_allowed", "tool_registration_allowed", "shell_command_execution_allowed")))
        _record(checks, "errors", "error_registry_exit_codes_unique", lambda: len(set(design.ERROR_REGISTRY.values())) == len(design.ERROR_REGISTRY))
        _record(checks, "errors", "success_exit_code_zero", lambda: adapter_design["exit_code_contract"]["success"] == 0)
        _record(checks, "errors", "all_failure_exit_codes_nonzero", lambda: all(value != 0 for value in design.ERROR_REGISTRY.values()))
        _record(checks, "source", "source_files_unchanged", lambda: not require_source_authority or source_hashes_before == (normalized_text_sha256(source_doc), normalized_text_sha256(source_module)))

        negative_cases = []
        request_extra = design.sample_request(); request_extra["extra"] = True
        negative_cases.append(lambda value=request_extra: design.validate_request(value))
        request_operation = design.sample_request(); request_operation["operation"] = "PLACE_ORDER"
        negative_cases.append(lambda value=request_operation: design.validate_request(value))
        request_actionable = design.sample_request(); request_actionable["allow_actionable_fields"] = True
        negative_cases.append(lambda value=request_actionable: design.validate_request(value))
        request_human = design.sample_request(); request_human["require_human_review"] = False
        negative_cases.append(lambda value=request_human: design.validate_request(value))
        response_extra = design.sample_response(); response_extra["extra"] = True
        negative_cases.append(lambda value=response_extra: design.validate_response(value))
        response_entry = design.sample_response(); response_entry["research_status"]["entry_price"] = 100.0
        negative_cases.append(lambda value=response_entry: design.validate_response(value))
        response_runtime = design.sample_response(); response_runtime["restrictions"]["openclaw_runtime_status_consumption_allowed"] = True
        negative_cases.append(lambda value=response_runtime: design.validate_response(value))
        response_tool = design.sample_response(); response_tool["restrictions"]["openclaw_tool_invocation_allowed"] = True
        negative_cases.append(lambda value=response_tool: design.validate_response(value))
        design_implementation = copy.deepcopy(adapter_design); design_implementation["decision_boundary"]["implementation_allowed"] = True; design_implementation["design_root_sha256"] = design.calculate_design_root(design_implementation)
        negative_cases.append(lambda value=design_implementation: design.validate_adapter_design(value))
        design_root_bad = copy.deepcopy(adapter_design); design_root_bad["design_root_sha256"] = "0" * 64
        negative_cases.append(lambda value=design_root_bad: design.validate_adapter_design(value))

        for index, case in enumerate(negative_cases, start=1):
            _record(
                checks,
                "negative_control",
                f"negative_control_{index:02d}_rejected",
                lambda case=case: _expect_rejected(case),
            )
        negative_control_count = len(negative_cases)

        _record(
            checks,
            "design",
            "design_root_deterministic",
            lambda: design.build_adapter_design()["design_root_sha256"]
            == design.build_adapter_design()["design_root_sha256"]
            == design.DESIGN_ROOT_SHA256,
        )
        forbidden_import_pattern = re.compile(
            r"(?m)^\s*(?:from|import)\s+(?:requests|httpx|socket|subprocess|openai|binance|websocket|flask|fastapi|uvicorn)\b"
        )
        _record(
            checks,
            "source",
            "design_source_forbidden_imports_absent",
            lambda: forbidden_import_pattern.search(
                design_module_path.read_text(encoding="utf-8")
            )
            is None,
        )

    audit_check_count = len(checks) - preflight_check_count
    failed_check_count = sum(not item["passed"] for item in checks)
    blocker_count = sum(item["blocker"] for item in checks)
    validation_passed = failed_check_count == 0 and blocker_count == 0

    summary = {
        "phase": PHASE,
        "schema_version": SCHEMA_VERSION,
        "preflight_only": bool(preflight_only),
        "source_review_commit": design.SOURCE_REVIEW_COMMIT,
        "current_head": str(git_state.get("current_head", "")),
        "source_review_commit_exists": bool(git_state.get("source_review_commit_exists", False)),
        "source_review_commit_is_ancestor": bool(git_state.get("source_review_commit_is_ancestor", False)),
        "contract_root_sha256": design.SOURCE_CONTRACT_ROOT_SHA256,
        "snapshot_sha256": design.SOURCE_SNAPSHOT_SHA256,
        "manifest_sha256": design.SOURCE_MANIFEST_SHA256,
        "design_root_sha256": design.DESIGN_ROOT_SHA256,
        "preflight_check_count": preflight_check_count,
        "audit_check_count": audit_check_count,
        "total_check_count": len(checks),
        "negative_control_count": negative_control_count,
        "failed_check_count": failed_check_count,
        "blocker_count": blocker_count,
        "local_consumer_adapter_design_count": 1,
        "local_consumer_adapter_implementation_count": 0,
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
        "recommended_next_phase": design.RECOMMENDED_NEXT_PHASE,
        "total_project_completed": False,
        "validation_passed": validation_passed,
        "validation_decision": PASS_DECISION if validation_passed else FAIL_DECISION,
    }

    if write_outputs:
        _write_outputs(root_path, summary, checks, adapter_design)
    if not validation_passed:
        failed = ",".join(item["check_name"] for item in checks if not item["passed"])
        raise Phase1042R6ValidationFailure(f"Phase 10.42R.6 blockers: {failed}")
    return summary


__all__ = [
    "FAIL_DECISION",
    "PASS_DECISION",
    "PHASE",
    "Phase1042R6ValidationFailure",
    "SCHEMA_VERSION",
    "normalized_text_sha256",
    "validate_json_schema_subset",
    "validate_phase_10_42r_6",
]
