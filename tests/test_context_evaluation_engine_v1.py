from __future__ import annotations

import hashlib
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from src.evaluation import context_evaluation_engine_v1 as m

POLICY_EFFECTIVE = "2026-08-21T00:45:00+00:00"

def policy():
    return {
        "schema_version": "CONTEXT_EVALUATION_ENGINE_POLICY_V1",
        "capability": "CONTEXT_EVALUATION_ENGINE_V1",
        "policy_effective_from_utc": POLICY_EFFECTIVE,
        "expected_pack_schema_version": "CONTEXT_FEATURE_PACK_V1_LEVEL_A_STANDARD_SCHEMA_V1",
        "expected_outcome_schema_version": "FORWARD_OUTCOME_LABELS_V1",
        "hypothesis_manifest_schema_version": "CONTEXT_EVALUATION_HYPOTHESIS_MANIFEST_V1",
        "cohort_manifest_schema_version": "CONTEXT_EVALUATION_COHORT_MANIFEST_V1",
        "supported_horizons_bars": [1, 2, 4, 8, 16],
        "outcome_branch": "synchronized_context_outcome",
        "outcome_field": "forward_return",
        "predictor_types": ["BINARY", "CATEGORICAL", "CONTINUOUS"],
        "allowed_transform": "IDENTITY",
        "min_hypotheses": 1,
        "max_hypotheses": 32,
        "min_cohort_entries": 1,
        "max_cohort_entries": 10000,
        "min_non_overlapping_observations": 10,
        "preferred_non_overlapping_observations": 30,
        "min_binary_group_observations": 5,
        "min_categorical_group_observations": 5,
        "max_categorical_levels": 8,
        "hypothesis_freeze_not_before_policy_required": True,
        "observation_not_before_hypothesis_freeze_required": True,
        "point_in_time_feature_required": True,
        "context_anchor_exact_match_required": True,
        "context_cutoff_exact_match_required": True,
        "non_overlapping_outcome_windows_required": True,
        "missing_feature_imputation_allowed": False,
        "late_feature_as_zero_allowed": False,
        "threshold_search_allowed": False,
        "predictor_transform_search_allowed": False,
        "model_fit_allowed": False,
        "hyperparameter_search_allowed": False,
        "p_value_generation_allowed": False,
        "significance_claim_allowed": False,
        "multiple_testing_winner_selection_allowed": False,
        "feature_ranking_allowed": False,
        "edge_claim_allowed": False,
        "feature_promotion_allowed": False,
        "quality_gate_evaluation_allowed": False,
        "directional_semantics": False,
        "signal_semantics": False,
        "paper_trade_execution_allowed": False,
        "real_capital_allowed": False,
        "live_alerts_allowed": False,
        "exchange_execution_allowed": False,
        "automation_allowed": False,
        "official_append_allowed": False,
    }

def hypothesis_manifest(
    predictor_type="CONTINUOUS",
    feature_id="BTC_CYCLE_HALVING_CONTEXT_V1",
    payload_path=None,
    horizon=1,
    frozen_at="2026-08-21T00:45:00+00:00",
):
    return {
        "schema_version": "CONTEXT_EVALUATION_HYPOTHESIS_MANIFEST_V1",
        "manifest_id": "HYP_V1",
        "frozen_at_utc": frozen_at,
        "hypotheses": [
            {
                "hypothesis_id": "H001",
                "feature_id": feature_id,
                "payload_path": payload_path or ["x"],
                "predictor_type": predictor_type,
                "horizon_bars": horizon,
                "outcome_field": "forward_return",
                "transform": "IDENTITY",
            }
        ],
    }

def cohort_manifest(entries):
    return {
        "schema_version": "CONTEXT_EVALUATION_COHORT_MANIFEST_V1",
        "cohort_id": "COHORT_V1",
        "entries": entries,
    }

def feature(
    feature_id,
    payload,
    status="AVAILABLE",
    eligible=True,
):
    return {
        "feature_id": feature_id,
        "status": status,
        "point_in_time_eligible": eligible,
        "payload": payload if status == "AVAILABLE" else None,
    }

def loaded_observation(
    idx,
    *,
    anchor_minute=None,
    predictor=0.0,
    predictor_type="CONTINUOUS",
    feature_id="BTC_CYCLE_HALVING_CONTEXT_V1",
    status="AVAILABLE",
    eligible=True,
    outcome=0.0,
    label_status="AVAILABLE",
    cutoff=None,
    primary_outcome=999.0,
):
    if anchor_minute is None:
        anchor_minute = idx * 15
    day_offset, minute_of_day = divmod(anchor_minute, 24 * 60)
    hour, minute = divmod(minute_of_day, 60)
    day = 21 + day_offset
    anchor = f"2026-08-{day:02d}T{hour:02d}:{minute:02d}:00+00:00"
    cutoff_value = cutoff or anchor
    oid = f"OBS_{idx:03d}"

    payload = {"x": predictor}
    features = [
        feature(fid, payload if fid == feature_id else {"x": 0.0})
        for fid in m.FEATURE_IDS
    ]
    target = next(x for x in features if x["feature_id"] == feature_id)
    target["status"] = status
    target["point_in_time_eligible"] = eligible
    target["payload"] = payload if status == "AVAILABLE" else None

    labels = {}
    for h in m.FORWARD_HORIZONS_BARS:
        labels[str(h)] = {
            "horizon_bars": h,
            "label_status": label_status if h == 1 else "PENDING",
            "forward_return": outcome if h == 1 and label_status == "AVAILABLE" else None,
        }

    return {
        "observation_id": oid,
        "context_cutoff_utc": cutoff_value,
        "context_anchor_open_utc": anchor,
        "pack": {
            "observation_id": oid,
            "features": features,
            "context_cutoff_utc": cutoff_value,
            "context_anchor_open_utc": anchor,
        },
        "outcomes": {
            "observation_id": oid,
            "forward_horizons_bars": list(m.FORWARD_HORIZONS_BARS),
            "primary_rule_outcome": {
                "labels": {
                    "1": {
                        "horizon_bars": 1,
                        "label_status": "AVAILABLE",
                        "forward_return": primary_outcome,
                    }
                }
            },
            "synchronized_context_outcome": {
                "context_available_at_utc": cutoff_value,
                "anchor_open_time_utc": anchor,
                "labels": labels,
            },
        },
        "descriptor": {
            "observation_id": oid,
            "synchronized_context_available_at_utc": cutoff_value,
        },
        "context_package_manifest_sha256": "a" * 64,
        "outcome_package_manifest_sha256": "b" * 64,
    }

class Tests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        self.repo = root / "repo"
        self.repo.mkdir()
        (self.repo / ".git").mkdir()
        official = self.repo / "data" / "forward"
        official.mkdir(parents=True)
        (official / "long_forward_observation_dataset_v1.csv").write_text(
            "header\n", encoding="utf-8"
        )
        (official / "long_forward_observation_dataset_v1.manifest.csv").write_text(
            "manifest\n", encoding="utf-8"
        )
        resources = self.repo / "src" / "evaluation" / "resources"
        resources.mkdir(parents=True)
        (resources / "context_evaluation_engine_policy_v1.json").write_text(
            json.dumps(policy(), sort_keys=True, indent=2) + "\n",
            encoding="utf-8",
        )
        self.external = root / "external"
        self.external.mkdir()
        os.environ.pop("TRADING_AI_OFFICIAL_LONG_EVIDENCE_APPEND_ALLOWED", None)

    def tearDown(self):
        os.environ.pop("TRADING_AI_OFFICIAL_LONG_EVIDENCE_APPEND_ALLOWED", None)
        self.tmp.cleanup()

    def test_01_identity_and_permissions(self):
        self.assertEqual(m.CAPABILITY, "CONTEXT_EVALUATION_ENGINE_V1")
        self.assertEqual(m.OUTCOME_BRANCH, "synchronized_context_outcome")
        self.assertEqual(m.OUTCOME_FIELD, "forward_return")
        self.assertEqual(m.PACKAGE_AUTHORIZATION, "PREPARE_CONTEXT_EVALUATION_ENGINE_V1")

    def test_02_policy_valid(self):
        result = m.validate_context_evaluation_engine_policy_v1(policy())
        self.assertEqual(result["min_non_overlapping_observations"], 10)
        self.assertEqual(result["supported_horizons_bars"], (1, 2, 4, 8, 16))

    def test_03_policy_pvalues_must_be_false(self):
        value = policy()
        value["p_value_generation_allowed"] = True
        with self.assertRaises(m.ContextEvaluationEngineError):
            m.validate_context_evaluation_engine_policy_v1(value)

    def test_04_hypothesis_manifest_valid(self):
        result = m.validate_hypothesis_manifest_v1(
            hypothesis_manifest(),
            policy=policy(),
        )
        self.assertEqual(result["hypotheses"][0]["hypothesis_id"], "H001")

    def test_05_hypothesis_freeze_before_policy_fails(self):
        value = hypothesis_manifest(
            frozen_at="2026-08-20T23:59:00+00:00"
        )
        with self.assertRaises(m.ContextEvaluationEngineError):
            m.validate_hypothesis_manifest_v1(value, policy=policy())

    def test_06_hypothesis_direction_field_fails(self):
        value = hypothesis_manifest()
        value["hypotheses"][0]["expected_direction"] = "POSITIVE"
        with self.assertRaises(m.ContextEvaluationEngineError):
            m.validate_hypothesis_manifest_v1(value, policy=policy())

    def test_07_hypothesis_transform_search_blocked(self):
        value = hypothesis_manifest()
        value["hypotheses"][0]["transform"] = "LOG"
        with self.assertRaises(m.ContextEvaluationEngineError):
            m.validate_hypothesis_manifest_v1(value, policy=policy())

    def test_08_hypothesis_bad_horizon_fails(self):
        value = hypothesis_manifest(horizon=3)
        with self.assertRaises(m.ContextEvaluationEngineError):
            m.validate_hypothesis_manifest_v1(value, policy=policy())

    def test_09_hypothesis_bad_feature_fails(self):
        value = hypothesis_manifest(feature_id="UNKNOWN_FEATURE")
        with self.assertRaises(m.ContextEvaluationEngineError):
            m.validate_hypothesis_manifest_v1(value, policy=policy())

    def test_10_cohort_manifest_sorted_unique(self):
        entries = [
            {
                "observation_id": "A",
                "context_pack_directory": "/tmp/a",
                "context_pack_manifest_sha256": "a" * 64,
                "outcome_package_directory": "/tmp/b",
                "outcome_package_manifest_sha256": "b" * 64,
            },
            {
                "observation_id": "B",
                "context_pack_directory": "/tmp/c",
                "context_pack_manifest_sha256": "c" * 64,
                "outcome_package_directory": "/tmp/d",
                "outcome_package_manifest_sha256": "d" * 64,
            },
        ]
        result = m.validate_cohort_manifest_v1(
            cohort_manifest(entries),
            policy=policy(),
        )
        self.assertEqual(len(result["entries"]), 2)

    def test_11_cohort_manifest_unsorted_fails(self):
        entries = [
            {
                "observation_id": "B",
                "context_pack_directory": "/tmp/a",
                "context_pack_manifest_sha256": "a" * 64,
                "outcome_package_directory": "/tmp/b",
                "outcome_package_manifest_sha256": "b" * 64,
            },
            {
                "observation_id": "A",
                "context_pack_directory": "/tmp/c",
                "context_pack_manifest_sha256": "c" * 64,
                "outcome_package_directory": "/tmp/d",
                "outcome_package_manifest_sha256": "d" * 64,
            },
        ]
        with self.assertRaises(m.ContextEvaluationEngineError):
            m.validate_cohort_manifest_v1(
                cohort_manifest(entries),
                policy=policy(),
            )

    def test_12_pre_freeze_observation_excluded(self):
        rows = [
            loaded_observation(
                1,
                anchor_minute=0,
                cutoff="2026-08-21T00:30:00+00:00",
            )
        ]
        results, audit = m.evaluate_context_cohort_v1(
            loaded_observations=rows,
            hypothesis_manifest=hypothesis_manifest(),
            policy=policy(),
        )
        self.assertEqual(
            audit["rows"][0]["exclusion_reason"],
            "OBSERVATION_PRE_HYPOTHESIS_FREEZE",
        )
        self.assertEqual(
            results["results"][0]["non_overlapping_observations"],
            0,
        )

    def test_13_late_feature_excluded_not_zero(self):
        rows = [
            loaded_observation(
                i,
                predictor=1.0,
                eligible=False,
                anchor_minute=15 * (i + 4),
            )
            for i in range(12)
        ]
        _, audit = m.evaluate_context_cohort_v1(
            loaded_observations=rows,
            hypothesis_manifest=hypothesis_manifest(),
            policy=policy(),
        )
        self.assertTrue(
            all(
                row["exclusion_reason"]
                == "FEATURE_NOT_POINT_IN_TIME_ELIGIBLE"
                for row in audit["rows"]
            )
        )

    def test_14_unavailable_feature_excluded(self):
        rows = [
            loaded_observation(
                i,
                status="UNAVAILABLE",
                anchor_minute=15 * (i + 4),
            )
            for i in range(12)
        ]
        _, audit = m.evaluate_context_cohort_v1(
            loaded_observations=rows,
            hypothesis_manifest=hypothesis_manifest(),
            policy=policy(),
        )
        self.assertTrue(
            all(
                row["exclusion_reason"] == "FEATURE_NOT_AVAILABLE"
                for row in audit["rows"]
            )
        )

    def test_15_pending_outcome_excluded(self):
        rows = [
            loaded_observation(
                i,
                label_status="PENDING",
                anchor_minute=15 * (i + 4),
            )
            for i in range(12)
        ]
        _, audit = m.evaluate_context_cohort_v1(
            loaded_observations=rows,
            hypothesis_manifest=hypothesis_manifest(),
            policy=policy(),
        )
        self.assertTrue(
            all(
                row["exclusion_reason"] == "OUTCOME_NOT_AVAILABLE"
                for row in audit["rows"]
            )
        )

    def test_16_primary_rule_outcome_is_ignored(self):
        rows = [
            loaded_observation(
                i,
                predictor=float(i),
                outcome=float(i),
                primary_outcome=-999.0 * i,
                anchor_minute=15 * (i + 4),
            )
            for i in range(12)
        ]
        results, audit = m.evaluate_context_cohort_v1(
            loaded_observations=rows,
            hypothesis_manifest=hypothesis_manifest(),
            policy=policy(),
        )
        effect = results["results"][0]["effect"]
        self.assertAlmostEqual(effect["effect_value"], 1.0)
        self.assertFalse(audit["primary_rule_outcome_used"])

    def test_17_continuous_spearman_positive_one(self):
        rows = [
            loaded_observation(
                i,
                predictor=float(i),
                outcome=float(i) / 100.0,
                anchor_minute=15 * (i + 4),
            )
            for i in range(12)
        ]
        results, _ = m.evaluate_context_cohort_v1(
            loaded_observations=rows,
            hypothesis_manifest=hypothesis_manifest(),
            policy=policy(),
        )
        row = results["results"][0]
        self.assertEqual(row["analysis_status"], "DESCRIPTIVE_ESTIMATE_AVAILABLE")
        self.assertAlmostEqual(row["effect"]["effect_value"], 1.0)

    def test_18_overlap_purge_is_horizon_aware(self):
        rows = [
            loaded_observation(
                i,
                predictor=float(i),
                outcome=float(i),
                anchor_minute=15 * (i + 4),
            )
            for i in range(20)
        ]
        manifest = hypothesis_manifest(horizon=4)
        # Supply horizon-4 labels in each row.
        for item in rows:
            labels = item["outcomes"]["synchronized_context_outcome"]["labels"]
            labels["4"] = {
                "horizon_bars": 4,
                "label_status": "AVAILABLE",
                "forward_return": float(item["observation_id"].split("_")[1]),
            }
        results, audit = m.evaluate_context_cohort_v1(
            loaded_observations=rows,
            hypothesis_manifest=manifest,
            policy=policy(),
        )
        self.assertEqual(
            results["results"][0]["non_overlapping_observations"],
            5,
        )
        self.assertTrue(
            any(
                row["exclusion_reason"] == "OVERLAPPING_FORWARD_WINDOW"
                for row in audit["rows"]
            )
        )

    def test_19_binary_difference(self):
        rows = []
        for i in range(12):
            rows.append(
                loaded_observation(
                    i,
                    predictor=(i % 2 == 0),
                    outcome=0.02 if i % 2 == 0 else -0.01,
                    anchor_minute=15 * (i + 4),
                )
            )
        results, _ = m.evaluate_context_cohort_v1(
            loaded_observations=rows,
            hypothesis_manifest=hypothesis_manifest(
                predictor_type="BINARY"
            ),
            policy=policy(),
        )
        effect = results["results"][0]["effect"]
        self.assertAlmostEqual(effect["effect_value"], 0.03)
        self.assertEqual(results["results"][0]["analysis_status"], "DESCRIPTIVE_ESTIMATE_AVAILABLE")

    def test_20_binary_group_minimum_enforced(self):
        rows = []
        for i in range(12):
            rows.append(
                loaded_observation(
                    i,
                    predictor=(i == 0),
                    outcome=float(i),
                    anchor_minute=15 * (i + 4),
                )
            )
        results, _ = m.evaluate_context_cohort_v1(
            loaded_observations=rows,
            hypothesis_manifest=hypothesis_manifest(
                predictor_type="BINARY"
            ),
            policy=policy(),
        )
        self.assertEqual(
            results["results"][0]["analysis_status"],
            "INSUFFICIENT_BINARY_GROUP_SAMPLE",
        )

    def test_21_categorical_summary_no_winner(self):
        rows = []
        categories = ["A", "B"]
        for i in range(12):
            rows.append(
                loaded_observation(
                    i,
                    predictor=categories[i % 2],
                    outcome=float(i) / 100.0,
                    anchor_minute=15 * (i + 4),
                )
            )
        results, _ = m.evaluate_context_cohort_v1(
            loaded_observations=rows,
            hypothesis_manifest=hypothesis_manifest(
                predictor_type="CATEGORICAL"
            ),
            policy=policy(),
        )
        effect = results["results"][0]["effect"]
        self.assertIsNone(effect["effect_value"])
        self.assertEqual(effect["categorical_level_count"], 2)
        self.assertFalse(results["best_hypothesis_selected"])

    def test_22_results_have_no_pvalue_significance_or_edge(self):
        rows = [
            loaded_observation(
                i,
                predictor=float(i),
                outcome=float(i),
                anchor_minute=15 * (i + 4),
            )
            for i in range(12)
        ]
        results, _ = m.evaluate_context_cohort_v1(
            loaded_observations=rows,
            hypothesis_manifest=hypothesis_manifest(),
            policy=policy(),
        )
        row = results["results"][0]
        self.assertIsNone(row["p_value"])
        self.assertFalse(row["significance_assigned"])
        self.assertFalse(row["edge_claim"])
        self.assertEqual(
            results["evaluation_decision"],
            "DESCRIPTIVE_ONLY_NO_EDGE_CLAIM",
        )

    def test_23_results_validator_rejects_pvalue(self):
        rows = [
            loaded_observation(
                i,
                predictor=float(i),
                outcome=float(i),
                anchor_minute=15 * (i + 4),
            )
            for i in range(12)
        ]
        results, _ = m.evaluate_context_cohort_v1(
            loaded_observations=rows,
            hypothesis_manifest=hypothesis_manifest(),
            policy=policy(),
        )
        results["results"][0]["p_value"] = 0.01
        with self.assertRaises(m.ContextEvaluationEngineError):
            m.validate_context_evaluation_results_v1(results)

    def _write_json(self, name, value):
        path = self.external / name
        path.write_text(
            json.dumps(value, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        return path

    def _make_minimal_packages(self, count=12):
        entries = []
        loaded_by_context = {}
        for i in range(count):
            loaded = loaded_observation(
                i,
                predictor=float(i),
                outcome=float(i) / 100.0,
                anchor_minute=15 * (i + 4),
            )
            cdir = self.external / f"context_{i:03d}"
            odir = self.external / f"outcome_{i:03d}"
            cdir.mkdir()
            odir.mkdir()
            (cdir / "context_feature_pack.json").write_text(
                json.dumps(loaded["pack"], sort_keys=True) + "\n",
                encoding="utf-8",
            )
            (odir / "forward_outcomes.json").write_text(
                json.dumps(loaded["outcomes"], sort_keys=True) + "\n",
                encoding="utf-8",
            )
            (odir / "observation_descriptor.json").write_text(
                json.dumps(loaded["descriptor"], sort_keys=True) + "\n",
                encoding="utf-8",
            )
            (cdir / "manifest.sha256").write_text("context\n", encoding="utf-8")
            (odir / "manifest.sha256").write_text("outcome\n", encoding="utf-8")
            csha = hashlib.sha256((cdir / "manifest.sha256").read_bytes()).hexdigest()
            osha = hashlib.sha256((odir / "manifest.sha256").read_bytes()).hexdigest()
            entry = {
                "observation_id": loaded["observation_id"],
                "context_pack_directory": str(cdir.resolve()),
                "context_pack_manifest_sha256": csha,
                "outcome_package_directory": str(odir.resolve()),
                "outcome_package_manifest_sha256": osha,
            }
            entries.append(entry)
            loaded_by_context[str(cdir.resolve())] = loaded
        return entries, loaded_by_context

    def test_24_missing_authorization_fails(self):
        h = self._write_json("h1.json", hypothesis_manifest())
        c = self._write_json(
            "c1.json",
            cohort_manifest(
                [
                    {
                        "observation_id": "A",
                        "context_pack_directory": str(self.external / "x"),
                        "context_pack_manifest_sha256": "a" * 64,
                        "outcome_package_directory": str(self.external / "y"),
                        "outcome_package_manifest_sha256": "b" * 64,
                    }
                ]
            ),
        )
        with self.assertRaises(m.ContextEvaluationEngineError):
            m.prepare_context_evaluation_engine_v1_package(
                repo_root=self.repo,
                hypothesis_manifest_json=h,
                cohort_manifest_json=c,
                output_directory=self.external / "out_auth",
                authorization=None,
            )

    def test_25_output_inside_repo_fails(self):
        h = self._write_json("h2.json", hypothesis_manifest())
        c = self._write_json(
            "c2.json",
            cohort_manifest(
                [
                    {
                        "observation_id": "A",
                        "context_pack_directory": str(self.external / "x2"),
                        "context_pack_manifest_sha256": "a" * 64,
                        "outcome_package_directory": str(self.external / "y2"),
                        "outcome_package_manifest_sha256": "b" * 64,
                    }
                ]
            ),
        )
        with self.assertRaises(m.ContextEvaluationEngineError):
            m.prepare_context_evaluation_engine_v1_package(
                repo_root=self.repo,
                hypothesis_manifest_json=h,
                cohort_manifest_json=c,
                output_directory=self.repo / "out",
                authorization=m.PACKAGE_AUTHORIZATION,
            )

    def test_26_gate_enabled_fails(self):
        os.environ["TRADING_AI_OFFICIAL_LONG_EVIDENCE_APPEND_ALLOWED"] = "1"
        h = self._write_json("h3.json", hypothesis_manifest())
        c = self._write_json(
            "c3.json",
            cohort_manifest(
                [
                    {
                        "observation_id": "A",
                        "context_pack_directory": str(self.external / "x3"),
                        "context_pack_manifest_sha256": "a" * 64,
                        "outcome_package_directory": str(self.external / "y3"),
                        "outcome_package_manifest_sha256": "b" * 64,
                    }
                ]
            ),
        )
        with self.assertRaises(m.ContextEvaluationEngineError):
            m.prepare_context_evaluation_engine_v1_package(
                repo_root=self.repo,
                hypothesis_manifest_json=h,
                cohort_manifest_json=c,
                output_directory=self.external / "out_gate",
                authorization=m.PACKAGE_AUTHORIZATION,
            )

    def test_27_package_roundtrip_and_tamper(self):
        entries, loaded_by_context = self._make_minimal_packages()
        h = self._write_json("hyp.json", hypothesis_manifest())
        c = self._write_json("cohort.json", cohort_manifest(entries))
        output = self.external / "eval_out"

        original_loader = m._load_cohort_entry

        def fake_loader(entry):
            return loaded_by_context[
                str(Path(entry["context_pack_directory"]).resolve())
            ]

        with patch.object(
            m,
            "validate_context_feature_pack_v1_package",
            return_value={},
        ), patch.object(
            m,
            "validate_forward_outcome_label_package",
            return_value={},
        ), patch.object(
            m,
            "_load_cohort_entry",
            side_effect=fake_loader,
        ):
            result = m.prepare_context_evaluation_engine_v1_package(
                repo_root=self.repo,
                hypothesis_manifest_json=h,
                cohort_manifest_json=c,
                output_directory=output,
                authorization=m.PACKAGE_AUTHORIZATION,
            )

        self.assertEqual(
            result["evaluation_decision"],
            "DESCRIPTIVE_ONLY_NO_EDGE_CLAIM",
        )
        validation = m.validate_context_evaluation_engine_v1_package(output)
        self.assertEqual(validation["manifest_entries"], 3)

        with (output / "evaluation_results.json").open("ab") as handle:
            handle.write(b"x")
        with self.assertRaises(m.ContextEvaluationEngineError):
            m.validate_context_evaluation_engine_v1_package(output)

    def test_28_source_inputs_not_modified_by_package(self):
        entries, loaded_by_context = self._make_minimal_packages()
        h = self._write_json("hyp4.json", hypothesis_manifest())
        c = self._write_json("cohort4.json", cohort_manifest(entries))
        h_sha = hashlib.sha256(h.read_bytes()).hexdigest()
        c_sha = hashlib.sha256(c.read_bytes()).hexdigest()

        def fake_loader(entry):
            return loaded_by_context[
                str(Path(entry["context_pack_directory"]).resolve())
            ]

        with patch.object(
            m,
            "_load_cohort_entry",
            side_effect=fake_loader,
        ):
            m.prepare_context_evaluation_engine_v1_package(
                repo_root=self.repo,
                hypothesis_manifest_json=h,
                cohort_manifest_json=c,
                output_directory=self.external / "eval_out2",
                authorization=m.PACKAGE_AUTHORIZATION,
            )

        self.assertEqual(hashlib.sha256(h.read_bytes()).hexdigest(), h_sha)
        self.assertEqual(hashlib.sha256(c.read_bytes()).hexdigest(), c_sha)

if __name__ == "__main__":
    unittest.main(verbosity=2)
