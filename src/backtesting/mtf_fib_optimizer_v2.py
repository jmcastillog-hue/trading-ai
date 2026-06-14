import os
import sys
import itertools

sys.path.append(
    os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            ".."
        )
    )
)

from backtesting.mtf_fib_backtester import (
    run_mtf_fib_short_backtest
)


def optimize_mtf_fib_short_strategy_v2(
    htf_df,
    ltf_df,
    min_trades=20
):

    entry_zones = [
        ("0.236", "0.382")
    ]

    invalidation_levels = [
        "0.618"
    ]

    min_drop_values = [
        4.5,
        5,
        5.5,
        6
    ]

    max_impulse_values = [
        60,
        80,
        100
    ]

    max_wait_values = [
        60,
        80,
        100
    ]

    max_trade_values = [
        80,
        120,
        160
    ]

    combinations = list(
        itertools.product(
            entry_zones,
            invalidation_levels,
            min_drop_values,
            max_impulse_values,
            max_wait_values,
            max_trade_values
        )
    )

    print(
        f"\nCombinaciones V2 a probar: {len(combinations)}\n"
    )

    results = []

    for index, (
        entry_zone,
        invalidation,
        min_drop,
        max_impulse,
        max_wait,
        max_trade
    ) in enumerate(combinations, start=1):

        zone_low, zone_high = entry_zone

        print(
            f"[{index}/{len(combinations)}] "
            f"drop={min_drop}% | "
            f"impulse={max_impulse} | "
            f"wait={max_wait} | "
            f"trade={max_trade}",
            flush=True
        )

        report = run_mtf_fib_short_backtest(
            htf_df=htf_df,
            ltf_df=ltf_df,
            min_drop_pct=min_drop,
            max_impulse_bars=max_impulse,
            max_wait_bars=max_wait,
            max_trade_bars=max_trade,
            entry_zone_low_ratio=zone_low,
            entry_zone_high_ratio=zone_high,
            invalidation_ratio=invalidation,
            left_bars=2,
            right_bars=2
        )

        performance = report["performance"]

        if performance["total_trades"] < min_trades:
            continue

        results.append({
            "zone": f"{zone_low}-{zone_high}",
            "invalidation": invalidation,
            "min_drop_pct": min_drop,
            "max_impulse_bars": max_impulse,
            "max_wait_bars": max_wait,
            "max_trade_bars": max_trade,
            "total_trades": performance["total_trades"],
            "win_rate": performance["win_rate"],
            "expectancy": performance["expectancy"],
            "profit_factor": performance["profit_factor"],
            "max_drawdown": performance["max_drawdown"]
        })

    results = sorted(
        results,
        key=lambda x: (
            x["profit_factor"],
            x["expectancy"],
            x["win_rate"]
        ),
        reverse=True
    )

    return results