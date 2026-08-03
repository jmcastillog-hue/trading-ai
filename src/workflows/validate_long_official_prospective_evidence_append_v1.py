from __future__ import annotations

import hashlib
import json
import os
import shutil
import tempfile
from pathlib import Path
from typing import Any, Callable

from src.integration.openclaw_read_only_local_connection_v1 import (
    validate_official_dataset,
)
from src.long_side.long_official_prospective_evidence_append_v1 import (
    CAPABILITY,
    MANIFEST_SCHEMA_V2,
    OFFICIAL_APPEND_AUTHORIZATION,
    OFFICIAL_DATASET_RELATIVE_PATH,
    OFFICIAL_MANIFEST_RELATIVE_PATH,
    SANDBOX_APPEND_AUTHORIZATION,
    OfficialEvidenceAppendError,
    ReviewedLongEvidenceInput,
    append_official_prospective_evidence,
    append_sandbox_pair,
)


ROOT = Path(__file__).resolve().parents[2]
OFFICIAL_DATASET_SHA256 = (
    "e3fa86a461fd46f4d66dc2e03f185e49b7b3438d3cbc33340c01f51310514ff1"
)
OFFICIAL_MANIFEST_SHA256 = (
    "99fc1f3f0e57bc11ec79c2c08481450a1bda1d7eaf8b84e85962fd25c3d4806e"
)


class ValidationFailure(RuntimeError):
    pass


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def controlled_reviewed_input() -> ReviewedLongEvidenceInput:
    source_artifact_bytes = b"controlled-reviewed-long-observation-v1\n"
    source_row_bytes = b"btc-long-observed-open-2026-08-02\n"
    return ReviewedLongEvidenceInput(
        observation_id="LONG-OFFICIAL-SANDBOX-OBS-001",
        observed_at_utc="2026-08-02T20:00:00+00:00",
        source_system="CONTROLLED_SANDBOX_VALIDATION",
        source_artifact="sandbox/controlled_reviewed_long_observation_v1.json",
        source_artifact_sha256=hashlib.sha256(source_artifact_bytes).hexdigest(),
        source_row_hash=hashlib.sha256(source_row_bytes).hexdigest(),
        candidate_id="LONG_BASE_FAILED_BREAKDOWN_V1",
        direction="LONG",
        symbol="BTCUSDT",
        timeframe="15m",
        observation_state="OBSERVED_OPEN",
        lifecycle_state="OPEN",
        entry_price=100.0,
        stop_price=95.0,
        target_price=112.5,
        invalidation_level=95.0,
        risk_reward=2.5,
        cost_profile="RESEARCH_COST_AWARE_REFERENCE_ONLY",
        market_context="CONTROLLED_SANDBOX_PROSPECTIVE_LONG_CONTEXT",
        activation_scope="RESEARCH_ONLY_NO_EXECUTION",
        signal_state="CANDIDATE_OBSERVED",
        audit_event_id="AUDIT-LONG-OFFICIAL-SANDBOX-001",
        created_by="TRADING_AI_DETERMINISTIC_VALIDATOR",
        reviewed_by="CONTROLLED_HUMAN_REVIEW_FIXTURE",
        notes="Controlled sandbox evidence. No official write and no execution.",
    )


def prepare_sandbox(source_root: Path, sandbox_root: Path) -> tuple[Path, Path]:
    dataset = sandbox_root / OFFICIAL_DATASET_RELATIVE_PATH
    manifest = sandbox_root / OFFICIAL_MANIFEST_RELATIVE_PATH
    dataset.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source_root / OFFICIAL_DATASET_RELATIVE_PATH, dataset)
    shutil.copy2(source_root / OFFICIAL_MANIFEST_RELATIVE_PATH, manifest)
    return dataset, manifest


def add_check(
    checks: list[dict[str, Any]],
    name: str,
    operation: Callable[[], Any],
) -> Any:
    try:
        value = operation()
    except Exception as exc:
        checks.append(
            {
                "check": name,
                "passed": False,
                "details": f"{type(exc).__name__}: {exc}",
            }
        )
        raise
    checks.append({"check": name, "passed": True, "details": "passed"})
    return value


def assert_true(condition: bool, message: str) -> None:
    if not condition:
        raise ValidationFailure(message)


def assert_failed_with_code(operation: Callable[[], Any], expected_code: str) -> OfficialEvidenceAppendError:
    try:
        operation()
    except OfficialEvidenceAppendError as exc:
        assert_true(exc.code == expected_code, f"Expected {expected_code}, got {exc.code}")
        return exc
    raise ValidationFailure(f"Expected failure code {expected_code}")


def run_validation(root: Path | str = ROOT) -> dict[str, Any]:
    source_root = Path(root).resolve()
    dataset_path = source_root / OFFICIAL_DATASET_RELATIVE_PATH
    manifest_path = source_root / OFFICIAL_MANIFEST_RELATIVE_PATH
    before_dataset_hash = sha256_path(dataset_path)
    before_manifest_hash = sha256_path(manifest_path)
    checks: list[dict[str, Any]] = []

    add_check(
        checks,
        "official_dataset_initial_hash",
        lambda: assert_true(
            before_dataset_hash == OFFICIAL_DATASET_SHA256,
            f"Unexpected official dataset SHA-256: {before_dataset_hash}",
        ),
    )
    add_check(
        checks,
        "official_manifest_initial_hash",
        lambda: assert_true(
            before_manifest_hash == OFFICIAL_MANIFEST_SHA256,
            f"Unexpected official manifest SHA-256: {before_manifest_hash}",
        ),
    )
    official_profile = add_check(
        checks,
        "current_v1_pair_read_only_validation",
        lambda: validate_official_dataset(source_root),
    )
    assert_true(official_profile["evidence_row_count"] == 0, "Official dataset is not empty before sandbox validation")

    with tempfile.TemporaryDirectory(prefix="long_official_append_success_") as temp:
        sandbox = Path(temp)
        prepare_sandbox(source_root, sandbox)
        result = add_check(
            checks,
            "sandbox_append_success",
            lambda: append_sandbox_pair(
                source_repo_root=source_root,
                sandbox_root=sandbox,
                reviewed=controlled_reviewed_input(),
                authorization=SANDBOX_APPEND_AUTHORIZATION,
                operation_id_factory=lambda: "sandbox-success-operation-0001",
                clock=lambda: "2026-08-02T20:10:00+00:00",
            ),
        )
        assert_true(result["target_evidence_row_count"] == 1, "Sandbox append did not create exactly one row")
        appended_profile = add_check(
            checks,
            "read_only_reader_accepts_manifest_v2",
            lambda: validate_official_dataset(sandbox),
        )
        assert_true(appended_profile["manifest_schema_version"] == MANIFEST_SCHEMA_V2, "Reader did not recognize manifest V2")
        assert_true(appended_profile["state"] == "PROSPECTIVE_EVIDENCE_COLLECTION_ACTIVE_READ_ONLY", "Reader state is not active read-only evidence collection")
        add_check(
            checks,
            "duplicate_event_rejected",
            lambda: assert_failed_with_code(
                lambda: append_sandbox_pair(
                    source_repo_root=source_root,
                    sandbox_root=sandbox,
                    reviewed=controlled_reviewed_input(),
                    authorization=SANDBOX_APPEND_AUTHORIZATION,
                    operation_id_factory=lambda: "sandbox-duplicate-operation-01",
                    clock=lambda: "2026-08-02T20:11:00+00:00",
                ),
                "DUPLICATE_EVIDENCE_EVENT",
            ),
        )

    for failpoint, operation_id in (
        ("AFTER_DATASET_REPLACED", "rollback-dataset-operation-01"),
        ("AFTER_MANIFEST_REPLACED", "rollback-manifest-operation-01"),
    ):
        with tempfile.TemporaryDirectory(prefix="long_official_append_rollback_") as temp:
            sandbox = Path(temp)
            sandbox_dataset, sandbox_manifest = prepare_sandbox(source_root, sandbox)
            original_dataset = sandbox_dataset.read_bytes()
            original_manifest = sandbox_manifest.read_bytes()
            failure = add_check(
                checks,
                f"{failpoint.lower()}_fails_closed",
                lambda failpoint=failpoint, operation_id=operation_id, sandbox=sandbox: assert_failed_with_code(
                    lambda: append_sandbox_pair(
                        source_repo_root=source_root,
                        sandbox_root=sandbox,
                        reviewed=controlled_reviewed_input(),
                        authorization=SANDBOX_APPEND_AUTHORIZATION,
                        fail_at=failpoint,
                        operation_id_factory=lambda: operation_id,
                        clock=lambda: "2026-08-02T20:12:00+00:00",
                    ),
                    "INJECTED_FAILURE",
                ),
            )
            assert_true(failure.rollback_performed, f"{failpoint} did not report rollback")
            assert_true(sandbox_dataset.read_bytes() == original_dataset, f"{failpoint} did not restore dataset")
            assert_true(sandbox_manifest.read_bytes() == original_manifest, f"{failpoint} did not restore manifest")
            residuals = [path for path in sandbox_dataset.parent.iterdir() if path.suffix in {".tmp", ".bak"} or path.name.endswith(".lock")]
            assert_true(not residuals, f"{failpoint} left residual artifacts: {residuals}")

    environment_gate_name = "TRADING_AI_OFFICIAL_LONG_EVIDENCE_APPEND_ALLOWED"
    original_environment_gate = os.environ.pop(environment_gate_name, None)
    try:
        add_check(
            checks,
            "official_append_requires_environment_gate",
            lambda: assert_failed_with_code(
                lambda: append_official_prospective_evidence(
                    repo_root=source_root,
                    reviewed=controlled_reviewed_input(),
                    authorization=OFFICIAL_APPEND_AUTHORIZATION,
                    operation_id_factory=lambda: "official-blocked-operation-01",
                    clock=lambda: "2026-08-02T20:13:00+00:00",
                ),
                "OFFICIAL_APPEND_ENVIRONMENT_GATE_REQUIRED",
            ),
        )
    finally:
        if original_environment_gate is not None:
            os.environ[environment_gate_name] = original_environment_gate

    operational_source = (
        source_root / "src/journal/operational_persistent_cycle_integration_v1.py"
    ).read_text(encoding="utf-8")
    failure_block = (
        'if not all_execution_flags_false(final_dataset_df):\n'
        '        integration_summary_df.loc[:, "execution_allowed"] = False\n'
    )
    add_check(
        checks,
        "operational_execution_failure_is_fail_closed",
        lambda: assert_true(
            failure_block in operational_source,
            "Operational failure block does not force execution_allowed=False",
        ),
    )

    readme = (source_root / "README.md").read_text(encoding="utf-8")
    stale_markers = (
        "The only permitted next phase is:",
        "The only permitted next phase is\n",
        "The only allowed next phase is\n",
    )
    add_check(
        checks,
        "readme_historical_next_phase_markers_removed",
        lambda: assert_true(
            not any(marker in readme for marker in stale_markers),
            "README still presents an obsolete historical phase as the only current route",
        ),
    )
    add_check(
        checks,
        "readme_records_append_capability",
        lambda: assert_true(
            "LONG official prospective evidence append capability" in readme,
            "README does not record the new capability",
        ),
    )

    after_dataset_hash = sha256_path(dataset_path)
    after_manifest_hash = sha256_path(manifest_path)
    add_check(
        checks,
        "official_dataset_unchanged",
        lambda: assert_true(after_dataset_hash == before_dataset_hash, "Official dataset changed during validation"),
    )
    add_check(
        checks,
        "official_manifest_unchanged",
        lambda: assert_true(after_manifest_hash == before_manifest_hash, "Official manifest changed during validation"),
    )

    failed = [check for check in checks if not check["passed"]]
    if failed:
        raise ValidationFailure(f"Validation failed: {failed}")

    return {
        "decision": "LONG_OFFICIAL_PROSPECTIVE_EVIDENCE_APPEND_V1_VALIDATED_IN_SANDBOX",
        "capability": CAPABILITY,
        "checks": len(checks),
        "failed_checks": 0,
        "blockers": 0,
        "official_dataset_sha256": after_dataset_hash,
        "official_manifest_sha256": after_manifest_hash,
        "official_dataset_changed": False,
        "official_manifest_changed": False,
        "official_evidence_rows_written": 0,
        "sandbox_evidence_rows_written": 1,
        "rollback_failpoints_validated": 2,
        "read_only_reader_supports_non_empty_v2": True,
        "operational_failure_execution_allowed": False,
        "paper_trade_execution_allowed": False,
        "real_capital_allowed": False,
        "market_execution_allowed": False,
        "exchange_execution_allowed": False,
        "automation_allowed": False,
        "execution_allowed": False,
        "human_review_required": True,
    }


def main() -> int:
    try:
        result = run_validation(ROOT)
    except Exception as exc:
        print(
            json.dumps(
                {
                    "decision": "LONG_OFFICIAL_PROSPECTIVE_EVIDENCE_APPEND_V1_VALIDATION_FAILED",
                    "error_type": type(exc).__name__,
                    "error": str(exc),
                    "official_dataset_write_performed": False,
                    "execution_allowed": False,
                },
                indent=2,
                sort_keys=True,
            )
        )
        return 1
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
