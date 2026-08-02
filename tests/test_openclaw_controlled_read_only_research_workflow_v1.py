from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

from src.integration.openclaw_controlled_read_only_research_workflow_v1 import (
    MODE_DETERMINISTIC,
    MODE_LOCAL_OLLAMA,
    OpenClawResearchWorkflowFailure,
    WORKFLOW_RESTRICTIONS,
    decode_workflow_request_token,
    encode_workflow_request_token,
    execute_workflow_request,
    validate_workflow_request,
)


ROOT = Path(__file__).resolve().parents[1]
RUNNER_MODULE = (
    "src.workflows.run_openclaw_controlled_read_only_research_workflow_v1"
)


def valid_status() -> dict:
    return {
        "connection_schema_version": "OPENCLAW_READ_ONLY_LOCAL_CONNECTION_V1",
        "connection_mode": (
            "LOCAL_READ_ONLY_STATUS_COMMAND_HUMAN_EXPLANATION_ONLY"
        ),
        "decision": (
            "CURRENT_VALIDATED_RESEARCH_STATUS_CONNECTED_"
            "FOR_HUMAN_EXPLANATION_ONLY"
        ),
        "sources": {},
        "research_status": {
            "legacy_short_candidate": {"status": "REJECTED"},
            "short_recovery_line": {"status": "CLOSED"},
            "short_recovery_surviving_variant_count": 0,
            "long_primary_candidate": {"status": "RESEARCH_ONLY"},
            "long_secondary_candidate": {"status": "REFERENCE_ONLY"},
            "long_official_dataset_state": (
                "INITIALIZED_EMPTY_READY_FOR_CONTROLLED_EVIDENCE"
            ),
            "long_official_evidence_row_count": 0,
            "retrospective_lockbox": {"status": "SEALED"},
            "prospective_holdout": {"status": "SEALED"},
            "total_project_completed": False,
        },
        "restrictions": {
            "local_read_only_status_consumption_allowed": True,
            "status_command_invocation_allowed": True,
            "other_openclaw_tool_invocation_allowed": False,
            "human_explanation_only": True,
            "actionable_trading_fields_present": False,
            "official_dataset_write_allowed": False,
            "openclaw_operational_integration_allowed": False,
            "signal_generation_enabled": False,
            "paper_trade_execution_allowed": False,
            "real_capital_allowed": False,
            "market_execution_allowed": False,
            "automation_allowed": False,
        },
        "human_review": {
            "required": True,
            "permission_override_allowed": False,
            "unknown_status_inference_allowed": False,
        },
    }


def request(mode: str = MODE_DETERMINISTIC) -> dict:
    return {
        "workflow_request_schema_version": (
            "OPENCLAW_CONTROLLED_READ_ONLY_RESEARCH_WORKFLOW_REQUEST_V1"
        ),
        "request_id": "phase-11-5-unit-test-v1",
        "operation": "GET_AND_EXPLAIN_VALIDATED_RESEARCH_STATUS",
        "explanation_mode": mode,
        "max_output_tokens": 112,
        "human_review_required": True,
    }


class FakeLocalClient:
    pass


class Phase115WorkflowTests(unittest.TestCase):
    def test_token_round_trip_is_canonical(self) -> None:
        token = encode_workflow_request_token(request())
        self.assertEqual(decode_workflow_request_token(token), request())

    def test_token_with_shell_metacharacter_is_rejected(self) -> None:
        with self.assertRaises(OpenClawResearchWorkflowFailure):
            decode_workflow_request_token("abc;whoami")

    def test_noncanonical_json_token_is_rejected(self) -> None:
        import base64

        raw = json.dumps(request(), indent=2).encode("utf-8")
        token = base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")
        with self.assertRaises(OpenClawResearchWorkflowFailure):
            decode_workflow_request_token(token)

    def test_unknown_request_field_is_rejected(self) -> None:
        value = request()
        value["extra"] = True
        with self.assertRaises(OpenClawResearchWorkflowFailure):
            validate_workflow_request(value)

    def test_human_review_cannot_be_disabled(self) -> None:
        value = request()
        value["human_review_required"] = False
        with self.assertRaises(OpenClawResearchWorkflowFailure):
            validate_workflow_request(value)

    def test_unsupported_operation_is_rejected(self) -> None:
        value = request()
        value["operation"] = "PLACE_ORDER"
        with self.assertRaises(OpenClawResearchWorkflowFailure):
            validate_workflow_request(value)

    @patch(
        "src.integration.openclaw_controlled_read_only_research_workflow_v1."
        "build_connection_status",
        return_value=valid_status(),
    )
    def test_deterministic_mode_uses_no_local_model(self, _) -> None:
        response = execute_workflow_request(
            request(MODE_DETERMINISTIC),
            root=ROOT,
        )
        self.assertEqual(response["explanation_route"], "PYTHON_TEMPLATE")
        self.assertFalse(response["local_model_called"])
        self.assertEqual(response["restrictions"], WORKFLOW_RESTRICTIONS)

    @patch(
        "src.integration.openclaw_controlled_read_only_research_workflow_v1."
        "execute_connection_request"
    )
    @patch(
        "src.integration.openclaw_controlled_read_only_research_workflow_v1."
        "build_connection_status",
        return_value=valid_status(),
    )
    def test_local_mode_delegates_through_phase_11_4(
        self,
        _,
        delegated,
    ) -> None:
        from src.integration.openclaw_controlled_local_utility_connection_v1 import (
            CONNECTION_RESTRICTIONS,
        )

        delegated.return_value = {
            "decision": (
                "OPENCLAW_CONTROLLED_LOCAL_UTILITY_COMPLETED_FOR_HUMAN_REVIEW"
            ),
            "delegated_route": "LOCAL_OLLAMA",
            "local_model_called": True,
            "local_model": "trading-ai-local-fast",
            "local_metrics": {"output_tokens": 12},
            "output": {"result": "Resumen validado."},
            "restrictions": dict(CONNECTION_RESTRICTIONS),
        }
        response = execute_workflow_request(
            request(MODE_LOCAL_OLLAMA),
            root=ROOT,
            client=FakeLocalClient(),
        )
        self.assertEqual(response["explanation_route"], "LOCAL_OLLAMA")
        self.assertTrue(response["local_model_called"])
        delegated.assert_called_once()

    @patch(
        "src.integration.openclaw_controlled_read_only_research_workflow_v1."
        "build_connection_status"
    )
    def test_actionable_source_field_fails_closed(self, source) -> None:
        status = valid_status()
        status["research_status"]["entry_price"] = 100.0
        source.return_value = status
        with self.assertRaises(OpenClawResearchWorkflowFailure):
            execute_workflow_request(request(), root=ROOT)

    @patch(
        "src.integration.openclaw_controlled_read_only_research_workflow_v1."
        "build_connection_status"
    )
    def test_enabled_source_permission_fails_closed(self, source) -> None:
        status = valid_status()
        status["restrictions"]["market_execution_allowed"] = True
        source.return_value = status
        with self.assertRaises(OpenClawResearchWorkflowFailure):
            execute_workflow_request(request(), root=ROOT)

    @patch(
        "src.integration.openclaw_controlled_read_only_research_workflow_v1."
        "execute_connection_request"
    )
    @patch(
        "src.integration.openclaw_controlled_read_only_research_workflow_v1."
        "build_connection_status",
        return_value=valid_status(),
    )
    def test_local_restriction_mismatch_fails_closed(
        self,
        _,
        delegated,
    ) -> None:
        delegated.return_value = {
            "decision": (
                "OPENCLAW_CONTROLLED_LOCAL_UTILITY_COMPLETED_FOR_HUMAN_REVIEW"
            ),
            "delegated_route": "LOCAL_OLLAMA",
            "local_model_called": True,
            "output": {"result": "Resumen"},
            "restrictions": {},
        }
        with self.assertRaises(OpenClawResearchWorkflowFailure):
            execute_workflow_request(request(MODE_LOCAL_OLLAMA), root=ROOT)

    def test_runner_rejects_missing_token(self) -> None:
        completed = subprocess.run(
            [sys.executable, "-m", RUNNER_MODULE],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        self.assertEqual(completed.returncode, 20)
        self.assertEqual(completed.stdout, "")

    def test_runner_rejects_extra_argument(self) -> None:
        completed = subprocess.run(
            [sys.executable, "-m", RUNNER_MODULE, "a", "b"],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        self.assertEqual(completed.returncode, 20)
        self.assertEqual(completed.stdout, "")


if __name__ == "__main__":
    unittest.main()
