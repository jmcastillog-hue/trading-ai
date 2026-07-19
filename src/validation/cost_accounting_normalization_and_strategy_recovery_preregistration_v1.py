from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

import pandas as pd

from src.execution.cost_aware_filter_v1 import build_cost_profiles
from src.execution.normalized_cost_accounting_v1 import (
    ACCOUNTING_CONTRACT,
    DECISION_STATUS,
    DRAWDOWN_ORDER_CONTRACT,
    WINDOW_UNIT_CONTRACT,
    accounting_identity_holds,
    normalize_short_trades,
    summarize_normalized_trades,
    validate_short_trade_schema,
)
from src.validation.signal_to_fill_timing_integrity_audit_v1 import (
    FILL_NEXT_OPEN,
    OFFICIAL_BACKUP_PATH,
    OFFICIAL_DATASET_PATH,
    OFFICIAL_LOCK_PATH,
    OFFICIAL_MANIFEST_PATH,
    OFFICIAL_TEMP_PATH,
)


PHASE = "10.42R.2B"
REPORTS_DIR = Path(
    "reports/phase_10_42r_2b_cost_accounting_normalization_"
    "and_strategy_recovery_preregistration_v1"
)
R2A_REPORTS_DIR = Path(
    "reports/phase_10_42r_2a_signal_to_fill_timing_integrity_audit_v1"
)
R2A_REQUIRED_REPORTS = {
    "summary": R2A_REPORTS_DIR / "summary_v1.csv",
    "checks": R2A_REPORTS_DIR / "checks_v1.csv",
    "short_timing_trades": R2A_REPORTS_DIR / "short_timing_trades_v1.csv",
}

KNOWN_RESEARCH_DATA_END_EXCLUSIVE = pd.Timestamp("2026-01-01T00:00:00Z")
RETROSPECTIVE_LOCKBOX_START = pd.Timestamp("2026-01-01T00:00:00Z")
RETROSPECTIVE_LOCKBOX_END = pd.Timestamp("2026-07-20T00:00:00Z")
PROSPECTIVE_HOLDOUT_START = pd.Timestamp("2026-07-20T00:00:00Z")
PROSPECTIVE_HOLDOUT_END = pd.Timestamp("2027-01-20T00:00:00Z")
RETROSPECTIVE_LOCKBOX_PATH = Path(
    "data/holdout/strategy_recovery_retrospective_lockbox_2026h1_v1.csv"
)
PROSPECTIVE_HOLDOUT_PATH = Path(
    "data/holdout/strategy_recovery_prospective_20260720_20270120_v1.csv"
)

SHORT_REJECTED_REFERENCE = "TARGET_SHORT_FIB_V5_MTF_V3_1 + FIXED_RR_2_5"
LONG_PRIMARY_REFERENCE = "LONG_BASE_FAILED_BREAKDOWN_V1"
LONG_SECONDARY_REFERENCE = "LONG_BASE_LIQUIDITY_SWEEP_V1"
SHORT_SYMBOL_COHORT = ("BTCUSDT", "ETHUSDT", "SOLUSDT")
SHORT_WALK_FORWARD_SPLITS = (
    "WF_202201_202301_TO_202301_202304",
    "WF_202204_202304_TO_202304_202307",
    "WF_202207_202307_TO_202307_202310",
    "WF_202210_202310_TO_202310_202401",
    "WF_202301_202401_TO_202401_202404",
    "WF_202304_202404_TO_202404_202407",
    "WF_202307_202407_TO_202407_202410",
    "WF_202310_202410_TO_202410_202501",
    "WF_202401_202501_TO_202501_202504",
    "WF_202404_202504_TO_202504_202507",
    "WF_202407_202507_TO_202507_202510",
    "WF_202410_202510_TO_202510_202601",
)
NEXT_PHASE = "PHASE_10_42R_2C_PREREGISTERED_STRATEGY_RECOVERY_DEVELOPMENT_DIAGNOSTIC_V1"

SAFETY_FLAGS = {
    "signal_generation_enabled": False,
    "forward_observation_allowed": False,
    "official_dataset_write_allowed": False,
    "evidence_persistence_allowed": False,
    "normalized_cost_decision_published": False,
    "candidate_reclassification_allowed": False,
    "strategy_recovery_execution_allowed": False,
    "paper_trade_execution_allowed": False,
    "real_capital_allowed": False,
    "live_alerts_allowed": False,
    "market_execution_allowed": False,
    "exchange_execution_allowed": False,
    "automation_allowed": False,
    "execution_allowed": False,
    "openclaw_operational_integration_allowed": False,
}


def file_sha256(path: Path) -> str:
    if not path.exists() or not path.is_file():
        return ""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_check(
    check_name: str,
    passed: bool,
    severity: str,
    details: str,
) -> dict[str, Any]:
    return {
        "check_name": check_name,
        "passed": bool(passed),
        "severity": severity,
        "details": details,
        "blocker": severity == "ERROR" and not bool(passed),
    }


def official_forward_artifacts_absent() -> bool:
    return not any(
        path.exists()
        for path in (
            OFFICIAL_DATASET_PATH,
            OFFICIAL_TEMP_PATH,
            OFFICIAL_LOCK_PATH,
            OFFICIAL_MANIFEST_PATH,
            OFFICIAL_BACKUP_PATH,
        )
    )


def all_permissions_false() -> bool:
    return all(value is False for value in SAFETY_FLAGS.values())


def load_r2a_reports() -> tuple[dict[str, pd.DataFrame], pd.DataFrame]:
    frames: dict[str, pd.DataFrame] = {}
    rows: list[dict[str, Any]] = []
    required_columns = {
        "summary": {"audit_completed", "validation_passed", "blocker_count"},
        "checks": {"check_name", "passed", "blocker"},
        "short_timing_trades": {
            "fill_mode",
            "direction",
            "raw_entry_reference",
            "raw_exit_reference",
            "position_units",
            "risk_amount",
            "gross_pnl",
            "fees",
            "result_r",
        },
    }
    for name, path in R2A_REQUIRED_REPORTS.items():
        exists = path.exists() and path.is_file()
        frame = pd.DataFrame()
        error = ""
        if exists:
            try:
                frame = pd.read_csv(path)
            except Exception as exc:
                error = f"{type(exc).__name__}: {exc}"
        missing = sorted(required_columns[name] - set(frame.columns))
        valid = bool(exists and not frame.empty and not error and not missing)
        frames[name] = frame
        rows.append(
            {
                "report_name": name,
                "path": str(path),
                "exists": exists,
                "size_bytes": path.stat().st_size if exists else 0,
                "sha256": file_sha256(path),
                "rows": len(frame),
                "missing_columns": "|".join(missing),
                "read_error": error,
                "report_valid": valid,
            }
        )
    return frames, pd.DataFrame(rows)


def build_accounting_contract() -> pd.DataFrame:
    rows = [
        (
            1,
            "FRICTIONLESS_GROSS_RESULT_R",
            "(raw_entry_reference - raw_exit_reference) * position_units / risk_amount for SHORT",
            "No fee, spread, slippage, funding or buffer embedded.",
        ),
        (
            2,
            "PROFILE_TOTAL_COST_R",
            "sum(profile cost components) / risk_pct_of_raw_entry",
            "Exactly one complete profile is applied.",
        ),
        (
            3,
            "NORMALIZED_NET_RESULT_R",
            "frictionless_gross_result_r - profile_total_cost_r",
            "Canonical diagnostic result; no second cost subtraction.",
        ),
        (
            4,
            "INTERNAL_ENGINE_RECONCILIATION",
            "frictionless gross R - embedded spread R - internal fee R = internal result_r",
            "Must reconcile within 1e-10 R.",
        ),
        (
            5,
            "DECISION_BOUNDARY",
            DECISION_STATUS,
            "Metrics cannot reclassify, approve or execute a candidate in this phase.",
        ),
    ]
    return pd.DataFrame(
        rows,
        columns=["step", "field", "formula", "invariant"],
    )


def build_recovery_preregistration() -> pd.DataFrame:
    rules = [
        ("PR-001", "objective", "Diagnose why corrected strategies fail; do not optimize in Phase 2B."),
        ("PR-002", "timing", "Only CLOSED_CANDLE_CORRECTED plus NEXT_BAR_OPEN_CORRECTED is eligible."),
        ("PR-003", "short_reference", f"{SHORT_REJECTED_REFERENCE} remains a retired failed reference and cannot be repaired in-place."),
        ("PR-004", "long_reference", f"{LONG_PRIMARY_REFERENCE} and {LONG_SECONDARY_REFERENCE} remain research-only references."),
        ("PR-005", "symbols", "BTCUSDT, ETHUSDT and SOLUSDT remain a fixed cohort; no result-driven symbol deletion."),
        ("PR-006", "known_data", "2022-01-01 through 2025-12-31 is known evidence and can never be relabeled as holdout."),
        ("PR-007", "diagnostic_slices", "Predeclared slices: symbol, calendar year, volatility tercile, trend regime and signal family."),
        ("PR-008", "multiplicity", "Any later candidate search must declare family count and variants before evaluation; maximum 3 families and 4 variants per family."),
        ("PR-009", "costs", f"All comparisons use {ACCOUNTING_CONTRACT} and all five fixed cost profiles."),
        ("PR-010", "primary_metrics", "Net expectancy R, profit factor, max drawdown R, positive-window rate and trade count."),
        ("PR-011", "minimum_evidence", "No promotion with fewer than 100 aggregate OOS trades or fewer than 20 trades per symbol."),
        ("PR-012", "promotion_gate", "A future candidate must be positive after base costs, non-failing under stress, stable across symbols/windows and pass multiplicity controls."),
        ("PR-013", "retrospective_lockbox", "2026-01-01 to 2026-07-20 may be opened once only after candidate specification freeze; evidence tier is secondary."),
        ("PR-014", "prospective_holdout", "2026-07-20 to 2027-01-20 remains sealed and is the confirmatory evidence tier."),
        ("PR-015", "mutation_rule", "Any hypothesis or threshold change requires a new version and invalidates unopened-test claims for data already viewed."),
        ("PR-016", "execution", "No signal, paper trade, alert, capital, exchange, automation or OpenClaw operational permission is granted."),
    ]
    frame = pd.DataFrame(rules, columns=["rule_id", "category", "locked_rule"])
    frame["preregistered"] = True
    frame["mutable_after_real_run"] = False
    return frame


def build_holdout_contract() -> pd.DataFrame:
    rows = [
        {
            "holdout_id": "RETROSPECTIVE_LOCKBOX_2026H1_V1",
            "evidence_tier": "SECONDARY_RETROSPECTIVE_LOCKBOX",
            "start": RETROSPECTIVE_LOCKBOX_START.isoformat(),
            "end_exclusive": RETROSPECTIVE_LOCKBOX_END.isoformat(),
            "path": str(RETROSPECTIVE_LOCKBOX_PATH),
            "must_be_absent_in_phase_2b": True,
            "exists": RETROSPECTIVE_LOCKBOX_PATH.exists(),
            "access_allowed": False,
            "open_condition": "CANDIDATE_SPECIFICATION_HASH_FROZEN",
        },
        {
            "holdout_id": "PROSPECTIVE_HOLDOUT_20260720_20270120_V1",
            "evidence_tier": "PRIMARY_PROSPECTIVE_CONFIRMATION",
            "start": PROSPECTIVE_HOLDOUT_START.isoformat(),
            "end_exclusive": PROSPECTIVE_HOLDOUT_END.isoformat(),
            "path": str(PROSPECTIVE_HOLDOUT_PATH),
            "must_be_absent_in_phase_2b": True,
            "exists": PROSPECTIVE_HOLDOUT_PATH.exists(),
            "access_allowed": False,
            "open_condition": "END_DATE_REACHED_AND_CANDIDATE_HASH_FROZEN",
        },
    ]
    return pd.DataFrame(rows)


def write_outputs(outputs: dict[str, pd.DataFrame]) -> None:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    for name, frame in outputs.items():
        frame.to_csv(REPORTS_DIR / f"{name}_v1.csv", index=False)


def validate_phase_10_42r_2b() -> dict[str, pd.DataFrame]:
    frames, lineage = load_r2a_reports()
    errors: list[dict[str, str]] = []
    normalized = pd.DataFrame()
    normalized_summary = pd.DataFrame()
    profiles = build_cost_profiles()

    reports_valid = bool(
        len(lineage) == len(R2A_REQUIRED_REPORTS)
        and lineage["report_valid"].astype(bool).all()
    )
    source_summary = frames.get("summary", pd.DataFrame())
    source_checks = frames.get("checks", pd.DataFrame())
    source_completed = bool(
        not source_summary.empty
        and bool(source_summary.iloc[0].get("audit_completed", False))
        and bool(source_summary.iloc[0].get("validation_passed", False))
        and int(source_summary.iloc[0].get("blocker_count", -1)) == 0
        and not source_checks.empty
        and not source_checks["blocker"].astype(bool).any()
    )

    source_trades = frames.get("short_timing_trades", pd.DataFrame())
    corrected_short = (
        source_trades[
            source_trades.get("fill_mode", pd.Series(dtype=str)).astype(str).eq(
                FILL_NEXT_OPEN
            )
            & source_trades.get("direction", pd.Series(dtype=str)).astype(str).eq(
                "SHORT"
            )
        ].copy()
        if not source_trades.empty
        else pd.DataFrame()
    )
    try:
        normalized = normalize_short_trades(
            corrected_short,
            profiles,
        )
        normalized_summary = summarize_normalized_trades(
            normalized,
            configured_symbols=list(SHORT_SYMBOL_COHORT),
            configured_split_names=list(SHORT_WALK_FORWARD_SPLITS),
        )
    except Exception as exc:
        errors.append(
            {"scope": "SHORT_COST_NORMALIZATION", "error": f"{type(exc).__name__}: {exc}"}
        )

    accounting_contract = build_accounting_contract()
    preregistration = build_recovery_preregistration()
    holdout_contract = build_holdout_contract()

    expected_source_rows = (
        int(source_summary.iloc[0].get("short_next_open_trades", 0))
        if not source_summary.empty
        else 0
    )
    profile_count = len(profiles)
    normalized_rows_expected = len(corrected_short) * profile_count
    profile_names = [profile.name for profile in profiles]
    expected_source_profile_pairs = {
        (source_row, profile_name)
        for source_row in range(len(corrected_short))
        for profile_name in profile_names
    }
    actual_source_profile_pairs = (
        list(
            zip(
                pd.to_numeric(
                    normalized.get(
                        "source_trade_row", pd.Series(dtype=float)
                    ),
                    errors="coerce",
                ),
                normalized.get(
                    "cost_profile", pd.Series(dtype=str)
                ).astype(str),
            )
        )
        if not normalized.empty
        else []
    )
    source_profile_cardinality_exact = bool(
        len(actual_source_profile_pairs) == normalized_rows_expected
        and len(set(actual_source_profile_pairs))
        == len(actual_source_profile_pairs)
        and set(actual_source_profile_pairs)
        == expected_source_profile_pairs
    )
    identity_valid = accounting_identity_holds(normalized)
    no_decisions = bool(
        not normalized.empty
        and not normalized["normalized_cost_decision_allowed"].astype(bool).any()
        and not normalized["candidate_reclassification_allowed"].astype(bool).any()
        and normalized["cost_decision_status"].eq(DECISION_STATUS).all()
    )
    prereg_locked = bool(
        len(preregistration) == 16
        and preregistration["preregistered"].astype(bool).all()
        and not preregistration["mutable_after_real_run"].astype(bool).any()
    )
    holdouts_absent = bool(not holdout_contract["exists"].astype(bool).any())
    source_schema_valid = not validate_short_trade_schema(corrected_short)
    known_timestamps = pd.to_datetime(
        corrected_short.get("entry_time", pd.Series(dtype=str)),
        errors="coerce",
        utc=True,
    )
    source_before_lockboxes = bool(
        not known_timestamps.empty
        and known_timestamps.notna().all()
        and known_timestamps.max() < RETROSPECTIVE_LOCKBOX_START
        and KNOWN_RESEARCH_DATA_END_EXCLUSIVE <= RETROSPECTIVE_LOCKBOX_START
        and RETROSPECTIVE_LOCKBOX_END == PROSPECTIVE_HOLDOUT_START
    )
    required_primary_summary_columns = {
        "trade_rows",
        "normalized_average_result_r",
        "normalized_profit_factor",
        "normalized_max_drawdown_r",
        "drawdown_order_contract",
        "window_unit_contract",
        "configured_window_rows",
        "observed_window_rows",
        "zero_trade_window_rows",
        "positive_window_rows",
        "positive_window_rate",
        "minimum_window_trade_count",
        "maximum_window_trade_count",
    }
    primary_metrics_published = bool(
        not normalized_summary.empty
        and required_primary_summary_columns.issubset(
            normalized_summary.columns
        )
    )
    summary_contracts_valid = bool(
        primary_metrics_published
        and normalized_summary["drawdown_order_contract"].eq(
            DRAWDOWN_ORDER_CONTRACT
        ).all()
        and normalized_summary["window_unit_contract"].eq(
            WINDOW_UNIT_CONTRACT
        ).all()
    )
    window_counts_valid = False
    if summary_contracts_valid and not normalized.empty:
        symbol_count = len(SHORT_SYMBOL_COHORT)
        split_count = len(SHORT_WALK_FORWARD_SPLITS)
        source_universe_valid = bool(
            set(normalized["symbol"].astype(str).unique())
            == set(SHORT_SYMBOL_COHORT)
            and set(normalized["split_name"].astype(str).unique()).issubset(
                set(SHORT_WALK_FORWARD_SPLITS)
            )
        )
        expected_windows = normalized_summary["scope"].map(
            lambda scope: (
                symbol_count * split_count
                if scope == "ALL_SYMBOLS"
                else split_count
            )
        )
        window_counts_valid = bool(
            source_universe_valid
            and normalized_summary["configured_window_rows"].eq(
                expected_windows
            ).all()
            and (
                normalized_summary["observed_window_rows"]
                + normalized_summary["zero_trade_window_rows"]
            ).eq(normalized_summary["configured_window_rows"]).all()
            and normalized_summary["positive_window_rows"].le(
                normalized_summary["observed_window_rows"]
            ).all()
            and normalized_summary["positive_window_rate"].between(
                0.0, 1.0, inclusive="both"
            ).all()
        )

    checks = pd.DataFrame(
        [
            build_check("phase_10_42r_2a_reports_valid", reports_valid, "ERROR", f"valid={int(lineage['report_valid'].astype(bool).sum())}/{len(lineage)}"),
            build_check("phase_10_42r_2a_completed_without_blockers", source_completed, "ERROR", "R2A audit must be completed with zero blockers."),
            build_check("corrected_short_source_schema_valid", source_schema_valid, "ERROR", f"missing={validate_short_trade_schema(corrected_short)}"),
            build_check("corrected_short_trade_count_matches_r2a", len(corrected_short) == expected_source_rows and expected_source_rows > 0, "ERROR", f"source={len(corrected_short)}, expected={expected_source_rows}"),
            build_check("all_five_cost_profiles_applied_once", source_profile_cardinality_exact and normalized_rows_expected > 0, "ERROR", f"rows={len(normalized)}, expected={normalized_rows_expected}, exact_source_profile_pairs={source_profile_cardinality_exact}, profiles={profile_count}"),
            build_check("gross_to_net_accounting_identity_holds", identity_valid, "ERROR", "Internal net reconciles and normalized net subtracts one component sum."),
            build_check("legacy_double_count_overlap_removed", bool(not normalized.empty and pd.to_numeric(normalized["normalization_delta_vs_legacy_r"], errors="coerce").gt(0).all()), "ERROR", "Normalized result adds back only the internally embedded fee/spread before applying one profile."),
            build_check("preregistered_primary_summary_metrics_published", primary_metrics_published, "ERROR", f"required={sorted(required_primary_summary_columns)}"),
            build_check("chronological_drawdown_and_window_universe_valid", summary_contracts_valid and window_counts_valid, "ERROR", f"drawdown={DRAWDOWN_ORDER_CONTRACT}, windows={WINDOW_UNIT_CONTRACT}"),
            build_check("normalized_metrics_are_diagnostic_only", no_decisions, "ERROR", DECISION_STATUS),
            build_check("recovery_preregistration_locked", prereg_locked, "ERROR", f"locked_rules={len(preregistration)}"),
            build_check("known_source_precedes_sealed_lockboxes", source_before_lockboxes, "ERROR", f"max_known_entry={known_timestamps.max() if not known_timestamps.empty else 'missing'}"),
            build_check("holdout_files_absent_and_unaccessed", holdouts_absent, "ERROR", "Neither lockbox is loaded or created in Phase 2B."),
            build_check("official_forward_artifacts_absent", official_forward_artifacts_absent(), "ERROR", str(OFFICIAL_DATASET_PATH)),
            build_check("all_execution_permissions_false", all_permissions_false(), "ERROR", str(SAFETY_FLAGS)),
            build_check("no_runtime_errors", not errors, "ERROR", f"errors={len(errors)}"),
        ]
    )
    validation_passed = not checks["blocker"].astype(bool).any()
    summary = pd.DataFrame(
        [
            {
                "phase": PHASE,
                "run_mode": "REPORT_ONLY_NORMALIZATION_AND_PREREGISTRATION",
                "audit_completed": validation_passed,
                "source_short_next_open_trades": len(corrected_short),
                "cost_profile_count": profile_count,
                "normalized_trade_profile_rows": len(normalized),
                "accounting_contract": ACCOUNTING_CONTRACT,
                "normalization_contract_validated": identity_valid,
                "normalized_metrics_generated": not normalized_summary.empty,
                "normalized_cost_decision_published": False,
                "short_candidate_status": "REVALIDATED_REJECTED_UNCHANGED",
                "long_candidate_status": "RESEARCH_ONLY_NOT_APPROVED",
                "candidate_reclassified": False,
                "recovery_preregistration_locked": prereg_locked,
                "retrospective_lockbox_status": "SEALED_NOT_ACCESSED",
                "prospective_holdout_status": "SEALED_NOT_ACCESSED",
                "official_dataset_exists": OFFICIAL_DATASET_PATH.exists(),
                "official_evidence_rows_written": 0,
                "error_rows": len(errors),
                "total_checks": len(checks),
                "blocker_count": int(checks["blocker"].astype(bool).sum()),
                "validation_passed": validation_passed,
                "validation_decision": (
                    "PHASE_10_42R_2B_COST_NORMALIZATION_AND_RECOVERY_PREREGISTRATION_COMPLETED"
                    if validation_passed
                    else "PHASE_10_42R_2B_COST_NORMALIZATION_AND_RECOVERY_PREREGISTRATION_FAILED"
                ),
                "recommended_next_phase": (
                    NEXT_PHASE if validation_passed else "REMEDIATE_PHASE_10_42R_2B_BLOCKERS"
                ),
                **SAFETY_FLAGS,
                "total_project_completed": False,
            }
        ]
    )

    outputs = {
        "summary": summary,
        "checks": checks,
        "r2a_report_lineage": lineage,
        "accounting_contract": accounting_contract,
        "normalized_short_trades": normalized,
        "normalized_short_summary": normalized_summary,
        "recovery_preregistration": preregistration,
        "holdout_contract": holdout_contract,
        "errors": pd.DataFrame(errors, columns=["scope", "error"]),
    }
    write_outputs(outputs)
    return outputs
