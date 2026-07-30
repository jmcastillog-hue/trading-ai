from __future__ import annotations

import unittest
from pathlib import Path

from src.integration.openclaw_read_only_local_connection_v1 import (
    build_connection_status,
    validate_official_empty_dataset,
)


ROOT = Path(__file__).resolve().parents[1]


class OpenClawReadOnlyLocalConnectionV1Tests(unittest.TestCase):
    def test_official_empty_dataset_is_verified(self) -> None:
        result = validate_official_empty_dataset(ROOT)

        self.assertEqual(result["phase"], "10.45")
        self.assertEqual(result["column_count"], 54)
        self.assertEqual(result["evidence_row_count"], 0)
        self.assertTrue(result["create_only"])
        self.assertTrue(result["human_review_required"])

    def test_connection_is_read_only_and_non_actionable(self) -> None:
        result = build_connection_status(ROOT)
        restrictions = result["restrictions"]

        self.assertTrue(
            restrictions["local_read_only_status_consumption_allowed"]
        )
        self.assertTrue(
            restrictions["status_command_invocation_allowed"]
        )
        self.assertFalse(
            restrictions["other_openclaw_tool_invocation_allowed"]
        )
        self.assertFalse(
            restrictions["actionable_trading_fields_present"]
        )
        self.assertFalse(
            restrictions["official_dataset_write_allowed"]
        )
        self.assertFalse(
            restrictions["openclaw_operational_integration_allowed"]
        )
        self.assertFalse(restrictions["signal_generation_enabled"])
        self.assertFalse(
            restrictions["paper_trade_execution_allowed"]
        )
        self.assertFalse(restrictions["real_capital_allowed"])
        self.assertFalse(restrictions["market_execution_allowed"])
        self.assertFalse(restrictions["automation_allowed"])

    def test_current_official_dataset_state_is_exposed(self) -> None:
        result = build_connection_status(ROOT)
        research = result["research_status"]

        self.assertEqual(
            research["long_official_dataset_state"],
            "INITIALIZED_EMPTY_READY_FOR_CONTROLLED_EVIDENCE",
        )
        self.assertEqual(
            research["long_official_evidence_row_count"],
            0,
        )
        self.assertFalse(research["total_project_completed"])
        self.assertTrue(result["human_review"]["required"])


if __name__ == "__main__":
    unittest.main()
