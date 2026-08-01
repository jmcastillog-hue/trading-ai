from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Mapping

from src.integration.local_auxiliary_model_routing_v1 import (
    LOCAL_MODEL,
    OLLAMA_CHAT_PATH,
    OLLAMA_HOST,
    OLLAMA_PORT,
    RESTRICTIONS,
    ROUTE_LOCAL_OLLAMA,
    ROUTE_MODEL_PRINCIPAL,
    ROUTE_PYTHON_TEMPLATE,
    OllamaLocalClient,
    RoutingFailure,
    build_ollama_request,
    execute_request,
)


PHASE = "11.3"
VALIDATION_SCHEMA_VERSION = "LOCAL_AUXILIARY_MODEL_ROUTING_VALIDATION_V1"
VALIDATED_DECISION = "PHASE_11_3_LOCAL_AUXILIARY_MODEL_ROUTING_VALIDATED"
FAILED_DECISION = "PHASE_11_3_LOCAL_AUXILIARY_MODEL_ROUTING_FAILED"
NEXT_PHASE = "PHASE_11_4_OPENCLAW_CONTROLLED_LOCAL_UTILITY_CONNECTION_V1"

DOC_PATH = Path("docs/PHASE_11_3_LOCAL_AUXILIARY_MODEL_ROUTING_V1.md")
SCHEMA_PATH = Path("schemas/local_auxiliary_model_request_v1.schema.json")
ROUTER_PATH = Path("src/integration/local_auxiliary_model_routing_v1.py")
RUNNER_PATH = Path("src/workflows/run_local_auxiliary_model_routing_v1.py")
TEST_PATH = Path("tests/test_local_auxiliary_model_routing_v1.py")
README_PATH = Path("README.md")
EVIDENCE_PATH = Path(
    "reports/phase_11_3/first_controlled_local_auxiliary_model_execution.json"
)

MOJIBAKE_MARKERS = ("â€“", "â†’", "â†“", "Ã—")


class FakeClient:
    def __init__(self, output: Mapping[str, Any] | None = None):
        self.called = False
        self.output = dict(output or {"result": "Mensaje local validado."})

    def model_available(self, model_name: str = LOCAL_MODEL) -> bool:
        return model_name == LOCAL_MODEL

    def chat(
        self,
        *,
        task_type: str,
        payload: Mapping[str, Any],
        max_output_tokens: int,
    ) -> dict[str, Any]:
        self.called = True
        return {
            "output": dict(self.output),
            "metrics": {
                "total_duration_ns": 1,
                "prompt_tokens": 10,
                "output_tokens": 5,
            },
            "request_policy": {
                "endpoint": f"http://{OLLAMA_HOST}:{OLLAMA_PORT}{OLLAMA_CHAT_PATH}",
                "think": False,
                "stream": False,
                "num_ctx": 4096,
                "num_predict": max_output_tokens,
                "temperature": 0,
                "keep_alive": "2m",
                "tools_present": False,
            },
        }


def add_check(
    checks: list[dict[str, Any]],
    name: str,
    passed: bool,
    details: str = "",
    *,
    blocker: bool = True,
) -> None:
    checks.append(
        {
            "check_name": name,
            "passed": bool(passed),
            "blocker": bool(blocker and not passed),
            "details": details,
        }
    )


def sample_request(
    task_type: str,
    payload: Mapping[str, Any],
    max_output_tokens: int = 96,
) -> dict[str, Any]:
    return {
        "task_type": task_type,
        "payload": dict(payload),
        "max_output_tokens": max_output_tokens,
        "human_review_required": True,
        "allow_external_action": False,
        "allow_actionable_trading_fields": False,
    }


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def write_evidence(evidence: Mapping[str, Any], root: Path) -> None:
    path = root / EVIDENCE_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            evidence,
            indent=2,
            sort_keys=True,
            ensure_ascii=True,
        )
        + "\n",
        encoding="utf-8",
        newline="\n",
    )


def validate_phase_11_3(
    *,
    root: Path | str = Path("."),
    live_ollama: bool = False,
    write_live_evidence: bool = False,
) -> dict[str, Any]:
    root_path = Path(root).resolve()
    checks: list[dict[str, Any]] = []

    for name, path in (
        ("doc_exists", DOC_PATH),
        ("schema_exists", SCHEMA_PATH),
        ("router_exists", ROUTER_PATH),
        ("runner_exists", RUNNER_PATH),
        ("tests_exist", TEST_PATH),
        ("readme_exists", README_PATH),
    ):
        exists = (root_path / path).is_file()
        add_check(checks, name, exists, str(root_path / path))

    readme_text = ""
    if (root_path / README_PATH).is_file():
        readme_text = (root_path / README_PATH).read_text(encoding="utf-8")
    mojibake_found = [marker for marker in MOJIBAKE_MARKERS if marker in readme_text]
    add_check(
        checks,
        "readme_utf8_mojibake_absent",
        not mojibake_found,
        ",".join(mojibake_found),
    )
    add_check(
        checks,
        "readme_phase_11_3_status_present",
        "Phase 11.3 Local Auxiliary Model Routing" in readme_text,
    )

    template_response = execute_request(
        sample_request(
            "BUILD_VALIDATED_STATUS_MESSAGE",
            {
                "title": "Trading-AI",
                "status": "Dataset oficial disponible",
                "evidence_rows": 0,
            },
        )
    )
    add_check(
        checks,
        "template_route_selected",
        template_response.get("route") == ROUTE_PYTHON_TEMPLATE,
        str(template_response.get("route")),
    )
    add_check(
        checks,
        "template_zero_tokens",
        template_response.get("model_tokens_used") == 0
        and template_response.get("local_model_called") is False,
    )
    add_check(
        checks,
        "template_preserves_execution_block",
        "Ejecución: no permitida." in str(template_response.get("output", "")),
    )

    fake_client = FakeClient()
    local_response = execute_request(
        sample_request(
            "REWRITE_MESSAGE",
            {
                "text": (
                    "El dataset oficial está disponible. Tiene cero filas de evidencia. "
                    "La revisión humana es obligatoria. La ejecución no está permitida."
                )
            },
        ),
        client=fake_client,
    )
    add_check(
        checks,
        "local_route_selected",
        local_response.get("route") == ROUTE_LOCAL_OLLAMA,
        str(local_response.get("route")),
    )
    add_check(checks, "local_fake_client_called", fake_client.called)
    policy = local_response.get("local_request_policy", {})
    add_check(checks, "local_thinking_disabled", policy.get("think") is False)
    add_check(checks, "local_streaming_disabled", policy.get("stream") is False)
    add_check(checks, "local_tools_absent", policy.get("tools_present") is False)
    add_check(
        checks,
        "local_endpoint_is_loopback_only",
        policy.get("endpoint")
        == f"http://{OLLAMA_HOST}:{OLLAMA_PORT}{OLLAMA_CHAT_PATH}",
        str(policy.get("endpoint")),
    )

    critical_client = FakeClient()
    critical_response = execute_request(
        sample_request("TRADING_DECISION", {"context": "validated context"}),
        client=critical_client,
    )
    add_check(
        checks,
        "critical_route_requires_principal",
        critical_response.get("route") == ROUTE_MODEL_PRINCIPAL,
        str(critical_response.get("route")),
    )
    add_check(
        checks,
        "critical_route_does_not_call_local",
        critical_client.called is False
        and critical_response.get("local_model_called") is False,
    )
    add_check(
        checks,
        "principal_model_exact",
        critical_response.get("principal_model_name") == "openai/gpt-5.6-sol",
    )

    for restriction, expected in RESTRICTIONS.items():
        add_check(
            checks,
            f"restriction_{restriction}",
            local_response.get("restrictions", {}).get(restriction) is expected,
            str(local_response.get("restrictions", {}).get(restriction)),
        )

    negative_requests = [
        (
            "external_action_rejected",
            {
                **sample_request("REWRITE_MESSAGE", {"text": "Texto."}),
                "allow_external_action": True,
            },
        ),
        (
            "actionable_permission_rejected",
            {
                **sample_request("REWRITE_MESSAGE", {"text": "Texto."}),
                "allow_actionable_trading_fields": True,
            },
        ),
        (
            "missing_human_review_rejected",
            {
                **sample_request("REWRITE_MESSAGE", {"text": "Texto."}),
                "human_review_required": False,
            },
        ),
        (
            "actionable_payload_key_rejected",
            sample_request(
                "REWRITE_MESSAGE",
                {"text": "Texto.", "entry_price": 100.0},
            ),
        ),
        (
            "unknown_task_rejected",
            sample_request("UNKNOWN_TASK", {"text": "Texto."}),
        ),
    ]

    for name, request in negative_requests:
        rejected = False
        try:
            execute_request(request, client=FakeClient())
        except RoutingFailure:
            rejected = True
        add_check(checks, name, rejected)

    ollama_payload = build_ollama_request(
        task_type="REWRITE_MESSAGE",
        payload={"text": "Texto validado."},
        max_output_tokens=96,
    )
    add_check(checks, "ollama_payload_think_false", ollama_payload.get("think") is False)
    add_check(checks, "ollama_payload_stream_false", ollama_payload.get("stream") is False)
    add_check(
        checks,
        "ollama_payload_uses_json_mode",
        ollama_payload.get("format") == "json",
        str(ollama_payload.get("format")),
    )
    add_check(checks, "ollama_payload_has_no_tools", "tools" not in ollama_payload)
    add_check(
        checks,
        "ollama_payload_model_exact",
        ollama_payload.get("model") == LOCAL_MODEL,
    )
    add_check(
        checks,
        "ollama_payload_num_ctx_4096",
        ollama_payload.get("options", {}).get("num_ctx") == 4096,
    )

    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "src.workflows.run_local_auxiliary_model_routing_v1",
            "unexpected-argument",
        ],
        cwd=root_path,
        text=True,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    add_check(
        checks,
        "runner_extra_argument_fails_closed",
        completed.returncode == 20,
        str(completed.returncode),
    )

    live_evidence: dict[str, Any] | None = None
    if live_ollama:
        client = OllamaLocalClient()
        model_available = False
        try:
            model_available = client.model_available(LOCAL_MODEL)
        except RoutingFailure as exc:
            add_check(checks, "live_ollama_reachable", False, str(exc))
        else:
            add_check(checks, "live_ollama_reachable", True)
        add_check(
            checks,
            "live_local_model_available",
            model_available,
            LOCAL_MODEL,
        )

        if model_available:
            live_request = sample_request(
                "REWRITE_MESSAGE",
                {
                    "text": (
                        "El dataset oficial está disponible. Tiene cero filas de evidencia. "
                        "La revisión humana es obligatoria. La ejecución no está permitida."
                    )
                },
                max_output_tokens=96,
            )
            try:
                live_response = execute_request(live_request, client=client)
            except RoutingFailure as exc:
                add_check(checks, "live_local_execution_passed", False, str(exc))
            else:
                add_check(
                    checks,
                    "live_local_execution_passed",
                    live_response.get("route") == ROUTE_LOCAL_OLLAMA
                    and live_response.get("decision")
                    == "LOCAL_LANGUAGE_UTILITY_COMPLETED_FOR_HUMAN_REVIEW",
                    str(live_response.get("decision")),
                )
                live_output = live_response.get("output")
                add_check(
                    checks,
                    "live_local_output_structured",
                    isinstance(live_output, dict)
                    and isinstance(live_output.get("result"), str)
                    and bool(live_output["result"].strip()),
                )
                live_policy = live_response.get("local_request_policy", {})
                add_check(
                    checks,
                    "live_local_thinking_disabled",
                    live_policy.get("think") is False,
                )
                add_check(
                    checks,
                    "live_local_tools_absent",
                    live_policy.get("tools_present") is False,
                )
                metrics = live_response.get("local_metrics", {})
                add_check(
                    checks,
                    "live_local_output_token_limit",
                    isinstance(metrics.get("output_tokens"), int)
                    and metrics["output_tokens"] <= 96,
                    str(metrics.get("output_tokens")),
                )
                result_text = live_output.get("result", "")
                live_evidence = {
                    "evidence_schema_version": (
                        "PHASE_11_3_FIRST_CONTROLLED_LOCAL_AUXILIARY_MODEL_EXECUTION_V1"
                    ),
                    "phase": PHASE,
                    "decision": "FIRST_CONTROLLED_LOCAL_AUXILIARY_MODEL_EXECUTION_PASSED",
                    "model": LOCAL_MODEL,
                    "endpoint": f"http://{OLLAMA_HOST}:{OLLAMA_PORT}{OLLAMA_CHAT_PATH}",
                    "task_type": "REWRITE_MESSAGE",
                    "route": live_response.get("route"),
                    "think": False,
                    "stream": False,
                    "tools_present": False,
                    "human_review_required": True,
                    "external_action_allowed": False,
                    "browser_control_allowed": False,
                    "message_send_allowed": False,
                    "trading_execution_allowed": False,
                    "official_dataset_write_allowed": False,
                    "result_sha256": sha256_text(result_text),
                    "result_character_count": len(result_text),
                    "metrics": metrics,
                }

    failed_checks = sum(1 for check in checks if not check["passed"])
    blocker_count = sum(1 for check in checks if check["blocker"])
    validation_passed = failed_checks == 0 and blocker_count == 0

    if write_live_evidence:
        if live_evidence is None:
            add_check(
                checks,
                "live_evidence_available_for_write",
                False,
                "Live evidence was not produced",
            )
            failed_checks += 1
            blocker_count += 1
            validation_passed = False
        else:
            write_evidence(live_evidence, root_path)
            add_check(
                checks,
                "live_evidence_written",
                (root_path / EVIDENCE_PATH).is_file(),
                str(root_path / EVIDENCE_PATH),
            )

    return {
        "validation_schema_version": VALIDATION_SCHEMA_VERSION,
        "phase": PHASE,
        "validation_passed": validation_passed,
        "validation_decision": (
            VALIDATED_DECISION if validation_passed else FAILED_DECISION
        ),
        "total_checks": len(checks),
        "passed_checks": sum(1 for check in checks if check["passed"]),
        "failed_checks": sum(1 for check in checks if not check["passed"]),
        "blocker_count": sum(1 for check in checks if check["blocker"]),
        "live_ollama_required": live_ollama,
        "local_model": LOCAL_MODEL,
        "python_template_route_enabled": True,
        "local_ollama_route_enabled": True,
        "principal_model_escalation_enabled": True,
        "openclaw_runtime_connection_enabled": False,
        "browser_control_allowed": False,
        "message_send_allowed": False,
        "trading_execution_allowed": False,
        "official_dataset_write_allowed": False,
        "recommended_next_phase": NEXT_PHASE,
        "checks": checks,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--live-ollama", action="store_true")
    parser.add_argument("--write-evidence", action="store_true")
    args = parser.parse_args()

    result = validate_phase_11_3(
        live_ollama=args.live_ollama,
        write_live_evidence=args.write_evidence,
    )
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
