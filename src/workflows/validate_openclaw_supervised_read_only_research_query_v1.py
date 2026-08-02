"""Validate Phase 11.6 without OpenClaw, Ollama, or external actions."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))

from src.integration.openclaw_supervised_read_only_research_query_v1 import (
    EVIDENCE_DATASET_STATUS,
    QUERY_ROUTE,
    encode_query_request_token,
    execute_query_token,
    validate_query_request,
    validate_query_response,
)

OFFICIAL_DATASET_PATH = "data/forward/long_forward_observation_dataset_v1.csv"
OFFICIAL_DATASET_SHA256 = (
    "e3fa86a461fd46f4d66dc2e03f185e49b7b3438d3cbc33340c01f51310514ff1"
)
OFFICIAL_MANIFEST_SHA256 = (
    "99fc1f3f0e57bc11ec79c2c08481450a1bda1d7eaf8b84e85962fd25c3d4806e"
)
EXPECTED_DATASET_STATE = "INITIALIZED_EMPTY_READY_FOR_CONTROLLED_EVIDENCE"
EXPECTED_EVIDENCE_ROW_COUNT = 0


class ValidationError(RuntimeError):
    """Raised when a Phase 11.6 validation invariant fails."""


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _tracked_files(root: Path) -> list[Path]:
    result = subprocess.run(
        ["git", "ls-files", "-z"],
        cwd=root,
        check=True,
        capture_output=True,
    )
    names = [
        item.decode("utf-8", errors="surrogateescape")
        for item in result.stdout.split(b"\0")
        if item
    ]
    return [root / name for name in names]


def _locate_exact_path_hash(
    root: Path,
    relative_path: str,
    expected_hash: str,
    label: str,
) -> Path:
    tracked = {
        path.relative_to(root).as_posix()
        for path in _tracked_files(root)
    }
    normalized = Path(relative_path).as_posix()
    if normalized not in tracked:
        raise ValidationError(
            f"{label} is not tracked at the official path: {normalized}"
        )

    path = root / Path(relative_path)
    if not path.is_file():
        raise ValidationError(f"{label} is missing: {normalized}")
    if _sha256(path) != expected_hash:
        raise ValidationError(f"{label} changed: {normalized}")
    return path


def _locate_unique_hash(root: Path, expected_hash: str, label: str) -> Path:
    matches = [
        path
        for path in _tracked_files(root)
        if path.is_file() and _sha256(path) == expected_hash
    ]
    if len(matches) != 1:
        relative = [str(path.relative_to(root)) for path in matches]
        raise ValidationError(
            f"{label} hash must identify exactly one tracked file; matches={relative}"
        )
    return matches[0]


def _load_request(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    return validate_query_request(value)


def main() -> int:
    """Run the direct deterministic validation."""

    dataset_path = _locate_exact_path_hash(
        REPOSITORY_ROOT,
        OFFICIAL_DATASET_PATH,
        OFFICIAL_DATASET_SHA256,
        "official dataset",
    )
    manifest_path = _locate_unique_hash(
        REPOSITORY_ROOT,
        OFFICIAL_MANIFEST_SHA256,
        "official manifest",
    )

    request_path = (
        REPOSITORY_ROOT
        / "examples"
        / "phase_11_6_first_controlled_supervised_query_request_v1.json"
    )
    request = _load_request(request_path)
    token = encode_query_request_token(request)
    response = execute_query_token(token, root=REPOSITORY_ROOT)
    validate_query_response(response)

    result = response["query_result"]
    expected = {
        "query_id": EVIDENCE_DATASET_STATUS,
        "query_route": QUERY_ROUTE,
        "local_model_called": False,
        "long_official_dataset_state": EXPECTED_DATASET_STATE,
        "long_official_evidence_row_count": EXPECTED_EVIDENCE_ROW_COUNT,
    }
    actual = {
        "query_id": response["query_id"],
        "query_route": response["query_route"],
        "local_model_called": response["local_model_called"],
        "long_official_dataset_state": result["long_official_dataset_state"],
        "long_official_evidence_row_count": result[
            "long_official_evidence_row_count"
        ],
    }
    if actual != expected:
        raise ValidationError(
            f"Direct query result changed; expected={expected}, actual={actual}"
        )

    if _sha256(dataset_path) != OFFICIAL_DATASET_SHA256:
        raise ValidationError("Official dataset changed during validation")
    if _sha256(manifest_path) != OFFICIAL_MANIFEST_SHA256:
        raise ValidationError("Official manifest changed during validation")

    print(
        json.dumps(
            {
                "decision": "PHASE_11_6_DIRECT_VALIDATION_PASSED",
                **actual,
                "human_review_required": response["human_review_required"],
                "official_dataset_changed": False,
                "official_manifest_changed": False,
                "openclaw_execution_performed": False,
            },
            ensure_ascii=True,
            separators=(",", ":"),
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
