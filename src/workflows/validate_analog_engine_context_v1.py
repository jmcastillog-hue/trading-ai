from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path

from src.context import analog_engine_context_v1 as m

POLICY = Path("src/context/resources/analog_engine_context_policy_v1.json")
SOURCE = Path("src/context/analog_engine_context_v1.py")
DOCS = Path("docs/ANALOG_ENGINE_CONTEXT_V1.md")
TESTS = Path("tests/test_analog_engine_context_v1.py")
MANIFEST = Path("ANALOG_ENGINE_CONTEXT_V1_MANIFEST.sha256")

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
            {"check": name, "passed": bool(ok), "blocker": not bool(ok), "details": details}
        )

    check("capability", m.CAPABILITY == "ANALOG_ENGINE_CONTEXT_V1", m.CAPABILITY)
    check("source_kind", m.SOURCE_KIND == "MODEL_DERIVED", m.SOURCE_KIND)
    check("query_schema", m.QUERY_SCHEMA_VERSION == "ANALOG_QUERY_VECTOR_SNAPSHOT_V1")
    check("library_schema", m.LIBRARY_SCHEMA_VERSION == "ANALOG_REFERENCE_LIBRARY_SNAPSHOT_V1")
    check("attempt_1", m.IMPLEMENTATION_OR_REPAIR_ATTEMPT == 1)
    check("max_attempts", m.MAX_IMPLEMENTATION_OR_REPAIR_ATTEMPTS == 10)
    check("authorization", m.PACKAGE_AUTHORIZATION == "PREPARE_ANALOG_ENGINE_CONTEXT_V1")

    check("policy_schema", policy["schema_version"] == "ANALOG_ENGINE_CONTEXT_POLICY_V1")
    check("policy_floor", policy["policy_effective_from_utc"] == "2026-08-19T01:30:00+00:00")
    check("policy_metric", policy["distance_metric"] == "EUCLIDEAN_PRESTANDARDIZED_VECTOR")
    check("policy_top_k", policy["top_k"] == 5)
    check("policy_feature_bounds", policy["min_feature_count"] == 2 and policy["max_feature_count"] == 32)
    check("policy_library_bounds", policy["min_library_rows"] == 5 and policy["max_library_rows"] == 10000)
    check("policy_exact_feature_space", policy["exact_feature_space_match_required"] is True)
    check("policy_exact_query", policy["exact_query_observation_match_required"] is True)
    check("policy_past_only", policy["historical_reference_strictly_before_query_required"] is True)
    check("policy_info_cutoff", policy["feature_information_cutoff_not_after_reference_required"] is True)
    check("policy_normalization_cutoff", policy["normalization_fit_cutoff_not_after_query_reference_required"] is True)
    check("policy_no_outcomes", policy["outcome_fields_allowed"] is False and policy["future_outcomes_used"] is False)
    check("policy_no_future_rows", policy["future_rows_allowed"] is False)
    check("policy_no_network", policy["producer_network_fetch_allowed"] is False)
    check("policy_no_training", policy["producer_model_training_allowed"] is False)
    check("policy_no_market_fetch", policy["producer_market_data_fetch_allowed"] is False)
    check("policy_no_direction", policy["directional_meaning_assigned"] is False)
    check("policy_no_vote", policy["analog_vote_allowed"] is False)
    check("policy_no_score", policy["composite_score_assigned"] is False)
    check("policy_no_signal", policy["signal_semantics"] is False)

    check("uses_pack", "context_feature_pack_v1_level_a_standard" in source)
    check("no_requests", "requests" not in imports, str(sorted(imports)))
    check("no_httpx", "httpx" not in imports)
    check("no_websocket", "websocket" not in imports and "websockets" not in imports)
    check("no_subprocess", "subprocess" not in imports)
    check("no_threads", not any(x in imports for x in ("threading", "multiprocessing", "asyncio", "schedule", "apscheduler")))
    check("no_official_writer", "append_official_prospective_evidence" not in source)

    check("outcome_key_guard", "PROHIBITED_OUTCOME_KEYS" in source and "PROHIBITED_OUTCOME_FIELD" in source)
    check("query_info_guard", "QUERY_INFORMATION_AFTER_REFERENCE" in source)
    check("query_creation_guard", "QUERY_INFORMATION_AFTER_SNAPSHOT_CREATED" in source)
    check("library_info_guard", "LIBRARY_INFORMATION_AFTER_REFERENCE" in source)
    check("library_creation_guard", "LIBRARY_INFORMATION_AFTER_SNAPSHOT_CREATED" in source)
    check("normalization_creation_guard", "NORMALIZATION_FIT_AFTER_LIBRARY_SNAPSHOT_CREATED" in source)
    check("future_row_guard", "FUTURE_OR_CURRENT_ANALOG_ROW" in source)
    check("normalization_guard", "NORMALIZATION_FIT_AFTER_QUERY_REFERENCE" in source)
    check("feature_space_guard", "FEATURE_SPACE_SHA_MISMATCH" in source)
    check("feature_names_guard", "FEATURE_NAMES_MISMATCH" in source)
    check("query_identity_guard", "QUERY_OBSERVATION_ID_MISMATCH" in source)
    check("availability_includes_info", "available = max(query_created, library_created, policy_effective, information_cutoff)" in source)
    check("deterministic_metric", "EUCLIDEAN_PRESTANDARDIZED_VECTOR" in source)
    check("no_vote_payload", '"analog_vote_performed": False' in source)
    check("no_direction_payload", '"directional_semantics": False' in source)
    check("no_signal_payload", '"signal_semantics": False' in source)
    check("no_score_payload", '"composite_score_assigned": False' in source)
    check("no_outcomes_payload", '"future_outcomes_used": False' in source)
    check("no_training_payload", '"producer_model_training_executed": False' in source)
    check("no_network_payload", '"producer_network_fetch_executed": False' in source)
    check("no_market_fetch_payload", '"producer_market_data_fetch_executed": False' in source)
    check("external_query_guard", "QUERY_INSIDE_REPOSITORY_PROHIBITED" in source)
    check("external_library_guard", "LIBRARY_INSIDE_REPOSITORY_PROHIBITED" in source)
    check("external_output_guard", "OUTPUT_INSIDE_REPOSITORY_PROHIBITED" in source)
    check("create_only", 'with path.open("xb")' in source)
    check("official_integrity", "OFFICIAL_ARTIFACT_CHANGED" in source)

    check("docs_past_only", "strictly older than the query" in docs)
    check("docs_no_outcomes", "No historical returns" in docs)
    check("docs_no_vote", "majority voting" in docs)
    check("docs_eval_boundary", "Evaluation boundary" in docs)

    check("test_outcome_guard", "test_08_library_outcome_field_fails" in tests)
    check("test_query_creation", "test_10_query_snapshot_creation_must_cover_information" in tests)
    check("test_library_creation", "test_11_library_snapshot_creation_must_cover_rows" in tests)
    check("test_normalization_creation", "test_12_normalization_fit_must_not_postdate_library_snapshot" in tests)
    check("test_future_guard", "test_16_future_library_row_fails" in tests)
    check("test_normalization_guard", "test_17_normalization_future_fit_fails" in tests)
    check("test_nearest_five", "test_18_deterministic_nearest_five" in tests)
    check("test_availability_info", "test_19_available_not_before_information" in tests)
    check("test_old_ineligible", "test_22_old_snapshots_pack_ineligible_due_policy_floor" in tests)
    check("test_post_policy", "test_23_post_policy_pack_eligible" in tests)
    check("test_package", "test_27_roundtrip_tamper_and_immutability" in tests)

    try:
        runtime = m.validate_analog_engine_context_policy_v1(policy)
        runtime_ok = (
            runtime["top_k"] == 5
            and runtime["distance_metric"] == "EUCLIDEAN_PRESTANDARDIZED_VECTOR"
        )
    except Exception:
        runtime_ok = False
    check("policy_runtime", runtime_ok)

    lines = [x for x in MANIFEST.read_text(encoding="utf-8").splitlines() if x.strip()]
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
        "market_data_fetched": False,
        "model_training_executed": False,
        "real_component_package_prepared": False,
        "official_append_executed": False,
    }

if __name__ == "__main__":
    result = run()
    print(json.dumps(result, indent=2, sort_keys=True))
    raise SystemExit(0 if result["blockers"] == 0 else 1)
