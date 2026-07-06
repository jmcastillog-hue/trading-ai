from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from src.long_side.long_forward_observation_controlled_report_only_dry_run_run_v1 import (
    READY_DECISION as CONTROLLED_REPORT_ONLY_DRY_RUN_READY_DECISION,
    validate_long_forward_observation_controlled_report_only_dry_run_run,
)
from src.long_side.long_forward_observation_dataset_bootstrap_v1 import (
    OFFICIAL_DATASET_PATH,
    PRIMARY_RESEARCH_CANDIDATE,
)


REPORTS_DIR = Path(
    "reports/phase_10_8_long_forward_observation_report_only_dry_run_output_integrity_review_v1"
)

PHASE_10_7_CONTROLLED_REPORT_ONLY_DRY_RUN_RUN_DOC_PATH = Path(
    "docs/PHASE_10_LONG_FORWARD_OBSERVATION_CONTROLLED_REPORT_ONLY_DRY_RUN_RUN.md"
)
PHASE_10_8_REPORT_ONLY_DRY_RUN_OUTPUT_INTEGRITY_REVIEW_DOC_PATH = Path(
    "docs/PHASE_10_LONG_FORWARD_OBSERVATION_REPORT_ONLY_DRY_RUN_OUTPUT_INTEGRITY_REVIEW.md"
)

OUTPUT_INTEGRITY_REVIEW_STATUS = (
    "LONG_FORWARD_OBSERVATION_REPORT_ONLY_DRY_RUN_OUTPUT_INTEGRITY_REVIEW_ONLY"
)

READY_DECISION = "REPORT_ONLY_DRY_RUN_OUTPUT_INTEGRITY_REVIEW_PASSED"
BLOCKED_DECISION = "REPORT_ONLY_DRY_RUN_OUTPUT_INTEGRITY_REVIEW_BLOCKED"

RECOMMENDED_NEXT_PHASE = (
    "PHASE_10_9_LONG_FORWARD_OBSERVATION_PRE_START_GATE_V1"
)

EXPECTED_SCHEMA_FIELD_COUNT = 42
EXPECTED_OUTPUT_ROW_COUNT = 1

REQUIRED_ROW_FIELDS = [
    "dry_run_id",
    "design_status",
    "observed_at",
    "symbol",
    "timeframe",
    "candidate_id",
    "observation_role",
    "direction",
    "signal_state",
    "market_context",
    "entry_price",
    "stop_price",
    "target_price",
    "risk_reward",
    "invalidation_level",
    "price_structure_valid",
    "manual_review_required",
    "manual_review_status",
    "reviewer_notes",
    "execution_allowed",
    "dry_run_execution_approved",
    "report_only_dry_run_execution_allowed",
    "forward_observation_start_allowed",
    "live_alert_sent",
    "paper_trade_submitted",
    "real_capital_used",
    "official_dataset_write_allowed",
    "accepted_as_real_evidence",
    "evidence_persistence_allowed",
    "evidence_write_performed",
    "resolution_status",
    "result_r",
    "mfe_r",
    "mae_r",
    "bars_to_resolution",
    "artifact_scope",
    "evidence_source",
    "safety_guard_status",
    "created_at_utc",
    "updated_at_utc",
    "notes",
    "recommended_next_action",
]

EXPECTED_FALSE_OUTPUT_GUARDS = [
    "execution_allowed",
    "dry_run_execution_approved",
    "forward_observation_start_allowed",
    "live_alert_sent",
    "paper_trade_submitted",
    "real_capital_used",
    "official_dataset_write_allowed",
    "accepted_as_real_evidence",
    "evidence_persistence_allowed",
    "evidence_write_performed",
]

EXPECTED_SUMMARY_FALSE_GUARDS = {
    "forward_observation_start_allowed": False,
    "official_dataset_write_performed": False,
    "real_forward_dataset_created": False,
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


def build_output_schema_integrity(
    source_schema_df: pd.DataFrame,
    output_rows_df: pd.DataFrame,
) -> pd.DataFrame:
    output_columns = output_rows_df.columns.astype(str).tolist()

    rows: list[dict[str, Any]] = []

    for position, field_name in enumerate(REQUIRED_ROW_FIELDS, start=1):
        schema_has_field = False

        if not source_schema_df.empty and "field_name" in source_schema_df.columns:
            schema_has_field = field_name in source_schema_df["field_name"].astype(str).tolist()

        output_has_field = field_name in output_columns

        rows.append(
            {
                "field_position": position,
                "field_name": field_name,
                "schema_has_field": schema_has_field,
                "output_has_field": output_has_field,
                "required": True,
                "passed": schema_has_field and output_has_field,
            }
        )

    return pd.DataFrame(rows)


def build_output_row_integrity(output_rows_df: pd.DataFrame) -> pd.DataFrame:
    row = output_rows_df.iloc[0].to_dict() if not output_rows_df.empty else {}

    price_structure_valid = False

    if row:
        try:
            price_structure_valid = (
                float(row.get("stop_price", 0.0))
                < float(row.get("entry_price", 0.0))
                < float(row.get("target_price", 0.0))
            )
        except (TypeError, ValueError):
            price_structure_valid = False

    rows = [
        {
            "integrity_id": "OUTPUT_INTEGRITY_001",
            "integrity_name": "output_row_count_one",
            "passed": int(len(output_rows_df)) == EXPECTED_OUTPUT_ROW_COUNT,
            "required_value": str(EXPECTED_OUTPUT_ROW_COUNT),
            "actual_value": str(len(output_rows_df)),
            "integrity_group": "row_count",
        },
        {
            "integrity_id": "OUTPUT_INTEGRITY_002",
            "integrity_name": "candidate_id_primary",
            "passed": str(row.get("candidate_id", "")) == PRIMARY_RESEARCH_CANDIDATE,
            "required_value": PRIMARY_RESEARCH_CANDIDATE,
            "actual_value": str(row.get("candidate_id", "")),
            "integrity_group": "candidate_scope",
        },
        {
            "integrity_id": "OUTPUT_INTEGRITY_003",
            "integrity_name": "direction_long",
            "passed": str(row.get("direction", "")) == "LONG",
            "required_value": "LONG",
            "actual_value": str(row.get("direction", "")),
            "integrity_group": "direction",
        },
        {
            "integrity_id": "OUTPUT_INTEGRITY_004",
            "integrity_name": "price_structure_valid",
            "passed": price_structure_valid,
            "required_value": "stop_price < entry_price < target_price",
            "actual_value": (
                f"{row.get('stop_price', '')} < "
                f"{row.get('entry_price', '')} < "
                f"{row.get('target_price', '')}"
            ),
            "integrity_group": "price_structure",
        },
        {
            "integrity_id": "OUTPUT_INTEGRITY_005",
            "integrity_name": "risk_reward_2_5",
            "passed": float(row.get("risk_reward", 0.0)) == 2.5 if row else False,
            "required_value": "2.5",
            "actual_value": str(row.get("risk_reward", "")),
            "integrity_group": "risk_reward",
        },
        {
            "integrity_id": "OUTPUT_INTEGRITY_006",
            "integrity_name": "artifact_scope_report_only",
            "passed": str(row.get("artifact_scope", "")) == "REPORT_ONLY_NOT_OFFICIAL_EVIDENCE",
            "required_value": "REPORT_ONLY_NOT_OFFICIAL_EVIDENCE",
            "actual_value": str(row.get("artifact_scope", "")),
            "integrity_group": "artifact_scope",
        },
        {
            "integrity_id": "OUTPUT_INTEGRITY_007",
            "integrity_name": "evidence_source_synthetic_not_real",
            "passed": (
                str(row.get("evidence_source", ""))
                == "CONTROLLED_SYNTHETIC_DRY_RUN_NOT_REAL_MARKET_EVIDENCE"
            ),
            "required_value": "CONTROLLED_SYNTHETIC_DRY_RUN_NOT_REAL_MARKET_EVIDENCE",
            "actual_value": str(row.get("evidence_source", "")),
            "integrity_group": "evidence_source",
        },
        {
            "integrity_id": "OUTPUT_INTEGRITY_008",
            "integrity_name": "safety_guard_status_passed",
            "passed": str(row.get("safety_guard_status", "")) == "PASSED_REPORT_ONLY_GUARDS",
            "required_value": "PASSED_REPORT_ONLY_GUARDS",
            "actual_value": str(row.get("safety_guard_status", "")),
            "integrity_group": "safety",
        },
        {
            "integrity_id": "OUTPUT_INTEGRITY_009",
            "integrity_name": "report_only_execution_allowed_true",
            "passed": safe_bool(row.get("report_only_dry_run_execution_allowed", False)),
            "required_value": "True",
            "actual_value": str(row.get("report_only_dry_run_execution_allowed", "")),
            "integrity_group": "report_only_run",
        },
    ]

    for field_name in EXPECTED_FALSE_OUTPUT_GUARDS:
        rows.append(
            {
                "integrity_id": f"OUTPUT_INTEGRITY_GUARD_{field_name}",
                "integrity_name": f"{field_name}_false",
                "passed": safe_bool(row.get(field_name, True), default=True) is False,
                "required_value": "False",
                "actual_value": str(row.get(field_name, "")),
                "integrity_group": "output_safety_guard",
            }
        )

    return pd.DataFrame(rows)


def build_output_summary_guard_integrity(phase_10_7_summary_df: pd.DataFrame) -> pd.DataFrame:
    summary = (
        phase_10_7_summary_df.iloc[0].to_dict()
        if not phase_10_7_summary_df.empty
        else {}
    )

    rows: list[dict[str, Any]] = []

    for field_name, required_value in EXPECTED_SUMMARY_FALSE_GUARDS.items():
        actual_value = safe_bool(summary.get(field_name, True), default=True)

        rows.append(
            {
                "guard_name": field_name,
                "required_value": required_value,
                "actual_value": actual_value,
                "passed": actual_value is required_value,
                "guard_group": "summary_safety_guard",
            }
        )

    rows.append(
        {
            "guard_name": "official_evidence_rows_written",
            "required_value": 0,
            "actual_value": int(summary.get("official_evidence_rows_written", -1)),
            "passed": int(summary.get("official_evidence_rows_written", -1)) == 0,
            "guard_group": "official_dataset_guard",
        }
    )

    return pd.DataFrame(rows)


def build_output_integrity_requirements(
    phase_10_7_summary_df: pd.DataFrame,
    run_decision_df: pd.DataFrame,
    output_schema_integrity_df: pd.DataFrame,
    output_row_integrity_df: pd.DataFrame,
    summary_guard_integrity_df: pd.DataFrame,
) -> pd.DataFrame:
    summary = (
        phase_10_7_summary_df.iloc[0].to_dict()
        if not phase_10_7_summary_df.empty
        else {}
    )

    decision = run_decision_df.iloc[0].to_dict() if not run_decision_df.empty else {}

    output_schema_complete = (
        not output_schema_integrity_df.empty
        and output_schema_integrity_df["passed"].astype(bool).all()
    )

    output_row_integrity_passed = (
        not output_row_integrity_df.empty
        and output_row_integrity_df["passed"].astype(bool).all()
    )

    summary_guards_passed = (
        not summary_guard_integrity_df.empty
        and summary_guard_integrity_df["passed"].astype(bool).all()
    )

    requirements = [
        {
            "requirement_id": "OUTPUT_INTEGRITY_REVIEW_REQ_001",
            "requirement_name": "phase_10_7_validation_passed",
            "passed": safe_bool(summary.get("validation_passed", False)),
            "required_value": "True",
            "actual_value": str(summary.get("validation_passed", "")),
            "requirement_group": "dependency",
        },
        {
            "requirement_id": "OUTPUT_INTEGRITY_REVIEW_REQ_002",
            "requirement_name": "controlled_report_only_dry_run_run_passed",
            "passed": safe_bool(
                summary.get("controlled_report_only_dry_run_run_passed", False)
            ),
            "required_value": "True",
            "actual_value": str(
                summary.get("controlled_report_only_dry_run_run_passed", "")
            ),
            "requirement_group": "controlled_report_only_run",
        },
        {
            "requirement_id": "OUTPUT_INTEGRITY_REVIEW_REQ_003",
            "requirement_name": "controlled_report_only_dry_run_run_decision_expected",
            "passed": str(
                summary.get("controlled_report_only_dry_run_run_decision", "")
            ).strip()
            == CONTROLLED_REPORT_ONLY_DRY_RUN_READY_DECISION,
            "required_value": CONTROLLED_REPORT_ONLY_DRY_RUN_READY_DECISION,
            "actual_value": str(
                summary.get("controlled_report_only_dry_run_run_decision", "")
            ),
            "requirement_group": "controlled_report_only_run",
        },
        {
            "requirement_id": "OUTPUT_INTEGRITY_REVIEW_REQ_004",
            "requirement_name": "report_only_dry_run_output_review_allowed",
            "passed": safe_bool(
                summary.get("report_only_dry_run_output_review_allowed", False)
            ),
            "required_value": "True",
            "actual_value": str(
                summary.get("report_only_dry_run_output_review_allowed", "")
            ),
            "requirement_group": "review_scope",
        },
        {
            "requirement_id": "OUTPUT_INTEGRITY_REVIEW_REQ_005",
            "requirement_name": "run_decision_table_consistent",
            "passed": (
                not run_decision_df.empty
                and safe_bool(decision.get("controlled_report_only_dry_run_run_passed", False))
                and str(
                    decision.get("controlled_report_only_dry_run_run_decision", "")
                ).strip()
                == CONTROLLED_REPORT_ONLY_DRY_RUN_READY_DECISION
            ),
            "required_value": "True",
            "actual_value": str(
                decision.get("controlled_report_only_dry_run_run_decision", "")
            ),
            "requirement_group": "summary_consistency",
        },
        {
            "requirement_id": "OUTPUT_INTEGRITY_REVIEW_REQ_006",
            "requirement_name": "output_schema_field_count_42",
            "passed": int(len(output_schema_integrity_df)) == EXPECTED_SCHEMA_FIELD_COUNT,
            "required_value": str(EXPECTED_SCHEMA_FIELD_COUNT),
            "actual_value": str(len(output_schema_integrity_df)),
            "requirement_group": "schema",
        },
        {
            "requirement_id": "OUTPUT_INTEGRITY_REVIEW_REQ_007",
            "requirement_name": "output_schema_complete",
            "passed": output_schema_complete,
            "required_value": "True",
            "actual_value": str(output_schema_complete),
            "requirement_group": "schema",
        },
        {
            "requirement_id": "OUTPUT_INTEGRITY_REVIEW_REQ_008",
            "requirement_name": "output_row_integrity_passed",
            "passed": output_row_integrity_passed,
            "required_value": "True",
            "actual_value": str(output_row_integrity_passed),
            "requirement_group": "output_integrity",
        },
        {
            "requirement_id": "OUTPUT_INTEGRITY_REVIEW_REQ_009",
            "requirement_name": "summary_guards_passed",
            "passed": summary_guards_passed,
            "required_value": "True",
            "actual_value": str(summary_guards_passed),
            "requirement_group": "safety",
        },
        {
            "requirement_id": "OUTPUT_INTEGRITY_REVIEW_REQ_010",
            "requirement_name": "official_dataset_not_written",
            "passed": safe_bool(
                summary.get("official_dataset_write_performed", True),
                default=True,
            )
            is False,
            "required_value": "False",
            "actual_value": str(summary.get("official_dataset_write_performed", "")),
            "requirement_group": "official_dataset_guard",
        },
        {
            "requirement_id": "OUTPUT_INTEGRITY_REVIEW_REQ_011",
            "requirement_name": "official_evidence_rows_written_zero",
            "passed": int(summary.get("official_evidence_rows_written", -1)) == 0,
            "required_value": "0",
            "actual_value": str(summary.get("official_evidence_rows_written", "")),
            "requirement_group": "official_dataset_guard",
        },
        {
            "requirement_id": "OUTPUT_INTEGRITY_REVIEW_REQ_012",
            "requirement_name": "forward_observation_not_started",
            "passed": safe_bool(
                summary.get("forward_observation_started", True),
                default=True,
            )
            is False,
            "required_value": "False",
            "actual_value": str(summary.get("forward_observation_started", "")),
            "requirement_group": "start_boundary",
        },
        {
            "requirement_id": "OUTPUT_INTEGRITY_REVIEW_REQ_013",
            "requirement_name": "market_execution_disabled",
            "passed": safe_bool(
                summary.get("market_execution_allowed", True),
                default=True,
            )
            is False,
            "required_value": "False",
            "actual_value": str(summary.get("market_execution_allowed", "")),
            "requirement_group": "market_execution_guard",
        },
        {
            "requirement_id": "OUTPUT_INTEGRITY_REVIEW_REQ_014",
            "requirement_name": "total_project_not_completed",
            "passed": safe_bool(
                summary.get("total_project_completed", True),
                default=True,
            )
            is False,
            "required_value": "False",
            "actual_value": str(summary.get("total_project_completed", "")),
            "requirement_group": "scope_control",
        },
    ]

    return pd.DataFrame(requirements)


def build_output_integrity_boundary_matrix() -> pd.DataFrame:
    rows = [
        {
            "boundary_item": "report_only_dry_run_output_integrity_review_allowed",
            "allowed": True,
            "boundary_type": "review_scope",
            "details": "Phase 10.8 may review report-only dry-run output integrity.",
        },
        {
            "boundary_item": "forward_observation_pre_start_review_allowed",
            "allowed": True,
            "boundary_type": "future_review",
            "details": "Phase 10.8 may recommend a future pre-start gate review.",
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


def build_output_integrity_decision_table(
    requirements_df: pd.DataFrame,
    boundary_matrix_df: pd.DataFrame,
    output_schema_integrity_df: pd.DataFrame,
    output_row_integrity_df: pd.DataFrame,
    summary_guard_integrity_df: pd.DataFrame,
) -> pd.DataFrame:
    total_requirements = int(len(requirements_df))
    passed_requirements = (
        int(requirements_df["passed"].astype(bool).sum())
        if total_requirements
        else 0
    )
    failed_requirements = total_requirements - passed_requirements

    output_schema_complete = (
        not output_schema_integrity_df.empty
        and output_schema_integrity_df["passed"].astype(bool).all()
    )

    output_row_integrity_passed = (
        not output_row_integrity_df.empty
        and output_row_integrity_df["passed"].astype(bool).all()
    )

    summary_guards_passed = (
        not summary_guard_integrity_df.empty
        and summary_guard_integrity_df["passed"].astype(bool).all()
    )

    allowed_review_items = {
        "report_only_dry_run_output_integrity_review_allowed",
        "forward_observation_pre_start_review_allowed",
    }

    disallowed_rows = boundary_matrix_df[
        ~boundary_matrix_df["boundary_item"].astype(str).isin(allowed_review_items)
    ]

    disallowed_operational_boundaries_passed = (
        not disallowed_rows.empty
        and disallowed_rows["allowed"].astype(bool).eq(False).all()
    )

    output_integrity_passed = (
        total_requirements > 0
        and failed_requirements == 0
        and output_schema_complete
        and output_row_integrity_passed
        and summary_guards_passed
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
                "report_only_dry_run_output_integrity_review_id": (
                    "PHASE_10_8_REPORT_ONLY_DRY_RUN_OUTPUT_INTEGRITY_REVIEW_001"
                ),
                "report_only_dry_run_output_integrity_review_status": (
                    OUTPUT_INTEGRITY_REVIEW_STATUS
                ),
                "report_only_dry_run_output_integrity_passed": output_integrity_passed,
                "report_only_dry_run_output_integrity_decision": (
                    READY_DECISION if output_integrity_passed else BLOCKED_DECISION
                ),
                "total_requirements": total_requirements,
                "passed_requirements": passed_requirements,
                "failed_requirements": failed_requirements,
                "failed_requirement_names": failed_requirement_names,
                "output_schema_complete": output_schema_complete,
                "output_row_integrity_passed": output_row_integrity_passed,
                "summary_guards_passed": summary_guards_passed,
                "disallowed_operational_boundaries_passed": (
                    disallowed_operational_boundaries_passed
                ),
                "forward_observation_pre_start_review_allowed": output_integrity_passed,
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


def validate_long_forward_observation_report_only_dry_run_output_integrity_review() -> dict[str, pd.DataFrame]:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    checks: list[dict[str, Any]] = []

    phase_anchors = {
        "phase_10_7_controlled_report_only_dry_run_run_doc_exists": (
            PHASE_10_7_CONTROLLED_REPORT_ONLY_DRY_RUN_RUN_DOC_PATH
        ),
        "phase_10_8_report_only_dry_run_output_integrity_review_doc_exists": (
            PHASE_10_8_REPORT_ONLY_DRY_RUN_OUTPUT_INTEGRITY_REVIEW_DOC_PATH
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

    phase_10_7_result = (
        validate_long_forward_observation_controlled_report_only_dry_run_run()
    )

    phase_10_7_summary_df = phase_10_7_result["summary"]
    source_report_only_dry_run_schema_df = phase_10_7_result[
        "source_report_only_dry_run_schema"
    ]
    source_controlled_report_only_dry_run_rows_df = phase_10_7_result[
        "controlled_report_only_dry_run_rows"
    ]
    source_run_schema_compatibility_df = phase_10_7_result[
        "run_schema_compatibility"
    ]
    source_run_assertions_df = phase_10_7_result["run_assertions"]
    source_run_requirements_df = phase_10_7_result["run_requirements"]
    source_run_boundary_matrix_df = phase_10_7_result["run_boundary_matrix"]
    source_run_safety_matrix_df = phase_10_7_result["run_safety_matrix"]
    source_run_decision_df = phase_10_7_result["run_decision"]
    source_checks_df = phase_10_7_result["checks"]

    phase_10_7_validation_passed = (
        not phase_10_7_summary_df.empty
        and bool(phase_10_7_summary_df.iloc[0].get("validation_passed", False))
    )

    controlled_run_passed = (
        not phase_10_7_summary_df.empty
        and safe_bool(
            phase_10_7_summary_df.iloc[0].get(
                "controlled_report_only_dry_run_run_passed",
                False,
            )
        )
    )

    output_schema_integrity_df = build_output_schema_integrity(
        source_schema_df=source_report_only_dry_run_schema_df,
        output_rows_df=source_controlled_report_only_dry_run_rows_df,
    )

    output_row_integrity_df = build_output_row_integrity(
        source_controlled_report_only_dry_run_rows_df
    )

    summary_guard_integrity_df = build_output_summary_guard_integrity(
        phase_10_7_summary_df
    )

    output_integrity_requirements_df = build_output_integrity_requirements(
        phase_10_7_summary_df=phase_10_7_summary_df,
        run_decision_df=source_run_decision_df,
        output_schema_integrity_df=output_schema_integrity_df,
        output_row_integrity_df=output_row_integrity_df,
        summary_guard_integrity_df=summary_guard_integrity_df,
    )

    output_integrity_boundary_matrix_df = build_output_integrity_boundary_matrix()

    output_integrity_decision_df = build_output_integrity_decision_table(
        requirements_df=output_integrity_requirements_df,
        boundary_matrix_df=output_integrity_boundary_matrix_df,
        output_schema_integrity_df=output_schema_integrity_df,
        output_row_integrity_df=output_row_integrity_df,
        summary_guard_integrity_df=summary_guard_integrity_df,
    )

    official_dataset_exists_after = OFFICIAL_DATASET_PATH.exists()

    decision = (
        output_integrity_decision_df.iloc[0].to_dict()
        if not output_integrity_decision_df.empty
        else {}
    )

    output_integrity_passed = safe_bool(
        decision.get("report_only_dry_run_output_integrity_passed", False)
    )

    output_integrity_decision = str(
        decision.get("report_only_dry_run_output_integrity_decision", "")
    )

    forward_observation_pre_start_review_allowed = safe_bool(
        decision.get("forward_observation_pre_start_review_allowed", False)
    )

    phase_10_7_summary = (
        phase_10_7_summary_df.iloc[0].to_dict()
        if not phase_10_7_summary_df.empty
        else {}
    )

    output_schema_complete = (
        not output_schema_integrity_df.empty
        and output_schema_integrity_df["passed"].astype(bool).all()
    )

    output_row_integrity_passed = (
        not output_row_integrity_df.empty
        and output_row_integrity_df["passed"].astype(bool).all()
    )

    summary_guards_passed = (
        not summary_guard_integrity_df.empty
        and summary_guard_integrity_df["passed"].astype(bool).all()
    )

    checks.append(
        build_check(
            check_group="phase_dependency",
            check_name="phase_10_7_validation_passed",
            passed=phase_10_7_validation_passed,
            severity="INFO" if phase_10_7_validation_passed else "ERROR",
            details=str(phase_10_7_summary.get("validation_decision", "")),
        )
    )

    checks.append(
        build_check(
            check_group="phase_dependency",
            check_name="controlled_report_only_dry_run_run_passed",
            passed=controlled_run_passed,
            severity="INFO" if controlled_run_passed else "ERROR",
            details=f"controlled_report_only_dry_run_run_passed={controlled_run_passed}",
        )
    )

    checks.append(
        build_check(
            check_group="output_integrity",
            check_name="output_schema_complete",
            passed=output_schema_complete,
            severity="INFO" if output_schema_complete else "ERROR",
            details=(
                "missing_fields="
                + ",".join(
                    output_schema_integrity_df[
                        ~output_schema_integrity_df["passed"].astype(bool)
                    ]["field_name"].astype(str)
                )
                if not output_schema_integrity_df.empty
                else "missing_fields=all"
            ),
        )
    )

    checks.append(
        build_check(
            check_group="output_integrity",
            check_name="output_row_integrity_passed",
            passed=output_row_integrity_passed,
            severity="INFO" if output_row_integrity_passed else "ERROR",
            details=(
                "failed_integrity_checks="
                + ",".join(
                    output_row_integrity_df[
                        ~output_row_integrity_df["passed"].astype(bool)
                    ]["integrity_name"].astype(str)
                )
                if not output_row_integrity_df.empty
                else "failed_integrity_checks=all"
            ),
        )
    )

    checks.append(
        build_check(
            check_group="output_integrity",
            check_name="summary_guards_passed",
            passed=summary_guards_passed,
            severity="INFO" if summary_guards_passed else "ERROR",
            details=(
                "failed_guards="
                + ",".join(
                    summary_guard_integrity_df[
                        ~summary_guard_integrity_df["passed"].astype(bool)
                    ]["guard_name"].astype(str)
                )
                if not summary_guard_integrity_df.empty
                else "failed_guards=all"
            ),
        )
    )

    checks.append(
        build_check(
            check_group="output_integrity",
            check_name="report_only_dry_run_output_integrity_passed",
            passed=output_integrity_passed,
            severity="INFO" if output_integrity_passed else "ERROR",
            details=f"report_only_dry_run_output_integrity_passed={output_integrity_passed}",
        )
    )

    checks.append(
        build_check(
            check_group="output_integrity",
            check_name="report_only_dry_run_output_integrity_decision_expected",
            passed=output_integrity_decision == READY_DECISION,
            severity="INFO" if output_integrity_decision == READY_DECISION else "ERROR",
            details=(
                "report_only_dry_run_output_integrity_decision="
                + output_integrity_decision
            ),
        )
    )

    checks.append(
        build_check(
            check_group="planning_scope",
            check_name="forward_observation_pre_start_review_allowed",
            passed=forward_observation_pre_start_review_allowed,
            severity=(
                "WARNING"
                if forward_observation_pre_start_review_allowed
                else "ERROR"
            ),
            details=(
                "This allows only a future pre-start review, not forward observation "
                "start, alerts, paper trading, real capital, official evidence "
                "persistence, or market execution."
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

    for _, guard_row in summary_guard_integrity_df.iterrows():
        checks.append(
            build_check(
                check_group="summary_safety_flags",
                check_name=str(guard_row["guard_name"]),
                passed=safe_bool(guard_row["passed"], False),
                severity="INFO" if safe_bool(guard_row["passed"], False) else "ERROR",
                details=(
                    f"{guard_row['guard_name']}="
                    f"{guard_row['actual_value']} "
                    f"(required={guard_row['required_value']})"
                ),
            )
        )

    checks.append(
        build_check(
            check_group="scope_control",
            check_name="output_integrity_review_only",
            passed=True,
            severity="WARNING",
            details="Phase 10.8 reviews report-only dry-run output integrity only.",
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
            check_name="phase_10_9_recommended_next",
            passed=True,
            severity="INFO",
            details=(
                "Recommended next step: "
                "Phase 10.9 LONG Forward Observation Pre-Start Gate V1."
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
                "phase": "10.8",
                "long_forward_observation_report_only_dry_run_output_integrity_review_defined": True,
                "phase_10_7_validation_passed": phase_10_7_validation_passed,
                "controlled_report_only_dry_run_run_passed": controlled_run_passed,
                "controlled_report_only_dry_run_run_decision": str(
                    phase_10_7_summary.get(
                        "controlled_report_only_dry_run_run_decision",
                        "",
                    )
                ),
                "report_only_dry_run_output_review_allowed": safe_bool(
                    phase_10_7_summary.get(
                        "report_only_dry_run_output_review_allowed",
                        False,
                    )
                ),
                "report_only_dry_run_output_row_count": int(
                    len(source_controlled_report_only_dry_run_rows_df)
                ),
                "report_only_dry_run_output_schema_field_count": int(
                    len(output_schema_integrity_df)
                ),
                "report_only_dry_run_output_schema_complete": output_schema_complete,
                "report_only_dry_run_output_candidate_valid": bool(
                    output_row_integrity_df[
                        output_row_integrity_df["integrity_name"].eq(
                            "candidate_id_primary"
                        )
                    ]["passed"].iloc[0]
                ),
                "report_only_dry_run_output_direction_valid": bool(
                    output_row_integrity_df[
                        output_row_integrity_df["integrity_name"].eq("direction_long")
                    ]["passed"].iloc[0]
                ),
                "report_only_dry_run_output_price_structure_valid": bool(
                    output_row_integrity_df[
                        output_row_integrity_df["integrity_name"].eq(
                            "price_structure_valid"
                        )
                    ]["passed"].iloc[0]
                ),
                "report_only_dry_run_output_artifact_scope_valid": bool(
                    output_row_integrity_df[
                        output_row_integrity_df["integrity_name"].eq(
                            "artifact_scope_report_only"
                        )
                    ]["passed"].iloc[0]
                ),
                "report_only_dry_run_output_evidence_source_valid": bool(
                    output_row_integrity_df[
                        output_row_integrity_df["integrity_name"].eq(
                            "evidence_source_synthetic_not_real"
                        )
                    ]["passed"].iloc[0]
                ),
                "report_only_dry_run_output_safety_guards_valid": summary_guards_passed,
                "report_only_dry_run_output_integrity_passed": output_integrity_passed,
                "report_only_dry_run_output_integrity_decision": (
                    output_integrity_decision
                ),
                "forward_observation_pre_start_review_allowed": (
                    forward_observation_pre_start_review_allowed
                ),
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
                "estimated_phase_10_progress_percent": 80,
                "total_checks": int(len(checks_df)),
                "warning_count": warning_count,
                "error_count": error_count,
                "blocker_count": blocker_count,
                "validation_passed": validation_passed,
                "validation_decision": (
                    "PHASE_10_8_LONG_FORWARD_OBSERVATION_REPORT_ONLY_DRY_RUN_OUTPUT_INTEGRITY_REVIEW_VALIDATED"
                    if validation_passed
                    else "PHASE_10_8_LONG_FORWARD_OBSERVATION_REPORT_ONLY_DRY_RUN_OUTPUT_INTEGRITY_REVIEW_FAILED"
                ),
            }
        ]
    )

    phase_10_7_summary_df.to_csv(
        REPORTS_DIR / "phase_10_7_source_summary_v1.csv",
        index=False,
    )
    source_report_only_dry_run_schema_df.to_csv(
        REPORTS_DIR / "phase_10_7_source_report_only_dry_run_schema_v1.csv",
        index=False,
    )
    source_controlled_report_only_dry_run_rows_df.to_csv(
        REPORTS_DIR / "phase_10_7_source_controlled_report_only_dry_run_rows_v1.csv",
        index=False,
    )
    source_run_schema_compatibility_df.to_csv(
        REPORTS_DIR / "phase_10_7_source_run_schema_compatibility_v1.csv",
        index=False,
    )
    source_run_assertions_df.to_csv(
        REPORTS_DIR / "phase_10_7_source_run_assertions_v1.csv",
        index=False,
    )
    source_run_requirements_df.to_csv(
        REPORTS_DIR / "phase_10_7_source_run_requirements_v1.csv",
        index=False,
    )
    source_run_boundary_matrix_df.to_csv(
        REPORTS_DIR / "phase_10_7_source_run_boundary_matrix_v1.csv",
        index=False,
    )
    source_run_safety_matrix_df.to_csv(
        REPORTS_DIR / "phase_10_7_source_run_safety_matrix_v1.csv",
        index=False,
    )
    source_run_decision_df.to_csv(
        REPORTS_DIR / "phase_10_7_source_run_decision_v1.csv",
        index=False,
    )
    source_checks_df.to_csv(
        REPORTS_DIR / "phase_10_7_source_checks_v1.csv",
        index=False,
    )
    output_schema_integrity_df.to_csv(
        REPORTS_DIR / "long_forward_observation_report_only_dry_run_output_schema_integrity_v1.csv",
        index=False,
    )
    output_row_integrity_df.to_csv(
        REPORTS_DIR / "long_forward_observation_report_only_dry_run_output_row_integrity_v1.csv",
        index=False,
    )
    summary_guard_integrity_df.to_csv(
        REPORTS_DIR / "long_forward_observation_report_only_dry_run_output_summary_guard_integrity_v1.csv",
        index=False,
    )
    output_integrity_requirements_df.to_csv(
        REPORTS_DIR / "long_forward_observation_report_only_dry_run_output_integrity_requirements_v1.csv",
        index=False,
    )
    output_integrity_boundary_matrix_df.to_csv(
        REPORTS_DIR / "long_forward_observation_report_only_dry_run_output_integrity_boundary_matrix_v1.csv",
        index=False,
    )
    output_integrity_decision_df.to_csv(
        REPORTS_DIR / "long_forward_observation_report_only_dry_run_output_integrity_decision_v1.csv",
        index=False,
    )
    checks_df.to_csv(
        REPORTS_DIR / "long_forward_observation_report_only_dry_run_output_integrity_checks_v1.csv",
        index=False,
    )
    summary_df.to_csv(
        REPORTS_DIR / "long_forward_observation_report_only_dry_run_output_integrity_summary_v1.csv",
        index=False,
    )

    return {
        "summary": summary_df,
        "source_phase_10_7_summary": phase_10_7_summary_df,
        "source_report_only_dry_run_schema": source_report_only_dry_run_schema_df,
        "source_controlled_report_only_dry_run_rows": (
            source_controlled_report_only_dry_run_rows_df
        ),
        "source_run_schema_compatibility": source_run_schema_compatibility_df,
        "source_run_assertions": source_run_assertions_df,
        "source_run_requirements": source_run_requirements_df,
        "source_run_boundary_matrix": source_run_boundary_matrix_df,
        "source_run_safety_matrix": source_run_safety_matrix_df,
        "source_run_decision": source_run_decision_df,
        "source_checks": source_checks_df,
        "output_schema_integrity": output_schema_integrity_df,
        "output_row_integrity": output_row_integrity_df,
        "summary_guard_integrity": summary_guard_integrity_df,
        "output_integrity_requirements": output_integrity_requirements_df,
        "output_integrity_boundary_matrix": output_integrity_boundary_matrix_df,
        "output_integrity_decision": output_integrity_decision_df,
        "checks": checks_df,
    }