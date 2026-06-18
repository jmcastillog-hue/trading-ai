from __future__ import annotations

from typing import Any


def detect_swing_lows(
    df,
    index: int,
    lookback_bars: int = 144,
    left_bars: int = 2,
    right_bars: int = 2,
) -> list[dict[str, Any]]:
    """
    Detecta swing lows usando solo información anterior al índice actual.

    Un swing low es una vela cuyo low es menor o igual que los lows
    de N velas a la izquierda y N velas a la derecha.

    Importante:
    Para evitar lookahead bias, solo se consideran swing lows ya confirmados
    antes del índice actual.
    """

    if index <= left_bars + right_bars:
        return []

    start = max(0, index - lookback_bars)
    end = index - right_bars

    swing_lows = []

    for i in range(start + left_bars, end):
        center_low = float(df.iloc[i]["low"])

        left_window = df.iloc[i - left_bars : i]["low"]
        right_window = df.iloc[i + 1 : i + 1 + right_bars]["low"]

        if len(left_window) < left_bars or len(right_window) < right_bars:
            continue

        if center_low <= float(left_window.min()) and center_low <= float(right_window.min()):
            swing_lows.append(
                {
                    "swing_index": i,
                    "level": center_low,
                    "atr": float(df.iloc[i].get("atr", 0)),
                }
            )

    return swing_lows


def build_sell_side_liquidity_zones(
    df,
    index: int,
    lookback_bars: int = 144,
    left_bars: int = 2,
    right_bars: int = 2,
    equal_low_tolerance_atr: float = 0.25,
) -> list[dict[str, Any]]:
    """
    Construye zonas de sell-side liquidity a partir de swing lows.

    Agrupa swing lows cercanos entre sí usando una tolerancia basada en ATR.
    Cada grupo representa una zona potencial de liquidez.

    La zona más relevante para un SHORT suele ser la más cercana bajo el precio.
    """

    row = df.iloc[index]
    current_price = float(row["close"])
    current_atr = float(row.get("atr", 0))

    if current_atr <= 0:
        return []

    swing_lows = detect_swing_lows(
        df=df,
        index=index,
        lookback_bars=lookback_bars,
        left_bars=left_bars,
        right_bars=right_bars,
    )

    swing_lows = [
        swing for swing in swing_lows
        if float(swing["level"]) < current_price
    ]

    if not swing_lows:
        return []

    tolerance = current_atr * equal_low_tolerance_atr

    zones = []
    used_indexes = set()

    sorted_swings = sorted(
        swing_lows,
        key=lambda item: float(item["level"]),
        reverse=True,
    )

    for swing in sorted_swings:
        swing_index = int(swing["swing_index"])

        if swing_index in used_indexes:
            continue

        level = float(swing["level"])

        cluster = [
            other for other in sorted_swings
            if abs(float(other["level"]) - level) <= tolerance
        ]

        for item in cluster:
            used_indexes.add(int(item["swing_index"]))

        cluster_levels = [float(item["level"]) for item in cluster]
        cluster_indexes = [int(item["swing_index"]) for item in cluster]

        zone_level = sum(cluster_levels) / len(cluster_levels)

        zones.append(
            {
                "zone_level": zone_level,
                "nearest_level": max(cluster_levels),
                "lowest_level": min(cluster_levels),
                "touches": len(cluster),
                "first_touch_index": min(cluster_indexes),
                "last_touch_index": max(cluster_indexes),
                "distance_to_zone": current_price - zone_level,
            }
        )

    zones = sorted(
        zones,
        key=lambda item: float(item["zone_level"]),
        reverse=True,
    )

    return zones


def get_nearest_sell_side_liquidity_zone(
    df,
    index: int,
    lookback_bars: int = 144,
    left_bars: int = 2,
    right_bars: int = 2,
    equal_low_tolerance_atr: float = 0.25,
    min_touches: int = 1,
) -> dict[str, Any] | None:
    """
    Devuelve la zona de liquidez bajista más cercana bajo el precio actual.

    min_touches:
    - 1 permite swing lows individuales.
    - 2 o más exige equal lows / zona con varios toques.
    """

    zones = build_sell_side_liquidity_zones(
        df=df,
        index=index,
        lookback_bars=lookback_bars,
        left_bars=left_bars,
        right_bars=right_bars,
        equal_low_tolerance_atr=equal_low_tolerance_atr,
    )

    valid_zones = [
        zone for zone in zones
        if int(zone["touches"]) >= min_touches
    ]

    if not valid_zones:
        return None

    return valid_zones[0]


def short_allowed_by_liquidity_zone_v2(
    df,
    index: int,
    min_atr_distance: float = 1.5,
    lookback_bars: int = 144,
    left_bars: int = 2,
    right_bars: int = 2,
    equal_low_tolerance_atr: float = 0.25,
    min_touches: int = 1,
) -> bool:
    """
    Permite SHORT solo si existe una zona de liquidez bajista cercana
    y con suficiente espacio desde el precio actual.

    Regla:
    current_price - nearest_sell_side_liquidity >= ATR * min_atr_distance
    """

    row = df.iloc[index]

    current_price = float(row["close"])
    atr = float(row.get("atr", 0))

    if atr <= 0:
        return False

    zone = get_nearest_sell_side_liquidity_zone(
        df=df,
        index=index,
        lookback_bars=lookback_bars,
        left_bars=left_bars,
        right_bars=right_bars,
        equal_low_tolerance_atr=equal_low_tolerance_atr,
        min_touches=min_touches,
    )

    if zone is None:
        return False

    zone_level = float(zone["zone_level"])

    if zone_level >= current_price:
        return False

    distance_to_zone = current_price - zone_level
    required_distance = atr * min_atr_distance

    return distance_to_zone >= required_distance


def get_liquidity_context_v2(
    df,
    index: int,
    min_atr_distance: float = 1.5,
    lookback_bars: int = 144,
    left_bars: int = 2,
    right_bars: int = 2,
    equal_low_tolerance_atr: float = 0.25,
    min_touches: int = 1,
) -> dict[str, Any]:
    row = df.iloc[index]

    current_price = float(row["close"])
    atr = float(row.get("atr", 0))

    zone = get_nearest_sell_side_liquidity_zone(
        df=df,
        index=index,
        lookback_bars=lookback_bars,
        left_bars=left_bars,
        right_bars=right_bars,
        equal_low_tolerance_atr=equal_low_tolerance_atr,
        min_touches=min_touches,
    )

    if zone is None or atr <= 0:
        return {
            "liquidity_v2_zone_level": None,
            "liquidity_v2_touches": 0,
            "liquidity_v2_distance": None,
            "liquidity_v2_required_distance": None,
            "liquidity_v2_space_ok": False,
        }

    zone_level = float(zone["zone_level"])
    distance_to_zone = current_price - zone_level
    required_distance = atr * min_atr_distance

    space_ok = (
        zone_level < current_price
        and distance_to_zone >= required_distance
    )

    return {
        "liquidity_v2_zone_level": zone_level,
        "liquidity_v2_touches": int(zone["touches"]),
        "liquidity_v2_distance": distance_to_zone,
        "liquidity_v2_required_distance": required_distance,
        "liquidity_v2_space_ok": space_ok,
    }