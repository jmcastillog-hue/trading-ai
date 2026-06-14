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

from src.decision.decision_engine import (
    evaluate_decision,
    build_decision_report_text
)


ALERT_JSON = "reports/fib_v5_live_alert_report.json"

DECISION_TXT = "reports/fib_v5_decision_report.txt"
DECISION_JSON = "reports/fib_v5_decision_report.json"


ACCOUNT_EQUITY = 1000
RISK_PER_TRADE_PCT = 1.0
MAX_ALLOWED_STOP_PCT = 5.0
HARD_MAX_STOP_PCT = 10.0
MAX_MARGIN_USAGE_PCT = 20.0
LEVERAGE = 1.0

# Seguridad:
# False = nunca autoriza operación real.
# True = permite clasificar como TRADE_CANDIDATE o SMALL_SIZE_ONLY,
# pero igual exige revisión manual.
ALLOW_REAL_TRADE = False


def load_json(
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


def save_json(
    path,
    data
):

    json_safe = json.loads(
        json.dumps(
            data,
            default=str
        )
    )

    with open(
        path,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            json_safe,
            file,
            indent=4,
            ensure_ascii=False
        )


def save_text(
    path,
    text
):

    with open(
        path,
        "w",
        encoding="utf-8"
    ) as file:

        file.write(
            text
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

    alert = load_json(
        ALERT_JSON
    )

    risk_report = build_risk_report(
        alert=alert,
        account_equity=ACCOUNT_EQUITY,
        risk_per_trade_pct=RISK_PER_TRADE_PCT,
        max_allowed_stop_pct=MAX_ALLOWED_STOP_PCT,
        leverage=LEVERAGE
    )

    decision = evaluate_decision(
        alert=alert,
        risk_report=risk_report,
        preferred_max_stop_pct=MAX_ALLOWED_STOP_PCT,
        hard_max_stop_pct=HARD_MAX_STOP_PCT,
        max_margin_usage_pct=MAX_MARGIN_USAGE_PCT,
        allow_real_trade=ALLOW_REAL_TRADE
    )

    report_text = build_decision_report_text(
        alert=alert,
        risk_report=risk_report,
        decision=decision
    )

    os.makedirs(
        "reports",
        exist_ok=True
    )

    save_text(
        DECISION_TXT,
        report_text
    )

    save_json(
        DECISION_JSON,
        {
            "alert": alert,
            "risk_report": risk_report,
            "decision": decision
        }
    )

    print(
        report_text
    )

    print(
        f"\nReporte TXT guardado en: {DECISION_TXT}"
    )

    print(
        f"Reporte JSON guardado en: {DECISION_JSON}"
    )


if __name__ == "__main__":
    main()