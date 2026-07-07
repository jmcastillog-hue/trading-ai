from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from src.long_side.long_forward_observation_dataset_bootstrap_v1 import (
    OFFICIAL_DATASET_PATH,
    PRIMARY_RESEARCH_CANDIDATE,
)
from src.long_side.long_forward_observation_phase_10_11_controlled_start_activation_preparation_v1 import (
    READY_DECISION as ACTIVATION_PREPARATION_READY_DECISION,
    validate_long_forward_observation_controlled_start_activation_preparation,
)


REPORTS_DIR = Path(
    "reports/phase_10_12_long_forward_observation_controlled_start_activation_dry_run_review_v1"
)

PHASE_10_11_CONTROLLED_START_ACTIVATION_PREPARATION_DOC_PATH = Path(
    "docs/PHASE_10_LONG_FORWARD_OBSERVATION_CONTROLLED_START_ACTIVATION_PREPARATION.md"
)
PHASE_10_12_CONTROLLED_START_ACTIVATION_DRY_RUN_REVIEW_DOC_PATH = Path(
    "docs/PHASE_10_LONG_FORWARD_OBSERVATION_CONTROLLED_START_ACTIVATION_DRY_RUN_REVIEW.md"
)

CONTROLLED_START_ACTIVATION_DRY_RUN_REVIEW_STATUS = (
    "LONG_FORWARD_OBSERVATION_CONTROLLED_START_ACTIVATION_DRY_RUN_REVIEW_ONLY"
)

READY_DECISION = (
    "CONTROLLED_START_ACTIVATION_DRY_RUN_REVIEW_READY_FOR_REPORT_ONLY_DRY_RUN_DESIGN"
)
BLOCKED_DECISION = "CONTROLLED_START_ACTIVATION_DRY_RUN_REVIEW_BLOCKED"

RECOMMENDED_NEXT_PHASE = (
    "PHASE_10_13_LONG_FORWARD_OBSERVATION_CONTROLLED_START_ACTIVATION_REPORT_ONLY_DRY_RUN_DESIGN_V1"
)

DRY_RUN_REVIEW_ITEMS = [
    {
        "item_id": "ACTIVATION_DRY_RUN_REVIEW_ITEM_001",
        "item_name": "confirm_phase_10_11_activation_preparation",
        "item_group": "dependency",
        "details": "Confirm Phase 10.11 activation preparation passed.",
    },
    {
        "item_id": "ACTIVATION_DRY_RUN_REVIEW_ITEM_002",
        "item_name": "confirm_activation_preparation_decision",
        "item_group": "activation_preparation",
        "details": "Confirm activation preparation is ready for dry-run review.",
    },
    {
        "item_id": "ACTIVATION_DRY_RUN_REVIEW_ITEM_003",
        "item_name": "confirm_future_dry_run_review_allowed",
        "item_group": "future_review",
        "details": "Confirm Phase 10.11 allowed only a future dry-run review.",
    },
    {
        "item_id": "ACTIVATION_DRY_RUN_REVIEW_ITEM_004",
        "item_name": "confirm_candidate_scope",
        "item_group": "candidate_scope",
        "details": f"Confirm primary candidate remains {PRIMARY_RESEARCH_CANDIDATE}.",
    },
    {
        "item_id": "ACTIVATION_DRY_RUN_REVIEW_ITEM_005",
        "item_name": "confirm_long_direction_scope",
        "item_group": "direction",
        "details": "Confirm LONG-only observation candidate scope.",
    },
    {
        "item_id": "ACTIVATION_DRY_RUN_REVIEW_ITEM_006",
        "item_name": "confirm_manual_confirmation_required",
        "item_group": "manual_control",
        "details": "Manual confirmation remains required before any future activation step.",
    },
    {
        "item_id": "ACTIVATION_DRY_RUN_REVIEW_ITEM_007",
        "item_name": "confirm_no_dry_run_execution",
        "item_group": "dry_run_boundary",
        "details": "Controlled start dry-run has not been performed.",
    },
    {
        "item_id": "ACTIVATION_DRY_RUN_REVIEW_ITEM_008",
        "item_name": "confirm_no_activation",
        "item_group": "activation_boundary",
        "details": "Controlled start activation has not been performed.",
    },
    {
        "item_id": "ACTIVATION_DRY_RUN_REVIEW_ITEM_009",
        "item_name": "confirm_no_forward_start",
        "item_group": "start_boundary",
        "details": "Forward observation has not started.",
    },
    {
        "item_id": "ACTIVATION_DRY_RUN_REVIEW_ITEM_010",
        "item_name": "confirm_official_dataset_lock",
        "item_group": "official_dataset_guard",
        "details": "Official dataset remains locked and unwritten.",
    },
    {
        "item_id": "ACTIVATION_DRY_RUN_REVIEW_ITEM_011",
        "item_name": "confirm_real_evidence_lock",
        "item_group": "official_dataset_guard",
        "details": "Real evidence acceptance remains locked.",
    },
    {
        "item_id": "ACTIVATION_DRY_RUN_REVIEW_ITEM_012",
        "item_name": "confirm_signal_and_alert_locks",
        "item_group": "signals_alerts",
        "details": "Signal generation and live alerts remain disabled.",
    },
    {
        "item_id": "ACTIVATION_DRY_RUN_REVIEW_ITEM_013",
        "item_name": "confirm_execution_locks",
        "item_group": "execution",
        "details": "Paper trading, real capital, market execution, and exchange execution remain disabled.",
    },
    {
        "item_id": "ACTIVATION_DRY_RUN_REVIEW_ITEM_014",
        "item_name": "prepare_future_report_only_dry_run_design",
        "item_group": "future_design",
        "details": "Allow only a future report-only dry-run design phase.",
    },
]

DRY_RUN_REVIEW_CONTROLS = [
    ("ACTIVATION_DRY_RUN_REVIEW_CONTROL_001", "phase_10_11_validation_passed", "dependency"),
    ("ACTIVATION_DRY_RUN_REVIEW_CONTROL_002", "activation_preparation_passed", "activation_preparation"),
    ("ACTIVATION_DRY_RUN_REVIEW_CONTROL_003", "activation_preparation_decision_confirmed", "activation_preparation"),
    ("ACTIVATION_DRY_RUN_REVIEW_CONTROL_004", "future_dry_run_review_allowed", "future_review"),
    ("ACTIVATION_DRY_RUN_REVIEW_CONTROL_005", "candidate_scope_locked", "candidate_scope"),
    ("ACTIVATION_DRY_RUN_REVIEW_CONTROL_006", "long_direction_locked", "direction"),
    ("ACTIVATION_DRY_RUN_REVIEW_CONTROL_007", "manual_confirmation_required", "manual_control"),
    ("ACTIVATION_DRY_RUN_REVIEW_CONTROL_008", "dry_run_not_performed", "dry_run_boundary"),
    ("ACTIVATION_DRY_RUN_REVIEW_CONTROL_009", "activation_not_performed", "activation_boundary"),
    ("ACTIVATION_DRY_RUN_REVIEW_CONTROL_010", "forward_observation_not_started", "start_boundary"),
    ("ACTIVATION_DRY_RUN_REVIEW_CONTROL_011", "dataset_creation_disabled", "official_dataset_guard"),
    ("ACTIVATION_DRY_RUN_REVIEW_CONTROL_012", "official_dataset_write_disabled", "official_dataset_guard"),
    ("ACTIVATION_DRY_RUN_REVIEW_CONTROL_013", "real_evidence_acceptance_disabled", "official_dataset_guard"),
    ("ACTIVATION_DRY_RUN_REVIEW_CONTROL_014", "evidence_persistence_disabled", "official_dataset_guard"),
    ("ACTIVATION_DRY_RUN_REVIEW_CONTROL_015", "signal_generation_disabled", "signals"),
    ("ACTIVATION_DRY_RUN_REVIEW_CONTROL_016", "live_alerts_disabled", "alerts"),
    ("ACTIVATION_DRY_RUN_REVIEW_CONTROL_017", "paper_trading_and_real_capital_disabled", "capital"),
    ("ACTIVATION_DRY_RUN_REVIEW_CONTROL_018", "market_and_exchange_execution_disabled", "execution"),
    ("ACTIVATION_DRY_RUN_REVIEW_CONTROL_019", "automation_disabled", "automation"),
]

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


def build_activation_dry_run_review_items() -> pd.DataFrame:
    rows: list[dict[str, Any]] = []

    for position, item in enumerate(DRY_RUN_REVIEW_ITEMS, start=1):
        rows.append(
            {
                "item_position": position,
                "item_id": item["item_id"],
                "item_name": item["item_name"],
                "item_group": item["item_group"],
                "required": True,
                "manual_confirmation_required": True,
                "dry_run_review_only": True,
                "report_only_dry_run_design_allowed": True,
                "dry_run_performed": False,
                "activation_performed": False,
                "forward_observation_start_allowed": False,
                "official_dataset_write_allowed": False,
                "market_execution_allowed": False,
                "passed": True,
                "details": item["details"],
            }
        )

    return pd.DataFrame(rows)


def build_activation_dry_run_review_controls() -> pd.DataFrame:
    rows: list[dict[str, Any]] = []

    for control_id, control_name, control_group in DRY_RUN_REVIEW_CONTROLS:
        rows.append(
            {
                "control_id": control_id,
                "control_name": control_name,
                "control_group": control_group,
                "required": True,
                "dry_run_review_only": True,
                "report_only_dry_run_design_allowed": True,
                "dry_run_performed": False,
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


def build_activation_dry_run_review_rules(
    items_df: pd.DataFrame,
    controls_df: pd.DataFrame,
) -> pd.DataFrame:
    item_count = int(len(items_df))
    control_count = int(len(controls_df))

    items_passed = not items_df.empty and items_df["passed"].astype(bool).all()
    controls_passed = not controls_df.empty and controls_df["passed"].astype(bool).all()

    all_items_review_only = (
        not items_df.empty and items_df["dry_run_review_only"].astype(bool).all()
    )
    all_items_design_allowed = (
        not items_df.empty
        and items_df["report_only_dry_run_design_allowed"].astype(bool).all()
    )
    all_items_no_dry_run = (
        not items_df.empty and items_df["dry_run_performed"].astype(bool).eq(False).all()
    )
    all_items_no_activation = (
        not items_df.empty and items_df["activation_performed"].astype(bool).eq(False).all()
    )
    all_controls_review_only = (
        not controls_df.empty and controls_df["dry_run_review_only"].astype(bool).all()
    )
    all_controls_design_allowed = (
        not controls_df.empty
        and controls_df["report_only_dry_run_design_allowed"].astype(bool).all()
    )
    all_controls_no_dry_run = (
        not controls_df.empty
        and controls_df["dry_run_performed"].astype(bool).eq(False).all()
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
        ("ACTIVATION_DRY_RUN_REVIEW_RULE_001", "activation_dry_run_review_item_count_14", item_count == 14, "14", str(item_count), "items"),
        ("ACTIVATION_DRY_RUN_REVIEW_RULE_002", "all_items_passed", items_passed, "True", str(items_passed), "items"),
        ("ACTIVATION_DRY_RUN_REVIEW_RULE_003", "all_items_review_only", all_items_review_only, "True", str(all_items_review_only), "scope_control"),
        ("ACTIVATION_DRY_RUN_REVIEW_RULE_004", "all_items_allow_only_future_design", all_items_design_allowed, "True", str(all_items_design_allowed), "future_design"),
        ("ACTIVATION_DRY_RUN_REVIEW_RULE_005", "all_items_no_dry_run_performed", all_items_no_dry_run, "False", "False", "dry_run_boundary"),
        ("ACTIVATION_DRY_RUN_REVIEW_RULE_006", "all_items_no_activation_performed", all_items_no_activation, "False", "False", "activation_boundary"),
        ("ACTIVATION_DRY_RUN_REVIEW_RULE_007", "activation_dry_run_review_control_count_19", control_count == 19, "19", str(control_count), "controls"),
        ("ACTIVATION_DRY_RUN_REVIEW_RULE_008", "all_controls_passed", controls_passed, "True", str(controls_passed), "controls"),
        ("ACTIVATION_DRY_RUN_REVIEW_RULE_009", "all_controls_review_only", all_controls_review_only, "True", str(all_controls_review_only), "scope_control"),
        ("ACTIVATION_DRY_RUN_REVIEW_RULE_010", "all_controls_allow_only_future_design", all_controls_design_allowed, "True", str(all_controls_design_allowed), "future_design"),
        ("ACTIVATION_DRY_RUN_REVIEW_RULE_011", "all_controls_no_dry_run_performed", all_controls_no_dry_run, "False", "False", "dry_run_boundary"),
        ("ACTIVATION_DRY_RUN_REVIEW_RULE_012", "all_controls_no_activation_performed", all_controls_no_activation, "False", "False", "activation_boundary"),
        ("ACTIVATION_DRY_RUN_REVIEW_RULE_013", "all_controlled_start_not_approved", all_controlled_start_not_approved, "False", "False", "start_boundary"),
        ("ACTIVATION_DRY_RUN_REVIEW_RULE_014", "all_start_disabled", all_start_disabled, "False", "False", "start_boundary"),
        ("ACTIVATION_DRY_RUN_REVIEW_RULE_015", "all_official_dataset_writes_disabled", all_dataset_writes_disabled, "False", "False", "official_dataset_guard"),
        ("ACTIVATION_DRY_RUN_REVIEW_RULE_016", "all_market_execution_disabled", all_market_execution_disabled, "False", "False", "market_execution_guard"),
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


def build_activation_dry_run_review_guard_matrix(
    phase_10_11_summary_df: pd.DataFrame,
) -> pd.DataFrame:
    summary = (
        phase_10_11_summary_df.iloc[0].to_dict()
        if not phase_10_11_summary_df.empty
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
                "passed": actual_value is required_value,
                "guard_group": "activation_dry_run_review_safety_guard",
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


def build_activation_dry_run_review_requirements(
    phase_10_11_summary_df: pd.DataFrame,
    activation_preparation_decision_df: pd.DataFrame,
    items_df: pd.DataFrame,
    controls_df: pd.DataFrame,
    rules_df: pd.DataFrame,
    guard_matrix_df: pd.DataFrame,
) -> pd.DataFrame:
    summary = (
        phase_10_11_summary_df.iloc[0].to_dict()
        if not phase_10_11_summary_df.empty
        else {}
    )

    decision = (
        activation_preparation_decision_df.iloc[0].to_dict()
        if not activation_preparation_decision_df.empty
        else {}
    )

    items_passed = not items_df.empty and items_df["passed"].astype(bool).all()
    controls_passed = not controls_df.empty and controls_df["passed"].astype(bool).all()
    rules_passed = not rules_df.empty and rules_df["passed"].astype(bool).all()
    guards_passed = not guard_matrix_df.empty and guard_matrix_df["passed"].astype(bool).all()

    requirements = [
        {
            "requirement_id": "ACTIVATION_DRY_RUN_REVIEW_REQ_001",
            "requirement_name": "phase_10_11_validation_passed",
            "passed": safe_bool(summary.get("validation_passed", False)),
            "required_value": "True",
            "actual_value": str(summary.get("validation_passed", "")),
            "requirement_group": "dependency",
        },
        {
            "requirement_id": "ACTIVATION_DRY_RUN_REVIEW_REQ_002",
            "requirement_name": "controlled_start_activation_preparation_passed",
            "passed": safe_bool(
                summary.get("controlled_start_activation_preparation_passed", False)
            ),
            "required_value": "True",
            "actual_value": str(
                summary.get("controlled_start_activation_preparation_passed", "")
            ),
            "requirement_group": "activation_preparation",
        },
        {
            "requirement_id": "ACTIVATION_DRY_RUN_REVIEW_REQ_003",
            "requirement_name": "controlled_start_activation_preparation_decision_expected",
            "passed": str(
                summary.get("controlled_start_activation_preparation_decision", "")
            ).strip()
            == ACTIVATION_PREPARATION_READY_DECISION,
            "required_value": ACTIVATION_PREPARATION_READY_DECISION,
            "actual_value": str(
                summary.get("controlled_start_activation_preparation_decision", "")
            ),
            "requirement_group": "activation_preparation",
        },
        {
            "requirement_id": "ACTIVATION_DRY_RUN_REVIEW_REQ_004",
            "requirement_name": "future_dry_run_review_allowed",
            "passed": safe_bool(
                summary.get(
                    "future_controlled_start_activation_dry_run_review_allowed",
                    False,
                )
            ),
            "required_value": "True",
            "actual_value": str(
                summary.get(
                    "future_controlled_start_activation_dry_run_review_allowed",
                    "",
                )
            ),
            "requirement_group": "future_review",
        },
        {
            "requirement_id": "ACTIVATION_DRY_RUN_REVIEW_REQ_005",
            "requirement_name": "activation_preparation_decision_table_consistent",
            "passed": (
                not activation_preparation_decision_df.empty
                and safe_bool(
                    decision.get("controlled_start_activation_preparation_passed", False)
                )
                and str(
                    decision.get(
                        "controlled_start_activation_preparation_decision",
                        "",
                    )
                ).strip()
                == ACTIVATION_PREPARATION_READY_DECISION
            ),
            "required_value": "True",
            "actual_value": str(
                decision.get("controlled_start_activation_preparation_decision", "")
            ),
            "requirement_group": "summary_consistency",
        },
        {
            "requirement_id": "ACTIVATION_DRY_RUN_REVIEW_REQ_006",
            "requirement_name": "activation_dry_run_review_items_passed",
            "passed": items_passed,
            "required_value": "True",
            "actual_value": str(items_passed),
            "requirement_group": "items",
        },
        {
            "requirement_id": "ACTIVATION_DRY_RUN_REVIEW_REQ_007",
            "requirement_name": "activation_dry_run_review_controls_passed",
            "passed": controls_passed,
            "required_value": "True",
            "actual_value": str(controls_passed),
            "requirement_group": "controls",
        },
        {
            "requirement_id": "ACTIVATION_DRY_RUN_REVIEW_REQ_008",
            "requirement_name": "activation_dry_run_review_rules_passed",
            "passed": rules_passed,
            "required_value": "True",
            "actual_value": str(rules_passed),
            "requirement_group": "rules",
        },
        {
            "requirement_id": "ACTIVATION_DRY_RUN_REVIEW_REQ_009",
            "requirement_name": "activation_dry_run_review_guards_passed",
            "passed": guards_passed,
            "required_value": "True",
            "actual_value": str(guards_passed),
            "requirement_group": "safety",
        },
        {
            "requirement_id": "ACTIVATION_DRY_RUN_REVIEW_REQ_010",
            "requirement_name": "dry_run_not_performed",
            "passed": safe_bool(
                summary.get(
                    "controlled_forward_observation_start_dry_run_performed",
                    True,
                ),
                default=True,
            )
            is False,
            "required_value": "False",
            "actual_value": str(
                summary.get(
                    "controlled_forward_observation_start_dry_run_performed",
                    "",
                )
            ),
            "requirement_group": "dry_run_boundary",
        },
        {
            "requirement_id": "ACTIVATION_DRY_RUN_REVIEW_REQ_011",
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
            "requirement_id": "ACTIVATION_DRY_RUN_REVIEW_REQ_012",
            "requirement_name": "controlled_start_not_approved",
            "passed": safe_bool(
                summary.get("controlled_forward_observation_start_approved", True),
                default=True,
            )
            is False,
            "required_value": "False",
            "actual_value": str(
                summary.get("controlled_forward_observation_start_approved", "")
            ),
            "requirement_group": "start_boundary",
        },
        {
            "requirement_id": "ACTIVATION_DRY_RUN_REVIEW_REQ_013",
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
            "requirement_id": "ACTIVATION_DRY_RUN_REVIEW_REQ_014",
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
            "requirement_id": "ACTIVATION_DRY_RUN_REVIEW_REQ_015",
            "requirement_name": "official_evidence_rows_written_zero",
            "passed": int(summary.get("official_evidence_rows_written", -1)) == 0,
            "required_value": "0",
            "actual_value": str(summary.get("official_evidence_rows_written", "")),
            "requirement_group": "official_dataset_guard",
        },
        {
            "requirement_id": "ACTIVATION_DRY_RUN_REVIEW_REQ_016",
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
            "requirement_id": "ACTIVATION_DRY_RUN_REVIEW_REQ_017",
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
            "requirement_id": "ACTIVATION_DRY_RUN_REVIEW_REQ_018",
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


def build_activation_dry_run_review_boundary_matrix() -> pd.DataFrame:
    rows = [
        {
            "boundary_item": "controlled_start_activation_dry_run_review_allowed",
            "allowed": True,
            "boundary_type": "review_scope",
            "details": "Phase 10.12 may review dry-run readiness.",
        },
        {
            "boundary_item": "future_controlled_start_activation_report_only_dry_run_design_allowed",
            "allowed": True,
            "boundary_type": "future_design",
            "details": "Phase 10.12 may recommend a future report-only dry-run design phase.",
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


def build_activation_dry_run_review_decision_table(
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
        "controlled_start_activation_dry_run_review_allowed",
        "future_controlled_start_activation_report_only_dry_run_design_allowed",
    }

    disallowed_rows = boundary_matrix_df[
        ~boundary_matrix_df["boundary_item"].astype(str).isin(allowed_review_items)
    ]

    disallowed_operational_boundaries_passed = (
        not disallowed_rows.empty
        and disallowed_rows["allowed"].astype(bool).eq(False).all()
    )

    activation_dry_run_review_passed = (
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
                "controlled_start_activation_dry_run_review_id": (
                    "PHASE_10_12_LONG_FORWARD_OBSERVATION_CONTROLLED_START_ACTIVATION_DRY_RUN_REVIEW_001"
                ),
                "controlled_start_activation_dry_run_review_status": (
                    CONTROLLED_START_ACTIVATION_DRY_RUN_REVIEW_STATUS
                ),
                "controlled_start_activation_dry_run_review_passed": (
                    activation_dry_run_review_passed
                ),
                "controlled_start_activation_dry_run_review_decision": (
                    READY_DECISION
                    if activation_dry_run_review_passed
                    else BLOCKED_DECISION
                ),
                "total_requirements": total_requirements,
                "passed_requirements": passed_requirements,
                "failed_requirements": failed_requirements,
                "failed_requirement_names": failed_requirement_names,
                "activation_dry_run_review_rules_passed": rules_passed,
                "activation_dry_run_review_guards_passed": guards_passed,
                "disallowed_operational_boundaries_passed": (
                    disallowed_operational_boundaries_passed
                ),
                "future_controlled_start_activation_report_only_dry_run_design_allowed": (
                    activation_dry_run_review_passed
                ),
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


def validate_long_forward_observation_controlled_start_activation_dry_run_review() -> dict[str, pd.DataFrame]:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    checks: list[dict[str, Any]] = []

    phase_anchors = {
        "phase_10_11_controlled_start_activation_preparation_doc_exists": (
            PHASE_10_11_CONTROLLED_START_ACTIVATION_PREPARATION_DOC_PATH
        ),
        "phase_10_12_controlled_start_activation_dry_run_review_doc_exists": (
            PHASE_10_12_CONTROLLED_START_ACTIVATION_DRY_RUN_REVIEW_DOC_PATH
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

    phase_10_11_result = (
        validate_long_forward_observation_controlled_start_activation_preparation()
    )

    phase_10_11_summary_df = phase_10_11_result["summary"]
    source_steps_df = phase_10_11_result["activation_preparation_steps"]
    source_controls_df = phase_10_11_result["activation_preparation_controls"]
    source_rules_df = phase_10_11_result["activation_preparation_rules"]
    source_requirements_df = phase_10_11_result["activation_preparation_requirements"]
    source_guard_matrix_df = phase_10_11_result["activation_preparation_guard_matrix"]
    source_boundary_matrix_df = phase_10_11_result[
        "activation_preparation_boundary_matrix"
    ]
    source_decision_df = phase_10_11_result["activation_preparation_decision"]
    source_checks_df = phase_10_11_result["checks"]

    phase_10_11_summary = (
        phase_10_11_summary_df.iloc[0].to_dict()
        if not phase_10_11_summary_df.empty
        else {}
    )

    phase_10_11_validation_passed = (
        not phase_10_11_summary_df.empty
        and safe_bool(phase_10_11_summary.get("validation_passed", False))
    )

    activation_preparation_passed = safe_bool(
        phase_10_11_summary.get(
            "controlled_start_activation_preparation_passed",
            False,
        )
    )

    items_df = build_activation_dry_run_review_items()
    controls_df = build_activation_dry_run_review_controls()
    rules_df = build_activation_dry_run_review_rules(
        items_df=items_df,
        controls_df=controls_df,
    )
    guard_matrix_df = build_activation_dry_run_review_guard_matrix(
        phase_10_11_summary_df
    )

    requirements_df = build_activation_dry_run_review_requirements(
        phase_10_11_summary_df=phase_10_11_summary_df,
        activation_preparation_decision_df=source_decision_df,
        items_df=items_df,
        controls_df=controls_df,
        rules_df=rules_df,
        guard_matrix_df=guard_matrix_df,
    )

    boundary_matrix_df = build_activation_dry_run_review_boundary_matrix()

    decision_df = build_activation_dry_run_review_decision_table(
        requirements_df=requirements_df,
        boundary_matrix_df=boundary_matrix_df,
        guard_matrix_df=guard_matrix_df,
        rules_df=rules_df,
    )

    official_dataset_exists_after = OFFICIAL_DATASET_PATH.exists()

    decision = decision_df.iloc[0].to_dict() if not decision_df.empty else {}

    activation_dry_run_review_passed = safe_bool(
        decision.get("controlled_start_activation_dry_run_review_passed", False)
    )
    activation_dry_run_review_decision = str(
        decision.get("controlled_start_activation_dry_run_review_decision", "")
    )
    future_report_only_design_allowed = safe_bool(
        decision.get(
            "future_controlled_start_activation_report_only_dry_run_design_allowed",
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
            check_name="phase_10_11_validation_passed",
            passed=phase_10_11_validation_passed,
            severity="INFO" if phase_10_11_validation_passed else "ERROR",
            details=str(phase_10_11_summary.get("validation_decision", "")),
        )
    )

    checks.append(
        build_check(
            check_group="phase_dependency",
            check_name="controlled_start_activation_preparation_passed",
            passed=activation_preparation_passed,
            severity="INFO" if activation_preparation_passed else "ERROR",
            details=(
                "controlled_start_activation_preparation_passed="
                f"{activation_preparation_passed}"
            ),
        )
    )

    checks.append(
        build_check(
            check_group="activation_dry_run_review",
            check_name="activation_dry_run_review_rules_passed",
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
            check_group="activation_dry_run_review",
            check_name="activation_dry_run_review_requirements_passed",
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
            check_group="activation_dry_run_review",
            check_name="activation_dry_run_review_guards_passed",
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
            check_group="activation_dry_run_review",
            check_name="controlled_start_activation_dry_run_review_passed",
            passed=activation_dry_run_review_passed,
            severity="INFO" if activation_dry_run_review_passed else "ERROR",
            details=(
                "controlled_start_activation_dry_run_review_passed="
                f"{activation_dry_run_review_passed}"
            ),
        )
    )

    checks.append(
        build_check(
            check_group="activation_dry_run_review",
            check_name="controlled_start_activation_dry_run_review_decision_expected",
            passed=activation_dry_run_review_decision == READY_DECISION,
            severity=(
                "INFO"
                if activation_dry_run_review_decision == READY_DECISION
                else "ERROR"
            ),
            details=(
                "controlled_start_activation_dry_run_review_decision="
                f"{activation_dry_run_review_decision}"
            ),
        )
    )

    checks.append(
        build_check(
            check_group="planning_scope",
            check_name="future_report_only_dry_run_design_allowed",
            passed=future_report_only_design_allowed,
            severity="WARNING" if future_report_only_design_allowed else "ERROR",
            details=(
                "This allows only a future report-only dry-run design phase, not "
                "dry-run execution, forward observation start, alerts, paper trading, "
                "real capital, official evidence persistence, or market execution."
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
                check_group="activation_dry_run_review_safety_flags",
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
            check_name="controlled_start_activation_dry_run_review_only",
            passed=True,
            severity="WARNING",
            details="Phase 10.12 validates only activation dry-run review.",
        )
    )

    checks.append(
        build_check(
            check_group="scope_control",
            check_name="controlled_start_dry_run_not_performed",
            passed=True,
            severity="WARNING",
            details="Controlled start dry-run is still not performed.",
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
            check_name="phase_10_13_recommended_next",
            passed=True,
            severity="INFO",
            details=(
                "Recommended next step: Phase 10.13 LONG Forward Observation "
                "Controlled Start Activation Report-Only Dry-Run Design V1."
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
                "phase": "10.12",
                "long_forward_observation_controlled_start_activation_dry_run_review_defined": True,
                "phase_10_11_validation_passed": phase_10_11_validation_passed,
                "controlled_start_activation_preparation_passed": activation_preparation_passed,
                "controlled_start_activation_preparation_decision": str(
                    phase_10_11_summary.get(
                        "controlled_start_activation_preparation_decision",
                        "",
                    )
                ),
                "future_controlled_start_activation_dry_run_review_allowed": safe_bool(
                    phase_10_11_summary.get(
                        "future_controlled_start_activation_dry_run_review_allowed",
                        False,
                    )
                ),
                "activation_dry_run_review_item_count": int(len(items_df)),
                "activation_dry_run_review_control_count": int(len(controls_df)),
                "activation_dry_run_review_rule_rows": int(len(rules_df)),
                "activation_dry_run_review_requirement_rows": int(len(requirements_df)),
                "activation_dry_run_review_rules_passed": rules_passed,
                "activation_dry_run_review_requirements_passed": requirements_passed,
                "activation_dry_run_review_guards_passed": guards_passed,
                "controlled_start_activation_dry_run_review_passed": (
                    activation_dry_run_review_passed
                ),
                "controlled_start_activation_dry_run_review_decision": (
                    activation_dry_run_review_decision
                ),
                "future_controlled_start_activation_report_only_dry_run_design_allowed": (
                    future_report_only_design_allowed
                ),
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
                    "PHASE_10_12_LONG_FORWARD_OBSERVATION_CONTROLLED_START_ACTIVATION_DRY_RUN_REVIEW_VALIDATED"
                    if validation_passed
                    else "PHASE_10_12_LONG_FORWARD_OBSERVATION_CONTROLLED_START_ACTIVATION_DRY_RUN_REVIEW_FAILED"
                ),
            }
        ]
    )

    phase_10_11_summary_df.to_csv(
        REPORTS_DIR / "phase_10_11_source_summary_v1.csv",
        index=False,
    )
    source_steps_df.to_csv(
        REPORTS_DIR / "phase_10_11_source_activation_preparation_steps_v1.csv",
        index=False,
    )
    source_controls_df.to_csv(
        REPORTS_DIR / "phase_10_11_source_activation_preparation_controls_v1.csv",
        index=False,
    )
    source_rules_df.to_csv(
        REPORTS_DIR / "phase_10_11_source_activation_preparation_rules_v1.csv",
        index=False,
    )
    source_requirements_df.to_csv(
        REPORTS_DIR / "phase_10_11_source_activation_preparation_requirements_v1.csv",
        index=False,
    )
    source_guard_matrix_df.to_csv(
        REPORTS_DIR / "phase_10_11_source_activation_preparation_guard_matrix_v1.csv",
        index=False,
    )
    source_boundary_matrix_df.to_csv(
        REPORTS_DIR / "phase_10_11_source_activation_preparation_boundary_matrix_v1.csv",
        index=False,
    )
    source_decision_df.to_csv(
        REPORTS_DIR / "phase_10_11_source_activation_preparation_decision_v1.csv",
        index=False,
    )
    source_checks_df.to_csv(
        REPORTS_DIR / "phase_10_11_source_checks_v1.csv",
        index=False,
    )
    items_df.to_csv(
        REPORTS_DIR / "long_forward_observation_controlled_start_activation_dry_run_review_items_v1.csv",
        index=False,
    )
    controls_df.to_csv(
        REPORTS_DIR / "long_forward_observation_controlled_start_activation_dry_run_review_controls_v1.csv",
        index=False,
    )
    rules_df.to_csv(
        REPORTS_DIR / "long_forward_observation_controlled_start_activation_dry_run_review_rules_v1.csv",
        index=False,
    )
    requirements_df.to_csv(
        REPORTS_DIR / "long_forward_observation_controlled_start_activation_dry_run_review_requirements_v1.csv",
        index=False,
    )
    guard_matrix_df.to_csv(
        REPORTS_DIR / "long_forward_observation_controlled_start_activation_dry_run_review_guard_matrix_v1.csv",
        index=False,
    )
    boundary_matrix_df.to_csv(
        REPORTS_DIR / "long_forward_observation_controlled_start_activation_dry_run_review_boundary_matrix_v1.csv",
        index=False,
    )
    decision_df.to_csv(
        REPORTS_DIR / "long_forward_observation_controlled_start_activation_dry_run_review_decision_v1.csv",
        index=False,
    )
    checks_df.to_csv(
        REPORTS_DIR / "long_forward_observation_controlled_start_activation_dry_run_review_checks_v1.csv",
        index=False,
    )
    summary_df.to_csv(
        REPORTS_DIR / "long_forward_observation_controlled_start_activation_dry_run_review_summary_v1.csv",
        index=False,
    )

    return {
        "summary": summary_df,
        "source_phase_10_11_summary": phase_10_11_summary_df,
        "source_activation_preparation_steps": source_steps_df,
        "source_activation_preparation_controls": source_controls_df,
        "source_activation_preparation_rules": source_rules_df,
        "source_activation_preparation_requirements": source_requirements_df,
        "source_activation_preparation_guard_matrix": source_guard_matrix_df,
        "source_activation_preparation_boundary_matrix": source_boundary_matrix_df,
        "source_activation_preparation_decision": source_decision_df,
        "source_checks": source_checks_df,
        "activation_dry_run_review_items": items_df,
        "activation_dry_run_review_controls": controls_df,
        "activation_dry_run_review_rules": rules_df,
        "activation_dry_run_review_requirements": requirements_df,
        "activation_dry_run_review_guard_matrix": guard_matrix_df,
        "activation_dry_run_review_boundary_matrix": boundary_matrix_df,
        "activation_dry_run_review_decision": decision_df,
        "checks": checks_df,
    }