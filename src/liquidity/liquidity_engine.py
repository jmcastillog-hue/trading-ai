from liquidity.equal_highs import (
    find_equal_highs
)

from liquidity.equal_lows import (
    find_equal_lows
)
def calculate_liquidity_zones(
    df,
    lookback=96
):


    recent_data = df.tail(lookback)

    liquidity_high = recent_data["high"].max()
    liquidity_low = recent_data["low"].min()
    current_price = df.iloc[-1]["close"]

    range_size = liquidity_high - liquidity_low

    if range_size == 0:
        position = 0.5
    else:
        position = (
            (current_price - liquidity_low)
            / range_size
        )

    distance_to_high_pct = (
        (liquidity_high - current_price)
        / current_price
    ) * 100

    distance_to_low_pct = (
        (current_price - liquidity_low)
        / current_price
    ) * 100

    return {
        "liquidity_high": float(liquidity_high),
        "liquidity_low": float(liquidity_low),
        "current_price": float(current_price),
        "position_in_range": float(position),
        "distance_to_high_pct": float(distance_to_high_pct),
        "distance_to_low_pct": float(distance_to_low_pct)
    }


def classify_liquidity_context(liquidity_report):

    position = liquidity_report["position_in_range"]

    if position >= 0.80:
        return "NEAR_BUY_SIDE_LIQUIDITY"

    if position <= 0.20:
        return "NEAR_SELL_SIDE_LIQUIDITY"

    return "MID_RANGE"

def generate_liquidity_report_v2(
    df,
    lookback=96,
    tolerance_pct=0.15,
    min_touches=2
):

    base_report = calculate_liquidity_zones(
        df,
        lookback=lookback
    )

    liquidity_context = classify_liquidity_context(
        base_report
    )

    equal_highs = find_equal_highs(
        df,
        lookback=lookback,
        tolerance_pct=tolerance_pct,
        min_touches=min_touches
    )

    equal_lows = find_equal_lows(
        df,
        lookback=lookback,
        tolerance_pct=tolerance_pct,
        min_touches=min_touches
    )

    buy_side_liquidity = (
        equal_highs[0]["level"]
        if len(equal_highs) > 0
        else None
    )

    sell_side_liquidity = (
        equal_lows[0]["level"]
        if len(equal_lows) > 0
        else None
    )

    return {
        "base": base_report,
        "context": liquidity_context,
        "equal_highs": equal_highs[:5],
        "equal_lows": equal_lows[:5],
        "buy_side_liquidity": buy_side_liquidity,
        "sell_side_liquidity": sell_side_liquidity
    }