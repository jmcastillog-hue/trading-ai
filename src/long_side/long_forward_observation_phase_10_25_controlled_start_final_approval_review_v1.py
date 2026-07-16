from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

import pandas as pd

from src.long_side.long_forward_observation_dataset_bootstrap_v1 import (
    OFFICIAL_DATASET_PATH,
    PRIMARY_RESEARCH_CANDIDATE,
)
from src.long_side.long_forward_observation_phase_10_24_controlled_start_dry_run_output_integrity_review_v1 import (
    READY_DECISION as SOURCE_READY_DECISION,
)


REPORTS_DIR = Path("reports/p10_25_start_final_approval_review_v1")
PHASE_10_24_REPORTS_DIR = Path(
    "reports/p10_24_start_dry_run_output_integrity_review_v1"
)

PHASE_10_24_DOC_PATH = Path(
    "docs/PHASE_10_LONG_FORWARD_OBSERVATION_CONTROLLED_START_DRY_RUN_OUTPUT_INTEGRITY_REVIEW.md"
)
PHASE_10_25_DOC_PATH = Path(
    "docs/PHASE_10_LONG_FORWARD_OBSERVATION_CONTROLLED_START_FINAL_APPROVAL_REVIEW.md"
)

SOURCE_SUMMARY_PATH = (
    PHASE_10_24_REPORTS_DIR / "start_dry_run_output_integrity_summary_v1.csv"
)
SOURCE_DRY_RUN_OUTPUT_PATH = (
    PHASE_10_24_REPORTS_DIR / "phase_10_23_source_dry_run_output_v1.csv"
)
SOURCE_ARTIFACT_METADATA_PATH = (
    PHASE_10_24_REPORTS_DIR / "source_dry_run_artifact_metadata_v1.csv"
)
SOURCE_VALIDATIONS_PATH = (
    PHASE_10_24_REPORTS_DIR / "start_dry_run_output_integrity_validations_v1.csv"
)
SOURCE_CONTROLS_PATH = (
    PHASE_10_24_REPORTS_DIR / "start_dry_run_output_integrity_controls_v1.csv"
)
SOURCE_RULES_PATH = (
    PHASE_10_24_REPORTS_DIR / "start_dry_run_output_integrity_rules_v1.csv"
)
SOURCE_REQUIREMENTS_PATH = (
    PHASE_10_24_REPORTS_DIR / "start_dry_run_output_integrity_requirements_v1.csv"
)
SOURCE_GUARD_MATRIX_PATH = (
    PHASE_10_24_REPORTS_DIR / "start_dry_run_output_integrity_guard_matrix_v1.csv"
)
SOURCE_DECISION_PATH = (
    PHASE_10_24_REPORTS_DIR / "start_dry_run_output_integrity_decision_v1.csv"
)
SOURCE_CHECKS_PATH = (
    PHASE_10_24_REPORTS_DIR / "start_dry_run_output_integrity_checks_v1.csv"
)

FINAL_APPROVAL_REVIEW_STATUS = (
    "LONG_FORWARD_OBSERVATION_CONTROLLED_START_FINAL_APPROVAL_REVIEW_ONLY"
)
READY_DECISION = (
    "CONTROLLED_FORWARD_OBSERVATION_START_FINAL_APPROVAL_REVIEW_"
    "READY_FOR_CONTROLLED_FORWARD_OBSERVATION_START_RUN"
)
BLOCKED_DECISION = (
    "CONTROLLED_FORWARD_OBSERVATION_START_FINAL_APPROVAL_REVIEW_BLOCKED"
)
RECOMMENDED_NEXT_PHASE = (
    "PHASE_10_26_LONG_FORWARD_OBSERVATION_CONTROLLED_START_RUN_V1"
)

EXPECTED_SOURCE_RUN_SCOPE = (
    "CONTROLLED_FORWARD_OBSERVATION_START_DRY_RUN_ONLY"
)
EXPECTED_SOURCE_EVIDENCE_SCOPE = "DRY_RUN_ONLY_NOT_REAL_EVIDENCE"
EXPECTED_SOURCE_VALIDATION_STATUS = "CONTROLLED_START_DRY_RUN_ROW_CREATED"

EXPECTED_SOURCE_COUNTS = {
    "integrity_validation_rows": 30,
    "integrity_control_rows": 20,
    "integrity_rule_rows": 14,
    "integrity_requirement_rows": 42,
    "integrity_guard_rows": 31,
}

EXPECTED_FALSE_GUARDS = {
    "controlled_forward_observation_start_run_performed": False,
    "controlled_forward_observation_start_performed": False,
    "forward_observation_start_allowed": False,
    "forward_observation_started": False,
    "official_dataset_write_allowed": False,
    "official_dataset_write_performed": False,
    "real_forward_dataset_created": False,
    "real_forward_signals_recorded": False,
    "journal_real_rows_accepted": False,
    "accepted_as_real_evidence": False,
    "evidence_persistence_allowed": False,
    "evidence_write_performed": False,
    "signal_generation_enabled": False,
    "live_alerts_allowed": False,
    "paper_trading_enabled": False,
    "long_strategy_approved": False,
    "long_entries_approved": False,
    "long_side_established": False,
    "paper_trade_execution_allowed": False,
    "real_capital_allowed": False,
    "market_execution_allowed": False,
    "exchange_execution_allowed": False,
    "automation_allowed": False,
    "execution_allowed": False,
    "real_entries_approved": False,
    "total_project_completed": False,
}

SOURCE_REQUIRED_PATHS = [
    SOURCE_SUMMARY_PATH,
    SOURCE_DRY_RUN_OUTPUT_PATH,
    SOURCE_ARTIFACT_METADATA_PATH,
    SOURCE_VALIDATIONS_PATH,
    SOURCE_CONTROLS_PATH,
    SOURCE_RULES_PATH,
    SOURCE_REQUIREMENTS_PATH,
    SOURCE_GUARD_MATRIX_PATH,
    SOURCE_DECISION_PATH,
    SOURCE_CHECKS_PATH,
]


def build_check(
    check_group: str,
    check_name: str,
    passed: bool,
    severity: str,
    details: str,
) -> dict[str, Any]:
    return {
        "check_group": check_group,
        "check_name": check_name,
        "passed": bool(passed),
        "severity": severity,
        "details": details,
        "blocker": severity == "ERROR" and not bool(passed),
    }


def safe_bool(value: Any, default: bool = False) -> bool:
    if isinstance(value, bool):
        return value

    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in {"true", "1", "yes", "y"}:
            return True
        if normalized in {"false", "0", "no", "n", ""}:
            return False

    try:
        if pd.isna(value):
            return default
    except Exception:
        pass

    try:
        return bool(value)
    except Exception:
        return default


def safe_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None or pd.isna(value):
            return default
        return float(value)
    except Exception:
        return default


def read_csv_if_exists(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()

    try:
        return pd.read_csv(path)
    except Exception:
        return pd.DataFrame()


def dataframe_all_passed(df: pd.DataFrame) -> bool:
    return (
        not df.empty
        and "passed" in df.columns
        and df["passed"].map(lambda value: safe_bool(value, False)).all()
    )


def sha256_file(path: Path) -> str:
    if not path.exists() or not path.is_file():
        return ""

    digest = hashlib.sha256()

    with path.open("rb") as file_handle:
        while True:
            chunk = file_handle.read(1024 * 1024)
            if not chunk:
                break
            digest.update(chunk)

    return digest.hexdigest()


def build_source_manifest() -> pd.DataFrame:
    rows: list[dict[str, Any]] = []

    for position, path in enumerate(SOURCE_REQUIRED_PATHS, start=1):
        exists = path.exists() and path.is_file()
        size_bytes = path.stat().st_size if exists else 0
        file_hash = sha256_file(path) if exists else ""

        rows.append(
            {
                "manifest_position": position,
                "artifact_name": path.name,
                "artifact_path": str(path),
                "artifact_exists": exists,
                "artifact_size_bytes": int(size_bytes),
                "artifact_non_empty": bool(size_bytes > 0),
                "artifact_sha256": file_hash,
                "artifact_sha256_valid": len(file_hash) == 64,
            }
        )

    return pd.DataFrame(rows)


def manifest_digest(manifest_df: pd.DataFrame) -> str:
    if manifest_df.empty:
        return ""

    required_columns = [
        "artifact_name",
        "artifact_path",
        "artifact_size_bytes",
        "artifact_sha256",
    ]

    if any(column not in manifest_df.columns for column in required_columns):
        return ""

    normalized = (
        manifest_df[required_columns]
        .astype(str)
        .sort_values(by=["artifact_name", "artifact_path"])
        .to_csv(index=False)
        .encode("utf-8")
    )

    return hashlib.sha256(normalized).hexdigest()


def build_final_approval_validations(
    source_summary_df: pd.DataFrame,
    source_dry_run_output_df: pd.DataFrame,
    source_artifact_metadata_df: pd.DataFrame,
    source_validations_df: pd.DataFrame,
    source_controls_df: pd.DataFrame,
    source_rules_df: pd.DataFrame,
    source_requirements_df: pd.DataFrame,
    source_guard_matrix_df: pd.DataFrame,
    source_decision_df: pd.DataFrame,
    source_manifest_before_df: pd.DataFrame,
    source_manifest_after_df: pd.DataFrame,
    official_dataset_absent: bool,
) -> pd.DataFrame:
    summary = (
        source_summary_df.iloc[0].to_dict()
        if not source_summary_df.empty
        else {}
    )
    dry_run_output = (
        source_dry_run_output_df.iloc[0].to_dict()
        if not source_dry_run_output_df.empty
        else {}
    )
    artifact_metadata = (
        source_artifact_metadata_df.iloc[0].to_dict()
        if not source_artifact_metadata_df.empty
        else {}
    )
    decision = (
        source_decision_df.iloc[0].to_dict()
        if not source_decision_df.empty
        else {}
    )

    manifest_before_digest = manifest_digest(source_manifest_before_df)
    manifest_after_digest = manifest_digest(source_manifest_after_df)

    all_source_artifacts_exist = (
        not source_manifest_before_df.empty
        and source_manifest_before_df["artifact_exists"]
        .map(lambda value: safe_bool(value, False))
        .all()
    )
    all_source_artifacts_non_empty = (
        not source_manifest_before_df.empty
        and source_manifest_before_df["artifact_non_empty"]
        .map(lambda value: safe_bool(value, False))
        .all()
    )
    all_source_hashes_valid = (
        not source_manifest_before_df.empty
        and source_manifest_before_df["artifact_sha256_valid"]
        .map(lambda value: safe_bool(value, False))
        .all()
    )
    source_artifacts_stable = (
        bool(manifest_before_digest)
        and manifest_before_digest == manifest_after_digest
    )

    entry_price = safe_float(dry_run_output.get("entry_price"))
    stop_price = safe_float(dry_run_output.get("stop_price"))
    target_price = safe_float(dry_run_output.get("target_price"))
    risk_reward = safe_float(dry_run_output.get("risk_reward"))
    expected_risk_reward = (
        round((target_price - entry_price) / (entry_price - stop_price), 4)
        if entry_price > stop_price
        else 0.0
    )

    source_counts_valid = all(
        int(safe_float(summary.get(field_name), -1)) == expected_count
        for field_name, expected_count in EXPECTED_SOURCE_COUNTS.items()
    )

    source_operational_locks_valid = all(
        safe_bool(dry_run_output.get(field_name, True), True) is False
        for field_name in EXPECTED_FALSE_GUARDS
        if field_name
        not in {
            "controlled_forward_observation_start_run_performed",
            "controlled_forward_observation_start_performed",
        }
    )

    source_hash = str(artifact_metadata.get("artifact_sha256", ""))
    source_artifact_path = Path(
        str(artifact_metadata.get("artifact_path", ""))
    )
    actual_source_hash = sha256_file(source_artifact_path)

    rows = [
        (
            "source_artifacts_exist",
            all_source_artifacts_exist,
            f"artifact_count={len(source_manifest_before_df)}",
        ),
        (
            "source_artifacts_non_empty",
            all_source_artifacts_non_empty,
            f"artifact_count={len(source_manifest_before_df)}",
        ),
        (
            "source_artifact_hashes_valid",
            all_source_hashes_valid,
            f"artifact_count={len(source_manifest_before_df)}",
        ),
        (
            "source_artifacts_stable_during_review",
            source_artifacts_stable,
            (
                f"manifest_before={manifest_before_digest},"
                f"manifest_after={manifest_after_digest}"
            ),
        ),
        (
            "phase_10_24_validation_passed",
            safe_bool(summary.get("validation_passed", False)),
            str(summary.get("validation_decision", "")),
        ),
        (
            "source_integrity_review_performed",
            safe_bool(
                summary.get(
                    "controlled_forward_observation_start_dry_run_output_integrity_review_performed",
                    False,
                )
            ),
            str(
                summary.get(
                    "controlled_forward_observation_start_dry_run_output_integrity_review_performed",
                    "",
                )
            ),
        ),
        (
            "source_integrity_review_passed",
            safe_bool(
                summary.get(
                    "controlled_forward_observation_start_dry_run_output_integrity_review_passed",
                    False,
                )
            ),
            str(
                summary.get(
                    "controlled_forward_observation_start_dry_run_output_integrity_review_passed",
                    "",
                )
            ),
        ),
        (
            "source_integrity_review_decision_valid",
            str(
                summary.get(
                    "controlled_forward_observation_start_dry_run_output_integrity_review_decision",
                    "",
                )
            )
            == SOURCE_READY_DECISION,
            str(
                summary.get(
                    "controlled_forward_observation_start_dry_run_output_integrity_review_decision",
                    "",
                )
            ),
        ),
        (
            "source_future_final_approval_review_allowed",
            safe_bool(
                summary.get(
                    "future_controlled_forward_observation_start_final_approval_review_allowed",
                    False,
                )
            ),
            str(
                summary.get(
                    "future_controlled_forward_observation_start_final_approval_review_allowed",
                    "",
                )
            ),
        ),
        (
            "source_decision_table_consistent",
            (
                not source_decision_df.empty
                and safe_bool(
                    decision.get(
                        "controlled_forward_observation_start_dry_run_output_integrity_review_passed",
                        False,
                    )
                )
                and str(
                    decision.get(
                        "controlled_forward_observation_start_dry_run_output_integrity_review_decision",
                        "",
                    )
                )
                == SOURCE_READY_DECISION
            ),
            str(
                decision.get(
                    "controlled_forward_observation_start_dry_run_output_integrity_review_decision",
                    "",
                )
            ),
        ),
        (
            "source_integrity_validations_passed",
            dataframe_all_passed(source_validations_df),
            f"validation_rows={len(source_validations_df)}",
        ),
        (
            "source_integrity_controls_passed",
            dataframe_all_passed(source_controls_df),
            f"control_rows={len(source_controls_df)}",
        ),
        (
            "source_integrity_rules_passed",
            dataframe_all_passed(source_rules_df),
            f"rule_rows={len(source_rules_df)}",
        ),
        (
            "source_integrity_requirements_passed",
            dataframe_all_passed(source_requirements_df),
            f"requirement_rows={len(source_requirements_df)}",
        ),
        (
            "source_integrity_guards_passed",
            dataframe_all_passed(source_guard_matrix_df),
            f"guard_rows={len(source_guard_matrix_df)}",
        ),
        (
            "source_integrity_counts_valid",
            source_counts_valid,
            ",".join(
                f"{field_name}={summary.get(field_name, '')}"
                for field_name in EXPECTED_SOURCE_COUNTS
            ),
        ),
        (
            "source_dry_run_output_row_count_one",
            len(source_dry_run_output_df) == 1,
            f"row_count={len(source_dry_run_output_df)}",
        ),
        (
            "source_candidate_valid",
            str(dry_run_output.get("candidate_id", ""))
            == PRIMARY_RESEARCH_CANDIDATE,
            str(dry_run_output.get("candidate_id", "")),
        ),
        (
            "source_direction_valid",
            str(dry_run_output.get("direction", "")) == "LONG",
            str(dry_run_output.get("direction", "")),
        ),
        (
            "source_price_structure_valid",
            stop_price < entry_price < target_price,
            f"stop={stop_price},entry={entry_price},target={target_price}",
        ),
        (
            "source_risk_reward_valid",
            risk_reward == expected_risk_reward and risk_reward == 2.5,
            f"risk_reward={risk_reward},expected={expected_risk_reward}",
        ),
        (
            "source_scope_valid",
            str(dry_run_output.get("run_scope", ""))
            == EXPECTED_SOURCE_RUN_SCOPE,
            str(dry_run_output.get("run_scope", "")),
        ),
        (
            "source_evidence_scope_valid",
            str(dry_run_output.get("evidence_scope", ""))
            == EXPECTED_SOURCE_EVIDENCE_SCOPE,
            str(dry_run_output.get("evidence_scope", "")),
        ),
        (
            "source_validation_status_valid",
            str(dry_run_output.get("validation_status", ""))
            == EXPECTED_SOURCE_VALIDATION_STATUS,
            str(dry_run_output.get("validation_status", "")),
        ),
        (
            "source_operational_locks_valid",
            source_operational_locks_valid,
            f"false_guard_count={len(EXPECTED_FALSE_GUARDS) - 2}",
        ),
        (
            "source_official_evidence_rows_zero",
            int(
                safe_float(
                    dry_run_output.get("official_evidence_rows_written"),
                    -1,
                )
            )
            == 0,
            str(dry_run_output.get("official_evidence_rows_written", "")),
        ),
        (
            "source_dry_run_artifact_metadata_valid",
            (
                safe_bool(artifact_metadata.get("artifact_exists", False))
                and safe_bool(
                    artifact_metadata.get("artifact_non_empty", False)
                )
                and safe_bool(
                    artifact_metadata.get(
                        "artifact_sha256_valid",
                        False,
                    )
                )
                and len(source_hash) == 64
            ),
            str(artifact_metadata.get("artifact_path", "")),
        ),
        (
            "source_dry_run_artifact_hash_matches",
            bool(source_hash)
            and source_hash == actual_source_hash,
            (
                f"metadata_sha256={source_hash},"
                f"actual_sha256={actual_source_hash}"
            ),
        ),
        (
            "official_dataset_absent",
            official_dataset_absent,
            f"official_dataset_absent={official_dataset_absent}",
        ),
        (
            "source_summary_and_decision_consistent",
            (
                str(
                    summary.get(
                        "controlled_forward_observation_start_dry_run_output_integrity_review_decision",
                        "",
                    )
                )
                == str(
                    decision.get(
                        "controlled_forward_observation_start_dry_run_output_integrity_review_decision",
                        "",
                    )
                )
                == SOURCE_READY_DECISION
            ),
            SOURCE_READY_DECISION,
        ),
        (
            "source_no_new_dry_run_confirmed",
            (
                safe_bool(
                    summary.get(
                        "new_controlled_forward_observation_start_dry_run_run_performed",
                        True,
                    ),
                    True,
                )
                is False
                and safe_bool(
                    summary.get(
                        "new_controlled_forward_observation_start_dry_run_performed",
                        True,
                    ),
                    True,
                )
                is False
            ),
            (
                "new_run="
                f"{summary.get('new_controlled_forward_observation_start_dry_run_run_performed', '')},"
                "new_dry_run="
                f"{summary.get('new_controlled_forward_observation_start_dry_run_performed', '')}"
            ),
        ),
        (
            "source_forward_observation_not_started",
            safe_bool(
                summary.get("forward_observation_started", True),
                True,
            )
            is False,
            str(summary.get("forward_observation_started", "")),
        ),
    ]

    return pd.DataFrame(
        [
            {
                "validation_name": validation_name,
                "passed": bool(passed),
                "details": details,
            }
            for validation_name, passed, details in rows
        ]
    )


def build_final_approval_evidence_chain(
    validations_df: pd.DataFrame,
) -> pd.DataFrame:
    validation_lookup = {
        str(row["validation_name"]): safe_bool(row["passed"], False)
        for _, row in validations_df.iterrows()
    }

    evidence_definitions = [
        ("phase_10_24_validation_passed", "dependency"),
        ("source_integrity_review_performed", "integrity_review"),
        ("source_integrity_review_passed", "integrity_review"),
        ("source_integrity_review_decision_valid", "integrity_review"),
        ("source_future_final_approval_review_allowed", "future_review"),
        ("source_artifacts_exist", "artifact"),
        ("source_artifacts_non_empty", "artifact"),
        ("source_artifact_hashes_valid", "artifact_integrity"),
        ("source_artifacts_stable_during_review", "artifact_integrity"),
        ("source_decision_table_consistent", "summary_consistency"),
        ("source_integrity_validations_passed", "validation"),
        ("source_integrity_controls_passed", "controls"),
        ("source_integrity_rules_passed", "rules"),
        ("source_integrity_requirements_passed", "requirements"),
        ("source_integrity_guards_passed", "safety"),
        ("source_integrity_counts_valid", "summary_consistency"),
        ("source_dry_run_output_row_count_one", "artifact"),
        ("source_candidate_valid", "candidate_scope"),
        ("source_direction_valid", "direction"),
        ("source_price_structure_valid", "price_structure"),
        ("source_risk_reward_valid", "risk_reward"),
        ("source_scope_valid", "scope_control"),
        ("source_evidence_scope_valid", "evidence_scope"),
        ("source_operational_locks_valid", "safety"),
        ("source_official_evidence_rows_zero", "official_dataset_guard"),
        ("source_dry_run_artifact_hash_matches", "artifact_integrity"),
        ("official_dataset_absent", "official_dataset_guard"),
        ("source_no_new_dry_run_confirmed", "dry_run_boundary"),
        ("source_forward_observation_not_started", "start_boundary"),
    ]

    return pd.DataFrame(
        [
            {
                "evidence_position": position,
                "evidence_id": f"START_FINAL_APPROVAL_EVIDENCE_{position:03d}",
                "evidence_name": evidence_name,
                "evidence_group": evidence_group,
                "required": True,
                "passed": validation_lookup.get(evidence_name, False),
                "details": (
                    "Validated from Phase 10.24 source artifacts and "
                    "Phase 10.23 copied dry-run output."
                ),
            }
            for position, (evidence_name, evidence_group) in enumerate(
                evidence_definitions,
                start=1,
            )
        ]
    )


def build_final_approval_controls(
    evidence_chain_df: pd.DataFrame,
) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "control_position": int(row["evidence_position"]),
                "control_id": (
                    f"START_FINAL_APPROVAL_CONTROL_"
                    f"{int(row['evidence_position']):03d}"
                ),
                "control_name": str(row["evidence_name"]),
                "control_group": str(row["evidence_group"]),
                "required": True,
                "final_approval_review_only": True,
                "future_controlled_forward_observation_start_run_allowed": True,
                "controlled_forward_observation_start_run_performed": False,
                "controlled_forward_observation_start_performed": False,
                "forward_observation_start_allowed": False,
                "official_dataset_write_allowed": False,
                "market_execution_allowed": False,
                "passed": safe_bool(row["passed"], False),
            }
            for _, row in evidence_chain_df.iterrows()
        ]
    )


def build_final_approval_guard_matrix() -> pd.DataFrame:
    rows: list[dict[str, Any]] = [
        {
            "guard_name": "controlled_forward_observation_start_final_approval_review_performed",
            "required_value": True,
            "actual_value": True,
            "passed": True,
            "guard_group": "final_approval_review_state",
        },
        {
            "guard_name": "future_controlled_forward_observation_start_run_allowed",
            "required_value": True,
            "actual_value": True,
            "passed": True,
            "guard_group": "final_approval_review_state",
        },
    ]

    for guard_name, required_value in EXPECTED_FALSE_GUARDS.items():
        rows.append(
            {
                "guard_name": guard_name,
                "required_value": required_value,
                "actual_value": required_value,
                "passed": True,
                "guard_group": "final_approval_review_safety_guard",
            }
        )

    rows.append(
        {
            "guard_name": "official_evidence_rows_written",
            "required_value": 0,
            "actual_value": 0,
            "passed": True,
            "guard_group": "official_dataset_guard",
        }
    )

    return pd.DataFrame(rows)


def build_final_approval_rules(
    validations_df: pd.DataFrame,
    evidence_chain_df: pd.DataFrame,
    controls_df: pd.DataFrame,
    guard_matrix_df: pd.DataFrame,
) -> pd.DataFrame:
    validations_passed = dataframe_all_passed(validations_df)
    evidence_passed = dataframe_all_passed(evidence_chain_df)
    controls_passed = dataframe_all_passed(controls_df)
    guards_passed = dataframe_all_passed(guard_matrix_df)

    rows = [
        (
            "final_approval_validation_count_32",
            len(validations_df) == 32,
            "32",
            str(len(validations_df)),
            "validation",
        ),
        (
            "all_final_approval_validations_passed",
            validations_passed,
            "True",
            str(validations_passed),
            "validation",
        ),
        (
            "final_approval_evidence_count_29",
            len(evidence_chain_df) == 29,
            "29",
            str(len(evidence_chain_df)),
            "evidence",
        ),
        (
            "all_final_approval_evidence_passed",
            evidence_passed,
            "True",
            str(evidence_passed),
            "evidence",
        ),
        (
            "final_approval_control_count_29",
            len(controls_df) == 29,
            "29",
            str(len(controls_df)),
            "controls",
        ),
        (
            "all_final_approval_controls_passed",
            controls_passed,
            "True",
            str(controls_passed),
            "controls",
        ),
        (
            "final_approval_guard_count_29",
            len(guard_matrix_df) == 29,
            "29",
            str(len(guard_matrix_df)),
            "safety",
        ),
        (
            "all_final_approval_guards_passed",
            guards_passed,
            "True",
            str(guards_passed),
            "safety",
        ),
        (
            "final_approval_review_only",
            True,
            "True",
            "True",
            "scope_control",
        ),
        (
            "future_controlled_start_run_allowed",
            True,
            "True",
            "True",
            "future_run",
        ),
        (
            "controlled_start_run_not_performed",
            True,
            "False",
            "False",
            "start_run_boundary",
        ),
        (
            "forward_observation_start_disabled",
            True,
            "False",
            "False",
            "start_boundary",
        ),
        (
            "official_dataset_writes_disabled",
            True,
            "False",
            "False",
            "official_dataset_guard",
        ),
        (
            "signal_generation_disabled",
            True,
            "False",
            "False",
            "signal_boundary",
        ),
        (
            "market_execution_disabled",
            True,
            "False",
            "False",
            "market_execution_guard",
        ),
        (
            "total_project_not_completed",
            True,
            "False",
            "False",
            "scope_control",
        ),
    ]

    return pd.DataFrame(
        [
            {
                "rule_id": f"START_FINAL_APPROVAL_RULE_{index:03d}",
                "rule_name": rule_name,
                "passed": bool(passed),
                "required_value": required_value,
                "actual_value": actual_value,
                "rule_group": rule_group,
            }
            for index, (
                rule_name,
                passed,
                required_value,
                actual_value,
                rule_group,
            ) in enumerate(rows, start=1)
        ]
    )


def build_final_approval_requirements(
    validations_df: pd.DataFrame,
    evidence_chain_df: pd.DataFrame,
    controls_df: pd.DataFrame,
    rules_df: pd.DataFrame,
    guard_matrix_df: pd.DataFrame,
) -> pd.DataFrame:
    validation_lookup = {
        str(row["validation_name"]): safe_bool(row["passed"], False)
        for _, row in validations_df.iterrows()
    }

    requirements: list[tuple[str, bool, str, str, str]] = []

    for validation_name in validations_df["validation_name"].astype(str).tolist():
        passed = validation_lookup.get(validation_name, False)
        requirements.append(
            (
                validation_name,
                passed,
                "True",
                str(passed),
                "source_validation",
            )
        )

    aggregate_requirements = [
        (
            "final_approval_evidence_chain_passed",
            dataframe_all_passed(evidence_chain_df),
            "True",
            str(dataframe_all_passed(evidence_chain_df)),
            "evidence",
        ),
        (
            "final_approval_controls_passed",
            dataframe_all_passed(controls_df),
            "True",
            str(dataframe_all_passed(controls_df)),
            "controls",
        ),
        (
            "final_approval_rules_passed",
            dataframe_all_passed(rules_df),
            "True",
            str(dataframe_all_passed(rules_df)),
            "rules",
        ),
        (
            "final_approval_guards_passed",
            dataframe_all_passed(guard_matrix_df),
            "True",
            str(dataframe_all_passed(guard_matrix_df)),
            "safety",
        ),
        (
            "final_approval_review_performed",
            True,
            "True",
            "True",
            "final_approval_review",
        ),
        (
            "future_controlled_start_run_allowed",
            True,
            "True",
            "True",
            "future_run",
        ),
        (
            "controlled_start_run_not_performed",
            True,
            "False",
            "False",
            "start_run_boundary",
        ),
        (
            "controlled_start_not_performed",
            True,
            "False",
            "False",
            "start_boundary",
        ),
        (
            "forward_observation_not_started",
            True,
            "False",
            "False",
            "start_boundary",
        ),
        (
            "official_evidence_rows_written_zero",
            True,
            "0",
            "0",
            "official_dataset_guard",
        ),
        (
            "signal_generation_disabled",
            True,
            "False",
            "False",
            "signal_boundary",
        ),
        (
            "paper_trading_disabled",
            True,
            "False",
            "False",
            "paper_trading_guard",
        ),
        (
            "market_execution_disabled",
            True,
            "False",
            "False",
            "market_execution_guard",
        ),
        (
            "total_project_not_completed",
            True,
            "False",
            "False",
            "scope_control",
        ),
    ]

    requirements.extend(aggregate_requirements)

    return pd.DataFrame(
        [
            {
                "requirement_id": f"START_FINAL_APPROVAL_REQ_{index:03d}",
                "requirement_name": requirement_name,
                "passed": bool(passed),
                "required_value": required_value,
                "actual_value": actual_value,
                "requirement_group": requirement_group,
            }
            for index, (
                requirement_name,
                passed,
                required_value,
                actual_value,
                requirement_group,
            ) in enumerate(requirements, start=1)
        ]
    )


def build_final_approval_decision_table(
    requirements_df: pd.DataFrame,
    rules_df: pd.DataFrame,
    guard_matrix_df: pd.DataFrame,
) -> pd.DataFrame:
    total_requirements = int(len(requirements_df))
    passed_requirements = (
        int(
            requirements_df["passed"]
            .map(lambda value: safe_bool(value, False))
            .sum()
        )
        if total_requirements
        else 0
    )
    failed_requirements = total_requirements - passed_requirements

    rules_passed = dataframe_all_passed(rules_df)
    guards_passed = dataframe_all_passed(guard_matrix_df)

    review_passed = (
        total_requirements > 0
        and failed_requirements == 0
        and rules_passed
        and guards_passed
    )

    failed_requirement_names = ""
    if not requirements_df.empty:
        failed_requirement_names = ",".join(
            requirements_df[
                ~requirements_df["passed"].map(
                    lambda value: safe_bool(value, False)
                )
            ]["requirement_name"]
            .astype(str)
            .tolist()
        )

    return pd.DataFrame(
        [
            {
                "controlled_forward_observation_start_final_approval_review_id": (
                    "PHASE_10_25_LONG_FORWARD_OBSERVATION_CONTROLLED_START_FINAL_APPROVAL_REVIEW_001"
                ),
                "controlled_forward_observation_start_final_approval_review_status": FINAL_APPROVAL_REVIEW_STATUS,
                "controlled_forward_observation_start_final_approval_review_performed": True,
                "controlled_forward_observation_start_final_approval_review_passed": review_passed,
                "controlled_forward_observation_start_final_approval_review_decision": (
                    READY_DECISION if review_passed else BLOCKED_DECISION
                ),
                "total_requirements": total_requirements,
                "passed_requirements": passed_requirements,
                "failed_requirements": failed_requirements,
                "failed_requirement_names": failed_requirement_names,
                "final_approval_rules_passed": rules_passed,
                "final_approval_guards_passed": guards_passed,
                "future_controlled_forward_observation_start_run_allowed": review_passed,
                "controlled_forward_observation_start_run_performed": False,
                "controlled_forward_observation_start_performed": False,
                "forward_observation_start_allowed": False,
                "forward_observation_started": False,
                "official_dataset_write_allowed": False,
                "official_dataset_write_performed": False,
                "real_forward_dataset_created": False,
                "official_evidence_rows_written": 0,
                "real_forward_signals_recorded": False,
                "journal_real_rows_accepted": False,
                "accepted_as_real_evidence": False,
                "evidence_persistence_allowed": False,
                "evidence_write_performed": False,
                "signal_generation_enabled": False,
                "live_alerts_allowed": False,
                "paper_trading_enabled": False,
                "long_strategy_approved": False,
                "long_entries_approved": False,
                "long_side_established": False,
                "paper_trade_execution_allowed": False,
                "real_capital_allowed": False,
                "market_execution_allowed": False,
                "exchange_execution_allowed": False,
                "automation_allowed": False,
                "execution_allowed": False,
                "real_entries_approved": False,
                "total_project_completed": False,
                "recommended_next_phase": RECOMMENDED_NEXT_PHASE,
            }
        ]
    )


def validate_long_forward_observation_controlled_start_final_approval_review() -> dict[str, pd.DataFrame]:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    checks: list[dict[str, Any]] = []

    for check_name, path in {
        "phase_10_24_output_integrity_review_doc_exists": PHASE_10_24_DOC_PATH,
        "phase_10_25_final_approval_review_doc_exists": PHASE_10_25_DOC_PATH,
    }.items():
        exists = path.exists()
        checks.append(
            build_check(
                check_group="phase_anchor",
                check_name=check_name,
                passed=exists,
                severity="INFO" if exists else "ERROR",
                details=str(path),
            )
        )

    official_dataset_exists_before = OFFICIAL_DATASET_PATH.exists()
    official_dataset_absent = not official_dataset_exists_before

    source_manifest_before_df = build_source_manifest()

    source_summary_df = read_csv_if_exists(SOURCE_SUMMARY_PATH)
    source_dry_run_output_df = read_csv_if_exists(SOURCE_DRY_RUN_OUTPUT_PATH)
    source_artifact_metadata_df = read_csv_if_exists(
        SOURCE_ARTIFACT_METADATA_PATH
    )
    source_validations_df = read_csv_if_exists(SOURCE_VALIDATIONS_PATH)
    source_controls_df = read_csv_if_exists(SOURCE_CONTROLS_PATH)
    source_rules_df = read_csv_if_exists(SOURCE_RULES_PATH)
    source_requirements_df = read_csv_if_exists(SOURCE_REQUIREMENTS_PATH)
    source_guard_matrix_df = read_csv_if_exists(SOURCE_GUARD_MATRIX_PATH)
    source_decision_df = read_csv_if_exists(SOURCE_DECISION_PATH)
    source_checks_df = read_csv_if_exists(SOURCE_CHECKS_PATH)

    source_manifest_after_df = build_source_manifest()

    final_approval_validations_df = build_final_approval_validations(
        source_summary_df=source_summary_df,
        source_dry_run_output_df=source_dry_run_output_df,
        source_artifact_metadata_df=source_artifact_metadata_df,
        source_validations_df=source_validations_df,
        source_controls_df=source_controls_df,
        source_rules_df=source_rules_df,
        source_requirements_df=source_requirements_df,
        source_guard_matrix_df=source_guard_matrix_df,
        source_decision_df=source_decision_df,
        source_manifest_before_df=source_manifest_before_df,
        source_manifest_after_df=source_manifest_after_df,
        official_dataset_absent=official_dataset_absent,
    )

    final_approval_evidence_chain_df = build_final_approval_evidence_chain(
        final_approval_validations_df
    )
    final_approval_controls_df = build_final_approval_controls(
        final_approval_evidence_chain_df
    )
    final_approval_guard_matrix_df = build_final_approval_guard_matrix()
    final_approval_rules_df = build_final_approval_rules(
        validations_df=final_approval_validations_df,
        evidence_chain_df=final_approval_evidence_chain_df,
        controls_df=final_approval_controls_df,
        guard_matrix_df=final_approval_guard_matrix_df,
    )
    final_approval_requirements_df = build_final_approval_requirements(
        validations_df=final_approval_validations_df,
        evidence_chain_df=final_approval_evidence_chain_df,
        controls_df=final_approval_controls_df,
        rules_df=final_approval_rules_df,
        guard_matrix_df=final_approval_guard_matrix_df,
    )
    final_approval_decision_df = build_final_approval_decision_table(
        requirements_df=final_approval_requirements_df,
        rules_df=final_approval_rules_df,
        guard_matrix_df=final_approval_guard_matrix_df,
    )

    decision = (
        final_approval_decision_df.iloc[0].to_dict()
        if not final_approval_decision_df.empty
        else {}
    )

    validation_lookup = {
        str(row["validation_name"]): safe_bool(row["passed"], False)
        for _, row in final_approval_validations_df.iterrows()
    }

    aggregate_checks = [
        (
            "final_approval_validations_passed",
            dataframe_all_passed(final_approval_validations_df),
        ),
        (
            "final_approval_evidence_chain_passed",
            dataframe_all_passed(final_approval_evidence_chain_df),
        ),
        (
            "final_approval_controls_passed",
            dataframe_all_passed(final_approval_controls_df),
        ),
        (
            "final_approval_rules_passed",
            dataframe_all_passed(final_approval_rules_df),
        ),
        (
            "final_approval_requirements_passed",
            dataframe_all_passed(final_approval_requirements_df),
        ),
        (
            "final_approval_guards_passed",
            dataframe_all_passed(final_approval_guard_matrix_df),
        ),
        (
            "controlled_start_final_approval_review_passed",
            safe_bool(
                decision.get(
                    "controlled_forward_observation_start_final_approval_review_passed",
                    False,
                )
            ),
        ),
        (
            "controlled_start_final_approval_review_decision_expected",
            str(
                decision.get(
                    "controlled_forward_observation_start_final_approval_review_decision",
                    "",
                )
            )
            == READY_DECISION,
        ),
    ]

    for check_name, passed in aggregate_checks:
        checks.append(
            build_check(
                check_group="final_approval_review",
                check_name=check_name,
                passed=passed,
                severity="INFO" if passed else "ERROR",
                details=(
                    str(
                        decision.get(
                            "controlled_forward_observation_start_final_approval_review_decision",
                            "",
                        )
                    )
                    if check_name
                    == "controlled_start_final_approval_review_decision_expected"
                    else f"{check_name}={passed}"
                ),
            )
        )

    official_dataset_exists_after = OFFICIAL_DATASET_PATH.exists()
    official_dataset_unchanged_absent = (
        not official_dataset_exists_before
        and not official_dataset_exists_after
    )

    checks.append(
        build_check(
            check_group="official_dataset_guard",
            check_name="official_dataset_not_created_or_written",
            passed=official_dataset_unchanged_absent,
            severity=(
                "INFO" if official_dataset_unchanged_absent else "ERROR"
            ),
            details=(
                f"before={official_dataset_exists_before},"
                f"after={official_dataset_exists_after}"
            ),
        )
    )

    for _, guard_row in final_approval_guard_matrix_df.iterrows():
        passed = safe_bool(guard_row.get("passed", False), False)
        checks.append(
            build_check(
                check_group="final_approval_review_safety_flags",
                check_name=str(guard_row.get("guard_name", "")),
                passed=passed,
                severity="INFO" if passed else "ERROR",
                details=(
                    f"{guard_row.get('guard_name', '')}="
                    f"{guard_row.get('actual_value', '')} "
                    f"(required={guard_row.get('required_value', '')})"
                ),
            )
        )

    scope_warnings = [
        (
            "final_approval_review_only",
            "Phase 10.25 performs only a final approval review.",
        ),
        (
            "controlled_start_run_not_performed",
            "The future controlled forward observation start run is not performed.",
        ),
        (
            "forward_observation_not_started",
            "Forward observation remains not started.",
        ),
        (
            "official_evidence_not_persisted",
            "Official evidence persistence remains disabled.",
        ),
        (
            "signal_generation_not_enabled",
            "Signal generation remains disabled.",
        ),
        (
            "paper_trading_not_enabled",
            "Paper trading execution remains disabled.",
        ),
        (
            "long_strategy_not_approved",
            "The LONG research candidate is not approved as a trading strategy.",
        ),
        (
            "real_capital_not_allowed",
            "Real capital remains prohibited.",
        ),
        (
            "market_execution_not_allowed",
            "Market execution remains prohibited.",
        ),
        (
            "total_project_not_completed",
            "The total project is not completed.",
        ),
    ]

    for check_name, details in scope_warnings:
        checks.append(
            build_check(
                check_group="scope_control",
                check_name=check_name,
                passed=True,
                severity="WARNING",
                details=details,
            )
        )

    future_start_run_allowed = safe_bool(
        decision.get(
            "future_controlled_forward_observation_start_run_allowed",
            False,
        )
    )

    checks.append(
        build_check(
            check_group="planning_scope",
            check_name="future_controlled_forward_observation_start_run_allowed",
            passed=future_start_run_allowed,
            severity="WARNING" if future_start_run_allowed else "ERROR",
            details=(
                "This permits only a future controlled forward observation "
                "start run. It does not start observation in this phase, write "
                "official evidence, generate live signals or alerts, enable "
                "paper trading, use real capital, or permit market execution."
            ),
        )
    )

    checks.append(
        build_check(
            check_group="phase_transition",
            check_name="phase_10_26_recommended_next",
            passed=True,
            severity="INFO",
            details=(
                "Recommended next step: Phase 10.26 LONG Forward Observation "
                "Controlled Start Run V1."
            ),
        )
    )

    checks_df = pd.DataFrame(checks)
    blocker_count = int(
        checks_df["blocker"]
        .map(lambda value: safe_bool(value, False))
        .sum()
    )
    error_count = int(checks_df["severity"].eq("ERROR").sum())
    warning_count = int(checks_df["severity"].eq("WARNING").sum())
    validation_passed = blocker_count == 0 and error_count == 0

    source_summary = (
        source_summary_df.iloc[0].to_dict()
        if not source_summary_df.empty
        else {}
    )
    source_dry_run_output = (
        source_dry_run_output_df.iloc[0].to_dict()
        if not source_dry_run_output_df.empty
        else {}
    )

    review_passed = safe_bool(
        decision.get(
            "controlled_forward_observation_start_final_approval_review_passed",
            False,
        )
    )
    review_decision = str(
        decision.get(
            "controlled_forward_observation_start_final_approval_review_decision",
            "",
        )
    )

    summary_df = pd.DataFrame(
        [
            {
                "phase": "10.25",
                "long_forward_observation_controlled_start_final_approval_review_defined": True,
                "phase_10_24_validation_passed": validation_lookup.get(
                    "phase_10_24_validation_passed",
                    False,
                ),
                "source_output_integrity_review_performed": validation_lookup.get(
                    "source_integrity_review_performed",
                    False,
                ),
                "source_output_integrity_review_passed": validation_lookup.get(
                    "source_integrity_review_passed",
                    False,
                ),
                "source_output_integrity_review_decision": str(
                    source_summary.get(
                        "controlled_forward_observation_start_dry_run_output_integrity_review_decision",
                        "",
                    )
                ),
                "source_future_final_approval_review_allowed": validation_lookup.get(
                    "source_future_final_approval_review_allowed",
                    False,
                ),
                "source_artifact_count": int(len(source_manifest_after_df)),
                "source_artifacts_exist": validation_lookup.get(
                    "source_artifacts_exist",
                    False,
                ),
                "source_artifacts_non_empty": validation_lookup.get(
                    "source_artifacts_non_empty",
                    False,
                ),
                "source_artifact_hashes_valid": validation_lookup.get(
                    "source_artifact_hashes_valid",
                    False,
                ),
                "source_artifacts_stable_during_review": validation_lookup.get(
                    "source_artifacts_stable_during_review",
                    False,
                ),
                "source_manifest_sha256": manifest_digest(
                    source_manifest_after_df
                ),
                "source_candidate_id": str(
                    source_dry_run_output.get("candidate_id", "")
                ),
                "source_candidate_valid": validation_lookup.get(
                    "source_candidate_valid",
                    False,
                ),
                "source_direction": str(
                    source_dry_run_output.get("direction", "")
                ),
                "source_direction_valid": validation_lookup.get(
                    "source_direction_valid",
                    False,
                ),
                "source_price_structure_valid": validation_lookup.get(
                    "source_price_structure_valid",
                    False,
                ),
                "source_risk_reward": safe_float(
                    source_dry_run_output.get("risk_reward")
                ),
                "source_risk_reward_valid": validation_lookup.get(
                    "source_risk_reward_valid",
                    False,
                ),
                "source_scope": str(
                    source_dry_run_output.get("run_scope", "")
                ),
                "source_scope_valid": validation_lookup.get(
                    "source_scope_valid",
                    False,
                ),
                "source_evidence_scope": str(
                    source_dry_run_output.get("evidence_scope", "")
                ),
                "source_evidence_scope_valid": validation_lookup.get(
                    "source_evidence_scope_valid",
                    False,
                ),
                "source_operational_locks_valid": validation_lookup.get(
                    "source_operational_locks_valid",
                    False,
                ),
                "source_official_evidence_rows_zero": validation_lookup.get(
                    "source_official_evidence_rows_zero",
                    False,
                ),
                "final_approval_validation_rows": int(
                    len(final_approval_validations_df)
                ),
                "final_approval_evidence_rows": int(
                    len(final_approval_evidence_chain_df)
                ),
                "final_approval_control_rows": int(
                    len(final_approval_controls_df)
                ),
                "final_approval_rule_rows": int(
                    len(final_approval_rules_df)
                ),
                "final_approval_requirement_rows": int(
                    len(final_approval_requirements_df)
                ),
                "final_approval_guard_rows": int(
                    len(final_approval_guard_matrix_df)
                ),
                "final_approval_validations_passed": dataframe_all_passed(
                    final_approval_validations_df
                ),
                "final_approval_evidence_chain_passed": dataframe_all_passed(
                    final_approval_evidence_chain_df
                ),
                "final_approval_controls_passed": dataframe_all_passed(
                    final_approval_controls_df
                ),
                "final_approval_rules_passed": dataframe_all_passed(
                    final_approval_rules_df
                ),
                "final_approval_requirements_passed": dataframe_all_passed(
                    final_approval_requirements_df
                ),
                "final_approval_guards_passed": dataframe_all_passed(
                    final_approval_guard_matrix_df
                ),
                "controlled_forward_observation_start_final_approval_review_performed": True,
                "controlled_forward_observation_start_final_approval_review_passed": review_passed,
                "controlled_forward_observation_start_final_approval_review_decision": review_decision,
                "future_controlled_forward_observation_start_run_allowed": future_start_run_allowed,
                "controlled_forward_observation_start_run_performed": False,
                "controlled_forward_observation_start_performed": False,
                "forward_observation_start_allowed": False,
                "official_dataset_exists_before": official_dataset_exists_before,
                "official_dataset_exists_after": official_dataset_exists_after,
                "official_dataset_write_allowed": False,
                "official_dataset_write_performed": False,
                "real_forward_dataset_created": False,
                "official_evidence_rows_written": 0,
                "real_forward_signals_recorded": False,
                "journal_real_rows_accepted": False,
                "accepted_as_real_evidence": False,
                "evidence_persistence_allowed": False,
                "evidence_write_performed": False,
                "forward_observation_started": False,
                "signal_generation_enabled": False,
                "live_alerts_allowed": False,
                "paper_trading_enabled": False,
                "long_strategy_approved": False,
                "long_entries_approved": False,
                "long_side_established": False,
                "paper_trade_execution_allowed": False,
                "real_capital_allowed": False,
                "market_execution_allowed": False,
                "exchange_execution_allowed": False,
                "automation_allowed": False,
                "execution_allowed": False,
                "real_entries_approved": False,
                "total_project_completed": False,
                "recommended_next_phase": RECOMMENDED_NEXT_PHASE,
                "estimated_phase_10_progress_percent": 100,
                "total_checks": int(len(checks_df)),
                "warning_count": warning_count,
                "error_count": error_count,
                "blocker_count": blocker_count,
                "validation_passed": validation_passed,
                "validation_decision": (
                    "PHASE_10_25_LONG_FORWARD_OBSERVATION_CONTROLLED_START_FINAL_APPROVAL_REVIEW_VALIDATED"
                    if validation_passed
                    else "PHASE_10_25_LONG_FORWARD_OBSERVATION_CONTROLLED_START_FINAL_APPROVAL_REVIEW_FAILED"
                ),
            }
        ]
    )

    source_summary_df.to_csv(
        REPORTS_DIR / "phase_10_24_source_summary_v1.csv",
        index=False,
    )
    source_dry_run_output_df.to_csv(
        REPORTS_DIR / "phase_10_23_source_dry_run_output_v1.csv",
        index=False,
    )
    source_artifact_metadata_df.to_csv(
        REPORTS_DIR / "phase_10_24_source_artifact_metadata_v1.csv",
        index=False,
    )
    source_validations_df.to_csv(
        REPORTS_DIR / "phase_10_24_source_integrity_validations_v1.csv",
        index=False,
    )
    source_controls_df.to_csv(
        REPORTS_DIR / "phase_10_24_source_integrity_controls_v1.csv",
        index=False,
    )
    source_rules_df.to_csv(
        REPORTS_DIR / "phase_10_24_source_integrity_rules_v1.csv",
        index=False,
    )
    source_requirements_df.to_csv(
        REPORTS_DIR / "phase_10_24_source_integrity_requirements_v1.csv",
        index=False,
    )
    source_guard_matrix_df.to_csv(
        REPORTS_DIR / "phase_10_24_source_integrity_guard_matrix_v1.csv",
        index=False,
    )
    source_decision_df.to_csv(
        REPORTS_DIR / "phase_10_24_source_integrity_decision_v1.csv",
        index=False,
    )
    source_checks_df.to_csv(
        REPORTS_DIR / "phase_10_24_source_checks_v1.csv",
        index=False,
    )
    source_manifest_after_df.to_csv(
        REPORTS_DIR / "source_integrity_review_artifact_manifest_v1.csv",
        index=False,
    )
    final_approval_validations_df.to_csv(
        REPORTS_DIR / "start_final_approval_validations_v1.csv",
        index=False,
    )
    final_approval_evidence_chain_df.to_csv(
        REPORTS_DIR / "start_final_approval_evidence_chain_v1.csv",
        index=False,
    )
    final_approval_controls_df.to_csv(
        REPORTS_DIR / "start_final_approval_controls_v1.csv",
        index=False,
    )
    final_approval_rules_df.to_csv(
        REPORTS_DIR / "start_final_approval_rules_v1.csv",
        index=False,
    )
    final_approval_requirements_df.to_csv(
        REPORTS_DIR / "start_final_approval_requirements_v1.csv",
        index=False,
    )
    final_approval_guard_matrix_df.to_csv(
        REPORTS_DIR / "start_final_approval_guard_matrix_v1.csv",
        index=False,
    )
    final_approval_decision_df.to_csv(
        REPORTS_DIR / "start_final_approval_decision_v1.csv",
        index=False,
    )
    checks_df.to_csv(
        REPORTS_DIR / "start_final_approval_checks_v1.csv",
        index=False,
    )
    summary_df.to_csv(
        REPORTS_DIR / "start_final_approval_summary_v1.csv",
        index=False,
    )

    return {
        "summary": summary_df,
        "source_phase_10_24_summary": source_summary_df,
        "source_dry_run_output": source_dry_run_output_df,
        "source_artifact_metadata": source_artifact_metadata_df,
        "source_integrity_validations": source_validations_df,
        "source_integrity_controls": source_controls_df,
        "source_integrity_rules": source_rules_df,
        "source_integrity_requirements": source_requirements_df,
        "source_integrity_guard_matrix": source_guard_matrix_df,
        "source_integrity_decision": source_decision_df,
        "source_checks": source_checks_df,
        "source_manifest": source_manifest_after_df,
        "final_approval_validations": final_approval_validations_df,
        "final_approval_evidence_chain": final_approval_evidence_chain_df,
        "final_approval_controls": final_approval_controls_df,
        "final_approval_rules": final_approval_rules_df,
        "final_approval_requirements": final_approval_requirements_df,
        "final_approval_guard_matrix": final_approval_guard_matrix_df,
        "final_approval_decision": final_approval_decision_df,
        "checks": checks_df,
    }
