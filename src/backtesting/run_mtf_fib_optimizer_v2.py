import os
import sys
import pandas as pd

sys.path.append(
    os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            "..",
            ".."
        )
    )
)

from src.quantitative.data_loader import (
    load_csv,
    validate_data,
    clean_data
)

from src.backtesting.mtf_fib_optimizer_v2 import (
    optimize_mtf_fib_short_strategy_v2
)


def load_market_data(path):

    df = load_csv(path)

    validate_data(df)

    df = clean_data(df)

    return df


def main():

    htf_df = load_market_data(
        "data/btcusdt_4h_history.csv"
    )

    ltf_df = load_market_data(
        "data/btcusdt_30m_history.csv"
    )

    results = optimize_mtf_fib_short_strategy_v2(
        htf_df,
        ltf_df,
        min_trades=20
    )

    df_results = pd.DataFrame(results)

    df_results.to_csv(
        "reports/mtf_fib_optimizer_v2_results.csv",
        index=False
    )

    print("\n=== MTF FIB OPTIMIZER V2 ===\n")

    print(
        "Resultados guardados en: reports/mtf_fib_optimizer_v2_results.csv\n"
    )

    print("Top 10 configuraciones:\n")

    for i, result in enumerate(
        results[:10],
        start=1
    ):

        print(f"--- Resultado #{i} ---")

        for key, value in result.items():

            if isinstance(value, float):

                print(
                    f"{key}: {value:.2f}"
                )

            else:

                print(
                    f"{key}: {value}"
                )

        print()


if __name__ == "__main__":
    main()