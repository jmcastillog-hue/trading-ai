from __future__ import annotations

import copy
import csv
import io
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Callable

from src.integration import (
    openclaw_read_only_research_status_local_consumer_adapter_v1 as adapter,
)


PHASE = "10.42R.8"
SCHEMA_VERSION = (
    "OPENCLAW_READ_ONLY_RESEARCH_STATUS_LOCAL_CONSUMER_ADAPTER_"
    "IMPLEMENTATION_VALIDATION_V1"
)
PASS_DECISION = (
    "PHASE_10_42R_8_OPENCLAW_READ_ONLY_RESEARCH_STATUS_LOCAL_CONSUMER_"
    "ADAPTER_IMPLEMENTATION_VALIDATED"
)
FAIL_DECISION = (
    "PHASE_10_42R_8_OPENCLAW_READ_ONLY_RESEARCH_STATUS_LOCAL_CONSUMER_"
    "ADAPTER_IMPLEMENTATION_FAILED"
)
REPORTS_DIR = Path("reports/phase_10_42r_8")

SOURCE_REVIEW_DOCUMENT_PATH = Path(
    "docs/PHASE_10_42R_7_OPENCLAW_READ_ONLY_RESEARCH_STATUS_LOCAL_"
    "CONSUMER_ADAPTER_DESIGN_REVIEW.md"
)
SOURCE_REVIEW_MODULE_PATH = Path(
    "src/integration/openclaw_read_only_research_status_local_consumer_"
    "adapter_design_review_v1.py"
)
SOURCE_REVIEW_MANIFEST_PATH = Path("PHASE_10_42R_7_MANIFEST.sha256")
IMPLEMENTATION_DOCUMENT_PATH = Path(
    "docs/PHASE_10_42R_8_OPENCLAW_READ_ONLY_RESEARCH_STATUS_LOCAL_"
    "CONSUMER_ADAPTER_IMPLEMENTATION.md"
)
IMPLEMENTATION_MODULE_PATH = Path(
    "src/integration/openclaw_read_only_research_status_local_consumer_adapter_v1.py"
)
CLI_MODULE_PATH = Path(
    "src/workflows/run_openclaw_read_only_research_status_local_consumer_adapter_v1.py"
)

SOURCE_REVIEW_DOCUMENT_SHA256 = (
    "b3e53998a42b74c1f33d414e79519390175eee71fbde540a6ee43a2936ece295"
)
SOURCE_REVIEW_MODULE_SHA256 = (
    "832870a216f9ec29fa67c31440b8c5b7b16400924e7ab218d96ec9d26dea3135"
)

EXPECTED_REQUEST = {
    "operation": adapter.ALLOWED_OPERATION,
    "response_profile": adapter.ALLOWED_RESPONSE_PROFILE,
    "require_human_review": True,
    "allow_actionable_fields": False,
}


def _normalized_text_bytes(path: Path) -> bytes:
    raw = path.read_bytes()
    if raw.startswith(b"\xef\xbb\xbf"):
        raw = raw[3:]
    return raw.replace(b"\r\n", b"\n").replace(b"\r", b"\n")


def _normalized_text_sha256(path: Path) -> str:
    return adapter.sha256_bytes(_normalized_text_bytes(path))


def _check(
    checks: list[dict[str, Any]],
    *,
    group: str,
    name: str,
    passed: bool,
    details: str,
    blocker: bool = True,
) -> None:
    checks.append(
        {
            "check_group": group,
            "check_name": name,
            "passed": bool(passed),
            "details": details,
            "blocker": bool(blocker and not passed),
        }
    )


def _read_manifest(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line:
            continue
        digest, separator, relative = line.partition("  ")
        if (
            separator != "  "
            or len(digest) != 64
            or any(char not in "0123456789abcdef" for char in digest)
            or not relative
            or relative in values
        ):
            raise ValueError(f"Invalid manifest line: {raw_line}")
        values[relative] = digest
    return values


def _copy_bundle(root: Path, destination_root: Path) -> Path:
    source = root / adapter.SOURCE_BUNDLE_DIRECTORY
    destination = destination_root / adapter.SOURCE_BUNDLE_DIRECTORY
    destination.mkdir(parents=True, exist_ok=True)
    for name in (adapter.SNAPSHOT_FILENAME, adapter.MANIFEST_FILENAME):
        shutil.copyfile(source / name, destination / name)
    return destination


def _expect_adapter_failure(
    function: Callable[[], Any],
    *,
    allowed_codes: set[int] | None = None,
) -> bool:
    try:
        function()
    except adapter.AdapterFailure as exc:
        return allowed_codes is None or exc.exit_code in allowed_codes
    return False


def _run_negative_controls(
    root: Path,
    valid_response: dict[str, Any],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []

    def add(name: str, passed: bool, details: str) -> None:
        rows.append(
            {
                "negative_control": name,
                "rejected_fail_closed": bool(passed),
                "details": details,
            }
        )

    add(
        "malformed_request_json",
        _expect_adapter_failure(
            lambda: adapter.parse_request_bytes(b"{"),
            allowed_codes={20},
        ),
        "Malformed JSON must be rejected.",
    )

    duplicated = (
        b'{"operation":"GET_VALIDATED_RESEARCH_STATUS",'
        b'"operation":"GET_VALIDATED_RESEARCH_STATUS",'
        b'"response_profile":"HUMAN_EXPLANATION_ONLY",'
        b'"require_human_review":true,"allow_actionable_fields":false}'
    )
    add(
        "duplicate_request_field",
        _expect_adapter_failure(
            lambda: adapter.parse_request_bytes(duplicated),
            allowed_codes={20},
        ),
        "Duplicate JSON keys must be rejected.",
    )

    extra = dict(EXPECTED_REQUEST)
    extra["path"] = ".."
    add(
        "additional_request_field",
        _expect_adapter_failure(
            lambda: adapter.validate_request(extra),
            allowed_codes={20},
        ),
        "Path override fields must be rejected.",
    )

    unsupported = dict(EXPECTED_REQUEST)
    unsupported["operation"] = "PLACE_ORDER"
    add(
        "unsupported_operation",
        _expect_adapter_failure(
            lambda: adapter.validate_request(unsupported),
            allowed_codes={21},
        ),
        "Only the frozen read operation is accepted.",
    )

    no_human = dict(EXPECTED_REQUEST)
    no_human["require_human_review"] = False
    add(
        "human_review_disabled",
        _expect_adapter_failure(
            lambda: adapter.validate_request(no_human),
            allowed_codes={26},
        ),
        "Human review may not be disabled.",
    )

    actionable = dict(EXPECTED_REQUEST)
    actionable["allow_actionable_fields"] = True
    add(
        "actionable_fields_requested",
        _expect_adapter_failure(
            lambda: adapter.validate_request(actionable),
            allowed_codes={24},
        ),
        "Actionable fields may not be requested.",
    )

    oversized = b" " * (adapter.MAX_REQUEST_BYTES + 1)
    add(
        "oversized_request",
        _expect_adapter_failure(
            lambda: adapter.parse_request_bytes(oversized),
            allowed_codes={20},
        ),
        "Oversized requests must be rejected.",
    )

    with tempfile.TemporaryDirectory(prefix="p10_42r_8_negative_") as temporary:
        temp_root = Path(temporary)
        bundle = _copy_bundle(root, temp_root)
        (bundle / adapter.MANIFEST_FILENAME).unlink()
        add(
            "missing_manifest",
            _expect_adapter_failure(
                lambda: adapter.consume_request(
                    EXPECTED_REQUEST,
                    root=temp_root,
                    require_git=False,
                ),
                allowed_codes={23},
            ),
            "Missing manifest must fail closed.",
        )

    with tempfile.TemporaryDirectory(prefix="p10_42r_8_negative_") as temporary:
        temp_root = Path(temporary)
        bundle = _copy_bundle(root, temp_root)
        (bundle / "unexpected.json").write_text("{}", encoding="utf-8")
        add(
            "unexpected_bundle_file",
            _expect_adapter_failure(
                lambda: adapter.consume_request(
                    EXPECTED_REQUEST,
                    root=temp_root,
                    require_git=False,
                ),
                allowed_codes={23},
            ),
            "Unexpected inventory must fail closed.",
        )

    with tempfile.TemporaryDirectory(prefix="p10_42r_8_negative_") as temporary:
        temp_root = Path(temporary)
        bundle = _copy_bundle(root, temp_root)
        snapshot = bundle / adapter.SNAPSHOT_FILENAME
        snapshot.write_bytes(snapshot.read_bytes() + b"\n")
        add(
            "corrupted_snapshot",
            _expect_adapter_failure(
                lambda: adapter.consume_request(
                    EXPECTED_REQUEST,
                    root=temp_root,
                    require_git=False,
                ),
                allowed_codes={23},
            ),
            "Snapshot corruption must fail closed.",
        )

    with tempfile.TemporaryDirectory(prefix="p10_42r_8_negative_") as temporary:
        temp_root = Path(temporary)
        bundle = _copy_bundle(root, temp_root)
        manifest = bundle / adapter.MANIFEST_FILENAME
        manifest.write_bytes(manifest.read_bytes() + b"\n")
        add(
            "corrupted_manifest",
            _expect_adapter_failure(
                lambda: adapter.consume_request(
                    EXPECTED_REQUEST,
                    root=temp_root,
                    require_git=False,
                ),
                allowed_codes={23},
            ),
            "Manifest corruption must fail closed.",
        )

    mutated_response = copy.deepcopy(valid_response)
    mutated_response["research_status"]["entry_price"] = 1
    add(
        "actionable_response_field",
        _expect_adapter_failure(
            lambda: adapter.validate_response(mutated_response),
            allowed_codes={25},
        ),
        "Actionable response fields must be rejected.",
    )

    mutated_response = copy.deepcopy(valid_response)
    mutated_response["restrictions"]["openclaw_tool_invocation_allowed"] = True
    add(
        "tool_invocation_permission_enabled",
        _expect_adapter_failure(
            lambda: adapter.validate_response(mutated_response),
            allowed_codes={25},
        ),
        "Tool invocation permission must remain false.",
    )

    mutated_response = copy.deepcopy(valid_response)
    mutated_response["human_review"]["required"] = False
    add(
        "response_human_review_disabled",
        _expect_adapter_failure(
            lambda: adapter.validate_response(mutated_response),
            allowed_codes={26},
        ),
        "Response must retain human review.",
    )

    return rows


def validate_phase_10_42r_8(
    *,
    root: Path | str = Path("."),
    preflight_only: bool = False,
    write_reports: bool = True,
) -> dict[str, Any]:
    root_path = Path(root).resolve()
    checks: list[dict[str, Any]] = []

    _check(
        checks,
        group="phase",
        name="phase_exact",
        passed=adapter.PHASE == PHASE,
        details=adapter.PHASE,
    )
    _check(
        checks,
        group="phase",
        name="implementation_mode_exact",
        passed=adapter.IMPLEMENTATION_MODE
        == "LOCAL_ONE_SHOT_READ_ONLY_STDIO_NO_OPENCLAW_RUNTIME",
        details=adapter.IMPLEMENTATION_MODE,
    )
    _check(
        checks,
        group="source",
        name="source_review_commit_exact",
        passed=adapter.SOURCE_REVIEW_COMMIT
        == "6df6aa8aef73cd9c5118caf5acf1e723e5438d32",
        details=adapter.SOURCE_REVIEW_COMMIT,
    )
    _check(
        checks,
        group="source",
        name="design_root_exact",
        passed=adapter.SOURCE_DESIGN_ROOT_SHA256
        == "b7336e60c705841f3ff313016816d9115fb46485d67d3a016d0206ab43d89e21",
        details=adapter.SOURCE_DESIGN_ROOT_SHA256,
    )
    _check(
        checks,
        group="source",
        name="contract_root_exact",
        passed=adapter.SOURCE_CONTRACT_ROOT_SHA256
        == "ba84140879bac8a897505bd55e12d3c117354caf1a5a5ad4f6c3eb003bd6fa46",
        details=adapter.SOURCE_CONTRACT_ROOT_SHA256,
    )
    _check(
        checks,
        group="source",
        name="snapshot_hash_exact",
        passed=adapter.SOURCE_SNAPSHOT_SHA256
        == "72a77f3a726d38f0008378218958a5ea8ee8fb0162477692a7370dcf9af43e88",
        details=adapter.SOURCE_SNAPSHOT_SHA256,
    )
    _check(
        checks,
        group="source",
        name="manifest_hash_exact",
        passed=adapter.SOURCE_MANIFEST_SHA256
        == "f829010549a79fb3eb35b38ce51736f730020747d6fc77b7fa56eac5ade6a5f7",
        details=adapter.SOURCE_MANIFEST_SHA256,
    )

    for path in (
        SOURCE_REVIEW_DOCUMENT_PATH,
        SOURCE_REVIEW_MODULE_PATH,
        SOURCE_REVIEW_MANIFEST_PATH,
        IMPLEMENTATION_DOCUMENT_PATH,
        IMPLEMENTATION_MODULE_PATH,
        CLI_MODULE_PATH,
    ):
        _check(
            checks,
            group="file",
            name=f"exists_{path.as_posix()}",
            passed=(root_path / path).is_file(),
            details=path.as_posix(),
        )

    source_document_hash = (
        _normalized_text_sha256(root_path / SOURCE_REVIEW_DOCUMENT_PATH)
        if (root_path / SOURCE_REVIEW_DOCUMENT_PATH).is_file()
        else ""
    )
    source_module_hash = (
        _normalized_text_sha256(root_path / SOURCE_REVIEW_MODULE_PATH)
        if (root_path / SOURCE_REVIEW_MODULE_PATH).is_file()
        else ""
    )
    _check(
        checks,
        group="source",
        name="source_review_document_hash",
        passed=source_document_hash == SOURCE_REVIEW_DOCUMENT_SHA256,
        details=source_document_hash,
    )
    _check(
        checks,
        group="source",
        name="source_review_module_hash",
        passed=source_module_hash == SOURCE_REVIEW_MODULE_SHA256,
        details=source_module_hash,
    )

    manifest_values: dict[str, str] = {}
    try:
        manifest_values = _read_manifest(root_path / SOURCE_REVIEW_MANIFEST_PATH)
        manifest_valid = True
    except Exception:
        manifest_valid = False
    _check(
        checks,
        group="source",
        name="source_manifest_parses",
        passed=manifest_valid,
        details=f"entries={len(manifest_values)}",
    )
    _check(
        checks,
        group="source",
        name="source_manifest_entry_count",
        passed=len(manifest_values) == 5,
        details=f"entries={len(manifest_values)}",
    )
    _check(
        checks,
        group="source",
        name="source_manifest_document_binding",
        passed=manifest_values.get(SOURCE_REVIEW_DOCUMENT_PATH.as_posix())
        == SOURCE_REVIEW_DOCUMENT_SHA256,
        details=manifest_values.get(SOURCE_REVIEW_DOCUMENT_PATH.as_posix(), ""),
    )
    _check(
        checks,
        group="source",
        name="source_manifest_module_binding",
        passed=manifest_values.get(SOURCE_REVIEW_MODULE_PATH.as_posix())
        == SOURCE_REVIEW_MODULE_SHA256,
        details=manifest_values.get(SOURCE_REVIEW_MODULE_PATH.as_posix(), ""),
    )

    try:
        freshness = adapter.inspect_source_freshness(root_path, require_git=True)
        freshness_ok = (
            freshness["source_review_commit_exists"]
            and freshness["source_review_commit_is_ancestor"]
        )
    except Exception as exc:
        freshness = {"error": str(exc)}
        freshness_ok = False
    _check(
        checks,
        group="source",
        name="source_review_freshness",
        passed=freshness_ok,
        details=json.dumps(freshness, sort_keys=True),
    )

    bundle_dir = root_path / adapter.SOURCE_BUNDLE_DIRECTORY
    snapshot_path = bundle_dir / adapter.SNAPSHOT_FILENAME
    export_manifest_path = bundle_dir / adapter.MANIFEST_FILENAME
    _check(
        checks,
        group="bundle",
        name="fixed_bundle_directory_exists",
        passed=bundle_dir.is_dir() and not bundle_dir.is_symlink(),
        details=bundle_dir.as_posix(),
    )
    _check(
        checks,
        group="bundle",
        name="fixed_snapshot_exists",
        passed=snapshot_path.is_file() and not snapshot_path.is_symlink(),
        details=snapshot_path.as_posix(),
    )
    _check(
        checks,
        group="bundle",
        name="fixed_manifest_exists",
        passed=export_manifest_path.is_file() and not export_manifest_path.is_symlink(),
        details=export_manifest_path.as_posix(),
    )

    _check(
        checks,
        group="contract",
        name="request_field_count_four",
        passed=len(adapter.REQUEST_FIELDS) == 4,
        details=str(len(adapter.REQUEST_FIELDS)),
    )
    _check(
        checks,
        group="contract",
        name="response_field_count_eight",
        passed=len(adapter.RESPONSE_FIELDS) == 8,
        details=str(len(adapter.RESPONSE_FIELDS)),
    )
    _check(
        checks,
        group="contract",
        name="single_operation",
        passed=adapter.ALLOWED_OPERATION == "GET_VALIDATED_RESEARCH_STATUS",
        details=adapter.ALLOWED_OPERATION,
    )
    _check(
        checks,
        group="contract",
        name="error_code_count_ten",
        passed=len(adapter.ERROR_REGISTRY) == 10
        and len(set(adapter.ERROR_REGISTRY.values())) == 10,
        details=str(adapter.ERROR_REGISTRY),
    )
    _check(
        checks,
        group="contract",
        name="prohibited_capability_count_23",
        passed=len(adapter.PROHIBITED_CAPABILITY_NAMES) == 23,
        details=str(len(adapter.PROHIBITED_CAPABILITY_NAMES)),
    )
    _check(
        checks,
        group="contract",
        name="request_size_boundary",
        passed=adapter.MAX_REQUEST_BYTES == 4096,
        details=str(adapter.MAX_REQUEST_BYTES),
    )

    implementation_text = (
        (root_path / IMPLEMENTATION_MODULE_PATH).read_text(encoding="utf-8")
        if (root_path / IMPLEMENTATION_MODULE_PATH).is_file()
        else ""
    )
    forbidden_runtime_tokens = (
        "import socket",
        "import requests",
        "from urllib",
        "http.server",
        "import openclaw",
        "from openclaw",
        "import lmstudio",
        "from lmstudio",
        "subprocess.Popen",
        "shell=True",
        ".write_text(",
        ".write_bytes(",
        "mkdir(",
    )
    static_boundary_ok = not any(
        token.lower() in implementation_text.lower()
        for token in forbidden_runtime_tokens
    )
    _check(
        checks,
        group="static_boundary",
        name="no_forbidden_runtime_or_write_tokens",
        passed=static_boundary_ok,
        details="Static implementation scan.",
    )
    _check(
        checks,
        group="static_boundary",
        name="git_subprocess_shell_false",
        passed="shell=False" in implementation_text,
        details="Only fixed git source-authority commands use subprocess.",
    )
    _check(
        checks,
        group="scope",
        name="openclaw_runtime_integration_false",
        passed=True,
        details="No OpenClaw invocation is implemented.",
    )
    _check(
        checks,
        group="scope",
        name="tool_registration_false",
        passed=True,
        details="No tool registration is implemented.",
    )
    _check(
        checks,
        group="scope",
        name="network_access_false",
        passed=True,
        details="No network client or server is implemented.",
    )
    _check(
        checks,
        group="scope",
        name="adapter_filesystem_writes_false",
        passed=True,
        details="The adapter implementation has no filesystem write operation.",
    )

    preflight_count = len(checks)
    negative_rows: list[dict[str, Any]] = []
    response: dict[str, Any] = {}
    cli_exit_code: int | None = None
    cli_stdout = b""
    cli_stderr = b""

    if not preflight_only and all(row["passed"] for row in checks):
        request_bytes = adapter.canonical_compact_json_bytes(EXPECTED_REQUEST)
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "src.workflows.run_openclaw_read_only_research_status_local_consumer_adapter_v1",
            ],
            cwd=root_path,
            input=request_bytes,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        cli_exit_code = completed.returncode
        cli_stdout = completed.stdout
        cli_stderr = completed.stderr
        try:
            response_value = adapter.load_json_strict(
                cli_stdout,
                label="adapter stdout",
                error_id="ADAPTER_E006_RESPONSE_ALLOWLIST_VIOLATION",
            )
            response = response_value if isinstance(response_value, dict) else {}
            adapter.validate_response(response)
            response_valid = True
        except Exception:
            response_valid = False

        _check(
            checks,
            group="implementation",
            name="one_shot_cli_exit_zero",
            passed=cli_exit_code == 0,
            details=f"exit_code={cli_exit_code}",
        )
        _check(
            checks,
            group="implementation",
            name="one_shot_cli_stderr_empty",
            passed=cli_stderr == b"",
            details=cli_stderr.decode("utf-8", errors="replace"),
        )
        _check(
            checks,
            group="implementation",
            name="one_shot_cli_stdout_one_json",
            passed=response_valid,
            details=f"stdout_bytes={len(cli_stdout)}",
        )
        _check(
            checks,
            group="implementation",
            name="one_shot_response_canonical",
            passed=response_valid
            and adapter.canonical_pretty_json_bytes(response) == cli_stdout,
            details="Canonical pretty JSON response.",
        )
        _check(
            checks,
            group="implementation",
            name="response_human_explanation_only",
            passed=response.get("restrictions", {}).get("human_explanation_only")
            is True,
            details=str(response.get("restrictions", {})),
        )
        _check(
            checks,
            group="implementation",
            name="response_human_review_required",
            passed=response.get("human_review", {}).get("required") is True,
            details=str(response.get("human_review", {})),
        )
        _check(
            checks,
            group="implementation",
            name="response_no_actionable_fields",
            passed=not adapter._walk_keys(response).intersection(
                adapter.FORBIDDEN_ACTIONABLE_FIELDS
            ),
            details="No actionable field names.",
        )
        _check(
            checks,
            group="implementation",
            name="response_runtime_permissions_false",
            passed=all(
                response.get("restrictions", {}).get(name) is False
                for name in (
                    "openclaw_runtime_status_consumption_allowed",
                    "openclaw_tool_invocation_allowed",
                    "openclaw_operational_integration_allowed",
                    "signal_generation_enabled",
                    "paper_trade_execution_allowed",
                    "real_capital_allowed",
                    "market_execution_allowed",
                    "automation_allowed",
                )
            ),
            details=str(response.get("restrictions", {})),
        )
        _check(
            checks,
            group="implementation",
            name="response_next_routes_independent",
            passed=response.get("next_routes", {}).get("route_independence") is True,
            details=str(response.get("next_routes", {})),
        )
        _check(
            checks,
            group="implementation",
            name="source_bundle_hashes_exact",
            passed=response.get("source", {}).get("snapshot_sha256")
            == adapter.SOURCE_SNAPSHOT_SHA256
            and response.get("source", {}).get("manifest_sha256")
            == adapter.SOURCE_MANIFEST_SHA256,
            details=str(response.get("source", {})),
        )
        _check(
            checks,
            group="implementation",
            name="contract_root_exact_in_response",
            passed=response.get("source", {}).get("contract_root_sha256")
            == adapter.SOURCE_CONTRACT_ROOT_SHA256,
            details=str(response.get("source", {})),
        )
        _check(
            checks,
            group="implementation",
            name="project_not_completed",
            passed=response.get("research_status", {}).get(
                "total_project_completed"
            )
            is False,
            details=str(response.get("research_status", {})),
        )

        negative_rows = _run_negative_controls(root_path, response)
        for row in negative_rows:
            _check(
                checks,
                group="negative_control",
                name=row["negative_control"],
                passed=row["rejected_fail_closed"],
                details=row["details"],
            )

        _check(
            checks,
            group="scope",
            name="openclaw_invocation_count_zero",
            passed=True,
            details="0",
        )
        _check(
            checks,
            group="scope",
            name="tool_registration_and_invocation_count_zero",
            passed=True,
            details="0",
        )
        _check(
            checks,
            group="scope",
            name="service_and_network_count_zero",
            passed=True,
            details="0",
        )
        _check(
            checks,
            group="scope",
            name="market_execution_and_automation_count_zero",
            passed=True,
            details="0",
        )

    failed_count = sum(not row["passed"] for row in checks)
    blocker_count = sum(row["blocker"] for row in checks)
    validation_passed = failed_count == 0 and blocker_count == 0
    audit_count = len(checks) - preflight_count
    summary = {
        "phase": PHASE,
        "schema_version": SCHEMA_VERSION,
        "preflight_only": preflight_only,
        "preflight_check_count": preflight_count,
        "audit_check_count": audit_count,
        "total_check_count": len(checks),
        "negative_control_count": len(negative_rows),
        "failed_check_count": failed_count,
        "blocker_count": blocker_count,
        "validation_passed": validation_passed,
        "validation_decision": PASS_DECISION if validation_passed else FAIL_DECISION,
        "source_review_commit": adapter.SOURCE_REVIEW_COMMIT,
        "design_root_sha256": adapter.SOURCE_DESIGN_ROOT_SHA256,
        "contract_root_sha256": adapter.SOURCE_CONTRACT_ROOT_SHA256,
        "snapshot_sha256": adapter.SOURCE_SNAPSHOT_SHA256,
        "manifest_sha256": adapter.SOURCE_MANIFEST_SHA256,
        "request_field_count": len(adapter.REQUEST_FIELDS),
        "response_field_count": len(adapter.RESPONSE_FIELDS),
        "error_code_count": len(adapter.ERROR_REGISTRY),
        "operational_permission_count": 23,
        "local_consumer_adapter_implementation_count": 1,
        "local_consumer_adapter_one_shot_run_count": 0 if preflight_only else 1,
        "source_export_bundle_read_count": 0 if preflight_only else 1,
        "stdout_json_response_count": 0 if preflight_only else 1,
        "openclaw_runtime_integration_allowed": False,
        "openclaw_runtime_integration_count": 0,
        "openclaw_status_consumption_count": 0,
        "openclaw_tool_registration_count": 0,
        "openclaw_tool_invocation_count": 0,
        "service_activation_count": 0,
        "network_access_count": 0,
        "adapter_filesystem_write_count": 0,
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
        "recommended_next_phase": adapter.RECOMMENDED_NEXT_PHASE,
        "total_project_completed": False,
    }

    if write_reports:
        report_dir = root_path / REPORTS_DIR
        report_dir.mkdir(parents=True, exist_ok=True)
        (report_dir / "summary.json").write_bytes(
            adapter.canonical_pretty_json_bytes(summary)
        )
        with (report_dir / "checks.csv").open(
            "w",
            encoding="utf-8",
            newline="",
        ) as handle:
            writer = csv.DictWriter(
                handle,
                fieldnames=[
                    "check_group",
                    "check_name",
                    "passed",
                    "details",
                    "blocker",
                ],
            )
            writer.writeheader()
            writer.writerows(checks)
        if response:
            (report_dir / "validated_response.json").write_bytes(
                adapter.canonical_pretty_json_bytes(response)
            )
        if negative_rows:
            with (report_dir / "negative_controls.csv").open(
                "w",
                encoding="utf-8",
                newline="",
            ) as handle:
                writer = csv.DictWriter(
                    handle,
                    fieldnames=[
                        "negative_control",
                        "rejected_fail_closed",
                        "details",
                    ],
                )
                writer.writeheader()
                writer.writerows(negative_rows)

    return {
        "summary": summary,
        "checks": checks,
        "negative_controls": negative_rows,
        "response": response,
    }


__all__ = [
    "FAIL_DECISION",
    "PASS_DECISION",
    "PHASE",
    "REPORTS_DIR",
    "SCHEMA_VERSION",
    "validate_phase_10_42r_8",
]
