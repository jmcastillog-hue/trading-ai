import os
import sys
import json

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

from src.paper_trading.paper_trade_logger import (
    load_paper_trades,
    update_open_trades,
    save_paper_trades,
    PAPER_TRADES_FILE,
    OPEN_STATUSES,
    short_result_pct,
    safe_float
)


ALERT_JSON = "reports/fib_v5_live_alert_report.json"


def load_current_price():

    if not os.path.exists(
        ALERT_JSON
    ):

        return None

    with open(
        ALERT_JSON,
        "r",
        encoding="utf-8"
    ) as file:

        alert = json.load(
            file
        )

    return safe_float(
        alert.get("current_price")
    )

def distance_down_pct(
    current_price,
    target_price
):

    if current_price <= 0:
        return 0

    return (
        (current_price - target_price)
        / current_price
    ) * 100

def distance_up_pct(
    current_price,
    level_price
):

    if current_price <= 0:
        return 0

    return (
        (level_price - current_price)
        / current_price
    ) * 100


def print_trade_status(
    row,
    current_price
):

    entry_price = safe_float(
        row.get("entry_price")
    )

    stop_price = safe_float(
        row.get("stop_price")
    )

    tp1_price = safe_float(
        row.get("tp1_price")
    )

    tp2_price = safe_float(
        row.get("tp2_price")
    )

    floating_result_pct = short_result_pct(
        entry_price=entry_price,
        exit_price=current_price
    )

    distance_down_to_tp1 = distance_down_pct(
        current_price=current_price,
        target_price=tp1_price
    )

    distance_down_to_tp2 = distance_down_pct(
        current_price=current_price,
        target_price=tp2_price
    )

    distance_up_to_stop = distance_up_pct(
        current_price=current_price,
        level_price=stop_price
    )

    print(
        "\n--- PAPER TRADE ABIERTO ---\n"
    )

    print(
        f"trade_id: {row.get('trade_id')}"
    )

    print(
        f"symbol: {row.get('symbol')}"
    )

    print(
        f"strategy: {row.get('strategy')}"
    )

    print(
        f"direction: {row.get('direction')}"
    )

    print(
        f"status: {row.get('status')}"
    )

    print(
        f"entry_time: {row.get('entry_time')}"
    )

    print(
        f"entry_price: {entry_price:.2f}"
    )

    print(
        f"current_price: {current_price:.2f}"
    )

    print(
        f"floating_result_pct: {floating_result_pct:.2f}%"
    )

    print(
        ""
    )

    print(
        f"tp1_price: {tp1_price:.2f}"
    )

    print(
        f"tp2_price: {tp2_price:.2f}"
    )

    print(
        f"stop_price: {stop_price:.2f}"
    )

    print(
        ""
    )

    print(
        f"distance_down_to_tp1_pct: {distance_down_to_tp1:.2f}%"
    )

    print(
        f"distance_down_to_tp2_pct: {distance_down_to_tp2:.2f}%"
    )

    print(
        f"distance_up_to_stop_pct: {distance_up_to_stop:.2f}%"
    )

    print(
        f"tp1_hit: {row.get('tp1_hit')}"
    )

    print(
        f"be_active: {row.get('be_active')}"
    )

    notes = row.get(
        "notes",
        ""
    )

    if notes:

        print(
            f"notes: {notes}"
        )


def print_summary(
    df
):

    print(
        "\n=== PAPER TRADE MONITOR ===\n"
    )

    print(
        f"total_trades: {len(df)}"
    )

    if len(df) == 0:
        return

    status_counts = (
        df["status"]
        .value_counts()
        .to_dict()
    )

    print(
        "\nstatus_counts:"
    )

    for status, count in status_counts.items():

        print(
            f"{status}: {count}"
        )


def main():

    current_price = load_current_price()

    if current_price is None:

        print(
            "No se encontró precio actual."
        )

        print(
            "Primero ejecuta: python src\\alerts\\run_fib_v5_live_alert.py"
        )

        return

    df = load_paper_trades(
        PAPER_TRADES_FILE
    )

    if len(df) == 0:

        print(
            "\n=== PAPER TRADE MONITOR ===\n"
        )

        print(
            "No hay paper trades registrados."
        )

        return

    df = update_open_trades(
        df,
        current_price=current_price
    )

    save_paper_trades(
        df,
        PAPER_TRADES_FILE
    )

    print_summary(
        df
    )

    open_df = df[
        df["status"].isin(
            OPEN_STATUSES
        )
    ]

    if len(open_df) == 0:

        print(
            "\nNo hay trades abiertos."
        )

        return

    for _, row in open_df.iterrows():

        print_trade_status(
            row,
            current_price=current_price
        )


if __name__ == "__main__":
    main()