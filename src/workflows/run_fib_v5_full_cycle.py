import subprocess
import sys


COMMANDS = [
    {
        "name": "MTF TREND REGIME ENGINE",
        "command": [
            sys.executable,
            "src\\regime\\run_mtf_trend_regime.py"
        ]
    },
    {
        "name": "LIVE ALERT ENGINE",
        "command": [
            sys.executable,
            "src\\alerts\\run_fib_v5_live_alert.py"
        ]
    },
    {
        "name": "DECISION ENGINE",
        "command": [
            sys.executable,
            "src\\decision\\run_fib_v5_decision.py"
        ]
    },
    {
        "name": "PAPER TRADE LOGGER",
        "command": [
            sys.executable,
            "src\\paper_trading\\run_paper_trade_logger.py"
        ]
    },
    {
        "name": "PAPER TRADE MONITOR",
        "command": [
            sys.executable,
            "src\\paper_trading\\run_paper_trade_monitor.py"
        ]
    },
    {
        "name": "CYCLE HISTORY LOGGER",
        "command": [
            sys.executable,
            "src\\workflows\\cycle_history_logger.py"
        ]
    }
]


def run_command(
    name,
    command
):

    print(
        f"\n=== EJECUTANDO {name} ===\n"
    )

    result = subprocess.run(
        command,
        text=True,
        capture_output=True
    )

    print(
        result.stdout
    )

    if result.stderr:

        print(
            "\n--- ERRORES / ADVERTENCIAS ---\n"
        )

        print(
            result.stderr
        )

    if result.returncode != 0:

        print(
            f"\n{name} falló con código: {result.returncode}"
        )

        return False

    return True


def main():

    print(
        "\n=== FIB V5 FULL CYCLE RUNNER ===\n"
    )

    for item in COMMANDS:

        success = run_command(
            name=item["name"],
            command=item["command"]
        )

        if not success:

            print(
                "\nFlujo detenido por error."
            )

            return

    print(
        "\n=== CICLO COMPLETADO ===\n"
    )

    print(
        "Archivos principales:"
    )

    print(
        "- reports/mtf_trend_regime_report.txt"
    )

    print(
        "- reports/mtf_trend_regime_report.json"
    )

    print(
        "- reports/fib_v5_live_alert_report.txt"
    )

    print(
        "- reports/fib_v5_decision_report.txt"
    )

    print(
        "- reports/paper_trades.csv"
    )

    print(
        "- reports/fib_v5_cycle_history.csv"
    )

    print(
        "\nEstado actualizado del paper trade mostrado en consola por PAPER TRADE MONITOR."
    )


if __name__ == "__main__":
    main()