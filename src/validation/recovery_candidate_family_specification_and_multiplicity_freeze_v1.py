from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path
from typing import Any

import pandas as pd

from src.analysis.recovery_candidate_family_specification_v1 import (
    BOOTSTRAP_RESAMPLES,
    EXPECTED_SPECIFICATION_ROOT_SHA256,
    FAMILY_LIMIT,
    FAMILY_WISE_ALPHA,
    FIXED_SYMBOLS,
    FROZEN_FAMILY_COUNT,
    FROZEN_VARIANT_COUNT,
    FROZEN_VARIANTS_PER_FAMILY,
    MULTIPLICITY_METHOD,
    PRIMARY_COST_PROFILE,
    SPECIFICATION_STATUS,
    STRESS_COST_PROFILE,
    SOURCE_PHASE_2C_ARCHIVE_SHA256,
    VARIANT_LIMIT_PER_FAMILY,
    build_acceptance_criteria,
    build_specification_artifacts,
    build_specification_manifest,
    canonical_frame_payload,
    canonical_frame_sha256,
    canonical_sha256,
    validate_new_identifiers_and_no_evaluation,
    validate_registry_limits,
    verify_specification_manifest,
)
from src.execution.cost_aware_filter_v1 import build_cost_profiles
from src.validation.closed_candle_mtf_revalidation_v1 import (
    OFFICIAL_BACKUP_PATH,
    OFFICIAL_DATASET_PATH,
    OFFICIAL_LOCK_PATH,
    OFFICIAL_MANIFEST_PATH,
    OFFICIAL_TEMP_PATH,
)
from src.validation.cost_accounting_normalization_and_strategy_recovery_preregistration_v1 import (
    PROSPECTIVE_HOLDOUT_PATH,
    RETROSPECTIVE_LOCKBOX_PATH,
    SHORT_REJECTED_REFERENCE,
    build_recovery_preregistration,
)


PHASE = "10.42R.2D"
PHASE_2C_ARCHIVE_SHA256 = SOURCE_PHASE_2C_ARCHIVE_SHA256
PHASE_2C_REPORTS_DIR = Path(
    "reports/phase_10_42r_2c_preregistered_strategy_recovery_"
    "development_diagnostic_v1"
)
REPORTS_DIR = Path(
    "reports/phase_10_42r_2d_recovery_candidate_family_specification_"
    "and_multiplicity_freeze_v1"
)
NEXT_PHASE = (
    "PHASE_10_42R_2E_FROZEN_RECOVERY_CANDIDATE_IMPLEMENTATION_"
    "AND_STATIC_CONFORMANCE_V1"
)

PHASE_2C_REPORT_CONTRACT: dict[str, dict[str, Any]] = {
    "acceptance_criteria_v1.csv": {
        "sha256": "38be6b081da55d87103ae9079f018decdbf1c21ac63ab017ebf244619415acd1",
        "size_bytes": 922,
        "rows": 10,
    },
    "checks_v1.csv": {
        "sha256": "7204b0a0787aeab54660ed65cb451df8179eb32b6f23d3b85eed6d9d53a4d20b",
        "size_bytes": 4565,
        "rows": 26,
    },
    "dataset_lineage_v1.csv": {
        "sha256": "49dae06458a25960514042c07b8583badd3dd84c49e80c9b02c786244d7c60e3",
        "size_bytes": 3254,
        "rows": 9,
    },
    "diagnostic_contract_v1.csv": {
        "sha256": "f1901223de37de27263be8acde9d9e12809fe15201a6e681b2465fdf2a6006a6",
        "size_bytes": 1216,
        "rows": 10,
    },
    "diagnostic_trade_features_v1.csv": {
        "sha256": "a805febcfaab488f0eb9ddf0fa16f196feaaedb1591216895b75539ac0ac5133",
        "size_bytes": 96556,
        "rows": 205,
    },
    "errors_v1.csv": {
        "sha256": "7dc76135c6e2cffbc5fa314988e0e2c4213b56170d067aa0393b6de649d7cf82",
        "size_bytes": 13,
        "rows": 0,
    },
    "holdout_contract_snapshot_v1.csv": {
        "sha256": "a6c49d7ec6c20374abab7ca58cb8a7bdfcc812f4040d742635048aa307af9c11",
        "size_bytes": 687,
        "rows": 2,
    },
    "phase_2b_report_lineage_v1.csv": {
        "sha256": "e5187e2060dddde88b28383c135b4531fcf385faf12e7054f6b3cde4e492124c",
        "size_bytes": 1855,
        "rows": 8,
    },
    "preregistration_snapshot_v1.csv": {
        "sha256": "aee516ffb654e132508c866a6f253b2a2665f5f4027c152e7999e6652773ef41",
        "size_bytes": 2189,
        "rows": 16,
    },
    "slice_catalog_v1.csv": {
        "sha256": "de166153a78a2da2848546678d69b8519e1621b99b992ed8edf64664c33275df",
        "size_bytes": 1375,
        "rows": 12,
    },
    "slice_coverage_v1.csv": {
        "sha256": "b123d86734d57efd8d4f301d4ae11ec1c210601462068ba060e33bd8d61547c0",
        "size_bytes": 405,
        "rows": 5,
    },
    "slice_metrics_v1.csv": {
        "sha256": "6cfe9266175d09775062cb1d9623c88d8edb9f98b6f1fa48ff45549b56e837bb",
        "size_bytes": 31580,
        "rows": 60,
    },
    "summary_v1.csv": {
        "sha256": "5779535c3464ba30b5e1ce2a08c9b52968bd57fa2c8831bd5c9232f8682619e6",
        "size_bytes": 1740,
        "rows": 1,
    },
    "volatility_thresholds_v1.csv": {
        "sha256": "2ac46b98d973b1a20dd2b104627655e536df7461ebfb7c044df2cf9b47a7ea0b",
        "size_bytes": 325,
        "rows": 1,
    },
}

SEMANTIC_SOURCE_REPORTS = {
    "summary": "summary_v1.csv",
    "checks": "checks_v1.csv",
    "errors": "errors_v1.csv",
    "preregistration": "preregistration_snapshot_v1.csv",
    "holdout": "holdout_contract_snapshot_v1.csv",
}

SAFETY_FLAGS = {
    "candidate_backtest_allowed": False,
    "comparative_backtest_allowed": False,
    "candidate_evaluation_allowed": False,
    "metric_calculation_allowed": False,
    "performance_comparison_allowed": False,
    "performance_ranking_allowed": False,
    "winner_selection_allowed": False,
    "candidate_promotion_allowed": False,
    "retired_candidate_repair_allowed": False,
    "retired_candidate_mutation_allowed": False,
    "symbol_selection_allowed": False,
    "parameter_optimization_allowed": False,
    "holdout_access_allowed": False,
    "retrospective_lockbox_access_allowed": False,
    "prospective_holdout_access_allowed": False,
    "signal_generation_enabled": False,
    "forward_observation_allowed": False,
    "official_dataset_write_allowed": False,
    "evidence_persistence_allowed": False,
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

FORBIDDEN_SPECIFICATION_IMPORT_PREFIXES = (
    "src.alerts",
    "src.backtesting",
    "src.decision",
    "src.exchange",
    "src.execution",
    "src.journal",
    "src.long_side",
    "src.paper_trading",
    "src.short_side",
    "src.strategies",
    "src.validation",
    "src.workflows",
)
SPECIFICATION_MODULE_PATH = Path(
    "src/analysis/recovery_candidate_family_specification_v1.py"
)


def _as_bool(series: pd.Series) -> pd.Series:
    if pd.api.types.is_bool_dtype(series):
        return series.fillna(False).astype(bool)
    return (
        series.astype(str)
        .str.strip()
        .str.lower()
        .map({"true": True, "false": False})
        .fillna(False)
    )


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


def holdout_files_absent() -> bool:
    return bool(
        not RETROSPECTIVE_LOCKBOX_PATH.exists()
        and not PROSPECTIVE_HOLDOUT_PATH.exists()
    )


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


def load_phase_2c_report_lineage() -> tuple[dict[str, pd.DataFrame], pd.DataFrame]:
    rows: list[dict[str, Any]] = []
    frames: dict[str, pd.DataFrame] = {}
    semantic_by_file = {
        filename: name for name, filename in SEMANTIC_SOURCE_REPORTS.items()
    }
    for filename, expected in PHASE_2C_REPORT_CONTRACT.items():
        path = PHASE_2C_REPORTS_DIR / filename
        exists = path.exists() and path.is_file()
        actual_hash = file_sha256(path)
        size_bytes = path.stat().st_size if exists else 0
        actual_rows = -1
        read_error = ""
        if exists:
            try:
                with path.open("rb") as handle:
                    actual_rows = max(0, len(handle.read().splitlines()) - 1)
            except Exception as exc:
                read_error = f"{type(exc).__name__}: {exc}"
        if filename in semantic_by_file and exists and not read_error:
            try:
                frames[semantic_by_file[filename]] = pd.read_csv(path)
            except Exception as exc:
                read_error = f"{type(exc).__name__}: {exc}"
                frames[semantic_by_file[filename]] = pd.DataFrame()
        exact = bool(
            exists
            and not read_error
            and actual_hash == expected["sha256"]
            and size_bytes == expected["size_bytes"]
            and actual_rows == expected["rows"]
        )
        rows.append(
            {
                "report_order": len(rows) + 1,
                "report_name": filename,
                "path": str(path),
                "exists": exists,
                "expected_sha256": expected["sha256"],
                "actual_sha256": actual_hash,
                "hash_matches": actual_hash == expected["sha256"],
                "expected_size_bytes": expected["size_bytes"],
                "actual_size_bytes": size_bytes,
                "size_matches": size_bytes == expected["size_bytes"],
                "expected_rows": expected["rows"],
                "actual_rows": actual_rows,
                "row_count_matches": actual_rows == expected["rows"],
                "semantic_content_loaded": filename in semantic_by_file,
                "read_error": read_error,
                "report_exact": exact,
            }
        )
    for semantic_name in SEMANTIC_SOURCE_REPORTS:
        frames.setdefault(semantic_name, pd.DataFrame())
    return frames, pd.DataFrame(rows)


def _canonical_frames_equal(left: pd.DataFrame, right: pd.DataFrame) -> bool:
    return canonical_frame_payload(left) == canonical_frame_payload(right)


def specification_imports_are_safe() -> tuple[bool, str]:
    if not SPECIFICATION_MODULE_PATH.exists():
        return False, f"missing={SPECIFICATION_MODULE_PATH}"
    tree = ast.parse(
        SPECIFICATION_MODULE_PATH.read_text(encoding="utf-8"),
        filename=str(SPECIFICATION_MODULE_PATH),
    )
    imported: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module)
    forbidden = sorted(
        module
        for module in imported
        if any(
            module == prefix or module.startswith(prefix + ".")
            for prefix in FORBIDDEN_SPECIFICATION_IMPORT_PREFIXES
        )
    )
    return not forbidden, f"imports={sorted(imported)}, forbidden={forbidden}"


def _contract_map(frame: pd.DataFrame) -> dict[str, Any]:
    return {
        str(row.contract_key): json.loads(str(row.locked_value_json))
        for row in frame.itertuples(index=False)
    }


def _family_rules_complete(families: pd.DataFrame) -> bool:
    required_rule_keys = {
        "context",
        "features",
        "all_entry_conditions",
        "stop_formula",
        "target_formula",
    }
    try:
        rules = [json.loads(value) for value in families["rule_json"]]
    except Exception:
        return False
    return bool(
        rules
        and all(set(rule) == required_rule_keys for rule in rules)
        and all(rule["all_entry_conditions"] for rule in rules)
        and all(rule["features"] for rule in rules)
    )


def _internal_specification_hashes_valid(
    artifacts: dict[str, pd.DataFrame],
) -> tuple[bool, str]:
    rebuilt = build_specification_artifacts()
    equal = bool(
        tuple(artifacts) == tuple(rebuilt)
        and all(
            canonical_frame_sha256(artifacts[name])
            == canonical_frame_sha256(rebuilt[name])
            for name in rebuilt
        )
    )
    return equal, f"artifacts={len(artifacts)}, exact_rebuild={equal}"


def write_outputs(outputs: dict[str, pd.DataFrame]) -> None:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    for name, frame in outputs.items():
        frame.to_csv(REPORTS_DIR / f"{name}_v1.csv", index=False)


def validate_phase_10_42r_2d(
    preflight_only: bool = False,
) -> dict[str, pd.DataFrame]:
    source_frames, source_lineage = load_phase_2c_report_lineage()
    errors: list[dict[str, str]] = []
    summary_2c = source_frames["summary"]
    checks_2c = source_frames["checks"]
    errors_2c = source_frames["errors"]
    preregistration_2c = source_frames["preregistration"]
    holdout_2c = source_frames["holdout"]

    source_reports_exact = bool(
        len(source_lineage) == len(PHASE_2C_REPORT_CONTRACT)
        and source_lineage["report_exact"].astype(bool).all()
    )
    phase_2c_summary_valid = bool(
        source_reports_exact
        and len(summary_2c) == 1
        and _as_bool(summary_2c["diagnostic_completed"]).all()
        and _as_bool(summary_2c["validation_passed"]).all()
        and int(summary_2c.iloc[0].get("source_short_trades", 0)) == 205
        and int(summary_2c.iloc[0].get("normalized_trade_profile_rows", 0))
        == 1025
        and int(summary_2c.iloc[0].get("diagnostic_metric_rows", 0)) == 60
        and int(summary_2c.iloc[0].get("blocker_count", -1)) == 0
        and int(summary_2c.iloc[0].get("error_rows", -1)) == 0
    )
    phase_2c_checks_valid = bool(
        len(checks_2c) == 26
        and checks_2c.get("check_name", pd.Series(dtype=str)).is_unique
        and _as_bool(checks_2c.get("passed", pd.Series(dtype=bool))).all()
        and not _as_bool(checks_2c.get("blocker", pd.Series(dtype=bool))).any()
    )
    phase_2c_errors_empty = bool(
        set(errors_2c.columns) == {"scope", "error"} and errors_2c.empty
    )
    preregistration_matches = _canonical_frames_equal(
        preregistration_2c,
        build_recovery_preregistration(),
    )
    phase_2c_statuses_preserved = bool(
        len(summary_2c) == 1
        and str(summary_2c.iloc[0].get("short_candidate_status", ""))
        == "RETIRED_REVALIDATED_REJECTED_UNCHANGED"
        and str(summary_2c.iloc[0].get("long_candidate_status", ""))
        == "RESEARCH_ONLY_NOT_APPROVED_UNCHANGED"
        and not _as_bool(summary_2c["candidate_reclassified"]).any()
    )
    phase_2c_permission_columns = [
        column
        for column in summary_2c.columns
        if column.endswith("_allowed") or column.endswith("_enabled")
    ]
    phase_2c_permissions_false = bool(
        phase_2c_permission_columns
        and not summary_2c[phase_2c_permission_columns].apply(_as_bool).any(axis=None)
    )
    phase_2c_holdout_snapshot_sealed = bool(
        len(holdout_2c) == 2
        and {
            "exists",
            "access_allowed",
            "phase_10_42r_2c_access_allowed",
            "phase_10_42r_2c_accessed",
        }.issubset(holdout_2c.columns)
        and not holdout_2c[
            [
                "exists",
                "access_allowed",
                "phase_10_42r_2c_access_allowed",
                "phase_10_42r_2c_accessed",
            ]
        ].apply(_as_bool).any(axis=None)
    )
    imports_safe, import_details = specification_imports_are_safe()

    preflight_checks = [
        build_check("phase_2c_all_14_reports_hash_exact", source_reports_exact, f"exact={int(source_lineage['report_exact'].astype(bool).sum())}/{len(source_lineage)}"),
        build_check("phase_2c_summary_contract_completed", phase_2c_summary_valid, "Phase 2C must retain 205 source rows, 1025 normalized rows, 60 metric rows and zero blockers."),
        build_check("phase_2c_all_26_checks_passed", phase_2c_checks_valid, f"checks={len(checks_2c)}"),
        build_check("phase_2c_errors_empty", phase_2c_errors_empty, f"errors={len(errors_2c)}"),
        build_check("phase_2c_preregistration_unchanged", preregistration_matches, "The exact 16-rule Phase 2B preregistration must persist."),
        build_check("phase_2c_candidate_statuses_preserved", phase_2c_statuses_preserved, SHORT_REJECTED_REFERENCE),
        build_check("phase_2c_permissions_all_false", phase_2c_permissions_false, f"permission_columns={phase_2c_permission_columns}"),
        build_check("phase_2c_archive_reference_frozen", len(PHASE_2C_ARCHIVE_SHA256) == 64, PHASE_2C_ARCHIVE_SHA256),
        build_check("phase_2c_holdout_snapshot_sealed", phase_2c_holdout_snapshot_sealed, "Both Phase 2C holdout rows must remain absent and unaccessed."),
        build_check("phase_2d_holdout_files_absent", holdout_files_absent(), "Phase 2D cannot open or create either holdout."),
        build_check("official_forward_artifacts_absent", official_forward_artifacts_absent(), str(OFFICIAL_DATASET_PATH)),
        build_check("phase_2d_all_permissions_false", all_permissions_false(), str(SAFETY_FLAGS)),
        build_check("specification_module_has_no_project_runtime_imports", imports_safe, import_details),
        build_check("phase_2d_source_is_reports_only", bool(source_lineage["semantic_content_loaded"].sum() == len(SEMANTIC_SOURCE_REPORTS)), "Only five semantic Phase 2C contracts are loaded; outcome tables are hash-only."),
    ]
    preflight_passed = not any(row["blocker"] for row in preflight_checks)

    blueprint_artifacts = build_specification_artifacts()
    blueprint_manifest, blueprint_root = build_specification_manifest(
        blueprint_artifacts
    )
    artifacts: dict[str, pd.DataFrame] = {
        name: frame.iloc[0:0].copy()
        for name, frame in blueprint_artifacts.items()
    }
    manifest = blueprint_manifest.iloc[0:0].copy()
    root = blueprint_root.iloc[0:0].copy()
    if not preflight_only and preflight_passed:
        try:
            artifacts = blueprint_artifacts
            manifest = blueprint_manifest
            root = blueprint_root
        except Exception as exc:
            errors.append(
                {
                    "scope": "RECOVERY_CANDIDATE_SPECIFICATION_FREEZE",
                    "error": f"{type(exc).__name__}: {exc}",
                }
            )

    if preflight_only:
        checks = pd.DataFrame(preflight_checks)
        validation_passed = preflight_passed
        specification_completed = False
        validation_decision = (
            "PHASE_10_42R_2D_PREFLIGHT_PASSED_READY_FOR_SPECIFICATION_FREEZE"
            if validation_passed
            else "PHASE_10_42R_2D_PREFLIGHT_FAILED"
        )
        recommended_next_phase = (
            "RUN_PHASE_10_42R_2D_FULL_SPECIFICATION_FREEZE"
            if validation_passed
            else "REMEDIATE_PHASE_10_42R_2D_PREFLIGHT_BLOCKERS"
        )
    else:
        families = artifacts.get("candidate_family_registry", pd.DataFrame())
        variants = artifacts.get("candidate_variant_registry", pd.DataFrame())
        common = artifacts.get("common_execution_contract", pd.DataFrame())
        costs = artifacts.get("cost_profile_freeze", pd.DataFrame())
        evaluation_order = artifacts.get("evaluation_order", pd.DataFrame())
        multiplicity = artifacts.get("multiplicity_contract", pd.DataFrame())
        gates = artifacts.get("promotion_gate_contract", pd.DataFrame())
        holdout_boundary = artifacts.get("holdout_boundary", pd.DataFrame())

        registry_valid, registry_details = (
            validate_registry_limits(families, variants)
            if not families.empty and not variants.empty
            else (False, "empty registries")
        )
        identity_valid, identity_details = (
            validate_new_identifiers_and_no_evaluation(families, variants)
            if not families.empty and not variants.empty
            else (False, "empty registries")
        )
        common_map = _contract_map(common) if not common.empty else {}
        fixed_cohort_valid = common_map.get("fixed_symbol_cohort") == list(
            FIXED_SYMBOLS
        )
        timing_valid = bool(
            common_map.get("higher_timeframe_availability")
            == "CLOSED_CANDLE_CORRECTED"
            and common_map.get("signal_confirmation") == "CLOSED_15M_BAR_T"
            and common_map.get("fill_contract") == "NEXT_15M_BAR_OPEN_T_PLUS_1"
            and common_map.get("simultaneous_stop_target_resolution")
            == "STOP_FIRST_PESSIMISTIC"
            and common_map.get("fixed_reward_to_risk") == 2.5
            and common_map.get("evaluation_allowed_in_phase_2d") is False
            and common_map.get("retired_reference_import_allowed") is False
        )
        source_cost_profiles = build_cost_profiles()
        expected_profiles = [profile.name for profile in source_cost_profiles]
        cost_comparison_columns = [
            "profile_order",
            "name",
            "platform",
            "mode",
            "fee_pct_round_trip",
            "spread_pct_round_trip",
            "slippage_pct_round_trip",
            "funding_or_time_cost_pct",
            "safety_buffer_pct",
            "total_cost_pct",
            "default_risk_pct",
            "risk_per_trade_pct",
        ]
        expected_cost_snapshot = pd.DataFrame(
            [
                {
                    "profile_order": order,
                    "name": profile.name,
                    "platform": profile.platform,
                    "mode": profile.mode,
                    "fee_pct_round_trip": profile.fee_pct_round_trip,
                    "spread_pct_round_trip": profile.spread_pct_round_trip,
                    "slippage_pct_round_trip": profile.slippage_pct_round_trip,
                    "funding_or_time_cost_pct": profile.funding_or_time_cost_pct,
                    "safety_buffer_pct": profile.safety_buffer_pct,
                    "total_cost_pct": profile.total_cost_pct,
                    "default_risk_pct": profile.default_risk_pct,
                    "risk_per_trade_pct": profile.risk_per_trade_pct,
                }
                for order, profile in enumerate(source_cost_profiles, start=1)
            ]
        )
        cost_valid = bool(
            len(costs) == 5
            and costs["name"].astype(str).tolist() == expected_profiles
            and _canonical_frames_equal(
                costs[cost_comparison_columns],
                expected_cost_snapshot[cost_comparison_columns],
            )
            and not _as_bool(costs["mutable_after_freeze"]).any()
        )
        order_valid = bool(
            len(evaluation_order) == FROZEN_VARIANT_COUNT
            and evaluation_order["evaluation_order"].astype(int).tolist()
            == list(range(1, FROZEN_VARIANT_COUNT + 1))
            and evaluation_order["variant_id"].astype(str).tolist()
            == variants["variant_id"].astype(str).tolist()
            and not evaluation_order[
                [
                    "order_implies_performance_rank",
                    "early_stopping_allowed",
                    "evaluation_allowed_in_phase_2d",
                    "mutable_after_freeze",
                ]
            ].apply(_as_bool).any(axis=None)
        )
        multiplicity_map = _contract_map(multiplicity) if not multiplicity.empty else {}
        multiplicity_valid = bool(
            multiplicity_map.get("frozen_family_count") == FROZEN_FAMILY_COUNT
            and multiplicity_map.get("variants_per_family")
            == FROZEN_VARIANTS_PER_FAMILY
            and multiplicity_map.get("frozen_total_variant_count")
            == FROZEN_VARIANT_COUNT
            and multiplicity_map.get("maximum_family_count") == FAMILY_LIMIT
            and multiplicity_map.get("maximum_variants_per_family")
            == VARIANT_LIMIT_PER_FAMILY
            and multiplicity_map.get("primary_cost_profile")
            == PRIMARY_COST_PROFILE
            and multiplicity_map.get("multiplicity_method")
            == MULTIPLICITY_METHOD
            and multiplicity_map.get("bootstrap_resamples") == BOOTSTRAP_RESAMPLES
            and multiplicity_map.get("family_wise_alpha") == FAMILY_WISE_ALPHA
            and multiplicity_map.get("performance_ranking_allowed") is False
            and multiplicity_map.get("winner_selection_allowed_in_evaluation_phase")
            is False
        )
        required_gates = {
            "AGGREGATE_OOS_TRADE_COUNT": ("GREATER_THAN_OR_EQUAL", "100"),
            "MINIMUM_OOS_TRADES_PER_SYMBOL": ("GREATER_THAN_OR_EQUAL", "20"),
            "STRESS_NORMALIZED_AVERAGE_RESULT_R": ("GREATER_THAN_OR_EQUAL", "0.0"),
            "STRESS_NORMALIZED_PROFIT_FACTOR": ("GREATER_THAN_OR_EQUAL", "1.0"),
            "HOLM_ADJUSTED_PRIMARY_P_VALUE": ("LESS_THAN_OR_EQUAL", "0.05"),
        }
        gate_lookup = {
            str(row.metric): (str(row.operator), str(row.threshold_json))
            for row in gates.itertuples(index=False)
        }
        gates_valid = bool(
            len(gates) == 14
            and all(gate_lookup.get(metric) == expected for metric, expected in required_gates.items())
            and _as_bool(gates["mandatory"]).all()
            and not _as_bool(gates["override_allowed"]).any()
            and not _as_bool(gates["mutable_after_freeze"]).any()
        )
        internal_hashes_valid, internal_hash_details = (
            _internal_specification_hashes_valid(artifacts)
            if artifacts
            else (False, "no artifacts")
        )
        manifest_valid, manifest_details = (
            verify_specification_manifest(artifacts, manifest, root)
            if artifacts and not manifest.empty and not root.empty
            else (False, "manifest/root absent")
        )
        holdout_boundary_valid = bool(
            len(holdout_boundary) == 2
            and _as_bool(holdout_boundary["phase_2d_must_be_absent"]).all()
            and not holdout_boundary[
                [
                    "phase_2d_access_allowed",
                    "phase_2d_open_allowed",
                    "future_open_permission_granted",
                    "mutable_after_freeze",
                ]
            ].apply(_as_bool).any(axis=None)
            and holdout_files_absent()
        )
        forbidden_output_names = sorted(
            name
            for name in artifacts
            if any(
                token in name
                for token in ("backtest", "comparison", "ranking", "winner", "trade_results")
            )
        )
        no_evaluation_outputs = bool(
            not forbidden_output_names
            and not variants.empty
            and pd.to_numeric(variants["result_rows"], errors="coerce").eq(0).all()
            and not _as_bool(variants["evaluated"]).any()
        )
        root_valid = bool(
            len(root) == 1
            and str(root.iloc[0].get("status", "")) == SPECIFICATION_STATUS
            and str(root.iloc[0].get("specification_root_sha256", ""))
            == EXPECTED_SPECIFICATION_ROOT_SHA256
            and not root[
                [
                    "evaluation_allowed",
                    "selection_allowed",
                    "holdout_access_allowed",
                    "mutable_after_freeze",
                ]
            ].apply(_as_bool).any(axis=None)
        )

        full_checks = [
            build_check("family_and_variant_limits_frozen", registry_valid, registry_details),
            build_check("new_identifiers_and_no_retired_repair", identity_valid, identity_details),
            build_check("fixed_three_symbol_cohort_frozen", fixed_cohort_valid, str(common_map.get("fixed_symbol_cohort"))),
            build_check("family_rules_are_complete_and_deterministic", _family_rules_complete(families), f"families={len(families)}"),
            build_check("closed_candle_next_open_timing_frozen", timing_valid, str({key: common_map.get(key) for key in ('higher_timeframe_availability','signal_confirmation','fill_contract','fixed_reward_to_risk')})),
            build_check("all_five_cost_profiles_frozen_exact", cost_valid, f"profiles={expected_profiles}"),
            build_check("evaluation_order_frozen_without_ranking", order_valid, f"orders={evaluation_order.get('evaluation_order', pd.Series(dtype=int)).tolist()}"),
            build_check("multiplicity_contract_frozen", multiplicity_valid, str(multiplicity_map)),
            build_check("minimum_evidence_and_stress_gates_frozen", gates_valid, str(required_gates)),
            build_check("internal_specification_hashes_reproduce", internal_hashes_valid, internal_hash_details),
            build_check("artifact_manifest_and_golden_root_sha_reproduce", manifest_valid, manifest_details),
            build_check("holdout_boundary_frozen_closed", holdout_boundary_valid, "No Phase 2D or future open permission is granted."),
            build_check("no_backtest_comparison_ranking_or_winner_outputs", no_evaluation_outputs, f"forbidden={forbidden_output_names}"),
            build_check("root_status_and_all_permissions_false", root_valid and all_permissions_false() and not errors, f"root_valid={root_valid}, errors={len(errors)}"),
        ]
        checks = pd.DataFrame([*preflight_checks, *full_checks])
        validation_passed = bool(
            not checks["blocker"].astype(bool).any() and not errors
        )
        specification_completed = validation_passed
        validation_decision = (
            "PHASE_10_42R_2D_RECOVERY_CANDIDATE_SPECIFICATION_AND_MULTIPLICITY_FREEZE_COMPLETED"
            if validation_passed
            else "PHASE_10_42R_2D_SPECIFICATION_FREEZE_FAILED"
        )
        recommended_next_phase = (
            NEXT_PHASE if validation_passed else "REMEDIATE_PHASE_10_42R_2D_BLOCKERS"
        )

    checks = checks.reset_index(drop=True)
    root_sha = (
        str(root.iloc[0]["specification_root_sha256"]) if not root.empty else ""
    )
    summary = pd.DataFrame(
        [
            {
                "phase": PHASE,
                "run_mode": "PREFLIGHT_ONLY" if preflight_only else "SPECIFICATION_FREEZE_ONLY",
                "audit_completed": validation_passed,
                "specification_completed": specification_completed,
                "source_phase_2c_archive_sha256": PHASE_2C_ARCHIVE_SHA256,
                "source_phase_2c_report_count": len(source_lineage),
                "family_count": len(artifacts.get("candidate_family_registry", pd.DataFrame())),
                "variant_count": len(artifacts.get("candidate_variant_registry", pd.DataFrame())),
                "maximum_family_count": FAMILY_LIMIT,
                "maximum_variants_per_family": VARIANT_LIMIT_PER_FAMILY,
                "cost_profile_count": len(artifacts.get("cost_profile_freeze", pd.DataFrame())),
                "promotion_gate_count": len(artifacts.get("promotion_gate_contract", pd.DataFrame())),
                "specification_artifact_count": len(manifest),
                "specification_root_sha256": root_sha,
                "short_candidate_status": "RETIRED_REVALIDATED_REJECTED_UNCHANGED",
                "long_candidate_status": "RESEARCH_ONLY_NOT_APPROVED_UNCHANGED",
                "candidate_backtest_rows": 0,
                "candidate_comparison_rows": 0,
                "candidate_result_rows": 0,
                "winner_selected": False,
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

    outputs: dict[str, pd.DataFrame] = {
        "summary": summary,
        "checks": checks,
        "phase_2c_report_lineage": source_lineage,
        "acceptance_criteria": build_acceptance_criteria(),
        **artifacts,
        "specification_artifact_manifest": manifest,
        "specification_root": root,
        "errors": pd.DataFrame(errors, columns=["scope", "error"]),
    }
    write_outputs(outputs)
    return outputs
