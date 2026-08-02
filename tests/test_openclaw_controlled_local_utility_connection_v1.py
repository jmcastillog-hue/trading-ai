from __future__ import annotations

import base64
import subprocess
import sys
import unittest
from pathlib import Path
from typing import Any, Mapping

from src.integration.openclaw_controlled_local_utility_connection_v1 import (
    CONNECTION_RESTRICTIONS,
    REQUEST_SCHEMA_VERSION,
    OpenClawLocalUtilityFailure,
    decode_request_token,
    encode_request_token,
    execute_connection_request,
    execute_request_token,
)


class FakeClient:
    def __init__(self, output: Mapping[str, Any] | None = None):
        self.called = False
        self.output = dict(output or {"result": "Texto local validado."})

    def model_available(self, model_name: str = "trading-ai-local-fast") -> bool:
        return True

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
                "endpoint": "http://127.0.0.1:11434/api/chat",
                "think": False,
                "stream": False,
                "num_ctx": 4096,
                "num_predict": max_output_tokens,
                "temperature": 0,
                "keep_alive": "2m",
                "tools_present": False,
            },
        }


def request(
    task_type: str = "REWRITE_MESSAGE",
    payload: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "connection_request_schema_version": REQUEST_SCHEMA_VERSION,
        "request_id": "phase-11-4-unit-test-v1",
        "task_type": task_type,
        "payload": dict(payload or {"text": "Texto validado."}),
        "max_output_tokens": 96,
        "human_review_required": True,
    }


class OpenClawControlledLocalUtilityConnectionV1Tests(unittest.TestCase):
    def test_token_round_trip_is_canonical(self):
        value = request()
        token = encode_request_token(value)
        self.assertNotIn("=", token)
        self.assertEqual(decode_request_token(token), value)

    def test_noncanonical_json_token_is_rejected(self):
        raw = (
            b'{"task_type":"REWRITE_MESSAGE",'
            b'"connection_request_schema_version":'
            b'"OPENCLAW_CONTROLLED_LOCAL_UTILITY_REQUEST_V1",'
            b'"request_id":"phase-11-4-unit-test-v1",'
            b'"payload":{"text":"Texto validado."},'
            b'"max_output_tokens":96,'
            b'"human_review_required":true}'
        )
        token = base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")
        with self.assertRaises(OpenClawLocalUtilityFailure):
            decode_request_token(token)

    def test_token_with_shell_metacharacter_is_rejected(self):
        with self.assertRaises(OpenClawLocalUtilityFailure):
            decode_request_token("abc;whoami")

    def test_unknown_field_is_rejected(self):
        value = request()
        value["allow_external_action"] = False
        with self.assertRaises(OpenClawLocalUtilityFailure):
            encode_request_token(value)

    def test_critical_task_is_rejected_before_router(self):
        client = FakeClient()
        with self.assertRaises(OpenClawLocalUtilityFailure):
            execute_connection_request(
                request(
                    "TRADING_DECISION",
                    {"context": "Contexto."},
                ),
                client=client,
            )
        self.assertFalse(client.called)

    def test_local_task_is_delegated(self):
        client = FakeClient()
        response = execute_connection_request(request(), client=client)
        self.assertTrue(client.called)
        self.assertEqual(response["delegated_route"], "LOCAL_OLLAMA")
        self.assertEqual(
            response["decision"],
            "OPENCLAW_CONTROLLED_LOCAL_UTILITY_COMPLETED_FOR_HUMAN_REVIEW",
        )
        self.assertTrue(response["local_model_called"])

    def test_template_task_uses_no_local_model(self):
        client = FakeClient()
        response = execute_connection_request(
            request(
                "BUILD_VALIDATED_STATUS_MESSAGE",
                {
                    "title": "Trading-AI",
                    "status": "Validado",
                    "evidence_rows": 0,
                },
            ),
            client=client,
        )
        self.assertFalse(client.called)
        self.assertEqual(response["delegated_route"], "PYTHON_TEMPLATE")
        self.assertFalse(response["local_model_called"])

    def test_all_connection_restrictions_are_preserved(self):
        response = execute_connection_request(
            request(),
            client=FakeClient(),
        )
        self.assertEqual(response["restrictions"], CONNECTION_RESTRICTIONS)
        self.assertTrue(
            response["restrictions"]["human_review_required"]
        )
        for key, value in response["restrictions"].items():
            if key != "human_review_required":
                self.assertFalse(value, key)

    def test_actionable_payload_key_fails_closed(self):
        token = encode_request_token(
            request(
                "REWRITE_MESSAGE",
                {
                    "text": "Texto.",
                    "entry_price": 100.0,
                },
            )
        )
        with self.assertRaises(OpenClawLocalUtilityFailure):
            execute_request_token(token, client=FakeClient())

    def test_runner_rejects_missing_token(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "src.workflows.run_openclaw_controlled_local_utility_connection_v1",
            ],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        self.assertEqual(completed.returncode, 20)
        self.assertEqual(completed.stdout, "")
        self.assertEqual(completed.stderr, "")

    def test_runner_rejects_extra_argument(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "src.workflows.run_openclaw_controlled_local_utility_connection_v1",
                "a",
                "b",
            ],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        self.assertEqual(completed.returncode, 20)

    def test_runner_invalid_token_fails_closed(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "src.workflows.run_openclaw_controlled_local_utility_connection_v1",
                "bad;token",
            ],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        self.assertNotEqual(completed.returncode, 0)
        self.assertEqual(completed.stdout, "")
        self.assertIn(
            "OPENCLAW_CONTROLLED_LOCAL_UTILITY_FAILED_CLOSED",
            completed.stderr,
        )

    def test_controlled_prompt_requires_foreground_wait(self):
        prompt_path = (
            Path(__file__).resolve().parents[1]
            / "docs"
            / "PHASE_11_4_FIRST_CONTROLLED_OPENCLAW_PROMPT_V1.md"
        )
        prompt = prompt_path.read_text(encoding="utf-8")
        self.assertIn('"yieldMs": 120000', prompt)
        self.assertIn('"timeout": 180', prompt)
        self.assertIn("do not use `process`", prompt.lower())


if __name__ == "__main__":
    unittest.main()
