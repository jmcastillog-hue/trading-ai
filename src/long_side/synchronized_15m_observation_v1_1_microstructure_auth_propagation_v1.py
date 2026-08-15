from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any, Callable, Mapping

from src.exchange import public_read_only_microstructure_snapshot_v1_1 as micro_v11
from src.long_side import synchronized_15m_observation_v1_1 as sync_v11

CAPABILITY = (
    "SYNCHRONIZED_15M_OBSERVATION_V1_1_"
    "MICROSTRUCTURE_AUTHORIZATION_PROPAGATION_V1"
)
IMPLEMENTATION_SCHEMA_VERSION = (
    "SYNCHRONIZED_15M_OBSERVATION_V1_1_"
    "MICROSTRUCTURE_AUTHORIZATION_PROPAGATION_IMPLEMENTATION_V1"
)
ATTESTATION_SCHEMA_VERSION = (
    "SYNCHRONIZED_15M_OBSERVATION_V1_1_"
    "MICROSTRUCTURE_AUTHORIZATION_PROPAGATION_ATTESTATION_V1"
)

MAX_IMPLEMENTATION_OR_REPAIR_ATTEMPTS = 10
IMPLEMENTATION_OR_REPAIR_ATTEMPT = 1

SESSION_AUTHORIZATION = (
    "RUN_BOUNDED_SYNCHRONIZED_15M_OBSERVATION_SESSION_"
    "V1_1_MICROSTRUCTURE_AUTH_PROPAGATION_V1"
)
LEGACY_USER_SESSION_AUTHORIZATION = sync_v11.SESSION_AUTHORIZATION
LEGACY_DELEGATED_MICROSTRUCTURE_AUTHORIZATION = (
    "CAPTURE_ONE_SHOT_BINANCE_USDM_PUBLIC_MICROSTRUCTURE_V1"
)
MICROSTRUCTURE_V1_1_AUTHORIZATION = (
    "CAPTURE_ONE_SHOT_BINANCE_USDM_PUBLIC_MICROSTRUCTURE_V1_1"
)

INNER_SESSION_DIRECTORY = "synchronized_v1_1_session"
ATTESTATION_FILENAME = "authorization_propagation.json"
MANIFEST_FILENAME = "manifest.sha256"

OFFICIAL_APPEND_GATE_NAME = "TRADING_AI_OFFICIAL_LONG_EVIDENCE_APPEND_ALLOWED"

FALSE_FIELDS = (
    "official_append_allowed",
    "official_dataset_write_allowed",
    "signal_generation_enabled",
    "live_alerts_allowed",
    "paper_trade_execution_allowed",
    "real_capital_allowed",
    "market_execution_allowed",
    "exchange_execution_allowed",
    "automation_allowed",
    "execution_allowed",
)


class AuthorizationPropagationError(RuntimeError):
    def __init__(self, code: str, message: str) -> None:
        self.code = code
        super().__init__(message)


def _req(ok: bool, code: str, message: str) -> None:
    if not ok:
        raise AuthorizationPropagationError(code, message)


def _sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _json_bytes(value: Mapping[str, Any]) -> bytes:
    return (
        json.dumps(
            dict(value),
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
            allow_nan=False,
        )
        + "\n"
    ).encode("utf-8")


def _write_new(path: Path, payload: bytes) -> None:
    with path.open("xb") as handle:
        handle.write(payload)
        handle.flush()
        os.fsync(handle.fileno())


def _inside(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def _gate_off() -> None:
    _req(
        os.environ.get(OFFICIAL_APPEND_GATE_NAME) != "1",
        "OFFICIAL_APPEND_GATE_ENABLED",
        OFFICIAL_APPEND_GATE_NAME,
    )


def _verify_authorization_contracts() -> None:
    _req(
        sync_v11.MICROSTRUCTURE_AUTHORIZATION
        == LEGACY_DELEGATED_MICROSTRUCTURE_AUTHORIZATION,
        "CLOSED_SYNC_V1_1_DELEGATED_AUTHORIZATION_CHANGED",
        sync_v11.MICROSTRUCTURE_AUTHORIZATION,
    )
    _req(
        micro_v11.AUTHORIZATION == MICROSTRUCTURE_V1_1_AUTHORIZATION,
        "REPAIRED_MICROSTRUCTURE_V1_1_AUTHORIZATION_CHANGED",
        micro_v11.AUTHORIZATION,
    )
    _req(
        LEGACY_USER_SESSION_AUTHORIZATION != SESSION_AUTHORIZATION,
        "OUTER_AUTHORIZATION_NOT_VERSIONED",
        SESSION_AUTHORIZATION,
    )


def make_microstructure_authorization_bridge(
    capture_callable: Callable[..., Mapping[str, Any]] | None = None,
    audit_sink: list[dict[str, Any]] | None = None,
) -> Callable[..., Mapping[str, Any]]:
    _verify_authorization_contracts()
    target = (
        capture_callable
        or micro_v11.capture_public_read_only_microstructure_snapshot_v1_1
    )
    audit = audit_sink if audit_sink is not None else []

    def bridge(
        *,
        repo_root: Path | str,
        output_directory: Path | str,
        authorization: str | None = None,
        **kwargs: Any,
    ) -> Mapping[str, Any]:
        _req(
            authorization == LEGACY_DELEGATED_MICROSTRUCTURE_AUTHORIZATION,
            "UNEXPECTED_CLOSED_SYNC_V1_1_DELEGATED_AUTHORIZATION",
            str(authorization),
        )
        result = dict(
            target(
                repo_root=repo_root,
                output_directory=output_directory,
                authorization=MICROSTRUCTURE_V1_1_AUTHORIZATION,
                **kwargs,
            )
        )
        _req(
            result.get("capability")
            == "PUBLIC_READ_ONLY_MICROSTRUCTURE_SNAPSHOT_V1_1",
            "MICROSTRUCTURE_V1_1_CAPABILITY_INVALID",
            str(result.get("capability")),
        )
        _req(
            int(result.get("request_count", -1)) == 7,
            "MICROSTRUCTURE_V1_1_REQUEST_CONTRACT_INVALID",
            str(result.get("request_count")),
        )
        audit.append(
            {
                "closed_sync_delegated_authorization_intercepted": True,
                "legacy_delegated_authorization": (
                    LEGACY_DELEGATED_MICROSTRUCTURE_AUTHORIZATION
                ),
                "repaired_microstructure_authorization_delegated": (
                    MICROSTRUCTURE_V1_1_AUTHORIZATION
                ),
                "microstructure_capability": result["capability"],
                "request_count": int(result["request_count"]),
            }
        )
        return result

    return bridge


def _default_inner_runner() -> Callable[..., Mapping[str, Any]]:
    return sync_v11.run_bounded_synchronized_15m_session_v1_1


def _default_inner_validator() -> Callable[[Path | str], Mapping[str, Any]]:
    return sync_v11.validate_synchronized_observation_session_v1_1


def run_bounded_synchronized_15m_session_with_microstructure_auth_propagation_v1(
    *,
    repo_root: Path | str,
    output_directory: Path | str,
    max_cycles: int,
    source_attestation: str,
    minimum_latest_closed_candle_utc: str | None,
    authorization: str | None = None,
    clock: Callable[..., Any] | None = None,
    sleeper: Callable[[float], None] | None = None,
    spot_capture_callable: Callable[..., Mapping[str, Any]] | None = None,
    package_callable: Callable[..., Mapping[str, Any]] | None = None,
    microstructure_capture_callable: Callable[..., Mapping[str, Any]] | None = None,
    microstructure_validate_callable: Callable[[Path | str], Mapping[str, Any]]
    | None = None,
    human_context_callable: Callable[[Mapping[str, Any]], Mapping[str, Any]]
    | None = None,
    inner_run_callable: Callable[..., Mapping[str, Any]] | None = None,
    inner_validate_callable: Callable[[Path | str], Mapping[str, Any]]
    | None = None,
) -> dict[str, Any]:
    _req(
        authorization == SESSION_AUTHORIZATION,
        "PROPAGATION_SESSION_AUTHORIZATION_REQUIRED",
        "authorization",
    )
    _verify_authorization_contracts()
    _gate_off()

    repo = Path(repo_root).resolve()
    out = Path(output_directory).resolve()

    _req((repo / ".git").is_dir(), "REPOSITORY_ROOT_INVALID", str(repo))
    _req(
        not _inside(out, repo),
        "OUTPUT_INSIDE_REPOSITORY_PROHIBITED",
        str(out),
    )
    _req(
        out.parent.is_dir() and not out.parent.is_symlink(),
        "OUTPUT_PARENT_INVALID",
        str(out.parent),
    )
    _req(
        not out.exists() and not out.is_symlink(),
        "OUTPUT_ALREADY_EXISTS",
        str(out),
    )
    _req(
        isinstance(max_cycles, int)
        and 1 <= max_cycles <= sync_v11.MAX_OBSERVATION_CYCLES,
        "SESSION_CYCLE_LIMIT_INVALID",
        str(max_cycles),
    )

    runner = inner_run_callable or _default_inner_runner()
    validator = inner_validate_callable or _default_inner_validator()

    audit: list[dict[str, Any]] = []
    bridge = make_microstructure_authorization_bridge(
        microstructure_capture_callable,
        audit,
    )

    out.mkdir()
    inner_output = out / INNER_SESSION_DIRECTORY

    inner_result = dict(
        runner(
            repo_root=repo,
            output_directory=inner_output,
            max_cycles=max_cycles,
            source_attestation=source_attestation,
            minimum_latest_closed_candle_utc=minimum_latest_closed_candle_utc,
            authorization=sync_v11.SESSION_AUTHORIZATION,
            clock=clock,
            sleeper=sleeper,
            spot_capture_callable=spot_capture_callable,
            package_callable=package_callable,
            microstructure_capture_callable=bridge,
            microstructure_validate_callable=microstructure_validate_callable,
            human_context_callable=human_context_callable,
        )
    )

    inner_validation = dict(validator(inner_output))
    completed = int(inner_result["completed_cycles"])
    _req(completed >= 1, "INNER_SESSION_NO_COMPLETED_CYCLE", str(completed))
    _req(
        int(inner_validation["completed_cycles"]) == completed,
        "INNER_SESSION_VALIDATION_MISMATCH",
        "completed_cycles",
    )
    _req(
        len(audit) == completed,
        "AUTHORIZATION_PROPAGATION_COUNT_MISMATCH",
        f"{len(audit)} != {completed}",
    )

    inner_manifest = inner_output / sync_v11.MANIFEST_FILENAME
    _req(
        inner_manifest.is_file() and not inner_manifest.is_symlink(),
        "INNER_SESSION_MANIFEST_MISSING",
        str(inner_manifest),
    )

    attestation = {
        "attestation_schema_version": ATTESTATION_SCHEMA_VERSION,
        "capability": CAPABILITY,
        "implementation_schema_version": IMPLEMENTATION_SCHEMA_VERSION,
        "implementation_or_repair_attempt": IMPLEMENTATION_OR_REPAIR_ATTEMPT,
        "max_implementation_or_repair_attempts": (
            MAX_IMPLEMENTATION_OR_REPAIR_ATTEMPTS
        ),
        "outer_session_authorization_contract": SESSION_AUTHORIZATION,
        "legacy_user_session_authorization_accepted": False,
        "closed_sync_v1_1_inner_session_authorization_is_internal_only": True,
        "closed_sync_v1_1_inner_session_authorization": (
            sync_v11.SESSION_AUTHORIZATION
        ),
        "legacy_microstructure_authorization_user_accepted": False,
        "legacy_delegated_microstructure_authorization_intercepted": True,
        "legacy_delegated_microstructure_authorization": (
            LEGACY_DELEGATED_MICROSTRUCTURE_AUTHORIZATION
        ),
        "repaired_microstructure_v1_1_authorization": (
            MICROSTRUCTURE_V1_1_AUTHORIZATION
        ),
        "authorization_propagation_count": len(audit),
        "authorization_propagation_audit": audit,
        "inner_session_directory": INNER_SESSION_DIRECTORY,
        "inner_session_capability": inner_result.get("capability"),
        "inner_session_manifest_sha256": _sha(inner_manifest),
        "completed_cycles": completed,
        "network_request_count": int(inner_result["network_request_count"]),
        "network_requests_per_completed_cycle": int(
            inner_result["network_requests_per_completed_cycle"]
        ),
        "candidate_count": int(inner_result["candidate_count"]),
        "stop_reason": inner_result["stop_reason"],
        "manual_confirmation_required": True,
        "manual_confirmed": False,
        "automatic_retry_allowed": False,
        "microstructure_authorization_repaired": True,
        "closed_synchronized_v1_1_source_modified": False,
        "repaired_microstructure_v1_1_source_modified": False,
        "primary_long_rule_modified": False,
        **{field: False for field in FALSE_FIELDS},
    }

    attestation_path = out / ATTESTATION_FILENAME
    _write_new(attestation_path, _json_bytes(attestation))

    manifest_lines = [
        f"{_sha(attestation_path)}  {ATTESTATION_FILENAME}",
        (
            f"{_sha(inner_manifest)}  "
            f"{INNER_SESSION_DIRECTORY}/{sync_v11.MANIFEST_FILENAME}"
        ),
    ]
    _write_new(
        out / MANIFEST_FILENAME,
        ("\n".join(manifest_lines) + "\n").encode("utf-8"),
    )

    validation = validate_authorization_propagation_session_v1(
        out,
        inner_validate_callable=validator,
    )

    return {
        "capability": CAPABILITY,
        "output_directory": str(out),
        "inner_session_directory": str(inner_output),
        "completed_cycles": completed,
        "candidate_count": int(inner_result["candidate_count"]),
        "stop_reason": inner_result["stop_reason"],
        "network_request_count": int(inner_result["network_request_count"]),
        "network_requests_per_completed_cycle": int(
            inner_result["network_requests_per_completed_cycle"]
        ),
        "authorization_propagation_count": len(audit),
        "microstructure_authorization_propagated": True,
        "legacy_user_session_authorization_accepted": False,
        "legacy_microstructure_authorization_user_accepted": False,
        "microstructure_v1_1_authorization": MICROSTRUCTURE_V1_1_AUTHORIZATION,
        "manual_confirmation_required": True,
        "manual_confirmed": False,
        "outer_manifest_entries": validation["outer_manifest_entries"],
        **{field: False for field in FALSE_FIELDS},
    }


def validate_authorization_propagation_session_v1(
    directory: Path | str,
    *,
    inner_validate_callable: Callable[[Path | str], Mapping[str, Any]]
    | None = None,
) -> dict[str, Any]:
    _verify_authorization_contracts()
    root = Path(directory).resolve()
    _req(
        root.is_dir() and not root.is_symlink(),
        "PROPAGATION_OUTPUT_INVALID",
        str(root),
    )

    attestation_path = root / ATTESTATION_FILENAME
    manifest_path = root / MANIFEST_FILENAME
    inner = root / INNER_SESSION_DIRECTORY
    inner_manifest = inner / sync_v11.MANIFEST_FILENAME

    for path in (attestation_path, manifest_path, inner_manifest):
        _req(
            path.is_file() and not path.is_symlink(),
            "PROPAGATION_FILE_MISSING",
            str(path),
        )

    lines = [
        line
        for line in manifest_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    _req(
        len(lines) == 2,
        "PROPAGATION_MANIFEST_INVALID",
        "entry count",
    )

    expected_names = {
        ATTESTATION_FILENAME,
        f"{INNER_SESSION_DIRECTORY}/{sync_v11.MANIFEST_FILENAME}",
    }
    seen: set[str] = set()
    for line in lines:
        parts = line.split("  ", 1)
        _req(
            len(parts) == 2 and len(parts[0]) == 64,
            "PROPAGATION_MANIFEST_INVALID",
            line,
        )
        expected_sha, name = parts
        path = root / name
        _req(
            path.is_file() and not path.is_symlink(),
            "PROPAGATION_MANIFEST_FILE_MISSING",
            name,
        )
        _req(
            _sha(path) == expected_sha,
            "PROPAGATION_MANIFEST_HASH_MISMATCH",
            name,
        )
        seen.add(name)

    _req(
        seen == expected_names,
        "PROPAGATION_MANIFEST_SCOPE_INVALID",
        str(sorted(seen)),
    )

    attestation = json.loads(attestation_path.read_text(encoding="utf-8"))
    _req(
        attestation["attestation_schema_version"] == ATTESTATION_SCHEMA_VERSION,
        "PROPAGATION_ATTESTATION_SCHEMA_INVALID",
        "schema",
    )
    _req(
        attestation["capability"] == CAPABILITY,
        "PROPAGATION_CAPABILITY_INVALID",
        str(attestation["capability"]),
    )
    _req(
        attestation["outer_session_authorization_contract"]
        == SESSION_AUTHORIZATION,
        "PROPAGATION_OUTER_AUTHORIZATION_INVALID",
        "authorization",
    )
    _req(
        attestation["legacy_user_session_authorization_accepted"] is False,
        "LEGACY_USER_SESSION_AUTHORIZATION_ACCEPTED",
        "legacy outer authorization",
    )
    _req(
        attestation["legacy_microstructure_authorization_user_accepted"]
        is False,
        "LEGACY_MICROSTRUCTURE_USER_AUTHORIZATION_ACCEPTED",
        "legacy micro authorization",
    )
    _req(
        attestation["legacy_delegated_microstructure_authorization_intercepted"]
        is True,
        "LEGACY_DELEGATED_AUTHORIZATION_NOT_INTERCEPTED",
        "bridge",
    )
    _req(
        attestation["repaired_microstructure_v1_1_authorization"]
        == MICROSTRUCTURE_V1_1_AUTHORIZATION,
        "REPAIRED_MICROSTRUCTURE_AUTHORIZATION_INVALID",
        "micro authorization",
    )
    _req(
        attestation["authorization_propagation_count"]
        == attestation["completed_cycles"],
        "AUTHORIZATION_PROPAGATION_COUNT_MISMATCH",
        "completed cycles",
    )
    _req(
        attestation["automatic_retry_allowed"] is False,
        "AUTOMATIC_RETRY_UNEXPECTEDLY_ALLOWED",
        "retry",
    )
    _req(
        attestation["primary_long_rule_modified"] is False,
        "PRIMARY_RULE_MODIFIED",
        "primary rule",
    )
    for field in FALSE_FIELDS:
        _req(
            attestation[field] is False,
            "PROPAGATION_PERMISSION_INVALID",
            field,
        )

    validator = inner_validate_callable or _default_inner_validator()
    inner_validation = dict(validator(inner))
    _req(
        int(inner_validation["completed_cycles"])
        == int(attestation["completed_cycles"]),
        "INNER_SESSION_VALIDATION_MISMATCH",
        "completed cycles",
    )

    return {
        "completed_cycles": int(attestation["completed_cycles"]),
        "candidate_count": int(attestation["candidate_count"]),
        "network_request_count": int(attestation["network_request_count"]),
        "authorization_propagation_count": int(
            attestation["authorization_propagation_count"]
        ),
        "outer_manifest_entries": len(lines),
        "microstructure_authorization_propagated": True,
        "legacy_user_session_authorization_accepted": False,
        "legacy_microstructure_authorization_user_accepted": False,
    }


__all__ = [
    "ATTESTATION_SCHEMA_VERSION",
    "CAPABILITY",
    "IMPLEMENTATION_OR_REPAIR_ATTEMPT",
    "LEGACY_DELEGATED_MICROSTRUCTURE_AUTHORIZATION",
    "LEGACY_USER_SESSION_AUTHORIZATION",
    "MAX_IMPLEMENTATION_OR_REPAIR_ATTEMPTS",
    "MICROSTRUCTURE_V1_1_AUTHORIZATION",
    "SESSION_AUTHORIZATION",
    "AuthorizationPropagationError",
    "make_microstructure_authorization_bridge",
    "run_bounded_synchronized_15m_session_with_microstructure_auth_propagation_v1",
    "validate_authorization_propagation_session_v1",
]
