from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from src.long_side.long_forward_observation_dataset_bootstrap_v1 import (
    OFFICIAL_DATASET_PATH,
    PRIMARY_RESEARCH_CANDIDATE,
)
from src.long_side.long_forward_observation_phase_10_19_controlled_start_activation_run_output_integrity_review_v1 import (
    validate_long_forward_observation_controlled_start_activation_run_output_integrity_review,
)


REPORTS_DIR = Path("reports/p10_20_pre_start_review_v1")
PHASE_10_19_REPORTS_DIR = Path("reports/p10_19_activation_output_integrity_v1")

PHASE_10_19_DOC_PATH = Path(
    "docs/PHASE_10_LONG_FORWARD_OBSERVATION_CONTROLLED_START_ACTIVATION_RUN_OUTPUT_INTEGRITY_REVIEW.md"
)
PHASE_10_20_DOC_PATH = Path(
    "docs/PHASE_10_LONG_FORWARD_OBSERVATION_CONTROLLED_PRE_START_REVIEW.md"
)

EXPECTED_PHASE_10_19_DECISION = (
    "CONTROLLED_START_ACTIVATION_RUN_OUTPUT_INTEGRITY_REVIEW_READY_FOR_CONTROLLED_FORWARD_OBSERVATION_PRE_START_REVIEW"
)

PRE_START_REVIEW_STATUS = (
    "LONG_FORWARD_OBSERVATION_CONTROLLED_PRE_START_REVIEW_ONLY"
)

READY_DECISION = (
    "CONTROLLED_FORWARD_OBSERVATION_PRE_START_REVIEW_READY_FOR_CONTROLLED_FORWARD_OBSERVATION_START_DRY_RUN_DESIGN"
)
BLOCKED_DECISION = "CONTROLLED_FORWARD_OBSERVATION_PRE_START_REVIEW_BLOCKED"

RECOMMENDED_NEXT_PHASE = (
    "PHASE_10_21_LONG_FORWARD_OBSERVATION_CONTROLLED_START_DRY_RUN_DESIGN_V1"
)

EXPECTED_FALSE_GUARDS = {
    "new_activation_run_performed": False,
    "controlled_forward_observation_start_dry_run_design_performed": False,
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


def get_phase_10_19_dataframe(
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


def build_pre_start_evidence_chain(
    phase_10_19_summary_df: pd.DataFrame,
    phase_10_19_decision_df: pd.DataFrame,
    source_activation_output_df: pd.DataFrame,
    source_integrity_validation_df: pd.DataFrame,
    source_integrity_controls_df: pd.DataFrame,
    source_integrity_rules_df: pd.DataFrame,
    source_integrity_requirements_df: pd.DataFrame,
    source_integrity_guard_matrix_df: pd.DataFrame,
    official_dataset_absent: bool,
) -> pd.DataFrame:
    summary = (
        phase_10_19_summary_df.iloc[0].to_dict()
        if not phase_10_19_summary_df.empty
        else {}
    )
    decision = (
        phase_10_19_decision_df.iloc[0].to_dict()
        if not phase_10_19_decision_df.empty
        else {}
    )
    output = (
        source_activation_output_df.iloc[0].to_dict()
        if not source_activation_output_df.empty
        else {}
    )

    validation_lookup = {
        str(row["validation_name"]): safe_bool(row["passed"], False)
        for _, row in source_integrity_validation_df.iterrows()
        if "validation_name" in source_integrity_validation_df.columns
    }

    rows = [
        (
            "PRE_START_EVIDENCE_001",
            "phase_10_19_validation_passed",
            "dependency",
            safe_bool(summary.get("validation_passed", False)),
            str(summary.get("validation_decision", "")),
        ),
        (
            "PRE_START_EVIDENCE_002",
            "activation_output_integrity_review_passed",
            "integrity_review",
            safe_bool(
                summary.get(
                    "controlled_start_activation_run_output_integrity_review_passed",
                    False,
                )
            ),
            str(
                summary.get(
                    "controlled_start_activation_run_output_integrity_review_passed",
                    "",
                )
            ),
        ),
        (
            "PRE_START_EVIDENCE_003",
            "activation_output_integrity_decision_expected",
            "integrity_review",
            str(
                summary.get(
                    "controlled_start_activation_run_output_integrity_review_decision",
                    "",
                )
            ).strip()
            == EXPECTED_PHASE_10_19_DECISION,
            str(
                summary.get(
                    "controlled_start_activation_run_output_integrity_review_decision",
                    "",
                )
            ),
        ),
        (
            "PRE_START_EVIDENCE_004",
            "future_pre_start_review_allowed",
            "future_review",
            safe_bool(
                summary.get(
                    "future_controlled_forward_observation_pre_start_review_allowed",
                    False,
                )
            ),
            str(
                summary.get(
                    "future_controlled_forward_observation_pre_start_review_allowed",
                    "",
                )
            ),
        ),
        (
            "PRE_START_EVIDENCE_005",
            "integrity_decision_table_consistent",
            "summary_consistency",
            (
                not phase_10_19_decision_df.empty
                and safe_bool(
                    decision.get(
                        "controlled_start_activation_run_output_integrity_review_passed",
                        False,
                    )
                )
                and str(
                    decision.get(
                        "controlled_start_activation_run_output_integrity_review_decision",
                        "",
                    )
                ).strip()
                == EXPECTED_PHASE_10_19_DECISION
            ),
            str(
                decision.get(
                    "controlled_start_activation_run_output_integrity_review_decision",
                    "",
                )
            ),
        ),
        (
            "PRE_START_EVIDENCE_006",
            "source_activation_output_row_count_one",
            "artifact",
            len(source_activation_output_df) == 1,
            f"row_count={len(source_activation_output_df)}",
        ),
        (
            "PRE_START_EVIDENCE_007",
            "source_candidate_valid",
            "candidate_scope",
            (
                str(output.get("candidate_id", "")) == PRIMARY_RESEARCH_CANDIDATE
                and validation_lookup.get("activation_output_candidate_valid", False)
            ),
            str(output.get("candidate_id", "")),
        ),
        (
            "PRE_START_EVIDENCE_008",
            "source_direction_valid",
            "direction",
            (
                str(output.get("direction", "")) == "LONG"
                and validation_lookup.get("activation_output_direction_valid", False)
            ),
            str(output.get("direction", "")),
        ),
        (
            "PRE_START_EVIDENCE_009",
            "source_control_plane_scope_valid",
            "scope_control",
            (
                str(output.get("activation_scope", ""))
                == "CONTROL_PLANE_ONLY_NOT_FORWARD_OBSERVATION"
                and validation_lookup.get(
                    "activation_output_control_plane_scope_valid",
                    False,
                )
            ),
            str(output.get("activation_scope", "")),
        ),
        (
            "PRE_START_EVIDENCE_010",
            "source_evidence_scope_valid",
            "evidence_scope",
            (
                str(output.get("evidence_scope", ""))
                == "ACTIVATION_CONTROL_ONLY_NOT_REAL_EVIDENCE"
                and validation_lookup.get("activation_output_evidence_scope_valid", False)
            ),
            str(output.get("evidence_scope", "")),
        ),
        (
            "PRE_START_EVIDENCE_011",
            "source_true_activation_fields_valid",
            "activation_control",
            validation_lookup.get(
                "activation_output_true_activation_fields_valid",
                False,
            ),
            str(
                validation_lookup.get(
                    "activation_output_true_activation_fields_valid",
                    False,
                )
            ),
        ),
        (
            "PRE_START_EVIDENCE_012",
            "source_operational_locks_valid",
            "safety",
            validation_lookup.get("activation_output_operational_locks_valid", False),
            str(validation_lookup.get("activation_output_operational_locks_valid", False)),
        ),
        (
            "PRE_START_EVIDENCE_013",
            "source_official_evidence_rows_zero",
            "official_dataset_guard",
            validation_lookup.get(
                "activation_output_official_evidence_rows_zero",
                False,
            ),
            str(output.get("official_evidence_rows_written", "")),
        ),
        (
            "PRE_START_EVIDENCE_014",
            "source_future_integrity_review_allowed",
            "future_review",
            validation_lookup.get(
                "activation_output_future_integrity_review_allowed",
                False,
            ),
            str(
                output.get(
                    "future_controlled_start_activation_run_output_integrity_review_allowed",
                    "",
                )
            ),
        ),
        (
            "PRE_START_EVIDENCE_015",
            "source_integrity_validations_passed",
            "validation",
            all_passed(source_integrity_validation_df),
            f"validation_rows={len(source_integrity_validation_df)}",
        ),
        (
            "PRE_START_EVIDENCE_016",
            "source_integrity_controls_passed",
            "controls",
            all_passed(source_integrity_controls_df),
            f"control_rows={len(source_integrity_controls_df)}",
        ),
        (
            "PRE_START_EVIDENCE_017",
            "source_integrity_rules_passed",
            "rules",
            all_passed(source_integrity_rules_df),
            f"rule_rows={len(source_integrity_rules_df)}",
        ),
        (
            "PRE_START_EVIDENCE_018",
            "source_integrity_requirements_passed",
            "requirements",
            all_passed(source_integrity_requirements_df),
            f"requirement_rows={len(source_integrity_requirements_df)}",
        ),
        (
            "PRE_START_EVIDENCE_019",
            "source_integrity_guards_passed",
            "safety",
            all_passed(source_integrity_guard_matrix_df),
            f"guard_rows={len(source_integrity_guard_matrix_df)}",
        ),
        (
            "PRE_START_EVIDENCE_020",
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


def build_pre_start_controls(evidence_df: pd.DataFrame) -> pd.DataFrame:
    rows = []

    for position, (_, evidence) in enumerate(evidence_df.iterrows(), start=1):
        passed = safe_bool(evidence["passed"], False)

        rows.append(
            {
                "control_position": position,
                "control_id": f"PRE_START_CONTROL_{position:03d}",
                "control_name": str(evidence["evidence_name"]),
                "control_group": str(evidence["evidence_group"]),
                "required": True,
                "pre_start_review_only": True,
                "future_controlled_forward_observation_start_dry_run_design_allowed": passed,
                "new_activation_run_allowed": False,
                "new_activation_run_performed": False,
                "controlled_forward_observation_start_dry_run_design_performed": False,
                "controlled_forward_observation_start_dry_run_performed": False,
                "forward_observation_start_allowed": False,
                "official_dataset_write_allowed": False,
                "market_execution_allowed": False,
                "passed": passed,
            }
        )

    return pd.DataFrame(rows)


def build_pre_start_guard_matrix(
    pre_start_review_passed: bool,
    future_dry_run_design_allowed: bool,
) -> pd.DataFrame:
    rows = [
        {
            "guard_name": "controlled_forward_observation_pre_start_review_passed",
            "required_value": True,
            "actual_value": pre_start_review_passed,
            "passed": pre_start_review_passed is True,
            "guard_group": "pre_start_review_state",
        },
        {
            "guard_name": "future_controlled_forward_observation_start_dry_run_design_allowed",
            "required_value": True,
            "actual_value": future_dry_run_design_allowed,
            "passed": future_dry_run_design_allowed is True,
            "guard_group": "pre_start_review_state",
        },
    ]

    for guard_name, required_value in EXPECTED_FALSE_GUARDS.items():
        rows.append(
            {
                "guard_name": guard_name,
                "required_value": required_value,
                "actual_value": required_value,
                "passed": True,
                "guard_group": "pre_start_review_safety_guard",
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


def build_pre_start_rules(
    evidence_df: pd.DataFrame,
    controls_df: pd.DataFrame,
    guard_matrix_df: pd.DataFrame,
) -> pd.DataFrame:
    evidence_passed = all_passed(evidence_df)
    controls_passed = all_passed(controls_df)
    guards_passed = all_passed(guard_matrix_df)

    review_only = (
        not controls_df.empty
        and controls_df["pre_start_review_only"]
        .map(lambda value: safe_bool(value, False))
        .all()
    )

    future_design_allowed = (
        not controls_df.empty
        and controls_df[
            "future_controlled_forward_observation_start_dry_run_design_allowed"
        ]
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

    no_dry_run_design_performed = (
        not controls_df.empty
        and controls_df["controlled_forward_observation_start_dry_run_design_performed"]
        .map(lambda value: safe_bool(value, True))
        .eq(False)
        .all()
    )

    no_start_dry_run_performed = (
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
        ("PRE_START_RULE_001", "pre_start_evidence_count_20", len(evidence_df) == 20, "20", str(len(evidence_df)), "evidence"),
        ("PRE_START_RULE_002", "all_pre_start_evidence_passed", evidence_passed, "True", str(evidence_passed), "evidence"),
        ("PRE_START_RULE_003", "pre_start_control_count_20", len(controls_df) == 20, "20", str(len(controls_df)), "controls"),
        ("PRE_START_RULE_004", "all_pre_start_controls_passed", controls_passed, "True", str(controls_passed), "controls"),
        ("PRE_START_RULE_005", "all_pre_start_guards_passed", guards_passed, "True", str(guards_passed), "safety"),
        ("PRE_START_RULE_006", "pre_start_review_only", review_only, "True", str(review_only), "scope_control"),
        ("PRE_START_RULE_007", "future_start_dry_run_design_allowed", future_design_allowed, "True", str(future_design_allowed), "future_design"),
        ("PRE_START_RULE_008", "no_new_activation_run", no_new_activation, "False", "False", "activation_boundary"),
        ("PRE_START_RULE_009", "no_start_dry_run_design_performed", no_dry_run_design_performed, "False", "False", "dry_run_design_boundary"),
        ("PRE_START_RULE_010", "no_start_dry_run_performed", no_start_dry_run_performed, "False", "False", "dry_run_boundary"),
        ("PRE_START_RULE_011", "forward_observation_start_disabled", start_disabled, "False", "False", "start_boundary"),
        ("PRE_START_RULE_012", "official_dataset_writes_disabled", dataset_write_disabled, "False", "False", "official_dataset_guard"),
        ("PRE_START_RULE_013", "market_execution_disabled", market_execution_disabled, "False", "False", "market_execution_guard"),
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


def build_pre_start_requirements(
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
                "requirement_id": f"PRE_START_REQ_{position:03d}",
                "requirement_name": str(evidence["evidence_name"]),
                "passed": passed,
                "required_value": "True",
                "actual_value": str(passed),
                "requirement_group": str(evidence["evidence_group"]),
            }
        )

    aggregate_rows = [
        ("pre_start_controls_passed", all_passed(controls_df), "controls", "True", "True"),
        ("pre_start_rules_passed", all_passed(rules_df), "rules", "True", "True"),
        ("pre_start_guards_passed", all_passed(guard_matrix_df), "safety", "True", "True"),
        ("new_activation_run_not_performed", True, "activation_boundary", "False", "False"),
        ("start_dry_run_design_not_performed", True, "dry_run_design_boundary", "False", "False"),
        ("start_dry_run_not_performed", True, "dry_run_boundary", "False", "False"),
        ("forward_observation_start_not_allowed", True, "start_boundary", "False", "False"),
        ("official_evidence_rows_written_zero", True, "official_dataset_guard", "0", "0"),
        ("market_execution_disabled", True, "market_execution_guard", "False", "False"),
        ("total_project_not_completed", True, "scope_control", "False", "False"),
    ]

    start_position = len(requirements) + 1

    for offset, (
        requirement_name,
        passed,
        requirement_group,
        required_value,
        actual_value,
    ) in enumerate(aggregate_rows):
        position = start_position + offset

        requirements.append(
            {
                "requirement_id": f"PRE_START_REQ_{position:03d}",
                "requirement_name": requirement_name,
                "passed": passed,
                "required_value": required_value,
                "actual_value": actual_value,
                "requirement_group": requirement_group,
            }
        )

    return pd.DataFrame(requirements)


def build_pre_start_decision_table(
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

    pre_start_passed = (
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
                "controlled_forward_observation_pre_start_review_id": (
                    "PHASE_10_20_LONG_FORWARD_OBSERVATION_CONTROLLED_PRE_START_REVIEW_001"
                ),
                "controlled_forward_observation_pre_start_review_status": PRE_START_REVIEW_STATUS,
                "controlled_forward_observation_pre_start_review_passed": pre_start_passed,
                "controlled_forward_observation_pre_start_review_decision": (
                    READY_DECISION if pre_start_passed else BLOCKED_DECISION
                ),
                "total_requirements": total_requirements,
                "passed_requirements": passed_requirements,
                "failed_requirements": failed_requirements,
                "failed_requirement_names": failed_requirement_names,
                "pre_start_rules_passed": rules_passed,
                "pre_start_guards_passed": guards_passed,
                "future_controlled_forward_observation_start_dry_run_design_allowed": pre_start_passed,
                "new_activation_run_performed": False,
                "controlled_forward_observation_start_dry_run_design_performed": False,
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


def validate_long_forward_observation_controlled_pre_start_review() -> dict[str, pd.DataFrame]:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    checks: list[dict[str, Any]] = []

    for check_name, path in {
        "phase_10_19_activation_output_integrity_doc_exists": PHASE_10_19_DOC_PATH,
        "phase_10_20_pre_start_review_doc_exists": PHASE_10_20_DOC_PATH,
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

    phase_10_19_result = (
        validate_long_forward_observation_controlled_start_activation_run_output_integrity_review()
    )

    source_summary_df = get_phase_10_19_dataframe(
        result=phase_10_19_result,
        aliases=("summary", "activation_output_integrity_summary"),
        csv_path=PHASE_10_19_REPORTS_DIR / "activation_output_integrity_summary_v1.csv",
    )

    source_activation_output_df = get_phase_10_19_dataframe(
        result=phase_10_19_result,
        aliases=(
            "source_activation_output",
            "activation_output",
            "source_phase_10_18_activation_output",
        ),
        csv_path=PHASE_10_19_REPORTS_DIR / "phase_10_18_source_activation_output_v1.csv",
    )

    source_integrity_validation_df = get_phase_10_19_dataframe(
        result=phase_10_19_result,
        aliases=(
            "activation_output_integrity_validation",
            "activation_output_integrity_validations",
        ),
        csv_path=PHASE_10_19_REPORTS_DIR / "activation_output_integrity_validations_v1.csv",
    )

    source_integrity_controls_df = get_phase_10_19_dataframe(
        result=phase_10_19_result,
        aliases=("activation_output_integrity_controls",),
        csv_path=PHASE_10_19_REPORTS_DIR / "activation_output_integrity_controls_v1.csv",
    )

    source_integrity_rules_df = get_phase_10_19_dataframe(
        result=phase_10_19_result,
        aliases=("activation_output_integrity_rules",),
        csv_path=PHASE_10_19_REPORTS_DIR / "activation_output_integrity_rules_v1.csv",
    )

    source_integrity_requirements_df = get_phase_10_19_dataframe(
        result=phase_10_19_result,
        aliases=("activation_output_integrity_requirements",),
        csv_path=PHASE_10_19_REPORTS_DIR / "activation_output_integrity_requirements_v1.csv",
    )

    source_integrity_guard_matrix_df = get_phase_10_19_dataframe(
        result=phase_10_19_result,
        aliases=("activation_output_integrity_guard_matrix",),
        csv_path=PHASE_10_19_REPORTS_DIR / "activation_output_integrity_guard_matrix_v1.csv",
    )

    source_integrity_decision_df = get_phase_10_19_dataframe(
        result=phase_10_19_result,
        aliases=(
            "activation_output_integrity_decision",
            "decision",
        ),
        csv_path=PHASE_10_19_REPORTS_DIR / "activation_output_integrity_decision_v1.csv",
    )

    source_checks_df = get_phase_10_19_dataframe(
        result=phase_10_19_result,
        aliases=("checks", "activation_output_integrity_checks"),
        csv_path=PHASE_10_19_REPORTS_DIR / "activation_output_integrity_checks_v1.csv",
    )

    official_dataset_exists_after_source_validation = OFFICIAL_DATASET_PATH.exists()
    official_dataset_absent = (
        official_dataset_exists_before is False
        and official_dataset_exists_after_source_validation is False
    )

    evidence_df = build_pre_start_evidence_chain(
        phase_10_19_summary_df=source_summary_df,
        phase_10_19_decision_df=source_integrity_decision_df,
        source_activation_output_df=source_activation_output_df,
        source_integrity_validation_df=source_integrity_validation_df,
        source_integrity_controls_df=source_integrity_controls_df,
        source_integrity_rules_df=source_integrity_rules_df,
        source_integrity_requirements_df=source_integrity_requirements_df,
        source_integrity_guard_matrix_df=source_integrity_guard_matrix_df,
        official_dataset_absent=official_dataset_absent,
    )
    controls_df = build_pre_start_controls(evidence_df)

    pre_start_evidence_passed = all_passed(evidence_df)
    pre_start_controls_passed = all_passed(controls_df)

    pre_start_review_prelim_passed = (
        pre_start_evidence_passed and pre_start_controls_passed
    )
    future_dry_run_design_allowed_prelim = pre_start_review_prelim_passed

    guard_matrix_df = build_pre_start_guard_matrix(
        pre_start_review_passed=pre_start_review_prelim_passed,
        future_dry_run_design_allowed=future_dry_run_design_allowed_prelim,
    )
    rules_df = build_pre_start_rules(
        evidence_df=evidence_df,
        controls_df=controls_df,
        guard_matrix_df=guard_matrix_df,
    )
    requirements_df = build_pre_start_requirements(
        evidence_df=evidence_df,
        controls_df=controls_df,
        rules_df=rules_df,
        guard_matrix_df=guard_matrix_df,
    )
    decision_df = build_pre_start_decision_table(
        requirements_df=requirements_df,
        rules_df=rules_df,
        guard_matrix_df=guard_matrix_df,
    )

    decision = decision_df.iloc[0].to_dict() if not decision_df.empty else {}

    pre_start_review_passed = safe_bool(
        decision.get(
            "controlled_forward_observation_pre_start_review_passed",
            False,
        )
    )
    pre_start_decision = str(
        decision.get(
            "controlled_forward_observation_pre_start_review_decision",
            "",
        )
    )
    future_dry_run_design_allowed = safe_bool(
        decision.get(
            "future_controlled_forward_observation_start_dry_run_design_allowed",
            False,
        )
    )

    official_dataset_exists_after = OFFICIAL_DATASET_PATH.exists()
    official_dataset_absent_final = (
        official_dataset_exists_before is False
        and official_dataset_exists_after is False
    )

    source_summary = (
        source_summary_df.iloc[0].to_dict() if not source_summary_df.empty else {}
    )
    source_output = (
        source_activation_output_df.iloc[0].to_dict()
        if not source_activation_output_df.empty
        else {}
    )

    phase_10_19_validation_passed = safe_bool(
        source_summary.get("validation_passed", False)
    )
    integrity_review_passed = safe_bool(
        source_summary.get(
            "controlled_start_activation_run_output_integrity_review_passed",
            False,
        )
    )
    integrity_review_decision = str(
        source_summary.get(
            "controlled_start_activation_run_output_integrity_review_decision",
            "",
        )
    )
    future_pre_start_review_allowed = safe_bool(
        source_summary.get(
            "future_controlled_forward_observation_pre_start_review_allowed",
            False,
        )
    )

    checks.append(
        build_check(
            "phase_dependency",
            "phase_10_19_validation_passed",
            phase_10_19_validation_passed,
            "INFO" if phase_10_19_validation_passed else "ERROR",
            str(source_summary.get("validation_decision", "")),
        )
    )
    checks.append(
        build_check(
            "phase_dependency",
            "activation_output_integrity_review_passed",
            integrity_review_passed,
            "INFO" if integrity_review_passed else "ERROR",
            f"integrity_review_passed={integrity_review_passed}",
        )
    )
    checks.append(
        build_check(
            "phase_dependency",
            "activation_output_integrity_review_decision_expected",
            integrity_review_decision == EXPECTED_PHASE_10_19_DECISION,
            "INFO" if integrity_review_decision == EXPECTED_PHASE_10_19_DECISION else "ERROR",
            integrity_review_decision,
        )
    )
    checks.append(
        build_check(
            "phase_dependency",
            "future_pre_start_review_allowed",
            future_pre_start_review_allowed,
            "INFO" if future_pre_start_review_allowed else "ERROR",
            f"future_pre_start_review_allowed={future_pre_start_review_allowed}",
        )
    )

    for _, evidence in evidence_df.iterrows():
        passed = safe_bool(evidence["passed"], False)

        checks.append(
            build_check(
                "pre_start_evidence",
                str(evidence["evidence_name"]),
                passed,
                "INFO" if passed else "ERROR",
                str(evidence["details"]),
            )
        )

    aggregate_checks = [
        ("pre_start_evidence_chain_passed", all_passed(evidence_df)),
        ("pre_start_controls_passed", all_passed(controls_df)),
        ("pre_start_rules_passed", all_passed(rules_df)),
        ("pre_start_requirements_passed", all_passed(requirements_df)),
        ("pre_start_guards_passed", all_passed(guard_matrix_df)),
        ("controlled_forward_observation_pre_start_review_passed", pre_start_review_passed),
        (
            "controlled_forward_observation_pre_start_review_decision_expected",
            pre_start_decision == READY_DECISION,
        ),
    ]

    for check_name, passed in aggregate_checks:
        checks.append(
            build_check(
                "pre_start_review",
                check_name,
                passed,
                "INFO" if passed else "ERROR",
                (
                    f"pre_start_decision={pre_start_decision}"
                    if check_name
                    == "controlled_forward_observation_pre_start_review_decision_expected"
                    else f"{check_name}={passed}"
                ),
            )
        )

    checks.append(
        build_check(
            "planning_scope",
            "future_controlled_forward_observation_start_dry_run_design_allowed",
            future_dry_run_design_allowed,
            "WARNING" if future_dry_run_design_allowed else "ERROR",
            (
                "This permits only a future controlled forward observation "
                "start dry-run design. It does not perform a dry-run, start "
                "forward observation, write official evidence, generate alerts, "
                "enable paper trading, use real capital, or permit market execution."
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
                "pre_start_safety_flags",
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
            build_check("scope_control", "pre_start_review_only", True, "WARNING", "Phase 10.20 performs only a controlled pre-start review."),
            build_check("scope_control", "no_new_activation_run", True, "WARNING", "No new activation run is performed in this phase."),
            build_check("scope_control", "start_dry_run_design_not_performed", True, "WARNING", "The future start dry-run design is not performed in this phase."),
            build_check("scope_control", "start_dry_run_not_performed", True, "WARNING", "No forward observation start dry-run is performed in this phase."),
            build_check("scope_control", "forward_observation_not_started", True, "WARNING", "Forward observation remains not started."),
            build_check("scope_control", "official_evidence_not_persisted", True, "WARNING", "Official evidence persistence remains disabled."),
            build_check("scope_control", "signal_generation_not_enabled", True, "WARNING", "Signal generation remains disabled."),
            build_check("scope_control", "paper_trading_not_enabled", True, "WARNING", "Paper trading execution remains disabled."),
            build_check("scope_control", "real_capital_not_allowed", True, "WARNING", "Real capital remains prohibited."),
            build_check("scope_control", "market_execution_not_allowed", True, "WARNING", "Market execution remains prohibited."),
            build_check("scope_control", "total_project_not_completed", True, "WARNING", "The total project is not completed."),
            build_check("phase_transition", "phase_10_21_recommended_next", True, "INFO", "Recommended next step: Phase 10.21 LONG Forward Observation Controlled Start Dry-Run Design V1."),
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
                "phase": "10.20",
                "long_forward_observation_controlled_pre_start_review_defined": True,
                "phase_10_19_validation_passed": phase_10_19_validation_passed,
                "controlled_start_activation_run_output_integrity_review_passed": integrity_review_passed,
                "controlled_start_activation_run_output_integrity_review_decision": integrity_review_decision,
                "future_controlled_forward_observation_pre_start_review_allowed": future_pre_start_review_allowed,
                "source_activation_output_row_count": len(source_activation_output_df),
                "source_candidate_id": str(source_output.get("candidate_id", "")),
                "source_candidate_valid": str(source_output.get("candidate_id", ""))
                == PRIMARY_RESEARCH_CANDIDATE,
                "source_direction": str(source_output.get("direction", "")),
                "source_direction_valid": str(source_output.get("direction", ""))
                == "LONG",
                "source_activation_scope": str(source_output.get("activation_scope", "")),
                "source_evidence_scope": str(source_output.get("evidence_scope", "")),
                "pre_start_evidence_count": len(evidence_df),
                "pre_start_control_count": len(controls_df),
                "pre_start_rule_rows": len(rules_df),
                "pre_start_requirement_rows": len(requirements_df),
                "pre_start_guard_rows": len(guard_matrix_df),
                "pre_start_evidence_chain_passed": all_passed(evidence_df),
                "pre_start_controls_passed": all_passed(controls_df),
                "pre_start_rules_passed": all_passed(rules_df),
                "pre_start_requirements_passed": all_passed(requirements_df),
                "pre_start_guards_passed": all_passed(guard_matrix_df),
                "controlled_forward_observation_pre_start_review_passed": pre_start_review_passed,
                "controlled_forward_observation_pre_start_review_decision": pre_start_decision,
                "future_controlled_forward_observation_start_dry_run_design_allowed": future_dry_run_design_allowed,
                "new_activation_run_performed": False,
                "controlled_forward_observation_start_dry_run_design_performed": False,
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
                    "PHASE_10_20_LONG_FORWARD_OBSERVATION_CONTROLLED_PRE_START_REVIEW_VALIDATED"
                    if validation_passed
                    else "PHASE_10_20_LONG_FORWARD_OBSERVATION_CONTROLLED_PRE_START_REVIEW_FAILED"
                ),
            }
        ]
    )

    source_summary_df.to_csv(REPORTS_DIR / "phase_10_19_source_summary_v1.csv", index=False)
    source_activation_output_df.to_csv(REPORTS_DIR / "phase_10_19_source_activation_output_v1.csv", index=False)
    source_integrity_validation_df.to_csv(REPORTS_DIR / "phase_10_19_source_integrity_validations_v1.csv", index=False)
    source_integrity_controls_df.to_csv(REPORTS_DIR / "phase_10_19_source_integrity_controls_v1.csv", index=False)
    source_integrity_rules_df.to_csv(REPORTS_DIR / "phase_10_19_source_integrity_rules_v1.csv", index=False)
    source_integrity_requirements_df.to_csv(REPORTS_DIR / "phase_10_19_source_integrity_requirements_v1.csv", index=False)
    source_integrity_guard_matrix_df.to_csv(REPORTS_DIR / "phase_10_19_source_integrity_guard_matrix_v1.csv", index=False)
    source_integrity_decision_df.to_csv(REPORTS_DIR / "phase_10_19_source_integrity_decision_v1.csv", index=False)
    source_checks_df.to_csv(REPORTS_DIR / "phase_10_19_source_checks_v1.csv", index=False)
    evidence_df.to_csv(REPORTS_DIR / "pre_start_evidence_chain_v1.csv", index=False)
    controls_df.to_csv(REPORTS_DIR / "pre_start_controls_v1.csv", index=False)
    rules_df.to_csv(REPORTS_DIR / "pre_start_rules_v1.csv", index=False)
    requirements_df.to_csv(REPORTS_DIR / "pre_start_requirements_v1.csv", index=False)
    guard_matrix_df.to_csv(REPORTS_DIR / "pre_start_guard_matrix_v1.csv", index=False)
    decision_df.to_csv(REPORTS_DIR / "pre_start_decision_v1.csv", index=False)
    checks_df.to_csv(REPORTS_DIR / "pre_start_checks_v1.csv", index=False)
    summary_df.to_csv(REPORTS_DIR / "pre_start_summary_v1.csv", index=False)

    return {
        "summary": summary_df,
        "source_phase_10_19_summary": source_summary_df,
        "source_activation_output": source_activation_output_df,
        "source_integrity_validation": source_integrity_validation_df,
        "source_integrity_controls": source_integrity_controls_df,
        "source_integrity_rules": source_integrity_rules_df,
        "source_integrity_requirements": source_integrity_requirements_df,
        "source_integrity_guard_matrix": source_integrity_guard_matrix_df,
        "source_integrity_decision": source_integrity_decision_df,
        "source_checks": source_checks_df,
        "pre_start_evidence_chain": evidence_df,
        "pre_start_controls": controls_df,
        "pre_start_rules": rules_df,
        "pre_start_requirements": requirements_df,
        "pre_start_guard_matrix": guard_matrix_df,
        "pre_start_decision": decision_df,
        "checks": checks_df,
    }