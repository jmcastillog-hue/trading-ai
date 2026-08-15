from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path

from src.exchange import forward_outcome_future_closed_candle_source_v1 as m
from src.long_side.forward_outcome_labeler_v1 import (
    FORWARD_HORIZONS_BARS,
    FUTURE_SOURCE_COLUMNS,
)

CAPABILITY = "FORWARD_OUTCOME_FUTURE_CLOSED_CANDLE_SOURCE_V1_VALIDATOR"

SOURCE = Path(
    "src/exchange/forward_outcome_future_closed_candle_source_v1.py"
)
DOCS = Path(
    "docs/FORWARD_OUTCOME_FUTURE_CLOSED_CANDLE_SOURCE_V1.md"
)
TESTS = Path(
    "tests/test_forward_outcome_future_closed_candle_source_v1.py"
)
MANIFEST = Path(
    "FORWARD_OUTCOME_FUTURE_CLOSED_CANDLE_SOURCE_V1_MANIFEST.sha256"
)


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
    tree = ast.parse(source)

    imports = sorted(
        {
            node.names[0].name.split(".")[0]
            for node in ast.walk(tree)
            if isinstance(node, ast.Import)
        }
        | {
            (node.module or "").split(".")[0]
            for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom) and node.module
        }
    )

    checks = []

    def check(name, passed, details, blocker=True):
        checks.append(
            {
                "check": name,
                "passed": bool(passed),
                "details": details,
                "blocker": bool(blocker and not passed),
            }
        )

    check(
        "capability",
        m.CAPABILITY == "FORWARD_OUTCOME_FUTURE_CLOSED_CANDLE_SOURCE_V1",
        m.CAPABILITY,
    )
    check(
        "authorization_exact",
        m.AUTHORIZATION
        == "CAPTURE_ONE_SHOT_FORWARD_OUTCOME_FUTURE_CLOSED_CANDLES_V1",
        m.AUTHORIZATION,
    )
    check(
        "required_rows_17",
        m.REQUIRED_CLOSED_ROWS == 17,
        str(m.REQUIRED_CLOSED_ROWS),
    )
    check(
        "forward_horizons_exact",
        tuple(FORWARD_HORIZONS_BARS) == (1, 2, 4, 8, 16),
        json.dumps(list(FORWARD_HORIZONS_BARS)),
    )
    check(
        "source_columns_exact",
        tuple(FUTURE_SOURCE_COLUMNS)
        == (
            "open_time_utc",
            "close_time_utc",
            "symbol",
            "timeframe",
            "open",
            "high",
            "low",
            "close",
            "volume",
            "candle_closed",
        ),
        json.dumps(list(FUTURE_SOURCE_COLUMNS)),
    )
    check(
        "btc_only",
        m.SYMBOL == "BTCUSDT",
        m.SYMBOL,
    )
    check(
        "15m_only",
        m.TIMEFRAME == "15m",
        m.TIMEFRAME,
    )
    check(
        "requests_import_only_network_client",
        "requests" in imports
        and "httpx" not in imports
        and "websocket" not in imports
        and "websockets" not in imports,
        json.dumps(imports),
    )
    check(
        "no_thread_process_scheduler",
        not any(
            name in imports
            for name in (
                "threading",
                "multiprocessing",
                "asyncio",
                "schedule",
                "apscheduler",
            )
        ),
        json.dumps(imports),
    )
    check(
        "no_subprocess",
        "subprocess" not in imports,
        json.dumps(imports),
    )
    check(
        "no_official_writer_import",
        "append_official_prospective_evidence" not in source,
        "absent",
    )
    check(
        "authorization_before_output",
        source.index("CAPTURE_AUTHORIZATION_REQUIRED")
        < source.index("out.mkdir()"),
        "ordered",
    )
    check(
        "one_get_call",
        source.count("response = get(") == 1,
        str(source.count("response = get(")),
    )
    check(
        "start_time_parameter",
        '"startTime": _milliseconds(first_open)' in source,
        "present",
    )
    check(
        "limit_parameter_17_contract",
        '"limit": REQUIRED_CLOSED_ROWS' in source,
        "present",
    )
    check(
        "maturity_gate",
        "REQUIRED_FORWARD_HORIZON_NOT_YET_MATURE" in source,
        "present",
    )
    check(
        "exact_start_and_gap_check",
        "BINANCE_KLINE_START_OR_GAP_INVALID" in source,
        "present",
    )
    check(
        "closed_at_capture_check",
        "FUTURE_CANDLE_NOT_CLOSED_AT_CAPTURE" in source,
        "present",
    )
    check(
        "external_output_guard",
        "OUTPUT_INSIDE_REPOSITORY_PROHIBITED" in source,
        "present",
    )
    check(
        "create_only_write",
        'with path.open("xb")' in source,
        "present",
    )
    check(
        "automatic_retry_false",
        '"automatic_retry_executed": False' in source,
        "present",
    )
    check(
        "api_key_false",
        '"api_key_used": False' in source,
        "present",
    )
    check(
        "account_order_false",
        '"account_endpoint_used": False' in source
        and '"order_endpoint_used": False' in source,
        "present",
    )
    check(
        "websocket_background_false",
        '"websocket_used": False' in source
        and '"background_execution": False' in source,
        "present",
    )
    check(
        "permission_false_surface",
        all(
            field in m.FALSE_FIELDS
            for field in (
                "official_append_allowed",
                "signal_generation_enabled",
                "live_alerts_allowed",
                "paper_trade_execution_allowed",
                "real_capital_allowed",
                "execution_allowed",
            )
        ),
        json.dumps(list(m.FALSE_FIELDS)),
    )
    check(
        "metadata_source_hash",
        '"source_sha256": source_sha' in source,
        "present",
    )
    check(
        "validator_manifest_scope",
        "MANIFEST_SCOPE_INVALID" in source,
        "present",
    )
    check(
        "docs_separate_from_sync",
        "deliberately separate from synchronized market observation" in docs,
        "present",
    )
    check(
        "docs_17_reason",
        "Why 17 candles" in docs,
        "present",
    )
    check(
        "docs_no_real_auth_by_publish",
        "Publishing this component does not authorize either real action." in docs,
        "present",
    )
    check(
        "docs_separate_package_auth",
        "label-package creation remain separate authorization" in docs,
        "present",
    )
    check(
        "test_old_auth_rejected",
        "test_05_old_spot_auth_rejected_before_request" in tests,
        "present",
    )
    check(
        "test_exact_params",
        "test_10_one_request_exact_params" in tests,
        "present",
    )
    check(
        "test_maturity",
        "test_09_horizon_must_be_mature" in tests,
        "present",
    )
    check(
        "test_gap",
        "test_14_gap_rejected" in tests,
        "present",
    )
    check(
        "test_tamper",
        "test_22_manifest_tamper_detected" in tests,
        "present",
    )
    check(
        "test_official_unchanged",
        "test_24_official_artifacts_unchanged" in tests,
        "present",
    )

    lines = [
        line
        for line in MANIFEST.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    manifest_ok = len(lines) == 4
    if manifest_ok:
        for line in lines:
            parts = line.split("  ", 1)
            if len(parts) != 2 or len(parts[0]) != 64:
                manifest_ok = False
                break
            path = Path(parts[1])
            if not path.is_file() or sha(path) != parts[0]:
                manifest_ok = False
                break

    check(
        "source_manifest_entries_4",
        len(lines) == 4,
        str(len(lines)),
    )
    check(
        "source_manifest_valid",
        manifest_ok,
        str(manifest_ok),
    )

    failed = [item for item in checks if not item["passed"]]
    blockers = [item for item in checks if item["blocker"]]

    return {
        "capability": CAPABILITY,
        "checks": len(checks),
        "failed_checks": len(failed),
        "blockers": len(blockers),
        "check_results": checks,
        "decision": (
            "FORWARD_OUTCOME_FUTURE_CLOSED_CANDLE_SOURCE_V1_"
            "VALIDATED_NO_REAL_NETWORK"
            if not blockers
            else "BLOCKED"
        ),
        "real_network_request_executed": False,
        "real_market_data_acquired": False,
        "official_append_executed": False,
        "real_future_source_capture_executed": False,
    }


if __name__ == "__main__":
    result = run()
    print(json.dumps(result, indent=2, sort_keys=True))
    raise SystemExit(0 if result["blockers"] == 0 else 1)
