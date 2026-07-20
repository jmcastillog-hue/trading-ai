from __future__ import annotations

import csv
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from src.integration.openclaw_read_only_research_status_contract_v1 import (
    EVIDENCE_SUMMARY,
    MASTER_DISPOSITION,
    OPENCLAW_NEXT_ROUTE,
    PHASE,
    PHASE_10_43_ROUTE,
    PROHIBITED_CAPABILITIES,
    READ_ONLY_CAPABILITIES,
    SCHEMA_VERSION,
    SOURCE_ANCHORS,
    build_status_snapshot,
    calculate_contract_root,
    validate_status_snapshot,
)


REPORTS_DIR = Path("reports/phase_10_42r_3")
SCHEMA_PATH = Path(
    "schemas/openclaw_read_only_research_status_contract_v1.schema.json"
)
PHASE_10_42_DOC = Path(
    "docs/PHASE_10_LONG_FORWARD_OBSERVATION_EVIDENCE_COLLECTION_"
    "OFFICIAL_DATASET_ATOMIC_WRITE_HARNESS_DESIGN.md"
)
PHASE_10_42R_DOC = Path(
    "docs/PHASE_10_42R_PROJECT_SCIENTIFIC_INTEGRITY_AND_REPRODUCIBILITY_AUDIT.md"
)
PHASE_10_42R_2_DOC = Path(
    "docs/PHASE_10_42R_2_SHORT_LONG_CLOSED_CANDLE_MTF_REVALIDATION.md"
)
PHASE_10_42R_2L_DOC = Path(
    "docs/PHASE_10_42R_2L_FROZEN_RECOVERY_CANDIDATE_"
    "INDEPENDENT_RESULT_AUDIT_AND_DISPOSITION.md"
)
README_PATH = Path("README.md")
GITIGNORE_PATH = Path(".gitignore")

VALIDATION_DECISION = (
    "PHASE_10_42R_3_MASTER_DISPOSITION_AND_OPENCLAW_READ_ONLY_"
    "RESEARCH_STATUS_CONTRACT_VALIDATED"
)
BLOCKED_DECISION = (
    "PHASE_10_42R_3_MASTER_DISPOSITION_AND_OPENCLAW_READ_ONLY_"
    "RESEARCH_STATUS_CONTRACT_BLOCKED"
)


@dataclass(frozen=True)
class Check:
    check_id: str
    check_name: str
    passed: bool
    details: str
    blocker: bool


class MasterDispositionValidationFailure(RuntimeError):
    pass


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _add_check(
    checks: list[Check],
    name: str,
    passed: bool,
    details: str,
    *,
    blocker: bool = True,
) -> None:
    ok = bool(passed)
    checks.append(
        Check(
            check_id=f"10.42R.3-CHECK-{len(checks) + 1:03d}",
            check_name=name,
            passed=ok,
            details=str(details),
            blocker=bool(blocker and not ok),
        )
    )


def _schema_contract_is_exact(schema: dict[str, Any]) -> bool:
    required = {
        "contract",
        "source_anchors",
        "master_disposition",
        "evidence_summary",
        "permissions",
        "openclaw_policy",
        "next_routes",
        "contract_root_sha256",
    }
    return (
        schema.get("$schema") == "https://json-schema.org/draft/2020-12/schema"
        and schema.get("title") == "OpenClaw Read-Only Research Status Contract V1"
        and schema.get("type") == "object"
        and schema.get("additionalProperties") is False
        and set(schema.get("required", [])) == required
        and set(schema.get("properties", {})) == required
    )


def _permission_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for name, value in READ_ONLY_CAPABILITIES.items():
        rows.append(
            {
                "permission_group": "READ_ONLY_CAPABILITY",
                "permission_name": name,
                "value": value,
                "openclaw_may_override": False,
            }
        )
    for name, value in PROHIBITED_CAPABILITIES.items():
        rows.append(
            {
                "permission_group": "PROHIBITED_CAPABILITY",
                "permission_name": name,
                "value": value,
                "openclaw_may_override": False,
            }
        )
    return rows


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8", newline="\n")
        return
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def validate_phase_10_42r_3(
    *,
    preflight_only: bool = False,
    root: Path | None = None,
    write_outputs: bool = True,
) -> dict[str, Any]:
    project_root = (root or Path.cwd()).resolve()
    checks: list[Check] = []

    paths = {
        "phase_10_42_document_exists": PHASE_10_42_DOC,
        "phase_10_42r_document_exists": PHASE_10_42R_DOC,
        "phase_10_42r_2_document_exists": PHASE_10_42R_2_DOC,
        "phase_10_42r_2l_document_exists": PHASE_10_42R_2L_DOC,
        "contract_schema_exists": SCHEMA_PATH,
        "readme_exists": README_PATH,
        "gitignore_exists": GITIGNORE_PATH,
    }
    for name, relative in paths.items():
        path = project_root / relative
        _add_check(checks, name, path.is_file(), relative.as_posix())

    def content(relative: Path) -> str:
        path = project_root / relative
        return _read_text(path) if path.is_file() else ""

    phase_10_42 = content(PHASE_10_42_DOC)
    phase_10_42r = content(PHASE_10_42R_DOC)
    phase_10_42r_2 = content(PHASE_10_42R_2_DOC)
    phase_10_42r_2l = content(PHASE_10_42R_2L_DOC)
    readme = content(README_PATH)
    gitignore = content(GITIGNORE_PATH)

    _add_check(
        checks,
        "phase_10_42_empty_schema_anchor_exact",
        (
            SOURCE_ANCHORS["long_empty_schema_candidate_sha256"] in phase_10_42
            and "54 canonical columns" in phase_10_42
            and "zero evidence rows" in phase_10_42
        ),
        SOURCE_ANCHORS["long_empty_schema_candidate_sha256"],
    )
    _add_check(
        checks,
        "phase_10_43_existing_route_preserved",
        "Phase 10.43 — LONG Forward Observation Evidence Collection Official Dataset Atomic Write Harness Design Review V1"
        in phase_10_42,
        PHASE_10_43_ROUTE,
    )
    _add_check(
        checks,
        "phase_10_42r_correction_anchor_present",
        (
            "closed-candle MTF remediation" in phase_10_42r
            and "REVALIDATION_REQUIRED" in phase_10_42r
        ),
        "closed-candle remediation",
    )
    _add_check(
        checks,
        "phase_10_42r_2_short_rejection_anchor_present",
        "REVALIDATED_REJECTED" in phase_10_42r_2,
        MASTER_DISPOSITION["legacy_short_candidate"],
    )
    _add_check(
        checks,
        "phase_10_42r_2_long_disposition_anchors_present",
        (
            "CERTIFIED_UNAFFECTED_AND_CONSISTENCY_REVALIDATED" in phase_10_42r_2
            and "LONG_FORWARD_OBSERVATION_CANDIDATE" in phase_10_42r_2
            and "LONG_SECONDARY_WATCHLIST" in phase_10_42r_2
        ),
        "primary research-only / secondary watchlist",
    )
    _add_check(
        checks,
        "phase_10_42r_2_design_permissions_present",
        (
            "phase_10_43_design_review_allowed" in phase_10_42r_2
            and "openclaw_read_only_status_design_allowed" in phase_10_42r_2
        ),
        "design permissions only",
    )
    _add_check(
        checks,
        "phase_2l_source_bundle_root_anchor_present",
        SOURCE_ANCHORS["phase_10_42r_2k_bundle_root_sha256"] in phase_10_42r_2l,
        SOURCE_ANCHORS["phase_10_42r_2k_bundle_root_sha256"],
    )
    _add_check(
        checks,
        "phase_2l_recovery_closure_decision_present",
        (
            "INDEPENDENT_RESULT_AUDIT_CONFIRMED_ALL_VARIANTS_REJECTED_"
            "RECOVERY_LINE_CLOSED_NO_LOCKBOX_OPENED"
        )
        in phase_10_42r_2l,
        "all variants rejected / line closed",
    )
    _add_check(
        checks,
        "readme_master_status_updated",
        (
            "Phase 10.42R.3 master disposition and OpenClaw read-only research "
            "status contract: validated and closed."
        )
        in readme,
        "README current status",
    )
    _add_check(
        checks,
        "gitignore_phase_output_registered",
        "reports/phase_10_42r_3/" in gitignore,
        "reports/phase_10_42r_3/",
    )

    schema_path = project_root / SCHEMA_PATH
    try:
        schema = json.loads(_read_text(schema_path)) if schema_path.is_file() else {}
    except json.JSONDecodeError:
        schema = {}
    _add_check(
        checks,
        "json_schema_contract_exact",
        _schema_contract_is_exact(schema),
        SCHEMA_PATH.as_posix(),
    )

    snapshot = build_status_snapshot(
        generated_at_utc="2026-07-20T00:00:00+00:00"
    )
    _add_check(
        checks,
        "read_only_capabilities_exact",
        snapshot["permissions"]["read_only_capabilities"] == READ_ONLY_CAPABILITIES,
        json.dumps(READ_ONLY_CAPABILITIES, sort_keys=True),
    )
    _add_check(
        checks,
        "prohibited_capabilities_exact",
        (
            snapshot["permissions"]["prohibited_capabilities"]
            == PROHIBITED_CAPABILITIES
            and all(value is False for value in PROHIBITED_CAPABILITIES.values())
        ),
        json.dumps(PROHIBITED_CAPABILITIES, sort_keys=True),
    )
    _add_check(
        checks,
        "next_routes_exact_and_independent",
        (
            snapshot["next_routes"]["long_dataset_track"] == PHASE_10_43_ROUTE
            and snapshot["next_routes"]["openclaw_read_only_track"]
            == OPENCLAW_NEXT_ROUTE
            and snapshot["next_routes"]["route_independence"] is True
        ),
        f"{PHASE_10_43_ROUTE}|{OPENCLAW_NEXT_ROUTE}",
    )

    preflight_count = len(checks)
    preflight_failed = [item for item in checks if not item.passed]
    preflight_blockers = [item for item in checks if item.blocker]

    if preflight_only:
        summary = {
            "phase": PHASE,
            "schema_version": SCHEMA_VERSION,
            "preflight_only": True,
            "preflight_check_count": preflight_count,
            "audit_check_count": 0,
            "total_check_count": preflight_count,
            "failed_check_count": len(preflight_failed),
            "blocker_count": len(preflight_blockers),
            "historical_evaluation_count": 0,
            "backtest_execution_count": 0,
            "performance_metric_recalculation_count": 0,
            "candidate_comparison_count": 0,
            "candidate_ranking_count": 0,
            "winner_selection_count": 0,
            "retrospective_lockbox_access_count": 0,
            "prospective_holdout_access_count": 0,
            "openclaw_runtime_integration_count": 0,
            "validation_passed": not preflight_blockers,
            "validation_decision": (
                "PREFLIGHT_PASSED" if not preflight_blockers else "PREFLIGHT_BLOCKED"
            ),
        }
        return {
            "summary": summary,
            "checks": tuple(asdict(item) for item in checks),
            "snapshot": snapshot,
        }

    if preflight_blockers:
        raise MasterDispositionValidationFailure(
            "Preflight blockers: "
            + ",".join(item.check_name for item in preflight_blockers)
        )

    snapshot = build_status_snapshot()
    snapshot_error = ""
    try:
        validate_status_snapshot(snapshot)
        snapshot_valid = True
    except Exception as exc:  # fail-closed diagnostic
        snapshot_valid = False
        snapshot_error = repr(exc)

    _add_check(checks, "status_snapshot_valid", snapshot_valid, snapshot_error)
    _add_check(
        checks,
        "contract_root_reproduced",
        snapshot["contract_root_sha256"] == calculate_contract_root(snapshot),
        snapshot["contract_root_sha256"],
    )
    _add_check(
        checks,
        "six_rejected_variants_exact",
        (
            EVIDENCE_SUMMARY["short_recovery_variant_count"] == 6
            and EVIDENCE_SUMMARY["short_recovery_rejected_variant_count"] == 6
        ),
        "6/6",
    )
    _add_check(
        checks,
        "zero_surviving_variants_exact",
        EVIDENCE_SUMMARY["short_recovery_surviving_variant_count"] == 0,
        "0",
    )
    _add_check(
        checks,
        "lockboxes_sealed",
        (
            MASTER_DISPOSITION["retrospective_lockbox"] == "SEALED"
            and MASTER_DISPOSITION["prospective_holdout"] == "SEALED"
        ),
        "SEALED/SEALED",
    )
    _add_check(
        checks,
        "long_empty_schema_state_exact",
        (
            EVIDENCE_SUMMARY["long_empty_schema_column_count"] == 54
            and EVIDENCE_SUMMARY["long_official_evidence_row_count"] == 0
        ),
        "54 columns / 0 evidence rows",
    )
    _add_check(
        checks,
        "operational_approval_count_zero",
        EVIDENCE_SUMMARY["operational_approval_count"] == 0,
        "0",
    )
    _add_check(
        checks,
        "openclaw_runtime_not_implemented",
        (
            snapshot["openclaw_policy"]["runtime_integration_status"]
            == "NOT_IMPLEMENTED"
            and snapshot["permissions"]["prohibited_capabilities"][
                "openclaw_runtime_status_consumption_allowed"
            ]
            is False
        ),
        "NOT_IMPLEMENTED",
    )
    _add_check(
        checks,
        "historical_evaluation_not_performed",
        PROHIBITED_CAPABILITIES["historical_evaluation_allowed"] is False,
        "0",
    )
    _add_check(
        checks,
        "backtest_not_executed",
        PROHIBITED_CAPABILITIES["backtest_execution_allowed"] is False,
        "0",
    )
    _add_check(
        checks,
        "performance_metrics_not_recalculated",
        PROHIBITED_CAPABILITIES["performance_metric_recalculation_allowed"] is False,
        "0",
    )
    _add_check(
        checks,
        "comparison_ranking_winner_disabled",
        (
            PROHIBITED_CAPABILITIES["candidate_comparison_allowed"] is False
            and PROHIBITED_CAPABILITIES["candidate_ranking_allowed"] is False
            and PROHIBITED_CAPABILITIES["winner_selection_allowed"] is False
        ),
        "0/0/0",
    )
    _add_check(
        checks,
        "recovery_repair_route_closed",
        snapshot["next_routes"]["another_recovery_repair_phase_allowed"] is False,
        "False",
    )
    _add_check(
        checks,
        "phase_10_43_route_allowed_but_not_executed",
        (
            snapshot["next_routes"]["phase_10_43_design_review_allowed"] is True
            and PROHIBITED_CAPABILITIES["official_dataset_write_allowed"] is False
        ),
        PHASE_10_43_ROUTE,
    )

    output_files: list[str] = []
    if write_outputs:
        output_dir = project_root / REPORTS_DIR
        output_dir.mkdir(parents=True, exist_ok=True)

        snapshot_path = output_dir / "openclaw_read_only_research_status_snapshot_v1.json"
        snapshot_path.write_text(
            json.dumps(snapshot, sort_keys=True, indent=2, ensure_ascii=True)
            + "\n",
            encoding="utf-8",
            newline="\n",
        )
        output_files.append(snapshot_path.name)

        permission_path = output_dir / "openclaw_read_only_permission_matrix_v1.csv"
        _write_csv(permission_path, _permission_rows())
        output_files.append(permission_path.name)

        disposition_rows = [
            {"status_name": name, "status_value": value}
            for name, value in MASTER_DISPOSITION.items()
        ]
        disposition_path = output_dir / "master_disposition_v1.csv"
        _write_csv(disposition_path, disposition_rows)
        output_files.append(disposition_path.name)

    _add_check(
        checks,
        "planned_report_artifacts_written",
        (not write_outputs) or len(output_files) == 3,
        ",".join(output_files),
    )

    failed = [item for item in checks if not item.passed]
    blockers = [item for item in checks if item.blocker]

    summary = {
        "phase": PHASE,
        "schema_version": SCHEMA_VERSION,
        "preflight_only": False,
        "source_anchor_count": len(SOURCE_ANCHORS),
        "master_disposition_field_count": len(MASTER_DISPOSITION),
        "read_only_capability_count": len(READ_ONLY_CAPABILITIES),
        "prohibited_capability_count": len(PROHIBITED_CAPABILITIES),
        "short_recovery_variant_count": 6,
        "rejected_variant_count": 6,
        "surviving_variant_count": 0,
        "long_empty_schema_column_count": 54,
        "long_official_evidence_row_count": 0,
        "preflight_check_count": preflight_count,
        "audit_check_count": len(checks) - preflight_count,
        "total_check_count": len(checks),
        "failed_check_count": len(failed),
        "blocker_count": len(blockers),
        "historical_evaluation_count": 0,
        "backtest_execution_count": 0,
        "performance_metric_recalculation_count": 0,
        "candidate_comparison_count": 0,
        "candidate_ranking_count": 0,
        "winner_selection_count": 0,
        "retrospective_lockbox_access_count": 0,
        "prospective_holdout_access_count": 0,
        "official_dataset_write_count": 0,
        "signal_generation_count": 0,
        "paper_trade_execution_count": 0,
        "real_capital_execution_count": 0,
        "openclaw_runtime_integration_count": 0,
        "contract_root_sha256": snapshot["contract_root_sha256"],
        "phase_10_43_design_review_allowed": True,
        "openclaw_read_only_status_export_implementation_allowed": True,
        "openclaw_runtime_integration_allowed": False,
        "total_project_completed": False,
        "recommended_phase_10_43_route": PHASE_10_43_ROUTE,
        "recommended_openclaw_route": OPENCLAW_NEXT_ROUTE,
        "validation_passed": not blockers,
        "validation_decision": VALIDATION_DECISION if not blockers else BLOCKED_DECISION,
        "output_directory": REPORTS_DIR.as_posix(),
        "output_files": output_files,
    }

    if write_outputs:
        output_dir = project_root / REPORTS_DIR
        checks_path = output_dir / "validation_checks_v1.csv"
        _write_csv(checks_path, [asdict(item) for item in checks])
        summary_path = output_dir / "validation_summary_v1.json"
        summary_path.write_text(
            json.dumps(summary, sort_keys=True, indent=2, ensure_ascii=True) + "\n",
            encoding="utf-8",
            newline="\n",
        )

    if blockers:
        raise MasterDispositionValidationFailure(
            "Master disposition blockers: "
            + ",".join(item.check_name for item in blockers)
        )

    return {
        "summary": summary,
        "checks": tuple(asdict(item) for item in checks),
        "snapshot": snapshot,
    }


__all__ = [
    "BLOCKED_DECISION",
    "MasterDispositionValidationFailure",
    "REPORTS_DIR",
    "VALIDATION_DECISION",
    "validate_phase_10_42r_3",
]
