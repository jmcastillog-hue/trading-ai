from __future__ import annotations

import ast
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

from src.long_side.synchronized_15m_observation_v1_1 import (
    CAPABILITY,
    DEPTH_BANDS_BPS,
    EXPECTED_MICROSTRUCTURE_REQUESTS_PER_CYCLE,
    EXPECTED_NETWORK_REQUESTS_PER_CYCLE,
    EXPECTED_SPOT_REQUESTS_PER_CYCLE,
    HISTORICAL_COMPONENT_NAMES,
    IMPLEMENTATION_OR_REPAIR_ATTEMPT,
    MAX_IMPLEMENTATION_OR_REPAIR_ATTEMPTS,
    MICROSTRUCTURE_DEPTH_LIMIT,
    REQUIRED_DEPTH_BANDS_BPS,
    SESSION_AUTHORIZATION,
    TEMPORAL_ALIGNMENT_POLICY_VERSION,
    assess_component_temporal_eligibility,
    build_microstructure_context_v1_1,
)

SOURCE_PATH = Path("src/long_side/synchronized_15m_observation_v1_1.py")
DOC_PATH = Path("docs/SYNCHRONIZED_15M_OBSERVATION_V1_1.md")
MANIFEST_PATH = Path("SYNCHRONIZED_15M_OBSERVATION_V1_1_MANIFEST.sha256")


def _fixture() -> dict:
    reference_close = datetime(
        2026, 8, 10, 23, 44, 59, 999000, tzinfo=timezone.utc
    )
    boundary = reference_close + timedelta(milliseconds=1)

    def band(bps: int, covered: bool, imbalance: float) -> dict:
        return {
            "band_bps": bps,
            "coverage_complete": covered,
            "bid_level_count": 100 if bps <= 10 else 1000,
            "ask_level_count": 100 if bps <= 10 else 1000,
            "bid_notional_usdt": 1000000.0 + bps,
            "ask_notional_usdt": 1200000.0 + bps,
            "notional_imbalance": imbalance,
        }

    return {
        "capability": "PUBLIC_READ_ONLY_MICROSTRUCTURE_SNAPSHOT_V1_1",
        "provider": "BINANCE_USDM_PUBLIC_REST",
        "symbol": "BTCUSDT",
        "timeframe": "15m",
        "request_count": 7,
        "depth_limit_requested": 1000,
        "depth_bands_bps": [5, 10, 25, 50],
        "reference_closed_candle_utc": reference_close.isoformat(),
        "order_book": {
            "best_bid": 63936.6,
            "best_ask": 63936.7,
            "mid_price": 63936.65,
            "spread_bps": 0.0156,
            "furthest_bid_distance_bps": 18.54,
            "furthest_ask_distance_bps": 19.62,
            "bands": {
                "5": band(5, True, -0.3366855719911952),
                "10": band(10, True, -0.15515907108284194),
                "25": band(25, False, -0.07921728717115499),
                "50": band(50, False, -0.07921728717115499),
            },
        },
        "open_interest": {
            "latest_15m": {
                "timestamp_utc": boundary.isoformat(),
                "sum_open_interest": 106287.591,
            },
            "previous_15m": {
                "timestamp_utc": (boundary - timedelta(minutes=15)).isoformat(),
                "sum_open_interest": 106336.682,
            },
            "current_time_utc": (boundary + timedelta(seconds=1)).isoformat(),
            "change_15m": -49.091,
            "change_15m_percent": -0.04616563078392868,
            "value_change_15m_usdt": -5256614.885993004,
            "value_change_15m_percent": -0.07728867352349457,
        },
        "mark_price_funding": {
            "provider_time_utc": (boundary + timedelta(seconds=9)).isoformat(),
            "mark_price": 63938.91114493,
            "index_price": 63967.50152174,
            "mark_index_basis_bps": -4.469515946355879,
            "last_funding_rate": 2.571e-05,
        },
        "taker_buy_sell_volume": {
            "latest_15m": {
                "timestamp_utc": (boundary - timedelta(minutes=30)).isoformat(),
                "buy_volume_base": 238.723,
                "sell_volume_base": 197.797,
                "net_taker_volume_base": 40.926,
                "buy_sell_ratio": 1.2069,
            },
            "previous_15m": {
                "timestamp_utc": (boundary - timedelta(minutes=45)).isoformat(),
                "buy_sell_ratio": 0.6562,
            },
        },
        "global_long_short_account_ratio": {
            "latest_15m": {
                "timestamp_utc": boundary.isoformat(),
                "long_account_fraction": 0.6159,
                "short_account_fraction": 0.3841,
                "long_short_account_ratio": 1.6035,
            },
            "previous_15m": {
                "timestamp_utc": (boundary - timedelta(minutes=15)).isoformat(),
                "long_short_account_ratio": 1.6035,
            },
        },
        "synchronization": {
            "reference_boundary_utc": boundary.isoformat(),
            "aligned_15m_components": [
                "open_interest_history",
                "taker_buy_sell_volume",
                "global_long_short_account_ratio",
            ],
            "point_in_time_components": [
                "order_book",
                "current_open_interest",
                "mark_price_funding",
            ],
            "point_in_time_components_are_not_historical_reconstruction": True,
        },
        "interpretation_constraints": {
            "context_only": True,
            "depth_coverage_is_explicit_not_assumed": True,
            "does_not_modify_frozen_long_rule": True,
        },
    }


def main() -> int:
    checks: list[dict] = []

    def add(name: str, passed: bool, details) -> None:
        checks.append(
            {
                "check": name,
                "passed": bool(passed),
                "details": details,
                "blocker": not bool(passed),
            }
        )

    source = SOURCE_PATH.read_text(encoding="utf-8")
    tree = ast.parse(source)
    imports: set[str] = set()
    calls: set[str] = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.add(node.module)
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                calls.add(node.func.id)
            elif isinstance(node.func, ast.Attribute):
                calls.add(node.func.attr)

    add("capability_v1_1", CAPABILITY == "SYNCHRONIZED_15M_OBSERVATION_V1_1", CAPABILITY)
    add("repair_attempt_3", IMPLEMENTATION_OR_REPAIR_ATTEMPT == 3, IMPLEMENTATION_OR_REPAIR_ATTEMPT)
    add("repair_limit_10", MAX_IMPLEMENTATION_OR_REPAIR_ATTEMPTS == 10, MAX_IMPLEMENTATION_OR_REPAIR_ATTEMPTS)
    add(
        "new_session_authorization",
        SESSION_AUTHORIZATION == "RUN_BOUNDED_SYNCHRONIZED_15M_OBSERVATION_SESSION_V1_1",
        SESSION_AUTHORIZATION,
    )
    add(
        "old_v1_session_authorization_not_constant",
        'SESSION_AUTHORIZATION = "RUN_BOUNDED_SYNCHRONIZED_15M_OBSERVATION_SESSION_V1"' not in source,
        "old token not assigned",
    )
    add("spot_request_contract", EXPECTED_SPOT_REQUESTS_PER_CYCLE == 1, EXPECTED_SPOT_REQUESTS_PER_CYCLE)
    add("micro_request_contract", EXPECTED_MICROSTRUCTURE_REQUESTS_PER_CYCLE == 7, EXPECTED_MICROSTRUCTURE_REQUESTS_PER_CYCLE)
    add("total_request_contract", EXPECTED_NETWORK_REQUESTS_PER_CYCLE == 8, EXPECTED_NETWORK_REQUESTS_PER_CYCLE)
    add("depth_1000", MICROSTRUCTURE_DEPTH_LIMIT == 1000, MICROSTRUCTURE_DEPTH_LIMIT)
    add("depth_bands_frozen", DEPTH_BANDS_BPS == (5, 10, 25, 50), list(DEPTH_BANDS_BPS))
    add("required_depth_bands_frozen", REQUIRED_DEPTH_BANDS_BPS == (5, 10), list(REQUIRED_DEPTH_BANDS_BPS))
    add(
        "historical_component_set_frozen",
        HISTORICAL_COMPONENT_NAMES
        == (
            "open_interest_history",
            "taker_buy_sell_volume",
            "global_long_short_account_ratio",
        ),
        list(HISTORICAL_COMPONENT_NAMES),
    )
    add(
        "temporal_policy_version",
        TEMPORAL_ALIGNMENT_POLICY_VERSION
        == "SYNCHRONIZED_COMPONENT_TIMESTAMP_ELIGIBILITY_V1",
        TEMPORAL_ALIGNMENT_POLICY_VERSION,
    )
    add(
        "no_direct_http_client",
        not any(name.startswith(("requests", "urllib", "httpx", "aiohttp")) for name in imports),
        sorted(imports),
    )
    add(
        "no_thread_process_runtime",
        not any(name.startswith(("threading", "multiprocessing", "subprocess")) for name in imports),
        sorted(imports),
    )
    add(
        "no_scheduler_dependency",
        not any(name.startswith(("schedule", "apscheduler")) for name in imports),
        sorted(imports),
    )
    add(
        "official_writer_absent",
        "append_official_prospective_evidence" not in source,
        "absent",
    )
    add(
        "no_messaging_browser_strings",
        all(
            token not in source.lower()
            for token in ("whatsapp", "telegram", "selenium", "playwright", "quantfury")
        ),
        "none",
    )
    add(
        "exact_timestamp_equality_present",
        "timestamp_equal_reference_boundary" in source
        and "component_time == reference_boundary" in source,
        "present",
    )
    add(
        "no_tolerance_window",
        "timedelta(seconds=30)" not in source
        and "timedelta(minutes=1)" not in source,
        "exact equality only",
    )
    add(
        "historical_equivalence_not_claimed",
        '"historical_interval_equivalence_claimed": False' in source,
        "false",
    )
    add(
        "point_in_time_not_historical",
        '"usable_for_historical_interval_alignment": False' in source,
        "false",
    )
    add(
        "misaligned_preserved_not_usable",
        '"misaligned_historical_component_preserved_but_not_usable": True' in source,
        "present",
    )
    add(
        "alignment_recomputed_marker",
        "alignment_recomputed_by_synchronized_observation_v1_1" in source,
        "present",
    )
    add(
        "microstructure_cannot_create_candidate",
        '"microstructure_can_create_candidate": False' in source,
        "false",
    )
    add(
        "microstructure_cannot_cancel_candidate",
        '"microstructure_can_cancel_candidate": False' in source,
        "false",
    )
    add(
        "microstructure_cannot_modify_primary_rule",
        '"microstructure_can_modify_primary_rule": False' in source,
        "false",
    )

    fixture = _fixture()
    eligibility = assess_component_temporal_eligibility(fixture)
    context = build_microstructure_context_v1_1(fixture)

    taker = eligibility["historical_components"]["taker_buy_sell_volume"]
    oi = eligibility["historical_components"]["open_interest_history"]
    global_ratio = eligibility["historical_components"]["global_long_short_account_ratio"]

    add("real_fixture_taker_delta_minus_1800", taker["timestamp_delta_seconds"] == -1800.0, taker["timestamp_delta_seconds"])
    add("real_fixture_taker_not_usable", taker["usable_for_synchronized_context"] is False, taker["usable_for_synchronized_context"])
    add("real_fixture_oi_usable", oi["usable_for_synchronized_context"] is True, oi["usable_for_synchronized_context"])
    add("real_fixture_global_usable", global_ratio["usable_for_synchronized_context"] is True, global_ratio["usable_for_synchronized_context"])
    add(
        "real_fixture_corrected_aligned_list",
        eligibility["aligned_historical_components"]
        == ["open_interest_history", "global_long_short_account_ratio"],
        eligibility["aligned_historical_components"],
    )
    add(
        "real_fixture_corrected_misaligned_list",
        eligibility["misaligned_historical_components"] == ["taker_buy_sell_volume"],
        eligibility["misaligned_historical_components"],
    )
    add(
        "upstream_alignment_preserved_as_provenance",
        eligibility["upstream_reported_aligned_15m_components"]
        == list(HISTORICAL_COMPONENT_NAMES),
        eligibility["upstream_reported_aligned_15m_components"],
    )
    add(
        "taker_numeric_preserved",
        context["taker_buy_sell_volume"]["latest_15m"]["buy_sell_ratio"] == 1.2069,
        context["taker_buy_sell_volume"]["latest_15m"]["buy_sell_ratio"],
    )
    add(
        "taker_payload_marked_unusable",
        context["taker_buy_sell_volume"]["latest_15m_usable_for_synchronized_context"] is False,
        context["taker_buy_sell_volume"]["latest_15m_usable_for_synchronized_context"],
    )
    add("depth_5_usable", context["bands"]["5"]["usable_for_context"] is True, context["bands"]["5"]["usable_for_context"])
    add("depth_10_usable", context["bands"]["10"]["usable_for_context"] is True, context["bands"]["10"]["usable_for_context"])
    add("depth_25_not_usable", context["bands"]["25"]["usable_for_context"] is False and context["bands"]["25"]["notional_imbalance_usable"] is None, context["bands"]["25"])
    add("depth_50_not_usable", context["bands"]["50"]["usable_for_context"] is False and context["bands"]["50"]["notional_imbalance_usable"] is None, context["bands"]["50"])

    docs = DOC_PATH.read_text(encoding="utf-8")
    add("docs_real_fixture", "2026-08-10T23:15:00+00:00" in docs and "-1800" in docs, "present")
    add("docs_forward_labeler_next", "FORWARD_OUTCOME_LABELER_V1" in docs, "present")
    add("docs_no_repeat_real_capture_required", "No repeat of the real synchronized capture is required" in docs, "present")

    manifest_lines = [
        line for line in MANIFEST_PATH.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    manifest_ok = len(manifest_lines) == 4
    if manifest_ok:
        for line in manifest_lines:
            parts = line.split("  ", 1)
            if len(parts) != 2 or len(parts[0]) != 64:
                manifest_ok = False
                break
            expected, name = parts
            path = Path(name)
            if not path.is_file():
                manifest_ok = False
                break
            import hashlib
            actual = hashlib.sha256(path.read_bytes()).hexdigest()
            if actual != expected:
                manifest_ok = False
                break
    add("source_manifest_valid", manifest_ok, len(manifest_lines))

    failed = [item for item in checks if not item["passed"]]
    payload = {
        "capability": "SYNCHRONIZED_15M_OBSERVATION_V1_1_VALIDATOR",
        "decision": "SYNCHRONIZED_15M_OBSERVATION_V1_1_TEMPORAL_ELIGIBILITY_VALIDATED_NO_REAL_NETWORK",
        "checks": len(checks),
        "failed_checks": len(failed),
        "blockers": sum(1 for item in failed if item["blocker"]),
        "real_regression_reference_boundary_utc": "2026-08-10T23:45:00+00:00",
        "real_regression_taker_timestamp_utc": "2026-08-10T23:15:00+00:00",
        "real_regression_taker_usable": False,
        "real_network_request_executed": False,
        "real_market_data_acquired": False,
        "official_append_executed": False,
        "check_results": checks,
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
