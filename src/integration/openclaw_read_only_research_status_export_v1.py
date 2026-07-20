from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import tempfile
import uuid
from pathlib import Path
from typing import Any, Mapping, Sequence

from src.integration import openclaw_read_only_research_status_contract_v1 as contract


PHASE = "10.42R.4"
EXPORT_SCHEMA_VERSION = "OPENCLAW_READ_ONLY_RESEARCH_STATUS_EXPORT_V1"
SOURCE_CONTRACT_COMMIT = "26c14a5a1fc63fbdb5bbb61f9bbc7d3dd46656d2"
SOURCE_CONTRACT_ROOT_SHA256 = (
    "ba84140879bac8a897505bd55e12d3c117354caf1a5a5ad4f6c3eb003bd6fa46"
)
SOURCE_CONTRACT_MODULE_PATH = Path(
    "src/integration/openclaw_read_only_research_status_contract_v1.py"
)
SOURCE_SCHEMA_PATH = Path(
    "schemas/openclaw_read_only_research_status_contract_v1.schema.json"
)
SOURCE_MANIFEST_PATH = Path("PHASE_10_42R_3_MANIFEST.sha256")
SOURCE_CONTRACT_MODULE_SHA256 = (
    "03f50b91f32af6cd421792810ba8da469faf1e35882eae8a21d176d861d770b5"
)
SOURCE_SCHEMA_SHA256 = (
    "e7e21b99d899ecd7157aa7b476ae6f379d6a01adea804271c83426b271e71289"
)
DETERMINISTIC_GENERATED_AT_UTC = "2026-07-20T00:00:00+00:00"
DEFAULT_OUTPUT_DIR = Path(
    "reports/phase_10_42r_4/openclaw_read_only_export_v1"
)
SNAPSHOT_FILENAME = "openclaw_read_only_research_status_v1.json"
MANIFEST_FILENAME = "openclaw_read_only_research_status_v1.manifest.json"
RECOMMENDED_NEXT_PHASE = (
    "PHASE_10_42R_5_OPENCLAW_READ_ONLY_RESEARCH_STATUS_EXPORT_"
    "INTEGRITY_AND_CONSUMER_BOUNDARY_REVIEW_V1"
)


class StatusExportError(RuntimeError):
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


def canonical_pretty_json_bytes(value: object) -> bytes:
    text = json.dumps(
        value,
        sort_keys=True,
        indent=2,
        ensure_ascii=True,
        allow_nan=False,
    )
    return (text + "\n").encode("utf-8")


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise StatusExportError(message)


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
    raise StatusExportError(f"Unsupported JSON schema type: {expected}")


def validate_json_schema_subset(
    value: object,
    schema: Mapping[str, Any],
    *,
    location: str = "$",
) -> None:
    expected_type = schema.get("type")
    if expected_type is not None:
        _require(
            isinstance(expected_type, str) and _json_type_matches(value, expected_type),
            f"{location}: type mismatch, expected {expected_type}",
        )

    if "const" in schema:
        _require(value == schema["const"], f"{location}: const mismatch")

    if isinstance(value, str):
        if "minLength" in schema:
            _require(len(value) >= int(schema["minLength"]), f"{location}: too short")
        if "pattern" in schema:
            _require(
                re.fullmatch(str(schema["pattern"]), value) is not None,
                f"{location}: pattern mismatch",
            )

    if isinstance(value, Mapping):
        required = schema.get("required", [])
        _require(isinstance(required, list), f"{location}: invalid required list")
        missing = [name for name in required if name not in value]
        _require(not missing, f"{location}: missing required fields {missing}")

        properties = schema.get("properties", {})
        _require(isinstance(properties, Mapping), f"{location}: invalid properties")
        if schema.get("additionalProperties") is False:
            extras = sorted(set(value) - set(properties))
            _require(not extras, f"{location}: unexpected fields {extras}")

        for name, child_schema in properties.items():
            if name in value:
                _require(
                    isinstance(child_schema, Mapping),
                    f"{location}.{name}: invalid child schema",
                )
                validate_json_schema_subset(
                    value[name], child_schema, location=f"{location}.{name}"
                )


def _read_source_manifest(root: Path) -> dict[str, str]:
    path = root / SOURCE_MANIFEST_PATH
    _require(path.is_file(), f"Missing source manifest: {path}")
    rows: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line:
            continue
        match = re.fullmatch(r"([0-9a-f]{64})  (.+)", line)
        _require(match is not None, f"Invalid source manifest line: {raw_line}")
        digest, relative = match.groups()
        _require(relative not in rows, f"Duplicate source manifest path: {relative}")
        rows[relative] = digest
    return rows


def inspect_git_freshness(root: Path, *, require_git: bool = True) -> dict[str, Any]:
    git_dir = root / ".git"
    if not git_dir.exists():
        _require(not require_git, "Git metadata is required for source freshness")
        return {
            "git_metadata_available": False,
            "current_head": "NOT_AVAILABLE",
            "source_commit_exists": False,
            "source_commit_is_ancestor": False,
            "freshness_check_skipped": True,
        }

    def run(arguments: Sequence[str], *, allow_failure: bool = False) -> subprocess.CompletedProcess[str]:
        completed = subprocess.run(
            ["git", "-C", str(root), *arguments],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        if not allow_failure and completed.returncode != 0:
            raise StatusExportError(
                f"Git command failed: {' '.join(arguments)}: {completed.stderr.strip()}"
            )
        return completed

    current_head = run(["rev-parse", "HEAD"]).stdout.strip()
    source_exists = run(
        ["cat-file", "-e", f"{SOURCE_CONTRACT_COMMIT}^{{commit}}"],
        allow_failure=True,
    ).returncode == 0
    ancestor = False
    if source_exists:
        ancestor = run(
            ["merge-base", "--is-ancestor", SOURCE_CONTRACT_COMMIT, "HEAD"],
            allow_failure=True,
        ).returncode == 0

    _require(source_exists, "Source contract commit does not exist in repository")
    _require(ancestor, "Source contract commit is not an ancestor of current HEAD")
    return {
        "git_metadata_available": True,
        "current_head": current_head,
        "source_commit_exists": source_exists,
        "source_commit_is_ancestor": ancestor,
        "freshness_check_skipped": False,
    }


def verify_source_authority(root: Path, *, require_git: bool = True) -> dict[str, Any]:
    module_path = root / SOURCE_CONTRACT_MODULE_PATH
    schema_path = root / SOURCE_SCHEMA_PATH
    _require(module_path.is_file(), f"Missing source contract module: {module_path}")
    _require(schema_path.is_file(), f"Missing source schema: {schema_path}")

    module_hash = normalized_text_sha256(module_path)
    schema_hash = normalized_text_sha256(schema_path)
    _require(module_hash == SOURCE_CONTRACT_MODULE_SHA256, "Source contract module hash mismatch")
    _require(schema_hash == SOURCE_SCHEMA_SHA256, "Source schema hash mismatch")

    manifest = _read_source_manifest(root)
    _require(
        manifest.get(SOURCE_CONTRACT_MODULE_PATH.as_posix())
        == SOURCE_CONTRACT_MODULE_SHA256,
        "Source manifest contract-module binding mismatch",
    )
    _require(
        manifest.get(SOURCE_SCHEMA_PATH.as_posix()) == SOURCE_SCHEMA_SHA256,
        "Source manifest schema binding mismatch",
    )

    git_state = inspect_git_freshness(root, require_git=require_git)
    return {
        "source_contract_commit": SOURCE_CONTRACT_COMMIT,
        "source_contract_module_sha256": module_hash,
        "source_schema_sha256": schema_hash,
        **git_state,
    }


def load_source_schema(root: Path) -> dict[str, Any]:
    value = json.loads((root / SOURCE_SCHEMA_PATH).read_text(encoding="utf-8"))
    _require(isinstance(value, dict), "Source schema must be an object")
    return value


def build_export_snapshot() -> dict[str, Any]:
    snapshot = contract.build_status_snapshot(
        generated_at_utc=DETERMINISTIC_GENERATED_AT_UTC
    )
    contract.validate_status_snapshot(snapshot)
    _require(
        snapshot["contract_root_sha256"] == SOURCE_CONTRACT_ROOT_SHA256,
        "Source contract root mismatch",
    )
    return snapshot


def build_export_manifest(snapshot_bytes: bytes) -> dict[str, Any]:
    return {
        "export_phase": PHASE,
        "export_schema_version": EXPORT_SCHEMA_VERSION,
        "export_mode": "LOCAL_FILE_EXPORT_READ_ONLY_NO_RUNTIME_CONSUMER",
        "snapshot_filename": SNAPSHOT_FILENAME,
        "snapshot_sha256": sha256_bytes(snapshot_bytes),
        "snapshot_size_bytes": len(snapshot_bytes),
        "source_contract_commit": SOURCE_CONTRACT_COMMIT,
        "source_contract_root_sha256": SOURCE_CONTRACT_ROOT_SHA256,
        "source_contract_module_sha256": SOURCE_CONTRACT_MODULE_SHA256,
        "source_schema_sha256": SOURCE_SCHEMA_SHA256,
        "deterministic_generated_at_utc": DETERMINISTIC_GENERATED_AT_UTC,
        "atomic_replace_used": True,
        "same_directory_temporary_file_used": True,
        "snapshot_published_before_manifest": True,
        "fail_closed_required": True,
        "human_review_required": True,
        "openclaw_runtime_status_consumption_allowed": False,
        "openclaw_tool_invocation_allowed": False,
        "openclaw_operational_integration_allowed": False,
        "official_dataset_write_allowed": False,
        "signal_generation_enabled": False,
        "paper_trade_execution_allowed": False,
        "real_capital_allowed": False,
        "market_execution_allowed": False,
        "automation_allowed": False,
        "recommended_next_phase": RECOMMENDED_NEXT_PHASE,
    }


def _fsync_parent_directory(path: Path) -> bool:
    flags = os.O_RDONLY | int(getattr(os, "O_DIRECTORY", 0))
    try:
        directory_fd = os.open(str(path), flags)
    except OSError:
        return False
    try:
        os.fsync(directory_fd)
        return True
    except OSError:
        return False
    finally:
        os.close(directory_fd)


def atomic_write_bytes(path: Path, payload: bytes) -> dict[str, Any]:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = path.parent / f".{path.name}.tmp-{os.getpid()}-{uuid.uuid4().hex}"
    replaced = False
    try:
        with open(temporary_path, "xb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_path, path)
        replaced = True
        parent_fsync = _fsync_parent_directory(path.parent)
        return {
            "path": path.as_posix(),
            "bytes_written": len(payload),
            "sha256": sha256_bytes(payload),
            "atomic_replace_performed": True,
            "parent_directory_fsync_performed": parent_fsync,
        }
    finally:
        if not replaced and temporary_path.exists():
            temporary_path.unlink()


def expected_export_bytes(root: Path) -> tuple[bytes, bytes]:
    snapshot = build_export_snapshot()
    schema = load_source_schema(root)
    validate_json_schema_subset(snapshot, schema)
    snapshot_bytes = canonical_pretty_json_bytes(snapshot)
    manifest = build_export_manifest(snapshot_bytes)
    manifest_bytes = canonical_pretty_json_bytes(manifest)
    return snapshot_bytes, manifest_bytes


def validate_export_bundle(
    root: Path | str = Path("."),
    *,
    output_dir: Path | str | None = None,
    require_git: bool = True,
) -> dict[str, Any]:
    root_path = Path(root).resolve()
    authority = verify_source_authority(root_path, require_git=require_git)
    bundle_dir = (
        Path(output_dir).resolve()
        if output_dir is not None
        else (root_path / DEFAULT_OUTPUT_DIR).resolve()
    )
    snapshot_path = bundle_dir / SNAPSHOT_FILENAME
    manifest_path = bundle_dir / MANIFEST_FILENAME
    _require(snapshot_path.is_file(), f"Missing snapshot: {snapshot_path}")
    _require(manifest_path.is_file(), f"Missing manifest: {manifest_path}")

    actual_inventory = sorted(
        path.name for path in bundle_dir.iterdir() if path.is_file()
    )
    _require(
        actual_inventory == sorted([SNAPSHOT_FILENAME, MANIFEST_FILENAME]),
        f"Export inventory mismatch: {actual_inventory}",
    )
    _require(
        not any(".tmp-" in path.name for path in bundle_dir.iterdir()),
        "Temporary export file remains",
    )

    snapshot_bytes = snapshot_path.read_bytes()
    manifest_bytes = manifest_path.read_bytes()
    snapshot = json.loads(snapshot_bytes.decode("utf-8"))
    manifest = json.loads(manifest_bytes.decode("utf-8"))
    _require(isinstance(snapshot, dict), "Snapshot must be an object")
    _require(isinstance(manifest, dict), "Manifest must be an object")

    contract.validate_status_snapshot(snapshot)
    validate_json_schema_subset(snapshot, load_source_schema(root_path))
    _require(
        snapshot.get("contract_root_sha256") == SOURCE_CONTRACT_ROOT_SHA256,
        "Exported contract root mismatch",
    )
    _require(manifest == build_export_manifest(snapshot_bytes), "Manifest mismatch")
    _require(
        manifest.get("snapshot_sha256") == sha256_bytes(snapshot_bytes),
        "Snapshot digest mismatch",
    )
    _require(
        manifest.get("snapshot_size_bytes") == len(snapshot_bytes),
        "Snapshot size mismatch",
    )
    expected_snapshot, expected_manifest = expected_export_bytes(root_path)
    _require(snapshot_bytes == expected_snapshot, "Snapshot is not deterministic")
    _require(manifest_bytes == expected_manifest, "Manifest is not deterministic")

    prohibited = snapshot["permissions"]["prohibited_capabilities"]
    read_only = snapshot["permissions"]["read_only_capabilities"]
    _require(all(value is False for value in prohibited.values()), "Prohibited permission enabled")
    _require(all(value is True for value in read_only.values()), "Read-only permission disabled")

    return {
        "validation_passed": True,
        "bundle_directory": bundle_dir.as_posix(),
        "export_file_count": 2,
        "snapshot_sha256": sha256_bytes(snapshot_bytes),
        "snapshot_size_bytes": len(snapshot_bytes),
        "manifest_sha256": sha256_bytes(manifest_bytes),
        "contract_root_sha256": snapshot["contract_root_sha256"],
        "read_only_capability_count": len(read_only),
        "prohibited_capability_count": len(prohibited),
        **authority,
    }


def publish_status_export(
    root: Path | str = Path("."),
    *,
    output_dir: Path | str | None = None,
    require_git: bool = True,
) -> dict[str, Any]:
    root_path = Path(root).resolve()
    verify_source_authority(root_path, require_git=require_git)
    bundle_dir = (
        Path(output_dir).resolve()
        if output_dir is not None
        else (root_path / DEFAULT_OUTPUT_DIR).resolve()
    )
    _require(
        (root_path / "reports") in bundle_dir.parents,
        "Default export must remain under the local reports tree",
    )
    forbidden_fragments = (
        "data/forward/official",
        "data/forward/candidates",
        "forward_evidence/official",
    )
    normalized_bundle = bundle_dir.as_posix().lower()
    _require(
        not any(fragment in normalized_bundle for fragment in forbidden_fragments),
        "Export path overlaps an evidence or candidate path",
    )

    snapshot_bytes, manifest_bytes = expected_export_bytes(root_path)
    snapshot_result = atomic_write_bytes(bundle_dir / SNAPSHOT_FILENAME, snapshot_bytes)
    manifest_result = atomic_write_bytes(bundle_dir / MANIFEST_FILENAME, manifest_bytes)
    validation = validate_export_bundle(
        root_path, output_dir=bundle_dir, require_git=require_git
    )
    return {
        **validation,
        "export_phase": PHASE,
        "export_schema_version": EXPORT_SCHEMA_VERSION,
        "atomic_snapshot_write_count": 1,
        "atomic_manifest_write_count": 1,
        "snapshot_parent_directory_fsync_performed": snapshot_result[
            "parent_directory_fsync_performed"
        ],
        "manifest_parent_directory_fsync_performed": manifest_result[
            "parent_directory_fsync_performed"
        ],
        "openclaw_runtime_integration_count": 0,
        "openclaw_status_consumption_count": 0,
        "openclaw_tool_invocation_count": 0,
        "official_dataset_write_count": 0,
        "signal_generation_count": 0,
        "paper_trade_execution_count": 0,
        "real_capital_execution_count": 0,
        "market_execution_count": 0,
        "automation_count": 0,
        "recommended_next_phase": RECOMMENDED_NEXT_PHASE,
    }


__all__ = [
    "DEFAULT_OUTPUT_DIR",
    "DETERMINISTIC_GENERATED_AT_UTC",
    "EXPORT_SCHEMA_VERSION",
    "MANIFEST_FILENAME",
    "PHASE",
    "RECOMMENDED_NEXT_PHASE",
    "SNAPSHOT_FILENAME",
    "SOURCE_CONTRACT_COMMIT",
    "SOURCE_CONTRACT_ROOT_SHA256",
    "StatusExportError",
    "atomic_write_bytes",
    "build_export_manifest",
    "build_export_snapshot",
    "canonical_pretty_json_bytes",
    "expected_export_bytes",
    "inspect_git_freshness",
    "normalized_text_sha256",
    "publish_status_export",
    "validate_export_bundle",
    "validate_json_schema_subset",
    "verify_source_authority",
]
