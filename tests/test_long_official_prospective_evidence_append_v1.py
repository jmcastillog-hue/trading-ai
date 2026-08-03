from __future__ import annotations

import csv
import hashlib
import io
import json
import os
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import pandas as pd

from src.integration.openclaw_read_only_local_connection_v1 import (
    LocalConnectionError,
    validate_official_dataset,
)
from src.journal import operational_persistent_cycle_integration_v1 as operational
from src.long_side.long_official_prospective_evidence_append_v1 import (
    CANONICAL_COLUMNS,
    MANIFEST_SCHEMA_V2,
    OFFICIAL_APPEND_AUTHORIZATION,
    OFFICIAL_APPEND_ENVIRONMENT_VARIABLE,
    OFFICIAL_DATASET_RELATIVE_PATH,
    OFFICIAL_LOCK_RELATIVE_PATH,
    OFFICIAL_MANIFEST_RELATIVE_PATH,
    SANDBOX_APPEND_AUTHORIZATION,
    OfficialEvidenceAppendError,
    ReviewedLongEvidenceInput,
    append_official_prospective_evidence,
    append_sandbox_pair,
    validate_existing_pair,
)


ROOT = Path(__file__).resolve().parents[1]


def reviewed_input(**updates) -> ReviewedLongEvidenceInput:
    values = {
        "observation_id": "LONG-OFFICIAL-TEST-OBS-001",
        "observed_at_utc": "2026-08-02T20:00:00+00:00",
        "source_system": "UNIT_TEST",
        "source_artifact": "sandbox/reviewed_long_observation.json",
        "source_artifact_sha256": hashlib.sha256(b"artifact\n").hexdigest(),
        "source_row_hash": hashlib.sha256(b"row\n").hexdigest(),
        "candidate_id": "LONG_BASE_FAILED_BREAKDOWN_V1",
        "direction": "LONG",
        "symbol": "BTCUSDT",
        "timeframe": "15m",
        "observation_state": "OBSERVED_OPEN",
        "lifecycle_state": "OPEN",
        "entry_price": 100.0,
        "stop_price": 95.0,
        "target_price": 112.5,
        "invalidation_level": 95.0,
        "risk_reward": 2.5,
        "cost_profile": "RESEARCH_COST_AWARE_REFERENCE_ONLY",
        "market_context": "CONTROLLED_UNIT_TEST_CONTEXT",
        "activation_scope": "RESEARCH_ONLY_NO_EXECUTION",
        "signal_state": "CANDIDATE_OBSERVED",
        "audit_event_id": "AUDIT-LONG-OFFICIAL-TEST-001",
        "created_by": "UNIT_TEST",
        "reviewed_by": "HUMAN_REVIEW_FIXTURE",
        "notes": "Unit-test evidence only.",
    }
    values.update(updates)
    return ReviewedLongEvidenceInput(**values)


def prepare_sandbox(temp_root: Path) -> tuple[Path, Path]:
    dataset = temp_root / OFFICIAL_DATASET_RELATIVE_PATH
    manifest = temp_root / OFFICIAL_MANIFEST_RELATIVE_PATH
    dataset.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(ROOT / OFFICIAL_DATASET_RELATIVE_PATH, dataset)
    shutil.copy2(ROOT / OFFICIAL_MANIFEST_RELATIVE_PATH, manifest)
    return dataset, manifest


def append_once(temp_root: Path, **kwargs):
    return append_sandbox_pair(
        source_repo_root=ROOT,
        sandbox_root=temp_root,
        reviewed=kwargs.pop("reviewed", reviewed_input()),
        authorization=SANDBOX_APPEND_AUTHORIZATION,
        operation_id_factory=kwargs.pop(
            "operation_id_factory",
            lambda: "unit-test-append-operation-0001",
        ),
        clock=kwargs.pop(
            "clock",
            lambda: "2026-08-02T20:10:00+00:00",
        ),
        **kwargs,
    )


class LongOfficialProspectiveEvidenceAppendV1Tests(unittest.TestCase):
    def test_canonical_schema_has_exactly_54_columns(self) -> None:
        self.assertEqual(len(CANONICAL_COLUMNS), 54)
        self.assertEqual(CANONICAL_COLUMNS[0], "evidence_id")
        self.assertEqual(CANONICAL_COLUMNS[-1], "notes")

    def test_non_long_direction_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            prepare_sandbox(root)
            with self.assertRaises(OfficialEvidenceAppendError) as caught:
                append_once(root, reviewed=reviewed_input(direction="SHORT"))
            self.assertEqual(caught.exception.code, "DIRECTION_NOT_LONG")

    def test_missing_human_confirmation_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            prepare_sandbox(root)
            with self.assertRaises(OfficialEvidenceAppendError) as caught:
                append_once(
                    root,
                    reviewed=reviewed_input(manual_confirmed=False),
                )
            self.assertEqual(
                caught.exception.code,
                "HUMAN_OR_VALIDATION_GATE_FAILED",
            )

    def test_non_frozen_risk_reward_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            prepare_sandbox(root)
            with self.assertRaises(OfficialEvidenceAppendError) as caught:
                append_once(
                    root,
                    reviewed=reviewed_input(
                        target_price=110.0,
                        risk_reward=2.0,
                    ),
                )
            self.assertEqual(caught.exception.code, "RISK_REWARD_INVALID")

    def test_sandbox_append_creates_one_valid_manifest_v2_row(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            dataset, manifest = prepare_sandbox(root)
            result = append_once(root)
            profile = validate_existing_pair(dataset, manifest)
            self.assertEqual(result["target_evidence_row_count"], 1)
            self.assertEqual(profile["evidence_row_count"], 1)
            self.assertEqual(profile["manifest_schema_version"], MANIFEST_SCHEMA_V2)
            self.assertFalse(result["execution_allowed"])
            self.assertTrue(result["accepted_as_real_evidence"])

    def test_duplicate_event_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            prepare_sandbox(root)
            append_once(root)
            with self.assertRaises(OfficialEvidenceAppendError) as caught:
                append_once(
                    root,
                    operation_id_factory=lambda: "unit-test-duplicate-operation-01",
                    clock=lambda: "2026-08-02T20:11:00+00:00",
                )
            self.assertEqual(caught.exception.code, "DUPLICATE_EVIDENCE_EVENT")

    def test_failure_after_dataset_replace_restores_original_pair(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            dataset, manifest = prepare_sandbox(root)
            before_dataset = dataset.read_bytes()
            before_manifest = manifest.read_bytes()
            with self.assertRaises(OfficialEvidenceAppendError) as caught:
                append_once(root, fail_at="AFTER_DATASET_REPLACED")
            self.assertEqual(caught.exception.code, "INJECTED_FAILURE")
            self.assertTrue(caught.exception.rollback_performed)
            self.assertEqual(dataset.read_bytes(), before_dataset)
            self.assertEqual(manifest.read_bytes(), before_manifest)
            self.assertFalse((dataset.parent / OFFICIAL_LOCK_RELATIVE_PATH.name).exists())

    def test_failure_after_manifest_replace_restores_original_pair(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            dataset, manifest = prepare_sandbox(root)
            before_dataset = dataset.read_bytes()
            before_manifest = manifest.read_bytes()
            with self.assertRaises(OfficialEvidenceAppendError) as caught:
                append_once(root, fail_at="AFTER_MANIFEST_REPLACED")
            self.assertEqual(caught.exception.code, "INJECTED_FAILURE")
            self.assertTrue(caught.exception.rollback_performed)
            self.assertEqual(dataset.read_bytes(), before_dataset)
            self.assertEqual(manifest.read_bytes(), before_manifest)

    def test_existing_lock_blocks_append(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            dataset, _ = prepare_sandbox(root)
            lock = dataset.parent / OFFICIAL_LOCK_RELATIVE_PATH.name
            lock.write_text("{}\n", encoding="utf-8", newline="\n")
            with self.assertRaises(OfficialEvidenceAppendError) as caught:
                append_once(root)
            self.assertEqual(caught.exception.code, "LOCK_CONTENTION")

    def test_official_append_requires_environment_gate(self) -> None:
        original = os.environ.pop(OFFICIAL_APPEND_ENVIRONMENT_VARIABLE, None)
        try:
            with self.assertRaises(OfficialEvidenceAppendError) as caught:
                append_official_prospective_evidence(
                    repo_root=ROOT,
                    reviewed=reviewed_input(),
                    authorization=OFFICIAL_APPEND_AUTHORIZATION,
                )
            self.assertEqual(
                caught.exception.code,
                "OFFICIAL_APPEND_ENVIRONMENT_GATE_REQUIRED",
            )
        finally:
            if original is not None:
                os.environ[OFFICIAL_APPEND_ENVIRONMENT_VARIABLE] = original

    def test_read_only_reader_accepts_non_empty_manifest_v2(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            prepare_sandbox(root)
            append_once(root)
            profile = validate_official_dataset(root)
            self.assertEqual(profile["evidence_row_count"], 1)
            self.assertEqual(
                profile["state"],
                "PROSPECTIVE_EVIDENCE_COLLECTION_ACTIVE_READ_ONLY",
            )
            self.assertTrue(profile["append_only"])

    def test_read_only_reader_fails_closed_when_lock_is_active(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            dataset, _ = prepare_sandbox(root)
            lock = dataset.parent / OFFICIAL_LOCK_RELATIVE_PATH.name
            lock.write_text("{}\n", encoding="utf-8", newline="\n")
            with self.assertRaises(LocalConnectionError):
                validate_official_dataset(root)

    def test_manifest_with_execution_permission_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            dataset, manifest = prepare_sandbox(root)
            append_once(root)
            rows = list(
                csv.DictReader(
                    io.StringIO(manifest.read_text(encoding="utf-8"))
                )
            )
            rows[0]["execution_allowed"] = "True"
            output = io.StringIO(newline="")
            writer = csv.DictWriter(
                output,
                fieldnames=list(rows[0].keys()),
                lineterminator="\n",
            )
            writer.writeheader()
            writer.writerow(rows[0])
            manifest.write_text(output.getvalue(), encoding="utf-8", newline="\n")
            with self.assertRaises(OfficialEvidenceAppendError) as caught:
                validate_existing_pair(dataset, manifest)
            self.assertEqual(caught.exception.code, "MANIFEST_PERMISSION_INVALID")

    def test_evidence_hash_tampering_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            dataset, manifest = prepare_sandbox(root)
            append_once(root)
            rows = list(
                csv.DictReader(
                    io.StringIO(dataset.read_text(encoding="utf-8"))
                )
            )
            rows[0]["market_context"] = "TAMPERED"
            output = io.StringIO(newline="")
            writer = csv.DictWriter(
                output,
                fieldnames=list(CANONICAL_COLUMNS),
                lineterminator="\n",
            )
            writer.writeheader()
            writer.writerows(rows)
            dataset.write_text(output.getvalue(), encoding="utf-8", newline="\n")
            with self.assertRaises(OfficialEvidenceAppendError) as caught:
                validate_existing_pair(dataset, manifest)
            self.assertIn(
                caught.exception.code,
                {"EVIDENCE_HASH_INVALID", "MANIFEST_BINDING_MISMATCH"},
            )

    def test_operational_execution_flag_failure_remains_fail_closed(self) -> None:
        temp_paths = {
            "dataset_path": Path("unused.csv"),
            "backup_dir": Path("unused_backups"),
            "snapshot_dir": Path("unused_snapshots"),
        }
        adapter_summary = pd.DataFrame(
            [{"validation_passed": False, "input_ready_for_cycle": False}]
        )
        persistence_summary = pd.DataFrame(
            [{"dataset_write_required": False}]
        )
        dangerous_dataset = pd.DataFrame([{"signal_id": "danger"}])
        base_summary = pd.DataFrame(
            [
                {
                    "execution_allowed": False,
                    "integration_decision": "BASELINE",
                }
            ]
        )
        with (
            patch.object(operational, "operational_paths", return_value=temp_paths),
            patch.object(
                operational,
                "run_operational_input_file_validator_adapter",
                return_value=(
                    adapter_summary,
                    pd.DataFrame(),
                    pd.DataFrame(),
                    pd.DataFrame(),
                    pd.DataFrame(),
                    pd.DataFrame(),
                    pd.DataFrame(),
                ),
            ),
            patch.object(
                operational,
                "load_operational_dataset",
                return_value=pd.DataFrame(),
            ),
            patch.object(
                operational,
                "persist_operational_observations",
                return_value=(dangerous_dataset, persistence_summary),
            ),
            patch.object(
                operational,
                "create_backup_if_needed",
                return_value=(False, ""),
            ),
            patch.object(
                operational,
                "create_snapshot_if_needed",
                return_value=(False, ""),
            ),
            patch.object(
                operational,
                "build_integration_summary_df",
                return_value=base_summary,
            ),
            patch.object(
                operational,
                "all_execution_flags_false",
                return_value=False,
            ),
        ):
            result = operational.run_operational_persistent_cycle_integration()
        summary = result[0].iloc[0]
        self.assertFalse(bool(summary["execution_allowed"]))
        self.assertEqual(
            summary["integration_decision"],
            "OPERATIONAL_INTEGRATION_FAILED_EXECUTION_FLAGS_ENABLED",
        )


if __name__ == "__main__":
    unittest.main()
