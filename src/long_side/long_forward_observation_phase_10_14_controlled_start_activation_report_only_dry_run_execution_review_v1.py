from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from src.long_side.long_forward_observation_dataset_bootstrap_v1 import (
    OFFICIAL_DATASET_PATH,
    PRIMARY_RESEARCH_CANDIDATE,
)
from src.long_side.long_forward_observation_phase_10_13_controlled_start_activation_report_only_dry_run_design_v1 import (
    READY_DECISION as REPORT_ONLY_DRY_RUN_DESIGN_READY_DECISION,
    validate_long_forward_observation_controlled_start_activation_report_only_dry_run_design,
)


REPORTS_DIR = Path(
    "reports/p10_14_activation_exec_review_v1"
)

PHASE_10_13_CONTROLLED_START_ACTIVATION_REPORT_ONLY_DRY_RUN_DESIGN_DOC_PATH = Path(
    "docs/PHASE_10_LONG_FORWARD_OBSERVATION_CONTROLLED_START_ACTIVATION_REPORT_ONLY_DRY_RUN_DESIGN.md"
)
PHASE_10_14_CONTROLLED_START_ACTIVATION_REPORT_ONLY_DRY_RUN_EXECUTION_REVIEW_DOC_PATH = Path(
    "docs/PHASE_10_LONG_FORWARD_OBSERVATION_CONTROLLED_START_ACTIVATION_REPORT_ONLY_DRY_RUN_EXECUTION_REVIEW.md"
)

CONTROLLED_START_ACTIVATION_REPORT_ONLY_DRY_RUN_EXECUTION_REVIEW_STATUS = (
    "LONG_FORWARD_OBSERVATION_CONTROLLED_START_ACTIVATION_REPORT_ONLY_DRY_RUN_EXECUTION_REVIEW_ONLY"
)

READY_DECISION = (
    "CONTROLLED_START_ACTIVATION_REPORT_ONLY_DRY_RUN_EXECUTION_REVIEW_READY_FOR_CONTROLLED_RUN"
)
BLOCKED_DECISION = (
    "CONTROLLED_START_ACTIVATION_REPORT_ONLY_DRY_RUN_EXECUTION_REVIEW_BLOCKED"
)

RECOMMENDED_NEXT_PHASE = (
    "PHASE_10_15_LONG_FORWARD_OBSERVATION_CONTROLLED_START_ACTIVATION_REPORT_ONLY_DRY_RUN_RUN_V1"
)

EXECUTION_REVIEW_ITEMS = [
    ("EXECUTION_REVIEW_ITEM_001", "confirm_phase_10_13_report_only_dry_run_design", "dependency"),
    ("EXECUTION_REVIEW_ITEM_002", "confirm_report_only_dry_run_design_decision", "design_decision"),
    ("EXECUTION_REVIEW_ITEM_003", "confirm_future_execution_review_allowed", "future_review"),
    ("EXECUTION_REVIEW_ITEM_004", "confirm_schema_field_count_52", "schema"),
    ("EXECUTION_REVIEW_ITEM_005", "confirm_schema_required_fields", "schema"),
    ("EXECUTION_REVIEW_ITEM_006", "confirm_component_count_14", "components"),
    ("EXECUTION_REVIEW_ITEM_007", "confirm_control_count_20", "controls"),
    ("EXECUTION_REVIEW_ITEM_008", "confirm_candidate_scope", "candidate_scope"),
    ("EXECUTION_REVIEW_ITEM_009", "confirm_long_direction_scope", "direction"),
    ("EXECUTION_REVIEW_ITEM_010", "confirm_report_only_scope", "report_only_scope"),
    ("EXECUTION_REVIEW_ITEM_011", "confirm_synthetic_evidence_scope", "evidence_source"),
    ("EXECUTION_REVIEW_ITEM_012", "confirm_no_dry_run_execution_yet", "dry_run_boundary"),
    ("EXECUTION_REVIEW_ITEM_013", "confirm_no_forward_start", "start_boundary"),
    ("EXECUTION_REVIEW_ITEM_014", "confirm_operational_locks", "safety"),
    ("EXECUTION_REVIEW_ITEM_015", "prepare_future_controlled_report_only_run", "future_run"),
]

EXECUTION_REVIEW_CONTROLS = [
    ("EXECUTION_REVIEW_CONTROL_001", "phase_10_13_validation_passed", "dependency"),
    ("EXECUTION_REVIEW_CONTROL_002", "report_only_dry_run_design_passed", "design"),
    ("EXECUTION_REVIEW_CONTROL_003", "report_only_dry_run_design_decision_confirmed", "design"),
    ("EXECUTION_REVIEW_CONTROL_004", "future_execution_review_allowed", "future_review"),
    ("EXECUTION_REVIEW_CONTROL_005", "schema_field_count_confirmed", "schema"),
    ("EXECUTION_REVIEW_CONTROL_006", "schema_required_fields_confirmed", "schema"),
    ("EXECUTION_REVIEW_CONTROL_007", "component_count_confirmed", "components"),
    ("EXECUTION_REVIEW_CONTROL_008", "control_count_confirmed", "controls"),
    ("EXECUTION_REVIEW_CONTROL_009", "candidate_scope_locked", "candidate_scope"),
    ("EXECUTION_REVIEW_CONTROL_010", "long_direction_locked", "direction"),
    ("EXECUTION_REVIEW_CONTROL_011", "manual_confirmation_required", "manual_control"),
    ("EXECUTION_REVIEW_CONTROL_012", "report_only_scope_locked", "report_only_scope"),
    ("EXECUTION_REVIEW_CONTROL_013", "synthetic_evidence_scope_locked", "evidence_source"),
    ("EXECUTION_REVIEW_CONTROL_014", "future_controlled_report_only_run_allowed", "future_run"),
    ("EXECUTION_REVIEW_CONTROL_015", "dry_run_execution_not_performed", "dry_run_boundary"),
    ("EXECUTION_REVIEW_CONTROL_016", "activation_not_performed", "activation_boundary"),
    ("EXECUTION_REVIEW_CONTROL_017", "forward_observation_start_disabled", "start_boundary"),
    ("EXECUTION_REVIEW_CONTROL_018", "official_dataset_write_disabled", "official_dataset_guard"),
    ("EXECUTION_REVIEW_CONTROL_019", "signal_generation_and_alerts_disabled", "signals_alerts"),
    ("EXECUTION_REVIEW_CONTROL_020", "capital_and_execution_disabled", "execution"),
    ("EXECUTION_REVIEW_CONTROL_021", "automation_disabled", "automation"),
]

EXPECTED_FALSE_GUARDS = {
    "controlled_forward_observation_start_approved": False,
    "controlled_forward_observation_start_activation_performed": False,
    "controlled_forward_observation_start_dry_run_performed": False,
    "controlled_start_activation_report_only_dry_run_execution_allowed": False,
    "controlled_start_activation_report_only_dry_run_execution_performed": False,
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


def build_execution_review_items() -> pd.DataFrame:
    rows: list[dict[str, Any]] = []

    for position, (item_id, item_name, item_group) in enumerate(
        EXECUTION_REVIEW_ITEMS,
        start=1,
    ):
        rows.append(
            {
                "item_position": position,
                "item_id": item_id,
                "item_name": item_name,
                "item_group": item_group,
                "required": True,
                "execution_review_only": True,
                "future_controlled_report_only_run_allowed": True,
                "dry_run_execution_allowed": False,
                "dry_run_execution_performed": False,
                "activation_performed": False,
                "forward_observation_start_allowed": False,
                "official_dataset_write_allowed": False,
                "market_execution_allowed": False,
                "passed": True,
            }
        )

    return pd.DataFrame(rows)


def build_execution_review_controls() -> pd.DataFrame:
    rows: list[dict[str, Any]] = []

    for control_id, control_name, control_group in EXECUTION_REVIEW_CONTROLS:
        rows.append(
            {
                "control_id": control_id,
                "control_name": control_name,
                "control_group": control_group,
                "required": True,
                "execution_review_only": True,
                "future_controlled_report_only_run_allowed": True,
                "dry_run_execution_allowed": False,
                "dry_run_execution_performed": False,
                "activation_performed": False,
                "controlled_start_approved": False,
                "forward_observation_start_allowed": False,
                "official_dataset_write_allowed": False,
                "real_evidence_acceptance_allowed": False,
                "signal_generation_allowed": False,
                "live_alerts_allowed": False,
                "paper_trading_allowed": False,
                "real_capital_allowed": False,
                "market_execution_allowed": False,
                "exchange_execution_allowed": False,
                "automation_allowed": False,
                "passed": True,
            }
        )

    return pd.DataFrame(rows)


def build_execution_review_rules(
    items_df: pd.DataFrame,
    controls_df: pd.DataFrame,
) -> pd.DataFrame:
    item_count = int(len(items_df))
    control_count = int(len(controls_df))

    items_passed = not items_df.empty and items_df["passed"].astype(bool).all()
    controls_passed = not controls_df.empty and controls_df["passed"].astype(bool).all()

    all_items_review_only = (
        not items_df.empty and items_df["execution_review_only"].astype(bool).all()
    )
    all_items_future_run_only = (
        not items_df.empty
        and items_df["future_controlled_report_only_run_allowed"].astype(bool).all()
    )
    all_items_no_execution = (
        not items_df.empty
        and items_df["dry_run_execution_allowed"].astype(bool).eq(False).all()
        and items_df["dry_run_execution_performed"].astype(bool).eq(False).all()
    )
    all_items_no_activation = (
        not items_df.empty
        and items_df["activation_performed"].astype(bool).eq(False).all()
    )

    all_controls_review_only = (
        not controls_df.empty and controls_df["execution_review_only"].astype(bool).all()
    )
    all_controls_future_run_only = (
        not controls_df.empty
        and controls_df["future_controlled_report_only_run_allowed"].astype(bool).all()
    )
    all_controls_no_execution = (
        not controls_df.empty
        and controls_df["dry_run_execution_allowed"].astype(bool).eq(False).all()
        and controls_df["dry_run_execution_performed"].astype(bool).eq(False).all()
    )
    all_controls_no_activation = (
        not controls_df.empty
        and controls_df["activation_performed"].astype(bool).eq(False).all()
    )
    all_controlled_start_not_approved = (
        not controls_df.empty
        and controls_df["controlled_start_approved"].astype(bool).eq(False).all()
    )
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
        ("EXECUTION_REVIEW_RULE_001", "execution_review_item_count_15", item_count == 15, "15", str(item_count), "items"),
        ("EXECUTION_REVIEW_RULE_002", "all_items_passed", items_passed, "True", str(items_passed), "items"),
        ("EXECUTION_REVIEW_RULE_003", "all_items_execution_review_only", all_items_review_only, "True", str(all_items_review_only), "scope_control"),
        ("EXECUTION_REVIEW_RULE_004", "all_items_allow_only_future_run", all_items_future_run_only, "True", str(all_items_future_run_only), "future_run"),
        ("EXECUTION_REVIEW_RULE_005", "all_items_no_dry_run_execution", all_items_no_execution, "False", "False", "dry_run_boundary"),
        ("EXECUTION_REVIEW_RULE_006", "all_items_no_activation", all_items_no_activation, "False", "False", "activation_boundary"),
        ("EXECUTION_REVIEW_RULE_007", "execution_review_control_count_21", control_count == 21, "21", str(control_count), "controls"),
        ("EXECUTION_REVIEW_RULE_008", "all_controls_passed", controls_passed, "True", str(controls_passed), "controls"),
        ("EXECUTION_REVIEW_RULE_009", "all_controls_execution_review_only", all_controls_review_only, "True", str(all_controls_review_only), "scope_control"),
        ("EXECUTION_REVIEW_RULE_010", "all_controls_allow_only_future_run", all_controls_future_run_only, "True", str(all_controls_future_run_only), "future_run"),
        ("EXECUTION_REVIEW_RULE_011", "all_controls_no_dry_run_execution", all_controls_no_execution, "False", "False", "dry_run_boundary"),
        ("EXECUTION_REVIEW_RULE_012", "all_controls_no_activation", all_controls_no_activation, "False", "False", "activation_boundary"),
        ("EXECUTION_REVIEW_RULE_013", "all_controlled_start_not_approved", all_controlled_start_not_approved, "False", "False", "start_boundary"),
        ("EXECUTION_REVIEW_RULE_014", "all_start_disabled", all_start_disabled, "False", "False", "start_boundary"),
        ("EXECUTION_REVIEW_RULE_015", "all_official_dataset_writes_disabled", all_dataset_writes_disabled, "False", "False", "official_dataset_guard"),
        ("EXECUTION_REVIEW_RULE_016", "all_market_execution_disabled", all_market_execution_disabled, "False", "False", "market_execution_guard"),
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


def build_execution_review_guard_matrix(
    phase_10_13_summary_df: pd.DataFrame,
) -> pd.DataFrame:
    summary = (
        phase_10_13_summary_df.iloc[0].to_dict()
        if not phase_10_13_summary_df.empty
        else {}
    )

    rows: list[dict[str, Any]] = []

    for guard_name, required_value in EXPECTED_FALSE_GUARDS.items():
        actual_value = safe_bool(summary.get(guard_name, required_value), default=True)

        rows.append(
            {
                "guard_name": guard_name,
                "required_value": required_value,
                "actual_value": actual_value,
                "passed": actual_value == required_value,
                "guard_group": "report_only_dry_run_execution_review_safety_guard",
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


def build_execution_review_requirements(
    phase_10_13_summary_df: pd.DataFrame,
    report_only_dry_run_design_decision_df: pd.DataFrame,
    source_schema_df: pd.DataFrame,
    source_components_df: pd.DataFrame,
    source_controls_df: pd.DataFrame,
    items_df: pd.DataFrame,
    controls_df: pd.DataFrame,
    rules_df: pd.DataFrame,
    guard_matrix_df: pd.DataFrame,
) -> pd.DataFrame:
    summary = (
        phase_10_13_summary_df.iloc[0].to_dict()
        if not phase_10_13_summary_df.empty
        else {}
    )

    decision = (
        report_only_dry_run_design_decision_df.iloc[0].to_dict()
        if not report_only_dry_run_design_decision_df.empty
        else {}
    )

    schema_valid = (
        int(len(source_schema_df)) == 52
        and source_schema_df["required"].astype(bool).all()
    )
    components_valid = (
        int(len(source_components_df)) == 14
        and source_components_df["passed"].astype(bool).all()
    )
    source_controls_valid = (
        int(len(source_controls_df)) == 20
        and source_controls_df["passed"].astype(bool).all()
    )
    items_passed = not items_df.empty and items_df["passed"].astype(bool).all()
    controls_passed = not controls_df.empty and controls_df["passed"].astype(bool).all()
    rules_passed = not rules_df.empty and rules_df["passed"].astype(bool).all()
    guards_passed = not guard_matrix_df.empty and guard_matrix_df["passed"].astype(bool).all()

    requirements = [
        {
            "requirement_id": "EXECUTION_REVIEW_REQ_001",
            "requirement_name": "phase_10_13_validation_passed",
            "passed": safe_bool(summary.get("validation_passed", False)),
            "required_value": "True",
            "actual_value": str(summary.get("validation_passed", "")),
            "requirement_group": "dependency",
        },
        {
            "requirement_id": "EXECUTION_REVIEW_REQ_002",
            "requirement_name": "report_only_dry_run_design_passed",
            "passed": safe_bool(
                summary.get(
                    "controlled_start_activation_report_only_dry_run_design_passed",
                    False,
                )
            ),
            "required_value": "True",
            "actual_value": str(
                summary.get(
                    "controlled_start_activation_report_only_dry_run_design_passed",
                    "",
                )
            ),
            "requirement_group": "design",
        },
        {
            "requirement_id": "EXECUTION_REVIEW_REQ_003",
            "requirement_name": "report_only_dry_run_design_decision_expected",
            "passed": str(
                summary.get(
                    "controlled_start_activation_report_only_dry_run_design_decision",
                    "",
                )
            ).strip()
            == REPORT_ONLY_DRY_RUN_DESIGN_READY_DECISION,
            "required_value": REPORT_ONLY_DRY_RUN_DESIGN_READY_DECISION,
            "actual_value": str(
                summary.get(
                    "controlled_start_activation_report_only_dry_run_design_decision",
                    "",
                )
            ),
            "requirement_group": "design",
        },
        {
            "requirement_id": "EXECUTION_REVIEW_REQ_004",
            "requirement_name": "future_execution_review_allowed",
            "passed": safe_bool(
                summary.get(
                    "future_controlled_start_activation_report_only_dry_run_execution_review_allowed",
                    False,
                )
            ),
            "required_value": "True",
            "actual_value": str(
                summary.get(
                    "future_controlled_start_activation_report_only_dry_run_execution_review_allowed",
                    "",
                )
            ),
            "requirement_group": "future_review",
        },
        {
            "requirement_id": "EXECUTION_REVIEW_REQ_005",
            "requirement_name": "design_decision_table_consistent",
            "passed": (
                not report_only_dry_run_design_decision_df.empty
                and safe_bool(
                    decision.get(
                        "controlled_start_activation_report_only_dry_run_design_passed",
                        False,
                    )
                )
                and str(
                    decision.get(
                        "controlled_start_activation_report_only_dry_run_design_decision",
                        "",
                    )
                ).strip()
                == REPORT_ONLY_DRY_RUN_DESIGN_READY_DECISION
            ),
            "required_value": "True",
            "actual_value": str(
                decision.get(
                    "controlled_start_activation_report_only_dry_run_design_decision",
                    "",
                )
            ),
            "requirement_group": "summary_consistency",
        },
        {
            "requirement_id": "EXECUTION_REVIEW_REQ_006",
            "requirement_name": "source_schema_valid",
            "passed": schema_valid,
            "required_value": "True",
            "actual_value": str(schema_valid),
            "requirement_group": "schema",
        },
        {
            "requirement_id": "EXECUTION_REVIEW_REQ_007",
            "requirement_name": "source_components_valid",
            "passed": components_valid,
            "required_value": "True",
            "actual_value": str(components_valid),
            "requirement_group": "components",
        },
        {
            "requirement_id": "EXECUTION_REVIEW_REQ_008",
            "requirement_name": "source_controls_valid",
            "passed": source_controls_valid,
            "required_value": "True",
            "actual_value": str(source_controls_valid),
            "requirement_group": "controls",
        },
        {
            "requirement_id": "EXECUTION_REVIEW_REQ_009",
            "requirement_name": "execution_review_items_passed",
            "passed": items_passed,
            "required_value": "True",
            "actual_value": str(items_passed),
            "requirement_group": "items",
        },
        {
            "requirement_id": "EXECUTION_REVIEW_REQ_010",
            "requirement_name": "execution_review_controls_passed",
            "passed": controls_passed,
            "required_value": "True",
            "actual_value": str(controls_passed),
            "requirement_group": "controls",
        },
        {
            "requirement_id": "EXECUTION_REVIEW_REQ_011",
            "requirement_name": "execution_review_rules_passed",
            "passed": rules_passed,
            "required_value": "True",
            "actual_value": str(rules_passed),
            "requirement_group": "rules",
        },
        {
            "requirement_id": "EXECUTION_REVIEW_REQ_012",
            "requirement_name": "execution_review_guards_passed",
            "passed": guards_passed,
            "required_value": "True",
            "actual_value": str(guards_passed),
            "requirement_group": "safety",
        },
        {
            "requirement_id": "EXECUTION_REVIEW_REQ_013",
            "requirement_name": "dry_run_execution_not_allowed_yet",
            "passed": safe_bool(
                summary.get(
                    "controlled_start_activation_report_only_dry_run_execution_allowed",
                    True,
                ),
                default=True,
            )
            is False,
            "required_value": "False",
            "actual_value": str(
                summary.get(
                    "controlled_start_activation_report_only_dry_run_execution_allowed",
                    "",
                )
            ),
            "requirement_group": "dry_run_boundary",
        },
        {
            "requirement_id": "EXECUTION_REVIEW_REQ_014",
            "requirement_name": "dry_run_execution_not_performed",
            "passed": safe_bool(
                summary.get(
                    "controlled_start_activation_report_only_dry_run_execution_performed",
                    True,
                ),
                default=True,
            )
            is False,
            "required_value": "False",
            "actual_value": str(
                summary.get(
                    "controlled_start_activation_report_only_dry_run_execution_performed",
                    "",
                )
            ),
            "requirement_group": "dry_run_boundary",
        },
        {
            "requirement_id": "EXECUTION_REVIEW_REQ_015",
            "requirement_name": "activation_not_performed",
            "passed": safe_bool(
                summary.get(
                    "controlled_forward_observation_start_activation_performed",
                    True,
                ),
                default=True,
            )
            is False,
            "required_value": "False",
            "actual_value": str(
                summary.get(
                    "controlled_forward_observation_start_activation_performed",
                    "",
                )
            ),
            "requirement_group": "activation_boundary",
        },
        {
            "requirement_id": "EXECUTION_REVIEW_REQ_016",
            "requirement_name": "forward_observation_start_not_allowed",
            "passed": safe_bool(
                summary.get("forward_observation_start_allowed", True),
                default=True,
            )
            is False,
            "required_value": "False",
            "actual_value": str(summary.get("forward_observation_start_allowed", "")),
            "requirement_group": "start_boundary",
        },
        {
            "requirement_id": "EXECUTION_REVIEW_REQ_017",
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
            "requirement_id": "EXECUTION_REVIEW_REQ_018",
            "requirement_name": "official_evidence_rows_written_zero",
            "passed": int(summary.get("official_evidence_rows_written", -1)) == 0,
            "required_value": "0",
            "actual_value": str(summary.get("official_evidence_rows_written", "")),
            "requirement_group": "official_dataset_guard",
        },
        {
            "requirement_id": "EXECUTION_REVIEW_REQ_019",
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
            "requirement_id": "EXECUTION_REVIEW_REQ_020",
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


def build_execution_review_boundary_matrix() -> pd.DataFrame:
    rows = [
        {
            "boundary_item": "controlled_start_activation_report_only_dry_run_execution_review_allowed",
            "allowed": True,
            "boundary_type": "review_scope",
            "details": "Phase 10.14 may review readiness for a controlled report-only dry-run run.",
        },
        {
            "boundary_item": "future_controlled_start_activation_report_only_dry_run_run_allowed",
            "allowed": True,
            "boundary_type": "future_run",
            "details": "Phase 10.14 may recommend a future controlled report-only dry-run run phase.",
        },
        {
            "boundary_item": "controlled_start_activation_report_only_dry_run_execution_allowed",
            "allowed": False,
            "boundary_type": "dry_run_boundary",
            "details": "Report-only dry-run execution remains disabled in this review phase.",
        },
        {
            "boundary_item": "controlled_start_activation_report_only_dry_run_execution_performed",
            "allowed": False,
            "boundary_type": "dry_run_boundary",
            "details": "Report-only dry-run execution is not performed in this phase.",
        },
        {
            "boundary_item": "controlled_forward_observation_start_dry_run_performed",
            "allowed": False,
            "boundary_type": "dry_run_boundary",
            "details": "Controlled start dry-run is not performed in this phase.",
        },
        {
            "boundary_item": "controlled_forward_observation_start_activation_performed",
            "allowed": False,
            "boundary_type": "activation_boundary",
            "details": "Controlled start activation is not performed in this phase.",
        },
        {
            "boundary_item": "controlled_forward_observation_start_approved",
            "allowed": False,
            "boundary_type": "operational_start",
            "details": "Controlled forward observation start remains unapproved.",
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
            "boundary_item": "signal_generation_allowed",
            "allowed": False,
            "boundary_type": "signals",
            "details": "Signal generation remains disabled.",
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


def build_execution_review_decision_table(
    requirements_df: pd.DataFrame,
    boundary_matrix_df: pd.DataFrame,
    guard_matrix_df: pd.DataFrame,
    rules_df: pd.DataFrame,
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

    allowed_review_items = {
        "controlled_start_activation_report_only_dry_run_execution_review_allowed",
        "future_controlled_start_activation_report_only_dry_run_run_allowed",
    }

    disallowed_rows = boundary_matrix_df[
        ~boundary_matrix_df["boundary_item"].astype(str).isin(allowed_review_items)
    ]

    disallowed_operational_boundaries_passed = (
        not disallowed_rows.empty
        and disallowed_rows["allowed"].astype(bool).eq(False).all()
    )

    execution_review_passed = (
        total_requirements > 0
        and failed_requirements == 0
        and rules_passed
        and guards_passed
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
                "controlled_start_activation_report_only_dry_run_execution_review_id": (
                    "PHASE_10_14_LONG_FORWARD_OBSERVATION_CONTROLLED_START_ACTIVATION_REPORT_ONLY_DRY_RUN_EXECUTION_REVIEW_001"
                ),
                "controlled_start_activation_report_only_dry_run_execution_review_status": (
                    CONTROLLED_START_ACTIVATION_REPORT_ONLY_DRY_RUN_EXECUTION_REVIEW_STATUS
                ),
                "controlled_start_activation_report_only_dry_run_execution_review_passed": (
                    execution_review_passed
                ),
                "controlled_start_activation_report_only_dry_run_execution_review_decision": (
                    READY_DECISION if execution_review_passed else BLOCKED_DECISION
                ),
                "total_requirements": total_requirements,
                "passed_requirements": passed_requirements,
                "failed_requirements": failed_requirements,
                "failed_requirement_names": failed_requirement_names,
                "execution_review_rules_passed": rules_passed,
                "execution_review_guards_passed": guards_passed,
                "disallowed_operational_boundaries_passed": (
                    disallowed_operational_boundaries_passed
                ),
                "future_controlled_start_activation_report_only_dry_run_run_allowed": (
                    execution_review_passed
                ),
                "controlled_forward_observation_start_approved": False,
                "controlled_forward_observation_start_activation_performed": False,
                "controlled_forward_observation_start_dry_run_performed": False,
                "controlled_start_activation_report_only_dry_run_execution_allowed": False,
                "controlled_start_activation_report_only_dry_run_execution_performed": False,
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


def validate_long_forward_observation_controlled_start_activation_report_only_dry_run_execution_review() -> dict[str, pd.DataFrame]:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    checks: list[dict[str, Any]] = []

    phase_anchors = {
        "phase_10_13_controlled_start_activation_report_only_dry_run_design_doc_exists": (
            PHASE_10_13_CONTROLLED_START_ACTIVATION_REPORT_ONLY_DRY_RUN_DESIGN_DOC_PATH
        ),
        "phase_10_14_controlled_start_activation_report_only_dry_run_execution_review_doc_exists": (
            PHASE_10_14_CONTROLLED_START_ACTIVATION_REPORT_ONLY_DRY_RUN_EXECUTION_REVIEW_DOC_PATH
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

    phase_10_13_result = (
        validate_long_forward_observation_controlled_start_activation_report_only_dry_run_design()
    )

    phase_10_13_summary_df = phase_10_13_result["summary"]
    source_schema_df = phase_10_13_result["report_only_dry_run_design_schema"]
    source_components_df = phase_10_13_result["report_only_dry_run_design_components"]
    source_controls_df = phase_10_13_result["report_only_dry_run_design_controls"]
    source_rules_df = phase_10_13_result["report_only_dry_run_design_rules"]
    source_requirements_df = phase_10_13_result["report_only_dry_run_design_requirements"]
    source_guard_matrix_df = phase_10_13_result["report_only_dry_run_design_guard_matrix"]
    source_boundary_matrix_df = phase_10_13_result["report_only_dry_run_design_boundary_matrix"]
    source_decision_df = phase_10_13_result["report_only_dry_run_design_decision"]
    source_checks_df = phase_10_13_result["checks"]

    phase_10_13_summary = (
        phase_10_13_summary_df.iloc[0].to_dict()
        if not phase_10_13_summary_df.empty
        else {}
    )

    phase_10_13_validation_passed = (
        not phase_10_13_summary_df.empty
        and safe_bool(phase_10_13_summary.get("validation_passed", False))
    )

    report_only_design_passed = safe_bool(
        phase_10_13_summary.get(
            "controlled_start_activation_report_only_dry_run_design_passed",
            False,
        )
    )

    items_df = build_execution_review_items()
    controls_df = build_execution_review_controls()
    rules_df = build_execution_review_rules(
        items_df=items_df,
        controls_df=controls_df,
    )
    guard_matrix_df = build_execution_review_guard_matrix(phase_10_13_summary_df)

    requirements_df = build_execution_review_requirements(
        phase_10_13_summary_df=phase_10_13_summary_df,
        report_only_dry_run_design_decision_df=source_decision_df,
        source_schema_df=source_schema_df,
        source_components_df=source_components_df,
        source_controls_df=source_controls_df,
        items_df=items_df,
        controls_df=controls_df,
        rules_df=rules_df,
        guard_matrix_df=guard_matrix_df,
    )

    boundary_matrix_df = build_execution_review_boundary_matrix()

    decision_df = build_execution_review_decision_table(
        requirements_df=requirements_df,
        boundary_matrix_df=boundary_matrix_df,
        guard_matrix_df=guard_matrix_df,
        rules_df=rules_df,
    )

    official_dataset_exists_after = OFFICIAL_DATASET_PATH.exists()

    decision = decision_df.iloc[0].to_dict() if not decision_df.empty else {}

    execution_review_passed = safe_bool(
        decision.get(
            "controlled_start_activation_report_only_dry_run_execution_review_passed",
            False,
        )
    )
    execution_review_decision = str(
        decision.get(
            "controlled_start_activation_report_only_dry_run_execution_review_decision",
            "",
        )
    )
    future_controlled_run_allowed = safe_bool(
        decision.get(
            "future_controlled_start_activation_report_only_dry_run_run_allowed",
            False,
        )
    )

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
            check_name="phase_10_13_validation_passed",
            passed=phase_10_13_validation_passed,
            severity="INFO" if phase_10_13_validation_passed else "ERROR",
            details=str(phase_10_13_summary.get("validation_decision", "")),
        )
    )

    checks.append(
        build_check(
            check_group="phase_dependency",
            check_name="report_only_dry_run_design_passed",
            passed=report_only_design_passed,
            severity="INFO" if report_only_design_passed else "ERROR",
            details=f"report_only_dry_run_design_passed={report_only_design_passed}",
        )
    )

    checks.append(
        build_check(
            check_group="execution_review",
            check_name="source_schema_field_count_52",
            passed=int(len(source_schema_df)) == 52,
            severity="INFO" if int(len(source_schema_df)) == 52 else "ERROR",
            details=f"source_schema_field_count={len(source_schema_df)}",
        )
    )

    checks.append(
        build_check(
            check_group="execution_review",
            check_name="source_component_count_14",
            passed=int(len(source_components_df)) == 14,
            severity="INFO" if int(len(source_components_df)) == 14 else "ERROR",
            details=f"source_component_count={len(source_components_df)}",
        )
    )

    checks.append(
        build_check(
            check_group="execution_review",
            check_name="source_control_count_20",
            passed=int(len(source_controls_df)) == 20,
            severity="INFO" if int(len(source_controls_df)) == 20 else "ERROR",
            details=f"source_control_count={len(source_controls_df)}",
        )
    )

    checks.append(
        build_check(
            check_group="execution_review",
            check_name="execution_review_items_count_15",
            passed=int(len(items_df)) == 15,
            severity="INFO" if int(len(items_df)) == 15 else "ERROR",
            details=f"execution_review_item_count={len(items_df)}",
        )
    )

    checks.append(
        build_check(
            check_group="execution_review",
            check_name="execution_review_control_count_21",
            passed=int(len(controls_df)) == 21,
            severity="INFO" if int(len(controls_df)) == 21 else "ERROR",
            details=f"execution_review_control_count={len(controls_df)}",
        )
    )

    checks.append(
        build_check(
            check_group="execution_review",
            check_name="execution_review_rules_passed",
            passed=rules_passed,
            severity="INFO" if rules_passed else "ERROR",
            details=(
                "failed_rules="
                + ",".join(
                    rules_df[~rules_df["passed"].astype(bool)]["rule_name"].astype(str)
                )
                if not rules_df.empty
                else "failed_rules=all"
            ),
        )
    )

    checks.append(
        build_check(
            check_group="execution_review",
            check_name="execution_review_requirements_passed",
            passed=requirements_passed,
            severity="INFO" if requirements_passed else "ERROR",
            details=(
                "failed_requirements="
                + ",".join(
                    requirements_df[~requirements_df["passed"].astype(bool)][
                        "requirement_name"
                    ].astype(str)
                )
                if not requirements_df.empty
                else "failed_requirements=all"
            ),
        )
    )

    checks.append(
        build_check(
            check_group="execution_review",
            check_name="execution_review_guards_passed",
            passed=guards_passed,
            severity="INFO" if guards_passed else "ERROR",
            details=(
                "failed_guards="
                + ",".join(
                    guard_matrix_df[~guard_matrix_df["passed"].astype(bool)][
                        "guard_name"
                    ].astype(str)
                )
                if not guard_matrix_df.empty
                else "failed_guards=all"
            ),
        )
    )

    checks.append(
        build_check(
            check_group="execution_review",
            check_name="controlled_start_activation_report_only_dry_run_execution_review_passed",
            passed=execution_review_passed,
            severity="INFO" if execution_review_passed else "ERROR",
            details=(
                "controlled_start_activation_report_only_dry_run_execution_review_passed="
                f"{execution_review_passed}"
            ),
        )
    )

    checks.append(
        build_check(
            check_group="execution_review",
            check_name="controlled_start_activation_report_only_dry_run_execution_review_decision_expected",
            passed=execution_review_decision == READY_DECISION,
            severity="INFO" if execution_review_decision == READY_DECISION else "ERROR",
            details=(
                "controlled_start_activation_report_only_dry_run_execution_review_decision="
                f"{execution_review_decision}"
            ),
        )
    )

    checks.append(
        build_check(
            check_group="planning_scope",
            check_name="future_controlled_report_only_dry_run_run_allowed",
            passed=future_controlled_run_allowed,
            severity="WARNING" if future_controlled_run_allowed else "ERROR",
            details=(
                "This allows only a future controlled report-only dry-run run phase, "
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

    for _, guard_row in guard_matrix_df.iterrows():
        checks.append(
            build_check(
                check_group="execution_review_safety_flags",
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
            check_name="report_only_dry_run_execution_review_only",
            passed=True,
            severity="WARNING",
            details="Phase 10.14 validates only report-only dry-run execution review.",
        )
    )

    checks.append(
        build_check(
            check_group="scope_control",
            check_name="report_only_dry_run_execution_not_performed",
            passed=True,
            severity="WARNING",
            details="Report-only dry-run execution is still not performed.",
        )
    )

    checks.append(
        build_check(
            check_group="scope_control",
            check_name="controlled_start_activation_not_performed",
            passed=True,
            severity="WARNING",
            details="Controlled start activation is still not performed.",
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
            check_name="phase_10_15_recommended_next",
            passed=True,
            severity="INFO",
            details=(
                "Recommended next step: Phase 10.15 LONG Forward Observation "
                "Controlled Start Activation Report-Only Dry-Run Run V1."
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
                "phase": "10.14",
                "long_forward_observation_controlled_start_activation_report_only_dry_run_execution_review_defined": True,
                "phase_10_13_validation_passed": phase_10_13_validation_passed,
                "controlled_start_activation_report_only_dry_run_design_passed": report_only_design_passed,
                "controlled_start_activation_report_only_dry_run_design_decision": str(
                    phase_10_13_summary.get(
                        "controlled_start_activation_report_only_dry_run_design_decision",
                        "",
                    )
                ),
                "future_controlled_start_activation_report_only_dry_run_execution_review_allowed": safe_bool(
                    phase_10_13_summary.get(
                        "future_controlled_start_activation_report_only_dry_run_execution_review_allowed",
                        False,
                    )
                ),
                "source_report_only_dry_run_design_schema_field_count": int(len(source_schema_df)),
                "source_report_only_dry_run_design_component_count": int(len(source_components_df)),
                "source_report_only_dry_run_design_control_count": int(len(source_controls_df)),
                "execution_review_item_count": int(len(items_df)),
                "execution_review_control_count": int(len(controls_df)),
                "execution_review_rule_rows": int(len(rules_df)),
                "execution_review_requirement_rows": int(len(requirements_df)),
                "execution_review_rules_passed": rules_passed,
                "execution_review_requirements_passed": requirements_passed,
                "execution_review_guards_passed": guards_passed,
                "controlled_start_activation_report_only_dry_run_execution_review_passed": (
                    execution_review_passed
                ),
                "controlled_start_activation_report_only_dry_run_execution_review_decision": (
                    execution_review_decision
                ),
                "future_controlled_start_activation_report_only_dry_run_run_allowed": (
                    future_controlled_run_allowed
                ),
                "controlled_forward_observation_start_approved": False,
                "controlled_forward_observation_start_activation_performed": False,
                "controlled_forward_observation_start_dry_run_performed": False,
                "controlled_start_activation_report_only_dry_run_execution_allowed": False,
                "controlled_start_activation_report_only_dry_run_execution_performed": False,
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
                    "PHASE_10_14_LONG_FORWARD_OBSERVATION_CONTROLLED_START_ACTIVATION_REPORT_ONLY_DRY_RUN_EXECUTION_REVIEW_VALIDATED"
                    if validation_passed
                    else "PHASE_10_14_LONG_FORWARD_OBSERVATION_CONTROLLED_START_ACTIVATION_REPORT_ONLY_DRY_RUN_EXECUTION_REVIEW_FAILED"
                ),
            }
        ]
    )

    phase_10_13_summary_df.to_csv(
        REPORTS_DIR / "phase_10_13_source_summary_v1.csv",
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
    items_df.to_csv(
        REPORTS_DIR / "long_forward_observation_controlled_start_activation_report_only_dry_run_execution_review_items_v1.csv",
        index=False,
    )
    controls_df.to_csv(
        REPORTS_DIR / "long_forward_observation_controlled_start_activation_report_only_dry_run_execution_review_controls_v1.csv",
        index=False,
    )
    rules_df.to_csv(
        REPORTS_DIR / "long_forward_observation_controlled_start_activation_report_only_dry_run_execution_review_rules_v1.csv",
        index=False,
    )
    requirements_df.to_csv(
        REPORTS_DIR / "long_forward_observation_controlled_start_activation_report_only_dry_run_execution_review_requirements_v1.csv",
        index=False,
    )
    guard_matrix_df.to_csv(
        REPORTS_DIR / "long_forward_observation_controlled_start_activation_report_only_dry_run_execution_review_guard_matrix_v1.csv",
        index=False,
    )
    boundary_matrix_df.to_csv(
        REPORTS_DIR / "long_forward_observation_controlled_start_activation_report_only_dry_run_execution_review_boundary_matrix_v1.csv",
        index=False,
    )
    decision_df.to_csv(
        REPORTS_DIR / "long_forward_observation_controlled_start_activation_report_only_dry_run_execution_review_decision_v1.csv",
        index=False,
    )
    checks_df.to_csv(
        REPORTS_DIR / "long_forward_observation_controlled_start_activation_report_only_dry_run_execution_review_checks_v1.csv",
        index=False,
    )
    summary_df.to_csv(
        REPORTS_DIR / "long_forward_observation_controlled_start_activation_report_only_dry_run_execution_review_summary_v1.csv",
        index=False,
    )

    return {
        "summary": summary_df,
        "source_phase_10_13_summary": phase_10_13_summary_df,
        "source_report_only_dry_run_design_schema": source_schema_df,
        "source_report_only_dry_run_design_components": source_components_df,
        "source_report_only_dry_run_design_controls": source_controls_df,
        "source_report_only_dry_run_design_rules": source_rules_df,
        "source_report_only_dry_run_design_requirements": source_requirements_df,
        "source_report_only_dry_run_design_guard_matrix": source_guard_matrix_df,
        "source_report_only_dry_run_design_boundary_matrix": source_boundary_matrix_df,
        "source_report_only_dry_run_design_decision": source_decision_df,
        "source_checks": source_checks_df,
        "execution_review_items": items_df,
        "execution_review_controls": controls_df,
        "execution_review_rules": rules_df,
        "execution_review_requirements": requirements_df,
        "execution_review_guard_matrix": guard_matrix_df,
        "execution_review_boundary_matrix": boundary_matrix_df,
        "execution_review_decision": decision_df,
        "checks": checks_df,
    }
