from __future__ import annotations

import csv
import hashlib
import json
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from src.long_side.long_primary_prospective_observation_source_adapter_v1 import (
    CANDIDATE_COLUMNS,
    REAL_SOURCE_ATTESTATION,
    REAL_SOURCE_AUTHORIZATION,
    SANDBOX_SOURCE_AUTHORIZATION,
    SOURCE_COLUMNS,
    SourceAdapterError,
    prepare_real_source_review_package,
    prepare_sandbox_validation_package,
    validate_review_package,
)


CAPTURED_AT = datetime(2026, 8, 4, 20, 15, tzinfo=timezone.utc)
PROSPECTIVE_START = datetime(2026, 8, 4, 19, 45, tzinfo=timezone.utc)


def utc_text(value: datetime) -> str:
    return value.isoformat()


def prepare_repo(root: Path) -> tuple[Path, Path]:
    (root / ".git").mkdir(parents=True)
    forward = root / "data" / "forward"
    forward.mkdir(parents=True)
    dataset = forward / "long_forward_observation_dataset_v1.csv"
    manifest = forward / "long_forward_observation_dataset_v1.manifest.csv"
    dataset.write_bytes(b"official-dataset-sentinel\n")
    manifest.write_bytes(b"official-manifest-sentinel\n")
    return dataset, manifest


def source_rows(
    count: int = 60,
    *,
    candidate_on_latest: bool = True,
    candidate_on_penultimate: bool = False,
) -> list[dict[str, str]]:
    latest_close = datetime(2026, 8, 4, 20, 0, tzinfo=timezone.utc)
    first_open = latest_close - timedelta(minutes=15 * count)
    rows: list[dict[str, str]] = []
    for index in range(count):
        open_time = first_open + timedelta(minutes=15 * index)
        close_time = open_time + timedelta(minutes=15)
        row = {
            "open_time_utc": utc_text(open_time),
            "close_time_utc": utc_text(close_time),
            "symbol": "BTCUSDT",
            "timeframe": "15m",
            "open": "100",
            "high": "102",
            "low": "99",
            "close": "101",
            "volume": "10",
            "candle_closed": "True",
        }
        rows.append(row)
    if candidate_on_penultimate:
        rows[-2].update(
            {
                "open": "98.8",
                "high": "101",
                "low": "98",
                "close": "100",
            }
        )
    if candidate_on_latest:
        rows[-1].update(
            {
                "open": "98.8",
                "high": "101",
                "low": "98",
                "close": "100",
            }
        )
    else:
        rows[-1].update(
            {
                "open": "100",
                "high": "101.5",
                "low": "99.2",
                "close": "100.5",
            }
        )
    return rows


def write_source(
    path: Path,
    rows: list[dict[str, str]],
    *,
    bom: bool = False,
) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    text_parts: list[str] = []
    from io import StringIO

    output = StringIO(newline="")
    writer = csv.DictWriter(
        output,
        fieldnames=list(SOURCE_COLUMNS),
        lineterminator="\n",
    )
    writer.writeheader()
    writer.writerows(rows)
    payload = output.getvalue().encode("utf-8")
    if bom:
        payload = b"\xef\xbb\xbf" + payload
    path.write_bytes(payload)
    return hashlib.sha256(payload).hexdigest()


def sandbox_append(
    repo: Path,
    source: Path,
    output: Path,
    *,
    captured_at: datetime = CAPTURED_AT,
    prospective_start: datetime = PROSPECTIVE_START,
    expected_source_sha256: str | None = None,
    authorization: str | None = SANDBOX_SOURCE_AUTHORIZATION,
):
    return prepare_sandbox_validation_package(
        repo_root=repo,
        source_csv=source,
        output_directory=output,
        captured_at_utc=utc_text(captured_at),
        prospective_start_utc=utc_text(prospective_start),
        expected_source_sha256=expected_source_sha256,
        authorization=authorization,
    )


class LongPrimaryProspectiveSourceAdapterTests(unittest.TestCase):
    def test_valid_sandbox_candidate_package(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            repo = root / "repo"
            repo.mkdir()
            dataset, manifest = prepare_repo(repo)
            source = root / "input.csv"
            source_hash = write_source(source, source_rows())
            output = root / "package"
            before = (dataset.read_bytes(), manifest.read_bytes())
            result = sandbox_append(
                repo,
                source,
                output,
                expected_source_sha256=source_hash,
            )
            self.assertTrue(result["candidate_detected"])
            self.assertEqual(result["candidate_rows_written"], 1)
            self.assertFalse(result["eligible_for_real_human_review"])
            self.assertFalse(result["official_dataset_write_performed"])
            self.assertEqual(
                before,
                (dataset.read_bytes(), manifest.read_bytes()),
            )
            validated = validate_review_package(output)
            self.assertTrue(validated["candidate_detected"])
            self.assertEqual(
                validated["package_scope"],
                "SANDBOX_VALIDATION_FIXTURE",
            )

    def test_valid_no_candidate_package(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            repo = root / "repo"
            repo.mkdir()
            prepare_repo(repo)
            source = root / "input.csv"
            write_source(source, source_rows(candidate_on_latest=False))
            output = root / "package"
            result = sandbox_append(repo, source, output)
            self.assertFalse(result["candidate_detected"])
            self.assertEqual(result["candidate_rows_written"], 0)
            with (output / "candidate_rows.csv").open(
                "r", encoding="utf-8", newline=""
            ) as handle:
                rows = list(csv.DictReader(handle))
            self.assertEqual(rows, [])

    def test_only_latest_closed_candle_is_evaluated(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            repo = root / "repo"
            repo.mkdir()
            prepare_repo(repo)
            source = root / "input.csv"
            write_source(
                source,
                source_rows(
                    candidate_on_latest=False,
                    candidate_on_penultimate=True,
                ),
            )
            output = root / "package"
            result = sandbox_append(repo, source, output)
            self.assertFalse(result["candidate_detected"])
            self.assertTrue(result["latest_candle_only_evaluated"])
            self.assertFalse(result["lookahead_used"])

    def test_insufficient_warmup_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            repo = root / "repo"
            repo.mkdir()
            prepare_repo(repo)
            source = root / "input.csv"
            write_source(source, source_rows(count=48))
            with self.assertRaises(SourceAdapterError) as caught:
                sandbox_append(repo, source, root / "package")
            self.assertEqual(
                caught.exception.code,
                "SOURCE_WARMUP_INSUFFICIENT",
            )

    def test_future_candle_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            repo = root / "repo"
            repo.mkdir()
            prepare_repo(repo)
            source = root / "input.csv"
            write_source(source, source_rows())
            with self.assertRaises(SourceAdapterError) as caught:
                sandbox_append(
                    repo,
                    source,
                    root / "package",
                    captured_at=datetime(
                        2026, 8, 4, 19, 59, tzinfo=timezone.utc
                    ),
                    prospective_start=datetime(
                        2026, 8, 4, 19, 45, tzinfo=timezone.utc
                    ),
                )
            self.assertEqual(
                caught.exception.code,
                "SOURCE_CONTAINS_FUTURE_CANDLE",
            )

    def test_stale_capture_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            repo = root / "repo"
            repo.mkdir()
            prepare_repo(repo)
            source = root / "input.csv"
            write_source(source, source_rows())
            with self.assertRaises(SourceAdapterError) as caught:
                sandbox_append(
                    repo,
                    source,
                    root / "package",
                    captured_at=datetime(
                        2026, 8, 4, 20, 31, tzinfo=timezone.utc
                    ),
                )
            self.assertEqual(caught.exception.code, "SOURCE_CAPTURE_STALE")

    def test_open_candle_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            repo = root / "repo"
            repo.mkdir()
            prepare_repo(repo)
            rows = source_rows()
            rows[-1]["candle_closed"] = "False"
            source = root / "input.csv"
            write_source(source, rows)
            with self.assertRaises(SourceAdapterError) as caught:
                sandbox_append(repo, source, root / "package")
            self.assertEqual(caught.exception.code, "OPEN_CANDLE_PROHIBITED")

    def test_invalid_ohlc_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            repo = root / "repo"
            repo.mkdir()
            prepare_repo(repo)
            rows = source_rows()
            rows[-1]["high"] = "97"
            source = root / "input.csv"
            write_source(source, rows)
            with self.assertRaises(SourceAdapterError) as caught:
                sandbox_append(repo, source, root / "package")
            self.assertEqual(caught.exception.code, "CANDLE_OHLC_INVALID")

    def test_unsorted_timestamps_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            repo = root / "repo"
            repo.mkdir()
            prepare_repo(repo)
            rows = source_rows()
            rows[-1]["open_time_utc"] = rows[-2]["open_time_utc"]
            rows[-1]["close_time_utc"] = rows[-2]["close_time_utc"]
            source = root / "input.csv"
            write_source(source, rows)
            with self.assertRaises(SourceAdapterError) as caught:
                sandbox_append(repo, source, root / "package")
            self.assertEqual(caught.exception.code, "CANDLE_ORDER_INVALID")

    def test_wrong_symbol_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            repo = root / "repo"
            repo.mkdir()
            prepare_repo(repo)
            rows = source_rows()
            rows[-1]["symbol"] = "ETHUSDT"
            source = root / "input.csv"
            write_source(source, rows)
            with self.assertRaises(SourceAdapterError) as caught:
                sandbox_append(repo, source, root / "package")
            self.assertEqual(caught.exception.code, "SOURCE_SYMBOL_INVALID")

    def test_wrong_timeframe_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            repo = root / "repo"
            repo.mkdir()
            prepare_repo(repo)
            rows = source_rows()
            rows[-1]["timeframe"] = "1h"
            source = root / "input.csv"
            write_source(source, rows)
            with self.assertRaises(SourceAdapterError) as caught:
                sandbox_append(repo, source, root / "package")
            self.assertEqual(
                caught.exception.code,
                "SOURCE_TIMEFRAME_INVALID",
            )

    def test_source_hash_mismatch_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            repo = root / "repo"
            repo.mkdir()
            prepare_repo(repo)
            source = root / "input.csv"
            write_source(source, source_rows())
            with self.assertRaises(SourceAdapterError) as caught:
                sandbox_append(
                    repo,
                    source,
                    root / "package",
                    expected_source_sha256="0" * 64,
                )
            self.assertEqual(caught.exception.code, "SOURCE_HASH_MISMATCH")

    def test_output_inside_repository_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            repo = root / "repo"
            repo.mkdir()
            prepare_repo(repo)
            source = root / "input.csv"
            write_source(source, source_rows())
            with self.assertRaises(SourceAdapterError) as caught:
                sandbox_append(
                    repo,
                    source,
                    repo / "reports" / "package",
                )
            self.assertEqual(
                caught.exception.code,
                "OUTPUT_INSIDE_REPOSITORY_PROHIBITED",
            )

    def test_existing_output_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            repo = root / "repo"
            repo.mkdir()
            prepare_repo(repo)
            source = root / "input.csv"
            write_source(source, source_rows())
            output = root / "package"
            output.mkdir()
            with self.assertRaises(SourceAdapterError) as caught:
                sandbox_append(repo, source, output)
            self.assertEqual(caught.exception.code, "OUTPUT_ALREADY_EXISTS")

    def test_real_package_requires_exact_attestation(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            repo = root / "repo"
            repo.mkdir()
            prepare_repo(repo)
            source = root / "input.csv"
            write_source(source, source_rows())
            with self.assertRaises(SourceAdapterError) as caught:
                prepare_real_source_review_package(
                    repo_root=repo,
                    source_csv=source,
                    output_directory=root / "package",
                    captured_at_utc=utc_text(CAPTURED_AT),
                    prospective_start_utc=utc_text(PROSPECTIVE_START),
                    source_system="BINANCE_PUBLIC_KLINES_CAPTURE",
                    source_capture_id="CAPTURE_001",
                    source_attestation="NOT_ATTESTED",
                    authorization=REAL_SOURCE_AUTHORIZATION,
                )
            self.assertEqual(
                caught.exception.code,
                "REAL_SOURCE_ATTESTATION_REQUIRED",
            )

    def test_real_path_marks_candidate_eligible_but_unconfirmed(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            repo = root / "repo"
            repo.mkdir()
            prepare_repo(repo)
            source = root / "input.csv"
            source_hash = write_source(source, source_rows())
            output = root / "package"
            result = prepare_real_source_review_package(
                repo_root=repo,
                source_csv=source,
                output_directory=output,
                captured_at_utc=utc_text(CAPTURED_AT),
                prospective_start_utc=utc_text(PROSPECTIVE_START),
                source_system="CONTROLLED_TEST_REAL_SOURCE_PATH",
                source_capture_id="CONTROLLED_TEST_CAPTURE_001",
                source_attestation=REAL_SOURCE_ATTESTATION,
                expected_source_sha256=source_hash,
                authorization=REAL_SOURCE_AUTHORIZATION,
            )
            self.assertTrue(result["eligible_for_real_human_review"])
            packet = json.loads(
                (output / "candidate_review_packet.json").read_text(
                    encoding="utf-8"
                )
            )
            self.assertFalse(packet["manual_confirmed"])
            self.assertEqual(packet["review_decision"], "PENDING")
            self.assertFalse(packet["official_dataset_write_allowed"])

    def test_manifest_tamper_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            repo = root / "repo"
            repo.mkdir()
            prepare_repo(repo)
            source = root / "input.csv"
            write_source(source, source_rows())
            output = root / "package"
            sandbox_append(repo, source, output)
            packet = output / "candidate_review_packet.json"
            packet.write_text("{}\n", encoding="utf-8", newline="\n")
            with self.assertRaises(SourceAdapterError) as caught:
                validate_review_package(output)
            self.assertEqual(
                caught.exception.code,
                "REVIEW_PACKAGE_HASH_MISMATCH",
            )

    def test_all_package_permissions_remain_false(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            repo = root / "repo"
            repo.mkdir()
            prepare_repo(repo)
            source = root / "input.csv"
            write_source(source, source_rows())
            output = root / "package"
            sandbox_append(repo, source, output)
            packet = json.loads(
                (output / "candidate_review_packet.json").read_text(
                    encoding="utf-8"
                )
            )
            for field in (
                "official_dataset_write_allowed",
                "evidence_persistence_allowed",
                "signal_generation_enabled",
                "live_alerts_allowed",
                "paper_trade_execution_allowed",
                "real_capital_allowed",
                "market_execution_allowed",
                "exchange_execution_allowed",
                "automation_allowed",
                "execution_allowed",
            ):
                self.assertIs(packet[field], False)
            with (output / "candidate_rows.csv").open(
                "r", encoding="utf-8", newline=""
            ) as handle:
                rows = list(csv.DictReader(handle))
            self.assertEqual(tuple(rows[0]), CANDIDATE_COLUMNS)

    def test_utf8_bom_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            repo = root / "repo"
            repo.mkdir()
            prepare_repo(repo)
            source = root / "input.csv"
            write_source(source, source_rows(), bom=True)
            with self.assertRaises(SourceAdapterError) as caught:
                sandbox_append(repo, source, root / "package")
            self.assertEqual(
                caught.exception.code,
                "SOURCE_ENCODING_INVALID",
            )

    def test_exact_local_authorization_is_required(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            repo = root / "repo"
            repo.mkdir()
            prepare_repo(repo)
            source = root / "input.csv"
            write_source(source, source_rows())
            with self.assertRaises(SourceAdapterError) as caught:
                sandbox_append(
                    repo,
                    source,
                    root / "package",
                    authorization=None,
                )
            self.assertEqual(
                caught.exception.code,
                "LOCAL_REVIEW_PACKAGE_AUTHORIZATION_REQUIRED",
            )


if __name__ == "__main__":
    unittest.main()
