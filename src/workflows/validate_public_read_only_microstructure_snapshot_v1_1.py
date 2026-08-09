from __future__ import annotations

import ast
import hashlib
import json
import subprocess
from pathlib import Path

from src.exchange import public_read_only_microstructure_snapshot_v1_1 as m

CAPABILITY = "PUBLIC_READ_ONLY_MICROSTRUCTURE_SNAPSHOT_V1_1_VALIDATOR"
SOURCE = Path("src/exchange/public_read_only_microstructure_snapshot_v1_1.py")
LEGACY_SOURCE = Path("src/exchange/public_read_only_microstructure_snapshot_v1.py")
DOCS = Path("docs/PUBLIC_READ_ONLY_MICROSTRUCTURE_SNAPSHOT_V1_1.md")
TESTS = Path("tests/test_public_read_only_microstructure_snapshot_v1_1.py")
MANIFEST = Path("PUBLIC_READ_ONLY_MICROSTRUCTURE_SNAPSHOT_V1_1_MANIFEST.sha256")
EXPECTED_BASE = "e302325af32ef6f2df83a1518314129164064e40"
EXPECTED_LEGACY_V1_BLOB = "7be592ec6bbac9a4657842947a2cbcebd2ccea9a"

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
        checks.append({
            "check": name,
            "passed": bool(passed),
            "details": details,
            "blocker": blocker and not passed,
        })

    check("capability_identity", m.CAPABILITY == "PUBLIC_READ_ONLY_MICROSTRUCTURE_SNAPSHOT_V1_1", m.CAPABILITY)
    check("authorization_exact_preserved", m.AUTHORIZATION == "CAPTURE_ONE_SHOT_BINANCE_USDM_PUBLIC_MICROSTRUCTURE_V1", m.AUTHORIZATION)
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
    check("no_thread_process_scheduler", not any(x in imports for x in ["threading", "multiprocessing", "asyncio", "schedule", "apscheduler"]), json.dumps(imports))
    check("no_official_writer_import", "append_official_prospective_evidence" not in source, "official writer absent")
    check("depth_limit_1000", m.DEPTH_LIMIT == 1000, str(m.DEPTH_LIMIT))
    check("depth_bands_frozen", tuple(m.DEPTH_BANDS_BPS) == (5, 10, 25, 50), json.dumps(list(m.DEPTH_BANDS_BPS)))
    depth_params = dict(m.ENDPOINTS[1][1] or {})
    check("depth_endpoint_uses_1000", depth_params == {"symbol": "BTCUSDT", "limit": 1000}, json.dumps(depth_params, sort_keys=True))
    legacy_ok = False
    legacy_details = "missing"
    if LEGACY_SOURCE.is_file():
        try:
            legacy_blob = subprocess.check_output(
                ["git", "rev-parse", f"{EXPECTED_BASE}:{LEGACY_SOURCE.as_posix()}"],
                text=True,
            ).strip()
            worktree_ok = subprocess.run(
                ["git", "diff", "--quiet", EXPECTED_BASE, "--", LEGACY_SOURCE.as_posix()]
            ).returncode == 0
            staged_ok = subprocess.run(
                ["git", "diff", "--cached", "--quiet", EXPECTED_BASE, "--", LEGACY_SOURCE.as_posix()]
            ).returncode == 0
            legacy_ok = legacy_blob == EXPECTED_LEGACY_V1_BLOB and worktree_ok and staged_ok
            legacy_details = json.dumps({
                "blob": legacy_blob,
                "worktree_diff": not worktree_ok,
                "staged_diff": not staged_ok,
            }, sort_keys=True)
        except (subprocess.CalledProcessError, OSError) as exc:
            legacy_details = type(exc).__name__
    check("legacy_v1_preserved", legacy_ok, legacy_details)
    check("transactional_create_only", ".tmp-" in source and "temp.rename(out)" in source and "shutil.rmtree" in source, "temp/rename/cleanup present")
    check("external_output_guard", "OUTPUT_INSIDE_REPOSITORY_PROHIBITED" in source, "guard present")
    check("false_permission_surface", len(m.FALSE_FIELDS) >= 10 and "execution_allowed" in m.FALSE_FIELDS and "signal_generation_enabled" in m.FALSE_FIELDS, str(len(m.FALSE_FIELDS)))
    check("coverage_explicit_not_assumed", "depth_coverage_is_explicit_not_assumed" in source and "coverage_complete" in source, "coverage contract present")
    check("context_only_constraints", "does_not_modify_frozen_long_rule" in source and "order_book_does_not_reveal_hidden_stops_or_liquidations" in source, "constraints present")
    check("official_docs_referenced", "developers.binance.com" in docs and "/fapi/v1/depth" in docs, "official Binance references documented")
    roadmap_markers = [
        "EXTERNAL_CYCLE_REGRESSION_BASELINE_V1",
        "Event Risk Calendar V1",
        "PLAN_BTC_LIQUIDITY_SWEEP_BEFORE_EXPANSION_RESEARCH_V1",
        "EXTERNAL_THESIS_MODEL_CARD_V1",
        "Forward Outcome Labeler V1",
        "Level A Standard",
        "Level B",
    ]
    check("approved_roadmap_documented", all(x in docs for x in roadmap_markers), "approved Level A/Level B roadmap markers present")
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
        "decision": "PUBLIC_READ_ONLY_MICROSTRUCTURE_SNAPSHOT_V1_1_VALIDATED_NO_REAL_NETWORK" if not blockers else "BLOCKED",
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
