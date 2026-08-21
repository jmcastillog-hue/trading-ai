from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path

from src.evaluation import context_evaluation_engine_v1 as m

POLICY = Path(
    "src/evaluation/resources/context_evaluation_engine_policy_v1.json"
)
SOURCE = Path("src/evaluation/context_evaluation_engine_v1.py")
DOCS = Path("docs/CONTEXT_EVALUATION_ENGINE_V1.md")
TESTS = Path("tests/test_context_evaluation_engine_v1.py")
MANIFEST = Path("CONTEXT_EVALUATION_ENGINE_V1_MANIFEST.sha256")


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

    check("capability", m.CAPABILITY == "CONTEXT_EVALUATION_ENGINE_V1", m.CAPABILITY)
    check("attempt_1", m.IMPLEMENTATION_OR_REPAIR_ATTEMPT == 1)
    check("max_attempts", m.MAX_IMPLEMENTATION_OR_REPAIR_ATTEMPTS == 10)
    check("authorization", m.PACKAGE_AUTHORIZATION == "PREPARE_CONTEXT_EVALUATION_ENGINE_V1")
    check("outcome_branch", m.OUTCOME_BRANCH == "synchronized_context_outcome")
    check("outcome_field", m.OUTCOME_FIELD == "forward_return")
    check("horizons", tuple(m.FORWARD_HORIZONS_BARS) == (1, 2, 4, 8, 16))
    check("predictor_types", m.SUPPORTED_PREDICTOR_TYPES == ("BINARY", "CATEGORICAL", "CONTINUOUS"))

    check("policy_schema", policy["schema_version"] == "CONTEXT_EVALUATION_ENGINE_POLICY_V1")
    check("policy_floor", policy["policy_effective_from_utc"] == "2026-08-21T00:45:00+00:00")
    check("policy_pack_schema", policy["expected_pack_schema_version"] == "CONTEXT_FEATURE_PACK_V1_LEVEL_A_STANDARD_SCHEMA_V1")
    check("policy_outcome_schema", policy["expected_outcome_schema_version"] == "FORWARD_OUTCOME_LABELS_V1")
    check("policy_horizons", policy["supported_horizons_bars"] == [1, 2, 4, 8, 16])
    check("policy_context_branch", policy["outcome_branch"] == "synchronized_context_outcome")
    check("policy_forward_return", policy["outcome_field"] == "forward_return")
    check("policy_identity_transform", policy["allowed_transform"] == "IDENTITY")
    check("policy_min_sample", policy["min_non_overlapping_observations"] == 10)
    check("policy_preferred_sample", policy["preferred_non_overlapping_observations"] == 30)
    check("policy_binary_group", policy["min_binary_group_observations"] == 5)
    check("policy_category_group", policy["min_categorical_group_observations"] == 5)
    check("policy_max_categories", policy["max_categorical_levels"] == 8)
    check("policy_freeze_guard", policy["hypothesis_freeze_not_before_policy_required"] is True)
    check("policy_post_freeze_guard", policy["observation_not_before_hypothesis_freeze_required"] is True)
    check("policy_pit_guard", policy["point_in_time_feature_required"] is True)
    check("policy_anchor_guard", policy["context_anchor_exact_match_required"] is True)
    check("policy_cutoff_guard", policy["context_cutoff_exact_match_required"] is True)
    check("policy_overlap_guard", policy["non_overlapping_outcome_windows_required"] is True)
    check("policy_no_imputation", policy["missing_feature_imputation_allowed"] is False)
    check("policy_no_late_zero", policy["late_feature_as_zero_allowed"] is False)
    check("policy_no_threshold_search", policy["threshold_search_allowed"] is False)
    check("policy_no_transform_search", policy["predictor_transform_search_allowed"] is False)
    check("policy_no_model_fit", policy["model_fit_allowed"] is False)
    check("policy_no_hyperparameter_search", policy["hyperparameter_search_allowed"] is False)
    check("policy_no_pvalues", policy["p_value_generation_allowed"] is False)
    check("policy_no_significance", policy["significance_claim_allowed"] is False)
    check("policy_no_winner", policy["multiple_testing_winner_selection_allowed"] is False)
    check("policy_no_ranking", policy["feature_ranking_allowed"] is False)
    check("policy_no_edge", policy["edge_claim_allowed"] is False)
    check("policy_no_promotion", policy["feature_promotion_allowed"] is False)
    check("policy_no_quality_gate", policy["quality_gate_evaluation_allowed"] is False)
    check("policy_no_direction", policy["directional_semantics"] is False)
    check("policy_no_signal", policy["signal_semantics"] is False)
    check("policy_no_paper", policy["paper_trade_execution_allowed"] is False)
    check("policy_no_real_capital", policy["real_capital_allowed"] is False)
    check("policy_no_alerts", policy["live_alerts_allowed"] is False)
    check("policy_no_exchange", policy["exchange_execution_allowed"] is False)
    check("policy_no_automation", policy["automation_allowed"] is False)
    check("policy_no_append", policy["official_append_allowed"] is False)

    check("imports_pack_validator", "validate_context_feature_pack_v1_package" in source)
    check("imports_outcome_validator", "validate_forward_outcome_label_package" in source)
    check("uses_feature_registry", "FEATURE_IDS" in source)
    check("uses_sync_branch", 'OUTCOME_BRANCH = "synchronized_context_outcome"' in source)
    check("no_primary_outcome_extract", '["primary_rule_outcome"]' not in source)
    check("freeze_guard_source", "OBSERVATION_PRE_HYPOTHESIS_FREEZE" in source)
    check("pit_guard_source", "FEATURE_NOT_POINT_IN_TIME_ELIGIBLE" in source)
    check("anchor_match_source", "CONTEXT_ANCHOR_MISMATCH" in source)
    check("cutoff_match_source", "CONTEXT_CUTOFF_MISMATCH" in source)
    check("pending_outcome_source", "OUTCOME_NOT_AVAILABLE" in source)
    check("overlap_purge_source", "OVERLAPPING_FORWARD_WINDOW" in source)
    check("spearman_source", "SPEARMAN_RHO" in source)
    check("binary_source", "MEAN_FORWARD_RETURN_DIFFERENCE_TRUE_MINUS_FALSE" in source)
    check("category_source", "CATEGORICAL_GROUP_SUMMARY_ONLY" in source)
    check("no_pvalue_result", '"p_value": None' in source)
    check("no_edge_result", '"edge_claim": False' in source)
    check("descriptive_decision", "DESCRIPTIVE_ONLY_NO_EDGE_CLAIM" in source)
    check("no_network_import", "requests" not in imports and "httpx" not in imports)
    check("no_websocket_import", "websocket" not in imports and "websockets" not in imports)
    check("no_subprocess_import", "subprocess" not in imports)
    check("no_threads_import", not any(x in imports for x in ("threading", "multiprocessing", "asyncio", "schedule", "apscheduler")))
    check("no_sklearn_import", "sklearn" not in imports)
    check("no_scipy_import", "scipy" not in imports)
    check("official_integrity_source", "OFFICIAL_ARTIFACT_CHANGED" in source)
    check("output_external_guard", "OUTPUT_INSIDE_REPOSITORY_PROHIBITED" in source)
    check("hypothesis_external_guard", "HYPOTHESIS_MANIFEST_INSIDE_REPOSITORY_PROHIBITED" in source)
    check("cohort_external_guard", "COHORT_MANIFEST_INSIDE_REPOSITORY_PROHIBITED" in source)
    check("create_only", 'with path.open("xb")' in source)

    check("docs_additive", "Why this is additive" in docs)
    check("docs_sync_outcome", "synchronized_context_outcome" in docs)
    check("docs_preregistered", "Preregistered hypothesis manifest" in docs)
    check("docs_overlap", "Outcome-window overlap" in docs)
    check("docs_no_pvalues", "p-values" in docs)
    check("docs_no_edge", "DESCRIPTIVE_ONLY_NO_EDGE_CLAIM" in docs)

    check("test_pre_freeze", "test_12_pre_freeze_observation_excluded" in tests)
    check("test_late_feature", "test_13_late_feature_excluded_not_zero" in tests)
    check("test_primary_ignored", "test_16_primary_rule_outcome_is_ignored" in tests)
    check("test_spearman", "test_17_continuous_spearman_positive_one" in tests)
    check("test_overlap", "test_18_overlap_purge_is_horizon_aware" in tests)
    check("test_binary", "test_19_binary_difference" in tests)
    check("test_category", "test_21_categorical_summary_no_winner" in tests)
    check("test_no_pvalue", "test_22_results_have_no_pvalue_significance_or_edge" in tests)
    check("test_package", "test_27_package_roundtrip_and_tamper" in tests)
    check("test_immutability", "test_28_source_inputs_not_modified_by_package" in tests)

    try:
        runtime = m.validate_context_evaluation_engine_policy_v1(policy)
        runtime_ok = (
            runtime["min_non_overlapping_observations"] == 10
            and runtime["preferred_non_overlapping_observations"] == 30
        )
    except Exception:
        runtime_ok = False
    check("policy_runtime", runtime_ok)

    lines = [
        line
        for line in MANIFEST.read_text(encoding="utf-8").splitlines()
        if line.strip()
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

    failed = [item for item in checks if not item["passed"]]
    blockers = [item for item in failed if item["blocker"]]

    return {
        "checks": len(checks),
        "failed_checks": len(failed),
        "blockers": len(blockers),
        "check_results": checks,
        "real_network_request_executed": False,
        "market_data_fetched": False,
        "model_fit_performed": False,
        "p_values_generated": False,
        "significance_assigned": False,
        "quality_gate_evaluated": False,
        "edge_established": False,
        "real_evaluation_package_prepared": False,
        "official_append_executed": False,
    }


if __name__ == "__main__":
    result = run()
    print(json.dumps(result, indent=2, sort_keys=True))
    raise SystemExit(0 if result["blockers"] == 0 else 1)
