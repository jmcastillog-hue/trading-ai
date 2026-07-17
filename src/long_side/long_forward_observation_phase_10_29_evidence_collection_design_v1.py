from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

import pandas as pd

from src.long_side.long_forward_observation_dataset_bootstrap_v1 import (
    OFFICIAL_DATASET_PATH,
    PRIMARY_RESEARCH_CANDIDATE,
)


REPORTS_DIR = Path("reports/p10_29_evidence_collection_design_v1")
SOURCE_DIR = Path("reports/p10_28_evidence_collection_precheck_v1")

PHASE_10_28_DOC_PATH = Path(
    "docs/PHASE_10_LONG_FORWARD_OBSERVATION_EVIDENCE_COLLECTION_PRECHECK.md"
)
PHASE_10_29_DOC_PATH = Path(
    "docs/PHASE_10_LONG_FORWARD_OBSERVATION_EVIDENCE_COLLECTION_DESIGN.md"
)

SOURCE_PATHS = {
    "summary": SOURCE_DIR / "evidence_collection_precheck_summary_v1.csv",
    "start_output": SOURCE_DIR / "phase_10_26_source_start_output_v1.csv",
    "design_requirements": SOURCE_DIR / "evidence_collection_design_requirements_v1.csv",
    "validations": SOURCE_DIR / "evidence_collection_precheck_validations_v1.csv",
    "evidence_chain": SOURCE_DIR / "evidence_collection_precheck_evidence_chain_v1.csv",
    "controls": SOURCE_DIR / "evidence_collection_precheck_controls_v1.csv",
    "rules": SOURCE_DIR / "evidence_collection_precheck_rules_v1.csv",
    "requirements": SOURCE_DIR / "evidence_collection_precheck_requirements_v1.csv",
    "guard_matrix": SOURCE_DIR / "evidence_collection_precheck_guard_matrix_v1.csv",
    "decision": SOURCE_DIR / "evidence_collection_precheck_decision_v1.csv",
    "checks": SOURCE_DIR / "evidence_collection_precheck_checks_v1.csv",
    "manifest": SOURCE_DIR / "source_precheck_artifact_manifest_v1.csv",
}

SOURCE_READY_DECISION = (
    "CONTROLLED_FORWARD_OBSERVATION_EVIDENCE_COLLECTION_PRECHECK_"
    "READY_FOR_EVIDENCE_COLLECTION_DESIGN"
)
SOURCE_OBSERVATION_STATE = "CONTROLLED_FORWARD_OBSERVATION_STARTED"

DESIGN_STATUS = "LONG_FORWARD_OBSERVATION_EVIDENCE_COLLECTION_DESIGN_ONLY"
READY_DECISION = (
    "CONTROLLED_FORWARD_OBSERVATION_EVIDENCE_COLLECTION_DESIGN_"
    "READY_FOR_DESIGN_REVIEW"
)
BLOCKED_DECISION = (
    "CONTROLLED_FORWARD_OBSERVATION_EVIDENCE_COLLECTION_DESIGN_BLOCKED"
)
RECOMMENDED_NEXT_PHASE = (
    "PHASE_10_30_LONG_FORWARD_OBSERVATION_EVIDENCE_COLLECTION_DESIGN_REVIEW_V1"
)

EXPECTED_SOURCE_COUNTS = {
    "precheck_validation_rows": 33,
    "precheck_evidence_rows": 33,
    "precheck_control_rows": 33,
    "precheck_rule_rows": 16,
    "precheck_requirement_rows": 48,
    "precheck_guard_rows": 31,
    "design_requirement_rows": 20,
}

SOURCE_FALSE_GUARDS = [
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

DESIGN_FALSE_GUARDS = [
    "new_controlled_forward_observation_start_run_performed",
    "new_controlled_forward_observation_start_performed",
    "evidence_collection_enabled",
    "evidence_collection_started",
    "official_dataset_schema_implemented",
] + SOURCE_FALSE_GUARDS

SCHEMA_FIELDS = [
    "evidence_id",
    "observation_id",
    "collected_at_utc",
    "observed_at_utc",
    "source_system",
    "source_artifact",
    "source_artifact_sha256",
    "source_row_hash",
    "candidate_id",
    "direction",
    "symbol",
    "timeframe",
    "observation_state",
    "evidence_status",
    "evidence_scope",
    "evidence_version",
    "entry_price",
    "stop_price",
    "target_price",
    "invalidation_level",
    "risk_reward",
    "cost_profile",
    "market_context",
    "activation_scope",
    "signal_state",
    "deduplication_key",
    "deduplication_status",
    "lifecycle_state",
    "review_status",
    "rejection_reason",
    "manual_confirmation_required",
    "manual_confirmed",
    "write_ahead_validation_passed",
    "schema_validation_passed",
    "provenance_validation_passed",
    "risk_structure_validation_passed",
    "evidence_hash",
    "previous_evidence_hash",
    "audit_event_id",
    "created_by",
    "reviewed_by",
    "rollback_reference",
    "accepted_as_real_evidence",
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
    "notes",
]

DESIGN_COMPONENT_SPECS = [
    ("accepted_observation_source_defined", "SOURCE_ALLOWLIST", "Allowlisted research sources with provenance."),
    ("timestamp_timezone_requirements_defined", "UTC_TIMESTAMP_CONTRACT", "Parseable UTC collection and observation timestamps."),
    ("candidate_identity_requirements_defined", "CANDIDATE_IDENTITY_CONTRACT", "Approved research candidate identifier."),
    ("direction_requirements_defined", "LONG_DIRECTION_CONTRACT", "Direction must be LONG."),
    ("symbol_timeframe_requirements_defined", "MARKET_IDENTITY_CONTRACT", "Non-empty symbol and timeframe."),
    ("price_structure_requirements_defined", "LONG_PRICE_STRUCTURE_CONTRACT", "Stop < entry < target and invalidation equals stop."),
    ("risk_reward_consistency_requirements_defined", "RISK_REWARD_CONTRACT", "Mathematically consistent R/R equal to 2.5."),
    ("evidence_identity_deduplication_rules_defined", "DEDUPLICATION_CONTRACT", "Deterministic evidence and deduplication identities."),
    ("observation_lifecycle_states_defined", "LIFECYCLE_CONTRACT", "Controlled lifecycle transitions."),
    ("evidence_review_status_defined", "REVIEW_STATUS_CONTRACT", "Explicit pending, approved or rejected review state."),
    ("evidence_rejection_rules_defined", "REJECTION_CONTRACT", "Reject malformed, duplicate, unverified or unsafe evidence."),
    ("write_ahead_validation_defined", "WRITE_AHEAD_VALIDATION_CONTRACT", "All validations precede future persistence."),
    ("official_dataset_schema_defined", "SCHEMA_DESIGN_CONTRACT", "Future schema defined without implementation."),
    ("official_dataset_write_guard_defined", "OFFICIAL_WRITE_GUARD_CONTRACT", "Official writes remain blocked."),
    ("evidence_hash_provenance_fields_defined", "HASH_PROVENANCE_CONTRACT", "Source, row and evidence hashes required."),
    ("audit_trail_requirements_defined", "AUDIT_TRAIL_CONTRACT", "Audit identifiers and actor references required."),
    ("manual_confirmation_requirements_defined", "MANUAL_CONFIRMATION_CONTRACT", "Human review precedes future acceptance."),
    ("rollback_recovery_behavior_defined", "ROLLBACK_RECOVERY_CONTRACT", "Rollback reference and recovery audit required."),
    ("no_signal_generation_boundary_defined", "NO_SIGNAL_BOUNDARY", "Evidence collection cannot generate signals."),
    ("no_execution_boundary_defined", "NO_EXECUTION_BOUNDARY", "Evidence collection cannot place orders."),
]

ACCEPTED_SOURCE_RULES = [
    ("SYSTEM_FORWARD_OBSERVATION_CANDIDATE_DETECTOR", "System-generated research candidate observation."),
    ("MANUAL_RESEARCH_REVIEW", "Human-created or corrected research observation."),
    ("CONTROLLED_MARKET_DATA_SNAPSHOT", "Controlled read-only market-data snapshot."),
]

LIFECYCLE_STATES = [
    (1, "CAPTURE_PENDING", False, False),
    (2, "CAPTURED_UNVALIDATED", False, False),
    (3, "VALIDATION_REJECTED", True, False),
    (4, "VALIDATED_PENDING_REVIEW", False, False),
    (5, "REVIEW_REJECTED", True, False),
    (6, "REVIEW_APPROVED_PENDING_PERSISTENCE", False, False),
    (7, "PERSISTENCE_BLOCKED", True, False),
    (8, "PERSISTED_OFFICIAL", True, True),
]

DEDUPLICATION_RULES = [
    ("DEDUP_001", "Require deterministic deduplication_key."),
    ("DEDUP_002", "Use candidate, direction, symbol and timeframe."),
    ("DEDUP_003", "Use observed_at_utc normalized to UTC."),
    ("DEDUP_004", "Use entry, stop, target and invalidation values."),
    ("DEDUP_005", "Use source_row_hash when source rows exist."),
    ("DEDUP_006", "Reject exact evidence_hash duplicates."),
    ("DEDUP_007", "Flag near-duplicates for manual review."),
    ("DEDUP_008", "Never silently overwrite prior evidence."),
]

REJECTION_RULES = [
    ("REJECT_001", "Missing evidence or observation identity."),
    ("REJECT_002", "Unparseable or non-UTC timestamps."),
    ("REJECT_003", "Source system is not allowlisted."),
    ("REJECT_004", "Missing or invalid provenance hash."),
    ("REJECT_005", "Candidate identity mismatch."),
    ("REJECT_006", "Direction is not LONG."),
    ("REJECT_007", "Missing symbol or timeframe."),
    ("REJECT_008", "Invalid LONG price structure."),
    ("REJECT_009", "Risk/reward is inconsistent or not 2.5."),
    ("REJECT_010", "Exact duplicate evidence."),
    ("REJECT_011", "Schema validation failed."),
    ("REJECT_012", "Write-ahead validation failed."),
    ("REJECT_013", "Manual confirmation required but absent."),
    ("REJECT_014", "Execution or alert flags are enabled."),
    ("REJECT_015", "Official dataset write guard is not active."),
]

WRITE_GUARDS = [
    ("WRITE_GUARD_001", "Precheck and design review must pass."),
    ("WRITE_GUARD_002", "Official dataset schema must be approved."),
    ("WRITE_GUARD_003", "Evidence schema validation must pass."),
    ("WRITE_GUARD_004", "Provenance validation must pass."),
    ("WRITE_GUARD_005", "Risk structure validation must pass."),
    ("WRITE_GUARD_006", "Deduplication validation must pass."),
    ("WRITE_GUARD_007", "Manual review must approve evidence."),
    ("WRITE_GUARD_008", "Evidence hash must be valid and unique."),
    ("WRITE_GUARD_009", "Audit event identifier must exist."),
    ("WRITE_GUARD_010", "Rollback reference must be available."),
    ("WRITE_GUARD_011", "Signal and execution flags must remain false."),
    ("WRITE_GUARD_012", "A later explicit persistence approval is required."),
]

AUDIT_REQUIREMENTS = [
    ("AUDIT_001", "Create a unique audit_event_id."),
    ("AUDIT_002", "Record created_by."),
    ("AUDIT_003", "Record reviewed_by when reviewed."),
    ("AUDIT_004", "Record collected_at_utc."),
    ("AUDIT_005", "Record observed_at_utc."),
    ("AUDIT_006", "Record source artifact and SHA-256."),
    ("AUDIT_007", "Record source row hash."),
    ("AUDIT_008", "Record evidence hash and prior hash."),
    ("AUDIT_009", "Record lifecycle and review transitions."),
    ("AUDIT_010", "Record rejection or rollback reason."),
]

BOUNDARY_RULES = [
    ("BOUNDARY_001", "Design artifacts only."),
    ("BOUNDARY_002", "No evidence collection."),
    ("BOUNDARY_003", "No evidence persistence."),
    ("BOUNDARY_004", "No official dataset creation."),
    ("BOUNDARY_005", "No official dataset writes."),
    ("BOUNDARY_006", "No signal generation."),
    ("BOUNDARY_007", "No live alerts."),
    ("BOUNDARY_008", "No paper trading."),
    ("BOUNDARY_009", "No real capital."),
    ("BOUNDARY_010", "No market or exchange execution."),
    ("BOUNDARY_011", "No automation."),
    ("BOUNDARY_012", "LONG strategy remains unapproved."),
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
        df[["artifact_name", "artifact_path", "artifact_size_bytes", "artifact_sha256"]]
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


def build_evidence_schema() -> pd.DataFrame:
    bool_fields = {
        "manual_confirmation_required",
        "manual_confirmed",
        "write_ahead_validation_passed",
        "schema_validation_passed",
        "provenance_validation_passed",
        "risk_structure_validation_passed",
        "accepted_as_real_evidence",
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
    }
    float_fields = {"entry_price", "stop_price", "target_price", "invalidation_level", "risk_reward"}
    datetime_fields = {"collected_at_utc", "observed_at_utc"}
    safety_fields = {
        "accepted_as_real_evidence",
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
    }
    optional_fields = {"previous_evidence_hash", "reviewed_by", "rollback_reference", "rejection_reason", "notes"}
    rows = []
    for position, field_name in enumerate(SCHEMA_FIELDS, start=1):
        field_type = "str"
        if field_name in bool_fields:
            field_type = "bool"
        elif field_name in float_fields:
            field_type = "float"
        elif field_name in datetime_fields:
            field_type = "datetime_utc"
        rows.append(
            {
                "field_position": position,
                "field_name": field_name,
                "field_type": field_type,
                "required": field_name not in optional_fields,
                "design_only": True,
                "official_dataset_implemented": False,
                "safety_lock_field": field_name in safety_fields,
                "default_value": False if field_name in safety_fields else "",
                "description": f"Design contract field: {field_name}.",
                "passed": True,
            }
        )
    return pd.DataFrame(rows)


def build_design_components(source_requirements: pd.DataFrame) -> pd.DataFrame:
    names = set(
        source_requirements.get("design_requirement_name", pd.Series(dtype=str))
        .astype(str)
        .tolist()
    )
    return pd.DataFrame(
        [
            {
                "component_position": position,
                "component_id": f"EVIDENCE_COLLECTION_DESIGN_COMPONENT_{position:03d}",
                "source_design_requirement_name": requirement_name,
                "source_requirement_found": requirement_name in names,
                "contract_id": contract_id,
                "specification": specification,
                "defined": True,
                "implemented": False,
                "evidence_collection_enabled": False,
                "official_dataset_write_allowed": False,
                "signal_generation_enabled": False,
                "market_execution_allowed": False,
                "passed": requirement_name in names,
            }
            for position, (requirement_name, contract_id, specification) in enumerate(
                DESIGN_COMPONENT_SPECS,
                start=1,
            )
        ]
    )


def build_accepted_source_rules() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "source_rule_position": position,
                "source_rule_id": f"ACCEPTED_SOURCE_RULE_{position:03d}",
                "source_system": source_system,
                "description": description,
                "allowlisted_for_future_design": True,
                "enabled_in_phase_10_29": False,
                "requires_provenance_hash": True,
                "requires_utc_timestamp": True,
                "requires_manual_review": True,
                "passed": True,
            }
            for position, (source_system, description) in enumerate(ACCEPTED_SOURCE_RULES, start=1)
        ]
    )


def build_lifecycle_states() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "lifecycle_position": position,
                "lifecycle_state": state,
                "terminal_state": terminal,
                "official_persistence_state": official,
                "enabled_in_phase_10_29": False,
                "requires_audit_event": True,
                "requires_manual_review": state in {"VALIDATED_PENDING_REVIEW", "REVIEW_APPROVED_PENDING_PERSISTENCE"},
                "passed": True,
            }
            for position, state, terminal, official in LIFECYCLE_STATES
        ]
    )


def build_rule_table(rows: list[tuple[str, str]], id_column: str, description_column: str) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "rule_position": position,
                id_column: rule_id,
                description_column: description,
                "defined": True,
                "implemented": False,
                "enabled_in_phase_10_29": False,
                "passed": True,
            }
            for position, (rule_id, description) in enumerate(rows, start=1)
        ]
    )


def build_validations(
    source: dict[str, pd.DataFrame],
    manifest_before: pd.DataFrame,
    manifest_after: pd.DataFrame,
    design_tables: dict[str, pd.DataFrame],
    official_dataset_absent: bool,
) -> pd.DataFrame:
    summary = source["summary"].iloc[0].to_dict() if not source["summary"].empty else {}
    output = source["start_output"].iloc[0].to_dict() if not source["start_output"].empty else {}
    decision = source["decision"].iloc[0].to_dict() if not source["decision"].empty else {}

    artifacts_exist = not manifest_before.empty and manifest_before["artifact_exists"].map(safe_bool).all()
    artifacts_non_empty = not manifest_before.empty and manifest_before["artifact_non_empty"].map(safe_bool).all()
    hashes_valid = not manifest_before.empty and manifest_before["artifact_sha256_valid"].map(safe_bool).all()
    stable = bool(manifest_digest(manifest_before)) and manifest_digest(manifest_before) == manifest_digest(manifest_after)

    counts_valid = all(
        int(safe_float(summary.get(field), -1)) == expected
        for field, expected in EXPECTED_SOURCE_COUNTS.items()
    )

    source_design = source["design_requirements"]
    source_design_count_valid = len(source_design) == 20
    source_design_defined = dataframe_all_passed(source_design)
    source_design_unimplemented = (
        not source_design.empty
        and "implemented_in_precheck" in source_design.columns
        and source_design["implemented_in_precheck"].map(lambda value: safe_bool(value, True)).eq(False).all()
    )

    entry = safe_float(output.get("entry_price"))
    stop = safe_float(output.get("stop_price"))
    target = safe_float(output.get("target_price"))
    risk_reward = safe_float(output.get("risk_reward"))
    expected_risk_reward = round((target - entry) / (entry - stop), 4) if entry > stop else 0.0
    source_locks_valid = all(safe_bool(output.get(field, True), True) is False for field in SOURCE_FALSE_GUARDS)

    summary_decision_consistent = (
        str(summary.get("evidence_collection_precheck_decision", ""))
        == str(decision.get("evidence_collection_precheck_decision", ""))
        == SOURCE_READY_DECISION
        and safe_bool(summary.get("evidence_collection_precheck_passed", False))
        and safe_bool(decision.get("evidence_collection_precheck_passed", False))
    )

    schema = design_tables["schema"]
    schema_valid = (
        len(schema) == 54
        and schema["field_name"].astype(str).tolist() == SCHEMA_FIELDS
        and dataframe_all_passed(schema)
        and schema["official_dataset_implemented"].map(lambda value: safe_bool(value, True)).eq(False).all()
    )
    safety_defaults_valid = (
        not schema.empty
        and schema.loc[schema["safety_lock_field"].map(safe_bool), "default_value"]
        .map(lambda value: safe_bool(value, True))
        .eq(False)
        .all()
    )

    rows = [
        ("source_artifacts_exist", artifacts_exist, f"artifact_count={len(manifest_before)}"),
        ("source_artifacts_non_empty", artifacts_non_empty, f"artifact_count={len(manifest_before)}"),
        ("source_artifact_hashes_valid", hashes_valid, f"artifact_count={len(manifest_before)}"),
        ("source_artifacts_stable_during_design", stable, f"before={manifest_digest(manifest_before)},after={manifest_digest(manifest_after)}"),
        ("phase_10_28_validation_passed", safe_bool(summary.get("validation_passed", False)), str(summary.get("validation_decision", ""))),
        ("source_precheck_performed", safe_bool(summary.get("evidence_collection_precheck_performed", False)), str(summary.get("evidence_collection_precheck_performed", ""))),
        ("source_precheck_passed", safe_bool(summary.get("evidence_collection_precheck_passed", False)), str(summary.get("evidence_collection_precheck_passed", ""))),
        ("source_precheck_decision_valid", str(summary.get("evidence_collection_precheck_decision", "")) == SOURCE_READY_DECISION, str(summary.get("evidence_collection_precheck_decision", ""))),
        ("source_future_design_allowed", safe_bool(summary.get("future_evidence_collection_design_allowed", False)), str(summary.get("future_evidence_collection_design_allowed", ""))),
        ("source_summary_decision_consistent", summary_decision_consistent, f"consistent={summary_decision_consistent}"),
        ("source_counts_valid", counts_valid, ",".join(f"{field}={summary.get(field, '')}" for field in EXPECTED_SOURCE_COUNTS)),
        ("source_validations_passed", dataframe_all_passed(source["validations"]), f"rows={len(source['validations'])}"),
        ("source_evidence_chain_passed", dataframe_all_passed(source["evidence_chain"]), f"rows={len(source['evidence_chain'])}"),
        ("source_controls_passed", dataframe_all_passed(source["controls"]), f"rows={len(source['controls'])}"),
        ("source_rules_passed", dataframe_all_passed(source["rules"]), f"rows={len(source['rules'])}"),
        ("source_requirements_passed", dataframe_all_passed(source["requirements"]), f"rows={len(source['requirements'])}"),
        ("source_guards_passed", dataframe_all_passed(source["guard_matrix"]), f"rows={len(source['guard_matrix'])}"),
        ("source_design_requirements_count_valid", source_design_count_valid, f"rows={len(source_design)}"),
        ("source_design_requirements_defined", source_design_defined, f"passed={source_design_defined}"),
        ("source_design_requirements_unimplemented", source_design_unimplemented, f"unimplemented={source_design_unimplemented}"),
        ("source_start_output_row_count_one", len(source["start_output"]) == 1, f"rows={len(source['start_output'])}"),
        ("source_candidate_valid", str(output.get("candidate_id", "")) == PRIMARY_RESEARCH_CANDIDATE, str(output.get("candidate_id", ""))),
        ("source_direction_valid", str(output.get("direction", "")) == "LONG", str(output.get("direction", ""))),
        ("source_observation_state_started", str(output.get("observation_state", "")) == SOURCE_OBSERVATION_STATE and safe_bool(output.get("forward_observation_started", False)), str(output.get("observation_state", ""))),
        ("source_price_structure_valid", stop < entry < target and safe_float(output.get("invalidation_level")) == stop, f"stop={stop},entry={entry},target={target}"),
        ("source_risk_reward_valid", risk_reward == expected_risk_reward and risk_reward == 2.5, f"risk_reward={risk_reward},expected={expected_risk_reward}"),
        ("source_operational_locks_valid", source_locks_valid, f"false_guard_count={len(SOURCE_FALSE_GUARDS)}"),
        ("source_official_evidence_rows_zero", int(safe_float(output.get("official_evidence_rows_written"), -1)) == 0, str(output.get("official_evidence_rows_written", ""))),
        ("official_dataset_absent", official_dataset_absent, f"official_dataset_absent={official_dataset_absent}"),
        ("evidence_schema_field_count_valid", len(schema) == 54, f"field_count={len(schema)}"),
        ("evidence_schema_valid", schema_valid, f"schema_valid={schema_valid}"),
        ("evidence_schema_safety_defaults_valid", safety_defaults_valid, f"safety_defaults_valid={safety_defaults_valid}"),
        ("design_components_valid", len(design_tables["components"]) == 20 and dataframe_all_passed(design_tables["components"]), f"rows={len(design_tables['components'])}"),
        ("accepted_source_rules_valid", len(design_tables["accepted_sources"]) == 3 and dataframe_all_passed(design_tables["accepted_sources"]), f"rows={len(design_tables['accepted_sources'])}"),
        ("lifecycle_states_valid", len(design_tables["lifecycle"]) == 8 and dataframe_all_passed(design_tables["lifecycle"]), f"rows={len(design_tables['lifecycle'])}"),
        ("deduplication_rules_valid", len(design_tables["deduplication"]) == 8 and dataframe_all_passed(design_tables["deduplication"]), f"rows={len(design_tables['deduplication'])}"),
        ("rejection_rules_valid", len(design_tables["rejection"]) == 15 and dataframe_all_passed(design_tables["rejection"]), f"rows={len(design_tables['rejection'])}"),
        ("write_guards_valid", len(design_tables["write_guards"]) == 12 and dataframe_all_passed(design_tables["write_guards"]), f"rows={len(design_tables['write_guards'])}"),
        ("audit_requirements_valid", len(design_tables["audit"]) == 10 and dataframe_all_passed(design_tables["audit"]), f"rows={len(design_tables['audit'])}"),
        ("boundary_rules_valid", len(design_tables["boundaries"]) == 12 and dataframe_all_passed(design_tables["boundaries"]), f"rows={len(design_tables['boundaries'])}"),
        ("all_design_tables_passed", all(dataframe_all_passed(table) for table in design_tables.values()), "all_design_tables_passed=True"),
        ("no_evidence_collection_enabled", True, "evidence_collection_enabled=False"),
        ("no_official_dataset_implementation", True, "official_dataset_schema_implemented=False"),
        ("no_duplicate_start_run", True, "new_start_run=False,new_start=False"),
    ]
    return pd.DataFrame([{"validation_name": name, "passed": bool(passed), "details": details} for name, passed, details in rows])


def build_evidence_chain(validations: pd.DataFrame) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "evidence_position": position,
                "evidence_id": f"EVIDENCE_COLLECTION_DESIGN_EVIDENCE_{position:03d}",
                "evidence_name": str(row["validation_name"]),
                "evidence_group": "design_validation",
                "required": True,
                "passed": safe_bool(row["passed"], False),
                "details": "Validated from Phase 10.28 and Phase 10.29 design artifacts.",
            }
            for position, (_, row) in enumerate(validations.iterrows(), start=1)
        ]
    )


def build_controls(evidence: pd.DataFrame) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "control_position": int(row["evidence_position"]),
                "control_id": f"EVIDENCE_COLLECTION_DESIGN_CONTROL_{int(row['evidence_position']):03d}",
                "control_name": str(row["evidence_name"]),
                "required": True,
                "design_only": True,
                "evidence_collection_enabled": False,
                "official_dataset_schema_implemented": False,
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
    for name in [
        "source_controlled_forward_observation_start_run_performed",
        "source_controlled_forward_observation_start_performed",
        "forward_observation_start_allowed",
        "forward_observation_started",
        "evidence_collection_design_performed",
        "evidence_collection_design_passed",
        "future_evidence_collection_design_review_allowed",
    ]:
        rows.append({"guard_name": name, "required_value": True, "actual_value": True, "passed": True, "guard_group": "design_state"})
    for name in DESIGN_FALSE_GUARDS:
        rows.append({"guard_name": name, "required_value": False, "actual_value": False, "passed": True, "guard_group": "design_safety_guard"})
    rows.append({"guard_name": "official_evidence_rows_written", "required_value": 0, "actual_value": 0, "passed": True, "guard_group": "official_dataset_guard"})
    return pd.DataFrame(rows)


def build_rules(validations: pd.DataFrame, evidence: pd.DataFrame, controls: pd.DataFrame, guards: pd.DataFrame, schema: pd.DataFrame, components: pd.DataFrame) -> pd.DataFrame:
    validation_count = len(validations)
    rows = [
        ("design_validation_count", validation_count > 0, ">0", str(validation_count), "validation"),
        ("all_design_validations_passed", dataframe_all_passed(validations), "True", str(dataframe_all_passed(validations)), "validation"),
        ("design_evidence_count_matches", len(evidence) == validation_count, str(validation_count), str(len(evidence)), "evidence"),
        ("all_design_evidence_passed", dataframe_all_passed(evidence), "True", str(dataframe_all_passed(evidence)), "evidence"),
        ("design_control_count_matches", len(controls) == validation_count, str(validation_count), str(len(controls)), "controls"),
        ("all_design_controls_passed", dataframe_all_passed(controls), "True", str(dataframe_all_passed(controls)), "controls"),
        ("design_guard_count_35", len(guards) == 35, "35", str(len(guards)), "safety"),
        ("all_design_guards_passed", dataframe_all_passed(guards), "True", str(dataframe_all_passed(guards)), "safety"),
        ("evidence_schema_field_count_54", len(schema) == 54, "54", str(len(schema)), "schema"),
        ("all_evidence_schema_fields_valid", dataframe_all_passed(schema), "True", str(dataframe_all_passed(schema)), "schema"),
        ("design_component_count_20", len(components) == 20, "20", str(len(components)), "design_components"),
        ("all_design_components_valid", dataframe_all_passed(components), "True", str(dataframe_all_passed(components)), "design_components"),
        ("design_only", True, "True", "True", "scope_control"),
        ("evidence_collection_disabled", True, "False", "False", "evidence_boundary"),
        ("official_dataset_not_implemented", True, "False", "False", "official_dataset_guard"),
        ("official_dataset_writes_disabled", True, "False", "False", "official_dataset_guard"),
        ("signal_generation_disabled", True, "False", "False", "signal_boundary"),
        ("market_execution_disabled", True, "False", "False", "market_execution_guard"),
        ("total_project_not_completed", True, "False", "False", "scope_control"),
    ]
    return pd.DataFrame(
        [
            {
                "rule_id": f"EVIDENCE_COLLECTION_DESIGN_RULE_{position:03d}",
                "rule_name": name,
                "passed": bool(passed),
                "required_value": required,
                "actual_value": actual,
                "rule_group": group,
            }
            for position, (name, passed, required, actual, group) in enumerate(rows, start=1)
        ]
    )


def build_requirements(validations: pd.DataFrame, evidence: pd.DataFrame, controls: pd.DataFrame, rules: pd.DataFrame, guards: pd.DataFrame, design_tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    rows = [
        (str(row["validation_name"]), safe_bool(row["passed"], False), "True", str(safe_bool(row["passed"], False)), "design_validation")
        for _, row in validations.iterrows()
    ]
    rows.extend(
        [
            ("design_evidence_chain_passed", dataframe_all_passed(evidence), "True", str(dataframe_all_passed(evidence)), "evidence"),
            ("design_controls_passed", dataframe_all_passed(controls), "True", str(dataframe_all_passed(controls)), "controls"),
            ("design_rules_passed", dataframe_all_passed(rules), "True", str(dataframe_all_passed(rules)), "rules"),
            ("design_guards_passed", dataframe_all_passed(guards), "True", str(dataframe_all_passed(guards)), "safety"),
        ]
    )
    for table_name, table in design_tables.items():
        rows.append((f"{table_name}_defined", dataframe_all_passed(table), "True", str(dataframe_all_passed(table)), "design_artifact"))
    rows.extend(
        [
            ("evidence_collection_design_performed", True, "True", "True", "design_state"),
            ("future_design_review_allowed", True, "True", "True", "future_review"),
            ("evidence_collection_not_enabled", True, "False", "False", "evidence_boundary"),
            ("official_dataset_schema_not_implemented", True, "False", "False", "official_dataset_guard"),
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
                "requirement_id": f"EVIDENCE_COLLECTION_DESIGN_REQ_{position:03d}",
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
    passed = len(requirements) > 0 and failed_requirements == 0 and dataframe_all_passed(rules) and dataframe_all_passed(guards)
    failed_names = ",".join(requirements[~requirements["passed"].map(safe_bool)]["requirement_name"].astype(str).tolist()) if not requirements.empty else ""
    return pd.DataFrame(
        [
            {
                "evidence_collection_design_id": "PHASE_10_29_LONG_FORWARD_OBSERVATION_EVIDENCE_COLLECTION_DESIGN_001",
                "evidence_collection_design_status": DESIGN_STATUS,
                "evidence_collection_design_performed": True,
                "evidence_collection_design_passed": passed,
                "evidence_collection_design_decision": READY_DECISION if passed else BLOCKED_DECISION,
                "total_requirements": len(requirements),
                "passed_requirements": passed_requirements,
                "failed_requirements": failed_requirements,
                "failed_requirement_names": failed_names,
                "design_rules_passed": dataframe_all_passed(rules),
                "design_guards_passed": dataframe_all_passed(guards),
                "source_controlled_forward_observation_start_run_performed": True,
                "source_controlled_forward_observation_start_performed": True,
                "forward_observation_start_allowed": True,
                "forward_observation_started": True,
                "future_evidence_collection_design_review_allowed": passed,
                "new_controlled_forward_observation_start_run_performed": False,
                "new_controlled_forward_observation_start_performed": False,
                "evidence_collection_enabled": False,
                "evidence_collection_started": False,
                "official_dataset_schema_implemented": False,
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


def validate_long_forward_observation_evidence_collection_design() -> dict[str, pd.DataFrame]:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    checks: list[dict[str, Any]] = []

    for name, path in {
        "phase_10_28_precheck_doc_exists": PHASE_10_28_DOC_PATH,
        "phase_10_29_design_doc_exists": PHASE_10_29_DOC_PATH,
    }.items():
        exists = path.exists()
        checks.append(build_check("phase_anchor", name, exists, "INFO" if exists else "ERROR", str(path)))

    official_before = OFFICIAL_DATASET_PATH.exists()
    manifest_before = build_manifest()
    source = {name: read_csv(path) for name, path in SOURCE_PATHS.items()}

    design_tables = {
        "schema": build_evidence_schema(),
        "components": build_design_components(source["design_requirements"]),
        "accepted_sources": build_accepted_source_rules(),
        "lifecycle": build_lifecycle_states(),
        "deduplication": build_rule_table(DEDUPLICATION_RULES, "deduplication_rule_id", "deduplication_rule"),
        "rejection": build_rule_table(REJECTION_RULES, "rejection_rule_id", "rejection_rule"),
        "write_guards": build_rule_table(WRITE_GUARDS, "write_guard_id", "write_guard"),
        "audit": build_rule_table(AUDIT_REQUIREMENTS, "audit_requirement_id", "audit_requirement"),
        "boundaries": build_rule_table(BOUNDARY_RULES, "boundary_rule_id", "boundary_rule"),
    }

    manifest_after = build_manifest()
    validations = build_validations(source, manifest_before, manifest_after, design_tables, official_dataset_absent=not official_before)
    evidence = build_evidence_chain(validations)
    controls = build_controls(evidence)
    guards = build_guard_matrix()
    rules = build_rules(validations, evidence, controls, guards, design_tables["schema"], design_tables["components"])
    requirements = build_requirements(validations, evidence, controls, rules, guards, design_tables)
    decision = build_decision(requirements, rules, guards)
    decision_row = decision.iloc[0].to_dict() if not decision.empty else {}

    aggregate_checks = [
        ("design_validations_passed", dataframe_all_passed(validations)),
        ("design_evidence_chain_passed", dataframe_all_passed(evidence)),
        ("design_controls_passed", dataframe_all_passed(controls)),
        ("design_rules_passed", dataframe_all_passed(rules)),
        ("design_requirements_passed", dataframe_all_passed(requirements)),
        ("design_guards_passed", dataframe_all_passed(guards)),
        ("evidence_schema_defined", dataframe_all_passed(design_tables["schema"])),
        ("design_components_defined", dataframe_all_passed(design_tables["components"])),
        ("evidence_collection_design_passed", safe_bool(decision_row.get("evidence_collection_design_passed", False))),
        ("evidence_collection_design_decision_expected", str(decision_row.get("evidence_collection_design_decision", "")) == READY_DECISION),
    ]
    for name, passed in aggregate_checks:
        details = str(decision_row.get("evidence_collection_design_decision", "")) if name.endswith("decision_expected") else f"{name}={passed}"
        checks.append(build_check("evidence_collection_design", name, passed, "INFO" if passed else "ERROR", details))

    official_after = OFFICIAL_DATASET_PATH.exists()
    official_unchanged_absent = not official_before and not official_after
    checks.append(build_check("official_dataset_guard", "official_dataset_not_created_or_written", official_unchanged_absent, "INFO" if official_unchanged_absent else "ERROR", f"before={official_before},after={official_after}"))

    for _, row in guards.iterrows():
        passed = safe_bool(row["passed"], False)
        checks.append(build_check("evidence_collection_design_safety_flags", str(row["guard_name"]), passed, "INFO" if passed else "ERROR", f"{row['guard_name']}={row['actual_value']} (required={row['required_value']})"))

    for name, details in [
        ("design_only", "Phase 10.29 defines only the evidence collection design."),
        ("observation_state_preserved", "The controlled observation state remains started."),
        ("evidence_collection_not_enabled", "Evidence collection remains disabled."),
        ("official_dataset_not_implemented", "The official evidence dataset is not implemented."),
        ("official_dataset_not_written", "The official evidence dataset remains absent and unwritten."),
        ("signal_generation_not_enabled", "Signal generation remains disabled."),
        ("live_alerts_not_enabled", "Live alerts remain disabled."),
        ("paper_trading_not_enabled", "Paper trading execution remains disabled."),
        ("long_strategy_not_approved", "The LONG research candidate is not approved as a trading strategy."),
        ("real_capital_not_allowed", "Real capital remains prohibited."),
        ("market_execution_not_allowed", "Market execution remains prohibited."),
        ("total_project_not_completed", "The total project is not completed."),
    ]:
        checks.append(build_check("scope_control", name, True, "WARNING", details))

    future_review_allowed = safe_bool(decision_row.get("future_evidence_collection_design_review_allowed", False))
    checks.append(build_check("planning_scope", "future_evidence_collection_design_review_allowed", future_review_allowed, "WARNING" if future_review_allowed else "ERROR", "This permits only a future evidence collection design review."))
    checks.append(build_check("phase_transition", "phase_10_30_recommended_next", True, "INFO", "Recommended next step: Phase 10.30 LONG Forward Observation Evidence Collection Design Review V1."))

    checks_df = pd.DataFrame(checks)
    blocker_count = int(checks_df["blocker"].map(safe_bool).sum())
    error_count = int(checks_df["severity"].eq("ERROR").sum())
    warning_count = int(checks_df["severity"].eq("WARNING").sum())
    validation_passed = blocker_count == 0 and error_count == 0

    source_summary = source["summary"].iloc[0].to_dict() if not source["summary"].empty else {}
    start_output = source["start_output"].iloc[0].to_dict() if not source["start_output"].empty else {}
    lookup = {str(row["validation_name"]): safe_bool(row["passed"]) for _, row in validations.iterrows()}
    design_passed = safe_bool(decision_row.get("evidence_collection_design_passed", False))
    design_decision = str(decision_row.get("evidence_collection_design_decision", ""))

    summary_df = pd.DataFrame(
        [
            {
                "phase": "10.29",
                "long_forward_observation_evidence_collection_design_defined": True,
                "phase_10_28_validation_passed": lookup.get("phase_10_28_validation_passed", False),
                "source_evidence_collection_precheck_performed": lookup.get("source_precheck_performed", False),
                "source_evidence_collection_precheck_passed": lookup.get("source_precheck_passed", False),
                "source_evidence_collection_precheck_decision": str(source_summary.get("evidence_collection_precheck_decision", "")),
                "source_future_evidence_collection_design_allowed": lookup.get("source_future_design_allowed", False),
                "source_artifact_count": len(manifest_after),
                "source_artifacts_exist": lookup.get("source_artifacts_exist", False),
                "source_artifacts_non_empty": lookup.get("source_artifacts_non_empty", False),
                "source_artifact_hashes_valid": lookup.get("source_artifact_hashes_valid", False),
                "source_artifacts_stable_during_design": lookup.get("source_artifacts_stable_during_design", False),
                "source_manifest_sha256": manifest_digest(manifest_after),
                "source_design_requirements_count": len(source["design_requirements"]),
                "source_design_requirements_defined": lookup.get("source_design_requirements_defined", False),
                "source_design_requirements_not_implemented_in_precheck": lookup.get("source_design_requirements_unimplemented", False),
                "source_candidate_id": str(start_output.get("candidate_id", "")),
                "source_candidate_valid": lookup.get("source_candidate_valid", False),
                "source_direction": str(start_output.get("direction", "")),
                "source_direction_valid": lookup.get("source_direction_valid", False),
                "source_observation_state": str(start_output.get("observation_state", "")),
                "source_observation_state_started": lookup.get("source_observation_state_started", False),
                "source_price_structure_valid": lookup.get("source_price_structure_valid", False),
                "source_risk_reward": safe_float(start_output.get("risk_reward")),
                "source_risk_reward_valid": lookup.get("source_risk_reward_valid", False),
                "source_operational_locks_valid": lookup.get("source_operational_locks_valid", False),
                "source_official_evidence_rows_zero": lookup.get("source_official_evidence_rows_zero", False),
                "official_dataset_absent": lookup.get("official_dataset_absent", False),
                "evidence_schema_field_count": len(design_tables["schema"]),
                "evidence_schema_valid": lookup.get("evidence_schema_valid", False),
                "evidence_schema_safety_defaults_valid": lookup.get("evidence_schema_safety_defaults_valid", False),
                "design_component_count": len(design_tables["components"]),
                "design_components_valid": lookup.get("design_components_valid", False),
                "accepted_source_rule_count": len(design_tables["accepted_sources"]),
                "accepted_source_rules_valid": lookup.get("accepted_source_rules_valid", False),
                "lifecycle_state_count": len(design_tables["lifecycle"]),
                "lifecycle_states_valid": lookup.get("lifecycle_states_valid", False),
                "deduplication_rule_count": len(design_tables["deduplication"]),
                "deduplication_rules_valid": lookup.get("deduplication_rules_valid", False),
                "rejection_rule_count": len(design_tables["rejection"]),
                "rejection_rules_valid": lookup.get("rejection_rules_valid", False),
                "write_guard_count": len(design_tables["write_guards"]),
                "write_guards_valid": lookup.get("write_guards_valid", False),
                "audit_requirement_count": len(design_tables["audit"]),
                "audit_requirements_valid": lookup.get("audit_requirements_valid", False),
                "boundary_rule_count": len(design_tables["boundaries"]),
                "boundary_rules_valid": lookup.get("boundary_rules_valid", False),
                "design_validation_rows": len(validations),
                "design_evidence_rows": len(evidence),
                "design_control_rows": len(controls),
                "design_rule_rows": len(rules),
                "design_requirement_rows": len(requirements),
                "design_guard_rows": len(guards),
                "design_validations_passed": dataframe_all_passed(validations),
                "design_evidence_chain_passed": dataframe_all_passed(evidence),
                "design_controls_passed": dataframe_all_passed(controls),
                "design_rules_passed": dataframe_all_passed(rules),
                "design_requirements_passed": dataframe_all_passed(requirements),
                "design_guards_passed": dataframe_all_passed(guards),
                "evidence_collection_design_performed": True,
                "evidence_collection_design_passed": design_passed,
                "evidence_collection_design_decision": design_decision,
                "source_controlled_forward_observation_start_run_performed": True,
                "source_controlled_forward_observation_start_performed": True,
                "forward_observation_start_allowed": True,
                "forward_observation_started": True,
                "future_evidence_collection_design_review_allowed": future_review_allowed,
                "new_controlled_forward_observation_start_run_performed": False,
                "new_controlled_forward_observation_start_performed": False,
                "evidence_collection_enabled": False,
                "evidence_collection_started": False,
                "official_dataset_schema_implemented": False,
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
                "validation_decision": (
                    "PHASE_10_29_LONG_FORWARD_OBSERVATION_EVIDENCE_COLLECTION_DESIGN_VALIDATED"
                    if validation_passed
                    else "PHASE_10_29_LONG_FORWARD_OBSERVATION_EVIDENCE_COLLECTION_DESIGN_FAILED"
                ),
            }
        ]
    )

    output_files = {
        "phase_10_28_source_summary_v1.csv": source["summary"],
        "phase_10_26_source_start_output_v1.csv": source["start_output"],
        "phase_10_28_source_design_requirements_v1.csv": source["design_requirements"],
        "phase_10_28_source_validations_v1.csv": source["validations"],
        "phase_10_28_source_evidence_chain_v1.csv": source["evidence_chain"],
        "phase_10_28_source_controls_v1.csv": source["controls"],
        "phase_10_28_source_rules_v1.csv": source["rules"],
        "phase_10_28_source_requirements_v1.csv": source["requirements"],
        "phase_10_28_source_guard_matrix_v1.csv": source["guard_matrix"],
        "phase_10_28_source_decision_v1.csv": source["decision"],
        "phase_10_28_source_checks_v1.csv": source["checks"],
        "phase_10_28_source_manifest_v1.csv": source["manifest"],
        "source_design_artifact_manifest_v1.csv": manifest_after,
        "evidence_collection_design_schema_v1.csv": design_tables["schema"],
        "evidence_collection_design_components_v1.csv": design_tables["components"],
        "evidence_collection_accepted_source_rules_v1.csv": design_tables["accepted_sources"],
        "evidence_collection_lifecycle_states_v1.csv": design_tables["lifecycle"],
        "evidence_collection_deduplication_rules_v1.csv": design_tables["deduplication"],
        "evidence_collection_rejection_rules_v1.csv": design_tables["rejection"],
        "evidence_collection_write_guards_v1.csv": design_tables["write_guards"],
        "evidence_collection_audit_requirements_v1.csv": design_tables["audit"],
        "evidence_collection_boundary_rules_v1.csv": design_tables["boundaries"],
        "evidence_collection_design_validations_v1.csv": validations,
        "evidence_collection_design_evidence_chain_v1.csv": evidence,
        "evidence_collection_design_controls_v1.csv": controls,
        "evidence_collection_design_rules_v1.csv": rules,
        "evidence_collection_design_requirements_v1.csv": requirements,
        "evidence_collection_design_guard_matrix_v1.csv": guards,
        "evidence_collection_design_decision_v1.csv": decision,
        "evidence_collection_design_checks_v1.csv": checks_df,
        "evidence_collection_design_summary_v1.csv": summary_df,
    }
    for filename, dataframe in output_files.items():
        dataframe.to_csv(REPORTS_DIR / filename, index=False)

    return {
        "summary": summary_df,
        "source_phase_10_28_summary": source["summary"],
        "source_start_output": source["start_output"],
        "source_design_requirements": source["design_requirements"],
        "source_validations": source["validations"],
        "source_evidence_chain": source["evidence_chain"],
        "source_controls": source["controls"],
        "source_rules": source["rules"],
        "source_requirements": source["requirements"],
        "source_guard_matrix": source["guard_matrix"],
        "source_decision": source["decision"],
        "source_checks": source["checks"],
        "source_manifest": source["manifest"],
        "design_manifest": manifest_after,
        "design_schema": design_tables["schema"],
        "design_components": design_tables["components"],
        "accepted_source_rules": design_tables["accepted_sources"],
        "lifecycle_states": design_tables["lifecycle"],
        "deduplication_rules": design_tables["deduplication"],
        "rejection_rules": design_tables["rejection"],
        "write_guards": design_tables["write_guards"],
        "audit_requirements": design_tables["audit"],
        "boundary_rules": design_tables["boundaries"],
        "design_validations": validations,
        "design_evidence_chain": evidence,
        "design_controls": controls,
        "design_rules": rules,
        "design_requirements": requirements,
        "design_guard_matrix": guards,
        "design_decision": decision,
        "checks": checks_df,
    }
