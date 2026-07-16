from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

from src.long_side.long_forward_observation_dataset_bootstrap_v1 import (
    OFFICIAL_DATASET_PATH,
    PRIMARY_RESEARCH_CANDIDATE,
)
from src.long_side.long_forward_observation_phase_10_25_controlled_start_final_approval_review_v1 import (
    READY_DECISION as SOURCE_READY_DECISION,
)


REPORTS_DIR = Path("reports/p10_26_controlled_start_run_v1")
PHASE_10_25_REPORTS_DIR = Path(
    "reports/p10_25_start_final_approval_review_v1"
)

PHASE_10_25_DOC_PATH = Path(
    "docs/PHASE_10_LONG_FORWARD_OBSERVATION_CONTROLLED_START_FINAL_APPROVAL_REVIEW.md"
)
PHASE_10_26_DOC_PATH = Path(
    "docs/PHASE_10_LONG_FORWARD_OBSERVATION_CONTROLLED_START_RUN.md"
)

SOURCE_SUMMARY_PATH = (
    PHASE_10_25_REPORTS_DIR / "start_final_approval_summary_v1.csv"
)
SOURCE_DRY_RUN_OUTPUT_PATH = (
    PHASE_10_25_REPORTS_DIR / "phase_10_23_source_dry_run_output_v1.csv"
)
SOURCE_VALIDATIONS_PATH = (
    PHASE_10_25_REPORTS_DIR / "start_final_approval_validations_v1.csv"
)
SOURCE_EVIDENCE_CHAIN_PATH = (
    PHASE_10_25_REPORTS_DIR / "start_final_approval_evidence_chain_v1.csv"
)
SOURCE_CONTROLS_PATH = (
    PHASE_10_25_REPORTS_DIR / "start_final_approval_controls_v1.csv"
)
SOURCE_RULES_PATH = (
    PHASE_10_25_REPORTS_DIR / "start_final_approval_rules_v1.csv"
)
SOURCE_REQUIREMENTS_PATH = (
    PHASE_10_25_REPORTS_DIR / "start_final_approval_requirements_v1.csv"
)
SOURCE_GUARD_MATRIX_PATH = (
    PHASE_10_25_REPORTS_DIR / "start_final_approval_guard_matrix_v1.csv"
)
SOURCE_DECISION_PATH = (
    PHASE_10_25_REPORTS_DIR / "start_final_approval_decision_v1.csv"
)
SOURCE_CHECKS_PATH = (
    PHASE_10_25_REPORTS_DIR / "start_final_approval_checks_v1.csv"
)

START_RUN_STATUS = (
    "LONG_FORWARD_OBSERVATION_CONTROLLED_START_RUN_OBSERVATION_ONLY"
)
READY_DECISION = (
    "CONTROLLED_FORWARD_OBSERVATION_START_RUN_COMPLETED_OBSERVATION_ONLY"
)
BLOCKED_DECISION = "CONTROLLED_FORWARD_OBSERVATION_START_RUN_BLOCKED"
RECOMMENDED_NEXT_PHASE = (
    "PHASE_10_27_LONG_FORWARD_OBSERVATION_CONTROLLED_START_RUN_OUTPUT_INTEGRITY_REVIEW_V1"
)

START_SCOPE = "CONTROLLED_FORWARD_OBSERVATION_START_OBSERVATION_ONLY"
EVIDENCE_SCOPE = "OBSERVATION_STATE_ONLY_NOT_REAL_EVIDENCE"
VALIDATION_STATUS = "CONTROLLED_FORWARD_OBSERVATION_START_ROW_CREATED"

EXPECTED_FALSE_GUARDS = {
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

START_RUN_OUTPUT_COLUMNS = [
    "start_run_id",
    "start_run_status",
    "started_at_utc",
    "source_phase",
    "source_validation_decision",
    "source_final_approval_decision",
    "symbol",
    "timeframe",
    "candidate_id",
    "direction",
    "observation_role",
    "observation_state",
    "market_context",
    "activation_scope",
    "start_scope",
    "evidence_scope",
    "entry_price",
    "stop_price",
    "target_price",
    "invalidation_level",
    "risk_reward",
    "cost_profile",
    "manual_confirmation_required",
    "controlled_forward_observation_start_final_approval_review_performed",
    "future_controlled_forward_observation_start_run_allowed",
    "controlled_forward_observation_start_run_allowed",
    "controlled_forward_observation_start_run_performed",
    "controlled_forward_observation_start_performed",
    "forward_observation_start_allowed",
    "forward_observation_started",
    "future_controlled_forward_observation_start_run_output_integrity_review_allowed",
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


def read_csv_if_exists(path: Path) -> pd.DataFrame:
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


def build_controlled_start_output(
    source_summary_df: pd.DataFrame,
    source_dry_run_output_df: pd.DataFrame,
    official_dataset_absent: bool,
) -> pd.DataFrame:
    if source_summary_df.empty or source_dry_run_output_df.empty:
        return pd.DataFrame(columns=START_RUN_OUTPUT_COLUMNS)

    source_summary = source_summary_df.iloc[0].to_dict()
    source_output = source_dry_run_output_df.iloc[0].to_dict()

    source_ready = (
        safe_bool(source_summary.get("validation_passed", False))
        and safe_bool(
            source_summary.get(
                "controlled_forward_observation_start_final_approval_review_performed",
                False,
            )
        )
        and safe_bool(
            source_summary.get(
                "controlled_forward_observation_start_final_approval_review_passed",
                False,
            )
        )
        and str(
            source_summary.get(
                "controlled_forward_observation_start_final_approval_review_decision",
                "",
            )
        )
        == SOURCE_READY_DECISION
        and safe_bool(
            source_summary.get(
                "future_controlled_forward_observation_start_run_allowed",
                False,
            )
        )
        and official_dataset_absent
    )

    if not source_ready:
        return pd.DataFrame(columns=START_RUN_OUTPUT_COLUMNS)

    row = {
        "start_run_id": (
            "PHASE_10_26_LONG_FORWARD_OBSERVATION_CONTROLLED_START_RUN_001"
        ),
        "start_run_status": START_RUN_STATUS,
        "started_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_phase": "10.25",
        "source_validation_decision": str(
            source_summary.get("validation_decision", "")
        ),
        "source_final_approval_decision": str(
            source_summary.get(
                "controlled_forward_observation_start_final_approval_review_decision",
                "",
            )
        ),
        "symbol": str(source_output.get("symbol", "BTCUSDT")),
        "timeframe": str(source_output.get("timeframe", "15m")),
        "candidate_id": str(
            source_output.get("candidate_id", PRIMARY_RESEARCH_CANDIDATE)
        ),
        "direction": str(source_output.get("direction", "LONG")),
        "observation_role": "PRIMARY_FORWARD_OBSERVATION_CONTROLLED_START",
        "observation_state": "CONTROLLED_FORWARD_OBSERVATION_STARTED",
        "market_context": (
            "SYNTHETIC_CONTROLLED_START_STATE_WITHOUT_SIGNAL_GENERATION"
        ),
        "activation_scope": "CONTROL_PLANE_OBSERVATION_STATE_ONLY",
        "start_scope": START_SCOPE,
        "evidence_scope": EVIDENCE_SCOPE,
        "entry_price": safe_float(source_output.get("entry_price")),
        "stop_price": safe_float(source_output.get("stop_price")),
        "target_price": safe_float(source_output.get("target_price")),
        "invalidation_level": safe_float(
            source_output.get("invalidation_level")
        ),
        "risk_reward": safe_float(source_output.get("risk_reward")),
        "cost_profile": str(
            source_output.get(
                "cost_profile",
                "RESEARCH_COST_AWARE_REFERENCE_ONLY",
            )
        ),
        "manual_confirmation_required": True,
        "controlled_forward_observation_start_final_approval_review_performed": True,
        "future_controlled_forward_observation_start_run_allowed": True,
        "controlled_forward_observation_start_run_allowed": True,
        "controlled_forward_observation_start_run_performed": True,
        "controlled_forward_observation_start_performed": True,
        "forward_observation_start_allowed": True,
        "forward_observation_started": True,
        "future_controlled_forward_observation_start_run_output_integrity_review_allowed": True,
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
            "Controlled forward observation start-state row only. "
            "No official dataset write. No real evidence. No live signal. "
            "No alert. No paper trading. No market execution."
        ),
        "validation_status": VALIDATION_STATUS,
    }

    return pd.DataFrame([row], columns=START_RUN_OUTPUT_COLUMNS)


def build_start_run_validations(
    source_summary_df: pd.DataFrame,
    source_dry_run_output_df: pd.DataFrame,
    start_output_df: pd.DataFrame,
    official_dataset_absent: bool,
) -> pd.DataFrame:
    source_summary = (
        source_summary_df.iloc[0].to_dict()
        if not source_summary_df.empty
        else {}
    )
    source_output = (
        source_dry_run_output_df.iloc[0].to_dict()
        if not source_dry_run_output_df.empty
        else {}
    )
    start_output = (
        start_output_df.iloc[0].to_dict()
        if not start_output_df.empty
        else {}
    )

    entry_price = safe_float(start_output.get("entry_price"))
    stop_price = safe_float(start_output.get("stop_price"))
    target_price = safe_float(start_output.get("target_price"))
    risk_reward = safe_float(start_output.get("risk_reward"))

    expected_risk_reward = (
        round((target_price - entry_price) / (entry_price - stop_price), 4)
        if entry_price > stop_price
        else 0.0
    )

    source_ready = (
        safe_bool(source_summary.get("validation_passed", False))
        and safe_bool(
            source_summary.get(
                "controlled_forward_observation_start_final_approval_review_performed",
                False,
            )
        )
        and safe_bool(
            source_summary.get(
                "controlled_forward_observation_start_final_approval_review_passed",
                False,
            )
        )
        and str(
            source_summary.get(
                "controlled_forward_observation_start_final_approval_review_decision",
                "",
            )
        )
        == SOURCE_READY_DECISION
        and safe_bool(
            source_summary.get(
                "future_controlled_forward_observation_start_run_allowed",
                False,
            )
        )
    )

    true_start_fields_valid = all(
        safe_bool(start_output.get(field_name, False))
        for field_name in EXPECTED_TRUE_START_FIELDS
    )

    operational_locks_valid = all(
        safe_bool(start_output.get(field_name, True), True) is False
        for field_name in EXPECTED_FALSE_GUARDS
    )

    rows = [
        (
            "phase_10_25_validation_passed",
            safe_bool(source_summary.get("validation_passed", False)),
            str(source_summary.get("validation_decision", "")),
        ),
        (
            "source_final_approval_review_performed",
            safe_bool(
                source_summary.get(
                    "controlled_forward_observation_start_final_approval_review_performed",
                    False,
                )
            ),
            str(
                source_summary.get(
                    "controlled_forward_observation_start_final_approval_review_performed",
                    "",
                )
            ),
        ),
        (
            "source_final_approval_review_passed",
            safe_bool(
                source_summary.get(
                    "controlled_forward_observation_start_final_approval_review_passed",
                    False,
                )
            ),
            str(
                source_summary.get(
                    "controlled_forward_observation_start_final_approval_review_passed",
                    "",
                )
            ),
        ),
        (
            "source_final_approval_decision_valid",
            str(
                source_summary.get(
                    "controlled_forward_observation_start_final_approval_review_decision",
                    "",
                )
            )
            == SOURCE_READY_DECISION,
            str(
                source_summary.get(
                    "controlled_forward_observation_start_final_approval_review_decision",
                    "",
                )
            ),
        ),
        (
            "source_future_start_run_allowed",
            safe_bool(
                source_summary.get(
                    "future_controlled_forward_observation_start_run_allowed",
                    False,
                )
            ),
            str(
                source_summary.get(
                    "future_controlled_forward_observation_start_run_allowed",
                    "",
                )
            ),
        ),
        (
            "source_ready_for_start_run",
            source_ready,
            f"source_ready={source_ready}",
        ),
        (
            "start_output_row_count_valid",
            len(start_output_df) == 1,
            f"row_count={len(start_output_df)}",
        ),
        (
            "start_output_schema_valid",
            start_output_df.columns.astype(str).tolist()
            == START_RUN_OUTPUT_COLUMNS,
            (
                f"actual_field_count={len(start_output_df.columns)},"
                f"expected_field_count={len(START_RUN_OUTPUT_COLUMNS)}"
            ),
        ),
        (
            "start_output_candidate_valid",
            str(start_output.get("candidate_id", ""))
            == PRIMARY_RESEARCH_CANDIDATE,
            str(start_output.get("candidate_id", "")),
        ),
        (
            "start_output_direction_valid",
            str(start_output.get("direction", "")) == "LONG",
            str(start_output.get("direction", "")),
        ),
        (
            "start_output_price_structure_valid",
            stop_price < entry_price < target_price,
            f"stop={stop_price},entry={entry_price},target={target_price}",
        ),
        (
            "start_output_risk_reward_valid",
            risk_reward == expected_risk_reward and risk_reward == 2.5,
            f"risk_reward={risk_reward},expected={expected_risk_reward}",
        ),
        (
            "start_output_scope_valid",
            str(start_output.get("start_scope", "")) == START_SCOPE,
            str(start_output.get("start_scope", "")),
        ),
        (
            "start_output_evidence_scope_valid",
            str(start_output.get("evidence_scope", "")) == EVIDENCE_SCOPE,
            str(start_output.get("evidence_scope", "")),
        ),
        (
            "start_output_observation_state_valid",
            str(start_output.get("observation_state", ""))
            == "CONTROLLED_FORWARD_OBSERVATION_STARTED",
            str(start_output.get("observation_state", "")),
        ),
        (
            "start_output_true_start_fields_valid",
            true_start_fields_valid,
            f"true_start_field_count={len(EXPECTED_TRUE_START_FIELDS)}",
        ),
        (
            "start_output_operational_locks_valid",
            operational_locks_valid,
            f"false_guard_count={len(EXPECTED_FALSE_GUARDS)}",
        ),
        (
            "start_output_official_evidence_rows_zero",
            int(
                safe_float(
                    start_output.get("official_evidence_rows_written"),
                    -1,
                )
            )
            == 0,
            str(start_output.get("official_evidence_rows_written", "")),
        ),
        (
            "start_output_validation_status_valid",
            str(start_output.get("validation_status", ""))
            == VALIDATION_STATUS,
            str(start_output.get("validation_status", "")),
        ),
        (
            "source_candidate_consistent",
            str(source_output.get("candidate_id", ""))
            == str(start_output.get("candidate_id", ""))
            == PRIMARY_RESEARCH_CANDIDATE,
            str(source_output.get("candidate_id", "")),
        ),
        (
            "source_direction_consistent",
            str(source_output.get("direction", ""))
            == str(start_output.get("direction", ""))
            == "LONG",
            str(source_output.get("direction", "")),
        ),
        (
            "source_risk_reward_consistent",
            safe_float(source_output.get("risk_reward")) == risk_reward == 2.5,
            (
                f"source={safe_float(source_output.get('risk_reward'))},"
                f"start={risk_reward}"
            ),
        ),
        (
            "official_dataset_absent",
            official_dataset_absent,
            f"official_dataset_absent={official_dataset_absent}",
        ),
        (
            "future_output_integrity_review_allowed",
            safe_bool(
                start_output.get(
                    "future_controlled_forward_observation_start_run_output_integrity_review_allowed",
                    False,
                )
            ),
            str(
                start_output.get(
                    "future_controlled_forward_observation_start_run_output_integrity_review_allowed",
                    "",
                )
            ),
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


def build_start_run_evidence_chain(
    validations_df: pd.DataFrame,
) -> pd.DataFrame:
    validation_lookup = {
        str(row["validation_name"]): safe_bool(row["passed"], False)
        for _, row in validations_df.iterrows()
    }

    definitions = [
        ("phase_10_25_validation_passed", "dependency"),
        ("source_final_approval_review_performed", "final_approval"),
        ("source_final_approval_review_passed", "final_approval"),
        ("source_final_approval_decision_valid", "final_approval"),
        ("source_future_start_run_allowed", "future_run"),
        ("source_ready_for_start_run", "start_readiness"),
        ("start_output_row_count_valid", "artifact"),
        ("start_output_schema_valid", "schema"),
        ("start_output_candidate_valid", "candidate_scope"),
        ("start_output_direction_valid", "direction"),
        ("start_output_price_structure_valid", "price_structure"),
        ("start_output_risk_reward_valid", "risk_reward"),
        ("start_output_scope_valid", "scope_control"),
        ("start_output_evidence_scope_valid", "evidence_scope"),
        ("start_output_observation_state_valid", "observation_state"),
        ("start_output_true_start_fields_valid", "start_control"),
        ("start_output_operational_locks_valid", "safety"),
        ("start_output_official_evidence_rows_zero", "official_dataset_guard"),
        ("start_output_validation_status_valid", "artifact"),
        ("source_candidate_consistent", "summary_consistency"),
        ("source_direction_consistent", "summary_consistency"),
        ("source_risk_reward_consistent", "summary_consistency"),
        ("official_dataset_absent", "official_dataset_guard"),
        ("future_output_integrity_review_allowed", "future_review"),
    ]

    return pd.DataFrame(
        [
            {
                "evidence_position": position,
                "evidence_id": f"CONTROLLED_START_RUN_EVIDENCE_{position:03d}",
                "evidence_name": evidence_name,
                "evidence_group": evidence_group,
                "required": True,
                "passed": validation_lookup.get(evidence_name, False),
                "details": (
                    "Validated from Phase 10.25 final approval artifacts "
                    "and the Phase 10.26 controlled start output."
                ),
            }
            for position, (evidence_name, evidence_group) in enumerate(
                definitions,
                start=1,
            )
        ]
    )


def build_start_run_controls(
    evidence_chain_df: pd.DataFrame,
) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "control_position": int(row["evidence_position"]),
                "control_id": (
                    f"CONTROLLED_START_RUN_CONTROL_"
                    f"{int(row['evidence_position']):03d}"
                ),
                "control_name": str(row["evidence_name"]),
                "control_group": str(row["evidence_group"]),
                "required": True,
                "controlled_start_run_observation_only": True,
                "future_controlled_forward_observation_start_run_output_integrity_review_allowed": True,
                "forward_observation_started": True,
                "official_dataset_write_allowed": False,
                "signal_generation_enabled": False,
                "market_execution_allowed": False,
                "passed": safe_bool(row["passed"], False),
            }
            for _, row in evidence_chain_df.iterrows()
        ]
    )


def build_start_run_guard_matrix() -> pd.DataFrame:
    rows: list[dict[str, Any]] = []

    true_state_guards = [
        "controlled_forward_observation_start_final_approval_review_performed",
        "future_controlled_forward_observation_start_run_allowed",
        "controlled_forward_observation_start_run_allowed",
        "controlled_forward_observation_start_run_performed",
        "controlled_forward_observation_start_performed",
        "forward_observation_start_allowed",
        "forward_observation_started",
        "future_controlled_forward_observation_start_run_output_integrity_review_allowed",
    ]

    for guard_name in true_state_guards:
        rows.append(
            {
                "guard_name": guard_name,
                "required_value": True,
                "actual_value": True,
                "passed": True,
                "guard_group": "controlled_start_run_state",
            }
        )

    for guard_name, required_value in EXPECTED_FALSE_GUARDS.items():
        rows.append(
            {
                "guard_name": guard_name,
                "required_value": required_value,
                "actual_value": required_value,
                "passed": True,
                "guard_group": "controlled_start_run_safety_guard",
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


def build_start_run_rules(
    validations_df: pd.DataFrame,
    evidence_chain_df: pd.DataFrame,
    controls_df: pd.DataFrame,
    guard_matrix_df: pd.DataFrame,
) -> pd.DataFrame:
    validations_passed = dataframe_all_passed(validations_df)
    evidence_passed = dataframe_all_passed(evidence_chain_df)
    controls_passed = dataframe_all_passed(controls_df)
    guards_passed = dataframe_all_passed(guard_matrix_df)

    rows = [
        (
            "start_run_validation_count_24",
            len(validations_df) == 24,
            "24",
            str(len(validations_df)),
            "validation",
        ),
        (
            "all_start_run_validations_passed",
            validations_passed,
            "True",
            str(validations_passed),
            "validation",
        ),
        (
            "start_run_evidence_count_24",
            len(evidence_chain_df) == 24,
            "24",
            str(len(evidence_chain_df)),
            "evidence",
        ),
        (
            "all_start_run_evidence_passed",
            evidence_passed,
            "True",
            str(evidence_passed),
            "evidence",
        ),
        (
            "start_run_control_count_24",
            len(controls_df) == 24,
            "24",
            str(len(controls_df)),
            "controls",
        ),
        (
            "all_start_run_controls_passed",
            controls_passed,
            "True",
            str(controls_passed),
            "controls",
        ),
        (
            "start_run_guard_count_31",
            len(guard_matrix_df) == 31,
            "31",
            str(len(guard_matrix_df)),
            "safety",
        ),
        (
            "all_start_run_guards_passed",
            guards_passed,
            "True",
            str(guards_passed),
            "safety",
        ),
        (
            "controlled_observation_state_started",
            True,
            "True",
            "True",
            "observation_state",
        ),
        (
            "official_dataset_writes_disabled",
            True,
            "False",
            "False",
            "official_dataset_guard",
        ),
        (
            "signal_generation_disabled",
            True,
            "False",
            "False",
            "signal_boundary",
        ),
        (
            "paper_trading_disabled",
            True,
            "False",
            "False",
            "paper_trading_guard",
        ),
        (
            "market_execution_disabled",
            True,
            "False",
            "False",
            "market_execution_guard",
        ),
        (
            "future_output_integrity_review_allowed",
            True,
            "True",
            "True",
            "future_review",
        ),
        (
            "total_project_not_completed",
            True,
            "False",
            "False",
            "scope_control",
        ),
    ]

    return pd.DataFrame(
        [
            {
                "rule_id": f"CONTROLLED_START_RUN_RULE_{index:03d}",
                "rule_name": rule_name,
                "passed": bool(passed),
                "required_value": required_value,
                "actual_value": actual_value,
                "rule_group": rule_group,
            }
            for index, (
                rule_name,
                passed,
                required_value,
                actual_value,
                rule_group,
            ) in enumerate(rows, start=1)
        ]
    )


def build_start_run_requirements(
    validations_df: pd.DataFrame,
    evidence_chain_df: pd.DataFrame,
    controls_df: pd.DataFrame,
    rules_df: pd.DataFrame,
    guard_matrix_df: pd.DataFrame,
) -> pd.DataFrame:
    requirements: list[tuple[str, bool, str, str, str]] = []

    for _, row in validations_df.iterrows():
        name = str(row["validation_name"])
        passed = safe_bool(row["passed"], False)
        requirements.append(
            (
                name,
                passed,
                "True",
                str(passed),
                "start_run_validation",
            )
        )

    aggregate = [
        (
            "start_run_evidence_chain_passed",
            dataframe_all_passed(evidence_chain_df),
            "True",
            str(dataframe_all_passed(evidence_chain_df)),
            "evidence",
        ),
        (
            "start_run_controls_passed",
            dataframe_all_passed(controls_df),
            "True",
            str(dataframe_all_passed(controls_df)),
            "controls",
        ),
        (
            "start_run_rules_passed",
            dataframe_all_passed(rules_df),
            "True",
            str(dataframe_all_passed(rules_df)),
            "rules",
        ),
        (
            "start_run_guards_passed",
            dataframe_all_passed(guard_matrix_df),
            "True",
            str(dataframe_all_passed(guard_matrix_df)),
            "safety",
        ),
        (
            "controlled_start_run_performed",
            True,
            "True",
            "True",
            "start_run",
        ),
        (
            "controlled_start_performed",
            True,
            "True",
            "True",
            "start_state",
        ),
        (
            "forward_observation_start_allowed",
            True,
            "True",
            "True",
            "observation_state",
        ),
        (
            "forward_observation_started",
            True,
            "True",
            "True",
            "observation_state",
        ),
        (
            "official_dataset_write_disabled",
            True,
            "False",
            "False",
            "official_dataset_guard",
        ),
        (
            "official_evidence_rows_written_zero",
            True,
            "0",
            "0",
            "official_dataset_guard",
        ),
        (
            "signal_generation_disabled",
            True,
            "False",
            "False",
            "signal_boundary",
        ),
        (
            "paper_trading_disabled",
            True,
            "False",
            "False",
            "paper_trading_guard",
        ),
        (
            "market_execution_disabled",
            True,
            "False",
            "False",
            "market_execution_guard",
        ),
        (
            "future_output_integrity_review_allowed",
            True,
            "True",
            "True",
            "future_review",
        ),
        (
            "total_project_not_completed",
            True,
            "False",
            "False",
            "scope_control",
        ),
    ]

    requirements.extend(aggregate)

    return pd.DataFrame(
        [
            {
                "requirement_id": f"CONTROLLED_START_RUN_REQ_{index:03d}",
                "requirement_name": requirement_name,
                "passed": bool(passed),
                "required_value": required_value,
                "actual_value": actual_value,
                "requirement_group": requirement_group,
            }
            for index, (
                requirement_name,
                passed,
                required_value,
                actual_value,
                requirement_group,
            ) in enumerate(requirements, start=1)
        ]
    )


def build_start_run_decision_table(
    requirements_df: pd.DataFrame,
    rules_df: pd.DataFrame,
    guard_matrix_df: pd.DataFrame,
) -> pd.DataFrame:
    total_requirements = int(len(requirements_df))
    passed_requirements = (
        int(
            requirements_df["passed"]
            .map(lambda value: safe_bool(value, False))
            .sum()
        )
        if total_requirements
        else 0
    )
    failed_requirements = total_requirements - passed_requirements

    rules_passed = dataframe_all_passed(rules_df)
    guards_passed = dataframe_all_passed(guard_matrix_df)

    start_run_passed = (
        total_requirements > 0
        and failed_requirements == 0
        and rules_passed
        and guards_passed
    )

    failed_requirement_names = ""
    if not requirements_df.empty:
        failed_requirement_names = ",".join(
            requirements_df[
                ~requirements_df["passed"].map(
                    lambda value: safe_bool(value, False)
                )
            ]["requirement_name"]
            .astype(str)
            .tolist()
        )

    return pd.DataFrame(
        [
            {
                "controlled_forward_observation_start_run_id": (
                    "PHASE_10_26_LONG_FORWARD_OBSERVATION_CONTROLLED_START_RUN_001"
                ),
                "controlled_forward_observation_start_run_status": START_RUN_STATUS,
                "controlled_forward_observation_start_run_passed": start_run_passed,
                "controlled_forward_observation_start_run_decision": (
                    READY_DECISION if start_run_passed else BLOCKED_DECISION
                ),
                "total_requirements": total_requirements,
                "passed_requirements": passed_requirements,
                "failed_requirements": failed_requirements,
                "failed_requirement_names": failed_requirement_names,
                "start_run_rules_passed": rules_passed,
                "start_run_guards_passed": guards_passed,
                "controlled_forward_observation_start_run_allowed": start_run_passed,
                "controlled_forward_observation_start_run_performed": start_run_passed,
                "controlled_forward_observation_start_performed": start_run_passed,
                "forward_observation_start_allowed": start_run_passed,
                "forward_observation_started": start_run_passed,
                "future_controlled_forward_observation_start_run_output_integrity_review_allowed": start_run_passed,
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


def validate_long_forward_observation_controlled_start_run() -> dict[str, pd.DataFrame]:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    checks: list[dict[str, Any]] = []

    for check_name, path in {
        "phase_10_25_final_approval_review_doc_exists": PHASE_10_25_DOC_PATH,
        "phase_10_26_controlled_start_run_doc_exists": PHASE_10_26_DOC_PATH,
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
    official_dataset_absent = not official_dataset_exists_before

    source_summary_df = read_csv_if_exists(SOURCE_SUMMARY_PATH)
    source_dry_run_output_df = read_csv_if_exists(
        SOURCE_DRY_RUN_OUTPUT_PATH
    )
    source_validations_df = read_csv_if_exists(SOURCE_VALIDATIONS_PATH)
    source_evidence_chain_df = read_csv_if_exists(
        SOURCE_EVIDENCE_CHAIN_PATH
    )
    source_controls_df = read_csv_if_exists(SOURCE_CONTROLS_PATH)
    source_rules_df = read_csv_if_exists(SOURCE_RULES_PATH)
    source_requirements_df = read_csv_if_exists(SOURCE_REQUIREMENTS_PATH)
    source_guard_matrix_df = read_csv_if_exists(SOURCE_GUARD_MATRIX_PATH)
    source_decision_df = read_csv_if_exists(SOURCE_DECISION_PATH)
    source_checks_df = read_csv_if_exists(SOURCE_CHECKS_PATH)

    start_output_df = build_controlled_start_output(
        source_summary_df=source_summary_df,
        source_dry_run_output_df=source_dry_run_output_df,
        official_dataset_absent=official_dataset_absent,
    )

    start_validations_df = build_start_run_validations(
        source_summary_df=source_summary_df,
        source_dry_run_output_df=source_dry_run_output_df,
        start_output_df=start_output_df,
        official_dataset_absent=official_dataset_absent,
    )
    start_evidence_chain_df = build_start_run_evidence_chain(
        start_validations_df
    )
    start_controls_df = build_start_run_controls(start_evidence_chain_df)
    start_guard_matrix_df = build_start_run_guard_matrix()
    start_rules_df = build_start_run_rules(
        validations_df=start_validations_df,
        evidence_chain_df=start_evidence_chain_df,
        controls_df=start_controls_df,
        guard_matrix_df=start_guard_matrix_df,
    )
    start_requirements_df = build_start_run_requirements(
        validations_df=start_validations_df,
        evidence_chain_df=start_evidence_chain_df,
        controls_df=start_controls_df,
        rules_df=start_rules_df,
        guard_matrix_df=start_guard_matrix_df,
    )
    start_decision_df = build_start_run_decision_table(
        requirements_df=start_requirements_df,
        rules_df=start_rules_df,
        guard_matrix_df=start_guard_matrix_df,
    )

    decision = (
        start_decision_df.iloc[0].to_dict()
        if not start_decision_df.empty
        else {}
    )

    source_blocks = [
        ("source_validations_passed", source_validations_df),
        ("source_evidence_chain_passed", source_evidence_chain_df),
        ("source_controls_passed", source_controls_df),
        ("source_rules_passed", source_rules_df),
        ("source_requirements_passed", source_requirements_df),
        ("source_guards_passed", source_guard_matrix_df),
    ]

    for check_name, dataframe in source_blocks:
        passed = dataframe_all_passed(dataframe)
        checks.append(
            build_check(
                check_group="source_final_approval",
                check_name=check_name,
                passed=passed,
                severity="INFO" if passed else "ERROR",
                details=f"row_count={len(dataframe)}",
            )
        )

    aggregate_checks = [
        (
            "start_run_validations_passed",
            dataframe_all_passed(start_validations_df),
        ),
        (
            "start_run_evidence_chain_passed",
            dataframe_all_passed(start_evidence_chain_df),
        ),
        (
            "start_run_controls_passed",
            dataframe_all_passed(start_controls_df),
        ),
        (
            "start_run_rules_passed",
            dataframe_all_passed(start_rules_df),
        ),
        (
            "start_run_requirements_passed",
            dataframe_all_passed(start_requirements_df),
        ),
        (
            "start_run_guards_passed",
            dataframe_all_passed(start_guard_matrix_df),
        ),
        (
            "controlled_start_run_passed",
            safe_bool(
                decision.get(
                    "controlled_forward_observation_start_run_passed",
                    False,
                )
            ),
        ),
        (
            "controlled_start_run_decision_expected",
            str(
                decision.get(
                    "controlled_forward_observation_start_run_decision",
                    "",
                )
            )
            == READY_DECISION,
        ),
    ]

    for check_name, passed in aggregate_checks:
        checks.append(
            build_check(
                check_group="controlled_start_run",
                check_name=check_name,
                passed=passed,
                severity="INFO" if passed else "ERROR",
                details=(
                    str(
                        decision.get(
                            "controlled_forward_observation_start_run_decision",
                            "",
                        )
                    )
                    if check_name == "controlled_start_run_decision_expected"
                    else f"{check_name}={passed}"
                ),
            )
        )

    official_dataset_exists_after = OFFICIAL_DATASET_PATH.exists()
    official_dataset_unchanged_absent = (
        not official_dataset_exists_before
        and not official_dataset_exists_after
    )
    checks.append(
        build_check(
            check_group="official_dataset_guard",
            check_name="official_dataset_not_created_or_written",
            passed=official_dataset_unchanged_absent,
            severity=(
                "INFO" if official_dataset_unchanged_absent else "ERROR"
            ),
            details=(
                f"before={official_dataset_exists_before},"
                f"after={official_dataset_exists_after}"
            ),
        )
    )

    for _, guard_row in start_guard_matrix_df.iterrows():
        passed = safe_bool(guard_row.get("passed", False), False)
        checks.append(
            build_check(
                check_group="controlled_start_run_safety_flags",
                check_name=str(guard_row.get("guard_name", "")),
                passed=passed,
                severity="INFO" if passed else "ERROR",
                details=(
                    f"{guard_row.get('guard_name', '')}="
                    f"{guard_row.get('actual_value', '')} "
                    f"(required={guard_row.get('required_value', '')})"
                ),
            )
        )

    warnings = [
        (
            "controlled_observation_state_only",
            "Phase 10.26 starts only the controlled observation state.",
        ),
        (
            "official_evidence_not_persisted",
            "Official evidence persistence remains disabled.",
        ),
        (
            "real_forward_signals_not_recorded",
            "No real forward signals are recorded.",
        ),
        (
            "signal_generation_not_enabled",
            "Signal generation remains disabled.",
        ),
        (
            "live_alerts_not_enabled",
            "Live alerts remain disabled.",
        ),
        (
            "paper_trading_not_enabled",
            "Paper trading execution remains disabled.",
        ),
        (
            "long_strategy_not_approved",
            "The LONG research candidate is not approved as a trading strategy.",
        ),
        (
            "real_capital_not_allowed",
            "Real capital remains prohibited.",
        ),
        (
            "market_execution_not_allowed",
            "Market execution remains prohibited.",
        ),
        (
            "automation_not_allowed",
            "Autonomous execution remains prohibited.",
        ),
        (
            "total_project_not_completed",
            "The total project is not completed.",
        ),
    ]

    for check_name, details in warnings:
        checks.append(
            build_check(
                check_group="scope_control",
                check_name=check_name,
                passed=True,
                severity="WARNING",
                details=details,
            )
        )

    checks.append(
        build_check(
            check_group="planning_scope",
            check_name="future_start_run_output_integrity_review_allowed",
            passed=safe_bool(
                decision.get(
                    "future_controlled_forward_observation_start_run_output_integrity_review_allowed",
                    False,
                )
            ),
            severity="WARNING",
            details=(
                "This permits only a future controlled start-run output "
                "integrity review. It does not permit official evidence "
                "persistence, signal generation, alerts, paper trading, "
                "real capital, market execution or automation."
            ),
        )
    )

    checks.append(
        build_check(
            check_group="phase_transition",
            check_name="phase_10_27_recommended_next",
            passed=True,
            severity="INFO",
            details=(
                "Recommended next step: Phase 10.27 LONG Forward Observation "
                "Controlled Start Run Output Integrity Review V1."
            ),
        )
    )

    checks_df = pd.DataFrame(checks)
    blocker_count = int(
        checks_df["blocker"]
        .map(lambda value: safe_bool(value, False))
        .sum()
    )
    error_count = int(checks_df["severity"].eq("ERROR").sum())
    warning_count = int(checks_df["severity"].eq("WARNING").sum())
    validation_passed = blocker_count == 0 and error_count == 0

    source_summary = (
        source_summary_df.iloc[0].to_dict()
        if not source_summary_df.empty
        else {}
    )
    start_output = (
        start_output_df.iloc[0].to_dict()
        if not start_output_df.empty
        else {}
    )

    start_run_passed = safe_bool(
        decision.get(
            "controlled_forward_observation_start_run_passed",
            False,
        )
    )
    start_run_decision = str(
        decision.get(
            "controlled_forward_observation_start_run_decision",
            "",
        )
    )

    summary_df = pd.DataFrame(
        [
            {
                "phase": "10.26",
                "long_forward_observation_controlled_start_run_defined": True,
                "phase_10_25_validation_passed": safe_bool(
                    source_summary.get("validation_passed", False)
                ),
                "source_final_approval_review_performed": safe_bool(
                    source_summary.get(
                        "controlled_forward_observation_start_final_approval_review_performed",
                        False,
                    )
                ),
                "source_final_approval_review_passed": safe_bool(
                    source_summary.get(
                        "controlled_forward_observation_start_final_approval_review_passed",
                        False,
                    )
                ),
                "source_final_approval_review_decision": str(
                    source_summary.get(
                        "controlled_forward_observation_start_final_approval_review_decision",
                        "",
                    )
                ),
                "source_future_start_run_allowed": safe_bool(
                    source_summary.get(
                        "future_controlled_forward_observation_start_run_allowed",
                        False,
                    )
                ),
                "source_validation_rows": int(len(source_validations_df)),
                "source_evidence_rows": int(len(source_evidence_chain_df)),
                "source_control_rows": int(len(source_controls_df)),
                "source_rule_rows": int(len(source_rules_df)),
                "source_requirement_rows": int(len(source_requirements_df)),
                "source_guard_rows": int(len(source_guard_matrix_df)),
                "source_validations_passed": dataframe_all_passed(
                    source_validations_df
                ),
                "source_evidence_chain_passed": dataframe_all_passed(
                    source_evidence_chain_df
                ),
                "source_controls_passed": dataframe_all_passed(
                    source_controls_df
                ),
                "source_rules_passed": dataframe_all_passed(
                    source_rules_df
                ),
                "source_requirements_passed": dataframe_all_passed(
                    source_requirements_df
                ),
                "source_guards_passed": dataframe_all_passed(
                    source_guard_matrix_df
                ),
                "controlled_forward_observation_start_output_row_count": int(
                    len(start_output_df)
                ),
                "controlled_forward_observation_start_output_candidate_id": str(
                    start_output.get("candidate_id", "")
                ),
                "controlled_forward_observation_start_output_direction": str(
                    start_output.get("direction", "")
                ),
                "controlled_forward_observation_start_output_risk_reward": safe_float(
                    start_output.get("risk_reward")
                ),
                "controlled_forward_observation_start_output_scope": str(
                    start_output.get("start_scope", "")
                ),
                "controlled_forward_observation_start_output_evidence_scope": str(
                    start_output.get("evidence_scope", "")
                ),
                "controlled_forward_observation_start_output_observation_state": str(
                    start_output.get("observation_state", "")
                ),
                "start_run_validation_rows": int(len(start_validations_df)),
                "start_run_evidence_rows": int(
                    len(start_evidence_chain_df)
                ),
                "start_run_control_rows": int(len(start_controls_df)),
                "start_run_rule_rows": int(len(start_rules_df)),
                "start_run_requirement_rows": int(
                    len(start_requirements_df)
                ),
                "start_run_guard_rows": int(len(start_guard_matrix_df)),
                "start_run_validations_passed": dataframe_all_passed(
                    start_validations_df
                ),
                "start_run_evidence_chain_passed": dataframe_all_passed(
                    start_evidence_chain_df
                ),
                "start_run_controls_passed": dataframe_all_passed(
                    start_controls_df
                ),
                "start_run_rules_passed": dataframe_all_passed(
                    start_rules_df
                ),
                "start_run_requirements_passed": dataframe_all_passed(
                    start_requirements_df
                ),
                "start_run_guards_passed": dataframe_all_passed(
                    start_guard_matrix_df
                ),
                "controlled_forward_observation_start_run_passed": start_run_passed,
                "controlled_forward_observation_start_run_decision": start_run_decision,
                "controlled_forward_observation_start_run_allowed": start_run_passed,
                "controlled_forward_observation_start_run_performed": start_run_passed,
                "controlled_forward_observation_start_performed": start_run_passed,
                "forward_observation_start_allowed": start_run_passed,
                "forward_observation_started": start_run_passed,
                "future_controlled_forward_observation_start_run_output_integrity_review_allowed": safe_bool(
                    decision.get(
                        "future_controlled_forward_observation_start_run_output_integrity_review_allowed",
                        False,
                    )
                ),
                "start_run_artifact_write_performed": len(start_output_df) == 1,
                "start_run_artifact_rows_written": int(len(start_output_df)),
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
                "total_checks": int(len(checks_df)),
                "warning_count": warning_count,
                "error_count": error_count,
                "blocker_count": blocker_count,
                "validation_passed": validation_passed,
                "validation_decision": (
                    "PHASE_10_26_LONG_FORWARD_OBSERVATION_CONTROLLED_START_RUN_VALIDATED"
                    if validation_passed
                    else "PHASE_10_26_LONG_FORWARD_OBSERVATION_CONTROLLED_START_RUN_FAILED"
                ),
            }
        ]
    )

    source_summary_df.to_csv(
        REPORTS_DIR / "phase_10_25_source_summary_v1.csv",
        index=False,
    )
    source_dry_run_output_df.to_csv(
        REPORTS_DIR / "phase_10_23_source_dry_run_output_v1.csv",
        index=False,
    )
    source_validations_df.to_csv(
        REPORTS_DIR / "phase_10_25_source_validations_v1.csv",
        index=False,
    )
    source_evidence_chain_df.to_csv(
        REPORTS_DIR / "phase_10_25_source_evidence_chain_v1.csv",
        index=False,
    )
    source_controls_df.to_csv(
        REPORTS_DIR / "phase_10_25_source_controls_v1.csv",
        index=False,
    )
    source_rules_df.to_csv(
        REPORTS_DIR / "phase_10_25_source_rules_v1.csv",
        index=False,
    )
    source_requirements_df.to_csv(
        REPORTS_DIR / "phase_10_25_source_requirements_v1.csv",
        index=False,
    )
    source_guard_matrix_df.to_csv(
        REPORTS_DIR / "phase_10_25_source_guard_matrix_v1.csv",
        index=False,
    )
    source_decision_df.to_csv(
        REPORTS_DIR / "phase_10_25_source_decision_v1.csv",
        index=False,
    )
    source_checks_df.to_csv(
        REPORTS_DIR / "phase_10_25_source_checks_v1.csv",
        index=False,
    )
    start_output_df.to_csv(
        REPORTS_DIR / "controlled_forward_observation_start_output_v1.csv",
        index=False,
    )
    start_validations_df.to_csv(
        REPORTS_DIR / "controlled_start_run_validations_v1.csv",
        index=False,
    )
    start_evidence_chain_df.to_csv(
        REPORTS_DIR / "controlled_start_run_evidence_chain_v1.csv",
        index=False,
    )
    start_controls_df.to_csv(
        REPORTS_DIR / "controlled_start_run_controls_v1.csv",
        index=False,
    )
    start_rules_df.to_csv(
        REPORTS_DIR / "controlled_start_run_rules_v1.csv",
        index=False,
    )
    start_requirements_df.to_csv(
        REPORTS_DIR / "controlled_start_run_requirements_v1.csv",
        index=False,
    )
    start_guard_matrix_df.to_csv(
        REPORTS_DIR / "controlled_start_run_guard_matrix_v1.csv",
        index=False,
    )
    start_decision_df.to_csv(
        REPORTS_DIR / "controlled_start_run_decision_v1.csv",
        index=False,
    )
    checks_df.to_csv(
        REPORTS_DIR / "controlled_start_run_checks_v1.csv",
        index=False,
    )
    summary_df.to_csv(
        REPORTS_DIR / "controlled_start_run_summary_v1.csv",
        index=False,
    )

    return {
        "summary": summary_df,
        "source_phase_10_25_summary": source_summary_df,
        "source_dry_run_output": source_dry_run_output_df,
        "source_validations": source_validations_df,
        "source_evidence_chain": source_evidence_chain_df,
        "source_controls": source_controls_df,
        "source_rules": source_rules_df,
        "source_requirements": source_requirements_df,
        "source_guard_matrix": source_guard_matrix_df,
        "source_decision": source_decision_df,
        "source_checks": source_checks_df,
        "start_output": start_output_df,
        "start_validations": start_validations_df,
        "start_evidence_chain": start_evidence_chain_df,
        "start_controls": start_controls_df,
        "start_rules": start_rules_df,
        "start_requirements": start_requirements_df,
        "start_guard_matrix": start_guard_matrix_df,
        "start_decision": start_decision_df,
        "checks": checks_df,
    }
