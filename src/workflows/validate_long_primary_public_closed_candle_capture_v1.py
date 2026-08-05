from __future__ import annotations

import ast
import csv
import json
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

from src.exchange.long_primary_public_closed_candle_capture_v1 import (
    METADATA_FILENAME,
    PUBLIC_SPOT_KLINES_URL,
    REAL_CAPTURE_AUTHORIZATION,
    SOURCE_COLUMNS,
    SOURCE_FILENAME,
    capture_real_binance_public_closed_candles,
    validate_closed_candle_capture,
)

REPORT_DECISION = (
    "LONG_PRIMARY_PUBLIC_CLOSED_CANDLE_CAPTURE_V1_"
    "VALIDATED_NO_REAL_NETWORK"
)
CAPTURE_TIME = datetime(2026, 8, 5, 0, 30, 0, tzinfo=timezone.utc)
INTERVAL_MS = 15 * 60 * 1000


class FakeResponse:
    def __init__(self, rows):
        self.rows = rows

    def raise_for_status(self) -> None:
        return None

    def json(self):
        return self.rows


def sha256_path(path: Path) -> str:
    import hashlib

    return hashlib.sha256(path.read_bytes()).hexdigest()


def git_status(repo: Path) -> list[str]:
    import subprocess

    result = subprocess.run(
        ["git", "status", "--porcelain=v1", "--untracked-files=all"],
        cwd=repo,
        text=True,
        capture_output=True,
        check=True,
    )
    return [line for line in result.stdout.splitlines() if line.strip()]


def build_rows() -> list[list[object]]:
    capture_ms = int(CAPTURE_TIME.timestamp() * 1000)
    latest_close_ms = capture_ms - 1
    latest_open_ms = latest_close_ms - (INTERVAL_MS - 1)
    first_open_ms = latest_open_ms - (62 * INTERVAL_MS)
    rows: list[list[object]] = []
    for index in range(63):
        open_ms = first_open_ms + (index * INTERVAL_MS)
        close_ms = open_ms + INTERVAL_MS - 1
        open_price = 60000.0 + index
        close_price = open_price + 5.0
        rows.append(
            [
                open_ms,
                str(open_price),
                str(close_price + 10.0),
                str(open_price - 10.0),
                str(close_price),
                "100",
                close_ms,
                "0",
                1,
                "0",
                "0",
                "0",
            ]
        )
    open_ms = first_open_ms + (63 * INTERVAL_MS)
    rows.append(
        [
            open_ms,
            "61000",
            "61010",
            "60990",
            "61005",
            "50",
            open_ms + INTERVAL_MS - 1,
            "0",
            1,
            "0",
            "0",
            "0",
        ]
    )
    return rows


def main() -> int:
    repo = Path.cwd().resolve()
    dataset = repo / "data/forward/long_forward_observation_dataset_v1.csv"
    manifest = repo / "data/forward/long_forward_observation_dataset_v1.manifest.csv"
    dataset_before = sha256_path(dataset)
    manifest_before = sha256_path(manifest)
    status_before = git_status(repo)

    checks: list[dict[str, object]] = []

    def add(name: str, passed: bool, details: str) -> None:
        checks.append(
            {
                "check": name,
                "passed": bool(passed),
                "blocker": not bool(passed),
                "details": details,
            }
        )

    with tempfile.TemporaryDirectory() as temp:
        output = Path(temp) / "capture"
        fake = FakeResponse(build_rows())
        with patch(
            "src.exchange.long_primary_public_closed_candle_capture_v1._utc_now",
            return_value=CAPTURE_TIME,
        ), patch(
            "src.exchange.long_primary_public_closed_candle_capture_v1.requests.get",
            return_value=fake,
        ) as mocked_get:
            result = capture_real_binance_public_closed_candles(
                repo_root=repo,
                output_directory=output,
                authorization=REAL_CAPTURE_AUTHORIZATION,
            )

        validation = validate_closed_candle_capture(output)
        with (output / SOURCE_FILENAME).open(
            "r", encoding="utf-8", newline=""
        ) as handle:
            reader = csv.DictReader(handle)
            rows = list(reader)
            header = tuple(reader.fieldnames or ())
        metadata = json.loads(
            (output / METADATA_FILENAME).read_text(encoding="utf-8")
        )

        add("mock_capture_completed", result["closed_candle_rows"] == 63, f"rows={result['closed_candle_rows']}")
        add("open_candle_excluded", result["open_candles_excluded"] == 1, f"excluded={result['open_candles_excluded']}")
        add("exact_source_schema", header == SOURCE_COLUMNS, f"columns={len(header)}")
        add("all_rows_closed", all(row["candle_closed"] == "True" for row in rows), "all closed")
        add("manifest_valid", validation["manifest_entries"] == 2, f"entries={validation['manifest_entries']}")
        add("single_request", mocked_get.call_count == 1, f"calls={mocked_get.call_count}")
        request_args, request_kwargs = mocked_get.call_args
        add("public_spot_endpoint", request_args[0] == PUBLIC_SPOT_KLINES_URL, request_args[0])
        add("request_params_exact", request_kwargs["params"] == {"symbol": "BTCUSDT", "interval": "15m", "limit": 64}, str(request_kwargs["params"]))
        add("no_redirects", request_kwargs["allow_redirects"] is False, str(request_kwargs["allow_redirects"]))
        add("no_review_package", result["review_package_created"] is False, "review_package_created=False")
        add("no_candidate_evaluation", result["candidate_evaluated"] is False, "candidate_evaluated=False")
        add("manual_unconfirmed", result["manual_confirmed"] is False, "manual_confirmed=False")
        permission_fields = (
            "official_dataset_write_allowed",
            "official_append_allowed",
            "signal_generation_enabled",
            "live_alerts_allowed",
            "paper_trade_execution_allowed",
            "real_capital_allowed",
            "market_execution_allowed",
            "exchange_execution_allowed",
            "automation_allowed",
            "execution_allowed",
        )
        add("all_permissions_false", all(metadata[field] is False for field in permission_fields), "all false")

    module_path = repo / "src/exchange/long_primary_public_closed_candle_capture_v1.py"
    tree = ast.parse(module_path.read_text(encoding="utf-8"))
    called_names: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                called_names.append(node.func.id)
            elif isinstance(node.func, ast.Attribute):
                called_names.append(node.func.attr)
    add("official_writer_not_called", "append_official_prospective_evidence" not in called_names, "absent")
    add("review_package_function_not_called", "prepare_real_source_review_package" not in called_names, "absent")
    source_text = module_path.read_text(encoding="utf-8")
    add("official_gate_not_referenced", "TRADING_AI_OFFICIAL_LONG_EVIDENCE_APPEND_ALLOWED" not in source_text, "absent")

    status_after = git_status(repo)
    dataset_after = sha256_path(dataset)
    manifest_after = sha256_path(manifest)
    add("repository_unchanged", status_before == status_after, f"before={status_before};after={status_after}")
    add("official_artifacts_unchanged", dataset_before == dataset_after and manifest_before == manifest_after, "unchanged")

    failed = [check for check in checks if not check["passed"]]
    summary = {
        "capability": "LONG_PRIMARY_PUBLIC_CLOSED_CANDLE_CAPTURE_V1",
        "decision": REPORT_DECISION,
        "checks": len(checks),
        "failed_checks": len(failed),
        "blockers": sum(1 for check in failed if check["blocker"]),
        "check_results": checks,
        "mocked_network_request_count": 1,
        "real_network_request_executed": False,
        "real_market_data_acquired": False,
        "real_capture_created": False,
        "review_package_created": False,
        "candidate_evaluated": False,
        "official_append_invoked": False,
        "official_dataset_changed": False,
        "official_manifest_changed": False,
        "all_execution_permissions_false": True,
    }
    print(json.dumps(summary, indent=2, sort_keys=True))
    if failed:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
