from __future__ import annotations

import ast
import json
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

from src.long_side.forward_outcome_labeler_v1 import (
    CAPABILITY,
    CONTEXT_ANCHOR_POLICY,
    FORWARD_HORIZONS_BARS,
    IMPLEMENTATION_OR_REPAIR_ATTEMPT,
    MAX_IMPLEMENTATION_OR_REPAIR_ATTEMPTS,
    PACKAGE_AUTHORIZATION,
    PRIMARY_ANCHOR_POLICY,
    TARGET_STOP_SAME_BAR_POLICY,
    label_forward_outcomes,
)

UTC = timezone.utc


def _candle(open_dt: datetime, o: float, h: float, l: float, c: float) -> dict[str, object]:
    return {
        "open_time_utc": open_dt.isoformat(),
        "close_time_utc": (open_dt + timedelta(minutes=15) - timedelta(milliseconds=1)).isoformat(),
        "symbol": "BTCUSDT",
        "timeframe": "15m",
        "open": o,
        "high": h,
        "low": l,
        "close": c,
        "volume": 1.0,
        "candle_closed": True,
    }


def _descriptor(candidate: bool = True) -> dict[str, object]:
    return {
        "observation_descriptor_schema_version": "FORWARD_OUTCOME_OBSERVATION_DESCRIPTOR_V1",
        "observation_id": "VALIDATOR_OBS",
        "source_session_capability": "SYNCHRONIZED_15M_OBSERVATION_V1_1",
        "source_session_directory": "/validator/session",
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
        "synchronized_context_available_at_utc": "2026-08-10T23:45:12+00:00",
        "synchronized_context_anchor_policy": CONTEXT_ANCHOR_POLICY,
        "primary_anchor_policy": PRIMARY_ANCHOR_POLICY,
        "point_in_time_context_is_not_historical_reconstruction": True,
    }


def _rows(count: int = 18) -> list[dict[str, object]]:
    start = datetime(2026, 8, 10, 23, 45, tzinfo=UTC)
    out = []
    for i in range(count):
        base = 100.0 + i
        out.append(_candle(start + timedelta(minutes=15 * i), base, base + 2, base - 1, base + 1))
    return out


def main() -> int:
    repo = Path.cwd()
    module_path = repo / "src/long_side/forward_outcome_labeler_v1.py"
    docs_path = repo / "docs/FORWARD_OUTCOME_LABELER_V1.md"
    manifest_path = repo / "FORWARD_OUTCOME_LABELER_V1_MANIFEST.sha256"
    source = module_path.read_text(encoding="utf-8")
    tree = ast.parse(source)
    imports = sorted({
        node.names[0].name if isinstance(node, ast.Import) else (node.module or "")
        for node in ast.walk(tree)
        if isinstance(node, (ast.Import, ast.ImportFrom))
    })

    checks: list[dict[str, object]] = []
    def add(name: str, passed: bool, details: object) -> None:
        checks.append({"check": name, "passed": bool(passed), "blocker": not bool(passed), "details": details})

    add("capability", CAPABILITY == "FORWARD_OUTCOME_LABELER_V1", CAPABILITY)
    add("implementation_attempt_1", IMPLEMENTATION_OR_REPAIR_ATTEMPT == 1, IMPLEMENTATION_OR_REPAIR_ATTEMPT)
    add("repair_limit_10", MAX_IMPLEMENTATION_OR_REPAIR_ATTEMPTS == 10, MAX_IMPLEMENTATION_OR_REPAIR_ATTEMPTS)
    add("horizons_frozen", FORWARD_HORIZONS_BARS == (1,2,4,8,16), list(FORWARD_HORIZONS_BARS))
    add("package_authorization_exact", PACKAGE_AUTHORIZATION == "PREPARE_FORWARD_OUTCOME_LABEL_PACKAGE_V1", PACKAGE_AUTHORIZATION)
    add("primary_anchor_policy", PRIMARY_ANCHOR_POLICY == "REFERENCE_BOUNDARY", PRIMARY_ANCHOR_POLICY)
    add("context_anchor_policy", CONTEXT_ANCHOR_POLICY == "FIRST_FULL_15M_BAR_OPEN_AT_OR_AFTER_CONTEXT_AVAILABILITY", CONTEXT_ANCHOR_POLICY)
    add("same_bar_policy", TARGET_STOP_SAME_BAR_POLICY == "AMBIGUOUS_SAME_BAR_NO_INTRABAR_ORDER_INFERENCE", TARGET_STOP_SAME_BAR_POLICY)
    add("no_requests_import", "requests" not in imports, imports)
    add("no_httpx_import", "httpx" not in imports, imports)
    add("no_websocket_import", all("websocket" not in x for x in imports), imports)
    add("no_threading_import", "threading" not in imports, imports)
    add("no_multiprocessing_import", "multiprocessing" not in imports, imports)
    add("no_scheduler_import", all(x not in imports for x in ("schedule","apscheduler")), imports)
    add("no_subprocess_import", "subprocess" not in imports, imports)
    add("official_writer_absent", "append_official_prospective_evidence" not in source, "absent")
    add("no_messaging_strings", all(x not in source.lower() for x in ("whatsapp", "telegram", "send_message")), "none")
    add("no_browser_strings", all(x not in source.lower() for x in ("selenium", "playwright", "tradingview")), "none")
    add("context_uses_capture_finished", "captured_finished_at_utc" in source, "present")
    add("context_skips_partial_bar", "partially_elapsed_bar_allowed\": False" in source, "present")
    add("maturity_explicit", '"label_status": "PENDING"' in source and '"label_status": "AVAILABLE"' in source, "present")
    add("intrabar_inference_disabled", '"intrabar_order_inferred": False' in source, "present")
    add("target_first_present", '"TARGET_FIRST"' in source, "present")
    add("stop_first_present", '"STOP_FIRST"' in source, "present")
    add("ambiguous_same_bar_present", '"AMBIGUOUS_SAME_BAR"' in source, "present")
    add("neither_present", '"NEITHER_WITHIN_HORIZON"' in source, "present")
    add("not_applicable_present", '"NOT_APPLICABLE"' in source, "present")
    add("future_closed_required", '"FUTURE_CANDLE_NOT_CLOSED"' in source, "present")
    add("future_gap_rejected", '"FUTURE_SOURCE_GAP"' in source, "present")
    add("future_anchor_gap_rejected", '"FUTURE_SOURCE_STARTS_AFTER_REQUIRED_ANCHOR"' in source, "present")
    add("candidate_long_geometry", 'stop_price < entry_price < target_price' in source, "present")

    rows = _rows()
    out = label_forward_outcomes(observation_descriptor=_descriptor(True), future_closed_candles=rows)
    add("mock_primary_anchor", out["primary_rule_outcome"]["anchor_open_time_utc"] == "2026-08-10T23:45:00+00:00", out["primary_rule_outcome"]["anchor_open_time_utc"])
    add("mock_context_anchor", out["synchronized_context_outcome"]["anchor_open_time_utc"] == "2026-08-11T00:00:00+00:00", out["synchronized_context_outcome"]["anchor_open_time_utc"])
    add("mock_primary_all_horizons_available", all(x["label_status"] == "AVAILABLE" for x in out["primary_rule_outcome"]["labels"].values()), out["primary_rule_outcome"]["labels"])
    add("mock_context_all_horizons_available", all(x["label_status"] == "AVAILABLE" for x in out["synchronized_context_outcome"]["labels"].values()), out["synchronized_context_outcome"]["labels"])
    add("mock_forward_return", abs(out["primary_rule_outcome"]["labels"]["1"]["forward_return"] - 0.01) < 1e-12, out["primary_rule_outcome"]["labels"]["1"]["forward_return"])
    add("mock_mfe", abs(out["primary_rule_outcome"]["labels"]["1"]["mfe_return"] - 0.02) < 1e-12, out["primary_rule_outcome"]["labels"]["1"]["mfe_return"])
    add("mock_mae", abs(out["primary_rule_outcome"]["labels"]["1"]["mae_return"] + 0.01) < 1e-12, out["primary_rule_outcome"]["labels"]["1"]["mae_return"])

    same = _rows()
    same[0]["high"] = 111.0
    same[0]["low"] = 94.0
    amb = label_forward_outcomes(observation_descriptor=_descriptor(True), future_closed_candles=same)
    add("mock_same_bar_ambiguous", amb["primary_rule_outcome"]["labels"]["1"]["target_stop_ordering"] == "AMBIGUOUS_SAME_BAR", amb["primary_rule_outcome"]["labels"]["1"]["target_stop_ordering"])
    add("mock_no_intrabar_inference", amb["intrabar_order_inferred"] is False, amb["intrabar_order_inferred"])

    partial = label_forward_outcomes(observation_descriptor=_descriptor(False), future_closed_candles=_rows(3))
    add("mock_pending_4_bar", partial["primary_rule_outcome"]["labels"]["4"]["label_status"] == "PENDING", partial["primary_rule_outcome"]["labels"]["4"])
    add("mock_noncandidate_not_applicable", partial["primary_rule_outcome"]["labels"]["1"]["target_stop_ordering"] == "NOT_APPLICABLE", partial["primary_rule_outcome"]["labels"]["1"]["target_stop_ordering"])
    add("mock_lookahead_false", out["lookahead_used"] is False, out["lookahead_used"])
    add("mock_context_partial_false", out["synchronized_context_outcome"]["partially_elapsed_bar_allowed"] is False, out["synchronized_context_outcome"]["partially_elapsed_bar_allowed"])
    add("mock_primary_partial_false", out["primary_rule_outcome"]["partially_elapsed_bar_allowed"] is False, out["primary_rule_outcome"]["partially_elapsed_bar_allowed"])

    docs = docs_path.read_text(encoding="utf-8")
    add("docs_two_clocks", "Two clocks, two anchors" in docs, "present")
    add("docs_forward_labeler_no_network", "zero network requests" in docs.lower(), "present")
    add("docs_context_next_full_bar", "first complete 15m bar open >= context_available_at" in docs, "present")
    add("docs_same_bar_ambiguity", "AMBIGUOUS_SAME_BAR" in docs, "present")
    add("docs_next_level_a", "Context Feature Pack V1" in docs, "present")

    lines = [line for line in manifest_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    add("source_manifest_entries_4", len(lines) == 4, len(lines))
    manifest_ok = True
    for line in lines:
        parts = line.split("  ", 1)
        if len(parts) != 2:
            manifest_ok = False
            break
        expected, rel = parts
        path = repo / rel
        if not path.is_file():
            manifest_ok = False
            break
        import hashlib
        if hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            manifest_ok = False
            break
    add("source_manifest_valid", manifest_ok, manifest_ok)

    failures = [item for item in checks if not item["passed"]]
    report = {
        "capability": "FORWARD_OUTCOME_LABELER_V1_VALIDATOR",
        "checks": len(checks),
        "failed_checks": len(failures),
        "blockers": len(failures),
        "check_results": checks,
        "decision": "FORWARD_OUTCOME_LABELER_V1_VALIDATED_NO_REAL_NETWORK" if not failures else "FORWARD_OUTCOME_LABELER_V1_VALIDATION_FAILED",
        "real_network_request_executed": False,
        "real_market_data_acquired": False,
        "official_append_executed": False,
    }
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
