from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path

from src.context import external_cycle_regression_baseline_v1 as m

POLICY = Path("src/context/resources/external_cycle_regression_baseline_policy_v1.json")
SOURCE = Path("src/context/external_cycle_regression_baseline_v1.py")
DOCS = Path("docs/EXTERNAL_CYCLE_REGRESSION_BASELINE_V1.md")
TESTS = Path("tests/test_external_cycle_regression_baseline_v1.py")
MANIFEST = Path("EXTERNAL_CYCLE_REGRESSION_BASELINE_V1_MANIFEST.sha256")

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

    check("capability", m.CAPABILITY == "EXTERNAL_CYCLE_REGRESSION_BASELINE_V1", m.CAPABILITY)
    check("source_kind", m.SOURCE_KIND == "EXTERNAL_MODEL", m.SOURCE_KIND)
    check("snapshot_schema", m.SNAPSHOT_SCHEMA_VERSION == "EXTERNAL_CYCLE_REGRESSION_BASELINE_SNAPSHOT_V1", m.SNAPSHOT_SCHEMA_VERSION)
    check("value_unit", m.VALUE_UNIT == "USD_PER_BTC", m.VALUE_UNIT)
    check("attempt_1", m.IMPLEMENTATION_OR_REPAIR_ATTEMPT == 1, str(m.IMPLEMENTATION_OR_REPAIR_ATTEMPT))
    check("max_attempts", m.MAX_IMPLEMENTATION_OR_REPAIR_ATTEMPTS == 10, str(m.MAX_IMPLEMENTATION_OR_REPAIR_ATTEMPTS))
    check("authorization", m.PACKAGE_AUTHORIZATION == "PREPARE_EXTERNAL_CYCLE_REGRESSION_BASELINE_V1", m.PACKAGE_AUTHORIZATION)

    check("policy_schema", policy["schema_version"] == "EXTERNAL_CYCLE_REGRESSION_BASELINE_POLICY_V1")
    check("policy_floor", policy["policy_effective_from_utc"] == "2026-08-19T00:40:00+00:00")
    check("policy_external_snapshot", policy["external_frozen_snapshot_required"] is True)
    check("policy_exact_reference", policy["reference_time_exact_observation_boundary_required"] is True)
    check("policy_no_fit", policy["producer_model_fit_allowed"] is False)
    check("policy_no_network", policy["producer_network_fetch_allowed"] is False)
    check("policy_no_market_price", policy["producer_market_price_input_allowed"] is False)
    check("policy_no_residual", policy["producer_residual_calculation_allowed"] is False)
    check("policy_no_outcomes", policy["future_outcomes_used"] is False)
    check("policy_no_direction", policy["directional_meaning_assigned"] is False)
    check("policy_no_score", policy["composite_score_assigned"] is False)
    check("policy_no_signal", policy["signal_semantics"] is False)

    check("uses_pack", "context_feature_pack_v1_level_a_standard" in source)
    check("no_requests", "requests" not in imports, str(sorted(imports)))
    check("no_httpx", "httpx" not in imports, str(sorted(imports)))
    check("no_websocket", "websocket" not in imports and "websockets" not in imports)
    check("no_subprocess", "subprocess" not in imports)
    check("no_threads", not any(x in imports for x in ("threading", "multiprocessing", "asyncio", "schedule", "apscheduler")))
    check("no_official_writer", "append_official_prospective_evidence" not in source)

    check("fit_before_info", "SNAPSHOT_FIT_AFTER_INFORMATION_CUTOFF" in source)
    check("info_before_generated", "SNAPSHOT_INFORMATION_AFTER_MODEL_GENERATED" in source)
    check("generated_before_created", "SNAPSHOT_MODEL_AFTER_SNAPSHOT_CREATED" in source)
    check("exact_reference", "SNAPSHOT_REFERENCE_TIME_MISMATCH" in source)
    check("policy_floor_available", "available = max(" in source)
    check("no_interpolation", '"interpolation_or_extrapolation_performed": False' in source)
    check("no_market_price", '"producer_market_price_input_used": False' in source)
    check("no_residual", '"producer_residual_calculation_performed": False' in source)
    check("no_model_fit", '"producer_model_fit_executed": False' in source)
    check("no_network_fetch", '"producer_network_fetch_executed": False' in source)
    check("no_direction", '"directional_semantics": False' in source)
    check("no_signal", '"signal_semantics": False' in source)
    check("no_score", '"composite_score_assigned": False' in source)
    check("no_outcomes", '"future_outcomes_used": False' in source)
    check("external_source_guard", "EXTERNAL_SNAPSHOT_INSIDE_REPOSITORY_PROHIBITED" in source)
    check("external_output_guard", "OUTPUT_INSIDE_REPOSITORY_PROHIBITED" in source)
    check("create_only", 'with path.open("xb")' in source)
    check("official_integrity", "OFFICIAL_ARTIFACT_CHANGED" in source)

    check("docs_no_fit", "does not fit a regression" in docs)
    check("docs_no_comparison", "Deliberately absent comparison" in docs)
    check("docs_point_in_time", "Point-in-time rules" in docs)
    check("docs_eval_boundary", "Evaluation boundary" in docs)

    check("test_exact_reference", "test_11_exact_reference_required" in tests)
    check("test_floor", "test_12_policy_floor_applied" in tests)
    check("test_old_ineligible", "test_14_old_snapshot_pack_ineligible" in tests)
    check("test_future_eligible", "test_15_post_policy_pack_eligible" in tests)
    check("test_package", "test_22_package_roundtrip" in tests)
    check("test_tamper", "test_23_tamper_detected" in tests)
    check("test_unchanged", "test_24_official_and_source_unchanged" in tests)

    try:
        runtime = m.validate_external_cycle_regression_baseline_policy_v1(policy)
        runtime_ok = runtime["value_unit"] == "USD_PER_BTC"
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
        "real_component_package_prepared": False,
        "official_append_executed": False,
    }

if __name__ == "__main__":
    result = run()
    print(json.dumps(result, indent=2, sort_keys=True))
    raise SystemExit(0 if result["blockers"] == 0 else 1)
