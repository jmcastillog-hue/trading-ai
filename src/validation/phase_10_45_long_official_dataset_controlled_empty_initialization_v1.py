from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from typing import Any

from src.long_side import long_forward_observation_phase_10_45_official_dataset_controlled_empty_initialization_v1 as phase

PASS_DECISION = "PHASE_10_45_GATE_A_ISOLATED_VALIDATION_PASSED"


def _git(root: Path, *args: str) -> str:
    return subprocess.run(["git", *args], cwd=root, check=True, capture_output=True, text=True).stdout.strip()


def validate(*, root: Path | str | None = None, verify_git: bool = True, write_reports: bool = True) -> dict[str, Any]:
    repo = Path(root).resolve() if root else Path(__file__).resolve().parents[2]
    controls: list[dict[str, Any]] = []
    errors: list[str] = []

    def check(name: str, value: bool, evidence: Any = "") -> None:
        controls.append({"control": name, "passed": bool(value), "evidence": str(evidence)})
        if not value:
            errors.append(name)

    preflight = phase.preflight_official(repo)
    check("candidate_hash_exact", preflight["candidate_sha256"] == phase.EXPECTED_SHA256, preflight["candidate_sha256"])
    check("candidate_bytes_exact", preflight["candidate_size_bytes"] == phase.EXPECTED_BYTES, preflight["candidate_size_bytes"])
    check("candidate_columns_exact", preflight["candidate_column_count"] == phase.EXPECTED_COLUMNS, preflight["candidate_column_count"])
    check("candidate_rows_zero", preflight["candidate_evidence_row_count"] == 0, preflight["candidate_evidence_row_count"])
    check("official_preflight_clean", preflight["state"] == "CLEAN_EMPTY", preflight["residuals"])
    check("official_write_default_false", preflight["official_write_allowed"] is False)
    check("create_only", preflight["create_only"] is True)
    check("replacement_forbidden", preflight["replacement_allowed"] is False)
    check("trading_effects_false", preflight["trading_effects"] is False)
    with tempfile.TemporaryDirectory(prefix="phase_10_45_validation_") as raw:
        sandbox = Path(raw)
        result = phase.initialize_in_isolated_directory(repo_root=repo, isolated_directory=sandbox, gate_b_authorization=phase.GATE_B_AUTHORIZATION, operation_id_factory=lambda: "a" * 32, clock=lambda: "2026-07-26T00:00:00+00:00")
        check("isolated_committed_clean", result["final_state"] == "COMMITTED_CLEAN")
        check("isolated_target_exact", result["target_sha256"] == phase.EXPECTED_SHA256)
        check("isolated_zero_rows", result["target_evidence_row_count"] == 0)
        check("isolated_no_trading", all(result[name] is False for name in ("signal_generation_enabled", "live_alerts_allowed", "paper_trade_execution_allowed", "real_capital_allowed", "market_execution_allowed", "exchange_execution_allowed", "automation_allowed", "execution_allowed")))
    if verify_git:
        changed = [line[3:] for line in _git(repo, "status", "--short").splitlines() if line]
        allowed = {"PHASE_10_45_MANIFEST.sha256", "docs/PHASE_10_45_LONG_FORWARD_OBSERVATION_EVIDENCE_COLLECTION_OFFICIAL_DATASET_CONTROLLED_EMPTY_INITIALIZATION.md", "src/long_side/long_forward_observation_phase_10_45_official_dataset_controlled_empty_initialization_v1.py", "src/validation/phase_10_45_long_official_dataset_controlled_empty_initialization_v1.py", "src/workflows/validate_phase_10_45_long_official_dataset_controlled_empty_initialization.py", "tests/test_phase_10_45_long_official_dataset_controlled_empty_initialization.py"}
        check("git_scope", set(changed).issubset(allowed), changed)
        check("git_diff_check", subprocess.run(["git", "diff", "--check"], cwd=repo).returncode == 0)
    passed = not errors
    summary = {"phase": phase.PHASE, "validation_decision": PASS_DECISION if passed else "FAILED", "validation_passed": passed, "control_count": len(controls), "passed_control_count": sum(item["passed"] for item in controls), "error_count": len(errors), "blocker_count": len(errors), "warning_count": 0, "official_initialization_executed": False, "official_dataset_write_count": 0, "network_access": False, "trading_effects": False}
    result = {"summary": summary, "controls": controls, "errors": errors}
    if write_reports:
        report_dir = repo / "reports" / "phase_10_45"
        report_dir.mkdir(parents=True, exist_ok=True)
        (report_dir / "validation_summary.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    return result


__all__ = ["PASS_DECISION", "validate"]
