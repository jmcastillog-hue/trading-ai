def analyze_short_zone_scenario(
    current_price,
    short_zone_low=64000,
    short_zone_high=67000,
    target_price=55000,
    invalidation_price=68200
):

    if current_price < short_zone_low:

        distance_to_zone = (
            (short_zone_low - current_price)
            / current_price
        ) * 100

        return {
            "scenario": "WAIT_FOR_RETRACE",
            "bias": "BEARISH",
            "current_price": current_price,
            "short_zone_low": short_zone_low,
            "short_zone_high": short_zone_high,
            "target_price": target_price,
            "invalidation_price": invalidation_price,
            "distance_to_zone_pct": distance_to_zone,
            "comment": "El precio aún está por debajo de la zona ideal de corto. Esperar rebote."
        }

    if (
        current_price >= short_zone_low
        and current_price <= short_zone_high
    ):

        potential_reward = (
            (current_price - target_price)
            / current_price
        ) * 100

        potential_risk = (
            (invalidation_price - current_price)
            / current_price
        ) * 100

        rr = (
            potential_reward / potential_risk
            if potential_risk > 0
            else 0
        )

        return {
            "scenario": "SHORT_ZONE_ACTIVE",
            "bias": "BEARISH",
            "current_price": current_price,
            "short_zone_low": short_zone_low,
            "short_zone_high": short_zone_high,
            "target_price": target_price,
            "invalidation_price": invalidation_price,
            "potential_reward_pct": potential_reward,
            "potential_risk_pct": potential_risk,
            "risk_reward": rr,
            "comment": "El precio está dentro de la zona ideal. Buscar confirmación bajista."
        }

    if (
        current_price > short_zone_high
        and current_price <= invalidation_price
    ):

        return {
            "scenario": "HIGH_RISK_SHORT_ZONE",
            "bias": "BEARISH_CAUTION",
            "current_price": current_price,
            "short_zone_low": short_zone_low,
            "short_zone_high": short_zone_high,
            "target_price": target_price,
            "invalidation_price": invalidation_price,
            "comment": "El precio superó la zona ideal, pero aún no invalidó el escenario."
        }

    return {
        "scenario": "SCENARIO_INVALIDATED",
        "bias": "NEUTRAL",
        "current_price": current_price,
        "short_zone_low": short_zone_low,
        "short_zone_high": short_zone_high,
        "target_price": target_price,
        "invalidation_price": invalidation_price,
        "comment": "El precio superó la invalidación. No buscar corto bajo esta hipótesis."
    }