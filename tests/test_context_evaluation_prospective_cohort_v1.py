from __future__ import annotations
import unittest
import hashlib
import json
from datetime import datetime, timedelta, timezone
from src.evaluation import context_evaluation_prospective_cohort_v1 as m


def policy():
    return {
        "schema_version":"CONTEXT_EVALUATION_PROSPECTIVE_COHORT_POLICY_V1","capability":"CONTEXT_EVALUATION_PROSPECTIVE_COHORT_V1","policy_effective_from_utc":"2026-08-22T16:15:00+00:00","preregistered_hypothesis_manifest_path":"research/context_evaluation/context_evaluation_hypothesis_manifest_v1.json","preregistered_hypothesis_manifest_sha256":"a"*64,"preregistered_hypothesis_frozen_at_utc":"2026-08-22T16:15:00+00:00","expected_hypothesis_manifest_schema":"CONTEXT_EVALUATION_HYPOTHESIS_MANIFEST_V1","expected_engine_cohort_manifest_schema":"CONTEXT_EVALUATION_COHORT_MANIFEST_V1","sampling_mode":"PREDECLARED_UTC_CONTEXT_ANCHORS","slot_alignment_minutes":15,"minimum_slot_spacing_bars":16,"bar_minutes":15,"minimum_plan_slots":10,"preferred_plan_slots":30,"maximum_plan_slots":1000,"earliest_preregistered_horizon_bars":2,"maximum_preregistered_horizon_bars":16,"admission_must_precede_earliest_outcome_completion":True,"admission_requires_exact_context_anchor_match":True,"admission_requires_context_cutoff_not_before_hypothesis_freeze":True,"admission_requires_predeclared_slot":True,"admission_may_read_forward_outcomes":False,"outcome_binding_requires_all_preregistered_horizons_available":True,"outcome_binding_may_select_on_outcome_value":False,"materializer_manual_subset_selection_allowed":False,"missing_slot_silently_dropped":False,"mutable_receipts_allowed":False,"network_fetch_allowed":False,"market_data_fetch_allowed":False,"model_fit_allowed":False,"p_value_generation_allowed":False,"significance_claim_allowed":False,"feature_ranking_allowed":False,"quality_gate_evaluation_allowed":False,"edge_claim_allowed":False,"signal_semantics":False,"paper_trade_execution_allowed":False,"real_capital_allowed":False,"live_alerts_allowed":False,"exchange_execution_allowed":False,"automation_allowed":False,"official_append_allowed":False,
    }

def hypothesis(): return {"frozen_at_utc":"2026-08-22T16:15:00+00:00"}

def plan(count=10,spacing=4,frozen="2026-08-22T17:00:00+00:00"):
    start=datetime(2026,8,22,20,0,tzinfo=timezone.utc)
    return {"schema_version":m.PLAN_SCHEMA_VERSION,"cohort_id":"C1","plan_frozen_at_utc":frozen,"hypothesis_manifest_sha256":"a"*64,"hypothesis_frozen_at_utc":"2026-08-22T16:15:00+00:00","sampling_mode":"PREDECLARED_UTC_CONTEXT_ANCHORS","slots":[{"slot_id":f"S{i:03d}","context_anchor_open_utc":(start+timedelta(hours=i*spacing)).isoformat()} for i in range(count)]}

def admission_pack(anchor="2026-08-22T20:00:00+00:00",cutoff="2026-08-22T19:55:00+00:00"): return {"observation_id":"OBS1","context_anchor_open_utc":anchor,"context_cutoff_utc":cutoff}

def admission(): return {"observation_id":"OBS1","context_anchor_open_utc":"2026-08-22T20:00:00+00:00","context_cutoff_utc":"2026-08-22T19:55:00+00:00"}

def outcomes(missing=None):
    labels={str(h):{"horizon_bars":h,"label_status":"PENDING" if h==missing else "AVAILABLE","forward_return":h/100} for h in (1,2,4,8,16)}
    return {"synchronized_context_outcome":{"context_available_at_utc":"2026-08-22T19:55:00+00:00","anchor_open_time_utc":"2026-08-22T20:00:00+00:00","labels":labels}}

class Tests(unittest.TestCase):
    def test_01_identity(self): self.assertEqual(m.CAPABILITY,"CONTEXT_EVALUATION_PROSPECTIVE_COHORT_V1")
    def test_02_policy_valid(self): self.assertEqual(m.validate_context_evaluation_prospective_cohort_policy_v1(policy())["minimum_slot_spacing_bars"],16)
    def test_03_policy_no_outcome_admission(self):
        p=policy(); p["admission_may_read_forward_outcomes"]=True
        with self.assertRaises(m.ContextEvaluationProspectiveCohortError): m.validate_context_evaluation_prospective_cohort_policy_v1(p)
    def test_04_policy_no_manual_subset(self):
        p=policy(); p["materializer_manual_subset_selection_allowed"]=True
        with self.assertRaises(m.ContextEvaluationProspectiveCohortError): m.validate_context_evaluation_prospective_cohort_policy_v1(p)
    def test_05_plan_valid(self): self.assertEqual(len(m.validate_prospective_cohort_plan_v1(plan(),policy=policy(),hypothesis_manifest=hypothesis(),hypothesis_manifest_sha256="a"*64)["slots"]),10)
    def test_06_plan_minimum_slots(self):
        with self.assertRaises(m.ContextEvaluationProspectiveCohortError): m.validate_prospective_cohort_plan_v1(plan(count=9),policy=policy(),hypothesis_manifest=hypothesis(),hypothesis_manifest_sha256="a"*64)
    def test_07_plan_spacing(self):
        with self.assertRaises(m.ContextEvaluationProspectiveCohortError): m.validate_prospective_cohort_plan_v1(plan(spacing=3),policy=policy(),hypothesis_manifest=hypothesis(),hypothesis_manifest_sha256="a"*64)
    def test_08_plan_misaligned(self):
        x=plan(); x["slots"][0]["context_anchor_open_utc"]="2026-08-22T20:07:00+00:00"
        with self.assertRaises(m.ContextEvaluationProspectiveCohortError): m.validate_prospective_cohort_plan_v1(x,policy=policy(),hypothesis_manifest=hypothesis(),hypothesis_manifest_sha256="a"*64)
    def test_09_plan_before_hypothesis_freeze(self):
        with self.assertRaises(m.ContextEvaluationProspectiveCohortError): m.validate_prospective_cohort_plan_v1(plan(frozen="2026-08-22T16:00:00+00:00"),policy=policy(),hypothesis_manifest=hypothesis(),hypothesis_manifest_sha256="a"*64)
    def test_10_plan_duplicate_slot_id(self):
        x=plan(); x["slots"][1]["slot_id"]=x["slots"][0]["slot_id"]
        with self.assertRaises(m.ContextEvaluationProspectiveCohortError): m.validate_prospective_cohort_plan_v1(x,policy=policy(),hypothesis_manifest=hypothesis(),hypothesis_manifest_sha256="a"*64)
    def test_11_plan_unsorted(self):
        x=plan(); x["slots"][0],x["slots"][1]=x["slots"][1],x["slots"][0]
        with self.assertRaises(m.ContextEvaluationProspectiveCohortError): m.validate_prospective_cohort_plan_v1(x,policy=policy(),hypothesis_manifest=hypothesis(),hypothesis_manifest_sha256="a"*64)
    def test_12_admission_valid(self):
        r=m.validate_admission_candidate_v1(pack=admission_pack(),plan=plan(),hypothesis_frozen_at_utc="2026-08-22T16:15:00+00:00",earliest_horizon_bars=2,admitted_at_utc=datetime(2026,8,22,20,5,tzinfo=timezone.utc)); self.assertEqual(r["slot_id"],"S000")
    def test_13_admission_unplanned(self):
        with self.assertRaises(m.ContextEvaluationProspectiveCohortError): m.validate_admission_candidate_v1(pack=admission_pack(anchor="2026-08-22T21:00:00+00:00",cutoff="2026-08-22T20:55:00+00:00"),plan=plan(),hypothesis_frozen_at_utc="2026-08-22T16:15:00+00:00",earliest_horizon_bars=2,admitted_at_utc=datetime(2026,8,22,21,5,tzinfo=timezone.utc))
    def test_14_admission_pre_hypothesis(self):
        with self.assertRaises(m.ContextEvaluationProspectiveCohortError): m.validate_admission_candidate_v1(pack=admission_pack(cutoff="2026-08-22T16:00:00+00:00"),plan=plan(),hypothesis_frozen_at_utc="2026-08-22T16:15:00+00:00",earliest_horizon_bars=2,admitted_at_utc=datetime(2026,8,22,20,5,tzinfo=timezone.utc))
    def test_15_admission_before_cutoff(self):
        with self.assertRaises(m.ContextEvaluationProspectiveCohortError): m.validate_admission_candidate_v1(pack=admission_pack(),plan=plan(),hypothesis_frozen_at_utc="2026-08-22T16:15:00+00:00",earliest_horizon_bars=2,admitted_at_utc=datetime(2026,8,22,19,50,tzinfo=timezone.utc))
    def test_16_admission_at_h2_completion_fails(self):
        with self.assertRaises(m.ContextEvaluationProspectiveCohortError): m.validate_admission_candidate_v1(pack=admission_pack(),plan=plan(),hypothesis_frozen_at_utc="2026-08-22T16:15:00+00:00",earliest_horizon_bars=2,admitted_at_utc=datetime(2026,8,22,20,30,tzinfo=timezone.utc))
    def test_17_binding_valid(self): self.assertEqual(m.validate_binding_candidate_v1(admission=admission(),descriptor={"observation_id":"OBS1"},outcomes=outcomes(),required_horizons=(2,4,16))["required_horizons_available"],[2,4,16])
    def test_18_binding_observation_mismatch(self):
        with self.assertRaises(m.ContextEvaluationProspectiveCohortError): m.validate_binding_candidate_v1(admission=admission(),descriptor={"observation_id":"OTHER"},outcomes=outcomes(),required_horizons=(2,4,16))
    def test_19_binding_cutoff_mismatch(self):
        x=outcomes(); x["synchronized_context_outcome"]["context_available_at_utc"]="2026-08-22T19:54:00+00:00"
        with self.assertRaises(m.ContextEvaluationProspectiveCohortError): m.validate_binding_candidate_v1(admission=admission(),descriptor={"observation_id":"OBS1"},outcomes=x,required_horizons=(2,4,16))
    def test_20_binding_anchor_mismatch(self):
        x=outcomes(); x["synchronized_context_outcome"]["anchor_open_time_utc"]="2026-08-22T20:15:00+00:00"
        with self.assertRaises(m.ContextEvaluationProspectiveCohortError): m.validate_binding_candidate_v1(admission=admission(),descriptor={"observation_id":"OBS1"},outcomes=x,required_horizons=(2,4,16))
    def test_21_binding_missing_h16(self):
        with self.assertRaises(m.ContextEvaluationProspectiveCohortError): m.validate_binding_candidate_v1(admission=admission(),descriptor={"observation_id":"OBS1"},outcomes=outcomes(missing=16),required_horizons=(2,4,16))
    def test_22_binding_does_not_return_forward_return(self): self.assertNotIn("forward_return",m.validate_binding_candidate_v1(admission=admission(),descriptor={"observation_id":"OBS1"},outcomes=outcomes(),required_horizons=(2,4,16)))
    def test_23_auth_constants(self): self.assertTrue(m.ADMISSION_AUTHORIZATION.startswith("PREPARE_") and m.BINDING_AUTHORIZATION.startswith("PREPARE_"))
    def test_24_no_outcome_argument_in_admission(self):
        import inspect; self.assertNotIn("outcome_package_directory",inspect.signature(m.prepare_context_admission_v1).parameters)
    def test_25_materializer_has_no_subset_argument(self):
        import inspect; self.assertNotIn("selected_observations",inspect.signature(m.materialize_engine_cohort_manifest_v1).parameters)

    def test_26_canonical_hypothesis_hash_is_line_ending_independent(self):
        value={"schema_version":"X","a":1}
        canonical=(json.dumps(value,sort_keys=True,separators=(",",":"),ensure_ascii=True,allow_nan=False)+"\n").encode("utf-8")
        crlf=(json.dumps(value,sort_keys=True,separators=(",",":"),ensure_ascii=True,allow_nan=False)+"\r\n").encode("utf-8")
        self.assertEqual(m._canonical_json_sha256(value),hashlib.sha256(canonical).hexdigest())
        self.assertNotEqual(hashlib.sha256(crlf).hexdigest(),hashlib.sha256(canonical).hexdigest())

if __name__ == "__main__": unittest.main(verbosity=2)
