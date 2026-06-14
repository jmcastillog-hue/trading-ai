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

from structure.market_structure import (
    generate_market_structure_report
)

from backtesting.trade_simulator import (
    simulate_trade_with_atr
)

from backtesting.strategy_tester import (
    prepare_indicator_columns
)

from backtesting.performance_metrics import (
    generate_performance_report
)


def get_sweep_bos_direction(setup):

    if setup == "LONG_SWEEP_BOS":
        return "LONG"

    if setup == "SHORT_SWEEP_BOS":
        return "SHORT"

    return "WAIT"


def run_sweep_bos_backtest(
    df,
    sl_multiplier=1,
    tp_multiplier=2,
    max_bars=8,
    structure_lookback=120,
    left_bars=2,
    right_bars=2
):

    df = prepare_indicator_columns(df)

    trades = []

    for i in range(
        structure_lookback,
        len(df) - max_bars
    ):

        partial_df = df.iloc[
            i - structure_lookback:i + 1
        ].copy()

        structure_report = generate_market_structure_report(
            partial_df,
            left_bars=left_bars,
            right_bars=right_bars
        )

        sweep_bos = structure_report[
            "sweep_bos_signal"
        ]

        direction = get_sweep_bos_direction(
            sweep_bos["setup"]
        )

        if direction == "WAIT":
            continue

        row = df.iloc[i]

        result = simulate_trade_with_atr(
            df=df,
            entry_index=i,
            direction=direction,
            atr_value=row["atr"],
            sl_multiplier=sl_multiplier,
            tp_multiplier=tp_multiplier,
            max_bars=max_bars
        )

        if result is None:
            continue

        trades.append({
            "timestamp": row["timestamp"],
            "direction": direction,
            "setup": sweep_bos["setup"],
            "bias": sweep_bos["bias"],
            "comment": sweep_bos["comment"],
            "result": result["result"],
            "exit_reason": result["exit_reason"],
            "result_pct": result["result_pct"]
        })

    performance = generate_performance_report(
        trades
    )

    return {
        "trades": trades,
        "performance": performance
    }