from __future__ import annotations

import csv
import tempfile
import unittest
from pathlib import Path

from src.validation import (
    frozen_recovery_candidate_historical_input_manifest_binding_and_integrity_validation_v1
    as binding,
)


class HistoricalInputManifestBindingIntegrityTests(unittest.TestCase):
    def write_dataset(self, path: Path, rows: list[tuple[str, ...]]) -> None:
        with path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.writer(handle, lineterminator="\n")
            writer.writerow(binding.CANONICAL_COLUMNS)
            writer.writerows(rows)

    def valid_row(self, open_time: str, close_time: str) -> tuple[str, ...]:
        return (open_time, "100", "110", "90", "105", "1.5", close_time)

    def test_phase_and_source_anchors_are_exact(self) -> None:
        self.assertEqual(binding.PHASE, "10.42R.2J")
        self.assertEqual(
            binding.SOURCE_PHASE_2I_COMMIT,
            "ddcd059bd747891c47e2738974b1b42465ba5adf",
        )
        self.assertEqual(
            binding.SOURCE_PHASE_2I_HARNESS_DESIGN_SHA256,
            "ee62064148bdb119c7b3390d7dab3db338b4d5b50a1eaf7adb44d4c9dffd5dbb",
        )

    def test_binding_root_is_exact_and_deterministic(self) -> None:
        self.assertEqual(
            binding.BINDING_ROOT_SHA256,
            "5c1ccb1c9fecdad2e196558a946944f5b9f89f258c5ef591a65d4c4c480d8c14",
        )
        self.assertEqual(binding.BINDING_ROOT_SHA256, binding.build_binding_root_sha256())

    def test_expected_registry_is_exact_three_by_three(self) -> None:
        self.assertEqual(len(binding.EXPECTED_DATASETS), 9)
        pairs = {
            (item["symbol"], item["timeframe"])
            for item in binding.EXPECTED_DATASETS.values()
        }
        self.assertEqual(
            pairs,
            {
                (symbol, timeframe)
                for symbol in binding.SYMBOLS
                for timeframe in binding.TIMEFRAMES
            },
        )

    def test_declared_gap_total_is_eighteen(self) -> None:
        self.assertEqual(
            sum(item["missing_interval_count"] for item in binding.EXPECTED_DATASETS.values()),
            18,
        )

    def test_expected_row_counts_reconcile_to_calendar(self) -> None:
        for item in binding.EXPECTED_DATASETS.values():
            self.assertEqual(
                item["row_count"] + item["missing_interval_count"],
                binding.expected_calendar_rows(item["timeframe"]),
            )

    def test_manifest_has_exact_twenty_five_fields(self) -> None:
        self.assertEqual(len(binding.MANIFEST_FIELDS), 25)
        self.assertEqual(binding.MANIFEST_FIELDS[0], "slot_id")
        self.assertEqual(binding.MANIFEST_FIELDS[-1], "manifest_row_sha256")

    def test_limited_permissions_are_exact(self) -> None:
        enabled = {name for name, value in binding.PERMISSIONS.items() if value}
        self.assertEqual(enabled, binding.ALLOWED_TRUE_PERMISSIONS)
        self.assertFalse(binding.PERMISSIONS["historical_evaluation_allowed"])
        self.assertFalse(binding.PERMISSIONS["paper_trade_execution_allowed"])
        self.assertFalse(binding.PERMISSIONS["real_capital_allowed"])

    def test_audit_artifact_hashes_are_exact_hex(self) -> None:
        self.assertEqual(len(binding.EXPECTED_AUDIT_ARTIFACT_HASHES), 3)
        for value in binding.EXPECTED_AUDIT_ARTIFACT_HASHES.values():
            self.assertEqual(len(value), 64)
            int(value, 16)

    def test_dataset_paths_and_hashes_are_unique(self) -> None:
        paths = [item["relative_path"] for item in binding.EXPECTED_DATASETS.values()]
        hashes = [item["file_sha256"] for item in binding.EXPECTED_DATASETS.values()]
        self.assertEqual(len(paths), len(set(paths)))
        self.assertEqual(len(hashes), len(set(hashes)))

    def test_manifest_row_hash_excludes_only_its_hash_field(self) -> None:
        row = {field: field for field in binding.MANIFEST_FIELDS}
        first = binding.canonical_manifest_row_sha256(row)
        row["manifest_row_sha256"] = "different"
        second = binding.canonical_manifest_row_sha256(row)
        self.assertEqual(first, second)
        row["symbol"] = "changed"
        self.assertNotEqual(first, binding.canonical_manifest_row_sha256(row))

    def test_parse_utc_requires_timezone(self) -> None:
        parsed = binding.parse_utc("2022-01-01T00:00:00.000000+00:00")
        self.assertEqual(parsed.utcoffset().total_seconds(), 0)
        with self.assertRaises(binding.BindingIntegrityFailure):
            binding.parse_utc("2022-01-01T00:00:00")

    def test_validate_ohlcv_accepts_valid_row(self) -> None:
        binding.validate_ohlcv(
            {"open": "100", "high": "110", "low": "90", "close": "105", "volume": "2"}
        )

    def test_validate_ohlcv_rejects_negative_volume(self) -> None:
        with self.assertRaises(binding.BindingIntegrityFailure):
            binding.validate_ohlcv(
                {"open": "100", "high": "110", "low": "90", "close": "105", "volume": "-1"}
            )

    def test_scan_dataset_detects_one_declared_gap(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "dataset.csv"
            self.write_dataset(
                path,
                [
                    self.valid_row(
                        "2022-01-01T00:00:00.000000+00:00",
                        "2022-01-01T00:14:59.999000+00:00",
                    ),
                    self.valid_row(
                        "2022-01-01T00:30:00.000000+00:00",
                        "2022-01-01T00:44:59.999000+00:00",
                    ),
                ],
            )
            scan = binding.scan_dataset(path, "15m")
            self.assertEqual(scan["row_count"], 2)
            self.assertEqual(scan["missing_interval_count"], 1)
            self.assertEqual(
                scan["missing_open_times"],
                ("2022-01-01T00:15:00.000000+00:00",),
            )

    def test_scan_dataset_rejects_duplicate_open(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "dataset.csv"
            row = self.valid_row(
                "2022-01-01T00:00:00.000000+00:00",
                "2022-01-01T00:14:59.999000+00:00",
            )
            self.write_dataset(path, [row, row])
            with self.assertRaises(binding.BindingIntegrityFailure):
                binding.scan_dataset(path, "15m")

    def test_scan_dataset_rejects_irregular_interval(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "dataset.csv"
            self.write_dataset(
                path,
                [
                    self.valid_row(
                        "2022-01-01T00:00:00.000000+00:00",
                        "2022-01-01T00:14:59.999000+00:00",
                    ),
                    self.valid_row(
                        "2022-01-01T00:16:00.000000+00:00",
                        "2022-01-01T00:30:59.999000+00:00",
                    ),
                ],
            )
            with self.assertRaises(binding.BindingIntegrityFailure):
                binding.scan_dataset(path, "15m")

    def test_acquisition_source_hash_is_exact(self) -> None:
        path = Path(
            "src/validation/"
            "frozen_recovery_candidate_historical_input_acquisition_and_binding_v1.py"
        )
        self.assertTrue(path.is_file())
        self.assertEqual(
            binding.normalized_source_sha256(path),
            binding.ACQUISITION_SOURCE_SHA256,
        )

    def test_next_phase_is_controlled_known_evidence_evaluation(self) -> None:
        self.assertIn("2K", binding.RECOMMENDED_NEXT_PHASE)
        self.assertIn("CONTROLLED_KNOWN_EVIDENCE_EVALUATION", binding.RECOMMENDED_NEXT_PHASE)


if __name__ == "__main__":
    unittest.main()
