from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from src.integration.openclaw_controlled_read_only_research_workflow_v1 import (
    MODE_DETERMINISTIC,
    MODE_LOCAL_OLLAMA,
    OpenClawResearchWorkflowFailure,
    WORKFLOW_RESTRICTIONS,
    decode_workflow_request_token,
    encode_workflow_request_token,
    execute_workflow_request,
)


ROOT = Path(__file__).resolve().parents[2]
DOC_PATH = ROOT / "docs" / (
    "PHASE_11_5_OPENCLAW_CONTROLLED_READ_ONLY_RESEARCH_WORKFLOW_V1.md"
)
PROMPT_PATH = ROOT / "docs" / (
    "PHASE_11_5_FIRST_CONTROLLED_OPENCLAW_RESEARCH_WORKFLOW_PROMPT_V1.md"
)
SCHEMA_PATH = ROOT / "schemas" / (
    "openclaw_controlled_read_only_research_workflow_request_v1.schema.json"
)
EXAMPLE_PATH = ROOT / "examples" / (
    "phase_11_5_first_controlled_read_only_research_request_v1.json"
)
INTEGRATION_PATH = ROOT / "src" / "integration" / (
    "openclaw_controlled_read_only_research_workflow_v1.py"
)
RUNNER_PATH = ROOT / "src" / "workflows" / (
    "run_openclaw_controlled_read_only_research_workflow_v1.py"
)
TEST_PATH = ROOT / "tests" / (
    "test_openclaw_controlled_read_only_research_workflow_v1.py"
)

OFFICIAL_DATASET = ROOT / "data" / "forward" / (
    "long_forward_observation_dataset_v1.csv"
)
OFFICIAL_MANIFEST = ROOT / "data" / "forward" / (
    "long_forward_observation_dataset_v1.manifest.csv"
)

EXPECTED_REQUEST = {
    "workflow_request_schema_version": (
        "OPENCLAW_CONTROLLED_READ_ONLY_RESEARCH_WORKFLOW_REQUEST_V1"
    ),
    "request_id": "phase-11-5-first-controlled-research-summary-v1",
    "operation": "GET_AND_EXPLAIN_VALIDATED_RESEARCH_STATUS",
    "explanation_mode": "DETERMINISTIC_TEMPLATE",
    "max_output_tokens": 112,
    "human_review_required": True,
}


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check(
    rows: list[dict[str, Any]],
    name: str,
    passed: bool,
    details: str = "",
    blocker: bool = False,
) -> None:
    rows.append(
        {
            "check_name": name,
            "passed": bool(passed),
            "details": details,
            "blocker": bool(blocker and not passed),
        }
    )


def run_validation(live_ollama: bool) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []
    before_dataset = sha256_file(OFFICIAL_DATASET)
    before_manifest = sha256_file(OFFICIAL_MANIFEST)

    for name, path in (
        ("doc_exists", DOC_PATH),
        ("prompt_exists", PROMPT_PATH),
        ("schema_exists", SCHEMA_PATH),
        ("example_exists", EXAMPLE_PATH),
        ("integration_exists", INTEGRATION_PATH),
        ("runner_exists", RUNNER_PATH),
        ("tests_exist", TEST_PATH),
    ):
        check(checks, name, path.is_file(), str(path), blocker=True)

    example = json.loads(EXAMPLE_PATH.read_text(encoding="utf-8"))
    check(
        checks,
        "example_request_exact",
        example == EXPECTED_REQUEST,
    )
    token = encode_workflow_request_token(example)
    check(
        checks,
        "token_round_trip_exact",
        decode_workflow_request_token(token) == EXPECTED_REQUEST,
    )
    prompt = PROMPT_PATH.read_text(encoding="utf-8")
    check(
        checks,
        "prompt_contains_exact_token",
        token in prompt,
    )
    check(
        checks,
        "prompt_requires_one_exec_call",
        "Make exactly one tool call." in prompt
        and "Use only the `exec` tool." in prompt,
    )
    check(
        checks,
        "prompt_requires_foreground_wait",
        '"yieldMs": 120000' in prompt
        and '"timeout": 180' in prompt
        and "Do not use `process`." in prompt,
    )
    check(
        checks,
        "prompt_prohibits_external_tools",
        "Do not use browser" in prompt
        and "Do not send or deliver anything externally." in prompt,
    )

    deterministic_request = dict(EXPECTED_REQUEST)
    deterministic_request["request_id"] = "phase-11-5-validator-template-v1"
    deterministic_request["explanation_mode"] = MODE_DETERMINISTIC
    deterministic = execute_workflow_request(
        deterministic_request,
        root=ROOT,
    )
    check(
        checks,
        "deterministic_route_passed",
        deterministic["explanation_route"] == "PYTHON_TEMPLATE",
    )
    check(
        checks,
        "deterministic_uses_no_local_model",
        deterministic["local_model_called"] is False,
    )
    check(
        checks,
        "workflow_restrictions_exact",
        deterministic["restrictions"] == WORKFLOW_RESTRICTIONS,
        blocker=True,
    )
    check(
        checks,
        "official_dataset_state_current",
        deterministic["research_status"]["long_official_dataset_state"]
        == "INITIALIZED_EMPTY_READY_FOR_CONTROLLED_EVIDENCE",
        blocker=True,
    )
    check(
        checks,
        "official_evidence_rows_zero",
        deterministic["research_status"]["long_official_evidence_row_count"]
        == 0,
        blocker=True,
    )

    live_response: dict[str, Any] | None = None
    if live_ollama:
        live_request = dict(EXPECTED_REQUEST)
        live_request["request_id"] = (
            "phase-11-5-validator-local-v1"
        )
        live_request["explanation_mode"] = MODE_LOCAL_OLLAMA
        live_response = execute_workflow_request(
            live_request,
            root=ROOT,
        )
        check(
            checks,
            "live_local_route_passed",
            live_response["explanation_route"] == "LOCAL_OLLAMA",
            blocker=True,
        )
        check(
            checks,
            "live_local_model_called",
            live_response["local_model_called"] is True,
            blocker=True,
        )
        check(
            checks,
            "live_output_nonempty",
            bool(live_response["explanation_output"]["result"].strip()),
            blocker=True,
        )

    negative_controls = 0

    for mutation in (
        {"operation": "PLACE_ORDER"},
        {"human_review_required": False},
        {"explanation_mode": "TRADING_DECISION"},
        {"extra": True},
    ):
        candidate = dict(EXPECTED_REQUEST)
        candidate.update(mutation)
        try:
            encode_workflow_request_token(candidate)
        except OpenClawResearchWorkflowFailure:
            negative_controls += 1

    for bad_token in ("abc;whoami", "", "=", "%%%%"):
        try:
            decode_workflow_request_token(bad_token)
        except OpenClawResearchWorkflowFailure:
            negative_controls += 1

    check(
        checks,
        "negative_controls_passed",
        negative_controls == 8,
        f"{negative_controls}/8",
        blocker=True,
    )

    after_dataset = sha256_file(OFFICIAL_DATASET)
    after_manifest = sha256_file(OFFICIAL_MANIFEST)
    check(
        checks,
        "official_dataset_unchanged",
        before_dataset == after_dataset,
        before_dataset,
        blocker=True,
    )
    check(
        checks,
        "official_manifest_unchanged",
        before_manifest == after_manifest,
        before_manifest,
        blocker=True,
    )

    failed = sum(1 for row in checks if not row["passed"])
    blockers = sum(1 for row in checks if row["blocker"])

    return {
        "phase": "11.5",
        "validation_schema_version": (
            "PHASE_11_5_CONTROLLED_READ_ONLY_RESEARCH_WORKFLOW_"
            "VALIDATION_V1"
        ),
        "validation_passed": failed == 0 and blockers == 0,
        "decision": (
            "PHASE_11_5_OPENCLAW_CONTROLLED_READ_ONLY_RESEARCH_"
            "WORKFLOW_READY_FOR_CONTROLLED_OPENCLAW_EXECUTION"
            if failed == 0 and blockers == 0
            else "PHASE_11_5_VALIDATION_FAILED"
        ),
        "live_ollama_requested": live_ollama,
        "total_checks": len(checks),
        "failed_checks": failed,
        "blocker_count": blockers,
        "negative_controls_passed": negative_controls,
        "official_dataset_sha256": after_dataset,
        "official_manifest_sha256": after_manifest,
        "live_route": (
            live_response["explanation_route"]
            if live_response is not None
            else None
        ),
        "local_model_called": (
            live_response["local_model_called"]
            if live_response is not None
            else False
        ),
        "checks": checks,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--live-ollama", action="store_true")
    args = parser.parse_args()
    result = run_validation(args.live_ollama)
    print(
        json.dumps(
            result,
            indent=2,
            sort_keys=True,
            ensure_ascii=True,
            allow_nan=False,
        )
    )
    return 0 if result["validation_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
