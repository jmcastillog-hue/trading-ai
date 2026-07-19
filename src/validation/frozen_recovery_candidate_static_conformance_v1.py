from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path
from typing import Any

import pandas as pd

from src.analysis.frozen_recovery_candidate_implementation_v1 import (
    EXPECTED_VARIANT_IDS,
    FAMILY_HANDLER_VERSIONS,
    IMPLEMENTATION_SCHEMA_VERSION,
    SOURCE_PHASE_2D_COMMIT,
    SOURCE_PHASE_2D_SPECIFICATION_MODULE_SHA256,
    SYNTHETIC_FIXTURE_SOURCE,
    ClosedMtfContext,
    FrozenSpecificationError,
    FrozenVariantImplementation,
    OrderDecision,
    SignalDecision,
    SyntheticBar,
    breakdown_condition,
    build_verified_implementations,
    construct_next_open_short_order,
    ema_close_span,
    ema_pullback_condition,
    evaluate_frozen_signal,
    mtf_context_is_closed_and_allowed,
    resolve_short_exit,
    retest_condition,
    verify_phase_2d_specification_root,
    wilder_atr14,
)
from src.analysis.recovery_candidate_family_specification_v1 import (
    EXPECTED_SPECIFICATION_ROOT_SHA256,
    build_specification_artifacts,
    canonical_frame_sha256,
    canonical_sha256,
)


PHASE = "10.42R.2E"
REPORTS_DIR = Path(
    "reports/phase_10_42r_2e_frozen_recovery_candidate_implementation_"
    "and_static_conformance_v1"
)
IMPLEMENTATION_MODULE_PATH = Path(
    "src/analysis/frozen_recovery_candidate_implementation_v1.py"
)
PHASE_2D_SPECIFICATION_MODULE_PATH = Path(
    "src/analysis/recovery_candidate_family_specification_v1.py"
)
RETROSPECTIVE_LOCKBOX_PATH = Path(
    "data/holdout/strategy_recovery_retrospective_lockbox_2026h1_v1.csv"
)
PROSPECTIVE_HOLDOUT_PATH = Path(
    "data/holdout/strategy_recovery_prospective_20260720_20270120_v1.csv"
)
OFFICIAL_FORWARD_PATHS = (
    Path("data/forward/long_forward_observation_dataset_v1.csv"),
    Path("data/forward/long_forward_observation_dataset_v1.csv.tmp"),
    Path("data/forward/long_forward_observation_dataset_v1.csv.lock"),
    Path("data/forward/long_forward_observation_dataset_v1.manifest.json"),
    Path("data/forward/long_forward_observation_dataset_v1.csv.backup"),
)
NEXT_PHASE = (
    "PHASE_10_42R_2F_FROZEN_RECOVERY_CANDIDATE_IMPLEMENTATION_"
    "INDEPENDENT_CODE_REVIEW_V1"
)
EXPECTED_IMPLEMENTATION_ROOT_SHA256 = (
    "c360cae27f60d7854521a769abb569f730f7e50137076b86abf7d1e4e77e4ef1"
)

SHORT_STATUS = "RETIRED_REVALIDATED_REJECTED_UNCHANGED"
LONG_STATUS = "RESEARCH_ONLY_NOT_APPROVED_UNCHANGED"

SAFETY_FLAGS = {
    "real_ohlcv_access_allowed": False,
    "historical_dataset_access_allowed": False,
    "phase_result_report_read_allowed": False,
    "candidate_backtest_allowed": False,
    "comparative_backtest_allowed": False,
    "candidate_evaluation_allowed": False,
    "performance_metric_calculation_allowed": False,
    "performance_comparison_allowed": False,
    "performance_ranking_allowed": False,
    "winner_selection_allowed": False,
    "candidate_promotion_allowed": False,
    "symbol_selection_allowed": False,
    "parameter_optimization_allowed": False,
    "retired_candidate_repair_allowed": False,
    "retired_candidate_mutation_allowed": False,
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

ALLOWED_IMPLEMENTATION_IMPORTS = {
    "__future__",
    "dataclasses",
    "json",
    "math",
    "typing",
    "src.analysis.recovery_candidate_family_specification_v1",
}
FORBIDDEN_CALL_NAMES = {
    "open",
    "read_csv",
    "read_excel",
    "read_json",
    "read_parquet",
    "urlopen",
    "request",
    "get",
    "post",
}
FORBIDDEN_LITERAL_TOKENS = (
    "data/",
    "reports/",
    ".csv",
    ".parquet",
    ".xlsx",
    "http://",
    "https://",
    "holdout",
)
FORBIDDEN_OUTPUT_NAME_TOKENS = (
    "backtest",
    "performance_metric",
    "comparison",
    "ranking",
    "winner",
    "trade_result",
    "pnl",
)


def normalized_source_sha256(path: Path) -> str:
    if not path.exists() or not path.is_file():
        return ""
    source = path.read_text(encoding="utf-8")
    normalized = source.replace("\r\n", "\n").replace("\r", "\n")
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def build_check(
    name: str,
    passed: bool,
    details: str,
    severity: str = "ERROR",
) -> dict[str, Any]:
    return {
        "check_name": name,
        "passed": bool(passed),
        "severity": severity,
        "details": details,
        "blocker": severity == "ERROR" and not bool(passed),
    }


def all_permissions_false() -> bool:
    return all(value is False for value in SAFETY_FLAGS.values())


def sealed_inputs_absent() -> bool:
    return bool(
        not RETROSPECTIVE_LOCKBOX_PATH.exists()
        and not PROSPECTIVE_HOLDOUT_PATH.exists()
        and not any(path.exists() for path in OFFICIAL_FORWARD_PATHS)
    )


def implementation_source_is_static_and_safe() -> tuple[bool, str]:
    if not IMPLEMENTATION_MODULE_PATH.exists():
        return False, f"missing={IMPLEMENTATION_MODULE_PATH}"
    try:
        source = IMPLEMENTATION_MODULE_PATH.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(IMPLEMENTATION_MODULE_PATH))
    except Exception as exc:
        return False, f"source read/parse failed: {type(exc).__name__}: {exc}"
    imports: set[str] = set()
    calls: set[str] = set()
    literals: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.add(node.module)
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                calls.add(node.func.id)
            elif isinstance(node.func, ast.Attribute):
                calls.add(node.func.attr)
        elif isinstance(node, ast.Constant) and isinstance(node.value, str):
            literals.append(node.value.lower().replace("\\", "/"))
    forbidden_imports = sorted(imports - ALLOWED_IMPLEMENTATION_IMPORTS)
    forbidden_calls = sorted(calls & FORBIDDEN_CALL_NAMES)
    forbidden_literals = sorted(
        {
            token
            for token in FORBIDDEN_LITERAL_TOKENS
            if any(token in literal for literal in literals)
        }
    )
    passed = not forbidden_imports and not forbidden_calls and not forbidden_literals
    return passed, (
        f"imports={sorted(imports)}, forbidden_imports={forbidden_imports}, "
        f"forbidden_calls={forbidden_calls}, forbidden_literals={forbidden_literals}"
    )


def _closed_context(
    *,
    regime_1h: str = "BEARISH",
    regime_4h: str = "STRONG_BEARISH",
    signal_close: int = 100,
    available_1h: int = 100,
    available_4h: int = 100,
) -> ClosedMtfContext:
    return ClosedMtfContext(
        regime_1h=regime_1h,
        regime_4h=regime_4h,
        signal_close_unit=signal_close,
        regime_1h_available_unit=available_1h,
        regime_4h_available_unit=available_4h,
    )


def _flat_history(count: int = 120) -> tuple[SyntheticBar, ...]:
    return tuple(SyntheticBar(99.7, 100.0, 99.0, 99.5) for _ in range(count))


def _f01_current() -> SyntheticBar:
    return SyntheticBar(100.5, 101.0, 99.5, 100.0)


def _f02_history(count: int = 120) -> tuple[SyntheticBar, ...]:
    bars = [SyntheticBar(100.6, 101.0, 100.0, 100.5) for _ in range(count)]
    bars.append(SyntheticBar(100.0, 100.2, 99.2, 99.4))
    return tuple(bars)


def _f02_current() -> SyntheticBar:
    return SyntheticBar(99.9, 100.0, 99.2, 99.5)


def _ema_trend_history(count: int = 230) -> tuple[SyntheticBar, ...]:
    bars: list[SyntheticBar] = []
    for index in range(count):
        close = 200.0 - 0.1 * index
        bars.append(SyntheticBar(close + 0.05, close + 0.2, close - 0.2, close))
    return tuple(bars)


def _ema_current() -> SyntheticBar:
    return SyntheticBar(177.4, 178.2, 176.8, 177.0)


def _case_row(
    order: int,
    case_id: str,
    category: str,
    variant_id: str,
    expected: str,
    observed: str,
) -> dict[str, Any]:
    return {
        "case_order": order,
        "case_id": case_id,
        "category": category,
        "variant_id": variant_id,
        "fixture_source": SYNTHETIC_FIXTURE_SOURCE,
        "expected_outcome": expected,
        "observed_outcome": observed,
        "passed": expected == observed,
        "real_data_rows": 0,
        "candidate_performance_rows": 0,
        "comparison_rows": 0,
        "ranking_rows": 0,
        "winner_rows": 0,
    }


def run_synthetic_conformance_cases(
    implementations: tuple[FrozenVariantImplementation, ...],
) -> pd.DataFrame:
    by_id = {item.variant_id: item for item in implementations}
    rows: list[dict[str, Any]] = []

    def add(
        case_id: str,
        category: str,
        variant_id: str,
        expected: str,
        observed: str,
    ) -> None:
        rows.append(
            _case_row(
                len(rows) + 1,
                case_id,
                category,
                variant_id,
                expected,
                observed,
            )
        )

    positive_inputs = {
        EXPECTED_VARIANT_IDS[0]: (_flat_history(), _f01_current()),
        EXPECTED_VARIANT_IDS[1]: (_flat_history(), _f01_current()),
        EXPECTED_VARIANT_IDS[2]: (_f02_history(), _f02_current()),
        EXPECTED_VARIANT_IDS[3]: (_f02_history(), _f02_current()),
        EXPECTED_VARIANT_IDS[4]: (_ema_trend_history(), _ema_current()),
        EXPECTED_VARIANT_IDS[5]: (_ema_trend_history(), _ema_current()),
    }
    positive_decisions: dict[str, SignalDecision] = {}
    for variant_id in EXPECTED_VARIANT_IDS:
        history, current = positive_inputs[variant_id]
        decision = evaluate_frozen_signal(
            by_id[variant_id],
            history=history,
            current=current,
            context=_closed_context(),
        )
        positive_decisions[variant_id] = decision
        add(
            f"POS-{len(positive_decisions):02d}",
            "FAMILY_POSITIVE",
            variant_id,
            "SIGNAL",
            decision.reason,
        )

    f01 = by_id[EXPECTED_VARIANT_IDS[0]]
    no_sweep = evaluate_frozen_signal(
        f01,
        history=_flat_history(),
        current=SyntheticBar(99.8, 100.0, 99.2, 99.5),
        context=_closed_context(),
    )
    add("NEG-F01-HIGH-EQUALITY", "FAMILY_NEGATIVE_BOUNDARY", f01.variant_id,
        "UPSIDE_SWEEP_RULE_BLOCKED", no_sweep.reason)

    wick_boundary = evaluate_frozen_signal(
        f01,
        history=_flat_history(),
        current=_f01_current(),
        context=_closed_context(),
    )
    add("BND-F01-WICK-EQUALITY", "FAMILY_NEGATIVE_BOUNDARY", f01.variant_id,
        "SIGNAL", wick_boundary.reason)

    zero_body = evaluate_frozen_signal(
        f01,
        history=_flat_history(),
        current=SyntheticBar(100.0, 101.0, 99.5, 100.0),
        context=_closed_context(),
    )
    add("NEG-F01-ZERO-BODY", "FAMILY_NEGATIVE_BOUNDARY", f01.variant_id,
        "UPSIDE_SWEEP_RULE_BLOCKED", zero_body.reason)

    late_mtf = evaluate_frozen_signal(
        f01,
        history=_flat_history(),
        current=_f01_current(),
        context=_closed_context(available_4h=101),
    )
    add("MTF-LATE-4H", "MTF_CLOSED_CANDLE", f01.variant_id,
        "MTF_CONTEXT_BLOCKED", late_mtf.reason)

    exact_mtf = evaluate_frozen_signal(
        f01,
        history=_flat_history(),
        current=_f01_current(),
        context=_closed_context(available_1h=100, available_4h=100),
    )
    add("MTF-EXACT-CLOSE", "MTF_CLOSED_CANDLE", f01.variant_id,
        "SIGNAL", exact_mtf.reason)

    unknown_mtf = evaluate_frozen_signal(
        f01,
        history=_flat_history(),
        current=_f01_current(),
        context=_closed_context(regime_1h="UNKNOWN"),
    )
    add("MTF-UNKNOWN", "MTF_CLOSED_CANDLE", f01.variant_id,
        "MTF_CONTEXT_BLOCKED", unknown_mtf.reason)

    non_synthetic = evaluate_frozen_signal(
        f01,
        history=_flat_history(),
        current=SyntheticBar(100.5, 101.0, 99.5, 100.0, source="FORBIDDEN_REAL_SOURCE"),
        context=_closed_context(),
    )
    add("SOURCE-NON-SYNTHETIC", "INPUT_BOUNDARY", f01.variant_id,
        "NON_SYNTHETIC_OR_INVALID_BAR", non_synthetic.reason)

    open_bar = evaluate_frozen_signal(
        f01,
        history=_flat_history(),
        current=SyntheticBar(100.5, 101.0, 99.5, 100.0, closed=False),
        context=_closed_context(),
    )
    add("SOURCE-OPEN-BAR", "INPUT_BOUNDARY", f01.variant_id,
        "NON_SYNTHETIC_OR_INVALID_BAR", open_bar.reason)

    add(
        "BND-F02-BREAK-EQUALITY",
        "FAMILY_NEGATIVE_BOUNDARY",
        EXPECTED_VARIANT_IDS[2],
        "FALSE",
        str(breakdown_condition(close=99.75, support=100.0, atr14=1.0, break_atr=0.25)).upper(),
    )
    add(
        "BND-F02-RETEST-HIGH-EQUALITY",
        "FAMILY_NEGATIVE_BOUNDARY",
        EXPECTED_VARIANT_IDS[2],
        "TRUE",
        str(retest_condition(
            current=SyntheticBar(99.7, 99.75, 99.4, 99.5),
            support=100.0,
            atr14=1.0,
            tolerance_atr=0.25,
        )).upper(),
    )
    add(
        "BND-F02-CLOSE-SUPPORT-EQUALITY",
        "FAMILY_NEGATIVE_BOUNDARY",
        EXPECTED_VARIANT_IDS[2],
        "FALSE",
        str(retest_condition(
            current=SyntheticBar(100.2, 100.3, 99.8, 100.0),
            support=100.0,
            atr14=1.0,
            tolerance_atr=0.25,
        )).upper(),
    )
    add(
        "BND-F03-SEPARATION-EQUALITY",
        "FAMILY_NEGATIVE_BOUNDARY",
        EXPECTED_VARIANT_IDS[5],
        "TRUE",
        str(ema_pullback_condition(
            current=SyntheticBar(99.0, 100.0, 98.0, 98.5),
            prior_close=99.0,
            ema20_t=99.5,
            ema50_t=99.75,
            ema200_t=101.0,
            ema20_previous=100.0,
            atr14_t=1.0,
            minimum_separation_atr=0.25,
        )).upper(),
    )
    add(
        "BND-F03-EMA-STACK-EQUALITY",
        "FAMILY_NEGATIVE_BOUNDARY",
        EXPECTED_VARIANT_IDS[5],
        "FALSE",
        str(ema_pullback_condition(
            current=SyntheticBar(99.0, 100.0, 98.0, 98.5),
            prior_close=99.0,
            ema20_t=99.5,
            ema50_t=99.5,
            ema200_t=101.0,
            ema20_previous=100.0,
            atr14_t=1.0,
            minimum_separation_atr=0.0,
        )).upper(),
    )

    signal = positive_decisions[f01.variant_id]
    accepted_order = construct_next_open_short_order(
        f01,
        signal,
        signal_bar_index=10,
        fill_bar_index=11,
        next_open=100.0,
        position_already_open=False,
    )
    add("EXEC-NEXT-OPEN", "NEXT_OPEN_GAP_OVERLAP", f01.variant_id,
        "ORDER_ACCEPTED", accepted_order.reason)

    wrong_fill = construct_next_open_short_order(
        f01, signal, signal_bar_index=10, fill_bar_index=10,
        next_open=100.0, position_already_open=False,
    )
    add("EXEC-WRONG-FILL", "NEXT_OPEN_GAP_OVERLAP", f01.variant_id,
        "FILL_NOT_NEXT_BAR_OPEN", wrong_fill.reason)

    overlap = construct_next_open_short_order(
        f01, signal, signal_bar_index=10, fill_bar_index=11,
        next_open=100.0, position_already_open=True,
    )
    add("EXEC-OVERLAP", "NEXT_OPEN_GAP_OVERLAP", f01.variant_id,
        "OVERLAPPING_POSITION_BLOCKED", overlap.reason)

    equal_gap = construct_next_open_short_order(
        f01, signal, signal_bar_index=10, fill_bar_index=11,
        next_open=float(signal.stop_price), position_already_open=False,
    )
    add("EXEC-GAP-EQUALITY", "NEXT_OPEN_GAP_OVERLAP", f01.variant_id,
        "INVALID_GAP_STOP_NOT_ABOVE_ENTRY", equal_gap.reason)

    if not accepted_order.accepted:
        raise FrozenSpecificationError("Positive order fixture was not accepted.")
    neutral = SyntheticBar(100.0, 100.5, 99.5, 100.0)
    stop_bar = SyntheticBar(100.0, float(accepted_order.stop_price) + 0.1, 99.5, 100.0)
    target_bar = SyntheticBar(100.0, 100.5, float(accepted_order.target_price) - 0.1, 99.0)
    simultaneous_bar = SyntheticBar(
        100.0,
        float(accepted_order.stop_price) + 0.1,
        float(accepted_order.target_price) - 0.1,
        100.0,
    )
    stop_exit = resolve_short_exit(accepted_order, (stop_bar,))
    target_exit = resolve_short_exit(accepted_order, (target_bar,))
    simultaneous_exit = resolve_short_exit(accepted_order, (simultaneous_bar,))
    time_exit = resolve_short_exit(accepted_order, tuple(neutral for _ in range(240)))
    still_open = resolve_short_exit(accepted_order, tuple(neutral for _ in range(239)))
    add("EXIT-STOP", "EXIT_RESOLUTION", f01.variant_id, "STOP", stop_exit.reason)
    add("EXIT-TARGET-ENTRY-BAR", "EXIT_RESOLUTION", f01.variant_id, "TARGET", target_exit.reason)
    add("EXIT-SIMULTANEOUS", "EXIT_RESOLUTION", f01.variant_id,
        "STOP_FIRST_SIMULTANEOUS", simultaneous_exit.reason)
    add("EXIT-TIME-240", "TIME_EXIT", f01.variant_id, "TIME_EXIT", time_exit.reason)
    add("EXIT-OPEN-239", "TIME_EXIT", f01.variant_id, "OPEN_NO_EXIT", still_open.reason)

    atr13 = wilder_atr14(_flat_history(13))
    atr14 = wilder_atr14(_flat_history(14))
    ema199 = ema_close_span(_ema_trend_history(199), 200)
    ema200 = ema_close_span(_ema_trend_history(200), 200)
    add("IND-ATR13-MISSING", "INDICATOR_METHOD", "ALL", "TRUE", str(atr13 is None).upper())
    add("IND-ATR14-AVAILABLE", "INDICATOR_METHOD", "ALL", "TRUE", str(atr14 is not None).upper())
    add("IND-EMA199-MISSING", "INDICATOR_METHOD", "ALL", "TRUE", str(ema199 is None).upper())
    add("IND-EMA200-AVAILABLE", "INDICATOR_METHOD", "ALL", "TRUE", str(ema200 is not None).upper())
    return pd.DataFrame(rows)


def build_implementation_catalog(
    implementations: tuple[FrozenVariantImplementation, ...],
) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "implementation_order": item.evaluation_order,
                "family_id": item.family_id,
                "variant_id": item.variant_id,
                "parameter_json": item.parameter_json,
                "handler_version": item.handler_version,
                "family_specification_sha256": item.family_specification_sha256,
                "variant_specification_sha256": item.variant_specification_sha256,
                "specification_root_sha256": item.specification_root_sha256,
                "implementation_sha256": item.implementation_sha256,
                "synthetic_fixture_only": True,
                "evaluated": False,
                "candidate_result_rows": 0,
                "ranking_allowed": False,
                "selection_allowed": False,
                "mutable_after_build": False,
            }
            for item in implementations
        ]
    )


def implementation_registry_equivalent(catalog: pd.DataFrame) -> tuple[bool, str]:
    artifacts = build_specification_artifacts()
    variants = artifacts["candidate_variant_registry"].sort_values("evaluation_order")
    passed = bool(
        len(catalog) == len(variants) == 6
        and catalog["variant_id"].tolist() == variants["variant_id"].tolist()
        and catalog["family_id"].tolist() == variants["family_id"].tolist()
        and catalog["parameter_json"].tolist() == variants["parameter_json"].tolist()
        and catalog["family_specification_sha256"].tolist()
        == variants["family_specification_sha256"].tolist()
        and catalog["variant_specification_sha256"].tolist()
        == variants["variant_specification_sha256"].tolist()
    )
    return passed, f"catalog={len(catalog)}, registry={len(variants)}"


def build_contract_snapshot() -> pd.DataFrame:
    rows = [
        ("phase_2d_root_sha256", EXPECTED_SPECIFICATION_ROOT_SHA256),
        ("source_phase_2d_commit", SOURCE_PHASE_2D_COMMIT),
        ("source_phase_2d_specification_module_sha256", SOURCE_PHASE_2D_SPECIFICATION_MODULE_SHA256),
        ("fixture_source", SYNTHETIC_FIXTURE_SOURCE),
        ("family_count", 3),
        ("variant_count", 6),
        ("real_ohlcv_rows", 0),
        ("phase_result_report_rows_read", 0),
        ("holdout_rows_read", 0),
        ("candidate_performance_rows", 0),
        ("comparison_rows", 0),
        ("ranking_rows", 0),
        ("winner_rows", 0),
        ("short_status", SHORT_STATUS),
        ("long_status", LONG_STATUS),
    ]
    return pd.DataFrame(
        [
            {
                "contract_order": index,
                "contract_key": key,
                "locked_value_json": json.dumps(value, separators=(",", ":")),
                "mutable_in_phase_2e": False,
            }
            for index, (key, value) in enumerate(rows, start=1)
        ]
    )


def build_permissions_snapshot() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {"permission": key, "allowed": value}
            for key, value in SAFETY_FLAGS.items()
        ]
    )


def build_acceptance_criteria() -> pd.DataFrame:
    criteria = [
        ("AC-001", "Phase 2D source module and golden root reproduce before implementation construction."),
        ("AC-002", "Exactly three frozen handlers and six registry-bound implementations are built."),
        ("AC-003", "Variant IDs, order, parameters and family/variant hashes equal Phase 2D exactly."),
        ("AC-004", "All fixtures are deterministic and explicitly synthetic."),
        ("AC-005", "Every frozen variant passes a positive synthetic signal fixture."),
        ("AC-006", "Negative and equality-boundary fixtures reproduce strict and inclusive operators."),
        ("AC-007", "Closed MTF availability blocks late or unknown context."),
        ("AC-008", "Next-open, invalid-gap and overlapping-position contracts conform."),
        ("AC-009", "Stop, target, simultaneous stop-first and 240-bar time exit conform."),
        ("AC-010", "No real OHLCV, phase result report or holdout is read."),
        ("AC-011", "No performance metric, comparison, ranking, winner or candidate result is emitted."),
        ("AC-012", "SHORT/LONG remain unchanged and every operational permission is false."),
    ]
    return pd.DataFrame(criteria, columns=["criterion_id", "acceptance_criterion"])


def _empty_schemas() -> dict[str, pd.DataFrame]:
    implementation_catalog = build_implementation_catalog(tuple())
    conformance = pd.DataFrame(
        columns=[
            "case_order", "case_id", "category", "variant_id",
            "fixture_source", "expected_outcome", "observed_outcome", "passed",
            "real_data_rows", "candidate_performance_rows", "comparison_rows",
            "ranking_rows", "winner_rows",
        ]
    )
    return {
        "implementation_catalog": implementation_catalog,
        "synthetic_conformance": conformance,
        "contract_snapshot": build_contract_snapshot().iloc[0:0].copy(),
        "implementation_manifest": pd.DataFrame(
            columns=["artifact_order", "artifact_name", "row_count", "canonical_sha256"]
        ),
        "implementation_root": pd.DataFrame(
            columns=[
                "schema_version", "phase_2d_root_sha256", "artifact_count",
                "implementation_root_sha256", "synthetic_fixture_only",
                "candidate_evaluation_allowed", "holdout_access_allowed",
            ]
        ),
    }


def build_implementation_manifest_and_root(
    catalog: pd.DataFrame,
    conformance: pd.DataFrame,
    contract: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    artifacts = (
        ("implementation_catalog", catalog),
        ("synthetic_conformance", conformance),
        ("contract_snapshot", contract),
    )
    manifest = pd.DataFrame(
        [
            {
                "artifact_order": order,
                "artifact_name": name,
                "row_count": len(frame),
                "canonical_sha256": canonical_frame_sha256(frame),
            }
            for order, (name, frame) in enumerate(artifacts, start=1)
        ]
    )
    root_payload = {
        "schema_version": IMPLEMENTATION_SCHEMA_VERSION,
        "phase_2d_root_sha256": EXPECTED_SPECIFICATION_ROOT_SHA256,
        "source_phase_2d_commit": SOURCE_PHASE_2D_COMMIT,
        "artifacts": manifest.to_dict(orient="records"),
    }
    root_sha = canonical_sha256(root_payload)
    if root_sha != EXPECTED_IMPLEMENTATION_ROOT_SHA256:
        raise FrozenSpecificationError(
            "Phase 2E implementation root drifted from its golden SHA-256."
        )
    root = pd.DataFrame(
        [
            {
                "schema_version": IMPLEMENTATION_SCHEMA_VERSION,
                "phase_2d_root_sha256": EXPECTED_SPECIFICATION_ROOT_SHA256,
                "artifact_count": len(manifest),
                "implementation_root_sha256": root_sha,
                "synthetic_fixture_only": True,
                "candidate_evaluation_allowed": False,
                "holdout_access_allowed": False,
            }
        ]
    )
    return manifest, root


def write_outputs(outputs: dict[str, pd.DataFrame]) -> None:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    for name, frame in outputs.items():
        frame.to_csv(REPORTS_DIR / f"{name}_v1.csv", index=False)


def validate_phase_10_42r_2e(
    *,
    preflight_only: bool = False,
) -> dict[str, pd.DataFrame]:
    errors: list[dict[str, str]] = []
    source_module_hash = normalized_source_sha256(
        PHASE_2D_SPECIFICATION_MODULE_PATH
    )
    source_module_exact = (
        source_module_hash == SOURCE_PHASE_2D_SPECIFICATION_MODULE_SHA256
    )
    root_sha = ""
    root_verified = False
    root_details = ""
    try:
        root_sha = verify_phase_2d_specification_root()
        root_verified = root_sha == EXPECTED_SPECIFICATION_ROOT_SHA256
        root_details = root_sha
    except Exception as exc:
        root_details = f"{type(exc).__name__}: {exc}"
    source_safe, source_safe_details = implementation_source_is_static_and_safe()
    output_names = {
        "implementation_catalog",
        "synthetic_conformance",
        "contract_snapshot",
        "implementation_manifest",
        "implementation_root",
        "permissions_snapshot",
        "acceptance_criteria",
        "summary",
        "checks",
        "errors",
    }
    forbidden_output_names = sorted(
        name
        for name in output_names
        if any(token in name for token in FORBIDDEN_OUTPUT_NAME_TOKENS)
    )
    preflight_checks = [
        build_check("phase_2d_source_commit_frozen", SOURCE_PHASE_2D_COMMIT == "a9ec58c493a46c9835b2ddb19c301f2957dadaca", SOURCE_PHASE_2D_COMMIT),
        build_check("phase_2d_specification_module_hash_exact", source_module_exact, f"actual={source_module_hash}"),
        build_check("phase_2d_golden_root_verified_before_build", root_verified, root_details),
        build_check("implementation_source_static_import_boundary", source_safe, source_safe_details),
        build_check("implementation_has_no_real_data_or_report_io", source_safe, source_safe_details),
        build_check("holdouts_and_official_artifacts_absent", sealed_inputs_absent(), "Metadata check only; no sealed file is opened."),
        build_check("real_ohlcv_access_prohibited", SAFETY_FLAGS["real_ohlcv_access_allowed"] is False, "No real-data loader exists in Phase 2E."),
        build_check("phase_result_report_reads_prohibited", SAFETY_FLAGS["phase_result_report_read_allowed"] is False, "Phase 2E reconstructs Phase 2D in memory."),
        build_check("all_operational_permissions_false", all_permissions_false(), str(SAFETY_FLAGS)),
        build_check("candidate_statuses_immutable", SHORT_STATUS == "RETIRED_REVALIDATED_REJECTED_UNCHANGED" and LONG_STATUS == "RESEARCH_ONLY_NOT_APPROVED_UNCHANGED", f"SHORT={SHORT_STATUS}; LONG={LONG_STATUS}"),
        build_check("output_contract_has_no_performance_artifact", not forbidden_output_names, f"forbidden={forbidden_output_names}"),
        build_check("synthetic_fixture_identity_frozen", SYNTHETIC_FIXTURE_SOURCE == "SYNTHETIC_DETERMINISTIC_PHASE_10_42R_2E_V1", SYNTHETIC_FIXTURE_SOURCE),
    ]
    preflight_passed = not any(row["blocker"] for row in preflight_checks)
    schemas = _empty_schemas()
    catalog = schemas["implementation_catalog"]
    conformance = schemas["synthetic_conformance"]
    contract = schemas["contract_snapshot"]
    manifest = schemas["implementation_manifest"]
    implementation_root = schemas["implementation_root"]

    if preflight_only:
        checks = pd.DataFrame(preflight_checks)
        validation_passed = preflight_passed
        implementation_completed = False
        decision = (
            "PHASE_10_42R_2E_PREFLIGHT_PASSED_READY_FOR_SYNTHETIC_CONFORMANCE"
            if validation_passed
            else "PHASE_10_42R_2E_PREFLIGHT_FAILED"
        )
        recommended_next = (
            "RUN_PHASE_10_42R_2E_FULL_STATIC_SYNTHETIC_CONFORMANCE"
            if validation_passed
            else "REMEDIATE_PHASE_10_42R_2E_PREFLIGHT_BLOCKERS"
        )
    else:
        implementations: tuple[FrozenVariantImplementation, ...] = tuple()
        if preflight_passed:
            try:
                implementations = build_verified_implementations()
                catalog = build_implementation_catalog(implementations)
                conformance = run_synthetic_conformance_cases(implementations)
                contract = build_contract_snapshot()
                manifest, implementation_root = build_implementation_manifest_and_root(
                    catalog, conformance, contract
                )
            except Exception as exc:
                errors.append(
                    {
                        "scope": "FROZEN_IMPLEMENTATION_STATIC_CONFORMANCE",
                        "error": f"{type(exc).__name__}: {exc}",
                    }
                )
        registry_equal, registry_details = (
            implementation_registry_equivalent(catalog)
            if not catalog.empty
            else (False, "empty implementation catalog")
        )
        cases_pass = bool(
            not conformance.empty
            and conformance["passed"].astype(bool).all()
            and conformance["fixture_source"].eq(SYNTHETIC_FIXTURE_SOURCE).all()
            and conformance[
                [
                    "real_data_rows", "candidate_performance_rows",
                    "comparison_rows", "ranking_rows", "winner_rows",
                ]
            ].apply(pd.to_numeric, errors="coerce").eq(0).all(axis=None)
        )
        categories = set(conformance.get("category", pd.Series(dtype=str)))
        family_positive = conformance[
            conformance.get("category", pd.Series(dtype=str)).eq("FAMILY_POSITIVE")
        ]
        family_boundary = conformance[
            conformance.get("category", pd.Series(dtype=str)).eq("FAMILY_NEGATIVE_BOUNDARY")
        ]
        mtf_cases = conformance[
            conformance.get("category", pd.Series(dtype=str)).eq("MTF_CLOSED_CANDLE")
        ]
        execution_cases = conformance[
            conformance.get("category", pd.Series(dtype=str)).eq("NEXT_OPEN_GAP_OVERLAP")
        ]
        exit_cases = conformance[
            conformance.get("category", pd.Series(dtype=str)).eq("EXIT_RESOLUTION")
        ]
        time_cases = conformance[
            conformance.get("category", pd.Series(dtype=str)).eq("TIME_EXIT")
        ]
        indicator_cases = conformance[
            conformance.get("category", pd.Series(dtype=str)).eq("INDICATOR_METHOD")
        ]
        deterministic_catalog = False
        deterministic_cases = False
        if implementations:
            catalog_b = build_implementation_catalog(build_verified_implementations())
            cases_b = run_synthetic_conformance_cases(implementations)
            deterministic_catalog = canonical_frame_sha256(catalog) == canonical_frame_sha256(catalog_b)
            deterministic_cases = canonical_frame_sha256(conformance) == canonical_frame_sha256(cases_b)
        full_checks = [
            build_check("root_bound_before_every_implementation_build", bool(implementations) and root_verified, root_sha),
            build_check("exact_three_handlers_six_implementations", len(FAMILY_HANDLER_VERSIONS) == 3 and len(catalog) == 6, f"handlers={len(FAMILY_HANDLER_VERSIONS)}, implementations={len(catalog)}"),
            build_check("registry_parameters_and_hashes_equivalent", registry_equal, registry_details),
            build_check("implementation_order_exact", tuple(catalog.get("variant_id", pd.Series(dtype=str))) == EXPECTED_VARIANT_IDS, str(catalog.get("variant_id", pd.Series(dtype=str)).tolist())),
            build_check("every_implementation_bound_to_golden_root", not catalog.empty and catalog["specification_root_sha256"].eq(EXPECTED_SPECIFICATION_ROOT_SHA256).all(), EXPECTED_SPECIFICATION_ROOT_SHA256),
            build_check("all_synthetic_conformance_cases_pass", cases_pass, f"passed={int(conformance.get('passed', pd.Series(dtype=bool)).sum())}/{len(conformance)}"),
            build_check("all_six_variants_have_positive_fixture", len(family_positive) == 6 and family_positive["passed"].astype(bool).all(), f"cases={len(family_positive)}"),
            build_check("negative_and_boundary_operators_conform", len(family_boundary) >= 7 and family_boundary["passed"].astype(bool).all(), f"cases={len(family_boundary)}"),
            build_check("closed_mtf_availability_conforms", len(mtf_cases) == 3 and mtf_cases["passed"].astype(bool).all(), f"cases={len(mtf_cases)}"),
            build_check("next_open_gap_overlap_conform", len(execution_cases) == 4 and execution_cases["passed"].astype(bool).all(), f"cases={len(execution_cases)}"),
            build_check("stop_target_simultaneous_resolution_conforms", len(exit_cases) == 3 and exit_cases["passed"].astype(bool).all(), f"cases={len(exit_cases)}"),
            build_check("time_exit_240_and_open_239_conform", len(time_cases) == 2 and time_cases["passed"].astype(bool).all(), f"cases={len(time_cases)}"),
            build_check("atr_ema_minimum_periods_conform", len(indicator_cases) == 4 and indicator_cases["passed"].astype(bool).all(), f"cases={len(indicator_cases)}"),
            build_check("implementation_and_fixtures_deterministic", deterministic_catalog and deterministic_cases, f"catalog={deterministic_catalog}, fixtures={deterministic_cases}, categories={sorted(categories)}"),
            build_check("implementation_golden_root_exact", not implementation_root.empty and implementation_root.iloc[0]["implementation_root_sha256"] == EXPECTED_IMPLEMENTATION_ROOT_SHA256, EXPECTED_IMPLEMENTATION_ROOT_SHA256),
        ]
        checks = pd.DataFrame([*preflight_checks, *full_checks])
        validation_passed = bool(
            not checks["blocker"].astype(bool).any() and not errors
        )
        implementation_completed = validation_passed
        decision = (
            "PHASE_10_42R_2E_FROZEN_IMPLEMENTATION_STATIC_CONFORMANCE_COMPLETED"
            if validation_passed
            else "PHASE_10_42R_2E_FROZEN_IMPLEMENTATION_STATIC_CONFORMANCE_FAILED"
        )
        recommended_next = (
            NEXT_PHASE if validation_passed else "REMEDIATE_PHASE_10_42R_2E_BLOCKERS"
        )

    root_value = (
        str(implementation_root.iloc[0]["implementation_root_sha256"])
        if not implementation_root.empty
        else ""
    )
    summary = pd.DataFrame(
        [
            {
                "phase": PHASE,
                "run_mode": "PREFLIGHT_ONLY" if preflight_only else "STATIC_SYNTHETIC_CONFORMANCE_ONLY",
                "validation_passed": validation_passed,
                "implementation_completed": implementation_completed,
                "phase_2d_root_sha256": root_sha,
                "implementation_root_sha256": root_value,
                "family_handler_count": 0 if preflight_only else len(FAMILY_HANDLER_VERSIONS),
                "variant_implementation_count": len(catalog),
                "synthetic_fixture_rows": len(conformance),
                "real_ohlcv_rows_read": 0,
                "phase_result_report_rows_read": 0,
                "holdout_rows_read": 0,
                "candidate_backtest_rows": 0,
                "candidate_performance_metric_rows": 0,
                "candidate_comparison_rows": 0,
                "candidate_ranking_rows": 0,
                "candidate_result_rows": 0,
                "winner_selected": False,
                "short_candidate_status": SHORT_STATUS,
                "long_candidate_status": LONG_STATUS,
                "official_dataset_exists": any(path.exists() for path in OFFICIAL_FORWARD_PATHS),
                "official_evidence_rows_written": 0,
                "total_checks": len(checks),
                "blocker_count": int(checks["blocker"].astype(bool).sum()),
                "error_rows": len(errors),
                "validation_decision": decision,
                "recommended_next_phase": recommended_next,
                "synthetic_fixture_only": True,
                **SAFETY_FLAGS,
                "total_project_completed": False,
            }
        ]
    )
    outputs = {
        "summary": summary,
        "checks": checks,
        "implementation_catalog": catalog,
        "synthetic_conformance": conformance,
        "contract_snapshot": contract,
        "implementation_manifest": manifest,
        "implementation_root": implementation_root,
        "permissions_snapshot": build_permissions_snapshot(),
        "acceptance_criteria": build_acceptance_criteria(),
        "errors": pd.DataFrame(errors, columns=["scope", "error"]),
    }
    write_outputs(outputs)
    return outputs
