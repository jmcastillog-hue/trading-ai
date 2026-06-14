import os
import sys
import json

sys.path.append(
    os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            "..",
            ".."
        )
    )
)

from src.risk.risk_manager import (
    build_risk_report
)


ALERT_JSON = "reports/fib_v5_live_alert_report.json"


# Cambia estos valores según tu caso real.
# Por seguridad, parte con números conservadores.
ACCOUNT_EQUITY = 1000
RISK_PER_TRADE_PCT = 1.0
MAX_ALLOWED_STOP_PCT = 5.0
LEVERAGE = 1.0


def load_alert(
    path
):

    with open(
        path,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(
            file
        )


def format_float(
    value,
    decimals=2
):

    try:

        return f"{float(value):.{decimals}f}"

    except Exception:

        return str(value)


def print_risk_report(
    report
):

    print(
        "\n=== FIB V5 RISK MANAGER ===\n"
    )

    print(
        f"risk_check: {report.get('risk_check')}"
    )

    if report.get("risk_check") != "OK":

        print(
            f"comment: {report.get('comment')}"
        )

        return

    print(
        f"account_equity: {format_float(report['account_equity'])}"
    )

    print(
        f"risk_per_trade_pct: {format_float(report['risk_per_trade_pct'])}%"
    )

    print(
        f"risk_amount: {format_float(report['risk_amount'])}"
    )

    print(
        f"entry_price: {format_float(report['entry_price'])}"
    )

    print(
        f"stop_price: {format_float(report['stop_price'])}"
    )

    print(
        f"tp1_price: {format_float(report['tp1_price'])}"
    )

    print(
        f"tp2_price: {format_float(report['tp2_price'])}"
    )

    print(
        f"stop_distance_pct: {format_float(report['stop_distance_pct'])}%"
    )

    print(
        f"position_notional: {format_float(report['position_notional'])}"
    )

    print(
        f"btc_size: {format_float(report['btc_size'], 8)}"
    )

    print(
        f"leverage: {format_float(report['leverage'])}x"
    )

    print(
        f"required_margin: {format_float(report['required_margin'])}"
    )

    outcomes = report["outcomes"]

    print(
        "\n--- RESULTADOS POTENCIALES V5 ---\n"
    )

    print(
        f"si_stop_directo: {format_float(outcomes['stop_result_pct'])}%"
    )

    print(
        f"si_tp1: {format_float(outcomes['tp1_result_pct'])}%"
    )

    print(
        f"si_tp2: {format_float(outcomes['tp2_result_pct'])}%"
    )

    print(
        f"si_tp1_y_breakeven: {format_float(outcomes['tp1_then_be_result_pct'])}%"
    )

    print(
        f"si_tp1_y_tp2: {format_float(outcomes['tp1_then_tp2_result_pct'])}%"
    )

    warnings = report.get(
        "warnings",
        []
    )

    if len(warnings) > 0:

        print(
            "\n--- ADVERTENCIAS ---\n"
        )

        for warning in warnings:

            print(
                f"- {warning}"
            )


def main():

    if not os.path.exists(
        ALERT_JSON
    ):

        print(
            f"No existe el archivo: {ALERT_JSON}"
        )

        print(
            "Primero ejecuta: python src\\alerts\\run_fib_v5_live_alert.py"
        )

        return

    alert = load_alert(
        ALERT_JSON
    )

    report = build_risk_report(
        alert=alert,
        account_equity=ACCOUNT_EQUITY,
        risk_per_trade_pct=RISK_PER_TRADE_PCT,
        max_allowed_stop_pct=MAX_ALLOWED_STOP_PCT,
        leverage=LEVERAGE
    )

    print_risk_report(
        report
    )


if __name__ == "__main__":
    main()