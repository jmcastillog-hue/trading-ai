from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path

from src.context import external_thesis_model_card_v1 as m

POLICY = Path("src/context/resources/external_thesis_model_card_policy_v1.json")
SOURCE = Path("src/context/external_thesis_model_card_v1.py")
DOCS = Path("docs/EXTERNAL_THESIS_MODEL_CARD_V1.md")
TESTS = Path("tests/test_external_thesis_model_card_v1.py")
MANIFEST = Path("EXTERNAL_THESIS_MODEL_CARD_V1_MANIFEST.sha256")

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
        checks.append({"check": name, "passed": bool(ok), "blocker": not bool(ok), "details": details})

    check("capability", m.CAPABILITY == "EXTERNAL_THESIS_MODEL_CARD_V1", m.CAPABILITY)
    check("source_kind", m.SOURCE_KIND == "EXTERNAL_MODEL", m.SOURCE_KIND)
    check("snapshot_schema", m.SNAPSHOT_SCHEMA_VERSION == "EXTERNAL_THESIS_MODEL_CARD_SNAPSHOT_V1", m.SNAPSHOT_SCHEMA_VERSION)
    check("attempt_1", m.IMPLEMENTATION_OR_REPAIR_ATTEMPT == 1)
    check("max_attempts", m.MAX_IMPLEMENTATION_OR_REPAIR_ATTEMPTS == 10)
    check("authorization", m.PACKAGE_AUTHORIZATION == "PREPARE_EXTERNAL_THESIS_MODEL_CARD_V1")

    check("policy_schema", policy["schema_version"] == "EXTERNAL_THESIS_MODEL_CARD_POLICY_V1")
    check("policy_floor", policy["policy_effective_from_utc"] == "2026-08-19T01:02:00+00:00")
    check("policy_external_snapshot", policy["external_frozen_snapshot_required"] is True)
    check("policy_applicability", policy["reference_inside_declared_applicability_required"] is True)
    check("policy_opaque_state", policy["opaque_state_code_required"] is True)
    check("policy_no_text", policy["text_claims_ingested"] is False)
    check("policy_no_targets", policy["target_prices_ingested"] is False)
    check("policy_no_confidence", policy["confidence_scores_ingested"] is False)
    check("policy_no_network", policy["producer_network_fetch_allowed"] is False)
    check("policy_no_execution", policy["producer_model_execution_allowed"] is False)
    check("policy_no_outcomes", policy["future_outcomes_used"] is False)
    check("policy_no_direction", policy["directional_meaning_assigned"] is False)
    check("policy_no_score", policy["composite_score_assigned"] is False)
    check("policy_no_signal", policy["signal_semantics"] is False)

    check("uses_pack", "context_feature_pack_v1_level_a_standard" in source)
    check("no_requests", "requests" not in imports, str(sorted(imports)))
    check("no_httpx", "httpx" not in imports)
    check("no_websocket", "websocket" not in imports and "websockets" not in imports)
    check("no_subprocess", "subprocess" not in imports)
    check("no_threads", not any(x in imports for x in ("threading", "multiprocessing", "asyncio", "schedule", "apscheduler")))
    check("no_official_writer", "append_official_prospective_evidence" not in source)

    check("published_before_info", "SNAPSHOT_PUBLISHED_AFTER_INFORMATION_CUTOFF" in source)
    check("info_before_generated", "SNAPSHOT_INFORMATION_AFTER_THESIS_GENERATED" in source)
    check("generated_before_created", "SNAPSHOT_THESIS_AFTER_SNAPSHOT_CREATED" in source)
    check("reference_after_start", "REFERENCE_BEFORE_THESIS_APPLICABILITY" in source)
    check("reference_before_end", "REFERENCE_AFTER_THESIS_APPLICABILITY" in source)
    check("policy_floor_available", "available = max(" in source)
    check("opaque_state_regex", "STATE_CODE_RE" in source)
    check("no_text_ingest", '"text_claims_ingested": False' in source)
    check("no_target_ingest", '"target_prices_ingested": False' in source)
    check("no_confidence_ingest", '"confidence_scores_ingested": False' in source)
    check("no_model_execution", '"producer_model_execution_executed": False' in source)
    check("no_network_fetch", '"producer_network_fetch_executed": False' in source)
    check("no_market_data", '"market_data_input_used": False' in source)
    check("no_direction", '"directional_semantics": False' in source)
    check("no_signal", '"signal_semantics": False' in source)
    check("no_score", '"composite_score_assigned": False' in source)
    check("no_outcomes", '"future_outcomes_used": False' in source)
    check("external_source_guard", "EXTERNAL_SNAPSHOT_INSIDE_REPOSITORY_PROHIBITED" in source)
    check("external_output_guard", "OUTPUT_INSIDE_REPOSITORY_PROHIBITED" in source)
    check("create_only", 'with path.open("xb")' in source)
    check("official_integrity", "OFFICIAL_ARTIFACT_CHANGED" in source)

    check("docs_opaque", "Opaque state code" in docs)
    check("docs_point_in_time", "Point-in-time order" in docs)
    check("docs_excluded", "Deliberately excluded fields" in docs)
    check("docs_eval_boundary", "Evaluation boundary" in docs)

    check("test_state_code", "test_07_bad_state_code_fails" in tests)
    check("test_applicability_start", "test_10_reference_before_start_fails" in tests)
    check("test_applicability_end", "test_11_reference_after_end_fails" in tests)
    check("test_old_ineligible", "test_15_old_snapshot_pack_ineligible" in tests)
    check("test_future_eligible", "test_16_post_policy_pack_eligible" in tests)
    check("test_no_text", "test_18_no_text_targets_confidence" in tests)
    check("test_package", "test_24_roundtrip_tamper_and_immutability" in tests)

    try:
        runtime = m.validate_external_thesis_model_card_policy_v1(policy)
        runtime_ok = runtime["snapshot_schema_version"] == "EXTERNAL_THESIS_MODEL_CARD_SNAPSHOT_V1"
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
        "external_model_fetched": False,
        "external_model_executed": False,
        "real_component_package_prepared": False,
        "official_append_executed": False,
    }

if __name__ == "__main__":
    result = run()
    print(json.dumps(result, indent=2, sort_keys=True))
    raise SystemExit(0 if result["blockers"] == 0 else 1)
