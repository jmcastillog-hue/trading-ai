from __future__ import annotations

import csv, hashlib, json, tempfile, unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from src.long_side.long_supervised_15m_observation_loop_v2 import (
    HUMAN_15M_FIBONACCI_CONTEXT,
    MAX_IMPLEMENTATION_OR_REPAIR_ATTEMPTS,
    MAX_OBSERVATION_CYCLES,
    REAL_SOURCE_ATTESTATION,
    SESSION_AUTHORIZATION,
    Supervised15mObservationLoopError,
    compare_with_frozen_human_context,
    next_15m_capture_time,
    run_bounded_supervised_15m_session,
    validate_supervised_15m_session,
)

FALSE_CAPTURE = {
    "review_package_created": False,
    "candidate_evaluated": False,
    "candidate_detected": False,
    "manual_confirmed": False,
    "official_dataset_write_performed": False,
    "official_manifest_write_performed": False,
    "official_append_invoked": False,
    "official_append_environment_gate_modified": False,
    "signal_generation_enabled": False,
    "live_alerts_allowed": False,
    "paper_trade_execution_allowed": False,
    "real_capital_allowed": False,
    "market_execution_allowed": False,
    "exchange_execution_allowed": False,
    "automation_allowed": False,
    "execution_allowed": False,
}
FALSE_PACKAGE = {
    "manual_confirmation_required": True,
    "manual_confirmed": False,
    "official_dataset_write_performed": False,
    "official_manifest_write_performed": False,
    "official_append_environment_gate_modified": False,
    "paper_trade_execution_allowed": False,
    "real_capital_allowed": False,
    "market_execution_allowed": False,
    "exchange_execution_allowed": False,
    "automation_allowed": False,
    "execution_allowed": False,
}

class Clock:
    def __init__(self): self.value = datetime(2026, 8, 8, 13, 47, 0, tzinfo=timezone.utc)
    def __call__(self): return self.value
    def sleep(self, seconds): self.value += timedelta(seconds=seconds)

class Tests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.root = Path(self.tmp.name)
        self.repo = self.root / "repo"; self.repo.mkdir(); (self.repo / ".git").mkdir()
        d = self.repo / "data/forward"; d.mkdir(parents=True)
        (d / "long_forward_observation_dataset_v1.csv").write_text("x\n", encoding="utf-8")
        (d / "long_forward_observation_dataset_v1.manifest.csv").write_text("y\n", encoding="utf-8")
        self.external = self.root / "external"; self.external.mkdir(); self.clock = Clock(); self.capture_count = 0; self.package_count = 0
    def tearDown(self): self.tmp.cleanup()
    def err(self, code, fn, *args, **kwargs):
        with self.assertRaises(Supervised15mObservationLoopError) as ctx: fn(*args, **kwargs)
        self.assertEqual(ctx.exception.code, code)
    def write_capture(self, directory: Path, close_time: datetime, *, request_count=1, safe=True):
        directory.mkdir(); source = directory / "btc_usdt_15m_closed_candles.csv"; meta = directory / "capture_metadata.json"
        rows=[]; start = close_time - timedelta(minutes=15*62 + 14, seconds=59.999)
        fields=["open_time_utc","close_time_utc","symbol","timeframe","open","high","low","close","volume","candle_closed"]
        for i in range(63):
            ot=start+timedelta(minutes=15*i); ct=ot+timedelta(minutes=14,seconds=59.999); p=64000+i
            rows.append({"open_time_utc":ot.isoformat(),"close_time_utc":ct.isoformat(),"symbol":"BTCUSDT","timeframe":"15m","open":str(p),"high":str(p+20),"low":str(p-20),"close":str(p+5),"volume":"100","candle_closed":"True"})
        with source.open("w",encoding="utf-8",newline="") as f: w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(rows)
        meta.write_text(json.dumps({"captured_at_utc":(close_time+timedelta(seconds=5)).isoformat()}),encoding="utf-8")
        sha=hashlib.sha256(source.read_bytes()).hexdigest(); result={"capture_id":f"CAP_{self.capture_count}","source_csv":str(source),"metadata_json":str(meta),"latest_closed_candle_utc":rows[-1]["close_time_utc"],"source_artifact_sha256":sha,"network_request_count":request_count,"one_shot_foreground":True,**FALSE_CAPTURE}
        if not safe: result["automation_allowed"]=True
        return result
    def capture(self, **kwargs):
        self.capture_count+=1; close=datetime(2026,8,8,13,59,59,999000,tzinfo=timezone.utc)+timedelta(minutes=15*(self.capture_count-1))
        return self.write_capture(Path(kwargs["output_directory"]),close)
    def package(self, **kwargs):
        self.package_count+=1; Path(kwargs["output_directory"]).mkdir(); candidate=False
        return {"package_id":f"PKG_{self.package_count}","source_artifact_sha256":kwargs["expected_source_sha256"],"latest_closed_candle_utc":kwargs["prospective_start_utc"],"candidate_detected":candidate,"eligible_for_real_human_review":candidate,**FALSE_PACKAGE}
    def run_session(self, cycles=1, minimum="2026-08-08T04:29:59.999000+00:00", capture=None, package=None):
        return run_bounded_supervised_15m_session(repo_root=self.repo,output_directory=self.external/"session",max_cycles=cycles,source_attestation=REAL_SOURCE_ATTESTATION,minimum_latest_closed_candle_utc=minimum,authorization=SESSION_AUTHORIZATION,clock=self.clock,sleeper=self.clock.sleep,capture_callable=capture or self.capture,package_callable=package or self.package)

    def test_01_next_time_after_grace(self): self.assertEqual(next_15m_capture_time(datetime(2026,8,8,13,47,tzinfo=timezone.utc)),datetime(2026,8,8,14,0,5,tzinfo=timezone.utc))
    def test_02_next_time_inside_grace(self): self.assertEqual(next_15m_capture_time(datetime(2026,8,8,14,0,3,tzinfo=timezone.utc)),datetime(2026,8,8,14,0,5,tzinfo=timezone.utc))
    def test_03_repair_limit(self): self.assertEqual(MAX_IMPLEMENTATION_OR_REPAIR_ATTEMPTS,10)
    def test_04_cycle_limit(self): self.assertEqual(MAX_OBSERVATION_CYCLES,8)
    def test_05_auth_required(self): self.err("SESSION_AUTHORIZATION_REQUIRED",run_bounded_supervised_15m_session,repo_root=self.repo,output_directory=self.external/"s",max_cycles=1,source_attestation=REAL_SOURCE_ATTESTATION,minimum_latest_closed_candle_utc=None)
    def test_06_attestation_required(self): self.err("SESSION_SOURCE_ATTESTATION_REQUIRED",run_bounded_supervised_15m_session,repo_root=self.repo,output_directory=self.external/"s",max_cycles=1,source_attestation="NO",minimum_latest_closed_candle_utc=None,authorization=SESSION_AUTHORIZATION)
    def test_07_cycle_zero_rejected(self): self.err("SESSION_CYCLE_LIMIT_INVALID",run_bounded_supervised_15m_session,repo_root=self.repo,output_directory=self.external/"s",max_cycles=0,source_attestation=REAL_SOURCE_ATTESTATION,minimum_latest_closed_candle_utc=None,authorization=SESSION_AUTHORIZATION)
    def test_08_cycle_over_max_rejected(self): self.err("SESSION_CYCLE_LIMIT_INVALID",run_bounded_supervised_15m_session,repo_root=self.repo,output_directory=self.external/"s",max_cycles=9,source_attestation=REAL_SOURCE_ATTESTATION,minimum_latest_closed_candle_utc=None,authorization=SESSION_AUTHORIZATION)
    def test_09_output_in_repo_rejected(self): self.err("OUTPUT_INSIDE_REPOSITORY_PROHIBITED",run_bounded_supervised_15m_session,repo_root=self.repo,output_directory=self.repo/"s",max_cycles=1,source_attestation=REAL_SOURCE_ATTESTATION,minimum_latest_closed_candle_utc=None,authorization=SESSION_AUTHORIZATION)
    def test_10_existing_output_rejected(self):
        p=self.external/"s"; p.mkdir(); self.err("OUTPUT_ALREADY_EXISTS",run_bounded_supervised_15m_session,repo_root=self.repo,output_directory=p,max_cycles=1,source_attestation=REAL_SOURCE_ATTESTATION,minimum_latest_closed_candle_utc=None,authorization=SESSION_AUTHORIZATION)
    def test_11_one_cycle(self):
        r=self.run_session(); self.assertEqual((r["completed_cycles"],r["candidate_count"],r["network_request_count"]),(1,0,1)); self.assertFalse(r["external_notifications_sent"])
    def test_12_three_cycles(self):
        r=self.run_session(3); self.assertEqual(r["completed_cycles"],3); self.assertEqual(r["stop_reason"],"MAX_CYCLES_COMPLETED")
    def test_13_stop_on_candidate(self):
        def p(**kwargs):
            self.package_count+=1; Path(kwargs["output_directory"]).mkdir(); cand=self.package_count==2
            return {"package_id":f"P{self.package_count}","source_artifact_sha256":kwargs["expected_source_sha256"],"latest_closed_candle_utc":kwargs["prospective_start_utc"],"candidate_detected":cand,"eligible_for_real_human_review":cand,**FALSE_PACKAGE}
        r=self.run_session(3,package=p); self.assertEqual(r["completed_cycles"],2); self.assertEqual(r["stop_reason"],"FIRST_CANDIDATE_PENDING_HUMAN_REVIEW")
    def test_14_old_first_candle_rejected(self):
        def c(**kwargs): self.capture_count+=1; return self.write_capture(Path(kwargs["output_directory"]),datetime(2026,8,8,4,29,59,999000,tzinfo=timezone.utc))
        self.err("DUPLICATE_OR_OLD_CANDLE",self.run_session,1,"2026-08-08T04:29:59.999000+00:00",c)
    def test_15_duplicate_second_candle_rejected(self):
        fixed=datetime(2026,8,8,14,0,0,tzinfo=timezone.utc)
        def c(**kwargs): self.capture_count+=1; return self.write_capture(Path(kwargs["output_directory"]),fixed)
        self.err("DUPLICATE_OR_OLD_CANDLE",self.run_session,2,None,c)
    def test_16_bad_request_count_rejected(self):
        def c(**kwargs): self.capture_count+=1; return self.write_capture(Path(kwargs["output_directory"]),datetime(2026,8,8,14,0,tzinfo=timezone.utc),request_count=2)
        self.err("CAPTURE_MODE_INVALID",self.run_session,1,None,c)
    def test_17_capture_permission_rejected(self):
        def c(**kwargs): self.capture_count+=1; return self.write_capture(Path(kwargs["output_directory"]),datetime(2026,8,8,14,0,tzinfo=timezone.utc),safe=False)
        self.err("CAPTURE_PERMISSION_INVALID",self.run_session,1,None,c)
    def test_18_context_classification(self):
        x=compare_with_frozen_human_context({"open":64981.61,"high":65001.46,"low":64976,"close":65001.45})
        self.assertEqual(x["positional_state"],"BETWEEN_INTERMEDIATE_AND_UPPER_LEVEL_1"); self.assertEqual(x["nearest_level"],"upper_level_1"); self.assertFalse(x["direction_inferred_from_levels"])
    def test_19_confluence_touch_neutral(self):
        x=compare_with_frozen_human_context({"open":64100,"high":64120,"low":63980,"close":64050}); self.assertTrue(x["zones"]["confluence_38_2_touched"]); self.assertFalse(x["actionable_signal_generated"])
    def test_20_session_validation(self):
        r=self.run_session(2); v=validate_supervised_15m_session(r["output_directory"]); self.assertEqual(v["completed_cycles"],2); self.assertEqual(v["manifest_entries"],2)

if __name__ == "__main__": unittest.main()
