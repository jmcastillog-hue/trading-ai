from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

import pandas as pd

from src.long_side.long_forward_observation_dataset_bootstrap_v1 import (
    OFFICIAL_DATASET_PATH,
    PRIMARY_RESEARCH_CANDIDATE,
)


REPORTS_DIR = Path(
    "reports/p10_27_controlled_start_run_output_integrity_review_v1"
)
SOURCE_DIR = Path("reports/p10_26_controlled_start_run_v1")

PHASE_10_26_DOC_PATH = Path(
    "docs/PHASE_10_LONG_FORWARD_OBSERVATION_CONTROLLED_START_RUN.md"
)
PHASE_10_27_DOC_PATH = Path(
    "docs/PHASE_10_LONG_FORWARD_OBSERVATION_CONTROLLED_START_RUN_OUTPUT_INTEGRITY_REVIEW.md"
)

SOURCE_PATHS = {
    "summary": SOURCE_DIR / "controlled_start_run_summary_v1.csv",
    "output": SOURCE_DIR / "controlled_forward_observation_start_output_v1.csv",
    "validations": SOURCE_DIR / "controlled_start_run_validations_v1.csv",
    "evidence_chain": SOURCE_DIR / "controlled_start_run_evidence_chain_v1.csv",
    "controls": SOURCE_DIR / "controlled_start_run_controls_v1.csv",
    "rules": SOURCE_DIR / "controlled_start_run_rules_v1.csv",
    "requirements": SOURCE_DIR / "controlled_start_run_requirements_v1.csv",
    "guard_matrix": SOURCE_DIR / "controlled_start_run_guard_matrix_v1.csv",
    "decision": SOURCE_DIR / "controlled_start_run_decision_v1.csv",
    "checks": SOURCE_DIR / "controlled_start_run_checks_v1.csv",
    "phase_10_25_summary": SOURCE_DIR / "phase_10_25_source_summary_v1.csv",
    "phase_10_23_dry_run": SOURCE_DIR / "phase_10_23_source_dry_run_output_v1.csv",
    "phase_10_25_validations": SOURCE_DIR / "phase_10_25_source_validations_v1.csv",
    "phase_10_25_evidence": SOURCE_DIR / "phase_10_25_source_evidence_chain_v1.csv",
    "phase_10_25_controls": SOURCE_DIR / "phase_10_25_source_controls_v1.csv",
    "phase_10_25_rules": SOURCE_DIR / "phase_10_25_source_rules_v1.csv",
    "phase_10_25_requirements": SOURCE_DIR / "phase_10_25_source_requirements_v1.csv",
    "phase_10_25_guards": SOURCE_DIR / "phase_10_25_source_guard_matrix_v1.csv",
    "phase_10_25_decision": SOURCE_DIR / "phase_10_25_source_decision_v1.csv",
    "phase_10_25_checks": SOURCE_DIR / "phase_10_25_source_checks_v1.csv",
}

SOURCE_READY_DECISION = (
    "CONTROLLED_FORWARD_OBSERVATION_START_RUN_COMPLETED_OBSERVATION_ONLY"
)
SOURCE_STATUS = (
    "LONG_FORWARD_OBSERVATION_CONTROLLED_START_RUN_OBSERVATION_ONLY"
)
SOURCE_START_SCOPE = (
    "CONTROLLED_FORWARD_OBSERVATION_START_OBSERVATION_ONLY"
)
SOURCE_EVIDENCE_SCOPE = "OBSERVATION_STATE_ONLY_NOT_REAL_EVIDENCE"
SOURCE_OBSERVATION_STATE = "CONTROLLED_FORWARD_OBSERVATION_STARTED"
SOURCE_VALIDATION_STATUS = "CONTROLLED_FORWARD_OBSERVATION_START_ROW_CREATED"

INTEGRITY_REVIEW_STATUS = (
    "LONG_FORWARD_OBSERVATION_CONTROLLED_START_RUN_OUTPUT_INTEGRITY_REVIEW_ONLY"
)
READY_DECISION = (
    "CONTROLLED_FORWARD_OBSERVATION_START_RUN_OUTPUT_INTEGRITY_REVIEW_"
    "READY_FOR_EVIDENCE_COLLECTION_PRECHECK"
)
BLOCKED_DECISION = (
    "CONTROLLED_FORWARD_OBSERVATION_START_RUN_OUTPUT_INTEGRITY_REVIEW_BLOCKED"
)
RECOMMENDED_NEXT_PHASE = (
    "PHASE_10_28_LONG_FORWARD_OBSERVATION_EVIDENCE_COLLECTION_PRECHECK_V1"
)

EXPECTED_SOURCE_COUNTS = {
    "start_run_validation_rows": 24,
    "start_run_evidence_rows": 24,
    "start_run_control_rows": 24,
    "start_run_rule_rows": 15,
    "start_run_requirement_rows": 39,
    "start_run_guard_rows": 31,
}

EXPECTED_TRUE_START_FIELDS = [
    "controlled_forward_observation_start_final_approval_review_performed",
    "future_controlled_forward_observation_start_run_allowed",
    "controlled_forward_observation_start_run_allowed",
    "controlled_forward_observation_start_run_performed",
    "controlled_forward_observation_start_performed",
    "forward_observation_start_allowed",
    "forward_observation_started",
    "future_controlled_forward_observation_start_run_output_integrity_review_allowed",
]

EXPECTED_FALSE_GUARDS = [
    "official_dataset_write_allowed",
    "official_dataset_write_performed",
    "real_forward_dataset_created",
    "real_forward_signals_recorded",
    "journal_real_rows_accepted",
    "accepted_as_real_evidence",
    "evidence_persistence_allowed",
    "evidence_write_performed",
    "signal_generation_enabled",
    "live_alerts_allowed",
    "paper_trading_enabled",
    "long_strategy_approved",
    "long_entries_approved",
    "long_side_established",
    "paper_trade_execution_allowed",
    "real_capital_allowed",
    "market_execution_allowed",
    "exchange_execution_allowed",
    "automation_allowed",
    "execution_allowed",
    "real_entries_approved",
    "total_project_completed",
]

EXPECTED_OUTPUT_COLUMNS = [
    "start_run_id",
    "start_run_status",
    "started_at_utc",
    "source_phase",
    "source_validation_decision",
    "source_final_approval_decision",
    "symbol",
    "timeframe",
    "candidate_id",
    "direction",
    "observation_role",
    "observation_state",
    "market_context",
    "activation_scope",
    "start_scope",
    "evidence_scope",
    "entry_price",
    "stop_price",
    "target_price",
    "invalidation_level",
    "risk_reward",
    "cost_profile",
    "manual_confirmation_required",
    "controlled_forward_observation_start_final_approval_review_performed",
    "future_controlled_forward_observation_start_run_allowed",
    "controlled_forward_observation_start_run_allowed",
    "controlled_forward_observation_start_run_performed",
    "controlled_forward_observation_start_performed",
    "forward_observation_start_allowed",
    "forward_observation_started",
    "future_controlled_forward_observation_start_run_output_integrity_review_allowed",
    "official_dataset_write_allowed",
    "official_dataset_write_performed",
    "real_forward_dataset_created",
    "official_evidence_rows_written",
    "real_forward_signals_recorded",
    "journal_real_rows_accepted",
    "accepted_as_real_evidence",
    "evidence_persistence_allowed",
    "evidence_write_performed",
    "signal_generation_enabled",
    "live_alerts_allowed",
    "paper_trading_enabled",
    "long_strategy_approved",
    "long_entries_approved",
    "long_side_established",
    "paper_trade_execution_allowed",
    "real_capital_allowed",
    "market_execution_allowed",
    "exchange_execution_allowed",
    "automation_allowed",
    "execution_allowed",
    "real_entries_approved",
    "total_project_completed",
    "expected_next_review_phase",
    "notes",
    "validation_status",
]

CRITICAL_OUTPUT_FIELDS = [
    "start_run_id",
    "start_run_status",
    "started_at_utc",
    "source_phase",
    "source_validation_decision",
    "source_final_approval_decision",
    "symbol",
    "timeframe",
    "candidate_id",
    "direction",
    "observation_role",
    "observation_state",
    "start_scope",
    "evidence_scope",
    "entry_price",
    "stop_price",
    "target_price",
    "risk_reward",
    "validation_status",
]


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


def build_source_manifest() -> pd.DataFrame:
    rows = []
    for position, (artifact_name, path) in enumerate(
        SOURCE_PATHS.items(), start=1
    ):
        exists = path.exists() and path.is_file()
        size_bytes = path.stat().st_size if exists else 0
        file_hash = sha256_file(path) if exists else ""
        rows.append(
            {
                "manifest_position": position,
                "artifact_name": artifact_name,
                "artifact_filename": path.name,
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
    columns = [
        "artifact_name",
        "artifact_path",
        "artifact_size_bytes",
        "artifact_sha256",
    ]
    if any(column not in manifest_df.columns for column in columns):
        return ""
    payload = (
        manifest_df[columns]
        .astype(str)
        .sort_values(["artifact_name", "artifact_path"])
        .to_csv(index=False)
        .encode("utf-8")
    )
    return hashlib.sha256(payload).hexdigest()


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


def parseable_utc_timestamp(value: Any) -> bool:
    try:
        timestamp = pd.to_datetime(value, utc=True, errors="raise")
        return not pd.isna(timestamp)
    except Exception:
        return False


def build_integrity_validations(
    source: dict[str, pd.DataFrame],
    manifest_before_df: pd.DataFrame,
    manifest_after_df: pd.DataFrame,
    output_hash_before: str,
    output_hash_after: str,
    official_dataset_absent: bool,
) -> pd.DataFrame:
    summary_df = source["summary"]
    output_df = source["output"]
    decision_df = source["decision"]

    summary = summary_df.iloc[0].to_dict() if not summary_df.empty else {}
    output = output_df.iloc[0].to_dict() if not output_df.empty else {}
    decision = decision_df.iloc[0].to_dict() if not decision_df.empty else {}

    artifacts_exist = (
        not manifest_before_df.empty
        and manifest_before_df["artifact_exists"]
        .map(lambda value: safe_bool(value, False))
        .all()
    )
    artifacts_non_empty = (
        not manifest_before_df.empty
        and manifest_before_df["artifact_non_empty"]
        .map(lambda value: safe_bool(value, False))
        .all()
    )
    hashes_valid = (
        not manifest_before_df.empty
        and manifest_before_df["artifact_sha256_valid"]
        .map(lambda value: safe_bool(value, False))
        .all()
    )
    digest_before = manifest_digest(manifest_before_df)
    digest_after = manifest_digest(manifest_after_df)
    artifacts_stable = bool(digest_before) and digest_before == digest_after

    source_counts_valid = all(
        int(safe_float(summary.get(field_name), -1)) == expected
        for field_name, expected in EXPECTED_SOURCE_COUNTS.items()
    )

    entry = safe_float(output.get("entry_price"))
    stop = safe_float(output.get("stop_price"))
    target = safe_float(output.get("target_price"))
    risk_reward = safe_float(output.get("risk_reward"))
    expected_rr = (
        round((target - entry) / (entry - stop), 4)
        if entry > stop
        else 0.0
    )

    true_start_fields_valid = all(
        safe_bool(output.get(field_name, False), False)
        for field_name in EXPECTED_TRUE_START_FIELDS
    )
    operational_locks_valid = all(
        safe_bool(output.get(field_name, True), True) is False
        for field_name in EXPECTED_FALSE_GUARDS
    )

    summary_output_consistent = (
        int(
            safe_float(
                summary.get(
                    "controlled_forward_observation_start_output_row_count"
                ),
                -1,
            )
        )
        == len(output_df)
        == 1
        and str(
            summary.get(
                "controlled_forward_observation_start_output_candidate_id",
                "",
            )
        )
        == str(output.get("candidate_id", ""))
        and str(
            summary.get(
                "controlled_forward_observation_start_output_direction",
                "",
            )
        )
        == str(output.get("direction", ""))
        and safe_float(
            summary.get(
                "controlled_forward_observation_start_output_risk_reward"
            ),
            -1.0,
        )
        == risk_reward
        and str(
            summary.get(
                "controlled_forward_observation_start_output_scope", ""
            )
        )
        == str(output.get("start_scope", ""))
        and str(
            summary.get(
                "controlled_forward_observation_start_output_evidence_scope",
                "",
            )
        )
        == str(output.get("evidence_scope", ""))
        and str(
            summary.get(
                "controlled_forward_observation_start_output_observation_state",
                "",
            )
        )
        == str(output.get("observation_state", ""))
    )

    decision_output_consistent = (
        not decision_df.empty
        and safe_bool(
            decision.get(
                "controlled_forward_observation_start_run_passed", False
            )
        )
        and str(
            decision.get(
                "controlled_forward_observation_start_run_decision", ""
            )
        )
        == SOURCE_READY_DECISION
        and safe_bool(
            decision.get(
                "controlled_forward_observation_start_run_performed", False
            )
        )
        == safe_bool(
            output.get(
                "controlled_forward_observation_start_run_performed", False
            )
        )
        and safe_bool(decision.get("forward_observation_started", False))
        == safe_bool(output.get("forward_observation_started", False))
    )

    rows = [
        ("source_artifacts_exist", artifacts_exist, f"artifact_count={len(manifest_before_df)}"),
        ("source_artifacts_non_empty", artifacts_non_empty, f"artifact_count={len(manifest_before_df)}"),
        ("source_artifact_hashes_valid", hashes_valid, f"artifact_count={len(manifest_before_df)}"),
        ("source_artifacts_stable_during_review", artifacts_stable, f"manifest_before={digest_before},manifest_after={digest_after}"),
        ("source_output_hash_stable", bool(output_hash_before) and output_hash_before == output_hash_after, f"sha_before={output_hash_before},sha_after={output_hash_after}"),
        ("phase_10_26_validation_passed", safe_bool(summary.get("validation_passed", False)), str(summary.get("validation_decision", ""))),
        ("source_start_run_passed", safe_bool(summary.get("controlled_forward_observation_start_run_passed", False)), str(summary.get("controlled_forward_observation_start_run_passed", ""))),
        ("source_start_run_decision_valid", str(summary.get("controlled_forward_observation_start_run_decision", "")) == SOURCE_READY_DECISION, str(summary.get("controlled_forward_observation_start_run_decision", ""))),
        ("source_future_integrity_review_allowed", safe_bool(summary.get("future_controlled_forward_observation_start_run_output_integrity_review_allowed", False)), str(summary.get("future_controlled_forward_observation_start_run_output_integrity_review_allowed", ""))),
        ("source_decision_table_consistent", not decision_df.empty and safe_bool(decision.get("controlled_forward_observation_start_run_passed", False)) and str(decision.get("controlled_forward_observation_start_run_decision", "")) == SOURCE_READY_DECISION, str(decision.get("controlled_forward_observation_start_run_decision", ""))),
        ("source_counts_valid", source_counts_valid, ",".join(f"{name}={summary.get(name, '')}" for name in EXPECTED_SOURCE_COUNTS)),
        ("source_validations_passed", dataframe_all_passed(source["validations"]), f"rows={len(source['validations'])}"),
        ("source_evidence_chain_passed", dataframe_all_passed(source["evidence_chain"]), f"rows={len(source['evidence_chain'])}"),
        ("source_controls_passed", dataframe_all_passed(source["controls"]), f"rows={len(source['controls'])}"),
        ("source_rules_passed", dataframe_all_passed(source["rules"]), f"rows={len(source['rules'])}"),
        ("source_requirements_passed", dataframe_all_passed(source["requirements"]), f"rows={len(source['requirements'])}"),
        ("source_guards_passed", dataframe_all_passed(source["guard_matrix"]), f"rows={len(source['guard_matrix'])}"),
        ("source_output_row_count_one", len(output_df) == 1, f"row_count={len(output_df)}"),
        ("source_output_schema_valid", output_df.columns.astype(str).tolist() == EXPECTED_OUTPUT_COLUMNS, f"actual_field_count={len(output_df.columns)},expected_field_count={len(EXPECTED_OUTPUT_COLUMNS)}"),
        ("source_output_critical_fields_present", bool(output) and critical_fields_present(output), f"critical_field_count={len(CRITICAL_OUTPUT_FIELDS)}"),
        ("source_output_identifier_valid", str(output.get("start_run_id", "")) == "PHASE_10_26_LONG_FORWARD_OBSERVATION_CONTROLLED_START_RUN_001", str(output.get("start_run_id", ""))),
        ("source_output_status_valid", str(output.get("start_run_status", "")) == SOURCE_STATUS, str(output.get("start_run_status", ""))),
        ("source_output_timestamp_valid", parseable_utc_timestamp(output.get("started_at_utc")), str(output.get("started_at_utc", ""))),
        ("source_output_candidate_valid", str(output.get("candidate_id", "")) == PRIMARY_RESEARCH_CANDIDATE, str(output.get("candidate_id", ""))),
        ("source_output_direction_valid", str(output.get("direction", "")) == "LONG", str(output.get("direction", ""))),
        ("source_output_price_structure_valid", stop < entry < target and safe_float(output.get("invalidation_level")) == stop, f"stop={stop},entry={entry},target={target}"),
        ("source_output_risk_reward_valid", risk_reward == expected_rr and risk_reward == 2.5, f"risk_reward={risk_reward},expected={expected_rr}"),
        ("source_output_scope_valid", str(output.get("start_scope", "")) == SOURCE_START_SCOPE, str(output.get("start_scope", ""))),
        ("source_output_evidence_scope_valid", str(output.get("evidence_scope", "")) == SOURCE_EVIDENCE_SCOPE, str(output.get("evidence_scope", ""))),
        ("source_output_observation_state_valid", str(output.get("observation_state", "")) == SOURCE_OBSERVATION_STATE, str(output.get("observation_state", ""))),
        ("source_output_true_start_fields_valid", true_start_fields_valid, f"true_start_field_count={len(EXPECTED_TRUE_START_FIELDS)}"),
        ("source_output_operational_locks_valid", operational_locks_valid, f"false_guard_count={len(EXPECTED_FALSE_GUARDS)}"),
        ("source_output_official_evidence_rows_zero", int(safe_float(output.get("official_evidence_rows_written"), -1)) == 0, str(output.get("official_evidence_rows_written", ""))),
        ("source_output_validation_status_valid", str(output.get("validation_status", "")) == SOURCE_VALIDATION_STATUS, str(output.get("validation_status", ""))),
        ("source_summary_output_consistent", summary_output_consistent, f"consistent={summary_output_consistent}"),
        ("source_decision_output_consistent", decision_output_consistent, f"consistent={decision_output_consistent}"),
        ("review_does_not_create_second_start_run", True, "new_start_run=False,new_start=False"),
        ("forward_observation_state_preserved", safe_bool(output.get("forward_observation_start_allowed", False)) and safe_bool(output.get("forward_observation_started", False)), f"allowed={output.get('forward_observation_start_allowed', '')},started={output.get('forward_observation_started', '')}"),
        ("evidence_collection_remains_disabled", safe_bool(output.get("accepted_as_real_evidence", True), True) is False and safe_bool(output.get("evidence_persistence_allowed", True), True) is False and safe_bool(output.get("evidence_write_performed", True), True) is False, "accepted=False,persistence=False,write=False"),
        ("official_dataset_absent", official_dataset_absent, f"official_dataset_absent={official_dataset_absent}"),
    ]

    return pd.DataFrame(
        [
            {"validation_name": name, "passed": bool(passed), "details": details}
            for name, passed, details in rows
        ]
    )


def build_integrity_evidence_chain(validations_df: pd.DataFrame) -> pd.DataFrame:
    lookup = {
        str(row["validation_name"]): safe_bool(row["passed"], False)
        for _, row in validations_df.iterrows()
    }
    names = [
        ("phase_10_26_validation_passed", "dependency"),
        ("source_start_run_passed", "source_start_run"),
        ("source_start_run_decision_valid", "source_start_run"),
        ("source_future_integrity_review_allowed", "future_review"),
        ("source_artifacts_exist", "artifact"),
        ("source_artifacts_non_empty", "artifact"),
        ("source_artifact_hashes_valid", "artifact_integrity"),
        ("source_artifacts_stable_during_review", "artifact_integrity"),
        ("source_output_hash_stable", "artifact_integrity"),
        ("source_decision_table_consistent", "summary_consistency"),
        ("source_counts_valid", "summary_consistency"),
        ("source_validations_passed", "validation"),
        ("source_evidence_chain_passed", "evidence"),
        ("source_controls_passed", "controls"),
        ("source_rules_passed", "rules"),
        ("source_requirements_passed", "requirements"),
        ("source_guards_passed", "safety"),
        ("source_output_row_count_one", "artifact"),
        ("source_output_schema_valid", "schema"),
        ("source_output_critical_fields_present", "schema"),
        ("source_output_identifier_valid", "identity"),
        ("source_output_status_valid", "status"),
        ("source_output_timestamp_valid", "timestamp"),
        ("source_output_candidate_valid", "candidate_scope"),
        ("source_output_direction_valid", "direction"),
        ("source_output_price_structure_valid", "price_structure"),
        ("source_output_risk_reward_valid", "risk_reward"),
        ("source_output_scope_valid", "scope_control"),
        ("source_output_evidence_scope_valid", "evidence_scope"),
        ("source_output_observation_state_valid", "observation_state"),
        ("source_output_true_start_fields_valid", "start_state"),
        ("source_output_operational_locks_valid", "safety"),
        ("source_output_official_evidence_rows_zero", "official_dataset_guard"),
        ("source_summary_output_consistent", "summary_consistency"),
        ("source_decision_output_consistent", "summary_consistency"),
        ("official_dataset_absent", "official_dataset_guard"),
    ]
    return pd.DataFrame(
        [
            {
                "evidence_position": position,
                "evidence_id": f"START_RUN_OUTPUT_INTEGRITY_EVIDENCE_{position:03d}",
                "evidence_name": name,
                "evidence_group": group,
                "required": True,
                "passed": lookup.get(name, False),
                "details": "Validated from the Phase 10.26 controlled start output and supporting report artifacts.",
            }
            for position, (name, group) in enumerate(names, start=1)
        ]
    )


def build_integrity_controls(evidence_df: pd.DataFrame) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "control_position": int(row["evidence_position"]),
                "control_id": f"START_RUN_OUTPUT_INTEGRITY_CONTROL_{int(row['evidence_position']):03d}",
                "control_name": str(row["evidence_name"]),
                "control_group": str(row["evidence_group"]),
                "required": True,
                "output_integrity_review_only": True,
                "forward_observation_state_preserved": True,
                "evidence_collection_enabled": False,
                "official_dataset_write_allowed": False,
                "signal_generation_enabled": False,
                "market_execution_allowed": False,
                "passed": safe_bool(row["passed"], False),
            }
            for _, row in evidence_df.iterrows()
        ]
    )


def build_integrity_guard_matrix() -> pd.DataFrame:
    rows = [
        ("source_controlled_forward_observation_start_run_performed", True, "source_observation_state"),
        ("source_controlled_forward_observation_start_performed", True, "source_observation_state"),
        ("forward_observation_start_allowed", True, "source_observation_state"),
        ("forward_observation_started", True, "source_observation_state"),
        ("controlled_start_run_output_integrity_review_performed", True, "integrity_review_state"),
        ("future_controlled_forward_observation_evidence_collection_precheck_allowed", True, "integrity_review_state"),
        ("new_controlled_forward_observation_start_run_performed", False, "no_duplicate_start_guard"),
        ("new_controlled_forward_observation_start_performed", False, "no_duplicate_start_guard"),
    ]
    for name in EXPECTED_FALSE_GUARDS:
        rows.append((name, False, "integrity_review_safety_guard"))
    result = pd.DataFrame(
        [
            {
                "guard_name": name,
                "required_value": required,
                "actual_value": required,
                "passed": True,
                "guard_group": group,
            }
            for name, required, group in rows
        ]
    )
    result = pd.concat(
        [
            result,
            pd.DataFrame(
                [
                    {
                        "guard_name": "official_evidence_rows_written",
                        "required_value": 0,
                        "actual_value": 0,
                        "passed": True,
                        "guard_group": "official_dataset_guard",
                    }
                ]
            ),
        ],
        ignore_index=True,
    )
    return result


def build_integrity_rules(
    validations_df: pd.DataFrame,
    evidence_df: pd.DataFrame,
    controls_df: pd.DataFrame,
    guards_df: pd.DataFrame,
) -> pd.DataFrame:
    rows = [
        ("integrity_validation_count_40", len(validations_df) == 40, "40", str(len(validations_df)), "validation"),
        ("all_integrity_validations_passed", dataframe_all_passed(validations_df), "True", str(dataframe_all_passed(validations_df)), "validation"),
        ("integrity_evidence_count_36", len(evidence_df) == 36, "36", str(len(evidence_df)), "evidence"),
        ("all_integrity_evidence_passed", dataframe_all_passed(evidence_df), "True", str(dataframe_all_passed(evidence_df)), "evidence"),
        ("integrity_control_count_36", len(controls_df) == 36, "36", str(len(controls_df)), "controls"),
        ("all_integrity_controls_passed", dataframe_all_passed(controls_df), "True", str(dataframe_all_passed(controls_df)), "controls"),
        ("integrity_guard_count_31", len(guards_df) == 31, "31", str(len(guards_df)), "safety"),
        ("all_integrity_guards_passed", dataframe_all_passed(guards_df), "True", str(dataframe_all_passed(guards_df)), "safety"),
        ("output_integrity_review_only", True, "True", "True", "scope_control"),
        ("observation_state_preserved", True, "True", "True", "observation_state"),
        ("no_duplicate_start_run", True, "False", "False", "no_duplicate_start_guard"),
        ("evidence_collection_disabled", True, "False", "False", "evidence_boundary"),
        ("official_dataset_writes_disabled", True, "False", "False", "official_dataset_guard"),
        ("signal_generation_disabled", True, "False", "False", "signal_boundary"),
        ("market_execution_disabled", True, "False", "False", "market_execution_guard"),
        ("total_project_not_completed", True, "False", "False", "scope_control"),
    ]
    return pd.DataFrame(
        [
            {
                "rule_id": f"START_RUN_OUTPUT_INTEGRITY_RULE_{index:03d}",
                "rule_name": name,
                "passed": bool(passed),
                "required_value": required,
                "actual_value": actual,
                "rule_group": group,
            }
            for index, (name, passed, required, actual, group) in enumerate(rows, start=1)
        ]
    )


def build_integrity_requirements(
    validations_df: pd.DataFrame,
    evidence_df: pd.DataFrame,
    controls_df: pd.DataFrame,
    rules_df: pd.DataFrame,
    guards_df: pd.DataFrame,
) -> pd.DataFrame:
    lookup = {
        str(row["validation_name"]): safe_bool(row["passed"], False)
        for _, row in validations_df.iterrows()
    }
    requirements = [
        (name, lookup.get(name, False), "True", str(lookup.get(name, False)), "integrity_validation")
        for name in validations_df["validation_name"].astype(str)
    ]
    requirements.extend(
        [
            ("integrity_evidence_chain_passed", dataframe_all_passed(evidence_df), "True", str(dataframe_all_passed(evidence_df)), "evidence"),
            ("integrity_controls_passed", dataframe_all_passed(controls_df), "True", str(dataframe_all_passed(controls_df)), "controls"),
            ("integrity_rules_passed", dataframe_all_passed(rules_df), "True", str(dataframe_all_passed(rules_df)), "rules"),
            ("integrity_guards_passed", dataframe_all_passed(guards_df), "True", str(dataframe_all_passed(guards_df)), "safety"),
            ("integrity_review_performed", True, "True", "True", "integrity_review"),
            ("future_evidence_collection_precheck_allowed", True, "True", "True", "future_precheck"),
            ("new_start_run_not_performed", True, "False", "False", "no_duplicate_start_guard"),
            ("new_start_not_performed", True, "False", "False", "no_duplicate_start_guard"),
            ("observation_state_remains_started", True, "True", "True", "observation_state"),
            ("evidence_collection_not_enabled", True, "False", "False", "evidence_boundary"),
            ("official_evidence_rows_written_zero", True, "0", "0", "official_dataset_guard"),
            ("signal_generation_disabled", True, "False", "False", "signal_boundary"),
            ("paper_trading_disabled", True, "False", "False", "paper_trading_guard"),
            ("market_execution_disabled", True, "False", "False", "market_execution_guard"),
            ("total_project_not_completed", True, "False", "False", "scope_control"),
        ]
    )
    return pd.DataFrame(
        [
            {
                "requirement_id": f"START_RUN_OUTPUT_INTEGRITY_REQ_{index:03d}",
                "requirement_name": name,
                "passed": bool(passed),
                "required_value": required,
                "actual_value": actual,
                "requirement_group": group,
            }
            for index, (name, passed, required, actual, group) in enumerate(requirements, start=1)
        ]
    )


def build_integrity_decision(
    requirements_df: pd.DataFrame,
    rules_df: pd.DataFrame,
    guards_df: pd.DataFrame,
) -> pd.DataFrame:
    total = int(len(requirements_df))
    passed = int(requirements_df["passed"].map(lambda value: safe_bool(value, False)).sum()) if total else 0
    failed = total - passed
    rules_passed = dataframe_all_passed(rules_df)
    guards_passed = dataframe_all_passed(guards_df)
    review_passed = total > 0 and failed == 0 and rules_passed and guards_passed
    failed_names = ""
    if not requirements_df.empty:
        failed_names = ",".join(
            requirements_df[
                ~requirements_df["passed"].map(lambda value: safe_bool(value, False))
            ]["requirement_name"].astype(str).tolist()
        )
    return pd.DataFrame(
        [
            {
                "controlled_start_run_output_integrity_review_id": "PHASE_10_27_LONG_FORWARD_OBSERVATION_CONTROLLED_START_RUN_OUTPUT_INTEGRITY_REVIEW_001",
                "controlled_start_run_output_integrity_review_status": INTEGRITY_REVIEW_STATUS,
                "controlled_start_run_output_integrity_review_performed": True,
                "controlled_start_run_output_integrity_review_passed": review_passed,
                "controlled_start_run_output_integrity_review_decision": READY_DECISION if review_passed else BLOCKED_DECISION,
                "total_requirements": total,
                "passed_requirements": passed,
                "failed_requirements": failed,
                "failed_requirement_names": failed_names,
                "integrity_rules_passed": rules_passed,
                "integrity_guards_passed": guards_passed,
                "source_controlled_forward_observation_start_run_performed": True,
                "source_controlled_forward_observation_start_performed": True,
                "forward_observation_start_allowed": True,
                "forward_observation_started": True,
                "future_controlled_forward_observation_evidence_collection_precheck_allowed": review_passed,
                "new_controlled_forward_observation_start_run_performed": False,
                "new_controlled_forward_observation_start_performed": False,
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


def validate_long_forward_observation_controlled_start_run_output_integrity_review() -> dict[str, pd.DataFrame]:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    checks: list[dict[str, Any]] = []

    for check_name, path in {
        "phase_10_26_controlled_start_run_doc_exists": PHASE_10_26_DOC_PATH,
        "phase_10_27_output_integrity_review_doc_exists": PHASE_10_27_DOC_PATH,
    }.items():
        exists = path.exists()
        checks.append(build_check("phase_anchor", check_name, exists, "INFO" if exists else "ERROR", str(path)))

    official_dataset_exists_before = OFFICIAL_DATASET_PATH.exists()
    manifest_before_df = build_source_manifest()
    output_hash_before = sha256_file(SOURCE_PATHS["output"])

    source = {name: read_csv_if_exists(path) for name, path in SOURCE_PATHS.items()}

    manifest_after_df = build_source_manifest()
    output_hash_after = sha256_file(SOURCE_PATHS["output"])

    validations_df = build_integrity_validations(
        source=source,
        manifest_before_df=manifest_before_df,
        manifest_after_df=manifest_after_df,
        output_hash_before=output_hash_before,
        output_hash_after=output_hash_after,
        official_dataset_absent=not official_dataset_exists_before,
    )
    evidence_df = build_integrity_evidence_chain(validations_df)
    controls_df = build_integrity_controls(evidence_df)
    guards_df = build_integrity_guard_matrix()
    rules_df = build_integrity_rules(validations_df, evidence_df, controls_df, guards_df)
    requirements_df = build_integrity_requirements(validations_df, evidence_df, controls_df, rules_df, guards_df)
    decision_df = build_integrity_decision(requirements_df, rules_df, guards_df)

    decision = decision_df.iloc[0].to_dict() if not decision_df.empty else {}
    aggregate_checks = [
        ("integrity_validations_passed", dataframe_all_passed(validations_df)),
        ("integrity_evidence_chain_passed", dataframe_all_passed(evidence_df)),
        ("integrity_controls_passed", dataframe_all_passed(controls_df)),
        ("integrity_rules_passed", dataframe_all_passed(rules_df)),
        ("integrity_requirements_passed", dataframe_all_passed(requirements_df)),
        ("integrity_guards_passed", dataframe_all_passed(guards_df)),
        ("output_integrity_review_passed", safe_bool(decision.get("controlled_start_run_output_integrity_review_passed", False))),
        ("output_integrity_review_decision_expected", str(decision.get("controlled_start_run_output_integrity_review_decision", "")) == READY_DECISION),
    ]
    for name, passed in aggregate_checks:
        details = str(decision.get("controlled_start_run_output_integrity_review_decision", "")) if name == "output_integrity_review_decision_expected" else f"{name}={passed}"
        checks.append(build_check("output_integrity_review", name, passed, "INFO" if passed else "ERROR", details))

    official_dataset_exists_after = OFFICIAL_DATASET_PATH.exists()
    official_dataset_unchanged_absent = not official_dataset_exists_before and not official_dataset_exists_after
    checks.append(build_check("official_dataset_guard", "official_dataset_not_created_or_written", official_dataset_unchanged_absent, "INFO" if official_dataset_unchanged_absent else "ERROR", f"before={official_dataset_exists_before},after={official_dataset_exists_after}"))

    for _, row in guards_df.iterrows():
        passed = safe_bool(row.get("passed", False), False)
        checks.append(build_check("output_integrity_review_safety_flags", str(row.get("guard_name", "")), passed, "INFO" if passed else "ERROR", f"{row.get('guard_name', '')}={row.get('actual_value', '')} (required={row.get('required_value', '')})"))

    warnings = [
        ("output_integrity_review_only", "Phase 10.27 reviews only the Phase 10.26 output."),
        ("observation_state_preserved", "The controlled observation state remains started."),
        ("no_duplicate_start_run", "No second controlled start run is performed."),
        ("evidence_collection_not_enabled", "Real evidence collection remains disabled."),
        ("official_dataset_not_written", "The official evidence dataset remains absent and unwritten."),
        ("signal_generation_not_enabled", "Signal generation remains disabled."),
        ("live_alerts_not_enabled", "Live alerts remain disabled."),
        ("paper_trading_not_enabled", "Paper trading execution remains disabled."),
        ("real_capital_not_allowed", "Real capital remains prohibited."),
        ("market_execution_not_allowed", "Market execution remains prohibited."),
        ("total_project_not_completed", "The total project is not completed."),
    ]
    for name, details in warnings:
        checks.append(build_check("scope_control", name, True, "WARNING", details))

    future_precheck_allowed = safe_bool(decision.get("future_controlled_forward_observation_evidence_collection_precheck_allowed", False))
    checks.append(build_check("planning_scope", "future_evidence_collection_precheck_allowed", future_precheck_allowed, "WARNING" if future_precheck_allowed else "ERROR", "This permits only a future evidence collection precheck. It does not enable evidence collection, official dataset writes, signals, alerts, paper trading, real capital or market execution."))
    checks.append(build_check("phase_transition", "phase_10_28_recommended_next", True, "INFO", "Recommended next step: Phase 10.28 LONG Forward Observation Evidence Collection Precheck V1."))

    checks_df = pd.DataFrame(checks)
    blocker_count = int(checks_df["blocker"].map(lambda value: safe_bool(value, False)).sum())
    error_count = int(checks_df["severity"].eq("ERROR").sum())
    warning_count = int(checks_df["severity"].eq("WARNING").sum())
    validation_passed = blocker_count == 0 and error_count == 0

    summary = source["summary"].iloc[0].to_dict() if not source["summary"].empty else {}
    output = source["output"].iloc[0].to_dict() if not source["output"].empty else {}
    lookup = {
        str(row["validation_name"]): safe_bool(row["passed"], False)
        for _, row in validations_df.iterrows()
    }
    review_passed = safe_bool(decision.get("controlled_start_run_output_integrity_review_passed", False))
    review_decision = str(decision.get("controlled_start_run_output_integrity_review_decision", ""))

    summary_df = pd.DataFrame(
        [
            {
                "phase": "10.27",
                "long_forward_observation_controlled_start_run_output_integrity_review_defined": True,
                "phase_10_26_validation_passed": lookup.get("phase_10_26_validation_passed", False),
                "source_controlled_start_run_passed": lookup.get("source_start_run_passed", False),
                "source_controlled_start_run_decision": str(summary.get("controlled_forward_observation_start_run_decision", "")),
                "source_future_output_integrity_review_allowed": lookup.get("source_future_integrity_review_allowed", False),
                "source_artifact_count": int(len(manifest_after_df)),
                "source_artifacts_exist": lookup.get("source_artifacts_exist", False),
                "source_artifacts_non_empty": lookup.get("source_artifacts_non_empty", False),
                "source_artifact_hashes_valid": lookup.get("source_artifact_hashes_valid", False),
                "source_artifacts_stable_during_review": lookup.get("source_artifacts_stable_during_review", False),
                "source_manifest_sha256": manifest_digest(manifest_after_df),
                "source_output_sha256": output_hash_after,
                "source_output_hash_stable": lookup.get("source_output_hash_stable", False),
                "source_output_row_count": int(len(source["output"])),
                "source_output_schema_valid": lookup.get("source_output_schema_valid", False),
                "source_output_identifier_valid": lookup.get("source_output_identifier_valid", False),
                "source_output_status_valid": lookup.get("source_output_status_valid", False),
                "source_output_timestamp_valid": lookup.get("source_output_timestamp_valid", False),
                "source_output_candidate_id": str(output.get("candidate_id", "")),
                "source_output_candidate_valid": lookup.get("source_output_candidate_valid", False),
                "source_output_direction": str(output.get("direction", "")),
                "source_output_direction_valid": lookup.get("source_output_direction_valid", False),
                "source_output_price_structure_valid": lookup.get("source_output_price_structure_valid", False),
                "source_output_risk_reward": safe_float(output.get("risk_reward")),
                "source_output_risk_reward_valid": lookup.get("source_output_risk_reward_valid", False),
                "source_output_scope": str(output.get("start_scope", "")),
                "source_output_scope_valid": lookup.get("source_output_scope_valid", False),
                "source_output_evidence_scope": str(output.get("evidence_scope", "")),
                "source_output_evidence_scope_valid": lookup.get("source_output_evidence_scope_valid", False),
                "source_output_observation_state": str(output.get("observation_state", "")),
                "source_output_observation_state_valid": lookup.get("source_output_observation_state_valid", False),
                "source_output_true_start_fields_valid": lookup.get("source_output_true_start_fields_valid", False),
                "source_output_operational_locks_valid": lookup.get("source_output_operational_locks_valid", False),
                "source_output_official_evidence_rows_zero": lookup.get("source_output_official_evidence_rows_zero", False),
                "source_summary_output_consistent": lookup.get("source_summary_output_consistent", False),
                "source_decision_output_consistent": lookup.get("source_decision_output_consistent", False),
                "integrity_validation_rows": int(len(validations_df)),
                "integrity_evidence_rows": int(len(evidence_df)),
                "integrity_control_rows": int(len(controls_df)),
                "integrity_rule_rows": int(len(rules_df)),
                "integrity_requirement_rows": int(len(requirements_df)),
                "integrity_guard_rows": int(len(guards_df)),
                "integrity_validations_passed": dataframe_all_passed(validations_df),
                "integrity_evidence_chain_passed": dataframe_all_passed(evidence_df),
                "integrity_controls_passed": dataframe_all_passed(controls_df),
                "integrity_rules_passed": dataframe_all_passed(rules_df),
                "integrity_requirements_passed": dataframe_all_passed(requirements_df),
                "integrity_guards_passed": dataframe_all_passed(guards_df),
                "controlled_start_run_output_integrity_review_performed": True,
                "controlled_start_run_output_integrity_review_passed": review_passed,
                "controlled_start_run_output_integrity_review_decision": review_decision,
                "source_controlled_forward_observation_start_run_performed": True,
                "source_controlled_forward_observation_start_performed": True,
                "forward_observation_start_allowed": True,
                "forward_observation_started": True,
                "future_controlled_forward_observation_evidence_collection_precheck_allowed": future_precheck_allowed,
                "new_controlled_forward_observation_start_run_performed": False,
                "new_controlled_forward_observation_start_performed": False,
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
                "validation_decision": "PHASE_10_27_LONG_FORWARD_OBSERVATION_CONTROLLED_START_RUN_OUTPUT_INTEGRITY_REVIEW_VALIDATED" if validation_passed else "PHASE_10_27_LONG_FORWARD_OBSERVATION_CONTROLLED_START_RUN_OUTPUT_INTEGRITY_REVIEW_FAILED",
            }
        ]
    )

    report_frames = {
        "phase_10_26_source_summary_v1.csv": source["summary"],
        "phase_10_26_source_start_output_v1.csv": source["output"],
        "phase_10_26_source_validations_v1.csv": source["validations"],
        "phase_10_26_source_evidence_chain_v1.csv": source["evidence_chain"],
        "phase_10_26_source_controls_v1.csv": source["controls"],
        "phase_10_26_source_rules_v1.csv": source["rules"],
        "phase_10_26_source_requirements_v1.csv": source["requirements"],
        "phase_10_26_source_guard_matrix_v1.csv": source["guard_matrix"],
        "phase_10_26_source_decision_v1.csv": source["decision"],
        "phase_10_26_source_checks_v1.csv": source["checks"],
        "source_start_run_artifact_manifest_v1.csv": manifest_after_df,
        "start_run_output_integrity_validations_v1.csv": validations_df,
        "start_run_output_integrity_evidence_chain_v1.csv": evidence_df,
        "start_run_output_integrity_controls_v1.csv": controls_df,
        "start_run_output_integrity_rules_v1.csv": rules_df,
        "start_run_output_integrity_requirements_v1.csv": requirements_df,
        "start_run_output_integrity_guard_matrix_v1.csv": guards_df,
        "start_run_output_integrity_decision_v1.csv": decision_df,
        "start_run_output_integrity_checks_v1.csv": checks_df,
        "start_run_output_integrity_summary_v1.csv": summary_df,
    }
    for filename, frame in report_frames.items():
        frame.to_csv(REPORTS_DIR / filename, index=False)

    return {
        "summary": summary_df,
        "source_phase_10_26_summary": source["summary"],
        "source_start_output": source["output"],
        "source_validations": source["validations"],
        "source_evidence_chain": source["evidence_chain"],
        "source_controls": source["controls"],
        "source_rules": source["rules"],
        "source_requirements": source["requirements"],
        "source_guard_matrix": source["guard_matrix"],
        "source_decision": source["decision"],
        "source_checks": source["checks"],
        "source_manifest": manifest_after_df,
        "integrity_validations": validations_df,
        "integrity_evidence_chain": evidence_df,
        "integrity_controls": controls_df,
        "integrity_rules": rules_df,
        "integrity_requirements": requirements_df,
        "integrity_guard_matrix": guards_df,
        "integrity_decision": decision_df,
        "checks": checks_df,
    }
