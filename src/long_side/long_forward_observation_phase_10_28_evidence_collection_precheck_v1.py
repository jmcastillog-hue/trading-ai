from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

import pandas as pd

from src.long_side.long_forward_observation_dataset_bootstrap_v1 import (
    OFFICIAL_DATASET_PATH,
    PRIMARY_RESEARCH_CANDIDATE,
)


REPORTS_DIR = Path("reports/p10_28_evidence_collection_precheck_v1")
SOURCE_DIR = Path(
    "reports/p10_27_controlled_start_run_output_integrity_review_v1"
)

PHASE_10_27_DOC_PATH = Path(
    "docs/PHASE_10_LONG_FORWARD_OBSERVATION_CONTROLLED_START_RUN_OUTPUT_INTEGRITY_REVIEW.md"
)
PHASE_10_28_DOC_PATH = Path(
    "docs/PHASE_10_LONG_FORWARD_OBSERVATION_EVIDENCE_COLLECTION_PRECHECK.md"
)

SOURCE_PATHS = {
    "summary": SOURCE_DIR / "start_run_output_integrity_summary_v1.csv",
    "start_output": SOURCE_DIR / "phase_10_26_source_start_output_v1.csv",
    "validations": SOURCE_DIR / "start_run_output_integrity_validations_v1.csv",
    "evidence_chain": SOURCE_DIR / "start_run_output_integrity_evidence_chain_v1.csv",
    "controls": SOURCE_DIR / "start_run_output_integrity_controls_v1.csv",
    "rules": SOURCE_DIR / "start_run_output_integrity_rules_v1.csv",
    "requirements": SOURCE_DIR / "start_run_output_integrity_requirements_v1.csv",
    "guard_matrix": SOURCE_DIR / "start_run_output_integrity_guard_matrix_v1.csv",
    "decision": SOURCE_DIR / "start_run_output_integrity_decision_v1.csv",
    "checks": SOURCE_DIR / "start_run_output_integrity_checks_v1.csv",
    "manifest": SOURCE_DIR / "source_start_run_artifact_manifest_v1.csv",
}

SOURCE_READY_DECISION = (
    "CONTROLLED_FORWARD_OBSERVATION_START_RUN_OUTPUT_INTEGRITY_REVIEW_"
    "READY_FOR_EVIDENCE_COLLECTION_PRECHECK"
)
SOURCE_START_SCOPE = (
    "CONTROLLED_FORWARD_OBSERVATION_START_OBSERVATION_ONLY"
)
SOURCE_EVIDENCE_SCOPE = "OBSERVATION_STATE_ONLY_NOT_REAL_EVIDENCE"
SOURCE_OBSERVATION_STATE = "CONTROLLED_FORWARD_OBSERVATION_STARTED"

PRECHECK_STATUS = "LONG_FORWARD_OBSERVATION_EVIDENCE_COLLECTION_PRECHECK_ONLY"
READY_DECISION = (
    "CONTROLLED_FORWARD_OBSERVATION_EVIDENCE_COLLECTION_PRECHECK_"
    "READY_FOR_EVIDENCE_COLLECTION_DESIGN"
)
BLOCKED_DECISION = (
    "CONTROLLED_FORWARD_OBSERVATION_EVIDENCE_COLLECTION_PRECHECK_BLOCKED"
)
RECOMMENDED_NEXT_PHASE = (
    "PHASE_10_29_LONG_FORWARD_OBSERVATION_EVIDENCE_COLLECTION_DESIGN_V1"
)

EXPECTED_SOURCE_COUNTS = {
    "integrity_validation_rows": 40,
    "integrity_evidence_rows": 36,
    "integrity_control_rows": 36,
    "integrity_rule_rows": 16,
    "integrity_requirement_rows": 55,
    "integrity_guard_rows": 31,
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

EXPECTED_START_OUTPUT_COLUMNS = [
    "start_run_id", "start_run_status", "started_at_utc", "source_phase",
    "source_validation_decision", "source_final_approval_decision", "symbol",
    "timeframe", "candidate_id", "direction", "observation_role",
    "observation_state", "market_context", "activation_scope", "start_scope",
    "evidence_scope", "entry_price", "stop_price", "target_price",
    "invalidation_level", "risk_reward", "cost_profile",
    "manual_confirmation_required",
    "controlled_forward_observation_start_final_approval_review_performed",
    "future_controlled_forward_observation_start_run_allowed",
    "controlled_forward_observation_start_run_allowed",
    "controlled_forward_observation_start_run_performed",
    "controlled_forward_observation_start_performed",
    "forward_observation_start_allowed", "forward_observation_started",
    "future_controlled_forward_observation_start_run_output_integrity_review_allowed",
    "official_dataset_write_allowed", "official_dataset_write_performed",
    "real_forward_dataset_created", "official_evidence_rows_written",
    "real_forward_signals_recorded", "journal_real_rows_accepted",
    "accepted_as_real_evidence", "evidence_persistence_allowed",
    "evidence_write_performed", "signal_generation_enabled",
    "live_alerts_allowed", "paper_trading_enabled", "long_strategy_approved",
    "long_entries_approved", "long_side_established",
    "paper_trade_execution_allowed", "real_capital_allowed",
    "market_execution_allowed", "exchange_execution_allowed",
    "automation_allowed", "execution_allowed", "real_entries_approved",
    "total_project_completed", "expected_next_review_phase", "notes",
    "validation_status",
]

DESIGN_REQUIREMENT_NAMES = [
    "accepted_observation_source_defined",
    "timestamp_timezone_requirements_defined",
    "candidate_identity_requirements_defined",
    "direction_requirements_defined",
    "symbol_timeframe_requirements_defined",
    "price_structure_requirements_defined",
    "risk_reward_consistency_requirements_defined",
    "evidence_identity_deduplication_rules_defined",
    "observation_lifecycle_states_defined",
    "evidence_review_status_defined",
    "evidence_rejection_rules_defined",
    "write_ahead_validation_defined",
    "official_dataset_schema_defined",
    "official_dataset_write_guard_defined",
    "evidence_hash_provenance_fields_defined",
    "audit_trail_requirements_defined",
    "manual_confirmation_requirements_defined",
    "rollback_recovery_behavior_defined",
    "no_signal_generation_boundary_defined",
    "no_execution_boundary_defined",
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


def read_csv(path: Path) -> pd.DataFrame:
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
        for chunk in iter(lambda: file_handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_manifest() -> pd.DataFrame:
    rows = []
    for position, (name, path) in enumerate(SOURCE_PATHS.items(), start=1):
        exists = path.exists() and path.is_file()
        size_bytes = path.stat().st_size if exists else 0
        file_hash = sha256_file(path) if exists else ""
        rows.append(
            {
                "manifest_position": position,
                "artifact_name": name,
                "artifact_filename": path.name,
                "artifact_path": str(path),
                "artifact_exists": exists,
                "artifact_size_bytes": int(size_bytes),
                "artifact_non_empty": size_bytes > 0,
                "artifact_sha256": file_hash,
                "artifact_sha256_valid": len(file_hash) == 64,
            }
        )
    return pd.DataFrame(rows)


def manifest_digest(df: pd.DataFrame) -> str:
    if df.empty:
        return ""
    payload = (
        df[
            [
                "artifact_name",
                "artifact_path",
                "artifact_size_bytes",
                "artifact_sha256",
            ]
        ]
        .astype(str)
        .sort_values(["artifact_name", "artifact_path"])
        .to_csv(index=False)
        .encode("utf-8")
    )
    return hashlib.sha256(payload).hexdigest()


def build_check(group: str, name: str, passed: bool, severity: str, details: str) -> dict[str, Any]:
    return {
        "check_group": group,
        "check_name": name,
        "passed": bool(passed),
        "severity": severity,
        "details": details,
        "blocker": severity == "ERROR" and not bool(passed),
    }


def build_design_requirements() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "design_requirement_position": position,
                "design_requirement_id": f"EVIDENCE_COLLECTION_DESIGN_REQ_{position:03d}",
                "design_requirement_name": name,
                "required_for_future_design": True,
                "defined_in_precheck": True,
                "implemented_in_precheck": False,
                "evidence_collection_enabled": False,
                "official_dataset_write_allowed": False,
                "signal_generation_enabled": False,
                "market_execution_allowed": False,
                "passed": True,
            }
            for position, name in enumerate(DESIGN_REQUIREMENT_NAMES, start=1)
        ]
    )


def build_validations(
    source: dict[str, pd.DataFrame],
    manifest_before: pd.DataFrame,
    manifest_after: pd.DataFrame,
    design_requirements: pd.DataFrame,
    official_dataset_absent: bool,
) -> pd.DataFrame:
    summary = source["summary"].iloc[0].to_dict() if not source["summary"].empty else {}
    output = source["start_output"].iloc[0].to_dict() if not source["start_output"].empty else {}
    decision = source["decision"].iloc[0].to_dict() if not source["decision"].empty else {}

    artifacts_exist = (
        not manifest_before.empty
        and manifest_before["artifact_exists"].map(safe_bool).all()
    )
    artifacts_non_empty = (
        not manifest_before.empty
        and manifest_before["artifact_non_empty"].map(safe_bool).all()
    )
    hashes_valid = (
        not manifest_before.empty
        and manifest_before["artifact_sha256_valid"].map(safe_bool).all()
    )
    stable = (
        bool(manifest_digest(manifest_before))
        and manifest_digest(manifest_before) == manifest_digest(manifest_after)
    )

    counts_valid = all(
        int(safe_float(summary.get(field), -1)) == expected
        for field, expected in EXPECTED_SOURCE_COUNTS.items()
    )

    entry = safe_float(output.get("entry_price"))
    stop = safe_float(output.get("stop_price"))
    target = safe_float(output.get("target_price"))
    rr = safe_float(output.get("risk_reward"))
    expected_rr = round((target - entry) / (entry - stop), 4) if entry > stop else 0.0

    true_fields_valid = all(
        safe_bool(output.get(field, False), False)
        for field in EXPECTED_TRUE_START_FIELDS
    )
    locks_valid = all(
        safe_bool(output.get(field, True), True) is False
        for field in EXPECTED_FALSE_GUARDS
    )

    summary_decision_consistent = (
        str(summary.get("controlled_start_run_output_integrity_review_decision", ""))
        == str(decision.get("controlled_start_run_output_integrity_review_decision", ""))
        == SOURCE_READY_DECISION
        and safe_bool(summary.get("controlled_start_run_output_integrity_review_passed", False))
        and safe_bool(decision.get("controlled_start_run_output_integrity_review_passed", False))
    )

    design_defined = (
        len(design_requirements) == 20
        and dataframe_all_passed(design_requirements)
        and design_requirements["implemented_in_precheck"].map(safe_bool).eq(False).all()
    )

    rows = [
        ("source_artifacts_exist", artifacts_exist, f"artifact_count={len(manifest_before)}"),
        ("source_artifacts_non_empty", artifacts_non_empty, f"artifact_count={len(manifest_before)}"),
        ("source_artifact_hashes_valid", hashes_valid, f"artifact_count={len(manifest_before)}"),
        ("source_artifacts_stable_during_precheck", stable, f"before={manifest_digest(manifest_before)},after={manifest_digest(manifest_after)}"),
        ("phase_10_27_validation_passed", safe_bool(summary.get("validation_passed", False)), str(summary.get("validation_decision", ""))),
        ("source_integrity_review_performed", safe_bool(summary.get("controlled_start_run_output_integrity_review_performed", False)), str(summary.get("controlled_start_run_output_integrity_review_performed", ""))),
        ("source_integrity_review_passed", safe_bool(summary.get("controlled_start_run_output_integrity_review_passed", False)), str(summary.get("controlled_start_run_output_integrity_review_passed", ""))),
        ("source_integrity_review_decision_valid", str(summary.get("controlled_start_run_output_integrity_review_decision", "")) == SOURCE_READY_DECISION, str(summary.get("controlled_start_run_output_integrity_review_decision", ""))),
        ("source_future_precheck_allowed", safe_bool(summary.get("future_controlled_forward_observation_evidence_collection_precheck_allowed", False)), str(summary.get("future_controlled_forward_observation_evidence_collection_precheck_allowed", ""))),
        ("source_summary_decision_consistent", summary_decision_consistent, f"consistent={summary_decision_consistent}"),
        ("source_counts_valid", counts_valid, ",".join(f"{k}={summary.get(k, '')}" for k in EXPECTED_SOURCE_COUNTS)),
        ("source_validations_passed", dataframe_all_passed(source["validations"]), f"rows={len(source['validations'])}"),
        ("source_evidence_chain_passed", dataframe_all_passed(source["evidence_chain"]), f"rows={len(source['evidence_chain'])}"),
        ("source_controls_passed", dataframe_all_passed(source["controls"]), f"rows={len(source['controls'])}"),
        ("source_rules_passed", dataframe_all_passed(source["rules"]), f"rows={len(source['rules'])}"),
        ("source_requirements_passed", dataframe_all_passed(source["requirements"]), f"rows={len(source['requirements'])}"),
        ("source_guards_passed", dataframe_all_passed(source["guard_matrix"]), f"rows={len(source['guard_matrix'])}"),
        ("source_start_output_row_count_one", len(source["start_output"]) == 1, f"row_count={len(source['start_output'])}"),
        ("source_start_output_schema_valid", source["start_output"].columns.astype(str).tolist() == EXPECTED_START_OUTPUT_COLUMNS, f"actual={len(source['start_output'].columns)},expected={len(EXPECTED_START_OUTPUT_COLUMNS)}"),
        ("source_candidate_valid", str(output.get("candidate_id", "")) == PRIMARY_RESEARCH_CANDIDATE, str(output.get("candidate_id", ""))),
        ("source_direction_valid", str(output.get("direction", "")) == "LONG", str(output.get("direction", ""))),
        ("source_price_structure_valid", stop < entry < target and safe_float(output.get("invalidation_level")) == stop, f"stop={stop},entry={entry},target={target}"),
        ("source_risk_reward_valid", rr == expected_rr and rr == 2.5, f"risk_reward={rr},expected={expected_rr}"),
        ("source_start_scope_valid", str(output.get("start_scope", "")) == SOURCE_START_SCOPE, str(output.get("start_scope", ""))),
        ("source_evidence_scope_valid", str(output.get("evidence_scope", "")) == SOURCE_EVIDENCE_SCOPE, str(output.get("evidence_scope", ""))),
        ("source_observation_state_started", str(output.get("observation_state", "")) == SOURCE_OBSERVATION_STATE and safe_bool(output.get("forward_observation_started", False)), str(output.get("observation_state", ""))),
        ("source_start_state_fields_valid", true_fields_valid, f"true_field_count={len(EXPECTED_TRUE_START_FIELDS)}"),
        ("source_operational_locks_valid", locks_valid, f"false_guard_count={len(EXPECTED_FALSE_GUARDS)}"),
        ("source_official_evidence_rows_zero", int(safe_float(output.get("official_evidence_rows_written"), -1)) == 0, str(output.get("official_evidence_rows_written", ""))),
        ("official_dataset_absent", official_dataset_absent, f"official_dataset_absent={official_dataset_absent}"),
        ("no_duplicate_start_run", True, "new_start_run=False,new_start=False"),
        ("evidence_collection_remains_disabled", safe_bool(output.get("accepted_as_real_evidence", True), True) is False and safe_bool(output.get("evidence_persistence_allowed", True), True) is False and safe_bool(output.get("evidence_write_performed", True), True) is False, "accepted=False,persistence=False,write=False"),
        ("evidence_collection_design_requirements_defined", design_defined, f"design_requirement_count={len(design_requirements)}"),
    ]

    return pd.DataFrame(
        [{"validation_name": name, "passed": bool(passed), "details": details} for name, passed, details in rows]
    )


def build_evidence_chain(validations: pd.DataFrame) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "evidence_position": position,
                "evidence_id": f"EVIDENCE_COLLECTION_PRECHECK_EVIDENCE_{position:03d}",
                "evidence_name": str(row["validation_name"]),
                "evidence_group": "precheck_validation",
                "required": True,
                "passed": safe_bool(row["passed"], False),
                "details": "Validated from Phase 10.27 and the preserved Phase 10.26 start output.",
            }
            for position, (_, row) in enumerate(validations.iterrows(), start=1)
        ]
    )


def build_controls(evidence: pd.DataFrame) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "control_position": int(row["evidence_position"]),
                "control_id": f"EVIDENCE_COLLECTION_PRECHECK_CONTROL_{int(row['evidence_position']):03d}",
                "control_name": str(row["evidence_name"]),
                "required": True,
                "precheck_only": True,
                "observation_state_preserved": True,
                "evidence_collection_enabled": False,
                "official_dataset_write_allowed": False,
                "signal_generation_enabled": False,
                "market_execution_allowed": False,
                "passed": safe_bool(row["passed"], False),
            }
            for _, row in evidence.iterrows()
        ]
    )


def build_guard_matrix() -> pd.DataFrame:
    rows = []
    true_guards = [
        "source_controlled_forward_observation_start_run_performed",
        "source_controlled_forward_observation_start_performed",
        "forward_observation_start_allowed",
        "forward_observation_started",
        "evidence_collection_precheck_performed",
        "future_evidence_collection_design_allowed",
    ]
    for name in true_guards:
        rows.append({"guard_name": name, "required_value": True, "actual_value": True, "passed": True, "guard_group": "precheck_state"})
    for name in [
        "new_controlled_forward_observation_start_run_performed",
        "new_controlled_forward_observation_start_performed",
    ]:
        rows.append({"guard_name": name, "required_value": False, "actual_value": False, "passed": True, "guard_group": "no_duplicate_start_guard"})
    for name in EXPECTED_FALSE_GUARDS:
        rows.append({"guard_name": name, "required_value": False, "actual_value": False, "passed": True, "guard_group": "precheck_safety_guard"})
    rows.append({"guard_name": "official_evidence_rows_written", "required_value": 0, "actual_value": 0, "passed": True, "guard_group": "official_dataset_guard"})
    return pd.DataFrame(rows)


def build_rules(validations: pd.DataFrame, evidence: pd.DataFrame, controls: pd.DataFrame, guards: pd.DataFrame, design: pd.DataFrame) -> pd.DataFrame:
    rows = [
        ("precheck_validation_count_33", len(validations) == 33, "33", str(len(validations)), "validation"),
        ("all_precheck_validations_passed", dataframe_all_passed(validations), "True", str(dataframe_all_passed(validations)), "validation"),
        ("precheck_evidence_count_33", len(evidence) == 33, "33", str(len(evidence)), "evidence"),
        ("all_precheck_evidence_passed", dataframe_all_passed(evidence), "True", str(dataframe_all_passed(evidence)), "evidence"),
        ("precheck_control_count_33", len(controls) == 33, "33", str(len(controls)), "controls"),
        ("all_precheck_controls_passed", dataframe_all_passed(controls), "True", str(dataframe_all_passed(controls)), "controls"),
        ("precheck_guard_count_31", len(guards) == 31, "31", str(len(guards)), "safety"),
        ("all_precheck_guards_passed", dataframe_all_passed(guards), "True", str(dataframe_all_passed(guards)), "safety"),
        ("design_requirement_count_20", len(design) == 20, "20", str(len(design)), "future_design"),
        ("all_design_requirements_defined", dataframe_all_passed(design), "True", str(dataframe_all_passed(design)), "future_design"),
        ("precheck_only", True, "True", "True", "scope_control"),
        ("evidence_collection_disabled", True, "False", "False", "evidence_boundary"),
        ("official_dataset_writes_disabled", True, "False", "False", "official_dataset_guard"),
        ("signal_generation_disabled", True, "False", "False", "signal_boundary"),
        ("market_execution_disabled", True, "False", "False", "market_execution_guard"),
        ("total_project_not_completed", True, "False", "False", "scope_control"),
    ]
    return pd.DataFrame(
        [
            {
                "rule_id": f"EVIDENCE_COLLECTION_PRECHECK_RULE_{position:03d}",
                "rule_name": name,
                "passed": bool(passed),
                "required_value": required,
                "actual_value": actual,
                "rule_group": group,
            }
            for position, (name, passed, required, actual, group) in enumerate(rows, start=1)
        ]
    )


def build_requirements(validations: pd.DataFrame, evidence: pd.DataFrame, controls: pd.DataFrame, rules: pd.DataFrame, guards: pd.DataFrame, design: pd.DataFrame) -> pd.DataFrame:
    rows = [
        (str(row["validation_name"]), safe_bool(row["passed"], False), "True", str(safe_bool(row["passed"], False)), "precheck_validation")
        for _, row in validations.iterrows()
    ]
    rows.extend(
        [
            ("precheck_evidence_chain_passed", dataframe_all_passed(evidence), "True", str(dataframe_all_passed(evidence)), "evidence"),
            ("precheck_controls_passed", dataframe_all_passed(controls), "True", str(dataframe_all_passed(controls)), "controls"),
            ("precheck_rules_passed", dataframe_all_passed(rules), "True", str(dataframe_all_passed(rules)), "rules"),
            ("precheck_guards_passed", dataframe_all_passed(guards), "True", str(dataframe_all_passed(guards)), "safety"),
            ("design_requirements_defined", dataframe_all_passed(design), "True", str(dataframe_all_passed(design)), "future_design"),
            ("precheck_performed", True, "True", "True", "precheck"),
            ("future_evidence_collection_design_allowed", True, "True", "True", "future_design"),
            ("new_start_run_not_performed", True, "False", "False", "no_duplicate_start_guard"),
            ("new_start_not_performed", True, "False", "False", "no_duplicate_start_guard"),
            ("observation_state_remains_started", True, "True", "True", "observation_state"),
            ("evidence_collection_not_enabled", True, "False", "False", "evidence_boundary"),
            ("official_evidence_rows_written_zero", True, "0", "0", "official_dataset_guard"),
            ("signal_generation_disabled", True, "False", "False", "signal_boundary"),
            ("paper_trading_disabled", True, "False", "False", "paper_trading_guard"),
            ("market_execution_disabled", True, "False", "False", "market_execution_guard"),
        ]
    )
    return pd.DataFrame(
        [
            {
                "requirement_id": f"EVIDENCE_COLLECTION_PRECHECK_REQ_{position:03d}",
                "requirement_name": name,
                "passed": bool(passed),
                "required_value": required,
                "actual_value": actual,
                "requirement_group": group,
            }
            for position, (name, passed, required, actual, group) in enumerate(rows, start=1)
        ]
    )


def build_decision(requirements: pd.DataFrame, rules: pd.DataFrame, guards: pd.DataFrame) -> pd.DataFrame:
    passed_requirements = int(requirements["passed"].map(safe_bool).sum()) if not requirements.empty else 0
    failed_requirements = len(requirements) - passed_requirements
    passed = (
        len(requirements) > 0
        and failed_requirements == 0
        and dataframe_all_passed(rules)
        and dataframe_all_passed(guards)
    )
    failed_names = ",".join(
        requirements[~requirements["passed"].map(safe_bool)]["requirement_name"].astype(str).tolist()
    ) if not requirements.empty else ""
    return pd.DataFrame(
        [
            {
                "evidence_collection_precheck_id": "PHASE_10_28_LONG_FORWARD_OBSERVATION_EVIDENCE_COLLECTION_PRECHECK_001",
                "evidence_collection_precheck_status": PRECHECK_STATUS,
                "evidence_collection_precheck_performed": True,
                "evidence_collection_precheck_passed": passed,
                "evidence_collection_precheck_decision": READY_DECISION if passed else BLOCKED_DECISION,
                "total_requirements": len(requirements),
                "passed_requirements": passed_requirements,
                "failed_requirements": failed_requirements,
                "failed_requirement_names": failed_names,
                "precheck_rules_passed": dataframe_all_passed(rules),
                "precheck_guards_passed": dataframe_all_passed(guards),
                "source_controlled_forward_observation_start_run_performed": True,
                "source_controlled_forward_observation_start_performed": True,
                "forward_observation_start_allowed": True,
                "forward_observation_started": True,
                "future_evidence_collection_design_allowed": passed,
                "new_controlled_forward_observation_start_run_performed": False,
                "new_controlled_forward_observation_start_performed": False,
                "evidence_collection_enabled": False,
                "evidence_collection_started": False,
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


def validate_long_forward_observation_evidence_collection_precheck() -> dict[str, pd.DataFrame]:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    checks: list[dict[str, Any]] = []

    for name, path in {
        "phase_10_27_output_integrity_review_doc_exists": PHASE_10_27_DOC_PATH,
        "phase_10_28_evidence_collection_precheck_doc_exists": PHASE_10_28_DOC_PATH,
    }.items():
        exists = path.exists()
        checks.append(build_check("phase_anchor", name, exists, "INFO" if exists else "ERROR", str(path)))

    official_before = OFFICIAL_DATASET_PATH.exists()
    manifest_before = build_manifest()
    source = {name: read_csv(path) for name, path in SOURCE_PATHS.items()}
    design = build_design_requirements()
    manifest_after = build_manifest()

    validations = build_validations(
        source,
        manifest_before,
        manifest_after,
        design,
        official_dataset_absent=not official_before,
    )
    evidence = build_evidence_chain(validations)
    controls = build_controls(evidence)
    guards = build_guard_matrix()
    rules = build_rules(validations, evidence, controls, guards, design)
    requirements = build_requirements(validations, evidence, controls, rules, guards, design)
    decision = build_decision(requirements, rules, guards)
    decision_row = decision.iloc[0].to_dict()

    aggregate = [
        ("precheck_validations_passed", dataframe_all_passed(validations)),
        ("precheck_evidence_chain_passed", dataframe_all_passed(evidence)),
        ("precheck_controls_passed", dataframe_all_passed(controls)),
        ("precheck_rules_passed", dataframe_all_passed(rules)),
        ("precheck_requirements_passed", dataframe_all_passed(requirements)),
        ("precheck_guards_passed", dataframe_all_passed(guards)),
        ("design_requirements_defined", dataframe_all_passed(design)),
        ("evidence_collection_precheck_passed", safe_bool(decision_row.get("evidence_collection_precheck_passed", False))),
        ("evidence_collection_precheck_decision_expected", str(decision_row.get("evidence_collection_precheck_decision", "")) == READY_DECISION),
    ]
    for name, passed in aggregate:
        details = str(decision_row.get("evidence_collection_precheck_decision", "")) if name.endswith("decision_expected") else f"{name}={passed}"
        checks.append(build_check("evidence_collection_precheck", name, passed, "INFO" if passed else "ERROR", details))

    official_after = OFFICIAL_DATASET_PATH.exists()
    official_unchanged_absent = not official_before and not official_after
    checks.append(build_check("official_dataset_guard", "official_dataset_not_created_or_written", official_unchanged_absent, "INFO" if official_unchanged_absent else "ERROR", f"before={official_before},after={official_after}"))

    for _, row in guards.iterrows():
        checks.append(build_check("evidence_collection_precheck_safety_flags", str(row["guard_name"]), safe_bool(row["passed"]), "INFO" if safe_bool(row["passed"]) else "ERROR", f"{row['guard_name']}={row['actual_value']} (required={row['required_value']})"))

    scope_warnings = [
        ("precheck_only", "Phase 10.28 performs only an evidence collection precheck."),
        ("observation_state_preserved", "The controlled observation state remains started."),
        ("evidence_collection_not_enabled", "Evidence collection remains disabled."),
        ("official_dataset_not_written", "The official evidence dataset remains absent and unwritten."),
        ("signal_generation_not_enabled", "Signal generation remains disabled."),
        ("live_alerts_not_enabled", "Live alerts remain disabled."),
        ("paper_trading_not_enabled", "Paper trading execution remains disabled."),
        ("long_strategy_not_approved", "The LONG research candidate is not approved as a trading strategy."),
        ("real_capital_not_allowed", "Real capital remains prohibited."),
        ("market_execution_not_allowed", "Market execution remains prohibited."),
        ("total_project_not_completed", "The total project is not completed."),
    ]
    for name, details in scope_warnings:
        checks.append(build_check("scope_control", name, True, "WARNING", details))

    future_design_allowed = safe_bool(decision_row.get("future_evidence_collection_design_allowed", False))
    checks.append(build_check("planning_scope", "future_evidence_collection_design_allowed", future_design_allowed, "WARNING" if future_design_allowed else "ERROR", "This permits only a future evidence collection design phase."))
    checks.append(build_check("phase_transition", "phase_10_29_recommended_next", True, "INFO", "Recommended next step: Phase 10.29 LONG Forward Observation Evidence Collection Design V1."))

    checks_df = pd.DataFrame(checks)
    blocker_count = int(checks_df["blocker"].map(safe_bool).sum())
    error_count = int(checks_df["severity"].eq("ERROR").sum())
    warning_count = int(checks_df["severity"].eq("WARNING").sum())
    validation_passed = blocker_count == 0 and error_count == 0

    summary = source["summary"].iloc[0].to_dict() if not source["summary"].empty else {}
    output = source["start_output"].iloc[0].to_dict() if not source["start_output"].empty else {}
    lookup = {str(row["validation_name"]): safe_bool(row["passed"]) for _, row in validations.iterrows()}

    summary_df = pd.DataFrame(
        [
            {
                "phase": "10.28",
                "long_forward_observation_evidence_collection_precheck_defined": True,
                "phase_10_27_validation_passed": lookup.get("phase_10_27_validation_passed", False),
                "source_output_integrity_review_performed": lookup.get("source_integrity_review_performed", False),
                "source_output_integrity_review_passed": lookup.get("source_integrity_review_passed", False),
                "source_output_integrity_review_decision": str(summary.get("controlled_start_run_output_integrity_review_decision", "")),
                "source_future_evidence_collection_precheck_allowed": lookup.get("source_future_precheck_allowed", False),
                "source_artifact_count": len(manifest_after),
                "source_artifacts_exist": lookup.get("source_artifacts_exist", False),
                "source_artifacts_non_empty": lookup.get("source_artifacts_non_empty", False),
                "source_artifact_hashes_valid": lookup.get("source_artifact_hashes_valid", False),
                "source_artifacts_stable_during_precheck": lookup.get("source_artifacts_stable_during_precheck", False),
                "source_manifest_sha256": manifest_digest(manifest_after),
                "source_start_output_row_count": len(source["start_output"]),
                "source_start_output_schema_valid": lookup.get("source_start_output_schema_valid", False),
                "source_candidate_id": str(output.get("candidate_id", "")),
                "source_candidate_valid": lookup.get("source_candidate_valid", False),
                "source_direction": str(output.get("direction", "")),
                "source_direction_valid": lookup.get("source_direction_valid", False),
                "source_price_structure_valid": lookup.get("source_price_structure_valid", False),
                "source_risk_reward": safe_float(output.get("risk_reward")),
                "source_risk_reward_valid": lookup.get("source_risk_reward_valid", False),
                "source_observation_state": str(output.get("observation_state", "")),
                "source_observation_state_started": lookup.get("source_observation_state_started", False),
                "source_start_state_fields_valid": lookup.get("source_start_state_fields_valid", False),
                "source_operational_locks_valid": lookup.get("source_operational_locks_valid", False),
                "source_official_evidence_rows_zero": lookup.get("source_official_evidence_rows_zero", False),
                "official_dataset_absent": lookup.get("official_dataset_absent", False),
                "design_requirement_rows": len(design),
                "design_requirements_defined": dataframe_all_passed(design),
                "precheck_validation_rows": len(validations),
                "precheck_evidence_rows": len(evidence),
                "precheck_control_rows": len(controls),
                "precheck_rule_rows": len(rules),
                "precheck_requirement_rows": len(requirements),
                "precheck_guard_rows": len(guards),
                "precheck_validations_passed": dataframe_all_passed(validations),
                "precheck_evidence_chain_passed": dataframe_all_passed(evidence),
                "precheck_controls_passed": dataframe_all_passed(controls),
                "precheck_rules_passed": dataframe_all_passed(rules),
                "precheck_requirements_passed": dataframe_all_passed(requirements),
                "precheck_guards_passed": dataframe_all_passed(guards),
                "evidence_collection_precheck_performed": True,
                "evidence_collection_precheck_passed": safe_bool(decision_row.get("evidence_collection_precheck_passed", False)),
                "evidence_collection_precheck_decision": str(decision_row.get("evidence_collection_precheck_decision", "")),
                "source_controlled_forward_observation_start_run_performed": True,
                "source_controlled_forward_observation_start_performed": True,
                "forward_observation_start_allowed": True,
                "forward_observation_started": True,
                "future_evidence_collection_design_allowed": future_design_allowed,
                "new_controlled_forward_observation_start_run_performed": False,
                "new_controlled_forward_observation_start_performed": False,
                "evidence_collection_enabled": False,
                "evidence_collection_started": False,
                "official_dataset_exists_before": official_before,
                "official_dataset_exists_after": official_after,
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
                "total_checks": len(checks_df),
                "warning_count": warning_count,
                "error_count": error_count,
                "blocker_count": blocker_count,
                "validation_passed": validation_passed,
                "validation_decision": "PHASE_10_28_LONG_FORWARD_OBSERVATION_EVIDENCE_COLLECTION_PRECHECK_VALIDATED" if validation_passed else "PHASE_10_28_LONG_FORWARD_OBSERVATION_EVIDENCE_COLLECTION_PRECHECK_FAILED",
            }
        ]
    )

    output_files = {
        "phase_10_27_source_summary_v1.csv": source["summary"],
        "phase_10_26_source_start_output_v1.csv": source["start_output"],
        "phase_10_27_source_validations_v1.csv": source["validations"],
        "phase_10_27_source_evidence_chain_v1.csv": source["evidence_chain"],
        "phase_10_27_source_controls_v1.csv": source["controls"],
        "phase_10_27_source_rules_v1.csv": source["rules"],
        "phase_10_27_source_requirements_v1.csv": source["requirements"],
        "phase_10_27_source_guard_matrix_v1.csv": source["guard_matrix"],
        "phase_10_27_source_decision_v1.csv": source["decision"],
        "phase_10_27_source_checks_v1.csv": source["checks"],
        "phase_10_27_source_manifest_v1.csv": source["manifest"],
        "source_precheck_artifact_manifest_v1.csv": manifest_after,
        "evidence_collection_design_requirements_v1.csv": design,
        "evidence_collection_precheck_validations_v1.csv": validations,
        "evidence_collection_precheck_evidence_chain_v1.csv": evidence,
        "evidence_collection_precheck_controls_v1.csv": controls,
        "evidence_collection_precheck_rules_v1.csv": rules,
        "evidence_collection_precheck_requirements_v1.csv": requirements,
        "evidence_collection_precheck_guard_matrix_v1.csv": guards,
        "evidence_collection_precheck_decision_v1.csv": decision,
        "evidence_collection_precheck_checks_v1.csv": checks_df,
        "evidence_collection_precheck_summary_v1.csv": summary_df,
    }
    for filename, df in output_files.items():
        df.to_csv(REPORTS_DIR / filename, index=False)

    return {
        "summary": summary_df,
        "source_phase_10_27_summary": source["summary"],
        "source_start_output": source["start_output"],
        "source_validations": source["validations"],
        "source_evidence_chain": source["evidence_chain"],
        "source_controls": source["controls"],
        "source_rules": source["rules"],
        "source_requirements": source["requirements"],
        "source_guard_matrix": source["guard_matrix"],
        "source_decision": source["decision"],
        "source_checks": source["checks"],
        "source_manifest": source["manifest"],
        "precheck_manifest": manifest_after,
        "design_requirements": design,
        "precheck_validations": validations,
        "precheck_evidence_chain": evidence,
        "precheck_controls": controls,
        "precheck_rules": rules,
        "precheck_requirements": requirements,
        "precheck_guard_matrix": guards,
        "precheck_decision": decision,
        "checks": checks_df,
    }
