from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path

from src.context import onchain_context_interface_v1 as m

POLICY = Path(
    "src/context/resources/onchain_context_interface_policy_v1.json"
)
SOURCE = Path("src/context/onchain_context_interface_v1.py")
DOCS = Path("docs/ONCHAIN_CONTEXT_INTERFACE_V1.md")
TESTS = Path("tests/test_onchain_context_interface_v1.py")
MANIFEST = Path("ONCHAIN_CONTEXT_INTERFACE_V1_MANIFEST.sha256")


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
    policy = json.loads(POLICY.read_text(encoding="utf-8"))
    tree = ast.parse(source)

    imports = {
        node.names[0].name.split(".")[0]
        for node in ast.walk(tree)
        if isinstance(node, ast.Import)
    }
    imports |= {
        (node.module or "").split(".")[0]
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module
    }

    checks = []

    def check(name, ok, details=""):
        checks.append(
            {
                "check": name,
                "passed": bool(ok),
                "blocker": not bool(ok),
                "details": details,
            }
        )

    check("capability", m.CAPABILITY == "ONCHAIN_CONTEXT_INTERFACE_V1", m.CAPABILITY)
    check("source_kind", m.SOURCE_KIND == "FUTURE_INTERFACE", m.SOURCE_KIND)
    check("snapshot_schema", m.SNAPSHOT_SCHEMA_VERSION == "ONCHAIN_CONTEXT_SNAPSHOT_V1")
    check("attempt_1", m.IMPLEMENTATION_OR_REPAIR_ATTEMPT == 1)
    check("max_attempts", m.MAX_IMPLEMENTATION_OR_REPAIR_ATTEMPTS == 10)
    check("authorization", m.PACKAGE_AUTHORIZATION == "PREPARE_ONCHAIN_CONTEXT_INTERFACE_V1")

    check("policy_schema", policy["schema_version"] == "ONCHAIN_CONTEXT_INTERFACE_POLICY_V1")
    check("policy_floor", policy["policy_effective_from_utc"] == "2026-08-19T02:27:00+00:00")
    check("policy_asset", policy["asset"] == "BTC")
    check("policy_network", policy["network"] == "BITCOIN")
    check("policy_metric_bounds", policy["min_metric_count"] == 1 and policy["max_metric_count"] == 64)
    check("policy_exact_identity", policy["exact_observation_identity_required"] is True)
    check("policy_observation_time", policy["metric_observation_not_after_reference_required"] is True)
    check("policy_info_order", policy["metric_information_cutoff_not_before_observation_end_required"] is True)
    check("policy_provider_order", policy["metric_provider_availability_not_before_information_cutoff_required"] is True)
    check("policy_snapshot_order", policy["snapshot_creation_not_before_metric_availability_required"] is True)
    check("policy_sorted_ids", policy["metric_ids_unique_and_sorted_required"] is True)
    check("policy_no_network", policy["producer_network_fetch_allowed"] is False)
    check("policy_no_market", policy["producer_market_data_fetch_allowed"] is False)
    check("policy_no_rpc", policy["producer_chain_rpc_allowed"] is False)
    check("policy_no_api", policy["producer_provider_api_allowed"] is False)
    check("policy_no_interpretation", policy["metric_interpretation_allowed"] is False)
    check("policy_no_direction", policy["directional_meaning_assigned"] is False)
    check("policy_no_threshold", policy["threshold_signal_allowed"] is False)
    check("policy_no_score", policy["composite_score_assigned"] is False)
    check("policy_no_signal", policy["signal_semantics"] is False)
    check("policy_no_outcomes", policy["future_outcomes_used"] is False)

    check("uses_pack", "context_feature_pack_v1_level_a_standard" in source)
    check("no_requests", "requests" not in imports, str(sorted(imports)))
    check("no_httpx", "httpx" not in imports)
    check("no_websocket", "websocket" not in imports and "websockets" not in imports)
    check("no_subprocess", "subprocess" not in imports)
    check("no_threads", not any(x in imports for x in ("threading", "multiprocessing", "asyncio", "schedule", "apscheduler")))
    check("no_official_writer", "append_official_prospective_evidence" not in source)

    check("outcome_key_guard", "PROHIBITED_OUTCOME_KEYS" in source and "PROHIBITED_OUTCOME_FIELD" in source)
    check("metric_id_guard", "METRIC_ID_RE" in source)
    check("duplicate_guard", "METRIC_IDS_DUPLICATE" in source)
    check("sorted_guard", "METRIC_IDS_NOT_SORTED" in source)
    check("info_order_guard", "METRIC_INFORMATION_BEFORE_OBSERVATION_END" in source)
    check("provider_order_guard", "METRIC_PROVIDER_AVAILABLE_BEFORE_INFORMATION" in source)
    check("snapshot_order_guard", "SNAPSHOT_CREATED_BEFORE_METRIC_AVAILABLE" in source)
    check("reference_guard", "METRIC_OBSERVATION_AFTER_REFERENCE" in source)
    check("reference_identity_guard", "SNAPSHOT_REFERENCE_MISMATCH" in source)
    check("observation_identity_guard", "SNAPSHOT_OBSERVATION_ID_MISMATCH" in source)
    check("availability_includes_info", "available = max(" in source and "information_cutoff" in source)
    check("metric_age", "age_seconds_at_reference" in source)
    check("no_network_payload", '"producer_network_fetch_executed": False' in source)
    check("no_market_payload", '"producer_market_data_fetch_executed": False' in source)
    check("no_rpc_payload", '"producer_chain_rpc_executed": False' in source)
    check("no_api_payload", '"producer_provider_api_executed": False' in source)
    check("no_interpret_payload", '"metric_interpretation_performed": False' in source)
    check("no_threshold_payload", '"threshold_signal_evaluated": False' in source)
    check("no_direction_payload", '"directional_semantics": False' in source)
    check("no_signal_payload", '"signal_semantics": False' in source)
    check("no_score_payload", '"composite_score_assigned": False' in source)
    check("no_outcomes_payload", '"future_outcomes_used": False' in source)
    check("external_snapshot_guard", "ONCHAIN_SNAPSHOT_INSIDE_REPOSITORY_PROHIBITED" in source)
    check("external_output_guard", "OUTPUT_INSIDE_REPOSITORY_PROHIBITED" in source)
    check("create_only", 'with path.open("xb")' in source)
    check("official_integrity", "OFFICIAL_ARTIFACT_CHANGED" in source)

    check("docs_provider_agnostic", "provider-agnostic" in docs)
    check("docs_point_in_time", "Point-in-time contract" in docs)
    check("docs_no_interpretation", "bullish/bearish meaning" in docs)
    check("docs_future_adapter", "future provider adapter" in docs)
    check("docs_eval_boundary", "Evaluation boundary" in docs)

    check("test_outcome_guard", "test_06_outcome_field_fails" in tests)
    check("test_duplicate_guard", "test_07_duplicate_metric_id_fails" in tests)
    check("test_sorted_guard", "test_08_unsorted_metric_ids_fail" in tests)
    check("test_reference_guard", "test_09_observation_after_reference_fails" in tests)
    check("test_info_guard", "test_10_information_before_observation_fails" in tests)
    check("test_provider_guard", "test_11_provider_available_before_information_fails" in tests)
    check("test_snapshot_order", "test_12_snapshot_created_before_metric_available_fails" in tests)
    check("test_old_ineligible", "test_15_old_snapshot_pack_ineligible_due_policy_floor" in tests)
    check("test_post_policy", "test_16_post_policy_pack_eligible" in tests)
    check("test_no_semantics", "test_18_no_network_rpc_interpretation_or_signal" in tests)
    check("test_late_snapshot", "test_23_snapshot_after_context_cutoff_pack_ineligible" in tests)
    check("test_package", "test_28_roundtrip_tamper_and_immutability" in tests)

    try:
        runtime = m.validate_onchain_context_interface_policy_v1(policy)
        runtime_ok = (
            runtime["asset"] == "BTC"
            and runtime["network"] == "BITCOIN"
            and runtime["max_metric_count"] == 64
        )
    except Exception:
        runtime_ok = False
    check("policy_runtime", runtime_ok)

    lines = [
        x for x in MANIFEST.read_text(encoding="utf-8").splitlines()
        if x.strip()
    ]
    manifest_ok = len(lines) == 5

    if manifest_ok:
        for line in lines:
            parts = line.split("  ", 1)
            if len(parts) != 2 or len(parts[0]) != 64:
                manifest_ok = False
                break
            target = Path(parts[1])
            if not target.is_file() or sha(target) != parts[0]:
                manifest_ok = False
                break

    check("manifest_entries_5", len(lines) == 5, str(len(lines)))
    check("manifest_valid", manifest_ok)

    failed = [x for x in checks if not x["passed"]]
    blockers = [x for x in failed if x["blocker"]]

    return {
        "checks": len(checks),
        "failed_checks": len(failed),
        "blockers": len(blockers),
        "check_results": checks,
        "real_network_request_executed": False,
        "provider_api_request_executed": False,
        "chain_rpc_request_executed": False,
        "market_data_fetched": False,
        "real_component_package_prepared": False,
        "official_append_executed": False,
    }


if __name__ == "__main__":
    result = run()
    print(json.dumps(result, indent=2, sort_keys=True))
    raise SystemExit(0 if result["blockers"] == 0 else 1)
