from __future__ import annotations

import ast, csv, hashlib, json, tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

from src.long_side.long_supervised_15m_observation_loop_v2 import (
    HUMAN_15M_FIBONACCI_CONTEXT, MAX_IMPLEMENTATION_OR_REPAIR_ATTEMPTS,
    REAL_SOURCE_ATTESTATION, SESSION_AUTHORIZATION,
    run_bounded_supervised_15m_session, validate_supervised_15m_session,
)

FALSE_CAPTURE={"review_package_created":False,"candidate_evaluated":False,"candidate_detected":False,"manual_confirmed":False,"official_dataset_write_performed":False,"official_manifest_write_performed":False,"official_append_invoked":False,"official_append_environment_gate_modified":False,"signal_generation_enabled":False,"live_alerts_allowed":False,"paper_trade_execution_allowed":False,"real_capital_allowed":False,"market_execution_allowed":False,"exchange_execution_allowed":False,"automation_allowed":False,"execution_allowed":False}
FALSE_PACKAGE={"manual_confirmation_required":True,"manual_confirmed":False,"official_dataset_write_performed":False,"official_manifest_write_performed":False,"official_append_environment_gate_modified":False,"paper_trade_execution_allowed":False,"real_capital_allowed":False,"market_execution_allowed":False,"exchange_execution_allowed":False,"automation_allowed":False,"execution_allowed":False}

class Clock:
    def __init__(self): self.value=datetime(2026,8,8,13,47,tzinfo=timezone.utc)
    def __call__(self): return self.value
    def sleep(self, seconds): self.value += timedelta(seconds=seconds)

def main() -> int:
    checks=[]
    def add(name, passed, details): checks.append({"check":name,"passed":bool(passed),"details":details,"blocker":not bool(passed)})
    path=Path("src/long_side/long_supervised_15m_observation_loop_v2.py"); source=path.read_text(encoding="utf-8"); tree=ast.parse(source)
    imports=set(); calls=set()
    for node in ast.walk(tree):
        if isinstance(node,ast.Import): imports.update(a.name for a in node.names)
        elif isinstance(node,ast.ImportFrom) and node.module: imports.add(node.module)
        elif isinstance(node,ast.Call):
            if isinstance(node.func,ast.Name): calls.add(node.func.id)
            elif isinstance(node.func,ast.Attribute): calls.add(node.func.attr)
    add("repair_attempt_limit_10",MAX_IMPLEMENTATION_OR_REPAIR_ATTEMPTS==10,str(MAX_IMPLEMENTATION_OR_REPAIR_ATTEMPTS))
    add("no_thread_process_runtime",not any(x.startswith(("threading","multiprocessing","subprocess")) for x in imports),str(sorted(imports)))
    add("no_scheduler_dependency",not any(x.startswith(("schedule","apscheduler")) for x in imports),"none")
    add("no_direct_http_client",not any(x.startswith(("requests","urllib","httpx","aiohttp")) for x in imports),"delegated to capture boundary")
    add("no_messaging_browser_strings",all(x not in source.lower() for x in ("whatsapp","telegram","selenium","playwright","quantfury")),"none")
    add("official_writer_absent","append_official_prospective_evidence" not in source,"absent")
    add("stop_on_candidate","FIRST_CANDIDATE_PENDING_HUMAN_REVIEW" in source,"present")
    add("human_context_non_actionable","direction_inferred_from_levels" in source and "actionable_signal_generated" in source,"present")
    add("microstructure_not_inferred","liquidity_side_inferred_without_microstructure" in source,"present")
    add("frozen_38_2_band",HUMAN_15M_FIBONACCI_CONTEXT["confluence_38_2_low"]==63956.34 and HUMAN_15M_FIBONACCI_CONTEXT["confluence_38_2_high"]==64019.05,"63956.34-64019.05")

    with tempfile.TemporaryDirectory() as td:
        root=Path(td); repo=root/"repo"; repo.mkdir(); (repo/".git").mkdir(); d=repo/"data/forward"; d.mkdir(parents=True); (d/"long_forward_observation_dataset_v1.csv").write_text("x\n",encoding="utf-8"); (d/"long_forward_observation_dataset_v1.manifest.csv").write_text("y\n",encoding="utf-8"); external=root/"external"; external.mkdir(); clock=Clock(); count=0
        def capture(**kwargs):
            nonlocal count; count+=1; out=Path(kwargs["output_directory"]); out.mkdir(); src=out/"btc_usdt_15m_closed_candles.csv"; meta=out/"capture_metadata.json"; latest=datetime(2026,8,8,13,59,59,999000,tzinfo=timezone.utc)+timedelta(minutes=15*(count-1)); start=latest-timedelta(minutes=15*62+14,seconds=59.999); fields=["open_time_utc","close_time_utc","symbol","timeframe","open","high","low","close","volume","candle_closed"]; rows=[]
            for i in range(63):
                ot=start+timedelta(minutes=15*i); ct=ot+timedelta(minutes=14,seconds=59.999); p=64000+i; rows.append({"open_time_utc":ot.isoformat(),"close_time_utc":ct.isoformat(),"symbol":"BTCUSDT","timeframe":"15m","open":str(p),"high":str(p+20),"low":str(p-20),"close":str(p+5),"volume":"100","candle_closed":"True"})
            with src.open("w",encoding="utf-8",newline="") as f: w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(rows)
            meta.write_text(json.dumps({"captured_at_utc":(latest+timedelta(seconds=5)).isoformat()}),encoding="utf-8"); sha=hashlib.sha256(src.read_bytes()).hexdigest(); return {"capture_id":f"MOCK_{count}","source_csv":str(src),"metadata_json":str(meta),"latest_closed_candle_utc":rows[-1]["close_time_utc"],"source_artifact_sha256":sha,"network_request_count":1,"one_shot_foreground":True,**FALSE_CAPTURE}
        def package(**kwargs):
            out=Path(kwargs["output_directory"]); out.mkdir(); return {"package_id":f"PKG_{count}","source_artifact_sha256":kwargs["expected_source_sha256"],"latest_closed_candle_utc":kwargs["prospective_start_utc"],"candidate_detected":False,"eligible_for_real_human_review":False,**FALSE_PACKAGE}
        before=(repo/"data/forward/long_forward_observation_dataset_v1.csv").read_bytes(),(repo/"data/forward/long_forward_observation_dataset_v1.manifest.csv").read_bytes()
        result=run_bounded_supervised_15m_session(repo_root=repo,output_directory=external/"session",max_cycles=2,source_attestation=REAL_SOURCE_ATTESTATION,minimum_latest_closed_candle_utc="2026-08-08T04:29:59.999000+00:00",authorization=SESSION_AUTHORIZATION,clock=clock,sleeper=clock.sleep,capture_callable=capture,package_callable=package)
        val=validate_supervised_15m_session(result["output_directory"]); after=(repo/"data/forward/long_forward_observation_dataset_v1.csv").read_bytes(),(repo/"data/forward/long_forward_observation_dataset_v1.manifest.csv").read_bytes()
        add("mock_session_completed",result["completed_cycles"]==2,str(result["completed_cycles"]))
        add("one_request_per_cycle",result["network_request_count"]==2,str(result["network_request_count"]))
        add("no_candidate_mock",result["candidate_count"]==0,str(result["candidate_count"]))
        add("session_manifest_valid",val["manifest_entries"]==2,str(val["manifest_entries"]))
        add("official_artifacts_unchanged",before==after,"unchanged")
        add("notifications_disabled",result["external_notifications_sent"] is False,"false")
        add("manual_confirmation_false",result["manual_confirmed"] is False,"false")
        add("bounded_foreground",result["bounded"] is True and result["foreground_only"] is True,"true")
    failed=[x for x in checks if not x["passed"]]
    payload={"capability":"LONG_SUPERVISED_15M_OBSERVATION_LOOP_V2","decision":"LONG_SUPERVISED_15M_OBSERVATION_LOOP_V2_VALIDATED_NO_REAL_NETWORK","checks":len(checks),"failed_checks":len(failed),"blockers":sum(1 for x in failed if x["blocker"]),"mocked_cycles":2,"real_network_request_executed":False,"real_market_data_acquired":False,"real_loop_executed":False,"external_notifications_sent":False,"official_append_executed":False,"check_results":checks}
    print(json.dumps(payload,indent=2,sort_keys=True)); return 1 if failed else 0

if __name__=="__main__": raise SystemExit(main())
