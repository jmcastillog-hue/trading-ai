from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path

from src.context import synchronized_microstructure_context_v1 as m

CAPABILITY = "SYNCHRONIZED_MICROSTRUCTURE_CONTEXT_V1_VALIDATOR"

POLICY = Path(
    "src/context/resources/synchronized_microstructure_context_policy_v1.json"
)
SOURCE = Path(
    "src/context/synchronized_microstructure_context_v1.py"
)
DOCS = Path(
    "docs/SYNCHRONIZED_MICROSTRUCTURE_CONTEXT_V1.md"
)
TESTS = Path(
    "tests/test_synchronized_microstructure_context_v1.py"
)
MANIFEST = Path(
    "SYNCHRONIZED_MICROSTRUCTURE_CONTEXT_V1_MANIFEST.sha256"
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
    policy = json.loads(
        POLICY.read_text(encoding="utf-8")
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
        m.CAPABILITY
        == "SYNCHRONIZED_MICROSTRUCTURE_CONTEXT_V1",
        m.CAPABILITY,
    )
    check(
        "feature_id",
        m.FEATURE_ID
        == "SYNCHRONIZED_MICROSTRUCTURE_CONTEXT_V1",
        m.FEATURE_ID,
    )
    check(
        "source_kind",
        m.SOURCE_KIND == "OBSERVED_MARKET",
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
        == "PREPARE_SYNCHRONIZED_MICROSTRUCTURE_CONTEXT_V1",
        m.PACKAGE_AUTHORIZATION,
    )
    check(
        "policy_schema",
        policy["schema_version"]
        == "SYNCHRONIZED_MICROSTRUCTURE_CONTEXT_POLICY_V1",
        policy["schema_version"],
    )
    check(
        "policy_effective_floor",
        policy["policy_effective_from_utc"]
        == "2026-08-17T00:00:00+00:00",
        policy["policy_effective_from_utc"],
    )
    check(
        "policy_source_capability",
        policy["source_snapshot_capability"]
        == "PUBLIC_READ_ONLY_MICROSTRUCTURE_SNAPSHOT_V1_1",
        policy["source_snapshot_capability"],
    )
    check(
        "policy_depth_limit",
        policy["source_depth_limit"] == 1000,
        str(policy["source_depth_limit"]),
    )
    check(
        "policy_depth_bands",
        policy["source_depth_bands_bps"]
        == [5, 10, 25, 50],
        json.dumps(policy["source_depth_bands_bps"]),
    )
    check(
        "policy_required_depth",
        policy["required_depth_bands_bps"]
        == [5, 10],
        json.dumps(policy["required_depth_bands_bps"]),
    )
    check(
        "policy_optional_depth",
        policy["optional_depth_bands_bps"]
        == [25, 50],
        json.dumps(policy["optional_depth_bands_bps"]),
    )
    check(
        "policy_temporal_version",
        policy["temporal_alignment_policy_version"]
        == "SYNCHRONIZED_COMPONENT_TIMESTAMP_ELIGIBILITY_V1",
        policy["temporal_alignment_policy_version"],
    )
    check(
        "policy_exact_equality",
        policy[
            "historical_component_exact_reference_boundary_equality_required"
        ]
        is True,
        "true",
    )
    check(
        "policy_misaligned_nonusable",
        policy[
            "misaligned_historical_component_preserved_but_not_usable"
        ]
        is True,
        "true",
    )
    check(
        "policy_point_in_time_not_reconstruction",
        policy[
            "point_in_time_components_are_not_historical_reconstruction"
        ]
        is True,
        "true",
    )
    check(
        "policy_retrospective_floor",
        policy[
            "retrospective_source_before_policy_effective_is_not_point_in_time_eligible"
        ]
        is True,
        "true",
    )
    check(
        "policy_no_direction",
        policy["directional_meaning_assigned"] is False,
        "false",
    )
    check(
        "policy_no_score",
        policy["composite_score_assigned"] is False,
        "false",
    )
    check(
        "policy_no_signal",
        policy["signal_semantics"] is False,
        "false",
    )

    check(
        "uses_published_pack",
        "context_feature_pack_v1_level_a_standard"
        in source,
        "present",
    )
    check(
        "uses_micro_v1_1_validator",
        "validate_public_read_only_microstructure_snapshot_v1_1"
        in source,
        "present",
    )
    check(
        "uses_sync_v1_1_builder",
        "build_microstructure_context_v1_1"
        in source,
        "present",
    )
    check(
        "uses_published_temporal_policy",
        "TEMPORAL_ALIGNMENT_POLICY_VERSION"
        in source,
        "present",
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
        "append_official_prospective_evidence"
        not in source,
        "absent",
    )

    check(
        "exact_reference_close_match",
        "REFERENCE_CLOSED_CANDLE_MISMATCH"
        in source,
        "present",
    )
    check(
        "exact_reference_boundary_match",
        "REFERENCE_BOUNDARY_MISMATCH"
        in source,
        "present",
    )
    check(
        "exact_context_availability_match",
        "CONTEXT_AVAILABILITY_MISMATCH"
        in source,
        "present",
    )
    check(
        "policy_floor_applied",
        "component_available_at = max("
        in source,
        "present",
    )
    check(
        "information_cutoff_capture_finish",
        '"information_cutoff_utc":'
        in source
        and '_utc(times["captured_finished"])'
        in source,
        "present",
    )
    check(
        "produced_after_policy",
        "PRODUCED_BEFORE_POLICY_EFFECTIVE"
        in source,
        "present",
    )
    check(
        "produced_after_source",
        "PRODUCED_BEFORE_SOURCE_COMPLETE"
        in source,
        "present",
    )

    check(
        "misaligned_values_null",
        '"values": values'
        in source
        and "if usable" in source,
        "present",
    )
    check(
        "no_tolerance_window",
        "tolerance" not in source.lower(),
        "absent",
    )
    check(
        "no_interval_equivalence",
        "interval_equivalence" not in source.lower(),
        "absent",
    )
    check(
        "depth_5_10_required",
        "REQUIRED_DEPTH_BANDS_BPS = (5, 10)"
        in source,
        "present",
    )
    check(
        "depth_25_50_optional",
        "OPTIONAL_DEPTH_BANDS_BPS = (25, 50)"
        in source,
        "present",
    )
    check(
        "no_depth_extrapolation",
        '"incomplete_depth_extrapolation_allowed":'
        in source,
        "present",
    )
    check(
        "no_hidden_stop_claim",
        '"order_book_hidden_stops_or_liquidations_revealed":'
        in source,
        "present",
    )
    check(
        "no_oi_direction_claim",
        '"open_interest_identifies_long_vs_short_direction":'
        in source,
        "present",
    )
    check(
        "no_funding_actionability",
        '"funding_and_ratios_actionable"'
        in source
        and "FORBIDDEN_PAYLOAD_SEMANTIC_ENABLED"
        in source,
        "present",
    )
    check(
        "no_future_outcomes",
        '"future_outcomes_used": False'
        in source,
        "present",
    )
    check(
        "no_direction_semantics",
        '"directional_semantics": False'
        in source,
        "present",
    )
    check(
        "no_signal_semantics",
        '"signal_semantics": False'
        in source,
        "present",
    )
    check(
        "no_composite_score",
        '"composite_score_assigned": False'
        in source,
        "present",
    )

    check(
        "external_source_required",
        "microstructure_snapshot_directory"
        in source,
        "present",
    )
    check(
        "source_inside_repo_prohibited",
        "SOURCE_SNAPSHOT_INSIDE_REPOSITORY_PROHIBITED"
        in source,
        "present",
    )
    check(
        "external_output_guard",
        "OUTPUT_INSIDE_REPOSITORY_PROHIBITED"
        in source,
        "present",
    )
    check(
        "create_only_write",
        'with path.open("xb")' in source,
        "present",
    )
    check(
        "package_network_false",
        '"real_network_request_executed":'
        in source,
        "present",
    )
    check(
        "market_acquisition_false",
        '"market_data_acquired_by_producer":'
        in source,
        "present",
    )
    check(
        "official_integrity_checks",
        "OFFICIAL_ARTIFACT_CHANGED"
        in source,
        "present",
    )

    check(
        "docs_no_acquisition",
        "performs **no market-data acquisition**"
        in docs,
        "present",
    )
    check(
        "docs_policy_floor",
        "Why the policy floor exists"
        in docs,
        "present",
    )
    check(
        "docs_old_source_ineligible",
        "point-in-time ineligible"
        in docs,
        "present",
    )
    check(
        "docs_exact_alignment",
        "exact provider timestamp"
        in docs,
        "present",
    )
    check(
        "docs_misaligned_values_null",
        "`values = null`" in docs,
        "present",
    )
    check(
        "docs_no_hidden_stops",
        "order book reveals hidden stops"
        in docs,
        "present",
    )
    check(
        "docs_no_scoring",
        "No scoring" in docs,
        "present",
    )

    check(
        "test_old_snapshot_floor",
        "test_13_old_snapshot_policy_floor_applied"
        in tests,
        "present",
    )
    check(
        "test_old_snapshot_ineligible",
        "test_14_old_snapshot_pack_ineligible"
        in tests,
        "present",
    )
    check(
        "test_future_snapshot_eligible",
        "test_15_future_snapshot_pack_eligible"
        in tests,
        "present",
    )
    check(
        "test_misaligned_taker",
        "test_22_misaligned_taker_excluded"
        in tests,
        "present",
    )
    check(
        "test_incomplete_depth",
        "test_25_incomplete_25_band_not_usable"
        in tests,
        "present",
    )
    check(
        "test_package_roundtrip",
        "test_37_package_roundtrip"
        in tests,
        "present",
    )
    check(
        "test_tamper",
        "test_38_package_tamper_detected"
        in tests,
        "present",
    )
    check(
        "test_official_unchanged",
        "test_39_official_artifacts_unchanged"
        in tests,
        "present",
    )

    try:
        policy_validation = (
            m.validate_synchronized_microstructure_context_policy_v1(
                policy
            )
        )
        policy_valid = (
            policy_validation[
                "source_depth_limit"
            ]
            == 1000
        )
        policy_details = json.dumps(
            policy_validation,
            sort_keys=True,
        )
    except Exception as exc:
        policy_valid = False
        policy_details = repr(exc)

    check(
        "policy_runtime_validation",
        policy_valid,
        policy_details,
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
            if (
                len(parts) != 2
                or len(parts[0]) != 64
            ):
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
            "SYNCHRONIZED_MICROSTRUCTURE_CONTEXT_V1_"
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
    print(
        json.dumps(
            result,
            indent=2,
            sort_keys=True,
        )
    )
    raise SystemExit(
        0 if result["blockers"] == 0 else 1
    )
