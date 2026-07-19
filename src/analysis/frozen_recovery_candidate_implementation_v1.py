from __future__ import annotations

from dataclasses import dataclass
import json
import math
from typing import Iterable

from src.analysis.recovery_candidate_family_specification_v1 import (
    EXPECTED_SPECIFICATION_ROOT_SHA256,
    FROZEN_VARIANT_COUNT,
    build_specification_artifacts,
    build_specification_manifest,
    canonical_sha256,
    verify_specification_manifest,
)


IMPLEMENTATION_SCHEMA_VERSION = "FROZEN_RECOVERY_CANDIDATE_IMPLEMENTATION_V1"
SOURCE_PHASE_2D_COMMIT = "a9ec58c493a46c9835b2ddb19c301f2957dadaca"
SOURCE_PHASE_2D_SPECIFICATION_MODULE_SHA256 = (
    "54f71b968c89239b0f4b5e49298be30ddf84c65170be3ce240743d94031f5c4b"
)
SYNTHETIC_FIXTURE_SOURCE = "SYNTHETIC_DETERMINISTIC_PHASE_10_42R_2E_V1"
ALLOWED_BEARISH_REGIMES = frozenset({"BEARISH", "STRONG_BEARISH"})
MAXIMUM_TRADE_BARS = 240
FIXED_REWARD_TO_RISK = 2.5

EXPECTED_VARIANT_IDS = (
    "RCV_SHORT_UPSIDE_SWEEP_REVERSAL_F01_N48_V01",
    "RCV_SHORT_UPSIDE_SWEEP_REVERSAL_F01_N96_V02",
    "RCV_SHORT_BREAKDOWN_RETEST_F02_N48_V01",
    "RCV_SHORT_BREAKDOWN_RETEST_F02_N96_V02",
    "RCV_SHORT_EMA_PULLBACK_CONTINUATION_F03_S000_V01",
    "RCV_SHORT_EMA_PULLBACK_CONTINUATION_F03_S025_V02",
)

FAMILY_HANDLER_VERSIONS = {
    "RCV_SHORT_UPSIDE_SWEEP_REVERSAL_F01_V1": "UPSIDE_SWEEP_REVERSAL_HANDLER_V1",
    "RCV_SHORT_BREAKDOWN_RETEST_F02_V1": "BREAKDOWN_RETEST_HANDLER_V1",
    "RCV_SHORT_EMA_PULLBACK_CONTINUATION_F03_V1": "EMA_PULLBACK_CONTINUATION_HANDLER_V1",
}

FAMILY_PARAMETER_KEYS = {
    "RCV_SHORT_UPSIDE_SWEEP_REVERSAL_F01_V1": {
        "prior_high_lookback_bars",
        "stop_atr_buffer",
        "wick_to_body_minimum",
    },
    "RCV_SHORT_BREAKDOWN_RETEST_F02_V1": {
        "break_atr",
        "retest_tolerance_atr",
        "retest_window_bars",
        "stop_atr_buffer",
        "support_lookback_bars",
    },
    "RCV_SHORT_EMA_PULLBACK_CONTINUATION_F03_V1": {
        "minimum_ema20_ema50_separation_atr",
        "stop_atr_buffer",
    },
}


class FrozenSpecificationError(RuntimeError):
    pass


@dataclass(frozen=True)
class SyntheticBar:
    open: float
    high: float
    low: float
    close: float
    closed: bool = True
    source: str = SYNTHETIC_FIXTURE_SOURCE


@dataclass(frozen=True)
class ClosedMtfContext:
    regime_1h: str
    regime_4h: str
    signal_close_unit: int
    regime_1h_available_unit: int
    regime_4h_available_unit: int
    source: str = SYNTHETIC_FIXTURE_SOURCE


@dataclass(frozen=True)
class FrozenVariantImplementation:
    evaluation_order: int
    family_id: str
    variant_id: str
    parameter_json: str
    handler_version: str
    family_specification_sha256: str
    variant_specification_sha256: str
    specification_root_sha256: str
    implementation_sha256: str

    @property
    def parameters(self) -> dict[str, float | int]:
        return json.loads(self.parameter_json)


@dataclass(frozen=True)
class SignalDecision:
    signal: bool
    reason: str
    stop_price: float | None


@dataclass(frozen=True)
class OrderDecision:
    accepted: bool
    reason: str
    entry_price: float | None
    stop_price: float | None
    target_price: float | None


@dataclass(frozen=True)
class ExitDecision:
    resolved: bool
    reason: str
    elapsed_trade_bars: int


def verify_phase_2d_specification_root() -> str:
    try:
        artifacts = build_specification_artifacts()
        manifest, root = build_specification_manifest(artifacts)
        valid, details = verify_specification_manifest(artifacts, manifest, root)
    except Exception as exc:
        raise FrozenSpecificationError(
            f"Phase 2D specification cannot be reconstructed: {type(exc).__name__}: {exc}"
        ) from exc
    if not valid:
        raise FrozenSpecificationError(
            f"Phase 2D manifest does not reproduce: {details}"
        )
    if len(root) != 1:
        raise FrozenSpecificationError("Phase 2D root must contain exactly one row.")
    root_sha = str(root.iloc[0]["specification_root_sha256"])
    if root_sha != EXPECTED_SPECIFICATION_ROOT_SHA256:
        raise FrozenSpecificationError(
            "Phase 2D root differs from the frozen golden SHA-256."
        )
    return root_sha


def build_verified_implementations() -> tuple[FrozenVariantImplementation, ...]:
    root_sha = verify_phase_2d_specification_root()
    artifacts = build_specification_artifacts()
    variants = artifacts["candidate_variant_registry"]
    implementations: list[FrozenVariantImplementation] = []
    for row in variants.sort_values("evaluation_order").itertuples(index=False):
        family_id = str(row.family_id)
        variant_id = str(row.variant_id)
        if family_id not in FAMILY_HANDLER_VERSIONS:
            raise FrozenSpecificationError(f"No frozen handler for {family_id}.")
        parameters = json.loads(str(row.parameter_json))
        if set(parameters) != FAMILY_PARAMETER_KEYS[family_id]:
            raise FrozenSpecificationError(
                f"Parameter schema drift for {variant_id}: {sorted(parameters)}"
            )
        payload = {
            "implementation_schema_version": IMPLEMENTATION_SCHEMA_VERSION,
            "specification_root_sha256": root_sha,
            "evaluation_order": int(row.evaluation_order),
            "family_id": family_id,
            "variant_id": variant_id,
            "parameter_json": str(row.parameter_json),
            "handler_version": FAMILY_HANDLER_VERSIONS[family_id],
            "family_specification_sha256": str(row.family_specification_sha256),
            "variant_specification_sha256": str(row.variant_specification_sha256),
        }
        implementations.append(
            FrozenVariantImplementation(
                evaluation_order=payload["evaluation_order"],
                family_id=family_id,
                variant_id=variant_id,
                parameter_json=payload["parameter_json"],
                handler_version=payload["handler_version"],
                family_specification_sha256=payload[
                    "family_specification_sha256"
                ],
                variant_specification_sha256=payload[
                    "variant_specification_sha256"
                ],
                specification_root_sha256=root_sha,
                implementation_sha256=canonical_sha256(payload),
            )
        )
    actual_ids = tuple(item.variant_id for item in implementations)
    if len(implementations) != FROZEN_VARIANT_COUNT or actual_ids != EXPECTED_VARIANT_IDS:
        raise FrozenSpecificationError(
            f"Frozen implementation order mismatch: {actual_ids}"
        )
    return tuple(implementations)


def _finite(value: float) -> bool:
    return isinstance(value, (int, float)) and math.isfinite(float(value))


def synthetic_bar_is_valid(bar: SyntheticBar) -> bool:
    values = (bar.open, bar.high, bar.low, bar.close)
    return bool(
        bar.source == SYNTHETIC_FIXTURE_SOURCE
        and bar.closed
        and all(_finite(value) for value in values)
        and bar.high >= max(bar.open, bar.close)
        and bar.low <= min(bar.open, bar.close)
        and bar.high >= bar.low
    )


def synthetic_bars_are_valid(bars: Iterable[SyntheticBar]) -> bool:
    materialized = tuple(bars)
    return bool(materialized and all(synthetic_bar_is_valid(bar) for bar in materialized))


def mtf_context_is_closed_and_allowed(context: ClosedMtfContext) -> bool:
    return bool(
        context.source == SYNTHETIC_FIXTURE_SOURCE
        and context.regime_1h in ALLOWED_BEARISH_REGIMES
        and context.regime_4h in ALLOWED_BEARISH_REGIMES
        and context.regime_1h_available_unit <= context.signal_close_unit
        and context.regime_4h_available_unit <= context.signal_close_unit
    )


def _ewm_adjust_false(
    values: tuple[float, ...],
    *,
    alpha: float,
    minimum_periods: int,
) -> float | None:
    if len(values) < minimum_periods or not values:
        return None
    if not all(_finite(value) for value in values):
        return None
    value = float(values[0])
    for item in values[1:]:
        value = alpha * float(item) + (1.0 - alpha) * value
    return value


def ema_close_span(bars: tuple[SyntheticBar, ...], span: int) -> float | None:
    if span <= 0 or not synthetic_bars_are_valid(bars):
        return None
    return _ewm_adjust_false(
        tuple(float(bar.close) for bar in bars),
        alpha=2.0 / (span + 1.0),
        minimum_periods=span,
    )


def wilder_atr14(bars: tuple[SyntheticBar, ...]) -> float | None:
    if not synthetic_bars_are_valid(bars):
        return None
    true_ranges: list[float] = []
    previous_close: float | None = None
    for bar in bars:
        if previous_close is None:
            true_range = bar.high - bar.low
        else:
            true_range = max(
                bar.high - bar.low,
                abs(bar.high - previous_close),
                abs(bar.low - previous_close),
            )
        true_ranges.append(float(true_range))
        previous_close = float(bar.close)
    return _ewm_adjust_false(
        tuple(true_ranges),
        alpha=1.0 / 14.0,
        minimum_periods=14,
    )


def breakdown_condition(
    *,
    close: float,
    support: float,
    atr14: float,
    break_atr: float,
) -> bool:
    return bool(close < support - break_atr * atr14)


def retest_condition(
    *,
    current: SyntheticBar,
    support: float,
    atr14: float,
    tolerance_atr: float,
) -> bool:
    return bool(
        synthetic_bar_is_valid(current)
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
    if not synthetic_bar_is_valid(current) or atr14_t <= 0.0:
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
        and current.close <= prior_high
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
        support = min(
            bar.low for bar in history[index - support_lookback : index]
        )
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
    if any(
        value is None
        for value in (ema20_t, ema50_t, ema200_t, ema20_previous, atr14_t)
    ):
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
    if implementation.specification_root_sha256 != EXPECTED_SPECIFICATION_ROOT_SHA256:
        raise FrozenSpecificationError("Implementation is not bound to the golden root.")
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
    if implementation.specification_root_sha256 != EXPECTED_SPECIFICATION_ROOT_SHA256:
        raise FrozenSpecificationError("Order implementation is not root-bound.")
    if not signal.signal or signal.stop_price is None:
        return OrderDecision(False, "NO_SIGNAL", None, None, None)
    if position_already_open:
        return OrderDecision(False, "OVERLAPPING_POSITION_BLOCKED", None, None, None)
    if fill_bar_index != signal_bar_index + 1:
        return OrderDecision(False, "FILL_NOT_NEXT_BAR_OPEN", None, None, None)
    if not _finite(next_open) or next_open <= 0.0:
        return OrderDecision(False, "INVALID_NEXT_OPEN", None, None, None)
    if signal.stop_price <= next_open:
        return OrderDecision(False, "INVALID_GAP_STOP_NOT_ABOVE_ENTRY", None, None, None)
    risk_distance = signal.stop_price - next_open
    target = next_open - FIXED_REWARD_TO_RISK * risk_distance
    return OrderDecision(
        True,
        "ORDER_ACCEPTED",
        float(next_open),
        float(signal.stop_price),
        float(target),
    )


def resolve_short_exit(
    order: OrderDecision,
    bars_from_entry: tuple[SyntheticBar, ...],
) -> ExitDecision:
    if not order.accepted or any(
        value is None
        for value in (order.entry_price, order.stop_price, order.target_price)
    ):
        return ExitDecision(False, "ORDER_NOT_ACCEPTED", 0)
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
