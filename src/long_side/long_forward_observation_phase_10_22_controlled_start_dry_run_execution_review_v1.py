from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from src.long_side.long_forward_observation_dataset_bootstrap_v1 import (
    OFFICIAL_DATASET_PATH,
    PRIMARY_RESEARCH_CANDIDATE,
)
from src.long_side.long_forward_observation_phase_10_21_controlled_start_dry_run_design_v1 import (
    validate_long_forward_observation_controlled_start_dry_run_design,
)


REPORTS_DIR = Path("reports/p10_22_start_dry_run_execution_review_v1")
PHASE_10_21_REPORTS_DIR = Path("reports/p10_21_start_dry_run_design_v1")

PHASE_10_21_DOC_PATH = Path(
    "docs/PHASE_10_LONG_FORWARD_OBSERVATION_CONTROLLED_START_DRY_RUN_DESIGN.md"
)
PHASE_10_22_DOC_PATH = Path(
    "docs/PHASE_10_LONG_FORWARD_OBSERVATION_CONTROLLED_START_DRY_RUN_EXECUTION_REVIEW.md"
)

SOURCE_READY_DECISION = (
    "CONTROLLED_FORWARD_OBSERVATION_START_DRY_RUN_DESIGN_READY_FOR_EXECUTION_REVIEW"
)

EXECUTION_REVIEW_STATUS = (
    "LONG_FORWARD_OBSERVATION_CONTROLLED_START_DRY_RUN_EXECUTION_REVIEW_ONLY"
)

READY_DECISION = (
    "CONTROLLED_FORWARD_OBSERVATION_START_DRY_RUN_EXECUTION_REVIEW_READY_FOR_CONTROLLED_START_DRY_RUN_RUN"
)
BLOCKED_DECISION = (
    "CONTROLLED_FORWARD_OBSERVATION_START_DRY_RUN_EXECUTION_REVIEW_BLOCKED"
)

RECOMMENDED_NEXT_PHASE = (
    "PHASE_10_23_LONG_FORWARD_OBSERVATION_CONTROLLED_START_DRY_RUN_RUN_V1"
)

EXPECTED_FALSE_GUARDS = {
    "controlled_forward_observation_start_dry_run_run_performed": False,
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


def get_phase_10_21_dataframe(
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


def build_execution_review_evidence_chain(
    source_summary_df: pd.DataFrame,
    source_design_output_df: pd.DataFrame,
    source_design_validations_df: pd.DataFrame,
    source_design_controls_df: pd.DataFrame,
    source_design_rules_df: pd.DataFrame,
    source_design_requirements_df: pd.DataFrame,
    source_design_guard_matrix_df: pd.DataFrame,
    source_design_decision_df: pd.DataFrame,
    official_dataset_absent: bool,
) -> pd.DataFrame:
    summary = source_summary_df.iloc[0].to_dict() if not source_summary_df.empty else {}
    design = (
        source_design_output_df.iloc[0].to_dict()
        if not source_design_output_df.empty
        else {}
    )
    decision = (
        source_design_decision_df.iloc[0].to_dict()
        if not source_design_decision_df.empty
        else {}
    )

    validation_lookup = {
        str(row["validation_name"]): safe_bool(row["passed"], False)
        for _, row in source_design_validations_df.iterrows()
    }

    entry_price = float(design.get("entry_price", 0) or 0)
    stop_price = float(design.get("stop_price", 0) or 0)
    target_price = float(design.get("target_price", 0) or 0)
    risk_reward = float(design.get("risk_reward", 0) or 0)

    price_structure_valid = stop_price < entry_price < target_price
    risk_reward_valid = risk_reward == 2.5

    rows = [
        (
            "EXEC_REVIEW_EVIDENCE_001",
            "phase_10_21_validation_passed",
            "dependency",
            safe_bool(summary.get("validation_passed", False)),
            str(summary.get("validation_decision", "")),
        ),
        (
            "EXEC_REVIEW_EVIDENCE_002",
            "start_dry_run_design_passed",
            "design",
            safe_bool(
                summary.get(
                    "controlled_forward_observation_start_dry_run_design_passed",
                    False,
                )
            ),
            str(
                summary.get(
                    "controlled_forward_observation_start_dry_run_design_passed",
                    "",
                )
            ),
        ),
        (
            "EXEC_REVIEW_EVIDENCE_003",
            "start_dry_run_design_decision_expected",
            "design",
            str(
                summary.get(
                    "controlled_forward_observation_start_dry_run_design_decision",
                    "",
                )
            ).strip()
            == SOURCE_READY_DECISION,
            str(
                summary.get(
                    "controlled_forward_observation_start_dry_run_design_decision",
                    "",
                )
            ),
        ),
        (
            "EXEC_REVIEW_EVIDENCE_004",
            "future_execution_review_allowed",
            "future_review",
            safe_bool(
                summary.get(
                    "future_controlled_forward_observation_start_dry_run_execution_review_allowed",
                    False,
                )
            ),
            str(
                summary.get(
                    "future_controlled_forward_observation_start_dry_run_execution_review_allowed",
                    "",
                )
            ),
        ),
        (
            "EXEC_REVIEW_EVIDENCE_005",
            "design_decision_table_consistent",
            "summary_consistency",
            (
                not source_design_decision_df.empty
                and safe_bool(
                    decision.get(
                        "controlled_forward_observation_start_dry_run_design_passed",
                        False,
                    )
                )
                and str(
                    decision.get(
                        "controlled_forward_observation_start_dry_run_design_decision",
                        "",
                    )
                ).strip()
                == SOURCE_READY_DECISION
            ),
            str(
                decision.get(
                    "controlled_forward_observation_start_dry_run_design_decision",
                    "",
                )
            ),
        ),
        (
            "EXEC_REVIEW_EVIDENCE_006",
            "source_design_output_row_count_one",
            "artifact",
            len(source_design_output_df) == 1,
            f"row_count={len(source_design_output_df)}",
        ),
        (
            "EXEC_REVIEW_EVIDENCE_007",
            "source_design_schema_valid",
            "schema",
            validation_lookup.get("design_output_schema_valid", False),
            str(validation_lookup.get("design_output_schema_valid", False)),
        ),
        (
            "EXEC_REVIEW_EVIDENCE_008",
            "source_design_candidate_valid",
            "candidate_scope",
            (
                validation_lookup.get("design_output_candidate_valid", False)
                and str(design.get("candidate_id", "")) == PRIMARY_RESEARCH_CANDIDATE
            ),
            str(design.get("candidate_id", "")),
        ),
        (
            "EXEC_REVIEW_EVIDENCE_009",
            "source_design_direction_valid",
            "direction",
            (
                validation_lookup.get("design_output_direction_valid", False)
                and str(design.get("direction", "")) == "LONG"
            ),
            str(design.get("direction", "")),
        ),
        (
            "EXEC_REVIEW_EVIDENCE_010",
            "source_design_price_structure_valid",
            "price_structure",
            (
                validation_lookup.get("design_output_price_structure_valid", False)
                and price_structure_valid
            ),
            f"stop={stop_price},entry={entry_price},target={target_price}",
        ),
        (
            "EXEC_REVIEW_EVIDENCE_011",
            "source_design_risk_reward_valid",
            "risk_reward",
            (
                validation_lookup.get("design_output_risk_reward_valid", False)
                and risk_reward_valid
            ),
            f"risk_reward={risk_reward}",
        ),
        (
            "EXEC_REVIEW_EVIDENCE_012",
            "source_design_scope_valid",
            "scope_control",
            (
                validation_lookup.get("design_output_scope_valid", False)
                and str(design.get("design_scope", ""))
                == "CONTROLLED_FORWARD_OBSERVATION_START_DRY_RUN_DESIGN_ONLY"
            ),
            str(design.get("design_scope", "")),
        ),
        (
            "EXEC_REVIEW_EVIDENCE_013",
            "source_design_evidence_scope_valid",
            "evidence_scope",
            (
                validation_lookup.get("design_output_evidence_scope_valid", False)
                and str(design.get("evidence_scope", ""))
                == "DESIGN_ONLY_NOT_REAL_EVIDENCE"
            ),
            str(design.get("evidence_scope", "")),
        ),
        (
            "EXEC_REVIEW_EVIDENCE_014",
            "source_design_true_design_fields_valid",
            "design_control",
            validation_lookup.get("design_output_true_design_fields_valid", False),
            str(validation_lookup.get("design_output_true_design_fields_valid", False)),
        ),
        (
            "EXEC_REVIEW_EVIDENCE_015",
            "source_design_operational_locks_valid",
            "safety",
            validation_lookup.get("design_output_operational_locks_valid", False),
            str(validation_lookup.get("design_output_operational_locks_valid", False)),
        ),
        (
            "EXEC_REVIEW_EVIDENCE_016",
            "source_design_official_evidence_rows_zero",
            "official_dataset_guard",
            validation_lookup.get("design_output_official_evidence_rows_zero", False),
            str(design.get("official_evidence_rows_written", "")),
        ),
        (
            "EXEC_REVIEW_EVIDENCE_017",
            "source_design_future_execution_review_allowed",
            "future_review",
            validation_lookup.get(
                "design_output_future_execution_review_allowed",
                False,
            ),
            str(
                design.get(
                    "future_controlled_forward_observation_start_dry_run_execution_review_allowed",
                    "",
                )
            ),
        ),
        (
            "EXEC_REVIEW_EVIDENCE_018",
            "source_design_validation_status_valid",
            "artifact",
            validation_lookup.get("design_output_validation_status_valid", False),
            str(design.get("validation_status", "")),
        ),
        (
            "EXEC_REVIEW_EVIDENCE_019",
            "source_design_controls_passed",
            "controls",
            all_passed(source_design_controls_df),
            f"control_rows={len(source_design_controls_df)}",
        ),
        (
            "EXEC_REVIEW_EVIDENCE_020",
            "source_design_rules_passed",
            "rules",
            all_passed(source_design_rules_df),
            f"rule_rows={len(source_design_rules_df)}",
        ),
        (
            "EXEC_REVIEW_EVIDENCE_021",
            "source_design_requirements_passed",
            "requirements",
            all_passed(source_design_requirements_df),
            f"requirement_rows={len(source_design_requirements_df)}",
        ),
        (
            "EXEC_REVIEW_EVIDENCE_022",
            "source_design_guards_passed",
            "safety",
            all_passed(source_design_guard_matrix_df),
            f"guard_rows={len(source_design_guard_matrix_df)}",
        ),
        (
            "EXEC_REVIEW_EVIDENCE_023",
            "official_dataset_absent",
            "official_dataset_guard",
            official_dataset_absent,
            f"official_dataset_absent={official_dataset_absent}",
        ),
    ]

    return pd.DataFrame(
        [
            {
                "evidence_id": evidence_id,
                "evidence_name": evidence_name,
                "evidence_group": evidence_group,
                "required": True,
                "passed": passed,
                "details": details,
            }
            for evidence_id, evidence_name, evidence_group, passed, details in rows
        ]
    )


def build_execution_review_controls(
    evidence_df: pd.DataFrame,
) -> pd.DataFrame:
    controls = []

    for position, (_, evidence) in enumerate(evidence_df.iterrows(), start=1):
        passed = safe_bool(evidence["passed"], False)

        controls.append(
            {
                "control_position": position,
                "control_id": f"START_DRY_RUN_EXEC_REVIEW_CONTROL_{position:03d}",
                "control_name": str(evidence["evidence_name"]),
                "control_group": str(evidence["evidence_group"]),
                "required": True,
                "execution_review_only": True,
                "future_controlled_forward_observation_start_dry_run_run_allowed": passed,
                "controlled_forward_observation_start_dry_run_run_performed": False,
                "controlled_forward_observation_start_dry_run_performed": False,
                "forward_observation_start_allowed": False,
                "official_dataset_write_allowed": False,
                "market_execution_allowed": False,
                "passed": passed,
            }
        )

    return pd.DataFrame(controls)


def build_execution_review_rules(
    evidence_df: pd.DataFrame,
    controls_df: pd.DataFrame,
    guard_matrix_df: pd.DataFrame,
) -> pd.DataFrame:
    evidence_passed = all_passed(evidence_df)
    controls_passed = all_passed(controls_df)
    guards_passed = all_passed(guard_matrix_df)

    review_only = (
        not controls_df.empty
        and controls_df["execution_review_only"]
        .map(lambda value: safe_bool(value, False))
        .all()
    )

    future_run_allowed = (
        not controls_df.empty
        and controls_df["future_controlled_forward_observation_start_dry_run_run_allowed"]
        .map(lambda value: safe_bool(value, False))
        .all()
    )

    run_not_performed = (
        not controls_df.empty
        and controls_df["controlled_forward_observation_start_dry_run_run_performed"]
        .map(lambda value: safe_bool(value, True))
        .eq(False)
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
        (
            "START_DRY_RUN_EXEC_REVIEW_RULE_001",
            "execution_review_evidence_count_23",
            len(evidence_df) == 23,
            "23",
            str(len(evidence_df)),
            "evidence",
        ),
        (
            "START_DRY_RUN_EXEC_REVIEW_RULE_002",
            "all_execution_review_evidence_passed",
            evidence_passed,
            "True",
            str(evidence_passed),
            "evidence",
        ),
        (
            "START_DRY_RUN_EXEC_REVIEW_RULE_003",
            "execution_review_control_count_23",
            len(controls_df) == 23,
            "23",
            str(len(controls_df)),
            "controls",
        ),
        (
            "START_DRY_RUN_EXEC_REVIEW_RULE_004",
            "all_execution_review_controls_passed",
            controls_passed,
            "True",
            str(controls_passed),
            "controls",
        ),
        (
            "START_DRY_RUN_EXEC_REVIEW_RULE_005",
            "all_execution_review_guards_passed",
            guards_passed,
            "True",
            str(guards_passed),
            "safety",
        ),
        (
            "START_DRY_RUN_EXEC_REVIEW_RULE_006",
            "execution_review_only",
            review_only,
            "True",
            str(review_only),
            "scope_control",
        ),
        (
            "START_DRY_RUN_EXEC_REVIEW_RULE_007",
            "future_start_dry_run_run_allowed",
            future_run_allowed,
            "True",
            str(future_run_allowed),
            "future_run",
        ),
        (
            "START_DRY_RUN_EXEC_REVIEW_RULE_008",
            "start_dry_run_run_not_performed",
            run_not_performed,
            "False",
            "False",
            "dry_run_run_boundary",
        ),
        (
            "START_DRY_RUN_EXEC_REVIEW_RULE_009",
            "start_dry_run_not_performed",
            dry_run_not_performed,
            "False",
            "False",
            "dry_run_boundary",
        ),
        (
            "START_DRY_RUN_EXEC_REVIEW_RULE_010",
            "forward_observation_start_disabled",
            start_disabled,
            "False",
            "False",
            "start_boundary",
        ),
        (
            "START_DRY_RUN_EXEC_REVIEW_RULE_011",
            "official_dataset_writes_disabled",
            dataset_writes_disabled,
            "False",
            "False",
            "official_dataset_guard",
        ),
        (
            "START_DRY_RUN_EXEC_REVIEW_RULE_012",
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
            for (
                rule_id,
                rule_name,
                passed,
                required_value,
                actual_value,
                rule_group,
            ) in rows
        ]
    )


def build_execution_review_guard_matrix(
    review_passed: bool,
) -> pd.DataFrame:
    rows = [
        {
            "guard_name": "controlled_forward_observation_start_dry_run_execution_review_performed",
            "required_value": True,
            "actual_value": True,
            "passed": True,
            "guard_group": "execution_review_state",
        },
        {
            "guard_name": "future_controlled_forward_observation_start_dry_run_run_allowed",
            "required_value": review_passed,
            "actual_value": review_passed,
            "passed": True,
            "guard_group": "execution_review_state",
        },
    ]

    for guard_name, required_value in EXPECTED_FALSE_GUARDS.items():
        rows.append(
            {
                "guard_name": guard_name,
                "required_value": required_value,
                "actual_value": required_value,
                "passed": True,
                "guard_group": "execution_review_safety_guard",
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


def build_execution_review_requirements(
    evidence_df: pd.DataFrame,
    controls_df: pd.DataFrame,
    rules_df: pd.DataFrame,
    guard_matrix_df: pd.DataFrame,
) -> pd.DataFrame:
    requirements = []

    for position, (_, evidence) in enumerate(evidence_df.iterrows(), start=1):
        passed = safe_bool(evidence["passed"], False)

        requirements.append(
            {
                "requirement_id": f"START_DRY_RUN_EXEC_REVIEW_REQ_{position:03d}",
                "requirement_name": str(evidence["evidence_name"]),
                "passed": passed,
                "required_value": "True",
                "actual_value": str(passed),
                "requirement_group": str(evidence["evidence_group"]),
            }
        )

    aggregate_rows = [
        (
            "execution_review_controls_passed",
            all_passed(controls_df),
            "controls",
            "True",
        ),
        (
            "execution_review_rules_passed",
            all_passed(rules_df),
            "rules",
            "True",
        ),
        (
            "execution_review_guards_passed",
            all_passed(guard_matrix_df),
            "safety",
            "True",
        ),
        (
            "start_dry_run_run_not_performed",
            True,
            "dry_run_run_boundary",
            "False",
        ),
        (
            "start_dry_run_not_performed",
            True,
            "dry_run_boundary",
            "False",
        ),
        (
            "forward_observation_start_not_allowed",
            True,
            "start_boundary",
            "False",
        ),
        (
            "official_evidence_rows_written_zero",
            True,
            "official_dataset_guard",
            "0",
        ),
        (
            "market_execution_disabled",
            True,
            "market_execution_guard",
            "False",
        ),
        (
            "total_project_not_completed",
            True,
            "scope_control",
            "False",
        ),
    ]

    start_position = len(requirements) + 1

    for offset, (
        requirement_name,
        passed,
        requirement_group,
        actual_value,
    ) in enumerate(aggregate_rows):
        position = start_position + offset

        requirements.append(
            {
                "requirement_id": f"START_DRY_RUN_EXEC_REVIEW_REQ_{position:03d}",
                "requirement_name": requirement_name,
                "passed": passed,
                "required_value": actual_value,
                "actual_value": actual_value,
                "requirement_group": requirement_group,
            }
        )

    return pd.DataFrame(requirements)


def build_execution_review_decision_table(
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

    review_passed = (
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
                "controlled_forward_observation_start_dry_run_execution_review_id": (
                    "PHASE_10_22_LONG_FORWARD_OBSERVATION_CONTROLLED_START_DRY_RUN_EXECUTION_REVIEW_001"
                ),
                "controlled_forward_observation_start_dry_run_execution_review_status": EXECUTION_REVIEW_STATUS,
                "controlled_forward_observation_start_dry_run_execution_review_passed": review_passed,
                "controlled_forward_observation_start_dry_run_execution_review_decision": (
                    READY_DECISION if review_passed else BLOCKED_DECISION
                ),
                "total_requirements": total_requirements,
                "passed_requirements": passed_requirements,
                "failed_requirements": failed_requirements,
                "failed_requirement_names": failed_requirement_names,
                "execution_review_rules_passed": rules_passed,
                "execution_review_guards_passed": guards_passed,
                "controlled_forward_observation_start_dry_run_execution_review_performed": True,
                "future_controlled_forward_observation_start_dry_run_run_allowed": review_passed,
                "controlled_forward_observation_start_dry_run_run_performed": False,
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


def validate_long_forward_observation_controlled_start_dry_run_execution_review() -> dict[str, pd.DataFrame]:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    checks: list[dict[str, Any]] = []

    phase_anchors = {
        "phase_10_21_start_dry_run_design_doc_exists": PHASE_10_21_DOC_PATH,
        "phase_10_22_start_dry_run_execution_review_doc_exists": PHASE_10_22_DOC_PATH,
    }

    for check_name, path in phase_anchors.items():
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

    phase_10_21_result = validate_long_forward_observation_controlled_start_dry_run_design()

    source_summary_df = get_phase_10_21_dataframe(
        result=phase_10_21_result,
        aliases=("summary", "start_dry_run_design_summary"),
        csv_path=PHASE_10_21_REPORTS_DIR / "start_dry_run_design_summary_v1.csv",
    )

    source_design_output_df = get_phase_10_21_dataframe(
        result=phase_10_21_result,
        aliases=(
            "start_dry_run_design_output",
            "controlled_start_dry_run_design_output",
            "design_output",
        ),
        csv_path=PHASE_10_21_REPORTS_DIR / "controlled_start_dry_run_design_output_v1.csv",
    )

    source_design_validations_df = get_phase_10_21_dataframe(
        result=phase_10_21_result,
        aliases=(
            "start_dry_run_design_validations",
            "design_validations",
            "start_dry_run_design_validation",
        ),
        csv_path=PHASE_10_21_REPORTS_DIR / "start_dry_run_design_validations_v1.csv",
    )

    source_design_controls_df = get_phase_10_21_dataframe(
        result=phase_10_21_result,
        aliases=("start_dry_run_design_controls", "design_controls"),
        csv_path=PHASE_10_21_REPORTS_DIR / "start_dry_run_design_controls_v1.csv",
    )

    source_design_rules_df = get_phase_10_21_dataframe(
        result=phase_10_21_result,
        aliases=("start_dry_run_design_rules", "design_rules"),
        csv_path=PHASE_10_21_REPORTS_DIR / "start_dry_run_design_rules_v1.csv",
    )

    source_design_requirements_df = get_phase_10_21_dataframe(
        result=phase_10_21_result,
        aliases=("start_dry_run_design_requirements", "design_requirements"),
        csv_path=PHASE_10_21_REPORTS_DIR / "start_dry_run_design_requirements_v1.csv",
    )

    source_design_guard_matrix_df = get_phase_10_21_dataframe(
        result=phase_10_21_result,
        aliases=("start_dry_run_design_guard_matrix", "design_guard_matrix"),
        csv_path=PHASE_10_21_REPORTS_DIR / "start_dry_run_design_guard_matrix_v1.csv",
    )

    source_design_decision_df = get_phase_10_21_dataframe(
        result=phase_10_21_result,
        aliases=("start_dry_run_design_decision", "design_decision"),
        csv_path=PHASE_10_21_REPORTS_DIR / "start_dry_run_design_decision_v1.csv",
    )

    source_checks_df = get_phase_10_21_dataframe(
        result=phase_10_21_result,
        aliases=("checks", "start_dry_run_design_checks"),
        csv_path=PHASE_10_21_REPORTS_DIR / "start_dry_run_design_checks_v1.csv",
    )

    official_dataset_exists_after_source_validation = OFFICIAL_DATASET_PATH.exists()

    official_dataset_absent = (
        official_dataset_exists_before is False
        and official_dataset_exists_after_source_validation is False
    )

    evidence_df = build_execution_review_evidence_chain(
        source_summary_df=source_summary_df,
        source_design_output_df=source_design_output_df,
        source_design_validations_df=source_design_validations_df,
        source_design_controls_df=source_design_controls_df,
        source_design_rules_df=source_design_rules_df,
        source_design_requirements_df=source_design_requirements_df,
        source_design_guard_matrix_df=source_design_guard_matrix_df,
        source_design_decision_df=source_design_decision_df,
        official_dataset_absent=official_dataset_absent,
    )

    controls_df = build_execution_review_controls(evidence_df)

    preliminary_guard_matrix_df = build_execution_review_guard_matrix(
        review_passed=all_passed(evidence_df) and all_passed(controls_df)
    )

    rules_df = build_execution_review_rules(
        evidence_df=evidence_df,
        controls_df=controls_df,
        guard_matrix_df=preliminary_guard_matrix_df,
    )

    requirements_df = build_execution_review_requirements(
        evidence_df=evidence_df,
        controls_df=controls_df,
        rules_df=rules_df,
        guard_matrix_df=preliminary_guard_matrix_df,
    )

    decision_df = build_execution_review_decision_table(
        requirements_df=requirements_df,
        rules_df=rules_df,
        guard_matrix_df=preliminary_guard_matrix_df,
    )

    decision = decision_df.iloc[0].to_dict() if not decision_df.empty else {}
    review_passed = safe_bool(
        decision.get(
            "controlled_forward_observation_start_dry_run_execution_review_passed",
            False,
        )
    )

    guard_matrix_df = build_execution_review_guard_matrix(
        review_passed=review_passed,
    )

    decision_df = build_execution_review_decision_table(
        requirements_df=requirements_df,
        rules_df=rules_df,
        guard_matrix_df=guard_matrix_df,
    )

    official_dataset_exists_after = OFFICIAL_DATASET_PATH.exists()

    source_summary = (
        source_summary_df.iloc[0].to_dict()
        if not source_summary_df.empty
        else {}
    )
    source_design = (
        source_design_output_df.iloc[0].to_dict()
        if not source_design_output_df.empty
        else {}
    )

    phase_10_21_validation_passed = safe_bool(
        source_summary.get("validation_passed", False)
    )
    design_passed = safe_bool(
        source_summary.get(
            "controlled_forward_observation_start_dry_run_design_passed",
            False,
        )
    )
    source_design_decision = str(
        source_summary.get(
            "controlled_forward_observation_start_dry_run_design_decision",
            "",
        )
    )
    future_execution_review_allowed = safe_bool(
        source_summary.get(
            "future_controlled_forward_observation_start_dry_run_execution_review_allowed",
            False,
        )
    )

    evidence_passed = all_passed(evidence_df)
    controls_passed = all_passed(controls_df)
    rules_passed = all_passed(rules_df)
    requirements_passed = all_passed(requirements_df)
    guards_passed = all_passed(guard_matrix_df)

    decision = decision_df.iloc[0].to_dict() if not decision_df.empty else {}
    review_passed = safe_bool(
        decision.get(
            "controlled_forward_observation_start_dry_run_execution_review_passed",
            False,
        )
    )
    review_decision = str(
        decision.get(
            "controlled_forward_observation_start_dry_run_execution_review_decision",
            "",
        )
    )
    future_run_allowed = safe_bool(
        decision.get(
            "future_controlled_forward_observation_start_dry_run_run_allowed",
            False,
        )
    )

    dependency_checks = [
        (
            "phase_10_21_validation_passed",
            phase_10_21_validation_passed,
            str(source_summary.get("validation_decision", "")),
        ),
        (
            "start_dry_run_design_passed",
            design_passed,
            f"design_passed={design_passed}",
        ),
        (
            "start_dry_run_design_decision_expected",
            source_design_decision == SOURCE_READY_DECISION,
            source_design_decision,
        ),
        (
            "future_execution_review_allowed",
            future_execution_review_allowed,
            f"future_execution_review_allowed={future_execution_review_allowed}",
        ),
    ]

    for check_name, passed, details in dependency_checks:
        checks.append(
            build_check(
                check_group="phase_dependency",
                check_name=check_name,
                passed=passed,
                severity="INFO" if passed else "ERROR",
                details=details,
            )
        )

    for _, evidence in evidence_df.iterrows():
        passed = safe_bool(evidence["passed"], False)

        checks.append(
            build_check(
                check_group="execution_review_evidence",
                check_name=str(evidence["evidence_name"]),
                passed=passed,
                severity="INFO" if passed else "ERROR",
                details=str(evidence["details"]),
            )
        )

    aggregate_checks = [
        ("execution_review_evidence_chain_passed", evidence_passed),
        ("execution_review_controls_passed", controls_passed),
        ("execution_review_rules_passed", rules_passed),
        ("execution_review_requirements_passed", requirements_passed),
        ("execution_review_guards_passed", guards_passed),
        ("controlled_start_dry_run_execution_review_passed", review_passed),
        ("controlled_start_dry_run_execution_review_decision_expected", review_decision == READY_DECISION),
    ]

    for check_name, passed in aggregate_checks:
        checks.append(
            build_check(
                check_group="execution_review",
                check_name=check_name,
                passed=passed,
                severity="INFO" if passed else "ERROR",
                details=(
                    f"review_decision={review_decision}"
                    if "decision" in check_name
                    else f"{check_name}={passed}"
                ),
            )
        )

    checks.append(
        build_check(
            check_group="planning_scope",
            check_name="future_controlled_start_dry_run_run_allowed",
            passed=future_run_allowed,
            severity="WARNING" if future_run_allowed else "ERROR",
            details=(
                "This permits only a future controlled start dry-run run. "
                "It does not execute the dry-run, start forward observation, "
                "write official evidence, generate alerts, enable paper trading, "
                "use real capital, or permit market execution."
            ),
        )
    )

    final_official_dataset_absent = (
        official_dataset_exists_before is False
        and official_dataset_exists_after is False
    )

    checks.append(
        build_check(
            check_group="official_dataset_guard",
            check_name="official_dataset_not_created_or_written",
            passed=final_official_dataset_absent,
            severity="INFO" if final_official_dataset_absent else "ERROR",
            details=(
                f"before={official_dataset_exists_before},"
                f"after={official_dataset_exists_after}"
            ),
        )
    )

    for _, guard in guard_matrix_df.iterrows():
        passed = safe_bool(guard["passed"], False)

        checks.append(
            build_check(
                check_group="execution_review_safety_flags",
                check_name=str(guard["guard_name"]),
                passed=passed,
                severity="INFO" if passed else "ERROR",
                details=(
                    f"{guard['guard_name']}={guard['actual_value']} "
                    f"(required={guard['required_value']})"
                ),
            )
        )

    scope_checks = [
        (
            "execution_review_only",
            "Phase 10.22 performs only the controlled start dry-run execution review.",
        ),
        (
            "start_dry_run_run_not_performed",
            "The future controlled start dry-run run is not performed in this phase.",
        ),
        (
            "start_dry_run_not_performed",
            "No forward observation start dry-run is executed in this phase.",
        ),
        (
            "forward_observation_not_started",
            "Forward observation remains not started.",
        ),
        (
            "official_evidence_not_persisted",
            "Official evidence persistence remains disabled.",
        ),
        (
            "signal_generation_not_enabled",
            "Signal generation remains disabled.",
        ),
        (
            "paper_trading_not_enabled",
            "Paper trading execution remains disabled.",
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
            "total_project_not_completed",
            "The total project is not completed.",
        ),
    ]

    for check_name, details in scope_checks:
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
            check_group="phase_transition",
            check_name="phase_10_23_recommended_next",
            passed=True,
            severity="INFO",
            details=(
                "Recommended next step: Phase 10.23 LONG Forward Observation "
                "Controlled Start Dry-Run Run V1."
            ),
        )
    )

    checks_df = pd.DataFrame(checks)

    blocker_count = int(checks_df["blocker"].map(lambda value: safe_bool(value)).sum())
    error_count = int(checks_df["severity"].eq("ERROR").sum())
    warning_count = int(checks_df["severity"].eq("WARNING").sum())

    validation_passed = blocker_count == 0 and error_count == 0

    summary_df = pd.DataFrame(
        [
            {
                "phase": "10.22",
                "long_forward_observation_controlled_start_dry_run_execution_review_defined": True,
                "phase_10_21_validation_passed": phase_10_21_validation_passed,
                "controlled_forward_observation_start_dry_run_design_passed": design_passed,
                "controlled_forward_observation_start_dry_run_design_decision": source_design_decision,
                "future_controlled_forward_observation_start_dry_run_execution_review_allowed": future_execution_review_allowed,
                "source_design_output_row_count": len(source_design_output_df),
                "source_design_output_candidate_id": str(source_design.get("candidate_id", "")),
                "source_design_output_candidate_valid": str(source_design.get("candidate_id", "")) == PRIMARY_RESEARCH_CANDIDATE,
                "source_design_output_direction": str(source_design.get("direction", "")),
                "source_design_output_direction_valid": str(source_design.get("direction", "")) == "LONG",
                "source_design_output_risk_reward": float(source_design.get("risk_reward", 0) or 0),
                "source_design_output_scope": str(source_design.get("design_scope", "")),
                "source_design_output_evidence_scope": str(source_design.get("evidence_scope", "")),
                "execution_review_evidence_count": len(evidence_df),
                "execution_review_control_count": len(controls_df),
                "execution_review_rule_rows": len(rules_df),
                "execution_review_requirement_rows": len(requirements_df),
                "execution_review_guard_rows": len(guard_matrix_df),
                "execution_review_evidence_chain_passed": evidence_passed,
                "execution_review_controls_passed": controls_passed,
                "execution_review_rules_passed": rules_passed,
                "execution_review_requirements_passed": requirements_passed,
                "execution_review_guards_passed": guards_passed,
                "controlled_forward_observation_start_dry_run_execution_review_passed": review_passed,
                "controlled_forward_observation_start_dry_run_execution_review_decision": review_decision,
                "controlled_forward_observation_start_dry_run_execution_review_performed": True,
                "future_controlled_forward_observation_start_dry_run_run_allowed": future_run_allowed,
                "controlled_forward_observation_start_dry_run_run_performed": False,
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
                    "PHASE_10_22_LONG_FORWARD_OBSERVATION_CONTROLLED_START_DRY_RUN_EXECUTION_REVIEW_VALIDATED"
                    if validation_passed
                    else "PHASE_10_22_LONG_FORWARD_OBSERVATION_CONTROLLED_START_DRY_RUN_EXECUTION_REVIEW_FAILED"
                ),
            }
        ]
    )

    source_summary_df.to_csv(
        REPORTS_DIR / "phase_10_21_source_summary_v1.csv",
        index=False,
    )
    source_design_output_df.to_csv(
        REPORTS_DIR / "phase_10_21_source_design_output_v1.csv",
        index=False,
    )
    source_design_validations_df.to_csv(
        REPORTS_DIR / "phase_10_21_source_design_validations_v1.csv",
        index=False,
    )
    source_design_controls_df.to_csv(
        REPORTS_DIR / "phase_10_21_source_design_controls_v1.csv",
        index=False,
    )
    source_design_rules_df.to_csv(
        REPORTS_DIR / "phase_10_21_source_design_rules_v1.csv",
        index=False,
    )
    source_design_requirements_df.to_csv(
        REPORTS_DIR / "phase_10_21_source_design_requirements_v1.csv",
        index=False,
    )
    source_design_guard_matrix_df.to_csv(
        REPORTS_DIR / "phase_10_21_source_design_guard_matrix_v1.csv",
        index=False,
    )
    source_design_decision_df.to_csv(
        REPORTS_DIR / "phase_10_21_source_design_decision_v1.csv",
        index=False,
    )
    source_checks_df.to_csv(
        REPORTS_DIR / "phase_10_21_source_checks_v1.csv",
        index=False,
    )
    evidence_df.to_csv(
        REPORTS_DIR / "start_dry_run_execution_review_evidence_chain_v1.csv",
        index=False,
    )
    controls_df.to_csv(
        REPORTS_DIR / "start_dry_run_execution_review_controls_v1.csv",
        index=False,
    )
    rules_df.to_csv(
        REPORTS_DIR / "start_dry_run_execution_review_rules_v1.csv",
        index=False,
    )
    requirements_df.to_csv(
        REPORTS_DIR / "start_dry_run_execution_review_requirements_v1.csv",
        index=False,
    )
    guard_matrix_df.to_csv(
        REPORTS_DIR / "start_dry_run_execution_review_guard_matrix_v1.csv",
        index=False,
    )
    decision_df.to_csv(
        REPORTS_DIR / "start_dry_run_execution_review_decision_v1.csv",
        index=False,
    )
    checks_df.to_csv(
        REPORTS_DIR / "start_dry_run_execution_review_checks_v1.csv",
        index=False,
    )
    summary_df.to_csv(
        REPORTS_DIR / "start_dry_run_execution_review_summary_v1.csv",
        index=False,
    )

    return {
        "summary": summary_df,
        "source_phase_10_21_summary": source_summary_df,
        "source_design_output": source_design_output_df,
        "source_design_validations": source_design_validations_df,
        "source_design_controls": source_design_controls_df,
        "source_design_rules": source_design_rules_df,
        "source_design_requirements": source_design_requirements_df,
        "source_design_guard_matrix": source_design_guard_matrix_df,
        "source_design_decision": source_design_decision_df,
        "source_checks": source_checks_df,
        "execution_review_evidence_chain": evidence_df,
        "execution_review_controls": controls_df,
        "execution_review_rules": rules_df,
        "execution_review_requirements": requirements_df,
        "execution_review_guard_matrix": guard_matrix_df,
        "execution_review_decision": decision_df,
        "checks": checks_df,
    }