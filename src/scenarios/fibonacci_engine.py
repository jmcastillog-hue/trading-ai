def calculate_bearish_fibonacci_levels(
    impulse_high,
    impulse_low
):

    price_range = impulse_high - impulse_low

    levels = {
        "0.236": impulse_low + (price_range * 0.236),
        "0.382": impulse_low + (price_range * 0.382),
        "0.500": impulse_low + (price_range * 0.500),
        "0.618": impulse_low + (price_range * 0.618),
        "0.786": impulse_low + (price_range * 0.786),
        "1.000": impulse_high
    }

    return levels


def find_recent_bearish_impulse(
    df,
    lookback=300,
    min_drop_pct=5
):

    recent_df = df.tail(lookback).copy()

    best_impulse = None
    best_drop = 0

    for i in range(len(recent_df) - 2):

        high_price = recent_df.iloc[i]["high"]

        for j in range(i + 1, len(recent_df)):

            low_price = recent_df.iloc[j]["low"]

            drop_pct = (
                (high_price - low_price)
                / high_price
            ) * 100

            if drop_pct > best_drop:

                best_drop = drop_pct

                best_impulse = {
                    "high_index": int(recent_df.index[i]),
                    "low_index": int(recent_df.index[j]),
                    "high_price": float(high_price),
                    "low_price": float(low_price),
                    "drop_pct": float(drop_pct),
                    "high_timestamp": recent_df.iloc[i]["timestamp"],
                    "low_timestamp": recent_df.iloc[j]["timestamp"]
                }

    if best_impulse is None:
        return None

    if best_impulse["drop_pct"] < min_drop_pct:
        return None

    return best_impulse


def build_short_fib_zone(
    impulse,
    zone_low_ratio="0.236",
    zone_high_ratio="0.382",
    invalidation_ratio="0.618"
):

    levels = calculate_bearish_fibonacci_levels(
        impulse_high=impulse["high_price"],
        impulse_low=impulse["low_price"]
    )

    zone_low = levels[zone_low_ratio]
    zone_high = levels[zone_high_ratio]
    invalidation = levels[invalidation_ratio]

    return {
        "impulse": impulse,
        "levels": levels,
        "short_zone_low": float(zone_low),
        "short_zone_high": float(zone_high),
        "target_price": float(impulse["low_price"]),
        "invalidation_price": float(invalidation)
    }