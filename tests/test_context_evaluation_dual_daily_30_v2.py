from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import unittest
from datetime import datetime, timedelta
from pathlib import Path

from src.evaluation import context_evaluation_prospective_cohort_v1 as cohort

PLAN_RELATIVE = Path(
    "research/context_evaluation/context_evaluation_dual_daily_30_plan_v2.json"
)
RUNNER_RELATIVE = Path("tools/context_evaluation_dual_daily_runner_v2.py")
V1_RUNNER_RELATIVE = Path("tools/context_evaluation_dual_daily_runner_v1.py")
EXPECTED_PLAN_SHA256 = (
    "fc1094fa9aab3cf5d683c396c3e179601f24260d04f30c2dca26d1e322ddc41b"
)
EXPECTED_CONTEXT_TEMPLATE_SHA256 = (
    "e97718c5256abd777f0c23395c7df43fe48dceffac1bac20ac50f7675dcc0dac"
)
EXPECTED_OUTCOME_TEMPLATE_SHA256 = (
    "3e997bd9197666b26acdcffec269925fbbe1c2b61665f5966a4cf573a9fc7eec"
)
CONTEXT_TEMPLATE_RELATIVE = Path(
    "research/context_evaluation/reference_runners/"
    "context_slot_reference_s008_v1_1.py"
)
OUTCOME_TEMPLATE_RELATIVE = Path(
    "research/context_evaluation/reference_runners/"
    "outcome_binding_reference_s008_v1.py"
)


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def canonical_json_bytes(value: object) -> bytes:
    return (
        json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
            allow_nan=False,
        )
        + "\n"
    ).encode("utf-8")


class DualDailyV2PlanTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.repo = repo_root()
        cls.plan_path = cls.repo / PLAN_RELATIVE
        cls.plan = json.loads(cls.plan_path.read_text(encoding="utf-8"))

    def test_01_plan_raw_and_canonical_hash_are_frozen(self) -> None:
        raw = self.plan_path.read_bytes()
        self.assertEqual(hashlib.sha256(raw).hexdigest(), EXPECTED_PLAN_SHA256)
        self.assertEqual(
            hashlib.sha256(canonical_json_bytes(self.plan)).hexdigest(),
            EXPECTED_PLAN_SHA256,
        )

    def test_02_plan_validates_under_frozen_prospective_policy(self) -> None:
        policy, _ = cohort.load_context_evaluation_prospective_cohort_policy_v1(
            self.repo
        )
        hypothesis, hypothesis_sha, _ = cohort.load_bound_hypothesis_manifest_v1(
            self.repo,
            policy=policy,
        )
        validated = cohort.validate_prospective_cohort_plan_v1(
            self.plan,
            policy=policy,
            hypothesis_manifest=hypothesis,
            hypothesis_manifest_sha256=hypothesis_sha,
        )
        self.assertEqual(
            validated["cohort_id"],
            "CONTEXT_LEVEL_A_DUAL_DAILY_30_V2",
        )
        self.assertEqual(len(validated["slots"]), 30)

    def test_03_slots_are_exactly_s001_through_s030(self) -> None:
        self.assertEqual(
            [item["slot_id"] for item in self.plan["slots"]],
            [f"S{i:03d}" for i in range(1, 31)],
        )

    def test_04_pre_dst_anchors_are_exact(self) -> None:
        anchors = [
            item["context_anchor_open_utc"] for item in self.plan["slots"][:4]
        ]
        self.assertEqual(
            anchors,
            [
                "2026-09-04T10:30:00+00:00",
                "2026-09-04T22:30:00+00:00",
                "2026-09-05T10:30:00+00:00",
                "2026-09-05T22:30:00+00:00",
            ],
        )

    def test_05_post_dst_anchors_are_0930_and_2130_utc(self) -> None:
        for item in self.plan["slots"][4:]:
            anchor = datetime.fromisoformat(item["context_anchor_open_utc"])
            self.assertIn((anchor.hour, anchor.minute), {(9, 30), (21, 30)})

    def test_06_spacing_is_11_or_12_hours_and_above_minimum(self) -> None:
        anchors = [
            datetime.fromisoformat(item["context_anchor_open_utc"])
            for item in self.plan["slots"]
        ]
        spacings = [b - a for a, b in zip(anchors, anchors[1:])]
        self.assertEqual(min(spacings), timedelta(hours=11))
        self.assertEqual(max(spacings), timedelta(hours=12))
        self.assertTrue(all(value > timedelta(hours=4) for value in spacings))

    def test_07_plan_boundaries_and_freeze_are_exact(self) -> None:
        self.assertEqual(
            self.plan["plan_frozen_at_utc"],
            "2026-09-03T00:20:00+00:00",
        )
        self.assertEqual(
            self.plan["slots"][0]["context_anchor_open_utc"],
            "2026-09-04T10:30:00+00:00",
        )
        self.assertEqual(
            self.plan["slots"][-1]["context_anchor_open_utc"],
            "2026-09-18T21:30:00+00:00",
        )

    def test_08_plan_contains_no_market_state_fields(self) -> None:
        forbidden = {
            "price", "close", "open", "high", "low", "volume",
            "direction", "signal", "candidate", "return",
            "forward_return", "result", "mfe", "mae", "threshold",
            "score", "regime", "volatility", "feature",
        }
        for item in self.plan["slots"]:
            self.assertTrue(forbidden.isdisjoint(item.keys()))

    def test_09_reference_template_hashes_are_exact(self) -> None:
        self.assertEqual(
            hashlib.sha256(
                (self.repo / CONTEXT_TEMPLATE_RELATIVE).read_bytes()
            ).hexdigest(),
            EXPECTED_CONTEXT_TEMPLATE_SHA256,
        )
        self.assertEqual(
            hashlib.sha256(
                (self.repo / OUTCOME_TEMPLATE_RELATIVE).read_bytes()
            ).hexdigest(),
            EXPECTED_OUTCOME_TEMPLATE_SHA256,
        )

    def test_10_runner_self_check_passes_without_network(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                str(self.repo / RUNNER_RELATIVE),
                "--self-check",
                "--repo",
                str(self.repo),
            ],
            cwd=self.repo,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        self.assertEqual(
            result.returncode,
            0,
            msg=result.stdout + "\n" + result.stderr,
        )
        self.assertIn("SELF_CHECK_PASSED=True", result.stdout)
        self.assertIn("REAL_HTTP_CALLS=0", result.stdout)
        self.assertIn(
            "ALL_30_CONTEXT_TRANSFORMS_COMPILE=True",
            result.stdout,
        )
        self.assertIn(
            "ALL_30_OUTCOME_TRANSFORMS_COMPILE=True",
            result.stdout,
        )
        self.assertIn(
            "TEMPLATE_EXTERNAL_PATH_REBIND_VERIFIED=True",
            result.stdout,
        )
        self.assertIn(
            "EVIDENCE_ROOT_EXTERNAL_AND_SHORT=True",
            result.stdout,
        )

    def test_11_v1_activation_is_blocked_fail_closed(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                str(self.repo / V1_RUNNER_RELATIVE),
                "--initialize-root",
                "--repo",
                str(self.repo),
            ],
            cwd=self.repo,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        self.assertNotEqual(result.returncode, 0)
        combined = result.stdout + "\n" + result.stderr
        self.assertIn("COHORT_SUPERSEDED_FAIL_CLOSED", combined)
        self.assertIn("CONTEXT_LEVEL_A_DUAL_DAILY_30_V2", combined)


if __name__ == "__main__":
    unittest.main(verbosity=2)
