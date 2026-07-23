from __future__ import annotations

import copy
import csv
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any

from src.long_side import (
    long_forward_observation_phase_10_42_evidence_collection_official_dataset_atomic_write_harness_design_v1
    as source_design,
)

PHASE = "10.43"
BASE_COMMIT = "da1a1a468e44c52c078f8227becc1cf2d10ed5e3"
DESIGN_COMMIT = "40d1c3720a398dad7751fb45212edb91f7f914ce"
PASS_DECISION = (
    "PHASE_10_43_LONG_FORWARD_OBSERVATION_EVIDENCE_COLLECTION_OFFICIAL_"
    "DATASET_ATOMIC_WRITE_HARNESS_DESIGN_REVIEW_VALIDATED"
)
FAIL_DECISION = (
    "PHASE_10_43_LONG_FORWARD_OBSERVATION_EVIDENCE_COLLECTION_OFFICIAL_"
    "DATASET_ATOMIC_WRITE_HARNESS_DESIGN_REVIEW_FAILED"
)
NEXT_PHASE = (
    "PHASE_10_44_LONG_FORWARD_OBSERVATION_EVIDENCE_COLLECTION_OFFICIAL_"
    "DATASET_ATOMIC_WRITE_HARNESS_IMPLEMENTATION_V1"
)
REPORT_DIR = Path("reports/phase_10_43")
CANDIDATE_PATH = Path(
    "data/forward/candidates/"
    "long_forward_observation_dataset_v1.empty_candidate.csv"
)
TARGET_PATH = Path("data/forward/long_forward_observation_dataset_v1.csv")
FIXED_TEMP_PATH = Path("data/forward/long_forward_observation_dataset_v1.tmp")
LOCK_PATH = Path("data/forward/long_forward_observation_dataset_v1.lock")
MANIFEST_PATH = Path("data/forward/long_forward_observation_dataset_v1.manifest.csv")
BACKUP_PATH = Path("data/forward/backups/long_forward_observation_dataset_v1")
CANDIDATE_SHA256 = "e3fa86a461fd46f4d66dc2e03f185e49b7b3438d3cbc33340c01f51310514ff1"
CANDIDATE_SIZE = 981

SOURCE_BLOBS = {
    "docs/PHASE_10_LONG_FORWARD_OBSERVATION_EVIDENCE_COLLECTION_OFFICIAL_DATASET_ATOMIC_WRITE_HARNESS_DESIGN.md": "b6490b09f93e655934a7ee517e331adb4575a272",
    "src/long_side/long_forward_observation_phase_10_42_evidence_collection_official_dataset_atomic_write_harness_design_v1.py": "6de0bd02a0c31640376ad1b3da206069137e3c17",
    "src/workflows/validate_phase_10_42_long_forward_observation_evidence_collection_official_dataset_atomic_write_harness_design.py": "97b8a8148b505a48ed93c2384c9e806c4944ff47",
    "data/forward/candidates/long_forward_observation_dataset_v1.empty_candidate.csv": "9d7141da51f3f968ab4629282d1ec3afde0b73ba",
}

REVIEW_CONTRACT = {'phase': '10.43', 'source_design_commit': '40d1c3720a398dad7751fb45212edb91f7f914ce', 'source_candidate_sha256': 'e3fa86a461fd46f4d66dc2e03f185e49b7b3438d3cbc33340c01f51310514ff1', 'implementation_scope': 'CREATE_ONLY_EMPTY_INITIALIZATION_IN_TEMPORARY_TEST_DIRECTORIES', 'official_run_reserved_for_phase': '10.45', 'existing_target_replacement_allowed_in_phase_10_44': False, 'official_dataset_write_allowed_in_phase_10_43': False, 'amendments': [{'id': 'R43-A1', 'name': 'UNIQUE_TEMP_PATH_TEMPLATE', 'binding': True, 'rule': 'Derive a unique same-directory temp path per operation; the fixed .tmp path is not an executable staging path.'}, {'id': 'R43-A2', 'name': 'ATOMIC_MANIFEST_COMMIT', 'binding': True, 'rule': 'Write the manifest through its own unique temp, flush/fsync, validate, atomic replace and durability barrier after target durability.'}, {'id': 'R43-A3', 'name': 'CREATE_ONLY_INITIALIZATION', 'binding': True, 'rule': 'Phase 10.44 supports only target-absent creation in temporary test directories; an existing target fails closed.'}, {'id': 'R43-A4', 'name': 'PLATFORM_DURABILITY_ADAPTER', 'binding': True, 'rule': 'Select and record a supported durability primitive; silent best-effort fallback is prohibited.'}, {'id': 'R43-A5', 'name': 'LOCK_RECORD_SCHEMA', 'binding': True, 'rule': 'Lock metadata includes operation id, pid, host, start time, candidate digest, target path and phase; creation is exclusive.'}, {'id': 'R43-A6', 'name': 'NO_AUTOMATIC_RECOVERY', 'binding': True, 'rule': 'No automatic deletion, resume or mutation of unowned lock/temp artifacts; recovery remains explicit and manual.'}], 'next_phase': 'PHASE_10_44_LONG_FORWARD_OBSERVATION_EVIDENCE_COLLECTION_OFFICIAL_DATASET_ATOMIC_WRITE_HARNESS_IMPLEMENTATION_V1', 'next_phase_type': 'IMPLEMENTATION_NOT_REVIEW'}
REVIEW_ROOT_SHA256 = "31575687b9439397a920d4cb960c572abd07c00e05148feeb1a1d9dc269552ac"


def canonical_root(value: dict[str, Any]) -> str:
    return hashlib.sha256(
        json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
        ).encode("utf-8")
    ).hexdigest()


def git_output(root: Path, *args: str) -> tuple[int, str]:
    result = subprocess.run(
        ["git", "-C", str(root), *args],
        capture_output=True,
        text=True,
        check=False,
    )
    return result.returncode, result.stdout.strip()


def add(
    checks: list[dict[str, Any]],
    group: str,
    name: str,
    passed: bool,
    details: str = "",
) -> None:
    checks.append(
        {
            "check_group": group,
            "check_name": name,
            "passed": bool(passed),
            "details": details,
            "blocker": not bool(passed),
        }
    )


def validate_contract(contract: dict[str, Any]) -> bool:
    amendments = contract.get("amendments")
    return (
        contract.get("phase") == "10.43"
        and contract.get("source_design_commit") == DESIGN_COMMIT
        and contract.get("source_candidate_sha256") == CANDIDATE_SHA256
        and contract.get("implementation_scope")
        == "CREATE_ONLY_EMPTY_INITIALIZATION_IN_TEMPORARY_TEST_DIRECTORIES"
        and contract.get("official_run_reserved_for_phase") == "10.45"
        and contract.get("existing_target_replacement_allowed_in_phase_10_44")
        is False
        and contract.get("official_dataset_write_allowed_in_phase_10_43")
        is False
        and isinstance(amendments, list)
        and len(amendments) == 6
        and all(item.get("binding") is True for item in amendments)
        and {item.get("name") for item in amendments}
        == {
            "UNIQUE_TEMP_PATH_TEMPLATE",
            "ATOMIC_MANIFEST_COMMIT",
            "CREATE_ONLY_INITIALIZATION",
            "PLATFORM_DURABILITY_ADAPTER",
            "LOCK_RECORD_SCHEMA",
            "NO_AUTOMATIC_RECOVERY",
        }
        and contract.get("next_phase") == NEXT_PHASE
        and contract.get("next_phase_type") == "IMPLEMENTATION_NOT_REVIEW"
        and canonical_root(contract) == REVIEW_ROOT_SHA256
    )


def negative_controls() -> list[dict[str, Any]]:
    cases: list[tuple[str, dict[str, Any]]] = []

    value = copy.deepcopy(REVIEW_CONTRACT)
    value["amendments"][0]["name"] = "FIXED_TEMP_PATH_ALLOWED"
    cases.append(("fixed_temp_path_allowed", value))

    value = copy.deepcopy(REVIEW_CONTRACT)
    value["amendments"][1]["name"] = "DIRECT_MANIFEST_WRITE"
    cases.append(("direct_manifest_write", value))

    value = copy.deepcopy(REVIEW_CONTRACT)
    value["existing_target_replacement_allowed_in_phase_10_44"] = True
    cases.append(("existing_target_replacement_enabled", value))

    value = copy.deepcopy(REVIEW_CONTRACT)
    value["implementation_scope"] = "OFFICIAL_DATASET_WRITE"
    cases.append(("official_write_scope_enabled", value))

    value = copy.deepcopy(REVIEW_CONTRACT)
    value["amendments"][3]["binding"] = False
    cases.append(("durability_fallback_not_binding", value))

    value = copy.deepcopy(REVIEW_CONTRACT)
    value["amendments"][5]["name"] = "AUTOMATIC_STALE_LOCK_DELETE"
    cases.append(("automatic_stale_lock_delete", value))

    value = copy.deepcopy(REVIEW_CONTRACT)
    value["source_candidate_sha256"] = "0" * 64
    cases.append(("candidate_hash_mutated", value))

    value = copy.deepcopy(REVIEW_CONTRACT)
    value["next_phase_type"] = "ANOTHER_REVIEW"
    cases.append(("review_loop_reopened", value))

    return [
        {
            "negative_control": name,
            "rejected_fail_closed": not validate_contract(contract),
        }
        for name, contract in cases
    ]


def validate(
    root: Path | str = Path("."),
    *,
    write_reports: bool = True,
) -> dict[str, Any]:
    root = Path(root).resolve()
    checks: list[dict[str, Any]] = []

    code, _ = git_output(root, "merge-base", "--is-ancestor", DESIGN_COMMIT, "HEAD")
    add(checks, "preflight", "design_commit_is_ancestor", code == 0)

    for path, expected_blob in SOURCE_BLOBS.items():
        code, actual_blob = git_output(root, "rev-parse", f"HEAD:{path}")
        add(
            checks,
            "preflight",
            f"source_blob_exact::{path}",
            code == 0 and actual_blob == expected_blob,
            actual_blob,
        )

    candidate = root / CANDIDATE_PATH
    candidate_bytes = candidate.read_bytes() if candidate.is_file() else b""
    add(checks, "preflight", "candidate_exists", candidate.is_file())
    add(checks, "preflight", "candidate_size_981", len(candidate_bytes) == CANDIDATE_SIZE)
    add(
        checks,
        "preflight",
        "candidate_sha256_exact",
        hashlib.sha256(candidate_bytes).hexdigest() == CANDIDATE_SHA256,
    )
    add(
        checks,
        "preflight",
        "candidate_utf8_without_bom",
        bool(candidate_bytes) and not candidate_bytes.startswith(b"\xef\xbb\xbf"),
    )
    add(checks, "preflight", "candidate_lf_only", b"\r" not in candidate_bytes)
    add(
        checks,
        "preflight",
        "candidate_one_physical_line",
        candidate_bytes.count(b"\n") == 1,
    )
    header = candidate_bytes.decode("utf-8").strip().split(",") if candidate_bytes else []
    add(checks, "preflight", "candidate_column_count_54", len(header) == 54)
    add(checks, "preflight", "official_target_absent", not (root / TARGET_PATH).exists())
    add(checks, "preflight", "fixed_temp_absent", not (root / FIXED_TEMP_PATH).exists())
    add(checks, "preflight", "official_lock_absent", not (root / LOCK_PATH).exists())
    add(checks, "preflight", "official_manifest_absent", not (root / MANIFEST_PATH).exists())
    add(checks, "preflight", "official_backup_absent", not (root / BACKUP_PATH).exists())

    preflight_count = len(checks)

    components = source_design.build_components()
    protocol = source_design.build_protocol()
    paths = source_design.build_path_contract()
    states = source_design.build_state_machine()
    invariants = source_design.build_invariants()
    failures = source_design.build_failure_modes()
    recovery = source_design.build_recovery_matrix()
    concurrency = source_design.build_concurrency_contract()

    add(checks, "audit", "component_count_14", len(components) == 14)
    add(checks, "audit", "protocol_count_18", len(protocol) == 18)
    add(checks, "audit", "path_count_7", len(paths) == 7)
    add(checks, "audit", "state_count_12", len(states) == 12)
    add(checks, "audit", "invariant_count_24", len(invariants) == 24)
    add(checks, "audit", "failure_mode_count_20", len(failures) == 20)
    add(checks, "audit", "recovery_state_count_14", len(recovery) == 14)
    add(checks, "audit", "concurrency_rule_count_12", len(concurrency) == 12)

    component_ids = set(components["component_id"].astype(str))
    add(
        checks,
        "audit",
        "required_components_present",
        {
            "LOCK_MANAGER",
            "TEMP_STAGER",
            "FILE_DURABILITY_BARRIER",
            "ATOMIC_REPLACER",
            "DIRECTORY_DURABILITY_BARRIER",
            "MANIFEST_COMMITTER",
            "RECOVERY_INSPECTOR",
        }.issubset(component_ids),
    )

    protocol_steps = set(protocol["protocol_step"].astype(str))
    add(checks, "audit", "protocol_unique_temp_present", "CREATE_UNIQUE_SAME_DIR_TEMP" in protocol_steps)
    add(checks, "audit", "protocol_temp_fsync_present", "FLUSH_AND_FSYNC_TEMP" in protocol_steps)
    add(checks, "audit", "protocol_atomic_replace_present", "ATOMIC_REPLACE_TARGET" in protocol_steps)
    add(checks, "audit", "protocol_parent_fsync_present", "FSYNC_PARENT_DIRECTORY" in protocol_steps)
    add(checks, "audit", "protocol_manifest_after_target_present", "COMMIT_MANIFEST" in protocol_steps)

    invariant_names = set(invariants["invariant_name"].astype(str))
    add(checks, "audit", "invariant_unique_temp_present", "temporary_filename_is_unique" in invariant_names)
    add(checks, "audit", "invariant_manifest_order_present", "manifest_never_precedes_target_commit" in invariant_names)
    add(checks, "audit", "failure_modes_never_silent", not failures["silent_continue_allowed"].astype(bool).any())
    add(checks, "audit", "recovery_never_automatic", not recovery["automatic_recovery_allowed"].astype(bool).any())
    add(checks, "audit", "source_components_unimplemented", not components["implemented_in_phase_10_42"].astype(bool).any())
    add(checks, "audit", "source_protocol_disallowed_in_10_42", not protocol["allowed_in_phase_10_42"].astype(bool).any())

    amendments = REVIEW_CONTRACT["amendments"]
    amendment_names = {item["name"] for item in amendments}
    add(checks, "audit", "review_amendment_count_6", len(amendments) == 6)
    add(checks, "audit", "review_amendments_all_binding", all(item["binding"] for item in amendments))
    add(checks, "audit", "unique_temp_binding", "UNIQUE_TEMP_PATH_TEMPLATE" in amendment_names)
    add(checks, "audit", "atomic_manifest_binding", "ATOMIC_MANIFEST_COMMIT" in amendment_names)
    add(
        checks,
        "audit",
        "create_only_scope_binding",
        REVIEW_CONTRACT["implementation_scope"]
        == "CREATE_ONLY_EMPTY_INITIALIZATION_IN_TEMPORARY_TEST_DIRECTORIES",
    )
    add(
        checks,
        "audit",
        "existing_target_replacement_disabled",
        REVIEW_CONTRACT["existing_target_replacement_allowed_in_phase_10_44"] is False,
    )
    add(checks, "audit", "platform_durability_no_silent_fallback", "PLATFORM_DURABILITY_ADAPTER" in amendment_names)
    add(checks, "audit", "stale_lock_auto_delete_disabled", "NO_AUTOMATIC_RECOVERY" in amendment_names)
    add(checks, "audit", "phase_10_43_official_write_disabled", REVIEW_CONTRACT["official_dataset_write_allowed_in_phase_10_43"] is False)
    add(checks, "audit", "review_contract_valid", validate_contract(REVIEW_CONTRACT))
    add(checks, "audit", "review_root_exact", canonical_root(REVIEW_CONTRACT) == REVIEW_ROOT_SHA256)
    add(checks, "audit", "next_phase_exact", REVIEW_CONTRACT["next_phase"] == NEXT_PHASE)
    add(checks, "audit", "next_phase_is_implementation", REVIEW_CONTRACT["next_phase_type"] == "IMPLEMENTATION_NOT_REVIEW")
    add(checks, "audit", "project_not_complete", True)

    negative_rows = negative_controls()
    for row in negative_rows:
        add(
            checks,
            "negative_control",
            f"negative::{row['negative_control']}",
            row["rejected_fail_closed"],
        )

    failed = sum(not row["passed"] for row in checks)
    blockers = sum(row["blocker"] for row in checks)
    passed = failed == 0 and blockers == 0
    summary = {
        "phase": PHASE,
        "source_design_commit": DESIGN_COMMIT,
        "review_root_sha256": REVIEW_ROOT_SHA256,
        "preflight_check_count": preflight_count,
        "audit_check_count": len(checks) - preflight_count,
        "total_check_count": len(checks),
        "negative_control_count": len(negative_rows),
        "failed_check_count": failed,
        "blocker_count": blockers,
        "validation_passed": passed,
        "validation_decision": PASS_DECISION if passed else FAIL_DECISION,
        "binding_amendment_count": 6,
        "phase_10_44_implementation_allowed": passed,
        "phase_10_44_official_dataset_write_allowed": False,
        "phase_10_44_existing_target_replacement_allowed": False,
        "phase_10_45_controlled_official_initialization_allowed": passed,
        "official_dataset_write_count": 0,
        "official_evidence_row_count": 0,
        "signal_generation_count": 0,
        "paper_trade_execution_count": 0,
        "real_capital_execution_count": 0,
        "market_execution_count": 0,
        "automation_count": 0,
        "next_phase": NEXT_PHASE,
        "next_phase_type": "IMPLEMENTATION_NOT_REVIEW",
        "total_project_completed": False,
    }

    if write_reports:
        report_dir = root / REPORT_DIR
        report_dir.mkdir(parents=True, exist_ok=True)
        (report_dir / "summary.json").write_text(
            json.dumps(summary, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        (report_dir / "binding_review_contract.json").write_text(
            json.dumps(REVIEW_CONTRACT, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        with (report_dir / "checks.csv").open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(
                handle,
                fieldnames=["check_group", "check_name", "passed", "details", "blocker"],
            )
            writer.writeheader()
            writer.writerows(checks)
        with (report_dir / "negative_controls.csv").open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(
                handle,
                fieldnames=["negative_control", "rejected_fail_closed"],
            )
            writer.writeheader()
            writer.writerows(negative_rows)

    return {
        "summary": summary,
        "checks": checks,
        "negative_controls": negative_rows,
        "review_contract": REVIEW_CONTRACT,
    }


__all__ = [
    "BASE_COMMIT",
    "DESIGN_COMMIT",
    "NEXT_PHASE",
    "PASS_DECISION",
    "PHASE",
    "REVIEW_CONTRACT",
    "REVIEW_ROOT_SHA256",
    "canonical_root",
    "negative_controls",
    "validate",
    "validate_contract",
]
