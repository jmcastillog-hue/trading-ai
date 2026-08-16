from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path

from src.context import btc_cycle_halving_context_v1 as m

CAPABILITY = "BTC_CYCLE_HALVING_CONTEXT_V1_VALIDATOR"

RESOURCE = Path(
    "src/context/resources/btc_cycle_halving_calendar_v1.json"
)
SOURCE = Path(
    "src/context/btc_cycle_halving_context_v1.py"
)
DOCS = Path(
    "docs/BTC_CYCLE_HALVING_CONTEXT_V1.md"
)
TESTS = Path(
    "tests/test_btc_cycle_halving_context_v1.py"
)
MANIFEST = Path(
    "BTC_CYCLE_HALVING_CONTEXT_V1_MANIFEST.sha256"
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
    calendar = json.loads(
        RESOURCE.read_text(encoding="utf-8")
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
        m.CAPABILITY == "BTC_CYCLE_HALVING_CONTEXT_V1",
        m.CAPABILITY,
    )
    check(
        "feature_id",
        m.FEATURE_ID == "BTC_CYCLE_HALVING_CONTEXT_V1",
        m.FEATURE_ID,
    )
    check(
        "source_kind",
        m.SOURCE_KIND == "DETERMINISTIC",
        m.SOURCE_KIND,
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
        == "PREPARE_BTC_CYCLE_HALVING_CONTEXT_V1",
        m.PACKAGE_AUTHORIZATION,
    )
    check(
        "resource_schema",
        calendar["schema_version"]
        == "BTC_CYCLE_HALVING_CALENDAR_V1",
        calendar["schema_version"],
    )
    check(
        "resource_reference_day_policy",
        calendar[
            "calendar_dates_are_reference_days_not_block_timestamps"
        ]
        is True,
        str(
            calendar[
                "calendar_dates_are_reference_days_not_block_timestamps"
            ]
        ),
    )
    check(
        "resource_interval_210000",
        calendar["protocol_halving_interval_blocks"]
        == 210000,
        str(calendar["protocol_halving_interval_blocks"]),
    )
    check(
        "resource_four_halvings",
        len(calendar["historical_halvings"]) == 4,
        str(len(calendar["historical_halvings"])),
    )
    check(
        "resource_block_heights",
        [
            item["block_height"]
            for item in calendar["historical_halvings"]
        ]
        == [210000, 420000, 630000, 840000],
        json.dumps(
            [
                item["block_height"]
                for item in calendar["historical_halvings"]
            ]
        ),
    )
    check(
        "resource_dates",
        [
            item["calendar_date_utc"]
            for item in calendar["historical_halvings"]
        ]
        == [
            "2012-11-28",
            "2016-07-09",
            "2020-05-11",
            "2024-04-20",
        ],
        json.dumps(
            [
                item["calendar_date_utc"]
                for item in calendar["historical_halvings"]
            ]
        ),
    )
    check(
        "resource_next_height",
        calendar[
            "next_protocol_halving_block_height_after_latest_record"
        ]
        == 1050000,
        str(
            calendar[
                "next_protocol_halving_block_height_after_latest_record"
            ]
        ),
    )
    check(
        "resource_no_future_time_estimate",
        calendar["future_halving_time_estimated"] is False,
        str(calendar["future_halving_time_estimated"]),
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
        "reference_boundary_information_cutoff",
        '"information_cutoff_utc": _utc(reference)'
        in source,
        "present",
    )
    check(
        "produced_at_availability",
        '"available_at_utc": _utc(produced_at)'
        in source,
        "present",
    )
    check(
        "only_past_halving_records",
        "<= reference" in source
        and "eligible_events" in source,
        "present",
    )
    check(
        "no_future_date_prediction",
        '"next_halving_time_estimated": False'
        in source
        and '"estimated_next_halving_utc": None'
        in source,
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
        "no_forward_outcome_input",
        '"future_outcomes_used": False' in source,
        "present",
    )
    check(
        "no_direction_semantics",
        '"directional_semantics": False' in source,
        "present",
    )
    check(
        "no_signal_semantics",
        '"signal_semantics": False' in source,
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
        "docs_context_only",
        "descriptive Bitcoin subsidy-cycle timing context only"
        in docs,
        "present",
    )
    check(
        "docs_no_future_time_estimate",
        "does not estimate when a future" in docs
        and "halving block will occur" in docs,
        "present",
    )
    check(
        "docs_not_block_timestamp",
        "not** represented as the exact block timestamp"
        in docs,
        "present",
    )
    check(
        "docs_retrospective_ineligible",
        "mark" in docs
        and "point-in-time ineligible" in docs,
        "present",
    )
    check(
        "test_days_since",
        "test_13_days_since_2024_halving_reference"
        in tests,
        "present",
    )
    check(
        "test_previous_cycle",
        "test_14_previous_cycle_length_1440_days"
        in tests,
        "present",
    )
    check(
        "test_quartile",
        "test_15_current_cycle_quartile_q3"
        in tests,
        "present",
    )
    check(
        "test_no_future_estimate",
        "test_16_no_future_halving_time_estimate"
        in tests,
        "present",
    )
    check(
        "test_pack_eligibility",
        "test_21_pack_compatible_before_cutoff"
        in tests
        and "test_22_pack_marks_late_producer_ineligible"
        in tests,
        "present",
    )
    check(
        "test_package_roundtrip",
        "test_29_package_roundtrip" in tests,
        "present",
    )
    check(
        "test_tamper",
        "test_31_package_tamper_detected" in tests,
        "present",
    )
    check(
        "test_official_unchanged",
        "test_32_official_artifacts_unchanged"
        in tests,
        "present",
    )

    try:
        calendar_validation = (
            m.validate_halving_calendar_v1(calendar)
        )
        calendar_valid = (
            calendar_validation[
                "historical_halving_count"
            ]
            == 4
        )
        calendar_details = json.dumps(
            calendar_validation,
            sort_keys=True,
        )
    except Exception as exc:
        calendar_valid = False
        calendar_details = repr(exc)

    check(
        "calendar_runtime_validation",
        calendar_valid,
        calendar_details,
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
        item
        for item in checks
        if not item["passed"]
    ]
    blockers = [
        item
        for item in checks
        if item["blocker"]
    ]

    return {
        "capability": CAPABILITY,
        "checks": len(checks),
        "failed_checks": len(failed),
        "blockers": len(blockers),
        "check_results": checks,
        "decision": (
            "BTC_CYCLE_HALVING_CONTEXT_V1_"
            "VALIDATED_NO_REAL_NETWORK"
            if not blockers
            else "BLOCKED"
        ),
        "real_network_request_executed": False,
        "real_market_data_acquired": False,
        "real_component_package_prepared": False,
        "official_append_executed": False,
    }


if __name__ == "__main__":
    result = run()
    print(json.dumps(result, indent=2, sort_keys=True))
    raise SystemExit(
        0 if result["blockers"] == 0 else 1
    )
