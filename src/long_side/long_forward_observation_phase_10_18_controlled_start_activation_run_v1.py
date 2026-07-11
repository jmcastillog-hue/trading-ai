from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

from src.long_side.long_forward_observation_dataset_bootstrap_v1 import (
    OFFICIAL_DATASET_PATH,
    PRIMARY_RESEARCH_CANDIDATE,
)
from src.long_side.long_forward_observation_phase_10_17_controlled_start_activation_final_approval_review_v1 import (
    READY_DECISION as FINAL_APPROVAL_READY_DECISION,
    validate_long_forward_observation_controlled_start_activation_final_approval_review,
)


REPORTS_DIR = Path("reports/p10_18_activation_run_v1")

PHASE_10_17_DOC_PATH = Path(
    "docs/PHASE_10_LONG_FORWARD_OBSERVATION_CONTROLLED_START_ACTIVATION_FINAL_APPROVAL_REVIEW.md"
)
PHASE_10_18_DOC_PATH = Path(
    "docs/PHASE_10_LONG_FORWARD_OBSERVATION_CONTROLLED_START_ACTIVATION_RUN.md"
)

ACTIVATION_OUTPUT_PATH = (
    REPORTS_DIR / "controlled_start_activation_run_output_v1.csv"
)

ACTIVATION_RUN_STATUS = (
    "LONG_FORWARD_OBSERVATION_CONTROLLED_START_ACTIVATION_RUN_CONTROL_PLANE_ONLY"
)

READY_DECISION = (
    "CONTROLLED_START_ACTIVATION_RUN_COMPLETED_CONTROL_PLANE_ONLY"
)
BLOCKED_DECISION = "CONTROLLED_START_ACTIVATION_RUN_BLOCKED"

RECOMMENDED_NEXT_PHASE = (
    "PHASE_10_19_LONG_FORWARD_OBSERVATION_CONTROLLED_START_ACTIVATION_RUN_"
    "OUTPUT_INTEGRITY_REVIEW_V1"
)

ACTIVATION_OUTPUT_COLUMNS = [
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

EXPECTED_FALSE_GUARDS = [
    "controlled_forward_observation_start_dry_run_performed",
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
]


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

    return bool(
        df["passed"]
        .map(lambda value: safe_bool(value, False))
        .all()
    )


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


def build_activation_output(
    phase_10_17_summary_df: pd.DataFrame,
) -> pd.DataFrame:
    summary = (
        phase_10_17_summary_df.iloc[0].to_dict()
        if not phase_10_17_summary_df.empty
        else {}
    )

    row = {
        "activation_run_id": (
            "PHASE_10_18_LONG_FORWARD_OBSERVATION_"
            "CONTROLLED_START_ACTIVATION_RUN_001"
        ),
        "activation_status": ACTIVATION_RUN_STATUS,
        "activated_at_utc": datetime.now(timezone.utc).isoformat(),
        "approval_source_phase": "10.17",
        "approval_source_validation_decision": str(
            summary.get("validation_decision", "")
        ),
        "approval_source_decision": str(
            summary.get(
                "controlled_start_activation_final_approval_review_decision",
                "",
            )
        ),
        "candidate_id": str(
            summary.get(
                "source_candidate_id",
                PRIMARY_RESEARCH_CANDIDATE,
            )
        ),
        "direction": str(summary.get("source_direction", "LONG")),
        "activation_scope": "CONTROL_PLANE_ONLY_NOT_FORWARD_OBSERVATION",
        "evidence_scope": "ACTIVATION_CONTROL_ONLY_NOT_REAL_EVIDENCE",
        "controlled_forward_observation_start_approved": True,
        "future_controlled_start_activation_run_allowed": True,
        "controlled_start_activation_allowed": True,
        "controlled_start_activation_performed": True,
        "controlled_forward_observation_start_activation_performed": True,
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
        "future_controlled_start_activation_run_output_integrity_review_allowed": True,
        "notes": (
            "Control-plane activation record only. "
            "Not forward observation. Not real evidence. "
            "Not a signal. Not market execution."
        ),
        "validation_status": "CONTROL_PLANE_ACTIVATION_ROW_CREATED",
    }

    return pd.DataFrame(
        [[row[column] for column in ACTIVATION_OUTPUT_COLUMNS]],
        columns=ACTIVATION_OUTPUT_COLUMNS,
    )


def validate_activation_output(
    output_df: pd.DataFrame,
) -> pd.DataFrame:
    row = output_df.iloc[0].to_dict() if len(output_df) == 1 else {}

    actual_columns = output_df.columns.astype(str).tolist()

    false_guards_valid = bool(row) and all(
        safe_bool(row.get(field_name, True), True) is False
        for field_name in EXPECTED_FALSE_GUARDS
    )

    validations = [
        (
            "activation_output_row_count_valid",
            len(output_df) == 1,
            f"row_count={len(output_df)}",
        ),
        (
            "activation_output_schema_valid",
            actual_columns == ACTIVATION_OUTPUT_COLUMNS,
            (
                f"actual_field_count={len(actual_columns)},"
                f"expected_field_count={len(ACTIVATION_OUTPUT_COLUMNS)}"
            ),
        ),
        (
            "activation_output_approval_decision_valid",
            str(row.get("approval_source_decision", ""))
            == FINAL_APPROVAL_READY_DECISION,
            str(row.get("approval_source_decision", "")),
        ),
        (
            "activation_output_candidate_valid",
            str(row.get("candidate_id", ""))
            == PRIMARY_RESEARCH_CANDIDATE,
            str(row.get("candidate_id", "")),
        ),
        (
            "activation_output_direction_valid",
            str(row.get("direction", "")) == "LONG",
            str(row.get("direction", "")),
        ),
        (
            "activation_output_control_plane_scope_valid",
            str(row.get("activation_scope", ""))
            == "CONTROL_PLANE_ONLY_NOT_FORWARD_OBSERVATION",
            str(row.get("activation_scope", "")),
        ),
        (
            "activation_output_evidence_scope_valid",
            str(row.get("evidence_scope", ""))
            == "ACTIVATION_CONTROL_ONLY_NOT_REAL_EVIDENCE",
            str(row.get("evidence_scope", "")),
        ),
        (
            "activation_output_start_approved",
            safe_bool(
                row.get(
                    "controlled_forward_observation_start_approved",
                    False,
                )
            ),
            str(
                row.get(
                    "controlled_forward_observation_start_approved",
                    "",
                )
            ),
        ),
        (
            "activation_output_activation_allowed",
            safe_bool(
                row.get("controlled_start_activation_allowed", False)
            ),
            str(row.get("controlled_start_activation_allowed", "")),
        ),
        (
            "activation_output_activation_performed",
            (
                safe_bool(
                    row.get(
                        "controlled_start_activation_performed",
                        False,
                    )
                )
                and safe_bool(
                    row.get(
                        "controlled_forward_observation_start_activation_performed",
                        False,
                    )
                )
            ),
            (
                f"control_activation="
                f"{row.get('controlled_start_activation_performed', '')},"
                f"forward_activation="
                f"{row.get('controlled_forward_observation_start_activation_performed', '')}"
            ),
        ),
        (
            "activation_output_operational_locks_valid",
            false_guards_valid,
            f"false_guard_count={len(EXPECTED_FALSE_GUARDS)}",
        ),
        (
            "activation_output_official_evidence_rows_zero",
            int(row.get("official_evidence_rows_written", -1)) == 0,
            str(row.get("official_evidence_rows_written", "")),
        ),
        (
            "activation_output_future_integrity_review_allowed",
            safe_bool(
                row.get(
                    "future_controlled_start_activation_run_output_integrity_review_allowed",
                    False,
                )
            ),
            str(
                row.get(
                    "future_controlled_start_activation_run_output_integrity_review_allowed",
                    "",
                )
            ),
        ),
    ]

    return pd.DataFrame(
        [
            {
                "validation_name": name,
                "passed": passed,
                "details": details,
            }
            for name, passed, details in validations
        ]
    )


def build_activation_controls(
    source_state: dict[str, bool],
    validation_df: pd.DataFrame,
    artifact_write_performed: bool,
) -> pd.DataFrame:
    validation_lookup = {
        str(row["validation_name"]): safe_bool(row["passed"], False)
        for _, row in validation_df.iterrows()
    }

    controls = [
        (
            "phase_10_17_validation_passed",
            source_state["phase_10_17_validation_passed"],
            "dependency",
        ),
        (
            "final_approval_review_passed",
            source_state["final_approval_review_passed"],
            "approval",
        ),
        (
            "final_approval_decision_expected",
            source_state["final_approval_decision_expected"],
            "approval",
        ),
        (
            "controlled_start_approved",
            source_state["controlled_start_approved"],
            "approval",
        ),
        (
            "future_activation_run_allowed",
            source_state["future_activation_run_allowed"],
            "approval",
        ),
        (
            "official_dataset_absent_before_run",
            source_state["official_dataset_absent_before_run"],
            "official_dataset_guard",
        ),
        (
            "activation_artifact_written",
            artifact_write_performed,
            "artifact",
        ),
        (
            "activation_output_row_count_valid",
            validation_lookup.get(
                "activation_output_row_count_valid",
                False,
            ),
            "artifact",
        ),
        (
            "activation_output_schema_valid",
            validation_lookup.get(
                "activation_output_schema_valid",
                False,
            ),
            "schema",
        ),
        (
            "activation_output_candidate_valid",
            validation_lookup.get(
                "activation_output_candidate_valid",
                False,
            ),
            "candidate_scope",
        ),
        (
            "activation_output_direction_valid",
            validation_lookup.get(
                "activation_output_direction_valid",
                False,
            ),
            "direction",
        ),
        (
            "activation_output_control_plane_scope_valid",
            validation_lookup.get(
                "activation_output_control_plane_scope_valid",
                False,
            ),
            "scope_control",
        ),
        (
            "activation_output_activation_performed",
            validation_lookup.get(
                "activation_output_activation_performed",
                False,
            ),
            "activation",
        ),
        (
            "activation_output_operational_locks_valid",
            validation_lookup.get(
                "activation_output_operational_locks_valid",
                False,
            ),
            "safety",
        ),
        (
            "official_evidence_rows_written_zero",
            validation_lookup.get(
                "activation_output_official_evidence_rows_zero",
                False,
            ),
            "official_dataset_guard",
        ),
        (
            "future_output_integrity_review_allowed",
            validation_lookup.get(
                "activation_output_future_integrity_review_allowed",
                False,
            ),
            "future_review",
        ),
    ]

    return pd.DataFrame(
        [
            {
                "control_id": f"ACTIVATION_RUN_CONTROL_{index:03d}",
                "control_name": name,
                "control_group": group,
                "required": True,
                "activation_run_control_plane_only": True,
                "forward_observation_start_allowed": False,
                "official_dataset_write_allowed": False,
                "market_execution_allowed": False,
                "passed": passed,
            }
            for index, (name, passed, group) in enumerate(
                controls,
                start=1,
            )
        ]
    )


def build_activation_guard_matrix(
    output_df: pd.DataFrame,
) -> pd.DataFrame:
    row = output_df.iloc[0].to_dict() if len(output_df) == 1 else {}

    guard_specs: list[tuple[str, Any]] = [
        ("controlled_forward_observation_start_approved", True),
        ("controlled_start_activation_allowed", True),
        ("controlled_start_activation_performed", True),
        (
            "controlled_forward_observation_start_activation_performed",
            True,
        ),
    ]

    guard_specs.extend(
        (guard_name, False)
        for guard_name in EXPECTED_FALSE_GUARDS
    )

    guard_specs.append(("official_evidence_rows_written", 0))

    rows: list[dict[str, Any]] = []

    for guard_name, required_value in guard_specs:
        actual_value = row.get(guard_name)

        if isinstance(required_value, bool):
            passed = safe_bool(
                actual_value,
                default=not required_value,
            ) is required_value
        else:
            try:
                passed = int(actual_value) == int(required_value)
            except (TypeError, ValueError):
                passed = False

        rows.append(
            {
                "guard_name": guard_name,
                "required_value": required_value,
                "actual_value": actual_value,
                "passed": passed,
                "guard_group": (
                    "activation_control_state"
                    if required_value is True
                    else "activation_run_safety_guard"
                ),
            }
        )

    return pd.DataFrame(rows)


def build_activation_rules(
    controls_df: pd.DataFrame,
    validation_df: pd.DataFrame,
    guard_matrix_df: pd.DataFrame,
) -> pd.DataFrame:
    controls_passed = all_passed(controls_df)
    validations_passed = all_passed(validation_df)
    guards_passed = all_passed(guard_matrix_df)

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

    rules = [
        (
            "activation_control_count_16",
            len(controls_df) == 16,
            "16",
            str(len(controls_df)),
            "controls",
        ),
        (
            "all_activation_controls_passed",
            controls_passed,
            "True",
            str(controls_passed),
            "controls",
        ),
        (
            "activation_validation_count_13",
            len(validation_df) == 13,
            "13",
            str(len(validation_df)),
            "validation",
        ),
        (
            "all_activation_validations_passed",
            validations_passed,
            "True",
            str(validations_passed),
            "validation",
        ),
        (
            "all_activation_guards_passed",
            guards_passed,
            "True",
            str(guards_passed),
            "safety",
        ),
        (
            "forward_observation_start_disabled",
            start_disabled,
            "False",
            "False",
            "start_boundary",
        ),
        (
            "official_dataset_writes_disabled",
            dataset_write_disabled,
            "False",
            "False",
            "official_dataset_guard",
        ),
        (
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
                "rule_id": f"ACTIVATION_RUN_RULE_{index:03d}",
                "rule_name": name,
                "passed": passed,
                "required_value": required,
                "actual_value": actual,
                "rule_group": group,
            }
            for index, (
                name,
                passed,
                required,
                actual,
                group,
            ) in enumerate(rules, start=1)
        ]
    )


def build_activation_requirements(
    controls_df: pd.DataFrame,
    rules_df: pd.DataFrame,
    guard_matrix_df: pd.DataFrame,
    official_dataset_absent_after: bool,
) -> pd.DataFrame:
    requirements: list[dict[str, Any]] = []

    for _, control in controls_df.iterrows():
        passed = safe_bool(control["passed"], False)

        requirements.append(
            {
                "requirement_id": (
                    f"ACTIVATION_RUN_REQ_{len(requirements) + 1:03d}"
                ),
                "requirement_name": str(control["control_name"]),
                "passed": passed,
                "required_value": "True",
                "actual_value": str(passed),
                "requirement_group": str(control["control_group"]),
            }
        )

    aggregate_requirements = [
        (
            "activation_rules_passed",
            all_passed(rules_df),
            "rules",
            "True",
        ),
        (
            "activation_guards_passed",
            all_passed(guard_matrix_df),
            "safety",
            "True",
        ),
        (
            "official_dataset_absent_after_run",
            official_dataset_absent_after,
            "official_dataset_guard",
            "True",
        ),
        (
            "forward_observation_not_started",
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

    for name, passed, group, actual_value in aggregate_requirements:
        requirements.append(
            {
                "requirement_id": (
                    f"ACTIVATION_RUN_REQ_{len(requirements) + 1:03d}"
                ),
                "requirement_name": name,
                "passed": passed,
                "required_value": actual_value,
                "actual_value": actual_value,
                "requirement_group": group,
            }
        )

    return pd.DataFrame(requirements)


def build_activation_decision(
    requirements_df: pd.DataFrame,
    rules_df: pd.DataFrame,
    guard_matrix_df: pd.DataFrame,
) -> pd.DataFrame:
    requirements_passed = all_passed(requirements_df)
    rules_passed = all_passed(rules_df)
    guards_passed = all_passed(guard_matrix_df)

    run_passed = (
        requirements_passed
        and rules_passed
        and guards_passed
    )

    failed_names = ",".join(
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
                "controlled_start_activation_run_id": (
                    "PHASE_10_18_LONG_FORWARD_OBSERVATION_"
                    "CONTROLLED_START_ACTIVATION_RUN_001"
                ),
                "controlled_start_activation_run_status": (
                    ACTIVATION_RUN_STATUS
                ),
                "controlled_start_activation_run_passed": run_passed,
                "controlled_start_activation_run_decision": (
                    READY_DECISION if run_passed else BLOCKED_DECISION
                ),
                "total_requirements": len(requirements_df),
                "passed_requirements": int(
                    requirements_df["passed"]
                    .map(lambda value: safe_bool(value, False))
                    .sum()
                ),
                "failed_requirements": int(
                    len(requirements_df)
                    - requirements_df["passed"]
                    .map(lambda value: safe_bool(value, False))
                    .sum()
                ),
                "failed_requirement_names": failed_names,
                "activation_rules_passed": rules_passed,
                "activation_guards_passed": guards_passed,
                "controlled_forward_observation_start_approved": run_passed,
                "controlled_start_activation_allowed": run_passed,
                "controlled_start_activation_performed": run_passed,
                "controlled_forward_observation_start_activation_performed": run_passed,
                "future_controlled_start_activation_run_output_integrity_review_allowed": run_passed,
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


def validate_long_forward_observation_controlled_start_activation_run(
) -> dict[str, pd.DataFrame]:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    checks: list[dict[str, Any]] = []

    for check_name, path in {
        "phase_10_17_final_approval_doc_exists": PHASE_10_17_DOC_PATH,
        "phase_10_18_activation_run_doc_exists": PHASE_10_18_DOC_PATH,
    }.items():
        exists = path.exists()

        checks.append(
            build_check(
                "phase_anchor",
                check_name,
                exists,
                "INFO" if exists else "ERROR",
                str(path),
            )
        )

    official_dataset_exists_before = OFFICIAL_DATASET_PATH.exists()

    phase_10_17_result = (
        validate_long_forward_observation_controlled_start_activation_final_approval_review()
    )

    source_summary_df = phase_10_17_result["summary"]
    source_decision_df = phase_10_17_result["final_approval_decision"]
    source_evidence_df = phase_10_17_result[
        "final_approval_evidence_chain"
    ]
    source_controls_df = phase_10_17_result["final_approval_controls"]
    source_rules_df = phase_10_17_result["final_approval_rules"]
    source_requirements_df = phase_10_17_result[
        "final_approval_requirements"
    ]
    source_guard_matrix_df = phase_10_17_result[
        "final_approval_guard_matrix"
    ]
    source_checks_df = phase_10_17_result["checks"]

    source_summary = (
        source_summary_df.iloc[0].to_dict()
        if not source_summary_df.empty
        else {}
    )

    phase_10_17_validation_passed = safe_bool(
        source_summary.get("validation_passed", False)
    )
    final_approval_review_passed = safe_bool(
        source_summary.get(
            "controlled_start_activation_final_approval_review_passed",
            False,
        )
    )
    final_approval_decision_expected = (
        str(
            source_summary.get(
                "controlled_start_activation_final_approval_review_decision",
                "",
            )
        )
        == FINAL_APPROVAL_READY_DECISION
    )
    controlled_start_approved = safe_bool(
        source_summary.get(
            "controlled_forward_observation_start_approved",
            False,
        )
    )
    future_activation_run_allowed = safe_bool(
        source_summary.get(
            "future_controlled_start_activation_run_allowed",
            False,
        )
    )

    approved_to_run = all(
        [
            phase_10_17_validation_passed,
            final_approval_review_passed,
            final_approval_decision_expected,
            controlled_start_approved,
            future_activation_run_allowed,
            official_dataset_exists_before is False,
        ]
    )

    output_df = pd.DataFrame(columns=ACTIVATION_OUTPUT_COLUMNS)
    artifact_write_performed = False
    artifact_rows_written = 0

    if approved_to_run:
        output_df = build_activation_output(source_summary_df)
        output_df.to_csv(ACTIVATION_OUTPUT_PATH, index=False)
        artifact_write_performed = ACTIVATION_OUTPUT_PATH.exists()
        artifact_rows_written = len(output_df)

    persisted_output_df = (
        pd.read_csv(ACTIVATION_OUTPUT_PATH)
        if ACTIVATION_OUTPUT_PATH.exists()
        else output_df
    )

    validation_df = validate_activation_output(persisted_output_df)

    source_state = {
        "phase_10_17_validation_passed": phase_10_17_validation_passed,
        "final_approval_review_passed": final_approval_review_passed,
        "final_approval_decision_expected": final_approval_decision_expected,
        "controlled_start_approved": controlled_start_approved,
        "future_activation_run_allowed": future_activation_run_allowed,
        "official_dataset_absent_before_run": (
            official_dataset_exists_before is False
        ),
    }

    controls_df = build_activation_controls(
        source_state=source_state,
        validation_df=validation_df,
        artifact_write_performed=artifact_write_performed,
    )

    guard_matrix_df = build_activation_guard_matrix(
        persisted_output_df
    )

    rules_df = build_activation_rules(
        controls_df=controls_df,
        validation_df=validation_df,
        guard_matrix_df=guard_matrix_df,
    )

    official_dataset_exists_after = OFFICIAL_DATASET_PATH.exists()

    requirements_df = build_activation_requirements(
        controls_df=controls_df,
        rules_df=rules_df,
        guard_matrix_df=guard_matrix_df,
        official_dataset_absent_after=(
            official_dataset_exists_after is False
        ),
    )

    decision_df = build_activation_decision(
        requirements_df=requirements_df,
        rules_df=rules_df,
        guard_matrix_df=guard_matrix_df,
    )

    decision = (
        decision_df.iloc[0].to_dict()
        if not decision_df.empty
        else {}
    )

    activation_run_passed = safe_bool(
        decision.get("controlled_start_activation_run_passed", False)
    )
    activation_run_decision = str(
        decision.get("controlled_start_activation_run_decision", "")
    )
    activation_performed = safe_bool(
        decision.get("controlled_start_activation_performed", False)
    )
    forward_activation_performed = safe_bool(
        decision.get(
            "controlled_forward_observation_start_activation_performed",
            False,
        )
    )
    future_integrity_review_allowed = safe_bool(
        decision.get(
            "future_controlled_start_activation_run_output_integrity_review_allowed",
            False,
        )
    )

    validation_lookup = {
        str(row["validation_name"]): safe_bool(row["passed"], False)
        for _, row in validation_df.iterrows()
    }

    dependency_checks = [
        (
            "phase_10_17_validation_passed",
            phase_10_17_validation_passed,
            str(source_summary.get("validation_decision", "")),
        ),
        (
            "final_approval_review_passed",
            final_approval_review_passed,
            str(final_approval_review_passed),
        ),
        (
            "final_approval_decision_expected",
            final_approval_decision_expected,
            str(
                source_summary.get(
                    "controlled_start_activation_final_approval_review_decision",
                    "",
                )
            ),
        ),
        (
            "controlled_start_approved",
            controlled_start_approved,
            str(controlled_start_approved),
        ),
        (
            "future_activation_run_allowed",
            future_activation_run_allowed,
            str(future_activation_run_allowed),
        ),
    ]

    for name, passed, details in dependency_checks:
        checks.append(
            build_check(
                "phase_dependency",
                name,
                passed,
                "INFO" if passed else "ERROR",
                details,
            )
        )

    checks.append(
        build_check(
            "activation_artifact",
            "activation_artifact_write_performed",
            artifact_write_performed,
            "INFO" if artifact_write_performed else "ERROR",
            str(ACTIVATION_OUTPUT_PATH),
        )
    )
    checks.append(
        build_check(
            "activation_artifact",
            "activation_artifact_rows_written_one",
            artifact_rows_written == 1,
            "INFO" if artifact_rows_written == 1 else "ERROR",
            f"rows_written={artifact_rows_written}",
        )
    )

    for name, passed in validation_lookup.items():
        checks.append(
            build_check(
                "activation_output_validation",
                name,
                passed,
                "INFO" if passed else "ERROR",
                str(passed),
            )
        )

    aggregate_checks = [
        ("activation_controls_passed", all_passed(controls_df)),
        ("activation_rules_passed", all_passed(rules_df)),
        (
            "activation_requirements_passed",
            all_passed(requirements_df),
        ),
        ("activation_guards_passed", all_passed(guard_matrix_df)),
        ("controlled_start_activation_run_passed", activation_run_passed),
        (
            "controlled_start_activation_run_decision_expected",
            activation_run_decision == READY_DECISION,
        ),
        ("controlled_start_activation_performed", activation_performed),
        (
            "controlled_forward_observation_start_activation_performed",
            forward_activation_performed,
        ),
    ]

    for name, passed in aggregate_checks:
        checks.append(
            build_check(
                "activation_run",
                name,
                passed,
                "INFO" if passed else "ERROR",
                (
                    f"decision={activation_run_decision}"
                    if name.endswith("decision_expected")
                    else f"{name}={passed}"
                ),
            )
        )

    checks.append(
        build_check(
            "planning_scope",
            "future_activation_output_integrity_review_allowed",
            future_integrity_review_allowed,
            "WARNING" if future_integrity_review_allowed else "ERROR",
            (
                "This permits only a future integrity review of the "
                "control-plane activation output."
            ),
        )
    )

    official_dataset_absent = (
        official_dataset_exists_before is False
        and official_dataset_exists_after is False
    )

    checks.append(
        build_check(
            "official_dataset_guard",
            "official_dataset_not_created_or_written",
            official_dataset_absent,
            "INFO" if official_dataset_absent else "ERROR",
            (
                f"before={official_dataset_exists_before},"
                f"after={official_dataset_exists_after}"
            ),
        )
    )

    for _, guard in guard_matrix_df.iterrows():
        passed = safe_bool(guard["passed"], False)

        checks.append(
            build_check(
                "activation_run_safety_flags",
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
                "activation_control_plane_only",
                True,
                "WARNING",
                "Activation is limited to the project control plane.",
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
                "phase_10_19_recommended_next",
                True,
                "INFO",
                (
                    "Recommended next step: Phase 10.19 LONG Forward "
                    "Observation Controlled Start Activation Run Output "
                    "Integrity Review V1."
                ),
            ),
        ]
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

    summary_df = pd.DataFrame(
        [
            {
                "phase": "10.18",
                "long_forward_observation_controlled_start_activation_run_defined": True,
                "phase_10_17_validation_passed": phase_10_17_validation_passed,
                "controlled_start_activation_final_approval_review_passed": final_approval_review_passed,
                "controlled_start_activation_final_approval_review_decision": str(
                    source_summary.get(
                        "controlled_start_activation_final_approval_review_decision",
                        "",
                    )
                ),
                "controlled_forward_observation_start_approved": controlled_start_approved,
                "future_controlled_start_activation_run_allowed": future_activation_run_allowed,
                "controlled_start_activation_allowed": activation_run_passed,
                "controlled_start_activation_performed": activation_performed,
                "controlled_forward_observation_start_activation_performed": forward_activation_performed,
                "activation_output_row_count": len(persisted_output_df),
                "activation_output_schema_valid": validation_lookup.get(
                    "activation_output_schema_valid",
                    False,
                ),
                "activation_output_candidate_valid": validation_lookup.get(
                    "activation_output_candidate_valid",
                    False,
                ),
                "activation_output_direction_valid": validation_lookup.get(
                    "activation_output_direction_valid",
                    False,
                ),
                "activation_output_control_plane_scope_valid": validation_lookup.get(
                    "activation_output_control_plane_scope_valid",
                    False,
                ),
                "activation_output_safety_guards_passed": validation_lookup.get(
                    "activation_output_operational_locks_valid",
                    False,
                ),
                "activation_artifact_write_performed": artifact_write_performed,
                "activation_artifact_rows_written": artifact_rows_written,
                "activation_control_count": len(controls_df),
                "activation_validation_rows": len(validation_df),
                "activation_rule_rows": len(rules_df),
                "activation_requirement_rows": len(requirements_df),
                "activation_guard_rows": len(guard_matrix_df),
                "activation_controls_passed": all_passed(controls_df),
                "activation_validations_passed": all_passed(validation_df),
                "activation_rules_passed": all_passed(rules_df),
                "activation_requirements_passed": all_passed(
                    requirements_df
                ),
                "activation_guards_passed": all_passed(guard_matrix_df),
                "controlled_start_activation_run_passed": activation_run_passed,
                "controlled_start_activation_run_decision": activation_run_decision,
                "future_controlled_start_activation_run_output_integrity_review_allowed": future_integrity_review_allowed,
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
                    "PHASE_10_18_LONG_FORWARD_OBSERVATION_"
                    "CONTROLLED_START_ACTIVATION_RUN_VALIDATED"
                    if validation_passed
                    else
                    "PHASE_10_18_LONG_FORWARD_OBSERVATION_"
                    "CONTROLLED_START_ACTIVATION_RUN_FAILED"
                ),
            }
        ]
    )

    source_summary_df.to_csv(
        REPORTS_DIR / "phase_10_17_source_summary_v1.csv",
        index=False,
    )
    source_decision_df.to_csv(
        REPORTS_DIR / "phase_10_17_source_final_approval_decision_v1.csv",
        index=False,
    )
    source_evidence_df.to_csv(
        REPORTS_DIR / "phase_10_17_source_approval_evidence_v1.csv",
        index=False,
    )
    source_controls_df.to_csv(
        REPORTS_DIR / "phase_10_17_source_approval_controls_v1.csv",
        index=False,
    )
    source_rules_df.to_csv(
        REPORTS_DIR / "phase_10_17_source_approval_rules_v1.csv",
        index=False,
    )
    source_requirements_df.to_csv(
        REPORTS_DIR / "phase_10_17_source_approval_requirements_v1.csv",
        index=False,
    )
    source_guard_matrix_df.to_csv(
        REPORTS_DIR / "phase_10_17_source_approval_guard_matrix_v1.csv",
        index=False,
    )
    source_checks_df.to_csv(
        REPORTS_DIR / "phase_10_17_source_checks_v1.csv",
        index=False,
    )
    persisted_output_df.to_csv(
        REPORTS_DIR / "controlled_start_activation_run_output_v1.csv",
        index=False,
    )
    validation_df.to_csv(
        REPORTS_DIR / "activation_run_validations_v1.csv",
        index=False,
    )
    controls_df.to_csv(
        REPORTS_DIR / "activation_run_controls_v1.csv",
        index=False,
    )
    rules_df.to_csv(
        REPORTS_DIR / "activation_run_rules_v1.csv",
        index=False,
    )
    requirements_df.to_csv(
        REPORTS_DIR / "activation_run_requirements_v1.csv",
        index=False,
    )
    guard_matrix_df.to_csv(
        REPORTS_DIR / "activation_run_guard_matrix_v1.csv",
        index=False,
    )
    decision_df.to_csv(
        REPORTS_DIR / "activation_run_decision_v1.csv",
        index=False,
    )
    checks_df.to_csv(
        REPORTS_DIR / "activation_run_checks_v1.csv",
        index=False,
    )
    summary_df.to_csv(
        REPORTS_DIR / "activation_run_summary_v1.csv",
        index=False,
    )

    return {
        "summary": summary_df,
        "source_phase_10_17_summary": source_summary_df,
        "source_final_approval_decision": source_decision_df,
        "source_final_approval_evidence": source_evidence_df,
        "source_final_approval_controls": source_controls_df,
        "source_final_approval_rules": source_rules_df,
        "source_final_approval_requirements": source_requirements_df,
        "source_final_approval_guard_matrix": source_guard_matrix_df,
        "source_checks": source_checks_df,
        "activation_output": persisted_output_df,
        "activation_validation": validation_df,
        "activation_controls": controls_df,
        "activation_rules": rules_df,
        "activation_requirements": requirements_df,
        "activation_guard_matrix": guard_matrix_df,
        "activation_decision": decision_df,
        "checks": checks_df,
    }