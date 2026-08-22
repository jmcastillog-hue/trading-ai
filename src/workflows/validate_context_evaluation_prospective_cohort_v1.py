from __future__ import annotations
import ast, hashlib, json
from pathlib import Path
from src.evaluation import context_evaluation_prospective_cohort_v1 as m
POLICY=Path("src/evaluation/resources/context_evaluation_prospective_cohort_policy_v1.json")
SOURCE=Path("src/evaluation/context_evaluation_prospective_cohort_v1.py")
DOCS=Path("docs/CONTEXT_EVALUATION_PROSPECTIVE_COHORT_V1.md")
TESTS=Path("tests/test_context_evaluation_prospective_cohort_v1.py")
MANIFEST=Path("CONTEXT_EVALUATION_PROSPECTIVE_COHORT_V1_MANIFEST.sha256")
def sha(path):
    h=hashlib.sha256(); h.update(path.read_bytes()); return h.hexdigest()
def run():
    source=SOURCE.read_text(encoding="utf-8"); docs=DOCS.read_text(encoding="utf-8"); tests=TESTS.read_text(encoding="utf-8"); policy=json.loads(POLICY.read_text(encoding="utf-8")); tree=ast.parse(source)
    imports={node.names[0].name.split(".")[0] for node in ast.walk(tree) if isinstance(node,ast.Import)} | {(node.module or "").split(".")[0] for node in ast.walk(tree) if isinstance(node,ast.ImportFrom) and node.module}
    checks=[]
    def check(name,ok,details=""): checks.append({"check":name,"passed":bool(ok),"blocker":not bool(ok),"details":str(details)})
    check("capability",m.CAPABILITY=="CONTEXT_EVALUATION_PROSPECTIVE_COHORT_V1")
    check("attempt_1",m.IMPLEMENTATION_OR_REPAIR_ATTEMPT==1); check("max_attempts",m.MAX_IMPLEMENTATION_OR_REPAIR_ATTEMPTS==10)
    check("plan_schema",m.PLAN_SCHEMA_VERSION=="CONTEXT_EVALUATION_PROSPECTIVE_COHORT_PLAN_V1")
    check("init_auth",m.INITIALIZE_AUTHORIZATION=="INITIALIZE_CONTEXT_EVALUATION_PROSPECTIVE_COHORT_V1")
    check("admission_auth",m.ADMISSION_AUTHORIZATION=="PREPARE_CONTEXT_EVALUATION_PROSPECTIVE_ADMISSION_V1")
    check("binding_auth",m.BINDING_AUTHORIZATION=="PREPARE_CONTEXT_EVALUATION_PROSPECTIVE_OUTCOME_BINDING_V1")
    check("materialize_auth",m.MATERIALIZE_AUTHORIZATION=="MATERIALIZE_CONTEXT_EVALUATION_ENGINE_COHORT_V1")
    check("policy_schema",policy["schema_version"]=="CONTEXT_EVALUATION_PROSPECTIVE_COHORT_POLICY_V1")
    check("policy_freeze",policy["policy_effective_from_utc"]=="2026-08-22T16:15:00+00:00")
    check("policy_hyp_sha",policy["preregistered_hypothesis_manifest_sha256"]=="4de33a61d2a1456e6bd673ddd044cd0c01bb3369d30595ec57773df1d922442b")
    check("canonical_hypothesis_hash","_canonical_json_sha256(raw)" in source)
    check("policy_sampling",policy["sampling_mode"]=="PREDECLARED_UTC_CONTEXT_ANCHORS")
    check("policy_alignment",policy["slot_alignment_minutes"]==15); check("policy_spacing",policy["minimum_slot_spacing_bars"]==16)
    check("policy_min_slots",policy["minimum_plan_slots"]==10); check("policy_preferred_slots",policy["preferred_plan_slots"]==30); check("policy_max_slots",policy["maximum_plan_slots"]==1000)
    check("policy_earliest",policy["earliest_preregistered_horizon_bars"]==2); check("policy_max_horizon",policy["maximum_preregistered_horizon_bars"]==16)
    for field in ("admission_may_read_forward_outcomes","outcome_binding_may_select_on_outcome_value","materializer_manual_subset_selection_allowed","missing_slot_silently_dropped","mutable_receipts_allowed","network_fetch_allowed","market_data_fetch_allowed","model_fit_allowed","p_value_generation_allowed","significance_claim_allowed","feature_ranking_allowed","quality_gate_evaluation_allowed","edge_claim_allowed","signal_semantics","paper_trade_execution_allowed","real_capital_allowed","live_alerts_allowed","exchange_execution_allowed","automation_allowed","official_append_allowed"): check("policy_false_"+field,policy[field] is False)
    check("pack_validator","validate_context_feature_pack_v1_package" in source); check("outcome_validator","validate_forward_outcome_label_package" in source); check("engine_cohort_validator","validate_cohort_manifest_v1" in source)
    check("plan_forbidden_keys","FORBIDDEN_PLAN_KEYS" in source); check("plan_alignment_guard","PLAN_SLOT_NOT_15M_ALIGNED" in source); check("plan_spacing_guard","PLAN_SLOT_SPACING_TOO_SHORT" in source); check("plan_freeze_guard","PLAN_SLOT_NOT_AFTER_PLAN_FREEZE" in source)
    check("admission_predeclared_guard","ADMISSION_ANCHOR_NOT_PREDECLARED" in source); check("admission_hyp_freeze_guard","ADMISSION_CONTEXT_BEFORE_HYPOTHESIS_FREEZE" in source); check("admission_deadline_guard","ADMISSION_AFTER_EARLIEST_OUTCOME_COMPLETION" in source)
    admission_segment=source[source.index("def prepare_context_admission_v1"):source.index("def validate_outcome_binding_receipt_v1")]
    check("admission_no_outcome_argument","outcome_package_directory" not in admission_segment)
    check("binding_observation_guard","BINDING_OBSERVATION_ID_MISMATCH" in source); check("binding_cutoff_guard","BINDING_CONTEXT_CUTOFF_MISMATCH" in source); check("binding_anchor_guard","BINDING_CONTEXT_ANCHOR_MISMATCH" in source); check("binding_maturity_guard","BINDING_REQUIRED_HORIZON_NOT_AVAILABLE" in source)
    check("binding_receipt_no_return",'"forward_return" not in receipt' in source)
    check("materializer_plan_scan",'for slot in loaded["plan"]["slots"]' in source); check("materializer_missing","SLOT_NOT_ADMITTED" in source); check("materializer_unbound","ADMITTED_OUTCOME_NOT_BOUND" in source); check("materializer_bound","BOUND_READY_FOR_ENGINE" in source); check("materializer_all_bound",'"all_bound_admissions_included":True' in source or '"all_bound_admissions_included": True' in source); check("materializer_no_manual",'"manual_subset_selection_performed":False' in source or '"manual_subset_selection_performed": False' in source)
    check("official_guard","OFFICIAL_ARTIFACT_CHANGED" in source); check("create_only",'open("xb")' in source)
    check("no_requests","requests" not in imports); check("no_httpx","httpx" not in imports); check("no_websocket","websocket" not in imports and "websockets" not in imports); check("no_subprocess","subprocess" not in imports); check("no_threads",not any(x in imports for x in ("threading","multiprocessing","asyncio","schedule","apscheduler"))); check("no_sklearn","sklearn" not in imports); check("no_scipy","scipy" not in imports)
    check("docs_bias","outcome-aware selection" in docs); check("docs_30m","30 minutes" in docs); check("docs_4h","4 hours" in docs); check("docs_commit_plan","committed" in docs and "published" in docs); check("docs_no_outcome_admission","no forward-outcome-package argument" in docs); check("docs_all_bound","Every valid bound admission is included automatically" in docs)
    check("test_plan","test_05_plan_valid" in tests); check("test_spacing","test_07_plan_spacing" in tests); check("test_admission_deadline","test_16_admission_at_h2_completion_fails" in tests); check("test_binding_maturity","test_21_binding_missing_h16" in tests); check("test_no_return","test_22_binding_does_not_return_forward_return" in tests); check("test_no_subset","test_25_materializer_has_no_subset_argument" in tests); check("test_canonical_hash","test_26_canonical_hypothesis_hash_is_line_ending_independent" in tests)
    try: runtime=m.validate_context_evaluation_prospective_cohort_policy_v1(policy); runtime_ok=runtime["minimum_slot_spacing_bars"]==16 and runtime["earliest_preregistered_horizon_bars"]==2 and runtime["maximum_preregistered_horizon_bars"]==16
    except Exception: runtime_ok=False
    check("policy_runtime",runtime_ok)
    lines=[line for line in MANIFEST.read_text(encoding="utf-8").splitlines() if line.strip()]; manifest_ok=len(lines)==5
    if manifest_ok:
        for line in lines:
            parts=line.split("  ",1)
            if len(parts)!=2 or len(parts[0])!=64 or not Path(parts[1]).is_file() or sha(Path(parts[1]))!=parts[0]: manifest_ok=False; break
    check("manifest_entries_5",len(lines)==5,len(lines)); check("manifest_valid",manifest_ok)
    failed=[x for x in checks if not x["passed"]]; blockers=[x for x in failed if x["blocker"]]
    return {"checks":len(checks),"failed_checks":len(failed),"blockers":len(blockers),"check_results":checks,"real_network_request_executed":False,"market_data_fetched":False,"real_cohort_plan_created":False,"real_cohort_root_initialized":False,"real_admission_receipt_created":False,"real_outcome_binding_created":False,"real_engine_cohort_materialized":False,"quality_gate_evaluated":False,"edge_established":False,"signal_generated":False,"official_append_executed":False}
if __name__=="__main__":
    result=run(); print(json.dumps(result,indent=2,sort_keys=True)); raise SystemExit(0 if result["blockers"]==0 else 1)
