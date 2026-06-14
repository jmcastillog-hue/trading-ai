import os
import pandas as pd


FILES = {
    "aggressive_v2_train": "reports/mtf_fib_oos_trades_aggressive_v2_train.csv",
    "aggressive_v2_test": "reports/mtf_fib_oos_trades_aggressive_v2_test.csv",
    "base_v1_train": "reports/mtf_fib_oos_trades_base_v1_train.csv",
    "base_v1_test": "reports/mtf_fib_oos_trades_base_v1_test.csv",
    "robust_v2_train": "reports/mtf_fib_oos_trades_robust_v2_train.csv",
    "robust_v2_test": "reports/mtf_fib_oos_trades_robust_v2_test.csv"
}


COST_SCENARIOS = [
    0.00,
    0.05,
    0.10,
    0.20,
    0.30
]


def calculate_performance(
    trades
):

    if len(trades) == 0:

        return {
            "total_trades": 0,
            "wins": 0,
            "losses": 0,
            "win_rate": 0,
            "expectancy": 0,
            "profit_factor": 0,
            "max_drawdown": 0,
            "net_result": 0
        }

    wins = trades[
        trades["net_result_pct"] > 0
    ]

    losses = trades[
        trades["net_result_pct"] <= 0
    ]

    gross_profit = wins["net_result_pct"].sum()

    gross_loss = abs(
        losses["net_result_pct"].sum()
    )

    if gross_loss == 0:

        profit_factor = 0

    else:

        profit_factor = gross_profit / gross_loss

    equity = trades["net_result_pct"].cumsum()

    peak = equity.cummax()

    drawdown = equity - peak

    max_drawdown = drawdown.min()

    return {
        "total_trades": len(trades),
        "wins": len(wins),
        "losses": len(losses),
        "win_rate": len(wins) / len(trades) * 100,
        "expectancy": trades["net_result_pct"].mean(),
        "profit_factor": profit_factor,
        "max_drawdown": max_drawdown,
        "net_result": trades["net_result_pct"].sum()
    }


def analyze_file(
    name,
    path
):

    if not os.path.exists(path):

        print(
            f"Archivo no encontrado: {path}"
        )

        return []

    df = pd.read_csv(path)

    results = []

    for cost in COST_SCENARIOS:

        temp = df.copy()

        temp["net_result_pct"] = (
            temp["result_pct"] - cost
        )

        performance = calculate_performance(
            temp
        )

        performance["config"] = name
        performance["cost_pct"] = cost

        results.append(performance)

    return results


def main():

    all_results = []

    for name, path in FILES.items():

        results = analyze_file(
            name,
            path
        )

        all_results.extend(results)

    results_df = pd.DataFrame(
        all_results
    )

    os.makedirs(
        "reports",
        exist_ok=True
    )

    output_path = "reports/mtf_fib_oos_cost_analysis.csv"

    results_df.to_csv(
        output_path,
        index=False
    )

    print(
        "\n=== OOS COST ANALYSIS ===\n"
    )

    for _, row in results_df.iterrows():

        if not row["config"].endswith("_test"):
            continue

        print(
            f"{row['config']} | costo: {row['cost_pct']:.2f}%"
        )

        print(
            f"trades: {int(row['total_trades'])}"
        )

        print(
            f"win_rate: {row['win_rate']:.2f}"
        )

        print(
            f"expectancy: {row['expectancy']:.2f}"
        )

        print(
            f"profit_factor: {row['profit_factor']:.2f}"
        )

        print(
            f"max_drawdown: {row['max_drawdown']:.2f}"
        )

        print(
            f"net_result: {row['net_result']:.2f}"
        )

        print()

    print(
        f"Reporte guardado en: {output_path}"
    )


if __name__ == "__main__":
    main()