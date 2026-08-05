from __future__ import annotations

import ast
import csv
import hashlib
import json
import os
import shutil
import subprocess
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from src.long_side.long_primary_prospective_observation_source_adapter_v1 import (
    CAPABILITY,
    REAL_SOURCE_AUTHORIZATION,
    SANDBOX_SOURCE_AUTHORIZATION,
    SOURCE_COLUMNS,
    SourceAdapterError,
    prepare_real_source_review_package,
    prepare_sandbox_validation_package,
    validate_review_package,
)


OFFICIAL_DATASET = Path(
    "data/forward/long_forward_observation_dataset_v1.csv"
)
OFFICIAL_MANIFEST = Path(
    "data/forward/long_forward_observation_dataset_v1.manifest.csv"
)
OFFICIAL_GATE = "TRADING_AI_OFFICIAL_LONG_EVIDENCE_APPEND_ALLOWED"
MODULE_PATH = Path(
    "src/long_side/long_primary_prospective_observation_source_adapter_v1.py"
)


class ValidationFailure(RuntimeError):
    pass


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValidationFailure(message)


def git_status() -> list[str]:
    completed = subprocess.run(
        ["git", "status", "--porcelain=v1", "--untracked-files=all"],
        text=True,
        capture_output=True,
        check=False,
        shell=False,
    )
    if completed.returncode != 0:
        raise ValidationFailure(completed.stderr.strip())
    return [
        line for line in completed.stdout.splitlines() if line.strip()
    ]


def build_rows(candidate: bool) -> list[dict[str, str]]:
    count = 60
    latest_close = datetime(2026, 8, 4, 20, 0, tzinfo=timezone.utc)
    first_open = latest_close - timedelta(minutes=15 * count)
    rows: list[dict[str, str]] = []
    for index in range(count):
        open_time = first_open + timedelta(minutes=15 * index)
        close_time = open_time + timedelta(minutes=15)
        rows.append(
            {
                "open_time_utc": open_time.isoformat(),
                "close_time_utc": close_time.isoformat(),
                "symbol": "BTCUSDT",
                "timeframe": "15m",
                "open": "100",
                "high": "102",
                "low": "99",
                "close": "101",
                "volume": "10",
                "candle_closed": "True",
            }
        )
    rows[-1].update(
        (
            {
                "open": "98.8",
                "high": "101",
                "low": "98",
                "close": "100",
            }
            if candidate
            else {
                "open": "100",
                "high": "101.5",
                "low": "99.2",
                "close": "100.5",
            }
        )
    )
    return rows


def write_source(path: Path, candidate: bool) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=list(SOURCE_COLUMNS),
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(build_rows(candidate))
    return sha256_path(path)


def main() -> int:
    root = Path.cwd().resolve()
    checks: list[dict[str, Any]] = []

    def add_check(name: str, passed: bool, details: str) -> None:
        checks.append(
            {
                "check": name,
                "passed": bool(passed),
                "details": details,
                "blocker": not bool(passed),
            }
        )

    require((root / ".git").is_dir(), "Repository root is invalid.")
    require((root / OFFICIAL_DATASET).is_file(), "Official dataset missing.")
    require((root / OFFICIAL_MANIFEST).is_file(), "Official manifest missing.")
    status_before = git_status()
    dataset_before = sha256_path(root / OFFICIAL_DATASET)
    manifest_before = sha256_path(root / OFFICIAL_MANIFEST)
    gate_before = os.environ.get(OFFICIAL_GATE)

    with tempfile.TemporaryDirectory(
        prefix="long_primary_source_adapter_validation_"
    ) as temp:
        external = Path(temp)
        sandbox_repo = external / "repo"
        sandbox_repo.mkdir()
        (sandbox_repo / ".git").mkdir()
        sandbox_forward = sandbox_repo / "data" / "forward"
        sandbox_forward.mkdir(parents=True)
        shutil.copy2(
            root / OFFICIAL_DATASET,
            sandbox_forward / OFFICIAL_DATASET.name,
        )
        shutil.copy2(
            root / OFFICIAL_MANIFEST,
            sandbox_forward / OFFICIAL_MANIFEST.name,
        )

        candidate_source = external / "candidate_source.csv"
        candidate_hash = write_source(candidate_source, True)
        candidate_output = external / "candidate_package"
        candidate_result = prepare_sandbox_validation_package(
            repo_root=sandbox_repo,
            source_csv=candidate_source,
            output_directory=candidate_output,
            captured_at_utc="2026-08-04T20:15:00+00:00",
            prospective_start_utc="2026-08-04T19:45:00+00:00",
            expected_source_sha256=candidate_hash,
            authorization=SANDBOX_SOURCE_AUTHORIZATION,
        )
        candidate_validation = validate_review_package(candidate_output)

        no_candidate_source = external / "no_candidate_source.csv"
        write_source(no_candidate_source, False)
        no_candidate_output = external / "no_candidate_package"
        no_candidate_result = prepare_sandbox_validation_package(
            repo_root=sandbox_repo,
            source_csv=no_candidate_source,
            output_directory=no_candidate_output,
            captured_at_utc="2026-08-04T20:15:00+00:00",
            prospective_start_utc="2026-08-04T19:45:00+00:00",
            authorization=SANDBOX_SOURCE_AUTHORIZATION,
        )

        production_rejected = False
        production_error_code = ""
        try:
            prepare_real_source_review_package(
                repo_root=sandbox_repo,
                source_csv=candidate_source,
                output_directory=external / "prohibited_real_package",
                captured_at_utc="2026-08-04T20:15:00+00:00",
                prospective_start_utc="2026-08-04T19:45:00+00:00",
                source_system="CONTROLLED_VALIDATION",
                source_capture_id="CONTROLLED_VALIDATION_CAPTURE",
                source_attestation="",
                authorization=REAL_SOURCE_AUTHORIZATION,
            )
        except SourceAdapterError as exc:
            production_rejected = True
            production_error_code = exc.code

        add_check(
            "sandbox_candidate_detected",
            candidate_result["candidate_detected"] is True,
            f"candidate_detected={candidate_result['candidate_detected']}",
        )
        add_check(
            "sandbox_candidate_row_created",
            candidate_result["candidate_rows_written"] == 1,
            f"rows={candidate_result['candidate_rows_written']}",
        )
        add_check(
            "sandbox_not_eligible_as_real",
            candidate_validation["eligible_for_real_human_review"] is False,
            (
                "eligible="
                f"{candidate_validation['eligible_for_real_human_review']}"
            ),
        )
        add_check(
            "latest_candle_only",
            candidate_result["latest_candle_only_evaluated"] is True,
            "latest_candle_only_evaluated=True",
        )
        add_check(
            "lookahead_disabled",
            candidate_result["lookahead_used"] is False,
            "lookahead_used=False",
        )
        add_check(
            "no_candidate_path",
            (
                no_candidate_result["candidate_detected"] is False
                and no_candidate_result["candidate_rows_written"] == 0
            ),
            (
                f"detected={no_candidate_result['candidate_detected']};"
                f"rows={no_candidate_result['candidate_rows_written']}"
            ),
        )
        add_check(
            "manual_confirmation_false",
            candidate_result["manual_confirmed"] is False,
            "manual_confirmed=False",
        )
        add_check(
            "official_dataset_write_false",
            candidate_result["official_dataset_write_performed"] is False,
            "official_dataset_write_performed=False",
        )
        add_check(
            "official_manifest_write_false",
            candidate_result["official_manifest_write_performed"] is False,
            "official_manifest_write_performed=False",
        )
        add_check(
            "all_execution_permissions_false",
            all(
                candidate_result[field] is False
                for field in (
                    "paper_trade_execution_allowed",
                    "real_capital_allowed",
                    "market_execution_allowed",
                    "exchange_execution_allowed",
                    "automation_allowed",
                    "execution_allowed",
                )
            ),
            "all execution permissions remain false",
        )
        add_check(
            "real_source_requires_attestation",
            (
                production_rejected
                and production_error_code
                == "REAL_SOURCE_ATTESTATION_REQUIRED"
            ),
            f"error_code={production_error_code}",
        )
        add_check(
            "review_manifest_valid",
            candidate_validation["manifest_entries"] == 4,
            (
                "manifest_entries="
                f"{candidate_validation['manifest_entries']}"
            ),
        )

    module_text = (root / MODULE_PATH).read_text(encoding="utf-8")
    module_tree = ast.parse(module_text, filename=str(MODULE_PATH))
    forbidden_calls: list[int] = []
    for node in ast.walk(module_tree):
        if not isinstance(node, ast.Call):
            continue
        name = ""
        if isinstance(node.func, ast.Name):
            name = node.func.id
        elif isinstance(node.func, ast.Attribute):
            name = node.func.attr
        if name == "append_official_prospective_evidence":
            forbidden_calls.append(node.lineno)
    add_check(
        "no_official_writer_call",
        not forbidden_calls,
        f"forbidden_call_lines={forbidden_calls}",
    )
    add_check(
        "official_gate_not_referenced",
        OFFICIAL_GATE not in module_text,
        "official append environment gate is not referenced",
    )

    dataset_after = sha256_path(root / OFFICIAL_DATASET)
    manifest_after = sha256_path(root / OFFICIAL_MANIFEST)
    status_after = git_status()
    gate_after = os.environ.get(OFFICIAL_GATE)

    add_check(
        "official_artifacts_unchanged",
        (
            dataset_after == dataset_before
            and manifest_after == manifest_before
        ),
        (
            f"dataset_same={dataset_after == dataset_before};"
            f"manifest_same={manifest_after == manifest_before}"
        ),
    )
    add_check(
        "repository_unchanged",
        status_after == status_before,
        (
            f"status_before={status_before};"
            f"status_after={status_after}"
        ),
    )
    add_check(
        "environment_gate_unchanged",
        gate_after == gate_before and gate_after != "1",
        f"before={gate_before!r};after={gate_after!r}",
    )

    failed = [check for check in checks if not check["passed"]]
    result = {
        "capability": CAPABILITY,
        "decision": (
            "LONG_PRIMARY_PROSPECTIVE_OBSERVATION_SOURCE_ADAPTER_"
            "V1_VALIDATED_NON_WRITING"
            if not failed
            else
            "LONG_PRIMARY_PROSPECTIVE_OBSERVATION_SOURCE_ADAPTER_"
            "V1_VALIDATION_FAILED"
        ),
        "checks": len(checks),
        "failed_checks": len(failed),
        "blockers": sum(1 for check in failed if check["blocker"]),
        "check_results": checks,
        "sandbox_candidate_rows": 1,
        "sandbox_no_candidate_rows": 0,
        "production_path_tested_with_controlled_fixture": False,
        "real_source_package_created": False,
        "official_append_invoked": False,
        "official_append_environment_gate_modified": False,
        "official_dataset_changed": dataset_after != dataset_before,
        "official_manifest_changed": manifest_after != manifest_before,
        "files_modified": status_after != status_before,
        "manual_confirmation_required": True,
        "manual_confirmed": False,
        "paper_trade_execution_allowed": False,
        "real_capital_allowed": False,
        "market_execution_allowed": False,
        "exchange_execution_allowed": False,
        "automation_allowed": False,
        "execution_allowed": False,
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    if failed:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
