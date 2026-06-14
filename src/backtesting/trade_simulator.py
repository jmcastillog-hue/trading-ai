def simulate_trade_with_atr(
    df,
    entry_index,
    direction,
    atr_value,
    sl_multiplier=1,
    tp_multiplier=2,
    max_bars=8
):

    entry_price = df.iloc[entry_index]["close"]

    if direction == "LONG":
        stop_loss = entry_price - (atr_value * sl_multiplier)
        take_profit = entry_price + (atr_value * tp_multiplier)

    elif direction == "SHORT":
        stop_loss = entry_price + (atr_value * sl_multiplier)
        take_profit = entry_price - (atr_value * tp_multiplier)

    else:
        return None

    for i in range(
        entry_index + 1,
        min(entry_index + max_bars + 1, len(df))
    ):

        high = df.iloc[i]["high"]
        low = df.iloc[i]["low"]

        if direction == "LONG":

            if low <= stop_loss:
                return {
                    "result": "LOSS",
                    "result_pct": -sl_multiplier,
                    "exit_reason": "STOP_LOSS"
                }

            if high >= take_profit:
                return {
                    "result": "WIN",
                    "result_pct": tp_multiplier,
                    "exit_reason": "TAKE_PROFIT"
                }

        if direction == "SHORT":

            if high >= stop_loss:
                return {
                    "result": "LOSS",
                    "result_pct": -sl_multiplier,
                    "exit_reason": "STOP_LOSS"
                }

            if low <= take_profit:
                return {
                    "result": "WIN",
                    "result_pct": tp_multiplier,
                    "exit_reason": "TAKE_PROFIT"
                }

    return {
        "result": "TIME_EXIT",
        "result_pct": 0,
        "exit_reason": "MAX_BARS"
    }