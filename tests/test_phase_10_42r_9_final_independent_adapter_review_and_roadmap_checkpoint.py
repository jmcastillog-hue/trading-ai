from pathlib import Path
import unittest
from src.validation.phase_10_42r_9_final_independent_adapter_review_and_roadmap_checkpoint_v1 import EXPECTED_BASE,PASS_DECISION,validate

class T(unittest.TestCase):
    def test_base(self): self.assertEqual(EXPECTED_BASE,"ad6dda3011390fffbb11d22b178e0dc474726ca9")
    def test_review(self):
        r=validate(Path("."),write_reports=False); self.assertTrue(r["summary"]["validation_passed"]); self.assertEqual(r["summary"]["validation_decision"],PASS_DECISION); self.assertTrue(r["summary"]["review_loop_closed"]); self.assertFalse(r["summary"]["phase_10_42r_10_review_allowed_by_default"]); self.assertFalse(r["summary"]["total_project_completed"])

if __name__=="__main__": unittest.main()
