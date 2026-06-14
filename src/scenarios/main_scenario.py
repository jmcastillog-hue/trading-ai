import os
import sys

sys.path.append(
    os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            "..",
            ".."
        )
    )
)

from src.scenarios.fibonacci_engine import (
    find_recent_bearish_impulse,
    build_short_fib_zone
)

from src.quantitative.data_loader import (
    load_csv,
    validate_data,
    clean_data
)

from src.scenarios.scenario_engine import (
    analyze_short_zone_scenario
)


def main():

    df = load_csv(
        "data/btcusdt_4h.csv"
    )

    validate_data(df)

    df = clean_data(df)

    current_price = float(
        df.iloc[-1]["close"]
        )

    impulse = find_recent_bearish_impulse(
        df,
        lookback=300,
        min_drop_pct=5
    )

    if impulse is None:

        print(
            "No se detectó impulso bajista relevante."
        )

        return

    fib_zone = build_short_fib_zone(
        impulse,
        zone_low_ratio="0.236",
        zone_high_ratio="0.382",
        invalidation_ratio="0.618"
    )

    scenario = analyze_short_zone_scenario(
        current_price=current_price,
        short_zone_low=fib_zone["short_zone_low"],
        short_zone_high=fib_zone["short_zone_high"],
        target_price=fib_zone["target_price"],
        invalidation_price=fib_zone["invalidation_price"]
    )

    print("\n=== FIBONACCI ENGINE V1 ===\n")

    print(
        f"Impulse high: {impulse['high_price']:.2f}"
    )

    print(
        f"Impulse low: {impulse['low_price']:.2f}"
    )

    print(
        f"Drop pct: {impulse['drop_pct']:.2f}%"
    )

    print("\nFibonacci Levels:")

    for key, value in fib_zone["levels"].items():

        print(
            f"{key}: {value:.2f}"
        )
    print("\n=== SCENARIO ENGINE V1 ===\n")

    for key, value in scenario.items():

        if isinstance(value, float):

            print(
                f"{key}: {value:.2f}"
            )

        else:

            print(
                f"{key}: {value}"
            )


if __name__ == "__main__":
    main()