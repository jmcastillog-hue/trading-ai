from __future__ import annotations

import unittest
from typing import Any, Mapping

from src.integration.local_auxiliary_model_routing_v1 import (
    LOCAL_MODEL,
    ROUTE_LOCAL_OLLAMA,
    ROUTE_MODEL_PRINCIPAL,
    ROUTE_PYTHON_TEMPLATE,
    RoutingFailure,
    build_ollama_request,
    execute_request,
    parse_request_bytes,
)


class FakeClient:
    def __init__(self, output: Mapping[str, Any] | None = None):
        self.called = False
        self.output = dict(output or {"result": "Texto corregido."})

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


def request(task_type: str, payload: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "task_type": task_type,
        "payload": dict(payload),
        "max_output_tokens": 96,
        "human_review_required": True,
        "allow_external_action": False,
        "allow_actionable_trading_fields": False,
    }


class LocalAuxiliaryModelRoutingV1Tests(unittest.TestCase):
    def test_template_route_uses_zero_tokens(self):
        response = execute_request(
            request(
                "BUILD_VALIDATED_STATUS_MESSAGE",
                {
                    "title": "Trading-AI",
                    "status": "Validado",
                    "evidence_rows": 0,
                },
            )
        )
        self.assertEqual(response["route"], ROUTE_PYTHON_TEMPLATE)
        self.assertEqual(response["model_tokens_used"], 0)
        self.assertFalse(response["local_model_called"])
        self.assertIn("Ejecución: no permitida.", response["output"])

    def test_low_risk_task_uses_local_model(self):
        client = FakeClient()
        response = execute_request(
            request("REWRITE_MESSAGE", {"text": "Texto validado."}),
            client=client,
        )
        self.assertEqual(response["route"], ROUTE_LOCAL_OLLAMA)
        self.assertTrue(client.called)
        self.assertTrue(response["restrictions"]["human_review_required"])
        self.assertFalse(response["restrictions"]["message_send_allowed"])

    def test_critical_task_requires_principal_without_local_call(self):
        client = FakeClient()
        response = execute_request(
            request("TRADING_DECISION", {"context": "Contexto."}),
            client=client,
        )
        self.assertEqual(response["route"], ROUTE_MODEL_PRINCIPAL)
        self.assertEqual(response["principal_model_name"], "openai/gpt-5.6-sol")
        self.assertFalse(client.called)

    def test_external_action_permission_is_rejected(self):
        value = request("REWRITE_MESSAGE", {"text": "Texto."})
        value["allow_external_action"] = True
        with self.assertRaises(RoutingFailure):
            execute_request(value, client=FakeClient())

    def test_actionable_trading_permission_is_rejected(self):
        value = request("REWRITE_MESSAGE", {"text": "Texto."})
        value["allow_actionable_trading_fields"] = True
        with self.assertRaises(RoutingFailure):
            execute_request(value, client=FakeClient())

    def test_forbidden_actionable_payload_key_is_rejected(self):
        with self.assertRaises(RoutingFailure):
            execute_request(
                request(
                    "REWRITE_MESSAGE",
                    {"text": "Texto.", "entry_price": 100.0},
                ),
                client=FakeClient(),
            )

    def test_unknown_task_is_rejected(self):
        with self.assertRaises(RoutingFailure):
            execute_request(
                request("UNKNOWN_TASK", {"text": "Texto."}),
                client=FakeClient(),
            )

    def test_ollama_request_disables_thinking_and_tools(self):
        body = build_ollama_request(
            task_type="REWRITE_MESSAGE",
            payload={"text": "Texto validado."},
            max_output_tokens=96,
        )
        self.assertFalse(body["think"])
        self.assertFalse(body["stream"])
        self.assertEqual(body["format"], "json")
        self.assertNotIn("tools", body)
        self.assertEqual(body["model"], LOCAL_MODEL)
        self.assertEqual(body["options"]["num_ctx"], 4096)

    def test_classification_output_is_limited_to_supplied_labels(self):
        client = FakeClient({"label": "URGENTE"})
        response = execute_request(
            request(
                "CLASSIFY_TEXT",
                {
                    "text": "Mensaje.",
                    "labels": ["NORMAL", "URGENTE"],
                },
            ),
            client=client,
        )
        self.assertEqual(response["output"]["label"], "URGENTE")

    def test_invalid_classification_output_fails_closed(self):
        client = FakeClient({"label": "INVENTADA"})
        with self.assertRaises(RoutingFailure):
            # Fake clients are trusted test doubles, so validate through the
            # production output validator by using a malformed local response
            # in the request path is covered separately in validation tests.
            from src.integration.local_auxiliary_model_routing_v1 import (
                validate_model_output,
            )
            validate_model_output(
                "CLASSIFY_TEXT",
                {"text": "Mensaje.", "labels": ["NORMAL", "URGENTE"]},
                client.output,
            )

    def test_strict_request_parser_rejects_duplicate_fields(self):
        payload = (
            b'{"task_type":"REWRITE_MESSAGE","task_type":"REWRITE_MESSAGE",'
            b'"payload":{"text":"x"},"max_output_tokens":96,'
            b'"human_review_required":true,"allow_external_action":false,'
            b'"allow_actionable_trading_fields":false}'
        )
        with self.assertRaises(RoutingFailure):
            parse_request_bytes(payload)


if __name__ == "__main__":
    unittest.main()
