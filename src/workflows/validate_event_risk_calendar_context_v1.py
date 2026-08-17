from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path

from src.context import event_risk_calendar_context_v1 as m

CAPABILITY = "EVENT_RISK_CALENDAR_CONTEXT_V1_VALIDATOR"

TAXONOMY = Path(
    "src/context/resources/event_risk_calendar_taxonomy_v1.json"
)
SOURCE = Path(
    "src/context/event_risk_calendar_context_v1.py"
)
DOCS = Path(
    "docs/EVENT_RISK_CALENDAR_CONTEXT_V1.md"
)
TESTS = Path(
    "tests/test_event_risk_calendar_context_v1.py"
)
MANIFEST = Path(
    "EVENT_RISK_CALENDAR_CONTEXT_V1_MANIFEST.sha256"
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
    taxonomy = json.loads(
        TAXONOMY.read_text(encoding="utf-8")
    )
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
            if isinstance(node, ast.ImportFrom)
            and node.module
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
        m.CAPABILITY == "EVENT_RISK_CALENDAR_CONTEXT_V1",
        m.CAPABILITY,
    )
    check(
        "feature_id",
        m.FEATURE_ID == "EVENT_RISK_CALENDAR_CONTEXT_V1",
        m.FEATURE_ID,
    )
    check(
        "source_kind",
        m.SOURCE_KIND == "DETERMINISTIC",
        m.SOURCE_KIND,
    )
    check(
        "snapshot_schema",
        m.SNAPSHOT_SCHEMA_VERSION
        == "EVENT_RISK_CALENDAR_SNAPSHOT_V1",
        m.SNAPSHOT_SCHEMA_VERSION,
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
        "authorization_exact",
        m.PACKAGE_AUTHORIZATION
        == "PREPARE_EVENT_RISK_CALENDAR_CONTEXT_V1",
        m.PACKAGE_AUTHORIZATION,
    )
    check(
        "taxonomy_schema",
        taxonomy["schema_version"]
        == "EVENT_RISK_CALENDAR_TAXONOMY_V1",
        taxonomy["schema_version"],
    )
    check(
        "taxonomy_count_8",
        len(taxonomy["event_types"]) == 8,
        str(len(taxonomy["event_types"])),
    )
    check(
        "taxonomy_no_direction",
        taxonomy["directional_meaning_assigned"] is False,
        str(taxonomy["directional_meaning_assigned"]),
    )
    check(
        "taxonomy_no_importance_score",
        taxonomy["importance_score_assigned"] is False,
        str(taxonomy["importance_score_assigned"]),
    )
    check(
        "taxonomy_no_surprise",
        taxonomy["event_surprise_used"] is False,
        str(taxonomy["event_surprise_used"]),
    )
    check(
        "taxonomy_no_market_reaction",
        taxonomy["market_reaction_used"] is False,
        str(taxonomy["market_reaction_used"]),
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
        "pack_dependency_present",
        "context_feature_pack_v1_level_a_standard"
        in source,
        "present",
    )
    check(
        "pack_compatibility_check_present",
        "validate_component_against_level_a_pack_v1"
        in source,
        "present",
    )
    check(
        "known_at_reference_filter",
        "if known_at <= reference" in source,
        "present",
    )
    check(
        "post_reference_exclusion_counter",
        "excluded_post_reference_schedule_knowledge"
        in source,
        "present",
    )
    check(
        "information_cutoff_reference",
        '"information_cutoff_utc": _utc(reference)'
        in source,
        "present",
    )
    check(
        "availability_produced_at",
        '"available_at_utc": _utc(produced_at)'
        in source,
        "present",
    )
    check(
        "snapshot_before_production",
        "SNAPSHOT_CREATED_AFTER_PRODUCTION" in source,
        "present",
    )
    check(
        "future_windows_present",
        all(
            key in source
            for key in ('"1h"', '"6h"', '"24h"', '"72h"', '"7d"')
        ),
        "present",
    )
    check(
        "recent_windows_present",
        "RECENT_WINDOWS_SECONDS" in source,
        "present",
    )
    check(
        "no_event_values",
        '"event_values_used": False' in source,
        "present",
    )
    check(
        "no_event_surprise",
        '"event_surprise_used": False' in source,
        "present",
    )
    check(
        "no_market_reaction",
        '"market_reaction_used": False' in source,
        "present",
    )
    check(
        "no_price_input",
        '"price_input_used": False' in source,
        "present",
    )
    check(
        "no_market_data_input",
        '"market_data_input_used": False' in source,
        "present",
    )
    check(
        "no_forward_outcomes",
        '"future_outcomes_used": False' in source,
        "present",
    )
    check(
        "no_direction",
        '"directional_semantics": False' in source,
        "present",
    )
    check(
        "no_signal",
        '"signal_semantics": False' in source,
        "present",
    )
    check(
        "no_importance_score",
        '"importance_score_assigned": False' in source,
        "present",
    )
    check(
        "external_snapshot_required",
        "event_calendar_snapshot_json" in source,
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
        '"real_network_request_executed": False'
        in source,
        "present",
    )
    check(
        "official_integrity_checks",
        "OFFICIAL_ARTIFACT_CHANGED" in source,
        "present",
    )
    check(
        "docs_separate_acquisition",
        "Separation of acquisition and feature production"
        in docs,
        "present",
    )
    check(
        "docs_no_web_acquisition",
        "performs no web or API acquisition" in docs,
        "present",
    )
    check(
        "docs_point_in_time",
        "schedule_known_at_utc <= reference_boundary_utc"
        in docs,
        "present",
    )
    check(
        "docs_no_values",
        "actual release values" in docs
        and "consensus values" in docs,
        "present",
    )
    check(
        "docs_no_signal",
        "cannot directly become a trading signal" in docs,
        "present",
    )
    check(
        "test_post_reference_exclusion",
        "test_15_post_reference_schedule_knowledge_excluded"
        in tests,
        "present",
    )
    check(
        "test_previous_event",
        "test_17_previous_event" in tests,
        "present",
    )
    check(
        "test_next_event",
        "test_18_next_event" in tests,
        "present",
    )
    check(
        "test_pack_eligibility",
        "test_26_pack_compatible_before_cutoff"
        in tests
        and "test_27_pack_marks_late_producer_ineligible"
        in tests,
        "present",
    )
    check(
        "test_package_roundtrip",
        "test_34_package_roundtrip" in tests,
        "present",
    )
    check(
        "test_tamper",
        "test_36_package_tamper_detected" in tests,
        "present",
    )
    check(
        "test_official_unchanged",
        "test_37_official_artifacts_unchanged"
        in tests,
        "present",
    )

    try:
        taxonomy_validation = (
            m.validate_event_risk_taxonomy_v1(
                taxonomy
            )
        )
        taxonomy_valid = (
            taxonomy_validation["event_type_count"] == 8
        )
        taxonomy_details = json.dumps(
            taxonomy_validation,
            sort_keys=True,
        )
    except Exception as exc:
        taxonomy_valid = False
        taxonomy_details = repr(exc)

    check(
        "taxonomy_runtime_validation",
        taxonomy_valid,
        taxonomy_details,
    )

    lines = [
        line
        for line in MANIFEST.read_text(
            encoding="utf-8"
        ).splitlines()
        if line.strip()
    ]
    manifest_ok = len(lines) == 5

    if manifest_ok:
        for line in lines:
            parts = line.split("  ", 1)
            if len(parts) != 2 or len(parts[0]) != 64:
                manifest_ok = False
                break
            path = Path(parts[1])
            if (
                not path.is_file()
                or sha(path) != parts[0]
            ):
                manifest_ok = False
                break

    check(
        "source_manifest_entries_5",
        len(lines) == 5,
        str(len(lines)),
    )
    check(
        "source_manifest_valid",
        manifest_ok,
        str(manifest_ok),
    )

    failed = [
        item for item in checks
        if not item["passed"]
    ]
    blockers = [
        item for item in checks
        if item["blocker"]
    ]

    return {
        "capability": CAPABILITY,
        "checks": len(checks),
        "failed_checks": len(failed),
        "blockers": len(blockers),
        "check_results": checks,
        "decision": (
            "EVENT_RISK_CALENDAR_CONTEXT_V1_"
            "VALIDATED_NO_REAL_NETWORK"
            if not blockers
            else "BLOCKED"
        ),
        "real_network_request_executed": False,
        "real_market_data_acquired": False,
        "real_event_calendar_acquired": False,
        "real_component_package_prepared": False,
        "official_append_executed": False,
    }


if __name__ == "__main__":
    result = run()
    print(json.dumps(result, indent=2, sort_keys=True))
    raise SystemExit(
        0 if result["blockers"] == 0 else 1
    )
