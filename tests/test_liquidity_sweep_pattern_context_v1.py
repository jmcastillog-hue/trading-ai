from __future__ import annotations

import csv, hashlib, json, os, tempfile, unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from src.context.liquidity_sweep_pattern_context_v1 import *

POLICY_EFFECTIVE="2026-08-17T00:00:00+00:00"; REFERENCE="2026-08-18T00:00:00+00:00"; REFERENCE_CLOSE="2026-08-17T23:59:59.999000+00:00"; CAPTURED_AT="2026-08-18T00:00:05+00:00"; CUTOFF="2026-08-18T00:00:10+00:00"

def descriptor(reference=REFERENCE, close=REFERENCE_CLOSE, cutoff=CUTOFF):
    return {"observation_descriptor_schema_version":"FORWARD_OUTCOME_OBSERVATION_DESCRIPTOR_V1","observation_id":"OBS_LIQ_001","symbol":"BTCUSDT","timeframe":"15m","reference_boundary_utc":reference,"reference_closed_candle_utc":close,"synchronized_context_available_at_utc":cutoff,"primary_candidate_detected":False}

def policy_fixture():
    return {"schema_version":"LIQUIDITY_SWEEP_PATTERN_CONTEXT_POLICY_V1","feature_id":"LIQUIDITY_SWEEP_PATTERN_CONTEXT_V1","policy_effective_from_utc":POLICY_EFFECTIVE,"source_capture_capability":"LONG_PRIMARY_PUBLIC_CLOSED_CANDLE_CAPTURE_V1","source_provider":"BINANCE_PUBLIC_SPOT_API","source_symbol":"BTCUSDT","source_timeframe":"15m","rolling_extreme_lookback_bars":48,"atr_bars":14,"same_bar_response_only":True,"future_bar_confirmation_used":False,"symmetric_high_low_context":True,"sweep_is_price_action_proxy_only":True,"hidden_stop_orders_observed":False,"liquidations_observed":False,"primary_candidate_semantics_reused":False,"directional_meaning_assigned":False,"composite_score_assigned":False,"signal_semantics":False}

def metadata(captured=CAPTURED_AT, close=REFERENCE_CLOSE, sha="a"*64):
    return {"capture_schema_version":"LONG_PRIMARY_PUBLIC_CLOSED_CANDLE_CAPTURE_V1","capability":"LONG_PRIMARY_PUBLIC_CLOSED_CANDLE_CAPTURE_V1","implementation_schema_version":"LONG_PRIMARY_PUBLIC_CLOSED_CANDLE_CAPTURE_IMPLEMENTATION_V1","capture_id":"LONGCAP_TEST_001","capture_mode":"ONE_SHOT_FOREGROUND","provider":"BINANCE_PUBLIC_SPOT_API","endpoint":"https://example.invalid","symbol":"BTCUSDT","timeframe":"15m","request_limit":64,"network_request_count":1,"captured_at_utc":captured,"closed_candle_rows":49,"open_candles_excluded":1,"latest_closed_candle_utc":close,"source_artifact":"btc_usdt_15m_closed_candles.csv","source_artifact_sha256":sha,"source_columns":["open_time_utc","close_time_utc","symbol","timeframe","open","high","low","close","volume","candle_closed"],"latest_candle_only_future_evaluation_contract":True,"lookahead_used":False,"automatic_or_recurring_capture":False,"review_package_created":False,"candidate_evaluated":False,"candidate_detected":False,"manual_confirmation_required":True,"manual_confirmed":False,"official_dataset_write_allowed":False,"official_append_allowed":False,"signal_generation_enabled":False,"live_alerts_allowed":False,"paper_trade_execution_allowed":False,"real_capital_allowed":False,"market_execution_allowed":False,"exchange_execution_allowed":False,"automation_allowed":False,"execution_allowed":False}

def rows(latest=(100.0,100.5,99.2,100.0,150.0), close=REFERENCE_CLOSE):
    close_dt=datetime.fromisoformat(close).astimezone(timezone.utc); latest_open=close_dt-timedelta(minutes=14,seconds=59,milliseconds=999); first=latest_open-timedelta(minutes=15*48); out=[]
    for i in range(49):
        ot=first+timedelta(minutes=15*i); ct=ot+timedelta(minutes=15)-timedelta(milliseconds=1); o,h,l,c,v=(100.0,101.0,99.0,100.0,100.0+i) if i<48 else latest; out.append({"open_time":ot,"close_time":ct,"open":o,"high":h,"low":l,"close":c,"volume":v})
    return out

def component(latest=(100.0,100.5,99.2,100.0,150.0), desc=None, meta=None, produced="2026-08-18T00:00:06+00:00", close=REFERENCE_CLOSE):
    return build_liquidity_sweep_pattern_context_v1_component(observation_descriptor=desc or descriptor(),capture_metadata=meta or metadata(),candles=rows(latest,close),source_csv_sha256="a"*64,source_manifest_sha256="b"*64,policy=policy_fixture(),policy_sha256="c"*64,produced_at_utc=produced)

class Tests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); root=Path(self.tmp.name); self.repo=root/"repo"; self.repo.mkdir(); (self.repo/".git").mkdir(); off=self.repo/"data"/"forward"; off.mkdir(parents=True); (off/"long_forward_observation_dataset_v1.csv").write_text("header\n"); (off/"long_forward_observation_dataset_v1.manifest.csv").write_text("manifest\n"); res=self.repo/"src"/"context"/"resources"; res.mkdir(parents=True); (res/"liquidity_sweep_pattern_context_policy_v1.json").write_text(json.dumps(policy_fixture(),sort_keys=True,indent=2)+"\n"); self.external=root/"external"; self.external.mkdir(); os.environ.pop("TRADING_AI_OFFICIAL_LONG_EVIDENCE_APPEND_ALLOWED",None)
    def tearDown(self): os.environ.pop("TRADING_AI_OFFICIAL_LONG_EVIDENCE_APPEND_ALLOWED",None); self.tmp.cleanup()
    def test_01_constants(self): self.assertEqual((CAPABILITY,FEATURE_ID,SOURCE_KIND),("LIQUIDITY_SWEEP_PATTERN_CONTEXT_V1","LIQUIDITY_SWEEP_PATTERN_CONTEXT_V1","OBSERVED_MARKET"))
    def test_02_policy(self): self.assertEqual(validate_liquidity_sweep_pattern_context_policy_v1(policy_fixture())["rolling_extreme_lookback_bars"],48)
    def test_03_policy_direction_forbidden(self):
        p=policy_fixture(); p["directional_meaning_assigned"]=True
        with self.assertRaises(LiquiditySweepPatternContextError): validate_liquidity_sweep_pattern_context_policy_v1(p)
    def test_04_no_sweep(self):
        p=component()["payload"]; self.assertFalse(p["lower_side_price_sweep"]); self.assertFalse(p["upper_side_price_sweep"])
    def test_05_lower_sweep_reclaim(self):
        p=component((99.4,100.0,98.5,99.5,150.0))["payload"]; self.assertTrue(p["lower_side_sweep_reclaim_same_bar"])
    def test_06_lower_no_reclaim(self):
        p=component((99.0,99.5,98.5,98.8,150.0))["payload"]; self.assertTrue(p["lower_side_price_sweep"]); self.assertFalse(p["lower_side_sweep_reclaim_same_bar"])
    def test_07_upper_sweep_rejection(self):
        p=component((100.6,101.5,100.0,100.5,150.0))["payload"]; self.assertTrue(p["upper_side_sweep_rejection_same_bar"])
    def test_08_upper_no_rejection(self):
        p=component((101.0,101.5,100.5,101.2,150.0))["payload"]; self.assertTrue(p["upper_side_price_sweep"]); self.assertFalse(p["upper_side_sweep_rejection_same_bar"])
    def test_09_two_sided(self): self.assertTrue(component((100.0,101.5,98.5,100.0,150.0))["payload"]["two_sided_sweep_same_bar"])
    def test_10_latest_excluded(self):
        p=component((100.0,110.0,90.0,100.0,150.0))["payload"]; self.assertEqual((p["rolling_low_48"],p["rolling_high_48"]),(99.0,101.0))
    def test_11_atr_positive(self): self.assertGreater(component()["payload"]["atr14"],0)
    def test_12_proxy_only(self):
        p=component()["payload"]; self.assertTrue(p["sweep_is_price_action_proxy_only"]); self.assertFalse(p["hidden_stop_orders_observed"]); self.assertFalse(p["liquidations_observed"])
    def test_13_no_direction_signal_score(self):
        p=component()["payload"]; self.assertFalse(p["directional_semantics"]); self.assertFalse(p["signal_semantics"]); self.assertFalse(p["composite_score_assigned"])
    def test_14_no_candidate_semantics(self):
        p=component()["payload"]; self.assertFalse(p["primary_candidate_semantics_reused"]); self.assertFalse(p["secondary_candidate_promoted"]); self.assertFalse(p["candidate_emitted"])
    def test_15_no_future_or_network(self):
        p=component()["payload"]; self.assertFalse(p["future_outcomes_used"]); self.assertFalse(p["market_data_acquired_by_producer"]); self.assertFalse(p["source_recaptured_by_producer"])
    def test_16_reference_mismatch(self):
        with self.assertRaises(LiquiditySweepPatternContextError): component(meta=metadata(close="2026-08-17T23:44:59.999000+00:00"))
    def test_17_capture_before_reference(self):
        with self.assertRaises(LiquiditySweepPatternContextError): component(meta=metadata(captured="2026-08-17T23:59:59+00:00"))
    def test_18_future_available_at_capture(self): self.assertEqual(component()["available_at_utc"],CAPTURED_AT)
    def test_19_old_floor(self):
        desc=descriptor("2026-08-10T23:45:00+00:00","2026-08-10T23:44:59.999000+00:00","2026-08-10T23:45:10+00:00"); meta=metadata("2026-08-10T23:45:05+00:00","2026-08-10T23:44:59.999000+00:00"); c=build_liquidity_sweep_pattern_context_v1_component(observation_descriptor=desc,capture_metadata=meta,candles=rows(close="2026-08-10T23:44:59.999000+00:00"),source_csv_sha256="a"*64,source_manifest_sha256="b"*64,policy=policy_fixture(),policy_sha256="c"*64,produced_at_utc="2026-08-17T00:00:01+00:00"); self.assertEqual(c["available_at_utc"],POLICY_EFFECTIVE); self.assertFalse(validate_component_against_level_a_pack_v1(observation_descriptor=desc,component=c)["point_in_time_eligible"])
    def test_20_pack_eligible_future(self): self.assertTrue(validate_component_against_level_a_pack_v1(observation_descriptor=descriptor(),component=component())["point_in_time_eligible"])
    def _desc_file(self):
        p=self.external/"descriptor.json"; p.write_text(json.dumps(descriptor(),sort_keys=True)+"\n"); return p
    def _capture(self,name="capture",latest=(100.0,100.5,99.2,100.0,150.0)):
        d=self.external/name; d.mkdir(); data=rows(latest); csvp=d/"btc_usdt_15m_closed_candles.csv"
        with csvp.open("w",newline="",encoding="utf-8") as f:
            w=csv.DictWriter(f,fieldnames=["open_time_utc","close_time_utc","symbol","timeframe","open","high","low","close","volume","candle_closed"],lineterminator="\n"); w.writeheader()
            for r in data:w.writerow({"open_time_utc":r["open_time"].isoformat(),"close_time_utc":r["close_time"].isoformat(),"symbol":"BTCUSDT","timeframe":"15m","open":r["open"],"high":r["high"],"low":r["low"],"close":r["close"],"volume":r["volume"],"candle_closed":"True"})
        sha=hashlib.sha256(csvp.read_bytes()).hexdigest(); m=metadata(sha=sha); mp=d/"capture_metadata.json"; mp.write_text(json.dumps(m,sort_keys=True,separators=(",",":"))+"\n"); lines=[]
        for fn in ("btc_usdt_15m_closed_candles.csv","capture_metadata.json"): lines.append(f"{hashlib.sha256((d/fn).read_bytes()).hexdigest()}  {fn}")
        (d/"manifest.sha256").write_text("\n".join(sorted(lines))+"\n"); return d
    def test_21_package_missing_auth(self):
        with self.assertRaises(LiquiditySweepPatternContextError): prepare_liquidity_sweep_pattern_context_v1_package(repo_root=self.repo,observation_descriptor_json=self._desc_file(),closed_candle_capture_directory=self._capture("a"),output_directory=self.external/"outa",produced_at_utc="2026-08-18T00:00:06+00:00")
    def test_22_package_inside_repo(self):
        with self.assertRaises(LiquiditySweepPatternContextError): prepare_liquidity_sweep_pattern_context_v1_package(repo_root=self.repo,observation_descriptor_json=self._desc_file(),closed_candle_capture_directory=self._capture("b"),output_directory=self.repo/"out",produced_at_utc="2026-08-18T00:00:06+00:00",authorization=PACKAGE_AUTHORIZATION)
    def test_23_gate(self):
        os.environ["TRADING_AI_OFFICIAL_LONG_EVIDENCE_APPEND_ALLOWED"]="1"
        with self.assertRaises(LiquiditySweepPatternContextError): prepare_liquidity_sweep_pattern_context_v1_package(repo_root=self.repo,observation_descriptor_json=self._desc_file(),closed_candle_capture_directory=self._capture("c"),output_directory=self.external/"outc",produced_at_utc="2026-08-18T00:00:06+00:00",authorization=PACKAGE_AUTHORIZATION)
    def test_24_roundtrip(self):
        out=self.external/"round"; result=prepare_liquidity_sweep_pattern_context_v1_package(repo_root=self.repo,observation_descriptor_json=self._desc_file(),closed_candle_capture_directory=self._capture("d",(99.4,100.0,98.5,99.5,150.0)),output_directory=out,produced_at_utc="2026-08-18T00:00:06+00:00",authorization=PACKAGE_AUTHORIZATION); self.assertEqual(result["component_status"],"AVAILABLE"); self.assertTrue(validate_liquidity_sweep_pattern_context_v1_package(out)["point_in_time_eligible_under_pack_policy"])
    def test_25_tamper(self):
        out=self.external/"tamper"; prepare_liquidity_sweep_pattern_context_v1_package(repo_root=self.repo,observation_descriptor_json=self._desc_file(),closed_candle_capture_directory=self._capture("e"),output_directory=out,produced_at_utc="2026-08-18T00:00:06+00:00",authorization=PACKAGE_AUTHORIZATION); (out/"liquidity_sweep_pattern_context_component.json").write_text("{}\n")
        with self.assertRaises(LiquiditySweepPatternContextError): validate_liquidity_sweep_pattern_context_v1_package(out)
    def test_26_official_unchanged(self):
        ds=self.repo/"data"/"forward"/"long_forward_observation_dataset_v1.csv"; mf=self.repo/"data"/"forward"/"long_forward_observation_dataset_v1.manifest.csv"; before=(ds.read_bytes(),mf.read_bytes()); prepare_liquidity_sweep_pattern_context_v1_package(repo_root=self.repo,observation_descriptor_json=self._desc_file(),closed_candle_capture_directory=self._capture("f"),output_directory=self.external/"outf",produced_at_utc="2026-08-18T00:00:06+00:00",authorization=PACKAGE_AUTHORIZATION); self.assertEqual(before,(ds.read_bytes(),mf.read_bytes()))
    def test_27_source_unchanged(self):
        src=self._capture("g"); before={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in src.iterdir()}; prepare_liquidity_sweep_pattern_context_v1_package(repo_root=self.repo,observation_descriptor_json=self._desc_file(),closed_candle_capture_directory=src,output_directory=self.external/"outg",produced_at_utc="2026-08-18T00:00:06+00:00",authorization=PACKAGE_AUTHORIZATION); self.assertEqual(before,{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in src.iterdir()})
    def test_28_load_policy_sha(self): self.assertEqual(len(load_liquidity_sweep_pattern_context_policy_v1(self.repo)[1]),64)

if __name__ == "__main__": unittest.main(verbosity=2)
