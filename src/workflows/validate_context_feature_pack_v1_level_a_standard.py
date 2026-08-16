from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path

from src.context import context_feature_pack_v1_level_a_standard as m

CAPABILITY = "CONTEXT_FEATURE_PACK_V1_LEVEL_A_STANDARD_VALIDATOR"

SOURCE = Path(
    "src/context/context_feature_pack_v1_level_a_standard.py"
)
DOCS = Path(
    "docs/CONTEXT_FEATURE_PACK_V1_LEVEL_A_STANDARD.md"
)
TESTS = Path(
    "tests/test_context_feature_pack_v1_level_a_standard.py"
)
MANIFEST = Path(
    "CONTEXT_FEATURE_PACK_V1_LEVEL_A_STANDARD_MANIFEST.sha256"
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

    def check(name, passed, details):
        checks.append(
            {
                "check": name,
                "passed": bool(passed),
                "details": details,
                "blocker": not bool(passed),
            }
        )

    check(
        "capability",
        m.CAPABILITY == "CONTEXT_FEATURE_PACK_V1_LEVEL_A_STANDARD",
        m.CAPABILITY,
    )
    check(
        "attempt_1",
        m.IMPLEMENTATION_OR_REPAIR_ATTEMPT == 1,
        str(m.IMPLEMENTATION_OR_REPAIR_ATTEMPT),
    )
    check(
        "max_attempts_10",
        m.MAX_IMPLEMENTATION_OR_REPAIR_ATTEMPTS == 10,
        str(m.MAX_IMPLEMENTATION_OR_REPAIR_ATTEMPTS),
    )
    check(
        "registry_count_8",
        len(m.FEATURE_IDS) == 8,
        str(len(m.FEATURE_IDS)),
    )
    check(
        "registry_unique",
        len(set(m.FEATURE_IDS)) == 8,
        json.dumps(list(m.FEATURE_IDS)),
    )
    check(
        "level_a_only",
        all(item["level"] == "A" for item in m.FEATURE_REGISTRY),
        json.dumps([item["level"] for item in m.FEATURE_REGISTRY]),
    )
    check(
        "btc_cycle_present",
        "BTC_CYCLE_HALVING_CONTEXT_V1" in m.FEATURE_IDS,
        "present",
    )
    check(
        "event_risk_present",
        "EVENT_RISK_CALENDAR_CONTEXT_V1" in m.FEATURE_IDS,
        "present",
    )
    check(
        "external_regression_present",
        "EXTERNAL_CYCLE_REGRESSION_BASELINE_V1" in m.FEATURE_IDS,
        "present",
    )
    check(
        "liquidity_pattern_present",
        "LIQUIDITY_SWEEP_PATTERN_CONTEXT_V1" in m.FEATURE_IDS,
        "present",
    )
    check(
        "thesis_card_present",
        "EXTERNAL_THESIS_MODEL_CARD_V1" in m.FEATURE_IDS,
        "present",
    )
    check(
        "analog_present",
        "ANALOG_ENGINE_CONTEXT_V1" in m.FEATURE_IDS,
        "present",
    )
    check(
        "microstructure_present",
        "SYNCHRONIZED_MICROSTRUCTURE_CONTEXT_V1" in m.FEATURE_IDS,
        "present",
    )
    check(
        "onchain_interface_present",
        "ONCHAIN_CONTEXT_INTERFACE_V1" in m.FEATURE_IDS,
        "present",
    )
    check(
        "authorization_exact",
        m.PACKAGE_AUTHORIZATION
        == "PREPARE_CONTEXT_FEATURE_PACK_V1_LEVEL_A_STANDARD",
        m.PACKAGE_AUTHORIZATION,
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
        "websocket" not in imports
        and "websockets" not in imports,
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
        "no_official_writer",
        "append_official_prospective_evidence" not in source,
        "absent",
    )
    check(
        "point_in_time_available_check",
        "available_at <= context_cutoff" in source,
        "present",
    )
    check(
        "point_in_time_information_check",
        "information_cutoff <= context_cutoff" in source,
        "present",
    )
    check(
        "information_before_availability",
        "FEATURE_INFORMATION_AFTER_AVAILABILITY" in source,
        "present",
    )
    check(
        "context_anchor_policy",
        "_ceil_15m(context_cutoff)" in source,
        "present",
    )
    check(
        "all_slots_required",
        "FEATURE_REGISTRY_SCOPE_INVALID" in source,
        "present",
    )
    check(
        "payload_sha",
        "payload_sha256" in source
        and "_canonical_sha256" in source,
        "present",
    )
    check(
        "no_composite_scoring",
        '"composite_scoring_performed": False' in source,
        "present",
    )
    check(
        "no_direction",
        '"direction_inferred": False' in source,
        "present",
    )
    check(
        "no_trade_action",
        '"trade_action_inferred": False' in source,
        "present",
    )
    check(
        "primary_preserved",
        '"primary_candidate_state_preserved": True' in source,
        "present",
    )
    check(
        "primary_rule_false",
        '"primary_rule_modified": False' in source,
        "present",
    )
    check(
        "external_output_guard",
        "OUTPUT_INSIDE_REPOSITORY_PROHIBITED" in source,
        "present",
    )
    check(
        "create_only_write",
        'with path.open("xb")' in source,
        "present",
    )
    check(
        "package_network_false",
        '"real_network_request_executed": False' in source,
        "present",
    )
    check(
        "package_component_network_false",
        '"component_source_network_performed_by_pack": False'
        in source,
        "present",
    )
    check(
        "docs_context_only",
        "It does not create a trading strategy, signal, score, ranking, direction"
        in docs,
        "present",
    )
    check(
        "docs_single_observation_not_enough",
        "A single observation must never be used to promote" in docs,
        "present",
    )
    check(
        "docs_point_in_time",
        "available_at_utc <= context_cutoff_utc" in docs
        and "information_cutoff_utc <= context_cutoff_utc" in docs,
        "present",
    )
    check(
        "docs_registry_eight",
        all(feature_id in docs for feature_id in m.FEATURE_IDS),
        "present",
    )
    check(
        "test_registry",
        "test_03_registry_order_exact" in tests,
        "present",
    )
    check(
        "test_late_feature",
        "test_07_available_after_cutoff_is_ineligible" in tests,
        "present",
    )
    check(
        "test_primary_preserved",
        "test_11_primary_candidate_false_preserved" in tests,
        "present",
    )
    check(
        "test_no_scoring",
        "test_21_no_scoring_or_direction" in tests,
        "present",
    )
    check(
        "test_package_roundtrip",
        "test_27_package_roundtrip" in tests,
        "present",
    )
    check(
        "test_tamper",
        "test_28_package_tamper_detected" in tests,
        "present",
    )
    check(
        "test_official_unchanged",
        "test_29_official_artifacts_unchanged" in tests,
        "present",
    )

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
            "CONTEXT_FEATURE_PACK_V1_LEVEL_A_STANDARD_"
            "VALIDATED_NO_REAL_NETWORK"
            if not blockers
            else "BLOCKED"
        ),
        "real_network_request_executed": False,
        "real_market_data_acquired": False,
        "official_append_executed": False,
        "real_context_pack_prepared": False,
    }


if __name__ == "__main__":
    result = run()
    print(json.dumps(result, indent=2, sort_keys=True))
    raise SystemExit(0 if result["blockers"] == 0 else 1)
