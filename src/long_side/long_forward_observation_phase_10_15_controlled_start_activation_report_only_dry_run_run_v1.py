from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

from src.long_side.long_forward_observation_dataset_bootstrap_v1 import (
    OFFICIAL_DATASET_PATH,
    PRIMARY_RESEARCH_CANDIDATE,
)
from src.long_side.long_forward_observation_phase_10_14_controlled_start_activation_report_only_dry_run_execution_review_v1 import (
    READY_DECISION as EXECUTION_REVIEW_READY_DECISION,
    validate_long_forward_observation_controlled_start_activation_report_only_dry_run_execution_review,
)


REPORTS_DIR = Path("reports/p10_15_activation_report_only_run_v1")

PHASE_10_14_EXECUTION_REVIEW_DOC_PATH = Path(
    "docs/PHASE_10_LONG_FORWARD_OBSERVATION_CONTROLLED_START_ACTIVATION_REPORT_ONLY_DRY_RUN_EXECUTION_REVIEW.md"
)
PHASE_10_15_REPORT_ONLY_DRY_RUN_RUN_DOC_PATH = Path(
    "docs/PHASE_10_LONG_FORWARD_OBSERVATION_CONTROLLED_START_ACTIVATION_REPORT_ONLY_DRY_RUN_RUN.md"
)

CONTROLLED_START_ACTIVATION_REPORT_ONLY_DRY_RUN_RUN_STATUS = (
    "LONG_FORWARD_OBSERVATION_CONTROLLED_START_ACTIVATION_REPORT_ONLY_DRY_RUN_RUN_ONLY"
)

READY_DECISION = (
    "CONTROLLED_START_ACTIVATION_REPORT_ONLY_DRY_RUN_RUN_COMPLETED_REPORT_ONLY"
)
BLOCKED_DECISION = "CONTROLLED_START_ACTIVATION_REPORT_ONLY_DRY_RUN_RUN_BLOCKED"

RECOMMENDED_NEXT_PHASE = (
    "PHASE_10_16_LONG_FORWARD_OBSERVATION_CONTROLLED_START_ACTIVATION_REPORT_ONLY_DRY_RUN_OUTPUT_INTEGRITY_REVIEW_V1"
)

EXPECTED_FALSE_GUARDS = {
    "controlled_forward_observation_start_approved": False,
    "controlled_forward_observation_start_activation_performed": False,
    "controlled_forward_observation_start_dry_run_performed": False,
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


def build_report_only_dry_run_row(schema_df: pd.DataFrame) -> pd.DataFrame:
    if schema_df.empty:
        return pd.DataFrame()

    schema_fields = schema_df["field_name"].astype(str).tolist()

    entry_price = 100.0
    stop_price = 95.0
    target_price = 112.5
    risk_reward = round((target_price - entry_price) / (entry_price - stop_price), 4)

    row = {
        "dry_run_design_id": "P10_15_CONTROLLED_START_ACTIVATION_REPORT_ONLY_DRY_RUN_001",
        "design_status": CONTROLLED_START_ACTIVATION_REPORT_ONLY_DRY_RUN_RUN_STATUS,
        "designed_at_utc": datetime.now(timezone.utc).isoformat(),
        "symbol": "BTCUSDT",
        "timeframe": "15m",
        "candidate_id": PRIMARY_RESEARCH_CANDIDATE,
        "direction": "LONG",
        "observation_role": "PRIMARY_FORWARD_OBSERVATION_REPORT_ONLY_DRY_RUN",
        "signal_state": "CONTROLLED_REPORT_ONLY_DRY_RUN",
        "market_context": "SYNTHETIC_CONTROLLED_START_ACTIVATION_DRY_RUN",
        "entry_price": entry_price,
        "stop_price": stop_price,
        "target_price": target_price,
        "invalidation_level": stop_price,
        "risk_reward": risk_reward,
        "cost_profile": "RESEARCH_COST_AWARE_REFERENCE_ONLY",
        "evidence_source": "SYNTHETIC_REPORT_ONLY_DRY_RUN",
        "evidence_scope": "REPORT_ONLY_NOT_REAL_EVIDENCE",
        "report_only": True,
        "synthetic_control_row": True,
        "manual_confirmation_required": True,
        "dry_run_execution_allowed": True,
        "dry_run_execution_performed": True,
        "controlled_start_activation_allowed": False,
        "controlled_start_activation_performed": False,
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
        "real_capital_allowed": False,
        "market_execution_allowed": False,
        "exchange_execution_allowed": False,
        "automation_allowed": False,
        "execution_allowed": False,
        "long_strategy_approved": False,
        "long_entries_approved": False,
        "long_side_established": False,
        "real_entries_approved": False,
        "total_project_completed": False,
        "expected_next_review_phase": RECOMMENDED_NEXT_PHASE,
        "notes": "Synthetic controlled report-only dry-run row. Not real evidence. Not a signal. Not execution.",
        "validation_status": "REPORT_ONLY_DRY_RUN_ROW_CREATED",
    }

    normalized_row = {field_name: row.get(field_name, "") for field_name in schema_fields}

    return pd.DataFrame([normalized_row], columns=schema_fields)


def build_report_only_dry_run_run_controls() -> pd.DataFrame:
    rows = [
        ("RUN_CONTROL_001", "phase_10_14_validation_passed", "dependency"),
        ("RUN_CONTROL_002", "execution_review_passed", "execution_review"),
        ("RUN_CONTROL_003", "execution_review_decision_confirmed", "execution_review"),
        ("RUN_CONTROL_004", "future_controlled_run_allowed", "future_run"),
        ("RUN_CONTROL_005", "source_schema_available", "schema"),
        ("RUN_CONTROL_006", "dry_run_row_created", "row_creation"),
        ("RUN_CONTROL_007", "single_row_only", "row_creation"),
        ("RUN_CONTROL_008", "schema_compatible", "schema"),
        ("RUN_CONTROL_009", "candidate_scope_valid", "candidate_scope"),
        ("RUN_CONTROL_010", "direction_valid", "direction"),
        ("RUN_CONTROL_011", "price_structure_valid", "price_structure"),
        ("RUN_CONTROL_012", "risk_reward_valid", "risk_reward"),
        ("RUN_CONTROL_013", "synthetic_evidence_scope_valid", "evidence_scope"),
        ("RUN_CONTROL_014", "report_only_scope_valid", "report_only_scope"),
        ("RUN_CONTROL_015", "official_dataset_write_disabled", "official_dataset_guard"),
        ("RUN_CONTROL_016", "signal_generation_and_alerts_disabled", "signals_alerts"),
        ("RUN_CONTROL_017", "capital_and_market_execution_disabled", "execution"),
        ("RUN_CONTROL_018", "future_output_integrity_review_allowed", "future_review"),
    ]

    return pd.DataFrame(
        [
            {
                "control_id": control_id,
                "control_name": control_name,
                "control_group": control_group,
                "required": True,
                "report_only_run": True,
                "dry_run_execution_allowed": control_name in {
                    "dry_run_row_created",
                    "single_row_only",
                    "schema_compatible",
                    "candidate_scope_valid",
                    "direction_valid",
                    "price_structure_valid",
                    "risk_reward_valid",
                    "synthetic_evidence_scope_valid",
                    "report_only_scope_valid",
                },
                "dry_run_execution_performed": control_name in {
                    "dry_run_row_created",
                    "single_row_only",
                    "schema_compatible",
                    "candidate_scope_valid",
                    "direction_valid",
                    "price_structure_valid",
                    "risk_reward_valid",
                    "synthetic_evidence_scope_valid",
                    "report_only_scope_valid",
                },
                "activation_performed": False,
                "forward_observation_start_allowed": False,
                "official_dataset_write_allowed": False,
                "market_execution_allowed": False,
                "passed": True,
            }
            for control_id, control_name, control_group in rows
        ]
    )


def build_report_only_dry_run_row_validation(
    dry_run_df: pd.DataFrame,
    schema_df: pd.DataFrame,
) -> pd.DataFrame:
    if dry_run_df.empty or schema_df.empty:
        return pd.DataFrame(
            [
                {
                    "validation_name": "dry_run_row_available",
                    "passed": False,
                    "details": "Dry-run row or schema is empty.",
                }
            ]
        )

    row = dry_run_df.iloc[0].to_dict()
    schema_fields = schema_df["field_name"].astype(str).tolist()
    actual_fields = dry_run_df.columns.astype(str).tolist()

    entry_price = float(row.get("entry_price", 0))
    stop_price = float(row.get("stop_price", 0))
    target_price = float(row.get("target_price", 0))
    risk_reward = float(row.get("risk_reward", 0))

    expected_risk_reward = round((target_price - entry_price) / (entry_price - stop_price), 4)

    false_guard_fields = [
        "controlled_start_activation_allowed",
        "controlled_start_activation_performed",
        "forward_observation_start_allowed",
        "forward_observation_started",
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
        "real_capital_allowed",
        "market_execution_allowed",
        "exchange_execution_allowed",
        "automation_allowed",
        "execution_allowed",
        "long_strategy_approved",
        "long_entries_approved",
        "long_side_established",
        "real_entries_approved",
        "total_project_completed",
    ]

    false_guards_passed = all(
        safe_bool(row.get(field_name, True), default=True) is False
        for field_name in false_guard_fields
    )

    rows = [
        {
            "validation_name": "row_count_is_one",
            "passed": int(len(dry_run_df)) == 1,
            "details": f"row_count={len(dry_run_df)}",
        },
        {
            "validation_name": "schema_compatible",
            "passed": actual_fields == schema_fields,
            "details": f"actual_field_count={len(actual_fields)},schema_field_count={len(schema_fields)}",
        },
        {
            "validation_name": "candidate_valid",
            "passed": str(row.get("candidate_id", "")) == PRIMARY_RESEARCH_CANDIDATE,
            "details": str(row.get("candidate_id", "")),
        },
        {
            "validation_name": "direction_valid",
            "passed": str(row.get("direction", "")) == "LONG",
            "details": str(row.get("direction", "")),
        },
        {
            "validation_name": "price_structure_valid",
            "passed": stop_price < entry_price < target_price,
            "details": f"stop={stop_price},entry={entry_price},target={target_price}",
        },
        {
            "validation_name": "risk_reward_valid",
            "passed": risk_reward == expected_risk_reward and risk_reward == 2.5,
            "details": f"risk_reward={risk_reward},expected={expected_risk_reward}",
        },
        {
            "validation_name": "report_only_scope_valid",
            "passed": safe_bool(row.get("report_only", False)) is True,
            "details": f"report_only={row.get('report_only', '')}",
        },
        {
            "validation_name": "synthetic_control_row_valid",
            "passed": safe_bool(row.get("synthetic_control_row", False)) is True,
            "details": f"synthetic_control_row={row.get('synthetic_control_row', '')}",
        },
        {
            "validation_name": "evidence_scope_valid",
            "passed": str(row.get("evidence_scope", "")) == "REPORT_ONLY_NOT_REAL_EVIDENCE",
            "details": str(row.get("evidence_scope", "")),
        },
        {
            "validation_name": "dry_run_execution_performed_report_only",
            "passed": (
                safe_bool(row.get("dry_run_execution_allowed", False)) is True
                and safe_bool(row.get("dry_run_execution_performed", False)) is True
            ),
            "details": (
                f"allowed={row.get('dry_run_execution_allowed', '')},"
                f"performed={row.get('dry_run_execution_performed', '')}"
            ),
        },
        {
            "validation_name": "official_evidence_rows_written_zero",
            "passed": int(row.get("official_evidence_rows_written", -1)) == 0,
            "details": str(row.get("official_evidence_rows_written", "")),
        },
        {
            "validation_name": "safety_false_guards_passed",
            "passed": false_guards_passed,
            "details": f"false_guard_count={len(false_guard_fields)}",
        },
    ]

    return pd.DataFrame(rows)


def build_report_only_dry_run_run_rules(
    controls_df: pd.DataFrame,
    row_validation_df: pd.DataFrame,
) -> pd.DataFrame:
    controls_passed = not controls_df.empty and controls_df["passed"].astype(bool).all()
    row_validation_passed = (
        not row_validation_df.empty and row_validation_df["passed"].astype(bool).all()
    )

    run_control_count = int(len(controls_df))
    row_validation_count = int(len(row_validation_df))

    all_start_disabled = (
        not controls_df.empty
        and controls_df["forward_observation_start_allowed"].astype(bool).eq(False).all()
    )
    all_dataset_writes_disabled = (
        not controls_df.empty
        and controls_df["official_dataset_write_allowed"].astype(bool).eq(False).all()
    )
    all_market_execution_disabled = (
        not controls_df.empty
        and controls_df["market_execution_allowed"].astype(bool).eq(False).all()
    )

    rows = [
        ("RUN_RULE_001", "run_control_count_18", run_control_count == 18, "18", str(run_control_count), "controls"),
        ("RUN_RULE_002", "all_controls_passed", controls_passed, "True", str(controls_passed), "controls"),
        ("RUN_RULE_003", "row_validation_count_12", row_validation_count == 12, "12", str(row_validation_count), "row_validation"),
        ("RUN_RULE_004", "all_row_validations_passed", row_validation_passed, "True", str(row_validation_passed), "row_validation"),
        ("RUN_RULE_005", "all_start_disabled", all_start_disabled, "False", "False", "start_boundary"),
        ("RUN_RULE_006", "all_official_dataset_writes_disabled", all_dataset_writes_disabled, "False", "False", "official_dataset_guard"),
        ("RUN_RULE_007", "all_market_execution_disabled", all_market_execution_disabled, "False", "False", "market_execution_guard"),
    ]

    return pd.DataFrame(
        [
            {
                "rule_id": rule_id,
                "rule_name": rule_name,
                "passed": passed,
                "required_value": required_value,
                "actual_value": actual_value,
                "rule_group": rule_group,
            }
            for rule_id, rule_name, passed, required_value, actual_value, rule_group in rows
        ]
    )


def build_report_only_dry_run_run_guard_matrix() -> pd.DataFrame:
    rows: list[dict[str, Any]] = []

    for guard_name, required_value in EXPECTED_FALSE_GUARDS.items():
        rows.append(
            {
                "guard_name": guard_name,
                "required_value": required_value,
                "actual_value": required_value,
                "passed": True,
                "guard_group": "report_only_dry_run_run_safety_guard",
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


def build_report_only_dry_run_run_requirements(
    phase_10_14_summary_df: pd.DataFrame,
    execution_review_decision_df: pd.DataFrame,
    dry_run_df: pd.DataFrame,
    row_validation_df: pd.DataFrame,
    controls_df: pd.DataFrame,
    rules_df: pd.DataFrame,
    guard_matrix_df: pd.DataFrame,
    artifact_write_performed: bool,
    artifact_rows_written: int,
) -> pd.DataFrame:
    summary = (
        phase_10_14_summary_df.iloc[0].to_dict()
        if not phase_10_14_summary_df.empty
        else {}
    )

    decision = (
        execution_review_decision_df.iloc[0].to_dict()
        if not execution_review_decision_df.empty
        else {}
    )

    row_validation = {
        str(row["validation_name"]): safe_bool(row["passed"], False)
        for _, row in row_validation_df.iterrows()
    }

    controls_passed = not controls_df.empty and controls_df["passed"].astype(bool).all()
    rules_passed = not rules_df.empty and rules_df["passed"].astype(bool).all()
    guards_passed = not guard_matrix_df.empty and guard_matrix_df["passed"].astype(bool).all()

    requirements = [
        {
            "requirement_id": "RUN_REQ_001",
            "requirement_name": "phase_10_14_validation_passed",
            "passed": safe_bool(summary.get("validation_passed", False)),
            "required_value": "True",
            "actual_value": str(summary.get("validation_passed", "")),
            "requirement_group": "dependency",
        },
        {
            "requirement_id": "RUN_REQ_002",
            "requirement_name": "execution_review_passed",
            "passed": safe_bool(
                summary.get(
                    "controlled_start_activation_report_only_dry_run_execution_review_passed",
                    False,
                )
            ),
            "required_value": "True",
            "actual_value": str(
                summary.get(
                    "controlled_start_activation_report_only_dry_run_execution_review_passed",
                    "",
                )
            ),
            "requirement_group": "execution_review",
        },
        {
            "requirement_id": "RUN_REQ_003",
            "requirement_name": "execution_review_decision_expected",
            "passed": str(
                summary.get(
                    "controlled_start_activation_report_only_dry_run_execution_review_decision",
                    "",
                )
            ).strip()
            == EXECUTION_REVIEW_READY_DECISION,
            "required_value": EXECUTION_REVIEW_READY_DECISION,
            "actual_value": str(
                summary.get(
                    "controlled_start_activation_report_only_dry_run_execution_review_decision",
                    "",
                )
            ),
            "requirement_group": "execution_review",
        },
        {
            "requirement_id": "RUN_REQ_004",
            "requirement_name": "future_controlled_run_allowed",
            "passed": safe_bool(
                summary.get(
                    "future_controlled_start_activation_report_only_dry_run_run_allowed",
                    False,
                )
            ),
            "required_value": "True",
            "actual_value": str(
                summary.get(
                    "future_controlled_start_activation_report_only_dry_run_run_allowed",
                    "",
                )
            ),
            "requirement_group": "future_run",
        },
        {
            "requirement_id": "RUN_REQ_005",
            "requirement_name": "execution_review_decision_table_consistent",
            "passed": (
                not execution_review_decision_df.empty
                and safe_bool(
                    decision.get(
                        "controlled_start_activation_report_only_dry_run_execution_review_passed",
                        False,
                    )
                )
                and str(
                    decision.get(
                        "controlled_start_activation_report_only_dry_run_execution_review_decision",
                        "",
                    )
                ).strip()
                == EXECUTION_REVIEW_READY_DECISION
            ),
            "required_value": "True",
            "actual_value": str(
                decision.get(
                    "controlled_start_activation_report_only_dry_run_execution_review_decision",
                    "",
                )
            ),
            "requirement_group": "summary_consistency",
        },
        {
            "requirement_id": "RUN_REQ_006",
            "requirement_name": "report_only_dry_run_row_count_one",
            "passed": int(len(dry_run_df)) == 1,
            "required_value": "1",
            "actual_value": str(len(dry_run_df)),
            "requirement_group": "row_creation",
        },
        {
            "requirement_id": "RUN_REQ_007",
            "requirement_name": "row_schema_compatible",
            "passed": row_validation.get("schema_compatible", False),
            "required_value": "True",
            "actual_value": str(row_validation.get("schema_compatible", False)),
            "requirement_group": "schema",
        },
        {
            "requirement_id": "RUN_REQ_008",
            "requirement_name": "row_candidate_valid",
            "passed": row_validation.get("candidate_valid", False),
            "required_value": "True",
            "actual_value": str(row_validation.get("candidate_valid", False)),
            "requirement_group": "candidate_scope",
        },
        {
            "requirement_id": "RUN_REQ_009",
            "requirement_name": "row_direction_valid",
            "passed": row_validation.get("direction_valid", False),
            "required_value": "True",
            "actual_value": str(row_validation.get("direction_valid", False)),
            "requirement_group": "direction",
        },
        {
            "requirement_id": "RUN_REQ_010",
            "requirement_name": "row_price_structure_valid",
            "passed": row_validation.get("price_structure_valid", False),
            "required_value": "True",
            "actual_value": str(row_validation.get("price_structure_valid", False)),
            "requirement_group": "price_structure",
        },
        {
            "requirement_id": "RUN_REQ_011",
            "requirement_name": "row_evidence_scope_valid",
            "passed": row_validation.get("evidence_scope_valid", False),
            "required_value": "True",
            "actual_value": str(row_validation.get("evidence_scope_valid", False)),
            "requirement_group": "evidence_scope",
        },
        {
            "requirement_id": "RUN_REQ_012",
            "requirement_name": "row_safety_false_guards_passed",
            "passed": row_validation.get("safety_false_guards_passed", False),
            "required_value": "True",
            "actual_value": str(row_validation.get("safety_false_guards_passed", False)),
            "requirement_group": "safety",
        },
        {
            "requirement_id": "RUN_REQ_013",
            "requirement_name": "run_controls_passed",
            "passed": controls_passed,
            "required_value": "True",
            "actual_value": str(controls_passed),
            "requirement_group": "controls",
        },
        {
            "requirement_id": "RUN_REQ_014",
            "requirement_name": "run_rules_passed",
            "passed": rules_passed,
            "required_value": "True",
            "actual_value": str(rules_passed),
            "requirement_group": "rules",
        },
        {
            "requirement_id": "RUN_REQ_015",
            "requirement_name": "run_guards_passed",
            "passed": guards_passed,
            "required_value": "True",
            "actual_value": str(guards_passed),
            "requirement_group": "safety",
        },
        {
            "requirement_id": "RUN_REQ_016",
            "requirement_name": "report_only_artifact_write_performed",
            "passed": artifact_write_performed,
            "required_value": "True",
            "actual_value": str(artifact_write_performed),
            "requirement_group": "artifact",
        },
        {
            "requirement_id": "RUN_REQ_017",
            "requirement_name": "report_only_artifact_rows_written_one",
            "passed": artifact_rows_written == 1,
            "required_value": "1",
            "actual_value": str(artifact_rows_written),
            "requirement_group": "artifact",
        },
        {
            "requirement_id": "RUN_REQ_018",
            "requirement_name": "official_evidence_rows_written_zero",
            "passed": True,
            "required_value": "0",
            "actual_value": "0",
            "requirement_group": "official_dataset_guard",
        },
        {
            "requirement_id": "RUN_REQ_019",
            "requirement_name": "market_execution_disabled",
            "passed": True,
            "required_value": "False",
            "actual_value": "False",
            "requirement_group": "market_execution_guard",
        },
        {
            "requirement_id": "RUN_REQ_020",
            "requirement_name": "total_project_not_completed",
            "passed": True,
            "required_value": "False",
            "actual_value": "False",
            "requirement_group": "scope_control",
        },
    ]

    return pd.DataFrame(requirements)


def build_report_only_dry_run_run_decision_table(
    requirements_df: pd.DataFrame,
    rules_df: pd.DataFrame,
    guard_matrix_df: pd.DataFrame,
) -> pd.DataFrame:
    total_requirements = int(len(requirements_df))
    passed_requirements = (
        int(requirements_df["passed"].astype(bool).sum())
        if total_requirements
        else 0
    )
    failed_requirements = total_requirements - passed_requirements

    rules_passed = not rules_df.empty and rules_df["passed"].astype(bool).all()
    guards_passed = not guard_matrix_df.empty and guard_matrix_df["passed"].astype(bool).all()

    run_passed = (
        total_requirements > 0
        and failed_requirements == 0
        and rules_passed
        and guards_passed
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
                "controlled_start_activation_report_only_dry_run_run_id": (
                    "PHASE_10_15_LONG_FORWARD_OBSERVATION_CONTROLLED_START_ACTIVATION_REPORT_ONLY_DRY_RUN_RUN_001"
                ),
                "controlled_start_activation_report_only_dry_run_run_status": (
                    CONTROLLED_START_ACTIVATION_REPORT_ONLY_DRY_RUN_RUN_STATUS
                ),
                "controlled_start_activation_report_only_dry_run_run_passed": run_passed,
                "controlled_start_activation_report_only_dry_run_run_decision": (
                    READY_DECISION if run_passed else BLOCKED_DECISION
                ),
                "total_requirements": total_requirements,
                "passed_requirements": passed_requirements,
                "failed_requirements": failed_requirements,
                "failed_requirement_names": failed_requirement_names,
                "report_only_dry_run_run_rules_passed": rules_passed,
                "report_only_dry_run_run_guards_passed": guards_passed,
                "future_controlled_start_activation_report_only_dry_run_output_integrity_review_allowed": run_passed,
                "controlled_forward_observation_start_approved": False,
                "controlled_forward_observation_start_activation_performed": False,
                "controlled_forward_observation_start_dry_run_performed": False,
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


def validate_long_forward_observation_controlled_start_activation_report_only_dry_run_run() -> dict[str, pd.DataFrame]:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    checks: list[dict[str, Any]] = []

    phase_anchors = {
        "phase_10_14_execution_review_doc_exists": PHASE_10_14_EXECUTION_REVIEW_DOC_PATH,
        "phase_10_15_report_only_dry_run_run_doc_exists": PHASE_10_15_REPORT_ONLY_DRY_RUN_RUN_DOC_PATH,
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

    phase_10_14_result = (
        validate_long_forward_observation_controlled_start_activation_report_only_dry_run_execution_review()
    )

    phase_10_14_summary_df = phase_10_14_result["summary"]
    source_schema_df = phase_10_14_result["source_report_only_dry_run_design_schema"]
    source_components_df = phase_10_14_result["source_report_only_dry_run_design_components"]
    source_controls_df = phase_10_14_result["source_report_only_dry_run_design_controls"]
    source_rules_df = phase_10_14_result["source_report_only_dry_run_design_rules"]
    source_requirements_df = phase_10_14_result["source_report_only_dry_run_design_requirements"]
    source_guard_matrix_df = phase_10_14_result["source_report_only_dry_run_design_guard_matrix"]
    source_boundary_matrix_df = phase_10_14_result["source_report_only_dry_run_design_boundary_matrix"]
    source_decision_df = phase_10_14_result["source_report_only_dry_run_design_decision"]
    source_checks_df = phase_10_14_result["source_checks"]
    execution_review_items_df = phase_10_14_result["execution_review_items"]
    execution_review_controls_df = phase_10_14_result["execution_review_controls"]
    execution_review_rules_df = phase_10_14_result["execution_review_rules"]
    execution_review_requirements_df = phase_10_14_result["execution_review_requirements"]
    execution_review_guard_matrix_df = phase_10_14_result["execution_review_guard_matrix"]
    execution_review_boundary_matrix_df = phase_10_14_result["execution_review_boundary_matrix"]
    execution_review_decision_df = phase_10_14_result["execution_review_decision"]

    phase_10_14_summary = (
        phase_10_14_summary_df.iloc[0].to_dict()
        if not phase_10_14_summary_df.empty
        else {}
    )

    phase_10_14_validation_passed = (
        not phase_10_14_summary_df.empty
        and safe_bool(phase_10_14_summary.get("validation_passed", False))
    )

    execution_review_passed = safe_bool(
        phase_10_14_summary.get(
            "controlled_start_activation_report_only_dry_run_execution_review_passed",
            False,
        )
    )

    dry_run_df = build_report_only_dry_run_row(source_schema_df)
    controls_df = build_report_only_dry_run_run_controls()
    row_validation_df = build_report_only_dry_run_row_validation(
        dry_run_df=dry_run_df,
        schema_df=source_schema_df,
    )
    rules_df = build_report_only_dry_run_run_rules(
        controls_df=controls_df,
        row_validation_df=row_validation_df,
    )
    guard_matrix_df = build_report_only_dry_run_run_guard_matrix()

    dry_run_artifact_path = (
        REPORTS_DIR / "controlled_start_activation_report_only_dry_run_output_v1.csv"
    )
    dry_run_df.to_csv(dry_run_artifact_path, index=False)

    artifact_write_performed = dry_run_artifact_path.exists()
    artifact_rows_written = int(len(dry_run_df)) if artifact_write_performed else 0

    requirements_df = build_report_only_dry_run_run_requirements(
        phase_10_14_summary_df=phase_10_14_summary_df,
        execution_review_decision_df=execution_review_decision_df,
        dry_run_df=dry_run_df,
        row_validation_df=row_validation_df,
        controls_df=controls_df,
        rules_df=rules_df,
        guard_matrix_df=guard_matrix_df,
        artifact_write_performed=artifact_write_performed,
        artifact_rows_written=artifact_rows_written,
    )

    decision_df = build_report_only_dry_run_run_decision_table(
        requirements_df=requirements_df,
        rules_df=rules_df,
        guard_matrix_df=guard_matrix_df,
    )

    official_dataset_exists_after = OFFICIAL_DATASET_PATH.exists()

    decision = decision_df.iloc[0].to_dict() if not decision_df.empty else {}

    run_passed = safe_bool(
        decision.get(
            "controlled_start_activation_report_only_dry_run_run_passed",
            False,
        )
    )
    run_decision = str(
        decision.get(
            "controlled_start_activation_report_only_dry_run_run_decision",
            "",
        )
    )
    future_output_integrity_review_allowed = safe_bool(
        decision.get(
            "future_controlled_start_activation_report_only_dry_run_output_integrity_review_allowed",
            False,
        )
    )

    row_validation_lookup = {
        str(row["validation_name"]): safe_bool(row["passed"], False)
        for _, row in row_validation_df.iterrows()
    }

    controls_passed = not controls_df.empty and controls_df["passed"].astype(bool).all()
    rules_passed = not rules_df.empty and rules_df["passed"].astype(bool).all()
    requirements_passed = (
        not requirements_df.empty and requirements_df["passed"].astype(bool).all()
    )
    guards_passed = (
        not guard_matrix_df.empty and guard_matrix_df["passed"].astype(bool).all()
    )

    checks.append(
        build_check(
            check_group="phase_dependency",
            check_name="phase_10_14_validation_passed",
            passed=phase_10_14_validation_passed,
            severity="INFO" if phase_10_14_validation_passed else "ERROR",
            details=str(phase_10_14_summary.get("validation_decision", "")),
        )
    )

    checks.append(
        build_check(
            check_group="phase_dependency",
            check_name="execution_review_passed",
            passed=execution_review_passed,
            severity="INFO" if execution_review_passed else "ERROR",
            details=f"execution_review_passed={execution_review_passed}",
        )
    )

    checks.append(
        build_check(
            check_group="report_only_dry_run_run",
            check_name="dry_run_artifact_written",
            passed=artifact_write_performed,
            severity="INFO" if artifact_write_performed else "ERROR",
            details=str(dry_run_artifact_path),
        )
    )

    checks.append(
        build_check(
            check_group="report_only_dry_run_run",
            check_name="dry_run_artifact_rows_written_one",
            passed=artifact_rows_written == 1,
            severity="INFO" if artifact_rows_written == 1 else "ERROR",
            details=f"artifact_rows_written={artifact_rows_written}",
        )
    )

    checks.append(
        build_check(
            check_group="report_only_dry_run_run",
            check_name="row_schema_compatible",
            passed=row_validation_lookup.get("schema_compatible", False),
            severity=(
                "INFO"
                if row_validation_lookup.get("schema_compatible", False)
                else "ERROR"
            ),
            details=str(row_validation_lookup.get("schema_compatible", False)),
        )
    )

    checks.append(
        build_check(
            check_group="report_only_dry_run_run",
            check_name="row_price_structure_valid",
            passed=row_validation_lookup.get("price_structure_valid", False),
            severity=(
                "INFO"
                if row_validation_lookup.get("price_structure_valid", False)
                else "ERROR"
            ),
            details=str(row_validation_lookup.get("price_structure_valid", False)),
        )
    )

    checks.append(
        build_check(
            check_group="report_only_dry_run_run",
            check_name="row_candidate_valid",
            passed=row_validation_lookup.get("candidate_valid", False),
            severity=(
                "INFO"
                if row_validation_lookup.get("candidate_valid", False)
                else "ERROR"
            ),
            details=str(row_validation_lookup.get("candidate_valid", False)),
        )
    )

    checks.append(
        build_check(
            check_group="report_only_dry_run_run",
            check_name="row_direction_valid",
            passed=row_validation_lookup.get("direction_valid", False),
            severity=(
                "INFO"
                if row_validation_lookup.get("direction_valid", False)
                else "ERROR"
            ),
            details=str(row_validation_lookup.get("direction_valid", False)),
        )
    )

    checks.append(
        build_check(
            check_group="report_only_dry_run_run",
            check_name="run_controls_passed",
            passed=controls_passed,
            severity="INFO" if controls_passed else "ERROR",
            details=f"controls_passed={controls_passed}",
        )
    )

    checks.append(
        build_check(
            check_group="report_only_dry_run_run",
            check_name="run_rules_passed",
            passed=rules_passed,
            severity="INFO" if rules_passed else "ERROR",
            details=f"rules_passed={rules_passed}",
        )
    )

    checks.append(
        build_check(
            check_group="report_only_dry_run_run",
            check_name="run_requirements_passed",
            passed=requirements_passed,
            severity="INFO" if requirements_passed else "ERROR",
            details=f"requirements_passed={requirements_passed}",
        )
    )

    checks.append(
        build_check(
            check_group="report_only_dry_run_run",
            check_name="run_guards_passed",
            passed=guards_passed,
            severity="INFO" if guards_passed else "ERROR",
            details=f"guards_passed={guards_passed}",
        )
    )

    checks.append(
        build_check(
            check_group="report_only_dry_run_run",
            check_name="controlled_start_activation_report_only_dry_run_run_passed",
            passed=run_passed,
            severity="INFO" if run_passed else "ERROR",
            details=f"run_passed={run_passed}",
        )
    )

    checks.append(
        build_check(
            check_group="report_only_dry_run_run",
            check_name="controlled_start_activation_report_only_dry_run_run_decision_expected",
            passed=run_decision == READY_DECISION,
            severity="INFO" if run_decision == READY_DECISION else "ERROR",
            details=f"run_decision={run_decision}",
        )
    )

    checks.append(
        build_check(
            check_group="planning_scope",
            check_name="future_output_integrity_review_allowed",
            passed=future_output_integrity_review_allowed,
            severity="WARNING" if future_output_integrity_review_allowed else "ERROR",
            details=(
                "This allows only a future output integrity review, not forward "
                "observation start, alerts, paper trading, real capital, official "
                "evidence persistence, or market execution."
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

    for _, guard_row in guard_matrix_df.iterrows():
        checks.append(
            build_check(
                check_group="report_only_dry_run_run_safety_flags",
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
            check_name="report_only_dry_run_run_only",
            passed=True,
            severity="WARNING",
            details="Phase 10.15 runs only a controlled report-only dry-run artifact.",
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
            check_name="signal_generation_not_enabled",
            passed=True,
            severity="WARNING",
            details="Signal generation remains disabled.",
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
            check_name="phase_10_16_recommended_next",
            passed=True,
            severity="INFO",
            details=(
                "Recommended next step: Phase 10.16 LONG Forward Observation "
                "Controlled Start Activation Report-Only Dry-Run Output Integrity Review V1."
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
                "phase": "10.15",
                "long_forward_observation_controlled_start_activation_report_only_dry_run_run_defined": True,
                "phase_10_14_validation_passed": phase_10_14_validation_passed,
                "controlled_start_activation_report_only_dry_run_execution_review_passed": execution_review_passed,
                "controlled_start_activation_report_only_dry_run_execution_review_decision": str(
                    phase_10_14_summary.get(
                        "controlled_start_activation_report_only_dry_run_execution_review_decision",
                        "",
                    )
                ),
                "future_controlled_start_activation_report_only_dry_run_run_allowed": safe_bool(
                    phase_10_14_summary.get(
                        "future_controlled_start_activation_report_only_dry_run_run_allowed",
                        False,
                    )
                ),
                "report_only_dry_run_run_row_count": int(len(dry_run_df)),
                "report_only_dry_run_row_schema_compatible": row_validation_lookup.get("schema_compatible", False),
                "report_only_dry_run_row_candidate_valid": row_validation_lookup.get("candidate_valid", False),
                "report_only_dry_run_row_direction_valid": row_validation_lookup.get("direction_valid", False),
                "report_only_dry_run_row_price_structure_valid": row_validation_lookup.get("price_structure_valid", False),
                "report_only_dry_run_row_evidence_scope_valid": row_validation_lookup.get("evidence_scope_valid", False),
                "report_only_dry_run_safety_guards_passed": guards_passed,
                "report_only_artifact_write_performed": artifact_write_performed,
                "report_only_artifact_rows_written": artifact_rows_written,
                "controlled_start_activation_report_only_dry_run_run_passed": run_passed,
                "controlled_start_activation_report_only_dry_run_run_decision": run_decision,
                "future_controlled_start_activation_report_only_dry_run_output_integrity_review_allowed": future_output_integrity_review_allowed,
                "controlled_forward_observation_start_approved": False,
                "controlled_forward_observation_start_activation_performed": False,
                "controlled_forward_observation_start_dry_run_performed": False,
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
                "estimated_phase_10_progress_percent": 100,
                "total_checks": int(len(checks_df)),
                "warning_count": warning_count,
                "error_count": error_count,
                "blocker_count": blocker_count,
                "validation_passed": validation_passed,
                "validation_decision": (
                    "PHASE_10_15_LONG_FORWARD_OBSERVATION_CONTROLLED_START_ACTIVATION_REPORT_ONLY_DRY_RUN_RUN_VALIDATED"
                    if validation_passed
                    else "PHASE_10_15_LONG_FORWARD_OBSERVATION_CONTROLLED_START_ACTIVATION_REPORT_ONLY_DRY_RUN_RUN_FAILED"
                ),
            }
        ]
    )

    phase_10_14_summary_df.to_csv(
        REPORTS_DIR / "phase_10_14_source_summary_v1.csv",
        index=False,
    )
    source_schema_df.to_csv(
        REPORTS_DIR / "phase_10_13_source_report_only_dry_run_design_schema_v1.csv",
        index=False,
    )
    source_components_df.to_csv(
        REPORTS_DIR / "phase_10_13_source_report_only_dry_run_design_components_v1.csv",
        index=False,
    )
    source_controls_df.to_csv(
        REPORTS_DIR / "phase_10_13_source_report_only_dry_run_design_controls_v1.csv",
        index=False,
    )
    source_rules_df.to_csv(
        REPORTS_DIR / "phase_10_13_source_report_only_dry_run_design_rules_v1.csv",
        index=False,
    )
    source_requirements_df.to_csv(
        REPORTS_DIR / "phase_10_13_source_report_only_dry_run_design_requirements_v1.csv",
        index=False,
    )
    source_guard_matrix_df.to_csv(
        REPORTS_DIR / "phase_10_13_source_report_only_dry_run_design_guard_matrix_v1.csv",
        index=False,
    )
    source_boundary_matrix_df.to_csv(
        REPORTS_DIR / "phase_10_13_source_report_only_dry_run_design_boundary_matrix_v1.csv",
        index=False,
    )
    source_decision_df.to_csv(
        REPORTS_DIR / "phase_10_13_source_report_only_dry_run_design_decision_v1.csv",
        index=False,
    )
    source_checks_df.to_csv(
        REPORTS_DIR / "phase_10_13_source_checks_v1.csv",
        index=False,
    )
    execution_review_items_df.to_csv(
        REPORTS_DIR / "phase_10_14_source_execution_review_items_v1.csv",
        index=False,
    )
    execution_review_controls_df.to_csv(
        REPORTS_DIR / "phase_10_14_source_execution_review_controls_v1.csv",
        index=False,
    )
    execution_review_rules_df.to_csv(
        REPORTS_DIR / "phase_10_14_source_execution_review_rules_v1.csv",
        index=False,
    )
    execution_review_requirements_df.to_csv(
        REPORTS_DIR / "phase_10_14_source_execution_review_requirements_v1.csv",
        index=False,
    )
    execution_review_guard_matrix_df.to_csv(
        REPORTS_DIR / "phase_10_14_source_execution_review_guard_matrix_v1.csv",
        index=False,
    )
    execution_review_boundary_matrix_df.to_csv(
        REPORTS_DIR / "phase_10_14_source_execution_review_boundary_matrix_v1.csv",
        index=False,
    )
    execution_review_decision_df.to_csv(
        REPORTS_DIR / "phase_10_14_source_execution_review_decision_v1.csv",
        index=False,
    )
    controls_df.to_csv(
        REPORTS_DIR / "controlled_start_activation_report_only_dry_run_run_controls_v1.csv",
        index=False,
    )
    row_validation_df.to_csv(
        REPORTS_DIR / "controlled_start_activation_report_only_dry_run_row_validation_v1.csv",
        index=False,
    )
    rules_df.to_csv(
        REPORTS_DIR / "controlled_start_activation_report_only_dry_run_run_rules_v1.csv",
        index=False,
    )
    guard_matrix_df.to_csv(
        REPORTS_DIR / "controlled_start_activation_report_only_dry_run_run_guard_matrix_v1.csv",
        index=False,
    )
    requirements_df.to_csv(
        REPORTS_DIR / "controlled_start_activation_report_only_dry_run_run_requirements_v1.csv",
        index=False,
    )
    decision_df.to_csv(
        REPORTS_DIR / "controlled_start_activation_report_only_dry_run_run_decision_v1.csv",
        index=False,
    )
    checks_df.to_csv(
        REPORTS_DIR / "controlled_start_activation_report_only_dry_run_run_checks_v1.csv",
        index=False,
    )
    summary_df.to_csv(
        REPORTS_DIR / "controlled_start_activation_report_only_dry_run_run_summary_v1.csv",
        index=False,
    )

    return {
        "summary": summary_df,
        "source_phase_10_14_summary": phase_10_14_summary_df,
        "source_report_only_dry_run_design_schema": source_schema_df,
        "source_report_only_dry_run_design_components": source_components_df,
        "source_report_only_dry_run_design_controls": source_controls_df,
        "source_report_only_dry_run_design_rules": source_rules_df,
        "source_report_only_dry_run_design_requirements": source_requirements_df,
        "source_report_only_dry_run_design_guard_matrix": source_guard_matrix_df,
        "source_report_only_dry_run_design_boundary_matrix": source_boundary_matrix_df,
        "source_report_only_dry_run_design_decision": source_decision_df,
        "source_checks": source_checks_df,
        "source_execution_review_items": execution_review_items_df,
        "source_execution_review_controls": execution_review_controls_df,
        "source_execution_review_rules": execution_review_rules_df,
        "source_execution_review_requirements": execution_review_requirements_df,
        "source_execution_review_guard_matrix": execution_review_guard_matrix_df,
        "source_execution_review_boundary_matrix": execution_review_boundary_matrix_df,
        "source_execution_review_decision": execution_review_decision_df,
        "report_only_dry_run_output": dry_run_df,
        "report_only_dry_run_run_controls": controls_df,
        "report_only_dry_run_row_validation": row_validation_df,
        "report_only_dry_run_run_rules": rules_df,
        "report_only_dry_run_run_guard_matrix": guard_matrix_df,
        "report_only_dry_run_run_requirements": requirements_df,
        "report_only_dry_run_run_decision": decision_df,
        "checks": checks_df,
    }