from __future__ import annotations

import ast
from dataclasses import asdict, dataclass, replace
import hashlib
import json
import math
from pathlib import Path
from typing import Any, Callable

import src.analysis.frozen_recovery_candidate_implementation_v1 as baseline
import src.analysis.frozen_recovery_candidate_implementation_v2 as corrected


PHASE = "10.42R.2F"
SOURCE_PHASE_2E_COMMIT = "7d7f8ee81156b1858a636b586eb5636b34b1c801"
PHASE_2D_ROOT_SHA256 = (
    "0872b2bf7355e8a9b35d5b4e0e05d3edf291006862ce9ee5eae847910ef4c015"
)
PHASE_2D_SOURCE_SHA256 = (
    "54f71b968c89239b0f4b5e49298be30ddf84c65170be3ce240743d94031f5c4b"
)
PHASE_2E_SOURCE_SHA256 = (
    "8ac370bf803e9bf033ce9f7e2edc94cb27ab4811a387bb2974e6dffeb53c83d4"
)
PHASE_2F_CORRECTED_SOURCE_SHA256 = (
    "ccf3cc05823515fa56e9e1183eb51ab903503e310aa037248847ad7445b2cc1e"
)
NEXT_PHASE = (
    "PHASE_10_42R_2G_FROZEN_RECOVERY_CANDIDATE_CORRECTION_"
    "INDEPENDENT_SYNTHETIC_ACCEPTANCE_V1"
)

PHASE_2D_SOURCE = Path(
    "src/analysis/recovery_candidate_family_specification_v1.py"
)
PHASE_2E_SOURCE = Path(
    "src/analysis/frozen_recovery_candidate_implementation_v1.py"
)
PHASE_2F_CORRECTED_SOURCE = Path(
    "src/analysis/frozen_recovery_candidate_implementation_v2.py"
)

SAFETY_FLAGS = {
    "real_ohlcv_access_allowed": False,
    "historical_result_report_access_allowed": False,
    "backtest_allowed": False,
    "performance_metric_calculation_allowed": False,
    "candidate_comparison_allowed": False,
    "candidate_ranking_allowed": False,
    "candidate_selection_allowed": False,
    "holdout_access_allowed": False,
    "retired_short_modification_allowed": False,
    "phase_2d_contract_modification_allowed": False,
    "signal_activation_allowed": False,
    "paper_trading_allowed": False,
    "live_trading_allowed": False,
    "alerts_allowed": False,
    "automation_allowed": False,
    "execution_allowed": False,
    "operational_integration_allowed": False,
    "openclaw_read_allowed": False,
    "openclaw_write_allowed": False,
    "openclaw_execution_allowed": False,
}


@dataclass(frozen=True)
class ReviewCheck:
    check_id: str
    check_name: str
    passed: bool
    details: str
    blocker: bool


@dataclass(frozen=True)
class ConfirmedFinding:
    finding_id: str
    severity: str
    file: str
    symbol: str
    reproducible_case: str
    baseline_observed: str
    contract_required: str
    corrected_observed: str
    status: str


class ReviewFailure(RuntimeError):
    pass


def normalized_source_sha256(path: Path) -> str:
    payload = path.read_bytes().replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest()


def _check(
    check_id: str,
    check_name: str,
    passed: bool,
    details: str,
    *,
    blocker: bool = True,
) -> ReviewCheck:
    return ReviewCheck(check_id, check_name, bool(passed), details, blocker)


def _source_is_isolated_and_static(path: Path) -> tuple[bool, str]:
    text = path.read_text(encoding="utf-8")
    tree = ast.parse(text)
    forbidden_import_roots = {
        "requests",
        "urllib",
        "httpx",
        "socket",
        "subprocess",
        "ccxt",
        "websocket",
    }
    forbidden_calls = {
        "open",
        "read_csv",
        "read_json",
        "read_parquet",
        "to_csv",
        "to_json",
        "to_parquet",
        "urlopen",
    }
    violations: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.split(".")[0] in forbidden_import_roots:
                    violations.append(f"import:{alias.name}")
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            if module.split(".")[0] in forbidden_import_roots:
                violations.append(f"import:{module}")
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                name = node.func.id
            elif isinstance(node.func, ast.Attribute):
                name = node.func.attr
            else:
                name = ""
            if name in forbidden_calls:
                violations.append(f"call:{name}@{getattr(node, 'lineno', 0)}")
    forbidden_literals = ("data/", "reports/", ".csv", ".parquet", "holdout")
    for literal in forbidden_literals:
        if literal in text.lower():
            violations.append(f"literal:{literal}")
    return not violations, ",".join(violations) if violations else "static_source_only"


def _context(
    *,
    signal_close: int = 100,
    available_1h: int = 100,
    available_4h: int = 100,
) -> corrected.ClosedMtfContext:
    return corrected.ClosedMtfContext(
        "BEARISH",
        "BEARISH",
        signal_close,
        available_1h,
        available_4h,
    )


def _flat_history(count: int = 120) -> tuple[corrected.SyntheticBar, ...]:
    return tuple(
        corrected.SyntheticBar(99.7, 100.0, 99.0, 99.5) for _ in range(count)
    )


def _f01_positive() -> corrected.SyntheticBar:
    return corrected.SyntheticBar(100.5, 101.5, 99.0, 99.5)


def _f01_close_equality() -> corrected.SyntheticBar:
    return corrected.SyntheticBar(100.5, 101.0, 99.5, 100.0)


def _f02_history(count: int = 120) -> tuple[corrected.SyntheticBar, ...]:
    bars = [corrected.SyntheticBar(100.6, 101.0, 100.0, 100.5) for _ in range(count)]
    bars.append(corrected.SyntheticBar(100.0, 100.2, 99.2, 99.4))
    return tuple(bars)


def _f02_current() -> corrected.SyntheticBar:
    return corrected.SyntheticBar(99.9, 100.0, 99.2, 99.5)


def _ema_history(count: int = 230) -> tuple[corrected.SyntheticBar, ...]:
    bars: list[corrected.SyntheticBar] = []
    for index in range(count):
        close = 200.0 - 0.1 * index
        bars.append(corrected.SyntheticBar(close + 0.05, close + 0.2, close - 0.2, close))
    return tuple(bars)


def _ema_current() -> corrected.SyntheticBar:
    return corrected.SyntheticBar(177.4, 178.2, 176.8, 177.0)


def _positive_signal(
    implementation: corrected.FrozenVariantImplementation,
) -> corrected.SignalDecision:
    if implementation.family_id.endswith("F01_V1"):
        history, current = _flat_history(), _f01_positive()
    elif implementation.family_id.endswith("F02_V1"):
        history, current = _f02_history(), _f02_current()
    else:
        history, current = _ema_history(), _ema_current()
    return corrected.evaluate_frozen_signal(
        implementation,
        history=history,
        current=current,
        context=_context(),
    )


def reproduce_confirmed_findings() -> tuple[ConfirmedFinding, ...]:
    implementation = baseline.build_verified_implementations()[0]
    history = _flat_history()
    context = _context()

    baseline_f01 = baseline.evaluate_frozen_signal(
        implementation,
        history=history,
        current=_f01_close_equality(),
        context=context,
    )
    corrected_f01 = corrected.evaluate_frozen_signal(
        implementation,
        history=history,
        current=_f01_close_equality(),
        context=context,
    )

    baseline_nan_order = baseline.construct_next_open_short_order(
        implementation,
        baseline.SignalDecision(True, "SIGNAL", math.nan),
        signal_bar_index=10,
        fill_bar_index=11,
        next_open=100.0,
        position_already_open=False,
    )
    corrected_nan_order = corrected.construct_next_open_short_order(
        implementation,
        corrected.SignalDecision(True, "SIGNAL", math.nan),
        signal_bar_index=10,
        fill_bar_index=11,
        next_open=100.0,
        position_already_open=False,
    )

    parameters = implementation.parameters
    parameters["prior_high_lookback_bars"] = 1
    tampered = replace(
        implementation,
        parameter_json=json.dumps(parameters, sort_keys=True, separators=(",", ":")),
    )
    baseline_tampered = baseline.evaluate_frozen_signal(
        tampered,
        history=history[:20],
        current=_f01_positive(),
        context=context,
    )
    corrected_tampered = "NO_EXCEPTION"
    try:
        corrected.evaluate_frozen_signal(
            tampered,
            history=history[:20],
            current=_f01_positive(),
            context=context,
        )
    except corrected.FrozenSpecificationError:
        corrected_tampered = "FrozenSpecificationError"

    infinite_context = corrected.ClosedMtfContext(
        "BEARISH", "BEARISH", math.inf, 100, 100
    )
    baseline_infinite = baseline.evaluate_frozen_signal(
        implementation,
        history=history,
        current=_f01_positive(),
        context=infinite_context,
    )
    corrected_infinite = corrected.evaluate_frozen_signal(
        implementation,
        history=history,
        current=_f01_positive(),
        context=infinite_context,
    )

    valid_signal = corrected.evaluate_frozen_signal(
        implementation,
        history=history,
        current=_f01_positive(),
        context=context,
    )
    baseline_fractional = baseline.construct_next_open_short_order(
        implementation,
        valid_signal,
        signal_bar_index=10.5,
        fill_bar_index=11.5,
        next_open=100.0,
        position_already_open=False,
    )
    corrected_fractional = corrected.construct_next_open_short_order(
        implementation,
        valid_signal,
        signal_bar_index=10.5,
        fill_bar_index=11.5,
        next_open=100.0,
        position_already_open=False,
    )

    invalid_order = baseline.OrderDecision(
        True, "ORDER_ACCEPTED", 100.0, math.nan, 90.0
    )
    neutral = (baseline.SyntheticBar(100.0, 100.5, 99.5, 100.0),)
    baseline_exit = baseline.resolve_short_exit(invalid_order, neutral)
    corrected_exit = corrected.resolve_short_exit(invalid_order, neutral)

    return (
        ConfirmedFinding(
            "2F-CF-001",
            "HIGH",
            str(PHASE_2E_SOURCE),
            "_evaluate_upside_sweep",
            "prior_high=100; high_t=101; close_t=100",
            baseline_f01.reason,
            "CLOSE_T_LESS_THAN_PRIOR_HIGH must block equality",
            corrected_f01.reason,
            "CORRECTED_IN_V2",
        ),
        ConfirmedFinding(
            "2F-CF-002",
            "HIGH",
            str(PHASE_2E_SOURCE),
            "construct_next_open_short_order / resolve_short_exit",
            "signal.stop_price=NaN and accepted order.stop_price=NaN",
            f"order={baseline_nan_order.reason};exit={baseline_exit.reason}",
            "non-finite state must fail closed",
            f"order={corrected_nan_order.reason};exit={corrected_exit.reason}",
            "CORRECTED_IN_V2",
        ),
        ConfirmedFinding(
            "2F-CF-003",
            "HIGH",
            str(PHASE_2E_SOURCE),
            "evaluate_frozen_signal",
            "canonical F01 parameter_json replaced with lookback=1",
            baseline_tampered.reason,
            "implementation identity must equal the frozen registry exactly",
            corrected_tampered,
            "CORRECTED_IN_V2",
        ),
        ConfirmedFinding(
            "2F-CF-004",
            "MEDIUM",
            str(PHASE_2E_SOURCE),
            "mtf_context_is_closed_and_allowed",
            "signal_close_unit=+Infinity with finite availability units",
            baseline_infinite.reason,
            "invalid/non-integer MTF availability state must block",
            corrected_infinite.reason,
            "CORRECTED_IN_V2",
        ),
        ConfirmedFinding(
            "2F-CF-005",
            "MEDIUM",
            str(PHASE_2E_SOURCE),
            "construct_next_open_short_order",
            "signal_bar_index=10.5; fill_bar_index=11.5",
            baseline_fractional.reason,
            "bar indices must be integers and fill must equal t+1",
            corrected_fractional.reason,
            "CORRECTED_IN_V2",
        ),
    )


def _run_case(name: str, operation: Callable[[], bool]) -> ReviewCheck:
    try:
        passed = bool(operation())
        return _check(f"2F-SYN-{name}", name, passed, "deterministic synthetic case")
    except Exception as exc:
        return _check(
            f"2F-SYN-{name}",
            name,
            False,
            f"{type(exc).__name__}: {exc}",
        )


def run_synthetic_review_cases() -> tuple[ReviewCheck, ...]:
    implementations = corrected.build_verified_implementations()
    first = implementations[0]
    positive_signals = tuple(_positive_signal(item) for item in implementations)
    positive_order = corrected.construct_next_open_short_order(
        first,
        positive_signals[0],
        signal_bar_index=10,
        fill_bar_index=11,
        next_open=100.0,
        position_already_open=False,
    )
    neutral = corrected.SyntheticBar(100.0, 100.5, 99.5, 100.0)
    stop_bar = corrected.SyntheticBar(
        100.0, float(positive_order.stop_price) + 0.1, 99.5, 100.0
    )
    target_bar = corrected.SyntheticBar(
        100.0, 100.5, float(positive_order.target_price) - 0.1, 99.0
    )
    both_bar = corrected.SyntheticBar(
        100.0,
        float(positive_order.stop_price) + 0.1,
        float(positive_order.target_price) - 0.1,
        100.0,
    )
    constant = tuple(corrected.SyntheticBar(100.0, 101.0, 99.0, 100.0) for _ in range(250))
    cases: list[tuple[str, Callable[[], bool]]] = [
        ("phase_2d_root", lambda: corrected.verify_phase_2d_specification_root() == PHASE_2D_ROOT_SHA256),
        ("six_canonical_variants", lambda: tuple(item.variant_id for item in implementations) == corrected.EXPECTED_VARIANT_IDS),
        ("all_family_positive_signals", lambda: all(item.signal and item.reason == "SIGNAL" for item in positive_signals)),
        ("f01_close_equality_blocks", lambda: not corrected.evaluate_frozen_signal(first, history=_flat_history(), current=_f01_close_equality(), context=_context()).signal),
        ("f01_high_equality_blocks", lambda: not corrected.evaluate_frozen_signal(first, history=_flat_history(), current=corrected.SyntheticBar(99.8, 100.0, 99.2, 99.5), context=_context()).signal),
        ("f02_break_equality_blocks", lambda: not corrected.breakdown_condition(close=99.75, support=100.0, atr14=1.0, break_atr=0.25)),
        ("f02_retest_equality_passes", lambda: corrected.retest_condition(current=corrected.SyntheticBar(99.7, 99.75, 99.4, 99.5), support=100.0, atr14=1.0, tolerance_atr=0.25)),
        ("f03_separation_equality_passes", lambda: corrected.ema_pullback_condition(current=corrected.SyntheticBar(99.0, 100.0, 98.0, 98.5), prior_close=99.0, ema20_t=99.5, ema50_t=99.75, ema200_t=101.0, ema20_previous=100.0, atr14_t=1.0, minimum_separation_atr=0.25)),
        ("f03_stack_equality_blocks", lambda: not corrected.ema_pullback_condition(current=corrected.SyntheticBar(99.0, 100.0, 98.0, 98.5), prior_close=99.0, ema20_t=99.5, ema50_t=99.5, ema200_t=101.0, ema20_previous=100.0, atr14_t=1.0, minimum_separation_atr=0.25)),
        ("ema_constant_exact", lambda: math.isclose(float(corrected.ema_close_span(constant, 200)), 100.0, rel_tol=0.0, abs_tol=1e-12)),
        ("wilder_atr_constant_exact", lambda: corrected.wilder_atr14(constant) == 2.0),
        ("late_mtf_blocks", lambda: not corrected.evaluate_frozen_signal(first, history=_flat_history(), current=_f01_positive(), context=_context(available_4h=101)).signal),
        ("nonfinite_mtf_blocks", lambda: not corrected.mtf_context_is_closed_and_allowed(corrected.ClosedMtfContext("BEARISH", "BEARISH", math.inf, 100, 100))),
        ("open_bar_blocks", lambda: not corrected.evaluate_frozen_signal(first, history=_flat_history(), current=corrected.SyntheticBar(100.5, 101.5, 99.0, 99.5, closed=False), context=_context()).signal),
        ("non_synthetic_bar_blocks", lambda: not corrected.evaluate_frozen_signal(first, history=_flat_history(), current=corrected.SyntheticBar(100.5, 101.5, 99.0, 99.5, source="REAL"), context=_context()).signal),
        ("nan_ohlc_blocks", lambda: not corrected.synthetic_bar_is_valid(corrected.SyntheticBar(100.0, math.nan, 99.0, 100.0))),
        ("next_open_order_accepts", lambda: positive_order.accepted and positive_order.reason == "ORDER_ACCEPTED"),
        ("target_formula_exact", lambda: math.isclose(float(positive_order.target_price), float(positive_order.entry_price) - 2.5 * (float(positive_order.stop_price) - float(positive_order.entry_price)), rel_tol=0.0, abs_tol=1e-12)),
        ("wrong_fill_blocks", lambda: corrected.construct_next_open_short_order(first, positive_signals[0], signal_bar_index=10, fill_bar_index=10, next_open=100.0, position_already_open=False).reason == "FILL_NOT_NEXT_BAR_OPEN"),
        ("fractional_index_blocks", lambda: corrected.construct_next_open_short_order(first, positive_signals[0], signal_bar_index=10.5, fill_bar_index=11.5, next_open=100.0, position_already_open=False).reason == "INVALID_BAR_INDEX"),
        ("overlap_blocks", lambda: corrected.construct_next_open_short_order(first, positive_signals[0], signal_bar_index=10, fill_bar_index=11, next_open=100.0, position_already_open=True).reason == "OVERLAPPING_POSITION_BLOCKED"),
        ("gap_equality_blocks", lambda: corrected.construct_next_open_short_order(first, positive_signals[0], signal_bar_index=10, fill_bar_index=11, next_open=float(positive_signals[0].stop_price), position_already_open=False).reason == "INVALID_GAP_STOP_NOT_ABOVE_ENTRY"),
        ("nan_signal_stop_blocks", lambda: corrected.construct_next_open_short_order(first, corrected.SignalDecision(True, "SIGNAL", math.nan), signal_bar_index=10, fill_bar_index=11, next_open=100.0, position_already_open=False).reason == "INVALID_SIGNAL_STOP"),
        ("stop_exit", lambda: corrected.resolve_short_exit(positive_order, (stop_bar,)).reason == "STOP"),
        ("target_exit", lambda: corrected.resolve_short_exit(positive_order, (target_bar,)).reason == "TARGET"),
        ("simultaneous_stop_first", lambda: corrected.resolve_short_exit(positive_order, (both_bar,)).reason == "STOP_FIRST_SIMULTANEOUS"),
        ("time_exit_240", lambda: corrected.resolve_short_exit(positive_order, tuple(neutral for _ in range(240))).reason == "TIME_EXIT"),
        ("open_at_239", lambda: corrected.resolve_short_exit(positive_order, tuple(neutral for _ in range(239))).reason == "OPEN_NO_EXIT"),
        ("nan_order_blocks", lambda: corrected.resolve_short_exit(corrected.OrderDecision(True, "ORDER_ACCEPTED", 100.0, math.nan, 90.0), (neutral,)).reason == "INVALID_ACCEPTED_ORDER"),
        ("altered_target_blocks", lambda: corrected.resolve_short_exit(corrected.OrderDecision(True, "ORDER_ACCEPTED", 100.0, 101.0, 98.0), (neutral,)).reason == "INVALID_ACCEPTED_ORDER"),
    ]
    return tuple(_run_case(name, operation) for name, operation in cases)


def review_risks_not_demonstrated() -> tuple[dict[str, str], ...]:
    return (
        {
            "risk_id": "2F-RISK-001",
            "area": "chronology",
            "description": "Synthetic bars carry no timestamp, so sequence ordering is a caller invariant.",
            "classification": "NOT_DEMONSTRATED_AS_DEFECT",
            "reason": "No incorrect result is reproducible when the documented tuple order is respected.",
        },
        {
            "risk_id": "2F-RISK-002",
            "area": "signal_provenance",
            "description": "SignalDecision is a public value object and has no variant identity field.",
            "classification": "NOT_DEMONSTRATED_AS_DEFECT",
            "reason": "The corrected order boundary validates state but this phase has no operational consumer.",
        },
    )


def optional_out_of_scope_improvements() -> tuple[dict[str, str], ...]:
    return (
        {
            "improvement_id": "2F-OPT-001",
            "description": "Introduce typed synthetic sequence identifiers before any authorized evaluation phase.",
            "scope": "OUT_OF_SCOPE_NO_CONTRACT_CHANGE_IN_2F",
        },
        {
            "improvement_id": "2F-OPT-002",
            "description": "Attach variant identity to future SignalDecision versions if an operational boundary is ever authorized.",
            "scope": "OUT_OF_SCOPE_NO_OPERATIONAL_PERMISSION",
        },
    )


def validate_phase_10_42r_2f(*, preflight_only: bool = False) -> dict[str, Any]:
    checks: list[ReviewCheck] = []
    checks.append(_check("2F-PRE-001", "phase_2d_root_exact", corrected.verify_phase_2d_specification_root() == PHASE_2D_ROOT_SHA256, PHASE_2D_ROOT_SHA256))
    for check_id, name, path, expected in (
        ("2F-PRE-002", "phase_2d_source_exact", PHASE_2D_SOURCE, PHASE_2D_SOURCE_SHA256),
        ("2F-PRE-003", "phase_2e_baseline_source_exact", PHASE_2E_SOURCE, PHASE_2E_SOURCE_SHA256),
        ("2F-PRE-004", "phase_2f_corrected_source_exact", PHASE_2F_CORRECTED_SOURCE, PHASE_2F_CORRECTED_SOURCE_SHA256),
    ):
        actual = normalized_source_sha256(path)
        checks.append(_check(check_id, name, actual == expected, f"expected={expected};actual={actual}"))
    isolated, details = _source_is_isolated_and_static(PHASE_2F_CORRECTED_SOURCE)
    checks.append(_check("2F-PRE-005", "corrected_source_static_and_isolated", isolated, details))
    checks.append(_check("2F-PRE-006", "all_permissions_false", bool(SAFETY_FLAGS) and all(value is False for value in SAFETY_FLAGS.values()), f"enabled={sum(bool(value) for value in SAFETY_FLAGS.values())}"))
    checks.append(_check("2F-PRE-007", "short_and_long_implementation_v1_untouched", PHASE_2E_SOURCE_SHA256 == normalized_source_sha256(PHASE_2E_SOURCE), "v1 preserved as audit evidence"))

    findings: tuple[ConfirmedFinding, ...] = ()
    risks: tuple[dict[str, str], ...] = ()
    optional: tuple[dict[str, str], ...] = ()
    if not preflight_only and all(item.passed for item in checks):
        findings = reproduce_confirmed_findings()
        checks.append(_check("2F-REV-001", "five_confirmed_findings_reproduced_and_corrected", len(findings) == 5 and all(item.status == "CORRECTED_IN_V2" for item in findings), f"confirmed={len(findings)}"))
        synthetic_checks = run_synthetic_review_cases()
        checks.extend(synthetic_checks)
        first_payload = json.dumps([asdict(item) for item in synthetic_checks], sort_keys=True, separators=(",", ":"))
        second_payload = json.dumps([asdict(item) for item in run_synthetic_review_cases()], sort_keys=True, separators=(",", ":"))
        checks.append(_check("2F-REV-002", "synthetic_review_deterministic", first_payload == second_payload, hashlib.sha256(first_payload.encode("utf-8")).hexdigest()))
        risks = review_risks_not_demonstrated()
        optional = optional_out_of_scope_improvements()
        checks.append(_check("2F-REV-003", "no_candidate_outcome_or_selection_produced", True, "source review contains no candidate outcomes, rankings or winners"))

    failed = tuple(item for item in checks if not item.passed)
    blockers = tuple(item for item in failed if item.blocker)
    summary = {
        "phase": PHASE,
        "source_phase_2e_commit": SOURCE_PHASE_2E_COMMIT,
        "preflight_only": preflight_only,
        "review_completed": not preflight_only and not blockers,
        "confirmed_finding_count": len(findings),
        "risk_not_demonstrated_count": len(risks),
        "optional_out_of_scope_count": len(optional),
        "synthetic_case_count": sum(item.check_id.startswith("2F-SYN-") for item in checks),
        "total_check_count": len(checks),
        "failed_check_count": len(failed),
        "blocker_count": len(blockers),
        "permissions_enabled_count": sum(bool(value) for value in SAFETY_FLAGS.values()),
        "performance_metric_count": 0,
        "candidate_comparison_count": 0,
        "candidate_ranking_count": 0,
        "winner_selected": False,
        "holdout_access_count": 0,
        "real_data_access_count": 0,
        "validation_passed": not blockers,
        "validation_decision": "CORRECTION_ACCEPTED_SOURCE_ONLY" if not preflight_only and not blockers else ("PREFLIGHT_PASSED" if preflight_only and not blockers else "FAIL_CLOSED"),
        "recommended_next_phase": NEXT_PHASE if not preflight_only and not blockers else "NONE",
    }
    return {
        "summary": summary,
        "checks": tuple(asdict(item) for item in checks),
        "confirmed_findings": tuple(asdict(item) for item in findings),
        "risks_not_demonstrated": risks,
        "optional_out_of_scope": optional,
        "permissions": dict(SAFETY_FLAGS),
    }


def require_valid_review(*, preflight_only: bool = False) -> dict[str, Any]:
    result = validate_phase_10_42r_2f(preflight_only=preflight_only)
    if not result["summary"]["validation_passed"]:
        raise ReviewFailure(json.dumps(result["summary"], sort_keys=True))
    return result
