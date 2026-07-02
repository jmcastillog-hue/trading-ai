from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from src.long_side.long_forward_observation_dataset_bootstrap_v1 import (
    DATASET_COLUMNS,
    OFFICIAL_DATASET_PATH,
    PRIMARY_RESEARCH_CANDIDATE,
)
from src.long_side.long_forward_observation_controlled_dataset_write_v1 import (
    validate_long_forward_observation_controlled_dataset_write,
)


REPORTS_DIR = Path("reports/phase_9_8_long_forward_observation_report_integrity_v1")

PHASE_9_7_CONTROLLED_DATASET_WRITE_DOC_PATH = Path(
    "docs/PHASE_9_LONG_FORWARD_OBSERVATION_CONTROLLED_DATASET_WRITE.md"
)
PHASE_9_8_REPORT_INTEGRITY_DOC_PATH = Path(
    "docs/PHASE_9_LONG_FORWARD_OBSERVATION_REPORT_INTEGRITY.md"
)

REPORT_INTEGRITY_STATUS = "LONG_FORWARD_OBSERVATION_REPORT_INTEGRITY_ONLY"

REQUIRED_PROVENANCE_COLUMNS = [
    "source_validation_decision",
    "source_validation_status",
    "source_bootstrap_action",
    "source_bootstrap_decision",
]

REQUIRED_CONTROLLED_WRITE_COLUMNS = [
    "controlled_write_id",
    "controlled_write_status",
    "controlled_write_scope",
    "controlled_report_write_allowed",
    "controlled_report_write_performed",
    "official_dataset_write_allowed",
    "official_dataset_write_performed",
    "official_dataset_path",
    "controlled_report_path",
    "controlled_write_note",
]

REQUIRED_SAFETY_COLUMNS = [
    "accepted_as_real_evidence",
    "evidence_write_allowed",
    "evidence_write_performed",
    "forward_observation_started",
    "signal_generation_enabled",
    "execution_allowed",
    "live_alert_sent",
    "paper_trade_submitted",
    "real_capital_used",
]

SAFETY_FLAGS = {
    "forward_observation_started": False,
    "signal_generation_enabled": False,
    "real_forward_signals_recorded": False,
    "journal_real_rows_accepted": False,
    "real_forward_dataset_created": False,
    "official_dataset_write_performed": False,
    "evidence_write_performed": False,
    "evidence_persistence_allowed": False,
    "accepted_as_real_evidence": False,
    "paper_trading_enabled": False,
    "long_strategy_approved": False,
    "long_entries_approved": False,
    "long_side_established": False,
    "paper_trade_execution_allowed": False,
    "real_capital_allowed": False,
    "live_alerts_allowed": False,
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


def build_schema_integrity_audit(
    controlled_report_write_df: pd.DataFrame,
) -> pd.DataFrame:
    available_columns = set(controlled_report_write_df.columns.astype(str).tolist())

    required_groups = {
        "dataset_columns": DATASET_COLUMNS,
        "provenance_columns": REQUIRED_PROVENANCE_COLUMNS,
        "controlled_write_columns": REQUIRED_CONTROLLED_WRITE_COLUMNS,
        "safety_columns": REQUIRED_SAFETY_COLUMNS,
    }

    rows: list[dict[str, Any]] = []

    for group_name, required_columns in required_groups.items():
        missing_columns = sorted(set(required_columns) - available_columns)

        rows.append(
            {
                "integrity_group": "schema",
                "audit_check": f"{group_name}_present",
                "passed": len(missing_columns) == 0,
                "required_column_count": len(required_columns),
                "missing_column_count": len(missing_columns),
                "missing_columns": ",".join(missing_columns),
                "details": f"{group_name} required={len(required_columns)}",
            }
        )

    rows.append(
        {
            "integrity_group": "schema",
            "audit_check": "controlled_report_has_single_row",
            "passed": len(controlled_report_write_df) == 1,
            "required_column_count": 0,
            "missing_column_count": 0,
            "missing_columns": "",
            "details": f"controlled_report_write_rows={len(controlled_report_write_df)}",
        }
    )

    return pd.DataFrame(rows)


def build_provenance_integrity_audit(
    controlled_report_write_df: pd.DataFrame,
) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []

    if controlled_report_write_df.empty:
        return pd.DataFrame(
            [
                {
                    "integrity_group": "provenance",
                    "audit_check": "controlled_report_row_exists_for_provenance",
                    "passed": False,
                    "details": "controlled_report_write_df is empty",
                }
            ]
        )

    row = controlled_report_write_df.iloc[0]

    provenance_fields = {
        "source_validation_decision": str(
            row.get("source_validation_decision", "")
        ).strip(),
        "source_validation_status": str(
            row.get("source_validation_status", "")
        ).strip(),
        "source_bootstrap_action": str(row.get("source_bootstrap_action", "")).strip(),
        "source_bootstrap_decision": str(
            row.get("source_bootstrap_decision", "")
        ).strip(),
        "controlled_write_id": str(row.get("controlled_write_id", "")).strip(),
        "controlled_write_status": str(
            row.get("controlled_write_status", "")
        ).strip(),
        "controlled_write_scope": str(row.get("controlled_write_scope", "")).strip(),
        "controlled_report_path": str(row.get("controlled_report_path", "")).strip(),
        "official_dataset_path": str(row.get("official_dataset_path", "")).strip(),
    }

    for field_name, field_value in provenance_fields.items():
        rows.append(
            {
                "integrity_group": "provenance",
                "audit_check": f"{field_name}_not_empty",
                "passed": field_value != "",
                "details": f"{field_name}={field_value}",
            }
        )

    expected_decision = "VALIDATED_FOR_FUTURE_FORWARD_OBSERVATION_INPUT"
    expected_status_prefix = "CONTROLLED_VALID_INPUT_ONLY"
    expected_scope = "REPORTS_ONLY_NOT_OFFICIAL_DATASET"

    rows.append(
        {
            "integrity_group": "provenance",
            "audit_check": "source_validation_decision_expected",
            "passed": provenance_fields["source_validation_decision"] == expected_decision,
            "details": (
                "source_validation_decision="
                + provenance_fields["source_validation_decision"]
            ),
        }
    )

    rows.append(
        {
            "integrity_group": "provenance",
            "audit_check": "source_validation_status_expected",
            "passed": provenance_fields["source_validation_status"].startswith(
                expected_status_prefix
            ),
            "details": (
                "source_validation_status="
                + provenance_fields["source_validation_status"]
            ),
        }
    )

    rows.append(
        {
            "integrity_group": "provenance",
            "audit_check": "controlled_write_scope_report_only",
            "passed": provenance_fields["controlled_write_scope"] == expected_scope,
            "details": "controlled_write_scope=" + provenance_fields["controlled_write_scope"],
        }
    )

    return pd.DataFrame(rows)


def build_safety_integrity_audit(
    controlled_report_write_df: pd.DataFrame,
) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []

    if controlled_report_write_df.empty:
        return pd.DataFrame(
            [
                {
                    "integrity_group": "safety",
                    "audit_check": "controlled_report_row_exists_for_safety",
                    "passed": False,
                    "details": "controlled_report_write_df is empty",
                }
            ]
        )

    row = controlled_report_write_df.iloc[0]

    expected_false_fields = [
        "accepted_as_real_evidence",
        "evidence_write_allowed",
        "evidence_write_performed",
        "forward_observation_started",
        "signal_generation_enabled",
        "execution_allowed",
        "live_alert_sent",
        "paper_trade_submitted",
        "real_capital_used",
        "official_dataset_write_performed",
    ]

    for field_name in expected_false_fields:
        value = safe_bool(row.get(field_name, True), default=True)

        rows.append(
            {
                "integrity_group": "safety",
                "audit_check": f"{field_name}_false",
                "passed": value is False,
                "details": f"{field_name}={value}",
            }
        )

    candidate_id = str(row.get("candidate_id", "")).strip()
    direction = str(row.get("direction", "")).strip()
    observation_role = str(row.get("observation_role", "")).strip()

    rows.append(
        {
            "integrity_group": "safety",
            "audit_check": "candidate_is_primary_research_candidate",
            "passed": candidate_id == PRIMARY_RESEARCH_CANDIDATE,
            "details": f"candidate_id={candidate_id}",
        }
    )

    rows.append(
        {
            "integrity_group": "safety",
            "audit_check": "direction_is_long",
            "passed": direction == "LONG",
            "details": f"direction={direction}",
        }
    )

    rows.append(
        {
            "integrity_group": "safety",
            "audit_check": "observation_role_is_primary",
            "passed": observation_role == "PRIMARY_FORWARD_OBSERVATION",
            "details": f"observation_role={observation_role}",
        }
    )

    return pd.DataFrame(rows)


def build_report_only_integrity_audit(
    controlled_report_write_df: pd.DataFrame,
    official_dataset_exists_before: bool,
    official_dataset_exists_after: bool,
) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []

    if controlled_report_write_df.empty:
        return pd.DataFrame(
            [
                {
                    "integrity_group": "report_only",
                    "audit_check": "controlled_report_row_exists_for_report_only_check",
                    "passed": False,
                    "details": "controlled_report_write_df is empty",
                }
            ]
        )

    row = controlled_report_write_df.iloc[0]

    controlled_report_path = str(row.get("controlled_report_path", "")).strip()
    official_dataset_path = str(row.get("official_dataset_path", "")).strip()
    controlled_write_scope = str(row.get("controlled_write_scope", "")).strip()

    controlled_report_write_performed = safe_bool(
        row.get("controlled_report_write_performed", False)
    )
    official_dataset_write_performed = safe_bool(
        row.get("official_dataset_write_performed", True),
        default=True,
    )
    official_dataset_write_allowed = safe_bool(
        row.get("official_dataset_write_allowed", True),
        default=True,
    )

    rows.append(
        {
            "integrity_group": "report_only",
            "audit_check": "controlled_report_path_under_reports",
            "passed": controlled_report_path.startswith("reports"),
            "details": f"controlled_report_path={controlled_report_path}",
        }
    )

    rows.append(
        {
            "integrity_group": "report_only",
            "audit_check": "official_dataset_path_matches_expected",
            "passed": official_dataset_path == str(OFFICIAL_DATASET_PATH),
            "details": f"official_dataset_path={official_dataset_path}",
        }
    )

    rows.append(
        {
            "integrity_group": "report_only",
            "audit_check": "controlled_write_scope_report_only",
            "passed": controlled_write_scope == "REPORTS_ONLY_NOT_OFFICIAL_DATASET",
            "details": f"controlled_write_scope={controlled_write_scope}",
        }
    )

    rows.append(
        {
            "integrity_group": "report_only",
            "audit_check": "controlled_report_write_performed",
            "passed": controlled_report_write_performed,
            "details": f"controlled_report_write_performed={controlled_report_write_performed}",
        }
    )

    rows.append(
        {
            "integrity_group": "report_only",
            "audit_check": "official_dataset_write_not_allowed",
            "passed": not official_dataset_write_allowed,
            "details": f"official_dataset_write_allowed={official_dataset_write_allowed}",
        }
    )

    rows.append(
        {
            "integrity_group": "report_only",
            "audit_check": "official_dataset_write_not_performed",
            "passed": not official_dataset_write_performed,
            "details": f"official_dataset_write_performed={official_dataset_write_performed}",
        }
    )

    rows.append(
        {
            "integrity_group": "report_only",
            "audit_check": "official_dataset_file_not_created",
            "passed": (
                official_dataset_exists_before is False
                and official_dataset_exists_after is False
            ),
            "details": (
                f"official_dataset_exists_before={official_dataset_exists_before},"
                f"official_dataset_exists_after={official_dataset_exists_after}"
            ),
        }
    )

    return pd.DataFrame(rows)


def combine_integrity_audits(
    schema_audit_df: pd.DataFrame,
    provenance_audit_df: pd.DataFrame,
    safety_audit_df: pd.DataFrame,
    report_only_audit_df: pd.DataFrame,
) -> pd.DataFrame:
    return pd.concat(
        [
            schema_audit_df,
            provenance_audit_df,
            safety_audit_df,
            report_only_audit_df,
        ],
        ignore_index=True,
    )


def build_report_integrity_summary_table(
    controlled_report_write_df: pd.DataFrame,
    schema_audit_df: pd.DataFrame,
    provenance_audit_df: pd.DataFrame,
    safety_audit_df: pd.DataFrame,
    report_only_audit_df: pd.DataFrame,
    combined_audit_df: pd.DataFrame,
    official_dataset_exists_before: bool,
    official_dataset_exists_after: bool,
) -> pd.DataFrame:
    schema_compatibility_passed = (
        not schema_audit_df.empty and schema_audit_df["passed"].astype(bool).all()
    )
    provenance_integrity_passed = (
        not provenance_audit_df.empty and provenance_audit_df["passed"].astype(bool).all()
    )
    safety_integrity_passed = (
        not safety_audit_df.empty and safety_audit_df["passed"].astype(bool).all()
    )
    report_only_integrity_passed = (
        not report_only_audit_df.empty and report_only_audit_df["passed"].astype(bool).all()
    )
    report_integrity_audit_passed = (
        not combined_audit_df.empty and combined_audit_df["passed"].astype(bool).all()
    )

    controlled_report_write_rows = int(len(controlled_report_write_df))
    controlled_row_source_candidate = ""

    if not controlled_report_write_df.empty:
        controlled_row_source_candidate = str(
            controlled_report_write_df.iloc[0].get("candidate_id", "")
        ).strip()

    return pd.DataFrame(
        [
            {
                "report_integrity_id": "PHASE_9_8_REPORT_INTEGRITY_001",
                "report_integrity_status": REPORT_INTEGRITY_STATUS,
                "controlled_report_write_rows": controlled_report_write_rows,
                "controlled_report_write_only": True,
                "controlled_row_source_candidate": controlled_row_source_candidate,
                "schema_compatibility_passed": schema_compatibility_passed,
                "provenance_integrity_passed": provenance_integrity_passed,
                "safety_integrity_passed": safety_integrity_passed,
                "report_only_integrity_passed": report_only_integrity_passed,
                "report_integrity_audit_rows": int(len(combined_audit_df)),
                "report_integrity_audit_passed": report_integrity_audit_passed,
                "official_dataset_path": str(OFFICIAL_DATASET_PATH),
                "official_dataset_exists_before": official_dataset_exists_before,
                "official_dataset_exists_after": official_dataset_exists_after,
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
                "execution_allowed": False,
                "live_alerts_allowed": False,
                "real_capital_allowed": False,
                "automation_allowed": False,
            }
        ]
    )


def validate_long_forward_observation_report_integrity() -> dict[str, pd.DataFrame]:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    checks: list[dict[str, Any]] = []

    phase_anchors = {
        "phase_9_7_controlled_dataset_write_doc_exists": (
            PHASE_9_7_CONTROLLED_DATASET_WRITE_DOC_PATH
        ),
        "phase_9_8_report_integrity_doc_exists": PHASE_9_8_REPORT_INTEGRITY_DOC_PATH,
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

    phase_9_7_result = validate_long_forward_observation_controlled_dataset_write()

    phase_9_7_summary_df = phase_9_7_result["summary"]
    source_controlled_report_write_df = phase_9_7_result["controlled_report_write"]
    source_controlled_write_audit_df = phase_9_7_result["controlled_write_audit"]
    source_controlled_dataset_write_summary_df = phase_9_7_result[
        "controlled_dataset_write_summary"
    ]

    phase_9_7_validation_passed = (
        not phase_9_7_summary_df.empty
        and bool(phase_9_7_summary_df.iloc[0].get("validation_passed", False))
    )

    controlled_dataset_write_defined = (
        not phase_9_7_summary_df.empty
        and bool(
            phase_9_7_summary_df.iloc[0].get(
                "long_forward_observation_controlled_dataset_write_defined",
                False,
            )
        )
    )

    official_dataset_exists_after = OFFICIAL_DATASET_PATH.exists()

    schema_audit_df = build_schema_integrity_audit(
        controlled_report_write_df=source_controlled_report_write_df,
    )
    provenance_audit_df = build_provenance_integrity_audit(
        controlled_report_write_df=source_controlled_report_write_df,
    )
    safety_audit_df = build_safety_integrity_audit(
        controlled_report_write_df=source_controlled_report_write_df,
    )
    report_only_audit_df = build_report_only_integrity_audit(
        controlled_report_write_df=source_controlled_report_write_df,
        official_dataset_exists_before=official_dataset_exists_before,
        official_dataset_exists_after=official_dataset_exists_after,
    )

    combined_integrity_audit_df = combine_integrity_audits(
        schema_audit_df=schema_audit_df,
        provenance_audit_df=provenance_audit_df,
        safety_audit_df=safety_audit_df,
        report_only_audit_df=report_only_audit_df,
    )

    report_integrity_summary_table_df = build_report_integrity_summary_table(
        controlled_report_write_df=source_controlled_report_write_df,
        schema_audit_df=schema_audit_df,
        provenance_audit_df=provenance_audit_df,
        safety_audit_df=safety_audit_df,
        report_only_audit_df=report_only_audit_df,
        combined_audit_df=combined_integrity_audit_df,
        official_dataset_exists_before=official_dataset_exists_before,
        official_dataset_exists_after=official_dataset_exists_after,
    )

    schema_compatibility_passed = (
        not schema_audit_df.empty and schema_audit_df["passed"].astype(bool).all()
    )
    provenance_integrity_passed = (
        not provenance_audit_df.empty and provenance_audit_df["passed"].astype(bool).all()
    )
    safety_integrity_passed = (
        not safety_audit_df.empty and safety_audit_df["passed"].astype(bool).all()
    )
    report_only_integrity_passed = (
        not report_only_audit_df.empty and report_only_audit_df["passed"].astype(bool).all()
    )
    report_integrity_audit_passed = (
        not combined_integrity_audit_df.empty
        and combined_integrity_audit_df["passed"].astype(bool).all()
    )

    checks.append(
        build_check(
            check_group="phase_dependency",
            check_name="phase_9_7_validation_passed",
            passed=phase_9_7_validation_passed,
            severity="INFO" if phase_9_7_validation_passed else "ERROR",
            details=(
                str(phase_9_7_summary_df.iloc[0].get("validation_decision", ""))
                if not phase_9_7_summary_df.empty
                else "Missing Phase 9.7 summary."
            ),
        )
    )

    checks.append(
        build_check(
            check_group="phase_dependency",
            check_name="long_forward_observation_controlled_dataset_write_defined",
            passed=controlled_dataset_write_defined,
            severity="INFO" if controlled_dataset_write_defined else "ERROR",
            details=f"controlled_dataset_write_defined={controlled_dataset_write_defined}",
        )
    )

    checks.append(
        build_check(
            check_group="integrity",
            check_name="schema_compatibility_passed",
            passed=schema_compatibility_passed,
            severity="INFO" if schema_compatibility_passed else "ERROR",
            details="Controlled report output includes required schema columns.",
        )
    )

    checks.append(
        build_check(
            check_group="integrity",
            check_name="provenance_integrity_passed",
            passed=provenance_integrity_passed,
            severity="INFO" if provenance_integrity_passed else "ERROR",
            details="Controlled report output preserves source provenance.",
        )
    )

    checks.append(
        build_check(
            check_group="integrity",
            check_name="safety_integrity_passed",
            passed=safety_integrity_passed,
            severity="INFO" if safety_integrity_passed else "ERROR",
            details="Controlled report output keeps safety flags disabled.",
        )
    )

    checks.append(
        build_check(
            check_group="integrity",
            check_name="report_only_integrity_passed",
            passed=report_only_integrity_passed,
            severity="INFO" if report_only_integrity_passed else "ERROR",
            details="Controlled report output remains report-only.",
        )
    )

    checks.append(
        build_check(
            check_group="integrity",
            check_name="report_integrity_audit_passed",
            passed=report_integrity_audit_passed,
            severity="INFO" if report_integrity_audit_passed else "ERROR",
            details=(
                "failed_integrity_checks="
                + ",".join(
                    combined_integrity_audit_df[
                        ~combined_integrity_audit_df["passed"].astype(bool)
                    ]["audit_check"].astype(str)
                )
                if not combined_integrity_audit_df.empty
                else "failed_integrity_checks=all"
            ),
        )
    )

    controlled_report_write_rows = int(len(source_controlled_report_write_df))

    checks.append(
        build_check(
            check_group="controlled_report",
            check_name="controlled_report_write_rows_one",
            passed=controlled_report_write_rows == 1,
            severity="INFO" if controlled_report_write_rows == 1 else "ERROR",
            details=f"controlled_report_write_rows={controlled_report_write_rows}",
        )
    )

    official_dataset_not_written = (
        official_dataset_exists_before is False
        and official_dataset_exists_after is False
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

    for flag_name, flag_value in SAFETY_FLAGS.items():
        checks.append(
            build_check(
                check_group="safety_flags",
                check_name=flag_name,
                passed=flag_value is False,
                severity="INFO" if flag_value is False else "ERROR",
                details=f"{flag_name}={flag_value}",
            )
        )

    checks.append(
        build_check(
            check_group="scope_control",
            check_name="report_integrity_only",
            passed=True,
            severity="WARNING",
            details="Phase 9.8 audits report integrity only.",
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
            check_group="phase_transition",
            check_name="phase_9_9_recommended_next",
            passed=True,
            severity="INFO",
            details=(
                "Recommended next step: "
                "Phase 9.9 LONG Forward Observation Pre-Start Gate V1."
            ),
        )
    )

    checks_df = pd.DataFrame(checks)

    blocker_count = int(checks_df["blocker"].astype(bool).sum())
    error_count = int(checks_df["severity"].eq("ERROR").sum())
    warning_count = int(checks_df["severity"].eq("WARNING").sum())

    validation_passed = blocker_count == 0 and error_count == 0

    summary_values = (
        report_integrity_summary_table_df.iloc[0].to_dict()
        if not report_integrity_summary_table_df.empty
        else {}
    )

    summary_df = pd.DataFrame(
        [
            {
                "phase": "9.8",
                "long_forward_observation_report_integrity_defined": True,
                "phase_9_7_validation_passed": phase_9_7_validation_passed,
                "long_forward_observation_controlled_dataset_write_defined": (
                    controlled_dataset_write_defined
                ),
                "controlled_report_write_rows": controlled_report_write_rows,
                "controlled_report_write_only": bool(
                    summary_values.get("controlled_report_write_only", False)
                ),
                "controlled_row_source_candidate": summary_values.get(
                    "controlled_row_source_candidate",
                    "",
                ),
                "schema_compatibility_passed": schema_compatibility_passed,
                "provenance_integrity_passed": provenance_integrity_passed,
                "safety_integrity_passed": safety_integrity_passed,
                "report_only_integrity_passed": report_only_integrity_passed,
                "report_integrity_audit_rows": int(len(combined_integrity_audit_df)),
                "report_integrity_audit_passed": report_integrity_audit_passed,
                "official_dataset_exists_before": official_dataset_exists_before,
                "official_dataset_exists_after": official_dataset_exists_after,
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
                "exchange_execution_allowed": False,
                "automation_allowed": False,
                "execution_allowed": False,
                "real_entries_approved": False,
                "total_project_completed": False,
                "recommended_next_phase": (
                    "PHASE_9_9_LONG_FORWARD_OBSERVATION_PRE_START_GATE_V1"
                ),
                "estimated_phase_9_progress_percent": 80,
                "total_checks": int(len(checks_df)),
                "warning_count": warning_count,
                "error_count": error_count,
                "blocker_count": blocker_count,
                "validation_passed": validation_passed,
                "validation_decision": (
                    "PHASE_9_8_LONG_FORWARD_OBSERVATION_REPORT_INTEGRITY_VALIDATED"
                    if validation_passed
                    else "PHASE_9_8_LONG_FORWARD_OBSERVATION_REPORT_INTEGRITY_FAILED"
                ),
            }
        ]
    )

    phase_9_7_summary_df.to_csv(
        REPORTS_DIR / "phase_9_7_source_summary_v1.csv",
        index=False,
    )
    source_controlled_report_write_df.to_csv(
        REPORTS_DIR / "phase_9_7_source_controlled_report_write_v1.csv",
        index=False,
    )
    source_controlled_write_audit_df.to_csv(
        REPORTS_DIR / "phase_9_7_source_controlled_write_audit_v1.csv",
        index=False,
    )
    source_controlled_dataset_write_summary_df.to_csv(
        REPORTS_DIR / "phase_9_7_source_controlled_dataset_write_summary_v1.csv",
        index=False,
    )
    schema_audit_df.to_csv(
        REPORTS_DIR / "long_forward_observation_report_schema_integrity_audit_v1.csv",
        index=False,
    )
    provenance_audit_df.to_csv(
        REPORTS_DIR / "long_forward_observation_report_provenance_integrity_audit_v1.csv",
        index=False,
    )
    safety_audit_df.to_csv(
        REPORTS_DIR / "long_forward_observation_report_safety_integrity_audit_v1.csv",
        index=False,
    )
    report_only_audit_df.to_csv(
        REPORTS_DIR / "long_forward_observation_report_only_integrity_audit_v1.csv",
        index=False,
    )
    combined_integrity_audit_df.to_csv(
        REPORTS_DIR / "long_forward_observation_report_integrity_audit_v1.csv",
        index=False,
    )
    report_integrity_summary_table_df.to_csv(
        REPORTS_DIR / "long_forward_observation_report_integrity_summary_table_v1.csv",
        index=False,
    )
    checks_df.to_csv(
        REPORTS_DIR / "long_forward_observation_report_integrity_checks_v1.csv",
        index=False,
    )
    summary_df.to_csv(
        REPORTS_DIR / "long_forward_observation_report_integrity_summary_v1.csv",
        index=False,
    )

    return {
        "summary": summary_df,
        "source_phase_9_7_summary": phase_9_7_summary_df,
        "source_controlled_report_write": source_controlled_report_write_df,
        "source_controlled_write_audit": source_controlled_write_audit_df,
        "source_controlled_dataset_write_summary": (
            source_controlled_dataset_write_summary_df
        ),
        "schema_integrity_audit": schema_audit_df,
        "provenance_integrity_audit": provenance_audit_df,
        "safety_integrity_audit": safety_audit_df,
        "report_only_integrity_audit": report_only_audit_df,
        "combined_integrity_audit": combined_integrity_audit_df,
        "report_integrity_summary": report_integrity_summary_table_df,
        "checks": checks_df,
    }