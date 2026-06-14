import pandas as pd
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


def optimize_mtf_fib_short_strategy(
    htf_df,
    ltf_df,
    min_trades=10
):

    entry_zones = [
        ("0.236", "0.382"),
        ("0.382", "0.500"),
        ("0.500", "0.618")
    ]

    invalidation_levels = [
        "0.618",
        "0.786"
    ]

    min_drop_values = [
        4,
        5,
        7
    ]

    max_impulse_values = [
        80,
        120
    ]

    max_wait_values = [
        80,
        120
    ]

    max_trade_values = [
        120,
        240
    ]

    level_order = {
        "0.236": 1,
        "0.382": 2,
        "0.500": 3,
        "0.618": 4,
        "0.786": 5,
        "1.000": 6
    }

    raw_combinations = list(
        itertools.product(
            entry_zones,
            invalidation_levels,
            min_drop_values,
            max_impulse_values,
            max_wait_values,
            max_trade_values
        )
    )

    combinations = []

    for combo in raw_combinations:

        entry_zone = combo[0]
        invalidation = combo[1]

        zone_low, zone_high = entry_zone

        if (
            level_order[invalidation]
            > level_order[zone_high]
        ):
            combinations.append(combo)

    total_combinations = len(combinations)

    print(
        f"\nCombinaciones válidas a probar: {total_combinations}\n"
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
            f"[{index}/{total_combinations}] "
            f"zona={zone_low}-{zone_high} | "
            f"invalidación={invalidation} | "
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

        df_results = pd.DataFrame(results)

        df_results.to_csv(
            "reports/mtf_fib_optimizer_results.csv",
        index=False
        )

        print(
            "\nResultados guardados en: reports/mtf_fib_optimizer_results.csv\n"
        )

        performance = report["performance"]

        if performance["total_trades"] < min_trades:
            continue

        result = {
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
        }

        results.append(result)

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