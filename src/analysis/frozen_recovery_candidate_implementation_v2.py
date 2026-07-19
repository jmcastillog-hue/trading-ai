from __future__ import annotations

from dataclasses import dataclass
import math

import src.analysis.frozen_recovery_candidate_implementation_v1 as v1


CORRECTION_SCHEMA_VERSION = "FROZEN_RECOVERY_CANDIDATE_IMPLEMENTATION_V2"
SOURCE_PHASE_2E_COMMIT = "7d7f8ee81156b1858a636b586eb5636b34b1c801"
SOURCE_PHASE_2E_IMPLEMENTATION_SHA256 = (
    "8ac370bf803e9bf033ce9f7e2edc94cb27ab4811a387bb2974e6dffeb53c83d4"
)

SyntheticBar = v1.SyntheticBar
ClosedMtfContext = v1.ClosedMtfContext
FrozenVariantImplementation = v1.FrozenVariantImplementation
SignalDecision = v1.SignalDecision
OrderDecision = v1.OrderDecision
ExitDecision = v1.ExitDecision
FrozenSpecificationError = v1.FrozenSpecificationError

EXPECTED_SPECIFICATION_ROOT_SHA256 = v1.EXPECTED_SPECIFICATION_ROOT_SHA256
EXPECTED_VARIANT_IDS = v1.EXPECTED_VARIANT_IDS
SYNTHETIC_FIXTURE_SOURCE = v1.SYNTHETIC_FIXTURE_SOURCE
ALLOWED_BEARISH_REGIMES = v1.ALLOWED_BEARISH_REGIMES
MAXIMUM_TRADE_BARS = v1.MAXIMUM_TRADE_BARS
FIXED_REWARD_TO_RISK = v1.FIXED_REWARD_TO_RISK

verify_phase_2d_specification_root = v1.verify_phase_2d_specification_root
build_verified_implementations = v1.build_verified_implementations


def _finite(value: object) -> bool:
    return bool(
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(float(value))
    )


def _plain_int(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _require_verified_implementation(
    implementation: FrozenVariantImplementation,
) -> None:
    canonical = build_verified_implementations()
    if implementation not in canonical:
        raise FrozenSpecificationError(
            "Implementation identity differs from the frozen Phase 2D registry."
        )


def synthetic_bar_is_valid(bar: SyntheticBar) -> bool:
    values = (bar.open, bar.high, bar.low, bar.close)
    return bool(
        bar.source == SYNTHETIC_FIXTURE_SOURCE
        and bar.closed is True
        and all(_finite(value) for value in values)
        and bar.high >= max(bar.open, bar.close)
        and bar.low <= min(bar.open, bar.close)
        and bar.high >= bar.low
    )


def synthetic_bars_are_valid(bars: tuple[SyntheticBar, ...]) -> bool:
    return bool(bars and all(synthetic_bar_is_valid(bar) for bar in bars))


def mtf_context_is_closed_and_allowed(context: ClosedMtfContext) -> bool:
    units = (
        context.signal_close_unit,
        context.regime_1h_available_unit,
        context.regime_4h_available_unit,
    )
    return bool(
        context.source == SYNTHETIC_FIXTURE_SOURCE
        and context.regime_1h in ALLOWED_BEARISH_REGIMES
        and context.regime_4h in ALLOWED_BEARISH_REGIMES
        and all(_plain_int(value) for value in units)
        and context.regime_1h_available_unit <= context.signal_close_unit
        and context.regime_4h_available_unit <= context.signal_close_unit
    )


def ema_close_span(bars: tuple[SyntheticBar, ...], span: int) -> float | None:
    if not _plain_int(span) or span <= 0 or not synthetic_bars_are_valid(bars):
        return None
    return v1.ema_close_span(bars, span)


def wilder_atr14(bars: tuple[SyntheticBar, ...]) -> float | None:
    if not synthetic_bars_are_valid(bars):
        return None
    return v1.wilder_atr14(bars)


def breakdown_condition(
    *,
    close: float,
    support: float,
    atr14: float,
    break_atr: float,
) -> bool:
    values = (close, support, atr14, break_atr)
    return bool(
        all(_finite(value) for value in values)
        and atr14 > 0.0
        and break_atr >= 0.0
        and close < support - break_atr * atr14
    )


def retest_condition(
    *,
    current: SyntheticBar,
    support: float,
    atr14: float,
    tolerance_atr: float,
) -> bool:
    values = (support, atr14, tolerance_atr)
    return bool(
        synthetic_bar_is_valid(current)
        and all(_finite(value) for value in values)
        and atr14 > 0.0
        and tolerance_atr >= 0.0
        and current.high >= support - tolerance_atr * atr14
        and current.close < support
        and current.close < current.open
    )


def ema_pullback_condition(
    *,
    current: SyntheticBar,
    prior_close: float,
    ema20_t: float,
    ema50_t: float,
    ema200_t: float,
    ema20_previous: float,
    atr14_t: float,
    minimum_separation_atr: float,
) -> bool:
    values = (
        prior_close,
        ema20_t,
        ema50_t,
        ema200_t,
        ema20_previous,
        atr14_t,
        minimum_separation_atr,
    )
    if (
        not synthetic_bar_is_valid(current)
        or not all(_finite(value) for value in values)
        or atr14_t <= 0.0
        or minimum_separation_atr < 0.0
    ):
        return False
    separation = (ema50_t - ema20_t) / atr14_t
    return bool(
        ema20_t < ema50_t < ema200_t
        and separation >= minimum_separation_atr
        and prior_close < ema20_previous
        and current.high >= ema20_t
        and current.close < ema20_t
        and current.close < current.open
    )


def _evaluate_upside_sweep(
    implementation: FrozenVariantImplementation,
    history: tuple[SyntheticBar, ...],
    current: SyntheticBar,
) -> SignalDecision:
    parameters = implementation.parameters
    lookback = int(parameters["prior_high_lookback_bars"])
    if len(history) < lookback:
        return SignalDecision(False, "INSUFFICIENT_PRIOR_HIGH_HISTORY", None)
    prior_high = max(bar.high for bar in history[-lookback:])
    atr14_t = wilder_atr14((*history, current))
    if atr14_t is None or atr14_t <= 0.0:
        return SignalDecision(False, "ATR14_UNAVAILABLE", None)
    body = abs(current.close - current.open)
    upper_wick = current.high - max(current.open, current.close)
    passed = bool(
        current.high > prior_high
        and current.close < prior_high
        and current.close < current.open
        and body > 0.0
        and upper_wick >= float(parameters["wick_to_body_minimum"]) * body
    )
    if not passed:
        return SignalDecision(False, "UPSIDE_SWEEP_RULE_BLOCKED", None)
    stop = current.high + float(parameters["stop_atr_buffer"]) * atr14_t
    return SignalDecision(True, "SIGNAL", stop)


def _most_recent_breakdown(
    history: tuple[SyntheticBar, ...],
    *,
    support_lookback: int,
    retest_window: int,
    break_atr: float,
) -> tuple[float, int] | None:
    first_index = max(0, len(history) - retest_window)
    for index in range(len(history) - 1, first_index - 1, -1):
        if index < support_lookback:
            continue
        support = min(bar.low for bar in history[index - support_lookback : index])
        atr14_j = wilder_atr14(history[: index + 1])
        if atr14_j is None or atr14_j <= 0.0:
            continue
        if breakdown_condition(
            close=history[index].close,
            support=support,
            atr14=atr14_j,
            break_atr=break_atr,
        ):
            return float(support), index
    return None


def _evaluate_breakdown_retest(
    implementation: FrozenVariantImplementation,
    history: tuple[SyntheticBar, ...],
    current: SyntheticBar,
) -> SignalDecision:
    parameters = implementation.parameters
    breakdown = _most_recent_breakdown(
        history,
        support_lookback=int(parameters["support_lookback_bars"]),
        retest_window=int(parameters["retest_window_bars"]),
        break_atr=float(parameters["break_atr"]),
    )
    if breakdown is None:
        return SignalDecision(False, "BREAKDOWN_NOT_FOUND", None)
    support, _ = breakdown
    atr14_t = wilder_atr14((*history, current))
    if atr14_t is None or atr14_t <= 0.0:
        return SignalDecision(False, "ATR14_UNAVAILABLE", None)
    if not retest_condition(
        current=current,
        support=support,
        atr14=atr14_t,
        tolerance_atr=float(parameters["retest_tolerance_atr"]),
    ):
        return SignalDecision(False, "BREAKDOWN_RETEST_RULE_BLOCKED", None)
    stop = max(current.high, support) + float(parameters["stop_atr_buffer"]) * atr14_t
    return SignalDecision(True, "SIGNAL", stop)


def _evaluate_ema_pullback(
    implementation: FrozenVariantImplementation,
    history: tuple[SyntheticBar, ...],
    current: SyntheticBar,
) -> SignalDecision:
    if not history:
        return SignalDecision(False, "EMA_HISTORY_UNAVAILABLE", None)
    bars_to_t = (*history, current)
    ema20_t = ema_close_span(bars_to_t, 20)
    ema50_t = ema_close_span(bars_to_t, 50)
    ema200_t = ema_close_span(bars_to_t, 200)
    ema20_previous = ema_close_span(history, 20)
    atr14_t = wilder_atr14(bars_to_t)
    values = (ema20_t, ema50_t, ema200_t, ema20_previous, atr14_t)
    if any(value is None for value in values):
        return SignalDecision(False, "EMA_OR_ATR_FEATURE_UNAVAILABLE", None)
    parameters = implementation.parameters
    passed = ema_pullback_condition(
        current=current,
        prior_close=history[-1].close,
        ema20_t=float(ema20_t),
        ema50_t=float(ema50_t),
        ema200_t=float(ema200_t),
        ema20_previous=float(ema20_previous),
        atr14_t=float(atr14_t),
        minimum_separation_atr=float(
            parameters["minimum_ema20_ema50_separation_atr"]
        ),
    )
    if not passed:
        return SignalDecision(False, "EMA_PULLBACK_RULE_BLOCKED", None)
    stop = current.high + float(parameters["stop_atr_buffer"]) * float(atr14_t)
    return SignalDecision(True, "SIGNAL", stop)


def evaluate_frozen_signal(
    implementation: FrozenVariantImplementation,
    *,
    history: tuple[SyntheticBar, ...],
    current: SyntheticBar,
    context: ClosedMtfContext,
) -> SignalDecision:
    _require_verified_implementation(implementation)
    if not synthetic_bars_are_valid((*history, current)):
        return SignalDecision(False, "NON_SYNTHETIC_OR_INVALID_BAR", None)
    if not mtf_context_is_closed_and_allowed(context):
        return SignalDecision(False, "MTF_CONTEXT_BLOCKED", None)
    if implementation.family_id == "RCV_SHORT_UPSIDE_SWEEP_REVERSAL_F01_V1":
        return _evaluate_upside_sweep(implementation, history, current)
    if implementation.family_id == "RCV_SHORT_BREAKDOWN_RETEST_F02_V1":
        return _evaluate_breakdown_retest(implementation, history, current)
    if implementation.family_id == "RCV_SHORT_EMA_PULLBACK_CONTINUATION_F03_V1":
        return _evaluate_ema_pullback(implementation, history, current)
    raise FrozenSpecificationError(
        f"Unknown frozen family implementation: {implementation.family_id}"
    )


def construct_next_open_short_order(
    implementation: FrozenVariantImplementation,
    signal: SignalDecision,
    *,
    signal_bar_index: int,
    fill_bar_index: int,
    next_open: float,
    position_already_open: bool,
) -> OrderDecision:
    _require_verified_implementation(implementation)
    if signal.signal is not True or signal.reason != "SIGNAL":
        return OrderDecision(False, "NO_SIGNAL", None, None, None)
    if signal.stop_price is None or not _finite(signal.stop_price):
        return OrderDecision(False, "INVALID_SIGNAL_STOP", None, None, None)
    if not isinstance(position_already_open, bool):
        return OrderDecision(False, "INVALID_POSITION_STATE", None, None, None)
    if position_already_open:
        return OrderDecision(False, "OVERLAPPING_POSITION_BLOCKED", None, None, None)
    if not _plain_int(signal_bar_index) or not _plain_int(fill_bar_index):
        return OrderDecision(False, "INVALID_BAR_INDEX", None, None, None)
    if fill_bar_index != signal_bar_index + 1:
        return OrderDecision(False, "FILL_NOT_NEXT_BAR_OPEN", None, None, None)
    if not _finite(next_open) or next_open <= 0.0:
        return OrderDecision(False, "INVALID_NEXT_OPEN", None, None, None)
    if signal.stop_price <= next_open:
        return OrderDecision(
            False, "INVALID_GAP_STOP_NOT_ABOVE_ENTRY", None, None, None
        )
    risk_distance = signal.stop_price - next_open
    target = next_open - FIXED_REWARD_TO_RISK * risk_distance
    if not _finite(target):
        return OrderDecision(False, "INVALID_ORDER_PRICES", None, None, None)
    return OrderDecision(
        True,
        "ORDER_ACCEPTED",
        float(next_open),
        float(signal.stop_price),
        float(target),
    )


def _accepted_order_is_valid(order: OrderDecision) -> bool:
    if order.accepted is not True or order.reason != "ORDER_ACCEPTED":
        return False
    prices = (order.entry_price, order.stop_price, order.target_price)
    if any(value is None for value in prices) or not all(
        _finite(value) for value in prices
    ):
        return False
    entry = float(order.entry_price)
    stop = float(order.stop_price)
    target = float(order.target_price)
    if entry <= 0.0 or stop <= entry or target >= entry:
        return False
    expected_target = entry - FIXED_REWARD_TO_RISK * (stop - entry)
    return math.isclose(target, expected_target, rel_tol=0.0, abs_tol=1e-12)


def resolve_short_exit(
    order: OrderDecision,
    bars_from_entry: tuple[SyntheticBar, ...],
) -> ExitDecision:
    if order.accepted is not True:
        return ExitDecision(False, "ORDER_NOT_ACCEPTED", 0)
    if not _accepted_order_is_valid(order):
        return ExitDecision(False, "INVALID_ACCEPTED_ORDER", 0)
    if bars_from_entry and not synthetic_bars_are_valid(bars_from_entry):
        return ExitDecision(False, "NON_SYNTHETIC_OR_INVALID_EXIT_BAR", 0)
    for elapsed, bar in enumerate(bars_from_entry[:MAXIMUM_TRADE_BARS], start=1):
        stop_hit = bar.high >= float(order.stop_price)
        target_hit = bar.low <= float(order.target_price)
        if stop_hit:
            reason = "STOP_FIRST_SIMULTANEOUS" if target_hit else "STOP"
            return ExitDecision(True, reason, elapsed)
        if target_hit:
            return ExitDecision(True, "TARGET", elapsed)
        if elapsed == MAXIMUM_TRADE_BARS:
            return ExitDecision(True, "TIME_EXIT", elapsed)
    return ExitDecision(False, "OPEN_NO_EXIT", len(bars_from_entry))
