from __future__ import annotations

import ast
import hashlib
import json
import os
import tempfile
from pathlib import Path

from src.long_side import synchronized_15m_observation_v1_1 as sync_v11
from src.exchange import public_read_only_microstructure_snapshot_v1_1 as micro_v11
from src.long_side import synchronized_15m_observation_v1_1_microstructure_auth_propagation_v1 as m

CAPABILITY = (
    "SYNCHRONIZED_15M_OBSERVATION_V1_1_"
    "MICROSTRUCTURE_AUTHORIZATION_PROPAGATION_V1_VALIDATOR"
)

SOURCE = Path(
    "src/long_side/"
    "synchronized_15m_observation_v1_1_microstructure_auth_propagation_v1.py"
)
DOCS = Path(
    "docs/"
    "SYNCHRONIZED_15M_OBSERVATION_V1_1_MICROSTRUCTURE_AUTH_PROPAGATION_V1.md"
)
TESTS = Path(
    "tests/"
    "test_synchronized_15m_observation_v1_1_microstructure_auth_propagation_v1.py"
)
MANIFEST = Path(
    "SYNCHRONIZED_15M_OBSERVATION_V1_1_"
    "MICROSTRUCTURE_AUTH_PROPAGATION_V1_MANIFEST.sha256"
)


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def run() -> dict:
    source = SOURCE.read_text(encoding="utf-8")
    docs = DOCS.read_text(encoding="utf-8")
    tests = TESTS.read_text(encoding="utf-8")
    tree = ast.parse(source)

    imports = sorted(
        {
            node.names[0].name.split(".")[0]
            for node in ast.walk(tree)
            if isinstance(node, ast.Import)
        }
        | {
            (node.module or "").split(".")[0]
            for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom) and node.module
        }
    )

    checks = []

    def check(name, passed, details, blocker=True):
        checks.append(
            {
                "check": name,
                "passed": bool(passed),
                "details": details,
                "blocker": bool(blocker and not passed),
            }
        )

    check(
        "capability",
        m.CAPABILITY
        == "SYNCHRONIZED_15M_OBSERVATION_V1_1_"
        "MICROSTRUCTURE_AUTHORIZATION_PROPAGATION_V1",
        m.CAPABILITY,
    )
    check(
        "implementation_attempt_1",
        m.IMPLEMENTATION_OR_REPAIR_ATTEMPT == 1,
        str(m.IMPLEMENTATION_OR_REPAIR_ATTEMPT),
    )
    check(
        "max_attempts_10",
        m.MAX_IMPLEMENTATION_OR_REPAIR_ATTEMPTS == 10,
        str(m.MAX_IMPLEMENTATION_OR_REPAIR_ATTEMPTS),
    )
    check(
        "new_outer_authorization",
        m.SESSION_AUTHORIZATION
        == "RUN_BOUNDED_SYNCHRONIZED_15M_OBSERVATION_SESSION_"
        "V1_1_MICROSTRUCTURE_AUTH_PROPAGATION_V1",
        m.SESSION_AUTHORIZATION,
    )
    check(
        "legacy_outer_authorization_not_accepted_contract",
        m.SESSION_AUTHORIZATION != sync_v11.SESSION_AUTHORIZATION,
        sync_v11.SESSION_AUTHORIZATION,
    )
    check(
        "closed_sync_legacy_micro_token_known",
        sync_v11.MICROSTRUCTURE_AUTHORIZATION
        == m.LEGACY_DELEGATED_MICROSTRUCTURE_AUTHORIZATION
        == "CAPTURE_ONE_SHOT_BINANCE_USDM_PUBLIC_MICROSTRUCTURE_V1",
        sync_v11.MICROSTRUCTURE_AUTHORIZATION,
    )
    check(
        "repaired_micro_v1_1_token_exact",
        micro_v11.AUTHORIZATION
        == m.MICROSTRUCTURE_V1_1_AUTHORIZATION
        == "CAPTURE_ONE_SHOT_BINANCE_USDM_PUBLIC_MICROSTRUCTURE_V1_1",
        micro_v11.AUTHORIZATION,
    )
    check(
        "no_requests_import",
        "requests" not in imports,
        json.dumps(imports),
    )
    check(
        "no_httpx_import",
        "httpx" not in imports,
        json.dumps(imports),
    )
    check(
        "no_websocket_import",
        "websocket" not in imports and "websockets" not in imports,
        json.dumps(imports),
    )
    check(
        "no_thread_process_scheduler",
        not any(
            name in imports
            for name in (
                "threading",
                "multiprocessing",
                "asyncio",
                "schedule",
                "apscheduler",
            )
        ),
        json.dumps(imports),
    )
    check(
        "no_subprocess_import",
        "subprocess" not in imports,
        json.dumps(imports),
    )
    check(
        "no_official_writer_import",
        "append_official_prospective_evidence" not in source,
        "official writer absent",
    )
    check(
        "bridge_present",
        "make_microstructure_authorization_bridge" in source,
        "present",
    )
    check(
        "bridge_delegates_new_token",
        "authorization=MICROSTRUCTURE_V1_1_AUTHORIZATION" in source,
        "present",
    )
    check(
        "bridge_checks_legacy_inner_seam",
        "UNEXPECTED_CLOSED_SYNC_V1_1_DELEGATED_AUTHORIZATION" in source,
        "present",
    )
    check(
        "outer_auth_checked_before_output",
        source.index("PROPAGATION_SESSION_AUTHORIZATION_REQUIRED")
        < source.index("out.mkdir()"),
        "ordered",
    )
    check(
        "external_output_guard",
        "OUTPUT_INSIDE_REPOSITORY_PROHIBITED" in source,
        "present",
    )
    check(
        "automatic_retry_false",
        '"automatic_retry_allowed": False' in source,
        "present",
    )
    check(
        "primary_rule_false",
        '"primary_long_rule_modified": False' in source,
        "present",
    )
    check(
        "false_permission_surface",
        all(
            item in m.FALSE_FIELDS
            for item in (
                "official_append_allowed",
                "signal_generation_enabled",
                "live_alerts_allowed",
                "paper_trade_execution_allowed",
                "real_capital_allowed",
                "execution_allowed",
            )
        ),
        json.dumps(list(m.FALSE_FIELDS)),
    )
    check(
        "outer_attestation_present",
        "authorization_propagation.json" in source,
        "present",
    )
    check(
        "outer_manifest_present",
        "manifest.sha256" in source,
        "present",
    )
    check(
        "inner_manifest_hashed",
        "inner_session_manifest_sha256" in source,
        "present",
    )
    check(
        "docs_additive_preserves_closed_sync",
        "closed `SYNCHRONIZED_15M_OBSERVATION_V1_1` implementation remains immutable"
        in docs,
        "present",
    )
    check(
        "docs_legacy_user_auth_not_accepted",
        "legacy user-facing synchronized authorization is **not** accepted" in docs,
        "present",
    )
    check(
        "docs_no_real_authorization_by_publish",
        "No real session is authorized merely by installing or publishing this repair."
        in docs,
        "present",
    )
    check(
        "docs_future_data_separate",
        "future-data acquisition must remain separately authorized" in docs,
        "present",
    )
    check(
        "test_legacy_outer_rejection",
        "test_10_old_outer_session_authorization_rejected_before_output" in tests,
        "present",
    )
    check(
        "test_new_micro_token_delegation",
        "test_17_mock_run_delegates_new_microstructure_v1_1_auth" in tests,
        "present",
    )
    check(
        "test_roundtrip",
        "test_23_roundtrip_validation" in tests,
        "present",
    )
    check(
        "test_permissions",
        "test_26_no_permissions_enabled" in tests,
        "present",
    )

    # Dynamic mock of the narrow bridge. No network.
    seen = []
    audit = []

    def target(**kwargs):
        seen.append(kwargs["authorization"])
        return {
            "capability": "PUBLIC_READ_ONLY_MICROSTRUCTURE_SNAPSHOT_V1_1",
            "request_count": 7,
        }

    bridge = m.make_microstructure_authorization_bridge(target, audit)
    bridge(
        repo_root=Path("."),
        output_directory=Path("mock-output"),
        authorization=m.LEGACY_DELEGATED_MICROSTRUCTURE_AUTHORIZATION,
    )

    check(
        "mock_bridge_new_token",
        seen == [m.MICROSTRUCTURE_V1_1_AUTHORIZATION],
        json.dumps(seen),
    )
    check(
        "mock_bridge_audit",
        len(audit) == 1
        and audit[0]["closed_sync_delegated_authorization_intercepted"] is True,
        json.dumps(audit, sort_keys=True),
    )

    # Source manifest.
    lines = [
        line
        for line in MANIFEST.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    manifest_ok = len(lines) == 4
    if manifest_ok:
        for line in lines:
            parts = line.split("  ", 1)
            if len(parts) != 2 or len(parts[0]) != 64:
                manifest_ok = False
                break
            path = Path(parts[1])
            if not path.is_file() or sha(path) != parts[0]:
                manifest_ok = False
                break

    check(
        "source_manifest_entries_4",
        len(lines) == 4,
        str(len(lines)),
    )
    check(
        "source_manifest_valid",
        manifest_ok,
        str(manifest_ok),
    )

    failed = [item for item in checks if not item["passed"]]
    blockers = [item for item in checks if item["blocker"]]

    return {
        "capability": CAPABILITY,
        "checks": len(checks),
        "failed_checks": len(failed),
        "blockers": len(blockers),
        "check_results": checks,
        "decision": (
            "SYNCHRONIZED_V1_1_MICROSTRUCTURE_AUTHORIZATION_"
            "PROPAGATION_V1_VALIDATED_NO_REAL_NETWORK"
            if not blockers
            else "BLOCKED"
        ),
        "real_network_request_executed": False,
        "real_market_data_acquired": False,
        "official_append_executed": False,
        "real_synchronized_session_executed": False,
    }


if __name__ == "__main__":
    result = run()
    print(json.dumps(result, indent=2, sort_keys=True))
    raise SystemExit(0 if result["blockers"] == 0 else 1)
