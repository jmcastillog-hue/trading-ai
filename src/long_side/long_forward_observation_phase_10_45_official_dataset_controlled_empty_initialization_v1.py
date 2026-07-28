from __future__ import annotations

import uuid
from pathlib import Path
from typing import Any, Callable

from src.long_side import long_forward_observation_phase_10_44_official_dataset_atomic_write_harness_implementation_v1 as atomic

PHASE = "10.45"
SCHEMA_VERSION = "LONG_FORWARD_OBSERVATION_OFFICIAL_DATASET_CONTROLLED_EMPTY_INITIALIZATION_V1"
GATE_B_AUTHORIZATION = "PHASE_10_45_GATE_B_EXPLICITLY_AUTHORIZED"
OFFICIAL_DIRECTORY = Path("data/forward")
TARGET_FILENAME = atomic.TARGET_FILENAME
MANIFEST_FILENAME = atomic.MANIFEST_FILENAME
LOCK_FILENAME = atomic.LOCK_FILENAME
EXPECTED_SHA256 = atomic.EXPECTED_CANDIDATE_SHA256
EXPECTED_BYTES = atomic.EXPECTED_CANDIDATE_SIZE_BYTES
EXPECTED_COLUMNS = atomic.EXPECTED_COLUMN_COUNT
EXPECTED_ROWS = 0
BACKUP_PATTERNS = (f"{TARGET_FILENAME}.bak*", f"{MANIFEST_FILENAME}.bak*", f"{TARGET_FILENAME}.backup*", f"{MANIFEST_FILENAME}.backup*")
TEMP_PATTERNS = (f"{TARGET_FILENAME}.tmp.*", f"{MANIFEST_FILENAME}.tmp.*")


class Phase1045Error(atomic.HarnessError):
    pass


def _require(value: bool, code: str, message: str) -> None:
    if not value:
        raise Phase1045Error(code, message)


def official_paths(repo_root: Path | str) -> dict[str, Path]:
    directory = Path(repo_root).resolve() / OFFICIAL_DIRECTORY
    return {"directory": directory, "target": directory / TARGET_FILENAME, "manifest": directory / MANIFEST_FILENAME, "lock": directory / LOCK_FILENAME}


def preflight_official(repo_root: Path | str) -> dict[str, Any]:
    root = Path(repo_root).resolve()
    candidate = root / atomic.CANDIDATE_RELATIVE_PATH
    payload = atomic.validate_candidate_path(root, candidate)
    metrics = atomic.validate_candidate_bytes(payload)
    paths = official_paths(root)
    directory = paths["directory"]
    residuals: list[str] = []
    for name in ("target", "manifest", "lock"):
        path = paths[name]
        if path.exists() or path.is_symlink():
            residuals.append(str(path.relative_to(root)).replace("\\", "/"))
    if directory.exists():
        for pattern in TEMP_PATTERNS + BACKUP_PATTERNS:
            residuals.extend(str(path.relative_to(root)).replace("\\", "/") for path in sorted(directory.glob(pattern)))
    residuals = sorted(set(residuals))
    return {"phase": PHASE, "state": "CLEAN_EMPTY" if not residuals else "RESIDUALS_BLOCKED", "residuals": residuals, "candidate_sha256": metrics["sha256"], "candidate_size_bytes": metrics["size_bytes"], "candidate_column_count": metrics["column_count"], "candidate_evidence_row_count": metrics["evidence_row_count"], "official_write_allowed": False, "create_only": True, "replacement_allowed": False, "trading_effects": False}


def _manifest_row(operation_id: str, created_at: str, target: Path, primitive: str) -> dict[str, Any]:
    row = atomic.build_manifest_row(operation_id=operation_id, created_at_utc=created_at, target_path=target, publication_primitive=primitive)
    row["phase"] = PHASE
    row["official_dataset_path_used"] = True
    return row


def verify_committed_pair(target: Path, manifest: Path) -> dict[str, Any]:
    metrics = atomic.validate_candidate_bytes(target.read_bytes())
    row = atomic.read_manifest(manifest)
    _require(row["phase"] == PHASE, "MANIFEST_PHASE_MISMATCH", "Manifest phase mismatch.")
    _require(Path(row["target_canonical_path"]) == target.resolve(), "MANIFEST_BINDING_MISMATCH", "Target path mismatch.")
    _require(row["target_sha256"] == metrics["sha256"], "MANIFEST_BINDING_MISMATCH", "Target hash mismatch.")
    _require(int(row["target_size_bytes"]) == EXPECTED_BYTES, "MANIFEST_BINDING_MISMATCH", "Target size mismatch.")
    _require(int(row["target_column_count"]) == EXPECTED_COLUMNS and int(row["target_evidence_row_count"]) == 0, "MANIFEST_BINDING_MISMATCH", "Target shape mismatch.")
    _require(row["create_only"].lower() == "true" and row["existing_target_replacement_allowed"].lower() == "false", "MANIFEST_PERMISSION_INVALID", "Create-only boundary invalid.")
    _require(row["official_dataset_path_used"].lower() == "true", "MANIFEST_PERMISSION_INVALID", "Official path binding absent.")
    blocked = ("signal_generation_enabled", "live_alerts_allowed", "paper_trade_execution_allowed", "real_capital_allowed", "market_execution_allowed", "exchange_execution_allowed", "automation_allowed", "execution_allowed")
    _require(all(row[name].lower() == "false" for name in blocked), "TRADING_PERMISSION_INVALID", "Trading permission enabled.")
    return {"target_sha256": metrics["sha256"], "target_size_bytes": metrics["size_bytes"], "target_column_count": metrics["column_count"], "target_evidence_row_count": metrics["evidence_row_count"]}


def initialize_official_empty_dataset(*, repo_root: Path | str, gate_b_authorization: str | None = None, fail_at: str | None = None, operation_id_factory: Callable[[], str] | None = None, clock: Callable[[], str] | None = None) -> dict[str, Any]:
    _require(gate_b_authorization == GATE_B_AUTHORIZATION, "GATE_B_AUTHORIZATION_REQUIRED", "Official initialization is blocked without explicit Gate B authorization.")
    root = Path(repo_root).resolve()
    preflight = preflight_official(root)
    _require(preflight["state"] == "CLEAN_EMPTY", "OFFICIAL_PREFLIGHT_FAILED", f"Official artifacts are not clean: {preflight['residuals']}")
    paths = official_paths(root)
    _require(paths["directory"].exists() and paths["directory"].is_dir() and not paths["directory"].is_symlink(), "OFFICIAL_DIRECTORY_INVALID", "Official directory must already exist.")
    operation_id = operation_id_factory() if operation_id_factory else uuid.uuid4().hex
    _require(len(operation_id) >= 16 and all(c.isalnum() or c in "-_" for c in operation_id), "OPERATION_ID_INVALID", "Unsafe operation id.")
    started_at = clock() if clock else atomic.utc_now()
    target_temp = paths["directory"] / f"{TARGET_FILENAME}.tmp.{operation_id}"
    manifest_temp = paths["directory"] / f"{MANIFEST_FILENAME}.tmp.{operation_id}"
    lock_record = atomic.build_lock_record(operation_id=operation_id, started_at_utc=started_at, candidate_path=root / atomic.CANDIDATE_RELATIVE_PATH, target_path=paths["target"])
    lock_record["phase"] = PHASE
    lock_record["official_dataset_path_used"] = True
    target_published = False
    try:
        atomic.acquire_lock(paths["lock"], lock_record)
        atomic._trigger_failpoint(fail_at, "AFTER_LOCK_ACQUIRED", operation_id)
        payload = atomic.validate_candidate_path(root, root / atomic.CANDIDATE_RELATIVE_PATH)
        for path in (paths["target"], paths["manifest"]):
            _require(not path.exists() and not path.is_symlink(), "CREATE_ONLY_BOUNDARY_VIOLATION", f"Artifact appeared after lock: {path}")
        atomic._durable_create_exclusive(target_temp, payload)
        atomic.validate_candidate_bytes(target_temp.read_bytes())
        atomic._trigger_failpoint(fail_at, "AFTER_TARGET_TEMP_DURABLE", operation_id)
        primitive = atomic.publish_create_only(target_temp, paths["target"])
        target_published = True
        atomic.validate_candidate_bytes(paths["target"].read_bytes())
        atomic._trigger_failpoint(fail_at, "AFTER_TARGET_PUBLISHED", operation_id)
        row = _manifest_row(operation_id, started_at, paths["target"], primitive)
        atomic._durable_create_exclusive(manifest_temp, atomic.canonical_manifest_bytes(row))
        atomic.read_manifest(manifest_temp)
        atomic._trigger_failpoint(fail_at, "AFTER_MANIFEST_TEMP_DURABLE", operation_id)
        atomic.publish_create_only(manifest_temp, paths["manifest"])
        pair = verify_committed_pair(paths["target"], paths["manifest"])
        atomic._trigger_failpoint(fail_at, "AFTER_MANIFEST_PUBLISHED", operation_id)
        atomic.release_owned_lock(paths["lock"], operation_id)
        final = preflight_official(root)
        committed_clean = paths["target"].exists() and paths["manifest"].exists() and not paths["lock"].exists() and not list(paths["directory"].glob("*.tmp.*"))
        _require(committed_clean, "FINAL_STATE_INVALID", "Committed pair is not clean.")
        return {"phase": PHASE, "operation_id": operation_id, "final_state": "COMMITTED_CLEAN", **pair, "create_only": True, "replacement_allowed": False, "official_evidence_rows_written": 0, "automatic_recovery_performed": False, "signal_generation_enabled": False, "live_alerts_allowed": False, "paper_trade_execution_allowed": False, "real_capital_allowed": False, "market_execution_allowed": False, "exchange_execution_allowed": False, "automation_allowed": False, "execution_allowed": False, "human_review_required": True, "post_commit_preflight_state": final["state"]}
    except Exception as exc:
        if not target_published:
            try:
                atomic._safe_remove_owned_temp(target_temp, operation_id)
                atomic._safe_remove_owned_temp(manifest_temp, operation_id)
                if paths["lock"].exists():
                    atomic.release_owned_lock(paths["lock"], operation_id)
            except Exception:
                pass
        if isinstance(exc, atomic.HarnessError):
            raise
        raise Phase1045Error("INTERNAL_FAIL_CLOSED", f"Internal error: {type(exc).__name__}") from exc


def initialize_in_isolated_directory(*, repo_root: Path | str, isolated_directory: Path | str, gate_b_authorization: str | None = None, **kwargs: Any) -> dict[str, Any]:
    _require(gate_b_authorization == GATE_B_AUTHORIZATION, "GATE_B_AUTHORIZATION_REQUIRED", "Explicit authorization is required even in isolation.")
    root = Path(repo_root).resolve()
    isolated = Path(isolated_directory).resolve()
    _require(not isolated.is_relative_to(root), "OFFICIAL_PATH_PROHIBITED_IN_ISOLATION", "Isolation directory must be outside the repository.")
    result = dict(atomic.initialize_empty_dataset_in_sandbox(repo_root=root, sandbox_root=isolated, **kwargs))
    result.update({
        "signal_generation_enabled": False,
        "live_alerts_allowed": False,
        "paper_trade_execution_allowed": False,
        "real_capital_allowed": False,
        "market_execution_allowed": False,
        "exchange_execution_allowed": False,
        "automation_allowed": False,
        "execution_allowed": False,
    })
    return result


__all__ = ["BACKUP_PATTERNS", "EXPECTED_BYTES", "EXPECTED_COLUMNS", "EXPECTED_ROWS", "EXPECTED_SHA256", "GATE_B_AUTHORIZATION", "LOCK_FILENAME", "MANIFEST_FILENAME", "PHASE", "Phase1045Error", "TARGET_FILENAME", "initialize_in_isolated_directory", "initialize_official_empty_dataset", "official_paths", "preflight_official", "verify_committed_pair"]
