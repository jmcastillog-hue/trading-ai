import os
import sys

sys.path.append(
    os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            ".."
        )
    )
)

from structure.swing_points import (
    detect_swing_highs,
    detect_swing_lows
)

from scenarios.fibonacci_engine import (
    calculate_bearish_fibonacci_levels
)

from alerts.fib_v5_alert_engine import (
    calculate_short_tp1,
    classify_alert_state,
    detect_latest_entry_signal
)


def find_bearish_impulses(
    htf_df,
    lookback_bars=300,
    min_drop_pct=5.0,
    max_impulse_bars=80,
    left_bars=2,
    right_bars=2
):

    recent_df = htf_df.tail(
        lookback_bars
    ).copy()

    recent_df = recent_df.reset_index(
        drop=True
    )

    swing_highs = detect_swing_highs(
        recent_df,
        left_bars=left_bars,
        right_bars=right_bars
    )

    swing_lows = detect_swing_lows(
        recent_df,
        left_bars=left_bars,
        right_bars=right_bars
    )

    impulses = []

    for swing_high in swing_highs:

        candidate_lows = [
            swing_low for swing_low in swing_lows
            if swing_low["index"] > swing_high["index"]
            and swing_low["index"] <= swing_high["index"] + max_impulse_bars
        ]

        if len(candidate_lows) == 0:
            continue

        swing_low = min(
            candidate_lows,
            key=lambda x: x["price"]
        )

        high_price = swing_high["price"]
        low_price = swing_low["price"]

        drop_pct = (
            (high_price - low_price)
            / high_price
        ) * 100

        if drop_pct < min_drop_pct:
            continue

        impulses.append({
            "high_index": swing_high["index"],
            "low_index": swing_low["index"],
            "high_timestamp": swing_high["timestamp"],
            "low_timestamp": swing_low["timestamp"],
            "high_price": float(high_price),
            "low_price": float(low_price),
            "drop_pct": float(drop_pct)
        })

    impulses = sorted(
        impulses,
        key=lambda x: x["low_timestamp"],
        reverse=True
    )

    return impulses


def build_candidate_from_impulse(
    impulse,
    ltf_df,
    entry_zone_low_ratio="0.236",
    entry_zone_high_ratio="0.382",
    invalidation_ratio="0.618",
    tp1_ratio=0.40,
    tp1_close_weight=0.50,
    use_last_closed_candle=True
):

    levels = calculate_bearish_fibonacci_levels(
        impulse_high=impulse["high_price"],
        impulse_low=impulse["low_price"]
    )

    zone_low = levels[
        entry_zone_low_ratio
    ]

    zone_high = levels[
        entry_zone_high_ratio
    ]

    stop_price = levels[
        invalidation_ratio
    ]

    target_price = impulse[
        "low_price"
    ]

    current_price = float(
        ltf_df.iloc[-1]["close"]
    )

    state = classify_alert_state(
        current_price=current_price,
        zone_low=zone_low,
        zone_high=zone_high,
        stop_price=stop_price,
        target_price=target_price
    )

    entry = detect_latest_entry_signal(
        ltf_df=ltf_df,
        zone_low=zone_low,
        zone_high=zone_high,
        use_last_closed_candle=use_last_closed_candle
    )

    entry_signal = (
        entry is not None
        and entry["entry_signal"] is True
        and state["state"] in [
            "FIB_ZONE_ACTIVE",
            "ABOVE_ENTRY_ZONE_BELOW_STOP"
        ]
    )

    if entry_signal:

        entry_price = entry[
            "entry_price"
        ]

        tp1_price = calculate_short_tp1(
            entry_price=entry_price,
            target_price=target_price,
            tp1_ratio=tp1_ratio
        )

    else:

        entry_price = None
        tp1_price = None

    setup_active = state["state"] not in [
        "SCENARIO_INVALIDATED",
        "TARGET_ALREADY_REACHED"
    ]

    distance_to_zone_pct = None

    if current_price < zone_low:

        distance_to_zone_pct = (
            (zone_low - current_price)
            / current_price
        ) * 100

    elif current_price > zone_high:

        distance_to_zone_pct = (
            (current_price - zone_high)
            / current_price
        ) * 100

    else:

        distance_to_zone_pct = 0

    return {
        "setup_active": setup_active,
        "state": (
            "SHORT_ENTRY_SIGNAL"
            if entry_signal
            else state["state"]
        ),
        "bias": state["bias"],
        "current_price": current_price,
        "comment": (
            "Se detecta señal SHORT V5."
            if entry_signal
            else state["comment"]
        ),
        "impulse": impulse,
        "fib_levels": levels,
        "entry_zone_low": float(zone_low),
        "entry_zone_high": float(zone_high),
        "stop_price": float(stop_price),
        "target_price": float(target_price),
        "distance_to_zone_pct": float(distance_to_zone_pct),
        "entry_signal": entry_signal,
        "entry": entry,
        "entry_price": entry_price,
        "tp1_price": tp1_price,
        "tp1_ratio": tp1_ratio,
        "tp1_close_weight": tp1_close_weight
    }


def choose_best_candidate(
    candidates
):

    active_candidates = [
        candidate for candidate in candidates
        if candidate["setup_active"]
    ]

    if len(active_candidates) == 0:
        return None

    entry_signals = [
        candidate for candidate in active_candidates
        if candidate["entry_signal"]
    ]

    if len(entry_signals) > 0:

        return sorted(
            entry_signals,
            key=lambda x: x["impulse"]["low_timestamp"],
            reverse=True
        )[0]

    zone_active = [
        candidate for candidate in active_candidates
        if candidate["state"] == "FIB_ZONE_ACTIVE"
    ]

    if len(zone_active) > 0:

        return sorted(
            zone_active,
            key=lambda x: x["impulse"]["low_timestamp"],
            reverse=True
        )[0]

    return sorted(
        active_candidates,
        key=lambda x: (
            x["distance_to_zone_pct"],
            -x["impulse"]["drop_pct"]
        )
    )[0]


def generate_fib_v5_alert_v2(
    htf_df,
    ltf_df,
    min_drop_pct=5.0,
    max_impulse_bars=80,
    lookback_bars=300,
    max_candidates=5,
    entry_zone_low_ratio="0.236",
    entry_zone_high_ratio="0.382",
    invalidation_ratio="0.618",
    tp1_ratio=0.40,
    tp1_close_weight=0.50,
    left_bars=2,
    right_bars=2,
    use_last_closed_candle=True
):

    impulses = find_bearish_impulses(
        htf_df=htf_df,
        lookback_bars=lookback_bars,
        min_drop_pct=min_drop_pct,
        max_impulse_bars=max_impulse_bars,
        left_bars=left_bars,
        right_bars=right_bars
    )

    if len(impulses) == 0:

        return {
            "setup_active": False,
            "state": "NO_VALID_BEARISH_IMPULSE",
            "bias": "NEUTRAL",
            "comment": "No se detectó impulso bajista 4H válido.",
            "candidates": []
        }

    candidates = []

    for impulse in impulses[:max_candidates]:

        candidate = build_candidate_from_impulse(
            impulse=impulse,
            ltf_df=ltf_df,
            entry_zone_low_ratio=entry_zone_low_ratio,
            entry_zone_high_ratio=entry_zone_high_ratio,
            invalidation_ratio=invalidation_ratio,
            tp1_ratio=tp1_ratio,
            tp1_close_weight=tp1_close_weight,
            use_last_closed_candle=use_last_closed_candle
        )

        candidates.append(
            candidate
        )

    best_candidate = choose_best_candidate(
        candidates
    )

    if best_candidate is None:

        return {
            "setup_active": False,
            "state": "NO_ACTIVE_CANDIDATE",
            "bias": "NEUTRAL",
            "comment": "Hay impulsos bajistas recientes, pero todos están invalidados o ya alcanzaron target.",
            "candidates": candidates
        }

    alert = best_candidate.copy()

    alert["candidates"] = candidates

    return alert
