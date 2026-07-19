from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from src.analysis.preregistered_strategy_recovery_diagnostic_v1 import (
    DIAGNOSTIC_SIGNAL_FAMILY,
    DIAGNOSTIC_STATUS,
    SLICE_DIMENSIONS,
    VOLATILITY_METHOD,
    VOLATILITY_TERCILES,
    attach_closed_candle_context,
    attach_features_to_normalized,
    build_slice_catalog,
    build_slice_coverage,
    build_slice_metrics,
    build_source_trade_features,
    validate_normalized_source_grid,
)
from src.execution.cost_aware_filter_v1 import build_cost_profiles
from src.validation.closed_candle_mtf_revalidation_v1 import (
    MODE_CORRECTED,
    OFFICIAL_BACKUP_PATH,
    OFFICIAL_DATASET_PATH,
    OFFICIAL_LOCK_PATH,
    OFFICIAL_MANIFEST_PATH,
    OFFICIAL_TEMP_PATH,
    build_mtf_regime_context,
    dataset_path,
    prepare_dataset_manifest,
)
from src.validation.cost_accounting_normalization_and_strategy_recovery_preregistration_v1 import (
    ACCOUNTING_CONTRACT,
    PROSPECTIVE_HOLDOUT_PATH,
    RETROSPECTIVE_LOCKBOX_PATH,
    SHORT_REJECTED_REFERENCE,
    SHORT_SYMBOL_COHORT,
    SHORT_WALK_FORWARD_SPLITS,
    build_accounting_contract,
    build_recovery_preregistration,
)


PHASE = "10.42R.2C"
EXPECTED_SOURCE_SHORT_TRADES = 205
REPORTS_DIR = Path(
    "reports/phase_10_42r_2c_preregistered_strategy_recovery_"
    "development_diagnostic_v1"
)
PHASE_2B_REPORTS_DIR = Path(
    "reports/phase_10_42r_2b_cost_accounting_normalization_"
    "and_strategy_recovery_preregistration_v1"
)
PHASE_2_REPORTS_DIR = Path(
    "reports/phase_10_42r_2_short_long_closed_candle_mtf_revalidation_v1"
)
PHASE_2_DATASET_MANIFEST_PATH = PHASE_2_REPORTS_DIR / "dataset_manifest_v1.csv"

NEXT_PHASE = (
    "PHASE_10_42R_2D_RECOVERY_CANDIDATE_FAMILY_SPECIFICATION_"
    "AND_MULTIPLICITY_FREEZE_V1"
)

PHASE_2B_REQUIRED_REPORTS = {
    "summary": PHASE_2B_REPORTS_DIR / "summary_v1.csv",
    "checks": PHASE_2B_REPORTS_DIR / "checks_v1.csv",
    "normalized_short_trades": PHASE_2B_REPORTS_DIR
    / "normalized_short_trades_v1.csv",
    "normalized_short_summary": PHASE_2B_REPORTS_DIR
    / "normalized_short_summary_v1.csv",
    "recovery_preregistration": PHASE_2B_REPORTS_DIR
    / "recovery_preregistration_v1.csv",
    "accounting_contract": PHASE_2B_REPORTS_DIR / "accounting_contract_v1.csv",
    "holdout_contract": PHASE_2B_REPORTS_DIR / "holdout_contract_v1.csv",
    "errors": PHASE_2B_REPORTS_DIR / "errors_v1.csv",
}

PHASE_2B_REQUIRED_COLUMNS = {
    "summary": {
        "audit_completed",
        "validation_passed",
        "blocker_count",
        "source_short_next_open_trades",
        "cost_profile_count",
        "normalized_trade_profile_rows",
        "accounting_contract",
        "short_candidate_status",
        "long_candidate_status",
        "candidate_reclassified",
    },
    "checks": {"check_name", "passed", "blocker"},
    "normalized_short_trades": {
        "source_trade_row",
        "cost_profile",
        "symbol",
        "split_name",
        "signal_time",
        "entry_time",
        "exit_time",
        "normalized_net_result_r",
        "frictionless_gross_result_r",
    },
    "normalized_short_summary": {
        "scope",
        "cost_profile",
        "trade_rows",
        "normalized_average_result_r",
        "normalized_profit_factor",
        "normalized_max_drawdown_r",
        "positive_window_rate",
    },
    "recovery_preregistration": {
        "rule_id",
        "category",
        "locked_rule",
        "preregistered",
        "mutable_after_real_run",
    },
    "accounting_contract": {"step", "field", "formula", "invariant"},
    "holdout_contract": {
        "holdout_id",
        "path",
        "exists",
        "access_allowed",
    },
    "errors": {"scope", "error"},
}

SPLIT_TEST_YEARS = {
    split_name: 2023 + index // 4
    for index, split_name in enumerate(SHORT_WALK_FORWARD_SPLITS)
}

SAFETY_FLAGS = {
    "signal_generation_enabled": False,
    "forward_observation_allowed": False,
    "official_dataset_write_allowed": False,
    "evidence_persistence_allowed": False,
    "candidate_search_enabled": False,
    "parameter_optimization_enabled": False,
    "diagnostic_ranking_enabled": False,
    "symbol_selection_enabled": False,
    "candidate_reclassification_allowed": False,
    "retired_candidate_mutation_allowed": False,
    "holdout_access_allowed": False,
    "retrospective_lockbox_access_allowed": False,
    "prospective_holdout_access_allowed": False,
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


def _as_bool(series: pd.Series) -> pd.Series:
    if pd.api.types.is_bool_dtype(series):
        return series.fillna(False).astype(bool)
    return series.astype(str).str.strip().str.lower().map(
        {"true": True, "false": False}
    ).fillna(False)


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
    details: str,
    severity: str = "ERROR",
) -> dict[str, Any]:
    return {
        "check_name": check_name,
        "passed": bool(passed),
        "severity": severity,
        "details": details,
        "blocker": severity == "ERROR" and not bool(passed),
    }


def all_permissions_false() -> bool:
    return all(value is False for value in SAFETY_FLAGS.values())


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


def holdout_files_absent() -> bool:
    return not RETROSPECTIVE_LOCKBOX_PATH.exists() and not PROSPECTIVE_HOLDOUT_PATH.exists()


def load_phase_2b_reports() -> tuple[dict[str, pd.DataFrame], pd.DataFrame]:
    frames: dict[str, pd.DataFrame] = {}
    rows: list[dict[str, Any]] = []
    for name, path in PHASE_2B_REQUIRED_REPORTS.items():
        exists = path.exists() and path.is_file()
        frame = pd.DataFrame()
        error = ""
        if exists:
            try:
                frame = pd.read_csv(path)
            except Exception as exc:
                error = f"{type(exc).__name__}: {exc}"
        missing = sorted(PHASE_2B_REQUIRED_COLUMNS[name] - set(frame.columns))
        permits_empty = name == "errors"
        valid = bool(
            exists
            and not error
            and not missing
            and (permits_empty or not frame.empty)
        )
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


def _canonical_frames_equal(left: pd.DataFrame, right: pd.DataFrame) -> bool:
    if list(left.columns) != list(right.columns) or len(left) != len(right):
        return False
    return left.fillna("").astype(str).reset_index(drop=True).equals(
        right.fillna("").astype(str).reset_index(drop=True)
    )


def build_dataset_lineage() -> tuple[pd.DataFrame, bool, bool]:
    current = prepare_dataset_manifest(allow_download=False)
    r2 = pd.DataFrame()
    read_error = ""
    if PHASE_2_DATASET_MANIFEST_PATH.exists():
        try:
            r2 = pd.read_csv(PHASE_2_DATASET_MANIFEST_PATH)
        except Exception as exc:
            read_error = f"{type(exc).__name__}: {exc}"

    manifest_valid = bool(
        len(current) == len(SHORT_SYMBOL_COHORT) * 3
        and current.get("dataset_valid", pd.Series(dtype=bool)).astype(bool).all()
    )
    required = {"symbol", "timeframe", "sha256", "rows", "dataset_valid"}
    r2_valid = bool(
        not read_error
        and not r2.empty
        and required.issubset(r2.columns)
        and _as_bool(r2["dataset_valid"]).all()
    )
    if not r2_valid:
        current["r2_manifest_path"] = str(PHASE_2_DATASET_MANIFEST_PATH)
        current["r2_manifest_read_error"] = read_error
        current["hash_matches_r2"] = False
        current["row_count_matches_r2"] = False
        return current, manifest_valid, False

    lineage = current.merge(
        r2[["symbol", "timeframe", "sha256", "rows"]],
        on=["symbol", "timeframe"],
        how="outer",
        suffixes=("_current", "_r2"),
        validate="one_to_one",
    )
    lineage["hash_matches_r2"] = lineage["sha256_current"].eq(
        lineage["sha256_r2"]
    )
    lineage["row_count_matches_r2"] = lineage["rows_current"].eq(
        lineage["rows_r2"]
    )
    lineage_valid = bool(
        len(lineage) == len(SHORT_SYMBOL_COHORT) * 3
        and lineage["hash_matches_r2"].all()
        and lineage["row_count_matches_r2"].all()
    )
    return lineage, manifest_valid, lineage_valid


def build_closed_candle_signal_context() -> pd.DataFrame:
    rows: list[pd.DataFrame] = []
    for symbol in SHORT_SYMBOL_COHORT:
        context = build_mtf_regime_context(
            dataset_path(symbol, "15m"),
            dataset_path(symbol, "1h"),
            dataset_path(symbol, "4h"),
            MODE_CORRECTED,
        )
        selected = context[["timestamp", "regime_1h", "regime_4h"]].copy()
        selected.insert(0, "symbol", symbol)
        rows.append(selected)
    return pd.concat(rows, ignore_index=True)


def build_diagnostic_contract() -> pd.DataFrame:
    rules = [
        ("DC-001", "evidence", "Only immutable known 2022-2025 development data may be read."),
        ("DC-002", "timing", "Trend context uses CLOSED_CANDLE_CORRECTED at signal_time."),
        ("DC-003", "reference", f"{SHORT_REJECTED_REFERENCE} remains retired and immutable."),
        ("DC-004", "cohort", "BTCUSDT, ETHUSDT and SOLUSDT remain in the fixed cohort."),
        ("DC-005", "slices", "Exactly symbol, calendar_year, volatility_tercile, trend_regime and signal_family are published."),
        ("DC-006", "volatility", f"Volatility uses {VOLATILITY_METHOD} without outcome columns."),
        ("DC-007", "metrics", "Every slice publishes net expectancy R, profit factor, chronological max drawdown, positive-window rate and trade count for all five profiles."),
        ("DC-008", "selection", "Rows are deterministic catalog order; ranking and result-driven selection are forbidden."),
        ("DC-009", "holdout", "Neither retrospective nor prospective holdout may exist or be accessed."),
        ("DC-010", "execution", "No signal, forward write, paper trade, capital, exchange, automation or OpenClaw operational permission is granted."),
    ]
    frame = pd.DataFrame(rules, columns=["contract_id", "category", "locked_rule"])
    frame["mandatory"] = True
    frame["mutable_during_phase"] = False
    return frame


def build_acceptance_criteria() -> pd.DataFrame:
    criteria = [
        ("AC-001", "All eight Phase 2B source reports are valid and Phase 2B closed with zero blockers."),
        ("AC-002", "The 16-rule preregistration and gross-to-net accounting contract exactly match code."),
        ("AC-003", "The exact 205 source x 5 profile grid is preserved and source fields are invariant."),
        ("AC-004", "All nine current OHLCV datasets are valid and hash-identical to the Phase 2 manifest."),
        ("AC-005", "Every source signal receives corrected closed-candle 1H and 4H trend context."),
        ("AC-006", "All three outcome-independent volatility terciles are represented."),
        ("AC-007", "All five preregistered dimensions and all five fixed cost profiles publish complete primary metrics."),
        ("AC-008", "No ranking, selection, candidate mutation, reclassification or execution permission is emitted."),
        ("AC-009", "Both holdouts and every official forward artifact remain absent."),
        ("AC-010", "The run produces zero errors and every ERROR check passes."),
    ]
    return pd.DataFrame(criteria, columns=["criterion_id", "acceptance_criterion"])


def write_outputs(outputs: dict[str, pd.DataFrame]) -> None:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    for name, frame in outputs.items():
        frame.to_csv(REPORTS_DIR / f"{name}_v1.csv", index=False)


def validate_phase_10_42r_2c(
    preflight_only: bool = False,
) -> dict[str, pd.DataFrame]:
    frames, phase_2b_lineage = load_phase_2b_reports()
    errors: list[dict[str, str]] = []
    dataset_lineage, datasets_valid, dataset_lineage_valid = build_dataset_lineage()

    source_reports_valid = bool(
        len(phase_2b_lineage) == len(PHASE_2B_REQUIRED_REPORTS)
        and phase_2b_lineage["report_valid"].astype(bool).all()
    )
    source_summary = frames.get("summary", pd.DataFrame())
    source_checks = frames.get("checks", pd.DataFrame())
    source_completed = bool(
        source_reports_valid
        and not source_summary.empty
        and _as_bool(source_summary["audit_completed"]).all()
        and _as_bool(source_summary["validation_passed"]).all()
        and int(source_summary.iloc[0].get("blocker_count", -1)) == 0
        and not source_checks.empty
        and _as_bool(source_checks["passed"]).all()
        and not _as_bool(source_checks["blocker"]).any()
        and frames.get("errors", pd.DataFrame()).empty
    )

    preregistration = frames.get("recovery_preregistration", pd.DataFrame())
    accounting_contract = frames.get("accounting_contract", pd.DataFrame())
    holdout_contract = frames.get("holdout_contract", pd.DataFrame())
    preregistration_valid = _canonical_frames_equal(
        preregistration,
        build_recovery_preregistration(),
    )
    accounting_contract_valid = _canonical_frames_equal(
        accounting_contract,
        build_accounting_contract(),
    )
    holdout_snapshot_valid = bool(
        len(holdout_contract) == 2
        and {"exists", "access_allowed"}.issubset(holdout_contract.columns)
        and not _as_bool(holdout_contract["exists"]).any()
        and not _as_bool(holdout_contract["access_allowed"]).any()
    )

    normalized = frames.get("normalized_short_trades", pd.DataFrame())
    profiles = [profile.name for profile in build_cost_profiles()]
    expected_source_rows = (
        int(source_summary.iloc[0].get("source_short_next_open_trades", 0))
        if not source_summary.empty
        else 0
    )
    source_summary_contract_valid = bool(
        not source_summary.empty
        and expected_source_rows == EXPECTED_SOURCE_SHORT_TRADES
        and int(source_summary.iloc[0].get("cost_profile_count", 0))
        == len(profiles)
        and int(
            source_summary.iloc[0].get("normalized_trade_profile_rows", 0)
        )
        == EXPECTED_SOURCE_SHORT_TRADES * len(profiles)
        and len(normalized) == EXPECTED_SOURCE_SHORT_TRADES * len(profiles)
        and str(source_summary.iloc[0].get("accounting_contract", ""))
        == ACCOUNTING_CONTRACT
    )
    source_grid_valid, source_grid_details = validate_normalized_source_grid(
        normalized,
        expected_source_rows=expected_source_rows,
        expected_profiles=profiles,
    )
    known_times = pd.to_datetime(
        normalized.get("signal_time", pd.Series(dtype=str)),
        errors="coerce",
        utc=True,
    )
    known_data_only = bool(
        not known_times.empty
        and known_times.notna().all()
        and known_times.min() >= pd.Timestamp("2022-01-01T00:00:00Z")
        and known_times.max() < pd.Timestamp("2026-01-01T00:00:00Z")
    )
    source_permissions_false = bool(
        not normalized.empty
        and {
            "normalized_cost_decision_allowed",
            "candidate_reclassification_allowed",
            "execution_allowed",
        }.issubset(normalized.columns)
        and not normalized[
            [
                "normalized_cost_decision_allowed",
                "candidate_reclassification_allowed",
                "execution_allowed",
            ]
        ].apply(_as_bool).any(axis=None)
    )
    source_candidate_preserved = bool(
        not source_summary.empty
        and {"short_candidate_status", "candidate_reclassified"}.issubset(
            source_summary.columns
        )
        and str(source_summary.iloc[0].get("short_candidate_status", ""))
        == "REVALIDATED_REJECTED_UNCHANGED"
        and not _as_bool(source_summary["candidate_reclassified"]).any()
    )
    source_long_status_preserved = bool(
        not source_summary.empty
        and str(source_summary.iloc[0].get("long_candidate_status", ""))
        == "RESEARCH_ONLY_NOT_APPROVED"
        and not _as_bool(source_summary["candidate_reclassified"]).any()
    )

    preflight_checks = [
        build_check("phase_10_42r_2b_reports_valid", source_reports_valid, f"valid={int(phase_2b_lineage['report_valid'].astype(bool).sum())}/{len(phase_2b_lineage)}"),
        build_check("phase_10_42r_2b_completed_without_blockers", source_completed, "Phase 2B must be completed with all checks passed and no errors."),
        build_check("locked_preregistration_matches_phase_2b", preregistration_valid, "The 16 preregistered rules must match exactly."),
        build_check("accounting_contract_unchanged", accounting_contract_valid, ACCOUNTING_CONTRACT),
        build_check("phase_2b_source_summary_contract_exact", source_summary_contract_valid, f"source_trades={EXPECTED_SOURCE_SHORT_TRADES}, profiles={len(profiles)}, normalized_rows={EXPECTED_SOURCE_SHORT_TRADES * len(profiles)}, accounting={ACCOUNTING_CONTRACT}"),
        build_check("normalized_source_profile_grid_exact", source_grid_valid, source_grid_details),
        build_check("rejected_short_status_preserved", source_candidate_preserved, SHORT_REJECTED_REFERENCE),
        build_check("long_research_status_preserved", source_long_status_preserved, "LONG remains research-only and not approved."),
        build_check("known_development_data_only", known_data_only, f"min={known_times.min() if not known_times.empty else 'missing'}, max={known_times.max() if not known_times.empty else 'missing'}"),
        build_check("current_datasets_valid", datasets_valid, f"valid={int(dataset_lineage.get('dataset_valid', dataset_lineage.get('dataset_valid_current', pd.Series(dtype=bool))).astype(bool).sum())}/{len(dataset_lineage)}"),
        build_check("dataset_hashes_match_phase_10_42r_2", dataset_lineage_valid, str(PHASE_2_DATASET_MANIFEST_PATH)),
        build_check("phase_2b_holdout_snapshot_sealed", holdout_snapshot_valid, "Both Phase 2B holdout rows must be absent and access_allowed=False."),
        build_check("holdout_files_absent_and_unaccessed", holdout_files_absent(), "No Phase 2C code path opens or creates a holdout."),
        build_check("official_forward_artifacts_absent", official_forward_artifacts_absent(), str(OFFICIAL_DATASET_PATH)),
        build_check("source_and_phase_permissions_false", source_permissions_false and all_permissions_false(), str(SAFETY_FLAGS)),
    ]
    preflight_passed = not any(row["blocker"] for row in preflight_checks)

    features = pd.DataFrame()
    thresholds = pd.DataFrame()
    catalog = pd.DataFrame()
    slice_metrics = pd.DataFrame()
    slice_coverage = pd.DataFrame()
    context = pd.DataFrame()

    if not preflight_only and preflight_passed:
        try:
            source_features, thresholds = build_source_trade_features(normalized)
            context = build_closed_candle_signal_context()
            features = attach_closed_candle_context(source_features, context)
            enriched = attach_features_to_normalized(normalized, features)
            catalog = build_slice_catalog(features, list(SHORT_SYMBOL_COHORT))
            slice_metrics = build_slice_metrics(
                enriched,
                catalog,
                symbols=list(SHORT_SYMBOL_COHORT),
                split_names=list(SHORT_WALK_FORWARD_SPLITS),
                split_years=SPLIT_TEST_YEARS,
                expected_profiles=profiles,
            )
            slice_coverage = build_slice_coverage(features, catalog)
        except Exception as exc:
            errors.append(
                {
                    "scope": "PREREGISTERED_DEVELOPMENT_DIAGNOSTIC",
                    "error": f"{type(exc).__name__}: {exc}",
                }
            )

    if preflight_only:
        checks = pd.DataFrame(preflight_checks)
        validation_passed = preflight_passed
        diagnostic_completed = False
        validation_decision = (
            "PHASE_10_42R_2C_PREFLIGHT_PASSED_READY_FOR_DIAGNOSTIC"
            if validation_passed
            else "PHASE_10_42R_2C_PREFLIGHT_FAILED"
        )
        recommended_next_phase = (
            "RUN_PHASE_10_42R_2C_FULL_DIAGNOSTIC"
            if validation_passed
            else "REMEDIATE_PHASE_10_42R_2C_PREFLIGHT_BLOCKERS"
        )
    else:
        context_complete = bool(
            len(features) == expected_source_rows
            and not features.empty
            and not features[["regime_1h", "regime_4h"]].eq("UNKNOWN").any(axis=None)
        )
        volatility_valid = bool(
            len(thresholds) == 1
            and not _as_bool(thresholds["outcome_columns_used"]).any()
            and set(features.get("volatility_tercile", pd.Series(dtype=str)).astype(str))
            == set(VOLATILITY_TERCILES)
        )
        coverage_valid = bool(
            len(slice_coverage) == len(SLICE_DIMENSIONS)
            and set(slice_coverage["slice_dimension"].astype(str))
            == set(SLICE_DIMENSIONS)
            and _as_bool(slice_coverage["coverage_complete"]).all()
        )
        primary_columns = {
            "trade_rows",
            "normalized_average_result_r",
            "normalized_profit_factor",
            "normalized_max_drawdown_r",
            "positive_window_rate",
            "configured_window_rows",
            "frictionless_average_result_r",
            "gross_edge_to_profile_cost_ratio",
        }
        numeric_primary = slice_metrics.reindex(
            columns=sorted(primary_columns)
        ).apply(pd.to_numeric, errors="coerce")
        primary_metrics_valid = bool(
            not slice_metrics.empty
            and primary_columns.issubset(slice_metrics.columns)
            and len(slice_metrics) == len(catalog) * len(profiles)
            and set(slice_metrics["slice_dimension"].astype(str))
            == set(SLICE_DIMENSIONS)
            and set(slice_metrics["cost_profile"].astype(str)) == set(profiles)
            and slice_metrics.groupby(
                ["slice_dimension", "slice_value"]
            )["cost_profile"].nunique().eq(len(profiles)).all()
            and numeric_primary.notna().all(axis=None)
            and np.isfinite(numeric_primary.to_numpy()).all()
            and pd.to_numeric(
                slice_metrics["positive_window_rate"], errors="coerce"
            ).between(0.0, 1.0, inclusive="both").all()
            and pd.to_numeric(
                slice_metrics["trade_rows"], errors="coerce"
            ).gt(0).all()
        )
        no_selection = bool(
            not features.empty
            and not catalog.empty
            and not slice_metrics.empty
            and not _as_bool(features["selection_allowed"]).any()
            and not _as_bool(catalog["ranking_allowed"]).any()
            and not _as_bool(catalog["selection_allowed"]).any()
            and not _as_bool(slice_metrics["ranking_allowed"]).any()
            and not _as_bool(slice_metrics["selection_allowed"]).any()
            and not _as_bool(
                slice_metrics["candidate_reclassification_allowed"]
            ).any()
            and not _as_bool(slice_metrics["execution_allowed"]).any()
        )
        fixed_cohort = bool(
            set(features.get("symbol", pd.Series(dtype=str)).astype(str))
            == set(SHORT_SYMBOL_COHORT)
            and set(
                catalog.loc[
                    catalog["slice_dimension"].eq("symbol"), "slice_value"
                ].astype(str)
            )
            == set(SHORT_SYMBOL_COHORT)
        )
        retired_reference_immutable = bool(
            set(features.get("signal_family", pd.Series(dtype=str)).astype(str))
            == {DIAGNOSTIC_SIGNAL_FAMILY}
            and not source_summary.empty
            and str(source_summary.iloc[0].get("short_candidate_status", ""))
            == "REVALIDATED_REJECTED_UNCHANGED"
            and not _as_bool(source_summary["candidate_reclassified"]).any()
        )
        full_checks = [
            build_check("closed_candle_context_complete_at_every_signal", context_complete, f"features={len(features)}, expected={expected_source_rows}"),
            build_check("outcome_independent_volatility_terciles_complete", volatility_valid, VOLATILITY_METHOD),
            build_check("all_five_preregistered_slices_complete", coverage_valid, f"dimensions={list(SLICE_DIMENSIONS)}"),
            build_check("all_primary_metrics_and_profiles_published", primary_metrics_valid, f"profiles={profiles}"),
            build_check("fixed_symbol_cohort_preserved_without_deletion", fixed_cohort, f"symbols={list(SHORT_SYMBOL_COHORT)}"),
            build_check("retired_short_reference_immutable", retired_reference_immutable, DIAGNOSTIC_SIGNAL_FAMILY),
            build_check("no_ranking_selection_or_reclassification", no_selection, DIAGNOSTIC_STATUS),
            build_check("holdouts_still_absent_after_diagnostic", holdout_files_absent(), "No holdout was created or accessed during diagnostics."),
            build_check("official_forward_artifacts_still_absent", official_forward_artifacts_absent(), str(OFFICIAL_DATASET_PATH)),
            build_check("all_execution_permissions_still_false", all_permissions_false(), str(SAFETY_FLAGS)),
            build_check("no_runtime_errors", not errors, f"errors={len(errors)}"),
        ]
        checks = pd.DataFrame([*preflight_checks, *full_checks])
        validation_passed = bool(
            not checks["blocker"].astype(bool).any() and not errors
        )
        diagnostic_completed = validation_passed
        validation_decision = (
            "PHASE_10_42R_2C_PREREGISTERED_DEVELOPMENT_DIAGNOSTIC_COMPLETED"
            if validation_passed
            else "PHASE_10_42R_2C_PREREGISTERED_DEVELOPMENT_DIAGNOSTIC_FAILED"
        )
        recommended_next_phase = (
            NEXT_PHASE
            if validation_passed
            else "REMEDIATE_PHASE_10_42R_2C_BLOCKERS"
        )

    checks = checks.reset_index(drop=True)
    summary = pd.DataFrame(
        [
            {
                "phase": PHASE,
                "run_mode": (
                    "PREFLIGHT_ONLY"
                    if preflight_only
                    else "KNOWN_DATA_2022_2025_REPORT_ONLY_DIAGNOSTIC"
                ),
                "audit_completed": validation_passed,
                "diagnostic_completed": diagnostic_completed,
                "known_data_only": known_data_only,
                "source_short_trades": expected_source_rows,
                "normalized_trade_profile_rows": len(normalized),
                "cost_profile_count": len(profiles),
                "diagnostic_slice_dimension_count": (
                    int(catalog["slice_dimension"].nunique())
                    if not catalog.empty
                    else 0
                ),
                "diagnostic_slice_value_count": len(catalog),
                "diagnostic_metric_rows": len(slice_metrics),
                "short_candidate_status": "RETIRED_REVALIDATED_REJECTED_UNCHANGED",
                "short_candidate_modified": False,
                "long_candidate_status": "RESEARCH_ONLY_NOT_APPROVED_UNCHANGED",
                "symbol_selected": False,
                "candidate_ranked": False,
                "candidate_reclassified": False,
                "retrospective_lockbox_status": "SEALED_NOT_ACCESSED",
                "prospective_holdout_status": "SEALED_NOT_ACCESSED",
                "official_dataset_exists": OFFICIAL_DATASET_PATH.exists(),
                "official_evidence_rows_written": 0,
                "error_rows": len(errors),
                "total_checks": len(checks),
                "blocker_count": int(checks["blocker"].astype(bool).sum()),
                "validation_passed": validation_passed,
                "validation_decision": validation_decision,
                "recommended_next_phase": recommended_next_phase,
                **SAFETY_FLAGS,
                "total_project_completed": False,
            }
        ]
    )

    holdout_snapshot = holdout_contract.copy()
    if not holdout_snapshot.empty:
        holdout_snapshot["phase_10_42r_2c_access_allowed"] = False
        holdout_snapshot["phase_10_42r_2c_accessed"] = False

    outputs = {
        "summary": summary,
        "checks": checks,
        "phase_2b_report_lineage": phase_2b_lineage,
        "dataset_lineage": dataset_lineage,
        "diagnostic_contract": build_diagnostic_contract(),
        "acceptance_criteria": build_acceptance_criteria(),
        "preregistration_snapshot": preregistration,
        "holdout_contract_snapshot": holdout_snapshot,
        "volatility_thresholds": thresholds,
        "diagnostic_trade_features": features,
        "slice_catalog": catalog,
        "slice_coverage": slice_coverage,
        "slice_metrics": slice_metrics,
        "errors": pd.DataFrame(errors, columns=["scope", "error"]),
    }
    write_outputs(outputs)
    return outputs
