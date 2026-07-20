from __future__ import annotations

import ast
import dataclasses
import hashlib
import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from src.analysis import frozen_recovery_candidate_implementation_v2 as corrected


PHASE = "10.42R.2G"
SOURCE_PHASE_2F_COMMIT = "a1fd9b168e61e94635c16a0f9e808f360268d676"
CORRECTED_SOURCE_PATH = Path(
    "src/analysis/frozen_recovery_candidate_implementation_v2.py"
)
EXPECTED_CORRECTED_SOURCE_SHA256 = (
    "ccf3cc05823515fa56e9e1183eb51ab903503e310aa037248847ad7445b2cc1e"
)
EXPECTED_VARIANT_IDS = (
    "RCV_SHORT_UPSIDE_SWEEP_REVERSAL_F01_N48_V01",
    "RCV_SHORT_UPSIDE_SWEEP_REVERSAL_F01_N96_V02",
    "RCV_SHORT_BREAKDOWN_RETEST_F02_N48_V01",
    "RCV_SHORT_BREAKDOWN_RETEST_F02_N96_V02",
    "RCV_SHORT_EMA_PULLBACK_CONTINUATION_F03_S000_V01",
    "RCV_SHORT_EMA_PULLBACK_CONTINUATION_F03_S025_V02",
)
ACCEPTED_DECISION = "CORRECTION_ACCEPTED_INDEPENDENT_SYNTHETIC_ONLY"
REJECTED_DECISION = "CORRECTION_REJECTED_INDEPENDENT_SYNTHETIC_ONLY"
RECOMMENDED_NEXT_PHASE = (
    "PHASE_10_42R_2H_FROZEN_RECOVERY_CANDIDATE_"
    "CONTROLLED_HISTORICAL_EVALUATION_PREREGISTRATION_V1"
)

PROHIBITED_IMPORT_ROOTS = {
    "ccxt",
    "httpx",
    "numpy",
    "pandas",
    "requests",
    "socket",
    "urllib",
    "websocket",
}
PROHIBITED_PATH_PREFIXES = (
    "data/",
    "reports/",
    "runtime/",
)
PROHIBITED_CALL_NAMES = {
    "read_csv",
    "read_excel",
    "to_csv",
    "to_excel",
    "download",
    "urlopen",
}

PERMISSION_FLAGS = {
    "real_data_access_allowed": False,
    "holdout_access_allowed": False,
    "historical_evaluation_allowed": False,
    "performance_metrics_allowed": False,
    "candidate_comparison_allowed": False,
    "candidate_ranking_allowed": False,
    "winner_selection_allowed": False,
    "forward_observation_allowed": False,
    "official_dataset_write_allowed": False,
    "paper_trade_execution_allowed": False,
    "real_capital_allowed": False,
    "live_alerts_allowed": False,
    "market_execution_allowed": False,
    "exchange_execution_allowed": False,
    "automation_allowed": False,
}


@dataclass(frozen=True)
class AcceptanceCheck:
    check_id: str
    check_name: str
    group: str
    passed: bool
    details: str
    blocker: bool


class SyntheticAcceptanceFailure(RuntimeError):
    pass


def normalized_source_sha256(path: Path) -> str:
    normalized = path.read_text(encoding="utf-8").replace("\r\n", "\n")
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def _check(
    check_id: str,
    check_name: str,
    group: str,
    passed: bool,
    details: str,
    *,
    blocker: bool = True,
) -> AcceptanceCheck:
    return AcceptanceCheck(
        check_id=check_id,
        check_name=check_name,
        group=group,
        passed=bool(passed),
        details=details,
        blocker=bool(blocker and not passed),
    )


def _source_is_static_and_synthetic_only(path: Path) -> tuple[bool, str]:
    try:
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source)
    except Exception as exc:
        return False, f"source_parse_failed={exc!r}"

    imported_roots: set[str] = set()
    prohibited_calls: set[str] = set()
    prohibited_paths: set[str] = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imported_roots.add(alias.name.split(".", 1)[0])

        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imported_roots.add(node.module.split(".", 1)[0])

        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                call_name = node.func.id
            elif isinstance(node.func, ast.Attribute):
                call_name = node.func.attr
            else:
                call_name = ""

            if call_name in PROHIBITED_CALL_NAMES:
                prohibited_calls.add(call_name)

        elif isinstance(node, ast.Constant) and isinstance(node.value, str):
            normalized = node.value.replace("\\", "/").lower()
            if normalized.startswith(PROHIBITED_PATH_PREFIXES):
                prohibited_paths.add(normalized)

    prohibited_imports = sorted(imported_roots & PROHIBITED_IMPORT_ROOTS)
    passed = not prohibited_imports and not prohibited_calls and not prohibited_paths

    details = json.dumps(
        {
            "prohibited_imports": prohibited_imports,
            "prohibited_calls": sorted(prohibited_calls),
            "prohibited_paths": sorted(prohibited_paths),
        },
        sort_keys=True,
    )
    return passed, details


def _canonical_implementations() -> tuple[corrected.FrozenVariantImplementation, ...]:
    implementations = corrected.build_verified_implementations()
    if not isinstance(implementations, tuple):
        raise SyntheticAcceptanceFailure("Canonical registry is not a tuple.")
    return implementations


def _implementation_map() -> dict[str, corrected.FrozenVariantImplementation]:
    implementations = _canonical_implementations()
    return {
        implementation.variant_id: implementation
        for implementation in implementations
    }


def _allowed_context(
    *,
    signal_close_unit: int = 100,
    regime_1h_available_unit: int = 100,
    regime_4h_available_unit: int = 100,
    regime_1h: str | None = None,
    regime_4h: str | None = None,
) -> corrected.ClosedMtfContext:
    regimes = tuple(sorted(corrected.ALLOWED_BEARISH_REGIMES))
    if not regimes:
        raise SyntheticAcceptanceFailure("No allowed bearish MTF regimes found.")
    selected_1h = regime_1h if regime_1h is not None else regimes[0]
    selected_4h = regime_4h if regime_4h is not None else regimes[0]
    return corrected.ClosedMtfContext(
        regime_1h=selected_1h,
        regime_4h=selected_4h,
        signal_close_unit=signal_close_unit,
        regime_1h_available_unit=regime_1h_available_unit,
        regime_4h_available_unit=regime_4h_available_unit,
    )


def _flat_history(count: int = 120) -> tuple[corrected.SyntheticBar, ...]:
    return tuple(
        corrected.SyntheticBar(
            open=100.0,
            high=101.0,
            low=99.0,
            close=100.0,
        )
        for _ in range(count)
    )


def _f01_positive_current() -> corrected.SyntheticBar:
    return corrected.SyntheticBar(
        open=100.0,
        high=102.0,
        low=98.5,
        close=99.0,
    )


def _f01_equality_current() -> corrected.SyntheticBar:
    return corrected.SyntheticBar(
        open=101.5,
        high=102.0,
        low=100.0,
        close=101.0,
    )


def _f02_history() -> tuple[corrected.SyntheticBar, ...]:
    base = list(_flat_history(112))
    base.append(
        corrected.SyntheticBar(
            open=100.0,
            high=100.0,
            low=96.5,
            close=97.0,
        )
    )
    base.extend(
        corrected.SyntheticBar(
            open=97.6,
            high=98.0,
            low=96.8,
            close=97.4,
        )
        for _ in range(7)
    )
    return tuple(base)


def _f02_positive_current() -> corrected.SyntheticBar:
    return corrected.SyntheticBar(
        open=99.2,
        high=99.4,
        low=97.7,
        close=98.0,
    )


def _f02_blocked_current() -> corrected.SyntheticBar:
    return corrected.SyntheticBar(
        open=97.5,
        high=98.0,
        low=96.9,
        close=97.4,
    )


def _ema_history(count: int = 230) -> tuple[corrected.SyntheticBar, ...]:
    bars: list[corrected.SyntheticBar] = []
    for index in range(count):
        close = 200.0 - 0.4 * index
        bars.append(
            corrected.SyntheticBar(
                open=close + 0.2,
                high=close + 0.6,
                low=close - 0.6,
                close=close,
            )
        )
    return tuple(bars)


def _ema_positive_current() -> corrected.SyntheticBar:
    return corrected.SyntheticBar(
        open=112.0,
        high=113.0,
        low=106.0,
        close=107.5,
    )


def _ema_blocked_current() -> corrected.SyntheticBar:
    return corrected.SyntheticBar(
        open=107.6,
        high=108.0,
        low=106.8,
        close=107.4,
    )


def _positive_signal(
    implementation: corrected.FrozenVariantImplementation,
) -> corrected.SignalDecision:
    if implementation.family_id == "RCV_SHORT_UPSIDE_SWEEP_REVERSAL_F01_V1":
        history = _flat_history()
        current = _f01_positive_current()
    elif implementation.family_id == "RCV_SHORT_BREAKDOWN_RETEST_F02_V1":
        history = _f02_history()
        current = _f02_positive_current()
    elif (
        implementation.family_id
        == "RCV_SHORT_EMA_PULLBACK_CONTINUATION_F03_V1"
    ):
        history = _ema_history()
        current = _ema_positive_current()
    else:
        raise SyntheticAcceptanceFailure(
            f"Unknown canonical family: {implementation.family_id}"
        )

    return corrected.evaluate_frozen_signal(
        implementation,
        history=history,
        current=current,
        context=_allowed_context(),
    )


def _accepted_order(
    implementation: corrected.FrozenVariantImplementation,
) -> corrected.OrderDecision:
    signal = corrected.SignalDecision(True, "SIGNAL", 105.0)
    return corrected.construct_next_open_short_order(
        implementation,
        signal,
        signal_bar_index=10,
        fill_bar_index=11,
        next_open=100.0,
        position_already_open=False,
    )


def _quiet_bar() -> corrected.SyntheticBar:
    return corrected.SyntheticBar(
        open=100.0,
        high=101.0,
        low=99.0,
        close=100.0,
    )


def _case(
    name: str,
    group: str,
    operation: Callable[[], bool],
) -> AcceptanceCheck:
    try:
        passed = operation() is True
        details = "operation_returned_true" if passed else "operation_returned_false"
    except Exception as exc:
        passed = False
        details = f"{type(exc).__name__}: {exc}"
    return _check(
        check_id="",
        check_name=name,
        group=group,
        passed=passed,
        details=details,
    )


def _raises_frozen_specification_error(
    operation: Callable[[], object],
) -> bool:
    try:
        operation()
    except corrected.FrozenSpecificationError:
        return True
    return False


def run_independent_synthetic_acceptance_cases() -> tuple[AcceptanceCheck, ...]:
    implementations = _canonical_implementations()
    by_id = _implementation_map()
    cases: list[AcceptanceCheck] = []

    for implementation in implementations:
        cases.append(
            _case(
                f"positive_signal_{implementation.variant_id}",
                "positive_family_acceptance",
                lambda implementation=implementation: (
                    (signal := _positive_signal(implementation)).signal is True
                    and signal.reason == "SIGNAL"
                    and signal.stop_price is not None
                    and math.isfinite(float(signal.stop_price))
                ),
            )
        )

    f01_variants = (
        by_id["RCV_SHORT_UPSIDE_SWEEP_REVERSAL_F01_N48_V01"],
        by_id["RCV_SHORT_UPSIDE_SWEEP_REVERSAL_F01_N96_V02"],
    )
    for implementation in f01_variants:
        cases.append(
            _case(
                f"f01_close_equality_blocks_{implementation.variant_id}",
                "corrected_boundary_acceptance",
                lambda implementation=implementation: (
                    corrected.evaluate_frozen_signal(
                        implementation,
                        history=_flat_history(),
                        current=_f01_equality_current(),
                        context=_allowed_context(),
                    ).reason
                    == "UPSIDE_SWEEP_RULE_BLOCKED"
                ),
            )
        )

    f02_variants = (
        by_id["RCV_SHORT_BREAKDOWN_RETEST_F02_N48_V01"],
        by_id["RCV_SHORT_BREAKDOWN_RETEST_F02_N96_V02"],
    )
    for implementation in f02_variants:
        cases.append(
            _case(
                f"f02_retest_boundary_blocks_{implementation.variant_id}",
                "family_negative_acceptance",
                lambda implementation=implementation: (
                    corrected.evaluate_frozen_signal(
                        implementation,
                        history=_f02_history(),
                        current=_f02_blocked_current(),
                        context=_allowed_context(),
                    ).reason
                    == "BREAKDOWN_RETEST_RULE_BLOCKED"
                ),
            )
        )

    f03_variants = (
        by_id["RCV_SHORT_EMA_PULLBACK_CONTINUATION_F03_S000_V01"],
        by_id["RCV_SHORT_EMA_PULLBACK_CONTINUATION_F03_S025_V02"],
    )
    for implementation in f03_variants:
        cases.append(
            _case(
                f"f03_pullback_boundary_blocks_{implementation.variant_id}",
                "family_negative_acceptance",
                lambda implementation=implementation: (
                    corrected.evaluate_frozen_signal(
                        implementation,
                        history=_ema_history(),
                        current=_ema_blocked_current(),
                        context=_allowed_context(),
                    ).reason
                    == "EMA_PULLBACK_RULE_BLOCKED"
                ),
            )
        )

    primary = implementations[0]

    invalid_bar_cases = (
        (
            "open_bar_blocks",
            corrected.SyntheticBar(100.0, 101.0, 99.0, 100.0, closed=False),
        ),
        (
            "wrong_source_bar_blocks",
            corrected.SyntheticBar(
                100.0,
                101.0,
                99.0,
                100.0,
                source="NOT_SYNTHETIC_ACCEPTANCE",
            ),
        ),
        (
            "nonfinite_bar_blocks",
            corrected.SyntheticBar(100.0, math.inf, 99.0, 100.0),
        ),
        (
            "incoherent_bar_blocks",
            corrected.SyntheticBar(100.0, 99.0, 101.0, 100.0),
        ),
    )
    for name, current in invalid_bar_cases:
        cases.append(
            _case(
                name,
                "synthetic_input_fail_closed",
                lambda current=current: (
                    corrected.evaluate_frozen_signal(
                        primary,
                        history=_flat_history(),
                        current=current,
                        context=_allowed_context(),
                    ).reason
                    == "NON_SYNTHETIC_OR_INVALID_BAR"
                ),
            )
        )

    mtf_cases = (
        (
            "late_1h_context_blocks",
            _allowed_context(regime_1h_available_unit=101),
        ),
        (
            "late_4h_context_blocks",
            _allowed_context(regime_4h_available_unit=101),
        ),
        (
            "unknown_regime_blocks",
            _allowed_context(regime_1h="UNKNOWN_REGIME"),
        ),
        (
            "infinite_signal_unit_blocks",
            dataclasses.replace(_allowed_context(), signal_close_unit=math.inf),
        ),
        (
            "fractional_signal_unit_blocks",
            dataclasses.replace(_allowed_context(), signal_close_unit=100.5),
        ),
        (
            "boolean_signal_unit_blocks",
            dataclasses.replace(_allowed_context(), signal_close_unit=True),
        ),
    )
    for name, context in mtf_cases:
        cases.append(
            _case(
                name,
                "mtf_fail_closed",
                lambda context=context: (
                    corrected.evaluate_frozen_signal(
                        primary,
                        history=_flat_history(),
                        current=_f01_positive_current(),
                        context=context,
                    ).reason
                    == "MTF_CONTEXT_BLOCKED"
                ),
            )
        )

    tampered = dataclasses.replace(
        primary,
        parameter_json=(
            '{"prior_high_lookback_bars":1,'
            '"stop_atr_buffer":0.25,'
            '"wick_to_body_minimum":1.0}'
        ),
    )
    cases.append(
        _case(
            "tampered_implementation_identity_raises",
            "identity_fail_closed",
            lambda: _raises_frozen_specification_error(
                lambda: corrected.evaluate_frozen_signal(
                    tampered,
                    history=_flat_history(),
                    current=_f01_positive_current(),
                    context=_allowed_context(),
                )
            ),
        )
    )

    order = _accepted_order(primary)
    cases.extend(
        (
            _case(
                "next_open_order_accepts_and_preserves_rr_2_5",
                "order_acceptance",
                lambda: (
                    order.accepted is True
                    and order.reason == "ORDER_ACCEPTED"
                    and order.entry_price == 100.0
                    and order.stop_price == 105.0
                    and order.target_price == 87.5
                ),
            ),
            _case(
                "nonfinite_signal_stop_blocks",
                "order_fail_closed",
                lambda: (
                    corrected.construct_next_open_short_order(
                        primary,
                        corrected.SignalDecision(True, "SIGNAL", math.nan),
                        signal_bar_index=10,
                        fill_bar_index=11,
                        next_open=100.0,
                        position_already_open=False,
                    ).reason
                    == "INVALID_SIGNAL_STOP"
                ),
            ),
            _case(
                "invalid_position_state_blocks",
                "order_fail_closed",
                lambda: (
                    corrected.construct_next_open_short_order(
                        primary,
                        corrected.SignalDecision(True, "SIGNAL", 105.0),
                        signal_bar_index=10,
                        fill_bar_index=11,
                        next_open=100.0,
                        position_already_open=1,
                    ).reason
                    == "INVALID_POSITION_STATE"
                ),
            ),
            _case(
                "overlapping_position_blocks",
                "order_fail_closed",
                lambda: (
                    corrected.construct_next_open_short_order(
                        primary,
                        corrected.SignalDecision(True, "SIGNAL", 105.0),
                        signal_bar_index=10,
                        fill_bar_index=11,
                        next_open=100.0,
                        position_already_open=True,
                    ).reason
                    == "OVERLAPPING_POSITION_BLOCKED"
                ),
            ),
            _case(
                "fractional_bar_indexes_block",
                "order_fail_closed",
                lambda: (
                    corrected.construct_next_open_short_order(
                        primary,
                        corrected.SignalDecision(True, "SIGNAL", 105.0),
                        signal_bar_index=10.5,
                        fill_bar_index=11.5,
                        next_open=100.0,
                        position_already_open=False,
                    ).reason
                    == "INVALID_BAR_INDEX"
                ),
            ),
            _case(
                "boolean_bar_indexes_block",
                "order_fail_closed",
                lambda: (
                    corrected.construct_next_open_short_order(
                        primary,
                        corrected.SignalDecision(True, "SIGNAL", 105.0),
                        signal_bar_index=True,
                        fill_bar_index=2,
                        next_open=100.0,
                        position_already_open=False,
                    ).reason
                    == "INVALID_BAR_INDEX"
                ),
            ),
            _case(
                "non_next_bar_fill_blocks",
                "order_fail_closed",
                lambda: (
                    corrected.construct_next_open_short_order(
                        primary,
                        corrected.SignalDecision(True, "SIGNAL", 105.0),
                        signal_bar_index=10,
                        fill_bar_index=12,
                        next_open=100.0,
                        position_already_open=False,
                    ).reason
                    == "FILL_NOT_NEXT_BAR_OPEN"
                ),
            ),
            _case(
                "invalid_next_open_blocks",
                "order_fail_closed",
                lambda: (
                    corrected.construct_next_open_short_order(
                        primary,
                        corrected.SignalDecision(True, "SIGNAL", 105.0),
                        signal_bar_index=10,
                        fill_bar_index=11,
                        next_open=math.inf,
                        position_already_open=False,
                    ).reason
                    == "INVALID_NEXT_OPEN"
                ),
            ),
            _case(
                "gap_above_stop_blocks",
                "order_fail_closed",
                lambda: (
                    corrected.construct_next_open_short_order(
                        primary,
                        corrected.SignalDecision(True, "SIGNAL", 105.0),
                        signal_bar_index=10,
                        fill_bar_index=11,
                        next_open=105.0,
                        position_already_open=False,
                    ).reason
                    == "INVALID_GAP_STOP_NOT_ABOVE_ENTRY"
                ),
            ),
        )
    )

    stop_bar = corrected.SyntheticBar(100.0, 105.0, 99.0, 104.0)
    target_bar = corrected.SyntheticBar(100.0, 101.0, 87.5, 90.0)
    simultaneous_bar = corrected.SyntheticBar(100.0, 105.0, 87.5, 100.0)
    invalid_exit_bar = corrected.SyntheticBar(
        100.0,
        101.0,
        99.0,
        100.0,
        closed=False,
    )
    invalid_accepted_order = corrected.OrderDecision(
        True,
        "ORDER_ACCEPTED",
        100.0,
        math.nan,
        87.5,
    )

    cases.extend(
        (
            _case(
                "target_exit_resolves",
                "exit_acceptance",
                lambda: (
                    corrected.resolve_short_exit(order, (target_bar,)).reason
                    == "TARGET"
                ),
            ),
            _case(
                "stop_exit_resolves",
                "exit_acceptance",
                lambda: (
                    corrected.resolve_short_exit(order, (stop_bar,)).reason
                    == "STOP"
                ),
            ),
            _case(
                "simultaneous_stop_is_conservative",
                "exit_acceptance",
                lambda: (
                    corrected.resolve_short_exit(order, (simultaneous_bar,)).reason
                    == "STOP_FIRST_SIMULTANEOUS"
                ),
            ),
            _case(
                "trade_remains_open_at_239_bars",
                "exit_boundary_acceptance",
                lambda: (
                    corrected.resolve_short_exit(
                        order,
                        tuple(_quiet_bar() for _ in range(239)),
                    )
                    == corrected.ExitDecision(False, "OPEN_NO_EXIT", 239)
                ),
            ),
            _case(
                "time_exit_resolves_at_240_bars",
                "exit_boundary_acceptance",
                lambda: (
                    corrected.resolve_short_exit(
                        order,
                        tuple(_quiet_bar() for _ in range(240)),
                    )
                    == corrected.ExitDecision(True, "TIME_EXIT", 240)
                ),
            ),
            _case(
                "nonfinite_accepted_order_blocks_exit",
                "exit_fail_closed",
                lambda: (
                    corrected.resolve_short_exit(
                        invalid_accepted_order,
                        (_quiet_bar(),),
                    ).reason
                    == "INVALID_ACCEPTED_ORDER"
                ),
            ),
            _case(
                "invalid_exit_bar_blocks",
                "exit_fail_closed",
                lambda: (
                    corrected.resolve_short_exit(
                        order,
                        (invalid_exit_bar,),
                    ).reason
                    == "NON_SYNTHETIC_OR_INVALID_EXIT_BAR"
                ),
            ),
        )
    )

    return tuple(
        dataclasses.replace(check, check_id=f"2G-SYN-{index:03d}")
        for index, check in enumerate(cases, start=1)
    )


def _preflight_checks() -> tuple[AcceptanceCheck, ...]:
    checks: list[AcceptanceCheck] = []

    source_exists = CORRECTED_SOURCE_PATH.is_file()
    checks.append(
        _check(
            "2G-PRE-001",
            "corrected_source_exists",
            "source_identity",
            source_exists,
            str(CORRECTED_SOURCE_PATH),
        )
    )

    source_hash = (
        normalized_source_sha256(CORRECTED_SOURCE_PATH)
        if source_exists
        else ""
    )
    checks.append(
        _check(
            "2G-PRE-002",
            "corrected_source_hash_exact",
            "source_identity",
            source_hash == EXPECTED_CORRECTED_SOURCE_SHA256,
            f"actual={source_hash}",
        )
    )

    static_passed, static_details = (
        _source_is_static_and_synthetic_only(CORRECTED_SOURCE_PATH)
        if source_exists
        else (False, "source_missing")
    )
    checks.append(
        _check(
            "2G-PRE-003",
            "corrected_source_is_static_and_synthetic_only",
            "source_scope",
            static_passed,
            static_details,
        )
    )

    implementations_first = _canonical_implementations()
    implementations_second = _canonical_implementations()
    actual_ids = tuple(item.variant_id for item in implementations_first)

    checks.append(
        _check(
            "2G-PRE-004",
            "canonical_registry_count_six",
            "registry",
            len(implementations_first) == 6,
            f"count={len(implementations_first)}",
        )
    )
    checks.append(
        _check(
            "2G-PRE-005",
            "canonical_variant_order_exact",
            "registry",
            actual_ids == EXPECTED_VARIANT_IDS,
            f"actual={actual_ids!r}",
        )
    )
    checks.append(
        _check(
            "2G-PRE-006",
            "canonical_registry_deterministic",
            "registry",
            implementations_first == implementations_second,
            "two independent builds compared",
        )
    )
    checks.append(
        _check(
            "2G-PRE-007",
            "phase_2e_source_commit_frozen",
            "lineage",
            corrected.SOURCE_PHASE_2E_COMMIT
            == "7d7f8ee81156b1858a636b586eb5636b34b1c801",
            f"actual={corrected.SOURCE_PHASE_2E_COMMIT}",
        )
    )
    checks.append(
        _check(
            "2G-PRE-008",
            "all_permissions_remain_disabled",
            "permissions",
            not any(PERMISSION_FLAGS.values()),
            json.dumps(PERMISSION_FLAGS, sort_keys=True),
        )
    )

    return tuple(checks)


def validate_phase_10_42r_2g(
    *,
    preflight_only: bool = False,
) -> dict[str, Any]:
    preflight_checks = _preflight_checks()
    preflight_passed = all(check.passed for check in preflight_checks)

    synthetic_checks: tuple[AcceptanceCheck, ...] = ()
    if preflight_passed and not preflight_only:
        synthetic_checks = run_independent_synthetic_acceptance_cases()

    all_checks = (*preflight_checks, *synthetic_checks)
    failed_checks = tuple(check for check in all_checks if not check.passed)
    blockers = tuple(check for check in all_checks if check.blocker)

    acceptance_completed = not preflight_only and bool(synthetic_checks)
    validation_passed = (
        preflight_passed
        and not failed_checks
        and not blockers
        and (preflight_only or acceptance_completed)
    )

    if preflight_only:
        decision = "PREFLIGHT_PASSED" if validation_passed else "PREFLIGHT_FAILED"
    else:
        decision = ACCEPTED_DECISION if validation_passed else REJECTED_DECISION

    accepted_variant_ids = (
        list(EXPECTED_VARIANT_IDS)
        if validation_passed and not preflight_only
        else []
    )

    summary = {
        "phase": PHASE,
        "preflight_only": preflight_only,
        "source_phase_2f_commit": SOURCE_PHASE_2F_COMMIT,
        "corrected_source_sha256": EXPECTED_CORRECTED_SOURCE_SHA256,
        "preflight_check_count": len(preflight_checks),
        "synthetic_case_count": len(synthetic_checks),
        "total_check_count": len(all_checks),
        "failed_check_count": len(failed_checks),
        "blocker_count": len(blockers),
        "accepted_variant_count": len(accepted_variant_ids),
        "acceptance_completed": acceptance_completed,
        "real_data_access_count": 0,
        "holdout_access_count": 0,
        "historical_evaluation_count": 0,
        "performance_metric_count": 0,
        "candidate_comparison_count": 0,
        "candidate_ranking_count": 0,
        "winner_selected": False,
        "report_artifact_write_count": 0,
        "permissions_enabled_count": sum(
            1 for value in PERMISSION_FLAGS.values() if value
        ),
        "validation_passed": validation_passed,
        "validation_decision": decision,
        "recommended_next_phase": (
            RECOMMENDED_NEXT_PHASE
            if validation_passed and not preflight_only
            else "NONE"
        ),
    }

    return {
        "summary": summary,
        "checks": [dataclasses.asdict(check) for check in all_checks],
        "accepted_variant_ids": accepted_variant_ids,
        "permissions": dict(PERMISSION_FLAGS),
    }


def require_valid_acceptance(
    *,
    preflight_only: bool = False,
) -> dict[str, Any]:
    result = validate_phase_10_42r_2g(preflight_only=preflight_only)
    if not result["summary"]["validation_passed"]:
        raise SyntheticAcceptanceFailure(
            json.dumps(result["summary"], sort_keys=True)
        )
    return result
