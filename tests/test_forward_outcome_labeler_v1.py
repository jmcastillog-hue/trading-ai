from __future__ import annotations

import csv
import hashlib
import json
import os
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from src.long_side.forward_outcome_labeler_v1 import (
    CAPABILITY,
    CONTEXT_ANCHOR_POLICY,
    FORWARD_HORIZONS_BARS,
    FUTURE_SOURCE_COLUMNS,
    IMPLEMENTATION_OR_REPAIR_ATTEMPT,
    MAX_IMPLEMENTATION_OR_REPAIR_ATTEMPTS,
    OBSERVATION_DESCRIPTOR_SCHEMA_VERSION,
    PACKAGE_AUTHORIZATION,
    PRIMARY_ANCHOR_POLICY,
    TARGET_STOP_SAME_BAR_POLICY,
    ForwardOutcomeLabelerError,
    build_observation_descriptor_from_synchronized_session,
    label_forward_outcomes,
    prepare_forward_outcome_label_package,
    read_future_closed_candles,
    validate_forward_outcome_label_package,
)

UTC = timezone.utc


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_manifest(root: Path, names: list[str]) -> None:
    (root / "manifest.sha256").write_text(
        "\n".join(f"{sha(root / name)}  {name}" for name in sorted(names)) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def candle(open_dt: datetime, o: float, h: float, l: float, c: float) -> dict[str, object]:
    close_dt = open_dt + timedelta(minutes=15) - timedelta(milliseconds=1)
    return {
        "open_time_utc": open_dt.isoformat(),
        "close_time_utc": close_dt.isoformat(),
        "symbol": "BTCUSDT",
        "timeframe": "15m",
        "open": o,
        "high": h,
        "low": l,
        "close": c,
        "volume": 1.0,
        "candle_closed": True,
    }


def descriptor(*, candidate: bool = False, context_at: str = "2026-08-10T23:45:12+00:00") -> dict[str, object]:
    return {
        "observation_descriptor_schema_version": OBSERVATION_DESCRIPTOR_SCHEMA_VERSION,
        "observation_id": "OBS_TEST",
        "source_session_capability": "SYNCHRONIZED_15M_OBSERVATION_V1_1",
        "source_session_directory": "/tmp/session",
        "source_session_summary_sha256": "0" * 64,
        "source_session_events_sha256": "1" * 64,
        "cycle_index": 1,
        "symbol": "BTCUSDT",
        "timeframe": "15m",
        "reference_closed_candle_utc": "2026-08-10T23:44:59.999000+00:00",
        "reference_boundary_utc": "2026-08-10T23:45:00+00:00",
        "reference_price": 100.0,
        "primary_candidate_detected": candidate,
        "primary_entry_price": 100.0,
        "primary_stop_price": 95.0 if candidate else None,
        "primary_target_price": 110.0 if candidate else None,
        "synchronized_context_available_at_utc": context_at,
        "synchronized_context_anchor_policy": CONTEXT_ANCHOR_POLICY,
        "primary_anchor_policy": PRIMARY_ANCHOR_POLICY,
        "point_in_time_context_is_not_historical_reconstruction": True,
    }


def future_rows(count: int = 18, *, first_open: datetime | None = None) -> list[dict[str, object]]:
    start = first_open or datetime(2026, 8, 10, 23, 45, tzinfo=UTC)
    rows = []
    for i in range(count):
        base = 100.0 + i
        rows.append(candle(start + timedelta(minutes=15 * i), base, base + 2.0, base - 1.0, base + 1.0))
    return rows


def write_future_csv(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FUTURE_SOURCE_COLUMNS, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def build_synthetic_environment(root: Path, *, candidate_detected: bool = False) -> tuple[Path, Path, Path]:
    repo = root / "repo"
    repo.mkdir()
    (repo / ".git").mkdir()
    official = repo / "data/forward"
    official.mkdir(parents=True)
    (official / "long_forward_observation_dataset_v1.csv").write_text("a,b\n", encoding="utf-8")
    (official / "long_forward_observation_dataset_v1.manifest.csv").write_text("x,y\n", encoding="utf-8")

    session = root / "session"
    session.mkdir()
    micro = root / "micro"
    micro.mkdir()
    micro_summary = {
        "capability": "PUBLIC_READ_ONLY_MICROSTRUCTURE_SNAPSHOT_V1_1",
        "reference_closed_candle_utc": "2026-08-10T23:44:59.999000+00:00",
        "captured_finished_at_utc": "2026-08-10T23:45:12+00:00",
    }
    (micro / "microstructure_snapshot.json").write_text(json.dumps(micro_summary) + "\n", encoding="utf-8")
    (micro / "raw_responses.json").write_text("{}\n", encoding="utf-8")
    (micro / "request_log.json").write_text("{}\n", encoding="utf-8")
    write_manifest(micro, ["microstructure_snapshot.json", "raw_responses.json", "request_log.json"])

    review = session / "reviews/cycle_0001"
    review.mkdir(parents=True)
    columns = [
        "observation_id","observed_at_utc","source_system","source_capture_id","source_artifact","source_artifact_sha256","source_row_hash","candidate_id","direction","symbol","timeframe","entry_price","stop_price","target_price","invalidation_level","risk_reward","rolling_low_48","atr14","failed_breakdown","reclaim_confirmed","bullish_confirmation","candidate_detected","review_status","manual_confirmation_required","manual_confirmed","official_dataset_write_allowed","evidence_persistence_allowed","signal_generation_enabled","live_alerts_allowed","paper_trade_execution_allowed","real_capital_allowed","market_execution_allowed","exchange_execution_allowed","automation_allowed","execution_allowed",
    ]
    with (review / "candidate_rows.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, lineterminator="\n")
        writer.writeheader()
        if candidate_detected:
            row = {key: "False" for key in columns}
            row.update({
                "observation_id": "LONGOBS_TEST",
                "observed_at_utc": "2026-08-10T23:44:59.999000+00:00",
                "source_system": "BINANCE_PUBLIC_SPOT_API",
                "source_capture_id": "CAP",
                "source_artifact": "x",
                "source_artifact_sha256": "0" * 64,
                "source_row_hash": "1" * 64,
                "candidate_id": "LONG_BASE_FAILED_BREAKDOWN_V1",
                "direction": "LONG",
                "symbol": "BTCUSDT",
                "timeframe": "15m",
                "entry_price": "100",
                "stop_price": "95",
                "target_price": "110",
                "invalidation_level": "95",
                "risk_reward": "2.5",
                "rolling_low_48": "97",
                "atr14": "2",
                "failed_breakdown": "True",
                "reclaim_confirmed": "True",
                "bullish_confirmation": "True",
                "candidate_detected": "True",
                "review_status": "PENDING_HUMAN_REVIEW",
                "manual_confirmation_required": "True",
                "manual_confirmed": "False",
            })
            writer.writerow(row)

    event = {
        "event": "CYCLE_COMPLETED",
        "cycle_index": 1,
        "review_package_id": "REVIEW_TEST",
        "microstructure_output_directory": str(micro),
        "latest_spot_candle": {
            "close_time_utc": "2026-08-10T23:44:59.999000+00:00",
            "close": 100.0,
        },
        "primary_evaluation": {
            "failed_breakdown": candidate_detected,
            "reclaim_confirmed": True,
            "bullish_confirmation": candidate_detected,
            "candidate_detected": candidate_detected,
        },
        "candidate_detected": candidate_detected,
        "synchronization": {
            "closed_candle_match": True,
            "spot_latest_closed_candle_utc": "2026-08-10T23:44:59.999000+00:00",
            "futures_reference_closed_candle_utc": "2026-08-10T23:44:59.999000+00:00",
        },
    }
    (session / "session_events.jsonl").write_text(json.dumps(event) + "\n", encoding="utf-8")
    (session / "session_summary.json").write_text(
        json.dumps({"capability": "SYNCHRONIZED_15M_OBSERVATION_V1_1"}) + "\n",
        encoding="utf-8",
    )
    write_manifest(session, ["session_events.jsonl", "session_summary.json"])

    future = root / "future.csv"
    write_future_csv(future, future_rows())
    return repo, session, future


class Tests(unittest.TestCase):
    def test_01_capability(self): self.assertEqual(CAPABILITY, "FORWARD_OUTCOME_LABELER_V1")
    def test_02_attempt(self): self.assertEqual(IMPLEMENTATION_OR_REPAIR_ATTEMPT, 1)
    def test_03_limit(self): self.assertEqual(MAX_IMPLEMENTATION_OR_REPAIR_ATTEMPTS, 10)
    def test_04_horizons(self): self.assertEqual(FORWARD_HORIZONS_BARS, (1,2,4,8,16))
    def test_05_auth_token(self): self.assertEqual(PACKAGE_AUTHORIZATION, "PREPARE_FORWARD_OUTCOME_LABEL_PACKAGE_V1")
    def test_06_primary_anchor(self):
        out = label_forward_outcomes(observation_descriptor=descriptor(), future_closed_candles=future_rows())
        self.assertEqual(out["primary_rule_outcome"]["anchor_open_time_utc"], "2026-08-10T23:45:00+00:00")
    def test_07_context_anchor_skips_partial(self):
        out = label_forward_outcomes(observation_descriptor=descriptor(), future_closed_candles=future_rows())
        self.assertEqual(out["synchronized_context_outcome"]["anchor_open_time_utc"], "2026-08-11T00:00:00+00:00")
        self.assertFalse(out["synchronized_context_outcome"]["partially_elapsed_bar_allowed"])
    def test_08_context_exact_boundary(self):
        out = label_forward_outcomes(observation_descriptor=descriptor(context_at="2026-08-10T23:45:00+00:00"), future_closed_candles=future_rows())
        self.assertEqual(out["synchronized_context_outcome"]["anchor_open_time_utc"], "2026-08-10T23:45:00+00:00")
    def test_09_forward_return(self):
        out = label_forward_outcomes(observation_descriptor=descriptor(), future_closed_candles=future_rows())
        self.assertAlmostEqual(out["primary_rule_outcome"]["labels"]["1"]["forward_return"], 0.01)
    def test_10_mfe(self):
        out = label_forward_outcomes(observation_descriptor=descriptor(), future_closed_candles=future_rows())
        self.assertAlmostEqual(out["primary_rule_outcome"]["labels"]["1"]["mfe_return"], 0.02)
    def test_11_mae(self):
        out = label_forward_outcomes(observation_descriptor=descriptor(), future_closed_candles=future_rows())
        self.assertAlmostEqual(out["primary_rule_outcome"]["labels"]["1"]["mae_return"], -0.01)
    def test_12_pending_maturity(self):
        out = label_forward_outcomes(observation_descriptor=descriptor(), future_closed_candles=future_rows(3))
        self.assertEqual(out["primary_rule_outcome"]["labels"]["4"]["label_status"], "PENDING")
        self.assertEqual(out["primary_rule_outcome"]["labels"]["2"]["label_status"], "AVAILABLE")
    def test_13_noncandidate_ordering(self):
        out = label_forward_outcomes(observation_descriptor=descriptor(), future_closed_candles=future_rows())
        self.assertEqual(out["primary_rule_outcome"]["labels"]["1"]["target_stop_ordering"], "NOT_APPLICABLE")
    def test_14_target_first(self):
        rows = future_rows(); rows[0].update({"high": 111.0, "low": 99.0})
        out = label_forward_outcomes(observation_descriptor=descriptor(candidate=True), future_closed_candles=rows)
        self.assertEqual(out["primary_rule_outcome"]["labels"]["1"]["target_stop_ordering"], "TARGET_FIRST")
    def test_15_stop_first(self):
        rows = future_rows(); rows[0].update({"high": 104.0, "low": 94.0})
        out = label_forward_outcomes(observation_descriptor=descriptor(candidate=True), future_closed_candles=rows)
        self.assertEqual(out["primary_rule_outcome"]["labels"]["1"]["target_stop_ordering"], "STOP_FIRST")
    def test_16_same_bar_ambiguous(self):
        rows = future_rows(); rows[0].update({"high": 111.0, "low": 94.0})
        out = label_forward_outcomes(observation_descriptor=descriptor(candidate=True), future_closed_candles=rows)
        self.assertEqual(out["primary_rule_outcome"]["labels"]["1"]["target_stop_ordering"], "AMBIGUOUS_SAME_BAR")
        self.assertFalse(out["intrabar_order_inferred"])
    def test_17_neither(self):
        rows = future_rows(); rows[0].update({"high": 104.0, "low": 96.0})
        out = label_forward_outcomes(observation_descriptor=descriptor(candidate=True), future_closed_candles=rows)
        self.assertEqual(out["primary_rule_outcome"]["labels"]["1"]["target_stop_ordering"], "NEITHER_WITHIN_HORIZON")
    def test_18_target_policy_literal(self): self.assertEqual(TARGET_STOP_SAME_BAR_POLICY, "AMBIGUOUS_SAME_BAR_NO_INTRABAR_ORDER_INFERENCE")
    def test_19_nonclosed_rejected(self):
        rows = future_rows(); rows[0]["candle_closed"] = False
        with self.assertRaises(ForwardOutcomeLabelerError): label_forward_outcomes(observation_descriptor=descriptor(), future_closed_candles=rows)
    def test_20_wrong_symbol_rejected(self):
        rows = future_rows(); rows[0]["symbol"] = "ETHUSDT"
        with self.assertRaises(ForwardOutcomeLabelerError): label_forward_outcomes(observation_descriptor=descriptor(), future_closed_candles=rows)
    def test_21_wrong_timeframe_rejected(self):
        rows = future_rows(); rows[0]["timeframe"] = "5m"
        with self.assertRaises(ForwardOutcomeLabelerError): label_forward_outcomes(observation_descriptor=descriptor(), future_closed_candles=rows)
    def test_22_bad_ohlc_rejected(self):
        rows = future_rows(); rows[0]["low"] = 105.0
        with self.assertRaises(ForwardOutcomeLabelerError): label_forward_outcomes(observation_descriptor=descriptor(), future_closed_candles=rows)
    def test_23_gap_rejected(self):
        rows = future_rows(); del rows[3]
        with self.assertRaises(ForwardOutcomeLabelerError): label_forward_outcomes(observation_descriptor=descriptor(), future_closed_candles=rows)
    def test_24_reference_boundary_rejected(self):
        d = descriptor(); d["reference_boundary_utc"] = "2026-08-10T23:45:00.001000+00:00"
        with self.assertRaises(ForwardOutcomeLabelerError): label_forward_outcomes(observation_descriptor=d, future_closed_candles=future_rows())
    def test_25_context_before_reference_rejected(self):
        d = descriptor(context_at="2026-08-10T23:44:59+00:00")
        with self.assertRaises(ForwardOutcomeLabelerError): label_forward_outcomes(observation_descriptor=d, future_closed_candles=future_rows())
    def test_26_candidate_geometry_required(self):
        d = descriptor(candidate=True); d["primary_stop_price"] = None
        with self.assertRaises(ForwardOutcomeLabelerError): label_forward_outcomes(observation_descriptor=d, future_closed_candles=future_rows())
    def test_27_noncandidate_geometry_forbidden(self):
        d = descriptor(); d["primary_stop_price"] = 95.0
        with self.assertRaises(ForwardOutcomeLabelerError): label_forward_outcomes(observation_descriptor=d, future_closed_candles=future_rows())
    def test_28_source_starts_after_anchor_rejected(self):
        rows = future_rows(first_open=datetime(2026,8,11,0,0,tzinfo=UTC))
        with self.assertRaises(ForwardOutcomeLabelerError): label_forward_outcomes(observation_descriptor=descriptor(), future_closed_candles=rows)
    def test_29_context_pending_when_anchor_not_mature(self):
        out = label_forward_outcomes(observation_descriptor=descriptor(), future_closed_candles=future_rows(1))
        self.assertEqual(out["synchronized_context_outcome"]["labels"]["1"]["label_status"], "PENDING")
    def test_30_build_descriptor_noncandidate(self):
        with tempfile.TemporaryDirectory() as td:
            _, session, _ = build_synthetic_environment(Path(td), candidate_detected=False)
            d = build_observation_descriptor_from_synchronized_session(synchronized_session_directory=session, cycle_index=1)
            self.assertFalse(d["primary_candidate_detected"])
            self.assertEqual(d["synchronized_context_available_at_utc"], "2026-08-10T23:45:12+00:00")
    def test_31_build_descriptor_candidate_geometry(self):
        with tempfile.TemporaryDirectory() as td:
            _, session, _ = build_synthetic_environment(Path(td), candidate_detected=True)
            d = build_observation_descriptor_from_synchronized_session(synchronized_session_directory=session, cycle_index=1)
            self.assertTrue(d["primary_candidate_detected"])
            self.assertEqual(d["primary_stop_price"], 95.0)
            self.assertEqual(d["primary_target_price"], 110.0)
    def test_32_package_auth_required(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); repo, session, future = build_synthetic_environment(root)
            with self.assertRaises(ForwardOutcomeLabelerError):
                prepare_forward_outcome_label_package(repo_root=repo, synchronized_session_directory=session, cycle_index=1, future_closed_candles_csv=future, output_directory=root/"out")
    def test_33_package_roundtrip(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); repo, session, future = build_synthetic_environment(root); out = root/"out"
            result = prepare_forward_outcome_label_package(repo_root=repo, synchronized_session_directory=session, cycle_index=1, future_closed_candles_csv=future, output_directory=out, authorization=PACKAGE_AUTHORIZATION)
            self.assertEqual(result["available_primary_horizons"], 5)
            self.assertEqual(result["available_context_horizons"], 5)
            self.assertEqual(validate_forward_outcome_label_package(out)["manifest_entries"], 3)
    def test_34_official_unchanged(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); repo, session, future = build_synthetic_environment(root); out = root/"out"
            ds = repo/"data/forward/long_forward_observation_dataset_v1.csv"; mf = repo/"data/forward/long_forward_observation_dataset_v1.manifest.csv"
            before = (sha(ds), sha(mf))
            prepare_forward_outcome_label_package(repo_root=repo, synchronized_session_directory=session, cycle_index=1, future_closed_candles_csv=future, output_directory=out, authorization=PACKAGE_AUTHORIZATION)
            self.assertEqual(before, (sha(ds), sha(mf)))
    def test_35_read_future_csv(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td)/"future.csv"; write_future_csv(p, future_rows(2)); rows = read_future_closed_candles(p)
            self.assertEqual(len(rows), 2)


if __name__ == "__main__":
    unittest.main(verbosity=2)
