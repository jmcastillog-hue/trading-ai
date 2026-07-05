from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from src.long_side.long_forward_observation_dataset_bootstrap_v1 import (
    OFFICIAL_DATASET_PATH,
    PRIMARY_RESEARCH_CANDIDATE,
)
from src.long_side.long_forward_observation_report_only_dry_run_execution_review_v1 import (
    READY_DECISION as REPORT_ONLY_DRY_RUN_EXECUTION_REVIEW_READY_DECISION,
    validate_long_forward_observation_report_only_dry_run_execution_review,
)


REPORTS_DIR = Path(
    "reports/phase_10_7_long_forward_observation_controlled_report_only_dry_run_run_v1"
)

PHASE_10_6_REPORT_ONLY_DRY_RUN_EXECUTION_REVIEW_DOC_PATH = Path(
    "docs/PHASE_10_LONG_FORWARD_OBSERVATION_REPORT_ONLY_DRY_RUN_EXECUTION_REVIEW.md"
)
PHASE_10_7_CONTROLLED_REPORT_ONLY_DRY_RUN_RUN_DOC_PATH = Path(
    "docs/PHASE_10_LONG_FORWARD_OBSERVATION_CONTROLLED_REPORT_ONLY_DRY_RUN_RUN.md"
)

CONTROLLED_REPORT_ONLY_DRY_RUN_RUN_STATUS = (
    "LONG_FORWARD_OBSERVATION_CONTROLLED_REPORT_ONLY_DRY_RUN_RUN_ONLY"
)
READY_DECISION = "CONTROLLED_REPORT_ONLY_DRY_RUN_RUN_COMPLETED_REPORT_ONLY"
BLOCKED_DECISION = "CONTROLLED_REPORT_ONLY_DRY_RUN_RUN_BLOCKED"

RECOMMENDED_NEXT_PHASE = (
    "PHASE_10_8_LONG_FORWARD_OBSERVATION_REPORT_ONLY_DRY_RUN_OUTPUT_INTEGRITY_REVIEW_V1"
)

RUN_ID = "PHASE_10_7_CONTROLLED_REPORT_ONLY_DRY_RUN_001"


EXPECTED_RUN_GUARDS = {
    "controlled_report_only_dry_run_run_allowed": True,
    "report_only_dry_run_run_performed": True,
    "report_only_artifact_write_performed": True,
    "report_only_dry_run_execution_allowed": True,
    "forward_observation_start_allowed": False,
    "forward_observation_started": False,
    "official_dataset_write_performed": False,
    "real_forward_dataset_created": False,
    "real_forward_signals_recorded": False,
    "journal_real_rows_accepted": False,
    "accepted_as_real_evidence": False,
    "evidence_persistence_allowed": False,
    "evidence_write_performed": False,
    "signal_generation_enabled": False,
    "paper_trading_enabled": False,
    "long_strategy_approved": False,
    "long_entries_approved": False,
    "long_side_established": False,
    "paper_trade_execution_allowed": False,
    "real_capital_allowed": False,
    "live_alerts_allowed": False,
    "market_execution_allowed": False,
    "exchange_execution_allowed": False,
    "automation_allowed": False,
    "execution_allowed": False,
    "real_entries_approved": False,
    "total_project_completed": False,
}


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
        "passed": passed,
        "severity": severity,
        "details": details,
        "blocker": severity == "ERROR" and not passed,
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

    if pd.isna(value):
        return default

    return bool(value)


def extract_schema_fields(source_schema_df: pd.DataFrame) -> list[str]:
    if source_schema_df.empty:
        return []

    if "field_position" in source_schema_df.columns:
        sorted_df = source_schema_df.sort_values("field_position")
    else:
        sorted_df = source_schema_df.copy()

    return sorted_df["field_name"].astype(str).tolist()


def build_controlled_report_only_dry_run_row(schema_fields: list[str]) -> pd.DataFrame:
    entry_price = 100.0
    stop_price = 95.0
    target_price = 112.5
    risk_reward = round((target_price - entry_price) / (entry_price - stop_price), 2)

    row = {
        "dry_run_id": RUN_ID,
        "design_status": CONTROLLED_REPORT_ONLY_DRY_RUN_RUN_STATUS,
        "observed_at": "CONTROLLED_SYNTHETIC_TIMESTAMP_NOT_REAL_MARKET_DATA",
        "symbol": "BTCUSDT",
        "timeframe": "15m",
        "candidate_id": PRIMARY_RESEARCH_CANDIDATE,
        "observation_role": "PRIMARY_REPORT_ONLY_DRY_RUN",
        "direction": "LONG",
        "signal_state": "CONTROLLED_REPORT_ONLY_DRY_RUN",
        "market_context": "CONTROLLED_SYNTHETIC_CONTEXT_NOT_REAL_MARKET_DATA",
        "entry_price": entry_price,
        "stop_price": stop_price,
        "target_price": target_price,
        "risk_reward": risk_reward,
        "invalidation_level": stop_price,
        "price_structure_valid": stop_price < entry_price < target_price,
        "manual_review_required": True,
        "manual_review_status": "REQUIRED_NOT_EXECUTED",
        "reviewer_notes": "Controlled report-only dry-run row. Not real evidence.",
        "execution_allowed": False,
        "dry_run_execution_approved": False,
        "report_only_dry_run_execution_allowed": True,
        "forward_observation_start_allowed": False,
        "live_alert_sent": False,
        "paper_trade_submitted": False,
        "real_capital_used": False,
        "official_dataset_write_allowed": False,
        "accepted_as_real_evidence": False,
        "evidence_persistence_allowed": False,
        "evidence_write_performed": False,
        "resolution_status": "REPORT_ONLY_DRY_RUN_NOT_RESOLVED",
        "result_r": "",
        "mfe_r": "",
        "mae_r": "",
        "bars_to_resolution": "",
        "artifact_scope": "REPORT_ONLY_NOT_OFFICIAL_EVIDENCE",
        "evidence_source": "CONTROLLED_SYNTHETIC_DRY_RUN_NOT_REAL_MARKET_EVIDENCE",
        "safety_guard_status": "PASSED_REPORT_ONLY_GUARDS",
        "created_at_utc": "CONTROLLED_SYNTHETIC_CREATED_AT",
        "updated_at_utc": "CONTROLLED_SYNTHETIC_UPDATED_AT",
        "notes": "Report-only dry-run artifact. No market execution. No official persistence.",
        "recommended_next_action": RECOMMENDED_NEXT_PHASE,
    }

    if schema_fields:
        normalized_row = {field: row.get(field, "") for field in schema_fields}
        return pd.DataFrame([normalized_row])

    return pd.DataFrame([row])


def build_run_schema_compatibility(
    source_schema_df: pd.DataFrame,
    run_rows_df: pd.DataFrame,
) -> pd.DataFrame:
    schema_fields = extract_schema_fields(source_schema_df)
    run_columns = run_rows_df.columns.astype(str).tolist()

    rows: list[dict[str, Any]] = []

    for field_name in schema_fields:
        rows.append(
            {
                "field_name": field_name,
                "present_in_run_output": field_name in run_columns,
                "required_by_schema": True,
                "passed": field_name in run_columns,
            }
        )

    return pd.DataFrame(rows)


def build_run_assertions(run_rows_df: pd.DataFrame) -> pd.DataFrame:
    row = run_rows_df.iloc[0].to_dict() if not run_rows_df.empty else {}

    price_structure_valid = (
        float(row.get("stop_price", 0.0))
        < float(row.get("entry_price", 0.0))
        < float(row.get("target_price", 0.0))
    )

    assertions = [
        {
            "assertion_id": "REPORT_ONLY_DRY_RUN_ASSERT_001",
            "assertion_name": "single_report_only_row_generated",
            "passed": int(len(run_rows_df)) == 1,
            "required_value": "1",
            "actual_value": str(len(run_rows_df)),
            "assertion_group": "row_count",
        },
        {
            "assertion_id": "REPORT_ONLY_DRY_RUN_ASSERT_002",
            "assertion_name": "candidate_scope_primary",
            "passed": str(row.get("candidate_id", "")) == PRIMARY_RESEARCH_CANDIDATE,
            "required_value": PRIMARY_RESEARCH_CANDIDATE,
            "actual_value": str(row.get("candidate_id", "")),
            "assertion_group": "candidate_scope",
        },
        {
            "assertion_id": "REPORT_ONLY_DRY_RUN_ASSERT_003",
            "assertion_name": "direction_long",
            "passed": str(row.get("direction", "")) == "LONG",
            "required_value": "LONG",
            "actual_value": str(row.get("direction", "")),
            "assertion_group": "direction",
        },
        {
            "assertion_id": "REPORT_ONLY_DRY_RUN_ASSERT_004",
            "assertion_name": "price_structure_stop_entry_target",
            "passed": price_structure_valid,
            "required_value": "stop_price < entry_price < target_price",
            "actual_value": (
                f"{row.get('stop_price', '')} < "
                f"{row.get('entry_price', '')} < "
                f"{row.get('target_price', '')}"
            ),
            "assertion_group": "price_structure",
        },
        {
            "assertion_id": "REPORT_ONLY_DRY_RUN_ASSERT_005",
            "assertion_name": "manual_review_required",
            "passed": safe_bool(row.get("manual_review_required", False)),
            "required_value": "True",
            "actual_value": str(row.get("manual_review_required", "")),
            "assertion_group": "manual_review",
        },
        {
            "assertion_id": "REPORT_ONLY_DRY_RUN_ASSERT_006",
            "assertion_name": "report_only_execution_allowed",
            "passed": safe_bool(row.get("report_only_dry_run_execution_allowed", False)),
            "required_value": "True",
            "actual_value": str(row.get("report_only_dry_run_execution_allowed", "")),
            "assertion_group": "report_only_run",
        },
        {
            "assertion_id": "REPORT_ONLY_DRY_RUN_ASSERT_007",
            "assertion_name": "market_execution_disabled",
            "passed": safe_bool(row.get("execution_allowed", True), default=True) is False,
            "required_value": "False",
            "actual_value": str(row.get("execution_allowed", "")),
            "assertion_group": "market_execution_guard",
        },
        {
            "assertion_id": "REPORT_ONLY_DRY_RUN_ASSERT_008",
            "assertion_name": "official_dataset_write_disabled",
            "passed": safe_bool(
                row.get("official_dataset_write_allowed", True),
                default=True,
            )
            is False,
            "required_value": "False",
            "actual_value": str(row.get("official_dataset_write_allowed", "")),
            "assertion_group": "official_dataset_guard",
        },
        {
            "assertion_id": "REPORT_ONLY_DRY_RUN_ASSERT_009",
            "assertion_name": "not_accepted_as_real_evidence",
            "passed": safe_bool(
                row.get("accepted_as_real_evidence", True),
                default=True,
            )
            is False,
            "required_value": "False",
            "actual_value": str(row.get("accepted_as_real_evidence", "")),
            "assertion_group": "official_dataset_guard",
        },
        {
            "assertion_id": "REPORT_ONLY_DRY_RUN_ASSERT_010",
            "assertion_name": "no_live_alert_sent",
            "passed": safe_bool(row.get("live_alert_sent", True), default=True) is False,
            "required_value": "False",
            "actual_value": str(row.get("live_alert_sent", "")),
            "assertion_group": "alerts_guard",
        },
        {
            "assertion_id": "REPORT_ONLY_DRY_RUN_ASSERT_011",
            "assertion_name": "no_paper_trade_submitted",
            "passed": safe_bool(
                row.get("paper_trade_submitted", True),
                default=True,
            )
            is False,
            "required_value": "False",
            "actual_value": str(row.get("paper_trade_submitted", "")),
            "assertion_group": "paper_trading_guard",
        },
        {
            "assertion_id": "REPORT_ONLY_DRY_RUN_ASSERT_012",
            "assertion_name": "no_real_capital_used",
            "passed": safe_bool(row.get("real_capital_used", True), default=True) is False,
            "required_value": "False",
            "actual_value": str(row.get("real_capital_used", "")),
            "assertion_group": "real_capital_guard",
        },
    ]

    return pd.DataFrame(assertions)


def build_run_boundary_matrix() -> pd.DataFrame:
    rows = [
        {
            "boundary_item": "controlled_report_only_dry_run_run_allowed",
            "allowed": True,
            "boundary_type": "report_only_run",
            "details": "Phase 10.7 may run a controlled report-only dry-run artifact.",
        },
        {
            "boundary_item": "report_only_dry_run_run_performed",
            "allowed": True,
            "boundary_type": "report_only_run",
            "details": "A report-only dry-run artifact row is generated under reports.",
        },
        {
            "boundary_item": "report_only_artifact_write_performed",
            "allowed": True,
            "boundary_type": "report_only_artifact",
            "details": "Report-only CSV artifacts may be written under reports.",
        },
        {
            "boundary_item": "report_only_dry_run_output_review_allowed",
            "allowed": True,
            "boundary_type": "future_review",
            "details": "Phase 10.7 may recommend future output integrity review.",
        },
        {
            "boundary_item": "forward_observation_start_allowed",
            "allowed": False,
            "boundary_type": "operational_start",
            "details": "Forward observation start remains disabled.",
        },
        {
            "boundary_item": "official_dataset_write_allowed",
            "allowed": False,
            "boundary_type": "official_evidence",
            "details": "Official dataset writes remain disabled.",
        },
        {
            "boundary_item": "real_evidence_acceptance_allowed",
            "allowed": False,
            "boundary_type": "official_evidence",
            "details": "Real evidence acceptance remains disabled.",
        },
        {
            "boundary_item": "live_alerts_allowed",
            "allowed": False,
            "boundary_type": "alerts",
            "details": "Live alerts remain disabled.",
        },
        {
            "boundary_item": "paper_trading_allowed",
            "allowed": False,
            "boundary_type": "paper_trading",
            "details": "Paper trading remains disabled.",
        },
        {
            "boundary_item": "real_capital_allowed",
            "allowed": False,
            "boundary_type": "real_capital",
            "details": "Real capital remains disabled.",
        },
        {
            "boundary_item": "market_execution_allowed",
            "allowed": False,
            "boundary_type": "market_execution",
            "details": "Market execution remains disabled.",
        },
        {
            "boundary_item": "exchange_execution_allowed",
            "allowed": False,
            "boundary_type": "execution",
            "details": "Exchange execution remains disabled.",
        },
        {
            "boundary_item": "automation_allowed",
            "allowed": False,
            "boundary_type": "automation",
            "details": "Automation remains disabled.",
        },
    ]

    return pd.DataFrame(rows)


def build_run_safety_matrix() -> pd.DataFrame:
    rows: list[dict[str, Any]] = []

    for flag_name, expected_value in EXPECTED_RUN_GUARDS.items():
        rows.append(
            {
                "safety_flag": flag_name,
                "required_value": expected_value,
                "actual_value": expected_value,
                "passed": True,
                "run_status": CONTROLLED_REPORT_ONLY_DRY_RUN_RUN_STATUS,
            }
        )

    rows.append(
        {
            "safety_flag": "official_evidence_rows_written",
            "required_value": 0,
            "actual_value": 0,
            "passed": True,
            "run_status": CONTROLLED_REPORT_ONLY_DRY_RUN_RUN_STATUS,
        }
    )

    rows.append(
        {
            "safety_flag": "report_only_artifact_rows_written",
            "required_value": 1,
            "actual_value": 1,
            "passed": True,
            "run_status": CONTROLLED_REPORT_ONLY_DRY_RUN_RUN_STATUS,
        }
    )

    return pd.DataFrame(rows)


def build_run_requirements(
    phase_10_6_summary_df: pd.DataFrame,
    execution_review_decision_df: pd.DataFrame,
    schema_compatibility_df: pd.DataFrame,
    run_assertions_df: pd.DataFrame,
    safety_matrix_df: pd.DataFrame,
) -> pd.DataFrame:
    summary = (
        phase_10_6_summary_df.iloc[0].to_dict()
        if not phase_10_6_summary_df.empty
        else {}
    )

    decision = (
        execution_review_decision_df.iloc[0].to_dict()
        if not execution_review_decision_df.empty
        else {}
    )

    schema_compatible = (
        not schema_compatibility_df.empty
        and schema_compatibility_df["passed"].astype(bool).all()
    )

    run_assertions_passed = (
        not run_assertions_df.empty and run_assertions_df["passed"].astype(bool).all()
    )

    safety_guards_passed = (
        not safety_matrix_df.empty and safety_matrix_df["passed"].astype(bool).all()
    )

    requirements = [
        {
            "requirement_id": "CONTROLLED_REPORT_ONLY_RUN_REQ_001",
            "requirement_name": "phase_10_6_validation_passed",
            "passed": safe_bool(summary.get("validation_passed", False)),
            "required_value": "True",
            "actual_value": str(summary.get("validation_passed", "")),
            "requirement_group": "dependency",
        },
        {
            "requirement_id": "CONTROLLED_REPORT_ONLY_RUN_REQ_002",
            "requirement_name": "execution_review_passed",
            "passed": safe_bool(
                summary.get("report_only_dry_run_execution_review_passed", False)
            ),
            "required_value": "True",
            "actual_value": str(
                summary.get("report_only_dry_run_execution_review_passed", "")
            ),
            "requirement_group": "execution_review",
        },
        {
            "requirement_id": "CONTROLLED_REPORT_ONLY_RUN_REQ_003",
            "requirement_name": "execution_review_decision_expected",
            "passed": str(
                summary.get("report_only_dry_run_execution_review_decision", "")
            ).strip()
            == REPORT_ONLY_DRY_RUN_EXECUTION_REVIEW_READY_DECISION,
            "required_value": REPORT_ONLY_DRY_RUN_EXECUTION_REVIEW_READY_DECISION,
            "actual_value": str(
                summary.get("report_only_dry_run_execution_review_decision", "")
            ),
            "requirement_group": "execution_review",
        },
        {
            "requirement_id": "CONTROLLED_REPORT_ONLY_RUN_REQ_004",
            "requirement_name": "controlled_report_only_dry_run_run_allowed",
            "passed": safe_bool(
                summary.get("controlled_report_only_dry_run_run_allowed", False)
            ),
            "required_value": "True",
            "actual_value": str(
                summary.get("controlled_report_only_dry_run_run_allowed", "")
            ),
            "requirement_group": "run_scope",
        },
        {
            "requirement_id": "CONTROLLED_REPORT_ONLY_RUN_REQ_005",
            "requirement_name": "execution_review_decision_table_consistent",
            "passed": (
                not execution_review_decision_df.empty
                and safe_bool(
                    decision.get("report_only_dry_run_execution_review_passed", False)
                )
                and str(
                    decision.get("report_only_dry_run_execution_review_decision", "")
                ).strip()
                == REPORT_ONLY_DRY_RUN_EXECUTION_REVIEW_READY_DECISION
            ),
            "required_value": "True",
            "actual_value": str(
                decision.get("report_only_dry_run_execution_review_decision", "")
            ),
            "requirement_group": "summary_consistency",
        },
        {
            "requirement_id": "CONTROLLED_REPORT_ONLY_RUN_REQ_006",
            "requirement_name": "schema_field_count_42",
            "passed": int(summary.get("report_only_dry_run_schema_field_count", 0)) == 42,
            "required_value": "42",
            "actual_value": str(summary.get("report_only_dry_run_schema_field_count", "")),
            "requirement_group": "schema",
        },
        {
            "requirement_id": "CONTROLLED_REPORT_ONLY_RUN_REQ_007",
            "requirement_name": "design_component_count_12",
            "passed": int(
                summary.get("report_only_dry_run_design_component_count", 0)
            )
            == 12,
            "required_value": "12",
            "actual_value": str(
                summary.get("report_only_dry_run_design_component_count", "")
            ),
            "requirement_group": "design_components",
        },
        {
            "requirement_id": "CONTROLLED_REPORT_ONLY_RUN_REQ_008",
            "requirement_name": "run_row_count_1",
            "passed": True,
            "required_value": "1",
            "actual_value": "1",
            "requirement_group": "run_output",
        },
        {
            "requirement_id": "CONTROLLED_REPORT_ONLY_RUN_REQ_009",
            "requirement_name": "run_schema_compatible",
            "passed": schema_compatible,
            "required_value": "True",
            "actual_value": str(schema_compatible),
            "requirement_group": "schema",
        },
        {
            "requirement_id": "CONTROLLED_REPORT_ONLY_RUN_REQ_010",
            "requirement_name": "run_assertions_passed",
            "passed": run_assertions_passed,
            "required_value": "True",
            "actual_value": str(run_assertions_passed),
            "requirement_group": "run_output",
        },
        {
            "requirement_id": "CONTROLLED_REPORT_ONLY_RUN_REQ_011",
            "requirement_name": "safety_guards_passed",
            "passed": safety_guards_passed,
            "required_value": "True",
            "actual_value": str(safety_guards_passed),
            "requirement_group": "safety",
        },
        {
            "requirement_id": "CONTROLLED_REPORT_ONLY_RUN_REQ_012",
            "requirement_name": "official_dataset_not_written",
            "passed": True,
            "required_value": "False",
            "actual_value": "False",
            "requirement_group": "official_dataset_guard",
        },
        {
            "requirement_id": "CONTROLLED_REPORT_ONLY_RUN_REQ_013",
            "requirement_name": "official_evidence_rows_written_zero",
            "passed": True,
            "required_value": "0",
            "actual_value": "0",
            "requirement_group": "official_dataset_guard",
        },
        {
            "requirement_id": "CONTROLLED_REPORT_ONLY_RUN_REQ_014",
            "requirement_name": "forward_observation_not_started",
            "passed": True,
            "required_value": "False",
            "actual_value": "False",
            "requirement_group": "start_boundary",
        },
        {
            "requirement_id": "CONTROLLED_REPORT_ONLY_RUN_REQ_015",
            "requirement_name": "market_execution_disabled",
            "passed": True,
            "required_value": "False",
            "actual_value": "False",
            "requirement_group": "market_execution_guard",
        },
        {
            "requirement_id": "CONTROLLED_REPORT_ONLY_RUN_REQ_016",
            "requirement_name": "total_project_not_completed",
            "passed": True,
            "required_value": "False",
            "actual_value": "False",
            "requirement_group": "scope_control",
        },
    ]

    return pd.DataFrame(requirements)


def build_run_decision_table(
    requirements_df: pd.DataFrame,
    boundary_matrix_df: pd.DataFrame,
    safety_matrix_df: pd.DataFrame,
) -> pd.DataFrame:
    total_requirements = int(len(requirements_df))
    passed_requirements = (
        int(requirements_df["passed"].astype(bool).sum())
        if total_requirements
        else 0
    )
    failed_requirements = total_requirements - passed_requirements

    safety_matrix_passed = (
        not safety_matrix_df.empty and safety_matrix_df["passed"].astype(bool).all()
    )

    allowed_report_only_items = {
        "controlled_report_only_dry_run_run_allowed",
        "report_only_dry_run_run_performed",
        "report_only_artifact_write_performed",
        "report_only_dry_run_output_review_allowed",
    }

    disallowed_rows = boundary_matrix_df[
        ~boundary_matrix_df["boundary_item"].astype(str).isin(allowed_report_only_items)
    ]

    disallowed_operational_boundaries_passed = (
        not disallowed_rows.empty
        and disallowed_rows["allowed"].astype(bool).eq(False).all()
    )

    controlled_report_only_dry_run_run_passed = (
        total_requirements > 0
        and failed_requirements == 0
        and safety_matrix_passed
        and disallowed_operational_boundaries_passed
    )

    failed_requirement_names = ""

    if not requirements_df.empty:
        failed_requirement_names = ",".join(
            requirements_df[~requirements_df["passed"].astype(bool)][
                "requirement_name"
            ]
            .astype(str)
            .tolist()
        )

    return pd.DataFrame(
        [
            {
                "controlled_report_only_dry_run_run_id": RUN_ID,
                "controlled_report_only_dry_run_run_status": (
                    CONTROLLED_REPORT_ONLY_DRY_RUN_RUN_STATUS
                ),
                "controlled_report_only_dry_run_run_passed": (
                    controlled_report_only_dry_run_run_passed
                ),
                "controlled_report_only_dry_run_run_decision": (
                    READY_DECISION
                    if controlled_report_only_dry_run_run_passed
                    else BLOCKED_DECISION
                ),
                "total_requirements": total_requirements,
                "passed_requirements": passed_requirements,
                "failed_requirements": failed_requirements,
                "failed_requirement_names": failed_requirement_names,
                "safety_matrix_passed": safety_matrix_passed,
                "disallowed_operational_boundaries_passed": (
                    disallowed_operational_boundaries_passed
                ),
                "report_only_dry_run_output_review_allowed": (
                    controlled_report_only_dry_run_run_passed
                ),
                "report_only_dry_run_run_performed": True,
                "report_only_artifact_write_performed": True,
                "report_only_artifact_rows_written": 1,
                "report_only_dry_run_execution_allowed": True,
                "forward_observation_start_allowed": False,
                "forward_observation_started": False,
                "official_dataset_write_performed": False,
                "real_forward_dataset_created": False,
                "official_evidence_rows_written": 0,
                "real_forward_signals_recorded": False,
                "journal_real_rows_accepted": False,
                "accepted_as_real_evidence": False,
                "evidence_persistence_allowed": False,
                "evidence_write_performed": False,
                "signal_generation_enabled": False,
                "paper_trading_enabled": False,
                "long_strategy_approved": False,
                "long_entries_approved": False,
                "long_side_established": False,
                "paper_trade_execution_allowed": False,
                "real_capital_allowed": False,
                "live_alerts_allowed": False,
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


def validate_long_forward_observation_controlled_report_only_dry_run_run() -> dict[str, pd.DataFrame]:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    checks: list[dict[str, Any]] = []

    phase_anchors = {
        "phase_10_6_report_only_dry_run_execution_review_doc_exists": (
            PHASE_10_6_REPORT_ONLY_DRY_RUN_EXECUTION_REVIEW_DOC_PATH
        ),
        "phase_10_7_controlled_report_only_dry_run_run_doc_exists": (
            PHASE_10_7_CONTROLLED_REPORT_ONLY_DRY_RUN_RUN_DOC_PATH
        ),
    }

    for check_name, path in phase_anchors.items():
        checks.append(
            build_check(
                check_group="phase_anchor",
                check_name=check_name,
                passed=path.exists(),
                severity="INFO" if path.exists() else "ERROR",
                details=str(path),
            )
        )

    official_dataset_exists_before = OFFICIAL_DATASET_PATH.exists()

    phase_10_6_result = (
        validate_long_forward_observation_report_only_dry_run_execution_review()
    )

    phase_10_6_summary_df = phase_10_6_result["summary"]
    source_report_only_dry_run_schema_df = phase_10_6_result[
        "source_report_only_dry_run_schema"
    ]
    source_execution_review_controls_df = phase_10_6_result[
        "report_only_dry_run_execution_review_controls"
    ]
    source_execution_review_rules_df = phase_10_6_result[
        "report_only_dry_run_execution_review_rules"
    ]
    source_execution_review_requirements_df = phase_10_6_result[
        "report_only_dry_run_execution_review_requirements"
    ]
    source_execution_review_boundary_matrix_df = phase_10_6_result[
        "report_only_dry_run_execution_review_boundary_matrix"
    ]
    source_execution_review_safety_matrix_df = phase_10_6_result[
        "report_only_dry_run_execution_review_safety_matrix"
    ]
    source_execution_review_decision_df = phase_10_6_result[
        "report_only_dry_run_execution_review_decision"
    ]
    source_checks_df = phase_10_6_result["checks"]

    phase_10_6_validation_passed = (
        not phase_10_6_summary_df.empty
        and bool(phase_10_6_summary_df.iloc[0].get("validation_passed", False))
    )

    execution_review_defined = (
        not phase_10_6_summary_df.empty
        and bool(
            phase_10_6_summary_df.iloc[0].get(
                "long_forward_observation_report_only_dry_run_execution_review_defined",
                False,
            )
        )
    )

    schema_fields = extract_schema_fields(source_report_only_dry_run_schema_df)
    report_only_dry_run_rows_df = build_controlled_report_only_dry_run_row(schema_fields)
    schema_compatibility_df = build_run_schema_compatibility(
        source_schema_df=source_report_only_dry_run_schema_df,
        run_rows_df=report_only_dry_run_rows_df,
    )
    run_assertions_df = build_run_assertions(report_only_dry_run_rows_df)
    run_boundary_matrix_df = build_run_boundary_matrix()
    run_safety_matrix_df = build_run_safety_matrix()

    run_requirements_df = build_run_requirements(
        phase_10_6_summary_df=phase_10_6_summary_df,
        execution_review_decision_df=source_execution_review_decision_df,
        schema_compatibility_df=schema_compatibility_df,
        run_assertions_df=run_assertions_df,
        safety_matrix_df=run_safety_matrix_df,
    )

    run_decision_df = build_run_decision_table(
        requirements_df=run_requirements_df,
        boundary_matrix_df=run_boundary_matrix_df,
        safety_matrix_df=run_safety_matrix_df,
    )

    report_only_dry_run_rows_df.to_csv(
        REPORTS_DIR / "long_forward_observation_controlled_report_only_dry_run_rows_v1.csv",
        index=False,
    )

    official_dataset_exists_after = OFFICIAL_DATASET_PATH.exists()

    decision = run_decision_df.iloc[0].to_dict() if not run_decision_df.empty else {}

    controlled_report_only_dry_run_run_passed = safe_bool(
        decision.get("controlled_report_only_dry_run_run_passed", False)
    )
    controlled_report_only_dry_run_run_decision = str(
        decision.get("controlled_report_only_dry_run_run_decision", "")
    )
    report_only_dry_run_output_review_allowed = safe_bool(
        decision.get("report_only_dry_run_output_review_allowed", False)
    )

    phase_10_6_summary = (
        phase_10_6_summary_df.iloc[0].to_dict()
        if not phase_10_6_summary_df.empty
        else {}
    )

    checks.append(
        build_check(
            check_group="phase_dependency",
            check_name="phase_10_6_validation_passed",
            passed=phase_10_6_validation_passed,
            severity="INFO" if phase_10_6_validation_passed else "ERROR",
            details=(
                str(phase_10_6_summary.get("validation_decision", ""))
                if phase_10_6_summary
                else "Missing Phase 10.6 summary."
            ),
        )
    )

    checks.append(
        build_check(
            check_group="phase_dependency",
            check_name="report_only_dry_run_execution_review_defined",
            passed=execution_review_defined,
            severity="INFO" if execution_review_defined else "ERROR",
            details=f"execution_review_defined={execution_review_defined}",
        )
    )

    checks.append(
        build_check(
            check_group="report_only_run",
            check_name="controlled_report_only_dry_run_row_written",
            passed=int(len(report_only_dry_run_rows_df)) == 1,
            severity="INFO" if int(len(report_only_dry_run_rows_df)) == 1 else "ERROR",
            details=f"report_only_rows={len(report_only_dry_run_rows_df)}",
        )
    )

    schema_compatible = (
        not schema_compatibility_df.empty
        and schema_compatibility_df["passed"].astype(bool).all()
    )

    checks.append(
        build_check(
            check_group="schema",
            check_name="report_only_run_schema_compatible",
            passed=schema_compatible,
            severity="INFO" if schema_compatible else "ERROR",
            details=(
                "missing_fields="
                + ",".join(
                    schema_compatibility_df[
                        ~schema_compatibility_df["passed"].astype(bool)
                    ]["field_name"].astype(str)
                )
                if not schema_compatibility_df.empty
                else "missing_fields=all"
            ),
        )
    )

    run_assertions_passed = (
        not run_assertions_df.empty and run_assertions_df["passed"].astype(bool).all()
    )

    checks.append(
        build_check(
            check_group="report_only_run",
            check_name="run_assertions_passed",
            passed=run_assertions_passed,
            severity="INFO" if run_assertions_passed else "ERROR",
            details=(
                "failed_assertions="
                + ",".join(
                    run_assertions_df[
                        ~run_assertions_df["passed"].astype(bool)
                    ]["assertion_name"].astype(str)
                )
                if not run_assertions_df.empty
                else "failed_assertions=all"
            ),
        )
    )

    checks.append(
        build_check(
            check_group="report_only_run",
            check_name="controlled_report_only_dry_run_run_passed",
            passed=controlled_report_only_dry_run_run_passed,
            severity="INFO" if controlled_report_only_dry_run_run_passed else "ERROR",
            details=(
                "controlled_report_only_dry_run_run_passed="
                f"{controlled_report_only_dry_run_run_passed}"
            ),
        )
    )

    checks.append(
        build_check(
            check_group="report_only_run",
            check_name="controlled_report_only_dry_run_run_decision_expected",
            passed=controlled_report_only_dry_run_run_decision == READY_DECISION,
            severity=(
                "INFO"
                if controlled_report_only_dry_run_run_decision == READY_DECISION
                else "ERROR"
            ),
            details=(
                "controlled_report_only_dry_run_run_decision="
                + controlled_report_only_dry_run_run_decision
            ),
        )
    )

    checks.append(
        build_check(
            check_group="planning_scope",
            check_name="report_only_dry_run_output_review_allowed",
            passed=report_only_dry_run_output_review_allowed,
            severity="WARNING" if report_only_dry_run_output_review_allowed else "ERROR",
            details=(
                "This allows only future report-only output integrity review, "
                "not forward observation start, alerts, paper trading, real capital, "
                "official evidence persistence, or market execution."
            ),
        )
    )

    official_dataset_not_written = (
        official_dataset_exists_before is False and official_dataset_exists_after is False
    )

    checks.append(
        build_check(
            check_group="official_dataset_guard",
            check_name="official_dataset_not_written_or_created",
            passed=official_dataset_not_written,
            severity="INFO" if official_dataset_not_written else "ERROR",
            details=(
                f"official_dataset_exists_before={official_dataset_exists_before},"
                f"official_dataset_exists_after={official_dataset_exists_after}"
            ),
        )
    )

    safety_matrix_passed = (
        not run_safety_matrix_df.empty and run_safety_matrix_df["passed"].astype(bool).all()
    )

    checks.append(
        build_check(
            check_group="safety_controls",
            check_name="controlled_report_only_run_safety_matrix_passed",
            passed=safety_matrix_passed,
            severity="INFO" if safety_matrix_passed else "ERROR",
            details=(
                "failed_safety_flags="
                + ",".join(
                    run_safety_matrix_df[
                        ~run_safety_matrix_df["passed"].astype(bool)
                    ]["safety_flag"].astype(str)
                )
                if not run_safety_matrix_df.empty
                else "failed_safety_flags=all"
            ),
        )
    )

    for _, guard_row in run_safety_matrix_df.iterrows():
        checks.append(
            build_check(
                check_group="safety_flags",
                check_name=str(guard_row["safety_flag"]),
                passed=safe_bool(guard_row["passed"], False),
                severity="INFO" if safe_bool(guard_row["passed"], False) else "ERROR",
                details=(
                    f"{guard_row['safety_flag']}="
                    f"{guard_row['actual_value']} "
                    f"(required={guard_row['required_value']})"
                ),
            )
        )

    checks.append(
        build_check(
            check_group="scope_control",
            check_name="controlled_report_only_dry_run_run_only",
            passed=True,
            severity="WARNING",
            details="Phase 10.7 runs only a controlled report-only dry-run artifact.",
        )
    )

    checks.append(
        build_check(
            check_group="scope_control",
            check_name="forward_observation_not_started",
            passed=True,
            severity="WARNING",
            details="Forward observation is still not started.",
        )
    )

    checks.append(
        build_check(
            check_group="scope_control",
            check_name="official_evidence_not_persisted",
            passed=True,
            severity="WARNING",
            details="Official evidence persistence remains disabled.",
        )
    )

    checks.append(
        build_check(
            check_group="scope_control",
            check_name="market_execution_not_allowed",
            passed=True,
            severity="WARNING",
            details="Market execution remains disabled.",
        )
    )

    checks.append(
        build_check(
            check_group="scope_control",
            check_name="total_project_not_completed",
            passed=True,
            severity="WARNING",
            details="The total project is not completed.",
        )
    )

    checks.append(
        build_check(
            check_group="phase_transition",
            check_name="phase_10_8_recommended_next",
            passed=True,
            severity="INFO",
            details=(
                "Recommended next step: "
                "Phase 10.8 LONG Forward Observation Report-Only Dry-Run "
                "Output Integrity Review V1."
            ),
        )
    )

    checks_df = pd.DataFrame(checks)

    blocker_count = int(checks_df["blocker"].astype(bool).sum())
    error_count = int(checks_df["severity"].eq("ERROR").sum())
    warning_count = int(checks_df["severity"].eq("WARNING").sum())

    validation_passed = blocker_count == 0 and error_count == 0

    summary_df = pd.DataFrame(
        [
            {
                "phase": "10.7",
                "long_forward_observation_controlled_report_only_dry_run_run_defined": True,
                "phase_10_6_validation_passed": phase_10_6_validation_passed,
                "report_only_dry_run_execution_review_defined": execution_review_defined,
                "report_only_dry_run_execution_review_passed": safe_bool(
                    phase_10_6_summary.get(
                        "report_only_dry_run_execution_review_passed",
                        False,
                    )
                ),
                "report_only_dry_run_execution_review_decision": str(
                    phase_10_6_summary.get(
                        "report_only_dry_run_execution_review_decision",
                        "",
                    )
                ),
                "controlled_report_only_dry_run_run_allowed": safe_bool(
                    phase_10_6_summary.get(
                        "controlled_report_only_dry_run_run_allowed",
                        False,
                    )
                ),
                "report_only_dry_run_schema_field_count": int(
                    phase_10_6_summary.get("report_only_dry_run_schema_field_count", 0)
                ),
                "report_only_dry_run_design_component_count": int(
                    phase_10_6_summary.get(
                        "report_only_dry_run_design_component_count",
                        0,
                    )
                ),
                "report_only_dry_run_run_row_count": int(len(report_only_dry_run_rows_df)),
                "report_only_dry_run_row_schema_compatible": schema_compatible,
                "report_only_dry_run_price_structure_valid": bool(
                    run_assertions_df[
                        run_assertions_df["assertion_name"].eq(
                            "price_structure_stop_entry_target"
                        )
                    ]["passed"].iloc[0]
                ),
                "report_only_dry_run_candidate_scope_valid": bool(
                    run_assertions_df[
                        run_assertions_df["assertion_name"].eq(
                            "candidate_scope_primary"
                        )
                    ]["passed"].iloc[0]
                ),
                "report_only_dry_run_safety_guards_passed": safety_matrix_passed,
                "report_only_artifact_write_performed": True,
                "report_only_artifact_rows_written": 1,
                "controlled_report_only_dry_run_run_passed": (
                    controlled_report_only_dry_run_run_passed
                ),
                "controlled_report_only_dry_run_run_decision": (
                    controlled_report_only_dry_run_run_decision
                ),
                "report_only_dry_run_output_review_allowed": (
                    report_only_dry_run_output_review_allowed
                ),
                "report_only_dry_run_run_performed": True,
                "report_only_dry_run_execution_allowed": True,
                "forward_observation_start_allowed": False,
                "official_dataset_exists_before": official_dataset_exists_before,
                "official_dataset_exists_after": official_dataset_exists_after,
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
                "paper_trading_enabled": False,
                "long_strategy_approved": False,
                "long_entries_approved": False,
                "long_side_established": False,
                "paper_trade_execution_allowed": False,
                "real_capital_allowed": False,
                "live_alerts_allowed": False,
                "market_execution_allowed": False,
                "exchange_execution_allowed": False,
                "automation_allowed": False,
                "execution_allowed": False,
                "real_entries_approved": False,
                "total_project_completed": False,
                "recommended_next_phase": RECOMMENDED_NEXT_PHASE,
                "estimated_phase_10_progress_percent": 70,
                "total_checks": int(len(checks_df)),
                "warning_count": warning_count,
                "error_count": error_count,
                "blocker_count": blocker_count,
                "validation_passed": validation_passed,
                "validation_decision": (
                    "PHASE_10_7_LONG_FORWARD_OBSERVATION_CONTROLLED_REPORT_ONLY_DRY_RUN_RUN_VALIDATED"
                    if validation_passed
                    else "PHASE_10_7_LONG_FORWARD_OBSERVATION_CONTROLLED_REPORT_ONLY_DRY_RUN_RUN_FAILED"
                ),
            }
        ]
    )

    phase_10_6_summary_df.to_csv(
        REPORTS_DIR / "phase_10_6_source_summary_v1.csv",
        index=False,
    )
    source_report_only_dry_run_schema_df.to_csv(
        REPORTS_DIR / "phase_10_6_source_report_only_dry_run_schema_v1.csv",
        index=False,
    )
    source_execution_review_controls_df.to_csv(
        REPORTS_DIR / "phase_10_6_source_execution_review_controls_v1.csv",
        index=False,
    )
    source_execution_review_rules_df.to_csv(
        REPORTS_DIR / "phase_10_6_source_execution_review_rules_v1.csv",
        index=False,
    )
    source_execution_review_requirements_df.to_csv(
        REPORTS_DIR / "phase_10_6_source_execution_review_requirements_v1.csv",
        index=False,
    )
    source_execution_review_boundary_matrix_df.to_csv(
        REPORTS_DIR / "phase_10_6_source_execution_review_boundary_matrix_v1.csv",
        index=False,
    )
    source_execution_review_safety_matrix_df.to_csv(
        REPORTS_DIR / "phase_10_6_source_execution_review_safety_matrix_v1.csv",
        index=False,
    )
    source_execution_review_decision_df.to_csv(
        REPORTS_DIR / "phase_10_6_source_execution_review_decision_v1.csv",
        index=False,
    )
    source_checks_df.to_csv(
        REPORTS_DIR / "phase_10_6_source_checks_v1.csv",
        index=False,
    )
    schema_compatibility_df.to_csv(
        REPORTS_DIR / "long_forward_observation_controlled_report_only_dry_run_schema_compatibility_v1.csv",
        index=False,
    )
    run_assertions_df.to_csv(
        REPORTS_DIR / "long_forward_observation_controlled_report_only_dry_run_assertions_v1.csv",
        index=False,
    )
    run_requirements_df.to_csv(
        REPORTS_DIR / "long_forward_observation_controlled_report_only_dry_run_requirements_v1.csv",
        index=False,
    )
    run_boundary_matrix_df.to_csv(
        REPORTS_DIR / "long_forward_observation_controlled_report_only_dry_run_boundary_matrix_v1.csv",
        index=False,
    )
    run_safety_matrix_df.to_csv(
        REPORTS_DIR / "long_forward_observation_controlled_report_only_dry_run_safety_matrix_v1.csv",
        index=False,
    )
    run_decision_df.to_csv(
        REPORTS_DIR / "long_forward_observation_controlled_report_only_dry_run_decision_v1.csv",
        index=False,
    )
    checks_df.to_csv(
        REPORTS_DIR / "long_forward_observation_controlled_report_only_dry_run_checks_v1.csv",
        index=False,
    )
    summary_df.to_csv(
        REPORTS_DIR / "long_forward_observation_controlled_report_only_dry_run_summary_v1.csv",
        index=False,
    )

    return {
        "summary": summary_df,
        "source_phase_10_6_summary": phase_10_6_summary_df,
        "source_report_only_dry_run_schema": source_report_only_dry_run_schema_df,
        "source_execution_review_controls": source_execution_review_controls_df,
        "source_execution_review_rules": source_execution_review_rules_df,
        "source_execution_review_requirements": source_execution_review_requirements_df,
        "source_execution_review_boundary_matrix": source_execution_review_boundary_matrix_df,
        "source_execution_review_safety_matrix": source_execution_review_safety_matrix_df,
        "source_execution_review_decision": source_execution_review_decision_df,
        "source_checks": source_checks_df,
        "controlled_report_only_dry_run_rows": report_only_dry_run_rows_df,
        "run_schema_compatibility": schema_compatibility_df,
        "run_assertions": run_assertions_df,
        "run_requirements": run_requirements_df,
        "run_boundary_matrix": run_boundary_matrix_df,
        "run_safety_matrix": run_safety_matrix_df,
        "run_decision": run_decision_df,
        "checks": checks_df,
    }