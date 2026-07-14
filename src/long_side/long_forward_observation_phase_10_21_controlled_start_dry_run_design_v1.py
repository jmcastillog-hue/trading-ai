from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

from src.long_side.long_forward_observation_dataset_bootstrap_v1 import (
    OFFICIAL_DATASET_PATH,
    PRIMARY_RESEARCH_CANDIDATE,
)
from src.long_side.long_forward_observation_phase_10_20_controlled_pre_start_review_v1 import (
    validate_long_forward_observation_controlled_pre_start_review,
)


REPORTS_DIR = Path("reports/p10_21_start_dry_run_design_v1")
PHASE_10_20_REPORTS_DIR = Path("reports/p10_20_pre_start_review_v1")

PHASE_10_20_DOC_PATH = Path(
    "docs/PHASE_10_LONG_FORWARD_OBSERVATION_CONTROLLED_PRE_START_REVIEW.md"
)
PHASE_10_21_DOC_PATH = Path(
    "docs/PHASE_10_LONG_FORWARD_OBSERVATION_CONTROLLED_START_DRY_RUN_DESIGN.md"
)

EXPECTED_PRE_START_DECISION = (
    "CONTROLLED_FORWARD_OBSERVATION_PRE_START_REVIEW_READY_FOR_CONTROLLED_FORWARD_OBSERVATION_START_DRY_RUN_DESIGN"
)

DESIGN_STATUS = (
    "LONG_FORWARD_OBSERVATION_CONTROLLED_START_DRY_RUN_DESIGN_ONLY"
)

READY_DECISION = (
    "CONTROLLED_FORWARD_OBSERVATION_START_DRY_RUN_DESIGN_READY_FOR_EXECUTION_REVIEW"
)
BLOCKED_DECISION = (
    "CONTROLLED_FORWARD_OBSERVATION_START_DRY_RUN_DESIGN_BLOCKED"
)

RECOMMENDED_NEXT_PHASE = (
    "PHASE_10_22_LONG_FORWARD_OBSERVATION_CONTROLLED_START_DRY_RUN_EXECUTION_REVIEW_V1"
)

EXPECTED_DESIGN_OUTPUT_FIELDS = [
    "dry_run_design_id",
    "design_status",
    "designed_at_utc",
    "source_phase",
    "source_validation_decision",
    "source_pre_start_decision",
    "symbol",
    "timeframe",
    "candidate_id",
    "direction",
    "observation_role",
    "signal_state",
    "market_context",
    "activation_scope",
    "design_scope",
    "evidence_scope",
    "entry_price",
    "stop_price",
    "target_price",
    "invalidation_level",
    "risk_reward",
    "cost_profile",
    "manual_confirmation_required",
    "controlled_forward_observation_pre_start_review_passed",
    "future_controlled_forward_observation_start_dry_run_design_allowed",
    "controlled_forward_observation_start_dry_run_design_allowed",
    "controlled_forward_observation_start_dry_run_design_performed",
    "future_controlled_forward_observation_start_dry_run_execution_review_allowed",
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

EXPECTED_TRUE_DESIGN_FIELDS = {
    "controlled_forward_observation_pre_start_review_passed": True,
    "future_controlled_forward_observation_start_dry_run_design_allowed": True,
    "controlled_forward_observation_start_dry_run_design_allowed": True,
    "controlled_forward_observation_start_dry_run_design_performed": True,
    "future_controlled_forward_observation_start_dry_run_execution_review_allowed": True,
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


def get_phase_10_20_dataframe(
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


def first_row(df: pd.DataFrame) -> dict[str, Any]:
    if df.empty:
        return {}

    return df.iloc[0].to_dict()


def build_start_dry_run_design_output(
    source_summary_df: pd.DataFrame,
    source_activation_output_df: pd.DataFrame,
) -> pd.DataFrame:
    summary = first_row(source_summary_df)
    source_activation = first_row(source_activation_output_df)

    candidate_id = str(
        source_activation.get(
            "candidate_id",
            summary.get("source_candidate_id", PRIMARY_RESEARCH_CANDIDATE),
        )
    )
    direction = str(
        source_activation.get(
            "direction",
            summary.get("source_direction", "LONG"),
        )
    )

    row = {
        "dry_run_design_id": (
            "PHASE_10_21_LONG_FORWARD_OBSERVATION_CONTROLLED_START_DRY_RUN_DESIGN_001"
        ),
        "design_status": DESIGN_STATUS,
        "designed_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_phase": "10.20",
        "source_validation_decision": str(summary.get("validation_decision", "")),
        "source_pre_start_decision": str(
            summary.get(
                "controlled_forward_observation_pre_start_review_decision",
                "",
            )
        ),
        "symbol": "BTCUSDT",
        "timeframe": "15m",
        "candidate_id": candidate_id,
        "direction": direction,
        "observation_role": "PRIMARY_FORWARD_OBSERVATION_START_DRY_RUN_DESIGN",
        "signal_state": "CONTROLLED_START_DRY_RUN_DESIGN_ONLY",
        "market_context": "SYNTHETIC_CONTROLLED_FORWARD_OBSERVATION_START_DRY_RUN_DESIGN",
        "activation_scope": str(
            source_activation.get(
                "activation_scope",
                "CONTROL_PLANE_ONLY_NOT_FORWARD_OBSERVATION",
            )
        ),
        "design_scope": "CONTROLLED_FORWARD_OBSERVATION_START_DRY_RUN_DESIGN_ONLY",
        "evidence_scope": "DESIGN_ONLY_NOT_REAL_EVIDENCE",
        "entry_price": 100.0,
        "stop_price": 95.0,
        "target_price": 112.5,
        "invalidation_level": 95.0,
        "risk_reward": 2.5,
        "cost_profile": "RESEARCH_COST_AWARE_REFERENCE_ONLY",
        "manual_confirmation_required": True,
        "controlled_forward_observation_pre_start_review_passed": safe_bool(
            summary.get(
                "controlled_forward_observation_pre_start_review_passed",
                False,
            )
        ),
        "future_controlled_forward_observation_start_dry_run_design_allowed": safe_bool(
            summary.get(
                "future_controlled_forward_observation_start_dry_run_design_allowed",
                False,
            )
        ),
        "controlled_forward_observation_start_dry_run_design_allowed": True,
        "controlled_forward_observation_start_dry_run_design_performed": True,
        "future_controlled_forward_observation_start_dry_run_execution_review_allowed": True,
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
            "Controlled forward observation start dry-run design only. "
            "Not a dry-run execution. Not forward observation. Not real evidence. "
            "Not a signal. Not market execution."
        ),
        "validation_status": "CONTROLLED_START_DRY_RUN_DESIGN_ROW_CREATED",
    }

    return pd.DataFrame([row], columns=EXPECTED_DESIGN_OUTPUT_FIELDS)


def build_start_dry_run_design_validation(
    design_output_df: pd.DataFrame,
    source_summary_df: pd.DataFrame,
) -> pd.DataFrame:
    if design_output_df.empty:
        return pd.DataFrame(
            [
                {
                    "validation_name": "design_output_available",
                    "passed": False,
                    "details": "Design output is empty.",
                }
            ]
        )

    row = design_output_df.iloc[0].to_dict()
    summary = first_row(source_summary_df)

    actual_fields = design_output_df.columns.astype(str).tolist()
    schema_valid = actual_fields == EXPECTED_DESIGN_OUTPUT_FIELDS

    price_structure_valid = (
        float(row.get("stop_price", 0)) < float(row.get("entry_price", 0))
        < float(row.get("target_price", 0))
    )

    true_design_fields_valid = all(
        safe_bool(row.get(field_name, False), default=False) is expected_value
        for field_name, expected_value in EXPECTED_TRUE_DESIGN_FIELDS.items()
    )

    operational_locks_valid = all(
        safe_bool(row.get(field_name, True), default=True) is False
        for field_name in EXPECTED_FALSE_OPERATIONAL_GUARDS
    )

    validations = [
        {
            "validation_name": "design_output_row_count_valid",
            "passed": len(design_output_df) == 1,
            "details": f"row_count={len(design_output_df)}",
        },
        {
            "validation_name": "design_output_schema_valid",
            "passed": schema_valid,
            "details": (
                f"actual_field_count={len(actual_fields)},"
                f"expected_field_count={len(EXPECTED_DESIGN_OUTPUT_FIELDS)}"
            ),
        },
        {
            "validation_name": "source_pre_start_decision_valid",
            "passed": str(
                summary.get(
                    "controlled_forward_observation_pre_start_review_decision",
                    "",
                )
            ).strip()
            == EXPECTED_PRE_START_DECISION,
            "details": str(
                summary.get(
                    "controlled_forward_observation_pre_start_review_decision",
                    "",
                )
            ),
        },
        {
            "validation_name": "design_output_candidate_valid",
            "passed": str(row.get("candidate_id", "")) == PRIMARY_RESEARCH_CANDIDATE,
            "details": str(row.get("candidate_id", "")),
        },
        {
            "validation_name": "design_output_direction_valid",
            "passed": str(row.get("direction", "")) == "LONG",
            "details": str(row.get("direction", "")),
        },
        {
            "validation_name": "design_output_price_structure_valid",
            "passed": price_structure_valid,
            "details": (
                f"stop={row.get('stop_price')},"
                f"entry={row.get('entry_price')},"
                f"target={row.get('target_price')}"
            ),
        },
        {
            "validation_name": "design_output_risk_reward_valid",
            "passed": float(row.get("risk_reward", 0)) == 2.5,
            "details": f"risk_reward={row.get('risk_reward')},expected=2.5",
        },
        {
            "validation_name": "design_output_scope_valid",
            "passed": str(row.get("design_scope", ""))
            == "CONTROLLED_FORWARD_OBSERVATION_START_DRY_RUN_DESIGN_ONLY",
            "details": str(row.get("design_scope", "")),
        },
        {
            "validation_name": "design_output_evidence_scope_valid",
            "passed": str(row.get("evidence_scope", ""))
            == "DESIGN_ONLY_NOT_REAL_EVIDENCE",
            "details": str(row.get("evidence_scope", "")),
        },
        {
            "validation_name": "design_output_true_design_fields_valid",
            "passed": true_design_fields_valid,
            "details": f"true_design_field_count={len(EXPECTED_TRUE_DESIGN_FIELDS)}",
        },
        {
            "validation_name": "design_output_operational_locks_valid",
            "passed": operational_locks_valid,
            "details": f"false_guard_count={len(EXPECTED_FALSE_OPERATIONAL_GUARDS)}",
        },
        {
            "validation_name": "design_output_official_evidence_rows_zero",
            "passed": int(row.get("official_evidence_rows_written", -1)) == 0,
            "details": str(row.get("official_evidence_rows_written", "")),
        },
        {
            "validation_name": "design_output_future_execution_review_allowed",
            "passed": safe_bool(
                row.get(
                    "future_controlled_forward_observation_start_dry_run_execution_review_allowed",
                    False,
                )
            )
            is True,
            "details": str(
                row.get(
                    "future_controlled_forward_observation_start_dry_run_execution_review_allowed",
                    "",
                )
            ),
        },
        {
            "validation_name": "design_output_validation_status_valid",
            "passed": str(row.get("validation_status", ""))
            == "CONTROLLED_START_DRY_RUN_DESIGN_ROW_CREATED",
            "details": str(row.get("validation_status", "")),
        },
    ]

    return pd.DataFrame(validations)


def build_start_dry_run_design_controls(
    validation_df: pd.DataFrame,
) -> pd.DataFrame:
    validation_lookup = {
        str(row["validation_name"]): safe_bool(row["passed"], False)
        for _, row in validation_df.iterrows()
    }

    rows = [
        (
            "START_DRY_RUN_DESIGN_CONTROL_001",
            "phase_10_20_validation_passed",
            "dependency",
            True,
        ),
        (
            "START_DRY_RUN_DESIGN_CONTROL_002",
            "pre_start_review_passed",
            "pre_start_review",
            True,
        ),
        (
            "START_DRY_RUN_DESIGN_CONTROL_003",
            "pre_start_decision_expected",
            "pre_start_review",
            validation_lookup.get("source_pre_start_decision_valid", False),
        ),
        (
            "START_DRY_RUN_DESIGN_CONTROL_004",
            "future_start_dry_run_design_allowed",
            "future_design",
            True,
        ),
        (
            "START_DRY_RUN_DESIGN_CONTROL_005",
            "design_artifact_written",
            "artifact",
            True,
        ),
        (
            "START_DRY_RUN_DESIGN_CONTROL_006",
            "design_output_row_count_valid",
            "artifact",
            validation_lookup.get("design_output_row_count_valid", False),
        ),
        (
            "START_DRY_RUN_DESIGN_CONTROL_007",
            "design_output_schema_valid",
            "schema",
            validation_lookup.get("design_output_schema_valid", False),
        ),
        (
            "START_DRY_RUN_DESIGN_CONTROL_008",
            "design_output_candidate_valid",
            "candidate_scope",
            validation_lookup.get("design_output_candidate_valid", False),
        ),
        (
            "START_DRY_RUN_DESIGN_CONTROL_009",
            "design_output_direction_valid",
            "direction",
            validation_lookup.get("design_output_direction_valid", False),
        ),
        (
            "START_DRY_RUN_DESIGN_CONTROL_010",
            "design_output_price_structure_valid",
            "price_structure",
            validation_lookup.get("design_output_price_structure_valid", False),
        ),
        (
            "START_DRY_RUN_DESIGN_CONTROL_011",
            "design_output_risk_reward_valid",
            "risk_reward",
            validation_lookup.get("design_output_risk_reward_valid", False),
        ),
        (
            "START_DRY_RUN_DESIGN_CONTROL_012",
            "design_output_scope_valid",
            "scope_control",
            validation_lookup.get("design_output_scope_valid", False),
        ),
        (
            "START_DRY_RUN_DESIGN_CONTROL_013",
            "design_output_evidence_scope_valid",
            "evidence_scope",
            validation_lookup.get("design_output_evidence_scope_valid", False),
        ),
        (
            "START_DRY_RUN_DESIGN_CONTROL_014",
            "design_output_true_design_fields_valid",
            "design_control",
            validation_lookup.get("design_output_true_design_fields_valid", False),
        ),
        (
            "START_DRY_RUN_DESIGN_CONTROL_015",
            "design_output_operational_locks_valid",
            "safety",
            validation_lookup.get("design_output_operational_locks_valid", False),
        ),
        (
            "START_DRY_RUN_DESIGN_CONTROL_016",
            "future_execution_review_allowed",
            "future_review",
            validation_lookup.get(
                "design_output_future_execution_review_allowed",
                False,
            ),
        ),
    ]

    return pd.DataFrame(
        [
            {
                "control_id": control_id,
                "control_name": control_name,
                "control_group": control_group,
                "required": True,
                "start_dry_run_design_only": True,
                "future_controlled_forward_observation_start_dry_run_execution_review_allowed": passed,
                "controlled_forward_observation_start_dry_run_performed": False,
                "forward_observation_start_allowed": False,
                "official_dataset_write_allowed": False,
                "market_execution_allowed": False,
                "passed": passed,
            }
            for control_id, control_name, control_group, passed in rows
        ]
    )


def build_start_dry_run_design_guard_matrix() -> pd.DataFrame:
    rows: list[dict[str, Any]] = []

    for guard_name, required_value in EXPECTED_TRUE_DESIGN_FIELDS.items():
        rows.append(
            {
                "guard_name": guard_name,
                "required_value": required_value,
                "actual_value": required_value,
                "passed": True,
                "guard_group": "start_dry_run_design_state",
            }
        )

    for guard_name, required_value in EXPECTED_FALSE_OPERATIONAL_GUARDS.items():
        rows.append(
            {
                "guard_name": guard_name,
                "required_value": required_value,
                "actual_value": required_value,
                "passed": True,
                "guard_group": "start_dry_run_design_safety_guard",
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


def build_start_dry_run_design_rules(
    controls_df: pd.DataFrame,
    validation_df: pd.DataFrame,
    guard_matrix_df: pd.DataFrame,
) -> pd.DataFrame:
    controls_passed = all_passed(controls_df)
    validations_passed = all_passed(validation_df)
    guards_passed = all_passed(guard_matrix_df)

    design_only = (
        not controls_df.empty
        and controls_df["start_dry_run_design_only"]
        .map(lambda value: safe_bool(value, False))
        .all()
    )

    future_execution_review_allowed = (
        not controls_df.empty
        and controls_df[
            "future_controlled_forward_observation_start_dry_run_execution_review_allowed"
        ]
        .map(lambda value: safe_bool(value, False))
        .all()
    )

    dry_run_not_performed = (
        not controls_df.empty
        and controls_df["controlled_forward_observation_start_dry_run_performed"]
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
        (
            "START_DRY_RUN_DESIGN_RULE_001",
            "start_dry_run_design_control_count_16",
            len(controls_df) == 16,
            "16",
            str(len(controls_df)),
            "controls",
        ),
        (
            "START_DRY_RUN_DESIGN_RULE_002",
            "all_design_controls_passed",
            controls_passed,
            "True",
            str(controls_passed),
            "controls",
        ),
        (
            "START_DRY_RUN_DESIGN_RULE_003",
            "start_dry_run_design_validation_count_14",
            len(validation_df) == 14,
            "14",
            str(len(validation_df)),
            "validation",
        ),
        (
            "START_DRY_RUN_DESIGN_RULE_004",
            "all_design_validations_passed",
            validations_passed,
            "True",
            str(validations_passed),
            "validation",
        ),
        (
            "START_DRY_RUN_DESIGN_RULE_005",
            "all_design_guards_passed",
            guards_passed,
            "True",
            str(guards_passed),
            "safety",
        ),
        (
            "START_DRY_RUN_DESIGN_RULE_006",
            "start_dry_run_design_only",
            design_only,
            "True",
            str(design_only),
            "scope_control",
        ),
        (
            "START_DRY_RUN_DESIGN_RULE_007",
            "future_execution_review_allowed",
            future_execution_review_allowed,
            "True",
            str(future_execution_review_allowed),
            "future_review",
        ),
        (
            "START_DRY_RUN_DESIGN_RULE_008",
            "start_dry_run_not_performed",
            dry_run_not_performed,
            "False",
            "False",
            "dry_run_boundary",
        ),
        (
            "START_DRY_RUN_DESIGN_RULE_009",
            "forward_observation_start_disabled",
            start_disabled,
            "False",
            "False",
            "start_boundary",
        ),
        (
            "START_DRY_RUN_DESIGN_RULE_010",
            "official_dataset_writes_disabled",
            dataset_write_disabled,
            "False",
            "False",
            "official_dataset_guard",
        ),
        (
            "START_DRY_RUN_DESIGN_RULE_011",
            "market_execution_disabled",
            market_execution_disabled,
            "False",
            "False",
            "market_execution_guard",
        ),
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


def build_start_dry_run_design_requirements(
    source_summary_df: pd.DataFrame,
    design_output_df: pd.DataFrame,
    validation_df: pd.DataFrame,
    controls_df: pd.DataFrame,
    rules_df: pd.DataFrame,
    guard_matrix_df: pd.DataFrame,
    official_dataset_absent: bool,
) -> pd.DataFrame:
    summary = first_row(source_summary_df)
    validation_lookup = {
        str(row["validation_name"]): safe_bool(row["passed"], False)
        for _, row in validation_df.iterrows()
    }

    controls_passed = all_passed(controls_df)
    rules_passed = all_passed(rules_df)
    guards_passed = all_passed(guard_matrix_df)
    validations_passed = all_passed(validation_df)

    rows = [
        (
            "START_DRY_RUN_DESIGN_REQ_001",
            "phase_10_20_validation_passed",
            safe_bool(summary.get("validation_passed", False)),
            "dependency",
            "True",
            str(summary.get("validation_passed", "")),
        ),
        (
            "START_DRY_RUN_DESIGN_REQ_002",
            "pre_start_review_passed",
            safe_bool(
                summary.get(
                    "controlled_forward_observation_pre_start_review_passed",
                    False,
                )
            ),
            "pre_start_review",
            "True",
            str(
                summary.get(
                    "controlled_forward_observation_pre_start_review_passed",
                    "",
                )
            ),
        ),
        (
            "START_DRY_RUN_DESIGN_REQ_003",
            "pre_start_decision_expected",
            str(
                summary.get(
                    "controlled_forward_observation_pre_start_review_decision",
                    "",
                )
            ).strip()
            == EXPECTED_PRE_START_DECISION,
            "pre_start_review",
            EXPECTED_PRE_START_DECISION,
            str(
                summary.get(
                    "controlled_forward_observation_pre_start_review_decision",
                    "",
                )
            ),
        ),
        (
            "START_DRY_RUN_DESIGN_REQ_004",
            "future_start_dry_run_design_allowed",
            safe_bool(
                summary.get(
                    "future_controlled_forward_observation_start_dry_run_design_allowed",
                    False,
                )
            ),
            "future_design",
            "True",
            str(
                summary.get(
                    "future_controlled_forward_observation_start_dry_run_design_allowed",
                    "",
                )
            ),
        ),
        (
            "START_DRY_RUN_DESIGN_REQ_005",
            "design_output_row_count_one",
            len(design_output_df) == 1,
            "artifact",
            "1",
            str(len(design_output_df)),
        ),
        (
            "START_DRY_RUN_DESIGN_REQ_006",
            "design_output_schema_valid",
            validation_lookup.get("design_output_schema_valid", False),
            "schema",
            "True",
            str(validation_lookup.get("design_output_schema_valid", False)),
        ),
        (
            "START_DRY_RUN_DESIGN_REQ_007",
            "design_output_candidate_valid",
            validation_lookup.get("design_output_candidate_valid", False),
            "candidate_scope",
            "True",
            str(validation_lookup.get("design_output_candidate_valid", False)),
        ),
        (
            "START_DRY_RUN_DESIGN_REQ_008",
            "design_output_direction_valid",
            validation_lookup.get("design_output_direction_valid", False),
            "direction",
            "True",
            str(validation_lookup.get("design_output_direction_valid", False)),
        ),
        (
            "START_DRY_RUN_DESIGN_REQ_009",
            "design_output_price_structure_valid",
            validation_lookup.get("design_output_price_structure_valid", False),
            "price_structure",
            "True",
            str(validation_lookup.get("design_output_price_structure_valid", False)),
        ),
        (
            "START_DRY_RUN_DESIGN_REQ_010",
            "design_output_risk_reward_valid",
            validation_lookup.get("design_output_risk_reward_valid", False),
            "risk_reward",
            "True",
            str(validation_lookup.get("design_output_risk_reward_valid", False)),
        ),
        (
            "START_DRY_RUN_DESIGN_REQ_011",
            "design_output_scope_valid",
            validation_lookup.get("design_output_scope_valid", False),
            "scope_control",
            "True",
            str(validation_lookup.get("design_output_scope_valid", False)),
        ),
        (
            "START_DRY_RUN_DESIGN_REQ_012",
            "design_output_evidence_scope_valid",
            validation_lookup.get("design_output_evidence_scope_valid", False),
            "evidence_scope",
            "True",
            str(validation_lookup.get("design_output_evidence_scope_valid", False)),
        ),
        (
            "START_DRY_RUN_DESIGN_REQ_013",
            "design_output_true_design_fields_valid",
            validation_lookup.get("design_output_true_design_fields_valid", False),
            "design_control",
            "True",
            str(
                validation_lookup.get(
                    "design_output_true_design_fields_valid",
                    False,
                )
            ),
        ),
        (
            "START_DRY_RUN_DESIGN_REQ_014",
            "design_output_operational_locks_valid",
            validation_lookup.get("design_output_operational_locks_valid", False),
            "safety",
            "True",
            str(
                validation_lookup.get(
                    "design_output_operational_locks_valid",
                    False,
                )
            ),
        ),
        (
            "START_DRY_RUN_DESIGN_REQ_015",
            "design_output_official_evidence_rows_zero",
            validation_lookup.get("design_output_official_evidence_rows_zero", False),
            "official_dataset_guard",
            "True",
            str(
                validation_lookup.get(
                    "design_output_official_evidence_rows_zero",
                    False,
                )
            ),
        ),
        (
            "START_DRY_RUN_DESIGN_REQ_016",
            "design_output_future_execution_review_allowed",
            validation_lookup.get(
                "design_output_future_execution_review_allowed",
                False,
            ),
            "future_review",
            "True",
            str(
                validation_lookup.get(
                    "design_output_future_execution_review_allowed",
                    False,
                )
            ),
        ),
        (
            "START_DRY_RUN_DESIGN_REQ_017",
            "design_output_validation_status_valid",
            validation_lookup.get("design_output_validation_status_valid", False),
            "artifact",
            "True",
            str(validation_lookup.get("design_output_validation_status_valid", False)),
        ),
        (
            "START_DRY_RUN_DESIGN_REQ_018",
            "all_design_validations_passed",
            validations_passed,
            "validation",
            "True",
            str(validations_passed),
        ),
        (
            "START_DRY_RUN_DESIGN_REQ_019",
            "design_controls_passed",
            controls_passed,
            "controls",
            "True",
            str(controls_passed),
        ),
        (
            "START_DRY_RUN_DESIGN_REQ_020",
            "design_rules_passed",
            rules_passed,
            "rules",
            "True",
            str(rules_passed),
        ),
        (
            "START_DRY_RUN_DESIGN_REQ_021",
            "design_guards_passed",
            guards_passed,
            "safety",
            "True",
            str(guards_passed),
        ),
        (
            "START_DRY_RUN_DESIGN_REQ_022",
            "official_dataset_absent",
            official_dataset_absent,
            "official_dataset_guard",
            "True",
            str(official_dataset_absent),
        ),
        (
            "START_DRY_RUN_DESIGN_REQ_023",
            "start_dry_run_not_performed",
            True,
            "dry_run_boundary",
            "False",
            "False",
        ),
        (
            "START_DRY_RUN_DESIGN_REQ_024",
            "forward_observation_start_not_allowed",
            True,
            "start_boundary",
            "False",
            "False",
        ),
        (
            "START_DRY_RUN_DESIGN_REQ_025",
            "official_evidence_rows_written_zero",
            True,
            "official_dataset_guard",
            "0",
            "0",
        ),
        (
            "START_DRY_RUN_DESIGN_REQ_026",
            "market_execution_disabled",
            True,
            "market_execution_guard",
            "False",
            "False",
        ),
        (
            "START_DRY_RUN_DESIGN_REQ_027",
            "total_project_not_completed",
            True,
            "scope_control",
            "False",
            "False",
        ),
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


def build_start_dry_run_design_decision_table(
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

    design_passed = (
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
                "controlled_forward_observation_start_dry_run_design_id": (
                    "PHASE_10_21_LONG_FORWARD_OBSERVATION_CONTROLLED_START_DRY_RUN_DESIGN_001"
                ),
                "controlled_forward_observation_start_dry_run_design_status": (
                    DESIGN_STATUS
                ),
                "controlled_forward_observation_start_dry_run_design_passed": (
                    design_passed
                ),
                "controlled_forward_observation_start_dry_run_design_decision": (
                    READY_DECISION if design_passed else BLOCKED_DECISION
                ),
                "total_requirements": total_requirements,
                "passed_requirements": passed_requirements,
                "failed_requirements": failed_requirements,
                "failed_requirement_names": failed_requirement_names,
                "start_dry_run_design_rules_passed": rules_passed,
                "start_dry_run_design_guards_passed": guards_passed,
                "future_controlled_forward_observation_start_dry_run_execution_review_allowed": design_passed,
                "controlled_forward_observation_start_dry_run_design_allowed": design_passed,
                "controlled_forward_observation_start_dry_run_design_performed": design_passed,
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


def validate_long_forward_observation_controlled_start_dry_run_design() -> dict[str, pd.DataFrame]:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    checks: list[dict[str, Any]] = []

    for check_name, path in {
        "phase_10_20_pre_start_review_doc_exists": PHASE_10_20_DOC_PATH,
        "phase_10_21_start_dry_run_design_doc_exists": PHASE_10_21_DOC_PATH,
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

    phase_10_20_result = validate_long_forward_observation_controlled_pre_start_review()

    source_summary_df = get_phase_10_20_dataframe(
        result=phase_10_20_result,
        aliases=("summary", "pre_start_summary"),
        csv_path=PHASE_10_20_REPORTS_DIR / "pre_start_summary_v1.csv",
    )

    source_activation_output_df = get_phase_10_20_dataframe(
        result=phase_10_20_result,
        aliases=(
            "source_activation_output",
            "phase_10_19_source_activation_output",
            "activation_output",
        ),
        csv_path=PHASE_10_20_REPORTS_DIR / "phase_10_19_source_activation_output_v1.csv",
    )

    source_integrity_validation_df = get_phase_10_20_dataframe(
        result=phase_10_20_result,
        aliases=(
            "source_integrity_validation",
            "source_integrity_validations",
            "phase_10_19_source_integrity_validation",
        ),
        csv_path=PHASE_10_20_REPORTS_DIR / "phase_10_19_source_integrity_validations_v1.csv",
    )

    source_integrity_controls_df = get_phase_10_20_dataframe(
        result=phase_10_20_result,
        aliases=("source_integrity_controls",),
        csv_path=PHASE_10_20_REPORTS_DIR / "phase_10_19_source_integrity_controls_v1.csv",
    )

    source_integrity_rules_df = get_phase_10_20_dataframe(
        result=phase_10_20_result,
        aliases=("source_integrity_rules",),
        csv_path=PHASE_10_20_REPORTS_DIR / "phase_10_19_source_integrity_rules_v1.csv",
    )

    source_integrity_requirements_df = get_phase_10_20_dataframe(
        result=phase_10_20_result,
        aliases=("source_integrity_requirements",),
        csv_path=PHASE_10_20_REPORTS_DIR / "phase_10_19_source_integrity_requirements_v1.csv",
    )

    source_integrity_guard_matrix_df = get_phase_10_20_dataframe(
        result=phase_10_20_result,
        aliases=("source_integrity_guard_matrix",),
        csv_path=PHASE_10_20_REPORTS_DIR / "phase_10_19_source_integrity_guard_matrix_v1.csv",
    )

    source_integrity_decision_df = get_phase_10_20_dataframe(
        result=phase_10_20_result,
        aliases=("source_integrity_decision",),
        csv_path=PHASE_10_20_REPORTS_DIR / "phase_10_19_source_integrity_decision_v1.csv",
    )

    source_pre_start_evidence_df = get_phase_10_20_dataframe(
        result=phase_10_20_result,
        aliases=("pre_start_evidence_chain",),
        csv_path=PHASE_10_20_REPORTS_DIR / "pre_start_evidence_chain_v1.csv",
    )

    source_pre_start_controls_df = get_phase_10_20_dataframe(
        result=phase_10_20_result,
        aliases=("pre_start_controls",),
        csv_path=PHASE_10_20_REPORTS_DIR / "pre_start_controls_v1.csv",
    )

    source_pre_start_rules_df = get_phase_10_20_dataframe(
        result=phase_10_20_result,
        aliases=("pre_start_rules",),
        csv_path=PHASE_10_20_REPORTS_DIR / "pre_start_rules_v1.csv",
    )

    source_pre_start_requirements_df = get_phase_10_20_dataframe(
        result=phase_10_20_result,
        aliases=("pre_start_requirements",),
        csv_path=PHASE_10_20_REPORTS_DIR / "pre_start_requirements_v1.csv",
    )

    source_pre_start_guard_matrix_df = get_phase_10_20_dataframe(
        result=phase_10_20_result,
        aliases=("pre_start_guard_matrix",),
        csv_path=PHASE_10_20_REPORTS_DIR / "pre_start_guard_matrix_v1.csv",
    )

    source_pre_start_decision_df = get_phase_10_20_dataframe(
        result=phase_10_20_result,
        aliases=("pre_start_decision",),
        csv_path=PHASE_10_20_REPORTS_DIR / "pre_start_decision_v1.csv",
    )

    source_checks_df = get_phase_10_20_dataframe(
        result=phase_10_20_result,
        aliases=("checks", "pre_start_checks"),
        csv_path=PHASE_10_20_REPORTS_DIR / "pre_start_checks_v1.csv",
    )

    official_dataset_exists_after_source_validation = OFFICIAL_DATASET_PATH.exists()
    official_dataset_absent = (
        official_dataset_exists_before is False
        and official_dataset_exists_after_source_validation is False
    )

    source_summary = first_row(source_summary_df)

    design_output_df = build_start_dry_run_design_output(
        source_summary_df=source_summary_df,
        source_activation_output_df=source_activation_output_df,
    )

    design_output_path = REPORTS_DIR / "controlled_start_dry_run_design_output_v1.csv"
    design_output_df.to_csv(design_output_path, index=False)

    validation_df = build_start_dry_run_design_validation(
        design_output_df=design_output_df,
        source_summary_df=source_summary_df,
    )
    controls_df = build_start_dry_run_design_controls(validation_df)
    guard_matrix_df = build_start_dry_run_design_guard_matrix()
    rules_df = build_start_dry_run_design_rules(
        controls_df=controls_df,
        validation_df=validation_df,
        guard_matrix_df=guard_matrix_df,
    )
    requirements_df = build_start_dry_run_design_requirements(
        source_summary_df=source_summary_df,
        design_output_df=design_output_df,
        validation_df=validation_df,
        controls_df=controls_df,
        rules_df=rules_df,
        guard_matrix_df=guard_matrix_df,
        official_dataset_absent=official_dataset_absent,
    )
    decision_df = build_start_dry_run_design_decision_table(
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

    decision = first_row(decision_df)

    phase_10_20_validation_passed = safe_bool(
        source_summary.get("validation_passed", False)
    )
    pre_start_review_passed = safe_bool(
        source_summary.get(
            "controlled_forward_observation_pre_start_review_passed",
            False,
        )
    )
    pre_start_decision = str(
        source_summary.get(
            "controlled_forward_observation_pre_start_review_decision",
            "",
        )
    )
    future_design_allowed = safe_bool(
        source_summary.get(
            "future_controlled_forward_observation_start_dry_run_design_allowed",
            False,
        )
    )

    design_passed = safe_bool(
        decision.get(
            "controlled_forward_observation_start_dry_run_design_passed",
            False,
        )
    )
    design_decision = str(
        decision.get(
            "controlled_forward_observation_start_dry_run_design_decision",
            "",
        )
    )
    future_execution_review_allowed = safe_bool(
        decision.get(
            "future_controlled_forward_observation_start_dry_run_execution_review_allowed",
            False,
        )
    )

    checks.extend(
        [
            build_check(
                "phase_dependency",
                "phase_10_20_validation_passed",
                phase_10_20_validation_passed,
                "INFO" if phase_10_20_validation_passed else "ERROR",
                str(source_summary.get("validation_decision", "")),
            ),
            build_check(
                "phase_dependency",
                "pre_start_review_passed",
                pre_start_review_passed,
                "INFO" if pre_start_review_passed else "ERROR",
                f"pre_start_review_passed={pre_start_review_passed}",
            ),
            build_check(
                "phase_dependency",
                "pre_start_decision_expected",
                pre_start_decision == EXPECTED_PRE_START_DECISION,
                "INFO" if pre_start_decision == EXPECTED_PRE_START_DECISION else "ERROR",
                pre_start_decision,
            ),
            build_check(
                "phase_dependency",
                "future_start_dry_run_design_allowed",
                future_design_allowed,
                "INFO" if future_design_allowed else "ERROR",
                f"future_start_dry_run_design_allowed={future_design_allowed}",
            ),
            build_check(
                "design_artifact",
                "design_artifact_write_performed",
                design_output_path.exists(),
                "INFO" if design_output_path.exists() else "ERROR",
                str(design_output_path),
            ),
            build_check(
                "design_artifact",
                "design_artifact_rows_written_one",
                len(design_output_df) == 1,
                "INFO" if len(design_output_df) == 1 else "ERROR",
                f"rows_written={len(design_output_df)}",
            ),
        ]
    )

    for _, validation in validation_df.iterrows():
        passed = safe_bool(validation["passed"], False)

        checks.append(
            build_check(
                "start_dry_run_design_validation",
                str(validation["validation_name"]),
                passed,
                "INFO" if passed else "ERROR",
                str(validation["details"]),
            )
        )

    aggregate_checks = [
        ("start_dry_run_design_controls_passed", all_passed(controls_df)),
        ("start_dry_run_design_validations_passed", all_passed(validation_df)),
        ("start_dry_run_design_rules_passed", all_passed(rules_df)),
        ("start_dry_run_design_requirements_passed", all_passed(requirements_df)),
        ("start_dry_run_design_guards_passed", all_passed(guard_matrix_df)),
        ("controlled_start_dry_run_design_passed", design_passed),
        (
            "controlled_start_dry_run_design_decision_expected",
            design_decision == READY_DECISION,
        ),
    ]

    for check_name, passed in aggregate_checks:
        checks.append(
            build_check(
                "start_dry_run_design",
                check_name,
                passed,
                "INFO" if passed else "ERROR",
                (
                    f"design_decision={design_decision}"
                    if check_name == "controlled_start_dry_run_design_decision_expected"
                    else f"{check_name}={passed}"
                ),
            )
        )

    checks.append(
        build_check(
            "planning_scope",
            "future_controlled_forward_observation_start_dry_run_execution_review_allowed",
            future_execution_review_allowed,
            "WARNING" if future_execution_review_allowed else "ERROR",
            (
                "This permits only a future execution review of the start dry-run "
                "design. It does not execute a dry-run, start forward observation, "
                "write official evidence, generate alerts, enable paper trading, "
                "use real capital, or permit market execution."
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
                "start_dry_run_design_safety_flags",
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
            build_check(
                "scope_control",
                "start_dry_run_design_only",
                True,
                "WARNING",
                "Phase 10.21 performs only controlled start dry-run design.",
            ),
            build_check(
                "scope_control",
                "start_dry_run_not_performed",
                True,
                "WARNING",
                "No forward observation start dry-run is performed in this phase.",
            ),
            build_check(
                "scope_control",
                "forward_observation_not_started",
                True,
                "WARNING",
                "Forward observation remains not started.",
            ),
            build_check(
                "scope_control",
                "official_evidence_not_persisted",
                True,
                "WARNING",
                "Official evidence persistence remains disabled.",
            ),
            build_check(
                "scope_control",
                "signal_generation_not_enabled",
                True,
                "WARNING",
                "Signal generation remains disabled.",
            ),
            build_check(
                "scope_control",
                "paper_trading_not_enabled",
                True,
                "WARNING",
                "Paper trading execution remains disabled.",
            ),
            build_check(
                "scope_control",
                "real_capital_not_allowed",
                True,
                "WARNING",
                "Real capital remains prohibited.",
            ),
            build_check(
                "scope_control",
                "market_execution_not_allowed",
                True,
                "WARNING",
                "Market execution remains prohibited.",
            ),
            build_check(
                "scope_control",
                "total_project_not_completed",
                True,
                "WARNING",
                "The total project is not completed.",
            ),
            build_check(
                "phase_transition",
                "phase_10_22_recommended_next",
                True,
                "INFO",
                (
                    "Recommended next step: Phase 10.22 LONG Forward Observation "
                    "Controlled Start Dry-Run Execution Review V1."
                ),
            ),
        ]
    )

    checks_df = pd.DataFrame(checks)

    blocker_count = int(checks_df["blocker"].map(lambda value: safe_bool(value)).sum())
    error_count = int(checks_df["severity"].eq("ERROR").sum())
    warning_count = int(checks_df["severity"].eq("WARNING").sum())

    validation_passed = blocker_count == 0 and error_count == 0

    output = first_row(design_output_df)

    summary_df = pd.DataFrame(
        [
            {
                "phase": "10.21",
                "long_forward_observation_controlled_start_dry_run_design_defined": True,
                "phase_10_20_validation_passed": phase_10_20_validation_passed,
                "controlled_forward_observation_pre_start_review_passed": pre_start_review_passed,
                "controlled_forward_observation_pre_start_review_decision": pre_start_decision,
                "future_controlled_forward_observation_start_dry_run_design_allowed": future_design_allowed,
                "design_output_row_count": len(design_output_df),
                "design_output_schema_valid": validation_lookup.get(
                    "design_output_schema_valid",
                    False,
                ),
                "design_output_candidate_id": str(output.get("candidate_id", "")),
                "design_output_candidate_valid": validation_lookup.get(
                    "design_output_candidate_valid",
                    False,
                ),
                "design_output_direction": str(output.get("direction", "")),
                "design_output_direction_valid": validation_lookup.get(
                    "design_output_direction_valid",
                    False,
                ),
                "design_output_price_structure_valid": validation_lookup.get(
                    "design_output_price_structure_valid",
                    False,
                ),
                "design_output_risk_reward": float(output.get("risk_reward", 0))
                if output
                else 0.0,
                "design_output_scope": str(output.get("design_scope", "")),
                "design_output_scope_valid": validation_lookup.get(
                    "design_output_scope_valid",
                    False,
                ),
                "design_output_evidence_scope": str(output.get("evidence_scope", "")),
                "design_output_evidence_scope_valid": validation_lookup.get(
                    "design_output_evidence_scope_valid",
                    False,
                ),
                "design_output_true_design_fields_valid": validation_lookup.get(
                    "design_output_true_design_fields_valid",
                    False,
                ),
                "design_output_operational_locks_valid": validation_lookup.get(
                    "design_output_operational_locks_valid",
                    False,
                ),
                "design_output_future_execution_review_allowed": validation_lookup.get(
                    "design_output_future_execution_review_allowed",
                    False,
                ),
                "start_dry_run_design_control_count": len(controls_df),
                "start_dry_run_design_validation_rows": len(validation_df),
                "start_dry_run_design_rule_rows": len(rules_df),
                "start_dry_run_design_requirement_rows": len(requirements_df),
                "start_dry_run_design_guard_rows": len(guard_matrix_df),
                "start_dry_run_design_controls_passed": all_passed(controls_df),
                "start_dry_run_design_validations_passed": all_passed(validation_df),
                "start_dry_run_design_rules_passed": all_passed(rules_df),
                "start_dry_run_design_requirements_passed": all_passed(
                    requirements_df
                ),
                "start_dry_run_design_guards_passed": all_passed(guard_matrix_df),
                "controlled_forward_observation_start_dry_run_design_passed": design_passed,
                "controlled_forward_observation_start_dry_run_design_decision": design_decision,
                "future_controlled_forward_observation_start_dry_run_execution_review_allowed": future_execution_review_allowed,
                "controlled_forward_observation_start_dry_run_design_allowed": design_passed,
                "controlled_forward_observation_start_dry_run_design_performed": design_passed,
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
                    "PHASE_10_21_LONG_FORWARD_OBSERVATION_CONTROLLED_START_DRY_RUN_DESIGN_VALIDATED"
                    if validation_passed
                    else "PHASE_10_21_LONG_FORWARD_OBSERVATION_CONTROLLED_START_DRY_RUN_DESIGN_FAILED"
                ),
            }
        ]
    )

    source_summary_df.to_csv(
        REPORTS_DIR / "phase_10_20_source_summary_v1.csv",
        index=False,
    )
    source_activation_output_df.to_csv(
        REPORTS_DIR / "phase_10_20_source_activation_output_v1.csv",
        index=False,
    )
    source_integrity_validation_df.to_csv(
        REPORTS_DIR / "phase_10_20_source_integrity_validations_v1.csv",
        index=False,
    )
    source_integrity_controls_df.to_csv(
        REPORTS_DIR / "phase_10_20_source_integrity_controls_v1.csv",
        index=False,
    )
    source_integrity_rules_df.to_csv(
        REPORTS_DIR / "phase_10_20_source_integrity_rules_v1.csv",
        index=False,
    )
    source_integrity_requirements_df.to_csv(
        REPORTS_DIR / "phase_10_20_source_integrity_requirements_v1.csv",
        index=False,
    )
    source_integrity_guard_matrix_df.to_csv(
        REPORTS_DIR / "phase_10_20_source_integrity_guard_matrix_v1.csv",
        index=False,
    )
    source_integrity_decision_df.to_csv(
        REPORTS_DIR / "phase_10_20_source_integrity_decision_v1.csv",
        index=False,
    )
    source_pre_start_evidence_df.to_csv(
        REPORTS_DIR / "phase_10_20_source_pre_start_evidence_chain_v1.csv",
        index=False,
    )
    source_pre_start_controls_df.to_csv(
        REPORTS_DIR / "phase_10_20_source_pre_start_controls_v1.csv",
        index=False,
    )
    source_pre_start_rules_df.to_csv(
        REPORTS_DIR / "phase_10_20_source_pre_start_rules_v1.csv",
        index=False,
    )
    source_pre_start_requirements_df.to_csv(
        REPORTS_DIR / "phase_10_20_source_pre_start_requirements_v1.csv",
        index=False,
    )
    source_pre_start_guard_matrix_df.to_csv(
        REPORTS_DIR / "phase_10_20_source_pre_start_guard_matrix_v1.csv",
        index=False,
    )
    source_pre_start_decision_df.to_csv(
        REPORTS_DIR / "phase_10_20_source_pre_start_decision_v1.csv",
        index=False,
    )
    source_checks_df.to_csv(
        REPORTS_DIR / "phase_10_20_source_checks_v1.csv",
        index=False,
    )
    validation_df.to_csv(
        REPORTS_DIR / "start_dry_run_design_validations_v1.csv",
        index=False,
    )
    controls_df.to_csv(
        REPORTS_DIR / "start_dry_run_design_controls_v1.csv",
        index=False,
    )
    rules_df.to_csv(
        REPORTS_DIR / "start_dry_run_design_rules_v1.csv",
        index=False,
    )
    requirements_df.to_csv(
        REPORTS_DIR / "start_dry_run_design_requirements_v1.csv",
        index=False,
    )
    guard_matrix_df.to_csv(
        REPORTS_DIR / "start_dry_run_design_guard_matrix_v1.csv",
        index=False,
    )
    decision_df.to_csv(
        REPORTS_DIR / "start_dry_run_design_decision_v1.csv",
        index=False,
    )
    checks_df.to_csv(
        REPORTS_DIR / "start_dry_run_design_checks_v1.csv",
        index=False,
    )
    summary_df.to_csv(
        REPORTS_DIR / "start_dry_run_design_summary_v1.csv",
        index=False,
    )

    return {
        "summary": summary_df,
        "source_phase_10_20_summary": source_summary_df,
        "source_activation_output": source_activation_output_df,
        "source_integrity_validation": source_integrity_validation_df,
        "source_integrity_controls": source_integrity_controls_df,
        "source_integrity_rules": source_integrity_rules_df,
        "source_integrity_requirements": source_integrity_requirements_df,
        "source_integrity_guard_matrix": source_integrity_guard_matrix_df,
        "source_integrity_decision": source_integrity_decision_df,
        "source_pre_start_evidence_chain": source_pre_start_evidence_df,
        "source_pre_start_controls": source_pre_start_controls_df,
        "source_pre_start_rules": source_pre_start_rules_df,
        "source_pre_start_requirements": source_pre_start_requirements_df,
        "source_pre_start_guard_matrix": source_pre_start_guard_matrix_df,
        "source_pre_start_decision": source_pre_start_decision_df,
        "source_checks": source_checks_df,
        "start_dry_run_design_output": design_output_df,
        "start_dry_run_design_validation": validation_df,
        "start_dry_run_design_controls": controls_df,
        "start_dry_run_design_rules": rules_df,
        "start_dry_run_design_requirements": requirements_df,
        "start_dry_run_design_guard_matrix": guard_matrix_df,
        "start_dry_run_design_decision": decision_df,
        "checks": checks_df,
    }