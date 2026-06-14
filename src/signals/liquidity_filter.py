def evaluate_liquidity_filter(
    signal_report,
    liquidity_report_v2,
    max_distance_pct=1.0
):

    signal = signal_report["signal"]

    current_price = liquidity_report_v2["base"]["current_price"]

    buy_side = liquidity_report_v2["buy_side_liquidity"]

    sell_side = liquidity_report_v2["sell_side_liquidity"]

    if buy_side is None or sell_side is None:
        return {
            "liquidity_filter": "NO_DATA",
            "adjusted_signal": signal,
            "comment": "No hay suficientes clusters de liquidez."
        }

    distance_to_buy_side = (
        (buy_side - current_price)
        / current_price
    ) * 100

    distance_to_sell_side = (
        (current_price - sell_side)
        / current_price
    ) * 100

    if signal == "LONG":

        if distance_to_buy_side <= max_distance_pct:
            return {
                "liquidity_filter": "WARNING",
                "adjusted_signal": "WAIT",
                "comment": "Long bloqueado: precio cerca de buy-side liquidity."
            }

        return {
            "liquidity_filter": "PASS",
            "adjusted_signal": "LONG",
            "comment": "Long permitido: espacio suficiente hacia buy-side liquidity."
        }

    if signal == "SHORT":

        if distance_to_sell_side <= max_distance_pct:
            return {
                "liquidity_filter": "WARNING",
                "adjusted_signal": "WAIT",
                "comment": "Short bloqueado: precio cerca de sell-side liquidity."
            }

        return {
            "liquidity_filter": "PASS",
            "adjusted_signal": "SHORT",
            "comment": "Short permitido: espacio suficiente hacia sell-side liquidity."
        }

    return {
        "liquidity_filter": "NEUTRAL",
        "adjusted_signal": "WAIT",
        "comment": "Sin señal direccional activa."
    }