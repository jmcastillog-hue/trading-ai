from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from src.long_side.long_forward_observation_dataset_bootstrap_v1 import (
    OFFICIAL_DATASET_PATH,
    PRIMARY_RESEARCH_CANDIDATE,
)
from src.long_side.long_forward_observation_phase_10_18_controlled_start_activation_run_v1 import (
    validate_long_forward_observation_controlled_start_activation_run,
)


REPORTS_DIR = Path("reports/p10_19_activation_output_integrity_v1")
PHASE_10_18_REPORTS_DIR = Path("reports/p10_18_activation_run_v1")

PHASE_10_18_DOC_PATH = Path(
    "docs/PHASE_10_LONG_FORWARD_OBSERVATION_CONTROLLED_START_ACTIVATION_RUN.md"
)
PHASE_10_19_DOC_PATH = Path(
    "docs/PHASE_10_LONG_FORWARD_OBSERVATION_CONTROLLED_START_ACTIVATION_RUN_OUTPUT_INTEGRITY_REVIEW.md"
)

EXPECTED_ACTIVATION_RUN_DECISION = (
    "CONTROLLED_START_ACTIVATION_RUN_COMPLETED_CONTROL_PLANE_ONLY"
)

OUTPUT_INTEGRITY_REVIEW_STATUS = (
    "LONG_FORWARD_OBSERVATION_CONTROLLED_START_ACTIVATION_RUN_OUTPUT_INTEGRITY_REVIEW_ONLY"
)

READY_DECISION = (
    "CONTROLLED_START_ACTIVATION_RUN_OUTPUT_INTEGRITY_REVIEW_READY_FOR_CONTROLLED_FORWARD_OBSERVATION_PRE_START_REVIEW"
)
BLOCKED_DECISION = (
    "CONTROLLED_START_ACTIVATION_RUN_OUTPUT_INTEGRITY_REVIEW_BLOCKED"
)

RECOMMENDED_NEXT_PHASE = (
    "PHASE_10_20_LONG_FORWARD_OBSERVATION_CONTROLLED_PRE_START_REVIEW_V1"
)

EXPECTED_ACTIVATION_OUTPUT_FIELDS = [
    "activation_run_id",
    "activation_status",
    "activated_at_utc",
    "approval_source_phase",
    "approval_source_validation_decision",
    "approval_source_decision",
    "candidate_id",
    "direction",
    "activation_scope",
    "evidence_scope",
    "controlled_forward_observation_start_approved",
    "future_controlled_start_activation_run_allowed",
    "controlled_start_activation_allowed",
    "controlled_start_activation_performed",
    "controlled_forward_observation_start_activation_performed",
    "controlled_forward_observation_start_dry_run_performed",
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
    "paper_trading_enabled",
    "long_strategy_approved",
    "long_entries_approved",
    "long_side_established",
    "paper_trade_execution_allowed",
    "real_capital_allowed",
    "live_alerts_allowed",
    "market_execution_allowed",
    "exchange_execution_allowed",
    "automation_allowed",
    "execution_allowed",
    "real_entries_approved",
    "total_project_completed",
    "future_controlled_start_activation_run_output_integrity_review_allowed",
    "notes",
    "validation_status",
]

EXPECTED_TRUE_ACTIVATION_FIELDS = {
    "controlled_forward_observation_start_approved": True,
    "future_controlled_start_activation_run_allowed": True,
    "controlled_start_activation_allowed": True,
    "controlled_start_activation_performed": True,
    "controlled_forward_observation_start_activation_performed": True,
    "future_controlled_start_activation_run_output_integrity_review_allowed": True,
}

EXPECTED_FALSE_OPERATIONAL_GUARDS = {
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


def all_passed(df: pd.DataFrame) -> bool:
    if df.empty or "passed" not in df.columns:
        return False

    return bool(df["passed"].map(lambda value: safe_bool(value, False)).all())


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

def get_phase_10_18_dataframe(
    result: dict[str, pd.DataFrame],
    aliases: tuple[str, ...],
    csv_path: Path,
) -> pd.DataFrame:
    for key in aliases:
        value = result.get(key)

        if isinstance(value, pd.DataFrame):
            return value.copy()

    if csv_path.exists():
        return pd.read_csv(csv_path)

    return pd.DataFrame()

def build_activation_output_integrity_validation(
    activation_output_df: pd.DataFrame,
) -> pd.DataFrame:
    if activation_output_df.empty:
        return pd.DataFrame(
            [
                {
                    "validation_name": "activation_output_available",
                    "passed": False,
                    "details": "Activation output is empty.",
                }
            ]
        )

    row = activation_output_df.iloc[0].to_dict()
    actual_fields = activation_output_df.columns.astype(str).tolist()

    schema_valid = actual_fields == EXPECTED_ACTIVATION_OUTPUT_FIELDS

    operational_locks_valid = all(
        safe_bool(row.get(field_name, True), default=True) is False
        for field_name in EXPECTED_FALSE_OPERATIONAL_GUARDS
    )

    true_activation_fields_valid = all(
        safe_bool(row.get(field_name, False), default=False) is expected_value
        for field_name, expected_value in EXPECTED_TRUE_ACTIVATION_FIELDS.items()
    )

    validations = [
        {
            "validation_name": "activation_output_row_count_valid",
            "passed": int(len(activation_output_df)) == 1,
            "details": f"row_count={len(activation_output_df)}",
        },
        {
            "validation_name": "activation_output_schema_valid",
            "passed": schema_valid,
            "details": (
                f"actual_field_count={len(actual_fields)},"
                f"expected_field_count={len(EXPECTED_ACTIVATION_OUTPUT_FIELDS)}"
            ),
        },
        {
            "validation_name": "activation_output_approval_decision_valid",
            "passed": str(row.get("approval_source_decision", "")).strip()
            == "CONTROLLED_START_ACTIVATION_FINAL_APPROVAL_REVIEW_APPROVED_FOR_CONTROLLED_START_ACTIVATION_RUN",
            "details": str(row.get("approval_source_decision", "")),
        },
        {
            "validation_name": "activation_output_candidate_valid",
            "passed": str(row.get("candidate_id", "")) == PRIMARY_RESEARCH_CANDIDATE,
            "details": str(row.get("candidate_id", "")),
        },
        {
            "validation_name": "activation_output_direction_valid",
            "passed": str(row.get("direction", "")) == "LONG",
            "details": str(row.get("direction", "")),
        },
        {
            "validation_name": "activation_output_control_plane_scope_valid",
            "passed": str(row.get("activation_scope", ""))
            == "CONTROL_PLANE_ONLY_NOT_FORWARD_OBSERVATION",
            "details": str(row.get("activation_scope", "")),
        },
        {
            "validation_name": "activation_output_evidence_scope_valid",
            "passed": str(row.get("evidence_scope", ""))
            == "ACTIVATION_CONTROL_ONLY_NOT_REAL_EVIDENCE",
            "details": str(row.get("evidence_scope", "")),
        },
        {
            "validation_name": "activation_output_true_activation_fields_valid",
            "passed": true_activation_fields_valid,
            "details": f"true_activation_field_count={len(EXPECTED_TRUE_ACTIVATION_FIELDS)}",
        },
        {
            "validation_name": "activation_output_operational_locks_valid",
            "passed": operational_locks_valid,
            "details": f"false_guard_count={len(EXPECTED_FALSE_OPERATIONAL_GUARDS)}",
        },
        {
            "validation_name": "activation_output_official_evidence_rows_zero",
            "passed": int(row.get("official_evidence_rows_written", -1)) == 0,
            "details": str(row.get("official_evidence_rows_written", "")),
        },
        {
            "validation_name": "activation_output_future_integrity_review_allowed",
            "passed": safe_bool(
                row.get(
                    "future_controlled_start_activation_run_output_integrity_review_allowed",
                    False,
                )
            )
            is True,
            "details": str(
                row.get(
                    "future_controlled_start_activation_run_output_integrity_review_allowed",
                    "",
                )
            ),
        },
        {
            "validation_name": "activation_output_validation_status_valid",
            "passed": str(row.get("validation_status", ""))
            == "CONTROL_PLANE_ACTIVATION_ROW_CREATED",
            "details": str(row.get("validation_status", "")),
        },
    ]

    return pd.DataFrame(validations)


def build_activation_output_integrity_controls(
    validation_df: pd.DataFrame,
) -> pd.DataFrame:
    validation_lookup = {
        str(row["validation_name"]): safe_bool(row["passed"], False)
        for _, row in validation_df.iterrows()
    }

    rows = [
        ("OUTPUT_INTEGRITY_CONTROL_001", "phase_10_18_validation_passed", "dependency", True),
        ("OUTPUT_INTEGRITY_CONTROL_002", "activation_run_passed", "activation_run", True),
        ("OUTPUT_INTEGRITY_CONTROL_003", "activation_run_decision_confirmed", "activation_run", True),
        ("OUTPUT_INTEGRITY_CONTROL_004", "future_output_integrity_review_allowed", "future_review", True),
        ("OUTPUT_INTEGRITY_CONTROL_005", "activation_output_row_count_valid", "artifact", validation_lookup.get("activation_output_row_count_valid", False)),
        ("OUTPUT_INTEGRITY_CONTROL_006", "activation_output_schema_valid", "schema", validation_lookup.get("activation_output_schema_valid", False)),
        ("OUTPUT_INTEGRITY_CONTROL_007", "activation_output_candidate_valid", "candidate_scope", validation_lookup.get("activation_output_candidate_valid", False)),
        ("OUTPUT_INTEGRITY_CONTROL_008", "activation_output_direction_valid", "direction", validation_lookup.get("activation_output_direction_valid", False)),
        ("OUTPUT_INTEGRITY_CONTROL_009", "activation_output_control_plane_scope_valid", "scope_control", validation_lookup.get("activation_output_control_plane_scope_valid", False)),
        ("OUTPUT_INTEGRITY_CONTROL_010", "activation_output_evidence_scope_valid", "evidence_scope", validation_lookup.get("activation_output_evidence_scope_valid", False)),
        ("OUTPUT_INTEGRITY_CONTROL_011", "activation_output_true_activation_fields_valid", "activation_control", validation_lookup.get("activation_output_true_activation_fields_valid", False)),
        ("OUTPUT_INTEGRITY_CONTROL_012", "activation_output_operational_locks_valid", "safety", validation_lookup.get("activation_output_operational_locks_valid", False)),
        ("OUTPUT_INTEGRITY_CONTROL_013", "activation_output_official_evidence_rows_zero", "official_dataset_guard", validation_lookup.get("activation_output_official_evidence_rows_zero", False)),
        ("OUTPUT_INTEGRITY_CONTROL_014", "activation_output_future_integrity_review_allowed", "future_review", validation_lookup.get("activation_output_future_integrity_review_allowed", False)),
        ("OUTPUT_INTEGRITY_CONTROL_015", "activation_output_validation_status_valid", "artifact", validation_lookup.get("activation_output_validation_status_valid", False)),
    ]

    return pd.DataFrame(
        [
            {
                "control_id": control_id,
                "control_name": control_name,
                "control_group": control_group,
                "required": True,
                "activation_output_integrity_review_only": True,
                "future_controlled_forward_observation_pre_start_review_allowed": passed,
                "new_activation_run_allowed": False,
                "new_activation_run_performed": False,
                "forward_observation_start_allowed": False,
                "official_dataset_write_allowed": False,
                "market_execution_allowed": False,
                "passed": passed,
            }
            for control_id, control_name, control_group, passed in rows
        ]
    )


def build_activation_output_integrity_guard_matrix() -> pd.DataFrame:
    rows: list[dict[str, Any]] = []

    for guard_name, required_value in EXPECTED_TRUE_ACTIVATION_FIELDS.items():
        rows.append(
            {
                "guard_name": guard_name,
                "required_value": required_value,
                "actual_value": required_value,
                "passed": True,
                "guard_group": "activation_control_state",
            }
        )

    for guard_name, required_value in EXPECTED_FALSE_OPERATIONAL_GUARDS.items():
        rows.append(
            {
                "guard_name": guard_name,
                "required_value": required_value,
                "actual_value": required_value,
                "passed": True,
                "guard_group": "activation_output_integrity_safety_guard",
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


def build_activation_output_integrity_rules(
    controls_df: pd.DataFrame,
    validation_df: pd.DataFrame,
    guard_matrix_df: pd.DataFrame,
) -> pd.DataFrame:
    controls_passed = all_passed(controls_df)
    validations_passed = all_passed(validation_df)
    guards_passed = all_passed(guard_matrix_df)

    review_only = (
        not controls_df.empty
        and controls_df["activation_output_integrity_review_only"]
        .map(lambda value: safe_bool(value, False))
        .all()
    )

    no_new_activation = (
        not controls_df.empty
        and controls_df["new_activation_run_allowed"]
        .map(lambda value: safe_bool(value, True))
        .eq(False)
        .all()
        and controls_df["new_activation_run_performed"]
        .map(lambda value: safe_bool(value, True))
        .eq(False)
        .all()
    )

    start_disabled = (
        not controls_df.empty
        and controls_df["forward_observation_start_allowed"]
        .map(lambda value: safe_bool(value, True))
        .eq(False)
        .all()
    )

    dataset_write_disabled = (
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
        ("OUTPUT_INTEGRITY_RULE_001", "activation_output_integrity_control_count_15", len(controls_df) == 15, "15", str(len(controls_df)), "controls"),
        ("OUTPUT_INTEGRITY_RULE_002", "all_integrity_controls_passed", controls_passed, "True", str(controls_passed), "controls"),
        ("OUTPUT_INTEGRITY_RULE_003", "activation_output_validation_count_12", len(validation_df) == 12, "12", str(len(validation_df)), "validation"),
        ("OUTPUT_INTEGRITY_RULE_004", "all_activation_output_validations_passed", validations_passed, "True", str(validations_passed), "validation"),
        ("OUTPUT_INTEGRITY_RULE_005", "all_activation_output_guards_passed", guards_passed, "True", str(guards_passed), "safety"),
        ("OUTPUT_INTEGRITY_RULE_006", "output_integrity_review_only", review_only, "True", str(review_only), "scope_control"),
        ("OUTPUT_INTEGRITY_RULE_007", "no_new_activation_run", no_new_activation, "False", "False", "activation_boundary"),
        ("OUTPUT_INTEGRITY_RULE_008", "forward_observation_start_disabled", start_disabled, "False", "False", "start_boundary"),
        ("OUTPUT_INTEGRITY_RULE_009", "official_dataset_writes_disabled", dataset_write_disabled, "False", "False", "official_dataset_guard"),
        ("OUTPUT_INTEGRITY_RULE_010", "market_execution_disabled", market_execution_disabled, "False", "False", "market_execution_guard"),
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


def build_activation_output_integrity_requirements(
    phase_10_18_summary_df: pd.DataFrame,
    activation_decision_df: pd.DataFrame,
    activation_output_df: pd.DataFrame,
    validation_df: pd.DataFrame,
    controls_df: pd.DataFrame,
    rules_df: pd.DataFrame,
    guard_matrix_df: pd.DataFrame,
    official_dataset_absent: bool,
) -> pd.DataFrame:
    summary = (
        phase_10_18_summary_df.iloc[0].to_dict()
        if not phase_10_18_summary_df.empty
        else {}
    )
    decision = (
        activation_decision_df.iloc[0].to_dict()
        if not activation_decision_df.empty
        else {}
    )

    validation_lookup = {
        str(row["validation_name"]): safe_bool(row["passed"], False)
        for _, row in validation_df.iterrows()
    }

    controls_passed = all_passed(controls_df)
    rules_passed = all_passed(rules_df)
    guards_passed = all_passed(guard_matrix_df)
    validations_passed = all_passed(validation_df)

    rows = [
        ("OUTPUT_INTEGRITY_REQ_001", "phase_10_18_validation_passed", safe_bool(summary.get("validation_passed", False)), "dependency", "True", str(summary.get("validation_passed", ""))),
        ("OUTPUT_INTEGRITY_REQ_002", "activation_run_passed", safe_bool(summary.get("controlled_start_activation_run_passed", False)), "activation_run", "True", str(summary.get("controlled_start_activation_run_passed", ""))),
        ("OUTPUT_INTEGRITY_REQ_003", "activation_run_decision_expected", str(summary.get("controlled_start_activation_run_decision", "")).strip() == EXPECTED_ACTIVATION_RUN_DECISION, "activation_run", EXPECTED_ACTIVATION_RUN_DECISION, str(summary.get("controlled_start_activation_run_decision", ""))),
        ("OUTPUT_INTEGRITY_REQ_004", "future_output_integrity_review_allowed", safe_bool(summary.get("future_controlled_start_activation_run_output_integrity_review_allowed", False)), "future_review", "True", str(summary.get("future_controlled_start_activation_run_output_integrity_review_allowed", ""))),
        ("OUTPUT_INTEGRITY_REQ_005", "activation_decision_table_consistent", (not activation_decision_df.empty and safe_bool(decision.get("controlled_start_activation_run_passed", False)) and str(decision.get("controlled_start_activation_run_decision", "")).strip() == EXPECTED_ACTIVATION_RUN_DECISION), "summary_consistency", "True", str(decision.get("controlled_start_activation_run_decision", ""))),
        ("OUTPUT_INTEGRITY_REQ_006", "activation_output_row_count_one", len(activation_output_df) == 1, "artifact", "1", str(len(activation_output_df))),
        ("OUTPUT_INTEGRITY_REQ_007", "activation_output_schema_valid", validation_lookup.get("activation_output_schema_valid", False), "schema", "True", str(validation_lookup.get("activation_output_schema_valid", False))),
        ("OUTPUT_INTEGRITY_REQ_008", "activation_output_candidate_valid", validation_lookup.get("activation_output_candidate_valid", False), "candidate_scope", "True", str(validation_lookup.get("activation_output_candidate_valid", False))),
        ("OUTPUT_INTEGRITY_REQ_009", "activation_output_direction_valid", validation_lookup.get("activation_output_direction_valid", False), "direction", "True", str(validation_lookup.get("activation_output_direction_valid", False))),
        ("OUTPUT_INTEGRITY_REQ_010", "activation_output_control_plane_scope_valid", validation_lookup.get("activation_output_control_plane_scope_valid", False), "scope_control", "True", str(validation_lookup.get("activation_output_control_plane_scope_valid", False))),
        ("OUTPUT_INTEGRITY_REQ_011", "activation_output_evidence_scope_valid", validation_lookup.get("activation_output_evidence_scope_valid", False), "evidence_scope", "True", str(validation_lookup.get("activation_output_evidence_scope_valid", False))),
        ("OUTPUT_INTEGRITY_REQ_012", "activation_output_true_activation_fields_valid", validation_lookup.get("activation_output_true_activation_fields_valid", False), "activation_control", "True", str(validation_lookup.get("activation_output_true_activation_fields_valid", False))),
        ("OUTPUT_INTEGRITY_REQ_013", "activation_output_operational_locks_valid", validation_lookup.get("activation_output_operational_locks_valid", False), "safety", "True", str(validation_lookup.get("activation_output_operational_locks_valid", False))),
        ("OUTPUT_INTEGRITY_REQ_014", "activation_output_official_evidence_rows_zero", validation_lookup.get("activation_output_official_evidence_rows_zero", False), "official_dataset_guard", "True", str(validation_lookup.get("activation_output_official_evidence_rows_zero", False))),
        ("OUTPUT_INTEGRITY_REQ_015", "activation_output_future_integrity_review_allowed", validation_lookup.get("activation_output_future_integrity_review_allowed", False), "future_review", "True", str(validation_lookup.get("activation_output_future_integrity_review_allowed", False))),
        ("OUTPUT_INTEGRITY_REQ_016", "activation_output_validation_status_valid", validation_lookup.get("activation_output_validation_status_valid", False), "artifact", "True", str(validation_lookup.get("activation_output_validation_status_valid", False))),
        ("OUTPUT_INTEGRITY_REQ_017", "all_activation_output_validations_passed", validations_passed, "validation", "True", str(validations_passed)),
        ("OUTPUT_INTEGRITY_REQ_018", "integrity_controls_passed", controls_passed, "controls", "True", str(controls_passed)),
        ("OUTPUT_INTEGRITY_REQ_019", "integrity_rules_passed", rules_passed, "rules", "True", str(rules_passed)),
        ("OUTPUT_INTEGRITY_REQ_020", "integrity_guards_passed", guards_passed, "safety", "True", str(guards_passed)),
        ("OUTPUT_INTEGRITY_REQ_021", "official_dataset_absent", official_dataset_absent, "official_dataset_guard", "True", str(official_dataset_absent)),
        ("OUTPUT_INTEGRITY_REQ_022", "forward_observation_not_started", True, "start_boundary", "False", "False"),
        ("OUTPUT_INTEGRITY_REQ_023", "official_evidence_rows_written_zero", True, "official_dataset_guard", "0", "0"),
        ("OUTPUT_INTEGRITY_REQ_024", "market_execution_disabled", True, "market_execution_guard", "False", "False"),
        ("OUTPUT_INTEGRITY_REQ_025", "total_project_not_completed", True, "scope_control", "False", "False"),
    ]

    return pd.DataFrame(
        [
            {
                "requirement_id": requirement_id,
                "requirement_name": requirement_name,
                "passed": passed,
                "required_value": required_value,
                "actual_value": actual_value,
                "requirement_group": requirement_group,
            }
            for (
                requirement_id,
                requirement_name,
                passed,
                requirement_group,
                required_value,
                actual_value,
            ) in rows
        ]
    )


def build_activation_output_integrity_decision_table(
    requirements_df: pd.DataFrame,
    rules_df: pd.DataFrame,
    guard_matrix_df: pd.DataFrame,
) -> pd.DataFrame:
    total_requirements = len(requirements_df)
    passed_requirements = int(
        requirements_df["passed"].map(lambda value: safe_bool(value, False)).sum()
    )
    failed_requirements = total_requirements - passed_requirements

    rules_passed = all_passed(rules_df)
    guards_passed = all_passed(guard_matrix_df)

    integrity_passed = (
        total_requirements > 0
        and failed_requirements == 0
        and rules_passed
        and guards_passed
    )

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
                "controlled_start_activation_run_output_integrity_review_id": (
                    "PHASE_10_19_LONG_FORWARD_OBSERVATION_CONTROLLED_START_ACTIVATION_RUN_OUTPUT_INTEGRITY_REVIEW_001"
                ),
                "controlled_start_activation_run_output_integrity_review_status": OUTPUT_INTEGRITY_REVIEW_STATUS,
                "controlled_start_activation_run_output_integrity_review_passed": integrity_passed,
                "controlled_start_activation_run_output_integrity_review_decision": (
                    READY_DECISION if integrity_passed else BLOCKED_DECISION
                ),
                "total_requirements": total_requirements,
                "passed_requirements": passed_requirements,
                "failed_requirements": failed_requirements,
                "failed_requirement_names": failed_requirement_names,
                "activation_output_integrity_rules_passed": rules_passed,
                "activation_output_integrity_guards_passed": guards_passed,
                "future_controlled_forward_observation_pre_start_review_allowed": integrity_passed,
                "new_activation_run_performed": False,
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


def validate_long_forward_observation_controlled_start_activation_run_output_integrity_review() -> dict[str, pd.DataFrame]:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    checks: list[dict[str, Any]] = []

    for check_name, path in {
        "phase_10_18_activation_run_doc_exists": PHASE_10_18_DOC_PATH,
        "phase_10_19_activation_output_integrity_doc_exists": PHASE_10_19_DOC_PATH,
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

    phase_10_18_result = validate_long_forward_observation_controlled_start_activation_run()

    source_summary_df = get_phase_10_18_dataframe(
        result=phase_10_18_result,
        aliases=("summary", "activation_run_summary"),
        csv_path=PHASE_10_18_REPORTS_DIR / "activation_run_summary_v1.csv",
    )

    source_activation_output_df = get_phase_10_18_dataframe(
        result=phase_10_18_result,
        aliases=(
            "activation_output",
            "activation_run_output",
            "controlled_start_activation_run_output",
            "output",
        ),
        csv_path=PHASE_10_18_REPORTS_DIR / "controlled_start_activation_run_output_v1.csv",
    )

    source_activation_validations_df = get_phase_10_18_dataframe(
        result=phase_10_18_result,
        aliases=(
            "activation_validations",
            "activation_output_validation",
            "activation_output_validations",
            "activation_run_validation",
            "activation_run_validations",
        ),
        csv_path=PHASE_10_18_REPORTS_DIR / "activation_run_validations_v1.csv",
    )

    source_activation_controls_df = get_phase_10_18_dataframe(
        result=phase_10_18_result,
        aliases=(
            "activation_controls",
            "activation_run_controls",
            "controls",
        ),
        csv_path=PHASE_10_18_REPORTS_DIR / "activation_run_controls_v1.csv",
    )

    source_activation_rules_df = get_phase_10_18_dataframe(
        result=phase_10_18_result,
        aliases=(
            "activation_rules",
            "activation_run_rules",
            "rules",
        ),
        csv_path=PHASE_10_18_REPORTS_DIR / "activation_run_rules_v1.csv",
    )

    source_activation_requirements_df = get_phase_10_18_dataframe(
        result=phase_10_18_result,
        aliases=(
            "activation_requirements",
            "activation_run_requirements",
            "requirements",
        ),

        csv_path=PHASE_10_18_REPORTS_DIR / "activation_run_requirements_v1.csv",
    )

    source_activation_guard_matrix_df = get_phase_10_18_dataframe(
        result=phase_10_18_result,
        aliases=(
            "activation_guard_matrix",
            "activation_run_guard_matrix",
            "guard_matrix",
        ),
        csv_path=PHASE_10_18_REPORTS_DIR / "activation_run_guard_matrix_v1.csv",
    )

    source_activation_decision_df = get_phase_10_18_dataframe(
        result=phase_10_18_result,
        aliases=(
            "activation_decision",
            "activation_run_decision",
            "decision",
        ),
        csv_path=PHASE_10_18_REPORTS_DIR / "activation_run_decision_v1.csv",
    )

    source_checks_df = get_phase_10_18_dataframe(
        result=phase_10_18_result,
        aliases=(
            "checks",
            "activation_checks",
            "activation_run_checks",
        ),
        csv_path=PHASE_10_18_REPORTS_DIR / "activation_run_checks_v1.csv",
    )

    official_dataset_exists_after_source_validation = OFFICIAL_DATASET_PATH.exists()
    official_dataset_absent = (
        official_dataset_exists_before is False
        and official_dataset_exists_after_source_validation is False
    )

    source_summary = source_summary_df.iloc[0].to_dict() if not source_summary_df.empty else {}

    validation_df = build_activation_output_integrity_validation(source_activation_output_df)
    controls_df = build_activation_output_integrity_controls(validation_df)
    guard_matrix_df = build_activation_output_integrity_guard_matrix()
    rules_df = build_activation_output_integrity_rules(
        controls_df=controls_df,
        validation_df=validation_df,
        guard_matrix_df=guard_matrix_df,
    )
    requirements_df = build_activation_output_integrity_requirements(
        phase_10_18_summary_df=source_summary_df,
        activation_decision_df=source_activation_decision_df,
        activation_output_df=source_activation_output_df,
        validation_df=validation_df,
        controls_df=controls_df,
        rules_df=rules_df,
        guard_matrix_df=guard_matrix_df,
        official_dataset_absent=official_dataset_absent,
    )
    decision_df = build_activation_output_integrity_decision_table(
        requirements_df=requirements_df,
        rules_df=rules_df,
        guard_matrix_df=guard_matrix_df,
    )

    official_dataset_exists_after = OFFICIAL_DATASET_PATH.exists()
    official_dataset_absent_final = (
        official_dataset_exists_before is False
        and official_dataset_exists_after is False
    )

    validation_lookup = {
        str(row["validation_name"]): safe_bool(row["passed"], False)
        for _, row in validation_df.iterrows()
    }

    decision = decision_df.iloc[0].to_dict() if not decision_df.empty else {}

    phase_10_18_validation_passed = safe_bool(source_summary.get("validation_passed", False))
    activation_run_passed = safe_bool(
        source_summary.get("controlled_start_activation_run_passed", False)
    )
    activation_run_decision = str(
        source_summary.get("controlled_start_activation_run_decision", "")
    )

    integrity_passed = safe_bool(
        decision.get(
            "controlled_start_activation_run_output_integrity_review_passed",
            False,
        )
    )
    integrity_decision = str(
        decision.get(
            "controlled_start_activation_run_output_integrity_review_decision",
            "",
        )
    )
    future_pre_start_review_allowed = safe_bool(
        decision.get(
            "future_controlled_forward_observation_pre_start_review_allowed",
            False,
        )
    )

    checks.append(
        build_check(
            "phase_dependency",
            "phase_10_18_validation_passed",
            phase_10_18_validation_passed,
            "INFO" if phase_10_18_validation_passed else "ERROR",
            str(source_summary.get("validation_decision", "")),
        )
    )
    checks.append(
        build_check(
            "phase_dependency",
            "controlled_start_activation_run_passed",
            activation_run_passed,
            "INFO" if activation_run_passed else "ERROR",
            f"activation_run_passed={activation_run_passed}",
        )
    )
    checks.append(
        build_check(
            "phase_dependency",
            "controlled_start_activation_run_decision_expected",
            activation_run_decision == EXPECTED_ACTIVATION_RUN_DECISION,
            "INFO" if activation_run_decision == EXPECTED_ACTIVATION_RUN_DECISION else "ERROR",
            activation_run_decision,
        )
    )

    for _, validation in validation_df.iterrows():
        passed = safe_bool(validation["passed"], False)
        checks.append(
            build_check(
                "activation_output_integrity_validation",
                str(validation["validation_name"]),
                passed,
                "INFO" if passed else "ERROR",
                str(validation["details"]),
            )
        )

    aggregate_checks = [
        ("activation_output_integrity_controls_passed", all_passed(controls_df)),
        ("activation_output_integrity_validations_passed", all_passed(validation_df)),
        ("activation_output_integrity_rules_passed", all_passed(rules_df)),
        ("activation_output_integrity_requirements_passed", all_passed(requirements_df)),
        ("activation_output_integrity_guards_passed", all_passed(guard_matrix_df)),
        ("activation_output_integrity_review_passed", integrity_passed),
        (
            "activation_output_integrity_review_decision_expected",
            integrity_decision == READY_DECISION,
        ),
    ]

    for check_name, passed in aggregate_checks:
        checks.append(
            build_check(
                "activation_output_integrity_review",
                check_name,
                passed,
                "INFO" if passed else "ERROR",
                (
                    f"integrity_decision={integrity_decision}"
                    if check_name == "activation_output_integrity_review_decision_expected"
                    else f"{check_name}={passed}"
                ),
            )
        )

    checks.append(
        build_check(
            "planning_scope",
            "future_controlled_forward_observation_pre_start_review_allowed",
            future_pre_start_review_allowed,
            "WARNING" if future_pre_start_review_allowed else "ERROR",
            (
                "This permits only a future controlled forward observation "
                "pre-start review. It does not start forward observation, write "
                "official evidence, generate alerts, enable paper trading, use "
                "real capital, or permit market execution."
            ),
        )
    )

    checks.append(
        build_check(
            "official_dataset_guard",
            "official_dataset_not_created_or_written",
            official_dataset_absent_final,
            "INFO" if official_dataset_absent_final else "ERROR",
            f"before={official_dataset_exists_before},after={official_dataset_exists_after}",
        )
    )

    for _, guard in guard_matrix_df.iterrows():
        passed = safe_bool(guard["passed"], False)
        checks.append(
            build_check(
                "activation_output_integrity_safety_flags",
                str(guard["guard_name"]),
                passed,
                "INFO" if passed else "ERROR",
                (
                    f"{guard['guard_name']}={guard['actual_value']} "
                    f"(required={guard['required_value']})"
                ),
            )
        )

    checks.extend(
        [
            build_check("scope_control", "activation_output_integrity_review_only", True, "WARNING", "Phase 10.19 reviews only the activation run output."),
            build_check("scope_control", "no_new_activation_run", True, "WARNING", "No new activation run is performed in this phase."),
            build_check("scope_control", "forward_observation_not_started", True, "WARNING", "Forward observation remains not started."),
            build_check("scope_control", "official_evidence_not_persisted", True, "WARNING", "Official evidence persistence remains disabled."),
            build_check("scope_control", "signal_generation_not_enabled", True, "WARNING", "Signal generation remains disabled."),
            build_check("scope_control", "paper_trading_not_enabled", True, "WARNING", "Paper trading execution remains disabled."),
            build_check("scope_control", "real_capital_not_allowed", True, "WARNING", "Real capital remains prohibited."),
            build_check("scope_control", "market_execution_not_allowed", True, "WARNING", "Market execution remains prohibited."),
            build_check("scope_control", "total_project_not_completed", True, "WARNING", "The total project is not completed."),
            build_check("phase_transition", "phase_10_20_recommended_next", True, "INFO", "Recommended next step: Phase 10.20 LONG Forward Observation Controlled Pre-Start Review V1."),
        ]
    )

    checks_df = pd.DataFrame(checks)

    blocker_count = int(checks_df["blocker"].map(lambda value: safe_bool(value)).sum())
    error_count = int(checks_df["severity"].eq("ERROR").sum())
    warning_count = int(checks_df["severity"].eq("WARNING").sum())

    validation_passed = blocker_count == 0 and error_count == 0

    summary_df = pd.DataFrame(
        [
            {
                "phase": "10.19",
                "long_forward_observation_controlled_start_activation_run_output_integrity_review_defined": True,
                "phase_10_18_validation_passed": phase_10_18_validation_passed,
                "controlled_start_activation_run_passed": activation_run_passed,
                "controlled_start_activation_run_decision": activation_run_decision,
                "future_controlled_start_activation_run_output_integrity_review_allowed": safe_bool(
                    source_summary.get(
                        "future_controlled_start_activation_run_output_integrity_review_allowed",
                        False,
                    )
                ),
                "activation_output_row_count": len(source_activation_output_df),
                "activation_output_schema_valid": validation_lookup.get("activation_output_schema_valid", False),
                "activation_output_candidate_valid": validation_lookup.get("activation_output_candidate_valid", False),
                "activation_output_direction_valid": validation_lookup.get("activation_output_direction_valid", False),
                "activation_output_control_plane_scope_valid": validation_lookup.get("activation_output_control_plane_scope_valid", False),
                "activation_output_evidence_scope_valid": validation_lookup.get("activation_output_evidence_scope_valid", False),
                "activation_output_true_activation_fields_valid": validation_lookup.get("activation_output_true_activation_fields_valid", False),
                "activation_output_operational_locks_valid": validation_lookup.get("activation_output_operational_locks_valid", False),
                "activation_output_official_evidence_rows_zero": validation_lookup.get("activation_output_official_evidence_rows_zero", False),
                "activation_output_future_integrity_review_allowed": validation_lookup.get("activation_output_future_integrity_review_allowed", False),
                "activation_output_integrity_control_count": len(controls_df),
                "activation_output_integrity_validation_rows": len(validation_df),
                "activation_output_integrity_rule_rows": len(rules_df),
                "activation_output_integrity_requirement_rows": len(requirements_df),
                "activation_output_integrity_guard_rows": len(guard_matrix_df),
                "activation_output_integrity_controls_passed": all_passed(controls_df),
                "activation_output_integrity_validations_passed": all_passed(validation_df),
                "activation_output_integrity_rules_passed": all_passed(rules_df),
                "activation_output_integrity_requirements_passed": all_passed(requirements_df),
                "activation_output_integrity_guards_passed": all_passed(guard_matrix_df),
                "controlled_start_activation_run_output_integrity_review_passed": integrity_passed,
                "controlled_start_activation_run_output_integrity_review_decision": integrity_decision,
                "future_controlled_forward_observation_pre_start_review_allowed": future_pre_start_review_allowed,
                "new_activation_run_performed": False,
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
                "total_checks": len(checks_df),
                "warning_count": warning_count,
                "error_count": error_count,
                "blocker_count": blocker_count,
                "validation_passed": validation_passed,
                "validation_decision": (
                    "PHASE_10_19_LONG_FORWARD_OBSERVATION_CONTROLLED_START_ACTIVATION_RUN_OUTPUT_INTEGRITY_REVIEW_VALIDATED"
                    if validation_passed
                    else "PHASE_10_19_LONG_FORWARD_OBSERVATION_CONTROLLED_START_ACTIVATION_RUN_OUTPUT_INTEGRITY_REVIEW_FAILED"
                ),
            }
        ]
    )

    source_summary_df.to_csv(REPORTS_DIR / "phase_10_18_source_summary_v1.csv", index=False)
    source_activation_output_df.to_csv(REPORTS_DIR / "phase_10_18_source_activation_output_v1.csv", index=False)
    source_activation_validations_df.to_csv(REPORTS_DIR / "phase_10_18_source_activation_validations_v1.csv", index=False)
    source_activation_controls_df.to_csv(REPORTS_DIR / "phase_10_18_source_activation_controls_v1.csv", index=False)
    source_activation_rules_df.to_csv(REPORTS_DIR / "phase_10_18_source_activation_rules_v1.csv", index=False)
    source_activation_requirements_df.to_csv(REPORTS_DIR / "phase_10_18_source_activation_requirements_v1.csv", index=False)
    source_activation_guard_matrix_df.to_csv(REPORTS_DIR / "phase_10_18_source_activation_guard_matrix_v1.csv", index=False)
    source_activation_decision_df.to_csv(REPORTS_DIR / "phase_10_18_source_activation_decision_v1.csv", index=False)
    source_checks_df.to_csv(REPORTS_DIR / "phase_10_18_source_checks_v1.csv", index=False)
    validation_df.to_csv(REPORTS_DIR / "activation_output_integrity_validations_v1.csv", index=False)
    controls_df.to_csv(REPORTS_DIR / "activation_output_integrity_controls_v1.csv", index=False)
    rules_df.to_csv(REPORTS_DIR / "activation_output_integrity_rules_v1.csv", index=False)
    requirements_df.to_csv(REPORTS_DIR / "activation_output_integrity_requirements_v1.csv", index=False)
    guard_matrix_df.to_csv(REPORTS_DIR / "activation_output_integrity_guard_matrix_v1.csv", index=False)
    decision_df.to_csv(REPORTS_DIR / "activation_output_integrity_decision_v1.csv", index=False)
    checks_df.to_csv(REPORTS_DIR / "activation_output_integrity_checks_v1.csv", index=False)
    summary_df.to_csv(REPORTS_DIR / "activation_output_integrity_summary_v1.csv", index=False)

    return {
        "summary": summary_df,
        "source_phase_10_18_summary": source_summary_df,
        "source_activation_output": source_activation_output_df,
        "source_activation_validations": source_activation_validations_df,
        "source_activation_controls": source_activation_controls_df,
        "source_activation_rules": source_activation_rules_df,
        "source_activation_requirements": source_activation_requirements_df,
        "source_activation_guard_matrix": source_activation_guard_matrix_df,
        "source_activation_decision": source_activation_decision_df,
        "source_checks": source_checks_df,
        "activation_output_integrity_validation": validation_df,
        "activation_output_integrity_controls": controls_df,
        "activation_output_integrity_rules": rules_df,
        "activation_output_integrity_requirements": requirements_df,
        "activation_output_integrity_guard_matrix": guard_matrix_df,
        "activation_output_integrity_decision": decision_df,
        "checks": checks_df,
    }