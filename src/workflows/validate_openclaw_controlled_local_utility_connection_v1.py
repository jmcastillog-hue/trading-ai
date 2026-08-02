from __future__ import annotations

import argparse
import base64
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

from src.integration.openclaw_controlled_local_utility_connection_v1 import (
    CONNECTION_RESTRICTIONS,
    CONNECTION_SCHEMA_VERSION,
    REQUEST_SCHEMA_VERSION,
    decode_request_token,
    encode_request_token,
)


PHASE = "11.4"
VALIDATION_SCHEMA_VERSION = (
    "OPENCLAW_CONTROLLED_LOCAL_UTILITY_CONNECTION_VALIDATION_V1"
)
READY_DECISION = (
    "PHASE_11_4_OPENCLAW_CONTROLLED_LOCAL_UTILITY_CONNECTION_READY"
)
FAILED_DECISION = (
    "PHASE_11_4_OPENCLAW_CONTROLLED_LOCAL_UTILITY_CONNECTION_FAILED"
)

WORKFLOW_MODULE = "src.workflows.run_openclaw_controlled_local_utility_connection_v1"
EXPECTED_PYTHON = r"C:\Users\jmcas\OpenClawProjects\trading-ai\.venv\Scripts\python.exe"
EXPECTED_WORKDIR = Path(r"C:\Users\jmcas\OpenClawProjects\trading-ai")
EXPECTED_SAMPLE_TOKEN = "eyJjb25uZWN0aW9uX3JlcXVlc3Rfc2NoZW1hX3ZlcnNpb24iOiJPUEVOQ0xBV19DT05UUk9MTEVEX0xPQ0FMX1VUSUxJVFlfUkVRVUVTVF9WMSIsImh1bWFuX3Jldmlld19yZXF1aXJlZCI6dHJ1ZSwibWF4X291dHB1dF90b2tlbnMiOjk2LCJwYXlsb2FkIjp7InRleHQiOiJFbCBkYXRhc2V0IG9maWNpYWwgZXN0XHUwMGUxIGRpc3BvbmlibGUgeSBjb250aWVuZSBjZXJvIGZpbGFzIGRlIGV2aWRlbmNpYS4gTGEgcmV2aXNpXHUwMGYzbiBodW1hbmEgZXMgb2JsaWdhdG9yaWEgeSBsYSBlamVjdWNpXHUwMGYzbiBvcGVyYXRpdmEgbm8gZXN0XHUwMGUxIHBlcm1pdGlkYS4ifSwicmVxdWVzdF9pZCI6InBoYXNlLTExLTQtZmlyc3QtY29udHJvbGxlZC1yZXdyaXRlLXYxIiwidGFza190eXBlIjoiUkVXUklURV9NRVNTQUdFIn0"
EXPECTED_COMMAND = r"C:\Users\jmcas\OpenClawProjects\trading-ai\.venv\Scripts\python.exe -m src.workflows.run_openclaw_controlled_local_utility_connection_v1 eyJjb25uZWN0aW9uX3JlcXVlc3Rfc2NoZW1hX3ZlcnNpb24iOiJPUEVOQ0xBV19DT05UUk9MTEVEX0xPQ0FMX1VUSUxJVFlfUkVRVUVTVF9WMSIsImh1bWFuX3Jldmlld19yZXF1aXJlZCI6dHJ1ZSwibWF4X291dHB1dF90b2tlbnMiOjk2LCJwYXlsb2FkIjp7InRleHQiOiJFbCBkYXRhc2V0IG9maWNpYWwgZXN0XHUwMGUxIGRpc3BvbmlibGUgeSBjb250aWVuZSBjZXJvIGZpbGFzIGRlIGV2aWRlbmNpYS4gTGEgcmV2aXNpXHUwMGYzbiBodW1hbmEgZXMgb2JsaWdhdG9yaWEgeSBsYSBlamVjdWNpXHUwMGYzbiBvcGVyYXRpdmEgbm8gZXN0XHUwMGUxIHBlcm1pdGlkYS4ifSwicmVxdWVzdF9pZCI6InBoYXNlLTExLTQtZmlyc3QtY29udHJvbGxlZC1yZXdyaXRlLXYxIiwidGFza190eXBlIjoiUkVXUklURV9NRVNTQUdFIn0"
TOKEN_PATTERN = re.compile(r"^[A-Za-z0-9_-]+$")

DOC_PATH = Path(
    "docs/PHASE_11_4_OPENCLAW_CONTROLLED_LOCAL_UTILITY_CONNECTION_V1.md"
)
PROMPT_PATH = Path(
    "docs/PHASE_11_4_FIRST_CONTROLLED_OPENCLAW_PROMPT_V1.md"
)
SCHEMA_PATH = Path(
    "schemas/openclaw_controlled_local_utility_request_v1.schema.json"
)
INTEGRATION_PATH = Path(
    "src/integration/openclaw_controlled_local_utility_connection_v1.py"
)
RUNNER_PATH = Path(
    "src/workflows/run_openclaw_controlled_local_utility_connection_v1.py"
)
TEST_PATH = Path(
    "tests/test_openclaw_controlled_local_utility_connection_v1.py"
)
EXAMPLE_REQUEST_PATH = Path(
    "examples/phase_11_4_first_controlled_local_utility_request_v1.json"
)

OFFICIAL_DATASET_PATH = Path(
    "data/forward/long_forward_observation_dataset_v1.csv"
)
OFFICIAL_MANIFEST_PATH = Path(
    "data/forward/long_forward_observation_dataset_v1.manifest.csv"
)

ACTIONABLE_KEYS = {
    "entry",
    "entry_price",
    "stop",
    "stop_loss",
    "target",
    "take_profit",
    "position_size",
    "quantity",
    "leverage",
    "side",
    "signal",
    "order",
    "exchange_command",
    "browser_command",
    "recipient",
    "destination",
}


def add_check(
    checks: list[dict[str, Any]],
    name: str,
    passed: bool,
    details: str = "",
) -> None:
    checks.append(
        {
            "check_name": name,
            "passed": bool(passed),
            "blocker": bool(not passed),
            "details": details,
        }
    )


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def contains_actionable_key(value: Any) -> bool:
    if isinstance(value, dict):
        for key, child in value.items():
            if key in ACTIONABLE_KEYS or contains_actionable_key(child):
                return True
    elif isinstance(value, list):
        return any(contains_actionable_key(child) for child in value)
    return False


def validate_phase_11_4(
    *,
    root: Path | str = Path("."),
    live_ollama: bool = False,
) -> dict[str, Any]:
    root_path = Path(root).resolve()
    checks: list[dict[str, Any]] = []

    for name, relative in (
        ("doc_exists", DOC_PATH),
        ("prompt_exists", PROMPT_PATH),
        ("schema_exists", SCHEMA_PATH),
        ("integration_exists", INTEGRATION_PATH),
        ("runner_exists", RUNNER_PATH),
        ("tests_exist", TEST_PATH),
        ("example_request_exists", EXAMPLE_REQUEST_PATH),
    ):
        add_check(
            checks,
            name,
            (root_path / relative).is_file(),
            str(root_path / relative),
        )

    example_request = json.loads(
        (root_path / EXAMPLE_REQUEST_PATH).read_text(encoding="utf-8")
    )
    sample_token = encode_request_token(example_request)
    add_check(
        checks,
        "sample_request_schema_exact",
        example_request.get("connection_request_schema_version")
        == REQUEST_SCHEMA_VERSION,
    )
    add_check(
        checks,
        "sample_token_exact",
        sample_token == EXPECTED_SAMPLE_TOKEN,
        sample_token,
    )
    add_check(
        checks,
        "sample_token_safe_characters_only",
        TOKEN_PATTERN.fullmatch(sample_token) is not None,
    )
    add_check(
        checks,
        "sample_token_round_trip",
        decode_request_token(sample_token) == example_request,
    )

    doc_text = (root_path / DOC_PATH).read_text(encoding="utf-8")
    prompt_text = (root_path / PROMPT_PATH).read_text(encoding="utf-8")
    add_check(
        checks,
        "doc_contains_exact_command",
        EXPECTED_COMMAND in doc_text,
    )
    add_check(
        checks,
        "prompt_contains_exact_command",
        EXPECTED_COMMAND in prompt_text,
    )
    add_check(
        checks,
        "prompt_requires_one_exec_call",
        "Make exactly one tool call." in prompt_text
        and "Use only the `exec` tool." in prompt_text,
    )
    add_check(
        checks,
        "prompt_requires_foreground_wait",
        '"yieldMs": 120000' in prompt_text
        and '"timeout": 180' in prompt_text
        and "do not use `process`" in prompt_text.lower(),
    )
    add_check(
        checks,
        "prompt_prohibits_delivery",
        "Do not deliver or send" in prompt_text,
    )
    add_check(
        checks,
        "prompt_prohibits_retries",
        "Do not retry" in prompt_text,
    )

    dataset_path = root_path / OFFICIAL_DATASET_PATH
    manifest_path = root_path / OFFICIAL_MANIFEST_PATH
    dataset_before = sha256_file(dataset_path)
    manifest_before = sha256_file(manifest_path)

    if live_ollama:
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                WORKFLOW_MODULE,
                sample_token,
            ],
            cwd=root_path,
            text=True,
            encoding="utf-8",
            errors="replace",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        add_check(
            checks,
            "live_runner_exit_zero",
            completed.returncode == 0,
            str(completed.returncode),
        )
        add_check(
            checks,
            "live_runner_stderr_empty",
            completed.stderr == "",
            completed.stderr[:1000],
        )
        response: dict[str, Any] = {}
        try:
            parsed = json.loads(completed.stdout)
            if isinstance(parsed, dict):
                response = parsed
                json_ok = True
            else:
                json_ok = False
        except json.JSONDecodeError:
            json_ok = False
        add_check(checks, "live_runner_stdout_valid_json", json_ok)
        add_check(
            checks,
            "live_connection_schema_exact",
            response.get("connection_schema_version")
            == CONNECTION_SCHEMA_VERSION,
            str(response.get("connection_schema_version")),
        )
        add_check(
            checks,
            "live_decision_expected",
            response.get("decision")
            == "OPENCLAW_CONTROLLED_LOCAL_UTILITY_COMPLETED_FOR_HUMAN_REVIEW",
            str(response.get("decision")),
        )
        add_check(
            checks,
            "live_delegated_route_local",
            response.get("delegated_route") == "LOCAL_OLLAMA",
            str(response.get("delegated_route")),
        )
        add_check(
            checks,
            "live_local_model_called",
            response.get("local_model_called") is True,
        )
        add_check(
            checks,
            "live_request_id_exact",
            response.get("request_id")
            == "phase-11-4-first-controlled-rewrite-v1",
            str(response.get("request_id")),
        )
        add_check(
            checks,
            "live_output_structured",
            isinstance(response.get("output"), dict)
            and isinstance(response["output"].get("result"), str)
            and bool(response["output"]["result"].strip()),
        )
        add_check(
            checks,
            "live_actionable_fields_absent",
            not contains_actionable_key(response),
        )
        for key, expected in CONNECTION_RESTRICTIONS.items():
            add_check(
                checks,
                f"live_restriction_{key}",
                response.get("restrictions", {}).get(key) is expected,
                str(response.get("restrictions", {}).get(key)),
            )

    missing_arg = subprocess.run(
        [sys.executable, "-m", WORKFLOW_MODULE],
        cwd=root_path,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    add_check(
        checks,
        "missing_argument_fails_closed",
        missing_arg.returncode == 20
        and missing_arg.stdout == ""
        and missing_arg.stderr == "",
        str(missing_arg.returncode),
    )

    extra_arg = subprocess.run(
        [
            sys.executable,
            "-m",
            WORKFLOW_MODULE,
            sample_token,
            "extra",
        ],
        cwd=root_path,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    add_check(
        checks,
        "extra_argument_fails_closed",
        extra_arg.returncode == 20,
        str(extra_arg.returncode),
    )

    invalid_token = subprocess.run(
        [
            sys.executable,
            "-m",
            WORKFLOW_MODULE,
            "bad;token",
        ],
        cwd=root_path,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    add_check(
        checks,
        "shell_metacharacter_token_fails_closed",
        invalid_token.returncode != 0
        and invalid_token.stdout == ""
        and "FAILED_CLOSED" in invalid_token.stderr,
        str(invalid_token.returncode),
    )

    critical_request = dict(example_request)
    critical_request["request_id"] = "phase-11-4-critical-negative-v1"
    critical_request["task_type"] = "TRADING_DECISION"
    critical_request["payload"] = {"context": "Contexto."}
    canonical = json.dumps(
        critical_request,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("utf-8")
    critical_token = base64.urlsafe_b64encode(canonical).decode("ascii").rstrip("=")
    critical = subprocess.run(
        [sys.executable, "-m", WORKFLOW_MODULE, critical_token],
        cwd=root_path,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    add_check(
        checks,
        "critical_task_fails_closed",
        critical.returncode == 22
        and critical.stdout == ""
        and "TASK_NOT_ALLOWED" in critical.stderr,
        str(critical.returncode),
    )

    add_check(
        checks,
        "official_dataset_unchanged",
        sha256_file(dataset_path) == dataset_before,
        dataset_before,
    )
    add_check(
        checks,
        "official_manifest_unchanged",
        sha256_file(manifest_path) == manifest_before,
        manifest_before,
    )

    failed_checks = sum(1 for check in checks if not check["passed"])
    blocker_count = sum(1 for check in checks if check["blocker"])
    passed = failed_checks == 0 and blocker_count == 0

    return {
        "validation_schema_version": VALIDATION_SCHEMA_VERSION,
        "phase": PHASE,
        "validation_passed": passed,
        "validation_decision": READY_DECISION if passed else FAILED_DECISION,
        "total_checks": len(checks),
        "passed_checks": sum(1 for check in checks if check["passed"]),
        "failed_checks": failed_checks,
        "blocker_count": blocker_count,
        "live_ollama_required": live_ollama,
        "direct_local_connection_validated": bool(live_ollama and passed),
        "openclaw_controlled_execution_completed": False,
        "authorized_workflow_module": WORKFLOW_MODULE,
        "authorized_command": EXPECTED_COMMAND,
        "expected_openclaw_tool": "exec",
        "expected_openclaw_tool_call_count": 1,
        "browser_control_allowed": False,
        "message_send_allowed": False,
        "trading_execution_allowed": False,
        "official_dataset_write_allowed": False,
        "automation_allowed": False,
        "next_action": "FIRST_CONTROLLED_OPENCLAW_LOCAL_UTILITY_EXECUTION_V1",
        "checks": checks,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--live-ollama", action="store_true")
    args = parser.parse_args()

    result = validate_phase_11_4(live_ollama=args.live_ollama)
    print(
        json.dumps(
            result,
            indent=2,
            sort_keys=True,
            ensure_ascii=True,
        )
    )
    return 0 if result["validation_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
