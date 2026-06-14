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

from src.paper_trading.paper_trade_logger import (
    load_decision_payload,
    log_paper_trade_from_decision,
    summarize_paper_trades
)


DECISION_JSON = "reports/fib_v5_decision_report.json"


def print_result(
    result
):

    print(
        "\n=== PAPER TRADE LOGGER V1 ===\n"
    )

    print(
        f"logged: {result.get('logged')}"
    )

    print(
        f"reason: {result.get('reason')}"
    )

    if result.get("trade_id"):

        print(
            f"trade_id: {result.get('trade_id')}"
        )

    print(
        f"paper_trades_path: {result.get('paper_trades_path')}"
    )

    print(
        f"total_trades: {result.get('total_trades')}"
    )


def print_summary():

    summary = summarize_paper_trades()

    print(
        "\n=== PAPER TRADES SUMMARY ===\n"
    )

    print(
        f"total_trades: {summary['total_trades']}"
    )

    print(
        f"open_trades: {summary['open_trades']}"
    )

    print(
        f"closed_trades: {summary['closed_trades']}"
    )

    print(
        "\nstatus_counts:"
    )

    for status, count in summary["status_counts"].items():

        print(
            f"{status}: {count}"
        )


def main():

    if not os.path.exists(
        DECISION_JSON
    ):

        print(
            f"No existe el archivo: {DECISION_JSON}"
        )

        print(
            "Primero ejecuta:"
        )

        print(
            "python src\\alerts\\run_fib_v5_live_alert.py"
        )

        print(
            "python src\\decision\\run_fib_v5_decision.py"
        )

        return

    payload = load_decision_payload(
        DECISION_JSON
    )

    result = log_paper_trade_from_decision(
        payload
    )

    print_result(
        result
    )

    print_summary()


if __name__ == "__main__":
    main()