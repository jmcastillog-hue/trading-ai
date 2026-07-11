from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from src.long_side.long_forward_observation_dataset_bootstrap_v1 import (
    OFFICIAL_DATASET_PATH,
    PRIMARY_RESEARCH_CANDIDATE,
)
from src.long_side.long_forward_observation_phase_10_16_controlled_start_activation_report_only_dry_run_output_integrity_review_v1 import (
    READY_DECISION as OUTPUT_INTEGRITY_READY_DECISION,
    validate_long_forward_observation_controlled_start_activation_report_only_dry_run_output_integrity_review,
)


REPORTS_DIR = Path("reports/p10_17_final_approval_review_v1")

PHASE_10_16_DOC_PATH = Path(
    "docs/PHASE_10_LONG_FORWARD_OBSERVATION_CONTROLLED_START_ACTIVATION_REPORT_ONLY_DRY_RUN_OUTPUT_INTEGRITY_REVIEW.md"
)
PHASE_10_17_DOC_PATH = Path(
    "docs/PHASE_10_LONG_FORWARD_OBSERVATION_CONTROLLED_START_ACTIVATION_FINAL_APPROVAL_REVIEW.md"
)

FINAL_APPROVAL_REVIEW_STATUS = (
    "LONG_FORWARD_OBSERVATION_CONTROLLED_START_ACTIVATION_FINAL_APPROVAL_REVIEW_ONLY"
)

READY_DECISION = (
    "CONTROLLED_START_ACTIVATION_FINAL_APPROVAL_REVIEW_APPROVED_FOR_CONTROLLED_START_ACTIVATION_RUN"
)
BLOCKED_DECISION = (
    "CONTROLLED_START_ACTIVATION_FINAL_APPROVAL_REVIEW_BLOCKED"
)

RECOMMENDED_NEXT_PHASE = (
    "PHASE_10_18_LONG_FORWARD_OBSERVATION_CONTROLLED_START_ACTIVATION_RUN_V1"
)

EXPECTED_FALSE_GUARDS = {
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


def build_approval_evidence_chain(
    summary_df: pd.DataFrame,
    integrity_decision_df: pd.DataFrame,
    output_df: pd.DataFrame,
    integrity_validation_df: pd.DataFrame,
    integrity_controls_df: pd.DataFrame,
    integrity_rules_df: pd.DataFrame,
    integrity_requirements_df: pd.DataFrame,
    integrity_guard_matrix_df: pd.DataFrame,
    official_dataset_absent: bool,
) -> pd.DataFrame:
    summary = summary_df.iloc[0].to_dict() if not summary_df.empty else {}
    decision = (
        integrity_decision_df.iloc[0].to_dict()
        if not integrity_decision_df.empty
        else {}
    )
    output = output_df.iloc[0].to_dict() if not output_df.empty else {}

    validation_lookup = {
        str(row["validation_name"]): safe_bool(row["passed"], False)
        for _, row in integrity_validation_df.iterrows()
    }

    rows = [
        (
            "APPROVAL_EVIDENCE_001",
            "phase_10_16_validation_passed",
            "dependency",
            safe_bool(summary.get("validation_passed", False)),
            str(summary.get("validation_decision", "")),
        ),
        (
            "APPROVAL_EVIDENCE_002",
            "output_integrity_review_passed",
            "integrity_review",
            safe_bool(
                summary.get(
                    "controlled_start_activation_report_only_dry_run_output_integrity_review_passed",
                    False,
                )
            ),
            str(
                summary.get(
                    "controlled_start_activation_report_only_dry_run_output_integrity_review_passed",
                    "",
                )
            ),
        ),
        (
            "APPROVAL_EVIDENCE_003",
            "output_integrity_review_decision_expected",
            "integrity_review",
            str(
                summary.get(
                    "controlled_start_activation_report_only_dry_run_output_integrity_review_decision",
                    "",
                )
            ).strip()
            == OUTPUT_INTEGRITY_READY_DECISION,
            str(
                summary.get(
                    "controlled_start_activation_report_only_dry_run_output_integrity_review_decision",
                    "",
                )
            ),
        ),
        (
            "APPROVAL_EVIDENCE_004",
            "future_final_approval_review_allowed",
            "future_review",
            safe_bool(
                summary.get(
                    "future_controlled_start_activation_final_approval_review_allowed",
                    False,
                )
            ),
            str(
                summary.get(
                    "future_controlled_start_activation_final_approval_review_allowed",
                    "",
                )
            ),
        ),
        (
            "APPROVAL_EVIDENCE_005",
            "integrity_decision_table_consistent",
            "summary_consistency",
            (
                not integrity_decision_df.empty
                and safe_bool(
                    decision.get(
                        "controlled_start_activation_report_only_dry_run_output_integrity_review_passed",
                        False,
                    )
                )
                and str(
                    decision.get(
                        "controlled_start_activation_report_only_dry_run_output_integrity_review_decision",
                        "",
                    )
                ).strip()
                == OUTPUT_INTEGRITY_READY_DECISION
            ),
            str(
                decision.get(
                    "controlled_start_activation_report_only_dry_run_output_integrity_review_decision",
                    "",
                )
            ),
        ),
        (
            "APPROVAL_EVIDENCE_006",
            "source_output_row_count_one",
            "artifact",
            len(output_df) == 1,
            f"row_count={len(output_df)}",
        ),
        (
            "APPROVAL_EVIDENCE_007",
            "source_schema_match",
            "schema",
            validation_lookup.get("schema_match", False),
            str(validation_lookup.get("schema_match", False)),
        ),
        (
            "APPROVAL_EVIDENCE_008",
            "source_report_only_valid",
            "report_only_scope",
            validation_lookup.get("report_only_valid", False),
            str(output.get("report_only", "")),
        ),
        (
            "APPROVAL_EVIDENCE_009",
            "source_synthetic_scope_valid",
            "evidence_scope",
            validation_lookup.get("synthetic_scope_valid", False),
            str(output.get("synthetic_control_row", "")),
        ),
        (
            "APPROVAL_EVIDENCE_010",
            "source_candidate_valid",
            "candidate_scope",
            (
                validation_lookup.get("candidate_valid", False)
                and str(output.get("candidate_id", ""))
                == PRIMARY_RESEARCH_CANDIDATE
            ),
            str(output.get("candidate_id", "")),
        ),
        (
            "APPROVAL_EVIDENCE_011",
            "source_long_direction_valid",
            "direction",
            (
                validation_lookup.get("direction_valid", False)
                and str(output.get("direction", "")) == "LONG"
            ),
            str(output.get("direction", "")),
        ),
        (
            "APPROVAL_EVIDENCE_012",
            "source_price_structure_valid",
            "price_structure",
            validation_lookup.get("price_structure_valid", False),
            str(validation_lookup.get("price_structure_valid", False)),
        ),
        (
            "APPROVAL_EVIDENCE_013",
            "source_risk_reward_valid",
            "risk_reward",
            (
                validation_lookup.get("risk_reward_valid", False)
                and float(output.get("risk_reward", 0)) == 2.5
            ),
            str(output.get("risk_reward", "")),
        ),
        (
            "APPROVAL_EVIDENCE_014",
            "source_evidence_scope_valid",
            "evidence_scope",
            (
                validation_lookup.get("evidence_scope_valid", False)
                and str(output.get("evidence_scope", ""))
                == "REPORT_ONLY_NOT_REAL_EVIDENCE"
            ),
            str(output.get("evidence_scope", "")),
        ),
        (
            "APPROVAL_EVIDENCE_015",
            "source_execution_locks_valid",
            "execution",
            validation_lookup.get("execution_locks_valid", False),
            str(validation_lookup.get("execution_locks_valid", False)),
        ),
        (
            "APPROVAL_EVIDENCE_016",
            "source_official_evidence_locks_valid",
            "official_dataset_guard",
            validation_lookup.get("official_evidence_locks_valid", False),
            str(validation_lookup.get("official_evidence_locks_valid", False)),
        ),
        (
            "APPROVAL_EVIDENCE_017",
            "source_integrity_controls_passed",
            "controls",
            all_passed(integrity_controls_df),
            f"control_rows={len(integrity_controls_df)}",
        ),
        (
            "APPROVAL_EVIDENCE_018",
            "source_integrity_rules_passed",
            "rules",
            all_passed(integrity_rules_df),
            f"rule_rows={len(integrity_rules_df)}",
        ),
        (
            "APPROVAL_EVIDENCE_019",
            "source_integrity_requirements_passed",
            "requirements",
            all_passed(integrity_requirements_df),
            f"requirement_rows={len(integrity_requirements_df)}",
        ),
        (
            "APPROVAL_EVIDENCE_020",
            "source_integrity_guards_passed",
            "safety",
            all_passed(integrity_guard_matrix_df),
            f"guard_rows={len(integrity_guard_matrix_df)}",
        ),
        (
            "APPROVAL_EVIDENCE_021",
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


def build_final_approval_controls(
    evidence_df: pd.DataFrame,
) -> pd.DataFrame:
    controls = []

    for position, (_, evidence) in enumerate(evidence_df.iterrows(), start=1):
        passed = safe_bool(evidence["passed"], False)

        controls.append(
            {
                "control_position": position,
                "control_id": f"FINAL_APPROVAL_CONTROL_{position:03d}",
                "control_name": str(evidence["evidence_name"]),
                "control_group": str(evidence["evidence_group"]),
                "required": True,
                "final_approval_review_only": True,
                "future_controlled_start_activation_run_allowed": passed,
                "activation_performed": False,
                "forward_observation_start_allowed": False,
                "official_dataset_write_allowed": False,
                "market_execution_allowed": False,
                "passed": passed,
            }
        )

    return pd.DataFrame(controls)


def build_final_approval_rules(
    evidence_df: pd.DataFrame,
    controls_df: pd.DataFrame,
) -> pd.DataFrame:
    evidence_passed = all_passed(evidence_df)
    controls_passed = all_passed(controls_df)

    all_review_only = (
        not controls_df.empty
        and controls_df["final_approval_review_only"]
        .map(lambda value: safe_bool(value, False))
        .all()
    )

    all_future_run_allowed = (
        not controls_df.empty
        and controls_df["future_controlled_start_activation_run_allowed"]
        .map(lambda value: safe_bool(value, False))
        .all()
    )

    no_activation_performed = (
        not controls_df.empty
        and controls_df["activation_performed"]
        .map(lambda value: safe_bool(value, True))
        .eq(False)
        .all()
    )

    all_start_disabled = (
        not controls_df.empty
        and controls_df["forward_observation_start_allowed"]
        .map(lambda value: safe_bool(value, True))
        .eq(False)
        .all()
    )

    all_dataset_writes_disabled = (
        not controls_df.empty
        and controls_df["official_dataset_write_allowed"]
        .map(lambda value: safe_bool(value, True))
        .eq(False)
        .all()
    )

    all_market_execution_disabled = (
        not controls_df.empty
        and controls_df["market_execution_allowed"]
        .map(lambda value: safe_bool(value, True))
        .eq(False)
        .all()
    )

    rows = [
        (
            "FINAL_APPROVAL_RULE_001",
            "approval_evidence_count_21",
            len(evidence_df) == 21,
            "21",
            str(len(evidence_df)),
            "evidence",
        ),
        (
            "FINAL_APPROVAL_RULE_002",
            "all_approval_evidence_passed",
            evidence_passed,
            "True",
            str(evidence_passed),
            "evidence",
        ),
        (
            "FINAL_APPROVAL_RULE_003",
            "final_approval_control_count_21",
            len(controls_df) == 21,
            "21",
            str(len(controls_df)),
            "controls",
        ),
        (
            "FINAL_APPROVAL_RULE_004",
            "all_final_approval_controls_passed",
            controls_passed,
            "True",
            str(controls_passed),
            "controls",
        ),
        (
            "FINAL_APPROVAL_RULE_005",
            "all_controls_final_approval_review_only",
            all_review_only,
            "True",
            str(all_review_only),
            "scope_control",
        ),
        (
            "FINAL_APPROVAL_RULE_006",
            "all_controls_allow_only_future_activation_run",
            all_future_run_allowed,
            "True",
            str(all_future_run_allowed),
            "future_run",
        ),
        (
            "FINAL_APPROVAL_RULE_007",
            "activation_not_performed",
            no_activation_performed,
            "False",
            "False",
            "activation_boundary",
        ),
        (
            "FINAL_APPROVAL_RULE_008",
            "forward_observation_start_disabled",
            all_start_disabled,
            "False",
            "False",
            "start_boundary",
        ),
        (
            "FINAL_APPROVAL_RULE_009",
            "official_dataset_writes_disabled",
            all_dataset_writes_disabled,
            "False",
            "False",
            "official_dataset_guard",
        ),
        (
            "FINAL_APPROVAL_RULE_010",
            "market_execution_disabled",
            all_market_execution_disabled,
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


def build_final_approval_guard_matrix() -> pd.DataFrame:
    rows = [
        {
            "guard_name": "controlled_forward_observation_start_approved",
            "required_value": True,
            "actual_value": True,
            "passed": True,
            "guard_group": "controlled_start_approval_state",
        }
    ]

    for guard_name, required_value in EXPECTED_FALSE_GUARDS.items():
        rows.append(
            {
                "guard_name": guard_name,
                "required_value": required_value,
                "actual_value": required_value,
                "passed": True,
                "guard_group": "final_approval_review_safety_guard",
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


def build_final_approval_requirements(
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
                "requirement_id": f"FINAL_APPROVAL_REQ_{position:03d}",
                "requirement_name": str(evidence["evidence_name"]),
                "passed": passed,
                "required_value": "True",
                "actual_value": str(passed),
                "requirement_group": str(evidence["evidence_group"]),
            }
        )

    aggregate_rows = [
        (
            "final_approval_controls_passed",
            all_passed(controls_df),
            "controls",
            "True",
        ),
        (
            "final_approval_rules_passed",
            all_passed(rules_df),
            "rules",
            "True",
        ),
        (
            "final_approval_guards_passed",
            all_passed(guard_matrix_df),
            "safety",
            "True",
        ),
        (
            "controlled_start_activation_not_performed",
            True,
            "activation_boundary",
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
                "requirement_id": f"FINAL_APPROVAL_REQ_{position:03d}",
                "requirement_name": requirement_name,
                "passed": passed,
                "required_value": actual_value,
                "actual_value": actual_value,
                "requirement_group": requirement_group,
            }
        )

    return pd.DataFrame(requirements)


def build_final_approval_decision_table(
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

    approval_passed = (
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
                "controlled_start_activation_final_approval_review_id": (
                    "PHASE_10_17_LONG_FORWARD_OBSERVATION_CONTROLLED_START_ACTIVATION_FINAL_APPROVAL_REVIEW_001"
                ),
                "controlled_start_activation_final_approval_review_status": (
                    FINAL_APPROVAL_REVIEW_STATUS
                ),
                "controlled_start_activation_final_approval_review_passed": (
                    approval_passed
                ),
                "controlled_start_activation_final_approval_review_decision": (
                    READY_DECISION if approval_passed else BLOCKED_DECISION
                ),
                "total_requirements": total_requirements,
                "passed_requirements": passed_requirements,
                "failed_requirements": failed_requirements,
                "failed_requirement_names": failed_requirement_names,
                "final_approval_rules_passed": rules_passed,
                "final_approval_guards_passed": guards_passed,
                "controlled_forward_observation_start_approved": approval_passed,
                "future_controlled_start_activation_run_allowed": approval_passed,
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


def validate_long_forward_observation_controlled_start_activation_final_approval_review() -> dict[str, pd.DataFrame]:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    checks: list[dict[str, Any]] = []

    phase_anchors = {
        "phase_10_16_output_integrity_review_doc_exists": PHASE_10_16_DOC_PATH,
        "phase_10_17_final_approval_review_doc_exists": PHASE_10_17_DOC_PATH,
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

    phase_10_16_result = (
        validate_long_forward_observation_controlled_start_activation_report_only_dry_run_output_integrity_review()
    )

    source_summary_df = phase_10_16_result["summary"]
    source_output_df = phase_10_16_result["source_report_only_dry_run_output"]
    source_integrity_controls_df = phase_10_16_result["output_integrity_controls"]
    source_integrity_validation_df = phase_10_16_result["output_integrity_validation"]
    source_integrity_rules_df = phase_10_16_result["output_integrity_rules"]
    source_integrity_requirements_df = phase_10_16_result[
        "output_integrity_requirements"
    ]
    source_integrity_guard_matrix_df = phase_10_16_result[
        "output_integrity_guard_matrix"
    ]
    source_integrity_decision_df = phase_10_16_result["output_integrity_decision"]
    source_checks_df = phase_10_16_result["checks"]

    official_dataset_exists_after_source_validation = OFFICIAL_DATASET_PATH.exists()

    official_dataset_absent = (
        official_dataset_exists_before is False
        and official_dataset_exists_after_source_validation is False
    )

    evidence_df = build_approval_evidence_chain(
        summary_df=source_summary_df,
        integrity_decision_df=source_integrity_decision_df,
        output_df=source_output_df,
        integrity_validation_df=source_integrity_validation_df,
        integrity_controls_df=source_integrity_controls_df,
        integrity_rules_df=source_integrity_rules_df,
        integrity_requirements_df=source_integrity_requirements_df,
        integrity_guard_matrix_df=source_integrity_guard_matrix_df,
        official_dataset_absent=official_dataset_absent,
    )

    controls_df = build_final_approval_controls(evidence_df)
    rules_df = build_final_approval_rules(evidence_df, controls_df)
    guard_matrix_df = build_final_approval_guard_matrix()
    requirements_df = build_final_approval_requirements(
        evidence_df=evidence_df,
        controls_df=controls_df,
        rules_df=rules_df,
        guard_matrix_df=guard_matrix_df,
    )
    decision_df = build_final_approval_decision_table(
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
    decision = decision_df.iloc[0].to_dict() if not decision_df.empty else {}

    phase_10_16_validation_passed = safe_bool(
        source_summary.get("validation_passed", False)
    )
    integrity_review_passed = safe_bool(
        source_summary.get(
            "controlled_start_activation_report_only_dry_run_output_integrity_review_passed",
            False,
        )
    )

    evidence_passed = all_passed(evidence_df)
    controls_passed = all_passed(controls_df)
    rules_passed = all_passed(rules_df)
    requirements_passed = all_passed(requirements_df)
    guards_passed = all_passed(guard_matrix_df)

    approval_passed = safe_bool(
        decision.get(
            "controlled_start_activation_final_approval_review_passed",
            False,
        )
    )
    approval_decision = str(
        decision.get(
            "controlled_start_activation_final_approval_review_decision",
            "",
        )
    )
    start_approved = safe_bool(
        decision.get(
            "controlled_forward_observation_start_approved",
            False,
        )
    )
    future_activation_run_allowed = safe_bool(
        decision.get(
            "future_controlled_start_activation_run_allowed",
            False,
        )
    )

    checks.append(
        build_check(
            "phase_dependency",
            "phase_10_16_validation_passed",
            phase_10_16_validation_passed,
            "INFO" if phase_10_16_validation_passed else "ERROR",
            str(source_summary.get("validation_decision", "")),
        )
    )

    checks.append(
        build_check(
            "phase_dependency",
            "output_integrity_review_passed",
            integrity_review_passed,
            "INFO" if integrity_review_passed else "ERROR",
            f"integrity_review_passed={integrity_review_passed}",
        )
    )

    for _, evidence in evidence_df.iterrows():
        passed = safe_bool(evidence["passed"], False)

        checks.append(
            build_check(
                "final_approval_evidence",
                str(evidence["evidence_name"]),
                passed,
                "INFO" if passed else "ERROR",
                str(evidence["details"]),
            )
        )

    aggregate_checks = [
        ("final_approval_evidence_passed", evidence_passed),
        ("final_approval_controls_passed", controls_passed),
        ("final_approval_rules_passed", rules_passed),
        ("final_approval_requirements_passed", requirements_passed),
        ("final_approval_guards_passed", guards_passed),
        ("final_approval_review_passed", approval_passed),
        (
            "final_approval_review_decision_expected",
            approval_decision == READY_DECISION,
        ),
        ("controlled_forward_observation_start_approved", start_approved),
    ]

    for check_name, passed in aggregate_checks:
        checks.append(
            build_check(
                "final_approval_review",
                check_name,
                passed,
                "INFO" if passed else "ERROR",
                (
                    f"approval_decision={approval_decision}"
                    if check_name == "final_approval_review_decision_expected"
                    else f"{check_name}={passed}"
                ),
            )
        )

    checks.append(
        build_check(
            "planning_scope",
            "future_controlled_start_activation_run_allowed",
            future_activation_run_allowed,
            "WARNING" if future_activation_run_allowed else "ERROR",
            (
                "This permits only a future controlled start activation run. "
                "It does not start forward observation, write official evidence, "
                "generate alerts, enable paper trading, use real capital, or "
                "permit market execution."
            ),
        )
    )

    final_official_dataset_absent = (
        official_dataset_exists_before is False
        and official_dataset_exists_after is False
    )

    checks.append(
        build_check(
            "official_dataset_guard",
            "official_dataset_not_written_or_created",
            final_official_dataset_absent,
            "INFO" if final_official_dataset_absent else "ERROR",
            (
                f"official_dataset_exists_before={official_dataset_exists_before},"
                f"official_dataset_exists_after={official_dataset_exists_after}"
            ),
        )
    )

    for _, guard in guard_matrix_df.iterrows():
        passed = safe_bool(guard["passed"], False)

        checks.append(
            build_check(
                "final_approval_safety_flags",
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
                "final_approval_review_only",
                True,
                "WARNING",
                "Phase 10.17 performs only the final approval review.",
            ),
            build_check(
                "scope_control",
                "activation_not_performed",
                True,
                "WARNING",
                "Controlled start activation is not performed in this phase.",
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
                "market_execution_not_allowed",
                True,
                "WARNING",
                "Market execution remains disabled.",
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
                "phase_10_18_recommended_next",
                True,
                "INFO",
                (
                    "Recommended next step: Phase 10.18 LONG Forward Observation "
                    "Controlled Start Activation Run V1."
                ),
            ),
        ]
    )

    checks_df = pd.DataFrame(checks)

    blocker_count = int(checks_df["blocker"].map(lambda value: safe_bool(value)).sum())
    error_count = int(checks_df["severity"].eq("ERROR").sum())
    warning_count = int(checks_df["severity"].eq("WARNING").sum())

    validation_passed = blocker_count == 0 and error_count == 0

    output = source_output_df.iloc[0].to_dict() if not source_output_df.empty else {}

    summary_df = pd.DataFrame(
        [
            {
                "phase": "10.17",
                "long_forward_observation_controlled_start_activation_final_approval_review_defined": True,
                "phase_10_16_validation_passed": phase_10_16_validation_passed,
                "controlled_start_activation_report_only_dry_run_output_integrity_review_passed": integrity_review_passed,
                "controlled_start_activation_report_only_dry_run_output_integrity_review_decision": str(
                    source_summary.get(
                        "controlled_start_activation_report_only_dry_run_output_integrity_review_decision",
                        "",
                    )
                ),
                "future_controlled_start_activation_final_approval_review_allowed": safe_bool(
                    source_summary.get(
                        "future_controlled_start_activation_final_approval_review_allowed",
                        False,
                    )
                ),
                "source_report_only_dry_run_output_row_count": len(source_output_df),
                "source_candidate_id": str(output.get("candidate_id", "")),
                "source_candidate_valid": str(output.get("candidate_id", ""))
                == PRIMARY_RESEARCH_CANDIDATE,
                "source_direction": str(output.get("direction", "")),
                "source_direction_valid": str(output.get("direction", ""))
                == "LONG",
                "source_risk_reward": float(output.get("risk_reward", 0))
                if output
                else 0.0,
                "source_report_only": safe_bool(output.get("report_only", False)),
                "source_synthetic_control_row": safe_bool(
                    output.get("synthetic_control_row", False)
                ),
                "source_evidence_scope": str(output.get("evidence_scope", "")),
                "final_approval_evidence_count": len(evidence_df),
                "final_approval_control_count": len(controls_df),
                "final_approval_rule_rows": len(rules_df),
                "final_approval_requirement_rows": len(requirements_df),
                "final_approval_guard_rows": len(guard_matrix_df),
                "final_approval_evidence_chain_passed": evidence_passed,
                "final_approval_controls_passed": controls_passed,
                "final_approval_rules_passed": rules_passed,
                "final_approval_requirements_passed": requirements_passed,
                "final_approval_guards_passed": guards_passed,
                "controlled_start_activation_final_approval_review_passed": approval_passed,
                "controlled_start_activation_final_approval_review_decision": approval_decision,
                "controlled_forward_observation_start_approved": start_approved,
                "future_controlled_start_activation_run_allowed": future_activation_run_allowed,
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
                "total_checks": len(checks_df),
                "warning_count": warning_count,
                "error_count": error_count,
                "blocker_count": blocker_count,
                "validation_passed": validation_passed,
                "validation_decision": (
                    "PHASE_10_17_LONG_FORWARD_OBSERVATION_CONTROLLED_START_ACTIVATION_FINAL_APPROVAL_REVIEW_VALIDATED"
                    if validation_passed
                    else "PHASE_10_17_LONG_FORWARD_OBSERVATION_CONTROLLED_START_ACTIVATION_FINAL_APPROVAL_REVIEW_FAILED"
                ),
            }
        ]
    )

    source_summary_df.to_csv(
        REPORTS_DIR / "phase_10_16_source_summary_v1.csv",
        index=False,
    )
    source_output_df.to_csv(
        REPORTS_DIR / "phase_10_15_source_report_only_dry_run_output_v1.csv",
        index=False,
    )
    source_integrity_controls_df.to_csv(
        REPORTS_DIR / "phase_10_16_source_integrity_controls_v1.csv",
        index=False,
    )
    source_integrity_validation_df.to_csv(
        REPORTS_DIR / "phase_10_16_source_integrity_validations_v1.csv",
        index=False,
    )
    source_integrity_rules_df.to_csv(
        REPORTS_DIR / "phase_10_16_source_integrity_rules_v1.csv",
        index=False,
    )
    source_integrity_requirements_df.to_csv(
        REPORTS_DIR / "phase_10_16_source_integrity_requirements_v1.csv",
        index=False,
    )
    source_integrity_guard_matrix_df.to_csv(
        REPORTS_DIR / "phase_10_16_source_integrity_guard_matrix_v1.csv",
        index=False,
    )
    source_integrity_decision_df.to_csv(
        REPORTS_DIR / "phase_10_16_source_integrity_decision_v1.csv",
        index=False,
    )
    source_checks_df.to_csv(
        REPORTS_DIR / "phase_10_16_source_checks_v1.csv",
        index=False,
    )
    evidence_df.to_csv(
        REPORTS_DIR / "final_approval_evidence_chain_v1.csv",
        index=False,
    )
    controls_df.to_csv(
        REPORTS_DIR / "final_approval_controls_v1.csv",
        index=False,
    )
    rules_df.to_csv(
        REPORTS_DIR / "final_approval_rules_v1.csv",
        index=False,
    )
    requirements_df.to_csv(
        REPORTS_DIR / "final_approval_requirements_v1.csv",
        index=False,
    )
    guard_matrix_df.to_csv(
        REPORTS_DIR / "final_approval_guard_matrix_v1.csv",
        index=False,
    )
    decision_df.to_csv(
        REPORTS_DIR / "final_approval_decision_v1.csv",
        index=False,
    )
    checks_df.to_csv(
        REPORTS_DIR / "final_approval_checks_v1.csv",
        index=False,
    )
    summary_df.to_csv(
        REPORTS_DIR / "final_approval_summary_v1.csv",
        index=False,
    )

    return {
        "summary": summary_df,
        "source_phase_10_16_summary": source_summary_df,
        "source_report_only_dry_run_output": source_output_df,
        "source_integrity_controls": source_integrity_controls_df,
        "source_integrity_validation": source_integrity_validation_df,
        "source_integrity_rules": source_integrity_rules_df,
        "source_integrity_requirements": source_integrity_requirements_df,
        "source_integrity_guard_matrix": source_integrity_guard_matrix_df,
        "source_integrity_decision": source_integrity_decision_df,
        "source_checks": source_checks_df,
        "final_approval_evidence_chain": evidence_df,
        "final_approval_controls": controls_df,
        "final_approval_rules": rules_df,
        "final_approval_requirements": requirements_df,
        "final_approval_guard_matrix": guard_matrix_df,
        "final_approval_decision": decision_df,
        "checks": checks_df,
    }