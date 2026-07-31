from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

from src.integration.openclaw_read_only_local_connection_v1 import (
    OFFICIAL_DATASET_PATH,
    OFFICIAL_MANIFEST_PATH,
)


PHASE = "11.2"
VALIDATION_SCHEMA_VERSION = (
    "OPENCLAW_READ_ONLY_END_TO_END_RUNBOOK_AND_RECOVERY_VALIDATION_V1"
)
VALIDATED_DECISION = (
    "PHASE_11_2_OPENCLAW_READ_ONLY_END_TO_END_RUNBOOK_AND_RECOVERY_VALIDATED"
)
FAILED_DECISION = (
    "PHASE_11_2_OPENCLAW_READ_ONLY_END_TO_END_RUNBOOK_AND_RECOVERY_FAILED"
)
EXPECTED_CONNECTION_DECISION = (
    "CURRENT_VALIDATED_RESEARCH_STATUS_CONNECTED_FOR_HUMAN_EXPLANATION_ONLY"
)
EXPECTED_OPENCLAW_EVIDENCE_DECISION = (
    "FIRST_CONTROLLED_OPENCLAW_READ_ONLY_EXECUTION_PASSED"
)
EXPECTED_OPENCLAW_COMMAND = (
    r"C:\Users\jmcas\OpenClawProjects\trading-ai\.venv\Scripts\python.exe "
    "-m src.workflows.run_openclaw_read_only_local_connection_v1"
)
RUNBOOK_PATH = Path(
    "docs/PHASE_11_2_OPENCLAW_READ_ONLY_END_TO_END_RUNBOOK_AND_RECOVERY_V1.md"
)
OPENCLAW_EVIDENCE_PATH = Path(
    "reports/phase_11_1/first_controlled_openclaw_read_only_execution.json"
)
WORKFLOW_MODULE = "src.workflows.run_openclaw_read_only_local_connection_v1"
ACTIONABLE_KEYS = {
    "entry",
    "entry_price",
    "stop",
    "stop_loss",
    "target",
    "take_profit",
    "position_size",
    "quantity",
    "leverage",
    "side",
    "signal",
    "order",
    "exchange_command",
}
REQUIRED_FALSE_RESTRICTIONS = {
    "other_openclaw_tool_invocation_allowed",
    "official_dataset_write_allowed",
    "openclaw_operational_integration_allowed",
    "signal_generation_enabled",
    "paper_trade_execution_allowed",
    "real_capital_allowed",
    "market_execution_allowed",
    "automation_allowed",
}
EVIDENCE_REQUIRED_FALSE_RESTRICTIONS = {
    "actionable_trading_fields_present",
    "automation_allowed",
    "market_execution_allowed",
    "official_dataset_write_allowed",
    "openclaw_operational_integration_allowed",
    "paper_trade_execution_allowed",
    "real_capital_allowed",
    "signal_generation_enabled",
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _collect_keys(value: Any) -> set[str]:
    keys: set[str] = set()
    if isinstance(value, dict):
        for key, nested in value.items():
            keys.add(str(key).lower())
            keys.update(_collect_keys(nested))
    elif isinstance(value, list):
        for nested in value:
            keys.update(_collect_keys(nested))
    return keys


def _check(name: str, passed: bool, details: str) -> dict[str, Any]:
    return {
        "check_name": name,
        "passed": bool(passed),
        "details": details,
        "blocker": not bool(passed),
    }


def _run(
    module: str,
    *,
    cwd: Path,
    extra_args: list[str] | None = None,
) -> subprocess.CompletedProcess[str]:
    command = [sys.executable, "-m", module]
    if extra_args:
        command.extend(extra_args)
    return subprocess.run(
        command,
        cwd=cwd,
        text=True,
        capture_output=True,
        check=False,
        shell=False,
    )


def _copy_isolated_runtime(root: Path, destination: Path) -> None:
    required_directories = (
        Path("src"),
        Path("data/forward"),
        Path("reports/phase_10_42r_4"),
    )
    for relative in required_directories:
        source = root / relative
        if not source.is_dir():
            raise FileNotFoundError(f"Missing isolated runtime source: {relative}")
        shutil.copytree(source, destination / relative)


def validate_phase_11_2(root: Path | str = Path(".")) -> dict[str, Any]:
    root_path = Path(root).resolve()
    checks: list[dict[str, Any]] = []

    dataset_path = root_path / OFFICIAL_DATASET_PATH
    manifest_path = root_path / OFFICIAL_MANIFEST_PATH
    runbook_path = root_path / RUNBOOK_PATH
    evidence_path = root_path / OPENCLAW_EVIDENCE_PATH

    checks.append(_check("runbook_exists", runbook_path.is_file(), str(runbook_path)))
    runbook_text = runbook_path.read_text(encoding="utf-8") if runbook_path.is_file() else ""
    checks.append(
        _check(
            "runbook_contains_exact_workflow",
            WORKFLOW_MODULE in runbook_text,
            WORKFLOW_MODULE,
        )
    )
    checks.append(
        _check(
            "runbook_contains_exact_openclaw_command",
            EXPECTED_OPENCLAW_COMMAND in runbook_text,
            EXPECTED_OPENCLAW_COMMAND,
        )
    )
    checks.append(_check("official_dataset_exists", dataset_path.is_file(), str(dataset_path)))
    checks.append(_check("official_manifest_exists", manifest_path.is_file(), str(manifest_path)))
    checks.append(_check("openclaw_evidence_exists", evidence_path.is_file(), str(evidence_path)))

    evidence: dict[str, Any] = {}
    evidence_error = ""
    if evidence_path.is_file():
        try:
            evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            evidence_error = str(exc)
    checks.append(_check("openclaw_evidence_valid_json", not evidence_error, evidence_error))
    checks.append(
        _check(
            "openclaw_evidence_decision_expected",
            evidence.get("decision") == EXPECTED_OPENCLAW_EVIDENCE_DECISION,
            str(evidence.get("decision", "")),
        )
    )
    checks.append(
        _check(
            "openclaw_evidence_exact_command",
            evidence.get("command") == EXPECTED_OPENCLAW_COMMAND,
            str(evidence.get("command", "")),
        )
    )
    checks.append(_check("openclaw_evidence_agent", evidence.get("agent") == "trading-ai", str(evidence.get("agent", ""))))
    checks.append(_check("openclaw_evidence_provider", evidence.get("provider") == "openai", str(evidence.get("provider", ""))))
    checks.append(_check("openclaw_evidence_model", evidence.get("model") == "gpt-5.6-sol", str(evidence.get("model", ""))))
    checks.append(_check("openclaw_evidence_one_tool_call", evidence.get("tool_calls") == 1, repr(evidence.get("tool_calls"))))
    checks.append(_check("openclaw_evidence_zero_tool_failures", evidence.get("tool_failures") == 0, repr(evidence.get("tool_failures"))))
    checks.append(_check("openclaw_evidence_exec_only", evidence.get("tools_used") == ["exec"], repr(evidence.get("tools_used"))))
    evidence_restrictions = evidence.get("restrictions", {}) if isinstance(evidence, dict) else {}
    for key in sorted(EVIDENCE_REQUIRED_FALSE_RESTRICTIONS):
        checks.append(
            _check(
                f"openclaw_evidence_restriction_false__{key}",
                evidence_restrictions.get(key) is False,
                repr(evidence_restrictions.get(key)),
            )
        )
    checks.append(
        _check(
            "openclaw_evidence_human_explanation_only",
            evidence_restrictions.get("human_explanation_only") is True,
            repr(evidence_restrictions.get("human_explanation_only")),
        )
    )

    dataset_before = _sha256(dataset_path) if dataset_path.is_file() else ""
    manifest_before = _sha256(manifest_path) if manifest_path.is_file() else ""

    success = _run(WORKFLOW_MODULE, cwd=root_path)
    checks.append(_check("workflow_exit_code_zero", success.returncode == 0, str(success.returncode)))
    checks.append(_check("workflow_stderr_empty", success.stderr.strip() == "", success.stderr.strip()))

    payload: dict[str, Any] = {}
    parse_error = ""
    try:
        payload = json.loads(success.stdout)
    except json.JSONDecodeError as exc:
        parse_error = str(exc)
    checks.append(_check("workflow_stdout_valid_json", not parse_error, parse_error))
    checks.append(
        _check(
            "connection_decision_expected",
            payload.get("decision") == EXPECTED_CONNECTION_DECISION,
            str(payload.get("decision", "")),
        )
    )

    restrictions = payload.get("restrictions", {}) if isinstance(payload, dict) else {}
    for key in sorted(REQUIRED_FALSE_RESTRICTIONS):
        checks.append(
            _check(
                f"restriction_false__{key}",
                restrictions.get(key) is False,
                repr(restrictions.get(key)),
            )
        )

    human_review = payload.get("human_review", {}) if isinstance(payload, dict) else {}
    checks.append(
        _check(
            "human_review_required",
            human_review.get("required") is True,
            repr(human_review.get("required")),
        )
    )

    all_keys = _collect_keys(payload)
    actionable_present = sorted(ACTIONABLE_KEYS.intersection(all_keys))
    checks.append(
        _check(
            "actionable_fields_absent",
            not actionable_present,
            ",".join(actionable_present),
        )
    )

    dataset_after = _sha256(dataset_path) if dataset_path.is_file() else ""
    manifest_after = _sha256(manifest_path) if manifest_path.is_file() else ""
    checks.append(_check("dataset_unchanged", dataset_before == dataset_after, dataset_after))
    checks.append(_check("manifest_unchanged", manifest_before == manifest_after, manifest_after))

    extra_argument = _run(WORKFLOW_MODULE, cwd=root_path, extra_args=["--not-allowed"])
    checks.append(
        _check(
            "extra_argument_fails_closed",
            extra_argument.returncode == 20,
            str(extra_argument.returncode),
        )
    )

    isolated_error = ""
    tampered_return_code: int | None = None
    tampered_stderr = ""
    try:
        with tempfile.TemporaryDirectory(prefix="phase_11_2_") as temp_dir:
            isolated_root = Path(temp_dir) / "repo"
            isolated_root.mkdir(parents=True)
            _copy_isolated_runtime(root_path, isolated_root)
            isolated_dataset = isolated_root / OFFICIAL_DATASET_PATH
            isolated_dataset.write_bytes(isolated_dataset.read_bytes() + b"tamper\n")
            tampered = _run(WORKFLOW_MODULE, cwd=isolated_root)
            tampered_return_code = tampered.returncode
            tampered_stderr = tampered.stderr.strip()
    except Exception as exc:
        isolated_error = f"{type(exc).__name__}: {exc}"

    checks.append(_check("isolated_recovery_test_prepared", not isolated_error, isolated_error))
    checks.append(
        _check(
            "tampered_dataset_fails_closed",
            tampered_return_code == 1,
            repr(tampered_return_code),
        )
    )
    checks.append(
        _check(
            "tampered_failure_reports_closed_decision",
            "LOCAL_READ_ONLY_CONNECTION_FAILED_CLOSED" in tampered_stderr,
            tampered_stderr,
        )
    )

    failed = [row for row in checks if not row["passed"]]
    validation_passed = not failed

    return {
        "phase": PHASE,
        "validation_schema_version": VALIDATION_SCHEMA_VERSION,
        "validation_passed": validation_passed,
        "validation_decision": VALIDATED_DECISION if validation_passed else FAILED_DECISION,
        "total_checks": len(checks),
        "passed_checks": len(checks) - len(failed),
        "failed_checks": len(failed),
        "blocker_count": len(failed),
        "mvp_read_only_completed": validation_passed,
        "local_auxiliary_model_integrated": False,
        "official_dataset_write_allowed": False,
        "signal_generation_enabled": False,
        "paper_trade_execution_allowed": False,
        "real_capital_allowed": False,
        "market_execution_allowed": False,
        "automation_allowed": False,
        "recommended_next_phase": "PHASE_11_3_LOCAL_AUXILIARY_MODEL_ROUTING_V1",
        "checks": checks,
    }


__all__ = [
    "FAILED_DECISION",
    "VALIDATED_DECISION",
    "validate_phase_11_2",
]
