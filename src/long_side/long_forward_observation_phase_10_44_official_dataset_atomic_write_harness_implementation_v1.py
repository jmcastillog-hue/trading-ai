from __future__ import annotations

import csv
import ctypes
import hashlib
import io
import json
import os
import socket
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Mapping

PHASE = "10.44"
IMPLEMENTATION_SCHEMA_VERSION = "LONG_FORWARD_OBSERVATION_OFFICIAL_DATASET_CREATE_ONLY_ATOMIC_WRITE_HARNESS_IMPLEMENTATION_V1"
SOURCE_REVIEW_COMMIT = "d5c5acefcc1f965566c20cb4d21bf62144d9a827"
SOURCE_REVIEW_ROOT_SHA256 = "31575687b9439397a920d4cb960c572abd07c00e05148feeb1a1d9dc269552ac"
CANDIDATE_RELATIVE_PATH = Path("data/forward/candidates/long_forward_observation_dataset_v1.empty_candidate.csv")
OFFICIAL_TARGET_RELATIVE_PATH = Path("data/forward/long_forward_observation_dataset_v1.csv")
TARGET_FILENAME = "long_forward_observation_dataset_v1.csv"
MANIFEST_FILENAME = "long_forward_observation_dataset_v1.manifest.csv"
LOCK_FILENAME = "long_forward_observation_dataset_v1.lock"
EXPECTED_CANDIDATE_SHA256 = "e3fa86a461fd46f4d66dc2e03f185e49b7b3438d3cbc33340c01f51310514ff1"
EXPECTED_CANDIDATE_SIZE_BYTES = 981
EXPECTED_COLUMN_COUNT = 54
EXPECTED_EVIDENCE_ROW_COUNT = 0
NEXT_PHASE = "PHASE_10_45_LONG_FORWARD_OBSERVATION_EVIDENCE_COLLECTION_OFFICIAL_DATASET_CONTROLLED_EMPTY_INITIALIZATION_V1"

FAILPOINTS = {
    "AFTER_LOCK_ACQUIRED",
    "AFTER_TARGET_TEMP_DURABLE",
    "AFTER_TARGET_PUBLISHED",
    "AFTER_MANIFEST_TEMP_DURABLE",
    "AFTER_MANIFEST_PUBLISHED",
}

MANIFEST_FIELDS = (
    "manifest_schema_version", "phase", "source_review_commit", "source_review_root_sha256",
    "operation_id", "created_at_utc", "candidate_sha256", "candidate_size_bytes",
    "target_filename", "target_canonical_path", "target_sha256", "target_size_bytes",
    "target_column_count", "target_evidence_row_count", "publication_primitive", "create_only",
    "existing_target_replacement_allowed", "official_dataset_path_used", "official_evidence_rows_written",
    "automatic_recovery_allowed", "signal_generation_enabled", "live_alerts_allowed",
    "paper_trade_execution_allowed", "real_capital_allowed", "market_execution_allowed",
    "exchange_execution_allowed", "automation_allowed", "execution_allowed", "human_review_required",
)

LOCK_FIELDS = (
    "lock_schema_version", "phase", "operation_id", "pid", "hostname", "started_at_utc",
    "candidate_sha256", "candidate_canonical_path", "target_canonical_path", "create_only",
    "official_dataset_path_used",
)


class HarnessError(RuntimeError):
    def __init__(self, code: str, message: str, *, operation_id: str = "", state: str = "") -> None:
        self.code = code
        self.operation_id = operation_id
        self.state = state
        super().__init__(message)


class InjectedHarnessFailure(HarnessError):
    pass


@dataclass(frozen=True)
class HarnessPaths:
    sandbox_root: Path
    target: Path
    manifest: Path
    lock: Path
    target_temp: Path
    manifest_temp: Path


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def canonical_json_bytes(value: Mapping[str, Any]) -> bytes:
    return (json.dumps(dict(value), sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False) + "\n").encode("utf-8")


def canonical_manifest_bytes(row: Mapping[str, Any]) -> bytes:
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=list(MANIFEST_FIELDS), lineterminator="\n", extrasaction="raise")
    writer.writeheader()
    writer.writerow({field: row[field] for field in MANIFEST_FIELDS})
    return output.getvalue().encode("utf-8")


def _require(condition: bool, code: str, message: str) -> None:
    if not condition:
        raise HarnessError(code, message)


def _write_all(fd: int, payload: bytes) -> None:
    view = memoryview(payload)
    written = 0
    while written < len(view):
        count = os.write(fd, view[written:])
        if count <= 0:
            raise HarnessError("WRITE_FAILED", "A durable write returned no progress.")
        written += count


def _durable_create_exclusive(path: Path, payload: bytes) -> None:
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    if hasattr(os, "O_BINARY"):
        flags |= os.O_BINARY
    fd = os.open(path, flags, 0o600)
    try:
        _write_all(fd, payload)
        os.fsync(fd)
    finally:
        os.close(fd)


def _fsync_directory(path: Path) -> None:
    flags = os.O_RDONLY
    if hasattr(os, "O_DIRECTORY"):
        flags |= os.O_DIRECTORY
    fd = os.open(path, flags)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def publication_primitive_name() -> str:
    if os.name == "nt":
        return "WINDOWS_MOVEFILEEX_WRITE_THROUGH_CREATE_ONLY"
    if os.name == "posix":
        return "POSIX_HARD_LINK_CREATE_ONLY_PLUS_DIRECTORY_FSYNC"
    raise HarnessError("UNSUPPORTED_PLATFORM_DURABILITY", f"Unsupported platform: {os.name}")


def _windows_publish_create_only(temp_path: Path, target_path: Path) -> None:
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    move_file_ex = kernel32.MoveFileExW
    move_file_ex.argtypes = [ctypes.c_wchar_p, ctypes.c_wchar_p, ctypes.c_uint32]
    move_file_ex.restype = ctypes.c_int
    ctypes.set_last_error(0)
    ok = move_file_ex(str(temp_path), str(target_path), 0x00000008)
    if not ok:
        raise HarnessError(
            "CREATE_ONLY_PUBLISH_FAILED",
            f"MoveFileExW create-only publish failed with Windows error {ctypes.get_last_error()}.",
        )


def publish_create_only(temp_path: Path, target_path: Path) -> str:
    _require(temp_path.parent == target_path.parent, "PATH_BOUNDARY_VIOLATION", "Publication requires the same parent directory.")
    _require(temp_path.exists() and temp_path.is_file() and not temp_path.is_symlink(), "TEMP_ARTIFACT_INVALID", "Staged artifact must be a regular file.")
    if target_path.exists() or target_path.is_symlink():
        raise HarnessError("EXISTING_TARGET_BLOCKED", f"Create-only target already exists: {target_path}")
    primitive = publication_primitive_name()
    if os.name == "nt":
        _windows_publish_create_only(temp_path, target_path)
    elif os.name == "posix":
        try:
            os.link(temp_path, target_path)
        except FileExistsError as exc:
            raise HarnessError("EXISTING_TARGET_BLOCKED", f"Target appeared concurrently: {target_path}") from exc
        except OSError as exc:
            raise HarnessError("CREATE_ONLY_PUBLISH_FAILED", f"POSIX publication failed: {exc}") from exc
        os.unlink(temp_path)
        _fsync_directory(target_path.parent)
    else:
        raise HarnessError("UNSUPPORTED_PLATFORM_DURABILITY", f"Unsupported platform: {os.name}")
    _require(target_path.exists() and target_path.is_file() and not target_path.is_symlink(), "POST_PUBLISH_TARGET_INVALID", "Published target is invalid.")
    return primitive


def inspect_candidate_bytes(payload: bytes) -> dict[str, Any]:
    try:
        decoded = payload.decode("utf-8", errors="strict")
        utf8_valid = True
    except UnicodeDecodeError:
        decoded = ""
        utf8_valid = False
    header = decoded[:-1] if decoded.endswith("\n") else decoded
    columns = header.split(",") if header else []
    return {
        "size_bytes": len(payload),
        "sha256": sha256_bytes(payload),
        "utf8_valid": utf8_valid,
        "utf8_bom_absent": not payload.startswith(b"\xef\xbb\xbf"),
        "lf_only": b"\r" not in payload,
        "physical_line_count": payload.count(b"\n"),
        "ends_with_single_lf": payload.endswith(b"\n") and not payload.endswith(b"\n\n"),
        "column_count": len(columns),
        "evidence_row_count": max(payload.count(b"\n") - 1, 0),
    }


def validate_candidate_bytes(payload: bytes) -> dict[str, Any]:
    result = inspect_candidate_bytes(payload)
    _require(result["size_bytes"] == EXPECTED_CANDIDATE_SIZE_BYTES, "CANDIDATE_SIZE_MISMATCH", f"Candidate size mismatch: {result['size_bytes']}")
    _require(result["sha256"] == EXPECTED_CANDIDATE_SHA256, "CANDIDATE_HASH_MISMATCH", f"Candidate SHA mismatch: {result['sha256']}")
    _require(result["utf8_valid"] and result["utf8_bom_absent"], "CANDIDATE_ENCODING_INVALID", "Candidate must be UTF-8 without BOM.")
    _require(result["lf_only"] and result["physical_line_count"] == 1 and result["ends_with_single_lf"], "CANDIDATE_LINE_ENDING_INVALID", "Candidate must be one LF-terminated line.")
    _require(result["column_count"] == EXPECTED_COLUMN_COUNT, "CANDIDATE_SCHEMA_MISMATCH", f"Expected {EXPECTED_COLUMN_COUNT} columns.")
    _require(result["evidence_row_count"] == EXPECTED_EVIDENCE_ROW_COUNT, "CANDIDATE_ROW_COUNT_MISMATCH", "Candidate must have zero evidence rows.")
    return result


def validate_candidate_path(repo_root: Path, candidate_path: Path) -> bytes:
    expected = (repo_root / CANDIDATE_RELATIVE_PATH).resolve()
    actual = candidate_path.resolve()
    _require(actual == expected, "CANDIDATE_PATH_BOUNDARY_VIOLATION", "Only the canonical candidate path is accepted.")
    _require(candidate_path.exists() and candidate_path.is_file() and not candidate_path.is_symlink(), "CANDIDATE_PATH_INVALID", "Canonical candidate must be a regular file.")
    payload = candidate_path.read_bytes()
    validate_candidate_bytes(payload)
    return payload


def resolve_paths(repo_root: Path, sandbox_root: Path, operation_id: str) -> HarnessPaths:
    repo = repo_root.resolve()
    sandbox = sandbox_root.resolve()
    _require(sandbox.exists() and sandbox.is_dir() and not sandbox.is_symlink(), "SANDBOX_INVALID", "Sandbox must be an existing regular directory.")
    try:
        inside_repository = sandbox.is_relative_to(repo)
    except ValueError:
        inside_repository = False
    _require(not inside_repository, "OFFICIAL_OR_REPOSITORY_PATH_PROHIBITED", "Phase 10.44 sandbox must be outside the repository.")
    target = sandbox / TARGET_FILENAME
    manifest = sandbox / MANIFEST_FILENAME
    lock = sandbox / LOCK_FILENAME
    target_temp = sandbox / f"{TARGET_FILENAME}.tmp.{operation_id}"
    manifest_temp = sandbox / f"{MANIFEST_FILENAME}.tmp.{operation_id}"
    official_target = (repo / OFFICIAL_TARGET_RELATIVE_PATH).resolve()
    _require(target.resolve() != official_target, "OFFICIAL_PATH_PROHIBITED", "Official dataset path is prohibited in Phase 10.44.")
    _require(len({p.resolve() for p in (target, manifest, lock, target_temp, manifest_temp)}) == 5, "PATH_COLLISION", "Harness paths must be distinct.")
    return HarnessPaths(sandbox, target, manifest, lock, target_temp, manifest_temp)


def build_lock_record(*, operation_id: str, started_at_utc: str, candidate_path: Path, target_path: Path) -> dict[str, Any]:
    record = {
        "lock_schema_version": "LONG_OFFICIAL_DATASET_WRITE_LOCK_V1",
        "phase": PHASE,
        "operation_id": operation_id,
        "pid": os.getpid(),
        "hostname": socket.gethostname(),
        "started_at_utc": started_at_utc,
        "candidate_sha256": EXPECTED_CANDIDATE_SHA256,
        "candidate_canonical_path": str(candidate_path.resolve()),
        "target_canonical_path": str(target_path.resolve()),
        "create_only": True,
        "official_dataset_path_used": False,
    }
    _require(set(record) == set(LOCK_FIELDS), "LOCK_SCHEMA_INVALID", "Lock fields mismatch.")
    return record


def acquire_lock(path: Path, record: Mapping[str, Any]) -> None:
    try:
        _durable_create_exclusive(path, canonical_json_bytes(record))
    except FileExistsError as exc:
        raise HarnessError("LOCK_CONTENTION", f"Exclusive lock already exists: {path}", operation_id=str(record.get("operation_id", "")), state="LOCK_CONTENTION") from exc


def read_lock(path: Path) -> dict[str, Any]:
    _require(path.exists() and path.is_file() and not path.is_symlink(), "LOCK_INVALID", "Lock must be a regular file.")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise HarnessError("LOCK_INVALID", "Lock JSON is invalid.") from exc
    _require(isinstance(value, dict) and set(value) == set(LOCK_FIELDS), "LOCK_SCHEMA_INVALID", "Lock fields mismatch.")
    return value


def release_owned_lock(path: Path, operation_id: str) -> None:
    record = read_lock(path)
    _require(record.get("operation_id") == operation_id, "LOCK_OWNERSHIP_MISMATCH", "Only the verified lock owner may remove it.")
    path.unlink()
    if os.name == "posix":
        _fsync_directory(path.parent)


def _safe_remove_owned_temp(path: Path, operation_id: str) -> None:
    if not path.exists():
        return
    _require(path.name.endswith(f".{operation_id}") and path.is_file() and not path.is_symlink(), "TEMP_OWNERSHIP_MISMATCH", "Refusing to remove unowned temp.")
    path.unlink()


def _trigger_failpoint(requested: str | None, point: str, operation_id: str) -> None:
    if requested == point:
        raise InjectedHarnessFailure("INJECTED_FAILURE", f"Injected failure at {point}.", operation_id=operation_id, state=point)


def build_manifest_row(*, operation_id: str, created_at_utc: str, target_path: Path, publication_primitive: str) -> dict[str, Any]:
    inspected = validate_candidate_bytes(target_path.read_bytes())
    return {
        "manifest_schema_version": "LONG_OFFICIAL_DATASET_MANIFEST_V1",
        "phase": PHASE,
        "source_review_commit": SOURCE_REVIEW_COMMIT,
        "source_review_root_sha256": SOURCE_REVIEW_ROOT_SHA256,
        "operation_id": operation_id,
        "created_at_utc": created_at_utc,
        "candidate_sha256": EXPECTED_CANDIDATE_SHA256,
        "candidate_size_bytes": EXPECTED_CANDIDATE_SIZE_BYTES,
        "target_filename": target_path.name,
        "target_canonical_path": str(target_path.resolve()),
        "target_sha256": inspected["sha256"],
        "target_size_bytes": inspected["size_bytes"],
        "target_column_count": inspected["column_count"],
        "target_evidence_row_count": inspected["evidence_row_count"],
        "publication_primitive": publication_primitive,
        "create_only": True,
        "existing_target_replacement_allowed": False,
        "official_dataset_path_used": False,
        "official_evidence_rows_written": 0,
        "automatic_recovery_allowed": False,
        "signal_generation_enabled": False,
        "live_alerts_allowed": False,
        "paper_trade_execution_allowed": False,
        "real_capital_allowed": False,
        "market_execution_allowed": False,
        "exchange_execution_allowed": False,
        "automation_allowed": False,
        "execution_allowed": False,
        "human_review_required": True,
    }


def read_manifest(path: Path) -> dict[str, str]:
    _require(path.exists() and path.is_file() and not path.is_symlink(), "MANIFEST_INVALID", "Manifest must be a regular file.")
    raw = path.read_bytes()
    _require(not raw.startswith(b"\xef\xbb\xbf") and b"\r" not in raw, "MANIFEST_ENCODING_INVALID", "Manifest must be UTF-8 LF-only without BOM.")
    try:
        reader = csv.DictReader(io.StringIO(raw.decode("utf-8", errors="strict")))
        rows = list(reader)
    except Exception as exc:
        raise HarnessError("MANIFEST_INVALID", "Manifest CSV is invalid.") from exc
    _require(reader.fieldnames == list(MANIFEST_FIELDS) and len(rows) == 1, "MANIFEST_SCHEMA_INVALID", "Manifest fields or row count invalid.")
    return rows[0]


def validate_committed_pair(target_path: Path, manifest_path: Path) -> dict[str, Any]:
    inspected = validate_candidate_bytes(target_path.read_bytes())
    manifest = read_manifest(manifest_path)
    false_fields = (
        "existing_target_replacement_allowed", "official_dataset_path_used", "automatic_recovery_allowed",
        "signal_generation_enabled", "live_alerts_allowed", "paper_trade_execution_allowed",
        "real_capital_allowed", "market_execution_allowed", "exchange_execution_allowed",
        "automation_allowed", "execution_allowed",
    )
    _require(manifest["target_filename"] == target_path.name, "MANIFEST_BINDING_MISMATCH", "Target filename mismatch.")
    _require(Path(manifest["target_canonical_path"]) == target_path.resolve(), "MANIFEST_BINDING_MISMATCH", "Canonical target mismatch.")
    _require(
        manifest["target_sha256"] == inspected["sha256"]
        and int(manifest["target_size_bytes"]) == inspected["size_bytes"]
        and int(manifest["target_column_count"]) == EXPECTED_COLUMN_COUNT
        and int(manifest["target_evidence_row_count"]) == 0,
        "MANIFEST_BINDING_MISMATCH", "Target metrics mismatch.",
    )
    _require(manifest["candidate_sha256"] == EXPECTED_CANDIDATE_SHA256 and int(manifest["candidate_size_bytes"]) == EXPECTED_CANDIDATE_SIZE_BYTES, "MANIFEST_BINDING_MISMATCH", "Candidate binding mismatch.")
    _require(manifest["source_review_root_sha256"] == SOURCE_REVIEW_ROOT_SHA256, "MANIFEST_BINDING_MISMATCH", "Review root mismatch.")
    _require(manifest["create_only"].lower() == "true" and manifest["human_review_required"].lower() == "true", "MANIFEST_PERMISSION_INVALID", "Create-only or review requirement invalid.")
    _require(all(manifest[field].lower() == "false" for field in false_fields), "MANIFEST_PERMISSION_INVALID", "A prohibited permission is enabled.")
    _require(int(manifest["official_evidence_rows_written"]) == 0, "MANIFEST_PERMISSION_INVALID", "Evidence rows must remain zero.")
    return {
        "target_sha256": inspected["sha256"],
        "target_size_bytes": inspected["size_bytes"],
        "target_column_count": inspected["column_count"],
        "target_evidence_row_count": inspected["evidence_row_count"],
        "manifest_operation_id": manifest["operation_id"],
        "publication_primitive": manifest["publication_primitive"],
    }


def inspect_recovery_state(sandbox_root: Path) -> dict[str, Any]:
    sandbox = sandbox_root.resolve()
    target = sandbox / TARGET_FILENAME
    manifest = sandbox / MANIFEST_FILENAME
    lock = sandbox / LOCK_FILENAME
    target_temps = sorted(sandbox.glob(f"{TARGET_FILENAME}.tmp.*"))
    manifest_temps = sorted(sandbox.glob(f"{MANIFEST_FILENAME}.tmp.*"))
    target_exists = target.exists()
    manifest_exists = manifest.exists()
    lock_exists = lock.exists()
    temp_count = len(target_temps) + len(manifest_temps)
    if not target_exists and not manifest_exists and not lock_exists and temp_count == 0:
        state = "CLEAN_EMPTY"
    elif target_exists and manifest_exists and not lock_exists and temp_count == 0:
        state = "COMMITTED_CLEAN"
    elif lock_exists and not target_exists and not manifest_exists and temp_count == 0:
        state = "LOCK_ONLY_RECOVERY_REQUIRED"
    elif not target_exists and not manifest_exists and temp_count > 0:
        state = "PRECOMMIT_RESIDUAL_RECOVERY_REQUIRED"
    elif target_exists and not manifest_exists:
        state = "TARGET_WITHOUT_MANIFEST_RECOVERY_REQUIRED"
    elif target_exists and manifest_exists and lock_exists:
        state = "TARGET_AND_MANIFEST_WITH_LOCK_RECOVERY_REQUIRED"
    elif manifest_exists and not target_exists:
        state = "MANIFEST_WITHOUT_TARGET_INVALID"
    else:
        state = "UNCLASSIFIED_RECOVERY_REQUIRED"
    return {
        "state": state,
        "target_exists": target_exists,
        "manifest_exists": manifest_exists,
        "lock_exists": lock_exists,
        "target_temp_count": len(target_temps),
        "manifest_temp_count": len(manifest_temps),
        "automatic_recovery_performed": False,
        "manual_review_required": state not in {"CLEAN_EMPTY", "COMMITTED_CLEAN"},
    }


def initialize_empty_dataset_in_sandbox(
    *,
    repo_root: Path | str,
    sandbox_root: Path | str,
    fail_at: str | None = None,
    operation_id_factory: Callable[[], str] | None = None,
    clock: Callable[[], str] | None = None,
) -> dict[str, Any]:
    repo = Path(repo_root).resolve()
    sandbox = Path(sandbox_root).resolve()
    if fail_at is not None and fail_at not in FAILPOINTS:
        raise HarnessError("UNKNOWN_FAILPOINT", f"Unknown failpoint: {fail_at}")
    operation_id = operation_id_factory() if operation_id_factory else uuid.uuid4().hex
    _require(len(operation_id) >= 16 and all(c.isalnum() or c in {"-", "_"} for c in operation_id), "OPERATION_ID_INVALID", "Operation id is unsafe.")
    started_at = clock() if clock else utc_now()
    candidate_path = repo / CANDIDATE_RELATIVE_PATH
    candidate_payload = validate_candidate_path(repo, candidate_path)
    paths = resolve_paths(repo, sandbox, operation_id)
    initial = inspect_recovery_state(sandbox)
    _require(initial["state"] == "CLEAN_EMPTY", "SANDBOX_NOT_CLEAN", f"Sandbox must start CLEAN_EMPTY, got {initial['state']}.")
    lock_record = build_lock_record(operation_id=operation_id, started_at_utc=started_at, candidate_path=candidate_path, target_path=paths.target)
    target_published = False
    try:
        acquire_lock(paths.lock, lock_record)
        _trigger_failpoint(fail_at, "AFTER_LOCK_ACQUIRED", operation_id)
        for path in (paths.target, paths.manifest):
            _require(not path.exists() and not path.is_symlink(), "CREATE_ONLY_BOUNDARY_VIOLATION", f"Artifact appeared after lock: {path}")
        _durable_create_exclusive(paths.target_temp, candidate_payload)
        validate_candidate_bytes(paths.target_temp.read_bytes())
        _trigger_failpoint(fail_at, "AFTER_TARGET_TEMP_DURABLE", operation_id)
        primitive = publish_create_only(paths.target_temp, paths.target)
        target_published = True
        validate_candidate_bytes(paths.target.read_bytes())
        _trigger_failpoint(fail_at, "AFTER_TARGET_PUBLISHED", operation_id)
        manifest_row = build_manifest_row(operation_id=operation_id, created_at_utc=started_at, target_path=paths.target, publication_primitive=primitive)
        _durable_create_exclusive(paths.manifest_temp, canonical_manifest_bytes(manifest_row))
        read_manifest(paths.manifest_temp)
        _trigger_failpoint(fail_at, "AFTER_MANIFEST_TEMP_DURABLE", operation_id)
        publish_create_only(paths.manifest_temp, paths.manifest)
        pair = validate_committed_pair(paths.target, paths.manifest)
        _trigger_failpoint(fail_at, "AFTER_MANIFEST_PUBLISHED", operation_id)
        release_owned_lock(paths.lock, operation_id)
        final_state = inspect_recovery_state(sandbox)
        _require(final_state["state"] == "COMMITTED_CLEAN", "FINAL_STATE_INVALID", f"Expected COMMITTED_CLEAN, got {final_state['state']}.")
        return {
            "phase": PHASE,
            "implementation_schema_version": IMPLEMENTATION_SCHEMA_VERSION,
            "operation_id": operation_id,
            "started_at_utc": started_at,
            "sandbox_root": str(sandbox),
            "target_path": str(paths.target),
            "manifest_path": str(paths.manifest),
            "publication_primitive": pair["publication_primitive"],
            "candidate_sha256": EXPECTED_CANDIDATE_SHA256,
            "target_sha256": pair["target_sha256"],
            "target_size_bytes": pair["target_size_bytes"],
            "target_column_count": pair["target_column_count"],
            "target_evidence_row_count": pair["target_evidence_row_count"],
            "create_only": True,
            "existing_target_replacement_allowed": False,
            "official_dataset_path_used": False,
            "official_dataset_write_count": 0,
            "official_evidence_rows_written": 0,
            "automatic_recovery_performed": False,
            "human_review_required": True,
            "final_state": final_state["state"],
            "next_phase": NEXT_PHASE,
        }
    except Exception as exc:
        if not target_published:
            try:
                _safe_remove_owned_temp(paths.target_temp, operation_id)
                _safe_remove_owned_temp(paths.manifest_temp, operation_id)
                if paths.lock.exists():
                    release_owned_lock(paths.lock, operation_id)
            except Exception:
                pass
        state = inspect_recovery_state(sandbox)["state"]
        if isinstance(exc, HarnessError):
            if not exc.operation_id:
                exc.operation_id = operation_id
            if not exc.state:
                exc.state = state
            raise
        raise HarnessError("INTERNAL_FAIL_CLOSED", f"Internal error: {type(exc).__name__}", operation_id=operation_id, state=state) from exc


__all__ = [
    "CANDIDATE_RELATIVE_PATH", "EXPECTED_CANDIDATE_SHA256", "EXPECTED_CANDIDATE_SIZE_BYTES",
    "EXPECTED_COLUMN_COUNT", "FAILPOINTS", "HarnessError", "HarnessPaths",
    "IMPLEMENTATION_SCHEMA_VERSION", "InjectedHarnessFailure", "LOCK_FIELDS", "LOCK_FILENAME",
    "MANIFEST_FIELDS", "MANIFEST_FILENAME", "NEXT_PHASE", "OFFICIAL_TARGET_RELATIVE_PATH",
    "PHASE", "SOURCE_REVIEW_COMMIT", "SOURCE_REVIEW_ROOT_SHA256", "TARGET_FILENAME",
    "acquire_lock", "build_lock_record", "build_manifest_row", "canonical_json_bytes",
    "canonical_manifest_bytes", "initialize_empty_dataset_in_sandbox", "inspect_candidate_bytes",
    "inspect_recovery_state", "publication_primitive_name", "publish_create_only", "read_lock",
    "read_manifest", "release_owned_lock", "resolve_paths", "sha256_bytes",
    "validate_candidate_bytes", "validate_candidate_path", "validate_committed_pair",
]
