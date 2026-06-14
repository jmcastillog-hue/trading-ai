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


def calculate_short_tp1(
    entry_price,
    target_price,
    tp1_ratio=0.40
):

    distance = entry_price - target_price

    return entry_price - (
        distance * tp1_ratio
    )


def is_bearish_candle(
    candle
):

    return candle["close"] < candle["open"]


def candle_touches_zone(
    candle,
    zone_low,
    zone_high
):

    return (
        candle["high"] >= zone_low
        and candle["low"] <= zone_high
    )


def find_latest_bearish_impulse(
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

    valid_impulses = []

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

        valid_impulses.append({
            "high_index": swing_high["index"],
            "low_index": swing_low["index"],
            "high_timestamp": swing_high["timestamp"],
            "low_timestamp": swing_low["timestamp"],
            "high_price": float(high_price),
            "low_price": float(low_price),
            "drop_pct": float(drop_pct)
        })

    if len(valid_impulses) == 0:
        return None

    latest_impulse = sorted(
        valid_impulses,
        key=lambda x: x["low_timestamp"],
        reverse=True
    )[0]

    return latest_impulse


def classify_alert_state(
    current_price,
    zone_low,
    zone_high,
    stop_price,
    target_price,
    near_zone_threshold_pct=0.20
):

    if current_price <= target_price:

        return {
            "state": "TARGET_ALREADY_REACHED",
            "bias": "NEUTRAL",
            "comment": "El precio ya alcanzó o perforó el target del impulso. No buscar nuevo short en este setup."
        }

    if current_price < zone_low:

        distance_to_zone_pct = (
            (zone_low - current_price)
            / current_price
        ) * 100

        if distance_to_zone_pct <= near_zone_threshold_pct:

            return {
                "state": "NEAR_ENTRY_ZONE",
                "bias": "BEARISH",
                "comment": "El precio está muy cerca de la zona Fibonacci. Vigilar cierre de vela bajista 30m dentro de la zona."
            }

        return {
            "state": "WAIT_FOR_RETRACE",
            "bias": "BEARISH",
            "comment": "El precio está por debajo de la zona Fibonacci. Esperar rebote hacia zona de entrada."
        }

    if (
        current_price >= zone_low
        and current_price <= zone_high
    ):

        return {
            "state": "FIB_ZONE_ACTIVE",
            "bias": "BEARISH",
            "comment": "El precio está dentro de la zona Fibonacci 0.236–0.382. Buscar vela bajista 30m."
        }

    if (
        current_price > zone_high
        and current_price <= stop_price
    ):

        return {
            "state": "ABOVE_ENTRY_ZONE_BELOW_STOP",
            "bias": "BEARISH_CAUTION",
            "comment": "El precio superó la zona óptima, pero aún no invalidó el setup."
        }

    return {
        "state": "SCENARIO_INVALIDATED",
        "bias": "NEUTRAL",
        "comment": "El precio superó la invalidación 0.618. No buscar short bajo este setup."
    }

    if current_price <= target_price:

        return {
            "state": "TARGET_ALREADY_REACHED",
            "bias": "NEUTRAL",
            "comment": "El precio ya alcanzó o perforó el target del impulso. No buscar nuevo short en este setup."
        }

    if current_price < zone_low:

        return {
            "state": "WAIT_FOR_RETRACE",
            "bias": "BEARISH",
            "comment": "El precio está por debajo de la zona Fibonacci. Esperar rebote hacia zona de entrada."
        }

    if (
        current_price >= zone_low
        and current_price <= zone_high
    ):

        return {
            "state": "FIB_ZONE_ACTIVE",
            "bias": "BEARISH",
            "comment": "El precio está dentro de la zona Fibonacci 0.236–0.382. Buscar vela bajista 30m."
        }

    if (
        current_price > zone_high
        and current_price <= stop_price
    ):

        return {
            "state": "ABOVE_ENTRY_ZONE_BELOW_STOP",
            "bias": "BEARISH_CAUTION",
            "comment": "El precio superó la zona óptima, pero aún no invalidó el setup."
        }

    return {
        "state": "SCENARIO_INVALIDATED",
        "bias": "NEUTRAL",
        "comment": "El precio superó la invalidación 0.618. No buscar short bajo este setup."
    }


def detect_latest_entry_signal(
    ltf_df,
    zone_low,
    zone_high,
    use_last_closed_candle=True
):

    if len(ltf_df) < 2:
        return None

    if use_last_closed_candle:

        candle = ltf_df.iloc[-2]

    else:

        candle = ltf_df.iloc[-1]

    touched_zone = candle_touches_zone(
        candle,
        zone_low,
        zone_high
    )

    bearish = is_bearish_candle(
        candle
    )

    if touched_zone and bearish:

        return {
            "entry_signal": True,
            "entry_time": candle["timestamp"],
            "entry_price": float(candle["close"]),
            "candle_open": float(candle["open"]),
            "candle_high": float(candle["high"]),
            "candle_low": float(candle["low"]),
            "candle_close": float(candle["close"]),
            "comment": "Entrada SHORT detectada: vela bajista 30m dentro de zona Fibonacci."
        }

    return {
        "entry_signal": False,
        "entry_time": candle["timestamp"],
        "entry_price": float(candle["close"]),
        "candle_open": float(candle["open"]),
        "candle_high": float(candle["high"]),
        "candle_low": float(candle["low"]),
        "candle_close": float(candle["close"]),
        "comment": "Aún no hay vela bajista 30m válida dentro de la zona."
    }


def generate_fib_v5_alert(
    htf_df,
    ltf_df,
    min_drop_pct=5.0,
    max_impulse_bars=80,
    lookback_bars=300,
    entry_zone_low_ratio="0.236",
    entry_zone_high_ratio="0.382",
    invalidation_ratio="0.618",
    tp1_ratio=0.40,
    tp1_close_weight=0.50,
    left_bars=2,
    right_bars=2,
    use_last_closed_candle=True
):

    impulse = find_latest_bearish_impulse(
        htf_df=htf_df,
        lookback_bars=lookback_bars,
        min_drop_pct=min_drop_pct,
        max_impulse_bars=max_impulse_bars,
        left_bars=left_bars,
        right_bars=right_bars
    )

    if impulse is None:

        return {
            "setup_active": False,
            "state": "NO_VALID_BEARISH_IMPULSE",
            "bias": "NEUTRAL",
            "comment": "No se detectó impulso bajista 4H válido."
        }

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

        final_state = "SHORT_ENTRY_SIGNAL"

        final_comment = (
            "Se detecta señal SHORT V5: impulso bajista 4H, "
            "precio en zona Fibonacci y vela bajista 30m confirmada."
        )

    else:

        entry_price = None
        tp1_price = None
        final_state = state["state"]
        final_comment = state["comment"]

    return {
        "setup_active": state["state"] not in [
            "NO_VALID_BEARISH_IMPULSE",
            "SCENARIO_INVALIDATED",
            "TARGET_ALREADY_REACHED"
        ],
        "state": final_state,
        "bias": state["bias"],
        "current_price": current_price,
        "comment": final_comment,
        "impulse": impulse,
        "fib_levels": levels,
        "entry_zone_low": float(zone_low),
        "entry_zone_high": float(zone_high),
        "stop_price": float(stop_price),
        "target_price": float(target_price),
        "entry_signal": entry_signal,
        "entry": entry,
        "entry_price": entry_price,
        "tp1_price": tp1_price,
        "tp1_ratio": tp1_ratio,
        "tp1_close_weight": tp1_close_weight,
        "management_plan": {
            "entry": "SHORT en cierre de vela bajista 30m dentro de zona Fibonacci 0.236–0.382.",
            "stop": "Stop en Fibonacci 0.618.",
            "tp1": "TP1 al 40% del camino hacia el target.",
            "tp1_action": "Cerrar 50% de la posición.",
            "after_tp1": "Mover el resto a breakeven.",
            "tp2": "Target final en mínimo del impulso 4H."
        }
    }