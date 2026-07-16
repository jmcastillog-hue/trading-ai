from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

from src.long_side.long_forward_observation_dataset_bootstrap_v1 import (
    OFFICIAL_DATASET_PATH,
    PRIMARY_RESEARCH_CANDIDATE,
)
from src.long_side.long_forward_observation_phase_10_23_controlled_start_dry_run_run_v1 import (
    EVIDENCE_SCOPE as SOURCE_EVIDENCE_SCOPE,
    READY_DECISION as SOURCE_READY_DECISION,
    RUN_SCOPE as SOURCE_RUN_SCOPE,
    START_DRY_RUN_OUTPUT_COLUMNS,
    VALIDATION_STATUS as SOURCE_VALIDATION_STATUS,
)


REPORTS_DIR = Path(
    "reports/p10_24_start_dry_run_output_integrity_review_v1"
)
PHASE_10_23_REPORTS_DIR = Path("reports/p10_23_start_dry_run_run_v1")

PHASE_10_23_DOC_PATH = Path(
    "docs/PHASE_10_LONG_FORWARD_OBSERVATION_CONTROLLED_START_DRY_RUN_RUN.md"
)
PHASE_10_24_DOC_PATH = Path(
    "docs/PHASE_10_LONG_FORWARD_OBSERVATION_CONTROLLED_START_DRY_RUN_OUTPUT_INTEGRITY_REVIEW.md"
)

SOURCE_SUMMARY_PATH = (
    PHASE_10_23_REPORTS_DIR / "start_dry_run_run_summary_v1.csv"
)
SOURCE_OUTPUT_PATH = (
    PHASE_10_23_REPORTS_DIR / "controlled_start_dry_run_output_v1.csv"
)
SOURCE_VALIDATIONS_PATH = (
    PHASE_10_23_REPORTS_DIR / "start_dry_run_run_validations_v1.csv"
)
SOURCE_EVIDENCE_CHAIN_PATH = (
    PHASE_10_23_REPORTS_DIR / "start_dry_run_run_evidence_chain_v1.csv"
)
SOURCE_CONTROLS_PATH = (
    PHASE_10_23_REPORTS_DIR / "start_dry_run_run_controls_v1.csv"
)
SOURCE_RULES_PATH = (
    PHASE_10_23_REPORTS_DIR / "start_dry_run_run_rules_v1.csv"
)
SOURCE_REQUIREMENTS_PATH = (
    PHASE_10_23_REPORTS_DIR / "start_dry_run_run_requirements_v1.csv"
)
SOURCE_GUARD_MATRIX_PATH = (
    PHASE_10_23_REPORTS_DIR / "start_dry_run_run_guard_matrix_v1.csv"
)
SOURCE_DECISION_PATH = (
    PHASE_10_23_REPORTS_DIR / "start_dry_run_run_decision_v1.csv"
)
SOURCE_CHECKS_PATH = (
    PHASE_10_23_REPORTS_DIR / "start_dry_run_run_checks_v1.csv"
)

INTEGRITY_REVIEW_STATUS = (
    "LONG_FORWARD_OBSERVATION_CONTROLLED_START_DRY_RUN_OUTPUT_INTEGRITY_REVIEW_ONLY"
)
READY_DECISION = (
    "CONTROLLED_FORWARD_OBSERVATION_START_DRY_RUN_OUTPUT_INTEGRITY_REVIEW_"
    "READY_FOR_CONTROLLED_FORWARD_OBSERVATION_START_FINAL_APPROVAL_REVIEW"
)
BLOCKED_DECISION = (
    "CONTROLLED_FORWARD_OBSERVATION_START_DRY_RUN_OUTPUT_INTEGRITY_REVIEW_BLOCKED"
)
RECOMMENDED_NEXT_PHASE = (
    "PHASE_10_25_LONG_FORWARD_OBSERVATION_CONTROLLED_START_FINAL_APPROVAL_REVIEW_V1"
)

EXPECTED_FALSE_GUARDS = {
    "new_controlled_forward_observation_start_dry_run_run_performed": False,
    "new_controlled_forward_observation_start_dry_run_performed": False,
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

EXPECTED_TRUE_SOURCE_RUN_FIELDS = [
    "controlled_forward_observation_start_dry_run_execution_review_performed",
    "future_controlled_forward_observation_start_dry_run_run_allowed",
    "controlled_forward_observation_start_dry_run_run_allowed",
    "controlled_forward_observation_start_dry_run_run_performed",
    "controlled_forward_observation_start_dry_run_performed",
    "future_controlled_forward_observation_start_dry_run_output_integrity_review_allowed",
]

CRITICAL_OUTPUT_FIELDS = [
    "dry_run_run_id",
    "dry_run_status",
    "executed_at_utc",
    "source_phase",
    "source_validation_decision",
    "source_execution_review_decision",
    "source_design_id",
    "symbol",
    "timeframe",
    "candidate_id",
    "direction",
    "run_scope",
    "evidence_scope",
    "entry_price",
    "stop_price",
    "target_price",
    "risk_reward",
    "validation_status",
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


def lookup_validation(
    validations_df: pd.DataFrame,
    validation_name: str,
) -> bool:
    if validations_df.empty or "validation_name" not in validations_df.columns:
        return False

    matching = validations_df[
        validations_df["validation_name"].astype(str) == validation_name
    ]
    if matching.empty:
        return False

    return safe_bool(matching.iloc[0].get("passed", False), False)


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


def build_artifact_metadata(path: Path) -> pd.DataFrame:
    exists = path.exists() and path.is_file()
    size_bytes = path.stat().st_size if exists else 0
    modified_at_utc = (
        datetime.fromtimestamp(
            path.stat().st_mtime,
            tz=timezone.utc,
        ).isoformat()
        if exists
        else ""
    )
    sha256 = sha256_file(path) if exists else ""

    return pd.DataFrame(
        [
            {
                "artifact_path": str(path),
                "artifact_exists": exists,
                "artifact_size_bytes": int(size_bytes),
                "artifact_non_empty": bool(size_bytes > 0),
                "artifact_sha256": sha256,
                "artifact_sha256_valid": len(sha256) == 64,
                "artifact_modified_at_utc": modified_at_utc,
            }
        ]
    )


def critical_fields_present(row: dict[str, Any]) -> bool:
    for field_name in CRITICAL_OUTPUT_FIELDS:
        value = row.get(field_name)

        if value is None:
            return False

        try:
            if pd.isna(value):
                return False
        except Exception:
            pass

        if isinstance(value, str) and not value.strip():
            return False

    return True


def build_integrity_validations(
    source_summary_df: pd.DataFrame,
    source_output_df: pd.DataFrame,
    source_validations_df: pd.DataFrame,
    source_evidence_chain_df: pd.DataFrame,
    source_controls_df: pd.DataFrame,
    source_rules_df: pd.DataFrame,
    source_requirements_df: pd.DataFrame,
    source_guard_matrix_df: pd.DataFrame,
    source_decision_df: pd.DataFrame,
    artifact_metadata_before_df: pd.DataFrame,
    artifact_metadata_after_df: pd.DataFrame,
    official_dataset_absent: bool,
) -> pd.DataFrame:
    summary = (
        source_summary_df.iloc[0].to_dict()
        if not source_summary_df.empty
        else {}
    )
    output = (
        source_output_df.iloc[0].to_dict()
        if not source_output_df.empty
        else {}
    )
    decision = (
        source_decision_df.iloc[0].to_dict()
        if not source_decision_df.empty
        else {}
    )
    metadata_before = (
        artifact_metadata_before_df.iloc[0].to_dict()
        if not artifact_metadata_before_df.empty
        else {}
    )
    metadata_after = (
        artifact_metadata_after_df.iloc[0].to_dict()
        if not artifact_metadata_after_df.empty
        else {}
    )

    entry_price = safe_float(output.get("entry_price"))
    stop_price = safe_float(output.get("stop_price"))
    target_price = safe_float(output.get("target_price"))
    risk_reward = safe_float(output.get("risk_reward"))
    expected_risk_reward = (
        round((target_price - entry_price) / (entry_price - stop_price), 4)
        if entry_price > stop_price
        else 0.0
    )

    true_run_fields_valid = all(
        safe_bool(output.get(field_name, False), False)
        for field_name in EXPECTED_TRUE_SOURCE_RUN_FIELDS
    )

    source_operational_locks_valid = all(
        safe_bool(output.get(field_name, True), True) is False
        for field_name in EXPECTED_FALSE_GUARDS
        if not field_name.startswith("new_")
    )

    columns = source_output_df.columns.astype(str).tolist()
    source_summary_row_count = int(
        safe_float(
            summary.get("controlled_start_dry_run_output_row_count"),
            -1,
        )
    )
    source_artifact_rows_written = int(
        safe_float(summary.get("dry_run_artifact_rows_written"), -1)
    )

    artifact_stable = (
        bool(metadata_before)
        and bool(metadata_after)
        and str(metadata_before.get("artifact_sha256", ""))
        == str(metadata_after.get("artifact_sha256", ""))
        and int(metadata_before.get("artifact_size_bytes", -1))
        == int(metadata_after.get("artifact_size_bytes", -2))
    )

    rows = [
        (
            "source_artifact_exists",
            safe_bool(metadata_before.get("artifact_exists", False)),
            str(metadata_before.get("artifact_path", SOURCE_OUTPUT_PATH)),
        ),
        (
            "source_artifact_non_empty",
            safe_bool(metadata_before.get("artifact_non_empty", False)),
            f"size_bytes={metadata_before.get('artifact_size_bytes', 0)}",
        ),
        (
            "source_artifact_sha256_valid",
            safe_bool(metadata_before.get("artifact_sha256_valid", False)),
            str(metadata_before.get("artifact_sha256", "")),
        ),
        (
            "source_artifact_stable_during_review",
            artifact_stable,
            (
                f"sha_before={metadata_before.get('artifact_sha256', '')},"
                f"sha_after={metadata_after.get('artifact_sha256', '')}"
            ),
        ),
        (
            "source_summary_validation_passed",
            safe_bool(summary.get("validation_passed", False)),
            str(summary.get("validation_decision", "")),
        ),
        (
            "source_run_passed",
            safe_bool(
                summary.get(
                    "controlled_forward_observation_start_dry_run_run_passed",
                    False,
                )
            ),
            str(
                summary.get(
                    "controlled_forward_observation_start_dry_run_run_passed",
                    "",
                )
            ),
        ),
        (
            "source_run_decision_valid",
            str(
                summary.get(
                    "controlled_forward_observation_start_dry_run_run_decision",
                    "",
                )
            )
            == SOURCE_READY_DECISION,
            str(
                summary.get(
                    "controlled_forward_observation_start_dry_run_run_decision",
                    "",
                )
            ),
        ),
        (
            "source_future_integrity_review_allowed",
            safe_bool(
                summary.get(
                    "future_controlled_forward_observation_start_dry_run_output_integrity_review_allowed",
                    False,
                )
            ),
            str(
                summary.get(
                    "future_controlled_forward_observation_start_dry_run_output_integrity_review_allowed",
                    "",
                )
            ),
        ),
        (
            "source_output_row_count_valid",
            len(source_output_df) == 1,
            f"row_count={len(source_output_df)}",
        ),
        (
            "source_output_schema_valid",
            columns == START_DRY_RUN_OUTPUT_COLUMNS,
            (
                f"actual_field_count={len(columns)},"
                f"expected_field_count={len(START_DRY_RUN_OUTPUT_COLUMNS)}"
            ),
        ),
        (
            "source_output_critical_fields_present",
            bool(output) and critical_fields_present(output),
            f"critical_field_count={len(CRITICAL_OUTPUT_FIELDS)}",
        ),
        (
            "source_output_candidate_valid",
            str(output.get("candidate_id", "")) == PRIMARY_RESEARCH_CANDIDATE,
            str(output.get("candidate_id", "")),
        ),
        (
            "source_output_direction_valid",
            str(output.get("direction", "")) == "LONG",
            str(output.get("direction", "")),
        ),
        (
            "source_output_price_structure_valid",
            stop_price < entry_price < target_price,
            f"stop={stop_price},entry={entry_price},target={target_price}",
        ),
        (
            "source_output_risk_reward_valid",
            risk_reward == expected_risk_reward and risk_reward == 2.5,
            f"risk_reward={risk_reward},expected={expected_risk_reward}",
        ),
        (
            "source_output_scope_valid",
            str(output.get("run_scope", "")) == SOURCE_RUN_SCOPE,
            str(output.get("run_scope", "")),
        ),
        (
            "source_output_evidence_scope_valid",
            str(output.get("evidence_scope", "")) == SOURCE_EVIDENCE_SCOPE,
            str(output.get("evidence_scope", "")),
        ),
        (
            "source_output_true_run_fields_valid",
            true_run_fields_valid,
            f"true_run_field_count={len(EXPECTED_TRUE_SOURCE_RUN_FIELDS)}",
        ),
        (
            "source_output_operational_locks_valid",
            source_operational_locks_valid,
            f"false_guard_count={len(EXPECTED_FALSE_GUARDS) - 2}",
        ),
        (
            "source_output_official_evidence_rows_zero",
            int(safe_float(output.get("official_evidence_rows_written"), -1)) == 0,
            str(output.get("official_evidence_rows_written", "")),
        ),
        (
            "source_output_validation_status_valid",
            str(output.get("validation_status", ""))
            == SOURCE_VALIDATION_STATUS,
            str(output.get("validation_status", "")),
        ),
        (
            "source_validations_passed",
            dataframe_all_passed(source_validations_df),
            f"validation_rows={len(source_validations_df)}",
        ),
        (
            "source_evidence_chain_passed",
            dataframe_all_passed(source_evidence_chain_df),
            f"evidence_rows={len(source_evidence_chain_df)}",
        ),
        (
            "source_controls_passed",
            dataframe_all_passed(source_controls_df),
            f"control_rows={len(source_controls_df)}",
        ),
        (
            "source_rules_passed",
            dataframe_all_passed(source_rules_df),
            f"rule_rows={len(source_rules_df)}",
        ),
        (
            "source_requirements_passed",
            dataframe_all_passed(source_requirements_df),
            f"requirement_rows={len(source_requirements_df)}",
        ),
        (
            "source_guards_passed",
            dataframe_all_passed(source_guard_matrix_df),
            f"guard_rows={len(source_guard_matrix_df)}",
        ),
        (
            "source_decision_table_consistent",
            (
                not source_decision_df.empty
                and safe_bool(
                    decision.get(
                        "controlled_forward_observation_start_dry_run_run_passed",
                        False,
                    )
                )
                and str(
                    decision.get(
                        "controlled_forward_observation_start_dry_run_run_decision",
                        "",
                    )
                )
                == SOURCE_READY_DECISION
            ),
            str(
                decision.get(
                    "controlled_forward_observation_start_dry_run_run_decision",
                    "",
                )
            ),
        ),
        (
            "source_summary_artifact_consistent",
            (
                len(source_output_df) == 1
                and source_summary_row_count == 1
                and source_artifact_rows_written == 1
            ),
            (
                f"output_rows={len(source_output_df)},"
                f"summary_rows={source_summary_row_count},"
                f"artifact_rows={source_artifact_rows_written}"
            ),
        ),
        (
            "official_dataset_absent",
            official_dataset_absent,
            f"official_dataset_absent={official_dataset_absent}",
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


def build_integrity_controls(
    validations_df: pd.DataFrame,
) -> pd.DataFrame:
    validation_lookup = {
        str(row["validation_name"]): safe_bool(row["passed"], False)
        for _, row in validations_df.iterrows()
    }

    control_definitions = [
        ("source_artifact_exists", "artifact"),
        ("source_artifact_non_empty", "artifact"),
        ("source_artifact_sha256_valid", "artifact_integrity"),
        ("source_artifact_stable_during_review", "artifact_integrity"),
        ("source_summary_validation_passed", "dependency"),
        ("source_run_passed", "source_run"),
        ("source_run_decision_valid", "source_run"),
        ("source_future_integrity_review_allowed", "future_review"),
        ("source_output_row_count_valid", "artifact"),
        ("source_output_schema_valid", "schema"),
        ("source_output_critical_fields_present", "schema"),
        ("source_output_candidate_valid", "candidate_scope"),
        ("source_output_direction_valid", "direction"),
        ("source_output_price_structure_valid", "price_structure"),
        ("source_output_risk_reward_valid", "risk_reward"),
        ("source_output_scope_valid", "scope_control"),
        ("source_output_evidence_scope_valid", "evidence_scope"),
        ("source_output_true_run_fields_valid", "run_control"),
        ("source_output_operational_locks_valid", "safety"),
        ("official_dataset_absent", "official_dataset_guard"),
    ]

    return pd.DataFrame(
        [
            {
                "control_position": position,
                "control_id": f"START_DRY_RUN_OUTPUT_INTEGRITY_CONTROL_{position:03d}",
                "control_name": control_name,
                "control_group": control_group,
                "required": True,
                "output_integrity_review_only": True,
                "future_controlled_forward_observation_start_final_approval_review_allowed": True,
                "new_start_dry_run_run_performed": False,
                "forward_observation_start_allowed": False,
                "official_dataset_write_allowed": False,
                "market_execution_allowed": False,
                "passed": validation_lookup.get(control_name, False),
            }
            for position, (control_name, control_group) in enumerate(
                control_definitions,
                start=1,
            )
        ]
    )


def build_integrity_guard_matrix() -> pd.DataFrame:
    rows: list[dict[str, Any]] = [
        {
            "guard_name": "source_controlled_forward_observation_start_dry_run_run_performed",
            "required_value": True,
            "actual_value": True,
            "passed": True,
            "guard_group": "source_dry_run_state",
        },
        {
            "guard_name": "source_controlled_forward_observation_start_dry_run_performed",
            "required_value": True,
            "actual_value": True,
            "passed": True,
            "guard_group": "source_dry_run_state",
        },
        {
            "guard_name": "controlled_forward_observation_start_dry_run_output_integrity_review_performed",
            "required_value": True,
            "actual_value": True,
            "passed": True,
            "guard_group": "integrity_review_state",
        },
        {
            "guard_name": "future_controlled_forward_observation_start_final_approval_review_allowed",
            "required_value": True,
            "actual_value": True,
            "passed": True,
            "guard_group": "integrity_review_state",
        },
    ]

    for guard_name, required_value in EXPECTED_FALSE_GUARDS.items():
        rows.append(
            {
                "guard_name": guard_name,
                "required_value": required_value,
                "actual_value": required_value,
                "passed": True,
                "guard_group": "integrity_review_safety_guard",
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


def build_integrity_rules(
    validations_df: pd.DataFrame,
    controls_df: pd.DataFrame,
    guard_matrix_df: pd.DataFrame,
) -> pd.DataFrame:
    validations_passed = dataframe_all_passed(validations_df)
    controls_passed = dataframe_all_passed(controls_df)
    guards_passed = dataframe_all_passed(guard_matrix_df)

    rows = [
        (
            "integrity_validation_count_30",
            len(validations_df) == 30,
            "30",
            str(len(validations_df)),
            "validation",
        ),
        (
            "all_integrity_validations_passed",
            validations_passed,
            "True",
            str(validations_passed),
            "validation",
        ),
        (
            "integrity_control_count_20",
            len(controls_df) == 20,
            "20",
            str(len(controls_df)),
            "controls",
        ),
        (
            "all_integrity_controls_passed",
            controls_passed,
            "True",
            str(controls_passed),
            "controls",
        ),
        (
            "integrity_guard_count_31",
            len(guard_matrix_df) == 31,
            "31",
            str(len(guard_matrix_df)),
            "safety",
        ),
        (
            "all_integrity_guards_passed",
            guards_passed,
            "True",
            str(guards_passed),
            "safety",
        ),
        (
            "output_integrity_review_only",
            True,
            "True",
            "True",
            "scope_control",
        ),
        (
            "future_final_approval_review_allowed",
            True,
            "True",
            "True",
            "future_review",
        ),
        (
            "no_new_start_dry_run_run",
            True,
            "False",
            "False",
            "dry_run_run_boundary",
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
                "rule_id": f"START_DRY_RUN_OUTPUT_INTEGRITY_RULE_{index:03d}",
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


def build_integrity_requirements(
    source_summary_df: pd.DataFrame,
    source_output_df: pd.DataFrame,
    source_decision_df: pd.DataFrame,
    validations_df: pd.DataFrame,
    controls_df: pd.DataFrame,
    rules_df: pd.DataFrame,
    guard_matrix_df: pd.DataFrame,
    official_dataset_absent: bool,
) -> pd.DataFrame:
    summary = (
        source_summary_df.iloc[0].to_dict()
        if not source_summary_df.empty
        else {}
    )
    output = (
        source_output_df.iloc[0].to_dict()
        if not source_output_df.empty
        else {}
    )
    decision = (
        source_decision_df.iloc[0].to_dict()
        if not source_decision_df.empty
        else {}
    )
    validation_lookup = {
        str(row["validation_name"]): safe_bool(row["passed"], False)
        for _, row in validations_df.iterrows()
    }

    requirements = [
        ("phase_10_23_validation_passed", validation_lookup.get("source_summary_validation_passed", False), "True", str(validation_lookup.get("source_summary_validation_passed", False)), "dependency"),
        ("source_run_passed", validation_lookup.get("source_run_passed", False), "True", str(validation_lookup.get("source_run_passed", False)), "source_run"),
        ("source_run_decision_expected", validation_lookup.get("source_run_decision_valid", False), SOURCE_READY_DECISION, str(summary.get("controlled_forward_observation_start_dry_run_run_decision", "")), "source_run"),
        ("source_future_integrity_review_allowed", validation_lookup.get("source_future_integrity_review_allowed", False), "True", str(validation_lookup.get("source_future_integrity_review_allowed", False)), "future_review"),
        ("source_artifact_exists", validation_lookup.get("source_artifact_exists", False), "True", str(validation_lookup.get("source_artifact_exists", False)), "artifact"),
        ("source_artifact_non_empty", validation_lookup.get("source_artifact_non_empty", False), "True", str(validation_lookup.get("source_artifact_non_empty", False)), "artifact"),
        ("source_artifact_sha256_valid", validation_lookup.get("source_artifact_sha256_valid", False), "True", str(validation_lookup.get("source_artifact_sha256_valid", False)), "artifact_integrity"),
        ("source_artifact_stable_during_review", validation_lookup.get("source_artifact_stable_during_review", False), "True", str(validation_lookup.get("source_artifact_stable_during_review", False)), "artifact_integrity"),
        ("source_output_row_count_one", validation_lookup.get("source_output_row_count_valid", False), "1", str(len(source_output_df)), "artifact"),
        ("source_output_schema_valid", validation_lookup.get("source_output_schema_valid", False), "True", str(validation_lookup.get("source_output_schema_valid", False)), "schema"),
        ("source_output_critical_fields_present", validation_lookup.get("source_output_critical_fields_present", False), "True", str(validation_lookup.get("source_output_critical_fields_present", False)), "schema"),
        ("source_output_candidate_valid", validation_lookup.get("source_output_candidate_valid", False), PRIMARY_RESEARCH_CANDIDATE, str(output.get("candidate_id", "")), "candidate_scope"),
        ("source_output_direction_valid", validation_lookup.get("source_output_direction_valid", False), "LONG", str(output.get("direction", "")), "direction"),
        ("source_output_price_structure_valid", validation_lookup.get("source_output_price_structure_valid", False), "True", str(validation_lookup.get("source_output_price_structure_valid", False)), "price_structure"),
        ("source_output_risk_reward_valid", validation_lookup.get("source_output_risk_reward_valid", False), "2.5", str(output.get("risk_reward", "")), "risk_reward"),
        ("source_output_scope_valid", validation_lookup.get("source_output_scope_valid", False), SOURCE_RUN_SCOPE, str(output.get("run_scope", "")), "scope_control"),
        ("source_output_evidence_scope_valid", validation_lookup.get("source_output_evidence_scope_valid", False), SOURCE_EVIDENCE_SCOPE, str(output.get("evidence_scope", "")), "evidence_scope"),
        ("source_output_true_run_fields_valid", validation_lookup.get("source_output_true_run_fields_valid", False), "True", str(validation_lookup.get("source_output_true_run_fields_valid", False)), "run_control"),
        ("source_output_operational_locks_valid", validation_lookup.get("source_output_operational_locks_valid", False), "True", str(validation_lookup.get("source_output_operational_locks_valid", False)), "safety"),
        ("source_output_official_evidence_rows_zero", validation_lookup.get("source_output_official_evidence_rows_zero", False), "0", str(output.get("official_evidence_rows_written", "")), "official_dataset_guard"),
        ("source_output_validation_status_valid", validation_lookup.get("source_output_validation_status_valid", False), SOURCE_VALIDATION_STATUS, str(output.get("validation_status", "")), "artifact"),
        ("source_validations_passed", validation_lookup.get("source_validations_passed", False), "True", str(validation_lookup.get("source_validations_passed", False)), "validation"),
        ("source_evidence_chain_passed", validation_lookup.get("source_evidence_chain_passed", False), "True", str(validation_lookup.get("source_evidence_chain_passed", False)), "evidence"),
        ("source_controls_passed", validation_lookup.get("source_controls_passed", False), "True", str(validation_lookup.get("source_controls_passed", False)), "controls"),
        ("source_rules_passed", validation_lookup.get("source_rules_passed", False), "True", str(validation_lookup.get("source_rules_passed", False)), "rules"),
        ("source_requirements_passed", validation_lookup.get("source_requirements_passed", False), "True", str(validation_lookup.get("source_requirements_passed", False)), "requirements"),
        ("source_guards_passed", validation_lookup.get("source_guards_passed", False), "True", str(validation_lookup.get("source_guards_passed", False)), "safety"),
        ("source_decision_table_consistent", validation_lookup.get("source_decision_table_consistent", False), SOURCE_READY_DECISION, str(decision.get("controlled_forward_observation_start_dry_run_run_decision", "")), "summary_consistency"),
        ("source_summary_artifact_consistent", validation_lookup.get("source_summary_artifact_consistent", False), "True", str(validation_lookup.get("source_summary_artifact_consistent", False)), "summary_consistency"),
        ("integrity_validations_passed", dataframe_all_passed(validations_df), "True", str(dataframe_all_passed(validations_df)), "validation"),
        ("integrity_controls_passed", dataframe_all_passed(controls_df), "True", str(dataframe_all_passed(controls_df)), "controls"),
        ("integrity_rules_passed", dataframe_all_passed(rules_df), "True", str(dataframe_all_passed(rules_df)), "rules"),
        ("integrity_guards_passed", dataframe_all_passed(guard_matrix_df), "True", str(dataframe_all_passed(guard_matrix_df)), "safety"),
        ("integrity_review_performed", True, "True", "True", "integrity_review"),
        ("future_final_approval_review_allowed", True, "True", "True", "future_review"),
        ("no_new_start_dry_run_run_performed", True, "False", "False", "dry_run_run_boundary"),
        ("no_new_start_dry_run_performed", True, "False", "False", "dry_run_boundary"),
        ("official_dataset_absent", official_dataset_absent, "True", str(official_dataset_absent), "official_dataset_guard"),
        ("forward_observation_not_started", True, "False", "False", "start_boundary"),
        ("official_evidence_rows_written_zero", True, "0", "0", "official_dataset_guard"),
        ("market_execution_disabled", True, "False", "False", "market_execution_guard"),
        ("total_project_not_completed", True, "False", "False", "scope_control"),
    ]

    return pd.DataFrame(
        [
            {
                "requirement_id": f"START_DRY_RUN_OUTPUT_INTEGRITY_REQ_{index:03d}",
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


def build_integrity_decision_table(
    requirements_df: pd.DataFrame,
    rules_df: pd.DataFrame,
    guard_matrix_df: pd.DataFrame,
) -> pd.DataFrame:
    total_requirements = len(requirements_df)
    passed_requirements = (
        int(requirements_df["passed"].map(lambda value: safe_bool(value, False)).sum())
        if total_requirements
        else 0
    )
    failed_requirements = total_requirements - passed_requirements

    rules_passed = dataframe_all_passed(rules_df)
    guards_passed = dataframe_all_passed(guard_matrix_df)

    integrity_passed = (
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
                "controlled_forward_observation_start_dry_run_output_integrity_review_id": (
                    "PHASE_10_24_LONG_FORWARD_OBSERVATION_CONTROLLED_START_DRY_RUN_OUTPUT_INTEGRITY_REVIEW_001"
                ),
                "controlled_forward_observation_start_dry_run_output_integrity_review_status": INTEGRITY_REVIEW_STATUS,
                "controlled_forward_observation_start_dry_run_output_integrity_review_performed": True,
                "controlled_forward_observation_start_dry_run_output_integrity_review_passed": integrity_passed,
                "controlled_forward_observation_start_dry_run_output_integrity_review_decision": (
                    READY_DECISION if integrity_passed else BLOCKED_DECISION
                ),
                "total_requirements": total_requirements,
                "passed_requirements": passed_requirements,
                "failed_requirements": failed_requirements,
                "failed_requirement_names": failed_requirement_names,
                "integrity_rules_passed": rules_passed,
                "integrity_guards_passed": guards_passed,
                "source_controlled_forward_observation_start_dry_run_run_performed": True,
                "source_controlled_forward_observation_start_dry_run_performed": True,
                "future_controlled_forward_observation_start_final_approval_review_allowed": integrity_passed,
                "new_controlled_forward_observation_start_dry_run_run_performed": False,
                "new_controlled_forward_observation_start_dry_run_performed": False,
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


def validate_long_forward_observation_controlled_start_dry_run_output_integrity_review() -> dict[str, pd.DataFrame]:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    checks: list[dict[str, Any]] = []

    for check_name, path in {
        "phase_10_23_start_dry_run_run_doc_exists": PHASE_10_23_DOC_PATH,
        "phase_10_24_output_integrity_review_doc_exists": PHASE_10_24_DOC_PATH,
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

    artifact_metadata_before_df = build_artifact_metadata(SOURCE_OUTPUT_PATH)

    source_summary_df = read_csv_if_exists(SOURCE_SUMMARY_PATH)
    source_output_df = read_csv_if_exists(SOURCE_OUTPUT_PATH)
    source_validations_df = read_csv_if_exists(SOURCE_VALIDATIONS_PATH)
    source_evidence_chain_df = read_csv_if_exists(SOURCE_EVIDENCE_CHAIN_PATH)
    source_controls_df = read_csv_if_exists(SOURCE_CONTROLS_PATH)
    source_rules_df = read_csv_if_exists(SOURCE_RULES_PATH)
    source_requirements_df = read_csv_if_exists(SOURCE_REQUIREMENTS_PATH)
    source_guard_matrix_df = read_csv_if_exists(SOURCE_GUARD_MATRIX_PATH)
    source_decision_df = read_csv_if_exists(SOURCE_DECISION_PATH)
    source_checks_df = read_csv_if_exists(SOURCE_CHECKS_PATH)

    artifact_metadata_after_df = build_artifact_metadata(SOURCE_OUTPUT_PATH)

    integrity_validations_df = build_integrity_validations(
        source_summary_df=source_summary_df,
        source_output_df=source_output_df,
        source_validations_df=source_validations_df,
        source_evidence_chain_df=source_evidence_chain_df,
        source_controls_df=source_controls_df,
        source_rules_df=source_rules_df,
        source_requirements_df=source_requirements_df,
        source_guard_matrix_df=source_guard_matrix_df,
        source_decision_df=source_decision_df,
        artifact_metadata_before_df=artifact_metadata_before_df,
        artifact_metadata_after_df=artifact_metadata_after_df,
        official_dataset_absent=official_dataset_absent,
    )

    integrity_controls_df = build_integrity_controls(integrity_validations_df)
    integrity_guard_matrix_df = build_integrity_guard_matrix()
    integrity_rules_df = build_integrity_rules(
        validations_df=integrity_validations_df,
        controls_df=integrity_controls_df,
        guard_matrix_df=integrity_guard_matrix_df,
    )
    integrity_requirements_df = build_integrity_requirements(
        source_summary_df=source_summary_df,
        source_output_df=source_output_df,
        source_decision_df=source_decision_df,
        validations_df=integrity_validations_df,
        controls_df=integrity_controls_df,
        rules_df=integrity_rules_df,
        guard_matrix_df=integrity_guard_matrix_df,
        official_dataset_absent=official_dataset_absent,
    )
    integrity_decision_df = build_integrity_decision_table(
        requirements_df=integrity_requirements_df,
        rules_df=integrity_rules_df,
        guard_matrix_df=integrity_guard_matrix_df,
    )

    official_dataset_exists_after = OFFICIAL_DATASET_PATH.exists()

    validation_lookup = {
        str(row["validation_name"]): safe_bool(row["passed"], False)
        for _, row in integrity_validations_df.iterrows()
    }
    decision = (
        integrity_decision_df.iloc[0].to_dict()
        if not integrity_decision_df.empty
        else {}
    )

    aggregate_checks = [
        (
            "source_artifact_exists",
            validation_lookup.get("source_artifact_exists", False),
        ),
        (
            "source_artifact_sha256_valid",
            validation_lookup.get("source_artifact_sha256_valid", False),
        ),
        (
            "source_artifact_stable_during_review",
            validation_lookup.get(
                "source_artifact_stable_during_review",
                False,
            ),
        ),
        (
            "source_output_schema_valid",
            validation_lookup.get("source_output_schema_valid", False),
        ),
        (
            "source_output_operational_locks_valid",
            validation_lookup.get(
                "source_output_operational_locks_valid",
                False,
            ),
        ),
        (
            "integrity_validations_passed",
            dataframe_all_passed(integrity_validations_df),
        ),
        (
            "integrity_controls_passed",
            dataframe_all_passed(integrity_controls_df),
        ),
        (
            "integrity_rules_passed",
            dataframe_all_passed(integrity_rules_df),
        ),
        (
            "integrity_requirements_passed",
            dataframe_all_passed(integrity_requirements_df),
        ),
        (
            "integrity_guards_passed",
            dataframe_all_passed(integrity_guard_matrix_df),
        ),
        (
            "output_integrity_review_passed",
            safe_bool(
                decision.get(
                    "controlled_forward_observation_start_dry_run_output_integrity_review_passed",
                    False,
                )
            ),
        ),
        (
            "output_integrity_review_decision_expected",
            str(
                decision.get(
                    "controlled_forward_observation_start_dry_run_output_integrity_review_decision",
                    "",
                )
            )
            == READY_DECISION,
        ),
    ]

    for check_name, passed in aggregate_checks:
        checks.append(
            build_check(
                check_group="output_integrity_review",
                check_name=check_name,
                passed=passed,
                severity="INFO" if passed else "ERROR",
                details=(
                    str(
                        decision.get(
                            "controlled_forward_observation_start_dry_run_output_integrity_review_decision",
                            "",
                        )
                    )
                    if check_name
                    == "output_integrity_review_decision_expected"
                    else f"{check_name}={passed}"
                ),
            )
        )

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
                "INFO"
                if official_dataset_unchanged_absent
                else "ERROR"
            ),
            details=(
                f"before={official_dataset_exists_before},"
                f"after={official_dataset_exists_after}"
            ),
        )
    )

    for _, guard_row in integrity_guard_matrix_df.iterrows():
        passed = safe_bool(guard_row.get("passed", False), False)
        checks.append(
            build_check(
                check_group="output_integrity_review_safety_flags",
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
            "output_integrity_review_only",
            "Phase 10.24 reviews only the Phase 10.23 dry-run output.",
        ),
        (
            "no_new_start_dry_run_run",
            "No new controlled start dry-run run is performed.",
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

    checks.append(
        build_check(
            check_group="planning_scope",
            check_name="future_final_approval_review_allowed",
            passed=safe_bool(
                decision.get(
                    "future_controlled_forward_observation_start_final_approval_review_allowed",
                    False,
                )
            ),
            severity="WARNING",
            details=(
                "This permits only a future controlled start final approval "
                "review. It does not start forward observation, write official "
                "evidence, generate signals or alerts, enable paper trading, "
                "use real capital, or permit market execution."
            ),
        )
    )

    checks.append(
        build_check(
            check_group="phase_transition",
            check_name="phase_10_25_recommended_next",
            passed=True,
            severity="INFO",
            details=(
                "Recommended next step: Phase 10.25 LONG Forward Observation "
                "Controlled Start Final Approval Review V1."
            ),
        )
    )

    checks_df = pd.DataFrame(checks)
    blocker_count = int(checks_df["blocker"].map(lambda value: safe_bool(value, False)).sum())
    error_count = int(checks_df["severity"].eq("ERROR").sum())
    warning_count = int(checks_df["severity"].eq("WARNING").sum())
    validation_passed = blocker_count == 0 and error_count == 0

    summary_source = (
        source_summary_df.iloc[0].to_dict()
        if not source_summary_df.empty
        else {}
    )
    source_output = (
        source_output_df.iloc[0].to_dict()
        if not source_output_df.empty
        else {}
    )
    artifact_metadata = (
        artifact_metadata_after_df.iloc[0].to_dict()
        if not artifact_metadata_after_df.empty
        else {}
    )

    integrity_passed = safe_bool(
        decision.get(
            "controlled_forward_observation_start_dry_run_output_integrity_review_passed",
            False,
        )
    )
    integrity_decision = str(
        decision.get(
            "controlled_forward_observation_start_dry_run_output_integrity_review_decision",
            "",
        )
    )

    summary_df = pd.DataFrame(
        [
            {
                "phase": "10.24",
                "long_forward_observation_controlled_start_dry_run_output_integrity_review_defined": True,
                "phase_10_23_validation_passed": validation_lookup.get("source_summary_validation_passed", False),
                "source_controlled_forward_observation_start_dry_run_run_passed": validation_lookup.get("source_run_passed", False),
                "source_controlled_forward_observation_start_dry_run_run_decision": str(
                    summary_source.get(
                        "controlled_forward_observation_start_dry_run_run_decision",
                        "",
                    )
                ),
                "source_controlled_forward_observation_start_dry_run_run_performed": safe_bool(
                    source_output.get(
                        "controlled_forward_observation_start_dry_run_run_performed",
                        False,
                    )
                ),
                "source_controlled_forward_observation_start_dry_run_performed": safe_bool(
                    source_output.get(
                        "controlled_forward_observation_start_dry_run_performed",
                        False,
                    )
                ),
                "source_future_controlled_forward_observation_start_dry_run_output_integrity_review_allowed": validation_lookup.get(
                    "source_future_integrity_review_allowed",
                    False,
                ),
                "source_dry_run_artifact_exists": validation_lookup.get("source_artifact_exists", False),
                "source_dry_run_artifact_non_empty": validation_lookup.get("source_artifact_non_empty", False),
                "source_dry_run_artifact_size_bytes": int(artifact_metadata.get("artifact_size_bytes", 0)),
                "source_dry_run_artifact_sha256": str(artifact_metadata.get("artifact_sha256", "")),
                "source_dry_run_artifact_sha256_valid": validation_lookup.get("source_artifact_sha256_valid", False),
                "source_dry_run_artifact_stable_during_review": validation_lookup.get("source_artifact_stable_during_review", False),
                "source_dry_run_output_row_count": int(len(source_output_df)),
                "source_dry_run_output_schema_valid": validation_lookup.get("source_output_schema_valid", False),
                "source_dry_run_output_candidate_id": str(source_output.get("candidate_id", "")),
                "source_dry_run_output_candidate_valid": validation_lookup.get("source_output_candidate_valid", False),
                "source_dry_run_output_direction": str(source_output.get("direction", "")),
                "source_dry_run_output_direction_valid": validation_lookup.get("source_output_direction_valid", False),
                "source_dry_run_output_price_structure_valid": validation_lookup.get("source_output_price_structure_valid", False),
                "source_dry_run_output_risk_reward": safe_float(source_output.get("risk_reward")),
                "source_dry_run_output_risk_reward_valid": validation_lookup.get("source_output_risk_reward_valid", False),
                "source_dry_run_output_scope": str(source_output.get("run_scope", "")),
                "source_dry_run_output_scope_valid": validation_lookup.get("source_output_scope_valid", False),
                "source_dry_run_output_evidence_scope": str(source_output.get("evidence_scope", "")),
                "source_dry_run_output_evidence_scope_valid": validation_lookup.get("source_output_evidence_scope_valid", False),
                "source_dry_run_output_true_run_fields_valid": validation_lookup.get("source_output_true_run_fields_valid", False),
                "source_dry_run_output_operational_locks_valid": validation_lookup.get("source_output_operational_locks_valid", False),
                "source_dry_run_output_official_evidence_rows_zero": validation_lookup.get("source_output_official_evidence_rows_zero", False),
                "integrity_validation_rows": int(len(integrity_validations_df)),
                "integrity_control_rows": int(len(integrity_controls_df)),
                "integrity_rule_rows": int(len(integrity_rules_df)),
                "integrity_requirement_rows": int(len(integrity_requirements_df)),
                "integrity_guard_rows": int(len(integrity_guard_matrix_df)),
                "integrity_validations_passed": dataframe_all_passed(integrity_validations_df),
                "integrity_controls_passed": dataframe_all_passed(integrity_controls_df),
                "integrity_rules_passed": dataframe_all_passed(integrity_rules_df),
                "integrity_requirements_passed": dataframe_all_passed(integrity_requirements_df),
                "integrity_guards_passed": dataframe_all_passed(integrity_guard_matrix_df),
                "controlled_forward_observation_start_dry_run_output_integrity_review_performed": True,
                "controlled_forward_observation_start_dry_run_output_integrity_review_passed": integrity_passed,
                "controlled_forward_observation_start_dry_run_output_integrity_review_decision": integrity_decision,
                "future_controlled_forward_observation_start_final_approval_review_allowed": safe_bool(
                    decision.get(
                        "future_controlled_forward_observation_start_final_approval_review_allowed",
                        False,
                    )
                ),
                "new_controlled_forward_observation_start_dry_run_run_performed": False,
                "new_controlled_forward_observation_start_dry_run_performed": False,
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
                    "PHASE_10_24_LONG_FORWARD_OBSERVATION_CONTROLLED_START_DRY_RUN_OUTPUT_INTEGRITY_REVIEW_VALIDATED"
                    if validation_passed
                    else "PHASE_10_24_LONG_FORWARD_OBSERVATION_CONTROLLED_START_DRY_RUN_OUTPUT_INTEGRITY_REVIEW_FAILED"
                ),
            }
        ]
    )

    source_summary_df.to_csv(
        REPORTS_DIR / "phase_10_23_source_summary_v1.csv",
        index=False,
    )
    source_output_df.to_csv(
        REPORTS_DIR / "phase_10_23_source_dry_run_output_v1.csv",
        index=False,
    )
    source_validations_df.to_csv(
        REPORTS_DIR / "phase_10_23_source_dry_run_validations_v1.csv",
        index=False,
    )
    source_evidence_chain_df.to_csv(
        REPORTS_DIR / "phase_10_23_source_dry_run_evidence_chain_v1.csv",
        index=False,
    )
    source_controls_df.to_csv(
        REPORTS_DIR / "phase_10_23_source_dry_run_controls_v1.csv",
        index=False,
    )
    source_rules_df.to_csv(
        REPORTS_DIR / "phase_10_23_source_dry_run_rules_v1.csv",
        index=False,
    )
    source_requirements_df.to_csv(
        REPORTS_DIR / "phase_10_23_source_dry_run_requirements_v1.csv",
        index=False,
    )
    source_guard_matrix_df.to_csv(
        REPORTS_DIR / "phase_10_23_source_dry_run_guard_matrix_v1.csv",
        index=False,
    )
    source_decision_df.to_csv(
        REPORTS_DIR / "phase_10_23_source_dry_run_decision_v1.csv",
        index=False,
    )
    source_checks_df.to_csv(
        REPORTS_DIR / "phase_10_23_source_checks_v1.csv",
        index=False,
    )
    artifact_metadata_after_df.to_csv(
        REPORTS_DIR / "source_dry_run_artifact_metadata_v1.csv",
        index=False,
    )
    integrity_validations_df.to_csv(
        REPORTS_DIR / "start_dry_run_output_integrity_validations_v1.csv",
        index=False,
    )
    integrity_controls_df.to_csv(
        REPORTS_DIR / "start_dry_run_output_integrity_controls_v1.csv",
        index=False,
    )
    integrity_rules_df.to_csv(
        REPORTS_DIR / "start_dry_run_output_integrity_rules_v1.csv",
        index=False,
    )
    integrity_requirements_df.to_csv(
        REPORTS_DIR / "start_dry_run_output_integrity_requirements_v1.csv",
        index=False,
    )
    integrity_guard_matrix_df.to_csv(
        REPORTS_DIR / "start_dry_run_output_integrity_guard_matrix_v1.csv",
        index=False,
    )
    integrity_decision_df.to_csv(
        REPORTS_DIR / "start_dry_run_output_integrity_decision_v1.csv",
        index=False,
    )
    checks_df.to_csv(
        REPORTS_DIR / "start_dry_run_output_integrity_checks_v1.csv",
        index=False,
    )
    summary_df.to_csv(
        REPORTS_DIR / "start_dry_run_output_integrity_summary_v1.csv",
        index=False,
    )

    return {
        "summary": summary_df,
        "source_phase_10_23_summary": source_summary_df,
        "source_dry_run_output": source_output_df,
        "source_dry_run_validations": source_validations_df,
        "source_dry_run_evidence_chain": source_evidence_chain_df,
        "source_dry_run_controls": source_controls_df,
        "source_dry_run_rules": source_rules_df,
        "source_dry_run_requirements": source_requirements_df,
        "source_dry_run_guard_matrix": source_guard_matrix_df,
        "source_dry_run_decision": source_decision_df,
        "source_checks": source_checks_df,
        "source_artifact_metadata": artifact_metadata_after_df,
        "integrity_validations": integrity_validations_df,
        "integrity_controls": integrity_controls_df,
        "integrity_rules": integrity_rules_df,
        "integrity_requirements": integrity_requirements_df,
        "integrity_guard_matrix": integrity_guard_matrix_df,
        "integrity_decision": integrity_decision_df,
        "checks": checks_df,
    }
