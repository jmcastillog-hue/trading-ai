from pathlib import Path
import unittest

from src.validation.phase_10_43_long_official_dataset_atomic_write_harness_design_review_v1 import (
    DESIGN_COMMIT,
    NEXT_PHASE,
    PASS_DECISION,
    REVIEW_CONTRACT,
    REVIEW_ROOT_SHA256,
    canonical_root,
    negative_controls,
    validate,
    validate_contract,
)


class Phase1043Tests(unittest.TestCase):
    def test_design_commit(self):
        self.assertEqual(DESIGN_COMMIT, "40d1c3720a398dad7751fb45212edb91f7f914ce")

    def test_review_root(self):
        self.assertEqual(canonical_root(REVIEW_CONTRACT), REVIEW_ROOT_SHA256)

    def test_contract_valid(self):
        self.assertTrue(validate_contract(REVIEW_CONTRACT))

    def test_six_amendments(self):
        self.assertEqual(len(REVIEW_CONTRACT["amendments"]), 6)

    def test_amendments_binding(self):
        self.assertTrue(all(x["binding"] for x in REVIEW_CONTRACT["amendments"]))

    def test_create_only_scope(self):
        self.assertEqual(
            REVIEW_CONTRACT["implementation_scope"],
            "CREATE_ONLY_EMPTY_INITIALIZATION_IN_TEMPORARY_TEST_DIRECTORIES",
        )

    def test_existing_target_replacement_disabled(self):
        self.assertFalse(
            REVIEW_CONTRACT["existing_target_replacement_allowed_in_phase_10_44"]
        )

    def test_official_write_disabled_in_review(self):
        self.assertFalse(
            REVIEW_CONTRACT["official_dataset_write_allowed_in_phase_10_43"]
        )

    def test_official_run_reserved_for_1045(self):
        self.assertEqual(REVIEW_CONTRACT["official_run_reserved_for_phase"], "10.45")

    def test_next_phase_exact(self):
        self.assertEqual(
            NEXT_PHASE,
            "PHASE_10_44_LONG_FORWARD_OBSERVATION_EVIDENCE_COLLECTION_"
            "OFFICIAL_DATASET_ATOMIC_WRITE_HARNESS_IMPLEMENTATION_V1",
        )

    def test_next_phase_is_implementation(self):
        self.assertEqual(REVIEW_CONTRACT["next_phase_type"], "IMPLEMENTATION_NOT_REVIEW")

    def test_unique_temp_binding(self):
        names = {x["name"] for x in REVIEW_CONTRACT["amendments"]}
        self.assertIn("UNIQUE_TEMP_PATH_TEMPLATE", names)

    def test_atomic_manifest_binding(self):
        names = {x["name"] for x in REVIEW_CONTRACT["amendments"]}
        self.assertIn("ATOMIC_MANIFEST_COMMIT", names)

    def test_platform_durability_binding(self):
        names = {x["name"] for x in REVIEW_CONTRACT["amendments"]}
        self.assertIn("PLATFORM_DURABILITY_ADAPTER", names)

    def test_no_automatic_recovery_binding(self):
        names = {x["name"] for x in REVIEW_CONTRACT["amendments"]}
        self.assertIn("NO_AUTOMATIC_RECOVERY", names)

    def test_eight_negative_controls(self):
        rows = negative_controls()
        self.assertEqual(len(rows), 8)
        self.assertTrue(all(x["rejected_fail_closed"] for x in rows))

    def test_full_validation(self):
        result = validate(Path("."), write_reports=False)
        self.assertTrue(result["summary"]["validation_passed"])
        self.assertEqual(result["summary"]["validation_decision"], PASS_DECISION)
        self.assertEqual(result["summary"]["total_check_count"], 59)
        self.assertEqual(result["summary"]["negative_control_count"], 8)

    def test_project_not_complete(self):
        result = validate(Path("."), write_reports=False)
        self.assertFalse(result["summary"]["total_project_completed"])


if __name__ == "__main__":
    unittest.main()
