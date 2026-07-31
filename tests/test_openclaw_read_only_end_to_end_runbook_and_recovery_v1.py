from __future__ import annotations

import unittest
from pathlib import Path

from src.validation.openclaw_read_only_end_to_end_runbook_and_recovery_v1 import (
    VALIDATED_DECISION,
    validate_phase_11_2,
)


class Phase112EndToEndRunbookRecoveryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = validate_phase_11_2(Path("."))

    def test_phase_11_2_validation_passes(self) -> None:
        self.assertTrue(self.result["validation_passed"])
        self.assertEqual(self.result["validation_decision"], VALIDATED_DECISION)
        self.assertEqual(self.result["failed_checks"], 0)
        self.assertEqual(self.result["blocker_count"], 0)
        self.assertTrue(self.result["mvp_read_only_completed"])

    def test_operational_permissions_remain_disabled(self) -> None:
        self.assertFalse(self.result["local_auxiliary_model_integrated"])
        self.assertFalse(self.result["official_dataset_write_allowed"])
        self.assertFalse(self.result["signal_generation_enabled"])
        self.assertFalse(self.result["paper_trade_execution_allowed"])
        self.assertFalse(self.result["real_capital_allowed"])
        self.assertFalse(self.result["market_execution_allowed"])
        self.assertFalse(self.result["automation_allowed"])

    def test_recovery_controls_are_present(self) -> None:
        lookup = {
            row["check_name"]: row["passed"]
            for row in self.result["checks"]
        }
        self.assertTrue(lookup["extra_argument_fails_closed"])
        self.assertTrue(lookup["tampered_dataset_fails_closed"])
        self.assertTrue(lookup["tampered_failure_reports_closed_decision"])
        self.assertTrue(lookup["dataset_unchanged"])
        self.assertTrue(lookup["manifest_unchanged"])


if __name__ == "__main__":
    unittest.main()
