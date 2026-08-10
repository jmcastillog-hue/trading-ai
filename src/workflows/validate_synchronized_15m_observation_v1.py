from __future__ import annotations

import ast
import csv
import hashlib
import json
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

from src.long_side.synchronized_15m_observation_v1 import (
    DEPTH_BANDS_BPS,
    EXPECTED_MICROSTRUCTURE_REQUESTS_PER_CYCLE,
    EXPECTED_NETWORK_REQUESTS_PER_CYCLE,
    EXPECTED_SPOT_REQUESTS_PER_CYCLE,
    MAX_IMPLEMENTATION_OR_REPAIR_ATTEMPTS,
    MICROSTRUCTURE_DEPTH_LIMIT,
    REAL_SOURCE_ATTESTATION,
    REQUIRED_DEPTH_BANDS_BPS,
    SESSION_AUTHORIZATION,
    run_bounded_synchronized_15m_session,
    validate_synchronized_observation_session,
)

FALSE_SPOT = {
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

FALSE_MICRO = {
    "api_key_used": False,
    "authenticated_endpoint_used": False,
    "websocket_used": False,
    "background_execution": False,
    "scheduler_installed": False,
    "directional_recommendation_generated": False,
    "signal_generation_enabled": False,
    "live_alerts_allowed": False,
    "paper_trade_execution_allowed": False,
    "real_capital_allowed": False,
    "market_execution_allowed": False,
    "exchange_execution_allowed": False,
    "official_append_allowed": False,
    "official_dataset_write_performed": False,
    "official_manifest_write_performed": False,
    "automation_allowed": False,
    "execution_allowed": False,
}


class Clock:
    def __init__(self):
        self.value = datetime(2026, 8, 10, 13, 47, tzinfo=timezone.utc)

    def __call__(self):
        return self.value

    def sleep(self, seconds):
        self.value += timedelta(seconds=seconds)


def main() -> int:
    checks: list[dict[str, object]] = []

    def add(name: str, passed: bool, details: object) -> None:
        checks.append(
            {
                "check": name,
                "passed": bool(passed),
                "details": details,
                "blocker": not bool(passed),
            }
        )

    source_path = Path("src/long_side/synchronized_15m_observation_v1.py")
    source = source_path.read_text(encoding="utf-8")
    tree = ast.parse(source)
    imports: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.add(node.module)

    add("repair_attempt_limit_10", MAX_IMPLEMENTATION_OR_REPAIR_ATTEMPTS == 10, MAX_IMPLEMENTATION_OR_REPAIR_ATTEMPTS)
    add("exact_spot_request_contract", EXPECTED_SPOT_REQUESTS_PER_CYCLE == 1, EXPECTED_SPOT_REQUESTS_PER_CYCLE)
    add("exact_micro_request_contract", EXPECTED_MICROSTRUCTURE_REQUESTS_PER_CYCLE == 7, EXPECTED_MICROSTRUCTURE_REQUESTS_PER_CYCLE)
    add("exact_total_request_contract", EXPECTED_NETWORK_REQUESTS_PER_CYCLE == 8, EXPECTED_NETWORK_REQUESTS_PER_CYCLE)
    add("microstructure_depth_1000", MICROSTRUCTURE_DEPTH_LIMIT == 1000, MICROSTRUCTURE_DEPTH_LIMIT)
    add("depth_bands_frozen", tuple(DEPTH_BANDS_BPS) == (5, 10, 25, 50), list(DEPTH_BANDS_BPS))
    add("required_depth_bands_frozen", tuple(REQUIRED_DEPTH_BANDS_BPS) == (5, 10), list(REQUIRED_DEPTH_BANDS_BPS))
    add("no_thread_process_runtime", not any(x.startswith(("threading", "multiprocessing", "subprocess")) for x in imports), sorted(imports))
    add("no_scheduler_dependency", not any(x.startswith(("schedule", "apscheduler")) for x in imports), sorted(imports))
    add("no_direct_http_client", not any(x.startswith(("requests", "urllib", "httpx", "aiohttp")) for x in imports), "delegated capture boundaries")
    add("no_messaging_browser_strings", all(x not in source.lower() for x in ("whatsapp", "telegram", "selenium", "playwright", "quantfury")), "none")
    add("official_writer_absent", "append_official_prospective_evidence" not in source, "absent")
    add("spot_capture_dependency_present", "long_primary_public_closed_candle_capture_v1" in source, "present")
    add("primary_adapter_dependency_present", "long_primary_prospective_observation_source_adapter_v1" in source, "present")
    add("microstructure_v1_1_dependency_present", "public_read_only_microstructure_snapshot_v1_1" in source, "present")
    add("legacy_loop_context_dependency_present", "long_supervised_15m_observation_loop_v2" in source, "present")
    add("strict_candle_match_present", "SPOT_FUTURES_CANDLE_MISMATCH" in source and "closed_candle_match" in source, "present")
    add("incomplete_depth_not_extrapolated", "notional_imbalance_usable" in source and "incomplete_depth_extrapolation_allowed" in source, "present")
    add("microstructure_cannot_create_candidate", '"microstructure_can_create_candidate": False' in source, "false")
    add("microstructure_cannot_cancel_candidate", '"microstructure_can_cancel_candidate": False' in source, "false")
    add("stop_on_primary_candidate", "FIRST_PRIMARY_CANDIDATE_PENDING_HUMAN_REVIEW" in source, "present")

    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        repo = root / "repo"
        repo.mkdir()
        (repo / ".git").mkdir()
        d = repo / "data/forward"
        d.mkdir(parents=True)
        (d / "long_forward_observation_dataset_v1.csv").write_text("x\n", encoding="utf-8")
        (d / "long_forward_observation_dataset_v1.manifest.csv").write_text("y\n", encoding="utf-8")
        external = root / "external"
        external.mkdir()
        clock = Clock()
        spot_count = 0
        micro_count = 0
        package_count = 0

        def close_for(index: int) -> datetime:
            return datetime(2026, 8, 10, 13, 59, 59, 999000, tzinfo=timezone.utc) + timedelta(minutes=15 * (index - 1))

        def spot_capture(**kwargs):
            nonlocal spot_count
            spot_count += 1
            out = Path(kwargs["output_directory"])
            out.mkdir()
            source_csv = out / "btc_usdt_15m_closed_candles.csv"
            metadata = out / "capture_metadata.json"
            close = close_for(spot_count)
            fields = ["open_time_utc", "close_time_utc", "symbol", "timeframe", "open", "high", "low", "close", "volume", "candle_closed"]
            rows = []
            start = close - timedelta(minutes=15 * 62 + 14, seconds=59.999)
            for i in range(63):
                ot = start + timedelta(minutes=15 * i)
                ct = ot + timedelta(minutes=14, seconds=59.999)
                p = 65000 + i
                rows.append(
                    {
                        "open_time_utc": ot.isoformat(),
                        "close_time_utc": ct.isoformat(),
                        "symbol": "BTCUSDT",
                        "timeframe": "15m",
                        "open": str(p),
                        "high": str(p + 20),
                        "low": str(p - 20),
                        "close": str(p + 5),
                        "volume": "100",
                        "candle_closed": "True",
                    }
                )
            with source_csv.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=fields)
                writer.writeheader()
                writer.writerows(rows)
            metadata.write_text(json.dumps({"captured_at_utc": (close + timedelta(seconds=5)).isoformat()}), encoding="utf-8")
            sha = hashlib.sha256(source_csv.read_bytes()).hexdigest()
            return {
                "capture_id": f"SPOT_{spot_count}",
                "source_csv": str(source_csv),
                "metadata_json": str(metadata),
                "latest_closed_candle_utc": rows[-1]["close_time_utc"],
                "source_artifact_sha256": sha,
                "network_request_count": 1,
                "one_shot_foreground": True,
                **FALSE_SPOT,
            }

        def package(**kwargs):
            nonlocal package_count
            package_count += 1
            out = Path(kwargs["output_directory"])
            out.mkdir()
            (out / "adapter_checks.json").write_text(
                json.dumps(
                    {
                        "failed_breakdown": False,
                        "reclaim_confirmed": True,
                        "bullish_confirmation": True,
                        "candidate_detected": False,
                    }
                ),
                encoding="utf-8",
            )
            return {
                "package_id": f"PKG_{package_count}",
                "source_artifact_sha256": kwargs["expected_source_sha256"],
                "latest_closed_candle_utc": kwargs["prospective_start_utc"],
                "candidate_detected": False,
                "eligible_for_real_human_review": False,
                **FALSE_PACKAGE,
            }

        def micro_capture(**kwargs):
            nonlocal micro_count
            micro_count += 1
            out = Path(kwargs["output_directory"])
            out.mkdir()
            close = close_for(micro_count)
            bands = {}
            coverage = {"5": True, "10": True, "25": False, "50": False}
            for key, bps in zip(("5", "10", "25", "50"), (5, 10, 25, 50)):
                bands[key] = {
                    "band_bps": bps,
                    "bid_level_count": 100 + bps,
                    "ask_level_count": 110 + bps,
                    "bid_qty_base": 10.0,
                    "ask_qty_base": 11.0,
                    "bid_notional_usdt": 1000000.0 + bps,
                    "ask_notional_usdt": 1100000.0 + bps,
                    "notional_imbalance": -0.047,
                    "coverage_complete": coverage[key],
                }
            summary = {
                "snapshot_schema_version": "PUBLIC_READ_ONLY_MICROSTRUCTURE_SNAPSHOT_V1_1",
                "capability": "PUBLIC_READ_ONLY_MICROSTRUCTURE_SNAPSHOT_V1_1",
                "implementation_schema_version": "PUBLIC_READ_ONLY_MICROSTRUCTURE_SNAPSHOT_IMPLEMENTATION_V1_1",
                "provider": "BINANCE_USDM_PUBLIC_REST",
                "symbol": "BTCUSDT",
                "timeframe": "15m",
                "reference_closed_candle_utc": close.isoformat(),
                "request_count": 7,
                "depth_limit_requested": 1000,
                "depth_bands_bps": [5, 10, 25, 50],
                "order_book": {
                    "returned_bid_levels": 1000,
                    "returned_ask_levels": 1000,
                    "best_bid": 65100.0,
                    "best_ask": 65100.1,
                    "mid_price": 65100.05,
                    "spread_bps": 0.015,
                    "furthest_bid_distance_bps": 20.0,
                    "furthest_ask_distance_bps": 19.0,
                    "bands": bands,
                },
                "open_interest": {"change_15m_percent": 0.01},
                "mark_price_funding": {"last_funding_rate": 0.00005},
                "taker_buy_sell_volume": {"latest_15m": {"buy_sell_ratio": 1.2}},
                "global_long_short_account_ratio": {"latest_15m": {"long_short_account_ratio": 1.1}},
                "synchronization": {"reference_boundary_utc": (close + timedelta(milliseconds=1)).isoformat()},
                "interpretation_constraints": {"context_only": True, "does_not_modify_frozen_long_rule": True, "depth_coverage_is_explicit_not_assumed": True},
                **FALSE_MICRO,
            }
            (out / "microstructure_snapshot.json").write_text(json.dumps(summary), encoding="utf-8")
            (out / "raw_responses.json").write_text("{}", encoding="utf-8")
            (out / "request_log.json").write_text("[]", encoding="utf-8")
            (out / "manifest.sha256").write_text("mock\n", encoding="utf-8")
            return {
                "capability": "PUBLIC_READ_ONLY_MICROSTRUCTURE_SNAPSHOT_V1_1",
                "output_directory": str(out),
                "request_count": 7,
                "depth_limit_requested": 1000,
                "depth_bands_bps": [5, 10, 25, 50],
                "reference_closed_candle_utc": close.isoformat(),
                "foreground_only": True,
                "public_read_only": True,
                **FALSE_MICRO,
            }

        def micro_validate(directory):
            summary = json.loads((Path(directory) / "microstructure_snapshot.json").read_text(encoding="utf-8"))
            return {
                "request_count": summary["request_count"],
                "depth_limit_requested": summary["depth_limit_requested"],
                "depth_bands_bps": summary["depth_bands_bps"],
            }

        def human_context(latest):
            return {"context_only": True, "actionable_signal_generated": False}

        before = (
            (d / "long_forward_observation_dataset_v1.csv").read_bytes(),
            (d / "long_forward_observation_dataset_v1.manifest.csv").read_bytes(),
        )

        result = run_bounded_synchronized_15m_session(
            repo_root=repo,
            output_directory=external / "session",
            max_cycles=2,
            source_attestation=REAL_SOURCE_ATTESTATION,
            minimum_latest_closed_candle_utc="2026-08-10T04:29:59.999000+00:00",
            authorization=SESSION_AUTHORIZATION,
            clock=clock,
            sleeper=clock.sleep,
            spot_capture_callable=spot_capture,
            package_callable=package,
            microstructure_capture_callable=micro_capture,
            microstructure_validate_callable=micro_validate,
            human_context_callable=human_context,
        )
        validation = validate_synchronized_observation_session(result["output_directory"])

        after = (
            (d / "long_forward_observation_dataset_v1.csv").read_bytes(),
            (d / "long_forward_observation_dataset_v1.manifest.csv").read_bytes(),
        )

        events = [
            json.loads(line)
            for line in (Path(result["output_directory"]) / "session_events.jsonl").read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        cycles = [event for event in events if event.get("event") == "CYCLE_COMPLETED"]

        add("mock_session_completed", result["completed_cycles"] == 2, result["completed_cycles"])
        add("mock_exact_request_total", result["network_request_count"] == 16, result["network_request_count"])
        add("mock_spot_capture_count", spot_count == 2, spot_count)
        add("mock_micro_capture_count", micro_count == 2, micro_count)
        add("mock_candle_match", all(x["synchronization"]["closed_candle_match"] for x in cycles), len(cycles))
        add("mock_required_depth_usable", all(x["microstructure_context"]["minimum_depth_context_usable"] for x in cycles), len(cycles))
        add("mock_incomplete_25_not_used", all(x["microstructure_context"]["bands"]["25"]["notional_imbalance_usable"] is None for x in cycles), len(cycles))
        add("mock_no_candidate", result["candidate_count"] == 0, result["candidate_count"])
        add("session_manifest_valid", validation["manifest_entries"] == 2, validation["manifest_entries"])
        add("official_artifacts_unchanged", before == after, "unchanged")
        add("notifications_disabled", result["external_notifications_sent"] is False, False)
        add("manual_confirmation_false", result["manual_confirmed"] is False, False)
        add("bounded_foreground", result["bounded"] is True and result["foreground_only"] is True, True)

    failed = [item for item in checks if not item["passed"]]
    payload = {
        "capability": "SYNCHRONIZED_15M_OBSERVATION_V1_VALIDATOR",
        "decision": "SYNCHRONIZED_15M_OBSERVATION_V1_VALIDATED_NO_REAL_NETWORK",
        "checks": len(checks),
        "failed_checks": len(failed),
        "blockers": sum(1 for item in failed if item["blocker"]),
        "mocked_cycles": 2,
        "mocked_network_requests": 16,
        "real_network_request_executed": False,
        "real_market_data_acquired": False,
        "real_session_executed": False,
        "external_notifications_sent": False,
        "official_append_executed": False,
        "check_results": checks,
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
