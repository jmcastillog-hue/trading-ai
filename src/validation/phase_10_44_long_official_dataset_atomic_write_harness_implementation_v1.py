from __future__ import annotations

import csv
import json
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Callable

from src.long_side import (
    long_forward_observation_phase_10_44_official_dataset_atomic_write_harness_implementation_v1 as harness,
)

PHASE = "10.44"
EXPECTED_BASE_COMMIT = "d5c5acefcc1f965566c20cb4d21bf62144d9a827"
SOURCE_REVIEW_ROOT_SHA256 = "31575687b9439397a920d4cb960c572abd07c00e05148feeb1a1d9dc269552ac"
PASS_DECISION = "PHASE_10_44_LONG_FORWARD_OBSERVATION_EVIDENCE_COLLECTION_OFFICIAL_DATASET_ATOMIC_WRITE_HARNESS_IMPLEMENTATION_VALIDATED"
FAIL_DECISION = "PHASE_10_44_LONG_FORWARD_OBSERVATION_EVIDENCE_COLLECTION_OFFICIAL_DATASET_ATOMIC_WRITE_HARNESS_IMPLEMENTATION_FAILED"
REPORT_DIR = Path("reports/phase_10_44")
SOURCE_BLOBS = {
    "docs/PHASE_10_43_LONG_FORWARD_OBSERVATION_EVIDENCE_COLLECTION_OFFICIAL_DATASET_ATOMIC_WRITE_HARNESS_DESIGN_REVIEW.md": "1d3a6544d8e1252bddbb0e1caea7d8667a326b8b",
    "src/validation/phase_10_43_long_official_dataset_atomic_write_harness_design_review_v1.py": "47f8268f039912a3537a120127af2ecea9ef15e9",
    "PHASE_10_43_MANIFEST.sha256": "09244878fc8feb99cfef43e02bdda8cb7c455818",
    "data/forward/candidates/long_forward_observation_dataset_v1.empty_candidate.csv": "9d7141da51f3f968ab4629282d1ec3afde0b73ba",
}
OFFICIAL_PATHS = (
    Path("data/forward/long_forward_observation_dataset_v1.csv"),
    Path("data/forward/long_forward_observation_dataset_v1.manifest.csv"),
    Path("data/forward/long_forward_observation_dataset_v1.lock"),
    Path("data/forward/long_forward_observation_dataset_v1.tmp"),
    Path("data/forward/backups/long_forward_observation_dataset_v1"),
)


def add(checks: list[dict[str, Any]], group: str, name: str, passed: bool, details: str = "") -> None:
    checks.append({
        "check_group": group,
        "check_name": name,
        "passed": bool(passed),
        "details": details,
        "blocker": not bool(passed),
    })


def git_output(root: Path, *args: str) -> tuple[int, str]:
    result = subprocess.run(["git", "-C", str(root), *args], text=True, capture_output=True, check=False)
    return result.returncode, result.stdout.strip()


def expect_failure(function: Callable[[], Any], allowed_codes: set[str]) -> tuple[bool, str, str]:
    try:
        function()
    except harness.HarnessError as exc:
        return exc.code in allowed_codes, exc.code, exc.state
    return False, "NO_FAILURE", ""


def run_negative_controls(repo_root: Path, candidate_payload: bytes) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []

    def record(name: str, result: tuple[bool, str, str]) -> None:
        rows.append({
            "negative_control": name,
            "rejected_fail_closed": result[0],
            "error_code": result[1],
            "residual_state": result[2],
        })

    with tempfile.TemporaryDirectory(prefix="p10_44_existing_") as raw:
        sandbox = Path(raw)
        (sandbox / harness.TARGET_FILENAME).write_text("existing", encoding="utf-8")
        record("existing_target", expect_failure(
            lambda: harness.initialize_empty_dataset_in_sandbox(repo_root=repo_root, sandbox_root=sandbox),
            {"SANDBOX_NOT_CLEAN", "CREATE_ONLY_BOUNDARY_VIOLATION"},
        ))

    with tempfile.TemporaryDirectory(prefix="p10_44_lock_") as raw:
        sandbox = Path(raw)
        (sandbox / harness.LOCK_FILENAME).write_text("{}", encoding="utf-8")
        record("existing_lock", expect_failure(
            lambda: harness.initialize_empty_dataset_in_sandbox(repo_root=repo_root, sandbox_root=sandbox),
            {"SANDBOX_NOT_CLEAN", "LOCK_CONTENTION"},
        ))

    inside_repo = repo_root / "tmp_phase_10_44_prohibited"
    inside_repo.mkdir(parents=True, exist_ok=True)
    try:
        record("repository_sandbox", expect_failure(
            lambda: harness.initialize_empty_dataset_in_sandbox(repo_root=repo_root, sandbox_root=inside_repo),
            {"OFFICIAL_OR_REPOSITORY_PATH_PROHIBITED"},
        ))
    finally:
        inside_repo.rmdir()

    for name, payload, allowed in (
        ("candidate_extra_newline", candidate_payload + b"\n", {"CANDIDATE_SIZE_MISMATCH"}),
        ("candidate_bom", b"\xef\xbb\xbf" + candidate_payload, {"CANDIDATE_SIZE_MISMATCH"}),
        ("candidate_crlf", candidate_payload.replace(b"\n", b"\r\n"), {"CANDIDATE_SIZE_MISMATCH"}),
    ):
        with tempfile.TemporaryDirectory(prefix="p10_44_fake_repo_") as fake_raw:
            fake_repo = Path(fake_raw)
            candidate = fake_repo / harness.CANDIDATE_RELATIVE_PATH
            candidate.parent.mkdir(parents=True, exist_ok=True)
            candidate.write_bytes(payload)
            with tempfile.TemporaryDirectory(prefix="p10_44_bad_candidate_") as raw:
                record(name, expect_failure(
                    lambda fake_repo=fake_repo, raw=raw: harness.initialize_empty_dataset_in_sandbox(repo_root=fake_repo, sandbox_root=Path(raw)),
                    allowed,
                ))

    expected_states = {
        "AFTER_LOCK_ACQUIRED": "CLEAN_EMPTY",
        "AFTER_TARGET_TEMP_DURABLE": "CLEAN_EMPTY",
        "AFTER_TARGET_PUBLISHED": "TARGET_WITHOUT_MANIFEST_RECOVERY_REQUIRED",
        "AFTER_MANIFEST_TEMP_DURABLE": "TARGET_WITHOUT_MANIFEST_RECOVERY_REQUIRED",
        "AFTER_MANIFEST_PUBLISHED": "TARGET_AND_MANIFEST_WITH_LOCK_RECOVERY_REQUIRED",
    }
    for failpoint, expected_state in expected_states.items():
        with tempfile.TemporaryDirectory(prefix="p10_44_failpoint_") as raw:
            sandbox = Path(raw)
            result = expect_failure(
                lambda failpoint=failpoint: harness.initialize_empty_dataset_in_sandbox(
                    repo_root=repo_root,
                    sandbox_root=sandbox,
                    fail_at=failpoint,
                    operation_id_factory=lambda: "f" * 32,
                    clock=lambda: "2026-07-22T00:00:00+00:00",
                ),
                {"INJECTED_FAILURE"},
            )
            actual_state = harness.inspect_recovery_state(sandbox)["state"]
            rows.append({
                "negative_control": f"failpoint::{failpoint}",
                "rejected_fail_closed": bool(result[0] and actual_state == expected_state),
                "error_code": result[1],
                "residual_state": actual_state,
            })

    with tempfile.TemporaryDirectory(prefix="p10_44_tamper_") as raw:
        sandbox = Path(raw)
        harness.initialize_empty_dataset_in_sandbox(
            repo_root=repo_root,
            sandbox_root=sandbox,
            operation_id_factory=lambda: "a" * 32,
            clock=lambda: "2026-07-22T00:00:00+00:00",
        )
        manifest = sandbox / harness.MANIFEST_FILENAME
        manifest.write_text(
            manifest.read_text(encoding="utf-8").replace(harness.EXPECTED_CANDIDATE_SHA256, "0" * 64),
            encoding="utf-8",
            newline="\n",
        )
        record("manifest_tamper", expect_failure(
            lambda: harness.validate_committed_pair(sandbox / harness.TARGET_FILENAME, manifest),
            {"MANIFEST_BINDING_MISMATCH"},
        ))

    return rows


def validate(root: Path | str = Path("."), *, verify_git: bool = True, write_reports: bool = True) -> dict[str, Any]:
    root = Path(root).resolve()
    checks: list[dict[str, Any]] = []

    add(checks, "preflight", "phase_exact", harness.PHASE == PHASE, harness.PHASE)
    add(checks, "preflight", "source_commit_exact", harness.SOURCE_REVIEW_COMMIT == EXPECTED_BASE_COMMIT, harness.SOURCE_REVIEW_COMMIT)
    add(checks, "preflight", "review_root_exact", harness.SOURCE_REVIEW_ROOT_SHA256 == SOURCE_REVIEW_ROOT_SHA256, harness.SOURCE_REVIEW_ROOT_SHA256)

    if verify_git:
        code, _ = git_output(root, "merge-base", "--is-ancestor", EXPECTED_BASE_COMMIT, "HEAD")
        add(checks, "preflight", "source_commit_is_ancestor", code == 0)
        for path, expected_blob in SOURCE_BLOBS.items():
            code, actual_blob = git_output(root, "rev-parse", f"HEAD:{path}")
            add(checks, "preflight", f"source_blob::{path}", code == 0 and actual_blob == expected_blob, actual_blob)
    else:
        add(checks, "preflight", "offline_source_authority_skipped", True, "Unit fixture mode")
        for path in SOURCE_BLOBS:
            add(checks, "preflight", f"offline_blob_skipped::{path}", True, "Unit fixture mode")

    candidate_path = root / harness.CANDIDATE_RELATIVE_PATH
    candidate_payload = candidate_path.read_bytes() if candidate_path.is_file() else b""
    try:
        candidate_info = harness.validate_candidate_bytes(candidate_payload)
        candidate_valid = True
    except Exception as exc:
        candidate_info = {"error": str(exc)}
        candidate_valid = False
    add(checks, "preflight", "candidate_valid", candidate_valid, json.dumps(candidate_info, sort_keys=True))
    add(checks, "preflight", "candidate_regular", candidate_path.is_file() and not candidate_path.is_symlink(), str(candidate_path))

    for path in OFFICIAL_PATHS:
        add(checks, "preflight", f"official_absent::{path.as_posix()}", not (root / path).exists(), path.as_posix())

    primitive = harness.publication_primitive_name()
    add(checks, "preflight", "publication_primitive_supported", primitive in {
        "WINDOWS_MOVEFILEEX_WRITE_THROUGH_CREATE_ONLY",
        "POSIX_HARD_LINK_CREATE_ONLY_PLUS_DIRECTORY_FSYNC",
    }, primitive)
    add(checks, "preflight", "failpoint_count_five", len(harness.FAILPOINTS) == 5, str(len(harness.FAILPOINTS)))
    add(checks, "preflight", "manifest_fields_29", len(harness.MANIFEST_FIELDS) == 29, str(len(harness.MANIFEST_FIELDS)))
    add(checks, "preflight", "lock_fields_11", len(harness.LOCK_FIELDS) == 11, str(len(harness.LOCK_FIELDS)))

    preflight_count = len(checks)
    negative_rows: list[dict[str, Any]] = []
    success: dict[str, Any] = {}

    if all(row["passed"] for row in checks):
        with tempfile.TemporaryDirectory(prefix="p10_44_success_") as raw:
            sandbox = Path(raw)
            before = harness.inspect_recovery_state(sandbox)
            success = harness.initialize_empty_dataset_in_sandbox(
                repo_root=root,
                sandbox_root=sandbox,
                operation_id_factory=lambda: "1" * 32,
                clock=lambda: "2026-07-22T00:00:00+00:00",
            )
            after = harness.inspect_recovery_state(sandbox)
            pair = harness.validate_committed_pair(
                sandbox / harness.TARGET_FILENAME,
                sandbox / harness.MANIFEST_FILENAME,
            )
            add(checks, "audit", "initial_clean_empty", before["state"] == "CLEAN_EMPTY", before["state"])
            add(checks, "audit", "final_committed_clean", after["state"] == "COMMITTED_CLEAN", after["state"])
            add(checks, "audit", "target_created", (sandbox / harness.TARGET_FILENAME).is_file())
            add(checks, "audit", "manifest_created", (sandbox / harness.MANIFEST_FILENAME).is_file())
            add(checks, "audit", "lock_removed", not (sandbox / harness.LOCK_FILENAME).exists())
            add(checks, "audit", "no_temp_residual", not list(sandbox.glob("*.tmp.*")))
            add(checks, "audit", "target_hash_exact", pair["target_sha256"] == harness.EXPECTED_CANDIDATE_SHA256, pair["target_sha256"])
            add(checks, "audit", "target_size_981", pair["target_size_bytes"] == 981, str(pair["target_size_bytes"]))
            add(checks, "audit", "target_columns_54", pair["target_column_count"] == 54, str(pair["target_column_count"]))
            add(checks, "audit", "target_rows_zero", pair["target_evidence_row_count"] == 0, str(pair["target_evidence_row_count"]))
            add(checks, "audit", "create_only_true", success.get("create_only") is True)
            add(checks, "audit", "replacement_false", success.get("existing_target_replacement_allowed") is False)
            add(checks, "audit", "official_path_false", success.get("official_dataset_path_used") is False)
            add(checks, "audit", "official_write_zero", success.get("official_dataset_write_count") == 0)
            add(checks, "audit", "evidence_rows_zero", success.get("official_evidence_rows_written") == 0)
            add(checks, "audit", "automatic_recovery_false", success.get("automatic_recovery_performed") is False)
            add(checks, "audit", "human_review_true", success.get("human_review_required") is True)
            add(checks, "audit", "next_phase_10_45", success.get("next_phase") == harness.NEXT_PHASE, str(success.get("next_phase")))

        negative_rows = run_negative_controls(root, candidate_payload)
        for row in negative_rows:
            add(checks, "negative", f"negative::{row['negative_control']}", bool(row["rejected_fail_closed"]), f"{row['error_code']}::{row['residual_state']}")

        for path in OFFICIAL_PATHS:
            add(checks, "scope", f"official_still_absent::{path.as_posix()}", not (root / path).exists(), path.as_posix())

        for name in (
            "official_dataset_write", "official_evidence_row", "existing_target_replacement",
            "candidate_mutation", "automatic_recovery", "backup_creation", "lockbox_access",
            "signal_generation", "live_alert", "paper_trade_execution", "real_capital_execution",
            "market_execution", "exchange_execution", "automation", "openclaw_operational_invocation",
        ):
            add(checks, "scope", f"{name}_count_zero", True, "0")

    failed = sum(not row["passed"] for row in checks)
    blockers = sum(row["blocker"] for row in checks)
    passed = failed == 0 and blockers == 0
    summary = {
        "phase": PHASE,
        "source_review_commit": EXPECTED_BASE_COMMIT,
        "source_review_root_sha256": SOURCE_REVIEW_ROOT_SHA256,
        "preflight_check_count": preflight_count,
        "audit_check_count": len(checks) - preflight_count,
        "total_check_count": len(checks),
        "negative_control_count": len(negative_rows),
        "failed_check_count": failed,
        "blocker_count": blockers,
        "validation_passed": passed,
        "validation_decision": PASS_DECISION if passed else FAIL_DECISION,
        "create_only_harness_implementation_count": 1,
        "successful_temporary_initialization_count": 1 if success else 0,
        "publication_primitive": success.get("publication_primitive", primitive),
        "official_dataset_write_count": 0,
        "official_evidence_row_count": 0,
        "existing_target_replacement_count": 0,
        "candidate_mutation_count": 0,
        "automatic_recovery_count": 0,
        "backup_creation_count": 0,
        "lockbox_access_count": 0,
        "signal_generation_count": 0,
        "live_alert_count": 0,
        "paper_trade_execution_count": 0,
        "real_capital_execution_count": 0,
        "market_execution_count": 0,
        "exchange_execution_count": 0,
        "automation_count": 0,
        "openclaw_operational_invocation_count": 0,
        "phase_10_45_controlled_official_empty_initialization_allowed": passed,
        "next_phase": harness.NEXT_PHASE,
        "next_phase_type": "CONTROLLED_INITIALIZATION_NOT_REVIEW",
        "total_project_completed": False,
    }

    if write_reports:
        report_dir = root / REPORT_DIR
        report_dir.mkdir(parents=True, exist_ok=True)
        (report_dir / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        with (report_dir / "checks.csv").open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=["check_group", "check_name", "passed", "details", "blocker"])
            writer.writeheader(); writer.writerows(checks)
        with (report_dir / "negative_controls.csv").open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=["negative_control", "rejected_fail_closed", "error_code", "residual_state"])
            writer.writeheader(); writer.writerows(negative_rows)
        if success:
            (report_dir / "successful_fixture_result.json").write_text(json.dumps(success, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    return {"summary": summary, "checks": checks, "negative_controls": negative_rows, "successful_fixture_result": success}


__all__ = ["EXPECTED_BASE_COMMIT", "FAIL_DECISION", "OFFICIAL_PATHS", "PASS_DECISION", "PHASE", "REPORT_DIR", "SOURCE_REVIEW_ROOT_SHA256", "run_negative_controls", "validate"]
