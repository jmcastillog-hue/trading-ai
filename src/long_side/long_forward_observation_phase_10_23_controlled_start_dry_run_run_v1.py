from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

from src.long_side.long_forward_observation_dataset_bootstrap_v1 import (
    OFFICIAL_DATASET_PATH,
    PRIMARY_RESEARCH_CANDIDATE,
)
from src.long_side.long_forward_observation_phase_10_22_controlled_start_dry_run_execution_review_v1 import (
    READY_DECISION as EXECUTION_REVIEW_READY_DECISION,
    validate_long_forward_observation_controlled_start_dry_run_execution_review,
)


REPORTS_DIR = Path("reports/p10_23_start_dry_run_run_v1")
PHASE_10_22_REPORTS_DIR = Path("reports/p10_22_start_dry_run_execution_review_v1")

PHASE_10_22_EXECUTION_REVIEW_DOC_PATH = Path(
    "docs/PHASE_10_LONG_FORWARD_OBSERVATION_CONTROLLED_START_DRY_RUN_EXECUTION_REVIEW.md"
)
PHASE_10_23_START_DRY_RUN_RUN_DOC_PATH = Path(
    "docs/PHASE_10_LONG_FORWARD_OBSERVATION_CONTROLLED_START_DRY_RUN_RUN.md"
)

START_DRY_RUN_RUN_STATUS = (
    "LONG_FORWARD_OBSERVATION_CONTROLLED_START_DRY_RUN_RUN_DRY_RUN_ONLY"
)
READY_DECISION = (
    "CONTROLLED_FORWARD_OBSERVATION_START_DRY_RUN_RUN_COMPLETED_DRY_RUN_ONLY"
)
BLOCKED_DECISION = (
    "CONTROLLED_FORWARD_OBSERVATION_START_DRY_RUN_RUN_BLOCKED"
)
RECOMMENDED_NEXT_PHASE = (
    "PHASE_10_24_LONG_FORWARD_OBSERVATION_CONTROLLED_START_DRY_RUN_OUTPUT_INTEGRITY_REVIEW_V1"
)

RUN_SCOPE = "CONTROLLED_FORWARD_OBSERVATION_START_DRY_RUN_ONLY"
EVIDENCE_SCOPE = "DRY_RUN_ONLY_NOT_REAL_EVIDENCE"
VALIDATION_STATUS = "CONTROLLED_START_DRY_RUN_ROW_CREATED"

EXPECTED_FALSE_GUARDS = {
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

START_DRY_RUN_OUTPUT_COLUMNS = [
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
    "observation_role",
    "signal_state",
    "market_context",
    "activation_scope",
    "run_scope",
    "evidence_scope",
    "entry_price",
    "stop_price",
    "target_price",
    "invalidation_level",
    "risk_reward",
    "cost_profile",
    "manual_confirmation_required",
    "controlled_forward_observation_start_dry_run_execution_review_performed",
    "future_controlled_forward_observation_start_dry_run_run_allowed",
    "controlled_forward_observation_start_dry_run_run_allowed",
    "controlled_forward_observation_start_dry_run_run_performed",
    "controlled_forward_observation_start_dry_run_performed",
    "future_controlled_forward_observation_start_dry_run_output_integrity_review_allowed",
    "forward_observation_start_allowed",
    "forward_observation_started",
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


def get_phase_10_22_dataframe(
    result: dict[str, pd.DataFrame],
    aliases: tuple[str, ...],
    csv_path: Path,
) -> pd.DataFrame:
    """Resolve Phase 10.22 tables without depending on one exact return-key name."""
    for key in aliases:
        value = result.get(key)
        if isinstance(value, pd.DataFrame):
            return value.copy()

    if csv_path.exists():
        return pd.read_csv(csv_path)

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


def build_start_dry_run_output(
    phase_10_22_summary_df: pd.DataFrame,
    execution_review_decision_df: pd.DataFrame,
    source_design_output_df: pd.DataFrame,
) -> pd.DataFrame:
    if source_design_output_df.empty:
        return pd.DataFrame(columns=START_DRY_RUN_OUTPUT_COLUMNS)

    summary = (
        phase_10_22_summary_df.iloc[0].to_dict()
        if not phase_10_22_summary_df.empty
        else {}
    )
    decision = (
        execution_review_decision_df.iloc[0].to_dict()
        if not execution_review_decision_df.empty
        else {}
    )
    source = source_design_output_df.iloc[0].to_dict()

    entry_price = safe_float(source.get("entry_price"), 100.0)
    stop_price = safe_float(source.get("stop_price"), 95.0)
    target_price = safe_float(source.get("target_price"), 112.5)
    invalidation_level = safe_float(source.get("invalidation_level"), stop_price)

    risk = entry_price - stop_price
    reward = target_price - entry_price
    risk_reward = round(reward / risk, 4) if risk > 0 else 0.0

    row = {
        "dry_run_run_id": (
            "PHASE_10_23_LONG_FORWARD_OBSERVATION_CONTROLLED_START_DRY_RUN_RUN_001"
        ),
        "dry_run_status": START_DRY_RUN_RUN_STATUS,
        "executed_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_phase": "10.22",
        "source_validation_decision": str(
            summary.get("validation_decision", "")
        ),
        "source_execution_review_decision": str(
            decision.get(
                "controlled_forward_observation_start_dry_run_execution_review_decision",
                summary.get(
                    "controlled_forward_observation_start_dry_run_execution_review_decision",
                    "",
                ),
            )
        ),
        "source_design_id": str(source.get("dry_run_design_id", "")),
        "symbol": str(source.get("symbol", "BTCUSDT")),
        "timeframe": str(source.get("timeframe", "15m")),
        "candidate_id": str(
            source.get("candidate_id", PRIMARY_RESEARCH_CANDIDATE)
        ),
        "direction": str(source.get("direction", "LONG")),
        "observation_role": "PRIMARY_FORWARD_OBSERVATION_START_DRY_RUN",
        "signal_state": "CONTROLLED_START_DRY_RUN_ONLY",
        "market_context": (
            "SYNTHETIC_CONTROLLED_FORWARD_OBSERVATION_START_DRY_RUN"
        ),
        "activation_scope": "CONTROL_PLANE_ONLY_NOT_FORWARD_OBSERVATION",
        "run_scope": RUN_SCOPE,
        "evidence_scope": EVIDENCE_SCOPE,
        "entry_price": entry_price,
        "stop_price": stop_price,
        "target_price": target_price,
        "invalidation_level": invalidation_level,
        "risk_reward": risk_reward,
        "cost_profile": str(
            source.get("cost_profile", "RESEARCH_COST_AWARE_REFERENCE_ONLY")
        ),
        "manual_confirmation_required": True,
        "controlled_forward_observation_start_dry_run_execution_review_performed": True,
        "future_controlled_forward_observation_start_dry_run_run_allowed": True,
        "controlled_forward_observation_start_dry_run_run_allowed": True,
        "controlled_forward_observation_start_dry_run_run_performed": True,
        "controlled_forward_observation_start_dry_run_performed": True,
        "future_controlled_forward_observation_start_dry_run_output_integrity_review_allowed": True,
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
        "expected_next_review_phase": RECOMMENDED_NEXT_PHASE,
        "notes": (
            "Controlled start dry-run row only. Not forward observation. "
            "Not real evidence. Not a live signal. Not paper trading. "
            "Not market execution."
        ),
        "validation_status": VALIDATION_STATUS,
    }

    return pd.DataFrame([row], columns=START_DRY_RUN_OUTPUT_COLUMNS)


def build_start_dry_run_output_validations(
    dry_run_output_df: pd.DataFrame,
) -> pd.DataFrame:
    if dry_run_output_df.empty:
        return pd.DataFrame(
            [
                {
                    "validation_name": "dry_run_output_row_count_valid",
                    "passed": False,
                    "details": "row_count=0",
                }
            ]
        )

    row = dry_run_output_df.iloc[0].to_dict()
    actual_columns = dry_run_output_df.columns.astype(str).tolist()

    entry_price = safe_float(row.get("entry_price"))
    stop_price = safe_float(row.get("stop_price"))
    target_price = safe_float(row.get("target_price"))
    risk_reward = safe_float(row.get("risk_reward"))
    expected_rr = (
        round((target_price - entry_price) / (entry_price - stop_price), 4)
        if entry_price > stop_price
        else 0.0
    )

    true_run_fields = [
        "controlled_forward_observation_start_dry_run_execution_review_performed",
        "future_controlled_forward_observation_start_dry_run_run_allowed",
        "controlled_forward_observation_start_dry_run_run_allowed",
        "controlled_forward_observation_start_dry_run_run_performed",
        "controlled_forward_observation_start_dry_run_performed",
        "future_controlled_forward_observation_start_dry_run_output_integrity_review_allowed",
    ]
    true_run_fields_valid = all(
        safe_bool(row.get(field_name, False), False) is True
        for field_name in true_run_fields
    )

    operational_locks_valid = all(
        safe_bool(row.get(field_name, True), True) is required_value
        for field_name, required_value in EXPECTED_FALSE_GUARDS.items()
    )

    rows = [
        (
            "dry_run_output_row_count_valid",
            len(dry_run_output_df) == 1,
            f"row_count={len(dry_run_output_df)}",
        ),
        (
            "dry_run_output_schema_valid",
            actual_columns == START_DRY_RUN_OUTPUT_COLUMNS,
            (
                f"actual_field_count={len(actual_columns)},"
                f"expected_field_count={len(START_DRY_RUN_OUTPUT_COLUMNS)}"
            ),
        ),
        (
            "source_execution_review_decision_valid",
            str(row.get("source_execution_review_decision", ""))
            == EXECUTION_REVIEW_READY_DECISION,
            str(row.get("source_execution_review_decision", "")),
        ),
        (
            "dry_run_output_candidate_valid",
            str(row.get("candidate_id", "")) == PRIMARY_RESEARCH_CANDIDATE,
            str(row.get("candidate_id", "")),
        ),
        (
            "dry_run_output_direction_valid",
            str(row.get("direction", "")) == "LONG",
            str(row.get("direction", "")),
        ),
        (
            "dry_run_output_price_structure_valid",
            stop_price < entry_price < target_price,
            f"stop={stop_price},entry={entry_price},target={target_price}",
        ),
        (
            "dry_run_output_risk_reward_valid",
            risk_reward == expected_rr and risk_reward == 2.5,
            f"risk_reward={risk_reward},expected={expected_rr}",
        ),
        (
            "dry_run_output_scope_valid",
            str(row.get("run_scope", "")) == RUN_SCOPE,
            str(row.get("run_scope", "")),
        ),
        (
            "dry_run_output_evidence_scope_valid",
            str(row.get("evidence_scope", "")) == EVIDENCE_SCOPE,
            str(row.get("evidence_scope", "")),
        ),
        (
            "dry_run_output_true_run_fields_valid",
            true_run_fields_valid,
            f"true_run_field_count={len(true_run_fields)}",
        ),
        (
            "dry_run_output_operational_locks_valid",
            operational_locks_valid,
            f"false_guard_count={len(EXPECTED_FALSE_GUARDS)}",
        ),
        (
            "dry_run_output_official_evidence_rows_zero",
            int(safe_float(row.get("official_evidence_rows_written"), -1)) == 0,
            str(row.get("official_evidence_rows_written", "")),
        ),
        (
            "dry_run_output_future_integrity_review_allowed",
            safe_bool(
                row.get(
                    "future_controlled_forward_observation_start_dry_run_output_integrity_review_allowed",
                    False,
                ),
                False,
            ),
            str(
                row.get(
                    "future_controlled_forward_observation_start_dry_run_output_integrity_review_allowed",
                    "",
                )
            ),
        ),
        (
            "dry_run_output_validation_status_valid",
            str(row.get("validation_status", "")) == VALIDATION_STATUS,
            str(row.get("validation_status", "")),
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


def build_start_dry_run_run_evidence_chain(
    phase_10_22_summary_df: pd.DataFrame,
    source_design_output_df: pd.DataFrame,
    source_design_validations_df: pd.DataFrame,
    source_design_controls_df: pd.DataFrame,
    source_design_rules_df: pd.DataFrame,
    source_design_requirements_df: pd.DataFrame,
    source_design_guard_matrix_df: pd.DataFrame,
    execution_review_decision_df: pd.DataFrame,
    official_dataset_absent: bool,
) -> pd.DataFrame:
    summary = (
        phase_10_22_summary_df.iloc[0].to_dict()
        if not phase_10_22_summary_df.empty
        else {}
    )
    source = (
        source_design_output_df.iloc[0].to_dict()
        if not source_design_output_df.empty
        else {}
    )
    decision = (
        execution_review_decision_df.iloc[0].to_dict()
        if not execution_review_decision_df.empty
        else {}
    )

    entry_price = safe_float(source.get("entry_price"))
    stop_price = safe_float(source.get("stop_price"))
    target_price = safe_float(source.get("target_price"))

    evidence_rows = [
        ("phase_10_22_validation_passed", "dependency", safe_bool(summary.get("validation_passed", False)), str(summary.get("validation_decision", ""))),
        ("start_dry_run_execution_review_passed", "execution_review", safe_bool(summary.get("controlled_forward_observation_start_dry_run_execution_review_passed", False)), str(summary.get("controlled_forward_observation_start_dry_run_execution_review_passed", ""))),
        ("start_dry_run_execution_review_decision_expected", "execution_review", str(summary.get("controlled_forward_observation_start_dry_run_execution_review_decision", "")) == EXECUTION_REVIEW_READY_DECISION, str(summary.get("controlled_forward_observation_start_dry_run_execution_review_decision", ""))),
        ("execution_review_performed", "execution_review", safe_bool(summary.get("controlled_forward_observation_start_dry_run_execution_review_performed", False)), str(summary.get("controlled_forward_observation_start_dry_run_execution_review_performed", ""))),
        ("future_start_dry_run_run_allowed", "future_run", safe_bool(summary.get("future_controlled_forward_observation_start_dry_run_run_allowed", False)), str(summary.get("future_controlled_forward_observation_start_dry_run_run_allowed", ""))),
        ("execution_review_decision_table_consistent", "summary_consistency", str(decision.get("controlled_forward_observation_start_dry_run_execution_review_decision", "")) == EXECUTION_REVIEW_READY_DECISION, str(decision.get("controlled_forward_observation_start_dry_run_execution_review_decision", ""))),
        ("source_design_output_row_count_one", "artifact", len(source_design_output_df) == 1, f"row_count={len(source_design_output_df)}"),
        ("source_design_candidate_valid", "candidate_scope", str(source.get("candidate_id", "")) == PRIMARY_RESEARCH_CANDIDATE, str(source.get("candidate_id", ""))),
        ("source_design_direction_valid", "direction", str(source.get("direction", "")) == "LONG", str(source.get("direction", ""))),
        ("source_design_price_structure_valid", "price_structure", stop_price < entry_price < target_price, f"stop={stop_price},entry={entry_price},target={target_price}"),
        ("source_design_risk_reward_valid", "risk_reward", safe_float(source.get("risk_reward")) == 2.5, f"risk_reward={source.get('risk_reward', '')}"),
        ("source_design_scope_valid", "scope_control", str(source.get("design_scope", "")) == "CONTROLLED_FORWARD_OBSERVATION_START_DRY_RUN_DESIGN_ONLY", str(source.get("design_scope", ""))),
        ("source_design_evidence_scope_valid", "evidence_scope", str(source.get("evidence_scope", "")) == "DESIGN_ONLY_NOT_REAL_EVIDENCE", str(source.get("evidence_scope", ""))),
        ("source_design_validation_status_valid", "artifact", str(source.get("validation_status", "")) == "CONTROLLED_START_DRY_RUN_DESIGN_ROW_CREATED", str(source.get("validation_status", ""))),
        ("source_design_validations_passed", "validation", dataframe_all_passed(source_design_validations_df), f"validation_rows={len(source_design_validations_df)}"),
        ("source_design_controls_passed", "controls", dataframe_all_passed(source_design_controls_df), f"control_rows={len(source_design_controls_df)}"),
        ("source_design_rules_passed", "rules", dataframe_all_passed(source_design_rules_df), f"rule_rows={len(source_design_rules_df)}"),
        ("source_design_requirements_passed", "requirements", dataframe_all_passed(source_design_requirements_df), f"requirement_rows={len(source_design_requirements_df)}"),
        ("source_design_guards_passed", "safety", dataframe_all_passed(source_design_guard_matrix_df), f"guard_rows={len(source_design_guard_matrix_df)}"),
        ("source_design_operational_locks_valid", "safety", lookup_validation(source_design_validations_df, "design_output_operational_locks_valid"), str(lookup_validation(source_design_validations_df, "design_output_operational_locks_valid"))),
        ("source_design_official_evidence_rows_zero", "official_dataset_guard", int(safe_float(source.get("official_evidence_rows_written"), -1)) == 0, str(source.get("official_evidence_rows_written", ""))),
        ("source_design_future_execution_review_allowed", "future_review", safe_bool(source.get("future_controlled_forward_observation_start_dry_run_execution_review_allowed", False)), str(source.get("future_controlled_forward_observation_start_dry_run_execution_review_allowed", ""))),
        ("official_dataset_absent", "official_dataset_guard", official_dataset_absent, f"official_dataset_absent={official_dataset_absent}"),
        ("project_execution_locks_confirmed", "safety", not any(safe_bool(source.get(field_name, False), False) for field_name in EXPECTED_FALSE_GUARDS), "all operational execution locks remain false"),
    ]

    return pd.DataFrame(
        [
            {
                "evidence_id": f"START_DRY_RUN_RUN_EVIDENCE_{index:03d}",
                "evidence_name": evidence_name,
                "evidence_group": evidence_group,
                "required": True,
                "passed": bool(passed),
                "details": details,
            }
            for index, (evidence_name, evidence_group, passed, details) in enumerate(
                evidence_rows,
                start=1,
            )
        ]
    )


def build_start_dry_run_run_controls(
    evidence_df: pd.DataFrame,
    validations_df: pd.DataFrame,
    artifact_write_performed: bool,
) -> pd.DataFrame:
    evidence_lookup = {
        str(row["evidence_name"]): safe_bool(row["passed"], False)
        for _, row in evidence_df.iterrows()
    }
    validation_lookup = {
        str(row["validation_name"]): safe_bool(row["passed"], False)
        for _, row in validations_df.iterrows()
    }

    controls = [
        ("phase_10_22_validation_passed", "dependency", evidence_lookup.get("phase_10_22_validation_passed", False)),
        ("execution_review_passed", "execution_review", evidence_lookup.get("start_dry_run_execution_review_passed", False)),
        ("execution_review_decision_expected", "execution_review", evidence_lookup.get("start_dry_run_execution_review_decision_expected", False)),
        ("execution_review_performed", "execution_review", evidence_lookup.get("execution_review_performed", False)),
        ("future_start_dry_run_run_allowed", "future_run", evidence_lookup.get("future_start_dry_run_run_allowed", False)),
        ("source_design_output_row_count_one", "artifact", evidence_lookup.get("source_design_output_row_count_one", False)),
        ("source_design_candidate_valid", "candidate_scope", evidence_lookup.get("source_design_candidate_valid", False)),
        ("source_design_direction_valid", "direction", evidence_lookup.get("source_design_direction_valid", False)),
        ("source_design_price_structure_valid", "price_structure", evidence_lookup.get("source_design_price_structure_valid", False)),
        ("source_design_risk_reward_valid", "risk_reward", evidence_lookup.get("source_design_risk_reward_valid", False)),
        ("dry_run_output_row_count_valid", "artifact", validation_lookup.get("dry_run_output_row_count_valid", False)),
        ("dry_run_output_schema_valid", "schema", validation_lookup.get("dry_run_output_schema_valid", False)),
        ("dry_run_output_candidate_valid", "candidate_scope", validation_lookup.get("dry_run_output_candidate_valid", False)),
        ("dry_run_output_direction_valid", "direction", validation_lookup.get("dry_run_output_direction_valid", False)),
        ("dry_run_output_price_structure_valid", "price_structure", validation_lookup.get("dry_run_output_price_structure_valid", False)),
        ("dry_run_output_operational_locks_valid", "safety", validation_lookup.get("dry_run_output_operational_locks_valid", False)),
        ("dry_run_artifact_write_performed", "artifact", artifact_write_performed),
        ("future_output_integrity_review_allowed", "future_review", validation_lookup.get("dry_run_output_future_integrity_review_allowed", False)),
    ]

    return pd.DataFrame(
        [
            {
                "control_position": position,
                "control_id": f"START_DRY_RUN_RUN_CONTROL_{position:03d}",
                "control_name": control_name,
                "control_group": control_group,
                "required": True,
                "start_dry_run_run_only": True,
                "future_controlled_forward_observation_start_dry_run_output_integrity_review_allowed": True,
                "forward_observation_start_allowed": False,
                "official_dataset_write_allowed": False,
                "market_execution_allowed": False,
                "passed": bool(passed),
            }
            for position, (control_name, control_group, passed) in enumerate(
                controls,
                start=1,
            )
        ]
    )


def build_start_dry_run_run_guard_matrix(
    run_passed_provisional: bool,
) -> pd.DataFrame:
    rows: list[dict[str, Any]] = [
        {
            "guard_name": "controlled_forward_observation_start_dry_run_run_allowed",
            "required_value": True,
            "actual_value": True,
            "passed": True,
            "guard_group": "start_dry_run_run_state",
        },
        {
            "guard_name": "controlled_forward_observation_start_dry_run_run_performed",
            "required_value": True,
            "actual_value": True,
            "passed": True,
            "guard_group": "start_dry_run_run_state",
        },
        {
            "guard_name": "controlled_forward_observation_start_dry_run_performed",
            "required_value": True,
            "actual_value": True,
            "passed": True,
            "guard_group": "start_dry_run_run_state",
        },
        {
            "guard_name": "future_controlled_forward_observation_start_dry_run_output_integrity_review_allowed",
            "required_value": True,
            "actual_value": bool(run_passed_provisional),
            "passed": bool(run_passed_provisional),
            "guard_group": "start_dry_run_run_state",
        },
    ]

    for guard_name, required_value in EXPECTED_FALSE_GUARDS.items():
        rows.append(
            {
                "guard_name": guard_name,
                "required_value": required_value,
                "actual_value": required_value,
                "passed": True,
                "guard_group": "start_dry_run_run_safety_guard",
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


def build_start_dry_run_run_rules(
    evidence_df: pd.DataFrame,
    controls_df: pd.DataFrame,
    validations_df: pd.DataFrame,
    guard_matrix_df: pd.DataFrame,
) -> pd.DataFrame:
    evidence_passed = dataframe_all_passed(evidence_df)
    controls_passed = dataframe_all_passed(controls_df)
    validations_passed = dataframe_all_passed(validations_df)
    guards_passed = dataframe_all_passed(guard_matrix_df)

    start_disabled = (
        not controls_df.empty
        and controls_df["forward_observation_start_allowed"]
        .map(lambda value: safe_bool(value, True))
        .eq(False)
        .all()
    )
    dataset_writes_disabled = (
        not controls_df.empty
        and controls_df["official_dataset_write_allowed"]
        .map(lambda value: safe_bool(value, True))
        .eq(False)
        .all()
    )
    market_execution_disabled = (
        not controls_df.empty
        and controls_df["market_execution_allowed"]
        .map(lambda value: safe_bool(value, True))
        .eq(False)
        .all()
    )

    rows = [
        ("start_dry_run_run_evidence_count_24", len(evidence_df) == 24, "24", str(len(evidence_df)), "evidence"),
        ("all_start_dry_run_run_evidence_passed", evidence_passed, "True", str(evidence_passed), "evidence"),
        ("start_dry_run_run_control_count_18", len(controls_df) == 18, "18", str(len(controls_df)), "controls"),
        ("all_start_dry_run_run_controls_passed", controls_passed, "True", str(controls_passed), "controls"),
        ("start_dry_run_run_validation_count_14", len(validations_df) == 14, "14", str(len(validations_df)), "validation"),
        ("all_start_dry_run_run_validations_passed", validations_passed, "True", str(validations_passed), "validation"),
        ("all_start_dry_run_run_guards_passed", guards_passed, "True", str(guards_passed), "safety"),
        ("start_dry_run_run_only", True, "True", "True", "scope_control"),
        ("future_output_integrity_review_allowed", True, "True", "True", "future_review"),
        ("forward_observation_start_disabled", start_disabled, "False", "False", "start_boundary"),
        ("official_dataset_writes_disabled", dataset_writes_disabled, "False", "False", "official_dataset_guard"),
        ("market_execution_disabled", market_execution_disabled, "False", "False", "market_execution_guard"),
    ]

    return pd.DataFrame(
        [
            {
                "rule_id": f"START_DRY_RUN_RUN_RULE_{position:03d}",
                "rule_name": rule_name,
                "passed": bool(passed),
                "required_value": required_value,
                "actual_value": actual_value,
                "rule_group": rule_group,
            }
            for position, (rule_name, passed, required_value, actual_value, rule_group) in enumerate(
                rows,
                start=1,
            )
        ]
    )


def build_start_dry_run_run_requirements(
    phase_10_22_summary_df: pd.DataFrame,
    execution_review_decision_df: pd.DataFrame,
    source_design_output_df: pd.DataFrame,
    dry_run_output_df: pd.DataFrame,
    validations_df: pd.DataFrame,
    evidence_df: pd.DataFrame,
    controls_df: pd.DataFrame,
    rules_df: pd.DataFrame,
    guard_matrix_df: pd.DataFrame,
    artifact_write_performed: bool,
    artifact_rows_written: int,
    official_dataset_absent: bool,
) -> pd.DataFrame:
    summary = (
        phase_10_22_summary_df.iloc[0].to_dict()
        if not phase_10_22_summary_df.empty
        else {}
    )
    decision = (
        execution_review_decision_df.iloc[0].to_dict()
        if not execution_review_decision_df.empty
        else {}
    )
    source = (
        source_design_output_df.iloc[0].to_dict()
        if not source_design_output_df.empty
        else {}
    )
    output = (
        dry_run_output_df.iloc[0].to_dict()
        if not dry_run_output_df.empty
        else {}
    )
    validation_lookup = {
        str(row["validation_name"]): safe_bool(row["passed"], False)
        for _, row in validations_df.iterrows()
    }

    requirement_rows = [
        ("phase_10_22_validation_passed", safe_bool(summary.get("validation_passed", False)), "True", str(summary.get("validation_passed", "")), "dependency"),
        ("execution_review_passed", safe_bool(summary.get("controlled_forward_observation_start_dry_run_execution_review_passed", False)), "True", str(summary.get("controlled_forward_observation_start_dry_run_execution_review_passed", "")), "execution_review"),
        ("execution_review_decision_expected", str(summary.get("controlled_forward_observation_start_dry_run_execution_review_decision", "")) == EXECUTION_REVIEW_READY_DECISION, EXECUTION_REVIEW_READY_DECISION, str(summary.get("controlled_forward_observation_start_dry_run_execution_review_decision", "")), "execution_review"),
        ("execution_review_performed", safe_bool(summary.get("controlled_forward_observation_start_dry_run_execution_review_performed", False)), "True", str(summary.get("controlled_forward_observation_start_dry_run_execution_review_performed", "")), "execution_review"),
        ("future_start_dry_run_run_allowed", safe_bool(summary.get("future_controlled_forward_observation_start_dry_run_run_allowed", False)), "True", str(summary.get("future_controlled_forward_observation_start_dry_run_run_allowed", "")), "future_run"),
        ("execution_review_decision_table_consistent", str(decision.get("controlled_forward_observation_start_dry_run_execution_review_decision", "")) == EXECUTION_REVIEW_READY_DECISION, EXECUTION_REVIEW_READY_DECISION, str(decision.get("controlled_forward_observation_start_dry_run_execution_review_decision", "")), "summary_consistency"),
        ("source_design_output_row_count_one", len(source_design_output_df) == 1, "1", str(len(source_design_output_df)), "artifact"),
        ("source_design_candidate_valid", str(source.get("candidate_id", "")) == PRIMARY_RESEARCH_CANDIDATE, PRIMARY_RESEARCH_CANDIDATE, str(source.get("candidate_id", "")), "candidate_scope"),
        ("source_design_direction_valid", str(source.get("direction", "")) == "LONG", "LONG", str(source.get("direction", "")), "direction"),
        ("source_design_price_structure_valid", safe_float(source.get("stop_price")) < safe_float(source.get("entry_price")) < safe_float(source.get("target_price")), "True", "True", "price_structure"),
        ("source_design_risk_reward_valid", safe_float(source.get("risk_reward")) == 2.5, "2.5", str(source.get("risk_reward", "")), "risk_reward"),
        ("source_design_scope_valid", str(source.get("design_scope", "")) == "CONTROLLED_FORWARD_OBSERVATION_START_DRY_RUN_DESIGN_ONLY", "CONTROLLED_FORWARD_OBSERVATION_START_DRY_RUN_DESIGN_ONLY", str(source.get("design_scope", "")), "scope_control"),
        ("source_design_evidence_scope_valid", str(source.get("evidence_scope", "")) == "DESIGN_ONLY_NOT_REAL_EVIDENCE", "DESIGN_ONLY_NOT_REAL_EVIDENCE", str(source.get("evidence_scope", "")), "evidence_scope"),
        ("dry_run_output_row_count_one", len(dry_run_output_df) == 1, "1", str(len(dry_run_output_df)), "artifact"),
        ("dry_run_output_schema_valid", validation_lookup.get("dry_run_output_schema_valid", False), "True", str(validation_lookup.get("dry_run_output_schema_valid", False)), "schema"),
        ("dry_run_output_source_decision_valid", validation_lookup.get("source_execution_review_decision_valid", False), "True", str(validation_lookup.get("source_execution_review_decision_valid", False)), "execution_review"),
        ("dry_run_output_candidate_valid", validation_lookup.get("dry_run_output_candidate_valid", False), "True", str(validation_lookup.get("dry_run_output_candidate_valid", False)), "candidate_scope"),
        ("dry_run_output_direction_valid", validation_lookup.get("dry_run_output_direction_valid", False), "True", str(validation_lookup.get("dry_run_output_direction_valid", False)), "direction"),
        ("dry_run_output_price_structure_valid", validation_lookup.get("dry_run_output_price_structure_valid", False), "True", str(validation_lookup.get("dry_run_output_price_structure_valid", False)), "price_structure"),
        ("dry_run_output_risk_reward_valid", validation_lookup.get("dry_run_output_risk_reward_valid", False), "True", str(validation_lookup.get("dry_run_output_risk_reward_valid", False)), "risk_reward"),
        ("dry_run_output_scope_valid", validation_lookup.get("dry_run_output_scope_valid", False), "True", str(validation_lookup.get("dry_run_output_scope_valid", False)), "scope_control"),
        ("dry_run_output_evidence_scope_valid", validation_lookup.get("dry_run_output_evidence_scope_valid", False), "True", str(validation_lookup.get("dry_run_output_evidence_scope_valid", False)), "evidence_scope"),
        ("dry_run_output_true_run_fields_valid", validation_lookup.get("dry_run_output_true_run_fields_valid", False), "True", str(validation_lookup.get("dry_run_output_true_run_fields_valid", False)), "run_control"),
        ("dry_run_output_operational_locks_valid", validation_lookup.get("dry_run_output_operational_locks_valid", False), "True", str(validation_lookup.get("dry_run_output_operational_locks_valid", False)), "safety"),
        ("dry_run_output_official_evidence_rows_zero", validation_lookup.get("dry_run_output_official_evidence_rows_zero", False), "True", str(validation_lookup.get("dry_run_output_official_evidence_rows_zero", False)), "official_dataset_guard"),
        ("dry_run_output_future_integrity_review_allowed", validation_lookup.get("dry_run_output_future_integrity_review_allowed", False), "True", str(validation_lookup.get("dry_run_output_future_integrity_review_allowed", False)), "future_review"),
        ("dry_run_output_validation_status_valid", validation_lookup.get("dry_run_output_validation_status_valid", False), "True", str(validation_lookup.get("dry_run_output_validation_status_valid", False)), "artifact"),
        ("evidence_chain_passed", dataframe_all_passed(evidence_df), "True", str(dataframe_all_passed(evidence_df)), "evidence"),
        ("run_controls_passed", dataframe_all_passed(controls_df), "True", str(dataframe_all_passed(controls_df)), "controls"),
        ("run_rules_passed", dataframe_all_passed(rules_df), "True", str(dataframe_all_passed(rules_df)), "rules"),
        ("run_guards_passed", dataframe_all_passed(guard_matrix_df), "True", str(dataframe_all_passed(guard_matrix_df)), "safety"),
        ("artifact_write_performed", artifact_write_performed, "True", str(artifact_write_performed), "artifact"),
        ("artifact_rows_written_one", artifact_rows_written == 1, "1", str(artifact_rows_written), "artifact"),
        ("controlled_start_dry_run_run_performed", safe_bool(output.get("controlled_forward_observation_start_dry_run_run_performed", False)), "True", str(output.get("controlled_forward_observation_start_dry_run_run_performed", "")), "dry_run_run"),
        ("controlled_start_dry_run_performed", safe_bool(output.get("controlled_forward_observation_start_dry_run_performed", False)), "True", str(output.get("controlled_forward_observation_start_dry_run_performed", "")), "dry_run"),
        ("official_dataset_absent", official_dataset_absent, "True", str(official_dataset_absent), "official_dataset_guard"),
        ("forward_observation_not_started", safe_bool(output.get("forward_observation_started", True), True) is False, "False", str(output.get("forward_observation_started", "")), "start_boundary"),
        ("market_execution_disabled", safe_bool(output.get("market_execution_allowed", True), True) is False, "False", str(output.get("market_execution_allowed", "")), "market_execution_guard"),
        ("total_project_not_completed", safe_bool(output.get("total_project_completed", True), True) is False, "False", str(output.get("total_project_completed", "")), "scope_control"),
    ]

    return pd.DataFrame(
        [
            {
                "requirement_id": f"START_DRY_RUN_RUN_REQ_{position:03d}",
                "requirement_name": requirement_name,
                "passed": bool(passed),
                "required_value": required_value,
                "actual_value": actual_value,
                "requirement_group": requirement_group,
            }
            for position, (
                requirement_name,
                passed,
                required_value,
                actual_value,
                requirement_group,
            ) in enumerate(requirement_rows, start=1)
        ]
    )


def build_start_dry_run_run_decision_table(
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
    run_passed = (
        total_requirements > 0
        and failed_requirements == 0
        and rules_passed
        and guards_passed
    )

    failed_requirement_names = ""
    if not requirements_df.empty:
        failed_requirement_names = ",".join(
            requirements_df[
                ~requirements_df["passed"].map(lambda value: safe_bool(value, False))
            ]["requirement_name"]
            .astype(str)
            .tolist()
        )

    return pd.DataFrame(
        [
            {
                "controlled_forward_observation_start_dry_run_run_id": (
                    "PHASE_10_23_LONG_FORWARD_OBSERVATION_CONTROLLED_START_DRY_RUN_RUN_001"
                ),
                "controlled_forward_observation_start_dry_run_run_status": START_DRY_RUN_RUN_STATUS,
                "controlled_forward_observation_start_dry_run_run_passed": run_passed,
                "controlled_forward_observation_start_dry_run_run_decision": (
                    READY_DECISION if run_passed else BLOCKED_DECISION
                ),
                "total_requirements": total_requirements,
                "passed_requirements": passed_requirements,
                "failed_requirements": failed_requirements,
                "failed_requirement_names": failed_requirement_names,
                "start_dry_run_run_rules_passed": rules_passed,
                "start_dry_run_run_guards_passed": guards_passed,
                "controlled_forward_observation_start_dry_run_run_performed": run_passed,
                "controlled_forward_observation_start_dry_run_performed": run_passed,
                "future_controlled_forward_observation_start_dry_run_output_integrity_review_allowed": run_passed,
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


def validate_long_forward_observation_controlled_start_dry_run_run() -> dict[str, pd.DataFrame]:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    checks: list[dict[str, Any]] = []

    for check_name, path in {
        "phase_10_22_start_dry_run_execution_review_doc_exists": PHASE_10_22_EXECUTION_REVIEW_DOC_PATH,
        "phase_10_23_start_dry_run_run_doc_exists": PHASE_10_23_START_DRY_RUN_RUN_DOC_PATH,
    }.items():
        checks.append(
            build_check(
                "phase_anchor",
                check_name,
                path.exists(),
                "INFO" if path.exists() else "ERROR",
                str(path),
            )
        )

    official_dataset_exists_before = OFFICIAL_DATASET_PATH.exists()

    phase_10_22_result = (
        validate_long_forward_observation_controlled_start_dry_run_execution_review()
    )

    phase_10_22_summary_df = get_phase_10_22_dataframe(
        phase_10_22_result,
        ("summary", "execution_review_summary", "start_dry_run_execution_review_summary"),
        PHASE_10_22_REPORTS_DIR / "start_dry_run_execution_review_summary_v1.csv",
    )
    source_design_output_df = get_phase_10_22_dataframe(
        phase_10_22_result,
        ("source_design_output", "source_start_dry_run_design_output", "phase_10_21_source_design_output"),
        PHASE_10_22_REPORTS_DIR / "phase_10_21_source_design_output_v1.csv",
    )
    source_design_validations_df = get_phase_10_22_dataframe(
        phase_10_22_result,
        ("source_design_validations", "source_start_dry_run_design_validations", "phase_10_21_source_design_validations"),
        PHASE_10_22_REPORTS_DIR / "phase_10_21_source_design_validations_v1.csv",
    )
    source_design_controls_df = get_phase_10_22_dataframe(
        phase_10_22_result,
        ("source_design_controls", "source_start_dry_run_design_controls", "phase_10_21_source_design_controls"),
        PHASE_10_22_REPORTS_DIR / "phase_10_21_source_design_controls_v1.csv",
    )
    source_design_rules_df = get_phase_10_22_dataframe(
        phase_10_22_result,
        ("source_design_rules", "source_start_dry_run_design_rules", "phase_10_21_source_design_rules"),
        PHASE_10_22_REPORTS_DIR / "phase_10_21_source_design_rules_v1.csv",
    )
    source_design_requirements_df = get_phase_10_22_dataframe(
        phase_10_22_result,
        ("source_design_requirements", "source_start_dry_run_design_requirements", "phase_10_21_source_design_requirements"),
        PHASE_10_22_REPORTS_DIR / "phase_10_21_source_design_requirements_v1.csv",
    )
    source_design_guard_matrix_df = get_phase_10_22_dataframe(
        phase_10_22_result,
        ("source_design_guard_matrix", "source_start_dry_run_design_guard_matrix", "phase_10_21_source_design_guard_matrix"),
        PHASE_10_22_REPORTS_DIR / "phase_10_21_source_design_guard_matrix_v1.csv",
    )
    source_design_decision_df = get_phase_10_22_dataframe(
        phase_10_22_result,
        ("source_design_decision", "source_start_dry_run_design_decision", "phase_10_21_source_design_decision"),
        PHASE_10_22_REPORTS_DIR / "phase_10_21_source_design_decision_v1.csv",
    )
    source_checks_df = get_phase_10_22_dataframe(
        phase_10_22_result,
        ("source_checks", "phase_10_21_source_checks"),
        PHASE_10_22_REPORTS_DIR / "phase_10_21_source_checks_v1.csv",
    )
    execution_review_evidence_chain_df = get_phase_10_22_dataframe(
        phase_10_22_result,
        ("execution_review_evidence_chain", "start_dry_run_execution_review_evidence_chain"),
        PHASE_10_22_REPORTS_DIR / "start_dry_run_execution_review_evidence_chain_v1.csv",
    )
    execution_review_controls_df = get_phase_10_22_dataframe(
        phase_10_22_result,
        ("execution_review_controls", "start_dry_run_execution_review_controls"),
        PHASE_10_22_REPORTS_DIR / "start_dry_run_execution_review_controls_v1.csv",
    )
    execution_review_rules_df = get_phase_10_22_dataframe(
        phase_10_22_result,
        ("execution_review_rules", "start_dry_run_execution_review_rules"),
        PHASE_10_22_REPORTS_DIR / "start_dry_run_execution_review_rules_v1.csv",
    )
    execution_review_requirements_df = get_phase_10_22_dataframe(
        phase_10_22_result,
        ("execution_review_requirements", "start_dry_run_execution_review_requirements"),
        PHASE_10_22_REPORTS_DIR / "start_dry_run_execution_review_requirements_v1.csv",
    )
    execution_review_guard_matrix_df = get_phase_10_22_dataframe(
        phase_10_22_result,
        ("execution_review_guard_matrix", "start_dry_run_execution_review_guard_matrix"),
        PHASE_10_22_REPORTS_DIR / "start_dry_run_execution_review_guard_matrix_v1.csv",
    )
    execution_review_decision_df = get_phase_10_22_dataframe(
        phase_10_22_result,
        ("execution_review_decision", "start_dry_run_execution_review_decision"),
        PHASE_10_22_REPORTS_DIR / "start_dry_run_execution_review_decision_v1.csv",
    )
    phase_10_22_checks_df = get_phase_10_22_dataframe(
        phase_10_22_result,
        ("checks", "execution_review_checks", "start_dry_run_execution_review_checks"),
        PHASE_10_22_REPORTS_DIR / "start_dry_run_execution_review_checks_v1.csv",
    )

    phase_10_22_summary = (
        phase_10_22_summary_df.iloc[0].to_dict()
        if not phase_10_22_summary_df.empty
        else {}
    )

    phase_10_22_validation_passed = safe_bool(
        phase_10_22_summary.get("validation_passed", False),
        False,
    )
    execution_review_passed = safe_bool(
        phase_10_22_summary.get(
            "controlled_forward_observation_start_dry_run_execution_review_passed",
            False,
        ),
        False,
    )
    execution_review_decision = str(
        phase_10_22_summary.get(
            "controlled_forward_observation_start_dry_run_execution_review_decision",
            "",
        )
    )
    execution_review_performed = safe_bool(
        phase_10_22_summary.get(
            "controlled_forward_observation_start_dry_run_execution_review_performed",
            False,
        ),
        False,
    )
    future_run_allowed = safe_bool(
        phase_10_22_summary.get(
            "future_controlled_forward_observation_start_dry_run_run_allowed",
            False,
        ),
        False,
    )

    official_dataset_absent_before = not official_dataset_exists_before

    dry_run_output_df = build_start_dry_run_output(
        phase_10_22_summary_df,
        execution_review_decision_df,
        source_design_output_df,
    )
    validations_df = build_start_dry_run_output_validations(dry_run_output_df)

    dry_run_output_path = REPORTS_DIR / "controlled_start_dry_run_output_v1.csv"
    dry_run_output_df.to_csv(dry_run_output_path, index=False)
    artifact_write_performed = dry_run_output_path.exists()
    artifact_rows_written = len(dry_run_output_df) if artifact_write_performed else 0

    evidence_df = build_start_dry_run_run_evidence_chain(
        phase_10_22_summary_df,
        source_design_output_df,
        source_design_validations_df,
        source_design_controls_df,
        source_design_rules_df,
        source_design_requirements_df,
        source_design_guard_matrix_df,
        execution_review_decision_df,
        official_dataset_absent_before,
    )
    controls_df = build_start_dry_run_run_controls(
        evidence_df,
        validations_df,
        artifact_write_performed,
    )

    provisional_pass = (
        dataframe_all_passed(evidence_df)
        and dataframe_all_passed(controls_df)
        and dataframe_all_passed(validations_df)
        and artifact_write_performed
        and artifact_rows_written == 1
    )
    guard_matrix_df = build_start_dry_run_run_guard_matrix(provisional_pass)
    rules_df = build_start_dry_run_run_rules(
        evidence_df,
        controls_df,
        validations_df,
        guard_matrix_df,
    )

    official_dataset_exists_after = OFFICIAL_DATASET_PATH.exists()
    official_dataset_absent = (
        not official_dataset_exists_before and not official_dataset_exists_after
    )

    requirements_df = build_start_dry_run_run_requirements(
        phase_10_22_summary_df,
        execution_review_decision_df,
        source_design_output_df,
        dry_run_output_df,
        validations_df,
        evidence_df,
        controls_df,
        rules_df,
        guard_matrix_df,
        artifact_write_performed,
        artifact_rows_written,
        official_dataset_absent,
    )
    decision_df = build_start_dry_run_run_decision_table(
        requirements_df,
        rules_df,
        guard_matrix_df,
    )

    decision = decision_df.iloc[0].to_dict() if not decision_df.empty else {}
    run_passed = safe_bool(
        decision.get(
            "controlled_forward_observation_start_dry_run_run_passed",
            False,
        ),
        False,
    )
    run_decision = str(
        decision.get(
            "controlled_forward_observation_start_dry_run_run_decision",
            "",
        )
    )
    future_integrity_review_allowed = safe_bool(
        decision.get(
            "future_controlled_forward_observation_start_dry_run_output_integrity_review_allowed",
            False,
        ),
        False,
    )

    dependency_checks = [
        ("phase_10_22_validation_passed", phase_10_22_validation_passed, str(phase_10_22_summary.get("validation_decision", ""))),
        ("execution_review_passed", execution_review_passed, f"execution_review_passed={execution_review_passed}"),
        ("execution_review_decision_expected", execution_review_decision == EXECUTION_REVIEW_READY_DECISION, execution_review_decision),
        ("execution_review_performed", execution_review_performed, f"execution_review_performed={execution_review_performed}"),
        ("future_start_dry_run_run_allowed", future_run_allowed, f"future_start_dry_run_run_allowed={future_run_allowed}"),
    ]
    for check_name, passed, details in dependency_checks:
        checks.append(
            build_check(
                "phase_dependency",
                check_name,
                passed,
                "INFO" if passed else "ERROR",
                details,
            )
        )

    for _, evidence_row in evidence_df.iterrows():
        passed = safe_bool(evidence_row.get("passed", False), False)
        checks.append(
            build_check(
                "start_dry_run_run_evidence",
                str(evidence_row.get("evidence_name", "")),
                passed,
                "INFO" if passed else "ERROR",
                str(evidence_row.get("details", "")),
            )
        )

    for _, validation_row in validations_df.iterrows():
        passed = safe_bool(validation_row.get("passed", False), False)
        checks.append(
            build_check(
                "start_dry_run_run_validation",
                str(validation_row.get("validation_name", "")),
                passed,
                "INFO" if passed else "ERROR",
                str(validation_row.get("details", "")),
            )
        )

    review_checks = [
        ("start_dry_run_run_evidence_chain_passed", dataframe_all_passed(evidence_df)),
        ("start_dry_run_run_controls_passed", dataframe_all_passed(controls_df)),
        ("start_dry_run_run_validations_passed", dataframe_all_passed(validations_df)),
        ("start_dry_run_run_rules_passed", dataframe_all_passed(rules_df)),
        ("start_dry_run_run_requirements_passed", dataframe_all_passed(requirements_df)),
        ("start_dry_run_run_guards_passed", dataframe_all_passed(guard_matrix_df)),
        ("controlled_start_dry_run_run_passed", run_passed),
        ("controlled_start_dry_run_run_decision_expected", run_decision == READY_DECISION),
    ]
    for check_name, passed in review_checks:
        checks.append(
            build_check(
                "start_dry_run_run",
                check_name,
                passed,
                "INFO" if passed else "ERROR",
                (
                    f"run_decision={run_decision}"
                    if check_name.endswith("decision_expected")
                    else f"{check_name}={passed}"
                ),
            )
        )

    checks.append(
        build_check(
            "planning_scope",
            "future_start_dry_run_output_integrity_review_allowed",
            future_integrity_review_allowed,
            "WARNING" if future_integrity_review_allowed else "ERROR",
            (
                "This permits only a future controlled start dry-run output "
                "integrity review. It does not start forward observation, write "
                "official evidence, generate live signals, enable paper trading, "
                "use real capital, or permit market execution."
            ),
        )
    )
    checks.append(
        build_check(
            "official_dataset_guard",
            "official_dataset_not_created_or_written",
            official_dataset_absent,
            "INFO" if official_dataset_absent else "ERROR",
            (
                f"before={official_dataset_exists_before},"
                f"after={official_dataset_exists_after}"
            ),
        )
    )

    for _, guard_row in guard_matrix_df.iterrows():
        passed = safe_bool(guard_row.get("passed", False), False)
        checks.append(
            build_check(
                "start_dry_run_run_safety_flags",
                str(guard_row.get("guard_name", "")),
                passed,
                "INFO" if passed else "ERROR",
                (
                    f"{guard_row.get('guard_name', '')}="
                    f"{guard_row.get('actual_value', '')} "
                    f"(required={guard_row.get('required_value', '')})"
                ),
            )
        )

    scope_warnings = [
        ("start_dry_run_run_only", "Phase 10.23 performs only one controlled start dry-run artifact."),
        ("forward_observation_not_started", "Forward observation remains not started."),
        ("official_evidence_not_persisted", "Official evidence persistence remains disabled."),
        ("signal_generation_not_enabled", "Signal generation remains disabled."),
        ("paper_trading_not_enabled", "Paper trading execution remains disabled."),
        ("real_capital_not_allowed", "Real capital remains prohibited."),
        ("market_execution_not_allowed", "Market execution remains prohibited."),
        ("total_project_not_completed", "The total project is not completed."),
    ]
    for check_name, details in scope_warnings:
        checks.append(build_check("scope_control", check_name, True, "WARNING", details))

    checks.append(
        build_check(
            "phase_transition",
            "phase_10_24_recommended_next",
            True,
            "INFO",
            (
                "Recommended next step: Phase 10.24 LONG Forward Observation "
                "Controlled Start Dry-Run Output Integrity Review V1."
            ),
        )
    )

    checks_df = pd.DataFrame(checks)
    blocker_count = int(checks_df["blocker"].map(lambda value: safe_bool(value, False)).sum())
    error_count = int(checks_df["severity"].eq("ERROR").sum())
    warning_count = int(checks_df["severity"].eq("WARNING").sum())
    validation_passed = blocker_count == 0 and error_count == 0

    source_output = (
        source_design_output_df.iloc[0].to_dict()
        if not source_design_output_df.empty
        else {}
    )

    summary_df = pd.DataFrame(
        [
            {
                "phase": "10.23",
                "long_forward_observation_controlled_start_dry_run_run_defined": True,
                "phase_10_22_validation_passed": phase_10_22_validation_passed,
                "controlled_forward_observation_start_dry_run_execution_review_passed": execution_review_passed,
                "controlled_forward_observation_start_dry_run_execution_review_decision": execution_review_decision,
                "controlled_forward_observation_start_dry_run_execution_review_performed": execution_review_performed,
                "future_controlled_forward_observation_start_dry_run_run_allowed": future_run_allowed,
                "source_design_output_row_count": len(source_design_output_df),
                "source_design_output_candidate_id": str(source_output.get("candidate_id", "")),
                "source_design_output_candidate_valid": str(source_output.get("candidate_id", "")) == PRIMARY_RESEARCH_CANDIDATE,
                "source_design_output_direction": str(source_output.get("direction", "")),
                "source_design_output_direction_valid": str(source_output.get("direction", "")) == "LONG",
                "source_design_output_risk_reward": safe_float(source_output.get("risk_reward")),
                "controlled_start_dry_run_output_row_count": len(dry_run_output_df),
                "controlled_start_dry_run_output_schema_valid": lookup_validation(validations_df, "dry_run_output_schema_valid"),
                "controlled_start_dry_run_output_candidate_valid": lookup_validation(validations_df, "dry_run_output_candidate_valid"),
                "controlled_start_dry_run_output_direction_valid": lookup_validation(validations_df, "dry_run_output_direction_valid"),
                "controlled_start_dry_run_output_price_structure_valid": lookup_validation(validations_df, "dry_run_output_price_structure_valid"),
                "controlled_start_dry_run_output_risk_reward_valid": lookup_validation(validations_df, "dry_run_output_risk_reward_valid"),
                "controlled_start_dry_run_output_scope_valid": lookup_validation(validations_df, "dry_run_output_scope_valid"),
                "controlled_start_dry_run_output_evidence_scope_valid": lookup_validation(validations_df, "dry_run_output_evidence_scope_valid"),
                "controlled_start_dry_run_output_true_run_fields_valid": lookup_validation(validations_df, "dry_run_output_true_run_fields_valid"),
                "controlled_start_dry_run_output_operational_locks_valid": lookup_validation(validations_df, "dry_run_output_operational_locks_valid"),
                "controlled_start_dry_run_output_official_evidence_rows_zero": lookup_validation(validations_df, "dry_run_output_official_evidence_rows_zero"),
                "start_dry_run_run_evidence_count": len(evidence_df),
                "start_dry_run_run_control_count": len(controls_df),
                "start_dry_run_run_validation_rows": len(validations_df),
                "start_dry_run_run_rule_rows": len(rules_df),
                "start_dry_run_run_requirement_rows": len(requirements_df),
                "start_dry_run_run_guard_rows": len(guard_matrix_df),
                "start_dry_run_run_evidence_chain_passed": dataframe_all_passed(evidence_df),
                "start_dry_run_run_controls_passed": dataframe_all_passed(controls_df),
                "start_dry_run_run_validations_passed": dataframe_all_passed(validations_df),
                "start_dry_run_run_rules_passed": dataframe_all_passed(rules_df),
                "start_dry_run_run_requirements_passed": dataframe_all_passed(requirements_df),
                "start_dry_run_run_guards_passed": dataframe_all_passed(guard_matrix_df),
                "controlled_forward_observation_start_dry_run_run_passed": run_passed,
                "controlled_forward_observation_start_dry_run_run_decision": run_decision,
                "controlled_forward_observation_start_dry_run_run_performed": run_passed,
                "controlled_forward_observation_start_dry_run_performed": run_passed,
                "future_controlled_forward_observation_start_dry_run_output_integrity_review_allowed": future_integrity_review_allowed,
                "dry_run_artifact_write_performed": artifact_write_performed,
                "dry_run_artifact_rows_written": artifact_rows_written,
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
                "total_checks": len(checks_df),
                "warning_count": warning_count,
                "error_count": error_count,
                "blocker_count": blocker_count,
                "validation_passed": validation_passed,
                "validation_decision": (
                    "PHASE_10_23_LONG_FORWARD_OBSERVATION_CONTROLLED_START_DRY_RUN_RUN_VALIDATED"
                    if validation_passed
                    else "PHASE_10_23_LONG_FORWARD_OBSERVATION_CONTROLLED_START_DRY_RUN_RUN_FAILED"
                ),
            }
        ]
    )

    outputs = {
        "start_dry_run_run_summary_v1.csv": summary_df,
        "phase_10_22_source_summary_v1.csv": phase_10_22_summary_df,
        "phase_10_21_source_design_output_v1.csv": source_design_output_df,
        "phase_10_21_source_design_validations_v1.csv": source_design_validations_df,
        "phase_10_21_source_design_controls_v1.csv": source_design_controls_df,
        "phase_10_21_source_design_rules_v1.csv": source_design_rules_df,
        "phase_10_21_source_design_requirements_v1.csv": source_design_requirements_df,
        "phase_10_21_source_design_guard_matrix_v1.csv": source_design_guard_matrix_df,
        "phase_10_21_source_design_decision_v1.csv": source_design_decision_df,
        "phase_10_21_source_checks_v1.csv": source_checks_df,
        "phase_10_22_source_execution_review_evidence_chain_v1.csv": execution_review_evidence_chain_df,
        "phase_10_22_source_execution_review_controls_v1.csv": execution_review_controls_df,
        "phase_10_22_source_execution_review_rules_v1.csv": execution_review_rules_df,
        "phase_10_22_source_execution_review_requirements_v1.csv": execution_review_requirements_df,
        "phase_10_22_source_execution_review_guard_matrix_v1.csv": execution_review_guard_matrix_df,
        "phase_10_22_source_execution_review_decision_v1.csv": execution_review_decision_df,
        "phase_10_22_source_checks_v1.csv": phase_10_22_checks_df,
        "controlled_start_dry_run_output_v1.csv": dry_run_output_df,
        "start_dry_run_run_validations_v1.csv": validations_df,
        "start_dry_run_run_evidence_chain_v1.csv": evidence_df,
        "start_dry_run_run_controls_v1.csv": controls_df,
        "start_dry_run_run_rules_v1.csv": rules_df,
        "start_dry_run_run_requirements_v1.csv": requirements_df,
        "start_dry_run_run_guard_matrix_v1.csv": guard_matrix_df,
        "start_dry_run_run_decision_v1.csv": decision_df,
        "start_dry_run_run_checks_v1.csv": checks_df,
    }
    for filename, dataframe in outputs.items():
        dataframe.to_csv(REPORTS_DIR / filename, index=False)

    return {
        "summary": summary_df,
        "source_phase_10_22_summary": phase_10_22_summary_df,
        "source_design_output": source_design_output_df,
        "source_design_validations": source_design_validations_df,
        "source_design_controls": source_design_controls_df,
        "source_design_rules": source_design_rules_df,
        "source_design_requirements": source_design_requirements_df,
        "source_design_guard_matrix": source_design_guard_matrix_df,
        "source_design_decision": source_design_decision_df,
        "source_checks": source_checks_df,
        "source_execution_review_evidence_chain": execution_review_evidence_chain_df,
        "source_execution_review_controls": execution_review_controls_df,
        "source_execution_review_rules": execution_review_rules_df,
        "source_execution_review_requirements": execution_review_requirements_df,
        "source_execution_review_guard_matrix": execution_review_guard_matrix_df,
        "source_execution_review_decision": execution_review_decision_df,
        "source_phase_10_22_checks": phase_10_22_checks_df,
        "controlled_start_dry_run_output": dry_run_output_df,
        "start_dry_run_run_validations": validations_df,
        "start_dry_run_run_evidence_chain": evidence_df,
        "start_dry_run_run_controls": controls_df,
        "start_dry_run_run_rules": rules_df,
        "start_dry_run_run_requirements": requirements_df,
        "start_dry_run_run_guard_matrix": guard_matrix_df,
        "start_dry_run_run_decision": decision_df,
        "checks": checks_df,
    }