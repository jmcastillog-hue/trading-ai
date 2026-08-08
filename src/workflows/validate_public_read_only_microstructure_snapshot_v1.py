from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path

from src.exchange import public_read_only_microstructure_snapshot_v1 as m

CAPABILITY = "PUBLIC_READ_ONLY_MICROSTRUCTURE_SNAPSHOT_V1_VALIDATOR"
SOURCE = Path("src/exchange/public_read_only_microstructure_snapshot_v1.py")
DOCS = Path("docs/PUBLIC_READ_ONLY_MICROSTRUCTURE_SNAPSHOT_V1.md")
TESTS = Path("tests/test_public_read_only_microstructure_snapshot_v1.py")
MANIFEST = Path("PUBLIC_READ_ONLY_MICROSTRUCTURE_SNAPSHOT_V1_MANIFEST.sha256")

def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def run() -> dict:
    source = SOURCE.read_text(encoding="utf-8")
    docs = DOCS.read_text(encoding="utf-8")
    tree = ast.parse(source)
    imports = sorted({
        node.names[0].name.split(".")[0]
        for node in ast.walk(tree)
        if isinstance(node, ast.Import)
    } | {
        (node.module or "").split(".")[0]
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module
    })
    checks = []

    def check(name: str, passed: bool, details: str, blocker: bool = True):
        checks.append({"check": name, "passed": bool(passed), "details": details, "blocker": blocker and not passed})

    check("capability_identity", m.CAPABILITY == "PUBLIC_READ_ONLY_MICROSTRUCTURE_SNAPSHOT_V1", m.CAPABILITY)
    check("authorization_exact", m.AUTHORIZATION == "CAPTURE_ONE_SHOT_BINANCE_USDM_PUBLIC_MICROSTRUCTURE_V1", m.AUTHORIZATION)
    check("symbol_timeframe_frozen", m.SYMBOL == "BTCUSDT" and m.TIMEFRAME == "15m", f"{m.SYMBOL}/{m.TIMEFRAME}")
    check("endpoint_count_7", len(m.ENDPOINTS) == 7, str(len(m.ENDPOINTS)))
    expected = [
        "/fapi/v1/klines",
        "/fapi/v1/depth",
        "/fapi/v1/openInterest",
        "/fapi/v1/premiumIndex",
        "/futures/data/openInterestHist",
        "/futures/data/takerlongshortRatio",
        "/futures/data/globalLongShortAccountRatio",
    ]
    check("endpoint_allowlist_exact", [x[0] for x in m.ENDPOINTS] == expected, json.dumps([x[0] for x in m.ENDPOINTS]))
    check("public_fapi_base_only", m.BASE_URL == "https://fapi.binance.com", m.BASE_URL)
    check("no_order_or_account_endpoints", not any(x in source for x in ["/order", "/account", "/positionRisk", "/listenKey"]), "restricted endpoint strings absent")
    check("no_top_trader_endpoints", "topLongShortAccountRatio" not in source and "topLongShortPositionRatio" not in source, "API-key top-trader endpoints absent")
    check("no_signature_or_recvwindow", "signature" not in source.lower() and "recvwindow" not in source.lower(), "signed request fields absent")
    check("no_api_key_header", "X-MBX-APIKEY" not in source and "headers=" not in source.replace(" ", ""), "no authentication header")
    check("no_websocket", "websocket" not in imports and "websockets" not in imports, json.dumps(imports))
    check("no_thread_process_scheduler", not any(x in imports for x in ["threading","multiprocessing","asyncio","schedule","apscheduler"]), json.dumps(imports))
    check("no_official_writer_import", "append_official_prospective_evidence" not in source, "official writer absent")
    check("depth_limit_100", m.DEPTH_LIMIT == 100, str(m.DEPTH_LIMIT))
    check("transactional_create_only", ".tmp-" in source and "temp.rename(out)" in source and "shutil.rmtree" in source, "temp/rename/cleanup present")
    check("external_output_guard", "OUTPUT_INSIDE_REPOSITORY_PROHIBITED" in source, "guard present")
    check("false_permission_surface", len(m.FALSE_FIELDS) >= 10 and "execution_allowed" in m.FALSE_FIELDS and "signal_generation_enabled" in m.FALSE_FIELDS, str(len(m.FALSE_FIELDS)))
    check("context_only_constraints", "does_not_modify_frozen_long_rule" in source and "order_book_does_not_reveal_hidden_stops_or_liquidations" in source, "constraints present")
    check("official_docs_referenced", "developers.binance" in docs and "/fapi/v1/depth" in docs and "/futures/data/takerlongshortRatio" in docs, "official Binance references documented")
    lines = [x for x in MANIFEST.read_text(encoding="utf-8").splitlines() if x.strip()]
    manifest_ok = len(lines) == 4
    if manifest_ok:
        for line in lines:
            parts = line.split("  ", 1)
            if len(parts) != 2 or len(parts[0]) != 64:
                manifest_ok = False
                break
            p = Path(parts[1])
            if not p.is_file() or sha(p) != parts[0]:
                manifest_ok = False
                break
    check("source_manifest_valid", manifest_ok, str(len(lines)))

    failed = [x for x in checks if not x["passed"]]
    blockers = [x for x in checks if x["blocker"]]
    return {
        "capability": CAPABILITY,
        "checks": len(checks),
        "failed_checks": len(failed),
        "blockers": len(blockers),
        "check_results": checks,
        "decision": "PUBLIC_READ_ONLY_MICROSTRUCTURE_SNAPSHOT_V1_VALIDATED_NO_REAL_NETWORK" if not blockers else "BLOCKED",
        "real_network_request_executed": False,
        "real_market_data_acquired": False,
        "api_key_used": False,
        "authenticated_endpoint_used": False,
        "websocket_used": False,
        "official_append_executed": False,
        "external_execution_allowed": False,
    }

if __name__ == "__main__":
    result = run()
    print(json.dumps(result, indent=2, sort_keys=True))
    raise SystemExit(0 if result["blockers"] == 0 else 1)
